# Kafka Connect — Exactly-once support for source connectors (KIP-618) & offset management

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-618%3A+Exactly-Once+Support+for+Source+Connectors · https://kafka.apache.org/documentation/#connect_exactlyonce · config: https://kafka.apache.org/43/generated/source_connector_config.html · https://docs.confluent.io/platform/current/connect/userguide.html#exactly-once-source-support
> **Tuần:** 5 — Schema Registry & Serialization + Kafka Connect · **Loại:** KIP + Apache Kafka Docs
> ⚠️ Trang cwiki KIP-618 **không crawl được** (bị chặn); phần Nội dung tổng hợp từ docs chính thức (bảng config Kafka 4.3 + Confluent userguide crawl được) và nội dung KIP — luôn đối chiếu link gốc.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Trước 3.3**: source connector chỉ **at-least-once** vì record ghi vào topic đích và offset ghi vào `connect-offsets` là **2 bước riêng** — task crash giữa 2 bước → khởi động lại đọc lại từ offset cũ → **duplicate**.
- **KIP-618 (Kafka 3.3+)**: worker dùng **transactional producer** ghi record + source offset trong **cùng 1 transaction** → **exactly-once source**. Chỉ hỗ trợ **distributed mode**.
- Worker: `exactly.once.source.support` = `disabled` (mặc định) → `preparing` → `enabled`. Nâng cấp **rolling 2 bước**: đặt tất cả worker `preparing` trước, rồi tất cả `enabled` (không nhảy thẳng `disabled` → `enabled` trên cluster đang chạy).
- Connector: `exactly.once.support` = `requested` (mặc định, best effort) hoặc **`required`** (preflight check: nếu connector/worker không hỗ trợ → tạo connector **thất bại**).
- `transaction.boundary` = **`poll`** (mặc định: mỗi batch `poll()` = 1 transaction) · `interval` (commit theo `transaction.boundary.interval.ms`, mặc định bằng `offset.flush.interval.ms` 60 s) · `connector` (connector tự quyết định qua `TransactionContext`).
- Connector có thể dùng **topic offset riêng** `offsets.storage.topic` (per-connector) — cần khi cluster đích khác cluster của worker; worker cũng vẫn ghi vào topic offset toàn cục.
- Bảo mật/ACL: worker cần quyền `Write`/`Describe` trên `TransactionalId` (`connect-cluster-<group.id>`… và per-connector), `IdempotentWrite` cluster; consumer đọc offsets với `read_committed`. Ngoài ra dùng **zombie fencing** (fence task thế hệ cũ trước khi khởi động thế hệ mới).
- **Sink connector không có EOS** ở cấp framework: sink đọc với consumer group `connect-<name>`, offset commit sau `put()`/`flush()` → at-least-once; muốn "exactly-once" ở đích → connector phải ghi **idempotent/upsert** (JDBC `insert.mode=upsert` + `pk.mode`, S3 sink theo partition offset deterministic, Elasticsearch dùng key làm `_id`).
- Offset source lưu dạng **map do connector định nghĩa**: `sourcePartition` (ví dụ `{"filename":"test.txt"}`, `{"server":"pg1"}`) + `sourceOffset` (`{"position":1234}`, `{"lsn":...}`); key trong `connect-offsets` = `["<connector-name>", {sourcePartition}]`.
- Consumer đọc topic của connector EOS phải đặt `isolation.level=read_committed` để không thấy record của transaction bị abort.

---

## 📄 Nội dung (tổng hợp từ KIP-618 và docs chính thức)

### Motivation

Kafka Connect source tasks deliver records to Kafka with a **producer** and periodically **commit source offsets** (the connector-defined positions such as a file position, database LSN or table primary-key watermark) to the offsets topic (`offset.storage.topic`) or the offsets file. Before Kafka 3.3 these two writes were independent: the worker wrote records first, then — every `offset.flush.interval.ms` (default 60 000 ms) — flushed the offsets. If a task crashed after records were produced but before their offsets were committed, the restarted task resumed from the older committed offset and **re-emitted** the records. Source connectors were therefore **at-least-once**. Additionally, during a rebalance a "zombie" task instance on a stuck worker could keep producing records concurrently with its replacement, causing duplicates that even a transactional producer could not prevent without fencing.

