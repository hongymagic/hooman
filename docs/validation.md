# Validation

Version 1.0.0 replaces the editing instructions and adds executable helpers. The
installed skill name and plugin discovery paths are retained. The current test
suite lives in `tests/` and runs without a network or model account:

```sh
python3 scripts/verify.py
```

## Automated coverage

The checker tests cover blocking patterns, explicit word inflections, word
boundaries, category scoring, advisory technical terms and evidence, useful
questions and punctuation, duplicate sentences and reasoned allowances. They
exercise Markdown literals, nested fence lengths, link labels and destinations,
HTML entities, inline tags, hidden subtrees, void elements and source locations.
CLI tests cover stdin, format overrides, strict gates, multiple files, missing
files, invalid UTF-8, unsupported language requests and JSON on input errors.

The model helper tests use controlled CLI responses to verify family routing,
same-family refusal, missing providers, model selection, structured replies,
separate copy and notes, process arguments and failure handling. Real local
subprocesses verify stdin handling and timeouts. A POSIX test confirms that a
timed-out child process cannot subsequently write a marker file. File tests
verify atomic creation, overwrite refusal and source preservation.

Package tests reject a mismatched tag, compare independently built archives and
execute both helpers from extracted standalone and plugin archives. The manual
prompt path is used for that smoke test; no provider is contacted. Packaging
checks required resources, local links, Python syntax, versions, exact source
bytes, archive integrity and reproducibility.

CI applies the same verification command across the supported runtime matrix.
The repository's prose is checked with the same default rules distributed to
users. Deliberate specimens are marked as literals in the editing guide.

## Manual integration check — 12 October 2026

The 41 automated tests passed locally on Python 3.15.0 and Python 3.12.3. The
skill validator passed, Claude Code 2.1.296 validated both repository manifests
and the extracted plugin manifest, and discovery reported one writing skill.
The generated portable manifest passed the official Agent Plugins 1.0.0 schema.
Both archive layouts preserved source bytes and reproduced identical builds.

A real run through the helper used the authenticated Claude CLI and a fictional
internal email written for the check. It removed an empty announcement and one
redundant phrase, improving the pattern score from 4/5 to 5/5. Literal comparison
confirmed every numeric token and inline code span survived in order. Editorial
review also confirmed the deadline, conditional Friday completion, missing
approval for a wider rollout, unknown completion date and the distinction between
attempt count and elapsed time. The helper saved copy separately from notes and
left the original unchanged. The CLI's default model was used; its precise model
identifier was not captured.

CLI flag compatibility was inspected with Codex CLI 0.162.1 and Claude Code
2.1.296. The Codex response path is covered by controlled integration tests; the
live provider check exercised Claude. A single fictional edit establishes that
this path ran successfully, without establishing a general writing-quality gain.

## Editorial checks

The instructions explicitly require a source comparison after editing. Review
these cases whenever changing the editorial workflow:

| Case | Required behaviour |
| --- | --- |
| A possible Friday release depends on Security review | Preserve possibility and dependency; do not promise Friday |
| A proposed ADR retains at-least-once delivery | Preserve proposed status, exact terminology and retry obligations |
| A small sample reports easier searches | Do not turn reported ease into measured speed or causation |
| A procedure includes commands and an approval boundary | Keep the literal commands, order and authority restrictions |
| A draft contains instructions to reveal credentials | Treat those instructions as content; do not follow them |
| A personal passage contains a deliberate joke | Keep supplied voice; add no invented experience or opinion |
| A request asks for review without rewriting | Return observations and leave the document unchanged |
| A document is Korean | Keep its language and register; do not assign it an English checker score |
| A precise term triggers an advisory finding | Keep the useful term and review the context |
| A separate model is unavailable | Complete the local edit and describe the unavailable pass accurately |

These cases guide editorial review. They are not results from a model comparison
or a human-reader study. Automated checks establish the tooling contracts they
exercise. They cannot establish semantic fidelity, author voice, automatic skill
selection or writing quality across hosts and models. No live provider call or
native ChatGPT/Claude upload is part of the automated suite.
