# 📝 Practice Questions — Week 10: Final Cumulative Mock Exam (Cross-Domain)

> **30 questions** · **cross-domain mini mock** in real CCDAK exam style, difficulty ≥ real exam · covers **all 6 CCDAK domains** (not scoped to a single week like previous weeks).
> ⏱️ **This is a cumulative cross-domain mock — run it timed, 45 minutes for 30 questions (pace ~90 seconds/question), straight through with no reference material, then self-grade with [answers.md](answers.md).** It is a half-size version of the real 60-question / 90-minute exam; use it to check your reflexes across all domains before the official full mocks later in the week.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first. answers.md includes a **per-domain score analysis** → find which domain is weak and go back to the matching week.
> Exam-weighted mix: **DEV 9 (30%) · FUND 7 (23%) · CONNECT 4 (13%) · OBS 4 (13%) · STREAMS 4 (13%) · TEST 2 (7%)**. Domain order is **shuffled** (like the real exam). Questions 11 and 26 simulate the CCDAK **matching** format using "which mapping is correct" options.
> Version anchor: **Apache Kafka 4.3** defaults unless a version is stated in the question.
> Tag: `[Domain · Topic · type]`. Multi = multiple-select (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../KAFKA-STUDY-PLAN.md)

---

### Question 1 — `[FUND · Replication · Single]`
A topic `payments` has a replication factor of **3** and `min.insync.replicas=2`. A producer writes with `acks=all`. During a maintenance window **one** broker hosting a replica of partition 0 is shut down, and later a **second** broker hosting another replica of partition 0 also fails. Which statement describes the producer's experience for partition 0?
- A. Writes succeed after the first failure and continue to succeed after the second failure because the leader is still alive.
- B. Writes succeed after the first failure; after the second failure the producer receives `NotEnoughReplicasException` (retriable) until a replica rejoins the ISR.
- C. Writes fail immediately after the first failure because `acks=all` requires all 3 replicas to acknowledge.
- D. Writes succeed after both failures but the broker silently downgrades the request to `acks=1`.

### Question 2 — `[DEV · Producer · Single]`
A developer keeps the Kafka 4.3 producer defaults but explicitly sets `acks=1` to reduce latency. On startup the application fails with a `ConfigException` about idempotence. What is the cause and the minimal correct fix that still keeps the lower latency?
- A. `enable.idempotence` defaults to `true` and requires `acks=all`; set `enable.idempotence=false` explicitly if `acks=1` is truly required.
- B. `acks=1` is no longer a valid value in Kafka 4.x; use `acks=0` instead.
- C. `max.in.flight.requests.per.connection` defaults to 5 and must be lowered to 1 before `acks=1` can be used.
- D. `retries` defaults to 0, which conflicts with idempotence; set `retries=2147483647`.

### Question 3 — `[CONNECT · Error handling · Single]`
A team runs a **JDBC source connector** and an **Elasticsearch sink connector** on the same distributed Connect cluster. Both occasionally receive records that fail deserialization in the converter. They want failing records to be routed to a dead letter queue topic instead of stopping the connector. Which statement is correct?
- A. Set `errors.tolerance=all` and `errors.deadletterqueue.topic.name` on both connectors; both will route bad records to the DLQ.
- B. Only the **sink** connector supports `errors.deadletterqueue.topic.name`; for the source connector you can only use `errors.tolerance=all` with `errors.log.enable=true` to skip and log.
- C. Only the **source** connector supports a DLQ because it owns the records it produces; the sink must be restarted manually.
- D. DLQs are configured on the Connect **worker** (`errors.deadletterqueue.topic.name` in `connect-distributed.properties`) and apply to every connector.

### Question 4 — `[STREAMS · Joins · Single]`
A Kafka Streams application enriches a `clicks` stream (keyed by `sessionId`, 24 partitions) with a small `products` reference topic (keyed by `productId`, 3 partitions, ~5,000 records). The join key is the `productId` field inside each click. Which approach works **without** repartitioning `clicks` and without co-partitioning requirements?
- A. Join `KStream<sessionId, Click>` with `KTable<productId, Product>` directly; Streams handles the key mismatch automatically.
- B. Read `products` as a `GlobalKTable` and use `KStream#join(GlobalKTable, KeyValueMapper, ValueJoiner)` extracting `productId` from the click as the lookup key.
- C. Repartition `products` to 24 partitions with `repartition()` and then perform a windowed KStream-KStream join.
- D. Use a KTable-KTable foreign-key join; it is the only join that supports different keys.

