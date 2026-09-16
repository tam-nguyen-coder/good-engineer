# ✅ Answers & Explanations — Week 10: Cross-Domain Mock (30 questions)

> Open only after you have finished the timed run of [questions.md](questions.md) (45 minutes, no notes).
> Back to [week plan](README.md) · [master plan](../../KAFKA-STUDY-PLAN.md)

**Answer key:** 1-B · 2-A · 3-B · 4-B · 5-B · 6-AC · 7-B · 8-A · 9-B · 10-AC · 11-B · 12-AC · 13-AC · 14-B · 15-B · 16-B · 17-AB · 18-A · 19-B · 20-B · 21-AC · 22-BD · 23-A · 24-A · 25-B · 26-B · 27-A · 28-A · 29-AB · 30-B

---

## 📊 Chấm điểm theo domain

Đánh dấu từng câu đúng/sai rồi điền bảng. Cột **Ngưỡng** là mức tối thiểu cần đạt trước khi đăng ký thi thật.

| Domain | Tỉ trọng CCDAK | Câu số | Số đúng / Tổng | % | Ngưỡng |
| --- | --- | --- | --- | --- | --- |
| **DEV** — Application Development | 28% | 2, 6, 8, 11, 15, 18, 22, 27, 29 | ___ / 9 | ___ | ≥ 78% (7/9) |
| **FUND** — Fundamentals | 23% | 1, 7, 12, 16, 21, 24, 30 | ___ / 7 | ___ | ≥ 71% (5/7) |
| **CONNECT** — Kafka Connect | 15% | 3, 10, 17, 25 | ___ / 4 | ___ | ≥ 75% (3/4) |
| **OBS** — Observability | 13% | 5, 13, 19, 28 | ___ / 4 | ___ | ≥ 75% (3/4) |
| **STREAMS** — Kafka Streams | 12% | 4, 14, 20, 26 | ___ / 4 | ___ | ≥ 75% (3/4) |
| **TEST** — Application Testing | 8% | 9, 23 | ___ / 2 | ___ | ≥ 50% (1/2) |
| **TỔNG** | 100% | 1–30 | ___ / 30 | ___ | **≥ 80%** |

> 📌 Bộ 30 câu này phân bổ **đúng theo tỉ trọng đề thật**, nên phần trăm từng domain là chỉ báo đáng tin về vùng yếu. Ghi lại bảng này sau **mỗi** lần mock để thấy xu hướng, không chỉ điểm tổng.

---

### Question 1 — Answer: **B**

- **Why correct:** RF=3 with `min.insync.replicas=2` tolerates exactly one failure. After the first broker goes down the ISR still holds 2 replicas, so `acks=all` writes succeed. After the second failure the ISR drops to 1, below the minimum, and the leader rejects the write with `NotEnoughReplicasException`, which is **retriable** — the producer keeps retrying until a replica catches up and rejoins the ISR.
- **Why the others are wrong:** A — this ignores `min.insync.replicas`, which is checked on every `acks=all` write. C — `acks=all` means "all **in-sync** replicas", not "all replicas", so one failure is survivable. D — the broker never silently weakens a durability request.
- 🧠 **Key point / trap:** RF=3 / min.isr=2 / acks=all is the standard production triple and survives exactly **one** broker loss for writes. Reads are unaffected in both cases.
- 📎 Source: Week 2 `resources/kafka-replication-isr.md`.

### Question 2 — Answer: **A**

- **Why correct:** since Kafka 3.0 `enable.idempotence` defaults to `true`, and the idempotent producer requires `acks=all`. Explicitly setting `acks=1` contradicts that and the producer refuses to start. The minimal fix that preserves the lower latency is to also turn idempotence off explicitly.
- **Why the others are wrong:** B — `acks=1` is still perfectly valid. C — `max.in.flight` ≤ 5 is an idempotence constraint and lowering it to 1 does not reconcile `acks=1` with idempotence. D — `retries` defaults to `Integer.MAX_VALUE`, not 0.
- 🧠 **Key point / trap:** the three idempotence constraints are `acks=all`, `retries > 0` and `max.in.flight ≤ 5`. Breaking any of them while idempotence is on is a **startup** failure, not a runtime one.
- 📎 Source: Week 3 `resources/kip-1030-defaults-kafka-4-0.md`.

