# Transactional Outbox pattern + Debezium Outbox Event Router SMT (giải bài dual-write)

> **Nguồn (official):** https://microservices.io/patterns/data/transactional-outbox.html · https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html (crawl qua bản nguồn GitHub `debezium/debezium` docs)
> **Tuần:** 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns · **Loại:** Pattern reference (microservices.io) + Debezium Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất. Trang debezium.io trả 403 khi crawl trực tiếp → phần Debezium lấy từ nguồn asciidoc trên GitHub và bổ sung từ kiến thức docs.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Dual-write problem**: service vừa `UPDATE` DB vừa `producer.send()` → không atomic (crash giữa 2 bước ⇒ mất event hoặc event "ma"); **2PC** giữa DB và Kafka không có. Giải: **Transactional Outbox** — ghi event vào bảng `outbox` **trong cùng local transaction** với business entity; **message relay** đọc outbox và publish lên Kafka.
- 2 kiểu relay: **Polling publisher** (job quét bảng — đơn giản, tốn DB, có độ trễ) vs **Transaction log tailing** (**CDC** đọc WAL/binlog — `Debezium` — không tốn query, gần real-time). Outbox → **at-least-once** ⇒ consumer phải **idempotent** (lưu event id đã xử lý).
- Bảng outbox chuẩn Debezium: `id` (UUID, event id) · `aggregatetype` (quyết định **topic đích**) · `aggregateid` (→ **Kafka key** ⇒ ordering theo aggregate) · `type` (loại event, ví dụ `OrderCreated`) · `payload` (JSON/JSONB) (+ cột thêm tuỳ ý).
- SMT `io.debezium.transforms.outbox.EventRouter`: `transforms=outbox`; `route.by.field` (mặc định `aggregatetype`); `route.topic.replacement` (mặc định **`outbox.event.${routedByValue}`** → `aggregatetype=Order` ⇒ topic `outbox.event.Order`); `table.field.event.id` (`id` → header `id`); `table.field.event.key` (`aggregateid` → key); `table.field.event.payload` (`payload` → value); `table.fields.additional.placement=type:header:eventType` (đưa cột vào header/envelope/partition); `table.expand.json.payload=true` (parse JSON string thành struct); `route.tombstone.on.empty.payload`; `table.op.invalid.behavior` = `warn` (mặc định)/`error`/`fatal` cho UPDATE; **DELETE bị bỏ qua** ⇒ app có thể `INSERT` rồi `DELETE` ngay trong cùng transaction để bảng outbox không phình.
- Liên hệ AWS/DVA: chạy Debezium trên **MSK Connect** (custom plugin từ S3) đọc RDS/Aurora Postgres (`rds.logical_replication=1`, `wal_level=logical`); tương tự **DynamoDB Streams + Lambda** là "CDC" phía AWS.
- Bẫy: "đảm bảo event chỉ phát khi DB commit" ⇒ Outbox, **không phải** `acks=all` hay transaction Kafka (Kafka transaction chỉ atomic **Kafka→Kafka**). "Không muốn sửa code ghi outbox" ⇒ CDC trực tiếp bảng nghiệp vụ (nhưng lộ schema nội bộ); outbox = **CDC có kiểm soát contract**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Pattern: Transactional outbox (microservices.io)

**Context** — A service command typically needs to update the database **and** send messages/events. For example, a service that participates in a saga needs to atomically update the database and send messages/events. Similarly, a service that publishes a domain event must atomically update an aggregate and publish an event. The database update and sending of the message must be atomic in order to avoid data inconsistencies and bugs.

**Problem** — How to reliably/atomically update the database and send messages/events?

**Forces** —

- 2PC is not an option (the message broker might not support 2PC, or it is undesirable coupling).
- If the database transaction commits, messages must be sent. Conversely, if the database rolls back, the messages must not be sent.
- Messages must be sent to the message broker in the order they were sent by the service. This ordering must be preserved across service instances.

**Solution** — *"The solution is for the service that sends the message to first store the message in the database as part of the transaction that updates the business entities. A separate process then sends the messages to the message broker."*

The **outbox** is a table (or, in a NoSQL database, a property of the document) holding messages. A **Message Relay** component reads the outbox and publishes the messages to the broker, using either the **Polling publisher** or the **Transaction log tailing** pattern.

