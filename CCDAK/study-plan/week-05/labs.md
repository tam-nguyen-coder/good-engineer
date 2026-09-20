# 🧪 Hands-on Labs — Tuần 5: Schema Registry & Serialization + Kafka Connect

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab (trừ khi lab sau nói "giữ").
> ⚙️ Yêu cầu chung: đã có `~/kafka-labs/` với 2 file compose chuẩn Tuần 1, `kafkajs@2`, Node.js 24, `curl`, `jq`. Tuần này thêm **2 container** (Schema Registry, Connect) → cần ~6 GB RAM trống.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab)

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d     # cluster 3 broker + 1 controller
export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092        # alias kt/kcp/kcc/kcg/kcfg trỏ vào cluster 3 node
npm i @kafkajs/confluent-schema-registry               # client Schema Registry cho Node (kafkajs đã có từ Tuần 1)
mkdir -p ~/kafka-labs/schemas ~/kafka-labs/connect-data
# Producer nhận stdin từ heredoc/pipe: alias kcp dùng `-it` sẽ báo "input device is not a TTY" → dùng hàm này
kcpi() { docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS "$@"; }
# Tổng số record của 1 topic (cộng log-end-offset các partition)
ktotal() { docker exec $KAFKA_CTR /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_BS --topic "$1" | awk -F: '{s+=$3} END {print s+0}'; }
```

> 📌 2 file compose chuẩn được định nghĩa ở [Tuần 1 — Lab 1.1 / 1.2](../week-01/labs.md). Tuần này **không in lại** cluster; mỗi service mới nằm trong 1 file **override** riêng (`docker-compose.registry.yml`, `docker-compose.connect.yml`, `docker-compose.debezium.yml`) và chạy chồng lên cluster bằng nhiều `-f`. Để khỏi gõ dài, đặt biến `COMPOSE_FILE` (Compose tự đọc, phân cách bằng `:`):
>
> ```bash
> export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.registry.yml:docker-compose.connect.yml
> docker compose up -d        # = docker compose -f a.yml -f b.yml -f c.yml up -d
> docker compose ps
> ```
>
> Mọi lệnh `docker compose` trong tuần này giả định đã `export COMPOSE_FILE` như trên (Lab 5.1 chỉ cần 2 file đầu — thêm file connect từ Lab 5.3 cũng không sao, container `connect` chỉ khởi động sớm hơn).

---

## Lab 5.1 — Thêm `Schema Registry` + produce/consume Avro bằng Node.js ⭐

**🎯 Mục tiêu:** Chạy `confluentinc/cp-schema-registry:8.0.0` (port **8081**) chồng lên cluster Tuần 1; đăng ký Avro schema cho subject `orders-value`; produce/consume Avro bằng `@kafkajs/confluent-schema-registry`; **nhìn thấy 5 byte wire format** bằng `kcc` thường và tự giải mã `schema ID`.
**🧩 Luyện kỹ năng (liên quan đề):**

- Wire format: magic `0x00` + schema ID int32 big-endian + payload.
- Subject mặc định `TopicNameStrategy` → `<topic>-value`; schema ID toàn cục vs version theo subject.
- REST `GET /subjects`, `GET /subjects/<s>/versions/latest`, `GET /schemas/ids/<id>`; topic `_schemas` 1 partition compacted.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo `~/kafka-labs/docker-compose.registry.yml` (chỉ phần **thêm**).

   ```yaml
   # ~/kafka-labs/docker-compose.registry.yml — override: thêm Schema Registry vào cluster Tuần 1
   # Host: http://localhost:8081 · Trong docker network: http://schema-registry:8081
   services:
     schema-registry:
       image: confluentinc/cp-schema-registry:8.0.0
       container_name: schema-registry
       hostname: schema-registry
       depends_on: [kafka-1, kafka-2, kafka-3]
       ports:
         - "8081:8081"
       environment:
         SCHEMA_REGISTRY_HOST_NAME: schema-registry
         SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
         # Registry là 1 Kafka client: dùng listener NỘI BỘ của broker (bẫy advertised.listeners Tuần 1)
         SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: PLAINTEXT://kafka-1:19092,PLAINTEXT://kafka-2:19092,PLAINTEXT://kafka-3:19092
         SCHEMA_REGISTRY_KAFKASTORE_TOPIC: _schemas              # mặc định; 1 partition, compacted, RF 3
         SCHEMA_REGISTRY_SCHEMA_COMPATIBILITY_LEVEL: backward    # mặc định global = BACKWARD
   ```
2. Khởi động và kiểm tra Registry sống + topic `_schemas`.

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.registry.yml
   docker compose up -d
   sleep 15
   curl -s localhost:8081/subjects            # → []  (chưa có subject)
   curl -s localhost:8081/config              # → {"compatibilityLevel":"BACKWARD"}
   kt --describe --topic _schemas             # PartitionCount: 1, Configs: cleanup.policy=compact,...
   ```
3. Tạo schema Avro v1 `~/kafka-labs/schemas/order-v1.avsc`.

   ```json
   {
     "type": "record",
     "name": "Order",
     "namespace": "com.acme.shop",
     "fields": [
       { "name": "orderId",    "type": "string" },
       { "name": "customerId", "type": "string" },
       { "name": "amount",     "type": "double" }
     ]
   }
   ```
4. Tạo `~/kafka-labs/avro-producer.mjs` — đăng ký schema rồi produce 5 record Avro, in 5 byte đầu.

   ```javascript
   // ~/kafka-labs/avro-producer.mjs — Lab 5.1
   import { readFileSync } from "node:fs";
   import { Kafka, logLevel } from "kafkajs";
   import { SchemaRegistry, SchemaType } from "@kafkajs/confluent-schema-registry";

   const TOPIC = "orders";
   const SCHEMA_FILE = process.env.SCHEMA ?? "./schemas/order-v1.avsc";
   const registry = new SchemaRegistry({ host: "http://localhost:8081" });

   // 1) Đăng ký schema dưới subject <topic>-value (TopicNameStrategy). Tương đương "CI/CD đăng ký" khi auto.register.schemas=false.
   //    Thư viện mặc định đặt subject = <namespace>.<name> → PHẢI truyền subject rõ ràng.
   const { id } = await registry.register(
     { type: SchemaType.AVRO, schema: readFileSync(SCHEMA_FILE, "utf8") },
     { subject: `${TOPIC}-value` },
   );
   console.log(`schema registered: subject=${TOPIC}-value id=${id}`);

   // 2) Produce: encode() trả Buffer đã có 5 byte prefix (magic + schema ID) + Avro binary
   const kafka = new Kafka({ clientId: "avro-producer", brokers: ["localhost:9092", "localhost:9094", "localhost:9096"], logLevel: logLevel.WARN });
   const producer = kafka.producer();
   await producer.connect();
   for (let i = 1; i <= 5; i++) {
     const order = { orderId: `o-${i}`, customerId: `c-${i % 2}`, amount: i * 10.5 };
     if (SCHEMA_FILE.includes("v2")) order.currency = "USD";        // Lab 5.2; union ["null","string"] không mơ hồ nên avsc nhận giá trị trần (nếu lỗi: { string: "USD" })
     const value = await registry.encode(id, order);
     console.log(
       `sent ${order.orderId}: magic=0x${value[0].toString(16).padStart(2, "0")} ` +
       `schemaId=${value.readInt32BE(1)} prefixHex=${value.subarray(0, 5).toString("hex")} ` +
       `avroBytes=${value.length - 5} totalBytes=${value.length} (JSON would be ${JSON.stringify(order).length})`,
     );
     await producer.send({ topic: TOPIC, messages: [{ key: order.customerId, value }] });
   }
   await producer.disconnect();
   ```
