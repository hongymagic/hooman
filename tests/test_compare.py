from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "human-writing" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from compare import compare  # noqa: E402 - load standalone bundle

ORIGINAL = """# Release plan

It is important to note that we may be able to ship on Friday 14 November, subject to
Security approving the review. We have not approved the wider rollout. Run `make deploy`
after 09:30 UTC. See [the runbook](https://example.test/runbook_(v2)) and email ops@example.test.
Priya Nair said "do not skip the canary". About 1,900 users are affected, 8% of the total.
"""
FAITHFUL = """# Release plan

We may be able to ship on Friday 14 November if Security approves the review; that is
subject to their sign-off. We have not approved the wider rollout. Run `make deploy` after
9:30 UTC. See [the runbook](https://example.test/runbook_(v2)) and email ops@example.test.
Priya Nair said "do not skip the canary". About 1900 users are affected, 8% of the total.
"""
DRIFTED = """# Release plan

We will ship on Friday 14 November once Security approves the review. Run `make release`
after 9:30 UTC. See [the runbook](https://example.test/runbook_(v2)). Priya said the canary
matters. About 1900 users are affected, 18% of the total.
"""


def difference(result: dict, kind: str) -> dict:
    return next(item for item in result["differences"] if item["kind"] == kind)


def kinds(result: dict) -> list[str]:
    return [item["kind"] for item in result["differences"]]


