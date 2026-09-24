#!/usr/bin/env python3
"""Verify every page's header still matches the canonical one in site_header.py.

    python3 scripts/check_site_header.py

Run this before opening a PR that touches a page's header, or that adds a
new page. It fails (with a diff) if a page's `.site-header` CSS or markup no
longer matches scripts/site_header.py — that file is the single source of
truth for what the header/button look like, precisely so they can't drift
apart the way sovereignty/research/ecocost once did.

If you're intentionally changing the header design: edit site_header.py
first, copy the new HEADER_CSS/HEADER_HTML into every page listed in
PAGES, then re-run this script to confirm they match.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from site_header import HEADER_CSS, HEADER_HTML, PAGES  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent


def check(rel_path: str, title: str) -> list[str]:
    page = ROOT / rel_path
    problems = []
    if not page.exists():
        return [f"{rel_path}: file is missing (remove it from PAGES in scripts/site_header.py?)"]

    text = page.read_text(encoding="utf-8")

    if HEADER_CSS not in text:
        problems.append(
            f"{rel_path}: .site-header CSS doesn't match scripts/site_header.py's HEADER_CSS "
            "(a rule was added, removed, or edited)"
        )

    expected_html = HEADER_HTML.format(title=title)
    if expected_html not in text:
        problems.append(
            f"{rel_path}: header markup doesn't match scripts/site_header.py's HEADER_HTML "
            f"for title {title!r} (check the <header id=\"siteHeader\"> block)"
        )

    return problems


def main() -> int:
    problems = []
    for rel_path, title in PAGES.items():
        problems.extend(check(rel_path, title))

    # Catch pages that use the shared header but were never added to PAGES.
    known = {ROOT / p for p in PAGES}
    for candidate in sorted(ROOT.glob("*/index.html")):
        if candidate in known:
            continue
        if 'id="siteHeader"' in candidate.read_text(encoding="utf-8"):
            problems.append(
                f"{candidate.relative_to(ROOT)}: has a #siteHeader but isn't listed in "
                "PAGES in scripts/site_header.py — add it so this check covers it"
            )

    if problems:
        for p in problems:
            print(p)
        return 1

    print(f"ok: {len(PAGES)} page header(s) match scripts/site_header.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
