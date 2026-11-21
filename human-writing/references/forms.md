# Forms

Each kind of document below has a form that was settled before language models.
Find the kind you are writing and use its labels, in its order. Leave out a
section that has nothing to report. A house template or the structure an author
already chose outranks these forms: when editing, keep the author's sections and
retitle only a heading that is not a label.

The labels are quoted from the sources named. The forms are conventions. Their
communities document them, and the evidence that they help readers is long use
more than experiment.

## README

1. Name, then one sentence that says what the project is, in under 120
   characters: `curl is a command-line tool for transferring data specified
   with URL syntax.`
2. `Description`, if one sentence is not enough: what it does, on what input,
   with what result.
3. `Requirements`
4. `Installation`
5. `Usage`: the first command that works, with its output.
6. `Options` or `Configuration`
7. `Limits`: what it does not do.
8. `Contributing`
9. `Licence`

In 38 READMEs and reference documents pinned before 2020, headings have a
median of two words and 93 per cent have four or fewer. The commonest are
`Contributing`, `License`, `Installation`, `Documentation` and `Build
instructions`. The
[standard-readme specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
sets `Background`, `Install`, `Usage`, `API`, `Contributing` and `License`.

## Reference page

The Unix manual page, from
[man-pages(7)](https://man7.org/linux/man-pages/man7/man-pages.7.html): `NAME`,
`SYNOPSIS`, `DESCRIPTION`, `OPTIONS`, `EXIT STATUS`, `ENVIRONMENT`, `FILES`,
`NOTES`, `BUGS`, `EXAMPLES`, `SEE ALSO`. `NAME` holds the name and a one-line
description. `DESCRIPTION` says what the program does in the present tense and
the third person. Each option is one entry: the option, then what it does.

- Use one term for one thing. A second word reads as a second thing.
- Describe current behaviour. What it replaced belongs in the changelog.
- Tables, lists and the passive with an unknown actor are at home here.

## Procedure

A how-to has a title that names the task, a `Prerequisites` section and numbered
steps. Each step is one action in the imperative, followed by the result the
reader should see. A warning comes before the step it applies to. Step headings
may be instructions, such as `Create the bucket`; the
[Google developer documentation style guide](https://developers.google.com/style/headings)
uses the bare infinitive for tasks and a noun phrase for everything else.

## Specification or proposal

From the [RFC style guide](https://www.rfc-editor.org/rfc/rfc7322): `Abstract`,
`Introduction`, `Terminology`, the body, `Security Considerations`,
`References`. The abstract stands alone: a reader of nothing else learns what
the document specifies.

## Decision record

From
[Michael Nygard's 2011 format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions):
`Title`, `Status`, `Context`, `Decision`, `Consequences`. One or two pages.
`Context` states the forces as facts. `Decision` begins "We will". `Consequences`
lists what becomes easier and what becomes harder.

## Message

Emails, memos, chat replies and review comments. The main point comes first.
The US Army's correspondence regulation, AR 25-50, calls this the bottom line up
front and adds sentences of about 15 words and paragraphs of no more than ten
lines.

1. The answer, the decision or the request.
2. The fact the reader lacks, with any link they need to act.
3. What happens next, who does it and by when.

A short message has no headings, bullets or bold. Do not restate the reader's
question or summarise their own work back to them. Keep the courtesy the
relationship calls for.

## Status report

`Decision needed`, with its deadline and cost, when there is one. Then
`Progress` against the target, as a figure. Then `Risks`, each with its
consequence and owner. Then `Next steps`, with dates.

## Incident report

A notice to customers states the impact, the current state, what the reader
must do or that nothing is needed, and when the next update comes. Times carry a
zone and figures a unit. One plain apology is enough when one is owed.

A postmortem follows the
[Google SRE example](https://sre.google/sre-book/example-postmortem/):
`Summary`, `Impact`, `Root Causes`, `Trigger`, `Resolution`, `Detection`,
`Action Items`, `Lessons Learned`, `Timeline`. Facts and analysis sit in
separate sections, as in an NTSB accident report: `Factual Information`,
`Analysis`, `Conclusions`, `Recommendations`.

## Change description

A commit message, after
[Tim Pope's 2008 note](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html):
a capitalised summary of 50 characters or fewer in the imperative, a blank
line, then a body wrapped at 72 characters that gives the reason.

A pull request: `Summary` of what changes for a user or caller, `Reason`,
`Verification`, and `Risks` when there are any. It does not narrate the diff or
the session that produced it.

A changelog, from [Keep a Changelog](https://keepachangelog.com/en/1.1.0/):
`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`, under a
heading for each version and its date.

A code comment explains a constraint the code cannot show.

## Research report

`Introduction`, `Methods`, `Results`, `Discussion`. Results are stated before
they are interpreted, and a limit of the method is stated with the result it
affects.

## Essay or post

No fixed form. State the position in the first paragraph, support it with what
the author supplied and end on the last point. The position comes from the
brief or the author's sample; do not manufacture a stance, an anecdote or a
reaction. A social post has no heading and no block of hashtags. When editing
one, a closing question is the author's choice.

## Product description

Say what the product is, what it does, what it runs on, what it costs and what
it does not do, each with the evidence the brief supplied. Section labels name
their content: `Features`, `Platforms`, `Security`, `Pricing`. Add no
statistic, customer, guarantee, tier or time saving the brief lacks; check the
draft against the brief with `compare.py --brief`.

When the brief asks for promotional copy, the same facts apply and the
headings may sell. Run the checker with an allowance that says so:
`--allow "pitch.headings=Landing page"`.

## Interface copy

Labels, headings, buttons, helper text, empty states and error messages. Each
string is read mid-task, beside the control or figure it describes.

- A heading is a label. `Time per question`, where a draft had a clause about
  where the time went.
- State the number or the thing: `40 minutes shared across 35 questions`.
- Keep the noun and the unit, and say what a bare number counts: `up 12 marks on
  Standard Test 9`.
- Reuse the product's word for a thing and its sentence for the same event.
  List the terms the neighbouring screens use before writing.
- An error message says what happened and what to do next. An empty state says
  what will appear and how to make it appear. A button names its action with
  the verb used elsewhere.

Read each string beside a neighbouring screen and in the rendered page with
real data, including zero, one and a long name. `check.py --profile interface`
reads one string per line. Short labels fall below what its rules can see, so
the comparison with existing screens is the test. The
[GOV.UK error message guidance](https://design-system.service.gov.uk/components/error-message/)
and Nielsen Norman Group's guidelines for
[error messages](https://www.nngroup.com/articles/error-message-guidelines/) and
[empty states](https://www.nngroup.com/articles/empty-state-interface-design/)
give the fuller standard.

## Other languages

Keep the input language and follow its grammar and register. The forms apply in
any language. The checker's rules are English only.
