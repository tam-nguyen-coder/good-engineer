# 📝 Practice Questions — Week 2: Reliability & Storage (replication, retention, log compaction, delivery semantics)

> **28 questions** · real CCDAK exam style, difficulty ≥ real exam · covers the full Week 2 material (Kafka 4.3 defaults) plus 2 Week 1 review questions.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first, no documentation.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (number to choose is stated). Config names are the **Java client / broker** names, as on the real exam.
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

---

### Question 1 — `[FUND · ISR · Single]`

A partition has `replication.factor=3`. One follower runs on an overloaded broker and is currently **8,000 records behind** the leader's log end offset, but it keeps sending fetch requests every few hundred milliseconds and its offset keeps increasing. All brokers use default settings. Which statement is correct?

- A. The follower is removed from the ISR as soon as it falls more than `replica.lag.max.messages` (default 4000) records behind
- B. The follower stays in the ISR as long as it has caught up to the leader's log end offset at least once within the last `replica.lag.time.max.ms` (default 30000 ms); Kafka has no record-count threshold
- C. The follower is removed from the ISR immediately because any lag greater than zero makes a replica out of sync
- D. The follower is removed from the ISR only if the KRaft controller detects that its broker session expired; lag never affects ISR membership

### Question 2 — `[FUND · High watermark · Single]`

A producer writes with `acks=1` and receives a successful acknowledgement with offset 1042. A consumer on the same partition, polling continuously, does not receive offset 1042 for several hundred milliseconds. There are no errors anywhere. What explains the delay?

- A. The consumer's `fetch.min.bytes` is too high
- B. The record is compressed and the broker must decompress it before serving it
- C. Consumers only read up to the **high watermark**, the offset up to which every replica in the ISR has replicated; the leader has appended the record (its log end offset advanced) but the followers have not fetched it yet
- D. The record was written to a follower first and must be forwarded to the leader

### Question 3 — `[FUND · acks × min.insync.replicas · Multi — Choose 2]`

A topic has `replication.factor=3` and `min.insync.replicas=2`. All producers use `acks=all`. Two of the three brokers hosting a partition crash at the same time. Which two statements describe the behaviour until at least one broker returns? (Choose two.)

- A. Producers continue writing successfully because the surviving replica is the leader and is in the ISR
- B. Producers receive `NotEnoughReplicasException` because the ISR size (1) is below `min.insync.replicas`
- C. Consumers also fail because the partition is below `min.insync.replicas`
- D. Consumers can still read all records up to the high watermark; no committed data is lost
- E. The controller elects a new leader outside the ISR to restore writes

### Question 4 — `[FUND · acks × min.insync.replicas · Multi — Choose 2]`

Which two of the following configurations are **mistakes** with respect to the goal "no data loss, and writes keep working during a single-broker rolling restart"? (Choose two.)

- A. `replication.factor=3`, `min.insync.replicas=3`, producers `acks=all`
- B. `replication.factor=3`, `min.insync.replicas=2`, producers `acks=all`
- C. `replication.factor=3`, `min.insync.replicas=2`, producers `acks=1`
- D. `replication.factor=3`, `min.insync.replicas=2`, producers `acks=-1`
- E. `replication.factor=3`, `min.insync.replicas=2`, producers with default `acks` on Kafka 4.3 clients

### Question 5 — `[FUND · Durability guarantees · Single]`

A team argues that their topic with `replication.factor=2`, `min.insync.replicas=1` and `acks=all` "cannot lose acknowledged data because `acks=all` waits for every replica". One broker is down for maintenance while producers keep writing. Which statement is correct?

- A. They are right; `acks=all` always waits for all assigned replicas, so the write would be rejected while a replica is down
- B. They are right, because `min.insync.replicas=1` is only used with `acks=1`
- C. They are wrong; `acks=all` waits only for the **current ISR**, which is now the leader alone (1 ≥ `min.insync.replicas`), so writes are acknowledged with a single copy and are lost if that broker fails before the other returns
- D. They are wrong, because `acks=all` is not a valid setting when `replication.factor=2`

