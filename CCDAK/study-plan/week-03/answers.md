# ✅ Answers & Explanations — Week 3: Producer Deep Dive + Transactions

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)
> All defaults quoted are **Apache Kafka 4.3 Java client** defaults (see `resources/producer-configs.md`). Where the old exam pool quotes a different number, it is called out.

**Answer key:** 1-B · 2-C · 3-C · 4-AC · 5-B · 6-B · 7-AC · 8-C · 9-B · 10-B · 11-A · 12-B · 13-B · 14-B · 15-A · 16-ABD · 17-BD · 18-B · 19-B · 20-BC · 21-AC · 22-C · 23-A · 24-AC · 25-B · 26-B · 27-BD · 28-B · 29-B

---

### Question 1 — Answer: **B**

- **Why correct:** `acks=all` only waits for the replicas that are **currently in the ISR**. With `min.insync.replicas` left at its broker default of **1**, the ISR can shrink to the leader alone (2 of 3 brokers down) and the leader still acknowledges the write. If that lone leader then fails before the followers catch up, the acknowledged records are gone. Setting `min.insync.replicas=2` on the topic (or broker) makes the leader reject writes with `NotEnoughReplicasException` (retriable) while the ISR is below 2, so the producer retries instead of silently accepting an unsafe write. This is the standard **RF=3 + `min.insync.replicas=2` + `acks=all`** durability formula.
- **Why the others are wrong:** A — `retries` already defaults to `Integer.MAX_VALUE` (2147483647); the writes did not fail, they were *accepted* by a lone leader, so retrying changes nothing. C — `max.in.flight.requests.per.connection=1` affects ordering, not durability. D — `acks=1` waits only for the leader and makes the loss window *larger*.
- 🧠 **Key point / trap:** "`acks=all` but data was still lost" → the missing piece is **`min.insync.replicas` on the topic/broker**, never a producer setting. `acks` is producer-side; `min.insync.replicas` is broker/topic-side.
- 📎 Source: `resources/producer-configs.md` (`acks` description: "all in-sync replicas"), `resources/confluent-producer-guide.md` (durability / ISR commit), Week 3 `README.md` (Buổi A §2 table).

### Question 2 — Answer: **C**

- **Why correct:** The Java client validates `delivery.timeout.ms ≥ linger.ms + request.timeout.ms` at construction time when `delivery.timeout.ms` is explicitly set. Here 20000 < 5000 + 30000 = 35000, so `new KafkaProducer(...)` throws `ConfigException` and the application never starts. The defaults satisfy the rule (120000 ≥ 5 + 30000).
- **Why the others are wrong:** A — the producer does not start at all, so no retrying happens. B and D — Kafka never silently rewrites `linger.ms` or caps `request.timeout.ms`; it fails fast. (Only when `delivery.timeout.ms` is left at its *default* and the sum exceeds 120000 does the client bump `delivery.timeout.ms` up to the sum and log a warning; an explicitly set, too-small value is a hard error.)
- 🧠 **Key point / trap:** Memorise the inequality **`delivery.timeout.ms` (120000) ≥ `linger.ms` (5) + `request.timeout.ms` (30000)**. A question that lists three timeouts is usually testing this rule.
- 📎 Source: `resources/producer-configs.md` (`delivery.timeout.ms`, `request.timeout.ms`, `linger.ms`), Week 3 `README.md` (Buổi A §3, Lab 3.6 in `labs.md`).

### Question 3 — Answer: **C**

- **Why correct:** `delivery.timeout.ms` is "an upper bound on the time to report success or failure after a call to `send()` returns": it covers the time in the accumulator (batching/linger), the in-flight request, and **all retries**. Setting it to 45000 caps the whole lifecycle at 45 s. Because `retries` defaults to 2147483647, the retry *count* never binds in practice; the *time* does.
- **Why the others are wrong:** A — `retries=45` is a count, not a duration; 45 retries with exponential backoff (`retry.backoff.ms` 100 → `retry.backoff.max.ms` 1000) plus 30 s request timeouts could take far longer than 45 s. B — `request.timeout.ms` bounds a **single** request/response; the producer can still retry many times. D — `max.block.ms` (60000) bounds how long `send()` itself blocks waiting for metadata or buffer space, not the delivery lifecycle.
- 🧠 **Key point / trap:** "how long the producer keeps trying" → **`delivery.timeout.ms`**, not `retries`, not `request.timeout.ms`.
- 📎 Source: `resources/producer-configs.md` (`delivery.timeout.ms`, `retries`, `max.block.ms`), `resources/kafkaproducer-javadoc.md` (retries default and recommendation to use `delivery.timeout.ms`).