### Question 5 — `[OBS · Consumer lag · Single]`
A consumer group's lag on Grafana grows steadily, yet the consumer process is alive, CPU is low, and `kafka-consumer-groups.sh --describe` shows the group **repeatedly rebalancing** every few minutes with members joining and leaving. Processing of each batch of 500 records takes about **6 minutes**. What is the MOST likely root cause?
- A. `session.timeout.ms` (45 s) expires because the heartbeat thread is blocked during processing.
- B. `max.poll.interval.ms` (default 300,000 ms) is exceeded, so the consumer is considered failed and evicted, triggering a rebalance; the fix is to lower `max.poll.records` or raise `max.poll.interval.ms`.
- C. `fetch.max.wait.ms` (500 ms) is too low, causing empty fetches and rebalances.
- D. The group coordinator is under-replicated because `__consumer_offsets` has only 50 partitions.

### Question 6 — `[DEV · Offset commit · Multi — Choose 2]`
A consumer processes each record and writes the result to an external database, then commits offsets. `enable.auto.commit` is set to `false` and the code calls `consumer.commitSync()` after processing the whole batch returned by `poll()`. The process crashes after writing 300 of 500 records from a batch. Which two statements are correct? (Choose two.)
- A. After restart, the new assignee re-reads all 500 records of that batch, so up to 300 records are processed twice (at-least-once).
- B. After restart, consumption resumes at record 301 because Kafka tracks per-record acknowledgements.
- C. To reduce duplicates without changing the delivery guarantee, the consumer can commit more granularly with `commitSync(Map<TopicPartition, OffsetAndMetadata>)` after every N records.
- D. Switching to `commitAsync()` would make the pipeline exactly-once.
- E. Setting `isolation.level=read_committed` prevents the duplicates.

### Question 7 — `[FUND · Log compaction · Single]`
A topic stores the latest profile per `userId` with `cleanup.policy=compact`. A deletion is published as a record with key `user-42` and a **null value**. Consumers that were offline for **3 days** and then restart from their committed offset notice they never observed the deletion for `user-42`. Which configuration explains this?
- A. `log.cleaner.min.compaction.lag.ms` defaults to 0, so the tombstone was compacted immediately with all other records.
- B. `log.cleaner.delete.retention.ms` defaults to 86,400,000 ms (24 hours); tombstones older than that can be removed by the cleaner, so consumers lagging more than 24 hours may miss them.
- C. `min.cleanable.dirty.ratio` defaults to 0.5, which forces tombstones to be deleted as soon as 50% of the log is dirty.
- D. Compacted topics do not support null values; the record was rejected by the broker.

### Question 8 — `[DEV · Transactions · Single]`
A consume-transform-produce application reads from topic `in`, writes to topic `out`, and must guarantee that output records and the consumed offsets are committed **atomically** (exactly-once). The developer configures a producer with `transactional.id=ctp-1` and `enable.idempotence=true`. Which sequence of calls and consumer setting completes the design?
- A. `initTransactions()` once; per batch: `beginTransaction()` → `send()` → `sendOffsetsToTransaction(offsets, consumer.groupMetadata())` → `commitTransaction()`; downstream consumers use `isolation.level=read_committed`.
- B. Per batch: `beginTransaction()` → `send()` → `consumer.commitSync()` → `commitTransaction()`; downstream consumers use `isolation.level=read_uncommitted`.
- C. `initTransactions()` per batch; `send()` → `flush()` → `consumer.commitAsync()`; no isolation level change is needed.
- D. Set `enable.auto.commit=true` with `auto.commit.interval.ms=0` so offsets are committed together with each `send()`.

### Question 9 — `[TEST · Kafka Streams testing · Single]`
A team wants **fast unit tests** for a Kafka Streams topology (a windowed aggregation with a state store) that run in CI in under a second per test, without starting any container or broker. Which tool is the correct choice?
- A. Testcontainers with the `apache/kafka:4.3.1` image, one container per test.
- B. `TopologyTestDriver` from `kafka-streams-test-utils`, piping records with `TestInputTopic` and asserting with `TestOutputTopic`, advancing wall-clock/stream time as needed.
- C. `MockProducer` and `MockConsumer` wired into the `KafkaStreams` instance.
- D. `EmbeddedKafkaCluster` from Spring Kafka, because state stores require a real broker for changelog topics.