### Question 3 — Answer: **B**

- **Why correct:** the dead-letter queue is implemented in the sink task's record pipeline, so `errors.deadletterqueue.topic.name` only takes effect for **sink** connectors. A source connector can tolerate and log failures (`errors.tolerance=all` with `errors.log.enable=true`) but has nowhere to route them.
- **Why the others are wrong:** A — the source connector will silently drop records and never populate the DLQ. C — inverted. D — these are **connector**-level properties, not worker-level ones.
- 🧠 **Key point / trap:** "DLQ = sink only" is one of the most reliably tested Connect facts.
- 📎 Source: Week 5 `resources/connect-error-handling-dlq-kip298.md`.

### Question 4 — Answer: **B**

- **Why correct:** a `GlobalKTable` is fully replicated to every instance, so it imposes **no co-partitioning requirement**. The `KStream#join(GlobalKTable, KeyValueMapper, ValueJoiner)` overload takes a mapper that derives the lookup key from the stream record, so `productId` can be extracted from the click without rekeying or repartitioning the 24-partition stream. A 5,000-record reference topic is small enough to replicate everywhere.
- **Why the others are wrong:** A — a KStream-KTable join requires matching keys and co-partitioning; Streams does not silently rekey. C — repartitioning `products` still leaves the key mismatch, and a KStream-KStream join needs a window and both sides as streams. D — a foreign-key join works between two **KTables**, not from a KStream.
- 🧠 **Key point / trap:** "enrich a large stream with small reference data on a different key" → **GlobalKTable**. The cost is memory and disk on every instance.
- 📎 Source: Week 6 `resources/streams-joins.md`.

### Question 5 — Answer: **B**

- **Why correct:** the heartbeat thread is alive (so the session timeout is satisfied), CPU is low and the group rebalances every few minutes while each batch takes about 6 minutes. That is longer than the default `max.poll.interval.ms` of 300,000 ms, so the consumer leaves the group each cycle. The fix is to shrink the work per iteration (`max.poll.records`) or raise the limit.
- **Why the others are wrong:** A — heartbeats are sent by a background thread and are explicitly reported as healthy. C — `fetch.max.wait.ms` affects fetch latency, never membership. D — 50 partitions is the normal default for `__consumer_offsets` and has nothing to do with rebalances.
- 🧠 **Key point / trap:** two independent clocks. Slow **processing** breaks `max.poll.interval.ms`; a dead **process** breaks `session.timeout.ms`.
- 📎 Source: Week 4 `resources/kafka-consumer-configs.md`.

### Question 6 — Answer: **A, C**

- **Why correct:** committing only after the whole batch means the crash left nothing committed for that batch, so the new assignee re-reads all 500 records and the first 300 are processed twice — textbook at-least-once (A). Committing every N records with the map-based `commitSync` shrinks the replay window without changing the guarantee (C).
- **Why the others are wrong:** B — Kafka tracks a single offset per partition, not per-record acknowledgements (that is what share groups add). D — `commitAsync()` changes blocking behaviour, not the delivery guarantee. E — `isolation.level` controls visibility of transactional records; it does nothing about reprocessing after a crash.
- 🧠 **Key point / trap:** to actually remove the duplicates you need an **idempotent consumer** (dedupe key) or a transactional read-process-write loop, not a different commit call.
- 📎 Source: Week 4 `resources/kafka-consumer-javadoc.md` and Week 9 `resources/kafka-error-handling-retry-dlq.md`.

### Question 7 — Answer: **B**

- **Why correct:** tombstones are kept for `log.cleaner.delete.retention.ms`, default **86,400,000 ms = 24 hours**, precisely so that consumers have a window in which to observe the deletion. A consumer offline for 3 days can come back after the tombstone was cleaned and will therefore never see it — it simply finds no record for `user-42`.
- **Why the others are wrong:** A — `min.compaction.lag.ms=0` allows compaction to start early but does not govern tombstone removal. C — the dirty ratio decides **when the cleaner runs**, not how long tombstones survive. D — null values are exactly how deletion is expressed in a compacted topic.
- 🧠 **Key point / trap:** the practical rule is that consumers of a compacted topic must not lag longer than `delete.retention.ms`, otherwise they miss deletions and keep stale state forever.
- 📎 Source: Week 2 `resources/kafka-log-compaction.md`.