### Question 4 — Answer: **A, C**

- **Why correct:** When `enable.idempotence=true` is set explicitly, the client enforces three constraints and throws `ConfigException` if any conflicts: `acks` must be `all` (A: `acks=1` fails with "Must set acks to all in order to use the idempotent producer"), `max.in.flight.requests.per.connection` must be **≤ 5** (C: 8 fails), and `retries` must be **> 0**.
- **Why the others are wrong:** B — 5 is exactly the maximum allowed and is the default. D — the compression codec is irrelevant to idempotence. E — 2147483647 is the default `retries` and satisfies `retries > 0`.
- 🧠 **Key point / trap:** Idempotence trio: **`acks=all` · `retries>0` · `max.in.flight ≤ 5`**. Note the subtle 4.x behaviour: if idempotence is only *implicitly* on (default) and you set a conflicting value, the client silently disables idempotence with a warning; if you set `enable.idempotence=true` *explicitly*, it is a hard `ConfigException`.
- 📎 Source: `resources/producer-configs.md` (`enable.idempotence`, `max.in.flight.requests.per.connection`, `retries` descriptions), `resources/confluent-producer-configs.md`.

### Question 5 — Answer: **B**

- **Why correct:** Since Kafka 3.0 the defaults are `enable.idempotence=true`, `acks=all`, `retries=Integer.MAX_VALUE`, `max.in.flight.requests.per.connection=5`. The broker tracks the producer ID and the sequence numbers of the last **5** batches per partition, so when a retried batch arrives after later batches it is placed in the correct order and duplicate sequences are discarded. Result: exactly one copy, in order, with no application changes.
- **Why the others are wrong:** A — this was true before idempotence existed; with idempotence on, `max.in.flight=5` still preserves order. C — `OutOfOrderSequenceException` is raised only when the broker sees a *gap* it cannot reconcile, not on a normal retry. D — idempotence *requires* `acks=all`, not `acks=1`.
- 🧠 **Key point / trap:** Old-exam trap. "Preserve order under retries → `max.in.flight=1`" is only the right answer when the question explicitly says `enable.idempotence=false`.
- 📎 Source: `resources/message-delivery-semantics.md` (producer ID + sequence number), `resources/kip-98-exactly-once-transactions.md` (idempotent producer design), Week 3 `README.md` (Buổi A §4).

### Question 6 — Answer: **B**

- **Why correct:** The broker expected sequence N for this producer ID/partition but received something else it cannot reconcile. This means a batch was lost or the broker's state diverged (for example the log was truncated or the producer state expired), so the client marks the producer as being in a **fatal** state. The Javadoc groups `OutOfOrderSequenceException` with `ProducerFencedException` and `AuthorizationException` as errors where the only correct action is `producer.close()` and start a fresh instance (a fresh producer ID).
- **Why the others are wrong:** A — it is not retriable; the producer will not fix it by itself. C — size violations surface as `RecordTooLargeException`. D — consumer offset commits have nothing to do with producer sequence numbers.
- 🧠 **Key point / trap:** Fatal idempotent/transactional trio: **`OutOfOrderSequenceException`, `ProducerFencedException`, `InvalidProducerEpochException`** → close and recreate the producer.
- 📎 Source: `resources/kafkaproducer-javadoc.md` (exception handling block in the transactional example), Week 3 `README.md` (Buổi A §3 retriable vs fatal table).

### Question 7 — Answer: **A, C**

- **Why correct:** A batch is sent when it reaches `batch.size` **or** `linger.ms` expires, whichever comes first. `batch-size-avg` ≈ record size means every batch holds one record: the accumulator flushes before more records arrive. Raising `linger.ms` from the default **5** to 50 lets more records accumulate (A). Raising `batch.size` from **16384** bytes gives room for bigger batches, and `compression.type=lz4` shrinks each batch on the wire so fewer bytes and fewer requests are needed (C). Both trade a few ms of latency for throughput, exactly what the question allows.
- **Why the others are wrong:** B — `acks=0` reduces waiting for acknowledgements but does not change the number of requests or batch size, and it sacrifices durability and disables idempotence. D — `max.in.flight=1` *reduces* throughput. E — a smaller `buffer.memory` (default 33554432 bytes) only makes `send()` block sooner.
- 🧠 **Key point / trap:** "increase throughput / fewer requests / accept latency" → **↑`linger.ms`, ↑`batch.size`, enable compression**. Remember `linger.ms` default is now 5 (Kafka 4.0, KIP-1030); older dumps say 0.
- 📎 Source: `resources/producer-configs.md` (`linger.ms`, `batch.size`, `compression.type`), `resources/confluent-producer-guide.md` (perf-test table: `linger.ms` 0→100 moves `batch-size-avg` 1215→16165), `resources/kip-1030-defaults-kafka-4-0.md`.

