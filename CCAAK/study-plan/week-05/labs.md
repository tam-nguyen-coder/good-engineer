# 🧪 Hands-on Labs — Tuần 5: Security administration (listener · TLS rotation · SCRAM · ACL ở quy mô)

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab (trừ khi lab nói "giữ cluster").
> ⚙️ Yêu cầu chung: **cluster 3 broker + 1 controller** từ [CCDAK Tuần 1 — Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md) (`~/kafka-labs/docker-compose.cluster.yml`), `kafkajs` đã cài trong `~/kafka-labs/`, và Java `keytool` + `openssl` trên máy host.
> 🔁 Tuần này **không làm lại** Lab TLS/SASL/ACL cơ bản của [CCDAK Tuần 7](../../../CCDAK/study-plan/week-07/labs.md) — mọi thao tác ở đây chạy trên **cluster nhiều node**, nghĩa là phải **rolling** và phải chứng minh **không downtime**.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung

### 1) Thư mục và biến môi trường

```bash
cd ~/kafka-labs
mkdir -p week-05/{certs,secrets,scripts}
cd week-05

export KAFKA_CTR=kafka-1
export KAFKA_BS=kafka-1:19092
export PW=labpass123
```

> ⚠️ **KHÔNG định nghĩa lại `docker-compose.cluster.yml`.** Mọi thay đổi của tuần này nằm trong các **file override** riêng (`docker-compose.w5-*.yml`) và được nạp bằng `-f docker-compose.cluster.yml -f docker-compose.w5-....yml`. Muốn trả cluster về trạng thái gốc thì chỉ cần bỏ file override.

### 2) Sơ đồ cổng của tuần — đọc trước khi dựng

| Cổng | Đang dùng cho | Ghi chú |
| --- | --- | --- |
| `9093` | **CONTROLLER** (node `controller`, `node.id=1`) | **Tuyệt đối không dùng lại** |
| `19092` | Listener nội bộ trong docker network (Tuần 5 đổi tên thành **`INTERNAL`**) | Inter-broker |
| `9092` / `9094` / `9096` | Listener từ host (Tuần 5 đổi tên thành **`ADMIN`**, vẫn `PLAINTEXT`) | Đường vận hành: mọi lệnh `kafka-configs.sh` / `kafka-acls.sh` đi qua đây |
| **`9192` / `9194` / `9196`** | **`EXTERNAL`** — `SASL_SSL` (mới) | Đường của ứng dụng |
| **`9292` / `9294` / `9296`** | **`MTLS`** — `SSL` + `ssl.client.auth=required` (Lab 5.7) | Đường của mTLS |

`node.id` của 3 broker lần lượt là **2 (kafka-1) · 3 (kafka-2) · 4 (kafka-3)** — nhớ kỹ vì `kafka-configs.sh --entity-type brokers --entity-name` nhận **node id**, không nhận tên container.

### 3) Sinh PKI nội bộ: CA `ca-2023` + keystore cho 3 broker

```bash
cat > ~/kafka-labs/week-05/scripts/gen-certs.sh <<'CCAAK_EOF'
#!/usr/bin/env bash
set -euo pipefail
cd ~/kafka-labs/week-05/certs
PW=${PW:-labpass123}
CA=${1:-ca-2023}          # tên CA
SUFFIX=${2:-2023}         # hậu tố file keystore

# 1) CA tự ký (bỏ qua nếu đã có)
if [ ! -f "$CA.crt" ]; then
  openssl req -new -x509 -keyout "$CA.key" -out "$CA.crt" -days 3650 -nodes \
    -subj "/CN=$CA/OU=Platform/O=Acme/C=VN"
fi

# 2) Mỗi broker một keystore riêng, SAN gồm tên trong docker network + localhost
for B in kafka-1 kafka-2 kafka-3; do
  SAN="DNS:$B,DNS:localhost,IP:127.0.0.1"
  KS="$B.$SUFFIX.p12"
  rm -f "$KS" "$B.csr" "$B.$SUFFIX.crt"

  keytool -genkeypair -alias "$B" -keyalg RSA -keysize 2048 -validity 365 \
    -keystore "$KS" -storetype pkcs12 -storepass "$PW" -keypass "$PW" \
    -dname "CN=$B,OU=Platform,O=Acme,C=VN" -ext "SAN=$SAN"

  keytool -certreq -alias "$B" -keystore "$KS" -storepass "$PW" \
    -file "$B.csr" -ext "SAN=$SAN"

  openssl x509 -req -CA "$CA.crt" -CAkey "$CA.key" -in "$B.csr" \
    -out "$B.$SUFFIX.crt" -days 365 -CAcreateserial -copy_extensions copyall

  keytool -importcert -alias CARoot -file "$CA.crt" -keystore "$KS" -storepass "$PW" -noprompt
  keytool -importcert -alias "$B"   -file "$B.$SUFFIX.crt" -keystore "$KS" -storepass "$PW" -noprompt
done

# 3) Truststore: chỉ chứa CA
TS="truststore.$SUFFIX.p12"
rm -f "$TS"
keytool -importcert -alias "$CA" -file "$CA.crt" -keystore "$TS" \
  -storetype pkcs12 -storepass "$PW" -noprompt

echo "== SAN của kafka-1 =="
openssl x509 -in "kafka-1.$SUFFIX.crt" -noout -text | grep -A1 "Subject Alternative Name"
CCAAK_EOF

chmod +x ~/kafka-labs/week-05/scripts/gen-certs.sh
~/kafka-labs/week-05/scripts/gen-certs.sh ca-2023 2023
```

> 🧠 `-copy_extensions copyall` là dòng quan trọng nhất trong script. Thiếu nó thì CA **vứt bỏ SAN** khi ký và bạn sẽ gặp `No subject alternative names present` — đúng cái bẫy PKI doanh nghiệp mà docs Kafka liệt kê.

### 4) File JAAS của broker (cho mechanism SCRAM ở listener `EXTERNAL`)

```bash
cat > ~/kafka-labs/week-05/secrets/broker_jaas.conf <<'CCAAK_EOF'
KafkaServer {
  org.apache.kafka.common.security.scram.ScramLoginModule required;
};
CCAAK_EOF

cat ~/kafka-labs/week-05/certs/ca-2023.crt > ~/kafka-labs/week-05/certs/ca-bundle.crt
cp ~/kafka-labs/week-05/certs/*.p12 ~/kafka-labs/week-05/secrets/
```

> 📌 `ca-bundle.crt` là file PEM **duy nhất** mà mọi client Node.js của tuần này đọc. Bây giờ nó chỉ chứa `ca-2023`; Lab 5.2 sẽ ghi đè nó thành `ca-2023 + ca-2026`. Nhờ vậy các lab sau không phải sửa code khi CA đổi — đúng cách một fleet client thật hoạt động.

> 📌 Section `KafkaServer` ở đây **không có `username`/`password`** vì inter-broker của lab là `PLAINTEXT` — broker không cần danh tính SASL của riêng nó. Trong production với inter-broker `SASL_SSL` thì section này **bắt buộc** có `username`/`password` của user admin, và user đó phải được tạo bằng `kafka-storage.sh format --add-scram` **trước khi** cluster lên lần đầu.

---

## Lab 5.1 — Thiết kế nhiều listener cho một cluster thật ⭐

