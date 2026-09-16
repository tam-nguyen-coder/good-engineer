# Kafka Connect — Worker/Connector configs, internal topics & REST API

> **Nguồn (official):** https://kafka.apache.org/documentation/#connect (User Guide) · bảng config sinh tự động: https://kafka.apache.org/43/generated/connect_config.html · https://kafka.apache.org/43/generated/sink_connector_config.html · https://kafka.apache.org/43/generated/source_connector_config.html · REST: https://docs.confluent.io/platform/current/connect/references/restapi.html
> **Tuần:** 5 — Schema Registry & Serialization + Kafka Connect · **Loại:** Apache Kafka Docs + Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn; trang `kafka.apache.org/documentation/#connect` render bằng JS nên phần User Guide được lấy từ các trang generated + Confluent tương ứng) — luôn đối chiếu link gốc.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kiến trúc: **Worker** (JVM process) chạy **Connector** (logic chia việc, không copy data) → sinh **Task** (copy data thật). `tasks.max` mặc định **1**; connector quyết định số task thực tế ≤ `tasks.max`.
- **Standalone**: 1 process, offset lưu file `offset.storage.file.filename`, cấu hình connector qua file properties khi khởi động, không HA. **Distributed**: nhiều worker cùng `group.id`, cấu hình qua **REST 8083**, state trong 3 **internal topic compacted**: `config.storage.topic` (**1** partition — bắt buộc), `offset.storage.topic` (mặc định `offset.storage.partitions`=**25**), `status.storage.topic` (`status.storage.partitions`=**5**); RF khuyến nghị **3**.
- **Converter ≠ Serializer**: `key.converter`/`value.converter` (worker-level, connector có thể override) chuyển đổi giữa Connect internal data (Struct/Schema) ↔ bytes trên Kafka. `JsonConverter` với `schemas.enable=true` (mặc định) bọc `{"schema":..., "payload":...}`; tắt để JSON "sạch".
- `plugin.path`: thư mục chứa plugin JAR, mỗi plugin có **class loader riêng** (isolation) → 2 connector dùng 2 version thư viện khác nhau vẫn chạy được.
- REST API: `GET /connectors`, `POST /connectors` (body `{"name","config":{}}`), `PUT /connectors/<n>/config` (**upsert** — tạo mới hoặc cập nhật), `GET /connectors/<n>/status`, `POST /connectors/<n>/restart?includeTasks=true&onlyFailed=true`, `PUT .../pause` | `/resume` | `/stop`, `DELETE /connectors/<n>`, `GET /connectors/<n>/tasks`, `GET /connector-plugins`, `PUT /connector-plugins/<class>/config/validate`, `GET|PATCH|DELETE /connectors/<n>/offsets` (3.6+).
- Trạng thái: `RUNNING`, `PAUSED`, `FAILED`, `STOPPED`, `UNASSIGNED`, `RESTARTING`. **Task FAILED không tự restart** và **không gây rebalance** → phải `POST .../restart?includeTasks=true`. Worker chết → rebalance task sang worker khác (delay tối đa `scheduled.rebalance.max.delay.ms` = **5 phút**, incremental cooperative rebalance `connect.protocol=sessioned`).
- `pause` = giữ task, không poll/put; `stop` (3.5+) = huỷ task, giữ config & offset; `DELETE` = xoá connector nhưng **offset trong `connect-offsets` vẫn còn** (tạo lại cùng tên → tiếp tục từ offset cũ; muốn reset dùng `DELETE /connectors/<n>/offsets` khi đã STOPPED).
- Sink connector dùng **consumer group `connect-<connector-name>`** (offset trong `__consumer_offsets`); source connector tự quản offset (key/value do connector định nghĩa) trong `connect-offsets`.
- `connector.client.config.override.policy` mặc định **`All`** (từ Kafka 3.0, KIP-722; trước đó `None`), giá trị `None`/`Principal`/`All`; connector override client bằng prefix `producer.override.*`, `consumer.override.*`, `admin.override.*`.
- Worker dùng client cho các mục đích: `producer.*` (source ghi), `consumer.*` (sink đọc), `admin.*` (tạo topic, DLQ). `offset.flush.interval.ms` mặc định **60000**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### 8.1 Overview

