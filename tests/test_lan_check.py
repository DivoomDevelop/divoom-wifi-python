from __future__ import annotations

import runpy
from pathlib import Path


def checker(make_client, monkeypatch, hardware):
    namespace = runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools/check_lan.py"))
    client = make_client(hardware, local_token=None)
    monkeypatch.setitem(namespace["check_device"].__globals__, "connect", lambda *a, **kw: client)
    return namespace["check_device"], client.device


def test_lan_check_separates_acknowledgements_from_business_data(make_client, server, monkeypatch):
    monkeypatch.delenv("DIVOOM_LOCAL_TOKEN", raising=False)
    server.replies["Sys/GetBrightness"] = {"ReturnCode": 0, "Brightness": 40}
    server.replies["Channel/GetOnOffScreen"] = {"ReturnCode": 0, "OnOff": 1}
    server.replies["Channel/GetClockInfo"] = {"ReturnCode": 0, "ClockId": 182}
    check, device = checker(make_client, monkeypatch, 402)
    result = check(device, 2)
    assert result["result"] == "pass"
    assert result["business_reads"] == 3
    assert [c["result"] for c in result["checks"]] == ["ack_only", "ack_only", "pass", "pass", "pass"]
    assert all("LocalToken" not in r["payload"] for r in server.records)


def test_lan_check_identity_mismatch_overrides_earlier_success(make_client, server, monkeypatch):
    server.replies["Device/GetLanCapabilities"] = {"ReturnCode": 0, "Hardware": 511, "JsonMaxBytes": 65536}
    check, device = checker(make_client, monkeypatch, 530)
    result = check(device, 2)
    assert result["business_reads"] == 1
    assert result["result"] == "identity_mismatch"
    assert len(result["checks"]) == 2
