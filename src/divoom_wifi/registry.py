"""Offline operation registry shared by product methods, CLI and documentation."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from importlib.resources import files
from typing import Any

from .errors import UnsupportedAPIError


@dataclass(frozen=True)
class Parameter:
    name: str
    wire: str
    type: str = "any"
    required: bool = False
    description: str = ""
    auto: str | None = None
    default: Any = None


@dataclass(frozen=True)
class APISpec:
    name: str
    product: str
    title: str
    route: str
    method: str
    command: str | None = None
    url: str | None = None
    path: str | None = None
    status_fields: tuple[str, ...] = ("ReturnCode",)
    parameters: tuple[Parameter, ...] = ()
    sources: tuple[int, ...] = ()
    source_urls: tuple[str, ...] = ()
    notes: str = ""
    token_required: bool = False
    constants: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@lru_cache(maxsize=1)
def load_registry() -> dict[str, dict[str, APISpec]]:
    data = json.loads(files("divoom_wifi").joinpath("data/apis.json").read_text(encoding="utf-8"))
    registry: dict[str, dict[str, APISpec]] = {}
    for entry in data["apis"]:
        entry = dict(entry)
        entry["parameters"] = tuple(Parameter(**p) for p in entry["parameters"])
        for key in ("status_fields", "sources", "source_urls"):
            entry[key] = tuple(entry[key])
        spec = APISpec(**entry)
        product = registry.setdefault(spec.product, {})
        if spec.name in product:
            raise RuntimeError(f"Duplicate API: {spec.product}/{spec.name}")
        product[spec.name] = spec
    return registry


def list_apis(product: str) -> list[APISpec]:
    return list(load_registry().get(product, {}).values())


def describe_api(product: str, name: str) -> APISpec:
    try:
        return load_registry()[product][name]
    except KeyError as exc:
        raise UnsupportedAPIError(f"{name!r} is not registered for {product}", api_name=name) from exc