5. Tạo `~/kafka-labs/avro-consumer.mjs`.

   ```javascript
   // ~/kafka-labs/avro-consumer.mjs — Lab 5.1
   import { Kafka, logLevel } from "kafkajs";
   import { SchemaRegistry } from "@kafkajs/confluent-schema-registry";

   const TOPIC = "orders";
   const registry = new SchemaRegistry({ host: "http://localhost:8081" });
   const kafka = new Kafka({ clientId: "avro-consumer", brokers: ["localhost:9092", "localhost:9094", "localhost:9096"], logLevel: logLevel.WARN });
   const consumer = kafka.consumer({ groupId: process.env.GROUP ?? "avro-consumer" });
   await consumer.connect();
   await consumer.subscribe({ topic: TOPIC, fromBeginning: true });
   await consumer.run({
     eachMessage: async ({ partition, message }) => {
       const schemaId = message.value.readInt32BE(1);          // byte 1..4 — deserializer thật cũng đọc thế này
       const decoded = await registry.decode(message.value);   // tra schema theo ID (cache), giải mã Avro
       console.log(`p${partition} off=${message.offset} key=${message.key} schemaId=${schemaId} value=${JSON.stringify(decoded)}`);
     },
   });
   process.on("SIGINT", async () => { await consumer.disconnect(); process.exit(0); });
   ```
6. Chạy producer, rồi consumer (terminal 2).

   ```bash
   cd ~/kafka-labs && node avro-producer.mjs
   # schema registered: subject=orders-value id=1
   # sent o-1: magic=0x00 schemaId=1 prefixHex=0000000001 avroBytes=17 totalBytes=22 (JSON would be 52)
   # ...
   node avro-consumer.mjs      # terminal 2 — in 5 record đã decode, Ctrl+C để dừng
   ```
7. **Bẫy wire format:** đọc topic bằng console consumer **thường** và soi byte.

   ```bash
   kcc --topic orders --from-beginning --max-messages 3
   # mỗi dòng bắt đầu bằng ký tự lạ (5 byte: 00 00 00 00 01) rồi chuỗi nhị phân Avro: ...o-1...c-1...
   docker exec kafka-1 /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-1:19092 \
     --topic orders --from-beginning --max-messages 1 2>/dev/null | od -A d -t x1 | head -2
   # 0000000 00 00 00 00 01 06 6f 2d 31 ...   ← byte 0 = magic, byte 1-4 = 00000001 = schema ID 1
   ```
8. Đối chiếu ID với REST API, và chứng minh **ID toàn cục / version theo subject**.

   ```bash
   curl -s localhost:8081/subjects                              # ["orders-value"]
   curl -s localhost:8081/subjects/orders-value/versions        # [1]
   curl -s localhost:8081/subjects/orders-value/versions/latest | jq '{subject,id,version}'
   curl -s localhost:8081/schemas/ids/1 | jq -r .schema | jq .  # đúng schema đã đăng ký

   # Đăng ký CÙNG schema dưới subject khác → cùng id=1, nhưng version=1 của subject mới
   jq -Rs '{schema: .}' schemas/order-v1.avsc > /tmp/body-v1.json
   curl -s -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
     --data @/tmp/body-v1.json localhost:8081/subjects/orders-archive-value/versions   # {"id":1}
   curl -s localhost:8081/schemas/ids/1/versions   # [{"subject":"orders-archive-value","version":1},{"subject":"orders-value","version":1}]
   ```

### ✅ Kiểm chứng

- `curl localhost:8081/subjects` có `orders-value`; `avro-producer.mjs` in `schemaId=1`, `prefixHex=0000000001`; Avro payload nhỏ hơn JSON ~2–3 lần.
- `od` in 5 byte đầu `00 00 00 00 01`; `kcc` thường in ký tự lạ → chính là **bẫy đề** "console consumer shows garbage".
- Cùng schema ở subject thứ hai → **cùng ID 1**; `_schemas` có **1 partition, compact**.

### 🧹 Dọn dẹp

```bash
# GIỮ Registry + topic orders cho Lab 5.2. Chỉ xoá subject phụ:
curl -s -X DELETE localhost:8081/subjects/orders-archive-value          # soft delete → [1]
curl -s -X DELETE "localhost:8081/subjects/orders-archive-value?permanent=true"
```

### 🧠 Ý nghĩa với đề thi

- Wire format **5 byte** là câu hỏi nhận diện: thấy "vài byte lạ đầu record" → Schema Registry serializer; dùng `kafka-avro-console-consumer`/`KafkaAvroDeserializer`.
- Schema **ID** nằm trong payload (toàn cục); **version** chỉ có nghĩa trong subject; `GET /schemas/ids/<id>` là cách deserializer tra schema.
- Registry là 1 Kafka client (`kafkastore.bootstrap.servers`), lưu state trong `_schemas` → sập Registry không mất schema; client đã cache vẫn chạy.
- Đăng ký schema **bằng tay/REST** (như ở đây) chính là mô hình production `auto.register.schemas=false`.

---

## Lab 5.2 — Schema evolution: 409 incompatible, default value, đổi compatibility qua REST

**🎯 Mục tiêu:** Ở `BACKWARD` (mặc định) thêm field **không default** → **HTTP 409**; thêm field **có default** → version 2; test compatibility bằng REST trước khi đăng ký; đổi `PUT /config/orders-value` sang `FORWARD` rồi `FULL` và thử lại từng thao tác → tự điền ma trận compatibility bằng kết quả thật.
**🧩 Luyện kỹ năng (liên quan đề):**

- `POST /compatibility/subjects/<s>/versions/latest?verbose=true` → `is_compatible` + lý do.
- `PUT /config/<subject>` (subject-level ưu tiên global); `DELETE /config/<subject>` về global.
- Thao tác được phép theo BACKWARD / FORWARD / FULL và thứ tự nâng cấp.

**⏱️ ~25 phút** · **Yêu cầu trước:** Lab 5.1 (subject `orders-value` version 1).

### Các bước

1. Tạo 3 schema ứng viên trong `~/kafka-labs/schemas/`.

   ```bash
   cd ~/kafka-labs/schemas
   # v2-bad: thêm field currency KHÔNG default
   jq '.fields += [{"name":"currency","type":"string"}]' order-v1.avsc > order-v2-bad.avsc
   # v2-good: thêm field currency CÓ default (nullable, null đứng trước trong union)
   jq '.fields += [{"name":"currency","type":["null","string"],"default":null}]' order-v1.avsc > order-v2-good.avsc
   # v3-drop: từ v2-good, XOÁ field amount (field không default)
   jq 'del(.fields[] | select(.name=="amount"))' order-v2-good.avsc > order-v3-drop.avsc
   cd ~/kafka-labs
   # Hàm tiện: test compatibility & register
   sr_test()     { jq -Rs '{schema: .}' "$1" | curl -s -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" --data @- "localhost:8081/compatibility/subjects/orders-value/versions/latest?verbose=true"; echo; }
   sr_register() { jq -Rs '{schema: .}' "$1" | curl -s -w " HTTP %{http_code}\n" -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" --data @- localhost:8081/subjects/orders-value/versions; }
   ```