**🎯 Mục tiêu:** Biến cluster 3 broker từ "một listener nội bộ + một listener host" thành **kiến trúc 4 listener của production**: `INTERNAL` (PLAINTEXT, inter-broker) · `ADMIN` (PLAINTEXT, vận hành) · `EXTERNAL` (SASL_SSL, ứng dụng) · `CONTROLLER` (riêng). Chứng minh **cả đường nội bộ lẫn đường ngoài cùng hoạt động**.
**🧩 Luyện kỹ năng (liên quan đề):**

- Tên listener **tự do** — `INTERNAL`/`EXTERNAL`/`ADMIN` không phải từ khoá; cái bắt buộc là `listener.security.protocol.map`.
- 5 config phải khớp nhau: `listeners` · `advertised.listeners` · `listener.security.protocol.map` · `inter.broker.listener.name` · `controller.listener.names`.
- Config **theo từng listener** bằng tiền tố `listener.name.<tên-thường>.<config>`.
- Tái hiện lỗi `advertised.listeners` sai — bẫy "bootstrap OK nhưng produce timeout".

**⏱️ ~50 phút** · **Yêu cầu trước:** Chuẩn bị chung (mục 1–4).

### Các bước

1. Tạo file override định nghĩa lại sơ đồ listener.

   ```yaml
   # ~/kafka-labs/docker-compose.w5-listeners.yml
   x-sec-env: &sec-env
     KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,INTERNAL:PLAINTEXT,ADMIN:PLAINTEXT,EXTERNAL:SASL_SSL
     KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
     KAFKA_LISTENER_NAME_EXTERNAL_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
     KAFKA_LISTENER_NAME_EXTERNAL_SSL_KEYSTORE_TYPE: PKCS12
     KAFKA_LISTENER_NAME_EXTERNAL_SSL_KEYSTORE_PASSWORD: labpass123
     KAFKA_LISTENER_NAME_EXTERNAL_SSL_KEY_PASSWORD: labpass123
     KAFKA_LISTENER_NAME_EXTERNAL_SSL_TRUSTSTORE_TYPE: PKCS12
     KAFKA_LISTENER_NAME_EXTERNAL_SSL_TRUSTSTORE_LOCATION: /etc/kafka/secrets/truststore.2023.p12
     KAFKA_LISTENER_NAME_EXTERNAL_SSL_TRUSTSTORE_PASSWORD: labpass123
     KAFKA_LISTENER_NAME_EXTERNAL_SSL_CLIENT_AUTH: none
     KAFKA_OPTS: "-Djava.security.auth.login.config=/etc/kafka/secrets/broker_jaas.conf"

   services:
     kafka-1:
       ports: ["9092:9092", "9192:9192"]
       environment:
         <<: *sec-env
         KAFKA_LISTENERS: INTERNAL://:19092,ADMIN://:9092,EXTERNAL://:9192
         KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-1:19092,ADMIN://localhost:9092,EXTERNAL://localhost:9192
         KAFKA_LISTENER_NAME_EXTERNAL_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka-1.2023.p12
       volumes: ["./week-05/secrets:/etc/kafka/secrets:ro"]

     kafka-2:
       ports: ["9094:9094", "9194:9194"]
       environment:
         <<: *sec-env
         KAFKA_LISTENERS: INTERNAL://:19092,ADMIN://:9094,EXTERNAL://:9194
         KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-2:19092,ADMIN://localhost:9094,EXTERNAL://localhost:9194
         KAFKA_LISTENER_NAME_EXTERNAL_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka-2.2023.p12
       volumes: ["./week-05/secrets:/etc/kafka/secrets:ro"]

     kafka-3:
       ports: ["9096:9096", "9196:9196"]
       environment:
         <<: *sec-env
         KAFKA_LISTENERS: INTERNAL://:19092,ADMIN://:9096,EXTERNAL://:9196
         KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-3:19092,ADMIN://localhost:9096,EXTERNAL://localhost:9196
         KAFKA_LISTENER_NAME_EXTERNAL_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka-3.2023.p12
       volumes: ["./week-05/secrets:/etc/kafka/secrets:ro"]
   ```

2. Khởi động và đọc dòng log xác nhận broker đã bind đủ listener.

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml up -d
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml logs kafka-1 \
     | grep -iE "Awaiting socket connections|advertised|Kafka Server started"
   ```

3. Kiểm tra **đường nội bộ** (`INTERNAL`/`ADMIN`, PLAINTEXT) — mọi lệnh vận hành đi lối này.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
     --create --topic payments.orders.created.v1 --partitions 6 --replication-factor 3
   docker exec kafka-1 /opt/kafka/bin/kafka-metadata-quorum.sh --bootstrap-server kafka-1:19092 describe --status
   ```

4. Tạo credential SCRAM cho ứng dụng và kiểm tra **đường ngoài** (`EXTERNAL`, SASL_SSL).

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 --alter \
     --add-config 'SCRAM-SHA-512=[iterations=8192,password=orders-secret]' \
     --entity-type users --entity-name svc-orders
   ```

   ```javascript
   // ~/kafka-labs/week-05/ext-ping.mjs
   import fs from "node:fs";
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w5-ext-ping",
     brokers: ["localhost:9192", "localhost:9194", "localhost:9196"],
     ssl: { ca: [fs.readFileSync(process.env.CA_BUNDLE ?? "certs/ca-bundle.crt", "utf-8")] },
     sasl: {
       mechanism: "scram-sha-512",
       username: process.env.KUSER ?? "svc-orders",
       password: process.env.KPASS ?? "orders-secret",
     },
     logLevel: logLevel.NOTHING,
   });

   const admin = kafka.admin();
   await admin.connect();
   const cluster = await admin.describeCluster();
   console.log("EXTERNAL OK →", cluster.brokers.map((b) => `${b.nodeId}=${b.host}:${b.port}`).join(" "));
   await admin.disconnect();
   ```

   ```bash
   cd ~/kafka-labs/week-05 && node ext-ping.mjs
   ```

5. **Thí nghiệm bẫy `advertised.listeners` (5 phút, rất đáng làm).** Sửa riêng `kafka-2`:

   ```yaml
   KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-2:19092,ADMIN://localhost:9094,EXTERNAL://kafka-2:9194
   ```

   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml up -d kafka-2
   cd ~/kafka-labs/week-05 && node ext-ping.mjs        # bootstrap vẫn OK
   # nhưng produce vào partition do kafka-2 làm leader sẽ treo rồi timeout
   ```

   Trả lại `EXTERNAL://localhost:9194` và `up -d kafka-2`.

6. **Thí nghiệm bẫy controller listener.** Thêm tạm vào `kafka-3`:

   ```yaml
   KAFKA_CONTROLLER_LISTENER_NAMES: INTERNAL
   ```

   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml up -d kafka-3
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml logs kafka-3 | tail -30
   ```

   Broker **không lên**: `controller.listener.names` không được trùng `inter.broker.listener.name`. Xoá dòng đó, `up -d kafka-3` lại.

### ✅ Kiểm chứng

- Bước 2: log của mỗi broker in **ba** endpoint (`INTERNAL`, `ADMIN`, `EXTERNAL`); listener `CONTROLLER` **không** xuất hiện trong `listeners` của broker vì đây là node `process.roles=broker`.
- Bước 3 và 4 **cùng thành công**: một cluster đang phục vụ hai đối tượng ở hai mức bảo mật khác nhau. Đây chính là câu "*security is optional — a mix of authenticated and unauthenticated clients is supported*" trong docs, nhìn thấy bằng mắt.
- Bước 4: bỏ khối `sasl` khỏi `ext-ping.mjs` → thất bại ở bước xác thực; bỏ khối `ssl` → treo rồi timeout (nói `PLAINTEXT` vào cổng `SASL_SSL`). **Hai lỗi khác nhau, hai tầng khác nhau.**
- Bước 5: `describeCluster()` in `3=kafka-2:9194` — địa chỉ host không resolve được → đúng triệu chứng "bootstrap OK, produce timeout".
- Bước 6: `docker compose ps` cho thấy `kafka-3` ở trạng thái `Restarting`/`Exited`.

### 🧹 Dọn dẹp

```bash
# GIỮ cluster và file override cho Lab 5.2 → 5.5
docker compose -f ~/kafka-labs/docker-compose.cluster.yml \
               -f ~/kafka-labs/docker-compose.w5-listeners.yml ps
