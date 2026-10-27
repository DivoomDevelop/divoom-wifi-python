# divoom-wifi-python

[中文说明](README.zh-CN.md) · [Complete API coverage](docs/API_COVERAGE.md) · [Protocol notes](docs/PROTOCOL.md)

A synchronous Python 3.11+ SDK and CLI for **PIXOO64, TimeGate, AstroToo and TimeFrame**.
Discover devices, choose one, and obtain the matching product client. Devices are identified by
`Hardware`, so changing a device's display name does not change its API profile.

## Features

- Browse device names and select a list entry, device ID or IP, with automatic product matching from hardware IDs.
- Use 138 product operations covering device settings, clocks, animation/text, tools, cloud queries and AstroToo media transfers.
- Inspect the selected product's APIs and parameters in Python or the interactive CLI.
- Use explicit typed methods, original response fields, documented protocol limits and predictable errors.
- Install with one runtime dependency, `requests`; use the same API on Windows, macOS and Linux.

The GitHub repository is `divoom-wifi-python`; the Python distribution and CLI are `divoom-wifi`,
and the import is `divoom_wifi`. See the [verification report](docs/VERIFICATION.md) for tested firmware
and the distinction between automated protocol checks and live device checks.

## Install

Clone and install from this repository:

```console
git clone https://github.com/DivoomDevelop/divoom-wifi-python.git
cd divoom-wifi-python
python -m pip install .
divoom-wifi --version
```

Or install directly from GitHub (requires Git):

```console
python -m pip install "git+https://github.com/DivoomDevelop/divoom-wifi-python.git"
```

For a downloaded wheel: `python -m pip install divoom_wifi-0.1.2-py3-none-any.whl`.
The only runtime dependency is `requests`. Windows, macOS and Linux use the same Python API.
No documentation website access is needed at runtime.

## Discover, select, call

Hardware **90, 92 and 400** requires a LAN token. Set `DIVOOM_LOCAL_TOKEN` before running the example,
or pass `local_token=...` to `connect()`. Other supported hardware does not require a token.

```python
from divoom_wifi import connect, discover_devices

devices = [device for device in discover_devices() if device.supported]
if not devices:
    raise SystemExit("No supported devices found; try a direct IP connection.")
for number, device in enumerate(devices, 1):
    print(number, device.name, device.product, device.hardware,
          device.device_id, device.ip, device.mac)
choice = int(input("Device number: "))
if not 1 <= choice <= len(devices):
    raise SystemExit("Invalid selection")

with connect(devices[choice - 1]) as device:
    print(type(device).__name__)  # Pixoo64 / TimeGate / TimeFrame / AstroToo
    print([api.name for api in device.list_apis()])
    print(device.describe_api("set_brightness").as_dict())
    print(device.set_brightness(brightness=40))
```

Discovery is **cloud-assisted**, via `https://app.divoom-gz.com/Device/ReturnSameLANDevice`.
It requires Internet access and can include unreachable/stale addresses. Control requests need
a route to the device's LAN IP. Unknown products remain in the discovery list with `supported=False`.
Missing hardware triggers a read-only query; an unsuccessful query never implies a model.

Direct connections work without the discovery service:

```python
from divoom_wifi import connect

with connect("192.168.1.50", hardware=530) as astro:
    print(astro.get_hardware_version())
    print(astro.get_brightness())

with connect("192.168.1.60", hardware=400, local_token=123456) as gate:
    gate.select_clock(clock_id=100, lcd_index=0, lcd_independence=0)
```

The shown IPs, token and IDs are placeholders. Only hardware **90, 92 and 400** requires a token for LAN
commands. Use `local_token=...` or `DIVOOM_LOCAL_TOKEN`: the SDK sends `DeviceToken` for PIXOO64 90/92
and `LocalToken` for TimeGate 400. Tokens stay in memory. Other hardware and all cloud/discovery requests
neither require nor receive the configured token. Cloud APIs automatically use the discovered device ID/MAC.
For a direct-IP cloud call, construct a `DeviceInfo` with that metadata, or supply `device_id` /
`device_mac` to the corresponding method.

## Product profiles

| Product | Hardware | Default command transport |
| --- | --- | --- |
| PIXOO64 | 90, 92 | POST `http://IP:80/post` |
| PIXOO64 | 96 | POST `http://IP:9000/divoom_api` |
| TIMEGATE | 400 | POST `http://IP:80/post` |
| TIMEGATE | 402 | POST `http://IP:9000/divoom_api` |
| TIMEFRAME | 510, 511, 512 | GET with JSON body, `http://IP:9000/divoom_api` |
| ASTROTOO | 530 | POST `http://IP:9000/divoom_api` |

TIMEFRAME's GET body follows the referenced documentation; some HTTP proxies discard GET bodies.
The SDK sends directly to the LAN device and never changes the method after a timeout or error.
The TIMEFRAME font service needs a device ID despite page 379 omitting parameters; the SDK supplies
it from discovery. With direct IP, pass `get_fonts(device_id=...)`.
`base_url="http://host:port"` overrides the origin while retaining the product's command route.
Direct IP without `hardware` attempts a read-only identity query on port 9000; older devices may
require an explicit hardware ID.

## Command line

Run `divoom-wifi` with no arguments for the device/API selection menu. Hardware 90/92/400 LAN commands
request a token with hidden input when needed. Other hardware does not prompt for one.
Noninteractive calls that need a token use `DIVOOM_LOCAL_TOKEN`.