### Question 8 — Answer: **A**

- **Why correct:** this is the canonical consume-transform-produce loop. `initTransactions()` runs **once** at startup to register the `transactional.id` and fence older instances. Per batch the producer opens a transaction, sends output, includes the consumed offsets in the same transaction via `sendOffsetsToTransaction(offsets, consumer.groupMetadata())`, then commits. Downstream readers need `isolation.level=read_committed` to actually benefit.
- **Why the others are wrong:** B — `consumer.commitSync()` commits outside the transaction, which breaks atomicity, and `read_uncommitted` would expose aborted records. C — `initTransactions()` per batch is wrong and `flush()` plus `commitAsync()` gives no atomicity. D — auto-commit is never transactional.
- 🧠 **Key point / trap:** the two details that make it exactly-once are **`sendOffsetsToTransaction`** on the write side and **`read_committed`** on the read side. Missing either one silently degrades the guarantee.
- 📎 Source: Week 3 `resources/kip-98-exactly-once-transactions.md`.

### Question 9 — Answer: **B**

- **Why correct:** `TopologyTestDriver` executes the topology in-process with an in-memory state store and a virtual clock, so a windowed aggregation test runs in milliseconds with no container. `TestInputTopic` and `TestOutputTopic` pipe and assert records, and time can be advanced explicitly.
- **Why the others are wrong:** A — a container per test costs seconds to tens of seconds. C — mock clients cannot be wired into a `KafkaStreams` instance. D — state stores do not need a real broker in tests; the driver handles changelogs internally.
- 🧠 **Key point / trap:** the test pyramid for Kafka is `MockProducer`/`MockConsumer` for client code, `TopologyTestDriver` for topologies, Testcontainers for genuine broker behaviour.
- 📎 Source: Week 6 `resources/streams-testing-topologytestdriver.md`.

### Question 10 — Answer: **A, C**

- **Why correct:** the Schema Registry default is **BACKWARD** (A), which permits deleting a field and adding a field **that has a default**, so both planned changes register. BACKWARD means a consumer on the new schema can read data written with the old schema, which is exactly why consumers are upgraded first (C).
- **Why the others are wrong:** B — the default is BACKWARD, not FORWARD, and FORWARD is the mode where producers go first. D — BACKWARD explicitly allows deletions; it is **adding a field without a default** that it rejects. E — a subject holds many versions; renaming it would break the topic-name convention.
- 🧠 **Key point / trap:** memorise the pairing **BACKWARD → consumers first**, **FORWARD → producers first**, **FULL → either order, defaults required**.
- 📎 Source: Week 5 `resources/schema-registry-compatibility.md`.

### Question 11 — Answer: **B**

- **Why correct:** every pairing matches Kafka 4.3: `linger.ms` **5** (raised from 0 in 4.0), `batch.size` **16,384** bytes as a per-partition cap, `delivery.timeout.ms` **120,000** as the overall bound on `send()` including retries, and `max.block.ms` **60,000** for how long `send()` may block on a full buffer or missing metadata.
- **Why the others are wrong:** A — `linger.ms` is no longer 0 and `delivery.timeout.ms` is 120,000, not 30,000 (that is `request.timeout.ms`). C — `batch.size` is 16 KB, not 1 MB (1 MB is `max.request.size`), and `max.block.ms` is 60,000. D — `linger.ms` is 5, and `max.block.ms` is a **producer** setting, not a consumer poll timeout.
- 🧠 **Key point / trap:** matching-style questions punish "nearly right" sets. The four numbers to hold together are **5 / 16 KB / 120 s / 60 s**.
- 📎 Source: Week 3 `resources/producer-configs.md`.

### Question 12 — Answer: **A, C**

