# 📝 Practice Questions — Week 6: Kafka Streams

> **28 questions** · real CCDAK exam style, difficulty ≥ real exam · covers the full Week 6 material (Kafka 4.3 Streams defaults, DSL, windows, joins, state, EOS v2, Processor API, `TopologyTestDriver`, ksqlDB) plus 3 review questions from Weeks 3–5.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (number to choose is stated). Config and API names are the **Java** names, as on the real exam.
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

---

### Question 1 — `[STREAMS · Architecture · Single]`

A team has written a Kafka Streams application that aggregates payment events. The operations lead asks how to deploy it and how to scale it later when traffic grows. Which statement is **correct**?

- A. The JAR must be submitted to a Kafka Streams cluster running on the brokers; scaling is done by adding stream workers to that cluster
- B. The application is a standalone JVM process that embeds the `kafka-streams` library; scaling is done by starting more instances with the **same** `application.id`, up to the number of input partitions
- C. The application must run inside a Kafka Connect worker as a custom SMT; scaling is done through `tasks.max`
- D. The application is a standalone process, but every instance must use a **different** `application.id` so the brokers can tell them apart

### Question 2 — `[STREAMS · Tasks & threads · Single]`

A Streams application reads a single input topic with **6 partitions** and performs a `groupByKey().count()`. It is deployed as **4 instances**, each configured with `num.stream.threads=2`. How many stream threads across the deployment will actually be processing records?

- A. 8 — every configured thread receives at least one task
- B. 6 — the application has 6 tasks, so 2 of the 8 threads stay idle
- C. 4 — one task per instance, the extra threads are used only for standby replicas
- D. 12 — 6 tasks for the source sub-topology plus 6 tasks for the aggregation sub-topology

### Question 3 — `[STREAMS · KStream vs KTable · Single]`

A topic `account-balance` receives one record per balance change, keyed by `accountId`, with the new balance as the value. A downstream Streams application must always work with the **current balance** of each account and must treat a record with a `null` value as "account closed, remove it". Which abstraction should the developer use to read the topic?

- A. `builder.stream("account-balance")` — a `KStream`, because balance changes are events
- B. `builder.table("account-balance")` — a `KTable`, because records are upserts per key and a `null` value is a tombstone that deletes the key
- C. `builder.globalTable("account-balance")` — a `GlobalKTable`, because balances must be visible to every instance
- D. `builder.stream("account-balance").groupByKey().reduce((old, cur) -> cur)` — the only way to get the latest value per key

### Question 4 — `[STREAMS · Repartitioning · Multi — Choose 2]`

A developer notices that a new internal topic named `orders-app-KSTREAM-KEY-SELECT-0000000002-repartition` appeared after deploying a topology that ends with `groupByKey().count()`. Which **two** DSL operations, if placed before the aggregation, would cause Kafka Streams to create such a repartition topic? (Choose two.)

- A. `mapValues((k, v) -> v.toUpperCase())`
- B. `selectKey((k, v) -> v.customerId())`
- C. `filter((k, v) -> v.amount() > 0)`
- D. `map((k, v) -> KeyValue.pair(k, v.amount()))`
- E. `peek((k, v) -> log.info("{} {}", k, v))`

### Question 5 — `[STREAMS · Internal topics · Single]`

A Streams application with `application.id=clicks-agg` runs the topology `builder.stream("clicks").groupByKey().count(Materialized.as("clicks-store")).toStream().to("clicks-per-user")`. The input topic `clicks` has 12 partitions. Which internal topics does Kafka Streams create, and with what configuration?

- A. `clicks-agg-clicks-store-changelog` with `cleanup.policy=compact` and 12 partitions; no repartition topic because the key is unchanged
- B. `clicks-agg-clicks-store-changelog` and `clicks-agg-clicks-store-repartition`, both with 12 partitions
- C. `clicks-agg-clicks-store-changelog` with `cleanup.policy=delete` and `retention.ms=604800000`
- D. No internal topics — `count()` keeps its state only in the local RocksDB store

### Question 6 — `[STREAMS · Windowing · Single]`

A monitoring team wants the number of failed logins per user **over the last 5 minutes**, refreshed **every minute**, so that each event contributes to several overlapping results. Which window definition matches the requirement?

- A. `TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5))`
- B. `TimeWindows.ofSizeAndGrace(Duration.ofMinutes(5), Duration.ofSeconds(30)).advanceBy(Duration.ofMinutes(1))`
- C. `SessionWindows.ofInactivityGapAndGrace(Duration.ofMinutes(5), Duration.ofMinutes(1))`
- D. `SlidingWindows.ofTimeDifferenceAndGrace(Duration.ofMinutes(1), Duration.ofMinutes(5))`

