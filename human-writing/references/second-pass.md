# A separate model edit

Read this before using the helper. It sends the draft to an installed CLI's model
provider using the account already authenticated there. That provider's data
handling and usage charges apply. Use it when the task authorises processing the
draft with that provider. No API key is stored or requested by Hooman.

The helper accepts English drafts. It uses Python 3.12 or newer and a current
Codex or Claude Code CLI supporting the flags below. It runs from a temporary
directory, sends the draft through stdin and does not expose it in process
arguments. It disables custom CLI configuration and session persistence. Codex
uses its read-only sandbox with shell execution disabled; Claude has tools and
MCP disabled. The CLIs still
need their own authentication and network access.

Commands below run from the skill directory. Use a draft path that exists and a
new output path:

```sh
python3 scripts/cleanse.py README.md --writer openai --output revised.md
```

| Writer family | Default reviewer |
| --- | --- |
| `openai` | Claude |
| `anthropic` | Codex |
| `google`, `other` | First installed CLI: Codex, then Claude |

Use `--reviewer codex` or `--reviewer claude` to choose explicitly. Same-family
routing fails. Do not label an OpenAI draft `other` to bypass that check. If the
writer's family is unknown, determine it before running an independent pass.
`--model` selects a model supported by that CLI; otherwise the CLI's default
applies. No model name is frozen into the helper. Codex is forced to its OpenAI
provider; Claude installations must use an Anthropic model for this family label
to be valid. Use `--audience` and `--purpose` to carry the actual brief.

The editorial prompt is [cleanse.txt](../prompts/cleanse.txt). To use it manually
without a model call:

```sh
python3 scripts/cleanse.py README.md --writer openai --prompt-only
```

That command prints instructions and input, not a rewritten draft. Paste it into
a different family's chat and request the specified JSON reply. Compare its
`copy` with the source and check the saved document afterwards.

## Result handling

The helper validates a structured reply containing `copy` and `notes`, checks the
returned copy and saves it atomically to a new file. It never replaces the source
or an existing destination. Standard output stays empty during a model pass;
change notes and checker findings go to stderr. Do not redirect stdout into a
draft file. A saved draft is a candidate that still needs a fidelity comparison.

| Exit | Meaning |
| --- | --- |
| 0 | A candidate was saved and has no blocking patterns, or a manual prompt was printed |
| 1 | A candidate was saved with blocking findings requiring another edit |
| 2 | Invalid input, a failed CLI, an invalid reply or a save error; no candidate was saved |
| 124 | The call exceeded its timeout or was interrupted; no candidate was saved |
| 127 | No different-family CLI was installed; no candidate was saved |

The default timeout is 180 seconds; `--timeout` accepts a positive finite number
of seconds. A timeout stops the process tree. The helper does not retry or fall
back to another provider after a CLI failure. Resolve authentication, access or
compatibility separately, or use the manual prompt and continue the local edit.

Before using a candidate, compare facts, uncertainty, obligations, code, links,
quotations and structure with the original. The helper's schema and pattern
checks cannot establish semantic fidelity. Accept only changes that help the
document and preserve the brief.