2. **BACKWARD** (mặc định): thêm field không default → 409.

   ```bash
   sr_test schemas/order-v2-bad.avsc
   # {"is_compatible":false,"messages":["{errorType:'READER_FIELD_MISSING_DEFAULT_VALUE', description:'The field 'currency' at path '/fields/3' in the new schema has no default value and is missing in the old schema', ...}"]}
   sr_register schemas/order-v2-bad.avsc
   # {"error_code":409,"message":"Schema being registered is incompatible with an earlier schema for subject \"orders-value\", details: [...]"} HTTP 409
   ```
3. Thêm field **có default** → OK, thành version 2 (ID mới = 2 vì chuỗi schema khác).

   ```bash
   sr_test schemas/order-v2-good.avsc          # {"is_compatible":true}
   sr_register schemas/order-v2-good.avsc      # {"id":2} HTTP 200
   curl -s localhost:8081/subjects/orders-value/versions        # [1,2]
   ```
4. Xoá field (không default) ở BACKWARD → **được** (consumer mới chỉ bỏ qua field cũ).

   ```bash
   sr_test schemas/order-v3-drop.avsc          # {"is_compatible":true}   ← KHÔNG đăng ký, để giữ latest = v2-good
   ```
5. Đổi subject sang **FORWARD** và thử lại 2 thao tác.

   ```bash
   curl -s -X PUT -H "Content-Type: application/vnd.schemaregistry.v1+json" \
     --data '{"compatibility":"FORWARD"}' localhost:8081/config/orders-value     # {"compatibility":"FORWARD"}
   curl -s localhost:8081/config/orders-value                                    # {"compatibilityLevel":"FORWARD"}
   curl -s localhost:8081/config                                                 # global vẫn BACKWARD

   # Thêm field bắt buộc (dựng từ v2-good để so với latest): FORWARD → ĐƯỢC (consumer cũ bỏ qua field mới)
   jq '.fields += [{"name":"channel","type":"string"}]' schemas/order-v2-good.avsc > schemas/order-v3-addreq.avsc
   sr_test schemas/order-v3-addreq.avsc        # {"is_compatible":true}
   # Xoá field không default (amount): FORWARD → KHÔNG (consumer cũ cần amount, không có default để điền)
   sr_test schemas/order-v3-drop.avsc          # {"is_compatible":false,... READER_FIELD_MISSING_DEFAULT_VALUE ...}
   # Xoá field CÓ default (currency): FORWARD → ĐƯỢC
   jq 'del(.fields[] | select(.name=="currency"))' schemas/order-v2-good.avsc > schemas/order-v3-dropopt.avsc
   sr_test schemas/order-v3-dropopt.avsc       # {"is_compatible":true}
   ```
6. Đổi sang **FULL** → chỉ thao tác trên field có default mới qua.

   ```bash
   curl -s -X PUT -H "Content-Type: application/vnd.schemaregistry.v1+json" \
     --data '{"compatibility":"FULL"}' localhost:8081/config/orders-value
   sr_test schemas/order-v3-addreq.avsc        # false  (thêm field không default)
   sr_test schemas/order-v3-drop.avsc          # false  (xoá field không default)
   sr_test schemas/order-v3-dropopt.avsc       # true   (xoá field có default)
   jq '.fields += [{"name":"channel","type":["null","string"],"default":null}]' schemas/order-v2-good.avsc > schemas/order-v3-addopt.avsc
   sr_test schemas/order-v3-addopt.avsc        # true   (thêm field có default)
   ```
7. Điền ma trận từ kết quả thật (so với README mục 6):

   | Thao tác (so với v2-good) | BACKWARD | FORWARD | FULL |
   |---|---|---|---|
   | Thêm `channel` không default | ❌ (bước 2) | ✅ | ❌ |
   | Thêm `channel` có default | ✅ | ✅ | ✅ |
   | Xoá `amount` (không default) | ✅ (bước 4) | ❌ | ❌ |
   | Xoá `currency` (có default) | ✅ | ✅ | ✅ |
8. Produce bằng schema **v2** rồi consume bằng consumer cũ (không đổi code) — thấy field mới xuất hiện vì deserializer luôn tra **writer schema theo ID**.

   ```bash
   curl -s -X DELETE localhost:8081/config/orders-value     # bỏ override → về global BACKWARD
   SCHEMA=./schemas/order-v2-good.avsc node avro-producer.mjs   # schemaId=2
   GROUP=avro-consumer-v2 node avro-consumer.mjs                 # record cũ schemaId=1 không có currency, record mới schemaId=2 có currency=USD → Ctrl+C
   ```

### ✅ Kiểm chứng

- Bước 2 trả **HTTP 409** + `READER_FIELD_MISSING_DEFAULT_VALUE`; bước 3 trả `{"id":2}` và versions `[1,2]`.
- `GET /config/orders-value` phản ánh đúng mode vừa `PUT`; `GET /config` global vẫn `BACKWARD` (subject-level ưu tiên).
- Ma trận bước 7 khớp bảng README: BACKWARD cho xoá bất kỳ / thêm có default; FORWARD cho thêm bất kỳ / xoá có default; FULL chỉ field có default.

### 🧹 Dọn dẹp

```bash
curl -s -X DELETE localhost:8081/config/orders-value 2>/dev/null   # chắc chắn về global
rm -f ~/kafka-labs/schemas/order-v3-*.avsc
# GIỮ topic orders + subject orders-value (2 version) — Lab 5.3 trở đi không cần nhưng vô hại.
```

### 🧠 Ý nghĩa với đề thi

- **409** = incompatible với mode hiện tại; sửa bằng **default value**, không phải `NONE`.
- BACKWARD = *schema mới đọc data cũ* → **consumer trước**; FORWARD = *schema cũ đọc data mới* → **producer trước**; FULL = chỉ field có default, thứ tự tuỳ ý.
- Test trước bằng `/compatibility/...` là việc của **CI/CD** khi `auto.register.schemas=false`.
- Subject-level config **ưu tiên** global; `DELETE /config/<s>` quay về global.

---

## Lab 5.3 — Connect distributed: worker, internal topics, REST API

**🎯 Mục tiêu:** Chạy `confluentinc/cp-kafka-connect:8.0.0` (REST **8083**) ở **distributed mode** chồng lên cluster; kiểm tra 3 internal topic (`connect-configs` 1 / `connect-offsets` 25 / `connect-status` 5, đều compacted) bằng `kt`; gọi `GET /`, `GET /connector-plugins`, `GET /connectors`.
**🧩 Luyện kỹ năng (liên quan đề):**

- Worker config: `group.id`, `config/offset/status.storage.topic`, `key/value.converter`, `plugin.path`, `offset.flush.interval.ms`.
- FileStream connector từ Kafka 3.2 **không** nằm trên classpath mặc định → phải thêm vào `plugin.path`.
- Converter đặt ở **worker**, connector override được.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung (Registry không bắt buộc nhưng để chạy).

### Các bước

