# Maintaining and releasing Hooman

## One source, two distributions

Maintain the skill only in `human-writing/`. Source compatibility manifests point to `./human-writing`, allowing the repository to serve as a Codex and Claude marketplace without a second skill copy or symlinks.

`scripts/package.py` generates:

| Asset | Contents | Intended use |
| --- | --- | --- |
| `human-writing-<version>.zip` | `human-writing/SKILL.md` and its supporting resources/licences | Standalone skill installation or upload |
| `hooman-<version>-plugin.zip` | Portable `plugin.json`, `skills/human-writing/`, `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `LICENSE` | Portable plugin import or a local plugin directory after extraction |
| `SHA256SUMS` | SHA-256 hashes for both ZIPs | Verify downloaded release assets |

The generated plugin uses fixed `skills/` discovery from [Agent Plugins 1.0.0](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json), as required by [OpenAI's current packaging documentation](https://developers.openai.com/plugins/build/plugins). Its OpenAI interface metadata is in `extensions.com.openai`; the separate Codex compatibility manifest remains available to older hosts. Claude uses its own compatibility manifest. The archive builder rewrites only these manifest skill paths; canonical skill files retain their exact bytes and relative links.

ZIP entries have sorted paths, fixed timestamps and permissions, and no compression. For this small text package, storing entries provides reproducible bytes without depending on a compressor version. Builds include the complete skill directory, including provenance, evaluation records and licence notices. Those references are not automatically loaded as writing instructions. No CI scripts or development dependencies ship in either runtime archive.

## Cut a release

1. Update the stable semantic version in `VERSION`, `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, and the plugin entry in `.claude-plugin/marketplace.json`. Update installation examples in `README.md` to that version. Pre-release version strings are deliberately unsupported by this small release pipeline.
2. Revisit the evaluation cases when changing editorial behaviour. Record the model, conditions, actual outputs and limitations in `human-writing/evals/`; do not infer writing quality from packaging checks.
3. Run `python3 scripts/package.py --check --tag v<version>`. Where available, validate the Claude source with `claude plugin validate --strict .claude-plugin/plugin.json` and `claude plugin validate --strict .claude-plugin/marketplace.json`.
4. Commit the finished change on `main` and let **Check package** pass. Create and push an annotated `v<version>` tag pointing at that commit. For version 0.1.1, the commands are:

   ```sh
   git tag -a v0.1.1 -m "Release Hooman 0.1.1"
   git push origin v0.1.1
   ```

5. The **Release** workflow checks the exact tag/version match, builds and validates the archives, then publishes a GitHub Release with both ZIPs and checksums. Open the resulting release and confirm all three assets are attached. It does not submit anything to an OpenAI or Anthropic directory.

The workflow uses the repository's automatic `GITHUB_TOKEN`; no personal access token or external service secret is required. Build jobs have `contents: read`; only the publish job receives `contents: write`. Pull requests do not run with publishing privileges, checkout does not retain credentials, and remote action dependencies are pinned to full commit SHAs following [GitHub's guidance](https://docs.github.com/en/actions/reference/security/secure-use). Dependabot proposes GitHub Actions updates monthly.

The action versions below were resolved from their upstream release tags on 22 September 2026:

| Action | Version | Inspected commit |
| --- | --- | --- |
| `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | `v7.0.0` | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| `actions/upload-artifact` | `v7.0.1` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |
| `actions/download-artifact` | `v8.0.1` | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` |

## Recover a failed release

If failure occurred before release creation, fix infrastructure issues and rerun the failed jobs for the same tag. Do not move a published tag. If the tagged content needs correction, create a new version.

`gh release create` uploads supplied assets through a draft before publication and `--verify-tag` refuses an absent tag. See the [GitHub CLI contract](https://cli.github.com/manual/gh_release_create). If a failed run leaves a draft, inspect it with `gh release view v<version>` and inspect the workflow logs. Confirm its target commit and assets before retrying; remove only that incomplete draft when appropriate, then rerun the release job. The pipeline does not overwrite or delete an existing release on a rerun.

To verify downloaded ZIPs on Linux, place them beside `SHA256SUMS` and run `sha256sum --check SHA256SUMS`. On macOS use `shasum -a 256 -c SHA256SUMS`. Checksums detect asset changes; they are not an independent signature of publisher identity.

## Compatibility checks and limits

On 22 September 2026, the packaging work used Python 3.14.7, Codex CLI 0.155.1 and Claude Code 2.1.278. `claude --plugin-dir . plugin details hooman` discovered exactly one `human-writing` skill and no agents, hooks, MCP servers or LSP servers. Both source Claude manifests passed native validation without warnings. The package helper verified deterministic builds, archive integrity and exact preservation of source files.

An extracted generated plugin also passed the bundled Codex plugin-creator validator and Claude's strict plugin validator, and Claude discovered its single skill. Its portable `plugin.json` passed validation against the official Agent Plugins 1.0.0 JSON Schema fetched for this review. An intentionally mismatched `v9.9.9` tag was rejected before packaging. PyYAML and jsonschema were used only in temporary validation environments; neither is a project or runtime dependency.

The bundled Codex plugin-creator validator requires the conventional `./skills/` layout even though the current Codex runtime supports custom legacy skill paths. Run that validator against an extracted generated plugin archive, where the conventional layout exists. Do not change the single canonical source layout merely to satisfy that older helper restriction.

The publication workflow must be observed on GitHub to establish that a release ran successfully. Local builds do not establish that. ChatGPT and Claude web/desktop uploads require eligible accounts and workspace permissions and have not been verified through their GUIs. A compatible package is not a claim of public-directory approval. Host models can still make editorial mistakes; the behavioural evaluation report states its own coverage.
