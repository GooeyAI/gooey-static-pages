#!/usr/bin/env python3
"""Build the /language/<name>/index.html evaluation pages from one template.

    python3 scripts/build_language_pages.py              # rewrite every page
    python3 scripts/build_language_pages.py swahili      # just one
    python3 scripts/build_language_pages.py --check      # fail if a page is stale

Layout and behaviour live in two shared files that every page links to:

    language/assets/language-page.css
    language/assets/language-page.js

What is specific to one language lives in language/_src/<slug>/:

    page.json      names, hero voice note, chart geometry, axis ranges, notes
    picks.frag     "Which chain should you pick?" section (editorial); each card's link is href="{{run}}",
                   filled with that chain's saved workflow by pick_runs()
    featured.frag  featured lab / "what changed the result?" section (editorial)
    faq.json       verified dataset context for the shared, data-driven FAQ

The numbers come straight from the data files in language/data/<code>/
(summary CSV, pricing JSON, EcoCost JSON), so the chart, table, hero sentence
and hero "recommended chain" card can't disagree with the data. The page header is pasted in
from scripts/site_header.py, and the footer's language list from
language/_src/languages.json.

A second page type, /language/<name>/ai-agent, is built the same way from language/_src/agent.tmpl,
language/_src/<slug>/agent.json and the shared language/assets/language-agent.{css,js}. Everything on it
that is not wording (recommended chains, scores, costs, CO2e, FAQ numbers) is computed from the same data.

To add a language: copy language/_src/<existing>/ to a new folder, edit it,
drop the data files in language/data/<code>/, run this script, then run
scripts/check_language_pages.py and scripts/check_site_header.py.
"""

from __future__ import annotations

import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from site_header import HEADER_CSS, HEADER_HTML  # noqa: E402
from language_faq import PRICING_COMING_SOON, faq_items, render_faq  # noqa: E402
import seo  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANG = ROOT / "language"
SRC = LANG / "_src"
DATA = LANG / "data"

# A chain is sovereign-deployable when every step can run in the country: an open-weight
# language model plus a speech step that can be self-hosted. Override per page with
# "sovereign_models" / "sovereign_speech" in page.json.
SOVEREIGN_MODELS = {"DeepSeek V4", "Kimi K3"}
SOVEREIGN_SPEECH = {"Omnilingual", "Intron", "Kikuyu Whisper v2"}
DIRECT_AUDIO = "Built-in audio"
# Some summary CSVs abbreviate the speech step; the page always shows the full name.
SPEECH_ALIASES = {"Omni": "Omnilingual"}

# The page's own <base> comes before the GOOEY-BASE-HREF placeholder. Only the first <base> in a document counts, and
# gooey.ai's proxy replaces the placeholder with <base href="<Pages host>/<this page's folder>/">, which would send the
# relative paths below one or two folders too deep. With ours first, gooey.ai requests <path> on gooey.ai, which
# redirects to the Pages host (CORS allows the fetch of samples.json). It is root-absolute, not "../": gooey.ai
# serves a page both with and without its trailing slash, and "../" from /language/x (no slash) is the site root.
HEAD = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <base href="/language/" />
    <!-- GOOEY-BASE-HREF -->
{seo}    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    />
    <style>
{header_css}    </style>
    <link rel="stylesheet" href="assets/language-page.css" />
  </head>
  <body class="layout-{layout} hub">
"""

TAIL = """
    <script>
      window.LANG_PAGE = {config};
    </script>
    <script src="assets/language-samples.js"></script>
    <script src="assets/language-page.js"></script>
    <script src="assets/language-links.js"></script>
  </body>
</html>
"""


def norm(name: str) -> str:
    """Match workflow names across the CSV ("GPT 5.6 Sol") and the JSON files ("GPT-5.6 Sol (direct audio)")."""
    name = name.replace("(direct audio)", "").replace("-", " ")
    return re.sub(r"\s+", " ", name).strip().lower()


def chains_for(page: dict) -> tuple[list, list, list]:
    """Aggregate summary CSV + pricing + EcoCost into the arrays the shared script reads."""
    d = DATA / page["code"]
    snap = page["snapshot"]
    rows = []
    with open(d / f"summary-{snap}.csv", encoding="utf-8", newline="") as f:
        lines = [l for l in f if not l.startswith("#") and l.strip()]
    for r in csv.DictReader(lines):
        wf = r["Workflow"].strip()
        model, _, speech = wf.partition(" + ")
        speech = SPEECH_ALIASES.get(speech, speech)
        wf = f"{model} + {speech}" if speech else model
        rows.append((wf, model, speech or DIRECT_AUDIO, float(r["Accuracy (mean)"]), float(r["Latency (median)"])))

    price = {norm(w["workflow"]): w for w in json.loads((d / f"pricing-{snap}.json").read_text())["workflows"]}
    eco = {norm(w["workflow"]): w for w in json.loads((d / f"ecocost-{snap}.json").read_text())["workflows"]}

    models = set(page.get("sovereign_models", SOVEREIGN_MODELS))
    speech_ok = set(page.get("sovereign_speech", SOVEREIGN_SPEECH))
    csv_rows, pricing, ecocost = [], [], []
    for wf, model, speech, acc, time in rows:
        key = norm(wf)
        if key not in price or key not in eco:
            raise SystemExit(f"{page['slug']}: '{wf}' is in the summary CSV but missing from the pricing or EcoCost JSON")
        csv_rows.append([model, speech, acc, time, model in models and speech in speech_ok])
        pricing.append(round(price[key]["cost_usd_per_1000"], 4))
        e = eco[key]
        if e.get("coverage") == "text_model_only":
            v = e["co2e_g_per_1000"]
            ecocost.append({"value": round(v["value"], 4), "min": round(v["min"], 4), "max": round(v["max"], 4)})
        else:
            # The JSON carries a long explanation; the page shows its first clause, and names the
            # model when the JSON only says "this text model".
            reason = e["reason"].split(";")[0].rstrip(".") + "."
            reason = reason.replace("The public", f"The {e['source_run_count']} public").replace("this text model", model)
            ecocost.append({"reason": reason})
    return csv_rows, pricing, ecocost


# A language's evaluation link must be its own bulk run, never the generic gooey.ai/bulk/ page:
# ask the team for the specific run when adding or updating a language.
BULK_RE = re.compile(r"^https://gooey\.ai/bulk/[a-z0-9-]+/$")


def eval_url(page: dict) -> str:
    url = page["hero"]["bulk_url"]
    if not BULK_RE.match(url):
        raise SystemExit(f"{page['slug']}: hero.bulk_url must be this language's own evaluation run "
                         f"(https://gooey.ai/bulk/<run>/), not {url!r}. Ask the team for the specific run.")
    return url


def workflow_urls(page: dict, csv_rows: list) -> list[str]:
    """Each chain's saved Gooey.AI workflow (or, if it was retitled since, the evaluation's run of it), in
    csv_rows order, from data/<code>/workflows-<snapshot>.json (scripts/fetch_language_workflows.py)."""
    path = DATA / page["code"] / f"workflows-{page['snapshot']}.json"
    if not path.exists():
        raise SystemExit(f"{page['slug']}: {path.relative_to(ROOT)} is missing; "
                         f"run python3 scripts/fetch_language_workflows.py {page['slug']}")
    key = lambda model, speech: norm(model if speech in ("", DIRECT_AUDIO) else f"{model} + {SPEECH_ALIASES.get(speech, speech)}")
    urls = {}
    for w in json.loads(path.read_text())["workflows"]:
        name = re.sub(r"^\d+\s+", "", w["tested_as"])
        name = re.sub(r"\s+-\s+" + re.escape(page["lang"]) + r"$", "", name)
        model, _, speech = name.partition(" + ")
        # A workflow edited after the evaluation may now run another model: link the evaluation's own run.
        urls[key(model.strip(), speech.strip())] = w["eval_run"] if w["retitled"] else w["url"]
    out = []
    for model, speech, *_ in csv_rows:
        if key(model, speech) not in urls:
            raise SystemExit(f"{page['slug']}: no saved workflow for '{model} + {speech}' in {path.relative_to(ROOT)}")
        out.append(urls[key(model, speech)])
    return out


def pick_runs(frag: str, page: dict, csv_rows: list) -> str:
    """Fill each pick card's href="{{run}}" with the saved workflow of the chain the card names (the same link the
    chains table uses), read from the card's own model and speech labels."""
    runs = dict(zip(((norm(r[0]), r[1]) for r in csv_rows), workflow_urls(page, csv_rows)))

    def card(m: re.Match) -> str:
        names = re.findall(r"<span>([^<]+)</span>", m.group(1))
        direct = 'class="dir"' in m.group(1)
        model, speech = names[0], (DIRECT_AUDIO if direct else names[1])
        hit = [u for (mo, sp), u in runs.items()
               if mo == norm(model) and norm(SPEECH_ALIASES.get(sp, sp) if sp else DIRECT_AUDIO) == norm(speech)]
        if len(hit) != 1:
            raise SystemExit(f"{page['slug']}: picks.frag card '{model} + {speech}' matches {len(hit)} evaluated chains")
        if 'href="{{run}}"' not in m.group(0):
            raise SystemExit(f"{page['slug']}: picks.frag card '{model} + {speech}' must link href=\"{{{{run}}}}\"")
        return m.group(0).replace('href="{{run}}"', f'href="{hit[0]}"')

    return re.sub(r'<article class="pick-card">\s*(<div class="chain">.*?</div>).*?</article>', card, frag, flags=re.S)