class CompareTests(unittest.TestCase):
    def test_faithful_edit_keeps_every_protected_token(self):
        result = compare(ORIGINAL, FAITHFUL, "markdown", "markdown")
        self.assertTrue(result["passed"])
        self.assertEqual(result["blocking"], 0)
        self.assertEqual(kinds(result), ["modality"])
        self.assertEqual(difference(result, "modality")["note"], "if 0 to 1")

    def test_drift_is_listed_by_kind(self):
        result = compare(ORIGINAL, DRIFTED, "markdown", "markdown")
        self.assertFalse(result["passed"])
        self.assertEqual(difference(result, "numbers")["dropped"], ["8%"])
        self.assertEqual(difference(result, "numbers")["added"], ["18%"])
        self.assertEqual(difference(result, "links")["dropped"], ["ops@example.test"])
        self.assertEqual(difference(result, "code")["dropped"], ["make deploy"])
        self.assertEqual(difference(result, "code")["added"], ["make release"])
        self.assertEqual(
            difference(result, "quotes")["dropped"], ["do not skip the canary"]
        )
        self.assertEqual(difference(result, "names")["dropped"], ["Nair"])
        self.assertEqual(
            difference(result, "negation")["dropped"],
            ["not approved the", "not skip the"],
        )
        self.assertEqual(
            difference(result, "modality")["note"],
            "may 1 to 0, subject to 1 to 0, will 0 to 1",
        )
        self.assertEqual(
            kinds(result),
            ["numbers", "links", "code", "quotes", "names", "negation", "modality"],
        )
        for kind in ("numbers", "links", "code", "quotes"):
            self.assertEqual(difference(result, kind)["severity"], "error")
        for kind in ("names", "negation", "modality"):
            self.assertEqual(difference(result, kind)["severity"], "review")

    def test_number_forms_that_mean_the_same(self):
        same = compare(
            "Three retries, 1,900 users and a 09:05 start.",
            "3 retries, 1900 users and a 9:05 start.",
        )
        self.assertEqual(same["differences"], [])
        changed = compare("It retries five times.", "It retries 50 times.")
        self.assertEqual(difference(changed, "numbers")["dropped"], ["five"])
        self.assertEqual(difference(changed, "numbers")["added"], ["50"])
        listed = compare(
            "Steps:\n\n1. Build\n2. Test",
            "Steps: build, then test.",
            "markdown",
            "markdown",
        )
        self.assertNotIn("numbers", kinds(listed))

    def test_repeated_mention_is_not_a_dropped_fact(self):
        result = compare(
            "Mobile arrives in January. Web is live today. Again: mobile in January, for 1,900 users.",
            "Mobile arrives in January for 1,900 users. Web is live today.",
        )
        self.assertTrue(result["passed"])
        self.assertEqual(difference(result, "mentions")["note"], "January 2 to 1")
        self.assertEqual(difference(result, "mentions")["severity"], "review")

    def test_dropped_claims_show_as_unmatched_sentences_and_vocabulary(self):
        original = (
            "The cache stores each response for sixty seconds. Women voted in large "
            "numbers despite decades of exclusion from public life. Younger voters "
            "queued beside village elders outside the polling stations. Turnout "
            "figures arrive on Thursday."
        )
        trimmed = "The cache stores each response for sixty seconds. Turnout figures arrive on Thursday."
        result = compare(original, trimmed)
        self.assertTrue(result["passed"])
        dropped = difference(result, "sentences")["dropped"]
        self.assertEqual(len(dropped), 2)
        self.assertTrue(dropped[0].startswith("Women voted in large numbers"))
        self.assertTrue(dropped[1].startswith("Younger voters queued beside"))
        self.assertIn(
            "content words no longer appear", difference(result, "vocabulary")["note"]
        )
        reworded = original.replace(
            "stores each response for", "keeps every response for"
        )
        self.assertEqual(compare(original, reworded)["differences"], [])

    def test_flattened_typography_is_reported(self):
        result = compare(
            "Everything’s harder — much harder — when “values” differ.",
            'Everything\'s harder, much harder, when "values" differ.',
        )
        self.assertTrue(result["passed"])
        self.assertEqual(
            difference(result, "typography")["note"],
            "curly quotes 3 to 0, em dashes 2 to 0",
        )

    def test_dates_and_fenced_code(self):
        result = compare(
            "Ship on Tuesday 10 November.\n\n```sh\nmake deploy\n```\n",
            "Ship on Wednesday 10 November.\n\n```sh\nmake deploy --force\n```\n",
            "markdown",
            "markdown",
        )
        self.assertEqual(difference(result, "dates")["dropped"], ["Tuesday"])
        self.assertEqual(difference(result, "dates")["added"], ["Wednesday"])
        self.assertEqual(difference(result, "code")["dropped"], ["make deploy"])
        self.assertEqual(difference(result, "code")["added"], ["make deploy --force"])

    def test_names_ignore_case_changes_headings_and_pronouns(self):
        result = compare(
            "# Getting Started\n\nThe guide covers Billing and the export. I'd run it on Monday.",
            "# Getting started\n\nBilling exports are covered in the Guide. I'm running it on Monday.",
            "markdown",
            "markdown",
        )
        self.assertNotIn("names", kinds(result))
        added = compare("The team shipped it.", "The team at Fernway shipped it.")
        self.assertEqual(difference(added, "names")["added"], ["Fernway"])

    def test_length_and_headings_ask_for_review(self):
        result = compare(
            "# Plan\n\n## Risks\n\n"
            + "The export runs nightly and writes one file. " * 12,
            "# Plan\n\nThe export runs nightly.",
            "markdown",
            "markdown",
        )
        self.assertTrue(result["passed"])
        self.assertEqual(difference(result, "headings")["dropped"], ["risks"])
        self.assertIn("of the original", difference(result, "length")["note"])

    def test_brief_reports_only_what_the_draft_adds(self):
        brief = "Facts about Harbour: $4 per user per month; free for teams of up to 3; SOC 2 Type II audited."
        faithful = "Harbour costs $4 per user per month. Teams of up to 3 pay nothing. It is SOC 2 Type II audited, and $4 is the only price."
        self.assertEqual(compare(brief, faithful, brief=True)["differences"], [])
        unnamed = compare(brief.replace(" about Harbour", ""), faithful, brief=True)
        self.assertEqual(difference(unnamed, "names")["added"], ["Harbour"])
        invented = faithful + " Switch in under 60 seconds with Zero-knowledge sync."
        result = compare(brief, invented, brief=True)
        self.assertFalse(result["passed"])
        self.assertEqual(difference(result, "numbers")["added"], ["60"])
        self.assertEqual(difference(result, "numbers")["dropped"], [])
        self.assertIn("Zero-knowledge", difference(result, "names")["added"])
        self.assertNotIn("negation", kinds(result))