### Question 10 — `[CONNECT · Schema Registry · Multi — Choose 2]`
A subject `orders-value` uses the **default** compatibility level of Confluent Schema Registry. The team plans to (1) **remove** the optional field `coupon` and (2) **add** a new field `channel` with a default value `"web"`. Consumers will be upgraded **before** producers. Which two statements are correct? (Choose two.)
- A. The default compatibility level is `BACKWARD`, which allows deleting fields and adding fields **with defaults**, so both changes register successfully.
- B. The default compatibility level is `FORWARD`, so adding `channel` requires no default value.
- C. Under `BACKWARD` compatibility a consumer using the new schema can read data written with the old schema, which is exactly the "consumers first" upgrade order.
- D. Both changes are rejected because `BACKWARD` only allows adding fields, never removing them.
- E. The subject name must be changed to `orders-value-v2` because Schema Registry does not support multiple versions per subject.

### Question 11 — `[DEV · Producer config matching · Single]`
*(Matching-style.)* A developer is mapping Kafka 4.3 **producer defaults** to their behavior. Which set of pairings is entirely correct?
- A. `linger.ms` = 0 → send immediately · `batch.size` = 16,384 bytes · `delivery.timeout.ms` = 30,000 ms · `max.block.ms` = 60,000 ms.
- B. `linger.ms` = 5 ms → wait up to 5 ms to fill a batch · `batch.size` = 16,384 bytes → per-partition batch cap · `delivery.timeout.ms` = 120,000 ms → upper bound for send() including retries · `max.block.ms` = 60,000 ms → how long send()/metadata fetch may block when the buffer is full.
- C. `linger.ms` = 5 ms · `batch.size` = 1,048,576 bytes · `delivery.timeout.ms` = 120,000 ms · `max.block.ms` = 30,000 ms.
- D. `linger.ms` = 100 ms · `batch.size` = 16,384 bytes · `delivery.timeout.ms` = 120,000 ms · `max.block.ms` = 60,000 ms → time a consumer blocks in poll().

### Question 12 — `[FUND · KRaft · Multi — Choose 2]`
A team is designing a production Apache Kafka 4.3 cluster. Which two statements about KRaft mode are correct? (Choose two.)
- A. Cluster metadata is stored in the internal `__cluster_metadata` topic replicated across the controller quorum; ZooKeeper is no longer used or supported.
- B. Running `process.roles=broker,controller` (combined mode) on every node is the recommended production layout because it minimizes the number of JVMs.
- C. The controller quorum should have an odd number of voters, typically 3 or 5, so the cluster tolerates the loss of 1 or 2 controllers respectively.
- D. `zookeeper.connect` must still be configured so that clients can discover the bootstrap brokers.
- E. Each broker must be formatted with `kafka-storage.sh format` using a different `cluster.id` for isolation.

### Question 13 — `[OBS · Broker metrics · Multi — Choose 2]`
After a broker in a 3-node cluster crashes, an operator inspects JMX metrics. Which two observations are **expected and correct** while the broker is down? (Choose two.)
- A. `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` is greater than 0 on the surviving leaders of partitions that had a replica on the dead broker.
- B. `kafka.controller:type=KafkaController,name=ActiveControllerCount` summed across all controllers is 0 until the broker restarts.
- C. If `unclean.leader.election.enable=false` and the dead broker was the only in-sync replica for a partition, `OfflinePartitionsCount` becomes greater than 0 for that partition.
- D. `UnderReplicatedPartitions` stays at 0 because `acks=all` producers automatically create new replicas on the surviving brokers.
- E. `records-lag-max` on the broker increases because the broker tracks consumer lag internally.