def archive_for(page: dict) -> list:
    """Older evaluations for the date menu: the Index and response time only (cost and CO2e were not recorded)."""
    out = []
    for a in page.get("archive", []):
        with open(DATA / page["code"] / f"summary-{a['snapshot']}.csv", encoding="utf-8", newline="") as f:
            lines = [l for l in f if not l.startswith("#") and l.strip()]
        rows = []
        for r in csv.DictReader(lines):
            model, _, speech = r["Workflow"].strip().partition(" + ")
            rows.append([model, speech or DIRECT_AUDIO, float(r["Accuracy (mean)"]), float(r["Latency (median)"]), False])
        out.append({"id": a["snapshot"], "label": a["label"], "csv": rows, "x": a["x"], "xTicks": a["xTicks"],
                    "score": a["score"], "note": a["note"]})
    return out


def language_list(current: str, href=None) -> str:
    """The footer's other-languages list. `href(slug)` gives the link for a language that has a page; a language
    without one (or no `href`) is plain text."""
    cfg = json.loads((SRC / "languages.json").read_text())
    slug_of = {json.loads(p.read_text())["lang"]: p.parent.name for p in SRC.glob("*/page.json")}
    def item(n: str) -> str:
        link = href(slug_of[n]) if href and n in slug_of else None
        return f'<li><a href="{link}">{n}</a></li>' if link else f"<li>{n}</li>"
    items = "".join(item(n) for n in cfg["languages"] if n != current)
    return (f'<ul class="language-list" aria-label="Other Gooey.AI languages">{items}'
            f'<li><strong>{cfg["all"]}</strong></li></ul>')


def ordinal_date(snapshot: str) -> str:
    """"2026-08-30" -> "30th Aug, 2026" (the hero sentence's date)."""
    y, m, d = (int(x) for x in snapshot.split("-"))
    suffix = "th" if 11 <= d % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m - 1]
    return f"{d}{suffix} {month}, {y}"


def hero_top(page: dict, csv_rows: list, pricing: list, ecocost: list) -> tuple[str, str]:
    """The hero sentence and the recommended-chain card, both about the chain with the highest Index."""
    lang, slug = page["lang"], page["slug"]
    i = min(range(len(csv_rows)), key=lambda k: (-csv_rows[k][2], csv_rows[k][3]))
    model, speech, acc, time, sov = csv_rows[i]
    model = model.replace("GPT 5.6 Sol", "GPT-5.6 Sol")
    direct = speech == DIRECT_AUDIO
    pairing = ", listening to the audio directly," if direct else f" language model paired with <strong>{speech}</strong> ASR"
    lead = (f"Our latest {lang} Index eval conducted on <strong>{ordinal_date(page['snapshot'])}</strong> found that "
            f"{'' if direct else 'the '}<strong>{model}</strong>{pairing} scored the <strong>highest Index</strong> "
            "on answers to questions asked by native speakers.")

    icon = lambda name, size: f'<img src="assets/kinyarwanda/{name}.svg" alt="" width="{size}" height="{size}" />'
    logos = icon(logo24(model), 24)
    if not direct:
        stem = js_dict("SPEECH_FILES")[speech]
        stem = f"{stem}-24" if (LANG / "assets" / "kinyarwanda" / f"{stem}-24.svg").exists() else stem
        logos += icon(stem, 24)
    name = f"{model} (direct audio)" if direct else f"{model} + {speech}"
    eco = ecocost[i]
    eco_metric = ""
    if "value" in eco:
        lowest = eco["value"] <= min(e["value"] for e in ecocost if "value" in e)
        eco_metric = (f'<div class="rec-metric">{icon("icon-leaf", 16)}<b>{eco["value"]:.1f} g</b><span>CO₂e</span>'
                      f'<small class="good">per 1,000 questions{", lowest" if lowest else ""}</small></div>')
    card = f"""<div class="rec-card">
                <div class="rec-chain">
                  <span class="rec-logos">{logos}</span>
                  <div class="rec-name"><strong>{name}</strong><span>{"Most accurate · Sovereign" if sov else "Most accurate · Private API"}</span></div>
                </div>
                <div class="rec-metrics">
                  <div class="rec-metric">{icon("icon-bullseye", 16)}<b>{round(acc * 100 + 1e-9)}</b><span>/ 100</span><small>{lang} Index</small></div>
                  {eco_metric}
                  <i class="rec-divider" aria-hidden="true"></i>
                  <div class="rec-more">
                    <span>{icon("icon-stopwatch", 14)}<b>{time:.1f} s</b> median reply</span>
                    <span{ ' class="pricing-pending"' if PRICING_COMING_SOON else '' }>{icon("icon-dollar", 14)}<b>{"Coming soon" if PRICING_COMING_SOON else money(pricing[i]) + " / 1,000"}</b> {"pricing" if PRICING_COMING_SOON else "questions"}</span>
                  </div>
                </div>
                <div class="top-actions">
                  <a class="hero-btn primary" href="https://gooey.ai/agent/" target="_blank" rel="noopener noreferrer">Build a {lang} agent</a>
                  <a class="hero-btn secondary" href="{page["hero"]["bulk_url"]}" target="_blank" rel="noopener noreferrer">View the {lang} AI evaluation<img src="assets/kinyarwanda/icon-arrow-ur.svg" alt="" width="12" height="12" /></a>
                </div>
              </div>"""
    return lead, card


AUDIO_RE = re.compile(r"\.(wav|mp3|m4a|opus|ogg)(\?|$)", re.I)


