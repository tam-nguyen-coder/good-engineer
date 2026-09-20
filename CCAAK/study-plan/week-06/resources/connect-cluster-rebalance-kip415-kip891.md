# Connect cluster — worker, task, rebalance (KIP-415) và nhiều version plugin (KIP-891)

> **Nguồn (official):** https://docs.confluent.io/platform/current/connect/concepts.html · https://docs.confluent.io/platform/current/connect/userguide.html · https://cwiki.apache.org/confluence/display/KAFKA/KIP-415 (qua https://kafka-options-explorer.conduktor.io/kip/415/) · https://cwiki.apache.org/confluence/display/KAFKA/KIP-891 · https://kafka.apache.org/43/generated/connect_config.html
> **Tuần:** 6 — Kafka Connect operations · **Loại:** Confluent Docs + KIP
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch) ngày 2026-09-20. **cwiki.apache.org chặn crawl** — phần KIP-415/KIP-891 lấy từ trang mirror Conduktor KIP Explorer + bảng config generated của Kafka 4.3, phần còn lại tổng hợp từ docs. Đối chiếu lại link gốc trước ngày thi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Worker** = JVM process. **Connector** = logic chia việc, **không** copy data. **Task** = thứ copy data thật. Task **không giữ state cục bộ**: state nằm trong `config.storage.topic` và `status.storage.topic` → task chết ở worker này, hồi sinh nguyên vẹn ở worker khác.
- Worker cùng `group.id` **tự tìm nhau qua giao thức group của Kafka** và tạo thành một Connect cluster. Một worker được bầu làm **leader**: leader tính assignment (connector + task → worker) và ghi vào config topic.
- **Quy tắc vàng phân biệt hai loại sự cố:** *"When a worker fails, tasks are rebalanced across the active workers. **When a task fails, no rebalance is triggered, as a task failure is considered an exceptional case.**"* → task FAILED phải **restart bằng tay qua REST**.
- **Rebalance của Connect là incremental cooperative từ Kafka 2.3 (KIP-415)**: chỉ task **cần đổi chủ** mới bị dừng, task còn lại **chạy xuyên suốt** rebalance. Trước 2.3 là eager — dừng toàn bộ mọi task trong cluster mỗi lần có worker vào/ra.
- `connect.protocol` mặc định **`sessioned`** (`eager` / `compatible` / `sessioned`) — `sessioned` là cooperative có thêm xác thực phiên giữa các worker.
- `scheduled.rebalance.max.delay.ms` mặc định **300000 ms (5 phút)**: khi worker rời nhóm, leader **hoãn** việc giao lại task của nó tối đa 5 phút để chờ nó quay lại. Restart worker trong 5 phút → task trở về đúng worker cũ, **không** xáo trộn cluster.
- **`tasks.max` là TRẦN, không phải lệnh.** Docs: *"The maximum number of tasks that should be created for this connector. The connector may create fewer tasks if it cannot achieve this level of parallelism."* Số task thật do connector quyết trong `taskConfigs(maxTasks)`.
- Với **sink** connector, mỗi task là **một consumer** trong consumer group `connect-<connector-name>`. Hầu hết sink connector trả về **đủ** `maxTasks` task → nếu `tasks.max` > số partition thì task dư **RUNNING nhưng không sở hữu partition nào** (`partition-count` = 0). **Công thức `min(tasks.max, partitions)` lan truyền trong tài liệu bên thứ ba là SAI** — nó mô tả số task *có việc*, không phải số task *được tạo*.
- Với **source** connector, số task do đặc thù nguồn quyết định: JDBC source thường 1 task/bảng, FileStream source **luôn đúng 1 task** dù `tasks.max` là bao nhiêu.
- **KIP-891 (Kafka 4.1)** — chạy **nhiều version của cùng một plugin** song song trên một cluster: `connector.plugin.version`, `key.converter.plugin.version`, `value.converter.plugin.version`, `header.converter.plugin.version`, `transforms.<alias>.plugin.version`, `predicates.<alias>.plugin.version`. Cho phép nâng cấp hai pha và rollback từng connector, thay vì phải dựng hai Connect cluster.
- Cài **version mới** vẫn cần restart worker (để nạp JAR), nhưng **migrate từng connector** sang version mới thì không cần restart cluster.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Connectors

"Connectors are high-level abstractions that coordinate data streaming."

- **Source connectors**: "ingest entire databases and stream table updates to Kafka topics"
- **Sink connectors**: "deliver data from Kafka topics to secondary indexes, such as Elasticsearch"

