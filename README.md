# Hooman

Hooman helps you turn a draft into writing you can use. It finds the habits that
make prose read as machine-made, edits the passages that have them, and checks
that the edit kept your facts.

Use it for emails, READMEs, technical decisions, updates, articles, product copy
and interface copy. English defaults to Australian spelling unless your brief or
draft sets another convention.

The `human-writing` skill holds the workflow and five references. Two local
scripts support it: a checker with line-level findings, and a comparison that
lists the numbers, dates, links, code, quotations and names an edit changed. A
third helper can send a draft to a different model family through an installed
Codex or Claude CLI. The scripts need Python 3.12 or newer and have no
third-party dependencies. The checker and the comparison make no network calls.

Hooman is an editing aid. It does not detect who wrote a text, and it is not a
tool for getting text past an AI detector or a disclosure rule.

## Try the checker

From a checkout:

```sh
python3 human-writing/scripts/check.py --text "It is worth noting that the export runs."
```

```text
<text>: needs editing; 8 words; 1 blocking, 0 to review
  1:1 [staging.announcement] error: It is worth noting
    Cut the announcement and keep the information.
```

That exits 1. After editing:

```sh
python3 human-writing/scripts/check.py --text "The export runs."
```

```text
<text>: pass; 3 words; 0 blocking, 0 to review
```

A pass means no blocking pattern matched. It does not verify facts, measure
quality or establish authorship, which is why the checker reports counts and no
score.

Blocking findings are empty phrases, chat leftovers and accumulations. No single
word blocks: word habits change with every model generation, and people use all
of them. Three contrast frames in thirty words do block:

```text
contrast.txt: needs editing; 30 words; 1 blocking, 3 to review
  1:15 [staging.contrast] review: was not the pipelines. It was
  1:15 [staging.contrasts] error: 3 contrast frames in 30 words
  1:67 [staging.contrast] review: was not flaky. It was
  1:126 [staging.contrast] review: , not another comment.
```

Check files, request JSON, or check interface strings one per line:

```sh
python3 human-writing/scripts/check.py README.md docs/*.md
python3 human-writing/scripts/check.py README.md --json
python3 human-writing/scripts/check.py strings.txt --profile interface
```

Markdown extraction excludes code and blockquotes. HTML extraction reads static
prose and omits scripts, styles and hidden subtrees. `--strict` adds advisory
findings to the gate. The [checker reference](human-writing/references/checker.md)
lists every rule, its threshold and the exit statuses. Rules cover English only.

## Compare an edit with its source

Rewrites change facts more often than writers expect, so the second script lists
what moved:

```sh
python3 human-writing/scripts/compare.py draft.md revised.md
```

```text
revised.md against the original: check before use; 1 blocking, 2 to review
  numbers   error: dropped: 1,900; added: 1,800
  names     review: dropped: Security
  modality  review: if 1 to 0, may 1 to 0, will 0 to 1
```

Here an edit changed a figure, dropped the approver and turned a possibility
into a commitment. With `--brief`, the first file is a set of supplied facts and
the report shows only what a draft added, which catches invented statistics and
features. The [fidelity guide](human-writing/references/fidelity.md) explains
each kind of difference and what a token comparison cannot see.

## Install

