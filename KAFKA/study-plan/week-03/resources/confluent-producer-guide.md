# Confluent — Kafka Producer for Confluent Platform (concepts guide) + Kafka Internals course: Producer hands-on

> **Nguồn (official):** https://docs.confluent.io/platform/current/clients/producer.html · https://developer.confluent.io/courses/architecture/producer-hands-on/
> **Tuần:** 3 — Producer chuyên sâu + Transactions/EOS · **Loại:** Confluent Docs (+ Confluent Developer course)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Producer không cần group coordination** → đơn giản hơn consumer. **Partitioner** map message → partition, producer gửi produce request tới **leader** của partition đó.
- Key **không rỗng giống nhau → cùng partition** (hash **murmur2**); không key → **sticky partitioner** gom batch.
- **Mọi write đi qua leader**; follower fetch từ leader; message được coi là **committed khi toàn bộ ISR đã ack** → mới đọc được.
- `acks`: `all` (mặc định) = leader + toàn bộ ISR; `1` = chỉ leader; `0` = không chờ (throughput max, không bền).
- **Ordering**: `retries > 0` có thể **đổi thứ tự** nếu retry thành công sau request sau; tài liệu Confluent ghi "`max.in.flight.requests.per.connection=1` để retry không reorder" — **đây là cách cũ**; với idempotence (mặc định) thì ≤ 5 vẫn giữ thứ tự.
- **Batching & nén**: `batch.size` (byte, Java client) và `linger.ms` cho batch đầy; `compression.type` nén **cả batch** → batch to nén tốt hơn. Client C/C++/Python/Go/.NET (librdkafka) dùng thêm `batch.num.messages`.
- **Queuing limits**: `buffer.memory` giới hạn RAM cho message chưa gửi → đầy thì **block**; `request.timeout.ms` tránh xếp hàng vô hạn.
- **Bảng perf-test (course)**: `linger.ms` 0 → 100 làm `batch-size-avg` **1215 → 16165** byte (≈ đầy `batch.size` 16384) nhưng `record-queue-time-avg` **4.2 → 95.5 ms**; `linger.ms=1500`+`batch.size=300000` → batch 275.700 byte nhưng queue time **1406 ms**. Với load thấp (200 rec/s), default lại tối ưu nhất → **tăng linger chỉ có lợi khi có đủ load**.
- Metrics cần thuộc: `batch-size-avg`, `outgoing-byte-rate`, `record-queue-time-avg`, `request-latency-avg` (Tuần 8 đào sâu).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Kafka Producer for Confluent Platform — Concepts

An Apache Kafka® Producer is a client application that publishes (writes) events to a Kafka cluster. The producer does not require group coordination, so it is conceptually simpler than the consumer.

**Partitioning.** The partitioner maps each message to a topic partition, and the producer sends a produce request to the leader of that partition. The partitioners shipped with Kafka guarantee that all messages with the same non-empty key will be sent to the same partition (using a murmur2 hash of the key). If no key is provided, partitions are chosen in a batching-aware manner by the sticky partitioner so that unkeyed records fill batches before moving on to another partition.

**Replication and durability.** Each partition in the Kafka cluster has a leader and a set of replicas among the brokers. All writes to the partition must go through the partition leader. The replicas are kept in sync by fetching from the leader. When the leader shuts down or fails, the next leader is chosen from among the in-sync replicas. Depending on how the producer is configured, each produce request to the partition leader can be held until the replicas have successfully acknowledged the write. This gives the producer some control over message durability at some cost to overall throughput. Messages written to the partition leader are not immediately readable by consumers regardless of the producer's acknowledgement settings. **When all in-sync replicas have acknowledged the write, then the message is considered committed, which makes it available for reading.** This ensures that messages cannot be lost by a broker failure after they have already been returned to the consumer.

### Kafka Producer configuration

**Core configuration.** You are required to set the `bootstrap.servers` property so that the producer can find the Kafka cluster. Although not required, you should always set a `client.id` since this allows you to easily correlate requests on the broker with the client instance which made it. These settings are the same for Java, C/C++, Python, Go and .NET clients.

