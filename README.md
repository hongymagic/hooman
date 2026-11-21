# Hooman

Hooman is an agent skill for writing, editing and reviewing English prose in a
plain style. It holds instructions for a language model, six reference files
and three Python scripts.

The skill is named `human-writing`. It has the model list the facts, take the
established form for the kind of document, and write one fact to a sentence
under headings that are labels. The standard is technical and business writing
from before language models. The thresholds are set against 703 human
documents: 600 from a published parallel corpus and 103 pinned to commits from
before November 2022, 38 of those from before 2020.

| Script | Function |
| --- | --- |
| `check.py` | Reports phrasing, headings and paragraphs that depart from the standard, by line and column |
| `compare.py` | Lists the numbers, dates, links, code, quotations and names an edit changed, or a draft added to its facts |
| `cleanse.py` | Sends a draft to a model of another family through a Codex or Claude CLI |

## Requirements

Python 3.12 or newer. The scripts have no third-party dependencies. `check.py`
and `compare.py` make no network calls. `cleanse.py` is optional and needs a
Codex or Claude CLI that is installed and signed in.

## Installation

Install the skill or the plugin on a host, not both.
[Releases](https://github.com/hongymagic/hooman/releases) hold versioned ZIPs
and checksums. To build the archives from a checkout:

```sh
python3 scripts/package.py
```

For version 2.0.0 this creates `dist/human-writing-2.0.0.zip`,
`dist/hooman-2.0.0-plugin.zip` and `dist/SHA256SUMS`.

### Codex

```sh
codex plugin marketplace add hongymagic/hooman
codex plugin add hooman@hooman
```

For a standalone skill, extract the skill ZIP into `~/.agents/skills/` or the
project's `.agents/skills/`, giving `.../skills/human-writing/SKILL.md`. Invoke
it as `$human-writing`. See the
[Codex skill documentation](https://learn.chatgpt.com/docs/build-skills).

### Claude Code

```sh
claude plugin marketplace add hongymagic/hooman
claude plugin install hooman@hooman
```

Invoke it as `/hooman:human-writing`. To load a checkout for one session:

```sh
claude --plugin-dir .
```

See the [Claude plugin documentation](https://code.claude.com/docs/en/plugins).

### ChatGPT and Claude

Where a workspace allows custom skill uploads, upload the standalone skill ZIP.
Upload and script execution depend on the host; see
[ChatGPT Skills](https://help.openai.com/en/articles/20001066) and
[Claude Skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
The plugin ZIP is a separate distribution with portable, Codex and Claude
manifests.

## Usage

### Skill

Name the skill and the job in a request:

- “Use human-writing to edit this draft. Keep my tone.”
- “Draft a status update from these facts.”
- “Review this ADR without rewriting it.”
- “Write the labels and empty states for this page.”

Supply the reader, the purpose and a writing sample where there is one. The
skill returns finished text. On request it returns copy only, or findings with
the document unchanged.

| File | Content |
| --- | --- |
| [SKILL.md](human-writing/SKILL.md) | The standard and the procedure |
| [forms.md](human-writing/references/forms.md) | Section labels for a README, a reference page, a memo, a report and nine other kinds of document |
| [exemplars.md](human-writing/references/exemplars.md) | Passages of human writing from 1863 to 2021, read before drafting |
| [patterns.md](human-writing/references/patterns.md) | Each checker finding, its fix and when to keep the passage |
| [fidelity.md](human-writing/references/fidelity.md) | The comparison and what it cannot see |
| [checker.md](human-writing/references/checker.md) | Rule IDs, thresholds, output and exit statuses |
| [second-pass.md](human-writing/references/second-pass.md) | The edit by a second model family |

### Checker

```sh
python3 human-writing/scripts/check.py --text "It is worth noting that the export runs."
```

```text
<text>: needs editing; 8 words; 1 blocking, 0 to review
  1:1 [staging.announcement] error: It is worth noting
    Cut the announcement and keep the information.
  English patterns only. A pass means no blocking pattern matched; it does not verify facts, quality or authorship.
```

The command exits 1. With the phrase removed it prints `pass` and exits 0.

A page with headings that pitch, shown without the advice line under each
finding and the closing line:

```text
page.md: needs editing; 22 words; 1 blocking, 5 to review
  3:1 [pitch.headings] error: 3 of 4 headings address or sell to the reader
  3:4 [pitch.heading] review: Try it with your team
  5:9 [pitch.benefit] review: helps you
  5:35 [pitch.benefit] review: with confidence
  7:4 [pitch.heading] review: Why Harbour
  9:4 [pitch.heading] review: Get a quote
```

Files, JSON output and interface strings:

```sh
python3 human-writing/scripts/check.py README.md docs/*.md
python3 human-writing/scripts/check.py README.md --json
python3 human-writing/scripts/check.py strings.txt --profile interface
```

An `error` finding fails the check. A `review` finding does not, unless
`--strict` is given. No single word is an error: empty phrases, chat leftovers
and accumulations are. The checker reads Markdown, HTML and plain text and
skips code and block quotations.

### Comparison

```sh
python3 human-writing/scripts/compare.py draft.md revised.md
```

```text
revised.md against the original: check before use; 1 blocking, 2 to review
  numbers   error: dropped: 1,900; added: 1,800
  names     review: dropped: Security
  modality  review: if 1 to 0, may 1 to 0, will 0 to 1
  Token comparison only. It cannot show that the meaning survived; read both versions.
```

The edit changed a figure, dropped the approver and turned a possibility into a
commitment. With `--brief`, the first file is a list of supplied facts and the
report shows what the draft added to it.

### Second-model edit

```sh
python3 human-writing/scripts/cleanse.py README.md --writer openai --output revised.md
```

`--writer` names the family that wrote the draft: `openai`, `anthropic`,
`google` or `other`. The helper sends an OpenAI draft to Claude, an Anthropic
draft to Codex and any other to the first installed CLI, Codex before Claude.
It refuses to send a draft to its own family. It validates the reply, checks it,
compares it with the source and writes a new file. It does not overwrite the
source or an existing output. Model calls are subject to the provider's data
handling and charges. `--prompt-only` prints the brief without calling a model.

## Limits

- Hooman is an editing aid. It does not detect who wrote a text, and it is not
  a tool for getting text past an AI detector or a disclosure rule.
- A pass means no blocking pattern matched. It does not verify a fact, measure
  quality or establish authorship.
- The rules are English only.
- The particulars count is a proxy: it sees digits, names, code, links and
  quotations, and it misses a definition written in lower case.
- The comparison works on tokens. It does not see a change of scope, cause or
  certainty that keeps the same words.
- The thresholds come from 703 human documents and 668 model documents. The
  [validation notes](docs/validation.md) give the rates and what the corpora
  do not cover.

## Evidence

The [evidence summary](docs/evidence.md) lists the studies and conventions the
design rests on. To repeat the measurements:

```sh
python3 scripts/calibrate.py fetch
python3 scripts/calibrate.py measure --rules
```

## Verification

```sh
python3 scripts/verify.py
```

The command runs the regression tests, checks this repository's prose with the
checker and validates both archives. CI runs it on Linux, macOS and Windows.
The tests make no model calls and no network calls.
[docs/releases.md](docs/releases.md) covers releases.

## Credits

The 2.0 rule catalogue followed a study of three MIT-licensed skills:
[blader/humanizer](https://github.com/blader/humanizer),
[hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) and
[conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing).
No text was copied from them.

The catalogue also draws on Wikipedia's
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
[tropes.fyi](https://tropes.fyi/directory), [sloptells](https://sloptells.com/)
and Simon Willison's
[LLM cliché highlighter](https://tools.simonwillison.net/llm-cliche-highlighter).
Calibration uses the
[HAP-E corpus](https://huggingface.co/datasets/browndw/human-ai-parallel-corpus)
by Reinhart and colleagues. The exemplars are credited in
[exemplars.md](human-writing/references/exemplars.md).

## Licence

[MIT](LICENSE).
