# Schema Registry — Wire format, Serializer/Deserializer & Subject Name Strategy

> **Nguồn (official):** https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html
> **Tuần:** 5 — Schema Registry & Serialization + Kafka Connect · **Loại:** Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Wire format = 5 byte overhead**: byte 0 là **magic byte = 0**, byte 1–4 là **schema ID int32 big-endian**, phần còn lại là payload (Avro binary / Protobuf / JSON). Protobuf chèn thêm **message indexes** (zigzag varint, thường là 1 byte `0`) trước payload.
- Consumer **không dùng** `KafkaAvroDeserializer` (ví dụ `kafka-console-consumer.sh` thường) sẽ đọc được **5 byte đầu là ký tự lạ/garbage** rồi payload nhị phân → dấu hiệu "record được ghi bằng Schema Registry serializer".
- Serializer/Deserializer: Avro `io.confluent.kafka.serializers.KafkaAvroSerializer` / `KafkaAvroDeserializer`; Protobuf `...protobuf.KafkaProtobufSerializer`; JSON Schema `...json.KafkaJsonSchemaSerializer`.
- Config bắt buộc: `schema.registry.url`. `auto.register.schemas` mặc định **true** (dev tiện, **production nên tắt** để CI/CD đăng ký schema có kiểm soát). `use.latest.version=false` mặc định (chỉ có ý nghĩa khi `auto.register.schemas=false`). `latest.compatibility.strict=true` mặc định.
- `specific.avro.reader=true` → deserialize ra class Avro sinh sẵn (SpecificRecord) thay vì `GenericRecord`.
- **Subject naming strategy**: `TopicNameStrategy` (mặc định) → subject `<topic>-key` / `<topic>-value`, **1 topic = 1 loại schema**; `RecordNameStrategy` → subject = tên record đầy đủ (nhiều event type trong 1 topic, compatibility check **xuyên mọi topic** cùng record); `TopicRecordNameStrategy` → `<topic>-<recordName>` (nhiều event type trong 1 topic nhưng compatibility **theo từng topic**).
- Config chọn strategy: `key.subject.name.strategy` / `value.subject.name.strategy` (đặt trên producer/consumer/converter).
- Schema ID là **duy nhất toàn cụm Schema Registry** (global), **version** chỉ có ý nghĩa **trong 1 subject**; cùng 1 schema đăng ký ở 2 subject → **cùng ID**, version có thể khác.
- Serializer **cache** schema ID theo schema string → chỉ gọi REST lần đầu; deserializer cache schema theo ID.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Wire Format

Schema Registry serializers and deserializers use a wire format that includes information about the schema ID at the beginning of the payload. Most users can ignore the details, but this matters if you need to work with the raw bytes (custom serializer, debugging with console tools, or a client in a language without a Schema Registry library).

| Bytes | Area | Description |
|---|---|---|
| Byte 0 | Magic Byte | Confluent serialization format version number; currently always **0**. |
| Bytes 1–4 | Schema ID | **4-byte schema ID** as returned by Schema Registry (int32, big-endian / network byte order). |
| Bytes 5–x | Message indexes | **Protobuf only**: an array of indexes that identifies the message type within the `.proto` file (zigzag varint encoded). The common case, the first message type in the schema, is optimized to a single `0` byte. Empty for Avro and JSON Schema. |
| Bytes x+1… | Data | Serialized data in the format-specific encoding (Avro binary encoding, Protobuf binary, JSON UTF-8). |

Because of this prefix, a plain consumer (for example `kafka-console-consumer` without the Avro formatter) prints a few unreadable bytes at the start of every record: the magic byte, the schema ID, then binary Avro data.

### Serializer and Deserializer classes

| Format | Producer (serializer) | Consumer (deserializer) |
|---|---|---|
| Avro | `io.confluent.kafka.serializers.KafkaAvroSerializer` | `io.confluent.kafka.serializers.KafkaAvroDeserializer` |
| Protobuf | `io.confluent.kafka.serializers.protobuf.KafkaProtobufSerializer` | `io.confluent.kafka.serializers.protobuf.KafkaProtobufDeserializer` |
| JSON Schema | `io.confluent.kafka.serializers.json.KafkaJsonSchemaSerializer` | `io.confluent.kafka.serializers.json.KafkaJsonSchemaDeserializer` |

For Kafka Connect the equivalent converters are `io.confluent.connect.avro.AvroConverter`, `io.confluent.connect.protobuf.ProtobufConverter`, `io.confluent.connect.json.JsonSchemaConverter`. For Kafka Streams, use the Serdes `GenericAvroSerde` / `SpecificAvroSerde` (`io.confluent.kafka.streams.serdes.avro`).

