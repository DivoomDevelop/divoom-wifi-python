"""Opt-in direct LAN checks for discovered Divoom devices; never sends a write.

Only discovery uses the cloud. Some read-only protocol probes (identified as
protocol_probe) are not part of that product's published SDK method catalog.
Business-field checks distinguish meaningful reads from acknowledgement-only replies.
Reports contain local addresses: keep them local unless intentionally redacted.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from divoom_wifi import DivoomError, TokenRequiredError, connect, discover_devices

# (SDK method or raw command, expected business fields, invocation kind).
READS = {
    "pixoo64": [("get_settings", ("Brightness",), "sdk"),
                ("get_device_time", ("LocalTime", "UTCTime"), "sdk")],
    "timegate": [("get_settings", ("Brightness",), "sdk"),
                 ("get_device_time", ("LocalTime", "UTCTime"), "sdk"),
                 ("Sys/GetBrightness", ("Brightness",), "protocol_probe"),
                 ("Channel/GetOnOffScreen", ("OnOff",), "protocol_probe"),
                 ("Channel/GetClockInfo", ("ClockId",), "protocol_probe")],
    "timeframe": [("Device/GetHardwareVersion", ("Hardware",), "protocol_probe"),
                  ("Sys/GetBrightness", ("Brightness",), "protocol_probe"),
                  ("Channel/GetOnOffScreen", ("OnOff",), "protocol_probe"),
                  ("Channel/GetClockInfo", ("ClockId",), "protocol_probe")],
    "astrotoo": [("get_hardware_version", ("Hardware",), "sdk"),
                 ("get_lan_capabilities", ("JsonMaxBytes",), "sdk"),
                 ("get_brightness", ("Brightness",), "sdk"),
                 ("get_screen", ("OnOff",), "sdk"),
                 ("get_current_clock", ("ClockId",), "sdk")],
}


def check_device(device, timeout: float) -> dict:
    row = {"name": device.name, "ip": device.ip, "hardware": device.hardware, "product": device.product,
           "checks": [], "business_reads": 0}
    with connect(device, timeout=timeout) as client:
        row["endpoint"] = client.base_url + client.profile.path
        row["method"] = client.profile.method
        for api, fields, kind in READS[device.product]:
            check = {"api": api, "kind": kind}
            started = time.monotonic()
            try:
                if kind == "sdk":
                    result = client.call(api)
                else:
                    payload = {"Command": api}
                    if client.profile.local_token_required:
                        if client._token is None:
                            raise TokenRequiredError(f"Hardware {device.hardware} requires a LAN token", api_name=api)
                        client.set_local_token(client._token)
                        payload[client.profile.token_field] = client._token
                    result = client._transport.request_json(
                        client.profile.method, row["endpoint"], payload, api_name=api,
                        status_fields=("error_code", "ReturnCode"))
                check["elapsed_ms"] = round((time.monotonic() - started) * 1000)
                check["response_fields"] = sorted(result)
                if result.get("DeviceId", device.device_id) != device.device_id:
                    check.update(result="identity_mismatch")
                    row["checks"].append(check)
                    break
                if "Hardware" in result and result["Hardware"] != device.hardware:
                    check.update(result="identity_mismatch")
                    row["checks"].append(check)
                    break
                check["result"] = "pass" if any(field in result for field in fields) else "ack_only"
                check["business"] = {field: result[field] for field in fields if field in result}
                if "FirmwareVersion" in result or "Software" in result:
                    row["firmware"] = result.get("FirmwareVersion", result.get("Software"))
                if check["result"] == "pass":
                    row["business_reads"] += 1
            except DivoomError as exc:
                check.update(result="failed", error=type(exc).__name__, message=str(exc),
                             elapsed_ms=round((time.monotonic() - started) * 1000),
                             http_status=exc.status_code, code=exc.code)
                if isinstance(exc.response, dict) and isinstance(exc.response.get("error_code"), str):
                    check["device_error"] = exc.response["error_code"]
                row["checks"].append(check)
                if type(exc).__name__ in ("NetworkError", "HTTPError", "TokenRequiredError"):
                    break
                continue
            row["checks"].append(check)
    row["result"] = ("identity_mismatch" if any(c["result"] == "identity_mismatch" for c in row["checks"])
                     else "pass" if row["business_reads"] else "unverified")
    print(f'{device.product} HW{device.hardware} {device.ip}: {row["result"]}, '
          f'{row["business_reads"]} meaningful reads', file=sys.stderr, flush=True)
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=3)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True, help="New local JSON report; never overwrites")
    args = parser.parse_args()
    if args.workers < 1 or args.timeout <= 0:
        parser.error("workers and timeout must be positive")
    if args.output.exists():
        raise FileExistsError(args.output)
    devices = discover_devices(timeout=15, probe_missing=False)
    targets = [d for d in devices if d.supported and not any(s in d.name.lower() for s in ("模拟", "simulat"))]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda d: check_device(d, args.timeout), targets))
    report = {"date": datetime.now(timezone(timedelta(hours=8))).isoformat(), "scope": "direct-LAN-read-only",
              "discovery_counts": dict(Counter(str(d.hardware) for d in devices)),
              "local_token_supplied": bool(os.environ.get("DIVOOM_LOCAL_TOKEN")), "devices": results,
              "summary": {product: {"tested": sum(r["product"] == product for r in results),
                                    "reachable_with_business_data": sum(r["product"] == product and r["result"] == "pass"
                                                                        for r in results)}
                          for product in READS}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"Private LAN report: {args.output}")


if __name__ == "__main__":
    main()
