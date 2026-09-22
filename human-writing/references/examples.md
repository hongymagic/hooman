# Editorial distinctions

These original examples illustrate choices, not required rewrites. All facts are fictional.

Read the relevant section only. The opening examples cover fidelity, voice and action
clarity. [Patterns and counterexamples](#patterns-to-remove-and-devices-to-keep) show
the boundary of the prohibited shortcuts. [Plain explanations](#plain-explanations)
and [natural phrasing](#natural-phrasing) show positive craft drawn from the research,
using newly invented scenarios.

## Courtesy without padding

Before:

> I wanted to take this opportunity to ask whether you could possibly send the revised invoice today. We need it to close the account.

Possible edit:

> Could you send the revised invoice today? We need it to close the account.

The request stays courteous and its reason survives. Removing the whole second sentence
would lose useful context rather than just shorten the email.

## Specifics with a boundary

Supplied facts: a trial included eight teams; six reported faster handovers; no timing
measurements were collected.

Unsupported draft:

> Our breakthrough workflow dramatically speeds up every handover.

Grounded draft:

> Six of the eight trial teams reported faster handovers. The trial did not measure handover times.

The distinction between a report and a measurement matters. A percentage reduction or
claim about all teams would need additional evidence.

## Uncertainty that earns its place

Before:

> It may perhaps be possible that the larger cache reduces disk reads, although the trace does not identify the cause.

Possible edit:

> The larger cache may reduce disk reads, although the trace does not identify the cause.

The overlapping hedges can go; the possibility and missing causal evidence remain.

## Passive voice with an unknown actor

> The credentials were rotated at 10:20 UTC. The incident log does not identify who rotated them.

Leave this alone if it serves the document. Changing it to “The security team rotated
the credentials” would invent an actor. There is no value in satisfying an active-voice rule.

## Voice without a new biography

Sample:

> The basil survived another week. We are both surprised.

Draft:

> I repotted the fern on Sunday. It is important to note that it still leans towards the window. I am choosing to call that ambition.

Possible edit:

> I repotted the fern on Sunday. It still leans towards the window. I am choosing to call that ambition.

The humour already belongs to the author. Adding a childhood gardening story or a
new joke is unnecessary to match the sample.

## Korean register

Before:

> 문의하신 내용과 관련하여 안내를 드리고자 합니다. 환불 처리에는 영업일 기준 3일이 소요될 예정입니다.

Possible edit:

> 문의하신 환불 처리에는 영업일 기준 3일이 소요될 예정입니다.

The edit removes an empty announcement while retaining polite register, the business-day
unit and the expected duration. Turning an expected duration into a guaranteed deadline
would change the meaning.

## A review can identify a blocker

Text: “The service launches on 4 March. The approved schedule says 6 March.”

Useful review: “The two launch dates conflict. Confirm which schedule governs before
publishing.”

A review need not pick a date or supply a replacement paragraph. Resolving the factual
conflict requires information that stylistic editing cannot provide.

## A visible action with its condition intact

Before:

> We also have an optional supplier briefing on Tuesday. As for the replacement screens, Finance has not yet approved the purchase. Please ask Leila to confirm the quantities by 11 am Monday. Leila can place the order once Finance approves it.

Possible edit for an internal action note:

> Please ask Leila to confirm the screen quantities by 11 am Monday. She can place the order once Finance approves the purchase; approval is still pending.
>
> The supplier briefing on Tuesday is optional.

The requested action, named person and deadline stay together. The purchase condition
and optional briefing remain visible. Making the note easier to scan does not mean
inventing a purchase deadline or dropping the dependency on Finance.

## Patterns to remove and devices to keep

### 9. Hollow reframing

Supplied fact: the release adds CSV export for reports.

Before:

> This isn't just another feature. It's a whole new way to take control of your data. You can now export reports as CSV.

Possible edit:

> You can now export reports as CSV.

The added framing offers no supported distinction or benefit. It is not needed to
make product copy confident or useful.

### 10. A genuine contrast

> The change limits concurrent requests, not the total number of requests. Clients can still retry after the current request finishes.

Keep this in technical documentation. The contrast defines scope; deleting it would
blur what the change controls. A surface ban on “not X” would make the explanation worse.

### 11. Manufactured suspense

Evidence supplied for an incident note: a stale cache entry caused the failure;
the deployed fix expires that entry when the account closes.

Before:

> The problem? A stale cache entry. The fix? We now expire the entry when the account closes. A small change. A massive leap forward.

Possible edit:

> A stale cache entry caused the failure. The deployed fix expires the entry when the account closes.

The rewrite keeps cause and deployed behaviour while removing theatrical framing and
an unsupported assessment of impact. If the cause or deployment were unknown, those
claims could not be supplied merely to make a tidy incident narrative.

### 12. A question that helps the reader

> What happens if the worker crashes after writing the record? The retry can deliver the event again, so the consumer still needs an idempotency key.

Keep this in a suitable explanation or FAQ. The question anticipates a specific
failure scenario and the answer explains a requirement. It does more than announce
the next sentence. The technical term and the possibility of redelivery both matter.

### 13. Borrowed authority and unsupported praise

Supplied facts: five teams tested the dashboard; four reported finding failed jobs
more easily; search times were not measured.

Unsupported draft:

> Leading engineers agree that our world-class dashboard sets a new standard for operational excellence.

Grounded draft:

> Four of the five trial teams reported finding failed jobs more easily. The trial did not measure search times.

An unspecified authority is not evidence. Do not add a ranking or quantified speedup.
If the original author disputes the supplied facts, surface the conflict rather than
silently treating the new sentence as a resolved factual correction.

### 14. Stacked synonyms and slogans

Supplied information: a guide covers account setup and three approval steps.

Before:

> The guide is clear, concise and easy to understand, giving you the clarity and confidence to move forward. It covers account setup and the three approval steps.

Possible edit:

> The guide covers account setup and the three approval steps.

The description tells readers what they will find. The praise repeats itself without
support. Three distinct approval steps would still deserve all three entries.

### 15. A repeated conclusion with a necessary condition

Before:

> The import now accepts compressed files. This means compressed files can now be imported. In summary, this opens the door to more flexible imports. Files larger than 20 MB still require approval.

Possible edit:

> The import now accepts compressed files. Files larger than 20 MB still require approval.

The repeated result and vague benefit can go. The closing restriction must stay;
“larger than 20 MB” must not become “20 MB or larger”. A useful final condition is
not padding just because it appears at the end.

### 16. Authored humour and uncertainty

Before:

> It is important to note that the new parser passed the staging checks. Production has a talent for finding my blind spots, so I'm leaving the fallback enabled until Friday. We do not yet know whether the staging sample covers malformed inputs.

Possible edit:

> The new parser passed the staging checks. Production has a talent for finding my blind spots, so I'm leaving the fallback enabled until Friday. We do not yet know whether the staging sample covers malformed inputs.

The author already supplied the humour. Cut the empty announcement without adding
jokes, removing personality or presenting incomplete test coverage as a settled fact.

## Plain explanations

### 17. Mechanism, evidence and limits

Supplied facts: an importer previously made one request per row. It now batches up
to 100 rows per request. For a staging fixture of 20,000 rows, the request count fell
from 20,000 to 200. Batching uses more memory. Production performance is untested.

Weak draft:

> Our revolutionary importer unlocks seamless scalability through an innovative approach. This marks a significant milestone in the evolution of our platform.

Grounded draft:

> The importer now sends up to 100 rows per request. On the 20,000-row staging fixture, the request count fell from 20,000 to 200. Batching uses more memory, and we have not tested production performance.

The mechanism explains the result; the test setting and cost constrain the claim.
Lower request count does not establish a matching latency reduction. Do not replace
the unmeasured outcome with a plausible percentage or a production guarantee.

### 18. Let a requirement explain the design

Supplied facts: a booking form originally allowed one contact per booking. Group
bookings now require a contact for each attendee. The team added attendee records
linked to the booking and kept the booking contact for billing questions.

Weak draft:

> We embraced a sophisticated data model to support the evolving needs of our users.

Grounded draft:

> The form allowed one contact per booking. Group bookings now need a contact for each attendee, so we added attendee records linked to the booking. We kept the booking contact for billing questions.

The changed requirement makes the design choice understandable. This uses the craft
of progressing from a concrete problem to its consequences; it does not borrow a
source author's anecdotes, code or voice. A supplied tradeoff would belong here too.

## Natural phrasing

### 19. Cadence follows the thought

Before:

> We finished the draft on Tuesday. We sent it to Maya that afternoon. We are waiting for her comments. We cannot publish until she approves it.

Possible edit for an internal update:

> We finished the draft on Tuesday and sent it to Maya that afternoon. We're waiting for her comments and cannot publish until she approves it.

Combine closely related thoughts to reduce the repeated starts. The timing, pending
comments and approval condition stay intact. Contractions fit this setting; they are
not required everywhere. Short sentences can still carry emphasis or the author's rhythm.

### 20. Ordinary verbs

Before:

> We will undertake an assessment of the applications on Monday and provide notification of our decision to applicants by Friday.

Possible edit:

> We will assess the applications on Monday and notify applicants of our decision by Friday.

The verbs carry the actions directly. Both dates, the recipient and the commitment
remain. Prefer the familiar phrase when it says the same thing; do not substitute a
vague everyday word for a necessary technical term.

### 21. Warmth without forced familiarity

Before, in a professional customer reply:

> Hey there! We totally get how frustrating this must be. Your refund request is under review, and we'll email you our decision by Friday. Sit tight—we've got you!

Possible edit:

> Your refund request is under review. We'll email you our decision by Friday.

Clear information can reassure without guessing how someone feels or implying a
favourable result. Keep an appropriate greeting or acknowledgement when the relationship
or known circumstances support it. The promised decision is not a promised refund.
