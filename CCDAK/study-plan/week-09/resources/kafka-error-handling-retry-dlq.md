# Kafka error handling patterns — Stop on error, Dead Letter Queue, Retry topics (non-blocking), Ordered retries

> **Nguồn (official):** https://www.confluent.io/blog/error-handling-patterns-in-kafka/ · https://developer.confluent.io/patterns/event-processing/dead-letter-stream/
> **Tuần:** 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns · **Loại:** Confluent Blog + Confluent Developer Patterns
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kafka **không có DLQ / retry sẵn cho consumer** (khác `SQS` có `RedrivePolicy` + `maxReceiveCount`) — bạn tự thiết kế bằng **topic**: `orders` → `orders-retry-1` → `orders-retry-2` → `orders-dlq`. Duy nhất có sẵn: **Kafka Connect sink DLQ** (`errors.tolerance=all` + `errors.deadletterqueue.topic.name` + `errors.deadletterqueue.context.headers.enable=true`) và **Kafka Streams** handlers (`DeserializationExceptionHandler`, `ProductionExceptionHandler`, `ProcessingExceptionHandler`).
- 4 pattern: **Stop on error** (dừng consumer, giữ ordering tuyệt đối — CDC/ledger) · **Dead Letter Queue** (lỗi không phục hồi → topic DLQ, stream chính chạy tiếp; **không retry**) · **Retry topic** (lỗi tạm thời → retry topic có delay, app retry riêng, **mất ordering** giữa record retry và record sau) · **Ordered retries** (registry key đang retry + redirect topic + tombstone để giữ thứ tự theo key).
- **Blocking retry** (retry tại chỗ trong `eachMessage`, `pause()` partition) giữ ordering nhưng chặn cả partition & rủi ro `max.poll.interval.ms` (5 phút) ⇒ rebalance. **Non-blocking retry** (publish sang retry topic) không chặn nhưng mất ordering — chỉ dùng khi nghiệp vụ chấp nhận eventual consistency.
- Headers khuyến nghị khi chuyển sang retry/DLQ: **original topic/partition/offset**, **retry attempt count**, **error message/stacktrace**, **timestamp** (SLA), event id. Delay giữa các lần retry: exponential backoff theo **timestamp trên record** (consumer retry topic `pause()` partition rồi `resume()` khi đến hạn) tránh thundering herd.
- **Poison pill** = record không bao giờ xử lý được (deserialization lỗi) → DLQ **ngay**, không retry. Reprocess DLQ **tự động** có rủi ro reorder/corrupt state ⇒ Confluent khuyên **reprocess thủ công**; DLQ thường là error log + alert.
- Liên hệ DVA: SQS DLQ redrive `StartMessageMoveTask` ↔ Kafka phải tự viết "redrive consumer" đọc DLQ và produce lại vào topic gốc; Lambda ESM Kafka có `DestinationConfig.OnFailure` (SQS/SNS/S3) là DLQ mức batch.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Error Handling Patterns in Kafka (Confluent blog)

Apache Kafka applications operate in distributed environments where failures are inevitable. Error handling strategies must align with business requirements regarding **ordering, retry capability, and data integrity**. Four primary patterns address increasing complexity levels.

#### Pattern 1: Stop on Error

**Use case:** Scenarios requiring strict sequential processing without exceptions, such as change-data-capture streams from databases.

**Mechanism:** When an error occurs during event transformation, the application halts immediately. Manual intervention becomes necessary to resolve the issue before processing resumes. Events cannot be diverted to alternative processing paths.

Characteristics: preserves complete ordering · no retry capability · requires human oversight for recovery · suitable for mission-critical, ordered workloads (CDC pipelines, ledger systems).

#### Pattern 2: Dead Letter Queue (DLQ)

**Concept:** Events that fail processing are automatically routed to a separate **error topic** while the main stream continues uninterrupted.

Processing paths: (1) successfully processed events → target topic; (2) non-recoverable events (malformed, missing required fields) → error/DLQ topic.

Key points: **no retry mechanism exists**; one-way routing to error topics; maintains main stream continuity; suitable for filtering irretrievable messages.

Design considerations: DLQ consumers should implement **alerting**; consider archiving DLQ messages for post-mortem analysis; implement reprocessing strategies separate from the main pipeline.

