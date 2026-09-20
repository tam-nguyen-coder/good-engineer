# 🧪 Hands-on Labs — Tuần 7: Security (TLS · SASL · ACL · Quotas) + Testing

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: 2 file compose chuẩn ở [Tuần 1 — Lab 1.1 / 1.2](../week-01/labs.md), `kafkajs` trong `~/kafka-labs/`, và **Java 17+** cho Lab 7.5 / 7.6.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung

```bash
cd ~/kafka-labs
mkdir -p week-07/{certs,jaas,gradle-tests}
cd week-07
```

> ⚠️ **Sơ đồ cổng của tuần này — đọc trước khi dựng.** Cluster Tuần 1 đã chiếm sẵn:
>
> | Cổng | Đang dùng cho |
> |---|---|
> | `9092` / `9094` / `9096` | `PLAINTEXT_HOST` của kafka-1 / kafka-2 / kafka-3 |
> | `9093` | **CONTROLLER** — tuyệt đối không dùng lại |
> | `19092` | listener nội bộ trong docker network |
>
> Vì vậy tuần này dùng **`9095`** cho listener `SSL` và **`9097`** cho listener `SASL_SSL`. Nhầm sang 9093 là lỗi khiến broker không khởi động được, và đó cũng là một bẫy cấu hình kinh điển.

Để đơn giản, Lab 7.1 → 7.4 chạy trên **cluster 1 node** (`docker-compose.single.yml`) thay vì cluster 3 node: bảo mật cần sinh chứng chỉ cho từng broker, một node đủ để học đúng cơ chế mà không phải tạo 3 bộ keystore.

```bash
export KAFKA_CTR=kafka
export KAFKA_BS=localhost:9092
```

---

## Lab 7.1 — TLS: CA riêng, keystore/truststore, và bẫy hostname verification ⭐

**🎯 Mục tiêu:** Tự tay dựng một CA, ký chứng chỉ cho broker, bật listener `SSL://:9095`, kết nối được bằng cả CLI lẫn `kafkajs` — rồi **cố tình tái hiện lỗi hostname verification** và sửa đúng cách.
**🧩 Luyện kỹ năng (liên quan đề):**

- Phân biệt **keystore** (tôi là ai) và **truststore** (tôi tin ai) — câu hỏi "client cần gì để chỉ mã hoá" hỏi thẳng cặp này.
- `ssl.endpoint.identification.algorithm=https` bật mặc định từ Kafka 2.0 và đòi **SAN**, không phải `CN`.
- Vì sao tắt xác thực hostname là cách sửa **sai**.

**⏱️ ~45 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Sinh CA và bộ keystore/truststore cho broker. Chú ý `-ext SAN=...` phải có **ngay từ lúc tạo CSR**.

   ```bash
   cd ~/kafka-labs/week-07/certs
   export PW=labpass123

   # 1) CA tự ký
   openssl req -new -x509 -keyout ca.key -out ca.crt -days 365 -nodes \
     -subj "/CN=kafka-lab-ca/OU=Lab/O=Study/C=VN"

   # 2) Keystore của broker + CSR có SAN (localhost cho host, kafka cho docker network)
   keytool -genkeypair -alias kafka -keyalg RSA -keysize 2048 -validity 365 \
     -keystore kafka.server.keystore.p12 -storetype pkcs12 \
     -storepass "$PW" -keypass "$PW" \
     -dname "CN=localhost,OU=Lab,O=Study,C=VN" \
     -ext "SAN=DNS:localhost,DNS:kafka,IP:127.0.0.1"

   keytool -certreq -alias kafka -keystore kafka.server.keystore.p12 \
     -storepass "$PW" -file kafka.csr \
     -ext "SAN=DNS:localhost,DNS:kafka,IP:127.0.0.1"

   # 3) CA ký CSR — BẮT BUỘC giữ lại SAN bằng -copy_extensions copyall
   openssl x509 -req -CA ca.crt -CAkey ca.key -in kafka.csr -out kafka-signed.crt \
     -days 365 -CAcreateserial -copy_extensions copyall

   # 4) Nạp CA + cert đã ký vào keystore
   keytool -importcert -alias CARoot -file ca.crt -keystore kafka.server.keystore.p12 \
     -storepass "$PW" -noprompt
   keytool -importcert -alias kafka -file kafka-signed.crt -keystore kafka.server.keystore.p12 \
     -storepass "$PW" -noprompt

   # 5) Truststore: chỉ cần CA
   keytool -importcert -alias CARoot -file ca.crt \
     -keystore kafka.client.truststore.p12 -storetype pkcs12 \
     -storepass "$PW" -noprompt

   # Kiểm tra SAN đã nằm trong cert
   openssl x509 -in kafka-signed.crt -noout -text | grep -A1 "Subject Alternative Name"
   ```
