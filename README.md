# Hooman

Hooman helps you turn a draft into writing you can use. It checks common editing
patterns, rewrites for the reader, gets a separate model edit when available,
then compares and checks the result.

Use it for emails, READMEs, technical decisions, updates, articles and product
copy. It preserves your facts and voice. English defaults to Australian spelling
unless your brief or draft establishes another convention.

The `human-writing` skill contains the workflow. A local checker gives line-level
findings and a score out of five. A separate helper can send a draft to a different
model family through an installed Codex or Claude CLI. The checker needs Python
3.12 or newer and has no third-party dependencies or network calls. The model
pass needs its own provider access. The instructions also support manual editing.

## Try the checker

From a checkout:

```sh
python3 human-writing/scripts/check.py --text "It is worth noting that the export runs."
```

That returns 4/5, identifies the empty announcement and exits 1. After editing:

```sh
python3 human-writing/scripts/check.py --text "The export runs."
```

That returns 5/5 and exits 0. A score reflects matched patterns. It does not verify
facts, measure all aspects of writing quality or establish who wrote the text.

Check a file or request a machine-readable report:

```sh
python3 human-writing/scripts/check.py README.md
python3 human-writing/scripts/check.py README.md --json
```

Markdown extraction excludes common literal examples and code. HTML extraction
reads static prose and omits scripts, styles and explicitly hidden subtrees.
Context-dependent findings remain advisory; `--strict` includes them in the gate.
See the [checker reference](human-writing/references/checker.md) for rule IDs,
allowances, extraction boundaries and exit statuses. Rules cover English only;
other languages need editorial review without this numeric score.

## Install

Choose the skill or plugin for each host to avoid duplicate entries.
[Releases](https://github.com/hongymagic/hooman/releases) contain versioned ZIPs and
checksums. To build this checkout's archives:

```sh
python3 scripts/package.py
```

For version 1.0.0 this creates `dist/human-writing-1.0.0.zip`,
`dist/hooman-1.0.0-plugin.zip` and `dist/SHA256SUMS`.

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

Supply the audience, purpose, constraints and a genuine writing sample when they
help. The skill returns finished prose by default and honours requests for copy
only. It can also report findings without changing the document.

[SKILL.md](human-writing/SKILL.md) contains the workflow and factual safeguards.
[Editing examples](human-writing/references/editing.md) show the decisions.

## Get a separate model edit

Use a CLI already installed and authenticated for a different model family.
For a draft written by an OpenAI model:

```sh
python3 human-writing/scripts/cleanse.py README.md --writer openai --output revised.md
```

For a draft written by an Anthropic model, use `--writer anthropic`. The helper
refuses same-family routing, validates a structured reply, checks the copy and
saves a new candidate file. It never overwrites your source or an existing output.
Compare that candidate with the source before accepting it. Provider data handling
and usage charges apply to model calls.

When another model is unavailable, print the brief for manual use:

```sh
python3 human-writing/scripts/cleanse.py README.md --writer openai --prompt-only
```

See [the separate model guide](human-writing/references/second-pass.md) for routing,
timeouts, failure handling and how to carry the editing brief.

## Verify

```sh
python3 scripts/verify.py
```

That runs regression tests, checks the repository's prose and validates both
reproducible archives. CI runs on Linux, macOS and Windows. Tests use controlled
CLI responses and real local subprocesses; they make no model calls. The
[validation notes](docs/validation.md) distinguish those checks from editorial
judgement. [Release instructions](docs/releases.md) cover publishing and recovery.

[MIT licensed](LICENSE).
