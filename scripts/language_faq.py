"""Shared, evidence-led FAQs for language evaluation hub pages (not agent/model pages)."""

from __future__ import annotations

import math
from html import escape


CLINICAL_SAFETY_CAVEAT = (
    "These benchmark results are not a clinical safety assessment. "
    "Any clinical or patient-facing use requires qualified clinical review."
)


def join_names(names: list[str]) -> str:
    return ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else names[0]


def score(accuracy: float) -> int:
    # Match the whole-number Index displayed by language-page.js, including .5 ties.
    return math.floor(accuracy * 100 + 0.5 + 1e-9)


def dollars(value: float, *, per_run: bool = False) -> str:
    if per_run:
        return "$" + f"{value:.4f}".rstrip("0").rstrip(".")
    return f"${value:,.2f}"


def faq_items(page: dict, rows: list, pricing: dict, eco: dict, editorial: dict, models: dict) -> list[tuple[str, str]]:
    """Ordered question/HTML-answer pairs; omit topics whose supporting facts are absent.

    Scores/timings come from the same summary rows as the charts. Editorial metadata contains
    verified dataset context only, never copied scores, winners, prices or hosting flags.
    In particular, chart sovereignty flags are not evidence of a fully local voice deployment.
    """
    if not rows:
        return []
    lang = escape(page["lang"])
    slug, code, snapshot = page["slug"], page["code"], page["snapshot"]
    link = lambda href, text: f'<a href="{escape(href, quote=True)}">{escape(text)}</a>'
    results = link(f"{slug}/#all-chains", "benchmark results")
    source = link(f"data/{code}/evaluation-latest.csv", "evaluation CSV")
    top = min(rows, key=lambda r: (-r[2], r[3]))
    label = lambda r: escape(r[0].replace("GPT 5.6 Sol", "GPT-5.6 Sol") +
                             (" (direct audio)" if r[1] == "Built-in audio" else f" + {r[1]}"))
    low = min(score(r[2]) for r in rows)
    high = score(top[2])
    items = [(f"What is the best AI for {lang}?",
              f"{label(top)} was the highest-scoring chain in our {snapshot} {lang} benchmark. "
              f"It achieved a {lang} Index of {high}/100 with a median response time of {top[3]:.1f} seconds "
              f"across {page['questions']} questions; see the {results}. "
              "This result applies to the tested questions and workflows, not every use case.")]

    if editorial.get("output_language"):
        output = escape(editorial["output_language"])
        items.append((f"Can AI models understand and answer questions in {lang}?",
                      f"Yes—the tested workflows processed spoken {lang} questions and produced answers in {output}. "
                      f"Across {len(rows)} chains, the {lang} Index ranged from {low} to {high}/100 in the {results}. "
                      f"These are complete-workflow results, not standalone speech-recognition scores or a test of answers written in {lang}."))

    open_models = sorted({r[0].replace("GPT 5.6 Sol", "GPT-5.6 Sol") for r in rows
                          if models.get(r[0].replace("GPT 5.6 Sol", "GPT-5.6 Sol"), {}).get("open") is True})
    if open_models:
        items.append((f"Can I run {lang} AI on my own servers?",
                      f"Open-weight language models such as {escape(join_names(open_models))} offer a starting point "
                      f"for running {lang} AI on your own servers. "
                      f"A fully local voice workflow also requires speech recognition that supports {lang} on local hardware. "
                      "Choose hardware that meets the models’ requirements and check each component’s licence and language support before deployment."))

    fast = [r for r in rows if r[3] < 10]
    if fast:
        phone = min(fast, key=lambda r: (-r[2], r[3]))
        phone_answer = (f"For phone-call pilots, {label(phone)} is the highest-scoring chain below our 10-second "
                        f"median response-time target ({score(phone[2])}/100, {phone[3]:.1f} seconds). ")
    else:
        fastest = min(rows, key=lambda r: r[3])
        phone_answer = (f"None of the {len(rows)} tested {lang} chains met our 10-second median response-time target "
                        f"for phone calls; the fastest was {label(fastest)} at {fastest[3]:.1f} seconds. ")
    items.append((f"Which {lang} AI models are best for phone calls and WhatsApp?",
                  phone_answer + f"For WhatsApp voice-note replies, {label(top)} had the highest {lang} Index "
                  f"({high}/100) in the {results}. "
                  "These timings exclude a complete phone connection and spoken reply; test telephony, network and text-to-speech latency before launch."))

    observed = pricing.get("workflows", [])
    if observed and len(observed) == len(rows) and all(w.get("observed_run_cost_usd") and w.get("sample_size") for w in observed):
        means = [w["observed_run_cost_usd"]["mean"] for w in observed]
        minimum, maximum = min(means), max(means)
        per_run = (dollars(minimum, per_run=True) if minimum == maximum else
                   f"{dollars(minimum, per_run=True)}–{dollars(maximum, per_run=True)}")
        per_thousand = (dollars(minimum * 1000) if minimum == maximum else
                        f"{dollars(minimum * 1000)}–{dollars(maximum * 1000)}")
        price_source = link(f"data/{code}/pricing-{snapshot}.json", "pricing snapshot")
        items.append((f"How much does a {lang} AI workflow cost?",
                      f"In our {snapshot} benchmark, the observed average whole-workflow Gooey.AI charge was "
                      f"{per_run} per question, or {per_thousand} per 1,000 questions, depending on the chain. "
                      f"The {price_source} calculates each chain’s average independently from its own recorded runs, "
                      "including the speech-recognition or direct-audio step used by that workflow. "
                      "These historical charges are not current provider list prices or a guarantee of future costs."))

    items.append((f"What does the {lang} Index measure?",
                  f"The {lang} Index is the mean semantic-similarity score between a workflow’s answers and the reference "
                  f"answers, scaled from 0 to 100. The {source} records scores for the {page['questions']} benchmark questions, "
                  "with a higher Index indicating closer agreement in meaning. "
                  "It is not the percentage of questions answered correctly, a standalone transcription score or a safety certification."))

    if editorial.get("dataset_description") and editorial.get("reference_description") and editorial.get("limitations"):
        dataset = escape(editorial["dataset_description"])
        references = escape(editorial["reference_description"])
        limitation = escape(editorial["limitations"])
        items.append((f"How were the {lang} AI models evaluated?",
                      f"On {snapshot}, we evaluated {len(rows)} chains using {page['questions']} spoken {lang} questions: {dataset}. "
                      f"The workflows used direct audio or speech recognition with a language model, and their answers were "
                      f"scored by semantic similarity against {references}; the {source} contains the questions, references, scores and run links. "
                      f"Scores are averaged and response times are medians; {limitation} "
                      f"{CLINICAL_SAFETY_CAVEAT}"))

    covered = [w for w in eco.get("workflows", []) if w.get("coverage") == "text_model_only"]
    if eco.get("workflows"):
        eco_source = link(f"data/{code}/ecocost-{snapshot}.json", "EcoCost snapshot")
        if covered:
            confidence = sorted({c for w in covered for c in w.get("confidence", [])})
            confidence_note = (f" with {escape(join_names(confidence))} confidence" if confidence else "")
            eco_answer = (f"Our EcoCost estimates cover text-model inference for {len(covered)} of the {len(rows)} tested {lang} chains, "
                          f"not their full environmental impact. The {eco_source} reports estimated CO₂e per 1,000 questions "
                          f"and uncertainty ranges{confidence_note}. ")
        else:
            eco_answer = f"The {eco_source} contains no covered text-model estimates for the tested {lang} chains. "
        items.append((f"What is the environmental impact of {lang} AI models?",
                      eco_answer + "Speech recognition and direct-audio inference are excluded, and missing estimates are not zero; "
                      "these data cannot establish the lowest-impact complete voice workflow."))
    return items


def render_faq(template: str, items: list[tuple[str, str]]) -> str:
    if not items:
        return ""
    # Preserve the existing native, keyboard-accessible details interaction and styling.
    markup = "\n".join(f"            <details open><summary>{q}</summary><p>{answer}</p></details>" for q, answer in items)
    return template.replace("{{faq_items}}", markup).rstrip("\n")
