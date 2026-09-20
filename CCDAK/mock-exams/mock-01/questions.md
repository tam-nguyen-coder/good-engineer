# 🎯 CCDAK Mock Exam 01 — 60 questions · 90 minutes

> **Exam-realistic full-length mock.** Distribution follows the official CCDAK domain weights.
> ⏱️ Set a timer for **90 minutes** (~90 seconds per question). No notes, no documentation, no pausing.
> 🔒 Answers, explanations and per-domain scoring: [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (4 options) · `Multi` (choose the stated number) · `Matching` · `Ordering`.
> Tag: `[Domain · Topic · Format]`. Domains: `DEV` `FUND` `CONNECT` `OBS` `STREAMS` `TEST`.
> Anchored to **Apache Kafka 4.3** — where a default changed in 3.0/4.0, the current value is correct.
> Back to [mock index](../README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

---

### Question 1 — `[FUND · Producer send path · Ordering]`

Put the stages of a single `producer.send(record, callback)` call in the order the Java client executes them, from the application thread through to the network.

| # | Stage |
|---|---|
| 1 | The record accumulator appends the record to a per-partition batch |
| 2 | The configured `ProducerInterceptor` chain sees the record |
| 3 | The partitioner picks the target partition number |
| 4 | The key and value serializers turn the objects into byte arrays |
| 5 | The sender (I/O) thread groups ready batches per broker and issues a produce request |

- A. 4 → 2 → 3 → 1 → 5
- B. 2 → 4 → 3 → 1 → 5
- C. 2 → 3 → 4 → 1 → 5
- D. 4 → 3 → 2 → 1 → 5

### Question 2 — `[DEV · Producer defaults · Single]`

A compliance review inspects a payments service running the **Kafka 4.3** Java client. Its `producer.properties` contains only `bootstrap.servers`, `key.serializer` and `value.serializer`. The reviewer, working from a 2019 training deck, writes: *"This producer only waits for the leader and can silently duplicate records when it retries — both must be fixed."* The topic itself was created with broker defaults. Which statement is correct?

- A. The reviewer is right: `acks` defaults to `1` and `enable.idempotence` to `false`, so both must be set explicitly.
- B. The producer already runs with `acks=all` and `enable.idempotence=true`, and `min.insync.replicas` defaults to **2**, so every acknowledged write is on two replicas.
- C. The producer already runs with `acks=all` and `enable.idempotence=true`, so retries cannot duplicate within the session — but the topic's `min.insync.replicas` is **1** by default, so "all in-sync replicas" can mean a single replica.
- D. `enable.idempotence=true` is the default and it also deduplicates across producer restarts, because a `transactional.id` is generated automatically.

### Question 3 — `[CONNECT · Converter vs SMT · Single]`

A Debezium PostgreSQL **source** connector currently writes Avro to Kafka. Two changes are required before the data lands on the topic: (1) the payloads must become **schemaless JSON**, and (2) the column field `cust_id` must be renamed to `customerId`. A junior engineer proposes doing both with the `transforms` chain. Which statement is correct?

- A. Both are SMT jobs. On a source connector the SMT chain runs **after** the converter, so an SMT can rewrite the serialized bytes into JSON.
- B. (1) is the converter's job, but (2) requires a custom `Partitioner`, because SMTs can only add or drop fields, never rename them.
- C. Both are converter jobs: `JsonConverter` accepts a `renames` property for exactly this case.
- D. (1) is the converter's job (`value.converter=org.apache.kafka.connect.json.JsonConverter` with `value.converter.schemas.enable=false`); (2) is an SMT (`ReplaceField$Value` with `renames=cust_id:customerId`). On a source connector the SMT chain runs **before** the converter.

### Question 4 — `[OBS · Broker metrics · Multi — Choose 2]`

A 5-broker KRaft cluster hosts topics with `replication.factor=3` and `min.insync.replicas=2`. A rack loses power and takes brokers 4 and 5 with it. Ten minutes later the dashboard reads, across the three survivors:

```
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions      = 140
kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount      = 22
kafka.controller:type=KafkaController,name=OfflinePartitionsCount    = 0
kafka.controller:type=KafkaController,name=ActiveControllerCount     = 1 (cluster-wide sum)
```

Which two conclusions are correct? (Choose two.)

- A. `UnderReplicatedPartitions=140` means 140 partitions lost their leader and need `kafka-leader-election.sh --election-type preferred`.
- B. `OfflinePartitionsCount=0` means every partition still has a leader, so consumers can read from all of them.
- C. A cluster-wide `ActiveControllerCount` of 1 is abnormal after losing two brokers; it should equal the number of surviving controllers.
- D. The 22 partitions counted by `UnderMinIsrPartitionCount` reject `acks=all` writes with `NotEnoughReplicasException` until a replica rejoins the ISR.
- E. `UnderMinIsrPartitionCount=22` also blocks consumers on those partitions until the ISR recovers.

### Question 5 — `[STREAMS · GlobalKTable · Single]`

A Kafka Streams application runs on 8 instances. To avoid repartitioning the input stream, a developer turned the `customers` topic (60 million records, about 120 GB, updated continuously) into a `GlobalKTable`. Since then, every instance takes 40+ minutes to reach `RUNNING` and each one consumes an extra 120 GB of disk. The enrichment itself is correct. What is the right fix?

- A. Keep the `GlobalKTable` and set `num.standby.replicas=1` so the state is warm on another instance.
- B. Replace the `GlobalKTable` with a `KTable` and re-key the stream on the join key (`selectKey(...).repartition()`), so each instance only holds the partitions assigned to it.
- C. Replace the `GlobalKTable` with a windowed KStream-KStream join on the join key.
- D. Keep the `GlobalKTable` and raise `statestore.cache.max.bytes` so the table fits in memory instead of on disk.

### Question 6 — `[FUND · min.insync.replicas · Single]`

The `ledger` topic has `replication.factor=3` and `min.insync.replicas=3`; producers use the Kafka 4.3 defaults. During a kernel patch one broker is taken down at a time. The producer logs:

```
WARN [Producer clientId=ledger-writer] Got error produce response with correlation id 8123
on topic-partition ledger-7, retrying (2147483646 attempts left). Error: NOT_ENOUGH_REPLICAS
```

Writes stall for the whole restart of each broker. The team wants writes to keep succeeding during a single-broker rolling restart **without weakening the guarantee that an acknowledged record survives the loss of one broker**. What should they change?

- A. Set `min.insync.replicas=2` on the `ledger` topic.
- B. Set `acks=1` on the producers.
- C. Set `unclean.leader.election.enable=true` on the topic.
- D. Raise `retries` and `delivery.timeout.ms` so the producer rides out each restart.

### Question 7 — `[TEST · MockProducer · Single]`

A unit test must verify two things about an order service, with no broker and no Docker: (a) the exact key and headers of the `ProducerRecord` it builds, and (b) that a `TimeoutException` returned to the send callback causes the payload to be appended to an in-memory `deadLetters` list. Which setup works?

- A. `new MockProducer<>(true, null, keySer, valSer)`; read `producer.history()` for (a) and call `producer.errorNext(new TimeoutException("boom"))` for (b).
- B. `new MockProducer<>(false, null, keySer, valSer)`; `producer.history()` returns every record sent since the last `clear()` regardless of completion for (a), and `producer.errorNext(new TimeoutException("boom"))` completes the pending future exceptionally and invokes the callback for (b).
- C. `MockProducer` never invokes callbacks, so (b) requires a real broker through Testcontainers.
- D. `new MockProducer<>()`; read `producer.uncommittedRecords()` for (a) and assign the public field `producer.sendException` for (b).

### Question 8 — `[DEV · Batching defaults · Single]`

A market-data gateway upgraded its Java client from **3.9 to 4.3**. Brokers, topics and application code are unchanged. Immediately after the rollout:

```
p99 send latency         2 ms  ->  7 ms
batch-size-avg         210 B   ->  1,400 B
records-per-request-avg  1.8   ->  12
record-error-rate          0   ->  0
```

Throughput and error rates are fine; only the added latency matters to this workload. What happened, and what is the minimal fix?

- A. `batch.size` changed from `16384` to `131072` in Kafka 4.0; set `batch.size=16384` explicitly.
- B. `linger.ms` still defaults to `0`, so the cause must be `acks` switching from `1` to `all` in 4.0; set `acks=1`.
- C. `compression.type` changed from `none` to `lz4` in Kafka 4.0; set `compression.type=none` explicitly.
- D. `linger.ms` changed from `0` to `5` in Kafka 4.0 (KIP-1030); set `linger.ms=0` explicitly.

### Question 9 — `[FUND · Retention & segments · Multi — Choose 2]`

A privacy review requires that records on `audit-trail` leave broker disks roughly two hours after they are written. The topic has 6 partitions and takes about 30 MB per day in total; every setting except `retention.ms=3600000` is a default. A week later, `kafka-log-dirs.sh` still shows seven days of data on disk and consumers reading `--from-beginning` still receive week-old records. Which two statements are correct? (Choose two.)

- A. `retention.ms` only deletes **closed** segments. At 30 MB/day the active segment will not reach `segment.bytes` (1 GB), and `segment.ms` defaults to 7 days, so the first roll happens after a week.
- B. `retention.ms` is ignored unless `retention.bytes` is also set to a positive value.
- C. Setting `segment.ms` to roughly 30 minutes (or a small `segment.bytes`) makes segments roll often enough for the one-hour retention to actually take effect.
- D. Switching to `cleanup.policy=compact` would delete every record older than `retention.ms`.
- E. The retention thread only runs at broker startup, so a rolling restart is required to reclaim the space.

### Question 10 — `[CONNECT · Dead letter queue · Single]`

On a **single-broker** development Connect cluster, a developer adds error handling to an Elasticsearch sink connector:

```
errors.tolerance=all
errors.deadletterqueue.topic.name=dlq-orders
errors.deadletterqueue.context.headers.enable=true
```

The task fails on startup:

```
org.apache.kafka.common.errors.InvalidReplicationFactorException:
Replication factor: 3 larger than available brokers: 1.
```

What is the cause and the correct fix?

- A. Connect never creates the DLQ topic; it must be pre-created manually and the error is the worker's admin client failing to describe it.
- B. `errors.tolerance=all` is invalid without `errors.retry.timeout`; the replication-factor message is a misleading side effect.
- C. `errors.deadletterqueue.topic.replication.factor` defaults to **3**; set it to `1` for this dev cluster.
- D. The DLQ topic inherits the broker's `default.replication.factor`, so raise that broker setting to 1 and restart the broker.

### Question 11 — `[DEV · Consumer liveness · Single]`

A team is writing a runbook sentence: *"If a consumer pod is SIGKILLed, its partitions are reassigned to another member within about N seconds."* The consumers run Kafka 4.3 clients on the classic protocol with no timeout overrides, and the processing loop is fast. Ignoring `group.initial.rebalance.delay.ms`, what is N and which configuration sets it?

- A. About **10 seconds** — `session.timeout.ms` defaults to `10000`.
- B. About **45 seconds** — `session.timeout.ms` defaults to `45000`; the coordinator evicts a member when no heartbeat arrives within that window, while heartbeats themselves go out every `heartbeat.interval.ms` (3000).
- C. About **300 seconds** — `max.poll.interval.ms` defaults to `300000` and is what detects a dead member.
- D. About **3 seconds** — `heartbeat.interval.ms` defaults to `3000` and a single missed heartbeat evicts the member.

### Question 12 — `[STREAMS · Windowing · Matching]`

Match each window definition to the behaviour it produces.

| # | Window definition |
|---|---|
| 1 | `TimeWindows.ofSizeAndGrace(Duration.ofMinutes(5), Duration.ofSeconds(30)).advanceBy(Duration.ofMinutes(1))` |
| 2 | `SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(30))` |
| 3 | `SlidingWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(10))` |
| 4 | `TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5))` |

| Letter | Behaviour |
|---|---|
| W | Fixed size, no overlap — every record belongs to exactly one window |
| X | Fixed size, overlapping — a new window starts on a fixed schedule, so one record contributes to several windows |
| Y | Variable length and data-driven — the window for a key closes after a period of inactivity for that key |
| Z | Bounded by the maximum time difference between two records; windows are created only when a record arrives, and both endpoints are inclusive |

- A. 1-Z · 2-Y · 3-X · 4-W
- B. 1-W · 2-Y · 3-Z · 4-X
- C. 1-X · 2-Y · 3-Z · 4-W
- D. 1-X · 2-Z · 3-Y · 4-W

### Question 13 — `[FUND · High watermark · Single]`

A topic has `replication.factor=3` and `min.insync.replicas=1`; producers use `acks=all`. During a storage incident both followers of partition 12 fall behind and are removed from the ISR, leaving only the leader. Producers keep writing successfully, and the platform team notices that end-to-end latency (produce acknowledged → visible to a consumer) actually **dropped** during the incident. Which statement explains the observation and names the risk?

- A. The high watermark is the smallest offset replicated to **every member of the ISR**. With one member, it advances as soon as the leader appends, so records become visible immediately — and an acknowledged record now exists on a single broker, so it is lost if that broker dies.
- B. Consumers transparently switched to fetching from the followers, which were less loaded; there is no durability risk because the data is still on three brokers.
- C. The broker silently downgraded `acks=all` to `acks=1` to preserve availability, which is why latency dropped.
- D. The high watermark plays no role here; latency dropped because replication traffic stopped competing for the network, and `acks=all` still waits for all three replicas, so durability is unchanged.

### Question 14 — `[OBS · Consumer poll metrics · Single]`

A consumer group with default configuration reports:

```
kafka.consumer:type=consumer-metrics
  time-between-poll-avg = 41,000     time-between-poll-max = 287,000
  last-poll-seconds-ago = 96         poll-idle-ratio-avg   = 0.04
kafka.consumer:type=consumer-coordinator-metrics
  rebalance-rate-per-hour = 0        failed-rebalance-total = 0
kafka.consumer:type=consumer-fetch-manager-metrics
  records-lag-max = 1,900,000
```

Which reading is MOST accurate?

- A. The group is already thrashing on rebalances; raise `session.timeout.ms`.
- B. `poll-idle-ratio-avg` near 0 means the consumer is starved of data; add partitions and consumers.
- C. The consumer spends nearly all its time in user code (`poll-idle-ratio-avg` = 0.04) and `time-between-poll-max` of 287 s is within seconds of the 300 s `max.poll.interval.ms`; it has not been evicted yet but is about to be. Lower `max.poll.records` or shorten the per-record work.
- D. Lag of 1.9 M with zero rebalances means the fetch path is the bottleneck; raise `fetch.max.bytes` and `max.partition.fetch.bytes`.

### Question 15 — `[DEV · Transactions · Ordering]`

A consume-transform-produce worker uses a transactional producer that was constructed with a stable `transactional.id`. Put the calls in the order they execute for **one** input batch, starting from a freshly constructed producer.

| # | Call |
|---|---|
| 1 | `producer.commitTransaction()` |
| 2 | `producer.send(...)` for each output record |
| 3 | `producer.initTransactions()` |
| 4 | `producer.beginTransaction()` |
| 5 | `consumer.poll(...)` returns the input batch |
| 6 | `producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata())` |

- A. 3 → 4 → 5 → 2 → 1 → 6
- B. 5 → 3 → 4 → 2 → 6 → 1
- C. 4 → 3 → 5 → 2 → 6 → 1
- D. 3 → 5 → 4 → 2 → 6 → 1

### Question 16 — `[CONNECT · Distributed mode · Single]`

Three Connect workers share `group.id=connect-prod` and serve REST on port 8083. An operator needs the consumer lag of the sink connector named `es-orders`, whose topic is `orders`. Running `kafka-consumer-groups.sh --describe --group connect-prod` prints a small, static set of offsets and no `orders` partitions at all. What is happening?

- A. Sink connectors do not use consumer groups at all; the only way to see progress is `GET /connectors/es-orders/status`.
- B. Sink connector positions live in the `connect-offsets` internal topic; read that topic with a console consumer.
- C. The connector must be given `consumer.group.id=connect-prod` so that its lag is reported under the worker group.
- D. `connect-prod` is the **worker** group used for worker and connector coordination. Each sink connector consumes with its own group named `connect-es-orders`; describe that group instead.

### Question 17 — `[TEST · MockConsumer · Multi — Choose 2]`

A developer unit-tests a poll loop that uses `subscribe()` with a `ConsumerRebalanceListener` which commits offsets in `onPartitionsRevoked`:

```java
MockConsumer<String, String> c = new MockConsumer<>("earliest");
c.subscribe(List.of("orders"), listener);
c.addRecord(new ConsumerRecord<>("orders", 0, 0L, "k", "v"));
ConsumerRecords<String, String> r = c.poll(Duration.ofMillis(100));
```

`poll()` throws `IllegalStateException` and the listener is never invoked. Which two changes make the test work? (Choose two.)

- A. Call `c.rebalance(List.of(new TopicPartition("orders", 0)))` — `MockConsumer` has no coordinator, so `subscribe()` alone assigns nothing, and `rebalance(...)` is what fires the listener callbacks.
- B. Call `c.updateBeginningOffsets(Map.of(new TopicPartition("orders", 0), 0L))` before `poll()`, because without a starting position the mock has nothing to poll from.
- C. Replace the constructor with `new MockConsumer<>(OffsetResetStrategy.EARLIEST)`, which is the supported form in 4.3.
- D. Call `c.setMaxPollRecords(1)` so that the buffered record is returned by `poll()`.
- E. Replace `MockConsumer` with a Testcontainers broker — rebalance listeners cannot run without a coordinator.

### Question 18 — `[FUND · KRaft quorum · Single]`

A cluster runs 3 dedicated KRaft controllers and 6 brokers. A network partition isolates the rack holding **two** of the three controllers. Which statement describes the cluster during the partition?

- A. Everything stops: brokers cannot serve produce or fetch requests without a controller quorum.
- B. The surviving controller becomes the active controller because it is the only candidate, and the cluster keeps operating normally.
- C. The quorum (a majority of 3 is 2) is lost, so no new metadata can be committed. Existing partition leaders keep serving produce and fetch requests, but leader elections, ISR updates, topic creation and ACL changes stall until a second controller returns.
- D. The brokers elect one of themselves as controller, because `process.roles` can be changed at runtime when a quorum is unavailable.

### Question 19 — `[DEV · Producer configs · Matching]`

Match each Kafka 4.3 producer configuration to what it bounds.

| # | Config |
|---|---|
| 1 | `max.block.ms` |
| 2 | `delivery.timeout.ms` |
| 3 | `request.timeout.ms` |
| 4 | `linger.ms` |
| 5 | `batch.size` |

| Letter | Bound |
|---|---|
| V | Bytes — the maximum size of one batch for one partition (default 16,384) |
| W | Milliseconds the accumulator waits for more records before a non-full batch becomes ready (default 5) |
| X | Milliseconds the client waits for a response to a single in-flight request before treating it as failed (default 30,000) |
| Y | Milliseconds `send()` and `partitionsFor()` may block waiting for metadata or accumulator memory (default 60,000) |
| Z | Total milliseconds from the `send()` call until success or final failure, covering linger, all retries and every request attempt (default 120,000) |

- A. 1-Y · 2-Z · 3-X · 4-W · 5-V
- B. 1-Z · 2-Y · 3-X · 4-W · 5-V
- C. 1-Y · 2-X · 3-Z · 4-W · 5-V
- D. 1-Y · 2-Z · 3-W · 4-X · 5-V

### Question 20 — `[STREAMS · KStream-KTable join · Single]`

A topology joins an `orders` `KStream` to a `customer-tier` `KTable`, both keyed by `customerId` with 12 partitions each, and writes the enriched order to an output topic. At 10:00 a customer is upgraded from `SILVER` to `GOLD`, and the tier change is written to `customer-tier`. The team expects the enriched form of that customer's earlier orders to be re-emitted with the new tier, but nothing appears on the output topic at 10:00. Which statement is correct?

- A. A KStream-KTable join is driven only from the **stream** side: a record arriving on the stream triggers a lookup, while a table update merely changes what future stream records will see.
- B. The join is missing a `JoinWindows` definition; without a window, table-side updates are silently discarded.
- C. The `KTable` must be materialized with `Materialized.as(...)` before its updates can trigger join output.
- D. `customer-tier` must be a `GlobalKTable`, which is the only table type whose updates trigger join output.

### Question 21 — `[OBS · Controller metrics · Single]`

A Prometheus rule sums `ActiveControllerCount` across all scraped Kafka nodes of a KRaft cluster with 3 dedicated controllers. The series normally reads exactly 1. For a 40-second window it read **0**; during that window `kafka-topics.sh --create` timed out, while produce and consume traffic on existing topics continued without errors. What happened?

- A. All three controllers crashed and the cluster was fully down; the surviving produce traffic must be a scraping artefact.
- B. A controller failover: the active controller lost leadership of the metadata quorum and a new one was elected. During the gap no node reported 1, so metadata writes such as topic creation failed, while brokers kept serving reads and writes from the metadata they already had.
- C. In KRaft, `ActiveControllerCount` is only exposed by brokers, so 0 is the normal steady-state value for a cluster with dedicated controllers.
- D. Two controllers briefly reported 1 each and the exporter subtracted them, which is the classic KRaft split-brain signature.

### Question 22 — `[CONNECT · Schema Registry compatibility · Matching]`

Match each Confluent Schema Registry compatibility setting to the rule it enforces on the next registered version of a subject.

| # | Compatibility |
|---|---|
| 1 | `BACKWARD` |
| 2 | `FORWARD` |
| 3 | `FULL` |
| 4 | `BACKWARD_TRANSITIVE` |

| Letter | Rule |
|---|---|
| W | Only add a field **with** a default, or delete a field **that has** a default — the change must work in both directions |
| X | Add an optional field (one with a default) or delete a field; the new schema is checked only against the **immediately previous** version, and consumers are upgraded first |
| Y | Add a field (with or without a default) or delete an optional field; data written with the new schema stays readable by the previous schema, and producers are upgraded first |
| Z | The same rule as one of the above, but the new schema is checked against **every** previously registered version, not just the last one |

- A. 1-Y · 2-X · 3-W · 4-Z
- B. 1-X · 2-Y · 3-W · 4-Z
- C. 1-X · 2-W · 3-Y · 4-Z
- D. 1-Z · 2-Y · 3-W · 4-X

### Question 23 — `[DEV · assign() and seek · Single]`

After an incident, an engineer must dump **only partition 7** of the `payments` topic to a file, starting at `2026-09-14T08:00:00Z`. The live consumer group `billing` is still running and must not be disturbed: no rebalance, no change to its committed offsets. Which approach meets all the constraints?

- A. `subscribe(List.of("payments"))` with `group.id=billing-replay` and `auto.offset.reset=earliest`, discarding every partition except 7 in application code.
- B. `kafka-consumer-groups.sh --group billing --reset-offsets --to-datetime 2026-09-14T08:00:00.000 --topic payments:7 --execute`, then let the running consumers replay into the file.
- C. `assign(List.of(new TopicPartition("payments", 7)))`, then translate the timestamp with `offsetsForTimes(...)` and call `seek(tp, offset)` before entering the poll loop.
- D. `subscribe(List.of("payments"))` with `group.id=billing` and a `ConsumerRebalanceListener` that calls `seek()` for partition 7 inside `onPartitionsAssigned`.

### Question 24 — `[FUND · Log compaction · Single]`

The `device-state` topic uses `cleanup.policy=compact` and is keyed by `deviceId`; all other settings are defaults. Two applications read it. Application A consumes continuously at the head of the log and observes **every** intermediate state change for a device. Application B replays the whole topic from offset 0 each night and usually observes exactly one record per device — but for some devices it sees two or three. Which statement explains both observations?

- A. Compaction is applied at read time and the result depends on the consumer's `isolation.level`, which differs between the two applications.
- B. `min.cleanable.dirty.ratio` defaults to 0.5, which means the cleaner deliberately keeps about half of the records for each key.
- C. A compacted topic always holds exactly one record per key, so A must actually be reading a different topic whose `cleanup.policy` is `delete`.
- D. The cleaner only rewrites **closed** segments, and only once the dirty ratio of the log reaches `min.cleanable.dirty.ratio` (0.5). The active segment is never compacted, so A sees every update at the head and B sees the latest value per key plus whatever has not yet been cleaned.

### Question 25 — `[TEST · TopologyTestDriver · Single]`

A topology is `builder.stream("in").groupByKey().count().toStream().to("out")`. A `TopologyTestDriver` test pipes five records with the **same key** and asserts that `outputTopic.readKeyValuesToList()` contains five entries with counts 1, 2, 3, 4, 5 — and it passes. In production the same topology writes only one or two records to `out` for an identical burst. Which statement explains the difference?

- A. `TopologyTestDriver` processes each piped record synchronously and flushes after every one, so every intermediate aggregation result is emitted. In production the record cache (`statestore.cache.max.bytes`, 10 MB) and `commit.interval.ms` (30,000 ms) conflate updates, so usually only the latest value per key is forwarded.
- B. Production loses records because `processing.guarantee` defaults to `at_least_once`, which permits dropping intermediate aggregation results.
- C. `TopologyTestDriver` disables state stores, so the counts it produces are synthetic; adding `Materialized.as(...)` makes the test realistic.
- D. This is a known bug fixed by wrapping the count in `suppress(Suppressed.untilWindowCloses(...))`.

### Question 26 — `[DEV · Offsets and lag · Single]`

`kafka-consumer-groups.sh --describe --group billing` prints one row:

```
GROUP    TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
billing  invoices  4          5000            5120            120
```

The consumer runs with `enable.auto.commit=false` and calls `commitSync(Map<TopicPartition, OffsetAndMetadata>)` after each record. Which statement is correct?

- A. The last record processed has offset **5000**, and 120 records remain: offsets 5001 through 5120.
- B. The last record this group processed on `invoices-4` has offset **4999**, and 120 records remain to be read: offsets 5000 through 5119.
- C. The last record processed has offset **5120**; `LAG` counts records already removed by retention.
- D. `CURRENT-OFFSET` is the consumer's in-memory fetch position rather than its committed offset, so nothing can be concluded about what was processed.

### Question 27 — `[OBS · Broker metrics · Matching]`

Match each broker metric reading to the symptom it indicates.

| # | Metric reading |
|---|---|
| 1 | `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` = 7 |
| 2 | `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` = 140 while `OfflinePartitionsCount` = 0 |
| 3 | `IsrShrinksPerSec` and `IsrExpandsPerSec` both elevated and roughly equal on one broker |
| 4 | `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` = 0.08 |

| Letter | Symptom |
|---|---|
| W | A replica keeps dropping out of and rejoining the ISR — a flapping follower, typically long GC pauses or saturated disk/network rather than a hard failure |
| X | Seven partitions have **no leader at all**: producers and consumers for them fail and availability is lost |
| Y | The request handler (I/O) thread pool is nearly saturated; requests queue and latency rises |
| Z | Followers are behind or a broker is down, but every partition still has a leader, so clients keep working with reduced durability |

- A. 1-Z · 2-X · 3-W · 4-Y
- B. 1-X · 2-W · 3-Z · 4-Y
- C. 1-X · 2-Z · 3-Y · 4-W
- D. 1-X · 2-Z · 3-W · 4-Y

### Question 28 — `[STREAMS · Exactly-once · Single]`

A Kafka Streams application runs with `processing.guarantee=exactly_once_v2` on Kafka 4.3. Downstream teams complain that output records now arrive in bursts every 30 seconds instead of continuously. Reviewing the diff, the team finds that someone added `commit.interval.ms=30000` to the properties with the comment *"restore the documented default"*. What is the effect of that line?

- A. It is ignored: under exactly-once the commit interval is pinned to 100 ms and cannot be overridden.
- B. Any value above 100 ms silently downgrades the guarantee to `at_least_once`, which is the real cause of the bursts.
- C. Under `exactly_once_v2` Streams lowers the **default** `commit.interval.ms` from 30,000 to **100** ms. Setting it back to 30,000 is honoured, and because output records only become visible to `read_committed` consumers when the transaction commits, end-to-end latency grows to about 30 seconds. Correctness is unaffected.
- D. The default under exactly-once is 30,000 like everywhere else, so this line changes nothing; the bursts must come from `statestore.cache.max.bytes`.

### Question 29 — `[CONNECT · tasks.max · Single]`

A distributed Connect cluster of 3 workers runs two connectors, both configured with `tasks.max=10`. For an S3 **sink** connector reading the 4-partition topic `events`, `GET /connectors/s3-events/tasks` returns **10** entries, all `RUNNING`, and `kafka-consumer-groups.sh --describe --group connect-s3-events` shows 10 members of which **6 own no partitions**. For a `FileStreamSource` connector, `GET /connectors/file-audit/tasks` returns **1** entry. Neither connector reports a failure. Which statement is correct?

- A. The 6 idle members mean a rebalance failed; restarting the connector will spread the 4 partitions across all 10 tasks.
- B. The number of tasks always equals the number of workers, so both connectors should show 3; the cluster is mis-sized.
- C. Raising `events` to 10 partitions would engage all 10 sink tasks and would also raise `file-audit` to 10 tasks.
- D. `tasks.max` is an upper bound and each connector decides how many task configurations it returns. A sink connector's tasks are members of one consumer group, so beyond the topic's 4 partitions the extra tasks are simply idle; `FileStreamSource` returns exactly one task whatever `tasks.max` says, because it tails a single file.

### Question 30 — `[DEV · Rebalance protocol · Ordering]`

A consumer using the **classic** group protocol (`group.protocol=classic`) starts up and joins an existing group. Put the steps in the order they occur.

| # | Step |
|---|---|
| 1 | The group leader runs the negotiated `partition.assignment.strategy` and produces the assignment for every member |
| 2 | `FindCoordinator` — the consumer discovers the broker that hosts its group's `__consumer_offsets` partition |
| 3 | `SyncGroup` — every member sends its assignment proposal (empty for non-leaders) and receives its own partitions |
| 4 | `JoinGroup` — members send their subscriptions and the coordinator designates one of them as group leader |
| 5 | The member starts sending `Heartbeat` requests from the background thread and begins fetching records |

- A. 2 → 4 → 1 → 3 → 5
- B. 2 → 4 → 3 → 1 → 5
- C. 4 → 2 → 1 → 3 → 5
- D. 2 → 1 → 4 → 3 → 5

### Question 31 — `[FUND · Message size · Single]`

An engineer adds a client-side guard: *"reject any record whose serialized size exceeds 1,048,576 bytes, because that is the broker limit."* A colleague objects that this is not the broker's number. Which statement about the Kafka 4.3 defaults is correct?

- A. Producer `max.request.size` defaults to **1,048,576** while broker `message.max.bytes` defaults to **1,048,588** — twelve bytes more, to leave room for record-batch overhead. The producer therefore rejects an oversized record client-side before the broker ever sees it.
- B. Both default to **1,048,576**, so the two limits are interchangeable and the guard is exactly right.
- C. `message.max.bytes` defaults to **1,000,000** and `max.request.size` to **1,048,576**, so the broker limit is the stricter of the two.
- D. `max.request.size` caps a single record while `message.max.bytes` caps the whole produce request across all partitions, so the broker limit is effectively far larger than 1 MB.

### Question 32 — `[OBS · Rebalance diagnostics · Multi — Choose 2]`

A group of 9 consumer pods runs the classic protocol with `partition.assignment.strategy` set to `CooperativeStickyAssignor` only, and no timeout overrides. Metrics:

```
rebalance-rate-per-hour    = 26        rebalance-latency-avg      = 210 ms
failed-rebalance-total     = 0         last-rebalance-seconds-ago = 47
assigned-partitions oscillates between 3 and 5 per member
records-lag-max stair-steps upward after each rebalance
```

The platform's node autoscaler recycles one pod roughly every two minutes; each restart completes in about 25 seconds. Which two statements are correct? (Choose two.)

- A. Raising `heartbeat.interval.ms` from 3,000 to 15,000 reduces the rebalance rate because fewer heartbeats mean fewer opportunities to detect a departure.
- B. `failed-rebalance-total = 0` proves the group is healthy, so the lag must come from slow record processing rather than from membership churn.
- C. Giving each pod a stable `group.instance.id` (static membership) means a pod that returns within `session.timeout.ms` — the 4.3 default of 45,000 ms already covers a 25-second restart — reclaims its partitions with no rebalance at all.
- D. Switching to `RangeAssignor` would move fewer partitions, because Range is the sticky assignor.
- E. The low `rebalance-latency-avg` is consistent with cooperative rebalancing: members keep the partitions that do not move, so the lag comes from the sheer rate of churn rather than from stop-the-world pauses.

### Question 33 — `[DEV · Idempotent producer · Multi — Choose 2]`

A Kafka 4.3 producer runs with defaults and no `transactional.id`. Which two statements about how it prevents duplicates are correct? (Choose two.)

- A. The broker issues a producer ID (PID), and the producer attaches a monotonically increasing sequence number **per partition**. A partition leader that receives a batch whose sequence it has already appended acknowledges it again without writing it twice.
- B. Deduplication survives a producer restart, because the PID is derived deterministically from `client.id`.
- C. Idempotence requires `max.in.flight.requests.per.connection=1`; any higher value silently disables deduplication while leaving the config enabled.
- D. The guarantee is scoped to a **single producer session and a single partition**. A restarted producer receives a new PID, so records re-sent by application-level retry logic after a restart can still be duplicated.
- E. Idempotence also removes duplicates on the consumer side, because `poll()` filters records whose sequence number it has already returned.

### Question 34 — `[CONNECT · Internal topics · Multi — Choose 2]`

A platform team stands up a second Connect cluster for another team. They copy `connect-distributed.properties` from the existing cluster, change only `rest.port` from 8083 to 8084, and start three new workers on different hosts. Connectors begin disappearing and reappearing on both clusters, and a connector created through the new cluster's REST API shows up on the old one. Which two statements are correct? (Choose two.)

- A. Two Connect clusters may safely share the three internal topics as long as their `group.id` values differ.
- B. Both sets of workers share the same `group.id` and the same `config.storage.topic`, `offset.storage.topic` and `status.storage.topic`, so the six workers joined **one** Connect cluster and are rebalancing against each other.
- C. A separate Connect cluster requires a distinct `group.id` **and** distinct internal topic names; `rest.port` has nothing to do with cluster membership.
- D. The root cause is that `config.storage.topic` has only 1 partition; raising it to 25 lets both clusters store their configs independently.
- E. Connect workers discover their peers through the REST port, so changing it to 8084 should have been sufficient to separate the clusters.

### Question 35 — `[FUND · Kafka 4.x upgrade · Single]`

An operator upgrades brokers from 3.7 to 4.3 by dropping in the new binaries and reusing the existing `server.properties`. One host logs a configuration failure naming `zookeeper.connect`, and another host, still on Java 11, fails with:

```
java.lang.UnsupportedClassVersionError: kafka/Kafka has been compiled by a more recent
version of the Java Runtime (class file version 61.0), this version of the Java Runtime
only recognizes class file versions up to 55.0
```

Which statement describes the required work?

- A. Restore `zookeeper.connect` and set `inter.broker.protocol.version=4.3`; brokers continue to support Java 11 and ZooKeeper coexistence through 4.x.
- B. Kafka 4.x is **KRaft-only** — ZooKeeper mode and `zookeeper.connect` were removed in 4.0 — and brokers require **Java 17** (class file 61.0). A ZooKeeper-based cluster must first be migrated to KRaft on a 3.x release (3.9.x is the recommended stepping stone) before upgrading, and the JVM must be upgraded too.
- C. `zookeeper.connect` was renamed to `controller.quorum.voters` in 4.0; rename the property in place and keep Java 11, which remains the broker baseline.
- D. Both messages indicate a corrupted installation; re-extract the 4.3 tarball onto both hosts and restart.

### Question 36 — `[STREAMS · Suppression · Multi — Choose 2]`

A billing topology aggregates revenue per merchant into hourly tumbling windows with a 10-minute grace period and `suppress(Suppressed.untilWindowCloses(BufferConfig.unbounded()))`. In production, busy merchants get their hourly figure a few minutes after the hour, but a low-traffic merchant's window is sometimes not emitted for many hours. Which two statements are correct? (Choose two.)

- A. `suppress(untilWindowCloses)` emits when **stream time** passes window end plus grace, and stream time advances from the timestamps of records arriving on that task's partitions — so a key that receives no further traffic keeps its window open.
- B. `suppress` is driven by wall-clock time, so a 10-minute grace period guarantees emission 10 minutes after the hour regardless of traffic.
- C. Setting `num.standby.replicas=1` makes suppressed windows emit on schedule by giving the buffer a warm copy.
- D. Switching to `Suppressed.untilTimeLimit(...)` would also guarantee exactly one output record per window per key.
- E. Suppression state is held per task, so a partition receiving no records at all does not advance stream time and emits nothing for the keys it owns, however long the wall clock runs.

### Question 37 — `[DEV · Assignment strategy · Single]`

A team wants to eliminate stop-the-world rebalances. Their consumers run Kafka 4.3 clients on the classic protocol with no `partition.assignment.strategy` configured, and every rebalance logs, for every member:

```
INFO [Consumer clientId=orders-3, groupId=orders] Revoke previously assigned partitions
     orders-0, orders-1, orders-2
```

A developer concludes: *"We must add `CooperativeStickyAssignor` to `partition.assignment.strategy`."* What is the correct analysis?

- A. The default is `RangeAssignor` alone, so the developer is right: add `CooperativeStickyAssignor` to the list and do a rolling restart.
- B. Cooperative rebalancing is only available with `group.protocol=consumer`; on the classic protocol the assignor list is ignored in 4.3.
- C. The default list is already `[RangeAssignor, CooperativeStickyAssignor]`. The group negotiates the **first** strategy that every member supports, which is `RangeAssignor` — an EAGER assignor. The change needed is to **remove** `RangeAssignor`, leaving `CooperativeStickyAssignor` alone; one rolling bounce is enough because every member already supports it.
- D. `StickyAssignor` is the cooperative implementation; set `partition.assignment.strategy=org.apache.kafka.clients.consumer.StickyAssignor`.

### Question 38 — `[TEST · Test strategy · Single]`

Three tests must be written for a payments pipeline, and the CI runners have Docker available:

1. the service builds a `ProducerRecord` with the right key and headers;
2. a `read_committed` consumer never sees records belonging to an **aborted** transaction;
3. a windowed aggregation topology emits the right final values.

Which assignment of tools is correct and keeps the suite fastest?

- A. (1) Testcontainers, (2) `MockConsumer` with `setPollException`, (3) Testcontainers.
- B. (1) `MockProducer`, (2) `MockConsumer` configured with `isolation.level=read_committed`, (3) `TopologyTestDriver`.
- C. All three with `TopologyTestDriver`, which starts an embedded broker for the cases that need one.
- D. (1) `MockProducer`, (2) a real broker through Testcontainers `KafkaContainer`, (3) `TopologyTestDriver`.

### Question 39 — `[FUND · Topic lifecycle · Multi — Choose 2]`

To clear a large backlog quickly, an operator deletes the topic `events` and immediately recreates it with the same name and the same partition count. The consumer group `analytics` was stopped beforehand and is restarted afterwards with `auto.offset.reset=latest`. Which two statements are correct? (Choose two.)

- A. Deleting a topic also deletes every consumer group that was subscribed to it, so `analytics` starts as a brand-new group.
- B. The recreated topic receives a **new topic ID**, so clients still holding the old ID see errors such as `UNKNOWN_TOPIC_ID` until they refresh their metadata.
- C. The recreated topic automatically inherits the deleted topic's non-default topic-level configuration, such as `retention.ms` and `cleanup.policy`.
- D. Deleting the topic does not immediately remove the group's committed offsets from `__consumer_offsets`. Those offsets now point beyond the end of the new, empty log, so the fetch position is out of range and the consumer resets according to `auto.offset.reset`.
- E. Committed offsets are preserved exactly, so `analytics` resumes from its previous offset and reads the new records from there onward.

### Question 40 — `[CONNECT · Source offsets · Single]`

A JDBC source connector `orders-jdbc` running in incrementing mode must re-ingest its table from the beginning. The operator calls `DELETE /connectors/orders-jdbc/offsets` and receives `400 Bad Request` with a message stating that the connector must be stopped first. What is the correct procedure on Kafka 4.3 Connect?

- A. `PUT /connectors/orders-jdbc/stop` (state becomes `STOPPED`: the config is kept and the tasks are removed) → `DELETE /connectors/orders-jdbc/offsets` → `PUT /connectors/orders-jdbc/resume`.
- B. `PUT /connectors/orders-jdbc/pause` → `DELETE /connectors/orders-jdbc/offsets` → `PUT /connectors/orders-jdbc/resume`; pausing is sufficient because it stops the tasks from polling.
- C. `DELETE /connectors/orders-jdbc` and recreate it with the same name and config — deleting a connector deletes its stored source offsets.
- D. `kafka-consumer-groups.sh --group connect-orders-jdbc --reset-offsets --to-earliest --execute`, because Connect stores source positions in a consumer group.

### Question 41 — `[DEV · Batching and compression · Multi — Choose 2]`

A producer sends 40,000 records/s of roughly 300-byte JSON, with `null` keys, to a 24-partition topic. Metrics:

```
batch-size-avg          = 1,050 bytes      records-per-request-avg = 3.5
request-rate            = 11,000 /s        compression-rate-avg    = 0.92
compression.type        = gzip             record-error-rate       = 0
```

Broker CPU and network-thread utilisation are both high, and the team can accept up to 50 ms of extra producer-side latency. Which two changes attack the problem? (Choose two.)

- A. Raise `linger.ms` from 5 to 50 and `batch.size` from 16,384 to 131,072 so the accumulator forms far fewer, far larger batches per partition.
- B. Set `max.in.flight.requests.per.connection=1` so that the producer waits for each response, which naturally lets batches grow while a request is outstanding.
- C. Switch `compression.type` from `gzip` to `lz4` or `zstd`: compression is applied per batch, the 0.92 ratio shows that 1 KB batches barely compress, and gzip is the most CPU-expensive codec of the set.
- D. Set `acks=0` so the brokers stop sending responses, which removes most of the broker CPU cost.
- E. Increase the topic from 24 to 96 partitions so that each batch fills faster.

### Question 42 — `[OBS · ISR churn · Single]`

On a 5-broker cluster with `replication.factor=3` and `min.insync.replicas=2`, `UnderReplicatedPartitions` oscillates between 0 and about 30 every few minutes. `IsrShrinksPerSec` and `IsrExpandsPerSec` both average around 0.4/s and only on broker 3. No broker has restarted, `OfflinePartitionsCount` is 0, and broker 3's GC log shows repeated stop-the-world pauses of 35 to 45 seconds. What is the MOST likely cause, and what happens to `acks=all` producers?

- A. `unclean.leader.election.enable` is set to `true`, so leadership keeps moving between replicas and `acks=all` writes fail during each move.
- B. Broker 3's GC pauses exceed `replica.lag.time.max.ms` (30,000 ms), so its follower replicas fall out of the ISR and rejoin on the next successful fetch. With RF=3 and `min.insync.replicas=2`, `acks=all` writes keep succeeding, but durability is reduced during each shrink.
- C. `replica.lag.max.messages` (default 4,000) is being exceeded; raise it to stop the flapping.
- D. The controller is flapping, so the real signal is `ActiveControllerCount`, and `acks=all` writes are rejected with `NotEnoughReplicasException` throughout.

### Question 43 — `[STREAMS · Joins · Single]`

A `KTable<String, Order>` built from `orders` (keyed by `orderId`, 24 partitions) must be joined to a `KTable<String, Customer>` built from `customers` (keyed by `customerId`, 6 partitions). Each order value carries a `customerId` field. The result must stay a table that updates when **either** side changes, and `orders` must not be repartitioned. Which approach is correct?

- A. Only a `GlobalKTable` avoids co-partitioning; convert `customers` to a `GlobalKTable` and use a KTable-GlobalKTable join.
- B. Co-partitioning is mandatory for every KTable-KTable join, and Streams performs the required repartition of `orders` automatically.
- C. Use the foreign-key join `orders.join(customers, order -> order.getCustomerId(), joiner)`: it is the KTable-KTable join that does not require co-partitioning, and Streams maintains it through internal subscription topics so a change on either side updates the result.
- D. Call `orders.toStream()` and use a KStream-GlobalKTable join, which returns a KTable and therefore keeps the table semantics.

### Question 44 — `[FUND · Broker recovery · Single]`

After a data-centre power loss, brokers restart and spend a long time in log recovery. An SRE follows a 2022 runbook: *"Kafka uses one recovery thread per data directory by default; raise `num.recovery.threads.per.data.dir` to speed up startup."* The brokers run Kafka 4.3 with 8 entries in `log.dirs`. Which statement is correct?

- A. The default is still **1**, so the runbook is current and doubling the value will roughly halve recovery time.
- B. The setting is named `num.recovery.threads` and is a single broker-wide pool, so the number of `log.dirs` is irrelevant.
- C. Recovery threads only matter for compacted topics, so the setting is irrelevant to a general-purpose cluster.
- D. The default is **2** since Kafka 4.0 (KIP-1030), and it applies **per data directory**, so 8 directories already give 16 recovery threads; raising it further helps only if the disks are not already saturated.

### Question 45 — `[DEV · Consumer group protocol · Single]`

A platform runs Kafka 4.3 brokers and 4.3 clients. A tech lead writes: *"KIP-848 went GA in 4.0, so our groups already use broker-side assignment — we can delete `session.timeout.ms` and `partition.assignment.strategy` from the consumer config."* But `kafka-consumer-groups.sh --describe --group orders --state` still reports the group as `Classic` with a member acting as group leader. Which statement is correct?

- A. `group.protocol` still defaults to `classic` in 4.3. KIP-848 is GA but **opt-in** via `group.protocol=consumer`; the classic protocol is deprecated in 4.3 yet remains the default, so both of those configs are still in effect.
- B. `group.protocol` has defaulted to `consumer` since 4.0, so the describe output is stale; restarting the group coordinator will refresh it.
- C. KIP-848 is enabled per topic by setting `group.type=consumer` on the topic, not on the client.
- D. The classic protocol was removed in 4.3, so a group reporting `Classic` indicates a client/broker version mismatch.

### Question 46 — `[CONNECT · SMT and predicates · Multi — Choose 2]`

A sink connector must skip every tombstone record and, on the records that survive, drop the `ssn` field before writing. The operator configures:

```
transforms=dropSsn
transforms.dropSsn.type=org.apache.kafka.connect.transforms.ReplaceField$Value
transforms.dropSsn.exclude=ssn

predicates=isTombstone
predicates.isTombstone.type=org.apache.kafka.connect.transforms.predicates.RecordIsTombstone
```

Tombstones still reach the connector and cause a `NullPointerException`. Which two statements are correct? (Choose two.)

- A. A predicate alone filters records; the only missing property is `predicates.isTombstone.negate=false`.
- B. Tombstones can only be removed by a converter, because an SMT cannot drop a record from the pipeline.
- C. Declaring a predicate is not enough: it must be attached to a transformation. Here that means adding a `Filter` SMT (`org.apache.kafka.connect.transforms.Filter`) with `transforms.dropTombstone.predicate=isTombstone`, and listing that alias in `transforms`.
- D. SMTs are applied in the order listed in `transforms`, so the tombstone filter must be placed **before** `dropSsn`, otherwise `ReplaceField$Value` still sees the null value first.
- E. `ReplaceField$Value` with `exclude` already skips records with a null value, so the `NullPointerException` must originate in the converter.

### Question 47 — `[TEST · MockProducer transactions · Single]`

A unit test for a consume-transform-produce loop must assert, without a broker, that for one input batch the code (a) sends exactly 3 output records and (b) commits the consumer offsets **inside the same transaction**. Which `MockProducer` API gives both assertions?

- A. `MockProducer` throws `UnsupportedOperationException` from `initTransactions()`, so the whole test needs a Testcontainers broker.
- B. After `commitTransaction()`, `history()` returns the 3 records, `consumerGroupOffsetsHistory()` returns the offsets that were passed to `sendOffsetsToTransaction`, and `commitCount()` confirms exactly one committed transaction.
- C. After `commitTransaction()`, `uncommittedRecords()` returns the 3 records and `uncommittedOffsets()` returns the offsets.
- D. `flushed()` returns `true` only once the offsets have been committed transactionally, and `history()` covers the records.

### Question 48 — `[FUND · Timestamps and retention · Single]`

One producer host has a clock that is 9 hours ahead. On Kafka 3.7 its records were accepted, and the log segments holding them stopped being removed by time-based retention. After the brokers were upgraded to 4.3, the same producer now fails with `InvalidTimestampException`. Which statement explains both behaviours?

- A. The upgrade set `log.message.timestamp.difference.max.ms=0`, which rejects any clock skew at all; there is no supported way to keep accepting a skewed producer.
- B. Time-based retention always uses the broker's append time, so the stuck segments must have had an unrelated cause such as an open file handle.
- C. With `message.timestamp.type=CreateTime` (the default) the broker stores the producer's timestamp, and time-based retention uses the largest timestamp in a segment — so a future-dated record pins the whole segment. Kafka 4.0 changed `message.timestamp.after.max.ms` from unlimited to **3,600,000 ms**, so records more than an hour ahead of broker time are now rejected; setting `message.timestamp.type=LogAppendTime` on the topic makes the broker stamp records itself.
- D. `message.timestamp.before.max.ms` defaults to one hour and is the setting that now rejects the record; `after.max.ms` remains unlimited.

### Question 49 — `[DEV · Partitioner · Multi — Choose 2]`

A service sends records with `null` keys to a 30-partition topic using the Kafka 4.3 defaults, and is considering switching to a `tenantId` key. Which two statements are correct? (Choose two.)

- A. With a `null` key the built-in partitioner sticks to one partition until that partition's batch is sent (`batch.size` reached or `linger.ms` elapsed) and then switches, so bursts of consecutive records share a partition while the long-run distribution stays roughly even.
- B. With a non-null key the partition is `murmur2(keyBytes) % numPartitions`, which is deterministic and identical across producer instances — but raising the partition count later remaps existing keys and breaks per-key ordering across the change.
- C. With a `null` key the producer round-robins strictly, record by record, across all 30 partitions.
- D. `partitioner.class` has no default in 4.3 and must be set explicitly once the topic has more than 16 partitions.
- E. Key-based partitioning applies only when `partitioner.ignore.keys=false` **and** the topic has fewer than 128 partitions; above that the producer falls back to the sticky partitioner.

### Question 50 — `[OBS · Producer metrics · Single]`

A producer writes 300-byte records to a 3-partition topic. Its configuration is the 4.3 default except `compression.type=snappy` and an explicit `linger.ms=0` added by the team "for lowest latency". Metrics:

```
batch-size-avg          = 310 bytes   (batch.size = 16,384)
records-per-request-avg = 1.1
record-queue-time-avg   = 0.4 ms
request-rate            = 9,100 /s
compression-rate-avg    = 0.99
buffer-available-bytes  = 33,100,000
```

Broker network threads are saturated. Which change gives the largest improvement for the smallest latency cost?

- A. Raise `batch.size` to 1 MB so that each request carries far more records.
- B. Raise `buffer.memory` to 128 MB, because the accumulator is clearly the bottleneck.
- C. Set `compression.type=none`: snappy on 300-byte records wastes CPU and is what drives the request rate up.
- D. Remove the `linger.ms=0` override (or set 10–20 ms): with no linger every record becomes its own request, which is why `batch-size-avg` equals one record and snappy has nothing to compress. A few milliseconds of linger collapses the request rate by an order of magnitude and makes compression effective.

### Question 51 — `[STREAMS · application.id · Multi — Choose 2]`

After a bad release, an operator "starts clean" by changing `application.id` from `fraud-scoring-v1` to `fraud-scoring-v2` and restarting all instances. Input topics are unchanged. Which two consequences are correct? (Choose two.)

- A. Changing `application.id` affects only metrics and the `client.id` prefix; offsets and state are keyed by topology, not by application id.
- B. `application.id` is also the consumer `group.id`, so the new group has no committed offsets and starts from the beginning of the input topics — Streams overrides `auto.offset.reset` to `earliest`.
- C. The existing changelog topics are renamed automatically to the new prefix, so state is preserved and startup is fast.
- D. Streams refuses to start unless `application.server` is changed at the same time.
- E. Every internal topic is prefixed with `application.id`, so brand-new repartition and changelog topics are created and every state store is rebuilt from scratch; the `fraud-scoring-v1-*` topics remain behind and must be deleted manually.

### Question 52 — `[DEV · Producer metadata · Single]`

A service deployed to staging fails on its very first `send()`:

```
org.apache.kafka.common.errors.TimeoutException: Topic orders-v2 not present in metadata after 60000 ms.
```

The topic exists on the **development** cluster, where the service was tested. The staging brokers are reachable from the pod, have `auto.create.topics.enable=false`, and `kafka-topics.sh --bootstrap-server <staging> --list` does not include `orders-v2`. Which statement identifies the timeout and the cause?

- A. 60,000 ms is `max.block.ms`: `send()` blocks waiting for metadata for a topic that does not exist on the cluster it is bootstrapped to, and with auto-creation disabled the broker never creates it. Create the topic on staging (or fix `bootstrap.servers`).
- B. 60,000 ms is `request.timeout.ms`, whose default is 60,000; raise it so the metadata request has time to complete.
- C. 60,000 ms is `delivery.timeout.ms`, whose default is 60,000; the record could not be delivered because the partition has no leader.
- D. 60,000 ms is `metadata.max.age.ms`, whose default is 60,000; the producer's cached metadata is stale, so call `producer.flush()` to force a refresh.

### Question 53 — `[FUND · Client compatibility · Single]`

A legacy Java application pinned to `kafka-clients:0.10.2.1` can no longer connect after the cluster is upgraded to 4.3; it fails during API version negotiation. Applications on 3.x clients are unaffected. Which statement is correct?

- A. Set `inter.broker.protocol.version=0.10.2` on the brokers and the old client will work again.
- B. Kafka 4.0 removed the old protocol API versions and raised the supported client baseline to **2.1** (KIP-896), so brokers no longer serve requests from clients older than 2.1; the application's client library must be upgraded.
- C. Set `message.format.version=0.10.2` on the topics the old client uses; that restores down-conversion for legacy clients.
- D. This is a TLS problem: 0.10.x clients cannot negotiate TLS 1.2, which 4.x brokers require.

### Question 54 — `[CONNECT · Error handling · Single]`

A JDBC sink connector is configured with:

```
errors.tolerance=all
errors.deadletterqueue.topic.name=dlq-payments
errors.deadletterqueue.context.headers.enable=true
```

It nevertheless dies with:

```
ERROR [payments-sink|task-0] WorkerSinkTask{id=payments-sink-0} Task threw an uncaught and
unrecoverable exception. Task is being killed and will not recover until manually restarted.
org.apache.kafka.connect.errors.ConnectException: Tolerance exceeded in error handler
  at org.apache.kafka.connect.runtime.errors.RetryWithToleranceOperator.execAndHandleError(...)
Caused by: java.sql.SQLIntegrityConstraintViolationException: Duplicate entry '80412' for key 'PRIMARY'
```

`dlq-payments` is empty. Why did `errors.tolerance=all` not save the task?

- A. `errors.deadletterqueue.topic.replication.factor` was not set, so the DLQ topic was never created and every failure escalated.
- B. `errors.tolerance=all` only takes effect together with `errors.retry.timeout=-1`; without it the tolerance counter is zero.
- C. The error-handling framework covers the stages the **framework** executes — the converters, the SMT chain, and `SinkTask.put()` only for exceptions the connector declares as `RetriableException`. A non-retriable failure inside the target system, such as this primary-key violation, is the connector's own concern: the task fails and nothing is routed to the DLQ. Fix the data or switch the connector to an upsert insert mode.
- D. Dead letter queues exist only for source connectors; sinks must rely on `errors.log.enable=true` and manual replay.

### Question 55 — `[DEV · read_committed and LSO · Single]`

An upstream service writes to `settlements` with a transactional producer that commits once every 5 minutes. A downstream consumer uses `isolation.level=read_committed`. A monitoring job computes lag as `endOffsets(tp) - committed(tp)` using a client configured the same way, and the consumer's own `records-lag-max` is also near zero — yet records reach the application in 5-minute bursts and the business reports a 5-minute delay. Which statement is correct?

- A. `records-lag-max` is only populated for `read_uncommitted` consumers, so the zero is a placeholder and the external calculation simply inherited it.
- B. Records from aborted transactions make the arithmetic produce a negative value, which both the metric and the job clamp to zero.
- C. The monitoring job should switch to `read_uncommitted` to measure lag correctly, and the consumer should do the same so that it stops waiting for commits.
- D. For a `read_committed` client, `endOffsets()` returns the **last stable offset** — the first offset of the earliest still-open transaction — not the high watermark. While the upstream transaction is open the LSO does not advance, so lag reads zero by construction even though records are already on the broker; the delay is the upstream commit interval.

### Question 56 — `[FUND · Leader election · Ordering]`

A partition leader fails on a Kafka 4.3 cluster where Eligible Leader Replicas are enabled and `unclean.leader.election.enable=false`. Put the candidate sources the controller considers in the order it tries them.

| # | Candidate |
|---|---|
| 1 | A replica listed in the partition's **Eligible Leader Replicas (ELR)** set |
| 2 | Any surviving replica, including one that was never in the ISR — only possible once unclean leader election is enabled |
| 3 | A replica currently in the **ISR** |
| 4 | The **last known leader**, once it comes back online |

- A. 1 → 3 → 4 → 2
- B. 3 → 4 → 1 → 2
- C. 3 → 1 → 4 → 2
- D. 3 → 1 → 2 → 4

### Question 57 — `[DEV · Transactions · Multi — Choose 2]`

A consume-transform-produce service must not emit duplicate output and must not lose the input offsets it has accounted for. The code already calls `initTransactions()`, `beginTransaction()`, `send()` and `commitTransaction()`. Which two additional requirements are mandatory? (Choose two.)

- A. Commit the input offsets with `producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata())` inside the transaction, and set `enable.auto.commit=false` on the input consumer, because an automatic commit would record offsets outside the transaction.
- B. Each instance must generate a fresh random `transactional.id` at startup so that two instances can never collide on the same id.
- C. The **input** consumer must use `isolation.level=read_committed`, because that is what allows its offsets to be committed transactionally.
- D. Downstream consumers must set `isolation.level=read_committed`; with the default `read_uncommitted` they read records that belong to transactions which were later aborted.
- E. `enable.idempotence=true` must be set explicitly, because configuring a `transactional.id` does not imply it.

### Question 58 — `[OBS · Consumer lag alerting · Single]`

An alert fires on the Prometheus series `kafka_consumer_fetch_manager_records_lag_max`. During a 40-minute outage in which every pod of the `settlement` group sat in `CrashLoopBackOff`, the alert never fired; the team learned about the backlog only from a downstream SLA breach. Which statement explains the gap and names the right signal?

- A. `records-lag-max` is a client-side JMX metric derived from the consumer's own fetch position, so when no consumer is running there is nothing to scrape and the series simply disappears rather than growing. Lag for a group that may be absent has to be computed broker-side from the group's **committed** offsets against the log end offsets (`kafka-consumer-groups.sh --describe`, `AdminClient.listConsumerGroupOffsets` plus `endOffsets`, or a lag exporter), and the alert must also fire on the **absence** of group members.
- B. `records-lag-max` reports 0 while a consumer is down, which is why the threshold was never crossed; alert on `records-lead-min` instead, which keeps reporting.
- C. Consumer lag metrics are only published when the group runs with `group.protocol=consumer`; the classic protocol reports lag only through the CLI.
- D. `offsets.retention.minutes` removed the group's committed offsets during the outage, so its lag genuinely was zero for the whole window.

### Question 59 — `[FUND · acks · Multi — Choose 2]`

A telemetry pipeline that can tolerate losing records sets `acks=0` and `enable.idempotence=false` for maximum throughput. Which two statements about this producer are correct? (Choose two.)

- A. `acks=0` is rejected at startup unless `retries=0` is also set explicitly.
- B. The send callback still runs, but `RecordMetadata.offset()` returns **-1**, because the broker sends no response from which an offset could be read.
- C. The producer does not retry broker-side failures for these records, because it never learns about them; only client-side failures such as serialization errors or buffer exhaustion surface to the application.
- D. Per-partition ordering is still guaranteed across a leader change, because unsent batches stay queued in the accumulator until the new leader is known.
- E. With `acks=0` the record is written to the leader's page cache before `send()` returns, so only an OS-level crash can lose it.

### Question 60 — `[DEV · auto.offset.reset · Single]`

A reconciliation consumer is configured with `auto.offset.reset=none` so that it "can never silently skip or reprocess data". Its very first deployment, with the brand-new `group.id=recon-v3`, crashes at startup:

```
org.apache.kafka.clients.consumer.NoOffsetForPartitionException:
Undefined offset with no reset policy for partitions: [ledger-0, ledger-1, ledger-2]
```

Which statement is correct?

- A. `none` is only valid together with `assign()`; a consumer that calls `subscribe()` must use `earliest` or `latest`.
- B. `auto.offset.reset` is consulted when the group has **no committed offset** for a partition or when its committed offset is **out of range**. `none` makes both cases throw, which is the intended safety net — a brand-new group must therefore have its starting offsets seeded deliberately, with `seek()`/`seekToBeginning()` in a rebalance listener or with `kafka-consumer-groups.sh --reset-offsets`.
- C. The exception means the topic does not exist yet; once it is created the reset policy is no longer consulted.
- D. Setting `enable.auto.commit=true` makes the consumer write initial offsets at startup, which removes the exception without changing the safety property.

---

> ✅ Hết giờ? Chấm bài ở [answers.md](answers.md) và điền bảng điểm theo domain trước khi xem giải thích.
