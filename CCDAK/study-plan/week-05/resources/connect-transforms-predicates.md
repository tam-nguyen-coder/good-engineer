# Kafka Connect — Single Message Transforms (SMT) & Predicates

> **Nguồn (official):** https://kafka.apache.org/43/generated/connect_transforms.html · https://kafka.apache.org/43/generated/connect_predicates.html · https://docs.confluent.io/platform/current/connect/transforms/overview.html
> **Tuần:** 5 — Schema Registry & Serialization + Kafka Connect · **Loại:** Apache Kafka Docs + Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- SMT = biến đổi **từng record** (stateless, 1-in → 0/1-out) ngay trong Connect: thêm/xoá/đổi tên field, mask, đổi topic đích, lọc. **Không** join/aggregate/window (việc đó là Kafka Streams/ksqlDB).
- Cấu hình: `transforms=a,b,c` (thứ tự = **thứ tự áp dụng**) + `transforms.<alias>.type=<class>` + config riêng `transforms.<alias>.<key>`. Hầu hết class có hậu tố **`$Key`** hoặc **`$Value`** để chọn áp lên key hay value (`InsertField$Value`).
- Vị trí trong pipeline: **Source**: connector → SMT → converter → Kafka. **Sink**: Kafka → converter → SMT → connector. SMT luôn làm việc trên Connect `Struct`/`Map`, không phải bytes.
- Hay hỏi: `InsertField` (thêm `topic.field`, `partition.field`, `offset.field`, `timestamp.field`, `static.field`+`static.value`), `MaskField` (fields → null/`replacement`), `ReplaceField` (`exclude`/`include`/`renames=a:b`), `ExtractField` (lấy 1 field làm cả key/value), `ValueToKey` (tạo key từ field của value), `HoistField`, `Flatten`, `Cast` (`spec=age:int32`), `RegexRouter` (`regex`+`replacement` đổi tên topic), `TimestampRouter` (`topic.format=${topic}-${timestamp}` + `timestamp.format=yyyyMMdd`), `TimestampConverter`, `SetSchemaMetadata`, `Filter`, `InsertHeader`/`DropHeaders`/`HeaderFrom`.
- **Predicate** (2.6+, KIP-585): `predicates=p1` + `predicates.p1.type=...` rồi gắn `transforms.<alias>.predicate=p1` (và `negate=true` để đảo). 3 predicate built-in: `TopicNameMatches` (`pattern`), `HasHeaderKey` (`name`), `RecordIsTombstone`. `Filter` **luôn phải** đi cùng predicate (không có predicate thì lọc mọi record).
- `RegexRouter`/`TimestampRouter` đổi **topic đích**: với source → đổi topic ghi vào Kafka; với sink → đổi tên bảng/index/thư mục đích (ví dụ S3 prefix, Elasticsearch index).
- Bẫy: lỗi trong SMT (ví dụ `Cast` sai kiểu) thuộc **stage transformation** của error handling → `errors.tolerance=all` sẽ **skip record** (sink: ghi DLQ).
- Debezium cung cấp thêm SMT riêng như `ExtractNewRecordState` (unwrap `before/after` envelope) — không phải built-in Apache Kafka.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Transformations

Connectors can be configured with transformations to make **lightweight message-at-a-time modifications**. They can be convenient for data massaging and event routing.

A transformation chain can be specified in the connector configuration:

- `transforms` — List of aliases for the transformation, specifying the **order** in which the transformations will be applied.
- `transforms.$alias.type` — Fully qualified class name for the transformation.
- `transforms.$alias.$transformationSpecificConfig` — Configuration properties for the transformation.

For example, let's take the built-in file source connector and use a transformation to add a static field. Throughout the example we'll use schemaless JSON data format (`value.converter.schemas.enable=false`). Add the following to the connector config:

