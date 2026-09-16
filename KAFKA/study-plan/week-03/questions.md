# 📝 Practice Questions — Week 3: Producer Deep Dive + Transactions

> **29 questions** · real CCDAK exam style, difficulty ≥ real exam · covers the full Week 3 material (Kafka 4.3 defaults) plus 2 Week 2 review questions.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (number to choose is stated). Config names are the **Java client** names, as on the real exam.
> Back to [week plan](README.md) · [master plan](../../KAFKA-STUDY-PLAN.md)

---

### Question 1 — `[DEV · acks/min.insync.replicas · Single]`

A payments team runs a topic with `replication.factor=3` and all producers set `acks=all` and `enable.idempotence=true`. During a rolling restart two brokers were briefly down at the same time, yet the producers kept writing successfully. After the brokers came back, some of the records written during that window were **lost**. Which change prevents this in the future?

- A. Increase `retries` on the producer to `Integer.MAX_VALUE`
- B. Set `min.insync.replicas=2` on the topic (or broker), so writes fail with `NotEnoughReplicasException` instead of being accepted by a lone leader
- C. Set `max.in.flight.requests.per.connection=1` on the producer
- D. Change the producer to `acks=1` so the leader acknowledges faster

### Question 2 — `[DEV · Producer timeouts · Single]`

A developer starts a producer with the following properties:

```
delivery.timeout.ms=20000
linger.ms=5000
request.timeout.ms=30000
```

What happens?

- A. The producer starts and retries each record for up to 20 seconds
- B. The producer starts but `linger.ms` is silently reduced to 0
- C. Creating the `KafkaProducer` fails with a `ConfigException`, because `delivery.timeout.ms` must be greater than or equal to `linger.ms + request.timeout.ms`
- D. The producer starts and `request.timeout.ms` is automatically capped at 15000

### Question 3 — `[DEV · retries · Single]`

An operations team wants a producer to give up on a record after **at most 45 seconds** of trying, including the time spent waiting in the batch and all retries. `retries` is left at its default. Which single configuration achieves this?

- A. `retries=45`
- B. `request.timeout.ms=45000`
- C. `delivery.timeout.ms=45000`
- D. `max.block.ms=45000`

### Question 4 — `[DEV · Idempotent producer · Multi — Choose 2]`

A developer explicitly sets `enable.idempotence=true`. Which two other producer settings, if set to the given values, would cause the producer to **fail at startup** with a `ConfigException`? (Choose two.)

- A. `acks=1`
- B. `max.in.flight.requests.per.connection=5`
- C. `max.in.flight.requests.per.connection=8`
- D. `compression.type=zstd`
- E. `retries=2147483647`

### Question 5 — `[DEV · Ordering · Single]`

A Kafka 4.3 producer uses all default settings and sends records with the same key. A transient `NotLeaderOrFollowerException` causes one batch to be retried while later batches to the same partition are already in flight. What is the outcome?

- A. Records may be written out of order because `max.in.flight.requests.per.connection` defaults to 5; the developer must set it to 1
- B. Records are written exactly once and in order, because idempotence is enabled by default and the broker uses producer ID + sequence numbers to reorder and de-duplicate up to 5 in-flight batches
- C. The retried batch is dropped and the producer throws `OutOfOrderSequenceException`
- D. Records are written in order but duplicates may appear, because idempotence only applies when `acks=1`

### Question 6 — `[DEV · Idempotent producer · Single]`

An idempotent producer's callback receives an `OutOfOrderSequenceException`. What does this indicate and what should the application do?

- A. A transient network issue; the producer will retry automatically and nothing needs to be done
- B. The broker received a sequence number it did not expect for this producer ID, meaning data may have been lost or reordered on the broker side; this is fatal for the producer, so the application should close it and create a new producer
- C. The record exceeded `max.request.size`; increase it and resend
- D. The consumer committed offsets out of order; reset the consumer group

### Question 7 — `[DEV · Batching/throughput · Multi — Choose 2]`

A log-shipping producer sends many small JSON records to a 12-partition topic. Monitoring shows `batch-size-avg` is close to the record size and `request-rate` is very high. The team wants to **increase throughput and reduce the number of requests** while accepting a few milliseconds of extra latency. Which two changes are the MOST effective? (Choose two.)

- A. Increase `linger.ms` from the default 5 to, for example, 50
- B. Set `acks=0`
- C. Increase `batch.size` from the default 16384 and enable `compression.type=lz4`
- D. Set `max.in.flight.requests.per.connection=1`
- E. Decrease `buffer.memory`