### Question 6 — `[FUND · Leader election · Multi — Choose 2]`

Which two statements about `unclean.leader.election.enable` are correct? (Choose two.)

- A. Its default value is `false`, so when every replica in the ISR is offline the partition stays unavailable until an ISR replica comes back
- B. Its default value is `true`, so Kafka always restores availability automatically
- C. It can be set only at broker level; there is no topic-level override
- D. Setting it to `true` favours availability: a replica outside the ISR can become leader, at the cost of losing records that were committed but not replicated to that replica
- E. When it is `true`, `min.insync.replicas` is ignored for `acks=all` writes

### Question 7 — `[FUND · ELR (KIP-966) · Single]`

A Kafka 4.3 cluster (new, default features) runs a topic with `replication.factor=3` and `min.insync.replicas=2`. After two failures the ISR shrank to only the leader. `kafka-topics.sh --describe` shows `Isr: 2  Elr: 3`. Now broker 2 also dies. What does the controller do, with `unclean.leader.election.enable=false`?

- A. Nothing; the partition remains offline until broker 2 returns, because the ISR is empty
- B. It elects replica 3 as leader because it is in the **Eligible Leader Replicas** set: replicas that left the ISR after the ISR had already dropped below `min.insync.replicas`, so they still hold every committed record (the high watermark could not advance in that state)
- C. It performs an unclean election automatically because ELR overrides `unclean.leader.election.enable`
- D. It elects replica 4 because the last known leader is always preferred over the ELR

### Question 8 — `[FUND · ELR (KIP-966) · Single]`

An operator on a Kafka 4.3 cluster with ELR enabled wants to raise the effective `min.insync.replicas` for the whole cluster from 1 to 2 and notices that some partitions previously listed an `Elr:` entry. Which statement is correct?

- A. Run `kafka-configs.sh --alter --entity-type brokers --entity-name <id> --add-config min.insync.replicas=2` on every broker; ELR state is unaffected
- B. The change must be made in `server.properties` on each broker and requires a full cluster restart
- C. `min.insync.replicas` cannot be changed once ELR is enabled
- D. Set it at **cluster level** (`--entity-type brokers --entity-default`); broker-level alteration is not allowed with ELR, and any change to `min.insync.replicas` (cluster or topic level) **clears the ELR state** of the affected partitions

### Question 9 — `[FUND · Preferred leader · Single]`

After a rolling restart, `kafka-topics.sh --describe` shows that broker 2 is the leader for **almost every partition**, even though `Replicas` lists different first replicas. Producers and consumers work but broker 2 is overloaded. All settings are default. Which statement is correct?

- A. `auto.leader.rebalance.enable` is `true` by default and the controller checks every `leader.imbalance.check.interval.seconds` (300 s), moving leadership back to the **preferred leader** (first replica in `Replicas`) when the imbalance exceeds `leader.imbalance.per.broker.percentage` (10%); to force it now run `kafka-leader-election.sh --election-type PREFERRED`
- B. Leadership never moves back automatically; the operator must run `kafka-reassign-partitions.sh` to change the replica list
- C. The topic's `unclean.leader.election.enable` must be set to `true` so that the original leaders can be re-elected
- D. The partitions must be recreated; leadership is fixed at topic creation time

### Question 10 — `[FUND · Rack awareness · Single]`

A company runs 6 brokers across 3 availability zones (2 per zone) and wants every partition with `replication.factor=3` to survive the loss of an entire zone. Which configuration achieves this at topic creation time?

- A. Set `min.insync.replicas=3` so that all three zones must acknowledge
- B. Create each topic with `--replica-assignment` and manually pick brokers in different zones for every partition
- C. Set `broker.rack=<zone-id>` on every broker; the controller then spreads the replicas of each partition across different racks when assigning replicas
- D. Enable `unclean.leader.election.enable=true` so that a replica in another zone can take over

### Question 11 — `[FUND · Segments & retention · Multi — Choose 2]`