2. Tạo file override thêm listener `SSL://:9095`.

   ```yaml
   # ~/kafka-labs/docker-compose.tls.yml
   services:
     kafka:
       ports:
         - "9095:9095"
       environment:
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9092,SSL://:9095,CONTROLLER://:9093
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:19092,PLAINTEXT_HOST://localhost:9092,SSL://localhost:9095
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SSL:SSL
         KAFKA_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka.server.keystore.p12
         KAFKA_SSL_KEYSTORE_PASSWORD: labpass123
         KAFKA_SSL_KEY_PASSWORD: labpass123
         KAFKA_SSL_KEYSTORE_TYPE: PKCS12
         KAFKA_SSL_TRUSTSTORE_LOCATION: /etc/kafka/secrets/kafka.client.truststore.p12
         KAFKA_SSL_TRUSTSTORE_PASSWORD: labpass123
         KAFKA_SSL_TRUSTSTORE_TYPE: PKCS12
         KAFKA_SSL_CLIENT_AUTH: none            # Lab 7.1 chỉ mã hoá; mTLS ở bước 6
       volumes:
         - ./week-07/certs:/etc/kafka/secrets:ro
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.single.yml -f docker-compose.tls.yml up -d
   docker compose -f docker-compose.single.yml -f docker-compose.tls.yml logs kafka | grep -iE "SSL|started"
   ```
3. Kết nối bằng CLI qua listener SSL.

   ```bash
   cat > ~/kafka-labs/week-07/client-ssl.properties <<'EOF'
   security.protocol=SSL
   ssl.truststore.location=/etc/kafka/secrets/kafka.client.truststore.p12
   ssl.truststore.password=labpass123
   ssl.truststore.type=PKCS12
   EOF
   docker cp ~/kafka-labs/week-07/client-ssl.properties kafka:/tmp/client-ssl.properties

   docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
     --bootstrap-server localhost:9095 --command-config /tmp/client-ssl.properties \
     --create --topic secure-orders --partitions 3 --replication-factor 1
   ```
4. Kết nối bằng `kafkajs` từ host (dùng `ca.crt` dạng PEM, không cần truststore).

   ```javascript
   // ~/kafka-labs/week-07/tls-producer.mjs
   import fs from "node:fs";
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w7-tls",
     brokers: ["localhost:9095"],
     ssl: { ca: [fs.readFileSync("certs/ca.crt", "utf-8")] },
     logLevel: logLevel.NOTHING,
   });

   const producer = kafka.producer();
   await producer.connect();
   await producer.send({
     topic: "secure-orders",
     messages: [{ key: "c1", value: JSON.stringify({ id: 1, total: 250 }) }],
   });
   console.log("Gửi qua TLS thành công");
   await producer.disconnect();
   ```

   ```bash
   cd ~/kafka-labs/week-07 && node tls-producer.mjs
   ```
5. **Tái hiện lỗi hostname verification**: kết nối bằng `127.0.0.1` thay vì `localhost` sau khi đã bỏ `IP:127.0.0.1` khỏi SAN, hoặc nhanh hơn là dựng một cert chỉ có `CN` mà không có SAN.

   ```bash
   # Cách nhanh: cert phụ chỉ có CN, không SAN
   keytool -genkeypair -alias nosan -keyalg RSA -keysize 2048 -validity 365 \
     -keystore nosan.p12 -storetype pkcs12 -storepass "$PW" -keypass "$PW" \
     -dname "CN=localhost,OU=Lab,O=Study,C=VN"
   # Thay KAFKA_SSL_KEYSTORE_LOCATION sang nosan.p12, restart, rồi chạy lại bước 4
   ```

   Lỗi mong đợi:

   ```
   javax.net.ssl.SSLHandshakeException: No subject alternative names present
   ```
6. **Sửa đúng cách** (cấp lại cert có SAN — quay lại bước 1) và **sửa sai cách** để biết vì sao không nên:

   ```properties
   # KHÔNG dùng ở production — chỉ để thấy nó "chạy được"
   ssl.endpoint.identification.algorithm=
   ```
7. (Mở rộng) Bật **mTLS**: đổi `KAFKA_SSL_CLIENT_AUTH: required`, sinh thêm keystore cho client, thêm `ssl.principal.mapping.rules` để principal thành `User:<CN>`.

   ```yaml
   KAFKA_SSL_CLIENT_AUTH: required
   KAFKA_SSL_PRINCIPAL_MAPPING_RULES: "RULE:^CN=(.*?),.*$/$1/,DEFAULT"
   ```

### ✅ Kiểm chứng

