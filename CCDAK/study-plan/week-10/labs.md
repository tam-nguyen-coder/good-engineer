# 🏗️ Capstone — Tuần 10: **Order Pipeline** (ghép toàn bộ stack 9 tuần) ⭐

> Đây **KHÔNG** phải các lab rời — mà là **1 pipeline end-to-end** bạn tự tay ghép qua **7 bước nối tiếp**. Mỗi bước chồng thêm 1 lớp lên hệ thống đã có và ôn lại đúng những gì đã học ở các tuần trước. Chạy **hoàn toàn local** bằng Docker — không tốn phí. GIỮ mọi thứ chạy tới hết Bước 7, rồi chạy **🧹 Dọn dẹp toàn bộ**.
> ⚙️ Yêu cầu chung: `~/kafka-labs/` với 4 file compose đã dựng ở các tuần trước (`docker-compose.cluster.yml` Tuần 1, `docker-compose.registry.yml` + `docker-compose.connect.yml` Tuần 5, `docker-compose.monitoring.yml` Tuần 8), project `~/kafka-labs/streams-lab/` (Java 17 + Gradle, Tuần 6), Node.js 24 với `kafkajs@2` + `@kafkajs/confluent-schema-registry`, `curl`, `jq`. Cần **~8 GB RAM trống** (4 container Kafka + Schema Registry + Connect + Prometheus + Grafana + 2 JVM Streams). Tổng **~3.5h** (chia 2 ngày như lịch trong README: Bước 1–3 Ngày 2, Bước 4–7 Ngày 4).
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md)

---

## 🎯 Bạn sẽ build cái gì

Một pipeline xử lý đơn hàng "production-like" thu nhỏ:

- Service `order-svc` (Node.js, xác thực **SCRAM**) sinh **1.000 order Avro** (`Schema Registry`), key = `customerId`, producer **idempotent**; cố tình bơm **5 % record hỏng** vào topic `orders-raw-bad`.
- Consumer group **`fulfillment`** (Node.js, user `analytics`) đọc cả 2 topic, **commit thủ công**, **dedup idempotent** theo `eventId` (SQLite), retry lỗi tạm 3 lần rồi đẩy **`orders-dlq`**; poison pill đi thẳng DLQ.
- **Kafka Streams (Java)** join `orders` ⋈ `customers` (`KTable` compacted) → **tumbling window 1 phút** tổng tiền theo `country` → `order-stats`, `processing.guarantee=exactly_once_v2`, **2 instance** chia task.
- **Kafka Connect** `FileStreamSink` đọc `order-stats` (`read_committed`) + SMT `InsertField` + `errors.tolerance=all` + DLQ riêng.
- **Prometheus/Grafana** theo dõi `UnderReplicatedPartitions` + lag; **kill 1 broker** → không mất data; **kill 1 Streams instance** → task chuyển; **reset offset** `fulfillment` → replay **không xử lý trùng**.

### 🗺️ Sơ đồ kiến trúc

```
   Node.js (host)                                   Docker network (cluster Tuần 1 + override)
 ┌──────────────────┐  SASL/SCRAM :29092/4/6   ┌─────────────────────────────────────────────────────┐
 │ order-producer   │ ───────────────────────► │  orders (12p, RF3, min.isr 2)  ◄── Avro, key=customerId
 │ user: order-svc  │ ───────────────────────► │  orders-raw-bad (5 % garbage)                        │
 │ idempotent, Avro │                          │  customers (12p, compacted)  ◄── seed-customers.mjs   │
 └──────────────────┘                          └──────┬───────────────────────┬──────────────────────┘
        ▲ schema id                                   │                       │
 ┌──────┴───────────┐                                 │                       │  PLAINTEXT :9092/4/6 (ANONYMOUS = super.user)
 │ Schema Registry  │                                 ▼                       ▼
 │ :8081 (Tuần 5)   │                    ┌──────────────────────┐   ┌────────────────────────────────────┐
 └──────────────────┘                    │ fulfillment consumer │   │ Kafka Streams  order-stats-app     │
                                         │ user: analytics      │   │ 2 instance · EOS v2 · standby 1    │
                                         │ manual commit        │   │ orders ⋈ KTable(customers)         │
                                         │ dedup eventId(SQLite)│   │ → selectKey(country) → tumbling 1' │
                                         │ retry ×3 → orders-dlq│   └──────────────┬─────────────────────┘
                                         └──────────────────────┘                  ▼
                                                                          order-stats (6p)  ──► Connect FileStreamSink
                                                                                 │                 read_committed + InsertField
                                                                                 └─(record hỏng)──► order-stats-dlq
   Prometheus :9090 · Grafana :3000 (Tuần 8) ── JMX exporter :7071 trên 3 broker ── URP / lag
```

### 📌 Mỗi bước ôn lại tuần / domain nào

| Bước | Ghép gì | Ôn lại tuần | Domain CCDAK |
| --- | --- | --- | --- |
| **1** | Topics (`orders` 12p RF3 min.isr 2, `customers` compacted, `order-stats`, `orders-dlq`, `orders-raw-bad`), user SCRAM `order-svc`/`analytics`, ACL với `StandardAuthorizer` | Tuần 1, 2, 7 | FUND, DEV |
| **2** ⭐ | Producer Node Avro idempotent, key = `customerId`, 1.000 order + 50 record hỏng | Tuần 3, 5 | DEV |
| **3** ⭐ | Consumer group `fulfillment`: manual commit, dedup, retry → DLQ | Tuần 4, 9 | DEV |
| **4** ⭐ | Kafka Streams Java: join + tumbling 1 phút + `exactly_once_v2`, 2 instance | Tuần 6 | STREAMS |
| **5** | Connect `FileStreamSink` + SMT + `errors.tolerance=all` + DLQ | Tuần 5 | CONNECT |
| **6** ⭐ | Grafana URP/lag; kill broker → không mất data; kill Streams instance → task chuyển | Tuần 2, 8 | OBS, FUND |
| **7** ⭐ | `--reset-offsets --to-earliest` → replay không xử lý trùng | Tuần 4, 9 | DEV |

---

## 🔧 Chuẩn bị chung (làm 1 lần)

```bash
cd ~/kafka-labs
export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092        # alias kt/kcp/kcc/kcg/kcfg/kq Tuần 1 trỏ vào cluster 3 node
mkdir -p ~/kafka-labs/capstone/schemas ~/kafka-labs/connect-data
# Hàm tiện ích đã dùng ở Tuần 5 (định nghĩa lại nếu shell mới):
kcpi()   { docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS "$@"; }
ktotal() { docker exec $KAFKA_CTR /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_BS --topic "$1" | awk -F: '{s+=$3} END {print s+0}'; }
kacl()   { docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-acls.sh --bootstrap-server $KAFKA_BS "$@"; }
```

> 📌 2 file compose chuẩn được định nghĩa ở [Tuần 1 — Lab 1.1 / 1.2](../week-01/labs.md); `docker-compose.registry.yml` / `docker-compose.connect.yml` ở [Tuần 5](../week-05/labs.md); `docker-compose.monitoring.yml` ở [Tuần 8](../week-08/labs.md); project Streams ở [Tuần 6](../week-06/labs.md). Capstone **không in lại** các file đó — chỉ thêm **1 override mới** (`docker-compose.capstone-security.yml`, Bước 1) để bật SASL/SCRAM + `StandardAuthorizer` mà không đụng TLS của Tuần 7.
>
> Code Node.js đặt trong `~/kafka-labs/capstone/` (Node resolve `node_modules` ở `~/kafka-labs/` — không cần `npm i` lại). Code Java thêm vào project `~/kafka-labs/streams-lab/` sẵn có.

---

## Bước 1 — Hạ tầng, topic, user SCRAM & ACL

**🎯 Mục tiêu:** Dựng toàn bộ stack (cluster 3 broker + controller, Schema Registry, Connect, Prometheus/Grafana) **cộng** listener `SASL_PLAINTEXT` với SCRAM-SHA-512 và `StandardAuthorizer`; tạo 5 topic đúng spec; tạo user `order-svc` (chỉ ghi) và `analytics` (đọc + group + ghi DLQ); chứng minh user thiếu quyền bị `TopicAuthorizationException`.
**🧩 Luyện kỹ năng (liên quan đề):**

- Topic config: `--partitions 12 --replication-factor 3 --config min.insync.replicas=2`; `cleanup.policy=compact` cho bảng tham chiếu; **co-partitioning** (`customers` phải cùng 12 partition với `orders` để join KStream-KTable ở Bước 4).
- SCRAM trong KRaft: credential lưu trong metadata log, tạo runtime bằng `kafka-configs.sh --entity-type users` (KIP-554), không restart broker.
- ACL với `StandardAuthorizer` (KIP-801): shortcut `--producer` / `--consumer --group`; mặc định **deny**; `super.users`.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung; cluster đang **tắt** (`docker compose -f docker-compose.cluster.yml down` nếu còn chạy từ tuần trước).

### Các bước

1. Tạo override `~/kafka-labs/docker-compose.capstone-security.yml` — thêm listener `SASL` (host port **29092 / 29094 / 29096**) + authorizer. Mọi client PLAINTEXT hiện có (Schema Registry, Connect, Streams, CLI trong container) tiếp tục chạy với principal `User:ANONYMOUS` được khai là **super user**; chỉ client qua listener SASL bị ACL kiểm soát.

   ```yaml
   # ~/kafka-labs/docker-compose.capstone-security.yml — override: SASL/SCRAM listener + StandardAuthorizer
   # Chạy CHỒNG lên cluster Tuần 1 (+ registry/connect/monitoring). Không TLS để capstone nhẹ; production = SASL_SSL (Tuần 7).
   # Quy tắc env của image apache/kafka: KAFKA_ + tên property viết hoa, "." → "_", "_" → "__", "-" → "___".
   x-capstone-security: &capstone-security
     KAFKA_AUTHORIZER_CLASS_NAME: org.apache.kafka.metadata.authorizer.StandardAuthorizer   # KRaft authorizer (KIP-801); AclAuthorizer (ZK) đã gỡ ở 4.0
     KAFKA_SUPER_USERS: User:ANONYMOUS                          # client PLAINTEXT (inter-broker, SR, Connect, Streams, CLI) = super user; ngăn cách nhiều user bằng ";"
     KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: "false"              # mặc định false — ghi rõ để nhớ: không ACL khớp → DENY
     KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
     # listener.name.sasl.scram-sha-512.sasl.jaas.config  (server-side JAAS cho listener tên SASL)
     KAFKA_LISTENER_NAME_SASL_SCRAM___SHA___512_SASL_JAAS_CONFIG: org.apache.kafka.common.security.scram.ScramLoginModule required;

   services:
     controller:
       environment:
         KAFKA_AUTHORIZER_CLASS_NAME: org.apache.kafka.metadata.authorizer.StandardAuthorizer   # controller cũng phải chạy authorizer (ACL lưu trong __cluster_metadata)
         KAFKA_SUPER_USERS: User:ANONYMOUS

     kafka-1:
       ports: ["29092:29092"]
       environment:
         <<: *capstone-security
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9092,SASL://:29092
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:19092,PLAINTEXT_HOST://localhost:9092,SASL://localhost:29092
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SASL:SASL_PLAINTEXT

     kafka-2:
       ports: ["29094:29094"]
       environment:
         <<: *capstone-security
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9094,SASL://:29094
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-2:19092,PLAINTEXT_HOST://localhost:9094,SASL://localhost:29094
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SASL:SASL_PLAINTEXT

     kafka-3:
       ports: ["29096:29096"]
       environment:
         <<: *capstone-security
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9096,SASL://:29096
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-3:19092,PLAINTEXT_HOST://localhost:9096,SASL://localhost:29096
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SASL:SASL_PLAINTEXT
   ```

   > ⚠️ Nếu broker không lên và log báo kiểu `SASL mechanism SCRAM-SHA-512 ... JAAS configuration` (mapping env `___` không được image nhận), thay dòng `KAFKA_LISTENER_NAME_SASL_...` bằng file JAAS: tạo `~/kafka-labs/capstone/kafka_server_jaas.conf` nội dung `KafkaServer { org.apache.kafka.common.security.scram.ScramLoginModule required; };`, mount vào `/etc/kafka/jaas.conf` và thêm `KAFKA_OPTS: -Djava.security.auth.login.config=/etc/kafka/jaas.conf`. Lưu ý `docker-compose.monitoring.yml` (Tuần 8) cũng dùng `KAFKA_OPTS` cho `-javaagent` — khi đó gộp 2 flag vào **một** giá trị `KAFKA_OPTS`.
