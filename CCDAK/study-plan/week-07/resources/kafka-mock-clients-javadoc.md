# Apache Kafka 4.3 Javadoc — `MockProducer<K,V>` & `MockConsumer<K,V>` (kafka-clients)

> **Nguồn (official):** https://kafka.apache.org/43/javadoc/org/apache/kafka/clients/producer/MockProducer.html · https://kafka.apache.org/43/javadoc/org/apache/kafka/clients/consumer/MockConsumer.html
> **Tuần:** 7 — Security & Testing · **Loại:** Apache Kafka Javadoc 4.3 (package `org.apache.kafka.clients`)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `MockProducer<K,V>` **implements `Producer<K,V>`** (nằm ngay trong `kafka-clients`, không cần thư viện test riêng) → inject vào code thay `KafkaProducer` qua interface. **Mặc định mỗi `send()` hoàn thành đồng bộ, thành công** (`MockProducer()` no-arg = autoComplete true, metadata "invented").
- Constructor quan trọng: `MockProducer(boolean autoComplete, Partitioner partitioner, Serializer<K> keySerializer, Serializer<V> valueSerializer)` (partitioner có thể `null`) và bản có `Cluster` để giả metadata partition. **`autoComplete=false`** → future treo cho tới khi test gọi **`completeNext()`** (thành công) hoặc **`errorNext(RuntimeException e)`** (complete future + gọi callback với exception) — đây là cách test đường lỗi/retry/DLQ **không cần broker**. Cả hai trả `boolean` (false nếu không còn call chờ).
- **`history()`** = danh sách `ProducerRecord` đã gửi từ lần `clear()` cuối, **bất kể** future đã hoàn thành hay chưa → assert topic/key/value/header. `flushed()` = mọi record đã hoàn thành; `closed()`.
- Transaction API đầy đủ: `initTransactions` / `beginTransaction` / `commitTransaction` / `abortTransaction` / `sendOffsetsToTransaction`; kiểm tra bằng `transactionInitialized()`, `transactionInFlight()`, `transactionCommitted()`, `transactionAborted()`, `commitCount()`, `uncommittedRecords()`, `uncommittedOffsets()`, `sentOffsets()`, `consumerGroupOffsetsHistory()`. **`fenceProducer()`** → các thao tác transactional sau đó ném `ProducerFencedException`.
- Inject lỗi bằng **field public**: `sendException`, `initTransactionException`, `beginTransactionException`, `commitTransactionException`, `abortTransactionException`, `sendOffsetsToTransactionException`, `flushException`, `closeException`, `partitionsForException` (gán RuntimeException → method tương ứng ném).
- `MockConsumer<K,V>` **implements `Consumer<K,V>`**, **KHÔNG thread-safe**; constructor **`MockConsumer(String offsetResetStrategy)`** nhận giá trị của `auto.offset.reset` (`"earliest"`/`"latest"`/`"none"`); bản `MockConsumer(OffsetResetStrategy)` **deprecated từ 4.0**.
- Recipe bắt buộc: **`assign(partitions)`** (hoặc `subscribe(...)` rồi **`rebalance(newAssignment)`** để giả rebalance vì mock không có coordinator) → **`updateBeginningOffsets(Map<TopicPartition,Long>)`** (thiếu → `poll` ném `IllegalStateException` vì không có position) → **`addRecord(ConsumerRecord)`** → `poll(Duration)` trả record. `updateEndOffsets` cho `seekToEnd`/`endOffsets`/`currentLag`.
- **`schedulePollTask(Runnable)`**: mỗi lần `poll()` chạy **1 task** đã xếp hàng (FIFO) — dùng để `addRecord`, `setPollException`, gọi `wakeup()` từ test thread → test **poll loop vô hạn** an toàn; `scheduleNopPollTask()` = task rỗng. `setPollException(KafkaException)` → lần `poll` kế tiếp ném; `setOffsetsException` → commit/seek ném; `setMaxPollRecords(long)` giới hạn số record mỗi poll.
- Kiểm tra commit: **`committed(Set<TopicPartition>)`** trả `OffsetAndMetadata` đã commit qua `commitSync`/`commitAsync`; `position()` trả vị trí hiện tại; `closed()`; `paused()`; `shouldRebalance()`/`resetShouldRebalance()` đi cùng `enforceRebalance()`.
- Dùng `MockProducer`/`MockConsumer` khi assertion **không phụ thuộc hành vi broker** (callback, retry, commit logic, transaction API); cần rebalance thật, `read_committed`, ACL/TLS → Testcontainers (xem `testcontainers-kafka.md`).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Class MockProducer<K,V>

