#!/usr/bin/env python3
"""Render the 1200x630 share images (og:image) of the generated pages.

    python3 scripts/build_og_images.py            # render the cards that don't exist yet, delete replaced ones
    python3 scripts/build_og_images.py --force    # re-render every card

Each page's card is described by the page builders through scripts/seo.py (og_image), and saved next to the page's
index.html as og-<hash>.jpg. Run this after build_language_pages.py or build_papers.py whenever a page's numbers,
title or picture change; check_og_images.py (in CI) fails until you do.

Needs Pillow and a Chromium-family browser (Chrome, Brave, Edge, Chromium, or Playwright's). Set OG_BROWSER to the
browser's executable to pick one. Inter is loaded from Google Fonts, so it needs the network.
"""

from __future__ import annotations

import glob
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import seo  # noqa: E402

BROWSERS = [  # Playwright's Chrome for Testing first: it has no first-run screens to hang a headless run
    *sorted(glob.glob(os.path.expanduser("~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/*.app/Contents/MacOS/*")),
            reverse=True),
    *sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome")), reverse=True),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge",
]


def browser() -> str:
    for b in ([os.environ["OG_BROWSER"]] if os.environ.get("OG_BROWSER") else BROWSERS):
        path = b if os.path.isabs(b) else shutil.which(b)
        if path and os.path.exists(path):
            return path
    raise SystemExit("No Chromium-family browser found. Install Chrome, or set OG_BROWSER to a browser executable.")


def cards() -> dict[pathlib.Path, dict]:
    """Build every generated page in memory (nothing is written), which registers each page's card."""
    import build_language_pages
    import build_papers
    import build_static_seo
    build_language_pages.all_pages()
    build_static_seo.pages()
    for paper in build_papers.PAPERS:
        if (build_papers.RESEARCH / "pdf" / f"{paper['slug']}.pdf").exists():
            build_papers.build_page(paper)
    return dict(seo.CARDS)


def render(card: dict, out: pathlib.Path, exe: str, scratch: pathlib.Path) -> None:
    from PIL import Image
    src, png = scratch / "card.html", scratch / "card.png"
    src.write_text(seo.card_html(card, seo.ROOT.as_uri() + "/"), encoding="utf-8")
    png.unlink(missing_ok=True)
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--no-first-run", "--no-default-browser-check", "--disable-extensions",
                    f"--screenshot={png}", "--window-size=1200,630", "--force-device-scale-factor=1",
                    "--virtual-time-budget=8000", f"--user-data-dir={scratch / 'profile'}", src.as_uri()],
                   check=True, capture_output=True, timeout=120)
    im = Image.open(png).convert("RGB")
    if im.size != (1200, 630):
        raise SystemExit(f"{out}: browser returned a {im.size} screenshot, not 1200x630")
    im.save(out, "JPEG", quality=85, optimize=True, progressive=True)


def main(argv: list[str]) -> int:
    force = "--force" in argv
    wanted = cards()
    todo = [p for p in wanted if force or not p.exists()]
    if todo:
        exe = browser()
        with tempfile.TemporaryDirectory() as tmp:
            for out in sorted(todo):
                render(wanted[out], out, exe, pathlib.Path(tmp))
                print(f"wrote {out.relative_to(seo.ROOT)} ({out.stat().st_size // 1024} KB)")
    # a page whose card changed points at a new file; remove the one it replaced
    for folder in {p.parent for p in wanted}:
        for old in folder.glob("og-*.jpg"):
            if old not in wanted:
                old.unlink()
                print(f"deleted {old.relative_to(seo.ROOT)}")
    print(f"ok: {len(wanted)} share image(s), {len(todo)} rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