- **Why correct:** KRaft keeps cluster metadata in the replicated internal topic `__cluster_metadata` and ZooKeeper is removed entirely in 4.x (A). The controller quorum is a Raft group, so an odd voter count of 3 or 5 tolerates the loss of 1 or 2 controllers respectively (C).
- **Why the others are wrong:** B — combined mode is documented as suitable for development and testing; production should isolate controllers. D — `zookeeper.connect` no longer exists, and clients never used it for bootstrapping anyway. E — every node in one cluster must be formatted with the **same** `cluster.id`; different ids produce nodes that refuse to form a cluster.
- 🧠 **Key point / trap:** "odd number, 3 or 5, tolerates (n−1)/2 failures" plus "same cluster id everywhere" are the two KRaft facts most often tested.
- 📎 Source: Week 1 `resources/` (KRaft configuration) and Week 8 `resources/kafka-upgrade-kraft.md`.

### Question 13 — Answer: **A, C**

- **Why correct:** with a broker down, partitions that had a replica there now have fewer in-sync replicas than replicas, so `UnderReplicatedPartitions` rises above 0 on the surviving leaders (A). If the dead broker held the only in-sync replica for a partition and unclean election is disabled, no leader can be chosen and `OfflinePartitionsCount` becomes positive (C).
- **Why the others are wrong:** B — exactly one controller remains active; the sum across the cluster stays 1 unless the controller quorum itself is broken. D — Kafka never auto-creates replacement replicas; that requires a manual reassignment. E — `records-lag-max` is a **consumer client** metric, not a broker metric.
- 🧠 **Key point / trap:** `UnderReplicatedPartitions` means degraded redundancy, `OfflinePartitionsCount` means lost availability. The second is the more serious alarm.
- 📎 Source: Week 8 `resources/kafka-monitoring-broker-metrics.md`.

### Question 14 — Answer: **B**

- **Why correct:** enabling exactly-once in Streams changes the default `commit.interval.ms` from 30,000 ms to **100 ms**, so the application commits transactions roughly 300 times more often. Each commit writes transaction markers and flushes caches, which is what costs throughput. Raising `commit.interval.ms` recovers throughput at the price of higher end-to-end latency.
- **Why the others are wrong:** A — EOS **v2** was introduced precisely to use one producer per **thread** instead of one per task, so it is faster than the original `exactly_once`. C — caching is not disabled; more frequent commits simply flush it more often. D — EOS v2 needs brokers ≥ 2.5, and 4.3 brokers are well past that.
- 🧠 **Key point / trap:** the first tuning knob after switching on EOS in Streams is always `commit.interval.ms`.
- 📎 Source: Week 6 `resources/streams-config.md`.

### Question 15 — Answer: **B**

- **Why correct:** under KIP-848 the group coordinator on the broker computes the assignment using a server-side assignor (`uniform` by default, or `range`), reconciliation is incremental, and the client-side `partition.assignment.strategy`, `session.timeout.ms` and `heartbeat.interval.ms` are ignored in favour of broker-side group configs.
- **Why the others are wrong:** A — client-side assignors are exactly what the new protocol removes. C — the opposite is true; KIP-848 is a KRaft-era feature and ZooKeeper is gone. D — `classic` is still the default in 4.3; `consumer` is opt-in, and 4.3 only logs a deprecation warning for classic.
- 🧠 **Key point / trap:** the silent part is the danger — those three client configs are ignored **without any error**, so a migrated application can behave differently than its configuration file suggests.
- 📎 Source: Week 4 `resources/kip-848-consumer-rebalance-protocol.md`.

### Question 16 — Answer: **B**

- **Why correct:** the default partitioner computes `hash(key) % partitionCount`. Changing the count from 6 to 12 changes the result for most keys, so new records for a key can land on a different partition while all previously written records stay exactly where they are. Per-key ordering across the change is therefore lost.
- **Why the others are wrong:** A — Kafka never rewrites or moves existing records when partitions are added. C — ordering is guaranteed **within a partition**, never globally across a topic. D — inverted; partitions can be increased but never decreased.
- 🧠 **Key point / trap:** for a keyed topic, over-provision partitions at creation time. Adding them later is a data-ordering change, not just a capacity change.
- 📎 Source: Week 8 `resources/kafka-basic-ops-reassignment.md`.

### Question 17 — Answer: **A, B**

