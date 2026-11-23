#!/usr/bin/env python3
"""Build the /models/<model>/ overview pages ("Claude Sonnet 5: Languages, Speed & Cost").

Called by scripts/build_language_pages.py (run that one; it builds every generated page). One page is written for
every model in language/_src/models.json that has results in at least one language: models/<model-slug>/index.html.

The page shows one language at a time ("Show results for"); every language's numbers are written into the HTML and
language/assets/language-model-overview.js only switches which one is visible (and the "Build an agent" link). The
default is the language where the model ranks best. `#<language-slug>` in the URL picks another.

Everything is computed from the same data as the /models/<model>/<language> pages (scripts/build_model_pages.py):
the language's summary CSV (Index, response time), its EcoCost JSON (CO2e), archived snapshots (Index over time) and
models.json (maker, open weights, hosting regions, the models it replaced). A block with no data is left out:

  * "Where it runs" needs models.json "hosted_in" / "zdr_in", or open weights;
  * "Index over time" needs an archived snapshot of the language, with the same questions, in which this model (or
    one it replaced, models.json "replaces") ran;
  * the carbon-footprint chart needs at least two models with an EcoCost figure in the language.

Monetary pricing is "Coming soon" here too (build_model_pages.PRICING_COMING_SOON).
"""

from __future__ import annotations

import html
import json
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_language_pages as b  # noqa: E402
import build_model_pages as mp  # noqa: E402
import seo  # noqa: E402

ROOT, SRC = b.ROOT, b.SRC
MODELS = mp.MODELS
ICONS = mp.ICONS
ASSET = mp.ASSET
PENDING = mp.PENDING
esc = html.escape

TAIL = """
    <script>
      window.MODEL_OVERVIEW = {config};
    </script>
    <script src="../language/assets/language-model-overview.js"></script>
    <script src="../language/assets/language-links.js"></script>
  </body>
</html>
"""

# Round flags for the evaluated languages' countries (page.json "flag")
_R = '<svg class="mo-flag" viewBox="0 0 16 16" aria-hidden="true"><clipPath id="mf{id}"><circle cx="8" cy="8" r="8"/></clipPath><g clip-path="url(#mf{id})">{body}</g><circle cx="8" cy="8" r="7.75" fill="none" stroke="rgba(0,0,0,.12)" stroke-width=".5"/></svg>'
LANG_FLAGS = {
    "rw": _R.format(id="rw", body='<rect width="16" height="16" fill="#20603d"/><rect width="16" height="10.7" fill="#fad201"/><rect width="16" height="8" fill="#00a1de"/><circle cx="12" cy="3.6" r="1.6" fill="#fad201"/>'),
    "ke": _R.format(id="ke", body='<rect width="16" height="16" fill="#006600"/><rect width="16" height="10" fill="#fff"/><rect width="16" height="9" fill="#bb0000"/><rect width="16" height="6" fill="#fff"/><rect width="16" height="5.4" fill="#000"/><ellipse cx="8" cy="8" rx="2" ry="4" fill="#bb0000"/>'),
    "ng": _R.format(id="ng", body='<rect width="16" height="16" fill="#008751"/><rect x="5.33" width="5.34" height="16" fill="#fff"/>'),
}
ICON_LANG = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 3.5h7M5.5 2v1.5M7.5 3.5c-.6 2.6-2.4 4.6-5 5.6M4 5.6c.8 1.4 2 2.6 3.6 3.2M9 14l2.5-6 2.5 6M9.8 12.2h3.4"/></svg>'
ICON_CHART = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 13.5h12M4 11V7M7 11V4M10 11V8M13 11V5.5"/></svg>'
ICON_TARGET = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><circle cx="8" cy="8" r="6"/><circle cx="8" cy="8" r="3.2"/><circle cx="8" cy="8" r=".6" fill="currentColor"/></svg>'
ICON_CLOCK = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="8.8" r="5.4"/><path d="M8 6v3l1.8 1.2M6.5 1.8h3"/></svg>'
ICON_CAL = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.2" y="3" width="11.6" height="10.8" rx="1.6"/><path d="M2.2 6.4h11.6M5.4 1.8v2.4M10.6 1.8v2.4"/></svg>'
ICON_DOWN = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m4 6 4 4 4-4"/></svg>'