```properties
name=local-file-source
connector.class=FileStreamSource
tasks.max=1
file=test.txt
topic=connect-test

transforms=MakeMap, InsertSource
transforms.MakeMap.type=org.apache.kafka.connect.transforms.HoistField$Value
transforms.MakeMap.field=line
transforms.InsertSource.type=org.apache.kafka.connect.transforms.InsertField$Value
transforms.InsertSource.static.field=data_source
transforms.InsertSource.static.value=test-file-source
```

Before the transformations the lines produced were plain strings: `"foo"`. `HoistField` wraps each line in a map with a single field `line` (`{"line":"foo"}`); `InsertField` then adds a static field, so the final record is `{"line":"foo","data_source":"test-file-source"}`.

Transformations operate on the Connect data API (`Struct` with `Schema`, or schemaless `Map`), **before** the converter serializes the record (source) or **after** the converter deserializes it (sink).

### Included transformations (org.apache.kafka.connect.transforms.*)

| Transformation | Description | Key configs |
|---|---|---|
| `InsertField` | Insert field(s) using attributes from the record metadata or a configured static value. Use the concrete transformation type designed for the record key (`InsertField$Key`) or value (`InsertField$Value`). | `offset.field`, `partition.field`, `static.field` + `static.value`, `timestamp.field`, `topic.field`. Suffix `!` = required, `?` = optional (e.g. `topic.field=src_topic!`). |
| `ReplaceField` | Filter or rename fields. | `exclude` (fields to drop), `include` (whitelist), `renames` (`old:new,...`). |
| `MaskField` | Mask specified fields with a valid null value for the field type (i.e. `0`, `false`, empty string, and so on) or a custom replacement. For numeric and string fields, an optional replacement value can be specified that is converted to the correct type. | `fields`, `replacement`. |
| `ValueToKey` | Replace the record key with a new key formed from a subset of fields in the record value. | `fields`. |
| `HoistField` | Wrap data using the specified field name in a `Struct` when schema present, or a `Map` in the case of schemaless data. | `field`. |
| `ExtractField` | Extract the specified field from a `Struct` when schema present, or a `Map` in the case of schemaless data. Any null values are passed through unmodified. | `field`, `field.syntax.version` (`V1`/`V2` for nested `a.b.c`). |
| `SetSchemaMetadata` | Set the schema name, version or both on the record's key or value schema. | `schema.name`, `schema.version`. |
| `TimestampRouter` | Update the record's topic field as a function of the original topic value and the record timestamp. This is mainly useful for **sink connectors**, since the topic field is often used to determine the equivalent entity name in the destination system (e.g. database table or search index name). | `topic.format` (default `${topic}-${timestamp}`), `timestamp.format` (default `yyyyMMdd`). |
| `RegexRouter` | Update the record topic using the configured regular expression and replacement string. Under the hood, the regex is compiled to a `java.util.regex.Pattern`. If the pattern matches the input topic, `java.util.regex.Matcher#replaceFirst()` is used with the replacement string to obtain the new topic. | `regex`, `replacement` (e.g. `regex=(.*)`, `replacement=$1-archive`; or `regex=server1\\.public\\.(.*)`, `replacement=$1` to strip a Debezium prefix). |
| `Flatten` | Flatten a nested data structure, generating names for each field by concatenating the field names at each level with a configurable delimiter character. | `delimiter` (default `.`). |
| `Cast` | Cast fields or the entire key or value to a specific type, e.g. to force an integer field to a smaller width. Cast from integers, floats, boolean and string to any other type, and cast binary to string (base64 encoded). | `spec` (`field1:type,field2:type` or a single type for the whole value; types `int8`…`int64`, `float32`, `float64`, `boolean`, `string`). |
| `TimestampConverter` | Convert timestamps between different formats such as Unix epoch, strings, and Connect Date/Timestamp types. | `field`, `target.type` (`string`, `unix`, `Date`, `Time`, `Timestamp`), `format` (SimpleDateFormat), `unix.precision`. |
| `Filter` | Drops all records, filtering them from subsequent transformations in the chain. This is intended to be used **conditionally** to filter out records matching (or not matching) a particular **Predicate**. | none (must be combined with `predicate`). |
| `InsertHeader` | Add a header to each record. | `header`, `value.literal`. |
| `DropHeaders` | Removes one or more headers from each record. | `headers`. |
| `HeaderFrom` | Moves or copies fields in the key/value of a record into that record's headers. | `fields`, `headers`, `operation` (`move`/`copy`). |

