# KIP-480 Sticky Partitioner & KIP-794 Strictly Uniform Sticky Partitioner (+ Confluent blog)

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-480%3A+Sticky+Partitioner · https://cwiki.apache.org/confluence/display/KAFKA/KIP-794%3A+Strictly+Uniform+Sticky+Partitioner · https://www.confluent.io/blog/apache-kafka-producer-improvements-sticky-partitioner/
> **Tuần:** 3 — Producer chuyên sâu + Transactions/EOS · **Loại:** KIP (+ Confluent blog)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.
> ⚠️ Hai trang cwiki KIP-480/KIP-794 **không crawl được** tại thời điểm viết (timeout) — phần KIP được **tổng hợp từ docs** (KIP text, `producer_config.html` 4.3, Javadoc `Partitioner`); phần blog Confluent crawl được.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Trước 2.4**: record **không key** đi **round-robin** từng record qua các partition → batch nhỏ, nhiều request, latency cao. Record **có key** → `murmur2(key) mod N` (không đổi qua các KIP).
- **KIP-480 (Kafka 2.4) — sticky partitioner**: record không key **dính 1 partition** cho tới khi batch đó **đầy (`batch.size`) hoặc hết `linger.ms`**, rồi **chọn ngẫu nhiên** partition khác. Thêm method `Partitioner.onNewBatch()`; class `UniformStickyPartitioner` (sticky kể cả có key).
- **Kết quả Confluent**: 3 producer × 10.000 msg/s, 16 partition → **p99 latency giảm ~½**; với `linger.ms=1000` p99 của round-robin **gấp 5 lần**; càng nhiều partition (16/64/128) lợi càng rõ; **CPU giảm**; keyed message không bị ảnh hưởng.
- **Vấn đề KIP-480**: switch partition theo "batch tạo mới" → khi `linger.ms=0` hoặc broker chậm, partition trên broker chậm nhận **nhiều record hơn** (batch ở đó chờ lâu → nhồi thêm) → phân bố **không đều**.
- **KIP-794 (Kafka 3.3) — strictly uniform sticky**: tích hợp thẳng vào `KafkaProducer` (không qua `Partitioner` plugin), switch partition sau khi đã gửi **≥ `batch.size` byte** vào partition đó (đếm byte, không đếm batch) → đều theo byte. Thêm **adaptive partitioning**: ưu tiên partition trên broker **nhanh** (queue ngắn) — `partitioner.adaptive.partitioning.enable` **true**; `partitioner.availability.timeout.ms` **0** (tắt; >0 = coi partition "không sẵn sàng" nếu broker không xử lý produce trong X ms).
- **`partitioner.ignore.keys`** (**false**): true → bỏ hash key, dùng sticky kể cả có key → **mất ordering theo key**.
- **Deprecate**: `DefaultPartitioner`, `UniformStickyPartitioner`, `Partitioner.onNewBatch()`. `partitioner.class` mặc định **null** = logic built-in mới. `RoundRobinPartitioner` vẫn còn (bỏ key, xoay vòng; có known issue phân bố lệch khi tạo batch mới).
- **Bẫy đề**: "vài ms nhiều record không key vào cùng 1 partition" = sticky đúng thiết kế, không phải bug; tổng thể vẫn đều.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### KIP-480: Sticky Partitioner (tổng hợp từ docs)

**Status:** Adopted, released in **Apache Kafka 2.4.0**.

**Motivation.** Currently, in the case where no partition and no key is specified, the default partitioner partitions records in a round-robin fashion. That means that each record in a series of consecutive records will be sent to a different partition until all the partitions are covered, and then the producer starts over again. While this spreads records out evenly among the partitions, it also results in more batches that are smaller in size. Smaller batches lead to more requests and queuing, as well as higher latency. A batch is sent when it is full (`batch.size`) or when `linger.ms` expires; with round-robin, records that arrive together are split across partitions and none of the per-partition batches fill up quickly.

**Proposed Changes.** The sticky partitioner changes the behavior for records with a null key only: it "sticks" to a single partition for all such records until the batch for that partition is completed (full or sent because of `linger.ms`), then picks a new partition at random and sticks to it. This aims to produce batches of `batch.size` even under moderate load. The partitioner still uses the key hash (murmur2) for keyed records, so keyed behaviour is unchanged.

**Public Interfaces.** A new default method is added to the `Partitioner` interface:

```java
/**
 * Notifies the partitioner a new batch is about to be created. When using the sticky partitioner,
 * this method can change the chosen sticky partition for the new batch.
 */
default void onNewBatch(String topic, Cluster cluster, int prevPartition) {}
```

`DefaultPartitioner` implements the sticky behaviour for null keys via `onNewBatch`. A new `UniformStickyPartitioner` is added which applies sticky partitioning to **all** records, ignoring keys (useful when ordering by key is not required and even batching is desired).

**Compatibility.** No config changes are needed; behaviour for null-key records changes from round-robin per record to sticky per batch. Overall distribution remains uniform over time because the sticky partition is chosen at random for each new batch.

