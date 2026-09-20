# Kafka Connect — Error handling, retries & Dead Letter Queue (KIP-298)

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-298%3A+Error+Handling+in+Connect · bảng config: https://kafka.apache.org/43/generated/sink_connector_config.html · https://docs.confluent.io/platform/current/connect/concepts.html#dead-letter-queue
> **Tuần:** 5 — Schema Registry & Serialization + Kafka Connect · **Loại:** KIP + Apache Kafka Docs
> ⚠️ Trang cwiki KIP-298 **không crawl được** (bị chặn) — phần Nội dung dưới đây được tổng hợp từ docs chính thức (bảng config Kafka 4.3 crawl thành công) và nội dung KIP; luôn đối chiếu link gốc.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Trước KIP-298 (Kafka 2.0), **mọi lỗi** (converter, SMT, put) làm **task FAILED** ngay. KIP-298 thêm khả năng **retry**, **tolerate/skip** và **DLQ**.
- `errors.tolerance` mặc định **`none`** (lỗi đầu tiên → task FAILED, phải restart qua REST) · `all` = **bỏ qua record lỗi** và tiếp tục.
- `errors.retry.timeout` mặc định **`0`** (không retry); `-1` = retry vô hạn; `errors.retry.delay.max.ms` mặc định **60000** (exponential backoff tới 1 phút). Chỉ retry lỗi **retriable** (`RetriableException`).
- `errors.log.enable` mặc định **false** → bật để ghi lỗi vào log worker; `errors.log.include.messages` mặc định **false** → bật để log **cả nội dung record** (cẩn thận PII).
- **DLQ chỉ có ở SINK connector**: `errors.deadletterqueue.topic.name` (mặc định rỗng = tắt), `errors.deadletterqueue.topic.replication.factor` mặc định **3** (cluster 1 node dev phải đặt **1**), `errors.deadletterqueue.context.headers.enable` mặc định **false** → bật để có header `__connect.errors.*`.
- Source connector **không có DLQ** vì record lỗi chưa có "topic Kafka" để tham chiếu; source chỉ có retry + log + skip (`errors.tolerance=all`).
- Giai đoạn được bao phủ: **converter** (key/value/header), **transformation (SMT)**, và với sink là **`put()`** khi connector ném `RetriableException` (retry) — lỗi bên trong hệ đích thường do connector tự xử lý hoặc dùng cơ chế riêng (Confluent `reporter.error.topic.name`).
- DLQ record = **bytes gốc** của record (key/value/header y nguyên), không phải bản đã biến đổi → có thể replay lại topic gốc sau khi sửa.
- Header DLQ: `__connect.errors.topic`, `.partition`, `.offset`, `.connector.name`, `.task.id`, `.stage` (`KEY_CONVERTER`/`VALUE_CONVERTER`/`HEADER_CONVERTER`/`TRANSFORMATION`/`KAFKA_CONSUME`...), `.class.name`, `.exception.class.name`, `.exception.message`, `.exception.stacktrace`.
- DLQ topic được **admin client của worker** tạo tự động nếu chưa có (cần quyền `Create` topic); ghi bằng producer của worker (override qua `admin.override.*`/`producer.override.*`).

---

## 📄 Nội dung (tổng hợp từ KIP-298 và docs chính thức)

### Motivation (KIP-298)

Prior to Kafka 2.0, any exception thrown while a Connect task processed a record — in a converter (deserialization), in a transformation, or in the connector's `put()`/`poll()` — caused the task to **fail immediately** and stop processing. Operators had to inspect logs, fix or skip the bad record manually and restart the task via the REST API. For long-running data pipelines a single malformed message ("poison pill") could halt an entire sink. KIP-298 adds a configurable **error-handling framework** in the Connect runtime that can:

1. **Retry** operations that fail with retriable errors, with exponential backoff, for a bounded (or unbounded) duration.
2. **Tolerate** errors — skip the problematic record and continue — instead of failing the task.
3. **Log** the error, optionally including the record contents.
4. For **sink connectors**, write the failed record to a **dead letter queue (DLQ)** topic, optionally with error-context headers.

### Scope — which stages are covered

The framework wraps the stages of the Connect pipeline that are executed by the framework itself:

| Stage (header value) | Source connector | Sink connector |
|---|---|---|
| `TASK_POLL` (SourceTask.poll) | retry | — |
| `TRANSFORMATION` (each SMT) | retry + tolerate | retry + tolerate |
| `KEY_CONVERTER` / `VALUE_CONVERTER` / `HEADER_CONVERTER` | retry + tolerate | retry + tolerate |
| `KAFKA_PRODUCE` (writing to Kafka) | retry (producer) | — |
| `KAFKA_CONSUME` (reading from Kafka) | — | retry |
| `TASK_PUT` (SinkTask.put) | — | retry on `RetriableException`; non-retriable exceptions from `put()` still fail the task (the connector owns error handling inside the target system) |

Errors during the connector's own interaction with the external system (e.g. a database constraint violation) are only covered if the connector throws `org.apache.kafka.connect.errors.RetriableException`; otherwise the connector must implement its own handling (Confluent's sink connectors expose `reporter.error.topic.name` via the *Connect Reporter* / `ErrantRecordReporter` API from KIP-610 which lets a sink report individual bad records to the same DLQ).

### Configuration (connector-level, Kafka 4.3)

