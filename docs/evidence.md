# Evidence

This page records the findings the design rests on and what each one changed.
Hooman 2.0 was rebuilt on 18 November 2026 from other skills and catalogues,
published research and this project's measurements. Version 3.0.0, on 21
November 2026, changed the method from avoiding patterns to writing in a plain
style from listed facts, after a second review of research and a measurement of older
human text. The measurements are in the [validation notes](validation.md).

## Method

**Older human text carries particulars, and model text carries fewer.** This
project counted the sentences that hold a figure, a name, code, a link or a
quotation. In READMEs and reference documents pinned before 2020 the median is
72 per cent and no document falls below 35. In 600 human-written documents from
the HAP-E corpus the medians are 50 to 77 per cent by register, and in a 2024
model's continuations of the same documents they are 23 to 43. In the 43
drafts from 2026 models long enough to count, of 68, the median is 41. The standard's rule on particulars, the
`particulars` findings and the list of facts written before drafting follow
from this.

**Older headings are labels.** In 103 pinned human documents, 20 of 687
headings invited, teased or addressed the reader and 7 gave an instruction. In
the 2026 model drafts, 25 of 159 pitched and 11 instructed. Manual pages and
RFCs use fixed noun labels. Style guides disagree: the Australian Government
Style Manual advises against questions as headings, Google's guide sets a bare
infinitive for tasks and a noun phrase otherwise, and Microsoft's asks for
headings that are "pithy". The skill uses labels, allows instruction headings
in procedures and reports them as advisory.

**Objective text measured as more usable.** Morkes and Nielsen had 51 people
use five versions of one website in 1997. Measured usability was 27 per cent
higher for the version in objective language than for the promotional
original, 58 per cent higher for the concise version and 124 per cent higher
for the version that was concise, scannable and objective. Microsoft's style
guide tells writers not to use `lets`, `allows` or `enables` for what a product
makes possible. The `pitch` findings follow from these.

**A sample steers style more than a description does.** Jemama and Kumar gave
five open models a statistical profile of an author's style, and the output
matched the author in 3 to 7 per cent of cases. With one paragraph by the
author it matched in 68 to 95 per cent, and with two in 91 to 100. Wang and
colleagues found that more demonstrations add little, that samples on one
topic do worse than varied ones, and that the output stays detectable as
model-written. The skill therefore ships passages of human writing, two to a
form on different subjects, and still measures the result.

**Naming a phrase can prime it.** Rana found that most violations of a
negative constraint were priming failures, and Mann and colleagues found a
rebound after "do not mention" instructions in most of nine models. Both are
preprints on small models. Anthropic's and OpenAI's prompting guides give the
same advice without data: say what to do. The skill states its standard as
positive rules, keeps phrase lists in the checker and has the model read the
pattern catalogue after a check, never before drafting.

**Writing from extracted facts is more faithful.** Zhang, Liu and Zhang found
that having ChatGPT extract sentences before summarising raised a factual
consistency score from 6 to 52 on one news set. Narayan and colleagues found
that a plan alone did not ensure faithfulness; dropping unsupported entities
from the plan did. The list of facts is therefore checked against the draft
with `compare.py --brief`, which reports what the draft added.

**Model edits drift, even small ones.** Abdulhai and colleagues found that
edits requested as grammar fixes changed meaning, raised adjectives by 40 to 87
per cent and cut pronouns by 31 to 56 per cent, against under 5 per cent for
human revisers. Van Nuenen found the same normalising in rewrites of personal
narrative, and Laban and colleagues measured an average loss of 25 per cent of
a document's content in long delegated editing. Hence the order of an edit:
delete first, rewrite only the sentences that fail and do not paraphrase the
rest.

**Deletion keeps meaning better than rewriting, at a cost.** Ladhak and
colleagues showed that the faithfulness gains of summarisation methods came
mainly from copying more of the source. Zhang, Wan and Bansal found a broken
reference or a similar fault in 30 per cent of extractive summaries. The
procedure adds a check that each pronoun still has its referent after a cut.

**Density has a readable limit.** In Adams and colleagues' Chain of Density
study, human summaries held 0.151 entities per token and plain GPT-4 summaries
0.122, and readers preferred about 0.15 to the densest version. The particulars
target is the human range, and the checker reports a low share, never a high
one.