def hero_question(page: dict) -> int:
    """The question the hero voice note plays: evaluation row 1 when its recording is a direct audio file and it
    has its text, otherwise the first sample card."""
    with (DATA / page["code"] / "evaluation-latest.csv").open(encoding="utf-8-sig") as f:
        row = next(csv.DictReader(f))
    target = row.get("Prompt_Target") or row.get("Question_Target") or ""
    source = row.get("question") or row.get("Prompt_Source") or row.get("Question_Source") or ""
    if AUDIO_RE.search(row.get("input_audio", "")) and target and source:
        return 1
    return json.loads((DATA / page["code"] / "samples.json").read_text())["samples"][0]["questionNumber"]


def voice_note(page: dict) -> str:
    """The hero voice note (language/_src/voice-note.frag), shared by the language and speech-to-text pages."""
    html = (SRC / "voice-note.frag").read_text().rstrip("\n")
    for key, value in {"lang": page["lang"], **{f"vn_{k}": v for k, v in hero_voice(page).items()}}.items():
        html = html.replace("{{%s}}" % key, value)
    return html


def hero_voice(page: dict) -> dict:
    """The hero voice note plays a real question from the evaluation: the first evaluation row when its
    recording is a direct audio file, otherwise the first sample card (whose audio is stored with the data)."""
    d = DATA / page["code"]
    esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    with (d / "evaluation-latest.csv").open(encoding="utf-8-sig") as f:
        row = next(csv.DictReader(f))
    audio = row.get("input_audio", "")
    target = row.get("Prompt_Target") or row.get("Question_Target") or ""
    source = row.get("question") or row.get("Prompt_Source") or row.get("Question_Source") or ""
    if AUDIO_RE.search(audio) and target and source:
        return {"audio": esc(audio), "text": esc(target.strip()), "sub": esc(source.strip()), "time": ""}
    first = json.loads((d / "samples.json").read_text())["samples"][0]
    secs = round(first["audioDurationSeconds"])
    return {"audio": esc(first["audioUrl"]), "text": esc(first["transcript"]), "sub": esc(first["questionEnglish"]),
            "time": f"{secs // 60}:{secs % 60:02d}"}


def render(slug: str) -> str:
    d = SRC / slug
    page = json.loads((d / "page.json").read_text())
    eval_url(page)
    csv_rows, pricing, ecocost = chains_for(page)
    n = len(csv_rows)
    n_sov = sum(1 for r in csv_rows if r[4])
    metrics = page["scatter"]["metrics"]

    config = {
        "lang": page["lang"], "dataDir": f"data/{page['code']}", "layout": page["layout"],
        "questions": page["questions"], "csv": csv_rows, "pricing": pricing, "eco": ecocost,
        "pricingComingSoon": PRICING_COMING_SOON,
        "geometry": page["geometry"],
        "scatter": {k: page["scatter"][k] for k in ("x", "xTicks", "labelBestSovereign", "metrics")},
        "archive": archive_for(page),
        "sample": page["sample"], "labSpeech": page.get("labSpeech"), "labSpeechShort": page.get("labSpeechShort"), "slug": slug, "workflows": workflow_urls(page, csv_rows),
        "modelSlugs": {m: v["slug"] for m, v in json.loads((SRC / "models.json").read_text()).items()},
    }

    hero = page["hero"]
    pin = '\n            <i class="map-pin" aria-hidden="true"></i>' if hero["map"].get("pin") else ""
    map_img = f'<img src="assets/kinyarwanda/{hero["map"]["file"]}" alt="" width="273" height="252" />{pin}'
    speech_key = "\n              ".join(
        f'<span><img src="assets/kinyarwanda/{icon}.svg" alt="" width="16" height="16" />{name}</span>'
        for name, icon in page["board"]["speech_key"]
    )
    models_meta = json.loads((SRC / "models.json").read_text())
    ranked_models = []
    for row in sorted(csv_rows, key=lambda r: (-r[2], r[3])):
        name = row[0].replace("GPT 5.6 Sol", "GPT-5.6 Sol")
        if name not in ranked_models:
            ranked_models.append(name)
    model_nav = ('<nav class="sr-only" aria-label="Results by model">' + " ".join(
        f'<a href="../models/{models_meta[m]["slug"]}/{slug}/">{m} in {page["lang"]}</a>' for m in ranked_models) + "</nav>")
    lead_html, rec_card = hero_top(page, csv_rows, pricing, ecocost)
    faq_context = json.loads((d / "faq.json").read_text()) if (d / "faq.json").exists() else {}
    data_dir = DATA / page["code"]
    faq = render_faq((SRC / "faq.tmpl").read_text(), faq_items(
        page, csv_rows,
        json.loads((data_dir / f"pricing-{page['snapshot']}.json").read_text()),
        json.loads((data_dir / f"ecocost-{page['snapshot']}.json").read_text()),
        faq_context, models_meta,
    ))

    slots = {
        "header": HEADER_HTML.format(title=f"Best AI for {page['lang']}").rstrip("\n"),
        "lang": page["lang"], "flag": page["flag"], "endonym": page["endonym"], "country": page["country"],
        "updated": page["updated"], "lead_html": lead_html, "rec_card": rec_card, "bulk_url": hero["bulk_url"],
        "map_alt": hero["map"]["alt"], "map_img": map_img, "map_key": hero["map"]["file"].rsplit(".", 1)[0].removeprefix("map-"),
        "voice_note": voice_note(page),
        "n": str(n), "n_sov": str(n_sov), "n_priv": str(n - n_sov), "questions": str(page["questions"]),
        "board_hint": page["board"]["hint"], "speech_key": speech_key,
        "picks_section": pick_runs((d / "picks.frag").read_text().rstrip("\n"), page, csv_rows),
        "featured_section": (d / "featured.frag").read_text().rstrip("\n"),
        "faq_section": faq,
        "scatter_aria": " " + page["scatter"]["aria"],
        "score_front": metrics["score"]["front"], "score_note": metrics["score"]["note"],
        "model_nav": model_nav, "samples_intro": page["samples_intro"],
        "language_list": language_list(page["lang"], lambda s: f"{s}/"), "slug": slug,
        "speech_card": speech_card(slug, page["lang"]),
    }
    body = (SRC / "body.tmpl").read_text()
    for key, value in slots.items():
        body = body.replace("{{%s}}" % key, value)
    left = re.findall(r"\{\{\w+\}\}", body)
    if left:
        raise SystemExit(f"{slug}: unfilled template slots {sorted(set(left))}")

    head = HEAD.format(layout=page["layout"], header_css=HEADER_CSS, seo=hub_seo(page, csv_rows, body))
    cfg_json = json.dumps(config, ensure_ascii=False, separators=(", ", ": "))
    return head + body.rstrip("\n") + "\n" + TAIL.format(config=cfg_json)