### Question 8 — Answer: **C**

- **Why correct:** `batch.size` is the size the accumulator *tries* to fill per partition; the docs say "no attempt will be made to batch records larger than this size", meaning an oversized record simply gets a batch of its own. The hard client-side limit for a single record/request is `max.request.size` (default **1048576** bytes); 40 KB is far below it, so the record is sent immediately (`linger.ms=0`) in a one-record batch.
- **Why the others are wrong:** A — `RecordTooLargeException` is thrown only for exceeding `max.request.size` (client) or `message.max.bytes` (broker, 1048588). B — Kafka never splits a record. D — `batch.size` is an upper bound, not a minimum to wait for; with `linger.ms=0` nothing waits anyway.
- 🧠 **Key point / trap:** `batch.size` = **ceiling**, `linger.ms` = **max wait**, `max.request.size` = **hard record/request limit**. A question saying "record larger than batch.size" is testing that the record still goes through.
- 📎 Source: `resources/producer-configs.md` (`batch.size`: "No attempt will be made to batch records larger than this size"; `max.request.size`).

### Question 9 — Answer: **B**

- **Why correct:** All unsent records live in a pool of `buffer.memory` = **33554432** bytes (32 MB). When the application produces faster than the sender thread can drain, the pool runs out and `send()` blocks for up to `max.block.ms` = **60000** ms, then fails with `BufferExhaustedException` (a subclass of `TimeoutException`, message "Failed to allocate ... bytes within the configured max blocking time 60000 ms"). Blocking for exactly 60 s is the signature.
- **Why the others are wrong:** A — a missing topic also blocks for `max.block.ms` waiting for metadata, but the error message would mention metadata/topic, not the buffer, and `metadata.max.age.ms` (300000) is a refresh interval, not a blocking bound. C — `delivery.timeout.ms` (120000) expiry is reported asynchronously through the callback, not by a blocking `send()`, and it is not controlled by `retries`. D — `session.timeout.ms` is a consumer setting.
- 🧠 **Key point / trap:** `send()` blocks only for two reasons: **no metadata yet** or **buffer full**; both are bounded by `max.block.ms`. Fixes: raise `buffer.memory`, batch/compress better, add partitions/brokers, or slow the producer.
- 📎 Source: `resources/producer-configs.md` (`buffer.memory`: "block for max.block.ms after which it will fail with an exception"; `max.block.ms` lists the blocking methods), `resources/kafkaproducer-javadoc.md`.

### Question 10 — Answer: **B**

- **Why correct:** The docs state "Compression is of full batches of data, so the efficacy of batching will also impact the compression ratio." With `linger.ms=0` batches are tiny and compress poorly; raising `linger.ms`/`batch.size` produces larger batches and better ratios. Among codecs, `zstd` (KIP-110, Kafka 2.1+) gives a ratio close to gzip at much lower CPU than gzip, which is the "best ratio with moderate CPU" sweet spot. Its level is tunable via `compression.zstd.level` (default 3).
- **Why the others are wrong:** A — compression is per batch, not per record, and snappy has a mediocre ratio. C — with the topic default `compression.type=producer` the broker stores the batch exactly as received; it does not recompress. D — lz4 is the *fastest* codec, not the highest ratio.
- 🧠 **Key point / trap:** codec cheat-sheet: **gzip** = highest ratio/most CPU, **zstd** = near-gzip ratio at moderate CPU, **lz4** = fastest, **snappy** = balanced. Compression ratio improves with **batch size**.
- 📎 Source: `resources/producer-configs.md` (`compression.type`, `compression.gzip.level` -1, `compression.lz4.level` 9, `compression.zstd.level` 3), `resources/confluent-producer-guide.md` (batching & compression).

### Question 11 — Answer: **A**

