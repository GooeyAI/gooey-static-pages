"""Search and sharing tags for generated pages: what goes in <head> after <title>, and the 1200x630 share image.

Every generated page (language, ai-agent, speech-to-text, model and research paper pages) gets the same set:

    description, canonical link, robots max-image-preview:large
    og:type / site_name / url / title / description / image (+ type, size, alt)
    twitter:card summary_large_image (+ image alt; X reads the og: tags for the rest)
    favicon, touch icon, theme colour (the same as gooey.ai)
    JSON-LD: WebPage or ScholarlyArticle, BreadcrumbList, FAQPage when the page has a FAQ, Dataset on a language page

URLs. The canonical URL is the gooey.ai address with a trailing slash, the form the pages' own links use
(language-links.js rewrites them to gooey.ai). Share images are linked on the Cloudflare Pages host directly:
gooey.ai answers asset URLs with a redirect to it, and some link-preview fetchers (WhatsApp) do not follow one.

Share images. og_image() describes a page's card (eyebrow, title, headline numbers, picture) and returns its URL.
The file name carries a hash of the card and of the template below, og-<hash>.jpg next to the page's index.html, so
a page whose numbers change points at a new file, social apps refetch it, and CI fails until the image is rendered:

    python3 scripts/build_og_images.py      # renders missing cards, deletes replaced ones
    python3 scripts/check_og_images.py      # fails if a page's og:image file is missing
"""

from __future__ import annotations

import hashlib
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://gooey.ai/"
ASSETS = "https://gooey-static-pages.pages.dev/"
# gooey.ai's own icons (the marketing site's Webflow CDN), so a shared or bookmarked page looks like the rest of gooey.ai
ICON = "https://cdn.prod.website-files.com/6864c89c210135e40bbd6674/68ad67680a9b0bee5776fa97_gooey-ico-2.png"
TOUCH = "https://cdn.prod.website-files.com/6864c89c210135e40bbd6674/68ad688f8931b3329a5b2083_webclip.png"
ORG = {"@type": "Organization", "@id": SITE + "#organization", "name": "Gooey.AI", "url": SITE,
       "logo": {"@type": "ImageObject", "url": TOUCH}}
EVALS = ("Language evaluations", SITE + "language-evaluation/")

# Lengths Google shows in a result: about 600 px of title (roughly 60 characters) and about 155-160 characters of
# description on desktop (less on phones). A description shorter than 120 leaves the snippet half empty, and Google is
# then more likely to write its own from the page. head() fails the build outside these limits.
TITLE_MAX = 60
DESC_MIN, DESC_MAX = 120, 155
BRAND = " | Gooey.AI"

# Every card this build described: output path -> card. build_og_images.py renders them.
CARDS: dict[pathlib.Path, dict] = {}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def text(fragment: str) -> str:
    """Plain text of an HTML fragment."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def url(path: str) -> str:
    """gooey.ai address of a repo folder, e.g. 'language/swahili' -> https://gooey.ai/language/swahili/"""
    return SITE + path.strip("/") + "/"


# --------------------------------------------------------------------------------------------------------------------
# <head>

def fit(*candidates: str, lo: int = 0, hi: int, what: str = "text") -> str:
    """The first candidate whose length is within lo..hi: list the fullest wording first and shorter fallbacks after,
    so a long language or model name still gets a title or description that fits."""
    for c in candidates:
        if lo <= len(c) <= hi:
            return c
    raise SystemExit(f"no {what} fits {lo}-{hi} characters; add a wording that does:\n"
                     + "\n".join(f"  {len(c):>3}  {c}" for c in candidates))


