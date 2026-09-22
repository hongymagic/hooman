## C03

# ADR-017: Retain at-least-once delivery

## Status
Proposed

## Context
The queue offers at-least-once delivery. Consumers use an idempotency key to suppress duplicate side effects. Deduplication entries expire after 24 hours, so a replay after that interval may repeat a side effect. The staging sample suggests lower p95 latency with batching; it does not establish that batching caused the reduction.

## Decision
We propose retaining at-least-once delivery. We have not committed to exactly-once processing. The retry budget must remain configurable.

## Consequences
Consumer idempotency remains necessary. We do not yet know whether the 24-hour window covers production replay patterns.

## C05

I visited the repair café on Saturday with my stubborn toaster. Jo found a loose wire. We fixed it in twenty minutes. I had been ready to buy a new one. The toast tasted exactly the same, which was, in its own way, a triumph.

## C06

Please send the signed form by Friday. We cannot book the inspection until we receive it. If you need more time, contact Priya.

## C11

Hi team,

**Monitor quantities — due 2 pm Friday**

Please confirm your team's monitor quantities to Leila by 2 pm Friday. Finance has not approved the purchase yet. Once Finance approves the budget, Leila may place the order.

**Optional supplier workshop — Tuesday, 10 am**

Sam will send the workshop recording on Wednesday. You do not need to attend the workshop to request monitors.

Thanks,
Mina

## C12

Before starting, obtain a sandbox account.

1. Clone the repository using `git clone https://example.org/team/demo.git`.
2. Open the `demo` directory with `cd demo`.
3. Run `pnpm install --frozen-lockfile`.

After those steps, administrators may run `pnpm seed:sandbox`. Other users must stop after installing dependencies and ask an administrator to seed the sandbox.

**Do not run the seed command against production.**

The optional tour is available after seeding. We have not estimated how long setup will take.

## C13

The library opens at nine on Saturday. I will be there at ten, returning the book I renewed three times. Some relationships need a firm ending.

## C14

**Passed:** Lint and unit tests.

**Failed:** Integration tests at `auth.spec.ts:42` — expected 200, received 401. The available logs do not establish the cause. No fix has been verified.

Noor will review the request and response logs tomorrow.
