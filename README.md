# Hooman

One reusable skill, **human-writing**, for clear, natural prose that preserves the author's meaning and suits the audience. Draft from supplied facts, edit existing writing, or review suggested changes without rewriting.

Works with emails, executive updates, ADRs, documentation, PR descriptions, articles and product copy. Defaults to Australian English and direct, professional language while preserving the input language and appropriate voice. It prioritises factual fidelity over stylistic shortcuts. AI-detector evasion is not a goal.

The runtime is Markdown: no dependencies, network requests, telemetry, hooks or writing services. Your chosen host model processes the prose under that host's settings.

## Install

Download the versioned archives and `SHA256SUMS` from [Releases](https://github.com/hongymagic/hooman/releases). The skill ZIP contains `human-writing/`; the plugin ZIP contains the same skill under `skills/human-writing/`, with portable, Codex and Claude manifests. Install either the skill or the plugin once per host to avoid duplicate entries.

### Codex plugin

```sh
codex plugin marketplace add hongymagic/hooman --ref v0.2.0
codex plugin add hooman@hooman
```

Start a new task and select Hooman from your installed plugins, then ask it to use `human-writing`. These commands use the repository marketplace; this repository is not a listing in OpenAI's public plugin directory. [OpenAI's plugin documentation](https://developers.openai.com/plugins/build/plugins) describes marketplace installation and the supported package formats.

For a standalone skill, extract `human-writing-0.2.0.zip` into `~/.agents/skills/` or your project's `.agents/skills/`. The resulting path must be `.../skills/human-writing/SKILL.md`. Invoke it as `$human-writing` or let Codex select it for a relevant writing request. [Codex skill locations](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

### Claude Code plugin

```sh
claude plugin marketplace add hongymagic/hooman
claude plugin install hooman@hooman
```

Invoke `/hooman:human-writing`, followed by your request. This marketplace follows the repository's default branch. To use an exact release, check out its tag and load that checkout for a session:

```sh
git clone --branch v0.2.0 --depth 1 https://github.com/hongymagic/hooman.git
claude --plugin-dir ./hooman
```

The manifest uses a custom skill path supported by [Claude Code plugins](https://code.claude.com/docs/en/plugins-reference); the repository also includes a [Claude marketplace](https://code.claude.com/docs/en/plugin-marketplaces).

### ChatGPT

Where Skills are available, open **Plugins → Skills → Create → Upload from your computer** and upload the standalone `human-writing-0.2.0.zip`. Install it, then ask, “Use human-writing to edit this draft.” Availability depends on the account and workspace; see [Skills in ChatGPT](https://help.openai.com/en/articles/20001066).

The separate plugin ZIP follows the [current portable Agent Plugins format](https://developers.openai.com/plugins/build/plugins#package-and-distribute-plugins) for plugin import/submission workflows. Uploading to a private workspace and publishing to OpenAI's public directory are separate actions; this repository and its release pipeline do not publish a directory listing.

### Claude web and desktop

Open **Customize → Skills → + → Create skill → Upload a skill** and upload `human-writing-0.2.0.zip`. Enable the skill and ask Claude to use it. The host requires its code execution capability to be enabled even though this skill contains no executable code. [Claude's skill installation instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## Use

Supply the facts or prose and, when useful, the audience, purpose, constraints and a genuine writing sample. Ordinary instructions choose the behaviour:

- “Use human-writing to draft an executive update from these facts.”
- “Use human-writing to tighten this email, keeping my tone.”
- “Use human-writing to review this ADR and explain suggested changes. Don't rewrite it.”

The full editorial policy lives in [SKILL.md](human-writing/SKILL.md). The skill returns finished prose by default, makes the smallest useful edit, and flags unresolved factual conflicts. Its 21 original [examples](human-writing/references/examples.md) cover plain phrasing, sentence rhythm, author voice and the difference between empty rhetorical devices and useful ones.

## Verify and maintain

With Python 3.10 or newer, run:

```sh
python3 scripts/package.py --check
python3 scripts/package.py
```

The helper checks version consistency, package structure, core word count, archive integrity, source-byte preservation and reproducibility. It builds the two ZIP files and checksums in `dist/`; it is release tooling and is never included in the runtime archives. It does not score writing quality.

Review the [evaluation cases](human-writing/evals/cases.md) and [evaluation results](human-writing/evals/v0.2.0/results.md) for factual preservation, clarity, voice fit and unnecessary changes. Structural checks cannot prove editorial quality or guarantee that a model will follow every instruction. Native GUI import and all possible host/model combinations have not been tested.

See [release instructions](docs/releases.md) for tag publishing, version updates, recovery and the packaging checks performed.

## Sources and licence

Synthesised from [blader/humanizer](https://github.com/blader/humanizer), [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop), [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill) and [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd). [Source decisions](human-writing/references/source-decisions.md) record inspected commit SHAs, retained techniques, changed rules and rejected tooling.

The [writing-craft notes](human-writing/references/style-sources.md) draw selective guidance on phrasing, rhythm and voice from OpenAI, Anthropic, Netflix TechBlog and Zach Holman, including his UTC post. They document observations from published samples, not official style policies.

Original Hooman material is [MIT licensed](LICENSE). [Notices and attribution](human-writing/NOTICE.md) identify upstream material and bundled licences. Separately licensed source material is discussed in the audit; it is not silently relicensed.