Because Kafka's producer supports **transactions** (KIP-98) and Connect's offsets are themselves stored in a Kafka topic, both writes can be made **atomic**: the records and the corresponding offset commit are written in the same transaction, and a consumer with `isolation.level=read_committed` sees either both or neither.

### Proposed changes

#### Worker-level: `exactly.once.source.support`

| Value | Behaviour |
|---|---|
| `disabled` (default) | Legacy behaviour; source tasks use a normal (idempotent) producer; at-least-once. |
| `preparing` | The worker **understands** the new protocol and is ready to participate (it will not run zombie-fencing rounds itself, but will not break a cluster that has EOS enabled). Used as the first phase of a rolling upgrade. |
| `enabled` | Source tasks run with transactional producers; the leader worker performs **zombie fencing** of old task generations before new generations start; per-connector offsets topics are used. |

Rolling upgrade procedure: (1) set every worker to `preparing` and restart them one at a time; (2) then set every worker to `enabled` and restart again. Downgrading follows the reverse order. Mixing `disabled` and `enabled` workers in one cluster is not supported (the leader refuses to start connectors with EOS if any worker is still `disabled`).

Exactly-once source support is only available in **distributed mode**; standalone workers do not support it (`exactly.once.source.support` is a distributed worker property).

#### Connector-level: `exactly.once.support`

| Value | Behaviour |
|---|---|
| `requested` (default) | Preflight check is skipped; the connector runs with exactly-once semantics if the worker supports it, otherwise at-least-once. |
| `required` | Preflight check: when the connector is created or reconfigured, Connect verifies that (a) the worker cluster has `exactly.once.source.support=enabled` and (b) the connector class declares that it can support exactly-once (`SourceConnector.exactlyOnceSupport()` returns `SUPPORTED`). If either check fails, the connector **fails to be created/started** with a validation error. |

A connector author indicates support by implementing `exactlyOnceSupport(Map<String,String> connectorConfig)` and, optionally, `canDefineTransactionBoundaries()`.

#### `transaction.boundary`