- Bước 1: lệnh `openssl x509 ... | grep -A1 "Subject Alternative Name"` **phải in ra** `DNS:localhost, DNS:kafka, IP Address:127.0.0.1`. Nếu trống thì `-copy_extensions copyall` đã bị bỏ sót và các bước sau sẽ thất bại.
- Bước 3 và 4 đều gửi/nhận được qua cổng 9095; bỏ `ssl` khỏi cấu hình `kafkajs` thì kết nối treo rồi timeout.
- Bước 5 cho đúng ngoại lệ về subject alternative name; bước 6 với thuật toán rỗng thì chạy được — đó chính là lý do đáp án "tắt xác thực hostname" luôn là bẫy.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
docker compose -f docker-compose.single.yml -f docker-compose.tls.yml down
# GIỮ thư mục week-07/certs cho Lab 7.2 (SASL_SSL dùng lại chính bộ keystore này)
```

### 🧠 Ý nghĩa với đề thi

- Chỉ mã hoá → client cần **`security.protocol=SSL` + truststore**. Thêm mTLS mới cần **keystore** phía client.
- `ssl.client.auth`: `none` (mặc định) · `requested` (client không có cert **vẫn vào được** → an toàn giả) · `required` (mTLS thật).
- Với mTLS, principal mặc định là **toàn bộ DN**; ACL viết theo `User:orders-service` sẽ không khớp nếu thiếu `ssl.principal.mapping.rules`.

---

## Lab 7.2 — SASL/SCRAM trên `SASL_SSL` ⭐

**🎯 Mục tiêu:** Tạo user `alice` bằng SCRAM-SHA-512 **lúc cluster đang chạy**, kết nối qua listener `SASL_SSL://:9097`, và tái hiện hai ngoại lệ dễ nhầm lẫn.
**🧩 Luyện kỹ năng (liên quan đề):**

- SCRAM lưu credential **salted + hashed trong metadata log**, đổi được lúc chạy — khác hẳn PLAIN.
- `sasl.jaas.config` inline thay cho file JAAS tĩnh.
- Phân biệt `UnsupportedSaslMechanismException` (sai mechanism) và `SaslAuthenticationException` (sai mật khẩu).

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 7.1 (bộ chứng chỉ trong `week-07/certs`).

### Các bước

1. Thêm listener `SASL_SSL://:9097` vào file override.

   ```yaml
   # ~/kafka-labs/docker-compose.sasl.yml
   services:
     kafka:
       ports:
         - "9095:9095"
         - "9097:9097"
       environment:
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9092,SSL://:9095,SASL_SSL://:9097,CONTROLLER://:9093
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:19092,PLAINTEXT_HOST://localhost:9092,SSL://localhost:9095,SASL_SSL://localhost:9097
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SSL:SSL,SASL_SSL:SASL_SSL
         KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
         KAFKA_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka.server.keystore.p12
         KAFKA_SSL_KEYSTORE_PASSWORD: labpass123
         KAFKA_SSL_KEY_PASSWORD: labpass123
         KAFKA_SSL_KEYSTORE_TYPE: PKCS12
         KAFKA_SSL_TRUSTSTORE_LOCATION: /etc/kafka/secrets/kafka.client.truststore.p12
         KAFKA_SSL_TRUSTSTORE_PASSWORD: labpass123
         KAFKA_SSL_TRUSTSTORE_TYPE: PKCS12
       volumes:
         - ./week-07/certs:/etc/kafka/secrets:ro
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.single.yml -f docker-compose.sasl.yml up -d
   ```
2. Tạo credential SCRAM cho `alice` **qua listener PLAINTEXT nội bộ** (cluster đang chạy, không cần restart).

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
     --bootstrap-server localhost:9092 --alter \
     --add-config 'SCRAM-SHA-512=[iterations=8192,password=alice-secret]' \
     --entity-type users --entity-name alice

   docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
     --bootstrap-server localhost:9092 --describe --entity-type users --entity-name alice
   ```

   > 📌 Cách thứ hai, dùng khi cần user **trước khi** cluster khởi động lần đầu:
   > `kafka-storage.sh format --add-scram 'SCRAM-SHA-512=[name=admin,password=admin-secret]' ...`
3. Kết nối bằng CLI với `sasl.jaas.config` inline.

   ```bash
   cat > ~/kafka-labs/week-07/client-sasl.properties <<'EOF'
   security.protocol=SASL_SSL
   sasl.mechanism=SCRAM-SHA-512
   sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="alice" password="alice-secret";
   ssl.truststore.location=/etc/kafka/secrets/kafka.client.truststore.p12
   ssl.truststore.password=labpass123
   ssl.truststore.type=PKCS12
   EOF
   docker cp ~/kafka-labs/week-07/client-sasl.properties kafka:/tmp/client-sasl.properties

   docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
     --bootstrap-server localhost:9097 --command-config /tmp/client-sasl.properties --list
   ```
4. Kết nối bằng `kafkajs`.

   ```javascript
   // ~/kafka-labs/week-07/sasl-producer.mjs
   import fs from "node:fs";
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w7-sasl",
     brokers: ["localhost:9097"],
     ssl: { ca: [fs.readFileSync("certs/ca.crt", "utf-8")] },
     sasl: { mechanism: "scram-sha-512", username: "alice", password: "alice-secret" },
     logLevel: logLevel.NOTHING,
   });

   const producer = kafka.producer();
   await producer.connect();
   await producer.send({ topic: "secure-orders", messages: [{ key: "c2", value: "hello-sasl" }] });
   console.log("Gửi qua SASL_SSL thành công");
   await producer.disconnect();
   ```
5. **Tái hiện 2 lỗi.** Đổi từng thứ một rồi chạy lại bước 4.

   ```javascript
   // (a) sai mật khẩu → SaslAuthenticationException
   sasl: { mechanism: "scram-sha-512", username: "alice", password: "sai-mat-khau" }

   // (b) sai mechanism (broker chỉ bật SCRAM-SHA-512) → lỗi thương lượng mechanism
   sasl: { mechanism: "scram-sha-256", username: "alice", password: "alice-secret" }
   ```
6. Xoá và tạo lại credential để thấy nó có hiệu lực ngay, không cần restart.

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
     --bootstrap-server localhost:9092 --alter \
     --delete-config 'SCRAM-SHA-512' --entity-type users --entity-name alice
   node sasl-producer.mjs    # thất bại ngay lập tức
   ```