### Question 7 — `[STREAMS · Windowing · Single]`

An e-commerce company wants to group a shopper's page views into a **visit**: a visit ends when the shopper has been inactive for **30 minutes**, regardless of how long the visit lasted. Which window type should be used?

- A. Tumbling window of 30 minutes, because every visit is capped at 30 minutes
- B. Hopping window of 30 minutes advancing by 5 minutes, to catch visits that straddle window boundaries
- C. Session window with a 30-minute inactivity gap — windows are dynamically sized and close only after the gap elapses
- D. Sliding window with a 30-minute time difference, because it only creates windows where records exist

### Question 8 — `[STREAMS · Grace period · Single]`

A windowed count uses `TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(1))`. Mobile clients buffer events offline and send them up to 2 minutes late with their original event timestamps. The team observes that these late events never appear in the counts, and the `dropped-records-total` metric increases. What is the most appropriate fix?

- A. Increase the window size to 3 minutes so late events fall into the same window
- B. Switch to `TimeWindows.ofSizeAndGrace(Duration.ofMinutes(1), Duration.ofMinutes(2))` so records arriving up to 2 minutes after window end are still accepted
- C. Set `default.timestamp.extractor=WallclockTimestampExtractor` so events are timestamped on arrival
- D. Set `deserialization.exception.handler=LogAndContinueExceptionHandler` to stop dropping records

### Question 9 — `[STREAMS · suppress · Multi — Choose 2]`

A billing team computes revenue per merchant per hourly tumbling window and wants **exactly one** record per merchant per hour written to the output topic, containing the final total, instead of a stream of intermediate updates. Which **two** statements about implementing this with `suppress()` are correct? (Choose two.)

- A. Use `.suppress(Suppressed.untilWindowCloses(BufferConfig.unbounded()))`; the window must be defined with an explicit grace period, and the final result is emitted only after `window end + grace` has passed in stream time
- B. Use `.suppress(Suppressed.untilTimeLimit(Duration.ofHours(1), BufferConfig.maxRecords(1000).emitEarlyWhenFull()))`; this guarantees a single final result per window
- C. Setting `statestore.cache.max.bytes=0` achieves the same effect as `suppress()` because it disables intermediate updates
- D. If no new records arrive on the input topic, the final result of the last window is not emitted until stream time advances past the window's close, because stream time only moves with incoming records
- E. `suppress()` can only be applied to `KStream`, so the windowed `KTable` must first be converted with `toStream()`

### Question 10 — `[STREAMS · Record cache · Single]`

A developer runs `stream.groupByKey().count().toStream().to("counts")` locally and produces 1,000 records with the same key within one second. They expect 1,000 records in `counts` (1, 2, 3, ... 1000) but see only a handful, the last one being `1000`. What explains this behavior, and how can they observe every intermediate count?

- A. Kafka Streams drops intermediate results by default; set `processing.guarantee=exactly_once_v2` to keep them
- B. The record cache (`statestore.cache.max.bytes`, default 10 MB) deduplicates updates per key and flushes downstream on commit (`commit.interval.ms`, default 30000); set the cache to 0 to forward every update — the final count is identical either way
- C. The output topic is compacted, so the broker removed the older values; set `cleanup.policy=delete` on `counts`
- D. `count()` uses a hopping window by default; use `TimeWindows.ofSizeWithNoGrace` to emit per record

### Question 11 — `[STREAMS · Join matrix · Multi — Choose 2]`

Which **two** join types in the Kafka Streams DSL do **not** require the two inputs to be co-partitioned? (Choose two.)

- A. `KStream`-`KStream` inner join with `JoinWindows`
- B. `KStream`-`GlobalKTable` join
- C. `KStream`-`KTable` left join
- D. `KTable`-`KTable` foreign-key join using a `Function<V, KO> foreignKeyExtractor`
- E. `KTable`-`KTable` outer join on the primary key

### Question 12 — `[STREAMS · Stream-stream join · Single]`

A fraud team wants to correlate `payment-authorized` events with `payment-captured` events for the same `paymentId` when the capture happens **within 10 minutes** of the authorization. Both topics have 8 partitions and are produced by the same service with the default partitioner. Which implementation is correct?

- A. `authorized.join(captured, joiner)` — a plain `KStream`-`KStream` join, since both are already co-partitioned
- B. `authorized.join(captured, joiner, JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(10)), StreamJoined.with(Serdes.String(), authSerde, captureSerde))` — a `KStream`-`KStream` join always needs a `JoinWindows`
- C. `authorized.join(captured.toTable(), joiner)` — convert one side to a `KTable` to avoid the window requirement
- D. `authorized.join(builder.globalTable("payment-captured"), (k, v) -> k, joiner)` — a `GlobalKTable` join, since no co-partitioning check is needed

