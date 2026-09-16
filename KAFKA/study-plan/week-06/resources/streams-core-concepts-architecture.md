# Kafka Streams — Core Concepts & Architecture

> **Nguồn (official):** https://docs.confluent.io/platform/current/streams/concepts.html · https://docs.confluent.io/platform/current/streams/architecture.html
> (bản Apache tương ứng: https://kafka.apache.org/documentation/streams/core-concepts · https://kafka.apache.org/documentation/streams/architecture)
> **Tuần:** 6 — Kafka Streams · **Loại:** Confluent Docs (nội dung trùng Apache Kafka Docs)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `Kafka Streams` là **library** (JAR) nhúng vào ứng dụng Java/JVM — **không có cluster riêng**, không chạy trong broker. Scale bằng cách **chạy thêm instance cùng `application.id`** (hoặc tăng `num.stream.threads`).
- **Topology** = đồ thị có hướng không chu trình (DAG) gồm **source processor** (đọc topic), **stream processor** (biến đổi), **sink processor** (ghi topic). Định nghĩa qua **DSL** (`StreamsBuilder`) hoặc **Processor API** (`Topology`).
- **Số task cố định = số partition lớn nhất** trong các input topic của sub-topology. **Song song tối đa = số partition**: topic 5 partition → tối đa 5 instance/thread có việc; instance thứ 6 **idle**.
- **`num.stream.threads`** (mặc định **1**) — mỗi thread chạy ≥1 task độc lập; thêm thread hay thêm instance đều chỉ là "nhân bản topology, xử lý tập partition khác".
- **Time semantics:** event-time (thời điểm xảy ra, gán bởi `TimestampExtractor`, mặc định là record timestamp), processing-time (lúc app xử lý — `WallclockTimestampExtractor`), ingestion-time (broker gắn khi `message.timestamp.type=LogAppendTime`). **Stream-time** = timestamp lớn nhất đã thấy trong task, chỉ tiến khi có record mới.
- **Stream-table duality:** stream là **changelog** của table (replay stream → dựng lại table); table là **snapshot** giá trị mới nhất mỗi key. `KStream` = INSERT (2 record cùng key độc lập); `KTable` = UPSERT (record sau ghi đè), `null` value = **tombstone** xoá; `GlobalKTable` = bản copy **đầy đủ mọi partition** trên **mỗi** instance → join không cần co-partition.
- **State store** cục bộ (RocksDB mặc định hoặc in-memory) + **changelog topic compacted** để phục hồi; **`num.standby.replicas`** (mặc định **0**) tạo bản copy nóng ở instance khác → failover nhanh, tốn 2× storage.
- **Grace period:** record đến sau `window-end + grace` bị **drop**. Trade-off latency vs correctness.
- **Processing guarantee:** `at_least_once` (mặc định) vs `exactly_once_v2` — state update + ghi output + commit offset **atomic trong 1 transaction**. Với EOS, state cục bộ lệch changelog → **xoá store và rebuild từ changelog**.
- **Record cache** (`statestore.cache.max.bytes`, mặc định **10 MB**): read cache + write-back buffer + **giảm số update đẩy xuống downstream** → "count không emit mỗi record". Kết quả cuối **giống nhau** dù cache bật hay tắt.
- **Depth-first processing:** mỗi record đi hết (sub-)topology trước khi record kế tiếp được xử lý → **không có backpressure** vì không buffer giữa các processor; consumer pull-based tự điều tiết.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Fundamental abstractions

**Stream** — "An unbounded, continuously updating sequence of key-value records" representing data that flows continuously without a defined endpoint.

**Stream Processing Application** — Any program using the Kafka Streams library to transform input streams into output streams. These applications run in separate JVM instances outside Kafka brokers, not within them.

**Processor Topology** — A directed acyclic graph of stream processors (nodes) connected by streams (edges), defining the computational logic for data transformation. Two special processor types exist:

- **Source Processor**: consumes from Kafka topics without upstream processors.
- **Sink Processor**: sends records to Kafka topics without downstream processors.

Developers can define topologies using either the low-level Processor API or the Kafka Streams DSL.

### Time semantics

Kafka Streams supports multiple notions of time:

- **Event-time**: when an event originally occurred at its source.
- **Processing-time**: when the stream processing application actually consumes the record.
- **Ingestion-time**: when the Kafka broker appends the record to a topic partition.
- **Stream-time**: the maximum timestamp observed across all processed records on a per-task basis.

Applications assign timestamps via `TimestampExtractor` implementations, enabling developers to enforce different time semantics based on business needs. The default extractor uses the built-in record timestamp (which is either producer/event time or broker/ingestion time depending on the topic's `message.timestamp.type`).

### Stream-table duality

A fundamental concept: streams and tables are two views of the same data.

- **Streams as tables**: a stream represents a changelog of a table; replaying it reconstructs the original table.
- **Tables as streams**: a table is a point-in-time snapshot of the latest value per key; iterating over entries produces a stream.

### KStream, KTable, and GlobalKTable

- **KStream**: represents a record stream where each data record is an INSERT. Two records with identical keys are treated independently.
- **KTable**: represents a changelog stream where records are UPSERTs. The second record with the same key overwrites the first. A record with a `null` value is a tombstone (DELETE).
- **GlobalKTable**: like KTable but populated with data from *all* topic partitions rather than one subset per application instance. Useful for broadcasting information and enabling star joins without co-partitioning requirements.

### Stateful operations

- **Aggregations**: combine multiple input records into a single output record (counts, sums…). Input can be KStream or KTable; output is always KTable.
- **Joins**: merge two input streams/tables based on record keys. Types: stream-stream, stream-table, table-table.
- **Windowing**: groups records with the same key into time-based windows — Tumbling (fixed, non-overlapping), Hopping (fixed, overlapping), Sliding (event-time based, per record pair), Session (dynamic, based on inactivity gaps).
- **Grace period**: the time a window allows for out-of-order arrival after the window ends. Records arriving after `window-end-time + grace-period` are discarded.

### Processing guarantees

- **At-least-once** (default): records may be redelivered but are never lost if failures occur.
- **Exactly-once** (`processing.guarantee="exactly_once_v2"`): each record is processed exactly once. State persistence, data production, and offset commits occur atomically within a single transaction.

### Out-of-order handling

Records may arrive out-of-timestamp order due to non-monotonic timestamps within a partition or multi-partition task processing with differing fetch timing. For stateless operations, order is irrelevant. For stateful operations like aggregations, grace periods manage the lateness trade-off between latency, correctness, and cost.

### Interactive queries

Allow treating the stream processing layer as an embedded database, querying application state directly without materializing to external systems.

---

### Parallelism model — stream partitions and tasks

Kafka Streams partitions data for processing through **stream partitions** and **stream tasks**: each stream partition maps to a Kafka topic partition; data records map to Kafka messages; record keys determine partitioning in both systems.

"Kafka Streams creates a fixed number of stream tasks based on the input stream partitions for the application, with each task being assigned a list of partitions from the input streams." **Maximum parallelism** is bounded by the maximum number of partitions in input topics. For example, "if your input topic has 5 partitions, then you can run up to 5 application instances."

### Threading model

Configure the number of **threads** per application instance through `num.stream.threads`. Each thread executes one or more stream tasks independently with their processor topologies. "Starting more stream threads or more instances of the application merely amounts to replicating the topology and having it process a different subset of Kafka partitions."

### Local state stores

Every stream task may embed one or more local state stores for stateful operations like `count()` or `aggregate()`. These can be RocksDB databases, in-memory hash maps, or other data structures. An application's entire state is "spread across the local state stores of the application's running instances" across multiple machines.

### Changelog topics and fault tolerance

For each state store, Kafka Streams maintains a replicated changelog Kafka topic tracking state updates. "Log compaction is enabled on the changelog topics so that old data can be purged safely to prevent the topics from growing indefinitely." If a task fails and restarts elsewhere, "Kafka Streams guarantees to restore their associated state stores to the content before the failure by replaying the corresponding changelog topics."

### Standby replicas

Configure `num.standby.replicas` to create fully replicated copies of local state. "When a task migration happens, Kafka Streams assigns a task to an application instance where such a standby replica already exists, to minimize the task (re)initialization cost." Starting in version 2.6, "Kafka Streams guarantees that a task is assigned to an instance with a fully caught-up local copy of the state exists, if such an instance exists." Rack awareness can distribute standby tasks across different racks using `rack.aware.assignment.tags`.

### Local state consistency

- **EOS**: "if the local state diverges from the changelog topic, Kafka Streams deletes the state store and rebuilds it from the changelog." A client-local checkpoint file stores metadata and is present only when state is consistent with the changelog.
- **ALOS**: "Kafka Streams may have 'dirty' writes, and no state rebuild is attempted, because this is what the at-least-once processing guarantee provides." Before resuming, "Kafka Streams reads the changelog from the checkpointed offsets to its end."

### Memory management — record caches

"This memory is used for internal caching and compacting of records before they are written to state stores, or forwarded downstream to other nodes." The cache serves three functions: (1) a read cache to speed up reading from a state store; (2) a write-back buffer batching records and reducing state store requests; (3) reducing records forwarded to downstream processors. Smaller caches yield larger downstream update rates; larger caches reduce network IO to Kafka and disk IO to RocksDB. "The final computation results are identical regardless of the cache size (including a disabled cache), which means it is safe to enable or disable the cache."

### Processing strategy — depth-first

"Each record consumed from Kafka goes through the whole processor (sub-)topology for processing and for (possibly) being written back to Kafka before the next record is processed." For each task, "only one message is processed at a time."

### Flow control and backpressure

Kafka Streams regulates stream progress "by the timestamps of data records by attempting to synchronize all source streams in terms of time." Kafka Streams does not use a backpressure mechanism: with depth-first processing "no records are being buffered in-memory between two connected stream processors." The pull-based Kafka consumer model allows "downstream processors to control the pace at which incoming data records are being read."
