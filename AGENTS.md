# Instructions for agents working in this repo

This is a small set of static marketing/position pages (see README.md for
the deploy model — Cloudflare Pages, served through gooey.ai via a proxy).
Each top-level folder (`sovereignty/`, `research/`, `ecocost/`, ...) is one
page, hand-written as a single self-contained `index.html`. There's no
build step, no bundler, no JS framework — pages are edited directly.

Two things have already gone wrong once in this repo and are easy to get
wrong again, so they're enforced by scripts instead of just written down
here:

## 1. Every page's links must be real

A page must not ship with placeholder/dummy links (`href="#"`, an empty
`href`, `javascript:void(0)`, an `example.com`/`test.com`-style stand-in
domain, leftover `TODO`/`FIXME` text in a URL), and every link — internal or
external — must actually resolve.

Before opening a PR that adds or edits a page, run:

```bash
python3 scripts/check_links.py
```

This checks every `<a href>` on every page: placeholder patterns fail
immediately; internal/relative links are resolved the same way the gooey.ai
proxy resolves them (respecting a page's own `<base href>`, see README.md)
and must point at a file that exists; external `http(s)` links get a live
request. It does **not** require external links to be on a gooey.ai domain —
these pages cite outside sources (news, papers, orgs) constantly, and that's
expected. "Related to Gooey, not dummy" means real and reachable, not
restricted to Gooey's own domain. A 404/410 or a dead domain fails the
check; rate-limiting/5xx/timeouts from someone else's server are printed as
warnings but don't fail it, since blocking a PR on a third party's flaky
server helps no one — use `--offline` to skip live checks entirely (e.g. if
you have no network).

This runs in CI on every PR (`.github/workflows/checks.yml`) — but run it
yourself first, it's faster than waiting on CI.

## 2. The header (logo + title + Login button) must look identical on every page

It didn't, until this file existed: sovereignty, research, and ecocost each
had their own slightly different header CSS (different position, button
shape, button color). `scripts/site_header.py` is now the single canonical
copy of that header's HTML and CSS. Every page still embeds its own literal
copy — there's no shared include, because each page is served standalone
through the gooey.ai proxy — but the copies must be byte-identical (aside
from each page's own `<span class="h-title">` text).

**Adding a new top-level page:** copy `HEADER_HTML`/`HEADER_CSS` from
`scripts/site_header.py` into the new page verbatim (substituting the
page's title), give the page's `:root` a `--pad-x: clamp(20px, 4vw, 60px);`
and `--site-header-h: 60px;`, wire up a scroll listener that toggles
`.scrolled` on `#siteHeader` (see the comment at the bottom of
`scripts/site_header.py` for the four-line version), and add the page to
`PAGES` in that same file.

**Changing the header design on purpose:** edit `HEADER_CSS`/`HEADER_HTML`
in `scripts/site_header.py` first, then paste the result into every page
listed in `PAGES`.

Either way, verify with:

```bash
python3 scripts/check_site_header.py
```

This also runs in CI on every PR.

## Before opening a PR for a new or edited page

1. `python3 scripts/check_links.py`
2. `python3 scripts/check_site_header.py` (if the page has the shared header)
3. Actually load the page in a browser and check it — these scripts catch
   drift and dead links, not visual regressions.