def hub_seo(page: dict, csv_rows: list, body: str) -> str:
    """Search and sharing tags for /language/<slug>: share card, WebPage, Dataset, breadcrumbs and FAQ."""
    lang, q, n, path = page["lang"], page["questions"], len(csv_rows), f"language/{page['slug']}"
    i = min(range(n), key=lambda k: (-csv_rows[k][2], csv_rows[k][3]))
    model, speech, acc, time, _ = csv_rows[i]
    top, score = chain_label({"model": model.replace("GPT 5.6 Sol", "GPT-5.6 Sol"), "speech": speech}), round(acc * 100 + 1e-9)
    title = f"Best AI for {lang}"
    image = seo.og_image(path, {
        "eyebrow": f"AI evaluation · {page['country']}", "title": title, "lead": ["Highest score", top],
        "stats": [[f"{lang} Index", str(score), "/ 100", f"highest of {n} chains"], ["Reply time", f"{time:.1f}", "s", "median"],
                  ["Questions", str(q), "", "asked by native speakers"]],
        "visual": {"kind": "map", "src": f"language/assets/kinyarwanda/{page['hero']['map']['file']}"},
    }, f"{title}: {top} scored {score} out of 100, the highest of {n} AI chains tested on {q} spoken {lang} questions.")
    dataset = {
        "@type": "Dataset", "@id": seo.url(path) + "#dataset", "name": f"{lang} AI evaluation, {page['updated']}",
        "description": (f"Questions, reference answers, scores and run links for {n} AI chains answering {q} spoken {lang} "
                        f"questions, from the Gooey.AI {lang} evaluation."),
        "url": seo.url(path), "creator": {"@id": seo.ORG["@id"]}, "publisher": {"@id": seo.ORG["@id"]},
        "dateModified": page["snapshot"], "isAccessibleForFree": True,
        "variableMeasured": [f"{lang} Index", "Median response time (seconds)"],
        "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv",
                          "contentUrl": f"{seo.ASSETS}language/data/{page['code']}/evaluation-latest.csv"}],
    }
    seo_title = seo.fit(f"{title}: {page['snapshot'][:4]} Voice AI Benchmark{seo.BRAND}",
                        f"{title}: Voice AI Benchmark{seo.BRAND}", f"{title}{seo.BRAND}", hi=seo.TITLE_MAX, what="title")
    sentence = (f"Compare {lang} AI models for voice calls and WhatsApp by accuracy, response time, cost, "
                "and sovereign deployment options.")
    description = seo.fit(f"{sentence} Tested on {q} spoken questions.", sentence,
                          f"Compare {lang} AI models by accuracy, response time, cost and sovereign deployment. Tested on {q} spoken questions.",
                          lo=seo.DESC_MIN, hi=seo.DESC_MAX, what=f"{lang} description")
    graph = [seo.ORG, seo.webpage(path, seo_title, description, image, page["snapshot"], seo.language(lang, page.get("endonym"))),
             dataset, seo.breadcrumbs(path, [("Home", seo.SITE), seo.EVALS, (lang, None)]), *seo.faq(path, body)]
    return seo.head(path=path, title=seo_title, description=description, og_title=seo_title.removesuffix(seo.BRAND),
                    image=image, graph=graph)


def sub_seo(page: dict, path: str, titles: list[str], descriptions: list[str], card: dict, alt: str, body: str,
            crumb: str) -> str:
    """Search and sharing tags for a page under /language/<slug>/ (ai-agent, speech-to-text). titles and descriptions
    are wordings from fullest to shortest; the first that fits Google's limits is used."""
    lang = page["lang"]
    title = seo.fit(*titles, hi=seo.TITLE_MAX, what=f"{path} title")
    description = seo.fit(*descriptions, lo=seo.DESC_MIN, hi=seo.DESC_MAX, what=f"{path} description")
    image = seo.og_image(path, card, alt)
    graph = [seo.ORG, seo.webpage(path, title, description, image, page["snapshot"], seo.language(lang, page.get("endonym"))),
             seo.breadcrumbs(path, [("Home", seo.SITE), seo.EVALS, (lang, seo.url(f"language/{page['slug']}")), (crumb, None)]),
             *seo.faq(path, body)]
    return seo.head(path=path, title=title, description=description, og_title=title.removesuffix(seo.BRAND),
                    image=image, graph=graph)


def speech_card(slug: str, lang: str) -> str:
    """The "More for <language>" Speech to text card: a link once the language has a speech-to-text page."""
    inner = ('<img class="more-art" src="assets/more/speech-to-text.png" alt="" width="800" height="600" loading="lazy" />\n'
             '              <div class="more-body"><div class="more-h"><span class="more-title"><img src="assets/kinyarwanda/icon-microphone.svg" alt="" width="16" height="16" />Speech to text</span>{arrow}</div><p>{sub}</p></div>')
    if (SRC / slug / "stt.json").exists():
        arrow = '<img src="assets/kinyarwanda/icon-arrow-right.svg" alt="" width="16" height="16" />'
        return (f'<a class="more-card" href="{slug}/speech-to-text/">\n              '
                + inner.format(arrow=arrow, sub=f"Transcribe {lang} audio") + "\n            </a>")
    return ('<article class="more-card disabled">\n              ' + inner.format(arrow="", sub="Results coming soon")
            + "\n            </article>")


def slugs() -> list[str]:
    return sorted(p.parent.name for p in SRC.glob("*/page.json"))


# ---------------------------------------------------------------------------------------------------------
# /language/<name>/ai-agent

AGENT_HEAD = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <base href="/language/" />
    <!-- GOOEY-BASE-HREF -->
{seo}    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    />
    <style>
{header_css}    </style>
    <link rel="stylesheet" href="assets/language-page.css" />
    <link rel="stylesheet" href="assets/language-agent.css" />
  </head>
  <body>
"""

AGENT_TAIL = """
    <script>
      window.AGENT_PAGE = {config};
    </script>
    <script src="assets/language-agent.js"></script>
    <script src="assets/language-links.js"></script>
  </body>
