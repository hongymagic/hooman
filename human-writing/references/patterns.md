# Patterns

This file explains the checker's findings. After a check, read the entry for
each rule ID reported. Each entry gives what the pattern looks like, what it
costs the reader, the fix and when to keep it. Specimens are invented and sit
in quotations or code so the checker skips them. Do not read the file before
drafting: [forms.md](forms.md) and [exemplars.md](exemplars.md) are the
drafting references, and a list of phrases to avoid is a poor model to write
from.

Meaning comes first. A pattern is a reason to look at a passage, and the fix is
whatever the passage was missing: usually a fact, a named actor or the point
itself. If the source has no such fact, write the simpler sentence or flag the
gap. Never invent one.

Remove the dressing and keep the claim. Before cutting a clause, ask what it
asserts. A claim is something the reader could repeat to someone else: `women
voted despite decades of exclusion` is one, and `a testament to resilience` is
not. Purple description often wraps real claims about who did what, how many
and despite what. Put those in plain words. Delete only what asserts nothing.

Act on an `error` finding at one sighting. A `review` finding is weak alone: one
stock word or one contrast is ordinary writing, and several in a passage are a
habit. Accumulation findings count those habits.

## Staging

The sentence signals that something matters and adds nothing the reader can use.
These are the most persistent habits in current model prose.

### Contrast frames: `staging.contrast`, `staging.contrasts`

> It's not a dashboard. It's a foundation for trust.
>
> The hard part wasn't the pipelines. It was the secrets.
>
> The fix is a config file, not another comment.

The negative half names a view nobody held, so the positive half sounds larger.
State the positive claim. The frame also splits across sentences, stacks several
negatives before the reveal and trails off in a clipped tail (`, no guessing`).

Sometimes the negative half is true and relevant: the author did believe it, or
the reader does. Then the fact stays and only the staged reveal goes.

> It wasn't flaky. It was a real race condition.

becomes

> The test we had written off as flaky was failing on a real race condition.

Keep the frame itself when both halves carry information the reader needs side
by side:

> The cache stores responses for 60 seconds, not 60 requests.

Removing one form invites another. After an edit, look for the same move made
with `rather than`, `instead of`, `more than just` or `less about`.

### Run-ups and announcements: `staging.scene`, `staging.announcement`, `staging.runup`

> In today's fast-paced digital world, managing invoices matters more than ever.
>
> It is worth noting that the export runs nightly.
>
> Here's the thing. Let's dive in.

The writer announces a point before making it. Cut the announcement and keep the
information. With a brief that supports it, the first specimen becomes:

> Export this month's invoices as a CSV from the Billing page.

Launch-voice openers belong here too: `We are thrilled to announce`, `Whether
you are a founder or an engineer`. Lead with the news and name the audience the
brief names. Keep an opening the piece depends on, such as a scene in a personal
essay.

### Reveals: `staging.reveal`

> The result? Builds take seven minutes.
>
> The headline number: seven minutes.

A question or label promises a payoff and delays it. Give the fact. Keep a
question the reader is asking, such as what happens when a worker crashes after
the write.

### Concessions and foils: `staging.concession`, `staging.strawman`

> None of this means style is unimportant.
>
> Some might argue the cache is wrong. While everyone else debated, we shipped.

The text answers an objection nobody raised or beats an opponent it invented. In
late 2026 the first specimen opened a paragraph in every opinion piece three
Claude models wrote for the calibration set. Say what does hold. Keep an
objection that someone made, attributed and answered in full.

### Depth and importance labels: `staging.depth`, `staging.signpost`

> At its core, the real question is trust. That distinction matters.
>
> Symmetry is the language of trust.

An ordinary point is dressed as a hidden truth, or a label tells the reader a
fact is important. Replace the saying with the claim it gestures at, and show
importance with the consequence: what breaks, costs or changes.

### Closers: `staging.closer`

> In conclusion, the future looks bright.
>
> So the next time you open a pull request, start with the design.

