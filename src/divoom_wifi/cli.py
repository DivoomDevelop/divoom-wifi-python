"""Discover -> choose device -> inspect matching APIs -> invoke."""
from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .client import BaseDevice, connect
from .discovery import DISCOVERY_URL, discover_devices
from .errors import DivoomError, TokenRequiredError, UnsupportedDeviceError, ValidationError
from .models import PROFILES, DeviceInfo
from .registry import APISpec, describe_api, list_apis


def _common(parser: argparse.ArgumentParser, *, child: bool = False) -> None:
    def add(*flags: str, **kwargs: Any) -> None:
        if child:
            kwargs["default"] = argparse.SUPPRESS
        parser.add_argument(*flags, **kwargs)
    add("--json", action="store_true", help="Output machine-readable JSON")
    add("--ip", help="Direct device IP/host (bypasses cloud discovery)")
    add("--hardware", type=int, help="Hardware ID, e.g. 90, 400, 510 or 530")
    add("--device-id", type=int, help="Select a discovered device ID; with --ip supplies cloud metadata")
    add("--mac", help="Device MAC for cloud APIs when connecting by IP")
    add("--base-url", help="Override local HTTP origin, e.g. http://127.0.0.1:9000")
    add("--product", choices=("pixoo64", "timegate", "timeframe", "astrotoo"), help="Offline API catalog")
    add("--timeout", type=float, default=15, help="Ordinary request timeout in seconds (default 15)")
    add("--upload-timeout", type=float, default=120, help="Upload timeout in seconds (default 120)")
    add("--discovery-url", default=DISCOVERY_URL, help=argparse.SUPPRESS)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="divoom-wifi", description=__doc__)
    root.add_argument("--version", action="version", version=__version__)
    _common(root)
    subs = root.add_subparsers(dest="action")
    for name, help_text in (("discover", "Find devices using the cloud-assisted LAN list"),
                            ("apis", "List the selected product's APIs"),
                            ("describe", "Show parameters, protocol and documentation"),
                            ("call", "Invoke an API on the selected device")):
        sub = subs.add_parser(name, help=help_text)
        _common(sub, child=True)
        if name in ("describe", "call"):
            sub.add_argument("api", help="Python method name shown by apis")
        if name == "call":
            sub.add_argument("--params", default="{}", help="JSON object, @UTF8-file, or - for stdin")
            sub.add_argument("--file", help="Upload file path")
            sub.add_argument("--preview", help="WebP preview file for video uploads")
            sub.add_argument("--duration", type=float, help="Declared video duration in seconds")
            sub.add_argument("--destination", help="New local output path for download_media")
    return root


def _emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def _device_table(devices: list[DeviceInfo]) -> None:
    print("#  Product     Hardware  Device ID    IP                 MAC           Name")
    for index, device in enumerate(devices, 1):
        print(f"{index:<2} {device.product or 'unsupported':<11} {device.hardware!s:<9} "
              f"{device.device_id!s:<12} {device.ip:<18} {device.mac or '-':<13} {device.name}")


def _discover(args: argparse.Namespace) -> list[DeviceInfo]:
    return discover_devices(timeout=args.timeout, discovery_url=args.discovery_url)


def _choose_device(devices: list[DeviceInfo]) -> DeviceInfo:
    if not devices:
        raise ValidationError("No devices found. Connect to the device LAN or use --ip and --hardware.")
    _device_table(devices)
    if not any(d.supported for d in devices):
        raise UnsupportedDeviceError("No supported hardware found")
    while True:
        answer = input("Select device number (q to quit): ").strip()
        if answer.lower() == "q":
            raise KeyboardInterrupt
        if answer.isascii() and answer.isdigit() and 1 <= int(answer) <= len(devices):
            device = devices[int(answer) - 1]
            if device.supported:
                return device
            print("Hardware is unknown/unsupported. Specify a supported --hardware explicitly if appropriate.")
        else:
            print("Enter a listed device number.")


def _connect(args: argparse.Namespace, *, interactive: bool = False) -> BaseDevice:
    if args.ip:
        selected = DeviceInfo(name=args.ip, ip=args.ip, hardware=args.hardware,
                              device_id=args.device_id, mac=args.mac)
    else:
        devices = _discover(args)
        if args.device_id is not None:
            matches = [d for d in devices if d.device_id == args.device_id]
            if len(matches) != 1:
                raise ValidationError("Device ID is absent or ambiguous; use an explicit --ip and --hardware")
            selected = matches[0]
        elif interactive or sys.stdin.isatty():
            selected = _choose_device(devices)
        else:
            supported = [d for d in devices if d.supported]
            if len(supported) != 1:
                raise ValidationError("Specify --device-id or --ip for noninteractive selection")
            selected = supported[0]
    client = connect(selected, hardware=args.hardware, base_url=args.base_url,
                     timeout=args.timeout, upload_timeout=args.upload_timeout)
    if args.product and client.product != args.product:
        client.close()
        raise UnsupportedDeviceError("--product does not match the selected device hardware")
    return client


