# Kafka Streams 4.x — Streams Rebalance Protocol (KIP-1071), DLQ (KIP-1034), ProcessingExceptionHandler (KIP-1033) & API removals

> **Nguồn (official):** https://docs.confluent.io/platform/current/streams/upgrade-guide.html (Confluent Platform 8.0–8.3 ≈ Apache Kafka 4.0–4.3)
> Nguồn gốc KIP: https://cwiki.apache.org/confluence/display/KAFKA/KIP-1071%3A+Streams+Rebalance+Protocol · https://cwiki.apache.org/confluence/display/KAFKA/KIP-1034%3A+Dead+letter+queue+in+Kafka+Streams (cwiki không crawl được lúc viết — nội dung KIP bên dưới tổng hợp từ docs & KIP)
> **Tuần:** 6 — Kafka Streams · **Loại:** Confluent Docs + KIP
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **KIP-1071 Streams Rebalance Protocol:** Early Access **4.1**, **GA 4.2**. Bật bằng **`group.protocol=streams`**. Ứng dụng đăng ký thành **streams group** (loại group mới, không còn là consumer group); **broker tính assignment** (task → instance) thay cho client-side `StreamsPartitionAssignor` nhúng trong consumer protocol cũ. Kế thừa tư tưởng KIP-848 (heartbeat gộp, rebalance tăng dần, không "stop-the-world").
- Tool đi kèm: **`kafka-streams-groups.sh`** (list/describe/delete streams group, reset offsets) — `kafka-consumer-groups.sh` **không** thấy streams group.
- Hạn chế (EA): không static membership, đổi topology phải tạo group mới, không subscribe theo pattern, **không migrate online** classic ↔ streams (phải dừng toàn bộ instance rồi đổi config).
- **KIP-1034 DLQ trong Kafka Streams (4.2):** set **`errors.deadletterqueue.topic.name`** → các handler mặc định (`DefaultProductionExceptionHandler`, `LogAndContinue*`) gửi record lỗi vào DLQ với header `__streams.errors.exception`, `__streams.errors.stacktrace`, `__streams.errors.message`, `__streams.errors.topic/partition/offset`. Handler trả `Response` (`.fail()/.resume()/.retry()` + `withDeadLetterQueueRecords(...)`); method cũ `handle()`/`handleSerializationException()` deprecated → `handleError()`/`handleSerializationError()`.
- **KIP-1033 `ProcessingExceptionHandler` (3.9):** bắt exception ném ra từ **user code** trong processor/DSL lambda/punctuator — trước đây chỉ có handler cho deserialization và production. Config `processing.exception.handler`; `processing.exception.handler.global.enabled` (4.3) mở rộng cho global store.
- **KIP-1056:** `default.deserialization.exception.handler` & `default.production.exception.handler` **deprecated** → dùng `deserialization.exception.handler`, `production.exception.handler`.
- **Xoá ở 4.0:** `KStream#through()` (→ `repartition()`), `KStream#branch()` (→ `split().branch()`), `transform/transformValues/flatTransform` & `Transformer` (→ `process/processValues`), `KafkaStreams#setUncaughtExceptionHandler(Thread.UncaughtExceptionHandler)` (chỉ còn bản nhận `StreamsUncaughtExceptionHandler`), các builder window cũ (`TimeWindows.of`, `JoinWindows.of`, `SessionWindows.with`), `processing.guarantee=exactly_once` / `exactly_once_beta` (chỉ còn `exactly_once_v2`).
- Khác: `kafka-streams-scala` deprecated (KIP-1244, 4.3); `dsl.store.format=HEADERS` store nhận header (KIP-1285, 4.3); changelog offset lưu trong RocksDB thay `.checkpoint` file (KIP-1035, 4.3).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### KIP-1071: Streams Rebalance Protocol (Early Access 8.1.x / Kafka 4.1 → GA 8.2.x / Kafka 4.2)

The Streams Rebalance Protocol, introduced as Early Access in Confluent Platform 8.1.x, became generally available in 8.2.x. This broker-driven rebalancing system registers applications as **Kafka Streams groups** rather than consumer groups, enabling broker-side assignment computation.

**Key features:**

- Configuration: `group.protocol=streams` enables the dedicated protocol (default remains `classic`).
- CLI tool: `kafka-streams-groups.sh` script for listing, describing, and deleting streams groups (and resetting offsets).
- Sticky task assignor included as the basic broker-side assignment strategy (`group.streams.assignors`); high-availability assignor semantics (standby/warmup) are preserved.
- Interactive Query support available.

**Early Access limitations (8.1.x):**

- No static membership support.
- Topology updates require a new group creation.
- Pattern-based topic subscriptions unsupported.
- Protocol migration between classic and streams protocols unavailable (offline migration: stop all instances, change `group.protocol`, restart).

**Important note:** a critical broker-side bug in Confluent Platform 8.2.0 (KAFKA-20254) prevented offline migration from the classic protocol to the Streams Rebalance Protocol. This is fixed in version 8.3.0.

**Motivation (from the KIP):** in the classic protocol, Kafka Streams piggybacks on the consumer group protocol and embeds its own task assignment logic (`StreamsPartitionAssignor`) in the `subscription`/`assignment` user-data of the group leader; every member has to join a synchronous "stop-the-world" rebalance and the broker has no visibility into tasks, sub-topologies or standby replicas. KIP-1071 defines a dedicated group type (`streams`) with new RPCs `StreamsGroupHeartbeat` and `StreamsGroupDescribe`: members send their topology (sub-topologies, source topics, repartition/changelog topics) and process state; the broker's group coordinator validates the topology, creates internal topics, computes active/standby/warmup task assignments and hands them out incrementally through heartbeats, in the same spirit as KIP-848 for plain consumers. Broker-side configs are prefixed `group.streams.*` (e.g. `group.streams.session.timeout.ms`, `group.streams.heartbeat.interval.ms`, `group.streams.num.standby.replicas`, `group.streams.max.size`).

