# Error handling & Dead Letter Queue trong Connect (KIP-298) — góc vận hành

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-298%3A+Error+Handling+in+Connect · https://kafka.apache.org/43/generated/sink_connector_config.html · https://developer.confluent.io/courses/kafka-connect/error-handling-and-dead-letter-queues/ · https://docs.confluent.io/platform/current/connect/concepts.html
> **Tuần:** 6 — Kafka Connect operations · **Loại:** KIP + Apache Kafka Docs + Confluent Developer
> ⚠️ **cwiki.apache.org chặn WebFetch** (trả về rỗng ở cả hai dạng URL). Phần bảng config dưới đây lấy **nguyên văn từ trang `sink_connector_config.html` đã crawl được**; phần mô tả KIP và danh sách header **không crawl được từ cwiki, tổng hợp từ docs Confluent + trang khoá học Confluent Developer đã crawl** — đối chiếu lại link gốc trước ngày thi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- KIP-298 (**Kafka 2.0**) thêm một khung xử lý lỗi thống nhất cho Connect, phủ các **giai đoạn (stage)**: đọc từ Kafka / ghi vào Kafka · **converter** (deserialize key, value, header) · **transformation (SMT)** · **`put()` của sink task** / `poll()` của source task.
- Ba lựa chọn vận hành, Confluent gọi là *"fail fast, silently ignore, and dead letter queues"*:
  1. `errors.tolerance=none` (**mặc định**) → task chuyển **FAILED** ngay ở record đầu tiên hỏng. *"the corresponding connector task is going to stop and you will have to deal with the issue and then restart it."*
  2. `errors.tolerance=all` **không có DLQ** → record hỏng **biến mất im lặng**. Đây là cấu hình nguy hiểm nhất và là đáp án "sai nhưng hấp dẫn" trong đề.
  3. `errors.tolerance=all` **+ DLQ** → record hỏng được đẩy sang topic khác kèm header chẩn đoán, pipeline chạy tiếp.
- **DLQ chỉ tồn tại cho sink connector.** Trang `source_connector_config.html` **không có** bất kỳ key `errors.deadletterqueue.*` nào. Source connector chỉ có `errors.tolerance`, `errors.log.*`, `errors.retry.*`.
- `errors.deadletterqueue.topic.replication.factor` mặc định **3** — trên cluster nhỏ phải hạ xuống, nếu không task chết đúng lúc cần DLQ nhất.
- `errors.deadletterqueue.context.headers.enable` mặc định **false**: nếu không bật, DLQ chỉ chứa key/value gốc mà **không** có lý do lỗi → gần như vô dụng khi điều tra. Luôn bật ở production.
- `errors.log.enable=false` và `errors.log.include.messages=false` là mặc định. Bật `include.messages` ghi **nội dung record** vào log ứng dụng → cân nhắc **PII**.
- `errors.retry.timeout` mặc định **0** = không retry. `-1` = retry vô hạn. `errors.retry.delay.max.ms` **60000** là trần backoff. Retry chỉ có ý nghĩa với lỗi **tạm thời** (hệ đích timeout), không cứu được record hỏng về format.
- Giám sát DLQ bằng **`task-error-metrics`**: `deadletterqueue-produce-requests` (số lần thử ghi), `deadletterqueue-produce-failures` (ghi hỏng), `total-records-skipped`, `total-record-errors`, `total-record-failures`, `last-error-timestamp`.
- Cảnh báo vận hành của Confluent: *"Dead letter queues aren't a default in Kafka Connect because you need a way of dealing with the dead letter queue messages, otherwise you are just producing them somewhere for no reason."* → **DLQ không có consumer/alert = mất dữ liệu có thủ tục**.
- Lỗi converter kinh điển: dữ liệu JSON đọc bằng `AvroConverter` → `Unknown magic byte!`; dữ liệu Avro đọc bằng `JsonConverter` → `DataException: Converting byte[] to Kafka Connect data failed due to serialization error`. Cách chữa đúng là **đổi converter**, DLQ chỉ là lưới an toàn.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Configuration (nguyên văn từ `sink_connector_config.html`, Kafka 4.3)

