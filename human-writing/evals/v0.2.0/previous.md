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

I went to the repair café on Saturday with my stubborn toaster. Jo found a loose wire. We fixed it in twenty minutes. I had been ready to buy a new one. The toast tasted exactly the same. A triumph, in its own way.

## C08

안녕하세요. 9월 24일 오후 2시부터 3시까지 점검이 진행될 예정입니다. 점검 중에는 결제 기능을 사용할 수 없습니다. 기존 주문 내역은 삭제되지 않습니다. 일정이 변경되면 다시 안내드리겠습니다.

## C13

The library opens at nine on Saturday. I will be there at ten, returning the book I renewed three times. Some relationships need a firm ending.

## C15

The optional `maxAttempts` setting limits the number of attempts, not the elapsed time. It does not change the 30-second timeout.

## C16

What happens if the worker crashes after writing the record? A retry may deliver the event again. The retry did exactly what we asked. A rare and inconvenient success. The consumer still needs an idempotency key.

## C17

Archive search is available only on the Team plan and remains in beta until 30 November. Seven customers tried it, and five reported that finding archived orders was easier. Search times and error rates were not measured.

## C18

The import now accepts compressed files. Files larger than 20 MB still require approval. Existing uploads will not be reprocessed. We will publish the guide on Thursday.

## C19

The credentials were rotated automatically at 10:20 UTC. The operator is unknown—check the audit log before naming anyone. Use a robust estimator; the sample contains outliers.

Before the handover:
- Record the incident ID.
- Confirm the rollback owner.
- Keep the fallback enabled.

## C20

---
title: "The result?"
slug: not-just-a-feature
---

The fixture contains the exact sample "This isn't just a feature. It's a revolution." The fixture is not approved product copy. See [the fixture](./fixtures/not-just-a-feature.json#the-result).

```json
{"prompt": "The result?", "approved": false}
```

## C21

We completed the draft on Tuesday and sent it to Maya that afternoon. We are waiting for her comments, and publication cannot proceed until she approves it. We will assess the applications on Monday and notify applicants of our decision by Friday.