### KIP-1034: Dead Letter Queue for Kafka Streams (8.2.x / Kafka 4.2)

Kafka Streams now supports Dead Letter Queue (DLQ) functionality. When the `errors.deadletterqueue.topic.name` configuration is set and `DefaultProductionExceptionHandler` (or the `LogAndContinue*` deserialization/processing handlers) is used, records causing exceptions are forwarded to the specified DLQ topic instead of being silently dropped.

**API changes:**

- `ProductionExceptionHandler$ProductionExceptionHandlerResponse` class deprecated; replaced by the `Response` class (`Response.fail()`, `Response.resume()`, `Response.retry()`, each accepting a list of `ProducerRecord<byte[], byte[]>` dead-letter records via `withDeadLetterQueueRecords`).
- Methods `handle()` and `handleSerializationException()` deprecated in favor of `handleError()` and `handleSerializationError()` respectively.
- Same `Response` pattern added to `DeserializationExceptionHandler#handleError` and `ProcessingExceptionHandler#handleError`, so a custom handler can build its own DLQ records.

Records sent to the DLQ carry the original key/value bytes plus headers describing the failure:

| Header | Content |
|---|---|
| `__streams.errors.exception` | Exception class name |
| `__streams.errors.message` | Exception message |
| `__streams.errors.stacktrace` | Stack trace |
| `__streams.errors.topic` / `__streams.errors.partition` / `__streams.errors.offset` | Origin of the failed record (when available) |

Unlike Kafka Connect (`errors.deadletterqueue.topic.name` only for sink connectors, with `errors.tolerance=all`), the Streams DLQ is driven by the exception handlers and the application must create/own the DLQ topic.

### KIP-1033: ProcessingExceptionHandler (Kafka 3.9)

Developers can provide a processing exception handler to manage exceptions thrown while processing a record (inside user code such as `map`, `filter`, `Processor#process`, punctuators). Configure via `StreamsConfig#PROCESSING_EXCEPTION_HANDLER_CLASS_CONFIG` (`processing.exception.handler`). The handler must implement `org.apache.kafka.streams.errors.ProcessingExceptionHandler` and return `FAIL` or `CONTINUE`; built-in `LogAndFailProcessingExceptionHandler` (default) and `LogAndContinueProcessingExceptionHandler`.

**Related:** KIP-1270 (8.3.x / Kafka 4.3) extends `ProcessingExceptionHandler` support to global stores and GlobalKTables via `processing.exception.handler.global.enabled`.

### API removals and deprecations (8.0.x / Kafka 4.0 and later)

**Removed deprecated APIs in 4.0:**

- Builder methods for time/session/join/sliding windows without explicit grace (`TimeWindows.of`, `.grace()`, `JoinWindows.of`, `SessionWindows.with`, `SlidingWindows.withTimeDifferenceAndGrace`) — use `ofSizeWithNoGrace`/`ofSizeAndGrace`, `ofTimeDifferenceWithNoGrace`/`ofTimeDifferenceAndGrace`, `ofInactivityGapWithNoGrace`/`ofInactivityGapAndGrace`.
- `KStream#branch()` in Java and Scala — use `KStream#split()`.
- `KafkaStreams#setUncaughtExceptionHandler(Thread.UncaughtExceptionHandler)` — use the overload taking `StreamsUncaughtExceptionHandler`.
- `KStream#through()` in Java and Scala — use `KStream#repartition()`.
- Old processor APIs (`org.apache.kafka.streams.processor.Processor`, `ProcessorSupplier`, `ProcessorContext` of the old package) — use `org.apache.kafka.streams.processor.api.*`.
- `Transformer`, `ValueTransformer`, `transform`, `transformValues`, `flatTransform`, `flatTransformValues` — use `process` / `processValues`.
- `processing.guarantee` values `exactly_once` and `exactly_once_beta` — only `exactly_once_v2` remains.

**Configuration changes:**

- KIP-1056: deprecated `default.deserialization.exception.handler` and `default.production.exception.handler`; use `deserialization.exception.handler` and `production.exception.handler` instead.
- KIP-1244 (8.3.x): the `kafka-streams-scala` module is deprecated for Scala 2.12 and 2.13. Migrate to the Java DSL types from `org.apache.kafka.streams.kstream`.
- KIP-1285 (8.3.x): headers-aware state stores are available via `dsl.store.format=HEADERS`, enabling Schema Registry header-based formats inside state stores.
- KIP-1035 (8.3.x): state store changelog offsets are now persisted within RocksDB stores rather than in separate `.checkpoint` files — migration is transparent.

### StreamsUncaughtExceptionHandler (KIP-671, since 2.8 — still current)

`KafkaStreams#setUncaughtExceptionHandler(StreamsUncaughtExceptionHandler)` returns one of `REPLACE_THREAD` (spawn a new stream thread; the failed task is retried — may re-process records under at-least-once), `SHUTDOWN_CLIENT` (shut down this `KafkaStreams` instance only), or `SHUTDOWN_APPLICATION` (all instances with the same `application.id` shut down cooperatively via the rebalance protocol).