1. Tạo `~/kafka-labs/docker-compose.connect.yml`.

   ```yaml
   # ~/kafka-labs/docker-compose.connect.yml — override: thêm 1 worker Kafka Connect (distributed mode)
   # REST: http://localhost:8083 · thư mục ./connect-data mount vào /data cho FileStream connector
   services:
     connect:
       image: confluentinc/cp-kafka-connect:8.0.0
       container_name: connect
       hostname: connect
       depends_on: [kafka-1, kafka-2, kafka-3]
       ports:
         - "8083:8083"
       volumes:
         - ./connect-data:/data
       environment:
         CONNECT_BOOTSTRAP_SERVERS: kafka-1:19092,kafka-2:19092,kafka-3:19092
         CONNECT_REST_PORT: 8083
         CONNECT_REST_ADVERTISED_HOST_NAME: connect          # worker khác dùng tên này để forward request tới leader
         # ---- Distributed mode: group + 3 internal topic (compacted). RF=3 vì cluster có min.insync.replicas=2 ----
         CONNECT_GROUP_ID: connect-cluster                    # KHÔNG được trùng consumer group nào
         CONNECT_CONFIG_STORAGE_TOPIC: connect-configs        # bắt buộc 1 partition
         CONNECT_OFFSET_STORAGE_TOPIC: connect-offsets        # mặc định 25 partition
         CONNECT_STATUS_STORAGE_TOPIC: connect-status         # mặc định 5 partition
         CONNECT_CONFIG_STORAGE_REPLICATION_FACTOR: 3
         CONNECT_OFFSET_STORAGE_REPLICATION_FACTOR: 3
         CONNECT_STATUS_STORAGE_REPLICATION_FACTOR: 3
         # ---- Converter mặc định của worker (connector có thể override) ----
         CONNECT_KEY_CONVERTER: org.apache.kafka.connect.storage.StringConverter
         CONNECT_VALUE_CONVERTER: org.apache.kafka.connect.json.JsonConverter
         CONNECT_VALUE_CONVERTER_SCHEMAS_ENABLE: "false"      # mặc định true → envelope {"schema","payload"}
         # ---- Plugin ----
         CONNECT_PLUGIN_PATH: /usr/share/java,/usr/share/confluent-hub-components,/usr/share/filestream-connectors
         # ---- Tiện lab: flush offset mỗi 10 s (mặc định 60000) ----
         CONNECT_OFFSET_FLUSH_INTERVAL_MS: 10000
   ```