### Question 14 — `[STREAMS · Exactly-once · Single]`
A Kafka Streams application (Kafka 4.3 client, brokers on 4.3) is switched from the default processing guarantee to `processing.guarantee=exactly_once_v2`. After the change, throughput drops noticeably even though the topology is unchanged. What is the MOST likely explanation?
- A. EOS v2 requires one transactional producer per task, which is why it is slower than the older `exactly_once`.
- B. With EOS enabled the default `commit.interval.ms` changes from 30,000 ms to 100 ms, so transactions are committed far more frequently; raising `commit.interval.ms` trades latency for throughput.
- C. `exactly_once_v2` disables state store caching entirely, so every update is written to RocksDB and the changelog.
- D. The brokers must be upgraded to at least 4.4 for EOS v2; until then the client falls back to a slow compatibility path.

### Question 15 — `[DEV · Consumer protocol · Single]`
A team migrates consumers to the **new consumer rebalance protocol** (KIP-848) on Apache Kafka 4.3 by setting `group.protocol=consumer`. Which statement about this configuration is correct?
- A. The client-side `partition.assignment.strategy` still decides the assignment; `CooperativeStickyAssignor` should be set for incremental rebalances.
- B. Partition assignment is computed **server-side** by the group coordinator using a broker-configured assignor (`uniform` or `range`); rebalances are incremental and `partition.assignment.strategy` / `session.timeout.ms` client settings are not used.
- C. The new protocol requires ZooKeeper-based coordination and therefore is unavailable on KRaft clusters.
- D. `group.protocol=consumer` is the default in 4.3 and cannot be changed back to `classic`.

### Question 16 — `[FUND · Partitions & ordering · Single]`
An `orders` topic has 6 partitions and producers use `orderId` as the key. A team increases the topic to 12 partitions to add consumer capacity. Which consequence is correct?
- A. Existing records are redistributed across the 12 partitions so that each key maps consistently to its new partition.
- B. New records for a given key may land on a different partition than older records for the same key, so per-key ordering across the change is no longer guaranteed; existing data stays where it is.
- C. Ordering is unaffected because Kafka guarantees global ordering across all partitions of a topic.
- D. The change fails because partition count can only be reduced, not increased, on a keyed topic.

### Question 17 — `[CONNECT · Distributed worker · Multi — Choose 2]`
A team runs Kafka Connect in **distributed** mode with three workers sharing `group.id=connect-cluster`. Which two statements are correct? (Choose two.)
- A. Connector and task configurations, source offsets, and statuses are stored in three compacted internal topics, by default `connect-configs` (1 partition), `connect-offsets` (25 partitions) and `connect-status` (5 partitions).
- B. Connectors are created and managed through the REST API (default port 8083); `tasks.max` sets the upper bound on parallel tasks a connector may spawn.
- C. Source connector offsets are stored in the consumer group `connect-cluster` in `__consumer_offsets`.
- D. Distributed mode requires ZooKeeper to elect the Connect leader worker.
- E. Each worker must run the same set of connectors defined in its `connect-distributed.properties` file.

### Question 18 — `[DEV · auto.offset.reset · Single]`
A brand-new consumer application with `group.id=audit-v2` starts against an existing topic with 30 days of retained data. The developer expects it to process the full history but it only receives records produced **after** it started. A second run with `auto.offset.reset=none` throws an exception immediately. Which explanation is correct?
- A. `auto.offset.reset` defaults to `latest`, so a group with no committed offsets starts at the log end; `none` throws `NoOffsetForPartitionException` when no committed offset exists. Use `earliest` for the first run.
- B. `auto.offset.reset` defaults to `earliest`; the missing history is caused by `fetch.min.bytes=1`.
- C. The group must be pre-created with `kafka-consumer-groups.sh --reset-offsets --to-earliest` before any consumer can read history.
- D. `auto.offset.reset=none` means "no reset ever", which is the recommended production value for new groups.

### Question 19 — `[OBS · Timeouts · Single]`
A Kafka 4.3 consumer with default configuration processes a poison record that takes **50 seconds** of CPU work inside the `poll()` loop. Heartbeats are sent by the background thread. Which timeout, if any, evicts this consumer from the group?
- A. `session.timeout.ms` (45,000 ms) expires because no heartbeat is sent during processing.
- B. Neither timeout: the heartbeat thread keeps the session alive and 50 seconds is below `max.poll.interval.ms` (300,000 ms), so the consumer stays in the group.
- C. `heartbeat.interval.ms` (3,000 ms) is exceeded, which immediately triggers a rebalance.
- D. `request.timeout.ms` (30,000 ms) expires and the coordinator removes the member.

