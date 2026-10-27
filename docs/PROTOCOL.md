# Protocol and compatibility notes / 协议与兼容性

Reference: public ShowDoc project 5, retrieved 2026-10-27. Runtime metadata is packaged in
`divoom_wifi/data/apis.json`; full development snapshots and per-page hashes are under `docs/reference`.
The SDK implements only the four requested product directories and their common protocol references.

## Identity and transport

The live discovery service includes `Hardware`, although page 25's example omits it. Hardware selects
the product and legacy/new endpoint. The product registry maps 90/92/96 to PIXOO64, 400/402 to TIMEGATE,
510/511/512 to TIMEFRAME, and 530 to ASTROTOO. The TIMEFRAME hardware mapping is also documented in
the official [Divoom LAN project](https://github.com/DivoomDevelop/mcp-divoom-lan).

Requests carry JSON bodies, including TIMEFRAME GET requests. Cloud hosts and methods retain each
page's documented URL; notably TIMEFRAME's dial list is a cloud GET body. LAN environment proxies
are disabled to keep local tokens on the direct connection. Cloud requests can use normal proxy
settings. Redirects are rejected and requests are not retried automatically.

Source differences are intentionally recorded:

- Legacy reboot tables use lowercase `command`; generated requests use canonical `Command` from
  the common command-format page. Reboot responses lack a documented schema; a missing success
  field or connection loss raises an error, even if the device may have rebooted.
- PIXOO64 page 54 labels `FileName` as Number, while its example and URL semantics require a string.
- Pages 137 and 355 describe the same gallery command and are merged; `GalleryShowTimeFlag` is optional.
- `SingleGalleyTime`, `BackgroudGif`, `BackgroudImageAddr` and `BackgroudImageLocalFlag` retain their
  protocol spelling. Nested `ItemList`/`DispList`/`LightList` fields remain nested.
- TimeGate's independence ID is conditional for channel selection; old text alignment is optional.
- TIMEFRAME page 379 omits request parameters. The live font service rejects `{}` with ReturnCode 12
  (Request data is null); sending DeviceId succeeds. The SDK injects the selected device ID and exposes
  an explicit device_id argument for direct-IP callers. This correction was verified on 2026-10-27.
- The TimeGate RGB example omits `KeyOnOff`; RGB fields are accepted as partial updates. At least
  one setting is required. Actual firmware behavior still needs per-device verification.

Python method names are conveniences. `describe_api()` contains the exact wire fields, original
parameter descriptions (including nested tables), source links and compatibility notes. Values in
nested dictionaries are not renamed. The general `call()` only dispatches registered product APIs.

## Results and errors

Legacy PIXOO64/TIMEGATE LAN results accept `error_code` or `ReturnCode`; if both are present both
must be zero. Cloud, TIMEFRAME and ASTROTOO JSON results require `ReturnCode`. Codes must be integers,
not booleans or strings. Responses are returned unchanged. HTTP failures, JSON failures, missing
status, and nonzero device status have distinct exception classes.

A successful acknowledgement may precede visible work or background processing. The library never
reports a write as having visibly completed solely because HTTP or JSON status indicates success.
Use readback appropriate to the operation. A write timeout has an uncertain outcome; inspect state
before deciding whether to repeat it.

## AstroToo capabilities, multipart and media

The client lazily reads `Device/GetLanCapabilities` before the first ordinary AstroToo operation,
unless an identity response already supplied the limits. Explicit capability calls refresh the cache.
JSON limits use UTF-8 bytes. Published limits cap any larger device-advertised values:

| Item | Published limit |
| --- | --- |
| JSON request/response | 65536 bytes |
| Entire photo upload body | 536870912 bytes, including JSON, boundaries, media and preview |
| Declared video duration | 1800 seconds |
| Clock image file | strictly less than 512000 bytes |
| Clock background | 480×480 JPEG/WebP |
| Staged element image | JPEG/PNG/WebP, at most 1024×1024 |

Multipart uploads have a JSON part first, followed by one clock file, or media and an optional
video preview. Every part has `Content-Length`; the complete body also has `Content-Length`.
The first yielded body block contains the complete JSON headers/content and following file boundary
and headers. The implementation streams file bytes in 64 KiB blocks and never assembles a video
in memory. The HTTP client's send boundary cannot control arbitrary TCP fragmentation; the legacy
firmware parser's fragmentation limitation still applies.

Media metadata uses the local album's `ClockId` (>=100000), not a watchface ID. Standalone metadata
defaults parent IDs, user ID and crop offsets to zero, uses a one-item batch, current millisecond
timestamps and a fresh batch marker. For an intentional multi-item batch, pass the same `photo_flag`
and correct `photo_index`/`photo_total_cnt` to every item. Names match multipart filenames and are
below 128 UTF-8 bytes; titles are below 512 bytes. Images derive their dimensions from headers.
Videos require declared dimensions/duration and a WebP preview; container and codec compatibility
are the caller/device's responsibility. The SDK performs no transcoding or full image decoding.

`upload_media()` sends only the multipart upload, with no second LocalAddToAlbum command.
`wait_for_photo()` polls paginated PhotoList results by ID or filename (using returned
OriginalFileId when FileName is absent). Use unique filenames to avoid matching existing media.
Polling timeout does not delete uploaded data or re-upload it. Request timeout is a requests
connect/read inactivity timeout, not a guarantee against arbitrarily slow trickle responses.

`upload_clock_asset()` returns a temporary `local://` reference that must be bound to a supported
clock slot promptly. It does not add to the photo library. Clock create injects the documented
request `ReturnCode:0` and `DialAssets:"image"`; clock background patch injects `DialAssets:"image"`.
An explicit ClockId is required for patch/replace unless UseCurrentDisplayClock is 1.
The firmware allocates new clock IDs. No managed-slot or cloud restore behavior is added.

GET/HEAD media access is limited to the selected device's `/userdata/` paths. Downloads stage the
network stream on disk, then exclusively create the destination. Existing files are preserved.
Disk failure during final copying may leave an incomplete new destination; the caller can inspect it.

## Verification boundary / 验证边界

自动化测试验证宿主端协议、完整请求字节、参数和错误处理；图像头测试不代表固件能解码该媒体。
现场验证仅执行只读查询，不执行重启、显示切换、亮度修改、上传或删除。
硬件版本、网络可达性和凭据不足导致的未验证项在 `VERIFICATION.md` 单独记录。