- **Why correct:** a distributed worker keeps connector configs, source offsets and statuses in three compacted internal topics with those default partition counts (A). Connectors are managed exclusively through the REST API on port 8083, and `tasks.max` caps how many tasks a connector may create (B).
- **Why the others are wrong:** C — **source** offsets live in `connect-offsets`; only **sink** connectors use a consumer group in `__consumer_offsets`. D — Connect uses the Kafka group protocol for worker coordination; ZooKeeper is not involved. E — in distributed mode connector configs come from the REST API and are shared by the cluster, not from each worker's properties file.
- 🧠 **Key point / trap:** remember **1 / 25 / 5** for configs / offsets / status, and that `tasks.max` is an upper bound the connector may legitimately undershoot.
- 📎 Source: Week 5 `resources/connect-user-guide-configs-rest.md`.

### Question 18 — Answer: **A**

- **Why correct:** `auto.offset.reset` defaults to `latest`, so a brand-new group with no committed offsets starts at the end of the log and sees only new records. With `none` the consumer throws `NoOffsetForPartitionException` because there is nothing to resume from. Reading the 30 days of history requires `earliest` on the first run.
- **Why the others are wrong:** B — the default is `latest`, and `fetch.min.bytes` only affects fetch batching. C — groups are created implicitly on first commit; no pre-seeding is needed. D — `none` means "fail if there is no committed offset", which is useful for detecting mistakes but is not a general production default.
- 🧠 **Key point / trap:** `auto.offset.reset` is consulted **only** when a committed offset is missing or out of range; it is not a "where to start every time" switch.
- 📎 Source: Week 4 `resources/kafka-consumer-configs.md`.

### Question 19 — Answer: **B**

- **Why correct:** the heartbeat thread runs independently of processing, so 50 seconds of CPU work does not breach `session.timeout.ms`. The poll-loop clock, `max.poll.interval.ms`, defaults to 300,000 ms, and 50 seconds is comfortably below it. Neither timeout evicts the consumer.
- **Why the others are wrong:** A — heartbeats continue during processing precisely because they live on a background thread. C — `heartbeat.interval.ms` is how often heartbeats are sent, not a timeout. D — `request.timeout.ms` bounds individual RPCs and does not remove group members.
- 🧠 **Key point / trap:** this is the mirror image of Question 5. Learn to check the actual processing duration against **300 s**, not against the 45 s session timeout.
- 📎 Source: Week 4 `resources/kafka-consumer-javadoc.md`.

### Question 20 — Answer: **B**

- **Why correct:** "the last 5 minutes, emitted every 1 minute, each record counted five times" is the definition of a **hopping** window: size 5 minutes with an advance of 1 minute. The 30-second grace period keeps late events eligible.
- **Why the others are wrong:** A — without `advanceBy` this is a tumbling window that emits once every 5 minutes and counts each record once. C — session windows group by inactivity gaps, which is a different concept entirely. D — a sliding window is defined by the time difference between records and is used mainly for joins and per-record windows, and this variant also drops the required grace period.
- 🧠 **Key point / trap:** tumbling is the special case of hopping where advance equals size. Whenever a question says each record contributes to several results, it is hopping.
- 📎 Source: Week 6 `resources/streams-dsl-api.md`.

### Question 21 — Answer: **A, C**

- **Why correct:** committing before processing means a crash in between loses those records, which is at-most-once (A). The idempotent producer assigns a producer id and per-partition sequence numbers so the broker discards duplicates caused by **retries within one producer session** (C).
- **Why the others are wrong:** B — idempotence covers the producer-to-broker hop only; end-to-end exactly-once additionally requires transactions plus `read_committed`, or an idempotent consumer. D — auto-commit gives at-least-once, never exactly-once. E — `acks=0` is the weakest setting and gives at-most-once, since the producer never learns whether the write landed.
- 🧠 **Key point / trap:** "idempotent producer ≠ exactly-once pipeline" is a favourite distractor. Scope it precisely: one session, one partition, retry-induced duplicates.
- 📎 Source: Week 2 `resources/kafka-delivery-semantics.md`.

### Question 22 — Answer: **B, D**

- **Why correct:** `RecordTooLargeException` (B) and `SerializationException` (D) are non-retriable. Retrying either sends the same oversized or unserializable record again, so the application must fix the payload, the serializer, or the size limits.
- **Why the others are wrong:** A — `NotLeaderOrFollowerException` is retriable; the client refreshes metadata and retries against the new leader. C — `NotEnoughReplicasException` is retriable and clears once the ISR recovers. E — `NetworkException` is a transient transport error and is retried.
- 🧠 **Key point / trap:** the test is "would retrying the identical request ever succeed?" For a too-large record or a broken serializer the answer is no, so the producer fails fast.
- 📎 Source: Week 3 `resources/kafkaproducer-javadoc.md`.

