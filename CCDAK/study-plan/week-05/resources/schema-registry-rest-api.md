# Schema Registry — REST API Reference (subjects, versions, compatibility, config)

> **Nguồn (official):** https://docs.confluent.io/platform/current/schema-registry/develop/api.html
> **Tuần:** 5 — Schema Registry & Serialization + Kafka Connect · **Loại:** Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Port mặc định **8081**; content type `application/vnd.schemaregistry.v1+json`.
- `GET /subjects` liệt kê subject; `GET /subjects/<s>/versions` liệt kê version (`[1,2,3]`); `GET /subjects/<s>/versions/latest` lấy schema mới nhất (trả `subject`, `id`, `version`, `schema`).
- `POST /subjects/<s>/versions` body `{"schema": "<schema string escaped>", "schemaType": "AVRO|PROTOBUF|JSON"}` → trả `{"id": N}`. **`schemaType` mặc định AVRO** nếu bỏ trống.
- `GET /schemas/ids/<id>` lấy schema theo **ID toàn cục** (chính là ID trong 5 byte wire format).
- `POST /compatibility/subjects/<s>/versions/latest` (hoặc `<version>`) → `{"is_compatible": true|false}` — test **trước** khi đăng ký.
- `GET /config` / `PUT /config` (global) và `GET|PUT|DELETE /config/<subject>` (theo subject; body **`compatibility`**, response trả **`compatibilityLevel`**).
- Mã lỗi: **409** schema không tương thích; **422** schema không hợp lệ (`42201`) hoặc compatibility level sai (`42203`); **404**: `40401` subject không tồn tại, `40402` version không tồn tại, `40403` schema ID không tồn tại.
- `DELETE /subjects/<s>` là **soft delete** (vẫn còn ID, không đăng ký lại được cùng schema với `permanent=true` mới xoá hẳn). `DELETE /subjects/<s>/versions/<v>` xoá 1 version.
- `GET|PUT /mode` : `READWRITE` (mặc định), `READONLY`, `IMPORT` (import schema giữ nguyên ID khi migrate cluster).
- Schema Registry lưu mọi thứ trong topic Kafka **`_schemas`** (1 partition, compacted); nhiều instance chạy **leader/follower** — chỉ leader ghi, follower forward request ghi tới leader.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Overview

The Schema Registry REST server uses content types for both requests and responses to indicate the serialization format and the API version. The recommended content type is:

```
Content-Type: application/vnd.schemaregistry.v1+json
```

All examples below assume Schema Registry is listening on `http://localhost:8081`.

### Schemas

**`GET /schemas/ids/{int: id}`** — Get the schema string identified by the input ID (the same ID that appears in the wire-format prefix).

```bash
curl -s http://localhost:8081/schemas/ids/1
# {"schema":"{\"type\":\"record\",\"name\":\"Order\",...}"}
```

Errors: `40403` Schema not found; `500` / `50001` backend datastore error.

**`GET /schemas/ids/{id}/versions`** — Get the subject-version pairs identified by the input ID.
**`GET /schemas/types`** — Get the schema types that are registered (`AVRO`, `PROTOBUF`, `JSON`).

### Subjects

**`GET /subjects`** — Get a list of registered subjects. Query parameters: `subjectPrefix`, `deleted=true` (include soft-deleted), `deletedOnly`.

```bash
curl -s http://localhost:8081/subjects
# ["orders-value","orders-key","payments-value"]
```

**`GET /subjects/{subject}/versions`** — Get a list of versions registered under the specified subject.

```bash
curl -s http://localhost:8081/subjects/orders-value/versions
# [1,2,3]
```

Errors: `40401` Subject not found.

**`GET /subjects/{subject}/versions/{version}`** — Get a specific version of the schema registered under this subject. `version` may be a positive integer or the string `latest`.

```bash
curl -s http://localhost:8081/subjects/orders-value/versions/latest
# {"subject":"orders-value","version":3,"id":7,"schema":"{...}"}
```

Response fields: `subject`, `id` (globally unique schema ID), `version`, `schemaType` (omitted for AVRO), `schema`. Errors: `40401` subject not found, `40402` version not found, `422`/`42202` invalid version.

**`GET /subjects/{subject}/versions/{version}/schema`** — Get only the schema string (unescaped).

**`POST /subjects/{subject}/versions`** — Register a new schema under the specified subject. If successfully registered, this returns the unique identifier of this schema in the registry. The returned identifier should be used to retrieve this schema from the schema registry and is different from the schema's version, which is associated with the subject. If the same schema is registered under a different subject, the same identifier is returned; however, the version of the schema may be different under different subjects. A schema **should be compatible with the previously registered schema(s)** (if there are any) as per the configured compatibility level.

Request body:

```json
{
  "schema": "{\"type\":\"record\",\"name\":\"Order\",\"fields\":[{\"name\":\"id\",\"type\":\"string\"}]}",
  "schemaType": "AVRO",
  "references": []
}
```