Kafka Connect is a tool for scalably and reliably streaming data between Apache Kafka and other systems. It makes it simple to quickly define **connectors** that move large collections of data into and out of Kafka. Kafka Connect can ingest entire databases or collect metrics from all your application servers into Kafka topics, making the data available for stream processing with low latency. An export job can deliver data from Kafka topics into secondary storage and query systems or into batch systems for offline analysis.

Kafka Connect features include:

- **A common framework for Kafka connectors** — standardizes integration of other data systems with Kafka, simplifying connector development, deployment, and management.
- **Distributed and standalone modes** — scale up to a large, centrally managed service supporting an entire organization or scale down to development, testing, and small production deployments.
- **REST interface** — submit and manage connectors to your Kafka Connect cluster via an easy to use REST API.
- **Automatic offset management** — with just a little information from connectors, Kafka Connect can manage the offset commit process automatically so connector developers do not need to worry about this error-prone part of connector development.
- **Distributed and scalable by default** — builds on the existing group management protocol; more workers can be added to scale up a Kafka Connect cluster.
- **Streaming/batch integration** — leveraging Kafka's existing capabilities, Kafka Connect is an ideal solution for bridging streaming and batch data systems.

### 8.2 User Guide — Running Kafka Connect

Kafka Connect currently supports two modes of execution: **standalone (single process)** and **distributed**.

In **standalone mode** all work is performed in a single process. This configuration is simpler to set up and get started with and may be useful in situations where only one worker makes sense (e.g. collecting log files), but it does not benefit from some of the features of Kafka Connect such as fault tolerance:

```bash
bin/connect-standalone.sh config/connect-standalone.properties [connector1.properties connector2.properties ...]
```

The first parameter is the configuration for the worker. This includes settings such as the Kafka connection parameters, serialization format, and how frequently to commit offsets. The remaining parameters are connector configuration files. Standalone worker configuration also includes `offset.storage.file.filename` — the file to store source connector offsets (must be unique per standalone worker on the same host).

**Distributed mode** handles automatic balancing of work, allows you to scale up (or down) dynamically, and offers fault tolerance both in the active tasks and for configuration and offset commit data:

```bash
bin/connect-distributed.sh config/connect-distributed.properties
```

The difference is in the class which is started and the configuration parameters which change how the Kafka Connect process decides where to store configurations, how to assign work, and where to store offsets and task statuses. In the distributed mode, Kafka Connect stores the offsets, configs and task statuses in Kafka topics. It is recommended to manually create the topics for offset, configs and statuses in order to achieve the desired number of partitions and replication factors. If the topics are not yet created when starting Kafka Connect, the topics will be auto created with default number of partitions and replication factor, which may not be best suited for its usage.

In particular, the following configuration parameters, in addition to the common settings mentioned above, are critical to set before starting your cluster:

- `group.id` (default `connect-cluster`) — unique name for the cluster, used in forming the Connect cluster group; note that this **must not conflict** with consumer group IDs.
- `config.storage.topic` (default `connect-configs`) — topic to use for storing connector and task configurations; this should be a **single partition**, highly replicated, **compacted** topic. You may need to manually create the topic to ensure single partition since auto created topics may have multiple partitions or be automatically configured for deletion rather than compaction.
- `offset.storage.topic` (default `connect-offsets`) — topic to use for storing offsets; this topic should have **many partitions**, be replicated, and be configured for **compaction**.
- `status.storage.topic` (default `connect-status`) — topic to use for storing statuses; this topic can have multiple partitions, and should be replicated and configured for compaction.

Note that in distributed mode the connector configurations are **not passed on the command line**. Instead, use the REST API described below to create, modify, and destroy connectors.

#### Worker configuration (selected, Kafka 4.3 generated docs)

