#!/usr/bin/env python3
"""Turn a Gooey.AI evaluator CSV into the data files a /language/<name> page reads.

    python3 scripts/build_language_data.py \\
        --csv ~/Downloads/hausa-evaluator-30.csv --code hau --lang Hausa --country NG \\
        --date 2026-08-30 --samples 5,12,14 --sample-chain 0

Writes language/data/<code>/:

    evaluation-latest.csv        the evaluator CSV, unchanged
    summary-<date>.csv           accuracy (mean semantic similarity) and latency (median run time) per chain
    pricing-<date>.json          observed whole-workflow run cost, from the public run pages in the CSV
    ecocost-<date>.json          EcoCost CO2e for the text-model step, from the same run pages
    samples.json (+ audio/)      the question cards shown on the page

Cost and EcoCost are not in the CSV; every "(N chain - Language) Run URL" column points at a public
Gooey.AI run page that embeds them, so this fetches those pages (cached in --cache, resumable).

Then: copy language/_src/<existing>/ to language/_src/<slug>/, edit it, and run
scripts/build_language_pages.py.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime
import json
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
csv.field_size_limit(10**8)

DIRECT_AUDIO_REASON = (
    "Direct-audio inference is outside the current EcoCost methodology scope; "
    "the text-token estimate embedded in these runs is intentionally excluded."
)
NO_RESULT_REASON = "The public Gooey.AI run records contain no EcoCost result for this text model."
METHODOLOGY_URL = "https://github.com/GooeyAI/ecocost/blob/main/METHODOLOGY.md"


def pretty(name: str) -> str:
    """CSV workflow name -> the name the page and the JSON files use."""
    name = name.replace("GPT 5.6 Sol", "GPT-5.6 Sol")
    return re.sub(r"\+ Omni$", "+ Omnilingual", name)


def workflows(rows: list[dict], lang: str) -> dict[int, str]:
    found = {}
    for col in rows[0]:
        m = re.fullmatch(r"\((\d+) (.+?) - %s\) Run URL" % re.escape(lang), col)
        if m:
            found[int(m.group(1))] = m.group(2)
    if not found:
        raise SystemExit(f"no '(N chain - {lang}) Run URL' columns found; is --lang right?")
    return found


def column(rows, idx, name, suffix, lang):
    return f"({idx} {name} - {lang}) {suffix}"


def fetch_run(url: str) -> dict:
    page = None
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            page = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
            break
        except Exception as e:  # noqa: BLE001 - retry, then record the failure
            err = str(e)
    if page is None:
        return {"url": url, "error": err}
    rec = {"url": url, "run_id": re.search(r"run_id=(\w+)", url).group(1)}
    i = page.find('"eco_cost":')
    if i >= 0:
        rest = page[i + len('"eco_cost":'):].lstrip()
        if not rest.startswith("null"):
            obj, _ = json.JSONDecoder().raw_decode(rest)
            rec["eco"] = {k: obj.get(k) for k in (
                "confidence", "reasons", "models", "co2e_grams", "co2e_min", "co2e_max", "energy_wh", "water_ml")}
    m = re.search(r'"run_cost_usd":([0-9.]+)', page) or re.search(r'"cost_label":"\$([0-9.]+)"', page)  # no EcoCost record -> label only
    rec["run_cost_usd"] = float(m.group(1)) if m else None
    m = re.search(r"Breakdown: .*?/run", page)
    rec["breakdown"] = m.group(0) if m else None
    return rec


def fetch_all(rows, wf, lang, cache_path: pathlib.Path) -> dict:
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    cache = {k: v for k, v in cache.items() if v.get("run_cost_usd") is not None}  # retry runs read without a cost
    jobs = [(i, int(r["ID"]), r[column(rows, i, name, "Run URL", lang)])
            for i, name in wf.items() for r in rows]
    todo = [j for j in jobs if f"{j[0]}|{j[1]}" not in cache]
    print(f"{len(jobs)} runs, {len(todo)} to fetch")
    with cf.ThreadPoolExecutor(6) as ex:
        for n, (job, rec) in enumerate(zip(todo, ex.map(lambda j: fetch_run(j[2]), todo)), 1):
            cache[f"{job[0]}|{job[1]}"] = rec
            if n % 30 == 0:
                cache_path.write_text(json.dumps(cache))
                print(f"  {n}/{len(todo)}", flush=True)
    cache_path.write_text(json.dumps(cache))
    failed = [k for k, v in cache.items() if "error" in v]
    if failed:
        raise SystemExit(f"{len(failed)} run pages failed to load (re-run to retry): {failed[:5]}")
    return cache


def write_summary(out, rows, wf, lang, args):
    lines = []
    max_latency = 0
    for i, name in wf.items():
        score_col = next(k for k in rows[0] if k.startswith(f"Compare Semantics Similarity - Output Text - {i} "))
        acc = statistics.mean(float(r[score_col]) for r in rows if r[score_col].strip())
        lat = statistics.median(float(r[column(rows, i, name, "Run Time", lang)]) for r in rows)
        max_latency = max(max_latency, lat)
        lines.append(f"{pretty(name)},{acc:.8f},{lat:.3f}")
    top = 2 * (int(max_latency // 2) + 1)
    slug = args.lang.lower()
    header = [f"# title: {args.lang} Evaluation of Audio AI Models", f"# country: {args.country}", "# byline: Gooey.AI",
              f"# date: {args.date}", f"# url: Gooey.AI/language/{slug}", "# x: Accuracy, 0, 1, 0.1",
              f"# y: Latency, 0, {top}, 2", "Workflow,Accuracy (mean),Latency (median)"]
    (out / f"summary-{args.date}.csv").write_text("\n".join(header + lines) + "\n", encoding="utf-8")


def wf_label(i, name):
    n = pretty(name)
    return f"{n} (direct audio)" if " + " not in n else n


def write_pricing(out, rows, wf, cache, args, snapshot):
    items = []
    for i, name in wf.items():
        runs = [cache[f"{i}|{int(r['ID'])}"] for r in rows]
        costs = [r["run_cost_usd"] for r in runs]
        mean = statistics.mean(costs)
        items.append({
            "workflow": wf_label(i, name), "sample_size": len(runs), "currency": "USD",
            "cost_usd_per_1000": mean * 1000,
            "observed_run_cost_usd": {"mean": mean, "min": min(costs), "max": max(costs)},
            "runs": [{"question_number": int(r["ID"]), "run_id": c["run_id"], "run_cost_usd": c["run_cost_usd"],
                      "cost_breakdown": c["breakdown"], "cost_source": "eco_cost.run_cost_usd"}
                     for r, c in zip(rows, runs)]})
    n = len(rows)
    doc = {
        "schema_version": 1, "benchmark_date": args.date, "snapshot_date": snapshot, "source_csv": "evaluation-latest.csv",
        "source": "Whole-workflow run_cost_usd records embedded in the public Gooey.AI run pages listed in the source CSV.",
        "currency": "USD",
        "normalization": f"For each workflow, take the arithmetic mean of the {n} observed whole-workflow run costs and multiply by 1,000 questions.",
        "scope": "Observed Gooey.AI run charge for the complete workflow, including speech recognition or direct-audio and text-model steps represented in each run.",
        "caveat": "These are historical observed Gooey.AI run charges for the benchmark snapshot, not current provider list prices or a future-price guarantee.",
        "workflows": items}
    (out / f"pricing-{args.date}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def write_ecocost(out, rows, wf, cache, args, snapshot):
    items = []
    for i, name in wf.items():
        runs = [cache[f"{i}|{int(r['ID'])}"] for r in rows]
        base = {"workflow": wf_label(i, name), "source_run_count": len(runs)}
        run_ids = [c["run_id"] for c in runs]
        eco = [c["eco"] for c in runs if c.get("eco")]
        direct = " + " not in pretty(name)
        if direct:
            models = sorted({m["model_id"] for e in eco for m in e["models"]})
            items.append({**base, "sample_size": 0, "coverage": "not_covered", "reason": DIRECT_AUDIO_REASON,
                          "model_ids_observed": models, "run_ids": run_ids})
        elif not eco:
            items.append({**base, "sample_size": 0, "coverage": "not_covered", "reason": NO_RESULT_REASON, "run_ids": run_ids})
        else:
            k = 1000 / len(eco)
            items.append({
                **base, "sample_size": len(eco), "coverage": "text_model_only",
                "model_ids": sorted({m["model_id"] for e in eco for m in e["models"]}),
                "co2e_g_per_1000": {"value": sum(e["co2e_grams"] for e in eco) * k,
                                    "min": sum(e["co2e_min"] for e in eco) * k, "max": sum(e["co2e_max"] for e in eco) * k},
                "energy_wh_per_1000": sum(e["energy_wh"] for e in eco) * k,
                "water_ml_per_1000": sum(e["water_ml"] for e in eco) * k,
                "confidence": sorted({e["confidence"] for e in eco}),
                "reasons": sorted({r for e in eco for r in e["reasons"]}), "run_ids": run_ids})
    n = len(rows)
    doc = {
        "schema_version": 1, "benchmark_date": args.date, "snapshot_date": snapshot, "source_csv": "evaluation-latest.csv",
        "source": "EcoCost records embedded in the public Gooey.AI run pages listed in the source CSV.",
        "methodology_url": METHODOLOGY_URL, "method_version": None,
        "method_version_note": "The public Gooey.AI run records do not expose an EcoCost method version.",
        "normalization": f"For each covered workflow, sum the {n} per-run values and multiply by 1000/{n}. Point, minimum, and maximum estimates are aggregated independently.",
        "scope": "Text-model inference only. Speech recognition and direct-audio inference are excluded.",
        "workflows": items}
    (out / f"ecocost-{args.date}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def write_samples(out, rows, wf, lang, args):
    chain = args.sample_chain
    name = wf[chain]
    score_col = next(k for k in rows[0] if k.startswith(f"Compare Semantics Similarity - Output Text - {chain} "))
    by_id = {r["ID"]: r for r in rows}
    audio_dir = out / "audio"
    samples = []
    for q in args.samples.split(","):
        r = by_id[q]
        src = r["input_audio"]
        m = re.search(r"drive\.google\.com/file/d/([\w-]+)", src)
        if m:  # Drive links can't be played in an <audio> tag, so host a copy
            audio_dir.mkdir(exist_ok=True)
            opus = audio_dir / f"{args.lang.lower()}-q{q}.opus"
            mp3 = opus.with_suffix(".mp3")
            subprocess.run(["curl", "-sL", "-m", "30", "-o", str(opus),
                            f"https://drive.usercontent.google.com/download?id={m.group(1)}&export=download"], check=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(opus), "-ac", "1", "-b:a", "48k", str(mp3)], check=True)
            opus.unlink()
            url = f"data/{args.code}/audio/{mp3.name}"
            path = mp3
        else:
            url, path = src, None
        dur = 0.0
        if path:
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                       capture_output=True, text=True).stdout.strip())
        section = r.get("Reference_page_section", "")
        samples.append({
            "questionNumber": int(q), "category": section.split(" - ")[-1] if " - " in section else section,
            "audioUrl": url, "audioDurationSeconds": round(dur, 3),
            "transcript": r["Question_Target"], "questionEnglish": r["Question_Source"],
            "answer": r[column(rows, chain, name, "Output Text", lang)],
            "expertAnswer": r["reference_answer"], "score": round(float(r[score_col]) * 100),
            "runtimeSeconds": float(r[column(rows, chain, name, "Run Time", lang)]),
            "runUrl": r[column(rows, chain, name, "Run URL", lang)]})
    doc = {"language": args.lang, "evaluationDate": args.date, "source": "evaluation-latest.csv",
           "workflow": pretty(name), "totalQuestions": len(rows), "samples": samples}
    (out / "samples.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", required=True, type=pathlib.Path)
    ap.add_argument("--code", required=True, help="data folder name, e.g. hau")
    ap.add_argument("--lang", required=True, help="name used in the CSV columns, e.g. Hausa")
    ap.add_argument("--country", required=True, help="ISO code for the summary header, e.g. NG")
    ap.add_argument("--date", required=True, help="benchmark date, YYYY-MM-DD")
    ap.add_argument("--samples", help="comma-separated question IDs to show as sample cards")
    ap.add_argument("--sample-chain", type=int, default=0, help="chain index whose answers the sample cards show")
    ap.add_argument("--cache", type=pathlib.Path, default=pathlib.Path("/tmp/language-runs-cache.json"))
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.csv, encoding="utf-8", newline="")))
    wf = workflows(rows, args.lang)
    out = ROOT / "language" / "data" / args.code
    out.mkdir(parents=True, exist_ok=True)
    snapshot = datetime.date.today().isoformat()

    shutil.copyfile(args.csv, out / "evaluation-latest.csv")
    write_summary(out, rows, wf, args.lang, args)
    cache = fetch_all(rows, wf, args.lang, args.cache)
    write_pricing(out, rows, wf, cache, args, snapshot)
    write_ecocost(out, rows, wf, cache, args, snapshot)
    if args.samples:
        write_samples(out, rows, wf, args.lang, args)
    print(f"wrote {out.relative_to(ROOT)}: {len(wf)} chains x {len(rows)} questions; snapshot {snapshot}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
