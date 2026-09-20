# ✅ Answers & Explanations — Week 6: Kafka Streams

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-B · 3-B · 4-BD · 5-A · 6-B · 7-C · 8-B · 9-AD · 10-B · 11-BD · 12-B · 13-B · 14-B · 15-AB · 16-B · 17-B · 18-AB · 19-B · 20-C · 21-B · 22-A · 23-AB · 24-B · 25-BC · 26-AC · 27-B · 28-B

---

### Question 1 — Answer: **B**

- **Why correct:** Kafka Streams is a **client library** packaged inside your own JVM application. There is no Streams cluster and nothing runs on the brokers. Instances that share the same `application.id` form one consumer group (`application.id` **is** the `group.id`), and Kafka assigns the stream tasks (one per input partition) across them. Useful parallelism is capped at the number of tasks, i.e. the number of input partitions.
- **Why the others are wrong:** A — there is no "Streams cluster" or "stream worker"; that describes Flink/Spark. C — Kafka Connect moves data in and out of Kafka; an SMT is a per-record transform, not a stateful stream processor. D — instances with **different** `application.id`s are different applications: each would read all partitions independently and produce duplicate outputs, with separate state and internal topics.
- 🧠 **Key point / trap:** "library, not a cluster" and "scale = more instances with the same `application.id`, up to #partitions".
- 📎 Source: `resources/streams-core-concepts-architecture.md` (Stream Processing Application, Parallelism model); `README.md` Buổi A §1–2.

### Question 2 — Answer: **B**

- **Why correct:** The number of tasks of a sub-topology equals the **maximum partition count** of its input topics: 6 partitions → **6 tasks**. `groupByKey()` keeps the key, so no repartition topic and no second sub-topology is created. 4 instances × 2 threads = 8 threads, but only 6 tasks exist, so exactly **6 threads** process records and 2 stay idle.
- **Why the others are wrong:** A — threads beyond the task count never receive a task. C — tasks are distributed across threads, not one per instance; standby replicas are off by default (`num.standby.replicas=0`) and are not what idle threads do. D — a repartition topic would create a second sub-topology only after a key-changing operation such as `groupBy` or `selectKey`; `groupByKey` does not.
- 🧠 **Key point / trap:** tasks = max input partitions per sub-topology; total useful threads ≤ tasks. To use more threads, add partitions.
- 📎 Source: `resources/streams-core-concepts-architecture.md` (Parallelism model, Threading model); `README.md` Buổi A §2.

### Question 3 — Answer: **B**

- **Why correct:** A `KTable` interprets the topic as a **changelog**: each record is an UPSERT for its key and a record with a `null` value is a **tombstone** that deletes the key. That is exactly "current balance per account, `null` = remove". The store behind it also enables Interactive Queries later.
- **Why the others are wrong:** A — a `KStream` treats every record as an independent INSERT; you would see each balance change, not the current value, and `null` values would be ignored by most operators rather than deleting anything. C — a `GlobalKTable` also has upsert semantics, but it copies **all** partitions to **every** instance; for a large, frequently-updated fact table that wastes memory/disk and is only justified for small reference data or non-key joins. D — `reduce` gives the latest value but does not treat `null` as a delete (null values are dropped before aggregation) and needlessly adds an aggregation store; `builder.table()` is the idiomatic answer.
- 🧠 **Key point / trap:** "latest value per key / upsert / null = delete" → `KTable`. "Every event matters" → `KStream`. "Small reference data on every instance" → `GlobalKTable`.
- 📎 Source: `resources/streams-core-concepts-architecture.md` (KStream, KTable, GlobalKTable); `README.md` Buổi A §3 table.

### Question 4 — Answer: **B, D**

