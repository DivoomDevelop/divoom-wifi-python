"""AstroToo streaming multipart and device-local file downloads."""
from __future__ import annotations

import math
import mimetypes
import secrets
import shutil
import struct
import tempfile
import time
from collections.abc import Iterator
from contextlib import ExitStack
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Self
from urllib.parse import quote, unquote, urlsplit
from uuid import uuid4

from .errors import ProtocolError, ValidationError
from .registry import APISpec
from .transport import json_bytes

if TYPE_CHECKING:
    from .client import BaseDevice


def image_info(path: Path) -> tuple[str, int, int]:
    """Read dimensions without loading an entire image or claiming codec validation."""
    with path.open("rb") as stream:
        header = stream.read(32)
        if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
            width, height = struct.unpack(">II", header[16:24])
            kind = "png"
        elif header[:6] in (b"GIF87a", b"GIF89a") and len(header) >= 10:
            width, height = struct.unpack("<HH", header[6:10])
            kind = "gif"
        elif header.startswith(b"BM") and len(header) >= 26:
            dib = struct.unpack("<I", header[14:18])[0]
            if dib == 12:
                width, height = struct.unpack("<HH", header[18:22])
            elif dib >= 40:
                stream.seek(18)
                width, height = struct.unpack("<ii", stream.read(8))
                height = abs(height)
            else:
                raise ValidationError("Unsupported BMP header")
            kind = "bmp"
        elif header.startswith(b"\xff\xd8"):
            stream.seek(2)
            while True:
                byte = stream.read(1)
                if byte != b"\xff":
                    raise ValidationError("Invalid JPEG dimensions/header")
                marker = stream.read(1)
                while marker == b"\xff":
                    marker = stream.read(1)
                if marker in (b"\xd8", b"\x01") or (marker and 0xD0 <= marker[0] <= 0xD7):
                    continue
                if not marker or marker in (b"\xda", b"\xd9"):
                    raise ValidationError("JPEG has no supported size header")
                length_bytes = stream.read(2)
                if len(length_bytes) != 2:
                    raise ValidationError("Truncated JPEG segment")
                length = struct.unpack(">H", length_bytes)[0]
                if length < 2:
                    raise ValidationError("Invalid JPEG segment length")
                if marker[0] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    frame = stream.read(5)
                    if len(frame) != 5:
                        raise ValidationError("Truncated JPEG frame")
                    height, width = struct.unpack(">HH", frame[1:5])
                    break
                stream.seek(length - 2, 1)
            kind = "jpeg"
        elif header.startswith(b"RIFF") and header[8:12] == b"WEBP":
            stream.seek(12)
            while True:
                chunk = stream.read(8)
                if len(chunk) != 8:
                    raise ValidationError("WebP has no supported size header")
                chunk_type, length = chunk[:4], int.from_bytes(chunk[4:], "little")
                data = stream.read(min(length, 10))
                if chunk_type == b"VP8X" and len(data) >= 10:
                    width = 1 + int.from_bytes(data[4:7], "little")
                    height = 1 + int.from_bytes(data[7:10], "little")
                    break
                if chunk_type == b"VP8 " and len(data) >= 10 and data[3:6] == b"\x9d\x01\x2a":
                    width, height = (v & 0x3FFF for v in struct.unpack("<HH", data[6:10]))
                    break
                if chunk_type == b"VP8L" and len(data) >= 5 and data[0] == 0x2F:
                    bits = int.from_bytes(data[1:5], "little")
                    width, height = 1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF)
                    break
                stream.seek(length - len(data) + (length & 1), 1)
            kind = "webp"
        else:
            raise ValidationError("Image must have a JPEG, PNG, WebP, BMP or GIF header; no transcoding is performed")
    if width <= 0 or height <= 0:
        raise ValidationError("Image dimensions must be positive")
    return kind, width, height


def _filename(value: str) -> str:
    if (not value or value in (".", "..") or any(c in value for c in '/\\"\r\n\x00')
            or any(ord(c) < 32 for c in value) or len(value.encode("utf-8")) >= 128):
        raise ValidationError("Multipart filenames must be bare names below 128 UTF-8 bytes without control characters")
    return value