Choose the skill or the plugin for each host to avoid duplicate entries.
[Releases](https://github.com/hongymagic/hooman/releases) contain versioned ZIPs
and checksums. To build this checkout's archives:

```sh
python3 scripts/package.py
```

For version 2.0.0 this creates `dist/human-writing-2.0.0.zip`,
`dist/hooman-2.0.0-plugin.zip` and `dist/SHA256SUMS`.

### Codex

Install through the repository marketplace:

```sh
codex plugin marketplace add hongymagic/hooman
codex plugin add hooman@hooman
```

For a standalone skill, extract the skill ZIP into `~/.agents/skills/` or your
project's `.agents/skills/`. The resulting path is
`.../skills/human-writing/SKILL.md`. Invoke `$human-writing`, or let the host
select it for a writing request. See the
[Codex skill documentation](https://learn.chatgpt.com/docs/build-skills).

### Claude Code

```sh
claude plugin marketplace add hongymagic/hooman
claude plugin install hooman@hooman
```

Invoke `/hooman:human-writing` with your draft and brief. To use a local checkout
for one session:

```sh
claude --plugin-dir .
```

See the [Claude plugin documentation](https://code.claude.com/docs/en/plugins).

### ChatGPT and Claude

Where custom skill uploads are available, upload the standalone skill ZIP and
ask the host to use `human-writing`. Upload and execution support depend on the
host and workspace. Follow the current instructions for
[ChatGPT Skills](https://help.openai.com/en/articles/20001066) or
[Claude Skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
The plugin ZIP is a separate plugin distribution, with portable, Codex and Claude
manifests. Installing a skill does not publish it to a directory.

## Use the skill

Ask naturally:

- “Use human-writing to de-slop this draft. Keep my tone.”
- “Draft an executive update from these facts.”
- “Review this ADR without rewriting it.”
- “Write the labels and empty states for this page.”

Supply the audience, the purpose, any constraints and a real writing sample when
you have them. The skill returns finished prose by default and honours requests
for copy only. It can also report findings without changing the document.

[SKILL.md](human-writing/SKILL.md) holds the workflow.
[Patterns](human-writing/references/patterns.md) lists what to edit, the fix and
when to keep each pattern. [Registers](human-writing/references/registers.md)
covers replies, documentation, updates, posts, product copy and interface copy.

## What it is built on

The catalogue and the thresholds come from three sources, combined in November
2026: existing skills and catalogues, published research, and this project's own
measurements.

The measurements used 115,000 words of technical and business prose pinned to
commits made before November 2022, 600 human-written documents from a published
parallel corpus with GPT-4o continuations of the same documents, and fresh
specimens from Claude, Codex and Gemini models. The
[validation notes](docs/validation.md) give the method, the rates and the limits.
[The evidence summary](docs/evidence.md) explains which findings shaped which
rules. To repeat the measurement:

```sh
python3 scripts/calibrate.py fetch
python3 scripts/calibrate.py measure --rules
```

## Get a separate model edit

This step is optional. Use a CLI already installed and authenticated for a
different model family. For a draft written by an OpenAI model:

```sh
python3 human-writing/scripts/cleanse.py README.md --writer openai --output revised.md
```

For a draft written by an Anthropic model, use `--writer anthropic`. The helper
refuses same-family routing, validates a structured reply, checks the copy,
compares it with your source and saves a new candidate file. It never overwrites
your source or an existing output. Provider data handling and usage charges
apply to model calls.

When another model is unavailable, print the brief for manual use:

```sh
python3 human-writing/scripts/cleanse.py README.md --writer openai --prompt-only
```

See [the separate model guide](human-writing/references/second-pass.md) for
routing, timeouts, failure handling and what the pass can and cannot establish.

## Verify

```sh
python3 scripts/verify.py
```

That runs the regression tests, checks the repository's prose with the rules it
distributes and validates both reproducible archives. CI runs on Linux, macOS
and Windows. Tests use controlled CLI responses and real local subprocesses;
they make no model calls and no network calls.
[Release instructions](docs/releases.md) cover publishing and recovery.

## Credits

Hooman 2.0 was rebuilt after studying three skills, all MIT licensed:
[blader/humanizer](https://github.com/blader/humanizer) for its account of
default choices and its ordering of patterns by strength,
[hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) for its
structure lists and reader-facing checks, and
[conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)
for its editing contract, its guard against inventing a voice and its habit of
measuring rules against human text. No text was copied; the patterns were
described afresh and measured again here.

The catalogue also draws on Wikipedia's
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
[tropes.fyi](https://tropes.fyi/directory), [sloptells](https://sloptells.com/)
and Simon Willison's
[LLM cliché highlighter](https://tools.simonwillison.net/llm-cliche-highlighter).
Calibration uses the
[HAP-E corpus](https://huggingface.co/datasets/browndw/human-ai-parallel-corpus)
by Reinhart and colleagues. The papers are listed in the
[evidence summary](docs/evidence.md).

[MIT licensed](LICENSE).