| Name | Default | Description |
|---|---|---|
| `bootstrap.servers` | `localhost:9092` | A list of host/port pairs used to establish the initial connection to the Kafka cluster. |
| `group.id` | — (required, distributed) | A unique string that identifies the Connect cluster group this worker belongs to. |
| `key.converter` / `value.converter` | — (required) | Converter class used to convert between Kafka Connect format and the serialized form that is written to Kafka. This controls the format of the keys/values in messages written to or read from Kafka, and since this is independent of connectors it allows any connector to work with any serialization format. Examples: `JsonConverter`, `AvroConverter`, `StringConverter`, `ByteArrayConverter`. |
| `header.converter` | `org.apache.kafka.connect.storage.SimpleHeaderConverter` | HeaderConverter class used to convert between Kafka Connect format and the serialized form for header values. |
| `config.storage.topic` | — | The name of the Kafka topic where connector configurations are stored. |
| `config.storage.replication.factor` | `3` | Replication factor used when creating the configuration storage topic. |
| `offset.storage.topic` | — | The name of the Kafka topic where source connector offsets are stored. |
| `offset.storage.partitions` | **`25`** | The number of partitions used when creating the offset storage topic. |
| `offset.storage.replication.factor` | `3` | Replication factor used when creating the offset storage topic. |
| `status.storage.topic` | — | The name of the Kafka topic where connector and task status are stored. |
| `status.storage.partitions` | **`5`** | The number of partitions used when creating the status storage topic. |
| `status.storage.replication.factor` | `3` | Replication factor used when creating the status storage topic. |
| `offset.flush.interval.ms` | `60000` | Interval at which to try committing offsets for tasks. |
| `offset.flush.timeout.ms` | `5000` | Maximum number of milliseconds to wait for records to flush and partition offset data to be committed to offset storage before cancelling the process and restoring the offset data to be committed in a future attempt. |
| `plugin.path` | `null` | List of paths separated by commas (`,`) that contain plugins (connectors, converters, transformations). Each path is a directory of plugin JARs (or a plugin directory with its dependencies). Plugins are loaded in isolation from each other. |
| `plugin.discovery` | `hybrid_warn` | Method to use to discover plugins: `only_scan`, `hybrid_warn`, `hybrid_fail`, `service_load` (ServiceLoader manifests, fastest). |
| `listeners` | `http://:8083` | List of comma-separated URIs the REST API will listen on. |
| `rest.advertised.host.name` / `rest.advertised.port` | `null` | Hostname/port given out to other workers to connect to (used to forward requests to the leader worker). |
| `connector.client.config.override.policy` | **`All`** | Class name or alias of implementation of `ConnectorClientConfigOverridePolicy`. Defines what client configurations can be overridden by the connector. The default implementation is `All`, meaning connector configurations can override all client properties. Other possible policies are `None` to disallow any overrides and `Principal` to allow overriding only principal-related (security) properties. |
| `exactly.once.source.support` | `disabled` | Whether to enable exactly-once support for source connectors in the cluster by using transactions to write source records and their source offsets, and by proactively fencing out old task generations before bringing up new ones. Values: `disabled`, `preparing`, `enabled`. |
| `task.shutdown.graceful.timeout.ms` | `5000` | Amount of time to wait for tasks to shutdown gracefully. |
| `scheduled.rebalance.max.delay.ms` | `300000` | The maximum delay that is scheduled in order to wait for the return of one or more departed workers before rebalancing and reassigning their connectors and tasks to the group. |
| `connect.protocol` | `sessioned` | Compatibility mode for Kafka Connect Protocol (`eager`, `compatible`, `sessioned` = incremental cooperative rebalancing with session keys). |
| `heartbeat.interval.ms` / `session.timeout.ms` / `rebalance.timeout.ms` | `3000` / `10000` / `60000` | Group membership timeouts of the worker itself in the Connect group. |

Producer/consumer/admin clients used by the worker can be configured with the prefixes `producer.`, `consumer.` and `admin.` (e.g. `producer.compression.type=lz4`, `consumer.max.poll.records=100`).

#### Connector configuration

Connector configurations are simple key-value mappings. In both standalone and distributed mode, they are included in the JSON payload for the REST request that creates (or modifies) the connector. In standalone mode these can also be defined in a properties file and passed to the Connect process on the command line.

Most configurations are connector dependent, so they cannot be outlined here. However, there are a few common options:

| Name | Default | Description |
|---|---|---|
| `name` | — | Globally unique name to use for this connector. |
| `connector.class` | — | The Java class for the connector. Name or alias of the class (e.g. `FileStreamSink`, `FileStreamSinkConnector`, `org.apache.kafka.connect.file.FileStreamSinkConnector`). |
| `tasks.max` | `1` | The maximum number of tasks that should be created for this connector. The connector may create fewer tasks if it cannot achieve this level of parallelism. |
| `key.converter` / `value.converter` / `header.converter` | `null` (inherit worker) | Optional — override the default key/value/header converter set by the worker. |
| `transforms` | `""` | Aliases for the transformations to be applied to records (chain, applied in the order listed). |
| `predicates` | `""` | Aliases for the predicates used by transformations. |
| `config.action.reload` | `restart` | The action that Connect should take on the connector when changes in external configuration providers result in a change in the connector's configuration properties (`none`, `restart`). |
| `errors.*` | see error-handling resource | Error tolerance, retries, logging and (sink only) dead letter queue. |