The ending repeats the piece or reaches for uplift. End on the last concrete
fact. Keep a closing line that adds a next step, a date or a decision.

## Rhythm

A shape is applied whether or not the meaning has it.

### Fragments, punch lines and negation chains: `rhythm.fragments`, `rhythm.closers`, `rhythm.negation`

> It had no preference for symmetry. No aesthetic prior. No nostalgia.
>
> Caching cuts repeat work. That is the real win.

Clipped beats pose as emphasis. Fold them into a sentence that makes a claim.
People write short closing lines too, and matched human text has more fragment
runs than model text, so judge the passage: one that lands a new fact stays.
This is also what careless de-slopping produces. Do not chop sentences to vary
rhythm.

### Question volleys: `rhythm.questions`

> Does this belong here? What happens when it changes? Who debugs it at night?

Stacked questions perform curiosity. Keep the one the reader is asking and
answer it, or state the claims. When the questions are the content, such as a
checklist a reviewer should run through, keep them and consider a list.

### Threes and pairs

No rule ID. Lists of three and mirrored sentence pairs sound complete whether
or not the content has three parts or two sides. Count the real items and write
that many. Three true items stay three.

### Dashes and uniform sentences: `rhythm.dashes`, `rhythm.uniform`

Many writers use dashes freely and current models use fewer than many editors,
so their number is evidence of nothing and no reason to restyle an author. The
checker flags only a sentence with three, which is hard to follow whoever wrote
it. In a draft that fails on other grounds, a dash at every join can be the
model skipping the choice of how two clauses relate; there, choose a full stop,
comma, colon or brackets.

Sentences of one length read like a recitation. Let the content set the length.
The repair is never a quota of short sentences.

### Repeated sentence: `rhythm.repeat`

An adjacent sentence says the same thing in the same words. Remove it or supply
what the second one was meant to add.

## Inflation

The fact underneath is usually sound. Keep it and remove the dressing. The risk
in this family is cutting too much.

### Significance: `inflation.significance`

> The library stands as a testament to open collaboration, marking a pivotal
> moment in the evolving landscape of tooling.

A routine event is said to mark a turning point or prove a legacy. State what
happened. Phrases such as `plays a key role` are ordinary in academic prose, so
they are advisory: say what the role is when you know.

### Stock vocabulary and clusters: `inflation.vocabulary`, `inflation.cluster`

One stock word is weak evidence of anything. People write `landscape` and
`pivotal`, and models move on from each list within a generation: `delve` and
`tapestry` mark 2023 and 2024 text and are nearly absent from 2026 models. So no
single word blocks. A cluster does: four or more stock or overused words within
a hundred, counting plain ones such as `crucial`, `comprehensive` and `enhance`
that are never reported singly. Rewrite the passage in plain terms. Do not swap
each word for a synonym, which only moves the habit to the next list.

### Emphasis and sincerity words: `inflation.intensifier`

`Genuinely`, `truly`, `quietly`, `deeply committed`. The claim should be strong
without help. Cut the word or say what makes the claim strong. `Actually` and
`really` are ordinary speech and are left alone.

### Is and has: `inflation.copula`

> The gallery serves as an exhibition space and boasts four rooms.

Use `is` and `has`. Keep `serves as` for a real role, such as a person serving
as chair.

### Trailing -ing clauses: `inflation.tail`, `inflation.tails`

> The team shipped the fix on Friday, highlighting its commitment to quality.

A participle clause is bolted onto a fact to tell the reader what it means. In
the 2024 calibration texts these ran at about seven times the matched human
rate. Give the second idea its own verb and subject if the source supports it,
and cut it if not. Reporting clauses such as `, suggesting that` are normal in
science writing; the blocking rule fires on recurrence.

### Stacked hedges: `inflation.hedge`

> The change could potentially help in some cases.

Keep the one qualification that carries the real uncertainty, with its
condition attached. Never upgrade a hypothesis to a result.

### Register

