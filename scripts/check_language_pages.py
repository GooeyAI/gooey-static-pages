#!/usr/bin/env python3
"""Keep every /language/<name> page identical in layout.

    python3 scripts/check_language_pages.py

The pages are generated (scripts/build_language_pages.py) from one template, one
stylesheet and one script. This fails when:

  * a page differs from what the generator would write today (someone hand-edited
    the HTML, or changed data/_src without re-running the build);
  * a page carries layout CSS or script of its own, instead of the shared files;
  * a chain uses a model or speech engine the shared script has no logo / name for;
  * a page or the shared script points at an image that doesn't exist.

All three generated page kinds are covered: /language/<name>, /language/<name>/ai-agent and
/models/<model>/<language>, and the links between them (every internal link resolves, no page is an orphan, and
each page links to the ones it should).
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_language_pages as build  # noqa: E402
from site_header import HEADER_CSS  # noqa: E402

LANG = build.LANG
JS = (LANG / "assets" / "language-page.js").read_text(encoding="utf-8")


def dict_keys(name: str) -> set[str]:
    """Keys of a `const NAME = { ... };` object literal in the shared script."""
    m = re.search(r"const %s = \{(.*?)\};" % name, JS, re.S)
    if not m:
        raise SystemExit(f"language-page.js: no `const {name}` found (did the check need updating?)")
    return {k1 or k2 for k1, k2 in re.findall(r'"([^"]+)"\s*:|(\w+)\s*:', m.group(1))}


def check(slug: str) -> list[str]:
    problems = []
    page_file = LANG / slug / "index.html"
    rel = f"language/{slug}/index.html"

    # 1. generated output is current
    expected = build.render(slug)
    actual = page_file.read_text(encoding="utf-8") if page_file.exists() else ""
    if actual != expected:
        problems.append(f"{rel}: differs from the generator's output; run `python3 scripts/build_language_pages.py {slug}`")
        return problems

    # 2. no page-level layout CSS/JS beyond the shared files
    styles = re.findall(r"<style>(.*?)</style>", actual, re.S)
    if len(styles) != 1 or styles[0].strip() != HEADER_CSS.strip():
        problems.append(f"{rel}: has CSS other than the shared header; put layout CSS in language/assets/language-page.css")
    scripts = re.findall(r"<script(?: [^>]*)?>", actual)
    if scripts != ["<script>", '<script src="assets/language-samples.js">', '<script src="assets/language-page.js">',
                   '<script src="assets/language-links.js">']:
        problems.append(f"{rel}: unexpected <script> tags {scripts}")

    # 3. every model / speech engine in the data is known to the shared script
    config = json.loads(re.search(r"window\.LANG_PAGE = (.*?);\n    </script>", actual, re.S).group(1))
    models = {r[0].replace("GPT 5.6 Sol", "GPT-5.6 Sol") for r in config["csv"]}
    speech = {r[1] for r in config["csv"]}
    for registry in ("LOGO_FILES", "MAKERS", "SHORT", "LABEL_BOX", "RING"):
        for missing in sorted(models - dict_keys(registry)):
            problems.append(f"{rel}: model {missing!r} is missing from {registry} in language/assets/language-page.js")
    for missing in sorted(speech - dict_keys("SPEECH_FILES")):
        problems.append(f"{rel}: speech engine {missing!r} is missing from SPEECH_FILES in language/assets/language-page.js")

    # 4. images referenced by the page exist (<base href="../"> makes them relative to language/)
    for ref in sorted(set(re.findall(r'(?:src|href)="((?:assets|data)/[^"?#]+)"', actual))):
        if not (LANG / ref).exists():
            problems.append(f"{rel}: {ref} does not exist under language/")
    return problems


def check_agent(slug: str) -> list[str]:
    problems = []
    page_file = LANG / slug / "ai-agent" / "index.html"
    rel = f"language/{slug}/ai-agent/index.html"
    expected = build.render_agent(slug)
    actual = page_file.read_text(encoding="utf-8") if page_file.exists() else ""
    if actual != expected:
        return [f"{rel}: differs from the generator's output; run `python3 scripts/build_language_pages.py {slug}`"]
    styles = re.findall(r"<style>(.*?)</style>", actual, re.S)
    if len(styles) != 1 or styles[0].strip() != HEADER_CSS.strip():
        problems.append(f"{rel}: has CSS other than the shared header; put it in language/assets/language-agent.css")
    scripts = re.findall(r"<script(?: [^>]*)?>", actual)
    if scripts != ["<script>", '<script src="assets/language-agent.js">', '<script src="assets/language-links.js">']:
        problems.append(f"{rel}: unexpected <script> tags {scripts}")
    agent = json.loads((build.SRC / slug / "agent.json").read_text())
    for model in agent["models"]:
        if model not in dict_keys("LOGO_FILES"):
            problems.append(f"{rel}: model {model!r} is missing from LOGO_FILES in language/assets/language-page.js")
    # <base href="../../"> makes asset and data paths relative to language/
    for ref in sorted(set(re.findall(r'(?:src|href)="((?:assets|data)/[^"?#]+)"', actual))):
        if not (LANG / ref).exists():
            problems.append(f"{rel}: {ref} does not exist under language/")
    return problems


def resolve(page: pathlib.Path, text: str, href: str) -> pathlib.Path:
    """Where an internal href goes, honouring the page's own <base href> (as the proxy and check_links.py do)."""
    m = re.search(r'<base href="([^"]*)"', text)
    base = (page.parent / m.group(1)).resolve() if m else page.parent
    target = (base / href.split("#", 1)[0].split("?", 1)[0]).resolve()
    return target / "index.html" if target.is_dir() else target