```

### 🧠 Ý nghĩa với đề thi

- Đề mô tả cấu hình bằng **tên listener**, không bằng số cổng. Đọc `listener.security.protocol.map` trước, rồi mới xét client nói protocol gì.
- **Broker-only node vẫn phải khai `controller.listener.names`** nhưng **không** đưa controller listener vào `listeners`, và **không** advertise nó.
- "Kết nối bootstrap thành công nhưng produce timeout" → gần như luôn là `advertised.listeners` sai, bất kể protocol nào.

---

## Lab 5.2 — Xoay chứng chỉ sắp hết hạn mà KHÔNG downtime ⭐

**🎯 Mục tiêu:** Chuyển toàn bộ cluster từ CA `ca-2023` sang `ca-2026` trong khi một producer và một consumer chạy liên tục — và chứng minh **không mất một message nào**.
**🧩 Luyện kỹ năng (liên quan đề):**

- Thứ tự bất biến: **truststore (CA mới) TRƯỚC → keystore SAU → gỡ CA cũ CUỐI CÙNG**.
- Keystore/truststore của listener **đã tồn tại** là **per-broker dynamic config** → đổi bằng `kafka-configs.sh`, **không restart**.
- Phương án dự phòng bằng **rolling restart** và quy tắc chờ `UnderReplicatedPartitions` về 0.
- Nhìn thấy hậu quả khi làm **ngược thứ tự**.

**⏱️ ~60 phút** · **Yêu cầu trước:** Lab 5.1 (cluster đang chạy với listener `EXTERNAL`).

### Các bước

1. Sinh CA mới và bộ keystore mới, rồi tạo **bundle tin cả hai CA**.

   ```bash
   cd ~/kafka-labs/week-05
   ./scripts/gen-certs.sh ca-2026 2026

   # truststore của broker: chứa CẢ HAI CA
   cd certs
   rm -f truststore.both.p12
   keytool -importcert -alias ca-2023 -file ca-2023.crt -keystore truststore.both.p12 \
     -storetype pkcs12 -storepass "$PW" -noprompt
   keytool -importcert -alias ca-2026 -file ca-2026.crt -keystore truststore.both.p12 \
     -storepass "$PW" -noprompt
   keytool -list -keystore truststore.both.p12 -storepass "$PW" | grep -c trustedCertEntry   # → 2

   # bundle PEM cho client (kafkajs)
   cat ca-2023.crt ca-2026.crt > ca-bundle.crt

   cp *.p12 ca-bundle.crt ~/kafka-labs/week-05/secrets/
   ```

2. Khởi động **client chạy liên tục** — đây là "đồng hồ downtime" của bài lab.

   ```javascript
   // ~/kafka-labs/week-05/heartbeat.mjs — gửi 1 message/giây và in kết quả từng giây
   import fs from "node:fs";
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w5-heartbeat",
     brokers: ["localhost:9192", "localhost:9194", "localhost:9196"],
     ssl: { ca: [fs.readFileSync(process.env.CA_BUNDLE ?? "certs/ca-bundle.crt", "utf-8")] },
     sasl: { mechanism: "scram-sha-512", username: "svc-orders", password: "orders-secret" },
     retry: { retries: 20, initialRetryTime: 200 },
     logLevel: logLevel.NOTHING,
   });

   const producer = kafka.producer();
   await producer.connect();
   let n = 0, ok = 0, fail = 0;
   setInterval(async () => {
     n += 1;
     try {
       await producer.send({
         topic: "payments.orders.created.v1",
         messages: [{ key: `k${n % 6}`, value: JSON.stringify({ n, at: Date.now() }) }],
       });
       ok += 1;
       process.stdout.write(`\r#${n} ok=${ok} fail=${fail}   `);
     } catch (e) {
       fail += 1;
       console.log(`\n#${n} ✗ ${e.constructor.name}: ${e.message}`);
     }
   }, 1000);
   ```

   ```bash
   cd ~/kafka-labs/week-05 && node heartbeat.mjs      # để chạy trong một cửa sổ terminal riêng
   ```

3. **Pha 1 — mở rộng lòng tin.** Đẩy truststore hai-CA lên **từng broker** bằng dynamic config (không restart).

   ```bash
   for ID in 2 3 4; do
     docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 \
       --entity-type brokers --entity-name $ID --alter \
       --add-config listener.name.external.ssl.truststore.location=/etc/kafka/secrets/truststore.both.p12
   done

   docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 \
     --entity-type brokers --entity-name 2 --describe
   ```

   Client đã dùng `ca-bundle.crt` từ bước 1 nên **phía client cũng đã tin cả hai CA**. Trong production đây là pha dài nhất: chờ mọi team triển khai truststore mới.

4. **Pha 2 — đổi danh tính.** Đổi keystore **từng broker một**, kiểm tra sức khoẻ giữa các bước.

   ```bash
   swap () {   # $1 = node id, $2 = tên container
     docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 \
       --entity-type brokers --entity-name "$1" --alter \
       --add-config listener.name.external.ssl.keystore.location=/etc/kafka/secrets/$2.2026.p12
     sleep 3
     docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
       --describe --under-replicated-partitions
   }

   swap 2 kafka-1
   swap 3 kafka-2
   swap 4 kafka-3
   ```

   Xác nhận cert đang phục vụ đã là cert mới:

   ```bash
   openssl s_client -connect localhost:9192 -servername localhost </dev/null 2>/dev/null \
     | openssl x509 -noout -issuer -subject -dates
   # issuer= /CN=ca-2026/...
   ```

5. **Pha 3 — thu hẹp lòng tin.** Khi mọi broker đã dùng cert `ca-2026`, gỡ CA cũ.

   ```bash
   for ID in 2 3 4; do
     docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 \
       --entity-type brokers --entity-name $ID --alter \
       --add-config listener.name.external.ssl.truststore.location=/etc/kafka/secrets/truststore.2026.p12
   done
   ```

6. **Phương án dự phòng — rolling restart.** Nếu môi trường của bạn không nhận dynamic config (một số bản image), làm theo cách kinh điển: sửa `KAFKA_LISTENER_NAME_EXTERNAL_SSL_KEYSTORE_LOCATION` trong file override cho **một** broker → `docker compose ... up -d kafka-N` → **chờ `--under-replicated-partitions` rỗng** → broker kế tiếp.

   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml up -d kafka-1
   until [ -z "$(docker exec kafka-2 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-2:19092 \
        --describe --under-replicated-partitions)" ]; do sleep 2; echo "chờ URP về 0..."; done
   ```

7. **Thí nghiệm làm NGƯỢC thứ tự (bắt buộc làm, 5 phút).** Dừng `heartbeat.mjs`, chạy lại với truststore **chỉ có CA cũ**:

   ```bash
   CA_BUNDLE=certs/ca-2023.crt node heartbeat.mjs
   ```

   Client không tin `ca-2026` → hỏng ngay lập tức. Đây chính xác là điều xảy ra với **toàn bộ ứng dụng của công ty** nếu bạn đổi keystore trước khi phát CA mới. Chạy lại với `ca-bundle.crt` để phục hồi.