Which two statements about log segments and retention in Kafka 4.3 (defaults) are correct? (Choose two.)

- A. A new segment is rolled every time a producer batch is appended
- B. The active segment rolls when it reaches `segment.bytes` (default 1 GiB) **or** when `segment.ms` (default 7 days) has elapsed since its first record, whichever comes first
- C. Retention deletes individual records as soon as each one is older than `retention.ms`
- D. Retention operates on the active segment first because it contains the newest data
- E. Retention and compaction work **one whole closed segment at a time**; the active segment is never deleted or compacted

### Question 12 — `[FUND · Retention trap · Single]`

A low-traffic audit topic (a few KB per day) is configured with `retention.ms=3600000` (1 hour). Two days later a consumer reading `--from-beginning` still receives records from 48 hours ago. `retention.bytes` is the default. What is the MOST likely cause and the fix?

- A. The broker's log cleaner thread is disabled; set `log.cleaner.enable=true`
- B. All records still sit in the **active segment**, which never expires; with default `segment.bytes` (1 GiB) and `segment.ms` (7 days) it has not rolled yet. Lower `segment.ms` (or `segment.bytes`) so the segment closes and becomes eligible; remember the deletion check runs only every `log.retention.check.interval.ms` (5 minutes)
- C. `retention.ms` only applies to compacted topics; set `cleanup.policy=compact`
- D. The consumer is reading from a follower replica that has stale data

### Question 13 — `[FUND · Retention configs · Multi — Choose 2]`

A topic has 8 partitions, `cleanup.policy=delete` and `retention.bytes=1073741824` (1 GiB). Which two statements are correct? (Choose two.)

- A. The topic can grow to about **8 GiB** in total, because `retention.bytes` is enforced **per partition**
- B. The topic is capped at 1 GiB in total across all partitions
- C. Setting `retention.ms=0` keeps records forever
- D. Setting `retention.ms=-1` disables time-based retention, so only the size limit applies; with `retention.bytes=-1` as well the data is kept forever
- E. `retention.bytes` is ignored whenever `retention.ms` is also set

### Question 14 — `[FUND · Log compaction guarantees · Multi — Choose 2]`

A topic uses `cleanup.policy=compact`. Which two guarantees does log compaction provide? (Choose two.)

- A. The **order** of records is never changed; compaction only removes records, it never reorders them
- B. At any instant the partition contains **exactly one** record per key
- C. The **offset** of a record never changes; if a consumer seeks to an offset that was compacted away, it receives the next offset that still exists
- D. Compaction runs on the active segment so that the latest writes are deduplicated immediately
- E. Records with a `null` key are stored as-is and simply skipped by the cleaner

### Question 15 — `[FUND · Tombstones · Single]`

An application maintains customer profiles in a compacted topic keyed by `customerId`. A customer requests deletion. Which action removes the customer from the topic, and what is the relevant timing?

- A. Produce a record with the same key and an **empty string** value; it is removed at the next compaction
- B. Produce a **tombstone**: the same key with a `null` value. Compaction then drops the older values for that key, and the tombstone itself is retained for `delete.retention.ms` (default 86400000 ms = 24 h) so that consumers reading from the beginning can still observe the delete
- C. Run `kafka-delete-records.sh` for the key; compacted topics do not support tombstones
- D. Lower `retention.ms` for the topic; the key disappears once the retention window passes

### Question 16 — `[FUND · Compaction tuning · Single]`

A compacted changelog topic receives updates slowly. Operators notice that compaction almost never runs, so the partition keeps many outdated values per key. `segment.ms` is already low, so segments do roll. Which change makes the cleaner run **more often**?

- A. Increase `min.compaction.lag.ms` so that records become eligible sooner
- B. Increase `delete.retention.ms` from 24 h to 48 h
- C. Lower `min.cleanable.dirty.ratio` from its default **0.5** (the cleaner only cleans a log when at least 50% of it is "dirty", i.e. not yet compacted)
- D. Set `cleanup.policy=delete` so that old values expire by time