class MultipartBody:
    """One-shot iterable with a known total length and complete metadata in block 1.

    Open descriptors pin input files for the transfer. Every part includes its
    byte length. Content-Length avoids HTTP chunked transfer encoding.
    TCP fragmentation itself remains under the OS/network's control.
    """

    def __init__(self, metadata: dict[str, Any], files: list[tuple[Path, str, str]], *, chunk_size: int = 65536):
        self.boundary = "DivoomPython" + uuid4().hex
        self.content_type = "multipart/form-data; boundary=" + self.boundary
        self.chunk_size = chunk_size
        self._stack = ExitStack()
        self._files: list[tuple[BinaryIO, int, bytes]] = []
        self._used = False
        blob = json_bytes(metadata)
        self._json = (f"--{self.boundary}\r\n"
                      'Content-Disposition: form-data; name="json"\r\n'
                      "Content-Type: application/json; charset=utf-8\r\n"
                      f"Content-Length: {len(blob)}\r\n\r\n").encode() + blob + b"\r\n"
        self._closing = f"\r\n--{self.boundary}--\r\n".encode()
        try:
            for path, name, mime in files:
                name = _filename(name)
                stream = self._stack.enter_context(path.open("rb"))
                size = stream.seek(0, 2)
                stream.seek(0)
                header = (f"--{self.boundary}\r\n"
                          f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
                          f"Content-Type: {mime}\r\nContent-Length: {size}\r\n\r\n").encode()
                self._files.append((stream, size, header))
        except BaseException:
            self.close()
            raise
        if not self._files:
            self.close()
            raise ValidationError("Multipart requires at least one file")
        self._length = (len(self._json) + sum(size + len(header) for _, size, header in self._files)
                        + 2 * (len(self._files) - 1) + len(self._closing))

    def __len__(self) -> int:
        return self._length

    def __iter__(self) -> Iterator[bytes]:
        if self._used:
            raise ValidationError("Multipart bodies cannot be retried/reused")
        self._used = True
        for index, (stream, size, header) in enumerate(self._files):
            # First body send includes the entire JSON part AND the next boundary/header.
            yield self._json + header if index == 0 else b"\r\n" + header
            remaining = size
            while remaining:
                chunk = stream.read(min(self.chunk_size, remaining))
                if not chunk:
                    raise ValidationError("Input file changed/truncated during upload; request was not retried")
                remaining -= len(chunk)
                yield chunk
            if stream.read(1):
                raise ValidationError("Input file grew during upload; request was not retried")
        yield self._closing

    def close(self) -> None:
        self._stack.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def _cap(client: BaseDevice, name: str, maximum: int) -> int:
    value = client.capabilities.get(name, maximum)
    if type(value) is not int or value <= 0:
        raise ProtocolError(f"Invalid capability: {name}")
    return min(value, maximum)


