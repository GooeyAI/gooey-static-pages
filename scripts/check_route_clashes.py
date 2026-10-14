#!/usr/bin/env python3
"""Ensure top-level static-page slugs do not clash with existing Gooey routes.

Run this before opening a PR that adds or renames a top-level page:

    python3 scripts/check_route_clashes.py
    python3 scripts/check_route_clashes.py lokalibrary

For each top-level ``<slug>/index.html``, this requests ``https://gooey.ai/<slug>``.
The route is safe when it is either:

* a 404, meaning a new page has not been deployed yet and the slug is free; or
* already proxied to this repository, identified by the Cloudflare Pages
  ``<base>`` tag that Gooey injects into static pages.

A successful Gooey page without that matching ``<base>`` tag is owned by
something else (for example a profile, workflow, or application route) and is
reported as a collision.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
GOOEY_ORIGIN = "https://gooey.ai"
PAGES_HOST = "gooey-static-pages.pages.dev"


class BaseParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.href: str | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag.lower() != "base" or self.href is not None:
            return
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.href = value
                return


def find_slugs(requested: list[str]) -> list[str]:
    if requested:
        return sorted({slug.strip("/") for slug in requested if slug.strip("/")})
    return sorted(
        path.name
        for path in ROOT.iterdir()
        if path.is_dir() and (path / "index.html").is_file()
    )


def is_matching_static_base(base_href: str | None, slug: str) -> bool:
    if not base_href:
        return False
    parsed = urllib.parse.urlparse(base_href)
    return (
        parsed.scheme == "https"
        and parsed.netloc == PAGES_HOST
        and parsed.path.rstrip("/") == f"/{slug}"
    )


def check_slug(slug: str) -> tuple[bool, str]:
    quoted_slug = urllib.parse.quote(slug, safe="")
    url = f"{GOOEY_ORIGIN}/{quoted_slug}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; gooey-route-check/1.0)"},
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return True, "available (404; not deployed yet)"
        return False, f"could not verify route (HTTP {error.code})"
    except urllib.error.URLError as error:
        return False, f"could not verify route ({error.reason})"
    except Exception as error:  # noqa: BLE001 - report network/parser failures cleanly
        return False, f"could not verify route ({error.__class__.__name__})"

    parser = BaseParser()
    parser.feed(body)
    if is_matching_static_base(parser.href, slug):
        return True, "already serves this repository's static page"

    detail = f"; found base {parser.href!r}" if parser.href else ""
    return (
        False,
        "URL COLLISION: Gooey already serves a non-static page at "
        f"{url}{detail}",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "slugs",
        nargs="*",
        help="specific top-level slugs to check (default: every top-level page)",
    )
    args = parser.parse_args()

    slugs = find_slugs(args.slugs)
    if not slugs:
        print("no top-level pages found", file=sys.stderr)
        return 1

    ok = True
    for slug in slugs:
        safe, message = check_slug(slug)
        ok = ok and safe
        label = "ok" if safe else "ERROR"
        print(f"{label}: /{slug} — {message}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