```
java.lang.Object
  org.apache.kafka.clients.producer.MockProducer<K,V>
All Implemented Interfaces: Closeable, AutoCloseable, Producer<K,V>

public class MockProducer<K,V> extends Object implements Producer<K,V>
```

A mock of the producer interface you can use for testing code that uses Kafka. By default this mock will synchronously complete each send call successfully. However it can be configured to allow the user to control the completion of the call and supply an optional error for the producer to throw.

#### Field Summary

| Modifier and Type | Field | Description |
| --- | --- | --- |
| `RuntimeException` | `abortTransactionException` | Exception to throw when `abortTransaction()` is called |
| `RuntimeException` | `beginTransactionException` | Exception to throw when `beginTransaction()` is called |
| `RuntimeException` | `closeException` | Exception to throw when `close()` or `close(Duration)` is called |
| `RuntimeException` | `commitTransactionException` | Exception to throw when `commitTransaction()` is called |
| `RuntimeException` | `flushException` | Exception to throw when `flush()` is called |
| `RuntimeException` | `initTransactionException` | Exception to throw when `initTransactions()` is called |
| `RuntimeException` | `partitionsForException` | Exception to throw when `partitionsFor(String)` is called |
| `RuntimeException` | `sendException` | Exception to throw when `send(ProducerRecord)` or `send(ProducerRecord, Callback)` is called |
| `RuntimeException` | `sendOffsetsToTransactionException` | Exception to throw when `sendOffsetsToTransaction(Map, ConsumerGroupMetadata)` is called |

#### Constructor Summary

| Constructor | Description |
| --- | --- |
| `MockProducer()` | Create a new mock producer with invented metadata. |
| `MockProducer(boolean autoComplete, Partitioner partitioner, Serializer<K> keySerializer, Serializer<V> valueSerializer)` | Create a new mock producer with invented metadata the given autoComplete setting, partitioner and key\value serializers. |
| `MockProducer(Cluster cluster, boolean autoComplete, Partitioner partitioner, Serializer<K> keySerializer, Serializer<V> valueSerializer)` | Create a mock producer |

#### Method Summary

| Modifier and Type | Method | Description |
| --- | --- | --- |
| `void` | `abortTransaction()` | See `KafkaProducer.abortTransaction()` |
| `void` | `beginTransaction()` | See `KafkaProducer.beginTransaction()` |
| `void` | `clear()` | Clear the stored history of sent records, consumer group offsets |
| `void` | `close()` / `close(Duration timeout)` | See `KafkaProducer.close()` |
| `boolean` | `closed()` | Checks whether this mock producer has been closed. |
| `long` | `commitCount()` | Gets the total number of transactions committed by this mock producer. |
| `void` | `commitTransaction()` | See `KafkaProducer.commitTransaction()` |
| `boolean` | `completeNext()` | Complete the earliest uncompleted call successfully. |
| `List<Map<String,Map<TopicPartition,OffsetAndMetadata>>>` | `consumerGroupOffsetsHistory()` | Get the list of committed consumer group offsets since the last call to `clear()` |
| `boolean` | `errorNext(RuntimeException e)` | Complete the earliest uncompleted call with the given error. |
| `void` | `fenceProducer()` | Fences this mock producer, causing it to throw `ProducerFencedException` on subsequent transactional operations. |
| `void` | `flush()` | See `KafkaProducer.flush()` |
| `boolean` | `flushed()` | Checks whether all sent records have been completed (no pending completions). |
| `List<ProducerRecord<K,V>>` | `history()` | Get the list of sent records since the last call to `clear()` |
| `void` | `initTransactions()` | See `KafkaProducer.initTransactions()` |
| `Map<MetricName,Metric>` | `metrics()` | See `KafkaProducer.metrics()` |
| `List<PartitionInfo>` | `partitionsFor(String topic)` | See `KafkaProducer.partitionsFor(String)` |
| `Future<RecordMetadata>` | `send(ProducerRecord<K,V> record)` | Adds the record to the list of sent records. |
| `Future<RecordMetadata>` | `send(ProducerRecord<K,V> record, Callback callback)` | Adds the record to the list of sent records. |
| `void` | `sendOffsetsToTransaction(Map<TopicPartition,OffsetAndMetadata> offsets, ConsumerGroupMetadata groupMetadata)` | See `KafkaProducer.sendOffsetsToTransaction(Map, ConsumerGroupMetadata)` |
| `boolean` | `sentOffsets()` | Checks whether offsets have been sent to the current transaction. |
| `void` | `setMockMetrics(MetricName name, Metric metric)` | Set a mock metric for testing purpose |
| `boolean` | `transactionAborted()` | Checks whether the current transaction has been aborted. |
| `boolean` | `transactionCommitted()` | Checks whether the current transaction has been committed. |
| `boolean` | `transactionInFlight()` | Checks whether a transaction is currently in progress. |
| `boolean` | `transactionInitialized()` | Checks whether transactions have been initialized for this mock producer. |
| `Map<String,Map<TopicPartition,OffsetAndMetadata>>` | `uncommittedOffsets()` | Gets the consumer group offsets sent in the current transaction that have not yet been committed. |
| `List<ProducerRecord<K,V>>` | `uncommittedRecords()` | Gets the list of records sent in the current transaction that have not yet been committed. |
| `Uuid` | `clientInstanceId(Duration timeout)` / `setClientInstanceId(Uuid)` / `injectTimeoutException(int)` / `disableTelemetry()` | Telemetry helpers (KIP-714) for testing purposes. |
| `List<KafkaMetric>` | `addedMetrics()` / `registerMetricForSubscription(KafkaMetric)` / `unregisterMetricFromSubscription(KafkaMetric)` | Metric subscription helpers. |

