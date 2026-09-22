# human-writing

A portable editorial skill for drafting, editing and reviewing prose. Its instructions
live in [SKILL.md](SKILL.md); the host model supplies the writing capability. The skill
has no runtime dependencies or external services.

After installing it in a host that supports Agent Skills, ask naturally:

- “Use human-writing to draft an executive update from these facts: …”
- “Use human-writing to tighten this email for a customer: …”
- “Use human-writing to review this ADR. Explain suggested changes without rewriting it: …”

Include the audience, purpose, constraints and an optional voice sample when useful.
Ordinary drafting and editing requests can also activate the skill through its description.
The host controls discovery and explicit invocation syntax.

For platform installation, downloadable bundles and release instructions, see the
[hooman repository](https://github.com/hongymagic/hooman#readme).

Optional [examples](references/examples.md) explain editorial choices;
[source decisions](references/source-decisions.md) record the inspected upstream commits
and synthesis. [Evaluation cases](evals/cases.md) define observable outcomes without
requiring exact rewrites. These resources are not loaded for ordinary writing tasks.
The [latest evaluation record](evals/v0.1.1/results.md) compares the structure refinement
with the previous skill and links the original baseline/assisted evaluation.

Read [NOTICE.md](NOTICE.md) and the bundled licences for attribution. The instructions
can reduce avoidable editorial drift, but a model can still misunderstand evidence or
miss a factual error; evaluation results document observed behaviour rather than a guarantee.
