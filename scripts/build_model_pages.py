#!/usr/bin/env python3
"""Build the /models/<model>/<language> pages ("GPT-5.6 Sol in Kinyarwanda: Accuracy, Speed & Cost").

Called by scripts/build_language_pages.py (run that one; it builds every generated page). One page is written
for every model that has results in a language: models/<model-slug>/<language-slug>/index.html.

Inputs, all shared with the language and ai-agent pages:

    language/data/<code>/               summary CSV, pricing + EcoCost JSON, evaluator CSV, samples.json
    language/_src/<slug>/agent.json     language name, country, data folder
    language/_src/<slug>/page.json      hero voice note, run URL, updated date
    language/_src/models.json           per-model facts: maker, open weights, hosting regions, previous version
    language/_src/model.tmpl            page skeleton

Everything on a page is computed from the data: ranks among the models, the comparison table, the three sample
answers (this model's best chain, from the evaluator CSV), cost and CO2e, the FAQ. A section needs data we do not
have yet is simply left out (the Figma frame's translation / transcription scores, for one).

"What changed since <previous model>" (language/_src/model-changed.tmpl) is shown only when both are true:

  1. models.json says which model this one replaced, newest first (older entries add bars to the chart):

        "replaces": [{"name": "GPT-5.1", "on": "Feb 12, 2026",
                      "notes": {"kinyarwanda": [["good", "Stays in Kinyarwanda more often."]]}}]

     "on" (optional) is when it was replaced; "notes" (optional) are the "In the answers" lines, per language,
     each ["good" | "info", text].
  2. An archived snapshot of the language (page.json "archive", data/<code>/summary-<date>.csv) has a chain of the
     replaced model, and its evaluation-<date>.csv asked the same questions as the current run. The chain with the
     same speech recognition as this model's best chain is used (like for like), else that model's best chain.

Otherwise the section, its sentence in the comparison paragraph and its FAQ answer are left out.
"""

from __future__ import annotations

import csv
import html
import json
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_language_pages as b  # noqa: E402
import seo  # noqa: E402

ROOT, LANG, SRC = b.ROOT, b.LANG, b.SRC
csv.field_size_limit(10**8)
MODELS = json.loads((SRC / "models.json").read_text(encoding="utf-8"))
TEMPLATE_CHANGED = (SRC / "model-changed.tmpl").read_text(encoding="utf-8")


def fill(template: str, slots: dict) -> str:
    out = template
    for key, value in slots.items():
        out = out.replace("{{%s}}" % key, str(value))
    left = re.findall(r"\{\{\w+\}\}", out)
    if left:
        raise SystemExit(f"unfilled template slots {sorted(set(left))}")
    return out
DOCS_EVAL = "https://docs.gooey.ai/speech-and-language/how-to-use-asr/how-to-create-language-evaluation-for-asr"
CONTACT = "https://gooey.ai/contact/"
API = "https://gooey.ai/api/"
esc = html.escape

# The page's own <base> comes before the GOOEY-BASE-HREF placeholder. Only the first <base> in a document counts, and
# gooey.ai's proxy replaces the placeholder with <base href="<Pages host>/<this page's folder>/">, which would send the
# relative paths below one or two folders too deep. With ours first, gooey.ai requests <path> on gooey.ai, which
# redirects to the Pages host (CORS allows the fetch of samples.json).
HEAD = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <base href="../../" />
    <!-- GOOEY-BASE-HREF -->
{seo}    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    />
    <style>
{header_css}    </style>
    <link rel="stylesheet" href="../language/assets/language-page.css" />
    <link rel="stylesheet" href="../language/assets/language-model.css" />
  </head>
  <body>
"""

TAIL = """
    <script>
      window.MODEL_PAGE = {config};
    </script>
    <script src="../language/assets/language-samples.js"></script>
    <script src="../language/assets/language-model.js"></script>
    <script src="../language/assets/language-links.js"></script>
  </body>
