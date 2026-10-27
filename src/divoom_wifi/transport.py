"""HTTP transport: explicit JSON bodies, per-origin serialization, no retries."""
from __future__ import annotations

import json
import math
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from urllib.parse import urlsplit

import requests

from .errors import DeviceError, HTTPError, NetworkError, ProtocolError, ValidationError

_LOCKS: dict[str, threading.RLock] = {}
_LOCKS_GUARD = threading.Lock()


def origin_lock(url: str) -> threading.RLock:
    parts = urlsplit(url)
    port = parts.port or (443 if parts.scheme == "https" else 80)
    key = f"{parts.scheme}://{(parts.hostname or '').lower()}:{port}"
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(key, threading.RLock())


def json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError) as exc:
        raise ValidationError("Parameters must be finite, UTF-8 JSON values") from exc


def check_status(result: Any, fields: tuple[str, ...], api_name: str) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ProtocolError("Expected a JSON object", api_name=api_name, response=result)
    found = [key for key in fields if key in result]
    if not found:
        raise ProtocolError(f"Missing status field: {' or '.join(fields)}", api_name=api_name, response=result)
    for key in found:
        code = result[key]
        if type(code) is not int:
            raise ProtocolError(f"Invalid {key}: expected an integer", api_name=api_name, response=result)
        if code != 0:
            message = result.get("ReturnMessage") or result.get("error_message") or f"Device returned {key}={code}"
            raise DeviceError(str(message), api_name=api_name, response=result, code=code)
    return result


class Transport:
    def __init__(self, timeout: float = 15, upload_timeout: float = 120):
        if any(type(value) not in (int, float) or not math.isfinite(value) or value <= 0
               for value in (timeout, upload_timeout)):
            raise ValidationError("Timeouts must be finite positive numbers")
        self.timeout = timeout
        self.upload_timeout = upload_timeout
        self._local = requests.Session()
        self._local.trust_env = False  # Never send LAN control tokens through environment proxies.
        self._cloud = requests.Session()
        self._closed = False

    @contextmanager
    def response(self, method: str, url: str, *, api_name: str, local: bool = True,
                 data: Any = None, headers: dict[str, str] | None = None,
                 timeout: float | None = None) -> Iterator[requests.Response]:
        if self._closed:
            raise ValidationError("Client is closed", api_name=api_name)
        with origin_lock(url):
            response = None
            try:
                session = self._local if local else self._cloud
                response = session.request(method, url, data=data, headers=headers,
                                           timeout=timeout or self.timeout, stream=True,
                                           allow_redirects=False)
                if not 200 <= response.status_code < 300:
                    preview = next(response.iter_content(2048), b"").decode("utf-8", errors="replace")
                    raise HTTPError(f"HTTP {response.status_code}", api_name=api_name,
                                    status_code=response.status_code, response=preview)
                yield response
            except requests.RequestException as exc:
                raise NetworkError(f"Network failure during {api_name}: {type(exc).__name__}",
                                   api_name=api_name) from exc
            finally:
                if response is not None:
                    response.close()

    def request_json(self, method: str, url: str, payload: dict[str, Any], *, api_name: str,
                     status_fields: tuple[str, ...] = ("ReturnCode",), local: bool = True,
                     max_bytes: int | None = None, timeout: float | None = None) -> dict[str, Any]:
        data = json_bytes(payload)
        if max_bytes is not None and len(data) > max_bytes:
            raise ValidationError(f"JSON request exceeds {max_bytes} UTF-8 bytes", api_name=api_name)
        with self.response(method, url, api_name=api_name, local=local, data=data, timeout=timeout,
                           headers={"Content-Type": "application/json; charset=utf-8"}) as response:
            return self.decode_json(response, api_name, status_fields, max_bytes)

    @staticmethod
    def decode_json(response: requests.Response, api_name: str, status_fields: tuple[str, ...],
                    max_bytes: int | None = None) -> dict[str, Any]:
        chunks = []
        size = 0
        for chunk in response.iter_content(8192):
            size += len(chunk)
            if max_bytes is not None and size > max_bytes:
                raise ProtocolError(f"JSON response exceeds {max_bytes} bytes", api_name=api_name)
            chunks.append(chunk)
        raw = b"".join(chunks)
        try:
            result = json.loads(raw.decode("utf-8-sig"))
        except (ValueError, UnicodeError) as exc:
            raise ProtocolError("Invalid JSON response", api_name=api_name,
                                response=raw[:2048].decode("utf-8", errors="replace")) from exc
        return check_status(result, status_fields, api_name)

    def close(self) -> None:
        self._local.close()
        self._cloud.close()
        self._closed = True