2. Khởi động **toàn bộ stack** bằng 5 file compose (đặt `COMPOSE_FILE` để khỏi gõ dài — dùng cho cả capstone và phần dọn dẹp).

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.registry.yml:docker-compose.connect.yml:docker-compose.monitoring.yml:docker-compose.capstone-security.yml
   docker compose up -d
   # tương đương: docker compose -f docker-compose.cluster.yml -f docker-compose.registry.yml -f docker-compose.connect.yml -f docker-compose.monitoring.yml -f docker-compose.capstone-security.yml up -d
   docker compose ps                                # controller, kafka-1/2/3, schema-registry, connect, prometheus, grafana: running
   until curl -s localhost:8081/subjects >/dev/null; do sleep 3; echo "waiting schema-registry..."; done
   until curl -s localhost:8083/ >/dev/null;         do sleep 3; echo "waiting connect...";         done
   kq describe --status | head -3                   # LeaderId: 1
   docker compose logs kafka-1 | grep -iE "authorizer|SASL" | tail -3   # thấy StandardAuthorizer loaded / SASL listener
   ```
3. Tạo 5 topic của pipeline (RF3, `min.insync.replicas=2` được broker áp mặc định — ghi rõ ở `orders` để nhớ).

   ```bash
   kt --create --topic orders          --partitions 12 --replication-factor 3 --config min.insync.replicas=2
   kt --create --topic orders-raw-bad  --partitions 12 --replication-factor 3
   kt --create --topic customers       --partitions 12 --replication-factor 3 --config cleanup.policy=compact --config min.cleanable.dirty.ratio=0.01 --config segment.ms=60000
   kt --create --topic order-stats     --partitions 6  --replication-factor 3
   kt --create --topic orders-dlq      --partitions 3  --replication-factor 3 --config retention.ms=604800000
   kt --describe --topic orders | head -2
   kt --describe --topic customers | head -1
   ```
4. Tạo 2 user SCRAM-SHA-512 (Admin API → lưu trong metadata log, **không restart**).

   ```bash
   kcfg --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=order-secret]'     --entity-type users --entity-name order-svc
   kcfg --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=analytics-secret]' --entity-type users --entity-name analytics
   kcfg --describe --entity-type users                     # 2 user, mechanism SCRAM-SHA-512, iterations 8192 (mặc định 4096)
   ```
5. Cấp ACL tối thiểu theo vai trò.

   ```bash
   # order-svc: chỉ GHI (Write + Describe + Create trên topic). Idempotent producer KHÔNG cần IdempotentWrite cluster từ 2.8 (KIP-679): có Write trên topic là đủ.
   kacl --add --allow-principal User:order-svc --producer --topic orders
   kacl --add --allow-principal User:order-svc --producer --topic orders-raw-bad
   # analytics: ĐỌC 2 topic (Read + Describe) + group fulfillment (Read) — shortcut --consumer
   kacl --add --allow-principal User:analytics --consumer --topic orders --topic orders-raw-bad --group fulfillment
   # analytics còn phải GHI được vào DLQ (consumer app produce record hỏng sang orders-dlq) — hay quên!
   kacl --add --allow-principal User:analytics --producer --topic orders-dlq
   kacl --list
   ```
6. Kiểm chứng ACL bằng Node — `~/kafka-labs/capstone/acl-check.mjs` thử **đúng** và **sai** vai trò.

   ```javascript
   // ~/kafka-labs/capstone/acl-check.mjs — Bước 1: user đúng quyền chạy được, user sai quyền bị AuthorizationException
   import { Kafka, logLevel } from "kafkajs";

   const SASL_BROKERS = ["localhost:29092", "localhost:29094", "localhost:29096"];   // listener SASL của override capstone
   const client = (username, password) =>
     new Kafka({
       clientId: `acl-check-${username}`,
       brokers: SASL_BROKERS,
       sasl: { mechanism: "scram-sha-512", username, password },   // Java: security.protocol=SASL_PLAINTEXT, sasl.mechanism=SCRAM-SHA-512, sasl.jaas.config=ScramLoginModule required username=... password=...
       logLevel: logLevel.NOTHING,
       retry: { retries: 1 },
     });

   async function attempt(label, fn) {
     try { await fn(); console.log(`✅ ${label}: OK`); }
     catch (e) { console.log(`❌ ${label}: ${e.name} — ${e.message}`); }
   }

   // 1) order-svc GHI orders → OK
   const svc = client("order-svc", "order-secret");
   const p1 = svc.producer(); await p1.connect();
   await attempt("order-svc write orders", () => p1.send({ topic: "orders", messages: [{ key: "acl", value: Buffer.from("probe") }] }));
   await p1.disconnect();

   // 2) analytics GHI orders → phải bị từ chối (chỉ có Read)
   const ana = client("analytics", "analytics-secret");
   const p2 = ana.producer(); await p2.connect();
   await attempt("analytics write orders (expect TOPIC_AUTHORIZATION_FAILED)", () => p2.send({ topic: "orders", messages: [{ value: "x" }] }));
   await p2.disconnect();

   // 3) order-svc ĐỌC với group → phải bị từ chối (không có Read topic / Read group)
   const c3 = svc.consumer({ groupId: "fulfillment" });
   await attempt("order-svc consume as group fulfillment (expect GROUP/TOPIC_AUTHORIZATION_FAILED)", async () => {
     await c3.connect(); await c3.subscribe({ topic: "orders" });
     await new Promise((res, rej) => { c3.on(c3.events.CRASH, (e) => rej(e.payload.error)); c3.run({ eachMessage: async () => {} }); setTimeout(res, 4000); });
   });
   await c3.disconnect().catch(() => {});

   // 4) sai password → SaslAuthenticationException
   const bad = client("analytics", "wrong");
   const p4 = bad.producer();
   await attempt("analytics wrong password (expect SASL_AUTHENTICATION_FAILED)", () => p4.connect());
   await p4.disconnect().catch(() => {});
   ```

   ```bash
   cd ~/kafka-labs/capstone && node acl-check.mjs
   ```
7. Xoá record thăm dò `acl` để `orders` sạch trước Bước 2 (record này không phải Avro → consumer Bước 3 sẽ coi là poison pill nếu để lại).

   ```bash
   kt --delete --topic orders && sleep 3 && kt --create --topic orders --partitions 12 --replication-factor 3 --config min.insync.replicas=2
   ```

### ✅ Kiểm chứng

- `docker compose ps` → 8 container `running`; `kq describe --status` có `LeaderId: 1`; Grafana mở được `http://localhost:3000`, Prometheus `http://localhost:9090/targets` 3 target broker **UP** (stack Tuần 8).
- `kt --describe --topic orders | head -1` → `PartitionCount: 12  ReplicationFactor: 3  Configs: min.insync.replicas=2`; `customers` có `cleanup.policy=compact`.
- `kcfg --describe --entity-type users` liệt kê `order-svc` và `analytics` với `SCRAM-SHA-512=iterations=8192`.
- `acl-check.mjs` in đúng 4 dòng: ✅ order-svc write · ❌ analytics write `TOPIC_AUTHORIZATION_FAILED` · ❌ order-svc consume `GROUP_AUTHORIZATION_FAILED` (hoặc `TOPIC_AUTHORIZATION_FAILED`) · ❌ wrong password `SASL_AUTHENTICATION_FAILED`.
- `kacl --list` cho thấy **không có** ACL nào cho `User:ANONYMOUS` — nó chạy được nhờ `super.users`, không phải ACL.

### 🧠 Ý nghĩa với đề thi

- **RF 3 + `min.insync.replicas=2` + `acks=all`** = bộ ba durability chuẩn; `min.insync.replicas` là topic/broker config, sửa được **không cần đổi producer code**.
- KStream-KTable join đòi **co-partitioning**: cùng số partition + cùng partitioner + cùng key → `customers` 12 partition dù chỉ có 20 khách.
- SCRAM credential nằm trong **metadata log KRaft**, tạo bằng `kafka-configs.sh --entity-type users` **runtime**; PLAIN thì tĩnh trong JAAS phải restart.
- Consumer cần **`Read` topic + `Read` group**; producer cần **`Write` topic**; app consume-rồi-produce-DLQ cần **cả hai**. Không ACL khớp → deny (`allow.everyone.if.no.acl.found=false`); `super.users` bỏ qua ACL.
- `kafka-acls.sh --authorizer-properties zookeeper.connect=...` là đáp án **sai** ở 4.x (flag đã gỡ, ZooKeeper đã gỡ).

---

## Bước 2 — Producer Node.js Avro idempotent (`order-svc`) ⭐

**🎯 Mục tiêu:** Seed 20 khách hàng vào `customers` (compacted); đăng ký schema Avro `orders-value` v1 trên Schema Registry; gửi **1.000 order** idempotent với key = `customerId`, timestamp trải đều 10 phút (để Bước 4 có nhiều window); bơm **50 record hỏng** (5 %) vào `orders-raw-bad`; ghi file `expected-r1.json` (tổng tiền theo country/window) để đối chiếu ở Bước 4 và `sent-r1.json` (số record ack thành công) để đối chiếu ở Bước 6.
**🧩 Luyện kỹ năng (liên quan đề):**

- `enable.idempotence=true` (kafkajs `idempotent: true`, bắt buộc `maxInFlightRequests: 1`; Java cho phép ≤ 5) ⇒ `acks=all`, PID + sequence.
- Wire format 5 byte + `TopicNameStrategy` (`orders-value`); **thêm field không default = không BACKWARD** (409 nếu subject cũ còn).
- Cùng key → cùng partition → ordering per customer; record timestamp `CreateTime` do producer đặt → window ở Streams.

**⏱️ ~35 phút** · **Yêu cầu trước:** Bước 1.

### Các bước

