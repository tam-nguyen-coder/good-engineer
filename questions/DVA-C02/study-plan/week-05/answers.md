# ✅ Answers & Explanations — Week 5

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-B · 2-AC · 3-B · 4-A · 5-B · 6-A · 7-B · 8-C · 9-B · 10-B · 11-B · 12-AC · 13-AC · 14-C · 15-AB · 16-A · 17-A · 18-B · 19-B · 20-A · 21-AC · 22-C · 23-AC · 24-B · 25-B · 26-AC

---

### Question 1 — Answer: **B**
- **Why correct:** An SQS standard queue provides **nearly unlimited throughput** and an **at-least-once** delivery model (duplicates are possible), but the prompt states the worker code is **idempotent**, so that is acceptable. **Best-effort ordering** is also fine because ordering is not required. This is the classic decoupling pattern.
- **Why the others are wrong:** A — FIFO is only needed when strict ordering plus no duplicates is required, and it caps throughput (300 / 3,000 / ~30k), which exceeds the requirement. C — a single-shard Kinesis stream provides only 1 MB/s and is meant for streaming/replay, not a decoupling job queue. D — SNS is pub/sub broadcast, not a job queue.
- 🧠 **Key point / trap:** "simple decoupling + high throughput + ordering not required + idempotent" → **SQS standard**.
- 📎 Source: `resources/sqs-standard-vs-fifo.md` (Standard: unlimited throughput, at-least-once, best-effort ordering).

### Question 2 — Answer: **A, C**
- **Why correct:** SQS FIFO preserves **ordering within each message group**, so `MessageGroupId` is required (A). Preventing duplicates (exactly-once processing) requires `MessageDeduplicationId` or content-based deduplication (C), with a **5-minute** deduplication window.
- **Why the others are wrong:** B — `VisibilityTimeout` set to 0 only returns messages immediately; it has nothing to do with ordering or dedup. D — long polling only reduces empty responses and cost. E — `DelaySeconds` only delays delivery (up to 15 minutes).
- 🧠 **Key point / trap:** FIFO = **`MessageGroupId` (ordering) + `MessageDeduplicationId` (deduplication)**. This pair is frequently tested.
- 📎 Source: `resources/sqs-standard-vs-fifo.md` (FIFO: exactly-once processing + FIFO delivery, dedup ID / content-based dedup).

### Question 3 — Answer: **B**
- **Why correct:** A message processed for **longer than the visibility timeout** reappears and is picked up by another consumer → duplicate processing. The standard fix is to call `ChangeMessageVisibility` periodically as a **heartbeat** to extend the timeout while processing continues. It requires the fewest changes and handles variable processing times.
- **Why the others are wrong:** A — FIFO does not "fully eliminate duplicates" when processing still exceeds the timeout, and standard is still at-least-once. C — reducing the timeout makes messages reappear even sooner → more duplicates. D — long polling only affects how messages are received, not long processing.
- 🧠 **Key point / trap:** processing > visibility timeout → **heartbeat with `ChangeMessageVisibility`** (or set the timeout to match processing time). Note the hard cap of **12 hours** does not reset.
- 📎 Source: `resources/sqs-visibility-timeout.md` (heartbeat, `ChangeMessageVisibility`).

### Question 4 — Answer: **A**
- **Why correct:** The visibility timeout defaults to **30 seconds** and maxes out at **12 hours** (measured from the first receive; extending it does NOT reset the 12-hour cap). If a task needs more than 12 hours → use **AWS Step Functions** or break the task into smaller pieces.
- **Why the others are wrong:** B — the maximum is 12 hours, not 24 hours, and extending does not reset it. C — the default is 30 seconds, not 60 seconds; increasing retention is unrelated. D — the default is not 0, and there is a 12-hour cap.
- 🧠 **Key point / trap:** **30 seconds / 12 hours**. Tasks longer than 12 hours → Step Functions.
- 📎 Source: `resources/sqs-visibility-timeout.md` (default 30s, max 12h, use Step Functions if > 12h).