**Resulting context** — Benefits: messages are guaranteed to be sent if and only if the database transaction commits; messages are sent in the order they were sent by the application; no 2PC. Drawbacks: potentially error-prone since the developer might forget to publish the message/event after updating the database. The Message Relay might publish a message more than once (crash after publishing but before recording that it has done so) — **the message consumer must be idempotent**, typically by tracking the IDs of messages it has already processed (**Idempotent Consumer** pattern).

**Related patterns** — Saga and Domain event patterns create the need for this pattern; Event sourcing is an alternative solution; Polling publisher and Transaction log tailing are the two ways to implement the message relay; consumers use the Idempotent Consumer pattern.

### Debezium — Outbox Event Router

The outbox event router SMT enables reliable data exchange between microservices: a service writes business data **and** an outbox row in one local transaction; Debezium captures the outbox table via the transaction log and the SMT routes each captured change event to the right Kafka topic with a stable key and payload.

#### Example outbox table

```sql
CREATE TABLE outbox (
  id            UUID         NOT NULL PRIMARY KEY,   -- unique event id → Kafka header "id"
  aggregatetype VARCHAR(255) NOT NULL,               -- routing: Order → outbox.event.Order
  aggregateid   VARCHAR(255) NOT NULL,               -- Kafka message key
  type          VARCHAR(255) NOT NULL,               -- event type, e.g. OrderCreated
  payload       JSONB                                -- Kafka message value
);
```

Additional custom columns can be included for supplementary data (and placed into headers or the envelope via `table.fields.additional.placement`).

#### Basic configuration

```
transforms=outbox
transforms.outbox.type=io.debezium.transforms.outbox.EventRouter
```

This applies the default behavior: route by `aggregatetype`, key = `aggregateid`, value = `payload`, header `id` = `id`.

#### Message routing

By default, the SMT routes messages using the `aggregatetype` column value. `route.by.field` (default `aggregatetype`) names the column; `route.topic.replacement` (default **`outbox.event.${routedByValue}`**) is the topic name template. When `aggregatetype` is `orders`, messages emit to topic `outbox.event.orders`. `route.topic.regex` (default `(?<routedByValue>.*)`) lets you match/transform the routing value.

#### Emitted message (example)

- **Key:** `"order-1001"` (value of `aggregateid`)
- **Headers:** `id=3f2a...-uuid` (value of `id`), plus any `additional.placement` headers, e.g. `eventType=OrderCreated`
- **Value:** the `payload` column (string, or expanded struct with `table.expand.json.payload=true`)

#### Configuration options

| Option | Default | Description |
| --- | --- | --- |
| `table.op.invalid.behavior` | `warn` | Behavior for UPDATE operations on the outbox table: `warn` (log + skip), `error` (log + skip... treated as error), `fatal` (stop connector). DELETE operations are filtered automatically. |
| `table.field.event.id` | `id` | Column with the unique event ID; written to the Kafka header `id`. |
| `table.field.event.key` | `aggregateid` | Column used as the Kafka record key. |
| `table.field.event.timestamp` | (none → change event timestamp) | Column used as the record timestamp. |
| `table.field.event.payload` | `payload` | Column used as the Kafka record value. |
| `table.fields.additional.placement` | (none) | Comma-separated `<column>:<placement>[:<alias>]`, placement = `header`, `envelope`, or `partition`. E.g. `type:header:eventType`. |
| `table.field.event.schema.version` | (none) | Column carrying the payload schema version. |
| `table.expand.json.payload` | `false` | Parse a JSON string payload into a Connect struct (Postgres JSON/JSONB). |
| `route.by.field` | `aggregatetype` | Column that determines the destination topic. |
| `route.topic.regex` | `(?<routedByValue>.*)` | Regex applied to the routing value. |
| `route.topic.replacement` | `outbox.event.${routedByValue}` | Destination topic name. Use a fixed string to send all events to one topic. |
| `route.tombstone.on.empty.payload` | `false` | Emit a tombstone (null value) when the payload is null/empty. |
| `tracing.*` | — | OpenTelemetry span context propagation options. |

#### Operational notes

- Only **INSERT** events are expected on the outbox table. The application may **delete the row immediately** in the same transaction (INSERT + DELETE) — the DELETE is filtered and the INSERT still appears in the WAL, so the outbox table stays empty.
- Combine with the Postgres connector config: `table.include.list=public.outbox`, `topic.prefix=shop`, `plugin.name=pgoutput`, `tombstones.on.delete=false`.
- Consumers should record the processed event `id` (from the header) in a `consumed_message` table / conditional write to stay **idempotent** under at-least-once delivery.