### Question 13 — `[STREAMS · Co-partitioning · Single]`

A Streams application joins `KStream<String, Order>` from topic `orders` (12 partitions) with `KTable<String, Customer>` from topic `customers` (6 partitions), both keyed by `customerId`. On startup the application fails with `TopologyException: ... topics are not co-partitioned`. Which change resolves the error **without** changing the existing topics?

- A. Set `num.stream.threads=12` so there is one thread per `orders` partition
- B. Call `orders.repartition(Repartitioned.numberOfPartitions(6))` before the join so that both inputs have the same partition count, accepting one extra internal topic
- C. Replace the `KTable` with a `builder.globalTable("customers")` while keeping the same two-argument `join(table, joiner)` call
- D. Set `topology.optimization=all`; Kafka Streams will automatically align partition counts at runtime

### Question 14 — `[STREAMS · GlobalKTable · Single]`

An `orders` stream is keyed by `orderId`; each value contains a `productId`. A `products` topic (500 records, rarely updated, 3 partitions) is keyed by `productId`. The team must enrich every order with the product name, and `orders` has 24 partitions. Which approach requires **no** repartitioning and no partition-count alignment?

- A. Read `products` as a `KTable` and call `orders.join(productsTable, joiner)`
- B. Read `products` as a `GlobalKTable` and call `orders.join(productsGlobal, (orderId, order) -> order.productId(), joiner)`, using the `KeyValueMapper` to look up by the foreign key
- C. `orders.selectKey((k, v) -> v.productId()).join(productsTable, joiner)` after increasing `products` to 24 partitions
- D. Read both as `KTable` and use a foreign-key join with `outerJoin`

### Question 15 — `[STREAMS · Exactly-once · Multi — Choose 2]`

A team switches a Streams application from the default processing guarantee to `processing.guarantee=exactly_once_v2` without changing any other Streams configuration. Which **two** statements describe what changes as a result? (Choose two.)

- A. `commit.interval.ms` defaults change from 30000 ms to 100 ms, and each commit becomes a Kafka transaction that atomically writes output records, state changelogs, and consumer offsets
- B. The application's internal consumer is switched to `isolation.level=read_committed` and the producer becomes idempotent and transactional, with **one producer per stream thread**
- C. Every instance must now use a distinct `application.id`, because transactional producers cannot share a group
- D. Side effects performed in `foreach()` or `peek()` — such as REST calls — are also executed exactly once
- E. The number of stream tasks doubles, because each task now needs a dedicated transaction coordinator

### Question 16 — `[STREAMS · EOS broker requirements · Single]` *(Week 3 review)*

A developer enables `processing.guarantee=exactly_once_v2` on a laptop cluster with a **single broker** (Kafka 4.3, default broker settings) and the application fails on startup with an error about the transaction state log. Why?

- A. `exactly_once_v2` requires KRaft dynamic quorum with at least 3 controllers
- B. The `__transaction_state` topic defaults to `transaction.state.log.replication.factor=3` and `transaction.state.log.min.isr=2`, so a 1-broker cluster cannot create it; lower both to 1 for development or run at least 3 brokers
- C. `exactly_once_v2` requires broker version 4.0 or newer; the laptop cluster is too old
- D. `exactly_once_v2` is only available on Confluent Platform, not on Apache Kafka

### Question 17 — `[STREAMS · Standby replicas · Single]`

A Streams application holds about 40 GB of state per instance. When an instance crashes, its tasks migrate to another instance and processing pauses for roughly 15 minutes while state is rebuilt from the changelog topics. The business wants failover in seconds. Which configuration change addresses this directly?

- A. Set `num.stream.threads` to a higher value so restoration runs in parallel
- B. Set `num.standby.replicas=1` (default 0) and provision at least n+1 instances, so a warm copy of each task's state already exists on another instance and is caught up continuously
- C. Set `statestore.cache.max.bytes` to 40 GB so the state fits in memory
- D. Use `withLoggingDisabled()` on the state stores so there is no changelog to replay

### Question 18 — `[STREAMS · State stores & changelog · Multi — Choose 2]`

Which **two** statements about Kafka Streams state stores are correct? (Choose two.)

