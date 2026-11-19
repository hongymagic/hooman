# Registers

Find the kind of document you are working on and read that part. Each one says
what its reader needs first and which habits matter there. Specimens are
invented and sit in quotations or code.

## Replies and messages

Chat replies, email replies and review comments. The reader wrote half the
thread and already has the context.

- Lead with the answer or the decision. Add the one fact they lack and any link
  they need to act.
- Do not restate their question, summarise their own work back to them or walk
  through a diagnosis nobody asked for. The proof that a plan works belongs in
  the ticket or document that follows.
- Break a chat reply at thought boundaries. A conversational reply carries no
  headings, bullets or bold.
- Keep the courtesy the relationship calls for. Drop praise for the question
  and the closing offer of more help.

Most of this is structural, so the checker will pass a reply that still buries
its answer. Read it as the recipient.

## Updates to people outside the work

Announcements, status reports and incident notices.

- An incident notice gives the impact, the current state, what the reader must
  do (or that nothing is needed) and what happens next, with a date. Give times
  with a zone and figures with a unit.
- A status report for a decision-maker opens with the decision needed, its
  deadline and its cost. Progress against the target comes next, then risks.
- State what changed for the reader. `We are thrilled to announce` and its
  relatives say how the writer feels.
- One plain apology is enough when one is owed.
- Keep the structure a skimming reader relies on: bold times in a timeline, a
  labelled line for the action required. Drop rules and slogans around it.

## Documentation, READMEs and how-to guides

- A README says what the project is in a sentence, shows a first command that
  works and lists the requirements. Detail follows.
- A how-to gives steps in order, one action each, in the imperative, with the
  result the reader should see. Prerequisites come before step one, and a
  warning comes before the step it applies to.
- Use one term for one thing. Variation that would be graceful in an essay sends
  a reader hunting for a second concept.
- Describe current behaviour. What it replaced belongs in the changelog.
- Lists, tables, fragments in reference tables and the passive with an unknown
  actor are all at home here. Treat the formatting findings as advisory.

## Pull requests, commit messages and code comments

Usually written inside other work, so return only the text.

- A pull request says what changes for a user or caller, why, how it was
  verified and what the reviewer should look at. Add risks and rollout when they
  exist. Do not narrate the diff or the session that produced it.
- A commit subject is imperative. The body gives the reason.
- A comment explains a constraint the code cannot show. It does not describe
  the edit that created the line.

## Essays, posts and newsletters

The staging habits concentrate here. In the calibration specimens, opinion
pieces drew contrast frames, the concession that nobody asked for, question
volleys and the call-to-action ending far more often than documentation did.

- The piece needs a position the author holds. Take it from the brief or the
  sample. Do not manufacture a stance, an anecdote or a reaction.
- Open on the claim or the scene. Support the claim with what the author
  supplied, and end on the last point.
- When drafting a social post, leave out the heading, the hashtag block and
  the closing question that fishes for replies. When editing one, a closing
  question is the author's choice and stays unless they ask.

## Product and marketing copy

- Say what the product does, for whom and at what price, with the proof that
  was supplied. Sales register is expected; unsupported claims are the risk.
- Never add a statistic, customer, guarantee, tier or time saving the brief did
  not contain. Models do this readily. Run the comparison with `--brief`: it
  lists added figures, names, links and quotations. Then read for added claims,
  which it cannot see.
- Address one audience.

## Interface copy

Labels, headings, buttons, helper text, empty states and error messages. Each
string is read mid-task, beside the control or figure it describes. Register is
the whole signal, and sentence-level advice about rhythm does not apply.

- A heading is a label. Name what the section holds.

  > Where the time went

  becomes

  > Time per question

- Say the number or the thing. A figure of speech standing where a fact could be
  is the tell: `adds to the picture`, `at a glance`.

  > 40 minutes shared across 35 questions

- Do not compress to the data model. Keep the noun and the unit, and say what a
  bare number counts: `up 12 marks on Standard Test 9`, never `up 12 on 9`.
- Reuse the product's word for a thing and its sentence for the same event.
  Before writing, list the terms the neighbouring screens use. A second word for
  the same thing reads as a second thing.
- Write one plain sentence where two clipped ones would pose as a saying.
- An error message says what happened and what to do next, without blame,
  jargon or `oops`. An empty state says what will appear and how to make it
  appear. A button names its action with the verb used elsewhere.
- Cut filler: `simply`, `easily`, `successfully`, an exclamation mark on a
  routine event.

Then test it the way it will be read: beside a neighbouring screen, and in the
rendered page with real data, including zero, one and a long name.

`check.py --profile interface` reads one string per line and applies only the
`interface` rules listed in [checker.md](checker.md). Short labels fall below
what pattern rules can see, so a clean result means little here; the comparison
with existing screens is the real test. With no existing screens to compare
against, take each term from the request, use it the same way throughout and
say that the comparison was not possible. The
[GOV.UK error message guidance](https://design-system.service.gov.uk/components/error-message/)
and Nielsen Norman Group's guidelines for
[error messages](https://www.nngroup.com/articles/error-message-guidelines/) and
[empty states](https://www.nngroup.com/articles/empty-state-interface-design/)
give the fuller standard.

## Other languages

Keep the input language and follow its grammar and register. Do not carry over
English contractions or word lists. The contrast frame and the run-up exist in
every language and can be edited by reading; the checker's rules are English
only.
