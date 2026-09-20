# Kafka Connect — Worker configuration reference (Apache Kafka 4.3)

> **Nguồn (official):** https://kafka.apache.org/43/generated/connect_config.html
> **Tuần:** 6 — Kafka Connect operations · **Loại:** Apache Kafka Docs (bảng config sinh tự động)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) ngày 2026-09-20 — luôn đối chiếu link gốc trước ngày thi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **3 config bắt buộc, không có default** ở distributed worker: `group.id`, `config.storage.topic`, `offset.storage.topic`, `status.storage.topic` (cùng `key.converter` / `value.converter`). Thiếu một cái → worker không khởi động.
- **Partition mặc định của internal topic:** `offset.storage.partitions` = **25**, `status.storage.partitions` = **5**. **Không tồn tại** `config.storage.partitions` — topic config **luôn phải 1 partition** (bắt buộc, không phải mặc định chỉnh được).
- **Replication factor mặc định của cả 3 topic = 3** (`config/offset/status.storage.replication.factor`). Giá trị `-1` = dùng default của broker. Trên cluster lab 1 broker phải hạ xuống **1**, nếu không worker chết khi tạo topic.
- **REST:** `listeners` mặc định **`http://:8083`**. `rest.advertised.host.name` / `rest.advertised.port` / `rest.advertised.listener` mặc định **null** — đây là địa chỉ worker khác dùng để **forward request tới leader**; sai giá trị này thì `POST /connectors` trên worker follower sẽ treo hoặc lỗi.
- **Đồng hồ của Connect group khác consumer group:** `session.timeout.ms` **10000** (consumer là 45000), `heartbeat.interval.ms` **3000**, `rebalance.timeout.ms` **60000**. Đừng chép số của consumer sang worker.
- `scheduled.rebalance.max.delay.ms` mặc định **300000** (5 phút): worker chết → leader **chờ tới 5 phút** trước khi giao lại task của nó, để tránh rebalance vô ích khi worker chỉ restart. Đây là lý do "kill worker xong task không chuyển ngay".
- `connect.protocol` mặc định **`sessioned`** (giá trị hợp lệ `eager`, `compatible`, `sessioned`) → mặc định là **incremental cooperative rebalance** (KIP-415, từ Kafka 2.3).
- `offset.flush.interval.ms` mặc định **60000** (1 phút), `offset.flush.timeout.ms` **5000**. Đây là nhịp commit offset của **source** task; lab thường hạ xuống 10000 để thấy kết quả nhanh.
- `connector.client.config.override.policy` mặc định **`All`** (đổi từ `None` ở Kafka 3.0, KIP-722). Từ **4.2** tài liệu khuyến nghị đặt **`Allowlist`**, và **`Allowlist` sẽ thành mặc định từ 5.0**. Giá trị: `None` / `Principal` / `All` / `Allowlist`.
- `plugin.path` mặc định **null**; `plugin.discovery` mặc định **`hybrid_warn`** (giá trị: `only_scan`, `hybrid_warn`, `hybrid_fail`, `service_load`). `*.plugin.version` (`connector.plugin.version`, `key/value/header.converter.plugin.version`) mặc định **null** → chạy song song nhiều version của cùng một plugin (KIP-891, Kafka **4.1**).
- `exactly.once.source.support` mặc định **`disabled`** (giá trị `disabled` / `preparing` / `enabled`) — bật EOS cho source connector cần **2 pha rolling restart** (`preparing` rồi `enabled`).
- `task.shutdown.graceful.timeout.ms` **5000** — tổng thời gian chờ **tất cả** task tắt êm, không phải mỗi task.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### High-priority worker configurations

| Configuration | Description | Type | Default | Valid Values | Importance |
|---|---|---|---|---|---|
| `group.id` | "A unique string that identifies the Connect cluster group this worker belongs to." | string | (none) | — | high |
| `config.storage.topic` | "The name of the Kafka topic where connector configurations are stored" | string | (none) | — | high |
| `config.storage.replication.factor` | Replication factor for configuration storage topic | short | 3 | Positive number ≤ broker count, or -1 | low |
| `offset.storage.topic` | "The name of the Kafka topic where source connector offsets are stored" | string | (none) | — | high |
| `offset.storage.partitions` | Number of partitions for offset storage topic | int | 25 | Positive number, or -1 | low |
| `offset.storage.replication.factor` | Replication factor for offset storage topic | short | 3 | Positive number ≤ broker count, or -1 | low |
| `status.storage.topic` | "The name of the Kafka topic where connector and task status are stored" | string | (none) | — | high |
| `status.storage.partitions` | Number of partitions for status storage topic | int | 5 | Positive number, or -1 | low |
| `status.storage.replication.factor` | Replication factor for status storage topic | short | 3 | Positive number ≤ broker count, or -1 | low |
| `bootstrap.servers` | Host/port pairs used to establish the initial connection to the Kafka cluster | list | `localhost:9092` | — | high |

### Converters

| Configuration | Description | Type | Default | Importance |
|---|---|---|---|---|
| `key.converter` | "Converter class for key serialization format between Kafka Connect and Kafka" | class | (none) | high |
| `value.converter` | "Converter class for value serialization format between Kafka Connect and Kafka" | class | (none) | high |
| `header.converter` | Converter for header serialization | class | `org.apache.kafka.connect.storage.SimpleHeaderConverter` | low |
| `key.converter.plugin.version` | Version of the key converter | string | null | low |
| `value.converter.plugin.version` | Version of the value converter | string | null | low |
| `header.converter.plugin.version` | Version of the header converter | string | null | low |

