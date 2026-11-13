# Instructions for agents working in this repo

This is a small set of static marketing/position pages (see README.md for
the deploy model — Cloudflare Pages, served through gooey.ai via a proxy).
Each top-level folder (`sovereignty/`, `research/`, `ecocost/`, ...) is one
page, hand-written as a single self-contained `index.html`. There's no
build step, no bundler, no JS framework — pages are edited directly.

Five things have already gone wrong once in this repo and are easy to get
wrong again, so they're enforced by scripts instead of just written down
here:

## 1. Pull the latest changes before editing anything

**Every agent must run `git pull --ff-only` before making any change in this
repository, even for a small follow-up edit.** Do not read the current checkout
and begin editing first. Check `git status`, preserve any existing user changes,
then pull. If local changes prevent the pull, do not overwrite, reset, or discard
them: preserve them safely (for example with a targeted stash), pull, restore
them, and resolve any conflict without losing either side. If that cannot be
done safely, stop and ask the user.

The pull must happen during the current user task; do not assume a pull from an
earlier session means the checkout is still current.

## 2. Every page's links must be real

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

## 3. A new page's Gooey URL must not clash with an existing route

Creating a top-level folder does not guarantee that its matching Gooey URL is
available. Gooey application routes — including profiles, workflows, and other
pages — take precedence over the static-page proxy. For example, a new
`lokalibrary/` folder cannot appear at `gooey.ai/lokalibrary` if that URL is
already assigned to a profile.

**Before opening a PR that adds or renames a top-level page**, run:

```bash
python3 scripts/check_route_clashes.py
```

The check requests every prospective `gooey.ai/<folder>` URL. It accepts a 404
(the slug is free and the new page is not deployed yet) or a page already
proxied to the matching folder in this repository. Any other successful page is
an existing Gooey route and fails as a collision. Do not merge the static page
until that existing route has been renamed or a different folder/URL slug has
been chosen. Never infer that a route is free merely because its raw
`gooey-static-pages.pages.dev` URL works.

This runs in CI on every PR (`.github/workflows/checks.yml`).

## 4. The header (logo + title + Login button) must look identical on every page

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

## 5. `/language/<name>` pages are generated — don't edit their HTML

The language evaluation pages (`language/kinyarwanda/`, `swahili/`, `kikuyu/`, ...)
all share one layout so that twenty of them stay identical. Their
`index.html` is **generated**; hand edits are overwritten and fail CI.

- Layout/CSS: `language/assets/language-page.css`. Charts, table, scatter, samples:
  `language/assets/language-page.js`. Change these once and every page follows.
- One language: `language/_src/<slug>/` (`page.json` plus `picks.frag`, `featured.frag`,
  `faq.json`). FAQ layout is shared in `language/_src/faq.tmpl`; `scripts/language_faq.py`
  generates the standard questions and answers from benchmark data and verified dataset
  context in `faq.json` (not manually maintained answers or hosting claims). The shared
  evaluation-method answer includes a clinical-safety caveat on every language page.
  Numbers come from `language/data/<code>/` (summary CSV, pricing and
  EcoCost JSON), so counts and charts can't disagree with the data.
- Shared page skeleton: `language/_src/body.tmpl`. Footer language list:
  `language/_src/languages.json`.
- A model or speech engine the shared script doesn't know yet (logo, maker, label size,
  ring colour) is added once to `language-page.js`; the check tells you what is missing.

Each language also has an `ai-agent` page (`language/<slug>/ai-agent/`), generated from
`language/_src/agent.tmpl`, `language/_src/<slug>/agent.json` and the shared
`language/assets/language-agent.{css,js}`. Its illustrations are `language/assets/ai-agent/hero.*` and
`channel.*` (webp, jpg or png); a labelled placeholder shows until they exist.

Each model has a page per language (`models/<model-slug>/<language-slug>/`, e.g.
`models/gpt-5-6-sol/kinyarwanda/`), generated from `language/_src/model.tmpl` and
`language/_src/models.json` (maker, open weights, hosting regions, optional previous version) plus the
language's data, with `language/assets/language-model.{css,js}`. `models/` is its own top-level route, so it needs
`models/assets/gooey-logo.png` for the shared header, and gooey.ai must proxy it like `language`.

Links between the three page kinds are relative paths, so `check_links.py` can verify them.
`language/assets/language-links.js` rewrites them to `gooey.ai` URLs when a page is served through the proxy.
`check_language_pages.py` also fails if a generated page is not linked from another one, or lacks the links it
should have (model page to its language page and agent page; language page to its agent page and every model page).

After any of those change:

```bash
python3 scripts/build_language_pages.py     # rewrite the pages
python3 scripts/check_language_pages.py     # fail if a page is stale or off-template
```

To add a language:

1. `python3 scripts/build_language_data.py --csv <evaluator.csv> --code <xxx> --lang <Name> --country <ISO> --date <YYYY-MM-DD> --samples 3,9,14`
   writes `language/data/<xxx>/` (summary, pricing, EcoCost, sample cards) from the evaluator CSV
   and the public run pages it links to.
2. Copy an existing `language/_src/<slug>/`, edit its wording and chart settings (`page.json`, the `.frag` files,
   and `agent.json` for the ai-agent page), then build.
3. Register both pages in `PAGES` in `scripts/site_header.py` and add the language's name to
   `language/_src/languages.json` if it isn't there.

## Before opening a PR for a new or edited page

1. Before making any change, run `git status` and `git pull --ff-only` as
   described above.
2. `python3 scripts/check_route_clashes.py`
3. `python3 scripts/check_links.py`
4. `python3 scripts/check_site_header.py` (if the page has the shared header)
   `python3 scripts/check_language_pages.py` (for `/language/<name>` pages)
5. Actually load the page in a browser and check it — these scripts catch
   drift and dead links, not visual regressions.