1. Danh sách khách hàng dùng chung `~/kafka-labs/capstone/customers.mjs` (deterministic → producer tính được "đáp án" tổng tiền theo country).

   ```javascript
   // ~/kafka-labs/capstone/customers.mjs — 20 khách hàng, 5 quốc gia × 4
   const COUNTRIES = ["VN", "SG", "US", "DE", "JP"];
   export const CUSTOMERS = Array.from({ length: 20 }, (_, i) => ({
     customerId: `c-${String(i + 1).padStart(2, "0")}`,
     name: `Customer ${i + 1}`,
     country: COUNTRIES[i % COUNTRIES.length],
   }));
   export const countryOf = Object.fromEntries(CUSTOMERS.map((c) => [c.customerId, c.country]));
   ```
2. Seed `customers` — `~/kafka-labs/capstone/seed-customers.mjs` (dùng listener PLAINTEXT như "job nội bộ"; gửi thêm 1 bản cập nhật cho `c-01` để thấy compaction giữ **bản mới nhất theo key**).

   ```javascript
   // ~/kafka-labs/capstone/seed-customers.mjs — Bước 2: nạp bảng tham chiếu vào topic compacted
   import { Kafka, logLevel } from "kafkajs";
   import { CUSTOMERS } from "./customers.mjs";

   const kafka = new Kafka({ clientId: "seed-customers", brokers: ["localhost:9092", "localhost:9094", "localhost:9096"], logLevel: logLevel.WARN });
   const producer = kafka.producer({ idempotent: true, maxInFlightRequests: 1 });
   await producer.connect();
   const messages = CUSTOMERS.map((c) => ({ key: c.customerId, value: JSON.stringify(c) }));
   messages.push({ key: "c-01", value: JSON.stringify({ ...CUSTOMERS[0], name: "Customer 1 (VIP)" }) });   // update cùng key → compaction giữ bản này
   await producer.send({ topic: "customers", messages });
   console.log(`seeded ${messages.length} records (20 customers + 1 update) into customers`);
   await producer.disconnect();
   ```
3. Schema Avro `~/kafka-labs/capstone/schemas/order-event-v1.avsc`.

   ```json
   {
     "type": "record",
     "name": "OrderEvent",
     "namespace": "com.acme.shop",
     "fields": [
       { "name": "eventId",    "type": "string", "doc": "UUID — khoá dedup ở consumer" },
       { "name": "orderId",    "type": "string" },
       { "name": "customerId", "type": "string", "doc": "= Kafka key → ordering per customer" },
       { "name": "amount",     "type": "double" },
       { "name": "currency",   "type": "string", "default": "USD" },
       { "name": "createdAt",  "type": "long",   "doc": "epoch millis, = record timestamp" }
     ]
   }
   ```
4. Producer `~/kafka-labs/capstone/order-producer.mjs` (in đầy đủ).

   ```javascript
   // ~/kafka-labs/capstone/order-producer.mjs — Bước 2 (và Bước 6 với ROUND=2 PACE_MS=30)
   // ENV: ROUND (1) · COUNT (1000) · BAD_RATIO (0.05) · PACE_MS (0: gửi nhanh; >0: nghỉ giữa các lô để kịp kill broker)
   import { readFileSync, writeFileSync, existsSync } from "node:fs";
   import { randomUUID } from "node:crypto";
   import { Kafka, logLevel } from "kafkajs";
   import { SchemaRegistry, SchemaType } from "@kafkajs/confluent-schema-registry";
   import { CUSTOMERS, countryOf } from "./customers.mjs";

   const ROUND = Number(process.env.ROUND ?? 1);
   const COUNT = Number(process.env.COUNT ?? 1000);
   const BAD_RATIO = Number(process.env.BAD_RATIO ?? 0.05);
   const PACE_MS = Number(process.env.PACE_MS ?? 0);
   const BATCH = 100;                                   // 100 record / send() — kafkajs gom theo partition (Java: linger.ms/batch.size)
   const TOPIC = "orders", BAD_TOPIC = "orders-raw-bad";
   const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

   // 1) Schema Registry: đăng ký (idempotent — schema giống hệt trả cùng id) dưới subject <topic>-value (TopicNameStrategy)
   const registry = new SchemaRegistry({ host: "http://localhost:8081" });
   const { id: schemaId } = await registry.register(
     { type: SchemaType.AVRO, schema: readFileSync(new URL("./schemas/order-event-v1.avsc", import.meta.url), "utf8") },
     { subject: `${TOPIC}-value` },
   );
   console.log(`schema ${TOPIC}-value id=${schemaId}`);

   // 2) Producer qua listener SASL với user order-svc (ACL: Write orders, orders-raw-bad)
   const kafka = new Kafka({
     clientId: "order-svc",
     brokers: ["localhost:29092", "localhost:29094", "localhost:29096"],
     sasl: { mechanism: "scram-sha-512", username: "order-svc", password: "order-secret" },
     logLevel: logLevel.WARN,
     retry: { initialRetryTime: 300, retries: 10, maxRetryTime: 10000 },   // Java: retries=MAX, delivery.timeout.ms=120000
   });
   const producer = kafka.producer({
     idempotent: true,             // Java: enable.idempotence=true (mặc định từ 3.0) → acks=all bắt buộc
     maxInFlightRequests: 1,       // kafkajs bắt buộc 1 khi idempotent; Java cho phép max.in.flight ≤ 5 vẫn giữ thứ tự
   });
   await producer.connect();

   // 3) Timestamp: trải đều COUNT record trên 10 phút, luôn TĂNG qua các round (tránh late record bị grace 10 s của Streams loại)
   const lastTsFile = new URL("./.last-ts", import.meta.url);
   const lastTs = existsSync(lastTsFile) ? Number(readFileSync(lastTsFile, "utf8")) : 0;
   const startTs = Math.max(Date.now(), lastTs + 1000);
   const stepMs = Math.floor(600_000 / COUNT);          // 1.000 record → 600 ms/record → 10 window 1 phút

   const expected = {};                                 // "VN@<windowStartMs>" → tổng tiền (đáp án cho Bước 4)
   let ok = 0, failed = 0, bad = 0;
   let lastTsUsed = startTs;

   for (let i = 0; i < COUNT; i += BATCH) {
     const good = [], garbage = [];
     for (let j = i; j < Math.min(i + BATCH, COUNT); j++) {
       const c = CUSTOMERS[j % CUSTOMERS.length];
       const ts = startTs + j * stepMs;
       lastTsUsed = ts;
       const order = {
         eventId: randomUUID(),
         orderId: `o-r${ROUND}-${String(j + 1).padStart(4, "0")}`,
         customerId: c.customerId,
         amount: Math.round(((j % 97) + 1) * 1.5 * 100) / 100,   // deterministic, 1.5 → 145.5
         currency: "USD",
         createdAt: ts,
       };
       good.push({ key: order.customerId, value: await registry.encode(schemaId, order), timestamp: String(ts) });
       const win = Math.floor(ts / 60_000) * 60_000;             // tumbling window 1 phút, căn theo epoch như Streams
       const k = `${countryOf[c.customerId]}@${win}`;
       expected[k] = Math.round(((expected[k] ?? 0) + order.amount) * 100) / 100;
       if (BAD_RATIO > 0 && j % Math.round(1 / BAD_RATIO) === 0) {          // 5 % → mỗi 20 record 1 rác
         garbage.push({ key: c.customerId, value: Buffer.from(JSON.stringify({ broken: true, seq: j, round: ROUND })), timestamp: String(ts) });
       }
     }
     try {
       await producer.send({ topic: TOPIC, acks: -1, messages: good });    // acks=all (idempotent); resolve = mọi partition đã ack
       ok += good.length;
     } catch (e) {                                                            // chỉ tới đây khi kafkajs đã hết retry nội bộ
       failed += good.length;
       console.log(`FAIL batch ${i}-${i + good.length - 1}: ${e.name} ${e.message}`);
     }
     if (garbage.length) {
       try { await producer.send({ topic: BAD_TOPIC, acks: -1, messages: garbage }); bad += garbage.length; }
       catch (e) { console.log(`FAIL bad batch: ${e.message}`); }
     }
     if ((i + BATCH) % 200 === 0 || i + BATCH >= COUNT) console.log(`round ${ROUND}: ok=${ok} failed=${failed} bad=${bad}`);
     if (PACE_MS) await sleep(PACE_MS);
   }
   await producer.disconnect();

   writeFileSync(lastTsFile, String(lastTsUsed));
   writeFileSync(new URL(`./expected-r${ROUND}.json`, import.meta.url), JSON.stringify(expected, null, 2));
   writeFileSync(new URL(`./sent-r${ROUND}.json`, import.meta.url), JSON.stringify({ round: ROUND, ok, failed, bad, windows: Object.keys(expected).length }, null, 2));
   console.log(`DONE round ${ROUND}: ok=${ok} failed=${failed} bad=${bad} windows=${Object.keys(expected).length} → expected-r${ROUND}.json, sent-r${ROUND}.json`);
   ```
5. Chạy seed rồi producer.

   ```bash
   cd ~/kafka-labs/capstone
   node seed-customers.mjs
   node order-producer.mjs
   ```
6. Soi kết quả trên cluster và Schema Registry.

   ```bash
   ktotal orders                      # 1000
   ktotal orders-raw-bad              # 50
   ktotal customers                   # 21 (compaction xoá bản cũ của c-01 sau khi segment đóng — không cần chờ)
   curl -s localhost:8081/subjects    # ["orders-value"]
   curl -s localhost:8081/subjects/orders-value/versions/latest | jq '{id, version, subject}'
   kcc --topic orders --partition 0 --from-beginning --max-messages 1 --property print.key=true | xxd | head -2   # byte đầu 00 + 4 byte schema id
   cat sent-r1.json
   ```

   > 📌 Nếu `register` trả **409** (`Schema being registered is incompatible`) là do subject `orders-value` từ Lab 5.1 còn trên Registry (chỉ xảy ra khi bạn không `down -v` cluster tuần 5): schema mới **thêm field không có default** (`eventId`, `createdAt`) → vi phạm `BACKWARD`. Xoá subject cũ: `curl -X DELETE localhost:8081/subjects/orders-value && curl -X DELETE "localhost:8081/subjects/orders-value?permanent=true"` rồi chạy lại. Bài học: muốn BACKWARD thì field mới **phải có default**.

### ✅ Kiểm chứng

- `ktotal orders` = **1.000**, `ktotal orders-raw-bad` = **50**; `sent-r1.json` có `"ok": 1000, "failed": 0, "bad": 50, "windows"` ≈ 10–11 (10 phút trải trên các mốc phút).
- Registry có đúng 1 subject `orders-value`, `version: 1`; record trong `orders` bắt đầu bằng `00 00 00 00 0x` (magic 0 + schema id).
- Cùng `customerId` luôn ở cùng partition: `kcc --topic orders --from-beginning --property print.key=true --property print.partition=true --timeout-ms 5000 2>/dev/null | awk '{print $1, $2}' | sort -u | awk '{print $2}' | sort | uniq -c` → mỗi key xuất hiện với **đúng 1** partition.

### 🧠 Ý nghĩa với đề thi

- Idempotent producer = chống duplicate do **retry nội bộ** trong 1 partition/1 session; **không** phải exactly-once end-to-end (đó là transactions + `read_committed`).
- Timestamp record (`CreateTime`) do producer đặt → là **event time** cho window ở Streams; `LogAppendTime` là config topic.
- Subject `TopicNameStrategy` = `<topic>-value`; schema ID **toàn cục**, version **theo subject**; thêm field bắt buộc không default → **không BACKWARD**.
- Batching qua mảng `messages` (Java `linger.ms` 5 ms mặc định từ 4.0, `batch.size` 16 KB) là đòn bẩy throughput số 1.

