"""Download the public reference for maintainers (never called by the SDK).

Existing snapshots are protected by an optimistic content check before writing.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import html
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = "https://docin.divoom-gz.com/server/index.php?s="
PRODUCTS = {"PIXOO64": "pixoo64", "TimeGate": "timegate", "TimeFrame": "timeframe", "AstroToo": "astrotoo"}


def get(route: str, **parameters: object) -> dict:
    request = urllib.request.Request(SERVER + route, data=urllib.parse.urlencode(parameters).encode())
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.load(response)
            break
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(attempt + 1)  # Only this read-only documentation fetch is retried.
    if result.get("error_code") != 0:
        raise RuntimeError(result)
    return result["data"]


def walk(catalog: dict, product: str, path: str = ""):
    path += "/" + catalog["cat_name"]
    for page in catalog.get("pages", []):
        yield {"page_id": int(page["page_id"]), "product": product, "category": path, "title": page["page_title"]}
    for child in catalog.get("catalogs", []):
        yield from walk(child, product, path)


def main() -> None:
    target = ROOT / "docs/reference/pages.json"
    before = target.read_bytes() if target.exists() else None
    menu = get("/api/item/info", item_id=5)["menu"]
    pages = []
    for catalog in menu["catalogs"]:
        if catalog["cat_name"] in PRODUCTS:
            pages.extend(walk(catalog, PRODUCTS[catalog["cat_name"]]))
    pages.extend({"page_id": p, "product": "common", "category": "/common", "title": ""} for p in (24, 25, 145))

    def download(page: dict) -> dict:
        data = get("/api/page/info", page_id=page["page_id"])
        content = html.unescape(data["page_content"])
        return {**page, "title": data["page_title"], "url": f'https://docin.divoom-gz.com/web/#/5/{page["page_id"]}',
                "content": content, "sha256": hashlib.sha256(content.encode()).hexdigest()}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        result = list(pool.map(download, pages))
    payload = json.dumps({"reference_date": "2026-10-27", "pages": result}, ensure_ascii=False, indent=2) + "\n"
    # Re-read immediately before the write: never replace an externally changed file.
    current = target.read_bytes() if target.exists() else None
    if current != before:
        raise RuntimeError(f"Concurrent edit detected: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
    print(f"Downloaded {len(result)} pages to {target}")


if __name__ == "__main__":
    main()