- **Why correct:** The topic-level `compression.type` defaults to `producer`, meaning the broker keeps whatever codec the producer used and appends the batch as-is. When the topic is pinned to a *different* codec (`gzip`), every incoming lz4 batch must be decompressed and recompressed with gzip on the broker, which is CPU-expensive (gzip is the most CPU-hungry codec). Setting the topic back to `compression.type=producer` removes the recompression step.
- **Why the others are wrong:** B — lz4 has been supported since Kafka 0.8.2. C — consumers decompress on their own side; `fetch.min.bytes` is unrelated. D — log compaction (`cleanup.policy=compact`) is a background process unrelated to compression codecs, and the symptom is tied to the codec mismatch.
- 🧠 **Key point / trap:** Topic `compression.type` values are the five codecs **plus `producer`** (default). Any value other than `producer` that differs from the producer's codec forces broker-side recompression.
- 📎 Source: Week 3 `README.md` (Buổi A §6 compression, "Broker giữ nguyên batch nén"), `resources/producer-configs.md` (`compression.type`).

### Question 12 — Answer: **B**

- **Why correct:** The built-in partitioner maps a keyed record to `murmur2(keyBytes) mod numPartitions`. Changing the divisor from 6 to 12 changes the result for most keys, so new records for `customerId=42` land in a different partition from the historical ones. Consumers can no longer rely on a single partition holding all events for a key, and any per-key ordering across old and new data is broken. Kafka does not migrate or re-hash existing data.
- **Why the others are wrong:** A — the partitioner is stateless; it never "remembers" assignments. C — `null`-keyed records use the sticky partitioner and have no ordering guarantee anyway; keyed records are the ones affected. D — Kafka allows increasing partitions on any topic (decreasing is not allowed); it does not know or care whether records are keyed.
- 🧠 **Key point / trap:** "add partitions to a keyed topic" → **key-to-partition mapping changes**. Plan partition count up front; if you must grow, create a new topic and migrate.
- 📎 Source: `resources/confluent-producer-guide.md` (murmur2 hashing of keys), `resources/kip-480-794-sticky-partitioner.md` (keyed vs unkeyed partitioning), Week 3 `README.md` (Buổi A §7, Lab 3.3).

### Question 13 — Answer: **B**

- **Why correct:** Since Kafka 2.4 (KIP-480) unkeyed records use the **sticky partitioner**: it picks one partition and sends all `null`-key records there until the batch is complete (full `batch.size` or `linger.ms` elapsed), then randomly switches. KIP-794 (Kafka 3.3) refined it to switch after `batch.size` **bytes** and added adaptive partitioning, so distribution is uniform over time while each batch is larger. Confluent's benchmark showed p99 latency roughly halved versus round-robin at 16 partitions.
- **Why the others are wrong:** A — this is designed behaviour, not a bug; `RoundRobinPartitioner` would recreate the small-batch problem. C — Kafka never derives an implicit key from timestamps. D — `partitioner.ignore.keys` (default `false`) only matters when records *have* keys; it does not force a single partition.
- 🧠 **Key point / trap:** "null key → many records in the same partition for a few ms, then it changes" = **sticky partitioner working correctly**. Over seconds the distribution is even.
- 📎 Source: `resources/kip-480-794-sticky-partitioner.md` (mechanism and Confluent benchmark), `resources/producer-configs.md` (`partitioner.class` null, `partitioner.adaptive.partitioning.enable` true).

### Question 14 — Answer: **B**

- **Why correct:** `partitioner.ignore.keys=true` tells the built-in partitioner to skip the key hash and treat every record like an unkeyed one (sticky/uniform distribution). Records for the same `deviceId` therefore scatter across partitions, so per-key ordering is lost and any downstream that assumes "one key lives in one partition" (compacted-topic readers, per-key state in Streams) breaks. The key is still stored in the record; only its use for *partition selection* is ignored.
- **Why the others are wrong:** A — the key *is* ignored for partitioning; compaction still uses it, which is exactly why compaction consumers get confused. C — idempotence is independent of partitioning. D — compression operates on the batch regardless of keys.
- 🧠 **Key point / trap:** Anything that spreads keyed records for "even distribution" (`partitioner.ignore.keys=true`, `RoundRobinPartitioner`) **trades away per-key ordering**.
- 📎 Source: `resources/producer-configs.md` (`partitioner.ignore.keys`: "producer won't use record keys to choose a partition"), `resources/kip-480-794-sticky-partitioner.md` (KIP-794 new configs).

### Question 15 — Answer: **A**

