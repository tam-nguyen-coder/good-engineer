# Schema Registry — Schema Evolution & Compatibility Types

> **Nguồn (official):** https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
> **Tuần:** 5 — Schema Registry & Serialization + Kafka Connect · **Loại:** Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Mặc định compatibility = **`BACKWARD`**: consumer dùng **schema mới** đọc được data ghi bằng **schema cũ**. Được phép: **xoá field**, **thêm field có default**. Thứ tự nâng cấp: **consumer trước**, producer sau.
- **`FORWARD`**: consumer dùng **schema cũ** đọc được data ghi bằng **schema mới**. Được phép: **thêm field**, **xoá field có default**. Thứ tự: **producer trước**.
- **`FULL`** = cả hai → chỉ được **thêm/xoá field CÓ default**. Nâng cấp thứ tự tuỳ ý.
- **`*_TRANSITIVE`**: kiểm tra với **tất cả** version trước, không chỉ version liền kề (X-2 ↔ X). Non-transitive chỉ so với version **mới nhất**.
- **`NONE`**: không kiểm tra — mọi thay đổi (kể cả đổi type, đổi tên record) đều đăng ký được → phải nâng cấp đồng thời, rất rủi ro.
- Vi phạm compatibility khi `POST /subjects/<s>/versions` → **HTTP 409 Conflict** với thông báo `Schema being registered is incompatible with an earlier schema`.
- Set compatibility toàn cục `PUT /config` body `{"compatibility": "FULL"}`; theo subject `PUT /config/<subject>`. Subject-level **ưu tiên** hơn global.
- Avro: field optional = union có `null` (`["null","string"]`, `"default": null`); **thêm field bắt buộc phải có `default`** để backward; `aliases` cho phép đổi tên field/record mà vẫn đọc được data cũ.
- Kafka Streams **chỉ hỗ trợ BACKWARD** (app Streams đọc cả input topic và state store/changelog nên phải nâng cấp trước).
- Rewind/replay topic (đọc lại data cũ) là lý do BACKWARD được chọn làm mặc định.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Schema evolution

An important aspect of data management is schema evolution. After the initial schema is defined, applications may need to evolve it over time. When this happens, it is critical for downstream consumers to be able to handle data encoded with both the old and the new schema seamlessly. Schema Registry allows you to define **compatibility rules** per subject; when a producer (or a CI process) registers a new version, Schema Registry checks it against the existing version(s) and **rejects** it (HTTP 409) if it violates the rule.

### Compatibility types

| Compatibility type | Changes allowed | Check is against which schemas | Upgrade first |
|---|---|---|---|
| `BACKWARD` (**default**) | Delete fields · Add **optional** fields (fields with a default value) | Last version | **Consumers** |
| `BACKWARD_TRANSITIVE` | Delete fields · Add optional fields | **All previous** versions | Consumers |
| `FORWARD` | Add fields · Delete **optional** fields | Last version | **Producers** |
| `FORWARD_TRANSITIVE` | Add fields · Delete optional fields | All previous versions | Producers |
| `FULL` | Add optional fields · Delete optional fields | Last version | **Any order** |
| `FULL_TRANSITIVE` | Add optional fields · Delete optional fields | All previous versions | Any order |
| `NONE` | All changes are accepted | Compatibility checking disabled | Depends (usually requires a new topic or simultaneous upgrade) |

### Backward compatibility

`BACKWARD` compatibility means that **consumers using the new schema can read data produced with the last schema**. For example, if there are three schemas for a subject that change in order X-2, X-1, and X, then BACKWARD compatibility ensures that consumers using the new schema X can process data written by producers using schema X or X-1, but not necessarily X-2. `BACKWARD_TRANSITIVE` extends this to all previous versions.

Allowed changes: **delete fields** and **add optional fields** (with a default). A consumer with the new schema that encounters old data missing a new field uses the field's default; old data that contains a deleted field simply ignores it.

Upgrade order: **upgrade all consumers first**, then producers. BACKWARD is the default because it fits Kafka's common pattern of consumers re-reading (rewinding) a topic that contains data written with older schemas.

### Forward compatibility

`FORWARD` compatibility means that **data produced with a new schema can be read by consumers using the last schema**, even though they may not be able to use the full capabilities of the new schema. Allowed changes: **add fields** and **delete optional fields**. A consumer on the old schema ignores the new field; if a field it expects was deleted, it must have had a default so the reader can fill it in.

