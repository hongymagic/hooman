#!/usr/bin/env python3
"""Check English prose for editing patterns. Standard library only; never edits input."""

from __future__ import annotations

import argparse
import bisect
import html
import json
import re
import sys
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    severity: str
    pattern: str
    advice: str


# Explicit inflections avoid matching unrelated words through guessed stems.
RULES = (
    Rule(
        "word.delving",
        "wording",
        "error",
        r"\bdelv(?:e|es|ed|ing)\b",
        "Say what the reader will learn or do.",
    ),
    Rule(
        "word.hype",
        "wording",
        "error",
        r"\b(?:game[ -]chang(?:er|ing)|revolutioni[sz](?:e|es|ed|ing)|unparalleled|supercharg(?:e|es|ed|ing)|turbocharg(?:e|es|ed|ing))\b",
        "Describe the specific change or capability.",
    ),
    Rule(
        "word.promotion",
        "wording",
        "review",
        r"\b(?:seamless(?:ly)?|empower(?:s|ed|ing)?|unlock(?:s|ed|ing)?|leverage[sd]?|leveraging|robust|holistic|synerg(?:y|ies)|bespoke|world[ -]class)\b",
        "Check the context; keep literal and technical uses.",
    ),
    Rule(
        "word.stature",
        "wording",
        "review",
        r"\b(?:cutting[ -]edge|state[ -]of[ -]the[ -]art|best[ -]in[ -]class|industry[ -]leading|groundbreaking)\b",
        "Replace unsupported stature with evidence you have.",
    ),
    Rule(
        "frame.scene",
        "framing",
        "error",
        r"\b(?:in today's (?:fast[ -]paced|ever[ -]evolving|digital) (?:digital )?(?:world|landscape)|in the ever[ -]evolving (?:world|landscape)|let's (?:dive|delve) (?:in|into))\b",
        "Start with the subject and its relevance to this reader.",
    ),
    Rule(
        "frame.announcement",
        "framing",
        "error",
        r"\b(?:it is (?:important|worthwhile|essential) to (?:note|mention)|it's (?:important|worthwhile|essential) to (?:note|mention)|it is worth noting|it's worth noting|i just wanted to (?:take a moment to |)(?:reach out|let you know))\b",
        "Remove the announcement and keep the information.",
    ),
    Rule(
        "frame.suspense",
        "framing",
        "error",
        r"\bthe (?:result|secret|kicker|upshot)\?",
        "State the result directly unless the question serves the reader.",
    ),
    Rule(
        "frame.contrast",
        "framing",
        "review",
        r"\bnot (?:just|merely|only)\b[^.!?\n]{0,100}\bbut\b|\b(?:isn't|is not|aren't|are not) just\b[^!?\n]{0,100}[.!]\s*(?:it(?:'s| is)|they(?:'re| are))\b",
        "Keep real distinctions; remove a slogan that merely inflates the claim.",
    ),
    Rule(
        "frame.hedges",
        "framing",
        "review",
        r"\b(?:may potentially|might possibly|could perhaps potentially)\b",
        "Keep the qualification that carries the actual uncertainty.",
    ),
    Rule(
        "repeat.synonyms",
        "repetition",
        "error",
        r"\b(?:each and every|first and foremost|in order to be able to|at this (?:point|moment) in time)\b",
        "Use one precise expression.",
    ),
    Rule(
        "cadence.triad",
        "cadence",
        "review",
        r"\b(?:fast(?:er)?|smart(?:er)?|simple(?:r)?|better|bolder|stronger),\s+(?:fast(?:er)?|smart(?:er)?|simple(?:r)?|better|bolder|stronger),?\s+and\s+(?:fast(?:er)?|smart(?:er)?|simple(?:r)?|better|bolder|stronger)\b",
        "Replace decorative adjectives with a useful detail; keep meaningful lists.",
    ),
    Rule(
        "evidence.numbers",
        "evidence",
        "review",
        r"\b\d[\d,]*(?:\.\d+)?\+?\s+(?:(?:active|happy|paying|satisfied)\s+)?(?:customers?|users?|clients?|subscribers?|teams?)\b|\b\d+(?:\.\d+)?\s*%\s+(?:faster|cheaper|growth|increase|reduction)\b",
        "Verify the source, scope and measurement; a number is not evidence of fabrication.",
    ),
    Rule(
        "evidence.placeholder",
        "evidence",
        "error",
        r"\[(?:needs? (?:proof|source|number|citation)|insert (?:statistic|testimonial|metric))\]",
        "Resolve the missing evidence before publication; never fill it by guessing.",
    ),
)
CATEGORIES = ("wording", "framing", "repetition", "cadence", "evidence")
RULE_IDS = {rule.id for rule in RULES} | {"repeat.sentence", "cadence.dashes"}
NORMALISE = str.maketrans({"’": "'", "‘": "'", "‑": "-", "–": "-", "\xa0": " "})


@dataclass(frozen=True)
class Finding:
    rule: str
    category: str
    severity: str
    line: int
    column: int
    text: str
    advice: str
    allowance: str | None = None


