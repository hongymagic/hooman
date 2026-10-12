from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "human-writing" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from check import allowances, audit, infer_format  # noqa: E402 - load standalone bundle


class CheckerTests(unittest.TestCase):
    def test_known_defects_are_blocking(self):
        cases = {
            "Delving into the configuration.": "word.delving",
            "The export is game-changing.": "word.hype",
            "In today’s fast‑paced digital world, work changes.": "frame.scene",
            "It is important to note that approval is pending.": "frame.announcement",
            "The result? The export runs twice.": "frame.suspense",
            "We check each and every file.": "repeat.synonyms",
            "The report includes [needs proof].": "evidence.placeholder",
        }
        for source, rule in cases.items():
            with self.subTest(source=source):
                result = audit(source)
                self.assertFalse(result["passed"])
                self.assertIn(rule, [finding["rule"] for finding in result["findings"]])

    def test_category_penalty_is_bounded(self):
        result = audit(
            "Delve into this game-changing export. It is worth noting that it runs."
        )
        self.assertEqual(result["score"], 3)
        self.assertEqual(len(result["findings"]), 3)

    def test_explicit_inflections_and_word_boundaries(self):
        for word in (
            "delve",
            "delves",
            "delved",
            "delving",
            "revolutionises",
            "revolutionizing",
            "supercharged",
        ):
            with self.subTest(word=word):
                self.assertFalse(audit(word)["passed"])
        for word in (
            "Delvecchio",
            "revolution",
            "revolutionary",
            "supercharger",
            "unlockable",
            "projectors",
            "teamsters",
        ):
            with self.subTest(word=word):
                self.assertEqual(audit(word)["findings"], [])

    def test_technical_terms_and_evidence_remain_advisory(self):
        result = audit(
            "Use a robust estimator. Unlock the account. We surveyed 12 customers."
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 5)
        self.assertEqual(
            {finding["severity"] for finding in result["findings"]}, {"review"}
        )

    def test_useful_devices_are_available(self):
        source = "What happens after a crash? The event may arrive again. Record the ID, confirm the owner and keep the fallback enabled. The key was rotated—its owner is unknown."
        self.assertEqual(audit(source)["findings"], [])

    def test_repeated_sentence(self):
        source = "The export includes all archived invoices. The export includes all archived invoices."
        result = audit(source)
        self.assertEqual(
            [finding["rule"] for finding in result["findings"]], ["repeat.sentence"]
        )
        self.assertEqual(result["score"], 4)

    def test_allowance_retains_finding_and_reason(self):
        result = audit(
            "Delve is a command.",
            allowed=allowances(["word.delving=Documented literal name"]),
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["findings"][0]["allowance"], "Documented literal name")
        for value in ("word.delving=", "unknown=Reason", "word.delving"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                allowances([value])

    def test_markdown_literals_are_excluded(self):
        source = """---
title: Delve
---
The export accepts compressed invoices.

```python
print("game-changing")
```

~~~text
It is worth noting that this is a specimen.
~~~

> Delve into a specimen.

    Delve is indented code.

`delve` and ``game-changing `sample` `` are examples.
~~Delve~~ is struck out.
[Documentation](https://example.test/delve_(game-changing) "delve") explains exports.
[An example][delve]
[delve]: https://example.test/game-changing
<!-- Delve into comments. -->
"""
        self.assertEqual(audit(source, "markdown")["findings"], [])

    def test_link_labels_and_inline_quotes_are_checked(self):
        for source in (
            "[Delve](https://example.test)",
            'The title is "game-changing".',
        ):
            with self.subTest(source=source):
                self.assertFalse(audit(source, "markdown")["passed"])

    def test_fence_inside_fence_and_unclosed_fence(self):
        source = "````text\n```\nDelve\n```\n````\nThe export runs."
        self.assertTrue(audit(source, "markdown")["passed"])
        with self.assertRaises(ValueError):
            audit("```text\nDelve", "markdown")

    def test_html_hidden_content_and_void_elements(self):
        source = """<html><head><title>Delve</title></head><body>
<div hidden><br><b>game-changing</b></div>
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
        result = audit("# Export\n\n`game-changing` Delve into invoices.", "markdown")
        self.assertEqual(
            (result["findings"][0]["line"], result["findings"][0]["column"]), (3, 17)
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
            ("Delve into imports.", 1),
            ("", 2),
        ):
            with self.subTest(source=source):
                result = self.run_cli("--text", source, "--json")
                self.assertEqual(result.returncode, status)
                self.assertEqual(json.loads(result.stdout)["passed"], status == 0)
                self.assertEqual(result.stderr, "")

    def test_stdin_format_override_and_strict_review(self):
        result = self.run_cli(
            "-", "--format", "markdown", input="`Delve` is a command."
        )
        self.assertEqual(result.returncode, 0)
        result = self.run_cli("--text", "Use a robust estimator.", "--strict", "--json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["results"][0]["score"], 5)

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
