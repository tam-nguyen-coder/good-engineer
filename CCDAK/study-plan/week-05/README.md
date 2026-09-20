# 🟦 Tuần 5 — Schema Registry & Serialization + Kafka Connect

> **Domain CCDAK:** Kafka Connect (CONNECT, 15%) + Application Development (DEV, phần serialization) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 5/10 — tuần "tích hợp": xong tuần này bạn đã phủ FUND + DEV + CONNECT (~66% đề), không có checkpoint nhưng là nền của mini-mock Tuần 7
>
> **Điều hướng:** [⬅️ Tuần 4](../week-04/README.md) · [🏠 Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md) · [Tuần 6 ➡️](../week-06/README.md)

## 🎯 Mục tiêu tuần này

- **Giải thích được** vì sao cần `Schema Registry` (contract giữa producer/consumer, tiết kiệm byte, chặn schema hỏng lúc produce) và đọc được **wire format 5 byte** (magic `0x00` + schema ID int32 + payload) bằng mắt.
- **Phân biệt được** Avro / Protobuf / JSON Schema và 3 **subject naming strategy** (`TopicNameStrategy` mặc định `<topic>-value`, `RecordNameStrategy`, `TopicRecordNameStrategy`) — chọn đúng khi đề nói "nhiều event type trong 1 topic".
- **Thuộc** bảng **compatibility modes** (`BACKWARD` mặc định / `FORWARD` / `FULL` / `*_TRANSITIVE` / `NONE`): thao tác nào được phép và **ai nâng cấp trước**.
- **Tự tay** đăng ký schema, produce/consume Avro bằng Node.js, gây lỗi **409 incompatible** rồi sửa; đổi compatibility bằng REST API.
- **Vẽ lại được** kiến trúc `Kafka Connect`: worker → connector → task, standalone vs distributed, 3 internal topic (1 / 25 / 5 partition, đều compacted), REST API 8083.
- **Phân biệt trong 5 giây** converter (`key.converter`/`value.converter`) ≠ SMT (`transforms`) ≠ serializer (app producer/consumer).
- **Cấu hình được** error handling: `errors.tolerance=all` + DLQ (**chỉ sink**) + header `__connect.errors.*`; exactly-once source (`exactly.once.source.support=enabled` + `exactly.once.support=required`); nhận diện Debezium CDC (`before/after/op`).

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

#### PHẦN 1 — Schema Registry & Serialization

**1. Vì sao cần schema (câu hỏi "why" hay xuất hiện)**

- Kafka broker chỉ thấy **byte[]**, không kiểm tra nội dung → producer đổi format là consumer chết **lúc consume**, không phải lúc produce. Schema = **hợp đồng** giữa hai bên, được kiểm tra **tại producer** (fail fast).
- Gửi schema kèm mỗi record (như JSON tự mô tả hay Avro container file) thì **tốn byte**; `Schema Registry` tách schema ra một dịch vụ REST riêng, record chỉ mang **ID 4 byte** → payload Avro nhị phân nhỏ hơn JSON 3–5 lần.
- Registry còn **chặn evolution sai** (compatibility check) → hỗ trợ nâng cấp producer/consumer độc lập, không phải deploy đồng thời.
- Schema Registry là **process riêng** (Confluent, Apache-2.0/Confluent Community License), lưu mọi thứ trong topic Kafka **`_schemas`** (1 partition, compacted); nhiều instance chạy **leader/follower** — chỉ leader ghi, follower forward request ghi. Port mặc định **8081**. Trên AWS có `AWS Glue Schema Registry` cùng vai trò (Tuần 9), Apicurio Registry là lựa chọn mã nguồn mở khác.

**2. Avro vs Protobuf vs JSON Schema — bảng bắt buộc**

| Tiêu chí | Avro (mặc định của hệ sinh thái Kafka) | Protobuf | JSON Schema |
|---|---|---|---|
| Định nghĩa schema | JSON (`.avsc`), IDL `.avdl` | `.proto` (IDL riêng) | JSON (draft-07) |
| Encoding | Nhị phân, **không có tag field** → nhỏ nhất, nhưng **bắt buộc có schema để đọc** | Nhị phân có field number → tự mô tả một phần | Text JSON, to nhất, dễ đọc |
| Evolution | Rất tốt: reader/writer schema resolution, `default`, `aliases` | Tốt: field number không đổi, `optional`, không được tái dùng số | Yếu nhất: `additionalProperties`, `required` quyết định; mở/đóng schema khác nhau |
| Codegen | Tuỳ chọn (`SpecificRecord`) hoặc `GenericRecord` | Bắt buộc/thường dùng codegen, đa ngôn ngữ mạnh (gRPC) | Không cần |
| Serializer Confluent | `KafkaAvroSerializer` / `KafkaAvroDeserializer` | `KafkaProtobufSerializer` / `KafkaProtobufDeserializer` | `KafkaJsonSchemaSerializer` / `KafkaJsonSchemaDeserializer` |
| Connect converter | `io.confluent.connect.avro.AvroConverter` | `ProtobufConverter` | `JsonSchemaConverter` (≠ `JsonConverter` của Apache!) |
| Wire format | 5 byte + Avro binary | 5 byte + **message indexes** (thường 1 byte `0`) + Protobuf | 5 byte + JSON UTF-8 |
| Chọn khi | Chuẩn Kafka, Connect/Streams/ksqlDB đều hỗ trợ tốt, cần evolution linh hoạt | Hệ đa ngôn ngữ, đã dùng gRPC, cần strong typing | Web/JS-first, cần con người đọc được, validation payload JSON hiện có |

**3. Wire format 5 byte (bẫy kinh điển)**

```
byte 0        : magic byte = 0x00  (version của format Confluent, luôn 0)
byte 1..4     : schema ID, int32 big-endian (ID TOÀN CỤC của Schema Registry, không phải version)
byte 5..      : (Protobuf) message indexes zigzag varint, thường là 1 byte 0x00
byte còn lại  : payload Avro binary / Protobuf / JSON
```

- ⚠️ `kafka-console-consumer.sh` thường đọc topic Avro → mỗi dòng bắt đầu bằng **vài ký tự lạ (5 byte)** rồi chuỗi nhị phân → dấu hiệu "record ghi bằng Schema Registry serializer"; phải dùng `kafka-avro-console-consumer` hoặc `KafkaAvroDeserializer`.
- Ngược lại: `AvroConverter`/`KafkaAvroDeserializer` đọc topic JSON/String → `SerializationException: Unknown magic byte!`.
- Serializer **cache** `schema → id`, deserializer cache `id → schema` → REST chỉ gọi lần đầu; Registry sập thì client "ấm" vẫn chạy, client mới khởi động **fail**.

