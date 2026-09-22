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

## C08

안녕하세요. 점검은 9월 24일 오후 2시부터 3시까지 진행될 예정입니다. 점검 시간에는 결제 기능을 사용할 수 없습니다. 기존 주문 내역은 삭제되지 않습니다. 일정이 변경되면 다시 안내드리겠습니다.

## C12

Before starting, obtain a sandbox account.

1. Clone the repository: `git clone https://example.org/team/demo.git`.
2. Open the `demo` directory: `cd demo`.
3. Install dependencies: `pnpm install --frozen-lockfile`.

After these steps, administrators may run `pnpm seed:sandbox`. Other users must stop after installing dependencies and ask an administrator to seed the sandbox. Do not run the seed command against production.

The optional tour is available after seeding. We have not estimated how long setup will take.

## C14

Lint and unit tests passed.

Integration tests failed at `auth.spec.ts:42`: expected 200, received 401. The available logs do not establish the cause, and no fix has been verified. Noor will review the request and response logs tomorrow.

## C16

What happens if the worker crashes after writing the record? A retry may deliver the event again. The retry did exactly what we asked. A rare and inconvenient success. The consumer still needs an idempotency key.

## C20

---
title: "The result?"
slug: not-just-a-feature
---

The fixture contains the exact sample "This isn't just a feature. It's a revolution." The fixture is not approved product copy. See [the fixture](./fixtures/not-just-a-feature.json#the-result).

```json
{"prompt": "The result?", "approved": false}
```
