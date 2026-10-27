from __future__ import annotations

import json
import struct
import time
from email import policy
from email.parser import BytesParser

import pytest

from divoom_wifi import NetworkError, ProtocolError, ValidationError
from divoom_wifi.transfers import MultipartBody, image_info


def multipart_parts(record):
    prefix = ("Content-Type: " + record["headers"]["Content-Type"] + "\r\nMIME-Version: 1.0\r\n\r\n").encode()
    return list(BytesParser(policy=policy.default).parsebytes(prefix + record["raw"]).iter_parts())


def test_multipart_first_block_and_lengths(images):
    metadata = {"Command": "Photo/LocalAddToAlbum", "PhotoTitle": "中文标题"}
    with MultipartBody(metadata, [(images.jpeg, images.jpeg.name, "image/jpeg"),
                                  (images.webp, images.webp.name, "image/webp")], chunk_size=7) as body:
        blocks = list(body)
        assert json.dumps(metadata, ensure_ascii=False, separators=(",", ":")).encode() in blocks[0]
        assert blocks[0].count(("--" + body.boundary).encode()) == 2
        assert b'filename="unique-photo.jpg"' in blocks[0]
        assert sum(map(len, blocks)) == len(body)
        raw = b"".join(blocks)
        parts = multipart_parts({"headers": {"Content-Type": body.content_type}, "raw": raw})
        assert len(parts) == 3
        for part in parts:
            assert int(part["Content-Length"]) == len(part.get_payload(decode=True))
        assert parts[1].get_payload(decode=True) == images.jpeg.read_bytes()
        assert parts[2].get_payload(decode=True) == images.webp.read_bytes()
        with pytest.raises(ValidationError, match="retried"):
            list(body)


def test_real_http_media_metadata_and_video_preview(make_client, server, images):
    astro = make_client()
    astro.upload_media(file_path=images.video, clock_id=110001, photo_width=480, photo_height=480,
                       preview_path=images.webp, video_duration=30, photo_title="中文标题")
    record = server.records[-1]
    parts = multipart_parts(record)
    assert record["path"] == "/upload"
    assert record["headers"].get("Transfer-Encoding") is None
    assert int(record["headers"]["Content-Length"]) == len(record["raw"])
    metadata = json.loads(parts[0].get_payload(decode=True))
    assert metadata["Command"] == "Photo/LocalAddToAlbum"
    assert metadata["FileName"] == images.video.name
    assert metadata["PreviewFileName"] == images.webp.name
    assert metadata["ParentItemId"] == metadata["UserId"] == 0
    assert metadata["SendTime"] > 1000000000000
    assert "video_duration" not in metadata
    assert parts[1].get_payload(decode=True) == images.video.read_bytes()
    assert parts[2].get_payload(decode=True) == images.webp.read_bytes()
    assert [r["payload"]["Command"] for r in server.records if r["payload"]] == ["Device/GetLanCapabilities"]


@pytest.mark.parametrize("args", [
    {"video_duration": 1801, "photo_width": 480, "photo_height": 480},
    {"video_duration": 30}, {"video_duration": 30, "photo_width": 480, "photo_height": 480},
])
def test_video_requirements_reject_before_upload(args, make_client, server, images):
    with pytest.raises(ValidationError):
        make_client().upload_media(file_path=images.video, clock_id=110001, **args)
    assert not any(r["path"] == "/upload" for r in server.records)


def test_dynamic_capability_limits_and_utf8_lengths(make_client, server, images):
    astro = make_client()
    astro.get_lan_capabilities()
    astro.capabilities["PhotoUploadMaxBytes"] = 10
    with pytest.raises(ValidationError, match="body"):
        astro.upload_media(file_path=images.jpeg, clock_id=110001)
    astro.capabilities["PhotoUploadMaxBytes"] = 536870912
    with pytest.raises(ValidationError, match="PhotoTitle"):
        astro.upload_media(file_path=images.jpeg, clock_id=110001, photo_title="中" * 171)
    with pytest.raises(ValidationError, match="filenames"):
        astro.upload_media(file_path=images.jpeg, clock_id=110001, file_name="中" * 43 + ".jpg")
    assert not any(r["path"] == "/upload" for r in server.records)


def test_background_dimensions_formats_and_exclusive_size(make_client, images):
    astro = make_client()
    with pytest.raises(ValidationError, match="480x480"):
        astro.replace_clock_background(file_path=images.png, clock_id=60001)
    astro.get_lan_capabilities()
    astro.capabilities["BackgroundMaxBytesExclusive"] = images.jpeg.stat().st_size
    with pytest.raises(ValidationError, match="smaller"):
        astro.upload_clock_asset(file_path=images.jpeg)


