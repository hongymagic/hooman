# Structure refinement evaluation — v0.1.1

Run on 22 September 2026. Compared the released v0.1.0 skill (935 core words)
with the revised v0.1.1 skill (969 words). Both conditions met the substantive
outcomes in this sample; the comparison does not demonstrate a general improvement.

## Method

Two fresh delegated model sessions each received the same seven requests from
[cases.md](../cases.md): C03, C05, C06 and C11–C14. Each also received its assigned
skill, without optional references, case criteria, source research or other
outputs. This comparison is between two skill versions, unlike the original
[unassisted/assisted evaluation](../results.md).

Each session used the host's inherited model/settings, with no override. The exact
model identifier and sampling parameters were not exposed in the run record.
Normal host instructions remained present. Each condition generated one batch
with one response per request; there were no retries or selections of preferred
answers. Raw outputs are [current.md](current.md) and [candidate.md](candidate.md).
Case-label headings are aggregation wrappers, not part of the individual answers.

A fresh reviewer saw the tasks, outcome notes and anonymised outputs only. It did
not see either skill, the integration rationale or the condition mapping. The
mapping was A = revised and B = current. Labels were fixed across cases rather
than rotated, so this review does not remove possible position bias. The
implementing agent also inspected both sets. These are model judgements, not
human-reader studies, clinical evidence or scores of likely authorship.

## Observed outcomes

| Case | Preservation and fit | Editorial tradeoff |
| --- | --- | --- |
| C03 ADR | Both retain neutral register, structure, terminology and uncertainty. | Current adds blank lines after headings; revised retains source spacing. Substantive tie. |
| C05 personal voice | Both retain all events and exclude the sample's factual mistake. | Revised preserves the original ending. Current uses a defensible, punchier fragment. Revised makes the smaller edit. |
| C06 effective note | Both return it unchanged. | Exact tie. |
| C11 action email | Both retain recipient/deadline, pending approval, conditional ordering, optional workshop and recording commitment. | Revised adds topic labels; current uses paragraphs with bold times. Revised repeats the deadline in its label and sentence; either presentation is reasonable for the task. |
| C12 procedure | Both keep prerequisites, exact commands, administrator boundary, handoff, production prohibition and unknown duration. | Revised separates the prohibition; current labels commands more concisely. No permissions or completeness regression observed. |
| C13 prose preference | Both leave the connected prose and humour unchanged, without added headings or tasks. | Exact tie; neither imposes a diagnosis-based template. |
| C14 partial success | Both retain passed checks, the failure/location, unknown cause, no verified fix and Noor's commitment. | Minor punctuation and sentence-length differences. Neither invents a diagnosis or time estimate. |

Deterministic checks also passed in both sets: all C12 inline literals in their
original order, exact unchanged C06 and C13 notes, and the C14 file/line identifier.
Semantic preservation was assessed by reading, not inferred from token presence.

The revised rule is retained as a compact clarification of the requested editorial
policy. There was no observed material failure to address with another runtime
rule. These outputs support compatibility on these cases, not a claim that the
34 additional words caused a measurable quality gain.

## Limits and package checks

This is a seven-case, single-trial comparison within one host configuration. The
other original cases were not rerun. It does not establish cross-model reliability,
long-document behaviour, automatic activation or an accessibility outcome for any
reader population. Native ChatGPT/Claude GUI imports were not tested.

The updated core passed the standard skill validator. Version/manifest consistency,
archive integrity, source-byte preservation and reproducible package builds passed.
The new upstream MIT notice was compared byte-for-byte with the inspected source.
Those checks establish package properties, not writing quality.
