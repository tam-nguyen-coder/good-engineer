# ✅ Answers — CCDAK Mock Exam 03

> Chỉ mở sau khi đã làm hết 60 câu trong [questions.md](questions.md) với đồng hồ 90 phút.
> Back to [mock index](../README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-C · 2-D · 3-C · 4-B · 5-B · 6-A · 7-C · 8-D · 9-C · 10-A · 11-D · 12-BD · 13-B · 14-D · 15-B · 16-C · 17-D · 18-AC · 19-B · 20-C · 21-B · 22-A · 23-BD · 24-B · 25-AC · 26-C · 27-BE · 28-D · 29-C · 30-C · 31-B · 32-D · 33-ACE · 34-A · 35-D · 36-A · 37-B · 38-BD · 39-C · 40-B · 41-AD · 42-D · 43-B · 44-CD · 45-C · 46-ABD · 47-D · 48-BC · 49-ACD · 50-A · 51-C · 52-B · 53-BC · 54-A · 55-AD · 56-D · 57-B · 58-A · 59-C · 60-B

---

## 📊 Chấm điểm theo domain

Đánh dấu từng câu đúng/sai rồi điền bảng. Câu `Multi`, `Matching`, `Ordering` chỉ tính đúng khi **khớp trọn vẹn** đáp án.

| Domain | Tỉ trọng CCDAK | Câu số | Số đúng / Tổng | % | Ngưỡng |
| --- | --- | --- | --- | --- | --- |
| **DEV** — Application Development | 28% | 2, 6, 9, 12, 16, 19, 23, 26, 30, 34, 37, 40, 44, 47, 52, 55, 59 | ___ / 17 | ___ | ≥ 76% (13/17) |
| **FUND** — Fundamentals | 23% | 1, 8, 11, 15, 20, 25, 29, 33, 39, 46, 51, 54, 58, 60 | ___ / 14 | ___ | ≥ 71% (10/14) |
| **CONNECT** — Kafka Connect | 15% | 3, 10, 17, 24, 31, 38, 45, 49, 56 | ___ / 9 | ___ | ≥ 78% (7/9) |
| **OBS** — Application Observability | 13% | 4, 13, 21, 27, 36, 41, 50, 57 | ___ / 8 | ___ | ≥ 75% (6/8) |
| **STREAMS** — Kafka Streams | 12% | 5, 14, 22, 28, 35, 42, 48 | ___ / 7 | ___ | ≥ 71% (5/7) |
| **TEST** — Application Testing | 8% | 7, 18, 32, 43, 53 | ___ / 5 | ___ | ≥ 60% (3/5) |
| **TỔNG** | 100% | 1–60 | ___ / 60 | ___ | **≥ 80% (48/60)** |

> 📌 Mock 03 kiểm tra **năng lực chọn phương án** chứ không phải trí nhớ config. Khi chấm, với mỗi câu sai hãy ghi rõ: *không biết kiến thức* hay *đọc sót qualifier*. Nếu phần lớn lỗi thuộc nhóm thứ hai, vấn đề của bạn là **kỹ thuật đọc đề**, không phải kiến thức — hãy tập gạch chân qualifier trước khi đọc options.

---

### Question 1 — Answer: **C**

- **Why correct:** the committee asked for durability over availability, and stated an explicit tolerance for downtime. `min.insync.replicas=2` with `acks=all` already blocks writes rather than accepting them unsafely. ELR (KIP-966 Part 1) is the piece that pays off *after* that: because the **strict min ISR** rule stops the high watermark advancing while `|ISR| < min.insync.replicas`, replicas that dropped out of the ISR at that point still hold every committed record. The KRaft controller records them in the partition's `Eligible Leader Replicas` field, and leader election tries ISR → ELR → last known leader.
- **Why the others are wrong:** A — unclean election is precisely "accept data loss to regain availability", the opposite of the stated position. B — `min.insync.replicas=1` lets a lone leader acknowledge writes that vanish if it dies; same trade in a different place. D — `acks=1` acknowledges before replication, so a leader failure loses acknowledged trades.
- 🧠 **Key point / trap:** ELR does **not** replace `unclean.leader.election.enable`, which is still `false` by default. ELR widens the set of *safe* candidates; unclean election widens the set of *any* candidates.
- 📎 Source: `../../study-plan/week-02/resources/kafka-eligible-leader-replicas.md`

### Question 2 — Answer: **D**

- **Why correct:** `record-queue-time-avg` measures how long a batch sits in the accumulator, and 12 ms of a 38 ms p99 is the accumulator wait created by `linger.ms=5` plus the time to fill a batch. Dropping `linger.ms` to 0 removes it and brings p99 to roughly 26 ms, inside the 30 ms budget. `acks`, `min.insync.replicas` and RF are untouched, so the durability requirement is intact.
- **Why the others are wrong:** A — the version trap: `linger.ms` has defaulted to **5** since Kafka 4.0 (KIP-1030), not 0, and a `batch-size-avg` of 2.1 KB against a 16 KB `batch.size` confirms batches are closing on time, not on size. B — `acks=1` acknowledges before replication and breaks the stated requirement (and, with idempotence on by default, would also fail at start-up). C — a larger `batch.size` makes records wait longer, not less.
- 🧠 **Key point / trap:** "reduce producer latency" → `linger.ms`; "increase throughput" → `linger.ms` **up** plus `batch.size` and compression. Know which direction the qualifier is pointing before you touch either.
- 📎 Source: `../../study-plan/week-03/resources/kip-1030-defaults-kafka-4-0.md`

### Question 3 — Answer: **C**

- **Why correct:** the qualifiers are "fewest lines of code the team owns" and "no new runtime service". Connect already runs, and a sink connector is configuration only — the framework supplies retries, DLQ routing, offset commits through the `connect-<name>` consumer group, and REST-based lifecycle management.
- **Why the others are wrong:** A — a hand-written consumer means owning buffering, retry, multipart upload, partition assignment and failure handling. B — Streams is a stream-processing library; using it purely as an S3 writer adds an application with no processing in it. D — Lambda works, but it is a new runtime, a new IAM surface and a function to maintain, which the "no new service" qualifier excludes.
- 🧠 **Key point / trap:** "move data between Kafka and an external system with no code" → **Connect**. Reach for Streams only when there is actual transformation, and for a plain consumer only when no connector exists.
- 📎 Source: `../../study-plan/week-05/resources/kafka-connect-101-course.md`

### Question 4 — Answer: **B**

- **Why correct:** diagnose first, because it is free and because skew invalidates everything after it: if one partition carries the load, adding members or partitions changes nothing. Then add consumers up to the partition count — no topic change, fully reversible. Then optimise the processing path — a code change but still reversible. Increasing the partition count comes last because it cannot be undone and it changes `murmur2(key) % partitions`, which breaks per-key ordering across the boundary.
- **Why the others are wrong:** A, C and D all place the irreversible partition increase before the free and reversible steps, and C starts with it.
- 🧠 **Key point / trap:** Kafka lets you *increase* partitions and never decrease them. Treat any partition-count change as a one-way door and spend the cheap options first.
- 📎 Source: `../../study-plan/week-08/resources/confluent-consumer-lag.md`

### Question 5 — Answer: **B**

- **Why correct:** both topics have 48 partitions, the same key and the same partitioner, so they are **co-partitioned** and a `KStream`-`KTable` join is legal without any repartitioning. The `KTable` is sharded across tasks, so each of the 6 instances materialises only the partitions it owns — roughly 10 GB, not 60 GB.
- **Why the others are wrong:** A — a `GlobalKTable` is fully replicated, so every instance would hold all 60 GB; it is the right tool for *small* reference data, not for a 40-million-row table. C — a foreign-key join is a `KTable`-`KTable` operation and the left side here is a stream; it would also add internal subscription topics. D — reducing `transactions` to 6 partitions destroys the parallelism that 90,000 records/s needs, and partition counts cannot be lowered in place anyway.
- 🧠 **Key point / trap:** `GlobalKTable` buys you "no co-partitioning, any lookup key" and charges you a full copy on every instance. When the keys already line up, `KTable` is both correct and cheaper.
- 📎 Source: `../../study-plan/week-06/resources/streams-joins.md`

### Question 6 — Answer: **A**

- **Why correct:** a consumer group can have at most one member per partition, so 12 partitions supports 12 members. Going from 4 to 12 triples consumption capacity, touches no producer, changes no key-to-partition mapping and needs no code at all — it is a replica-count change. Per-account ordering is a property of the key and the partition, so it is unaffected.
- **Why the others are wrong:** B — a share group assigns one partition to several members and acknowledges records individually, which is exactly how ordering is lost. C — more records per poll does not make processing faster and pushes the batch closer to `max.poll.interval.ms`. D — separate `group.id` values mean every instance reads **all** 12 partitions, so each one does four times the work it does now.
- 🧠 **Key point / trap:** before doing anything clever about lag, check whether the group is even using the partitions it already has. `members < partitions` is the cheapest fix there is.
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-configs.md`

### Question 7 — Answer: **C**

- **Why correct:** the Confluent serdes accept a `schema.registry.url` with the `mock://` scheme, which resolves to an in-process `MockSchemaRegistryClient` scoped to the name after the scheme. Nothing is written to the shared registry, no container starts, and both the serializer and the deserializer exercise the real Avro code path including the 5-byte wire prefix — which is exactly what the test is about.
- **Why the others are wrong:** A — correct but violates the "milliseconds, no Docker" constraint. B — swapping in `StringSerializer` removes the Avro serde, so the test proves nothing about schema resolution. D — `TopologyTestDriver` tests a Streams topology; there is no topology here.
- 🧠 **Key point / trap:** the test pyramid for Kafka is `MockProducer`/`MockConsumer` for client logic, `mock://` serdes for schema behaviour, `TopologyTestDriver` for topologies, Testcontainers for genuine broker behaviour. Pick the lowest rung that can actually observe the thing you are asserting.
- 📎 Source: `../../study-plan/week-07/resources/kafka-mock-clients-javadoc.md` and `../../study-plan/week-07/resources/testcontainers-kafka.md`

### Question 8 — Answer: **D**

- **Why correct:** the Kafka documentation states the trade explicitly — share groups give "finer-grained sharing of partitions and records … at the expense of record ordering". A partition may be assigned to several share consumers, each record is acquired under its own lock, and there is nothing that keeps two records of the same key in sequence. Ordering per key needs a consumer group, where a partition has exactly one owner.
- **Why the others are wrong:** A — `share.isolation.level` controls whether uncommitted transactional records are visible; it has nothing to do with the relative order of two committed records. B — the acquisition lock governs redelivery timing; lengthening it cannot serialise two concurrent workers. C — the minimum for `share.delivery.count.limit` is 2, so 1 is not even a legal value, and a delivery cap has no bearing on ordering.
- 🧠 **Key point / trap:** the whole point of share groups is to break the "one partition, one consumer" invariant. That invariant is also what gave you ordering. You cannot keep both.
- 📎 Source: `../../study-plan/week-02/resources/kafka-share-groups.md`

### Question 9 — Answer: **C**

- **Why correct:** each change fixes one hop, and following the data path gives 2 → 3 → 4 → 1. **2**: the database-to-Kafka hop is the dual-write problem, and only an outbox written inside the business transaction (published by CDC) removes it. **3**: the Streams stage is Kafka-to-Kafka, which is exactly what `exactly_once_v2` covers. **4**: every reader downstream of a transactional writer needs `read_committed`, otherwise it sees aborted records. **1**: the Kafka-to-DynamoDB hop is outside any Kafka transaction, so the sink itself must be idempotent.
- **Why the others are wrong:** A puts the external sink first and never fixes the source. B applies `read_committed` before there is a transactional writer to read from. D starts inside the topology and leaves the dual write in place, which is the hop that actually loses and invents events.
- 🧠 **Key point / trap:** "exactly-once end to end" is never one setting. It is three separate problems — ingest atomicity, in-Kafka processing, and sink idempotency — and Kafka transactions solve only the middle one.
- 📎 Source: `../../study-plan/week-09/resources/transactional-outbox-debezium.md` and `../../study-plan/week-06/resources/streams-config.md`

### Question 10 — Answer: **A**

- **Why correct:** validate, register, then deploy in the order the compatibility mode dictates. `POST /compatibility/subjects/<subject>/versions/latest` checks the candidate **without** creating a version, so a broken change never reaches the registry. `FORWARD` means a consumer on the **old** schema can read data written with the **new** one, so the producers may go first and the existing consumers keep working — hence 2 before 3.
- **Why the others are wrong:** B upgrades consumers first, which is the `BACKWARD` order. C registers before validating, which is the thing the requirement rules out. D deploys consumers before the schema even exists.
- 🧠 **Key point / trap:** memorise the pairing and then read the mode off the subject: **BACKWARD → consumers first** · **FORWARD → producers first** · **FULL → either order, every added or removed field needs a default**.
- 📎 Source: `../../study-plan/week-05/resources/schema-registry-compatibility.md`

### Question 11 — Answer: **D**

- **Why correct:** 1-X — committing before processing means a crash loses the un-processed records, which is at-most-once. 2-Y — committing after processing means a crash replays the batch, which is at-least-once. 3-Z — offsets and output inside one transaction, read with `read_committed`, is exactly-once **within Kafka**. 4-W — at-least-once delivery with sink-side deduplication is what is usually called effectively-once: Kafka still redelivers, the sink discards the repeat.
- **Why the others are wrong:** A swaps at-most-once and at-least-once. B maps the deduplicating sink onto plain at-least-once and vice versa. C calls the pre-processing commit exactly-once, which is the most expensive mistake on this list.
- 🧠 **Key point / trap:** the guarantee is decided by **where the commit sits relative to the side effect**, not by which commit method you call. `commitAsync()` versus `commitSync()` changes blocking, never semantics.
- 📎 Source: `../../study-plan/week-02/resources/kafka-delivery-semantics.md`

### Question 12 — Answer: **B, D**

- **Why correct:** B — a Kafka transaction covers the consumed offsets and the produced records atomically when `sendOffsetsToTransaction` carries `consumer.groupMetadata()`, and the guarantee only becomes visible to readers that set `isolation.level=read_committed`. D — Kafka transactions do not span external systems, so the PostgreSQL write must be idempotent in its own right; a unique constraint on `event_id` with `ON CONFLICT DO NOTHING` is the standard form.
- **Why the others are wrong:** A — `enable.idempotence=true` is indeed the default in 4.x, but the producer id is assigned by the broker per producer **session**; a restart gets a new one, so idempotence removes duplicates caused by retries inside one session, not across restarts. C — `read_committed` filters aborted transactions written by *others*; it does nothing about this service's own retries. E — fencing works precisely because the `transactional.id` is **stable**; a fresh random id on every start-up cannot fence the previous instance.
- 🧠 **Key point / trap:** the three scopes are easy to confuse — idempotent producer (retries, one session), transactions (Kafka only, across restarts via a stable `transactional.id`), sink idempotency (everything outside Kafka).
- 📎 Source: `../../study-plan/week-03/resources/kip-98-exactly-once-transactions.md`

### Question 13 — Answer: **B**

- **Why correct:** **lead** is the mirror image of lag: `records-lead-min` is the distance from the consumer's position down to the partition's **log start offset**. When it approaches 0 the retention cleaner is about to delete records the consumer has not read, which is the exact failure the alert must catch (this is why KIP-92 added it).
- **Why the others are wrong:** A — lag tells you how far behind the head you are, which correlates with the risk but never states it; a healthy pipeline can carry large steady lag and a doomed one can have small lag on a short-retention topic. C — a broker replication alarm, unrelated to retention. D — that warns about eviction from the group, a different failure.
- 🧠 **Key point / trap:** lag measures distance to the **end** of the log, lead measures distance to the **start**. Alert on both: lag for throughput, lead for data loss.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md`

### Question 14 — Answer: **D**

- **Why correct:** two event streams correlated by time is the textbook `KStream`-`KStream` windowed join; both topics are co-partitioned (24 partitions, same key, same producer), so it is legal. `leftJoin` supplies the unmatched clicks, and since Kafka 3.1 the unmatched side of a stream-stream left/outer join is emitted only **after the grace period**, which is precisely the "only once it is certain no match will arrive" requirement.
- **Why the others are wrong:** A — a `KStream`-`KTable` join has no window, so there is no way to express "within the previous 30 minutes", and it would match against whatever impression happened to be latest. B — a `GlobalKTable` join is also windowless, and replicating the impression stream to every instance makes no sense. C — a foreign-key join joins two tables; clicks are events, not a state per key.
- 🧠 **Key point / trap:** the only join type that takes a window is `KStream`-`KStream`. If the requirement contains a time span, that is the join.
- 📎 Source: `../../study-plan/week-06/resources/streams-joins.md`

### Question 15 — Answer: **B**

- **Why correct:** partition count has to satisfy the **tightest** of several constraints, and here it is the consumer side: 600 ÷ 15 = 40 members minimum, and a consumer group cannot have more members than partitions. 48 clears that floor, divides evenly by the 12 brokers so leadership is balanced, and leaves growth room. Going much higher costs open file handles, more producer memory, longer controller-driven leader elections after a failure and more end-to-end latency — and since the key mapping must stay stable, the count has to be right the first time.
- **Why the others are wrong:** A — 12 partitions caps the group at 12 members × 15 MB/s = 180 MB/s, less than a third of the requirement. C — 600 partitions is an order of magnitude past the need and pays every per-partition cost for nothing. D — 6 partitions is under a tenth of the required parallelism, and fewer partitions does not reliably mean lower latency once the partitions are saturated.
- 🧠 **Key point / trap:** size partitions from the **slowest consumer**, round up to a multiple of the broker count, then sanity-check against producer throughput. Never size them from ingress alone.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md` and `../../study-plan/week-08/resources/confluent-consumer-lag.md`

### Question 16 — Answer: **C**

- **Why correct:** `assign()` is manual partition assignment: no group coordinator, no rebalance, no membership, and — with no `group.id` — nothing written to `__consumer_offsets`. Combined with `seek()` it reads exactly the range asked for. The documented trade-off is that group tooling cannot report lag for such a consumer and the job must handle its own restart position.
- **Why the others are wrong:** A — a fresh `group.id` still creates a group that appears in `kafka-consumer-groups.sh --list`, still commits offsets that linger for `offsets.retention.minutes`, and `subscribe()` assigns **all** partitions, not just partition 3. B — seeking inside the production group moves that group's position and re-delivers everything to the production consumers. D — a share group has no per-partition position to seek, and it would be a second group on the topic with its own state.
- 🧠 **Key point / trap:** `subscribe()` = group membership, automatic assignment, rebalances, committed offsets. `assign()` = you own the partition list, the position and the failover. Read the question for which of those the scenario actually wants.
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-javadoc.md`

### Question 17 — Answer: **D**

- **Why correct:** an SMT is a per-record, stateless transformation (1 record in, 0 or 1 out), which covers projection, renaming and topic routing: `ReplaceField$Value` with `exclude=ssn` and `renames=cust_id:customerId`, then `RegexRouter` to rewrite the topic name. It cannot join, aggregate or window, so requirement (4) — attaching a value looked up from a second topic — belongs in Kafka Streams or ksqlDB.
- **Why the others are wrong:** A — the first three fit; the fourth does not, and no chaining makes an SMT stateful. B — a converter decides the wire format (bytes ↔ Connect `Struct`); it does not reshape or enrich records. C — a custom connector could do it, but that is the *most* moving parts, not the fewest, and it hard-codes business logic into an ingestion component.
- 🧠 **Key point / trap:** converter = "what format is on the wire"; SMT = "how do I reshape this one record"; Streams/ksqlDB = "how do I combine records". Connect questions almost always turn on which of the three the requirement needs.
- 📎 Source: `../../study-plan/week-05/resources/connect-transforms-predicates.md`

### Question 18 — Answer: **A, C**

- **Why correct:** A — `MockProducer` has a constructor taking a `Cluster` and a `Partitioner`, so the real custom partitioner runs against a declared 12-partition topic and the returned `RecordMetadata` carries the chosen partition. No broker, microseconds per case. C — `TopologyTestDriver` runs the topology in-process with a virtual clock; piping records with explicit timestamps past window end plus grace is exactly how a final-result assertion is written.
- **Why the others are wrong:** B — a real broker adds seconds per run and tests nothing the mock cannot, because the partitioner is pure client-side logic. D — `MockConsumer` replays records into a consumer; it has no window machinery. E — window closing in Streams is driven by **stream time** derived from record timestamps, not by any broker clock, so a real broker adds nothing here.
- 🧠 **Key point / trap:** partitioners, serializers, callbacks and commit logic are client-side and belong in mocks. Only rebalances, transaction visibility, ACLs and genuine broker failures justify a container.
- 📎 Source: `../../study-plan/week-07/resources/kafka-mock-clients-javadoc.md` and `../../study-plan/week-06/resources/streams-testing-topologytestdriver.md`

### Question 19 — Answer: **B**

- **Why correct:** 1-Y — the outbox exists for the dual-write problem: one local transaction writes both the entity and the event, and CDC publishes the event afterwards. 2-X — claim-check exists because a payload exceeds what the cluster will carry: store the blob elsewhere, publish the pointer. 3-Z — an idempotent consumer exists because at-least-once delivery will replay records and the sink must not apply the effect twice. 4-W — non-blocking retry topics exist so a slow or failing dependency does not hold the poll loop past `max.poll.interval.ms`.
- **Why the others are wrong:** A swaps outbox and idempotent consumer. C swaps claim-check and retry topics. D scrambles all four.
- 🧠 **Key point / trap:** each of these patterns has a **cost** the exam likes to test: outbox needs an application change, claim-check adds a second store on the read path, an idempotent consumer needs a durable dedupe key, and retry topics give up ordering.
- 📎 Source: `../../study-plan/week-09/resources/kafka-error-handling-retry-dlq.md`

### Question 20 — Answer: **C**

- **Why correct:** a compacted topic keeps at least the latest record per key, so the log size tracks the 20 million keys rather than the update rate, and a new service can rebuild the full state by reading from offset 0. Deletions are expressed as tombstones (null value), which is the stated requirement. The constraint that comes with it is `log.cleaner.delete.retention.ms`, **24 hours** by default: after that the cleaner may remove a tombstone, so a consumer lagging longer will never learn about the deletion and will keep stale state forever.
- **Why the others are wrong:** A — infinite retention under `delete` keeps every one of the ~1,000 updates per second forever, so storage grows with updates, which the requirement rules out, and bootstrap gets slower every day. B — mixing in `delete` with a 7-day retention deletes segments regardless of whether a key's latest value lives in them, so a customer who has not moved house in a week disappears from the state. D — share groups are a consumption model; they have nothing to say about what the log retains.
- 🧠 **Key point / trap:** "compacted topic as a key-value store" is a real pattern with one hard rule: **consumers must not lag longer than `delete.retention.ms`** or they miss deletions.
- 📎 Source: `../../study-plan/week-02/resources/kafka-log-compaction.md`

### Question 21 — Answer: **B**

- **Why correct:** every signal points the same way. `NOT_ENOUGH_REPLICAS` is returned by the **leader** when the ISR has fewer members than `min.insync.replicas`, which with RF=3 / min.isr=2 means the ISR has shrunk to 1. It is a **retriable** error, so the producer keeps retrying with its default `retries=Integer.MAX_VALUE` until the overall bound `delivery.timeout.ms` — **120,000 ms** — expires, which is exactly the `120001 ms has passed since batch creation` in the second log line. `UnderReplicatedPartitions=37` with `UnderMinIsrPartitionCount=4` is the broker-side view of the same event, and `OfflinePartitionsCount=0` proves leaders still exist. The problem is a missing or lagging broker, not client configuration.
- **Why the others are wrong:** A — raising `delivery.timeout.ms` would only make the producer wait longer for a condition it cannot influence; it treats the symptom. C — `acks=all` means all **in-sync** replicas, not all replicas; a single slow follower drops out of the ISR and the remaining two still satisfy min.isr. There is also no `acks=2`. D — a lost metadata quorum would show `ActiveControllerCount` misbehaving and would not leave partition leaders serving traffic; the dashboard shows exactly 1.
- 🧠 **Key point / trap:** read the two log lines as cause and effect. `NOT_ENOUGH_REPLICAS` is the cause (broker side), `Expiring N record(s) … 120001 ms` is the producer giving up after `delivery.timeout.ms`.
- 📎 Source: `../../study-plan/week-02/resources/kafka-replication-isr.md` and `../../study-plan/week-08/resources/kafka-monitoring-broker-metrics.md`

### Question 22 — Answer: **A**

- **Why correct:** Streams changes `commit.interval.ms` from **30,000** to **100** automatically when `processing.guarantee=exactly_once_v2`, because under EOS every commit interval is a transaction and a long interval would hold records invisible to `read_committed` readers for half a minute. The visible consequences are lower end-to-end latency for those readers and a large increase in commit and transaction-marker traffic on the brokers. EOS also needs at least three brokers in the default configuration, because `transaction.state.log.replication.factor` is 3 with `transaction.state.log.min.isr=2`.
- **Why the others are wrong:** B — there is always a cost; pretending otherwise is how EOS gets switched on in a single-broker staging cluster and fails at start-up. C — standby replicas shorten failover; they are unrelated to the processing guarantee and default to 0 under both settings. D — the interval goes down, not up; the whole point is smaller, more frequent transactions.
- 🧠 **Key point / trap:** the two numbers to hold together are `commit.interval.ms` **30,000 → 100** and `transaction.state.log.replication.factor` **3**. The old `exactly_once` and `exactly_once_beta` values were removed in 4.0.
- 📎 Source: `../../study-plan/week-06/resources/streams-config.md`

### Question 23 — Answer: **B, D**

- **Why correct:** both preserve per-`orderId` ordering because the record is never taken off its partition. B is the idiomatic version: `pause()` the partition, keep calling `poll()` so heartbeats continue and the `max.poll.interval.ms` clock stays satisfied (paused partitions simply return no records), then `resume()` when the backoff expires. D is the blunt version: raise `max.poll.interval.ms` past the 10-minute worst case and retry in the processing loop. Both block the partition — that is the price of ordering — and D additionally slows down the detection of a genuinely stuck consumer.
- **Why the others are wrong:** A — a retry topic is precisely where ordering is lost: the retried record is reprocessed after records that came later on the same key, and the requirement forbids a new topic anyway. C — a second consumer group reads the **whole** topic, so every record would be processed twice. E — share groups give up ordering by design and the group would also need per-record acknowledgement semantics the service does not have.
- 🧠 **Key point / trap:** blocking retry keeps ordering and pays with head-of-line blocking; non-blocking retry keeps throughput and pays with reordering. There is no option that keeps both, and the qualifier always tells you which one the business bought.
- 📎 Source: `../../study-plan/week-09/resources/kafka-error-handling-retry-dlq.md`

### Question 24 — Answer: **B**

- **Why correct:** the hard constraint is "the application cannot be changed in any way", and that is the one constraint the outbox pattern cannot satisfy — an outbox requires the application to write the outbox row. Log-based CDC reads the PostgreSQL write-ahead log, so it observes exactly the committed transactions and nothing that was rolled back, with no application involvement. `ExtractNewRecordState` unwraps Debezium's `before`/`after` envelope into a plain record. The cost, which the answer states, is that consumers are now coupled to the vendor's internal schema — the very coupling an outbox is designed to prevent.
- **Why the others are wrong:** A — correct pattern, disallowed here; it is the right answer to the same question **without** the vendor constraint. C — a database trigger calling a Kafka producer is a dual write dressed up: the send is not part of the database transaction and can fail after the commit, or succeed before a rollback. D — timestamp polling misses deletes entirely, misses rows committed out of timestamp order, and misses any change that is overwritten between two polls.
- 🧠 **Key point / trap:** this is the deliberate inversion of the usual outbox question. Outbox = CDC with a contract you control, but it needs an application change. Direct CDC = no application change, but downstream inherits the internal schema.
- 📎 Source: `../../study-plan/week-05/resources/debezium-postgres-cdc.md` and `../../study-plan/week-09/resources/transactional-outbox-debezium.md`

### Question 25 — Answer: **A, C**

- **Why correct:** A — RF=3 with `min.insync.replicas=2` and `acks=all` is the standard production triple: one broker can be lost with writes still succeeding, and a second loss stops writes with `NotEnoughReplicasException` rather than losing anything already acknowledged. C — this is the ELR mechanism exactly: because the high watermark cannot advance while `|ISR| < min.insync.replicas`, a replica that left the ISR at that moment still holds every committed record, so the controller records it in the partition's ELR set and may elect it.
- **Why the others are wrong:** B — the opposite is documented: **any** change to `min.insync.replicas` at cluster level or topic level, even re-applying the same value, clears the ELR state of the affected partitions. It also has to be set at cluster level once ELR is on; broker-level values are removed. D — `min.insync.replicas=3` with RF=3 means the first broker failure stops writes, which is strictly worse availability for no extra durability. E — ELR widens the set of replicas known to be complete; unclean election allows a replica known to be **incomplete**. They are not substitutes.
- 🧠 **Key point / trap:** with RF=3, min.isr is **2**. Setting it equal to RF is the classic over-correction, and the ELR-clearing rule in option B is the detail that separates people who read the 4.x docs from people who did not.
- 📎 Source: `../../study-plan/week-02/resources/kafka-eligible-leader-replicas.md`

### Question 26 — Answer: **C**

- **Why correct:** the default partitioner hashes the record key with **murmur2**, and that hash is part of the client contract, implemented identically by every mainstream client including `kafkajs` and `@confluentinc/kafka-javascript`. Using the composite key `tenantId|metricName` gives ordering per pair for free, spreads one tenant's metrics across partitions because the metric name is part of the key, and requires the two teams to agree on exactly one thing: the key format. No shared library, no partition arithmetic.
- **Why the others are wrong:** A — reimplementing the hash in two languages means two implementations to keep identical, and hard-coding `% 30` bakes the partition count into application code in two places. B — the `Partitioner` interface is Java only, so the Node.js side cannot use it; the class would also have to be versioned and deployed in lockstep. D — a null key hands partitioning to the sticky partitioner, which spreads records without regard to any key, so ordering per pair is gone.
- 🧠 **Key point / trap:** "same key → same partition" is a guarantee of the **protocol**, not of your code. Reach for an explicit partition number or a custom partitioner only when the default hash genuinely cannot express the requirement.
- 📎 Source: `../../study-plan/week-03/resources/kip-480-794-sticky-partitioner.md`

### Question 27 — Answer: **B, E**

- **Why correct:** B — the client's `records-lag-max` is computed from the consumer's **current position**, i.e. what it has fetched, while the CLI computes `LAG = LOG-END-OFFSET − CURRENT-OFFSET` from the **committed** offset in `__consumer_offsets`. With auto-commit at 5 s the committed offset trails the position, so the CLI can legitimately show more lag than the client does for the same healthy consumer. E — `poll-idle-ratio-avg` is the fraction of time the consumer spends waiting for records; near 1 means it is starved of data, near 0 means user code owns the thread. It rises as a leading indicator before lag becomes visible.
- **Why the others are wrong:** A — `records-lag-max` lives under `kafka.consumer:type=consumer-fetch-manager-metrics`; it is a **client** metric and the client must be scraped. C — inverted: `UnderReplicatedPartitions > 0` is degraded redundancy, `OfflinePartitionsCount > 0` is lost availability, which is the more serious of the two. D — `compression-rate-avg` is compressed size over uncompressed size, so **lower is better**; 1.0 means no compression at all.
- 🧠 **Key point / trap:** two different lag numbers for one consumer group is normal, not a bug. Know which side computed the one you are looking at before you write the alert threshold.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md` and `../../study-plan/week-08/resources/confluent-consumer-lag.md`

### Question 28 — Answer: **D**

- **Why correct:** three constraints line up on ksqlDB: analysts write SQL and no Java, the cluster already exists so nothing new is deployed, and the dashboard performs a **point lookup by merchant**. `CREATE TABLE ... AS SELECT` compiles into a persistent Kafka Streams topology that materialises the aggregate, and a **pull** query reads the current value for one key and returns immediately — the ksqlDB equivalent of an Interactive Query.
- **Why the others are wrong:** A — technically ideal but it is a Java application the analysts cannot write and the platform team would have to operate. B — hand-rolled in-memory counters lose state on restart and re-implement windowing badly. C — right product, wrong query type: a push query streams every change of every merchant forever, which is a firehose for a dashboard that wants one number.
- 🧠 **Key point / trap:** **push query** (`EMIT CHANGES`) = a continuous stream of updates. **Pull query** = a snapshot of the current value for a key, then it ends. Exam scenarios that say "look up" or "current value for X" want a pull query.
- 📎 Source: `../../study-plan/week-06/resources/ksqldb-concepts.md`

### Question 29 — Answer: **C**

- **Why correct:** 1-Y — more consumers than partitions, per-record acknowledgement and a delivery-attempt cap is the definition of a share group (`share.delivery.count.limit` archives a record once it is exceeded). 2-W — independent delivery to several services is what separate `group.id` values have always given; a topic is durable pub/sub, not a queue drained by the first reader. 3-Z — latest value per key, kept indefinitely, so a new service can rebuild state, is `cleanup.policy=compact`. 4-X — old data readable through Kafka clients but off broker disks is tiered storage.
- **Why the others are wrong:** A swaps the share group and the three consumer groups. B and D swap compaction with tiered storage, which is the most common confusion of the four: compaction bounds storage by **key space**, tiered storage moves storage **elsewhere** without changing what is retained.
- 🧠 **Key point / trap:** tiered storage does not support compacted topics. If a requirement asks for both "latest value per key" and "cheap 90-day history", it is asking for two topics.
- 📎 Source: `../../study-plan/week-02/resources/kafka-share-groups.md` and `../../study-plan/week-08/resources/kafka-tiered-storage.md`

### Question 30 — Answer: **C**

- **Why correct:** the default `TopicNameStrategy` derives the subject from the topic (`customer.events-value`), which forces one schema per topic — hence the failure on the second record type. `TopicRecordNameStrategy` uses `<topic>-<recordName>`, so `customer.events-CustomerCreated`, `customer.events-CustomerAddressChanged` and `customer.events-CustomerClosed` are three independent subjects that coexist in one topic. Because the topic name is part of the subject, the same record type in `customer.events.replay` evolves under a **different** subject — which is exactly the independence the team asked for.
- **Why the others are wrong:** A — compatibility `NONE` lets anything register and removes the safety net entirely; it does not solve multiple types, it just stops complaining. B — `RecordNameStrategy` uses only the record name, so the subject is shared across **every** topic carrying that record; compatibility would then be checked jointly for `customer.events` and `customer.events.replay`, which is the behaviour the requirement rules out. D — a union of three types in one schema means every schema change to any type touches the shared subject, and consumers must branch on the union.
- 🧠 **Key point / trap:** three strategies, one distinguishing question — *what is the compatibility boundary?* Topic (`TopicNameStrategy`) · record type across all topics (`RecordNameStrategy`) · record type within one topic (`TopicRecordNameStrategy`).
- 📎 Source: `../../study-plan/week-05/resources/schema-registry-wire-format-serdes.md`

### Question 31 — Answer: **B**

- **Why correct:** three facts combine. First, a `FAILED` task is **not** restarted automatically and does **not** trigger a worker rebalance, which is why the connector-level state stays `RUNNING` and nothing alerted — Connect monitoring must look at task state, not just connector state. Second, `Unknown magic byte!` means the deserializer found a first byte other than `0`, so the record does not carry the 5-byte Schema Registry prefix: a non-Avro record on an Avro topic, a poison pill that will fail on every retry. Third, the durable fix for a sink connector is `errors.tolerance=all` with `errors.deadletterqueue.topic.name`, and the immediate fix is the restart endpoint with `includeTasks=true&onlyFailed=true`.
- **Why the others are wrong:** A — `RUNNING` at connector level says nothing about tasks, and nothing will restart the task by itself. C — raising `tasks.max` cannot exceed the 12 partitions, and new tasks do not rescue a failed one. D — DLQ settings are **connector**-level properties, not worker properties.
- 🧠 **Key point / trap:** `GET /connectors/<name>/status` returns a connector state *and* a task array. Alerting on the connector state alone silently tolerates a fraction of your throughput disappearing.
- 📎 Source: `../../study-plan/week-05/resources/connect-error-handling-dlq-kip298.md` and `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md`

### Question 32 — Answer: **D**

- **Why correct:** the cost is 180 container start-ups, so the fix is to stop paying it 180 times. A `@Container static` field under `@Testcontainers` starts one container for the whole class (or an even wider shared instance for the suite), and per-test isolation comes from generating unique topic and `group.id` names rather than from a fresh broker. On top of that, the tests that never needed a broker — partitioners, serializers, callbacks, commit logic, topologies — move down the pyramid to `MockProducer`/`MockConsumer` and `TopologyTestDriver`, which removes them from the container path entirely.
- **Why the others are wrong:** A — this throws away exactly the coverage the requirement says to keep: rebalances, transaction visibility, real broker errors. B — `EmbeddedKafkaCluster` runs a broker inside the test JVM at a version that drifts from production, which is the reason Testcontainers is preferred. C — `apache/kafka-native` genuinely starts in under a second and is worth adopting, but it still pays a per-test setup and teardown and it does nothing for the tests that should never have started a broker at all.
- 🧠 **Key point / trap:** "make CI faster" in a Kafka codebase is almost always two moves: **share the container** and **push tests down the pyramid**. Changing the image is an optimisation on top, not the fix.
- 📎 Source: `../../study-plan/week-07/resources/testcontainers-kafka.md`

### Question 33 — Answer: **A, C, E**

- **Why correct:** A — `cleanup.policy=compact,delete` is the only policy that applies both behaviours; compaction gives requirement (i) and the delete policy gives requirement (iii). C — `delete.retention.ms=604800000` is 7 days, extending the default 24-hour tombstone window so a consumer lagging up to a week still observes deletions, which is requirement (ii). E — `retention.ms=7776000000` is 90 days, which is what makes the `delete` half of the policy remove old segments.
- **Why the others are wrong:** B — `compact` alone with infinite retention satisfies (i) and (ii) but never caps storage, so (iii) fails. D — `min.cleanable.dirty.ratio` controls **when the cleaner decides to run**, not what it retains or how long tombstones survive; setting it to 0 makes the cleaner run constantly and burns I/O for no change in outcome.
- 🧠 **Key point / trap:** the trade-off this design accepts is real and worth saying out loud — under `compact,delete` a key that is not updated for 90 days is removed **entirely**, latest value and all. If that is unacceptable, the answer is `compact` alone and a different plan for storage.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md` and `../../study-plan/week-02/resources/kafka-log-compaction.md`

### Question 34 — Answer: **A**

- **Why correct:** 2 → 3 → 1 → 4. Check the server side first: the protocol is served by the group coordinator, so the brokers must be on 4.x with `group.version` enabled before any client asks for it. Then decide the assignor, because `group.remote.assignor` has to be part of the config the first migrated instance starts with — the mapping is `RangeAssignor` → `range` and `CooperativeSticky`/`Sticky`/`RoundRobin` → `uniform`. Then roll the instances: the first member with `group.protocol=consumer` flips the group's type, and the remaining classic members continue to be served through the coordinator's adapter layer. Finally verify that the group type is `consumer` and no classic member is left, because a lingering classic member keeps the adapter path alive and a group with no `consumer` members reverts.
- **Why the others are wrong:** B starts rolling clients before confirming the brokers support the protocol. C rolls before choosing the assignor, so the first migrated members get the default server-side assignor instead of the intended equivalent. D verifies before rolling anything.
- 🧠 **Key point / trap:** the three client configs the new protocol **ignores** are `session.timeout.ms`, `heartbeat.interval.ms` and `partition.assignment.strategy` — their equivalents become broker-side group configs (`consumer.session.timeout.ms` 45,000, `consumer.heartbeat.interval.ms` 5,000). `max.poll.interval.ms` stays a client config.
- 📎 Source: `../../study-plan/week-04/resources/kip-848-consumer-rebalance-protocol.md`

### Question 35 — Answer: **D**

- **Why correct:** 1-X — `KStream`-`KStream` is the only join that **requires** a window, and both sides must be co-partitioned. 2-Y — `KStream`-`KTable` has no window, needs co-partitioning, and only a record arriving on the stream side produces output (a table update merely refreshes state). 3-W — `KStream`-`GlobalKTable` needs no co-partitioning because every instance holds the whole table, and the overload takes a `KeyValueMapper` that derives the lookup key from the stream record. 4-Z — a foreign-key `KTable`-`KTable` join is the other join with no co-partitioning requirement; Streams handles the redistribution internally through subscription topics, and there is no window.
- **Why the others are wrong:** A puts the `KeyValueMapper` on `KStream`-`KTable`. B calls the stream-stream join windowless. C assigns the no-co-partitioning property to the wrong pair, swapping `GlobalKTable` and the foreign-key join.
- 🧠 **Key point / trap:** exactly **two** joins escape co-partitioning — `KStream`-`GlobalKTable` and the `KTable`-`KTable` foreign-key join — and exactly **one** takes a window.
- 📎 Source: `../../study-plan/week-06/resources/streams-joins.md`

### Question 36 — Answer: **A**

- **Why correct:** `transactional.id` identifies one logical producer, and the broker guarantees that only the newest holder of an id may write: registering it in `initTransactions()` bumps the producer epoch and fences every older holder. Four replicas sharing `orders-tx` therefore fence each other in a loop, which is why throughput collapses to roughly what one working producer can do. The fix is a **stable, per-instance** id — a StatefulSet ordinal, or an id derived from the set of partitions the instance owns — so that each instance fences only its own predecessor after a restart.
- **Why the others are wrong:** B — this is not a transient rollout artefact; it repeats forever because the replicas are permanently in conflict. C — a random id per start-up does remove the exception, and that is exactly the danger: fencing across restarts disappears, so a hung old instance can keep writing, and every abandoned id holds transactional state until `transactional.id.expiration.ms` (7 days). D — a client `transaction.timeout.ms` above the broker's `transaction.max.timeout.ms` (15 minutes) is rejected at `initTransactions()` with a different error, and the message here names a newer producer with the same id.
- 🧠 **Key point / trap:** stable per-instance `transactional.id` is the whole zombie-fencing mechanism. "Stable" and "unique per instance" are both required; dropping either one silently removes a guarantee.
- 📎 Source: `../../study-plan/week-03/resources/kip-98-exactly-once-transactions.md`

### Question 37 — Answer: **B**

- **Why correct:** the two requirements are independent and each has its own idiomatic answer. Fan-out is what separate consumer groups have always done — a second `group.id` reads the same topic from its own offsets with no change to the first. Scaling past the partition ceiling for an unordered, slow, per-record workload is exactly what share groups (KIP-932, GA in 4.2) were added for: a partition may be assigned to several members, so 40 workers can share 12 partitions, each record is acknowledged individually and the acquisition lock plus delivery count handle the 3–8 second processing time and any stuck record.
- **Why the others are wrong:** A — in a consumer group of 52 members on 12 partitions, 40 members sit idle whatever the assignor. C — raising to 52 partitions works but over-partitions the topic for the sake of one slow consumer and is irreversible. D — MirrorMaker 2 duplicates the data into a second topic to solve a problem a second `group.id` solves for free, and `max.poll.records` does not make each email send faster.
- 🧠 **Key point / trap:** a Kafka topic is already pub/sub. If a question says two teams "need the same data", the answer is almost never a copy of the topic.
- 📎 Source: `../../study-plan/week-02/resources/kafka-share-groups.md`

### Question 38 — Answer: **B, D**

- **Why correct:** B — `errors.tolerance=all` alone drops bad records; adding `errors.deadletterqueue.topic.name` makes them recoverable, and `errors.deadletterqueue.context.headers.enable=true` stamps the original topic, partition, offset and exception onto the DLQ record so an operator can find and replay it. D — the visibility half of the requirement: `total-records-skipped` counts what was tolerated, and `deadletterqueue-produce-failures` catches the silent case where the DLQ producer itself could not write, which `errors.tolerance=all` also swallows.
- **Why the others are wrong:** A — logging satisfies "never stops the connector" but not "remains recoverable"; a worker log is not a replayable store. C — the DLQ is implemented in the **sink** task's record pipeline; a source connector can only tolerate and log, so configuring a DLQ on it does nothing. E — `errors.retry.timeout=-1` retries forever, which stops progress on that partition indefinitely — the opposite of "must never stop the connector".
- 🧠 **Key point / trap:** "DLQ = sink only" is one of the most reliably tested Connect facts, and the second half — that `errors.tolerance=all` can drop records **including DLQ write failures** — is what makes the metrics mandatory rather than optional.
- 📎 Source: `../../study-plan/week-05/resources/connect-error-handling-dlq-kip298.md`

### Question 39 — Answer: **C**

- **Why correct:** a KRaft controller quorum is a Raft group, so it tolerates the loss of (n−1)/2 voters: 3 controllers tolerate 1, 5 tolerate 2. One controller per AZ with 3 AZs means an AZ failure costs exactly one voter and the remaining two still form a majority. The qualifiers then settle it: **smallest** configuration that meets the requirement, and the **documented production topology**, which is dedicated controller nodes — combined mode is documented for development and testing.
- **Why the others are wrong:** A — the arithmetic works but combined mode is not the documented production layout, and it couples controller availability to broker load. B — 5 controllers at 2/2/1 also survives one AZ, but it is two extra nodes and a wider quorum than the requirement needs, which the "smallest" qualifier excludes. D — an even voter count is the classic mistake: with 4 controllers a majority is 3, so losing the AZ that holds 2 leaves 2 and the quorum is gone.
- 🧠 **Key point / trap:** odd voter counts only. 3 or 5, dedicated in production, and spread so that no single failure domain holds a majority.
- 📎 Source: `../../study-plan/week-01/resources/kafka-operations-kraft.md`

### Question 40 — Answer: **B**

- **Why correct:** a unique `group.id` per instance turns the shared reply topic into a broadcast: every instance receives every reply and keeps only the one whose `correlationId` it is waiting for. Nothing is created or deleted at runtime, and instances can come and go freely as the API autoscales, because group membership is per-instance and disposable. The request carries `replyTopic` and `correlationId` headers, the caller parks a future in a map, and a timeout completes it exceptionally if the 2-second budget is missed. The cost — every instance reads every reply — is acceptable because replies are small and the fan-out is at most 12.
- **Why the others are wrong:** A — one shared group means each reply goes to exactly **one** instance, which is usually not the one waiting for it, so most requests time out. C — creating and deleting a topic per instance is explicitly forbidden here, and it churns cluster metadata on every scale event. D — a fixed partition per instance works only while the instance count is fixed; at 3 instances, 9 partitions are unread, and at a scale event two instances can claim the same partition number.
- 🧠 **Key point / trap:** "reply must return to the sender" over Kafka has two viable shapes — broadcast plus correlation-id filtering, or a dedicated reply destination per instance. Autoscaling and "no runtime topic creation" are the qualifiers that pick between them.
- 📎 Source: `../../study-plan/week-03/resources/kafkaproducer-javadoc.md` and `../../study-plan/week-04/resources/kafka-consumer-javadoc.md`

### Question 41 — Answer: **A, D**

- **Why correct:** the metrics rule out the usual suspects — `time-between-poll-max` of 8 s against a 300,000 ms limit means processing is not the problem, and `failed-rebalance-total=0` means nothing is erroring. What remains is churn: two pods leaving and rejoining every four minutes, each event costing the whole group a rebalance. A — static membership gives each pod a stable `group.instance.id`, so the coordinator keeps its assignment, the pod does not send `LeaveGroup` on shutdown, and a restart completing inside `session.timeout.ms` (**45,000 ms** by default in 4.x) causes **no rebalance at all**. D — KIP-848 removes the synchronisation barrier entirely: the coordinator computes the target assignment and members converge incrementally through `ConsumerGroupHeartbeat`, so one member's departure no longer stops the other 29.
- **Why the others are wrong:** B — the version trap. `session.timeout.ms` has defaulted to **45,000 ms** since 3.0 (KIP-735), not 10,000; and raising it without a stable `group.instance.id` does not prevent the rebalance, it only delays the failure detection. C — `max.poll.records` addresses slow processing, which the 8 s poll interval rules out. E — the assignor changes *how* partitions are distributed, not *how often* a redistribution is triggered.
- 🧠 **Key point / trap:** the price of static membership is slower detection of a genuine crash — size `session.timeout.ms` to the restart window and no larger. Also note a Deployment does not give pods stable identities; static membership wants a StatefulSet.
- 📎 Source: `../../study-plan/week-04/resources/kip-345-static-membership.md` and `../../study-plan/week-04/resources/kip-848-consumer-rebalance-protocol.md`

### Question 42 — Answer: **D**

- **Why correct:** the two mechanisms protect against different failures, and the trade is sound only for the one a persistent volume covers. A StatefulSet pod that is rescheduled and reattaches its own bound PVC finds its RocksDB directory and its checkpoint file intact, so it replays only the changelog tail — seconds, not 25 minutes. What disappears is protection against losing an instance whose volume does not come back (a zone failure, a deleted PVC, a node replaced with local storage): the task is then reassigned to a different instance with no local state, which must restore all 40 GB from the changelog. That is precisely the outage the standby replica was buying insurance against.
- **Why the others are wrong:** A — "always sound" ignores the failure mode the standby covers; local state is faster *when it is there*. B — Streams always uses `state.dir`; `num.standby.replicas` controls whether **other** instances keep warm copies, not whether the owner keeps a local one. C — inverted. Under EOS v2 an **unclean** shutdown makes local state untrustworthy and Streams wipes and restores it, so EOS makes persistent volumes *less* reliable as a recovery mechanism, not more.
- 🧠 **Key point / trap:** persistent volume = fast restart of the **same** instance. Standby replica = fast failover to a **different** instance. A resilience story usually wants both, and a cost-cutting exercise has to name which failure it is now accepting.
- 📎 Source: `../../study-plan/week-06/resources/streams-config.md`

### Question 43 — Answer: **B**

- **Why correct:** `MockProducer` implements the full transactional surface and exposes `transactionInitialized()`, `transactionInFlight()`, `transactionCommitted()`, `transactionAborted()`, `commitCount()`, `uncommittedRecords()`, `uncommittedOffsets()` and `sentOffsets()`, so a unit test can genuinely assert that the application drives the API in the right order and includes the right offsets. What it cannot assert is anything the **broker** enforces: epoch-based fencing of a zombie by `transactional.id`, the last stable offset, and what a `read_committed` consumer does or does not see. Those require an integration test with a real broker.
- **Why the others are wrong:** A — the calls being recorded is not the same as the guarantee holding; the test would pass against an implementation that never fences anything. C — factually wrong, `MockProducer` has transaction support and even a `fenceProducer()` helper to make subsequent transactional calls throw. D — `TopologyTestDriver` runs a topology in-process with no broker, so the EOS commit path it exercises is the driver's, not Kafka's.
- 🧠 **Key point / trap:** a mock proves your code calls the API correctly. Only a broker proves the API gives you the guarantee. Exam questions about "does this test prove X" almost always turn on which side of that line X falls.
- 📎 Source: `../../study-plan/week-07/resources/kafka-mock-clients-javadoc.md`

### Question 44 — Answer: **C, D**

- **Why correct:** C — the accumulator allocates batches per partition, so 96 partitions at a 1 MB `batch.size` can want roughly 96 MB of unsent batches against a `buffer.memory` default of **32 MB**. That is why `buffer-available-bytes` hits 0 and `waiting-threads` is positive: `send()` is blocking on allocation, and after `max.block.ms` (60,000 ms) it throws `TimeoutException`. Either raise `buffer.memory` or lower `batch.size`. D — `linger.ms=200` is 40× the 4.x default of 5 and is the direct cause of most of the 850 ms; `record-queue-time-avg` will show it. Lowering it trades batch size and compression ratio for latency, which is the trade the requirement asks for.
- **Why the others are wrong:** A — `acks=all` is explicitly off the table, and the latency here is client-side queueing, not replication. B — `gzip` is *more* CPU-expensive than `zstd` at comparable ratios; the CPU is not the bottleneck anyway. E — `max.in.flight.requests.per.connection` above 5 is incompatible with `enable.idempotence=true`, which is the 4.x default, so the producer would refuse to start.
- 🧠 **Key point / trap:** `batch.size` is a **per-partition** allocation. On a wide topic, `partitions × batch.size` is the number to compare against `buffer.memory`, and that comparison is the one most tuning guides skip.
- 📎 Source: `../../study-plan/week-03/resources/producer-configs.md` and `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md`

### Question 45 — Answer: **C**

- **Why correct:** records written by `KafkaAvroSerializer` start with the Schema Registry **wire format**: 1 magic byte `0`, then a 4-byte big-endian schema id, then the Avro binary payload. `JsonConverter` cannot read that at any setting, because the bytes are not JSON at all. The converter has to match the serializer that wrote the data — `AvroConverter` with `schema.registry.url` so it can resolve the id and decode the payload into a Connect `Struct`.
- **Why the others are wrong:** A — the trap the error message itself sets. `schemas.enable=false` is the right advice for *plain JSON without an envelope*; here it would just move the failure from "no schema/payload fields" to a parse error on binary bytes. B — an SMT operates on Connect `Struct`/`Map` values **after** the converter has decoded the bytes, so it never sees the problem and cannot fix it. D — key and value converters are independent by design; it is normal to run `StringConverter` for keys and `AvroConverter` for values.
- 🧠 **Key point / trap:** error messages give generic advice. Read the message for the **symptom** and the pipeline for the **cause** — here, "who wrote these bytes" answers it in one step.
- 📎 Source: `../../study-plan/week-05/resources/schema-registry-wire-format-serdes.md` and `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md`

### Question 46 — Answer: **A, B, D**

- **Why correct:** A — a topic is a durable log; any number of consumer groups read it independently with their own offsets, so one topic serving both readers is the right starting point. B — this is the real cost of the design: Kafka serves tail reads from the page cache, and a bulk scan of 30 days pulls cold segments through that cache, evicting what the real-time consumer was hitting. The `fetch-latency-avg` of the real-time consumer rises accordingly, and a `consumer_byte_rate` quota on the batch job's principal is the documented way to bound the interference. D — `log.retention.hours` defaults to **168** (7 days), which is well short of 30, so it has to be raised for this topic.
- **Why the others are wrong:** C — the opposite of how Kafka works; a partition is assigned to one consumer *within* a group, never exclusively across groups. E — an `assign()` consumer does not appear in the other service's group either way, because groups are separated by `group.id`; using `assign()` here would only cost the batch job its group-level lag reporting for no benefit.
- 🧠 **Key point / trap:** "one topic, two very different read patterns" is a legitimate design whose failure mode is **page-cache contention**, not correctness. Quotas are the lever, and the CCDAK-relevant default to remember is `log.retention.hours=168`.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md` and `../../study-plan/week-07/resources/kafka-quotas.md`

### Question 47 — Answer: **D**

- **Why correct:** the qualifier is "largest reduction in stop-the-world time" under a client-config-only constraint. KIP-848 replaces `JoinGroup`/`SyncGroup` with a single `ConsumerGroupHeartbeat`, moves assignment computation to the group coordinator, and lets members converge incrementally through epochs — there is no synchronisation barrier at all, which is what a 60-member group suffers from most. It is GA since 4.0, so a 4.3 cluster supports it, and switching it on makes `partition.assignment.strategy`, `session.timeout.ms` and `heartbeat.interval.ms` no-ops on the client.
- **Why the others are wrong:** A — a real improvement over eager rebalancing, and worth knowing that `CooperativeStickyAssignor` is one of the two defaults in 3.0+ — but the default list is `[RangeAssignor, CooperativeStickyAssignor]` and the group selects the **first** strategy all members support, so `RangeAssignor` is what is actually in use until you configure otherwise. Even configured, it still rebalances the whole group, just with fewer partitions revoked. B — static membership is the right tool for restarts, but a Kubernetes **Deployment** does not give pods stable identities, and the constraint forbids changing the workload type. C — `RoundRobinAssignor` is an eager assignor; it makes the stop-the-world pause no shorter.
- 🧠 **Key point / trap:** "one of the defaults" is not "the default in effect". With `[Range, CooperativeSticky]` the group picks Range, so teams who believe they already have cooperative rebalancing usually do not.
- 📎 Source: `../../study-plan/week-04/resources/kip-848-consumer-rebalance-protocol.md`

### Question 48 — Answer: **B, C**

- **Why correct:** B — any rekeying operator followed by a stateful one forces Streams to insert an internal `<application.id>-...-repartition` topic so that records with the same new key land on the same task. Every record therefore makes a round trip through the broker: written once, read once, on top of the original ingest. At 200,000 records/s that is the dominant cost of this topology and it adds a network hop to end-to-end latency. C — the repartition topic is a transport, not a store: it uses `cleanup.policy=delete` and Streams actively purges records it has already processed with `DeleteRecords`, so its footprint stays bounded. The **changelog** topic is the compacted one, and it grows with the key space.
- **Why the others are wrong:** A — `groupBy(...)` is `selectKey(...).groupByKey()` written more compactly; it repartitions too. D — `statestore.cache.max.bytes` controls how much downstream emission is deduplicated in memory; setting it to 0 makes the topology emit **more** records, not fewer, and does not touch repartitioning. E — inverted: the repartition topic is `delete`, the changelog is `compact`.
- 🧠 **Key point / trap:** if the key is already the one you want to group by, use `groupByKey()` on it and Streams skips the repartition entirely. Half of the "Streams is slow" reports are an avoidable `selectKey`.
- 📎 Source: `../../study-plan/week-06/resources/streams-core-concepts-architecture.md` and `../../study-plan/week-06/labs.md`

### Question 49 — Answer: **A, C, D**

- **Why correct:** A — `route.topic.replacement` defaults to `outbox.event.${routedByValue}`, so producing `Order-events` instead of `outbox.event.Order` requires overriding it to `${routedByValue}-events`. C — `table.field.event.key=aggregateid` promotes the aggregate id to the Kafka record key, which is what puts every event of one aggregate instance on one partition and therefore in order. D — `table.fields.additional.placement=type:header:eventType` copies the `type` column into a record header, so consumers can route or filter on the event type without deserializing the payload.
- **Why the others are wrong:** B — `route.by.field` defaults to `aggregatetype`, which is already what the requirement asks for; pointing it at `type` would create one topic per **event type** instead of one per aggregate type. E — `table.expand.json.payload` parses a JSON string column into a structured value; it has nothing to do with the record key, which is set by `table.field.event.key`.
- 🧠 **Key point / trap:** the outbox column contract is worth memorising because the SMT's defaults are built on it — `aggregatetype` → topic, `aggregateid` → key, `type` → event type, `payload` → value, `id` → event id header.
- 📎 Source: `../../study-plan/week-09/resources/transactional-outbox-debezium.md`

### Question 50 — Answer: **A**

- **Why correct:** a quota is enforced entirely on the **broker**, keyed by user principal and/or client-id, so it needs no cooperation from the client at all — which is exactly the "without touching its code or its configuration" requirement. The broker throttles by delaying its responses to that principal; the client observes it as `produce-throttle-time-avg > 0` and experiences it as backpressure. Because the quota is scoped to one principal, no other client is affected.
- **Why the others are wrong:** B — this is a client-side change, which is forbidden, and smaller batches would increase request rate, making the pressure worse. C — a second cluster solves it, at the cost of a second cluster, replication and a migration; the question asks for a lever, not a rebuild. D — `max.request.size` is a **producer** config, there is no broker-side equivalent under that name, and the broker-side size limit (`message.max.bytes`) would reject records rather than pace them.
- 🧠 **Key point / trap:** pair the quota with awareness of its downstream effect. A throttled producer's accumulator fills, `buffer-available-bytes` falls, and `send()` will eventually throw `TimeoutException` after `max.block.ms` — so "we quota'd the batch job" is not the end of the conversation with its owners.
- 📎 Source: `../../study-plan/week-07/resources/kafka-quotas.md`

### Question 51 — Answer: **C**

- **Why correct:** the constraints are all satisfied by one keyed topic. Per-tenant ordering comes from the key, so it holds for free. Partition count is sized to **throughput**, decoupling the cluster from the tenant list, so 50 new tenants a week cost nothing — no topic creation, no controller metadata growth, no reassignment. The answer also names what is given up: with one topic there are no per-tenant ACLs and no per-tenant retention, and a single dominant tenant becomes a hot partition. The scenario explicitly buys out both of those with "one retention policy, one access-control boundary".
- **Why the others are wrong:** A — 24,000 partitions multiplies every per-partition cost: open file handles, controller metadata, memory in every producer's accumulator, and the time the controller needs to elect leaders after a broker failure. Each onboarding also becomes a cluster operation. B — 4,000 partitions is more manageable, but it still ties the cluster to the tenant list, still requires a topic creation per tenant, and caps each tenant at one partition of throughput. D — a share group changes how records are consumed and would destroy the per-tenant ordering the requirement demands.
- 🧠 **Key point / trap:** "topic per tenant" is the right answer when tenants need **different ACLs or different retention**. Strip those away and it becomes a scaling liability. The exam signals which world you are in through exactly those two words.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md`

### Question 52 — Answer: **B**

- **Why correct:** SCRAM credentials are stored in the cluster's own metadata, so they are created, changed and deleted at runtime with `kafka-configs.sh --alter --add-config 'SCRAM-SHA-512=[password=...]' --entity-type users` and take effect without restarting a broker. The client needs only a `sasl.jaas.config` string, which a serverless function can hold in an environment variable or a secret — no keystore file on disk. Running it over `SASL_SSL` keeps the exchange encrypted.
- **Why the others are wrong:** A — mTLS requires the client to present a certificate from a keystore, which the serverless client cannot do, and rotation means reissuing and redistributing certificates. C — Kerberos needs a KDC, a keytab file and clock synchronisation; it is the heaviest option here and again file-based. D — SASL/PLAIN reads its credentials from a static JAAS file on each broker, so adding or rotating a user means editing files and restarting brokers, which is exactly the requirement that rules it out.
- 🧠 **Key point / trap:** the reflex is "username/password stored on the broker, changeable at runtime → **SASL/SCRAM**". SASL/PLAIN looks similar and fails on the rotation requirement every time.
- 📎 Source: `../../study-plan/week-07/resources/kafka-security-sasl.md`

### Question 53 — Answer: **B, C**

- **Why correct:** B — a broker restart mid-run exercises leader election, ISR changes, producer retries and idempotent sequence-number handling. None of that exists in a mock, so the only way to observe it is a real broker whose lifecycle the test controls, which is what Testcontainers is for. C — the second behaviour is pure client logic. `MockConsumer.schedulePollTask(Runnable)` runs one queued task per `poll()` call, so scheduling `consumer.wakeup()` makes the wake-up land inside a poll exactly as it would in production; the test then asserts the shutdown path with `committed(...)` and `closed()`, in microseconds and with no Docker.
- **Why the others are wrong:** A — `errorNext()` injects an exception into the callback; it does not reproduce the leader change, the retry sequencing or the deduplication the broker performs. D — `TopologyTestDriver` runs a Streams topology and does not own a `KafkaConsumer` the test can wake up. E — two drivers with one `application.id` do not form a group; `TopologyTestDriver` has no group membership at all.
- 🧠 **Key point / trap:** `schedulePollTask` is the idiomatic way to test an infinite poll loop without a broker — it is the hook for injecting records, exceptions and `wakeup()` at a controlled point in the loop.
- 📎 Source: `../../study-plan/week-07/resources/testcontainers-kafka.md` and `../../study-plan/week-07/resources/kafka-mock-clients-javadoc.md`

### Question 54 — Answer: **A**

- **Why correct:** tiered storage separates the local tier (broker disk, serving tail reads from the page cache) from a remote tier (object storage) holding closed segments. `local.retention.ms` sized to the real-time consumers' worst lag keeps their reads entirely local, so their latency is unchanged, while `retention.ms` at 90 days governs the remote tier. Crucially the data stays addressable through ordinary Kafka clients at the same offsets — the backfill just reads slower when it reaches the remote tier, which is the accepted trade.
- **Why the others are wrong:** B — a legitimate alternative and the answer to a differently-worded question, but it breaks the stated requirement: the history is then Parquet in S3, not a Kafka topic, so the backfill needs a second client stack and the archive's ordering and file format become the team's problem. C — compaction keeps the latest value per key, which is not the same data set as 90 days of history, and tiered storage does not support compacted topics anyway. D — `log.retention.bytes` caps storage by deleting data; it does not preserve 90 days.
- 🧠 **Key point / trap:** "long retention cheaply, still readable as Kafka" → tiered storage. "Long retention cheaply, any format" → archive with a sink connector. The phrase that separates them is whether the reader must keep using Kafka clients.
- 📎 Source: `../../study-plan/week-08/resources/kafka-tiered-storage.md`

### Question 55 — Answer: **A, D**

- **Why correct:** A — auto-commit runs inside `poll()`, committing whatever the previous `poll()` returned once `auto.commit.interval.ms` (default **5,000**) has elapsed. That bounds the replay window at about 5 seconds, and it means the committed offset can cover records that were handed to the application but not yet processed — which is why auto-commit alone is not enough when the side effect must be durable first. D — `commitAsync()` after each batch avoids a synchronous round trip on the hot path, and a final `commitSync()` in `finally` (on shutdown or on partition revocation) makes sure the last position is durably recorded rather than lost to a failed async commit.
- **Why the others are wrong:** B — a synchronous commit per record is a broker round trip per record; at 40,000 records/s it is the bottleneck, not the optimisation. C — `isolation.level` controls visibility of transactional records; it has no effect on replay after a crash. E — committing before processing converts the pipeline to at-most-once, so a crash silently drops records. An idempotent sink absorbs **duplicates**, not **losses**.
- 🧠 **Key point / trap:** the `commitAsync()` in the loop plus `commitSync()` in `finally` pattern is the standard high-throughput shape. Know why both halves are there: throughput from the first, durability of the final position from the second.
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-configs.md`

### Question 56 — Answer: **D**

- **Why correct:** MSK Replicator supports a **self-managed** Kafka cluster as the source with MSK Provisioned as the target, replicates data together with topic configuration, ACLs and **consumer group offsets**, and its **identical topic name** mode keeps the names unchanged so clients need no reconfiguration when they fail over. It is a managed service, so there is no Connect cluster to size, secure or operate — which is the qualifier that decides this question. The trade-off is AWS lock-in and an MSK-only target.
- **Why the others are wrong:** A — technically correct and the right answer without the last constraint: `IdentityReplicationPolicy` preserves topic names and `MirrorCheckpointConnector` translates offsets. But MirrorMaker 2 *is* a Connect cluster, which the requirement excludes. B — an S3 round trip loses ordering guarantees, offsets and topic configuration, and adds two connectors plus a bucket to operate. C — no such feature exists; `replica.fetch.remote` is not a cross-cluster replication mechanism.
- 🧠 **Key point / trap:** MM2 and MSK Replicator solve the same problem with opposite operating models. The exam picks between them on "do you want to run it yourself", and picks **identical topic name** mode whenever clients must not be reconfigured at failover.
- 📎 Source: `../../study-plan/week-09/resources/msk-replicator.md` and `../../study-plan/week-08/resources/kafka-georeplication-mirrormaker2.md`

### Question 57 — Answer: **B**

- **Why correct:** with RF=3 and `min.insync.replicas=2`, one broker being down leaves 2 in-sync replicas and writes continue. Restarting the next broker before the previous one has rejoined the ISR takes a partition to 1 in-sync replica, which is below the minimum, and the leader starts rejecting `acks=all` writes with `NOT_ENOUGH_REPLICAS`. The only lever that satisfies both "zero produce errors" and "no risk of losing an acknowledged record" is pacing: wait until `UnderReplicatedPartitions` is back to 0 before taking the next broker down. A rejoining broker has to catch up on the backlog it missed and then stay within `replica.lag.time.max.ms` (**30,000 ms**) to be readmitted to the ISR, so the wait is not instantaneous. Running `kafka-leader-election.sh --election-type PREFERRED` afterwards restores leadership balance.
- **Why the others are wrong:** A — unclean election trades data loss for availability, which the second half of the requirement forbids. C — `min.insync.replicas=3` makes the *first* broker restart stop writes; it is strictly worse. D — `acks=1` removes the errors by removing the guarantee, which is exactly the risk the requirement rules out.
- 🧠 **Key point / trap:** `UnderReplicatedPartitions` returning to 0 is the gate for the next step in any rolling operation — restart, upgrade or reassignment. Pacing by a fixed sleep instead of by the metric is how this outage happens.
- 📎 Source: `../../study-plan/week-08/resources/kafka-upgrade-kraft.md` and `../../study-plan/week-08/resources/kafka-monitoring-broker-metrics.md`

### Question 58 — Answer: **A**

- **Why correct:** all four of these defaults changed between 2.8 and 4.3, and an application that changes nothing inherits all of them. `acks` `1` → **`all`** and `enable.idempotence` `false` → **`true`** arrived together in 3.0 (KIP-679). Consumer `session.timeout.ms` `10000` → **`45000`** also arrived in 3.0 (KIP-735), with `heartbeat.interval.ms` staying at 3,000. `linger.ms` `0` → **`5`** arrived in 4.0 (KIP-1030). The practical effects: writes are more durable and slightly slower, retries no longer create duplicates within a session, a dead consumer is detected later, and every record waits up to 5 ms for batch-mates.
- **Why the others are wrong:** B — `acks` did change, and `linger.ms` went to 5, not 100. C — this is the half-updated version of the truth and the most tempting distractor: it gets 3.0 right and misses 4.0 entirely. D — `partition.assignment.strategy` changed in the other direction (`RangeAssignor` → `[RangeAssignor, CooperativeStickyAssignor]`), and `group.protocol` still defaults to **`classic`** in 4.3; `consumer` is opt-in, with the classic protocol deprecated in 4.3 and slated to become the default later.
- 🧠 **Key point / trap:** the five changed defaults worth memorising as a block — `acks=all`, `enable.idempotence=true`, `linger.ms=5`, `session.timeout.ms=45000`, `num.recovery.threads.per.data.dir=2` — plus the three that did **not** change: `heartbeat.interval.ms=3000`, `max.poll.interval.ms=300000`, `group.protocol=classic`.
- 📎 Source: `../../study-plan/week-03/resources/kip-1030-defaults-kafka-4-0.md` and `../../study-plan/VALIDATION.md`

### Question 59 — Answer: **C**

- **Why correct:** this is the standard shape for parallelising a consumer without breaking either invariant. Routing on `hash(key) % N` guarantees that all records of one key go to one worker, so per-key order is preserved even though the partition is processed concurrently. Committing a **watermark** — the lowest offset that is still in flight on that partition — guarantees no offset is committed ahead of an unfinished side effect. And `pause()`ing the partition when in-flight work crosses a bound keeps `poll()` running (so heartbeats and `max.poll.interval.ms` stay satisfied) without pulling in more work than the pool can hold.
- **Why the others are wrong:** A — this is the naive version and it breaks both invariants: a shared pool interleaves records of the same key, and committing on submission commits offsets for work that has not happened. B — more records per poll does not add parallelism; the single thread still processes them one at a time, and raising `max.poll.interval.ms` only delays the moment the group gives up on it. D — one consumer per key is unbounded in instance count and is capped by the partition count anyway; keys sharing a partition would still contend.
- 🧠 **Key point / trap:** the three things any multi-threaded consumer must keep straight are **key affinity** (ordering), **offset watermarking** (no premature commit) and **pause/resume** (flow control without losing group membership). An answer missing any one of them is wrong however fast it is.
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-javadoc.md`

### Question 60 — Answer: **B**

- **Why correct:** when `broker.rack` is set on every broker, Kafka's replica assignment spreads a partition's replicas across as many distinct racks as possible. With RF=3 and exactly 3 racks, that means one replica per AZ, so an AZ failure removes exactly one replica and leaves 2 — precisely `min.insync.replicas`, so writes continue and nothing acknowledged is at risk. The answer also states the condition that makes it a *guarantee* rather than a coincidence: rack-aware placement is applied at creation and at reassignment, so any topic created with an RF that is not a multiple of the rack count, and any manual reassignment, has to be re-verified.
- **Why the others are wrong:** A — `replica.selector.class` controls which replica a **consumer fetches from** (follower fetching for locality); it does not influence where replicas are placed. C — RF=4 across 3 racks puts two replicas in one AZ, so losing that AZ drops to 2 — no better than RF=3, at 33% more storage. D — unclean election makes a leader available by accepting data loss, which is a different requirement from staying at or above min.isr.
- 🧠 **Key point / trap:** rack awareness is a **placement** feature, follower fetching is a **read locality** feature, and neither changes durability arithmetic on its own. The durability claim comes from `RF ≥ racks` combined with `min.insync.replicas`.
- 📎 Source: `../../study-plan/week-01/resources/kafka-design-persistence-replication.md`

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (48+/60) | Đạt ngưỡng cá nhân trên một đề **thiên về thiết kế** — đây là dạng khó nhất của CCDAK. | Review 100% câu sai. Với mỗi câu sai, viết lại **qualifier** của đề và giải thích bằng một câu tại sao nó loại ba phương án còn lại. Làm nốt các mock còn lại; đủ **3 bộ khác nhau ≥ 80%** thì đặt lịch thi. |
| **70–79%** (42–47/60) | Kiến thức ổn, kỹ năng chọn phương án chưa chắc. | Phân loại câu sai thành *thiếu kiến thức* và *đọc sót qualifier*. Nhóm thứ hai chữa bằng luyện đề, không phải đọc lại tài liệu: làm lại đúng những câu đó sau 2 ngày, **che phương án**, tự viết đáp án rồi mới mở. Nhóm thứ nhất → đọc lại tuần tương ứng ở bảng dưới. **Chưa đặt lịch thi.** |
| **< 70%** (≤ 41/60) | Chưa sẵn sàng. | **Van an toàn: lùi lịch thi 1 tuần.** Lấy 2 domain thấp nhất, học lại Buổi A + B của các tuần tương ứng và làm lại lab, rồi làm mini-mock của từng tuần trước khi thử full mock lần nữa. |

> 📌 Mock này cố tình xây các câu mà **cả 4 phương án đều chạy được**. Nếu bạn chọn một phương án "không sai về kỹ thuật" nhưng không đáp ứng qualifier, hãy ghi vào sổ câu sai là **đọc sót qualifier** — đó là lỗi phổ biến nhất khiến người có kiến thức tốt vẫn trượt CCDAK. Câu đúng nhờ đoán may cũng tính là câu sai.

---

## 🔁 Bản đồ câu sai → tuần cần học lại

| Chủ đề của câu sai | Câu số | Học lại |
| --- | --- | --- |
| Rack awareness, KRaft quorum, cluster sizing | 39, 60 | **Tuần 1** — `week-01/README.md` |
| Replication, ISR, ELR, compaction, retention, share groups | 1, 8, 20, 25, 29, 33, 46, 51, 54 | **Tuần 2** — `week-02/README.md` |
| Producer latency/throughput, partitioner, transactions, fencing | 2, 12, 26, 36, 44 | **Tuần 3** — `week-03/README.md` |
| Consumer scaling, `assign()` vs `subscribe()`, commit strategy, rebalance protocol, poll-loop design | 6, 16, 34, 40, 41, 47, 55, 59 | **Tuần 4** — `week-04/README.md` |
| Connect tool choice, SMT vs converter, task failure & DLQ, CDC, schema strategy & compatibility | 3, 10, 17, 24, 30, 31, 38, 45 | **Tuần 5** — `week-05/README.md` |
| Streams table types, joins, EOS, repartition, state recovery, ksqlDB | 5, 14, 22, 28, 35, 42, 48 | **Tuần 6** — `week-06/README.md` |
| Testing strategy, mocks, Testcontainers, authentication choice, quotas | 7, 18, 32, 43, 50, 52, 53 | **Tuần 7** — `week-07/README.md` |
| Metrics semantics, lag triage, rolling restart, producer failure diagnosis | 4, 13, 21, 27, 57 | **Tuần 8** — `week-08/README.md` |
| Design patterns (outbox, claim-check, idempotent consumer, retry), MSK Replicator, exactly-once pipeline | 9, 19, 23, 49, 56 | **Tuần 9** — `week-09/README.md` |
| Delivery semantics, partition sizing, consumption model, version defaults | 11, 15, 37, 58 | **Tuần 10** — `week-10/README.md` + [`VALIDATION.md`](../../study-plan/VALIDATION.md) |