### ✅ Kiểm chứng

- Bước 2: `--describe` in ra `SCRAM-SHA-512=salt=...,stored_key=...` — **không có mật khẩu dạng rõ**.
- Bước 5a báo lỗi xác thực (sai credential); bước 5b báo lỗi **mechanism không được hỗ trợ**. Hai lỗi khác nhau tuy nhìn thoáng qua rất giống.
- Bước 6 chứng minh credential quản lý **lúc chạy**: xoá xong là client hỏng ngay, không cần khởi động lại broker.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
docker compose -f docker-compose.single.yml -f docker-compose.sasl.yml down
# GIỮ certs + compose file cho Lab 7.3
```

### 🧠 Ý nghĩa với đề thi

- Yêu cầu "thêm/xoay/thu hồi user **không restart broker**, không lưu mật khẩu dạng rõ" → **SCRAM**, không bao giờ là PLAIN.
- PLAIN chỉ chấp nhận được **trên `SASL_SSL`**; trên `SASL_PLAINTEXT` thì mật khẩu đi trần trên mạng.
- `sasl.mechanism` của client **phải nằm trong** `sasl.enabled.mechanisms` của listener, nếu không thì thất bại ngay ở bước thương lượng.

---

## Lab 7.3 — ACL với `StandardAuthorizer` ⭐

**🎯 Mục tiêu:** Bật authorization, tự tay gặp `TopicAuthorizationException` và `GroupAuthorizationException`, rồi cấp quyền tối thiểu bằng hai cờ tiện lợi `--producer` / `--consumer`.
**🧩 Luyện kỹ năng (liên quan đề):**

- `--producer` mở rộng thành **Write + Describe + Create**; `--consumer --group` thêm **Read trên Group**.
- Pattern **PREFIXED** cho topic sinh động.
- **Deny thắng Allow**, và `allow.everyone.if.no.acl.found` chỉ nới cho resource **chưa có ACL nào**.

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 7.2 (user `alice` và listener SASL_SSL).

### Các bước

1. Bổ sung authorizer vào file override của Lab 7.2 (thêm 3 biến, giữ nguyên phần còn lại).

   ```yaml
   KAFKA_AUTHORIZER_CLASS_NAME: org.apache.kafka.metadata.authorizer.StandardAuthorizer
   KAFKA_SUPER_USERS: "User:ANONYMOUS"     # listener PLAINTEXT nội bộ = admin của lab
   KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: "false"
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.single.yml -f docker-compose.sasl.yml up -d
   ```
2. Tạo lại credential cho alice (nếu đã xoá ở Lab 7.2 bước 6) rồi thử produce — **phải bị từ chối**.

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
     --bootstrap-server localhost:9092 --alter \
     --add-config 'SCRAM-SHA-512=[password=alice-secret]' \
     --entity-type users --entity-name alice

   docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
     --bootstrap-server localhost:9092 --create --topic orders --partitions 3 --replication-factor 1

   cd week-07 && node sasl-producer.mjs      # đổi topic thành "orders" trước khi chạy
   # → TopicAuthorizationException / Not authorized to access topics: [orders]
   ```
3. Cấp quyền **producer** tối thiểu.

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 \
     --add --allow-principal User:alice --producer --topic orders
   docker exec -it kafka /opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 --list --topic orders
   ```
4. Thử **consume** — lần này lỗi chuyển sang nhóm.

   ```javascript
   // ~/kafka-labs/week-07/sasl-consumer.mjs  (rút gọn: cùng cấu hình Kafka như sasl-producer.mjs)
   const consumer = kafka.consumer({ groupId: "billing" });
   await consumer.connect();
   await consumer.subscribe({ topic: "orders", fromBeginning: true });
   await consumer.run({ eachMessage: async ({ message }) => console.log(message.value.toString()) });
   ```

   ```bash
   node sasl-consumer.mjs
   # → GroupAuthorizationException: Not authorized to access group: billing
   ```
5. Cấp quyền **consumer** kèm group.

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 \
     --add --allow-principal User:alice --consumer --topic orders --group billing
   node sasl-consumer.mjs      # chạy được
   ```