### Plugins & runtime

| Configuration | Description | Type | Default | Valid Values | Importance |
|---|---|---|---|---|---|
| `plugin.path` | "List of paths containing plugins (connectors, converters, transformations)" | list | null | — | low |
| `plugin.discovery` | "Method to discover plugins: only_scan, hybrid_warn, hybrid_fail, or service_load" | string | `hybrid_warn` | [ONLY_SCAN, SERVICE_LOAD, HYBRID_WARN, HYBRID_FAIL] | low |
| `connect.protocol` | "Compatibility mode for Kafka Connect Protocol" | string | `sessioned` | [eager, compatible, sessioned] | low |

### Offsets & task management

| Configuration | Description | Type | Default | Importance |
|---|---|---|---|---|
| `offset.flush.interval.ms` | "Interval at which to try committing offsets for tasks." | long | 60000 (1 min) | low |
| `offset.flush.timeout.ms` | "Maximum milliseconds to wait for records to flush and offsets to commit" | long | 5000 (5 sec) | low |
| `task.shutdown.graceful.timeout.ms` | "Time to wait for tasks to shutdown gracefully; total for all tasks" | long | 5000 (5 sec) | low |
| `topic.creation.enable` | "Whether to allow automatic creation of topics used by source connectors" | boolean | true | low |

### REST interface

| Configuration | Description | Type | Default | Importance |
|---|---|---|---|---|
| `listeners` | "List of URIs the REST API will listen on (HTTP/HTTPS)" | list | `http://:8083` | low |
| `rest.advertised.host.name` | "Hostname given out to other workers to connect to" | string | null | low |
| `rest.advertised.port` | "Port given out to other workers to connect to" | int | null | low |
| `rest.advertised.listener` | "Advertised listener (HTTP or HTTPS) for inter-worker communication" | string | null | low |
| `rest.extension.classes` | "Comma-separated ConnectRestExtension class names for custom REST API extensions" | list | "" | low |

### Cluster membership & rebalancing

| Configuration | Description | Type | Default | Valid Values | Importance |
|---|---|---|---|---|---|
| `heartbeat.interval.ms` | "Expected time between heartbeats to group coordinator" | int | 3000 (3 sec) | — | high |
| `session.timeout.ms` | "Timeout for detecting worker failures via heartbeat" | int | 10000 (10 sec) | — | high |
| `rebalance.timeout.ms` | "Maximum time for worker to join group during rebalance" | int | 60000 (1 min) | — | high |
| `worker.sync.timeout.ms` | "Time to wait before giving up on resynchronizing configurations" | int | 3000 (3 sec) | — | medium |
| `worker.unsync.backoff.ms` | "Time to wait before rejoining cluster after sync failure" | int | 300000 (5 min) | — | medium |
| `scheduled.rebalance.max.delay.ms` | "Maximum delay to wait for departed workers before rebalancing" | int | 300000 (5 min) | [0,...,2147483647] | low |

### Exactly-once source & client overrides

| Configuration | Description | Type | Default | Valid Values | Importance |
|---|---|---|---|---|---|
| `exactly.once.source.support` | "Enable exactly-once via transactions and task fencing" | string | `disabled` | [DISABLED, ENABLED, PREPARING] | high |
| `connector.client.config.override.policy` | "Policy class defining which client configs connectors can override" | string | `All` | — | medium |

> Trích **Kafka Connect User Guide 4.3**, mục Security: *"Since Kafka 4.2.0, it's recommended to set `connector.client.config.override.policy` to `Allowlist`, this will be the default from Kafka 5.0.0, and explicitly only allow configurations that you need to override."*

### DNS & metrics

| Configuration | Description | Type | Default | Valid Values | Importance |
|---|---|---|---|---|---|
| `client.dns.lookup` | "DNS lookup strategy" | string | `use_all_dns_ips` | [use_all_dns_ips, resolve_canonical_bootstrap_servers_only] | medium |
| `metric.reporters` | "List of metrics reporter classes" | list | `org.apache.kafka.common.metrics.JmxReporter` | — | low |
| `metrics.num.samples` | "Number of samples to compute metrics" | int | 2 | [1,...] | low |
| `metrics.recording.level` | "Highest metrics recording level: INFO or DEBUG" | string | INFO | [INFO, DEBUG] | low |
| `metrics.sample.window.ms` | "Time window over which metrics samples are computed" | long | 30000 (30 sec) | [0,...] | low |

### Client prefixes worker sử dụng

- `producer.*` — client mà **source** task dùng để ghi vào Kafka, và client ghi **DLQ** của sink task.
- `consumer.*` — client mà **sink** task dùng để đọc từ Kafka (group `connect-<connector-name>`).
- `admin.*` — client tạo internal topic, DLQ topic, và topic do source connector tự tạo (`topic.creation.*`).
- Ở mức **connector**, cùng các prefix đó nhưng thêm `override`: `producer.override.*`, `consumer.override.*`, `admin.override.*` — chỉ có hiệu lực khi `connector.client.config.override.policy` cho phép.
