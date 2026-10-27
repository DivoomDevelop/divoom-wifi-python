from __future__ import annotations

import io
import json
import sys

import pytest

from divoom_wifi import (
    DeviceError,
    DeviceInfo,
    ProtocolError,
    UnsupportedDeviceError,
    cli,
    connect,
    discover_devices,
)


def row(name="same name", hardware=530, device_id=1):
    result = {"DeviceName": name, "DevicePrivateIP": "127.0.0.1", "DeviceId": device_id,
              "DeviceMac": "aabbccddeeff"}
    if hardware is not None:
        result["Hardware"] = hardware
    return result


def test_discovery_preserves_names_duplicates_and_unknown_hardware(server):
    server.replies["/discover"] = {"ReturnCode": 0, "DeviceList": [row(hardware=90), row(hardware=530, device_id=2),
                                                                  row(hardware=700, device_id=3)]}
    devices = discover_devices(discovery_url=server.url + "/discover")
    assert len(devices) == 3
    assert [d.name for d in devices] == ["same name"] * 3
    assert [d.product for d in devices] == ["pixoo64", "astrotoo", None]
    assert [d.supported for d in devices] == [True, True, False]
    assert server.records[0]["payload"] == {}
    assert len(server.records) == 1


@pytest.mark.parametrize("reply,error", [({"ReturnCode": 3, "DeviceList": []}, DeviceError),
                                          ({"ReturnCode": 0}, ProtocolError),
                                          ({"ReturnCode": 0, "DeviceList": [{}]}, ProtocolError)])
def test_discovery_errors(server, reply, error):
    server.replies["/discover"] = reply
    with pytest.raises(error):
        discover_devices(discovery_url=server.url + "/discover")


def test_missing_hardware_queries_read_only_and_does_not_guess(server, monkeypatch):
    from divoom_wifi import discovery
    server.replies["/discover"] = {"ReturnCode": 0, "DeviceList": [row(name="Pixoo64", hardware=None)]}
    calls = []
    def probe(ip, **kwargs):
        calls.append(ip)
        return {"Hardware": 530}
    monkeypatch.setattr(discovery, "probe_hardware", probe)
    devices = discover_devices(discovery_url=server.url + "/discover")
    assert devices[0].product == "astrotoo"
    assert calls == ["127.0.0.1"]
    def failed(*a, **kw):
        raise ProtocolError("no identity")
    monkeypatch.setattr(discovery, "probe_hardware", failed)
    device = discover_devices(discovery_url=server.url + "/discover")[0]
    assert device.hardware is None and not device.supported
    assert "probe_error" in device.raw


def test_direct_ip_identifies_hardware_and_unknown_stays_unknown(server):
    with connect("127.0.0.1", base_url=server.url) as client:
        assert client.product == "astrotoo"
    assert [r["payload"]["Command"] for r in server.records] == ["Device/GetHardwareVersion"]
    server.replies["Device/GetHardwareVersion"] = {"ReturnCode": 0, "Hardware": 700}
    with pytest.raises(UnsupportedDeviceError):
        connect("127.0.0.1", base_url=server.url)
    server.replies["Device/GetHardwareVersion"] = (404, b"", {})
    with pytest.raises(UnsupportedDeviceError, match="specify hardware"):
        connect("127.0.0.1", base_url=server.url)


def test_cli_offline_catalog_and_description(capsys):
    assert cli.main(["apis", "--product", "timegate", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert len(result) == 39
    assert all(s["product"] == "timegate" for s in result)
    assert cli.main(["--json", "describe", "set_brightness", "--hardware", "530"]) == 0
    assert json.loads(capsys.readouterr().out)["parameters"][0]["wire"] == "Brightness"


def test_cli_json_call_files_and_wire_params(server, tmp_path, capsys):
    path = tmp_path / "parameters.json"
    path.write_text('{"Brightness": 41}', encoding="utf-8")
    result = cli.main(["call", "set_brightness", "--ip", "127.0.0.1", "--hardware", "90",
                       "--base-url", server.url, "--params", "@" + str(path), "--json"])
    assert result == 0
    assert json.loads(capsys.readouterr().out)["ReturnCode"] == 0
    assert server.records[-1]["payload"] == {"Command": "Channel/SetBrightness", "Brightness": 41}


def test_cli_noninteractive_token_error_does_not_leak(server, monkeypatch, capsys):
    monkeypatch.delenv("DIVOOM_LOCAL_TOKEN", raising=False)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    assert cli.main(["call", "get_settings", "--ip", "127.0.0.1", "--hardware", "400",
                     "--base-url", server.url, "--json"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert json.loads(captured.err)["error"] == "TokenRequiredError"
    assert not server.records


def test_cli_empty_discovery_and_selection_by_id(server, capsys):
    server.replies["/discover"] = {"ReturnCode": 0, "DeviceList": []}
    assert cli.main(["discover", "--discovery-url", server.url + "/discover", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == []
    server.replies["/discover"] = {"ReturnCode": 0, "DeviceList": [row(hardware=90, device_id=7),
                                                                  row(hardware=530, device_id=8)]}
    assert cli.main(["call", "get_brightness", "--device-id", "8", "--base-url", server.url,
                     "--discovery-url", server.url + "/discover", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["ReturnCode"] == 0
    assert server.records[-1]["payload"]["Command"] == "Sys/GetBrightness"


def test_cli_timegate_402_does_not_prompt_for_optional_token(server, monkeypatch, capsys):
    monkeypatch.delenv("DIVOOM_LOCAL_TOKEN", raising=False)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    assert cli.main(["call", "get_settings", "--ip", "127.0.0.1", "--hardware", "402",
                     "--base-url", server.url, "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["ReturnCode"] == 0
    assert server.records[-1]["payload"] == {"Command": "Channel/GetAllConf"}


def test_full_interactive_selection_then_call_and_quit(server, monkeypatch, capsys):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.delenv("DIVOOM_LOCAL_TOKEN", raising=False)
    # First try unsupported hardware, then choose TimeGate, run a read, exit.
    devices = [DeviceInfo("same", "127.0.0.1", 700, 1), DeviceInfo("same", "127.0.0.1", 400, 2)]
    monkeypatch.setattr(cli, "_discover", lambda args: devices)
    answers = iter(["1", "2", "get_settings", "{}", "q"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt: "543210")
    assert cli.main(["--base-url", server.url]) == 0
    captured = capsys.readouterr()
    assert "unsupported" in captured.out
    assert "Selected same: timegate" in captured.out
    assert "543210" not in captured.out + captured.err
    assert server.records[-1]["payload"]["LocalToken"] == 543210


def test_cli_stdin_and_invalid_json(server, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"brightness":50}'))
    target = ["--ip", "127.0.0.1", "--hardware", "90", "--base-url", server.url]
    assert cli.main(["call", "set_brightness", *target, "--params", "-"]) == 0
    assert server.records[-1]["payload"]["Brightness"] == 50
    capsys.readouterr()
    assert cli.main(["call", "set_brightness", *target, "--params", "[]", "--json"]) == 2
    captured = capsys.readouterr()
    assert json.loads(captured.err)["error"] == "ValidationError"


def test_cli_no_terminal_never_hangs(monkeypatch, capsys):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    assert cli.main([]) == 2
    assert "terminal" in capsys.readouterr().err
