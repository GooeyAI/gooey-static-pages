#!/usr/bin/env python3
"""Save the Gooey.AI workflows each language's evaluation ran, so the chains table can link to them.

    python3 scripts/fetch_language_workflows.py              # every language
    python3 scripts/fetch_language_workflows.py kinyarwanda  # one language

Reads `hero.bulk_url` from language/_src/<slug>/page.json (the language's own bulk evaluation run),
lists the saved workflows that run compared, in run order, and writes
language/data/<code>/workflows-<snapshot>.json. Run order matches the "(N <title>) Run URL" columns
of evaluation-latest.csv, which is how the build pairs each chain with its workflow.

A workflow can be edited after the evaluation (for example moved to a newer model). Each entry keeps
the title it had in the evaluation (`tested_as`), its title when fetched (`title_now`) and the
evaluation's own run of it for the first question (`eval_run`). When the titles differ the entry is
marked `retitled`, and the page links `eval_run` instead, so the link shows the model that was scored.
"""
from __future__ import annotations

import csv
import datetime
import html
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "language" / "_src"
DATA = ROOT / "language" / "data"
BULK_RE = re.compile(r"^https://gooey\.ai/bulk/[a-z0-9-]+/$")
RUN_URL_RE = re.compile(r'run_urls:[0-9a-f-]+" value="&quot;(https://gooey\.ai/[^&"]+)&quot;".*?<p>(.*?)</p>', re.S)


def tested_runs(code: str) -> list[tuple[str, str]]:
    """(title in the evaluation, its run URL for the first question), in run order."""
    with (DATA / code / "evaluation-latest.csv").open(encoding="utf-8-sig", newline="") as f:
        first = next(csv.DictReader(f))
    return [(c[1:-len(") Run URL")], first[c].strip()) for c in first if c.startswith("(") and c.endswith(") Run URL")]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("-", " ")).strip().lower()


def fetch(slug: str) -> int:
    page = json.loads((SRC / slug / "page.json").read_text())
    url = page["hero"]["bulk_url"]
    if not BULK_RE.match(url):
        print(f"{slug}: hero.bulk_url {url!r} is not a specific evaluation run; ask the team for it", file=sys.stderr)
        return 1
    req = urllib.request.Request(url, headers={"User-Agent": "gooey-static-pages/fetch_language_workflows"})
    body = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    found = [(u, html.unescape(re.sub(r"<[^>]+>", "", t)).strip()) for u, t in RUN_URL_RE.findall(body)]
    tested = tested_runs(page["code"])
    if not found or len(found) != len(tested):
        print(f"{slug}: the bulk run lists {len(found)} workflows but evaluation-latest.csv has {len(tested)} chains",
              file=sys.stderr)
        return 1
    workflows = [{"tested_as": t, "title_now": now, "retitled": norm(now) != norm(t), "url": u, "eval_run": run}
                 for (t, run), (u, now) in zip(tested, found)]
    out = DATA / page["code"] / f"workflows-{page['snapshot']}.json"
    out.write_text(json.dumps({
        "source": url,
        "fetched": datetime.date.today().isoformat(),
        "note": "Saved Gooey.AI workflows the bulk evaluation ran, in run order. A retitled workflow was edited "
                "after the evaluation; pages link its eval_run (the evaluation's run of question 1) instead.",
        "workflows": workflows,
    }, indent=2, ensure_ascii=False) + "\n")
    changed = [w for w in workflows if w["retitled"]]
    print(f"{slug}: wrote {out.relative_to(ROOT)} ({len(workflows)} workflows, {len(changed)} retitled since the evaluation)")
    for w in changed:
        print(f"    {w['tested_as']!r} is now {w['title_now']!r}; linking its evaluation run instead")
    return 0


def main(argv: list[str]) -> int:
    slugs = argv or sorted(p.parent.name for p in SRC.glob("*/page.json"))
    return max(fetch(s) for s in slugs)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