def test_clock_create_constants_and_asset_no_double_command(make_client, server, images):
    astro = make_client()
    astro.create_local_clock(file_path=images.jpeg, clock_name="Desk", item_list=[{"disp": 4}])
    parts = multipart_parts(server.records[-1])
    metadata = json.loads(parts[0].get_payload(decode=True))
    assert metadata == {"Command": "Device/CreateLocalClock", "ReturnCode": 0, "ClockName": "Desk",
                        "DialAssets": "image", "ItemList": [{"disp": 4}]}
    astro.upload_clock_asset(file_path=images.png)
    assert server.records[-1]["path"] == "/upload_local_asset"
    assert len([r for r in server.records if r["path"] == "/divoom_api"]) == 1  # capability read only


def test_download_head_and_existing_file_preserved(make_client, server, tmp_path):
    astro = make_client()
    target = tmp_path / "media.bin"
    assert astro.download_media(path="/userdata/hello%20world.bin", destination=target) == target
    assert target.read_bytes() == b"\x00media-bytes\xff"
    headers = astro.head_media(path="/userdata/hello%20world.bin")
    assert int(headers["Content-Length"]) == len(b"\x00media-bytes\xff")
    assert server.records[-1]["method"] == "HEAD"
    with pytest.raises(FileExistsError):
        astro.download_media(path="/userdata/hello.bin", destination=target)
    assert target.read_bytes() == b"\x00media-bytes\xff"


@pytest.mark.parametrize("path", ["http://elsewhere/file", "//elsewhere/file", "/userdata/../private",
                                   "/userdata/%2e%2e/private", "/etc/passwd", "/userdata/test?redirect=elsewhere"])
def test_download_paths_remain_on_selected_device(path, make_client, server, tmp_path):
    with pytest.raises(ValidationError):
        make_client().download_media(path=path, destination=tmp_path / "no.bin")
    assert not any(r["path"].startswith("/userdata/") for r in server.records)


def test_wait_for_photo_uses_returned_original_path_and_pagination(make_client, server):
    calls = []
    def photos(record):
        start = record["payload"]["StartNum"]
        calls.append(start)
        if len(calls) == 1:
            return {"ReturnCode": 0, "PhotoList": []}
        if start == 1:
            return {"ReturnCode": 0, "PhotoList": [{"PhotoId": i} for i in range(100)]}
        return {"ReturnCode": 0, "PhotoList": [{"PhotoId": 101, "OriginalFileId": "/userdata/album/new%20photo.jpg"}]}
    server.replies["Photo/GetPhotoList"] = photos
    photo = make_client().wait_for_photo(clock_id=110001, file_name="new photo.jpg", poll_interval=0.001)
    assert photo["PhotoId"] == 101
    assert calls == [1, 1, 101]
    assert all(r["payload"]["Command"] in ("Photo/GetPhotoList", "Device/GetLanCapabilities") for r in server.records)


def test_poll_timeout_does_not_upload_or_retry_writes(make_client, server):
    server.replies["Photo/GetPhotoList"] = {"ReturnCode": 0, "PhotoList": []}
    started = time.monotonic()
    with pytest.raises(NetworkError, match="not retried"):
        make_client().wait_for_photo(clock_id=110001, photo_id=123, timeout=0.04, poll_interval=0.005)
    assert time.monotonic() - started < 0.5
    assert all(r["payload"]["Command"] in ("Photo/GetPhotoList", "Device/GetLanCapabilities") for r in server.records)


def test_poll_requires_well_formed_photo_list(make_client, server):
    server.replies["Photo/GetPhotoList"] = {"ReturnCode": 0}
    with pytest.raises(ProtocolError):
        make_client().wait_for_photo(clock_id=110001, photo_id=1)


def test_image_header_dimensions_and_corruption(images, tmp_path):
    assert image_info(images.jpeg) == ("jpeg", 480, 480)
    assert image_info(images.png) == ("png", 32, 48)
    assert image_info(images.webp) == ("webp", 480, 480)
    gif = tmp_path / "tiny.gif"
    gif.write_bytes(b"GIF89a" + struct.pack("<HH", 10, 20))
    assert image_info(gif) == ("gif", 10, 20)
    corrupt = tmp_path / "bad.jpg"
    corrupt.write_bytes(b"\xff\xd8\xff\xc0\x00\x11")
    with pytest.raises(ValidationError):
        image_info(corrupt)