### Confluent blog — "Apache Kafka Producer Improvements with the Sticky Partitioner" (crawled)

**Background: the default partitioner problem.** Before Apache Kafka 2.4, the default partitioner used different strategies based on message keys. For records with keys, it would hash the key to determine the partition. However, for null-keyed records, it would "cycle through the topic's partitions and send a record to each one." This round-robin approach created inefficient batching patterns.

**The core issue.** Records destined for the same partition can be combined into larger batches, reducing overhead per message. When null-keyed records were spread across multiple partitions via round-robin, they couldn't consolidate into larger batches, resulting in smaller batches with higher effective cost-per-record and increased latency.

**How the sticky partitioner works.** Instead of round-robin distribution, it "pick[s] a single partition to send all non-keyed records. Once the batch at that partition is filled or otherwise completed, the sticky partitioner randomly chooses and 'sticks' to a new partition." To support this, Kafka 2.4 introduced "a new method called `onNewBatch` to the partitioner interface for use right before a new batch is created." The `DefaultPartitioner` implements this feature.

**Performance results.**
- High-partition scenarios: with 3 producers sending 10,000 messages/second to 16 partitions, sticky partitioning reduced **p99 latency to approximately half** that of default partitioning.
- Scaling benefits: "The decrease in latency became more apparent as partitions increased" — comparing 16, 64, and 128 partitions showed default strategy latency increasing "at a much faster rate".
- With `linger.ms=1000`: "The p99 latency of the default partitioning strategy was **five times larger**."
- CPU: "the sticky partitioner decreased CPU usage in many cases," with "a noticeable drop" in multi-producer scenarios.

**Behavior with mixed or keyed messages.** Testing revealed no significant downside for keyed messages. With "a mixture of keyless and keyed messages," performance remained comparable. For pure keyed scenarios, "since keyed values ignore the sticky partitioner, the benefit is not very significant" but latency remained unchanged.

### KIP-794: Strictly Uniform Sticky Partitioner (tổng hợp từ docs)

**Status:** Adopted, released in **Apache Kafka 3.3.0**.

**Motivation.** The KIP-480 sticky partitioner switches partition when a *new batch is created*. This has two problems: (1) with `linger.ms=0` (the pre-4.0 default) a batch is created for almost every record when the producer is not under heavy load, so "stickiness" barely materialises and switching becomes nearly per-record; (2) when one broker is slow, the batch for a partition on that broker stays open longer, so more records are appended to it before the switch — the slow partition receives **more** data than fast ones, the opposite of what you want. The distribution is therefore not uniform, and can amplify broker slowness.

**Proposed changes.**
- Move the default partitioning logic **into `KafkaProducer` / `RecordAccumulator`** instead of a pluggable `Partitioner`, so the producer can use accumulator state (bytes produced, queue sizes) to decide when to switch.
- **Uniform sticky**: switch to a new partition once at least **`batch.size` bytes** have been produced to the current sticky partition, regardless of how many batches that took. This gives strictly uniform distribution by bytes over time.
- **Adaptive partitioning** (`partitioner.adaptive.partitioning.enable=true`): weight the choice of the next sticky partition by the length of each partition's send queue in the accumulator, so partitions hosted on faster brokers receive proportionally more records. `partitioner.availability.timeout.ms` (default 0 = disabled): if a broker has not accepted produce requests for a partition for this long, the partition is treated as unavailable and skipped.
- **`partitioner.ignore.keys`** (default `false`): when `true`, the built-in logic does not hash keys and uses uniform sticky partitioning for all records (replacement for the deprecated `UniformStickyPartitioner`).

**Public interfaces.**
- `partitioner.class` default changes to **`null`** (built-in logic). Setting it to a custom class disables all built-in logic and the three new configs have no effect.
- `DefaultPartitioner` and `UniformStickyPartitioner` are **deprecated**; `Partitioner.onNewBatch()` is deprecated.
- New producer configs: `partitioner.adaptive.partitioning.enable` (boolean, true), `partitioner.availability.timeout.ms` (long, 0), `partitioner.ignore.keys` (boolean, false).

**Compatibility.** Keyed records are partitioned exactly as before (murmur2 hash mod partition count), so key-to-partition mapping does not change. Applications that relied on `onNewBatch` in a custom partitioner should migrate their logic into `partition()`.

### Kafka 4.3 `producer_config.html` — `partitioner.class` description (crawled)

If not set, the default partitioning logic is used. This strategy sends records to a partition until at least `batch.size` bytes is produced to the partition. It works with the strategy: 1) If no partition is specified but a key is present, choose a partition based on a hash of the key. 2) If no partition or key is present, choose the sticky partition that changes when at least `batch.size` bytes are produced to the partition. `org.apache.kafka.clients.producer.RoundRobinPartitioner`: each record in a series of consecutive records is sent to a different partition, regardless of whether the 'key' is provided or not, until partitions run out and the process starts over again. Note: there's a known issue that will cause uneven distribution when a new batch is created.
