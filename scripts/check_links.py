#!/usr/bin/env python3
"""Check every link on every page for placeholder junk and dead targets.

Run this before opening a PR that adds or edits a page:

    python3 scripts/check_links.py            # full check, hits the network
    python3 scripts/check_links.py --offline  # skip live HTTP checks (CI-safe, no network flakiness)
    python3 scripts/check_links.py sovereignty/index.html research/index.html

It scans every `href="..."` in the given files (default: every *.html in the
repo) and fails if a link is:

  * a placeholder/dummy value — "#", "", "javascript:void(0)", an
    example.com / test.com / lorem-ipsum style stand-in domain, or a
    "TODO"/"FIXME" left in a URL
  * an internal link (relative path, or an absolute /path) that doesn't
    resolve to a real file in the repo — resolved the same way the proxy
    resolves it, honoring a page's own `<base href>` if it sets one
  * an external http(s) link that doesn't actually load (unless --offline)

It does NOT require external links to be on a gooey.ai domain — pages here
cite outside sources (news coverage, papers, orgs) all the time, and that's
fine. "related to Gooey, not dummy" means real, reachable, non-placeholder
links, not links restricted to Gooey's own domain.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent

PLACEHOLDER_DOMAINS = {
    "example.com", "example.org", "example.net",
    "test.com", "foo.com", "bar.com", "baz.com",
    "yourdomain.com", "yoursite.com", "mysite.com", "website.com",
    "placeholder.com", "sample.com", "dummy.com", "acme.com",
}
PLACEHOLDER_TEXT = re.compile(r"\b(TODO|FIXME|XXX|lorem ?ipsum)\b", re.I)
EMPTY_HREFS = {"", "#"}
JS_HREF = re.compile(r"^\s*javascript\s*:", re.I)

BASE_HREF_RE = re.compile(r'<base\s+href="([^"]*)"', re.I)


class LinkParser(HTMLParser):
    """Collects (href, line) for every <a href=...> in a document."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, int]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value is not None:
                self.links.append((value, self.getpos()[0]))


def find_pages(paths: list[str]) -> list[pathlib.Path]:
    if paths:
        return [pathlib.Path(p).resolve() for p in paths]
    return sorted(ROOT.rglob("*.html"))


def classify(href: str) -> str | None:
    """Return a failure reason, or None if the href looks fine structurally."""
    stripped = href.strip()
    if stripped in EMPTY_HREFS:
        return "empty/placeholder anchor"
    if JS_HREF.match(stripped):
        return "javascript: pseudo-link"
    if PLACEHOLDER_TEXT.search(stripped):
        return "placeholder text (TODO/FIXME/lorem ipsum) left in URL"
    if stripped.startswith(("http://", "https://")):
        host = re.sub(r"^https?://", "", stripped).split("/", 1)[0].split(":", 1)[0].lower()
        if host in PLACEHOLDER_DOMAINS:
            return f"placeholder domain ({host})"
    return None


def resolve_internal(href: str, page: pathlib.Path, base_href: str | None) -> pathlib.Path:
    if base_href:
        base_dir = (page.parent / base_href).resolve()
    else:
        base_dir = page.parent
    return (base_dir / href.split("#", 1)[0].split("?", 1)[0]).resolve()


def check_page(page: pathlib.Path) -> list[tuple[int, str, str]]:
    """Return a list of (line, href, reason) failures for one page."""
    text = page.read_text(encoding="utf-8", errors="replace")
    m = BASE_HREF_RE.search(text)
    base_href = m.group(1) if m else None

    parser = LinkParser()
    parser.feed(text)

    failures = []
    for href, line in parser.links:
        stripped = href.strip()
        if stripped.startswith("mailto:") or stripped.startswith("tel:"):
            continue
        if stripped.startswith("#"):
            if stripped == "#":
                failures.append((line, href, "empty/placeholder anchor"))
            continue  # in-page anchors aren't file targets to resolve

        reason = classify(stripped)
        if reason:
            failures.append((line, href, reason))
            continue

        if stripped.startswith(("http://", "https://")):
            continue  # checked separately, in bulk, with caching

        if stripped.startswith("//"):
            continue  # protocol-relative, treat like an external link

        target = resolve_internal(stripped, page, base_href)
        try:
            shown = target.relative_to(ROOT)
        except ValueError:
            shown = target  # resolved outside the repo entirely
        if not target.exists():
            failures.append((line, href, f"no such file: {shown}"))

    return failures


