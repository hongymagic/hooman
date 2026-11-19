# Running and interpreting the checker

Python 3.12 or newer is supported. The checker has no third-party dependencies,
makes no network calls and never writes to the files it reads. Commands below
run from the skill directory; use absolute script paths from elsewhere.

```sh
python3 scripts/check.py --text "The import accepts compressed files."
python3 scripts/check.py README.md
python3 scripts/check.py README.md --json
python3 scripts/check.py strings.txt --profile interface
```

Pass several file paths to check a set. Use `-` for stdin and `--format markdown`
or `--format html` for pasted documents. Extensions select Markdown for `.md`,
`.markdown` and `.mdown`, HTML for `.html` and `.htm`, and plain text otherwise.
An explicit `--format` overrides that choice. UTF-8 files may include a BOM.

## What a result means

The summary line reads `pass` or `needs editing`, followed by the word count and
the number of blocking and advisory findings. Under `--strict` it reads `needs
review` when only advisory findings remain. There is no score. A count out of
five invited the reading that five meant good, and the checker cannot know that.

| Finding | Meaning | Default gate |
| --- | --- | --- |
| `error` | An empty phrase, a chat leftover or an accumulation | Fails |
| `review` | Context decides: a stock word, a contrast, a formatting habit | Does not fail |
| Finding with an allowance | The caller gave a reason to keep this rule's matches | Does not fail |

A pass means no blocking pattern matched. It says nothing about factual truth,
writing quality or who wrote the text. No single word blocks; words date within
a model generation and people use all of them.