2. Khởi động (thêm file connect vào `COMPOSE_FILE`) và chờ REST lên (~40–60 s).

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.registry.yml:docker-compose.connect.yml
   docker compose up -d
   until curl -s localhost:8083/ >/dev/null; do sleep 3; echo "waiting connect..."; done
   curl -s localhost:8083/ | jq          # {"version":"8.0.0-ccs","commit":"...","kafka_cluster_id":"MkU3OEVBNTcwNTJENDM2Qk"}
   ```
3. Kiểm tra 3 internal topic.

   ```bash
   kt --list | grep '^connect-'
   for t in connect-configs connect-offsets connect-status; do kt --describe --topic $t | head -1; done
   # Topic: connect-configs  PartitionCount: 1   ReplicationFactor: 3  Configs: min.insync.replicas=2,cleanup.policy=compact
   # Topic: connect-offsets  PartitionCount: 25  ReplicationFactor: 3  Configs: ...cleanup.policy=compact
   # Topic: connect-status   PartitionCount: 5   ReplicationFactor: 3  Configs: ...cleanup.policy=compact
   ```
4. Xem plugin đã cài và connector hiện có.

   ```bash
   curl -s localhost:8083/connector-plugins | jq -r '.[] | "\(.type)\t\(.class)"' | sort
   # sink   org.apache.kafka.connect.file.FileStreamSinkConnector
   # source org.apache.kafka.connect.file.FileStreamSourceConnector
   # source org.apache.kafka.connect.mirror.MirrorSourceConnector / MirrorCheckpointConnector / MirrorHeartbeatConnector  (MirrorMaker 2 — Tuần 8)
   curl -s "localhost:8083/connector-plugins?connectorsOnly=false" | jq -r '.[] | select(.type=="converter" or .type=="transformation") | "\(.type)\t\(.class)"' | sort | head -30
   curl -s localhost:8083/connectors      # []
   ```
5. Thử **validate** config trước khi tạo (bắt lỗi thiếu field bắt buộc).

   ```bash
   curl -s -X PUT -H "Content-Type: application/json" \
     --data '{"connector.class":"org.apache.kafka.connect.file.FileStreamSourceConnector","tasks.max":"1"}' \
     localhost:8083/connector-plugins/org.apache.kafka.connect.file.FileStreamSourceConnector/config/validate | jq '{error_count, errors: [.configs[] | select(.value.errors|length>0) | {name: .definition.name, errors: .value.errors}]}'
   # error_count: 1 → "topic": Missing required configuration "topic" which has no default value.
   ```
6. Soi config thật của worker để đối chiếu số liệu.

   ```bash
   docker exec connect bash -c 'grep -E "^(group.id|offset.storage|config.storage|status.storage|plugin.path|offset.flush|connector.client.config.override.policy|exactly.once)" /etc/kafka-connect/kafka-connect.properties'
   ```

### ✅ Kiểm chứng

- `GET /` trả `kafka_cluster_id` = `CLUSTER_ID` của compose Tuần 1 (Connect là client của cluster).
- 3 topic `connect-*` với partition **1 / 25 / 5**, `cleanup.policy=compact`, RF 3.
- `connector-plugins` liệt kê `FileStreamSourceConnector`/`FileStreamSinkConnector` (nhờ `plugin.path` có `/usr/share/filestream-connectors`) và bộ MirrorMaker 2.
- Validate báo thiếu `topic` với `error_count: 1`.

### 🧹 Dọn dẹp

```bash
# GIỮ worker cho Lab 5.4 → 5.7. Không xoá gì.
```

### 🧠 Ý nghĩa với đề thi

- Distributed = `group.id` + **3 topic compacted** (1/25/5) + REST 8083; connector **không** cấu hình qua CLI.
- Converter là **worker default**, connector override (`value.converter` trong config connector).
- `plugin.path` + class loader isolation; plugin phải có trên **mọi** worker.
- `PUT /connector-plugins/<class>/config/validate` là endpoint validate — đề hỏi "kiểm tra config trước khi tạo".

---

## Lab 5.4 — FileStreamSource → topic → FileStreamSink với SMT `HoistField` → `InsertField` → `RegexRouter` ⭐

**🎯 Mục tiêu:** Pipeline file → Kafka → file hoàn toàn bằng cấu hình. Source dùng chain 3 SMT (theo **thứ tự**): bọc dòng text vào struct, thêm field metadata, **đổi tên topic đích** bằng regex. Sink thêm `partition`/`offset` bằng `InsertField` rồi ghi file. Thấy `tasks.max` chỉ là trần và lỗi khi **đảo thứ tự** SMT.
**🧩 Luyện kỹ năng (liên quan đề):**

- SMT chain thứ tự = thứ tự áp dụng; `$Value`/`$Key`; `RegexRouter` ở source đổi topic Kafka.
- `InsertField` với `static.field`, `topic.field` (source) và `partition.field`, `offset.field` (chỉ sink).
- Source: SMT → converter; sink: converter → SMT; `topics` bắt buộc cho sink.
- `tasks.max` là trần (FileStreamSource luôn 1 task; sink ≤ số partition).

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 5.3 đang chạy.

### Các bước

1. Chuẩn bị file đầu vào và topic đích (3 partition để sink có thể chạy 2 task).

   ```bash
   cd ~/kafka-labs
   chmod 777 connect-data                       # Linux: user appuser (uid 1000) trong container cần quyền ghi
   printf 'line-1 hello\nline-2 kafka\nline-3 connect\n' > connect-data/input.txt
   kt --create --topic lines-enriched --partitions 3 --replication-factor 3
   ```
2. Tạo `~/kafka-labs/file-source.json` — chú ý topic khai báo là `raw-lines` nhưng sẽ bị `RegexRouter` đổi thành `lines-enriched`.

   ```json
   {
     "name": "file-source",
     "config": {
       "connector.class": "org.apache.kafka.connect.file.FileStreamSourceConnector",
       "tasks.max": "3",
       "file": "/data/input.txt",
       "topic": "raw-lines",
       "transforms": "wrap,addMeta,route",
       "transforms.wrap.type": "org.apache.kafka.connect.transforms.HoistField$Value",
       "transforms.wrap.field": "line",
       "transforms.addMeta.type": "org.apache.kafka.connect.transforms.InsertField$Value",
       "transforms.addMeta.static.field": "data_source",
       "transforms.addMeta.static.value": "file-source",
       "transforms.addMeta.topic.field": "src_topic",
       "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
       "transforms.route.regex": "raw-(.*)",
       "transforms.route.replacement": "$1-enriched"
     }
   }
   ```
3. Tạo connector, xem status và số task.

   ```bash
   curl -s -X POST -H "Content-Type: application/json" --data @file-source.json localhost:8083/connectors | jq .name
   sleep 5
   curl -s localhost:8083/connectors/file-source/status | jq '{connector: .connector.state, tasks: [.tasks[] | {id, state}]}'
   # tasks: [{"id":0,"state":"RUNNING"}]  ← chỉ 1 task dù tasks.max=3 (FileStreamSource không chia được file)
   curl -s localhost:8083/connectors/file-source/tasks | jq length     # 1
   ```
4. Đọc topic đích — tên đã đổi, value là JSON (worker `JsonConverter`, `schemas.enable=false`) có field mới.

   ```bash
   kt --list | grep lines            # chỉ có lines-enriched, KHÔNG có raw-lines
   kcc --topic lines-enriched --from-beginning --property print.partition=true --timeout-ms 5000
   # Partition:1  {"line":"line-1 hello","data_source":"file-source","src_topic":"raw-lines"}
   # ...
   ```
   > 🧠 `src_topic` = `raw-lines` chứ không phải `lines-enriched` vì `InsertField` chạy **trước** `RegexRouter` trong chain — bằng chứng "thứ tự = thứ tự áp dụng".
5. Tạo `~/kafka-labs/file-sink.json` — sink đọc `lines-enriched`, thêm toạ độ Kafka bằng `InsertField` (chỉ sink có `partition.field`/`offset.field`), ghi ra file.

   ```json
   {
     "name": "file-sink",
     "config": {
       "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
       "tasks.max": "2",
       "topics": "lines-enriched",
       "file": "/data/output.txt",
       "transforms": "addCoords",
       "transforms.addCoords.type": "org.apache.kafka.connect.transforms.InsertField$Value",
       "transforms.addCoords.partition.field": "kafka_partition",
       "transforms.addCoords.offset.field": "kafka_offset",
       "transforms.addCoords.timestamp.field": "kafka_ts"
     }
   }
   ```
   ```bash
   curl -s -X POST -H "Content-Type: application/json" --data @file-sink.json localhost:8083/connectors | jq .name
   sleep 8
   curl -s localhost:8083/connectors/file-sink/status | jq '[.tasks[] | {id, state}]'    # 2 task RUNNING (≤ 3 partition)
   cat connect-data/output.txt
   # {line=line-1 hello, data_source=file-source, src_topic=raw-lines, kafka_partition=1, kafka_offset=0, kafka_ts=Mon Sep 15 ...}
   ```
   > 📌 FileStreamSink ghi `value.toString()` — với JSON schemaless value là `Map` nên in kiểu `{k=v}` của Java. Muốn ra JSON chuẩn thì đổi sink sang `StringConverter` nhưng khi đó `InsertField` **không** chạy được (value là String, không phải Map/Struct) — hãy thử để thấy lỗi.
6. Tail file: thêm dòng vào `input.txt` → source đọc tiếp (giữ offset là vị trí byte trong file), sink ghi tiếp.

   ```bash
   printf 'line-4 tail works\n' >> connect-data/input.txt
   sleep 10 && tail -1 connect-data/output.txt
   ```
7. **Thí nghiệm đảo thứ tự SMT** → lỗi vì `InsertField` nhận String thay vì Map.

   ```bash
   jq '.config.transforms = "addMeta,wrap,route"' file-source.json | jq .config > /tmp/bad-order.json
   curl -s -X PUT -H "Content-Type: application/json" --data @/tmp/bad-order.json localhost:8083/connectors/file-source/config >/dev/null
   printf 'line-5 will fail\n' >> connect-data/input.txt
   sleep 8
   curl -s localhost:8083/connectors/file-source/status | jq '{tasks: [.tasks[] | {id, state, trace: (.trace // "" | split("\n")[0])}]}'
   # state: "FAILED", trace: "org.apache.kafka.connect.errors.ConnectException: Tolerance exceeded in error handler" (nguyên nhân sâu: DataException: Only Map objects supported in absence of schema, found: java.lang.String)
   ```
8. Sửa lại thứ tự bằng `PUT .../config` rồi **restart task** (task FAILED không tự hồi).

   ```bash
   jq .config file-source.json | curl -s -X PUT -H "Content-Type: application/json" --data @- localhost:8083/connectors/file-source/config >/dev/null
   curl -s -X POST "localhost:8083/connectors/file-source/restart?includeTasks=true&onlyFailed=true"
   sleep 8
   curl -s localhost:8083/connectors/file-source/status | jq '[.tasks[] | .state]'     # ["RUNNING"]
   tail -2 connect-data/output.txt                                                        # line-5 đã qua
   ```

### ✅ Kiểm chứng

- Không có topic `raw-lines`; `lines-enriched` chứa JSON có `line`, `data_source`, `src_topic=raw-lines`.
- `file-source` chỉ **1 task** dù `tasks.max=3`; `file-sink` **2 task** với `tasks.max=2`.
- `output.txt` có `kafka_partition`/`kafka_offset` do SMT ở sink thêm.
- Đảo chain → task **FAILED** với `Only Map objects supported`; sửa config + `restart?includeTasks=true&onlyFailed=true` → RUNNING.

### 🧹 Dọn dẹp

```bash
# GIỮ file-source + file-sink cho Lab 5.7. Nếu không làm 5.7 ngay:
# curl -s -X DELETE localhost:8083/connectors/file-sink; curl -s -X DELETE localhost:8083/connectors/file-source
```

### 🧠 Ý nghĩa với đề thi

- `transforms=a,b,c` áp dụng **đúng thứ tự**; SMT làm việc trên `Struct`/`Map`, không trên bytes/String.
- `RegexRouter` ở **source** đổi topic Kafka; ở sink đổi tên bảng/index đích.
- `InsertField`: `topic.field`/`static.field` mọi nơi; `partition.field`/`offset.field` **chỉ sink**.
- `tasks.max` là **trần**; task FAILED phải **restart qua REST**; `PUT /connectors/<n>/config` để đổi config không mất offset.

---

## Lab 5.5 — Error handling: `errors.tolerance=none` → task FAILED; `all` + DLQ + header `__connect.errors.*`

**🎯 Mục tiêu:** Sink `JsonConverter` với `schemas.enable=true` (envelope) đọc topic có record hỏng. Mặc định → task **FAILED** (đọc `trace`). Đổi sang `errors.tolerance=all` + `errors.deadletterqueue.topic.name` + `context.headers.enable` → record hỏng vào DLQ với header lỗi, pipeline chạy tiếp.
**🧩 Luyện kỹ năng (liên quan đề):**

- `errors.tolerance` none/all; `errors.log.enable`, `errors.log.include.messages`; `errors.retry.timeout`.
- DLQ **chỉ sink**; header `__connect.errors.stage=VALUE_CONVERTER`, `.exception.message`, `.topic/.partition/.offset`.
- DLQ record = **byte gốc** → replay được.

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 5.3 đang chạy.

### Các bước

1. Tạo topic và sink với converter **đòi envelope** (override converter của worker), error handling mặc định.

   ```bash
   cd ~/kafka-labs
   kt --create --topic json-orders --partitions 1 --replication-factor 3
   cat > json-sink.json <<'EOF'
   {
     "name": "json-sink",
     "config": {
       "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
       "tasks.max": "1",
       "topics": "json-orders",
       "file": "/data/json-out.txt",
       "value.converter": "org.apache.kafka.connect.json.JsonConverter",
       "value.converter.schemas.enable": "true"
     }
   }
   EOF
   curl -s -X POST -H "Content-Type: application/json" --data @json-sink.json localhost:8083/connectors | jq .name
   ```
2. Gửi 1 record **đúng envelope** và 1 record **JSON trần** (thiếu `schema`/`payload`).

   ```bash
   kcpi --topic json-orders <<'EOF'
   {"schema":{"type":"struct","name":"order","optional":false,"fields":[{"field":"id","type":"int32","optional":false},{"field":"status","type":"string","optional":false}]},"payload":{"id":1,"status":"PAID"}}
   {"id":2,"status":"PAID"}
   EOF
   sleep 8
   cat connect-data/json-out.txt                   # Struct{id=1,status=PAID}
   curl -s localhost:8083/connectors/json-sink/status | jq '{connector: .connector.state, task: .tasks[0].state, trace: (.tasks[0].trace // "" | split("\n") | map(select(test("DataException"))) | .[0])}'
   # connector: RUNNING, task: FAILED, trace: "...DataException: JsonConverter with schemas.enable requires \"schema\" and \"payload\" fields and may not contain additional fields..."
   ```
   > 🧠 Connector `RUNNING` nhưng task `FAILED` — trạng thái điển hình đề mô tả. Lỗi ở giai đoạn **VALUE_CONVERTER**, trước mọi SMT.
3. Bật tolerance + DLQ + header + log, rồi restart task.

   ```bash
   jq '.config + {
     "errors.tolerance": "all",
     "errors.log.enable": "true",
     "errors.log.include.messages": "true",
     "errors.deadletterqueue.topic.name": "dlq-json-sink",
     "errors.deadletterqueue.topic.replication.factor": "3",
     "errors.deadletterqueue.context.headers.enable": "true"
   }' json-sink.json | curl -s -X PUT -H "Content-Type: application/json" --data @- localhost:8083/connectors/json-sink/config >/dev/null
   curl -s -X POST "localhost:8083/connectors/json-sink/restart?includeTasks=true&onlyFailed=true"
   sleep 8
   curl -s localhost:8083/connectors/json-sink/status | jq '.tasks[0].state'      # "RUNNING"
   kt --list | grep dlq                                                            # dlq-json-sink (worker admin client tự tạo, 1 partition)
   ```
4. Đọc DLQ với header — record hỏng `{"id":2,...}` đã được chuyển sang đây **nguyên byte**.

   ```bash
   kcc --topic dlq-json-sink --from-beginning --property print.headers=true --timeout-ms 5000
   # __connect.errors.topic:json-orders,__connect.errors.partition:0,__connect.errors.offset:1,__connect.errors.connector.name:json-sink,__connect.errors.task.id:0,__connect.errors.stage:VALUE_CONVERTER,__connect.errors.class.name:org.apache.kafka.connect.json.JsonConverter,__connect.errors.exception.class.name:org.apache.kafka.connect.errors.DataException,__connect.errors.exception.message:JsonConverter with schemas.enable requires "schema" and "payload" fields...,__connect.errors.exception.stacktrace:...	{"id":2,"status":"PAID"}
   ```
5. Gửi thêm 1 record đúng + 1 record không phải JSON → pipeline **không dừng**, record hỏng vào DLQ.

   ```bash
   kcpi --topic json-orders <<'EOF'
   {"schema":{"type":"struct","name":"order","optional":false,"fields":[{"field":"id","type":"int32","optional":false},{"field":"status","type":"string","optional":false}]},"payload":{"id":3,"status":"SHIPPED"}}
   this is not json at all
   EOF
   sleep 8
   cat connect-data/json-out.txt                    # Struct{id=1,...} và Struct{id=3,...}
   kcc --topic dlq-json-sink --from-beginning --timeout-ms 5000 | wc -l          # 2 record hỏng
   docker compose logs connect 2>/dev/null | grep -c "Error encountered in task json-sink-0"   # errors.log.enable → có log
   kcg --describe --group connect-json-sink          # CURRENT-OFFSET = LOG-END-OFFSET = 4, LAG 0 → record hỏng đã được "skip"
   ```
6. (Đọc, không chạy) Thử cấu hình tương tự trên **source** `file-source`: `errors.deadletterqueue.topic.name` bị **bỏ qua** vì source không có DLQ — worker chỉ log warning. Đây là bẫy đề.

### ✅ Kiểm chứng

- Với mặc định (`errors.tolerance=none`): task **FAILED**, `trace` chứa `JsonConverter with schemas.enable requires "schema" and "payload"`.
- Với `all` + DLQ: topic `dlq-json-sink` được tự tạo; record hỏng có header `__connect.errors.stage=VALUE_CONVERTER` và **body y nguyên** record gốc.
- Consumer group `connect-json-sink` LAG = 0 → offset đi qua record hỏng.

### 🧹 Dọn dẹp

```bash
curl -s -X DELETE localhost:8083/connectors/json-sink
kt --delete --topic json-orders
kt --delete --topic dlq-json-sink
rm -f ~/kafka-labs/connect-data/json-out.txt
```

### 🧠 Ý nghĩa với đề thi

- Mặc định `errors.tolerance=none` → **task FAILED**, không tự restart, không rebalance.
- Recipe DLQ (**sink only**): `errors.tolerance=all` + `errors.deadletterqueue.topic.name` + `errors.deadletterqueue.context.headers.enable=true`; `errors.log.include.messages` chỉ ghi vào **log**, cẩn thận PII.
- Sink lag đo qua consumer group **`connect-<name>`**.
- Header `__connect.errors.*` cho biết **stage** (`VALUE_CONVERTER` / `TRANSFORMATION` / `TASK_PUT`) và toạ độ gốc để replay.

---

## Lab 5.6 (tuỳ chọn) — Debezium PostgreSQL CDC: `op=c/u/d` + tombstone

**🎯 Mục tiêu:** Chạy `quay.io/debezium/connect` (một cluster Connect **thứ hai**, REST **8084**) + `postgres:16` (`wal_level=logical`); tạo connector `PostgresConnector`; INSERT/UPDATE/DELETE → đọc envelope `before/after/op` và **tombstone** trên topic `pg1.public.customers`.
**🧩 Luyện kỹ năng (liên quan đề):**

- CDC log-based bắt được DELETE (JDBC polling không); topic `<topic.prefix>.<schema>.<table>`; luôn 1 task.
- Hai cluster Connect trên cùng Kafka → **khác `group.id` và khác 3 internal topic**.
- Envelope Debezium; `REPLICA IDENTITY FULL` để có `before` đầy đủ; `tombstones.on.delete`.

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 5.3 (cluster + Registry đang chạy; worker `connect` có thể giữ).

### Các bước

1. Tạo `~/kafka-labs/docker-compose.debezium.yml`.

   ```yaml
   # ~/kafka-labs/docker-compose.debezium.yml — override: Postgres (logical WAL) + Connect cluster thứ 2 chạy Debezium
   # Debezium REST: http://localhost:8084 (container 8083) · Postgres: localhost:5432 (postgres/postgres, db shop)
   services:
     postgres:
       image: postgres:16
       container_name: postgres
       hostname: postgres
       command: ["postgres", "-c", "wal_level=logical", "-c", "max_wal_senders=4", "-c", "max_replication_slots=4"]
       ports:
         - "5432:5432"
       environment:
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: postgres
         POSTGRES_DB: shop

     debezium:
       image: quay.io/debezium/connect:3.1        # kiểm tra tag mới nhất tại quay.io/debezium/connect
       container_name: debezium
       hostname: debezium
       depends_on: [postgres, kafka-1, kafka-2, kafka-3]
       ports:
         - "8084:8083"
       environment:
         BOOTSTRAP_SERVERS: kafka-1:19092,kafka-2:19092,kafka-3:19092
         GROUP_ID: debezium-cluster                # KHÁC connect-cluster
         CONFIG_STORAGE_TOPIC: dbz-configs         # KHÁC connect-configs
         OFFSET_STORAGE_TOPIC: dbz-offsets
         STATUS_STORAGE_TOPIC: dbz-status
         CONFIG_STORAGE_REPLICATION_FACTOR: 3      # image mặc định 1 → sẽ fail vì min.insync.replicas=2
         OFFSET_STORAGE_REPLICATION_FACTOR: 3
         STATUS_STORAGE_REPLICATION_FACTOR: 3
         KEY_CONVERTER_SCHEMAS_ENABLE: "false"     # JsonConverter không envelope cho dễ đọc
         VALUE_CONVERTER_SCHEMAS_ENABLE: "false"
   ```
2. Khởi động, tạo bảng và bật `REPLICA IDENTITY FULL`.

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.registry.yml:docker-compose.connect.yml:docker-compose.debezium.yml
   docker compose up -d
   until curl -s localhost:8084/ >/dev/null; do sleep 3; echo "waiting debezium..."; done
   docker exec -i postgres psql -U postgres -d shop <<'EOF'
   CREATE TABLE customers (id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT);
   ALTER TABLE customers REPLICA IDENTITY FULL;   -- để before có đủ cột (mặc định chỉ PK)
   INSERT INTO customers (name, email) VALUES ('Alice', 'alice@acme.com');
   EOF
   kt --list | grep -E '^(dbz-|connect-)'           # 2 bộ internal topic tách biệt
   ```