6. **PREFIXED** cho nhóm topic sinh động.

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 \
     --add --allow-principal User:alice --producer \
     --topic orders- --resource-pattern-type prefixed

   docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 \
     --create --topic orders-eu --partitions 1 --replication-factor 1
   # produce vào orders-eu → thành công mà không cần ACL riêng
   ```
7. **Deny thắng Allow.**

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 \
     --add --deny-principal User:alice --operation Write --topic orders-eu
   # produce lại vào orders-eu → bị từ chối, dù ACL prefixed vẫn còn
   docker exec -it kafka /opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 --list
   ```

### ✅ Kiểm chứng

- Bước 2 và bước 4 cho **hai ngoại lệ khác nhau**: một về Topic, một về Group. Đọc tên ngoại lệ là biết thiếu ACL trên resource nào.
- `--list` ở bước 3 hiển thị đúng **ba** operation cho cờ `--producer`: `WRITE`, `DESCRIBE`, `CREATE`.
- Bước 7: Deny có hiệu lực ngay cả khi tồn tại một Allow khớp rộng hơn.

### 🧹 Dọn dẹp

```bash
docker exec -it kafka /opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 \
  --remove --allow-principal User:alice --producer --topic orders --force
docker exec -it kafka /opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 --list
# GIỮ cluster cho Lab 7.4
```

### 🧠 Ý nghĩa với đề thi

- Nhớ hai phép mở rộng: `--producer` = **Write + Describe + Create**; `--consumer --group g` = **Read + Describe** trên topic **cộng Read** trên group.
- Producer transactional cần thêm **Write trên `TransactionalId`**; producer idempotent trên broker cũ hơn 2.8 cần **IdempotentWrite trên Cluster**.
- Thứ tự đánh giá **Deny → Allow → mặc định từ chối**, giống hệt logic IAM bạn đã quen từ `SAA-C03`.

---

## Lab 7.4 — Quota băng thông cho producer

**🎯 Mục tiêu:** Đặt `producer_byte_rate` cho `alice`, đo throughput thực tế bị kìm về đúng hạn mức, và thấy rằng client **không nhận lỗi nào**.
**🧩 Luyện kỹ năng (liên quan đề):**

- Cơ chế throttle = broker **trì hoãn response**, không ném ngoại lệ.
- Metric `produce-throttle-time-avg` là dấu vết duy nhất phía client.
- Quota là **per-broker**, không phải tổng toàn cluster.

**⏱️ ~25 phút** · **Yêu cầu trước:** Lab 7.3 (cluster + alice).

### Các bước

1. Đo throughput **trước khi** có quota.

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic orders --num-records 20000 --record-size 1000 --throughput -1 \
     --producer.config /tmp/client-sasl.properties \
     --producer-props bootstrap.servers=localhost:9097
   ```
2. Đặt quota **100 KB/s** cho alice.

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
     --bootstrap-server localhost:9092 --alter \
     --add-config 'producer_byte_rate=102400' \
     --entity-type users --entity-name alice

   docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
     --bootstrap-server localhost:9092 --describe --entity-type users --entity-name alice
   ```
3. Chạy lại đúng lệnh ở bước 1 và so sánh.
4. Thử mức ưu tiên: thêm quota riêng cho cặp `(user, client-id)` và xem nó thắng quota mức user.

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
     --bootstrap-server localhost:9092 --alter \
     --add-config 'producer_byte_rate=10485760' \
     --entity-type users --entity-name alice \
     --entity-type clients --entity-name perf-producer
   ```
5. Gỡ quota và xác nhận throughput trở lại bình thường.

   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-configs.sh \
     --bootstrap-server localhost:9092 --alter \
     --delete-config 'producer_byte_rate' --entity-type users --entity-name alice
   ```

### ✅ Kiểm chứng