---

## Bước 3 — Consumer group `fulfillment`: manual commit + dedup + retry → DLQ ⭐

**🎯 Mục tiêu:** Consumer Node.js (user `analytics`) đọc `orders` + `orders-raw-bad`, **tắt auto-commit**, xử lý từng record rồi commit **offset kế tiếp** bằng tay; **dedup** theo `eventId` trong SQLite (ghi kết quả nghiệp vụ + `event_id` **cùng transaction**); lỗi tạm thời retry với backoff **tối đa 3 lần** rồi đẩy `orders-dlq` với header lý do; **poison pill** (không decode Avro được) đi thẳng DLQ; DLQ cũng dedup theo `(topic, partition, offset)` để replay không tạo DLQ trùng.
**🧩 Luyện kỹ năng (liên quan đề):**

- `enable.auto.commit=false` + `commitSync` **sau** xử lý = at-least-once; commit = offset **record kế tiếp** (`lastOffset + 1`).
- `session.timeout.ms` 45 s / `heartbeat.interval.ms` 3 s vs `max.poll.interval.ms` 5 phút — retry backoff phải ngắn để không bị kick.
- Idempotent consumer (dedup store) là cách duy nhất biến at-least-once thành "hiệu ứng exactly-once" khi sink không phải Kafka.

**⏱️ ~40 phút** · **Yêu cầu trước:** Bước 2 (đã có 1.000 + 50 record).

### Các bước

1. Consumer `~/kafka-labs/capstone/fulfillment-consumer.mjs` (in đầy đủ). `node:sqlite` có sẵn trong Node 24 (có thể in `ExperimentalWarning` — bỏ qua).

   ```javascript
   // ~/kafka-labs/capstone/fulfillment-consumer.mjs — Bước 3, 6, 7
   // ENV: MAX_ATTEMPTS (3) · ALWAYS_FAIL (vd "o-r1-0500": order này luôn lỗi → vào DLQ sau 3 lần) · DB (./fulfillment.db)
   import { DatabaseSync } from "node:sqlite";
   import { Kafka, logLevel } from "kafkajs";
   import { SchemaRegistry } from "@kafkajs/confluent-schema-registry";

   const GROUP = "fulfillment";
   const TOPICS = ["orders", "orders-raw-bad"];
   const DLQ = "orders-dlq";
   const MAX_ATTEMPTS = Number(process.env.MAX_ATTEMPTS ?? 3);
   const ALWAYS_FAIL = (process.env.ALWAYS_FAIL ?? "").split(",").filter(Boolean);
   const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

   // ---- Dedup store (SQLite, file bền qua restart) ----
   const db = new DatabaseSync(new URL(process.env.DB ?? "./fulfillment.db", import.meta.url).pathname);
   db.exec(`
     CREATE TABLE IF NOT EXISTS processed_events (event_id TEXT PRIMARY KEY, order_id TEXT, source TEXT, processed_at INTEGER);
     CREATE TABLE IF NOT EXISTS orders_fulfilled (order_id TEXT PRIMARY KEY, customer_id TEXT, amount REAL, fulfilled_at INTEGER);
     CREATE TABLE IF NOT EXISTS dlq_sent (source TEXT PRIMARY KEY, reason TEXT, sent_at INTEGER);
   `);
   const qSeen    = db.prepare("SELECT 1 FROM processed_events WHERE event_id = ?");
   const qDlqSeen = db.prepare("SELECT 1 FROM dlq_sent WHERE source = ?");
   const insEvent = db.prepare("INSERT INTO processed_events VALUES (?, ?, ?, ?)");
   const insOrder = db.prepare("INSERT OR REPLACE INTO orders_fulfilled VALUES (?, ?, ?, ?)");
   const insDlq   = db.prepare("INSERT INTO dlq_sent VALUES (?, ?, ?)");

   // ---- Kafka: user analytics (ACL: Read orders/orders-raw-bad, Read group fulfillment, Write orders-dlq) ----
   const registry = new SchemaRegistry({ host: "http://localhost:8081" });
   const kafka = new Kafka({
     clientId: `fulfillment-${process.pid}`,
     brokers: ["localhost:29092", "localhost:29094", "localhost:29096"],
     sasl: { mechanism: "scram-sha-512", username: "analytics", password: "analytics-secret" },
     logLevel: logLevel.WARN,
   });
   const consumer = kafka.consumer({
     groupId: GROUP,
     sessionTimeout: 45000,        // Java: session.timeout.ms=45000 (mặc định 3.0+; kafkajs mặc định 30000)
     heartbeatInterval: 3000,      // Java: heartbeat.interval.ms=3000 (≤ 1/3 session)
     readUncommitted: false,       // Java: isolation.level=read_committed (kafkajs mặc định đã là read_committed)
   });
   const dlqProducer = kafka.producer({ idempotent: true, maxInFlightRequests: 1 });

   const stats = { processed: 0, skipped: 0, retried: 0, dlq: 0, dlqSkipped: 0, commits: 0 };
   const printStats = () => console.log(`[stats] processed=${stats.processed} skipped=${stats.skipped} retried=${stats.retried} dlq=${stats.dlq} dlqSkipped=${stats.dlqSkipped} commits=${stats.commits}`);

   // ---- "Nghiệp vụ" giả lập: lỗi tạm thời (downstream 503) cho order kết thúc bằng 00 ở 2 lần đầu; ALWAYS_FAIL luôn lỗi ----
   async function fulfil(order, attempt) {
     if (ALWAYS_FAIL.includes(order.orderId)) throw new Error(`payment gateway rejected ${order.orderId} (permanent)`);
     if (order.orderId.endsWith("00") && attempt < 3) throw new Error(`downstream 503 (transient) for ${order.orderId}`);
     await sleep(2);   // mô phỏng I/O
   }

   function markProcessed(order, source) {
     db.exec("BEGIN");   // kết quả nghiệp vụ + event_id trong CÙNG transaction → crash giữa chừng vẫn an toàn
     try {
       insOrder.run(order.orderId, order.customerId, order.amount, Date.now());
       insEvent.run(order.eventId, order.orderId, source, Date.now());
       db.exec("COMMIT");
     } catch (e) { db.exec("ROLLBACK"); throw e; }
   }

   async function sendToDlq(m, topic, partition, source, type, err, attempts) {
     if (qDlqSeen.get(source)) { stats.dlqSkipped++; return; }          // replay: không tạo DLQ trùng
     await dlqProducer.send({
       topic: DLQ, acks: -1,
       messages: [{
         key: m.key, value: m.value,                                    // giữ nguyên payload gốc để redrive
         headers: {
           "error-type": type, "error-reason": String(err.message).slice(0, 200), attempts: String(attempts),
           "source-topic": topic, "source-partition": String(partition), "source-offset": String(m.offset),
           "failed-at": new Date().toISOString(),
         },
       }],
     });
     insDlq.run(source, type, Date.now());
     stats.dlq++;
     console.log(`[dlq] ${type} ${source}: ${err.message}`);
   }

   async function handle(topic, partition, m) {
     const source = `${topic}-${partition}-${m.offset}`;
     let order;
     try { order = await registry.decode(m.value); }                   // 5 byte header → schema id → Avro
     catch (e) { return sendToDlq(m, topic, partition, source, "poison", e, 0); }   // poison pill → DLQ NGAY, không retry

     if (qSeen.get(order.eventId)) { stats.skipped++; return; }        // DEDUP theo eventId (replay/duplicate at-least-once)

     for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
       try {
         await fulfil(order, attempt);
         markProcessed(order, source);
         stats.processed++;
         if (attempt > 1) console.log(`[retry-ok] ${order.orderId} succeeded on attempt ${attempt}`);
         return;
       } catch (e) {
         if (attempt === MAX_ATTEMPTS) return sendToDlq(m, topic, partition, source, "exhausted", e, attempt);
         stats.retried++;
         await sleep(200 * 2 ** (attempt - 1));                        // backoff 200/400 ms — ngắn để không vượt max.poll.interval.ms (5 phút)
       }
     }
   }

   await dlqProducer.connect();
   await consumer.connect();
   await consumer.subscribe({ topics: TOPICS, fromBeginning: true });   // = auto.offset.reset=earliest, CHỈ khi group chưa có offset
   consumer.on(consumer.events.GROUP_JOIN, ({ payload }) =>
     console.log(`[group] joined generation=${payload.generationId} assigned=${JSON.stringify(Object.fromEntries(Object.entries(payload.memberAssignment).map(([t, p]) => [t, p.length])))} partitions`));

   await consumer.run({
     autoCommit: false,              // Java: enable.auto.commit=false
     eachBatchAutoResolve: false,
     eachBatch: async ({ batch, resolveOffset, heartbeat, isRunning, isStale }) => {
       let last = null;
       for (const m of batch.messages) {
         if (!isRunning() || isStale()) break;
         await handle(batch.topic, batch.partition, m);
         resolveOffset(m.offset);
         last = m.offset;
         await heartbeat();
       }
       if (last !== null) {
         // Java: consumer.commitSync(Map.of(tp, new OffsetAndMetadata(lastOffset + 1))) — commit = offset KẾ TIẾP cần đọc
         await consumer.commitOffsets([{ topic: batch.topic, partition: batch.partition, offset: (BigInt(last) + 1n).toString() }]);
         stats.commits++;
       }
     },
   });

   const timer = setInterval(printStats, 5000);
   process.on("SIGINT", async () => {
     clearInterval(timer); printStats();
     await consumer.disconnect(); await dlqProducer.disconnect(); db.close();
     process.exit(0);
   });
   ```
2. Chạy consumer ở **terminal 2** (giữ chạy suốt capstone; Ctrl+C khi cần).

   ```bash
   cd ~/kafka-labs/capstone && node fulfillment-consumer.mjs
   ```
   Output mẫu: `[group] joined generation=1 assigned={"orders":12,"orders-raw-bad":12} partitions`, vài dòng `[dlq] poison orders-raw-bad-3-0: ...`, `[retry-ok] o-r1-0100 succeeded on attempt 3`, rồi `[stats] processed=1000 skipped=0 retried=20 dlq=50 dlqSkipped=0 commits=...`.
3. **Terminal 1:** kiểm tra lag, offset đã commit và SQLite.

   ```bash
   kcg --describe --group fulfillment | sort -k3 -n | head -30      # LAG = 0 mọi partition; CURRENT-OFFSET = LOG-END-OFFSET
   ktotal orders-dlq                                                  # 50 (= số poison pill)
   kcc --topic orders-dlq --from-beginning --max-messages 2 --property print.headers=true --property print.key=true 2>/dev/null
   sqlite3 ~/kafka-labs/capstone/fulfillment.db 'select count(*) from processed_events; select count(*) from orders_fulfilled; select count(*) from dlq_sent;'
   # không có sqlite3 CLI → node -e 'const {DatabaseSync}=require("node:sqlite");const d=new DatabaseSync(process.env.HOME+"/kafka-labs/capstone/fulfillment.db");console.log(d.prepare("select count(*) n from processed_events").get())'
   ```