### Question 5 — Answer: **B**
- **Why correct:** SQS message retention defaults to **4 days** and is configurable from ~**60 seconds to 14 days**. 10 days falls within this range, so it is entirely valid — simply set the retention period to 10 days.
- **Why the others are wrong:** A — 4 days is the *default*, not the cap; the cap is 14 days. C — the Extended Client is for payloads > 256 KB, not for extending retention. D — SQS does not retain for 24 hours; 24 hours is the *default* for Kinesis.
- 🧠 **Key point / trap:** SQS retention = **default 4 days, maximum 14 days**. Don't confuse it with Kinesis's 24 hours.
- 📎 Source: Week 5 `README.md` (MUST-KNOW table — message retention).

### Question 6 — Answer: **A**
- **Why correct:** **Long polling** (`WaitTimeSeconds` > 0, up to **20 seconds**) makes SQS wait until a message is available before returning and queries ALL servers → reducing both empty responses and false empty responses → **lowering cost**. This is the classic answer.
- **Why the others are wrong:** B — adding consumers does not reduce empty responses; it increases the number of requests. C — a visibility timeout of 0 is unrelated to polling cost. D — short polling is the cause of many empty responses, so it does the opposite.
- 🧠 **Key point / trap:** "reduce empty responses / lower cost when polling SQS" → **long polling with `WaitTimeSeconds` ≤ 20s**.
- 📎 Source: `resources/sqs-long-polling.md` (long polling reduces empty responses and cost, max 20s).

### Question 7 — Answer: **B**
- **Why correct:** A **dead-letter queue** with a `RedrivePolicy` (`deadLetterTargetArn` plus `maxReceiveCount`): when a message is received more than `maxReceiveCount` times without being deleted (a poison message), it is automatically moved to the DLQ for investigation, keeping the main queue unclogged.
- **Why the others are wrong:** A — a delay queue only delays message delivery. C — long polling only affects how messages are received. D — deduplication prevents duplicates; it does not handle repeatedly failing messages.
- 🧠 **Key point / trap:** poison messages / repeated failures → **DLQ + `maxReceiveCount`**.
- 📎 Source: Week 5 `README.md` (DLQ + `maxReceiveCount`, Lab 2).

### Question 8 — Answer: **C**
- **Why correct:** SQS messages are capped at **256 KB**. For larger payloads (1.5 MB), use the **Amazon SQS Extended Client Library**: store the actual payload in S3 and send only a pointer through SQS; it supports up to **2 GB**. No service change is required.
- **Why the others are wrong:** A — compression does not guarantee it always stays under 256 KB and loses the original data. B — splitting/reassembling is complex and error-prone with ordering. D — SNS is also capped at **256 KB**, so it does not solve the problem.
- 🧠 **Key point / trap:** payload > 256 KB → **Extended Client + S3** (up to 2 GB), NO service change.
- 📎 Source: Week 5 `README.md` (large messages → SQS Extended Client + S3).

### Question 9 — Answer: **B**
- **Why correct:** SQS FIFO defaults to 300 messages/s (up to 3,000 with batching); enabling **high throughput mode** raises it to **~30,000 messages/s**. Scale by distributing messages across **many `MessageGroupId` values** (each group preserves its own ordering and processes in parallel).
- **Why the others are wrong:** A — 300 messages/s is not a hard limit; high throughput mode exists. C — moving to standard loses the ordering/no-duplicate guarantees. D — the visibility timeout is unrelated to throughput.
- 🧠 **Key point / trap:** need FIFO + very high throughput → **high throughput mode + many message groups** (~30k messages/s).
- 📎 Source: `resources/sqs-standard-vs-fifo.md` (high throughput mode → 30,000 TPS).