### ✅ Kiểm chứng

- Cửa sổ chạy `heartbeat.mjs` **giữ nguyên `fail=0`** xuyên suốt bước 3 → 5. Đó là bằng chứng "không downtime", và cũng là cách duy nhất chứng minh được điều đó.
- Bước 4: `openssl s_client` in `issuer= /CN=ca-2026`, còn `--under-replicated-partitions` **không in gì** sau mỗi lần swap.
- Bước 7: client chỉ tin CA cũ báo lỗi chuỗi tin cậy (`unable to verify the first certificate` / `SELF_SIGNED_CERT_IN_CHAIN` tuỳ phiên bản Node), **không phải** lỗi xác thực SASL — đọc đúng tên lỗi là biết hỏng ở tầng nào.

### 🧹 Dọn dẹp

```bash
# Gỡ mọi dynamic config của tuần này nếu muốn về trạng thái sạch
for ID in 2 3 4; do
  docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 \
    --entity-type brokers --entity-name $ID --alter \
    --delete-config listener.name.external.ssl.keystore.location,listener.name.external.ssl.truststore.location
done
# GIỮ cluster cho Lab 5.3
```

### 🧠 Ý nghĩa với đề thi

- Câu "xoay chứng chỉ không downtime" có **hai** lời giải đúng: dynamic config (không restart) và rolling restart. Phương án sai luôn là **đổi cert trước rồi mới phát CA**.
- Nhớ **hai luật kiểm tra tin cậy của inter-broker listener** (ngược chiều nhau) — chúng tồn tại chính là để chặn bạn làm sai thứ tự. Listener client **không** được bảo vệ như thế.
- `--under-replicated-partitions` là cổng kiểm tra giữa hai node trong **mọi** thủ tục rolling, không riêng gì bảo mật.

---

## Lab 5.3 — SCRAM vận hành: thêm, xoay, thu hồi lúc đang chạy

**🎯 Mục tiêu:** Tạo 3 principal, xoay mật khẩu của 1 principal, **thu hồi** 1 principal — và chứng minh (a) client của principal bị thu hồi chết, (b) hai principal còn lại **không hề hấn**, (c) thu hồi **chưa chắc** cắt được kết nối đang mở.
**🧩 Luyện kỹ năng (liên quan đề):**

- `kafka-configs.sh --entity-type users` là toàn bộ vòng đời credential — không restart, không file trên đĩa.
- `--describe` in salt/stored_key/iterations, **không bao giờ in mật khẩu**.
- `connections.max.reauth.ms` mặc định **0** → thu hồi không cắt session cũ.

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 5.1.

### Các bước

1. Tạo 3 user với iteration khác nhau để thấy tham số có hiệu lực.

   ```bash
   kcfg () { docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 "$@"; }

   kcfg --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=orders-secret]'  --entity-type users --entity-name svc-orders
   kcfg --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=billing-secret]' --entity-type users --entity-name svc-billing
   kcfg --alter --add-config 'SCRAM-SHA-512=[iterations=4096,password=audit-secret]'   --entity-type users --entity-name svc-audit

   kcfg --describe --entity-type users
   ```

2. Xác nhận cả 3 đều vào được listener `EXTERNAL`.

   ```bash
   cd ~/kafka-labs/week-05
   KUSER=svc-orders  KPASS=orders-secret  node ext-ping.mjs
   KUSER=svc-billing KPASS=billing-secret node ext-ping.mjs
   KUSER=svc-audit   KPASS=audit-secret   node ext-ping.mjs
   ```

3. **Xoay mật khẩu** của `svc-billing` lúc đang chạy (không restart gì cả).

   ```bash
   kcfg --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=billing-secret-v2]' \
     --entity-type users --entity-name svc-billing

   KUSER=svc-billing KPASS=billing-secret    node ext-ping.mjs   # ✗ mật khẩu cũ chết ngay
   KUSER=svc-billing KPASS=billing-secret-v2 node ext-ping.mjs   # ✓ mật khẩu mới dùng được ngay
   ```

4. **Thu hồi** `svc-audit`, rồi kiểm tra hai user kia.

   ```bash
   kcfg --alter --delete-config 'SCRAM-SHA-512' --entity-type users --entity-name svc-audit
   kcfg --describe --entity-type users --entity-name svc-audit    # không còn cấu hình nào

   KUSER=svc-audit   KPASS=audit-secret      node ext-ping.mjs    # ✗ SaslAuthenticationException
   KUSER=svc-orders  KPASS=orders-secret     node ext-ping.mjs    # ✓ không ảnh hưởng
   KUSER=svc-billing KPASS=billing-secret-v2 node ext-ping.mjs    # ✓ không ảnh hưởng
   ```

5. **Thí nghiệm quan trọng nhất của lab — thu hồi KHÔNG cắt kết nối đang mở.**

   ```bash
   # a) mở một kết nối dài bằng svc-billing
   cd ~/kafka-labs/week-05
   KUSER=svc-billing KPASS=billing-secret-v2 node heartbeat.mjs &   # để chạy nền
   sleep 10

   # b) thu hồi credential trong khi nó đang chạy
   kcfg --alter --delete-config 'SCRAM-SHA-512' --entity-type users --entity-name svc-billing

   # c) quan sát 60 giây: fail vẫn = 0, message vẫn được ghi
   ```

6. Bật **re-authentication** rồi lặp lại bước 5 để thấy khác biệt.

   ```yaml
   # thêm vào khối x-sec-env của docker-compose.w5-listeners.yml
   KAFKA_LISTENER_NAME_EXTERNAL_CONNECTIONS_MAX_REAUTH_MS: 30000
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml up -d
   ```

   > ⚠️ Không phải client nào cũng hỗ trợ SASL re-authentication. Với `kafkajs`, kết nối sẽ **bị ngắt** khi hết hạn thay vì tự xác thực lại — đó vẫn là kết quả đúng về mặt bảo mật (session không sống mãi), chỉ khác về trải nghiệm client. **Gỡ dòng này sau khi thí nghiệm xong** để các lab sau không bị nhiễu.

7. Biện pháp **tức thời** khi cần chặn ngay mà không chờ re-auth: thêm **Deny ACL** (làm ở Lab 5.4).

### ✅ Kiểm chứng

- Bước 1: `--describe` in dạng `SCRAM-SHA-512=salt=...,stored_key=...,server_key=...,iterations=8192` — **không có mật khẩu**, và iteration đúng như đã đặt.
- Bước 3: mật khẩu cũ hỏng và mật khẩu mới chạy **trong cùng một giây**, không restart broker. Đây là điểm khác biệt số một giữa SCRAM và PLAIN.
- Bước 4: chỉ principal bị thu hồi chết; hai principal kia không nhận bất kỳ ảnh hưởng nào — chứng minh credential là **per-principal**, không phải cấu hình toàn cục.
- Bước 5: `fail=0` sau khi credential đã bị xoá → **đúng hành vi mặc định** (`connections.max.reauth.ms=0`). Nếu bạn thấy client chết ngay thì hãy kiểm tra xem môi trường có đặt sẵn config này không.

### 🧹 Dọn dẹp

