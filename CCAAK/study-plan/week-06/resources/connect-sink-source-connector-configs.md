# Connector configuration — sink vs source (Apache Kafka 4.3)

> **Nguồn (official):** https://kafka.apache.org/43/generated/sink_connector_config.html · https://kafka.apache.org/43/generated/source_connector_config.html
> **Tuần:** 6 — Kafka Connect operations · **Loại:** Apache Kafka Docs (bảng config sinh tự động)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch) ngày 2026-09-20 — luôn đối chiếu link gốc.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **`tasks.max` mặc định `1`** cho cả sink và source, kiểu `int`, valid `[1,...]`. Mô tả chính thức: *"Maximum number of tasks to use for this connector"* — **maximum**, không phải exact.
- `tasks.max.enforce` (**deprecated**, mặc định `true`): buộc runtime từ chối khi connector sinh nhiều task hơn `tasks.max`. Nó chặn *vượt trần*, **không** ép connector tạo đủ trần.
- **Khác biệt lớn nhất giữa hai bảng: `errors.deadletterqueue.*` CHỈ có ở sink.** Bảng source connector **không có** bất kỳ config DLQ nào. Đây là câu hỏi lặp lại trong đề.
- DLQ: `errors.deadletterqueue.topic.name` mặc định `""` (rỗng = tắt) · `errors.deadletterqueue.topic.replication.factor` mặc định **3** · `errors.deadletterqueue.context.headers.enable` mặc định **false**.
- Bẫy RF: DLQ RF mặc định **3**. Trên cluster 1 broker phải đặt `errors.deadletterqueue.topic.replication.factor=1`, nếu không task FAILED ngay khi tạo DLQ topic.
- `errors.tolerance` mặc định **`none`** (`none` / `all`): *"'none' signals any error causes immediate task failure; 'all' skips problematic records."* Đặt `all` **mà không** khai DLQ = **nuốt record im lặng**.
- `errors.log.enable` mặc định **false**, `errors.log.include.messages` mặc định **false** → mặc định log **không** chứa nội dung record hỏng. Bật `include.messages` là quyết định có yếu tố **bảo mật/PII**.
- `errors.retry.timeout` mặc định **0** (không retry), `errors.retry.delay.max.ms` mặc định **60000**. Đặt `errors.retry.timeout=-1` = retry vô hạn.
- `config.action.reload` mặc định **`restart`** (`none` / `restart`): khi config ngoại vi (vd file chứa secret) đổi, Connect tự restart task.
- Chỉ **source** có `exactly.once.support` (mặc định `requested`, giá trị `REQUIRED`/`REQUESTED`), `transaction.boundary` (mặc định `poll`, giá trị `POLL`/`INTERVAL`/`CONNECTOR`), `transaction.boundary.interval.ms` (mặc định `null`), `offsets.storage.topic` (offset topic **riêng cho một connector**) và `topic.creation.groups`.
- Chỉ **sink** có `topics` và `topics.regex` (đều mặc định `""`) — khai đúng **một trong hai**.
- Cả hai đều có `*.plugin.version` (mặc định `null`) từ KIP-891 để ghim version plugin.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Sink connector configurations

| Configuration | Description | Type | Default | Valid Values |
|---|---|---|---|---|
| `name` | "Globally unique name to use for this connector." | string | (none) | non-empty string without ISO control characters |
| `connector.class` | "Name or alias of the class for this connector. Must be a subclass of org.apache.kafka.connect.connector.Connector." | string | (none) | — |
| `connector.plugin.version` | "Version of the connector." | string | null | PluginVersionValidator |
| `tasks.max` | "Maximum number of tasks to use for this connector." | int | 1 | [1,...] |
| `topics` | "List of topics to consume, separated by commas" | list | "" | — |
| `topics.regex` | "Regular expression giving topics to consume. Under the hood, the regex is compiled to a `java.util.regex.Pattern`." | string | "" | valid regex |
| `tasks.max.enforce` | "(Deprecated) Whether to enforce that the tasks.max property is respected by the connector." | boolean | true | — |
| `key.converter` | "Converter class used to convert between Kafka Connect format and serialized form written to Kafka." | class | null | Concrete subclass of `org.apache.kafka.connect.storage.Converter` |
| `value.converter` | "Converter class for values in messages written to or read from Kafka." | class | null | Concrete subclass of `Converter` |
| `header.converter` | "HeaderConverter class for converting header values in messages." | class | null | Concrete subclass of `HeaderConverter` |
| `config.action.reload` | "The action that Connect should take when external configuration changes occur." | string | restart | [none, restart] |
| `transforms` | "Aliases for the transformations to be applied to records." | list | "" | non-null string, unique transformation aliases |
| `predicates` | "Aliases for the predicates used by transformations." | list | "" | non-null string, unique predicate aliases |
| `errors.retry.timeout` | "The maximum duration in milliseconds that a failed operation will be reattempted." | long | 0 | — |
| `errors.retry.delay.max.ms` | "The maximum duration in milliseconds between consecutive retry attempts." | long | 60000 (1 minute) | — |
| `errors.tolerance` | "'none' signals any error causes immediate task failure; 'all' skips problematic records." | string | none | [none, all] |
| `errors.log.enable` | "If true, write each error and failed operation details to the Connect application log." | boolean | false | — |
| `errors.log.include.messages` | "Whether to include in the log the Connect record that resulted in a failure." | boolean | false | — |
| `errors.deadletterqueue.topic.name` | "The name of the topic to be used as the dead letter queue (DLQ) for error messages." | string | "" | — |
| `errors.deadletterqueue.topic.replication.factor` | "Replication factor used to create the dead letter queue topic when absent." | short | 3 | — |
| `errors.deadletterqueue.context.headers.enable` | "If true, add headers containing error context to messages written to the dead letter queue." | boolean | false | — |

