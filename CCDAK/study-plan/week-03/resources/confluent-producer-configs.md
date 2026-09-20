# Confluent Platform — Kafka Producer Configuration Reference

> **Nguồn (official):** https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html
> **Tuần:** 3 — Producer chuyên sâu + Transactions/EOS · **Loại:** Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Trang Confluent liệt kê config **theo thứ tự importance high → low**; nội dung/mặc định **giống Apache Kafka** (Confluent Platform 8.0 tương ứng Kafka 4.0) — dùng để đối chiếu chéo với `producer-configs.md`.
- **Importance high**: `bootstrap.servers`, `key.serializer`/`value.serializer`, `buffer.memory` (**33554432**), `compression.type` (**none**), `retries` (**2147483647**).
- **Importance medium**: `batch.size` **16384**, `client.id`, `delivery.timeout.ms` **120000**, `linger.ms` **5**, `max.block.ms` **60000**, `max.request.size` **1048576**, `partitioner.class` **null**, `partitioner.ignore.keys` **false**, `request.timeout.ms` **30000**.
- **Importance low** nhưng đề hỏi nhiều: `acks` **all**, `enable.idempotence` **true**, `max.in.flight.requests.per.connection` **5**, `transactional.id` null, `transaction.timeout.ms` **60000**, `interceptor.classes` "", `metadata.max.age.ms` **300000**, `retry.backoff.ms` **100**, `retry.backoff.max.ms` **1000**, `partitioner.adaptive.partitioning.enable` **true**.
- Mô tả `acks` của Confluent nhấn mạnh: `acks=1` mất data nếu leader chết **ngay sau khi ack, trước khi follower replicate**; `acks=all` "leader waits for the **full set of in-sync replicas**".
- Mô tả `buffer.memory`: "records are sent faster than they can be delivered → block `max.block.ms` → **fail with an exception**".
- `max.block.ms` chi phối cả nhóm method transaction (`initTransactions`, `sendOffsetsToTransaction`, `commitTransaction`, `abortTransaction`) — đề hay hỏi "transaction API block bao lâu".
- `retries`: "no different than if the client resent the record upon receiving the error" — tức retry có thể **đổi thứ tự** nếu không idempotent và `max.in.flight > 1`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

To configure a Kafka producer in Confluent Platform, set the properties listed below. Properties appear in order of importance, from high to low. The Java producer shipped with Confluent Platform is the Apache Kafka Java client, so names and defaults match the Apache Kafka release the platform version is based on.

### acks
The number of acknowledgments the producer requires the leader to have received before considering a request complete. This controls the durability of records that are sent.
- `acks=0`: the producer will not wait for any acknowledgment from the server at all. The record will be immediately added to the socket buffer and considered sent. No guarantee can be made that the server has received the record, and the `retries` configuration will not take effect. The offset given back for each record will always be set to -1.
- `acks=1`: the leader will write the record to its local log but will respond without awaiting full acknowledgement from all followers. Should the leader fail immediately after acknowledging the record but before the followers have replicated it, the record will be lost.
- `acks=all` (equivalent to `-1`): the leader waits for the full set of in-sync replicas to acknowledge the record. This guarantees that the record will not be lost as long as at least one in-sync replica remains alive. This is the strongest available guarantee.
- Type: string · Default: **all** · Valid Values: [all, -1, 0, 1] · Importance: low

### enable.idempotence
When set to 'true', the producer will ensure that exactly one copy of each message is written in the stream. If 'false', producer retries due to broker failures, etc., may write duplicates of the retried message in the stream. Enabling idempotence requires `max.in.flight.requests.per.connection` ≤ 5 (with message ordering preserved for any allowable value), `retries` > 0, and `acks` = 'all'.
- Type: boolean · Default: **true** · Importance: low

### max.in.flight.requests.per.connection
The maximum number of unacknowledged requests the client will send on a single connection before blocking. If greater than 1 and `enable.idempotence` is false, there is a risk of message reordering after a failed send due to retries. Enabling idempotence requires this value to be ≤ 5.
- Type: int · Default: **5** · Valid Values: [1,…] · Importance: low

### retries
Number of times to retry a request that fails with a transient error. Setting a value greater than zero will cause the client to resend any record whose send fails with a potentially transient error. Note that this retry is no different than if the client resent the record upon receiving the error. Produce requests will be failed before the number of retries has been exhausted if `delivery.timeout.ms` expires first.
- Type: int · Default: **2147483647** · Valid Values: [0,…,2147483647] · Importance: high