- A. Both RocksDB (persistent) and in-memory stores are fault tolerant by default, because updates are written to a changelog topic named `<application.id>-<store-name>-changelog`
- B. The changelog topic of a key-value store uses `cleanup.policy=compact`, while the changelog of a windowed store uses `compact,delete` because its keys embed window timestamps
- C. In-memory stores cannot be used with `exactly_once_v2` because they have no changelog
- D. `state.dir` defaults to a persistent volume path, so restarting an instance never triggers a changelog replay
- E. `GlobalKTable` state is backed by its own compacted changelog topic named `<application.id>-<store>-changelog`

### Question 19 — `[STREAMS · Deserialization errors · Single]`

A Streams application reads Avro records. A producer bug wrote a single malformed record into partition 3. The Streams instance owning partition 3 logs `SerializationException` and shuts down; after every restart it fails on the same record, while other partitions keep working. Which configuration lets the application skip the bad record and continue?

- A. `production.exception.handler=DefaultProductionExceptionHandler`
- B. `deserialization.exception.handler=LogAndContinueExceptionHandler` (the default `LogAndFailExceptionHandler` stops the client on the first undeserializable record)
- C. `StreamsUncaughtExceptionHandler` returning `REPLACE_THREAD`, so a fresh thread retries the partition
- D. `default.timestamp.extractor=LogAndSkipOnInvalidTimestamp`

### Question 20 — `[STREAMS · Uncaught exceptions · Single]`

A new release of a Streams application contains a bug: a `NullPointerException` is thrown inside a `mapValues` lambda for **every** record of a certain type that is present on all partitions. The team has registered a `StreamsUncaughtExceptionHandler`. Which response minimizes damage until a fix is deployed?

- A. `REPLACE_THREAD` — a new thread takes over the task and retries, keeping the application alive
- B. `SHUTDOWN_CLIENT` — only the affected instance stops; the others keep processing
- C. `SHUTDOWN_APPLICATION` — all instances sharing the `application.id` shut down cooperatively, because the error is deterministic and would recur on every instance
- D. No handler is needed; Kafka Streams automatically routes the failing record to a dead letter topic

### Question 21 — `[STREAMS · Dead letter queue · Single]` *(Week 5 review)*

A team runs Kafka 4.3 with a Kafka Connect JDBC **sink** connector and a Kafka Streams application. They want both to send records that cannot be processed to a dead letter topic instead of stopping. Which statement is correct?

- A. Only Kafka Connect supports a DLQ (`errors.deadletterqueue.topic.name` with `errors.tolerance=all`); Kafka Streams has no DLQ mechanism
- B. In Connect, `errors.deadletterqueue.topic.name` works only for **sink** connectors with `errors.tolerance=all`; in Kafka Streams (4.2+, KIP-1034) setting `errors.deadletterqueue.topic.name` makes the default exception handlers forward failed records to that topic with `__streams.errors.*` headers
- C. Both Connect and Streams automatically create and write to a DLQ topic named `<app.id>-dlq` without configuration
- D. Streams supports a DLQ only through `StreamsUncaughtExceptionHandler`, which receives the failing record

### Question 22 — `[STREAMS · Punctuation · Single]`

A Processor API processor schedules `context.schedule(Duration.ofSeconds(10), PunctuationType.STREAM_TIME, punctuator)`. A test pipes **60 records** with event timestamps 1 s, 2 s, ..., 60 s into the topology, and the whole batch is processed in 20 seconds of real time. How many times is the punctuator invoked, and how would the answer change with `WALL_CLOCK_TIME`?

- A. 6 times with `STREAM_TIME` (driven by the 60 s of event time); about 2 times with `WALL_CLOCK_TIME` (driven by the 20 s of real time)
- B. 2 times with `STREAM_TIME`; 6 times with `WALL_CLOCK_TIME`
- C. 6 times in both modes — the punctuation type only affects the timestamp passed to the callback
- D. 60 times with `STREAM_TIME` (once per record); 2 times with `WALL_CLOCK_TIME`

### Question 23 — `[STREAMS · Processor API · Multi — Choose 2]`

A developer builds a topology with `Topology.addProcessor("dedupe", supplier, "source")` and attaches a RocksDB store via `addStateStore(storeBuilder, "dedupe")`. Which **two** statements are correct? (Choose two.)

- A. `ProcessorSupplier#get()` must return a **new** `Processor` instance on every call, because each task gets its own processor and store instance
- B. `ProcessorContext#recordMetadata()` returns an empty `Optional` when called from inside a punctuator, because no record is being processed
- C. The processor must call `store.close()` in `Processor#close()` to release RocksDB resources
- D. `context.commit()` immediately and synchronously commits the current offsets and flushes the store
- E. The old `org.apache.kafka.streams.processor.Processor` interface can still be used interchangeably with `org.apache.kafka.streams.processor.api.Processor` in Kafka 4.x

