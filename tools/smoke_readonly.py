"""Opt-in live smoke test using a fixed allowlist of read-only operations.

Reports omit LAN addresses, MACs, device IDs, names and business data. No write
command, upload, snapshot generation or deletion is issued.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from divoom_wifi import DivoomError, connect, discover_devices
from divoom_wifi.discovery import probe_hardware

READS = {"pixoo64": ("get_settings", "get_device_time"),
         "timegate": ("get_fonts", "get_channel_info"),
         "timeframe": ("get_fonts", "get_dial_list"),
         "astrotoo": ("get_hardware_version", "get_lan_capabilities", "get_brightness", "get_screen")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=3)
    parser.add_argument("--per-hardware", type=int, default=2)
    parser.add_argument("--product", choices=tuple(READS), help="Limit reads to one product")
    parser.add_argument("--output", type=Path, help="New JSON report file; existing files are refused")
    args = parser.parse_args()
    if args.per_hardware < 1:
        parser.error("--per-hardware must be positive")
    # UTC+08 avoids depending on the Windows tzdata database.
    report = {"date": datetime.now(timezone(timedelta(hours=8))).isoformat(), "scope": "read-only",
              "discovery_counts": {}, "devices": []}
    devices = discover_devices(timeout=15, probe_missing=False)
    report["discovery_counts"] = dict(Counter(str(d.hardware) for d in devices))
    groups = defaultdict(list)
    for device in devices:
        if (device.supported and (not args.product or device.product == args.product)
                and not any(s in device.name.lower() for s in ("模拟", "simulat"))):
            groups[device.hardware].append(device)
    for hardware, group in groups.items():
        for number, device in enumerate(group[:args.per_hardware], 1):
            row = {"hardware": hardware, "product": device.product, "sample": number, "checks": []}
            print(f"Checking {device.product} hardware={hardware} sample={number}", file=sys.stderr)
            with connect(device, timeout=args.timeout) as client:
                if device.product == "timeframe":
                    try:
                        identity = probe_hardware(device.ip, timeout=args.timeout)
                        row["checks"].append({"api": "probe_hardware", "result": "pass",
                                              "reported_hardware": identity.get("Hardware"),
                                              "firmware": identity.get("FirmwareVersion", identity.get("Software"))})
                    except DivoomError as exc:
                        row["checks"].append({"api": "probe_hardware", "result": "unavailable", "error": type(exc).__name__})
                operations = list(READS[device.product])
                if device.product == "timegate" and os.environ.get("DIVOOM_LOCAL_TOKEN"):
                    operations.append("get_settings")
                for name in operations:
                    try:
                        params = {"start_num": 1, "end_num": 1} if name == "get_dial_list" else {}
                        result = client.call(name, **params)
                        check = {"api": name, "result": "pass", "response_fields": sorted(result)}
                        if name == "get_hardware_version":
                            check["reported_hardware"] = result.get("Hardware")
                            check["firmware"] = result.get("FirmwareVersion", result.get("Software"))
                        row["checks"].append(check)
                    except DivoomError as exc:
                        row["checks"].append({"api": name, "result": "unavailable", "error": type(exc).__name__,
                                              "code": exc.code, "http_status": exc.status_code})
            report["devices"].append(row)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError(args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(text)
    print(text)


if __name__ == "__main__":
    main()