def collect_external_links(pages: list[pathlib.Path]) -> dict[str, list[tuple[pathlib.Path, int]]]:
    by_url: dict[str, list[tuple[pathlib.Path, int]]] = {}
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        parser = LinkParser()
        parser.feed(text)
        for href, line in parser.links:
            stripped = href.strip()
            if stripped.startswith(("http://", "https://")):
                by_url.setdefault(stripped, []).append((page, line))
    return by_url


def _request(url: str, method: str) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; gooey-link-check/1.0)"}
    if method == "GET":
        headers["Range"] = "bytes=0-0"  # ask for one byte, some servers still send the whole body
    req = urllib.request.Request(url, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        if resp.status >= 400:
            return f"HTTP {resp.status}"
    return None


def _try(url: str, method: str) -> tuple[bool, str | None]:
    """Return (fatal, message). message is None on success."""
    try:
        err = _request(url, method)
        if err is None:
            return False, None
        code = int(err.split()[1])
        return code in (404, 410), err
    except urllib.error.HTTPError as e:
        if e.code in (403, 405, 429, 501) or e.code >= 500:
            return False, f"HTTP {e.code}"  # bot-blocking / rate-limit / server hiccup, not our problem
        return e.code in (404, 410), f"HTTP {e.code}"
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if isinstance(e.reason, OSError) and "not known" in reason.lower():
            return True, "DNS lookup failed (domain doesn't exist)"
        return False, f"unreachable ({reason})"  # timeout / TLS / connection issue: often transient
    except Exception as e:  # noqa: BLE001 - never let one flaky URL crash the whole check
        return False, f"unreachable ({e.__class__.__name__})"


def check_url_live(url: str) -> tuple[bool, str | None]:
    """Return (fatal, message). message is None when the link is fine.

    Only a 404/410 or a dead domain (DNS failure) is fatal — those mean the
    link is genuinely broken. Rate-limiting, 5xx, timeouts and TLS hiccups
    are printed as warnings but don't fail the check: they're as likely to be
    the target server having a bad moment (or blocking bots) as an actually
    dead link, and CI shouldn't block a PR over someone else's flaky server.

    Some servers (worldbank.org among them) also return 404 for HEAD but 200
    for GET, so a HEAD failure is retried with GET before it's trusted.
    """
    fatal, message = _try(url, "HEAD")
    if message is None:
        return False, None
    return _try(url, "GET")


def _rel(path: pathlib.Path) -> pathlib.Path | str:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="specific HTML files to check (default: every *.html)")
    ap.add_argument("--offline", action="store_true", help="skip live HTTP checks of external links")
    args = ap.parse_args()

    pages = find_pages(args.paths)
    if not pages:
        print("no HTML files found", file=sys.stderr)
        return 1

    ok = True

    for page in pages:
        for line, href, reason in check_page(page):
            ok = False
            print(f"{_rel(page)}:{line}: {reason} -> {href!r}")

    if not args.offline:
        by_url = collect_external_links(pages)
        with ThreadPoolExecutor(max_workers=12) as pool:
            results = dict(zip(by_url, pool.map(check_url_live, by_url)))
        for url, (fatal, message) in results.items():
            if message is None:
                continue
            ok = ok and not fatal
            label = "" if fatal else "warning: "
            for page, line in by_url[url]:
                print(f"{_rel(page)}:{line}: {label}{message} -> {url!r}")

    if ok:
        print(f"ok: checked {len(pages)} page(s)")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