### Question 23 — Answer: **A**

- **Why correct:** `MockProducer` records every `ProducerRecord` passed to `send()` in `history()`, so the test can assert the exact topic, key, headers and value with no broker and no waiting. `autoComplete=true` completes the futures immediately so the code under test proceeds normally.
- **Why the others are wrong:** B — a real broker is correct for integration tests but violates the "no broker, milliseconds" requirement. C — `TopologyTestDriver` tests Streams topologies, not plain producer code. D — `MockConsumer` simulates consumption; it cannot observe what was sent.
- 🧠 **Key point / trap:** assert on `history()` rather than on a consumed record whenever the thing under test is *what the application decided to send*.
- 📎 Source: Week 7 `resources/kafka-mock-clients-javadoc.md`.

### Question 24 — Answer: **A**

- **Why correct:** retention is applied per **segment**, and the active segment is never deleted. With ~10 MB/day the active segment will not reach `segment.bytes` of 1 GB for years, and `segment.ms` of 7 days is the only other trigger, so nothing becomes eligible for deletion within the hour. Lowering `segment.ms` (or `segment.bytes`) makes the 1-hour retention effective.
- **Why the others are wrong:** B — topic-level `retention.ms` legitimately overrides the broker default, in both directions. C — `min.insync.replicas` concerns write durability and never disables retention. D — the `delete` policy is fully automatic; the cleaner thread is what compaction uses.
- 🧠 **Key point / trap:** "retention set but data is still there" is a segment-roll question, not a retention question. This also explains why the Week 2 retention lab sets `segment.ms` to a few seconds.
- 📎 Source: Week 2 `resources/kafka-topic-configs.md`.

### Question 25 — Answer: **B**

- **Why correct:** the converter is the boundary between Kafka bytes and Connect's internal record format, so deserializing Confluent Avro requires `AvroConverter` plus the Schema Registry URL. Field-level masking happens **after** conversion, in the transform chain, using the `MaskField$Value` SMT with `transforms.mask.fields=email`.
- **Why the others are wrong:** A — `JsonConverter` cannot read the Avro wire format and will fail on the 5-byte header. C — there is no Avro SMT, and converters are not named per transformation. D — converters have no masking options; that is precisely what SMTs are for.
- 🧠 **Key point / trap:** converter answers "what format is on the wire", SMT answers "how do I reshape each record". Mixing the two is the standard Connect distractor.
- 📎 Source: Week 5 `resources/connect-transforms-predicates.md`.

### Question 26 — Answer: **B**

- **Why correct:** within one sub-topology the task count equals the **largest** input partition count, so 12 tasks. Three instances with 2 threads each give 6 threads sharing those 12 tasks, about 2 tasks per thread when balanced. `num.standby.replicas=1` keeps one warm copy of each task's state on another instance, restored from the changelog topic, which shortens failover.
- **Why the others are wrong:** A — tasks are not the sum of partition counts, and standby replicas are passive, not throughput-adding. C — the task count follows the maximum, not the minimum, and a fourth instance cannot create more than 12 tasks. D — threads are not capped by instance count, and standby replicas work fine under EOS v2.
- 🧠 **Key point / trap:** parallelism ceiling = max input partitions. Adding instances beyond that leaves threads idle, exactly as extra consumers idle in a consumer group.
- 📎 Source: Week 6 `resources/streams-core-concepts-architecture.md`.

### Question 27 — Answer: **A**

- **Why correct:** static membership gives each pod a stable `group.instance.id`. The coordinator remembers its assignment, the pod does not send `LeaveGroup` on shutdown, and a restart completing inside `session.timeout.ms` reclaims the same partitions with **no rebalance at all**. Assignment logic itself is unchanged.
- **Why the others are wrong:** B — `heartbeat.interval.ms` is the send frequency, not a grace period, and 60 s would exceed the session timeout. C — different `group.id` values would create 20 separate groups, each consuming everything. D — `max.poll.interval.ms` bounds processing time, not restart time.
- 🧠 **Key point / trap:** the price of a long session timeout is slower detection of genuine crashes. Size it to the restart window, not larger.
- 📎 Source: Week 4 `resources/kip-345-static-membership.md`.