@dataclass
class Prose:
    text: str
    positions: list[int]


def blank(value: str) -> str:
    return "".join("\n" if char == "\n" else " " for char in value)


def markdown_mask(source: str) -> str:
    """Mask common literal Markdown forms without changing source offsets."""
    text = source
    if text.startswith("---\n"):
        match = re.match(r"\A---\n.*?\n(?:---|\.\.\.)[ \t]*(?:\n|$)", text, re.S)
        if match:
            text = blank(match[0]) + text[match.end() :]
    lines = text.splitlines(keepends=True)
    fence: tuple[str, int] | None = None
    for index, line in enumerate(lines):
        opener = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            lines[index] = blank(line)
            if re.fullmatch(
                r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*\n?",
                line,
            ):
                fence = None
        elif opener:
            fence = (opener[1][0], len(opener[1]))
            lines[index] = blank(line)
        elif re.match(r"^(?: {0,3}>| {4}|\t| {0,3}\[[^\]]+\]:[ \t]*\S)", line):
            lines[index] = blank(line)
    text = "".join(lines)
    for pattern in (
        r"(`+)(?!`).*?(?<!`)\1(?!`)",
        r"~~[^\n]*?~~",
        r"<https?://[^>\n]+>",
        r"<[^<>\s]+@[^<>\s]+>",
    ):
        text = re.sub(pattern, lambda m: blank(m[0]), text, flags=re.S)
    # Balanced destinations allow URLs such as /docs/function(a), including titles.
    chars = list(text)
    for match in re.finditer(r"\]\(", text):
        depth, end = 1, match.end()
        while end < len(text) and depth:
            if text[end] == "\\":
                end += 2
                continue
            depth += (text[end] == "(") - (text[end] == ")")
            end += 1
        if depth == 0:
            chars[match.start() + 1 : end] = blank(text[match.start() + 1 : end])
    text = "".join(chars)
    text = re.sub(
        r"(\[[^\]\n]+\])\[[^\]\n]*\]", lambda m: m[1] + blank(m[0][len(m[1]) :]), text
    )
    return text


class ProseHTML(HTMLParser):
    """Extract static HTML text, mapping decoded entities back to source locations."""

    VOID = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    SKIP = {"head", "script", "style", "template", "pre", "code", "svg", "noscript"}
    BLOCK = {
        "p",
        "div",
        "section",
        "article",
        "header",
        "footer",
        "main",
        "li",
        "ul",
        "ol",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "br",
        "hr",
        "tr",
        "td",
        "th",
        "blockquote",
    }

    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.starts = [0] + [m.end() for m in re.finditer("\n", source)]
        self.stack: list[tuple[str, bool]] = []
        self.chars: list[str] = []
        self.positions: list[int] = []

    def source_offset(self) -> int:
        line, column = self.getpos()
        return self.starts[line - 1] + column

    def hidden(self) -> bool:
        return bool(self.stack and self.stack[-1][1])

    def boundary(self) -> None:
        self.chars.append("\n")
        self.positions.append(self.source_offset())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        hidden = (
            self.hidden()
            or tag in self.SKIP
            or "hidden" in values
            or (values.get("aria-hidden") or "").lower() == "true"
        )
        hidden = hidden or bool(
            re.search(
                r"(?:display\s*:\s*none|visibility\s*:\s*hidden)\b",
                values.get("style") or "",
                re.I,
            )
        )
        if tag in self.BLOCK:
            self.boundary()
        if tag not in self.VOID:
            self.stack.append((tag, hidden))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break
        if tag in self.BLOCK or tag in self.SKIP:
            self.boundary()

    def handle_data(self, data: str) -> None:
        if not self.hidden():
            self.chars.extend(data)
            self.positions.extend(
                range(self.source_offset(), self.source_offset() + len(data))
            )

    def entity(self, token: str) -> None:
        if not self.hidden():
            decoded = html.unescape(token)
            self.chars.extend(decoded)
            self.positions.extend([self.source_offset()] * len(decoded))

    def handle_entityref(self, name: str) -> None:
        self.entity("&" + name + ";")

    def handle_charref(self, name: str) -> None:
        self.entity("&#" + name + ";")


def extract(source: str, format: str) -> Prose:
    if format == "text":
        return Prose(source, list(range(len(source))))
    masked = markdown_mask(source) if format == "markdown" else source
    parser = ProseHTML(masked)
    parser.feed(masked)
    parser.close()
    return Prose("".join(parser.chars), parser.positions)


def infer_format(path: str, requested: str = "auto") -> str:
    if requested != "auto":
        return requested
    suffix = Path(path).suffix.lower()
    return (
        "markdown"
        if suffix in {".md", ".markdown", ".mdown"}
        else "html"
        if suffix in {".html", ".htm"}
        else "text"
    )


def allowances(values: list[str]) -> dict[str, str]:
    result = {}
    for value in values:
        rule, separator, reason = value.partition("=")
        if not separator or rule not in RULE_IDS or not reason.strip():
            raise ValueError(
                "--allow requires a known rule ID and a nonempty reason: RULE=REASON"
            )
        result[rule] = reason.strip()
    return result