</html>
"""

CHECK_SVG = ('<svg class="ag-check" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3.5 8.5 3 3 6-7"/></svg>')
FILE_SVG = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><rect x="5" y="5" width="8" height="8.5" rx="1.5"/>'
            '<path d="M3.5 10.5V3.8c0-.7.6-1.3 1.3-1.3H10"/></svg>')
ART = {  # slot -> (file stem, alt text); an image is used when language/assets/ai-agent/<stem>.<ext> exists
    "hero": ("hero", "Hands holding a phone that shows a confirmation tick, in front of a shop counter", 485),
    "channel": ("channel", "Hands holding a phone with a voice note and a text message", 380),
}
NUMBER_WORDS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve"]


def js_dict(name: str) -> dict:
    """A `const NAME = { "key": "value", ... };` object literal from the shared page script."""
    text = (LANG / "assets" / "language-page.js").read_text(encoding="utf-8")
    m = re.search(r"const %s = \{(.*?)\};" % name, text, re.S)
    return {(a or b): c for a, b, c in re.findall(r'(?:"([^"]+)"|(\w+))\s*:\s*"([^"]*)"', m.group(1))}


def logo24(model: str) -> str:
    stem = js_dict("LOGO_FILES")[model]
    return f"{stem}-24" if (LANG / "assets" / "kinyarwanda" / f"{stem}-24.svg").exists() else stem


def art(slot: str) -> str:
    stem, alt, height = ART[slot]
    for ext in ("webp", "jpg", "png"):
        if (LANG / "assets" / "ai-agent" / f"{stem}.{ext}").exists():
            return f'<img class="ag-art" src="assets/ai-agent/{stem}.{ext}" alt="{alt}" width="984" height="{height}" />'
    return f'<div class="ag-art ag-art-placeholder" role="img" aria-label="{alt}">Illustration to come</div>'


def chain_label(c: dict) -> str:
    return c["model"] + (" + built-in audio" if c["speech"] == DIRECT_AUDIO else f" + {c['speech']}")


def money(v: float) -> str:
    return f"${v:,.0f}" if v >= 1000 else f"${v:.2f}"


def amount(v: float, unit: str) -> str:
    digits = 0 if v >= 100 else 1 if v >= 10 else 2
    return f"{round(v, digits):,} {unit}"


def agent_facts(a: dict) -> dict:
    csv_rows, pricing, ecocost = chains_for(a)
    d = DATA / a["code"]
    eco_json = {norm(w["workflow"]): w for w in json.loads((d / f"ecocost-{a['snapshot']}.json").read_text())["workflows"]}
    chains = []
    for (model, speech, acc, time, sov), cost, eco in zip(csv_rows, pricing, ecocost):
        model = model.replace("GPT 5.6 Sol", "GPT-5.6 Sol")
        key = norm(model + ("" if speech == DIRECT_AUDIO else f" + {speech}"))
        chains.append({"model": model, "speech": speech, "acc": acc, "score": round(acc * 100 + 1e-9), "time": time,
                       "sov": sov, "cost": cost, "eco": eco, "eco_full": eco_json[key]})
    order = sorted(chains, key=lambda c: (-c["acc"], c["time"]))
    median = sorted(c["score"] for c in chains)[len(chains) // 2]
    top = order[0]
    # Best trade-off: the most accurate of the faster half of the chains (the top chain aside).
    median_time = sorted(c["time"] for c in chains)[len(chains) // 2]
    trade = max((c for c in chains if c["time"] <= median_time and c is not top), key=lambda c: (c["acc"], -c["time"]))
    picks = [(top, "Most accurate"), (trade, "Best trade-off")]
    taken = lambda c: any(c is p for p, _ in picks)
    # Third pick: the best self-hostable chain when the top one isn't (and it isn't already picked); otherwise the best
    # direct-audio chain, otherwise the best chain from a model not yet picked.
    third, tag = None, ""
    if not top["sov"]:
        host = next((c for c in order if c["sov"]), None)  # only if the best self-hostable chain isn't already listed
        third = host if host and not taken(host) else None
        tag = "Best self-hostable"
    if third is None:
        third = next((c for c in order if c["speech"] == DIRECT_AUDIO and not taken(c)), None)
        tag = "Special mention"
    if third is None:
        third = next((c for c in order if c["model"] not in {p["model"] for p, _ in picks}), None)
        tag = "Also strong"
    if third:
        picks.append((third, tag))
    return {"chains": chains, "order": order, "top": top, "picks": picks, "median": median,
            "fast": [c for c in chains if c["time"] < 10]}


def agent_faq(a: dict, f: dict) -> str:
    chains, top, fast = f["chains"], f["top"], f["fast"]
    n, lang = len(chains), a["lang"]
    fastest = min(chains, key=lambda c: c["time"])
    if fast:
        count = NUMBER_WORDS[len(fast)] if len(fast) < len(NUMBER_WORDS) else str(len(fast))
        phone = (f"Yes. {count} of the {n} chains we tested answer in under 10 s, fast enough for calls. "
                 "Connect a number in step 3.")
    else:
        phone = (f"Not yet. None of the {n} chains we tested answered in under 10 s, which calls need; the fastest takes "
                 f"{fastest['time']:.1f} s ({chain_label(fastest)}). Use WhatsApp or the web for now, and test a phone line before launch.")
    costs = [c["cost"] for c in chains]
    if max(costs) - min(costs) < 0.005:
        price = (f"Every chain we tested was charged {money(costs[0])} per 1,000 runs on Gooey.AI, about "
                 f"{money(costs[0] / 1000)} a run. The calculator above scales that to your volume.")
    else:
        price = (f"On Gooey.AI the observed charge was {money(min(costs))} to {money(max(costs))} per 1,000 {lang} runs, "
                 "depending on the chain. The calculator above scales it to your volume.")
    sov = [chain_label(c) for c in f["order"] if c["sov"]]
    joined = ", ".join(sov[:-1]) + " and " + sov[-1] if len(sov) > 1 else (sov[0] if sov else "")
    data = (f"Yes, with a sovereign-deployable chain: {joined} can run in {a['country']} or on your own servers. "
            "Other chains use a private API, which sends audio to its maker’s cloud. Hosting types are still being confirmed."
            if sov else f"Not with the chains we tested: all of them use a private API that sends audio to its maker’s cloud.")
    qa = [(f"Which AI should my {lang} agent use?",
           f"Start with {chain_label(top)}: it scored highest on real {lang} questions ({top['score']} out of 100) and answers in a "
           f"median {top['time']:.1f} s. You can switch chains later without rebuilding."),
          ("Can it work on a phone line?", phone), ("What does it cost to run?", price),
          (f"Can I keep data in {a['country']}?", data)]
    return "\n".join(f"            <details{' open' if i < 2 else ''}><summary>{q}</summary><p>{ans}</p></details>"
                     for i, (q, ans) in enumerate(qa))


def render_agent(slug: str) -> str:
    a = json.loads((SRC / slug / "agent.json").read_text())
    f = agent_facts(a)
    lang, top = a["lang"], f["top"]
    logos = js_dict("LOGO_FILES")
    for m in sorted({*a["models"], *(c["model"] for c in f["chains"])}):
        if m not in logos:
            raise SystemExit(f"{slug} ai-agent: model {m!r} has no logo; add it to LOGO_FILES in language/assets/language-page.js")

    chain_rows = []
    for i, (c, tag) in enumerate(f["picks"]):
        sel = " selected" if i == 0 else ""
        chain_rows.append(
            f'                <li><button class="ag-chain{sel}" type="button" data-model="{c["model"]}" aria-pressed="{str(i == 0).lower()}">'
            f'<img src="assets/kinyarwanda/{logo24(c["model"])}.svg" alt="" width="24" height="24" />'
            f'<span class="ag-chain-text"><b>{chain_label(c)}</b><small>{tag} · score {c["score"]} · {c["time"]:.1f} s</small></span>'
            f"{CHECK_SVG}</button></li>")

    model_rows = []
    in_data = sorted({c["model"] for c in f["chains"]}, key=lambda m: -max(c["acc"] for c in f["chains"] if c["model"] == m))
    for m in [*a["models"], *[m for m in in_data if m not in a["models"]]]:
        # the picker shows each model's best chain, so a model's score is never understated
        c = max((x for x in f["chains"] if x["model"] == m), key=lambda x: (x["acc"], -x["time"]))
        sel = " selected" if m == top["model"] else ""
        model_rows.append(
            f'                  <li><button class="ag-model{sel}" type="button" data-model="{m}" aria-pressed="{str(bool(sel)).lower()}">'
            f'<img src="assets/kinyarwanda/{logo24(m)}.svg" alt="" width="24" height="24" />'
            f'<span><b>{m}</b><small>Score {c["score"]} · {c["time"]:.1f} s · Global</small></span>{CHECK_SVG}</button></li>')

    file_rows = "\n".join(
        f'                  <li class="ag-file">{FILE_SVG}<span><b>{n}</b><small>{sub}</small></span>{CHECK_SVG}</li>'
        for n, sub in a["knowledge"])

    n_fast, n = len(f["fast"]), len(f["chains"])
    channels = {
        "whatsapp": f"Connect your WhatsApp Business number. Users send voice notes or text and get answers back in {lang}.",
        "phone": (f"Connect a phone number. Callers speak {lang} and hear spoken answers. Calls need a reply in under 10 s, "
                  + (f"which {n_fast} of the {n} chains we tested achieve." if n_fast else
                     f"and none of the {n} chains we tested manages that yet, so test before you launch.")),
        "web": f"Add the agent to your website as a chat widget. Visitors type or speak {lang} and read or hear the answer.",
    }

    full = top["eco_full"]
    per = None
    if full.get("coverage") == "text_model_only":
        per = {"co2e": full["co2e_g_per_1000"]["value"], "waterL": full["water_ml_per_1000"] / 1000,
               "energyKwh": full["energy_wh_per_1000"] / 1000}
    config = {"perThousand": {"cost": top["cost"], "co2e": per and per["co2e"], "waterL": per and per["waterL"],
                              "energyKwh": per and per["energyKwh"]}, "channels": channels}

    slots = {
        "header": HEADER_HTML.format(title=f"Build a {lang} AI agent").rstrip("\n"),
        "slug": slug, "lang": lang, "art_hero": art("hero"), "art_channel": art("channel"),
        "chain_rows": "\n".join(chain_rows), "model_rows": "\n".join(model_rows), "file_rows": file_rows,
        "channel_whatsapp": channels["whatsapp"],
        "top_label": chain_label(top), "top_logo": logos[top["model"]], "top_cost": money(top["cost"]),
        "top_co2e": "Not covered" if not per else (f"{per['co2e']:.0f} g"),
        "top_co2e_line": "CO2e not covered" if not per else f"About {per['co2e']:.0f} g CO2e",
        "top_water": "Not covered" if not per else amount(per["waterL"], "L"),
        "top_energy": "Not covered" if not per else amount(per["energyKwh"], "kWh"),
        "faq_items": agent_faq(a, f), "language_list": language_list(lang, lambda s: f"{s}/ai-agent/"),
    }
    body = (SRC / "agent.tmpl").read_text()
    for key, value in slots.items():
        body = body.replace("{{%s}}" % key, value)
    left = re.findall(r"\{\{\w+\}\}", body)
    if left:
        raise SystemExit(f"{slug} ai-agent: unfilled template slots {sorted(set(left))}")
    launch = f"Launch a {lang} AI agent on WhatsApp, phone calls or the web, built on the most accurate AI in our tests"
    descriptions = [f"{launch}: {chain_label(top)} ({top['score']}/100).", f"{launch} ({top['score']}/100).",
                    f"Launch a {lang} AI agent on WhatsApp, phone calls or the web with {chain_label(top)}, "
                    f"the most accurate AI in our tests."]
    page = json.loads((SRC / slug / "page.json").read_text())
    title = f"Build a {lang} AI agent"
    card = {"eyebrow": f"AI agent · {a['country']}", "title": title, "lead": ["Recommended chain", chain_label(top)],
            "stats": [[f"{lang} Index", str(top["score"]), "/ 100", "most accurate tested"],
                      ["Reply time", f"{top['time']:.1f}", "s", "median, phone-ready" if top["time"] < 10 else "median"],
                      ["Channels", "3", "", "WhatsApp, phone, web"]],
            "visual": {"kind": "photo", "src": "language/assets/more/ai-agent.png"}}
    alt = (f"{title}: {chain_label(top)}, the most accurate chain tested, scored {top['score']} out of 100 "
           f"with a {top['time']:.1f} s median reply.")
    titles = [f"Build a {lang} AI Agent for WhatsApp & Phone{seo.BRAND}", f"Build a {lang} AI Agent{seo.BRAND}"]
    seo_tags = sub_seo(page, f"language/{slug}/ai-agent", titles, descriptions, card, alt, body, "AI agent")
    head = AGENT_HEAD.format(lang=lang, header_css=HEADER_CSS, seo=seo_tags)
    cfg = json.dumps(config, ensure_ascii=False, separators=(", ", ": "))
    return head + body.rstrip("\n") + "\n" + AGENT_TAIL.format(config=cfg)


def agent_slugs() -> list[str]:
    return sorted(p.parent.name for p in SRC.glob("*/agent.json"))


STT_HEAD = AGENT_HEAD.replace(
    '<link rel="stylesheet" href="assets/language-agent.css" />',
    '<link rel="stylesheet" href="assets/language-agent.css" />\n    <link rel="stylesheet" href="assets/language-stt.css" />')

STT_TAIL = """
    <script>
      window.STT_PAGE = {config};
    </script>
    <script src="assets/language-samples.js"></script>
    <script src="assets/language-stt.js"></script>
    <script src="assets/language-links.js"></script>
  </body>