| Configuration | Description | Type | Default | Valid Values |
|---|---|---|---|---|
| `errors.retry.timeout` | "The maximum duration in milliseconds that a failed operation will be reattempted." | long | 0 | — |
| `errors.retry.delay.max.ms` | "The maximum duration in milliseconds between consecutive retry attempts." | long | 60000 (1 minute) | — |
| `errors.tolerance` | "'none' signals any error causes immediate task failure; 'all' skips problematic records." | string | none | [none, all] |
| `errors.log.enable` | "If true, write each error and failed operation details to the Connect application log." | boolean | false | — |
| `errors.log.include.messages` | "Whether to include in the log the Connect record that resulted in a failure." | boolean | false | — |
| `errors.deadletterqueue.topic.name` | "The name of the topic to be used as the dead letter queue (DLQ) for error messages." | string | "" | — |
| `errors.deadletterqueue.topic.replication.factor` | "Replication factor used to create the dead letter queue topic when absent." | short | 3 | — |
| `errors.deadletterqueue.context.headers.enable` | "If true, add headers containing error context to messages written to the dead letter queue." | boolean | false | — |

> Bảng `source_connector_config.html` chứa `errors.retry.timeout`, `errors.retry.delay.max.ms`, `errors.tolerance`, `errors.log.enable`, `errors.log.include.messages` — và **không** chứa key `errors.deadletterqueue.*` nào.

### Dead letter queue — Confluent Docs (concepts)

"Dead Letter Queues apply only to sink connectors. To create a DLQ, configure:"

```
errors.tolerance = all
errors.deadletterqueue.topic.name = <topic-name>
```

"When `errors.tolerance` is `none` (default), invalid records cause connector failure. When set to `all`, errors are ignored and processing continues. Optional header context can be enabled via `errors.deadletterqueue.context.headers.enable=true`."

### Error handling patterns — Confluent Developer course

"Kafka Connect supports three error-handling approaches: fail fast, silently ignore, and dead letter queues."

**Fail fast (default):** "if Connect receives a serialization error… the corresponding connector task is going to stop and you will have to deal with the issue and then restart it."

**Dead letter queue:** "another Kafka topic to which messages can be routed by Kafka Connect if they fail to process in some way."

**Wrong converter:** if JSON messages are processed with an Avro converter, an "Unknown magic byte!" exception occurs because "the data is in a format other than that which the Avro deserializer expects."

**Multiple formats in one topic:** "the connector instance can only be configured to use a single converter."

**Inspecting the DLQ:** "you can inspect their headers, which will contain reasons for their rejection, and you can also look at their keys and values."

**Reprocessing:** "set the dead letter queue to receive the erroring messages, then reprocess them from the dead letter queue with the appropriate converter and send them onto the sink."

**Why it is not the default:** "Dead letter queues aren't a default in Kafka Connect because you need a way of dealing with the dead letter queue messages, otherwise you are just producing them somewhere for no reason."

### Header chẩn đoán trên record DLQ

*(Tổng hợp từ docs Confluent — không crawl được bảng gốc trên cwiki.)* Khi `errors.deadletterqueue.context.headers.enable=true`, mỗi record ghi vào DLQ mang thêm các header có tiền tố `__connect.errors.`:

| Header | Chứa gì |
|---|---|
| `__connect.errors.topic` | Topic gốc của record hỏng |
| `__connect.errors.partition` | Partition gốc |
| `__connect.errors.offset` | Offset gốc |
| `__connect.errors.connector.name` | Tên connector gặp lỗi |
| `__connect.errors.task.id` | Id của task gặp lỗi |
| `__connect.errors.stage` | Giai đoạn pipeline gây lỗi (vd `VALUE_CONVERTER`, `TRANSFORMATION`, `TASK_PUT`) |
| `__connect.errors.class.name` | Class thực thi giai đoạn đó (vd converter class) |
| `__connect.errors.exception.class.name` | Class của exception |
| `__connect.errors.exception.message` | Message của exception |
| `__connect.errors.exception.stacktrace` | Stack trace đầy đủ |

Bộ ba `topic` / `partition` / `offset` cho phép **truy ngược record gốc** trong topic nguồn, và `stage` cho biết ngay lỗi nằm ở converter, ở SMT hay ở hệ đích.

### Metrics đi kèm (`kafka.connect:type=task-error-metrics`)

| Attribute | Description |
|---|---|
| `total-record-errors` | "The number of record processing errors in this task." |
| `total-record-failures` | "The number of record processing failures in this task." |
| `total-records-skipped` | "The number of records skipped due to errors." |
| `total-retries` | "The number of operations retried." |
| `total-errors-logged` | "The number of errors that were logged." |
| `deadletterqueue-produce-requests` | "The number of attempted writes to the dead letter queue." |
| `deadletterqueue-produce-failures` | "The number of failed writes to the dead letter queue." |
| `last-error-timestamp` | "The epoch timestamp when this task last encountered an error." |