3. Tạo connector Debezium qua REST 8084.

   ```bash
   cat > pg-cdc.json <<'EOF'
   {
     "name": "pg-cdc",
     "config": {
       "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
       "tasks.max": "1",
       "database.hostname": "postgres",
       "database.port": "5432",
       "database.user": "postgres",
       "database.password": "postgres",
       "database.dbname": "shop",
       "topic.prefix": "pg1",
       "plugin.name": "pgoutput",
       "slot.name": "dbz_shop",
       "publication.autocreate.mode": "filtered",
       "table.include.list": "public.customers",
       "snapshot.mode": "initial"
     }
   }
   EOF
   curl -s -X POST -H "Content-Type: application/json" --data @pg-cdc.json localhost:8084/connectors | jq .name
   sleep 10
   curl -s localhost:8084/connectors/pg-cdc/status | jq '[.connector.state, .tasks[0].state]'   # ["RUNNING","RUNNING"]
   kt --list | grep pg1                    # pg1.public.customers (+ pg1 schema-change topic)
   ```
4. Terminal 2: consume topic CDC với key + header; Terminal 1: chạy UPDATE và DELETE.

   ```bash
   # terminal 2
   kcc --topic pg1.public.customers --from-beginning --property print.key=true --property print.offset=true
   ```
   ```bash
   # terminal 1
   docker exec -i postgres psql -U postgres -d shop <<'EOF'
   UPDATE customers SET email = 'alice@example.org' WHERE id = 1;
   DELETE FROM customers WHERE id = 1;
   EOF
   ```
   Terminal 2 in 4 record (rút gọn):
   ```
   Offset:0  {"id":1}  {"before":null,"after":{"id":1,"name":"Alice","email":"alice@acme.com"},"source":{...,"snapshot":"last"},"op":"r",...}      ← snapshot ban đầu
   Offset:1  {"id":1}  {"before":{"id":1,"name":"Alice","email":"alice@acme.com"},"after":{"id":1,"name":"Alice","email":"alice@example.org"},"op":"u",...}
   Offset:2  {"id":1}  {"before":{"id":1,"name":"Alice","email":"alice@example.org"},"after":null,"op":"d",...}
   Offset:3  {"id":1}  null                                                                                                                       ← TOMBSTONE
   ```