No rule ID. Model prose runs longer, more Latinate and more nominalised than
people writing in the same genre: `the utilisation of` for `using`, `provides
facilitation of` for `helps`. Prefer the plain word and the verb.

## Pitch

The text sells its subject where it should describe it. These habits are older
than language models: product pages, launch posts and some documentation have
them. Reference writing from before 2020 mostly does not. In 103 pinned human
documents, 20 of 687 headings addressed or invited the reader, about 1 in 34.
In 68 drafts from 2026 models, 25 of 159 did, about 1 in 6.

### Headings: `pitch.heading`, `pitch.headings`, `formatting.instructions`

> Try the checker
>
> Why Harbour
>
> Works where you work
>
> Passwords your whole team can share, safely.

A heading invites, teases, addresses the reader or reads as a slogan. A heading
is a label: a noun phrase that names what the section holds. The four above
become:

> Checker
>
> Comparison with other managers
>
> Supported platforms
>
> Shared vaults

Take the label from the document's form in [forms.md](forms.md) where it has
one. `pitch.headings` blocks when three or more headings pitch and they are a
quarter of the document's headings.

`formatting.instructions` is advisory. It reports two or more subheadings that
give an instruction, such as `Install the CLI`. Older manuals label the section
`Installation` and keep the instruction in the steps. Keep instruction headings
in a procedure whose headings are its steps, and where the house style sets
them. Keep a question heading in a list of questions readers ask.

### Benefits: `pitch.benefit`

> The importer helps you move accounts in minutes, so you can focus on what
> matters.

The sentence names what the reader gains and leaves out what the thing does.
State the mechanism and the figure:

> The importer copies an account and its history. A 2 GB account takes about
> four minutes.

If the source has no figure, state the mechanism alone. Keep a benefit the
brief supplies as a fact with its evidence, such as a measured time saving.
`This flag lets you skip validation` is ordinary in reference writing and is
advisory; `This flag skips validation` is shorter.

### Calls: `pitch.call`

> Ready to move your team? Get started today.

Give the next step once, as an instruction with its command or link. Keep one
call to action where the brief asks for one.

### Praise words: `pitch.praise`

`Seamless`, `powerful`, `intuitive`, `world-class` and their kin praise without
describing. Name the capability or give the measurement. Keep technical senses,
such as a `robust` estimator or `unlocking` an account.

## Particulars

Rules: `particulars.share`, `particulars.run`.

A particular is something a reader could check or act on: a figure, a name, a
date, a command, a link, a quotation. The checker counts the sentences that
carry one. In READMEs and reference documents pinned before 2020 the median is
72 per cent and none falls below 35. In a 2024 model's continuations of
human-written documents the medians are 23 to 43 per cent, against 50 to 77 for
the human originals.

`particulars.share` reports a document of twelve or more sentences in which
fewer than 35 per cent carry one. `particulars.run` reports four consecutive
sentences in a paragraph or list item that carry none.

> The system keeps the work moving for the people who rely on it. It brings the
> pieces together in a way that feels natural.

For each sentence reported, find what it refers to in the source and say that:
the number, the name, the command. If the source has nothing behind the
sentence, cut it. Never supply a particular the source lacks.

Both findings are advisory and never count towards `density.signals`. The count
is a proxy. A definition such as `tmux is a terminal multiplexer` carries no
particular the checker can see, and instructions, principles and personal
narrative run lower than reference writing. Keep a general sentence that
states a rule, a definition or a judgement the reader needs.

## Formatting

Rules: `formatting.labels`, `formatting.bold`, `formatting.titlecase`,
`formatting.instructions`, `formatting.rules`, `formatting.hashtags`,
`formatting.emoji`.

These findings are always advisory, because the same mark is decoration in one
document and structure in another. Decoration on every item is the habit: bold
scattered through sentences, a rule between every section, emoji as bullets, a
slogan after each heading, a block of hashtags. Remove what carries no
information. Keep what a skimming reader uses: the times in a timeline, the
labels in a status report, the one warning that must not be missed.