**Sink** connectors also have a few additional options to control their input. Each sink connector must set one of the following: `topics` (a comma-separated list of topics to use as input) or `topics.regex` (a Java regular expression of topics to use as input).

**Source** connectors (Kafka 2.6+) can define `topic.creation.groups` / `topic.creation.default.partitions` / `topic.creation.default.replication.factor` so the worker creates output topics with specific settings; exactly-once related: `exactly.once.support` (`requested`/`required`), `transaction.boundary` (`poll`/`interval`/`connector`), `transaction.boundary.interval.ms`, `offsets.storage.topic`.

Example (distributed, JSON):

```json
{
  "name": "orders-s3-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "4",
    "topics": "orders",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://schema-registry:8081",
    "transforms": "addTs",
    "transforms.addTs.type": "org.apache.kafka.connect.transforms.InsertField$Value",
    "transforms.addTs.timestamp.field": "ingested_at",
    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "dlq-orders-s3",
    "errors.deadletterqueue.context.headers.enable": "true",
    "consumer.override.max.poll.records": "200"
  }
}
```

#### Overriding producer/consumer settings per connector

By default, connectors inherit the worker's `producer.*` and `consumer.*` settings. Since Kafka 2.3 (KIP-458) a connector may override client settings with the prefixes **`producer.override.`** (source connectors), **`consumer.override.`** (sink connectors) and **`admin.override.`** (DLQ producer / topic creation). Which properties may be overridden is controlled by the worker's `connector.client.config.override.policy`: `None` (nothing), `Principal` (only security/`sasl.*`/`ssl.*`, so each connector can run under its own identity), `All` (default since 3.0 — anything). If a connector requests a disallowed override, its creation is rejected with an error at validation time.

### 8.2 REST API

Since Kafka Connect is intended to be run as a service, it also provides a REST API for managing connectors. By default, this service runs on port **8083**. When executed in distributed mode, the REST API will be the primary interface to the cluster. You can make requests to any cluster member; the REST API automatically forwards requests to the leader if required. Content type is `application/json`.

| Method + path | Description |
|---|---|
| `GET /` | Top-level: worker version, commit, `kafka_cluster_id`. |
| `GET /connectors` | Return a list of active connectors. `?expand=status`, `?expand=info` return status/info for each. |
| `POST /connectors` | Create a new connector; the request body should be a JSON object containing a string `name` field and an object `config` field with the connector configuration parameters. Returns `201 Created`; `409 Conflict` if a rebalance is in progress or a connector with the same name exists. |
| `GET /connectors/{name}` | Get information about a specific connector (config + tasks). |
| `GET /connectors/{name}/config` | Get the configuration parameters for a specific connector. |
| `PUT /connectors/{name}/config` | Create a new connector using the given configuration, or **update the configuration for an existing connector** (idempotent upsert). Body is just the config object. Returns `201` on create, `200` on update. |
| `GET /connectors/{name}/status` | Get current status of the connector, including whether it is running, failed, paused, etc., which worker it is assigned to, error information if it has failed, and the state of all its tasks. |
| `POST /connectors/{name}/restart?includeTasks=<true|false>&onlyFailed=<true|false>` | Restart a connector and its tasks instances. `includeTasks` (default `false`) also restarts the task instances; `onlyFailed` (default `false`) restarts only instances with a `FAILED` status. Returns `202 Accepted`; `409` during rebalance. |
| `PUT /connectors/{name}/pause` | Pause the connector and its tasks, which stops message processing until the connector is resumed. Any resources claimed by its tasks are left allocated. |
| `PUT /connectors/{name}/stop` | (3.5+) Stop the connector and shut down its tasks, deallocating any resources claimed by its tasks. Config and offsets are retained; required before altering/resetting offsets. |
| `PUT /connectors/{name}/resume` | Resume a paused or stopped connector (or do nothing if the connector is not paused/stopped). |
| `DELETE /connectors/{name}` | Delete a connector, halting all tasks and deleting its configuration. `204 No Content`. **Offsets are not deleted.** |
| `GET /connectors/{name}/tasks` | Get a list of tasks currently running for a connector, with their configs. |
| `GET /connectors/{name}/tasks/{taskId}/status` | Get current status of the task, including if it is running, failed, paused, etc., which worker it is assigned to, and error information if it has failed. |
| `POST /connectors/{name}/tasks/{taskId}/restart` | Restart an individual task (typically because it has failed). |
| `GET /connectors/{name}/topics` | (2.5+) Get the set of topic names the connector has used since it was created or since a request to reset its set of active topics. `PUT /connectors/{name}/topics/reset` resets the set. |
| `GET /connectors/{name}/offsets` | (3.5+) Get the current offsets for a connector (source: connector-defined partition/offset maps; sink: Kafka topic-partition offsets of its consumer group). |
| `PATCH /connectors/{name}/offsets` | (3.6+) Alter the offsets for a connector — connector must be in `STOPPED` state. |
| `DELETE /connectors/{name}/offsets` | (3.6+) Reset the offsets for a connector — connector must be in `STOPPED` state. |
| `GET /connector-plugins` | Return a list of connector plugins installed in the Kafka Connect cluster (class, type, version). Note that the API only checks for connectors on the worker that handles the request, which means you may see inconsistent results, especially during a rolling upgrade if you add new connector jars. `?connectorsOnly=false` also lists converters, transformations, predicates. |
| `GET /connector-plugins/{plugin-type}/config` | (3.2+) Get the configuration definition for the specified plugin. |
| `PUT /connector-plugins/{connector-type}/config/validate` | Validate the provided configuration values against the configuration definition. This API performs per-config validation, returns suggested values and error messages during validation. |
| `GET /admin/loggers` · `GET|PUT /admin/loggers/{logger}` | (2.4+) List / change log levels at runtime, e.g. `{"level": "DEBUG"}`. `?scope=cluster` (3.7+) applies to all workers. |