- **Why correct:** Operations that can **change the key** mark the stream for repartitioning: `selectKey` (B) and `map` (D) — as well as `flatMap`, `groupBy`, and `process`. The repartition topic (`<application.id>-<name>-repartition`) is physically created only when a stateful operation (aggregation/join) follows, which `groupByKey().count()` does.
- **Why the others are wrong:** A — `mapValues` cannot touch the key, so it never triggers repartitioning (this is why it is preferred over `map` when only the value changes). C — `filter` keeps the key. E — `peek` is a side-effect operator that forwards records unchanged.
- 🧠 **Key point / trap:** key-changing (`map/flatMap/selectKey/groupBy`) + stateful = repartition topic. `groupByKey`, `mapValues`, `filter`, `processValues` never repartition.
- 📎 Source: `resources/streams-dsl-api.md` (Stateless transformations table, "marks the stream for re-partitioning"); `README.md` Buổi A §4.

### Question 5 — Answer: **A**

- **Why correct:** `count(Materialized.as("clicks-store"))` creates a state store, and every fault-tolerant store is backed by a changelog topic named `<application.id>-<store-name>-changelog` → `clicks-agg-clicks-store-changelog`. Key-value changelogs are **compacted** (`cleanup.policy=compact`) so they can be replayed to rebuild the store; the changelog has the same partition count as the task count, **12**. Because `groupByKey()` keeps the input key, no repartition topic is needed.
- **Why the others are wrong:** B — no key change occurred, so no repartition topic; repartition topic names also derive from the operator name, not the store name. C — `delete` with 7-day retention would eventually lose state needed for restoration; key-value changelogs are compacted (windowed changelogs use `compact,delete`). D — local RocksDB alone is not fault tolerant; the changelog exists precisely so another instance can restore the store.
- 🧠 **Key point / trap:** `-changelog` = compacted backup of a state store; `-repartition` = only after a key change. Both are prefixed with `application.id`.
- 📎 Source: `resources/streams-core-concepts-architecture.md` (Changelog topics and fault tolerance); `resources/streams-processor-api.md` (State stores / logging); `README.md` Buổi A §5.

### Question 6 — Answer: **B**

- **Why correct:** "Last 5 minutes, refreshed every minute, each event in several results" describes a **hopping** window: fixed size 5 minutes with an **advance interval** of 1 minute (`advanceBy` smaller than the size), so windows overlap and each record belongs to 5 windows. Hopping windows are built with `TimeWindows.ofSizeAndGrace(...).advanceBy(...)` (or `ofSizeWithNoGrace(...).advanceBy(...)`).
- **Why the others are wrong:** A — without `advanceBy`, size = advance → a **tumbling** window; each event counts in exactly one window and results are not refreshed every minute. C — a session window is data-driven (inactivity gap), not fixed-size or periodically refreshed. D — sliding windows are defined by the time difference between records and are used for aggregations/joins where you want exact "within N of each other" semantics; also the arguments are swapped (time difference 1 min, grace 5 min).
- 🧠 **Key point / trap:** tumbling = size equals advance (no overlap); hopping = `advanceBy` < size (overlap). The new API requires an explicit grace choice (`WithNoGrace` / `AndGrace`); `TimeWindows.of()` was removed in 4.0.
- 📎 Source: `resources/streams-dsl-api.md` (Windowing table and code); `README.md` Buổi A §6 table.

### Question 7 — Answer: **C**

- **Why correct:** A **session window** groups records for a key into dynamically sized windows separated by an **inactivity gap**. A visit stays open as long as page views keep arriving within 30 minutes of the previous one and closes only after 30 minutes of silence — exactly the requirement. API: `SessionWindows.ofInactivityGapAndGrace(Duration.ofMinutes(30), grace)` (or `ofInactivityGapWithNoGrace`).
- **Why the others are wrong:** A — tumbling windows are fixed and aligned to the epoch; a visit that spans a boundary is split, and a visit can be longer than 30 minutes. B — hopping windows overlap and are fixed-size; they do not model "ends after inactivity". D — sliding windows are fixed-size (the time difference) and are meant for "records within N of each other" aggregations/joins, not variable-length sessions.
- 🧠 **Key point / trap:** "inactivity", "session", "gap" → `SessionWindows`. Sessions for the same key that come within the gap of each other are **merged** (the aggregation needs a `Merger`).
- 📎 Source: `resources/streams-dsl-api.md` (Windowing: Session window); `README.md` Buổi A §6.

