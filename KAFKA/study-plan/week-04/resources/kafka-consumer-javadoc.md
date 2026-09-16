# Apache Kafka 4.3 Javadoc — `KafkaConsumer` (offsets, failure detection, manual commit, seek, multi-threading)

> **Nguồn (official):** https://kafka.apache.org/43/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html
> **Tuần:** 4 — Consumer chuyên sâu: group, rebalance, offset · **Loại:** Apache Kafka Docs (Javadoc)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Consumer có 2 "vị trí": **position** = offset của record **tiếp theo** sẽ trả về (tự tăng sau `poll()`); **committed position** = offset cuối đã lưu an toàn → restart đọc tiếp từ đây. **Offset commit luôn là offset của record kế tiếp** (`lastProcessed + 1`).
- Phát hiện consumer chết: không heartbeat trong `session.timeout.ms` (**45 s**) → coordinator loại; không `poll()` trong `max.poll.interval.ms` (**5 phút**) → **client tự rời group**. Hai "núm chỉnh": `max.poll.interval.ms` (tăng) và `max.poll.records` (**500**, giảm để mỗi vòng nhanh hơn).
- Auto commit (`enable.auto.commit=true`, `auto.commit.interval.ms`) → **at-least-once**; manual `commitSync()` sau khi xử lý xong batch → at-least-once có kiểm soát; commit trước xử lý → at-most-once.
- `assign()` = **manual partition assignment**: không dùng group coordination, consumer chết **không** rebalance, không tự nhận partition mới; không trộn `assign()` với `subscribe()`.
- Lưu offset ngoài Kafka (DB) cùng kết quả trong **1 transaction** + `seek()` khi start → exactly-once ở phía consumer; cần `enable.auto.commit=false` và `seek` trong `onPartitionsAssigned`.
- Điều khiển vị trí: `seek(tp, offset)`, `seekToBeginning`, `seekToEnd`, `offsetsForTimes(Map<TP, ts>)` → `OffsetAndTimestamp` rồi `seek` (broker ≥ 0.10.1).
- `pause(partitions)` / `resume(partitions)`: vẫn `poll()` (giữ heartbeat, không bị kick) nhưng không nhận record từ partition đã pause → pattern worker pool.
- `isolation.level=read_committed`: chỉ đọc tới **LSO** (Last Stable Offset), lọc record của transaction abort; control marker chiếm offset nhưng không trả về.
- `KafkaConsumer` **không thread-safe**; phương thức duy nhất gọi từ thread khác là **`wakeup()`** → `poll()` ném `WakeupException`; 2 pattern: **1 consumer / thread** vs **tách consume và process** (queue + `pause`/`resume`, commit thủ công phức tạp hơn).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Cross-Version Compatibility

This client can communicate with brokers that are version 0.10.0 or newer. Older or newer brokers may not support certain features. For instance, brokers before version 0.10.1 don't support `offsetsForTimes`. An `UnsupportedVersionException` is thrown when invoking an API that is not available on the running broker version.

### Offsets and Consumer Position

Kafka maintains a numerical offset for each record in a partition. This offset acts as a unique identifier of a record within that partition, and also denotes the position of the consumer in the partition. The **position** of the consumer gives the offset of the next record that will be given out. It will be one larger than the highest offset the consumer has seen in that partition. It automatically advances every time the consumer receives messages in a call to `poll(Duration)`.

The **committed position** is the last offset that has been stored securely. Should the process fail and restart, this is the offset that the consumer will recover to. The consumer can either automatically commit offsets periodically; or it can choose to control this committed position manually by calling one of the commit APIs (e.g. `commitSync` and `commitAsync`).

### Consumer Groups and Topic Subscriptions

Kafka uses the concept of *consumer groups* to allow a pool of processes to divide the work of consuming and processing records. These processes can either be running on the same machine or they can be distributed over many machines. All consumer instances sharing the same `group.id` will be part of the same consumer group.

Each consumer in a group can dynamically set the list of topics it wants to subscribe to through one of the `subscribe` APIs. Kafka will deliver each message in the subscribed topics to one process in each consumer group. This is achieved by balancing the partitions between all members in the consumer group so that **each partition is assigned to exactly one consumer in the group**. So if there is a topic with four partitions, and a consumer group with two processes, each process would consume from two partitions.