class ReviewedCaseTests(unittest.TestCase):
    """Inputs an independent review found mishandled: false passes, then false blocks."""

    def test_quotation_after_a_short_quote(self):
        original = 'He said "No" and left. Later she told the team "the launch went well" over lunch.'
        result = compare(original, original.replace("well", "badly"))
        self.assertEqual(
            difference(result, "quotes")["dropped"], ["the launch went well"]
        )
        self.assertEqual(
            difference(result, "quotes")["added"], ["the launch went badly"]
        )
        narration = compare(
            'He said "No" and left quickly. Later she said "the launch went well".',
            'He said "No" and then left. Later she said "the launch went well".',
        )
        self.assertTrue(narration["passed"])

    def test_quoted_blocks_nested_items_footnotes_and_front_matter(self):
        quoted = compare(
            "> Revenue rose 12% in March and we will not cut jobs.\n",
            "> Revenue rose 15% in April and we will cut jobs.\n",
            "markdown",
            "markdown",
        )
        self.assertEqual(kinds(quoted), ["numbers", "dates", "quotes", "negation"])
        nested = compare(
            "- Plan\n    - Budget is $1,900 for 5 people in 2025.\n",
            "- Plan\n    - Budget is $2,900 for 5 people in 2025.\n",
            "markdown",
            "markdown",
        )
        self.assertEqual(difference(nested, "numbers")["added"], ["$2,900"])
        footnote = compare(
            "It runs nightly.[^1]\n\n[^1]: Since 2019.\n",
            "It runs nightly.[^1]\n\n[^1]: Since 2021.\n",
            "markdown",
            "markdown",
        )
        self.assertEqual(difference(footnote, "numbers")["dropped"], ["2019"])
        front = compare(
            "---\ntitle: Plan\ndate: 2026-11-18\n---\nText here.\n",
            "---\ntitle: Plan\ndate: 2026-11-19\n---\nText here.\n",
            "markdown",
            "markdown",
        )
        self.assertEqual(kinds(front), ["code"])
        page = compare(
            "<p>Run <code>rm -rf build</code> now.</p>",
            "<p>Run <code>rm -rf /</code> now.</p>",
            "html",
            "html",
        )
        self.assertEqual(difference(page, "code")["dropped"], ["rm -rf build"])
        self.assertEqual(difference(page, "code")["added"], ["rm -rf /"])

    def test_figures_beside_letters_and_emphasis(self):
        result = compare(
            "Upgrade to v2.1 and see p.5. It is _12%_ faster.",
            "Upgrade to v2.2 and see p.6. It is _15%_ faster.",
        )
        self.assertEqual(difference(result, "numbers")["dropped"], ["12%", "2.1", "5"])
        self.assertEqual(difference(result, "numbers")["added"], ["15%", "2.2", "6"])

    def test_brief_facts_in_code_spans_and_nested_items_are_supplied(self):
        brief = "Facts:\n\n- Price is `$1,900`\n    - Starts in 2025 with 5 seats\n"
        draft = "The plan costs $1,900 and starts in 2025 with 5 seats."
        result = compare(brief, draft, "markdown", "markdown", brief=True)
        self.assertEqual(result["differences"], [])

    def test_unchanged_facts_do_not_block(self):
        link = "[the docs](https://example.com/docs)"
        for original, revised, format in (
            ("Start 1 server and wait.", "Start one server and wait.", "text"),
            ("May I suggest a call?", "Can I suggest a call?", "text"),
            (f"See **{link}** today.", f"See {link} today.", "markdown"),
            (
                'She said "the launch went\nvery well indeed" today.',
                'She said "the launch went very well indeed" today.',
                "text",
            ),
        ):
            with self.subTest(original=original):
                self.assertTrue(compare(original, revised, format, format)["passed"])
        month = compare("It ships in May.", "It ships in June.")
        self.assertEqual(kinds(month), ["dates"])
        self.assertEqual(difference(month, "dates")["dropped"], ["May"])

    def test_names_survive_punctuation_changes_and_open_sentences(self):
        same = compare(
            "Acme--the vendor--said 'Acme' is _really_ ready.",
            "Acme—the vendor—said Acme is really ready.",
        )
        self.assertEqual(kinds(same), ["typography"])
        swapped = compare("Acme ships on Friday.", "Globex ships on Friday.")
        self.assertEqual(difference(swapped, "names")["dropped"], ["Acme"])
        self.assertEqual(difference(swapped, "names")["added"], ["Globex"])
        openers = compare(
            "However, the cache works. Additionally, it is fast.",
            "The cache works and it is fast.",
        )
        self.assertEqual(openers["differences"], [])

    def test_documents_without_prose_compare_clean(self):
        for text, format in (("```sh\nmake\n```\n", "markdown"), ("", "text")):
            with self.subTest(text=text):
                self.assertEqual(compare(text, text, format, format)["differences"], [])

    def test_worst_case_inputs_stay_fast(self):
        started = time.perf_counter()
        for text in (
            "a" * 40000,
            "-" * 40000,
            "x" * 40000 + "n't",
            "1," * 20000,
            '"' * 20001,
            "](" * 20000,
            "`" * 30000,
        ):
            compare(text, text)
        # Typical total is well under a second; one branch used to take seven.
        self.assertLess(time.perf_counter() - started, 15)


