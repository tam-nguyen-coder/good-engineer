# Kafka Streams DSL — Stateless, Stateful, Windowing, Suppress

> **Nguồn (official):** https://docs.confluent.io/platform/current/streams/developer-guide/dsl-api.html
> (bản Apache tương ứng: https://kafka.apache.org/documentation/streams/developer-guide/dsl-api.html)
> **Tuần:** 6 — Kafka Streams · **Loại:** Confluent Docs (nội dung trùng Apache Kafka Docs)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất. Phần **Joining** tách riêng ở [streams-joins.md](streams-joins.md).

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Stateless không đổi key → không repartition:** `filter`, `filterNot`, `mapValues`, `flatMapValues`, `peek`, `foreach`, `print`, `merge`, `branch/split`.
- **Stateless đổi key → đánh dấu repartition:** `map`, `flatMap`, `selectKey`, `groupBy`. Repartition **chỉ thực sự xảy ra** khi có phép **stateful** (aggregate/join) phía sau → tự tạo topic `<application.id>-<name>-repartition`. `groupByKey` **không** repartition (trừ khi stream đã bị đánh dấu trước đó).
- `KStream#through()` và `KStream#branch()` đã **bị xoá** (4.0) → dùng `repartition()` và `split()`. `transform/transformValues` bị xoá → dùng `process()/processValues()`.
- **Aggregation** cần 3 thứ: **`Initializer`** (chạy 1 lần/key), **`Aggregator`** (adder), với `KGroupedTable` thêm **subtractor** (xử lý update/xoá). `reduce` không đổi kiểu giá trị; `aggregate` đổi được kiểu. `count` trả `KTable<K, Long>`.
- **`Materialized.as("store-name")`** đặt tên state store (bắt buộc nếu muốn Interactive Query) + `.withKeySerde/.withValueSerde`.
- **4 loại window:** Tumbling `TimeWindows.ofSizeWithNoGrace(size)` (size = advance, không chồng); Hopping `TimeWindows.ofSizeAndGrace(size, grace).advanceBy(advance)` (advance < size → 1 record rơi vào nhiều window); Sliding `SlidingWindows.ofTimeDifferenceAndGrace(diff, grace)` (window theo cặp record, dùng cho join stream-stream & aggregation); Session `SessionWindows.ofInactivityGapAndGrace(gap, grace)` (không cố định kích thước, gộp theo khoảng nghỉ).
- API mới **bắt buộc khai báo grace** (`ofSizeWithNoGrace` / `ofSizeAndGrace`); API cũ `TimeWindows.of(...)` mặc định grace **24 h** đã deprecated/xoá.
- **`suppress(Suppressed.untilWindowCloses(BufferConfig.unbounded()))`** → chỉ emit **1 kết quả cuối** mỗi window sau khi window đóng (window-end + grace). `untilTimeLimit(duration, bufferConfig)` → giới hạn theo thời gian. Không dùng suppress → mỗi record đầu vào có thể sinh 1 update (bị cache gom bớt).
- Kết quả windowed aggregation có key kiểu **`Windowed<K>`** (key + `window().start()/end()`).
- Ghi ra topic: `stream.to("topic", Produced.with(keySerde, valueSerde))`; đọc: `builder.stream("topic", Consumed.with(...))`, `builder.table(...)`, `builder.globalTable(...)`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Stream and table types

- **KStream**: represents a partitioned record stream. Each application instance processes only a subset of input topic partitions. Records are processed individually as events (INSERT semantics).
- **KTable**: interprets a Kafka topic as a changelog stream where records with the same key are treated as UPSERT (non-null values) or DELETE (null values, tombstones). Each instance handles a partition subset. Requires a state store name for Interactive Queries support.
- **GlobalKTable**: each application instance receives data from ALL input topic partitions. Useful for reference data that must be available locally across all instances. Requires explicit state store naming.

```java
StreamsBuilder builder = new StreamsBuilder();
KStream<String, Long> stream = builder.stream("word-counts-input-topic",
    Consumed.with(Serdes.String(), Serdes.Long()));
KTable<String, Long> table = builder.table("word-counts-input-topic",
    Materialized.<String, Long, KeyValueStore<Bytes, byte[]>>as("word-counts-store")
        .withKeySerde(Serdes.String()).withValueSerde(Serdes.Long()));
GlobalKTable<String, Long> global = builder.globalTable("word-counts-input-topic",
    Materialized.<String, Long, KeyValueStore<Bytes, byte[]>>as("word-counts-global-store"));
```

### Stateless transformations

These operations process records without maintaining state.

| Transformation | Type | Behavior |
|---|---|---|
| **Branch / Split** | KStream → BranchedKStream | Routes records to multiple streams based on predicates (`split().branch(pred, Branched.as("x"))`) |
| **Filter** | KStream/KTable → same | Retains records matching a condition |
| **Inverse Filter** (`filterNot`) | KStream/KTable → same | Removes records matching a condition |
| **FlatMap** | KStream → KStream | Produces 0..N output records; allows key/value changes; *marks the stream for re-partitioning* |
| **FlatMapValues** | KStream → KStream | Produces multiple outputs; keeps original key; no re-partitioning |
| **Foreach** | KStream/KTable → void | Terminal operation; executes side effects |
| **GroupByKey** | KStream → KGroupedStream | Groups by existing key; re-partitions **only if** the stream was previously marked |
| **GroupBy** | KStream/KTable → KGroupedStream/KGroupedTable | Groups by a new key; *always causes re-partitioning* |
| **Map** | KStream → KStream | One-to-one transformation; changes key/value types; *marks for re-partitioning* |
| **MapValues** | KStream/KTable → same | Retains key; transforms values only; no re-partitioning |
| **Merge** | (KStream, KStream) → KStream | Combines two streams; preserves relative order within each input |
| **Peek** | KStream → KStream | Non-terminal side effects (logging/metrics); returns unchanged stream |
| **Print** | KStream → void | Terminal; outputs to stdout or file |
| **Repartition** | KStream → KStream | Manually trigger re-partitioning with a specified partition count (`Repartitioned.numberOfPartitions(n)`) |
| **SelectKey** | KStream → KStream | Assigns a new key; *marks for re-partitioning* |
| **ToStream** | KTable → KStream | Converts table changelog to a record stream |
| **ToTable** | KStream → KTable | Converts an event stream to a table |

Re-partitioning is applied lazily: a stream that was marked for re-partitioning is actually re-partitioned (through an internal `<application.id>-<name>-repartition` topic) only when a subsequent stateful operation (aggregation or join) requires correctly partitioned data.

```java
KStream<byte[], String> words = sentences.flatMapValues(v -> Arrays.asList(v.split("\\s+")));
KStream<String, String> rekeyed = words.selectKey((k, v) -> v);           // marked for repartition
KGroupedStream<String, String> grouped = rekeyed.groupByKey();            // repartition topic created here
```

### Stateful transformations — aggregation

Combines records sharing a key into a single result. Aggregating is a generalization of `reduce` and allows the result type to differ from the input type.

```java
KGroupedStream<String, Long> grouped = stream.groupByKey();

// Non-windowed aggregation
KTable<String, Long> agg = grouped.aggregate(
    () -> 0L,                                   // initializer
    (aggKey, newValue, aggValue) -> aggValue + newValue,   // adder
    Materialized.<String, Long, KeyValueStore<Bytes, byte[]>>as("aggregated-stream-store")
        .withValueSerde(Serdes.Long()));

// KGroupedTable needs an adder AND a subtractor
KTable<String, Long> aggTable = groupedTable.aggregate(
    () -> 0L,
    (aggKey, newValue, aggValue) -> aggValue + newValue,   // adder
    (aggKey, oldValue, aggValue) -> aggValue - oldValue,   // subtractor
    Materialized.as("aggregated-table-store"));
```

**Key rules**: the initializer runs once per key (before the first record is processed). The adder is invoked for non-null values; records with `null` keys are ignored. For `KGroupedTable`, when a key is updated the subtractor is called with the old value and the adder with the new value; a tombstone triggers only the subtractor.

**Windowed aggregation**:

```java
KTable<Windowed<String>, Long> windowed = grouped
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)))
    .aggregate(() -> 0L, (k, v, agg) -> agg + v,
        Materialized.<String, Long, WindowStore<Bytes, byte[]>>as("time-windowed-aggregated-stream-store")
            .withValueSerde(Serdes.Long()));

KTable<Windowed<String>, Long> sessionized = grouped
    .windowedBy(SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(5)))
    .aggregate(() -> 0L, (k, v, agg) -> agg + v,
        (aggKey, leftAgg, rightAgg) -> leftAgg + rightAgg,   // session merger
        Materialized.as("sessionized-aggregated-stream-store"));
```

### Count and reduce

- **Count**: tallies records per key; available windowed and non-windowed; result is `KTable<K, Long>`.
- **Reduce**: combines values of the *same* type; requires an adder (and a subtractor for tables). Cannot change the result type, unlike `aggregate`.

```java
KTable<String, Long> counted = grouped.count();
KTable<String, Long> reduced = grouped.reduce((aggValue, newValue) -> aggValue + newValue);
```

### Windowing

Windows let you control how to group records that have the same key for stateful operations such as aggregations or joins into so-called windows.

| Window type | Behavior | Description |
|---|---|---|
| Tumbling time window | Time-based | Fixed-size, non-overlapping, gap-less windows |
| Hopping time window | Time-based | Fixed-size, overlapping windows |
| Sliding time window | Time-based | Fixed-size, overlapping windows that work on differences between record timestamps |
| Session window | Session-based | Dynamically-sized, non-overlapping, data-driven windows |

```java
// Tumbling: size == advance interval
TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5));
TimeWindows.ofSizeAndGrace(Duration.ofMinutes(5), Duration.ofMinutes(1));

// Hopping: advance < size (a record may belong to several windows)
TimeWindows.ofSizeAndGrace(Duration.ofMinutes(5), Duration.ofMinutes(1)).advanceBy(Duration.ofMinutes(1));

// Sliding: window defined by the time difference between two records
SlidingWindows.ofTimeDifferenceAndGrace(Duration.ofMinutes(10), Duration.ofMinutes(30));

// Session: inactivity gap
SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(5));
SessionWindows.ofInactivityGapAndGrace(Duration.ofMinutes(5), Duration.ofMinutes(1));
```

Hopping windows are aligned to the epoch (start at timestamp 0). Tumbling windows are a special case of hopping windows where size equals advance.

**Grace period**: allows late-arriving (out-of-order) records within a time buffer before the window closes. Records arriving after `window end + grace` are dropped (a `dropped-records` metric is incremented). Legacy `TimeWindows.of(size)` used a default grace of 24 hours; the newer `ofSizeWithNoGrace` / `ofSizeAndGrace` factory methods require an explicit choice.

**Window retention**: a windowed store keeps windows for at least `retention` (default = window size + grace); it can be increased with `Materialized.withRetention(...)`. The changelog topic for a window store uses both `compact` and `delete` cleanup policies (retention adds `windowstore.changelog.additional.retention.ms`, default 1 day).

### Suppress operator

Controls downstream emissions from stateful operations. Instead of emitting every intermediate update, buffer results and emit only when a condition is met.

```java
// Emit exactly one final result per window, after window end + grace
windowed.suppress(Suppressed.untilWindowCloses(BufferConfig.unbounded()));

// Rate-limit updates: at most one update per key every 10 s (any KTable)
table.suppress(Suppressed.untilTimeLimit(Duration.ofSeconds(10), BufferConfig.maxBytes(1_000_000L).emitEarlyWhenFull()));
```

`untilWindowCloses` requires a strict buffer config (`unbounded()` or `maxRecords/maxBytes` with `shutDownWhenFull()`) because emitting early would violate the "final result" contract. `untilWindowCloses` works only for windowed aggregations with a defined grace period.

### Writing output

```java
stream.to("output-topic", Produced.with(Serdes.String(), Serdes.Long()));
table.toStream().to("output-topic");
```

Sends transformed data back to Kafka topics for downstream consumption. Records with `null` value written from a `KTable` stream are tombstones.