**4. Config serializer/deserializer phải thuộc (đề hỏi theo tên Java)**

| Config | Mặc định | Ý nghĩa & bẫy |
|---|---|---|
| `schema.registry.url` | bắt buộc | Danh sách URL (`http://sr1:8081,http://sr2:8081`) |
| `auto.register.schemas` | **true** | Serializer tự đăng ký schema khi gặp lần đầu. **Production nên `false`** → schema đăng ký qua CI/CD (Maven/Gradle plugin, REST); producer mang schema lạ → **fail fast** thay vì lặng lẽ tạo version mới |
| `use.latest.version` | false | Chỉ có nghĩa khi `auto.register.schemas=false`: dùng **version mới nhất** của subject thay vì tra đúng schema của object (cần cho union/schema references) |
| `latest.compatibility.strict` | true | Đi cùng `use.latest.version`: kiểm tra schema object tương thích với latest, không thì lỗi |
| `specific.avro.reader` | false | Deserializer trả **`SpecificRecord`** (class sinh sẵn) thay `GenericRecord` |
| `key.subject.name.strategy` / `value.subject.name.strategy` | `TopicNameStrategy` | Cách đặt tên subject (mục 5); chỉ ảnh hưởng **serializer** (deserializer dùng ID trong payload) |
| `normalize.schemas` | false | Chuẩn hoá whitespace/thứ tự field để 2 schema tương đương cùng ID |

**5. Subject naming strategy — "nhiều event type trong 1 topic" chọn gì?**

| Strategy | Subject | Khi nào dùng | Compatibility kiểm tra theo |
|---|---|---|---|
| `TopicNameStrategy` (**mặc định**) | `<topic>-key`, `<topic>-value` | 1 topic = 1 loại record (trường hợp thường) | Từng **topic** |
| `RecordNameStrategy` | `<namespace>.<RecordName>` (vd `com.acme.OrderCreated`) | Nhiều event type trong 1 topic **hoặc** cùng record xuất hiện ở nhiều topic, muốn 1 schema dùng chung | **Mọi topic** dùng record đó |
| `TopicRecordNameStrategy` | `<topic>-<namespace>.<RecordName>` | Nhiều event type trong 1 topic nhưng mỗi topic **tiến hoá độc lập** | Từng **topic + record** |

- Với `TopicNameStrategy`, đẩy record khác **tên** vào cùng topic → compatibility check **fail** (đổi record name là incompatible), trừ khi `NONE`. Cách 2 giữ `TopicNameStrategy`: Avro **union** top-level + schema references + `auto.register.schemas=false`, `use.latest.version=true`.
- **Schema ID vs version:** ID **duy nhất toàn Registry** (cùng chuỗi schema đăng ký ở 2 subject → **cùng ID**); version **tăng dần trong 1 subject** (1, 2, 3…). Wire format chỉ mang **ID**.

**6. Compatibility modes — bảng bắt buộc (thao tác được phép + thứ tự nâng cấp)**

| Mode | Định nghĩa | Được phép | So với version | **Nâng cấp trước** |
|---|---|---|---|---|
| `BACKWARD` (**mặc định**) | Schema **mới** đọc được data **cũ** | **Xoá field**; **thêm field có default** | Mới nhất | **Consumer** |
| `BACKWARD_TRANSITIVE` | Như trên với **mọi** version cũ | Xoá field; thêm field có default | Tất cả | Consumer |
| `FORWARD` | Schema **cũ** đọc được data **mới** | **Thêm field**; **xoá field có default** | Mới nhất | **Producer** |
| `FORWARD_TRANSITIVE` | Như trên với mọi version | Thêm field; xoá field có default | Tất cả | Producer |
| `FULL` | Cả hai chiều | **Chỉ thêm/xoá field CÓ default** | Mới nhất | Tuỳ ý |
| `FULL_TRANSITIVE` | Cả hai chiều, mọi version | Chỉ thêm/xoá field có default | Tất cả | Tuỳ ý |
| `NONE` | Không kiểm tra | Mọi thứ (đổi type, đổi tên) | — | Phải deploy đồng thời / topic mới |

Ma trận thao tác (Avro/Protobuf):

| Thao tác | BACKWARD | FORWARD | FULL |
|---|---|---|---|
| Thêm field **có** default | ✅ | ✅ | ✅ |
| Xoá field **có** default | ✅ | ✅ | ✅ |
| Thêm field **không** default (required) | ❌ **409** | ✅ | ❌ |
| Xoá field **không** default | ✅ | ❌ | ❌ |
| Đổi tên field không `aliases` / đổi type | ❌ | ❌ | ❌ |

- Cách nhớ: **BACKWARD = consumer mới, data cũ** → consumer phải tự điền được field thiếu → field mới phải có **default**; xoá field thì consumer mới cứ bỏ qua. Kafka hay **rewind/replay** data cũ → đó là lý do BACKWARD làm mặc định.
- Vi phạm khi `POST /subjects/<s>/versions` → **HTTP 409 Conflict** `Schema being registered is incompatible with an earlier schema`. Test trước bằng `POST /compatibility/subjects/<s>/versions/latest` → `{"is_compatible": false}`.
- Transitive: non-transitive chỉ so với **version liền trước**; nếu consumer có thể đọc lại data từ **v1** (retention dài, compaction) thì cần `*_TRANSITIVE`.
- Avro: field optional = có `default` (nullable: `["null","string"]`, `"default": null`); `aliases` cho phép đổi tên mà vẫn đọc data cũ. Kafka Streams app **chỉ hỗ trợ BACKWARD** (đọc cả changelog cũ).

**7. REST API Schema Registry (port 8081, content type `application/vnd.schemaregistry.v1+json`)**