### Question 8 — Answer: **B**

- **Why correct:** A record whose event timestamp falls into a window that has already **closed** (stream time > window end + grace) is a *late* record and is **dropped** (the `dropped-records-total` metric increments). `ofSizeWithNoGrace` sets grace = 0, so any out-of-order record is dropped. Declaring a **2-minute grace period** keeps the window open long enough to accept records up to 2 minutes after the window end.
- **Why the others are wrong:** A — a bigger window changes the business meaning of the count and still drops records that arrive after the (larger) window has closed. C — wall-clock timestamps would make the counts depend on arrival time and lose event-time semantics; late events would be counted in the wrong window. D — deserialization handlers deal with records that cannot be decoded; late records deserialize fine.
- 🧠 **Key point / trap:** late-arriving data → **grace period**, not window size. Grace increases result latency (final result only after end + grace) and store retention.
- 📎 Source: `resources/streams-dsl-api.md` (Grace period); `resources/streams-core-concepts-architecture.md` (Out-of-order handling); `README.md` Buổi A §6.

### Question 9 — Answer: **A, D**

- **Why correct:** A — `Suppressed.untilWindowCloses(BufferConfig.unbounded())` buffers all intermediate results and emits **exactly one** final record per window once stream time passes `window end + grace`; the window must therefore be declared with a grace period, and the buffer config must be strict (`unbounded()` or a bounded buffer with `shutDownWhenFull()`), because emitting early would break the "final result" contract. D — stream time is the maximum event timestamp seen by the task and **only advances when records arrive**, so a quiet topic delays the emission of the last window's final result until a newer record shows up.
- **Why the others are wrong:** B — `untilTimeLimit(...)` is a rate limiter for any `KTable` and `emitEarlyWhenFull()` explicitly allows early emissions, so it does not guarantee a single final result. C — disabling the cache does the **opposite**: every update is forwarded downstream. E — `suppress()` is a `KTable` operator applied to the windowed `KTable` before `toStream()`.
- 🧠 **Key point / trap:** `suppress(untilWindowCloses)` = one final result per window; requires grace + strict buffer; depends on **stream time**, not wall-clock time.
- 📎 Source: `resources/streams-dsl-api.md` (Suppress operator); `resources/streams-core-concepts-architecture.md` (Time semantics: stream-time); `README.md` Buổi A §6.

### Question 10 — Answer: **B**

- **Why correct:** Aggregation results pass through the **record cache** (`statestore.cache.max.bytes`, default **10 MB** shared by all threads). The cache keeps only the latest value per key and flushes downstream (and to the changelog) when it fills up or at each commit (`commit.interval.ms`, default **30000 ms**). 1,000 updates to one key in one second collapse into a few emitted values ending in `1000`. Setting the cache to 0 (or `Materialized.withCachingDisabled()`) forwards every update; the **final result is the same** either way.
- **Why the others are wrong:** A — Streams never "drops" results; EOS changes atomicity (and lowers `commit.interval.ms` to 100 ms, which would flush more often) but is not the mechanism. C — broker-side compaction would not act within a second and does not explain the local behavior. D — `count()` on an un-windowed grouped stream is not windowed at all.
- 🧠 **Key point / trap:** "aggregation output is batched / fewer records than expected" → record cache + commit interval, not data loss. `cache.max.bytes.buffering` is the deprecated old name.
- 📎 Source: `resources/streams-core-concepts-architecture.md` (Memory management — record caches); `resources/streams-config.md` (`statestore.cache.max.bytes`, `commit.interval.ms`); `README.md` Buổi A §5.

### Question 11 — Answer: **B, D**