### Question 20 — `[STREAMS · Windowing · Single]`
A retail dashboard needs, every **1 minute**, the revenue of the **last 5 minutes** (so each record contributes to five results). Late events up to 30 seconds must still be counted. Which window definition is correct?
- A. `TimeWindows.ofSizeAndGrace(Duration.ofMinutes(5), Duration.ofSeconds(30))` — a tumbling window.
- B. `TimeWindows.ofSizeAndGrace(Duration.ofMinutes(5), Duration.ofSeconds(30)).advanceBy(Duration.ofMinutes(1))` — a hopping window.
- C. `SessionWindows.ofInactivityGapAndGrace(Duration.ofMinutes(5), Duration.ofSeconds(30))`.
- D. `SlidingWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5))`.

### Question 21 — `[FUND · Delivery semantics · Multi — Choose 2]`
Which two statements about delivery semantics in Apache Kafka are correct? (Choose two.)
- A. A consumer that commits offsets **before** processing records achieves at-most-once delivery: a crash after commit but before processing loses those records.
- B. Enabling `enable.idempotence=true` on the producer alone provides end-to-end exactly-once from producer to consumer.
- C. An idempotent producer prevents duplicate writes caused by producer retries within a single producer session to a partition, using a producer ID and per-partition sequence numbers.
- D. Kafka's default consumer configuration (`enable.auto.commit=true`) yields exactly-once because commits happen inside `poll()`.
- E. `acks=0` guarantees at-least-once delivery because the broker never rejects the write.

### Question 22 — `[DEV · Producer errors · Multi — Choose 2]`
A producer's send callback reports several exception types. Which two are **non-retriable (fatal)** and require the application to fix the record or configuration rather than rely on the producer's internal retries? (Choose two.)
- A. `NotLeaderOrFollowerException`
- B. `RecordTooLargeException`
- C. `NotEnoughReplicasException`
- D. `SerializationException`
- E. `NetworkException`

### Question 23 — `[TEST · Unit testing clients · Single]`
A developer wants a **unit test** for a service method that builds a `ProducerRecord` with specific headers and a key derived from the payload and then calls `send()`. The test must assert the exact record sent, run with no broker, and complete in milliseconds. Which approach is correct?
- A. Inject `MockProducer<String, String>` with `autoComplete=true` and matching serializers, call the method, then inspect `mockProducer.history()`.
- B. Start a broker with Testcontainers and consume the record back with a real `KafkaConsumer`.
- C. Use `TopologyTestDriver`, since it is the standard test harness for any Kafka client code.
- D. Use `MockConsumer` and call `addRecord()` to simulate the send.

### Question 24 — `[FUND · Retention · Single]`
A topic is configured with `retention.ms=3600000` (1 hour) and default segment settings (`segment.bytes=1073741824`, `segment.ms=604800000`). Traffic is low (~10 MB/day). An operator notices records **much older than 1 hour** are still readable. Which explanation is correct?
- A. Retention is enforced only on **closed** segments; with low traffic the single active segment never reaches 1 GB or 7 days, so nothing is eligible for deletion yet. Lower `segment.ms` (or `segment.bytes`) to make retention effective.
- B. `retention.ms` cannot be set below `log.retention.hours` (168 hours) at the topic level; the broker silently uses 7 days.
- C. Records are kept because `min.insync.replicas` is 1, which disables retention.
- D. The log cleaner only runs when `cleanup.policy=compact`; with `delete` you must trigger deletion manually.

### Question 25 — `[CONNECT · Converter vs SMT · Single]`
A sink connector reads Avro records (produced with the Confluent Avro serializer) and must (1) deserialize them using Schema Registry and (2) **mask** the `email` field before writing to the destination. Which combination is correct?
- A. `value.converter=org.apache.kafka.connect.json.JsonConverter` for (1) and `transforms=mask` with `MaskField$Value` for (2).
- B. `value.converter=io.confluent.connect.avro.AvroConverter` with `value.converter.schema.registry.url` for (1) and `transforms=mask`, `transforms.mask.type=org.apache.kafka.connect.transforms.MaskField$Value`, `transforms.mask.fields=email` for (2).
- C. `transforms=avro` using an Avro SMT for (1) and `value.converter=MaskFieldConverter` for (2).
- D. `value.converter=io.confluent.connect.avro.AvroConverter` handles both because converters can be configured with a `mask.fields` option.