**Fixed forms rest on convention.** The section labels in
[forms.md](../human-writing/references/forms.md) are quoted from their sources.
No controlled study was found showing that a manual page, a decision record or
an inverted pyramid helps readers; the nearest evidence is for structured
abstracts. The forms are defaults that a house template or an author's
structure overrides.

## Patterns

**Word lists date within a model generation.** Kobak and colleagues traced
model-assisted writing in biomedical abstracts through excess style words such
as `delve`. Thelwall and Kousha found many of those terms falling in 2025 full
texts while quieter ones kept rising. Wikipedia's catalogue now lists AI
vocabulary by model era, and sloptells records `delve` and `tapestry` as absent
from current models. People have also adopted the words. So no single word
blocks, the stock list is reviewed with each calibration, and words count
mainly in clusters.

**Structure outlasts vocabulary.** Reinhart and colleagues found grammatical and
rhetorical differences between model and human text that persist across model
sizes and are larger for instruction-tuned models. On their corpus this project
measured trailing `-ing` clauses at about seven times the human rate. Zamaraeva
and colleagues found `rather than` at seven times its 2019 rate in 2026 NLP
papers, and found that reward models favour the construction. The staging and
trailing-clause rules therefore lead the catalogue, and recurrence blocks where
a single use does not.

**The em dash is no longer evidence.** Wikipedia moved em dash overuse to its
historical indicators in 2026, and sloptells publishes it as a negative result:
acclaimed human prose uses as many. The checker reports dash density as a
statistic and keeps one advisory rule, for three dashes in a single sentence.

**Readers who use these models notice.** Jakesch, Hancock and Naaman showed that
lay readers judge by flawed heuristics and perform near chance. Russell,
Karpinska and Iyyer found that people who often write with these models detect
their text accurately, citing vocabulary first and then structure, formality and
originality. The skill is written for that second reader.

**Rewrites change facts.** Wang, Zhu and Chen audited eleven commercial
humanising tools and found a number, date, name or quotation changed or dropped
in 35 to 65 per cent of the documents that contained one. Mohamed and colleagues
showed that repeated generation distorts information, and Sourati and
colleagues that model rewriting narrows the variety of human prose. Hence the
comparison script, the rule against inventing detail, the limit of two editing
passes and the instruction to edit sentences that fail and leave the rest.

**Editors mostly remove what adds nothing.** Chakrabarty, Laban and Wu had
professional writers edit model paragraphs and derived a taxonomy that includes
cliché and unnecessary exposition. The skill's first test for a sentence is
whether it gives the reader something new.

**Pattern checks misfire on people.** Liang and colleagues showed detectors
flagging non-native English writers. This project's own human corpus fails the
gate between 1.5 and 17 per cent of the time, mostly on filler that people
write too. The checker is therefore described as an editing aid and never as a
detector, and it reports counts where version 1 reported a score.

**Prohibition is a blunt tool.** Paech and colleagues found that banning tokens
outright became unusable after about two thousand patterns, while backtracking
past an unwanted string suppressed four times as many and kept quality. That
favours checking a draft and rewriting the passage over a longer list of
forbidden words. In the first evaluation of version 2.0, instructions strong
enough to clear the patterns also cut true claims. The catalogue now says what
to keep in each family, and the comparison lists sentences that left no trace.

## Open questions

- No study was found testing whether a second model family catches the first's
  habits. The separate model pass is optional for that reason.
- No controlled test of samples against rule lists on prose was found, and none
  showing that reporting counts back to a model improves its next draft.
- The particulars count and the heading rules are this project's own. They are
  measured on public corpora and have not been replicated.
- No measured study of interface copy was found. The interface copy entry in
  forms.md rests on content-design standards and one product owner's review.
- The calibration measures the checker. It does not measure whether readers
  prefer the edits. The small evaluation in the validation notes used a model
  judge, which was too noisy to rank the versions and preferred unconstrained
  rewrites on voice. A study with human readers has not been done.

## Sources

Research on method:

- Morkes and Nielsen, [Concise, SCANNABLE, and Objective: How to Write for the Web](https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/)
- Jemama and Kumar, [How Well Do LLMs Imitate Human Writing Style?](https://arxiv.org/abs/2509.24930)
- Wang et al., [Catch Me If You Can? Not Yet: LLMs Still Struggle to Imitate the Implicit Writing Styles of Everyday Authors](https://arxiv.org/abs/2509.14543)
- Rana, [Semantic Gravity Wells: Why Negative Constraints Backfire](https://arxiv.org/abs/2601.08070)
- Mann et al., [Don't Think of the White Bear: Ironic Negation in Transformer Models Under Cognitive Load](https://arxiv.org/abs/2511.12381)
- Zhang, Liu and Zhang, [Extractive Summarization via ChatGPT for Faithful Summary Generation](https://arxiv.org/abs/2304.04193)
- Narayan et al., [Planning with Learned Entity Prompts for Abstractive Summarization](https://arxiv.org/abs/2104.07606)
- Abdulhai et al., [How LLMs Distort Our Written Language](https://arxiv.org/abs/2603.18161)
- van Nuenen, [Voice Under Revision: Large Language Models and the Normalization of Personal Narrative](https://arxiv.org/abs/2604.22142)
- Laban et al., [LLMs Corrupt Your Documents When You Delegate](https://arxiv.org/abs/2604.15597)
- Ladhak et al., [Faithful or Extractive? On Mitigating the Faithfulness-Abstractiveness Trade-off in Abstractive Summarization](https://arxiv.org/abs/2108.13684)
- Zhang, Wan and Bansal, [Extractive is not Faithful: An Investigation of Broad Unfaithfulness Problems in Extractive Summarization](https://arxiv.org/abs/2209.03549)
- Adams et al., [From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting](https://arxiv.org/abs/2309.04269)

Forms and style guides:

- [man-pages(7)](https://man7.org/linux/man-pages/man7/man-pages.7.html) and the [RFC style guide](https://www.rfc-editor.org/rfc/rfc7322)
- Nygard, [Documenting architecture decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- Google, [Example postmortem](https://sre.google/sre-book/example-postmortem/) and [Headings and titles](https://developers.google.com/style/headings)
- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Pope, [A note about Git commit messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
- Australian Government Style Manual, [Headings](https://www.stylemanual.gov.au/structuring-content/headings)
- Microsoft Writing Style Guide, [let, lets](https://learn.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/l/let-lets) and [Headings](https://learn.microsoft.com/en-us/style-guide/scannable-content/headings)
- Anthropic, [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- OpenAI, [Best practices for prompt engineering with the OpenAI API](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api)

Research on patterns:

- Kobak et al., [Delving into LLM-assisted writing in biomedical publications through excess vocabulary](https://arxiv.org/abs/2406.07016)
- Thelwall and Kousha, [Have LLM-associated terms increased in article full texts in all fields?](https://arxiv.org/abs/2604.07565)
- Reinhart et al., [Do LLMs write like humans? Variation in grammatical and rhetorical styles](https://arxiv.org/abs/2410.16107), with the [HAP-E corpus](https://huggingface.co/datasets/browndw/human-ai-parallel-corpus)
- Zamaraeva et al., [The rise of antithesis in NLP papers](https://arxiv.org/abs/2610.10092)
- Jakesch, Hancock and Naaman, [Human heuristics for AI-generated language are flawed](https://doi.org/10.1073/pnas.2208839120)
- Russell, Karpinska and Iyyer, [People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text](https://arxiv.org/abs/2501.15654)
- Wang, Zhu and Chen, [Humanized but Still True? Auditing Facts and Detection in AI-Text Humanizers](https://arxiv.org/abs/2611.00359)
- Mohamed et al., [LLM as a Broken Telephone: Iterative Generation Distorts Information](https://arxiv.org/abs/2502.20258)
- Sourati et al., [The shrinking landscape of linguistic diversity in the age of large language models](https://www.nature.com/articles/s41562-026-02550-0)
- Chakrabarty, Laban and Wu, [Can AI writing be salvaged?](https://arxiv.org/abs/2409.14509)
- Liang et al., [GPT detectors are biased against non-native English writers](https://arxiv.org/abs/2304.02819)
- Paech et al., [Antislop: A Comprehensive Framework for Identifying and Eliminating Repetitive Patterns in Language Models](https://arxiv.org/abs/2510.15061)

Catalogues and skills:

- Wikipedia, [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [sloptells](https://sloptells.com/), [tropes.fyi](https://tropes.fyi/directory) and Simon Willison's [LLM cliché highlighter](https://tools.simonwillison.net/llm-cliche-highlighter)
- Graphite, [AI Tells](https://graphite.io/research/ai-tells)
- [blader/humanizer](https://github.com/blader/humanizer), [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) and [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)