def head(*, path: str, title: str, description: str, og_title: str, og_type: str = "website",
         image: tuple[str, str] | None = None, graph: list[dict] = (), exact_title: bool = False,
         article: dict | None = None) -> str:
    """<title> and the tags that follow it, one per line, indented for <head>. image is (url, alt).
    og_title is the title without the brand: link previews show the site name on their own.
    exact_title lets a title run past TITLE_MAX when it must not be shortened (a paper's published title)."""
    if len(title) > TITLE_MAX and not exact_title:
        raise SystemExit(f"{path}: title is {len(title)} characters, over {TITLE_MAX}: {title}")
    if not DESC_MIN <= len(description) <= DESC_MAX:
        raise SystemExit(f"{path}: description is {len(description)} characters, not {DESC_MIN}-{DESC_MAX}: {description}")
    canonical = url(path)
    tags = [
        f"<title>{html.escape(title, quote=False)}</title>",
        f'<meta name="description" content="{esc(description)}" />',
        f'<link rel="canonical" href="{canonical}" />',
        '<meta name="robots" content="max-image-preview:large" />',
        f'<meta property="og:type" content="{og_type}" />',
        '<meta property="og:site_name" content="Gooey.AI" />',
        f'<meta property="og:url" content="{canonical}" />',
        f'<meta property="og:title" content="{esc(og_title)}" />',
        f'<meta property="og:description" content="{esc(description)}" />',
    ]
    if image:
        img, alt = image
        tags += [f'<meta property="og:image" content="{img}" />',
                 '<meta property="og:image:type" content="image/jpeg" />',
                 '<meta property="og:image:width" content="1200" />',
                 '<meta property="og:image:height" content="630" />',
                 f'<meta property="og:image:alt" content="{esc(alt)}" />']
    for key, prop in (("section", "article:section"), ("published", "article:published_time"),
                      ("modified", "article:modified_time")):
        if (article or {}).get(key):
            tags.append(f'<meta property="{prop}" content="{esc(article[key])}" />')
    tags.append('<meta name="twitter:card" content="summary_large_image" />')
    if image:
        tags.append(f'<meta name="twitter:image:alt" content="{esc(image[1])}" />')
    tags += [f'<link rel="icon" href="{ICON}" />',
             f'<link rel="apple-touch-icon" href="{TOUCH}" />',
             '<meta name="theme-color" content="#ffffff" />']
    if graph:
        blob = json.dumps({"@context": "https://schema.org", "@graph": list(graph)}, ensure_ascii=False)
        tags.append('<script type="application/ld+json">' + blob.replace("<", "\\u003c") + "</script>")
    return "".join(f"    {t}\n" for t in tags)


# --------------------------------------------------------------------------------------------------------------------
# JSON-LD

def webpage(path: str, name: str, description: str, image: tuple[str, str] | None = None, modified: str | None = None,
            about: dict | None = None, kind: str = "WebPage") -> dict:
    u = url(path)
    node = {"@type": kind, "@id": u, "url": u, "name": name, "description": description, "inLanguage": "en",
            "isPartOf": {"@type": "WebSite", "name": "Gooey.AI", "url": SITE}, "publisher": {"@id": ORG["@id"]},
            "breadcrumb": {"@id": u + "#breadcrumb"}}
    if image:
        node["primaryImageOfPage"] = {"@type": "ImageObject", "url": image[0], "width": 1200, "height": 630}
    if modified:
        node["dateModified"] = modified
    if about:
        node["about"] = about
    return node