4. Thử **duplicate do at-least-once**: Ctrl+C consumer, xoá offset đã commit của **1 partition** về đầu rồi chạy lại → record đó được đọc lại nhưng bị dedup.

   ```bash
   kcg --group fulfillment --topic orders:0 --reset-offsets --to-earliest --execute      # group phải INACTIVE; không --execute = dry-run
   node fulfillment-consumer.mjs      # terminal 2 — sau vài giây: skipped = số record của partition 0 (~83), processed = 0
   ```
5. (Tuỳ chọn) Xem đường "hết 3 lần retry → DLQ": Ctrl+C, reset partition 0 lần nữa với `ALWAYS_FAIL` là 1 order **chưa** xử lý — không có vì tất cả đã xử lý → thay bằng xoá dòng dedup của 1 order rồi replay:

   ```bash
   sqlite3 ~/kafka-labs/capstone/fulfillment.db "delete from processed_events where order_id='o-r1-0001'"
   kcg --group fulfillment --topic orders --reset-offsets --to-earliest --execute
   ALWAYS_FAIL=o-r1-0001 node fulfillment-consumer.mjs      # thấy [dlq] exhausted orders-<p>-<off>: payment gateway rejected o-r1-0001 (permanent) → dlq=1
   sqlite3 ~/kafka-labs/capstone/fulfillment.db "delete from dlq_sent where source like 'orders-%' and reason='exhausted'"   # dọn để Bước 7 sạch; record trong orders-dlq vẫn còn (51)
   ```
   Kết thúc bước này để consumer **đang chạy** (không `ALWAYS_FAIL`) cho các bước sau.

### ✅ Kiểm chứng

- Sau lần chạy đầu: `[stats] processed=1000 skipped=0 dlq=50`, `retried=20` (10 order `…00` × 2 lần), `kcg --describe` LAG = 0 trên 24 partition, `ktotal orders-dlq` = 50, SQLite `processed_events` = 1.000.
- Header DLQ có `error-type: poison`, `source-topic: orders-raw-bad`, `source-offset`; value là payload gốc (`{"broken":true,...}`).
- Bước 4 (reset 1 partition): **processed = 0**, skipped ≈ 83 — dedup chặn duplicate; `orders-dlq` không tăng.
- Consumer không bao giờ bị `REBALANCE_IN_PROGRESS`/kick vì backoff tổng < 1 s/record ≪ 5 phút.

### 🧠 Ý nghĩa với đề thi

- Commit **sau** xử lý = **at-least-once** → phải có **idempotent consumer**; commit **trước** = at-most-once. Offset commit là offset **kế tiếp** (last + 1).
- `CommitFailedException` = xử lý lâu hơn `max.poll.interval.ms` → group đã rebalance; sửa bằng giảm `max.poll.records`/xử lý nhanh, **không** phải tăng `session.timeout.ms`.
- Poison pill (`SerializationException`) không tự trôi: offset không tiến → kẹt vòng lặp; cách chuẩn: **DLQ + header lý do** rồi đi tiếp. Kafka consumer **không có** DLQ/`maxReceiveCount` sẵn — đó là Connect sink hoặc `SQS`.
- `--reset-offsets` cần group **inactive** + `--execute`; `auto.offset.reset`/`fromBeginning` chỉ tác dụng khi **chưa có** committed offset.

---

## Bước 4 — Kafka Streams (Java): join `orders` ⋈ `customers` → tumbling 1 phút → `order-stats`, EOS v2 ⭐

**🎯 Mục tiêu:** Viết `OrderStatsApp` trong project Tuần 6: `KStream<String, GenericRecord>` (Avro qua Schema Registry) join `KTable<String, String>` (`customers`, JSON) lấy `country` → `selectKey(country)` (repartition) → `groupByKey` → `TimeWindows.ofSizeAndGrace(1 phút, 10 s)` → `reduce(sum)` → `order-stats` (JSON string). `processing.guarantee=exactly_once_v2`, `num.standby.replicas=1`. Chạy **2 instance** và kiểm chứng tổng tiền theo country/window **khớp với `expected-r1.json`** của producer.
**🧩 Luyện kỹ năng (liên quan đề):**

- KStream-KTable join: **không window**, cần **co-partition**; đổi key trước aggregation → **repartition topic** `<app.id>-...-repartition`; state store + **changelog** compacted.
- Tumbling = size = advance, không chồng; **grace** bắt buộc khai báo (`ofSizeAndGrace`/`ofSizeWithNoGrace`); record trễ quá grace bị **drop**.
- `exactly_once_v2` ⇒ `commit.interval.ms` 30 000 → **100**, consumer nội bộ `read_committed`, 1 transactional producer / thread; downstream phải `read_committed`.
- Số task = số partition lớn nhất trong sub-topology (12) → 2 instance chia 6/6; `num.standby.replicas=1` để failover nhanh (Bước 6).

**⏱️ ~50 phút** · **Yêu cầu trước:** Bước 2 (data), project `~/kafka-labs/streams-lab/` build được (Tuần 6).

### Các bước

1. Thêm dependency vào `~/kafka-labs/streams-lab/build.gradle.kts` (Confluent Avro Serde + Jackson; **giữ** kafka-streams 4.3.1 bằng `force` để artifact `-ccs` của Confluent không kéo version khác).

   ```kotlin
   // THÊM vào build.gradle.kts Tuần 6 (không xoá gì)
   repositories {
       mavenCentral()
       maven("https://packages.confluent.io/maven/")                 // io.confluent:* không có trên Maven Central
   }

   dependencies {
       implementation("io.confluent:kafka-streams-avro-serde:8.0.0") // GenericAvroSerde / SpecificAvroSerde nói chuyện với Schema Registry
       implementation("com.fasterxml.jackson.core:jackson-databind:2.18.3")   // parse JSON của customers
   }

   configurations.all {
       resolutionStrategy.force(                                     // Confluent 8.0 kéo kafka 8.0.0-ccs (= AK 4.0) — ép về 4.3.1 cho đồng nhất
           "org.apache.kafka:kafka-streams:4.3.1",
           "org.apache.kafka:kafka-clients:4.3.1"
       )
   }
   ```
2. Tạo `~/kafka-labs/streams-lab/src/main/java/lab/OrderStatsApp.java` (in đầy đủ; dùng `Common.props/run` của Tuần 6).

   ```java
   // ~/kafka-labs/streams-lab/src/main/java/lab/OrderStatsApp.java — Capstone Bước 4
   package lab;

   import com.fasterxml.jackson.databind.JsonNode;
   import com.fasterxml.jackson.databind.ObjectMapper;
   import io.confluent.kafka.serializers.AbstractKafkaSchemaSerDeConfig;
   import io.confluent.kafka.streams.serdes.avro.GenericAvroSerde;
   import org.apache.avro.generic.GenericRecord;
   import org.apache.kafka.common.serialization.Serde;
   import org.apache.kafka.common.serialization.Serdes;
   import org.apache.kafka.streams.KafkaStreams;
   import org.apache.kafka.streams.KeyValue;
   import org.apache.kafka.streams.StreamsBuilder;
   import org.apache.kafka.streams.StreamsConfig;
   import org.apache.kafka.streams.Topology;
   import org.apache.kafka.streams.kstream.Consumed;
   import org.apache.kafka.streams.kstream.Grouped;
   import org.apache.kafka.streams.kstream.KStream;
   import org.apache.kafka.streams.kstream.KTable;
   import org.apache.kafka.streams.kstream.Materialized;
   import org.apache.kafka.streams.kstream.Produced;
   import org.apache.kafka.streams.kstream.TimeWindows;

   import java.time.Duration;
   import java.util.Locale;
   import java.util.Map;
   import java.util.Properties;

   public class OrderStatsApp {
       /** Kết quả join, chỉ sống trong bộ nhớ giữa join và groupByKey → không cần Serde. */
       record Enriched(String country, double amount) {}

       public static void main(String[] args) {
           Properties props = Common.props("order-stats-app");                       // application.id = group.id = prefix internal topics
           props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2); // mặc định at_least_once; EOS v2 cần broker ≥ 2.5
           props.remove(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG);                   // để Streams tự hạ 30000 → 100 ms khi EOS
           props.put(StreamsConfig.NUM_STANDBY_REPLICAS_CONFIG, 1);                  // mặc định 0; =1 → instance còn lại đã có state khi bạn kill instance kia (Bước 6)
           String schemaRegistry = System.getenv().getOrDefault("SCHEMA_REGISTRY", "http://localhost:8081");

           // Serde Avro generic: đọc 5 byte header → hỏi Schema Registry theo schema id → GenericRecord
           Serde<GenericRecord> orderSerde = new GenericAvroSerde();
           orderSerde.configure(Map.of(AbstractKafkaSchemaSerDeConfig.SCHEMA_REGISTRY_URL_CONFIG, schemaRegistry), false);
           ObjectMapper json = new ObjectMapper();

           StreamsBuilder builder = new StreamsBuilder();

           // KTable từ topic compacted: upsert theo key customerId (bản mới nhất thắng — c-01 "VIP")
           KTable<String, String> customers = builder.table("customers", Consumed.with(Serdes.String(), Serdes.String()));
           KStream<String, GenericRecord> orders = builder.stream("orders", Consumed.with(Serdes.String(), orderSerde));

           orders
               // KStream ⋈ KTable: KHÔNG window, cần co-partition (orders & customers cùng 12 partition, cùng key customerId)
               .join(customers, (order, customerJson) -> new Enriched(country(json, customerJson), (Double) order.get("amount")))
               .selectKey((customerId, e) -> e.country())                                 // đổi key → Streams chèn repartition topic trước aggregation
               .mapValues(Enriched::amount)
               .groupByKey(Grouped.with(Serdes.String(), Serdes.Double()))              // serde cho repartition topic
               .windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofMinutes(1), Duration.ofSeconds(10)))   // tumbling 1' + grace 10 s (bắt buộc khai báo grace)
               .reduce(Double::sum, Materialized.with(Serdes.String(), Serdes.Double()))  // state store + changelog <app.id>-KSTREAM-REDUCE-...-changelog
               .toStream()
               .map((windowedKey, total) -> KeyValue.pair(
                       windowedKey.key() + "@" + windowedKey.window().start(),          // key "VN@1758016800000" — khớp expected-rN.json của producer
                       String.format(Locale.ROOT,
                               "{\"country\":\"%s\",\"windowStart\":%d,\"windowEnd\":%d,\"total\":%.2f}",
                               windowedKey.key(), windowedKey.window().start(), windowedKey.window().end(), total)))
               .peek((k, v) -> System.out.println("stats " + k + " -> " + v))
               .to("order-stats", Produced.with(Serdes.String(), Serdes.String()));

           Topology topology = builder.build();
           System.out.println(topology.describe());                                    // 2 sub-topology: [join] → repartition → [window reduce]
           Common.run(new KafkaStreams(topology, props));
       }

       private static String country(ObjectMapper json, String customerJson) {
           try {
               JsonNode n = json.readTree(customerJson);
               return n.get("country").asText();
           } catch (Exception e) {
               return "UNKNOWN";
           }
       }
   }
   ```
