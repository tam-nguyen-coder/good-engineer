# 🎯 CCDAK Mock Exam 03 — 60 questions · 90 minutes

> **Exam-realistic full-length mock.** Distribution follows the official CCDAK domain weights.
> ⏱️ Set a timer for **90 minutes** (~90 seconds per question). No notes, no documentation, no pausing.
> 🔒 Answers, explanations and per-domain scoring: [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (4 options) · `Multi` (choose the stated number) · `Matching` · `Ordering`.
> Tag: `[Domain · Topic · Format]`. Domains: `DEV` `FUND` `CONNECT` `OBS` `STREAMS` `TEST`.
> Anchored to **Apache Kafka 4.3** — where a default changed in 3.0/4.0, the current value is correct.
> 🎚️ **Focus of this mock: design and trade-offs.** In most questions every option would *work*; the qualifier in the stem — *MOST cost-effective*, *FEWEST changes*, *without changing the producer*, *while preserving per-key ordering*, *survive the loss of one broker* — is what makes exactly one option right. Read the qualifier before the options.
> Back to [mock index](../README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

---

### Question 1 — `[FUND · Durability vs availability · Single]`

A trading platform runs the topic `trades` with RF=3, `min.insync.replicas=2` and producers at `acks=all` on Kafka 4.3. A rack failure takes two of the three replicas of partition 7 offline at the same time and writes to that partition stop. The risk committee states its position in one sentence: *"A twenty-minute write outage on this topic is acceptable; silently losing a trade we already acknowledged is not."* All four options below are valid Kafka settings. Which one matches that statement?

- A. Set `unclean.leader.election.enable=true` on `trades` so a replica that is behind can take leadership the moment the ISR empties
- B. Lower `min.insync.replicas` to `1` on `trades` so the surviving leader keeps accepting writes on its own
- C. Change nothing about availability: keep `unclean.leader.election.enable=false` and confirm `eligible.leader.replicas.version=1` is active. Writes stay blocked while the ISR is below 2, but if the last in-sync leader also fails the controller can still elect a replica recorded in the partition's ELR set, because the high watermark cannot advance while `|ISR| < min.insync.replicas`
- D. Set `acks=1` on the producers so a write no longer depends on the size of the ISR

### Question 2 — `[DEV · Producer latency · Single]`

A card-authorisation producer on Kafka 4.3 uses defaults except `compression.type=zstd`. The topic is RF=3 with `min.insync.replicas=2` and the producer uses `acks=all`. Measured p99 for `send()`→ack is **38 ms** against a budget of **30 ms**. Client metrics: `record-queue-time-avg` **12 ms**, `request-latency-avg` **22 ms**, `batch-size-avg` **2.1 KB**, `buffer-available-bytes` steady near 32 MB. The requirement is to cut p99 **without weakening the guarantee that an acknowledged record survives the loss of one broker**. Which change does that?

- A. Nothing can be gained from `linger.ms`: it defaults to `0`, so the accumulator already flushes on every `send()` and the 12 ms must be network time
- B. Set `acks=1`; the leader alone acknowledges, which removes the replication round trip from the critical path
- C. Raise `batch.size` from 16,384 to 1,048,576 so fewer produce requests are needed
- D. Set `linger.ms=0`. The 4.x default is **5 ms**, and 12 ms of queue time confirms records are waiting for batch-mates; `acks`, `min.insync.replicas` and RF are untouched. The price is smaller batches, more requests and a worse compression ratio

### Question 3 — `[CONNECT · Tool selection · Single]`

A team must land every record of `orders` into Amazon S3 as Parquet files partitioned by event date, with retries and offset tracking. They already operate a three-worker **distributed Connect cluster** for two other pipelines. The requirement is to ship this with the **fewest lines of code the team has to own** and **without adding a new runtime service**. All four options work.

- A. Write a Java consumer that uses `assign()`, buffers records in memory and uploads with the AWS SDK
- B. Write a Kafka Streams application that calls `foreach()` and uploads each buffer to S3
- C. Configure the Amazon S3 sink connector on the existing distributed Connect cluster, with a field partitioner for the event date — no application code, and retries, DLQ and offset management come from the framework
- D. Create a Lambda event source mapping on the topic and write the Parquet upload inside the function

### Question 4 — `[OBS · Consumer lag · Ordering]`

A consumer group's lag rises monotonically. Order the four steps below the way a team should attempt them — **cheapest and least irreversible first**.

| # | Step |
|---|---|
| 1 | Increase the topic's partition count so the group can grow past its current ceiling |
| 2 | Check whether the lag sits on a few partitions only, which would point to key skew rather than to a shortage of capacity |
| 3 | Add consumer instances up to the number of partitions so every partition has its own member |
| 4 | Profile the per-record path and batch the downstream writes so each record costs less |

- A. 3 → 1 → 4 → 2
- B. 2 → 3 → 4 → 1
- C. 1 → 3 → 2 → 4
- D. 3 → 2 → 1 → 4

### Question 5 — `[STREAMS · Table type · Single]`

A Streams application enriches `transactions` (48 partitions, keyed by `accountId`, 90,000 records/s) with `accounts` (48 partitions, keyed by `accountId`, 40 million records, about 60 GB on disk). Both topics are produced by the same service with the default partitioner. The application will run on 6 instances and the requirement is to **minimise the state each instance has to hold**. Both table types would produce correct results.

- A. Read `accounts` as a `GlobalKTable` and join with a `KeyValueMapper`, so no co-partitioning is needed
- B. Read `accounts` as a `KTable` and use a `KStream`-`KTable` join: the two topics are already co-partitioned, so each instance materialises only its share of the 60 GB — roughly 10 GB — instead of the whole table
- C. Read `accounts` as a `KTable` and use a foreign-key `KTable`-`KTable` join so Streams handles the distribution internally
- D. Repartition `transactions` to 6 partitions so the join state fits one instance per partition

### Question 6 — `[DEV · Ordering vs parallelism · Single]`

The topic `positions` has **12 partitions** and every record is keyed by `accountId`. A consumer group of **4 instances** is falling behind. Per-`accountId` ordering is a hard requirement, the **producer must not be changed**, and the **partition count must stay at 12**. All four options are things teams really do.

- A. Scale the group to 12 instances so each member owns exactly one partition; the key-to-partition mapping is untouched, so per-account ordering is unaffected and no code changes at all are needed
- B. Convert the group to a share group so all instances can read from every partition
- C. Raise `max.poll.records` from 500 to 5,000 so each poll does more work
- D. Give each instance its own `group.id` so they stop competing for partitions

### Question 7 — `[TEST · Schema testing · Single]`

A unit test must prove that a consumer configured with Avro schema **v2** (one added field with a default) can deserialize bytes that were produced with schema **v1**. It must run in milliseconds, must not require Docker, and must not write anything to the shared Schema Registry. All four options are real techniques.

- A. Start `confluentinc/cp-schema-registry` with Testcontainers and register both versions against a throwaway subject
- B. Use `MockProducer` and `MockConsumer` with `StringSerializer`/`StringDeserializer` and compare the JSON strings
- C. Point both `KafkaAvroSerializer` and `KafkaAvroDeserializer` at `schema.registry.url=mock://compat-test`, which resolves to an in-process mock registry client scoped to that name; register v1, serialize, then deserialize with the v2 reader schema and assert the defaulted field
- D. Use `TopologyTestDriver`, because it is the standard harness whenever serdes are involved

### Question 8 — `[FUND · Share groups · Single]`

A team converts `payment-instructions` (12 partitions, keyed by `accountId`) from a consumer group to a **share group** so they can run 40 workers instead of 12. Within a day, support reports that a *cancel* instruction is occasionally applied **before** the *create* instruction it cancels, for the same account. All four statements describe real Kafka behaviour.

- A. The share group needs `share.isolation.level=read_committed`; the reordering comes from reading uncommitted transactional records
- B. `share.record.lock.duration.ms` (default 30,000 ms) is too short, so records are released and redelivered out of order; raise it to 60,000 ms
- C. Set `share.delivery.count.limit=1` so no record is ever delivered twice, which removes the reordering
- D. Share groups trade ordering for sharing: a partition may be assigned to several members at once and records are acquired individually, so two instructions for one account can be processed concurrently. Ordering per `accountId` requires a **consumer group**, where a partition has exactly one owner — so either cap the group at 12 members or raise the partition count to raise the ceiling

### Question 9 — `[DEV · Exactly-once end-to-end · Ordering]`

A pipeline runs: PostgreSQL → (service) → Kafka → Kafka Streams → Kafka → (consumer) → DynamoDB. Management asks for "exactly-once end to end". Order the four changes below by the **hop they fix**, following the data path from the source database to the external sink.

| # | Change |
|---|---|
| 1 | Make the DynamoDB write idempotent — a conditional `PutItem` keyed by the event id — because a Kafka transaction cannot span an external system |
| 2 | Replace the service's dual write to PostgreSQL and Kafka with an outbox table published by a CDC source connector |
| 3 | Set `processing.guarantee=exactly_once_v2` on the Streams stage |
| 4 | Set `isolation.level=read_committed` on every consumer that reads the output of a transactional writer |

- A. 1 → 2 → 3 → 4
- B. 2 → 4 → 3 → 1
- C. 2 → 3 → 4 → 1
- D. 3 → 2 → 1 → 4

### Question 10 — `[CONNECT · Schema evolution · Ordering]`

The subject `shipments-value` is set to **`FORWARD`** compatibility. The next schema version adds an optional field and removes a field that has a default. Order the four deployment steps so the pipeline keeps working at every moment.

| # | Step |
|---|---|
| 1 | Register the new schema version against the subject |
| 2 | Roll out the **producers** so they start writing the new schema |
| 3 | Roll out the **consumers** so they use the new schema |
| 4 | Validate the candidate schema against the subject without registering it |

- A. 4 → 1 → 2 → 3
- B. 4 → 1 → 3 → 2
- C. 1 → 4 → 3 → 2
- D. 4 → 3 → 1 → 2

### Question 11 — `[FUND · Delivery semantics · Matching]`

Match each consumer arrangement to the guarantee it actually delivers.

| # | Arrangement |
|---|---|
| 1 | Offsets are committed as soon as `poll()` returns, before the records are processed |
| 2 | Offsets are committed after processing, once the side effects are durable |
| 3 | The output records and the consumed offsets are written in one Kafka transaction, and downstream readers use `isolation.level=read_committed` |
| 4 | Offsets are committed after processing, and each event id is written to the sink inside the sink's own transaction so replays are discarded |

| Letter | Guarantee |
|---|---|
| W | At-least-once, with duplicates absorbed at the sink (effectively-once) |
| X | At-most-once |
| Y | At-least-once |
| Z | Exactly-once within Kafka |

- A. 1-Y · 2-X · 3-Z · 4-W
- B. 1-X · 2-W · 3-Z · 4-Y
- C. 1-Z · 2-Y · 3-X · 4-W
- D. 1-X · 2-Y · 3-Z · 4-W

### Question 12 — `[DEV · Exactly-once scope · Multi — Choose 2]`

A service on Kafka 4.3 reads `orders`, applies a pricing function, writes to `priced-orders`, **and** inserts one audit row into PostgreSQL per record. The requirement is worded as "guarantee no duplicates across restarts". Which **two** statements are correct? (Choose two.)

- A. `enable.idempotence=true` — already the default in 4.x — also removes duplicates across producer **restarts**, because the producer id is derived from `client.id` and survives the restart
- B. Wrapping the read and the `priced-orders` write in one transaction, including `sendOffsetsToTransaction(offsets, consumer.groupMetadata())`, removes duplicates on the **Kafka** hop, provided downstream consumers set `isolation.level=read_committed`
- C. Setting `isolation.level=read_committed` on this service's own consumer removes the duplicates this service produces
- D. The PostgreSQL audit row is **not** covered by the Kafka transaction; it has to be made idempotent on its own, for example `INSERT ... ON CONFLICT (event_id) DO NOTHING`
- E. Generating a fresh random `transactional.id` at every start-up keeps fencing intact while avoiding `ProducerFencedException`

### Question 13 — `[OBS · Metric selection · Single]`

A platform team must raise an alert when a consumer pipeline is **about to lose records that retention will delete before they are read**. All four are real metrics that the team already scrapes. Which one is the correct trigger?

- A. `records-lag-max` crossing a fixed absolute threshold
- B. `records-lead-min` approaching **0** — lead is the distance between the consumer's position and the partition's **log start offset**, so a lead near zero means the retention cleaner is about to overtake the consumer
- C. `UnderReplicatedPartitions > 0` on any broker
- D. `time-between-poll-avg` approaching `max.poll.interval.ms`

### Question 14 — `[STREAMS · Joins · Single]`

`impressions` and `clicks` are both 24-partition topics keyed by `adId` and written by the same service. The requirement: emit an enriched record for every click that has a matching impression **within the previous 30 minutes**, and also emit clicks that never matched — but only once it is certain no match will arrive. All four compile.

- A. `clicks.join(impressionsTable, joiner)` — a `KStream`-`KTable` join, which needs no window because the table always holds the latest impression
- B. `clicks.leftJoin(impressionsGlobalTable, keyMapper, joiner)` — a `GlobalKTable` join, so no co-partitioning is required
- C. A foreign-key `KTable`-`KTable` join between the two topics read as tables
- D. `clicks.leftJoin(impressions, joiner, JoinWindows.ofTimeDifferenceAndGrace(Duration.ofMinutes(30), Duration.ofMinutes(5)))` — a windowed `KStream`-`KStream` left join; the unmatched clicks are emitted only after the grace period closes the window

### Question 15 — `[FUND · Partition sizing · Single]`

A new topic must sustain **600 MB/s** of ingress. Each consumer instance can process at most **15 MB/s**, the cluster has **12 brokers** and will stay at 12 for the next year, and the p99 end-to-end budget is 100 ms. Records are keyed and per-key ordering matters, so the partition count should not be changed later. What is the best starting partition count?

- A. **12** — one partition per broker, which keeps leadership perfectly balanced
- B. **48** — the consumer side needs at least 600 ÷ 15 = 40 members, and a consumer group cannot exceed one member per partition, so 40 is the parallelism floor; rounding up to 48 keeps it a multiple of 12 for even leadership and leaves headroom, while going far beyond that adds per-partition overhead and lengthens leader election
- C. **600** — one partition per MB/s of ingress, so a partition never becomes a bottleneck
- D. **6** — fewer partitions always means lower end-to-end latency, and consumers can be made faster later

### Question 16 — `[DEV · assign vs subscribe · Single]`

A nightly reconciliation job must re-read **exactly partition 3** of `ledger` from offset 1,000,000 to the end. It must not disturb the production consumer group, must not appear in that group's membership or lag output, and must not leave offsets behind. All four options run.

- A. `subscribe()` with a fresh `group.id` and `auto.offset.reset=earliest`, then `seek()` to the offset
- B. `subscribe()` with the production `group.id` and `seek()` on partition 3
- C. `assign(List.of(new TopicPartition("ledger", 3)))` followed by `seek(tp, 1_000_000L)`, with no `group.id` — there is no group membership, no rebalance and nothing written to `__consumer_offsets`; the trade-off is that the job gets no broker-side lag reporting and owns its own failover
- D. Create a share group on `ledger` and reset its start offset with `kafka-share-groups.sh --reset-offsets`

### Question 17 — `[CONNECT · SMT boundaries · Single]`

A JDBC source connector pulls rows from four tables. The pipeline must (1) drop the `ssn` column, (2) rename `cust_id` to `customerId`, (3) publish each table to `cdc.<table>` instead of the connector's default `jdbc-<table>`, and (4) attach each customer's display name, which lives in a separate `customers` topic. The team wants the **fewest moving parts**.

- A. All four steps as a chain of SMTs on the source connector
- B. Replace the converter with one that performs the projection and the lookup
- C. Write a custom source connector that does all four inside `poll()`
- D. Steps (1)–(3) as SMTs on the source connector — `ReplaceField$Value` with `exclude` and `renames`, plus `RegexRouter` — and step (4) as a separate Kafka Streams or ksqlDB job, because an SMT is per-record and stateless and cannot join two topics

### Question 18 — `[TEST · Test pyramid · Multi — Choose 2]`

Two behaviours must be covered, both without Docker: **(1)** a custom `Partitioner` sends every record whose key starts with the same tenant prefix to the same partition of a 12-partition topic; **(2)** a windowed aggregation emits its final result only after the grace period has passed. Which **two** approaches fit? (Choose two.)

- A. For (1), build `new MockProducer<>(cluster, true, customPartitioner, keySerializer, valueSerializer)` with a `Cluster` that declares 12 partitions, send one record per tenant key, and assert the `partition()` on each returned `RecordMetadata`
- B. For (1), run Testcontainers with a real 12-partition topic and read the records back to see where they landed
- C. For (2), use `TopologyTestDriver`: pipe records with explicit timestamps, advance stream time past the window end plus the grace period, then assert on the `TestOutputTopic`
- D. For (2), use `MockConsumer` and `addRecord()` with timestamps beyond the window
- E. For (2), use Testcontainers with `apache/kafka-native`, because window closing depends on the broker's clock

### Question 19 — `[DEV · Design patterns · Matching]`

Match each design pattern to the problem it exists to solve.

| # | Pattern |
|---|---|
| 1 | Transactional outbox published by CDC |
| 2 | Claim-check |
| 3 | Idempotent consumer with a processed-event table |
| 4 | Non-blocking retry topics |

| Letter | Problem |
|---|---|
| W | A downstream dependency is intermittently unavailable and retrying in place would blow past `max.poll.interval.ms` |
| X | A record's payload is larger than the cluster will accept |
| Y | A service writes to its database and to Kafka, and the two disagree after a crash |
| Z | The pipeline is at-least-once and the sink must not apply the same effect twice |

- A. 1-Z · 2-X · 3-Y · 4-W
- B. 1-Y · 2-X · 3-Z · 4-W
- C. 1-Y · 2-W · 3-Z · 4-X
- D. 1-X · 2-Y · 3-W · 4-Z

### Question 20 — `[FUND · Topic design · Single]`

A new service must know the **current** shipping address of each of 20 million customers at start-up, sourced from Kafka, **without adding a database**. Addresses change about 1,000 times per second. The team wants storage that grows with the number of *customers*, not with the number of *updates*, and deletions must be visible to consumers that are up to 24 hours behind. All four configurations are legal.

- A. `cleanup.policy=delete` with `retention.ms=-1`, so nothing is ever removed and the service replays the full history at start-up
- B. `cleanup.policy=compact,delete` with `retention.ms=604800000`
- C. `cleanup.policy=compact`, with deletions published as tombstones (null value). Storage stays proportional to the key space and the service bootstraps by reading from offset 0. The constraint to design around is `delete.retention.ms` — 24 hours by default — after which a tombstone may be cleaned, so a consumer that lags longer than that will miss the deletion
- D. Leave the topic as it is and read it with a share group so each record is delivered once

### Question 21 — `[OBS · Producer failures · Single]`

A high-volume producer starts logging:

```
WARN  o.a.k.c.p.internals.Sender - [Producer clientId=ingest-7] Got error produce response with
  correlation id 84213 on topic-partition events-11, retrying (2147483646 attempts left).
  Error: NOT_ENOUGH_REPLICAS
ERROR o.a.k.c.p.internals.ErrorLoggingCallback -
  org.apache.kafka.common.errors.TimeoutException: Expiring 42 record(s) for events-11:120001 ms
  has passed since batch creation
```

At the same moment the broker dashboard shows `UnderMinIsrPartitionCount` = 4, `UnderReplicatedPartitions` = 37, `OfflinePartitionsCount` = 0, `ActiveControllerCount` = 1. The topic is RF=3 with `min.insync.replicas=2` and the producer uses `acks=all` with default timeouts. Which reading is correct?

- A. The producer is misconfigured: `delivery.timeout.ms` is too low and should be raised above 120,000 ms so the retries have time to succeed
- B. A broker hosting replicas of those partitions is down or lagging. The ISR has shrunk below `min.insync.replicas=2`, so the leader rejects `acks=all` writes with the **retriable** `NOT_ENOUGH_REPLICAS`; the producer retries until `delivery.timeout.ms` (120,000 ms) expires and the batch is failed. `OfflinePartitionsCount=0` shows leaders still exist, so the fix belongs on the broker side, not in the client config
- C. `acks=all` waits for all three replicas, so any single slow follower produces this error; setting `acks=2` fixes it
- D. `UnderReplicatedPartitions=37` with `OfflinePartitionsCount=0` means the controller has lost the metadata quorum; restart the controllers

### Question 22 — `[STREAMS · Exactly-once trade-off · Single]`

A Streams application is moving from `processing.guarantee=at_least_once` to `exactly_once_v2`. The team wants to know what else changes before they schedule the rollout. All four statements sound plausible.

- A. `commit.interval.ms` switches from **30,000** to **100**, so the application commits a transaction roughly ten times a second: end-to-end latency for `read_committed` readers improves, but the broker takes on far more commit and transaction-marker traffic. The cluster also needs at least three brokers, because `transaction.state.log.replication.factor` defaults to 3
- B. Nothing else changes; EOS v2 is a pure correctness improvement with no operational cost
- C. EOS v2 requires `num.standby.replicas ≥ 1`, because a task's state must be recoverable before a transaction can be committed
- D. `commit.interval.ms` rises from 30,000 to 100,000 so that fewer, larger transactions are committed

### Question 23 — `[DEV · Retry design · Multi — Choose 2]`

An order-fulfilment consumer calls a warehouse API that returns HTTP 503 during outages lasting up to **10 minutes**. Per-`orderId` ordering is a hard requirement, and the team is **not allowed to add a new service or a new topic**. Which **two** designs satisfy both constraints? (Choose two.)

- A. Publish each failed record to `orders-retry-1` and move on; ordering survives because the record keeps its original key
- B. Retry in place but keep the poll loop alive: on failure call `pause()` on that partition, keep calling `poll()` (paused partitions return nothing, so heartbeats and `max.poll.interval.ms` stay healthy) and `resume()` after the backoff. Ordering is preserved; the cost is head-of-line blocking on that partition
- C. Run the retry logic as a second consumer group on the same topic so retries proceed in parallel with the main flow
- D. Raise `max.poll.interval.ms` comfortably above the worst-case retry budget and retry inside the processing loop — the smallest change of all, paid for with slower detection of a genuinely stuck consumer
- E. Convert the group to a share group so a failed record is `RELEASE`d and redelivered to another worker

### Question 24 — `[CONNECT · CDC design · Single]`

Every committed row change in a vendor-supplied ordering application's PostgreSQL database must become a Kafka event. No event may exist for a rolled-back transaction and no committed change may be lost. **The team cannot change the vendor application in any way** — not its code, not its schema, not its write path. All four designs are used in production somewhere.

- A. Transactional outbox: insert the event into an `outbox` table inside the same transaction as the business write, and publish the outbox with a CDC connector
- B. Point a Debezium PostgreSQL source connector at the business tables themselves and unwrap the change envelope with `ExtractNewRecordState`. Nothing in the application changes; the price is that downstream consumers are now coupled to the vendor's internal table schema, which the outbox pattern would have shielded them from
- C. Add a database trigger that calls a Kafka producer with a `transactional.id` so the send is part of the database transaction
- D. Poll the tables on a schedule with `SELECT ... WHERE updated_at > ?` and publish whatever comes back

### Question 25 — `[FUND · Replication design · Multi — Choose 2]`

A cluster review covers a 4.3 cluster with RF=3, `min.insync.replicas=2` set at cluster level, `acks=all`, `unclean.leader.election.enable=false` and ELR enabled. Which **two** statements about this configuration are correct? (Choose two.)

- A. Losing one broker keeps writes available; losing two brokers that host replicas of the same partition stops writes for that partition but does not lose any acknowledged record
- B. Any change to `min.insync.replicas` — even re-applying the same value — leaves the ELR state of the affected partitions untouched
- C. With ELR enabled the controller may elect a replica that is **no longer in the ISR**, provided it is recorded in the partition's ELR set; those replicas are safe because the high watermark cannot advance while the ISR is smaller than `min.insync.replicas`
- D. `min.insync.replicas` should be raised to 3 to match RF=3, which is the strongest durability setting for this topic
- E. Enabling ELR makes `unclean.leader.election.enable=true` safe, because ELR guarantees the elected replica is complete

### Question 26 — `[DEV · Partitioning strategy · Single]`

A multi-tenant metrics topic has 30 partitions. Records of one tenant must spread across partitions for throughput, but every record of one `(tenantId, metricName)` pair must stay ordered. Two producer applications write to the topic — one in Java, one in Node.js — and they are owned by different teams. The requirement is to make both agree on the mapping with the **smallest amount of logic the two teams must keep in sync**. All four options can be implemented.

- A. Compute `Math.abs(hash(tenantId + metricName)) % 30` in each application and set the `partition` explicitly on every `ProducerRecord`
- B. Write a custom `Partitioner` class and deploy it in both applications
- C. Set the record key to the composite `tenantId + "|" + metricName` and let the default partitioner hash it. `murmur2` is part of the client contract and is implemented identically by every mainstream client, so the two applications agree with no shared code at all — as long as the partition count is never changed
- D. Leave the key null so the sticky partitioner spreads records evenly, and put the ordering key in a header

### Question 27 — `[OBS · Metric semantics · Multi — Choose 2]`

A team is writing the SLO dashboard for a Kafka pipeline. Which **two** of their statements are correct? (Choose two.)

- A. `records-lag-max` is a broker-side metric, so it is available for every consumer without instrumenting the client
- B. The client's `records-lag-max` is computed from the consumer's **current position**, while `kafka-consumer-groups.sh --describe` computes LAG from the **committed** offset — so with auto-commit every 5 s the CLI can report more lag than the client does
- C. `UnderReplicatedPartitions > 0` is an availability alarm, while `OfflinePartitionsCount > 0` is only a redundancy warning
- D. `compression-rate-avg` close to 1.0 means the producer is achieving an excellent compression ratio
- E. `poll-idle-ratio-avg` close to 0 means the application spends nearly all of its time in user processing code rather than waiting for records, which flags a slow consumer before the lag graph does

### Question 28 — `[STREAMS · Tool selection · Single]`

Analysts who write SQL but no Java need a continuously maintained count of orders per merchant over the last hour, and a dashboard that looks up **one merchant at a time** and gets the current value immediately. The platform team already operates a ksqlDB cluster and does not want to take on another deployment. All four options produce correct numbers.

- A. A Kafka Streams application with a windowed aggregation and Interactive Queries behind a REST endpoint
- B. A plain consumer group that keeps the counts in memory and exposes them over HTTP
- C. A ksqlDB **push** query (`SELECT ... EMIT CHANGES`) that streams every change of every merchant to the dashboard, which filters client-side
- D. A ksqlDB `CREATE TABLE ... AS SELECT ... WINDOW HOPPING (SIZE 1 HOUR, ADVANCE BY 1 MINUTE) GROUP BY merchantId`, served to the dashboard with **pull** queries against the materialised table

### Question 29 — `[FUND · Requirement to feature · Matching]`

Match each requirement to the Kafka capability that satisfies it with the least additional machinery.

| # | Requirement |
|---|---|
| 1 | 200 workers must share 12 partitions of independent jobs, each job acknowledged on its own, with a cap on redelivery attempts |
| 2 | Three unrelated services must each receive every record of one topic and track their own progress |
| 3 | Only the latest value per entity must survive, indefinitely, so a new service can rebuild its state from the log |
| 4 | Records older than 30 days must stay readable through the Kafka protocol without occupying broker disks |

| Letter | Capability |
|---|---|
| W | Three consumer groups, each with its own `group.id` |
| X | Tiered storage |
| Y | A share group |
| Z | `cleanup.policy=compact` |

- A. 1-W · 2-Y · 3-X · 4-Z
- B. 1-Y · 2-W · 3-X · 4-Z
- C. 1-Y · 2-W · 3-Z · 4-X
- D. 1-Z · 2-W · 3-Y · 4-X

### Question 30 — `[DEV · Subject naming · Single]`

The topic `customer.events` must carry `CustomerCreated`, `CustomerAddressChanged` and `CustomerClosed` Avro records so that their relative order per customer is preserved. With the default strategy, registering the second record type against the subject fails. The same three record types are also produced to a separate `customer.events.replay` topic, and the team wants each topic's copy of a type to be able to evolve **independently**.

- A. Keep `TopicNameStrategy` and set the subject's compatibility level to `NONE`
- B. Switch to `RecordNameStrategy`, so the subject is the full record name
- C. Switch to `TopicRecordNameStrategy`, so the subject is `<topic>-<recordName>`: the three types coexist in one topic and each topic's copy of a type evolves under its own subject
- D. Define a single union schema containing all three record types and keep `TopicNameStrategy`

### Question 31 — `[CONNECT · Task failure · Single]`

A distributed Connect cluster of three workers runs an S3 sink connector with `tasks.max=12` against a 12-partition topic. Throughput has dropped by about one twelfth and nothing alerted. `GET /connectors/s3-sink/status` returns:

```json
{"name":"s3-sink",
 "connector":{"state":"RUNNING","worker_id":"10.0.3.21:8083"},
 "tasks":[{"id":0,"state":"RUNNING","worker_id":"10.0.3.21:8083"},
          {"id":1,"state":"FAILED","worker_id":"10.0.3.22:8083",
           "trace":"org.apache.kafka.connect.errors.ConnectException: Exiting WorkerSinkTask due to unrecoverable exception.\n\tCaused by: org.apache.kafka.connect.errors.DataException: Failed to deserialize data for topic orders to Avro:\n\tCaused by: org.apache.kafka.common.errors.SerializationException: Unknown magic byte!"}]}
```

Which explanation and remedy is correct?

- A. The connector reports `RUNNING`, so the cluster is healthy; the task will be picked up at the next worker rebalance
- B. A **failed task is not restarted automatically and does not trigger a rebalance**, which is why the connector as a whole still reports `RUNNING` — so task state must be alerted on separately. `Unknown magic byte!` means a record on the topic does not carry the 5-byte Schema Registry prefix, i.e. a poison pill; the durable fix is `errors.tolerance=all` plus `errors.deadletterqueue.topic.name` (supported on sink connectors), and the immediate fix is `POST /connectors/s3-sink/restart?includeTasks=true&onlyFailed=true`
- C. Raise `tasks.max` to 24 so a spare task takes over the partition the failed task owned
- D. Set `errors.tolerance=all` in `connect-distributed.properties` so it applies to every connector on the worker

### Question 32 — `[TEST · CI design · Single]`

A CI suite takes 26 minutes because each of its 180 tests starts its own `KafkaContainer`. The team must cut the time without losing coverage of genuine broker behaviour. All four are legitimate techniques.

- A. Replace every Testcontainers test with `MockProducer`/`MockConsumer`
- B. Replace Testcontainers with `EmbeddedKafkaCluster` so the broker runs inside the test JVM
- C. Keep one container per test but switch the image to `apache/kafka-native`, which starts in under a second
- D. Share a **single static** `KafkaContainer` across the test class or the whole suite (JUnit 5 `@Testcontainers` with `@Container static`), isolate tests by generating a unique topic and `group.id` per test, and move the tests that only exercise client-side logic to `MockProducer`/`MockConsumer` and the topology tests to `TopologyTestDriver`

### Question 33 — `[FUND · Retention design · Multi — Choose 3]`

A topic must satisfy three requirements at once: (i) the latest value per key is retained, (ii) a consumer that is up to **7 days** behind still observes deletions, and (iii) segments older than **90 days** are removed so storage is capped. Which **three** settings does this design require? (Choose three.)

- A. `cleanup.policy=compact,delete`
- B. `cleanup.policy=compact` on its own with `retention.ms=-1`
- C. `delete.retention.ms=604800000`
- D. `min.cleanable.dirty.ratio=0`
- E. `retention.ms=7776000000`

### Question 34 — `[DEV · Consumer protocol migration · Ordering]`

Order the steps of an **online** migration of a running consumer group from the classic protocol to the KIP-848 consumer protocol.

| # | Step |
|---|---|
| 1 | Roll the application instances one at a time with `group.protocol=consumer`, dropping `partition.assignment.strategy`, `session.timeout.ms` and `heartbeat.interval.ms` from the client config because the new protocol ignores them |
| 2 | Confirm the cluster is on 4.x and that `kafka-features.sh describe` shows `group.version` enabled on the brokers |
| 3 | Map the current client-side assignor onto a server-side one — `RangeAssignor` → `range`, `CooperativeSticky`/`Sticky`/`RoundRobin` → `uniform` — and set `group.remote.assignor` accordingly |
| 4 | Confirm with `kafka-consumer-groups.sh --describe` that the group type has flipped to `consumer` and no member is still on the classic protocol |

- A. 2 → 3 → 1 → 4
- B. 1 → 2 → 3 → 4
- C. 2 → 1 → 3 → 4
- D. 3 → 2 → 4 → 1

### Question 35 — `[STREAMS · Join requirements · Matching]`

Match each join to the requirements it imposes.

| # | Join |
|---|---|
| 1 | `KStream`-`KStream` |
| 2 | `KStream`-`KTable` |
| 3 | `KStream`-`GlobalKTable` |
| 4 | `KTable`-`KTable` foreign-key |

| Letter | Requirement |
|---|---|
| W | No co-partitioning; the lookup key is derived from each stream record by a `KeyValueMapper` |
| X | Co-partitioning required; a window is mandatory |
| Y | Co-partitioning required; no window; only the stream side produces output |
| Z | No co-partitioning; Streams repartitions internally; no window |

- A. 1-X · 2-W · 3-Y · 4-Z
- B. 1-Y · 2-X · 3-Z · 4-W
- C. 1-X · 2-Y · 3-Z · 4-W
- D. 1-X · 2-Y · 3-W · 4-Z

### Question 36 — `[OBS · Transactional producer · Single]`

A transactional service runs four replicas in Kubernetes. All four set `transactional.id=orders-tx`. Shortly after every deployment the logs fill with:

```
org.apache.kafka.common.errors.ProducerFencedException: There is a newer producer with the same
  transactionalId which fences the current one.
```

and throughput collapses to roughly one quarter of what was expected. Which reading is correct?

- A. The four replicas share a single `transactional.id`, so each replica's `initTransactions()` fences the other three and only one can hold the id at a time. The id must be **stable per instance** — a StatefulSet ordinal, or derived from the partitions the instance owns — because a stable id is exactly what makes zombie fencing work across restarts
- B. This is the normal cost of transactions during a rolling deployment and can be ignored once the rollout finishes
- C. `transactional.id` should be generated randomly at start-up so two instances never collide; the exception disappears and nothing is lost
- D. `transaction.timeout.ms` on the client exceeds the broker's `transaction.max.timeout.ms` of 15 minutes, so the broker fences the producer

### Question 37 — `[DEV · Consumption model · Single]`

An email-notification service consumes `user-events` (12 partitions) on Kafka 4.3. Two requirements arrive in the same sprint: **(1)** a fraud team must also see every record of `user-events`; **(2)** the email service must scale to **40 workers**, because each send takes 3–8 seconds. Ordering does not matter for emails. No new infrastructure may be introduced. Which combination is right?

- A. One consumer group of 52 members using `CooperativeStickyAssignor`
- B. Give the fraud team its own `group.id` — a second consumer group reads the same topic independently and keeps its own offsets — and convert the email service to a **share group**, so its 40 workers can exceed the 12-partition ceiling with per-record acknowledgement
- C. Raise `user-events` to 52 partitions and keep one consumer group per team
- D. Replicate `user-events` into a second topic with MirrorMaker 2 for the fraud team, and raise `max.poll.records` on the email service

### Question 38 — `[CONNECT · Error handling · Multi — Choose 2]`

A JDBC **sink** connector writes to a reporting database. The requirements: a malformed record must never stop the connector; any record that is skipped must remain recoverable; and an operator must be able to see how many records were skipped. Which **two** configurations are needed? (Choose two.)

- A. `errors.tolerance=all` on its own, relying on `errors.log.enable=true` to write the offending record into the worker log
- B. `errors.tolerance=all` together with `errors.deadletterqueue.topic.name=jdbc-sink-dlq` and `errors.deadletterqueue.context.headers.enable=true`, which stamps the original topic, partition, offset and exception onto the DLQ record's headers
- C. The same DLQ settings on the paired JDBC **source** connector, so both directions are covered
- D. An alert on the sink task's `total-records-skipped` and `deadletterqueue-produce-failures` metrics, because with `errors.tolerance=all` anything the DLQ producer itself fails to write is dropped silently
- E. `errors.retry.timeout=-1` so the connector keeps retrying a bad record until an operator intervenes

### Question 39 — `[FUND · KRaft sizing · Single]`

A regulated workload needs a new Kafka 4.3 cluster across **three** availability zones. It must survive the loss of one entire AZ with cluster metadata still writable, use the **smallest** configuration that meets the requirement, and follow the documented production topology. All four are deployable KRaft layouts.

- A. Three controllers in combined mode, co-located with three brokers, one node per AZ
- B. Five dedicated controllers spread 2 / 2 / 1 across the three AZs
- C. Three dedicated controllers, one per AZ — a Raft quorum of 3 tolerates the loss of one voter, which is exactly one AZ, and dedicated controller nodes are what Kafka documents for production (combined mode is documented for development and testing)
- D. Four dedicated controllers, two in each of two AZs

### Question 40 — `[DEV · Request-reply · Single]`

An HTTP endpoint must call a pricing engine **over Kafka** and return the answer within 2 seconds. The API runs behind a load balancer and autoscales between 3 and 12 instances. The reply to a request must reach the instance that issued it, and **no topics may be created or deleted at runtime**. All four are implementable.

- A. One shared `pricing-replies` topic consumed by all instances in the **same** consumer group; each instance keeps only the replies whose correlation id it recognises
- B. One shared `pricing-replies` topic where each instance uses a **unique `group.id`**, so every instance sees every reply, matches on the `correlationId` header and discards the rest; the request carries `replyTopic` and `correlationId` headers and pending requests sit in a map with a timeout
- C. One reply topic per instance, created when the instance starts and deleted when it stops
- D. A reply topic with 12 partitions where each instance `assign()`s a fixed partition number and the request carries `replyPartition`

### Question 41 — `[OBS · Rebalance diagnostics · Multi — Choose 2]`

A group of 30 consumers on Kafka 4.3 rebalances about 40 times an hour. `rebalance-rate-per-hour` is 40, `failed-rebalance-total` is 0, `time-between-poll-max` is 8 s against a 300,000 ms limit, and CPU is normal. The platform's autoscaler rolls two pods every four minutes as a matter of routine. Which **two** changes address the cause? (Choose two.)

- A. Give each pod a stable `group.instance.id` (static membership) and size `session.timeout.ms` — **45,000 ms** by default in 4.x — to the pod restart window, so a member that returns in time reclaims its partitions with **no rebalance at all**
- B. Raise `session.timeout.ms` from its default of 10,000 ms to 120,000 ms
- C. Lower `max.poll.records` so each poll cycle is shorter
- D. Move the group to `group.protocol=consumer` (KIP-848), where the coordinator computes the assignment and members converge incrementally, so one member joining or leaving no longer imposes a stop-the-world barrier on the other 29
- E. Switch `partition.assignment.strategy` to `RoundRobinAssignor` for a more even spread

### Question 42 — `[STREAMS · State recovery · Single]`

A Streams application holds about 40 GB of state and currently runs with `num.standby.replicas=1`, with `state.dir` on the pod's ephemeral disk. To cut the cloud bill the team proposes dropping to `num.standby.replicas=0` and instead mounting a StatefulSet persistent volume for `state.dir`. Under which condition is that a sound trade, and what does it give up? All four statements describe real behaviour.

- A. It is always sound, because reading a local persistent volume is faster than catching up a standby from the changelog
- B. It is unsound, because Streams ignores `state.dir` whenever `num.standby.replicas` is 0
- C. It is sound only under `processing.guarantee=exactly_once_v2`, which writes a checkpoint that makes local state reusable after any crash
- D. It is sound when a pod is rescheduled and reattaches its **own** bound volume: the task restarts on local state and only replays the changelog from its checkpoint. What it gives up is the case where an instance is lost and its volume does not come back — the task is then reassigned to another instance, which must restore the whole 40 GB from the changelog, which is exactly the outage the standby was preventing

### Question 43 — `[TEST · Test scope · Single]`

A developer says their `MockProducer`-based unit test "proves the service is exactly-once". What is the correct assessment? All four statements describe real capabilities.

- A. The claim holds: `MockProducer` implements `initTransactions()`, `beginTransaction()`, `commitTransaction()` and `abortTransaction()` and `history()` shows exactly what was sent
- B. `MockProducer` does record the transactional calls, and `transactionCommitted()`, `uncommittedRecords()` and `sentOffsets()` let the test assert that the **application calls the API in the right order**. It cannot prove exactly-once, because fencing by `transactional.id`, the last stable offset and `read_committed` visibility are **broker** behaviours — those need an integration test against a real broker
- C. The claim fails because `MockProducer` has no transaction support at all; only a real `KafkaProducer` does
- D. `TopologyTestDriver` would prove it, because it runs the genuine EOS code path end to end

### Question 44 — `[DEV · Batching trade-off · Multi — Choose 2]`

A producer feeding a 96-partition topic is configured `linger.ms=200`, `batch.size=1048576`, `compression.type=zstd`, `acks=all`, everything else at the 4.3 defaults. Throughput is excellent, but p99 end-to-end latency is 850 ms, `buffer-available-bytes` regularly reaches 0 and `waiting-threads` is above 0. The requirement: bring p99 under 300 ms **without leaving `acks=all`**. Which **two** statements are correct? (Choose two.)

- A. `acks=1` is the only way to reach 300 ms with this record rate
- B. Replacing `zstd` with `gzip` reduces CPU time in the send path and therefore latency
- C. With 96 partitions and `batch.size=1 MB`, the accumulator can hold up to about 96 MB of unsent batches, far beyond the 32 MB `buffer.memory` default — which is why the buffer empties, `send()` blocks and will eventually throw `TimeoutException` after `max.block.ms` (60,000 ms). Either raise `buffer.memory` or lower `batch.size`
- D. Lowering `linger.ms` from 200 towards the 4.x default of **5** removes most of the accumulator wait; `record-queue-time-avg` will confirm it, and the cost is smaller batches and a worse compression ratio
- E. Raising `max.in.flight.requests.per.connection` to 10 lets more batches be in flight and shortens the queue

### Question 45 — `[CONNECT · Converters · Single]`

A sink connector is configured with

```properties
value.converter=org.apache.kafka.connect.json.JsonConverter
value.converter.schemas.enable=true
```

and fails on every record with

```
org.apache.kafka.connect.errors.DataException: JsonConverter with schemas.enable requires "schema"
  and "payload" fields and may not contain additional fields. If you are trying to deserialize plain
  JSON data, set schemas.enable=false in your converter configuration.
```

The topic is written by an application that uses `KafkaAvroSerializer` against Schema Registry. Which change is correct?

- A. Follow the message and set `value.converter.schemas.enable=false`
- B. Add an SMT that converts the JSON payload into Avro before the connector sees it
- C. Set `value.converter=io.confluent.connect.avro.AvroConverter` with `value.converter.schema.registry.url=http://schema-registry:8081`. The records are Avro behind the 5-byte Schema Registry wire prefix, which no JSON converter can read at any `schemas.enable` setting
- D. `key.converter` must always match `value.converter`; set both to `AvroConverter` and the value error disappears as a side effect

### Question 46 — `[FUND · Shared topic design · Multi — Choose 3]`

One topic must serve two very different readers: a nightly batch job that scans the last **30 days** in bulk, and a real-time service that must see each record within 200 ms. The team plans to keep it as a single topic. Which **three** statements about that design are correct? (Choose three.)

- A. Both readers can consume the same topic independently with their own `group.id`; a topic is a durable log, not a queue drained by whoever reads first
- B. The batch job's large sequential fetches evict the broker page cache that the real-time consumer depends on, so the real-time consumer's `fetch-latency-avg` can rise while the batch runs — a `consumer_byte_rate` quota on the batch job's principal bounds the damage
- C. The two readers must use different topics, because a topic can only be assigned to one consumer group at a time
- D. Retention has to cover 30 days: `log.retention.hours` defaults to **168** (7 days), so it must be raised for this topic
- E. The batch job has to use `assign()` so it does not show up inside the real-time service's consumer group

### Question 47 — `[DEV · Rebalance strategy · Single]`

A 60-member consumer group runs as a Kubernetes **Deployment** on Kafka 4.3. A rolling update takes 12 minutes and throughput drops to near zero for most of it. The team may change **client configuration only** — the workload type and the rollout strategy are fixed — and wants the **largest reduction in stop-the-world time**. All four options are real.

- A. Set `partition.assignment.strategy=CooperativeStickyAssignor`, which revokes only the partitions that actually move
- B. Set `group.instance.id` for static membership and size `session.timeout.ms` to the pod restart window
- C. Set `partition.assignment.strategy=RoundRobinAssignor` for an even spread across members
- D. Set `group.protocol=consumer` (KIP-848): the group coordinator computes the target assignment and members converge incrementally through `ConsumerGroupHeartbeat`, so there is no `JoinGroup`/`SyncGroup` barrier at all. `partition.assignment.strategy`, `session.timeout.ms` and `heartbeat.interval.ms` are then ignored on the client

### Question 48 — `[STREAMS · Repartition cost · Multi — Choose 2]`

A topology runs `stream.selectKey(...).groupByKey().count()` over a 64-partition topic at 200,000 records/s. Which **two** statements about the cost of this design are correct? (Choose two.)

- A. Replacing `selectKey(...).groupByKey()` with `groupBy(...)` avoids the repartition, because `groupBy` can group without rekeying
- B. `selectKey` ahead of a stateful operation inserts an internal **repartition topic**, so every record is written back to Kafka and read again — roughly doubling broker traffic for this topology and adding a network round trip to end-to-end latency
- C. The repartition topic uses `cleanup.policy=delete` and Streams purges already-processed records from it, so its disk cost stays bounded — unlike the **changelog** topic, which is compacted and grows with the key space
- D. Setting `statestore.cache.max.bytes=0` removes the repartition topic, because no buffering is needed
- E. The repartition topic is compacted, so it retains one record per key and its size is bounded by cardinality

### Question 49 — `[CONNECT · Outbox routing · Multi — Choose 3]`

A Debezium PostgreSQL connector with the `EventRouter` SMT publishes a standard outbox table (`id`, `aggregatetype`, `aggregateid`, `type`, `payload`). The team needs: each aggregate type in a topic named `<aggregatetype>-events`; all events of one aggregate **instance** in order; and the event type readable by consumers **without parsing the payload**. Which **three** settings are required? (Choose three.)

- A. `transforms.outbox.route.topic.replacement=${routedByValue}-events` — the default is `outbox.event.${routedByValue}`
- B. `transforms.outbox.route.by.field=type`
- C. `transforms.outbox.table.field.event.key=aggregateid`
- D. `transforms.outbox.table.fields.additional.placement=type:header:eventType`
- E. `transforms.outbox.table.expand.json.payload=true`, without which the record key cannot be set

### Question 50 — `[OBS · Quotas · Single]`

A nightly batch loader saturates the cluster and degrades the latency of every real-time service on it. The requirement is to bound the batch loader **without touching its code or its configuration** and without affecting any other client. All four are real levers.

- A. Apply a `producer_byte_rate` quota to the loader's principal: `kafka-configs.sh --alter --add-config 'producer_byte_rate=10485760' --entity-type users --entity-name batch-loader`. The broker delays its responses, which the client experiences as backpressure and which shows up as `produce-throttle-time-avg > 0` on that client
- B. Lower the loader's `linger.ms` so it sends smaller requests
- C. Move the batch topic to a separate cluster
- D. Lower `max.request.size` on the brokers so the loader's requests are rejected above the limit

### Question 51 — `[FUND · Tenant topic design · Single]`

A SaaS platform has 4,000 tenants and is growing by roughly 50 per week. Per-tenant ordering is required. All tenants share one retention policy and one access-control boundary — a single internal service consumes everything — and **onboarding a tenant must not require a cluster operation**. All four layouts are workable.

- A. One topic per tenant with 6 partitions each: 24,000 partitions, and a topic-creation call per new tenant
- B. One topic per tenant with 1 partition each, so the partition total stays at 4,000
- C. One topic keyed by `tenantId`, with the partition count sized to throughput rather than to tenant count: per-tenant ordering comes from the key, onboarding is just a new key, and controller metadata does not grow with the tenant list. The trade-off is that per-tenant ACLs and per-tenant retention are no longer expressible, and one very large tenant becomes a hot partition
- D. One topic read by a share group, with the tenant id in a header

### Question 52 — `[DEV · Authentication choice · Single]`

An application must authenticate to a **self-managed** Kafka cluster. The requirements: credentials must be creatable and rotatable at runtime without restarting brokers, and one of the clients is a serverless function that cannot ship a keystore file. All four mechanisms are supported by Kafka.

- A. mTLS with `ssl.client.auth=required`
- B. SASL/SCRAM-SHA-512 over `SASL_SSL`: credentials live in cluster metadata and are created, changed and deleted at runtime with `kafka-configs.sh`, and a client needs only a JAAS configuration string
- C. SASL/GSSAPI with a Kerberos KDC
- D. SASL/PLAIN over `SASL_SSL` with a static JAAS file on each broker

### Question 53 — `[TEST · Test selection · Multi — Choose 2]`

Two behaviours must be covered before a release: **(1)** after a broker restart mid-run, an idempotent producer's records still arrive in order per key with no duplicates; **(2)** the service's poll loop exits cleanly when `wakeup()` is called from a shutdown hook, committing the last processed offsets before closing. Which **two** approaches fit best? (Choose two.)

- A. For (1), `MockProducer` with `errorNext(new NotLeaderOrFollowerException(...))` to simulate the restart
- B. For (1), Testcontainers with a real broker: run the producer, restart the container mid-run, then read everything back and assert the per-key sequence — broker restart behaviour cannot be mocked
- C. For (2), `MockConsumer`: seed records with `addRecord()`, use `schedulePollTask(() -> consumer.wakeup())` so the wake-up lands inside a `poll()` call, then assert `committed(...)` and `closed()`
- D. For (2), `TopologyTestDriver`, because it owns the consumer lifecycle
- E. For (1), two `TopologyTestDriver` instances sharing one `application.id`

### Question 54 — `[FUND · Long retention · Single]`

A topic ingests 40 TB per day and must keep 90 days of history that a backfill job reads occasionally. Provisioning 3.6 PB of broker disk is out of the question, and the real-time consumers' latency must not change. The backfill must keep reading **through ordinary Kafka clients**, with no second data format to maintain. All four are real designs.

- A. Enable tiered storage on the topic (`remote.storage.enable=true`) and set `local.retention.ms` to cover the worst lag of the real-time consumers, leaving `retention.ms` at 90 days. Hot data stays on broker disk and closed segments move to object storage; the backfill reads the remote tier at higher latency, which is the accepted cost
- B. Cut `retention.ms` to 7 days and archive everything with a Connect S3 sink, so the backfill reads S3 instead of Kafka
- C. Set `cleanup.policy=compact` so only the latest value per key survives and 90 days fits on disk
- D. Set `log.retention.bytes` per partition so the topic caps itself and old data is dropped automatically

### Question 55 — `[DEV · Commit strategy · Multi — Choose 2]`

A consumer processes 40,000 records/s and writes to an **idempotent** HTTP sink. The team wants to minimise both the replay window after a crash and the overhead of committing. Which **two** statements are correct? (Choose two.)

- A. `enable.auto.commit=true` with `auto.commit.interval.ms=5000` (the default) means up to 5 seconds of processed work can be replayed after a crash — and because the commit happens inside `poll()`, it can commit offsets for records that were returned but not yet processed
- B. `commitSync()` after every record gives the smallest replay window and is the right default at this record rate
- C. `isolation.level=read_committed` reduces the number of duplicates the consumer sees after a crash
- D. `commitAsync()` after each batch, with a final `commitSync()` in a `finally` block, bounds the replay window to one batch while keeping the hot path free of blocking round trips
- E. Because the sink is idempotent, offsets can be committed before processing with no consequence

### Question 56 — `[CONNECT · Cross-cluster replication · Single]`

A self-managed on-premises Kafka cluster must be mirrored into **Amazon MSK Provisioned** for disaster recovery. The requirements: topic names identical on both sides so clients need no reconfiguration at failover, consumer group offsets translated so consumers resume where they stopped, and **no Connect cluster to operate**. All four are real options.

- A. MirrorMaker 2 on a dedicated Connect cluster with `replication.policy.class=IdentityReplicationPolicy` and `MirrorCheckpointConnector` for offsets
- B. A Connect S3 sink on-premises paired with a Connect S3 source in AWS
- C. Kafka's built-in cross-cluster replication, enabled with `replica.fetch.remote=true` on the target brokers
- D. MSK Replicator in **identical topic name** mode with consumer group offset sync enabled — a managed service that replicates data, topic configuration, ACLs and offsets with no Connect cluster to run; the trade-off is that it is AWS-managed and the target must be MSK

### Question 57 — `[OBS · Rolling restart · Single]`

During a rolling broker restart of a six-broker cluster (topics at RF=3, `min.insync.replicas=2`, producers at `acks=all`) the operator restarts brokers back to back. `UnderMinIsrPartitionCount` spikes to 130 and producers log `NOT_ENOUGH_REPLICAS`. The next restart must complete with **zero produce errors and no risk of losing an acknowledged record**. All four are real operational levers.

- A. Set `unclean.leader.election.enable=true` for the duration of the restart and back to `false` afterwards
- B. Wait between brokers until `UnderReplicatedPartitions` is back to **0**: a restarted broker has to re-enter the ISR of every partition it hosts — bounded by `replica.lag.time.max.ms` (30,000 ms) plus the time to catch up on the backlog — before the next broker may be taken down. Running `kafka-leader-election.sh --election-type PREFERRED` after each broker rejoins restores leadership balance
- C. Raise `min.insync.replicas` to 3 during the restart so the cluster refuses any unsafe write
- D. Move the producers to `acks=1` for the duration of the restart and back to `acks=all` afterwards

### Question 58 — `[FUND · Version defaults · Single]`

A team upgrades both its cluster and its client libraries from **2.8** to **4.3** and deliberately changes **no client property at all**. Which set of behaviour changes should they plan for? All four lists name real defaults.

- A. `acks` goes from `1` to `all`; `enable.idempotence` from `false` to `true`; `linger.ms` from `0` to `5`; consumer `session.timeout.ms` from `10000` to `45000`
- B. `acks` stays at `1`; the only change is `linger.ms`, which goes from `0` to `100`
- C. `acks` goes to `all` and `enable.idempotence` to `true`, but `linger.ms` is still `0` and `session.timeout.ms` is still `10000`
- D. `partition.assignment.strategy` goes from `[RangeAssignor, CooperativeStickyAssignor]` to `RangeAssignor`, and `group.protocol` now defaults to `consumer`

### Question 59 — `[DEV · Poll loop design · Single]`

A consumer calls a downstream service whose p99 is 250 ms. At the default `max.poll.records=500` that is about two minutes of work per poll — inside the limit, but the team needs ten times the throughput. Ordering per key is required, and no offset may be committed before its record's side effect is durable. All four designs exist in the wild.

- A. Submit every record of the batch to a fixed thread pool and commit the batch's last offset as soon as the submissions return
- B. Raise `max.poll.records` to 5,000 and keep the single-threaded loop, raising `max.poll.interval.ms` to match
- C. Dispatch each record to a **per-key worker queue** (worker = `hash(key) % N`), track the lowest un-acknowledged offset per partition and commit only that watermark, and `pause()` a partition once its in-flight count crosses a bound so `poll()` keeps running without fetching more
- D. Run one consumer instance per key so each key has its own ordered pipeline

### Question 60 — `[FUND · Rack-aware placement · Single]`

A nine-broker cluster spans three AZs and every broker sets `broker.rack` to its AZ. Topics are created with RF=3 and `min.insync.replicas=2`. The team must be able to state that losing one AZ never takes a partition below `min.insync.replicas`. All four statements are about real mechanisms.

- A. Set `replica.selector.class` to the rack-aware selector so consumers fetch from the replica in their own AZ
- B. Rely on rack-aware replica assignment: with `broker.rack` set and RF equal to the number of racks, Kafka places one replica per rack when the topic is created, so losing one AZ leaves exactly two in-sync replicas. The guarantee only holds if it is re-checked after every partition reassignment and after any topic created with an RF that is not a multiple of the rack count
- C. Raise RF to 4 so two replicas survive in each of the remaining AZs
- D. Set `unclean.leader.election.enable=true` so a leader is always available after an AZ failure

---

> ✅ Hết giờ? Chấm bài ở [answers.md](answers.md) và điền bảng điểm theo domain trước khi xem giải thích.
