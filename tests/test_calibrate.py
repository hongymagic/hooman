from __future__ import annotations

import contextlib
import hashlib
import http.client
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "calibrate.py"
MANIFEST = ROOT / "scripts" / "calibration-corpus.json"
sys.path.insert(0, str(ROOT / "scripts"))
import calibrate  # noqa: E402 - maintainer script, outside any package

BODIES = {
    "docs/notes.md": b"The export writes one file per month.\n",
    # A reStructuredText heading: read as Markdown, the tildes would open a fence.
    "docs/guide.rst": b"Usage\n~~~~~\n\nRun the export from the Billing page.\n",
}
# One cell fails the gate, and one carries separators that end a line for
# str.splitlines but not for the cache.
TEXTS = {
    "gpt4o-news": "It is worth noting that it runs.",
    "human-news": "First line. Second line.\u0085Third line. Fourth line.",
}


def rows(name: str, count: int = 200) -> list[dict]:
    register = name.split("-")[1]
    return [
        {
            "doc_id": f"{register}_{index + 1:04d}@{name}",
            "text": TEXTS.get(name)
            or f"Batch {index} finished before the nightly export.",
        }
        for index in range(count)
    ]


def jsonl(documents: list[dict]) -> bytes:
    return "".join(json.dumps(row) + "\n" for row in documents).encode()


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.cache = self.folder / "cache"
        self.manifest = self.folder / "manifest.json"
        self.pinned = {
            "human": [
                {
                    "repo": "example/notes",
                    "commit": "0" * 40,
                    "path": path,
                    "register": "docs",
                    "words": len(body.split()),
                    "sha256": hashlib.sha256(body).hexdigest(),
                }
                for path, body in BODIES.items()
            ],
            "parallel": {
                name: hashlib.sha256(jsonl(rows(name))).hexdigest()
                for name in calibrate.cells()
            },
        }
        self.manifest.write_text(json.dumps(self.pinned), encoding="utf-8")
        for patcher in (
            mock.patch.object(calibrate, "MANIFEST", self.manifest),
            mock.patch.object(calibrate.time, "sleep"),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.first_rows = {first: name for name, first in calibrate.cells().items()}

    def serve(self, bodies=BODIES, page=None, reply=None):
        """Stand in for the network. `page` reshapes one page of rows as the
        dataset server sends it; `reply` replaces the whole body."""

        def download(url: str) -> bytes:
            if "raw.githubusercontent.com" in url:
                return bodies[url.split("/" + "0" * 40 + "/")[1]]
            if reply is not None:
                return reply
            offset = int(re.search(r"offset=(\d+)", url)[1])
            first = offset if offset in self.first_rows else offset - calibrate.PAGE
            cell = rows(self.first_rows[first])[offset - first :][: calibrate.PAGE]
            payload = {
                "features": [],
                "rows": [
                    {"row_idx": offset + index, "row": row, "truncated_cells": []}
                    for index, row in enumerate(cell)
                ],
                "num_rows_total": 66320,
                "num_rows_per_page": calibrate.PAGE,
                "partial": False,
            }
            return json.dumps(page(payload) if page else payload).encode()

        return mock.patch.object(calibrate, "download", download)

    def run_main(self, *args) -> tuple[int, str, str]:
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = calibrate.main([*args, "--cache", str(self.cache)])
        return status, output.getvalue(), errors.getvalue()

    def fetched(self) -> None:
        with self.serve():
            self.assertEqual(self.run_main("fetch")[0], 0)

    def cached(self) -> list[str]:
        return sorted(path.name for path in (self.cache / "parallel").iterdir())

    def test_manifest_pins_every_source_and_cell_to_a_hash(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(manifest["human"]), 60)
        for entry in manifest["human"]:
            with self.subTest(path=entry["path"]):
                self.assertRegex(entry["repo"], r"^[\w.-]+/[\w.-]+$")
                self.assertRegex(entry["commit"], r"^[0-9a-f]{40}$")
                self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(entry["words"], 0)
        self.assertEqual(set(manifest["parallel"]), set(calibrate.cells()))
        for name, pin in manifest["parallel"].items():
            with self.subTest(cell=name):
                self.assertRegex(pin, r"^[0-9a-f]{64}$")

    def test_fetch_then_measure(self):
        self.fetched()
        self.assertEqual(
            (self.cache / "human-tech" / "00-notes.md").read_bytes(),
            BODIES["docs/notes.md"],
        )
        sets = calibrate.corpora(self.cache, [])
        self.assertEqual(
            {name: len(texts) for name, texts in sets.items()},
            {"human-tech": 2, **dict.fromkeys(calibrate.cells(), 200)},
        )
        # A second run finds everything in place and asks the network for nothing.
        with mock.patch.object(calibrate, "download", side_effect=AssertionError):
            self.assertEqual(self.run_main("fetch")[0], 0)

    def test_only_the_pinned_documents_reach_the_cache(self):
        def short(payload):
            return {**payload, "rows": payload["rows"][:37]}

        def cut(payload):
            # The server reports a shortened text on the row it shortened.
            payload["rows"][3]["truncated_cells"] = ["text"]
            return payload

        def other_ids(payload):
            for item in payload["rows"]:
                item["row"]["doc_id"] = item["row"]["doc_id"].split("@")[0] + "@other"
            return payload

        def repeated(payload):
            first = rows("gpt4o-acad")[: calibrate.PAGE]
            for item, row in zip(payload["rows"], first):
                item["row"] = row
            return payload

        def shortened(payload):
            for item in payload["rows"]:
                item["row"]["text"] = item["row"]["text"][:10]
            return payload

        for label, page, message in (
            ("short", short, "the 74 documents received differ"),
            ("cut", cut, "the server cut texts short"),
            ("other ids", other_ids, "differ from the pinned corpus"),
            ("one page twice", repeated, "differ from the pinned corpus"),
            ("shortened texts", shortened, "differ from the pinned corpus"),
        ):
            with self.subTest(label), self.serve(page=page):
                status, _, errors = self.run_main("fetch")
                self.assertEqual(status, 1)
                self.assertIn(message, errors)
                self.assertEqual(self.cached(), [])

    def test_unexpected_replies_are_reported_not_raised(self):
        row = rows("gpt4o-acad")[0]
        for reply in (
            b"[]",
            b"null",
            b'"error"',
            b"{}",
            b'{"rows": null}',
            b'{"rows": [{"row_idx": 1}]}',
            json.dumps({"rows": [{"row": {"doc_id": "a"}, "truncated_cells": []}]}),
            json.dumps({"rows": [{"row": row}]}),
            b"<html>Bad gateway</html>",
            b"\xff\xfe",
        ):
            body = reply if isinstance(reply, bytes) else reply.encode()
            with self.subTest(reply=body[:30]), self.serve(reply=body):
                status, _, errors = self.run_main("fetch")
                self.assertEqual(status, 1)
                self.assertIn("unexpected reply from the dataset server", errors)
                self.assertEqual(self.cached(), [])

    def test_damaged_cache_is_fetched_again(self):
        self.fetched()
        human = self.cache / "human-tech" / "00-notes.md"
        parallel = self.cache / "parallel"
        whole = rows("gpt4o-acad")
        damage = {
            "gpt4o-acad": jsonl(whole[:37]),
            "gpt4o-blog": b'{"doc_id": "blog_',
            # Two hundred lines, the last one without its text.
            "gpt4o-news": jsonl(rows("gpt4o-news")[:199])
            + b'{"doc_id": "news_0200@gpt4o-news", "text": null}\n',
            "human-acad": jsonl(rows("human-acad")[:100] * 2),
            "human-blog": jsonl(
                [{**row, "text": row["text"][:10]} for row in rows("human-blog")]
            ),
        }
        for name, body in damage.items():
            with self.subTest(name):
                (parallel / f"{name}.jsonl").write_bytes(body)
                status, _, errors = self.run_main("measure")
                self.assertEqual(status, 1)
                self.assertIn("differs from the manifest; run fetch first", errors)
                self.fetched()
                self.assertEqual(
                    (parallel / f"{name}.jsonl").read_bytes(), jsonl(rows(name))
                )
        human.write_bytes(BODIES["docs/notes.md"][:10])
        self.assertEqual(self.run_main("measure")[0], 1)
        self.fetched()
        self.assertEqual(human.read_bytes(), BODIES["docs/notes.md"])
        self.assertEqual(self.run_main("measure")[0], 0)

    def test_wrong_download_never_reaches_the_cache(self):
        wrong = {**BODIES, "docs/notes.md": b"Something else entirely.\n"}
        with self.serve(bodies=wrong):
            status, _, errors = self.run_main("fetch")
        self.assertEqual(status, 1)
        self.assertIn("hash mismatch for example/notes/docs/notes.md", errors)
        self.assertEqual(list((self.cache / "human-tech").iterdir()), [])

    def test_cut_off_body_is_retried_then_reported(self):
        with mock.patch.object(
            calibrate.urllib.request,
            "urlopen",
            side_effect=http.client.IncompleteRead(b"partial"),
        ) as urlopen:
            with self.assertRaisesRegex(RuntimeError, "could not fetch"):
                calibrate.download("https://example.test/file")
        self.assertEqual(urlopen.call_count, 5)

    def test_unicode_line_separators_stay_inside_their_text(self):
        self.fetched()
        cached = (self.cache / "parallel" / "human-news.jsonl").read_bytes()
        self.assertTrue(cached.isascii())
        self.assertEqual(cached.count(b"\n"), 200)
        texts = calibrate.corpora(self.cache, [])["human-news"]
        self.assertEqual(texts[0], ("text", TEXTS["human-news"]))

    def test_measure_reads_what_the_manifest_names_and_all_of_it(self):
        status, _, errors = self.run_main("measure")
        self.assertEqual(status, 1)
        self.assertIn("run fetch first", errors)
        self.fetched()
        human = self.cache / "human-tech"
        (human / "07-stale.md").write_text("It is worth noting that it runs.\n", "utf-8")
        self.assertEqual(len(calibrate.corpora(self.cache, [])["human-tech"]), 2)
        # A cache that a failed fetch left part-filled is not measured in part.
        (self.cache / "parallel" / "human-blog.jsonl").unlink()
        status, output, errors = self.run_main("measure")
        self.assertEqual((status, output), (1, ""))
        self.assertIn("human-blog.jsonl is missing or differs", errors)
        self.fetched()
        (human / "01-guide.rst").write_bytes(BODIES["docs/guide.rst"] + b"Edited.\n")
        status, _, errors = self.run_main("measure")
        self.assertEqual(status, 1)
        self.assertIn("01-guide.rst is missing or differs from the manifest", errors)

    def test_measure_reports_each_corpus_and_rule(self):
        self.fetched()
        extra = self.folder / "drafts"
        extra.mkdir()
        (extra / "draft.md").write_text("Let's dive into exports.\n", "utf-8")
        # A byte order mark must not turn front matter into prose.
        (extra / "marked.md").write_text(
            "---\ntitle: It is worth noting\n---\nThe export runs.\n", "utf-8-sig"
        )
        status, output, errors = self.run_main(
            "measure", "--rules", "--extra", f"drafts={extra}"
        )
        self.assertEqual(status, 0, errors)
        table: dict[str, list[str]] = {}
        for line in filter(None, output.splitlines()):
            # The summary table comes first; later tables reuse the corpus names.
            table.setdefault(line.split()[0], line.split())
        # Seven words in the Markdown file; eight in the reStructuredText one,
        # whose text sits under a heading underlined with tildes.
        self.assertEqual(table["human-tech"][1:4], ["2", "15", "0.0"])
        self.assertEqual(table["gpt4o-news"][1:4], ["200", "1400", "100.0"])
        self.assertEqual(table["human-news"][1:4], ["200", "1600", "0.0"])
        self.assertEqual(table["drafts"][1:4], ["2", "7", "50.0"])
        self.assertIn("staging.announcement", output)
        self.assertIn("staging.runup", output)

    def test_extra_needs_a_free_name_and_a_directory_with_texts(self):
        self.fetched()
        empty = self.folder / "empty"
        empty.mkdir()
        for value, message in (
            ("drafts", "--extra takes NAME=DIR"),
            ("drafts=", "--extra takes NAME=DIR"),
            (f"={empty}", "--extra takes NAME=DIR"),
            (f"drafts={self.folder / 'missing'}", "--extra takes NAME=DIR"),
            (f"drafts={empty}", "no .md or .txt files"),
            (f"human-tech={empty}", "that name is already in use"),
            (f"gpt4o-news={empty}", "that name is already in use"),
        ):
            with self.subTest(value):
                status, output, errors = self.run_main("measure", "--extra", value)
                self.assertEqual((status, output), (1, ""))
                self.assertIn(message, errors)

    def test_manifest_must_describe_the_corpus(self):
        without_cell = {**self.pinned, "parallel": {"gpt4o-acad": "0" * 64}}
        for manifest in ({}, [], [{}], {"human": [{}], "parallel": {}}, without_cell):
            self.manifest.write_text(json.dumps(manifest), encoding="utf-8")
            for command in ("fetch", "measure"):
                with self.subTest(manifest=manifest, command=command), self.serve():
                    status, output, errors = self.run_main(command)
                    self.assertEqual((status, output), (1, ""))
                    self.assertIn("does not describe the pinned corpus", errors)

    def test_measure_needs_a_fetched_corpus(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "measure", "--cache", str(self.cache)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("run fetch first", result.stderr)


if __name__ == "__main__":
    unittest.main()