def upload(client: BaseDevice, spec: APISpec, payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload)
    path = Path(payload.pop("file_path"))
    if not path.is_file() or path.stat().st_size == 0:
        raise ValidationError("Upload file must be a nonempty regular file", api_name=spec.name)
    preview = payload.pop("preview_path", None)
    duration = payload.pop("video_duration", None)
    files = []
    media = spec.name == "upload_media"
    if media:
        if client.capabilities.get("SupportsPhotoLibrary") is False:
            raise ValidationError("Device reports no photo library support", api_name=spec.name)
        video = duration is not None or preview is not None or path.suffix.lower() in (".mp4", ".mov", ".m4v", ".avi", ".webm", ".mkv")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if video:
            maximum = _cap(client, "PhotoVideoMaxSeconds", 1800)
            if type(duration) not in (int, float) or not math.isfinite(duration) or not 0 < duration <= maximum:
                raise ValidationError(f"Video requires a declared video_duration in (0, {maximum}] seconds", api_name=spec.name)
            if preview is None:
                raise ValidationError("Video requires preview_path (WebP)", api_name=spec.name)
            preview = Path(preview)
            if not preview.is_file() or image_info(preview)[0] != "webp":
                raise ValidationError("Video preview must be a WebP file", api_name=spec.name)
            if any(type(payload.get(key)) is not int or payload[key] <= 0 for key in ("PhotoWidth", "PhotoHeight")):
                raise ValidationError("Video requires positive photo_width and photo_height", api_name=spec.name)
            preview_name = _filename(payload.get("PreviewFileName") or preview.name)
            payload["PreviewFileName"] = preview_name
            files.append((preview, preview_name, "image/webp"))
        else:
            kind, width, height = image_info(path)
            for field, actual in (("PhotoWidth", width), ("PhotoHeight", height)):
                if field in payload and payload[field] != actual:
                    raise ValidationError(f"{field} does not match actual image dimensions", api_name=spec.name)
                payload[field] = actual
            if payload.get("PreviewFileName"):
                raise ValidationError("Images require an empty PreviewFileName", api_name=spec.name)
            payload["PreviewFileName"] = ""
            mime = "image/" + kind
        name = _filename(payload.get("FileName") or path.name)
        payload["FileName"] = name
        if files and files[0][1] == name:
            raise ValidationError("Media and preview filenames must differ", api_name=spec.name)
        files.insert(0, (path, name, mime))
        if len(payload["PhotoTitle"].encode("utf-8")) >= 512:
            raise ValidationError("PhotoTitle must be below 512 UTF-8 bytes", api_name=spec.name)
        if not 0 <= payload["PhotoIndex"] < payload["PhotoTotalCnt"]:
            raise ValidationError("Require 0 <= PhotoIndex < PhotoTotalCnt", api_name=spec.name)
        now = int(time.time() * 1000)
        payload.setdefault("SendTime", now)
        payload.setdefault("TakingTime", now)
        payload.setdefault("PhotoFlag", secrets.randbelow(2147483646) + 1)
    else:
        kind, width, height = image_info(path)
        maximum = _cap(client, "BackgroundMaxBytesExclusive", 512000)
        if path.stat().st_size >= maximum:
            raise ValidationError(f"Clock image must be smaller than {maximum} bytes", api_name=spec.name)
        if spec.name == "upload_clock_asset":
            if kind not in ("jpeg", "png", "webp") or max(width, height) > 1024:
                raise ValidationError("Clock asset must be JPEG/PNG/WebP no larger than 1024x1024", api_name=spec.name)
        elif kind not in ("jpeg", "webp") or (width, height) != (480, 480):
            raise ValidationError("Clock background must be a 480x480 JPEG or WebP", api_name=spec.name)
        files.append((path, _filename(path.name), "image/" + kind))
    if len(json_bytes(payload)) > client.json_limit:
        raise ValidationError("Multipart JSON metadata exceeds device limit", api_name=spec.name)
    with MultipartBody(payload, files) as body:
        if media and len(body) > _cap(client, "PhotoUploadMaxBytes", 536870912):
            raise ValidationError("Complete upload body exceeds PhotoUploadMaxBytes", api_name=spec.name)
        with client._transport.response("POST", client.base_url + spec.path, api_name=spec.name,
                                        data=body, headers={"Content-Type": body.content_type,
                                                            "Content-Length": str(len(body))},
                                        timeout=client._transport.upload_timeout) as response:
            return client._transport.decode_json(response, spec.name, spec.status_fields, client.json_limit)


def media_url(origin: str, path: str) -> str:
    parts = urlsplit(path)
    decoded = unquote(path)
    if (parts.scheme or parts.netloc or parts.query or parts.fragment or not path.startswith("/userdata/")
            or "\\" in decoded or "\x00" in decoded or any(c in decoded for c in "\r\n")
            or any(segment in ("..", ".") for segment in decoded.split("/"))):
        raise ValidationError("Use an exact device-returned /userdata/ path on the selected device")
    return origin + quote(path, safe="/%:@")


def download(client: BaseDevice, spec: APISpec, payload: dict[str, Any]) -> Path | dict[str, str]:
    url = media_url(client.base_url, payload["path"])
    if spec.route == "head":
        with client._transport.response("HEAD", url, api_name=spec.name) as response:
            return dict(response.headers)
    target = Path(payload["destination"])
    if target.exists():
        raise FileExistsError(f"Destination already exists: {target}")
    # Stage network data before creating the destination; exclusive creation
    # protects a file another process creates while the download is in flight.
    with tempfile.TemporaryFile(dir=target.parent) as staged:
        with client._transport.response("GET", url, api_name=spec.name) as response:
            for chunk in response.iter_content(65536):
                staged.write(chunk)
        staged.seek(0)
        with target.open("xb") as output:
            shutil.copyfileobj(staged, output, length=65536)
    return target
