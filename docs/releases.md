# Maintaining and releasing Hooman

## Canonical bundle

Maintain the installed skill in `human-writing/`. Both repository plugin manifests
point there. The package builder includes the instructions, references, prompt,
checker, model helper and project licence. Tests and release tooling stay outside
the runtime bundle. Python caches are excluded.

| Asset | Layout |
| --- | --- |
| `human-writing-<version>.zip` | `human-writing/SKILL.md` with its supporting files |
| `hooman-<version>-plugin.zip` | `skills/human-writing/`, portable `plugin.json`, host manifests and licence |
| `SHA256SUMS` | SHA-256 digests of both ZIPs |

The plugin archive uses [Agent Plugins 1.0.0](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json)
with OpenAI metadata in `extensions.com.openai`, plus Codex and Claude compatibility
manifests. Only manifest discovery paths change during packaging. Canonical files
retain their bytes and relative paths. Entries use sorted names, fixed timestamps
and permissions, and stored compression for deterministic archives.

## Verify a change

```sh
python3 scripts/verify.py
python3 scripts/package.py --check --tag v1.0.0
```

The verification command runs regression tests, the prose gate and two independent
builds for byte comparison. Packaging also validates versions, required resources,
local links, Python 3.12 syntax and archive contents. Tests execute helpers from
extracted standalone and plugin archives to catch missing runtime resources.

Revisit editorial cases when changing the instructions or rules. Use real outputs
for any writing-quality claim. A pattern test or package check does not establish
that a model follows the skill, preserves every fact or improves prose for readers.

Validate Claude manifests with the installed CLI when available:

```sh
claude plugin validate --strict .claude-plugin/plugin.json
claude plugin validate --strict .claude-plugin/marketplace.json
```

## Publish

1. Update `VERSION`, both host manifests, the Claude marketplace entry and versioned
   examples. Keep a stable semantic version; prerelease strings are unsupported.
2. Run verification and inspect the final diff. Run `python3 scripts/package.py`
   to build local assets for inspection.
3. Commit the change and wait for CI. Create an annotated tag matching `VERSION`
   and push it. For this version:

   ```sh
   git tag -a v1.0.0 -m "Release Hooman 1.0.0"
   git push origin v1.0.0
   ```

4. The release workflow repeats verification, checks the tag, builds the archives
   and publishes both ZIPs with checksums. Confirm the three attached assets.

The workflow uses `GITHUB_TOKEN`. Build jobs have read access; only publishing
receives `contents: write`. Checkout does not retain credentials. Releases do not
submit a public plugin listing or install the package into anyone's host.

## Runtime and action pins

CI uses Python 3.15.0, the current stable release verified against
[Python's downloads](https://www.python.org/downloads/). It also checks the minimum
supported series on Python 3.12.15 on Linux. Supporting 3.12 allows hosts with that
maintained runtime to execute dependency-free helpers; no newer runtime feature
is required. Full Python 3.15.0 checks run on Linux, macOS and Windows.

Action tags were resolved to these commits on 12 October 2026:

| Action | Version | Commit |
| --- | --- | --- |
| checkout | 7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| setup-python | 7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| upload-artifact | 7.0.2 | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |
| download-artifact | 8.0.2 | `9000827ccba6bdab643e8b6fd33ac0654aef8333` |

Dependabot checks action updates monthly. Hooman does not install or pin the
optional model CLIs; their host manages updates and authentication. The helper
uses current documented structured-output options and a CLI default model unless
`--model` is supplied. Consult the [Codex non-interactive reference](https://learn.chatgpt.com/docs/non-interactive-mode)
and [Claude CLI reference](https://code.claude.com/docs/en/cli-reference) when
updating those integrations.

## Recover a failed release

If the failure precedes publication, inspect the logs and rerun infrastructure
failures for the same tag. Do not move a published tag. Correct tagged content in
a new version. If an incomplete draft release remains, verify its target and
assets before removing that draft and rerunning. The workflow does not overwrite
an existing release.

Verify downloaded assets beside `SHA256SUMS` with `sha256sum --check SHA256SUMS`
on Linux or `shasum -a 256 -c SHA256SUMS` on macOS. A checksum verifies bytes, not
publisher identity.