| Endpoint | Việc |
|---|---|
| `GET /subjects` | Liệt kê subject (`["orders-value", ...]`) |
| `GET /subjects/<s>/versions` · `GET /subjects/<s>/versions/latest` (hoặc `/<n>`) | Liệt kê version `[1,2]` · lấy schema (trả `subject`, `id`, `version`, `schema`) |
| `POST /subjects/<s>/versions` body `{"schema": "<escaped>", "schemaType": "AVRO\|PROTOBUF\|JSON"}` | Đăng ký → `{"id": N}`; **409** incompatible; **422** schema sai; `schemaType` mặc định AVRO |
| `GET /schemas/ids/<id>` | Lấy schema theo **ID toàn cục** (chính là ID trong 5 byte) |
| `POST /compatibility/subjects/<s>/versions/latest` | Test tương thích → `{"is_compatible": true\|false}` (`?verbose=true` cho lý do) |
| `GET\|PUT /config` · `GET\|PUT\|DELETE /config/<s>` | Compatibility **global** / **theo subject** (subject ưu tiên); body `{"compatibility": "FULL"}`, response `compatibilityLevel` |
| `DELETE /subjects/<s>` | **Soft delete** (ID vẫn còn để deserialize data cũ); `?permanent=true` xoá hẳn |
| `GET\|PUT /mode` | `READWRITE` (mặc định) / `READONLY` / `IMPORT` (giữ nguyên ID khi migrate) |

#### PHẦN 2 — Kafka Connect

**8. Kiến trúc: worker → connector → task**

- `Kafka Connect` = framework **tích hợp bằng cấu hình, không code**, chạy **process riêng** (worker JVM), không nằm trong broker. **Source** = ngoài → Kafka; **Sink** = Kafka → ngoài.
- **Worker**: JVM chạy Connect. **Connector**: logic **chia việc** (không copy data). **Task**: đơn vị **song song thật sự** copy data. `tasks.max` (mặc định **1**) là **trần**; connector quyết định số task thực tế (FileStreamSource, Debezium Postgres luôn **1 task**; JDBC source = số bảng; sink ≤ số partition).
- `plugin.path`: thư mục JAR plugin; mỗi plugin có **class loader riêng** (isolation) → 2 connector dùng 2 version thư viện khác nhau vẫn sống chung. Converter/SMT bên thứ ba phải có trên **mọi** worker.
- Task **FAILED không tự restart, không gây rebalance** → `POST /connectors/<n>/restart?includeTasks=true&onlyFailed=true`. Worker chết → task **chuyển** sang worker khác (incremental cooperative rebalance, `connect.protocol=sessioned`, chờ tối đa `scheduled.rebalance.max.delay.ms` = **5 phút**).

**9. Standalone vs Distributed — bảng bắt buộc**

| | Standalone | Distributed |
|---|---|---|
| Lệnh | `connect-standalone.sh worker.properties connector1.properties ...` | `connect-distributed.sh worker.properties` |
| Số worker | **1** process | N worker cùng **`group.id`** (không được trùng consumer group nào) |
| Cấu hình connector | File properties **trên dòng lệnh** lúc start | **REST API** (8083) `POST /connectors` — không truyền qua CLI |
| Offset source | File `offset.storage.file.filename` | Topic `offset.storage.topic` (mặc định **`connect-offsets`**, **25** partition, compacted) |
| Config / status | Trong RAM | `config.storage.topic` (**`connect-configs`**, **1** partition — bắt buộc), `status.storage.topic` (**`connect-status`**, **5** partition); đều **compacted**, RF khuyến nghị 3 |
| HA / scale | ❌ | ✅ rebalance task, thêm worker để scale |
| Exactly-once source | ❌ | ✅ (3.3+) |
| Dùng khi | Dev, gom log trên 1 máy | Production |

- Nên **tạo tay** 3 internal topic (đúng partition + `cleanup.policy=compact`); auto-create có thể sinh topic `delete` nhiều partition → `connect-configs` **phải 1 partition** để giữ thứ tự config.
- `offset.flush.interval.ms` mặc định **60000**. Worker dùng 3 client: `producer.*` (source ghi), `consumer.*` (sink đọc), `admin.*` (tạo topic/DLQ).

**10. Converter ≠ SMT ≠ Serializer — bảng bắt buộc**

| | Serializer / Deserializer | Converter | SMT (Single Message Transform) |
|---|---|---|---|
| Ở đâu | App producer/consumer (`key.serializer`, `value.deserializer`) | **Connect worker/connector** (`key.converter`, `value.converter`, `header.converter`) | Connector (`transforms=a,b` + `transforms.a.type`) |
| Làm gì | Object ↔ byte[] | Connect `Struct`/`Schema` (hoặc `Map` schemaless) ↔ byte[] trên Kafka — **ranh giới Connect ↔ Kafka** | Biến đổi **từng record** trên Connect data (thêm/xoá/mask field, đổi topic đích, lọc) |
| Ví dụ | `StringSerializer`, `KafkaAvroSerializer` | `JsonConverter` (+ `schemas.enable`), `AvroConverter`, `StringConverter`, `ByteArrayConverter` | `InsertField`, `MaskField`, `ReplaceField`, `RegexRouter`, `TimestampRouter`, `ExtractField`, `Cast`, `Filter` |
| Cần Schema Registry | Avro/Protobuf/JSON Schema | `AvroConverter`/`ProtobufConverter`/`JsonSchemaConverter` cần `<key\|value>.converter.schema.registry.url` | Không |
| Tương tác | Cùng Avro Confluent → **cùng wire format** với converter → app và Connect đọc chung topic | Đặt ở worker, connector **override** được | Chạy **theo thứ tự** khai báo; trả `null` = drop record |

- Pipeline: **Source**: connector `poll()` → **SMT** → **converter** → Kafka. **Sink**: Kafka → **converter** → **SMT** → connector `put()`. SMT **không bao giờ** thấy byte; lỗi parse xảy ra ở converter **trước** SMT.
- `JsonConverter` `schemas.enable` mặc định **true** → bọc `{"schema":{...},"payload":{...}}`. Sink đọc JSON "trần" với `schemas.enable=true` → `DataException: JsonConverter with schemas.enable requires "schema" and "payload" fields` → đặt `value.converter.schemas.enable=false` (nhưng sink cần schema như JDBC sẽ không chạy → dùng Avro + Registry).
- `ByteArrayConverter` = pass-through không schema (archive nguyên bản ra S3, MirrorMaker 2). Key thường `StringConverter`.

**11. SMT & predicate — thuộc tên và tác dụng**