def num(v: float) -> str:
    """A CO2e figure in grams: one decimal under 10, whole grams above."""
    return f"{v:.1f}" if v < 10 else f"{v:.0f}"


def co2(c: dict) -> float | None:
    full = c.get("eco_full") or {}
    return full["co2e_g_per_1000"]["value"] if full.get("coverage") == "text_model_only" else None


def nice_max(v: float) -> float:
    for mag in (1, 10, 100, 1000):
        for step in (1, 2, 2.5, 5):
            if step * mag * 4 >= v:
                return step * mag * 4
    return v


def logo(model: str, size: int = 16) -> str:
    return f'<img src="{ASSET}kinyarwanda/{b.logo24(model)}.svg" alt="" width="{size}" height="{size}" />'


def speech_text(c: dict) -> str:
    return "Built-in audio" if c["speech"] == b.DIRECT_AUDIO else f"{c['speech']} speech recognition"


# ---------------------------------------------------------------------------------------------------------
# one language's facts for one model

def facts_for(model: str, L: dict) -> dict:
    c = L["best"][model]
    ranked = L["ranked"]
    n = len(ranked)
    rank = mp.competition_rank([x["acc"] for x in ranked], c["acc"], False)
    t_rank = mp.competition_rank([round(x["time"], 1) for x in ranked], round(c["time"], 1), True)
    ecos = [(x, co2(x)) for x in ranked if co2(x) is not None]
    e = co2(c)
    e_rank = mp.competition_rank([round(v, 1) for _, v in ecos], round(e, 1), True) if e is not None else None
    # Index over time: this model, or one it replaced, in archived snapshots with the same questions
    names = [model] + [r["name"] for r in MODELS[model].get("replaces") or []]
    series = []
    for snap in reversed(L["archive"]):   # oldest first
        runs = [x for x in snap["chains"] if b.norm(x["model"]) in {b.norm(nm) for nm in names}]
        if runs:
            best = max(runs, key=lambda x: (x["acc"], -x["time"]))
            series.append({"month": snap["month"], "label": snap["label"], "name": best["model"], "score": best["score"],
                           "time": best["time"]})
    series.append({"month": mp.month_short(L["snapshot"]), "label": L["updated"], "name": model, "score": c["score"],
                   "time": c["time"]})
    return {"L": L, "c": c, "n": n, "rank": rank, "t_rank": t_rank, "e": e, "e_rank": e_rank, "ecos": ecos,
            "med_score": statistics.median(x["score"] for x in ranked),
            "med_time": statistics.median(x["time"] for x in ranked),
            "med_eco": statistics.median(v for _, v in ecos) if ecos else None,
            "series": series if len(series) > 1 else [], "label": b.chain_label(c)}


def rank_text(f: dict) -> str:
    return f"#{f['rank']} of {f['n']}"


# ---------------------------------------------------------------------------------------------------------
# blocks

def hero_card(f: dict) -> str:
    L = f["L"]
    tag = f"Best of {f['n']} models" if f["rank"] == 1 else f"{rank_text(f)} models"
    return (f'<div class="mo-score-card"><span class="mo-sc-cap">{LANG_FLAGS.get(L["flag"], "")}{esc(L["lang"])} Index</span>'
            f'<p><b>{f["c"]["score"]}</b><small>/ 100</small><em class="{"top" if f["rank"] == 1 else ""}">{tag}</em></p></div>')


def stats(f: dict, model: str, langs_tested: int, scores: list[int]) -> str:
    L, c = f["L"], f["c"]
    cards = [
        (ICON_LANG, f"{L['lang']} Index", str(c["score"]), f"{rank_text(f)} models · median {f['med_score']:.0f}", ""),
        (ICON_TARGET, "Languages tested", str(langs_tested),
         f"Index {min(scores)} to {max(scores)}" if langs_tested > 1 else "more coming", ""),
        (ICONS["leaf"], "Eco cost", f"{num(f['e'])}<small>g</small>" if f["e"] is not None else "Not covered",
         (f"CO₂e per 1,000 questions · median {num(f['med_eco'])}" if f["e"] is not None else
          "No EcoCost figure for this chain"), "" if f["e"] is not None else " muted"),
        (ICON_CLOCK, "Response time", f"{c['time']:.1f}<small>s</small>", f"per answer · median {f['med_time']:.1f} s", ""),
        (ICONS["coin"], "Cost per 1,000 questions", PENDING, "Pricing is not published yet", " pricing-pending"),
    ]
    return "".join(f'<div class="mo-stat{cls}"><span>{icon}{esc(k)}</span><b>{v}</b><small>{esc(sub)}</small></div>'
                   for icon, k, v, sub, cls in cards)