### Class MockConsumer<K,V>

```
java.lang.Object
  org.apache.kafka.clients.consumer.MockConsumer<K,V>
All Implemented Interfaces: Closeable, AutoCloseable, Consumer<K,V>

public class MockConsumer<K,V> extends Object implements Consumer<K,V>
```

A mock of the `Consumer` interface you can use for testing code that uses Kafka. This class is **not threadsafe**. However, you can use the `schedulePollTask(Runnable)` method to write multithreaded tests where a driver thread waits for `poll(Duration)` to be called by a background thread and then can safely perform operations during a callback.

#### Constructor Summary

| Constructor | Description |
| --- | --- |
| `MockConsumer(String offsetResetStrategy)` | A mock consumer is instantiated by providing `ConsumerConfig.AUTO_OFFSET_RESET_CONFIG` value as the input. |
| `MockConsumer(OffsetResetStrategy offsetResetStrategy)` | **Deprecated.** Since 4.0. |

#### Method Summary (chọn lọc — đầy đủ ở link gốc)

| Modifier and Type | Method | Ghi chú |
| --- | --- | --- |
| `void` | `addRecord(ConsumerRecord<K,V> record)` | Record được trả ở lần `poll` kế tiếp; partition phải đã được assign và có beginning offset. |
| `void` | `assign(Collection<TopicPartition> partitions)` | Gán partition thủ công (không cần coordinator). |
| `Set<TopicPartition>` | `assignment()` | |
| `Map<TopicPartition,Long>` | `beginningOffsets(Collection<TopicPartition>)` / `endOffsets(Collection<TopicPartition>)` | Trả giá trị đã set bằng `updateBeginningOffsets` / `updateEndOffsets`. |
| `void` | `close()` / `close(CloseOptions option)` / `close(Duration)` (deprecated) | |
| `boolean` | `closed()` | |
| `void` | `commitAsync()` / `commitAsync(OffsetCommitCallback)` / `commitAsync(Map<TopicPartition,OffsetAndMetadata>, OffsetCommitCallback)` | |
| `void` | `commitSync()` / `commitSync(Duration)` / `commitSync(Map<TopicPartition,OffsetAndMetadata>)` / `commitSync(Map, Duration)` | |
| `Map<TopicPartition,OffsetAndMetadata>` | `committed(Set<TopicPartition> partitions)` / `committed(Set<TopicPartition>, Duration)` | Đọc offset đã commit — dùng để assert commit logic. |
| `OptionalLong` | `currentLag(TopicPartition)` | |
| `void` | `enforceRebalance()` / `enforceRebalance(String reason)` | Đặt cờ `shouldRebalance()`. |
| `ConsumerGroupMetadata` | `groupMetadata()` | |
| `Duration` | `lastPollTimeout()` | Timeout của lần `poll` gần nhất. |
| `Map<String,List<PartitionInfo>>` | `listTopics()` | |
| `Map<TopicPartition,OffsetAndTimestamp>` | `offsetsForTimes(Map<TopicPartition,Long>)` | |
| `List<PartitionInfo>` | `partitionsFor(String topic)` | Từ `updatePartitions`. |
| `void` | `pause(Collection<TopicPartition>)` / `resume(Collection<TopicPartition>)` | |
| `Set<TopicPartition>` | `paused()` | |
| `ConsumerRecords<K,V>` | `poll(Duration timeout)` | Chạy 1 scheduled task (nếu có) rồi trả record đã `addRecord`; ném exception đã `setPollException`. |
| `long` | `position(TopicPartition partition)` | |
| `void` | `rebalance(Collection<TopicPartition> newAssignment)` | **Simulate a rebalance event.** Gọi `onPartitionsRevoked`/`onPartitionsAssigned` của listener đã `subscribe`. |
| `void` | `resetShouldRebalance()` | |
| `void` | `scheduleNopPollTask()` | |
| `void` | `schedulePollTask(Runnable task)` | **Schedule a task to be executed during a poll().** One task per poll invocation. |
| `void` | `seek(TopicPartition, long offset)` / `seek(TopicPartition, OffsetAndMetadata)` | |
| `void` | `seekToBeginning(Collection<TopicPartition>)` / `seekToEnd(Collection<TopicPartition>)` | |
| `void` | `setMaxPollRecords(long maxPollRecords)` | Sets the maximum number of records returned in a single call to `poll(Duration)`. |
| `void` | `setOffsetsException(KafkaException exception)` | |
| `void` | `setPollException(KafkaException exception)` | |
| `boolean` | `shouldRebalance()` | |
| `void` | `subscribe(Collection<String> topics)` / `subscribe(Collection<String>, ConsumerRebalanceListener)` / `subscribe(Pattern)` / `subscribe(SubscriptionPattern)` | Chỉ ghi nhận subscription; assignment thật phải qua `rebalance(...)`. |
| `Set<String>` | `subscription()` | |
| `void` | `unsubscribe()` | |
| `void` | `updateBeginningOffsets(Map<TopicPartition,Long> newOffsets)` | **Bắt buộc** trước `poll` khi reset strategy = earliest. |
| `void` | `updateEndOffsets(Map<TopicPartition,Long> newOffsets)` | Cần khi reset strategy = latest / dùng `seekToEnd` / `currentLag`. |
| `void` | `updateDurationOffsets(Map<TopicPartition,Long> newOffsets)` | |
| `void` | `updatePartitions(String topic, List<PartitionInfo> partitions)` | Metadata giả cho `partitionsFor`/`listTopics`. |
| `void` | `wakeup()` | Lần `poll` kế tiếp ném `WakeupException`. |
| `Uuid` | `clientInstanceId(Duration)` / `setClientInstanceId(Uuid)` / `injectTimeoutException(int)` / `disableTelemetry()` | Telemetry helpers. |

