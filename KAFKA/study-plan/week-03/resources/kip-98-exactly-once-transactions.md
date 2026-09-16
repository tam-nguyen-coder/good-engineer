# KIP-98 — Exactly Once Delivery and Transactional Messaging (+ Confluent blog "Transactions in Apache Kafka", KIP-890 transaction protocol v2)

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging · https://www.confluent.io/blog/transactions-apache-kafka/ · https://kafka.apache.org/43/operations/transaction-protocol/
> **Tuần:** 3 — Producer chuyên sâu + Transactions/EOS · **Loại:** KIP (+ Confluent blog, Apache Kafka Docs)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.
> ⚠️ Trang cwiki KIP-98 **không crawl được** tại thời điểm viết (timeout) — phần KIP được **tổng hợp từ docs** (KIP-98 design doc, Javadoc `KafkaProducer`, broker configs); phần blog Confluent và trang transaction-protocol crawl được.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **3 vấn đề KIP-98 giải quyết**: (1) producer retry tạo **duplicate**; (2) app crash sau khi ghi output nhưng **trước khi commit offset** → xử lý lại; (3) **zombie instance** — instance cũ treo rồi sống lại, ghi trùng với instance mới.
- **Idempotent producer**: broker cấp **PID (producer ID)** khi `InitProducerId`; mỗi batch mang **sequence number** tăng dần theo (PID, partition). Broker giữ trạng thái **5 batch gần nhất** → seq trùng → bỏ (dedup), seq nhảy → `OutOfOrderSequenceException`. Chống duplicate **1 partition, 1 session**.
- **Transactional producer**: `transactional.id` (unique, **ổn định qua restart**) → coordinator cấp **PID + epoch**; mỗi `initTransactions()` **bump epoch** → request mang epoch cũ bị `ProducerFencedException` (**zombie fencing**).
- **Transaction coordinator** = module trên mỗi broker; `hash(transactional.id) mod 50` → partition của topic nội bộ **`__transaction_state`** (`transaction.state.log.num.partitions` **50**, `transaction.state.log.replication.factor` **3**, `transaction.state.log.min.isr` **2**) → leader partition đó là coordinator. Log chỉ chứa **trạng thái** (Empty/Ongoing/PrepareCommit/PrepareAbort/CompleteCommit/CompleteAbort), không chứa data.
- **Luồng**: FindCoordinator → InitProducerId → AddPartitionsToTxn → Produce → AddOffsetsToTxn + TxnOffsetCommit → EndTxn → coordinator ghi **PrepareCommit** → **WriteTxnMarkers** (control record COMMIT/ABORT vào từng partition + `__consumer_offsets`) → **CompleteCommit** (2-phase commit).
- **Consumer `read_committed`**: đọc tới **LSO (last stable offset)** = offset đầu của transaction **đang mở** sớm nhất; record của transaction **abort** bị lọc phía client nhờ marker + danh sách aborted txn broker gửi kèm. `read_uncommitted` (mặc định) đọc tới HW.
- **Timeout**: producer `transaction.timeout.ms` **60000** ≤ broker `transaction.max.timeout.ms` **900000** (15 phút), vượt → `InvalidTxnTimeoutException`; `transactional.id.expiration.ms` **604800000** (7 ngày); `transaction.abort.timed.out.transaction.cleanup.interval.ms` **10000**.
- **Chi phí** (Confluent): 1 KB record, commit mỗi **100 ms** → throughput giảm ~**3%**; consumer `read_committed` **không** giảm throughput (không buffer, giữ zero-copy).
- **KIP-890 (Kafka 4.0, transaction version 2)**: bump epoch **mỗi transaction** (không chỉ mỗi `initTransactions()`) → chặn "hanging transaction"; feature flag `transaction.version=2`; client ≥ 4.0 tự dùng khi bắt đầu transaction kế tiếp; `AddPartitionsToTxn` được gộp phía server.
- **Chọn `transactional.id`**: theo **input partition/shard** (Kafka Streams làm vậy) để mapping input ↔ id ổn định; **UUID random mỗi lần start = mất fencing**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### KIP-98 — Motivation (tổng hợp từ design doc)

This document outlines a proposal for strengthening the message delivery semantics of Kafka. It builds on significant work done over the years, most notably on idempotence and transactions.

Kafka currently (pre-0.11) provides at-least-once semantics: if a producer fails to receive an acknowledgement, it must retry, and the retried write may be a duplicate. In stream-processing applications the "consume-transform-produce" loop compounds the problem: the application may crash after producing its output but before committing its input offset, causing reprocessing; and a "zombie" instance — one that the group thinks is dead but is still running — may keep producing. The KIP proposes two related features:

1. **An idempotent producer**: exactly-once, in-order delivery per partition within a producer session, with no API changes.
2. **Transactions**: atomic writes across multiple partitions (including the `__consumer_offsets` topic), with fencing of zombie producers.

### Summary of guarantees

- **Idempotent producer guarantees:** when `enable.idempotence=true`, the producer is assigned a **producer ID (PID)** and attaches a monotonically increasing **sequence number** per topic-partition to every record batch. The broker keeps, for each (PID, partition), the sequence and offset of the last **5** batches, and (a) rejects a batch whose sequence it has already seen as a duplicate (returning the original offset), (b) rejects a batch whose sequence is not the expected next one with `OUT_OF_ORDER_SEQUENCE_NUMBER`. Because at most 5 requests may be in flight, the broker can reorder retried batches and ordering is preserved. This requires `acks=all`, `retries > 0`, `max.in.flight.requests.per.connection ≤ 5`.
- **Transactional guarantees:** with a `transactional.id`, the application can produce to multiple topic-partitions and commit consumer offsets **atomically**: either all writes become visible to `read_committed` consumers or none do. Transactions also provide **zombie fencing** across producer sessions.

### Key concepts

- **TransactionalId** (`transactional.id`): user-provided, uniquely identifies a logical producer across restarts. Kafka guarantees that only one producer with a given TransactionalId can be active at a time.
- **Producer epoch:** incremented by the coordinator every time `InitProducerId` is called for a TransactionalId. Any request carrying an older epoch is rejected with `ProducerFencedException`, which fences the old ("zombie") producer.
- **Transaction coordinator:** a module running in every broker. Each TransactionalId is mapped (by hash) to a partition of the internal **transaction log** topic `__transaction_state`; the leader of that partition is the coordinator for that TransactionalId. The transaction log is compacted and stores only the **state** of each transaction (Empty, Ongoing, PrepareCommit, PrepareAbort, CompleteCommit, CompleteAbort, Dead), the set of partitions in the transaction, the PID, epoch, and timeout — never the messages themselves.
- **Control messages / transaction markers:** special records (`COMMIT` / `ABORT`) written by the coordinator into every partition that participated in a transaction. They are never returned to applications; consumers use them to decide the fate of preceding transactional records.
- **Last Stable Offset (LSO):** for each partition, the offset of the first record of the earliest transaction that is still open (or the high watermark if none). A `read_committed` consumer never fetches beyond the LSO.
- **Isolation level:** consumer config `isolation.level`, `read_uncommitted` (default) or `read_committed`. In `read_committed` the broker also returns the list of aborted transactions overlapping the fetch so the client can filter out their records.

### Data flow

1. **FindCoordinator** — the producer locates the transaction coordinator for its `transactional.id`.
2. **InitProducerId** — the coordinator returns a PID and bumps the epoch; it first completes (commits or aborts) any transaction left open by a previous incarnation of the same `transactional.id`. Requested `transaction.timeout.ms` is validated against broker `transaction.max.timeout.ms` (`INVALID_TRANSACTION_TIMEOUT` if larger).
3. **beginTransaction()** — client-side only; the transaction starts on the coordinator when the first partition is added.
4. **AddPartitionsToTxn** — the first time the producer sends to a new partition inside the transaction, it registers that partition with the coordinator (state → Ongoing). Under KIP-890 (transaction v2) the broker receiving the produce request registers the partition with the coordinator itself.
5. **Produce** — regular produce requests carrying PID, epoch, and sequence numbers; records are appended to the partition logs immediately (they are simply not yet visible to `read_committed` consumers).
6. **AddOffsetsToTxn + TxnOffsetCommit** — `sendOffsetsToTransaction()` registers the consumer group's `__consumer_offsets` partition with the coordinator, then writes the offsets to the group coordinator as transactional records.
7. **EndTxn (commit or abort)** — the coordinator writes **PrepareCommit / PrepareAbort** to the transaction log (phase 1), then sends **WriteTxnMarkers** to the leader of every participating partition, which append a COMMIT or ABORT control record (phase 2), and finally writes **CompleteCommit / CompleteAbort** to the transaction log.
8. If the producer does not end the transaction within `transaction.timeout.ms`, the coordinator proactively **aborts** it and bumps the epoch.

### Producer API (from KIP-98 / Javadoc)

```java
producer.initTransactions();                       // once per producer instance
consumer.subscribe(topics);                        // consumer: isolation.level=read_committed, enable.auto.commit=false
while (true) {
    ConsumerRecords records = consumer.poll(Duration.ofMillis(100));
    producer.beginTransaction();
    for (ConsumerRecord r : records) {
        producer.send(new ProducerRecord<>(outputTopic, transform(r)));
    }
    producer.sendOffsetsToTransaction(currentOffsets(records), consumer.groupMetadata());
    producer.commitTransaction();                  // or producer.abortTransaction() on error
}
```

