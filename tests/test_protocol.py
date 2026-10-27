from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
import requests

from divoom_wifi import (
    AstroToo,
    DeviceError,
    DeviceInfo,
    HTTPError,
    NetworkError,
    Pixoo64,
    ProtocolError,
    TimeFrame,
    TimeGate,
    TokenRequiredError,
    UnsupportedAPIError,
    UnsupportedDeviceError,
    ValidationError,
    connect,
)
from divoom_wifi.models import PROFILES
from divoom_wifi.registry import load_registry

SPECS = [spec for product in load_registry().values() for spec in product.values()]
HARDWARE = {"pixoo64": 90, "timegate": 400, "timeframe": 510, "astrotoo": 530}


def values_for(spec, images, mode):
    special = {"ClockId": 110001, "ToClockId": 110002, "PhotoId": 123,
               "StartNum": 1, "EndNum": 100, "Brightness": 40, "Minute": 2, "Second": 3,
               "PicNum": 1, "PicWidth": 64, "PicOffset": 0, "PicID": 1, "PicSpeed": 100,
               "LcdArray": [1, 0, 0, 0, 0], "ItemList": [{"disp": 4, "item_id": "clock"}],
               "ItemPatchList": [{"index": 0, "patch": {"color_1": "#FFFFFF"}}],
               "DispList": [{"ID": 1, "Type": "Text", "TextMessage": "中文 text"}],
               "LightList": [{"SelectEffect": 1}], "PhotoList": [123], "PhotoIndex": 0,
               "PhotoTotalCnt": 1, "PhotoWidth": 480, "PhotoHeight": 480,
               "PreviewFileName": "", "Color": "#FFFFFF", "UseCurrentDisplayClock": 0,
               "file_path": str(images.jpeg), "path": "/userdata/app_pic/photo.jpg",
               "destination": str(images.root / f"download-{mode}.bin")}
    params = {}
    for p in spec.parameters:
        if p.auto or p.name in ("preview_path", "video_duration"):
            continue
        value = special.get(p.wire, p.default)
        if value is None:
            value = {"str": "Divoom", "int": 1, "float": 1000.0, "list": ["a"], "dict": {}, "bool": True}.get(p.type)
        if spec.name == "upload_media" and p.wire == "FileName":
            value = images.jpeg.name
        params[p.name if mode == "named" else p.wire] = value
    return params


@pytest.mark.parametrize("mode", ["named", "wire"])
@pytest.mark.parametrize("spec", SPECS, ids=lambda s: s.product + "." + s.name)
def test_every_registered_operation_over_real_http(spec, mode, make_client, server, images):
    client = make_client(HARDWARE[spec.product])
    params = values_for(spec, images, mode)
    result = getattr(client, spec.name)(**params) if mode == "named" else client.call(spec.name, **params)
    record = server.records[-1]
    assert record["method"] == spec.method
    if spec.route == "cloud":
        assert client.cloud_urls[-1] == spec.url
    elif spec.route in ("download", "head"):
        assert record["path"] == "/userdata/app_pic/photo.jpg"
        assert not record["raw"]
    elif spec.route == "upload":
        assert record["path"] == spec.path
        assert int(record["headers"]["Content-Length"]) == len(record["raw"])
        assert "Transfer-Encoding" not in record["headers"]
        assert images.jpeg.read_bytes() in record["raw"]
        metadata = record["raw"].split(b"\r\n\r\n", 1)[1].split(b"\r\n--", 1)[0]
        assert json.loads(metadata)["Command"] == spec.command
    else:
        assert record["path"] == PROFILES[HARDWARE[spec.product]].path
    if spec.route in ("cloud", "lan"):
        body = record["payload"]
        assert body.get("Command") == spec.command
        for p in spec.parameters:
            expected = (getattr(client.device, p.auto) if p.auto
                        else params.get(p.name if mode == "named" else p.wire))
            assert body[p.wire] == expected
        token_expected = spec.route == "lan" and client.profile.local_token_required
        assert ("LocalToken" in body or "DeviceToken" in body) == token_expected
        if token_expected:
            assert body[client.profile.token_field] == 123456
        assert result["business"] == {"unchanged": True} if spec.name not in ("get_hardware_version", "get_lan_capabilities") else result["Hardware"] == 530
    if spec.route == "download":
        assert Path(result).read_bytes() == b"\x00media-bytes\xff"


