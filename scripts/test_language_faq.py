#!/usr/bin/env python3
"""Regression tests for shared language-hub FAQs: python3 scripts/test_language_faq.py."""

import copy
import json
import unittest

import build_language_pages as build
from language_faq import CLINICAL_SAFETY_CAVEAT, faq_items, render_faq, score


class LanguageFAQTests(unittest.TestCase):
    def setUp(self):
        self.page = {"lang": "Example", "slug": "example", "code": "ex", "snapshot": "2026-08-30", "questions": 24}
        self.rows = [["Model A", "Speech A", 0.85, 7.5, True], ["Model B", "Built-in audio", 0.9, 12, False]]
        self.pricing = {"workflows": [
            {"observed_run_cost_usd": {"mean": 0.04}, "sample_size": 24},
            {"observed_run_cost_usd": {"mean": 0.06}, "sample_size": 24},
        ]}
        self.eco = {"workflows": [{"coverage": "text_model_only", "confidence": ["low"]}, {"coverage": "not_covered"}]}
        self.editorial = {"output_language": "English", "dataset_description": "general-knowledge questions",
                          "reference_description": "dataset reference answers", "limitations": "the dataset is small."}
        self.models = {"Model A": {"open": True}, "Model B": {"open": False}}

    def items(self, **overrides):
        args = dict(page=self.page, rows=self.rows, pricing=self.pricing, eco=self.eco,
                    editorial=self.editorial, models=self.models, pricing_coming_soon=False)
        return faq_items(**(args | overrides))

    def test_standard_questions_and_order(self):
        self.assertEqual([q for q, _ in self.items()], [
            "What is the best AI for Example?",
            "Can AI models understand and answer questions in Example?",
            "Can I run Example AI on my own servers?",
            "Which Example AI models are best for phone calls and WhatsApp?",
            "How much does a Example AI workflow cost?",
            "What does the Example Index measure?",
            "How were the Example AI models evaluated?",
            "What is the environmental impact of Example AI models?",
        ])

    def test_winner_and_call_candidate_update_with_data(self):
        answers = dict(self.items())
        self.assertIn("Model B (direct audio)", answers["What is the best AI for Example?"])
        self.assertIn("Model A + Speech A is the highest-scoring chain below", answers[
            "Which Example AI models are best for phone calls and WhatsApp?"])
        rows = copy.deepcopy(self.rows)
        rows[0][2] = 0.95
        self.assertIn("Model A + Speech A", dict(self.items(rows=rows))["What is the best AI for Example?"])

    def test_ten_seconds_is_not_below_target(self):
        rows = copy.deepcopy(self.rows)
        rows[0][3] = 10
        answer = dict(self.items(rows=rows))["Which Example AI models are best for phone calls and WhatsApp?"]
        self.assertIn("None of the 2 tested Example chains met", answer)
        self.assertIn("10.0 seconds", answer)

    def test_pricing_keeps_per_chain_averages(self):
        answer = dict(self.items())["How much does a Example AI workflow cost?"]
        self.assertIn("$0.04–$0.06", answer)
        self.assertIn("$40.00–$60.00 per 1,000", answer)
        self.assertIn("each chain’s average independently", answer)
        self.assertIn("historical", answer)

    def test_pricing_coming_soon_preserves_question_without_amounts(self):
        answers = dict(self.items(pricing_coming_soon=True))
        answer = answers["How much does a Example AI workflow cost?"]
        self.assertIn('class="pricing-pending"', answer)
        self.assertIn("Coming soon", answer)
        self.assertNotIn("$", answer)
        self.assertNotIn("pricing-2026", answer)
        self.assertIn("low confidence", answers["What is the environmental impact of Example AI models?"])

    def test_hosting_does_not_treat_chart_flag_as_proof(self):
        answer = dict(self.items())["Can I run Example AI on my own servers?"]
        self.assertIn("Model A offer a starting point", answer)
        self.assertIn("speech recognition", answer)
        self.assertNotIn("Model B", answer)
        self.assertNotIn("still being verified", answer)
        self.assertNotIn("Yes", answer)

    def test_unsupported_topics_are_omitted(self):
        questions = [q for q, _ in self.items(editorial={}, models={}, pricing={}, eco={})]
        self.assertEqual(len(questions), 3)  # winner, channels and Index remain supported by summary rows
        self.assertFalse(any("own servers" in q or "evaluated" in q or "cost?" in q for q in questions))
        self.assertEqual(self.items(rows=[]), [])

    def test_ecocost_keeps_partial_scope_and_missing_values(self):
        answer = dict(self.items())["What is the environmental impact of Example AI models?"]
        self.assertIn("1 of the 2", answer)
        self.assertIn("low confidence", answer)
        self.assertIn("direct-audio inference are excluded", answer)
        self.assertIn("missing estimates are not zero", answer)
        uncovered = {"workflows": [{"coverage": "not_covered"}]}
        self.assertIn("no covered text-model estimates", dict(self.items(eco=uncovered))[
            "What is the environmental impact of Example AI models?"])

    def test_escape_editorial_text_and_preserve_native_controls(self):
        page = self.page | {"lang": "A&B <Language>"}
        items = self.items(page=page, editorial=self.editorial | {"dataset_description": "<script>unsafe</script>"})
        html = render_faq((build.SRC / "faq.tmpl").read_text(), items)
        self.assertIn("A&amp;B &lt;Language&gt;", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertEqual(html.count("<summary>"), 8)
        self.assertEqual(html.count("<details open>"), 8)
        self.assertNotIn("{{", html)

    def test_score_rounding_matches_charts(self):
        self.assertEqual(score(0.825), 83)
        self.assertEqual(score(0.62666667), 63)

    def test_clinical_caveat_is_shared_not_language_metadata(self):
        answer = dict(self.items())["How were the Example AI models evaluated?"]
        self.assertIn(CLINICAL_SAFETY_CAVEAT, answer)
        self.assertIn("the dataset is small.", answer)

    def test_all_language_pages_share_eight_questions_and_local_context(self):
        for slug in build.slugs():
            with self.subTest(slug=slug):
                html = build.render(slug)
                section = html.split('id="faq"', 1)[1].split("</section>", 1)[0]
                self.assertEqual(section.count("<summary>"), 8)
                self.assertNotIn("Does ChatGPT", section)
                self.assertNotIn("still being verified", section)
                self.assertIn(CLINICAL_SAFETY_CAVEAT, section)
                self.assertEqual(section.count(CLINICAL_SAFETY_CAVEAT), 1)
                page = json.loads((build.SRC / slug / "page.json").read_text())
                self.assertIn(f"data/{page['code']}/ecocost-{page['snapshot']}.json", section)
                self.assertNotIn(f"data/{page['code']}/pricing-{page['snapshot']}.json", section)
                self.assertIn("Coming soon", section)
                self.assertNotIn("$", section)
                self.assertIn('"pricingComingSoon": true', html)
                if slug == "kinyarwanda":
                    self.assertIn("22 general-knowledge questions about Kenya and two medical questions", section)
                    self.assertNotIn("health and farming", section)
                if slug == "hausa":
                    self.assertIn("None of the 13 tested Hausa chains met", section)
                    self.assertIn("qualified clinical review", section)


if __name__ == "__main__":
    unittest.main()