class SecondReviewTests(unittest.TestCase):
    """Inputs a second independent review found mishandled, by the same two measures."""

    def errors(self, original, revised, format="text", other=None, brief=False):
        result = compare(original, revised, format, other or format, brief)
        return [
            item["kind"] for item in result["differences"] if item["severity"] == "error"
        ]

    def check(self, cases, format="text"):
        for original, revised, expected in cases:
            with self.subTest(original=original, revised=revised):
                self.assertEqual(self.errors(original, revised, format), expected)

    def test_carriage_returns_change_nothing(self):
        front = "---\ntitle: Plan\nowner: ops\n---\nWe ship on Friday.\n"
        fenced = "Run this:\n\n```sh\nmake build\nmake deploy\n```\n"
        for text in (front, fenced):
            with self.subTest(text=text):
                returned = text.replace("\n", "\r\n")
                result = compare(text, returned, "markdown", "markdown")
                self.assertEqual(result["differences"], [])
        draft = front.replace("\n", "\r\n")
        self.assertEqual(
            self.errors(draft, draft.replace("ops", "dev"), "markdown"), ["code"]
        )

    def test_html_is_read_as_its_reader_sees_it(self):
        self.check(
            (
                (
                    "<p>Email ops@example.test or see https://x.test/a today.</p>",
                    "<p>Email dev@example.test or see https://x.test/b today.</p>",
                    ["links"],
                ),
                (
                    "<p>See <a href=/docs/a>the guide</a>.</p>",
                    "<p>See <a href=/docs/b>the guide</a>.</p>",
                    ["links"],
                ),
                (
                    "<p>See <a href=\"/o'brien/a\">the guide</a>.</p>",
                    "<p>See <a href=\"/o'brien/b\">the guide</a>.</p>",
                    ["links"],
                ),
                # An end tag left out, as HTML allows, hides nothing after it.
                (
                    "<html><head><title>T</title><body><p>Growth 12% on Friday.</p></body></html>",
                    "<html><head><title>T</title><body><p>Growth 15% on Monday.</p></body></html>",
                    ["numbers", "dates"],
                ),
                (
                    "<ul><li hidden>Old<li>Growth 12% on Friday.</ul>",
                    "<ul><li hidden>Old<li>Growth 15% on Monday.</ul>",
                    ["numbers", "dates"],
                ),
                (
                    '<p>Growth: <span aria-hidden="true">12%</span></p>',
                    '<p>Growth: <span aria-hidden="true">15%</span></p>',
                    ["numbers"],
                ),
                (
                    "<p>Chart:</p><svg><text>12%</text></svg>",
                    "<p>Chart:</p><svg><text>15%</text></svg>",
                    ["numbers"],
                ),
                (
                    "<title>Plan for 2025</title><p>Text.</p>",
                    "<title>Plan for 2026</title><p>Text.</p>",
                    ["numbers"],
                ),
                (
                    '<p>Chart <img alt="Growth of 12%" src="a.png"></p>',
                    '<p>Chart <img alt="Growth of 15%" src="a.png"></p>',
                    ["numbers"],
                ),
                (
                    "<blockquote><p>The launch went well today.</p></blockquote>",
                    "<blockquote><p>The launch went badly today.</p></blockquote>",
                    ["quotes"],
                ),
                (
                    "<p>She said <q>the launch went well</q>.</p>",
                    "<p>She said <q>the launch went badly</q>.</p>",
                    ["quotes"],
                ),
                (
                    "<pre>if x:\n    y()\nz()</pre><p>T.</p>",
                    "<pre>if x: y() z()</pre><p>T.</p>",
                    ["code"],
                ),
                # What no reader sees is not compared.
                (
                    '<p>Text here.</p><!-- <a href="/old">old</a> -->',
                    "<p>Text here.</p>",
                    [],
                ),
                (
                    '<p>Text here.</p><div hidden>Was 12% <a href="/old">old</a></div>',
                    "<p>Text here.</p>",
                    [],
                ),
            ),
            "html",
        )
        markdown = "# Plan\n\nRun `make deploy` and see [docs](https://x.test/a). Costs $5.\n\n> We will ship it.\n"
        page = (
            '<h1>Plan</h1><p>Run <code>make deploy</code> and see <a href="https://x.test/a">'
            "docs</a>. Costs $5.</p><blockquote><p>We will ship it.</p></blockquote>"
        )
        self.assertEqual(self.errors(markdown, page, "markdown", "html"), [])

    def test_changed_figures_in_every_spelling(self):
        self.check(
            (
                ("Margin moved to -5% this quarter.", "Margin moved to 5% this quarter.", ["numbers"]),
                ("Revenue changed by +5%.", "Revenue changed by -5%.", ["numbers"]),
                ("It was significant at p < .05.", "It was significant at p < .5.", ["numbers"]),
                ("The call starts at 9:30am.", "The call starts at 9:30pm.", ["numbers"]),
                ("The call starts at 9 a.m. sharp.", "The call starts at 9 p.m. sharp.", ["numbers"]),
                ("It has twenty nodes.", "It has thirty nodes.", ["numbers"]),
                ("It has twenty-one nodes.", "It has 22 nodes.", ["numbers"]),
                ("Latency fell to 5 ms.", "Latency fell to 5 s.", ["numbers"]),
                ("It costs US$5 million.", "It costs A$5 million.", ["numbers"]),
            )
        )

    def test_figures_written_another_way_are_unchanged(self):
        self.check(
            (
                ("We ship on 14th November.", "We ship on 14 November.", []),
                ("Costs rose 5 percent.", "Costs rose 5%.", []),
                ("Costs rose 5 %.", "Costs rose 5 per cent.", []),
                ("See pages 4,5 and 6.", "See pages 4, 5 and 6.", []),
                ("It took 5ms today.", "It took 5 ms today.", []),
                ("Latency was 1,500ms.", "Latency was 1500ms.", []),
                ("There were 0 errors.", "There were zero errors.", []),
                ("It has twenty-one nodes.", "It has 21 nodes.", []),
                ("Gains of +5% by 9:30 a.m. on 2026-11-19.", "Gains of 5% by 9:30am on 2026-11-19.", []),
                ("Read pages 5-10.", "Read pages 5–10.", []),
            )
        )
        self.assertEqual(
            difference(compare("Pages 4, 5 and 6.", "Pages 4, 5 and 7."), "numbers")["dropped"],
            ["6"],
        )

    def test_a_figure_that_opens_a_line_is_not_a_list_marker(self):
        wrapped = "The team grew from 12 to\n42. Next year it doubles.\n"
        self.check(
            (
                (wrapped, wrapped.replace("42", "45"), ["numbers"]),
                (wrapped, "The team grew from 12 to 42. Next year\nit doubles.\n", []),
                (
                    "We counted (roughly\n40) users.\n",
                    "We counted (roughly\n50) users.\n",
                    ["numbers"],
                ),
                (
                    "Steps:\n\n1. Build\n2. Test\n   more\n3. Ship",
                    "Steps: build, then test more, then ship.",
                    [],
                ),
            ),
            "markdown",
        )
        self.check((("Total:\n42. That is all.\n", "Total:\n45. That is all.\n", ["numbers"]),))

    def test_one_stands_in_for_1_only_beside_the_same_word(self):
        self.check(
            (
                ("We lost 1 server and 2 queues.", "We lost 2 queues and no one noticed.", ["numbers"]),
                ("No one objected, so phase 2 can start.", "Phase 1 and phase 2 can start.", ["numbers"]),
                ("Start 1 server and wait.", "Start one server and wait.", []),
                ("We are in phase one now.", "We are in phase 1 now.", []),
            )
        )
        brief = "No one has signed up. Price is $4."
        draft = "Price is $4 and 1 customer has signed up."
        self.assertEqual(self.errors(brief, draft, brief=True), ["numbers"])
        self.assertEqual(
            self.errors("Price is $4.", "Price is $4 for twenty seats.", brief=True),
            ["numbers"],
        )

    def test_dates_in_other_positions_cases_and_spellings(self):
        self.check(
            (
                ("In May, we shipped the export.", "In March, we shipped the export.", ["dates"]),
                ("The deadline is 5th May.", "The deadline is 5th March.", ["dates"]),
                ("Due 20th Jan.", "Due 20th Feb.", ["dates"]),
                ("Standup is on Mondays.", "Standup is on Tuesdays.", ["dates"]),
                ("see you on monday.", "see you on tuesday.", ["dates"]),
                ("Meet Thu 5 June.", "Meet Thursday 5 June.", []),
                ("Due 5  May.", "Due 5 May.", []),
                ("We will ship on 5\nMay after review.\n", "We will ship on 5 May\nafter review.\n", []),
            )
        )
        self.check(
            (
                ("# RELEASE ON FRIDAY\n\nText here.", "# Release on Friday\n\nText here.", []),
                ("# RELEASE IN MAY\n\nText here.", "# Release in May\n\nText here.", []),
                ("Due 5&nbsp;May.\n", "Due 5 May.\n", []),
            ),
            "markdown",
        )

    def test_links_by_reference_in_tags_and_with_titles(self):
        inline = "See [the docs](docs/a.md) today.\n"
        self.check(
            (
                (
                    "See [the guide][g].\n\n[g]: /docs/install\n",
                    "See [the guide][g].\n\n[g]: /docs/uninstall\n",
                    ["links"],
                ),
                (
                    "See [the guide][a].\n\n[a]: /a\n[b]: /b\n",
                    "See [the guide][b].\n\n[a]: /a\n[b]: /b\n",
                    ["links"],
                ),
                (
                    'See <a href="/docs/a">the guide</a>.',
                    'See <a href="/docs/b">the guide</a>.',
                    ["links"],
                ),
                (
                    'See [the report](https://x.test/r "Q3 2025: revenue up 12%").',
                    'See [the report](https://x.test/r "Q4 2025: revenue up 21%").',
                    ["numbers", "quotes"],
                ),
                # One link written three ways.
                (inline, "See [the docs][docs] today.\n\n[docs]: docs/a.md\n", []),
                (inline, 'See <a href="docs/a.md">the docs</a> today.\n', []),
                (
                    "See [the docs](https://x.test/a) today.\n",
                    "See [the docs][1] today.\n\n[1]: https://x.test/a\n",
                    [],
                ),
                (
                    "Mail ops@x.test today.\n",
                    "Mail [ops@x.test](mailto:ops@x.test) today.\n",
                    [],
                ),
                (
                    "See https://x.test/?a=1&amp;b=2 now.\n",
                    "See https://x.test/?a=1&b=2 now.\n",
                    [],
                ),
            ),
            "markdown",
        )
        self.check(
            (
                ("Visit www.example.com for details.", "Visit www.example.org for details.", ["links"]),
                ("Logs go to s3://logs-prod/app now.", "Logs go to s3://logs-dev/app now.", ["links"]),
                (
                    "See appendix [B](page 12, revised 5 May).",
                    "See appendix [B](page 21, revised 6 June).",
                    ["numbers", "dates"],
                ),
            )
        )

    def test_quotations_beside_inch_marks_in_blocks_and_in_curly_marks(self):
        monitor = 'The 27" monitor is fine. She said "do not skip the canary".'
        self.check(
            (
                (monitor, monitor.replace("do not", "always"), ["quotes"]),
                (
                    "She said “the launch went well” and left.",
                    'She said "the launch went well" and left.',
                    [],
                ),
                (
                    # A stray pair of marks reads the same curly or straight.
                    'Items:\n* "More emphasis on safety (and defaults).”\n* "Docs"\n',
                    'Items:\n* "More emphasis on safety (and defaults)."\n* "Docs"\n',
                    [],
                ),
            )
        )
        spaced = 'The 27" monitor ships.\n  \nShe said it was "fine by me" today.\n'
        self.check(
            (
                (spaced, spaced.replace("fine", "not fine"), ["quotes"]),
                (spaced, spaced.replace("  \n", "\n"), []),
                ("> It’s fine and we’ll ship it.\n", "> It's fine and we'll ship it.\n", []),
                ("> **Note:** we will ship it.\n", "> Note: we will ship it.\n", []),
                ("> We will ship it.\n", "> We will ship it\n", []),
                (
                    "> We will ship it soon and\nthen rest for a while.\n",
                    "> We will ship it\nsoon and then rest for a while.\n",
                    [],
                ),
                (
                    'She said "the *launch* went well".',
                    'She said "the launch went well".',
                    [],
                ),
                (
                    "She said &ldquo;the launch went well&rdquo;.\n",
                    'She said "the launch went well".\n',
                    [],
                ),
                (
                    "> Note\n>\n> ```sh\n> make deploy\n> ```\n",
                    "> Note\n>\n> ```sh\n> make release\n> ```\n",
                    ["code"],
                ),
            ),
            "markdown",
        )

    def test_code_in_indented_blocks_tags_and_wrapped_spans(self):
        self.check(
            (
                ("Text:\n\n    make deploy\n", "Text:\n\n    make release\n", ["code"]),
                (
                    "Run <code>make deploy</code> now.",
                    "Run <code>make release</code> now.",
                    ["code"],
                ),
                (
                    "- Step\n\n    ```sh\n    make deploy\n    ```\n",
                    "- Step\n\n    ```sh\n    make release\n    ```\n",
                    ["code"],
                ),
                # Under a list item, four spaces carry the item on.
                (
                    "- item\n\n    continued deploy text\n",
                    "- item\n\n    continued release text\n",
                    [],
                ),
                (
                    "To deploy, run `make deploy\n--force` and wait.\n",
                    "To deploy, run `make deploy --force`\nand wait.\n",
                    [],
                ),
                # One block, indented and then fenced.
                (
                    "Text:\n\n    make deploy\n    make test\n",
                    "Text:\n\n```sh\nmake deploy\nmake test\n```\n",
                    [],
                ),
                # A Markdown escape is not part of the text, except in code.
                ("It grew 5\\% for snake\\_case.", "It grew 5% for snake_case.", []),
                ("Type `a\\_b` here.", "Type `a_b` here.", ["code"]),
            ),
            "markdown",
        )
        indented = compare(
            "Run:\n\n```py\nif x:\n    y()\nz()\n```\n",
            "Run:\n\n```py\nif x:\n  y()\nz()\n```\n",
            "markdown",
            "markdown",
        )
        self.assertIn("spacing or line breaks", difference(indented, "code")["note"])

    def test_text_that_only_looks_like_front_matter_is_prose(self):
        text = "---\n# Weekly notes\n\nWe ship on Friday.\n\n---\n\nThe export runs.\n"
        self.assertEqual(
            self.errors(text, text.replace("Friday", "Monday"), "markdown"), ["dates"]
        )
        self.assertEqual(
            self.errors(text, text.replace("We ship", "The team ships"), "markdown"), []
        )

    def test_a_brief_supplies_its_facts_however_they_are_set(self):
        quoted = 'The team said "run `make deploy` before lunch" twice.'
        for format in ("markdown", "text"):
            with self.subTest(format=format):
                self.assertEqual(
                    compare(quoted, quoted, format, format, True)["differences"], []
                )
        for brief, draft, format in (
            ("```\nmax_users: 50\n```\n", "The limit is 50 users.", "markdown"),
            ("---\nmax_users: 50\n---\nText.\n", "The limit is 50 users.", "markdown"),
            ("<p>Price is <code>$4</code>.</p>", "The price is $4.", "html"),
            ("The command is make deploy.", "Run `make deploy`.", "text"),
            (
                "> This is the best launch.\n",
                'Priya said "This is the best launch."',
                "markdown",
            ),
        ):
            with self.subTest(brief=brief):
                self.assertEqual(self.errors(brief, draft, format, "markdown", True), [])
        invented = self.errors(
            "The command is make deploy.", "Run `make release`.", "text", "markdown", True
        )
        self.assertEqual(invented, ["code"])

    def test_comments_are_not_compared(self):
        self.check(
            (
                (
                    "The export runs nightly.\n\n<!-- TODO: recheck the 2.1 figures on Friday -->\n",
                    "The export runs nightly.\n",
                    [],
                ),
                (
                    "Text here.\n\n<!-- [old](https://x.test/old) and `rm -rf` -->\n",
                    "Text here.\n",
                    [],
                ),
            ),
            "markdown",
        )

    def test_rewrapped_text_compares_clean(self):
        original = (
            'The state-of-the-art model reached 96 h of uptime, said the lead: "It is '
            'a high-performance, well-tested system." It runs at least 5 times a day.'
        )
        wrapped = (
            "The state-of-the-\nart model reached 96\nh of uptime, said the lead: "
            '"It is a high-\nperformance, well-tested system." It runs at\nleast 5 times a day.'
        )
        self.assertEqual(compare(original, wrapped)["differences"], [])
        # Two lines are too few to look hard-wrapped; they are joined all the same.
        short = compare("It took 96 h to finish.", "It took 96\nh to finish.")
        self.assertEqual(short["differences"], [])

    def test_more_worst_case_inputs_stay_fast(self):
        started = time.perf_counter()
        for text, format in (
            ("<pre>" * 10000, "html"),
            ("<code>" * 8000, "html"),
            ("<b>" * 8000 + "Text here." + "</i>" * 6000, "html"),
            ("<q>" * 10000 + "x" + "</q>" * 10000, "html"),
            ('<a href="x">' * 8000 + "word " * 2000, "html"),
            ("one " * 20000, "text"),
            ("x" + " " * 40000 + "y", "text"),
            ("[a][b]" * 8000 + "\n\n[b]: /x\n", "markdown"),
            ("[a](x)" * 8000, "markdown"),
            ("\ue001" * 20000, "text"),
            ("> a\n" * 10000, "markdown"),
            ("\n    code\n" * 8000, "markdown"),
            ("a-\nb " * 10000, "text"),
        ):
            compare(text, text, format, format)
        # Typical total is about two seconds; two of these took four each.
        self.assertLess(time.perf_counter() - started, 30)


