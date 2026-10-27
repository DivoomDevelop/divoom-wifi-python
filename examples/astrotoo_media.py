"""Upload ONE image/video to a caller-selected existing normal local album.

Use a unique media filename. Video example:
python examples/astrotoo_media.py --ip 192.168.1.50 --album 110001 clip.mp4 \
    --preview preview.webp --duration 30 --width 480 --height 480
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from divoom_wifi import connect


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ip", required=True)
    parser.add_argument("--album", type=int, required=True, help="Existing normal AlbumType:0 album ClockId")
    parser.add_argument("file", type=Path)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    args = parser.parse_args()
    with connect(args.ip, hardware=530) as astro:
        print(json.dumps(astro.get_local_albums(), ensure_ascii=False, indent=2))
        print(astro.upload_media(file_path=args.file, clock_id=args.album,
                                 preview_path=args.preview, video_duration=args.duration,
                                 photo_width=args.width, photo_height=args.height))
        print(astro.wait_for_photo(clock_id=args.album, file_name=args.file.name, timeout=60))


if __name__ == "__main__":
    main()
