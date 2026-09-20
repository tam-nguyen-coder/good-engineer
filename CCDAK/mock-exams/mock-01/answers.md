# ✅ Answers — CCDAK Mock Exam 01

> Chỉ mở sau khi đã làm hết 60 câu trong [questions.md](questions.md) với đồng hồ 90 phút.
> Back to [mock index](../README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-D · 4-BD · 5-B · 6-A · 7-B · 8-D · 9-AC · 10-C · 11-B · 12-C · 13-A · 14-C · 15-D · 16-D · 17-AB · 18-C · 19-A · 20-A · 21-B · 22-B · 23-C · 24-D · 25-A · 26-B · 27-D · 28-C · 29-D · 30-A · 31-A · 32-CE · 33-AD · 34-BC · 35-B · 36-AE · 37-C · 38-D · 39-BD · 40-A · 41-AC · 42-B · 43-C · 44-D · 45-A · 46-CD · 47-B · 48-C · 49-AB · 50-D · 51-BE · 52-A · 53-B · 54-C · 55-D · 56-C · 57-AD · 58-A · 59-BC · 60-B

---

## 📊 Chấm điểm theo domain

Đánh dấu từng câu đúng/sai rồi điền bảng. Cột **Ngưỡng** là mức tối thiểu cần đạt trước khi đăng ký thi thật.

| Domain | Tỉ trọng CCDAK | Câu số | Số đúng / Tổng | % | Ngưỡng |
| --- | --- | --- | --- | --- | --- |
| **DEV** — Application Development | 28% | 2, 8, 11, 15, 19, 23, 26, 30, 33, 37, 41, 45, 49, 52, 55, 57, 60 | ___ / 17 | ___ | ≥ 76% (13/17) |
| **FUND** — Fundamentals | 23% | 1, 6, 9, 13, 18, 24, 31, 35, 39, 44, 48, 53, 56, 59 | ___ / 14 | ___ | ≥ 71% (10/14) |
| **CONNECT** — Kafka Connect | 15% | 3, 10, 16, 22, 29, 34, 40, 46, 54 | ___ / 9 | ___ | ≥ 78% (7/9) |
| **OBS** — Application Observability | 13% | 4, 14, 21, 27, 32, 42, 50, 58 | ___ / 8 | ___ | ≥ 75% (6/8) |
| **STREAMS** — Kafka Streams | 12% | 5, 12, 20, 28, 36, 43, 51 | ___ / 7 | ___ | ≥ 71% (5/7) |
| **TEST** — Application Testing | 8% | 7, 17, 25, 38, 47 | ___ / 5 | ___ | ≥ 60% (3/5) |
| **TỔNG** | 100% | 1–60 | ___ / 60 | ___ | **≥ 80% (48/60)** |

> 📌 Câu Multi chỉ tính đúng khi chọn **đủ và chỉ** hai phương án đúng. Câu Matching/Ordering tính đúng khi toàn bộ chuỗi ghép khớp — đề thật cũng chấm nguyên câu, không chấm từng cặp.

---

### Question 1 — Answer: **B**

- **Why correct:** `send()` runs on the application thread in this order: the `ProducerInterceptor` chain sees the record first (stage 2), then the key and value **serializers** turn it into bytes (4), then the **partitioner** picks a partition — it needs the serialized key bytes to hash (3), then the record is appended to a per-partition batch in the accumulator (1) and `send()` returns a future. The background **sender** thread later groups ready batches per broker and issues the produce request (5).
- **Why the others are wrong:** A — interceptors run before serialization, not after; they see the `ProducerRecord` as the application built it. C — the partitioner cannot run before serialization because the default partitioner hashes the **serialized** key bytes. D — same two errors combined: serialization before interceptors and partitioning before interceptors.
- 🧠 **Key point / trap:** the memorable rule is *interceptor → serializer → partitioner → accumulator → sender*. The partitioner needing serialized bytes is what fixes the middle of the order, and the accumulator/sender split is what makes `send()` asynchronous.
- 📎 Source: `../../study-plan/week-03/resources/kafkaproducer-javadoc.md`.

### Question 2 — Answer: **C**

- **Why correct:** since Kafka 3.0 the producer defaults are `acks=all` and `enable.idempotence=true`, so the reviewer's 2019 description is outdated on both points. What the reviewer *should* have flagged is the topic side: broker `min.insync.replicas` still defaults to **1**, so "all in-sync replicas" can legitimately mean one replica and an acknowledged write can still be lost with the broker that holds it.
- **Why the others are wrong:** A — those are the pre-3.0 defaults; this is exactly what stale practice material teaches. B — `min.insync.replicas` defaults to **1**, not 2; the production triple RF=3 / min.isr=2 / `acks=all` has to be configured deliberately. D — the idempotent producer is scoped to one producer **session**; a restart yields a new producer ID, and no `transactional.id` is ever generated automatically.
- 🧠 **Key point / trap:** a Kafka 4.3 producer with no configuration is already durable on the *client* side. The remaining hole is always the *topic* side — `min.insync.replicas=1`.
- 📎 Source: `../../study-plan/week-03/resources/producer-configs.md` (`acks` = all, `enable.idempotence` = true) and `../../study-plan/week-02/resources/kafka-replication-isr.md`.

### Question 3 — Answer: **D**

- **Why correct:** a converter decides **what the bytes on the Kafka topic look like** (`value.converter`, plus `schemas.enable` for `JsonConverter`), while an SMT reshapes the **structured record** inside Connect. Renaming a field is `ReplaceField$Value` with `renames=cust_id:customerId`. On a **source** connector the pipeline is `connector → SMT chain → converter → Kafka`, so the SMT operates on the structured record before it is serialized.
- **Why the others are wrong:** A — the direction is inverted. On a source the converter is last; on a sink it is first (`Kafka → converter → SMT chain → connector`). Either way an SMT never sees serialized bytes. B — `ReplaceField` renames fields with the `renames` property; a `Partitioner` is a producer concept and has nothing to do with Connect field names. C — `JsonConverter` has no `renames` property; converters know nothing about individual field names.
- 🧠 **Key point / trap:** *converter answers "what format", SMT answers "what shape"*. Add the direction rule: **source = SMT then converter, sink = converter then SMT**.
- 📎 Source: `../../study-plan/week-05/resources/connect-transforms-predicates.md`.

### Question 4 — Answer: **B, D**

- **Why correct:** B — `OfflinePartitionsCount` counts partitions with **no leader**. At 0, every partition still has a leader, so both produce and consume paths work. D — `UnderMinIsrPartitionCount` counts partitions whose ISR is smaller than `min.insync.replicas`. For those 22 partitions an `acks=all` write is rejected with `NotEnoughReplicasException`, which is **retriable**, so the producer keeps retrying until a replica catches up.
- **Why the others are wrong:** A — `UnderReplicatedPartitions` counts `|ISR| < |replicas|`, which is a durability signal, not a leadership signal; leaderless partitions would show up in `OfflinePartitionsCount`. C — exactly one node in the cluster must report `ActiveControllerCount=1`, so a cluster-wide sum of 1 is the healthy value regardless of how many brokers are down. E — the minimum-ISR check is applied on the **write** path only; consumers read up to the high watermark and are unaffected.
- 🧠 **Key point / trap:** three counters, three different failures — `UnderReplicated` = reduced durability, `UnderMinIsr` = writes blocked, `OfflinePartitions` = availability lost. Only the last one stops reads.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-broker-metrics.md`.

### Question 5 — Answer: **B**

- **Why correct:** a `GlobalKTable` is **fully replicated to every instance** and bootstrapped completely before the application reaches `RUNNING`. Eight instances × 120 GB is 960 GB of duplicated state and a 40-minute cold start, which is exactly what the symptoms describe. A `GlobalKTable` is meant for small, slowly changing lookup data. Making it a `KTable` partitions the state so each instance holds only its share; the price is that the stream must be re-keyed on the join key so the two sides are co-partitioned.
- **Why the others are wrong:** A — standby replicas add *more* copies of state; they shorten failover but make the disk and bootstrap problem worse. C — a KStream-KStream join requires both sides to be streams and a join window, which changes the semantics from "look up current customer" to "match events in a time window". D — `statestore.cache.max.bytes` is a write-deduplication cache in front of the store, not a sizing knob for the store itself; 120 GB will never be cached.
- 🧠 **Key point / trap:** `GlobalKTable` trades **memory/disk on every instance** for **no co-partitioning requirement**. Once the table stops being small, that trade goes the wrong way and a repartition plus `KTable` is cheaper.
- 📎 Source: `../../study-plan/week-06/resources/streams-joins.md`.

### Question 6 — Answer: **A**

- **Why correct:** `min.insync.replicas=3` on an RF=3 topic means every single replica must be in the ISR before an `acks=all` write is accepted — so taking one broker down blocks writes, which is what `NOT_ENOUGH_REPLICAS` says. Setting `min.insync.replicas=2` still guarantees that an acknowledged record is on **two** replicas, so losing one broker loses nothing, while leaving enough headroom for a one-at-a-time restart.
- **Why the others are wrong:** B — `acks=1` acknowledges after the leader alone persists the record, so a leader failure before replication loses acknowledged data. That violates the stated requirement. C — unclean leader election deliberately trades data loss for availability, and it would not make the write succeed here anyway. D — the log already shows `2147483646 attempts left`: `retries` defaults to `Integer.MAX_VALUE` and the retries are already happening. More retries do not make the ISR bigger; they only delay the eventual failure.
- 🧠 **Key point / trap:** `min.insync.replicas` equal to RF is the classic over-correction — it buys no extra durability over RF−1 but costs you all rolling-restart headroom. With RF=3 the answer is always **2**. The "2147483646 attempts left" in the log is the tell that retry tuning is a dead end.
- 📎 Source: `../../study-plan/week-02/resources/kafka-replication-isr.md`.

### Question 7 — Answer: **B**

- **Why correct:** `MockProducer` implements `Producer<K,V>` and ships inside `kafka-clients`, so no extra test library is needed. With `autoComplete=false` each `send()` returns a future that stays pending until the test calls `completeNext()` or `errorNext(RuntimeException)`; `errorNext` completes the future exceptionally **and** invokes the registered callback, which is exactly what drives the dead-letter path. `history()` returns every `ProducerRecord` sent since the last `clear()`, whether or not its future has completed, so the key and headers can be asserted.
- **Why the others are wrong:** A — `autoComplete=true` (the first argument) completes every `send()` immediately and successfully, so there is no pending call left and `errorNext()` simply returns `false`. C — `MockProducer` does invoke callbacks; that is its main reason to exist. D — `uncommittedRecords()` only lists records sent inside an **open transaction**, which this test does not have, and the public `sendException` field makes `send()` itself throw synchronously rather than routing the error through the callback.
- 🧠 **Key point / trap:** the `autoComplete` flag is the whole question. `true` = happy path only; `false` + `completeNext()`/`errorNext()` = you control success and failure, which is how you unit-test retry and DLQ logic without a broker.
- 📎 Source: `../../study-plan/week-07/resources/kafka-mock-clients-javadoc.md`.

### Question 8 — Answer: **D**

- **Why correct:** KIP-1030 changed the producer default `linger.ms` from **0 to 5** in Kafka 4.0. Every symptom follows: batches now wait up to 5 ms, so `batch-size-avg` and `records-per-request-avg` jump and p99 latency rises by roughly the linger value. The minimal fix for a latency-critical workload is to set `linger.ms=0` explicitly, which was the implicit behaviour before the upgrade.
- **Why the others are wrong:** A — `batch.size` still defaults to 16,384 and is only a **ceiling**; it never causes the producer to wait. B — `linger.ms` does **not** still default to 0 (that is the stale value), and the `acks` default changed in **3.0**, not 4.0, so it cannot explain a 3.9 → 4.3 regression. C — `compression.type` still defaults to `none`, and compression would not add a consistent few milliseconds of latency to every send.
- 🧠 **Key point / trap:** this is the single most common stale number in CCDAK material. Kafka 4.0 mnemonic: **5 / 2 / 1 hour / 1 MB** — `linger.ms`=5, `num.recovery.threads.per.data.dir`=2, future-timestamp limit 1 hour, minimum `segment.bytes` 1 MB. A latency regression of "about 5 ms" right after a 4.x client upgrade is `linger.ms` until proven otherwise.
- 📎 Source: `../../study-plan/week-03/resources/kip-1030-defaults-kafka-4-0.md`.

### Question 9 — Answer: **A, C**

- **Why correct:** A — retention deletes whole **closed** segments; the active segment is never eligible. A segment closes when it reaches `segment.bytes` (default 1 GB) or `segment.ms` (default 7 days) has elapsed. At 30 MB/day split over 6 partitions, the size trigger will never fire, so the topic effectively inherits a 7-day floor. C — lowering `segment.ms` to about 30 minutes makes segments close frequently, after which `retention.ms=1h` actually removes them. The practical delay becomes roughly `segment.ms` + `retention.ms` plus one `log.retention.check.interval.ms` cycle (default 5 minutes).
- **Why the others are wrong:** B — `retention.ms` and `retention.bytes` are independent; either one on its own triggers deletion. D — compaction keeps the **latest value per key** and never applies an age rule; `compact,delete` would combine both, but plain `compact` deletes nothing by age. E — the log retention thread runs continuously on `log.retention.check.interval.ms`, not only at startup.
- 🧠 **Key point / trap:** "I set a short `retention.ms` and the data is still there" is always the **active segment**. On low-volume topics you must lower `segment.ms` (or `segment.bytes`) as well, otherwise the retention setting is decorative.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md`.

### Question 10 — Answer: **C**

- **Why correct:** when the DLQ topic does not exist, the worker's admin client creates it using `errors.deadletterqueue.topic.replication.factor`, whose default is **3** (and one partition). On a single-broker development cluster that request fails with exactly this `InvalidReplicationFactorException`. Setting the property to `1` for the dev environment fixes it.
- **Why the others are wrong:** A — Connect does auto-create the DLQ topic; the error text ("Replication factor: 3 larger than available brokers: 1") is a *create* failure, not a describe failure. B — `errors.tolerance=all` is valid on its own; `errors.retry.timeout` is an independent, optional setting. D — the replication factor comes from the connector's own `errors.deadletterqueue.topic.replication.factor` property, not from the broker's `default.replication.factor`, and broker settings are not what this error reports.
- 🧠 **Key point / trap:** three DLQ facts to keep together — **sink connectors only**, `...topic.replication.factor` defaults to **3**, and `...context.headers.enable` defaults to **false** (turn it on or the DLQ record carries no `__connect.errors.*` explanation of why it failed).
- 📎 Source: `../../study-plan/week-05/resources/connect-error-handling-dlq-kip298.md`.

### Question 11 — Answer: **B**

- **Why correct:** on the classic protocol the coordinator declares a member dead when no heartbeat arrives within `session.timeout.ms`, whose default has been **45,000 ms** since Kafka 3.0 (KIP-735). `heartbeat.interval.ms` stayed at 3,000, so a healthy member sends roughly 15 heartbeats per session window. A SIGKILLed pod is therefore detected after about 45 seconds, and the rebalance follows.
- **Why the others are wrong:** A — 10,000 is the pre-3.0 default, still quoted in older courses. C — `max.poll.interval.ms` (300,000) detects an application that has stopped calling `poll()`, not a process that has died; a dead process stops heartbeating first, so the session timeout always wins. D — `heartbeat.interval.ms` is the send frequency, and a single missed heartbeat is not an eviction; the coordinator waits out the whole session timeout.
- 🧠 **Key point / trap:** two clocks, two failure modes. **Process died** → `session.timeout.ms` (45 s). **Process alive but stuck in user code** → `max.poll.interval.ms` (5 min). If crash detection is too slow, the knob is the session timeout — and lowering it is the price of static membership.
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-configs.md`.

### Question 12 — Answer: **C**

- **Why correct:** 1-X — `TimeWindows` with `advanceBy` shorter than the window size is a **hopping** window: fixed size, fixed advance, overlapping, so each record falls into `size / advance` windows (five here). 2-Y — `SessionWindows` are **session** windows: variable length, driven by an inactivity gap per key. 3-Z — `SlidingWindows.ofTimeDifference` defines windows by the maximum time difference between records, with inclusive endpoints, and creates a window only when a record arrives. 4-W — a `TimeWindows` with no `advanceBy` is **tumbling**: advance equals size, so windows do not overlap and every record lands in exactly one.
- **Why the others are wrong:** A — swaps hopping and sliding; sliding windows are not created on a fixed schedule. B — makes the plain `TimeWindows` overlapping and the `advanceBy` variant non-overlapping, which is backwards. D — swaps session and sliding.
- 🧠 **Key point / trap:** the four window types are a guaranteed CCDAK topic. Distinguish by what determines the boundary: **clock schedule** (tumbling and hopping), **record spacing** (sliding), **inactivity** (session). Tumbling is just hopping with `advance == size`.
- 📎 Source: `../../study-plan/week-06/resources/streams-dsl-api.md`.

### Question 13 — Answer: **A**

- **Why correct:** the high watermark is the highest offset replicated to **every replica currently in the ISR**, and consumers may only read up to it. When the ISR shrinks to the leader alone, "every member of the ISR" means the leader, so the high watermark advances the instant the leader appends — latency to visibility drops to nearly zero. That is also exactly when durability is at its worst: with `min.insync.replicas=1` the write is accepted, acknowledged, and exists on one disk.
- **Why the others are wrong:** B — follower fetching requires explicit rack-aware configuration and never happens automatically, and the followers here are out of sync, so they hold *less* data, not more. C — the broker never silently weakens a durability request; `acks=all` means "all in-sync replicas", and the set of in-sync replicas is what changed. D — replication traffic is not what gates visibility; the high watermark is, and `acks=all` waits for the ISR, not for all replicas.
- 🧠 **Key point / trap:** "records became visible faster" during an incident is a **durability alarm**, not a performance win. It means the ISR collapsed. The pairing to remember: `acks=all` + `min.insync.replicas=1` is the configuration that looks safe and is not.
- 📎 Source: `../../study-plan/week-02/resources/kafka-replication-isr.md`.

### Question 14 — Answer: **C**

- **Why correct:** `poll-idle-ratio-avg` is the fraction of time `poll()` spends waiting for data rather than the application spending time in user code. At 0.04 the consumer is busy processing 96% of the time. `time-between-poll-max` of 287,000 ms sits just under the 300,000 ms `max.poll.interval.ms`, so the worst iteration nearly missed the deadline — and the zero rebalance count confirms it has not been evicted **yet**. The two standard remedies both shorten one iteration: fewer records per poll (`max.poll.records`, default 500) or faster per-record work.
- **Why the others are wrong:** A — `rebalance-rate-per-hour` is 0 and `failed-rebalance-total` is 0, so nothing is thrashing; raising `session.timeout.ms` addresses heartbeats, which are fine here. B — a `poll-idle-ratio-avg` near 0 means the opposite of starvation: the consumer never waits for data because it is always behind. D — with 1.9 M records of backlog the fetcher is clearly not short of data to return; making fetches bigger would lengthen each iteration and push `time-between-poll-max` over the limit.
- 🧠 **Key point / trap:** `time-between-poll-max` approaching `max.poll.interval.ms` is the one metric that predicts an eviction **before** it happens. Read it together with `poll-idle-ratio-avg` to decide whether the fix is "fetch less per poll" or "make processing faster".
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md`.

### Question 15 — Answer: **D**

- **Why correct:** `initTransactions()` runs **once per producer instance**, before the loop — it registers the `transactional.id` with the coordinator, fetches a producer ID and bumps the epoch, fencing any zombie from a previous incarnation. Then each iteration is: `poll()` for input (5), `beginTransaction()` (4), `send()` the outputs (2), `sendOffsetsToTransaction()` to bring the input offsets into the same transaction (6), and `commitTransaction()` (1).
- **Why the others are wrong:** A — begins the transaction before polling, and worse, commits the transaction *before* sending the offsets, so the offsets would land outside it and exactly-once is broken. B — `initTransactions()` must complete before any transactional call; polling first is harmless but the option also implies init happens per batch, which is wrong. C — `beginTransaction()` before `initTransactions()` throws `IllegalStateException`: the producer has no producer ID yet.
- 🧠 **Key point / trap:** *init once, begin/send/sendOffsets/commit per batch*. Offsets must go in **before** the commit; the whole point is that output records and input offsets become visible atomically.
- 📎 Source: `../../study-plan/week-03/resources/kip-98-exactly-once-transactions.md`.

### Question 16 — Answer: **D**

- **Why correct:** a distributed Connect worker's `group.id` names the **worker group** — the coordination group the workers themselves use, whose offsets in `__consumer_offsets` are tiny and unrelated to any connector's data. Every **sink** connector runs its own consumer group named `connect-<connector-name>`, so the lag of `es-orders` lives under the group `connect-es-orders`, and that is what `kafka-consumer-groups.sh --describe` must target.
- **Why the others are wrong:** A — sink connectors are ordinary consumers and do form a consumer group; `status` shows task state, not position. B — `connect-offsets` holds **source** connector positions (which are connector-defined, e.g. a file offset or a binlog position); sinks do not use it. C — overriding the connector's consumer group id is not supported for sinks; the framework derives it from the connector name precisely so operators can find it.
- 🧠 **Key point / trap:** two different offset stores. **Sink** = consumer group `connect-<name>` in `__consumer_offsets`, resettable with `kafka-consumer-groups.sh`. **Source** = the `connect-offsets` topic, resettable with `DELETE /connectors/<name>/offsets` while STOPPED.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md`.

### Question 17 — Answer: **A, B**

- **Why correct:** A — `MockConsumer` has no group coordinator, so `subscribe()` only records the subscription; nothing is ever assigned. `rebalance(Collection<TopicPartition>)` simulates the assignment **and** fires `onPartitionsRevoked`/`onPartitionsAssigned` on the registered listener, which is the only way to exercise rebalance-listener logic in a unit test. B — the mock needs a position for each assigned partition; without `updateBeginningOffsets(...)` (for an `earliest` reset strategy) `poll()` throws `IllegalStateException`, which is the exact symptom described.
- **Why the others are wrong:** C — `MockConsumer(OffsetResetStrategy)` is **deprecated since 4.0**; the supported constructor takes the `auto.offset.reset` value as a `String`, which the code already uses. D — `setMaxPollRecords(long)` caps how many records one `poll()` returns; it does not create an assignment or a position. E — the whole point of `rebalance(...)` is that listeners *can* be tested without a coordinator; Testcontainers is the right tool for broker-dependent behaviour, not for this.
- 🧠 **Key point / trap:** the `MockConsumer` recipe is three steps in a fixed order: **assign (or subscribe + rebalance) → updateBeginningOffsets → addRecord**. Skipping the middle step is the standard `IllegalStateException`.
- 📎 Source: `../../study-plan/week-07/resources/kafka-mock-clients-javadoc.md`.

### Question 18 — Answer: **C**

- **Why correct:** the KRaft controller quorum is a Raft group: with 3 voters, a majority of 2 is required to commit anything to `__cluster_metadata`. Losing two leaves one voter, which can neither elect itself leader nor commit records. The consequence is precise: **metadata writes stop** (no leader elections, no ISR changes, no topic or ACL changes), while brokers keep serving produce and fetch on existing partitions from the metadata they already hold — degrading only as individual brokers fail with nobody to elect replacements.
- **Why the others are wrong:** A — brokers do not need a live controller to serve traffic on partitions whose leadership is unchanged; the data plane and the metadata plane are separate. B — a single voter out of three is a minority and can never become leader; that is the entire point of a quorum. D — `process.roles` is a static configuration read at startup, and brokers never promote themselves.
- 🧠 **Key point / trap:** quorum arithmetic — **3 controllers tolerate 1 loss, 5 tolerate 2**, which is why an even number buys nothing. And know the failure shape: losing the quorum freezes the control plane first, not the data plane.
- 📎 Source: `../../study-plan/week-01/resources/kafka-operations-kraft.md`.

### Question 19 — Answer: **A**

- **Why correct:** 1-Y — `max.block.ms` (60,000) bounds how long `send()` and `partitionsFor()` may **block** the calling thread waiting for metadata or for accumulator memory. 2-Z — `delivery.timeout.ms` (120,000) is the total upper bound from `send()` returning until the record is reported as delivered or failed, covering linger, every retry and every request attempt. 3-X — `request.timeout.ms` (30,000) applies to **one** in-flight request. 4-W — `linger.ms` (5) is how long a non-full batch waits. 5-V — `batch.size` (16,384) is a byte ceiling on a single per-partition batch.
- **Why the others are wrong:** B — swaps `max.block.ms` and `delivery.timeout.ms`: 60,000 is the blocking bound, 120,000 the delivery bound. C — swaps `delivery.timeout.ms` and `request.timeout.ms`; the validation rule `delivery.timeout.ms ≥ linger.ms + request.timeout.ms` only makes sense with delivery as the outer bound. D — swaps `linger.ms` and `request.timeout.ms`, which are three orders of magnitude apart.
- 🧠 **Key point / trap:** nest them mentally: `request.timeout.ms` (one attempt) ⊂ `delivery.timeout.ms` (all attempts) — and `max.block.ms` sits outside both because it governs the **calling thread**, not the network.
- 📎 Source: `../../study-plan/week-03/resources/producer-configs.md`.

### Question 20 — Answer: **A**

- **Why correct:** a KStream-KTable join is a **stream-driven lookup**. Each record on the stream side triggers a lookup against the current value in the table; an update on the table side only changes what subsequent stream records will see. Re-emitting historical results would require the stream's past records to be retained, which a `KStream` does not do — only KTable-KTable joins are triggered from both sides.
- **Why the others are wrong:** B — KStream-KTable joins are explicitly **non-windowed**; `JoinWindows` belongs to KStream-KStream joins. C — materialization controls whether the table's state is queryable and how it is stored; it never changes which side triggers output. D — a `GlobalKTable` is even more one-sided: a `KStream`-`GlobalKTable` join is also stream-driven, and a `GlobalKTable` update never emits anything.
- 🧠 **Key point / trap:** learn the join matrix by **what triggers output**: KStream-KStream both sides (windowed), KStream-KTable stream side only, KStream-GlobalKTable stream side only, KTable-KTable both sides. "The table changed but nothing was emitted" is correct behaviour, not a bug.
- 📎 Source: `../../study-plan/week-06/resources/streams-joins.md`.

### Question 21 — Answer: **B**

- **Why correct:** exactly one node in a KRaft cluster reports `ActiveControllerCount=1`, so the cluster-wide sum is the health signal. A 40-second reading of 0 across a controller failover is the classic shape: the old active controller lost quorum leadership, the remaining voters elected a new one, and for that interval nobody was active. Metadata operations — creating a topic is one — fail during the gap, while brokers continue serving produce and fetch from cached metadata for partitions whose leadership has not changed.
- **Why the others are wrong:** A — if all controllers were gone the cluster would still serve existing partitions, but the gap would not be a clean 40 seconds followed by recovery, and produce traffic continuing is evidence against total failure, not an artefact. C — dedicated controllers expose the metric; that is precisely how you know which one is active. D — a sum of 0 cannot come from two nodes reporting 1; and KRaft's Raft quorum prevents two simultaneous active controllers by construction.
- 🧠 **Key point / trap:** alert on `ActiveControllerCount ≠ 1` **sustained**, not instantaneous — a brief 0 during failover is normal, a persistent 0 means no quorum and a persistent 2 means your scrape targets are wrong.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-broker-metrics.md`.

### Question 22 — Answer: **B**

- **Why correct:** 1-X — `BACKWARD` (the default) means the **new schema can read old data**, which permits deleting a field or adding one with a default, checked only against the immediately previous version; consumers are upgraded first. 2-Y — `FORWARD` means **old schema can read new data**, which permits adding a field (with or without a default) or deleting an optional one; producers are upgraded first. 3-W — `FULL` is both directions at once, so only fields **with defaults** may be added or removed. 4-Z — the `_TRANSITIVE` variants apply the same rule against **every** registered version rather than just the last.
- **Why the others are wrong:** A — swaps `BACKWARD` and `FORWARD`, which also inverts the upgrade order; this is the single most-tested confusion in the topic. C — makes `BACKWARD` behave like `FULL` and `FULL` like `FORWARD`. D — makes `BACKWARD` transitive and `BACKWARD_TRANSITIVE` non-transitive, which is the definition reversed.
- 🧠 **Key point / trap:** anchor on the **upgrade order**, not the field rules: `BACKWARD` → **consumers first**, `FORWARD` → **producers first**, `FULL` → either. Then derive the permitted change from there. A required field with no default is never allowed under `BACKWARD` — it returns HTTP 409.
- 📎 Source: `../../study-plan/week-05/resources/schema-registry-compatibility.md`.

### Question 23 — Answer: **C**

- **Why correct:** `assign()` takes manual control of specific partitions with no group coordination at all — no `JoinGroup`, no rebalance, and no interference with the `billing` group's committed offsets (as long as the tool does not commit). `offsetsForTimes(Map<TopicPartition, Long>)` translates the wall-clock instant into the offset of the first record with a timestamp at or after it, and `seek(tp, offset)` positions the consumer there before the poll loop starts.
- **Why the others are wrong:** A — `subscribe()` with any `group.id` joins a group and reads all partitions; filtering in code wastes the whole topic's bandwidth and still does not give a timestamp start position. B — `--reset-offsets --execute` requires the group to be **inactive** and would rewind the live `billing` consumers, which is exactly what must not happen. D — using `group.id=billing` makes the tool a member of the production group: it triggers a rebalance, steals partitions from real consumers, and its `seek()` would rewind live processing.
- 🧠 **Key point / trap:** the reflex is *"read specific partitions, don't disturb anyone" → `assign()`*, and *"start at a point in time" → `offsetsForTimes()` + `seek()`*. `--reset-offsets` is the operational equivalent but demands an idle group.
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-javadoc.md`.

### Question 24 — Answer: **D**

- **Why correct:** the log cleaner works on the "dirty" portion of the log — the closed segments after the last cleaned offset — and only starts once the dirty ratio reaches `min.cleanable.dirty.ratio` (0.5). The **active segment is never compacted**. So a consumer reading at the head (A) sees the raw, uncompacted tail of the log with every intermediate update, while a full replay (B) sees the compacted region (one record per key) plus whatever dirty-but-not-yet-cleaned records sit after it — which is why B occasionally sees two or three records for a key.
- **Why the others are wrong:** A — compaction is a background rewrite of segment files on disk, not a read-time filter; `isolation.level` concerns transaction markers and is unrelated. B — the dirty ratio is a *trigger threshold* for running the cleaner, not a retention proportion; it does not preserve half the records per key. C — a compacted topic makes no guarantee of exactly one record per key at any instant; the guarantee is that the **latest** value for every key that has not been tombstoned is retained.
- 🧠 **Key point / trap:** compaction guarantees *"you will always find the latest value for a key"*, never *"you will find only one record per key"*. The head of the log is uncompacted by definition, which is why compacted topics are safe for real-time consumers.
- 📎 Source: `../../study-plan/week-02/resources/kafka-log-compaction.md`.

### Question 25 — Answer: **A**

- **Why correct:** `TopologyTestDriver` runs the topology in the caller's thread, processing each `pipeInput` record to completion and flushing before returning, so no caching or commit interval ever coalesces results — every intermediate aggregation is forwarded. A real application buffers updates in the record cache (`statestore.cache.max.bytes`, 10 MB by default) and flushes on eviction or at `commit.interval.ms` (30,000 ms), so a burst of updates to the same key typically yields one downstream record with the final count.
- **Why the others are wrong:** B — `at_least_once` permits duplicates, never silent drops; and the missing records are not lost, they are conflated (the last count is still correct). C — `TopologyTestDriver` fully supports state stores, and they are queryable through `driver.getKeyValueStore(...)`; the test would not produce correct running counts otherwise. D — `suppress` is a windowed-emit control; this topology is not windowed, and suppression would reduce output further rather than reconciling the two environments.
- 🧠 **Key point / trap:** `TopologyTestDriver` is a **semantics** test, not a **timing** test. Assert on the final state store value, or on the set of results, rather than on the exact number of intermediate records — otherwise the test encodes behaviour the real runtime does not promise.
- 📎 Source: `../../study-plan/week-06/resources/streams-testing-topologytestdriver.md`.

### Question 26 — Answer: **B**

- **Why correct:** a committed offset is always **the offset of the next record to read**, i.e. last processed + 1. `CURRENT-OFFSET 5000` therefore means offsets 0–4999 are done and the next fetch starts at 5000. `LOG-END-OFFSET 5120` is the offset the next produced record will receive, so the records still to read are 5000 through 5119 — exactly the 120 that `LAG` reports (`LEO − committed`).
- **Why the others are wrong:** A — this is the off-by-one the convention is designed to avoid; if 5000 had been processed the committed offset would be 5001. C — `LOG-END-OFFSET` is the next offset to be written, not a processed record, and `LAG` never counts records that retention has deleted. D — `CURRENT-OFFSET` in `kafka-consumer-groups.sh` is read from `__consumer_offsets`, so it is the **committed** offset; the in-memory fetch position is what the client-side `records-lag-max` metric uses, which is a different number.
- 🧠 **Key point / trap:** `commitSync(Map)` takes `new OffsetAndMetadata(record.offset() + 1)`. Forgetting the `+ 1` reprocesses one record per commit forever — a bug that never surfaces in tests because it looks like ordinary at-least-once duplication.
- 📎 Source: `../../study-plan/week-04/resources/kafka-ops-consumer-groups-share-groups.md`.

### Question 27 — Answer: **D**

- **Why correct:** 1-X — `OfflinePartitionsCount > 0` means partitions with **no leader**; produce and fetch both fail for them, which is the only one of the four readings that costs availability. 2-Z — `UnderReplicatedPartitions` high with `OfflinePartitionsCount = 0` means replicas are behind or a broker is down but every partition still has a leader: clients work, durability is reduced. 3-W — `IsrShrinksPerSec` and `IsrExpandsPerSec` rising together and in balance is **flapping**: a replica that keeps falling behind and catching up, typically GC pauses or saturated disk/network, not a hard failure. 4-Y — `RequestHandlerAvgIdlePercent` near 0 (healthy is well above 0.3) means the I/O thread pool is saturated and requests are queueing.
- **Why the others are wrong:** A — swaps the offline and under-replicated readings, which inverts "availability lost" and "durability reduced". B — makes under-replication mean flapping and flapping mean reduced durability; shrink/expand rates specifically indicate churn, while the URP gauge does not distinguish churn from a steady shortfall. C — swaps the flapping and thread-saturation symptoms, which come from entirely different metric families (`ReplicaManager` versus `KafkaRequestHandlerPool`).
- 🧠 **Key point / trap:** the triage ladder is `OfflinePartitionsCount` (availability) → `UnderMinIsrPartitionCount` (writes) → `UnderReplicatedPartitions` (durability) → ISR shrink/expand rates (churn). Answer the availability question before the durability one.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-broker-metrics.md`.

### Question 28 — Answer: **C**

- **Why correct:** Streams applies a different **default** for `commit.interval.ms` under exactly-once: 30,000 ms with `at_least_once`, but **100 ms** with `exactly_once_v2`, because under EOS a commit is a transaction commit and nothing becomes visible to `read_committed` consumers until it happens. An explicit `commit.interval.ms=30000` is honoured, so the application now commits — and therefore publishes — once every 30 seconds. Output is still exactly-once; only latency changed.
- **Why the others are wrong:** A — the value is a normal configuration and is not pinned; that is precisely why this mistake is possible. B — the commit interval has no effect on the processing guarantee; `processing.guarantee` alone determines it. D — 30,000 is the `at_least_once` default, not the EOS default; this is the stale number the question is built around, and the record cache would not produce a clean 30-second rhythm.
- 🧠 **Key point / trap:** under EOS, `commit.interval.ms` is your **end-to-end latency dial**, not just a checkpoint frequency. Raising it batches more work into each transaction (less overhead) at the cost of delaying every downstream `read_committed` reader by that interval.
- 📎 Source: `../../study-plan/week-06/resources/streams-config.md`.

### Question 29 — Answer: **D**

- **Why correct:** `tasks.max` is a **maximum**, and the connector's `taskConfigs(int maxTasks)` decides how many task configurations it actually returns. This S3 sink asked for all 10, and all 10 started — but a sink connector's tasks are consumers in a single group (`connect-s3-events`), so the usual rule applies: a partition has at most one owner within a group, and with 4 partitions the remaining 6 members own nothing. `FileStreamSource` is the opposite case: it tails one file, cannot split the work, and returns exactly one task configuration no matter what `tasks.max` says.
- **Why the others are wrong:** A — this is the normal, successful outcome of a rebalance, not a failed one; no assignor can give one partition to two members of the same group, so restarting changes nothing. B — tasks are *distributed* across workers, but their **count** comes from the connector, not the cluster size; 3 workers can run 1 task or 40. C — the first half is right (10 partitions would engage 10 sink tasks) but the second half is wrong: `FileStreamSource` is structurally single-task and is unaffected by the topic.
- 🧠 **Key point / trap:** `tasks.max` misleads in both directions — it never *forces* parallelism on a source that cannot split its work, and on a sink it can create tasks that exist but do nothing. Useful sink parallelism is capped by the **partition count**, exactly as it is for any consumer group.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md`.

### Question 30 — Answer: **A**

- **Why correct:** the classic join sequence is `FindCoordinator` (2) to locate the broker hosting the group's `__consumer_offsets` partition, then `JoinGroup` (4), where every member sends its subscription and the coordinator designates one member as **group leader** and forwards all subscriptions to it. The leader then computes the assignment locally (1) using the negotiated `partition.assignment.strategy`, and returns it in its `SyncGroup` request (3); the coordinator hands each member its own slice in the `SyncGroup` response. Only then does the member start heartbeating and fetching (5).
- **Why the others are wrong:** B — puts `SyncGroup` before the assignment is computed; the leader's `SyncGroup` request *is* how the assignment is delivered to the coordinator. C — `JoinGroup` cannot precede `FindCoordinator`, because the member does not yet know which broker to send it to. D — the assignment cannot be computed before `JoinGroup`, since the leader is chosen there and receives the subscriptions there.
- 🧠 **Key point / trap:** the cleanest way to tell the two protocols apart is **who computes the assignment**: a client (the group leader) under `classic`, the broker (the coordinator) under KIP-848's `consumer` protocol, where `JoinGroup`/`SyncGroup` disappear entirely.
- 📎 Source: `../../study-plan/week-04/resources/confluent-consumer-group-protocol-course.md`.

### Question 31 — Answer: **A**

- **Why correct:** the two limits are deliberately not equal. Producer `max.request.size` is **1,048,576** (a round 1 MiB), while broker/topic `message.max.bytes` is **1,048,588** — twelve bytes larger to accommodate record-batch overhead. Because the producer limit is the smaller one and is enforced client-side, an oversized record fails with `RecordTooLargeException` before any network call.
- **Why the others are wrong:** B — they differ by 12 bytes, which is exactly the trap; treating them as one number is how teams raise one and not the other. C — 1,000,000 was never the default; and inventing a stricter broker limit reverses which side rejects first. D — `max.request.size` caps the whole request (and thereby the largest uncompressed batch), while `message.max.bytes` caps the largest record batch the broker accepts, so the broker limit is not "far larger".
- 🧠 **Key point / trap:** the message-size chain has three links that must be raised **together**: producer `max.request.size` → broker/topic `message.max.bytes` (and `replica.fetch.max.bytes`) → consumer `max.partition.fetch.bytes`. Raising only the producer's is the standard half-fix.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md`.

### Question 32 — Answer: **C, E**

- **Why correct:** C — static membership (KIP-345) gives each pod a stable `group.instance.id`. The coordinator remembers its assignment, the pod does not send `LeaveGroup` on shutdown, and a restart that completes inside `session.timeout.ms` reclaims the same partitions with **no rebalance at all**. The 4.3 default of 45,000 ms already covers a 25-second restart, so nothing else needs tuning. E — `rebalance-latency-avg` of 210 ms is what cooperative rebalancing looks like: only partitions that change owner are revoked, so members that keep their partitions never stop processing. The lag therefore comes from how *often* rebalances happen, not how long each one takes.
- **Why the others are wrong:** A — `heartbeat.interval.ms` is the send frequency; a departing pod is detected by the session timeout (or by an explicit `LeaveGroup`), so a slower heartbeat delays detection without reducing the number of rebalances. B — `failed-rebalance-total = 0` only means every rebalance completed; 26 successful rebalances per hour is itself the problem. E's reading of the latency metric is the counter-argument to "processing is slow". D — `RangeAssignor` is neither sticky nor cooperative; switching to it would make every rebalance stop-the-world and move more partitions, not fewer.
- 🧠 **Key point / trap:** cooperative rebalancing makes each rebalance **cheap**; static membership makes rebalances **not happen**. On Kubernetes with frequent pod churn you want the second, and the two compose — they are not alternatives.
- 📎 Source: `../../study-plan/week-04/resources/kip-345-static-membership.md` and `../../study-plan/week-04/resources/kip-429-incremental-cooperative-rebalance.md`.

### Question 33 — Answer: **A, D**

- **Why correct:** A — the broker assigns a producer ID and the producer stamps each batch with a per-partition sequence number. The partition leader tracks the last sequence it appended for that PID; a retry carrying an already-seen sequence is acknowledged again without being written, which is what makes retries safe. D — the deduplication state is keyed by PID, and a restarted producer is issued a **new** PID, so nothing links the new session to the old one. Idempotence is therefore "no duplicates from *client retries* within one session, per partition", not "no duplicates ever".
- **Why the others are wrong:** B — the PID is allocated by the broker's `InitProducerId` request and has no relationship to `client.id`; there is no way to make it survive a restart without a `transactional.id`. C — the constraint is `max.in.flight.requests.per.connection ≤ 5`, not `= 1`; within that bound the broker can reorder-detect and the client retries in order. Setting it to 6 or more fails at **startup** with a `ConfigException` rather than silently disabling anything. E — the consumer has no idea that sequence numbers exist; `poll()` returns whatever is in the log.
- 🧠 **Key point / trap:** the scope sentence to memorise: **one producer session, one partition**. Duplicates across restarts, or atomicity across partitions, require **transactions** (`transactional.id`) or an idempotent consumer.
- 📎 Source: `../../study-plan/week-03/resources/kip-98-exactly-once-transactions.md`.

### Question 34 — Answer: **B, C**

- **Why correct:** B — a distributed Connect cluster is defined by its `group.id` plus its three internal topics. Copying the file unchanged means the new workers join the existing group and read and write the same `config.storage.topic`, so all six workers form one cluster and continuously rebalance connectors between themselves — which is exactly the "appearing on both clusters" symptom. C — separating them requires a distinct `group.id` **and** distinct `config.storage.topic`, `offset.storage.topic` and `status.storage.topic` names; `rest.port` only changes which socket the HTTP API listens on.
- **Why the others are wrong:** A — sharing the internal topics with different `group.id` values still means two clusters writing connector configs and task status into the same compacted topics, which corrupts each other's state; the topics must be separate too. D — `config.storage.topic` **must** have exactly one partition (ordering of config records depends on it); raising it to 25 breaks the cluster rather than separating two. E — Connect workers discover each other through the group coordinator using `group.id`, not through the REST port; REST is a client-facing API.
- 🧠 **Key point / trap:** the Connect internal-topic defaults are worth memorising as a triple — `connect-configs` **1** partition (mandatory), `connect-offsets` **25**, `connect-status` **5**, all compacted, RF 3 in production. And cluster identity is `group.id` + those three topic names, never the port.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md`.

### Question 35 — Answer: **B**

- **Why correct:** two independent 4.0 changes are colliding. Kafka 4.x is **KRaft-only**: ZooKeeper mode and the `zookeeper.connect` property were removed, so a ZooKeeper-based cluster must be migrated to KRaft while still on a 3.x release (3.9.x is the recommended last stop, since 4.x requires software and metadata version ≥ 3.3.x) before the binaries are swapped. Separately, Kafka 4.0 raised the broker and Connect JVM requirement to **Java 17**, which is what class file version 61.0 means.
- **Why the others are wrong:** A — `zookeeper.connect` no longer exists in 4.x and `inter.broker.protocol.version` is not how KRaft versions are managed (`kafka-features.sh` and the metadata version are); Java 11 is only supported for **clients and Streams**, not brokers. C — `zookeeper.connect` and `controller.quorum.voters` are not the same property renamed; they belong to two different architectures, and a KRaft node also needs `process.roles`, a formatted storage directory and a controller listener. D — both messages are precise and expected for this upgrade path; reinstalling changes nothing.
- 🧠 **Key point / trap:** the 4.0 breaking-change trio: **KRaft only**, **Java 17 for broker/Connect** (Java 11 still fine for clients/Streams), and **client protocol baseline 2.1**. There is no in-place ZooKeeper-to-4.x jump.
- 📎 Source: `../../study-plan/week-08/resources/kafka-upgrade-kraft.md`.

### Question 36 — Answer: **A, E**

- **Why correct:** A — `suppress(untilWindowCloses)` releases a window's final result when **stream time** — the maximum record timestamp the task has observed — passes window end plus grace. Stream time is data-driven, so a key whose traffic stops keeps its last window buffered indefinitely. E — suppression buffers and stream time are maintained **per task**, and each task owns specific input partitions. A partition receiving no records does not advance stream time at all, so none of the keys hashed to it emit, no matter how long wall-clock time runs.
- **Why the others are wrong:** B — Streams is event-time based by default; the grace period is measured in stream time, which is exactly why the low-traffic merchant is delayed. C — standby replicas are about failover of state, not about emission timing. D — `untilTimeLimit(...)` emits the **latest** value seen for a key after the time limit and then allows further updates for the same window, so it can produce several records per window; only `untilWindowCloses` gives the single final result.
- 🧠 **Key point / trap:** "final result" suppression trades timeliness for exactly-one-output. If the business needs a result at a wall-clock deadline, you need either steady traffic (a heartbeat record per partition is a common trick) or a punctuator, not `suppress`.
- 📎 Source: `../../study-plan/week-06/resources/streams-dsl-api.md`.

### Question 37 — Answer: **C**

- **Why correct:** since Kafka 3.0 the default `partition.assignment.strategy` is the **list** `[RangeAssignor, CooperativeStickyAssignor]`. A group selects the highest-priority strategy that every member supports, which is `RangeAssignor` — and `RangeAssignor` uses the EAGER protocol, so every member revokes everything on every rebalance, exactly as the log shows. Because `CooperativeStickyAssignor` is already present in every member's list, one rolling bounce that removes `RangeAssignor` flips the group to `COOPERATIVE` with no downtime.
- **Why the others are wrong:** A — `RangeAssignor` alone is the pre-3.0 default; adding the cooperative assignor to the end of the list changes nothing, because Range still wins the negotiation. This is the trap. B — cooperative rebalancing has existed in the **classic** protocol since Kafka 2.4 (KIP-429); KIP-848 is a separate, later redesign. D — `StickyAssignor` minimises partition movement but still reports `RebalanceProtocol.EAGER`; only `CooperativeStickyAssignor` is cooperative.
- 🧠 **Key point / trap:** `StickyAssignor ≠ CooperativeStickyAssignor`, and the list is negotiated by **first common entry**, so adding a better assignor after a worse one is a no-op. In 4.3 the fix is usually a removal, not an addition.
- 📎 Source: `../../study-plan/week-04/resources/kip-429-incremental-cooperative-rebalance.md`.

### Question 38 — Answer: **D**

- **Why correct:** each test is matched to the cheapest tool that can actually observe the behaviour. (1) is pure client-side logic — `MockProducer.history()` asserts the exact record with no broker. (2) depends on transaction markers, the last stable offset and broker-side filtering, none of which any mock implements, so it needs a real broker: `Testcontainers` `KafkaContainer` against `apache/kafka` (or the native image, which starts in under a second). (3) is topology semantics, which `TopologyTestDriver` evaluates in-process in milliseconds.
- **Why the others are wrong:** A — using Testcontainers for (1) pays container startup for an assertion that needs no broker, and `MockConsumer.setPollException` injects a client exception, which has nothing to do with transaction isolation. B — `MockConsumer` accepts no `isolation.level` semantics; it returns whatever records the test added, so the assertion would be vacuously true. C — `TopologyTestDriver` does **not** start a broker; it is an in-memory topology harness and cannot test (1) or (2).
- 🧠 **Key point / trap:** the decision rule is *"does the assertion depend on broker behaviour?"* If no → mocks or `TopologyTestDriver`. If yes (rebalance, `read_committed`, ACLs, TLS, real transactions) → Testcontainers. Mixing this up produces tests that pass and prove nothing.
- 📎 Source: `../../study-plan/week-07/resources/testcontainers-kafka.md` and `../../study-plan/week-07/resources/kafka-mock-clients-javadoc.md`.

### Question 39 — Answer: **B, D**

- **Why correct:** B — a topic's identity in KRaft metadata is a **topic ID** (a UUID), not just its name. Recreating the topic mints a new one, so any client still holding the old ID gets `UNKNOWN_TOPIC_ID` until its metadata refreshes. D — deleting a topic does not synchronously purge the group's entries in `__consumer_offsets`. The group therefore restarts with a committed offset far beyond the new log's end offset; the fetch position is out of range and `auto.offset.reset` decides what happens, which with `latest` means the group silently jumps to the end.
- **Why the others are wrong:** A — consumer groups are independent objects; deleting a topic does not delete groups (they are removed by `--delete` or by offset expiry). C — a recreated topic is created with **broker defaults** unless the create command supplies configs; `retention.ms`, `cleanup.policy` and everything else set on the old topic are gone. E — offsets are preserved as *numbers*, which is precisely the problem: they no longer refer to anything, so they cannot be resumed from.
- 🧠 **Key point / trap:** "delete and recreate the topic" is never a clean reset. You inherit stale committed offsets, lose all topic-level configuration, and hand every client a metadata refresh. Purging data is `kafka-delete-records.sh` or a short `retention.ms`, not a topic rebuild.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md` and `../../study-plan/week-04/resources/kafka-ops-consumer-groups-share-groups.md`.

### Question 40 — Answer: **A**

- **Why correct:** the offsets REST endpoints (Kafka 3.6+) require the connector to be in the `STOPPED` state, which is what `PUT /connectors/<name>/stop` produces: the configuration is retained, the tasks are deallocated, and the connector holds no source offsets open. `DELETE /connectors/<name>/offsets` then clears the stored positions, and `resume` restarts the tasks, which begin from scratch.
- **Why the others are wrong:** B — `pause` keeps the tasks allocated and merely stops them polling; the REST API rejects an offsets reset in that state, which is the 400 the operator already received. C — deleting a connector removes the connector and its config but **not** its entries in `connect-offsets`; recreating it under the same name resumes from the old position, which is the classic surprise. D — sink connectors use a consumer group (`connect-<name>`) resettable with `kafka-consumer-groups.sh`, but source connectors store connector-defined positions in `connect-offsets`, which that tool cannot touch.
- 🧠 **Key point / trap:** three connector states, three meanings — `PAUSED` (tasks alive, idle), `STOPPED` (tasks gone, config kept, offsets editable), `DELETE` (config gone, offsets kept). Only `STOPPED` unlocks the offsets API.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md`.

### Question 41 — Answer: **A, C**

- **Why correct:** A — `batch-size-avg` of 1,050 bytes against a 16,384-byte `batch.size` and only 3.5 records per request means batches are leaving almost empty; with 40,000 records/s spread over 24 partitions each partition gets roughly 1,700 records/s, so raising `linger.ms` to 50 ms accumulates about 85 records (~25 KB) per partition per batch. Raising `batch.size` to 131,072 stops the larger batch from being split. Request rate collapses by roughly an order of magnitude, which is what relieves the broker's network threads. C — compression is applied **per batch**, so the 0.92 ratio is a direct consequence of 1 KB batches; larger batches compress far better, and `lz4`/`zstd` deliver a comparable or better ratio at a fraction of gzip's CPU.
- **Why the others are wrong:** B — `max.in.flight.requests.per.connection=1` serialises requests per connection, adding latency and reducing throughput; batches do grow slightly as a side effect, but it is the wrong instrument and it costs pipelining. D — `acks=0` changes the durability contract (and is incompatible with the default `enable.idempotence=true`, so it would fail at startup unless idempotence is also disabled); the requirement says nothing about accepting data loss. E — more partitions means **fewer records per partition per unit time**, so batches get smaller and the request rate goes up. This is the intuitive-but-backwards option.
- 🧠 **Key point / trap:** throughput tuning is always the same pair — **give the accumulator time (`linger.ms`) and room (`batch.size`)**, then pick a cheap codec. Adding partitions is a *consumer* parallelism lever and actively hurts batching.
- 📎 Source: `../../study-plan/week-03/resources/confluent-producer-configs.md`.

### Question 42 — Answer: **B**

- **Why correct:** a follower stays in the ISR as long as it has fetched up to the leader's log end offset within `replica.lag.time.max.ms`, default **30,000 ms**. A 35–45 second stop-the-world pause freezes broker 3's replica fetcher threads past that window, so the leader removes those replicas; when the JVM resumes, they catch up and rejoin. Shrink and expand rates therefore rise together on one broker only. With RF=3 and `min.insync.replicas=2`, losing one replica still leaves two in the ISR, so `acks=all` writes continue to succeed — with a smaller safety margin during each shrink.
- **Why the others are wrong:** A — unclean leader election defaults to `false` and would show up as leadership changes and potential data loss, not as balanced ISR churn on one broker; and it does not make `acks=all` fail. C — `replica.lag.max.messages` was **removed in Kafka 0.9**; ISR membership has been purely time-based since then. This option is a pure legacy distractor. D — `OfflinePartitionsCount` is 0 and the churn is isolated to one broker, neither of which fits a controller problem; and with `min.insync.replicas=2` an ISR of 2 does not trigger `NotEnoughReplicasException`.
- 🧠 **Key point / trap:** shrink and expand rising **together and in balance** = flapping (fix the broker: GC, disk, network). A shrink with no matching expand = a genuinely lost or dead replica. The threshold is always `replica.lag.time.max.ms` = 30 s.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-broker-metrics.md` and `../../study-plan/week-02/resources/kafka-replication-isr.md`.

### Question 43 — Answer: **C**

- **Why correct:** the KTable-KTable **foreign-key join** is the one DSL join designed for tables whose keys differ. You supply a `foreignKeyExtractor` that pulls `customerId` out of each order value, and Streams maintains the relationship using internal subscription and response topics — so `orders` is never re-keyed, co-partitioning is not required, and an update on **either** table propagates to the result, which stays a `KTable`.
- **Why the others are wrong:** A — there is no KTable-GlobalKTable join in the DSL; `GlobalKTable` can only be joined from a `KStream`. B — co-partitioning is required for the *primary-key* KTable-KTable join, and Streams never repartitions a KTable automatically; mismatched partition counts throw a `TopologyException` at build time. D — `toStream().join(globalKTable, ...)` returns a `KStream`, and the join is stream-driven, so a change on the `customers` side would emit nothing — it fails the "updates when either side changes" requirement.
- 🧠 **Key point / trap:** two joins escape co-partitioning, for different reasons: **KStream-GlobalKTable** (the table is replicated everywhere) and **KTable-KTable foreign-key** (Streams builds the subscription plumbing). Everything else needs same partition count and same partitioning.
- 📎 Source: `../../study-plan/week-06/resources/streams-joins.md`.

### Question 44 — Answer: **D**

- **Why correct:** KIP-1030 raised the default of `num.recovery.threads.per.data.dir` from 1 to **2** in Kafka 4.0, so the runbook's premise is out of date. The name is literal: the value is applied **per entry in `log.dirs`**, so a broker with 8 data directories already runs 16 recovery threads. Raising it helps only while the disks still have headroom; beyond that it adds contention.
- **Why the others are wrong:** A — 1 is the pre-4.0 value, which is what makes the runbook look plausible. B — there is no broker-wide `num.recovery.threads` config; the per-directory scoping is the whole point, and it is why the total scales with `log.dirs`. C — recovery threads rebuild indexes and validate segments after an unclean shutdown for **every** log, compacted or not.
- 🧠 **Key point / trap:** this belongs to the same 4.0 default sweep as `linger.ms`: **5 / 2 / 1 hour / 1 MB**. And read "per data dir" literally — the effective thread count is the config value × the number of `log.dirs`.
- 📎 Source: `../../study-plan/week-03/resources/kip-1030-defaults-kafka-4-0.md`.

### Question 45 — Answer: **A**

- **Why correct:** KIP-848 reached general availability in Kafka 4.0, but **general availability is not the default**. `group.protocol` still defaults to `classic` in 4.3; the new protocol is opted into per consumer with `group.protocol=consumer`. The classic protocol is marked deprecated in 4.3, which signals a future change but does not alter today's behaviour. Because the group is still classic, `session.timeout.ms` and `partition.assignment.strategy` are very much in effect and deleting them would silently revert to their classic defaults.
- **Why the others are wrong:** B — `consumer` has never been the default; the `Classic` state in the describe output is the authoritative, current answer, not stale data. C — there is no per-topic `group.type=consumer`; `group.type=share` exists for share groups, which are an unrelated feature (KIP-932). D — the classic protocol is deprecated in 4.3, not removed; a group reporting `Classic` on matched 4.3 versions is simply the default.
- 🧠 **Key point / trap:** "GA" and "default" are different milestones, and CCDAK likes the gap. Under `group.protocol=consumer` the client's `session.timeout.ms`, `heartbeat.interval.ms` and `partition.assignment.strategy` are **silently ignored** in favour of broker-side group configs and `group.remote.assignor` (`uniform` or `range`) — so switching protocols is not a no-op.
- 📎 Source: `../../study-plan/week-04/resources/kip-848-consumer-rebalance-protocol.md`.

### Question 46 — Answer: **C, D**

- **Why correct:** C — a predicate is inert until a transformation references it. The idiomatic way to drop records is the `Filter` SMT, which drops **every** record it sees and is therefore only useful with a predicate attached (`transforms.<alias>.predicate=isTombstone`); the alias must also appear in the `transforms` list or the transformation never runs. D — `transforms` is an ordered list and the chain is applied in that order, so the filter must precede `dropSsn`; otherwise `ReplaceField$Value` is handed a null value first and throws.
- **Why the others are wrong:** A — `negate` defaults to `false` already, and setting it explicitly changes nothing; predicates never filter on their own. B — SMTs can absolutely remove a record from the pipeline — that is what `Filter` does — while converters only translate formats. E — `ReplaceField$Value` operates on the value and has no null guard of its own; the stack trace points at the SMT stage, not the converter.
- 🧠 **Key point / trap:** the predicate contract is three lines — declare it under `predicates`, give it a `type`, then **bind** it with `transforms.<alias>.predicate`. `Filter` without a predicate silently drops your entire topic, which is the other half of this trap.
- 📎 Source: `../../study-plan/week-05/resources/connect-transforms-predicates.md`.

### Question 47 — Answer: **B**

- **Why correct:** `MockProducer` implements the full transactional API (`initTransactions`, `beginTransaction`, `sendOffsetsToTransaction`, `commitTransaction`, `abortTransaction`) plus a set of inspection methods. After the transaction commits, `history()` holds the records sent since the last `clear()` — giving assertion (a) — `consumerGroupOffsetsHistory()` returns the list of offset maps committed through `sendOffsetsToTransaction` — giving assertion (b) — and `commitCount()` confirms exactly one transaction was committed rather than several.
- **Why the others are wrong:** A — the transactional API is fully supported by the mock; that is what makes unit-testing EOS logic possible without a broker. C — `uncommittedRecords()` and `uncommittedOffsets()` report what is pending **inside an open transaction**; after `commitTransaction()` both are empty, so the assertions would fail. D — `flushed()` reports whether all sends have completed and says nothing about offsets or transactions.
- 🧠 **Key point / trap:** remember the pairing — `uncommitted*()` before the commit, `history()` / `consumerGroupOffsetsHistory()` / `commitCount()` after. For the abort path, set the public `commitTransactionException` field or call `fenceProducer()` to simulate a `ProducerFencedException`.
- 📎 Source: `../../study-plan/week-07/resources/kafka-mock-clients-javadoc.md`.

### Question 48 — Answer: **C**

- **Why correct:** with the default `message.timestamp.type=CreateTime` the broker stores the producer's own timestamp. Time-based retention decides whether a segment may be deleted using the **largest** timestamp it contains, so one record dated 9 hours in the future keeps the whole segment alive for 9 extra hours — the 3.7 symptom. Kafka 4.0 (KIP-1030) changed `message.timestamp.after.max.ms` from `Long.MAX_VALUE` to **3,600,000 ms**, so a record more than an hour ahead of broker time is now rejected with `InvalidTimestampException` — the 4.3 symptom. Switching the topic to `message.timestamp.type=LogAppendTime` makes the broker stamp records itself and immunises both retention and the validation check against client clocks.
- **Why the others are wrong:** A — `log.message.timestamp.difference.max.ms` was **removed** in 4.0 and replaced by the `before`/`after` pair; and the limit is one hour, not zero, with `message.timestamp.after.max.ms` being raisable per topic. B — retention uses the record timestamp under `CreateTime`; it only uses append time when the topic is set to `LogAppendTime`. D — `message.timestamp.before.max.ms` still defaults to `Long.MAX_VALUE` (unlimited); the one-hour bound is on the **after** side, which is the side that matters for a fast clock.
- 🧠 **Key point / trap:** one skewed producer clock can pin a segment forever under `CreateTime`. The 4.0 guard is one-sided on purpose — future timestamps break retention and time-index lookups, past timestamps only make data expire sooner.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md` and `../../study-plan/week-03/resources/kip-1030-defaults-kafka-4-0.md`.

### Question 49 — Answer: **A, B**

- **Why correct:** A — the built-in partitioner for `null` keys is the **uniform sticky** partitioner (KIP-480/794): it keeps choosing one partition until that partition's batch is dispatched, then picks another. This produces large, well-compressed batches and even distribution over time, at the cost of short-term clustering — which is exactly what someone watching a burst of records observes. B — with a key, the partition is `murmur2(serialized key) % numPartitions`, deterministic and identical across producers and languages. The hazard is the modulus: increasing `numPartitions` changes the mapping for most keys, so records for one key can land in a different partition and the per-key order across the change is lost.
- **Why the others are wrong:** C — strict per-record round-robin was the pre-2.4 behaviour and is precisely what the sticky partitioner replaced, because it produced tiny batches. D — there is a default partitioner and it needs no configuration; partition count is irrelevant to whether it exists. E — invented. `partitioner.ignore.keys=true` makes the producer ignore keys entirely (giving even spread and losing key-based ordering), and no partition-count threshold changes the algorithm.
- 🧠 **Key point / trap:** the two reflexes — *"null key"* → sticky partitioner, *"ordering per key"* → set a key **and never increase the partition count afterwards**. If capacity must grow, create a new topic with the target partition count and migrate.
- 📎 Source: `../../study-plan/week-03/resources/kip-480-794-sticky-partitioner.md`.

### Question 50 — Answer: **D**

- **Why correct:** every number in the dump points at one cause. `batch-size-avg` of 310 bytes equals a single record, `records-per-request-avg` of 1.1 confirms one record per request, `record-queue-time-avg` of 0.4 ms shows nothing is waiting in the accumulator, and `compression-rate-avg` of 0.99 shows snappy has no repeated content to work with inside a one-record batch. That is the signature of `linger.ms=0`: the sender dispatches a batch the moment a record is available. Restoring the 4.3 default of 5 ms — or setting 10–20 ms — lets batches form, which cuts the request rate by roughly an order of magnitude and finally gives compression something to compress, for a few milliseconds of added latency.
- **Why the others are wrong:** A — `batch.size` is a **ceiling**, not a trigger. With `linger.ms=0` the batch is sent as soon as the sender is free, so a 1 MB ceiling changes nothing; the current average is 310 bytes against an existing 16 KB ceiling. B — `buffer-available-bytes` of 33.1 MB out of a 32 MB `buffer.memory` shows the buffer is essentially untouched, and `record-queue-time-avg` of 0.4 ms confirms it. C — the codec does not determine how many requests are issued; removing snappy would leave the request rate at 9,100/s and give up the compression that will become effective once batches grow.
- 🧠 **Key point / trap:** `linger.ms=0` is a real setting with a real cost, and "for lowest latency" is how it gets into configs. `batch-size-avg ≈ one record` plus a compression ratio near 1.0 is the fingerprint — and note that `batch.size` can never fix it, because only `linger.ms` makes the producer **wait**.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md` and `../../study-plan/week-03/resources/kip-1030-defaults-kafka-4-0.md`.

### Question 51 — Answer: **B, E**

- **Why correct:** B — `application.id` is used verbatim as the consumer `group.id`, so a new value means a group with no committed offsets. Streams overrides the client default and sets `auto.offset.reset=earliest`, so the application reprocesses the input topics from the beginning. E — `application.id` also prefixes every internal topic (`<app.id>-...-repartition`, `<app.id>-...-changelog`) and names the subdirectory under `state.dir`. New names mean new topics and a full state rebuild; the `fraud-scoring-v1-*` topics keep consuming disk until someone deletes them.
- **Why the others are wrong:** A — it is far more than cosmetic; the id is the group, the state directory and the internal topic prefix all at once. C — Kafka never renames topics, and Streams has no migration mechanism between application ids. D — `application.server` is an optional setting for interactive queries and is unrelated to startup validation.
- 🧠 **Key point / trap:** changing `application.id` **is** the documented way to deploy a topology as a brand-new application — but it is a full reset, not a restart: reprocess from earliest, rebuild all state, and orphan the old internal topics. Budget the reprocessing time before doing it in production.
- 📎 Source: `../../study-plan/week-06/resources/streams-config.md`.

### Question 52 — Answer: **A**

- **Why correct:** `send()` must resolve metadata for the target topic before it can pick a partition, and the time it is allowed to block doing so is `max.block.ms`, whose default is **60,000 ms** — matching the message exactly. The topic genuinely does not exist on the staging cluster, and `auto.create.topics.enable=false` means the metadata request will never start returning it, so the call blocks for the full minute and then throws. The fix is to create the topic on staging or point `bootstrap.servers` at the intended cluster.
- **Why the others are wrong:** B — `request.timeout.ms` defaults to **30,000**, not 60,000, and it bounds a single RPC, not the metadata wait inside `send()`. C — `delivery.timeout.ms` defaults to **120,000**, and its errors concern a record that entered the accumulator; this record never got that far. D — `metadata.max.age.ms` defaults to **300,000** and is a proactive refresh interval, not a wait; and `flush()` cannot conjure a topic that does not exist.
- 🧠 **Key point / trap:** the number in the message identifies the config. Memorise the four producer timeouts and their defaults — `max.block.ms` 60,000, `request.timeout.ms` 30,000, `delivery.timeout.ms` 120,000, `metadata.max.age.ms` 300,000 — and "not present in metadata after N ms" is always `max.block.ms`.
- 📎 Source: `../../study-plan/week-03/resources/producer-configs.md`.

### Question 53 — Answer: **B**

- **Why correct:** Kafka 4.0 (KIP-896) removed the old protocol API versions, raising the minimum client the brokers will talk to from 0.10-era to **2.1**. A 0.10.2.1 client therefore fails during `ApiVersions` negotiation, while 3.x clients are comfortably above the baseline. There is no server-side compatibility switch: the only remedy is upgrading the client library. (The rule is symmetric — brokers must be ≥ 2.1 before Java clients are upgraded to 4.0.)
- **Why the others are wrong:** A — `inter.broker.protocol.version` governs the protocol between brokers and no longer exists in KRaft-based 4.x; it never controlled client compatibility. C — `message.format.version` / `log.message.format.version` was **removed in 4.0**; down-conversion for legacy clients is exactly the capability that was dropped. D — the failure is at protocol negotiation, not the TLS handshake, and 0.10.x clients do support TLS 1.2.
- 🧠 **Key point / trap:** the 4.0 compatibility floor is **client ≥ 2.1**, and it cuts both ways during an upgrade — upgrade any client older than 2.1 *before* the brokers, not after.
- 📎 Source: `../../study-plan/week-08/resources/kafka-upgrade-kraft.md`.

### Question 54 — Answer: **C**

- **Why correct:** KIP-298's error-handling framework wraps only the stages the Connect **runtime** executes: the key, value and header converters, the SMT chain, the Kafka consume/produce steps, and `SinkTask.put()` — the last only to the extent that the connector throws a `RetriableException`, which the framework retries. A non-retriable failure from inside the destination system, such as a primary-key violation raised by the JDBC driver, belongs to the connector's own error handling. The framework re-throws it, the task dies, and nothing reaches the DLQ (which is why `dlq-payments` is empty). The remedies are data-level: deduplicate upstream, or configure the connector for upsert semantics.
- **Why the others are wrong:** A — the replication factor only matters when Connect has to *create* the DLQ topic; the stack trace names the SQL exception, not a topic creation failure, and an empty-but-existing DLQ is consistent with "nothing was routed there". B — `errors.retry.timeout` is an independent optional setting with a default of 0; `errors.tolerance=all` works without it. D — DLQs are **sink-only**; the statement is precisely inverted. Source connectors are the ones that cannot have a DLQ.
- 🧠 **Key point / trap:** `errors.tolerance=all` protects you from **bad bytes** (deserialization, conversion, transformation), not from a **rejecting destination**. If the stack trace's `Caused by` names the target system rather than a converter or SMT, the DLQ was never going to catch it.
- 📎 Source: `../../study-plan/week-05/resources/connect-error-handling-dlq-kip298.md`.

### Question 55 — Answer: **D**

- **Why correct:** a `read_committed` consumer never fetches beyond the **last stable offset**, which is the first offset of the earliest still-open transaction (or the high watermark when no transaction is open). Both `endOffsets()` and the client's own `records-lag-max` are computed against that bound, so while the upstream producer holds a transaction open for five minutes the LSO is frozen and the lag arithmetic yields zero — even though the records are physically on the broker. The delay is the upstream commit cadence, not a consumer problem, and the fix is to commit transactions more frequently upstream.
- **Why the others are wrong:** A — `records-lag-max` is populated for every consumer; the isolation level changes the *bound* it measures against, not whether it exists. B — aborted records are filtered on the client after the fetch; they never make the offset arithmetic negative. C — switching the monitoring job to `read_uncommitted` would indeed reveal the true backlog, but switching the **consumer** would break its correctness guarantee by exposing it to records from transactions that may be aborted. The option conflates a measurement change with a semantics change.
- 🧠 **Key point / trap:** `read_committed` changes what "the end of the partition" means. Consumer lag for a transactional pipeline is bounded below by the producer's commit interval — measure end-to-end latency, not lag, and watch for a **flat zero** lag as the sign that an upstream transaction is open (or hung).
- 📎 Source: `../../study-plan/week-03/resources/kip-98-exactly-once-transactions.md`.

### Question 56 — Answer: **C**

- **Why correct:** the controller prefers, in order: a replica still in the **ISR** (3) — guaranteed to hold every committed record; then a replica in the **ELR** (1), the KIP-966 set of replicas that were in sync when the ISR shrank and are therefore known not to have lost data; then the **last known leader** (4) once it returns, which is the final clean option; and only with `unclean.leader.election.enable=true` would it fall back to an arbitrary surviving replica (2), accepting data loss for availability.
- **Why the others are wrong:** A — ELR is a fallback *behind* the ISR, never ahead of it; a live in-sync replica is always the best candidate. B — the last known leader ranks after the ELR: an ELR member is provably caught up to the high watermark at the time of the shrink, so it is tried first. D — the unclean fallback is the last resort of all, after the last known leader, and it is disabled by default.
- 🧠 **Key point / trap:** the chain is **ISR → ELR → last known leader → (unclean)**. ELR is the 4.x addition that closes the old gap where an ISR collapsing to one replica meant choosing between unavailability and data loss; it is enabled by default for clusters created on 4.1 and later.
- 📎 Source: `../../study-plan/week-02/resources/kafka-eligible-leader-replicas.md`.

### Question 57 — Answer: **A, D**

- **Why correct:** A — the whole point of the transactional API for consume-transform-produce is that the **input offsets** and the **output records** commit atomically. That requires `sendOffsetsToTransaction(offsets, consumer.groupMetadata())` inside the transaction and `enable.auto.commit=false` on the consumer; leaving auto-commit on would write offsets on a separate, untransactional path and reintroduce both duplicates and gaps. D — transactional writes are physically appended to the log immediately and are only hidden from `read_committed` readers. A downstream consumer left on the default `read_uncommitted` sees records from transactions that were later aborted, which defeats the guarantee at the last hop.
- **Why the others are wrong:** B — a random `transactional.id` per start is the classic anti-pattern: fencing works by the coordinator bumping the **epoch** for a *stable* id, so a random id means a restarted instance cannot fence its own zombie predecessor, and it also leaves transactional state to expire behind it. C — the input consumer's `isolation.level` governs what *it* reads (it matters in a chained EOS pipeline), but it has nothing to do with whether its offsets are committed transactionally; that is decided by `sendOffsetsToTransaction`. E — configuring `transactional.id` implies `enable.idempotence=true`, and it is the default in 4.3 anyway.
- 🧠 **Key point / trap:** exactly-once has **three** required pieces, and teams usually ship two: transactional producer with a stable id, `sendOffsetsToTransaction` with auto-commit off, and `read_committed` downstream. Miss the last one and the guarantee exists in the log but not in the consumer.
- 📎 Source: `../../study-plan/week-03/resources/kip-98-exactly-once-transactions.md`.

### Question 58 — Answer: **A**

- **Why correct:** `records-lag-max` belongs to `consumer-fetch-manager-metrics` and is computed inside a running consumer from its own fetch position against the partition's log end offset. When every pod is crash-looping there is no JVM to expose JMX, so the time series goes **absent** rather than large — and a threshold rule on an absent series never fires. Lag for a group that might not be running has to come from the broker side: the group's committed offsets in `__consumer_offsets` compared against log end offsets, which is what `kafka-consumer-groups.sh --describe`, `AdminClient.listConsumerGroupOffsets` plus `endOffsets`, or a dedicated lag exporter provide. The alert also needs a companion rule on member count or `absent()`.
- **Why the others are wrong:** B — a stopped consumer reports nothing at all, not 0; and `records-lead-min` is the same family of client-side metric, so it disappears too. C — client lag metrics are protocol-independent; both classic and KIP-848 groups publish them. D — `offsets.retention.minutes` defaults to **10,080** (7 days), so a 40-minute outage removes nothing, and even if offsets had expired the lag would be undefined, not zero.
- 🧠 **Key point / trap:** the two lag viewpoints answer different questions. **Client-side** (`records-lag-max`, fetch position) says *"how far behind is the thing that is reading"*; **broker-side** (committed offset) says *"how far behind is the group"* and keeps working when the group is gone. Production alerting needs the second, plus an absence rule.
- 📎 Source: `../../study-plan/week-08/resources/confluent-consumer-lag.md`.

### Question 59 — Answer: **B, C**

- **Why correct:** B — with `acks=0` the producer does not wait for any response, so the broker never reports an offset; the callback still fires and `RecordMetadata.offset()` (and the timestamp) come back as **-1**. C — retries exist to react to an error response. With no response there is no error to react to, so broker-side problems — a leader change, a full disk, a rejected batch — are invisible to the producer. Only failures the client can see itself, such as a serializer throwing or `buffer.memory` being exhausted, reach the application.
- **Why the others are wrong:** A — `acks=0` is a valid value on its own. What *is* rejected at startup is `acks=0` together with `enable.idempotence=true`, which is why the scenario disables idempotence explicitly. D — this is the opposite of the truth: during a leader change, in-flight records sent with `acks=0` are silently dropped, producing gaps rather than preserved order. E — the record is handed to the network and forgotten; `send()` returns before the broker has necessarily received it at all, let alone written it to the page cache.
- 🧠 **Key point / trap:** `acks=0` is not "slightly weaker durability" — it removes the **feedback channel**. You lose retries, offsets and error reporting together. Use it only where losing records is genuinely acceptable and you have another way to detect that the pipeline has stopped working.
- 📎 Source: `../../study-plan/week-02/resources/kafka-delivery-semantics.md`.

### Question 60 — Answer: **B**

- **Why correct:** `auto.offset.reset` is consulted in exactly two situations: the group has **no committed offset** for a partition, or its committed offset is **out of range** (retention deleted the data it pointed at). `none` makes both throw — `NoOffsetForPartitionException` for the first, `OffsetOutOfRangeException` for the second — which is the safety property the team wanted. The consequence is that a brand-new group has no automatic starting point, so the offsets must be seeded deliberately: `seekToBeginning()`/`seek()` inside `onPartitionsAssigned`, or `kafka-consumer-groups.sh --reset-offsets` before the first run.
- **Why the others are wrong:** A — `none` is valid with `subscribe()`; the exception it raises is the documented behaviour, not a misconfiguration. C — the exception explicitly names three existing partitions of `ledger`; a missing topic produces a metadata timeout or `UnknownTopicOrPartitionException` instead. D — auto-commit only writes offsets the consumer has actually reached, and the consumer cannot reach any position without first resolving one, so this changes nothing (and enabling auto-commit would weaken, not preserve, the reconciliation guarantee).
- 🧠 **Key point / trap:** `auto.offset.reset` never applies to a group that has a valid committed offset — which is why setting it to `earliest` on an existing group does **not** replay history. `none` converts both reset situations into loud failures, which is the right choice for financial reconciliation as long as you own the seeding step.
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-configs.md`.

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (48+/60) | Đạt ngưỡng cá nhân ngay ở mock đầu tiên. | Review 100% câu sai, mỗi câu đáng nhớ viết một file phân tích 6 mục trong [`../../questions/`](../../questions/README.md). Nghỉ 1 ngày rồi làm [Mock 02](../mock-02/questions.md). Đủ **cả 3 mock ≥ 80%** thì đặt lịch thi. |
| **70–79%** (42–47/60) | Gần đạt, lỗ hổng còn cục bộ. | Xác định domain thấp nhất trong bảng chấm điểm, dành **2 ngày** đọc lại đúng tuần đó + làm lại lab của tuần. Làm lại các câu sai của Mock 01 rồi mới sang Mock 02. **Chưa đặt lịch thi.** |
| **< 70%** (≤ 41/60) | Chưa sẵn sàng. | **Van an toàn: lùi lịch thi 1 tuần.** Quay lại 2 domain điểm thấp nhất, học lại Buổi A + B của các tuần tương ứng, làm mini-mock từng tuần, rồi mới thử Mock 01 lần hai. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / dính bẫy version / hết giờ), và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may cũng tính là câu sai.

---

## 🔁 Bản đồ câu sai → tuần cần học lại

| Chủ đề | Câu trong mock này | Học lại |
| --- | --- | --- |
| KRaft, quorum, upgrade path, client baseline | 18, 35, 53 | [Tuần 1](../../study-plan/week-01/README.md) + [Tuần 8](../../study-plan/week-08/README.md) `kafka-upgrade-kraft.md` |
| ISR, high watermark, `min.insync.replicas`, ELR, `acks` | 6, 13, 56, 59 | [Tuần 2](../../study-plan/week-02/README.md) — `kafka-replication-isr.md`, `kafka-eligible-leader-replicas.md` |
| Retention, segment roll, compaction, tombstone, timestamp | 9, 24, 48 | [Tuần 2](../../study-plan/week-02/README.md) — `kafka-topic-configs.md`, `kafka-log-compaction.md` |
| Message size chain, topic lifecycle | 31, 39 | [Tuần 2](../../study-plan/week-02/README.md) |
| Producer defaults, batching, compression, partitioner, send path | 1, 2, 8, 19, 41, 49 | [Tuần 3](../../study-plan/week-03/README.md) — `kip-1030-defaults-kafka-4-0.md`, `producer-configs.md` |
| Idempotence, transactions, `read_committed`/LSO | 15, 33, 55, 57 | [Tuần 3](../../study-plan/week-03/README.md) — `kip-98-exactly-once-transactions.md` |
| Producer timeouts & metadata | 52 | [Tuần 3](../../study-plan/week-03/README.md) — `producer-configs.md` |
| Consumer liveness, rebalance protocol, assignors, KIP-848 | 11, 30, 37, 45 | [Tuần 4](../../study-plan/week-04/README.md) — `kip-429-…`, `kip-848-…` |
| Offsets, commit `+1`, `auto.offset.reset`, `assign()`/`seek()` | 23, 26, 60 | [Tuần 4](../../study-plan/week-04/README.md) — `kafka-consumer-configs.md`, `kafka-consumer-javadoc.md` |
| Connect: converter vs SMT, predicates | 3, 46 | [Tuần 5](../../study-plan/week-05/README.md) — `connect-transforms-predicates.md` |
| Connect: DLQ, error handling, tasks, offsets, distributed mode | 10, 16, 29, 34, 40, 54 | [Tuần 5](../../study-plan/week-05/README.md) — `connect-error-handling-dlq-kip298.md`, `connect-user-guide-configs-rest.md` |
| Schema Registry compatibility | 22 | [Tuần 5](../../study-plan/week-05/README.md) — `schema-registry-compatibility.md` |
| Streams: joins, windows, suppression, `application.id`, EOS | 5, 12, 20, 28, 36, 43, 51 | [Tuần 6](../../study-plan/week-06/README.md) — `streams-joins.md`, `streams-dsl-api.md`, `streams-config.md` |
| Testing: mocks, `TopologyTestDriver`, Testcontainers | 7, 17, 25, 38, 47 | [Tuần 7](../../study-plan/week-07/README.md) — `kafka-mock-clients-javadoc.md`, `testcontainers-kafka.md` |
| Observability: broker metrics, controller, ISR churn | 4, 21, 27, 42 | [Tuần 8](../../study-plan/week-08/README.md) — `kafka-monitoring-broker-metrics.md` |
| Observability: client metrics, poll loop, lag, rebalance churn | 14, 32, 50, 58 | [Tuần 8](../../study-plan/week-08/README.md) — `kafka-monitoring-client-metrics.md`, `confluent-consumer-lag.md` |

> 🧠 **Đọc kết quả theo bẫy, không chỉ theo domain.** 9 câu của mock này đánh trực tiếp vào **mặc định đã đổi theo version** — 2, 8, 11, 28, 31, 35, 37, 44, 45. Nếu sai từ 3 câu trở lên trong nhóm này thì vấn đề không phải kiến thức Kafka mà là **tài liệu ôn đã lỗi thời**: đọc lại [`../../study-plan/VALIDATION.md`](../../study-plan/VALIDATION.md) §"Mặc định ĐÃ ĐỔI theo version" trước khi làm Mock 02.
