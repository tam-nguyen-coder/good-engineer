# 🎯 CCDAK Mock Exam 02 — 60 questions · 90 minutes

> **Exam-realistic full-length mock.** Distribution follows the official CCDAK domain weights.
> ⏱️ Set a timer for **90 minutes** (~90 seconds per question). No notes, no documentation, no pausing.
> 🔒 Answers, explanations and per-domain scoring: [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (4 options) · `Multi` (choose the stated number) · `Matching` · `Ordering`.
> Tag: `[Domain · Topic · Format]`. Domains: `DEV` `FUND` `CONNECT` `OBS` `STREAMS` `TEST`.
> Anchored to **Apache Kafka 4.3** — where a default changed in 3.0/4.0, the current value is correct.
> 🩺 **Theme of this mock: diagnosis and operations.** Most questions start from a symptom — a log line, an exception, a CLI output or a metric — and ask you to reason backwards to the cause and the fix.
> Back to [mock index](../README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

---

### Question 1 — `[FUND · Replication · Single]`

A broker hosting the leader of `ledger-7` logs the following repeatedly for two minutes:

```
[2026-09-18 02:14:07,338] ERROR [ReplicaManager broker=3] Error processing append operation on partition ledger-7
org.apache.kafka.common.errors.NotEnoughReplicasException: The size of the current ISR Set(3) is insufficient to satisfy the min.isr requirement of 2 for partition ledger-7
```

The topic has `replication.factor=3`; producers use the Kafka 4.3 defaults. During those two minutes the producer's `record-error-rate` stayed at **0** and then jumped, and no application code caught `NotEnoughReplicasException`. Which statement is the MOST accurate reading of this incident?

- A. The producer was configured with `acks=1`, which the broker upgraded to `acks=all` because `min.insync.replicas=2`; setting `acks=0` would make the writes succeed.
- B. Two of the three replicas left the ISR, so the leader rejected the appends. `NotEnoughReplicasException` is **retriable**, so the producer silently retried inside `delivery.timeout.ms` (120 s); only when that deadline passed did the callback fire, with a `TimeoutException`. The operator must restore a second replica to the ISR.
- C. `NotEnoughReplicasException` is fatal, so the producer aborted immediately; the absence of errors for two minutes proves the application swallowed the callback exception.
- D. The ISR shrank because `replica.lag.time.max.ms` is too high; lowering it from 30,000 ms would have kept the followers in the ISR.

### Question 2 — `[DEV · Producer buffering · Single]`

A service publishes to **14 different topics** through a single shared `KafkaProducer`. During an incident its JMX metrics show `buffer-available-bytes` ≈ 0, `waiting-threads` = 38 and `bufferpool-wait-ratio` ≈ 0.81, while `produce-throttle-time-avg` is **0** and `record-error-rate` is **0**. Per-broker, `request-latency-avg` is 6–9 ms for brokers 1, 2 and 4 but **4,200 ms for broker 3**. Threads publishing to topics whose leaders are *not* on broker 3 are blocked too. What explains the blast radius?

- A. Each topic gets its own `buffer.memory` allocation, so only the topics led by broker 3 should block; the cross-topic blocking proves the client has a deadlock bug and must be upgraded.
- B. `max.in.flight.requests.per.connection=5` is exhausted cluster-wide; setting it to 1 releases the accumulator and unblocks the other topics.
- C. `produce-throttle-time-avg=0` rules out a broker problem, so the cause is `linger.ms=5` holding batches; setting `linger.ms=0` frees the buffer.
- D. `buffer.memory` (32 MB) is a **single pool shared by every partition of every topic**; batches destined for the degraded broker cannot drain, so they consume the whole pool and `send()` blocks for any topic until `max.block.ms` (60 s) expires. Fix broker 3 — raising `buffer.memory` only delays the stall.

### Question 3 — `[CONNECT · Converters · Single]`

A distributed Connect cluster's `connect-distributed.properties` contains `value.converter=org.apache.kafka.connect.json.JsonConverter` and `value.converter.schemas.enable=true`. Five Avro sink connectors run happily (each sets its own `value.converter` in its connector config). A **new** Elasticsearch sink reading `orders` — plain JSON such as `{"id":42,"status":"PAID"}` written by a Node.js service — fails on startup:

```
org.apache.kafka.connect.errors.DataException: JsonConverter with schemas.enable requires "schema" and "payload" fields and may not contain additional fields. If you are trying to deserialize plain JSON data, set schemas.enable=false in your converter configuration.
```

Fix this connector **without editing the worker properties and without restarting any worker**. What do you do?

- A. `PUT /connectors/es-orders/config` adding `"value.converter": "org.apache.kafka.connect.json.JsonConverter"` and `"value.converter.schemas.enable": "false"` — connector-level converter settings override the worker defaults for this connector only.
- B. Set `value.converter.schemas.enable=false` in `connect-distributed.properties` and roll all three workers; the Avro connectors are unaffected because they override `value.converter`.
- C. Add `"errors.tolerance": "all"` and `"errors.deadletterqueue.topic.name": "dlq-es-orders"` so the bad records are skipped and indexing continues.
- D. Add `"schemas.enable": "false"` to the connector configuration — Connect applies unprefixed converter options to whichever converter is active.

### Question 4 — `[OBS · Consumer lag · Single]`

On-call is paged because `fraud-scoring` lag is climbing. They run:

```
$ kafka-consumer-groups.sh --bootstrap-server broker-1:9092 --describe --group fraud-scoring

GROUP          TOPIC      PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG      CONSUMER-ID  HOST  CLIENT-ID
fraud-scoring  txns       0          9812440         9903118         90678    -            -     -
fraud-scoring  txns       1          9811902         9902547         90645    -            -     -
fraud-scoring  txns       2          9812210         9903004         90794    -            -     -
```

What does this output prove?

- A. The group coordinator is unreachable, so the tool could not resolve member metadata; the lag figures are therefore unreliable.
- B. The consumers use static membership, which hides `CONSUMER-ID` from the describe output; the application is running normally and the lag is a reporting artefact.
- C. The group currently has **no active members** — the dashes in `CONSUMER-ID` / `HOST` / `CLIENT-ID` mean the partitions are unassigned, so the group is `Empty`. `LAG` is still computed from the last committed offsets against the log end offsets and will keep growing until a consumer rejoins.
- D. The consumers are alive but stuck inside `poll()` waiting on `fetch.max.wait.ms`, which blanks the member columns until the next fetch returns.

### Question 5 — `[DEV · Consumer group protocol · Single]`

A team migrated a consumer fleet to `group.protocol=consumer` (KIP-848) on Apache Kafka 4.3. Since the migration the application logs, every few minutes:

```
org.apache.kafka.clients.consumer.CommitFailedException: Offset commit cannot be completed since the consumer is not part of an active group for auto partition assignment; it is likely that the consumer was kicked out of the group.
```

To fix it an engineer raised the client property `session.timeout.ms` from 45000 to 120000 and redeployed. Nothing changed. Each `poll()` iteration calls a batch-scoring service that occasionally takes **6 minutes**. What is the MOST accurate diagnosis?

- A. `session.timeout.ms` may not exceed `group.max.session.timeout.ms`, so the broker silently rejected 120000 and reverted to 45000; raise the broker limit and the commits will succeed.
- B. KIP-848 removed `max.poll.interval.ms`; the only remaining liveness clock is the broker's `consumer.session.timeout.ms`, which an administrator must raise with `kafka-configs.sh --entity-type groups`.
- C. `CommitFailedException` under the new protocol always means the offsets topic is under-replicated; check `__consumer_offsets` before touching client configuration.
- D. Under `group.protocol=consumer` the client's `session.timeout.ms` and `heartbeat.interval.ms` are **ignored** (member liveness is owned by the broker's group configs), so the change was a no-op. The clock that actually evicts this member is `max.poll.interval.ms` (300,000 ms), which is still a client config — lower `max.poll.records` or raise `max.poll.interval.ms`.

### Question 6 — `[STREAMS · Repartitioning · Single]`

A Kafka Streams application was refactored so that a logging step could report the key of each record:

```java
builder.stream("payments", Consumed.with(Serdes.String(), paymentSerde))
       .selectKey((key, value) -> key)          // added for logging, key is unchanged
       .filter((key, value) -> value.amount() > 0)
       .groupByKey()
       .count()
       .toStream()
       .to("payment-counts");
```

After the release, an internal topic `pay-app-KSTREAM-KEY-SELECT-0000000001-repartition` appeared, end-to-end latency doubled and produce traffic to the cluster rose sharply. What is the cause, and what is the fix **with the fewest changes**?

- A. `filter()` between a key-changing operator and `groupByKey()` is what creates the repartition topic; move `filter()` before `selectKey()` to remove it.
- B. `selectKey()` sets the internal "key changing" flag regardless of what the lambda returns, so the following `groupByKey()` forces a repartition topic. Streams cannot know the lambda is a no-op — remove `selectKey()` and log inside `peek()` instead.
- C. `count()` always creates a repartition topic in addition to its changelog; use `reduce()` with an explicit `Materialized` store to avoid it.
- D. The repartition topic appears because `payments` and `payment-counts` have different partition counts; align them and the topic disappears.

### Question 7 — `[FUND · Rolling restart · Ordering]`

Put the steps of a safe rolling restart of **one** broker in a `replication.factor=3` / `min.insync.replicas=2` cluster into the order they must be performed.

| # | Step |
|---|---|
| 1 | Run `kafka-leader-election.sh --election-type PREFERRED --all-topic-partitions` so leadership returns to its preferred replicas |
| 2 | Confirm `UnderReplicatedPartitions = 0` and `OfflinePartitionsCount = 0` before touching the next broker |
| 3 | Stop the broker so that controlled shutdown migrates its partition leaderships to other in-sync replicas |
| 4 | Start the broker again and wait until its replicas have rejoined the ISR of every partition it hosts |

- A. 2 → 3 → 4 → 1
- B. 3 → 2 → 4 → 1
- C. 3 → 4 → 1 → 2
- D. 4 → 3 → 1 → 2

### Question 8 — `[DEV · Message size · Single]`

A Java producer fails on a subset of records:

```
org.apache.kafka.common.errors.RecordTooLargeException: The message is 3145770 bytes when serialized which is larger than 1048576, which is the value of the max.request.size configuration.
```

The platform team responded by raising the broker's `message.max.bytes` to 5,242,880 and performing a rolling restart. The error is unchanged. Why did the broker change have no effect, and what is the minimal correct fix?

- A. The exception is raised **client-side** before any request leaves the JVM — the message names `max.request.size`, a producer configuration (default 1,048,576). Raise `max.request.size` on the producer; the broker-side `message.max.bytes` increase is still needed, but on its own it can never be reached.
- B. The broker change needed `--entity-type topics`; setting `max.message.bytes` on the topic instead of `message.max.bytes` on the broker would have fixed it without touching the producer.
- C. `batch.size` (16,384) caps a single record, so the producer rejects anything larger; raise `batch.size` above the record size.
- D. The consumer's `max.partition.fetch.bytes` (1 MB) propagates back to the producer through metadata; raise it on every consumer of the topic.

### Question 9 — `[CONNECT · Converters, SMTs & serializers · Matching]`

Match each component to the job it performs.

| # | Component |
|---|---|
| 1 | `value.converter=io.confluent.connect.avro.AvroConverter` on a sink connector |
| 2 | `transforms.mask.type=org.apache.kafka.connect.transforms.MaskField$Value` |
| 3 | `value.serializer=io.confluent.kafka.serializers.KafkaAvroSerializer` in a plain `KafkaProducer` |
| 4 | `header.converter=org.apache.kafka.connect.storage.SimpleHeaderConverter` |

| Letter | Job |
|---|---|
| W | Converts each record **header** value between its Kafka byte form and Connect's internal representation |
| X | Reshapes the fields of a record **after** it has been turned into Connect's internal `Struct`, before it reaches the sink |
| Y | Converts the whole record **value** between Kafka bytes and Connect's internal data + schema representation |
| Z | Turns an application object into bytes inside an ordinary producer — no Connect framework involved |

- A. 1-X · 2-Y · 3-W · 4-Z
- B. 1-Y · 2-Z · 3-X · 4-W
- C. 1-W · 2-X · 3-Z · 4-Y
- D. 1-Y · 2-X · 3-Z · 4-W

### Question 10 — `[FUND · Eligible Leader Replicas · Single]`

On a Kafka 4.3 cluster created with default features, `unclean.leader.election.enable=false`:

```
$ kafka-topics.sh --bootstrap-server broker-1:9092 --describe --topic ledger

Topic: ledger  Partition: 4  Leader: none  Replicas: 5,6,7  Isr:   Elr: 6  LastKnownElr: 5
```

Broker **5** (the previous leader) is back online but was rebuilt with an empty log directory. Broker **6** is still down. Broker **7** is online and has been out of the ISR for an hour. What does the controller do?

- A. It elects broker **5**, the last known leader, because `LastKnownElr` names it and a returning last known leader always outranks ELR members.
- B. It keeps the partition offline until broker **6** returns, then elects 6 — 6 is in the ELR, so it holds every committed record and can lead with no data loss. Broker 5 lost its log directory and was therefore dropped from the ELR; broker 7 is in neither ISR nor ELR, so with unclean election disabled it cannot be elected.
- C. It elects broker **7** because it is the only online replica; ELR only ranks candidates and never blocks an election.
- D. It leaves the partition offline permanently — once `Isr` is empty the partition can only be recovered by setting `unclean.leader.election.enable=true`, exactly as before Kafka 4.0.

### Question 11 — `[OBS · Broker threads · Single]`

A broker on a 16-vCPU host is saturated. Its metrics:

- `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` = **0.24** (`num.io.threads` is already **32**)
- `kafka.network:type=RequestChannel,name=RequestQueueSize` growing
- `kafka.network:type=RequestMetrics,request=Produce`: `LocalTimeMs` ≈ **140 ms**, `RemoteTimeMs` ≈ 6 ms, `RequestQueueTimeMs` ≈ 2 ms
- disk utilisation ≈ 25 %, page cache healthy

The hottest topic was recently given `compression.type=gzip`; its producers send `compression.type=lz4`. Which change addresses the bottleneck?

- A. Set the topic's `compression.type` back to `producer`. Because the topic codec differs from the batch codec, the broker must decompress and re-compress every batch on the request-handler thread, which is exactly what `LocalTimeMs` measures.
- B. Raise `num.io.threads` from 32 to 64; `RequestHandlerAvgIdlePercent` below 0.3 always means too few io threads.
- C. Raise `num.network.threads` from 3 to 12; a growing `RequestQueueSize` is produced by the network layer, not the io pool.
- D. Lower `min.insync.replicas` to 1 so produce requests stop waiting for followers — `LocalTimeMs` includes follower acknowledgement time.

### Question 12 — `[DEV · Producer defaults · Single]`

An order service upgraded its `kafka-clients` dependency from 3.9.0 to 4.3.1. No application code and no producer property changed. After the deploy, p99 `send()`-to-ack latency rose from ~2 ms to ~8 ms, throughput per request improved, `batch-size-avg` grew from 900 B to 6.4 KB and `record-queue-time-avg` settled at about 5 ms. What happened, and what restores the old latency?

- A. `batch.size` changed its default from 16,384 to 65,536 in 4.0; set `batch.size=16384` explicitly.
- B. `acks` changed its default from `1` to `all` in 4.0, adding follower round-trip time; set `acks=1` to restore latency.
- C. `linger.ms` changed its default from **0 to 5** in Kafka 4.0 (KIP-1030), so batches now wait up to 5 ms in the accumulator. Set `linger.ms=0` explicitly to get the previous behaviour, accepting smaller batches.
- D. `enable.idempotence` became the default in 4.0 and adds a sequence-number round trip; set `enable.idempotence=false`.

### Question 13 — `[TEST · TopologyTestDriver · Single]`

A developer tests `groupByKey().count()` with `TopologyTestDriver`. Piping 5 records with the same key, the test reads **5** output records (1, 2, 3, 4, 5) from the `TestOutputTopic` and the assertions pass. In production, the same topology under steady load emits far fewer updates per key. Which statement explains the difference correctly?

- A. `TopologyTestDriver` does not support state stores, so it recomputes the count from scratch for each record; production numbers are the trustworthy ones.
- B. `TopologyTestDriver` flushes the record cache after every piped record, so every intermediate aggregation update is forwarded. In production `statestore.cache.max.bytes` (10 MB) and `commit.interval.ms` (30,000 ms) coalesce updates for the same key, so only the value at eviction or commit time is emitted. Both produce the same **final** value.
- C. Production uses `suppress(untilWindowCloses)` implicitly for all aggregations; the test driver does not, which is why it emits more records.
- D. The difference comes from `num.stream.threads` (1 in the test, higher in production): more threads means fewer emitted updates per key.

### Question 14 — `[FUND · Share groups · Multi — Choose 2]`

A team on Apache Kafka 4.3 moves a job-processing workload to a **share group**. Each job takes about **45 seconds** of processing before the worker calls `acknowledge(record, AcknowledgeType.ACCEPT)`. Operators observe that many jobs are executed **twice**, by two different workers, with no error in the logs. Which two statements are correct? (Choose two.)

- A. The acquisition lock defaults to **30 seconds** (`share.record.lock.duration.ms`), so the lock expires mid-processing and the record is released and re-delivered to another member before the first worker acknowledges it.
- B. `max.poll.interval.ms` governs share-group record locks exactly as it governs classic consumer groups; raising it to 600,000 ms is the supported fix.
- C. Raising the group config `share.record.lock.duration.ms` above the worst-case processing time — up to the broker's `group.share.max.record.lock.duration.ms` (60,000 ms) — or shortening the unit of work removes the duplicate deliveries.
- D. Share groups (KIP-932) are still early access in 4.3, so duplicate delivery is expected and the workload must move back to a classic consumer group for production.
- E. Acknowledging with `AcknowledgeType.REJECT` instead of `ACCEPT` would have prevented the second delivery while still marking the job successful.

### Question 15 — `[CONNECT · Dead letter queue · Multi — Choose 2]`

An S3 sink connector runs with `errors.tolerance=all` and `errors.deadletterqueue.topic.name=dlq-s3-orders`. Bad records do reach the DLQ, but the on-call engineer complains that (1) a DLQ record carries no indication of **which stage** failed or **which offset** it came from, and (2) the DLQ topic has a single partition while `orders` has 24, so replaying it is slow. Which two statements are correct? (Choose two.)

- A. Setting `errors.deadletterqueue.topic.partitions=24` on the connector makes Connect create the topic with matching parallelism.
- B. `errors.deadletterqueue.context.headers.enable` defaults to **false**; setting it to `true` adds `__connect.errors.*` headers carrying the original topic/partition/offset, the connector and task, the failing stage and the exception.
- C. The DLQ holds the record **after** the converter and transformation chain have run, which is why the original offset is unavailable without extra configuration.
- D. When the DLQ topic does not already exist, the worker's admin client creates it with **1 partition** (only the replication factor is configurable, through `errors.deadletterqueue.topic.replication.factor`); to get 24 partitions the topic must be pre-created manually.
- E. Switching to `errors.tolerance=none` preserves the error context because the task then fails with the full stack trace in the DLQ record.

### Question 16 — `[DEV · Transactions · Single]`

A payments service runs as a Kubernetes `Deployment` with `replicas=3`. All three pods read `TRANSACTIONAL_ID=payments-tx` from the same `ConfigMap`. Two of the three pods crash-loop with:

```
org.apache.kafka.common.errors.ProducerFencedException: There is a newer producer with the same transactionalId which fences the current one.
```

Exactly one pod makes progress at any moment, and which one it is keeps changing. What is happening and what is the correct fix?

- A. `ProducerFencedException` is retriable; wrap `commitTransaction()` in a retry loop and all three pods will make progress with the shared id.
- B. The broker's `transactional.id.expiration.ms` (7 days) is too long, so stale epochs survive; lowering it to 60,000 ms lets all three pods share the id safely.
- C. Generate a fresh random UUID as `transactional.id` in each pod on every start; unique ids per start are exactly what the transactional protocol expects.
- D. A `transactional.id` identifies **one** logical producer. Every `initTransactions()` bumps the epoch and fences all older producers with that id, so the three pods fence each other in turn. Give each instance a **stable, unique** id (for example a `StatefulSet` ordinal suffix, `payments-tx-0/1/2`) so zombie fencing protects restarts of the same instance instead of siblings.

### Question 17 — `[OBS · Lag diagnosis · Ordering]`

A consumer group's lag has been growing for an hour. Put the diagnostic steps in the order that gathers the cheapest, most decisive evidence first.

| # | Step |
|---|---|
| 1 | Compare `records-lag` **per partition** to decide whether every partition is behind or only one (a hot key / skewed partition) |
| 2 | Add consumer instances up to the partition count, and if that ceiling is already reached, add partitions |
| 3 | Run `kafka-consumer-groups.sh --describe --group g --members --verbose` to confirm the group has live members and that every partition is assigned |
| 4 | Read `time-between-poll-max` and `poll-idle-ratio-avg` to decide whether the application loop or the brokers are the bottleneck |

- A. 1 → 3 → 2 → 4
- B. 4 → 3 → 1 → 2
- C. 3 → 1 → 4 → 2
- D. 3 → 4 → 2 → 1

### Question 18 — `[STREAMS · Co-partitioning · Single]`

A Streams application joins `KStream<String, Order>` from `orders` with `KTable<String, Payment>` from `payments`. Both topics have **24 partitions** and both are keyed by `orderId` as a `String`. The application starts cleanly — no `TopologyException` — but roughly 60 % of joins emit `null` on the table side even though a matching payment exists in the topic. The `payments` topic is written by a legacy service configured with `partitioner.class=org.apache.kafka.clients.producer.RoundRobinPartitioner`. What is wrong?

- A. Co-partitioning requires the same partition count **and** the same key-to-partition mapping. Round-robin partitioning breaks the mapping, so a task owning partition *n* of `orders` looks up a table state store built from partition *n* of `payments`, which does not hold that key. Either remove the custom partitioner or re-key `payments` through a `repartition()` inside Streams.
- B. `KStream`-`KTable` joins require the table to be materialised with `Materialized.as(...)`; without it lookups return `null` for most keys.
- C. Streams validates partition counts at build time, so a clean start proves co-partitioning is satisfied; the nulls must come from a `Serde` mismatch on the value.
- D. The table side is empty until `max.task.idle.ms` elapses; raising it from the default to 30,000 ms removes the nulls.

### Question 19 — `[DEV · Offsets · Multi — Choose 2]`

A consumer group restarts after a 10-day outage and logs:

```
org.apache.kafka.clients.consumer.OffsetOutOfRangeException: Fetch position FetchPosition{offset=88214, offsetEpoch=Optional[7], currentLeader=...} is out of range for partition events-3
```

It then continues without crashing, and monitoring shows it consumed **0** of the ~4 million records that accumulated during the outage. The topic has `retention.ms=604800000` (7 days); the group's committed offsets are still present. Which two statements are correct? (Choose two.)

- A. Retention deleted the segments containing offset 88214, so the fetch position fell **below the partition's log start offset**; with the default `auto.offset.reset=latest` the consumer reset to the log end offset and skipped everything in between.
- B. `offsets.retention.minutes` (10,080 = 7 days) expired and deleted the group's committed offsets — that is what produced the exception.
- C. The group exceeded `max.poll.interval.ms` during the outage, so the coordinator rebalanced it and invalidated its positions.
- D. `records-lead-min` trending toward 0 is the metric that warns of this failure **before** it happens, because it measures the distance between the consumer's position and the log start offset.
- E. The topic is compacted, so the cleaner removed the record at offset 88214 and left a gap that the fetcher reports as out of range.

### Question 20 — `[FUND · MSK listeners · Matching]`

Match each Amazon MSK broker port to the authentication it serves for in-VPC clients.

| # | Port |
|---|---|
| 1 | 9092 |
| 2 | 9094 |
| 3 | 9096 |
| 4 | 9098 |

| Letter | Client configuration |
|---|---|
| W | `security.protocol=SASL_SSL` with `sasl.mechanism=SCRAM-SHA-512` and credentials in AWS Secrets Manager |
| X | `security.protocol=SASL_SSL` with `sasl.mechanism=AWS_MSK_IAM` and the `aws-msk-iam-auth` callback handler |
| Y | `security.protocol=PLAINTEXT` — no encryption, no authentication |
| Z | `security.protocol=SSL` — TLS encryption, optional mutual TLS, no SASL |

- A. 1-Y · 2-W · 3-Z · 4-X
- B. 1-Z · 2-Y · 3-X · 4-W
- C. 1-Y · 2-Z · 3-X · 4-W
- D. 1-Y · 2-Z · 3-W · 4-X

### Question 21 — `[OBS · ISR stability · Multi — Choose 2]`

Every broker in a 5-node cluster logs pairs of lines like these, several hundred times an hour, always naming broker 4:

```
[2026-09-19 11:02:31,740] INFO [Partition orders-11 broker=2] Shrinking ISR from 2,4,5 to 2,5. Leader: (highWatermark: 8812340, endOffset: 8812351). Out of sync replicas: (brokerId: 4, endOffset: 8809912)
[2026-09-19 11:02:58,113] INFO [Partition orders-11 broker=2] Expanding ISR from 2,5 to 2,5,4
```

Topics use `replication.factor=3` and `min.insync.replicas=2`; producers use `acks=all`. Which two statements are correct? (Choose two.)

- A. The flapping is caused by `acks=all` itself: each acknowledgement forces an ISR recomputation, so lowering producers to `acks=1` stops the churn.
- B. Raising `min.insync.replicas` to 3 pins broker 4 in the ISR and stops the shrink/expand cycle.
- C. Broker 4 repeatedly falls more than `replica.lag.time.max.ms` (30,000 ms) behind and then catches up — typical of a saturated disk or NIC, long GC pauses, or too few `num.replica.fetchers` on that broker.
- D. The `Shrinking ISR` lines indicate unclean leader elections are occurring; set `unclean.leader.election.enable=false` to stop them.
- E. While the ISR is `2,5` the partition still satisfies `min.insync.replicas=2`, so `acks=all` writes keep succeeding; durability is reduced to two copies but nothing fails yet.

### Question 22 — `[TEST · MockProducer · Multi — Choose 2]`

A service routes records whose `send()` fails with a `TimeoutException` to a local dead-letter path. The team wants a **unit test** for that path that runs in milliseconds with no broker. Which two statements about `org.apache.kafka.clients.producer.MockProducer` are correct? (Choose two.)

- A. `MockProducer` only simulates successful sends; error paths require `Testcontainers` with a real broker that is then stopped mid-test.
- B. Constructing it with `autoComplete=false` leaves each `send()` future pending until the test calls `completeNext()` (success) or `errorNext(new TimeoutException("simulated"))`, which completes the future **and** invokes the registered callback with that exception — exactly what the error path needs.
- C. `history()` returns every `ProducerRecord` passed to `send()` since the last `clear()`, whether or not its future has completed, so the test can assert the topic, key, value and headers of the record that was attempted.
- D. `MockProducer` lives in `kafka-streams-test-utils`, so the test module must add that dependency.
- E. `errorNext()` throws the supplied exception from `send()` itself, so the test asserts with `assertThrows(TimeoutException.class, () -> service.publish(...))`.

### Question 23 — `[DEV · ACLs · Single]`

A Kafka Streams application with `application.id=payments-app` is deployed to a cluster running `StandardAuthorizer` with `allow.everyone.if.no.acl.found=false`. Its principal `User:payments-app` was granted `Read` on `payments`, `Write` on `payment-counts` and `Read` on group `payments-app`. The application starts and immediately dies:

```
org.apache.kafka.common.errors.TopicAuthorizationException: Not authorized to access topics: [payments-app-counts-store-changelog]
```

What is the correct least-privilege fix?

- A. Grant `Read` on the `__consumer_offsets` topic; Streams stores changelog data there and the message names the state store only for readability.
- B. Streams creates and uses internal topics named `<application.id>-*` (changelog and repartition topics). Grant `Describe`, `Read`, `Write` — plus `Create` on the cluster, or pre-create the topics — on a **PREFIXED** resource pattern for `payments-app`.
- C. The changelog topic belongs to the internal Streams principal, so `User:payments-app` must be added to the broker's `super.users` list.
- D. Set `topology.optimization=all` so Streams reuses the input topic as the changelog and no internal topic — and therefore no extra ACL — is needed.

### Question 24 — `[CONNECT · SMT chain · Ordering]`

A Debezium PostgreSQL source connector must, for each change event: flatten the Debezium envelope so that downstream sees the row itself; mask the `cust_id` column; rename `cust_id` to `customerId`; and publish to topic `orders` instead of `pg1.public.orders`. Put the four transformations into the order they must appear in `transforms=`.

| # | Transformation |
|---|---|
| 1 | `org.apache.kafka.connect.transforms.RegexRouter` rewriting `pg1.public.orders` to `orders` |
| 2 | `io.debezium.transforms.ExtractNewRecordState` unwrapping the envelope to the `after` row |
| 3 | `org.apache.kafka.connect.transforms.ReplaceField$Value` renaming `cust_id` to `customerId` |
| 4 | `org.apache.kafka.connect.transforms.MaskField$Value` masking the field `cust_id` |

- A. 1 → 2 → 3 → 4
- B. 2 → 3 → 4 → 1
- C. 2 → 4 → 3 → 1
- D. 4 → 2 → 1 → 3

### Question 25 — `[DEV · SASL · Multi — Choose 2]`

A Connect worker is configured for `SASL_SSL` with `sasl.mechanism=SCRAM-SHA-512` and starts fine — it reaches the group, reads `connect-configs` and serves the REST API. Every connector, however, fails immediately:

```
org.apache.kafka.common.errors.UnsupportedSaslMechanismException: Client SASL mechanism 'GSSAPI' not enabled in the server, enabled mechanisms are [SCRAM-SHA-512]
```

Which two statements explain and fix this? (Choose two.)

- A. The unprefixed `sasl.*` / `security.protocol` worker properties configure only the worker's **own** clients; the producers and consumers that Connect creates for connectors are configured from the `producer.*` and `consumer.*` prefixed copies, which are missing here and fall back to the defaults (`GSSAPI`).
- B. Because the worker authenticated successfully, the connectors inherit its credentials automatically; the error can only mean the broker's `sasl.enabled.mechanisms` list was changed after the worker started.
- C. Per-connector overrides use `producer.override.*` / `consumer.override.*` and are allowed because `connector.client.config.override.policy` defaults to `All` since Kafka 3.0; setting it to `None` would be required first.
- D. `GSSAPI` appears because Connect always negotiates Kerberos first and downgrades; adding `sasl.enabled.mechanisms=GSSAPI,SCRAM-SHA-512` on the brokers is the supported fix.
- E. Duplicating the security settings as `producer.security.protocol=SASL_SSL`, `producer.sasl.mechanism=SCRAM-SHA-512`, `producer.sasl.jaas.config=...` (and the `consumer.` and `admin.` equivalents) in the worker properties fixes every connector at once.

### Question 26 — `[STREAMS · Record cache · Multi — Choose 2]`

A Streams application computes `groupByKey().count()` and writes to an output topic. Under production load, end-to-end latency is under 1 second. On a low-traffic tenant cluster — a few records per minute — the same application shows an end-to-end latency of almost exactly **30 seconds**, and the output topic receives records in bursts. Nothing is logged. Which two statements are correct? (Choose two.)

- A. Adding `suppress(Suppressed.untilWindowCloses(...))` is required to reduce the latency, because non-windowed aggregations otherwise buffer indefinitely.
- B. Updates sit in the state store's record cache until the cache evicts them (`statestore.cache.max.bytes`, default 10 MB) or the next commit flushes it; with little traffic the cache never fills, so the **commit** at `commit.interval.ms` (default 30,000 ms) is what releases the output.
- C. Enabling `processing.guarantee=exactly_once_v2` would make the latency worse, because EOS raises `commit.interval.ms` to 300,000 ms.
- D. The 30-second delay is the consumer's `fetch.max.wait.ms` accumulating across sub-topologies; raising `fetch.min.bytes` removes it.
- E. Setting `statestore.cache.max.bytes=0` makes every update forward immediately, trading downstream record volume and I/O for latency; lowering `commit.interval.ms` achieves the same effect more gently.

### Question 27 — `[OBS · Metric to configuration · Matching]`

Match each abnormal client metric to the configuration change that addresses its root cause.

| # | Abnormal metric |
|---|---|
| 1 | `records-lead-min` falling steadily toward 0 |
| 2 | `time-between-poll-max` ≈ 295,000 ms |
| 3 | `buffer-available-bytes` ≈ 0 with `waiting-threads` > 0 |
| 4 | `batch-size-avg` ≈ 300 B with a very high `request-rate` |

| Letter | Change |
|---|---|
| W | Raise `linger.ms` and `batch.size` so more records travel per request |
| X | Raise the topic's `retention.ms` (or add consumers) before the unread data is deleted |
| Y | Raise `buffer.memory` / `max.block.ms`, or remove whatever is preventing the sender from draining |
| Z | Lower `max.poll.records` or raise `max.poll.interval.ms` |

- A. 1-X · 2-Z · 3-Y · 4-W
- B. 1-Z · 2-X · 3-W · 4-Y
- C. 1-X · 2-Y · 3-Z · 4-W
- D. 1-W · 2-Z · 3-Y · 4-X

### Question 28 — `[FUND · KRaft · Multi — Choose 2]`

A Kafka 4.3 cluster has 6 brokers and a **3-node dedicated controller quorum**. Two controllers are lost in a rack failure. On the surviving controller, `kafka-metadata-quorum.sh --describe --status` reports `LeaderId: -1`, and `ActiveControllerCount` is 0 everywhere. Which two statements describe the cluster's behaviour? (Choose two.)

- A. All produce requests are rejected immediately with `NotControllerException` until a controller quorum is restored.
- B. Any broker can be promoted to controller automatically, because in KRaft every broker is a latent voter.
- C. With only 1 of 3 voters alive the quorum has no majority, so no metadata record can be committed: topic creation, ACL changes, partition reassignment and **leader elections** all stop.
- D. Brokers keep serving produce and fetch requests for partitions whose leaders are still alive, using the metadata they had already replicated; any broker failure from now on leaves its partitions without a new leader.
- E. Editing `controller.quorum.voters` on the surviving controller to list only itself restores the quorum without a restart.

### Question 29 — `[FUND · Topic configuration · Single]`

Writes to `orders` with `acks=all` kept succeeding while only one replica was in the ISR, even though the team is certain they set `min.insync.replicas=2` on the topic weeks ago. An engineer runs:

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --describe --all --entity-type topics --entity-name orders | grep min.insync

  min.insync.replicas=1 sensitive=false synonyms={STATIC_BROKER_CONFIG:min.insync.replicas=1, DEFAULT_CONFIG:min.insync.replicas=1}
```

What does this output tell them?

- A. The topic override exists but is masked because `STATIC_BROKER_CONFIG` outranks `DYNAMIC_TOPIC_CONFIG`; remove the static value from `server.properties` to let the topic setting take effect.
- B. No `DYNAMIC_TOPIC_CONFIG` entry appears, so the topic-level override does not exist — the effective value comes from the broker's `server.properties`. The earlier `--alter` must have targeted a different entity (another topic, or `--entity-type brokers`) or was later deleted. Re-apply it with `--entity-type topics --entity-name orders`.
- C. `--describe --all` prints broker defaults only; the topic override is invisible here and the real problem must lie in the producer's `acks` setting.
- D. The synonyms list proves `min.insync.replicas` cannot be set per topic in Kafka 4.x; it is a cluster-level setting only.

### Question 30 — `[CONNECT · Source offsets · Single]`

A JDBC source connector named `jdbc-orders` had ingested 40 million rows. To make it "start clean" after a schema change, an operator deleted it and created a connector named `jdbc-orders-v2` with an otherwise identical configuration. The whole table was re-ingested and every downstream consumer saw duplicates. What happened, and what is the supported way to reset a source connector's position?

- A. `DELETE /connectors/jdbc-orders` also deleted its offsets, so any replacement connector would have re-ingested regardless of its name; the only workaround is a new `offset.storage.topic` per connector.
- B. Source connectors store their position in `__consumer_offsets` under a group named after the connector; reset it with `kafka-consumer-groups.sh --reset-offsets --group connect-jdbc-orders-v2`.
- C. `connect-offsets` is compacted with a 24-hour `delete.retention.ms`, so the offsets had already expired; raising that value would have preserved them across the rename.
- D. Source offsets live in the `connect-offsets` topic keyed by **connector name** plus the connector-defined source partition, so a new name means a new key and no stored position. To reset deliberately, `PUT /connectors/{name}/stop`, then `DELETE /connectors/{name}/offsets` (or `PATCH` to a chosen position), then resume.

### Question 31 — `[STREAMS · Standby replicas · Single]`

A stateful Streams application holds ~30 GB of state per instance and runs with `num.standby.replicas=1`. Failover of a single crashed instance is fast, as expected. But when the team scales from 3 to **8** instances to absorb Black Friday traffic, the five new instances sit almost idle for close to an hour before they start taking meaningful work, even though the cluster is not CPU-bound. What explains the slow ramp-up?

- A. Streams does not hand an active stateful task to an instance until a **warm-up replica** on that instance has caught up to within `acceptable.recovery.lag` (10,000 records). Only `max.warmup.replicas` (default **2**) warm-ups run at a time, and the follow-up assignment happens on a probing rebalance every `probing.rebalance.interval.ms` (default **600,000 ms**). Raising both shortens the ramp-up at the cost of extra restore traffic.
- B. New instances must first be added to `group.instance.id` static membership before they receive tasks; without it they are treated as transient members and stay unassigned.
- C. The task count is fixed at startup by the first instance to join, so scaling out only takes effect after a full application restart.
- D. `num.standby.replicas=1` caps the group at 2 × the original instance count, so five of the eight instances are structurally idle; set it to 0 to use them.

### Question 32 — `[TEST · Schema Registry testing · Single]`

A team has two testing needs. (1) Thousands of fast unit tests must serialize and deserialize Avro records through `KafkaAvroSerializer` without any network call. (2) One nightly suite must prove that the **real** Schema Registry rejects an incompatible schema under the subject's configured compatibility level. Which combination is correct?

- A. (1) Use `TopologyTestDriver`, which ships its own in-memory Schema Registry. (2) Use `MockSchemaRegistryClient`, which enforces the same compatibility rules as the real server.
- B. (1) Point the unit tests at a shared development Schema Registry with `auto.register.schemas=false`. (2) Use `TopologyTestDriver`, the only tool that can evaluate compatibility levels.
- C. (1) Configure the serializer with the pseudo-URL `schema.registry.url=mock://my-scope`, which wires in `MockSchemaRegistryClient` — an in-memory registry with no HTTP at all. (2) Use Testcontainers to start a real Schema Registry (and broker) and assert the registration failure.
- D. (1) Use `MockProducer`, which bypasses serializers entirely. (2) Use `EmbeddedKafkaCluster`, which includes a Schema Registry by default.

### Question 33 — `[DEV · TLS · Single]`

Producers connecting to `broker-3.internal:9095` began failing after a certificate rotation:

```
javax.net.ssl.SSLHandshakeException: No subject alternative names matching IP address 10.0.4.21 found
```

The on-call engineer restored service by adding `ssl.endpoint.identification.algorithm=` (empty) to every client and the incident was closed. What is the consequence of that change, and what is the correct fix?

- A. The property only controls whether the client logs a warning; encryption and authentication are unaffected, so the change is safe to keep permanently.
- B. It switches the client from one-way TLS to mutual TLS, which is stronger; the SAN mismatch disappears because the client certificate is now used for identity.
- C. It disables certificate-chain validation entirely, so the correct fix is to import the broker certificate into every client truststore and leave the property empty.
- D. Setting the property to an empty string **disables hostname verification**, so a client will now accept any certificate that chains to a trusted CA — including one presented by a man-in-the-middle on the path. The correct fix is to re-issue the broker certificate with a Subject Alternative Name covering the address clients actually use (and to have clients connect by that name), then restore the default `https`.

### Question 34 — `[OBS · Partition reassignment · Single]`

An operator started a reassignment during business hours:

```
$ kafka-reassign-partitions.sh --bootstrap-server broker-1:9092 --execute \
    --reassignment-json-file move.json --throttle 10000000
The inter-broker throttle limit was set to 10000000 B/s
```

Two hours later, `--verify` still prints:

```
Status of partition reassignment:
Reassignment of partition [orders,3] is completed.
Reassignment of partition [orders,7] is still in progress.
```

`orders` sustains about 45 MB/s of incoming writes. What is happening, and what is the correct next step?

- A. `--verify` only reports partitions from the most recent `--execute`, so `[orders,7]` is stale output; re-run `--execute` with the same file to refresh it.
- B. The throttle (10 MB/s) is below the topic's incoming write rate, so the destination replica can never catch up — `max(BytesInPerSec) > throttle` means the reassignment never finishes. Re-run with `--additional --execute --throttle <higher value>` on the same JSON file and watch `kafka.server:type=FetcherLagMetrics,name=ConsumerLag` fall.
- C. The throttles were already cleared when `[orders,3]` completed, so replication is now unthrottled and `[orders,7]` is simply large; no action is needed.
- D. `--verify` cannot complete while producers are writing; pause the producers, run `--verify` again and the reassignment will finish.

### Question 35 — `[OBS · Partition reassignment · Ordering]`

Two brokers were added to a cluster and hold no partitions. Put the steps of moving existing partitions onto them in the correct order.

| # | Step |
|---|---|
| 1 | Run with `--verify` and the same JSON file to confirm completion and let the tool clear the broker-level and topic-level throttles |
| 2 | Run with `--generate`, `--topics-to-move-json-file` and `--broker-list`, saving the printed **current** assignment for rollback |
| 3 | Watch `kafka.server:type=FetcherLagMetrics,name=ConsumerLag` on the destination brokers decrease toward 0 |
| 4 | Run with `--execute`, the proposed reassignment JSON file and `--throttle` |

- A. 4 → 2 → 1 → 3
- B. 2 → 1 → 4 → 3
- C. 2 → 4 → 3 → 1
- D. 4 → 3 → 2 → 1

### Question 36 — `[DEV · Static membership · Single]`

A consumer group of 6 pods uses static membership. The `group.instance.id` is set from a Helm value that was accidentally hard-coded, so all six pods report the same id. Five pods crash-loop with:

```
org.apache.kafka.common.errors.FencedInstanceIdException: The broker rejected this static consumer since another consumer with the same group.instance.id has registered with a different member.id.
```

Only one pod consumes, and lag on the other partitions grows without bound. What is the correct fix?

- A. `group.instance.id` must be **unique per instance and stable across restarts** — that is the whole point of static membership. Derive it from a per-pod identity (a `StatefulSet` ordinal, or the pod name via the downward API), so each of the six pods registers as a distinct static member.
- B. Remove `group.instance.id` from all pods; `FencedInstanceIdException` only occurs with static membership and dynamic membership is always safe for Kubernetes.
- C. Raise `session.timeout.ms` above the pod restart time; the exception is a symptom of the coordinator expiring the shared member before the replacement registers.
- D. Set `group.protocol=consumer`; KIP-848 replaces `group.instance.id` with `group.remote.assignor`, so the collision cannot occur.

### Question 37 — `[OBS · Tiered storage · Single]`

A topic on a Kafka 4.3 cluster runs with `remote.storage.enable=true`, `local.retention.ms=3600000` (1 hour) and `retention.ms=7776000000` (90 days). After a long consumer outage the group restarts and the team observes: `records-lag-max` ≈ 120 million, `records-lead-min` ≈ **0**, `fetch-latency-avg` up from 4 ms to about 900 ms, and broker `RemoteTimeMs` for `FetchConsumer` elevated. Throughput per consumer is a fraction of normal, but nothing errors. What is the correct interpretation?

- A. `records-lead-min` at 0 means the data has already been deleted; the group will start throwing `OffsetOutOfRangeException` and must be reset with `--to-earliest`.
- B. The consumers have fallen behind the **local** retention window, so their fetches are served from remote (tiered) object storage instead of the page cache. Nothing is lost — `retention.ms` still protects 90 days — but catch-up reads are far slower; scale consumers out and expect degraded throughput until the group re-enters the local window.
- C. The fetch latency comes from `fetch.max.wait.ms` (500 ms) because the consumers are now reading with `fetch.min.bytes` too high; lower it to 1 to restore throughput.
- D. Tiered storage does not serve consumer fetches — only replica fetches — so the latency must come from an under-replicated partition; check `UnderReplicatedPartitions`.

### Question 38 — `[CONNECT · Tasks · Single]`

An S3 sink connector reads topic `events` (4 partitions) and is configured with `tasks.max=12` on a 3-worker Connect cluster. `GET /connectors/s3-events/status` shows **12 tasks, all `RUNNING`**, spread over the three workers. Throughput is unchanged from when `tasks.max` was 4, and the per-task metric `sink-record-read-rate` is 0 for eight of them. What is the correct explanation and the change that actually raises throughput?

- A. Eight tasks failed to acquire an S3 multipart upload slot; raise `s3.part.size` so all twelve can write concurrently.
- B. The Connect rebalance has not completed; issue `POST /connectors/s3-events/restart?includeTasks=true` and the idle tasks will pick up partitions.
- C. `tasks.max` is a per-worker limit, so 12 means 12 per worker (36 total); lower it to 2 so the assignment can balance across partitions.
- D. All tasks of a sink connector are members of **one consumer group** subscribed to `events`; with 4 partitions only 4 tasks can receive an assignment and the other 8 idle. Increase the partition count of `events` (and only then raise `tasks.max` to match).

### Question 39 — `[DEV · Quotas · Single]`

A reporting consumer suddenly slows down. Its metrics show `fetch-throttle-time-avg` ≈ 780 ms while `bytes-consumed-rate` is only ~3 MB/s. `kafka-configs.sh --describe --entity-type users --entity-name analytics-svc` prints `request_percentage=200` and **no** `consumer_byte_rate`. On the brokers, the byte-rate recorded for this user's fetches is far below any configured bandwidth limit, but throttle time is accumulating against its **request** quota. The consumer runs with `fetch.min.bytes=1` and `fetch.max.wait.ms=10`. What is the MOST likely cause and fix?

- A. The client is being throttled by the **request-rate quota** (a percentage of request-handler and network thread time, not bandwidth). Thousands of near-empty fetches per second burn that budget. Raise `fetch.min.bytes` and `fetch.max.wait.ms` so each fetch returns useful work, or raise `request_percentage`.
- B. `consumer_byte_rate` is unset, which means a default of 0 B/s, so every fetch is throttled; set an explicit `consumer_byte_rate` for the user.
- C. `fetch-throttle-time-avg` only reports bandwidth throttling, so the metric contradicts the quota configuration and must be a client bug; upgrade `kafka-clients`.
- D. `request_percentage=200` means 200 % of total broker CPU, which is invalid and disables the quota; the throttling must come from `max.partition.fetch.bytes` being too small.

### Question 40 — `[FUND · Timestamps & retention · Multi — Choose 2]`

Records written to `device-telemetry` disappear within minutes even though the topic has `retention.ms=604800000` (7 days). The topic uses the default `message.timestamp.type`. A firmware bug makes one fleet of devices stamp records with **seconds** since the epoch rather than milliseconds, so their timestamps resolve to early 1970. Which two statements are correct? (Choose two.)

- A. With `message.timestamp.type=CreateTime` (the default) retention is evaluated against the **producer's** timestamp, so a segment whose maximum timestamp is in 1970 becomes eligible for deletion as soon as it rolls.
- B. Setting the topic to `message.timestamp.type=LogAppendTime` makes the broker overwrite every record timestamp at append time, which makes retention immune to client clock bugs — at the cost of losing true event time for downstream stream processing.
- C. Lowering `log.retention.check.interval.ms` prevents the premature deletion because the cleaner will notice the anomaly before acting on it.
- D. `message.timestamp.before.max.ms` defaults to 1 hour, so the broker already rejected these records and the data loss must have another cause.
- E. Compacting the topic (`cleanup.policy=compact`) protects records with old timestamps, because compaction ignores timestamps entirely.

### Question 41 — `[STREAMS · Windowing · Single]`

A dashboard fed by a Streams application reports the count of failed logins per user per **1-minute** window. Operators complain that the number for a window that closed at 09:00 keeps changing for the rest of the day and only settles the next morning. The topology, ported from an older codebase, contains:

```java
.groupByKey()
.windowedBy(TimeWindows.of(Duration.ofMinutes(1)))
.count()
```

What is the cause, and what is the correct modern form?

- A. Tumbling windows never close; only session windows do. Switch to `SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(1))`.
- B. The state store's retention is 24 hours by default and republishes every window at the retention boundary; set `Materialized.withRetention(Duration.ofMinutes(1))`.
- C. The legacy `TimeWindows.of(size)` factory applies a **default grace period of 24 hours**, so late records keep updating a closed window for a full day. Replace it with `TimeWindows.ofSizeAndGrace(Duration.ofMinutes(1), Duration.ofSeconds(30))` — the current API forces an explicit grace choice — and add `suppress(Suppressed.untilWindowCloses(...))` if exactly one final result per window is required.
- D. The dashboard is reading a changelog topic rather than the output topic; point it at the output topic and the updates stop.

### Question 42 — `[DEV · Consumer memory · Single]`

A consumer subscribed to a 60-partition topic runs with `max.poll.records=100` in a container limited to 1 GB of heap. It dies with `OutOfMemoryError` during traffic spikes. A developer argues that `max.poll.records=100` makes large memory use impossible. Why is that reasoning wrong, and which settings actually bound the consumer's fetch memory?

- A. `max.poll.records` bounds memory correctly; the `OutOfMemoryError` must come from the producer side of the same JVM.
- B. `fetch.min.bytes` (1) is the true memory bound and must be raised so the broker sends fewer, smaller responses.
- C. Memory is bounded by `receive.buffer.bytes` (64 KB); the leak must be in application code because Kafka cannot buffer more than that.
- D. `max.poll.records` only limits how many records `poll()` hands the application from an **already fetched** internal buffer. The fetch itself is bounded by `fetch.max.bytes` (50 MB across the response) and `max.partition.fetch.bytes` (1 MB **per partition**) — with 60 assigned partitions that is up to ~60 MB of uncompressed records in flight, plus decompression overhead. Lower `max.partition.fetch.bytes` and `fetch.max.bytes`, or spread the partitions over more instances.

### Question 43 — `[CONNECT · Exactly-once source · Multi — Choose 2]`

A 4-worker distributed Connect cluster must move its source connectors from at-least-once to exactly-once delivery. Which two statements about enabling it are correct? (Choose two.)

- A. Exactly-once source support also works in standalone mode, provided the worker sets `offset.storage.file.filename` to a durable path.
- B. Setting `exactly.once.support=required` on a connector is what enables EOS for the cluster; the worker property is only a fallback.
- C. Downstream consumers need no change, because Connect's transactional producer marks aborted batches so that `read_uncommitted` consumers skip them automatically.
- D. `exactly.once.source.support` is a **worker** property with values `disabled` (default) → `preparing` → `enabled`; the upgrade is a two-pass rolling restart — set every worker to `preparing` first, then every worker to `enabled`. Going straight from `disabled` to `enabled` on a live cluster is not supported.
- E. With EOS enabled the worker writes each `SourceTask.poll()` batch and its source offsets in **one producer transaction**; `transaction.boundary` defaults to `poll` and can be changed to `interval` or `connector`.

### Question 44 — `[FUND · Retention · Single]`

To cap disk usage, an operator sets `retention.bytes=10737418240` (10 GiB) on topic `clickstream`, expecting the topic to stop growing past 10 GiB. Weeks later the topic occupies about 240 GiB on disk and is still growing. The topic has **24 partitions** and `replication.factor=3`; `retention.ms` is the 7-day default. What is the explanation?

- A. `retention.bytes` is only honoured when `cleanup.policy=compact,delete`; with the default `delete` policy, only `retention.ms` applies.
- B. `retention.bytes` is applied **per partition**, not per topic: 24 partitions × 10 GiB = 240 GiB of log per replica set, which is exactly what they observe. To cap the topic at 10 GiB, divide by the partition count (and remember replication multiplies the cluster-wide footprint by 3).
- C. `retention.bytes` counts uncompressed bytes while the disk stores compressed segments, so the on-disk figure is unrelated to the setting.
- D. `retention.bytes` is a broker-level setting that cannot be overridden per topic; the value was silently ignored.

### Question 45 — `[DEV · Partitioner · Single]`

A producer sends **null-keyed** telemetry to a 12-partition topic. A dashboard shows that, during a period when broker 2 had elevated `request-latency-avg`, the partitions led by broker 2 received roughly 40 % fewer records than the others, and `batch-size-avg` rose on the remaining partitions. The team opens a bug report claiming the partitioner is broken. What is the correct explanation?

- A. This is the intended behaviour of the default partitioner. For null keys it batches stickily per partition and, with `partitioner.adaptive.partitioning.enable=true`, it biases new batches **toward faster brokers** based on observed latency. Records with keys are unaffected — their partition is still `murmur2(key) % numPartitions`.
- B. The sticky partitioner distributes strictly round-robin per batch, so an imbalance of 40 % can only come from a custom `partitioner.class`; inspect the producer configuration.
- C. The imbalance proves broker 2 was rejecting produce requests; the missing records were silently dropped and must be replayed.
- D. Null-keyed records always go to partition 0 unless `partitioner.ignore.keys=true` is set; the skew is a symptom of that setting being toggled at runtime.

### Question 46 — `[TEST · Testcontainers · Single]`

An integration suite of 18 JUnit 5 test classes uses Testcontainers with a Kafka container. Each class is annotated `@Testcontainers` with an **instance** `@Container` field, and the suite takes 9 minutes in CI — almost all of it container start-up. The tests themselves are fast and none of them needs a pristine broker, only isolation from each other's data. What is the most effective change?

- A. Replace Testcontainers with `TopologyTestDriver` in all 18 classes; it is the supported way to run integration tests against real broker behaviour.
- B. Keep one container per class but set `testcontainers.reuse.enable=true` in `~/.testcontainers.properties`; reuse is designed for ephemeral CI runners and removes the start-up cost there.
- C. Start **one** broker container for the whole suite — a `static @Container` field in a shared base class (or a manually managed singleton started once in a static initialiser) — and isolate tests by generating a unique topic name and `group.id` per test.
- D. Run the 18 classes in parallel with a container each; total wall-clock time drops even though total start-up cost is unchanged, and this is preferable to sharing state.

### Question 47 — `[FUND · Metadata · Single]`

A new service connects to an Amazon MSK cluster successfully (the bootstrap handshake and SASL authentication both succeed, visible in the broker logs), but every `send()` fails after exactly 60 seconds:

```
org.apache.kafka.common.errors.TimeoutException: Topic orders-eu not present in metadata after 60000 ms.
```

The cluster runs with `auto.create.topics.enable=false`. Which statement is consistent with this exact message, and what does the 60 seconds correspond to?

- A. The 60 seconds is `request.timeout.ms` (30,000 ms) applied twice; the only possible cause is a broken `advertised.listeners` configuration on the brokers.
- B. Either the topic genuinely does not exist, or the principal lacks `Describe` on it — an unauthorised client is told nothing, so the topic simply never appears in the metadata response. The 60 seconds is `max.block.ms` (default 60,000 ms), which bounds how long `send()` waits for metadata.
- C. `auto.create.topics.enable=false` makes the producer throw `UnknownTopicOrPartitionException`, so this message must instead indicate a DNS failure resolving the bootstrap servers.
- D. The 60 seconds is `delivery.timeout.ms` (120,000 ms) halved by the retry backoff; create the topic and also raise `metadata.max.age.ms`.

### Question 48 — `[DEV · Schema Registry · Multi — Choose 2]`

A CI deploy fails when the producer starts:

```
io.confluent.kafka.schemaregistry.client.rest.exceptions.RestClientException: Schema being registered is incompatible with an earlier schema for subject "orders-value"; error code: 409
```

The change added a required field `channel` (type `string`, no default) to the Avro record. The subject uses the registry's default compatibility level. Which two statements are correct? (Choose two.)

- A. The default compatibility level is `BACKWARD`: a consumer using the **new** schema must be able to read data written with the **old** one. A newly added field without a default breaks that, because old records carry no value for it — giving `channel` a default (for example `"web"`) makes the change compatible.
- B. HTTP 409 means the schema is byte-identical to an existing version; re-registering the same schema under a new subject resolves it.
- C. The same change would be accepted under `FORWARD` compatibility, which is the correct level when producers are upgraded before consumers; switching the subject's level is a deliberate, documented decision rather than a workaround.
- D. Setting `auto.register.schemas=false` on the producer would have let the deploy succeed, because the incompatible schema would simply not be registered.
- E. Compatibility is evaluated across every version ever registered for the subject regardless of level, so no change to a required field can ever be accepted.

### Question 49 — `[STREAMS · Error handling · Multi — Choose 2]`

One malformed record on partition 7 makes a Kafka Streams 4.3 application shut down the whole instance with a `StreamsException` wrapping a deserialization error. The team needs the application to keep running **and** to keep the bad record for later analysis. Which two configurations achieve that? (Choose two.)

- A. Set `errors.tolerance=all` and `errors.deadletterqueue.topic.name`, exactly as for a Connect sink connector — Streams reuses the Connect error-handling framework.
- B. Set `default.deserialization.exception.handler` to `LogAndContinueExceptionHandler`, which logs the failure and skips the record so the task keeps processing.
- C. The default handler is `LogAndFailExceptionHandler`, but it can be kept as-is because Streams retries a failed deserialization up to `retries` times before shutting down.
- D. Set `errors.deadletterqueue.topic.name` (Kafka Streams DLQ, KIP-1034, available from 4.2): with the `LogAndContinue*` handlers in place, failing records are forwarded to that topic with `__streams.errors.*` headers instead of being silently dropped. The application must create and own the DLQ topic.
- E. Set `processing.guarantee=exactly_once_v2`, which routes records that fail deserialization into the aborted transaction and therefore out of the way.

### Question 50 — `[FUND · Message size · Single]`

To "make the broker match the producer", an operator set `max.message.bytes=1048576` on topic `audit` (the broker default is 1,048,588). Producers send 200 KB records with `compression.type=none`, `batch.size=1048576` and `linger.ms=50`. Individual records are well under the limit, yet the producer now intermittently receives:

```
org.apache.kafka.common.errors.RecordTooLargeException: The request included a message larger than the max message size the server will accept.
```

Why?

- A. `max.message.bytes` is measured before compression on the producer and after compression on the broker, so the two can never agree; the setting must always be left at its default.
- B. Setting `max.message.bytes` on a topic also lowers `replica.fetch.max.bytes` for that topic, and followers reject the batch first; raise `replica.fetch.max.bytes` instead.
- C. 1,048,576 is below the minimum allowed value for `max.message.bytes`, so the broker silently reverted the topic to 0 and rejects everything above the header size.
- D. On the broker the limit is applied to the whole **record batch** as it arrives (after compression), not to individual records. Five 200 KB records accumulated by `batch.size`/`linger.ms` form a batch above 1,048,576 bytes and are rejected. Raise `max.message.bytes`, lower `batch.size`, or enable compression — the odd default of 1,048,588 exists precisely to leave room for batch overhead.

### Question 51 — `[DEV · Consumer liveness · Single]`

A team deployed a consumer group on Kafka 4.3 using a `consumer.properties` copied from a 2019 runbook, which contains `session.timeout.ms=10000` and `heartbeat.interval.ms=3000`. Pods take about 20 seconds to restart during a rolling deploy, and every deploy now produces a storm of rebalances and several minutes of stalled consumption. Processing per batch is fast (well under a second). What is the MOST accurate diagnosis?

- A. `heartbeat.interval.ms=3000` is too low for Kafka 4.3, where the default is 15,000 ms; heartbeat flooding is what triggers the rebalances.
- B. `session.timeout.ms` has no effect since Kafka 4.0 because all groups use KIP-848 by default; the rebalances must come from `max.poll.interval.ms`.
- C. The runbook pinned the **pre-3.0** default. Since Kafka 3.0 (KIP-735) `session.timeout.ms` defaults to **45,000 ms**, comfortably longer than a 20-second restart; at 10,000 ms the coordinator declares each restarting pod dead and rebalances. Remove the override (or set it to 45000) and, for rolling deploys, combine it with static membership.
- D. `session.timeout.ms=10000` is still the Kafka 4.3 default and therefore cannot be the cause; the rebalances come from `group.initial.rebalance.delay.ms` (3,000 ms).

### Question 52 — `[CONNECT · Worker rebalance · Single]`

A Connect worker is terminated by the cloud provider during a node rotation. `GET /connectors/es-orders/status` immediately shows two of its tasks in state `UNASSIGNED`, and they stay that way for about five minutes before restarting on the surviving workers. Nothing is logged as an error. Operators want to know whether this is a bug.

- A. It is intended behaviour. Connect uses incremental cooperative rebalancing (KIP-415) and deliberately holds a departed worker's connectors and tasks for up to `scheduled.rebalance.max.delay.ms` (default **300,000 ms**) so that a briefly restarting worker can reclaim them without a second reassignment. Lower it to trade faster failover for more rebalance churn.
- B. It is a bug fixed in Kafka 4.2; tasks of a dead worker should be reassigned on the next heartbeat. Upgrade the cluster.
- C. `UNASSIGNED` means the tasks failed; `POST /connectors/es-orders/restart?includeTasks=true&onlyFailed=true` is required after every worker loss.
- D. The delay is `session.timeout.ms` inherited from the worker's consumer configuration; raise `connect.protocol` to `sessioned` to eliminate it.

### Question 53 — `[STREAMS · GlobalKTable · Single]`

An enrichment topology joins a high-volume `orders` stream against a `products` `GlobalKTable`. A product's price is updated at 10:00:00.000 and an order referencing it is produced at 10:00:00.400. The joined output carries the **old** price. Both topics are healthy and the Streams instance is not lagging. Which statement is correct?

- A. `GlobalKTable` updates are applied only at `commit.interval.ms` boundaries; lowering it to 100 ms makes the join deterministic.
- B. The join is driven by table-side records, so the order was processed before the price update arrived; swapping the join sides fixes the ordering.
- C. `max.task.idle.ms` controls this and defaults to 0; raising it to 500 ms makes Streams wait for the `GlobalKTable` to catch up.
- D. A `GlobalKTable` is maintained by a separate global consumer thread that is **not** time-synchronised with the stream tasks, so a stream record may be joined against a state that has not yet applied a very recent table update. `GlobalKTable` trades this timing guarantee for the freedom from co-partitioning; if event-time correctness matters, use a co-partitioned `KTable` join instead.

### Question 54 — `[FUND · ELR & min.insync.replicas · Single]`

On a Kafka 4.3 cluster with ELR enabled, an operator tries to raise the effective `min.insync.replicas` from 1 to 2 by running `kafka-configs.sh --alter --entity-type brokers --entity-name 3 --add-config min.insync.replicas=2` on each broker in turn. Afterwards, `Elr:` is empty for many partitions and the durability behaviour is not what they expected. Which statement is correct?

- A. Per-broker `min.insync.replicas` is the recommended way to roll the change out gradually; the empty `Elr:` column simply means no replica has ever left the ISR.
- B. With ELR enabled, `min.insync.replicas` must be managed at the **cluster level** (`--entity-type brokers --entity-default`); per-broker values are not supported and existing static broker-level values are removed. Also, any change to `min.insync.replicas` at cluster or topic level — even to the same value — **clears the ELR state** of the affected partitions, which then has to be rebuilt.
- C. ELR replaces `min.insync.replicas` entirely in 4.x, so the setting is ignored and the command had no effect at all.
- D. ELR state is cleared only by `unclean.leader.election.enable=true`; the empty `Elr:` column proves unclean election was turned on somewhere.

### Question 55 — `[DEV · Exceptions · Matching]`

Match each exception to its root cause.

| # | Exception |
|---|---|
| 1 | `ProducerFencedException` |
| 2 | `OffsetOutOfRangeException` |
| 3 | `UnsupportedSaslMechanismException` |
| 4 | `InvalidPartitionsException` |

| Letter | Root cause |
|---|---|
| W | The client's `sasl.mechanism` is not in the broker listener's `sasl.enabled.mechanisms` |
| X | `kafka-topics.sh --alter --partitions` asked for fewer partitions than the topic already has |
| Y | Another producer registered the same `transactional.id` and bumped the producer epoch |
| Z | The fetch position no longer exists in the partition's log — typically retention removed it |

- A. 1-Y · 2-W · 3-Z · 4-X
- B. 1-Z · 2-Y · 3-X · 4-W
- C. 1-Y · 2-Z · 3-W · 4-X
- D. 1-X · 2-Z · 3-W · 4-Y

### Question 56 — `[TEST · CI pipeline · Multi — Choose 2]`

A pull-request pipeline must fail within two minutes when (1) a changed Avro schema would be rejected by subject `orders-value`'s compatibility level and (2) a topology change alters the shape of the output records. Which two approaches satisfy both requirements **and** the time budget? (Choose two.)

- A. Start a full Testcontainers stack (broker plus Schema Registry) for every pull request and let the producer fail at runtime — it exercises the real components, but start-up alone blows the two-minute budget.
- B. Register the candidate schema with `auto.register.schemas=true` in CI and inspect the resulting version list; the registry rejects incompatible schemas, so registration doubles as the check.
- C. Call `POST /compatibility/subjects/orders-value/versions/latest` (or the Schema Registry Maven/Gradle plugin's compatibility-test goal) against the shared registry — it evaluates the schema **without registering** it and returns in milliseconds.
- D. Rely on `errors.tolerance=all` in the pipeline's smoke test so that incompatible records are routed to a DLQ topic and the build can count them.
- E. Drive the topology with `TopologyTestDriver`, piping fixed input through `TestInputTopic` and asserting the `TestOutputTopic` records against golden expectations; no broker is started.

### Question 57 — `[FUND · Unclean leader election · Single]`

After a data-centre incident, operators set `unclean.leader.election.enable=true` cluster-wide to bring offline partitions back. Service resumed. The next morning:

```
$ kafka-consumer-groups.sh --bootstrap-server broker-1:9092 --describe --group settlement

GROUP       TOPIC   PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
settlement  ledger  2          4471920         4470118         -1802
settlement  ledger  5          3980455         3978001         -2454
```

The finance warehouse also holds settlement rows for records that can no longer be found in `ledger`. What happened?

- A. Unclean election promoted replicas that were **out of sync**. Their logs were shorter than the old leaders', so committed records were lost and the partitions were truncated. Committed consumer offsets now point past the new log end offset, which is why `LAG` is negative; the warehouse rows are the records that existed only on the lost leaders.
- B. Negative lag means the consumer group is ahead of the log because it used `assign()` and committed offsets manually; unclean election is unrelated.
- C. The `__consumer_offsets` partitions were rebuilt with `--to-latest`, which over-committed the group; reset the group with `--to-current` and the lag returns to 0.
- D. Negative lag is a known display bug in `kafka-consumer-groups.sh` when `isolation.level=read_committed` is used; the data is intact.

### Question 58 — `[DEV · Offset commit · Multi — Choose 2]`

Every rolling deploy of a consumer group causes a burst of duplicate side effects downstream — roughly the last few seconds of work per pod is repeated. The consumers use the defaults (`enable.auto.commit=true`, `auto.commit.interval.ms=5000`) and the pods are stopped with `SIGTERM`, which the application handles by calling `System.exit(0)` without touching the consumer. Which two changes reduce the duplicates? (Choose two.)

- A. With auto-commit, offsets advance only every 5,000 ms, so anything processed since the last automatic commit is re-delivered after the restart — up to five seconds of work per pod.
- B. Setting `enable.auto.commit=false` on its own removes the duplicates, because offsets are then committed by the broker at the end of every fetch.
- C. Setting `isolation.level=read_committed` makes the redelivered records invisible to downstream consumers.
- D. Handle `SIGTERM` by waking the poll loop and calling `consumer.close()` (which commits the current position for an auto-commit consumer and sends a `LeaveGroup`), or call `commitSync()` explicitly before exiting.
- E. Setting `max.poll.records=1` guarantees exactly-once processing, because each record is committed before the next is fetched.

### Question 59 — `[CONNECT · Internal topics · Single]`

A platform team runs two Connect clusters against the same Kafka cluster: `connect-cdc` (`group.id=connect-cdc`) and `connect-sinks` (`group.id=connect-sinks`). To "save topics", both worker configurations point at `config.storage.topic=connect-configs`, `offset.storage.topic=connect-offsets` and `status.storage.topic=connect-status`. Connectors now appear and disappear from both clusters' `GET /connectors` output, configurations revert unpredictably, and source connectors occasionally re-ingest. What is wrong?

- A. The clusters must additionally set `connect.protocol=sessioned`; with it, records in the shared topics are namespaced by `group.id` and the conflict disappears.
- B. The three internal topics are the **durable state** of one Connect cluster, not a shared resource. Each cluster reads every record in `connect-configs` and treats it as its own desired state, so the two clusters continually overwrite each other and read each other's source offsets. Give each cluster its own distinct set of internal topic names (a unique `group.id` alone is not enough).
- C. The problem is only the offsets topic; sharing `connect-configs` and `connect-status` is supported and recommended for multi-cluster deployments.
- D. `connect-configs` must have 25 partitions rather than 1 so that the two clusters hash to different partitions; recreate it with more partitions.

### Question 60 — `[FUND · Internal topics · Single]`

A cluster started life as a single-broker development instance and later grew to three brokers. During a planned restart of broker 2, about a third of the consumer groups stopped committing and their clients logged coordinator errors until broker 2 came back. Investigation shows:

```
$ kafka-topics.sh --bootstrap-server broker-1:9092 --describe --topic __consumer_offsets | head -2
Topic: __consumer_offsets  TopicId: ...  PartitionCount: 50  ReplicationFactor: 1  Configs: cleanup.policy=compact,...
```

What is the cause, and what is the correct remediation?

- A. Setting `offsets.topic.replication.factor=3` on the brokers and rolling them re-creates the topic with the new factor, preserving committed offsets.
- B. 50 partitions is too few for 3 brokers; run `kafka-topics.sh --alter --partitions 150` on `__consumer_offsets` so every broker hosts a coordinator.
- C. `__consumer_offsets` is a KRaft metadata topic replicated by the controller quorum, so its displayed replication factor is cosmetic; the real cause must be `group.initial.rebalance.delay.ms`.
- D. `__consumer_offsets` was created when the cluster had one broker, so `offsets.topic.replication.factor` produced RF=1 and each partition has exactly one replica. A group whose coordinator partition lives on the restarting broker has no failover. `offsets.topic.replication.factor` applies **only at creation time**, so the existing topic's replication factor must be raised with `kafka-reassign-partitions.sh`.

---

> ✅ Hết giờ? Chấm bài ở [answers.md](answers.md) và điền bảng điểm theo domain trước khi xem giải thích.
