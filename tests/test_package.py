from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import package  # noqa: E402 - load release tooling


class PackageTests(unittest.TestCase):
    def test_tag_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must match"):
            package.validate("v9.9.9")

    def test_archives_are_reproducible_and_helpers_work_after_extraction(self):
        with contextlib.redirect_stdout(io.StringIO()):
            validated = package.validate(None)
        version, _, _, files = validated
        self.assertFalse(
            any("__pycache__" in name or name.endswith(".pyc") for name in files)
        )
        with tempfile.TemporaryDirectory() as temporary:
            first, second = Path(temporary) / "first", Path(temporary) / "second"
            package.build(first, *validated)
            package.build(second, *validated)
            for path in first.iterdir():
                self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())
            for name, prefix in (
                (f"human-writing-{version}.zip", "human-writing"),
                (f"hooman-{version}-plugin.zip", "skills/human-writing"),
            ):
                with self.subTest(archive=name):
                    extracted = Path(temporary) / name.removesuffix(".zip")
                    with zipfile.ZipFile(first / name) as archive:
                        archive.extractall(extracted)
                    skill = extracted / prefix
                    check = subprocess.run(
                        [
                            sys.executable,
                            str(skill / "scripts/check.py"),
                            "--text",
                            "Invoices can be exported.",
                            "--json",
                        ],
                        cwd=temporary,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        check=False,
                    )
                    self.assertEqual(check.returncode, 0, check.stderr)
                    self.assertTrue(json.loads(check.stdout)["passed"])
                    prompt = subprocess.run(
                        [
                            sys.executable,
                            str(skill / "scripts/cleanse.py"),
                            str(skill / "README.md"),
                            "--writer",
                            "openai",
                            "--prompt-only",
                        ],
                        cwd=temporary,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        check=False,
                    )
                    self.assertEqual(prompt.returncode, 0, prompt.stderr)
                    self.assertIn('"draft":', prompt.stdout)
                    self.assertEqual(prompt.stderr, "")


if __name__ == "__main__":
    unittest.main()
