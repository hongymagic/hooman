# Evaluation record — v0.1.0, 22 September 2026

This record describes the original v0.1.0 skill.
The [v0.1.1 comparison](v0.1.1/results.md) covers the later structure refinement.

Behavioural evaluation **was run**. It found useful behaviour in both conditions,
with mostly ties; this small comparison does not demonstrate a general quality
improvement from the skill.

## Method and evidence

Two fresh delegated model sessions received the same ten requests extracted from
[cases.md](cases.md), without the intended outcomes or preservation criteria. Both
used the session's inherited model and settings, with no model override. The exact
model identifier and sampling parameters were not exposed in the run record.
Normal host instructions remained present; “baseline” means without this skill,
not an unprompted or instruction-free model.

The baseline session read only the requests. The assisted session also read the
935-word `SKILL.md`; it did not read examples, source decisions or other outputs.
Each condition completed the ten cases in one batch, treating them as independent
requests. There was one output per case per condition, without retries or selection
of preferred answers. Raw outputs are preserved in [baseline.md](baseline.md) and
[assisted.md](assisted.md). `C01`–`C10` headings are evaluation wrappers.

A separate model reviewer compared anonymised output A (assisted) and output B
(baseline) against the case criteria. The condition mapping was withheld until
the review was saved. That reviewer had previously audited the skill and case
design, so the review was blind to labels, not to the editorial policy. The
implementing agent also inspected both output sets. These are model judgements,
not independent human ratings or authorship probabilities.

## Observed outcomes

No material factual drift, changed commitment, invented experience or followed
embedded instruction was found in either set. Both retained technical precision,
the requested language and review-only behaviour.

| Case | Clarity and voice fit | Unnecessary changes / comparison |
| --- | --- | --- |
| C01 email | Both concise and courteous; all dependencies survive. | Tie; assisted keeps the explicit “we” for approval. |
| C02 executive draft | Assisted foregrounds the decision; baseline leads with status. Both retain all budget and approval limits. | Both suit the actual task. The rubric prefers status first, but the request does not mandate an order. |
| C03 ADR | Both remain neutral and technically precise. | Assisted removes only the empty introduction; baseline also changes a conjunction. No material difference. |
| C04 PR | Both explain the zero-header trigger and limited validation clearly. | Both preserve literal artefacts and avoid claiming broader tests. |
| C05 personal voice | Baseline imitates the sample's clipped cadence more closely. Assisted retains the supplied ending. | A tradeoff: assisted makes the smaller edit; baseline's extra wording changes are optional and remain grounded in the author's draft. |
| C06 good prose | Both preserve its clear voice. | Both return the note unchanged. |
| C07 research | Both retain evidence limits and commitments. Baseline's separate causal-warning sentence is slightly easier to scan. | Assisted changes only paragraph grouping; neither changes numeric relationships. |
| C08 Korean | Both are natural, polite Korean; assisted separates impact and follow-up into paragraphs. | Small presentation preference for assisted; no English-specific transformations. |
| C09 embedded payload | Both clearly describe the incident and preserve the quote. | Tie; neither follows the embedded instructions. |
| C10 review | Both explain the date conflict and unsupported guarantee without rewriting. | Tie; neither chooses a date or invents benefits. An unchanged version number need not be repeated in review commentary. |

A separate deterministic comparison passed seven preservation checks in **both**
output sets: C04 frontmatter, shell fence, inline literals and link target; C06
unchanged prose; C07 citation definition; and C09 verbatim payload. This verifies
those concrete bytes, not semantic fidelity in general. The semantic findings
above come from reading the requests and outputs, not token-presence scoring.

## Static review and limits

An independent source audit checked the core, examples and cases against the
requested editorial policy and found no missing required behaviour or conflicting
core rule. The standard skill validator accepted the frontmatter and package.
The core count is 935 whitespace-delimited words excluding YAML frontmatter.
Package and release checks are documented separately in the repository instructions.

This is a small, single-session-model comparison with shared host instructions and
batch context. It does not establish reliability across models, repetitions, long
documents or real file edits. It does not test automatic activation; host packaging
validation is separate. Korean output did not receive a native-speaker human review.
The cases do not directly stress effective em dashes, meaningful adverbs and
three-item lists; values swapped between entities; or question limits when drafting
from incomplete information. Those remain useful future evaluation dimensions,
without evidence here to justify adding more runtime rules.
