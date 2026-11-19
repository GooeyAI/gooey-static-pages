#!/usr/bin/env python3
"""Fail if a page's share image (og:image) is missing, or isn't a 1200x630 JPEG.

    python3 scripts/check_og_images.py

A page's og:image is linked on the Cloudflare Pages host or on gooey.ai, so it maps straight to a file in this repo.
Generated pages name the file after a hash of the card's content (scripts/seo.py), so this also catches a card that
wasn't re-rendered after its page's numbers changed: run python3 scripts/build_og_images.py. Standard library only.
"""

from __future__ import annotations

import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOSTS = ("https://gooey-static-pages.pages.dev/", "https://gooey.ai/")
SKIP = {"drafts", "node_modules", "_src", ".git", ".claude"}
OG_RE = re.compile(r'<meta\s+property="og:image"\s+content="([^"]+)"', re.S)


def jpeg_size(data: bytes) -> tuple[int, int] | None:
    """(width, height) from a JPEG's start-of-frame marker, or None if it isn't a JPEG."""
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            return None
        marker, length = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + length
    return None


def main() -> int:
    problems, checked = [], 0
    for page in sorted(ROOT.rglob("index.html")):
        rel = page.relative_to(ROOT)
        if SKIP & set(rel.parts):
            continue
        for src in OG_RE.findall(page.read_text(encoding="utf-8")):
            host = next((h for h in HOSTS if src.startswith(h)), None)
            if not host:
                problems.append(f"{rel}: og:image {src} is not on this site")
                continue
            checked += 1
            f = ROOT / src[len(host):]
            if not f.is_file():
                problems.append(f"{rel}: og:image {f.relative_to(ROOT)} does not exist (run: python3 scripts/build_og_images.py)")
            elif f.name.startswith("og-") and jpeg_size(f.read_bytes()) != (1200, 630):
                problems.append(f"{rel}: {f.relative_to(ROOT)} is not a 1200x630 JPEG")
    if problems:
        print("share image problems:")
        for p in problems:
            print("  " + p)
        return 1
    print(f"ok: {checked} share image(s) exist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
