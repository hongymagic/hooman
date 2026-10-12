# human-writing

Draft, edit or review prose for its reader. The skill checks a draft, rewrites it,
uses a different model family for a second edit when available, then compares and
checks the result.

Ask “Use human-writing to edit this draft”, “De-slop this copy”, or “Review this
without rewriting it”. Supply the audience, purpose and a real voice sample when
useful. Finished prose is the default output.

[SKILL.md](SKILL.md) contains the workflow.
[Editing examples](references/editing.md) explain its decisions.
[The checker](references/checker.md) runs locally with Python 3.12 or newer;
[the separate model helper](references/second-pass.md) uses an installed,
authenticated Codex or Claude CLI. The instructions also work without execution,
but a manual review cannot supply a measured checker result.

See the [project installation guide](https://github.com/hongymagic/hooman#install).
This bundle is [MIT licensed](LICENSE).