5. Xem offset nguồn của connector (LSN) và 1 task duy nhất.

   ```bash
   curl -s localhost:8084/connectors/pg-cdc/offsets | jq        # partition {"server":"pg1"}, offset {"lsn":..., "txId":..., "ts_usec":...}
   curl -s localhost:8084/connectors/pg-cdc/tasks | jq length   # 1
   docker exec -i postgres psql -U postgres -d shop -c "SELECT slot_name, active, confirmed_flush_lsn FROM pg_replication_slots;"
   ```

### ✅ Kiểm chứng

- Topic `pg1.public.customers` có `op=r` (snapshot), `u`, `d` và **record null** cuối (tombstone) — cùng key `{"id":1}` → cùng partition.
- `before` của `u`/`d` đầy đủ cột nhờ `REPLICA IDENTITY FULL`.
- `kt --list` thấy 2 bộ internal topic `connect-*` và `dbz-*` — 2 cluster Connect sống chung 1 Kafka.

### 🧹 Dọn dẹp

```bash
curl -s -X DELETE localhost:8084/connectors/pg-cdc
docker exec -i postgres psql -U postgres -d shop -c "SELECT pg_drop_replication_slot('dbz_shop');" 2>/dev/null
docker compose stop debezium postgres && docker compose rm -f debezium postgres
kt --delete --topic pg1.public.customers; kt --delete --topic pg1 2>/dev/null
for t in dbz-configs dbz-offsets dbz-status; do kt --delete --topic $t; done
export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.registry.yml:docker-compose.connect.yml
rm -f ~/kafka-labs/pg-cdc.json
```

### 🧠 Ý nghĩa với đề thi

- "Capture deletes / no polling load on DB" → **Debezium CDC** (WAL/binlog), không phải JDBC source.
- Delete = `op=d` + **tombstone** (`tombstones.on.delete=true`); sink không chịu null → `Filter` + `RecordIsTombstone`.
- Debezium luôn **1 task**; offset = LSN trong `connect-offsets` (ở đây `dbz-offsets`).
- Replication slot giữ WAL → connector dừng lâu = đầy đĩa; dọn slot khi gỡ connector.

---