- **Why correct:** B — each `GlobalKTable` instance holds **all** partitions of its topic, so a stream record can be looked up regardless of which partition it came from; the join even accepts a `KeyValueMapper` to pick an arbitrary lookup key. D — the `KTable`-`KTable` **foreign-key** join internally creates subscription/response repartition topics and handles the routing itself, so no manual co-partitioning is required.
- **Why the others are wrong:** A, C, E — stream-stream, stream-table, and primary-key table-table joins are all equi-joins on the record key executed inside a task; both inputs must have the **same number of partitions and the same partitioning strategy** so matching keys land in the same task. Streams checks the partition count at startup and throws `TopologyException` if it differs.
- 🧠 **Key point / trap:** "no co-partitioning" → `GlobalKTable` join or FK table-table join. Everything else needs same partition count + same partitioner.
- 📎 Source: `resources/streams-joins.md` (Co-partitioning requirements, Join operations overview table); `README.md` Buổi A §8.

### Question 12 — Answer: **B**

- **Why correct:** A `KStream`-`KStream` join is **always windowed**: you must pass a `JoinWindows` (`ofTimeDifferenceWithNoGrace(Duration.ofMinutes(10))` here) that defines how far apart in event time two records may be to match; `StreamJoined` supplies the serdes. Both topics have 8 partitions and the same partitioner, so co-partitioning holds.
- **Why the others are wrong:** A — there is no un-windowed `KStream.join(KStream, joiner)` overload; the code does not compile. C — turning captures into a `KTable` keeps only the **latest** capture per key and loses the "within 10 minutes" semantics (a stream-table join has no time window). D — a `GlobalKTable` is for slowly changing reference data, not a high-volume event stream; it also has no time window and would replicate all captures to every instance.
- 🧠 **Key point / trap:** stream-stream join = `JoinWindows` mandatory + co-partitioning. Left/outer stream-stream joins emit unmatched results only after the window (plus grace) closes.
- 📎 Source: `resources/streams-joins.md` (KStream-KStream join); `README.md` Buổi A §8.

### Question 13 — Answer: **B**

- **Why correct:** `KStream`-`KTable` joins require co-partitioned inputs. Kafka Streams verifies the **partition count** at startup and fails with `TopologyException` on mismatch (12 vs 6). Calling `repartition(Repartitioned.numberOfPartitions(6))` on the stream writes it through an internal repartition topic with 6 partitions using the default partitioner, aligning it with `customers` without touching the source topics.
- **Why the others are wrong:** A — thread count has nothing to do with partition alignment. C — a `GlobalKTable` join uses a **three-argument** `join(globalTable, keyValueMapper, joiner)`; keeping the two-argument call does not compile, and a `GlobalKTable` is a different design decision (full copy per instance). D — topology optimization merges/reuses topics; it does not fix a co-partitioning violation.
- 🧠 **Key point / trap:** `TopologyException ... not co-partitioned` → align partition counts with `repartition()` (or design topics with equal counts). Streams cannot detect a **partitioner** mismatch — that is on you.
- 📎 Source: `resources/streams-joins.md` (Co-partitioning requirements); `resources/streams-dsl-api.md` (repartition); `README.md` Buổi A §8.

### Question 14 — Answer: **B**

- **Why correct:** `products` is a small, rarely changing **reference table** keyed differently (`productId`) from the stream (`orderId`). A `GlobalKTable` gives every instance a complete local copy, so the join needs neither co-partitioning nor equal partition counts (3 vs 24 is fine), and the `KeyValueMapper` `(orderId, order) -> order.productId()` extracts the foreign key for the lookup.
- **Why the others are wrong:** A — a `KTable` join requires the same key on both sides **and** co-partitioning; `orderId` ≠ `productId` and 24 ≠ 3. C — this works but costs a repartition topic for `orders` (24 partitions of order traffic re-written) plus increasing `products` to 24 partitions — exactly what the question rules out. D — a FK table-table join needs `orders` as a `KTable` (loses per-event semantics) and does not support `outerJoin`.
- 🧠 **Key point / trap:** "enrich stream with small lookup data on a different key" → `KStream`-`GlobalKTable` + `KeyValueMapper`.
- 📎 Source: `resources/streams-joins.md` (KStream-GlobalKTable join); `README.md` Buổi A §3 and §8.

### Question 15 — Answer: **A, B**

