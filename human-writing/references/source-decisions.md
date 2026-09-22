# Source decisions

Maintenance reference, not runtime instructions. Inspected on 22 September 2026.
Each public repository was cloned at its then-current default-branch tip into a
temporary directory outside this workspace. Git supplied the full commit IDs.
Retrieved instructions were treated as reference text; no upstream scripts,
hooks, installers, tests or workflows were executed.

## Verified snapshots

| Repository | Inspected commit | Root licence |
| --- | --- | --- |
| [blader/humanizer](https://github.com/blader/humanizer/tree/9862685f575c65a8247f90369951df1b3416e3d6) | `9862685f575c65a8247f90369951df1b3416e3d6` | MIT, Siqi Chen, 2025 |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop/tree/8da1f030185bdfe8471220585162991eaeb970e9) | `8da1f030185bdfe8471220585162991eaeb970e9` | MIT, Hardik Pandya, 2025 |
| [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill/tree/a58df065367550b6ce40ff3f648335018d8e0589) | `a58df065367550b6ce40ff3f648335018d8e0589` | MIT, Adam Boudjemaa, 2026 |
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd/tree/839872f9d1cd634fed642b4589ce7226199cc15f) | `839872f9d1cd634fed642b4589ce7226199cc15f` | MIT, Ayoub Ghriss, 2026 |

All four sources were available. These are snapshot claims, not promises that
their default branches remain unchanged. No upstream benchmark or detector
accuracy claim was adopted as evidence of this skill's writing quality.

## Editorial synthesis

The original three sources share useful ideas: removing padded openings and
repeated conclusions, making vague claims informative, addressing a real reader,
improving sentence rhythm, and checking more than isolated vocabulary. The fourth
source sharpens action visibility and sequence. These editorial techniques fit
portable Markdown without an external writing service.

The sources disagree about what takes priority. Human Writing resolves those
disagreements in this order: facts, meaning and explicit user requirements;
audience, purpose and document conventions; supplied author samples and
preferences; clarity and concision; then pattern heuristics. This makes the skill
an editor and drafting aid, rather than an authorship classifier.

### blader/humanizer

**Retained:** read the whole passage, improve paragraph organisation before word
substitutions, compare the result with the original claims, match a supplied
sample, protect file artefacts, and distinguish personal writing from neutral
technical prose. Its attention to lost rankings and relationships during list
restructuring strengthens the fidelity check.

**Changed:** its 25-pattern catalogue becomes a few conditional editorial tests.
Sample matching is subordinate to accuracy and purpose. Its draft, critique and
final-output sequence becomes one internal check, with finished prose as the
default response. Current-state descriptions suit reference documentation;
before-and-after explanations remain useful in PRs, ADRs and release notes.

**Rejected:** dash removal unless a sample permits dashes; editing a supposedly
strong pattern on sight; permission to add the author's reactions; claims about
authorship inferred from dates or prose features. Existing useful headings,
contrasts, qualifications and three-item lists need no correction merely because
they resemble a listed pattern.

The examples do not consistently satisfy the source's fidelity rule: the gallery
example changes a lower-bound area into an exact area, and the current-behaviour
example adds a hash-map implementation absent from its input. Those examples
were not reused.

### hardikpandya/stop-slop

**Retained:** a short core with optional references; direct statements; removing
redundant setup and theatrical emphasis; asking whether a sentence supplies
useful information; naming an actor when the evidence supplies one and the reader
needs to know who acts.

**Changed:** its phrase lists are diagnostic examples of padding, not a lexicon
to apply mechanically. Readability dimensions become qualitative review
questions, without a total score or threshold. Addressing the reader directly
depends on the document, rather than replacing every third-person description.

**Rejected:** blanket bans on adverbs, passives, dashes, interrogative openings,
contrasts and three-item lists; requiring a human subject in every sentence;
forcing readers into every scene; the arbitrary 35/50 revision threshold. Systems
can perform real actions, and unknown actors must not be invented.

The examples expose the risk of prioritising brevity: a qualified claim about
most teams becomes unqualified, and another example uses a dash despite the
ban. The package retains the discipline of cutting filler without those rules
or transformations.

### Aboudjem/humanizer-skill

