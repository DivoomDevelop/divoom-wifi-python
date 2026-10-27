from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

from divoom_wifi import AstroToo, Pixoo64, TimeFrame, TimeGate
from divoom_wifi.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = load_registry()


def test_every_source_page_is_accounted_for():
    pages = json.loads((ROOT / "docs/reference/pages.json").read_text(encoding="utf-8"))["pages"]
    coverage = json.loads((ROOT / "docs/reference/coverage.json").read_text(encoding="utf-8"))["pages"]
    assert len(pages) == len(coverage) == 144
    assert len([p for p in pages if p["product"] != "common"]) == 141
    assert {p["page_id"] for p in pages} == {p["page_id"] for p in coverage}
    for page, entry in zip(pages, coverage):
        assert entry["sha256"] == hashlib.sha256(page["content"].encode()).hexdigest()
        if entry["kind"] == "api":
            spec = REGISTRY[entry["product"]][entry["api"]]
            assert entry["page_id"] in spec.sources
            assert entry["url"] in spec.source_urls
        else:
            assert entry["page_id"] in (24, 25, 145, 358, 381, 430)
    assert {k: len(v) for k, v in REGISTRY.items()} == {"pixoo64": 45, "timegate": 39, "timeframe": 16, "astrotoo": 38}


@pytest.mark.parametrize("product,cls", [("pixoo64", Pixoo64), ("timegate", TimeGate),
                                         ("timeframe", TimeFrame), ("astrotoo", AstroToo)])
def test_product_methods_have_explicit_typed_signatures(product, cls):
    for spec in REGISTRY[product].values():
        function = cls.__dict__[spec.name]
        signature = inspect.signature(function)
        assert list(signature.parameters) == ["self"] + [p.name for p in spec.parameters]
        assert signature.return_annotation is not inspect.Signature.empty
        assert function.__doc__
        for param in list(signature.parameters.values())[1:]:
            assert param.annotation is not inspect.Parameter.empty
            assert param.kind == inspect.Parameter.KEYWORD_ONLY


def test_reference_generation_is_reproducible():
    subprocess.run([sys.executable, "tools/build_reference.py", "--check"], cwd=ROOT, check=True)


def test_nested_fields_and_documented_typos_are_preserved():
    pixoo = REGISTRY["pixoo64"]
    gate = REGISTRY["timegate"]
    assert [p.wire for p in pixoo["send_display_list"].parameters] == ["ItemList"]
    assert "SelectEffect" not in [p.wire for p in gate["set_rgb"].parameters]
    assert "BackgroudGif" in [p.wire for p in gate["send_display_list"].parameters]
    assert "SingleGalleyTime" in [p.wire for p in pixoo["set_gallery_time"].parameters]
    assert pixoo["set_gallery_time"].sources == (137, 355)
    assert pixoo["select_visualizer"].command == "Channel/SetEqPosition"
    assert gate["select_visualizer"].command == "Channel/SetEqPosition"
    assert pixoo["select_cloud_channel"].command == "Channel/CloudIndex"
    assert gate["get_fonts"].url == "https://appin.divoom-gz.com/Device/GetTimeDialFontList"
    assert REGISTRY["timeframe"]["get_dial_list"].method == "GET"
