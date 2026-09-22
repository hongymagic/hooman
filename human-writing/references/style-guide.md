# Writing style guide

Read the section that helps with the current passage. These examples illustrate
editorial choices, not a single voice to impose on every writer. Their facts are
fictional; they are not details to add to someone else's draft.

## Start with something worth saying

Before:

> I wanted to take this opportunity to ask whether you could possibly send the revised invoice today. We need it to close the account.

Edit:

> Could you send the revised invoice today? We need it to close the account.

The request stays courteous. Its reason earns the second sentence. Cut the preamble,
not the context that helps someone understand or act. An intentional narrative may
need a slower opening; do not move its conclusion to the front by habit.

## Let verbs carry the action

Before:

> We will undertake an assessment of the applications on Monday and provide notification of our decision to applicants by Friday.

Edit:

> We will assess the applications on Monday and notify applicants of our decision by Friday.

The same actions, dates and recipient survive in fewer words. Name an actor when
the evidence supplies one and readers need to know who acts. “The credentials were
rotated at 10:20 UTC” is useful when the actor is unknown. Do not invent a security
team to make the sentence active. Address the reader when they have a role in the
sentence, not merely to make the writing feel personal.

## Let one thought lead to the next

Before:

> The form allowed one contact per booking. Group bookings now need a contact for each attendee. In light of these evolving requirements, we implemented an enhancement to the data model. We added attendee records linked to the booking. We kept the booking contact for billing questions.

Edit:

> The form allowed one contact per booking. Group bookings now need a contact for each attendee, so we added attendee records linked to the booking. We kept the booking contact for billing questions.

“So” connects a requirement to the response. Another transition or a claim about
sophistication would add little. Explain an unfamiliar term where readers meet it;
use an analogy only as far as the comparison holds. A worked example should make
the point concrete, not introduce an unrelated anecdote.

## Let the thought set the pace

Before:

> We finished the draft on Tuesday. We sent it to Maya that afternoon. We are waiting for her comments. We cannot publish until she approves it.

Edit for an internal update:

> We finished the draft on Tuesday and sent it to Maya that afternoon. We're waiting for her comments and cannot publish until she approves it.

Join related thoughts; give a new thought room. Contractions can suit this register.
Short sentences can also work, especially when they carry the author's emphasis or
humour. Do not vary sentence lengths just to produce an irregular pattern.

## Keep the writer in the sentence

Before:

> I repotted the fern on Sunday. It is important to note that it still leans towards the window. I am choosing to call that ambition.

Edit:

> I repotted the fern on Sunday. It still leans towards the window. I am choosing to call that ambition.

The humour belongs to the author. Removing the announcement is enough. A supplied
sample can guide cadence and word choice without donating its anecdotes, opinions
or factual mistakes. Formal technical prose also has a voice; informality is not
the measure of natural writing.

## Be warm without performing familiarity

For a professional customer reply:

> Your refund request is under review. We'll email you our decision by Friday.

Clear information can reassure without “Hey there!”, “We totally get it” or “We've
got you!” Keep a greeting, thanks or acknowledgement when it fits the relationship
and known circumstances. Do not guess someone's feelings. A decision promised for
Friday is not a promised refund.

## Say exactly how much you know

Before:

> It may perhaps be possible that the larger cache reduces disk reads, although the trace does not identify the cause.

Edit:

> The larger cache may reduce disk reads, although the trace does not identify the cause.

The duplicated qualification goes; the real uncertainty stays. Plain confidence
comes from evidence: “Six of the eight trial teams reported faster handovers. The
trial did not measure handover times.” That is a report, not a measured speedup.
Keep test settings and limits beside results. Fewer requests do not establish lower
latency, and staging results do not establish production performance.

## Remove empty rhetorical devices

Each edit below keeps the substantive information in its original sentence.

| Padded wording | Useful wording |
| --- | --- |
| “This isn't just another feature. It's a new era of control. Reports now export as CSV.” | “Reports now export as CSV.” |
| “The problem? A stale cache entry caused the failure. The fix? The deployed change expires it when the account closes.” | “A stale cache entry caused the failure. The deployed change expires it when the account closes.” |
| “The guide is clear, concise and easy to understand. It covers account setup and three approval steps.” | “The guide covers account setup and three approval steps.” |
| “The import now accepts compressed files. This means compressed files can now be imported. Files larger than 20 MB still require approval.” | “The import now accepts compressed files. Files larger than 20 MB still require approval.” |

Delete praise that does no explanatory work. An unsupported claim about what experts
agree on needs evidence or an unresolved note, not a more plausible invented claim.
Keep a closing sentence when it adds a restriction, implication or next action.

## Keep a device when it does real work

> The change limits concurrent requests, not the total number of requests.

This contrast defines scope.

> What happens if the worker crashes after writing the record? The retry may deliver the event again, so the consumer still needs an idempotency key.

This question anticipates a reader's concern. The term names a specific requirement.
Neither passage needs to be flattened into a pattern-free sentence. Three distinct
points deserve three entries; an adverb such as “automatically” may carry a fact.
Necessary jargon, a useful dash and purposeful parallel structure may all stay.

## Make the shape help the reader

Keep an action beside its owner, deadline and conditions: “Ask Leila to confirm the
quantities by 11 am Monday. She can order once Finance approves the purchase.”
Optional background should not obscure that request. Number steps when order matters,
keeping prerequisites and role restrictions attached to the steps they govern.

When restructuring a list, preserve priorities, rankings and relationships as well
as the items. Use headings or a table when they make the material easier to navigate;
honour a preference for connected prose. No diagnosis dictates a layout.

Reference documentation usually needs present behaviour. A PR description may need
the old behaviour to explain a fix; an ADR may need the alternatives and why a choice
is proposed. Keep those distinctions without forcing a common article outline.

## Follow the language and register

Before:

> 문의하신 내용과 관련하여 안내를 드리고자 합니다. 환불 처리에는 영업일 기준 3일이 소요될 예정입니다.

Edit:

> 문의하신 환불 처리에는 영업일 기준 3일이 소요될 예정입니다.

The announcement disappears; polite Korean, business days and expected duration
remain. English phrase lists and preferences about contractions do not transfer
mechanically to another language.