```bash
kill %1 2>/dev/null           # dừng heartbeat chạy nền
# gỡ KAFKA_LISTENER_NAME_EXTERNAL_CONNECTIONS_MAX_REAUTH_MS khỏi file override rồi:
cd ~/kafka-labs && docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml up -d
# tạo lại credential cho Lab 5.4
docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 --alter \
  --add-config 'SCRAM-SHA-512=[password=billing-secret-v2]' --entity-type users --entity-name svc-billing
```

### 🧠 Ý nghĩa với đề thi

- "Thêm/xoay/thu hồi user **không restart broker**, không lưu mật khẩu dạng rõ" → **luôn là SCRAM**, không bao giờ là PLAIN.
- Câu hỏi "đã xoá credential lúc 10:00, 10:20 vẫn thấy nó ghi" → `connections.max.reauth.ms=0`. Hai cách xử lý: **Deny ACL** (ngay lập tức) và bật re-authentication (lâu dài).
- Credential cho **inter-broker** là ngoại lệ: phải tạo bằng `kafka-storage.sh format --add-scram` **trước** lần khởi động đầu tiên.

---

## Lab 5.4 — ACL ở quy mô: PREFIXED theo tenant, Deny thắng Allow ⭐

**🎯 Mục tiêu:** Bật `StandardAuthorizer` trên **cả broker lẫn controller**, quản 2 tenant bằng vài ACL `PREFIXED`, tái hiện `TopicAuthorizationException` rồi `GroupAuthorizationException`, và chứng minh **Deny thắng Allow**.
**🧩 Luyện kỹ năng (liên quan đề):**

- `authorizer.class.name` phải đặt trên **mọi node**, kể cả controller.
- `--producer` = Write + Describe + Create; `--consumer --group` thêm Read trên Group.
- `PREFIXED` phủ topic **sẽ tạo trong tương lai**; `--resource-pattern-type match` để truy vấn.
- Deny thắng Allow bất kể pattern rộng hay hẹp.

**⏱️ ~55 phút** · **Yêu cầu trước:** Lab 5.1 và 5.3.

### Các bước

1. Bật authorizer. Tạo file override thứ hai (**không** sửa file của Lab 5.1).

   ```yaml
   # ~/kafka-labs/docker-compose.w5-acl.yml
   x-authz-env: &authz-env
     KAFKA_AUTHORIZER_CLASS_NAME: org.apache.kafka.metadata.authorizer.StandardAuthorizer
     KAFKA_SUPER_USERS: "User:ANONYMOUS"     # listener ADMIN/INTERNAL là PLAINTEXT → principal ANONYMOUS
     KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: "false"

   services:
     controller: { environment: { <<: *authz-env } }
     kafka-1:    { environment: { <<: *authz-env } }
     kafka-2:    { environment: { <<: *authz-env } }
     kafka-3:    { environment: { <<: *authz-env } }
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml -f docker-compose.w5-acl.yml up -d
   ```

   > ⚠️ `super.users` ngăn cách bằng **dấu chấm phẩy**: `"User:ANONYMOUS;User:admin"`. Dùng dấu phẩy là tự khoá mình ra ngoài — đúng bẫy của câu hỏi số 25.

2. Tạo topic cho 2 tenant qua đường ADMIN (principal `ANONYMOUS` là super user nên không bị chặn).

   ```bash
   kt () { docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 "$@"; }
   for T in payments.orders.created.v1 payments.orders.dlq.v1 logistics.shipments.created.v1; do
     kt --create --topic "$T" --partitions 3 --replication-factor 3 --if-not-exists
   done
   kt --list
   ```

3. **Tái hiện `TopicAuthorizationException`.**

   ```bash
   cd ~/kafka-labs/week-05
   KUSER=svc-orders KPASS=orders-secret node heartbeat.mjs
   # → #1 ✗ ... Not authorized to access topics: [payments.orders.created.v1]
   ```

4. Cấp quyền producer bằng **một** ACL `PREFIXED` cho cả tenant.

   ```bash
   kacl () { docker exec kafka-1 /opt/kafka/bin/kafka-acls.sh --bootstrap-server kafka-1:19092 "$@"; }

   kacl --add --allow-principal User:svc-orders --producer \
        --topic payments. --resource-pattern-type prefixed

   kacl --list --topic payments. --resource-pattern-type prefixed
   ```

   Chạy lại `heartbeat.mjs` → chạy được. Một ACL, phủ **mọi** topic bắt đầu bằng `payments.`.

5. **Tái hiện `GroupAuthorizationException`.**

   ```javascript
   // ~/kafka-labs/week-05/ext-consumer.mjs
   import fs from "node:fs";
   import { Kafka, logLevel } from "kafkajs";
   const kafka = new Kafka({
     clientId: "w5-consumer",
     brokers: ["localhost:9192", "localhost:9194", "localhost:9196"],
     ssl: { ca: [fs.readFileSync("certs/ca-bundle.crt", "utf-8")] },
     sasl: { mechanism: "scram-sha-512", username: process.env.KUSER, password: process.env.KPASS },
     logLevel: logLevel.NOTHING,
   });
   const consumer = kafka.consumer({ groupId: process.env.KGROUP ?? "payments.reconcile" });
   await consumer.connect();
   await consumer.subscribe({ topic: process.env.KTOPIC ?? "payments.orders.created.v1", fromBeginning: true });
   await consumer.run({ eachMessage: async ({ message }) => console.log("←", message.value.toString().slice(0, 60)) });
   ```

   ```bash
   KUSER=svc-orders KPASS=orders-secret node ext-consumer.mjs
   # → GroupAuthorizationException: Not authorized to access group: payments.reconcile
   ```

6. Cấp quyền consumer, cũng bằng **PREFIXED** cho cả topic lẫn group.

   ```bash
   kacl --add --allow-principal User:svc-orders --operation Read --operation Describe \
        --topic payments. --resource-pattern-type prefixed
   kacl --add --allow-principal User:svc-orders --operation Read \
        --group payments. --resource-pattern-type prefixed

   KUSER=svc-orders KPASS=orders-secret node ext-consumer.mjs   # chạy được
   ```

7. **Chứng minh PREFIXED phủ topic tương lai.**

   ```bash
   kt --create --topic payments.orders.audit.v1 --partitions 3 --replication-factor 3
   KTOPIC=payments.orders.audit.v1 KUSER=svc-orders KPASS=orders-secret node ext-consumer.mjs
   # chạy ngay, KHÔNG cần thêm ACL nào
   ```

8. **Chứng minh Deny thắng Allow.**

   ```bash
   kacl --add --deny-principal User:svc-orders --operation Write \
        --topic payments.orders.dlq.v1 --resource-pattern-type literal

   # sửa topic trong heartbeat.mjs thành payments.orders.dlq.v1 rồi chạy — bị từ chối
   # dù ACL PREFIXED "payments." vẫn còn nguyên và vẫn ALLOW Write
   ```

9. **Cách ly tenant.** `svc-orders` không được đụng vào tenant khác:

   ```bash
   KTOPIC=logistics.shipments.created.v1 KUSER=svc-orders KPASS=orders-secret node ext-consumer.mjs
   # → TopicAuthorizationException
   ```

10. **Hai lệnh tra cứu phải thuộc.**

    ```bash
    kacl --list --principal User:svc-orders
    kacl --list --topic payments.orders.created.v1                              # rỗng — chỉ khớp LITERAL
    kacl --list --topic payments.orders.created.v1 --resource-pattern-type match  # thấy hết
    ```

### ✅ Kiểm chứng