Confluent Platform adds further transformations (`Drop`, `ExtractTopic`, `TopicRegexRouter`, `MessageTimestampRouter`, `TombstoneHandler`, `GzipDecompress`, `EventRouter`…), and Debezium ships `io.debezium.transforms.ExtractNewRecordState` (unwraps the CDC envelope so only `after` is emitted).

### Predicates

Transformations can be configured with **predicates** so that the transformation is applied only to messages which satisfy some condition. In particular, when combined with the `Filter` transformation predicates can be used to selectively filter out certain messages.

Predicates are specified in the connector configuration:

- `predicates` — Set of aliases for the predicates to be applied to some of the transformations.
- `predicates.$alias.type` — Fully qualified class name for the predicate.
- `predicates.$alias.$predicateSpecificConfig` — Configuration properties for the predicate.

All transformations have the implicit config properties `predicate` and `negate`. A predicular predicate is associated with a transformation by setting the transformation's `predicate` config to the predicate's alias. The predicate's value can be reversed using the `negate` configuration property.

Example: a source connector produces to many different topics and you want to (1) filter out the records in the `foo` topic entirely and (2) apply `ExtractField` with the field name `other_field` to records in all topics **except** the topic `bar`:

```properties
transforms=Filter,Extract
transforms.Filter.type=org.apache.kafka.connect.transforms.Filter
transforms.Filter.predicate=IsFoo

transforms.Extract.type=org.apache.kafka.connect.transforms.ExtractField$Key
transforms.Extract.field=other_field
transforms.Extract.predicate=IsBar
transforms.Extract.negate=true

predicates=IsFoo,IsBar
predicates.IsFoo.type=org.apache.kafka.connect.transforms.predicates.TopicNameMatches
predicates.IsFoo.pattern=foo

predicates.IsBar.type=org.apache.kafka.connect.transforms.predicates.TopicNameMatches
predicates.IsBar.pattern=bar
```

Included predicates (`org.apache.kafka.connect.transforms.predicates.*`):

| Predicate | Description | Config |
|---|---|---|
| `TopicNameMatches` | A predicate which is true for records with a topic name that matches the configured regular expression. | `pattern` (valid regex, non-empty). |
| `HasHeaderKey` | A predicate which is true for records with at least one header with the configured name. | `name`. |
| `RecordIsTombstone` | A predicate which is true for records which are tombstones (i.e. have **null value**). | none. |

Typical use: drop tombstones before a sink that cannot handle null values —

```properties
transforms=dropTombstones
transforms.dropTombstones.type=org.apache.kafka.connect.transforms.Filter
transforms.dropTombstones.predicate=isTombstone
predicates=isTombstone
predicates.isTombstone.type=org.apache.kafka.connect.transforms.predicates.RecordIsTombstone
```

### Where SMTs sit in the pipeline

```
SOURCE:  external system → SourceTask.poll() → [SMT chain] → Converter (Connect data → bytes) → Kafka topic
SINK:    Kafka topic → Converter (bytes → Connect data) → [SMT chain] → SinkTask.put() → external system
```

Consequences:

- An SMT never sees serialized bytes; a record that the converter cannot deserialize (for example invalid JSON with `JsonConverter`) fails at the **converter** stage, before any SMT runs.
- For a **source** connector, `RegexRouter`/`TimestampRouter` change the Kafka topic the record is written to. For a **sink**, they change the logical destination name the connector derives from the topic (table, index, bucket prefix), because the record has already been read from its Kafka topic.
- Chained transforms are applied strictly in the order of the `transforms` list; if one returns `null` (e.g. `Filter`), the remaining transforms are skipped and the record is dropped.
- SMTs run inside the task thread; heavy logic (external lookups, joins, aggregations) does not belong here — use Kafka Streams / ksqlDB instead.
