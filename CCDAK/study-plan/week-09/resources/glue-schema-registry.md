# AWS Glue Schema Registry — schemas, registries, compatibility modes, quotas (so với Confluent Schema Registry)

> **Nguồn (official):** https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html
> **Tuần:** 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `AWS Glue Schema Registry` = schema registry **serverless, miễn phí**, tích hợp `Apache Kafka`/`Amazon MSK`, `Kinesis Data Streams`, `Managed Service for Apache Flink`, `Lambda` (ESM decode), `Kafka Connect`, `Kafka Streams`. Format: **Avro** (1.11.x), **JSON Schema** (Draft-04/06/07, validate bằng Everit), **Protobuf** (proto2/proto3, không hỗ trợ `extensions`/`groups`). Serde lib Java open-source `aws-glue-schema-registry` (`software.amazon.glue:schema-registry-serde`), config `AWSKafkaAvroSerializer`/`AWSKafkaAvroDeserializer`, `registry.name`, `schemaAutoRegistrationEnabled`, tuỳ chọn **ZLIB compression**.
- Phân cấp: **Registry** (container có ARN → gắn IAM policy) → **Schema** (DataFormat, Compatibility, `SchemaCheckpoint`) → **SchemaVersion** (số tăng dần, status) → **SchemaVersionMetadata** (≤ 10 key-value/version).
- **8 compatibility mode**: `NONE`, `DISABLED` (khoá version mới), `BACKWARD` (**mặc định & khuyến nghị**: consumer mới đọc data cũ — được xoá field / thêm field optional), `BACKWARD_ALL`, `FORWARD` (consumer cũ đọc data mới — được thêm field / xoá field optional), `FORWARD_ALL`, `FULL`, `FULL_ALL`. So với Confluent: `*_ALL` ≈ `*_TRANSITIVE`; Glue kiểm tra theo **checkpoint version** (đổi bằng `UpdateSchema`), Confluent theo version trước.
- Wire format khác Confluent: Glue header = **1 byte version(3) + 1 byte compression + 16 byte schema version UUID** (18 byte) vs Confluent **1 byte magic + 4 byte schema ID** (5 byte). Producer/consumer **không đọc lẫn nhau** giữa 2 registry nếu không có converter.
- Quota: **100 registry/region**, **10.000 schema version/region/account**, schema payload ≤ **170 KB**, 10 metadata pair/version.
- IAM: `glue:GetSchemaVersion`, `glue:GetSchemaByDefinition`, `glue:RegisterSchemaVersion`, `glue:CreateSchema` (auto-registration), `glue:GetRegistry`; Lambda ESM dùng `glue:GetRegistry` + `glue:GetSchemaVersion`.
- Bẫy: "cần schema registry cho MSK, không muốn trả tiền/quản server" ⇒ Glue SR (không cần chạy container `cp-schema-registry`). "Kafka Streams/Confluent tooling, subject naming strategy, REST API tương thích Confluent" ⇒ Confluent SR (Glue **không** có REST API tương thích Confluent).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### AWS Glue Schema Registry

The AWS Glue Schema Registry allows you to centrally discover, control, and evolve data stream schemas. A *schema* defines the structure and format of a data record. With AWS Glue Schema Registry, you can manage and enforce schemas on your data streaming applications using convenient integrations with **Apache Kafka, Amazon Managed Streaming for Apache Kafka, Amazon Kinesis Data Streams, Amazon Managed Service for Apache Flink, and AWS Lambda**.

The Schema Registry supports **AVRO (v1.11.4)** data format, **JSON** data format with JSON Schema format for the schema (specifications Draft-04, Draft-06, and Draft-07) with JSON schema validation using the Everit library, **Protocol Buffers (Protobuf)** versions proto2 and proto3 without support for `extensions` or `groups`, and Java language support. Supported features include compatibility, schema sourcing via metadata, auto-registration of schemas, IAM compatibility, and optional **ZLIB compression** to reduce storage and data transfer. **The Schema Registry is serverless and free to use.**

Using a schema as a data format contract between producers and consumers leads to improved data governance, higher quality data, and enables data consumers to be resilient to compatible upstream changes. The Schema Registry supplies a serializer and deserializer for certain systems such as Amazon MSK or Apache Kafka.

### Schemas

A *schema* defines the structure and format of a data record. A schema is a versioned specification for reliable data publication, consumption, or storage. Example Avro schema:

```json
{
  "type": "record",
  "namespace": "ABC_Organization",
  "name": "Employee",
  "fields": [
    { "name": "Name", "type": "string" },
    { "name": "Age", "type": "int" },
    { "name": "address", "type": { "type": "record", "name": "addressRecord",
        "fields": [ { "name": "street", "type": "string" }, { "name": "zipcode", "type": "int" } ] } }
  ]
}
```

### Registries

A *registry* is a logical container of schemas. Registries allow you to organize your schemas, as well as manage access control for your applications. A registry has an Amazon Resource Name (ARN) to allow you to organize and set different access permissions to schema operations within the registry. You may use the default registry or create as many new registries as necessary.

**AWS Glue Schema Registry hierarchy:**