"A connector instance manages copying data between Kafka and another system, while a connector plugin contains the implementing classes."

### Tasks

"Tasks are the primary actors in Connect's data model. Each connector instance coordinates a set of tasks that copy data."

"Tasks enable parallelism without internal state storage — their state lives in Kafka's `config.storage.topic` and `status.storage.topic`."

### Task rebalancing

"When connectors are submitted, workers rebalance tasks so each worker has approximately the same amount of work. Rebalancing also occurs when task counts change or configurations update."

> "**When a worker fails, tasks are rebalanced across the active workers. When a task fails, no rebalance is triggered, as a task failure is considered an exceptional case.**"

### Workers

**Standalone workers**: "A single process is responsible for executing all connectors and tasks." This suits development but offers "limited functionality: scalability is limited to the single process and there is no fault tolerance."

**Distributed workers**: "In distributed mode, you start many worker processes using the same `group.id` and they coordinate to schedule execution of connectors and tasks across all available workers." Workers with identical `group.id` form a cluster and "use consumer groups to coordinate and rebalance."

From the Confluent user guide: "Distributed workers that are configured with matching `group.id` values discover each other and form a Kafka Connect cluster." · "All workers in a Connect cluster use the same internal topics. Workers in a different cluster must use different internal topics." · "The `config.storage` internal topic must always have exactly one partition." · "if a node unexpectedly leaves the cluster, Kafka Connect distributes the work of that node to other nodes in the cluster."

### Converters and transforms

"Converters are required to have a Kafka Connect deployment support a particular data format when writing to, or reading from Kafka."

"The `key.converter` and `value.converter` properties are where you specify the type of converter to use." Per-connector overrides replace the whole converter block: "If a converter is added to a connector configuration, all converter properties in the worker configuration prefixed with the converter type added are not used."

"Connectors can be configured with transformations to make simple and lightweight modifications to individual messages."

### Producer / consumer overrides per connector

"You may need to override default settings" using `producer.*` and `consumer.*` properties at the worker level, or `producer.override.*` and `consumer.override.*` properties in connector configurations. Per-connector overrides allow "different Kafka principal" credentials per connector.

### Shutdown

"Do not use `kill -9` to stop the process" — a graceful shutdown lets tasks flush and commit offsets and lets the worker leave the group cleanly.

### KIP-415 — Incremental Cooperative Rebalancing in Kafka Connect

Shipped in **Kafka 2.3**, status Accepted.

"KIP-415 replaces Kafka Connect's traditional approach with a more efficient model. Rather than the previous method where all task assignments were revoked during rebalancing, the new protocol **only tasks that need to move are stopped and restarted, leaving unaffected tasks running throughout the rebalance**."

Related worker configuration (from `connect_config.html`):

| Config | Default | Notes |
|---|---|---|
| `connect.protocol` | `sessioned` | valid values `eager`, `compatible`, `sessioned` |
| `scheduled.rebalance.max.delay.ms` | `300000` (5 min) | "Maximum delay to wait for departed workers before rebalancing" |
| `rebalance.timeout.ms` | `60000` (1 min) | "Maximum time for worker to join group during rebalance" |
| `session.timeout.ms` | `10000` (10 s) | "Timeout for detecting worker failures via heartbeat" |
| `heartbeat.interval.ms` | `3000` (3 s) | "Expected time between heartbeats to group coordinator" |

### KIP-891 — Running multiple versions of Connector plugins

Shipped in **Kafka 4.1.0**.

"KIP-891 allows Kafka Connect workers to load and run multiple versions of the same connector plugin simultaneously, decoupling connector version installation from migration of individual connector instances."

Motivation: "Without multi-version support, upgrading a connector across all tasks requires a simultaneous cutover with no incremental rollback path, and running two connector versions requires two separate Connect clusters."

"Multiple connector versions makes it possible to do two phase upgrades to connectors with the benefit of easier rollbacks. A connector runtime restart will still be required to install a newer version, however existing connectors can still continue to use the older version. The migration to the newer version is decoupled from the installation of the connector and will not require a cluster restart."

"The KIP allows specifying versions for all plugins in Connector configs (converters, header converters, transforms, and predicates) not just connectors & tasks, and specifies a range of versions instead of an exact match."

Corresponding configuration keys visible in `connect_config.html` / `sink_connector_config.html` / `source_connector_config.html`: `connector.plugin.version`, `key.converter.plugin.version`, `value.converter.plugin.version`, `header.converter.plugin.version` (all default `null`).