- Bước 3 cho throughput tụt về xấp xỉ **100 KB/s** (khoảng 100 record/giây với bản ghi 1 KB), và dòng tổng kết của công cụ in **`avg throttle time`** lớn hơn 0.
- **Không có ngoại lệ nào** xuất hiện — đây là điểm mấu chốt: quota làm chậm chứ không làm hỏng.
- Bước 4: với `client.id=perf-producer`, hạn mức áp dụng là 10 MB/s chứ không phải 100 KB/s.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
docker compose -f docker-compose.single.yml -f docker-compose.sasl.yml down
```

### 🧠 Ý nghĩa với đề thi

- Triệu chứng "throughput bị chặn trần mà log sạch bong" → nghĩ ngay tới **quota**, kiểm tra `produce-throttle-time-avg` / `fetch-throttle-time-avg`.
- Thứ tự ưu tiên từ hẹp tới rộng: `(user, client-id)` → `user` → `client-id` → các mức mặc định.
- Quota tính **trên từng broker**, nên trần thực tế của một client bằng hạn mức nhân số broker nó ghi vào.

---

## Lab 7.5 — Unit test với `MockProducer` và `MockConsumer` ⭐

**🎯 Mục tiêu:** Viết hai test chạy trong **mili giây, không cần broker**: một test xác nhận producer định tuyến lỗi sang nhánh dead-letter, một test xác nhận consumer commit đúng offset.
**🧩 Luyện kỹ năng (liên quan đề):**

- `history()` ghi lại mọi record đã gửi; `errorNext()` hoàn thành future kế tiếp **bằng lỗi**, không ném từ `send()`.
- Công thức ba bước của `MockConsumer`: **assign → updateBeginningOffsets → addRecord**.
- Quy tắc **commit = offset cuối + 1**.

**⏱️ ~35 phút** · **Yêu cầu trước:** Java 17+ và Gradle.

### Các bước

1. Dựng project.

   ```bash
   mkdir -p ~/kafka-labs/week-07/gradle-tests/src/test/java/lab
   cd ~/kafka-labs/week-07/gradle-tests
   ```

   ```kotlin
   // build.gradle.kts
   plugins { java }
   repositories { mavenCentral() }
   dependencies {
       testImplementation("org.apache.kafka:kafka-clients:4.3.1")
       testImplementation("org.junit.jupiter:junit-jupiter:5.11.3")
       testRuntimeOnly("org.junit.platform:junit-platform-launcher")
   }
   java { toolchain { languageVersion = JavaLanguageVersion.of(17) } }
   tasks.test { useJUnitPlatform(); testLogging { showStandardStreams = true } }
   ```
2. Test `MockProducer`: xác nhận record được gửi đúng và lỗi được định tuyến sang DLQ.

   ```java
   // src/test/java/lab/MockProducerTest.java
   package lab;

   import org.apache.kafka.clients.producer.*;
   import org.apache.kafka.common.errors.TimeoutException;
   import org.apache.kafka.common.serialization.StringSerializer;
   import org.junit.jupiter.api.Test;

   import java.util.concurrent.atomic.AtomicReference;

   import static org.junit.jupiter.api.Assertions.*;

   class MockProducerTest {

       /** Code under test: gửi record, lỗi thì đẩy sang nhánh dead-letter. */
       static void publish(Producer<String, String> producer, String key, String value,
                           AtomicReference<String> deadLetter) {
           ProducerRecord<String, String> record = new ProducerRecord<>("orders", key, value);
           record.headers().add("source", "lab7".getBytes());
           producer.send(record, (metadata, exception) -> {
               if (exception != null) deadLetter.set(key);
           });
       }

       @Test
       void ghi_lai_dung_record_da_gui() {
           MockProducer<String, String> producer =
                   new MockProducer<>(true, new StringSerializer(), new StringSerializer());
           AtomicReference<String> dlq = new AtomicReference<>();

           publish(producer, "c1", "{\"total\":250}", dlq);

           assertEquals(1, producer.history().size());
           ProducerRecord<String, String> sent = producer.history().get(0);
           assertEquals("orders", sent.topic());
           assertEquals("c1", sent.key());
           assertEquals("lab7", new String(sent.headers().lastHeader("source").value()));
           assertNull(dlq.get(), "không có lỗi thì không được chạm vào DLQ");
       }

       @Test
       void loi_gui_duoc_dinh_tuyen_sang_dlq() {
           // autoComplete=false → future chỉ hoàn thành khi ta chủ động gọi
           MockProducer<String, String> producer =
                   new MockProducer<>(false, new StringSerializer(), new StringSerializer());
           AtomicReference<String> dlq = new AtomicReference<>();

           publish(producer, "c2", "{\"total\":900}", dlq);
           assertNull(dlq.get(), "trước errorNext callback chưa chạy");

           producer.errorNext(new TimeoutException("broker không phản hồi"));

           assertEquals("c2", dlq.get());
           assertEquals(1, producer.history().size(), "history giữ record kể cả khi gửi lỗi");
       }
   }
   ```
3. Test `MockConsumer`: xác nhận commit đúng `offset + 1`.

   ```java
   // src/test/java/lab/MockConsumerTest.java
   package lab;

   import org.apache.kafka.clients.consumer.*;
   import org.apache.kafka.common.TopicPartition;
   import org.junit.jupiter.api.Test;

   import java.time.Duration;
   import java.util.*;

   import static org.junit.jupiter.api.Assertions.assertEquals;

   class MockConsumerTest {

       /** Code under test: xử lý hết batch rồi commit offset cuối + 1. */
       static int processAndCommit(Consumer<String, String> consumer, List<String> sink) {
           ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
           Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
           for (ConsumerRecord<String, String> r : records) {
               sink.add(r.value());
               offsets.put(new TopicPartition(r.topic(), r.partition()),
                           new OffsetAndMetadata(r.offset() + 1));   // +1 là điểm mấu chốt
           }
           if (!offsets.isEmpty()) consumer.commitSync(offsets);
           return records.count();
       }

       @Test
       void commit_offset_cuoi_cong_mot() {
           MockConsumer<String, String> consumer = new MockConsumer<>("earliest");
           TopicPartition tp = new TopicPartition("orders", 0);

           // Ba bước bắt buộc — thiếu bước nào cũng ném IllegalStateException
           consumer.assign(List.of(tp));
           consumer.updateBeginningOffsets(Map.of(tp, 0L));
           consumer.addRecord(new ConsumerRecord<>("orders", 0, 0L, "c1", "v1"));
           consumer.addRecord(new ConsumerRecord<>("orders", 0, 1L, "c2", "v2"));

           List<String> sink = new ArrayList<>();
           int count = processAndCommit(consumer, sink);

           assertEquals(2, count);
           assertEquals(List.of("v1", "v2"), sink);
           assertEquals(2L, consumer.committed(Set.of(tp)).get(tp).offset(),
                        "record cuối có offset 1 → phải commit 2");
       }
   }
   ```
4. Chạy test.

   ```bash
   gradle test --console=plain
   ```

### ✅ Kiểm chứng

- Cả ba test xanh. Thử **cố tình phá** để thấy test có ý nghĩa:
  - Bỏ `+ 1` trong `processAndCommit` → test cuối đỏ với thông báo mong đợi 2 nhưng nhận 1.
  - Đổi `new MockProducer<>(false, ...)` thành `true` ở test thứ hai → `errorNext` không còn future nào đang chờ và DLQ vẫn rỗng.
  - Bỏ dòng `updateBeginningOffsets` → `IllegalStateException`.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs/week-07/gradle-tests && gradle clean
```

