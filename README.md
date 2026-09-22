# Hooman

Hooman provides one reusable skill, **human-writing**, for drafting, editing and reviewing prose. It works from the facts or writing you supply, preserving your meaning and adapting to your audience and voice.

Use it for emails, executive updates, ADRs, documentation, PR descriptions, articles and product copy. It defaults to direct, professional language and Australian English when writing in English, and preserves the input language unless you ask for a translation. Factual accuracy takes priority over style. AI-detector evasion is not a goal.

The skill is Markdown, with no runtime dependencies, network requests, telemetry, hooks or external writing services. Your chosen host model processes the prose under that host's settings. The core instructions are complete on their own.

## Install

Choose the instructions for your host below. Install either the skill or the plugin once per host to avoid duplicate entries.

Versioned archives and `SHA256SUMS` are available from [Releases](https://github.com/hongymagic/hooman/releases). The standalone skill ZIP contains `human-writing/`. The plugin ZIP contains the same skill under `skills/human-writing/`, with portable, Codex and Claude manifests.

### Codex

To install the plugin from the repository marketplace:

```sh
codex plugin marketplace add hongymagic/hooman --ref v0.3.0
codex plugin add hooman@hooman
```

Start a new task, select Hooman from your installed plugins and ask it to use `human-writing`. This repository is not listed in OpenAI's public plugin directory. [OpenAI's plugin documentation](https://developers.openai.com/plugins/build/plugins) covers marketplace installation and supported package formats.

For a standalone skill, extract `human-writing-0.3.0.zip` into `~/.agents/skills/` or your project's `.agents/skills/`. The resulting path must be `.../skills/human-writing/SKILL.md`. Invoke it as `$human-writing` or let Codex select it for a relevant writing request. See [Codex skill locations](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

### Claude Code

Install the plugin from the repository marketplace:

```sh
claude plugin marketplace add hongymagic/hooman
claude plugin install hooman@hooman
```

Invoke `/hooman:human-writing`, followed by your request. This marketplace follows the repository's default branch. For an exact release, check out its tag and load that checkout for a session:

```sh
git clone --branch v0.3.0 --depth 1 https://github.com/hongymagic/hooman.git
claude --plugin-dir ./hooman
```

The manifest uses a custom skill path supported by [Claude Code plugins](https://code.claude.com/docs/en/plugins-reference). The repository also includes a [Claude marketplace](https://code.claude.com/docs/en/plugin-marketplaces).

### ChatGPT

Where Skills are available, open **Plugins → Skills → Create → Upload from your computer** and upload the standalone `human-writing-0.3.0.zip`. Install it, then ask, “Use human-writing to edit this draft.” Availability depends on your account and workspace; see [Skills in ChatGPT](https://help.openai.com/en/articles/20001066).

The separate plugin ZIP follows the [current portable Agent Plugins format](https://developers.openai.com/plugins/build/plugins#package-and-distribute-plugins) for plugin import and submission workflows. Uploading to a private workspace and publishing to OpenAI's public directory are separate actions. This repository and its release pipeline do not publish a directory listing.

### Claude web and desktop

Open **Customize → Skills → + → Create skill → Upload a skill** and upload `human-writing-0.3.0.zip`. Enable the skill and ask Claude to use it. Claude requires code execution to be enabled even though this skill contains no executable code. See [Claude's skill installation instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## Use

Supply the facts or prose. Add the audience, purpose, constraints and a genuine writing sample when they would help. Use ordinary instructions to choose what the skill does:

- “Use human-writing to draft an executive update from these facts.”
- “Use human-writing to tighten this email, keeping my tone.”
- “Use human-writing to review this ADR and explain suggested changes. Don't rewrite it.”

The skill returns finished prose by default. When editing, it makes the smallest useful change; when reviewing, it explains suggested changes without rewriting. It flags unresolved factual conflicts.

[SKILL.md](human-writing/SKILL.md) contains the full editorial policy. The optional [style guide](human-writing/references/style-guide.md) illustrates plain phrasing, sentence rhythm, author voice and the difference between empty rhetorical devices and useful ones.

## Verify and maintain

With Python 3.10 or newer, run:

```sh
python3 scripts/package.py --check
python3 scripts/package.py
```

The packaging helper checks version consistency, package structure, core word count, archive integrity, source-byte preservation and reproducibility. It builds the two ZIP files and checksums in `dist/`. The helper is release tooling, is never included in the runtime archives and does not score writing quality.

Review the [evaluation cases](human-writing/evals/cases.md) and [evaluation results](human-writing/evals/v0.3.0/results.md) for factual preservation, clarity, voice fit and unnecessary changes. Structural checks cannot prove editorial quality or guarantee that a model will follow every instruction. Native GUI import and all possible host/model combinations have not been tested.

The [release instructions](docs/releases.md) cover tag publishing, version updates, recovery and packaging checks.

## Licence

Original Hooman material is [MIT licensed](LICENSE). See [notices and attribution](human-writing/NOTICE.md) for upstream material and bundled licences.