### Question 28 — Answer: **A**

- **Why correct:** the three signals line up into one story. An elevated `produce-throttle-time-avg` shows the broker is delaying responses because of a `producer_byte_rate` quota; delayed responses keep batches in the accumulator, which drives `record-queue-time-avg` up and `buffer-available-bytes` toward zero; once the 32 MB buffer is exhausted `send()` blocks for `max.block.ms` and then throws that exact `TimeoutException`. The remedy is to raise the quota or slow the producer down.
- **Why the others are wrong:** B — a high `linger.ms` would not produce broker-side throttle time, and setting it to 0 would only make batches smaller. C — partition count does not multiply `batch.size` against `buffer.memory` in the way described. D — `delivery.timeout.ms` governs the send deadline; the error message names the **memory allocation** timeout, which is `max.block.ms`.
- 🧠 **Key point / trap:** read the exception text carefully — "failed to allocate memory within the configured max blocking time" points at `buffer.memory` and `max.block.ms`, and the throttle metric identifies the upstream cause.
- 📎 Source: Week 8 `resources/kafka-monitoring-client-metrics.md` and Week 7 `resources/kafka-quotas.md`.

### Question 29 — Answer: **A, B**

- **Why correct:** `acks=all` with idempotence enabled means an acknowledged record is on all in-sync replicas and retries cannot create duplicates (A). `min.insync.replicas=2` with RF=3 is what makes "all in-sync replicas" meaningful — it guarantees at least two copies exist before the write is acknowledged, so losing one broker loses nothing (B).
- **Why the others are wrong:** C — `acks=1` acknowledges after the leader alone persists the record, so a leader failure before replication loses acknowledged data. D — unclean leader election deliberately trades data loss for availability, which is the opposite of the requirement. E — `min.insync.replicas=3` is *more* durable but makes writes fail as soon as any single broker is down, violating "even if one broker fails".
- 🧠 **Key point / trap:** min.isr equal to RF is the classic over-correction. With RF=3 the answer for surviving one failure is always **2**.
- 📎 Source: Week 2 `resources/kafka-replication-isr.md`.

### Question 30 — Answer: **B**

- **Why correct:** every requirement maps to share groups: more consumers than partitions, per-record acknowledgement with accept/release/reject, redelivery driven by a delivery-attempt count and an acquisition lock, and no ordering guarantee. Queues for Kafka reached general availability in 4.2, so a 4.3 cluster can use it.
- **Why the others are wrong:** A — in a classic consumer group a partition has at most one owner, so 14 of the 20 members would be idle. C — Streams tasks are also bounded by partition count, and Streams offers no per-record acknowledgement. D — no assignor gives a partition to several consumers of the same group; that is the invariant share groups were created to break.
- 🧠 **Key point / trap:** this is Kafka's answer to the `SQS` work-queue pattern you already know. The lock duration plays the role of the visibility timeout and the delivery limit plays the role of `maxReceiveCount`.
- 📎 Source: Week 2 `resources/kafka-share-groups.md`.

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (24+/30) | Đạt ngưỡng cá nhân. | Review 100% câu sai, viết file phân tích 6 mục trong `questions/KAFKA/`. Làm tiếp full mock **60 câu / 90 phút** từ một bộ practice khác. Đủ **3 bộ khác nhau ≥ 80%** thì đặt lịch thi. |
| **70–79%** (21–23/30) | Gần đạt, còn lỗ hổng cục bộ. | Xác định domain thấp nhất trong bảng chấm điểm, dành **2 ngày** đọc lại đúng tuần đó + làm lại lab của tuần. Mock lại sau đó, **chưa đặt lịch thi**. |
| **< 70%** (≤ 20/30) | Chưa sẵn sàng. | **Van an toàn: lùi lịch thi 1 tuần.** Quay lại 2 domain điểm thấp nhất, học lại Buổi A + B của các tuần tương ứng, rồi làm mini-mock của từng tuần trước khi thử full mock lần nữa. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / dính bẫy / hết giờ), và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may cũng tính là câu sai.