Upgrade order: **upgrade producers first**, then consumers.

### Full compatibility

`FULL` compatibility means schemas are **both backward and forward compatible**: old data can be read with the new schema and new data can be read with the old schema. Allowed changes: **add optional fields** and **delete optional fields** only. Producers and consumers can be upgraded independently in any order.

### No compatibility checking

`NONE` disables compatibility checks. Any schema is accepted — for example changing a field's type from `string` to `int`, or renaming the record. This is sometimes used in development or when a topic is being re-created from scratch, but in production it typically means old and new data cannot be read by the same consumer; a common practice is to write the new format to a **new topic** instead.

### Summary of allowed changes (Avro / Protobuf)

| Change | BACKWARD | FORWARD | FULL |
|---|---|---|---|
| Add optional field (with default) | ✔ | ✔ | ✔ |
| Remove optional field (with default) | ✔ | ✔ | ✔ |
| Add required field (no default) | ✘ | ✔ | ✘ |
| Remove required field (no default) | ✔ | ✘ | ✘ |
| Add union / oneof variant | ✘ | ✔ | ✘ |
| Remove union / oneof variant | ✔ | ✘ | ✘ |
| Widen scalar type (int → long) | ✘* | ✔ | ✘ |
| Narrow scalar type (long → int) | ✔* | ✘ | ✘ |
| Rename field without alias | ✘ | ✘ | ✘ |
| Change field type (string → int) | ✘ | ✘ | ✘ |

*Type promotion in Avro follows the Avro resolution rules (int → long → float → double, string ↔ bytes); the reader schema decides. In practice avoid type changes; add a new field instead.

### Transitive vs non-transitive

Non-transitive types (`BACKWARD`, `FORWARD`, `FULL`) compare the new schema only with the **latest registered version**. Transitive types (`*_TRANSITIVE`) compare it with **all previously registered versions**. Example: version 1 has field `a`; version 2 deletes `a` (BACKWARD OK); version 3 re-adds `a` as required without a default. With `BACKWARD`, version 3 is compared only to version 2 (which has no `a`) → the check is about adding a required field → **rejected**. But other sequences can pass non-transitive checks while a consumer on version 3 cannot read version 1 data; `BACKWARD_TRANSITIVE` closes that gap at the cost of stricter evolution.

### Setting compatibility

Global (applies to subjects without their own setting):

```bash
curl -X PUT -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"compatibility": "BACKWARD"}' http://localhost:8081/config
```

Per subject (overrides global):

```bash
curl -X PUT -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"compatibility": "FULL_TRANSITIVE"}' http://localhost:8081/config/orders-value
```

Test before registering:

```bash
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"schema": "{...}"}' \
  http://localhost:8081/compatibility/subjects/orders-value/versions/latest
# → {"is_compatible": false}
```

Schema Registry server-wide default is set by `schema.compatibility.level` in `schema-registry.properties` (default `backward`).

### Avro-specific rules

- A field is optional when it has a **default value**. To allow `null`, use a union with `null` first and `"default": null`:
  `{"name": "email", "type": ["null", "string"], "default": null}`
- Adding a field **without** a default is a **backward-incompatible** change (a consumer on the new schema cannot construct the field from old data).
- Deleting a field is backward compatible; it is forward compatible only if the field had a default in the old schema.
- **`aliases`**: renaming a field or record is normally incompatible, but an alias on the new schema (`"aliases": ["oldName"]`) lets the reader map old data to the new name.
- Changing the **record name** or **namespace** without aliases is incompatible.
- Enum: adding a symbol is forward compatible; the reader must have a `default` symbol for it to be backward compatible.

### Kafka Streams

For Kafka Streams applications, **only BACKWARD compatibility is supported** because a Streams application reads both its input topics and its own internal (state store changelog, repartition) topics that may contain data written with older schemas. Upgrade the Streams application (consumer) before upstream producers.

### Order of upgrading clients — summary

| Compatibility | Upgrade order |
|---|---|
| `BACKWARD`, `BACKWARD_TRANSITIVE` | Consumers first |
| `FORWARD`, `FORWARD_TRANSITIVE` | Producers first |
| `FULL`, `FULL_TRANSITIVE` | Any order |
| `NONE` | No guarantee; coordinate manually |
