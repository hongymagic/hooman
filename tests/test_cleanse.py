from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "human-writing" / "scripts"))
import cleanse  # noqa: E402 - load standalone bundle


class RoutingTests(unittest.TestCase):
    def test_writer_uses_other_family(self):
        with patch("cleanse.shutil.which", side_effect=lambda name: "/bin/" + name):
            self.assertEqual(cleanse.select_reviewer("openai")[0], "claude")
            self.assertEqual(cleanse.select_reviewer("anthropic")[0], "codex")
            self.assertEqual(cleanse.select_reviewer("google")[0], "codex")
            self.assertEqual(cleanse.select_reviewer("other", "claude")[0], "claude")

    def test_same_family_fails_even_if_installed(self):
        with self.assertRaisesRegex(cleanse.CleanseError, "different model family"):
            cleanse.select_reviewer("openai", "codex")

    def test_missing_rival_does_not_fall_back_to_writer(self):
        with patch("cleanse.shutil.which", return_value=None):
            with self.assertRaises(cleanse.CleanseError) as caught:
                cleanse.select_reviewer("openai")
        self.assertEqual(caught.exception.status, 127)


class ReplyTests(unittest.TestCase):
    def test_valid_and_invalid_structured_replies(self):
        self.assertEqual(
            cleanse.validate_reply({"copy": "The import runs.", "notes": []}),
            ("The import runs.", []),
        )
        for value in (
            None,
            [],
            {},
            {"copy": "", "notes": []},
            {"copy": "x", "notes": "note"},
            {"copy": "x", "notes": [1]},
            {"copy": "x", "notes": [], "other": True},
        ):
            with self.subTest(value=value), self.assertRaises(cleanse.CleanseError):
                cleanse.validate_reply(value)

    def test_codex_reads_final_message_instead_of_console_transcript(self):
        commands = []

        def run(command, prompt, directory, timeout):
            commands.append(command)
            self.assertEqual(prompt, "private draft")
            self.assertNotIn("private draft", command)
            self.assertNotEqual(directory, ROOT)
            response = Path(command[command.index("--output-last-message") + 1])
            response.write_text(
                json.dumps(
                    {"copy": "Invoices can be exported.", "notes": ["Cut the opening."]}
                ),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(
                command, 0, "CLI banner and usage", "diagnostics"
            )

        with patch("cleanse.run_bounded", side_effect=run):
            copy, notes = cleanse.model_pass(
                "codex", "/bin/codex", "private draft", "test-model", 10
            )
        self.assertEqual(copy, "Invoices can be exported.")
        self.assertEqual(notes, ["Cut the opening."])
        self.assertIn("--ignore-user-config", commands[0])
        self.assertIn("read-only", commands[0])
        self.assertIn("shell_tool", commands[0])
        self.assertIn("unified_exec", commands[0])
        self.assertIn("test-model", commands[0])

    def test_claude_requires_successful_structured_output(self):
        payload = {
            "subtype": "success",
            "is_error": False,
            "structured_output": {"copy": "Invoices can be exported.", "notes": []},
        }
        with patch(
            "cleanse.run_bounded",
            return_value=subprocess.CompletedProcess([], 0, json.dumps(payload), ""),
        ) as run:
            self.assertEqual(
                cleanse.model_pass("claude", "/bin/claude", "draft", None, 10)[0],
                "Invoices can be exported.",
            )
            command = run.call_args.args[0]
            self.assertIn("--safe-mode", command)
            self.assertEqual(command[command.index("--tools") + 1], "")
            self.assertIn("--strict-mcp-config", command)
        for payload in (
            {"subtype": "error_max_turns", "is_error": True},
            {"subtype": "success"},
            [],
        ):
            with self.subTest(payload=payload):
                with patch(
                    "cleanse.run_bounded",
                    return_value=subprocess.CompletedProcess(
                        [], 0, json.dumps(payload), ""
                    ),
                ):
                    with self.assertRaises(cleanse.CleanseError):
                        cleanse.model_pass("claude", "/bin/claude", "draft", None, 10)

    def test_failures_never_return_a_console_transcript_as_copy(self):
        for name, status, stdout in (
            ("codex", 0, "banner"),
            ("claude", 0, "plain prose"),
            ("claude", 42, "failed"),
        ):
            with self.subTest(name=name, status=status):
                with patch(
                    "cleanse.run_bounded",
                    return_value=subprocess.CompletedProcess(
                        [], status, stdout, "private diagnostic"
                    ),
                ):
                    with self.assertRaises(cleanse.CleanseError) as caught:
                        cleanse.model_pass(name, "/bin/cli", "draft", None, 10)
                    self.assertNotIn("private diagnostic", str(caught.exception))


class ProcessTests(unittest.TestCase):
    def test_stdin_is_literal_and_output_channels_are_separate(self):
        with tempfile.TemporaryDirectory() as temporary:
            prompt = "$(echo secret) `literal`\n한글"
            result = cleanse.run_bounded(
                [
                    sys.executable,
                    "-c",
                    "import sys; print(sys.stdin.read()); print('notes',file=sys.stderr)",
                ],
                prompt,
                Path(temporary),
                5,
            )
            self.assertEqual(result.stdout, prompt + "\n")
            self.assertEqual(result.stderr, "notes\n")

    def test_timeout_returns_124(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(cleanse.CleanseError) as caught:
                cleanse.run_bounded(
                    [sys.executable, "-c", "import time; time.sleep(30)"],
                    "draft",
                    Path(temporary),
                    0.1,
                )
            self.assertEqual(caught.exception.status, 124)

    @unittest.skipUnless(os.name == "posix", "POSIX process-group behaviour")
    def test_timeout_stops_descendants(self):
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "child-ran"
            child = "import time; from pathlib import Path; time.sleep(0.5); Path('child-ran').touch()"
            parent = (
                "import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', "
                + repr(child)
                + "]); time.sleep(30)"
            )
            with self.assertRaises(cleanse.CleanseError):
                cleanse.run_bounded(
                    [sys.executable, "-c", parent], "draft", Path(temporary), 0.1
                )
            time.sleep(0.6)
            self.assertFalse(marker.exists())


class SaveTests(unittest.TestCase):
    def test_failed_flush_leaves_no_candidate_or_temporary_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "draft.md"
            with patch("cleanse.os.fsync", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    cleanse.save_new(path, "Invoices can be exported.")
            self.assertEqual(list(path.parent.iterdir()), [])

    def test_atomic_creation_refuses_overwrite_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "draft.md"
            cleanse.save_new(path, "Original bytes.\n")
            self.assertEqual(path.read_bytes(), b"Original bytes.\n")
            with self.assertRaises(FileExistsError):
                cleanse.save_new(path, "Replacement")
            self.assertEqual(path.read_bytes(), b"Original bytes.\n")
            self.assertEqual(list(path.parent.iterdir()), [path])


class CleanseCLITests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.draft = Path(self.temporary.name) / "draft.md"
        self.draft.write_text(
            "It is worth noting that the export runs.\n", encoding="utf-8"
        )
        self.output = self.draft.with_name("revised.md")

    def invoke(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = cleanse.main([str(self.draft), "--writer", "openai", *extra])
        return status, out.getvalue(), err.getvalue()

    def test_success_saves_copy_only_and_preserves_source(self):
        original = self.draft.read_bytes()
        with (
            patch("cleanse.select_reviewer", return_value=("claude", "/bin/claude")),
            patch(
                "cleanse.model_pass",
                return_value=("The export runs.\n", ["Removed filler."]),
            ),
        ):
            status, out, err = self.invoke("--output", str(self.output))
        self.assertEqual(status, 0)
        self.assertEqual(out, "")
        self.assertEqual(self.output.read_bytes(), b"The export runs.\n")
        self.assertEqual(self.draft.read_bytes(), original)
        self.assertIn("Removed filler.", err)
        self.assertIn("before 4/5, after 5/5", err)

    def test_blocking_candidate_is_saved_for_review_and_exits_one(self):
        with (
            patch("cleanse.select_reviewer", return_value=("claude", "/bin/claude")),
            patch("cleanse.model_pass", return_value=("Delve into exports.", [])),
        ):
            status, _, _ = self.invoke("--output", str(self.output))
        self.assertEqual(status, 1)
        self.assertEqual(self.output.read_text(), "Delve into exports.")

    def test_no_candidate_on_model_failure_or_empty_extraction(self):
        for value in (cleanse.CleanseError("failed", 124), ("`Delve`", [])):
            with self.subTest(value=value):
                options = (
                    {"side_effect": value}
                    if isinstance(value, Exception)
                    else {"return_value": value}
                )
                with (
                    patch(
                        "cleanse.select_reviewer",
                        return_value=("claude", "/bin/claude"),
                    ),
                    patch("cleanse.model_pass", **options),
                ):
                    status, out, _ = self.invoke("--output", str(self.output))
                self.assertIn(status, (2, 124))
                self.assertEqual(out, "")
                self.assertFalse(self.output.exists())

    def test_bad_input_never_calls_model(self):
        cases = (
            ("--timeout", "nan"),
            ("--timeout", "inf"),
            ("--timeout", "0"),
            ("--prompt-only", "--output", str(self.output)),
            (),
        )
        with patch("cleanse.model_pass") as model:
            for args in cases:
                with self.subTest(args=args):
                    self.assertEqual(self.invoke(*args)[0], 2)
            self.draft.write_text("", encoding="utf-8")
            self.assertEqual(self.invoke("--output", str(self.output))[0], 2)
            model.assert_not_called()

    def test_existing_destination_is_rejected_before_model_call(self):
        self.output.write_text("Keep this.", encoding="utf-8")
        with patch("cleanse.model_pass") as model:
            self.assertEqual(self.invoke("--output", str(self.output))[0], 2)
            model.assert_not_called()
        self.assertEqual(self.output.read_text(), "Keep this.")

    def test_manual_prompt_is_explicit_and_does_not_call_model(self):
        with patch("cleanse.model_pass") as model:
            status, out, err = self.invoke("--prompt-only")
            model.assert_not_called()
        self.assertEqual(status, 0)
        self.assertIn('"draft":', out)
        self.assertIn(self.draft.read_text().strip(), out)
        self.assertEqual(err, "")
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
