# Kafka Connect User Guide — standalone vs distributed, plugin path, client override

> **Nguồn (official):** https://kafka.apache.org/43/kafka-connect/user-guide/ (mục *Running Kafka Connect*, *Configuring Connectors*, *Plugin Discovery*, *Security*) · https://kafka.apache.org/documentation/#connect
> **Tuần:** 6 — Kafka Connect operations · **Loại:** Apache Kafka Docs 4.3
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) ngày 2026-09-20 — luôn đối chiếu link gốc.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Standalone** = `bin/connect-standalone.sh config/connect-standalone.properties connector1.properties [connector2.properties …]` — **một process**, connector khai bằng **file properties truyền trên dòng lệnh**, offset source lưu **ra file local** `offset.storage.file.filename`. Không HA, không scale. Chỉ dùng cho dev, demo, hoặc edge/agent thu log trên chính máy sinh dữ liệu.
- **Distributed** = `bin/connect-distributed.sh config/connect-distributed.properties` — **không** truyền file connector; connector **chỉ tạo/sửa qua REST 8083**. Đây là chế độ chuẩn production.
- Cả hai chế độ đều bắt buộc: `bootstrap.servers`, `key.converter`, `value.converter`.
- Distributed bắt buộc thêm: `group.id` (**không được trùng với bất kỳ consumer group id nào**), `config.storage.topic`, `offset.storage.topic`, `status.storage.topic`.
- Docs nói thẳng: `config.storage.topic` *"should have a single partition, be replicated, and be configured for compaction"*. Nên **tạo tay 3 internal topic trước** để kiểm soát partition và replication factor thay vì để Connect tự tạo.
- `plugin.path` = danh sách thư mục chứa plugin; mỗi plugin được nạp bằng **classloader riêng** → hai connector dùng hai version thư viện khác nhau không xung đột. Plugin **không** nằm trong `plugin.path` sẽ rơi về classpath chung và mất isolation.
- `plugin.discovery`: `service_load` nhanh nhất nhưng đòi mọi plugin khai `ServiceLoader` manifest; `hybrid_warn` (mặc định) tương thích tất cả. Đổi sang `service_load` phải kiểm plugin trước.
- Sink connector bắt buộc khai **`topics`** (danh sách, phẩy) **hoặc** `topics.regex` (Java regex) — không được khai cả hai.
- Client override theo connector: prefix `producer.override.*`, `consumer.override.*`, `admin.override.*`; mức worker dùng prefix không có `override`: `producer.*`, `consumer.*`, `admin.*`.
- **Bảo mật:** *"Since Kafka 4.2.0, it's recommended to set `connector.client.config.override.policy` to `Allowlist`, this will be the default from Kafka 5.0.0, and explicitly only allow configurations that you need to override."* Lý do: chính sách `All` (mặc định hiện tại) cho phép connector override cả `sasl.jaas.config` → ai POST được connector thì mượn được credential bất kỳ.
- REST API đầy đủ tại 8083, kể cả nhóm offset `GET|PATCH|DELETE /connectors/{name}/offsets`.
- Đặc tả OpenAPI của REST API nằm ở `https://kafka.apache.org/43/generated/connect_rest.yaml`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Running Kafka Connect — standalone mode

Standalone mode executes all work in a single process:

```
bin/connect-standalone.sh config/connect-standalone.properties connector1.properties [connector2.properties ...]
```

"This simpler setup suits single-worker scenarios but lacks fault tolerance features."

The parameter specific to standalone mode is:

- `offset.storage.file.filename` — "File to store source connector offsets" (local file on the worker's disk).

### Running Kafka Connect — distributed mode

```
bin/connect-distributed.sh config/connect-distributed.properties
```

"Distributed Mode … provides automatic work balancing, dynamic scaling, and fault tolerance. Configuration, offsets, and task statuses persist in Kafka topics rather than local files."

Note the difference in how the command line is used: "in distributed mode you do **not** pass connector configuration files on the command line. Instead, use the REST API described below to create, modify, and destroy connectors."

### Configuration parameters both modes need

- `bootstrap.servers` — list of Kafka servers used to bootstrap connections to Kafka.
- `key.converter` — converter class used to convert between Kafka Connect format and the serialized form written to Kafka.
- `value.converter` — same, for values.

### Configuration parameters specific to distributed mode

- `group.id` (default `connect-cluster`) — "unique name for the cluster, used in forming the Connect cluster group; note that this **must not conflict with consumer group IDs**".
- `config.storage.topic` (default `connect-configs`) — "topic to use for storing connector and task configurations; note that this **should be a single partition, highly replicated, compacted topic**. You may need to manually create the topic to ensure the single partition for the config topic, as auto created topics may have multiple partitions."
- `offset.storage.topic` (default `connect-offsets`) — "topic to use for storing offsets; this topic should have many partitions, be replicated, and be configured for compaction."
- `status.storage.topic` (default `connect-statuses`) — "topic to use for storing statuses; this topic can have multiple partitions, and should be replicated and configured for compaction."

"Note that in distributed mode the connector configurations are not passed on the command line. Instead, use the REST API to create, modify, and destroy connectors."

### Configuring Connectors

"Connector configurations are simple key-value mappings." A few are common to all connectors:

- `name` — "Unique name for the connector. Attempting to register again with the same name will fail."
- `connector.class` — "The Java class for the connector." Can be the full class name, the alias without the `Connector` suffix, or the simple class name.
- `tasks.max` — "The maximum number of tasks that should be created for this connector. The connector may create fewer tasks if it cannot achieve this level of parallelism."
- `key.converter` / `value.converter` (optional) — "Override the default key/value converter set by the worker."

Sink connectors additionally take:

- `topics` — "A comma-separated list of topics to use as input for this connector."
- `topics.regex` — "A Java regular expression of topics to use as input for this connector."

"For any other options, you should consult the documentation for the connector."

### Plugin Discovery

"`plugin.path` … a list of paths that contain Connect plugins (connectors, converters, transformations)."

`plugin.discovery` controls how the worker locates plugins:

- `only_scan` — reflection-based scanning only (slowest startup, most compatible).
- `hybrid_warn` — **default** — service loading plus reflection scanning, logs a warning for plugins that are not service-loadable.
- `hybrid_fail` — same as `hybrid_warn`, but fails startup instead of warning.
- `service_load` — service loading only, fastest startup, requires every plugin to be migrated.

"Before enabling `service_load`, verify that all of your plugins are compatible."

### Overriding producer and consumer configurations

Worker-level defaults for the clients Connect creates use the prefixes `producer.` and `consumer.` (and `admin.`).

Per-connector overrides use `producer.override.` and `consumer.override.` (and `admin.override.`) in the **connector** configuration, and are gated by the worker-level `connector.client.config.override.policy`.

### Security

> "Since Kafka 4.2.0, it's recommended to set `connector.client.config.override.policy` to `Allowlist`, this will be the default from Kafka 5.0.0, and explicitly only allow configurations that you need to override."

### Transformations and predicates

Connect ships 15+ single message transformations (`Cast`, `ExtractField`, `Filter`, `Flatten`, `HoistField`, `InsertField`, `MaskField`, `RegexRouter`, `ReplaceField`, `TimestampConverter`, `TimestampRouter`, `ValueToKey`, …) and three predicates, chained through the `transforms` configuration property.

### REST API

Key endpoints exposed on port `8083`: `GET /connectors`, `POST /connectors`, `GET|PUT /connectors/{name}/config`, `GET /connectors/{name}/status`, `PUT /connectors/{name}/pause|stop|resume`, `POST /connectors/{name}/restart`, `DELETE /connectors/{name}`, `GET /connector-plugins`, and the offset endpoints `GET|PATCH|DELETE /connectors/{name}/offsets`. The full machine-readable specification is published at `https://kafka.apache.org/43/generated/connect_rest.yaml`.

### Error handling

Connect supports a dead letter queue through `errors.deadletterqueue.topic.name`. Error tolerance is controlled by `errors.tolerance` (`none` default, `all` to keep going), with optional logging through `errors.log.enable=true` and `errors.log.include.messages=true`.