</html>
"""

ASSET = "../language/assets/"  # <base href="../../"> makes paths relative to models/
ICONS = {
    "cloud": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.5 12.5a3 3 0 0 1-.4-5.97A4 4 0 0 1 11.8 5.6 3.5 3.5 0 0 1 11.5 12.5z"/></svg>',
    "globe": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="8" r="6"/><path d="M2 8h12M8 2c1.7 1.8 2.5 3.8 2.5 6S9.7 12.2 8 14c-1.7-1.8-2.5-3.8-2.5-6S6.3 3.8 8 2z"/></svg>',
    "shield": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 1.8 13 3.6v4c0 3-2.2 5.2-5 6.6-2.8-1.4-5-3.6-5-6.6v-4z"/><path d="m5.8 8 1.5 1.5 3-3"/></svg>',
    "server": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="2.5" width="11" height="4.5" rx="1.2"/><rect x="2.5" y="9" width="11" height="4.5" rx="1.2"/><path d="M5 4.8h.01M5 11.3h.01"/></svg>',
    "mic": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5.5" y="1.5" width="5" height="8" rx="2.5"/><path d="M3 7.5a5 5 0 0 0 10 0M8 12.5v2"/></svg>',
    "leaf": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 13.5C2.5 7 6 3 13.5 2.5c0 7-4 11-11 11zM2.5 13.5c1.8-3.2 4-5.3 6.5-6.8"/></svg>',
    "drop": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 2s4.5 4.4 4.5 7.5a4.5 4.5 0 0 1-9 0C3.5 6.4 8 2 8 2z"/></svg>',
    "bolt": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 1.5 3.5 9H8l-1 5.5L12.5 7H8z"/></svg>',
    "bulb": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 12.5h4M6.5 14.5h3M8 1.8a4.2 4.2 0 0 0-2.3 7.7c.4.3.6.7.6 1.2v.3h3.4v-.3c0-.5.2-.9.6-1.2A4.2 4.2 0 0 0 8 1.8z"/></svg>',
    "coin": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="1.75" y="1.75" width="12.5" height="12.5" rx="2.5"/><path d="M8 4v8M10.2 5.9C9.8 5.3 9 5 8 5c-1.2 0-2.2.5-2.2 1.5S6.7 8 8 8s2.2.5 2.2 1.5S9.2 11 8 11c-1 0-1.8-.3-2.2-.9"/></svg>',
    "check": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 8.5 3.2 3L13 4.5"/></svg>',
    "info": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="8" r="6.25"/><path d="M8 7.2v3.8M8 5h.01"/></svg>',
    "lock": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3.5" y="7" width="9" height="7" rx="1.5"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2"/></svg>',
    "chev": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 3.5 4.5 4.5L6 12.5"/></svg>',
}

# Monetary pricing is not published yet: every evaluated chain was billed the same flat Gooey.AI run charge, so cost
# slots show "Coming soon" (greyed out) instead of a figure, as on the language pages. EcoCost figures stay live.
PRICING_COMING_SOON = True
PENDING = "Coming soon"

# Round flags shown before a hosting region in "Where you can run it" (names as in models.json hosted_in / zdr_in).
_ROUND = '<svg class="md-flag" viewBox="0 0 16 16" aria-hidden="true"><clipPath id="f{id}"><circle cx="8" cy="8" r="8"/></clipPath><g clip-path="url(#f{id})">{body}</g><circle cx="8" cy="8" r="7.75" fill="none" stroke="rgba(0,0,0,.12)" stroke-width=".5"/></svg>'
FLAGS = {
    "Global": ICONS["globe"].replace("<svg ", '<svg class="md-flag" ', 1),
    "US": _ROUND.format(id="us", body='<rect width="16" height="16" fill="#fff"/>' + "".join(
        f'<rect y="{y}" width="16" height="1.25" fill="#d22f27"/>' for y in (0, 2.5, 5, 7.5, 10, 12.5, 15))
        + '<rect width="8" height="8.75" fill="#1e50a0"/>'),
    "Germany": _ROUND.format(id="de", body='<rect width="16" height="5.4" fill="#1a1a1a"/><rect y="5.3" width="16" height="5.4" fill="#d22f27"/><rect y="10.6" width="16" height="5.4" fill="#f1b31c"/>'),
    "France": _ROUND.format(id="fr", body='<rect width="5.4" height="16" fill="#1e50a0"/><rect x="5.3" width="5.4" height="16" fill="#fff"/><rect x="10.6" width="5.4" height="16" fill="#d22f27"/>'),
}


def hero_art() -> str:
    """The hero illustration: language/assets/models/hero.{webp,jpg,png} (4:3), else the labelled placeholder."""
    alt = "Hands holding a phone showing a check mark, in front of terraced hills"
    for ext in ("webp", "jpg", "png"):
        if (b.LANG / "assets" / "models" / f"hero.{ext}").exists():
            return f'<img class="md-art" src="{ASSET}models/hero.{ext}" alt="{alt}" width="399" height="300" fetchpriority="high" />'
    return f'<div class="md-art" role="img" aria-label="{alt}">Illustration to come</div>'


def eco_art() -> str:
    """The EcoCost card's illustration: language/assets/models/ecocost.{webp,jpg,png} (4:3), else a plain placeholder."""
    for ext in ("webp", "jpg", "png"):
        if (b.LANG / "assets" / "models" / f"ecocost.{ext}").exists():
            return (f'<img class="md-eco-art" src="{ASSET}models/ecocost.{ext}" alt="Cupped hands holding a seedling in soil" '
                    'width="220" height="165" loading="lazy" decoding="async" />')
    return '<div class="md-eco-art" role="img" aria-label="Illustration to come"></div>'


# ---------------------------------------------------------------------------------------------------------
# data

def languages() -> dict[str, dict]:
    """Language slug -> everything the model pages need about it (name, data folder, hero voice, run URL)."""
    out = {}
    for slug in b.agent_slugs():
        a = json.loads((SRC / slug / "agent.json").read_text())
        page = json.loads((SRC / slug / "page.json").read_text())
        facts = b.agent_facts(a)
        best = {}
        for c in facts["chains"]:
            if c["model"] not in best or (c["acc"], -c["time"]) > (best[c["model"]]["acc"], -best[c["model"]]["time"]):
                best[c["model"]] = c
        ranked = sorted(best.values(), key=lambda c: (-c["acc"], c["time"]))
        out[slug] = {"archive": archived_runs(a["code"], page), "slug": slug, "lang": a["lang"], "country": a["country"], "code": a["code"], "snapshot": a["snapshot"],
                     "updated": page["updated"], "questions": page["questions"], "bulk_url": page["hero"]["bulk_url"],
                     "voice": page["hero"]["voice"], "flag": page["flag"], "facts": facts, "best": best, "ranked": ranked}
    return out


def questions(path: pathlib.Path) -> set[str] | None:
    if not path.exists():
        return None
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
    col = next((k for k in ("Prompt_Target", "Question_Target", "Prompt_Source", "Prompt") if rows and k in rows[0]), None)
    return {r[col].strip() for r in rows} if col else None


def archived_runs(code: str, page: dict) -> list[dict]:
    """Older snapshots of a language (page.json "archive"), newest first, that asked the same questions as the current
    run: each with its chains' scores and response times. A snapshot whose questions differ, or can't be checked, is
    skipped, so its numbers are never set beside today's."""
    now = questions(b.DATA / code / "evaluation-latest.csv")
    out = []
    for a in sorted(page.get("archive", []), key=lambda a: a["snapshot"], reverse=True):
        snap = a["snapshot"]
        if not now or questions(b.DATA / code / f"evaluation-{snap}.csv") != now:
            continue
        lines = [l for l in open(b.DATA / code / f"summary-{snap}.csv", encoding="utf-8") if not l.startswith("#") and l.strip()]
        chains = []
        for r in csv.DictReader(lines):
            model, _, speech = r["Workflow"].strip().partition(" + ")
            speech = b.SPEECH_ALIASES.get(speech, speech) or b.DIRECT_AUDIO
            acc = float(r["Accuracy (mean)"])
            chains.append({"model": model, "speech": speech, "acc": acc, "score": round(acc * 100 + 1e-9),
                           "time": float(r["Latency (median)"])})
        out.append({"snapshot": snap, "label": a["label"], "month": month_short(snap), "chains": chains})
    return out