### Question 17 — `[FUND · cleanup.policy · Single]`

A "user-session" topic must always expose the **latest** state for each session key, but sessions that received no update for **30 days** must disappear entirely from the log. Which topic configuration meets both requirements?

- A. `cleanup.policy=delete`, `retention.ms=2592000000`
- B. `cleanup.policy=compact` only; compaction removes keys after 30 days automatically
- C. `cleanup.policy=compact`, `delete.retention.ms=2592000000`
- D. `cleanup.policy=compact,delete`, `retention.ms=2592000000`

### Question 18 — `[FUND · Compaction use cases · Multi — Choose 2]`

Which two are appropriate uses of a **log-compacted** topic? (Choose two.)

- A. The internal topic `__consumer_offsets`, where only the latest committed offset per group/topic/partition matters
- B. A click-stream topic where analysts must replay every individual click for the last 7 days
- C. A metrics topic where every sample is needed to compute averages over time
- D. A CDC (change data capture) topic that must let a new service rebuild the current state of every database row by reading from the beginning
- E. A topic whose records have no key

### Question 19 — `[FUND · Delivery semantics · Single]`

A consumer application calls `commitSync()` **immediately after** `poll()` returns and **before** it processes the records. The application crashes half-way through processing the batch. Which delivery semantics does this design implement?

- A. At-least-once: the records are reprocessed after restart
- B. **At-most-once**: the offsets were already committed, so the unprocessed records of the batch are skipped after restart and are effectively lost
- C. Exactly-once, because `commitSync()` is synchronous
- D. Transactional delivery, because the commit and the poll are in the same thread

### Question 20 — `[FUND · Exactly-once · Multi — Choose 2]`

A consume-transform-produce application reads from topic A and writes to topic B, both in the same Kafka cluster. Which two elements are **required** to achieve exactly-once semantics for the whole pipeline? (Choose two.)

- A. A transactional producer (`transactional.id` set) that writes the output records **and** the consumer offsets (`sendOffsetsToTransaction`) in the same transaction
- B. `acks=1` on the producer so that the transaction commits faster
- C. `enable.auto.commit=true` on the consumer so that offsets are never forgotten
- D. Downstream consumers of topic B using `isolation.level=read_committed` so they never see records from aborted transactions
- E. `cleanup.policy=compact` on topic B so duplicate keys are removed

### Question 21 — `[FUND · Ordering · Single]`

An order-management system must process all events for a given `orderId` in the exact order they were produced, and needs high throughput across many orders. Events currently go to a 12-partition topic with a `null` key. Which change is correct?

- A. Reduce the topic to 1 partition; it is the only way Kafka can guarantee ordering
- B. Keep the `null` key and set `max.in.flight.requests.per.connection=1` on the producer
- C. Use `orderId` as the record **key**: all events for one order hash to the same partition, and Kafka guarantees order **within a partition**, so per-order ordering holds while the 12 partitions keep the parallelism
- D. Enable `cleanup.policy=compact` so that records are sorted by key

### Question 22 — `[FUND · Message size · Multi — Choose 2]`

A Java producer with default settings tries to send a **2 MB** record to a topic with default settings and fails with `RecordTooLargeException`. The team wants this record size to be produced **and** accepted by the broker. Which two configurations must be raised? (Choose two.)

- A. Producer `max.request.size` (default 1048576 bytes)
- B. Producer `batch.size` (default 16384 bytes)
- C. Topic `max.message.bytes` (or broker `message.max.bytes`, default 1048588 bytes)
- D. Topic `segment.bytes` (default 1 GiB)
- E. Consumer `fetch.min.bytes` (default 1 byte)

### Question 23 — `[FUND · Topic configs · Multi — Choose 2]`

Which two statements about topic-level configuration are correct? (Choose two.)