### Question 24 — `[STREAMS · Interactive Queries · Single]`

A Streams application materializes `KTable<String, Long> counts` with `Materialized.as("counts-store")` and exposes a REST endpoint `GET /count/{key}`. With one instance everything works. After scaling to three instances, some keys return `null` from `streams.store(...)`. What is the correct fix?

- A. Set `num.standby.replicas=2` so every instance holds every key
- B. Set `application.server=host:port` on each instance and use `streams.queryMetadataForKey("counts-store", key, serializer)` to find the instance owning the key, then forward the HTTP request to that instance's `activeHost()`
- C. Replace the `KTable` with a `GlobalKTable`, because aggregations always require one for Interactive Queries
- D. Query `__consumer_offsets` for the partition assignment and connect directly to the broker holding the changelog

### Question 25 — `[TEST · TopologyTestDriver · Multi — Choose 2]`

A developer writes JUnit 5 tests for a windowed aggregation and a `WALL_CLOCK_TIME` punctuator using `TopologyTestDriver` from `kafka-streams-test-utils`. Which **two** statements are correct? (Choose two.)

- A. `TopologyTestDriver` requires a running broker reachable at the configured `bootstrap.servers`, which is why the property is mandatory
- B. Input is processed synchronously: after `inputTopic.pipeInput(key, value, timestamp)` the output can be read immediately with `outputTopic.readKeyValue()`, and event time can be advanced with `inputTopic.advanceTime(...)` or explicit record timestamps to close windows
- C. Wall-clock punctuators do not fire on their own in the test driver; the test must call `testDriver.advanceWallClockTime(Duration)` to trigger them
- D. `TopologyTestDriver` can verify rebalance behavior when a second instance joins, as long as two drivers share the same `application.id`
- E. State stores cannot be inspected in tests; assertions must be made only on output topics

### Question 26 — `[STREAMS · Streams Rebalance Protocol · Multi — Choose 2]` *(Week 4 review)*

A platform team upgrades to Kafka 4.3 and wants to adopt the Streams Rebalance Protocol (KIP-1071) for a Kafka Streams application. Which **two** statements are correct? (Choose two.)

- A. It is enabled per application with `group.protocol=streams`; the application then registers as a **streams group** and the broker's group coordinator computes the active/standby task assignment, in the spirit of KIP-848 for plain consumers
- B. It is enabled by setting `partition.assignment.strategy=StreamsPartitionAssignor` on the embedded consumer
- C. Streams groups are inspected with `kafka-streams-groups.sh`; `kafka-consumer-groups.sh` does not list them, and migrating a running application from `classic` to `streams` requires stopping all instances first
- D. The protocol is still Early Access in Kafka 4.3 and must not be used in production
- E. When enabled, `num.standby.replicas` is ignored because standby tasks are not supported by the new protocol

### Question 27 — `[STREAMS · ksqlDB · Single]`

An analyst opens the ksqlDB CLI against a table created with `CREATE TABLE pageviews_per_user AS SELECT user_id, COUNT(*) AS cnt FROM pageviews GROUP BY user_id EMIT CHANGES;`. They run two statements:

1. `SELECT user_id, cnt FROM pageviews_per_user WHERE user_id = 'u42';`
2. `SELECT user_id, cnt FROM pageviews_per_user EMIT CHANGES;`

Which statement describes the behavior?

- A. Both are push queries and stream updates until the client disconnects
- B. Statement 1 is a **pull query** that returns the current value for `u42` and terminates; statement 2 is a **push query** that streams every change continuously — and the `CREATE TABLE ... AS SELECT` itself is a persistent query compiled into a Kafka Streams topology
- C. Statement 1 fails, because tables can only be queried with `EMIT CHANGES`
- D. Statement 2 fails, because `EMIT CHANGES` is allowed only on streams, not tables

### Question 28 — `[STREAMS · KafkaStreams lifecycle · Single]`

During a rolling deployment, a health-check calls `streams.store(...)` on a freshly started instance and receives `InvalidStateStoreException: the state store may have migrated to another instance`. The store name and `Materialized` configuration are correct. What is the most likely cause and appropriate handling?

- A. The store was deleted by log compaction; increase `delete.retention.ms` on the changelog topic
- B. The instance is still in the `REBALANCING` state (or restoring state) and has not reached `RUNNING`; the caller should check `streams.state()` (or a `StateListener`) and retry the query once the instance is `RUNNING`
- C. `application.id` must be changed on every deployment so the new instance gets its own store
- D. Interactive Queries require `processing.guarantee=exactly_once_v2`; enable it and restart
