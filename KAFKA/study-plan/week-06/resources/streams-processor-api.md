# Kafka Streams — Processor API (PAPI), State Stores, Punctuation

> **Nguồn (official):** https://docs.confluent.io/platform/current/streams/developer-guide/processor-api.html
> (bản Apache tương ứng: https://kafka.apache.org/documentation/streams/developer-guide/processor-api.html)
> **Tuần:** 6 — Kafka Streams · **Loại:** Confluent Docs (nội dung trùng Apache Kafka Docs)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Processor API** = cấp thấp, kiểm soát từng record: interface `Processor<KIn, VIn, KOut, VOut>` với `init(ProcessorContext)`, `process(Record)`, `close()`. DSL được **xây trên** PAPI; DSL dùng PAPI qua `KStream#process()` / `processValues()`.
- **`ProcessorContext`**: `forward(Record)` (đẩy xuống downstream, có thể chọn child name), `schedule(Duration, PunctuationType, Punctuator)`, `commit()` (yêu cầu commit sớm), `getStateStore(name)`, `recordMetadata()` (topic/partition/offset — **không có** trong punctuator), `applicationId/taskId`.
- **Punctuation** — 2 loại: **`STREAM_TIME`** (theo event-time, **chỉ tiến khi có record mới**; 60 record timestamp 1..60 s + schedule 10 s → gọi **6 lần** bất kể tốc độ xử lý; **không** chạy khi stream idle) vs **`WALL_CLOCK_TIME`** (theo đồng hồ hệ thống; xử lý 60 record đó trong 20 s → **2 lần**, trong 5 s → **0 lần**). Trong `TopologyTestDriver` wall-clock phải `advanceWallClockTime`.
- **State store** tạo qua `Stores.keyValueStoreBuilder(Stores.persistentKeyValueStore("name"), keySerde, valueSerde)` (RocksDB trên disk — **mặc định/khuyến nghị**) hoặc `Stores.inMemoryKeyValueStore("name")` (heap, nhanh, mất khi restart nhưng vẫn restore từ changelog). Cả hai **fault-tolerant mặc định** nhờ changelog (`withLoggingEnabled(config)`); `withLoggingDisabled()` → **mất fault tolerance & không có standby**.
- Changelog của **key-value store** = compacted; changelog của **window/session store** = `compact,delete` (key có timestamp → xoá theo retention).
- Nối store vào processor: `topology.addStateStore(storeBuilder, "ProcessorName")` hoặc `ProcessorSupplier#stores()` (`ConnectedStoreProvider`) → store tự gắn. **`ProcessorSupplier#get()` phải trả instance mới mỗi lần** (mỗi task 1 processor riêng) — trả singleton là bug kinh điển.
- Topology thủ công: `new Topology().addSource("Source", "topic").addProcessor("Process", supplier, "Source").addStateStore(builder, "Process").addSink("Sink", "out-topic", "Process")`.
- **Timestamped store** (`Stores.timestampedKeyValueStoreBuilder`) lưu thêm timestamp cập nhật; **Versioned store** (`Stores.persistentVersionedKeyValueStore(name, historyRetention)`) lưu nhiều phiên bản theo thời gian → join stream-table đúng thời điểm; tốn RAM hơn, **không cache, không Interactive Query**.
- `close()` **không** đóng state store (library quản lý) — chỉ huỷ punctuator/tài nguyên riêng; Streams có thể gọi `init()` lại sau `close()`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Processor interface

The Processor API enables developers to define custom stream processors by implementing the `Processor` interface (`org.apache.kafka.streams.processor.api.Processor`). Its key methods:

- **`init(ProcessorContext<KOut, VOut> context)`**: called by Kafka Streams during task construction. Performs initialization, uses the provided `ProcessorContext` to schedule punctuation and to access state stores.
- **`process(Record<KIn, VIn> record)`**: called for each received record to perform processing logic on a per-record basis.
- **`close()`**: cleans up resources. Kafka Streams may reuse Processor objects by calling `init()` again after `close()`. Cancel punctuators (via the `Cancellable` returned by `schedule`) inside `close()` when tasks are migrated.

The interface takes four generic parameters: `KIn`, `VIn`, `KOut`, `VOut` — the input and output key/value types. If your processor doesn't forward records, set the output types to `Void`.

### ProcessorContext

The `ProcessorContext` controls the processing workflow and provides access to:

- **Record metadata**: topic, partition, offset via `recordMetadata()` (an `Optional` — empty when called from a punctuator).
- **Application metadata**: `applicationId()`, `taskId()`, `stateDir()`, `appConfigs()`.
- **`forward(Record<KOut, VOut>)`** / `forward(record, childName)`: sends records downstream to all or a specific child processor.
- **`schedule(Duration interval, PunctuationType type, Punctuator callback)`**: schedules periodic invocation; returns a `Cancellable`.
- **`commit()`**: requests a commit of the current processing progress (honoured at the next opportunity, not synchronous).
- **`getStateStore(String name)`**: accesses a state store connected to this processor.
- Record headers can be read/modified through the `Record#headers()`.

### Punctuation: stream-time vs wall-clock-time

Punctuation enables periodic processing independent of individual records.

**Stream-time (`PunctuationType.STREAM_TIME`)** — triggered purely by data. Stream-time advances only when records with new (larger) timestamps arrive. Example: if you process a stream of 60 records with consecutive timestamps from 1 (first record) to 60 seconds (last record) and schedule a punctuation every 10 seconds, `punctuate()` is called 6 times — regardless of the time required to actually process those records. Stream-time is derived from the `TimestampExtractor`.

**Wall-clock-time (`PunctuationType.WALL_CLOCK_TIME`)** — triggered by actual system time. Processing the same 60 records within 20 seconds yields 2 punctuations; within 5 seconds yields none.

Stream-time doesn't advance during task idling or when awaiting new records, so stream-time punctuation won't trigger without input data. You can schedule multiple punctuators with different types in the same processor.

### State stores

State stores maintain processing state for stateful operations. The `Stores` factory creates store builders:

**Persistent KeyValueStore (RocksDB)** — recommended for most use cases; stores data on local disk; capacity limited by disk space; fault-tolerant by default. Variants: time window, session window, timestamped, timestamped window, versioned.

```java
StoreBuilder<KeyValueStore<String, Long>> countStoreBuilder = Stores.keyValueStoreBuilder(
    Stores.persistentKeyValueStore("persistent-counts"),
    Serdes.String(),
    Serdes.Long());
```

**In-memory KeyValueStore** — stores data in memory; capacity limited by heap; useful where local disk is unavailable or wiped between restarts; also fault-tolerant by default (restored from the changelog).

```java
StoreBuilder<KeyValueStore<String, Long>> countStoreBuilder = Stores.keyValueStoreBuilder(
    Stores.inMemoryKeyValueStore("inmemory-counts"),
    Serdes.String(),
    Serdes.Long());
```

### Fault tolerance and changelog topics

State stores are backed up to compacted changelog topics (`<application.id>-<store-name>-changelog`) for fault tolerance and task migration. Windowed stores use changelog topics with both compaction and deletion enabled, because message keys include window timestamps and old windows can be dropped after retention. Enable or disable logging:

```java
// Disable fault tolerance (no changelog, no standby replicas)
.withLoggingDisabled();

// Enable with custom changelog topic configuration
Map<String, String> changelogConfig = new HashMap<>();
changelogConfig.put("min.insync.replicas", "1");
.withLoggingEnabled(changelogConfig);
```

Disabling changelogs removes fault tolerance and prevents standby replicas. Caching can be toggled per store with `.withCachingEnabled()` / `.withCachingDisabled()`.

### Timestamped state stores

KTables store timestamps by default (`TimestampedKeyValueStore`). Timestamped stores improve semantics for out-of-order data, allow detecting out-of-order joins/aggregations, and provide update timestamps in interactive queries.

### Versioned state stores

Rather than storing a single value per key, versioned stores maintain multiple versions, supporting timestamped retrieval (`get(key, asOfTimestamp)`). Each store has a fixed-duration **history retention** determining how long old versions persist — this also serves as the grace period for out-of-order writes.

```java
StoreBuilder<VersionedKeyValueStore<String, String>> versioned = Stores.versionedKeyValueStoreBuilder(
    Stores.persistentVersionedKeyValueStore("versioned-store", Duration.ofMinutes(30)),
    Serdes.String(), Serdes.String());
```

Versioned stores have higher memory overhead than non-versioned stores and don't support caching or interactive queries. Upgrades from non-versioned to versioned persistent key-value stores are supported (same changelog format).

### Topology: connecting processors and state stores

```java
Topology builder = new Topology();
builder.addSource("Source", "source-topic")
    .addProcessor("Process", () -> new WordCountProcessor(), "Source")
    .addStateStore(countStoreBuilder, "Process")
    .addSink("Sink", "sink-topic", "Process");
```

- **`addSource(name, topics...)`**: a source processor node reading from the given topics (optionally with explicit deserializers / `TimestampExtractor`).
- **`addProcessor(name, ProcessorSupplier, parentNames...)`**: a processor node fed by the named parents.
- **`addStateStore(StoreBuilder, processorNames...)`**: creates the store and connects it to the given processors.
- **`addSink(name, topic, parentNames...)`**: a sink node writing to a topic (optionally with serializers / `StreamPartitioner`).

Alternatively, use `ConnectedStoreProvider` so the store is declared together with the processor:

```java
.addProcessor("Process", new ProcessorSupplier<String, String, String, String>() {
    public Processor<String, String, String, String> get() { return new WordCountProcessor(); }
    public Set<StoreBuilder<?>> stores() { return Collections.singleton(countStoreBuilder); }
}, "Source")
```

**Important**: `ProcessorSupplier#get()` must return a **new instance** on each call — never provide a singleton, because each task gets its own processor instance.

### WordCountProcessor example

```java
public class WordCountProcessor implements Processor<String, String, String, String> {
    private KeyValueStore<String, Integer> kvStore;

    @Override
    public void init(final ProcessorContext<String, String> context) {
        context.schedule(Duration.ofSeconds(1), PunctuationType.STREAM_TIME, timestamp -> {
            try (final KeyValueIterator<String, Integer> iter = kvStore.all()) {
                while (iter.hasNext()) {
                    final KeyValue<String, Integer> entry = iter.next();
                    context.forward(new Record<>(entry.key, entry.value.toString(), timestamp));
                }
            }
        });
        kvStore = context.getStateStore("Counts");
    }

    @Override
    public void process(final Record<String, String> record) {
        final String[] words = record.value().toLowerCase(Locale.getDefault()).split("\\W+");
        for (final String word : words) {
            final Integer oldValue = kvStore.get(word);
            if (oldValue == null) {
                kvStore.put(word, 1);
            } else {
                kvStore.put(word, oldValue + 1);
            }
        }
    }

    @Override
    public void close() {
        // close any resources managed by this processor
        // Note: Do not close any StateStores as these are managed by the library
    }
}
```

### Using the Processor API from the DSL

`KStream#process(ProcessorSupplier, storeNames...)` and `KStream#processValues(FixedKeyProcessorSupplier, ...)` embed a custom processor in a DSL topology (replacing the removed `transform`/`transformValues`). `processValues` guarantees the key is unchanged, so no repartitioning is triggered.