- Bước 4: `--list` in đúng **ba** operation cho cờ `--producer`: `WRITE`, `DESCRIBE`, `CREATE`.
- Bước 3 và 5 cho **hai ngoại lệ khác nhau** — tên ngoại lệ chỉ thẳng resource type còn thiếu.
- Bước 7: topic mới chạy được **mà không thêm ACL** — đây là toàn bộ giá trị của quy ước đặt tên.
- Bước 8: Deny có hiệu lực dù ALLOW prefixed rộng hơn vẫn tồn tại.
- Bước 10: `--list` mặc định **rỗng** trong khi `--resource-pattern-type match` in đủ — nhớ cặp này, nó cứu bạn mỗi lần audit ACL.
- Nếu ngay sau khi `--add` mà client vẫn bị từ chối vài giây: **bình thường**. ACL lan truyền qua `__cluster_metadata` nên **eventually consistent**.

### 🧹 Dọn dẹp

```bash
# GIỮ authorizer + ACL cho Lab 5.5 (lab đó dựa trên trạng thái này)
docker exec kafka-1 /opt/kafka/bin/kafka-acls.sh --bootstrap-server kafka-1:19092 --list
```

### 🧠 Ý nghĩa với đề thi

- Bài toán "300 topic, 80 service" có **một** lời giải đúng: **quy ước đặt tên + PREFIXED + một principal cho một app**. Mọi phương án giảm số ACL bằng cách **giảm kiểm soát** (super user, allow-everyone, `User:*`) đều sai.
- `allow.everyone.if.no.acl.found` chỉ nới cho resource **chưa có ACL nào** — thêm một ACL là cả thế giới mất quyền.
- Nhớ `--producer` = Write + Describe + Create; `--consumer --group g` = Read + Describe trên Topic **+ Read** trên Group; Read/Write/Delete **ngầm cho** Describe.

---

## Lab 5.5 — 💥 Gây hỏng rồi sửa: thu hồi nhầm ACL của service đang chạy

**🎯 Mục tiêu:** Mô phỏng một sự cố thật — dọn ACL quá tay làm chết một service đang chạy — rồi **chẩn đoán bằng `kafka-authorizer.log`** và cấp lại **đúng quyền tối thiểu**, không nhiều hơn một operation nào.
**🧩 Luyện kỹ năng (liên quan đề):**

- `kafka-authorizer.log` ghi **DENY ở INFO**, ALLOW ở DEBUG → dòng DENY có sẵn, không cần đổi logging.
- Dòng DENY cho đủ **principal + operation + resource + host + request** → chính là đặc tả của bản vá.
- Phản xạ "cấp `--operation All` cho xong" là sai; phải đọc log rồi cấp đúng.

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 5.4 (authorizer đang bật).

### Các bước

1. Dựng một service "đang chạy production": cấp quyền đầy đủ cho `svc-billing` rồi bật consumer liên tục.

   ```bash
   kacl --add --allow-principal User:svc-billing --consumer \
        --topic payments. --resource-pattern-type prefixed \
        --group billing- --resource-pattern-type prefixed
   ```

   > 📌 Nếu bản CLI của bạn không nhận **hai** `--resource-pattern-type` trong một lệnh, tách thành hai lệnh:
   > `--add --allow-principal User:svc-billing --operation Read --operation Describe --topic payments. --resource-pattern-type prefixed`
   > và `--add --allow-principal User:svc-billing --operation Read --group billing- --resource-pattern-type prefixed`.

   ```bash
   cd ~/kafka-labs/week-05
   KUSER=svc-billing KPASS=billing-secret-v2 KGROUP=billing-etl node ext-consumer.mjs
   # để chạy trong một terminal riêng — đây là "service production"
   ```

2. **Gây hỏng.** Một đồng nghiệp dọn ACL và xoá nhầm nhóm quyền của `svc-billing`:

   ```bash
   kacl --remove --allow-principal User:svc-billing --operation Read --operation Describe \
        --topic payments. --resource-pattern-type prefixed --force
   kacl --remove --allow-principal User:svc-billing --operation Read \
        --group billing- --resource-pattern-type prefixed --force
   ```

   Terminal của service bắt đầu văng ngoại lệ.

3. **Chẩn đoán — đừng đoán, hãy đọc log.**

   ```bash
   for C in kafka-1 kafka-2 kafka-3; do
     echo "===== $C ====="
     docker exec $C sh -lc 'tail -n 40 /opt/kafka/logs/kafka-authorizer.log 2>/dev/null | grep -i denied' \
       || docker logs --tail 200 $C 2>&1 | grep -i "denied"
   done
   ```

   Bạn sẽ thấy các dòng dạng:

   ```
   INFO Principal = User:svc-billing is Denied operation = Read on resource = Topic:LITERAL:payments.orders.created.v1
        from host = 172.19.0.1 for request = Fetch with resourceRefCount = 1
   INFO Principal = User:svc-billing is Denied operation = Read on resource = Group:LITERAL:billing-etl
        from host = 172.19.0.1 for request = OffsetFetch with resourceRefCount = 1
   ```

   > 📌 Nếu file `kafka-authorizer.log` không tồn tại trong image bạn dùng, nhánh `docker logs ... | grep denied` ở trên vẫn lấy được cùng thông tin từ console appender. Ghi lại **đường dẫn thật** trên hệ của bạn — biết log ở đâu là nửa phần việc chẩn đoán.

4. **Lập danh sách quyền thiếu từ log** (đây là bước tư duy, hãy tự viết ra giấy trước khi gõ lệnh):

   | Dòng log | Resource | Operation cần cấp |
   | --- | --- | --- |
   | `request = Fetch` | `Topic:payments.orders.created.v1` | `Read` (ngầm có `Describe`) |
   | `request = OffsetFetch` | `Group:billing-etl` | `Read` |

5. **Sửa bằng quyền tối thiểu** — và giữ nguyên chiến lược PREFIXED thay vì vá từng topic:

   ```bash
   kacl --add --allow-principal User:svc-billing --operation Read --operation Describe \
        --topic payments. --resource-pattern-type prefixed
   kacl --add --allow-principal User:svc-billing --operation Read \
        --group billing- --resource-pattern-type prefixed
   ```

   Service tự hồi phục sau vài giây (client retry), không cần restart.

6. **Đối chiếu phương án sai** để thấy vì sao nó tệ: nếu bạn "sửa nhanh" bằng

   ```bash
   # KHÔNG làm ở production
   kacl --add --allow-principal User:svc-billing --operation All --topic '*'
   ```

   thì service cũng chạy lại — nhưng giờ nó có quyền **Delete** mọi topic của mọi tenant. Gỡ ngay:

   ```bash
   kacl --remove --allow-principal User:svc-billing --operation All --topic '*' --force
   ```

### ✅ Kiểm chứng

- Bước 3: log cho **hai** dòng DENY với **hai** resource type khác nhau — nếu bạn chỉ sửa một cái thì service vẫn chết, và log sẽ nói cho bạn biết cái còn lại.
- Bước 5: `kacl --list --principal User:svc-billing` in đúng **ba** entry (Read + Describe trên Topic PREFIXED, Read trên Group PREFIXED) — không có `All`, không có wildcard.
- Service hồi phục **mà không restart** → ACL có hiệu lực ngay ở request kế tiếp, khác hẳn credential (Lab 5.3).

### 🧹 Dọn dẹp

```bash
# GIỮ nguyên trạng thái cho Lab 5.6
docker exec kafka-1 /opt/kafka/bin/kafka-acls.sh --bootstrap-server kafka-1:19092 --list --principal User:svc-billing
```

### 🧠 Ý nghĩa với đề thi