def know(f: dict, model: str) -> tuple[str, list[str]]:
    L, c, meta = f["L"], f["c"], MODELS[model]
    lang = L["lang"]
    open_w = any(x["sov"] for x in L["facts"]["chains"] if x["model"] == model)
    if f["rank"] == 1:
        p1 = (f"<strong>{esc(model)}</strong> is the <strong>strongest model we tested for {lang}</strong>: it scores "
              f"<strong>{c['score']}</strong> on the {lang} Index, the highest of {f['n']} models, against a median of {f['med_score']:.0f}.")
    else:
        lead = L["ranked"][0]
        p1 = (f"<strong>{esc(model)}</strong> ranks <strong>#{f['rank']} of {f['n']}</strong> models for {lang}: it scores "
              f"<strong>{c['score']}</strong> on the {lang} Index, against a median of {f['med_score']:.0f}; "
              f"{esc(lead['model'])} leads with {lead['score']}.")
    how = ("listens to the audio directly" if c["speech"] == b.DIRECT_AUDIO else
           f"scores best with <strong>{esc(c['speech'])}</strong> speech recognition")
    faster = "faster than" if c["time"] < f["med_time"] - 0.05 else "slower than" if c["time"] > f["med_time"] + 0.05 else "level with"
    phone = "inside" if c["time"] < 10 else "over"
    p2 = (f"It {how}, and answers in <strong>{c['time']:.1f} seconds</strong>, {faster} the median of {f['med_time']:.1f} s "
          f"and {phone} the 10-second limit for phone calls.")
    if f["e"] is not None:
        lower = "lower than" if f["e"] < f["med_eco"] - 0.05 else "higher than" if f["e"] > f["med_eco"] + 0.05 else "level with"
        p3 = (f"Its language-model step emits about <strong>{num(f['e'])} g CO₂e</strong> per 1,000 questions, "
              f"{lower} the median of {num(f['med_eco'])} g. Pricing is coming soon.")
    else:
        p3 = "Its carbon footprint is not covered by EcoCost for this chain yet. Pricing is coming soon."
    if open_w:
        p4 = "Its weights are <strong>open</strong>, so you can run it on your own servers."
    elif meta.get("zdr_in"):
        p4 = (f"It is <strong>proprietary</strong>, run from {esc(meta['maker'])}’s cloud, with zero data retention in "
              f"{mp.and_join(meta['zdr_in'])}.")
    else:
        p4 = f"It is <strong>proprietary</strong> and runs only in {esc(meta['maker'])}’s cloud."
    chips = []
    chips.append(f"Best {lang} score" if f["rank"] == 1 else f"#{f['rank']} in {lang}")
    if f["t_rank"] <= max(1, -(-f["n"] // 3)):
        chips.append("Among the fastest")
    if c["time"] < 10:
        chips.append("Phone-ready, under 10 s")
    if f["e_rank"] == 1:
        chips.append("Lowest footprint")
    if open_w:
        chips.append("Open weights")
    return "".join(f'<p>{p}</p>' for p in (f"{p1} {p2}", p3, p4)), chips


def places(names: list[str]) -> str:
    return "".join(f'<span class="mo-place">{mp.FLAGS.get(nm, "")}{esc(nm)}</span>' for nm in names)


def specs(f: dict, model: str) -> str:
    L, c, meta = f["L"], f["c"], MODELS[model]
    open_w = meta.get("open")
    rows = [
        (ICONS["server"], "Maker", f'<span class="mo-maker">{logo(model)}{esc(meta["maker"])}</span>'),
        (ICONS["lock"], "License", "Open weights" if open_w else "Proprietary"),
        (ICONS["shield"], "Self-hostable", "Yes" if open_w else "No"),
        (ICONS["mic"], f"Speech input ({L['lang']})", esc(speech_text(c))),
    ]
    if meta.get("hosted_in"):
        rows.append((ICONS["cloud"], "Hosted in", places(meta["hosted_in"])))
    if meta.get("zdr_in"):
        rows.append((ICONS["shield"], "Zero data retention", places(meta["zdr_in"])))
    rows.append((ICONS["coin"], "Pricing", f'<span class="pricing-pending">{PENDING}</span>'))
    rows.append((ICON_CAL, "Evaluated", esc(L["updated"])))
    return "".join(f'<div class="mo-spec"><span>{i}{esc(k)}</span><b>{v}</b></div>' for i, k, v in rows)


def where(model: str) -> str:
    meta = MODELS[model]
    cards = []
    zdr = meta.get("zdr_in") or []
    for nm in zdr + [x for x in meta.get("hosted_in") or [] if x not in zdr]:
        ok = nm in zdr
        cards.append(f'<article class="mo-region"><h3>{mp.FLAGS.get(nm, "")}{esc(nm)}</h3>'
                     f'<p class="pricing-pending">Price {PENDING.lower()}</p>'
                     f'<small class="{"ok" if ok else ""}">{ICONS["shield"] if ok else ICONS["info"]}'
                     f'{"Zero data retention" if ok else "Provider hosting"}</small></article>')
    if meta.get("open"):
        cards.append(f'<article class="mo-region"><h3>{ICONS["lock"]}Your own servers</h3>'
                     f'<p>Open weights</p><small class="ok">{ICONS["shield"]}Nothing leaves your network</small></article>')
    if not cards:
        return ""
    n = len(cards)
    sub = (f"{n} place{'s' * (n != 1)} you can run {esc(model)}. Prices per region are coming soon."
           if not meta.get("open") or n > 1 else f"{esc(model)} has open weights, so it can run wherever you host it.")
    return f"""
      <section class="md-section" aria-labelledby="where-title">
        <div class="container">
          <h2 id="where-title">Where it runs</h2>
          <p class="md-sub mo-sub">{sub}</p>
          <div class="mo-regions" style="--n:{min(n, 4)}">{"".join(cards)}</div>
          <p class="mo-fine"><a class="md-link plain" href="{mp.CONTACT}">Need it in another region? Talk to us</a></p>
        </div>
      </section>"""


def lang_chart(model: str, f: dict, tested: list[dict]) -> str:
    top = 100
    bars = []
    for g in tested:
        on = g["L"]["slug"] == f["L"]["slug"]
        h = g["c"]["score"] / top * 180
        bars.append(f'<div class="mo-bar{" on" if on else ""}">'
                    f'<span style="height:{h:.0f}px"><b>{g["c"]["score"]}</b><i style="bottom:{g["med_score"] / top * 180:.0f}px" title="median {g["med_score"]:.0f}"></i></span>'
                    f'<small>{LANG_FLAGS.get(g["L"]["flag"], "")}{esc(g["L"]["lang"])}</small><em>#{g["rank"]} of {g["n"]}</em></div>')
    return f"""<article class="mo-card mo-wide-half">
              <header><h3>{ICON_LANG}Language understanding</h3></header>
              <p class="mo-card-sub">Each bar is {esc(model)}’s Index in that language, from 0 to 100. The tick marks the median of the models tested there.</p>
              <div class="mo-bars" style="--n:{len(tested)}">{"".join(bars)}</div>
              <p class="mo-legend"><span class="on">{f["c"]["score"]} selected language ({esc(f["L"]["lang"])})</span><span>other languages</span><span class="tick">median of all models</span></p>
            </article>"""


def scatter(model: str, f: dict) -> str:
    L = f["L"]
    pts = f["ecos"]
    if len(pts) < 2:
        return ""
    W, H, l, r, t, bm = 460, 250, 34, 14, 12, 30
    xmax = nice_max(max(v for _, v in pts) * 1.1)
    ymin = max(0, (min(x["score"] for x, _ in pts) - 8) // 10 * 10)
    X = lambda v: l + v / xmax * (W - l - r)
    Y = lambda s: t + (100 - s) / (100 - ymin) * (H - t - bm)
    out = []
    for i in range(5):
        v = xmax * i / 4
        out.append(f'<line x1="{X(v):.1f}" y1="{t}" x2="{X(v):.1f}" y2="{H - bm}" class="g"/><text x="{X(v):.1f}" y="{H - bm + 14}" class="ax" text-anchor="middle">{num(v) if v else 0}</text>')
    for s in range(int(ymin), 101, 10):
        out.append(f'<line x1="{l}" y1="{Y(s):.1f}" x2="{W - r}" y2="{Y(s):.1f}" class="g"/><text x="{l - 6}" y="{Y(s) + 3:.1f}" class="ax" text-anchor="end">{s}</text>')
    me = next((v for x, v in pts if x["model"] == model), None)
    if me is not None:
        c = f["c"]
        out.append(f'<rect x="{l}" y="{t}" width="{X(me) - l:.1f}" height="{Y(c["score"]) - t:.1f}" class="better"/>'
                   f'<text x="{l + 6}" y="{t + 13}" class="bt">Higher score, lower footprint</text>')
    for x, v in sorted(pts, key=lambda p: p[0]["model"] == model):
        mine = x["model"] == model
        extra = f" · {x['score']}, {num(v)} g" if mine else ""
        cx, cy = X(v), Y(x["score"])
        anchor = "end" if cx > W - 120 else "start"
        dx = -10 if anchor == "end" else 10
        out.append(f'<g class="pt{" me" if mine else ""}"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{6 if mine else 4.5}"/>'
                   f'<text x="{cx + dx:.1f}" y="{cy + 4:.1f}" text-anchor="{anchor}">{esc(x["model"])}{extra}</text></g>')
    missing = [x["model"] for x in L["ranked"] if co2(x) is None]
    note = (f'<p class="mo-card-foot">Not covered by EcoCost: {esc(mp.and_join(missing))}.</p>' if missing else "")
    mine_note = "" if me is not None else f'<p class="mo-card-foot">{esc(model)}’s chain has no EcoCost figure, so it is not plotted.</p>'
    return f"""<article class="mo-card mo-wide-half">
              <header><h3>{ICONS["leaf"]}{esc(L["lang"])} Index and carbon footprint</h3></header>
              <p class="mo-card-sub">Models with an EcoCost figure in {esc(L["lang"])}. Up and to the left is better.</p>
              <svg class="mo-scatter" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(L['lang'])} Index against grams of CO2e per 1,000 questions">{"".join(out)}
                <text x="{(W + l) / 2:.0f}" y="{H - 2}" class="ax" text-anchor="middle">g CO₂e per 1,000 questions, lower is better</text></svg>
              {mine_note}{note}
            </article>"""


def over_time(model: str, f: dict) -> str:
    s = f["series"]
    if not s:
        return ""
    W, H, l, r, t, bm = 940, 180, 34, 40, 24, 26
    lo = max(0, (min(p["score"] for p in s) - 10) // 10 * 10)
    X = lambda i: l + (i / (len(s) - 1)) * (W - l - r)
    Y = lambda v: t + (100 - v) / (100 - lo) * (H - t - bm)
    grid = "".join(f'<line x1="{l}" x2="{W - r}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="g"/><text x="{l - 6}" y="{Y(v) + 3:.1f}" class="ax" text-anchor="end">{v}</text>'
                   for v in range(int(lo), 101, 20))
    line = " ".join(f"{X(i):.1f},{Y(p['score']):.1f}" for i, p in enumerate(s))
    dots = "".join(f'<circle cx="{X(i):.1f}" cy="{Y(p["score"]):.1f}" r="4"/><text x="{X(i):.1f}" y="{Y(p["score"]) - 10:.1f}" text-anchor="middle" class="v">{p["score"]}</text>'
                   f'<text x="{X(i):.1f}" y="{H - 6}" text-anchor="middle" class="ax">{esc(p["month"])}{"" if p["name"] == model else " · " + esc(p["name"])}</text>'
                   for i, p in enumerate(s))
    d = s[-1]["score"] - s[0]["score"]
    chip = f"{'+' if d > 0 else ''}{d} since {s[0]['month'].split()[0]}" if d else f"Level since {s[0]['month'].split()[0]}"
    names = [p["name"] for p in s]
    how = (f"{esc(model)} in every round." if all(nm == model for nm in names) else
           f"Newest {esc(MODELS[model]['maker'])} model at each round ({' → '.join(esc(n) for n in dict.fromkeys(names))}).")
    return f"""<article class="mo-card mo-full">
              <header><h3>{ICON_TARGET}{esc(f["L"]["lang"])} Index over time</h3><span class="mo-card-meta">{esc(s[0]["month"])} to {esc(s[-1]["month"])}</span></header>
              <div class="mo-over-head"><b>{s[-1]["score"]}</b><span class="mo-chip-d">{chip}</span><small>{how} Same {f["L"]["questions"]} questions each round.</small></div>
              <svg class="mo-line" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(f['L']['lang'])} Index by evaluation round">{grid}<polyline points="{line}"/>{dots}</svg>
            </article>"""


def small_cards(model: str, f: dict) -> str:
    c, L = f["c"], f["L"]
    s = f["series"]
    if f["e"] is not None:
        eco = (f'<b>{num(f["e"])} g</b><span class="mo-chip-d">median {num(f["med_eco"])} g</span>'
               f'<small>CO₂e per 1,000 {esc(L["lang"])} questions, language-model step. {esc(f["label"])}.</small>')
    else:
        eco = f'<b class="muted">Not covered</b><small>No EcoCost figure for {esc(f["label"])}.</small>'
    if len(s) > 1:
        d = s[-1]["time"] - s[0]["time"]
        dt = f'<span class="mo-chip-d">{"-" if d < 0 else "+"}{abs(d):.1f} s since {esc(s[0]["month"].split()[0])}</span>'
    else:
        dt = f'<span class="mo-chip-d">median {f["med_time"]:.1f} s</span>'
    return f"""<article class="mo-card mo-half" data-toggle>
              <header><div class="mo-seg" role="tablist"><button type="button" role="tab" aria-selected="false" data-k="cost">Cost</button><button type="button" role="tab" aria-selected="true" data-k="eco">CO₂e</button></div></header>
              <div class="mo-small" data-k="eco">{eco}</div>
              <div class="mo-small pricing-pending" data-k="cost" hidden><b>{PENDING}</b><small>Cost per 1,000 {esc(L["lang"])} questions is not published yet.</small></div>
            </article>
            <article class="mo-card mo-half">
              <header><h3>{ICON_CLOCK}Response time</h3></header>
              <div class="mo-small"><b>{c["time"]:.1f} s</b>{dt}<small>Median per {esc(L["lang"])} question, {esc(f["label"])}. {"Inside" if c["time"] < 10 else "Over"} the 10-second limit for phone calls.</small></div>
            </article>"""


def rounds(model: str, f: dict) -> str:
    L = f["L"]
    items = [f'<li><span class="mo-dot"></span><p class="mo-r-date">{esc(mp.month_short(L["snapshot"]))}<em>Latest</em></p>'
             f'<p>{f["n"]} models on {L["questions"]} spoken {esc(L["lang"])} questions. {esc(model)} scores {f["c"]["score"]}.</p>'
             f'<a href="{esc(L["bulk_url"])}" target="_blank" rel="noopener noreferrer">View the run{ICONS["chev"]}</a></li>']
    by_month = {p["month"]: p for p in f["series"][:-1]}
    for snap in L["archive"]:
        n = len({x["model"] for x in snap["chains"]})
        p = by_month.get(snap["month"])
        said = (f"{esc(p['name'])} scores {p['score']}." if p else f"{esc(model)} was not in this round.")
        items.append(f'<li><span class="mo-dot"></span><p class="mo-r-date">{esc(snap["month"])}<em>Archived</em></p>'
                     f'<p>{n} models on the same questions. {said}</p>'
                     f'<a href="../language/{L["slug"]}/">See the {esc(L["lang"])} page{ICONS["chev"]}</a></li>')
    return f"""<article class="mo-card mo-full">
              <header><h3>{ICON_CAL}Evaluation rounds</h3><a class="md-btn mo-btn-sm" href="../language/{L["slug"]}/">Compare models in {esc(L["lang"])}</a></header>
              <p class="mo-card-sub">What was measured in each {esc(L["lang"])} round.</p>
              <ol class="mo-rounds">{"".join(items)}</ol>
            </article>"""


# ---------------------------------------------------------------------------------------------------------
# page

def overview_slugs() -> list[str]:
    tested = {m for m, _ in mp.model_slugs()}
    return [m for m in MODELS if m in tested]


def render(model: str) -> str:
    meta = MODELS[model]
    mslug = meta["slug"]
    langs = mp.languages()
    tested = [facts_for(model, L) for L in langs.values() if model in L["best"]]
    tested.sort(key=lambda g: [x["lang"] for x in langs.values()].index(g["L"]["lang"]))
    default = min(tested, key=lambda g: (g["rank"], -g["c"]["score"]))
    scores = [g["c"]["score"] for g in tested]
    k = len(tested)
    open_w = bool(meta.get("open"))

    def panel(g: dict, html_: str, tag: str = "div", cls: str = "") -> str:
        hidden = "" if g is default else " hidden"
        return f'<{tag} class="mo-panel{cls}" data-lang="{g["L"]["slug"]}"{hidden}>{html_}</{tag}>'

    # hero lead
    firsts = [g["L"]["lang"] for g in tested if g["rank"] == 1]
    if firsts:
        head = f"{esc(model)} is the strongest model we tested for {mp.and_join(firsts)}."
    else:
        head = f"{esc(model)} does best in {default['L']['lang']}, #{default['rank']} of {default['n']} models."
    tail = (f"It was evaluated on spoken questions in {k} language{'s' * (k != 1)}"
            + (", and its weights are open." if open_w else f", and runs in {esc(meta['maker'])}’s cloud."))
    lead = f"<strong>{head}</strong> {tail}"

    options = "".join(f'<option value="{g["L"]["slug"]}"{" selected" if g is default else ""}>{esc(g["L"]["lang"])}</option>' for g in tested)
    know_html = []
    for g in tested:
        text, chips = know(g, model)
        know_html.append(panel(g, f"""
            <div class="mo-know">
              <h2>What to know about {esc(model)}</h2>
              <div class="mo-know-text">{text}</div>
              <div class="md-chips">{"".join(f"<span>{esc(x)}</span>" for x in chips)}</div>
              <a class="md-link" href="{mslug}/{g["L"]["slug"]}/">Full {esc(g["L"]["lang"])} results: sample answers, comparison and footprint{ICONS["chev"]}</a>
            </div>
            <div class="mo-specs">
              <h2>Specifications</h2>
              <div class="mo-spec-list">{specs(g, model)}</div>
            </div>""", cls=" mo-know-grid"))
    evals = []
    for g in tested:
        evals.append(panel(g, "\n            ".join(x for x in (
            lang_chart(model, g, tested), scatter(model, g), over_time(model, g), small_cards(model, g), rounds(model, g)) if x),
            cls=" mo-grid"))
    other = []
    for name in json.loads((SRC / "languages.json").read_text())["languages"]:
        g = next((g for g in tested if g["L"]["lang"] == name), None)
        other.append(f'<li><a href="{mslug}/{g["L"]["slug"]}/">{name}</a></li>' if g else f"<li>{name}</li>")
    other.append(f'<li><strong>{json.loads((SRC / "languages.json").read_text())["all"]}</strong></li>')
    latest = max(tested, key=lambda g: g["L"]["snapshot"])["L"]

    slots = {
        "header": b.HEADER_HTML.format(title=model).rstrip("\n"),
        "model": esc(model), "maker": esc(meta["maker"]),
        "meta_line": f'{logo(model)}{esc(meta["maker"])}<span>·</span>{meta["kind"]}<span>·</span>Evaluated {latest["updated"]}',
        "lead": lead, "agent": f"../language/{default['L']['slug']}/ai-agent/",
        "compare": f"../language/{default['L']['slug']}/",
        "art": mp.hero_art(), "score_cards": "".join(panel(g, hero_card(g)) for g in tested),
        "options": options, "lang_icon": ICON_LANG, "down": ICON_DOWN,
        "stats": "".join(panel(g, stats(g, model, k, scores), cls=" mo-stats") for g in tested),
        "fine": (f"Index: how closely answers to spoken questions match an expert’s, from 0 to 100, using {esc(model)}’s best "
                 f"chain in each language. Response time and CO₂e come from the same runs. Pricing is coming soon."),
        "know": "".join(know_html), "where": where(model),
        "evals_sub": (f"Every chart below uses the language chosen above, except Language understanding, which compares "
                      f"the {k} languages {esc(model)} was tested in."),
        "evals": "".join(evals),
        "cta_title": f"Build an agent with {esc(model)}",
        "cta_text": f"Start from {esc(model)} and add your own tools, data and a WhatsApp number. Switch models any time. Free to start.",
        "api": mp.API,
        "other_title": f"{esc(model)} in other languages",
        "other_languages": f'<ul class="language-list" aria-label="{esc(model)} in other languages">{"".join(other)}</ul>',
        "updated": latest["updated"],
        "email": f"Email me when {esc(model)}’s results change",
    }
    body = mp.fill((SRC / "model-overview.tmpl").read_text(encoding="utf-8"), slots)

    path = f"models/{mslug}"
    base = f"{model}: Languages, Speed & Cost"
    title = seo.fit(base + seo.BRAND, base, f"{model}{seo.BRAND}", hi=seo.TITLE_MAX, what=f"{model} title")
    per = ", ".join(f"{g['L']['lang']} {g['c']['score']}" for g in tested)
    description = seo.fit(
        f"How {model} does on spoken questions in {k} languages ({per} out of 100), with response time and carbon footprint.",
        f"{model} on spoken questions in {k} languages ({per} out of 100), with response time and footprint.",
        f"{model} on spoken questions in {k} languages: Index, response time and carbon footprint per language, from Gooey.AI evaluations.",
        f"{model} on spoken questions in {k} languages: Index, response time, carbon footprint and where it runs, from Gooey.AI's own evaluations.",
        lo=seo.DESC_MIN, hi=seo.DESC_MAX, what=f"{model} description")
    d = default
    speech_logo = b.js_dict("SPEECH_FILES")[d["c"]["speech"]]
    card = {"eyebrow": f"Model · {meta['maker']}", "title": model, "date": latest["updated"],
            **({"badge": ["Sovereign-deployable", "landmark"]} if open_w else {}),
            "visual": {"kind": "score", "label": f"{d['L']['lang']} Index", "sub": f"Best of its {k} languages" if k > 1 else "Accuracy on spoken questions",
                       "value": d["c"]["score"], "note": f"#{d['rank']} of {d['n']} models", "sovereign": open_w,
                       "chain": d["label"], "logos": [f"language/assets/kinyarwanda/{b.logo24(model)}.svg",
                                                      f"language/assets/kinyarwanda/{'icon-mic-legend' if speech_logo == 'icon-mic' else speech_logo}.svg"]}}
    image = seo.og_image(path, card, f"{model}: {d['L']['lang']} Index {d['c']['score']} out of 100, #{d['rank']} of {d['n']} models. "
                                     f"Tested in {k} language{'s' * (k != 1)}.")
    graph = [seo.ORG, seo.webpage(path, title, description, image, latest["snapshot"]),
             seo.breadcrumbs(path, [("Home", seo.SITE), seo.EVALS, (model, None)])]
    tags = seo.head(path=path, title=title, description=description, og_title=base, image=image, graph=graph)
    head_html = mp.HEAD.format(seo=tags, header_css=b.HEADER_CSS).replace(
        '<link rel="stylesheet" href="../language/assets/language-model.css" />',
        '<link rel="stylesheet" href="../language/assets/language-model.css" />\n'
        '    <link rel="stylesheet" href="../language/assets/language-model-overview.css" />')
    config = {"model": model, "default": default["L"]["slug"],
              "languages": {g["L"]["slug"]: {"lang": g["L"]["lang"], "agent": f"../language/{g['L']['slug']}/ai-agent/",
                                             "compare": f"../language/{g['L']['slug']}/"} for g in tested}}
    return head_html + body.rstrip("\n") + "\n" + TAIL.format(config=json.dumps(config, ensure_ascii=False, separators=(", ", ": ")))


def pages() -> dict[pathlib.Path, str]:
    return {ROOT / "models" / MODELS[m]["slug"] / "index.html": render(m) for m in overview_slugs()}


if __name__ == "__main__":
    for path, page in pages().items():
        path.write_text(page, encoding="utf-8")
        print("wrote", path.relative_to(ROOT))
