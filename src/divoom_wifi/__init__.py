"""Divoom WiFi: discover, select by hardware, and control the matching APIs."""
from .client import BaseDevice, connect
from .discovery import discover_devices
from .errors import (
    DeviceError,
    DivoomError,
    HTTPError,
    NetworkError,
    ProtocolError,
    TokenRequiredError,
    UnsupportedAPIError,
    UnsupportedDeviceError,
    ValidationError,
)
from .models import PROFILES, DeviceInfo, ProductProfile
from .products import AstroToo, Pixoo64, TimeFrame, TimeGate
from .registry import APISpec, Parameter

__version__ = "0.1.0"
__all__ = [
    "PROFILES",
    "APISpec",
    "AstroToo",
    "BaseDevice",
    "DeviceError",
    "DeviceInfo",
    "DivoomError",
    "HTTPError",
    "NetworkError",
    "Parameter",
    "Pixoo64",
    "ProductProfile",
    "ProtocolError",
    "TimeFrame",
    "TimeGate",
    "TokenRequiredError",
    "UnsupportedAPIError",
    "UnsupportedDeviceError",
    "ValidationError",
    "connect",
    "discover_devices",
]