3. Build và chạy **instance A** (terminal 3) rồi **instance B** (terminal 4, `state.dir` khác để không tranh RocksDB lock).

   ```bash
   cd ~/kafka-labs/streams-lab && ./gradlew build -x test
   # Terminal 3 — instance A
   ./gradlew run -PmainClass=lab.OrderStatsApp
   # Terminal 4 — instance B
   STATE_DIR=/tmp/kafka-streams-lab-2 ./gradlew run -PmainClass=lab.OrderStatsApp
   ```
   Log cần thấy: `processing.guarantee = exactly_once_v2`, `commit.interval.ms = 100`, `isolation.level = read_committed` (consumer nội bộ), `transactional.id = order-stats-app-...`, `[state] REBALANCING -> RUNNING`, nhiều dòng `stats VN@... -> {...}` (mỗi update trung gian là 1 record vì không `suppress`).
4. **Terminal 1:** soi internal topic, group và output.

   ```bash
   kt --list | grep order-stats-app
   # order-stats-app-KSTREAM-KEY-SELECT-0000000005-repartition  (12 partition — do selectKey)
   # order-stats-app-KSTREAM-REDUCE-STATE-STORE-0000000007-changelog (12 partition, compact)
   # order-stats-app-customers-STATE-STORE-0000000000-changelog ... (KTable materialized; tên số có thể khác)
   kcg --describe --group order-stats-app --members --verbose      # 2 member, mỗi member ~18 partition (orders 12 + customers 12 + repartition 12 = 36 chia 2)
   kcc --topic order-stats --from-beginning --isolation-level read_committed --property print.key=true --timeout-ms 8000 2>/dev/null | tail -5
   ```
5. Đối chiếu **đáp án**: `~/kafka-labs/capstone/verify-stats.mjs` đọc `order-stats` (`read_committed`), giữ **giá trị mới nhất theo key** (update cuối của mỗi window), so với tổng `expected-r*.json`.

   ```javascript
   // ~/kafka-labs/capstone/verify-stats.mjs — Bước 4 & 6: tổng tiền theo country/window ở order-stats phải khớp producer
   import { readdirSync, readFileSync } from "node:fs";
   import { Kafka, logLevel } from "kafkajs";

   const dir = new URL("./", import.meta.url);
   const expected = {};
   for (const f of readdirSync(dir).filter((f) => /^expected-r\d+\.json$/.test(f))) {      // cộng dồn mọi round
     for (const [k, v] of Object.entries(JSON.parse(readFileSync(new URL(f, dir), "utf8")))) expected[k] = Math.round(((expected[k] ?? 0) + v) * 100) / 100;
   }

   const kafka = new Kafka({ clientId: "verify-stats", brokers: ["localhost:9092", "localhost:9094", "localhost:9096"], logLevel: logLevel.NOTHING });
   const consumer = kafka.consumer({ groupId: `verify-stats-${Date.now()}`, readUncommitted: false });   // read_committed: bỏ record của transaction abort
   await consumer.connect();
   await consumer.subscribe({ topic: "order-stats", fromBeginning: true });

   const latest = {};
   let records = 0;
   const done = new Promise((res) => {
     let t = setTimeout(res, 8000);
     consumer.run({ eachMessage: async ({ message }) => { records++; latest[message.key.toString()] = JSON.parse(message.value.toString()).total; clearTimeout(t); t = setTimeout(res, 4000); } });
   });
   await done;
   await consumer.disconnect();

   let ok = 0, bad = 0;
   for (const [k, exp] of Object.entries(expected)) {
     const got = latest[k];
     if (got !== undefined && Math.abs(got - exp) < 0.01) ok++;
     else { bad++; console.log(`MISMATCH ${k}: expected=${exp} got=${got}`); }
   }
   const extra = Object.keys(latest).filter((k) => !(k in expected));
   console.log(`records read=${records} windows expected=${Object.keys(expected).length} match=${ok} mismatch=${bad} unexpected=${extra.length}`);
   process.exit(bad || extra.length ? 1 : 0);
   ```

   ```bash
   cd ~/kafka-labs/capstone && node verify-stats.mjs
   # records read=~1000+ windows expected=11 match=11 mismatch=0 unexpected=0
   ```
   > 📌 Số update trung gian ≈ số order (mỗi order làm tổng của 1 window đổi, cache 10 MB flush mỗi commit 100 ms). Muốn **1 record/window** thì thêm `.suppress(Suppressed.untilWindowCloses(unbounded()))` trước `toStream()` — nhưng window cuối chỉ phát khi stream time vượt `end + grace`, tức cần record mới hơn (Bước 6 round 2 sẽ đẩy nó ra).

### ✅ Kiểm chứng

- `topology.describe()` in **2 sub-topology** (Sub-topology 0: source orders/customers + join + KEY-SELECT sink → repartition; Sub-topology 1: source repartition + windowed reduce + sink `order-stats`).
- `kt --list | grep order-stats-app` có **1 repartition + ≥ 1 changelog**, đều 12 partition, changelog `cleanup.policy=compact`.
- `kcg --describe --group order-stats-app --members --verbose` → **2 member**, tổng partition = 36, không partition nào bị gán 2 lần.
- `verify-stats.mjs` → `mismatch=0 unexpected=0`, số window ≈ 10–11 = `windows` trong `sent-r1.json`.
- Log có `commit.interval.ms = 100` và `isolation.level = read_committed` mà bạn **không** set tay → do `exactly_once_v2`.

### 🧠 Ý nghĩa với đề thi

- "Enrich stream với bảng tham chiếu **cùng key**" → KStream-KTable join (co-partition, không window); **khác key / bảng nhỏ** → `GlobalKTable`; 2 KStream → **windowed** join.
- Đổi key trước aggregation ⇒ **repartition topic**; mọi aggregation có state ⇒ **changelog** compacted; số task = max partition trong sub-topology.
- Tumbling vs hopping vs sliding vs session: "count per 1 minute, non-overlapping" = **tumbling**; grace quyết định record trễ có được tính không.
- `exactly_once_v2` là **config Streams** (`processing.guarantee`), tự ép `commit.interval.ms=100` → throughput giảm — đề hỏi "why slower after EOS" → đây. Downstream phải đọc **`read_committed`**.
- `num.standby.replicas=1` = failover nhanh (restore state từ bản sao thay vì replay changelog).

---

## Bước 5 — Connect `FileStreamSink` từ `order-stats` với SMT + `errors.tolerance=all` + DLQ

**🎯 Mục tiêu:** Đăng ký sink connector qua REST (Tuần 5) đọc `order-stats` với `consumer.override.isolation.level=read_committed`, thêm metadata bằng SMT `InsertField` (static field + partition/offset), ghi file `connect-data/order-stats.out`; bật `errors.tolerance=all` + DLQ `order-stats-dlq` + header lý do; bơm 1 record không phải JSON để thấy record đi DLQ **mà connector vẫn RUNNING**.
**🧩 Luyện kỹ năng (liên quan đề):**

- Converter (worker default, connector override) vs SMT (`transforms`); `JsonConverter` + `schemas.enable=false` → value = `Map` → `InsertField$Value` chạy được.
- **DLQ chỉ có ở sink**: `errors.tolerance=all`, `errors.deadletterqueue.topic.name`, `errors.deadletterqueue.context.headers.enable=true` → header `__connect.errors.*`.
- Client override `consumer.override.*` (`connector.client.config.override.policy=All` mặc định từ 3.0).

**⏱️ ~25 phút** · **Yêu cầu trước:** Bước 4 (có data trong `order-stats`); Connect worker Tuần 5 đang chạy (REST 8083).

### Các bước

1. Đăng ký connector.

   ```bash
   curl -s -X PUT -H "Content-Type: application/json" localhost:8083/connectors/order-stats-file-sink/config -d '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "2",
     "topics": "order-stats",
     "file": "/data/order-stats.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.json.JsonConverter",
     "value.converter.schemas.enable": "false",
     "consumer.override.isolation.level": "read_committed",
     "transforms": "addMeta",
     "transforms.addMeta.type": "org.apache.kafka.connect.transforms.InsertField$Value",
     "transforms.addMeta.static.field": "pipeline",
     "transforms.addMeta.static.value": "capstone",
     "transforms.addMeta.partition.field": "kafka_partition",
     "transforms.addMeta.offset.field": "kafka_offset",
     "errors.tolerance": "all",
     "errors.log.enable": "true",
     "errors.log.include.messages": "true",
     "errors.deadletterqueue.topic.name": "order-stats-dlq",
     "errors.deadletterqueue.topic.replication.factor": "3",
     "errors.deadletterqueue.context.headers.enable": "true"
   }' | jq '{name, tasks: .tasks | length}'
   sleep 5
   curl -s localhost:8083/connectors/order-stats-file-sink/status | jq '{connector: .connector.state, tasks: [.tasks[] | {id, state}]}'
   ```
2. Xem file output (mỗi dòng là `value.toString()` của `Map` sau SMT — dạng `{country=VN, windowStart=..., total=..., pipeline=capstone, kafka_partition=3, kafka_offset=17}`).

   ```bash
   wc -l ~/kafka-labs/connect-data/order-stats.out
   tail -3 ~/kafka-labs/connect-data/order-stats.out
   ```
3. Bơm 1 record **không phải JSON** vào `order-stats` (giả lập producer lạ ghi sai format) → converter lỗi → DLQ, connector không FAILED.

   ```bash
   echo 'this-is-not-json' | kcpi --topic order-stats
   sleep 5
   curl -s localhost:8083/connectors/order-stats-file-sink/status | jq -r '.tasks[].state'      # RUNNING, RUNNING
   kcc --topic order-stats-dlq --from-beginning --property print.headers=true --timeout-ms 5000 2>/dev/null
   docker compose logs connect 2>/dev/null | grep -E "Error encountered in task|DataException" | tail -2
   ```
4. Đối chứng với `errors.tolerance=none` (mặc định) — đổi config, bơm record hỏng lần nữa → task **FAILED**; rồi đổi lại `all` và `restart`.

   ```bash
   curl -s localhost:8083/connectors/order-stats-file-sink/config | jq '.["errors.tolerance"]="none"' | \
     curl -s -X PUT -H "Content-Type: application/json" localhost:8083/connectors/order-stats-file-sink/config -d @- >/dev/null
   sleep 3; echo 'still-not-json' | kcpi --topic order-stats; sleep 5
   curl -s localhost:8083/connectors/order-stats-file-sink/status | jq -r '.tasks[] | "\(.id) \(.state) \(.trace // "" | split("\n")[0])"'   # 1 task FAILED: DataException: Converting byte[] to Kafka Connect data failed
   curl -s localhost:8083/connectors/order-stats-file-sink/config | jq '.["errors.tolerance"]="all"' | \
     curl -s -X PUT -H "Content-Type: application/json" localhost:8083/connectors/order-stats-file-sink/config -d @- >/dev/null
   curl -s -X POST "localhost:8083/connectors/order-stats-file-sink/restart?includeTasks=true&onlyFailed=true"
   sleep 5; curl -s localhost:8083/connectors/order-stats-file-sink/status | jq -r '.tasks[].state'     # RUNNING, RUNNING
   ```

### ✅ Kiểm chứng