**Message durability.** You can control the durability of messages written to Kafka through the `acks` setting. The default value of `all` requires an explicit acknowledgement from the partition leader that the write succeeded and that it was replicated to all in-sync replicas. The strongest guarantee is `acks=all`, which means the leader waits for the full set of in-sync replicas to acknowledge the record. If you set `acks=1`, only the leader is required to acknowledge; a leader failure right after the acknowledgement can lose the record. With `acks=0`, the producer does not wait for acknowledgement at all, which maximizes throughput but offers no durability guarantee.

**Message ordering.** In general, messages are written to the broker in the same order that they are received by the producer client. However, if you enable message retries by setting `retries` to a value larger than 0 (which is the default), then message reordering may occur since the retry may occur after a following write succeeded. To enable retries without reordering, you can set `max.in.flight.requests.per.connection` to 1 to ensure that only one request can be sent to the broker at a time. Without retries enabled, the broker will preserve the order of writes it receives, but there could be gaps due to individual send failures. *(Editorial note for exam: with the idempotent producer, which is enabled by default since Kafka 3.0, ordering is preserved for `max.in.flight.requests.per.connection` up to 5 without setting it to 1.)*

**Batching and compression.** Kafka producers attempt to collect sent messages into batches to improve throughput. With the Java client, you can use `batch.size` to control the maximum size in bytes of each message batch. To give more time for batches to fill, you can use `linger.ms` to have the producer delay sending. Compression can be enabled with the `compression.type` setting. Compression covers full message batches, so larger batches will typically mean a higher compression rate. With the librdkafka-based clients (C/C++, Python, Go, .NET) you can use `batch.num.messages` to set a limit on the number of messages contained in each batch.

**Queuing limits.** Use `buffer.memory` to limit the total memory that is available to the Java client for collecting unsent messages. When this limit is hit, the producer will block on additional sends for as long as `max.block.ms` before raising an exception. Additionally, to avoid keeping records queued indefinitely, you can set a timeout using `request.timeout.ms`. If this timeout expires before a message can be successfully sent, then it will be removed from the queue and an exception will be thrown. The overall lifetime of a record inside the producer is bounded by `delivery.timeout.ms`.

**Transactions.** Setting `transactional.id` turns the producer into a transactional producer: call `initTransactions()` once, then wrap `send()` calls between `beginTransaction()` and `commitTransaction()` (or `abortTransaction()`). Consumer offsets can be included with `sendOffsetsToTransaction()`. Downstream consumers must set `isolation.level=read_committed` to see only committed records.

### Kafka Internals course — Producer hands-on (developer.confluent.io)

**Producer architecture components.** The Apache Kafka producer consists of several key components working together: the **Serializer** converts records into byte arrays for transmission; the **Partitioner** determines which topic partition receives each record; the **Record Accumulator** buffers records into batches before sending; the **Sender Thread** manages the actual transmission of batches to brokers.

**Batching configuration.** Two critical settings control batch behavior: `batch.size` (default ~16 KB) is the maximum size a batch reaches before flushing to the broker; `linger.ms` (0 in the course, **5 since Kafka 4.0**) is the maximum time the producer waits while accumulating records in a batch. These settings directly impact throughput versus latency tradeoffs. Other settings covered: `acks` (broker acknowledgment requirements), `retries` (attempts to resend failed records), and idempotence (prevents duplicate records).

**Hands-on exercise.** The tutorial runs `kafka-producer-perf-test.sh` (200 records/second at 1000 bytes each) with four configurations and reads producer JMX metrics:

| Configuration | batch-size-avg (bytes) | outgoing-byte-rate | record-queue-time-avg | request-latency-avg |
|---|---|---|---|---|
| `linger.ms=0`, `batch.size=16384` | 1215 | 75594 | 4.2 ms | 43.3 ms |
| `linger.ms=100`, `batch.size=16384` | 16165 | 68867 | 95.5 ms | 53.6 ms |
| `linger.ms=100`, `batch.size=300000` | 23720 | 68721 | 109.1 ms | 63.8 ms |
| `linger.ms=1500`, `batch.size=300000` | 275700 | 68246 | 1406.3 ms | 226.1 ms |

**Key finding.** For this low-volume scenario the producer defaults proved optimal; increasing `linger.ms` and `batch.size` raised `batch-size-avg` dramatically (1215 → 275700 bytes) but the records spent correspondingly longer in the accumulator (`record-queue-time-avg` 4.2 ms → 1406 ms) while the byte rate did not improve, because the workload never generated enough records to fill batches quickly. Larger batching pays off only when the producer is under real load; otherwise it only adds latency.