### Question 8 — `[DEV · batch.size · Single]`

A producer has `batch.size=16384` (default) and `linger.ms=0`. The application sends a single 40 KB record. Which statement is correct?

- A. The record is rejected with `RecordTooLargeException` because it exceeds `batch.size`
- B. The record is split across three batches
- C. The record is sent in its own batch; `batch.size` is only an upper bound on how much the producer tries to accumulate per partition, and the effective limit for one record is `max.request.size` (1 MB by default)
- D. The producer waits until 16 KB worth of additional records arrive before sending

### Question 9 — `[DEV · buffer.memory/max.block.ms · Single]`

A producer application suddenly experiences `send()` calls that block for exactly **60 seconds** and then fail with a `TimeoutException` whose message mentions the buffer. Which is the MOST likely cause, and which setting controls the blocking time?

- A. The topic does not exist; controlled by `metadata.max.age.ms`
- B. Records are produced faster than they can be sent, so the 32 MB `buffer.memory` is exhausted; `send()` blocks for `max.block.ms` (default 60000) before failing with `BufferExhaustedException`
- C. `delivery.timeout.ms` expired; controlled by `retries`
- D. The consumer group is rebalancing; controlled by `session.timeout.ms`

### Question 10 — `[DEV · Compression · Single]`

A team produces highly compressible text records and wants the **best compression ratio with moderate CPU cost**. They also want to understand why the ratio is poor when `linger.ms=0`. Which statement is correct?

- A. Use `compression.type=snappy`; compression is per record, so `linger.ms` has no effect
- B. Use `compression.type=zstd`; compression is applied per **batch**, so small batches (low `linger.ms`, small `batch.size`) compress poorly and larger batches improve the ratio
- C. Use `compression.type=gzip`; the broker recompresses every batch anyway, so producer settings are irrelevant
- D. Use `compression.type=lz4`; it always has the highest ratio of all codecs

### Question 11 — `[DEV · Compression · Single]`

After enabling `compression.type=lz4` on all producers, broker CPU usage **increased** sharply on one topic. The topic-level configuration shows `compression.type=gzip`. What is happening and what is the fix?

- A. The broker must decompress each lz4 batch and recompress it as gzip; set the topic's `compression.type=producer` so the broker stores batches as received
- B. lz4 is not supported by the broker; switch producers to gzip
- C. Consumers are sending decompression work back to the broker; set `fetch.min.bytes` higher
- D. The broker is compacting the log; set `cleanup.policy=delete`

### Question 12 — `[DEV · Partitioner · Single]`

An order-processing topic has 6 partitions and producers key every record by `customerId`. To increase consumer parallelism, an operator runs `kafka-topics.sh --alter --partitions 12`. What is the consequence for ordering?

- A. None; the default partitioner remembers previous key-to-partition assignments
- B. Records for a given `customerId` may now go to a **different** partition than before, because the partitioner computes `murmur2(key) mod numPartitions`; ordering per key across old and new records is broken
- C. Only records with a `null` key are affected
- D. Kafka rejects the alter command because partition counts cannot change on keyed topics

### Question 13 — `[DEV · Partitioner · Single]`

A producer sends records with a `null` key to a 20-partition topic. A developer notices that within a few milliseconds, many consecutive records land in the **same** partition, then the producer switches to another partition. Which statement is correct?

- A. This is a bug in the default partitioner; the developer should set `partitioner.class=RoundRobinPartitioner`
- B. This is the built-in sticky partitioner (KIP-480/KIP-794) working as designed: unkeyed records stick to one partition until the batch is full or `linger.ms` elapses, producing larger batches and lower latency, while distribution stays even over time
- C. The records share an implicit key derived from the timestamp
- D. The producer has `partitioner.ignore.keys=true`, which forces a single partition

### Question 14 — `[DEV · Partitioner · Single]`

A team sets `partitioner.ignore.keys=true` on a producer that keys records by `deviceId` to get a perfectly even spread across partitions. What is the trade-off they must accept?

- A. None; keys are still used for partitioning, only for compaction they are ignored
- B. Records with the same `deviceId` can now land in different partitions, so per-key ordering and "one key, one partition" assumptions (for example for log compaction consumers) are lost
- C. The producer can no longer enable idempotence
- D. Compression is disabled because keys are stripped from the record

### Question 15 — `[DEV · Custom Partitioner · Single]`

A retailer wants records whose key starts with `vip-` to always go to partition 0, while all other keys keep the default hashing behavior. How should this be implemented?