def audit(
    source: str, format: str = "text", allowed: dict[str, str] | None = None
) -> dict:
    prose = extract(source, format)
    if not prose.text.strip():
        raise ValueError("no prose to check after excluding literal content")
    normal = prose.text.translate(NORMALISE)
    line_starts = [0] + [m.end() for m in re.finditer("\n", source)]
    findings: list[Finding] = []

    def add(rule: Rule, start: int, end: int) -> None:
        position = prose.positions[start]
        line_index = bisect.bisect_right(line_starts, position) - 1
        findings.append(
            Finding(
                rule.id,
                rule.category,
                rule.severity,
                line_index + 1,
                position - line_starts[line_index] + 1,
                re.sub(r"\s+", " ", prose.text[start:end]).strip(),
                rule.advice,
                (allowed or {}).get(rule.id),
            )
        )

    for rule in RULES:
        for match in re.finditer(rule.pattern, normal, re.I):
            add(rule, match.start(), match.end())
    previous = None
    duplicate = Rule(
        "repeat.sentence",
        "repetition",
        "error",
        "",
        "Remove the repeated sentence or supply its distinct information.",
    )
    dashes = Rule(
        "cadence.dashes",
        "cadence",
        "review",
        "",
        "Check repeated interruptions; keep punctuation that carries meaning.",
    )
    for match in re.finditer(r"[^.!?\n]+[.!?]?", normal):
        sentence = re.sub(r"\s+", " ", match[0]).strip().casefold()
        if len(sentence.split()) >= 5 and sentence == previous:
            add(duplicate, match.start(), match.end())
        if match[0].count("—") >= 3:
            add(dashes, match.start(), match.end())
        previous = sentence if sentence else previous
    findings.sort(key=lambda finding: (finding.line, finding.column, finding.rule))
    blocking = {
        finding.category
        for finding in findings
        if finding.severity == "error" and not finding.allowance
    }
    return {
        "score": 5 - len(blocking),
        "maximum": 5,
        "passed": not blocking,
        "language": "en",
        "format": format,
        "words": len(prose.text.split()),
        "findings": [asdict(finding) for finding in findings],
    }


def report(result: dict, stream=None) -> None:
    stream = stream or sys.stdout
    print(
        f"{result.get('path', '<text>')}: {result['score']}/5; {result['words']} words; "
        + ("no blocking patterns" if result["passed"] else "editing required"),
        file=stream,
    )
    for finding in result["findings"]:
        status = (
            "allowed: " + finding["allowance"]
            if finding["allowance"]
            else finding["severity"]
        )
        print(
            f"  {finding['line']}:{finding['column']} [{finding['rule']}] {status}: {finding['text']}",
            file=stream,
        )
        print(f"    {finding['advice']}", file=stream)
    print(
        "  English patterns only. Review findings and factual accuracy before publication.",
        file=stream,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="UTF-8 files, or - for stdin")
    parser.add_argument("--text", help="Check a literal string instead of files")
    parser.add_argument(
        "--format", choices=("auto", "text", "markdown", "html"), default="auto"
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Only English (en) is supported; no language detection",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable report, including input errors",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Also fail for unresolved review findings"
    )
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        metavar="RULE=REASON",
        help="Keep a finding visible but exempt it for this invocation",
    )
    args = parser.parse_args(argv)
    results, errors = [], []
    try:
        if args.language.lower().split("-")[0] != "en":
            raise ValueError("unsupported language; the checker covers English only")
        if (args.text is not None and args.paths) or (
            args.text is None and not args.paths
        ):
            raise ValueError(
                "provide files, - for stdin, or --text; do not combine --text with files"
            )
        if args.paths.count("-") > 1:
            raise ValueError("stdin can only be read once")
        allowed = allowances(args.allow)
        for path in args.paths or ["<text>"]:
            try:
                source = (
                    args.text
                    if args.text is not None
                    else sys.stdin.read()
                    if path == "-"
                    else Path(path).read_text(encoding="utf-8-sig")
                )
                result = {
                    "path": path,
                    **audit(source, infer_format(path, args.format), allowed),
                }
                results.append(result)
            except (OSError, UnicodeError, ValueError) as error:
                errors.append({"path": path, "message": str(error)})
    except ValueError as error:
        errors.append({"path": None, "message": str(error)})
    passed = not errors and all(
        result["passed"]
        and (not args.strict or all(f["allowance"] for f in result["findings"]))
        for result in results
    )
    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "passed": passed,
                    "results": results,
                    "errors": errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for result in results:
            report(result)
        for error in errors:
            print(
                f"hooman: {error['path'] or 'input'}: {error['message']}",
                file=sys.stderr,
            )
    return 2 if errors else 0 if passed else 1


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="strict")
    for output in (sys.stdout, sys.stderr):
        if hasattr(output, "reconfigure"):
            output.reconfigure(errors="replace")
    raise SystemExit(main())
