from __future__ import annotations

import json
import struct
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit

import pytest
import requests

from divoom_wifi import DeviceInfo, connect

CAPS = {"ReturnCode": 0, "Hardware": 530, "JsonMaxBytes": 65536, "SupportsPhotoLibrary": True,
        "PhotoUploadMaxBytes": 536870912, "PhotoVideoMaxSeconds": 1800,
        "BackgroundMaxBytesExclusive": 512000, "CanvasWidth": 480, "CanvasHeight": 480}


@pytest.fixture(scope="session")
def http_server():
    state = SimpleNamespace(records=[], replies={}, delay=0, active=0, max_active=0, guard=threading.Lock())

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def handle_request(self):
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            try:
                payload = json.loads(raw) if raw and "application/json" in self.headers.get("Content-Type", "") else None
            except ValueError:
                payload = None
            record = {"method": self.command, "path": self.path, "headers": dict(self.headers),
                      "raw": raw, "payload": payload}
            with state.guard:
                state.records.append(record)
                state.active += 1
                state.max_active = max(state.max_active, state.active)
            try:
                if state.delay:
                    time.sleep(state.delay)
                key = payload.get("Command") if payload else self.path
                reply = state.replies.get(key)
                if callable(reply):
                    reply = reply(record)
                if reply is None:
                    if self.path.startswith("/userdata/"):
                        reply = b"\x00media-bytes\xff"
                    elif key in ("Device/GetLanCapabilities", "Device/GetHardwareVersion"):
                        reply = CAPS
                    else:
                        reply = {"ReturnCode": 0, "error_code": 0, "business": {"unchanged": True}}
                status, response_headers = 200, {}
                if isinstance(reply, tuple):
                    status, reply, response_headers = reply
                body = reply if isinstance(reply, bytes) else json.dumps(reply, ensure_ascii=False).encode()
                self.send_response(status)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Content-Type", "application/json" if isinstance(reply, dict) else "application/octet-stream")
                for k, v in response_headers.items():
                    self.send_header(k, v)
                self.end_headers()
                if self.command != "HEAD":
                    try:
                        self.wfile.write(body)
                    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                        pass  # Expected timeout tests disconnect while the fixture is delayed.
            finally:
                with state.guard:
                    state.active -= 1

        do_GET = handle_request
        do_POST = handle_request
        do_HEAD = handle_request

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    state.url = f"http://127.0.0.1:{server.server_port}"
    yield state
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.fixture
def server(http_server):
    # Previous timeout tests can leave a delayed handler finishing; wait for it.
    deadline = time.monotonic() + 2
    while http_server.active and time.monotonic() < deadline:
        time.sleep(0.005)
    http_server.records.clear()
    http_server.replies.clear()
    http_server.delay = 0
    http_server.max_active = 0
    return http_server


@pytest.fixture(autouse=True)
def no_external_network(monkeypatch):
    original = requests.Session.request

    def local_only(self, method, url, **kwargs):
        if urlsplit(url).hostname not in ("127.0.0.1", "localhost"):
            raise AssertionError(f"Tests must not access external services/devices: {url}")
        return original(self, method, url, **kwargs)
    monkeypatch.setattr(requests.Session, "request", local_only)


@pytest.fixture
def make_client(server):
    clients = []

    def make(hardware=530, **kwargs):
        info = DeviceInfo("Renamed device", "127.0.0.1", hardware, 300000001, "aabbccddeeff")
        client = connect(info, base_url=server.url, local_token=kwargs.pop("local_token", 123456), **kwargs)
        client._transport._cloud.trust_env = False  # Local HTTP fixture must not use CI environment proxies.
        client.cloud_urls = []
        original = client._transport._cloud.request

        def cloud_request(method, url, **options):
            client.cloud_urls.append(url)
            return original(method, server.url + "/cloud" + urlsplit(url).path, **options)
        client._transport._cloud.request = cloud_request
        clients.append(client)
        return client
    yield make
    for client in clients:
        client.close()


@pytest.fixture
def images(tmp_path):
    # Header-only fixtures exercise dimensions/wire bytes, not firmware decoding.
    jpeg = tmp_path / "unique-photo.jpg"
    jpeg.write_bytes(b"\xff\xd8\xff\xc0\x00\x11\x08" + struct.pack(">HH", 480, 480) + b"\x03" + b"\x00" * 9 + b"\xff\xd9")
    png = tmp_path / "element.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 32, 48) + b"\x00" * 12)
    webp = tmp_path / "preview.webp"
    chunk = b"\x00" * 4 + (479).to_bytes(3, "little") * 2
    webp.write_bytes(b"RIFF" + (22).to_bytes(4, "little") + b"WEBPVP8X\x0a\x00\x00\x00" + chunk)
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"fake-video-for-wire-tests" * 10000)
    return SimpleNamespace(jpeg=jpeg, png=png, webp=webp, video=video, root=Path(tmp_path))