| SMT (`org.apache.kafka.connect.transforms.*`, hậu tố `$Key`/`$Value`) | Tác dụng | Config chính |
|---|---|---|
| `InsertField` | Thêm field từ metadata hoặc giá trị tĩnh | `topic.field`, `partition.field`, `offset.field`, `timestamp.field`, `static.field`+`static.value` |
| `MaskField` | Che field (null/0/"" hoặc `replacement`) — PII | `fields`, `replacement` |
| `ReplaceField` | Bỏ/giữ/đổi tên field | `exclude`, `include`, `renames=a:b` |
| `ExtractField` | Lấy 1 field làm toàn bộ key/value | `field` |
| `ValueToKey` / `HoistField` / `Flatten` | Tạo key từ value / bọc giá trị vào struct / phẳng hoá nested | `fields` / `field` / `delimiter` |
| `Cast` | Đổi kiểu | `spec=age:int32` |
| `RegexRouter` | Đổi **topic** theo regex | `regex`, `replacement` (`$1`) |
| `TimestampRouter` | Đổi topic theo timestamp | `topic.format=${topic}-${timestamp}`, `timestamp.format=yyyyMMdd` |
| `TimestampConverter` | Unix ↔ string ↔ Connect Timestamp | `field`, `target.type`, `format` |
| `Filter` | **Drop** record — **phải** đi với predicate | `predicate=<alias>`, `negate` |
| `InsertHeader` / `DropHeaders` / `HeaderFrom` | Thao tác header | — |

- **Predicate** (KIP-585): `predicates=p` + `predicates.p.type=` `TopicNameMatches` (`pattern`) / `HasHeaderKey` (`name`) / `RecordIsTombstone`; gắn `transforms.x.predicate=p`, đảo bằng `negate=true`. Drop tombstone trước sink không chịu null: `Filter` + `RecordIsTombstone`.
- `RegexRouter`/`TimestampRouter` ở **source** → đổi topic Kafka ghi vào; ở **sink** → đổi **tên bảng/index/prefix đích** (record đã đọc khỏi topic rồi).
- SMT là stateless, 1-in → 0/1-out; join/aggregate/window → `Kafka Streams`/`ksqlDB` (Tuần 6).

**12. REST API Kafka Connect (port 8083, gọi worker nào cũng được — tự forward tới leader)**

| Method + path | Việc |
|---|---|
| `GET /` · `GET /connector-plugins` | Version worker, `kafka_cluster_id` · plugin đã cài (`?connectorsOnly=false` kèm converter/SMT) |
| `GET /connectors` (`?expand=status`) | Danh sách connector |
| `POST /connectors` body `{"name": "...", "config": {...}}` | Tạo → **201**; **409** khi đang rebalance hoặc trùng tên |
| `PUT /connectors/<n>/config` body = config | **Upsert**: tạo mới (201) hoặc **cập nhật** (200) — cách chuẩn để đổi config |
| `GET /connectors/<n>` · `/config` · `/status` · `/tasks` · `/tasks/<id>/status` · `/topics` | Thông tin / trạng thái (`RUNNING`, `PAUSED`, `STOPPED`, `FAILED` + `trace`, `UNASSIGNED`, `RESTARTING`) |
| `POST /connectors/<n>/restart?includeTasks=true&onlyFailed=true` | Restart connector (+task) → 202 |
| `PUT /connectors/<n>/pause` · `/resume` · `/stop` (3.5+) | Pause giữ task, không poll/put · resume · stop huỷ task nhưng **giữ config & offset** |
| `DELETE /connectors/<n>` | Xoá connector (204) — **offset KHÔNG bị xoá** |
| `GET\|PATCH\|DELETE /connectors/<n>/offsets` (3.5/3.6+) | Xem / sửa / **reset offset** — connector phải **STOPPED** |
| `PUT /connector-plugins/<class>/config/validate` | Validate config trước khi tạo |
| `GET\|PUT /admin/loggers/<logger>` | Đổi log level runtime |

**13. Error handling & DLQ (KIP-298) — bảng source vs sink**

| | Source connector | Sink connector |
|---|---|---|
| `errors.tolerance` | `none` (mặc định: lỗi → task **FAILED**) / `all` (skip record) | Như source |
| `errors.retry.timeout` / `errors.retry.delay.max.ms` | `0` (không retry) / `-1` vô hạn · `60000` | Như source |
| `errors.log.enable` / `errors.log.include.messages` | `false` / `false` (bật để log cả record — cẩn thận PII) | Như source |
| **DLQ** `errors.deadletterqueue.topic.name` | ❌ **KHÔNG có** (record chưa có toạ độ Kafka để tham chiếu) | ✅ mặc định rỗng = tắt; `errors.deadletterqueue.topic.replication.factor` **3** (dev 1 broker phải đặt 1); `errors.deadletterqueue.context.headers.enable=true` → header **`__connect.errors.*`** (`topic`, `partition`, `offset`, `connector.name`, `task.id`, `stage`, `class.name`, `exception.class.name`, `exception.message`, `exception.stacktrace`) |
| Giai đoạn bao phủ | `TASK_POLL`, `TRANSFORMATION`, `*_CONVERTER`, `KAFKA_PRODUCE` | `KAFKA_CONSUME`, `*_CONVERTER`, `TRANSFORMATION`, `TASK_PUT` (chỉ khi connector ném `RetriableException`) |
| **Offset** lưu ở | `connect-offsets` (hoặc file standalone), dạng **map connector tự định nghĩa** (`sourcePartition` → `sourceOffset`), key = `["<connector>", {sourcePartition}]` | `__consumer_offsets` qua consumer group **`connect-<connector-name>`** → xem lag bằng `kafka-consumer-groups.sh --describe --group connect-<n>` |
| Delivery mặc định | At-least-once (record và offset ghi 2 bước) | At-least-once (commit sau `put()`/`flush()`) |
| Exactly-once | ✅ KIP-618 (3.3+): worker `exactly.once.source.support=enabled` (rolling: `preparing` → `enabled`) + connector `exactly.once.support=required` (preflight check, `requested` mặc định) + `transaction.boundary=poll\|interval\|connector`; chỉ **distributed** | ❌ framework không có; dựa vào **idempotent/upsert** (JDBC `insert.mode=upsert`, S3 tên object deterministic, ES `_id`=key) |
| Xoá connector rồi tạo lại cùng tên | **Tiếp tục** từ offset cũ (offset vẫn trong topic); reset: stop → `DELETE /connectors/<n>/offsets` | Group `connect-<n>` còn tới `offsets.retention.minutes` (7 ngày) → cũng tiếp tục |

- DLQ record = **byte gốc** (key/value/header y nguyên như đọc từ Kafka), không phải bản đã biến đổi → replay được. Topic DLQ được **admin client của worker** tự tạo (1 partition) nếu chưa có.
- Consumer đọc topic của source EOS phải `isolation.level=read_committed` (ôn Tuần 3).

**14. Override client theo connector + connector phổ biến**