### 🧠 Ý nghĩa với đề thi

- `MockProducer` nằm ngay trong `kafka-clients`, **không cần** thư viện test riêng, và hỗ trợ cả API transaction.
- `errorNext(e)` **không** làm `send()` ném lỗi; nó hoàn thành future kế tiếp bằng ngoại lệ, đúng như broker trả lỗi bất đồng bộ.
- Khi assertion là "ứng dụng đã quyết định gửi cái gì", hãy khẳng định trên `history()` thay vì đọc ngược từ một broker thật.

---

## Lab 7.6 — Integration test với Testcontainers

**🎯 Mục tiêu:** Chạy một broker **thật** trong test, produce rồi consume, để thấy ranh giới giữa mock và integration test.
**🧩 Luyện kỹ năng (liên quan đề):**

- Khi nào bắt buộc dùng broker thật: rebalance, transaction, `read_committed`, ACL/TLS.
- `getBootstrapServers()` trả về địa chỉ với cổng ngẫu nhiên.

**⏱️ ~25 phút** · **Yêu cầu trước:** Lab 7.5 (project Gradle) và Docker đang chạy.

### Các bước

1. Thêm dependency.

   ```kotlin
   // build.gradle.kts — thêm vào khối dependencies
   testImplementation("org.testcontainers:testcontainers-kafka:2.0.5")
   testImplementation("org.testcontainers:junit-jupiter:1.20.4")
   ```
2. Viết test.

   ```java
   // src/test/java/lab/KafkaContainerIT.java
   package lab;

   import org.apache.kafka.clients.consumer.*;
   import org.apache.kafka.clients.producer.*;
   import org.apache.kafka.common.serialization.*;
   import org.junit.jupiter.api.Test;
   import org.testcontainers.junit.jupiter.Container;
   import org.testcontainers.junit.jupiter.Testcontainers;
   import org.testcontainers.kafka.KafkaContainer;
   import org.testcontainers.utility.DockerImageName;

   import java.time.Duration;
   import java.util.*;

   import static org.junit.jupiter.api.Assertions.assertEquals;

   @Testcontainers
   class KafkaContainerIT {

       @Container
       static KafkaContainer kafka =
               new KafkaContainer(DockerImageName.parse("apache/kafka:4.3.1"));

       @Test
       void produce_roi_consume_tren_broker_that() {
           Map<String, Object> common = Map.of("bootstrap.servers", kafka.getBootstrapServers());

           Properties p = new Properties();
           p.putAll(common);
           p.put("key.serializer", StringSerializer.class.getName());
           p.put("value.serializer", StringSerializer.class.getName());
           try (Producer<String, String> producer = new KafkaProducer<>(p)) {
               producer.send(new ProducerRecord<>("it-orders", "c1", "hello")).get();
           } catch (Exception e) {
               throw new RuntimeException(e);
           }

           Properties c = new Properties();
           c.putAll(common);
           c.put("key.deserializer", StringDeserializer.class.getName());
           c.put("value.deserializer", StringDeserializer.class.getName());
           c.put("group.id", "it-group");
           c.put("auto.offset.reset", "earliest");
           try (Consumer<String, String> consumer = new KafkaConsumer<>(c)) {
               consumer.subscribe(List.of("it-orders"));
               ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(10));
               assertEquals(1, records.count());
               assertEquals("hello", records.iterator().next().value());
           }
       }
   }
   ```
3. Chạy.

   ```bash
   gradle test --tests '*KafkaContainerIT' --console=plain
   ```

### ✅ Kiểm chứng

- Lần chạy đầu mất vài chục giây vì phải kéo image; các lần sau nhanh hơn nhưng vẫn **chậm hơn hẳn** Lab 7.5 — đó chính là lý do không dùng Testcontainers cho mọi test.
- `docker ps` trong lúc test chạy cho thấy một container Kafka tạm với cổng ngẫu nhiên; nó tự bị xoá khi test kết thúc.

### 🧹 Dọn dẹp