Membership in a consumer group is maintained dynamically: if a process fails, the partitions assigned to it will be reassigned to other consumers in the same group. Similarly, if a new consumer joins the group, partitions will be moved from existing consumers to the new one. This is known as **rebalancing** the group. Group rebalancing is also used when new partitions are added to one of the subscribed topics or when a new topic matching a subscribed regex is created.

### Detecting Consumer Failures

After subscribing to a set of topics, the consumer will automatically join the group when `poll(Duration)` is invoked. The poll API is designed to ensure consumer liveness. As long as you continue to call poll, the consumer will stay in the group and continue to receive messages from the partitions it was assigned. Underneath the covers, the consumer sends periodic heartbeats to the server. If the consumer crashes or is unable to send heartbeats for a duration of `session.timeout.ms`, then the consumer will be considered dead and its partitions will be reassigned.

It is also possible that the consumer could encounter a "livelock" situation where it is continuing to send heartbeats, but no progress is being made. To prevent the consumer from holding onto its partitions indefinitely in this case, we provide a liveness detection mechanism using the `max.poll.interval.ms` setting. Basically if you don't call poll at least as frequently as the configured max interval, then the client will proactively leave the group so that another consumer can take over its partitions. When this happens, you may see an offset commit failure (as indicated by a `CommitFailedException` thrown from a call to `commitSync()`). This is a safety mechanism which guarantees that only active members of the group are able to commit offsets. So to stay in the group, you must continue to call poll.

The consumer provides two configuration settings to control the behavior of the poll loop:

1. `max.poll.interval.ms`: By increasing the interval between expected polls, you can give the consumer more time to handle a batch of records returned from `poll(Duration)`. The drawback is that increasing this value may delay a group rebalance since the consumer will only join the rebalance inside the call to poll.
2. `max.poll.records`: Use this setting to limit the total records returned from a single call to poll. This can make it easier to predict the maximum that must be handled within each poll interval. By tuning this value, you may be able to reduce the poll interval, which will reduce the impact of group rebalancing.

For use cases where message processing time varies unpredictably, neither of these options may be sufficient. The recommended way to handle these cases is to move message processing to another thread, which allows the consumer to continue calling poll while the processor is still working. Some care must be taken to ensure that committed offsets do not get ahead of the actual position. Typically, you must disable automatic commits and manually commit processed offsets for records only after the thread has finished handling them. Note also that you will need to `pause` the partition so that no new records are received from poll until after thread has finished handling those previously returned.

### Automatic Offset Committing

```java
Properties props = new Properties();
props.setProperty("bootstrap.servers", "localhost:9092");
props.setProperty("group.id", "test");
props.setProperty("enable.auto.commit", "true");
props.setProperty("auto.commit.interval.ms", "1000");
props.setProperty("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
props.setProperty("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("foo", "bar"));
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records)
        System.out.printf("offset = %d, key = %s, value = %s%n", record.offset(), record.key(), record.value());
}
```

Setting `enable.auto.commit` means that offsets are committed automatically with a frequency controlled by the config `auto.commit.interval.ms`.

### Manual Offset Control

Instead of relying on the consumer to periodically commit consumed offsets, users can also control when records should be considered as consumed and hence commit their offsets. This is useful when the consumption of the messages is coupled with some processing logic and hence a message should not be considered as consumed until it is completed processing.

```java
props.setProperty("enable.auto.commit", "false");
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("foo", "bar"));
final int minBatchSize = 200;
List<ConsumerRecord<String, String>> buffer = new ArrayList<>();
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        buffer.add(record);
    }
    if (buffer.size() >= minBatchSize) {
        insertIntoDb(buffer);
        consumer.commitSync();
        buffer.clear();
    }
}
```

