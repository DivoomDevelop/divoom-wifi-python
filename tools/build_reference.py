"""Build reviewed API metadata, explicit Python methods and a coverage index.

The table/parser corrections below are deliberately kept in source control.
Run --check in CI; generation refuses to overwrite an externally edited output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    26: "reboot", 27: "get_dial_types", 28: "get_dial_list", 29: "select_clock",
    30: "get_current_clock", 31: "select_channel", 32: "select_custom_page",
    33: "select_visualizer", 34: "select_cloud_channel", 35: "get_current_channel",
    36: "set_brightness", 37: "get_settings", 38: "set_weather_location", 39: "set_timezone",
    40: "set_utc", 41: "set_screen", 42: "get_device_time", 43: "set_temperature_mode",
    44: "set_rotation", 45: "set_mirror_mode", 46: "set_hour_mode", 47: "set_highlight_mode",
    48: "set_white_balance", 49: "get_weather", 137: "set_gallery_time", 355: "set_gallery_time",
    50: "set_countdown", 51: "set_stopwatch", 52: "set_scoreboard", 53: "set_noise_tool",
    54: "play_gif", 55: "get_animation_id", 56: "reset_animation_id", 57: "send_animation",
    58: "send_text", 59: "clear_text", 60: "get_fonts", 61: "send_display_list", 62: "play_buzzer",
    63: "play_divoom_gif", 64: "get_uploaded_images", 65: "get_liked_images", 356: "save_gif",
    357: "play_gif_frame", 66: "send_command_list", 67: "use_command_url",
    140: "reboot", 102: "set_brightness", 103: "get_settings", 104: "set_weather_location",
    105: "set_timezone", 106: "set_utc", 107: "set_screen", 108: "get_device_time",
    109: "set_temperature_mode", 110: "set_mirror_mode", 111: "set_hour_mode", 112: "get_weather",
    138: "set_gallery_time", 353: "set_rgb", 113: "get_dial_types", 114: "get_dial_list",
    115: "get_whole_dial_list", 116: "select_whole_clock", 117: "select_channel_type",
    118: "get_channel_info", 119: "select_clock", 120: "select_visualizer", 121: "set_countdown",
    122: "set_stopwatch", 123: "set_scoreboard", 124: "set_noise_tool", 125: "play_buzzer",
    126: "get_liked_images", 127: "get_uploaded_images", 128: "play_divoom_gif", 129: "play_gif",
    130: "play_gif_on_all_screens", 133: "send_animation", 134: "send_text", 141: "clear_text",
    131: "get_fonts", 132: "send_display_list", 135: "send_command_list", 136: "use_command_url",
    359: "reboot", 370: "set_countdown", 371: "set_stopwatch", 372: "set_scoreboard",
    373: "set_noise_tool", 362: "set_brightness", 363: "set_weather_location", 367: "set_screen",
    368: "set_mirror_mode", 369: "set_hour_mode", 360: "get_dial_list", 361: "select_clock",
    374: "enter_custom_mode", 375: "exit_custom_mode", 377: "update_display_items", 379: "get_fonts",
    382: "get_hardware_version", 383: "get_lan_capabilities", 384: "get_device_id",
    386: "get_brightness", 387: "get_screen", 388: "get_current_clock", 389: "get_storage_status",
    390: "get_weather", 391: "get_screen_snapshot", 392: "set_brightness", 393: "set_screen",
    398: "set_hour_mode", 399: "set_temperature_mode", 401: "get_local_albums", 402: "get_local_photos",
    406: "set_album_cover", 407: "add_photos_to_album", 408: "remove_photos_from_album",
    409: "delete_photos", 412: "set_album_config", 413: "upload_media", 414: "download_media",
    415: "get_local_clock", 416: "patch_local_clock", 417: "get_local_fonts",
    418: "upload_clock_asset", 419: "create_local_clock", 420: "patch_clock_background",
    421: "replace_clock_background", 422: "get_countdown", 423: "set_countdown",
    424: "get_stopwatch", 425: "set_stopwatch", 426: "get_scoreboard", 427: "set_scoreboard",
    428: "get_noise_tool", 429: "set_noise_tool",
}
REFERENCE = {358, 381, 430, 24, 25, 145}
UPLOADS = {413: "/upload", 418: "/upload_local_asset", 419: "/create_local_clock",
           420: "/patch_local_clock", 421: "/replace_clock_dial_bg"}
CLASSES = {"pixoo64": "Pixoo64", "timegate": "TimeGate", "timeframe": "TimeFrame", "astrotoo": "AstroToo"}


def snake(value: str) -> str:
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value).lower()


def section(text: str, heading: str) -> str:
    match = re.search(r"(?im)^#####\s*(?:" + heading + r")\s*\n", text)
    return re.split(r"(?m)^#####\s+", text[match.end():])[0].strip() if match else ""


def parameter(wire: str, kind: str, description: str, *, required: bool = True,
              auto: str | None = None, default=None) -> dict:
    return {"name": snake(wire), "wire": wire, "type": kind, "required": required,
            "description": description, "auto": auto, "default": default}


def parse(page: dict) -> dict:
    pid, product, text = page["page_id"], page["product"], page["content"]
    table = section(text, "para|parameters|request parameters")
    command = None
    params = []
    token = False
    for line in table.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not re.match(r"^[A-Za-z]", cells[0]) or cells[0].lower() in ("name", "returned path"):
            continue
        wire, datatype, description = cells[:3]
        if wire.lower() == "command":
            command = re.search(r"([A-Za-z]+/[A-Za-z0-9_]+)", description).group(1)
            continue
        if wire == "LocalToken":
            token = True
            continue
        if pid in (61, 132) and wire == "TextId":
            break  # Following unindented rows document ItemList elements, not root fields.
        if pid == 353 and wire == "SelectEffect":
            continue  # This is a LightList element.
        for field in [x.strip() for x in wire.split(",")]:
            kind = ("list" if "array" in datatype.lower() else "dict" if "object" in datatype.lower()
                    else "str" if datatype.lower() == "string" else "bool" if datatype.lower() == "boolean"
                    else "float" if field in ("SendTime", "TakingTime") else "int")
            required = "optional" not in description.lower() and "required unless" not in description.lower()
            auto = {"DeviceId": "device_id", "DeviceMac": "mac"}.get(field)
            default = None
            if field == "Page":
                default = 1
            if field == "DeviceType":
                default = "LCD" if product == "timegate" else "Frame"
            if field in ("ParentItemId", "ParentClockId") and product == "astrotoo":
                default = 0
            if pid == 353:
                required = False  # Example omits KeyOnOff; RGB updates are partial.
            if pid == 117 and field == "LcdIndependence":
                required = False  # Only required for ChannelType=1.
            if pid in (58, 134) and field == "align":
                required = False  # Old firmware predates the documented alignment feature.
            if pid == 54 and field == "FileName":
                kind = "str"  # Table says Number, but example and semantics are a URL string.
            params.append(parameter(field, kind, description, required=required, auto=auto, default=default))

    request_url = section(text, "Request URL")
    urls = re.findall(r"https?://[^\s`\"“”]+", request_url)
    cloud = next((url for url in urls if "/IP" not in url and "//IP:" not in url), None)
    method_section = section(text, "Request method|request")
    method = "GET" if re.search(r"(?i)\bGET\b", method_section) else "POST"
    route = "cloud" if cloud else "lan"
    constants = {}
    notes = section(text, "command description")
    if pid == 379:
        params.append(parameter("DeviceId", "int", "Device ID. Omitted in page 379; live service requires a nonempty request. "
                                "Automatically supplied from discovery (verified 2026-10-27).", auto="device_id"))
        notes += "\nLive verification on 2026-10-27: empty JSON returns ReturnCode=12 (Request data is null); " \
                 "a request containing DeviceId succeeds. DeviceId is injected from the selected device."
    if table:
        notes += "\n\nRequest parameter table (including nested element fields):\n" + table
    extra_notes = section(text, "Notes")
    if extra_notes:
        notes += "\n\n" + extra_notes
    if pid in (26, 140, 359):
        notes += "\nThe reboot table spells command in lowercase; use canonical Command from common page 24."
    if pid in UPLOADS:
        route = "upload"
        params.insert(0, parameter("file_path", "path", "Local file path; streamed as the binary file part."))
    if pid in (419, 420):
        constants["DialAssets"] = "image"
        params = [p for p in params if p["wire"] != "DialAssets"]
    if pid == 419:
        constants["ReturnCode"] = 0
        params = [p for p in params if p["wire"] != "ReturnCode"]
    if pid == 413:
        # File names and image dimensions are derived; callers can explicitly provide matching metadata.
        for p in params:
            if p["wire"] in ("FileName", "PreviewFileName", "PhotoWidth", "PhotoHeight"):
                p["required"] = False
            if p["wire"] in ("ParentItemId", "ParentClockId", "UserId", "PhotoX", "PhotoY", "PhotoIndex"):
                p["default"] = 0
            if p["wire"] == "PhotoTotalCnt":
                p["default"] = 1
            if p["wire"] == "PhotoTitle":
                p["default"] = ""
            if p["wire"] in ("PhotoFlag", "SendTime", "TakingTime"):
                p["required"] = False
        params += [parameter("preview_path", "path", "Required WebP preview file for a video.", required=False),
                   parameter("video_duration", "float", "Required declared video duration in seconds.", required=False)]
    if pid == 414:
        route, cloud, command = "download", None, None
        params = [parameter("path", "str", "Exact device-returned /userdata/ path."),
                  parameter("destination", "path", "New local file path; existing files are never overwritten.")]
    if pid in (416, 420, 421):
        notes += "\nClockId is required unless UseCurrentDisplayClock=1."
    if pid == 54:
        notes += "\nFileName is a URL string; the Number datatype in the table is a documentation typo."
    return {"name": NAMES[pid], "product": product, "title": page["title"], "route": route,
            "method": method, "command": command, "url": cloud, "path": UPLOADS.get(pid),
            "status_fields": (["error_code", "ReturnCode"] if route == "lan" and product in ("pixoo64", "timegate")
                              else ["ReturnCode"]), "parameters": params, "sources": [pid],
            "source_urls": [page["url"]], "notes": notes.strip(), "token_required": token,
            "constants": constants}


def methods(apis: list[dict]) -> str:
    lines = ['"""Explicit product APIs generated from reviewed metadata; see tools/build_reference.py."""',
             "from __future__ import annotations", "", "from pathlib import Path", "from typing import Any",
             "", "from .client import BaseDevice", ""]
    for product, class_name in CLASSES.items():
        lines += ["", f"class {class_name}(BaseDevice):", f'    """{class_name} operations from the official WiFi reference."""',
                  f'    product_name = "{product}"']
        for spec in [s for s in apis if s["product"] == product]:
            params = spec["parameters"]
            signatures = []
            for p in params:
                annotation = {"list": "list[Any]", "dict": "dict[str, Any]", "path": "str | Path",
                              "any": "Any"}.get(p["type"], p["type"])
                optional = not p["required"] or p["auto"] or p["default"] is not None
                if optional:
                    annotation += " | None"
                signatures.append(f'{p["name"]}: {annotation}' + (" = None" if optional else ""))
            args = ", *, " + ", ".join(signatures) if signatures else ""
            return_type = "Path" if spec["route"] == "download" else "dict[str, Any]"
            lines += ["", f'    def {spec["name"]}(self{args}) -> {return_type}:',
                      f'        """{spec["title"]}.']
            for p in params:
                desc = p["description"].replace('"""', "'''").replace("\\", "\\\\")
                lines.append(f'\n        :param {p["name"]}: {desc} (wire: {p["wire"]})')
            lines += ["", "        Sources: " + ", ".join(spec["source_urls"]), '        """']
            kwargs = ", ".join(f'{p["name"]}={p["name"]}' for p in params)
            comma = ", " if kwargs else ""
            lines.append(f'        return self.call("{spec["name"]}"{comma}{kwargs})')
        if product == "astrotoo":
            lines += ["", "    def head_media(self, *, path: str) -> dict[str, str]:",
                      '        """Read headers of a device-returned /userdata/ path without downloading it."""',
                      '        return self.call("head_media", path=path)']
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source = json.loads((ROOT / "docs/reference/pages.json").read_text(encoding="utf-8"))
    apis = []
    coverage = []
    for page in source["pages"]:
        pid = page["page_id"]
        if pid in REFERENCE:
            coverage.append({**{k: page[k] for k in ("page_id", "product", "title", "url", "sha256")},
                             "kind": "reference", "api": "discover_devices" if pid == 25 else None})
            continue
        if pid not in NAMES:
            raise RuntimeError(f"Unreviewed page: {pid} {page['title']}")
        spec = parse(page)
        previous = next((s for s in apis if s["product"] == spec["product"] and s["name"] == spec["name"]), None)
        if previous:
            assert pid == 355  # Only this documented duplicate is intentionally merged.
            for param in spec["parameters"]:
                if param["wire"] not in [p["wire"] for p in previous["parameters"]]:
                    previous["parameters"].append({**param, "required": False})
            previous["sources"] += spec["sources"]
            previous["source_urls"] += spec["source_urls"]
            previous["notes"] += "\n\n" + spec["notes"]
        else:
            apis.append(spec)
        coverage.append({**{k: page[k] for k in ("page_id", "product", "title", "url", "sha256")},
                         "kind": "api", "api": spec["name"]})
    download = next(s for s in apis if s["name"] == "download_media")
    apis.append({**download, "name": "head_media", "title": "Read local media headers", "route": "head",
                 "method": "HEAD", "parameters": download["parameters"][:1]})
    data = {"schema_version": 1, "reference_date": source["reference_date"], "apis": apis}
    coverage_data = {"reference_date": source["reference_date"], "pages": coverage}
    outputs = {
        "src/divoom_wifi/data/apis.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        "src/divoom_wifi/products.py": methods([s for s in apis if s["name"] != "head_media"]),
        "docs/reference/coverage.json": json.dumps(coverage_data, ensure_ascii=False, indent=2) + "\n",
    }
    index = ["# API coverage", "", "Generated from the public reference snapshot. See `coverage.json` for every page.", "",
             "| Product | Python method | Transport | Source pages |", "| --- | --- | --- | --- |"]
    for s in apis:
        sources = ", ".join(f"[{pid}]({url})" for pid, url in zip(s["sources"], s["source_urls"]))
        index.append(f'| {s["product"]} | `{s["name"]}` | {s["method"]} {s["route"]} | {sources} |')
    outputs["docs/API_COVERAGE.md"] = "\n".join(index) + "\n"
    hash_path = ROOT / "docs/reference/generated_hashes.json"
    old_hash_bytes = hash_path.read_bytes() if hash_path.exists() else None
    known = json.loads(old_hash_bytes) if old_hash_bytes else {}
    new_hashes = {}
    for relative, text in outputs.items():
        path = ROOT / relative
        payload = text.encode("utf-8")
        current = path.read_bytes() if path.exists() else None  # Immediate fresh read before each write.
        if args.check:
            if current != payload:
                raise SystemExit(f"Out of date: {relative}")
        elif current != payload:
            if current is not None and hashlib.sha256(current).hexdigest() != known.get(relative):
                raise SystemExit(f"Refusing to overwrite external edits: {relative}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        new_hashes[relative] = hashlib.sha256(payload).hexdigest()
    if not args.check:
        current_hash_bytes = hash_path.read_bytes() if hash_path.exists() else None
        if current_hash_bytes != old_hash_bytes:
            raise SystemExit("Concurrent change to generated_hashes.json")
        hash_path.write_text(json.dumps(new_hashes, indent=2) + "\n", encoding="utf-8")
    print(f"{len(source['pages'])} pages accounted for; {dict(Counter(s['product'] for s in apis))}")


if __name__ == "__main__":
    main()