- **Why correct:** A — with `exactly_once_v2`, Streams lowers the default `commit.interval.ms` from **30000** to **100** ms, and a commit becomes a **transaction** that atomically publishes output records, changelog updates and consumer offsets. B — Streams overrides the embedded clients: consumer `isolation.level=read_committed`, producer `enable.idempotence=true` with an auto-generated `transactional.id`, using **one transactional producer per stream thread** (the removed `exactly_once` used one per task, which is why v2 scales better).
- **Why the others are wrong:** C — all instances keep the same `application.id`; the `transactional.id` is derived per thread automatically. D — EOS covers Kafka topics, state stores and offsets only; external side effects in `peek`/`foreach` (REST, DB writes) can still run more than once after a failure. E — task count is unchanged; the transaction coordinator is a broker-side module, not a per-task resource.
- 🧠 **Key point / trap:** EOS v2 = 100 ms commits, read_committed consumer, 1 producer/thread, Kafka-to-Kafka only. `exactly_once` and `exactly_once_beta` were removed in 4.0.
- 📎 Source: `resources/streams-config.md` (Processing guarantee details, Consumer and producer configuration overrides); `README.md` Buổi A §9 table.

### Question 16 — Answer: **B**

- **Why correct:** EOS relies on the transaction coordinator and its internal topic `__transaction_state`, created with broker defaults `transaction.state.log.replication.factor=3` and `transaction.state.log.min.isr=2`. A single broker cannot satisfy RF=3, so the topic cannot be created and the transactional producer inside Streams fails at `initTransactions()`. For development, set both to 1 (the Week 1 single-node compose does this) or run 3 brokers.
- **Why the others are wrong:** A — KRaft quorum size is unrelated to transactions. C — `exactly_once_v2` needs brokers **2.5+**, which 4.3 satisfies. D — EOS is a core Apache Kafka feature (KIP-98 / KIP-447).
- 🧠 **Key point / trap:** "EOS fails on 1-broker dev cluster" → transaction state log RF/min.isr. Same trap applies to `__consumer_offsets` (`offsets.topic.replication.factor`).
- 📎 Source: `resources/streams-config.md` (Processing guarantee details: "at least 3 brokers"); Week 3 README §9 (transaction coordinator, `__transaction_state`).

### Question 17 — Answer: **B**

- **Why correct:** By default (`num.standby.replicas=0`) a migrated task must **replay its changelog** from Kafka into a fresh RocksDB before processing resumes — 40 GB takes minutes. A **standby replica** is a shadow copy of the store kept continuously up to date on another instance; on failure Streams assigns the active task to the instance that already has the (nearly) caught-up copy, so failover takes seconds. Cost: 2× storage and at least n+1 instances.
- **Why the others are wrong:** A — more threads do not speed up restoring one task's state and add nothing if there are no spare tasks. C — the record cache is a write-back/dedup buffer, not a way to hold state in memory, and 40 GB of heap is unrealistic. D — disabling logging removes the changelog entirely: no restoration **and** no standby possible — state would simply be lost.
- 🧠 **Key point / trap:** "fast failover / long restoration" → `num.standby.replicas` (default 0). Also keep `state.dir` on a persistent volume so a plain restart replays only the delta.
- 📎 Source: `resources/streams-core-concepts-architecture.md` (Standby replicas); `resources/streams-config.md` (`num.standby.replicas`, `acceptable.recovery.lag`, State directory); `README.md` Buổi A §5.

### Question 18 — Answer: **A, B**

- **Why correct:** A — logging is enabled by default for every store type; RocksDB and in-memory stores alike are backed by `<application.id>-<store-name>-changelog`, so an in-memory store is rebuilt from the changelog after a restart. B — key-value changelogs are **compacted**; windowed/session store changelogs use `compact,delete` because keys contain window timestamps and expired windows can be deleted after retention (`windowstore.changelog.additional.retention.ms`, default 1 day).
- **Why the others are wrong:** C — in-memory stores work with EOS; they have a changelog like any other store. D — `state.dir` defaults to `/tmp/kafka-streams` (`${java.io.tmpdir}`), which is why production deployments must point it to a persistent volume. E — a `GlobalKTable` is restored directly from its **source topic**; it does not get a separate changelog topic.
- 🧠 **Key point / trap:** changelog names, compaction policy per store type, and `state.dir` default are all fair game on the exam.
- 📎 Source: `resources/streams-processor-api.md` (State stores: logging, changelog policies); `resources/streams-config.md` (`state.dir`, `windowstore.changelog.additional.retention.ms`); `README.md` Buổi A §5.