@pytest.mark.parametrize("hw,cls,port,path,method", [
    (90, Pixoo64, 80, "/post", "POST"), (92, Pixoo64, 80, "/post", "POST"),
    (96, Pixoo64, 9000, "/divoom_api", "POST"), (400, TimeGate, 80, "/post", "POST"),
    (402, TimeGate, 9000, "/divoom_api", "POST"), (510, TimeFrame, 9000, "/divoom_api", "GET"),
    (511, TimeFrame, 9000, "/divoom_api", "GET"), (512, TimeFrame, 9000, "/divoom_api", "GET"),
    (530, AstroToo, 9000, "/divoom_api", "POST"),
])
def test_all_hardware_routes(hw, cls, port, path, method, make_client, server):
    with connect(DeviceInfo("Completely renamed", "192.0.2.1", hw)) as default:
        assert isinstance(default, cls)
        assert default.base_url == f"http://192.0.2.1:{port}"
    client = make_client(hw)
    client.set_brightness(brightness=42)
    record = server.records[-1]
    assert (record["method"], record["path"], record["payload"]["Brightness"]) == (method, path, 42)


@pytest.mark.parametrize("result,error", [
    ({}, ProtocolError), ({"ReturnCode": "0"}, ProtocolError), ({"ReturnCode": False}, ProtocolError),
    ([0], ProtocolError), ({"ReturnCode": 17, "ReturnMessage": "rejected"}, DeviceError),
    ({"ReturnCode": 0, "error_code": 4}, DeviceError),
])
def test_status_validation(result, error, make_client, server):
    server.replies["Channel/SetBrightness"] = result
    with pytest.raises(error) as info:
        make_client(90).set_brightness(brightness=20)
    assert info.value.api_name == "set_brightness"
    assert info.value.response == result


@pytest.mark.parametrize("reply,error", [(b"not-json", ProtocolError), ((500, b"failed", {}), HTTPError),
                                          ((302, b"", {"Location": "/post"}), HTTPError)])
def test_http_invalid_json_and_no_redirects(reply, error, make_client, server):
    server.replies["Channel/SetBrightness"] = reply
    with pytest.raises(error):
        make_client(90).set_brightness(brightness=20)
    assert len(server.records) == 1


def test_timeout_write_is_never_retried(make_client, server):
    server.delay = 0.15
    with pytest.raises(NetworkError):
        make_client(510, timeout=0.03).set_brightness(brightness=40)
    time.sleep(0.2)
    assert len(server.records) == 1
    assert server.records[0]["method"] == "GET"


def test_connection_error_preserves_cause(make_client, monkeypatch):
    client = make_client(90)
    def fail(*a, **kw):
        raise requests.ConnectionError("test")
    monkeypatch.setattr(client._transport._local, "request", fail)
    with pytest.raises(NetworkError) as info:
        client.get_settings()
    assert isinstance(info.value.__cause__, requests.ConnectionError)


def test_unknown_hardware_and_wrong_product_are_rejected(server):
    for hardware in (700, 123):
        with pytest.raises(UnsupportedDeviceError):
            connect("127.0.0.1", hardware=hardware)
    with pytest.raises(UnsupportedDeviceError):
        AstroToo(DeviceInfo("AstroToo", "127.0.0.1", 90))
    assert not server.records


def test_unsupported_api_and_invalid_parameters_do_not_send(make_client, server):
    client = make_client(90)
    with pytest.raises(UnsupportedAPIError):
        client.call("upload_media")
    for params in ({"brightness": -1}, {"brightness": 101}, {"brightness": True}, {},
                   {"brightness": 20, "Brightness": 20}, {"brightness": 20, "typo": 1}):
        with pytest.raises(ValidationError):
            client.call("set_brightness", **params)
    assert not server.records


def test_tokens_are_injected_only_where_documented(make_client, server, monkeypatch):
    monkeypatch.delenv("DIVOOM_LOCAL_TOKEN", raising=False)
    gate = make_client(400, local_token=None)
    with pytest.raises(TokenRequiredError):
        gate.set_brightness(brightness=40)
    assert not server.records
    monkeypatch.setenv("DIVOOM_LOCAL_TOKEN", "654321")
    gate = make_client(400, local_token=None)
    gate.set_brightness(brightness=40)
    assert server.records[-1]["payload"]["LocalToken"] == 654321
    gate.get_uploaded_images()
    assert server.records[-1]["payload"] == {"DeviceId": 300000001, "DeviceMac": "aabbccddeeff", "Page": 1}
    assert "654321" not in str(gate.describe_api("set_brightness").as_dict())


@pytest.mark.parametrize("hardware,field", [(90, "DeviceToken"), (92, "DeviceToken"), (400, "LocalToken")])
def test_legacy_lan_requires_token_but_cloud_does_not(hardware, field, make_client, server, monkeypatch):
    monkeypatch.delenv("DIVOOM_LOCAL_TOKEN", raising=False)
    client = make_client(hardware, local_token=None)
    with pytest.raises(TokenRequiredError):
        client.get_settings()
    assert not server.records
    client.get_uploaded_images()
    assert not {"DeviceToken", "LocalToken"}.intersection(server.records[-1]["payload"])
    client.set_local_token(654321)
    client.get_settings()
    assert server.records[-1]["payload"] == {"Command": "Channel/GetAllConf", field: 654321}