def check_model(path: pathlib.Path, expected: str) -> list[str]:
    problems = []
    rel = str(path.relative_to(build.ROOT))
    actual = path.read_text(encoding="utf-8") if path.exists() else ""
    if actual != expected:
        return [f"{rel}: differs from the generator's output; run `python3 scripts/build_language_pages.py {path.parent.name}`"]
    styles = re.findall(r"<style>(.*?)</style>", actual, re.S)
    if len(styles) != 1 or styles[0].strip() != HEADER_CSS.strip():
        problems.append(f"{rel}: has CSS other than the shared header; put it in language/assets/language-model.css")
    scripts = re.findall(r"<script(?: [^>]*)?>", actual)
    want = ["<script>", '<script src="../language/assets/language-samples.js">', '<script src="../language/assets/language-model.js">',
            '<script src="../language/assets/language-links.js">']
    if scripts != want:
        problems.append(f"{rel}: unexpected <script> tags {scripts}")
    for ref in sorted(set(re.findall(r'(?:src|href)="((?:\.\./language/|assets/)[^"?#]+)"', actual))):
        if not (path.parents[2] / ref).resolve().exists():
            problems.append(f"{rel}: {ref} does not exist")
    return problems


def check_links(pages: dict[pathlib.Path, str]) -> list[str]:
    """Links between the generated pages: they resolve, nothing is an orphan, and the pages that should link do."""
    problems, inbound, out = [], {p: set() for p in pages}, {}
    for page, text in pages.items():
        out[page] = set()
        for href in re.findall(r'<a [^>]*href="([^"]+)"', text):
            if re.match(r"([a-z][a-z0-9+.-]*:|//|#)", href, re.I):
                continue
            target = resolve(page, text, href)
            if not target.exists():
                problems.append(f"{page.relative_to(build.ROOT)}: link {href!r} does not resolve ({target.relative_to(build.ROOT) if build.ROOT in target.parents else target})")
            elif target in pages:
                out[page].add(target)
                inbound[target].add(page)
    for page in pages:
        if page not in out[page] and not (inbound[page] - {page}):
            problems.append(f"{page.relative_to(build.ROOT)}: no other generated page links to it")
    for page in pages:
        parts = page.relative_to(build.ROOT).parts
        want = []
        if parts[0] == "models":
            lslug = parts[2]
            want = [build.LANG / lslug / "index.html", build.LANG / lslug / "ai-agent" / "index.html"]
        elif len(parts) == 4 and parts[1] != "assets" and parts[3] == "index.html" and parts[2] == "ai-agent":
            want = [build.LANG / parts[1] / "index.html"]
        elif len(parts) == 3:  # language hub
            want = [build.LANG / parts[1] / "ai-agent" / "index.html"] + [
                q for q in pages if q.relative_to(build.ROOT).parts[0] == "models" and q.relative_to(build.ROOT).parts[2] == parts[1]]
        for w in want:
            if w not in out[page]:
                problems.append(f"{page.relative_to(build.ROOT)}: should link to {w.relative_to(build.ROOT)}")
    return problems


def main() -> int:
    problems = []
    slugs = build.slugs()
    for slug in slugs:
        problems.extend(check(slug))
    for slug in build.agent_slugs():
        problems.extend(check_agent(slug))
    pages = build.all_pages()
    for path, html in pages.items():
        if path.parts[-4] == "models" or "models" in path.relative_to(build.ROOT).parts[:1]:
            problems.extend(check_model(path, html))
    problems.extend(check_links(pages))

    # images the shared script builds at run time
    for name in sorted(set(re.findall(r'"((?:logo|icon|map)-[\w-]+)"', JS))):
        if not (LANG / "assets" / "kinyarwanda" / f"{name}.svg").exists():
            problems.append(f"language/assets/language-page.js: language/assets/kinyarwanda/{name}.svg does not exist")

    # a language page that exists on disk but has no source can't be regenerated
    for page in sorted(LANG.glob("*/index.html")):
        if page.parent.name not in slugs and 'class="layout-' in page.read_text(encoding="utf-8"):
            problems.append(f"language/{page.parent.name}/index.html: generated-looking page with no language/_src/{page.parent.name}/")

    if problems:
        print("\n".join(problems))
        return 1
    n_models = sum(1 for p in pages if p.relative_to(build.ROOT).parts[0] == "models")
    print(f"ok: {len(slugs)} language, {len(build.agent_slugs())} ai-agent and {n_models} model page(s) are in sync with the templates, "
          f"and their links resolve ({', '.join(slugs)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