- Từ 2.3 (KIP-458): `producer.override.*` (source), `consumer.override.*` (sink), `admin.override.*` (DLQ/topic creation). Worker quyết định bằng `connector.client.config.override.policy` = `All` (**mặc định từ 3.0**, trước là `None`) / `Principal` (chỉ security) / `None`. Kafka 4.2 thêm **`Allowlist`** (chỉ cho phép danh sách key khai báo). Override bị chặn → tạo connector **fail lúc validate**.
- Connector hay gặp: **JDBC source** (polling theo `mode=incrementing|timestamp|bulk`, **không bắt được DELETE**) / **JDBC sink** (`insert.mode=upsert`, `pk.mode`), **S3 sink** (`flush.size`, partitioner theo thời gian), **Elasticsearch sink** (key → `_id`), **HTTP sink**, **Debezium CDC** (log-based: MySQL binlog, Postgres WAL/`pgoutput`, bắt được DELETE; envelope `before`/`after`/`source`/**`op`**=`c`/`u`/`d`/`r`; delete → `op=d` + **tombstone** cùng key; topic `<topic.prefix>.<schema>.<table>`; luôn 1 task; SMT `ExtractNewRecordState` unwrap). **MirrorMaker 2** chạy **trên Connect** (`MirrorSourceConnector`, `MirrorCheckpointConnector`, `MirrorHeartbeatConnector`) — Tuần 8. `Amazon MSK Connect` = Connect managed — Tuần 9.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + code):** [labs.md](labs.md). Dùng lại cluster 3 node Tuần 1 (`docker-compose.cluster.yml`) + 2 file override mới: `docker-compose.registry.yml` (Schema Registry 8081) và `docker-compose.connect.yml` (Connect 8083).

- **Lab 5.1 ⭐** — Thêm `Schema Registry` (`confluentinc/cp-schema-registry:8.0.0`) bằng compose override; Node.js `@kafkajs/confluent-schema-registry` đăng ký Avro schema, produce/consume; `curl :8081/subjects`; đọc topic bằng `kcc` thường → **thấy 5 byte lạ** và tự giải mã `schema ID` bằng `readInt32BE(1)`.
- **Lab 5.2** — Schema evolution: thêm field **không default** ở `BACKWARD` → **409**; thêm field **có default** → OK (version 2); `PUT /config/<subject>` sang `FORWARD` rồi `FULL` và thử lại từng thao tác → tự điền ma trận compatibility.
- **Lab 5.3** — Connect distributed (`confluentinc/cp-kafka-connect:8.0.0`): `kt --list` thấy `connect-configs`(1)/`connect-offsets`(25)/`connect-status`(5) compacted; `GET /connector-plugins`, `GET /`.
- **Lab 5.4 ⭐** — FileStreamSource → topic → FileStreamSink với SMT chain `HoistField` → `InsertField` → `RegexRouter`; thấy topic đích đổi tên và field mới; đổi thứ tự chain để thấy lỗi.
- **Lab 5.5** — DLQ: sink `errors.tolerance=all` + `errors.deadletterqueue.topic.name` + `context.headers.enable`; bơm record hỏng → DLQ, đọc header `__connect.errors.*`; so với `errors.tolerance=none` → task FAILED + `trace`.
- **Lab 5.6 (tuỳ chọn)** — Debezium Postgres CDC (`quay.io/debezium/connect` + `postgres:16` `wal_level=logical`): INSERT/UPDATE/DELETE → `op=c/u/d` + tombstone.
- **Lab 5.7** — REST ops: pause/resume/restart, đọc `connect-offsets` bằng `kcc --property print.key=true`, `kcg --describe --group connect-<sink>`, stop → `DELETE /offsets` → resume đọc lại từ đầu.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**1. Bảng quyết định: mode compatibility theo tình huống**

| Tình huống đề | Chọn | Vì sao |
|---|---|---|
| Consumer có thể **replay** data rất cũ (retention dài, compacted topic) | `BACKWARD_TRANSITIVE` hoặc `FULL_TRANSITIVE` | Non-transitive chỉ so với version liền trước |
| Nhiều team consumer, không kiểm soát được thứ tự deploy | `FULL` / `FULL_TRANSITIVE` | Nâng cấp tuỳ ý, chỉ được thêm/xoá field có default |
| Producer nâng cấp trước, consumer cũ vẫn phải đọc data mới | `FORWARD` | Consumer cũ bỏ qua field mới |
| Kafka Streams app dùng Avro | `BACKWARD` | Streams chỉ hỗ trợ BACKWARD |
| Đổi type/đổi tên record, chấp nhận không đọc được data cũ | `NONE` + **topic mới** | Không có mode nào cho phép đổi type |
| Cần thêm field bắt buộc nhưng đang `BACKWARD` | Thêm với **default** (hoặc `["null", T]` default null) | Field không default = 409 |

**2. Bảng quyết định: sự cố Connect → hành động**

| Triệu chứng | Nguyên nhân | Sửa |
|---|---|---|
| `Unknown magic byte!` | `AvroConverter` đọc topic không phải Avro-SR | Đổi `JsonConverter`/`StringConverter` hoặc sửa producer |
| `JsonConverter with schemas.enable requires "schema" and "payload"` | JSON trần + `schemas.enable=true` | `value.converter.schemas.enable=false` hoặc Avro |
| Console consumer in ký tự lạ đầu dòng | Wire format 5 byte | `kafka-avro-console-consumer` / `KafkaAvroDeserializer` |
| Task `FAILED`, connector `RUNNING` | Lỗi record + `errors.tolerance=none`; không tự restart | Xem `trace` ở `/status`; sửa; `POST .../restart?includeTasks=true&onlyFailed=true` |
| Poison record dừng sink | Thiếu tolerance | `errors.tolerance=all` + DLQ + headers (sink) |
| Source connector cấu hình DLQ mà không có gì | Source **không có DLQ** | Chỉ retry/log/skip; connector tự xử lý |
| `tasks.max=8` nhưng chỉ 1 task chạy | Connector không chia được (FileStream, Debezium) | Nhiều connector / dùng connector khác |
| Tạo lại connector đọc tiếp offset cũ | Offset còn trong `connect-offsets`/consumer group | Stop → `DELETE /connectors/<n>/offsets` (3.6+) hoặc đổi tên connector |
| Duplicate từ source sau crash | At-least-once mặc định | EOS source: worker `enabled` + connector `required`; consumer `read_committed` |
| Override `consumer.override.*` bị từ chối | `connector.client.config.override.policy=None` | Đổi `All`/`Principal`/`Allowlist` ở worker |
| Connect 2 cluster trên cùng Kafka lỗi lạ | Trùng `group.id` hoặc trùng internal topic | Mỗi cluster Connect: `group.id` + 3 topic riêng |
| `connect-configs` có nhiều partition | Auto-create | Tạo tay 1 partition compacted |

**3. `kafkajs` + `@kafkajs/confluent-schema-registry` ↔ Java — map để không lẫn khi thi**

| Java | Node.js (lab) | Ghi chú |
|---|---|---|
| `KafkaAvroSerializer` + `schema.registry.url` | `new SchemaRegistry({ host })` + `registry.encode(id, obj)` rồi `producer.send` | Thư viện Node tự thêm 5 byte |
| `KafkaAvroDeserializer` | `registry.decode(message.value)` | Đọc ID từ byte 1–4, tra schema, cache |
| `auto.register.schemas` | `registry.register(schema, { subject })` gọi tay | Tương đương "đăng ký qua CI/CD" |
| `value.subject.name.strategy` | tham số `subject` khi `register` | Mặc định thư viện = `<namespace>.<name>` → **luôn truyền `subject: '<topic>-value'`** |
| Compatibility | `register(..., { compatibility })` hoặc `curl PUT /config/<s>` | Thư viện mặc định set `BACKWARD` cho subject mới |

**4. Đọc thêm (30–40 phút)**

- Confluent Docs: *Schema Evolution and Compatibility*, *Formats, Serializers, and Deserializers* (wire format), *Schema Registry API Reference*.
- Apache Kafka Docs 4.3: *8. Kafka Connect* (User Guide, REST API, Exactly-once, Connector Development — chỉ đọc phần Connector/Task lifecycle), generated `connect_transforms.html`.
- KIP-298 (Error handling), KIP-618 (Exactly-once source), KIP-585 (Predicates), KIP-458 (Client override).
- Confluent Developer: *Kafka Connect 101* (free) + *Schema Registry 101*. Sách *Kafka: The Definitive Guide* 2nd ed. — Chương 3 phần Serializers/Avro, Chương 9 *Building Data Pipelines* (Kafka Connect).

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(bằng tiếng Anh — văn phong đề CCDAK.)*

- Làm 30 câu **không tra tài liệu**, tự chấm; câu sai → quay lại đúng mục Buổi A và **ghi sổ** (nhầm chiều BACKWARD/FORWARD? nhầm converter với SMT? quên DLQ chỉ sink?).
- Tự viết lại **bằng trí nhớ** 3 bảng: compatibility (thao tác + thứ tự nâng cấp), converter vs SMT vs serializer, source vs sink (DLQ/offset). So với README.
- **Spaced repetition** mốc **1 / 3 / 7 ngày** cho bộ số: 5 byte / 8081 / 8083 / 1–25–5 partition / 409 / `tasks.max=1` / 60 s flush / 5 phút rebalance delay / 3.3 EOS source.
- Tuần 7 có **mini-mock CONNECT+STREAMS+TEST ≥70%** — CONNECT 15% chủ yếu từ tuần này.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| Wire format | **5 byte**: magic `0x00` (1 byte) + **schema ID int32** (4 byte) + payload; Protobuf thêm message indexes |
| Port | Schema Registry **8081**, Connect REST **8083** |
| Compatibility mặc định | **`BACKWARD`**: schema mới đọc data cũ → **xoá field / thêm field có default**; nâng cấp **consumer trước** |
| `FORWARD` | Thêm field / xoá field có default; nâng cấp **producer trước** |
| `FULL` | Chỉ thêm/xoá field **có default**; thứ tự tuỳ ý |
| `*_TRANSITIVE` | So với **mọi** version trước (non-transitive chỉ so với latest) |
| Vi phạm compatibility | **HTTP 409** khi `POST /subjects/<s>/versions`; test trước `POST /compatibility/subjects/<s>/versions/latest` |
| Subject mặc định | `TopicNameStrategy` → `<topic>-key` / `<topic>-value`; nhiều type/topic → `RecordNameStrategy` (check xuyên topic) / `TopicRecordNameStrategy` (check theo topic) |
| Schema ID vs version | ID **toàn cục** (cùng schema → cùng ID ở mọi subject); version **theo subject** |
| `auto.register.schemas` | Mặc định **true**; production **false** + CI/CD; `use.latest.version` chỉ có nghĩa khi auto-register tắt |
| `_schemas` | **1 partition**, compacted; leader/follower — chỉ leader ghi |
| Connect internal topics | `connect-configs` **1** · `connect-offsets` **25** · `connect-status` **5** partition — **đều compacted**, RF 3 |
| `tasks.max` | Mặc định **1**, là **trần**; FileStream/Debezium luôn 1 task |
| Converter vs SMT | `key.converter`/`value.converter` = bytes ↔ Connect data · `transforms` = biến đổi record theo **thứ tự**; source: SMT → converter; sink: converter → SMT |
| `JsonConverter` | `schemas.enable` mặc định **true** → envelope `schema`+`payload` |
| Task FAILED | **Không tự restart, không rebalance** → `POST .../restart?includeTasks=true` |
| `errors.tolerance` | `none` mặc định / `all` skip; `errors.retry.timeout` 0 (-1 vô hạn); `errors.log.enable` false |
| DLQ | **Chỉ SINK**: `errors.deadletterqueue.topic.name` + `.context.headers.enable=true` → header `__connect.errors.*`; RF mặc định 3 |
| Offset | Source: `connect-offsets` (map connector định nghĩa) · Sink: consumer group **`connect-<name>`**; `DELETE /connectors/<n>` **không** xoá offset |
| EOS source (KIP-618, 3.3+) | Worker `exactly.once.source.support=enabled` + connector `exactly.once.support=required`; `transaction.boundary=poll`; chỉ distributed; sink **không** có |
| Override policy | `connector.client.config.override.policy` = **`All`** (mặc định 3.0+) / `Principal` / `None` / `Allowlist` (4.2); prefix `producer.override.*` / `consumer.override.*` |
| Debezium | `op` = `c`/`u`/`d`/`r`; delete → `op=d` + **tombstone**; topic `<prefix>.<schema>.<table>`; bắt được DELETE (JDBC polling thì không) |
| Rebalance Connect | Worker chết → chờ `scheduled.rebalance.max.delay.ms` **5 phút**; `offset.flush.interval.ms` **60 s** |

## ⚠️ Bẫy đề hay gặp

- Thấy "console consumer in vài ký tự lạ rồi dữ liệu nhị phân" → dễ nghĩ topic hỏng/nén, nhưng đúng là **wire format 5 byte** (magic + schema ID) → dùng deserializer Avro.
- Thấy "thêm field mới vào schema, đăng ký bị 409" → dễ chọn đổi sang `NONE`, nhưng đúng là **thêm `default`** cho field (BACKWARD cho phép thêm field có default).
- Thấy "BACKWARD" → dễ nghĩ "producer nâng cấp trước", nhưng đúng là **consumer trước** (schema mới ở phía đọc). FORWARD mới là producer trước.
- Thấy "xoá field bắt buộc" → tưởng luôn an toàn, nhưng chỉ an toàn ở **BACKWARD**; **FORWARD/FULL** yêu cầu field xoá phải **có default**.
- Thấy "consumer thay đổi `value.subject.name.strategy`" → tưởng ảnh hưởng deserialize, nhưng deserializer dùng **ID trong payload**; strategy chỉ có nghĩa với **serializer/converter**.
- Thấy "schema giống nhau ở 2 topic khác nhau, version khác nhau" → dễ nghĩ 2 schema khác, nhưng **ID giống nhau** (ID toàn cục), version theo subject.
- Thấy "`JsonConverter` để đọc topic Avro" hay "`AvroConverter` để đọc JSON" → `Unknown magic byte!` / lỗi parse — **converter phải khớp format thực trên topic**.
- Thấy "`transforms` để chuyển JSON sang Avro" → sai: đổi format là việc của **converter**, SMT chỉ sửa nội dung record.
- Thấy "source connector cấu hình `errors.deadletterqueue.topic.name`" → tưởng có DLQ, nhưng **source không có DLQ** (chỉ sink).
- Thấy "task FAILED, tăng `tasks.max` hoặc restart worker" → sai; task FAILED **không tự restart** → `POST /connectors/<n>/restart?includeTasks=true`.
- Thấy "`tasks.max=4` nhưng chỉ 1 task" → tưởng bug worker, nhưng `tasks.max` là **trần**; FileStream/Debezium chỉ tạo 1.
- Thấy "xoá connector rồi tạo lại để đọc lại từ đầu" → sai: **offset vẫn còn**; phải stop → `DELETE /connectors/<n>/offsets` hoặc đổi tên connector.
- Thấy "bật exactly-once cho sink connector bằng `exactly.once.support=required`" → sai: KIP-618 chỉ cho **source**; sink dựa vào idempotent write.
- Thấy "`connect-offsets` cần 1 partition để giữ thứ tự" → nhầm với `connect-configs`; offsets **25**, status **5**, configs **1**.
- Thấy "SMT `Filter` không có predicate" → **drop mọi record**; `Filter` luôn phải đi với `predicate`.
- Thấy "Schema Registry sập → toàn bộ producer dừng ngay" → không hẳn: client đã **cache** schema/ID vẫn chạy; client mới hoặc schema mới mới fail.

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
|---|---|
| "magic byte", "first 5 bytes", "garbage characters in console consumer" | **Wire format**: `0x00` + schema ID int32 → dùng Avro deserializer |
| "consumers upgraded first" / "new schema reads old data" | **`BACKWARD`** (mặc định) |
| "producers upgraded first" / "old consumers read new data" | **`FORWARD`** |
| "upgrade in any order" | **`FULL`** — chỉ field có default |
| "must read data written by all previous versions" | **`*_TRANSITIVE`** |
| "HTTP 409 when registering schema" | **Incompatible** với compatibility hiện tại |
| "multiple event types in one topic, evolve per topic" | **`TopicRecordNameStrategy`** |
| "same record type across many topics, one shared schema" | **`RecordNameStrategy`** |
| "production, schemas registered by CI" | **`auto.register.schemas=false`** (+ `use.latest.version=true` khi cần) |
| "generated Avro classes on consumer" | **`specific.avro.reader=true`** |
| "where Schema Registry stores schemas" | Topic **`_schemas`**, 1 partition, compacted |
| "no code, move data between Kafka and DB/S3" | **Kafka Connect** (source/sink) |
| "offsets in a local file" | **Standalone** mode |
| "connector configs via REST, fault tolerant" | **Distributed** mode (`group.id`, 3 internal topics) |
| "1 / 25 / 5 partitions, compacted" | `connect-configs` / `connect-offsets` / `connect-status` |
| "bytes ↔ Connect data", "format of data on the topic" | **Converter** (`key.converter`/`value.converter`) |
| "add timestamp field / mask PII / rename topic per record" | **SMT** `InsertField` / `MaskField` / `RegexRouter` |
| "drop tombstones before sink" | `Filter` + predicate **`RecordIsTombstone`** |
| "`{"schema":..., "payload":...}` required" | `JsonConverter` **`schemas.enable`** (mặc định true) |
| "skip bad records, keep pipeline running" | **`errors.tolerance=all`** (+ DLQ nếu sink) |
| "dead letter queue" | **Sink only**: `errors.deadletterqueue.topic.name` + `.context.headers.enable` → `__connect.errors.*` |
| "task FAILED, how to recover" | **`POST /connectors/<n>/restart?includeTasks=true&onlyFailed=true`** |
| "change connector config" | **`PUT /connectors/<n>/config`** (upsert) |
| "reset connector offsets" | Stop → **`DELETE /connectors/<n>/offsets`** (3.6+) |
| "sink connector lag" | `kafka-consumer-groups.sh --describe --group` **`connect-<name>`** |
| "duplicates from source connector after crash" | **EOS source** (KIP-618): worker `exactly.once.source.support=enabled` + connector `exactly.once.support=required` |
| "connector needs its own credentials / client tuning" | **`consumer.override.*` / `producer.override.*`** + `connector.client.config.override.policy` |
| "capture deletes from database" | **Debezium CDC** (log-based; JDBC polling không bắt delete) |
| "`op: d` followed by null value" | Debezium delete + **tombstone** |
| "replicate cluster to cluster on Connect" | **MirrorMaker 2** (Tuần 8) |

## 🧪 Lab checklist

- [ ] Lab 5.1 ⭐ — `docker-compose.registry.yml` chạy; `curl :8081/subjects` thấy `orders-value`; Node produce/consume Avro OK; `kcc` thường in 5 byte lạ; tự decode `schema ID` từ byte 1–4 khớp `GET /schemas/ids/<id>`.
- [ ] Lab 5.2 — Thêm field không default → **409**; thêm field có default → version 2; đổi `PUT /config/orders-value` sang `FORWARD`/`FULL` và điền ma trận 3×3 bằng kết quả thật.
- [ ] Lab 5.3 — `kt --describe` thấy `connect-configs` 1 partition, `connect-offsets` 25, `connect-status` 5, `cleanup.policy=compact`; `GET /connector-plugins` liệt kê FileStreamSource/Sink.
- [ ] Lab 5.4 ⭐ — File → topic `lines-enriched` (đổi tên bởi `RegexRouter`), record có field `data_source` + `ingested_at`; sink ghi ra `/data/output.txt`.
- [ ] Lab 5.5 — Record hỏng vào `dlq-file-sink` với header `__connect.errors.stage=VALUE_CONVERTER`; với `errors.tolerance=none` task FAILED có `trace`; restart qua REST.
- [ ] Lab 5.6 (tuỳ chọn) — Debezium: INSERT → `op=c`, UPDATE → `op=u`, DELETE → `op=d` + tombstone trên `pg1.public.customers`.
- [ ] Lab 5.7 — pause/resume/restart; đọc key/value trong `connect-offsets`; `kcg --describe --group connect-file-sink` thấy LAG; stop → `DELETE /offsets` → resume đọc lại từ đầu.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Record Avro qua Schema Registry trên topic có cấu trúc byte thế nào? Vì sao console consumer thường in ký tự lạ?**
  **Đáp án gọn:** 1 byte magic `0x00` + 4 byte schema ID (int32 big-endian) + payload Avro nhị phân; console consumer không hiểu wire format nên in 5 byte đầu thành ký tự lạ — dùng `kafka-avro-console-consumer`.
- **`BACKWARD` cho phép thao tác gì, ai nâng cấp trước? `FORWARD` thì sao?**
  **Đáp án gọn:** BACKWARD (mặc định): xoá field, thêm field có default; consumer trước. FORWARD: thêm field, xoá field có default; producer trước. FULL: chỉ thêm/xoá field có default, thứ tự tuỳ ý. `_TRANSITIVE` so với mọi version.
- **Khác nhau schema ID và version? Subject mặc định của topic `orders` là gì?**
  **Đáp án gọn:** ID toàn cục (cùng schema → cùng ID), version theo subject; `TopicNameStrategy` → `orders-key`, `orders-value`.
- **Kể 3 internal topic của Connect distributed với số partition và cleanup policy.**
  **Đáp án gọn:** `connect-configs` 1 partition, `connect-offsets` 25, `connect-status` 5 — đều compacted, RF 3.
- **Converter khác SMT ở đâu? Thứ tự chạy trong source và sink?**
  **Đáp án gọn:** Converter đổi bytes ↔ Connect data (ranh giới Kafka), SMT sửa nội dung từng record. Source: SMT → converter → Kafka. Sink: Kafka → converter → SMT → put().
- **DLQ có ở connector loại nào? Cần config gì để có header lỗi?**
  **Đáp án gọn:** Chỉ **sink**: `errors.tolerance=all` + `errors.deadletterqueue.topic.name` + `errors.deadletterqueue.context.headers.enable=true` → header `__connect.errors.*`.
- **Task FAILED thì Connect làm gì? Bạn làm gì?**
  **Đáp án gọn:** Không tự restart, không rebalance; xem `trace` ở `GET /connectors/<n>/status`, sửa lỗi, `POST /connectors/<n>/restart?includeTasks=true&onlyFailed=true`.
- **Bật exactly-once cho source connector cần gì? Sink có được không?**
  **Đáp án gọn:** Kafka 3.3+, distributed: worker `exactly.once.source.support=enabled` (rolling qua `preparing`) + connector `exactly.once.support=required`; consumer đọc `read_committed`. Sink không có EOS framework → idempotent/upsert.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- Confluent Docs: [Schema Evolution and Compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html) · [Formats, Serializers, and Deserializers (wire format)](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html) · [Schema Registry API Reference](https://docs.confluent.io/platform/current/schema-registry/develop/api.html) · [Kafka Connect Concepts](https://docs.confluent.io/platform/current/connect/concepts.html) · [Connect REST Interface](https://docs.confluent.io/platform/current/connect/references/restapi.html).
- Apache Kafka Docs 4.3: [Kafka Connect User Guide](https://kafka.apache.org/documentation/#connect) · [Worker configs](https://kafka.apache.org/43/generated/connect_config.html) · [Sink connector configs](https://kafka.apache.org/43/generated/sink_connector_config.html) · [Source connector configs](https://kafka.apache.org/43/generated/source_connector_config.html) · [Transformations](https://kafka.apache.org/43/generated/connect_transforms.html) · [Predicates](https://kafka.apache.org/43/generated/connect_predicates.html).
- KIP: [KIP-298 Error Handling in Connect](https://cwiki.apache.org/confluence/display/KAFKA/KIP-298%3A+Error+Handling+in+Connect) · [KIP-618 Exactly-Once Support for Source Connectors](https://cwiki.apache.org/confluence/display/KAFKA/KIP-618%3A+Exactly-Once+Support+for+Source+Connectors) · KIP-585 (Predicates) · KIP-458 (Client config override).
- Debezium: [PostgreSQL connector](https://debezium.io/documentation/reference/stable/connectors/postgresql.html).
- Khoá học: Confluent Developer — *Kafka Connect 101* và *Schema Registry 101* (miễn phí); Stephane Maarek — *Apache Kafka Series: Kafka Connect Hands-on Learning* + *Confluent Schema Registry & REST Proxy*; sách *Kafka: The Definitive Guide* 2nd ed. — Ch.3 (Serializers, Avro), Ch.9 (Building Data Pipelines).
- Node.js: [`@kafkajs/confluent-schema-registry`](https://kafkajs.github.io/confluent-schema-registry/) docs.

## ✅ Checklist hoàn thành Tuần 5

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (5 byte / 8081 / 8083 / 1–25–5 / 409 / BACKWARD=consumer trước / DLQ chỉ sink)
- [ ] Tự viết lại 3 bảng: compatibility, converter vs SMT vs serializer, source vs sink bằng trí nhớ
- [ ] Hoàn thành 6 lab bắt buộc (5.1 và 5.4 bắt buộc), 5.6 tuỳ chọn
- [ ] Làm xong 30 câu [questions.md](questions.md) ≥ 70%, xem lại 100% câu sai
- [ ] Vượt Cổng tự kiểm tra (8 câu)