In this example we will consume a batch of records and batch them up in memory. When we have enough records batched, we will insert them into a database. If we allowed offsets to auto commit as in the previous example, records would be considered consumed after they were returned to the user in `poll`. It would then be possible for our process to fail after batching the records, but before they had been inserted into the database. To avoid this, we will manually commit the offsets only after the corresponding records have been inserted into the database. This gives us exact control of when a record is considered consumed. This raises the opposite possibility: the process could fail in the interval after the insert into the database but before the commit (even though this would likely just be a few milliseconds, it is a possibility). In this case the process that took over consumption would consume from last committed offset and would repeat the insert of the last batch of data. Used in this way Kafka provides what is often called **"at-least-once"** delivery guarantees, as each record will likely be delivered one time but in failure cases could be duplicated.

The above example uses `commitSync` to mark all received records as committed. In some cases you may wish to have even finer control over which records have been committed by specifying an offset explicitly. In the example below we commit offset after we finish handling the records in each partition.

```java
try {
    while (running) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(Long.MAX_VALUE));
        for (TopicPartition partition : records.partitions()) {
            List<ConsumerRecord<String, String>> partitionRecords = records.records(partition);
            for (ConsumerRecord<String, String> record : partitionRecords) {
                System.out.println(record.offset() + ": " + record.value());
            }
            long lastOffset = partitionRecords.get(partitionRecords.size() - 1).offset();
            consumer.commitSync(Collections.singletonMap(partition, new OffsetAndMetadata(lastOffset + 1)));
        }
    }
} finally {
    consumer.close();
}
```

**Note: The committed offset should always be the offset of the next message that your application will read.** Thus, when calling `commitSync(offsets)` you should add one to the offset of the last message processed.

### Manual Partition Assignment

In the previous examples, we subscribed to the topics we were interested in and let Kafka dynamically assign a fair share of the partitions for those topics based on the active consumers in the group. However, in some cases you may need finer control over the specific partitions that are assigned. To use this mode, instead of subscribing to the topic using `subscribe`, you just call `assign(Collection)` with the full list of partitions that you want to consume.

```java
String topic = "foo";
TopicPartition partition0 = new TopicPartition(topic, 0);
TopicPartition partition1 = new TopicPartition(topic, 1);
consumer.assign(Arrays.asList(partition0, partition1));
```

Once assigned, you can call `poll` in a loop, just as in the preceding examples to consume records. The group that the consumer specifies is still used for committing offsets, but now the set of partitions will only change with another call to `assign`. Manual partition assignment does not use group coordination, so consumer failures will not cause assigned partitions to be rebalanced. Each consumer acts independently even if it shares a `groupId` with another consumer. To avoid offset commit conflicts, you should usually ensure that the `groupId` is unique for each consumer instance.

Note that it isn't possible to mix manual partition assignment (i.e. using `assign`) with dynamic partition assignment through topic subscription (i.e. using `subscribe`).

### Storing Offsets Outside Kafka

The consumer application need not use Kafka's built-in offset storage, it can store offsets in a store of its own choosing. The primary use case for this is allowing the application to store both the offset and the results of the consumption in the same system in a way that both the results and offsets are stored atomically. This is not always possible, but when it is it will make the consumption fully atomic and give **"exactly once"** semantics that are stronger than the default "at-least-once" semantics you get with Kafka's offset commit functionality.

Each record comes with its own offset, so to manage your own offset you just need to do the following:

- Configure `enable.auto.commit=false`
- Use the offset provided with each `ConsumerRecord` to save your position.
- On restart restore the position of the consumer using `seek(TopicPartition, long)`.

This type of usage is simplest when the partition assignment is also done manually (this would be likely in the search index use case described above). If the partition assignment is done automatically special care is needed to handle the case where partition assignments change. This can be done by providing a `ConsumerRebalanceListener` instance in the call to `subscribe(Collection, ConsumerRebalanceListener)`. When partitions are taken from a consumer the consumer will want to commit its offset for those partitions by implementing `ConsumerRebalanceListener.onPartitionsRevoked(Collection)`. When partitions are assigned to a consumer, the consumer will want to look up the offset for those new partitions and correctly initialize the consumer to that position by implementing `ConsumerRebalanceListener.onPartitionsAssigned(Collection)`.

### Controlling The Consumer's Position

In most use cases the consumer will simply consume records from beginning to end, periodically committing its position. However Kafka allows the consumer to manually control its position, moving forward or backwards in a partition at will. This means a consumer can re-consume older records, or skip to the most recent records without actually consuming the intermediate records.