| Value | Behaviour |
|---|---|
| `poll` (default) | A new producer transaction is started and committed for every **batch** of records returned from `SourceTask.poll()`. Simplest; each poll batch and its offsets are atomic. |
| `interval` | Transactions are committed on a user-defined time interval, `transaction.boundary.interval.ms` (if not set, defaults to the worker's `offset.flush.interval.ms`). Fewer, larger transactions → higher throughput, higher end-to-end latency. |
| `connector` | The connector itself defines transaction boundaries through the `TransactionContext` API (`commitTransaction()`, `abortTransaction()`, or per-record variants). Only valid if `canDefineTransactionBoundaries()` returns `SUPPORTED`. |

Source connector configs (Kafka 4.3 generated docs):

| Name | Default | Valid values | Description |
|---|---|---|---|
| `exactly.once.support` | `requested` | `REQUIRED`, `REQUESTED` | Permitted values are `requested`, `required`. If set to `required`, forces a preflight check for the connector to ensure that it can provide exactly-once semantics with the given configuration. Some connectors may be capable of providing exactly-once semantics but not signal to Connect that they support this; in that case, documentation for the connector should be consulted carefully before creating it, and the value for this property should be set to `requested`. Additionally, if the value is set to `required` but the worker that performs preflight validation does not have exactly-once support enabled for source connectors, requests to create or validate the connector will fail. |
| `transaction.boundary` | `poll` | `INTERVAL`, `POLL`, `CONNECTOR` | Permitted values are: `poll`, `interval`, `connector`. If set to `poll`, a new producer transaction will be started and committed for every batch of records that each task from this connector provides to Connect. If set to `connector`, relies on connector-defined transaction boundaries; note that not all connectors are capable of defining their own transaction boundaries, and in that case, attempts to instantiate a connector with this value will fail. Finally, if set to `interval`, commits transactions only after a user-defined time interval has passed. |
| `transaction.boundary.interval.ms` | `null` | `[0,…]` | If `transaction.boundary` is set to `interval`, determines the interval for producer transaction commits by connector tasks. If unset, defaults to the value of the worker-level `offset.flush.interval.ms` property. It has no effect if a different transaction boundary is specified. |
| `offsets.storage.topic` | `null` | non-empty string | The name of a separate offsets topic to use for this connector. If empty or not specified, the worker's global offsets topic name will be used. If specified, the offsets topic will be created if it does not already exist on the Kafka cluster targeted by this connector's producer (which may be different from the one used for the worker's global offsets topic if the `bootstrap.servers` property of the connector's producer has been overridden from the worker's). Only applicable in distributed mode; in standalone mode, setting this property will have no effect. |

#### How a transaction wraps records and offsets

For each transaction boundary the task's transactional producer (with `transactional.id` derived from the connector name and task ID, e.g. `<group.id>-<connector>-<taskId>`) does:

1. `beginTransaction()`
2. `send()` every source record to its target topic(s);
3. `send()` the corresponding **offset records** to the connector's offsets topic (per-connector `offsets.storage.topic` if configured, which must be on the **same cluster** as the target topics — a transaction cannot span clusters) — this is why a separate offsets topic is needed when the connector produces to a different cluster than the worker's;
4. `commitTransaction()`.

If the task fails between steps, the transaction is aborted: neither the records nor the offsets become visible to `read_committed` consumers, and the restarted task resumes from the last committed offsets without duplicates. The worker additionally writes the offsets to the **global** offsets topic (outside the transaction) so tooling such as `GET /connectors/{name}/offsets` keeps working.

#### Zombie fencing

Before a new generation of tasks for a connector starts, the **leader worker** fences out the previous generation by initialising transactional producers with the old tasks' `transactional.id`s (`initTransactions()`), which bumps the producer epoch and causes any still-running zombie task to fail on its next produce with `ProducerFencedException`. This requires the leader to have `Write`/`Describe` on the connector's transactional IDs and an `IdempotentWrite` cluster permission.

#### Required ACLs (secured clusters)

| Principal | Resource | Operations |
|---|---|---|
| Worker (leader) | `TransactionalId` `<group.id>-<connector>-<taskId>` for every task | `Write`, `Describe` |
| Worker (leader) | Cluster | `IdempotentWrite` |
| Connector producer | `TransactionalId` its own | `Write`, `Describe` |
| Connector producer | Cluster | `IdempotentWrite` |
| Connector producer | Topic (offsets topic) | `Write`, `Read`, `Describe`, `Create` (if it must be created) |
| Connector consumer (for reading offsets) | Group `<group.id>` / offsets topic | `Read` with `isolation.level=read_committed` |

### Limitations

- Only **source** connectors and only **distributed** mode.
- Connectors must be designed for it: a connector whose offsets do not fully capture its position (for example one that reads from a non-replayable API) cannot be exactly-once even with the framework's help — hence `exactly.once.support=required` as a guard.
- **Sink connectors are not covered.** A sink reads with the worker's consumer (group `connect-<connector-name>`), calls `put()`, and commits consumer offsets after `flush()`/`preCommit()`; a crash between writing to the external system and committing offsets replays records → at-least-once. Effective exactly-once for sinks relies on **idempotent writes** (upserts keyed by a primary key or the Kafka coordinates topic-partition-offset, deterministic object names as in the S3 sink) or on the target system's own transactions managed by the connector.
- Throughput cost: transactional producers add commit round-trips per boundary; `interval` boundaries amortise this.

### Offsets in Connect — summary

| | Source connector | Sink connector |
|---|---|---|
| Where stored | `offset.storage.topic` (default `connect-offsets`, 25 partitions, compacted) or standalone `offset.storage.file.filename`; optional per-connector `offsets.storage.topic` | `__consumer_offsets` via consumer group **`connect-<connector-name>`** |
| Format | Connector-defined `sourcePartition` map → `sourceOffset` map, keyed by `[connectorName, sourcePartition]` | Kafka topic-partition → offset |
| Commit trigger | `offset.flush.interval.ms` (60 s), or transaction boundary when EOS | After `put()`/`flush()` (`preCommit()` may override), at consumer commit interval |
| Inspect | `kafka-console-consumer --topic connect-offsets --property print.key=true`; `GET /connectors/{name}/offsets` | `kafka-consumer-groups --describe --group connect-<name>`; `GET /connectors/{name}/offsets` |
| Reset / alter | `PATCH`/`DELETE /connectors/{name}/offsets` (connector `STOPPED`, 3.6+); or produce a tombstone with the same key to `connect-offsets` (legacy) | Same REST endpoints, or `kafka-consumer-groups --reset-offsets` while the connector is stopped |
| Effect of `DELETE /connectors/{name}` | Offsets **remain** in the topic → a recreated connector with the same name resumes | Consumer group remains until `offsets.retention.minutes` (7 days) → recreated sink resumes |