- **Why correct:** Custom routing is exactly what the `org.apache.kafka.clients.producer.Partitioner` interface is for: implement `partition(topic, key, keyBytes, value, valueBytes, cluster)` (return 0 when the key starts with `vip-`, otherwise `Utils.toPositive(Utils.murmur2(keyBytes)) % numPartitions` to keep default behaviour), plus `configure()` and `close()`, and register the class via `partitioner.class`.
- **Why the others are wrong:** B — `onAcknowledgement` runs *after* the broker responds; the partition is already chosen. `onSend` could in theory set `record.partition`, but interceptors are meant for cross-cutting metadata, not routing logic, and it would bypass the partitioner. C — Kafka fully supports custom partitioning. D — `RoundRobinPartitioner` ignores keys entirely and cannot pin a prefix to partition 0.
- 🧠 **Key point / trap:** "route by key content / VIP partition / hot-key isolation" → **custom `Partitioner` + `partitioner.class`**.
- 📎 Source: `resources/producer-configs.md` (`partitioner.class` description listing custom `Partitioner` implementations), Week 3 `README.md` (Buổi A §7 custom partitioner; Lab 3.3 `createPartitioner` in `kafkajs`).

### Question 16 — Answer: **A, B, D**

- **Why correct:** A record passes through four size gates. Client: `max.request.size` (default 1048576) — already raised. Broker: `message.max.bytes` (default 1048588) or the topic override `max.message.bytes` (A) — the quoted message "larger than the max message size the server will accept" is precisely this broker-side rejection. Replication: followers fetch with `replica.fetch.max.bytes` (default 1048576); if it is smaller than the record, followers cannot replicate it and the ISR shrinks (B). Consumption: `max.partition.fetch.bytes` (default 1048576) and `fetch.max.bytes` (52428800) must allow the record, otherwise the consumer stalls on that partition (D). (Since KIP-74 a consumer will still make progress on an oversized *first* record, but the limits should still be aligned.)
- **Why the others are wrong:** C — `batch.size` (16384) is only a batching target; oversized records get their own batch. E — `linger.ms` controls wait time, not size.
- 🧠 **Key point / trap:** Large-record checklist: **`max.request.size` → `message.max.bytes`/`max.message.bytes` → `replica.fetch.max.bytes` → `max.partition.fetch.bytes`**. Or avoid it with the **claim-check** pattern (store payload in object storage, send a pointer).
- 📎 Source: `resources/producer-configs.md` (`max.request.size`), Week 3 `README.md` (Buổi A §8 and Buổi C decision table "Record > 1 MB"), `labs.md` Lab 3.6.

### Question 17 — Answer: **B, D**

- **Why correct:** Both are subclasses of `RetriableException`. `NotLeaderOrFollowerException` (B) means the producer sent to a broker that is no longer the leader; the client refreshes metadata and retries. `NotEnoughReplicasException` (D) means the ISR is currently below `min.insync.replicas`; the condition is transient, so the client retries until `delivery.timeout.ms` (120000 ms) expires.
- **Why the others are wrong:** A — `RecordTooLargeException` is deterministic: the same record will always be too large, so it fails immediately. C — `SerializationException` is thrown synchronously in `send()` before the record ever reaches the accumulator. E — `TopicAuthorizationException` is an ACL problem that needs an operator; retrying cannot fix it.
- 🧠 **Key point / trap:** Retriable = "the cluster state may change" (leader election, ISR, network, timeout). Fatal = "the request itself is wrong" (size, serialization, auth, invalid topic).
- 📎 Source: Week 3 `README.md` (Buổi A §3 retriable vs fatal table), `resources/producer-configs.md` (`retries`: "fails with a potentially transient error").

### Question 18 — Answer: **B**

- **Why correct:** Serialization happens on the calling thread inside `send()`, before partitioning and before the record enters the `RecordAccumulator`. A type mismatch makes `LongSerializer.serialize()` throw `ClassCastException`, which `KafkaProducer` wraps in `SerializationException` and rethrows to the caller. No `Future` is returned, no callback is invoked, and nothing is retried.
- **Why the others are wrong:** A — the exception never reaches the callback and is not retriable. C — the broker never sees the record; it only receives bytes. D — the consumer is never involved because nothing was produced.
- 🧠 **Key point / trap:** Two error paths: **synchronous** (`SerializationException`, `TimeoutException` from `max.block.ms`, `IllegalStateException`) thrown by `send()` itself vs **asynchronous** (`RecordTooLargeException`, `TimeoutException` from `delivery.timeout.ms`, `NotEnoughReplicasException`) delivered through the callback/Future.
- 📎 Source: `resources/kafkaproducer-javadoc.md` (send flow), Week 3 `README.md` (Buổi A §1 send path, §3 table "ném đồng bộ tại send()").

### Question 19 — Answer: **B**