- A. The default `compression.type` on the topic is `gzip`, so every batch is recompressed by the broker
- B. With the default `compression.type=producer`, the broker stores batches with whatever codec the producer used and does **not** recompress them
- C. `message.timestamp.type=CreateTime` (the default) makes the broker overwrite the record timestamp with the time it appended the record
- D. `message.timestamp.type=LogAppendTime` makes the broker overwrite the record timestamp with the broker's own clock at append time, which is useful when producer clocks cannot be trusted
- E. `message.timestamp.type` can only be set in `server.properties`, never per topic

### Question 24 — `[FUND · Share groups (KIP-932) · Multi — Choose 2]`

A team wants to use Kafka as a **work queue** on Kafka 4.3: 20 worker instances must pull tasks from a 4-partition topic, each task must be acknowledged individually, and failed tasks must be retried automatically. Ordering does not matter. Which two statements are correct? (Choose two.)

- A. A **share group** (Queues for Kafka, KIP-932, GA in Kafka 4.2) fits: several consumers can consume from the **same** partition, so all 20 workers stay busy even with 4 partitions
- B. A classic consumer group fits as-is: 20 consumers on 4 partitions will share records evenly
- C. Share groups preserve strict per-partition ordering exactly like consumer groups
- D. Share consumers acknowledge each record as `ACCEPT`, `RELEASE` (redeliver) or `REJECT` (do not redeliver), instead of committing an offset
- E. Share group state is stored in `__consumer_offsets`, exactly like consumer group offsets

### Question 25 — `[FUND · Share groups (KIP-932) · Single]`

A share consumer fetches a record and its processing fails because a downstream service is temporarily unavailable. The consumer wants the record to be redelivered to **another** member of the share group soon, and wants poison records to stop being redelivered eventually. All group settings are default. Which statement is correct?

- A. Acknowledge the record with `RELEASE`; it becomes available again immediately. If the consumer did nothing, the acquisition lock would expire after `group.share.record.lock.duration.ms` (default 30000 ms) and the record would be released anyway. After the delivery count reaches `group.share.delivery.count.limit` (default 5) the record is archived and not delivered again
- B. Acknowledge the record with `ACCEPT`; the broker retries it automatically
- C. Acknowledge the record with `REJECT`; it is redelivered to another consumer within 30 s
- D. Call `seek()` on the share consumer to reset the partition to the failed offset

### Question 26 — `[FUND · Tiered storage · Single]`

A compliance team requires **one year** of retention on a high-volume event topic (`cleanup.policy=delete`). The operations team refuses to add brokers just for disk capacity. Which Kafka feature addresses this?

- A. Log compaction, which shrinks the topic to one record per key
- B. `retention.bytes=-1`, which offloads data to the operating system page cache
- C. **Tiered storage** (KIP-405, GA since 3.9): set `remote.storage.enable=true` on the topic so closed segments are copied to remote object storage while brokers keep only `local.retention.ms` worth of data locally
- D. Increasing `segment.bytes` so fewer, larger files are stored

### Question 27 — `[FUND · Week 1 review · KRaft · Single]`

In a Kafka 4.3 cluster, which component elects partition leaders when a broker fails, and where is the cluster metadata persisted?

- A. ZooKeeper elects the leaders and stores metadata under `/brokers/topics`
- B. The **active KRaft controller** elects new leaders (from the ISR, or the ELR when enabled) and persists metadata in the internal `__cluster_metadata` topic, which brokers replicate as observers; ZooKeeper support was removed in Kafka 4.0
- C. Each broker elects itself leader for the partitions it hosts; metadata lives in `__consumer_offsets`
- D. The producer with the highest `client.id` elects the leader and stores metadata in `__transaction_state`

### Question 28 — `[FUND · Week 1 review · Partitions & consumers · Single]`

A topic has **6 partitions**. A classic consumer group subscribed to it is scaled to **8 consumer instances**. Which statement is correct?

- A. All 8 instances receive records because partitions are split by record key among instances
- B. Kafka automatically increases the partition count to 8
- C. The group fails to start because the number of consumers exceeds the number of partitions
- D. Exactly 6 instances are assigned one partition each and **2 instances stay idle**, because within a consumer group a partition is consumed by at most one member; to use more consumers than partitions you would need more partitions or a share group
