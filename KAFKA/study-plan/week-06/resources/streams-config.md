# Kafka Streams — Configuration Guide (`StreamsConfig`)

> **Nguồn (official):** https://docs.confluent.io/platform/current/streams/developer-guide/config-streams.html
> (bản Apache tương ứng: https://kafka.apache.org/documentation/streams/developer-guide/config-streams.html · https://kafka.apache.org/documentation/#streamsconfigs)
> **Tuần:** 6 — Kafka Streams · **Loại:** Confluent Docs (nội dung trùng Apache Kafka Docs)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **2 config bắt buộc:** `application.id` (= consumer `group.id`, prefix `client.id`, tên thư mục state, **prefix mọi internal topic** `<app.id>-...-repartition/-changelog`) và `bootstrap.servers`. Đổi `application.id` = **app mới**, mất state & offset cũ.
- `processing.guarantee` **`at_least_once`** (mặc định) / **`exactly_once_v2`** (cần broker ≥ 2.5; EOS cần ≥ **3 broker** theo mặc định `transaction.state.log.replication.factor=3`, `transaction.state.log.min.isr=2`). Giá trị `exactly_once` và `exactly_once_beta` cũ đã **bị xoá** ở 4.0.
- `commit.interval.ms` **30000** (ALOS) → tự đổi thành **100** khi EOS. Với EOS mỗi commit = 1 transaction → interval nhỏ giảm độ trễ end-to-end cho consumer `read_committed`.
- `statestore.cache.max.bytes` **10485760** (10 MB, chia đều cho các thread; tên cũ `cache.max.bytes.buffering` deprecated). Cache = 0 → downstream nhận **mọi** update.
- `num.stream.threads` **1**; `num.standby.replicas` **0** (đặt 1 → failover tức thì, tốn 2× storage, cần n+1 instance); `replication.factor` **-1** ở Apache 4.x (= broker default; Confluent ghi 1) cho internal topics — production nên **3**.
- `state.dir` mặc định `/${java.io.tmpdir}/kafka-streams` → production phải trỏ vào **persistent volume**, nếu không mỗi restart phải restore toàn bộ từ changelog.
- `default.key.serde` / `default.value.serde` mặc định **null** → không set thì phải truyền `Consumed.with/Produced.with/Grouped.with/Materialized.with…` ở mọi operator, nếu không sẽ lỗi `StreamsException: ... no default serde`.
- `default.timestamp.extractor` **`FailOnInvalidTimestamp`** (event-time từ record timestamp; timestamp âm → ném lỗi). Thay bằng `LogAndSkipOnInvalidTimestamp` (bỏ qua), `UsePartitionTimeOnInvalidTimestamp` (ước lượng), `WallclockTimestampExtractor` (processing-time).
- Exception handlers: `deserialization.exception.handler` (mặc định **`LogAndFailExceptionHandler`**; đổi sang `LogAndContinueExceptionHandler` để skip poison pill) · `production.exception.handler` (mặc định `DefaultProductionExceptionHandler` → FAIL; 4.2+ hỗ trợ DLQ qua `errors.deadletterqueue.topic.name`) · `processing.exception.handler` (3.9+, `LogAndFailProcessingExceptionHandler` mặc định / `LogAndContinueProcessingExceptionHandler`). Tên có tiền tố `default.` đã **deprecated** (KIP-1056).
- `task.timeout.ms` **300000** (5 phút) — task bị lỗi tạm thời (TimeoutException) retry tới đó rồi mới ném lỗi. `max.task.idle.ms` **0** — chờ dữ liệu partition khác để xử lý đúng thứ tự thời gian.
- `application.server` (`host:port`) — bắt buộc cho **Interactive Queries** phân tán (`queryMetadataForKey`). `group.protocol` **classic** / **`streams`** (KIP-1071, GA 4.2).
- Streams **ghi đè** client config: consumer `group.id=application.id`, `auto.offset.reset=earliest`, `enable.auto.commit=false`; khi EOS: consumer `isolation.level=read_committed`, producer `enable.idempotence=true`, `transactional.id` tự sinh. Ghi đè thủ công bằng prefix `consumer.`, `producer.`, `main.consumer.`, `restore.consumer.`, `global.consumer.`, `admin.`, `topic.`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Required configuration parameters

**application.id** (Required) — An identifier for the stream processing application. Must be unique within the Kafka cluster. Must use only alphanumeric characters, dots, hyphens, and underscores. It is used as: the default Kafka consumer and producer `client.id` prefix, the Kafka consumer `group.id` for coordination, the name of the subdirectory in the state directory (`state.dir`), and the prefix of internal Kafka topic names. Update the `application.id` when you deploy a new version of the application, unless you want to reuse the existing data in internal topics and state stores.

**bootstrap.servers** (Required) — A list of host/port pairs to use for establishing the initial connection to the Kafka cluster, e.g. `"kafka-broker1:9092,kafka-broker2:9092"`. Kafka Streams applications can only communicate with a single Kafka cluster specified by this config value.

### Optional configuration parameters

| Parameter name | Importance | Default value | Description |
|---|---|---|---|
| `acceptable.recovery.lag` | Medium | 10,000 | The maximum acceptable lag (total number of offsets to catch up from the changelog) for an instance to be considered caught-up and able to receive an active task. |
| `application.server` | Low | empty string | A `host:port` pair pointing to an embedded user-defined endpoint that can be used for discovering the locations of state stores within a single Kafka Streams application (Interactive Queries). |
| `buffered.records.per.partition` | Low | 1000 | The maximum number of records to buffer per partition. |
| `statestore.cache.max.bytes` | Medium | 10485760 bytes | Maximum number of memory bytes to be used for record caches across all threads. (Replaces deprecated `cache.max.bytes.buffering`.) |
| `commit.interval.ms` | Low | 30000 ms (`at_least_once`) / 100 ms (`exactly_once_v2`) | The frequency in milliseconds with which to save the position (offsets in source topics) of tasks. |
| `default.key.serde` | Medium | null | Default serializer/deserializer class for record keys, implements the `Serde` interface. |
| `default.value.serde` | Medium | null | Default serializer/deserializer class for record values, implements the `Serde` interface. |
| `default.timestamp.extractor` | Medium | `FailOnInvalidTimestamp` | Timestamp extractor class that implements the `TimestampExtractor` interface. |
| `deserialization.exception.handler` | Medium | `LogAndFailExceptionHandler` | Exception handling class that implements the `DeserializationExceptionHandler` interface. |
| `production.exception.handler` | Medium | `DefaultProductionExceptionHandler` | Exception handling class that implements the `ProductionExceptionHandler` interface. |
| `processing.exception.handler` | Medium | `LogAndFailProcessingExceptionHandler` | Exception handling class that implements the `ProcessingExceptionHandler` interface. |
| `errors.deadletterqueue.topic.name` | Low | null | Name of the dead letter queue topic used by the default exception handlers (KIP-1034). |
| `max.task.idle.ms` | Medium | 0 | Maximum amount of time a stream task will stay idle when not all of its partition buffers contain records, to avoid potential out-of-order record processing across multiple input streams. |
| `max.warmup.replicas` | Medium | 2 | The maximum number of warmup replicas (extra standbys beyond the configured `num.standby.replicas`) that can be assigned at once. |
| `num.standby.replicas` | High | 0 | The number of standby replicas (shadow copies of local state stores) for each task. |
| `num.stream.threads` | Medium | 1 | The number of threads to execute stream processing. |
| `probing.rebalance.interval.ms` | Low | 600000 ms (10 minutes) | The maximum time to wait before triggering a rebalance to probe for warmup replicas that have sufficiently caught up. |
| `processing.guarantee` | Medium | `at_least_once` | The processing mode. Can be either `at_least_once` or `exactly_once_v2` (requires brokers version 2.5 or newer). |
| `rack.aware.assignment.tags` / `rack.aware.assignment.strategy` | Medium | empty / `none` | Rack-aware standby and task assignment (`min_traffic`, `balance_subtopology`). |
| `replication.factor` | High | -1 (broker default) | The replication factor for changelog and repartition topics created by the application. |
| `rocksdb.config.setter` | Medium | — | The RocksDB configuration class implementing `RocksDBConfigSetter`. |
| `state.dir` | High | `/${java.io.tmpdir}/kafka-streams` | Directory location for state stores. |
| `task.timeout.ms` | Medium | 300000 ms (5 minutes) | The maximum amount of time a task might stall due to internal errors and retries until an error is raised. `0` = raise on first error. |
| `topology.optimization` | Low | `NO_OPTIMIZATION` | Set to `all` or a comma-separated list of `merge.repartition.topics`, `reuse.ktable.source.topics`, `single.store.self.join`. |
| `upgrade.from` | Medium | — | The version you are upgrading from during a rolling upgrade. |
| `windowstore.changelog.additional.retention.ms` | Low | 86400000 ms (1 day) | Added to a windows `maintainMs` to ensure data is not deleted from the log prematurely; allows for clock drift. |
| `group.protocol` | Low | `classic` | The group protocol: `classic` (consumer-group based, client-side assignment) or `streams` (KIP-1071 Streams Rebalance Protocol, broker-side assignment). |

### Exception handlers

**deserialization.exception.handler** — handles records that fail to deserialize. The handler returns `FAIL` (shut down the client) or `CONTINUE` (drop the record and continue). Built-in: `LogAndContinueExceptionHandler` (log and continue), `LogAndFailExceptionHandler` (log and fail — default). Use `CONTINUE` for "poison pill" records that would otherwise block a partition.

**production.exception.handler** — handles exceptions triggered when trying to interact with a broker, such as attempting to produce a record that is too large (`RecordTooLargeException`) or serialization errors. Returns `FAIL`, `CONTINUE`, or `RETRY`. Default `DefaultProductionExceptionHandler` always fails; with `errors.deadletterqueue.topic.name` set, the default handlers send the failed record to the DLQ topic.

**processing.exception.handler** (KIP-1033) — handles exceptions thrown by user code inside processors (`process()`, punctuators, DSL lambdas). Returns `FAIL` or `CONTINUE`. Built-in: `LogAndContinueProcessingExceptionHandler`, `LogAndFailProcessingExceptionHandler`.

### Timestamp extractors

- **`FailOnInvalidTimestamp`** (default) — retrieves the built-in timestamp embedded in Kafka messages (event-time if the producer set it, ingestion-time if the topic uses `LogAppendTime`). Throws `StreamsException` on invalid (negative) timestamps.
- **`LogAndSkipOnInvalidTimestamp`** — logs a warning and returns the invalid timestamp, causing the record to be silently dropped.
- **`UsePartitionTimeOnInvalidTimestamp`** — returns the valid built-in timestamp; on invalid timestamp it uses the partition time (previous record's timestamp) or throws if none.
- **`WallclockTimestampExtractor`** — returns `System.currentTimeMillis()`, i.e. processing-time semantics.
- Custom: implement `TimestampExtractor#extract(ConsumerRecord, long partitionTime)` to read a timestamp from the payload; return a negative value to drop a record.

### Consumer and producer configuration overrides

Kafka Streams assigns the following default values (some depend on `processing.guarantee`):

| Parameter | Client | Streams default |
|---|---|---|
| `group.id` | Consumer | same as `application.id` |
| `auto.offset.reset` | Consumer | `earliest` |
| `enable.auto.commit` | Consumer | `false` (Streams commits itself) |
| `isolation.level` | Consumer | `read_committed` when `exactly_once_v2` |
| `enable.idempotence` | Producer | `true` when `exactly_once_v2` |
| `transactional.id` | Producer | `<application.id>-<processId>-<threadId>` when `exactly_once_v2` |
| `linger.ms` | Producer | 100 |
| `max.poll.interval.ms` | Consumer | `Integer.MAX_VALUE` in older versions; now inherits the consumer default (300000) |
| `partition.assignment.strategy` | Consumer | `StreamsPartitionAssignor` (cannot be overridden under `classic`) |

Override client configs with the `consumer.`, `producer.`, `admin.` prefixes (e.g. `producer.max.request.size`), or per-consumer-type with `main.consumer.`, `restore.consumer.`, `global.consumer.`. Internal topic configs use the `topic.` prefix (e.g. `topic.min.insync.replicas`).

### Processing guarantee details

- **`at_least_once`** (default): committing means saving the position (offsets) of the processor; default `commit.interval.ms` = 30000 ms.
- **`exactly_once_v2`**: committing means committing the transaction, which includes saving the position and the output records atomically; default `commit.interval.ms` = 100 ms. Requires brokers 2.5+ (Confluent Platform 5.5+). By default the cluster must have at least 3 brokers, configurable via `transaction.state.log.replication.factor` and `transaction.state.log.min.isr`. `exactly_once_v2` uses one producer per stream thread (instead of one per task in the removed `exactly_once`) which improves scalability.

### Key configuration notes

- **State directory**: use persistent volumes for production rather than `/tmp/`; recreating state requires significant resources (restoring from changelog).
- **Standby replicas**: `num.standby.replicas=1` enables near-instant fail-over but requires 2× storage; provision n+1 instances for n standbys.
- **Replication factor**: set to 3 for internal topics so that up to two broker failures are tolerated.
- **Stream threads**: controls parallelism within one instance; total useful threads across all instances ≤ number of tasks.
- **Task timeout**: set to 0 ms to raise an error on first failure; larger values allow transparent retries of transient errors.