- Status `connector: RUNNING`, 2 task `RUNNING`; `order-stats.out` có số dòng ≈ số record trong `order-stats` (`ktotal order-stats`), mỗi dòng có `pipeline=capstone`, `kafka_partition`, `kafka_offset`.
- `order-stats-dlq` có record `this-is-not-json` với header `__connect.errors.topic=order-stats`, `__connect.errors.exception.class.name=org.apache.kafka.connect.errors.DataException`, `__connect.errors.stage=VALUE_CONVERTER`.
- Với `errors.tolerance=none` → task **FAILED** ngay record hỏng đầu tiên; `restart?onlyFailed=true` đưa về RUNNING sau khi đổi lại `all`.
- `kcg --describe --group connect-order-stats-file-sink` (group ngầm của sink = `connect-<name>`) LAG = 0.

### 🧠 Ý nghĩa với đề thi

- "Route bad records instead of failing connector" → `errors.tolerance=all` + `errors.deadletterqueue.topic.name` — **chỉ sink connector**; source lỗi chỉ log.
- Đổi format dữ liệu (JSON → Avro) là việc của **Converter**; SMT chỉ sửa/thêm/route từng record — `InsertField` cần Struct/Map, nên `StringConverter` sẽ lỗi với SMT này.
- Sink connector = consumer group `connect-<name>`, offset trong `__consumer_offsets`; source offset trong `connect-offsets` (25 partition).
- Sink đọc output của Streams EOS phải `consumer.override.isolation.level=read_committed`, nếu không có thể ghi cả record của transaction **abort**.

---

## Bước 6 — Chaos & quan sát: Grafana, kill broker (không mất data), kill Streams instance (task chuyển) ⭐

**🎯 Mục tiêu:** Mở Grafana/Prometheus (Tuần 8) theo dõi `UnderReplicatedPartitions` và lag `fulfillment`; chạy producer **round 2** (1.000 order, chậm lại) và **`docker stop kafka-2` giữa chừng** → chứng minh **không mất record đã ack** (`sent OK` = tổng end offset tăng thêm), consumer & Streams tiếp tục; `kill -9` **1 Streams instance** → task chuyển sang instance còn lại, `verify-stats.mjs` vẫn khớp; bật lại broker → URP về 0, ISR hồi đủ.
**🧩 Luyện kỹ năng (liên quan đề):**

- `UnderReplicatedPartitions` > 0 khi follower rời ISR; leader election trong ISR; `acks=all` + `min.isr=2` vẫn ghi được khi mất **1** broker.
- Lag = LEO − committed offset; đọc `kcg --describe`.
- Streams failover: task + state (standby) chuyển sang instance sống; transactional producer cũ bị **fence** (`ProducerFencedException`) khi instance khác nhận task.

**⏱️ ~35 phút** · **Yêu cầu trước:** Bước 3 (consumer chạy, terminal 2), Bước 4 (2 Streams instance, terminal 3/4), Bước 5 (connector RUNNING).

### Các bước

1. Mở dashboard và xác nhận trạng thái "xanh" **trước** chaos.

   ```bash
   open http://localhost:3000        # Grafana (đăng nhập theo Tuần 8, mặc định admin/admin) — dashboard/panel PromQL Lab 8.1
   open http://localhost:9090/graph  # Prometheus — dán PromQL bên dưới
   ```
   PromQL cần xem (tên metric theo rules `kafka-jmx.yml` Tuần 8):
   ```promql
   sum(kafka_server_replicamanager_underreplicatedpartitions)              # phải = 0
   sum(kafka_controller_kafkacontroller_offlinepartitionscount)             # phải = 0
   sum(rate(kafka_server_brokertopicmetrics_messagesinpersec_count[1m]))    # tăng khi producer chạy
   ```
   Lag consumer theo CLI (kafkajs không có JMX; Tuần 8 dùng `lag-watch.mjs`):
   ```bash
   watch -n 2 "docker exec kafka-1 /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka-1:19092 --describe --group fulfillment 2>/dev/null | awk 'NR>1{l+=\$6} END{print \"fulfillment total LAG:\", l+0}'"
   ```
2. Ghi lại **tổng end offset hiện tại** làm mốc, tìm broker đang là leader nhiều partition của `orders`.

   ```bash
   BEFORE=$(ktotal orders); echo "orders before round 2: $BEFORE"       # 1000
   kt --describe --topic orders | grep -c "Leader: 3"                     # số partition kafka-2 (node.id 3) đang lead — thường 4
   ```
3. **Terminal 5:** chạy producer round 2, gửi **chậm** (~30–40 s) để kịp kill broker; **không** bơm record hỏng (`BAD_RATIO=0`) để số DLQ giữ 50.

   ```bash
   cd ~/kafka-labs/capstone && ROUND=2 COUNT=1000 BAD_RATIO=0 PACE_MS=40 node order-producer.mjs
   ```
4. **Terminal 1:** khi terminal 5 in `round 2: ok=200…`, **stop kafka-2** rồi quan sát ~20 giây, sau đó **start lại**.

   ```bash
   docker stop kafka-2
   sleep 5
   kt --describe --topic orders | head -4          # Leader đổi cho partition từng có Leader: 3; Isr: 2,4 (mất 3)
   # Prometheus: sum(underreplicatedpartitions) nhảy lên (≈ tổng partition có replica trên kafka-2: orders 12 + customers 12 + ... ≥ 30)
   # Terminal 5: có thể thấy 1–2 dòng WARN kafkajs (NOT_LEADER_OR_FOLLOWER / request timed out) rồi tiếp tục ok=… — KHÔNG có dòng FAIL
   # Terminal 2 (consumer): vẫn in [stats] processed tăng; Terminal 3/4 (Streams): có thể REBALANCING ngắn rồi RUNNING
   sleep 20
   docker start kafka-2
   ```
5. Đợi terminal 5 in `DONE round 2: ok=1000 failed=0`. **Chứng minh không mất data:**

   ```bash
   AFTER=$(ktotal orders); echo "before=$BEFORE after=$AFTER delta=$((AFTER-BEFORE)) sent_ok=$(jq .ok ~/kafka-labs/capstone/sent-r2.json)"
   # delta == sent_ok (== 1000). Nếu failed>0 trong sent-r2.json thì delta ≥ ok (batch fail có thể đã được ghi mà ack mất — idempotence chặn duplicate)
   sleep 20
   kt --describe --topic orders | grep -vc "Isr: [0-9],[0-9],[0-9]"      # 1 (chỉ dòng header) → mọi partition ISR đủ 3 sau khi kafka-2 đuổi kịp
   ```
   Prometheus: `sum(kafka_server_replicamanager_underreplicatedpartitions)` về **0**; Grafana lag `fulfillment` tăng vọt rồi về 0.
6. **Kill 1 Streams instance** (giết đúng JVM của instance B bằng `jps`, không `pkill -f` vì sẽ chết cả 2).

   ```bash
   jps -l | grep OrderStatsApp                                   # 2 dòng <pid> lab.OrderStatsApp
   kill -9 $(jps -l | awk '/lab.OrderStatsApp/{print $1}' | tail -1)
   sleep 15
   kcg --describe --group order-stats-app --members --verbose      # còn 1 member giữ TOÀN BỘ 36 partition
   ```
   Terminal của instance còn sống: `[state] RUNNING -> REBALANCING`, log `Restoring ... from standby` / `Assigned tasks ... to clients` rồi `REBALANCING -> RUNNING` — nhanh vì có **standby replica**. Terminal của instance bị kill: Gradle báo `FAILED` / process killed.
7. Kiểm chứng end-to-end sau chaos: tổng tiền vẫn đúng (cộng dồn round 1 + 2), consumer xử lý đủ, Connect vẫn ghi.

   ```bash
   cd ~/kafka-labs/capstone && node verify-stats.mjs               # mismatch=0 (expected-r1 + expected-r2)
   # Terminal 2: [stats] processed=2000 skipped=… dlq=50
   sqlite3 ~/kafka-labs/capstone/fulfillment.db 'select count(*) from processed_events'      # 2000
   curl -s localhost:8083/connectors/order-stats-file-sink/status | jq -r '.tasks[].state'    # RUNNING RUNNING
   ktotal orders-dlq                                                # 50 (hoặc 51 nếu bạn làm mục 5 tuỳ chọn ở Bước 3)
   ```