- Đề rất hay cho **nguyên văn một dòng log DENY** rồi hỏi "lệnh nào khôi phục đúng quyền cần thiết". Đáp án luôn là cờ `--consumer`/`--producer` hoặc danh sách operation khớp log, **không bao giờ** là `--operation All` và **không bao giờ** là thêm vào `super.users`.
- Ngoại lệ phía client cho bạn **resource type**; log authorizer cho bạn **operation + resource cụ thể + host**. Dùng cả hai.
- ACL có hiệu lực **ngay** (sau khi lan truyền), credential thì không cắt được session cũ. Hai vòng đời khác nhau — đừng nhầm.

---

## Lab 5.6 — 💥 Gây hỏng rồi sửa: `AclAuthorizer` làm broker không khởi động

**🎯 Mục tiêu:** Tự tay tạo ra lỗi kinh điển nhất của tài liệu CCAAK đời cũ — khai authorizer của thời ZooKeeper trên cluster KRaft — rồi đọc log và sửa.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc `ConfigException` và nhận ra đây là **lỗi cấu hình lúc khởi động**, không phải lỗi runtime.
- Phân biệt `kafka.security.authorizer.AclAuthorizer` (ZooKeeper, đã gỡ ở 4.0) và `org.apache.kafka.metadata.authorizer.StandardAuthorizer` (KRaft).
- Thấy rằng cluster **vẫn phục vụ** khi 1/3 broker chết — và vì sao đó không phải lý do để thong thả.

**⏱️ ~25 phút** · **Yêu cầu trước:** Lab 5.4.

### Các bước

1. Gây hỏng **một** broker (không phải cả cụm — đây là cách hỏng thật khi rolling).

   ```yaml
   # ~/kafka-labs/docker-compose.w5-broken.yml
   services:
     kafka-3:
       environment:
         KAFKA_AUTHORIZER_CLASS_NAME: kafka.security.authorizer.AclAuthorizer
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml \
                  -f docker-compose.w5-acl.yml -f docker-compose.w5-broken.yml up -d kafka-3
   ```

2. Quan sát triệu chứng ở tầng hạ tầng trước.

   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml \
                  -f docker-compose.w5-acl.yml -f docker-compose.w5-broken.yml ps
   # kafka-3: Restarting / Exited
   ```

3. Đọc log — **đây mới là bước cho điểm**.

   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml \
                  -f docker-compose.w5-acl.yml -f docker-compose.w5-broken.yml logs kafka-3 | tail -30
   ```

   ```
   org.apache.kafka.common.config.ConfigException: Invalid value kafka.security.authorizer.AclAuthorizer
   for configuration authorizer.class.name: Class kafka.security.authorizer.AclAuthorizer could not be found.
   ```

4. Đọc tác động lên cluster trong lúc broker đang chết.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
     --describe --under-replicated-partitions
   docker exec kafka-1 /opt/kafka/bin/kafka-metadata-quorum.sh --bootstrap-server kafka-1:19092 describe --status
   ```

   Partition có replica trên `kafka-3` đang **under-replicated**; với RF=3 / `min.insync.replicas=2` thì producer `acks=all` **vẫn ghi được** — mất thêm một broker nữa mới dừng ghi.

5. Sửa: gỡ file override hỏng và khởi động lại.

   ```bash
   rm ~/kafka-labs/docker-compose.w5-broken.yml
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml \
                  -f docker-compose.w5-acl.yml up -d kafka-3

   until [ -z "$(docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
        --describe --under-replicated-partitions)" ]; do sleep 2; echo "chờ URP về 0..."; done
   echo "URP = 0 — được phép đụng vào broker tiếp theo"
   ```

6. (Mở rộng, 5 phút) Thử một biến thể sai khác: gõ nhầm package thành `org.apache.kafka.metadata.StandardAuthorizer` (thiếu `.authorizer`) → **cùng một** `ConfigException`. Thông điệp lỗi này bao trùm mọi lỗi "class không tìm thấy" cho các config kiểu `class`.

### ✅ Kiểm chứng

- Bước 3: log kết thúc bằng `ConfigException ... could not be found` và **không có** dòng `Kafka Server started` — dấu hiệu chắc chắn của lỗi cấu hình khởi động, khác hẳn lỗi runtime (broker lên rồi mới hỏng).
- Bước 4: `--under-replicated-partitions` in danh sách partition; quorum controller vẫn khoẻ vì controller không bị đụng tới.
- Bước 5: sau khi URP về 0 mới coi là khôi phục xong. **Đừng** kết luận "đã sửa" chỉ vì container ở trạng thái `Up`.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml -f docker-compose.w5-acl.yml ps
# GIỮ cluster cho Lab 5.7
```

### 🧠 Ý nghĩa với đề thi

- Đây là **bẫy version số một** của domain Security. Mọi phương án nhắc `AclAuthorizer`, `--zookeeper`, `zookeeper.connect`, `zookeeper.set.acl` hay znode đều sai ở Kafka 4.x.
- Nhớ nhận diện nhanh bằng **package**: `kafka.security.authorizer.*` = ZooKeeper · `org.apache.kafka.metadata.authorizer.*` = KRaft.
- Và nhớ đặt authorizer trên **controller** nữa — quên controller thì các thao tác quản trị được chuyển tiếp lên đó sẽ không bị kiểm soát.

---

## Lab 5.7 — mTLS và `ssl.principal.mapping.rules`

**🎯 Mục tiêu:** Dựng một listener mTLS thứ tư, xem principal **trước** khi có mapping rule (DN đầy đủ, ACL không khớp) và **sau** khi có rule (`User:svc-report`, ACL khớp ngay).
**🧩 Luyện kỹ năng (liên quan đề):**

- `ssl.client.auth=required` là mTLS thật; `requested` là bẫy.
- Principal mặc định của mTLS là **toàn bộ DN**.
- `ssl.principal.mapping.rules` đánh giá **theo thứ tự, cái đầu tiên khớp thắng**, kết thúc bằng `DEFAULT`.

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 5.4 (authorizer đang bật).

### Các bước

1. Sinh cert cho client `svc-report` (dùng CA hiện hành `ca-2026`), xuất ra PEM cho `kafkajs`.

   ```bash
   cd ~/kafka-labs/week-05/certs
   openssl req -new -newkey rsa:2048 -nodes -keyout svc-report.key -out svc-report.csr \
     -subj "/CN=svc-report/OU=Analytics/O=Acme/C=VN"
   openssl x509 -req -CA ca-2026.crt -CAkey ca-2026.key -in svc-report.csr \
     -out svc-report.crt -days 365 -CAcreateserial
   openssl x509 -in svc-report.crt -noout -subject
   cp svc-report.* ~/kafka-labs/week-05/secrets/
   ```