### Question 19 — Answer: **B**

- **Why correct:** Records that cannot be deserialized are handled by the `deserialization.exception.handler`. The default `LogAndFailExceptionHandler` shuts the client down, so the same poison pill kills the instance after every restart. `LogAndContinueExceptionHandler` logs the error, **skips** the record and continues; since 4.2 you can additionally set `errors.deadletterqueue.topic.name` so the skipped record is forwarded to a DLQ.
- **Why the others are wrong:** A — the production handler covers errors while **writing** to Kafka (e.g. `RecordTooLargeException`), and the default one fails anyway. C — replacing the thread re-reads the same offset and fails again in an endless loop. D — that extractor handles invalid **timestamps**, not undecodable payloads.
- 🧠 **Key point / trap:** poison pill on input → `deserialization.exception.handler=LogAndContinueExceptionHandler`. The `default.`-prefixed config names are deprecated (KIP-1056).
- 📎 Source: `resources/streams-config.md` (Exception handlers); `resources/streams-upgrade-kip-1071-dlq.md` (KIP-1034, KIP-1056); `README.md` Buổi A §10 table.

### Question 20 — Answer: **C**

- **Why correct:** The failure is **deterministic** and affects records on every partition, so any instance that picks up the tasks will hit it too. `SHUTDOWN_APPLICATION` makes all instances with the same `application.id` shut down cooperatively (coordinated through the rebalance protocol), avoiding an endless crash-restart cycle and giving operators a clear signal.
- **Why the others are wrong:** A — `REPLACE_THREAD` is for transient errors; here the new thread re-processes the same records and throws again, while at-least-once may also cause duplicates on each retry. B — `SHUTDOWN_CLIENT` stops one instance, whose tasks migrate to the others, which then fail in turn — a slow cascading shutdown. D — Streams has no automatic DLQ for arbitrary user-code exceptions; you would need `processing.exception.handler` (3.9+) plus `errors.deadletterqueue.topic.name` (4.2+) to route such records.
- 🧠 **Key point / trap:** `StreamsUncaughtExceptionHandler` responses: `REPLACE_THREAD` (transient) · `SHUTDOWN_CLIENT` (this instance) · `SHUTDOWN_APPLICATION` (deterministic bug everywhere). The old `Thread.UncaughtExceptionHandler` overload was removed in 4.0.
- 📎 Source: `resources/streams-upgrade-kip-1071-dlq.md` (StreamsUncaughtExceptionHandler, KIP-1033); `README.md` Buổi A §10.

### Question 21 — Answer: **B**

- **Why correct:** In **Kafka Connect**, the DLQ (`errors.deadletterqueue.topic.name`, with `errors.tolerance=all`) exists only for **sink** connectors (source connectors have no Kafka record to dead-letter). In **Kafka Streams**, KIP-1034 (Kafka 4.2) added `errors.deadletterqueue.topic.name`: the built-in handlers (`DefaultProductionExceptionHandler`, `LogAndContinue*`) then forward failed records to that topic with headers such as `__streams.errors.exception`, `__streams.errors.stacktrace`, `__streams.errors.topic/partition/offset`. The application must create the DLQ topic itself.
- **Why the others are wrong:** A — Streams has had a DLQ since 4.2. C — neither system auto-creates a DLQ topic without configuration. D — the uncaught exception handler decides thread/instance fate and does not receive the failing record.
- 🧠 **Key point / trap:** Connect DLQ = sink only + `errors.tolerance=all`; Streams DLQ = 4.2+, handler-driven, same config key name.
- 📎 Source: `resources/streams-upgrade-kip-1071-dlq.md` (KIP-1034); Week 5 README (Connect error handling).

### Question 22 — Answer: **A**

