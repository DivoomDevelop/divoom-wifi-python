"""Exceptions preserve the operation and the device response, never request secrets."""
from __future__ import annotations

from typing import Any


class DivoomError(Exception):
    def __init__(self, message: str, *, api_name: str | None = None,
                 response: Any = None, status_code: int | None = None, code: Any = None):
        super().__init__(message)
        self.api_name = api_name
        self.response = response
        self.status_code = status_code
        self.code = code


class NetworkError(DivoomError):
    """Connection failure or timeout. A timed-out write may already have executed."""


class HTTPError(DivoomError):
    """Non-success HTTP status (including redirects)."""


class ProtocolError(DivoomError):
    """Invalid JSON, missing status, or a malformed protocol response."""


class DeviceError(DivoomError):
    """The service returned a nonzero status code."""


class UnsupportedDeviceError(DivoomError):
    """Hardware is unknown or does not belong to the four supported products."""


class UnsupportedAPIError(DivoomError):
    """This operation is not registered for the selected product."""


class ValidationError(DivoomError, ValueError):
    """Parameters or file data do not meet the documented contract."""


class TokenRequiredError(ValidationError):
    """Provide the TimeGate LocalToken displayed in device settings."""
