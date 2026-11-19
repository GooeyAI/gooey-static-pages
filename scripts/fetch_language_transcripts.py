#!/usr/bin/env python3
"""Save what each speech recognizer heard for the questions a speech-to-text page shows.

    python3 scripts/fetch_language_transcripts.py              # every language with a speech-to-text page
    python3 scripts/fetch_language_transcripts.py kinyarwanda  # one language

For each recognizer in language/_src/<slug>/stt.json (except direct audio), it opens the public Gooey.AI run of
that recognizer's chain ("chain" in stt.json) for the hero question and for every sample question in
language/data/<code>/samples.json, and stores the run's `raw_input_text`: the recognizer's transcript of the
question audio, before the language model sees it. Output: language/data/<code>/transcripts-<snapshot>.json.

The expert transcript is not copied here: the build reads it from evaluation-latest.csv (Prompt_Target).
"""
from __future__ import annotations

import csv
import datetime
import json
import re
import sys
import urllib.request

import build_language_pages as build


def run_urls(page: dict) -> dict[str, str]:
    """Normalized chain name -> its "(N title) Run URL" column in evaluation-latest.csv."""
    with (build.DATA / page["code"] / "evaluation-latest.csv").open(encoding="utf-8-sig", newline="") as f:
        header = next(csv.reader(f))
    cols = {}
    for c in header:
        if not (c.startswith("(") and c.endswith(") Run URL")):
            continue
        name = re.sub(r"^\d+\s+", "", c[1:-len(") Run URL")])
        name = re.sub(r"\s+-\s+" + re.escape(page["lang"]) + r"$", "", name)
        model, _, speech = name.partition(" + ")
        speech = build.SPEECH_ALIASES.get(speech.strip(), speech.strip()) or build.DIRECT_AUDIO
        cols[build.norm(f"{model.strip()} + {speech}")] = c
    return cols


def heard(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "gooey-static-pages/fetch_language_transcripts"})
    body = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    i = body.find('"raw_input_text":')
    if i < 0:
        raise SystemExit(f"{url}: no raw_input_text on the run page")
    text, _ = json.JSONDecoder().raw_decode(body[i + len('"raw_input_text":'):].lstrip())
    return text.strip()


def fetch(slug: str) -> int:
    page = json.loads((build.SRC / slug / "page.json").read_text())
    st = json.loads((build.SRC / slug / "stt.json").read_text())
    d = build.DATA / page["code"]
    with (d / "evaluation-latest.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    questions = [build.hero_question(page)] + [s["questionNumber"] for s in json.loads((d / "samples.json").read_text())["samples"]]
    cols = run_urls(page)
    out = []
    for r in st["recognizers"]:
        if r["speech"] == build.DIRECT_AUDIO:
            continue
        col = cols.get(build.norm(r["chain"]))
        if not col:
            print(f"{slug}: chain {r['chain']!r} has no Run URL column in evaluation-latest.csv", file=sys.stderr)
            return 1
        for q in dict.fromkeys(questions):
            url = rows[q - 1][col].strip()
            out.append({"question": q, "recognizer": r["speech"], "chain": r["chain"], "run": url, "text": heard(url)})
    path = d / f"transcripts-{page['snapshot']}.json"
    path.write_text(json.dumps({
        "source": "Public Gooey.AI runs linked from evaluation-latest.csv",
        "fetched": datetime.date.today().isoformat(),
        "note": "text is the run's raw_input_text: the speech recognizer's transcript of the question audio, "
                "before the language model. The expert transcript is Prompt_Target in evaluation-latest.csv.",
        "transcripts": out,
    }, indent=2, ensure_ascii=False) + "\n")
    print(f"{slug}: wrote {path.relative_to(build.ROOT)} ({len(out)} transcripts)")
    return 0


def main(argv: list[str]) -> int:
    return max(fetch(s) for s in (argv or build.stt_slugs()))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
