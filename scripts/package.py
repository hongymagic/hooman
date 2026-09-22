#!/usr/bin/env python3
"""Validate and package the single Markdown skill using only the standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
IDENTITY_FIELDS = (
    "name", "version", "description", "author", "homepage", "repository", "license", "keywords"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(relative: str) -> dict:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"Expected an object: {relative}")
    return value


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def source_files() -> dict[str, bytes]:
    files = {}
    for path in sorted((ROOT / "human-writing").rglob("*")):
        require(not path.is_symlink(), f"Release source must not contain symlinks: {path}")
        if path.is_file():
            name = path.relative_to(ROOT).as_posix()
            require(not path.name.startswith("."), f"Unexpected hidden runtime file: {name}")
            require(path.suffix not in {".py", ".pyc", ".sh", ".js", ".exe"},
                    f"Unexpected executable runtime resource: {name}")
            files[name] = path.read_bytes()
    return files


def validate(tag: str | None) -> tuple[str, dict, dict, dict[str, bytes]]:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version)
            is not None, "VERSION must contain a stable semantic version, such as 0.1.0")
    require(tag is None or tag == f"v{version}", f"Tag {tag!r} must match v{version}")
    codex = read_json(".codex-plugin/plugin.json")
    claude = read_json(".claude-plugin/plugin.json")
    for manifest in (codex, claude):
        require(manifest.get("name") == "hooman", "Plugin name must be hooman")
        require(manifest.get("version") == version, "Plugin versions must match VERSION")
        require(manifest.get("skills") == "./human-writing", "Source must use the canonical skill")
        require(not {"hooks", "mcpServers", "apps"}.intersection(manifest),
                "This package is a standalone Markdown skill")
    for key in IDENTITY_FIELDS:
        require(codex.get(key) == claude.get(key), f"Manifest metadata differs: {key}")
        require(bool(codex.get(key)), f"Missing manifest metadata: {key}")
    codex_market = read_json(".agents/plugins/marketplace.json")
    claude_market = read_json(".claude-plugin/marketplace.json")
    for market in (codex_market, claude_market):
        require(market.get("name") == "hooman", "Marketplace name must be hooman")
        require(len(market.get("plugins", [])) == 1, "Expected exactly one marketplace plugin")
        require(market["plugins"][0].get("name") == "hooman", "Marketplace plugin must be hooman")
    codex_entry = codex_market["plugins"][0]
    require(codex_entry.get("source") == {"source": "local", "path": "./"},
            "Codex marketplace must point to the repository root")
    require(codex_entry.get("policy") == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "Unexpected Codex marketplace policy")
    require(claude_market["plugins"][0].get("source") == "./", "Claude marketplace must use the repository root")
    require(claude_market["plugins"][0].get("version") == version, "Marketplace version must match VERSION")

    files = source_files()
    for name in ("SKILL.md", "README.md", "references/style-guide.md",
                 "evals/cases.md", "NOTICE.md"):
        require(bool(files.get(f"human-writing/{name}")), f"Missing or empty skill resource: {name}")
    require(any(name.startswith("human-writing/licenses/") for name in files), "Missing upstream licences")
    text = files["human-writing/SKILL.md"].decode("utf-8")
    parts = text.split("---\n", 2)
    require(len(parts) == 3 and parts[0] == "", "SKILL.md needs closed YAML frontmatter")
    require(re.search(r"^name: human-writing\s*$", parts[1], re.MULTILINE) is not None,
            "Skill name must match human-writing")
    require(re.search(r"^description: .+", parts[1], re.MULTILINE) is not None,
            "Skill frontmatter needs a description")
    words = len(parts[2].split())
    require(words <= 1500, f"Core skill exceeds 1,500 words: {words}")
    licence = (ROOT / "LICENSE").read_bytes()
    require(bool(licence.strip()), "Missing project licence")
    if "human-writing/LICENSE" in files:
        require(files["human-writing/LICENSE"] == licence, "Root and skill project licences differ")
    files["human-writing/LICENSE"] = licence
    print(f"Validated metadata, version {version}, runtime resources, and core length ({words} words).")
    return version, codex, claude, files


def write_zip(path: Path, files: dict[str, bytes]) -> None:
    # Stored entries avoid compressor-version differences; this small package needs no compression.
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, contents in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, contents)
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None, f"Corrupt archive: {path.name}")
        require(set(archive.namelist()) == set(files), f"Archive inventory differs: {path.name}")
        for name, contents in files.items():
            require(archive.read(name) == contents, f"Archive changed source bytes: {name}")


def build(output: Path, version: str, codex: dict, claude: dict, files: dict[str, bytes]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    standalone = output / f"human-writing-{version}.zip"
    plugin = output / f"hooman-{version}-plugin.zip"
    write_zip(standalone, files)
    portable = {"$schema": SCHEMA, **{key: codex[key] for key in IDENTITY_FIELDS}}
    portable["extensions"] = {"com.openai": {"interface": codex["interface"]}}
    plugin_files = {f"skills/{name}": content for name, content in files.items()}
    plugin_files.update({
        "plugin.json": json_bytes(portable),
        ".codex-plugin/plugin.json": json_bytes({**codex, "skills": "./skills/"}),
        ".claude-plugin/plugin.json": json_bytes({**claude, "skills": "./skills/"}),
        "LICENSE": files["human-writing/LICENSE"],
    })
    write_zip(plugin, plugin_files)
    checksums = "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
        for path in (standalone, plugin)
    )
    (output / "SHA256SUMS").write_text(checksums, encoding="ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate and compare two temporary builds")
    parser.add_argument("--tag", help="Require an exact release tag matching VERSION")
    args = parser.parse_args()
    validated = validate(args.tag)
    if args.check:
        with tempfile.TemporaryDirectory(prefix="hooman-check-") as temporary:
            first, second = (Path(temporary) / name for name in ("first", "second"))
            build(first, *validated)
            build(second, *validated)
            for path in first.iterdir():
                require(path.read_bytes() == (second / path.name).read_bytes(),
                        f"Build is not reproducible: {path.name}")
        print("Both archive layouts preserve source bytes; archive integrity and reproducibility passed.")
    else:
        build(ROOT / "dist", *validated)
        print("Built dist/human-writing-*.zip, dist/hooman-*-plugin.zip, and dist/SHA256SUMS.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Package validation failed: {error}", file=sys.stderr)
        sys.exit(1)