- **Why correct:** `STREAM_TIME` punctuation is driven by **event time**: stream time advances from 1 s to 60 s as the records are processed, crossing six 10-second boundaries, so the punctuator fires **6 times** regardless of how fast the batch is processed (and never fires while no records arrive). `WALL_CLOCK_TIME` is driven by the **system clock**: 20 seconds of real time contain two 10-second intervals, so roughly **2 invocations**; if the batch were processed in 5 seconds it would not fire at all.
- **Why the others are wrong:** B swaps the two semantics. C — the type changes *when* the callback runs, not just the timestamp argument. D — stream-time punctuation is not per record; it fires when stream time crosses the schedule interval.
- 🧠 **Key point / trap:** `STREAM_TIME` = data-driven (idle → no punctuation); `WALL_CLOCK_TIME` = clock-driven. In `TopologyTestDriver`, wall-clock punctuation requires `advanceWallClockTime`.
- 📎 Source: `resources/streams-processor-api.md` (Punctuation: stream-time vs wall-clock-time); `README.md` Buổi A §13.

### Question 23 — Answer: **A, B**

- **Why correct:** A — Kafka Streams calls `ProcessorSupplier#get()` once per task and expects a **fresh** `Processor` each time; returning a shared singleton mixes state (fields, cached store handles) across tasks and threads. B — `recordMetadata()` returns an `Optional` that is present only while processing a record; inside a punctuator there is no current record, so it is empty.
- **Why the others are wrong:** C — state stores are managed by the library; `Processor#close()` must **not** close them (only cancel punctuators and release the processor's own resources). D — `context.commit()` merely **requests** a commit at the next opportunity; it is not synchronous. E — the old `org.apache.kafka.streams.processor.Processor` API was removed in 4.0; only `org.apache.kafka.streams.processor.api.Processor` remains.
- 🧠 **Key point / trap:** new processor instance per `get()`; never close stores in `close()`; `commit()` is a hint.
- 📎 Source: `resources/streams-processor-api.md` (Processor interface, ProcessorContext, "must return a new instance"); `resources/streams-upgrade-kip-1071-dlq.md` (API removals).

### Question 24 — Answer: **B**

- **Why correct:** Each instance owns only the partitions (and therefore keys) of its assigned tasks, so a local `store().get(key)` for a key owned by another instance returns `null`. Kafka Streams provides discovery, not RPC: configure `application.server=host:port` on every instance, call `queryMetadataForKey(storeName, key, keySerializer)` to obtain `KeyQueryMetadata` with `activeHost()` (and `standbyHosts()`), and forward the request to that host over your own REST/gRPC layer.
- **Why the others are wrong:** A — standby replicas improve failover; they do not make every instance hold every key (and would need n−1 standbys plus querying standbys explicitly). C — a `GlobalKTable` is not an aggregation result; you cannot turn a `count()` into one. D — `__consumer_offsets` holds offsets, not store locations, and brokers do not serve state stores.
- 🧠 **Key point / trap:** Interactive Queries across instances = `application.server` + `queryMetadataForKey` + your own RPC. Queries are only valid when the instance is `RUNNING`.
- 📎 Source: `resources/streams-config.md` (`application.server`); `resources/streams-core-concepts-architecture.md` (Interactive queries); `README.md` Buổi A §12.

### Question 25 — Answer: **B, C**

- **Why correct:** B — `TopologyTestDriver` processes each piped record **synchronously** through the topology, so output is available immediately; event time is controlled by explicit record timestamps or `TestInputTopic#advanceTime`, which is how you close windows and trigger `suppress` in tests. C — the driver has no real clock: `WALL_CLOCK_TIME` punctuators fire only when the test calls `testDriver.advanceWallClockTime(Duration)` (stream-time punctuators fire automatically as record timestamps advance).
- **Why the others are wrong:** A — no broker is used; `bootstrap.servers` is required by `StreamsConfig` validation but can be a dummy value such as `dummy:1234`. D — the driver runs a single topology instance; rebalancing, multiple instances and network behavior need integration tests (Testcontainers/EmbeddedKafka, Week 7). E — stores are accessible via `getKeyValueStore`, `getWindowStore`, `getSessionStore` for seeding and assertions.
- 🧠 **Key point / trap:** `TopologyTestDriver` = fast, synchronous, broker-less unit test of a topology; remember `advanceWallClockTime` and `close()` (try-with-resources).
- 📎 Source: `resources/streams-testing-topologytestdriver.md` (Overview, Time control, State store access); `README.md` Buổi A §15.

### Question 26 — Answer: **A, C**

- **Why correct:** A — KIP-1071 introduces a dedicated **streams group** type: with `group.protocol=streams` the application sends its topology to the broker and the **group coordinator** computes active/standby/warmup task assignments and hands them out incrementally through `StreamsGroupHeartbeat`, following the broker-driven design of KIP-848 for consumers. C — streams groups are managed with `kafka-streams-groups.sh` (list/describe/delete/reset offsets); `kafka-consumer-groups.sh` does not show them, and there is no online migration — all instances must be stopped before switching `group.protocol`.
- **Why the others are wrong:** B — that is the **classic** mechanism (client-side `StreamsPartitionAssignor` embedded in the consumer protocol), which the new protocol replaces; it is not user-configurable either. D — the protocol was Early Access in 4.1 and **GA in 4.2**. E — standby tasks are supported; the broker even has `group.streams.num.standby.replicas`.
- 🧠 **Key point / trap:** KIP-1071 = Streams Rebalance Protocol, GA 4.2, `group.protocol=streams`, `kafka-streams-groups.sh`, broker-side assignment (like KIP-848 from Week 4).
- 📎 Source: `resources/streams-upgrade-kip-1071-dlq.md` (KIP-1071); `resources/streams-config.md` (`group.protocol`); Week 4 README (KIP-848).

### Question 27 — Answer: **B**

- **Why correct:** In ksqlDB a query **without** `EMIT CHANGES` against a table is a **pull query**: it reads the current value from the materialized view (a Kafka Streams state store under the hood) and returns a finite result, then terminates — the SQL equivalent of an Interactive Query. A query **with** `EMIT CHANGES` is a **push query** that streams every update to the client until it disconnects. `CREATE TABLE ... AS SELECT` (CTAS) is a **persistent query**: ksqlDB compiles it into a Kafka Streams topology that runs continuously and writes its results to a new topic, restarting automatically because it is stored in the command topic.
- **Why the others are wrong:** A — statement 1 has no `EMIT CHANGES`, so it is not a push query. C — pull queries on tables are exactly what materialized views are for. D — `EMIT CHANGES` works on both streams and tables.
- 🧠 **Key point / trap:** push = `EMIT CHANGES` (continuous); pull = no `EMIT CHANGES`, table lookup, returns once. CSAS/CTAS = persistent query. ksqlDB REST port 8088.
- 📎 Source: `resources/ksqldb-concepts.md` (Query types, Materialized views); `README.md` Buổi A §16.

### Question 28 — Answer: **B**

- **Why correct:** `KafkaStreams` moves `CREATED → REBALANCING → RUNNING`. While an instance is `REBALANCING` (joining the group, receiving tasks, restoring stores from changelogs) its stores are not yet queryable, and `store()` throws `InvalidStateStoreException` with exactly this message. The proper pattern is to gate Interactive Queries on `streams.state() == RUNNING` (or use a `StateListener` for readiness) and retry.
- **Why the others are wrong:** A — compaction of the changelog does not delete a store; `delete.retention.ms` governs tombstones. C — changing `application.id` creates a brand-new application with empty state and re-reads inputs from the beginning — never done for routine deploys. D — Interactive Queries are independent of the processing guarantee.
- 🧠 **Key point / trap:** `InvalidStateStoreException` right after start = `REBALANCING`, retry when `RUNNING`. Terminal states: `ERROR` (via `PENDING_ERROR`) and `NOT_RUNNING` (via `PENDING_SHUTDOWN`).
- 📎 Source: `README.md` Buổi A §11–12; `resources/streams-core-concepts-architecture.md` (Interactive queries, Local state consistency).
