# Kafka Connect 101 (Confluent Developer) — Course overview & converters

> **Nguồn (official):** https://developer.confluent.io/courses/kafka-connect/intro/ · module converters: https://developer.confluent.io/courses/kafka-connect/connectors-configuration-converters-transforms/ · concepts: https://docs.confluent.io/platform/current/connect/concepts.html
> **Tuần:** 5 — Schema Registry & Serialization + Kafka Connect · **Loại:** Confluent Developer course + Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kafka Connect = framework **tích hợp bằng cấu hình, không viết code** giữa Kafka và hệ ngoài; chạy **process riêng** (worker), không nằm trong broker.
- **Source** = ngoài → Kafka (JDBC source, Debezium, S3 source, MQTT); **Sink** = Kafka → ngoài (JDBC sink, S3 sink, Elasticsearch, HTTP sink, Snowflake).
- **Converter** là **ranh giới Connect ↔ Kafka**: cùng converter dùng cho mọi connector; đặt ở worker, override ở connector. Danh sách: `AvroConverter`, `ProtobufConverter`, `JsonSchemaConverter` (cần `schema.registry.url`), `JsonConverter` (`schemas.enable` mặc định **true** → envelope `schema`+`payload`), `StringConverter`, `ByteArrayConverter` (pass-through, không schema).
- Bẫy kinh điển: sink dùng `JsonConverter` với `schemas.enable=true` đọc JSON "trần" → lỗi **`JsonConverter with schemas.enable requires "schema" and "payload" fields`** → sửa: `value.converter.schemas.enable=false` (nhưng sink cần schema như JDBC sẽ không chạy) hoặc dùng Avro + Schema Registry.
- Bẫy 2: topic ghi bằng Avro (`KafkaAvroSerializer`) nhưng sink dùng `JsonConverter` → lỗi parse (**byte đầu là magic 0x00**); ngược lại topic JSON mà dùng `AvroConverter` → `Unknown magic byte!`.
- **Serializer** (producer/consumer app) ≠ **Converter** (Connect) — 2 API khác nhau nhưng **cùng wire format** khi cùng dùng Avro Schema Registry → interoperable.
- Converter được cấu hình **riêng cho key và value** (`key.converter` thường `StringConverter`, `value.converter` Avro/JSON).
- Task failed **không** tự restart; worker failed → task **chuyển** sang worker khác. Nhiều worker cùng `group.id` = 1 cluster Connect.
- Deployment: self-managed (standalone/distributed, Docker/K8s với Strimzi/Confluent for Kubernetes) hoặc **fully managed** (Confluent Cloud connectors, `Amazon MSK Connect`).
- Monitoring: REST `/status`, JMX metrics `kafka.connect:type=connector-task-metrics` (`status`, `batch-size-avg`), `sink-record-lag`… (tuần 8).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### What is Kafka Connect?

Kafka Connect is the component of Apache Kafka that provides **streaming integration between Kafka and other systems** — databases, cloud services, search indexes, file systems, and key-value stores. It runs in its own process, separate from the Kafka brokers, and is distributed, scalable and fault tolerant. Best of all, it is **configuration-based**: you do not write code to move data; you configure a connector.

Ingest data from upstream systems into Kafka with **source connectors**; write data from Kafka topics to downstream systems with **sink connectors**. Hundreds of connectors exist (Confluent Hub), covering relational databases (JDBC, Debezium CDC for MySQL/PostgreSQL/SQL Server/MongoDB/Oracle), object stores (Amazon S3, GCS, Azure Blob), data warehouses (Snowflake, BigQuery, Redshift), search (Elasticsearch/OpenSearch), messaging (JMS, MQTT, ActiveMQ), SaaS (Salesforce, ServiceNow), and generic HTTP.

### Workers, connectors and tasks

- A **worker** is the JVM process that runs Connect. Workers form a cluster by sharing a `group.id`.
- A **connector** instance is a logical job: it knows how to split the copy work into tasks (for example, a JDBC source connector assigns tables to tasks) but does not itself copy data.
- A **task** is the unit of parallelism that actually copies data. `tasks.max` is the upper bound; the connector decides how many tasks to create (Debezium PostgreSQL always creates 1).
- Tasks have no state of their own: configuration, offsets and status live in Kafka (internal topics), so a task can be moved to another worker and resume.

### Task rebalancing

When a connector is first submitted to the cluster, the workers rebalance the full set of connectors and their tasks so that each worker has approximately the same amount of work. This same rebalancing procedure is also used when connectors increase or decrease the number of tasks they require, or when a connector's configuration is changed. When a worker fails, tasks are rebalanced across the active workers. When a task fails, no rebalance is triggered as a task failure is considered an exceptional case; failed tasks are not automatically restarted by the framework and should be restarted via the REST API.

### Converters

Converters are necessary to have a Kafka Connect deployment support a particular data format when writing to, or reading from, Kafka. Tasks use converters to change the format of data from **bytes to a Connect internal data format** (a `Struct` with a `Schema`, or a schemaless `Map`) and vice versa.

Confluent Platform provides the following converters:

| Converter | Class | Needs Schema Registry | Notes |
|---|---|---|---|
| Avro | `io.confluent.connect.avro.AvroConverter` | **Yes** (`<key|value>.converter.schema.registry.url`) | Compact binary, full schema evolution; the standard choice. |
| Protobuf | `io.confluent.connect.protobuf.ProtobufConverter` | Yes | Strong typing, cross-language. |
| JSON Schema | `io.confluent.connect.json.JsonSchemaConverter` | Yes | JSON payload validated by a registered JSON Schema. |
| JSON | `org.apache.kafka.connect.json.JsonConverter` | No | Ships with Apache Kafka. `schemas.enable` (default **true**) embeds the schema in every message as `{"schema": {...}, "payload": {...}}`; set `false` for plain JSON (then no schema is available to sinks that need one). |
| String | `org.apache.kafka.connect.storage.StringConverter` | No | Treats key/value as a UTF-8 string; common for keys. |
| ByteArray | `org.apache.kafka.connect.converters.ByteArrayConverter` | No | Pass-through raw bytes, no schema, no transformation of content (e.g. archive topics verbatim to S3, or MirrorMaker 2). |
| Primitives | `DoubleConverter`, `FloatConverter`, `IntegerConverter`, `LongConverter`, `ShortConverter` | No | Numeric keys/values. |

Converters are decoupled from connectors themselves to allow for the **reuse** of converters between connectors naturally. For example, using the same Avro converter, the JDBC Source Connector can write Avro data to Kafka, and the HDFS Sink Connector can read Avro data from Kafka. This means the same converter can be used even though, for example, the JDBC source returns a `ResultSet` that is eventually written to HDFS as a Parquet file.

Configuration is per **key** and **value** (and header via `header.converter`):

```properties
key.converter=org.apache.kafka.connect.storage.StringConverter
value.converter=io.confluent.connect.avro.AvroConverter
value.converter.schema.registry.url=http://schema-registry:8081
```

Set the defaults at the **worker** level; any connector may **override** them in its own config (useful when one topic is JSON and another is Avro on the same cluster).

#### Converter vs serializer

An application producer uses a **serializer** (`KafkaAvroSerializer`) and a consumer uses a **deserializer**; Kafka Connect uses a **converter**, which is bidirectional and works with Connect's internal `Struct`/`Schema` types. They are different Java interfaces, but when both use the Confluent Avro implementation they read and write the **same wire format** (magic byte + schema ID + Avro payload) and register schemas under the same `TopicNameStrategy` subjects, so a Java/Node application and a Connect sink are fully interoperable on the same topic.

#### Common converter errors

| Symptom | Cause | Fix |
|---|---|---|
| `org.apache.kafka.connect.errors.DataException: JsonConverter with schemas.enable requires "schema" and "payload" fields and may not contain additional fields` | Sink reads plain JSON but `value.converter.schemas.enable=true` (default). | Set `value.converter.schemas.enable=false`, or produce with the envelope, or switch to Avro + Schema Registry. |
| `Unknown magic byte!` (`SerializationException`) | `AvroConverter` reading a topic that is **not** Avro/Schema-Registry encoded (plain JSON/String). | Use `JsonConverter`/`StringConverter` for that topic (or fix the producer). |
| `Converting byte[] to Kafka Connect data failed due to serialization error` / `Unrecognized token` | `JsonConverter` reading Avro bytes (first byte `0x00`). | Use `AvroConverter` + `schema.registry.url`. |
| Sink requires a schema (`Sink connector 'x' is configured with 'delete.enabled=false' and 'pk.mode=none' and therefore requires records with a non-null Struct value and non-null Struct schema`) | JDBC/other schema-aware sink fed by schemaless JSON. | Use Avro/Protobuf/JSON Schema converter, or `schemas.enable=true` envelope. |

### Single Message Transforms

SMTs are stateless, per-record functions configured on a connector (`transforms=...`) for light massaging: insert/mask/rename/drop fields, change the destination topic, cast types, filter with predicates. They run after the source connector produces a record (before conversion) or after the sink converter deserializes it (before `put()`). Anything stateful — joins, aggregations, windowing, enrichment against another topic — belongs in Kafka Streams or ksqlDB, not in an SMT.

### Deployment models

| Model | Where it runs | Notes |
|---|---|---|
| Standalone | Single worker process, connector configs on the command line, offsets in a local file | Dev/test, edge log collection; no fault tolerance. |
| Distributed (self-managed) | N workers with the same `group.id`, REST API on 8083, state in `connect-configs/offsets/status` | Production self-managed; on Kubernetes via Strimzi / Confluent for Kubernetes. |
| Fully managed | Confluent Cloud connectors, `Amazon MSK Connect` | No workers to run; configure via UI/API/CLI; custom plugins supported on MSK Connect. |

### Course modules (Kafka Connect 101)

1. **Introduction to Kafka Connect** — why integration without code; sources vs sinks.
2. **Hands On: Getting Started** — Confluent Cloud connector walkthrough.
3. **Running Kafka Connect** — workers, connectors, tasks; standalone vs distributed; internal topics.
4. **Connectors, Configuration, Converters, and Transforms** — anatomy of a connector config; converter choice; SMT basics.
5. **Hands On: Use SMTs with a Managed Connector** — `InsertField`, `MaskField`, routing.
6. **Confluent Cloud Managed Connector API / CLI** — programmatic management (recognition).
7. **Deployment** — sizing, workers per cluster, separating Connect clusters per team.
8. **Running Kafka Connect in Docker** — `cp-kafka-connect` image, installing plugins with `confluent-hub install`.
9. **Hands On: Self-Managed Connector in Docker** — Debezium / JDBC examples.
10. **Kafka Connect's REST API** — create/update/status/pause/resume/restart/delete.
11. **Monitoring Kafka Connect** — status endpoint, JMX metrics, Confluent Control Center.
12. **Errors and Dead Letter Queues** — `errors.tolerance`, DLQ headers, when to use `all`.
13. **Troubleshooting Kafka Connect** — reading task `trace`, log levels via `/admin/loggers`, converter mismatches, plugin path issues.