Keep formatting the format calls for: a definition list, steps a reader follows
in order, bold on the one action a skimming reader must not miss. Keep an
author's consistent style too. Title case throughout a human-written handbook
is a house style, and changing it is restyling; change heading case only where
it comes with other marks of a model draft, such as slogan subtitles. A slogan
after a heading's colon is dressing; a subtitle that names the content is a
label. Turn a list back into prose only when the request allows restructuring.

## Leftovers

Rules: `leftovers.chat`, `leftovers.courtesy`, `leftovers.cutoff`,
`leftovers.markup`, `leftovers.placeholder`, `leftovers.reasoning`,
`leftovers.meta`.

Text that was never meant for this reader: an assistant's greeting, praise or
offer of more help; a statement about what the model knows or could not find; a
guess filling that gap; citation tokens and tracking parameters pasted from a
chat tool; an empty placeholder; reasoning scaffolds; a sentence about the
document or the edit where the subject should be.

> This function was added to replace the earlier loop.

Describe the thing as it is. History belongs in a changelog or commit message.
Remove the wrapper and keep the content. Keep a sign-off the relationship calls
for: letters ended with courtesies long before chatbots. Watch for working
shorthand too: a label coined during the task that the reader never saw defined.

## Evidence

Rules: `evidence.numbers`, `evidence.attribution`.

A finding here asks for verification. It accuses nobody. Check a figure's
source, scope and measurement. Five customers reporting easier searches do not
establish faster searches, and a staging result does not establish production
behaviour. For `Experts say` or `Studies show`, name the source and what it
found, or cut the claim. Do not drop the attribution and keep the claim as fact.

## Wrong reader

No rule ID. A model writes for a stranger. In a reply, the reader wrote half the
thread: lead with the decision and keep only the reasoning that could change
their mind. `Whether you are X or Y` addresses everyone and so nobody. Pick the
audience the brief names.

## Interface copy

Rules: `interface.figure`, `interface.filler`, `interface.heading`,
`interface.shorthand`, `interface.pair`. They run only under `--profile
interface`, on one string per line, and all are advisory.

- `interface.figure`: a figure of speech stands where a number or a thing could
  be. State the number or name the thing.
- `interface.filler`: filler such as `simply`, `easily`, `successfully`,
  `please note` or `oops`. Cut the word. Keep it where it changes the meaning.
- `interface.heading`: a label phrased as a clause or a two-word question.
  Name what the section holds.
- `interface.shorthand`: a string that ends on a bare number. Say what the
  number counts, with its noun and unit.
- `interface.pair`: two clipped sentences in one string. State the fact once
  in one sentence.

Keep the product's own word for a thing even when a rule reports it. The entry
for interface copy in [forms.md](forms.md) gives the full standard.

## Accumulation: `density.signals`

Six or more advisory findings at ten or more per thousand words block as a
group. That density is rare in the human calibration texts and usual in model
drafts. Evidence, formatting and particulars findings do not count towards it.

Every accumulation finding, this one and the contrast, cluster, trailing
clause and pitched heading counts, asks for a judgement on each instance. Fix the empty ones. Keep
those that meet the keep-condition above. If the count still blocks and every
remaining instance earns its place, pass `--allow` with that reason. Do not
delete sound sentences to bring a number down.

## Exceptions

These are not signs of anything, and editing them damages ordinary writing: one
dash, curly quotation marks, correct grammar, a formal or plain register, a
transition word, a single stock word, `is` and `has`, a short sentence that
carries a fact, first person, contractions. Also leave a watched phrase inside
a quotation, a title or a passage that discusses the phrase.

Keep what carries a voice unless it hurts the meaning: an odd specific detail,
mixed feelings, a dated reference, an aside, a deliberate fragment.

## Sources

The catalogue draws on Wikipedia's
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
on the skills and studies credited in the
[project README](https://github.com/hongymagic/hooman#credits), and on this
project's own calibration against dated human and model text.