- A. Implement `org.apache.kafka.clients.producer.Partitioner`, put the routing logic in `partition(...)`, and register it with `partitioner.class`
- B. Implement a `ProducerInterceptor` and change the record's partition in `onAcknowledgement`
- C. Create a second topic for VIP customers; Kafka cannot route by key prefix
- D. Set `partitioner.class=org.apache.kafka.clients.producer.RoundRobinPartitioner`

### Question 16 — `[DEV · RecordTooLarge · Multi — Choose 3]`

A producer must send 3 MB records. After raising `max.request.size` to 4 MB, the producer still fails with `RecordTooLargeException` ("larger than the max message size the server will accept"). Which three additional settings need to be reviewed so that the record can be produced **and** replicated **and** consumed? (Choose three.)

- A. Broker `message.max.bytes` (or topic `max.message.bytes`)
- B. Broker `replica.fetch.max.bytes`
- C. Producer `batch.size`
- D. Consumer `max.partition.fetch.bytes` (and `fetch.max.bytes`)
- E. Producer `linger.ms`

### Question 17 — `[DEV · Retriable vs fatal · Multi — Choose 2]`

Which two exceptions are **retriable**, meaning the Kafka producer retries them automatically (within `delivery.timeout.ms`) without any application code? (Choose two.)

- A. `RecordTooLargeException`
- B. `NotLeaderOrFollowerException`
- C. `SerializationException`
- D. `NotEnoughReplicasException`
- E. `TopicAuthorizationException`

### Question 18 — `[DEV · Serialization · Single]`

A producer is configured with `value.serializer=org.apache.kafka.common.serialization.LongSerializer`, but application code passes a `String` value. Where does the error surface?

- A. In the `Callback` as a retriable exception, and the producer retries until `delivery.timeout.ms`
- B. `send()` throws `SerializationException` **synchronously** before the record enters the buffer; it is not retried and the callback is not invoked
- C. The broker rejects the record with `InvalidRecordException`
- D. The consumer receives the record and fails to deserialize it

### Question 19 — `[DEV · TimeoutException · Single]`

Producers log:

```
org.apache.kafka.common.errors.TimeoutException: Expiring 12 record(s) for orders-3:120027 ms has passed since batch creation
```

Which statement is correct?

- A. `request.timeout.ms` (30 s) expired for one request; increase it to 120000
- B. `delivery.timeout.ms` (default 120000 ms) expired: the batch could not be successfully acknowledged within 2 minutes despite retries, usually because the partition leader was unavailable or the ISR was below `min.insync.replicas`; investigate the brokers first
- C. `linger.ms` is too high; set it to 0
- D. The consumer has not polled within `max.poll.interval.ms`

### Question 20 — `[DEV · Producer threading · Multi — Choose 2]`

A web service with 50 request-handling threads publishes events to Kafka. Which two statements about `KafkaProducer` are correct? (Choose two.)

- A. `KafkaProducer` is not thread-safe; each thread must create its own instance
- B. `KafkaProducer` is thread-safe and sharing one instance across threads is generally faster than using many instances, because batches and connections are shared
- C. Callbacks run on the producer's background I/O (sender) thread, so they must be fast and non-blocking; callbacks for the same partition execute in order
- D. Callbacks run on the thread that called `send()`, so they can safely perform blocking database calls
- E. `send()` always blocks until the broker acknowledges the record

### Question 21 — `[DEV · Transactions · Multi — Choose 2]`

A stream-processing service uses the Kafka transactional API. Each instance generates a **random UUID** as `transactional.id` on every start. Which two problems does this design cause? (Choose two.)

- A. Zombie fencing does not work: a stalled old instance is never fenced because the new instance registers under a different `transactional.id` and epoch, so both may commit output for the same input
- B. Transactions cannot span more than one partition
- C. `initTransactions()` cannot recover or abort an in-flight transaction left by the previous run of that instance, because the coordinator tracks transactions by `transactional.id`
- D. The producer is forced to use `acks=1`
- E. `__transaction_state` will be created with only 1 partition

### Question 22 — `[DEV · Transactions · Single]`

A transactional producer's `commitTransaction()` throws `ProducerFencedException`. What is the correct handling?

- A. Call `abortTransaction()` and retry the transaction with the same producer
- B. Increase `transaction.timeout.ms` and retry
- C. Treat it as fatal: another producer with the same `transactional.id` has been initialized with a higher epoch, so this producer must be closed (`close()`) and a new instance created
- D. Call `initTransactions()` again on the same producer to obtain a new epoch

### Question 23 — `[DEV · isolation.level/LSO · Single]`