- **Why correct:** The message "Expiring N record(s) for topic-partition: X ms has passed since batch creation" is emitted when a batch has lived in the producer longer than `delivery.timeout.ms` (default **120000** ms; 120027 ms confirms it). It means every attempt inside that window failed or never got a response, which typically points at the partition leader being unavailable, the ISR being below `min.insync.replicas` (repeated `NotEnoughReplicasException`), or network saturation. The first action is to inspect broker/ISR health; only then consider raising `delivery.timeout.ms`.
- **Why the others are wrong:** A — `request.timeout.ms` (30000) governs one request; its expiry is retried silently and does not produce this message. C — `linger.ms` (5 ms) adds only milliseconds; it cannot cause a 120 s expiry. D — `max.poll.interval.ms` is a consumer setting.
- 🧠 **Key point / trap:** "since batch creation" → **`delivery.timeout.ms`**. Do not reflexively answer "increase `request.timeout.ms`".
- 📎 Source: `resources/producer-configs.md` (`delivery.timeout.ms`), Week 3 `README.md` (Bẫy đề "Expiring N record(s)"), `labs.md` Lab 3.6.

### Question 20 — Answer: **B, C**

- **Why correct:** The Javadoc opens with "The producer is thread safe and sharing a single producer instance across threads will generally be faster than having multiple instances", because one instance shares the accumulator (bigger batches), connections, and metadata (B). Callbacks execute on the producer's single background I/O (`Sender`) thread, so a slow callback stalls all sending; callbacks for records sent to the same partition are invoked in order (C).
- **Why the others are wrong:** A — the opposite of the documented thread-safety guarantee (it is `KafkaConsumer` that is not thread-safe). D — callbacks do *not* run on the caller thread; blocking DB calls inside them freeze the I/O thread. E — `send()` is asynchronous; it returns a `Future` immediately unless it must block for metadata or buffer space (bounded by `max.block.ms`).
- 🧠 **Key point / trap:** **Producer = thread-safe, share it. Consumer = not thread-safe, one per thread.** Callbacks run on the I/O thread: keep them non-blocking.
- 📎 Source: `resources/kafkaproducer-javadoc.md` (thread-safety statement, asynchronous send, callback ordering), `resources/confluent-producer-guide.md`.

### Question 21 — Answer: **A, C**

- **Why correct:** Zombie fencing works by bumping the **producer epoch** for a given `transactional.id` on every `initTransactions()`; requests carrying an older epoch are rejected with `ProducerFencedException`. If each start uses a brand-new UUID, the new instance gets a new id and epoch 0 while the stalled old instance keeps its own id and epoch, so nothing fences it and both can commit output for the same input partitions (A). Likewise, `initTransactions()` "ensures any transactions initiated by previous instances of the producer with the same `transactional.id` are completed" (committed or aborted) before continuing; with a new id there is no previous instance to clean up, so an in-flight transaction from the crashed run simply lingers until the coordinator times it out after `transaction.timeout.ms` (60000 ms) (C).
- **Why the others are wrong:** B — transactions always span multiple partitions/topics regardless of id. D — a transactional producer *requires* `acks=all` (idempotence is implied). E — `__transaction_state` has **50** partitions (`transaction.state.log.num.partitions`) irrespective of client ids.
- 🧠 **Key point / trap:** `transactional.id` must be **unique per logical producer and stable across restarts**, typically derived from the input partition or shard (this is what Kafka Streams does). Random UUID = no fencing.
- 📎 Source: `resources/kip-98-exactly-once-transactions.md` (zombie fencing, epoch, choosing `transactional.id`), `resources/kafkaproducer-javadoc.md` (`initTransactions` semantics).

### Question 22 — Answer: **C**