### Ghi chú thêm (tổng hợp, không nằm trong javadoc)

- Pattern test producer với `autoComplete=false`:

```java
MockProducer<String, String> producer = new MockProducer<>(false, null, new StringSerializer(), new StringSerializer());
Future<RecordMetadata> f = producer.send(new ProducerRecord<>("orders", "k1", "v1"), (md, ex) -> { /* callback */ });
assertFalse(f.isDone());
producer.errorNext(new TimeoutException("simulated"));   // callback nhận ex, f.get() ném ExecutionException
assertEquals(1, producer.history().size());
```

- Pattern test consumer:

```java
MockConsumer<String, String> consumer = new MockConsumer<>("earliest");
TopicPartition tp = new TopicPartition("orders", 0);
consumer.assign(List.of(tp));
consumer.updateBeginningOffsets(Map.of(tp, 0L));
consumer.addRecord(new ConsumerRecord<>("orders", 0, 0L, "k1", "v1"));
ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
consumer.commitSync();
assertEquals(1L, consumer.committed(Set.of(tp)).get(tp).offset());   // commit = offset record KẾ TIẾP
```

- Thư viện ngoài `kafka-clients`: `TopologyTestDriver` (`kafka-streams-test-utils`) cho Streams; `MockSchemaRegistryClient` / URL `mock://` (Confluent serializer) cho Avro/Protobuf serde.
