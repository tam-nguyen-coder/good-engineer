# ✅ Answers — CCDAK Mock Exam 02

> Chỉ mở sau khi đã làm hết 60 câu trong [questions.md](questions.md) với đồng hồ 90 phút.
> Back to [mock index](../README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-D · 3-A · 4-C · 5-D · 6-B · 7-C · 8-A · 9-D · 10-B · 11-A · 12-C · 13-B · 14-AC · 15-BD · 16-D · 17-C · 18-A · 19-AD · 20-D · 21-CE · 22-BC · 23-B · 24-C · 25-AE · 26-BE · 27-A · 28-CD · 29-B · 30-D · 31-A · 32-C · 33-D · 34-B · 35-C · 36-A · 37-B · 38-D · 39-A · 40-AB · 41-C · 42-D · 43-DE · 44-B · 45-A · 46-C · 47-B · 48-AC · 49-BD · 50-D · 51-C · 52-A · 53-D · 54-B · 55-C · 56-CE · 57-A · 58-AD · 59-B · 60-D

> 📌 Với câu `Multi`, chỉ tính **đúng** khi chọn đủ và đúng cả hai phương án — không có điểm một phần.

---

## 📊 Chấm điểm theo domain

| Domain | Tỉ trọng | Câu số | Số đúng / Tổng | % | Ngưỡng |
| --- | --- | --- | --- | --- | --- |
| **DEV** — Application Development | 28% | 2, 5, 8, 12, 16, 19, 23, 25, 33, 36, 39, 42, 45, 48, 51, 55, 58 | ___ / 17 | ___ % | ≥ 76% (13/17) |
| **FUND** — Fundamentals | 23% | 1, 7, 10, 14, 20, 28, 29, 40, 44, 47, 50, 54, 57, 60 | ___ / 14 | ___ % | ≥ 71% (10/14) |
| **CONNECT** — Kafka Connect | 15% | 3, 9, 15, 24, 30, 38, 43, 52, 59 | ___ / 9 | ___ % | ≥ 78% (7/9) |
| **OBS** — Application Observability | 13% | 4, 11, 17, 21, 27, 34, 35, 37 | ___ / 8 | ___ % | ≥ 75% (6/8) |
| **STREAMS** — Kafka Streams | 12% | 6, 18, 26, 31, 41, 49, 53 | ___ / 7 | ___ % | ≥ 71% (5/7) |
| **TEST** — Application Testing | 8% | 13, 22, 32, 46, 56 | ___ / 5 | ___ % | ≥ 60% (3/5) |
| **TỔNG** | 100% | 1–60 | ___ / 60 | ___ % | **≥ 80% (48/60)** |

> ⚠️ Confluent **không công bố** ngưỡng đậu chính thức (chấm Pass/Fail). Con số ~75% lưu truyền trong cộng đồng chỉ là **phỏng đoán**. Ngưỡng 80% ở trên là **ngưỡng cá nhân** đặt cao hơn để có biên an toàn.

---

### Question 1 — Answer: **B**

- **Why correct:** the broker log names the exact condition — `min.isr requirement of 2` with `ISR Set(3)`, i.e. only one replica in sync. `NotEnoughReplicasException` is a **retriable** error, so the idempotent producer (4.3 defaults: `acks=all`, `retries=Integer.MAX_VALUE`) keeps retrying the batch in the background. Nothing reaches the application callback until `delivery.timeout.ms` (120,000 ms) expires, which is why `record-error-rate` was flat for two minutes and then spiked. The cure is on the broker side: restore a second in-sync replica.
- **Why the others are wrong:** A — brokers never "upgrade" a producer's `acks`; the value is what the client sends per request, and `acks=0` would not help because the write is rejected at the leader. C — `NotEnoughReplicasException` is explicitly retriable; a fatal error would have surfaced immediately in the callback. D — `replica.lag.time.max.ms` (30,000 ms) decides *when* a lagging follower is evicted; lowering it evicts followers **sooner**, making the problem worse, and the followers here are down, not merely slow.
- 🧠 **Key point / trap:** a retriable broker-side error shows up in the application as a **timeout**, not as the original exception. Always read the broker log next to the client log.
- 📎 Source: `../../study-plan/week-02/resources/kafka-replication-isr.md` and `../../study-plan/week-03/resources/producer-configs.md`.

### Question 2 — Answer: **D**

- **Why correct:** `buffer.memory` (32 MB by default) is **one pool for the whole producer**, not per topic or per broker. Batches bound for the degraded broker cannot be acknowledged, so they occupy the pool; once it is exhausted, `send()` blocks in the allocator for any partition of any topic — which is exactly what `waiting-threads=38` and `bufferpool-wait-ratio≈0.81` report. `produce-throttle-time-avg=0` rules out a quota, and the per-broker `request-latency-avg` split identifies the culprit.
- **Why the others are wrong:** A — there is no per-topic allocation; that misconception is the whole point of the question. B — `max.in.flight.requests.per.connection` is per **connection**, so exhausting it on broker 3 cannot stall broker 1; and lowering it to 1 would reduce throughput everywhere. C — `linger.ms=5` caps waiting at 5 ms and cannot hold 32 MB; a zero throttle time rules out quotas, not brokers.
- 🧠 **Key point / trap:** one sick broker can stall a producer's traffic to **every** topic, because the accumulator is shared. Watch `request-latency-avg` broken down per broker, not just the average.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md` (buffer group: `buffer-available-bytes`, `waiting-threads`, `bufferpool-wait-ratio`).

### Question 3 — Answer: **A**

- **Why correct:** `key.converter` / `value.converter` and their `*.converter.*` sub-properties are worker defaults that a connector may override in its own configuration. Supplying both the converter class and `value.converter.schemas.enable=false` on this connector changes only this connector, needs only a `PUT .../config` (no worker restart), and leaves the five Avro connectors alone.
- **Why the others are wrong:** B — this does work technically, but the requirement says *without editing the worker properties and without restarting any worker*; it is the classic "right answer to the wrong question" distractor. C — `errors.tolerance=all` plus a DLQ would route **every** record to the DLQ, because every record fails the converter; the index would stay empty. D — Connect only reads converter options under the `key.converter.` / `value.converter.` / `header.converter.` prefixes; an unprefixed `schemas.enable` is ignored.
- 🧠 **Key point / trap:** converter settings live at two levels. Read the qualifier to decide which level you are allowed to touch.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md` (connector-level `key.converter`/`value.converter` override the worker).

### Question 4 — Answer: **C**

- **Why correct:** `kafka-consumer-groups.sh --describe` prints `CONSUMER-ID`, `HOST` and `CLIENT-ID` per **assigned** partition. A dash in all three means no member owns the partition, i.e. the group is in state `Empty`. `LAG` is still meaningful — it is `LOG-END-OFFSET − CURRENT-OFFSET`, computed from the last committed offsets — and will keep rising until a consumer joins.
- **Why the others are wrong:** A — if the coordinator were unreachable the command would fail with a coordinator error rather than print offsets. B — static membership changes the member id, it does not hide it; `--members` still lists every static member. D — a consumer blocked inside `poll()` is still a group member and still appears in the output with its id and host.
- 🧠 **Key point / trap:** dashes in the member columns = nobody is consuming. Confirm with `--state`, which will print `STATE: Empty`.
- 📎 Source: `../../study-plan/week-04/resources/kafka-ops-consumer-groups-share-groups.md` (describe output columns; `LAG = LOG-END-OFFSET − CURRENT-OFFSET`).

### Question 5 — Answer: **D**

- **Why correct:** under the KIP-848 protocol (`group.protocol=consumer`) the **broker** owns member liveness, so the client's `session.timeout.ms` and `heartbeat.interval.ms` are silently ignored — which is why raising one of them changed nothing. `max.poll.interval.ms` stays a genuine client concern because only the client knows how long the application spent between polls; with a 6-minute batch it exceeds the 300,000 ms default and the member is removed, invalidating the next commit.
- **Why the others are wrong:** A — the broker does clamp a session timeout to `group.max.session.timeout.ms`, but under this protocol the client value is not used at all, so the clamping is irrelevant here. B — `max.poll.interval.ms` is very much alive under KIP-848; it is the one liveness clock that stays on the client. C — `CommitFailedException` is a group-membership error, not a replication error.
- 🧠 **Key point / trap:** the dangerous part of KIP-848 is that the ignored configs fail **silently**. Split it as: member liveness → broker; application liveness (`max.poll.interval.ms`) → client.
- 📎 Source: `../../study-plan/week-04/resources/kip-848-consumer-rebalance-protocol.md` (ignored client configs, broker group configs).

### Question 6 — Answer: **B**

- **Why correct:** `selectKey()`, `map()` and `flatMap()` set the topology's internal *key-changing* flag because Streams cannot inspect the lambda. The next key-based operation — here `groupByKey()` — therefore inserts a repartition topic, which means an extra produce plus an extra consume for every record: exactly the doubled latency and extra traffic observed. Replacing it with `peek()` (which cannot change the key) removes the flag and the topic.
- **Why the others are wrong:** A — `filter()` is key-preserving and never triggers repartitioning; moving it changes nothing. C — `count()` creates a **changelog** topic (`-changelog`), which is normal and is not what appeared; the name in the log ends in `-repartition` and references `KSTREAM-KEY-SELECT`. D — repartition topics are created by key-changing operators, not by a partition-count mismatch between input and output topics.
- 🧠 **Key point / trap:** the internal topic name tells you the cause. `...-KEY-SELECT-...-repartition` always points at `selectKey`/`map`. Use `mapValues`, `flatMapValues` or `peek` whenever the key does not actually change.
- 📎 Source: `../../study-plan/week-06/resources/streams-dsl-api.md` (key-changing operators and automatic repartitioning).

### Question 7 — Answer: **C**

- **Why correct:** the order is 3 → 4 → 1 → 2. Stop the broker so **controlled shutdown** hands its leaderships to in-sync replicas (avoiding an availability gap); start it and wait for its replicas to rejoin every ISR; run a **preferred** leader election so leadership comes back and the cluster is balanced again; and only then verify `UnderReplicatedPartitions = 0` and `OfflinePartitionsCount = 0` before moving to the next broker.
- **Why the others are wrong:** A (2 → 3 → 4 → 1) — the verification gate belongs **after** the restart of this broker, immediately before touching the next one; verifying first proves nothing about the broker you just bounced. B (3 → 2 → 4 → 1) — checking URP while the broker is still down guarantees a non-zero reading, so the gate can never pass. D (4 → 3 → 1 → 2) — starting before stopping is not a sequence.
- 🧠 **Key point / trap:** with RF=3 and `min.insync.replicas=2` you may lose exactly **one** replica at a time. The URP gate is what enforces "one at a time"; skipping it is how rolling restarts turn into outages.
- 📎 Source: `../../study-plan/week-08/resources/kafka-upgrade-kraft.md` (roll one broker at a time, wait for URP = 0).

### Question 8 — Answer: **A**

- **Why correct:** the message text names `max.request.size`, and that check runs inside `KafkaProducer.send()` **before** anything is sent. The default is 1,048,576 bytes and it is a producer property — so no broker change can affect it. Raising `max.request.size` is the minimal fix; the broker's `message.max.bytes` (default 1,048,588) and the topic's `max.message.bytes` must also be large enough, otherwise the next failure is the broker-side variant of the same exception.
- **Why the others are wrong:** B — a topic-level `max.message.bytes` is a broker-side limit too, so it is equally unreachable while the client rejects the record locally. C — `batch.size` is a batching target, not a per-record limit; a record larger than `batch.size` is simply sent in a batch of its own. D — consumer configuration never propagates to producers.
- 🧠 **Key point / trap:** `RecordTooLargeException` has two distinct messages. "*…which is the value of the max.request.size configuration*" = client-side; "*The request included a message larger than the max message size the server will accept*" = broker-side. The text tells you which knob to turn.
- 📎 Source: `../../study-plan/week-03/resources/producer-configs.md` (`max.request.size` 1,048,576) and `../../study-plan/week-02/resources/kafka-topic-configs.md`.

### Question 9 — Answer: **D**

- **Why correct:** 1-Y · 2-X · 3-Z · 4-W. A **converter** is the byte boundary: `AvroConverter` turns the record value between Kafka bytes and Connect's internal data + schema (Y). An **SMT** operates after conversion, reshaping the in-memory `Struct` (X). A **serializer** belongs to a plain `KafkaProducer` and has nothing to do with Connect (Z). The **header converter** does for headers what the value converter does for values (W).
- **Why the others are wrong:** A inverts converter and SMT (`1-X`, `2-Y`) — the single most common Connect confusion — and then swaps serializer and header converter as well. B assigns the SMT to the serializer's job and the serializer to the SMT's job (`2-Z`, `3-X`), which reverses the "inside Connect vs outside Connect" boundary. C swaps the **value** converter and the **header** converter (`1-W`, `4-Y`): both are converters, but one handles the record value and the other only the headers.
- 🧠 **Key point / trap:** converter answers *what format is on the wire*; SMT answers *how do I reshape each record*; serializer is the plain-client equivalent of a converter and never appears in a connector configuration.
- 📎 Source: `../../study-plan/week-05/resources/connect-transforms-predicates.md` and `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md`.

### Question 10 — Answer: **B**

- **Why correct:** with ELR the controller elects in this order: (1) a replica in the **ISR**; (2) if the ISR is empty, an unfenced replica in the **ELR**; (3) otherwise the **last known leader**, if unfenced. Here the ISR is empty and `Elr: 6`, so broker 6 is the only safe candidate — ELR members are guaranteed to hold every committed record because the high watermark cannot advance while `|ISR| < min.insync.replicas`. Broker 5 restarted with an empty log directory, which the broker reports at registration, so the controller removes it from the ELR. Broker 7 is in neither set, and with `unclean.leader.election.enable=false` it cannot be elected.
- **Why the others are wrong:** A — the last known leader is the **last** resort, not the first, and a replica that lost its log directory is disqualified. C — ELR does not merely rank candidates; outside ISR ∪ ELR an election is by definition unclean and is blocked by the default. D — this is precisely the pre-4.0 behaviour that ELR was introduced to improve on; it is the version trap in this question.
- 🧠 **Key point / trap:** learn the election ladder **ISR → ELR → last known leader**, and remember that a replica rebuilt on an empty disk drops out of the ELR.
- 📎 Source: `../../study-plan/week-02/resources/kafka-eligible-leader-replicas.md` (election order; `Elr:` / `LastKnownElr:` in `--describe`).

### Question 11 — Answer: **A**

- **Why correct:** `LocalTimeMs` measures the time a request spends being processed **at the leader** on a request-handler thread. When a topic's `compression.type` differs from the codec the producer used, the broker must decompress and re-compress every batch during the append, which is CPU work on exactly those threads — hence a 140 ms `LocalTimeMs`, a saturated handler pool and a growing request queue despite idle disks. Setting the topic back to `compression.type=producer` (the default) makes the broker store the batch as received.
- **Why the others are wrong:** B — adding threads to a pool that is busy doing avoidable CPU work only spreads the same work over more threads on a 16-vCPU host; and `RequestHandlerAvgIdlePercent < 0.3` means "the io pool is saturated", not automatically "too few threads". C — `NetworkProcessorAvgIdlePercent` is the metric for the network pool; `RequestQueueSize` grows because the io pool cannot drain it. D — `RemoteTimeMs` (6 ms here) is the follower-wait component; `LocalTimeMs` does not include it.
- 🧠 **Key point / trap:** split `TotalTimeMs` into its five parts before changing anything. `LocalTimeMs` high → leader-side CPU/disk work; `RemoteTimeMs` high on Produce → waiting for followers.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-broker-metrics.md` and `../../study-plan/week-02/resources/kafka-topic-configs.md` (`compression.type` default `producer`).

### Question 12 — Answer: **C**

- **Why correct:** KIP-1030 changed the producer default `linger.ms` from **0 to 5** in Kafka 4.0. Every symptom matches: batches now wait up to 5 ms in the accumulator (`record-queue-time-avg ≈ 5 ms`), so they are larger (`batch-size-avg` 900 B → 6.4 KB), throughput per request improves and p99 latency rises by roughly the linger. Setting `linger.ms=0` explicitly restores the 3.x behaviour.
- **Why the others are wrong:** A — `batch.size` is unchanged at 16,384; note that `batch-size-avg` rose to 6.4 KB, still below it. B — `acks` moved from `1` to `all` in **3.0**, not 4.0, so a 3.9 → 4.3 upgrade cannot have changed it; this is the wrong-version trap. D — `enable.idempotence` also became the default in **3.0**, and it adds no per-record round trip.
- 🧠 **Key point / trap:** keep the two waves apart — **3.0**: `acks=all`, `enable.idempotence=true`, `session.timeout.ms=45000`; **4.0**: `linger.ms=5`, KRaft-only, `num.recovery.threads.per.data.dir=2`.
- 📎 Source: `../../study-plan/week-03/resources/kip-1030-defaults-kafka-4-0.md` and `../../study-plan/VALIDATION.md` (row 3).

### Question 13 — Answer: **B**

- **Why correct:** `TopologyTestDriver` processes one piped record at a time and flushes afterwards, so every intermediate aggregation update is forwarded to the output topic — the test legitimately sees 1, 2, 3, 4, 5. In production the state store's record cache (`statestore.cache.max.bytes`, 10 MB) and the commit at `commit.interval.ms` (30,000 ms) coalesce successive updates of the same key, so far fewer records are emitted. The **final** value per key is identical either way, which is why the assertions remain valid.
- **Why the others are wrong:** A — `TopologyTestDriver` fully supports state stores; `driver.getKeyValueStore(...)` is a standard assertion target. C — `suppress` is never implicit; it must be added explicitly. D — thread count affects parallelism, not how many updates a single key emits.
- 🧠 **Key point / trap:** write assertions against the **final** state, not against the exact number of emitted updates — that count is a caching artefact and differs between the test driver and production.
- 📎 Source: `../../study-plan/week-06/resources/streams-testing-topologytestdriver.md` (cache flushed per record) and `../../study-plan/week-06/resources/streams-config.md`.

### Question 14 — Answer: **A, C**

- **Why correct:** A — a share consumer holds a record under a time-limited **acquisition lock**, default **30 seconds**. A 45-second unit of work outlives the lock, so the broker releases the record and hands it to another member while the first is still working — duplicate execution with no error anywhere. C — the remedy is to make the lock outlive the work (group config `share.record.lock.duration.ms`, bounded by the broker's `group.share.min/max.record.lock.duration.ms`, i.e. 15,000–60,000 ms) or to shorten the unit of work.
- **Why the others are wrong:** B — `max.poll.interval.ms` belongs to classic consumer groups; share groups use the acquisition lock instead. D — Queues for Kafka reached **GA in 4.2** (early access 4.0, preview 4.1), so "still early access in 4.3" is the outdated-value trap. E — `REJECT` means *this record is unprocessable, never deliver it again*; using it to signal success would silently discard genuine failures.
- 🧠 **Key point / trap:** the acquisition lock is the share-group analogue of an SQS visibility timeout — size it above your worst-case processing time, and remember the broker caps it at 60 s.
- 📎 Source: `../../study-plan/week-02/resources/kafka-share-groups.md` (lock duration 30 s, bounds, ACCEPT/RELEASE/REJECT).

### Question 15 — Answer: **B, D**

- **Why correct:** B — `errors.deadletterqueue.context.headers.enable` defaults to **false**; turning it on adds `__connect.errors.topic`, `.partition`, `.offset`, `.connector.name`, `.task.id`, `.stage`, `.exception.class.name` and more to every DLQ record, which is exactly the missing context. D — when the DLQ topic does not exist, the worker's admin client creates it with **one partition**; only `errors.deadletterqueue.topic.replication.factor` is configurable, so a 24-partition DLQ has to be pre-created.
- **Why the others are wrong:** A — there is no `errors.deadletterqueue.topic.partitions` property. C — the DLQ holds the record exactly **as read from Kafka** (raw key bytes, value bytes and original headers), precisely so that it can be replayed; that is why the original offset is recoverable at all. E — `errors.tolerance=none` fails the task on the first bad record and writes nothing to a DLQ.
- 🧠 **Key point / trap:** three DLQ facts that are almost always tested together — **sink connectors only**, **context headers off by default**, **auto-created with one partition and RF 3**.
- 📎 Source: `../../study-plan/week-05/resources/connect-error-handling-dlq-kip298.md`.

### Question 16 — Answer: **D**

- **Why correct:** a `transactional.id` names **one** logical producer. `initTransactions()` registers it with the transaction coordinator and bumps the producer **epoch**, which fences every earlier producer holding that id — the zombie-fencing mechanism. Three pods sharing one id therefore fence each other in a loop, and only the most recent one can commit. The fix is a stable, unique id per instance (a `StatefulSet` ordinal is the canonical pattern), so fencing protects a restart of *the same* instance.
- **Why the others are wrong:** A — `ProducerFencedException` is **fatal**: the producer must be closed and a new one created; retrying the commit cannot succeed. B — `transactional.id.expiration.ms` governs how long an idle id's metadata is retained; it cannot make an id safe to share. C — a fresh random UUID per start breaks fencing in the opposite direction: a restarted instance gets a new id, so the old zombie is never fenced and duplicates become possible.
- 🧠 **Key point / trap:** `transactional.id` must be both **unique across instances** and **stable across restarts**. Failing either half is a classic exam scenario — this question is the "shared id" half, the UUID-per-start question is the other.
- 📎 Source: `../../study-plan/week-03/resources/kip-98-exactly-once-transactions.md` (transactional id, epoch, zombie fencing).

### Question 17 — Answer: **C**

- **Why correct:** the order is 3 → 1 → 4 → 2. Start with the cheapest question — does the group have live members and is every partition assigned (`--describe --members --verbose` shows idle members with `#PARTITIONS 0`)? Then localise: is every partition lagging, or only one (`records-lag` per partition, which points at a hot key)? Then decide whether the application loop or the cluster is the bottleneck (`time-between-poll-max` against `max.poll.interval.ms`, `poll-idle-ratio-avg` near 0 meaning user code is slow). Only then scale, which is the expensive, irreversible step.
- **Why the others are wrong:** A (1 → 3 → 2 → 4) reads per-partition lag before establishing that anyone is consuming at all, and scales before looking at the poll metrics. B (4 → 3 → 1 → 2) starts with the poll metrics, which are meaningless if the group is `Empty`. D (3 → 4 → 2 → 1) scales before localising the lag, so a single hot partition would be "fixed" by adding consumers that cannot possibly be assigned any work.
- 🧠 **Key point / trap:** adding consumers is the *last* step, and it is useless once the number of members equals the partition count. Confirm membership → localise → measure the loop → scale.
- 📎 Source: `../../study-plan/week-08/resources/confluent-consumer-lag.md` and `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md`.

### Question 18 — Answer: **A**

- **Why correct:** co-partitioning requires **both** the same partition count **and** the same key-to-partition function. Streams only validates the partition count, which is why the application starts cleanly. `RoundRobinPartitioner` ignores the key, so `payments` records for a given `orderId` are scattered; the task that owns partition *n* of `orders` reads a state store built from partition *n* of `payments`, which usually does not hold that key — producing nulls for most lookups. Fix the producer, or force Streams to re-key the table side through `repartition()`.
- **Why the others are wrong:** B — a `KTable` from `builder.table(...)` is materialised for joins whether or not you name the store; a missing `Materialized` never causes systematic misses. C — the clean start is exactly the trap: the partition-count check passes, the hash check does not exist. D — `max.task.idle.ms` controls how long a task waits for the slower input to catch up in **time**; it cannot conjure a key that lives in a different partition.
- 🧠 **Key point / trap:** "same number of partitions" is necessary but not sufficient. A non-default `partitioner.class` on either side silently breaks co-partitioning without a single exception.
- 📎 Source: `../../study-plan/week-06/resources/streams-joins.md` (co-partitioning requirements).

### Question 19 — Answer: **A, D**

- **Why correct:** A — seven-day retention against a ten-day outage means the segments holding offset 88214 were deleted, so the fetch position fell **below the log start offset**. The consumer's `auto.offset.reset` is the default `latest`, so it silently jumped to the log end offset and consumed none of the backlog. D — `records-lead-min` measures the distance from the consumer's position to the **log start offset**; it trending toward 0 is the standard early warning for exactly this failure (the mirror image of `records-lag-max`, which measures distance to the log end).
- **Why the others are wrong:** B — the stem says the committed offsets are still present, and an expired commit produces a reset with **no** `OffsetOutOfRangeException`, because there is no position to be out of range. C — exceeding `max.poll.interval.ms` gives `CommitFailedException`, not an out-of-range fetch. E — compaction removes superseded records but does not advance the log start offset past a consumer's position; the consumer simply receives the next surviving offset.
- 🧠 **Key point / trap:** `auto.offset.reset=latest` turns data loss into **silence**. If you need to be told, set it to `none` and handle the exception; alert on `records-lead-min` long before that.
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md` (`records-lead-min`) and `../../study-plan/week-04/resources/kafka-consumer-configs.md`.

### Question 20 — Answer: **D**

- **Why correct:** 1-Y · 2-Z · 3-W · 4-X. The MSK port map is fixed: **9092** plaintext (in-VPC only, no auth), **9094** TLS, **9096** SASL/SCRAM (credentials in AWS Secrets Manager), **9098** IAM (`SASL_SSL` + `AWS_MSK_IAM`).
- **Why the others are wrong:** A swaps 9094 and 9096, i.e. puts SCRAM on the TLS-only port. B puts TLS on 9092 and plaintext on 9094, inverting the two. C swaps 9096 and 9098, putting IAM on the SCRAM port — the most tempting error because both are `SASL_SSL`.
- 🧠 **Key point / trap:** remember the ladder 9092 → 9094 → 9096 → 9098 as "nothing → TLS → SCRAM → IAM". Public access uses 9194/9196/9198, and the mnemonic still holds.
- 📎 Source: `../../study-plan/week-09/resources/msk-iam-access-control.md` and `../../study-plan/week-09/resources/msk-cluster-types-provisioned-express-serverless.md`.

### Question 21 — Answer: **C, E**

- **Why correct:** C — a follower is removed from the ISR when it has not fully caught up for `replica.lag.time.max.ms` (30,000 ms) and re-added when it does. A repeating shrink/expand cycle naming one broker is the signature of that broker periodically falling behind: saturated disk or NIC, long GC pauses, or too few `num.replica.fetchers` to keep up with the leaders it follows. E — while the ISR is `2,5` the partition still has two in-sync replicas, so `acks=all` writes with `min.insync.replicas=2` keep succeeding; durability is degraded but nothing fails. Only a shrink to a single replica would start rejecting writes.
- **Why the others are wrong:** A — acknowledgements do not recompute the ISR; the ISR is maintained by the leader from follower fetch progress, independently of `acks`. B — raising `min.insync.replicas` to 3 does nothing to a lagging follower; it only makes writes fail the instant the ISR drops below 3. D — `Shrinking ISR` is routine ISR maintenance; an unclean election logs a leader change with an out-of-sync replica, and `unclean.leader.election.enable` is already `false` by default.
- 🧠 **Key point / trap:** ISR flapping is a **broker health** signal, not a configuration signal. Chase the lagging broker; never "fix" it by changing `min.insync.replicas` or `acks`.
- 📎 Source: `../../study-plan/week-02/resources/kafka-replication-isr.md` (`replica.lag.time.max.ms`, ISR shrink/expand).

### Question 22 — Answer: **B, C**

- **Why correct:** B — `MockProducer(false, ...)` leaves each `send()` future uncompleted until the test drives it with `completeNext()` or `errorNext(RuntimeException)`; `errorNext` completes the future exceptionally **and** invokes the callback with that exception, which is exactly how you exercise a dead-letter branch without a broker. C — `history()` returns every `ProducerRecord` handed to `send()` since the last `clear()`, regardless of completion state, so the test can assert topic, key, value and headers.
- **Why the others are wrong:** A — simulating failures is one of `MockProducer`'s primary purposes; Testcontainers is unnecessary here and would blow the "milliseconds" budget. D — `MockProducer` ships inside `kafka-clients` itself, not `kafka-streams-test-utils`. E — `errorNext()` completes the **future** with the exception; `send()` itself returns normally, so the assertion is on `future.get()` throwing `ExecutionException` (or on the callback), not on `send()` throwing.
- 🧠 **Key point / trap:** `autoComplete=false` plus `completeNext()`/`errorNext()` is the whole toolkit for unit-testing producer success, retry and DLQ paths. Remember it lives in `kafka-clients`.
- 📎 Source: `../../study-plan/week-07/resources/kafka-mock-clients-javadoc.md`.

### Question 23 — Answer: **B**

- **Why correct:** Kafka Streams creates internal topics prefixed with `application.id` — `<app-id>-<store>-changelog` and `<app-id>-...-repartition` — and reads, writes and (at reset time) deletes them. Granting only the input/output topics leaves those internal topics unauthorised, which is what the exception names. The least-privilege answer is a **PREFIXED** ACL on `payments-app` for `Describe`, `Read` and `Write`, plus either `Create` on the cluster or pre-created topics.
- **Why the others are wrong:** A — `__consumer_offsets` stores committed offsets, not changelog data, and clients never need direct ACLs on it. C — there is no separate "internal Streams principal"; the application authenticates as its own principal, and `super.users` is the opposite of least privilege. D — `topology.optimization` can reuse a **source topic** as the changelog for a `KTable` read directly from it, but it does nothing for the state store of an aggregation, and this application still needs repartition topics.
- 🧠 **Key point / trap:** whenever a Streams app hits an authorization error, read the topic name: an `<application.id>-` prefix means you forgot the internal topics. One PREFIXED ACL covers them all.
- 📎 Source: `../../study-plan/week-07/resources/kafka-security-authorization-acls.md` (PREFIXED patterns) and `../../study-plan/week-06/resources/streams-core-concepts-architecture.md` (internal topic naming).

### Question 24 — Answer: **C**

- **Why correct:** the order is 2 → 4 → 3 → 1. `ExtractNewRecordState` must run first: until the Debezium envelope is unwrapped, the row's fields are nested under `after` and no field-level SMT can see `cust_id`. Masking must come **before** the rename, because `MaskField$Value` is configured with the field name `cust_id`, which no longer exists once `ReplaceField$Value` has renamed it. `RegexRouter` rewrites the **topic name** rather than the value, so it is independent of the field work and conventionally goes last.
- **Why the others are wrong:** A (1 → 2 → 3 → 4) routes first and masks last, so the mask targets a field that has already been renamed away. B (2 → 3 → 4 → 1) renames before masking — same failure, the mask silently matches nothing. D (4 → 2 → 1 → 3) masks before unwrapping, when `cust_id` is still nested and invisible to the SMT.
- 🧠 **Key point / trap:** SMTs run **in the order listed in `transforms=`**, each on the output of the previous one. Unwrap first, then field operations in the order their field names still exist, then routing.
- 📎 Source: `../../study-plan/week-05/resources/connect-transforms-predicates.md` and `../../study-plan/week-05/resources/debezium-postgres-cdc.md`.

### Question 25 — Answer: **A, E**

- **Why correct:** A — a Connect worker creates several kinds of client. Its **own** clients (group membership, internal topics, admin) read the unprefixed `bootstrap.servers` / `security.protocol` / `sasl.*` worker properties, which is why the worker itself starts fine. The producers and consumers it creates **for connectors** are configured from the `producer.*` and `consumer.*` prefixed copies; with those absent, `sasl.mechanism` falls back to its default `GSSAPI`, which the broker does not offer. E — duplicating the security block under `producer.`, `consumer.` and `admin.` prefixes in the worker properties fixes every connector at once.
- **Why the others are wrong:** B — connectors do **not** inherit the worker's unprefixed security settings; that is precisely the trap. C — `producer.override.*` / `consumer.override.*` are real and are permitted because `connector.client.config.override.policy` defaults to `All` since Kafka 3.0, but setting the policy to `None` would **forbid** overrides, not enable them, and per-connector overrides are the wrong tool for a cluster-wide misconfiguration. D — Connect does not negotiate Kerberos first; `GSSAPI` appears simply because it is the default value of `sasl.mechanism`, and enabling `GSSAPI` on the brokers would weaken security to work around a client typo.
- 🧠 **Key point / trap:** "the worker connects but every connector fails" almost always means missing `producer.` / `consumer.` / `admin.` prefixed copies of the security settings.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md` (client prefixes, override policy) and `../../study-plan/week-07/resources/kafka-security-sasl.md`.

### Question 26 — Answer: **B, E**

- **Why correct:** B — an aggregation writes into the state store's record cache; a downstream record is only forwarded when the cache evicts the entry (`statestore.cache.max.bytes`, default 10 MB) or when the commit flushes it. At a few records per minute the cache never fills, so the **commit** at `commit.interval.ms` (default 30,000 ms) is the only trigger — producing the almost exactly 30-second latency and the bursty output. E — `statestore.cache.max.bytes=0` disables the coalescing and forwards every update immediately; lowering `commit.interval.ms` is the gentler version of the same trade-off.
- **Why the others are wrong:** A — `suppress(untilWindowCloses)` applies to **windowed** aggregations and would *increase* latency, not reduce it; this aggregation is not windowed. C — under `exactly_once_v2` the default `commit.interval.ms` drops to **100 ms**, so EOS would make this particular latency far better, not worse. D — `fetch.max.wait.ms` is 500 ms and does not accumulate to 30 seconds; and raising `fetch.min.bytes` would make a low-traffic pipeline slower.
- 🧠 **Key point / trap:** a Streams latency that is suspiciously close to a round 30 seconds is the commit interval. High traffic hides it because the cache evicts long before the commit.
- 📎 Source: `../../study-plan/week-06/resources/streams-config.md` (`statestore.cache.max.bytes` 10 MB, `commit.interval.ms` 30,000 / 100 with EOS).

### Question 27 — Answer: **A**

- **Why correct:** 1-X · 2-Z · 3-Y · 4-W. `records-lead-min → 0` means the consumer's position is approaching the **log start offset**, so retention is about to delete unread data — buy time with retention or consumers (X). `time-between-poll-max ≈ 295,000 ms` is brushing `max.poll.interval.ms` (300,000 ms), so shrink the work per iteration or raise the limit (Z). An exhausted accumulator with threads waiting is the `buffer.memory` / `max.block.ms` story, and the real cure is whatever is stopping the sender from draining (Y). Tiny batches with a high request rate is the classic batching problem (W).
- **Why the others are wrong:** B inverts the first two and swaps the last two. C maps the buffer symptom to the poll-interval fix and the poll symptom to the buffer fix. D maps `records-lead-min` to batching and tiny batches to retention — the two most unrelated pairings in the set.
- 🧠 **Key point / trap:** keep `records-lag-*` and `records-lead-*` apart: **lag** is the distance to the log end (am I behind?), **lead** is the distance to the log start (am I about to lose data?).
- 📎 Source: `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md`.

### Question 28 — Answer: **C, D**

- **Why correct:** C — a KRaft controller quorum commits metadata by majority. With 1 of 3 voters alive there is no majority, `LeaderId: -1`, and no metadata record can be committed: no topic creation, no ACL change, no reassignment and, critically, **no leader election**. D — brokers continue to serve produce and fetch for partitions whose leaders are still alive, working from the metadata they already replicated; the cluster is frozen rather than dead, but the next broker failure leaves its partitions leaderless.
- **Why the others are wrong:** A — data-plane requests are served by brokers from cached metadata; they are not rejected wholesale, and `NotControllerException` is an admin-path error. B — in KRaft only nodes whose `process.roles` includes `controller` are voters; a plain broker cannot be promoted. E — with a static quorum, `controller.quorum.voters` is read at start-up, so editing it requires a restart; with a dynamic quorum, membership changes go through `kafka-metadata-quorum.sh --add-controller` / `--remove-controller` and still need a majority to commit.
- 🧠 **Key point / trap:** losing the controller quorum freezes the **control plane** while the **data plane** limps on. That is exactly why the quorum should be 3 or 5 and spread across failure domains.
- 📎 Source: `../../study-plan/week-01/resources/kafka-operations-kraft.md` and `../../study-plan/week-01/resources/kip-500-kip-853-kraft-confluent.md`.

### Question 29 — Answer: **B**

- **Why correct:** `--describe --all` prints the **effective** value plus its `synonyms`, listing every level that defines it in precedence order: `DYNAMIC_TOPIC_CONFIG` > `DYNAMIC_BROKER_CONFIG` > `DYNAMIC_DEFAULT_BROKER_CONFIG` > `STATIC_BROKER_CONFIG` > `DEFAULT_CONFIG`. Here the synonyms contain only `STATIC_BROKER_CONFIG` and `DEFAULT_CONFIG` — there is **no topic-level entry at all**, so the override was never applied to this topic (wrong entity name, wrong `--entity-type`, or deleted later). Re-apply it against `--entity-type topics --entity-name orders`.
- **Why the others are wrong:** A — the precedence is the other way round: a dynamic topic config **beats** a static broker config, which is the whole reason topic overrides work. C — `--describe --all` is precisely the form that shows effective values and synonyms for a topic; without `--all` it shows only explicit overrides. D — `min.insync.replicas` is a standard per-topic override and appears in the topic config list.
- 🧠 **Key point / trap:** `--describe` alone answers "what did we override?", `--describe --all` answers "what is actually in force and where does it come from?". Read the synonyms list before blaming the client.
- 📎 Source: `../../study-plan/week-02/labs.md` (synonyms output and precedence order) and `../../study-plan/week-02/resources/kafka-topic-configs.md`.

### Question 30 — Answer: **D**

- **Why correct:** a source connector's position lives in the `connect-offsets` topic, keyed by the **connector name** together with the connector-defined source partition. Renaming the connector therefore produces a new key with no stored offset, so the task starts from the beginning — the re-ingest. The supported reset path is `PUT /connectors/{name}/stop` (the connector must be in `STOPPED` state), then `DELETE /connectors/{name}/offsets` to clear them or `PATCH /connectors/{name}/offsets` to set a chosen position, then resume.
- **Why the others are wrong:** A — `DELETE /connectors/{name}` removes the connector and its configuration but explicitly **does not** delete its offsets; recreating it under the *same* name resumes where it left off. B — source connectors do not use `__consumer_offsets` or a consumer group; that applies to **sink** connectors. C — `connect-offsets` is compacted precisely so that the latest offset per key is retained indefinitely; `delete.retention.ms` governs tombstone visibility, not live keys.
- 🧠 **Key point / trap:** connector **name** is the identity of a source connector's position. Never rename a connector to "start fresh" — stop it and reset its offsets through the REST API.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md` (`GET|PATCH|DELETE /connectors/{name}/offsets`, 3.6+, requires `STOPPED`).

### Question 31 — Answer: **A**

- **Why correct:** KIP-441 warm-up replicas exist so that scaling out never stops processing. A new instance first receives a **warm-up replica** that restores state from the changelog; the active task only moves once that replica is within `acceptable.recovery.lag` (default 10,000 records). Only `max.warmup.replicas` warm-ups (default **2**) are assigned at a time, and the reassignment happens on a **probing rebalance** whose interval defaults to `probing.rebalance.interval.ms` = **600,000 ms** (10 minutes). Five new instances × 30 GB of state, two at a time, on 10-minute probes, is close to an hour.
- **Why the others are wrong:** B — static membership reduces rebalances; it has nothing to do with whether a stateful task may move. C — the task count is derived from the input partition count, not from the first instance, and Streams rebalances on every membership change. D — `num.standby.replicas` adds passive copies of state; it does not cap the group size, and setting it to 0 would remove the fast-failover behaviour the team relies on.
- 🧠 **Key point / trap:** for large state, "scaling out is slow" is usually **by design**. Tune `max.warmup.replicas` and `probing.rebalance.interval.ms` in advance of a known traffic event rather than during it.
- 📎 Source: `../../study-plan/week-06/resources/streams-config.md` (`acceptable.recovery.lag` 10,000 · `max.warmup.replicas` 2 · `probing.rebalance.interval.ms` 600,000).

### Question 32 — Answer: **C**

- **Why correct:** (1) the Confluent serdes accept a pseudo-URL `mock://<scope>`, which wires in `MockSchemaRegistryClient` — an in-process registry with no HTTP call at all, so thousands of serialization round trips cost nothing. (2) Verifying that the **real** registry enforces the subject's compatibility level requires the real component, which is exactly what Testcontainers provides for a nightly (slower) suite.
- **Why the others are wrong:** A — `TopologyTestDriver` has no Schema Registry of its own, and `MockSchemaRegistryClient` is the fast in-memory stand-in, not the thing under test for compatibility enforcement. B — pointing unit tests at a shared registry reintroduces the network and makes tests order-dependent; and `TopologyTestDriver` cannot evaluate compatibility levels. D — `MockProducer` does bypass serializers, which makes it useless for requirement (1); `EmbeddedKafkaCluster` is a broker, not a registry.
- 🧠 **Key point / trap:** match the double to the question. Serde correctness → `mock://`. Registry **policy** correctness → a real registry.
- 📎 Source: `../../study-plan/week-07/resources/testcontainers-kafka.md` (Testcontainers + Schema Registry, `mock://` for serdes) and `../../study-plan/week-05/resources/schema-registry-wire-format-serdes.md`.

### Question 33 — Answer: **D**

- **Why correct:** `ssl.endpoint.identification.algorithm` defaults to `https`, which makes the client verify that the broker's certificate actually identifies the host it dialled (via the SAN extension). Setting it to an empty string turns that check off: the client still requires a certificate chaining to a trusted CA, but it no longer cares **whose** certificate it is, so anything holding a CA-signed certificate — including an attacker with one — is accepted. The real fix is to re-issue the broker certificate with a SAN covering the name clients use, have clients connect by that name, and restore the default.
- **Why the others are wrong:** A — it is not a logging switch; it disables a real security control. B — it has nothing to do with mutual TLS, which is controlled by `ssl.client.auth` on the broker and a keystore on the client. C — chain validation is governed by the truststore and remains active; only hostname verification is disabled, so importing the certificate does not address the risk and leaving the property empty keeps the hole open.
- 🧠 **Key point / trap:** "No subject alternative names matching…" means the certificate is wrong, not the client. Since Kafka 2.0 hostname verification is on by default, and turning it off is a downgrade dressed up as a fix.
- 📎 Source: `../../study-plan/week-07/resources/kafka-security-ssl.md` (`ssl.endpoint.identification.algorithm`, SAN requirement).

### Question 34 — Answer: **B**

- **Why correct:** reassignment moves data by ordinary replica fetching, and the `--throttle` value caps that traffic. When the throttle is below the topic's incoming write rate (`max(BytesInPerSec) > throttle` — 10 MB/s against 45 MB/s here) the destination replica falls further behind every second and can never enter the ISR, so the reassignment stays "in progress" forever. Raise it in place with `--additional --execute --throttle <higher>` on the same JSON file and confirm that `kafka.server:type=FetcherLagMetrics,name=ConsumerLag` is falling.
- **Why the others are wrong:** A — `--verify` reports the live status of the last `--execute`; the line is current, not stale, and re-running `--execute` on an in-flight reassignment is not a refresh. C — the tool clears throttles only when **every** partition in the file has completed, and it prints `Clearing broker-level throttles…` when it does; no such line appeared. D — `--verify` is a status query and is unaffected by producer traffic; pausing producers would in fact let the throttled fetcher catch up, but that is a workaround, not the diagnosis.
- 🧠 **Key point / trap:** two throttle traps live together — a throttle set **too low** means the move never finishes, and forgetting to run `--verify` after it does finish leaves normal replication throttled.
- 📎 Source: `../../study-plan/week-08/resources/kafka-basic-ops-reassignment.md` (throttle vs `BytesInPerSec`, `--additional`, `FetcherLagMetrics`).

### Question 35 — Answer: **C**

- **Why correct:** the order is 2 → 4 → 3 → 1. `--generate` proposes a plan and prints the **current** assignment, which must be saved because it is the only rollback artefact. `--execute` applies the proposed plan with a throttle so business traffic is not starved. While it runs, `FetcherLagMetrics ConsumerLag` on the destination brokers is the progress signal. Finally `--verify` confirms completion **and** is what removes the broker-level and topic-level throttles the tool installed.
- **Why the others are wrong:** A (4 → 2 → 1 → 3) executes before a plan exists. B (2 → 1 → 4 → 3) verifies before executing, which reports nothing useful and leaves throttles to be cleaned up later. D (4 → 3 → 2 → 1) again executes first and generates the plan afterwards.
- 🧠 **Key point / trap:** `--verify` is not optional housekeeping. If you never run it, `leader.replication.throttled.rate` and `follower.replication.throttled.rate` stay in place and silently throttle ordinary replication.
- 📎 Source: `../../study-plan/week-08/resources/kafka-basic-ops-reassignment.md` (`--generate` / `--execute` / `--verify`, throttle removal).

### Question 36 — Answer: **A**

- **Why correct:** static membership (KIP-345) works by giving each instance a `group.instance.id` that is **unique among members** and **stable across restarts**, so the coordinator can hand a returning instance its previous assignment without a rebalance. When six pods claim the same id, the coordinator treats each new registration as a replacement and fences the previous holder with `FencedInstanceIdException`. Deriving the id from a per-pod identity (a `StatefulSet` ordinal, or the pod name through the downward API) restores both properties.
- **Why the others are wrong:** B — removing the id does stop the exception, but it also throws away the benefit the team wanted (no rebalance on rolling restarts); the fix is to set the id correctly, not to abandon the feature. C — the session timeout governs how long a **missing** member is tolerated; it cannot resolve a collision between two live members. D — KIP-848 keeps `group.instance.id` for static membership; `group.remote.assignor` chooses the server-side assignor and is unrelated.
- 🧠 **Key point / trap:** `FencedInstanceIdException` has exactly one meaning — two live members are claiming one static id. It is almost always a templating or environment-variable mistake.
- 📎 Source: `../../study-plan/week-04/resources/kip-345-static-membership.md`.

### Question 37 — Answer: **B**

- **Why correct:** with tiered storage, `local.retention.ms` governs how much of the log stays on broker disks; older segments are offloaded to remote storage and remain readable for the full `retention.ms`. A consumer that falls behind the **local** window is served from remote storage instead of the page cache, which is exactly the observed signature: `records-lead-min` at 0 relative to the *local* start, `fetch-latency-avg` in the hundreds of milliseconds and elevated `RemoteTimeMs` on `FetchConsumer`. No data is lost and nothing errors — throughput is simply much lower until the group catches back up into the local window.
- **Why the others are wrong:** A — remote data is still within `retention.ms` (90 days), so it has not been deleted and `OffsetOutOfRangeException` does not apply. C — the consumers use the defaults here, and `fetch.max.wait.ms` caps at 500 ms; it cannot explain 900 ms averages accompanied by broker-side `RemoteTimeMs`. D — serving consumer fetches from remote storage is precisely what tiered storage does; that is the feature.
- 🧠 **Key point / trap:** on a tiered topic, `records-lead-min ≈ 0` no longer means imminent data loss — it means "about to read from object storage". Alert on fetch latency and remote read metrics instead.
- 📎 Source: `../../study-plan/week-08/resources/kafka-tiered-storage.md` and `../../study-plan/week-08/resources/kafka-monitoring-client-metrics.md`.

### Question 38 — Answer: **D**

- **Why correct:** every task of a sink connector is a consumer in **one** consumer group subscribed to the connector's topics. The framework does start `tasks.max` tasks — all 12 are legitimately `RUNNING` — but the group can only assign 4 partitions, so 8 members sit idle with `sink-record-read-rate` at 0. The parallelism ceiling is the partition count, exactly as for any consumer group; raising throughput means adding partitions to `events` first.
- **Why the others are wrong:** A — the idle tasks read nothing at all, so they never reach the S3 write path; `s3.part.size` tunes upload chunking, not assignment. B — the tasks are `RUNNING`, not `UNASSIGNED` or `FAILED`; a restart produces the same 4/8 split. C — `tasks.max` is a per-connector total across the whole cluster, not per worker, and lowering it to 2 would reduce parallelism below the available 4.
- 🧠 **Key point / trap:** for a sink connector, useful tasks = `min(tasks.max, partitions)`. Idle tasks look healthy in `/status`, so check `sink-record-read-rate` per task before concluding that scaling worked.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md` (`tasks.max`, sink tasks as a consumer group).

### Question 39 — Answer: **A**

- **Why correct:** Kafka has three quota types — `producer_byte_rate`, `consumer_byte_rate` and `request_percentage`. The last one limits the share of **request-handler and network thread time** a client may use (a quota of *n*% is *n*% of one thread, out of `(num.io.threads + num.network.threads) * 100`%). With `fetch.min.bytes=1` and `fetch.max.wait.ms=10` the consumer issues a flood of near-empty fetches, each costing broker thread time while moving almost no bytes — so the byte rate stays low while the request quota is exhausted, and the broker returns throttle delays that the client records as `fetch-throttle-time-avg`. Batch the fetches (raise `fetch.min.bytes` and `fetch.max.wait.ms`) or raise `request_percentage`.
- **Why the others are wrong:** B — an unset quota means *no limit*, not 0 B/s; unconfigured clients are unthrottled unless a `--entity-default` exists. C — the client-side `fetch-throttle-time-avg` records the throttle delay the broker returned, whatever quota produced it; it is not bandwidth-specific. D — `request_percentage=200` is valid and means 200% of one thread (two threads' worth), not 200% of the host.
- 🧠 **Key point / trap:** low bytes plus high throttle time equals a **request-rate** quota. Chatty clients with tiny fetches are the usual victims.
- 📎 Source: `../../study-plan/week-07/resources/kafka-quotas.md` (three quota types, request-rate semantics, `fetch-throttle-time-avg`).

### Question 40 — Answer: **A, B**

- **Why correct:** A — with the default `message.timestamp.type=CreateTime` the broker stores the **producer's** timestamp, and retention deletes a segment once its maximum timestamp is older than `retention.ms`. Records stamped in 1970 make their segment eligible the moment it rolls, regardless of when it was actually written. B — `LogAppendTime` makes the broker overwrite every timestamp at append, which immunises retention (and log-roll behaviour) against client clock bugs; the cost is that event time is lost, so downstream Streams windowing must fall back to a timestamp extractor reading a field inside the payload.
- **Why the others are wrong:** C — `log.retention.check.interval.ms` only changes **how often** the deletion check runs; the verdict is the same. D — `message.timestamp.before.max.ms` defaults to `Long.MAX_VALUE` (it is `message.timestamp.after.max.ms` that defaults to 1 hour), so timestamps far in the past are accepted by default; setting it explicitly would be a valid *additional* guard. E — compaction retains the latest value per key and is unrelated to timestamp-driven deletion; it also would not suit a telemetry topic.
- 🧠 **Key point / trap:** "records vanish long before `retention.ms`" is a **timestamp** bug, not a retention bug. The two guards are `LogAppendTime` and `message.timestamp.before.max.ms`.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md` (`message.timestamp.type` / `.after.max.ms` 1 h / `.before.max.ms` MAX_LONG).

### Question 41 — Answer: **C**

- **Why correct:** the legacy factory `TimeWindows.of(size)` carried an implicit **grace period of 24 hours**, so a window that ended at 09:00 kept accepting and re-emitting updates for late records until 09:00 the next day — exactly the reported symptom. The modern API deliberately removed the hidden default: `ofSizeWithNoGrace(size)` and `ofSizeAndGrace(size, grace)` force an explicit choice. A 30-second grace bounds the lateness, and `suppress(Suppressed.untilWindowCloses(...))` turns the stream of updates into one final result per window.
- **Why the others are wrong:** A — tumbling windows do close (at window end + grace); session windows close on an inactivity gap and would change the semantics entirely. B — store retention controls how long a window's state is queryable, not whether late records update it, and it never republishes windows spontaneously. D — the changelog carries the same updates as the output topic in this topology; the source of the updates is the grace period, not the topic being read.
- 🧠 **Key point / trap:** any surviving `TimeWindows.of(...)` in a codebase is a 24-hour grace period hiding in plain sight. The API change from `of` to `ofSizeAndGrace` / `ofSizeWithNoGrace` exists precisely because that default surprised everyone.
- 📎 Source: `../../study-plan/week-06/resources/streams-dsl-api.md` (grace period; legacy `TimeWindows.of` default 24 h).

### Question 42 — Answer: **D**

- **Why correct:** `max.poll.records` slices an **already fetched** internal buffer; it never reaches the broker and never bounds memory. The fetch is bounded by `fetch.max.bytes` (50 MB for the whole response) and `max.partition.fetch.bytes` (1 MB **per partition**). With 60 assigned partitions the consumer can hold roughly 60 MB of uncompressed records, plus decompression buffers and the objects the deserializer creates — easily fatal in a 1 GB heap under load. Lower `max.partition.fetch.bytes`, lower `fetch.max.bytes`, or spread the partitions over more instances.
- **Why the others are wrong:** A — the whole premise of the question is that this reasoning is wrong; `max.poll.records` shapes the processing loop, not the network buffer. B — `fetch.min.bytes` is a *minimum* that makes the broker wait; raising it increases, not decreases, the bytes returned per response. C — `receive.buffer.bytes` is the socket buffer; the decoded records live on the heap far beyond it.
- 🧠 **Key point / trap:** consumer memory scales with **assigned partitions × `max.partition.fetch.bytes`**, not with `max.poll.records`. This is the same distinction as "`max.poll.records` does not reduce network traffic".
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-configs.md` (`fetch.max.bytes` 50 MB, `max.partition.fetch.bytes` 1 MB, `max.poll.records` 500 client-side only).

### Question 43 — Answer: **D, E**

- **Why correct:** D — `exactly.once.source.support` is a **worker** property with three values, `disabled` (default) → `preparing` → `enabled`, and the upgrade is a two-pass rolling restart: every worker to `preparing` first, then every worker to `enabled`. Mixing `disabled` and `enabled` workers in one cluster is not supported, so the direct jump is refused. E — once enabled, the worker writes each `SourceTask.poll()` batch and its source offsets inside **one producer transaction**; `transaction.boundary` defaults to `poll` and may be set to `interval` (using `transaction.boundary.interval.ms`) or `connector`.
- **Why the others are wrong:** A — exactly-once source support is **distributed mode only**; a standalone worker has no leader to perform zombie fencing and no per-connector offsets topic. B — `exactly.once.support=required` is a per-connector **preflight check** that the connector class and the worker can actually deliver EOS; it enables nothing on its own and fails outright if the worker has EOS disabled. C — consumers of an EOS source topic must set `isolation.level=read_committed`; a `read_uncommitted` consumer sees aborted records.
- 🧠 **Key point / trap:** three independent switches — worker `exactly.once.source.support`, connector `exactly.once.support`, consumer `isolation.level`. All three must line up, and the worker rollout is two passes.
- 📎 Source: `../../study-plan/week-05/resources/connect-exactly-once-source-kip618.md`.

### Question 44 — Answer: **B**

- **Why correct:** `retention.bytes` (like `retention.ms`) is evaluated **per partition**. With 24 partitions the topic can grow to 24 × 10 GiB = 240 GiB of log per full replica set, which is precisely what they measured. To cap the topic at 10 GiB the value must be divided by the partition count, and the cluster-wide disk footprint is a further ×3 because `replication.factor=3`.
- **Why the others are wrong:** A — `retention.bytes` is honoured under the plain `delete` policy; `compact,delete` merely adds compaction on top. C — retention is measured against the bytes actually stored on disk, which are the compressed segment bytes. D — `log.retention.bytes` is the broker default and `retention.bytes` is its documented per-topic override; the value was honoured, just not with the semantics the operator assumed.
- 🧠 **Key point / trap:** every retention setting is per **partition**, and every disk-sizing estimate must then be multiplied by the replication factor. Both multipliers are routinely forgotten in capacity planning questions.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md` (`retention.bytes` per partition; `log.retention.bytes` default -1).

### Question 45 — Answer: **A**

- **Why correct:** for records with a `null` key the default partitioner batches **stickily** — it fills one partition's batch, then picks another — and since KIP-794 it also does **adaptive partitioning**: `partitioner.adaptive.partitioning.enable` is `true` by default, so the choice of the next sticky partition is weighted by each partition's send-queue length in the accumulator — partitions on faster brokers receive proportionally more records. A 40 % deficit on a slow broker's partitions, with larger batches elsewhere, is the feature working as designed. Records **with** a key are untouched — their partition is still `murmur2(key) % numPartitions`.
- **Why the others are wrong:** B — the sticky partitioner is deliberately not strict round-robin; that is what makes batching effective. C — produce failures surface as exceptions and a non-zero `record-error-rate`, not as a quiet skew; nothing is dropped. D — null-keyed records are spread across partitions, not pinned to partition 0, and `partitioner.ignore.keys=true` affects **keyed** records by making Kafka ignore the key.
- 🧠 **Key point / trap:** partition **balance** is not a goal for null-keyed records; throughput is. Only keyed records carry an ordering-and-placement contract, and that contract is unaffected by adaptive partitioning.
- 📎 Source: `../../study-plan/week-03/resources/kip-480-794-sticky-partitioner.md`.

### Question 46 — Answer: **C**

- **Why correct:** with an **instance** `@Container` field, Testcontainers starts and stops a broker for every test class — 18 start-ups. Declaring the field `static` (or managing a singleton started once in a static initialiser of a shared base class) starts one broker for the whole suite and lets Ryuk clean it up at JVM exit. Because the tests need isolation only from each other's *data*, generating a unique topic name and `group.id` per test gives that isolation at zero cost.
- **Why the others are wrong:** A — `TopologyTestDriver` tests a Streams topology in isolation; it is not a substitute for tests that exercise a real broker, real clients and real consumer-group behaviour. B — container **reuse** (`testcontainers.reuse.enable`) keeps a container alive *between JVM runs* on a developer machine; it is explicitly not intended for, and gives nothing on, an ephemeral CI runner that is destroyed after the build. D — running 18 containers in parallel multiplies memory and CPU pressure on the runner and usually makes the suite slower and flakier, not faster.
- 🧠 **Key point / trap:** `static @Container` = one container per class; a shared singleton = one per suite. The default (instance field) is per test class and is where integration-suite time goes.
- 📎 Source: `../../study-plan/week-07/resources/testcontainers-kafka.md` (`static KafkaContainer`, shared across the class; Ryuk cleanup).

### Question 47 — Answer: **B**

- **Why correct:** the message is produced when the producer cannot find the topic in the cluster metadata. Two causes give exactly this text: the topic really does not exist (and `auto.create.topics.enable=false` means nothing will create it), or the principal lacks `Describe` on it — an unauthorised client is simply not told the topic exists, so it never appears in the metadata response. The 60 seconds is `max.block.ms` (default 60,000 ms), which bounds how long `send()` may block waiting for metadata or for buffer space.
- **Why the others are wrong:** A — `request.timeout.ms` is 30,000 ms and is a per-RPC timeout, not a metadata deadline; a broken `advertised.listeners` normally prevents the connection itself, which the stem rules out. C — with auto-creation disabled the client never gets `UnknownTopicOrPartitionException` from `send()`; it waits for metadata and then times out with this exact message, and the successful authentication rules out DNS. D — `delivery.timeout.ms` (120,000 ms) starts only once a batch exists; the record never got that far, and `metadata.max.age.ms` controls refresh frequency, not the block.
- 🧠 **Key point / trap:** "not present in metadata after 60000 ms" is a **two-suspect** message: missing topic or missing `Describe` ACL. On MSK with IAM, the second is the more common one.
- 📎 Source: `../../study-plan/week-03/resources/producer-configs.md` (`max.block.ms` 60,000) and `../../study-plan/week-07/resources/kafka-security-authorization-acls.md`.

### Question 48 — Answer: **A, C**

- **Why correct:** A — the registry's default compatibility level is `BACKWARD`: a reader on the **new** schema must be able to read data written with the **old** one. Adding a required field breaks that, because old records carry no value for it and the reader has no default to fall back on; giving `channel` a default makes the change compatible. C — the same change **is** accepted under `FORWARD`, whose contract is that a reader on the old schema can read data written with the new one. Choosing `FORWARD` is a legitimate, documented decision for a producers-first rollout, not a hack.
- **Why the others are wrong:** B — HTTP 409 from Schema Registry means **incompatible**; re-registering an identical schema is idempotent and simply returns the existing id. D — `auto.register.schemas=false` moves the failure, it does not remove it: the producer then fails with `Schema not found` because no matching schema is registered. E — compatibility is evaluated against the latest version for `BACKWARD` / `FORWARD` and across all versions only for the `*_TRANSITIVE` levels, and a required field with a default is perfectly acceptable.
- 🧠 **Key point / trap:** map the level to the **rollout order** — `BACKWARD` = consumers first, `FORWARD` = producers first, `FULL` = either. Then check whether the specific change (add / remove, with or without a default) satisfies it.
- 📎 Source: `../../study-plan/week-05/resources/schema-registry-compatibility.md`.

### Question 49 — Answer: **B, D**

- **Why correct:** B — the default `default.deserialization.exception.handler` is `LogAndFailExceptionHandler`, which is why one bad record kills the instance. Switching to `LogAndContinueExceptionHandler` logs the failure and skips the record so the task survives. D — skipping alone loses the evidence; setting `errors.deadletterqueue.topic.name` (the Kafka Streams DLQ from KIP-1034, available since 4.2) makes the `LogAndContinue*` handlers forward the failing record to that topic with `__streams.errors.exception` / `.stacktrace` / `.topic` / `.partition` / `.offset` headers. Unlike Connect, Streams does not create the DLQ topic for you.
- **Why the others are wrong:** A — `errors.tolerance` is a **Connect** property; Streams has no such setting and its DLQ is driven by the exception handlers instead. C — the default handler is indeed `LogAndFailExceptionHandler`, but there is no deserialization retry: a malformed record will never parse, so retrying is pointless and Streams does not do it. E — `exactly_once_v2` governs transactional output; a deserialization failure happens before any processing and is unaffected.
- 🧠 **Key point / trap:** the two frameworks look alike and are not. Connect: `errors.tolerance=all` + DLQ, **sink only**, topic auto-created. Streams: exception handler + `errors.deadletterqueue.topic.name`, topic owned by you.
- 📎 Source: `../../study-plan/week-06/resources/streams-upgrade-kip-1071-dlq.md` (KIP-1034 DLQ, `__streams.errors.*` headers).

### Question 50 — Answer: **D**

- **Why correct:** on the broker the size limit is applied to the whole **record batch** as it arrives — after compression, including batch overhead — not to individual records. With `batch.size=1048576`, `linger.ms=50` and no compression, the accumulator happily assembles five 200 KB records into a batch above the 1,048,576-byte ceiling, and the broker rejects it. The odd default of **1,048,588** exists precisely to leave headroom above a round 1 MiB for the batch header. Raise `max.message.bytes`, lower `batch.size`, or turn on compression.
- **Why the others are wrong:** A — both sides measure the same thing (the compressed batch); the mismatch here is the operator's 12-byte "tidying", not a units problem, and leaving the default is not the only option. B — `replica.fetch.max.bytes` is a broker-level fetch bound and is not derived from a topic's `max.message.bytes`; and the rejection happens at the leader on append, before any follower fetch. C — 1,048,576 is a perfectly valid value; nothing is silently reverted.
- 🧠 **Key point / trap:** 1,048,588 ≠ 1,048,576. `message.max.bytes` / `max.message.bytes` is a **batch-level, post-compression** limit on the broker, while `max.request.size` is a per-request limit on the producer.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs.md` and `../../study-plan/week-01/resources/kafka-broker-configs-listeners.md` (`message.max.bytes` 1,048,588, measured after compression at batch level).

### Question 51 — Answer: **C**

- **Why correct:** the runbook froze a **pre-3.0** value. KIP-735 raised the default `session.timeout.ms` from 10,000 to **45,000 ms** in Kafka 3.0 exactly so that ordinary restarts and short GC pauses do not evict members. At 10,000 ms a 20-second pod restart always outlives the session, so the coordinator declares each pod dead, rebalances, then rebalances again when it returns. Removing the override restores 45,000 ms; pairing it with static membership (`group.instance.id`) removes the rebalance entirely for planned restarts.
- **Why the others are wrong:** A — `heartbeat.interval.ms` is still 3,000 ms in 4.3 (the rule of thumb is ≤ ⅓ of the session timeout, and 3,000 fits 45,000 well); it did not change. B — `group.protocol` still defaults to `classic` in 4.3, so `session.timeout.ms` is very much in force; and fast processing rules out `max.poll.interval.ms`. D — 10,000 ms is the **old** default, which is the trap the whole question is built on; `group.initial.rebalance.delay.ms` (3,000 ms) only delays the first rebalance of an empty group.
- 🧠 **Key point / trap:** a value copied from an old runbook is indistinguishable from a deliberate override. When a default has moved, the stale config is *more* dangerous than no config, because nothing warns you.
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-configs.md` (`session.timeout.ms` 45,000 since 3.0) and `../../study-plan/VALIDATION.md` (row 4).

### Question 52 — Answer: **A**

- **Why correct:** since Kafka 2.3 (KIP-415) Connect uses incremental cooperative rebalancing. When a worker leaves, the leader deliberately **withholds** its connectors and tasks for up to `scheduled.rebalance.max.delay.ms` (default **300,000 ms** = 5 minutes) so that a worker restarting briefly can reclaim its own work without a second, disruptive reassignment. The tasks show as `UNASSIGNED` during that window, and nothing is logged as an error because nothing is wrong. Lowering the value trades faster failover for more rebalance churn on every deployment.
- **Why the others are wrong:** B — this is long-standing designed behaviour, not a defect, and no release removed it. C — `UNASSIGNED` is not `FAILED`; the tasks restart on their own, and a `restart?onlyFailed=true` call would be a no-op. D — the delay is a Connect worker property, not a consumer `session.timeout.ms`; `connect.protocol` selects the rebalance protocol (`eager` / `compatible` / `sessioned`) and does not remove the scheduled delay.
- 🧠 **Key point / trap:** a five-minute gap after a Connect worker dies is the default, not an incident. Tune `scheduled.rebalance.max.delay.ms` to your node-rotation behaviour before you page anyone.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md` (`scheduled.rebalance.max.delay.ms` 300,000, KIP-415).

### Question 53 — Answer: **D**

- **Why correct:** a `GlobalKTable` is bootstrapped and then kept up to date by a dedicated **global consumer thread** that reads all partitions of the table topic independently of the stream tasks. There is no time synchronisation between that thread and the processing of a stream record, so a record arriving 400 ms after a table update may legitimately be joined against the pre-update state. That looseness is the price of the `GlobalKTable`'s two big advantages: no co-partitioning requirement and arbitrary foreign-key lookups. When event-time correctness matters, use a co-partitioned `KStream`-`KTable` join, which does respect timestamps.
- **Why the others are wrong:** A — the global thread applies updates as it reads them, not on commit boundaries; lowering `commit.interval.ms` does not make the join deterministic. B — a `KStream`-`GlobalKTable` join is triggered **only** by stream-side records, and the join sides cannot be swapped. C — `max.task.idle.ms` synchronises the inputs of a **task** (for example the two sides of a `KStream`-`KTable` join); the global store is not a task input, so it has no effect here.
- 🧠 **Key point / trap:** `GlobalKTable` = full local copy, no co-partitioning, **no timestamp synchronisation**. `KTable` = co-partitioned, per-task, timestamp-aware. Pick based on which guarantee you actually need.
- 📎 Source: `../../study-plan/week-06/resources/streams-joins.md` (KStream-GlobalKTable: stream-side triggered, no co-partitioning, updates only refresh local state).

### Question 54 — Answer: **B**

- **Why correct:** when the ELR feature is enabled, `min.insync.replicas` becomes a **cluster-level** setting: it must be managed with `--entity-type brokers --entity-default`, per-broker values are not supported, and any existing static broker-level value is removed. On top of that, **any** update to `min.insync.replicas` at cluster or topic level — even setting it to the value it already has — clears the ELR state of the affected partitions, which then has to be rebuilt as replicas fall out of and return to the ISR. Both effects together explain the empty `Elr:` column and the unexpected behaviour.
- **Why the others are wrong:** A — per-broker values are exactly what ELR disallows, and an empty `Elr:` here is a consequence of the change, not evidence that nothing ever left the ISR. C — ELR complements `min.insync.replicas`; the strict-min-ISR rule that makes ELR safe is *defined* in terms of it. D — ELR state is cleared by `min.insync.replicas` changes and by a replica losing its log directory; `unclean.leader.election.enable` remains `false` by default and is a separate mechanism.
- 🧠 **Key point / trap:** with ELR, `min.insync.replicas` is a cluster-wide knob with a side effect — touching it resets ELR. Set it once, at the cluster default, before you start relying on ELR.
- 📎 Source: `../../study-plan/week-02/resources/kafka-eligible-leader-replicas.md` (cluster-level requirement; ELR state cleared on any `min.insync.replicas` change).

### Question 55 — Answer: **C**

- **Why correct:** 1-Y · 2-Z · 3-W · 4-X. `ProducerFencedException` means another producer claimed the same `transactional.id` and bumped the epoch (Y). `OffsetOutOfRangeException` means the fetch position no longer exists in the log, normally because retention removed it (Z). `UnsupportedSaslMechanismException` means the client's `sasl.mechanism` is not in the listener's `sasl.enabled.mechanisms` (W). `InvalidPartitionsException` is what `kafka-topics.sh --alter --partitions` returns when asked to **shrink** a topic (X).
- **Why the others are wrong:** A swaps the two security/offset causes (SASL onto the offset exception and vice versa). B rotates three of the four, pairing the transaction exception with retention. D swaps the transaction and partition-count causes, which is the easiest slip because both are "administrative" errors.
- 🧠 **Key point / trap:** classify before you match — **transactional** (`ProducerFenced`, `OutOfOrderSequence`), **position** (`OffsetOutOfRange`), **security** (`UnsupportedSaslMechanism`, `TopicAuthorization`), **admin** (`InvalidPartitions`, `InvalidReplicationFactor`). The class usually eliminates three options.
- 📎 Source: `../../study-plan/week-03/resources/kip-98-exactly-once-transactions.md`, `../../study-plan/week-07/resources/kafka-security-sasl.md` and `../../study-plan/week-01/resources/kafka-intro-and-quickstart.md`.

### Question 56 — Answer: **C, E**

- **Why correct:** C — `POST /compatibility/subjects/{subject}/versions/latest` (and the Schema Registry Maven/Gradle plugin's compatibility-test goal) evaluates a candidate schema against the subject's configured level and returns `{"is_compatible": false}` **without registering anything**, in milliseconds. That is the purpose-built CI check. E — `TopologyTestDriver` runs the whole topology in-process with `TestInputTopic` / `TestOutputTopic`, so asserting output records against golden expectations catches a shape change in under a second with no broker.
- **Why the others are wrong:** A — a full Testcontainers stack does exercise the real components, but broker plus registry start-up alone consumes most of the two-minute budget; it belongs in a nightly suite, which is exactly the "technically correct, wrong requirement" trap. B — registering the schema makes the check destructive: a compatible-but-unwanted schema is now permanently a version of the production subject. D — `errors.tolerance=all` is a Connect runtime setting; counting DLQ records is a slow, indirect and non-deterministic substitute for a compile-time check.
- 🧠 **Key point / trap:** the compatibility **check** endpoint and the **register** endpoint are different calls. CI must use the former; only the deploy step may use the latter.
- 📎 Source: `../../study-plan/week-07/resources/schema-registry-compatibility-testing.md` and `../../study-plan/week-06/resources/streams-testing-topologytestdriver.md`.

### Question 57 — Answer: **A**

- **Why correct:** unclean leader election lets a replica that is **not** in the ISR become leader. Such a replica is missing records the old leader had already committed, so when it takes over, the partition's log end offset moves **backwards** and followers truncate to match. Committed consumer offsets, recorded against the old, longer log, now point past the new log end — which is exactly why `LAG` is negative. The warehouse rows are the records that existed only on the replicas that were lost: acknowledged data, permanently gone. This is the trade the flag makes explicit — availability in exchange for durability.
- **Why the others are wrong:** B — `assign()` does not let a consumer commit an offset beyond the log end; nothing about manual assignment produces negative lag. C — the group's offsets were not reset; if they had been reset `--to-latest`, they would equal the log end offset and lag would be 0, not negative. D — negative lag is a genuine signal here, not a display artefact, and `isolation.level` affects the last stable offset, which can make lag look *larger*, not negative.
- 🧠 **Key point / trap:** `CURRENT-OFFSET > LOG-END-OFFSET` (negative lag) is the fingerprint of **log truncation**. After an unclean election, always reconcile downstream systems — Kafka cannot tell you what it lost.
- 📎 Source: `../../study-plan/week-02/resources/kafka-replication-isr.md` (`unclean.leader.election.enable`, truncation and data loss).

### Question 58 — Answer: **A, D**

- **Why correct:** A — with `enable.auto.commit=true` the offsets are committed by the poll loop at most every `auto.commit.interval.ms` (5,000 ms). Everything processed since the last automatic commit is re-delivered after the restart, which is the "last few seconds of work per pod" the team sees. D — handling `SIGTERM` by waking the poll loop and calling `consumer.close()` commits the current position (auto-commit consumers commit on close) and sends a `LeaveGroup`, so both the duplicates and the rebalance delay shrink; an explicit `commitSync()` before exit achieves the same.
- **Why the others are wrong:** B — turning auto-commit off without adding explicit commits makes things worse, not better: the broker never commits offsets on the client's behalf. C — `read_committed` filters records from **aborted transactions**; redelivered records were committed normally and remain fully visible. E — `max.poll.records=1` reduces the *window* of duplicates but guarantees nothing: the crash can still land between processing and the next automatic commit, and it destroys throughput.
- 🧠 **Key point / trap:** auto-commit plus a hard exit is at-least-once with a five-second blast radius. A graceful `close()` in the shutdown hook is the single highest-value line of code in a consumer.
- 📎 Source: `../../study-plan/week-04/resources/kafka-consumer-configs.md` (`enable.auto.commit` / `auto.commit.interval.ms` 5,000) and `../../study-plan/week-04/resources/kafka-consumer-javadoc.md`.

### Question 59 — Answer: **B**

- **Why correct:** `config.storage.topic`, `offset.storage.topic` and `status.storage.topic` hold the **entire durable state** of one Connect cluster: the set of connectors, their configurations, their task assignments and their source offsets. A worker reads every record in the config topic and treats it as its own desired state, so two clusters sharing those topics each try to run the other's connectors and each overwrite the other's configurations — producing exactly the flapping, reverting and re-ingesting described. A distinct `group.id` separates the rebalance groups but not the state, so each cluster needs its own three topics.
- **Why the others are wrong:** A — `connect.protocol` selects the rebalance protocol; it does not namespace records inside the internal topics. C — the config topic is the worst one to share, because it defines which connectors exist; sharing internal topics is never supported. D — the internal topics are read in full by every worker regardless of partitioning, and `connect-configs` must be a **single-partition** compacted topic precisely so that configuration ordering is total.
- 🧠 **Key point / trap:** "one Connect cluster = one `group.id` **and** one set of three internal topics". `connect-configs` 1 partition, `connect-offsets` 25, `connect-status` 5 — all compacted.
- 📎 Source: `../../study-plan/week-05/resources/connect-user-guide-configs-rest.md` (internal topics 1/25/5, compacted, per cluster).

### Question 60 — Answer: **D**

- **Why correct:** `offsets.topic.replication.factor` is consulted **only when `__consumer_offsets` is first created**. Created on a single-broker cluster, the topic got RF=1 and each of its 50 partitions has exactly one replica. Every consumer group is coordinated by the broker leading the `__consumer_offsets` partition chosen by `hash(group.id) % 50`, so restarting one of three brokers takes roughly a third of the groups' coordinators offline with no failover. The remedy is to raise the replication factor of the **existing** topic with `kafka-reassign-partitions.sh` (a JSON plan listing three replicas for each of the 50 partitions).
- **Why the others are wrong:** A — changing the broker property and restarting does nothing to an existing topic; Kafka never recreates `__consumer_offsets`. B — 50 partitions across 3 brokers is entirely normal and already spreads coordinators; partition count is not the issue, replica count is. C — `__consumer_offsets` is an ordinary replicated topic on the data plane; `__cluster_metadata` is the KRaft metadata log, and the two are unrelated.
- 🧠 **Key point / trap:** this trap follows every cluster that started as a one-broker sandbox. Audit the replication factor of `__consumer_offsets`, `__transaction_state` and the Connect internal topics after any cluster growth.
- 📎 Source: `../../study-plan/week-08/resources/kafka-basic-ops-reassignment.md` (raising RF with a reassignment plan) and `../../study-plan/week-04/resources/kafka-ops-consumer-groups-share-groups.md` (coordinator selection, 50 partitions).

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (48+/60) | Đạt ngưỡng cá nhân trên một mock full-length. | Review **100%** câu sai, viết phân tích 6 mục cho từng câu. Kiểm tra bảng domain: nếu có domain nào dưới ngưỡng riêng của nó thì vẫn phải ôn domain đó dù tổng đã đạt. Làm tiếp một mock full-length **khác** (mock-01 hoặc bộ thứ ba). Đủ **3 bộ khác nhau ≥ 80%** thì đặt lịch thi. |
| **70–79%** (42–47/60) | Gần đạt, còn lỗ hổng cục bộ. | Lấy **2 domain thấp nhất** trong bảng chấm điểm, dành **3 ngày** đọc lại đúng các tuần tương ứng ở bảng dưới + làm lại lab của tuần đó. Làm lại mock này sau 7 ngày (không nhìn đáp án trong thời gian đó), rồi mới sang mock khác. **Chưa đặt lịch thi.** |
| **< 70%** (≤ 41/60) | Chưa sẵn sàng. | **Van an toàn: lùi lịch thi ít nhất 2 tuần.** Quay lại học tuần tương ứng của 3 domain thấp nhất (Buổi A + B), làm mini-mock cuối mỗi tuần đạt ≥ 80% rồi mới thử full mock lần nữa. Nếu sai nhiều ở nhóm câu "đọc log/CLI/metric", ưu tiên **Tuần 8** trước tiên. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / dính bẫy version / hết giờ), và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may **cũng tính là câu sai**.
> 📌 Mock này cố ý nặng về **chẩn đoán**. Nếu bạn sai nhiều ở nhóm câu in log/CLI/metric nhưng lại làm tốt câu lý thuyết, vấn đề không phải kiến thức mà là **phản xạ đọc triệu chứng** — luyện bằng cách chạy lại lab Tuần 8 và tự gây lỗi rồi đọc metric.

---

## 🔁 Bản đồ câu sai → tuần cần học lại

| Chủ đề của câu sai | Câu số | Tuần cần học lại |
| --- | --- | --- |
| Replication, ISR, min.insync.replicas, unclean election | 1, 21, 57 | **Tuần 2** (+ Tuần 1 phần replication) |
| ELR (KIP-966) và ràng buộc `min.insync.replicas` cluster-level | 10, 54 | **Tuần 2** |
| Retention, timestamp, log/segment, message size | 40, 44, 50 | **Tuần 2** (+ Tuần 1 phần log) |
| KRaft, controller quorum, metadata, internal topics | 28, 47, 60 | **Tuần 1** (+ Tuần 8 phần reassignment) |
| Producer: buffer, batching, partitioner, message size, defaults đã đổi | 2, 8, 12, 45 | **Tuần 3** |
| Transactions & idempotence | 16 | **Tuần 3** |
| Consumer: liveness, commit, offset reset, bộ nhớ fetch | 5, 19, 42, 51, 58 | **Tuần 4** |
| Static membership & KIP-848 | 5, 36 | **Tuần 4** |
| Share groups (Queues for Kafka) | 14 | **Tuần 2** (+ Tuần 4 phần tooling) |
| Schema Registry: compatibility, wire format | 48 | **Tuần 5** |
| Connect: converter, SMT, DLQ, tasks, offsets, worker & internal topics | 3, 9, 15, 24, 30, 38, 52, 59 | **Tuần 5** |
| Connect exactly-once source (KIP-618) | 43 | **Tuần 5** |
| Kafka Streams: repartition, co-partition, cache, window, GlobalKTable, standby | 6, 18, 26, 31, 41, 53 | **Tuần 6** |
| Kafka Streams error handling & DLQ (KIP-1034) | 49 | **Tuần 6** |
| Security: TLS/SAN, SASL, ACL, quota | 23, 25, 33, 39 | **Tuần 7** |
| Testing: TopologyTestDriver, MockProducer, Testcontainers, CI | 13, 22, 32, 46, 56 | **Tuần 7** (+ Tuần 6 phần TTD) |
| Observability: metric client & broker, lag, CLI chẩn đoán | 4, 11, 17, 27, 34, 35, 37 | **Tuần 8** |
| Tiered storage | 37 | **Tuần 8** |
| MSK: port & authentication | 20 | **Tuần 9** |
| Exception → nguyên nhân (tổng hợp) | 55 | **Tuần 3 + 4 + 7** |

> 🔗 Sau khi ôn xong tuần tương ứng, làm lại **mini-mock cuối tuần đó** (file `questions.md` của tuần đó trong `../../study-plan/`) trước khi quay lại mock full-length.
