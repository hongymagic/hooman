# What the evidence says

Hooman 2.0 was rebuilt on 18 November 2026 from three kinds of source: other
skills and catalogues, published research, and measurements made for this
project. This page records which findings shaped the design. The measurements
are in the [validation notes](validation.md).

## Findings and what they changed

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
forbidden words. The first evaluation of this version showed the cost of
pushing too hard in the other direction: instructions strong enough to clear
the patterns also cut true claims. The catalogue now says what to keep in each
family, and the comparison lists sentences that left no trace.

## Open questions

- No study was found testing whether a second model family catches the first's
  habits. The separate model pass is optional for that reason.
- Evidence that listing banned phrases primes a model to use them is thin. The
  long lists live in the checker anyway, and the instructions describe families.
- No measured study of interface copy was found. That section rests on
  content-design standards and one product owner's review.
- The calibration measures the checker. It does not measure whether readers
  prefer the edits. The small evaluation in the validation notes used a model
  judge, which was too noisy to rank the versions and preferred unconstrained
  rewrites on voice. A study with human readers has not been done.

## Sources

Research:

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
