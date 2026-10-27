"""Read a clock, or apply a caller-provided JSON-only patch and read it back.

Read: python examples/astrotoo_clock.py --ip 192.168.1.50
Write: add --clock-id ID --patch patch.json after inspecting the saved configuration.
patch.json contains an ItemPatchList array, e.g. [{"index":0,"patch":{"size":72}}].
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from divoom_wifi import connect


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ip", required=True)
    parser.add_argument("--clock-id", type=int)
    parser.add_argument("--patch", type=Path)
    args = parser.parse_args()
    if args.patch and args.clock_id is None:
        parser.error("--patch requires an explicit --clock-id")
    with connect(args.ip, hardware=530) as astro:
        print(json.dumps(astro.get_local_clock(clock_id=args.clock_id), ensure_ascii=False, indent=2))
        print(json.dumps(astro.get_local_fonts(), ensure_ascii=False, indent=2))
        if args.patch:
            changes = json.loads(args.patch.read_text(encoding="utf-8-sig"))
            print(astro.patch_local_clock(clock_id=args.clock_id, item_patch_list=changes))
            print(json.dumps(astro.get_local_clock(clock_id=args.clock_id), ensure_ascii=False, indent=2))
            print(astro.get_current_clock())


if __name__ == "__main__":
    main()
