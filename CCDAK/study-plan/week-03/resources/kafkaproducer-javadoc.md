# Apache Kafka 4.3 — Producer API & `KafkaProducer` Javadoc

> **Nguồn (official):** https://kafka.apache.org/documentation/#producerapi (trang mới: https://kafka.apache.org/43/apis/#producer-api) · https://kafka.apache.org/43/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html
> **Tuần:** 3 — Producer chuyên sâu + Transactions/EOS · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **`KafkaProducer` thread-safe**: 1 instance chia sẻ nhiều thread **nhanh hơn** nhiều instance (chia sẻ batch, connection, metadata). Ngược với `KafkaConsumer`.
- **`send()` là async**: bỏ record vào buffer per-partition và return `Future<RecordMetadata>` ngay; **I/O thread** nền gom batch gửi đi. Chỉ block khi chờ metadata hoặc buffer đầy — tối đa `max.block.ms` (**60000**).
- `batch.size` (**16384**) tăng → batch to hơn nhưng tốn RAM; `linger.ms` > 0 → chờ thêm record vào batch (đổi latency lấy throughput). `buffer.memory` (**33554432**) hết → block rồi `TimeoutException`.
- `acks=all` (mặc định) chờ full commit — chậm nhất nhưng bền nhất. `retries` mặc định **Integer.MAX_VALUE** → dùng **`delivery.timeout.ms`** (120000) để giới hạn thời gian retry.
- **Idempotent mặc định từ 3.0**: nâng at-least-once → exactly-once **trong 1 session**; **app tự gọi `send()` lại thì không dedup được**. Nếu `send()` fail dù retry vô hạn → nên tắt producer và kiểm tra record cuối có bị duplicate không.
- **Transactional**: set `transactional.id` → idempotence tự bật; topic nên **RF ≥ 3**, `min.insync.replicas=2`. API **blocking**, ném exception; **1 transaction mở/producer**; `initTransactions()` gọi **đúng 1 lần** và hoàn tất/abort transaction cũ cùng `transactional.id`.
- **Xử lý lỗi transaction**: `ProducerFencedException` / `OutOfOrderSequenceException` / `AuthorizationException` → **`close()`**; `KafkaException` khác → **`abortTransaction()`** rồi thử lại.
- `sendOffsetsToTransaction(offsets, consumer.groupMetadata())` đưa offset consumer vào cùng transaction (EOS consume-transform-produce); `flush()` block tới khi gửi hết; `close(Duration)` chờ tối đa timeout.
- Maven artifact: `org.apache.kafka:kafka-clients:4.3.1`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### 2.1 Producer API

Kafka includes six core apis: Producer, Consumer, Share consumer (share groups), Streams, Connect, Admin.

The Producer API allows applications to send streams of data to topics in the Kafka cluster. Examples showing how to use the producer are given in the javadocs. To use the producer, you can use the following maven dependency:

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>4.3.1</version>
</dependency>
```

### Class `KafkaProducer<K,V>`

A Kafka client that publishes records to the Kafka cluster.

**The producer is thread safe and sharing a single producer instance across threads will generally be faster than having multiple instances.**

Here is a simple example of using the producer to send records with strings containing sequential numbers as the key/value pairs.

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("linger.ms", 1);
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

Producer<String, String> producer = new KafkaProducer<>(props);
for (int i = 0; i < 100; i++)
    producer.send(new ProducerRecord<String, String>("my-topic", Integer.toString(i), Integer.toString(i)));

producer.close();
```

The producer consists of a pool of buffer space that holds records that haven't yet been transmitted to the server as well as a background I/O thread that is responsible for turning these records into requests and transmitting them to the cluster. Failure to close the producer after use will leak these resources.

The `send()` method is asynchronous. When called, it adds the record to a buffer of pending record sends and immediately returns. This allows the producer to batch together individual records for efficiency.

The `acks` config controls the criteria under which requests are considered complete. The default setting "all" will result in blocking on the full commit of the record, the slowest but most durable setting.

If the request fails, the producer can automatically retry. The `retries` setting defaults to `Integer.MAX_VALUE`, and it's recommended to use `delivery.timeout.ms` to control retry behavior, instead of `retries`.

The producer maintains buffers of unsent records for each partition. These buffers are of a size specified by the `batch.size` config. Making this larger can result in more batching, but requires more memory (since we will generally have one of these buffers for each active partition).

By default a buffer is available to send immediately even if there is additional unused space in the buffer. However if you want to reduce the number of requests you can set `linger.ms` to something greater than 0. This will instruct the producer to wait up to that number of milliseconds before sending a request in hope that more records will arrive to fill up the same batch. This is analogous to Nagle's algorithm in TCP. For example, in the code snippet above, likely all 100 records would be sent in a single request since we set our linger time to 1 millisecond. However this setting would add 1 millisecond of latency to our request waiting for more records to arrive if we didn't fill up the buffer. Note that records that arrive close together in time will generally batch together even with `linger.ms=0` so under heavy load batching will occur regardless of the linger configuration; however setting this to something larger than 0 can lead to fewer, more efficient requests when not under maximal load at the cost of a small amount of latency.

The `buffer.memory` controls the total amount of memory available to the producer for buffering. If records are sent faster than they can be transmitted to the server then this buffer space will be exhausted. When the buffer space is exhausted additional send calls will block. The threshold for time to block is determined by `max.block.ms` after which it throws a `TimeoutException`.

The `key.serializer` and `value.serializer` instruct how to turn the key and value objects the user provides with their `ProducerRecord` into bytes. You can use the included `ByteArraySerializer` or `StringSerializer` for simple byte or string types.