Exception handling: `ProducerFencedException`, `OutOfOrderSequenceException`, `AuthorizationException` are **fatal** — close the producer. Any other `KafkaException` — call `abortTransaction()` and retry the batch.

### Broker configurations introduced

| Config | Default | Meaning |
|---|---|---|
| `transaction.state.log.num.partitions` | 50 | Partitions of `__transaction_state` |
| `transaction.state.log.replication.factor` | 3 | RF of the transaction log |
| `transaction.state.log.min.isr` | 2 | `min.insync.replicas` for the transaction log |
| `transaction.max.timeout.ms` | 900000 (15 min) | Maximum `transaction.timeout.ms` a producer may request |
| `transactional.id.expiration.ms` | 604800000 (7 days) | Idle time before a TransactionalId's metadata is expired |
| `transaction.abort.timed.out.transaction.cleanup.interval.ms` | 10000 | How often the coordinator scans for timed-out transactions |
| `transaction.remove.expired.transaction.cleanup.interval.ms` | 3600000 | How often expired TransactionalIds are removed |

### Confluent blog — "Transactions in Apache Kafka" (crawled)

**Why transactions are needed.** Transactions address critical failures in read-process-write patterns. Without them, applications risk: (1) duplicate writes — producer retries can create multiple copies of output message B; (2) reprocessing — if a stream processor crashes after writing B but before marking input A as consumed, A gets reprocessed upon recovery; (3) zombie instances — multiple processor instances may simultaneously process the same input topics after failures, generating duplicates. Transactions solve problems 2 and 3 by enabling atomic read-process-write cycles and "zombie fencing"; the idempotent producer solves problem 1.

**Transactional semantics.** *Atomic multi-partition writes:* all messages in a transaction succeed together or none at all. Since offset commits are themselves Kafka writes, committing an offset and writing output messages can happen atomically within a single transaction. *Zombie fencing:* each transactional producer receives a unique `transactional.id`. Upon initialization, the broker increments an epoch associated with this ID, immediately fencing off any producers with older epochs. *Read committed:* consumers in `read_committed` mode only receive committed transactional messages, filtering out aborted transactions and withholding uncommitted ones.

**How transactions work.** The architecture introduces a **transaction coordinator** (module on each broker managing transactional state), a **transaction log** (internal Kafka topic storing transaction metadata, not messages), and **control markers** written to partitions indicating commit/abort status. Data flow: (A) producer–coordinator registration, (B) state persistence to the transaction log, (C) producer writes to target partitions, (D) coordinator writes commit markers after a two-phase commit.

**Performance.** "For a producer producing 1KB records at maximum throughput, committing messages every 100ms results in only a 3% degradation in throughput." Transactional consumers show no throughput degradation in `read_committed` mode since they avoid buffering and preserve zero-copy semantics. The overhead of a transaction is independent of the number of messages it contains, so longer transactions amortise better at the cost of end-to-end latency.

**Choosing `transactional.id`.** The identifier must be unique and stable across restarts. Critically, the input topic-partition mapping must remain consistent for a given ID — otherwise zombie fencing fails and messages can leak through. Kafka Streams uses a static encoding (application id + task id) to maintain this invariant.

### Kafka 4.3 docs — Transaction Protocol (KIP-890, crawled)

Apache Kafka 4.0 introduced Transactions Server Side Defense (KIP-890), strengthening the transactional protocol. The enhancement ensures "every transaction includes the intended messages and duplicates are not written as part of the next transaction" by bumping the producer epoch on each transaction. The protocol activates automatically in Kafka 4.0+ clusters and is managed through the `transaction.version` feature flag, configurable at cluster creation via the storage tool or dynamically with the features tool. Set `transaction.version=2` to activate the new protocol on brokers. Producer clients version 4.0 and above automatically adopt the enhanced protocol upon connection or reconnection without restarts; upgrades occur at transaction boundaries — "a producer will not upgrade mid-transaction, but on the start of the next transaction after it becomes aware of the server-side upgrade." Downgrades work the same way. The new protocol consolidates partition additions into a single server-side call rather than separate client and server calls. The hardcoded retry backoff from KAFKA-5477 no longer applies; servers now retry adding partitions when encountering `CONCURRENT_TRANSACTIONS` before returning errors to clients, controlled by `add.partitions.to.txn.retry.backoff.ms` and `add.partitions.to.txn.retry.backoff.max.ms`.
