"""Shared parameter binding and dispatch; products expose explicit methods."""
from __future__ import annotations

import math
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self, overload
from urllib.parse import unquote, urlsplit

from .discovery import normalize_origin, probe_hardware
from .errors import (
    HTTPError,
    NetworkError,
    ProtocolError,
    TokenRequiredError,
    UnsupportedDeviceError,
    ValidationError,
)
from .models import PROFILES, DeviceInfo
from .registry import APISpec, describe_api, list_apis
from .transport import Transport, origin_lock

if TYPE_CHECKING:
    from .products import AstroToo, Pixoo64, TimeFrame, TimeGate


class BaseDevice:
    """Context-managed synchronous device client. Prefer the connect() factory."""

    def __init__(self, device: DeviceInfo, *, local_token: int | str | None = None,
                 timeout: float = 15, upload_timeout: float = 120, base_url: str | None = None):
        if device.hardware not in PROFILES:
            raise UnsupportedDeviceError(f"Unsupported hardware: {device.hardware}; specify a supported hardware ID")
        self.device = device
        self.profile = PROFILES[device.hardware]
        self.product = self.profile.product
        expected_product = getattr(type(self), "product_name", self.product)
        if expected_product != self.product:
            raise UnsupportedDeviceError(f"{type(self).__name__} cannot control {self.product}")
        self.base_url = normalize_origin(base_url or device.ip, self.profile.port)
        self._transport = Transport(timeout, upload_timeout)
        self._token = local_token if local_token is not None else os.environ.get("DIVOOM_LOCAL_TOKEN")
        self.capabilities: dict[str, Any] = dict(device.raw.get("hardware_query", {}))
        self._capabilities_loaded = "JsonMaxBytes" in self.capabilities

    def list_apis(self) -> list[APISpec]:
        """Return only this product's registered operations, without network I/O."""
        return list_apis(self.product)

    def describe_api(self, name: str) -> APISpec:
        """Return protocol fields, source URLs, parameter help and transport."""
        return describe_api(self.product, name)

    def set_local_token(self, token: int | str) -> None:
        """Set a TimeGate token in memory only; useful after a hidden CLI prompt."""
        if type(token) is int:
            value = token
        elif isinstance(token, str) and token.isascii() and token.isdigit():
            value = int(token)
        else:
            raise ValidationError("LocalToken must be a nonnegative integer")
        if value < 0:
            raise ValidationError("LocalToken must be a nonnegative integer")
        self._token = value

    def _bind(self, spec: APISpec, supplied: dict[str, Any]) -> dict[str, Any]:
        remaining = dict(supplied)
        payload = dict(spec.constants)
        if spec.command:
            payload["Command"] = spec.command
        for param in spec.parameters:
            aliases = list(dict.fromkeys((param.name, param.wire)))
            provided = [key for key in aliases if key in remaining]
            if len(provided) > 1:
                raise ValidationError(f"Specify only one of {param.name}/{param.wire}", api_name=spec.name)
            value = remaining.pop(provided[0]) if provided else None
            if value is None and param.auto:
                value = getattr(self.device, param.auto)
            if value is None:
                value = param.default
            if value is None:
                if param.required:
                    raise ValidationError(f"Missing {param.name} ({param.wire})", api_name=spec.name)
                continue
            valid = {
                "int": lambda v: type(v) is int,
                "float": lambda v: type(v) in (int, float) and math.isfinite(v),
                "str": lambda v: isinstance(v, str),
                "bool": lambda v: type(v) is bool,
                "list": lambda v: isinstance(v, list),
                "dict": lambda v: isinstance(v, dict),
                "path": lambda v: isinstance(v, (str, Path)),
                "any": lambda v: True,
            }[param.type](value)
            if not valid:
                raise ValidationError(f"{param.name} must be {param.type}", api_name=spec.name)
            payload[param.wire] = value
        if remaining:
            raise ValidationError(f"Unknown parameters: {', '.join(sorted(remaining))}", api_name=spec.name)
        if spec.token_required:
            if self._token is None:
                raise TokenRequiredError("TimeGate requires LocalToken from device settings; set DIVOOM_LOCAL_TOKEN "
                                         "or pass local_token to connect()", api_name=spec.name)
            self.set_local_token(self._token)
            payload["LocalToken"] = self._token
        self._validate_payload(spec, payload)
        return payload

    def _validate_payload(self, spec: APISpec, payload: dict[str, Any]) -> None:
        def range_check(key: str, low: int, high: int) -> None:
            if key in payload and not low <= payload[key] <= high:
                raise ValidationError(f"{key} must be between {low} and {high}", api_name=spec.name)

        for key in ("Brightness", "RValue", "GValue", "BValue", "SlideshowSpeed", "VideoVolume"):
            range_check(key, 0, 100)
        for key in ("LcdIndex", "LcdId"):
            range_check(key, 0, 4)
        for key in ("OnOff", "NoiseStatus", "UseCurrentDisplayClock", "GalleryShowTimeFlag"):
            range_check(key, 0, 1)
        if spec.name in ("set_hour_mode", "set_mirror_mode", "set_temperature_mode", "set_highlight_mode"):
            range_check("Mode", 0, 1)
        if spec.name == "set_rotation":
            range_check("Mode", 0, 3)
        if "Page" in payload and payload["Page"] < 1:
            raise ValidationError("Page must be at least 1", api_name=spec.name)
        if "StartNum" in payload and (payload["StartNum"] < 1 or payload["EndNum"] < payload["StartNum"]):
            raise ValidationError("Require 1 <= StartNum <= EndNum", api_name=spec.name)
        if self.product == "astrotoo":
            if spec.name == "get_local_photos" and payload["EndNum"] - payload["StartNum"] >= 100:
                raise ValidationError("Photo list pages may contain at most 100 entries", api_name=spec.name)
            for key in ("ClockId", "ToClockId"):
                if spec.command and spec.command.startswith("Photo/") and key in payload and payload[key] < 100000:
                    raise ValidationError(f"{key} must be a local album ID >= 100000", api_name=spec.name)
            if "PhotoList" in payload and (not payload["PhotoList"] or any(type(v) is not int or v < 0
                                                                       for v in payload["PhotoList"])):
                raise ValidationError("PhotoList must contain photo IDs", api_name=spec.name)
            if "ClockName" in payload and not 1 <= len(payload["ClockName"].encode("utf-8")) <= 63:
                raise ValidationError("ClockName must be 1..63 UTF-8 bytes", api_name=spec.name)
            if (spec.name in ("patch_local_clock", "patch_clock_background", "replace_clock_background")
                    and "ClockId" not in payload and payload.get("UseCurrentDisplayClock") != 1):
                raise ValidationError("ClockId is required unless UseCurrentDisplayClock=1", api_name=spec.name)
            if spec.name == "create_local_clock" and not payload["ItemList"]:
                raise ValidationError("ItemList must not be empty", api_name=spec.name)
        if spec.name == "set_countdown":
            range_check("Second", 0, 59)
            range_check("Status", 0, 1)
            if payload["Minute"] < 0:
                raise ValidationError("Minute must be nonnegative", api_name=spec.name)
        if spec.name == "set_stopwatch":
            range_check("Status", 0, 2)
        if spec.name == "select_channel_type":
            range_check("ChannelType", 0, 1)
            if payload["ChannelType"] == 1 and "LcdIndependence" not in payload:
                raise ValidationError("LcdIndependence is required for ChannelType=1", api_name=spec.name)
        if spec.name == "send_animation":
            range_check("PicNum", 1, 59)
            range_check("PicOffset", 0, payload["PicNum"] - 1)
            widths = (16, 32, 64, 128) if self.product == "timegate" else (16, 32, 64)
            if payload["PicWidth"] not in widths:
                raise ValidationError(f"PicWidth must be one of {widths}", api_name=spec.name)
        if "LcdArray" in payload and (len(payload["LcdArray"]) != 5
                                      or any(type(v) is not int or v not in (0, 1) for v in payload["LcdArray"])):
            raise ValidationError("LcdArray must contain five numeric 0/1 values", api_name=spec.name)
        if spec.name == "set_rgb" and len(payload) <= 2:  # Command and LocalToken alone do nothing.
            raise ValidationError("Provide at least one RGB setting", api_name=spec.name)

    def call(self, name: str, **params: Any) -> Any:
        """Invoke a registered API using Python names or exact protocol field names.

        None omits an optional field. HTTP/JSON errors raise DivoomError subclasses;
        successful JSON responses are returned unchanged. No write is retried.
        """
        return self._call(name, params)

    def _call(self, name: str, params: dict[str, Any], *, request_timeout: float | None = None) -> Any:
        spec = self.describe_api(name)  # Resolve product support before any network traffic.
        payload = self._bind(spec, params)
        with origin_lock(self.base_url):
            if (self.product == "astrotoo" and name not in ("get_hardware_version", "get_lan_capabilities")
                    and not self._capabilities_loaded):
                self._call("get_lan_capabilities", {}, request_timeout=request_timeout)
            if spec.route in ("download", "head", "upload"):
                from .transfers import download, upload
                if spec.route == "upload":
                    return upload(self, spec, payload)
                return download(self, spec, payload)
            local = spec.route == "lan"
            url = self.base_url + self.profile.path if local else spec.url
            limit = self.json_limit if self.product == "astrotoo" and local else None
            result = self._transport.request_json(spec.method, url, payload, api_name=name,
                                                  status_fields=spec.status_fields, local=local,
                                                  max_bytes=limit, timeout=request_timeout)
            if name in ("get_lan_capabilities", "get_hardware_version") and self.product == "astrotoo":
                self.capabilities.update(result)
                if name == "get_lan_capabilities":
                    self._capabilities_loaded = True
            return result

    @property
    def json_limit(self) -> int:
        value = self.capabilities.get("JsonMaxBytes", 65536)
        if type(value) is not int or value <= 0:
            raise ProtocolError("Invalid JsonMaxBytes in capabilities")
        return min(value, 65536)

    def wait_for_photo(self, *, clock_id: int, file_name: str | None = None, photo_id: int | None = None,
                       timeout: float = 30, poll_interval: float = 1) -> dict[str, Any]:
        """Poll AstroToo photo pages until a matching entry exists, without re-uploading.

        Prefer a new unique filename or a known PhotoId; an old matching filename
        cannot prove a new upload completed. Return the matching photo entry.
        """
        self.describe_api("get_local_photos")
        if timeout <= 0 or poll_interval <= 0 or (file_name is None and photo_id is None):
            raise ValidationError("Provide file_name or photo_id and positive polling timeouts")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            start = 1
            while time.monotonic() < deadline:
                result = self._call("get_local_photos", {"clock_id": clock_id, "start_num": start,
                                                         "end_num": start + 99},
                                    request_timeout=min(self._transport.timeout, deadline - time.monotonic()))
                photos = result.get("PhotoList")
                if not isinstance(photos, list):
                    raise ProtocolError("Photo list response omitted PhotoList", api_name="wait_for_photo", response=result)
                for photo in photos:
                    if not isinstance(photo, dict):
                        raise ProtocolError("PhotoList entry must be an object", api_name="wait_for_photo", response=result)
                    original = photo.get("OriginalFileId", "")
                    returned_name = (unquote(urlsplit(original).path).rsplit("/", 1)[-1]
                                     if isinstance(original, str) else "")
                    if ((photo_id is None or photo.get("PhotoId") == photo_id)
                            and (file_name is None or photo.get("FileName", returned_name) == file_name)):
                        return photo
                if len(photos) < 100:
                    break
                start += 100
            remaining = deadline - time.monotonic()
            if remaining > 0:
                time.sleep(min(poll_interval, remaining))
        raise NetworkError("Timed out waiting for photo insertion; upload was not retried", api_name="wait_for_photo")

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


