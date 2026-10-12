#!/usr/bin/env python3
"""Ask a different model family to edit a draft, validate the reply, and check it."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from check import audit, infer_format, report

HERE = Path(__file__).resolve().parent
FAMILIES = {"codex": "openai", "claude": "anthropic"}
SCHEMA = {
    "type": "object",
    "properties": {
        "copy": {"type": "string"},
        "notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["copy", "notes"],
    "additionalProperties": False,
}


class CleanseError(Exception):
    def __init__(self, message: str, status: int = 2):
        super().__init__(message)
        self.status = status


def select_reviewer(writer: str, requested: str | None = None) -> tuple[str, str]:
    if requested and FAMILIES[requested] == writer:
        raise CleanseError(
            "the reviewer must use a different model family from the writer"
        )
    candidates = (
        [requested]
        if requested
        else [name for name, family in FAMILIES.items() if family != writer]
    )
    for name in candidates:
        binary = shutil.which(name)
        if binary:
            return name, binary
    raise CleanseError(
        "no different-family CLI is installed; use --prompt-only for a manual pass", 127
    )


def make_prompt(source: str, audience: str, purpose: str) -> str:
    instructions = (HERE.parent / "prompts" / "cleanse.txt").read_text(encoding="utf-8")
    # JSON separates the editing brief from draft text without a collision-prone sentinel.
    return (
        instructions
        + "\n\n"
        + json.dumps(
            {"audience": audience, "purpose": purpose, "draft": source},
            ensure_ascii=False,
        )
    )


def run_bounded(
    command: list[str], prompt: str, directory: Path, timeout: float
) -> subprocess.CompletedProcess:
    # Stdin keeps the draft out of process arguments and shell history.
    # A new process group lets a POSIX timeout stop CLI children as well as the parent.
    with subprocess.Popen(
        command,
        cwd=directory,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        start_new_session=os.name == "posix",
    ) as process:
        try:
            stdout, stderr = process.communicate(prompt, timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            elif os.name == "nt":
                # taskkill is provided by Windows; /T also stops spawned children.
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            process.kill()
            process.communicate()
            raise CleanseError(
                "the model pass timed out or was interrupted; no draft was saved", 124
            ) from None
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def validate_reply(value: object) -> tuple[str, list[str]]:
    if not isinstance(value, dict) or set(value) != {"copy", "notes"}:
        raise CleanseError(
            "the model reply does not match the copy/notes schema; no draft was saved"
        )
    copy, notes = value["copy"], value["notes"]
    if not isinstance(copy, str) or not copy.strip():
        raise CleanseError("the model returned an empty draft; no draft was saved")
    if not isinstance(notes, list) or any(not isinstance(note, str) for note in notes):
        raise CleanseError(
            "the model returned invalid change notes; no draft was saved"
        )
    return copy, notes


def model_pass(
    name: str, binary: str, prompt: str, model: str | None, timeout: float
) -> tuple[str, list[str]]:
    with tempfile.TemporaryDirectory(prefix="hooman-edit-") as temporary:
        directory = Path(temporary)
        schema = directory / "schema.json"
        response = directory / "response.json"
        schema.write_text(json.dumps(SCHEMA), encoding="utf-8")
        if name == "codex":
            command = [
                binary,
                "exec",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--disable",
                "shell_tool",
                "--disable",
                "unified_exec",
                "-c",
                'model_provider="openai"',
                "--output-schema",
                str(schema),
                "--output-last-message",
                str(response),
            ]
        else:
            command = [
                binary,
                "--print",
                "--safe-mode",
                "--restricted",
                "--tools",
                "",
                "--strict-mcp-config",
                "--mcp-config",
                '{"mcpServers":{}}',
                "--no-session-persistence",
                "--permission-mode",
                "dontAsk",
                "--output-format",
                "json",
                "--json-schema",
                json.dumps(SCHEMA),
            ]
        if model:
            command += ["--model", model]
        if name == "codex":
            command.append("-")
        completed = run_bounded(command, prompt, directory, timeout)
        if completed.returncode:
            raise CleanseError(
                f"{name} exited with status {completed.returncode}; no draft was saved. Check CLI authentication and supported flags."
            )
        try:
            if name == "codex":
                value = json.loads(response.read_text(encoding="utf-8"))
            else:
                envelope = json.loads(completed.stdout)
                if (
                    not isinstance(envelope, dict)
                    or envelope.get("is_error")
                    or envelope.get("subtype") != "success"
                ):
                    raise CleanseError(
                        "the reviewer did not return a successful result; no draft was saved"
                    )
                value = envelope.get("structured_output")
            return validate_reply(value)
        except (OSError, ValueError) as error:
            raise CleanseError(
                "the reviewer did not return valid structured output; no draft was saved"
            ) from error


def save_new(path: Path, copy: str) -> None:
    """Publish a complete file atomically, refusing an existing destination."""
    staged = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=".hooman-",
            delete=False,
        ) as temporary:
            staged = Path(temporary.name)
            temporary.write(copy)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.link(staged, path)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="UTF-8 draft, or - for stdin")
    parser.add_argument(
        "--writer",
        required=True,
        choices=("openai", "anthropic", "google", "other"),
        help="The model family that wrote the draft",
    )
    parser.add_argument(
        "--reviewer",
        choices=tuple(FAMILIES),
        help="Select a different-family CLI explicitly",
    )
    parser.add_argument(
        "--model",
        help="Optional model ID for the selected CLI; otherwise use its default",
    )
    parser.add_argument("--audience", default="Infer from the draft")
    parser.add_argument(
        "--purpose",
        default="Edit for clarity and natural phrasing while preserving meaning",
    )
    parser.add_argument("--timeout", type=float, default=180, metavar="SECONDS")
    parser.add_argument(
        "--format", choices=("auto", "text", "markdown", "html"), default="auto"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save to a new file; an existing file is never overwritten",
    )
    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="Print instructions and draft for manual use; do not call a model",
    )
    args = parser.parse_args(argv)
    try:
        if not math.isfinite(args.timeout) or args.timeout <= 0:
            raise CleanseError("--timeout must be a finite positive number")
        if args.prompt_only and args.output:
            raise CleanseError("--prompt-only cannot be combined with --output")
        if not args.prompt_only and args.output is None:
            raise CleanseError("--output is required for a model pass")
        if args.output and (args.output.exists() or args.output.is_symlink()):
            raise CleanseError("the output already exists; choose a new path")
        if args.output and not args.output.parent.is_dir():
            raise CleanseError("the output parent directory does not exist")
        source = (
            sys.stdin.read()
            if args.path == "-"
            else Path(args.path).read_text(encoding="utf-8-sig")
        )
        format = infer_format(args.path, args.format)
        before = audit(source, format)
        prompt = make_prompt(source, args.audience, args.purpose)
        if args.prompt_only:
            print(prompt)
            return 0
        name, binary = select_reviewer(args.writer, args.reviewer)
        copy, notes = model_pass(name, binary, prompt, args.model, args.timeout)
        after = audit(copy, format)
        save_new(args.output, copy)
        print(
            f"Saved {args.output}; reviewer {name}; before {before['score']}/5, after {after['score']}/5.",
            file=sys.stderr,
        )
        for note in notes:
            print(f"  {note}", file=sys.stderr)
        report({"path": str(args.output), **after}, stream=sys.stderr)
        print(
            "Compare the saved draft with the original for factual drift and protected content before using it.",
            file=sys.stderr,
        )
        return 0 if after["passed"] else 1
    except CleanseError as error:
        print(f"hooman: {error}", file=sys.stderr)
        return error.status
    except (OSError, UnicodeError, ValueError) as error:
        print(f"hooman: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="strict")
    for output in (sys.stdout, sys.stderr):
        if hasattr(output, "reconfigure"):
            output.reconfigure(errors="replace")
    raise SystemExit(main())