### delivery.timeout.ms
An upper bound on the time to report success or failure after a call to `send()` returns. This limits the total time that a record will be delayed prior to sending, the time to await acknowledgement from the broker (if expected), and the time allowed for retriable send failures. Should be ≥ `request.timeout.ms` + `linger.ms`.
- Type: int · Default: **120000** (2 minutes) · Valid Values: [0,…] · Importance: medium

### request.timeout.ms
The configuration controls the maximum amount of time the client will wait for the response of a request. If the response is not received before the timeout elapses the client will resend the request if necessary or fail the request if retries are exhausted.
- Type: int · Default: **30000** (30 seconds) · Valid Values: [0,…] · Importance: medium

### linger.ms
The producer groups together any records that arrive in between request transmissions into a single batched request. This setting accomplishes this by adding a small amount of artificial delay — that is, rather than immediately sending out a record, the producer will wait for up to the given delay to allow other records to be sent so that the sends can be batched together.
- Type: long · Default: **5** · Valid Values: [0,…] · Importance: medium

### batch.size
The producer will attempt to batch records together into fewer requests whenever multiple records are being sent to the same partition. This configuration controls the default batch size in bytes.
- Type: int · Default: **16384** · Valid Values: [0,…] · Importance: medium

### buffer.memory
The total bytes of memory the producer can use to buffer records waiting to be sent to the server. If records are sent faster than they can be delivered to the server the producer will block for `max.block.ms` after which it will fail with an exception.
- Type: long · Default: **33554432** · Valid Values: [0,…] · Importance: high

### max.block.ms
The configuration controls how long the `KafkaProducer`'s `send()`, `partitionsFor()`, `initTransactions()`, `sendOffsetsToTransaction()`, `commitTransaction()` and `abortTransaction()` methods will block.
- Type: long · Default: **60000** (1 minute) · Valid Values: [0,…] · Importance: medium

### max.request.size
The maximum size of a request in bytes. This setting will limit the number of record batches the producer will send in a single request to avoid sending huge requests.
- Type: int · Default: **1048576** · Valid Values: [0,…] · Importance: medium

### compression.type
The compression type for all data generated by the producer. The default is none (i.e. no compression). Valid values are `none`, `gzip`, `snappy`, `lz4`, or `zstd`. Compression is of full batches of data, so the efficacy of batching will also impact the compression ratio.
- Type: string · Default: **none** · Importance: high

### partitioner.class
Determines which partition to send a record to when records are produced. Available options include the default partitioning logic (used when not set), `org.apache.kafka.clients.producer.RoundRobinPartitioner`, or custom implementations of the `org.apache.kafka.clients.producer.Partitioner` interface.
- Type: class · Default: **null** · Importance: medium

### partitioner.ignore.keys
When set to 'true' the producer won't use record keys to choose a partition. If 'false', producer would choose a partition based on a hash of the key when a key is present.
- Type: boolean · Default: **false** · Importance: medium

### partitioner.adaptive.partitioning.enable
When set to 'true', the producer will try to adapt to broker performance and produce more messages to partitions hosted on faster brokers. If 'false', the producer will try to distribute messages uniformly.
- Type: boolean · Default: **true** · Importance: low

### transactional.id
The TransactionalId to use for transactional delivery. This enables reliability semantics which span multiple producer sessions since it allows the client to guarantee that transactions using the same TransactionalId have been completed prior to starting any new transactions.
- Type: string · Default: **null** · Valid Values: non-empty string · Importance: low

### transaction.timeout.ms
The maximum amount of time in milliseconds that a transaction will remain open before the coordinator proactively aborts it.
- Type: int · Default: **60000** (1 minute) · Importance: low

### interceptor.classes
A list of classes to use as interceptors. Implementing the `org.apache.kafka.clients.producer.ProducerInterceptor` interface allows you to intercept (and possibly mutate) the records received by the producer before they are published to the Kafka cluster.
- Type: list · Default: "" · Importance: low

### retry.backoff.ms
The amount of time to wait before attempting to retry a failed request to a given topic partition. This avoids repeatedly sending requests in a tight loop under some failure scenarios.
- Type: long · Default: **100** · Valid Values: [0,…] · Importance: low

### retry.backoff.max.ms
The maximum amount of time in milliseconds to wait when retrying a request to the broker that has repeatedly failed.
- Type: long · Default: **1000** (1 second) · Valid Values: [0,…] · Importance: low

### metadata.max.age.ms
The period of time in milliseconds after which we force a refresh of metadata even if we haven't seen any partition leadership changes to proactively discover any new brokers or partitions.
- Type: long · Default: **300000** (5 minutes) · Valid Values: [0,…] · Importance: low

### client.id
An id string to pass to the server when making requests. The purpose of this is to be able to track the source of requests beyond just ip/port by allowing a logical application name to be included in server-side request logging.
- Type: string · Default: "" · Importance: medium