def _api_table(apis: list[APISpec]) -> None:
    for index, spec in enumerate(apis, 1):
        print(f"{index:>2}. {spec.name:<28} {spec.method:<4} {spec.route:<8} {spec.title}")


def _describe(spec: APISpec, as_json: bool = False) -> None:
    if as_json:
        _emit(spec.as_dict())
        return
    print(f"{spec.product}.{spec.name}: {spec.title}")
    print(f"Transport: {spec.method} {spec.url or spec.path or 'product LAN endpoint'}")
    if spec.command:
        print(f"Command: {spec.command}")
    if spec.route == "lan" and spec.product in ("pixoo64", "timegate"):
        print("Only hardware 90/92/400 requires a LAN token: DeviceToken for 90/92, LocalToken for 400. "
              "Use DIVOOM_LOCAL_TOKEN or hidden input; other hardware does not require or send a token.")
    for p in spec.parameters:
        state = "required" if p.required and p.default is None and not p.auto else "optional/automatic"
        print(f"  {p.name} ({p.wire}, {p.type}, {state}): {p.description}")
    if spec.notes:
        print(spec.notes)
    print("Documentation: " + ", ".join(spec.source_urls))


def _params(text: str) -> dict[str, Any]:
    try:
        if text == "-":
            value = json.load(sys.stdin)
        elif text.startswith("@"):
            value = json.loads(Path(text[1:]).read_text(encoding="utf-8-sig"))
        else:
            value = json.loads(text)
    except (ValueError, OSError) as exc:
        raise ValidationError(f"Cannot read JSON parameters: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError("Parameters must be a JSON object")
    return value


def _token(client: BaseDevice, spec: APISpec) -> None:
    if spec.route == "lan" and client.profile.local_token_required and client._token is None:
        if not sys.stdin.isatty():
            raise TokenRequiredError("Set DIVOOM_LOCAL_TOKEN for noninteractive hardware 90/92/400 LAN commands")
        client.set_local_token(getpass.getpass("Device token from settings (hidden): "))


def _interactive(args: argparse.Namespace) -> int:
    if not sys.stdin.isatty():
        raise ValidationError("Interactive mode requires a terminal. Use discover / apis / describe / call.")
    with _connect(args, interactive=True) as client:
        print(f"Selected {client.device.name}: {client.product}, hardware {client.device.hardware}")
        apis = client.list_apis()
        while True:
            _api_table(apis)
            answer = input("API number or method name (q to quit): ").strip()
            if answer.lower() == "q":
                return 0
            try:
                name = apis[int(answer) - 1].name if answer.isdigit() and 1 <= int(answer) <= len(apis) else answer
                spec = client.describe_api(name)
                _describe(spec)
                params = _params(input("Parameters as JSON or @file (Enter for {}): ").strip() or "{}")
                if spec.route == "upload" and "file_path" not in params:
                    params["file_path"] = input("Upload file path: ").strip().strip('"')
                if spec.route == "download" and "destination" not in params:
                    params["destination"] = input("New download destination: ").strip().strip('"')
                _token(client, spec)
                _emit(client.call(name, **params))
            except (DivoomError, OSError) as exc:
                print(f"Error: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.action is None:
            return _interactive(args)
        if args.action == "discover":
            devices = _discover(args)
            _emit([d.as_dict() for d in devices]) if args.json else _device_table(devices)
            return 0
        if args.action in ("apis", "describe") and not args.ip and args.device_id is None:
            product = args.product
            if args.hardware is not None:
                if args.hardware not in PROFILES:
                    raise UnsupportedDeviceError(f"Hardware {args.hardware} is not supported")
                hardware_product = PROFILES[args.hardware].product
                if product and product != hardware_product:
                    raise UnsupportedDeviceError("--product and --hardware disagree")
                product = hardware_product
            if product:
                if args.action == "apis":
                    apis = list_apis(product)
                    _emit([s.as_dict() for s in apis]) if args.json else _api_table(apis)
                else:
                    _describe(describe_api(product, args.api), args.json)
                return 0
        with _connect(args) as client:
            if args.action == "apis":
                apis = client.list_apis()
                _emit([s.as_dict() for s in apis]) if args.json else _api_table(apis)
            elif args.action == "describe":
                _describe(client.describe_api(args.api), args.json)
            else:
                params = _params(args.params)
                for flag, key in (("file", "file_path"), ("preview", "preview_path"),
                                  ("duration", "video_duration"), ("destination", "destination")):
                    value = getattr(args, flag)
                    if value is not None:
                        if key in params:
                            raise ValidationError(f"Specify {key} once, in --params or its file option")
                        params[key] = value
                spec = client.describe_api(args.api)
                _token(client, spec)
                _emit(client.call(args.api, **params))
        return 0
    except (DivoomError, OSError) as exc:
        if args.json:
            print(json.dumps({"error": type(exc).__name__, "message": str(exc),
                              "api": getattr(exc, "api_name", None)}, ensure_ascii=False), file=sys.stderr)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, EOFError):
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
