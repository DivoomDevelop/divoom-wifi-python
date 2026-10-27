"""Cloud-assisted LAN discovery; no scanning and no name-based model guesses."""
from __future__ import annotations

from dataclasses import replace
from typing import Any
from urllib.parse import urlsplit

from .errors import DivoomError, ProtocolError, ValidationError
from .models import DeviceInfo
from .transport import Transport

DISCOVERY_URL = "https://app.divoom-gz.com/Device/ReturnSameLANDevice"


def normalize_origin(address: str, default_port: int = 9000) -> str:
    """Accept a host/IP or an HTTP(S) origin, including an explicit port."""
    if not isinstance(address, str) or not address.strip():
        raise ValidationError("A device IP or hostname is required")
    parts = urlsplit(address if "://" in address else "http://" + address)
    try:
        port = parts.port or default_port
    except ValueError as exc:
        raise ValidationError("Invalid port") from exc
    if (parts.scheme not in ("http", "https") or not parts.hostname or parts.username or parts.password
            or parts.query or parts.fragment or parts.path not in ("", "/") or not 1 <= port <= 65535):
        raise ValidationError("Address must be an HTTP(S) origin without credentials, path, query or fragment")
    host = parts.hostname
    if ":" in host:
        host = "[" + host + "]"
    return f"{parts.scheme}://{host}:{port}"


def _integer(value: Any, field: str) -> int | None:
    if value is None or value == "":
        return None
    if type(value) is int or (isinstance(value, str) and value.isascii() and value.isdigit()):
        return int(value)
    raise ProtocolError(f"Invalid discovery {field}", api_name="discover_devices")


def probe_hardware(ip: str, *, timeout: float = 3, base_url: str | None = None) -> dict[str, Any]:
    """Issue only Device/GetHardwareVersion. Failure never implies a product."""
    origin = normalize_origin(base_url or ip)
    transport = Transport(timeout=timeout)
    try:
        result = transport.request_json("POST", origin + "/divoom_api",
                                        {"Command": "Device/GetHardwareVersion"}, api_name="probe_hardware")
        hardware = _integer(result.get("Hardware"), "Hardware")
        if hardware is None:
            raise ProtocolError("Hardware query omitted Hardware", api_name="probe_hardware", response=result)
        return {**result, "Hardware": hardware}
    finally:
        transport.close()


def discover_devices(*, timeout: float = 15, probe_missing: bool = True,
                     discovery_url: str = DISCOVERY_URL) -> list[DeviceInfo]:
    """Return devices including unknown hardware; duplicate names are preserved.

    This service is cloud-assisted and can return unreachable/stale addresses.
    Hardware probing is read-only, and only attempted when Hardware is absent.
    ``discovery_url`` is useful for service mirrors and local integration tests.
    """
    transport = Transport(timeout=timeout)
    try:
        result = transport.request_json("POST", discovery_url, {}, api_name="discover_devices", local=False)
    finally:
        transport.close()
    rows = result.get("DeviceList")
    if not isinstance(rows, list):
        raise ProtocolError("Discovery omitted DeviceList array", api_name="discover_devices", response=result)
    devices = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("DevicePrivateIP"), str):
            raise ProtocolError("Invalid discovery device entry", api_name="discover_devices", response=row)
        device = DeviceInfo(name=str(row.get("DeviceName") or "Unnamed"), ip=row["DevicePrivateIP"],
                            hardware=_integer(row.get("Hardware"), "Hardware"),
                            device_id=_integer(row.get("DeviceId"), "DeviceId"),
                            mac=row.get("DeviceMac"), raw=dict(row))
        if device.hardware is None and probe_missing:
            try:
                info = probe_hardware(device.ip, timeout=min(timeout, 3))
                device = replace(device, hardware=info["Hardware"], raw={**device.raw, "hardware_query": info})
            except DivoomError as exc:
                device = replace(device, raw={**device.raw, "probe_error": str(exc)})
        devices.append(device)
    return devices