### Question 10 — Answer: **B**
- **Why correct:** The **same event** must reach **multiple independent systems** → the **SNS-to-multiple-SQS fan-out** pattern: SNS publishes once, each queue receives a copy, and each system processes at its own pace (decoupled broadcast).
- **Why the others are wrong:** A — a single SQS queue: each message is processed by only **one** consumer, so the three systems do NOT all receive it. C — a FIFO group does not help broadcast to multiple systems. D — writing three times from code loses decoupling, is error-prone, and is hard to scale.
- 🧠 **Key point / trap:** "multiple systems need the **same** data, processed independently" → **SNS → multiple SQS** (don't pick a single SQS).
- 📎 Source: Week 5 `README.md` (SNS → multiple SQS fan-out, Lab 1; exam-trap table).

### Question 11 — Answer: **B**
- **Why correct:** By default, subscribers receive ALL messages. Attach a **filter policy** (JSON) to the subscription → SNS delivers only matching messages (based on message attributes or the message body) → no manual filtering in code.
- **Why the others are wrong:** A — creating many topics adds complexity and is unnecessary when a filter policy is available. C — an SQS message group does not filter by content. D — raw message delivery only changes the body format; it does not filter.
- 🧠 **Key point / trap:** "each subscriber receives only certain messages" → **SNS filter policy**, no need for many topics.
- 📎 Source: `resources/sns-message-filtering.md` (filter policy JSON, MessageAttributes/MessageBody).

### Question 12 — Answer: **A, C**
- **Why correct:** Fan-out that **preserves ordering + no duplicates** requires combining an **SNS FIFO topic** (A) with **SQS FIFO** queues as subscribers (C). The FIFO topic preserves ordering and deduplicates, and it is typically paired with SQS FIFO.
- **Why the others are wrong:** B — a standard topic does not guarantee ordering. D — SQS standard is best-effort ordering and may duplicate. E — Firehose is a data-loading service, not an ordered fan-out mechanism.
- 🧠 **Key point / trap:** fan-out that is **ordered + exactly-once** → **SNS FIFO topic + SQS FIFO**.
- 📎 Source: Week 5 `README.md` (SNS FIFO topic typically paired with SQS FIFO).

### Question 13 — Answer: **A, C**
- **Why correct:** "Multiple consumers read the **same** data, independently and concurrently" → **SNS** (pub/sub push to multiple subscribers) and **Kinesis Data Streams** (multiple applications read the same stream independently and concurrently).
- **Why the others are wrong:** B — a single SQS queue: each message is processed by only **one** consumer; consumers split the messages rather than all receiving them. D — FIFO with a single message group only serializes; it does not broadcast. E — the Extended Client is only for sending large payloads.
- 🧠 **Key point / trap:** multiple consumers need the **same** data → **SNS** or **Kinesis** (NOT a single SQS queue).
- 📎 Source: Week 5 `README.md` (WHEN-to-use SQS/SNS/Kinesis table); `resources/kinesis-data-streams-concepts.md` (multiple applications read independently and concurrently).

### Question 14 — Answer: **C**
- **Why correct:** Real-time + **ordered by partition key** + **multiple consumers** + **replay** of older data → only **Kinesis Data Streams** meets all of these (retention of 24h–365 days enables replay).
- **Why the others are wrong:** A — SQS standard is best-effort, has no replay, and delivers each message to one consumer. B — SNS has no replay and no storage. D — Firehose **cannot replay** and is not for multiple consumers reading in real time.
- 🧠 **Key point / trap:** "ordered + multiple consumers + **replay**" → **Kinesis Data Streams** (replay is the deciding factor).
- 📎 Source: `resources/kinesis-data-streams-concepts.md` (retention up to 365 days → replay; multiple consumers); Week 5 `README.md` replay trap.

### Question 15 — Answer: **A, B**
- **Why correct:** `ProvisionedThroughputExceededException` = exceeding the per-shard write limit (1 MB/s or 1,000 records/s). Two approaches: (A) **increase the number of shards** (resharding) to add up total throughput; (B) switch to **on-demand mode** so AWS manages shards automatically based on throughput.
- **Why the others are wrong:** C — visibility timeout is an SQS concept and does not exist in Kinesis. D — long polling is an SQS feature. E — reducing retention does not increase write throughput.
- 🧠 **Key point / trap:** Kinesis write throttling → **add shards** or go **on-demand**. Don't drag in SQS concepts (visibility / long polling).
- 📎 Source: `resources/kinesis-data-streams-concepts.md` (shard 1 MB/s or 1,000 rec/s; on-demand vs provisioned); `README.md` (throttling → `ProvisionedThroughputExceededException`).

### Question 16 — Answer: **A**
- **Why correct:** **Enhanced fan-out (EFO)** gives **each consumer its own dedicated 2 MB/s per shard** via an HTTP/2 push pipe, rather than sharing a single 2 MB/s like shared fan-out → eliminating latency caused by bandwidth contention.
- **Why the others are wrong:** B — retention only affects how long data is kept, not read bandwidth. C — Firehose does not allow multiple consumers to read in real time. D — shared fan-out still shares the 2 MB/s → it does not resolve contention.
- 🧠 **Key point / trap:** "dedicated read bandwidth per consumer" → **enhanced fan-out (2 MB/s per consumer per shard)**.
- 📎 Source: Week 5 `README.md` (enhanced fan-out 2 MB/s dedicated per consumer/shard).

### Question 17 — Answer: **A**
- **Why correct:** Spiky traffic + multiple real-time consumers + replay + **no shard management** → Kinesis Data Streams in **on-demand** capacity mode: AWS manages shards, no capacity planning is needed, and you pay for the throughput actually used.
- **Why the others are wrong:** B — a fixed single provisioned shard is easily throttled on traffic spikes and still requires manual shard adjustment. C — SQS does not allow multiple consumers to read the same data or replay. D — Firehose has no replay and is not for multiple consumers reading in real time.
- 🧠 **Key point / trap:** "no shard/capacity management" + streaming → **Kinesis on-demand**.
- 📎 Source: `resources/kinesis-data-streams-concepts.md` (on-demand manages shards); Week 5 `README.md` quick-reflex table.

### Question 18 — Answer: **B**
- **Why correct:** **Kinesis Data Firehose**: near-real-time, **automatically loads** data into S3/Redshift/OpenSearch/Splunk, buffers by size or time, requires **no consumer** and **no shard management**. It has no replay — but the prompt does not need replay.
- **Why the others are wrong:** A — KDS + KCL requires **writing your own consumer**, which contradicts "no consumer code." C — SQS + Lambda requires writing your own load logic. D — SNS does not automatically load/buffer data into S3/Redshift.
- 🧠 **Key point / trap:** "auto-load a stream into S3/Redshift, no code, no replay needed" → **Firehose**.
- 📎 Source: Week 5 `README.md` (Firehose auto-loads, no replay, no shard management).

### Question 19 — Answer: **B**
- **Why correct:** Kinesis Data Streams retention defaults to **24 hours** and can be increased up to a maximum of **8,760 hours = 365 days** using `IncreaseStreamRetentionPeriod` → enabling replay of up to 1 year (with additional charges beyond 24 hours).
- **Why the others are wrong:** A — Kinesis can replay within the retention period; there is no need to back up to S3 yourself. C — Firehose is not for replaying a stream. D — the retention cap is 365 days, not 7 days.
- 🧠 **Key point / trap:** Kinesis replay → increase retention, up to **365 days**.
- 📎 Source: `resources/kinesis-data-streams-concepts.md` (retention 24h → 8,760h/365 days, `IncreaseStreamRetentionPeriod`).

### Question 20 — Answer: **A**
- **Why correct:** Orchestrating many steps (call an API, wait, branch, retry, catch errors) is exactly what **AWS Step Functions** does: `Choice` (branching), `Retry` (retry with backoff), `Catch` (catch errors and branch to compensation) — declared in Amazon States Language, with no need to cram retry logic into the Lambda code, plus a visual execution diagram.
- **Why the others are wrong:** B — increasing the timeout does not address retries/branching/observability. C — a DLQ only holds failed messages; it does not orchestrate a multi-step workflow. D — recursive Lambda invocation is hard to control, error-prone, and not observable.
- 🧠 **Key point / trap:** "orchestrate many steps, `Retry`/`Catch`/`Choice`, reduce code" → **Step Functions**.
- 📎 Source: Week 5 `README.md` (Step Functions ASL: Task/Choice/Retry/Catch; Lab 3).

### Question 21 — Answer: **A, C**
- **Why correct:** Step Functions **Express** workflows run for up to **5 minutes** and are optimized for **high-volume event processing** (IoT/streaming) (A); they use **at-least-once** (asynchronous) semantics, which suits **idempotent** operations (C).
- **Why the others are wrong:** B — exactly-once belongs to **Standard** (Express async is at-least-once). D — running for up to 1 year is **Standard**. E — billing by state transitions is **Standard**; Express is billed by number of executions + duration + memory.
- 🧠 **Key point / trap:** Express = **≤ 5 minutes, high-volume, at-least-once**; Standard = **≤ 1 year, exactly-once, billed by state transitions**.
- 📎 Source: `resources/stepfunctions-standard-vs-express.md` (Standard vs Express comparison table).

### Question 22 — Answer: **C**
- **Why correct:** A **payment (non-idempotent)** workflow that runs long, must **run no more than once**, and must retain audit history → **Standard**: exactly-once, runs for up to **1 year**, retains execution history for **90 days** (viewable/replayable via API + console).
- **Why the others are wrong:** A/B — Express runs for at most 5 minutes, which does not fit a long workflow; async is at-least-once (may run more than once → dangerous for non-idempotent operations like charging a payment); Express is not stored by Step Functions (you must enable CloudWatch Logs). D — Standard runs for up to 1 year and is not limited to 5 minutes (that is Express).
- 🧠 **Key point / trap:** payment / non-idempotent / long / audit → **Standard (exactly-once, up to 1 year)**.
- 📎 Source: `resources/stepfunctions-standard-vs-express.md` (Standard: exactly-once, non-idempotent like charging a payment, 90-day history).

### Question 23 — Answer: **A, C**
- **Why correct:** Need HA/failover + persistence + rich data structures → **ElastiCache for Redis** (Valkey/Redis OSS): it has replication/HA and persistence (snapshot/AOF) (A); Redis supports **sorted sets/lists/hashes**, which suit a leaderboard (C).
- **Why the others are wrong:** B — Memcached does **not** have persistence/failover. D — Memcached does not have replication (Redis does). E — the two engines are NOT equal: only Redis has snapshots and failover.
- 🧠 **Key point / trap:** HA + persistence + data structures / leaderboard / pub-sub / durable sessions → **Redis**; Memcached is only simple key-value, no HA/persistence.
- 📎 Source: Week 5 `README.md` (Redis vs Memcached table).

### Question 24 — Answer: **B**
- **Why correct:** Simple key-value data, needs to **scale horizontally**, and should exploit **multi-threading**, with no need for persistence/complex structures → **ElastiCache for Memcached** (multi-threaded, easy horizontal scaling, low cost).
- **Why the others are wrong:** A — Redis is mostly single-threaded and strong on HA/persistence/data structures — overkill for a simple need. C — DAX is a cache specifically for DynamoDB, not a general key-value cache here. D — an RDS read replica is a replica of a relational database, not a caching layer.
- 🧠 **Key point / trap:** simple cache + multi-threading + horizontal scaling → **Memcached**.
- 📎 Source: Week 5 `README.md` (Redis vs Memcached table: Memcached is multi-threaded, scales horizontally).

### Question 25 — Answer: **B**
- **Why correct:** **Lazy loading (cache-aside)**: read the cache first; on a **miss** → query the database → write to the cache. It caches only the data actually used (saving memory), the first miss is slower, and a **TTL** lets data expire automatically to prevent stale data.
- **Why the others are wrong:** A — write-through writes to the cache on every database write → the cache is always fresh but caches even never-read data (wasting memory), which is the opposite of the description. C — a TTL is **typically combined** with lazy loading, not unusable with it. D — write-behind/buffering does not match the description and is not a strategy covered in the week's material.
- 🧠 **Key point / trap:** "cache only data that is read + slower first miss + TTL" → **lazy loading (cache-aside)**; "always fresh but wastes memory" → write-through.
- 📎 Source: Week 5 `README.md` (caching strategy: lazy loading vs write-through, TTL).

### Question 26 — Answer: **A, C**
- **Why correct:** RDS Proxy **pools and reuses** connections → reducing the number of open connections to the database and taming the "connection storm" caused by Lambda scaling (A); it also integrates with **Secrets Manager** for secure credential retrieval / supports **IAM authentication** and improves resilience during failover — and it can be enabled **without code changes** (C).
- **Why the others are wrong:** B — RDS Proxy does not scale up the RDS instance itself. D — RDS Proxy does not cache query results (that is ElastiCache/DAX). E — there is no need to replace RDS with DynamoDB; the requirement is only to pool connections.
- 🧠 **Key point / trap:** Lambda causing a connection storm to RDS → **RDS Proxy** (connection pooling + Secrets Manager/IAM), no need to increase the DB size.
- 📎 Source: `resources/rds-proxy.md` (connection pooling, Secrets Manager / IAM auth, failover, no code changes).