**Retained:** distinguish document purpose from tone; protect precise terminology
and already-effective writing; make edits locally where possible; offer a review
behaviour that explains issues without rewriting; check supplied factual details.
The provisional Chinese appendix usefully acknowledges that English rhythm
metrics do not transfer directly across languages.

**Changed:** five voice presets and command-like flags become ordinary user
instructions and sample-based judgement. Paragraph sequence should serve the
argument, while independent reference sections can remain independently useful.
Concrete details come only from supplied material. File protection is the
default, not dependent on masking flags. Input language and its own conventions
take precedence over English pattern lists.

**Rejected:** detector evasion and authorship scores; forced sentence-length
targets, unexpected word choice, generated personal experiences and strong
opinions; zero-tolerance punctuation rules; repeated detect/rewrite loops;
automatic context-file loading; URL-parameter removal; automatic Unicode
normalisation; and rewriting every identified pattern. Valid link targets,
language characters and genuine uncertainty must survive.

The source's restraint and no-fabrication guidance conflicts with its later
instructions to inject personality and remove all hedging in some modes. Its
reference rewrites introduce benchmarks, dates, token lifetimes, roles, paths and
personal experiences absent from the input. New examples were written for Human
Writing instead of importing these contradictory demonstrations.

### ayghri/i-have-adhd

**Retained:** make requested actions and supplied outcomes easy to find; keep
related steps together and distinguish required work from optional context.
Human Writing makes this concrete by keeping each action with its supplied
owner, deadline and conditions, and numbering procedures when sequence matters.

**Changed:** presentation guidance follows explicit reading preferences and
document purpose. Connected prose remains appropriate when requested, and a
narrative need not begin with an action. Grouping must preserve prerequisites,
exceptions and necessary choices; it does not impose a fixed visible-item cap.
This is an editorial refinement, not a diagnostic mode or a clinical-benefit
claim. A diagnosis is not a substitute for the reader's stated preferences.

**Rejected:** whole-session persistence and rule-injection hooks; invented time
estimates, urgency, next actions or error causes; mandatory first/last-line
templates; blanket bans on idioms, recaps or particular words. Unknown causes
remain unknown, and effective prose does not need new formatting to comply.