def breadcrumbs(path: str, trail: list[tuple[str, str | None]]) -> dict:
    """trail: (name, url) from Home down; the last item's url may be None (this page)."""
    u = url(path)
    return {"@type": "BreadcrumbList", "@id": u + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": link or u} for i, (n, link) in enumerate(trail)]}


def faq(path: str, body: str) -> list[dict]:
    """FAQPage from the page's own FAQ section (<section id="faq">, one <details> per question), so the structured
    data can never say something the page doesn't. A question whose answer is a "coming soon" placeholder is left out."""
    m = re.search(r'<section[^>]*\bid="faq".*?</section>', body, re.S)
    if not m:
        return []
    pairs = []
    for q, a in re.findall(r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>", m.group(0), re.S):
        if "pricing-pending" in a:
            continue
        pairs.append({"@type": "Question", "name": text(q), "acceptedAnswer": {"@type": "Answer", "text": text(a)}})
    if not pairs:
        return []
    return [{"@type": "FAQPage", "@id": url(path) + "#faq", "mainEntity": pairs}]


def language(name: str, endonym: str | None = None) -> dict:
    node = {"@type": "Language", "name": name}
    if endonym and endonym != name:
        node["alternateName"] = endonym
    return node


# --------------------------------------------------------------------------------------------------------------------
# Share image (1200 x 630)
#
# The Gooey Pages share-image layout: a 400 px picture across the top, a teal rule, then a band with the eyebrow, the
# title and the Gooey.AI wordmark. On a generated page the picture is the page's headline result: a white panel with
# the top result and up to three numbers, beside the country map, the page's illustration or the model's logo.
#
# card = {"eyebrow": str, "title": str,
#         "date": str,                                  # optional, "bars" layout only: shown after the eyebrow
#         "lead": [label, text],                        # optional: the line at the top of the panel (text may be "")
#         "stats": [[label, value, unit, note], ...],   # up to 3
#         "people": [[name, affiliation], ...],         # instead of stats, up to 3
#         "paper": {"logo": file or None, "title": str, "byline": str, "marks": [files]},   # a research paper's panel
#         "wall": {"label": str, "logos": [files], "byline": str, "marks": [files]},      # a full-width row of logos
#         "visual": {"kind": "map" | "photo" | "logo" | "banner", "src": repo-relative file,   (or "bars": see BOARD_CSS)
#                    "position": CSS object-position (banner only, optional)}}
# A "banner" fills the whole picture area, as on the hand-written pages (their own 3:1 banner, never cropped badly).
# Files are repo-relative paths; their bytes are part of the card's hash.

CARD_CSS = """
html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:#fff;-webkit-font-smoothing:antialiased}
.og{width:1200px;height:630px;display:grid;grid-template-rows:400px 1fr;font-family:Inter,system-ui,sans-serif;color:#0a1021}
.og__top{position:relative;overflow:hidden;background:#eef9f7}
.og__dots{position:absolute;inset:0 auto 0 0;width:520px;background-image:radial-gradient(#3cc9b8 2.4px,transparent 2.9px);
  background-size:24px 24px;-webkit-mask-image:linear-gradient(90deg,#000 0,rgba(0,0,0,.55) 30%,transparent 100%);opacity:.55}
.og__circle{position:absolute;width:560px;height:560px;border-radius:50%;background:#c9f4ec;right:-60px;top:-140px}
.og__panel{position:absolute;left:56px;top:44px;width:660px;height:312px;box-sizing:border-box;padding:28px 30px;border-radius:20px;
  background:#fff;box-shadow:0 12px 36px rgba(10,16,33,.10);display:flex;flex-direction:column;gap:22px}
.og__lead span{display:block;font:600 15px/20px Inter,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#00665c}
.og__lead b{display:block;margin-top:6px;font:600 30px/38px Inter,sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.og__stats{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:14px;flex:1}
.og__stat{border:1px solid #e3e7ea;border-radius:14px;padding:16px 18px;display:flex;flex-direction:column;justify-content:space-between}
.og__stat span{font:500 16px/20px Inter,sans-serif;color:#4a5160}
.og__stat b{font:600 50px/1 Inter,sans-serif;letter-spacing:-.02em}
.og__stat b small{margin-left:4px;font:500 20px/1 Inter,sans-serif;letter-spacing:0;color:#4a5160}
.og__stat i{font:400 15px/19px Inter,sans-serif;font-style:normal;color:#5b6270;display:-webkit-box;-webkit-line-clamp:2;
  -webkit-box-orient:vertical;overflow:hidden}
.og__people{display:grid;gap:16px;align-content:start}
.og__people div{font:600 26px/32px Inter,sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.og__people div span{display:block;font:400 18px/24px Inter,sans-serif;color:#5b6270;overflow:hidden;text-overflow:ellipsis}
.og__panel.og__paper{top:30px;height:340px;padding:24px 30px;justify-content:space-between;gap:14px}
.og__venue{display:block;height:80px;max-width:300px;object-fit:contain;object-position:left center}
.og__ptitle{font:400 32px/40px Domine,serif;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;text-wrap:balance}
.og__by{display:flex;align-items:center;justify-content:space-between;gap:20px}
.og__by span{font:500 18px/24px Inter,sans-serif;color:#4a5160;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.og__marks{display:flex;gap:10px;flex:none}
.og__marks img{height:34px;width:auto}
.og__panel.og__wall{width:1088px;justify-content:space-between}
.og__logos{display:flex;flex-wrap:wrap;align-items:center;gap:22px 40px}
.og__logos img{height:64px;max-width:200px;object-fit:contain}
.og__banner{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.og__photo{position:absolute;right:0;top:0;width:470px;height:400px;object-fit:cover}
.og__map{position:absolute;right:70px;top:30px;width:370px;height:340px;object-fit:contain}
.og__logo{position:absolute;right:120px;top:70px;width:260px;height:260px;border-radius:50%;background:#fff;
  box-shadow:0 12px 36px rgba(10,16,33,.10);display:grid;place-items:center}
.og__logo img{width:140px;height:140px;object-fit:contain}
.og__band{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:40px;padding:0 56px;border-top:6px solid #00998a}
.og__eyebrow{font:600 20px/24px Inter,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#00665c;margin-bottom:10px}
.og__title{font:400 var(--size)/calc(var(--size) + 8px) Domine,serif;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  overflow:hidden;text-wrap:balance}
.og__mark{height:62px}
"""

CARD_HTML = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap">
<style>@font-face{{font-family:Domine;src:url("{root}language/assets/fonts/Domine-VariableFont_wght.ttf");font-weight:400 700}}
{css}</style></head><body><div class="og">
<div class="og__top"><div class="og__dots"></div><div class="og__circle"></div>{visual}{panel}</div>
<div class="og__band"><div><div class="og__eyebrow">{eyebrow}</div><div class="og__title" style="--size:{size}px">{title}</div></div>
<img class="og__mark" src="{root}language/assets/gooey-logo.png" alt=""></div>
</div></body></html>"""

WORDMARK = "language/assets/gooey-logo.png"

# The language pages' card ("visual": {"kind": "bars", "bars": [[score, sovereign, model logo, speech logo], ...]}, highest
# first): the Gooey.AI style guide's flat white hairline cards on the halftone background. Eyebrow and date across the
# top with the wordmark, the title, top chain and stat tiles on the left, the top Index bars on the right. Bar height is
# the score out of 100; blue (Blue 800) is sovereign-deployable, grey is private API.
BOARD_CSS = """
html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:#eef9f7;-webkit-font-smoothing:antialiased}
.bg{position:fixed;inset:0 auto 0 0;width:640px;background-image:radial-gradient(#3cc9b8 2.4px,transparent 2.9px);background-size:24px 24px;
  -webkit-mask-image:linear-gradient(90deg,#000 0,rgba(0,0,0,.55) 30%,transparent 100%);opacity:.55}
.c{position:relative;width:1200px;height:630px;box-sizing:border-box;padding:48px 56px 44px;display:grid;grid-template-columns:520px 1fr;
  grid-template-rows:auto 1fr;column-gap:40px;font-family:Inter,system-ui,sans-serif;color:#0a1021}
.top{grid-column:1/-1;display:flex;justify-content:space-between;align-items:center;margin-bottom:36px}
.top img{height:44px;mix-blend-mode:multiply}
.meta{font:500 18px/1 Inter,sans-serif;color:#4b587a}
.meta b{font-weight:600;font-size:16px;letter-spacing:.06em;text-transform:uppercase;color:#00998a}
.l{display:flex;flex-direction:column;min-width:0}
h1{margin:0;font:400 var(--h)/1.05 Domine,serif;letter-spacing:-.01em}
.win{margin-top:28px;font:500 16px/1 Inter,sans-serif;color:#4b587a}
.win strong{display:block;margin-top:10px;font:700 26px/1.2 Inter,sans-serif;color:#0a1021;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stats{margin-top:auto;display:flex;gap:12px}
.s{flex:1 1 auto;background:#fff;border:1px solid #e6e6e6;border-radius:16px;padding:16px 18px}
.s span{display:flex;align-items:center;gap:6px;font:500 14px/1 Inter,sans-serif;color:#4b587a;white-space:nowrap}
.s span img{width:16px;height:16px}
.s b{display:block;margin-top:12px;font:600 40px/1 Inter,sans-serif;letter-spacing:-.02em;white-space:nowrap}
.s b small{margin-left:4px;font:500 16px/1 Inter,sans-serif;letter-spacing:0;color:#4b587a}
.s i{display:block;margin-top:8px;font:400 13px/1.3 Inter,sans-serif;font-style:normal;color:#636363}
.r{background:#fff;border:1px solid #e6e6e6;border-radius:24px;padding:22px 24px 18px;display:flex;flex-direction:column;min-width:0}
.rh{display:flex;justify-content:space-between;align-items:center;gap:12px;font:500 14px/1 Inter,sans-serif;color:#4b587a}
.rh h3{margin:0;font:400 22px/1 Domine,serif;color:#0a1021;white-space:nowrap}
.lg{display:flex;gap:14px}.lg span{display:flex;align-items:center;gap:6px;white-space:nowrap}
.lg span:before{content:"";width:10px;height:10px;border-radius:2px;background:var(--c)}
.bars{flex:1;margin-top:14px;display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));column-gap:8px;align-items:end}
.bars div{display:flex;flex-direction:column;align-items:center;gap:6px}
.bars b{font:600 14px/1 Inter,sans-serif}
.bars i{display:block;width:100%;border-radius:4px 4px 0 0;background:#b9b9b9}
.bars img{width:18px;height:18px;object-fit:contain}
.bars i+img{margin-top:4px}
.win strong img{width:26px;height:26px;object-fit:contain;vertical-align:-4px;margin-right:10px}
.badge{display:inline-flex;align-items:center;gap:12px;align-self:flex-start;margin-top:28px;padding:12px 22px 12px 16px;
  border-radius:32px;font:400 15px/1 Inter,sans-serif;color:#4b587a;background:#f7f5f2;border:1px solid #e6e6e6;white-space:nowrap}
.badge b{font:700 20px/1 Inter,sans-serif;color:#0a1021}
.badge img{width:26px;height:26px}
.badge.on{background:#ebfffd;border-color:#73fff1;color:#00665c}
.badge.on b{color:#00332e}
.ranks{margin-top:28px;display:flex;flex-direction:column;gap:10px}
.ranks>span{font:500 16px/1 Inter,sans-serif;color:#4b587a;margin-bottom:4px}
.rk{display:grid;grid-template-columns:28px 28px minmax(0,1fr) auto;align-items:center;gap:12px;background:#fff;border:1px solid #e6e6e6;
  border-radius:16px;padding:14px 18px}
.rk em{font:600 18px/1 Inter,sans-serif;font-style:normal;color:#8994b1}
.rk img{width:28px;height:28px;object-fit:contain}
.rk div{min-width:0;font:700 20px/1.1 Inter,sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rk div small{display:block;margin-top:4px;font:400 14px/1 Inter,sans-serif;color:#636363}
.rk b{font:600 28px/1 Inter,sans-serif;letter-spacing:-.02em}
.rk b small{margin-left:3px;font:500 14px/1 Inter,sans-serif;color:#4b587a;letter-spacing:0}
.art{background:#fff;border:1px solid #e6e6e6;border-radius:24px;overflow:hidden}
.art img{display:block;width:100%;height:100%;object-fit:cover}
"""

BOARD_HTML = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<style>@font-face{{font-family:Domine;src:url("{root}language/assets/fonts/Domine-VariableFont_wght.ttf");font-weight:400 700}}
{css}</style></head><body><div class="bg"></div><div class="c">
<div class="top"><div class="meta"><b>{eyebrow}</b>{date}</div><img src="{root}language/assets/gooey-logo.png" alt=""></div>
<div class="l"><h1 style="--h:{size}px">{title}</h1>{lead}{badge}{ranks}<div class="stats">{stats}</div></div>
{right}
</div></body></html>"""


BOARD_KINDS = ("bars", "art")
BOARD_LEGEND = [["Sovereign", "#2a28ba"], ["Private", "#b9b9b9"]]


def board_html(card: dict, root: str) -> str:
    """ranks: {"label": str, "rows": [[logo file, name, score, note], ...]}, a numbered list under the title.
    badge: [label, "landmark" (sovereign, teal) or "cloud" (private, neutral)], under the title.
    visual "bars": {"bars": [[score, highlighted, model logo, speech logo], ...], "label": chart title,
    "legend": [[highlighted label, colour], [other label, colour]] (default sovereign / private)}; visual "art": {"src": image}."""
    v = card["visual"]
    # a stat is [label, value, unit, note] or [label, value, unit, note, icon file shown before the label]
    icon = lambda st: f'<img src="{root}{st[4]}" alt="">' if len(st) > 4 else ""
    stats = "".join(f'<div class="s"><span>{icon(st)}{esc(st[0])}</span><b>{esc(st[1])}{f"<small>{esc(st[2])}</small>" if st[2] else ""}</b>'
                    f'<i>{esc(st[3])}</i></div>' for st in card.get("stats", []))
    if v["kind"] == "bars":
        (on, on_c), (off, off_c) = v.get("legend", BOARD_LEGEND)
        cells = "".join(f'<div><b>{s}</b><i style="height:{s * 2.2:.0f}px;background:{on_c if hi else off_c}"></i>'
                        f'<img src="{root}{m}" alt=""><img src="{root}{a}" alt=""></div>' for s, hi, m, a in v["bars"])
        right = (f'<div class="r"><div class="rh"><h3>{esc(v.get("label", "Index"))}</h3><div class="lg">'
                 f'<span style="--c:{on_c}">{esc(on)}</span><span style="--c:{off_c}">{esc(off)}</span></div></div>'
                 f'<div class="bars" style="--n:{len(v["bars"])}">{cells}</div></div>')
    else:
        right = f'<div class="art"><img src="{root}{v["src"]}" alt=""></div>'
    logos = "".join(f'<img src="{root}{f}" alt="">' for f in card.get("lead_logos", []))
    lead = (f'<div class="win">{esc(card["lead"][0])}<strong>{logos}{esc(card["lead"][1])}</strong></div>'
            if card.get("lead") else "")
    badge = ""
    if card.get("badge"):
        label, icon = card["badge"]
        badge = (f'<div class="badge{" on" if icon == "landmark" else ""}"><img src="{root}language/assets/kinyarwanda/icon-{icon}.svg" alt="">'
                 f'<b>{esc(label)}</b></div>')
    ranks = ""
    if card.get("ranks"):
        rows = "".join(f'<div class="rk"><em>{n}</em><img src="{root}{logo}" alt=""><div>{esc(label)}'
                       f'{f"<small>{esc(note)}</small>" if note else ""}</div><b>{score}<small>/ 100</small></b></div>'
                       for n, (logo, label, score, note) in enumerate(card["ranks"]["rows"], 1))
        ranks = f'<div class="ranks"><span>{esc(card["ranks"]["label"])}</span>{rows}</div>'
    t = card["title"]
    return BOARD_HTML.format(badge=badge, ranks=ranks, root=root, css=BOARD_CSS, eyebrow=esc(card["eyebrow"]),
                             date=f" &nbsp;·&nbsp; {esc(card['date'])}" if card.get("date") else "",
                             size=60 if len(t) <= 20 else 52 if len(t) <= 26 else 44, title=esc(t), lead=lead, stats=stats,
                             right=right)


def card_html(card: dict, root: str) -> str:
    """The card as a standalone HTML page; root is the repo folder as a file:// URL ending in '/'."""
    if (card.get("visual") or {}).get("kind") in BOARD_KINDS:
        return board_html(card, root)
    v = card.get("visual")
    visual = ""
    if v:
        src = root + v.get("src", "")
        visual = {"photo": f'<img class="og__photo" src="{src}" alt="">',
                  "map": f'<img class="og__map" src="{src}" alt="">',
                  "logo": f'<div class="og__logo"><img src="{src}" alt=""></div>',
                  "banner": f'<img class="og__banner" src="{src}" alt="" style="object-position:{v.get("position", "center")}">',
                  }[v["kind"]]
    inner = ""
    if card.get("lead"):
        label, line = card["lead"]
        inner += f'<div class="og__lead"><span>{esc(label)}</span>{f"<b>{esc(line)}</b>" if line else ""}</div>'
    if card.get("stats"):
        cells = "".join(
            f'<div class="og__stat"><span>{esc(label)}</span><b>{esc(value)}{f"<small>{esc(unit)}</small>" if unit else ""}</b>'
            f'<i>{esc(note)}</i></div>' for label, value, unit, note in card["stats"])
        inner += f'<div class="og__stats" style="--n:{len(card["stats"])}">{cells}</div>'
    if card.get("people"):
        inner += '<div class="og__people">' + "".join(
            f'<div>{esc(n)}<span>{esc(a)}</span></div>' for n, a in card["people"]) + "</div>"
    p = card.get("paper")
    if p:
        marks = "".join(f'<img src="{root}{m}" alt="">' for m in p["marks"])
        inner += ((f'<img class="og__venue" src="{root}{p["logo"]}" alt="">' if p.get("logo") else "")
                  + f'<div class="og__ptitle">{esc(p["title"])}</div>'
                  + f'<div class="og__by"><span>{esc(p["byline"])}</span><div class="og__marks">{marks}</div></div>')
    w = card.get("wall")
    if w:
        inner += (f'<div class="og__lead"><span>{esc(w["label"])}</span></div>'
                  + '<div class="og__logos">' + "".join(f'<img src="{root}{f}" alt="">' for f in w["logos"]) + "</div>"
                  + f'<div class="og__by"><span>{esc(w["byline"])}</span><div class="og__marks">'
                  + "".join(f'<img src="{root}{m}" alt="">' for m in w["marks"]) + "</div></div>")
    kind = " og__paper" if p else " og__wall" if w else ""
    panel = f'<div class="og__panel{kind}">{inner}</div>' if inner else ""
    t = card["title"]
    return CARD_HTML.format(root=root, css=CARD_CSS, visual=visual, panel=panel, eyebrow=esc(card["eyebrow"]),
                            size=46 if len(t) <= 44 else 40, title=esc(t))


def og_image(path: str, card: dict, alt: str) -> tuple[str, str]:
    """Register a page's share card and return (image URL, alt text) for head()."""
    h = hashlib.sha1()
    board = (card.get("visual") or {}).get("kind") in BOARD_KINDS
    h.update((BOARD_CSS + BOARD_HTML).encode() if board else (CARD_CSS + CARD_HTML).encode())
    h.update(json.dumps(card, sort_keys=True, ensure_ascii=False).encode())
    v = card.get("visual") or {}
    files = ([WORDMARK] + ([v["src"]] if v.get("src") else []) + [f for b in v.get("bars", []) for f in b[2:]]
             + card.get("lead_logos", []) + [r[0] for r in (card.get("ranks") or {}).get("rows", [])] + [st[4] for st in card.get("stats", []) if len(st) > 4]
             + ([f"language/assets/kinyarwanda/icon-{card['badge'][1]}.svg"] if card.get("badge") else []))
    if card.get("paper"):
        files += ([card["paper"]["logo"]] if card["paper"].get("logo") else []) + card["paper"]["marks"]
    if card.get("wall"):
        files += card["wall"]["logos"] + card["wall"]["marks"]
    for f in files:
        h.update((ROOT / f).read_bytes())
    rel = f"{path.strip('/')}/og-{h.hexdigest()[:10]}.jpg"
    CARDS[ROOT / rel] = card
    return ASSETS + rel, alt