- `schema` (string, required): the schema string, **JSON-escaped**.
- `schemaType` (string): `AVRO` (default), `PROTOBUF`, `JSON`.
- `references` (array): schemas referenced by this schema (`name`, `subject`, `version`).

Response: `{"id": 7}`. Status codes: `200 OK`; `409 Conflict` — incompatible schema (`Schema being registered is incompatible with an earlier schema for subject "orders-value"`); `422` / `42201` — invalid schema; `500` / `50001`, `50002`, `50003` — backend / timeout / leader errors.

```bash
curl -s -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"schema": "{\"type\": \"string\"}"}' \
  http://localhost:8081/subjects/test-value/versions
# {"id":1}
```

**`POST /subjects/{subject}`** — Check if a schema has already been registered under the specified subject; if so, return the schema string along with its globally unique identifier, its version under this subject and the subject name.

**`DELETE /subjects/{subject}`** — Deletes the specified subject and its associated compatibility level if registered. Default is a **soft delete**: versions are hidden but the IDs are kept so that data already written can still be deserialized; add `?permanent=true` (after a soft delete) to hard-delete. Returns the list of deleted versions, e.g. `[1,2,3]`.

**`DELETE /subjects/{subject}/versions/{version}`** — Deletes a specific version of the schema registered under this subject. Also soft by default; `?permanent=true` for hard delete.

### Compatibility

**`POST /compatibility/subjects/{subject}/versions/{version}`** — Test input schema against a particular version of a subject's schema for compatibility. The compatibility level applied is the one configured for the subject, falling back to the global level. `version` can be `latest`. Query `?verbose=true` returns the reasons for incompatibility.

```bash
curl -s -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"schema": "{...new schema...}"}' \
  "http://localhost:8081/compatibility/subjects/orders-value/versions/latest?verbose=true"
# {"is_compatible":false,"messages":["READER_FIELD_MISSING_DEFAULT_VALUE: ..."]}
```

**`POST /compatibility/subjects/{subject}/versions`** — Test against **all** versions (useful with transitive levels).

Errors: `40401`, `40402`, `42201` invalid schema, `42202` invalid version.

### Config

**`GET /config`** — Get global compatibility level.

```bash
curl -s http://localhost:8081/config
# {"compatibilityLevel":"BACKWARD"}
```

**`PUT /config`** — Update global compatibility level. Request body uses the key **`compatibility`**; the response echoes it. Valid values: `NONE`, `BACKWARD`, `BACKWARD_TRANSITIVE`, `FORWARD`, `FORWARD_TRANSITIVE`, `FULL`, `FULL_TRANSITIVE`.

```bash
curl -s -X PUT -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"compatibility": "FULL"}' http://localhost:8081/config
# {"compatibility":"FULL"}
```

Errors: `422` / `42203` invalid compatibility level.

**`GET /config/{subject}`** — Get compatibility level for a subject. Add `?defaultToGlobal=true` to fall back to the global level instead of a `40401`/`40408` error when the subject has no override.

**`PUT /config/{subject}`** — Update compatibility level for the specified subject (overrides the global setting for that subject only).

```bash
curl -s -X PUT -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"compatibility": "FORWARD"}' http://localhost:8081/config/orders-value
```

**`DELETE /config/{subject}`** — Remove the subject-level override; the subject reverts to the global level.

### Mode

**`GET /mode`**, **`PUT /mode`**, **`GET|PUT /mode/{subject}`** — The mode controls whether schemas may be registered: `READWRITE` (default), `READONLY`, `IMPORT` (allows registering schemas with a **specific ID and version**, used when migrating schemas between registries so IDs embedded in existing messages remain valid). `PUT /mode?force=true` overrides an existing check.

### Status codes summary

| Code | Meaning |
|---|---|
| `200` | OK |
| `404` | `40401` Subject not found · `40402` Version not found · `40403` Schema not found · `40408` Subject-level compatibility not configured |
| `409` | **Incompatible schema** (compatibility check failed) |
| `422` | `42201` Invalid schema · `42202` Invalid version · `42203` Invalid compatibility level |
| `500` | `50001` Error in the backend datastore · `50002` Operation timed out · `50003` Error while forwarding the request to the primary |

### Deployment notes (HA)

Schema Registry stores all schemas, subjects and config in the Kafka topic **`_schemas`** (`kafkastore.topic`, 1 partition, `cleanup.policy=compact`). Multiple Schema Registry instances form a cluster with a single **leader** (elected via the Kafka group protocol, `kafkastore.bootstrap.servers` / `schema.registry.group.id`); only the leader performs writes (registrations), while followers serve reads and **forward** write requests to the leader. Because the state is in Kafka, any instance can be restarted and rebuild its cache by replaying `_schemas`.
