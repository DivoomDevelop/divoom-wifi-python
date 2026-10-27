"""Device identity and immutable product routing profiles."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProductProfile:
    product: str
    hardware: int
    port: int
    path: str
    method: str
    local_token_required: bool = False
    token_field: str = "LocalToken"


PROFILES = {
    hw: ProductProfile(product, hw, port, path, method, local_token_required=(hw in (90, 92, 400)),
                       token_field="DeviceToken" if hw in (90, 92) else "LocalToken")
    for product, hardware, port, path, method in (
        ("pixoo64", (90, 92), 80, "/post", "POST"),
        ("pixoo64", (96,), 9000, "/divoom_api", "POST"),
        ("timegate", (400,), 80, "/post", "POST"),
        ("timegate", (402,), 9000, "/divoom_api", "POST"),
        ("timeframe", (510, 511, 512), 9000, "/divoom_api", "GET"),
        ("astrotoo", (530,), 9000, "/divoom_api", "POST"),
    )
    for hw in hardware
}


@dataclass(frozen=True)
class DeviceInfo:
    name: str
    ip: str
    hardware: int | None = None
    device_id: int | None = None
    mac: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)

    @property
    def product(self) -> str | None:
        profile = PROFILES.get(self.hardware)
        return profile.product if profile else None

    @property
    def supported(self) -> bool:
        return self.product is not None

    def as_dict(self) -> dict[str, Any]:
        return {**asdict(self), "product": self.product, "supported": self.supported}
