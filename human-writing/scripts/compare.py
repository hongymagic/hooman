#!/usr/bin/env python3
"""Compare a revision with its source and list the fact-bearing tokens that changed.

Standard library only; never edits input. A clean comparison shows that these
tokens survived. It cannot show that the meaning did.
"""

from __future__ import annotations

import argparse
import bisect
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Isolated interpreters (python -I) leave the script's directory off the path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import (  # noqa: E402
    DEFINITION,
    DESTINATION,
    FRONT_MATTER,
    LITERAL_LESS_THAN,
    NEWLINE,
    NORMALISE,
    ORDERED,
    Elements,
    block_kind,
    blocks,
    concealed,
    flow,
    infer_format,
    line_kinds,
    literal_markup,
    stem,
)

# A token of these kinds that disappears or appears is an error; the other
# kinds ask for a second look.
BLOCKING = ("numbers", "dates", "links", "code", "quotes")
UNITS = "one two three four five six seven eight nine".split()
TEENS = (
    "ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen"
).split()
TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()
WORD_VALUES = {
    "zero": 0,
    **{word: value for value, word in enumerate(UNITS, 1)},
    **{word: value for value, word in enumerate(TEENS, 10)},
    **{word: 10 * value for value, word in enumerate(TENS, 2)},
}
# "one" is usually a pronoun, so on its own it is not a figure; `compare`
# lets it stand in for a 1 only beside the same word. "Zero-knowledge" and
# "zero-day" are terms, not counts.
NUMBER_WORD = (
    rf"\b(?:(?:{'|'.join(TENS)})(?:[- ](?:{'|'.join(UNITS)}))?"
    rf"|{'|'.join(['zero(?!-)', *UNITS[1:], *TEENS])}"
    r"|hundred|thousand|million|billion|half|twice|dozen)\b"
)
NUMBER = re.compile(
    # A sign belongs to the figure after a space or a bracket. Between two
    # figures the same mark is a range or a date.
    r"(?P<sign>(?<![\w.-])[-−+])?"
    r"(?P<currency>(?-i:[A-Z]{1,3})?[$€£¥])?"
    r"(?P<figure>(?:\d{1,3}(?:,\d{3})+(?!\d)|\d+)(?:[.:]\d+)*|(?<![\w.])\.\d+)"
    r"(?P<suffix> ?%| ?per ?cent\b|(?:st|nd|rd|th)\b"
    r"| ?(?:[ap]\.?m\b\.?|ms|bn|[kmxsh])\b)?"
    rf"|(?P<word>{NUMBER_WORD})",
    re.I,
)
# Suffixes that are a way of writing, not part of the figure.
SUFFIXES = {"percent": "%", "st": "", "nd": "", "rd": "", "th": ""}
MONTHS = "January|February|April|June|July|August|September|October|November|December"
WEEKDAYS = "Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
# "May I", "the sun" and "we sat" are not dates; these need a number or a
# preposition beside them.
SHORT_DATES = (
    "May|March|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec"
    "|Mon|Tues?|Wed|Thu(?:rs?)?|Fri|Sat|Sun"
)
BEFORE_A_MONTH = "in by of on until since from during early late".split()
DATE = re.compile(
    rf"\b(?i:{MONTHS}|(?:{WEEKDAYS})s?)\b"
    rf"|(?:(?<=\d\s)|(?<=\d(?i:st|nd|rd|th)\s))(?:{SHORT_DATES})\b"
    rf"|\b(?:{SHORT_DATES})\b\.?(?=\s\d)"
    "|(?:"
    + "|".join(rf"(?<=\b(?i:{word})\s)" for word in BEFORE_A_MONTH)
    + r")(?:May|March|MAY|MARCH)\b"
)
URL = re.compile(
    r"(?<![\w.+-])(?:[A-Za-z][A-Za-z0-9+.-]{1,20}://|mailto:|www\.(?=[\w-]+\.[\w-]))"
    r"[^\s<>\[\]\"'`]+"
    r"|(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
)
FENCE = re.compile(r"[ \t]*(`{3,}|~{3,})")
INDENTED = re.compile(r" {4}|\t")
# In Markdown a backslash before punctuation is an escape: "5\%" reads "5%".
ESCAPED = r"\\([!-/:-@\[-`{-~])"
BLOCKQUOTE = re.compile(r" {0,3}(?:>[ \t]?)+")
# Private-use marks set around what the reader sees as code, a quotation or a
# link target. Each pass leaves them in the text, so that content a later pass
# drops (an HTML comment, a hidden element) takes its literals with it.
CODE_OPEN, CODE_CLOSE, QUOTE_OPEN, QUOTE_CLOSE = "", "", "", ""
BLOCK_OPEN, BLOCK_CLOSE, LINK_OPEN, LINK_CLOSE = "", "", "", ""
PRIVATE = dict.fromkeys(range(0xE000, 0xE009))
CODE_MARKS = dict.fromkeys(map(ord, CODE_OPEN + CODE_CLOSE))
CODE_SPAN = re.compile(f"{CODE_OPEN}([^{CODE_CLOSE}]*){CODE_CLOSE}")
CODE_BLOCK = re.compile(f"{BLOCK_OPEN}([^{BLOCK_CLOSE}]*){BLOCK_CLOSE}")
LINK_TARGET = re.compile(f"{LINK_OPEN}([^{LINK_CLOSE}]*){LINK_CLOSE}")
# Code is literal: a bracket or a backtick inside it is not Markdown.
MARKED_CODE = f"{BLOCK_OPEN}[^{BLOCK_CLOSE}]*{BLOCK_CLOSE}|{CODE_OPEN}[^{CODE_CLOSE}]*{CODE_CLOSE}"
# A code span may wrap across lines but never across a blank line. It opens
# only at the head of a backtick run, which keeps a long run linear.
INLINE_CODE = re.compile(
    MARKED_CODE + r"|(?<!`)(`+)(?!`)((?:(?!\n[ \t]*\n).)+?)(?<!`)\1(?!`)", re.S
)
REFERENCE = re.compile(
    MARKED_CODE + r"|\[([^\]\n]{1,500})\](?:\[([^\]\n]{0,500})\])?(?!\()"
)
LINK_DESTINATION = re.compile(MARKED_CODE + "|(" + DESTINATION.pattern + ")", re.S)
# "](target "title")": a target without spaces, then an optional title.
LINK = re.compile(
    r"\s*(<[^<>\n]*>|[^\s<>]\S*)?(?:\s+(\"[^\"]*\"|'[^']*'|\([^()]*\)))?\s*"
)
QUOTATIONS = (
    re.compile(f"{QUOTE_OPEN}([^{QUOTE_OPEN}{QUOTE_CLOSE}]*){QUOTE_CLOSE}"),
    # Read after curly marks are made straight, so that flattening them never
    # changes which words are quoted. An inch mark opens nothing: 27" is a size.
    re.compile(r'(?<!\w)"(?=\S)([^"\n]*?)(?<=\S)"(?!\w)'),
)
# A line broken after the hyphen of a compound is still one word.
HYPHEN_BREAK = re.compile(r"(?<=[A-Za-z]-)\n(?=[A-Za-z])")
NAME = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:['_-][A-Za-z0-9]+)*")
NEGATION = re.compile(
    r"\b(?:not|no|never|none|neither|nor|without|cannot|\w{1,20}n't)\b(?:\W+\w+){0,2}",
    re.I,
)
MODALITY = re.compile(
    r"\b(?:may|might|could|should|must|shall|will|would|can|cannot|likely|unlikely"
    r"|probably|possibly|perhaps|approximately|roughly|nearly|almost|at least|at most"
    r"|up to|only|unless|until|except|if|provided|pending|subject to|expected"
    r"|estimated|planned|proposed|draft|tentative)\b",
    re.I,
)
CONTENT_WORD = re.compile(r"[a-z][a-z'-]{3,}")
FUNCTION_WORDS = frozenset(
    "about after also been before being both could does each from have here into"
    " just more most much must only other over same should some such than that"
    " their them then there these they this those very were what when where which"
    " while will with would your".split()
)
# Words that open sentences without being names. A capitalised word elsewhere
# in a sentence is taken as a name; one that opens a sentence is taken as a
# name only if it is not listed here and never appears in lower case.
SENTENCE_OPENERS = FUNCTION_WORDS | frozenset(
    "the and but for not all any are can did has had her his how its let may new"
    " now our out see she too use was who why yes you add back done even ever"
    " every few first get give goes going good great help however instead keep"
    " last later like long look made make many maybe might need never next none"
    " often once one open otherwise overall perhaps please put read run save"
    " second send set show since still sure take thanks thank third though three"
    " thus today try two under until upon used using usually want well went"
    " whether within without work yesterday tomorrow although because again"
    " already always another around during either enough finally further"
    " generally indeed meanwhile moreover furthermore additionally nevertheless"
    " nonetheless notably importantly interestingly crucially ultimately"
    " essentially basically clearly obviously similarly likewise consequently"
    " accordingly hence besides regardless afterwards earlier recently currently"
    " previously eventually suddenly unfortunately fortunately honestly frankly"
    " simply actually really certainly absolutely several something sometimes"
    " whose whom whenever dear hello above below between across along among"
    " anyone everyone nobody someone nothing everything anything".split()
)
# Retyping a text tends to flatten these marks, which changes an author's style.
TYPOGRAPHY = {"curly quotes": "[“”‘’]", "em dashes": "—", "en dashes": "–"}
# An original sentence counts as carried over when half its content words survive.
SENTENCE_WORDS = 5
SENTENCE_COVERAGE = 0.5
# A quarter of the content words gone is a rewrite; look for dropped claims.
VOCABULARY_WORDS = 10
VOCABULARY_SHARE = 0.25


class Tokens(Counter):
    """Counts of normalised tokens that remember how each was first written."""

    def __init__(self) -> None:
        super().__init__()
        self.forms: dict[str, str] = {}

    def note(self, key: str, form: str | None = None) -> None:
        if key:
            self[key] += 1
            self.forms.setdefault(key, form if form is not None else key)


def flat(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def plain(value: str) -> str:
    """Words without the typography and emphasis around them."""
    return flat(re.sub(r"[*_`~]", "", value.translate(NORMALISE)))


def code_block(text: str) -> str:
    """A block of code as written, less the blank lines and trailing spaces around it."""
    return "\n".join(line.rstrip() for line in text.split("\n")).strip("\n")


def link(target: str) -> str:
    """A link target as compared: entities decoded, and an address without "mailto:"."""
    return html.unescape(target.strip().strip("<>")).removeprefix("mailto:")


def label(text: str) -> str:
    return flat(text).casefold()


def markdown_blocks(text: str) -> tuple[str, dict[str, str]]:
    """Mark the block-level literals of Markdown and collect its link definitions.

    Front matter and code blocks are marked as code and a block quotation as a
    quotation. Unlike the checker, nothing the reader sees is dropped: a quoted
    block, a nested bullet and a footnote all carry facts that an edit can change.
    """
    kept: list[str] = []
    targets: dict[str, str] = {}
    fence: tuple[str, int] | None = None
    literal: list[str] = []
    quoted = indented = listed = False
    blank = True

    def code(block: str) -> None:
        kept.extend(
            ["", BLOCK_OPEN + html.escape(block, quote=False) + BLOCK_CLOSE, ""]
        )

    def unquote() -> None:
        nonlocal quoted
        if quoted:
            kept[-1] += QUOTE_CLOSE
            quoted = False

    front = FRONT_MATTER.match(text)
    if front:
        code(front[0])
        text = text[front.end() :]
    for raw in text.split("\n"):
        marker = BLOCKQUOTE.match(raw)
        line = raw[marker.end() :] if marker else raw
        opener = FENCE.match(line)
        if fence:
            closes = opener and opener[1][0] == fence[0] and len(opener[1]) >= fence[1]
            if closes and not line.strip().strip("`~"):
                code("\n".join(literal))
                fence, literal = None, []
            else:
                literal.append(line)
        elif indented and (not line.strip() or INDENTED.match(line)):
            literal.append(line)
        elif not line.strip():
            unquote()
            kept.append("")
            blank = True
        else:
            if indented:
                # Without its indent, the block equals the same code in a fence.
                code("\n".join(INDENTED.sub("", line, count=1) for line in literal))
                indented, literal = False, []
            if opener:
                unquote()
                fence = (opener[1][0], len(opener[1]))
            # Four spaces after a blank line are code, except under a list
            # item, where they are the item going on.
            elif blank and not listed and INDENTED.match(line):
                indented = True
                literal.append(line)
            else:
                if block_kind(line) == "item":
                    listed = True
                elif not INDENTED.match(line):
                    listed = False
                definition = DEFINITION.fullmatch(line)
                if definition and label(definition[1]):
                    targets.setdefault(label(definition[1]), definition[2])
                    line = definition[3] or ""
                elif marker and not quoted:
                    # Later lines belong to the quotation until a blank one,
                    # with or without a marker of their own.
                    line, quoted = QUOTE_OPEN + line, True
                kept.append(line)
                blank = False
    if fence:
        # An unclosed fence runs to the end of the document.
        code("\n".join(literal))
    elif indented:
        code("\n".join(INDENTED.sub("", line, count=1) for line in literal))
    unquote()
    return "\n".join(kept), targets


def spans(text: str, markdown: bool, targets: dict[str, str]) -> str:
    """Mark the inline literals: code spans and the targets of links."""

    def span(match: re.Match) -> str:
        if match[2] is None:
            return match[0]
        # The HTML pass that follows must read code as it is written.
        inner = html.escape(match[2], quote=False) if markdown else match[2]
        return CODE_OPEN + inner + CODE_CLOSE

    def reference(match: re.Match) -> str:
        target = match[1] and targets.get(label(match[2] or match[1]))
        if not target:
            return match[0]
        return f"[{match[1]}]{LINK_OPEN}{target}{LINK_CLOSE}"

    def destination(match: re.Match) -> str:
        inner = LINK.fullmatch(match[1][2:-1]) if match[1] else None
        if not inner:
            # Code, or a bracket and a parenthesis: "[B](page 12, revised 5 May)".
            return match[0]
        target = inner[1] or ""
        shown = match.string[max(0, match.start() - 500) : match.start()]
        # "[a@b.example](mailto:a@b.example)" names its address once.
        if link(target) == link(shown.rpartition("[")[2].translate(PRIVATE)):
            target = ""
        return f"] {LINK_OPEN}{target}{LINK_CLOSE}{inner[2] or ''} "

    text = INLINE_CODE.sub(span, text)
    if targets:
        text = REFERENCE.sub(reference, text)
    return LINK_DESTINATION.sub(destination, text)


class Page(Elements):
    """Read HTML as its reader does, marking the literals a comparison protects.

    Scripts, styles and concealed elements are left out. Markdown goes through
    here too, for the tags, comments and entities it may carry.
    """

    UNSEEN = {"script", "style", "template"}
    UNLINKED = {"link", "script", "base"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chars: list[str] = []
        self.finished = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.imply_end(tag)
        values = dict(attrs)
        unseen = tag in self.UNSEEN or concealed(values)
        if tag in self.BLOCK or tag == "title":
            self.chars.append("\n")
        if unseen and tag in self.VOID:
            return
        # What an unseen element holds is cut where the element ends, and its
        # own text and target with it.
        start = len(self.chars)
        if values.get("alt"):
            self.chars.append(f" {values['alt']} ")
        target = values.get("href") or values.get("src") or ""
        if tag in self.UNLINKED:
            target = ""
        # A link is marked where it ends, once its own text is known.
        if target and tag != "a":
            self.chars.append(LINK_OPEN + target + LINK_CLOSE)
        if tag in self.VOID:
            return
        if unseen:
            role = "unseen"
        elif tag in ("code", "pre") and self.nearest({"code", "pre"}) < 0:
            role = tag
        elif tag in ("blockquote", "q"):
            role = "quote"
            self.chars.append(QUOTE_OPEN)
        else:
            role = "link" if tag == "a" and target else ""
        self.enter(tag, (role, start if unseen else len(self.chars), target))

    def leave(self, tag: str, state: object) -> None:
        role, mark, target = state
        if role == "unseen":
            # One that never ends is read; see ProseHTML.
            if not self.finished:
                del self.chars[mark:]
        elif role in ("code", "pre"):
            inner = "".join(self.chars[mark:])
            targets = LINK_TARGET.findall(inner)
            marks = (CODE_OPEN, CODE_CLOSE) if role == "code" else (BLOCK_OPEN, BLOCK_CLOSE)
            literal = LINK_TARGET.sub("", inner).translate(PRIVATE)
            self.chars[mark:] = [
                marks[0],
                literal,
                marks[1],
                *(LINK_OPEN + found + LINK_CLOSE for found in targets),
            ]
        elif role == "quote":
            self.chars.append(QUOTE_CLOSE)
        elif role == "link":
            shown = "".join(self.chars[mark:]).translate(PRIVATE)
            if link(target) != link(flat(shown)):
                self.chars.append(LINK_OPEN + target + LINK_CLOSE)
        if tag in self.BLOCK or tag == "title":
            self.chars.append("\n")

    def handle_data(self, data: str) -> None:
        self.chars.append(data)

    def text(self) -> str:
        """Everything read; call once, after the last feed."""
        self.close()
        self.finished = True
        self.end(0)
        return "".join(self.chars).replace(LITERAL_LESS_THAN, "<")


def number(match: re.Match) -> str:
    """One spelling for forms that say the same: 1,900 and 1900, 09:30 and 9:30,
    5 ms and 5ms, 5 per cent and 5%, 14th and 14, twenty-one and 21."""
    if match["word"]:
        words = re.split("[- ]", match["word"].casefold())
        if words[0] not in WORD_VALUES:
            return words[0]
        return str(sum(WORD_VALUES[word] for word in words))
    figure = match["figure"].replace(",", "")
    if figure.startswith("."):
        figure = "0" + figure
    # 09:30 and 9:30 are the same time; a leading zero is formatting.
    figure = re.sub(r"^0+(?=\d)", "", figure)
    suffix = re.sub(r"[ .]", "", (match["suffix"] or "").casefold())
    sign = "-" if match["sign"] in ("-", "−") else ""
    currency = (match["currency"] or "").casefold()
    return sign + currency + figure + SUFFIXES.get(suffix, suffix)


def unnumbered(line: str) -> str:
    """Swap the marker of a numbered list item for a bullet: it is layout, not a figure."""
    marker = ORDERED.match(line)
    if not marker:
        return line
    digits = marker.end(1) - marker.start(1)
    return line[: marker.start(1)] + "-" + " " * digits + line[marker.end(1) + 1 :]


def beside(words: list[str], target: str) -> set[str]:
    """The words on either side of each use of a word, as "left|" and "|right"."""
    found = set()
    for index, word in enumerate(words):
        if word == target:
            if index:
                found.add(stem(words[index - 1]) + "|")
            if index + 1 < len(words):
                found.add("|" + stem(words[index + 1]))
    return found


def names(structure: list, flowed: str) -> tuple[set[str], set[str]]:
    """Words that look like names or identifiers, and every word seen."""
    sentences = [
        (block.kind, NAME.findall(flowed[sentence.start : sentence.end]))
        for block in structure
        for sentence in block.sentences
    ]
    words = [re.sub(r"'s$", "", token) for _, tokens in sentences for token in tokens]
    seen = {word.casefold() for word in words}
    lower = {word for word in words if word[0].islower()}
    marked: set[str] = set()
    for kind, tokens in sentences:
        if kind == "heading":
            continue
        for index, token in enumerate(tokens):
            word = re.sub(r"'s$", "", token)
            if re.fullmatch(r"I(?:'\w+)?", word):
                continue
            shaped = bool(re.search(r"[a-z][A-Z]|_|\d", word)) or (
                len(word) > 1 and word.isupper()
            )
            if index:
                capitalised = word[0].isupper()
            else:
                folded = word.casefold()
                capitalised = (
                    word[0].isupper()
                    and len(word) > 2
                    and folded not in SENTENCE_OPENERS
                    and folded not in lower
                )
            if shaped or capitalised:
                marked.add(word)
    return marked, seen


def content(text: str) -> set[str]:
    return {
        stem(word)
        for word in CONTENT_WORD.findall(text.casefold())
        if word not in FUNCTION_WORDS
    }


def tokens(source: str, format: str, keep_code: bool = False) -> dict:
    # Line endings and trailing spaces are not content; nor are the marks used here.
    text = NEWLINE.sub("\n", source).translate(PRIVATE)
    text = "\n".join(line.rstrip(" \t") for line in text.split("\n"))
    targets: dict[str, str] = {}
    if format == "markdown":
        text, targets = markdown_blocks(text)
    if format != "html":
        text = spans(text, format == "markdown", targets)
    if format != "text":
        page = Page()
        page.feed(literal_markup(text, format == "markdown"))
        text = page.text()
    if format == "markdown":
        text = re.sub(
            f"{MARKED_CODE}|{ESCAPED}", lambda match: match[1] or match[0], text
        )

    code, links, quotes = Tokens(), Tokens(), Tokens()

    def block(match: re.Match) -> str:
        code.note(code_block(match[1]))
        # A brief may give a fact in a code block; the draft may state it in prose.
        return f"\n{match[1]}\n" if keep_code else "\n"

    def target(match: re.Match) -> str:
        links.note(link(match[1]))
        return " "

    text = LINK_TARGET.sub(target, CODE_BLOCK.sub(block, text))
    for match in CODE_SPAN.finditer(text):
        code.note(flat(match[1]))
    # A quotation keeps the code inside it, and may wrap across lines; a blank
    # line always ends it.
    quoting = text.translate(CODE_MARKS)
    joined = re.sub(r"(?<!\n)\n(?!\n)", " ", HYPHEN_BREAK.sub("", quoting))
    joined = joined.translate(NORMALISE)
    for pattern in QUOTATIONS:
        for match in pattern.finditer(joined):
            for paragraph in re.split(r"\n\s*\n", match[1]):
                words = plain(paragraph).strip(" .,;:!?")
                if len(words.split()) >= 2:
                    quotes.note(words.casefold(), words)
    prose = (quoting if keep_code else CODE_SPAN.sub(" ", text)).translate(PRIVATE)
    for match in URL.finditer(prose):
        links.note(link(match[0].rstrip(".,;:!?)*_~>]'\"")))
    prose = re.sub(r"(?<=\S)[ \t]{2,}", " ", URL.sub(" ", prose).translate(NORMALISE))
    lines = prose.split("\n")
    prose = "\n".join(
        unnumbered(line) if kind == "item" else line
        for line, kind in zip(lines, line_kinds(lines))
    )
    # Unlike the checker, read a wrapped line as its paragraph going on in every
    # format: a figure and its unit may sit either side of the break.
    flowed = flow(prose, "markdown", "prose")
    pieces, kept = [], 0
    for match in HYPHEN_BREAK.finditer(prose):
        # Where the lines were joined, the word is whole again.
        if flowed[match.start()] == " ":
            pieces.append(flowed[kept : match.start()])
            kept = match.end()
    flowed = "".join(pieces) + flowed[kept:]
    structure = blocks(flowed)
    # A month or weekday is compared as a date, so it is neither a name nor "may".
    undated = DATE.sub(lambda match: " " * len(match[0]), flowed)
    marked, seen = names(structure, undated)
    numbers, dates = Tokens(), Tokens()
    for match in NUMBER.finditer(flowed):
        numbers.note(number(match), match[0])
    for match in DATE.finditer(flowed):
        dates.note(match[0][:3].casefold(), match[0])
    spoken = re.findall(r"[a-z0-9]+", flowed.casefold())
    typography = {
        mark: len(re.findall(marks, source)) for mark, marks in TYPOGRAPHY.items()
    }
    return {
        "words": len(prose.split()),
        "numbers": numbers,
        "ones": beside(spoken, "one"),
        "singles": beside(spoken, "1"),
        "dates": dates,
        "links": links,
        "code": code,
        "quotes": quotes,
        "plain": plain(joined.translate(PRIVATE)).casefold(),
        "names": marked,
        "seen": seen,
        "content": content(flowed),
        "typography": Counter(typography),
        "sentences": [
            flowed[sentence.start : sentence.end]
            for block in structure
            if block.kind in ("paragraph", "item")
            for sentence in block.sentences
        ],
        "negation": Counter(
            re.sub(r"[^\w']+", " ", match[0]).strip().casefold()
            for match in NEGATION.finditer(flowed)
        ),
        "modality": Counter(
            match[0].casefold() for match in MODALITY.finditer(undated)
        ),
        "headings": Counter(
            re.sub(r"^[#\s]+|[#\s]+$", "", flowed[block.start : block.end]).casefold()
            for block in structure
            if block.kind == "heading"
        ),
    }


def compare(
    original: str,
    revised: str,
    original_format: str = "text",
    revised_format: str = "text",
    brief: bool = False,
) -> dict:
    """List what the revision dropped or added. With `brief`, the original is a
    set of supplied facts, so only additions count."""
    # A brief may give a fact in backticks; the draft is free to state it in prose.
    before = tokens(original, original_format, keep_code=brief)
    after = tokens(revised, revised_format)
    differences = []

    def record(kind: str, dropped: list[str], added: list[str], note: str = "") -> None:
        dropped = [] if brief else dropped
        if dropped or added or note:
            differences.append(
                {
                    "kind": kind,
                    "severity": "error" if kind in BLOCKING else "review",
                    "dropped": dropped,
                    "added": added,
                    "note": note,
                }
            )

    def shifts(old: Counter, new: Counter, keys: set[str]) -> list[str]:
        return [
            f"{getattr(old, 'forms', {}).get(key, key)} {old[key]} to {new[key]}"
            for key in sorted(keys)
            if old[key] != new[key]
        ]

    def supplied(key: str) -> bool:
        words = re.escape(plain(key).casefold())
        return bool(words and re.search(rf"(?<!\w){words}(?!\w)", before["plain"]))

    mentions: list[str] = []
    for kind in BLOCKING:
        old, new = before[kind], after[kind]
        dropped, added = old.keys() - new.keys(), new.keys() - old.keys()
        note = ""
        if kind == "numbers":
            # "1 server" and "one server" say the same thing; "no one" says
            # nothing about a 1 that went missing elsewhere.
            if before["singles"] & after["ones"]:
                dropped.discard("1")
            if after["singles"] & before["ones"]:
                added.discard("1")
        elif brief and kind in ("code", "quotes"):
            # The brief's own words are supplied, however the draft sets them.
            added = {key for key in added if not supplied(key)}
        elif kind == "code" and {flat(key) for key in dropped} & {
            flat(key) for key in added
        }:
            note = "spacing or line breaks changed inside a code block"
        record(
            kind,
            sorted(old.forms[key] for key in dropped),
            sorted(new.forms[key] for key in added),
            note,
        )
        mentions += shifts(old, new, old.keys() & new.keys())
    record(
        "names",
        sorted(
            name for name in before["names"] if name.casefold() not in after["seen"]
        ),
        sorted(
            name for name in after["names"] if name.casefold() not in before["seen"]
        ),
    )
    if not brief:
        # A fact stated twice and now once is still stated; show it for a look.
        record("mentions", [], [], ", ".join(mentions))
        record(
            "negation",
            sorted((before["negation"] - after["negation"]).elements()),
            sorted((after["negation"] - before["negation"]).elements()),
        )
        modality = before["modality"].keys() | after["modality"].keys()
        record(
            "modality",
            [],
            [],
            ", ".join(shifts(before["modality"], after["modality"], modality)),
        )
        record(
            "headings",
            sorted((before["headings"] - after["headings"]).elements()),
            sorted((after["headings"] - before["headings"]).elements()),
        )
        marks = before["typography"].keys()
        record(
            "typography",
            [],
            [],
            ", ".join(shifts(before["typography"], after["typography"], marks)),
        )
        unmatched = []
        for sentence in before["sentences"]:
            stems = content(sentence)
            kept = len(stems & after["content"]) / max(len(stems), 1)
            if len(stems) >= SENTENCE_WORDS and kept < SENTENCE_COVERAGE:
                unmatched.append(flat(sentence))
        record("sentences", unmatched, [])
        gone = before["content"] - after["content"]
        share = len(gone) / max(len(before["content"]), 1)
        if len(gone) >= VOCABULARY_WORDS and share > VOCABULARY_SHARE:
            record(
                "vocabulary",
                [],
                [],
                f"{len(gone)} of {len(before['content'])} content words no longer appear ({share:.0%})",
            )
        ratio = after["words"] / max(before["words"], 1)
        if before["words"] and (ratio < 0.6 or ratio > 1.25):
            record(
                "length",
                [],
                [],
                f"{before['words']} to {after['words']} words ({ratio:.0%} of the original)",
            )
    blocking = [item for item in differences if item["severity"] == "error"]
    return {
        "passed": not blocking,
        "blocking": len(blocking),
        "review": len(differences) - len(blocking),
        "brief": brief,
        "words": {"original": before["words"], "revised": after["words"]},
        "differences": differences,
    }


def excerpt(value: str, counterparts: list[str]) -> str:
    """Sixty characters of a token, from near where it departs from the token it
    most resembles on the other side. `counterparts` is sorted."""
    text = flat(value)
    if len(text) <= 60:
        return text
    # In sorted order, the token sharing the longest opening is a neighbour.
    at = bisect.bisect_left(counterparts, text)
    shared = 0
    for near in counterparts[max(at - 1, 0) : at + 1]:
        same = next(
            (index for index, pair in enumerate(zip(text, near)) if pair[0] != pair[1]),
            min(len(text), len(near)),
        )
        shared = max(shared, same)
    start = max(0, min(shared - 20, len(text) - 57))
    cut = text[start : start + 57]
    return ("..." if start else "") + cut + ("..." if start + 57 < len(text) else "")


def report(result: dict, stream=None) -> None:
    stream = stream or sys.stdout
    label = "against the brief" if result["brief"] else "against the original"
    state = (
        "check before use"
        if result["blocking"]
        else "no protected token changed"
        if result["passed"]
        else "review before use"
    )
    print(
        f"{result.get('revised', '<revised>')} {label}: {state}"
        f"; {result['blocking']} blocking, {result['review']} to review",
        file=stream,
    )
    for item in result["differences"]:
        parts = []
        for side, other in (("dropped", "added"), ("added", "dropped")):
            counterparts = sorted(flat(value) for value in item[other])
            shown = [excerpt(value, counterparts) for value in item[side]]
            if shown:
                parts.append(f"{side}: {', '.join(shown)}")
        if item["note"]:
            parts.append(item["note"])
        print(f"  {item['kind']:9} {item['severity']}: {'; '.join(parts)}", file=stream)
    print(
        "  Token comparison only. It cannot show that the meaning survived; read both versions.",
        file=stream,
    )


def read(path: str) -> str:
    text = (
        sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8-sig")
    )
    return text.removeprefix("﻿")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("original", help="UTF-8 source or brief, or - for stdin")
    parser.add_argument("revised", help="UTF-8 revision or draft, or - for stdin")
    parser.add_argument(
        "--brief",
        action="store_true",
        help="Treat the first file as supplied facts and report only what the draft adds",
    )
    parser.add_argument(
        "--format",
        choices=("auto", "text", "markdown", "html"),
        default="auto",
        help="Applies to both files; auto infers each from its extension",
    )
    parser.add_argument("--json", action="store_true", help="Machine-readable report")
    parser.add_argument(
        "--strict", action="store_true", help="Also fail for differences to review"
    )
    args = parser.parse_args(argv)
    try:
        if args.original == args.revised == "-":
            raise ValueError("stdin can only be read once")
        result = {
            "original": args.original,
            "revised": args.revised,
            **compare(
                read(args.original),
                read(args.revised),
                infer_format(args.original, args.format),
                infer_format(args.revised, args.format),
                args.brief,
            ),
        }
    except (OSError, UnicodeError, ValueError) as error:
        if args.json:
            print(
                json.dumps(
                    {"schema_version": 1, "passed": False, "error": str(error)},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"hooman: {error}", file=sys.stderr)
        return 2
    # Under --strict a difference to review fails the comparison.
    result["passed"] = result["passed"] and not (args.strict and result["review"])
    if args.json:
        print(json.dumps({"schema_version": 1, **result}, ensure_ascii=False, indent=2))
    else:
        report(result)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="strict")
    for output in (sys.stdout, sys.stderr):
        if hasattr(output, "reconfigure"):
            output.reconfigure(errors="replace")
    raise SystemExit(main())