```console
divoom-wifi discover
divoom-wifi discover --json
divoom-wifi apis --product astrotoo
divoom-wifi describe upload_media --product astrotoo
divoom-wifi call get_brightness --device-id 300000001 --json
divoom-wifi call get_brightness --ip 192.168.1.50 --hardware 530 --json
```

Create `brightness.json` containing `{"brightness":40}`, then:

```console
divoom-wifi call set_brightness --ip 192.168.1.50 --hardware 530 --params '@brightness.json'
divoom-wifi call upload_clock_asset --ip 192.168.1.50 --hardware 530 --file element.png
```

`--params` accepts inline JSON, `@file` or `-` for standard input. Field names can be Python names
(`brightness`) or exact protocol names (`Brightness`), but not both in one request. Use `--file`,
`--preview`, `--duration` and `--destination` for transfers. JSON errors go to stderr, exit code 2;
successful commands exit 0; interrupted interactive sessions exit 130.

## AstroToo files and clocks

```python
from divoom_wifi import connect

with connect("192.168.1.50", hardware=530) as astro:
    print(astro.get_lan_capabilities())
    albums = astro.get_local_albums()  # Select an existing normal AlbumType:0 album.
    print(albums)
    # Replace with an existing local album ID returned above.
    result = astro.upload_media(file_path="unique-photo.jpg", clock_id=110001)
    # ReturnCode 0 acknowledges handling; insertion happens in the background.
    photo = astro.wait_for_photo(clock_id=110001, file_name="unique-photo.jpg", timeout=30)
    astro.download_media(path=photo["OriginalFileId"], destination="downloaded-photo.jpg")
    print(astro.head_media(path=photo["OriginalFileId"]))
```

Uploads stream from disk, include per-part and complete `Content-Length`, and send metadata before
files. First-block metadata behavior is tested at the HTTP client boundary; arbitrary TCP
fragmentation and video codecs still depend on the network and firmware. A video requires
`preview_path` (WebP), `video_duration` in seconds, and actual `photo_width` / `photo_height`.
Limits are read from device capabilities and capped at the reference's published limits.
Filenames must be unique within the intended upload workflow; reusing an existing filename can
make polling ambiguous. The SDK does not transcode images/videos. Downloads never overwrite a file.

Clock methods include `get_local_clock`, `patch_local_clock`, `get_local_fonts`, `upload_clock_asset`,
`create_local_clock`, `patch_clock_background` and `replace_clock_background`. Backgrounds must be
480×480 JPEG/WebP, below 512000 bytes. Staged `local://` assets are temporary and must be bound
promptly. Use locally available fonts and read back the clock/current display after writes.

## API and errors

Each documented operation has an explicit typed Python method and an offline registry entry.
`device.call("set_brightness", Brightness=40)` uses the same binding/validation as the named method.
Nested display, patch and command objects preserve their exact protocol spelling; inspect
`describe_api()` for the original nested parameter tables and source links.

JSON results preserve the original business fields. Failures raise `DivoomError` subclasses:
`NetworkError`, `HTTPError`, `ProtocolError`, `DeviceError`, `ValidationError`,
`TokenRequiredError`, `UnsupportedDeviceError` or `UnsupportedAPIError`.
Exceptions expose `api_name`, `response`, `status_code` and `code` where available.
HTTP 200 alone is not success: status fields must be present, integer-valued and zero.

Ordinary requests default to 15 seconds, uploads to 120 seconds; pass `timeout` /
`upload_timeout` to `connect()` to change them. Calls to the same device origin are serialized
across client instances in a process. Writes are never automatically retried; a timeout may
occur after the device applied a change. Polling only repeats read operations.

## Development and distribution

```console
python -m pip install -e '.[dev]'
python -m pytest
python tools/build_reference.py --check
python -m build
python -m twine check dist/*
```

The reference snapshot contains 141 product pages plus 3 common pages. It maps to 138 product
operations after merging the gallery duplicate and adding HEAD for the documented download route.
`docs/reference/coverage.json` accounts for every page. `tools/sync_reference.py` downloads a fresh
public snapshot; review changes before running `tools/build_reference.py`. Generation refuses
to replace externally edited generated outputs. Neither tool is used at runtime.

See [verification results](docs/VERIFICATION.md) for the tested environments and physical-device
coverage. API exposure does not certify every firmware, parameter combination or video codec.
The package excludes PIXOO16, Bluetooth protocols, undocumented firmware commands and the visual
watchface editor. Installation instructions above use this GitHub repository or a locally built wheel.

## Support and contributing

See [direct LAN verification](docs/LAN_CHECKS.md) for the four-product retest and the hardware 400/402
token difference. To run read-only checks against discovered devices locally:

```console
python tools/check_lan.py --output .venv/lan-checks/report.json
```

Only discovery uses the cloud; device checks connect directly to LAN endpoints. Replies without
expected business fields are reported as `ack_only`. Some read-only probes are outside a product's
published Python method catalog and are labeled `protocol_probe`. Reports contain local IPs and
should be kept local. Existing report files are never overwritten.

Report bugs or propose features in [GitHub Issues](https://github.com/DivoomDevelop/divoom-wifi-python/issues).
Include the SDK version, product, hardware/firmware version, the API involved and a minimal example.
For API additions, update the reviewed registry, explicit methods, documentation and protocol tests together.
Pull requests run package checks on Windows, macOS and Linux with Python 3.11 and 3.13.

[MIT License](LICENSE). Copyright (c) 2026 Divoom Developers.