A downstream consumer uses `isolation.level=read_committed`. Its lag suddenly grows even though the producer's `record-send-rate` is normal and brokers are healthy. A single upstream instance is hung inside an open transaction. Which explanation is correct?

- A. `read_committed` consumers can only read up to the **last stable offset (LSO)**, which is held at the first offset of the earliest still-open transaction; until that transaction commits, aborts, or is aborted by the coordinator after `transaction.timeout.ms` (default 60000 ms), no newer records are visible
- B. The consumer must switch to `read_uncommitted` because `read_committed` is deprecated
- C. The broker is compacting the partition; wait for `min.cleanable.dirty.ratio`
- D. The consumer's `max.poll.records` is too low

### Question 24 — `[DEV · Transactions API · Multi — Choose 2]`

A consume-transform-produce application must guarantee that its input offsets are committed **atomically** with its output records. Which two requirements are mandatory? (Choose two.)

- A. Call `producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata())` inside the transaction, before `commitTransaction()`
- B. Set `enable.auto.commit=true` on the consumer so offsets are committed every 5 seconds
- C. Set `enable.auto.commit=false` on the consumer and do not call `commitSync()`/`commitAsync()` for those offsets
- D. Set `acks=1` on the producer to reduce transaction latency
- E. Call `consumer.commitSync()` immediately after `commitTransaction()`

### Question 25 — `[DEV · Transactions · Single]`

A batch job needs transactions that may stay open for up to **20 minutes**. The developer sets `transaction.timeout.ms=1200000` on the producer and leaves the brokers at defaults. What happens when `initTransactions()` is called?

- A. It succeeds; the coordinator accepts any producer-specified timeout
- B. It fails with `InvalidTxnTimeoutException`, because the requested value exceeds the broker's `transaction.max.timeout.ms` (default 900000 ms = 15 minutes)
- C. It succeeds but the coordinator aborts every transaction after the default 60000 ms
- D. It blocks for `max.block.ms` and then throws `TimeoutException`

### Question 26 — `[ARCH · EOS boundaries · Single]`

A service consumes from Kafka and writes results to a **PostgreSQL** table, using a transactional Kafka producer with `sendOffsetsToTransaction`. The team claims this is exactly-once end-to-end. Which statement is correct?

- A. Correct; Kafka transactions include any external system the application writes to
- B. Incorrect; Kafka transactions only make Kafka topic writes and `__consumer_offsets` commits atomic. The database write is outside the transaction, so the service needs an idempotent sink (for example upsert keyed by record key or by topic-partition-offset), storing offsets in the same DB transaction, or an outbox/Connect-based design
- C. Incorrect; exactly-once requires `acks=0`
- D. Correct, as long as `isolation.level=read_committed` is set on the PostgreSQL connection

### Question 27 — `[DEV · Idempotent vs transactional · Multi — Choose 2]`

Which two situations are **NOT** protected by the idempotent producer alone (`enable.idempotence=true`, no `transactional.id`)? (Choose two.)

- A. A batch is retried after the acknowledgement was lost on the network, and would otherwise be written twice
- B. The application itself catches an exception and calls `send()` again for the same business event
- C. Two batches to the same partition arrive out of order after a retry
- D. The application writes to topic A, then crashes before writing the matching record to topic B, leaving a partial multi-topic write
- E. A retried batch is de-duplicated within the same producer session

### Question 28 — `[DEV · ProducerInterceptor · Single]`

A platform team wants to add a `trace-id` header to **every** record produced by many applications, and to count acknowledged records per topic, without modifying application code. Which mechanism fits?

- A. A custom `Serializer` that appends the header to the value bytes
- B. A `ProducerInterceptor` configured via `interceptor.classes`: `onSend()` runs before serialization and can add headers, and `onAcknowledgement()` runs when the broker responds and can update metrics
- C. A custom `Partitioner` that writes the header in `partition()`
- D. A broker-side `Authorizer` plugin

### Question 29 — `[FUND · Replication review (Week 2) · Single]`

A topic is created with `replication.factor=3` and `min.insync.replicas=2`; producers use `acks=all`. How many brokers hosting this partition can be **down simultaneously** while producers continue to write successfully, and how many can be down before committed data is at risk?

- A. 2 brokers down and writes continue; data is at risk only if all 3 are lost
- B. 1 broker down and writes continue (ISR = 2 ≥ `min.insync.replicas`); with 2 brokers down writes are rejected with `NotEnoughReplicasException`, but already-committed data is still safe on the surviving replica
- C. 0 brokers may be down; any failure stops writes
- D. 2 brokers down and writes continue, because `acks=all` only waits for the leader