Example status response:

```json
{
  "name": "orders-s3-sink",
  "connector": { "state": "RUNNING", "worker_id": "connect-1:8083" },
  "tasks": [
    { "id": 0, "state": "RUNNING", "worker_id": "connect-1:8083" },
    { "id": 1, "state": "FAILED",  "worker_id": "connect-2:8083",
      "trace": "org.apache.kafka.connect.errors.ConnectException: ..." }
  ],
  "type": "sink"
}
```

Connector and task states: `UNASSIGNED` (not yet assigned to a worker), `RUNNING`, `PAUSED` (administratively paused), `STOPPED` (connector only, 3.5+), `FAILED` (usually because an exception was raised — check `trace`), `RESTARTING` (in the process of restarting). Note: a failed task is **not** automatically restarted and does **not** trigger a rebalance; use the restart endpoint. When a connector is paused, in-flight tasks finish their current batch; paused state is persisted in `status.storage.topic` and survives worker restarts.

### Task rebalancing

When a connector is first submitted to the cluster, the workers rebalance the full set of connectors in the cluster and their tasks so that each worker has approximately the same amount of work. This rebalancing procedure is also used when connectors increase or decrease the number of tasks they require, or when a connector's configuration is changed. When a worker fails, tasks are rebalanced across the active workers. When a task fails, no rebalance is triggered as a task failure is considered an exceptional case. As such, failed tasks are not automatically restarted by the framework and should be restarted via the REST API. Since Kafka 2.3 (KIP-415) Connect uses **incremental cooperative rebalancing** (`connect.protocol=compatible|sessioned`): only the affected connectors/tasks are revoked and reassigned, and a departed worker's tasks are held for up to `scheduled.rebalance.max.delay.ms` (5 min) to allow it to return before reassignment.

### Plugin isolation

Each plugin directory under `plugin.path` is loaded by its own class loader, so connectors that bundle conflicting versions of the same library (for example two different Jackson or HTTP client versions) do not interfere. The Connect framework classes and the converters shipped with Kafka (`JsonConverter`, `StringConverter`, `ByteArrayConverter`) are always available; third-party converters (`AvroConverter`, `ProtobufConverter`) and transformations must be present on `plugin.path` (or the classpath) of **every** worker. In the `apache/kafka` Docker image the FileStream connectors live in `/opt/kafka/libs/connect-file-<version>.jar` and, since Kafka 3.2, are no longer on the default classpath — add that directory to `plugin.path` to use them.