### Source connector configurations

| Configuration | Type | Default | Valid Values | Description |
|---|---|---|---|---|
| `name` | string | (none) | non-empty string without ISO control characters | "Globally unique name to use for this connector" |
| `connector.class` | string | (none) | Subclass of `org.apache.kafka.connect.connector.Connector` | "Name or alias of the class for this connector" |
| `connector.plugin.version` | string | null | PluginVersionValidator | Version of the connector |
| `tasks.max` | int | 1 | [1,...] | "Maximum number of tasks to use for this connector" |
| `tasks.max.enforce` | boolean | true | — | Deprecated property controlling task limit enforcement |
| `key.converter` | class | null | Converter subclass with public no-arg constructor | "Converter class used to convert between Kafka Connect format and serialized form" |
| `key.converter.plugin.version` | string | null | PluginVersionValidator | Version of the key converter |
| `value.converter` | class | null | Converter subclass with public no-arg constructor | "Converter class used to convert between Kafka Connect format and serialized form" |
| `value.converter.plugin.version` | string | null | PluginVersionValidator | Version of the value converter |
| `header.converter` | class | null | HeaderConverter subclass with public no-arg constructor | "HeaderConverter class used to convert between Kafka Connect format" |
| `header.converter.plugin.version` | string | null | PluginVersionValidator | Version of the header converter |
| `config.action.reload` | string | restart | [none, restart] | "Action Connect should take when external configuration changes" |
| `transforms` | list | "" | non-null string, unique aliases | "Aliases for the transformations to be applied to records" |
| `predicates` | list | "" | non-null string, unique aliases | "Aliases for the predicates used by transformations" |
| `errors.retry.timeout` | long | 0 | — | "Maximum duration in milliseconds that a failed operation will be reattempted" |
| `errors.retry.delay.max.ms` | long | 60000 | — | "Maximum duration in milliseconds between consecutive retry attempts" |
| `errors.tolerance` | string | none | [none, all] | "Behavior for tolerating errors during connector operation" |
| `errors.log.enable` | boolean | false | — | "If true, write each error and details of failed operation to log" |
| `errors.log.include.messages` | boolean | false | — | "Whether to include the Connect record that resulted in failure" |
| `topic.creation.groups` | list | "" | non-null string, unique groups | "Groups of configurations for topics created by source connectors" |
| `exactly.once.support` | string | requested | [REQUIRED, REQUESTED] | "Permits preflight validation that connector provides exactly-once semantics" |
| `transaction.boundary` | string | poll | [INTERVAL, POLL, CONNECTOR] | "Determines when producer transactions are started and committed" |
| `transaction.boundary.interval.ms` | long | null | [0,...] | "Interval for producer transaction commits when boundary is 'interval'" |
| `offsets.storage.topic` | string | null | non-empty string | "Name of a separate offsets topic to use for this connector" |

> 📌 **Xác nhận trực tiếp từ trang generated:** bảng source connector **không có** `errors.deadletterqueue.topic.name`, `errors.deadletterqueue.topic.replication.factor` hay `errors.deadletterqueue.context.headers.enable`. DLQ là tính năng **chỉ của sink connector**.

### Side-by-side: what only ONE of the two has

| Configuration | Sink | Source | Notes |
|---|---|---|---|
| `topics` / `topics.regex` | ✅ | — | A sink declares exactly one of the two; both default to `""` |
| `errors.deadletterqueue.topic.name` | ✅ | — | Empty string = DLQ disabled |
| `errors.deadletterqueue.topic.replication.factor` | ✅ | — | Default **3** — the topic is created on demand with this RF |
| `errors.deadletterqueue.context.headers.enable` | ✅ | — | Default **false** |
| `exactly.once.support` | — | ✅ | `requested` (default) or `required`; preflight validation only |
| `transaction.boundary` | — | ✅ | `poll` (default), `interval`, `connector` |
| `transaction.boundary.interval.ms` | — | ✅ | Default `null`; used only when the boundary is `interval` |
| `offsets.storage.topic` | — | ✅ | Per-connector offsets topic, overriding the worker's `offset.storage.topic` |
| `topic.creation.groups` | — | ✅ | Groups of settings for topics the source connector creates itself |

### Shared by both

`name`, `connector.class`, `connector.plugin.version`, `tasks.max`, `tasks.max.enforce`, `key.converter`, `value.converter`, `header.converter` (plus each converter's `*.plugin.version`), `config.action.reload`, `transforms`, `predicates`, `errors.retry.timeout`, `errors.retry.delay.max.ms`, `errors.tolerance`, `errors.log.enable`, `errors.log.include.messages`.

### Reading the `tasks.max` wording carefully

The generated documentation string is "**Maximum** number of tasks to use for this connector", type `int`, default `1`, valid values `[1,...]`. The runtime passes this number to the connector as `taskConfigs(maxTasks)` and uses whatever list of task configurations the connector returns.

`tasks.max.enforce` — marked **(Deprecated)**, default `true` — makes the runtime reject a connector that returns *more* configurations than the maximum. Nothing in either configuration table forces a connector to return *fewer* than the maximum when the input topic has fewer partitions, which is why a sink connector with `tasks.max=6` on a 3-partition topic normally ends up with six tasks and three empty assignments.