@overload
def connect(device: DeviceInfo | str, *, hardware: Literal[530], local_token: int | str | None = None,
            timeout: float = 15, upload_timeout: float = 120, base_url: str | None = None) -> AstroToo: ...


@overload
def connect(device: DeviceInfo | str, *, hardware: Literal[90, 92, 96], local_token: int | str | None = None,
            timeout: float = 15, upload_timeout: float = 120, base_url: str | None = None) -> Pixoo64: ...


@overload
def connect(device: DeviceInfo | str, *, hardware: Literal[400, 402], local_token: int | str | None = None,
            timeout: float = 15, upload_timeout: float = 120, base_url: str | None = None) -> TimeGate: ...


@overload
def connect(device: DeviceInfo | str, *, hardware: Literal[510, 511, 512], local_token: int | str | None = None,
            timeout: float = 15, upload_timeout: float = 120, base_url: str | None = None) -> TimeFrame: ...


@overload
def connect(device: DeviceInfo | str, *, hardware: int | None = None, local_token: int | str | None = None,
            timeout: float = 15, upload_timeout: float = 120,
            base_url: str | None = None) -> Pixoo64 | TimeGate | TimeFrame | AstroToo: ...


def connect(device: DeviceInfo | str, *, hardware: int | None = None, local_token: int | str | None = None,
            timeout: float = 15, upload_timeout: float = 120, base_url: str | None = None) -> BaseDevice:
    """Select a product class from Hardware, never from a user-editable device name.

    A direct IP without hardware triggers one read-only query on port 9000.
    Use an explicit hardware ID for older firmware that cannot answer that query.
    base_url overrides the HTTP origin (host/port), retaining the product route.
    """
    from dataclasses import replace

    from .products import AstroToo, Pixoo64, TimeFrame, TimeGate

    info = device if isinstance(device, DeviceInfo) else DeviceInfo(name=device, ip=device)
    if hardware is not None:
        if type(hardware) is not int:
            raise ValidationError("hardware must be an integer")
        info = replace(info, hardware=hardware)
    if info.hardware is None:
        try:
            result = probe_hardware(info.ip, timeout=min(timeout, 3), base_url=base_url)
        except (NetworkError, ProtocolError, HTTPError) as exc:
            raise UnsupportedDeviceError("Could not identify hardware; specify hardware explicitly") from exc
        info = replace(info, hardware=result["Hardware"], raw={**info.raw, "hardware_query": result})
    if info.hardware not in PROFILES:
        raise UnsupportedDeviceError(f"Hardware {info.hardware} is not supported")
    cls = {"pixoo64": Pixoo64, "timegate": TimeGate, "timeframe": TimeFrame, "astrotoo": AstroToo}[info.product]
    return cls(info, local_token=local_token, timeout=timeout, upload_timeout=upload_timeout, base_url=base_url)