</html>
"""

COPY_SVG = ('<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4" '
            'stroke-linejoin="round" aria-hidden="true"><rect x="5.5" y="5.5" width="8" height="8" rx="1.5"/>'
            '<path d="M10.5 3.5V3A1.5 1.5 0 0 0 9 1.5H3A1.5 1.5 0 0 0 1.5 3v6A1.5 1.5 0 0 0 3 10.5h.5"/></svg>')
CHECK_12 = ('<svg viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.4" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m2.5 6.5 2.2 2.2 4.8-5.4"/></svg>')
# The step-1 illustration: language/assets/speech-to-text/step1.{webp,jpg,png}, 1024 x 768 (4:3, the Figma slot's shape).
STT_ART = ("step1", "A hand holding a phone that turns a spoken voice note into text, outside a health clinic", (1024, 768))


def stt_art() -> str:
    stem, alt, size = STT_ART
    for ext in ("webp", "jpg", "png"):
        if (LANG / "assets" / "speech-to-text" / f"{stem}.{ext}").exists():
            return f'<img class="ag-art" src="assets/speech-to-text/{stem}.{ext}" alt="{alt}" width="{size[0]}" height="{size[1]}" />'
    return f'<div class="ag-art ag-art-placeholder" role="img" aria-label="{alt}">Illustration to come</div>'


def stt_art_file() -> str:
    """The speech-to-text illustration for the share card: step 1's picture, or the "More for" card's until it exists."""
    stem = STT_ART[0]
    for ext in ("webp", "jpg", "png"):
        if (LANG / "assets" / "speech-to-text" / f"{stem}.{ext}").exists():
            return f"language/assets/speech-to-text/{stem}.{ext}"
    return "language/assets/more/speech-to-text.png"


def compare_words(expert: str, heard: str) -> dict:
    """Which of `heard`'s words match the expert's transcript, ignoring case, punctuation and hyphens.
    matched counts the expert's words that the recognizer got; the rest of `heard` is underlined on the page."""
    import difflib
    key = lambda w: re.sub(r"[^\w']", "", w.lower().replace("’", "'").replace("‘", "'").replace("-", ""))
    want = [key(w) for w in expert.split() if key(w)]
    words = heard.split()
    got = [key(w) for w in words]
    ok = [False] * len(words)
    matched = 0
    for block in difflib.SequenceMatcher(None, want, got, autojunk=False).get_matching_blocks():
        matched += block.size
        for k in range(block.b, block.b + block.size):
            ok[k] = True
    return {"words": [[w, o] for w, o in zip(words, ok)], "matched": matched, "total": len(want)}


def stt_slugs() -> list[str]:
    return sorted(p.parent.name for p in SRC.glob("*/stt.json"))


