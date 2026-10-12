# Running and interpreting the checker

Python 3.12 or newer is supported. The checker has no third-party dependencies,
makes no network calls and never writes to the files it reads. Commands below
run from the skill directory; use absolute script paths from elsewhere.

```sh
python3 scripts/check.py --text "The import accepts compressed files."
python3 scripts/check.py README.md
python3 scripts/check.py README.md --json
```

Pass multiple file paths to check a set. Use `-` for stdin and `--format markdown`
or `--format html` for pasted documents. Extensions select Markdown for `.md`,
`.markdown`, `.mdown`, HTML for `.html`, `.htm`, and plain text otherwise. An
explicit `--format` overrides that choice. UTF-8 files may include a BOM.

## What a score means

There are five categories: wording, framing, repetition, cadence and evidence.
Each category with an unresolved `error` finding subtracts one point. Repeating
a defect adds findings but does not subtract additional category points.
A score of 5/5 means no blocking patterns matched. It says nothing about factual
truth, overall writing quality or who wrote the text. The rules are English only;
the checker does not detect language. Use it for English and select `--language`
explicitly when integrating a multilingual pipeline. Requests for other languages
fail rather than returning a passing score.

| Finding | Meaning | Default gate |
| --- | --- | --- |
| `error` | A likely editing defect, such as empty framing or a repeated sentence | Fails |
| `review` | Context matters, such as a technical term, useful contrast or numeric claim | Does not fail |
| Finding with an allowance | The caller supplied a reason to retain this rule's matches | Does not fail |

`--strict` also fails for unresolved review findings, without changing the numeric
score. Check `passed` and exit status, rather than the score alone, in CI.
An allowance applies to all matches of that rule for the current invocation:

```sh
python3 scripts/check.py --text "Delve is the command's documented name." --allow "word.delving=Literal command name required by the documentation"
```

Allowances remain visible alongside their reasons. Unknown IDs and blank reasons
are errors. Scope invocations narrowly when a rule is necessary in one document.
Do not exempt a rule just to silence an inconvenient finding.

## Rule catalogue

| IDs | What to inspect |
| --- | --- |
| `word.delving`, `word.hype` | Inflated vocabulary that delays an explanation |
| `word.promotion`, `word.stature` | Promotional wording; literal or technical uses can be appropriate |
| `frame.scene`, `frame.announcement`, `frame.suspense` | Openings that postpone useful information |
| `frame.contrast`, `frame.hedges` | Empty slogans and redundant uncertainty; preserve real distinctions |
| `repeat.synonyms`, `repeat.sentence` | Padded expressions and adjacent duplicate sentences |
| `cadence.triad`, `cadence.dashes` | Decorative adjective triples and repeated interruptions |
| `evidence.numbers`, `evidence.placeholder` | Checkable claims and explicitly unresolved proof |

## Extraction boundaries

Markdown extraction omits fenced and indented code, inline code, blockquotes,
struck text, initial YAML frontmatter, comments, link destinations and reference
definitions. Link labels remain prose. Inline quotation marks do not suppress
checking. Put deliberate specimens in code or blockquotes when authoring a guide;
do not reformat publication copy to conceal a finding.

The Markdown reader handles these common forms; it is not a complete CommonMark
or MDX renderer. Lazy blockquote continuations and complex nested Markdown can
need manual review. A four-space indented prose line is treated as code.

HTML extraction excludes head content, scripts, styles, templates, code, SVG,
noscript and subtrees marked `hidden`, `aria-hidden="true"`, inline `display:none`
or inline `visibility:hidden`. Inline tags retain adjoining text, block boundaries
separate it, and HTML entities are decoded. Source line and column point back to
the original file, including decoded entities. Attributes are not prose.
The checker does not run JavaScript, load CSS, evaluate classes or determine which
responsive view is visible. Review a rendered page when those affect its copy.

## Automation contract

Exit 0 means the selected gate passed; exit 1 means unresolved findings failed the
gate; exit 2 means invalid input or an I/O error. Empty extracted prose is an error.
If one file cannot be read, the command reports results for the other files and
exits 2. A failure is never reported as a clean document.

`--json` emits one object with `schema_version: 1`, `passed`, `results` and `errors`.
Each result contains path, format, language, word count, score, maximum and
findings. Each finding contains a rule ID, category, severity, source line/column,
matched text, advice and an optional allowance. Input errors stay in the JSON
report. Argument syntax errors use argparse's normal stderr output and exit 2.