## Lab 5.7 — REST ops: pause/resume/restart, đọc `connect-offsets`, lag sink, reset offset

**🎯 Mục tiêu:** Vận hành `file-source`/`file-sink` từ Lab 5.4 bằng REST: pause sink → lag tăng (`kcg --describe --group connect-file-sink`) → resume; đọc key/value offset source trong `connect-offsets`; `stop` → `DELETE /offsets` → `resume` để source đọc lại file từ đầu; xoá connector rồi tạo lại → tiếp tục từ offset cũ.
**🧩 Luyện kỹ năng (liên quan đề):**

- Trạng thái `PAUSED`/`STOPPED`/`RUNNING`; `pause` giữ task, `stop` huỷ task giữ config+offset.
- Source offset = map `{"filename":...}` → `{"position":...}` trong `connect-offsets`; sink offset = consumer group `connect-<name>`.
- `DELETE /connectors/<n>` **không** xoá offset; reset = `stop` + `DELETE /connectors/<n>/offsets` (3.6+).

**⏱️ ~25 phút** · **Yêu cầu trước:** Lab 5.4 (file-source + file-sink RUNNING).

### Các bước

1. Pause sink, bơm thêm dòng → source vẫn produce, sink **lag** tăng.

   ```bash
   cd ~/kafka-labs
   curl -s -X PUT localhost:8083/connectors/file-sink/pause
   curl -s localhost:8083/connectors/file-sink/status | jq '[.connector.state, .tasks[].state]'   # ["PAUSED","PAUSED","PAUSED"]
   for i in 6 7 8; do echo "line-$i while paused" >> connect-data/input.txt; done
   sleep 8
   kcg --describe --group connect-file-sink
   # GROUP              TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID ...
   # connect-file-sink  lines-enriched  0..2       ...             ...             tổng LAG = 3 (task paused vẫn giữ membership → CONSUMER-ID có giá trị)
   ```
2. Resume → lag về 0, file output có 3 dòng mới.

   ```bash
   curl -s -X PUT localhost:8083/connectors/file-sink/resume
   sleep 8
   kcg --describe --group connect-file-sink | awk 'NR>1 {lag+=$6} END {print "total LAG:", lag}'    # 0
   tail -3 connect-data/output.txt
   ```
3. Đọc offset **source** trong topic `connect-offsets` và qua REST.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-1:19092 \
     --topic connect-offsets --from-beginning --property print.key=true --timeout-ms 5000 2>/dev/null | grep file-source | tail -1
   # ["file-source",{"filename":"/data/input.txt"}]	{"position":142}      ← key = [connector, sourcePartition], value = sourceOffset (byte position)
   curl -s localhost:8083/connectors/file-source/offsets | jq
   curl -s localhost:8083/connectors/file-sink/offsets | jq '.offsets[0]'     # sink: {"partition":{"kafka_topic":"lines-enriched","kafka_partition":0},"offset":{"kafka_offset":N}}
   ```
4. Restart source (connector + task) — không đổi offset.

   ```bash
   curl -s -X POST "localhost:8083/connectors/file-source/restart?includeTasks=true" -w "HTTP %{http_code}\n"    # 202/204
   sleep 5 && curl -s localhost:8083/connectors/file-source/status | jq '[.tasks[].state]'
   ```
5. **Xoá rồi tạo lại** cùng tên → tiếp tục từ offset cũ (không đọc lại file).

   ```bash
   LINES_BEFORE=$(ktotal lines-enriched)
   curl -s -X DELETE localhost:8083/connectors/file-source -w "HTTP %{http_code}\n"        # 204
   curl -s -X POST -H "Content-Type: application/json" --data @file-source.json localhost:8083/connectors >/dev/null
   sleep 10
   LINES_AFTER=$(ktotal lines-enriched)
   echo "before=$LINES_BEFORE after=$LINES_AFTER"       # bằng nhau → không re-ingest
   ```
6. **Reset offset đúng cách**: `stop` → `DELETE /offsets` → `resume` → source đọc lại từ byte 0 → topic nhận **duplicate** toàn bộ file (at-least-once là chuyện bình thường của Connect).

   ```bash
   curl -s -X PUT localhost:8083/connectors/file-source/stop
   sleep 3 && curl -s localhost:8083/connectors/file-source/status | jq '[.connector.state, (.tasks|length)]'    # ["STOPPED",0] — task đã huỷ
   curl -s -X DELETE localhost:8083/connectors/file-source/offsets | jq        # {"message":"The Connect framework-managed offsets for this connector have been reset successfully..."}
   curl -s -X PUT localhost:8083/connectors/file-source/resume
   sleep 10
   echo "total records: $(ktotal lines-enriched)"      # ≈ gấp đôi LINES_AFTER → file được đọc lại từ đầu
   ```
7. Thử `DELETE /offsets` khi connector đang RUNNING → bị từ chối.

   ```bash
   curl -s -X DELETE localhost:8083/connectors/file-source/offsets | jq -r .message    # "Connectors must be in the STOPPED state before their offsets can be modified..."
   ```

### ✅ Kiểm chứng

- Pause → trạng thái `PAUSED`, LAG group `connect-file-sink` > 0; resume → LAG 0.
- Key trong `connect-offsets` có dạng `["file-source",{"filename":"/data/input.txt"}]`, value `{"position":N}`.
- Xoá + tạo lại: số record topic **không đổi**; stop + `DELETE /offsets` + resume: số record **tăng gấp đôi**.
- `DELETE /offsets` khi RUNNING → lỗi yêu cầu `STOPPED`.

### 🧹 Dọn dẹp (kết thúc tuần)

```bash
cd ~/kafka-labs
for c in file-sink file-source; do curl -s -X DELETE localhost:8083/connectors/$c; done
kt --delete --topic lines-enriched
kt --delete --topic orders
curl -s -X DELETE localhost:8081/subjects/orders-value >/dev/null; curl -s -X DELETE "localhost:8081/subjects/orders-value?permanent=true" >/dev/null
rm -f connect-data/*.txt /tmp/body-v1.json /tmp/bad-order.json
# Tắt toàn bộ (cluster + registry + connect). GIỮ 3 file compose override + *.mjs + schemas/ cho Tuần 7/10.
export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.registry.yml:docker-compose.connect.yml
docker compose down
unset COMPOSE_FILE
```

### 🧠 Ý nghĩa với đề thi

- `pause` = task còn, không xử lý (giữ assignment); `stop` (3.5+) = huỷ task, giữ config + offset — điều kiện để sửa/reset offset.
- Source offset trong **`connect-offsets`** (key `[connector, sourcePartition]`); sink offset trong **consumer group `connect-<name>`** → 2 cách xem lag/offset khác nhau.
- **`DELETE /connectors/<n>` không xoá offset**; reset = `stop` → `DELETE /connectors/<n>/offsets` → `resume`.
- Source mặc định **at-least-once** (reset/crash → duplicate) → muốn EOS: KIP-618 (`exactly.once.source.support=enabled` + `exactly.once.support=required`).

---

> ✅ Xong 6–7 lab? Giữ lại `docker-compose.registry.yml`, `docker-compose.connect.yml`, `avro-producer.mjs`/`avro-consumer.mjs`, `schemas/` — Tuần 7 (contract test với Schema Registry) và Tuần 10 (capstone) dùng tiếp. Đối chiếu [Lab checklist trong README](README.md#-lab-checklist) rồi làm [bộ câu hỏi luyện tập](questions.md) trước khi sang Tuần 6.