### Question 26 — `[STREAMS · Parallelism matching · Single]`
*(Matching-style.)* A Kafka Streams application (single sub-topology) reads `orders` (12 partitions) and `customers` (6 partitions), runs on **3 instances** each with `num.stream.threads=2`, and has `num.standby.replicas=1`. Which set of statements is entirely correct?
- A. Tasks = 18 (12 + 6) · each thread runs exactly 3 tasks · standby replicas are extra active tasks that double throughput.
- B. Tasks = 12 (max partition count among input topics) · 6 threads share the 12 tasks (2 tasks per thread when balanced) · each task's state has 1 standby copy on another instance for fast failover, restored from the changelog topic.
- C. Tasks = 6 (min partition count) · adding a 4th instance would add more tasks · standby replicas are written to a repartition topic.
- D. Tasks = 12 · only 3 threads are used because the number of threads is capped at the number of instances · standby replicas are disabled under EOS v2.

### Question 27 — `[DEV · Static membership · Single]`
A consumer group of 20 pods on Kubernetes is redeployed with a rolling restart. Each pod restart triggers **two** rebalances (leave + rejoin), causing minutes of paused consumption. The team wants to eliminate rebalances during restarts that complete within about 1 minute, **without** changing partition assignment logic. Which change is correct?
- A. Set a unique, stable `group.instance.id` per pod (static membership) and keep `session.timeout.ms` above the restart duration; a member rejoining within the session timeout resumes its previous assignment without a rebalance.
- B. Set `heartbeat.interval.ms=60000` so the coordinator waits a minute before noticing the pod left.
- C. Set `group.id` to a different value on each pod so no rebalance can occur.
- D. Set `max.poll.interval.ms=60000` to allow the pod to restart within the poll interval.

### Question 28 — `[OBS · Producer health · Single]`
A producer application intermittently throws `TimeoutException: Failed to allocate memory within the configured max blocking time 60000 ms` from `send()`. The JMX metric `buffer-available-bytes` is near 0 and `record-queue-time-avg` is very high, while the broker shows elevated `produce-throttle-time-avg` for this client. What is the MOST accurate diagnosis?
- A. The broker is applying a **producer quota** (`producer_byte_rate`) to this client, delaying responses; batches accumulate until `buffer.memory` (32 MB) is exhausted and `send()` blocks up to `max.block.ms` then fails. Raise the quota or throttle the producer.
- B. `linger.ms` is too high, so records never leave the buffer; set `linger.ms=0`.
- C. The topic has too many partitions, so `batch.size` (16 KB) is multiplied beyond `buffer.memory`; reduce partitions.
- D. `delivery.timeout.ms` is too low; increase it to 600,000 ms.

### Question 29 — `[DEV · No data loss · Multi — Choose 2]`
A financial application must **never lose an acknowledged record** even if one broker fails, and must not write duplicates on retry. The topic has a replication factor of 3. Which two configuration choices are required? (Choose two.)
- A. Producer `acks=all` with `enable.idempotence=true` (retries left at the default `Integer.MAX_VALUE`).
- B. Topic `min.insync.replicas=2`.
- C. Producer `acks=1` with `retries=10` to keep latency low.
- D. Broker `unclean.leader.election.enable=true` so a leader is always available.
- E. Topic `min.insync.replicas=3` so every replica must acknowledge.

### Question 30 — `[FUND · Share groups · Single]`
A team on Apache Kafka 4.3 has a work-queue use case: thousands of independent jobs per second on a 6-partition topic, each job must be processed once with an explicit acknowledgement, jobs that fail should be redelivered, and they want **more than 6** consumers to process concurrently. Ordering is irrelevant. Which feature fits best?
- A. A classic consumer group with 20 members; the extra 14 members share the load of the 6 partitions.
- B. A **share group** (Queues for Kafka, KIP-932, GA in 4.2): consumers cooperatively consume records from the same partitions with per-record acknowledgement (accept/release/reject) and delivery-attempt counting, without partition ownership or ordering guarantees.
- C. Kafka Streams with `num.stream.threads=20` to create 20 tasks over the 6 partitions.
- D. A consumer group with `partition.assignment.strategy=RoundRobinAssignor`, which assigns each partition to multiple consumers.
