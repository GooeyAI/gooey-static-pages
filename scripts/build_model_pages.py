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
have yet is simply left out; the Figma frame's translation / transcription scores and "what changed since the
previous version" appear when language/_src/models.json gives a `previous` block for the model (see below).

models.json "previous" (optional, per model):

    "previous": {"name": "GPT-5.5", "replaced": "Feb 12, 2026",
                 "history": [["GPT-5", "Aug 2025", 74], ["GPT-5.5", "Feb 2026", 81]],
                 "languages": {"kinyarwanda": {"score": 81, "time": 8.4, "cost": 52.0,
                                               "notes": ["Stays in Kinyarwanda more often."]}}}
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

ROOT, LANG, SRC = b.ROOT, b.LANG, b.SRC
csv.field_size_limit(10**8)
MODELS = json.loads((SRC / "models.json").read_text(encoding="utf-8"))
DOCS_EVAL = "https://docs.gooey.ai/speech-and-language/how-to-use-asr/how-to-create-language-evaluation-for-asr"
CONTACT = "https://gooey.ai/contact/"
API = "https://gooey.ai/api/"
esc = html.escape

HEAD = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <!-- GOOEY-BASE-HREF -->
    <base href="../../" />
    <title>{title} | Gooey.AI</title>
    <meta
      name="description"
      content="{description}"
    />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="{title} | Gooey.AI" />
    <meta
      property="og:description"
      content="{description}"
    />
    <meta property="og:url" content="https://gooey.ai/models/{mslug}/{lslug}" />
    <meta property="og:site_name" content="Gooey.AI" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
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
    "chev": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 3.5 4.5 4.5L6 12.5"/></svg>',
}


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
        out[slug] = {"slug": slug, "lang": a["lang"], "country": a["country"], "code": a["code"], "snapshot": a["snapshot"],
                     "updated": page["updated"], "questions": page["questions"], "bulk_url": page["hero"]["bulk_url"],
                     "voice": page["hero"]["voice"], "flag": page["flag"], "facts": facts, "best": best, "ranked": ranked}
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
    prev = (meta.get("previous") or {})
    prev_l = (prev.get("languages") or {}).get(lslug)

    # ---- lead + comparison copy
    good, bad = [], []
    (good if c["time"] < 10 else bad).append("fast enough for phone calls" if c["time"] < 10 else "too slow for live phone calls")
    if not same_cost:
        if c_rank == 1:
            good.append("the cheapest of the " + str(N))
        elif c["cost"] >= max(costs) - 1e-9:
            bad.append("costly")
    (good if own_sov else bad).append("can be self-hosted" if own_sov else "cannot be self-hosted")
    if good and bad:
        verdict = f"It is {and_join(good)}, but {and_join(bad)}."
    else:
        verdict = f"It is {and_join(good or bad)}."
    lead = (f"As of {month_year(L['updated'])}, <strong>{esc(model)}</strong> ranks #{rank} of {N} models on spoken {lang} questions. "
            f"{esc(verdict)}")

    level = "above average" if c["score"] > mean_score + 1 else "below average" if c["score"] < mean_score - 1 else "about average"
    speed_word = ("among the fastest" if t_rank <= max(1, math.ceil(N / 3)) else
                  "among the slowest" if t_rank > N - math.ceil(N / 3) else "mid-table on speed")
    contrast = "but" if (level == "below average") == (t_rank <= math.ceil(N / 3)) and level != "about average" else "and"
    phone = (" and well inside the 10-second limit for phone calls" if c["time"] <= 8 else
             " and inside the 10-second limit for phone calls" if c["time"] < 10 else " and over the 10-second limit for phone calls")
    if same_cost:
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
                  f"{cost_sentence} {host_sentence}")
    compare_p2 = ""
    if prev_l:
        ds, dt, dc = c["score"] - prev_l["score"], prev_l["time"] - c["time"], prev_l["cost"] - c["cost"]
        compare_p2 = (f'<p class="md-p2">Compared with <strong>{esc(prev["name"])}</strong>, which it replaced, {esc(model)} is '
                      f"<strong>{abs(ds)} points {'higher' if ds >= 0 else 'lower'}</strong>. It answers <strong>{abs(dt):.1f} seconds "
                      f"{'faster' if dt >= 0 else 'slower'}</strong> and costs <strong>{b.money(abs(dc))} {'less' if dc >= 0 else 'more'}</strong> "
                      "per 1,000 questions.</p>")
    chips = []
    if t_rank <= max(1, math.ceil(N / 3)):
        chips.append(f"Among the fastest, #{t_rank} of {N}")
    if c["time"] < 10:
        chips.append("Phone-ready, under 10 s")
    chips.append("The most accurate of the " + str(N) if rank == 1 else f"{leader['score'] - c['score']} points below the leader")
    if not same_cost and c["cost"] >= max(costs) - 1e-9:
        chips.append(f"Highest cost of the {N}")
    elif not same_cost and c_rank == 1:
        chips.append(f"Lowest cost of the {N}")
    if own_sov:
        chips.append("Open weights")

    # ---- hero
    voice = L["voice"]
    wave = re.search(r'<span class="wave".*?</span>', (SRC / "body.tmpl").read_text(), re.S).group(0)
    stats = [
        (f"{lang} answer score" if False else "Answer score", str(c["score"]), f"#{rank} of {N} · out of 100"),
        ("Response time", f"{c['time']:.1f} s", f"{rank_phrase(t_rank, [round(t, 1) for t in times], round(c['time'], 1))} · median per answer"),
        ("Cost", b.money(c["cost"]), f"{rank_phrase(c_rank, [round(x, 2) for x in costs], round(c['cost'], 2))} · per 1,000 questions"),
    ]
    stat_html = "\n".join(f'          <div class="md-stat"><span>{k}</span><b>{v}</b><small>{s}</small></div>' for k, v, s in stats)

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
    rows_html.append(f'<div class="md-th-label"><b>Cost</b><small>per 1,000 questions</small></div>' + "".join(
        cell(i == 0, b.money(x["cost"]), f"{rank_phrase(c_rank, [round(v, 2) for v in costs], round(c['cost'], 2))}" if i == 0
             else delta(round(x["cost"], 2), round(c["cost"], 2), b.money), round(x["cost"], 2) <= best_cost) for i, x in enumerate(cols)))
    ncol = len(cols)
    table = (f'<div class="md-table-scroll"><div class="md-table" style="--cols:{ncol}" role="table" aria-label="{esc(model)} compared with the top models">\n'
             + "\n".join("            " + r for r in rows_html) + "\n          </div></div>")
    if prev_l:
        pass  # the previous version's column is shown in the "what changed" block below

    # ---- sample answers
    sample_data = samples_for(L, c)

    # ---- previous version block
    changed = ""
    if prev_l:
        ds, dt, dc = c["score"] - prev_l["score"], prev_l["time"] - c["time"], prev_l["cost"] - c["cost"]
        chip = lambda text, tone="": f'<span class="md-chip-d {tone}">{text}</span>'
        rows = [
            ("Answer score", "matches the expert answer", str(prev_l["score"]), str(c["score"]),
             chip(f"{abs(ds)} points {'higher' if ds > 0 else 'lower'}" if ds else "unchanged", "good" if ds > 0 else "")),
            ("Response time", "median per answer", f"{prev_l['time']:.1f} s", f"{c['time']:.1f} s",
             chip(f"{abs(dt):.1f} seconds {'faster' if dt > 0 else 'slower'}" if abs(dt) >= 0.05 else "unchanged", "good" if dt > 0 else "")),
            ("Cost", "per 1,000 questions", b.money(prev_l["cost"]), b.money(c["cost"]),
             chip(f"{b.money(abs(dc))} {'cheaper' if dc > 0 else 'dearer'}" if abs(dc) >= 0.005 else "unchanged", "good" if dc > 0 else "")),
        ]
        row_html = "\n".join(f'<div class="md-change-row"><span><b>{k}</b><small>{s}</small></span><em>{a}</em><i>→</i><strong>{z}</strong>{d}</div>'
                             for k, s, a, z, d in rows)
        notes = "".join(f"<li>{esc(n)}</li>" for n in prev_l.get("notes", []))
        history = [*prev.get("history", []), [model, re.sub(r"^([A-Za-z]{3}) \d+, (\d{4})$", r"\1 \2", L["updated"]), c["score"]]]
        top = max(v for _, _, v in history)
        bars = "".join(f'<div class="md-bar{" me" if i == len(history) - 1 else ""}"><span style="height:{v / top * 100:.0f}%"><b>{v}</b></span>'
                       f"<small>{esc(n)}<br />{esc(d)}</small></div>" for i, (n, d, v) in enumerate(history))
        changed = f"""
      <section class="md-section" aria-labelledby="changed-title">
        <div class="container">
          <h2 id="changed-title">What changed since {esc(prev['name'])}</h2>
          <p class="md-sub">{esc(model)} replaced {esc(prev['name'])} on {esc(prev['replaced'])}. We re-ran the same {L['questions']} questions on {L['updated']}.</p>
          <div class="md-change">
            <div class="md-change-card">
{row_html}
              {('<div class="md-in"><small>In the answers</small><ul>' + notes + '</ul></div>') if notes else ''}
            </div>
            <div class="md-change-card md-versions"><b>{lang} answer score by version</b><div class="md-bars">{bars}</div></div>
          </div>
        </div>
      </section>"""

    # ---- where you can run it
    hosted_rows = ""
    if meta.get("hosted_in"):
        hosted_rows += (f'<div class="md-fact"><span>{ICONS["globe"]}Hosted in</span><b>{esc(", ".join(meta["hosted_in"]))}</b></div>')
    if meta.get("zdr_in"):
        hosted_rows += (f'<div class="md-fact"><span>{ICONS["shield"]}Zero Data Retention in</span><b>{esc(", ".join(meta["zdr_in"]))}</b></div>')
    card1_title = "Hosted with zero data retention" if meta.get("zdr_in") else "Hosted by the provider"
    card1_body = (f"No data is kept, but requests leave {L['country']}." if meta.get("zdr_in") else
                  f"Requests go to {meta['maker']}’s cloud and leave {L['country']}. Check the provider’s data terms for your use.")
    host_label = b.chain_label(host) if host else ""
    run = f"""
          <article class="md-run">
            <div class="md-diagram"><span class="md-chip ok">Available now</span><div class="md-flow"><span class="md-node">{ICONS['mic']}<small>Your app</small></span><i></i><span class="md-node">{ICONS['cloud']}<small>Provider cloud</small></span></div></div>
            <h3>{ICONS['cloud']}{card1_title}</h3>
            <p>{esc(card1_body)}</p>
            {hosted_rows}
            <small class="md-foot">About {b.money(c['cost'])} per 1,000 questions</small>
          </article>
          <article class="md-run">
            <div class="md-diagram"><span class="md-chip">{'Not yet for ' + esc(L['country']) if meta.get('in_region_note') else 'Ask us'}</span><div class="md-flow dim"><span class="md-node">{ICONS['mic']}<small>Your app</small></span><i></i><span class="md-node">{ICONS['cloud']}<small>Cloud in {esc(L['country'])}</small></span></div></div>
            <h3>{ICONS['globe']}In-region or sovereign cloud</h3>
            <p>Data stays in a named country.</p>
            <p class="note">{esc(meta.get('in_region_note') or f'Ask us whether {model} can run in {L["country"]}.')}</p>
            <a class="md-link" href="{CONTACT}">Talk to us about on-prem{ICONS['chev']}</a>
          </article>
          <article class="md-run">
            <div class="md-diagram self"><span class="md-chip{' ok' if own_sov else ''}">{'Open weights' if own_sov else 'Not for ' + esc(model)}</span><div class="md-flow"><span class="md-node">{ICONS['mic']}<small>Your app</small></span><i></i><span class="md-node on">{ICONS['server']}<small>Your servers</small></span></div></div>
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
    cfg = {"subject": {"cost": c["cost"]}, "ref": None, "perMonth": 50000}
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
              <div class="md-eco-art"></div>
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
            <p class="md-eco-note">{esc(reason)} We show cost, but no CO₂e, water or energy figure for this chain.</p>
            <a class="md-link plain" href="../ecocost/">How this is estimated (ecocost)</a>
          </div>"""
    if ref:
        cfg["ref"] = {"label": host_label, "cost": ref["cost"]}
        if ref_cov and covered:
            rv = ref_full["co2e_g_per_1000"]["value"]
            cfg["ref"].update({"co2e": rv, "waterL": ref_full["water_ml_per_1000"] / 1000, "energyKwh": ref_full["energy_wh_per_1000"] / 1000})
    tiles = [("cost", "coin", "Cost"), ("co2e", "leaf", "CO₂e"), ("waterL", "drop", "Water"), ("energyKwh", "bolt", "Energy")]
    tiles_html = "".join(
        f'<div class="md-vol-tile" data-k="{k}"><span>{ICONS[i]}{n}</span><b>—</b><div class="md-track"><i></i></div><small></small></div>'
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
                    f"Partly. {model} scored {c['score']} out of 100 on spoken {lang} questions with {speech}, #{rank} of {N} models; "
                    f"{leader['model']} scored {leader['score']}."))
    if prev_l:
        ds = c["score"] - prev_l["score"]
        faq.append((f"Is {model} better than {prev['name']} for {lang}?",
                    f"On our questions it scores {abs(ds)} points {'higher' if ds >= 0 else 'lower'} ({prev_l['score']} to {c['score']}) "
                    f"and answers in {c['time']:.1f} s instead of {prev_l['time']:.1f} s."))
    faq.append((f"Can I run {model} on my own servers?",
                (f"Yes. {model} has open weights, so you can host it yourself, together with an open speech model such as Omnilingual." if own_sov else
                 f"No. {model} is only available from {meta['maker']}’s cloud. " + (f"The best chain you can host yourself is {host_label} (score {host['score']})." if host else "None of the chains we tested can be self-hosted."))))
    eco_text = (f"Its estimated footprint is {full['co2e_g_per_1000']['value']:.1f} g CO₂e per 1,000 questions for the language-model step (confidence: low)." if covered
                else "Its carbon footprint is not covered by our EcoCost estimate yet.")
    faq.append((f"What does {model} cost, and what is its carbon footprint?",
                f"On Gooey.AI the observed charge for {label} was {b.money(c['cost'])} per 1,000 questions. {eco_text}"))
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
        "table_title": f"Against the top {len(others)}" + (f" and {prev['name']}" if prev_l else ""),
        "table": table, "updated": L["updated"], "questions": str(L["questions"]), "docs_eval": DOCS_EVAL,
        "data_csv": f"../language/data/{L['code']}/evaluation-latest.csv", "contact": CONTACT, "api": API,
        "sample_intro": (f"Three of the {L['questions']} questions. Answers are from {esc(model)} with {esc(speech)}"
                         f"{' speech recognition' if c['speech'] != b.DIRECT_AUDIO else ''}, each graded against an expert’s."),
        "changed": changed, "run": run, "planet_left": planet_left, "planet_right": planet_right,
        "faq_items": faq_items, "cta_title": f"Build a {lang} agent with {model}",
        "cta_text": f"Start from {esc(model)} with {esc(speech)}, the best-scoring chain for this model. Free to start.",
        "other_title": f"{model} in other languages", "other_languages": other_languages,
        "email": f"Email me when {model}’s {lang} results change",
        "art": '<div class="md-art" role="img" aria-label="Illustration of a phone showing a voice note">Illustration to come</div>',
    }
    body = (SRC / "model.tmpl").read_text()
    for key, value in slots.items():
        body = body.replace("{{%s}}" % key, value)
    left = re.findall(r"\{\{\w+\}\}", body)
    if left:
        raise SystemExit(f"{mslug}/{lslug}: unfilled template slots {sorted(set(left))}")
    title = f"{model} in {lang}: Accuracy, Speed & Cost"
    description = (f"How {model} does on spoken {lang} questions: score {c['score']} out of 100 (#{rank} of {N} models), "
                   f"{c['time']:.1f} s response, {b.money(c['cost'])} per 1,000 questions.")
    head = HEAD.format(title=esc(title, quote=False), description=esc(description), mslug=mslug, lslug=lslug, header_css=b.HEADER_CSS)
    config = {"lang": lang, "model": model, "samples": sample_data, "who": {"model": model, "logo": b.js_dict("LOGO_FILES")[model]},
              "volume": cfg}
    return head + body.rstrip("\n") + "\n" + TAIL.format(config=json.dumps(config, ensure_ascii=False, separators=(", ", ": ")))


def pages() -> dict[pathlib.Path, str]:
    out = {}
    for model, lslug in model_slugs():
        out[ROOT / "models" / MODELS[model]["slug"] / lslug / "index.html"] = render_model(model, lslug)
    return out