def month_short(snapshot: str) -> str:
    y, m, _ = (int(x) for x in snapshot.split("-"))
    return f"{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][m - 1]} {y}"


def previous_runs(model: str, c: dict, L: dict) -> list[dict]:
    """The models this one replaced (models.json "replaces", newest first) that ran in an archived snapshot of the
    language, each as the chain to compare with: same speech recognition as `c` if that ran, else its best chain.
    Empty unless the direct predecessor (the first entry) has data, so "What changed since" never skips a version."""
    out = []
    for i, r in enumerate(MODELS[model].get("replaces") or []):
        for snap in L["archive"]:
            runs = [x for x in snap["chains"] if b.norm(x["model"]) == b.norm(r["name"])]
            if not runs:
                continue
            same = [x for x in runs if b.norm(x["speech"]) == b.norm(c["speech"])]
            pick = max(same or runs, key=lambda x: (x["acc"], -x["time"]))
            out.append({**pick, "name": r["name"], "on": r.get("on"), "notes": (r.get("notes") or {}).get(L["slug"], []),
                        "snapshot": snap, "like": bool(same)})
            break
        if i == 0 and not out:
            return []
    return out


def model_slugs() -> list[tuple[str, str]]:
    """(model, language slug) for every page: a model with at least one chain in that language."""
    return [(m, slug) for slug, L in languages().items() for m in sorted(L["best"], key=lambda m: L["ranked"].index(L["best"][m]))]


def rank_phrase(rank: int, values: list[float], value: float, lower_better: bool = False) -> str:
    """'#2 of 5', with ', tied' when another model has the same value."""
    tied = sum(1 for v in values if abs(v - value) < 1e-9) > 1
    return f"#{rank} of {len(values)}" + (", tied" if tied else "")


def competition_rank(values: list[float], value: float, lower_better: bool) -> int:
    return 1 + sum(1 for v in values if (v < value - 1e-9 if lower_better else v > value + 1e-9))


def and_join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def month_year(updated: str) -> str:
    months = {"Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April", "May": "May", "Jun": "June", "Jul": "July",
              "Aug": "August", "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December"}
    m = re.match(r"([A-Z][a-z]{2}) \d+, (\d{4})", updated)
    return f"{months[m.group(1)]} {m.group(2)}" if m else updated


def chain_outputs(code: str, lang: str) -> tuple[list[dict], dict[str, int]]:
    """Evaluator CSV rows, and normalised chain name -> chain index in its columns."""
    rows = list(csv.DictReader(open(b.DATA / code / "evaluation-latest.csv", encoding="utf-8", newline="")))
    index = {}
    for col in rows[0]:
        m = re.fullmatch(r"\((\d+) (.+?) - %s\) Run URL" % re.escape(lang), col)
        if m:
            name = m.group(2)
            head, _, speech = name.partition(" + ")
            name = head + (f" + {b.SPEECH_ALIASES.get(speech, speech)}" if speech else "")
            index[b.norm(name)] = int(m.group(1))
    return rows, index


def samples_for(L: dict, chain: dict) -> dict:
    """The language's three sample questions, answered by `chain`, from the evaluator CSV."""
    base = json.loads((b.DATA / L["code"] / "samples.json").read_text())
    rows, index = chain_outputs(L["code"], L["lang"])
    key = b.norm(chain["model"] + ("" if chain["speech"] == b.DIRECT_AUDIO else f" + {chain['speech']}"))
    i = index[key]
    col = lambda suffix: next(c for c in rows[0] if re.fullmatch(r"\(%d .+? - %s\) %s" % (i, re.escape(L["lang"]), suffix), c))
    sem = next(c for c in rows[0] if c.startswith(f"Compare Semantics Similarity - Output Text - {i} "))
    out = []
    for s in base["samples"]:
        row = rows[s["questionNumber"] - 1]
        answer = row[col("Output Text")].strip()
        answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.S).strip() or answer   # some models return their reasoning
        answer = re.sub(r'^🎧:\s*"[^"]*"\s*', "", answer).strip() or answer  # drop the transcript line some chains prepend
        out.append({**s, "answer": answer, "score": round(float(row[sem]) * 100),
                    "runtimeSeconds": float(row[col("Run Time")]), "runUrl": row[col("Run URL")]})
    return {"totalQuestions": base["totalQuestions"], "samples": out}


# ---------------------------------------------------------------------------------------------------------
# page