@pytest.mark.parametrize("hardware", [96, 402, 510, 511, 512, 530])
@pytest.mark.parametrize("token", [None, 654321])
def test_other_hardware_does_not_require_or_send_tokens(hardware, token, make_client, server, monkeypatch):
    monkeypatch.delenv("DIVOOM_LOCAL_TOKEN", raising=False)
    client = make_client(hardware, local_token=token)
    client.set_brightness(brightness=40)
    assert server.records[-1]["payload"] == {"Command": "Channel/SetBrightness", "Brightness": 40}


@pytest.mark.parametrize("hardware", [400, 402])
def test_partial_rgb_settings_do_not_depend_on_token_field_count(hardware, make_client, server):
    client = make_client(hardware)
    with pytest.raises(ValidationError, match="at least one RGB"):
        client.set_rgb()
    client.set_rgb(on_off=0)
    expected = {"Command": "Channel/SetRGBInfo", "OnOff": 0}
    if hardware == 400:
        expected["LocalToken"] = 123456
    assert server.records[-1]["payload"] == expected


def test_conditional_clock_target_and_channel_type(make_client, server):
    astro = make_client()
    with pytest.raises(ValidationError):
        astro.patch_local_clock(clock_name="Name")
    assert not server.records
    astro.patch_local_clock(use_current_display_clock=1, clock_name="Name")
    assert "ClockId" not in server.records[-1]["payload"]
    gate = make_client(400)
    gate.select_channel_type(channel_type=0)
    assert "LcdIndependence" not in server.records[-1]["payload"]
    with pytest.raises(ValidationError):
        gate.select_channel_type(channel_type=1)


def test_timegate_402_can_send_without_token(make_client, server, monkeypatch):
    monkeypatch.delenv("DIVOOM_LOCAL_TOKEN", raising=False)
    gate = make_client(402, local_token=None)
    assert not gate.profile.local_token_required
    gate.get_settings()
    assert server.records[-1]["path"] == "/divoom_api"
    assert server.records[-1]["payload"] == {"Command": "Channel/GetAllConf"}
    gate.set_brightness(brightness=40)
    assert server.records[-1]["payload"] == {"Command": "Channel/SetBrightness", "Brightness": 40}
    assert make_client(400).profile.local_token_required


def test_timeframe_fonts_inject_documentation_omission(make_client, server):
    frame = make_client(510)
    frame.get_fonts()
    assert frame.cloud_urls[-1] == "https://appin.divoom-gz.com/Device/GetTimeDialFontV2"
    assert server.records[-1]["payload"] == {"DeviceId": 300000001}
    with connect("127.0.0.1", hardware=510, base_url=server.url) as direct:
        before = len(server.records)
        with pytest.raises(ValidationError, match="device_id"):
            direct.get_fonts()
        assert len(server.records) == before


def test_json_utf8_limit_and_nonfinite_values(make_client, server):
    astro = make_client()
    astro.get_lan_capabilities()
    server.records.clear()
    with pytest.raises(ValidationError):
        astro.patch_local_clock(clock_id=60001, item_patch_list=[{"text": "中" * 22000}])
    assert not server.records
    with pytest.raises(ValidationError):
        make_client(90).send_display_list(item_list=[{"value": float("nan")}])
    assert not server.records


def test_capability_query_and_response_size(make_client, server):
    astro = make_client()
    astro.get_brightness()
    assert [r["payload"]["Command"] for r in server.records] == ["Device/GetLanCapabilities", "Sys/GetBrightness"]
    server.replies["Sys/GetBrightness"] = {"ReturnCode": 0, "data": "x" * 65536}
    with pytest.raises(ProtocolError):
        astro.get_brightness()


def test_same_origin_serialized_across_client_instances(make_client, server):
    server.delay = 0.02
    clients = [make_client(90) for _ in range(4)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda c: c.get_settings(), clients))
    assert len(results) == 4
    assert server.max_active == 1


def test_close_and_positive_timeouts(make_client):
    with pytest.raises(ValidationError):
        make_client(90, timeout=0)
    client = make_client(90)
    client.close()
    with pytest.raises(ValidationError, match="closed"):
        client.get_settings()


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), -1, True])
def test_invalid_timeouts_are_validation_errors(timeout, make_client):
    with pytest.raises(ValidationError, match="finite positive"):
        make_client(90, timeout=timeout)