- **Why correct:** `ProducerFencedException` means the transaction coordinator has seen a newer `initTransactions()` for the same `transactional.id` and bumped the epoch; this instance is now a zombie. The Javadoc pattern is explicit: catch `ProducerFencedException | OutOfOrderSequenceException | AuthorizationException` → `producer.close()`; only other `KafkaException`s are handled with `abortTransaction()` and retry.
- **Why the others are wrong:** A — `abortTransaction()` on a fenced producer throws again (the coordinator rejects every request from the old epoch). B — `transaction.timeout.ms` controls coordinator-initiated aborts of *long-open* transactions, not fencing. D — `initTransactions()` may be called only once per producer instance; calling it again throws `IllegalStateException`.
- 🧠 **Key point / trap:** **Fenced = fatal = `close()`**. The application should let the newer instance own that `transactional.id`.
- 📎 Source: `resources/kafkaproducer-javadoc.md` (transactional example's catch blocks), `resources/kip-98-exactly-once-transactions.md`.

### Question 23 — Answer: **A**

- **Why correct:** A `read_committed` consumer only fetches up to the **last stable offset (LSO)**, the offset of the first record of the earliest transaction that is still open on that partition. Everything after the LSO, including committed data from *other* producers, stays invisible until that transaction is committed or aborted. A hung producer therefore freezes the LSO; the coordinator will abort the transaction after `transaction.timeout.ms` (default **60000** ms, bounded by broker `transaction.max.timeout.ms` 900000 ms), at which point the LSO advances and the "lag" disappears. Measured lag grows because the high watermark keeps moving while the consumer's position cannot.
- **Why the others are wrong:** B — `read_committed` is not deprecated; it is the required level for EOS pipelines. C — compaction does not block reads. D — `max.poll.records` (500) affects per-poll batch size, not visibility.
- 🧠 **Key point / trap:** "`read_committed` lag rises but nothing is slow" → **LSO pinned by an open transaction**. Check `transaction.timeout.ms` and stuck producers, not the consumer.
- 📎 Source: `resources/kip-98-exactly-once-transactions.md` (LSO, `read_committed`, coordinator abort), `resources/message-delivery-semantics.md` ("Using Transactions": read-committed vs read-uncommitted).

### Question 24 — Answer: **A, C**

- **Why correct:** Exactly-once consume-transform-produce requires the input offsets to be written to `__consumer_offsets` **as part of the same transaction** as the output records. That is what `sendOffsetsToTransaction(offsets, consumer.groupMetadata())` does; it must be called before `commitTransaction()` (A). Any *other* offset commit path would break atomicity, so the consumer must have `enable.auto.commit=false` and must not call `commitSync()`/`commitAsync()` for those offsets (C). The design doc for "Using Transactions" lists `isolation.level=read_committed` and `enable.auto.commit=false` as the consumer requirements.
- **Why the others are wrong:** B — auto-commit every `auto.commit.interval.ms` (5000 ms) commits offsets outside the transaction, which can commit input that was never atomically produced. D — a transactional producer implies idempotence, which requires `acks=all`; `acks=1` would fail configuration. E — a `commitSync()` after `commitTransaction()` is redundant at best and, if the transaction later aborts on retry, creates a window where offsets are committed but output is not.
- 🧠 **Key point / trap:** EOS triad on the consumer side: **`enable.auto.commit=false` + offsets via `sendOffsetsToTransaction` + `isolation.level=read_committed`**. Passing `consumer.groupMetadata()` (not just the group id) also lets the coordinator fence stale consumer generations.
- 📎 Source: `resources/message-delivery-semantics.md` ("Using Transactions" requirements), `resources/kip-98-exactly-once-transactions.md` (Confluent blog API pattern), `labs.md` Lab 3.5.

### Question 25 — Answer: **B**

- **Why correct:** During `initTransactions()` the producer sends its `transaction.timeout.ms` to the coordinator in `InitProducerId`. The broker rejects any value larger than `transaction.max.timeout.ms`, whose default is **900000** ms (15 minutes), with `InvalidTxnTimeoutException`. 1200000 ms (20 minutes) exceeds it, so `initTransactions()` fails. The fix is to raise the broker setting or shorten the transaction.
- **Why the others are wrong:** A — the coordinator enforces the broker maximum precisely to stop a client from holding partitions' LSO indefinitely. C — the producer's own value would be honoured if it were ≤ 15 minutes; the coordinator never silently substitutes 60000. D — this is a validation error returned immediately, not a `max.block.ms` (60000) timeout.
- 🧠 **Key point / trap:** Transaction timeout pair: producer **`transaction.timeout.ms` 60000** ≤ broker **`transaction.max.timeout.ms` 900000**. Violation = `InvalidTxnTimeoutException` at `initTransactions()`.
- 📎 Source: `resources/producer-configs.md` (`transaction.timeout.ms`), `resources/kip-98-exactly-once-transactions.md` (`transaction.max.timeout.ms` broker config), Week 3 `README.md` (PHẢI NHỚ table).

### Question 26 — Answer: **B**

- **Why correct:** A Kafka transaction makes atomic exactly two kinds of writes: records to Kafka topic partitions and offset commits to `__consumer_offsets`. Anything written to PostgreSQL happens outside the coordinator's two-phase commit, so a crash between the DB write and `commitTransaction()` (or the reverse) yields duplicates or gaps. The design doc's closing note says as much: for external systems, "store its offset in the same place as its output", or make the sink idempotent (upsert keyed by business key or topic-partition-offset), or use an outbox/`Kafka Connect` sink that manages offsets.
- **Why the others are wrong:** A — Kafka has no hooks into external databases. C — `acks=0` is incompatible with idempotence/transactions and offers the *weakest* guarantee. D — PostgreSQL's READ COMMITTED isolation is unrelated to Kafka's `isolation.level`.
- 🧠 **Key point / trap:** **EOS in Kafka is Kafka → Kafka.** The moment a non-Kafka sink appears, the answer is idempotent sink / offsets-in-DB / outbox / Connect, never "Kafka transactions cover it".
- 📎 Source: `resources/message-delivery-semantics.md` (external systems paragraph), Week 3 `README.md` (Buổi A §9 "Giới hạn", Cổng tự kiểm tra Q8).

### Question 27 — Answer: **B, D**

- **Why correct:** The idempotent producer de-duplicates only what *it* retries internally, identified by producer ID + sequence number, within one producer session and per partition. A second `send()` issued by application code is a brand-new record with a new sequence number, so it is written twice (B). Writes to two different topics are two independent partitions with no atomicity between them; if the process dies after topic A is acknowledged, topic B never receives its record and nothing rolls back topic A. Only a **transaction** (`transactional.id`, `commitTransaction`) makes multi-partition writes all-or-nothing (D).
- **Why the others are wrong:** A, E — a lost acknowledgement followed by a client retry is exactly the duplicate that sequence numbers catch. C — ordering of up to 5 in-flight batches on the same partition is preserved by the broker's sequence tracking.
- 🧠 **Key point / trap:** Idempotence = **retry-level, single-partition, single-session**. Transactions = **application-level atomicity across partitions/topics + offsets + zombie fencing**.
- 📎 Source: `resources/kafkaproducer-javadoc.md` ("application-level re-sends cannot be de-duplicated"; "guarantees within a single session"), Week 3 `README.md` (Buổi A §10 table idempotent vs transactional).

### Question 28 — Answer: **B**

- **Why correct:** `ProducerInterceptor` is the plugin point for cross-cutting behaviour without touching business code. It is enabled by adding the class to `interceptor.classes` (default empty list). `onSend(ProducerRecord)` is called before the key/value serializers run and may return a modified record, for example with an extra `trace-id` header; `onAcknowledgement(RecordMetadata, Exception)` is called on the I/O thread when the broker responds, which is the right place to increment per-topic counters. Interceptors chain in configuration order, and exceptions thrown inside them are logged and swallowed.
- **Why the others are wrong:** A — headers are separate from the value bytes; encoding them into the payload breaks every consumer and does not count acknowledgements. C — a `Partitioner` only chooses a partition and has no access to acknowledgements. D — a broker `Authorizer` decides ACLs; it cannot add headers or see client-side acks.
- 🧠 **Key point / trap:** "add metadata / audit / metrics on every produced record, no code change" → **`ProducerInterceptor` via `interceptor.classes`**. Consumer twin: `ConsumerInterceptor` with `onConsume`/`onCommit`.
- 📎 Source: `resources/producer-configs.md` (`interceptor.classes`: "intercept (and possibly mutate) the records ... before they are published"), Week 3 `README.md` (Buổi A §8).

### Question 29 — Answer: **B**

- **Why correct:** With RF=3 and `min.insync.replicas=2`, the leader accepts an `acks=all` write only while the ISR has at least 2 members. One broker down leaves ISR=2, so writes continue. Two brokers down leaves ISR=1 < 2, so the leader rejects writes with `NotEnoughReplicasException` (the producer retries until `delivery.timeout.ms`). Data that was already committed is still present on the surviving replica, so nothing already acknowledged is lost; availability is sacrificed to protect durability.
- **Why the others are wrong:** A and D — with 2 brokers down the ISR is 1, below `min.insync.replicas`, so writes stop; and `acks=all` waits for all *ISR* members, not just the leader. C — `min.insync.replicas=2` explicitly tolerates one failure while continuing to write.
- 🧠 **Key point / trap:** **RF=3 + `min.insync.replicas=2` = tolerate 1 broker for writes, tolerate 2 brokers without losing committed data.** `min.insync.replicas=3` would mean any single failure stops writes.
- 📎 Source: `resources/producer-configs.md` (`acks=all` semantics), `resources/confluent-producer-guide.md` (ISR commit rule), Week 2 `../week-02/README.md` (replication / ISR).
