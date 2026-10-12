#!/usr/bin/env python3
"""Run the release's tests, prose checks and reproducible package validation."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    documents = [
        root / "README.md",
        *(root / "docs").glob("*.md"),
        *(root / "human-writing").glob("*.md"),
        *(root / "human-writing" / "references").glob("*.md"),
    ]
    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        [
            sys.executable,
            "human-writing/scripts/check.py",
            *(str(path) for path in sorted(documents)),
        ],
        [sys.executable, "scripts/package.py", "--check"],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=root, check=False)
        if completed.returncode:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