The thresholds were set against dated text. In November 2026 the blocking rules
failed 1.5 to 5 per cent of 600 human-written documents from a published
parallel corpus, and 61.5 to 98 per cent of a 2024 model's continuations of the
same documents. They failed 17 per cent of 65 longer technical and business
documents written before November 2022. Most human failures were filler such as
`it should be noted` and `let's dive into`, which people also write. The
[validation notes](https://github.com/hongymagic/hooman/blob/main/docs/validation.md)
give the corpora, the per-rule rates and the limits of the measurement.

`--strict` also fails on unresolved review findings. In CI, read `passed` and
the exit status. An allowance applies to every match of one rule for the
current invocation:

```sh
python3 scripts/check.py notes.md --allow "staging.announcement=Quoted from the 2019 changelog"
```

Allowances stay visible beside their reasons. Unknown IDs and blank reasons are
errors. Scope an allowance to the document that needs it, and do not exempt a
rule to silence an inconvenient finding.

The rules are English only and the checker does not detect language. Requests
for another `--language` fail; they never return a pass.

## Rule catalogue

[patterns.md](patterns.md) explains each family, its fix and when to keep the
pattern. Severity is the default; a rule ID can carry both when some phrasings
are emptier than others.

| ID | Severity | What it matches |
| --- | --- | --- |
| `staging.scene` | error | Stock scene-setting openers |
| `staging.announcement` | error | A phrase announcing that a point or a piece of news is coming |
| `staging.runup` | error, review | Run-ups before the point; catch-all openers are advisory |
| `staging.reveal` | error, review | A question or label that stages a payoff |
| `staging.concession` | error, review | A concession to an objection nobody raised |
| `staging.strawman` | review | An invented opponent or lagging crowd |
| `staging.depth` | review | Sayings that pose as hidden truths |
| `staging.signpost` | review | Labels telling the reader a fact is important |
| `staging.closer` | error, review | Uplift and summary endings |
| `staging.contrast` | review | One contrast frame |
| `staging.contrasts` | error | Three or more frames at four or more per 1,000 words |
| `rhythm.negation` | error | Three negatives in a row |
| `rhythm.repeat` | error | An adjacent sentence repeated word for word |
| `rhythm.fragments` | review | Three consecutive sentences of four words or fewer |
| `rhythm.closers` | review | Three or more paragraphs, and at least a quarter, ending on five words or fewer |
| `rhythm.questions` | review | Three consecutive questions |
| `rhythm.dashes` | review | Three em dashes in one sentence |
| `rhythm.uniform` | review | Twelve or more sentences with length variation under 0.30 |
| `inflation.significance` | error, review | Stock importance claims; conventional academic phrasings are advisory |
| `inflation.promotion` | review | Sales words |
| `inflation.vocabulary` | review | Stock words |
| `inflation.cluster` | error | Four distinct stock or overused words within 100 words |
| `inflation.intensifier` | review | Emphasis and sincerity words |
| `inflation.copula` | review | Inflated substitutes for is and has |
| `inflation.tail` | review | A trailing `-ing` clause that glosses the sentence |
| `inflation.tails` | error | Three or more trailing clauses at three or more per 1,000 words |
| `inflation.hedge` | review | Stacked qualifiers |
| `formatting.labels` | review | Bold labels opening at least three list items and half the list |
| `formatting.bold` | review | Eight or more bold spans at 15 or more per 1,000 words |
| `formatting.titlecase` | review | Two or more title-case subheadings |
| `formatting.headline` | review | Two or more subheadings that open like a story |
| `formatting.rules` | review | Three or more horizontal rules |
| `formatting.hashtags` | review | A run of four or more hashtags |
| `formatting.emoji` | review | Emoji in headings or list items |
| `leftovers.chat` | error | An assistant's greeting, praise or offer |
| `leftovers.courtesy` | review | Sign-offs that may be residue or ordinary courtesy |
| `leftovers.cutoff` | error | Statements about what a model knows or was given |
| `leftovers.markup` | error | Citation tokens and tracking parameters from chat tools |
| `leftovers.placeholder` | error | An unfilled slot or unresolved evidence marker |
| `leftovers.reasoning` | error | Reasoning scaffolds |
| `leftovers.meta` | review | Sentences about the document or the edit |
| `evidence.numbers` | review | Figures to verify |
| `evidence.attribution` | review | Unnamed experts and studies |
| `density.signals` | error | Six or more advisory findings at ten or more per 1,000 words |
| `interface.figure` | review | A figure of speech in an interface string |
| `interface.filler` | review | Filler words in an interface string |
| `interface.heading` | review | A label phrased as a clause or a two-word question |
| `interface.shorthand` | review | A string ending on a bare number |
| `interface.pair` | review | Two clipped sentences in one string |

Formatting rules apply to Markdown and plain text. HTML carries its formatting
in tags the checker removes. Formatting findings never block and never count
towards `density.signals`: whether a bold label is decoration or structure
depends on the document, which the checker cannot see. Evidence findings do not
count either, and an allowed finding stops counting too.

When `inflation.tails` fires, every trailing clause is listed as an
`inflation.tail` finding so you can see them. Below the threshold only the
glossing verbs are reported, because an occasional participle clause is
ordinary English.

## Interface profile

`--profile interface` reads one string per line. It applies the `interface`
rules and the leftover rules that suit short strings, and skips every rule that
needs sentences or paragraphs. Nothing in the `interface` family blocks. Short
labels fall below what pattern rules can see: the profile catches a few common
frames and cannot tell a good label from a poor one. Compare the strings with
the product's existing screens, as [registers.md](registers.md) describes.

## Extraction boundaries

Markdown extraction omits fenced and indented code, inline code, blockquotes,
struck text, initial YAML frontmatter, comments, link destinations and reference
definitions. Link labels and footnote definitions remain prose. Inline quotation
marks do not suppress checking. Put deliberate specimens in code or blockquotes
when writing a guide; do not reformat publication copy to conceal a finding.

Frontmatter is recognised when the first line after the opening `---` that is
neither blank nor a comment is a key. A document that opens with a horizontal
rule, or with a rule and a heading, is read as prose. A line is a reference
definition only when it holds a label, a target and at most a title, so
`[Editor]: a sentence of prose` is checked. A chat tool's tracking parameter is
the one thing still read inside a link destination, a reference definition, an
autolink or an HTML attribute.

In Markdown a `<` is markup only where it opens a whole tag, comment or
declaration, as CommonMark reads it: the attributes must parse and the tag must
close before a blank line. Any other `<`, as in `n<k`, is text, and so is one
after a backslash. An element that hides its content hides it as far as its end
tag. One that never ends is read as prose, so a tag named in passing, such as
`<pre>` in a sentence, cannot hide the rest of the document. An unfinished
comment is read the same way.

A bracketed placeholder followed by a link target or a reference label is a
link's text and passes. Two placeholders side by side are both reported.

Files, stdin and `--text` are read alike: CRLF and CR count as line breaks. A
finding that depends on opening a sentence points at its first word, after any
list marker, quotation mark or emphasis.

A single line break inside a Markdown paragraph is treated as a space, so a
pattern split across wrapped lines is still found. Plain text is treated the
same way only when it looks hard-wrapped; otherwise each line is a paragraph.

The Markdown reader handles these common forms; it is not a complete CommonMark
or MDX renderer. Lazy blockquote continuations and complex nested Markdown can
need manual review. A four-space indented prose line is treated as code.

HTML extraction excludes head content, scripts, styles, templates, code, SVG,
noscript and subtrees marked `hidden`, `aria-hidden="true"`, inline `display:none`
or inline `visibility:hidden`. End tags that HTML lets an author leave out are
supplied: a new `<li>` ends the item before it, and `<body>` ends an unclosed
`<head>`. Inline tags retain adjoining text, block boundaries
separate it, and HTML entities are decoded. Source line and column point back to
the original file, including decoded entities. Attributes are not prose, apart
from that tracking parameter.
The checker does not run JavaScript, load CSS, evaluate classes or determine which
responsive view is visible. Review a rendered page when those affect its copy.

## Automation contract

Exit 0 means the selected gate passed; exit 1 means unresolved findings failed the
gate; exit 2 means invalid input or an I/O error. Empty extracted prose is an error.
If one file cannot be read, the command reports results for the other files and
exits 2. A failure is never reported as a clean document.

`--json` emits one object with `schema_version: 2`, `passed`, `results` and
`errors`. Each result contains the path, format, language, profile, word count,
`passed`, the `blocking` and `review` counts, `stats` and `findings`. Under
`--strict` each result's `passed` is false while review findings remain. `stats`
holds the sentence count, mean sentence length, length variation and em dashes
per 1,000 words. Each finding contains a rule ID, category, severity, source
line and column, matched text or a count, advice and an optional allowance.
Input errors stay in the JSON report. Argument syntax errors use argparse's
normal stderr output and exit 2.
