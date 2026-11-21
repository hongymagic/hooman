from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "human-writing"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
from check import (  # noqa: E402 - load standalone bundle
    RULE_IDS,
    allowances,
    audit,
    extract,
    infer_format,
    sentences,
)

PLAIN = (
    "The export writes one CSV file per month. Each row holds the invoice number, "
    "the customer and the amount. Run it from the Billing page, and the file "
    "downloads when the job finishes."
)


def rules(result: dict, severity: str | None = None) -> list[str]:
    return [
        finding["rule"]
        for finding in result["findings"]
        if severity is None or finding["severity"] == severity
    ]


class BlockingRuleTests(unittest.TestCase):
    def test_empty_phrases_and_leftovers_block(self):
        cases = {
            "In today's fast-paced digital world, work changes.": "staging.scene",
            "In today’s fast‑paced digital world, work changes.": "staging.scene",
            "It is important to note that approval is pending.": "staging.announcement",
            "Without further ado, the release notes.": "staging.announcement",
            "We are thrilled to announce the new export.": "staging.announcement",
            "Here's the thing about retries.": "staging.runup",
            "Let's dive into the configuration.": "staging.runup",
            "The result? The export runs twice.": "staging.reveal",
            "It runs twice. Honestly? That is fine.": "staging.reveal",
            "None of this means the cache is wrong.": "staging.concession",
            "The future looks bright for the team.": "staging.closer",
            "No meetings, no approvals, no delays.": "rhythm.negation",
            "The bridge stands as a testament to its builders.": "inflation.significance",
            "The update takes reporting to the next level.": "inflation.significance",
            "Great question! The export runs nightly.": "leftovers.chat",
            "Certainly! The export runs nightly.": "leftovers.chat",
            "Would you like me to add a summary?": "leftovers.chat",
            "As of my last update, the API had two versions.": "leftovers.cutoff",
            "The export runs nightly. contentReference[oaicite:0]": "leftovers.markup",
            "The report includes [needs proof].": "leftovers.placeholder",
            "Contact [Your Name] for access.": "leftovers.placeholder",
            "Let me think step by step about the order.": "leftovers.reasoning",
        }
        for source, rule in cases.items():
            with self.subTest(source=source):
                result = audit(source)
                self.assertFalse(result["passed"])
                self.assertIn(rule, rules(result, "error"))

    def test_plain_prose_and_useful_devices_have_no_findings(self):
        for source in (
            PLAIN,
            "What happens after a crash? The event may arrive again. Record the ID, "
            "confirm the owner and keep the fallback enabled. The key was rotated—its "
            "owner is unknown.",
            "It isn't raining. Take the bike.",
            "The server did not restart. It logged the error and kept serving requests.",
            "However, existing work covers the manufacturing and processing sectors.",
            "The endpoint accepts JSON, including nested arrays, according to the schema.",
            "Certainly the export can run twice a day.",
            "Honestly, the migration was dull.",
        ):
            with self.subTest(source=source):
                self.assertEqual(audit(source)["findings"], [])

    def test_no_single_word_blocks(self):
        for word in (
            "Delve",
            "tapestry",
            "robust",
            "seamlessly",
            "game-changing",
            "genuinely",
        ):
            with self.subTest(word=word):
                result = audit(f"{word} appears once in this sentence about exports.")
                self.assertTrue(result["passed"])
                self.assertEqual(result["review"], 1)

    def test_explicit_inflections_and_word_boundaries(self):
        for word in (
            "delves",
            "delved",
            "delving",
            "revolutionises",
            "supercharged",
            "utilizing",
        ):
            with self.subTest(word=word):
                self.assertEqual(audit(word)["review"], 1)
        for word in (
            "Delvecchio",
            "revolution",
            "supercharger",
            "unlockable",
            "landscaper",
            "journeyman",
        ):
            with self.subTest(word=word):
                self.assertEqual(audit(word)["findings"], [])

    def test_common_words_count_only_in_clusters(self):
        single = audit("The review is crucial for the release and the export.")
        self.assertEqual(single["findings"], [])
        clustered = audit(
            "The platform offers comprehensive insights and plays a crucial part in "
            "a vibrant landscape of tools that enhance every vital workflow."
        )
        self.assertIn("inflation.cluster", rules(clustered, "error"))
        spread = audit(
            "The review is crucial. "
            + PLAIN * 4
            + " The guide is comprehensive. "
            + PLAIN * 4
            + " The landscape changed. "
            + PLAIN * 4
            + " The team is vital."
        )
        self.assertNotIn("inflation.cluster", rules(spread))

    def test_contrast_frames_block_only_when_they_recur(self):
        once = audit("It isn't a timeout, it is a refused connection. " + PLAIN)
        self.assertEqual(rules(once), ["staging.contrast"])
        self.assertTrue(once["passed"])
        repeated = audit(
            "The hard part wasn't the pipelines. It was the secrets. The test wasn't "
            "flaky. It was a real race. The fix is a config file, not another comment."
        )
        self.assertIn("staging.contrasts", rules(repeated, "error"))
        self.assertEqual(rules(repeated).count("staging.contrast"), 3)

    def test_trailing_clauses_block_only_when_they_recur(self):
        twice = audit(
            "The cache stores each response, reducing the load on the database. "
            "It expires entries after a minute, keeping the data fresh. " + PLAIN
        )
        self.assertEqual(twice["findings"], [])
        recurring = audit(
            "The cache stores each response, reducing the load on the database. "
            "It expires entries after a minute, keeping the data fresh. "
            "The worker retries failed jobs, ensuring that no message is lost."
        )
        self.assertIn("inflation.tails", rules(recurring, "error"))
        self.assertEqual(rules(recurring).count("inflation.tail"), 3)

    def test_dense_review_findings_block(self):
        source = (
            "The update is seamless. Notably, it works offline. Whether you are new "
            "or experienced, it helps. Here's why. It is truly quiet. At its core it "
            "is a queue. This matters. Experts say 40% faster results follow."
        )
        result = audit(source)
        self.assertIn("density.signals", rules(result, "error"))
        self.assertIn("evidence.attribution", rules(result))
        relaxed = audit(
            source, allowed=allowances(["staging.runup=The author's own openers"])
        )
        self.assertNotIn("density.signals", rules(relaxed))
        self.assertTrue(relaxed["passed"])

    def test_formatting_and_evidence_never_count_towards_density(self):
        report = """## Incident Timeline And Impact

## Root Cause And Next Steps

- **09:10** deploy began.
- **09:12** alerts fired.
- **10:41** rollback finished.

---

---

---

Studies show 12 customers saw errors. Experts say 40% faster recovery is possible.
"""
        result = audit(report, "markdown")
        self.assertTrue(result["passed"])
        self.assertGreaterEqual(result["review"], 6)
        self.assertNotIn("density.signals", rules(result))

    def test_repeated_sentence(self):
        source = "The export includes all archived invoices. The export includes all archived invoices."
        result = audit(source)
        self.assertEqual(rules(result), ["rhythm.repeat"])
        self.assertFalse(result["passed"])
        masked = "The `first` view is overridden by this setting. The `second` view is overridden by this setting."
        self.assertEqual(audit(masked, "markdown")["findings"], [])

    def test_allowance_retains_finding_and_reason(self):
        result = audit(
            "It is worth noting that Delve is a command.",
            allowed=allowances(["staging.announcement=Quoted from the changelog"]),
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["blocking"], 0)
        announcement = next(
            f for f in result["findings"] if f["rule"] == "staging.announcement"
        )
        self.assertEqual(announcement["allowance"], "Quoted from the changelog")
        for value in (
            "staging.announcement=",
            "unknown=Reason",
            "staging.announcement",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                allowances([value])


class ReviewRuleTests(unittest.TestCase):
    def test_context_dependent_phrases_stay_advisory(self):
        cases = {
            "The headline number: builds now take seven minutes.": "staging.reveal",
            "I'm not saying the cache is wrong.": "staging.concession",
            "Some might argue the cache is wrong.": "staging.strawman",
            "At its core, the cache is a map.": "staging.depth",
            "This matters for the release.": "staging.signpost",
            "In conclusion, the cache is a map.": "staging.closer",
            "So the next time you open a review, start there.": "staging.closer",
            "We heard you, so the export is back.": "staging.runup",
            "Caching plays a key role in the design.": "inflation.significance",
            "The gallery serves as an exhibition space.": "inflation.copula",
            "The colours are blue and gold, reflecting the coast.": "inflation.tail",
            "The cache could potentially reduce latency.": "inflation.hedge",
            "Simply click the button to continue.": "inflation.intensifier",
            "I hope this helps with the migration.": "leftovers.courtesy",
            "In this article, we will look at caching.": "leftovers.meta",
            "We surveyed 12 customers last month.": "evidence.numbers",
            "Studies show the cache helps.": "evidence.attribution",
        }
        for source, rule in cases.items():
            with self.subTest(source=source):
                result = audit(source)
                self.assertTrue(result["passed"])
                self.assertIn(rule, rules(result, "review"))

    def test_rhythm_findings(self):
        fragments = audit(
            "The release went out on Friday as planned. No fuss. No drama. No rollbacks."
        )
        self.assertIn("rhythm.fragments", rules(fragments, "review"))
        questions = audit(
            "A reviewer should ask harder questions. Does this belong here? What "
            "happens when the requirements change? Who will debug it at night?"
        )
        self.assertIn("rhythm.questions", rules(questions, "review"))
        closers = audit(
            "\n\n".join(
                f"The {name} stage takes longer than the team planned for it. {closer}"
                for name, closer in (
                    ("build", "That is the point."),
                    ("test", "It always does."),
                    ("deploy", "Nobody minds much."),
                )
            )
        )
        self.assertIn("rhythm.closers", rules(closers, "review"))
        dashes = audit("The key — rotated last week — has no owner — yet.")
        self.assertIn("rhythm.dashes", rules(dashes, "review"))
        ordinary = audit(
            "The key — rotated last week — has no owner. The log — kept for a year — is full."
        )
        self.assertEqual(ordinary["findings"], [])
        self.assertGreater(ordinary["stats"]["em_dashes_per_1000"], 100)
        uniform = audit(
            " ".join(
                f"The {name} service handles requests from the gateway every single day."
                for name in "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima".split()
            )
        )
        self.assertIn("rhythm.uniform", rules(uniform, "review"))
        self.assertEqual(uniform["stats"]["sentences"], 12)

    def test_formatting_findings_apply_to_markdown_only(self):
        source = """# Release Notes

## What We Shipped This Week

- **Speed:** builds finish sooner.
- **Safety:** secrets moved to roles.
- **Scope:** fourteen pipelines moved.

---

## Where The Time Went

The **build** and the **test** and the **deploy** and the **cache** stages moved.
The **lint** and the **scan** and the **pack** and the **ship** stages stayed.

---

## 🚀 What Comes Next For Us

---

#DevOps #GitHubActions #Jenkins #CloudSecurity
"""
        found = rules(audit(source, "markdown"), "review")
        for rule in (
            "formatting.labels",
            "formatting.bold",
            "formatting.titlecase",
            "formatting.rules",
            "formatting.hashtags",
            "formatting.emoji",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, found)
        plain = "## How to install\n\n## What's new\n\n- **Speed:** builds finish sooner.\n"
        self.assertEqual(audit(plain, "markdown")["findings"], [])
        self.assertEqual(
            audit(
                "<h2>What We Shipped This Week</h2><h2>Where The Time Went</h2>", "html"
            )["findings"],
            [],
        )

    def test_pitch_phrasing_stays_advisory(self):
        cases = {
            "The dashboard is powerful and intuitive.": "pitch.praise",
            "The export helps you close the month.": "pitch.benefit",
            "Tag each run so you can find it later.": "pitch.benefit",
            "The checks let teams deploy with confidence.": "pitch.benefit",
            "The importer makes it easy to move accounts.": "pitch.benefit",
            "Set up the importer in minutes.": "pitch.benefit",
            "Ready to move your accounts? Sign up today.": "pitch.call",
        }
        for source, rule in cases.items():
            with self.subTest(source=source):
                result = audit(source)
                self.assertTrue(result["passed"])
                self.assertIn(rule, rules(result, "review"))
        for source in (
            "The interval is reported with confidence limits of 95%.",
            "The flag allows the caller to skip validation.",
            "The job finishes in 4 minutes.",
            "Tag each run so that the scheduler can find it.",
            "A robust estimator ignores the outliers.",
        ):
            with self.subTest(source=source):
                self.assertNotIn("pitch.benefit", rules(audit(source)))
                self.assertNotIn("pitch.call", rules(audit(source)))

    def test_headings_that_pitch_are_reported_one_by_one(self):
        for heading in (
            "Try the checker",
            "Get started",
            "Works where you work",
            "Why Harbour",
            "What it is built on",
            "Ready to switch?",
            "Passwords for the whole team, safely.",
            "**Meet the importer**",
        ):
            with self.subTest(heading=heading):
                result = audit(f"# tidewatch\n\n## {heading} ##\n\n{PLAIN}", "markdown")
                self.assertEqual(rules(result), ["pitch.heading"])
                self.assertTrue(result["passed"])
                self.assertEqual(result["findings"][0]["text"], heading.strip("*"))
        numbered = audit(f"## 3) Describe your changes\n\n{PLAIN}", "markdown")
        self.assertEqual(
            [(f["rule"], f["text"], f["column"]) for f in numbered["findings"]],
            [("pitch.heading", "Describe your changes", 7)],
        )
        labels = (
            "# tidewatch\n\n## Installation\n\n## Getting started\n\n## How to release"
            "\n\n## What's new\n\n## What is an edition?\n\n## Build instructions\n\n"
            "## Use cases\n\n## Tabs or spaces?\n\n" + PLAIN
        )
        self.assertEqual(audit(labels, "markdown")["findings"], [])

    def test_pitch_headings_block_when_they_recur(self):
        page = (
            "# Harbour\n\n## Try it with your team\n\n## Why Harbour\n\n"
            "## Get a quote\n\n## Pricing\n\n" + PLAIN
        )
        result = audit(page, "markdown")
        self.assertIn("pitch.headings", rules(result, "error"))
        self.assertEqual(rules(result).count("pitch.heading"), 3)
        self.assertIn(
            "3 of 5 headings address or sell to the reader",
            [finding["text"] for finding in result["findings"]],
        )
        # Three in a long reference document are a small share of its headings.
        reference = page + "".join(f"\n\n## Option {n}\n\n{PLAIN}" for n in range(9))
        self.assertNotIn("pitch.headings", rules(audit(reference, "markdown")))
        allowed = audit(
            page, "markdown", allowances(["pitch.headings=Landing page; headings are the copy"])
        )
        self.assertTrue(allowed["passed"])

    def test_instruction_headings_are_advisory(self):
        steps = "# tidewatch\n\n## Install\n\n## Configure the bucket\n\n## Run it\n\n" + PLAIN
        result = audit(steps, "markdown")
        self.assertEqual(rules(result), ["formatting.instructions"])
        self.assertTrue(result["passed"])
        self.assertEqual(
            result["findings"][0]["text"], "3 of 3 subheadings are instructions"
        )
        one = "# tidewatch\n\n## Install the binary\n\n## Options\n\n" + PLAIN
        self.assertEqual(audit(one, "markdown")["findings"], [])

    def test_particulars_are_counted_from_figures_names_code_and_links(self):
        general = (
            "The system keeps the work moving for the people who rely on it. It brings "
            "the pieces together in a way that feels natural. Each part plays its role "
            "and the whole becomes more than the parts. The approach is simple by "
            "design. The team can spend its time on the work that matters most to it."
        )
        result = audit(f"{general}\n\n{general}\n\n{general}", "markdown")
        self.assertTrue(result["passed"])
        self.assertEqual(result["stats"]["particulars_percent"], 0)
        found = {finding["rule"]: finding["text"] for finding in result["findings"]}
        self.assertEqual(
            found["particulars.share"],
            "0 of 15 sentences carry a number, a name, code or a link",
        )
        self.assertEqual(rules(result).count("particulars.run"), 3)
        self.assertEqual(
            found["particulars.run"],
            "5 sentences from: The system keeps the work moving for the people who rely on ",
        )
        self.assertNotIn("density.signals", rules(result))
        specific = (
            "The export writes 12 files a year. Run `make export` to start it. The "
            "Billing page links to [the schedule](https://example.com/schedule). Priya "
            "Nair approved the change on Tuesday. The API returns a 429 when the limit "
            "is reached."
        )
        result = audit(f"{specific}\n\n{specific} Next.\n\n{specific} Last.", "markdown")
        self.assertEqual(result["stats"]["particulars_percent"], 100)
        self.assertNotIn("particulars.share", rules(result))
        self.assertNotIn("particulars.run", rules(result))
        # A list number and a capital at the head of a sentence are not particulars.
        listed = "1. Keep the reader in mind when the work begins.\n2. Read it again the next day."
        self.assertEqual(audit(listed, "markdown")["stats"]["particulars_percent"], 0)
        # Fewer than twelve counted sentences is too few to judge a share.
        self.assertNotIn("particulars.share", rules(audit(general, "markdown")))

    def test_soft_line_breaks_join_sentences(self):
        wrapped = "The hard part wasn't the\npipelines. It was the secrets."
        self.assertEqual(rules(audit(wrapped, "markdown")), ["staging.contrast"])
        run = "Ship it now. Do it today. Tell them all."
        self.assertEqual(rules(audit(run, "markdown")), ["rhythm.fragments"])
        separate = run.replace(". ", ".\n\n")
        self.assertEqual(audit(separate, "markdown")["findings"], [])

    def test_sentence_boundaries_respect_abbreviations(self):
        text = "See e.g. Smith vs. Jones. Dr. Who agreed. It works (v1.2). Then stop."
        found = [text[s.start : s.end] for s in sentences(text, 0)]
        self.assertEqual(
            found,
            [
                "See e.g. Smith vs. Jones.",
                "Dr. Who agreed.",
                "It works (v1.2).",
                "Then stop.",
            ],
        )


class InterfaceProfileTests(unittest.TestCase):
    def test_interface_strings(self):
        source = "\n".join(
            (
                "Where the time went",
                "Why this?",
                "What is your email?",
                "Each bar is a question. The line is the pace.",
                "Start with Standard Test 11: 9",
                "Progress at a glance",
                "Simply tap a bar to see more",
                "40 minutes shared across 35 questions",
                "Saved. You can close this tab.",
            )
        )
        result = audit(source, profile="interface")
        self.assertTrue(result["passed"])
        self.assertEqual(
            [(f["line"], f["rule"]) for f in result["findings"]],
            [
                (1, "interface.figure"),
                (2, "interface.heading"),
                (4, "interface.pair"),
                (5, "interface.shorthand"),
                (6, "interface.figure"),
                (7, "interface.filler"),
            ],
        )

    def test_prose_rules_stay_out_of_interface_copy(self):
        strings = "No tests yet\nNo practice this week\nNo timing data yet\nThat is the point."
        self.assertEqual(audit(strings, profile="interface")["findings"], [])
        leftover = audit("Great question! Here is your label.", profile="interface")
        self.assertIn("leftovers.chat", rules(leftover, "error"))


class ExtractionTests(unittest.TestCase):
    def test_markdown_literals_are_excluded(self):
        source = """---
title: It is worth noting
---
The export accepts compressed invoices.

```python
print("None of this means anything")
```

~~~text
It is worth noting that this is a specimen.
~~~

> Let's dive into a specimen.

    Let's dive into indented code.

`delve` and ``it is worth noting `sample` `` are examples.
~~Let's dive in~~ is struck out.
[Documentation](https://example.test/delve_(tapestry) "delve") explains exports.
[An example][delve]
[delve]: https://example.test/tapestry
<!-- Let's dive into comments. -->
"""
        self.assertEqual(audit(source, "markdown")["findings"], [])

    def test_link_labels_and_inline_quotes_are_checked(self):
        for source in (
            "[Let's dive in](https://example.test)",
            'The title is "Let\'s dive in".',
        ):
            with self.subTest(source=source):
                self.assertFalse(audit(source, "markdown")["passed"])

    def test_fence_inside_fence_and_unclosed_fence(self):
        source = "````text\n```\nLet's dive in\n```\n````\nThe export runs."
        self.assertEqual(audit(source, "markdown")["findings"], [])
        with self.assertRaises(ValueError):
            audit("```text\nLet's dive in", "markdown")

    def test_html_hidden_content_and_void_elements(self):
        source = """<html><head><title>Delve</title></head><body>
<div hidden><br><b>Let's dive in</b></div>
<div aria-hidden="true">Delve</div><p style="display: none !important">Delve</p>
<p style="visibility:hidden">Delve</p><script>Delve</script>
<style>.Delve {color:red}</style><template>Delve</template><svg>Delve</svg>
<pre>Delve</pre><code>Delve</code><!-- Delve -->
<p aria-hidden>Invoices can be exported.</p><img alt="Delve">
</body></html>"""
        self.assertEqual(audit(source, "html")["findings"], [])

    def test_html_entities_inline_tags_and_locations(self):
        source = "<p>Exports run.</p>\n<p>D&#101;l<span>v</span>e into invoices.</p>"
        result = audit(source, "html")
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(result["findings"][0]["text"], "Delve")
        self.assertEqual(
            (result["findings"][0]["line"], result["findings"][0]["column"]), (2, 4)
        )

    def test_blocks_do_not_merge_words(self):
        self.assertEqual(audit("<p>Del</p><p>ve</p>", "html")["findings"], [])

    def test_markdown_source_locations_survive_masks(self):
        result = audit("# Export\n\n`tapestry` Delve into invoices.", "markdown")
        self.assertEqual(
            (result["findings"][0]["line"], result["findings"][0]["column"]), (3, 12)
        )

    def test_empty_extracted_documents_fail(self):
        for source, format in (
            ("", "text"),
            ("  \n", "text"),
            ("<script>Delve</script>", "html"),
            ("`Delve`", "markdown"),
        ):
            with self.subTest(format=format), self.assertRaises(ValueError):
                audit(source, format)

    def test_format_inference(self):
        self.assertEqual(infer_format("draft.MD"), "markdown")
        self.assertEqual(infer_format("page.htm"), "html")
        self.assertEqual(infer_format("draft.txt"), "text")
        self.assertEqual(infer_format("page.html", "text"), "text")


class ReviewedCaseTests(unittest.TestCase):
    """Inputs an independent review found mishandled: false passes, then false blocks."""

    def test_prose_after_a_lone_backtick_or_less_than_sign_is_read(self):
        announcement = "It is important to note that the future is bright."
        for source in (
            f"Use the ` character to quote names.\n\n{announcement}\n\nRun `make` to build.",
            f"Latency fell when n<k for every shard.\n\n{announcement}",
        ):
            with self.subTest(source=source):
                self.assertEqual(
                    rules(audit(source, "markdown"), "error"),
                    ["staging.announcement", "staging.closer"],
                )
        inline = "Text <b>bold</b> and <br> break. It is worth noting that x<y and y>z holds."
        self.assertEqual(rules(audit(inline, "markdown")), ["staging.announcement"])
        self.assertEqual(
            extract("Latency fell when n<k for every shard.", "markdown").text,
            "Latency fell when n<k for every shard.",
        )

    def test_footnotes_and_text_after_an_opening_rule_are_read(self):
        for source in (
            "The export runs.[^1]\n\n[^1]: It is important to note that it runs nightly.",
            "---\n\nIt is important to note that it runs.\n\n---\n\nMore text here.",
        ):
            with self.subTest(source=source):
                self.assertEqual(
                    rules(audit(source, "markdown")), ["staging.announcement"]
                )

    def test_cluster_counts_a_word_that_another_rule_reports(self):
        for noun in ("importance", "value"):
            with self.subTest(noun=noun):
                source = (
                    f"This underscores the {noun} of a holistic, multifaceted and "
                    "nuanced approach to the work."
                )
                self.assertIn("inflation.cluster", rules(audit(source), "error"))

    def test_sentence_ending_in_no_and_questions_in_curly_quotes(self):
        repeated = "We asked twice and the answer was no. We asked twice and the answer was no."
        self.assertEqual(rules(audit(repeated)), ["rhythm.repeat"])
        for opening, closing in ("“”", '""'):
            with self.subTest(opening=opening):
                source = " ".join(
                    f"{opening}Is it {word}?{closing}"
                    for word in ("fast", "cheap", "good")
                )
                self.assertIn("rhythm.questions", rules(audit(source)))

    def test_tracking_parameter_is_found_inside_a_link_target(self):
        target = "https://example.com/r?utm_source=chatgpt.com"
        for source, format in (
            (f"Read [the report]({target}) today.", "markdown"),
            (f"Read <{target}> today.", "markdown"),
            (f"Read {target} today.", "text"),
            (f'<p>Read <a href="{target}">the report</a> today.</p>', "html"),
            (f'<p>Read <a href="{target}" hidden>the report</a> today.</p>', "html"),
        ):
            with self.subTest(source=source):
                result = audit(source, format)
                if "hidden" in source:
                    self.assertEqual(result["findings"], [])
                    continue
                self.assertEqual(rules(result, "error"), ["leftovers.markup"])
                finding = result["findings"][0]
                self.assertEqual(finding["text"], "utm_source=chatgpt.com")
                self.assertEqual(finding["column"], source.index("utm_source") + 1)

    def test_openers_in_list_items_and_emphasis_and_hyphenated_negation(self):
        listed = audit(
            "- Certainly! Here is the list.\n\n**Certainly!** Done.", "markdown"
        )
        self.assertEqual(rules(listed), ["leftovers.chat", "leftovers.chat"])
        negation = audit("No sign-up. No lock-in. No catch.")
        self.assertIn("rhythm.negation", rules(negation, "error"))
        reveal = audit(
            "It ran twice. The result? Two files. And the kicker? Nobody noticed."
        )
        self.assertEqual(rules(reveal, "error"), ["staging.reveal", "staging.reveal"])
        chat = audit("As an AI language model, I cannot browse.")
        self.assertEqual(rules(chat, "error"), ["leftovers.chat"])

    def test_ordinary_text_that_resembles_a_leftover_passes(self):
        for source in (
            "See [Your account](https://example.com/account) and [Insert menu][ref].",
            "She joined the lab as an AI researcher in 2019.",
            "How do we verify the result?",
            "We shipped on Friday, something the team had wanted for years. It left "
            "the desk clear, everything in its place. We read the logs, nothing in "
            "them looked wrong.",
        ):
            with self.subTest(source=source):
                self.assertEqual(audit(source, "markdown")["findings"], [])

    def test_ampersand_without_an_entity_keeps_its_sentence(self):
        source = "We fund R&D. Then AT&T called. Tom &amp; Jerry agreed."
        text = extract(source, "markdown").text
        self.assertEqual(text, "We fund R&D. Then AT&T called. Tom & Jerry agreed.")
        self.assertEqual(len(sentences(text, 0)), 3)


class SecondReviewTests(unittest.TestCase):
    """Inputs a second independent review found mishandled."""

    ANNOUNCEMENT = "It is important to note that the future is bright."
    BOTH = ["staging.announcement", "staging.closer"]

    def errors(self, source: str, format: str = "markdown") -> list[str]:
        return rules(audit(source, format), "error")

    def test_carriage_returns_change_nothing(self):
        for source in (
            f"Intro line.\n\n```sh\nmake\n```\n\n{self.ANNOUNCEMENT}\n",
            f"Use the ` key here.\n\n{self.ANNOUNCEMENT}\n\nPress ` again.\n",
        ):
            for ending in ("\r\n", "\r"):
                with self.subTest(source=source, ending=ending):
                    self.assertEqual(
                        self.errors(source.replace("\n", ending)), self.BOTH
                    )
        front = "---\ntitle: Notes\nsummary: It is worth noting\n---\nThe export runs.\n"
        self.assertEqual(audit(front.replace("\n", "\r\n"), "markdown")["findings"], [])
        finding = audit("First line.\r\nIt is worth noting that it runs.\r\n")["findings"][0]
        self.assertEqual((finding["line"], finding["column"]), (2, 1))

    def test_a_less_than_sign_never_swallows_the_text_after_it(self):
        opening = "Throughput drops when n<k for every shard."
        for source in (
            f"{opening} {self.ANNOUNCEMENT} Use the -> operator to chain.",
            f"{opening}\n\n{self.ANNOUNCEMENT}\n\nThen x > y.",
        ):
            with self.subTest(source=source):
                self.assertEqual(self.errors(source), self.BOTH)

    def test_a_tag_named_in_passing_does_not_hide_what_follows(self):
        for tag in (
            "<pre>",
            "\\<pre>",
            "<head>",
            "<code>",
            "<script>",
            "<style>",
            "<template>",
            "<svg>",
            "<noscript>",
            "<div hidden>",
            "<!--",
            "<!DOCTYPE",
            "<?",
            "<![CDATA[",
        ):
            with self.subTest(tag=tag):
                source = f"Use the {tag} form with care.\n\n{self.ANNOUNCEMENT}"
                self.assertEqual(self.errors(source), self.BOTH)
        for source in (
            f"<p>Start with <!-- and end later.</p><p>{self.ANNOUNCEMENT}</p>",
            # An end tag HTML lets the author omit still ends the element.
            f"<p>Lead.</p><ul><li hidden>Old item<li>{self.ANNOUNCEMENT}</ul>",
            f"<html><head><title>T</title><body><p>{self.ANNOUNCEMENT}</p></body></html>",
            f"<table><tr><td hidden>Old<td>{self.ANNOUNCEMENT}</table>",
            # A marked section crashed the parser of some Python releases.
            f"<p>Lead.</p>\n<![ x ]>\n<![if !vml]><p>{self.ANNOUNCEMENT}</p><![endif]>",
        ):
            with self.subTest(source=source):
                self.assertEqual(self.errors(source, "html"), self.BOTH)
        hidden = f"<pre>{self.ANNOUNCEMENT}</pre><p>The export runs.</p>"
        self.assertEqual(audit(hidden, "html")["findings"], [])

    def test_link_definitions_and_front_matter_are_told_from_prose(self):
        self.assertEqual(
            self.errors(f"[Editor]: {self.ANNOUNCEMENT}\n\nPlain sentence here."),
            self.BOTH,
        )
        self.assertEqual(
            self.errors("[10:42]: It is worth noting that the deploy began."),
            ["staging.announcement"],
        )
        source = "[The report][r] is out.\n\n[r]: https://example.com/?utm_source=chatgpt.com"
        finding = audit(source, "markdown")["findings"][0]
        self.assertEqual(finding["rule"], "leftovers.markup")
        self.assertEqual(
            (finding["line"], finding["column"]),
            (3, source.splitlines()[2].index("utm_source") + 1),
        )
        heading = f"---\n# Weekly notes\n\n{self.ANNOUNCEMENT}\n\n---\n\nThe export runs.\n"
        self.assertEqual(self.errors(heading), self.BOTH)
        commented = "---\n# generated\ntitle: It is worth noting\n---\nThe export runs.\n"
        self.assertEqual(audit(commented, "markdown")["findings"], [])

    def test_placeholders_side_by_side_are_both_reported(self):
        for format in ("markdown", "text"):
            with self.subTest(format=format):
                self.assertEqual(
                    self.errors("Contact [Your Name][Your Email] today.", format),
                    ["leftovers.placeholder"] * 2,
                )
        self.assertEqual(
            self.errors("Contact [Your Name][^1] today."), ["leftovers.placeholder"]
        )

    def test_sentence_openers_after_quotes_brackets_and_markers(self):
        for source, format in (
            ('He asked "why now?" The result? Silence.', "text"),
            ("## The result?\n\nTwo files were written by the job.", "markdown"),
            ("(It ran twice.) The result? Two files.", "text"),
            ("**It ran twice.** The result? Two files.", "markdown"),
            ("- [ ] The result? Two files.", "markdown"),
            ("***The result?*** Two files.", "markdown"),
            ("| Step | The result? Two files. |", "markdown"),
            ('It ran. ("The result? Two files.")', "text"),
        ):
            with self.subTest(source=source):
                self.assertEqual(self.errors(source, format), ["staging.reveal"])

    def test_a_finding_points_at_its_words_not_the_marker_before_them(self):
        for source, format, column, text in (
            ("`x` Certainly! Here is the list.", "markdown", 5, "Certainly!"),
            ("  Certainly! Here is the list.", "text", 3, "Certainly!"),
            ("~~old~~ The result? Two files.", "markdown", 9, "The result?"),
            ("    - The result? Two files.", "text", 7, "The result?"),
            ("- **Certainly!** Done.", "markdown", 5, "Certainly!"),
        ):
            with self.subTest(source=source):
                finding = next(
                    found
                    for found in audit(source, format)["findings"]
                    if found["severity"] == "error"
                )
                self.assertEqual((finding["column"], finding["text"]), (column, text))


class ContractTests(unittest.TestCase):
    def test_every_rule_is_documented(self):
        reference = (SKILL / "references" / "checker.md").read_text(encoding="utf-8")
        for rule in sorted(RULE_IDS):
            with self.subTest(rule=rule):
                self.assertIn(f"`{rule}`", reference)

    def test_worst_case_inputs_stay_fast(self):
        cases = (
            "This is not just a thing " * 3000,
            "no time, no money, no luck, " * 3000,
            "It ran, highlighting the result. " * 3000,
            "Why? " * 15000,
            "delve crucial robust landscape vital insights " * 2000,
            "](" * 25000,
            "[insert " * 10000,
            "[a](b(c(d " * 8000,
            "- **Label:** text here\n" * 4000,
            "word " * 30000,
            "1," * 20000,
            "1" * 40000 + " % faster",
            "?" * 40000,
            "a" * 40000,
            "x" + "`" * 30000,
            "vital-" * 8000,
            "robust-and-seamless-" * 2400,
            "<a b" + " b" * 20000,
            '<a b="' * 10000,
            "## " + "a b c " * 10000,
            "## Why " + "a " * 30000,
            "## Try a\n" * 6000,
            "helps you so you can " * 6000,
            "built for a a a " * 6000,
            "ready to a " * 8000,
            "A B c " * 10000,
            "a b c d. " * 8000,
        )
        pages = (
            "<b>" * 8000 + "Text here." + "</i>" * 6000,
            "<dd><dl>" + "<b>" * 8000 + "<dd></dd>" * 6000 + "x",
            "<pre>" * 10000 + "x y z",
            "<a " * 16000,
            "<![" * 20000 + "x",
            "<!--" * 15000 + "x",
        )
        started = time.perf_counter()
        for source, format in [
            *((source, "markdown") for source in cases),
            *((source, "html") for source in pages),
        ]:
            try:
                audit(source, format)
            except ValueError:
                pass
        # Typical total is under two seconds; quadratic matching took minutes.
        self.assertLess(time.perf_counter() - started, 30)


class CheckerCLITests(unittest.TestCase):
    def run_cli(self, *args, input=None):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "check.py"), *args],
            input=input,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_cli_statuses_and_json(self):
        for source, status in (
            ("The import runs.", 0),
            ("It is worth noting that the import runs.", 1),
            ("", 2),
        ):
            with self.subTest(source=source):
                result = self.run_cli("--text", source, "--json")
                payload = json.loads(result.stdout)
                self.assertEqual(result.returncode, status)
                self.assertEqual(payload["passed"], status == 0)
                self.assertEqual(payload["schema_version"], 2)
                self.assertEqual(result.stderr, "")
        payload = json.loads(
            self.run_cli(
                "--text", "It is worth noting that Delve runs.", "--json"
            ).stdout
        )
        self.assertEqual(
            (payload["results"][0]["blocking"], payload["results"][0]["review"]), (1, 1)
        )

    def test_text_report_names_the_gate_not_a_score(self):
        result = self.run_cli("--text", "It is worth noting that Delve runs.")
        self.assertIn("needs editing; 7 words; 1 blocking, 1 to review", result.stdout)
        self.assertIn("[staging.announcement] error", result.stdout)
        self.assertIn(
            "pass; 3 words", self.run_cli("--text", "The import runs.").stdout
        )

    def test_stdin_format_override_profile_and_strict_review(self):
        result = self.run_cli(
            "-", "--format", "markdown", input="`It is worth noting` is a phrase."
        )
        self.assertEqual(result.returncode, 0)
        result = self.run_cli("--text", "Use a robust estimator.", "--strict", "--json")
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["results"][0]["blocking"], 0)
        # The report, the per-file result and the exit status agree under --strict.
        self.assertFalse(payload["passed"])
        self.assertFalse(payload["results"][0]["passed"])
        result = self.run_cli("--text", "Use a robust estimator.", "--strict")
        self.assertEqual(result.returncode, 1)
        self.assertIn("needs review; 4 words; 0 blocking, 1 to review", result.stdout)
        marked = "﻿---\ntitle: It is worth noting\n---\nThe export runs.\n"
        result = self.run_cli("-", "--format", "markdown", input=marked)
        self.assertEqual(result.returncode, 0)
        self.assertIn("pass; 3 words", result.stdout)
        # Standard input keeps its carriage returns; a fence must still close.
        returns = "Intro.\r\n\r\n```sh\r\nmake\r\n```\r\n\r\nIt is worth noting that it runs.\r\n"
        result = self.run_cli("-", "--format", "markdown", input=returns)
        self.assertEqual(result.returncode, 1)
        self.assertIn("[staging.announcement] error", result.stdout)
        result = self.run_cli(
            "--text", "Where the time went", "--profile", "interface", "--json"
        )
        payload = json.loads(result.stdout)["results"][0]
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["profile"], "interface")
        self.assertEqual(payload["review"], 1)

    def test_invalid_requests(self):
        for args in (
            ("--language", "ko", "--text", "안녕하세요"),
            ("--text", "hello", "file.md"),
            ("-", "-"),
            (),
            ("--text", "hello", "--allow", "bad=Reason"),
        ):
            with self.subTest(args=args):
                result = self.run_cli(*args, "--json")
                self.assertEqual(result.returncode, 2)
                self.assertFalse(json.loads(result.stdout)["passed"])

    def test_multifile_errors_do_not_hide_valid_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "draft.md"
            path.write_text("The import runs.", encoding="utf-8-sig")
            result = self.run_cli(
                str(path), str(path.with_name("missing.md")), "--json"
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(len(payload["results"]), 1)
            self.assertEqual(len(payload["errors"]), 1)

    def test_invalid_utf8_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "draft.txt"
            path.write_bytes(b"\xff")
            result = self.run_cli(str(path), "--json")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(len(json.loads(result.stdout)["errors"]), 1)


if __name__ == "__main__":
    unittest.main()
