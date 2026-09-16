# Kafka Streams — Testing (`TopologyTestDriver`, `MockProcessorContext`)

> **Nguồn (official):** https://docs.confluent.io/platform/current/streams/developer-guide/test-streams.html
> (bản Apache tương ứng: https://kafka.apache.org/documentation/streams/developer-guide/testing.html)
> **Tuần:** 6 — Kafka Streams · **Loại:** Confluent Docs (nội dung trùng Apache Kafka Docs)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Artifact test: **`org.apache.kafka:kafka-streams-test-utils`** (scope test). Cùng version với `kafka-streams`.
- **`TopologyTestDriver`** = thay thế `KafkaStreams` trong test: **không cần broker/ZooKeeper/Docker**, xử lý **đồng bộ** (pipe input → đọc output ngay), chạy cực nhanh → dùng cho **unit test topology** (DSL hoặc Processor API). Không test được rebalance, nhiều instance, hay hành vi mạng → những thứ đó cần **integration test** (Testcontainers/EmbeddedKafka — Tuần 7).
- `testDriver.createInputTopic(name, keySerializer, valueSerializer)` → `TestInputTopic#pipeInput(key, value[, timestamp])`, `pipeKeyValueList`, `advanceTime`.
- `testDriver.createOutputTopic(name, keyDeserializer, valueDeserializer)` → `TestOutputTopic#readKeyValue()`, `readValue()`, `readRecord()` (kèm timestamp/headers), `readKeyValuesToList()`, `readKeyValuesToMap()` (giá trị cuối mỗi key), `isEmpty()`, `getQueueSize()`.
- **Thời gian:** punctuator **event-time (STREAM_TIME)** tự chạy khi record có timestamp mới đi qua; **wall-clock** phải gọi **`testDriver.advanceWallClockTime(Duration)`**. Windowed aggregation test bằng cách pipe record với **timestamp tường minh** (hoặc `TestInputTopic` có `startTimestamp` + `autoAdvance`).
- Truy cập state store để seed/kiểm tra: `testDriver.getKeyValueStore("store-name")`, `getWindowStore`, `getSessionStore`, `getTimestampedKeyValueStore`.
- **Luôn `testDriver.close()`** (hoặc try-with-resources) để giải phóng RocksDB/thư mục state — thường đặt `state.dir` = temp dir trong test.
- **`MockProcessorContext`** để unit test **1 `Processor`** riêng lẻ: bắt `forwarded()`, `committed()`, đăng ký in-memory store (`withLoggingDisabled()`), lấy punctuator đã schedule qua `scheduledPunctuators()` và gọi `punctuate(ts)` **thủ công** (mock **không** tự chạy punctuator).
- Cache: TopologyTestDriver mặc định flush cache sau mỗi record nên output của aggregation thấy **từng update** — khác production (cache 10 MB gom). Kết quả cuối vẫn đúng.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Overview

Kafka Streams provides two primary testing tools: `TopologyTestDriver` for tests that exercise an entire topology without a running Kafka cluster, and `MockProcessorContext` for unit-testing custom `Processor` implementations.

### Adding test dependencies

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-streams-test-utils</artifactId>
    <version>4.3.1</version>
    <scope>test</scope>
</dependency>
```

```kotlin
// Gradle Kotlin DSL
testImplementation("org.apache.kafka:kafka-streams-test-utils:4.3.1")
```

### Testing a Streams application with TopologyTestDriver

The `TopologyTestDriver` serves as a drop-in replacement for the `KafkaStreams` class. It requires "no external system dependencies, and it also processes input synchronously, so you can verify the results immediately after providing input."

```java
// Processor API
Topology topology = new Topology();
topology.addSource("sourceProcessor", "input-topic");
topology.addProcessor("processor", ..., "sourceProcessor");
topology.addSink("sinkProcessor", "output-topic", "processor");

// or DSL
StreamsBuilder builder = new StreamsBuilder();
builder.stream("input-topic").filter(...).to("output-topic");
Topology topology = builder.build();

// setup test driver
Properties props = new Properties();
props.setProperty(StreamsConfig.APPLICATION_ID_CONFIG, "test");
props.setProperty(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:1234");   // not used, but required
TopologyTestDriver testDriver = new TopologyTestDriver(topology, props);
```

### Input and output topics

Create test input topics and pipe records through them:

```java
TestInputTopic<String, Integer> inputTopic = testDriver.createInputTopic(
    "input-topic",
    new StringSerializer(),
    new IntegerSerializer());
inputTopic.pipeInput("key", 42);                                  // uses auto-advancing/default timestamp
inputTopic.pipeInput("key", 43, Instant.parse("2026-01-01T00:00:00Z"));   // explicit event time
inputTopic.pipeKeyValueList(List.of(KeyValue.pair("a", 1), KeyValue.pair("b", 2)));
```

Create output topics to verify results:

```java
TestOutputTopic<String, Long> outputTopic = testDriver.createOutputTopic(
    "result-topic",
    new StringDeserializer(),
    new LongDeserializer());

assertThat(outputTopic.readKeyValue(), equalTo(new KeyValue<>("a", 21L)));
assertThat(outputTopic.isEmpty(), is(true));   // no further output

// read all at once
List<KeyValue<String, Long>> all = outputTopic.readKeyValuesToList();
Map<String, Long> latest = outputTopic.readKeyValuesToMap();    // last value per key
TestRecord<String, Long> rec = outputTopic.readRecord();          // includes timestamp & headers
```

`TestInputTopic` and `TestOutputTopic` can also be created with `Serde` objects (`createInputTopic(topic, keySerde.serializer(), valueSerde.serializer())`). Reading from an empty output topic throws `NoSuchElementException` — check `isEmpty()` first.

### Time control

The `TopologyTestDriver` supports punctuations. Event-time (stream-time) punctuations trigger automatically based on the timestamps of piped records, while wall-clock punctuations require manual advancement:

```java
testDriver.advanceWallClockTime(Duration.ofMillis(20L));
assertThat(outputTopic.readKeyValue(),
    equalTo(new KeyValue<>("triggered-key", "triggered-value")));
```

For windowed operations, control event time by piping records with explicit timestamps, or configure the input topic with a start time and auto-advance:

```java
TestInputTopic<String, String> in = testDriver.createInputTopic("in",
    new StringSerializer(), new StringSerializer(),
    Instant.parse("2026-01-01T00:00:00Z"), Duration.ofSeconds(10));   // each pipeInput +10 s
in.advanceTime(Duration.ofMinutes(2));   // move event time forward (closes windows / fires suppress)
```

### State store access

Access state stores before or after piping input, to pre-populate them or to verify updates:

```java
KeyValueStore<String, Long> store = testDriver.getKeyValueStore("store-name");
assertEquals(Long.valueOf(2L), store.get("some key"));

WindowStore<String, Long> windowStore = testDriver.getWindowStore("windowed-store");
```

Always close the test driver when finished (this also cleans up state directories):

```java
testDriver.close();
```

### Unit testing processors with MockProcessorContext

For custom `Processor` (and `FixedKeyProcessor`) implementations, use `MockProcessorContext` from `org.apache.kafka.streams.processor.api` to capture forwarded data:

```java
final Processor<String, String, String, Long> processorUnderTest = ...;
final MockProcessorContext<String, Long> context = new MockProcessorContext<>();
processorUnderTest.init(context);
```

Pass configuration to the mock context:

```java
final Properties props = new Properties();
props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
final MockProcessorContext<String, Long> context = new MockProcessorContext<>(props);
```

Capturing forwarded records:

```java
processorUnderTest.process(new Record<>("key", "value", 0L));

final Iterator<CapturedForward<? extends String, ? extends Long>> forwarded = context.forwarded().iterator();
assertEquals(new Record<>("key", 5L, 0L), forwarded.next().record());
assertFalse(forwarded.hasNext());

context.resetForwards();
assertEquals(0, context.forwarded().size());
```

Set record metadata (topic/partition/offset) that the processor may read:

```java
context.setRecordMetadata("topicName", 0, 0L);
```

Register in-memory state stores (logging must be disabled — there is no changelog in a mock):

```java
final KeyValueStore<String, Integer> store =
    Stores.keyValueStoreBuilder(
        Stores.inMemoryKeyValueStore("myStore"),
        Serdes.String(),
        Serdes.Integer())
    .withLoggingDisabled()
    .build();
store.init(context.getStateStoreContext(), store);
context.addStateStore(store);
```

Punctuator scheduling — the mock captures scheduled punctuators without automatically executing them:

```java
final MockProcessorContext.CapturedPunctuator capturedPunctuator = context.scheduledPunctuators().get(0);
final long interval = capturedPunctuator.getInterval().toMillis();
final PunctuationType type = capturedPunctuator.getType();
final Punctuator punctuator = capturedPunctuator.getPunctuator();
punctuator.punctuate(0L);   // trigger manually
```

Commit requests are also captured: `assertTrue(context.committed()); context.resetCommit();`.

For automatic punctuator firing and full topology behaviour, use `TopologyTestDriver` with a simple topology containing your processor.