| Property | Default | Applies to | Description |
|---|---|---|---|
| `errors.retry.timeout` | `0` | source + sink | The maximum duration in milliseconds that a failed operation will be reattempted. The default is `0`, which means no retries will be attempted. Use `-1` for infinite retries. |
| `errors.retry.delay.max.ms` | `60000` (1 min) | source + sink | The maximum duration in milliseconds between consecutive retry attempts. Jitter will be added to the delay once this limit is reached to prevent thundering herd issues. |
| `errors.tolerance` | `none` | source + sink | Behavior for tolerating errors during connector operation. `none` is the default value and signals that any error will result in an immediate connector task failure; `all` changes the behavior to skip over problematic records. |
| `errors.log.enable` | `false` | source + sink | If true, write each error and the details of the failed operation and problematic record to the Connect application log. This is `false` by default, so that only errors that are not tolerated are reported. |
| `errors.log.include.messages` | `false` | source + sink | Whether to include in the log the Connect record that resulted in a failure. For sink records, the topic, partition, offset, and timestamp will be logged. For source records, the key and value (and their schemas), all headers, and the timestamp, Kafka topic, Kafka partition, source partition, and source offset will be logged. This is `false` by default, which will prevent record keys, values, and headers from being written to log files, although some information such as topic and partition number will still be logged. |
| `errors.deadletterqueue.topic.name` | `""` | **sink only** | The name of the topic to be used as the dead letter queue (DLQ) for messages that result in an error when processed by this sink connector, or its transformations or converters. The topic name is blank by default, which means that no messages are to be recorded in the DLQ. |
| `errors.deadletterqueue.topic.replication.factor` | `3` | sink only | Replication factor used to create the dead letter queue topic when it doesn't already exist. |
| `errors.deadletterqueue.context.headers.enable` | `false` | sink only | If true, add headers containing error context to the messages written to the dead letter queue. To avoid clashing with headers from the original record, all error context header names, all error context header names will start with `__connect.errors.` |

Retries honour the task's shutdown: a retry loop is interrupted if the task is stopped. With `errors.tolerance=none` and `errors.retry.timeout>0`, the operation is retried until the timeout and **then** the task fails.

### Dead letter queue behaviour (sink connectors)

When `errors.tolerance=all` and `errors.deadletterqueue.topic.name` is set:

1. The record that failed in a converter, transformation or (retriable) `put()` is written **as originally read from Kafka** — the raw key bytes, value bytes and original headers — to the DLQ topic. Because the record is stored unmodified, it can later be replayed to the original topic (or reprocessed by a fixed pipeline).
2. The DLQ producer is the worker's producer (`producer.*` / `admin.*` settings apply). If the topic does not exist, the worker's admin client creates it with `errors.deadletterqueue.topic.replication.factor` and **1 partition** (partition count is not configurable through this property; create the topic manually for more).
3. If `errors.deadletterqueue.context.headers.enable=true`, the following headers are added:

| Header | Content |
|---|---|
| `__connect.errors.topic` | Name of the topic that contained the message. |
| `__connect.errors.partition` | Partition number of the topic that contained the message. |
| `__connect.errors.offset` | Offset of the message in the original topic. |
| `__connect.errors.connector.name` | Name of the connector. |
| `__connect.errors.task.id` | ID of the task. |
| `__connect.errors.stage` | Stage where the failure occurred (e.g. `VALUE_CONVERTER`, `TRANSFORMATION`, `TASK_PUT`). |
| `__connect.errors.class.name` | Fully qualified class name of the component that failed (converter or transformation class). |
| `__connect.errors.exception.class.name` | Class of the exception thrown. |
| `__connect.errors.exception.message` | Message of the exception. |
| `__connect.errors.exception.stacktrace` | Stack trace of the exception. |

4. Processing continues with the next record; the sink's consumer offset advances past the bad record.

Why no DLQ for source connectors: a failed source record has not yet been written to Kafka and carries connector-specific `sourcePartition`/`sourceOffset` rather than a Kafka topic-partition-offset; the framework can only log/skip it. Source connectors needing quarantine behaviour implement it themselves.

### Typical configurations

Fail fast (default, safest for correctness):

```properties
errors.tolerance=none
```

Retry transient errors for up to 10 minutes, then fail:

```properties
errors.retry.timeout=600000
errors.retry.delay.max.ms=30000
errors.tolerance=none
errors.log.enable=true
```

Keep the pipeline flowing, quarantine bad records (sink):

```properties
errors.tolerance=all
errors.log.enable=true
errors.log.include.messages=true
errors.deadletterqueue.topic.name=dlq-orders-sink
errors.deadletterqueue.topic.replication.factor=1      # dev single-broker; 3 in production
errors.deadletterqueue.context.headers.enable=true
```

Inspect a DLQ record with its headers:

```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic dlq-orders-sink \
  --from-beginning --property print.headers=true --property print.key=true
```

### Confluent Platform additions (recognition only)

Confluent sink connectors that implement the *Connect Reporter* expose `reporter.error.topic.name` / `reporter.result.topic.name` (and `reporter.bootstrap.servers`) to record per-record failures raised **inside** the connector (e.g. HTTP 4xx from a REST sink), complementing the framework-level `errors.deadletterqueue.*` which covers converter/SMT stages. Confluent Cloud managed connectors expose the same `errors.tolerance` / DLQ semantics with an auto-created `dlq-<connector-id>` topic.