def render_stt(slug: str) -> str:
    """/language/<slug>/speech-to-text. Wording comes from _src/<slug>/stt.json; every score, time, average and
    link is computed from the language's evaluation data, so this page can't disagree with the language page."""
    import html as _html
    esc = lambda t: _html.escape(str(t), quote=True)
    st = json.loads((SRC / slug / "stt.json").read_text())
    page = json.loads((SRC / slug / "page.json").read_text())
    lang, bulk = page["lang"], eval_url(page)
    csv_rows, _, _ = chains_for(page)
    links = workflow_urls(page, csv_rows)
    chains = [{"model": m.replace("GPT 5.6 Sol", "GPT-5.6 Sol"), "speech": sp, "acc": acc, "score": round(acc * 100 + 1e-9),
               "time": t, "url": links[i]} for i, (m, sp, acc, t, _sov) in enumerate(csv_rows)]
    name = lambda c: c["model"] if c["speech"] == DIRECT_AUDIO else f'{c["model"]} + {c["speech"]}'
    by_key = {norm(f'{c["model"]} + {c["speech"]}'): c for c in chains}
    top = max(chains, key=lambda c: (c["acc"], -c["time"]))

    recs = []
    for r in st["recognizers"]:
        cs = [c for c in chains if c["speech"] == r["speech"]]
        if not cs:
            raise SystemExit(f"{slug} speech-to-text: no chain uses {r['speech']!r}")
        if norm(r["chain"]) not in by_key:
            raise SystemExit(f"{slug} speech-to-text: chain {r['chain']!r} is not in the evaluation")
        recs.append({**r, "label": r.get("label", r["speech"]), "chains": cs, "source": by_key[norm(r["chain"])],
                     "avg": sum(c["acc"] for c in cs) / len(cs) * 100,
                     "best": max(cs, key=lambda c: (c["acc"], -c["time"])), "direct": r["speech"] == DIRECT_AUDIO})
    rec = next((r for r in recs if r["speech"] == top["speech"]), None)
    if rec is None:
        raise SystemExit(f"{slug} speech-to-text: the top chain's speech step {top['speech']!r} is not in stt.json recognizers")
    recs.sort(key=lambda r: r is not rec)
    api = rec if rec.get("api") else next((r for r in recs if r.get("api")), None)
    if api is None:
        raise SystemExit(f"{slug} speech-to-text: no recognizer in stt.json has an 'api' preset")
    separate = [r for r in recs if not r["direct"]]

    index = lambda c: f'<strong>{c["score"]} / 100</strong> {lang} Index'

    def card_text(r: dict) -> str:
        if r["direct"]:
            b = r["best"]
            return (f'{r["about"]} It listens to the question and answers in one step: {index(b)}, '
                    f'{b["time"]:.1f} s median reply.')
        parts = [r["about"]]
        for o in separate:
            if o is r:
                continue
            shared = {c["model"] for c in r["chains"]} & {c["model"] for c in o["chains"]}
            mine = {c["model"]: c["time"] for c in r["chains"]}
            theirs = {c["model"]: c["time"] for c in o["chains"]}
            if shared and all(mine[m] < theirs[m] for m in shared):
                parts.append(f'Faster than {o["label"]} with every language model we paired it with.')
        if r is rec:
            parts.append(f'Powers the top chain, {name(top)}: {index(top)}.')
        else:
            b = r["best"]
            parts.append(f'Best paired with {b["model"]}: {index(b)}.')
        return " ".join(parts)

    # Hosting, worded as on the language page: a recognizer is sovereign-deployable when its speech step is
    # (direct audio: when the model is).
    sov_models = set(page.get("sovereign_models", SOVEREIGN_MODELS))
    sov_speech = set(page.get("sovereign_speech", SOVEREIGN_SPEECH))
    hosting = lambda r: ("Sovereign" if (r["best"]["model"] in sov_models if r["direct"] else r["speech"] in sov_speech)
                         else "Private API")

    def logo(stem: str, size: int) -> str:
        big = f"{stem}-24"
        use = big if size == 24 and (LANG / "assets" / "kinyarwanda" / f"{big}.svg").exists() else stem
        return f'<img src="assets/kinyarwanda/{use}.svg" alt="" width="{size}" height="{size}" />'

    cards = []
    for r in recs:
        kind = "Recommended" if r is rec else DIRECT_AUDIO if r["direct"] else r.get("tag", "")
        tag = (CHECK_12 if r is rec else "") + " · ".join(x for x in (kind, hosting(r)) if x)
        cards.append(f'            <article class="st-card{" rec" if r is rec else ""}"><span class="st-tag">{tag}</span>'
                     f'<h3>{logo(r["logo"], 24)}{r["label"]}</h3><p>{card_text(r)}</p></article>')

    samples = json.loads((DATA / page["code"] / "samples.json").read_text())
    sample = samples["samples"][0]
    with (DATA / page["code"] / "evaluation-latest.csv").open(encoding="utf-8-sig", newline="") as f:
        eval_rows = list(csv.DictReader(f))
    expert_of = lambda q: (eval_rows[q - 1].get("Prompt_Target") or eval_rows[q - 1].get("Question_Target") or "").strip()
    tpath = DATA / page["code"] / f"transcripts-{page['snapshot']}.json"
    if not tpath.exists():
        raise SystemExit(f"{slug} speech-to-text: {tpath.relative_to(ROOT)} is missing; "
                         f"run python3 scripts/fetch_language_transcripts.py {slug}")
    heard = {(t["question"], t["recognizer"]): t["text"] for t in json.loads(tpath.read_text())["transcripts"]}
    def heard_by(q: int, r: dict) -> str:
        if (q, r["speech"]) not in heard:
            raise SystemExit(f"{slug} speech-to-text: no {r['speech']} transcript for question {q} in {tpath.name}; "
                             f"run python3 scripts/fetch_language_transcripts.py {slug}")
        return heard[(q, r["speech"])]
    hero_q = hero_question(page)
    shown = rec if not rec["direct"] else (separate[0] if separate else None)
    if shown is None:
        raise SystemExit(f"{slug} speech-to-text: needs at least one speech recognizer besides direct audio")
    transcript_samples = [{
        "questionNumber": x["questionNumber"], "category": x.get("category", ""), "audioUrl": x["audioUrl"],
        "audioDurationSeconds": x["audioDurationSeconds"], "expert": expert_of(x["questionNumber"]),
        "heard": [{"label": r["label"], "logo": r["logo"], **compare_words(expert_of(x["questionNumber"]), heard_by(x["questionNumber"], r))}
                  for r in separate],
    } for x in samples["samples"]]
    stt_config = {"lang": lang, "langCode": st.get("lang_code", ""), "dataBase": f"data/{page['code']}/",
                  "totalQuestions": samples["totalQuestions"], "samples": transcript_samples}

    sample_model, _, sample_speech = samples["workflow"].partition(" + ")
    sample_speech = sample_speech or DIRECT_AUDIO

    curl = (f'curl https://api.gooey.ai/v2/speech \\\n'
            f'  -H "Authorization: Bearer $GOOEY_API_KEY" \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f"  -d '{{\n"
            f'    "documents": ["{sample["audioUrl"]}"],\n'
            f'    "selected_model": "{api["api"]["model"]}",\n'
            f'    "language": "{api["api"]["language"]}"\n'
            f"  }}'")
    prompt = (f"Transcribe spoken {lang} with the Gooey.AI speech API.\n"
              f"POST https://api.gooey.ai/v2/speech with the header Authorization: Bearer $GOOEY_API_KEY and a JSON body:\n"
              f"- documents: a list of public audio file URLs\n"
              f'- selected_model: "{api["api"]["model"]}" ({api["label"]}, the speech recognizer in the best {lang} chain '
              f"in our {page['updated']} evaluation)\n"
              f'- language: "{api["api"]["language"]}"\n'
              f"Get a key at https://gooey.ai/account/api-keys/ and see https://api.gooey.ai/docs for the response format.\n\n"
              f"Example:\n{curl}\n")

    # FAQ
    ranked = sorted(separate, key=lambda r: -r["avg"])
    best = ranked[0]
    who = f'{best["maker"]}’s {best["label"]}' if best.get("maker") else best["label"]
    others = " and ".join(f'{o["avg"]:.1f}/100 for {o["label"]}' for o in ranked[1:])
    results = f'<a href="{slug}/#all-chains">benchmark results</a>'
    a1 = (f"{who} was the strongest speech recognition in our {page['updated']} {lang} benchmark: chains using it "
          f"averaged a {lang} Index of {best['avg']:.1f}/100")
    a1 += f", against {others}." if others else "."
    for r in recs:
        if r["direct"]:
            a1 += f' {r["label"]} (direct audio), which needs no separate speech step, scored {r["best"]["score"]}/100.'
    a1 += f" See the {results}. These are complete-workflow results, not standalone speech-recognition scores."
    fast = [c for c in chains if c["time"] < 10]
    fastest = min(chains, key=lambda c: c["time"])
    a2 = (f"The {page['questions']} benchmark questions were sent as WhatsApp voice notes. For phone-call pilots, "
          + (f"{len(fast)} of the {len(chains)} chains stayed below our 10-second median response-time target; the fastest was "
             f"{name(fastest)} ({fastest['time']:.1f} seconds). " if fast else
             f"none of the {len(chains)} chains stayed below our 10-second median response-time target. ")
          + "These timings exclude a complete phone connection and spoken reply; test telephony, network and "
            "text-to-speech latency before launch.")
    data_dir = DATA / page["code"]
    hub_faq = dict(faq_items(page, csv_rows, json.loads((data_dir / f"pricing-{page['snapshot']}.json").read_text()),
                             json.loads((data_dir / f"ecocost-{page['snapshot']}.json").read_text()),
                             json.loads((SRC / slug / "faq.json").read_text()) if (SRC / slug / "faq.json").exists() else {},
                             json.loads((SRC / "models.json").read_text())))
    index_q = f"What does the {lang} Index measure?"
    faq = [(f"What is the best {lang} speech to text?", a1),
           ("Does it work on WhatsApp voice notes and phone calls?", a2),
           ("Can I run it on my own servers?", st["self_host"])]
    if index_q in hub_faq:
        faq.append((index_q, hub_faq[index_q]))
    faq_section = render_faq((SRC / "faq.tmpl").read_text(), faq)

    if rec["direct"]:
        found = f"<strong>{rec['label']}</strong>, listening to the audio directly,"
    else:
        found = f"<strong>{rec['label']}</strong> ASR, paired with the <strong>{top['model']}</strong> language model,"
    lead_html = (f"Turn spoken {lang} into text. Our latest {lang} Index eval conducted on "
                 f"<strong>{ordinal_date(page['snapshot'])}</strong> found that {found} scored the "
                 f"<strong>highest Index</strong> on answers to questions asked by native speakers.")

    slots = {
        "header": HEADER_HTML.format(title=f"{lang} speech to text").rstrip("\n"),
        "slug": slug, "lang": lang, "lang_code": st.get("lang_code", ""),
        "voice_note": voice_note(page), "heard_label": shown["label"], "heard_logo": shown["logo"],
        "heard_text": esc(heard_by(hero_q, shown)),
        "samples_intro": (f"{['One', 'Two', 'Three', 'Four', 'Five'][len(samples['samples']) - 1] if len(samples['samples']) <= 5 else len(samples['samples'])} "
                          f"of the {samples['totalQuestions']} questions, sent as WhatsApp voice notes. "
                          "Underlined words differ from the expert’s transcript."),
        "copy_svg": COPY_SVG,
        "questions": str(page["questions"]),
        "model_cards": "\n".join(cards),
        "art_step1": stt_art(), "rec_label": api["label"], "rec_logo": api["logo"],
        "sample_audio": esc(sample["audioUrl"]), "sample_english": esc(sample["questionEnglish"]),
        "sample_transcript": esc(sample["transcript"]), "sample_answer": esc(sample["answer"]),
        "sample_speech": sample_speech, "sample_model": sample_model,
        "api_curl": esc(curl), "api_prompt": esc(prompt),
        "faq_section": faq_section, "lead_html": lead_html,
        "cta_text": f"Start from {name(top)}, the chain with the highest {lang} Index.",
        "language_list": language_list(lang, lambda s: f"{s}/speech-to-text/" if (SRC / s / "stt.json").exists() else None),
    }
    body = (SRC / "stt.tmpl").read_text()
    for key, value in slots.items():
        body = body.replace("{{%s}}" % key, value)
    left = re.findall(r"\{\{\w+\}\}", body)
    if left:
        raise SystemExit(f"{slug} speech-to-text: unfilled template slots {sorted(set(left))}")
    labels = f"{', '.join(r['label'] for r in recs[:-1])} and {recs[-1]['label']}"
    q, best = page["questions"], f"Best result: {top['score']}/100 with {rec['label']}."
    descriptions = [f"Turn spoken {lang} into text. {labels} compared on {q} real spoken questions; {name(top)} scored {top['score']}/100.",
                    f"Turn spoken {lang} into text: {labels} compared on {q} real spoken questions. {best}",
                    f"Turn spoken {lang} into text: {len(recs)} speech recognizers compared on {q} real spoken questions. {best}"]
    titles = [f"{lang} Speech to Text: ASR Models Compared{seo.BRAND}", f"{lang} Speech to Text{seo.BRAND}"]
    title = f"{lang} speech to text"
    card = {"eyebrow": f"Speech to text · {page['country']}", "title": title, "lead": ["Best recognizer", rec["label"]],
            "stats": [[f"{lang} Index", str(top["score"]), "/ 100", f"with {top['model']}"],
                      ["Recognizers", str(len(recs)), "", "compared"],
                      ["Questions", str(page["questions"]), "", "asked by native speakers"]],
            "visual": {"kind": "photo", "src": stt_art_file()}}
    alt = (f"{title}: {len(recs)} recognizers compared on {page['questions']} spoken questions; the top chain, {name(top)}, "
           f"scored {top['score']} out of 100.")
    seo_tags = sub_seo(page, f"language/{slug}/speech-to-text", titles, descriptions, card, alt, body, "Speech to text")
    head = STT_HEAD.format(lang=lang, header_css=HEADER_CSS, seo=seo_tags)
    cfg = json.dumps(stt_config, ensure_ascii=False, separators=(", ", ": "))
    return head + body.rstrip("\n") + "\n" + STT_TAIL.format(config=cfg)


def all_pages(only: list[str] | None = None) -> dict[pathlib.Path, str]:
    """Every generated page: output path -> HTML. `only` filters by language slug."""
    pages = {}
    for slug in slugs():
        if not only or slug in only:
            pages[LANG / slug / "index.html"] = render(slug)
    for slug in agent_slugs():
        if not only or slug in only:
            pages[LANG / slug / "ai-agent" / "index.html"] = render_agent(slug)
    for slug in stt_slugs():
        if not only or slug in only:
            pages[LANG / slug / "speech-to-text" / "index.html"] = render_stt(slug)
    import build_model_pages  # imported here: it imports this module
    for path, page in build_model_pages.pages().items():
        if not only or path.parent.name in only:
            pages[path] = page
    return pages


def main(argv: list[str]) -> int:
    check = "--check" in argv
    wanted = [a for a in argv if not a.startswith("--")]
    pages = all_pages(wanted)
    stale = []
    for out, html in pages.items():
        rel = out.relative_to(ROOT)
        if check:
            if not out.exists() or out.read_text(encoding="utf-8") != html:
                stale.append(str(rel))
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8")
            print(f"wrote {rel}")
    if stale:
        print("stale (run: python3 scripts/build_language_pages.py):")
        for item in stale:
            print("  " + item)
        return 1
    if check:
        print(f"ok: {len(pages)} language page(s) match their template + data")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
