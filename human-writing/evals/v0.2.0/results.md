# Phrasing refinement evaluation — v0.2.0

Run on 22 September 2026. Compared the released v0.1.1 core (969 words) with
v0.2.0 (1,184 words). The change adds clearer boundaries around empty rhetorical
devices and guidance on plain phrasing. Both conditions preserved the material
facts in this sample. The results do not establish a general quality improvement.

## Method

Two fresh delegated model sessions each received the same 11 requests from
[cases.md](../cases.md): C03, C05, C08, C13 and C15–C21. Each received its assigned
core, without optional examples, research notes, outcome criteria or the other
condition's outputs. This compares two skill versions. The earlier
[unassisted/assisted evaluation](../results.md) and
[structure refinement comparison](../v0.1.1/results.md) remain separate records.

Sessions used the host's inherited model and settings, with no overrides. The exact
model identifier and sampling parameters were not exposed in the run record.
Normal host instructions remained present; this was not an isolated provider API
experiment. Each condition produced one batch, with one answer per request and
no retries or selection of preferred answers. Raw outputs are
[previous.md](previous.md) and [revised.md](revised.md). Case-label headings are
aggregation wrappers, not part of the requested prose.

The implementing agent read the outputs and checked their meaning against the
requests. A fresh reviewer received the requests, criteria and anonymised outputs
only, without either core or the condition mapping. Labels alternated by case:
A was previous for C03, C08, C15, C17, C19 and C21; A was revised for the other
cases. These are model judgements, not a human-reader study or an authorship test.

## Observed outcomes

| Case | Factual preservation | Clarity, voice and unnecessary changes |
| --- | --- | --- |
| C03 ADR | Both retain the proposal, jargon, obligations and causal uncertainty. | Identical; neutral technical voice survives. |
| C05 personal writing | Both retain the events and exclude the sample's factual mistake. | Revised removes only the filler. Previous changes the opening verb and makes the ending punchier. Both fit the voice; revised makes the smaller edit. |
| C08 Korean | Both retain the schedule, expected status, payment restriction, order history and conditional notice. | Identical natural, polite Korean; no English pattern substitutions. |
| C13 prose preference | Both preserve every fact and the authored joke. | Identical to the supplied note; no diagnosis-based formatting imposed. |
| C15 contrast | Both preserve the optional setting, identifier, scope distinction and unchanged timeout. | Identical; remove the empty slogan while keeping the useful contrast. |
| C16 question and humour | Both keep the failure scenario, possible redelivery and idempotency requirement. | Identical; cut the generic opening and preserve the reader question and authored fragments. |
| C17 product copy | Both keep the counts, reported ease, absent measurements, plan restriction and beta date. | Same plain voice; only conjunction versus semicolon differs. No invented authority or performance claim. |
| C18 closing information | Both retain the strict threshold, prohibition and Thursday commitment. | Identical; remove the recap without losing distinct closing facts. |
| C19 effective prose | Both preserve technical wording and all instructions. | Previous is unchanged; revised adds a blank line before the list. The blind reviewer preferred exact formatting preservation here, while noting the spacing may aid Markdown rendering. Both retain the passive, adverb, dash and three entries. |
| C20 literal phrasing | Both preserve frontmatter, the quoted slogan, JSON, link target and unapproved status. | Identical; remove only the surrounding empty announcement. |
| C21 natural phrasing | Both preserve timing, recipient, approval dependency and notification commitment. | Both join related thoughts and use direct verbs. Revised uses a contraction and semicolon; previous is slightly more formal. Neither invents personality. |

Seven of the 11 answer pairs are textually identical. The clearest difference is
the smaller edit to the personal piece; most other differences are acceptable
stylistic choices. No material fidelity or requested-behaviour failure was observed.
That supports retaining these clarifications without claiming that the extra
instructions caused a measurable improvement.

The blind reviewer found both personal-writing versions defensible and no clear
overall preference. It recorded C19's extra blank line as a minor formatting
departure, without a substantive compliance failure. The implementing agent
considered that spacing useful for rendering. Neither judgement changes the
finding that this sample demonstrates no broad advantage for either version.

## Additional checks

Literal comparisons verified C20's exact frontmatter, quotation, JSON and link
target in both conditions, and the C15 identifier. C13 stayed unchanged. C19
stayed unchanged apart from the revised answer's list spacing. The revised core
used for generation matches the release source byte-for-byte. These checks
supplement semantic review; token preservation alone cannot establish fidelity.

An independent static review covered all 21 examples and the writing-source guide.
It caught an early example that implied a design had previously worked well and
that a booking type was newly introduced without either fact being supplied.
That example was corrected before final review. The final review found no
substantive fidelity issue. Netflix and Holman provenance was cross-checked
against the research notes; the reviewer did not independently reopen every post.

The core passed the standard skill validator. Both Claude source manifests passed
strict native validation. Version consistency, core length, runtime-resource
checks, source-byte preservation, archive integrity and reproducible builds passed.
Packaging checks establish distribution properties, not writing quality.

## Limits

This is a single-trial comparison on 11 selected cases in one host configuration.
Other cases were not rerun. The expanded examples were reviewed statically and
were not loaded in this comparison, so their behavioural contribution is untested.
The run does not establish automatic activation, long-document performance,
cross-model consistency or native ChatGPT/Claude GUI import. A model can still
overedit, miss factual drift or misjudge an author's voice.