8. (Tuỳ chọn, 3 phút) Leader **không** tự quay về preferred ngay (`leader.imbalance.check.interval.seconds=300`): ép bầu lại.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-leader-election.sh --bootstrap-server kafka-1:19092 --election-type PREFERRED --all-topic-partitions
   ```
   Sau đó khởi động lại instance B (terminal 4: `STATE_DIR=/tmp/kafka-streams-lab-2 ./gradlew run -PmainClass=lab.OrderStatsApp`) để có lại 2 instance.

### ✅ Kiểm chứng

- Trong lúc kafka-2 chết: `Isr` mọi partition thiếu node 3, leader mới nằm trong ISR cũ; Prometheus URP > 0; producer **không có dòng FAIL** (chỉ WARN retry); consumer/Streams/Connect vẫn RUNNING.
- `delta == sent_ok == 1000` → **không mất record đã ack** (acks=all + min.isr 2 + RF 3 chịu được 1 broker).
- Sau `docker start kafka-2` ≤ 30 s: ISR đủ 3 ở mọi partition, URP = 0.
- Sau kill Streams instance: group `order-stats-app` còn **1 member / 36 partition**, `verify-stats.mjs` `mismatch=0` (EOS v2: không double-count dù task chuyển giữa transaction).
- `processed = 2000`, `orders-dlq` không đổi (50), Connect RUNNING.

### 🧠 Ý nghĩa với đề thi

- `UnderReplicatedPartitions` > 0 = follower tụt/broker chết → check broker health, `replica.lag.time.max.ms` (30 s), disk/network; `OfflinePartitionsCount` > 0 mới là mất khả năng phục vụ.
- Mất **1** broker với RF3/min.isr2: ghi vẫn OK; mất **2** → `NotEnoughReplicasException` (retriable) chứ không âm thầm mất; đọc không bị ảnh hưởng.
- Client tự refresh metadata sau `NotLeaderOrFollowerException` — không đổi `bootstrap.servers`; leader không tự về preferred ngay (300 s) → `kafka-leader-election.sh`.
- Streams instance chết → task (và state) chuyển sang instance khác; `num.standby.replicas` rút ngắn restore; transactional producer của instance chết bị **fence** bởi epoch mới → không double-write.
- Lag tăng vọt lúc chaos rồi về 0 = bình thường; lag **tăng liên tục** mới là consumer chậm/đứng.

---

## Bước 7 — Replay: reset offset `fulfillment` về đầu → không xử lý trùng ⭐

**🎯 Mục tiêu:** Dừng consumer, `--reset-offsets --to-earliest` cho **toàn bộ topic** của group `fulfillment`, chạy lại → consumer đọc lại **2.000 order + 50 record hỏng** nhưng `processed` mới = **0**, `skipped` = 2.000, `dlqSkipped` = 50 và `orders-dlq` **không tăng** — nhờ dedup ở Bước 3.
**🧩 Luyện kỹ năng (liên quan đề):**

- `kafka-consumer-groups.sh --reset-offsets` cần group **inactive** + `--execute`; các scenario `--to-earliest/--to-latest/--to-offset/--shift-by/--to-datetime/--by-duration`.
- Replay là tính năng cốt lõi của Kafka (log bất biến, retention) → mọi consumer phải **idempotent**.

**⏱️ ~15 phút** · **Yêu cầu trước:** Bước 6.

### Các bước

1. **Terminal 2:** Ctrl+C consumer (đọc dòng `[stats]` cuối: `processed=2000 ... dlq=50`). Kiểm tra group đã inactive.

   ```bash
   kcg --describe --group fulfillment --state       # STATE: Empty, #MEMBERS: 0
   ```
2. Dry-run rồi execute reset về đầu cho mọi topic của group.

   ```bash
   kcg --group fulfillment --all-topics --reset-offsets --to-earliest --dry-run | head -5    # NEW-OFFSET = 0 mọi partition, chưa đổi gì
   kcg --group fulfillment --all-topics --reset-offsets --to-earliest --execute
   kcg --describe --group fulfillment | awk 'NR>1{l+=$6} END{print "LAG tổng sau reset:", l}'   # 2050 (2000 orders + 50 raw-bad)
   ```
3. Chạy lại consumer, chờ LAG về 0 (~10 s), đọc `[stats]`.

   ```bash
   cd ~/kafka-labs/capstone && node fulfillment-consumer.mjs
   # [stats] processed=0 skipped=2000 retried=0 dlq=0 dlqSkipped=50 commits=…
   ```
4. **Terminal 1:** xác nhận không có side effect trùng.

   ```bash
   ktotal orders-dlq                                                   # vẫn 50 (không tạo DLQ trùng nhờ dedup theo source topic-partition-offset)
   sqlite3 ~/kafka-labs/capstone/fulfillment.db 'select count(*) from processed_events; select count(*) from orders_fulfilled;'   # 2000, 2000 — không tăng
   kcg --describe --group fulfillment | awk 'NR>1{l+=$6} END{print "LAG:", l}'   # 0
   ```
5. (Tuỳ chọn) Replay **có chọn lọc**: chỉ 1 partition từ thời điểm cụ thể / lùi 100 offset — để thuộc cú pháp.

   ```bash
   # Ctrl+C consumer trước
   kcg --group fulfillment --topic orders:0 --reset-offsets --shift-by -100 --execute
   kcg --group fulfillment --topic orders --reset-offsets --to-datetime 2026-01-01T00:00:00.000 --dry-run | head -3
   kcg --group fulfillment --topic orders --reset-offsets --by-duration PT1H --dry-run | head -3
   ```

### ✅ Kiểm chứng

- Sau reset: LAG tổng = **2.050** (= `ktotal orders` + `ktotal orders-raw-bad`); `--dry-run` không đổi CURRENT-OFFSET, `--execute` mới đổi.
- Sau chạy lại: `processed=0`, `skipped=2000`, `dlqSkipped=50`, `dlq=0`; `orders-dlq` vẫn 50; SQLite không tăng dòng. *(README ghi "replay 1.000 record, skipped = 1.000" — đó là khi bạn **không** chạy round 2 ở Bước 6; số đúng luôn = tổng record trong `orders`.)*
- Reset khi consumer **đang chạy** → lỗi `Assignments can only be reset if the group 'fulfillment' is inactive` — thử để nhớ.

### 🧠 Ý nghĩa với đề thi

- Cùng data đọc lại bao nhiêu lần cũng được (retention còn) — đó là điểm khác hàng đợi truyền thống; hệ quả: consumer **phải idempotent** (`eventId`/upsert/`(topic,partition,offset)` trong sink).
- `--reset-offsets` = sửa `__consumer_offsets` của group; cần group **inactive**, có `--execute`; `--to-earliest` ≠ `auto.offset.reset=earliest` (cái sau chỉ áp dụng khi **chưa có** committed offset).
- Idempotent **producer** (Bước 2) và idempotent **consumer** (Bước 3) là 2 việc khác nhau; exactly-once "thật" chỉ có Kafka→Kafka bằng transactions/Streams EOS (Bước 4).

---

## 🧹 Dọn dẹp toàn bộ

Chạy **Ngày trước thi** (README: `docker compose down -v` mọi thứ). Thứ tự: dừng tiến trình → xoá connector/Streams state → down mọi compose → xoá thư mục lab.

```bash
# 1) Ctrl+C mọi terminal: consumer (2), 2 Streams instance (3, 4), producer (5)
cd ~/kafka-labs
export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.registry.yml:docker-compose.connect.yml:docker-compose.monitoring.yml:docker-compose.capstone-security.yml

# 2) Connector + Streams internal topics (tuỳ chọn — down -v ở bước 4 xoá hết dữ liệu; làm để thuộc lệnh)
curl -s -X DELETE localhost:8083/connectors/order-stats-file-sink
docker exec kafka-1 /opt/kafka/bin/kafka-streams-application-reset.sh --bootstrap-server kafka-1:19092 \
  --application-id order-stats-app --input-topics orders,customers          # xoá repartition/changelog + reset offset app
for t in orders orders-raw-bad customers order-stats orders-dlq order-stats-dlq; do kt --delete --topic $t; done
kcg --delete --group fulfillment
kacl --remove --force --allow-principal User:order-svc --producer --topic orders
kcfg --alter --delete-config 'SCRAM-SHA-512' --entity-type users --entity-name order-svc
kcfg --alter --delete-config 'SCRAM-SHA-512' --entity-type users --entity-name analytics

# 3) Down TOÀN BỘ stack capstone (xoá cả volume)
docker compose down -v --remove-orphans

# 4) Down mọi compose còn sót của các tuần khác (single node Tuần 1, secure Tuần 7, debezium Tuần 5, ksqldb Tuần 6, MM2 Tuần 8…)
docker compose $(printf -- '-f %s ' docker-compose.*.yml) down -v --remove-orphans 2>/dev/null
docker ps -a --format '{{.Names}}\t{{.Status}}' | grep -Ei 'kafka|controller|schema|connect|prometheus|grafana|postgres|ksql|debezium' && \
  docker rm -f $(docker ps -aq --filter name=kafka --filter name=controller --filter name=schema-registry --filter name=connect --filter name=prometheus --filter name=grafana) 2>/dev/null
docker volume ls -q | grep -Ei 'kafka|grafana|prometheus' | xargs -r docker volume rm

# 5) Thư mục lab: xoá dữ liệu capstone, GIỮ 2 file compose chuẩn + code nếu muốn ôn lại sau thi
rm -rf ~/kafka-labs/capstone /tmp/kafka-streams-lab* ~/kafka-labs/connect-data/order-stats.out
# rm -rf ~/kafka-labs                                # xoá hẳn nếu không cần nữa

# 6) (Tuỳ chọn) Xoá image để trả ~4–5 GB đĩa
docker image rm apache/kafka:4.3.1 confluentinc/cp-schema-registry:8.0.0 confluentinc/cp-kafka-connect:8.0.0 2>/dev/null
docker images --format '{{.Repository}}:{{.Tag}}' | grep -Ei 'prom/prometheus|grafana/grafana|debezium|ksqldb|postgres' | xargs -r docker image rm
docker system prune -f
docker ps -a; docker volume ls     # đều trống
```

> ✅ Kiểm chứng dọn dẹp: `docker ps -a` không còn container Kafka, `docker volume ls` không còn volume kafka/grafana/prometheus, `ls ~/kafka-labs/capstone` báo không tồn tại, `lsof -i :9092 -i :8081 -i :8083 -i :3000 -i :9090` không có tiến trình.

---

## ✅ Checklist "Trước ngày thi"

Đối chiếu với **Tiêu chí SẴN SÀNG đăng ký thi** (README mục PHẢI NHỚ) — chỉ đặt lịch khi tick **đủ**.

**Capstone (tiêu chí 4)**

- [ ] Bước 1: `kt --describe orders` = 12p/RF3/min.isr 2; `acl-check.mjs` in 1 ✅ + 3 ❌ đúng exception.
- [ ] Bước 2: `ktotal orders` = 1.000, `orders-raw-bad` = 50, subject `orders-value` v1, `sent-r1.json` `failed: 0`.
- [ ] Bước 3: `processed=1000 dlq=50`; reset 1 partition → `processed=0`, `skipped>0`.
- [ ] Bước 4: 2 member Streams, `verify-stats.mjs` `mismatch=0`; log có `commit.interval.ms = 100` + `read_committed`.
- [ ] Bước 5: connector RUNNING, file có `pipeline=capstone`; record hỏng vào `order-stats-dlq` với header `__connect.errors.*`; `errors.tolerance=none` → FAILED.
- [ ] Bước 6: `delta == sent_ok` khi kill broker; URP về 0; kill Streams instance → 1 member/36 partition; `verify-stats.mjs` vẫn khớp.
- [ ] Bước 7: reset `--to-earliest` → `processed=0 skipped=2000 dlqSkipped=50`, `orders-dlq` không tăng.
- [ ] 🧹 Dọn dẹp toàn bộ: `docker ps -a` trống, volume trống.

**Kiến thức (tiêu chí 1–3)**

- [ ] ≥ 3 bộ practice **khác nhau** đạt **≥ 80 %** ổn định, canh giờ 90', cách nhau ≥ 1 ngày; không bài nào < 70 % (nếu có → đã lùi lịch 1 tuần).
- [ ] Review **100 %** câu sai + file phân tích 6 mục trong `CCDAK/questions/` cho câu đáng nhớ.
- [ ] Đọc trôi **bảng số §6** + **bảng phản xạ §7** của Kế hoạch tổng; tự viết lại **cram sheet 1 trang** từ trí nhớ và đối chiếu 60 fact.
- [ ] Thuộc **15 bẫy** (README) — đặc biệt defaults đổi theo version: `acks=all`/idempotence (3.0), `session.timeout.ms=45 s` (3.0), `linger.ms=5` (4.0), KRaft-only + Java 17 (4.0), share groups GA (4.2), classic protocol deprecated (4.3).
- [ ] Giải thích được **bằng chính capstone** 6 cụm hay hỏi: no data loss (Bước 1+6) · idempotent vs exactly-once (Bước 2+3+4) · manual commit & offset kế tiếp (Bước 3) · join/window/EOS Streams (Bước 4) · DLQ chỉ sink + converter vs SMT (Bước 5) · URP/lag/reset offset (Bước 6+7).

**Hậu cần thi (Checklist ngày thi trong README)**

- [ ] Đối chiếu [confluent.io/certification](https://www.confluent.io/certification/) (nhà cung cấp proctor, lệ phí, chính sách) — xem [resources/ccdak-official-exam-page.md](resources/ccdak-official-exam-page.md) và [resources/confluent-certification-faq-policies.md](resources/confluent-certification-faq-policies.md).
- [ ] Cài **Honorlock Chrome extension**, chạy **System Check** ≥ 1 ngày trước; Chrome 120+, webcam + micro, mạng ≥ 1 Mbps down / 2,5 Mbps up; tắt VPN/extension khác.
- [ ] **Government ID** còn hạn, tên khớp tài khoản training.confluent.io; phòng trống, một mình, sẵn sàng quay 360°.
- [ ] Ngủ đủ; trước giờ thi chỉ đọc cram sheet + 15 bẫy; nhớ nhịp **90 giây/câu**, đánh dấu câu khó, default theo **version mới nhất**.

> 🎓 Đủ 4 tiêu chí → đặt lịch tại [training.confluent.io](https://training.confluent.io/) (catalog view 108). Chưa đủ → lùi lịch, không "thử vận may".