Kafka allows specifying the position using `seek(TopicPartition, long)` to specify the new position. Special methods for seeking to the earliest and latest offset the server maintains are also available (`seekToBeginning(Collection)` and `seekToEnd(Collection)` respectively). `offsetsForTimes(Map)` looks up the offsets for the given partitions by timestamp, returning the earliest offset whose timestamp is greater than or equal to the given timestamp.

### Consumption Flow Control

If a consumer is assigned multiple partitions to fetch data from, it will try to consume from all of them at the same time, effectively giving these partitions the same priority for consumption. Kafka supports dynamic controlling of consumption flows by using `pause(Collection)` and `resume(Collection)` to pause the consumption on the specified assigned partitions and resume the consumption on the specified paused partitions respectively in the future `poll(Duration)` calls.

### Reading Transactional Messages

Transactions were introduced in Kafka 0.11.0 wherein applications can write to multiple topics and partitions atomically. In order for this to work, consumers reading from these partitions should be configured to only read committed data. This can be achieved by setting the `isolation.level=read_committed` in the consumer's configuration.

In `read_committed` mode, the consumer will read only those transactional messages which have been successfully committed. It will continue to read non-transactional messages as before. There is no client-side buffering in `read_committed` mode. Instead, the end offset of a partition for a `read_committed` consumer would be the offset of the first message in the partition belonging to an open transaction. This offset is known as the **'Last Stable Offset' (LSO)**.

A `read_committed` consumer will only read up to the LSO and filter out any transactional messages which have been aborted. The LSO also affects the behavior of `seekToEnd(Collection)` and `endOffsets(Collection)` for `read_committed` consumers. Partitions with transactional messages will include commit or abort markers which indicate the result of a transaction. There markers are not returned to applications, yet have an offset in the log. As a result, applications reading from topics with transactional messages will see gaps in the consumed offsets.

### Multi-threaded Processing

**The Kafka consumer is NOT thread-safe.** All network I/O happens in the thread of the application making the call. It is the responsibility of the user to ensure that multi-threaded access is properly synchronized. Un-synchronized access will result in `ConcurrentModificationException`.

The only exception to this rule is `wakeup()`, which can safely be used from an external thread to interrupt an active operation. In this case, a `WakeupException` will be thrown from the thread blocking on the operation. This can be used to shutdown the consumer from another thread.

```java
public class KafkaConsumerRunner implements Runnable {
    private final AtomicBoolean closed = new AtomicBoolean(false);
    private final KafkaConsumer consumer;

    public void run() {
        try {
            consumer.subscribe(Arrays.asList("topic"));
            while (!closed.get()) {
                ConsumerRecords records = consumer.poll(Duration.ofMillis(10000));
                // Handle new records
            }
        } catch (WakeupException e) {
            // Ignore exception if closing
            if (!closed.get()) throw e;
        } finally {
            consumer.close();
        }
    }

    // Shutdown hook which can be called from a separate thread
    public void shutdown() {
        closed.set(true);
        consumer.wakeup();
    }
}
```

#### 1. One Consumer Per Thread

A simple option is to give each thread its own consumer instance. **PRO:** It is the easiest to implement; it is often the fastest as no inter-thread co-ordination is needed; it makes in-order processing on a per-partition basis very easy to implement (each thread just processes messages in the order it receives them). **CON:** More consumers means more TCP connections to the cluster (one per thread); multiple consumers means more requests being sent to the server and slightly less batching of data; the number of total threads across all processes will be limited by the total number of partitions.

#### 2. Decouple Consumption and Processing

Another alternative is to have one or more consumer threads that do all data consumption and hands off `ConsumerRecords` instances to a blocking queue consumed by a pool of processor threads that actually handle the record processing. **PRO:** This option allows independently scaling the number of consumers and processors. This makes it possible to have a single consumer that feeds many processor threads, avoiding any limitation on partitions. **CON:** Guaranteeing order across the processors requires particular care as the threads will execute independently; manually committing the position becomes harder as it requires that all threads co-ordinate to ensure that processing is complete for that partition.
