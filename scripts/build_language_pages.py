#!/usr/bin/env python3
"""Build the /language/<name>/index.html evaluation pages from one template.

    python3 scripts/build_language_pages.py              # rewrite every page
    python3 scripts/build_language_pages.py swahili      # just one
    python3 scripts/build_language_pages.py --check      # fail if a page is stale

Layout and behaviour live in two shared files that every page links to:

    language/assets/language-page.css
    language/assets/language-page.js

What is specific to one language lives in language/_src/<slug>/:

    page.json      names, hero copy, chart geometry, axis ranges, notes
    picks.frag     "Which chain should you pick?" section (editorial)
    featured.frag  featured lab / "what changed the result?" section (editorial)
    faq.frag       FAQ section (editorial)

The numbers come straight from the data files in language/data/<code>/
(summary CSV, pricing JSON, EcoCost JSON), so the chart, table and hero
counts can't disagree with the data. The page header is pasted in
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

HEAD = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <!-- GOOEY-BASE-HREF -->
    <base href="../" />
    <title>Best AI for {lang} | Gooey.AI</title>
    <meta
      name="description"
      content="{description}"
    />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="Best AI for {lang} | Gooey.AI" />
    <meta
      property="og:description"
      content="{og_description}"
    />
    <meta property="og:url" content="https://gooey.ai/language/{slug}" />
    <meta property="og:site_name" content="Gooey.AI" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    />
    <style>
{header_css}    </style>
    <link rel="stylesheet" href="assets/language-page.css" />
  </head>
  <body class="layout-{layout}">
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


def language_list(current: str, href=None) -> str:
    """The footer's other-languages list. `href(slug)` gives the link for a language that has a page; a language
    without one (or no `href`) is plain text."""
    cfg = json.loads((SRC / "languages.json").read_text())
    slug_of = {json.loads(p.read_text())["lang"]: p.parent.name for p in SRC.glob("*/page.json")}
    items = "".join((f'<li><a href="{href(slug_of[n])}">{n}</a></li>' if href and n in slug_of else f"<li>{n}</li>")
                    for n in cfg["languages"] if n != current)
    return (f'<ul class="language-list" aria-label="Other Gooey.AI languages">{items}'
            f'<li><strong>{cfg["all"]}</strong></li></ul>')


def render(slug: str) -> str:
    d = SRC / slug
    page = json.loads((d / "page.json").read_text())
    csv_rows, pricing, ecocost = chains_for(page)
    n = len(csv_rows)
    n_sov = sum(1 for r in csv_rows if r[4])
    metrics = page["scatter"]["metrics"]

    config = {
        "lang": page["lang"], "dataDir": f"data/{page['code']}", "layout": page["layout"],
        "questions": page["questions"], "csv": csv_rows, "pricing": pricing, "eco": ecocost,
        "geometry": page["geometry"],
        "scatter": {k: page["scatter"][k] for k in ("x", "xTicks", "labelBestSovereign", "metrics")},
        "sample": page["sample"], "labSpeech": page.get("labSpeech"), "slug": slug,
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
    chains_foot = f'<p>{page["chains_foot_p"]}</p>{model_nav}'

    slots = {
        "header": HEADER_HTML.format(title=f"Best AI for {page['lang']}").rstrip("\n"),
        "lang": page["lang"], "flag": page["flag"], "endonym": page["endonym"], "country": page["country"],
        "updated": page["updated"], "lead_html": hero["lead_html"], "bulk_url": hero["bulk_url"],
        "map_alt": hero["map"]["alt"], "map_img": map_img,
        "vn_time": hero["voice"]["time"], "vn_text": hero["voice"]["text"], "vn_sub": hero["voice"]["sub"],
        "n": str(n), "n_sov": str(n_sov), "n_priv": str(n - n_sov), "questions": str(page["questions"]),
        "board_hint": page["board"]["hint"], "speech_key": speech_key, "board_note": page["board"]["note"],
        "picks_section": (d / "picks.frag").read_text().rstrip("\n"),
        "featured_section": (d / "featured.frag").read_text().rstrip("\n"),
        "faq_section": (d / "faq.frag").read_text().rstrip("\n"),
        "scatter_aria": " " + page["scatter"]["aria"],
        "score_front": metrics["score"]["front"], "score_note": metrics["score"]["note"],
        "chains_foot": chains_foot, "samples_intro": page["samples_intro"],
        "language_list": language_list(page["lang"], lambda s: f"{s}/"), "slug": slug,
    }
    body = (SRC / "body.tmpl").read_text()
    for key, value in slots.items():
        body = body.replace("{{%s}}" % key, value)
    left = re.findall(r"\{\{\w+\}\}", body)
    if left:
        raise SystemExit(f"{slug}: unfilled template slots {sorted(set(left))}")

    head = HEAD.format(
        lang=page["lang"], slug=slug, layout=page["layout"], header_css=HEADER_CSS,
        description=page["meta"]["description"], og_description=page["meta"]["og_description"],
    )
    cfg_json = json.dumps(config, ensure_ascii=False, separators=(", ", ": "))
    return head + body.rstrip("\n") + "\n" + TAIL.format(config=cfg_json)


def slugs() -> list[str]:
    return sorted(p.parent.name for p in SRC.glob("*/page.json"))


# ---------------------------------------------------------------------------------------------------------
# /language/<name>/ai-agent

AGENT_HEAD = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <!-- GOOEY-BASE-HREF -->
    <base href="../../" />
    <title>Build a {lang} AI agent | Gooey.AI</title>
    <meta
      name="description"
      content="{description}"
    />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="Build a {lang} AI agent | Gooey.AI" />
    <meta
      property="og:description"
      content="{description}"
    />
    <meta property="og:url" content="https://gooey.ai/language/{slug}/ai-agent" />
    <meta property="og:site_name" content="Gooey.AI" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
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
    description = (f"Launch a {lang} AI agent on WhatsApp, a phone line or the web, using the chain that scored best in our tests "
                   f"({chain_label(top)}, {top['score']} out of 100).")
    head = AGENT_HEAD.format(lang=lang, slug=slug, header_css=HEADER_CSS, description=description)
    cfg = json.dumps(config, ensure_ascii=False, separators=(", ", ": "))
    return head + body.rstrip("\n") + "\n" + AGENT_TAIL.format(config=cfg)


def agent_slugs() -> list[str]:
    return sorted(p.parent.name for p in SRC.glob("*/agent.json"))


def all_pages(only: list[str] | None = None) -> dict[pathlib.Path, str]:
    """Every generated page: output path -> HTML. `only` filters by language slug."""
    pages = {}
    for slug in slugs():
        if not only or slug in only:
            pages[LANG / slug / "index.html"] = render(slug)
    for slug in agent_slugs():
        if not only or slug in only:
            pages[LANG / slug / "ai-agent" / "index.html"] = render_agent(slug)
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