Example producer configuration (Java):

```java
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);
props.put("schema.registry.url", "http://localhost:8081");
props.put("auto.register.schemas", false);   // recommended in production
props.put("use.latest.version", true);
```

Example consumer configuration:

```java
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaAvroDeserializer.class);
props.put("schema.registry.url", "http://localhost:8081");
props.put("specific.avro.reader", true);     // return generated SpecificRecord classes
```

### Core configuration properties

| Property | Default | Description |
|---|---|---|
| `schema.registry.url` | — (required) | Comma-separated list of Schema Registry URLs. |
| `auto.register.schemas` | `true` | Whether the serializer should attempt to register the schema with Schema Registry during serialization. Disable in production so that schemas are registered through a controlled process (CI/CD, Maven/Gradle plugin) and a producer with an unexpected schema fails fast instead of silently registering it. |
| `use.latest.version` | `false` | Only used when `auto.register.schemas=false`. If `true`, the serializer looks up the **latest** schema version in the subject and uses it for serialization (instead of looking up the exact schema of the object). Useful for schemas with references / union of event types. |
| `latest.compatibility.strict` | `true` | Only used when `use.latest.version=true`. Checks that the latest subject version is backward compatible with the schema of the object being serialized; if not, an error is thrown. |
| `normalize.schemas` | `false` | Normalize schemas during registration and lookup so semantically equivalent schemas (different whitespace/field ordering) are treated as the same. |
| `use.schema.id` | — | Use a specific schema ID for serialization (pins the schema). |
| `specific.avro.reader` | `false` | (Deserializer, Avro) If `true`, deserialize into generated `SpecificRecord` classes instead of `GenericRecord`. |
| `key.subject.name.strategy` / `value.subject.name.strategy` | `TopicNameStrategy` | Class that determines the subject name under which the key/value schema is registered. |
| `basic.auth.credentials.source` / `basic.auth.user.info` | — | Authentication to a secured Schema Registry (`USER_INFO` with `user:password`). |

### Subject name strategy

The serializer registers the schema under a **subject**. Compatibility checks are performed **per subject**. The strategy determines how the subject name is derived:

| Strategy | Subject name | When to use |
|---|---|---|
| `io.confluent.kafka.serializers.subject.TopicNameStrategy` (**default**) | `<topic>-key`, `<topic>-value` | One topic carries **one** record type (the usual case). Schema evolution is scoped to the topic. |
| `io.confluent.kafka.serializers.subject.RecordNameStrategy` | `<fully-qualified record name>` (e.g. `com.acme.OrderCreated`) | Multiple event types in one topic **or** the same record type spread across many topics. Compatibility is checked across **all** topics using that record name. |
| `io.confluent.kafka.serializers.subject.TopicRecordNameStrategy` | `<topic>-<fully-qualified record name>` | Multiple event types in one topic, but compatibility should be checked **per topic** (different topics can evolve the same record independently). |

Notes:

- With `TopicNameStrategy`, producing a record with a **different** record type to the same topic fails the compatibility check (Avro record name change is incompatible) unless compatibility is `NONE`.
- With `RecordNameStrategy` / `TopicRecordNameStrategy`, a consumer must be able to handle several record types (usually via `GenericRecord` or a union schema).
- The strategy configured on the **consumer** does not affect deserialization (the schema ID in the payload is used); it is only relevant for the serializer/producer and for Connect converters.

### Schema ID vs version

- **Schema ID** is a globally unique integer assigned by Schema Registry the first time a schema string is registered. Registering the identical schema again (in any subject) returns the same ID.
- **Version** is a monotonically increasing number **within a subject** (1, 2, 3, …). The same schema ID may be version 3 in `orders-value` and version 1 in `orders-dlq-value`.
- The wire format carries only the **ID**, never the version.

### Caching

Serializers keep an in-memory cache of `schema → id` and deserializers of `id → schema` so Schema Registry is called only the first time a schema/ID is seen per client instance. If Schema Registry is unavailable, a client whose cache is already warm can continue to work; a cold client fails with a `SerializationException` wrapping a `RestClientException`.

### Multiple event types in one topic

Two approaches:

1. Use `RecordNameStrategy` / `TopicRecordNameStrategy` so each event type gets its own subject.
2. Keep `TopicNameStrategy` and register an Avro **union** top-level schema (`[ "com.acme.OrderCreated", "com.acme.OrderCancelled" ]`) using **schema references**, with `auto.register.schemas=false` and `use.latest.version=true` on the producer.
