# human-writing

Draft, edit or review prose for its reader. The skill checks a draft for patterns
worth editing, edits the passages that fail, compares the result with the source
so no fact drifts, and checks again.

Ask “Use human-writing to edit this draft”, “De-slop this copy”, or “Review this
without rewriting it”. Supply the audience, the purpose and a real writing sample
when you have them. Finished prose is the default output.

- [SKILL.md](SKILL.md) is the workflow.
- [Patterns](references/patterns.md) lists what to edit, the fix and when to keep it.
- [Registers](references/registers.md) covers replies, documentation, updates,
  posts, product copy and interface copy.
- [Fidelity](references/fidelity.md) explains the before-and-after comparison.
- [The checker](references/checker.md) documents rule IDs and output.
- [The separate model helper](references/second-pass.md) is optional and uses an
  installed, authenticated Codex or Claude CLI.

The checker and the comparison run locally with Python 3.12 or newer and make no
network calls. The instructions also work without execution, but a manual review
cannot supply a measured result.

See the [project installation guide](https://github.com/hongymagic/hooman#install).
This bundle is [MIT licensed](LICENSE).
