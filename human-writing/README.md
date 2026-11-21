# human-writing

human-writing is an agent skill for writing, editing and reviewing English
prose in a plain style. The model lists the facts, takes the established form
for the kind of document and writes one fact to a sentence under label
headings. Two scripts check the result and compare it with its source.

## Contents

| File | Content |
| --- | --- |
| [SKILL.md](SKILL.md) | The standard and the procedure |
| [forms.md](references/forms.md) | Section labels for each kind of document |
| [exemplars.md](references/exemplars.md) | Passages of human writing from 1863 to 2021 |
| [patterns.md](references/patterns.md) | Each checker finding, its fix and when to keep the passage |
| [fidelity.md](references/fidelity.md) | The comparison of an edit with its source |
| [checker.md](references/checker.md) | Rule IDs, thresholds and output |
| [second-pass.md](references/second-pass.md) | The optional edit by a second model family |

## Requirements

Python 3.12 or newer for the scripts. `check.py` and `compare.py` make no
network calls. `cleanse.py` needs an installed, signed-in Codex or Claude CLI.
Without script execution the instructions still apply, and no measured result
is reported.

## Installation

See the
[project installation guide](https://github.com/hongymagic/hooman#installation).

## Usage

Make a request such as “Use human-writing to edit this draft”, “Draft a status
update from these facts” or “Review this without rewriting it”. Supply the
reader, the purpose and a writing sample where there is one. The output is
finished text.

## Licence

[MIT](LICENSE). The passages in exemplars.md carry their own terms, listed in
that file.