def render_model(model: str, lslug: str) -> str:
    langs = languages()
    L = langs[lslug]
    meta = MODELS[model]
    mslug = meta["slug"]
    best, ranked, facts = L["best"], L["ranked"], L["facts"]
    c = best[model]
    N = len(ranked)
    lang = L["lang"]
    scores = [x["score"] for x in ranked]
    times = [x["time"] for x in ranked]
    costs = [x["cost"] for x in ranked]
    rank = competition_rank([x["acc"] for x in ranked], c["acc"], False)
    t_rank = competition_rank([round(t, 1) for t in times], round(c["time"], 1), True)
    c_rank = competition_rank([round(x, 2) for x in costs], round(c["cost"], 2), True)
    leader = ranked[0]
    mean_score = sum(scores) / N
    same_cost = max(costs) - min(costs) < 0.005
    host = next((x for x in facts["order"] if x["sov"] and x["model"] != model), None)   # best self-hostable chain of another model
    own_sov = any(x["sov"] for x in facts["chains"] if x["model"] == model)
    label = b.chain_label(c)
    speech = "built-in audio" if c["speech"] == b.DIRECT_AUDIO else c["speech"]
    mlink = lambda name: f"{MODELS[name]['slug']}/{lslug}/"
    hub = f"../language/{lslug}/"
    agent = f"../language/{lslug}/ai-agent/"
    runs = previous_runs(model, c, L)      # the models this one replaced, in an archived snapshot; [] = no section
    prev = runs[0] if runs else None

    # ---- lead + comparison copy
    # Each point is a verb phrase ("is …" / "can …"), so any mix reads as one sentence after "It".
    good, bad = [], []
    (good if c["time"] < 10 else bad).append("is fast enough for phone calls" if c["time"] < 10 else "is too slow for live phone calls")
    if not same_cost and not PRICING_COMING_SOON:
        if c_rank == 1:
            good.append("is the cheapest of the " + str(N))
        elif c["cost"] >= max(costs) - 1e-9:
            bad.append("is costly")
    (good if own_sov else bad).append("can be self-hosted" if own_sov else "cannot be self-hosted")
    if good and bad:
        verdict = f"It {and_join(good)}, but {and_join(bad)}."
    else:
        verdict = f"It {and_join(good or bad)}."
    lead = (f"<strong>As of {month_year(L['updated'])}, {esc(model)} ranks #{rank} of {N} models on spoken {lang} questions.</strong> "
            f"{esc(verdict)}")

    level = "above average" if c["score"] > mean_score + 1 else "below average" if c["score"] < mean_score - 1 else "about average"
    speed_word = ("among the fastest" if t_rank <= max(1, math.ceil(N / 3)) else
                  "among the slowest" if t_rank > N - math.ceil(N / 3) else "mid-table on speed")
    contrast = "but" if (level == "below average") == (t_rank <= math.ceil(N / 3)) and level != "about average" else "and"
    phone = (" and well inside the 10-second limit for phone calls" if c["time"] <= 8 else
             " and inside the 10-second limit for phone calls" if c["time"] < 10 else " and over the 10-second limit for phone calls")
    if PRICING_COMING_SOON:
        cost_sentence = ""
    elif same_cost:
        cost_sentence = f"Every model was charged the same, about <strong>{b.money(c['cost'])}</strong> per 1,000 questions."
    else:
        word = "expensive" if c["cost"] >= max(costs) - 1e-9 else "cheap" if c_rank == 1 else "mid-priced"
        extra = f", the highest of the {N}" if word == "expensive" else f", the lowest of the {N}" if word == "cheap" else ""
        cost_sentence = f"It is <strong>{word}</strong> at about <strong>{b.money(c['cost'])}</strong> per 1,000 questions{extra}."
    if own_sov:
        host_sentence = "It <strong>can be self-hosted</strong>: its weights are open."
    elif host:
        d = host["score"] - c["score"]
        host_sentence = (f"It <strong>cannot be self-hosted</strong>. The best self-hostable chain, <strong>{esc(b.chain_label(host))}</strong>, "
                         f"scores {host['score']}, {abs(d)} points {'higher' if d > 0 else 'lower'}.")
    else:
        host_sentence = "It <strong>cannot be self-hosted</strong>, and no chain we tested can."
    compare_p1 = (f"<strong>{esc(model)}</strong> is <strong>{level}</strong> in {lang} accuracy (score {c['score']}, #{rank} of {N} models) "
                  f"{contrast} <strong>{speed_word}</strong>: it answers in <strong>{c['time']:.1f} seconds</strong>, #{t_rank} of {N}{phone}. "
                  + (f"{cost_sentence} " if cost_sentence else "") + host_sentence)
    compare_p2 = ""
    if prev:
        ds, dt = c["score"] - prev["score"], prev["time"] - c["time"]
        compare_p2 = (f'<p class="md-p2">Compared with <strong>{esc(prev["name"])}</strong>, which it replaced, {esc(model)} is '
                      + (f"<strong>{abs(ds)} point{'s' * (abs(ds) != 1)} {'higher' if ds > 0 else 'lower'}</strong>" if ds else "<strong>level</strong>")
                      + f" on the same {L['questions']} questions and answers <strong>{abs(dt):.1f} seconds {'faster' if dt >= 0 else 'slower'}</strong>.</p>")
    chips = []
    if t_rank <= max(1, math.ceil(N / 3)):
        chips.append(f"Among the fastest, #{t_rank} of {N}")
    if c["time"] < 10:
        chips.append("Phone-ready, under 10 s")
    chips.append("The most accurate of the " + str(N) if rank == 1 else f"{leader['score'] - c['score']} points below the leader")
    if PRICING_COMING_SOON:
        pass
    elif not same_cost and c["cost"] >= max(costs) - 1e-9:
        chips.append(f"Highest cost of the {N}")
    elif not same_cost and c_rank == 1:
        chips.append(f"Lowest cost of the {N}")
    if own_sov:
        chips.append("Open weights")

    # ---- hero
    voice = L["voice"]
    wave = re.search(r'<span class="wave".*?</span>', (SRC / "voice-note.frag").read_text(), re.S).group(0)
    stats = [
        (f"{lang} answer score" if False else "Answer score", str(c["score"]), f"#{rank} of {N} · out of 100"),
        ("Response time", f"{c['time']:.1f} s", f"{rank_phrase(t_rank, [round(t, 1) for t in times], round(c['time'], 1))} · median per answer"),
        ("Cost", PENDING, "per 1,000 questions") if PRICING_COMING_SOON else
        ("Cost", b.money(c["cost"]), f"{rank_phrase(c_rank, [round(x, 2) for x in costs], round(c['cost'], 2))} · per 1,000 questions"),
    ]
    stat_html = "\n".join(f'          <div class="md-stat{" pricing-pending" if v == PENDING else ""}"><span>{k}</span><b>{v}</b><small>{s}</small></div>'
                         for k, v, s in stats)

    # ---- comparison table
    others = [x for x in ranked if x["model"] != model][:3]
    cols = [c, *others]
    differs = lambda vals: max(vals) - min(vals) > 1e-9
    best_score = max(x["acc"] for x in cols) if differs([x["acc"] for x in cols]) else 9
    best_time = min(round(x["time"], 1) for x in cols) if differs([round(x["time"], 1) for x in cols]) else -1
    best_cost = min(round(x["cost"], 2) for x in cols) if differs([round(x["cost"], 2) for x in cols]) else -1

    def delta(value, ref, fmt, unit=""):
        if abs(value - ref) < 1e-9:
            return "same"
        return f"{'↑' if value > ref else '↓'} {fmt(abs(value - ref))}{unit}"

    def head_cell(x, first):
        mm = MODELS[x["model"]]
        r = ranked.index(x) + 1
        sub = f"This model, ranked #{r}" if first else f"Ranked #{r}"
        kind = ('<span class="dot sov"></span>Sovereign-deployable' if x["sov"] else '<span class="dot"></span>Private API')
        inner = (f'<img src="{ASSET}kinyarwanda/{b.logo24(x["model"])}.svg" alt="" width="16" height="16" />{esc(x["model"])}')
        title = f'<b>{inner}</b>' if first else f'<a href="{mlink(x["model"])}">{inner}</a>'
        return f'<div class="md-th{" me" if first else ""}">{title}<small>{sub}</small><small class="kind">{kind}</small></div>'

    def cell(first, text, sub, best):
        return f'<div class="md-td{" me" if first else ""}{" best" if best else ""}"><b>{text}</b><small>{sub}</small></div>'

    rows_html = [f'<div class="md-corner"></div>' + "".join(head_cell(x, i == 0) for i, x in enumerate(cols))]
    rows_html.append(f'<div class="md-th-label"><b>Answer score</b><small>matches the expert answer</small></div>' + "".join(
        cell(i == 0, str(x["score"]), f"#{rank} of {N}" if i == 0 else delta(x["score"], c["score"], str), x["acc"] >= best_score - 1e-9 and best_score != 9)
        for i, x in enumerate(cols)))
    rows_html.append('<div class="md-group">Speed and cost, not in the score</div>')
    rows_html.append(f'<div class="md-th-label"><b>Response time</b><small>median per answer</small></div>' + "".join(
        cell(i == 0, f"{x['time']:.1f} s", f"#{t_rank} of {N}" if i == 0 else delta(round(x["time"], 1), round(c["time"], 1), lambda v: f"{v:.1f}", " s"),
             round(x["time"], 1) <= best_time) for i, x in enumerate(cols)))
    if PRICING_COMING_SOON:
        rows_html.append('<div class="md-th-label pricing-pending"><b>Cost</b><small>per 1,000 questions</small></div>' + "".join(
            f'<div class="md-td pricing-pending{" me" if i == 0 else ""}"><b>{PENDING}</b><small></small></div>' for i in range(len(cols))))
    else:
        rows_html.append(f'<div class="md-th-label"><b>Cost</b><small>per 1,000 questions</small></div>' + "".join(
            cell(i == 0, b.money(x["cost"]), f"{rank_phrase(c_rank, [round(v, 2) for v in costs], round(c['cost'], 2))}" if i == 0
                 else delta(round(x["cost"], 2), round(c["cost"], 2), b.money), round(x["cost"], 2) <= best_cost) for i, x in enumerate(cols)))
    ncol = len(cols)
    table = (f'<div class="md-table-scroll"><div class="md-table" style="--cols:{ncol}" role="table" aria-label="{esc(model)} compared with the top models">\n'
             + "\n".join("            " + r for r in rows_html) + "\n          </div></div>")

    # ---- sample answers
    sample_data = samples_for(L, c)

    # ---- what changed since the previous version (language/_src/model-changed.tmpl); only when `prev` has data
    changed = ""
    if prev:
        ds, dt = c["score"] - prev["score"], prev["time"] - c["time"]
        chip = lambda text, tone="": f'<span class="md-chip-d {tone}">{text}</span>'
        unit = lambda v: f'{v:.1f}<small>s</small>'
        rows = [
            ("Answer score", "matches the expert answer", str(prev["score"]), str(c["score"]),
             chip(f"{abs(ds)} point{'s' * (abs(ds) != 1)} {'higher' if ds > 0 else 'lower'}" if ds else "unchanged", "good" if ds > 0 else "")),
            ("Response time", "median per answer", unit(prev["time"]), f"{c['time']:.1f} s",
             chip(f"{abs(dt):.1f} seconds {'faster' if dt > 0 else 'slower'}" if abs(dt) >= 0.05 else "unchanged", "good" if dt > 0 else "")),
        ]
        if PRICING_COMING_SOON:
            rows.append(("Cost", "per 1,000 questions", "", PENDING, ""))
        row_html = "\n".join(
            f'              <div class="md-change-row{" pricing-pending" if z == PENDING else ""}"><span><b>{k}</b><small>{sub}</small></span>'
            f'<em>{a}</em><i>{"" if z == PENDING else "→"}</i><strong>{z}</strong>{d}</div>' for k, sub, a, z, d in rows)
        notes = "".join(f'<li class="{tone}">{ICONS["check" if tone == "good" else "info"]}{esc(text)}</li>' for tone, text in prev["notes"])
        bars_data = [(x["name"], x["snapshot"]["month"], x["score"]) for x in reversed(runs)] + [(model, month_short(L["snapshot"]), c["score"])]
        top = max(v for _, _, v in bars_data)
        bars = "".join(f'<div class="md-bar{" me" if i == len(bars_data) - 1 else ""}"><b>{v}</b><span style="height:{v / top * 194:.0f}px"></span>'
                       f"<small>{esc(n)}<br />{esc(d)}</small></div>" for i, (n, d, v) in enumerate(bars_data))
        first = runs[-1]
        d0 = c["score"] - first["score"]
        caption = (f"{abs(d0)} point{'s' * (abs(d0) != 1)} {'higher' if d0 > 0 else 'lower'} than {first['name']} in {first['snapshot']['month']}"
                   if d0 else f"Level with {first['name']} in {first['snapshot']['month']}")
        speech = "built-in audio" if c["speech"] == b.DIRECT_AUDIO else f"{c['speech']} speech recognition"
        how = (f"Both with {speech}." if prev["like"] else
               f"{esc(b.chain_label(prev))} then, {esc(b.chain_label(c))} now: {esc(prev['name'])} did not run with {speech}.")
        replaced = f" on {esc(prev['on'])}" if prev.get("on") else ""
        changed = fill(TEMPLATE_CHANGED, {
            "prev": esc(prev["name"]), "lang": lang,
            "sub": (f"{esc(model)} replaced {esc(prev['name'])}{replaced}. Both answered the same {L['questions']} questions: "
                    f"{esc(prev['name'])} on {esc(prev['snapshot']['label'])}, {esc(model)} on {L['updated']}. {how}"),
            "rows": row_html,
            "notes": f'<div class="md-in"><small>In the answers</small><ul>{notes}</ul></div>' if notes else "",
            "bars": bars, "caption": caption})

    # ---- where you can run it
    def places(names: list[str]) -> str:
        marks = "".join(FLAGS.get(n, "") for n in names)
        return f'<b>{marks}<span>{esc(", ".join(names))}</span></b>'
    hosted_rows = ""
    if meta.get("hosted_in"):
        hosted_rows += f'<div class="md-fact"><span>{ICONS["cloud"]}Hosted in</span>{places(meta["hosted_in"])}</div>'
    if meta.get("zdr_in"):
        hosted_rows += f'<div class="md-fact"><span>{ICONS["shield"]}Zero Data Retention in</span>{places(meta["zdr_in"])}</div>'
    if hosted_rows:
        hosted_rows = f'<div class="md-facts">{hosted_rows}</div>'
    card1_title = "Hosted with zero data retention" if meta.get("zdr_in") else "Hosted by the provider"
    card1_body = (f"No data is kept, but requests leave {L['country']}." if meta.get("zdr_in") else
                  f"Requests go to {meta['maker']}’s cloud and leave {L['country']}. Check the provider’s data terms for your use.")
    host_label = b.chain_label(host) if host else ""
    run = f"""
          <article class="md-run">
            <div class="md-diagram md-dg-provider"><span class="md-region"><span>{esc(L['country'])}</span></span><span class="md-chip ok">Available now</span><span class="md-node md-a">{ICONS['mic']}<small>Your app</small></span><i class="md-arrow"></i><span class="md-node md-b">{ICONS['cloud']}<small>Provider cloud</small></span></div>
            <h3>{ICONS['cloud']}{card1_title}</h3>
            <p>{esc(card1_body)}</p>
            {hosted_rows}
            <small class="md-foot{' pricing-pending' if PRICING_COMING_SOON else ''}">{'Pricing coming soon' if PRICING_COMING_SOON else 'About ' + b.money(c['cost']) + ' per 1,000 questions'}</small>
          </article>
          <article class="md-run">
            <div class="md-diagram md-dg-region"><span class="md-region"><span>{esc(L['country'])}</span></span><span class="md-chip">{'Not yet for ' + esc(L['country']) if meta.get('in_region_note') else 'Ask us'}</span><span class="md-node md-a">{ICONS['mic']}<small>Your app</small></span><i class="md-arrow"></i><span class="md-node md-b">{ICONS['cloud']}<small>Cloud in {esc(L['country'])}</small></span></div>
            <h3>{ICONS['globe']}In-region or sovereign cloud</h3>
            <p>Data stays in a named country.</p>
            <p class="note">{esc(meta.get('in_region_note') or f'Ask us whether {model} can run in {L["country"]}.')}</p>
            <a class="md-link" href="{CONTACT}">Talk to us about on-prem{ICONS['chev']}</a>
          </article>
          <article class="md-run">
            <div class="md-diagram md-dg-self"><span class="md-region"><span>{ICONS['lock']}Your network</span></span><span class="md-chip{' ok' if own_sov else ''}">{'Open weights' if own_sov else 'Not for ' + esc(model)}</span><span class="md-node md-a">{ICONS['mic']}<small>Your app</small></span><i class="md-arrow"></i><span class="md-node md-b">{ICONS['server']}<small>Your servers</small></span></div>
            <h3>{ICONS['shield']}Self-hosted on your own servers</h3>
            <p>Nothing leaves your network. Open-weight chains only.</p>
            {('<div class="md-best"><small>Best chain you can host yourself</small><a href="' + mlink(host['model']) + '"><img src="' + ASSET + 'kinyarwanda/' + b.logo24(host['model']) + '.svg" alt="" width="16" height="16" />' + esc(host_label) + '</a><small>Score ' + str(host['score']) + ', open weights</small></div>') if (host and not own_sov) else ('<div class="md-best"><small>You can host this chain yourself</small><b>' + esc(label) + '</b><small>Score ' + str(c['score']) + ', open weights</small></div>' if own_sov else '')}
            <a class="md-link" href="{CONTACT}">Ask us about hardware and cost{ICONS['chev']}</a>
          </article>"""

    # ---- planet
    full = c["eco_full"]
    covered = full.get("coverage") == "text_model_only"
    ref = host if (host and not own_sov) else None
    ref_full = ref["eco_full"] if ref else None
    ref_cov = bool(ref_full and ref_full.get("coverage") == "text_model_only")
    cfg = {"subject": {} if PRICING_COMING_SOON else {"cost": c["cost"]}, "ref": None, "perMonth": 50000}
    if covered:
        v = full["co2e_g_per_1000"]
        water_l, energy_kwh = full["water_ml_per_1000"] / 1000, full["energy_wh_per_1000"] / 1000
        cfg["subject"].update({"co2e": v["value"], "waterL": water_l, "energyKwh": energy_kwh})
        conf = (full.get("confidence") or ["low"])[0]
        lo, hi = v["min"], v["max"]
        pos = 0 if hi <= lo else (v["value"] - lo) / (hi - lo)
        tree_min = v["value"] / (21000 / 525600)
        led_min = full["energy_wh_per_1000"] / 10 * 60
        planet_left = f"""
          <div class="md-eco">
            <div class="md-eco-head">
              <div>
                <p class="md-eco-cap">{ICONS['leaf']}Per 1,000 questions · {esc(label)}</p>
                <p class="md-eco-big"><b>{v['value']:.1f} g</b><small>CO₂e</small></p>
                <div class="md-range"><i style="left:{pos * 100:.0f}%"></i></div>
                <p class="md-eco-cap2">Likely {lo:.1f} to {hi:.1f} g · confidence: {esc(conf)}</p>
              </div>
              {eco_art()}
            </div>
            <div class="md-eco-tiles"><div><span>{ICONS['drop']}Water</span><b>{full['water_ml_per_1000']:.0f} mL</b></div><div><span>{ICONS['bolt']}Energy</span><b>{full['energy_wh_per_1000']:.0f} Wh</b></div></div>
            <div class="md-eco-chips"><span>{ICONS['leaf']}≈ {tree_min:.0f} minutes of one tree’s CO₂ uptake</span><span>{ICONS['bulb']}≈ {led_min:.0f} minutes of a 10 W LED bulb</span></div>
            <p class="md-eco-note">Estimate for the language-model step only: speech recognition and voices are not in it yet.</p>
            <a class="md-link plain" href="../ecocost/">How this is estimated (ecocost)</a>
          </div>"""
    else:
        reason = ("Direct-audio inference is outside the current EcoCost scope." if c["speech"] == b.DIRECT_AUDIO
                  else "The public run records for this chain contain no EcoCost result.")
        planet_left = f"""
          <div class="md-eco">
            <p class="md-eco-cap">{ICONS['leaf']}Per 1,000 questions · {esc(label)}</p>
            <p class="md-eco-big"><b>Not covered</b></p>
            <p class="md-eco-note">{esc(reason)} {'There is' if PRICING_COMING_SOON else 'We show cost, but'} no CO₂e, water or energy figure for this chain.</p>
            <a class="md-link plain" href="../ecocost/">How this is estimated (ecocost)</a>
          </div>"""
    if ref:
        cfg["ref"] = {"label": host_label, **({} if PRICING_COMING_SOON else {"cost": ref["cost"]})}
        if ref_cov and covered:
            rv = ref_full["co2e_g_per_1000"]["value"]
            cfg["ref"].update({"co2e": rv, "waterL": ref_full["water_ml_per_1000"] / 1000, "energyKwh": ref_full["energy_wh_per_1000"] / 1000})
    tiles = [("cost", "coin", "Cost"), ("co2e", "leaf", "CO₂e"), ("waterL", "drop", "Water"), ("energyKwh", "bolt", "Energy")]
    tiles_html = "".join(
        (f'<div class="md-vol-tile pricing-pending" data-k="{k}"><span>{ICONS[i]}{n}</span><b>{PENDING}</b><div class="md-track"><i></i></div><small></small></div>'
         if k == "cost" and PRICING_COMING_SOON else
         f'<div class="md-vol-tile" data-k="{k}"><span>{ICONS[i]}{n}</span><b>—</b><div class="md-track"><i></i></div><small></small></div>')
        for k, i, n in tiles if k == "cost" or covered)
    ref_note = (f'<p class="md-vol-note"><i class="dot sov"></i>{esc(host_label)}, the best chain you can host yourself. Grey: {esc(label)}.</p>' if ref else
                f'<p class="md-vol-note">Figures scale linearly with the number of questions.</p>')
    planet_right = f"""
          <div class="md-volume">
            <h3>At your volume</h3>
            <div class="md-vol-row"><span>Questions per month</span><b id="mdVol">50,000</b></div>
            <input class="md-range-input" id="mdRange" type="range" min="0" max="100" step="0.1" value="74" aria-label="Questions per month" />
            <div class="md-vol-tiles">{tiles_html}</div>
            {ref_note}
          </div>"""

    # ---- FAQ
    faq = []
    faq.append((f"How good is {model} at {lang}?",
                f"As of {month_year(L['updated'])}, {model} with {speech} speech recognition scores {c['score']} out of 100 on the {lang} "
                f"questions, #{rank} of {N} models. It answers in {c['time']:.1f} seconds." if c["speech"] != b.DIRECT_AUDIO else
                f"As of {month_year(L['updated'])}, {model} listening to the audio directly scores {c['score']} out of 100 on the {lang} "
                f"questions, #{rank} of {N} models. It answers in {c['time']:.1f} seconds."))
    if meta["maker"] == "OpenAI":
        faq.append((f"Does ChatGPT understand {lang}?",
                    f"ChatGPT is OpenAI’s app; we test its models directly. {model} scored {c['score']} on spoken {lang} questions, #{rank} of {N}."))
    else:
        faq.append((f"Does {model} understand {lang}?",
                    (f"{model} scored highest of the {N} models we tested: {c['score']} out of 100 on spoken {lang} questions "
                     f"with {speech}." if rank == 1 else
                     f"Partly. {model} scored {c['score']} out of 100 on spoken {lang} questions with {speech}, #{rank} of {N} models; "
                     f"{leader['model']} scored {leader['score']}.")))
    if prev:
        ds = c["score"] - prev["score"]
        faq.append((f"Is {model} better than {prev['name']} for {lang}?",
                    (f"On the same {L['questions']} questions it scores {abs(ds)} point{'s' * (abs(ds) != 1)} {'higher' if ds > 0 else 'lower'} "
                     if ds else f"On the same {L['questions']} questions it scores the same ") +
                    f"({prev['score']} to {c['score']}, {prev['snapshot']['label']} to {L['updated']}) "
                    f"and answers in {c['time']:.1f} s instead of {prev['time']:.1f} s."))
    faq.append((f"Can I run {model} on my own servers?",
                (f"Yes. {model} has open weights, so you can host it yourself, together with an open speech model such as Omnilingual." if own_sov else
                 f"No. {model} is only available from {meta['maker']}’s cloud. " + (f"The best chain you can host yourself is {host_label} (score {host['score']})." if host else "None of the chains we tested can be self-hosted."))))
    eco_text = (f"Its estimated footprint is {full['co2e_g_per_1000']['value']:.1f} g CO₂e per 1,000 questions for the language-model step (confidence: {(full.get('confidence') or ['low'])[0]})." if covered
                else "Its carbon footprint is not covered by our EcoCost estimate yet.")
    faq.append((f"What does {model} cost, and what is its carbon footprint?",
                (f"Pricing is coming soon. {eco_text}" if PRICING_COMING_SOON else
                 f"On Gooey.AI the observed charge for {label} was {b.money(c['cost'])} per 1,000 questions. {eco_text}")))
    faq.append(("How often are these results updated?",
                f"The numbers on this page come from the {L['updated']} run of {L['questions']} questions. We update the page when we re-run the benchmark."))
    faq_items = "\n".join(f"            <details{' open' if i == 0 else ''}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for i, (q, a) in enumerate(faq))

    # ---- footer: same model in other languages
    items = []
    cfg_langs = json.loads((SRC / "languages.json").read_text())
    slug_by_name = {x["lang"]: s for s, x in langs.items()}
    for name in cfg_langs["languages"]:
        if name == lang:
            continue
        s = slug_by_name.get(name)
        if s and model in langs[s]["best"]:
            items.append(f'<li><a href="{mslug}/{s}/">{name}</a></li>')
        else:
            items.append(f"<li>{name}</li>")
    items.append(f'<li><strong>{cfg_langs["all"]}</strong></li>')
    other_languages = f'<ul class="language-list" aria-label="{esc(model)} in other languages">{"".join(items)}</ul>'

    slots = {
        "header": b.HEADER_HTML.format(title=f"{model} in {lang}").rstrip("\n"),
        "lang": lang, "model": esc(model), "hub": hub, "agent": agent, "bulk_url": L["bulk_url"],
        "meta_line": f'<img src="{ASSET}kinyarwanda/{b.logo24(model)}.svg" alt="" width="16" height="16" />{esc(meta["maker"])}<span>·</span>{meta["kind"]}<span>·</span>Evaluated {L["updated"]}',
        "lead": lead, "stats": stat_html, "wave": wave, "vn_time": voice["time"], "vn_text": voice["text"], "vn_sub": voice["sub"],
        "compare_p1": compare_p1, "compare_p2": compare_p2, "chips": "".join(f"<span>{esc(x)}</span>" for x in chips),
        "table_title": f"Against the top {len(others)}",
        "table": table, "updated": L["updated"], "questions": str(L["questions"]), "docs_eval": DOCS_EVAL,
        "data_csv": f"../language/data/{L['code']}/evaluation-latest.csv", "contact": CONTACT, "api": API,
        "sample_intro": (f"Three of the {L['questions']} questions. Answers are from {esc(model)} with {esc(speech)}"
                         f"{' speech recognition' if c['speech'] != b.DIRECT_AUDIO else ''}, each graded against an expert’s."),
        "changed": changed, "run": run, "planet_left": planet_left, "planet_right": planet_right,
        "faq_items": faq_items, "cta_title": f"Build a {lang} agent with {model}",
        "cta_text": f"Start from {esc(model)} with {esc(speech)}, the best-scoring chain for this model. Free to start.",
        "other_title": f"{model} in other languages", "other_languages": other_languages,
        "email": f"Email me when {model}’s {lang} results change",
        "art": hero_art(),
    }
    body = (SRC / "model.tmpl").read_text()
    for key, value in slots.items():
        body = body.replace("{{%s}}" % key, value)
    left = re.findall(r"\{\{\w+\}\}", body)
    if left:
        raise SystemExit(f"{mslug}/{lslug}: unfilled template slots {sorted(set(left))}")
    base = f"{model} in {lang}: Accuracy, Speed & Cost"
    title = seo.fit(base + seo.BRAND, base, f"{model} in {lang}{seo.BRAND}", hi=seo.TITLE_MAX, what=f"{model} in {lang} title")
    how = f"How {model} does on spoken {lang} questions: score {c['score']} out of 100 (#{rank} of {N} models), {c['time']:.1f} s response"
    # While pricing is "Coming soon" the description leaves cost out (see PRICING_COMING_SOON).
    hosting = "it can be self-hosted" if own_sov else "it cannot be self-hosted"
    description = seo.fit(*([f"{how}, and {hosting}."] if PRICING_COMING_SOON else [f"{how}, {b.money(c['cost'])} per 1,000 questions."]),
                          f"{how}.",
                          f"{model} on spoken {lang} questions: {c['score']}/100 (#{rank} of {N} models), {c['time']:.1f} s response.",
                          lo=seo.DESC_MIN, hi=seo.DESC_MAX, what=f"{model} in {lang} description")
    path = f"models/{mslug}/{lslug}"
    card = {"eyebrow": f"{lang} evaluation · {meta['maker']}", "title": f"{model} in {lang}", "lead": ["Best chain", label],
            "stats": [[f"{lang} Index", str(c["score"]), "/ 100", f"#{rank} of {N} models"],
                      ["Reply time", f"{c['time']:.1f}", "s", f"median, #{t_rank} of {N}"],
                      ["Self-hosting", "Yes" if own_sov else "No", "", "open weights" if meta.get("open") else "proprietary model"]],
            "visual": {"kind": "logo", "src": f"language/assets/kinyarwanda/{b.js_dict('LOGO_FILES')[model]}.svg"}}
    image = seo.og_image(path, card, f"{model} in {lang}: {lang} Index {c['score']} out of 100, #{rank} of {N} models, "
                                     f"with a {c['time']:.1f} s median reply.")
    lang_page = json.loads((SRC / lslug / "page.json").read_text())
    graph = [seo.ORG, seo.webpage(path, title, description, image, L["snapshot"],
                                  seo.language(lang, lang_page.get("endonym"))),
             seo.breadcrumbs(path, [("Home", seo.SITE), seo.EVALS, (lang, seo.url(f"language/{lslug}")), (model, None)]),
             *seo.faq(path, body)]
    tags = seo.head(path=path, title=title, description=description, og_title=base, image=image, graph=graph)
    head = HEAD.format(seo=tags, header_css=b.HEADER_CSS)
    config = {"lang": lang, "model": model, "samples": sample_data, "who": {"model": model, "logo": b.js_dict("LOGO_FILES")[model]},
              "volume": cfg}
    return head + body.rstrip("\n") + "\n" + TAIL.format(config=json.dumps(config, ensure_ascii=False, separators=(", ", ": ")))


def pages() -> dict[pathlib.Path, str]:
    out = {}
    for model, lslug in model_slugs():
        out[ROOT / "models" / MODELS[model]["slug"] / lslug / "index.html"] = render_model(model, lslug)
    return out