#### Pattern 3: Retry Topic with Retry Application

**Scenario:** Recoverable failures where dependent data eventually becomes available (e.g., item pricing delays in purchase request processing).

Processing paths: (1) normal flow → target topic; (2) non-recoverable errors → DLQ; (3) **temporary failures → retry topic**.

Architecture: dedicated **retry instances** (fewer than main instances); periodic retry attempts on delayed topics; backoff strategies prevent immediate reprocessing.

**Critical limitation:** *"Events are not guaranteed to be processed in the same sequence"* due to retry delays creating longer processing paths than normal flow. Example: Event 1 (requiring retry) arrives at target after Event 2 (processed immediately), causing out-of-order delivery.

When to use: applications where ordering is not critical; business logic tolerates eventual consistency.

#### Pattern 4: Maintain Order During Retries

**Problem addressed:** Inventory management and similar use cases where ordering is critical. Processing a decrease before a previous increase could trigger false purchase alerts or negative inventory states.

**Main application responsibilities:**

1. Maintain an in-memory registry of items (keys) with pending retries.
2. Route the first failed event for an item to the retry topic with a **unique message ID header**.
3. Publish the message ID to a **redirect/tracking topic**.
4. Subsequent events for the same item automatically route to the retry path, preserving order.
5. Listen to the redirect topic for **tombstone events** confirming successful retries, then remove the item from the registry.

**Retry application responsibilities:** process retry topic events sequentially; publish tombstone (null-value) events to the redirect topic upon successful processing.

Header usage: the message ID embedded in headers prevents original payload alteration and enables tombstone correlation for cleanup.

Recovery strategy: upon application failure, rebuild in-memory state by consuming the redirect topic from the beginning (compacted), reconstructing the pending items registry.

Advantages: maintains strict ordering for related events while enabling non-blocking retries; balances throughput with consistency requirements.

#### Header and metadata patterns

Recommended headers for retry logic: **original topic, partition, offset** (source identification) · **retry attempt counter** · **error details/stacktrace** · **timestamp** (SLA monitoring). Tombstone events (null values with specific keys) signal successful completion.

#### Choosing appropriate patterns

| Pattern | Use when |
| --- | --- |
| Stop on Error | CDC pipelines, ledger systems, financial transactions requiring immutability |
| Dead Letter Queue | Data validation failures, schema mismatches, filtering operations |
| Retry Topic | Microservices with external dependencies, temporary failures, eventual consistency acceptable |
| Ordered Retries | Inventory management, state machines, dependent event sequences |

Design recommendations: implement **exponential backoff** on retry topics to prevent thundering herd; separate DLQ and retry topics to distinguish recoverable from permanent failures; monitor retry topic lag as an indicator of dependency issues; consider **max retry counts** to prevent infinite loops; implement circuit breakers for permanent failures; log all routing decisions.

### Dead Letter Stream pattern (Confluent Developer)

**Problem:** Event processing applications need to handle cases where messages cannot be processed due to invalid data, corruption, or technical failures without terminating or becoming stuck.

**Solution:** When an event cannot be processed for unrecoverable reasons, it gets published to a "dead letter stream" for logging, later reprocessing, or other remediation. The dead letter event can include contextual details explaining why processing failed.

**Implementation:**

- *Kafka consumer:* wrap event processing in try/catch; on `SerializationException` or processing failure, report to a dead-event reporter that produces to the dead letter topic (with error headers).
- *Kafka Connect:* `errors.tolerance=all`, route problematic records via `errors.deadletterqueue.topic.name`, enable `errors.deadletterqueue.context.headers.enable=true` for error context (only **sink** connectors support the DLQ).
- *Kafka Streams:* register a custom `ProductionExceptionHandler` / `DeserializationExceptionHandler` (`default.deserialization.exception.handler`) that emits a dead event.
- *ksqlDB:* built-in handling for records that fail to deserialize (`ksql.deserialization.error.topic` / processing log).

**Considerations:** Automatic reprocessing of dead letter events risks **reordering and potential data corruption** when events represent state changes. Manual reprocessing is often preferred, with dead letter streams serving primarily as error logs.

**Related patterns:** Event Processing Application, Claim Check, Idempotent Reader / Idempotent Writer, Correlation Identifier, Event Router, Event Filter, Event Mapper, Event Translator.