class CompareCLITests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        for name, text in (("a.md", ORIGINAL), ("b.md", FAITHFUL), ("c.md", DRIFTED)):
            (self.folder / name).write_text(text, encoding="utf-8")

    def run_cli(self, *args, input=None):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "compare.py"), *args],
            input=input,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            cwd=self.folder,
        )

    def test_statuses_json_and_strict(self):
        faithful = self.run_cli("a.md", "b.md")
        self.assertEqual(faithful.returncode, 0)
        self.assertIn("no protected token changed; 0 blocking, 1 to review", faithful.stdout)
        # The headline, the JSON and the exit status agree under --strict.
        strict = self.run_cli("a.md", "b.md", "--strict")
        self.assertEqual(strict.returncode, 1)
        self.assertIn("review before use; 0 blocking, 1 to review", strict.stdout)
        strict = self.run_cli("a.md", "b.md", "--strict", "--json")
        self.assertFalse(json.loads(strict.stdout)["passed"])
        drifted = self.run_cli("a.md", "c.md", "--json")
        payload = json.loads(drifted.stdout)
        self.assertEqual(drifted.returncode, 1)
        self.assertEqual(payload["schema_version"], 1)
        self.assertFalse(payload["passed"])
        self.assertEqual(payload["blocking"], 4)

    def test_text_report_and_stdin(self):
        result = self.run_cli("a.md", "-", "--format", "markdown", input=DRIFTED)
        self.assertEqual(result.returncode, 1)
        self.assertIn("check before use; 4 blocking, 3 to review", result.stdout)
        self.assertIn("numbers   error: dropped: 8%; added: 18%", result.stdout)
        self.assertIn("cannot show that the meaning survived", result.stdout)
        # Standard input keeps its carriage returns; a file equals itself.
        returned = ORIGINAL.replace("\n", "\r\n")
        same = self.run_cli("a.md", "-", "--format", "markdown", input=returned)
        self.assertEqual(same.returncode, 0)
        self.assertIn("0 blocking, 0 to review", same.stdout)

    def test_report_shows_where_long_tokens_differ(self):
        path = "https://example.test/a/very/long/path/that/goes/on/and/on/for/a/while/"
        (self.folder / "d.txt").write_text(f"See {path}install.html now.\n", "utf-8")
        (self.folder / "e.txt").write_text(f"See {path}uninstall.html now.\n", "utf-8")
        result = self.run_cli("d.txt", "e.txt")
        self.assertIn("while/install.html; added: ...", result.stdout)
        self.assertIn("while/uninstall.html", result.stdout)
        self.assertEqual(result.stderr, "")
        payload = json.loads(self.run_cli("d.txt", "e.txt", "--json").stdout)
        self.assertEqual(payload["differences"][0]["dropped"], [f"{path}install.html"])

    def test_input_errors(self):
        for args in (("a.md", "missing.md"), ("-", "-")):
            with self.subTest(args=args):
                result = self.run_cli(*args, "--json", input="")
                self.assertEqual(result.returncode, 2)
                self.assertFalse(json.loads(result.stdout)["passed"])
        self.assertIn("hooman:", self.run_cli("a.md", "missing.md").stderr)


if __name__ == "__main__":
    unittest.main()