#### Idempotent producer

From Kafka 3.0, the `enable.idempotence` configuration defaults to true. When enabling idempotence, `retries` config will default to `Integer.MAX_VALUE` and the `acks` config will default to `all`. There are no API changes for the idempotent producer, so existing applications will not need to be modified to take advantage of this feature.

To take advantage of the idempotent producer, it is imperative to avoid application level re-sends since these cannot be de-duplicated. As such, if an application enables idempotence, it is recommended to leave the `retries` config unset, as it will be defaulted to `Integer.MAX_VALUE`. Additionally, if a `send(ProducerRecord)` returns an error even with infinite retries (for instance if the message expires in the buffer before being sent), then it is recommended to shut down the producer and check the contents of the last produced message to ensure that it is not duplicated. Finally, the producer can only guarantee idempotence for messages sent within a single session.

#### Transactional producer

To use the transactional producer and the attendant APIs, you must set the `transactional.id` configuration property. If the `transactional.id` is set, idempotence is automatically enabled along with the producer configs which idempotence depends on. Further, topics which are included in transactions should be configured for durability. In particular, the `replication.factor` should be at least 3, and the `min.insync.replicas` for these topics should be set to 2. Finally, in order for transactional guarantees to be realized from end-to-end, the consumers must be configured to read only committed messages as well.

The purpose of the `transactional.id` is to enable transaction recovery across multiple sessions of a single producer instance. It would typically be derived from the shard identifier in a partitioned, stateful, application. As such, it should be unique to each producer instance running within a partitioned application.

All the new transactional APIs are blocking and will throw exceptions on failure. The example below illustrates how the new APIs are meant to be used.

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("transactional.id", "my-transactional-id");
Producer<String, String> producer = new KafkaProducer<>(props, new StringSerializer(), new StringSerializer());

producer.initTransactions();

try {
    producer.beginTransaction();
    for (int i = 0; i < 100; i++)
        producer.send(new ProducerRecord<>("my-topic", Integer.toString(i), Integer.toString(i)));
    producer.commitTransaction();
} catch (ProducerFencedException | OutOfOrderSequenceException | AuthorizationException e) {
    // We can't recover from these exceptions, so our only option is to close the producer and exit.
    producer.close();
} catch (KafkaException e) {
    // For all other exceptions, just abort the transaction and try again.
    producer.abortTransaction();
}
producer.close();
```

As is hinted at in the example, there can be only one open transaction per producer. All messages sent between the `beginTransaction()` and `commitTransaction()` calls will be part of a single transaction. When the `transactional.id` is specified, all messages sent by the producer must be part of a transaction.

The transactional producer uses exceptions to communicate error states. In particular, it is not required to specify callbacks for `producer.send()` or to call `.get()` on the returned Future: a `KafkaException` would be thrown if any of the `producer.send()` or transactional calls hit an irrecoverable error during a transaction. By calling `producer.abortTransaction()` upon receiving a `KafkaException` we can ensure that any successful writes are marked as aborted, hence keeping the transactional guarantees.

### Method summary (selected)

- **`Future<RecordMetadata> send(ProducerRecord<K,V> record)` / `send(record, Callback callback)`** — Asynchronously send a record to a topic and invoke the provided callback when the send has been acknowledged. The send is asynchronous and this method will return immediately once the record has been stored in the buffer of records waiting to be sent. Fully non-blocking usage can make use of the `Callback` parameter to provide a callback that will be invoked when the request is complete. Callbacks for records being sent to the same partition are guaranteed to execute in order. Note that callbacks will generally execute in the I/O thread of the producer and so should be reasonably fast or they will delay the sending of messages from other threads. The `RecordMetadata` contains the partition the record was sent to, the offset it was assigned and the timestamp of the record. If `acks=0`, the offset will be -1.
- **`void flush()`** — Invoking this method makes all buffered records immediately available to send (even if `linger.ms` is greater than 0) and blocks on the completion of the requests associated with these records.
- **`List<PartitionInfo> partitionsFor(String topic)`** — Get the partition metadata for the given topic; blocks up to `max.block.ms`.
- **`void initTransactions()`** — Needs to be called before any other methods when the `transactional.id` is set in the configuration. This method does the following: 1. Ensures any transactions initiated by previous instances of the producer with the same `transactional.id` are completed. If the previous instance had failed with a transaction in progress, it will be aborted. If the last transaction had begun completion, but not yet finished, this method awaits its completion. 2. Gets the internal producer id and epoch, used in all future transactional messages issued by the producer.
- **`void beginTransaction()`** — Should be called before the start of each new transaction.
- **`void sendOffsetsToTransaction(Map<TopicPartition,OffsetAndMetadata> offsets, ConsumerGroupMetadata groupMetadata)`** — Sends a list of specified offsets to the consumer group coordinator, and also marks those offsets as part of the current transaction. These offsets will be considered committed only if the transaction is committed successfully. This method should be used when you need to batch consumed and produced messages together, typically in a consume-transform-produce pattern. The consumer group metadata should be obtained from `KafkaConsumer.groupMetadata()`, which lets the coordinator fence stale consumer instances.
- **`void commitTransaction()`** — Commits the ongoing transaction. This method will flush any unsent records before actually committing the transaction.
- **`void abortTransaction()`** — Aborts the ongoing transaction. Any unflushed produce messages will be aborted when this call is made.
- **`void close()` / `close(Duration timeout)`** — Close this producer. Blocks until all previously sent requests complete, or until the timeout expires. `close(Duration.ZERO)` fails pending requests immediately.