- **Registry**: RegistryName, RegistryArn, CreatedTime, UpdatedTime
  - **Schema**: SchemaName, SchemaArn, DataFormat [Avro, Json, or Protobuf], Compatibility [BACKWARD, BACKWARD_ALL, FORWARD, FORWARD_ALL, FULL, FULL_ALL, NONE, DISABLED], Status [PENDING, AVAILABLE, DELETING], SchemaCheckpoint [integer]
    - **SchemaVersion**: SchemaVersionNumber, Status [PENDING, AVAILABLE, DELETING, FAILURE], SchemaDefinition
      - **SchemaVersionMetadata**: MetadataKey, MetadataValue

### Schema versioning and compatibility

Each schema can have multiple versions. Versioning is governed by a compatibility rule that is applied on a schema. Requests to register new schema versions are checked against this rule by the Schema Registry before they can succeed.

A schema version that is marked as a **checkpoint** is used to determine the compatibility of registering new versions of a schema. When a schema first gets created the default checkpoint will be the first version. You can use the CLI/SDK to change the checkpoint using the `UpdateSchema` API. In the console, editing the schema definition or compatibility mode will change the checkpoint to the latest version by default.

There are **8 compatibility modes**: NONE, DISABLED, BACKWARD, BACKWARD_ALL, FORWARD, FORWARD_ALL, FULL, FULL_ALL.

- **NONE**: No compatibility mode applies. Any new version added will be accepted without undergoing a compatibility check.
- **DISABLED**: Prevents versioning for a particular schema. No new versions can be added.
- **BACKWARD**: **Recommended** because it allows consumers to read both the current and the previous schema version. Use this to check compatibility against the previous schema version when you **delete fields or add optional fields**. A typical use case is when your application has been created for the most recent schema.
  - *Avro example:* schema with first name (required), last name (required), email (required), phone number (optional). Removing the required `email` field registers successfully (consumers ignore the extra field in old messages). Adding a **required** `zip code` field fails (new consumers cannot read old messages missing it); adding it as **optional** succeeds.
  - *JSON example:* adding an optional property registers only if the original schema sets `additionalProperties: false`.
  - *Protobuf / gRPC:* adding a new RPC method is backward compatible; removing an existing RPC method is not.
- **BACKWARD_ALL**: Allows consumers to read both the current and **all previous** schema versions.
- **FORWARD**: Allows consumers to read both the current and the subsequent schema versions. Use this when you **add fields or delete optional fields**. A typical use case is when your application has been created for a previous schema and should be able to process a more recent schema.
  - *Avro example:* adding a required `phone number` field registers successfully; deleting a **required** `first name` field fails (old consumers need it); deleting an optional field succeeds.
- **FORWARD_ALL**: Consumers can read data written by producers of any new registered schema; checks against all previous versions.
- **FULL**: Consumers can read data written with the previous **or** next version of the schema. Use when you **add or remove optional fields**.
- **FULL_ALL**: Consumers can read data written by producers using all previous schema versions.

In the Avro data format, fields may be optional or required. An optional field is one in which the `Type` includes null. In Protobuf, fields can be optional (including repeated) or required in proto2 syntax, while all fields are optional in proto3 syntax.

### Open source Serde libraries

AWS provides open-source Serde libraries as a framework for serializing and deserializing data (GitHub `awslabs/aws-glue-schema-registry`). Kafka producer configuration example (Java):

```
key.serializer=org.apache.kafka.common.serialization.StringSerializer
value.serializer=com.amazonaws.services.schemaregistry.serializers.GlueSchemaRegistryKafkaSerializer
region=us-east-1
registry.name=orders-registry
dataFormat=AVRO
schemaAutoRegistrationEnabled=true
compatibility=BACKWARD
compression=ZLIB
```

The serializer registers/looks up the schema, then writes the record as: **version byte (3) + compression byte + 16-byte schema version UUID + payload**. The consumer uses `GlueSchemaRegistryKafkaDeserializer` to fetch the schema version by UUID (cached) and decode.

### Quotas of the Schema Registry

Soft limits:

- **Schema version metadata key-value pairs** — up to **10 key-value pairs per SchemaVersion** per AWS Region.

Hard limits:

- **Registries** — up to **100 registries per AWS Region** for this account.
- **SchemaVersion** — up to **10000 schema versions per AWS Region** for this account. Each new schema creates a new schema version, so you can theoretically have up to 10000 schemas per account per region, if each schema has only one version.
- **Schema payloads** — size limit of **170 KB**.

### Glue Schema Registry vs Confluent Schema Registry (tổng hợp từ docs, không nằm trong trang crawl)

| | AWS Glue Schema Registry | Confluent Schema Registry |
| --- | --- | --- |
| Hosting / cost | Serverless, free | Self-host container (8081) or Confluent Cloud (paid) |
| Formats | Avro, JSON Schema, Protobuf | Avro, JSON Schema, Protobuf |
| Compatibility | 8 modes incl. `*_ALL`, checked vs checkpoint | 7 modes incl. `*_TRANSITIVE` (default BACKWARD) |
| Wire format | 18-byte header (version, compression, UUID) | 5-byte header (magic 0 + 4-byte ID) |
| Naming | Registry / schema name (free-form) | Subject naming strategies (`TopicNameStrategy`...) |
| Auth | IAM | Basic auth / mTLS / RBAC |
| Integrations | MSK, Kinesis, Flink, Lambda ESM, Connect, Streams | Kafka ecosystem, Connect converters, ksqlDB, Streams serdes |
| REST API | AWS API (`glue:*`), no Confluent-compatible REST | Confluent REST API (`/subjects`, `/schemas/ids`) |