2. Thêm listener `MTLS`. Tạo file override thứ ba.

   ```yaml
   # ~/kafka-labs/docker-compose.w5-mtls.yml
   x-mtls-env: &mtls-env
     KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,INTERNAL:PLAINTEXT,ADMIN:PLAINTEXT,EXTERNAL:SASL_SSL,MTLS:SSL
     KAFKA_LISTENER_NAME_MTLS_SSL_CLIENT_AUTH: required
     KAFKA_LISTENER_NAME_MTLS_SSL_KEYSTORE_TYPE: PKCS12
     KAFKA_LISTENER_NAME_MTLS_SSL_KEYSTORE_PASSWORD: labpass123
     KAFKA_LISTENER_NAME_MTLS_SSL_KEY_PASSWORD: labpass123
     KAFKA_LISTENER_NAME_MTLS_SSL_TRUSTSTORE_TYPE: PKCS12
     KAFKA_LISTENER_NAME_MTLS_SSL_TRUSTSTORE_LOCATION: /etc/kafka/secrets/truststore.both.p12
     KAFKA_LISTENER_NAME_MTLS_SSL_TRUSTSTORE_PASSWORD: labpass123

   services:
     kafka-1:
       ports: ["9092:9092", "9192:9192", "9292:9292"]
       environment:
         <<: *mtls-env
         KAFKA_LISTENERS: INTERNAL://:19092,ADMIN://:9092,EXTERNAL://:9192,MTLS://:9292
         KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-1:19092,ADMIN://localhost:9092,EXTERNAL://localhost:9192,MTLS://localhost:9292
         KAFKA_LISTENER_NAME_MTLS_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka-1.2026.p12
     kafka-2:
       ports: ["9094:9094", "9194:9194", "9294:9294"]
       environment:
         <<: *mtls-env
         KAFKA_LISTENERS: INTERNAL://:19092,ADMIN://:9094,EXTERNAL://:9194,MTLS://:9294
         KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-2:19092,ADMIN://localhost:9094,EXTERNAL://localhost:9194,MTLS://localhost:9294
         KAFKA_LISTENER_NAME_MTLS_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka-2.2026.p12
     kafka-3:
       ports: ["9096:9096", "9196:9196", "9296:9296"]
       environment:
         <<: *mtls-env
         KAFKA_LISTENERS: INTERNAL://:19092,ADMIN://:9096,EXTERNAL://:9196,MTLS://:9296
         KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-3:19092,ADMIN://localhost:9096,EXTERNAL://localhost:9196,MTLS://localhost:9296
         KAFKA_LISTENER_NAME_MTLS_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka-3.2026.p12
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml \
                  -f docker-compose.w5-acl.yml -f docker-compose.w5-mtls.yml up -d
   ```

3. Cấp ACL cho **tên ngắn** (giống cách mọi runbook viết) rồi thử kết nối mTLS.

   ```bash
   kacl --add --allow-principal User:svc-report --operation Read --operation Describe \
        --topic payments. --resource-pattern-type prefixed
   kacl --add --allow-principal User:svc-report --operation Read \
        --group reporting- --resource-pattern-type prefixed
   ```

   ```javascript
   // ~/kafka-labs/week-05/mtls-consumer.mjs
   import fs from "node:fs";
   import { Kafka, logLevel } from "kafkajs";
   const kafka = new Kafka({
     clientId: "w5-mtls",
     brokers: ["localhost:9292", "localhost:9294", "localhost:9296"],
     ssl: {
       ca: [fs.readFileSync("certs/ca-bundle.crt", "utf-8")],
       key: fs.readFileSync("certs/svc-report.key", "utf-8"),
       cert: fs.readFileSync("certs/svc-report.crt", "utf-8"),
     },
     logLevel: logLevel.NOTHING,
   });
   const consumer = kafka.consumer({ groupId: "reporting-daily" });
   await consumer.connect();
   await consumer.subscribe({ topic: "payments.orders.created.v1", fromBeginning: true });
   await consumer.run({ eachMessage: async ({ message }) => console.log("←", message.value.toString().slice(0, 60)) });
   ```

   ```bash
   cd ~/kafka-labs/week-05 && node mtls-consumer.mjs
   # → TopicAuthorizationException, mặc dù ACL cho User:svc-report đã tồn tại
   ```

4. **Xem principal mà broker thật sự thấy.**

   ```bash
   docker exec kafka-1 sh -lc 'tail -n 20 /opt/kafka/logs/kafka-authorizer.log 2>/dev/null | grep -i denied' \
     || docker logs --tail 200 kafka-1 2>&1 | grep -i denied
   # Principal = User:CN=svc-report,OU=Analytics,O=Acme,C=VN is Denied operation = Describe ...
   ```

5. Thêm **principal mapping rule** và khởi động lại (đây là config broker-level, read-only → rolling restart).

   ```yaml
   # thêm vào khối x-mtls-env
   KAFKA_SSL_PRINCIPAL_MAPPING_RULES: "RULE:^CN=(.*?),.*$$/$$1/,DEFAULT"
   ```

   > ⚠️ Trong `docker-compose.yml`, `$` phải viết **`$$`** nếu không Compose sẽ coi `$1` là biến môi trường và thay bằng chuỗi rỗng. Đây là lỗi copy-paste kinh điển khi đưa mapping rule vào Compose/Helm.

   ```bash
   cd ~/kafka-labs
   for B in kafka-1 kafka-2 kafka-3; do
     docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml \
                    -f docker-compose.w5-acl.yml -f docker-compose.w5-mtls.yml up -d $B
     until [ -z "$(docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
          --describe --under-replicated-partitions)" ]; do sleep 2; done
   done
   ```

6. Chạy lại `mtls-consumer.mjs` → chạy được, **không đổi một dòng ACL nào**.

7. (Mở rộng, 5 phút) Đổi `KAFKA_LISTENER_NAME_MTLS_SSL_CLIENT_AUTH` sang `requested`, bỏ `key`/`cert` khỏi `mtls-consumer.mjs` và chạy lại: client **vẫn kết nối được** với principal `User:ANONYMOUS`. Đó chính là "an toàn giả" mà docs cảnh báo.

### ✅ Kiểm chứng

- Bước 3: ACL đúng, credential đúng, nhưng vẫn bị từ chối → chứng tỏ vấn đề nằm ở **hình dạng principal**, không phải ở quyền.
- Bước 4: log in principal là **DN đầy đủ** — bằng chứng trực tiếp, không phải suy đoán.
- Bước 6: cùng một ACL, cùng một cert, chỉ thêm mapping rule là chạy.
- Bước 7: kết nối **không có cert** vẫn thành công với `requested` — và nếu `allow.everyone.if.no.acl.found=false` thì nó sẽ bị chặn ở tầng ACL với principal `ANONYMOUS`, không phải ở tầng xác thực. Đọc kỹ principal trong log để phân biệt.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml -f docker-compose.w5-listeners.yml \
               -f docker-compose.w5-acl.yml -f docker-compose.w5-mtls.yml down
rm -f docker-compose.w5-listeners.yml docker-compose.w5-acl.yml docker-compose.w5-mtls.yml
# giữ ~/kafka-labs/week-05/certs nếu muốn làm lại lab; xoá nếu không:
# rm -rf ~/kafka-labs/week-05
```

### 🧠 Ý nghĩa với đề thi

- Câu "ACL viết `User:svc-x` nhưng mTLS vẫn bị từ chối" → thiếu **`ssl.principal.mapping.rules`**. Phương án "viết lại ACL bằng DN đầy đủ" chạy được nhưng **không phải** cách tối thiểu và rất dễ vỡ khi cấp lại cert với OU khác.
- Rule đánh giá **theo thứ tự**, cái đầu tiên khớp thắng, luôn có `DEFAULT` ở cuối; `/L` và `/U` ép chữ thường/hoa.
- `ssl.principal.mapping.rules` là config **broker-level read-only** → cần rolling restart, khác với keystore/truststore (dynamic).

---

> ✅ Xong 7 lab? Quay lại **Lab checklist** trong [plan tuần](README.md#-lab-checklist) tick từng ô, rồi làm [questions.md](questions.md) trong **45 phút, không mở tài liệu** — đó chính là **MINI-MOCK SEC** và là **cổng chặn ≥70%** để được sang Tuần 6.