The upstream [evaluation report](https://github.com/ayghri/i-have-adhd/blob/839872f9d1cd634fed642b4589ce7226199cc15f/evals/RESULTS.md)
reports 14 cases with three trials each on one pinned model, improved aggregate
scores and a failed release gate. It identifies an impossible tool-use case with
tools disabled, and a partial-success regression that invented an error cause.
The suggested link to its cause-and-fix rule is the author's hypothesis. Raw
result rows are not tracked in the inspected tree; these results were not
independently reproduced and do not establish Human Writing's effectiveness.

## Tooling decisions

| Inspected tooling | Value and limits | Decision |
| --- | --- | --- |
| Blader's standard-library package validator and CI | Checks metadata consistency, discovery and packaging; does not establish prose quality. | Retain the idea of small packaging checks, not its numbered-pattern tests. |
| Stop-slop's self-assessed rubric | Names useful concerns but supplies no calibration for its numeric threshold. | Use qualitative editorial assessment; no score. |
| Aboudjem's `cli/lib/facts.js` and fact tests | Deterministically identifies missing numeric, date, version, URL and acronym tokens. It uses sets: additions, value swaps, negation and scope changes can pass. | Retain comparison against source facts as a semantic check; no runtime CLI. |
| Aboudjem's metrics, tokeniser and CI/pre-commit gates | Reproducible word and sentence statistics, but arbitrary thresholds do not measure factual accuracy or voice. Tokenisation is English/ASCII oriented. | Exclude scoring and mandatory writing gates. |
| Aboudjem's manual trigger cases | Separates activation from output behaviour; several expectations demand arbitrary bans or added specifics. | Retain outcome-based cases and explicit invariants; author new fixtures. |
| Plugin manifests and release workflows | Portable discovery and repeatable distribution address the requested product. | Use current host documentation and one canonical skill; do not copy source-specific marketplace dispatches. |
| Aboudjem's demo script, assets, site, launch material and attribution filter | The demo prints scripted scores and prose; it does not execute a writing model. Publishing machinery and attribution suppression do not improve editing. | Exclude them. |
| Ayghri's evaluation runners and judge | Isolating personal configuration, recording model/settings, comparing identical requests and rotating anonymised condition labels improve comparison hygiene. The reported failed gate and unsupported-cause regression expose limits. | Retain useful comparison practices; exclude its numeric rubric, runner dependencies and persistence hook from the runtime. |

No source tooling was benchmarked or executed. The assessments above come from
source inspection, including explicit set-comparison limitations in the CLI's
implementation, documentation and tests. Package integrity checks and behavioural
evaluation are separate kinds of evidence.

## Inspection scope

Paths below are relative to the pinned repository; grouped paths identify the
files read or, where stated, indexed.

- **Blader:** `SKILL.md`, `README.md`, `LICENSE`, `AGENTS.md`,
  `.claude-plugin/{plugin,marketplace}.json`, `agents/openai.yaml`,
  `scripts/validate-package.py`, `.github/workflows/validate.yml`. These are all
  tracked files in the snapshot.
- **Stop-slop:** `SKILL.md`, `README.md`, `LICENSE`, `CHANGELOG.md`,
  `references/{phrases,structures,examples}.md`. These are all tracked files in
  the snapshot; it includes no executable tooling.
- **Aboudjem, editorial material:** `skills/humanizer/{SKILL,README}.md`,
  `skills/humanizer/references/{patterns,patterns.zh,always-on-templates}.md`,
  `skills/humanizer/evals/evals.json`, `README.md`, `AGENTS.md`,
  `docs/{science,comparison}.md`.
- **Aboudjem, licences and tooling:** `LICENSE`, `cli/LICENSE`,
  `CODE_OF_CONDUCT.md`, `cli/{README.md,package.json,index.js}`,
  `cli/lib/{facts,metrics,report,scan,tokenize,vocabulary}.js`,
  `cli/test/facts.test.js`; test names were indexed in
  `cli/test/{cli,metrics}.test.js`. Also inspected
  `.claude-plugin/{plugin,marketplace}.json`,
  `.copilot-plugin/plugin.json`, `.cursor-plugin/plugin.json`,
  `.github/actions/humanizer-gate/action.yml`,
  `.github/workflows/{ci,release,no-ai-attribution}.yml`,
  `.pre-commit-hooks.yaml`, `tools/{demo.sh,demo.tape}`.
- **Aboudjem, inventory only:** the tracked-file listing and a repository-wide
  licensing/attribution text search covered the remaining tree. Translated
  READMEs, site content, dependency locks and visual assets were not exhaustively
  reviewed; none is imported.
- **Ayghri:** `skills/i-have-adhd/SKILL.md`, `README.md`, `LICENSE`,
  `evals/{README,RESULTS,rubric}.md`, `evals/cases.jsonl` and
  `hooks/always-on.mjs`; evaluation prompt construction in `scripts/judge.py`
  and relevant runner configuration and measurement logic in `scripts/run_evals.py`.
  Remaining tracked paths were inventoried, not exhaustively reviewed. No source
  scripts, installers, hooks or model runners were executed.

## Licensing boundary

The four root MIT licence files are preserved byte-for-byte under `licenses/`,
with attribution in [NOTICE.md](../NOTICE.md). The Aboudjem CLI licence duplicates
its root MIT notice; its code is not included.

Both Humanizer repositories point to Wikipedia material. Wikimedia's current
[licensing terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content)
require respecting the underlying text licences, including attribution and
share-alike conditions. A repository's MIT label does not replace those terms.
Human Writing includes no Wikipedia-derived catalogue, quotations or adapted
upstream examples.

The [HC3 dataset card](https://huggingface.co/datasets/Hello-SimpleAI/HC3/blob/main/README.md)
declares CC BY-SA 4.0 with stricter source-dataset terms retained where applicable.
The Aboudjem references state that they did not reuse its unlicensed detector
code. Human Writing imports neither the corpus nor that code. Its separately
attributed Contributor Covenant document, other research text, third-party
dependencies and assets are likewise excluded. All package prose, examples and
evaluation fixtures are newly authored; the preserved MIT notices recognise
the upstream editorial work.