```bash
gradle clean
docker ps -a | grep testcontainers    # phải rỗng; nếu còn thì docker rm -f <id>
```

### 🧠 Ý nghĩa với đề thi

- Ranh giới chọn công cụ: assertion **phụ thuộc hành vi broker** thì cần broker thật, ngược lại thì mock.
- `TopologyTestDriver` (Tuần 6) nằm giữa hai thái cực: chạy topology Streams thật nhưng vẫn trong tiến trình, không cần broker.

---

## Lab 7.7 — Contract test schema trong CI

**🎯 Mục tiêu:** Viết một script CI **chặn pull request** khi schema mới phá vỡ compatibility, mà **không đăng ký** version mới vào registry.
**🧩 Luyện kỹ năng (liên quan đề):**

- Phân biệt `POST /compatibility/...` (chỉ kiểm tra) và `POST /subjects/.../versions` (đăng ký thật).
- Ở mức `BACKWARD`, thêm field **không có default** là vi phạm.

**⏱️ ~25 phút** · **Yêu cầu trước:** Schema Registry từ [Tuần 5 — Lab 5.1](../week-05/labs.md).

### Các bước

1. Khởi động cluster và Schema Registry, đăng ký schema nền.

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.registry.yml up -d

   curl -s -X POST http://localhost:8081/subjects/orders-value/versions \
     -H "Content-Type: application/vnd.schemaregistry.v1+json" \
     -d '{"schema":"{\"type\":\"record\",\"name\":\"Order\",\"fields\":[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"total\",\"type\":\"double\"}]}"}'
   curl -s http://localhost:8081/config/orders-value ; echo
   ```
2. Viết script CI.

   ```bash
   # ~/kafka-labs/week-07/check-compat.sh
   #!/usr/bin/env bash
   set -euo pipefail
   SR=${SR:-http://localhost:8081}
   SUBJECT=$1
   SCHEMA_FILE=$2

   PAYLOAD=$(jq -Rs '{schema: .}' < "$SCHEMA_FILE")
   RESP=$(curl -s -X POST "$SR/compatibility/subjects/$SUBJECT/versions/latest" \
     -H "Content-Type: application/vnd.schemaregistry.v1+json" -d "$PAYLOAD")

   echo "Registry trả về: $RESP"
   if [ "$(echo "$RESP" | jq -r '.is_compatible // "error"')" != "true" ]; then
     echo "❌ Schema KHÔNG tương thích với $SUBJECT — chặn merge."
     exit 1
   fi
   echo "✅ Tương thích."
   ```

   ```bash
   chmod +x ~/kafka-labs/week-07/check-compat.sh
   ```
3. Thử **trường hợp hỏng**: thêm field bắt buộc, không default.

   ```bash
   cd ~/kafka-labs/week-07
   cat > bad.avsc <<'EOF'
   {"type":"record","name":"Order","fields":[
     {"name":"id","type":"string"},
     {"name":"total","type":"double"},
     {"name":"channel","type":"string"}
   ]}
   EOF
   ./check-compat.sh orders-value bad.avsc ; echo "exit=$?"
   ```
4. Thử **trường hợp hợp lệ**: cùng field nhưng có default.

   ```bash
   cat > good.avsc <<'EOF'
   {"type":"record","name":"Order","fields":[
     {"name":"id","type":"string"},
     {"name":"total","type":"double"},
     {"name":"channel","type":"string","default":"web"}
   ]}
   EOF
   ./check-compat.sh orders-value good.avsc ; echo "exit=$?"
   ```
5. Xác nhận registry **không** bị thêm version nào trong suốt quá trình.

   ```bash
   curl -s http://localhost:8081/subjects/orders-value/versions ; echo
   ```

### ✅ Kiểm chứng

- Bước 3 in `"is_compatible":false`, script thoát với mã **1** — đủ để CI đánh trượt pull request.
- Bước 4 in `"is_compatible":true`, thoát mã **0**.
- Bước 5 vẫn chỉ có `[1]`: endpoint compatibility **không đăng ký** gì cả. Đây là khác biệt cốt lõi so với gọi nhầm `/subjects/.../versions`.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml -f docker-compose.registry.yml down -v
rm -f week-07/bad.avsc week-07/good.avsc
```

### 🧠 Ý nghĩa với đề thi

- Câu hỏi "chặn PR khi schema không tương thích **mà không tạo version mới**" → luôn là endpoint **`/compatibility`**, hoặc goal `test-compatibility` của Maven plugin.
- Ở `BACKWARD`: **xoá field** và **thêm field có default** thì được; **thêm field không default** thì không.
- Mức compatibility lấy từ config của **subject**, chưa đặt thì rơi về config **global**.

---

> ✅ Xong 7 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist), rồi làm [bộ 30 câu luyện tập](questions.md) và **MINI-MOCK CONNECT + STREAMS + TEST**. Ngưỡng qua cổng sang Tuần 8: **≥ 70%**. Giữ lại `week-07/certs/` nếu bạn muốn thử lại TLS ở Capstone Tuần 10.
