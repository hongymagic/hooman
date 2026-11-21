#!/usr/bin/env python3
"""Measure the checker against dated human and model text.

Maintainer tooling, outside the runtime bundle. `fetch` downloads public texts
into a cache and `measure` runs the checker over that cache. The texts are never
committed: calibration-corpus.json records sources, commits and hashes only.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "human-writing" / "scripts"))
from check import audit  # noqa: E402 - load the checker being measured

MANIFEST = Path(__file__).with_name("calibration-corpus.json")
# Manifest key and corpus name of each set of pinned human texts. The older set
# holds READMEs and reference documents as they stood before 2020.
HUMAN_SETS = {"human": "human-tech", "older": "human-older"}
ROWS = (
    "https://datasets-server.huggingface.co/rows"
    "?dataset=browndw/human-ai-parallel-corpus&config=default&split=train"
)
# First row of each author's block in the parallel corpus, and of each register
# within a block. Every block holds the same documents in the same order, so
# equal offsets give matched pairs.
AUTHORS = {"gpt4o": 0, "human": 24870}
REGISTERS = {"acad": 0, "blog": 1227, "news": 4148}
DOCUMENTS_PER_CELL = 200
PAGE = 100
# In reStructuredText a line of tildes or backticks underlines a heading. Read
# as Markdown it would open a code fence and hide the text below it.
RST_UNDERLINE = re.compile(r"(?m)^[~`]{3,}[ \t]*$")


def download(url: str) -> bytes:
    failure: Exception | None = None
    for attempt in range(5):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "hooman-calibration"}
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        # A body cut off mid-transfer raises IncompleteRead, which is not an OSError.
        except (OSError, http.client.HTTPException) as error:
            failure = error
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"could not fetch {url}: {failure}")


def cells() -> dict[str, int]:
    """Name and first row of each cell of the parallel corpus."""
    return {
        f"{author}-{register}": block + start
        for author, block in AUTHORS.items()
        for register, start in REGISTERS.items()
    }


def pins() -> dict:
    """The manifest: human texts by commit and hash, parallel cells by hash."""
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        described = (
            all(manifest[key] for key in HUMAN_SETS)
            and all(
                isinstance(entry[field], str)
                for key in HUMAN_SETS
                for entry in manifest[key]
                for field in ("repo", "commit", "path", "sha256")
            )
            and set(manifest["parallel"]) == set(cells())
            and all(isinstance(pin, str) for pin in manifest["parallel"].values())
        )
    except (ValueError, KeyError, TypeError, AttributeError):
        described = False
    if not described:
        raise RuntimeError(f"{MANIFEST.name} does not describe the pinned corpus")
    return manifest


def sources(human: list[dict]) -> list[tuple[str, dict]]:
    """Cache file name and manifest entry of each pinned human text."""
    return [
        (f"{index:02d}-{Path(entry['path']).name}", entry)
        for index, entry in enumerate(human)
    ]


def digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def holds(path: Path, pin: str) -> bool:
    """True when the cache holds this file exactly as it was pinned."""
    return path.is_file() and digest(path.read_bytes()) == pin


def page(body: bytes, name: str) -> list[dict]:
    """The documents in one page of rows from the dataset server."""
    try:
        items = json.loads(body)["rows"]
        cut = any(item["truncated_cells"] for item in items)
        rows = [
            {"doc_id": item["row"]["doc_id"], "text": item["row"]["text"]}
            for item in items
        ]
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise RuntimeError(
            f"{name}: unexpected reply from the dataset server"
        ) from error
    if cut:
        raise RuntimeError(f"{name}: the server cut texts short")
    return rows


def fetch(cache: Path) -> None:
    manifest = pins()
    for key, corpus in HUMAN_SETS.items():
        human = cache / corpus
        human.mkdir(parents=True, exist_ok=True)
        for name, entry in sources(manifest[key]):
            if holds(human / name, entry["sha256"]):
                continue
            body = download(
                f"https://raw.githubusercontent.com/{entry['repo']}/{entry['commit']}/{entry['path']}"
            )
            # Nothing reaches the cache until it matches the manifest.
            if digest(body) != entry["sha256"]:
                raise RuntimeError(f"hash mismatch for {entry['repo']}/{entry['path']}")
            (human / name).write_bytes(body)
    parallel = cache / "parallel"
    parallel.mkdir(exist_ok=True)
    for name, first in cells().items():
        target = parallel / f"{name}.jsonl"
        if holds(target, manifest["parallel"][name]):
            continue
        rows: list[dict] = []
        for offset in range(0, DOCUMENTS_PER_CELL, PAGE):
            reply = download(f"{ROWS}&offset={first + offset}&length={PAGE}")
            rows += page(reply, name)
        # One line of ASCII per document: the same bytes on every platform, and
        # no line separator inside a text can split a line.
        body = "".join(json.dumps(row) + "\n" for row in rows).encode()
        if digest(body) != manifest["parallel"][name]:
            raise RuntimeError(
                f"{name}: the {len(rows)} documents received differ from the "
                "pinned corpus; nothing cached"
            )
        target.write_bytes(body)
    print(f"Corpus cached in {cache}")


def corpora(cache: Path, extras: list[str]) -> dict[str, list[tuple[str, str]]]:
    """Corpus name to (format, text) pairs: the whole pinned corpus, then extras."""
    manifest = pins()
    sets: dict[str, list[tuple[str, str]]] = {}
    # Only what the manifest names, and all of it: a stale, changed or missing
    # file would shift every figure.
    for key, corpus in HUMAN_SETS.items():
        sets[corpus] = []
        for name, entry in sources(manifest[key]):
            path = cache / corpus / name
            if not holds(path, entry["sha256"]):
                raise RuntimeError(
                    f"{path} is missing or differs from the manifest; run fetch first"
                )
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            # reStructuredText is close enough to Markdown for code masking, once
            # its underlines are out of the way.
            if path.suffix != ".md":
                text = RST_UNDERLINE.sub("", text)
            sets[corpus].append(("markdown", text))
    for name in cells():
        path = cache / "parallel" / f"{name}.jsonl"
        if not holds(path, manifest["parallel"][name]):
            raise RuntimeError(
                f"{path} is missing or differs from the manifest; run fetch first"
            )
        lines = path.read_bytes().decode("ascii").split("\n")
        sets[name] = [("text", json.loads(line)["text"]) for line in lines if line]
    for extra in extras:
        name, _, folder = extra.partition("=")
        if not (name and folder and Path(folder).is_dir()):
            raise ValueError(
                f"--extra takes NAME=DIR with an existing directory: {extra}"
            )
        if name in sets:
            raise ValueError(f"--extra {name}: that name is already in use")
        files = sorted(Path(folder).glob("*.md")) + sorted(Path(folder).glob("*.txt"))
        if not files:
            raise ValueError(f"--extra {name}: no .md or .txt files in {folder}")
        sets[name] = [
            ("markdown" if path.suffix == ".md" else "text", path.read_text("utf-8-sig"))
            for path in files
        ]
    return sets


def measure(cache: Path, extras: list[str], show_rules: bool) -> None:
    sets = corpora(cache, extras)
    blocked: dict[str, Counter] = {}
    hits: dict[str, Counter] = {}
    sizes = {}
    print(
        f"{'corpus':16}{'docs':>6}{'words':>9}{'fail %':>8}{'block/1k':>10}{'review/1k':>11}"
    )
    for name, documents in sets.items():
        words = failing = blocking = review = checked = 0
        blocked[name], hits[name] = Counter(), Counter()
        for format, text in documents:
            try:
                result = audit(text, format)
            except ValueError:
                continue
            checked += 1
            words += result["words"]
            failing += not result["passed"]
            blocking += result["blocking"]
            review += result["review"]
            hits[name].update(finding["rule"] for finding in result["findings"])
            blocked[name].update(
                {f["rule"] for f in result["findings"] if f["severity"] == "error"}
            )
        sizes[name] = (checked, words)
        print(
            f"{name:16}{checked:6d}{words:9d}{100 * failing / max(checked, 1):8.1f}"
            f"{1000 * blocking / max(words, 1):10.2f}{1000 * review / max(words, 1):11.2f}"
        )
    if not show_rules:
        return
    for title, table, scale in (
        ("% of documents with a blocking finding, by rule", blocked, 0),
        ("findings per 100,000 words, by rule", hits, 1),
    ):
        print(f"\n{title}")
        print(f"{'':28}" + "".join(f"{name[:11]:>12}" for name in sets))
        for rule in sorted({rule for counter in table.values() for rule in counter}):
            columns = [
                100000 * table[name][rule] / max(sizes[name][1], 1)
                if scale
                else 100 * table[name][rule] / max(sizes[name][0], 1)
                for name in sets
            ]
            print(f"{rule:28}" + "".join(f"{cell:12.1f}" for cell in columns))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("fetch", "measure"))
    parser.add_argument(
        "--cache",
        type=Path,
        default=ROOT / ".calibration",
        help="Where fetched texts are kept; ignored by git",
    )
    parser.add_argument(
        "--extra",
        action="append",
        default=[],
        metavar="NAME=DIR",
        help="Also measure the .md and .txt files in a directory",
    )
    parser.add_argument("--rules", action="store_true", help="Add per-rule tables")
    args = parser.parse_args(argv)
    try:
        if args.command == "fetch":
            fetch(args.cache)
        else:
            measure(args.cache, args.extra, args.rules)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"calibrate: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
