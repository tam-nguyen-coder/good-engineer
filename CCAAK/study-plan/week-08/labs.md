# 🛠️ Capstone — Tuần 8: **Cluster Rescue** (vận hành, chẩn đoán, khôi phục) ⭐

> Đây **KHÔNG** phải các lab rời, cũng **KHÔNG** phải bài xây pipeline như capstone của CCDAK. Đây là **một ca trực**: bạn dựng một cluster production-like, ghi baseline, rồi lần lượt **bị phá 4 lần** và phải chẩn đoán + khôi phục theo playbook, cuối cùng **diễn tập DR**. Đề CCAAK hỏi *"người vận hành làm gì tiếp theo"* — bài này là chỗ duy nhất trong bộ tài liệu bạn thật sự phải trả lời câu đó dưới áp lực.
> ⚙️ **Yêu cầu chung:** `~/kafka-labs/` với `docker-compose.cluster.yml` (CCDAK [Tuần 1 — Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md)) và `docker-compose.monitoring.yml` (CCDAK [Tuần 8 — Lab 8.1](../../../CCDAK/study-plan/week-08/labs.md)); Docker Desktop với **~7 GB RAM trống**; `curl`, `jq`. Tổng **~3.5h** (chia 2 ngày như lịch trong [README](README.md): Bước 1–3 Ngày 2, Bước 4–7 Ngày 4).
> ⚠️ **Luật chơi:** mỗi bài phá, hãy **tự chẩn đoán trước** bằng đúng thứ tự **metric → log → config → hành động**. Chỉ mở phần *Chẩn đoán* sau khi bạn đã tự viết ra giả thuyết của mình. Bạn có thể nhờ người khác chạy khối *Gây sự cố* mà không cho bạn xem — cách đó gần thi thật nhất.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md)

---

## 🎯 Bạn sẽ vận hành cái gì

Một cluster nhỏ nhưng **có đủ mọi thứ khiến production khó**:

- **3 broker + 1 controller tách riêng** (KRaft), `broker.rack` = `rack-a/b/c`, RF 3 / `min.insync.replicas` 2.
- **Listener `SECURE` = SASL_SSL** (TLS bằng CA tự ký + SCRAM-SHA-512) với **`StandardAuthorizer`**, ACL tối thiểu cho hai service, **quota** băng thông cho tenant.
- **Broker `kafka-3` có 2 `log.dirs`**, trong đó một dir nằm trên tmpfs **32 MB** — để ổ đĩa có thể đầy thật.
- **Prometheus + Grafana** với **alert rule** cho 4 metric đèn đỏ.
- **Một broker thứ tư (`kafka-4`, node 5) chưa bật**, dùng cho bài phá "thêm broker nhưng không nhận traffic".
- **Cluster B 1 node** ở Bước 7 làm đích DR cho MirrorMaker 2.

### 🗺️ Sơ đồ

```
                    docker network kafka-labs_default
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │  controller (node 1, process.roles=controller)   __cluster_metadata           │
 │        ▲ quorum 1 voter · observer: 2,3,4(,5)                                 │
 │  ┌─────┴──────┐  ┌────────────┐  ┌────────────────────────────┐  ┌──────────┐ │
 │  │ kafka-1    │  │ kafka-2    │  │ kafka-3                    │  │ kafka-4  │ │
 │  │ node 2     │  │ node 3     │  │ node 4                     │  │ node 5   │ │
 │  │ rack-a     │  │ rack-b     │  │ rack-c                     │  │ rack-a   │ │
 │  │ :19092     │  │ :19092     │  │ :19092                     │  │ (profile │ │
 │  │ :29092 TLS │  │ :29092 TLS │  │ :29092 TLS                 │  │  scale)  │ │
 │  │ 1 log.dir  │  │ 1 log.dir  │  │ 2 log.dirs (data2 = 32 MB) │  │          │ │
 │  └────────────┘  └────────────┘  └────────────────────────────┘  └──────────┘ │
 │        │ JMX exporter :7071 (Tuần 8 CCDAK)                                    │
 │        ▼                                                                      │
 │  Prometheus :9090  ──alert rules──►  Grafana :3000                            │
 └───────────────────────────────────────────────────────────────────────────────┘
        ▲ PLAINTEXT (CLI, super user ANONYMOUS)    ▲ SASL_SSL (etl-svc, analytics — bị ACL + quota)

        Bước 7:  cluster A ──MirrorMaker 2──►  kafka-b (cluster B, 1 node, :9192)
```

### 📌 Mỗi bước ôn lại tuần / domain nào

| Bước | Nội dung | Ôn lại tuần | Domain CCAAK |
| --- | --- | --- | --- |
| **1** | Dựng cluster production-like: controller tách riêng, `broker.rack`, TLS + SCRAM + ACL, quota, alert | Tuần 1, 4, 5, 7 | FUND, ARCH, SEC, OBS |
| **2** | Sizing + baseline metric | Tuần 2, 3, 4, 7 | CFG, ARCH, OBS |
| **3** ⭐ | **Bài phá 1 — durability:** `min.insync.replicas=3` trên RF3 + mất 1 broker | Tuần 3, 7 | CFG, FUND, TROUBLE |
| **4** ⭐ | **Bài phá 2 — storage:** một `log.dirs` đầy → `KafkaStorageException` | Tuần 2, 7 | CFG, TROUBLE |
| **5** ⭐ | **Bài phá 3 — security:** ACL bị thu hồi nhầm | Tuần 5, 7 | SEC, TROUBLE |
| **6** ⭐ | **Bài phá 4 — cân bằng:** broker mới không nhận traffic → reassign + throttle | Tuần 4 | ARCH, CFG |
| **7** | **Diễn tập DR:** MirrorMaker 2 + dịch offset | Tuần 4, 6 | ARCH, CONNECT |

---

## 🔧 Chuẩn bị chung (làm 1 lần)

```bash
cd ~/kafka-labs
mkdir -p ~/kafka-labs/capstone/certs ~/kafka-labs/capstone/out ~/kafka-labs/capstone/mm2

# CLI chạy từ container `controller`: 3 broker sẽ có KAFKA_OPTS=-javaagent(:7071) và JMX_PORT
# → mọi JVM khởi động BÊN TRONG broker (kể cả docker exec kafka-1 kafka-topics.sh) cố bind lại 7071/9999
#   và chết với "Address already in use". Container `controller` cùng image, cùng network, không gắn agent.
export KAFKA_CTR=controller KAFKA_BS=kafka-1:19092

# Alias Tuần 1 (kt/kcp/kcc/kcg/kcfg/kq/ksh) đọc $KAFKA_CTR và $KAFKA_BS → tự trỏ đúng.
# Alias thêm cho capstone (tool chưa có alias):
alias krp='docker exec -i  $KAFKA_CTR /opt/kafka/bin/kafka-reassign-partitions.sh --bootstrap-server $KAFKA_BS'
alias kle='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-leader-election.sh   --bootstrap-server $KAFKA_BS'
alias kld='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-log-dirs.sh          --bootstrap-server $KAFKA_BS'
alias kacl='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-acls.sh             --bootstrap-server $KAFKA_BS'
alias koff='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-get-offsets.sh      --bootstrap-server $KAFKA_BS'
alias kperf='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh'
alias kfeat='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-features.sh        --bootstrap-server $KAFKA_BS'

# Hàm tiện ích
ktotal() { docker exec $KAFKA_CTR /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_BS --topic "$1" | awk -F: '{s+=$3} END {print s+0}'; }
urp()    { curl -s localhost:7071/metrics | grep -E '^kafka_server_replicamanager_underreplicatedpartitions' ; }
```

> 📌 **Không in lại compose gốc.** `docker-compose.cluster.yml` (controller node 1 + kafka-1/2/3 = node 2/3/4, host 9092/9094/9096, listener nội bộ `kafka-1:19092`) định nghĩa ở [CCDAK Tuần 1 — Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md); `docker-compose.monitoring.yml` (JMX Exporter :7071 + Prometheus :9090 + Grafana :3000) ở [CCDAK Tuần 8 — Lab 8.1](../../../CCDAK/study-plan/week-08/labs.md). Capstone chỉ thêm **một file override mới** (`docker-compose.capstone.yml`, Bước 1) và **một file cluster DR** (`docker-compose.capstone-dr.yml`, Bước 7).

> ⚠️ **Bắt đầu sạch.** Capstone đổi `log.dirs` của `kafka-3` và bật authorizer → phải format lại storage. Trước Bước 1:
>
> ```bash
> cd ~/kafka-labs && docker compose $(printf -- '-f %s ' docker-compose.*.yml) down -v --remove-orphans 2>/dev/null; docker ps -a | grep -E 'kafka|controller' || echo "sạch"
> ```

---

## Bước 1 — Dựng cluster production-like (controller tách riêng · rack · TLS + SCRAM + ACL · quota · alert)

**🎯 Mục tiêu:** Dựng lại toàn bộ những gì đã học Tuần 1–7 thành **một** cluster: controller tách riêng, 3 broker có `broker.rack`, listener `SECURE` chạy **SASL_SSL** (TLS bằng CA tự ký + SCRAM-SHA-512) với `StandardAuthorizer`, ACL tối thiểu cho `etl-svc` (ghi) và `analytics` (đọc + group), **quota** `producer_byte_rate` cho `etl-svc`, và Prometheus có **alert rule** cho 4 metric đèn đỏ.
**🧩 Luyện kỹ năng (liên quan đề):**

- `process.roles=controller` tách riêng; quorum; `broker.rack` ảnh hưởng replica placement.
- `listener.security.protocol.map` + `inter.broker.listener.name`; SASL_SSL vs SSL vs PLAINTEXT trên cùng cluster.
- SCRAM tạo **lúc chạy** bằng `kafka-configs.sh --entity-type users` (credential nằm trong metadata KRaft, không cần restart).
- `StandardAuthorizer`, `super.users`, `allow.everyone.if.no.acl.found=false`, ACL tối thiểu cho producer/consumer.
- Quota 4 loại và cách đặt theo user/client-id.

**⏱️ ~45 phút** · **Yêu cầu trước:** Chuẩn bị chung; mọi compose cũ đã `down -v`.

### Các bước

1. **Sinh chứng chỉ TLS** (CA tự ký + keystore cho từng broker + truststore dùng chung). Chỉ cần `keytool` có sẵn trong image Kafka.

   ```bash
   cat > ~/kafka-labs/capstone/make-certs.sh <<'EOF'
   #!/usr/bin/env bash
   set -euo pipefail
   cd /certs; PASS=capstone123
   # 1) CA tự ký
   keytool -genkeypair -alias ca -keyalg RSA -keysize 2048 -validity 365 \
     -dname "CN=capstone-ca,O=kafka-labs" -ext bc:c \
     -keystore ca.p12 -storetype PKCS12 -storepass $PASS -keypass $PASS
   keytool -exportcert -alias ca -keystore ca.p12 -storepass $PASS -rfc -file ca.crt
   # 2) Truststore dùng chung cho broker và client (chỉ chứa CA)
   keytool -importcert -noprompt -alias ca -file ca.crt \
     -keystore truststore.p12 -storetype PKCS12 -storepass $PASS
   # 3) Keystore cho từng node, SAN = hostname trong docker network
   for n in kafka-1 kafka-2 kafka-3 kafka-4; do
     keytool -genkeypair -alias "$n" -keyalg RSA -keysize 2048 -validity 365 \
       -dname "CN=$n,O=kafka-labs" -keystore "$n.p12" -storetype PKCS12 -storepass $PASS -keypass $PASS
     keytool -certreq  -alias "$n" -keystore "$n.p12" -storepass $PASS -file "$n.csr"
     keytool -gencert  -alias ca   -keystore ca.p12   -storepass $PASS \
       -infile "$n.csr" -outfile "$n.crt" -ext "san=dns:$n,dns:localhost,ip:127.0.0.1" -validity 365 -rfc
     keytool -importcert -noprompt -alias ca  -file ca.crt   -keystore "$n.p12" -storepass $PASS
     keytool -importcert -noprompt -alias "$n" -file "$n.crt" -keystore "$n.p12" -storepass $PASS
   done
   ls -1 *.p12 *.crt
   EOF
   docker run --rm -v ~/kafka-labs/capstone/certs:/certs \
     -v ~/kafka-labs/capstone/make-certs.sh:/make-certs.sh:ro \
     apache/kafka:4.3.1 bash /make-certs.sh
   ```

   Output mẫu (cuối cùng): `ca.p12  kafka-1.p12  kafka-2.p12  kafka-3.p12  kafka-4.p12  truststore.p12  ca.crt ...`
2. **Tạo file override** `~/kafka-labs/docker-compose.capstone.yml`. Nó **chỉ thêm** rack, listener `SECURE`, authorizer, log dir thứ hai cho `kafka-3`, và service `kafka-4` nằm trong profile `scale` (chưa chạy).

   ```yaml
   # ~/kafka-labs/docker-compose.capstone.yml — override cho Capstone Tuần 8 (CCAAK)
   # Chạy CHỒNG lên docker-compose.cluster.yml (Tuần 1) + docker-compose.monitoring.yml (Tuần 8 CCDAK).
   # Quy tắc env của image apache/kafka: KAFKA_ + tên property viết hoa, "." → "_", "_" → "__", "-" → "___".
   x-capstone-secure: &capstone-secure
     KAFKA_AUTHORIZER_CLASS_NAME: org.apache.kafka.metadata.authorizer.StandardAuthorizer  # KRaft; AclAuthorizer (ZK) đã gỡ ở 4.0
     KAFKA_SUPER_USERS: User:ANONYMOUS                       # client PLAINTEXT (inter-broker, CLI, JMX exporter) = super user
     KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: "false"           # mặc định đã là false — ghi rõ để nhớ: không ACL khớp → DENY
     KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
     KAFKA_LISTENER_NAME_SECURE_SCRAM___SHA___512_SASL_JAAS_CONFIG: org.apache.kafka.common.security.scram.ScramLoginModule required;
     KAFKA_SSL_KEYSTORE_TYPE: PKCS12
     KAFKA_SSL_TRUSTSTORE_TYPE: PKCS12
     KAFKA_SSL_TRUSTSTORE_LOCATION: /certs/truststore.p12
     KAFKA_SSL_TRUSTSTORE_PASSWORD: capstone123
     KAFKA_SSL_KEYSTORE_PASSWORD: capstone123
     KAFKA_SSL_KEY_PASSWORD: capstone123

   services:
     controller:
       volumes: ["./capstone/certs:/certs:ro"]               # controller chạy CLI secure ở Bước 5
       environment:
         KAFKA_AUTHORIZER_CLASS_NAME: org.apache.kafka.metadata.authorizer.StandardAuthorizer  # ACL lưu trong __cluster_metadata
         KAFKA_SUPER_USERS: User:ANONYMOUS

     kafka-1:
       volumes: ["./capstone/certs:/certs:ro"]
       environment:
         <<: *capstone-secure
         KAFKA_BROKER_RACK: rack-a
         KAFKA_SSL_KEYSTORE_LOCATION: /certs/kafka-1.p12
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9092,SECURE://:29092
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:19092,PLAINTEXT_HOST://localhost:9092,SECURE://kafka-1:29092
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SECURE:SASL_SSL

     kafka-2:
       volumes: ["./capstone/certs:/certs:ro"]
       environment:
         <<: *capstone-secure
         KAFKA_BROKER_RACK: rack-b
         KAFKA_SSL_KEYSTORE_LOCATION: /certs/kafka-2.p12
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9094,SECURE://:29092
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-2:19092,PLAINTEXT_HOST://localhost:9094,SECURE://kafka-2:29092
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SECURE:SASL_SSL

     kafka-3:
       volumes: ["./capstone/certs:/certs:ro"]
       tmpfs:
         - /var/lib/kafka/data2:size=32m                     # ổ đĩa "nhỏ" để Bước 4 làm đầy được thật
       environment:
         <<: *capstone-secure
         KAFKA_BROKER_RACK: rack-c
         KAFKA_SSL_KEYSTORE_LOCATION: /certs/kafka-3.p12
         KAFKA_LOG_DIRS: /tmp/kraft-combined-logs,/var/lib/kafka/data2    # JBOD 2 dir
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9096,SECURE://:29092
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-3:19092,PLAINTEXT_HOST://localhost:9096,SECURE://kafka-3:29092
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SECURE:SASL_SSL

     # Broker thứ tư — CHƯA chạy. Bước 6 bật bằng: docker compose --profile scale up -d kafka-4
     kafka-4:
       image: apache/kafka:4.3.1
       container_name: kafka-4
       hostname: kafka-4
       profiles: ["scale"]
       depends_on: [controller]
       ports: ["9098:9098"]
       volumes: ["./capstone/certs:/certs:ro"]
       environment:
         <<: *capstone-secure
         CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"                # PHẢI trùng cluster A, nếu không → InconsistentClusterId
         KAFKA_NODE_ID: 5
         KAFKA_PROCESS_ROLES: broker
         KAFKA_CONTROLLER_QUORUM_VOTERS: 1@controller:9093
         KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
         KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
         KAFKA_BROKER_RACK: rack-a
         KAFKA_SSL_KEYSTORE_LOCATION: /certs/kafka-4.p12
         KAFKA_DEFAULT_REPLICATION_FACTOR: 3
         KAFKA_MIN_INSYNC_REPLICAS: 2
         KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
         KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
         KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
         KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9098,SECURE://:29092
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-4:19092,PLAINTEXT_HOST://localhost:9098,SECURE://kafka-4:29092
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SECURE:SASL_SSL
   ```

   > ⚠️ Nếu broker không lên và log báo về `SASL mechanism SCRAM-SHA-512 ... JAAS configuration` (image không nhận mapping `___`), thay dòng `KAFKA_LISTENER_NAME_SECURE_...` bằng file JAAS: tạo `~/kafka-labs/capstone/kafka_server_jaas.conf` chứa `KafkaServer { org.apache.kafka.common.security.scram.ScramLoginModule required; };`, mount vào `/etc/kafka/jaas.conf` và thêm `-Djava.security.auth.login.config=/etc/kafka/jaas.conf` vào `KAFKA_OPTS`. Lưu ý `docker-compose.monitoring.yml` cũng dùng `KAFKA_OPTS` cho `-javaagent` → gộp **cả hai** flag vào **một** giá trị `KAFKA_OPTS`.
3. **Khởi động toàn bộ stack** (3 file compose).

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.monitoring.yml:docker-compose.capstone.yml
   docker compose up -d
   docker compose ps
   docker compose logs kafka-3 | grep -E "Kafka Server started|Loading logs from log dirs" | tail -3
   ```
4. **Kiểm tra sức khoẻ nền tảng:** quorum, rack, log dir.

   ```bash
   kq describe --status                 # LeaderId: 1, CurrentVoters: [1], CurrentObservers: [2,3,4]
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server $KAFKA_BS | grep -E "^kafka-[0-9]"
   kld --describe --broker-list 2,3,4 | jq -r '.brokers[] | "broker \(.broker) dirs: \([.logDirs[].logDir]|join(", "))"'
   ```
   Output mẫu:
   ```
   kafka-1:19092 (id: 2 rack: rack-a) -> (...)
   kafka-2:19092 (id: 3 rack: rack-b) -> (...)
   kafka-3:19092 (id: 4 rack: rack-c) -> (...)
   broker 2 dirs: /tmp/kraft-combined-logs
   broker 3 dirs: /tmp/kraft-combined-logs
   broker 4 dirs: /tmp/kraft-combined-logs, /var/lib/kafka/data2
   ```
5. **Tạo user SCRAM lúc chạy** (không restart broker) và **client properties** để dùng listener `SECURE`.

   ```bash
   kcfg --alter --entity-type users --entity-name etl-svc   --add-config 'SCRAM-SHA-512=[password=etl-pass-v1]'
   kcfg --alter --entity-type users --entity-name analytics --add-config 'SCRAM-SHA-512=[password=ana-pass-v1]'
   kcfg --describe --entity-type users                       # 2 dòng SCRAM-SHA-512=salt=...,iterations=4096

   for U in etl-svc:etl-pass-v1 analytics:ana-pass-v1; do
     N=${U%%:*}; P=${U##*:}
     cat > ~/kafka-labs/capstone/client-$N.properties <<EOF
   security.protocol=SASL_SSL
   ssl.truststore.location=/certs/truststore.p12
   ssl.truststore.type=PKCS12
   ssl.truststore.password=capstone123
   sasl.mechanism=SCRAM-SHA-512
   sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="$N" password="$P";
   EOF
   done
   docker cp ~/kafka-labs/capstone/client-etl-svc.properties   controller:/tmp/
   docker cp ~/kafka-labs/capstone/client-analytics.properties controller:/tmp/
   ```
6. **ACL tối thiểu** cho hai service, và **quota** cho `etl-svc`.

   ```bash
   # etl-svc: chỉ GHI vào orders (--producer thêm Write + Describe trên Topic)
   kacl --add --allow-principal User:etl-svc   --producer --topic orders
   # analytics: ĐỌC orders + group fulfillment (--consumer thêm Read+Describe Topic và Read Group)
   kacl --add --allow-principal User:analytics --consumer --topic orders --group fulfillment
   kacl --list --topic orders --group fulfillment

   # Quota băng thông: etl-svc tối đa 2 MB/s produce (đủ thấp để thấy throttle ở Bước 2)
   kcfg --alter --entity-type users --entity-name etl-svc --add-config 'producer_byte_rate=2097152'
   kcfg --describe --entity-type users --entity-name etl-svc
   ```
7. **Alert rule cho Prometheus.** Thêm 4 metric đèn đỏ vào cấu hình đã có từ CCDAK Tuần 8 (chỉ **thêm** `rule_files`, không viết lại `prometheus.yml`).

   ```bash
   cat > ~/kafka-labs/monitoring/alerts.yml <<'EOF'
   groups:
     - name: kafka-red-lights
       rules:
         - alert: UnderReplicatedPartitions          # redundancy suy giảm → ticket
           expr: sum(kafka_server_replicamanager_underreplicatedpartitions) > 0
           for: 2m
           labels: {severity: warning}
         - alert: OfflinePartitions                  # mất availability → gọi dậy
           expr: sum(kafka_controller_kafkacontroller_offlinepartitionscount) > 0
           for: 30s
           labels: {severity: critical}
         - alert: UnderMinIsrPartitions              # acks=all đang bị chặn → gọi dậy
           expr: sum(kafka_server_replicamanager_underminisrpartitioncount) > 0
           for: 30s
           labels: {severity: critical}
         - alert: ActiveControllerNotOne             # 0 = không controller, >1 = split brain
           expr: sum(kafka_controller_kafkacontroller_activecontrollercount) != 1
           for: 1m
           labels: {severity: critical}
   EOF
   grep -q '^rule_files:' ~/kafka-labs/monitoring/prometheus.yml || \
     printf '\nrule_files:\n  - /etc/prometheus/alerts.yml\n' >> ~/kafka-labs/monitoring/prometheus.yml
   # Mount file rule vào container Prometheus (thư mục monitoring/ đã được mount ở Tuần 8;
   # nếu compose của bạn mount từng file thì thêm 1 dòng volumes cho alerts.yml rồi up -d lại)
   docker compose up -d prometheus
   curl -s localhost:9090/api/v1/rules | jq -r '.data.groups[].rules[].name'
   ```
   Output mẫu: `UnderReplicatedPartitions`, `OfflinePartitions`, `UnderMinIsrPartitions`, `ActiveControllerNotOne`.

### ✅ Kiểm chứng

- `kq describe --status` → **1 leader**, `CurrentVoters: [1]` (controller tách riêng), `CurrentObservers` gồm 2, 3, 4.
- `kafka-broker-api-versions.sh` in đúng **3 broker kèm `rack: rack-a / rack-b / rack-c`** — rack đã có hiệu lực.
- `kld --describe --broker-list 2,3,4` → **broker 4 (`kafka-3`) có 2 log dir**, các broker khác 1.
- `kcfg --describe --entity-type users` in **2 user SCRAM**; `kacl --list` in đúng **ACL của `etl-svc` (Write/Describe Topic)** và **`analytics` (Read Topic + Read Group)**, **không có ACL thừa**.
- `kcfg --describe --entity-type users --entity-name etl-svc` chứa `producer_byte_rate=2097152`.
- `curl -s localhost:9090/api/v1/rules` liệt kê **4 alert**; Grafana `localhost:3000` vẽ được `UnderReplicatedPartitions` (đang = 0).

### 🧠 Ý nghĩa với đề thi

- **Controller tách riêng** là câu trả lời chuẩn cho production; `broker,controller` (combined) chỉ dành cho dev. Quorum lẻ 3/5 chịu mất `(N-1)/2`.
- **`broker.rack` phải có TRƯỚC khi tạo partition** thì replica mới được rải theo rack — bật sau không tự di chuyển replica cũ (phải reassign). Đề hay hỏi đúng chỗ này.
- Một cluster có thể chạy **nhiều listener với protocol khác nhau cùng lúc**; `inter.broker.listener.name` quyết định broker nói chuyện với nhau qua listener nào — đây là chỗ hay bị quên khi auditor đòi "mã hoá cả traffic inter-broker".
- **SCRAM tạo lúc chạy**, không restart; credential nằm trong metadata log KRaft. `kafka-storage.sh format --add-scram` chỉ dùng cho credential **đầu tiên**, lúc bootstrap.
- **ACL tối thiểu**: `--producer` = Write + Describe trên Topic; `--consumer --group` = Read + Describe trên Topic **và** Read trên Group. Thiếu vế Group là nguyên nhân `GroupAuthorizationException`.

---

## Bước 2 — Baseline: sizing, tạo topic, ghi "thế nào là bình thường"

**🎯 Mục tiêu:** Tự **tính** sizing từ yêu cầu nghiệp vụ, tạo topic đúng con số tính được, chạy tải ổn định, rồi **ghi lại trạng thái bình thường ra file**. Không có baseline thì mọi bài phá phía sau chỉ là đoán.
**🧩 Luyện kỹ năng (liên quan đề):**

- Công thức partition `max(T/P, T/C)` và disk `throughput × retention × RF × 1.2`; **không giảm được partition**.
- Đọc phân bố leader/replica theo broker và theo rack.
- Biết metric nào là "đèn xanh" để nhận ra lệch ở bước sau.

**⏱️ ~25 phút** · **Yêu cầu trước:** Bước 1.

### Các bước

1. **Tính sizing bằng tay trước khi gõ lệnh.** Yêu cầu: ghi ổn định **20 MB/s**, retention **24 giờ**, **RF 3**, dự phòng **20%**; đo được một producer đẩy ~10 MB/s, một consumer xử lý ~5 MB/s.

   | Đại lượng | Phép tính | Kết quả |
   | --- | --- | --- |
   | Partition | `max(20/10, 20/5)` = `max(2, 4)` | **4**, cộng biên tăng trưởng 1.5× → **6** |
   | Dữ liệu gốc/ngày | 20 MB/s × 86.400 s | **1,73 TB** |
   | Sau RF 3 | 1,73 × 3 | **5,18 TB** |
   | Cộng dự phòng 20% | 5,18 × 1,2 | **≈ 6,2 TB** đĩa thô cho cả cluster |

   ```bash
   # Ghi lại phép tính để đối chiếu với câu hỏi sizing trong mock
   cat > ~/kafka-labs/capstone/out/sizing.txt <<'EOF'
   target write 20 MB/s · retention 24h · RF 3 · headroom 1.2
   partitions = max(20/10, 20/5) = 4  -> chọn 6 (biên tăng trưởng 1.5x, KHÔNG giảm được về sau)
   disk       = 20 MB/s * 86400 * 3 * 1.2 = ~6.2 TB raw cho cả cluster
   EOF
   ```
2. **Tạo topic theo đúng con số tính được** (thu nhỏ retention để lab chạy nhanh).

   ```bash
   kt --create --topic orders --partitions 6 --replication-factor 3 \
      --config min.insync.replicas=2 --config segment.ms=60000 --config retention.ms=3600000
   kt --describe --topic orders
   ```
   Output mẫu — nhờ `broker.rack`, 3 replica của mỗi partition nằm ở **3 rack khác nhau**:
   ```
   Topic: orders  PartitionCount: 6  ReplicationFactor: 3  Configs: min.insync.replicas=2,segment.ms=60000,retention.ms=3600000
     Topic: orders  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3,4  Elr:   LastKnownElr:
     Topic: orders  Partition: 1  Leader: 3  Replicas: 3,4,2  Isr: 3,4,2  Elr:   LastKnownElr:
     ...
   ```
3. **Chạy tải nền** (giữ terminal 2 mở suốt capstone) — producer qua listener **SECURE** với user `etl-svc`, để quota và ACL có tác dụng thật.

   ```bash
   # Terminal 2 — producer qua SASL_SSL, 3 MB/s (trên quota 2 MB/s → sẽ bị throttle, đó là chủ ý)
   docker exec -it controller /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic orders --num-records 2000000 --record-size 1024 --throughput 3000 \
     --producer-props bootstrap.servers=kafka-1:29092 acks=all \
     --producer.config /tmp/client-etl-svc.properties
   ```
   Output mẫu mỗi 5 giây — chú ý throughput bị ghim dưới mức yêu cầu vì quota:
   ```
   10014 records sent, 2002.4 records/sec (1.96 MB/sec), 412.7 ms avg latency, 1201.0 ms max latency.
   ```
4. **Consumer nền** (terminal 3) với user `analytics`, group `fulfillment`.

   ```bash
   docker exec -it controller /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:29092 --topic orders --group fulfillment \
     --consumer.config /tmp/client-analytics.properties > /dev/null
   ```
5. **Ghi baseline** (terminal 1). Đây là file bạn sẽ `diff` ở mỗi bài phá.

   ```bash
   cat > ~/kafka-labs/capstone/snapshot.sh <<'EOF'
   #!/usr/bin/env bash
   echo "=== $(date '+%F %T') ==="
   echo "--- red lights (Prometheus) ---"
   for m in kafka_server_replicamanager_underreplicatedpartitions \
            kafka_server_replicamanager_underminisrpartitioncount \
            kafka_controller_kafkacontroller_offlinepartitionscount \
            kafka_controller_kafkacontroller_activecontrollercount; do
     printf '%-62s %s\n' "$m" "$(curl -s localhost:7071/metrics | awk -v m="$m" '$1==m {s+=$2} END{print s+0}')"
   done
   echo "--- leaders per broker ---"
   docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 --describe --topic orders \
     | awk '/Partition:/ {print $6}' | sort | uniq -c | awk '{print "broker "$2": "$1" leader(s)"}'
   echo "--- log dir sizes (broker 4) ---"
   docker exec controller /opt/kafka/bin/kafka-log-dirs.sh --bootstrap-server kafka-1:19092 --describe --broker-list 4 \
     | tail -1 | jq -r '.brokers[].logDirs[] | "\(.logDir)  error=\(.error)  partitions=\(.partitions|length)"'
   echo "--- consumer lag ---"
   docker exec controller /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka-1:19092 --describe --group fulfillment \
     | awk 'NR>1 {lag+=$6} END {print "total lag:", lag+0}'
   EOF
   chmod +x ~/kafka-labs/capstone/snapshot.sh
   ~/kafka-labs/capstone/snapshot.sh | tee ~/kafka-labs/capstone/out/baseline.txt
   ```
   Output mẫu (đây là "bình thường"):
   ```
   --- red lights (Prometheus) ---
   kafka_server_replicamanager_underreplicatedpartitions          0
   kafka_server_replicamanager_underminisrpartitioncount          0
   kafka_controller_kafkacontroller_offlinepartitionscount        0
   kafka_controller_kafkacontroller_activecontrollercount         1
   --- leaders per broker ---
   broker 2: 2 leader(s)
   broker 3: 2 leader(s)
   broker 4: 2 leader(s)
   --- log dir sizes (broker 4) ---
   /tmp/kraft-combined-logs   error=null  partitions=6
   /var/lib/kafka/data2       error=null  partitions=0
   --- consumer lag ---
   total lag: 137
   ```

### ✅ Kiểm chứng

- `sizing.txt` có đủ **3 phép tính** (partition, dữ liệu/ngày sau RF, đĩa thô kèm dự phòng) và bạn giải thích được từng số **không nhìn file**.
- `kt --describe --topic orders` → 6 partition, RF 3, `min.insync.replicas=2`, và **mỗi partition có 3 replica nằm ở 3 broker khác rack**.
- `baseline.txt` có **4 đèn xanh**: URP 0 · UnderMinIsr 0 · OfflinePartitions 0 · ActiveController **1**.
- Leader **chia đều 2/2/2** giữa 3 broker.
- Producer bị **ghim ~2 MB/s** dù yêu cầu 3 MB/s → quota đang hoạt động, và **không có lỗi nào trong log** (đúng bản chất throttle).

### 🧠 Ý nghĩa với đề thi

- Sizing là câu hỏi tính toán hiếm hoi của CCAAK: **disk = throughput × retention × RF × headroom**; **partition = `max(T/P, T/C)`** + biên. Nhớ rằng **tăng được, không giảm được**.
- "Throughput chạm trần đều đặn, log sạch" = **quota**, không phải bug. Metric để xác nhận là `produce-throttle-time-avg` phía client.
- Đèn xanh phải thuộc, vì mọi câu chẩn đoán đều bắt đầu bằng "cái nào **khác** bình thường": `ActiveControllerCount` tổng = **1**, ba metric còn lại = **0**.

---

## Bước 3 ⭐ — Bài phá số 1: DURABILITY (`min.insync.replicas=3` trên topic RF3, rồi mất 1 broker)

**🎯 Mục tiêu:** Một đồng nghiệp "tăng độ bền" bằng cách đặt `min.insync.replicas=3` trên topic RF 3. Vài ngày sau một broker chết và **toàn bộ producer `acks=all` đứng**. Bạn phải chẩn đoán đúng nguyên nhân và khôi phục bằng **hành động rẻ nhất, đảo ngược được**, không được hy sinh độ bền.
**🧩 Luyện kỹ năng (liên quan đề):**

- Ma trận `RF × min.insync.replicas × acks` và vì sao `min.isr = RF` là **over-correction**.
- Phân biệt `UnderReplicatedPartitions` (redundancy) và `UnderMinIsrPartitionCount` (ghi bị chặn).
- Không hạ `min.insync.replicas` xuống 1 và không bật unclean election trong hoảng loạn.

**⏱️ ~30 phút** · **Yêu cầu trước:** Bước 2 (tải nền đang chạy).

### Các bước

1. **Gây sự cố** (nhờ người khác chạy khối này, hoặc chạy rồi quên đi 5 phút).

   ```bash
   kcfg --alter --entity-type topics --entity-name orders --add-config min.insync.replicas=3
   docker stop kafka-2
   ```
2. **Quan sát triệu chứng trước khi kết luận.** Terminal 2 (producer) bắt đầu in:

   ```
   org.apache.kafka.common.errors.NotEnoughReplicasException: Messages are rejected since there are fewer in-sync replicas than required.
   ```
   Alert nào nổ?
   ```bash
   curl -s localhost:9090/api/v1/alerts | jq -r '.data.alerts[] | "\(.labels.alertname) \(.state)"'
   ~/kafka-labs/capstone/snapshot.sh
   ```
   Output mẫu — **hai** đèn đỏ, và đây là chỗ phân biệt:
   ```
   UnderReplicatedPartitions firing
   UnderMinIsrPartitions     firing
   ...
   kafka_server_replicamanager_underreplicatedpartitions          6
   kafka_server_replicamanager_underminisrpartitioncount          6
   kafka_controller_kafkacontroller_offlinepartitionscount        0     <-- KHÔNG mất availability đọc
   kafka_controller_kafkacontroller_activecontrollercount         1
   ```
3. **Chẩn đoán theo thứ tự metric → log → config.**

   ```bash
   # metric: URP > 0 VÀ UnderMinIsr > 0 → không chỉ suy giảm redundancy mà ghi đã bị chặn
   # log:    broker nào mất?
   kt --describe --topic orders | head -3
   # Isr: 2,4 (mất node 3 = container kafka-2) — RF vẫn 3 replica, ISR còn 2
   # config: tại sao ISR = 2 lại chặn ghi?
   kcfg --describe --entity-type topics --entity-name orders
   ```
   Output mẫu:
   ```
   Dynamic configs for topic orders are:
     min.insync.replicas=3 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:min.insync.replicas=3, STATIC_BROKER_CONFIG:min.insync.replicas=2, DEFAULT_CONFIG:min.insync.replicas=1}
   ```
   → **Kết luận:** ISR = 2 là hoàn toàn khoẻ mạnh với RF 3; thứ chặn ghi là **override ở mức topic** `min.insync.replicas=3`. Cột `synonyms` cho thấy broker vẫn đặt 2 nhưng `DYNAMIC_TOPIC_CONFIG` thắng.
4. **Khôi phục — chọn nấc rẻ nhất.** Cân nhắc bốn phương án rồi mới gõ:

   | Phương án | Chi phí | Đảo ngược được? | Đánh giá |
   | --- | --- | --- | --- |
   | Bật `unclean.leader.election.enable=true` | **mất dữ liệu** | không | ❌ không liên quan — không có partition nào offline |
   | Hạ `min.insync.replicas=1` | mất guard durability | có | ❌ quá tay theo chiều ngược lại |
   | Đổi producer sang `acks=1` | mất guard, phải sửa client | có | ❌ đụng client, ai nhớ revert? |
   | **Đặt `min.insync.replicas=2`** | không mất gì | **có** | ✅ đúng chuẩn production |

   ```bash
   kcfg --alter --entity-type topics --entity-name orders --add-config min.insync.replicas=2
   # Terminal 2: producer tự hết lỗi trong vài giây (NotEnoughReplicas là lỗi RETRIABLE)
   ~/kafka-labs/capstone/snapshot.sh      # UnderMinIsr về 0; URP vẫn 6 vì broker còn thiếu
   ```
5. **Khôi phục phần còn lại:** bật lại broker và chờ URP về 0 — đây mới là "sửa nguyên nhân gốc", bước 4 chỉ là cầm máu.

   ```bash
   docker start kafka-2
   for i in $(seq 1 30); do u=$(curl -s localhost:7071/metrics | awk '$1=="kafka_server_replicamanager_underreplicatedpartitions"{s+=$2} END{print s+0}'); echo "URP=$u"; [ "$u" = "0" ] && break; sleep 5; done
   kt --describe --topic orders | head -3          # Isr đủ 3 replica trở lại
   ```
6. **(3 phút) Thí nghiệm ngược để nhớ ma trận.** Dừng **hai** broker và xem điều gì xảy ra với `min.insync.replicas=2`.

   ```bash
   docker stop kafka-2 kafka-3
   # Producer lại NotEnoughReplicas — lần này ĐÚNG: ISR = 1 < min.isr = 2, Kafka từ chối thay vì âm thầm ghi 1 bản
   docker start kafka-2 kafka-3
   ```

### ✅ Kiểm chứng

- Lúc sự cố: **URP = 6 và UnderMinIsr = 6**, nhưng `OfflinePartitionsCount = 0` — bạn giải thích được vì sao **đọc vẫn được mà ghi thì không**.
- `kcfg --describe --entity-type topics --entity-name orders` in cột **`synonyms`** cho thấy `DYNAMIC_TOPIC_CONFIG` thắng `STATIC_BROKER_CONFIG`.
- Sau khi đặt `min.insync.replicas=2`: producer ở terminal 2 **tự hồi phục không cần restart** (chứng minh `NotEnoughReplicas` là lỗi retriable), `UnderMinIsr` về **0**.
- Sau `docker start kafka-2`: **URP về 0** và `Isr` đủ 3 replica.
- Bạn **không** dùng đến `unclean.leader.election.enable` ở bất kỳ điểm nào.

### 🧠 Ý nghĩa với đề thi

- **RF 3 + `min.insync.replicas` 2 + `acks=all`** = chịu mất **đúng 1** broker, vẫn ghi được, không mất dữ liệu. `min.isr = RF` biến một setting độ bền thành **sự cố availability** — đây là câu hỏi lặp lại nhiều nhất trong CCAAK.
- Phân biệt hai metric: **URP > 0** = redundancy suy giảm (ticket); **UnderMinIsr > 0** = `acks=all` **đang bị chặn** (gọi dậy). Đề mô tả triệu chứng bằng đúng hai từ này.
- `NotEnoughReplicasException` là lỗi **retriable** — producer tự hồi phục khi ISR đủ lại. Vì thế hành động đúng là **khôi phục replica**, không phải hạ ngưỡng.
- Luôn kiểm config **ở mức topic** trước khi kết luận về broker: cột `synonyms` là bằng chứng.

---

## Bước 4 ⭐ — Bài phá số 2: STORAGE (một `log.dirs` đầy → `KafkaStorageException`)

**🎯 Mục tiêu:** Một ổ đĩa trong JBOD của `kafka-3` đầy. Broker **vẫn sống** nhưng các partition nằm trên ổ đó offline. Bạn phải định vị bằng `kafka-log-dirs.sh`, hiểu vì sao broker không chết, và khôi phục mà không xoá tay file nào.
**🧩 Luyện kỹ năng (liên quan đề):**

- JBOD: Kafka rải partition theo **số partition mỗi dir**, không theo dung lượng; một dir hỏng chỉ hạ partition của dir đó.
- `kafka-log-dirs.sh --describe` đọc `error`, `size`, danh sách partition mỗi dir.
- Di chuyển replica **giữa các dir trong cùng broker** bằng trường `log_dirs` của reassignment JSON.

**⏱️ ~35 phút** · **Yêu cầu trước:** Bước 3 (cluster đã khoẻ trở lại).

### Các bước

1. **Dồn một partition sang ổ nhỏ** (đây là bước "ai đó đã làm trước bạn"), rồi **gây sự cố** bằng cách đổ dữ liệu cho đầy 32 MB.

   ```bash
   # Đưa replica của orders-0 trên broker 4 sang /var/lib/kafka/data2
   docker exec -i controller bash -c 'cat > /tmp/move-dir.json' <<'EOF'
   {"version":1,"partitions":[
     {"topic":"orders","partition":0,"replicas":[2,3,4],"log_dirs":["any","any","/var/lib/kafka/data2"]}
   ]}
   EOF
   krp --reassignment-json-file /tmp/move-dir.json --execute
   krp --reassignment-json-file /tmp/move-dir.json --verify
   kld --describe --broker-list 4 | tail -1 | jq -r '.brokers[].logDirs[] | "\(.logDir) partitions=\([.partitions[].partition]|join(","))"'

   # Gây sự cố: bơm ~60 MB vào orders-0 (key cố định → cùng partition không đủ chắc; dùng --partition qua produce trực tiếp)
   docker exec -it controller bash -lc 'yes "$(head -c 900 /dev/zero | tr "\0" "x")" | head -70000 | \
     /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic orders \
     --property parse.key=false --request-required-acks 1 >/dev/null'
   ```
   > 📌 Muốn chắc chắn đổ vào đúng partition 0 thì thay bằng `kafka-producer-perf-test.sh` trên một topic riêng có **1 partition** đặt trên `data2`. Cách trên đơn giản hơn: 6 partition × ~10 MB cũng đủ làm đầy ổ 32 MB.
2. **Quan sát triệu chứng.**

   ```bash
   docker logs kafka-3 --since 5m 2>&1 | grep -E "No space left|Stopping serving logs|KafkaStorageException|offline" | tail -6
   ```
   Output mẫu:
   ```
   java.io.IOException: No space left on device
   [..] WARN  Stopping serving logs in dir /var/lib/kafka/data2 (kafka.log.LogManager)
   [..] ERROR [ReplicaManager broker=4] Error processing append operation on partition orders-0 (kafka.server.ReplicaManager)
   org.apache.kafka.common.errors.KafkaStorageException: Log directory /var/lib/kafka/data2 is offline
   ```
   ```bash
   docker ps --filter name=kafka-3 --format '{{.Names}} {{.Status}}'   # VẪN "Up" — broker không chết
   ~/kafka-labs/capstone/snapshot.sh
   ```
3. **Chẩn đoán bằng `kafka-log-dirs.sh`** — lệnh đọc, miễn phí, không đụng gì.

   ```bash
   kld --describe --broker-list 4 | tail -1 | jq '.brokers[].logDirs[] | {logDir, error, partitions: (.partitions|length)}'
   ```
   Output mẫu:
   ```json
   { "logDir": "/tmp/kraft-combined-logs", "error": null, "partitions": 5 }
   { "logDir": "/var/lib/kafka/data2", "error": "KAFKA_STORAGE_ERROR", "partitions": 0 }
   ```
   → **Kết luận:** chỉ dir `data2` offline; broker 4 vẫn phục vụ 5 partition còn lại. Partition `orders-0` mất **một** replica (còn 2 trong ISR) nên vẫn ghi được với `min.isr=2` — cluster **không** ngừng dịch vụ.
4. **Khôi phục.** Với ổ thật, thứ tự đúng là: giải phóng chỗ hoặc thay ổ → broker nhận lại dir khi restart. Trong lab, tmpfs được tạo lại khi container restart:

   ```bash
   # (a) Ngăn controller đặt partition mới lên ổ đang có vấn đề — Kafka 4.3, KIP-1066
   kcfg --alter --entity-type brokers --entity-name 4 --add-config 'cordoned.log.dirs=/var/lib/kafka/data2' 2>/dev/null \
     || echo "cordoned.log.dirs không khả dụng trên bản này — bỏ qua, xem ghi chú bên dưới"

   # (b) Restart broker → tmpfs được tạo lại rỗng, dir online trở lại, replica được đồng bộ lại từ leader
   docker restart kafka-3
   sleep 20
   kld --describe --broker-list 4 | tail -1 | jq -r '.brokers[].logDirs[] | "\(.logDir) error=\(.error)"'

   # (c) Trả replica orders-0 về ổ chính để ổ nhỏ không tái phát
   docker exec -i controller bash -c 'cat > /tmp/move-back.json' <<'EOF'
   {"version":1,"partitions":[
     {"topic":"orders","partition":0,"replicas":[2,3,4],"log_dirs":["any","any","/tmp/kraft-combined-logs"]}
   ]}
   EOF
   krp --reassignment-json-file /tmp/move-back.json --execute
   krp --reassignment-json-file /tmp/move-back.json --verify
   kcfg --alter --entity-type brokers --entity-name 4 --delete-config 'cordoned.log.dirs' 2>/dev/null
   ~/kafka-labs/capstone/snapshot.sh
   ```
   > 📌 `cordoned.log.dirs` là tính năng **4.3 (KIP-1066)** và cú pháp có thể khác trên bản bạn chạy — đây là mục đã ghi trong [`../VALIDATION.md`](../VALIDATION.md) là *"cần kiểm lại khi thực hành"*. Nếu lệnh (a) báo lỗi thì bỏ qua, phần còn lại vẫn chạy đúng.

### ✅ Kiểm chứng

- Trong lúc sự cố: `docker ps` cho thấy `kafka-3` **vẫn Up**, nhưng `kld --describe --broker-list 4` in `error=KAFKA_STORAGE_ERROR` cho **đúng một** dir.
- `OfflinePartitionsCount` vẫn **0** và producer vẫn ghi được — bạn giải thích được vì sao (replica còn lại ≥ `min.insync.replicas`).
- Sau khôi phục: **cả hai dir `error=null`**, `orders-0` có đủ 3 replica trong ISR, URP về **0**.
- Bạn **không** dùng `rm` trên bất kỳ file `.log` nào.

### 🧠 Ý nghĩa với đề thi

- **Một `log.dirs` hỏng ≠ broker chết.** Broker chỉ dừng hẳn khi **mọi** dir hỏng. Đây là điểm phân biệt JBOD với "một ổ duy nhất".
- Kafka chọn dir cho partition mới theo **số partition ít nhất**, **không** theo dung lượng còn trống → mất cân bằng dung lượng là chuyện bình thường, không phải lỗi phần cứng.
- `kafka-reassign-partitions.sh` làm được **hai** việc: đổi broker (trường `replicas`) và đổi thư mục trong cùng broker (trường `log_dirs`). Đề hay hỏi "di chuyển partition sang ổ khác **trên cùng broker** dùng công cụ nào".
- `KafkaStorageException` luôn dẫn về `log.dirs`: đọc `server.log`, chạy `kafka-log-dirs.sh`, rồi mới quyết định.

---

## Bước 5 ⭐ — Bài phá số 3: SECURITY (ACL bị thu hồi nhầm, service chết im lặng)

**🎯 Mục tiêu:** Một lần dọn ACL đã xoá nhầm quyền của `analytics`. Consumer **không crash**, chỉ dừng tiến và lag tăng. Không có gì trong `server.log`. Bạn phải tìm ra bằng `kafka-authorizer.log` và cấp lại **đúng quyền tối thiểu**, không dùng `super.users`.
**🧩 Luyện kỹ năng (liên quan đề):**

- Consumer cần **hai** ACL: `Read` trên Topic **và** `Read` trên Group.
- Bật log authorizer lúc chạy bằng `--entity-type broker-loggers` (không restart).
- `TopicAuthorizationException` vs `GroupAuthorizationException`; vì sao `super.users` và `allow.everyone.if.no.acl.found=true` là hai câu trả lời sai.

**⏱️ ~30 phút** · **Yêu cầu trước:** Bước 2 (consumer `fulfillment` đang chạy ở terminal 3).

### Các bước

1. **Bật log authorizer chi tiết** — làm trước, vì đây là bước một người vận hành có kinh nghiệm luôn làm khi nghi ngờ ACL.

   ```bash
   for id in 2 3 4; do
     kcfg --alter --entity-type broker-loggers --entity-name $id --add-config kafka.authorizer.logger=DEBUG
   done
   kcfg --describe --entity-type broker-loggers --entity-name 2 | tr ',' '\n' | grep authorizer
   ```
2. **Gây sự cố** (nhờ người khác chạy).

   ```bash
   kacl --remove --force --allow-principal User:analytics --operation Read --group fulfillment
   ```
3. **Quan sát triệu chứng.** Terminal 3 (consumer) dừng nhận record; terminal 1:

   ```bash
   kcg --describe --group fulfillment          # LAG tăng dần, CONSUMER-ID vẫn còn (client chưa chết)
   docker logs kafka-1 --since 3m 2>&1 | grep -i "server.log\|ERROR" | tail -5   # KHÔNG có gì liên quan
   ```
   Client in:
   ```
   org.apache.kafka.common.errors.GroupAuthorizationException: Not authorized to access group: fulfillment
   ```
4. **Chẩn đoán bằng `kafka-authorizer.log`.**

   ```bash
   docker exec kafka-1 sh -c 'ls /opt/kafka/logs 2>/dev/null | head'     # xem appender ghi ra file hay stdout
   docker exec kafka-1 sh -c 'tail -n 50 /opt/kafka/logs/kafka-authorizer.log 2>/dev/null' \
     || docker logs kafka-1 --since 3m 2>&1 | grep authorizer | tail -5
   ```
   Output mẫu — dòng log nói chính xác thiếu gì:
   ```
   [2026-09-20 09:41:02,455] INFO Principal = User:analytics is Denied operation = Read from host = 172.19.0.4
     on resource = Group:LITERAL:fulfillment for request = OffsetFetch with resourceRefCount = 1 (kafka.authorizer.logger)
   ```
   Đối chiếu với ACL hiện có:
   ```bash
   kacl --list --principal User:analytics
   # Chỉ còn Read/Describe trên Topic:orders — vế Group đã biến mất
   ```
5. **Khôi phục — quyền tối thiểu, không hơn.** Ba phương án, chỉ một đúng:

   | Phương án | Vấn đề |
   | --- | --- |
   | Thêm `User:analytics` vào `super.users` | ❌ bỏ qua **toàn bộ** authorization cho principal đó, và cần restart broker |
   | `allow.everyone.if.no.acl.found=true` | ❌ đảo posture mặc định của **cả cluster** từ deny sang allow |
   | **Cấp lại đúng `Read` trên Group `fulfillment`** | ✅ một ACL, đúng phạm vi, đảo ngược được |

   ```bash
   kacl --add --allow-principal User:analytics --operation Read --group fulfillment
   kacl --list --principal User:analytics
   kcg --describe --group fulfillment          # LAG bắt đầu giảm, consumer tự hồi phục
   ```
6. **(3 phút) Xem mặt còn lại của cặp bẫy:** thu hồi quyền **Topic** để thấy exception đổi tên.

   ```bash
   kacl --remove --force --allow-principal User:analytics --operation Read --topic orders
   # Client đổi sang: TopicAuthorizationException: Not authorized to access topics: [orders]
   kacl --add --allow-principal User:analytics --operation Read --topic orders
   ```
7. **Trả log về mức cũ** (DEBUG trên authorizer rất ồn).

   ```bash
   for id in 2 3 4; do
     kcfg --alter --entity-type broker-loggers --entity-name $id --add-config kafka.authorizer.logger=INFO
   done
   ```

### ✅ Kiểm chứng

- `server.log` **không** có lỗi nào liên quan — bạn chứng minh được rằng sự cố ACL **không** hiện ở log broker thông thường.
- `kafka-authorizer.log` (hoặc `docker logs` sau khi bật DEBUG) in đúng dòng `Denied operation = Read ... on resource = Group:LITERAL:fulfillment`.
- `kacl --list --principal User:analytics` sau khi sửa có **đúng** hai nhóm quyền: Topic `orders` (Read/Describe) và Group `fulfillment` (Read) — **không có quyền thừa**, không có `super.users`.
- Lag của group `fulfillment` **giảm trở lại** mà không restart consumer.
- Bạn phân biệt được bằng thực nghiệm: thiếu Group → `GroupAuthorizationException`; thiếu Topic → `TopicAuthorizationException`.

### 🧠 Ý nghĩa với đề thi

- **Consumer cần hai ACL.** Quên vế Group là nguyên nhân số một của `GroupAuthorizationException`, và đề dùng đúng tên exception đó làm manh mối.
- Sự cố ACL **im lặng phía broker**: bằng chứng nằm ở `kafka-authorizer.log`, không ở `server.log`. Biết bật `kafka.authorizer.logger` lúc chạy qua `--entity-type broker-loggers` là kỹ năng vận hành thật.
- `super.users` và `allow.everyone.if.no.acl.found=true` là hai **phương án quá tay kinh điển** trong đề — chúng "đúng kỹ thuật" nhưng phá nguyên tắc quyền tối thiểu.
- Với `StandardAuthorizer`, **Deny thắng Allow** và mặc định là **deny** khi không có ACL khớp. Pattern **PREFIXED** là cách đúng để cấp quyền cho hàng trăm topic cùng tiền tố.

---

## Bước 6 ⭐ — Bài phá số 4: CÂN BẰNG (thêm broker nhưng nó không nhận traffic)

**🎯 Mục tiêu:** Thêm `kafka-4` (node 5) vào cluster. Nó join thành công, hiện trong `--describe`, nhưng **không nhận một partition nào** và ba broker cũ vẫn gánh 100% tải. Bạn phải reassign **có throttle**, gỡ throttle đúng cách, rồi trả leader về preferred replica.
**🧩 Luyện kỹ năng (liên quan đề):**

- Kafka **không tự cân bằng**: broker mới chỉ nhận topic **tạo sau**.
- Bốn bước `--generate` → `--execute --throttle` → `--verify` (chính nó gỡ throttle) → `kafka-leader-election.sh --election-type preferred`.
- Đọc config throttle động ở mức broker và mức topic.

**⏱️ ~35 phút** · **Yêu cầu trước:** Bước 4 (cluster khoẻ).

### Các bước

1. **Bật broker thứ tư** (nằm trong profile `scale`).

   ```bash
   cd ~/kafka-labs
   docker compose --profile scale up -d kafka-4
   sleep 20
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server $KAFKA_BS | grep -E "^kafka-[0-9]"
   ```
   Output mẫu — node 5 đã join:
   ```
   kafka-1:19092 (id: 2 rack: rack-a) -> (...)
   kafka-2:19092 (id: 3 rack: rack-b) -> (...)
   kafka-3:19092 (id: 4 rack: rack-c) -> (...)
   kafka-4:19092 (id: 5 rack: rack-a) -> (...)
   ```
2. **Quan sát triệu chứng:** node 5 join nhưng **trống rỗng**.

   ```bash
   kt --describe --topic orders | awk '/Partition:/ {print $8}' | tr ',' '\n' | sort | uniq -c
   # 6 x node 2, 6 x node 3, 6 x node 4, 0 x node 5
   kld --describe --broker-list 5 | tail -1 | jq -r '.brokers[].logDirs[] | "partitions=\(.partitions|length)"'   # 0
   ```
   → Đây **không** phải lỗi. Kafka không bao giờ tự di chuyển partition; đây là hành vi thiết kế, và là lý do "thêm broker" không phải hành động khắc phục tức thời cho một cluster quá tải.
3. **`--generate`: sinh kế hoạch, chưa di chuyển gì.** Lưu luôn bản `current` làm kế hoạch rollback.

   ```bash
   docker exec -i controller bash -c 'cat > /tmp/topics-to-move.json' <<'EOF'
   {"version":1,"topics":[{"topic":"orders"}]}
   EOF
   krp --topics-to-move-json-file /tmp/topics-to-move.json --broker-list 2,3,4,5 --generate \
     | tee ~/kafka-labs/capstone/out/gen.txt

   cd ~/kafka-labs/capstone/out
   awk '/^Current partition replica assignment/{f=1;next} /^Proposed partition reassignment/{f=0} f && NF' gen.txt > current.json
   awk '/^Proposed partition reassignment/{f=1;next} f && NF' gen.txt > reassign.json
   docker cp reassign.json controller:/tmp/reassign.json
   docker cp current.json  controller:/tmp/current.json
   jq -r '[.partitions[].replicas[]] | group_by(.) | map("node \(.[0]): \(length)") | join("  ")' reassign.json
   # node 2: 5  node 3: 4  node 4: 5  node 5: 4   <-- kế hoạch đã rải sang node 5
   ```
4. **`--execute --throttle`: giới hạn băng thông replication.** Cố tình đặt thấp (1 MB/s) để kịp quan sát.

   ```bash
   krp --reassignment-json-file /tmp/reassign.json --execute --throttle 1000000
   ```
   Output mẫu — đọc kỹ dòng cảnh báo, nó chính là câu hỏi trong đề:
   ```
   Current partition replica assignment {...}
   Save this to use as the --reassignment-json-file option during rollback
   Warning: You must run --verify periodically, until the reassignment completes, to ensure the throttle is removed.
   The inter-broker throttle limit was set to 1000000 B/s
   Successfully started partition reassignments for orders-0,orders-1,...,orders-5
   ```
   Trong lúc đang chạy, soi throttle config động:
   ```bash
   kcfg --describe --entity-type brokers --entity-name 5 | tr ',' '\n' | grep throttled
   # leader.replication.throttled.rate=1000000  follower.replication.throttled.rate=1000000  (DYNAMIC_BROKER_CONFIG)
   kcfg --describe --entity-type topics  --entity-name orders | tr ',' '\n' | grep throttled
   # leader.replication.throttled.replicas=0:2,0:3,...   follower.replication.throttled.replicas=0:5,...
   kt --describe --topic orders | head -3     # partition đang chuyển hiện 4 replica tạm thời
   ```
5. **`--verify` tới khi xong — và chính nó gỡ throttle.**

   ```bash
   while krp --reassignment-json-file /tmp/reassign.json --verify | tee /dev/stderr | grep -q "still in progress"; do sleep 5; done
   ```
   Output mẫu khi hoàn tất:
   ```
   Status of partition reassignment:
   Reassignment of partition orders-0 is completed.
   ...
   Clearing broker-level throttles on brokers 2,3,4,5
   Clearing topic-level throttles on topic orders
   ```
   Kiểm chứng throttle đã biến mất:
   ```bash
   kcfg --describe --entity-type brokers --entity-name 5 | grep -c throttled   # 0
   kcfg --describe --entity-type topics  --entity-name orders | grep -c throttled   # 0
   ```
6. **Trả leader về preferred replica.** Sau reassignment, leader thường không nằm ở replica đầu danh sách.

   ```bash
   kt --describe --topic orders | awk '/Partition:/ {split($8,r,","); print "p"$4" leader="$6" preferred="r[1]}'
   kle --election-type preferred --all-topic-partitions
   kt --describe --topic orders | awk '/Partition:/ {split($8,r,","); print "p"$4" leader="$6" preferred="r[1]}'
   ~/kafka-labs/capstone/snapshot.sh
   ```
7. **(tuỳ chọn 3 phút) Rollback** để thấy `current.json` có tác dụng gì: `krp --reassignment-json-file /tmp/current.json --execute` → `--verify` → node 5 lại trống.

### ✅ Kiểm chứng

- Ngay sau khi bật, node 5 **join được** (hiện trong `kafka-broker-api-versions.sh`) nhưng có **0 partition** — và bạn giải thích được rằng đây là hành vi đúng, không phải lỗi.
- `--generate` in **hai** JSON (current + proposed); `reassign.json` rải replica sang node 5.
- Trong lúc `--execute --throttle 1000000`: broker 5 có `leader/follower.replication.throttled.rate=1000000` (`DYNAMIC_BROKER_CONFIG`), topic có `*.replication.throttled.replicas`, và `kt --describe` hiện partition có **4 replica tạm thời**.
- `--verify` cuối in `completed` cho cả 6 partition **và** `Clearing broker-level throttles` + `Clearing topic-level throttles`; đếm config throttle còn lại = **0**.
- Sau `kle --election-type preferred`: **leader = replica đầu tiên** ở mọi partition, và leader chia đều 4 broker.

### 🧠 Ý nghĩa với đề thi

- "Thêm broker mà không nhận traffic" là một trong những câu hỏi kinh điển nhất của CCAAK. Đáp án luôn là **reassignment**, không phải restart, không phải tăng partition.
- **`--verify` là bước gỡ throttle.** Bỏ qua nó để lại `leader.replication.throttled.rate` trong config động, bóp mọi replication về sau — kể cả lúc khôi phục sau sự cố kế tiếp. Đây chính là bẫy mà đề cài ở phương án "đã xong sau `--execute`".
- Cùng một tool làm: đổi broker (`replicas`), đổi thư mục trong broker (`log_dirs`), tăng RF (thêm replica vào JSON). Đổi giữa chừng throttle bằng `--additional --execute --throttle N`.
- **Reassignment đổi replica; `kafka-leader-election.sh` chỉ đổi leader** (không copy dữ liệu). Triệu chứng "sau bảo trì một broker gánh hết leader" → **election**, không phải reassign.

---

## Bước 7 — Diễn tập DR: MirrorMaker 2 sang cluster thứ hai + dịch offset

**🎯 Mục tiêu:** Dựng cluster B 1 node, chạy MirrorMaker 2 sao chép `orders` sang B, **kiểm chứng dữ liệu khớp**, và chứng minh **offset của consumer group được dịch** sang B để failover không phải đọc lại từ đầu.
**🧩 Luyện kỹ năng (liên quan đề):**

- MM2 = 3 connector trên Kafka Connect: `MirrorSourceConnector`, `MirrorCheckpointConnector`, `MirrorHeartbeatConnector`.
- `DefaultReplicationPolicy` → topic đích `A.orders` (chống loop); `IdentityReplicationPolicy` giữ tên.
- Offset **đổi** khi qua MM2 → cần checkpoint / `sync.group.offsets.enabled`; đối lập với Cluster Linking giữ nguyên offset.

**⏱️ ~40 phút** · **Yêu cầu trước:** Bước 6 (cluster A khoẻ, có dữ liệu trong `orders`, group `fulfillment` có offset).

### Các bước

1. **Cluster B (1 node)** — file riêng, project riêng, join cùng docker network để MM2 gọi được cả hai bằng hostname.

   ```yaml
   # ~/kafka-labs/docker-compose.capstone-dr.yml — cluster B: 1 node KRaft combined, đích DR
   # Chạy: docker compose -p kafka-dr -f docker-compose.capstone-dr.yml up -d
   # Host: localhost:9192 · Trong docker network: kafka-b:19092
   services:
     kafka-b:
       image: apache/kafka:4.3.1
       container_name: kafka-b
       hostname: kafka-b
       ports: ["9192:9192"]
       environment:
         CLUSTER_ID: "5L6g3nShT-eMCtK--X86sw"         # KHÁC cluster A — hai cluster độc lập
         KAFKA_NODE_ID: 1
         KAFKA_PROCESS_ROLES: broker,controller       # combined: chấp nhận được cho cluster DR thu nhỏ trong lab
         KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-b:9093
         KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9192,CONTROLLER://:9093
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-b:19092,PLAINTEXT_HOST://localhost:9192
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
         KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
         KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1    # 1 broker → mọi internal topic phải RF 1
         KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
         KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
         KAFKA_SHARE_COORDINATOR_STATE_TOPIC_REPLICATION_FACTOR: 1
         KAFKA_NUM_PARTITIONS: 6
         KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
         KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
   networks:
     default:
       name: kafka-labs_default                        # network của project cluster A (thư mục ~/kafka-labs)
       external: true
   ```

   ```bash
   cd ~/kafka-labs
   docker network ls | grep kafka-labs_default          # phải có; tên khác thì sửa dòng name: ở trên
   docker compose -p kafka-dr -f docker-compose.capstone-dr.yml up -d
   export KAFKA_B=kafka-b:19092
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_B --list   # rỗng nhưng kết nối OK
   ```
2. **Chốt số liệu nguồn** để lát nữa đối chiếu.

   ```bash
   ktotal orders | tee ~/kafka-labs/capstone/out/src-count.txt
   kcg --describe --group fulfillment | awk 'NR>1 && $1!="" {s+=$4} END {print "A/fulfillment committed total:", s+0}'
   ```
3. **Viết `mm2.properties`.**

   ```properties
   # ~/kafka-labs/capstone/mm2/mm2.properties — MirrorMaker 2 dedicated mode, flow A -> B
   clusters = A, B
   A.bootstrap.servers = kafka-1:19092,kafka-2:19092,kafka-3:19092
   B.bootstrap.servers = kafka-b:19092

   # Mặc định MỌI flow tắt — phải bật tường minh
   A->B.enabled = true
   A->B.topics = orders
   B->A.enabled = false
   B->A.emit.heartbeats.enabled = false      # không tạo topic RF1 trên A (A có min.insync.replicas=2 → acks=all sẽ lỗi)

   # Cluster B chỉ 1 broker → mọi topic MM2 tạo ở B phải RF 1
   replication.factor = 1
   checkpoints.topic.replication.factor = 1
   heartbeats.topic.replication.factor = 1
   offset-syncs.topic.replication.factor = 1
   offset-syncs.topic.location = target      # mặc định "source" (=A); dời sang B để A sạch
   config.storage.replication.factor = 1
   offset.storage.replication.factor = 1
   status.storage.replication.factor = 1

   # Dịch offset consumer group A -> B và ghi thẳng vào __consumer_offsets của B (khi group ở B inactive)
   sync.group.offsets.enabled = true
   sync.group.offsets.interval.seconds = 5
   emit.checkpoints.interval.seconds = 5
   emit.heartbeats.interval.seconds = 1
   refresh.topics.interval.seconds = 10
   refresh.groups.interval.seconds = 10
   sync.topic.configs.enabled = true
   tasks.max = 3

   # DefaultReplicationPolicy → topic đích tên A.orders. Bỏ comment dòng dưới để giữ nguyên tên "orders".
   # replication.policy.class = org.apache.kafka.connect.mirror.IdentityReplicationPolicy
   ```
4. **Chạy MM2** trong container riêng (dedicated mode tự dựng worker Connect — không cần Connect cluster sẵn). Giữ terminal 4 mở.

   ```bash
   docker run --rm -it --name mm2 --network kafka-labs_default \
     -v ~/kafka-labs/capstone/mm2:/mm2 apache/kafka:4.3.1 \
     /opt/kafka/bin/connect-mirror-maker.sh /mm2/mm2.properties
   ```
   Log đáng chú ý (30–60 giây): `Kafka MirrorMaker initializing ...`, `creating herder for A->B`, `Starting connector MirrorSourceConnector` / `MirrorCheckpointConnector` / `MirrorHeartbeatConnector`, `replicating 6 topic-partitions A->B: [orders-0 ... orders-5]`, `Kafka MirrorMaker started`.
5. **Kiểm chứng dữ liệu ở B.**

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_B --list
   ```
   Output mẫu:
   ```
   A.checkpoints.internal
   A.orders
   heartbeats
   mm2-configs.A.internal
   mm2-offset-syncs.A.internal
   mm2-offsets.A.internal
   mm2-status.A.internal
   ```
   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_B --topic A.orders \
     | awk -F: '{s+=$3} END {print "B/A.orders total:", s+0}'
   cat ~/kafka-labs/capstone/out/src-count.txt        # so với A/orders total
   # heartbeat tăng ~1/giây → liveness của đường replication
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_B \
     --topic heartbeats --from-beginning --max-messages 2 \
     --formatter org.apache.kafka.connect.mirror.formatters.HeartbeatFormatter
   # Heartbeat{sourceClusterAlias=A, targetClusterAlias=B, timestamp=...}
   ```
6. **Kiểm chứng offset đã được dịch** — phần quan trọng nhất của diễn tập DR.

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_B \
     --topic A.checkpoints.internal --from-beginning --max-messages 3 \
     --formatter org.apache.kafka.connect.mirror.formatters.CheckpointFormatter
   # Checkpoint{consumerGroupId=fulfillment, topicPartition=A.orders-0, upstreamOffset=1204, downstreamOffset=1204, metadata=}

   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_B --list
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_B --describe --group fulfillment
   ```
   Output mẫu — group tồn tại ở B **dù chưa consumer nào từng nối B**; offset **có thể thấp hơn** ở A vì offset-sync ghi theo lô (dịch conservative, không bao giờ vượt):
   ```
   GROUP        TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID  HOST  CLIENT-ID
   fulfillment  A.orders  0          1204            1290            86   -            -     -
   ```
7. **Diễn tập failover:** consumer đọc tiếp ở B từ offset đã dịch, **không** đọc lại từ đầu.

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_B \
     --topic A.orders --group fulfillment --timeout-ms 8000 | wc -l
   # Số dòng ≈ LAG ở bước 6, KHÔNG phải tổng số record
   ```
8. **(tuỳ chọn 5 phút) So sánh chính sách đặt tên:** Ctrl+C MM2, bỏ comment `replication.policy.class`, chạy lại, produce thêm ở A → B xuất hiện thêm topic **`orders`** (tên giữ nguyên) chứa **chỉ record mới**. Lý do: offset của `MirrorSourceConnector` lưu trong `mm2-offsets.A.internal`, **không phụ thuộc tên topic đích** → đổi policy chỉ đổi đích cho record từ đó về sau.

### ✅ Kiểm chứng

- B có `A.orders` với **số record khớp** `src-count.txt` (chênh nhỏ là bình thường nếu producer nền vẫn chạy — dừng terminal 2 trước khi so cho chính xác), cùng số partition và cùng phân bố key → partition.
- B có `heartbeats` (end offset tăng ~1/giây) và `A.checkpoints.internal` đọc được bằng `CheckpointFormatter`.
- `kafka-consumer-groups.sh --describe --group fulfillment` **trên B** có offset cho `A.orders` mà **chưa consumer nào commit ở B**.
- Bước 7 đọc được **≈ LAG**, không phải toàn bộ topic → chứng minh offset đã được dịch, và cũng cho thấy dịch là **conservative** (có thể đọc lặp vài record → consumer phải idempotent).
- Cluster A **không** có topic mới nào do MM2 tạo (`kt --list` chỉ có `orders` + internal của A).

### 🧠 Ý nghĩa với đề thi

- **MM2 đổi offset; Cluster Linking giữ nguyên offset byte-for-byte.** Khi đề nói *"consumer phải resume đúng offset sau failover"* trên Confluent Platform → Cluster Linking. Trên Apache Kafka thuần → MM2 + offset translation, và chấp nhận đọc lặp.
- `DefaultReplicationPolicy` → `A.orders` (chống loop, cho phép active/active). `IdentityReplicationPolicy` giữ tên → chỉ dùng cho **migration / active-passive**.
- MM2 tạo **nhiều topic nội bộ ở cả hai cluster** với RF lấy từ config — cluster có `min.insync.replicas=2` mà topic RF 1 sẽ chặn ghi (`NotEnoughReplicas`). Đây là bài học vận hành thật, và cũng là lý do file properties ở trên hạ mọi `*.replication.factor` về 1 cho B.
- **RPO/RTO:** MM2 là bất đồng bộ → RPO > 0. Muốn RPO = 0 thì phải là **stretch cluster**, và cái giá là độ trễ giữa các DC nằm trong đường ghi.

---

## 🧹 Dọn dẹp toàn bộ

Chạy vào **Ngày 6** của lịch 7 ngày cuối (README: `docker compose down -v` mọi thứ), để máy nhẹ cho Honorlock System Check. Thứ tự: dừng tiến trình → gỡ cấu hình đã đặt → down mọi compose → xoá thư mục.

```bash
# 1) Ctrl+C mọi terminal: producer (2), consumer (3), MM2 (4)
cd ~/kafka-labs
export KAFKA_CTR=controller KAFKA_BS=kafka-1:19092
export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.monitoring.yml:docker-compose.capstone.yml
docker rm -f mm2 2>/dev/null

# 2) Gỡ những gì capstone đã đặt (làm để thuộc lệnh — bước 4 xoá volume sẽ dọn hết dù sao)
krp --reassignment-json-file /tmp/reassign.json --verify | grep -E "Clearing|completed" | tail -3   # chắc chắn throttle đã gỡ
for id in 2 3 4 5; do
  kcfg --alter --entity-type brokers --entity-name $id \
    --delete-config leader.replication.throttled.rate,follower.replication.throttled.rate 2>/dev/null
  kcfg --alter --entity-type broker-loggers --entity-name $id --add-config kafka.authorizer.logger=INFO 2>/dev/null
done
kacl --remove --force --allow-principal User:etl-svc   --producer --topic orders
kacl --remove --force --allow-principal User:analytics --consumer --topic orders --group fulfillment
kcfg --alter --entity-type users --entity-name etl-svc   --delete-config 'SCRAM-SHA-512,producer_byte_rate'
kcfg --alter --entity-type users --entity-name analytics --delete-config 'SCRAM-SHA-512'
kcg --delete --group fulfillment
kt  --delete --topic orders

# 3) Down cluster DR (project riêng)
docker compose -p kafka-dr -f docker-compose.capstone-dr.yml down -v

# 4) Down TOÀN BỘ stack capstone, kể cả service trong profile `scale`
docker compose --profile scale down -v --remove-orphans

# 5) Down mọi compose còn sót của các tuần khác (single node, secure, connect, ksqldb, MM2…)
docker compose $(printf -- '-f %s ' docker-compose.*.yml) down -v --remove-orphans 2>/dev/null
docker ps -a --format '{{.Names}}' | grep -Ei 'kafka|controller|prometheus|grafana|connect|schema' \
  | xargs -r docker rm -f
docker volume ls -q | grep -Ei 'kafka|grafana|prometheus' | xargs -r docker volume rm

# 6) Thư mục lab: xoá dữ liệu capstone, GIỮ 2 file compose chuẩn nếu muốn ôn lại sau thi
rm -rf ~/kafka-labs/capstone
# rm -f ~/kafka-labs/docker-compose.capstone.yml ~/kafka-labs/docker-compose.capstone-dr.yml
# rm -rf ~/kafka-labs                                   # xoá hẳn nếu không cần nữa

# 7) (Tuỳ chọn) Xoá image để trả ~4–5 GB đĩa
docker image rm apache/kafka:4.3.1 2>/dev/null
docker images --format '{{.Repository}}:{{.Tag}}' | grep -Ei 'prom/prometheus|grafana/grafana' | xargs -r docker image rm
docker system prune -f
docker ps -a; docker volume ls        # đều trống
```

> ✅ **Kiểm chứng dọn dẹp:** `docker ps -a` không còn container Kafka; `docker volume ls` không còn volume kafka/grafana/prometheus; `ls ~/kafka-labs/capstone` báo không tồn tại; `lsof -i :9092 -i :9094 -i :9096 -i :9098 -i :9192 -i :3000 -i :9090 -i :7071` không có tiến trình nào.

---

## ✅ Checklist "Trước ngày thi"

Đối chiếu với **Tiêu chí SẴN SÀNG đăng ký thi** ([README](README.md#-phải-nhớ-tuần-này)) — chỉ đặt lịch khi tick **đủ cả bốn nhóm**.

**Capstone (tiêu chí 4)**

- [ ] **Bước 1:** `kq describe --status` có 1 leader + controller tách riêng; 3 broker in đúng `rack: rack-a/b/c`; `kld` cho thấy broker 4 có 2 log dir; 2 user SCRAM tạo **không restart**; `kacl --list` chỉ có quyền tối thiểu; 4 alert rule nạp được vào Prometheus.
- [ ] **Bước 2:** `sizing.txt` có đủ 3 phép tính và bạn đọc lại được **không nhìn file**; `baseline.txt` có 4 đèn xanh (URP 0 · UnderMinIsr 0 · Offline 0 · ActiveController **1**); leader chia đều 2/2/2; producer bị quota ghim ~2 MB/s **mà log sạch**.
- [ ] **Bước 3 (durability):** tái hiện được `NotEnoughReplicas`; đọc được cột `synonyms` để chứng minh `DYNAMIC_TOPIC_CONFIG` thắng; khôi phục bằng `min.insync.replicas=2` và **không** chạm tới unclean election; URP về 0 sau khi broker trở lại.
- [ ] **Bước 4 (storage):** `kld` in `error=KAFKA_STORAGE_ERROR` cho đúng **một** dir trong khi broker vẫn `Up`; khôi phục xong cả hai dir `error=null`; **không** `rm` file `.log` nào.
- [ ] **Bước 5 (security):** tìm ra nguyên nhân bằng `kafka-authorizer.log` (không phải `server.log`); cấp lại **đúng một** ACL; tái hiện được **cả hai** exception `GroupAuthorizationException` và `TopicAuthorizationException`.
- [ ] **Bước 6 (cân bằng):** node 5 join nhưng 0 partition; `--execute --throttle` tạo config throttle động; `--verify` in `Clearing ... throttles` và **đếm throttle còn lại = 0**; preferred leader election trả leader về replica đầu.
- [ ] **Bước 7 (DR):** `A.orders` ở B khớp số record; `A.checkpoints.internal` đọc được; group `fulfillment` có offset ở B **dù chưa consumer nào nối B**; failover chỉ đọc ≈ LAG chứ không đọc lại toàn bộ.
- [ ] **🧹 Dọn dẹp toàn bộ:** `docker ps -a` trống, volume trống, không port nào còn bị chiếm.

**Kiến thức (tiêu chí 1–3)**

- [ ] **≥3 bộ mock KHÁC NHAU đạt ≥80%** ổn định, canh giờ 90', cách nhau ≥1 ngày; **không bài nào <70%** (nếu có → đã lùi lịch 1 tuần).
- [ ] **Review 100% câu sai** + file phân tích **6 mục + 3 mục bổ sung** (*Trục đánh đổi*, *Hành động rẻ hơn đã bị bỏ qua*, *Lý do mình sai*) trong [`CCAAK/questions/`](../../questions/README.md).
- [ ] Số câu sai nhãn **"bẫy version" = 0** — đối chiếu [`resources/kafka-4x-operational-changes.md`](resources/kafka-4x-operational-changes.md).
- [ ] Đọc trôi **bảng số [§6](../../CCAAK-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng)** + **bảng phản xạ [§7](../../CCAAK-STUDY-PLAN.md#7-bảng-phản-xạ-triệu-chứng--hành-động)**; **tự viết lại cram sheet 1 trang** từ trí nhớ rồi đối chiếu **60 fact** trong README.
- [ ] Thuộc **playbook tổng hợp** và **15 bẫy**, đặc biệt **5 bẫy version** (ZooKeeper/znode/`--zookeeper`/`AclAuthorizer`/syllabus 4 domain cũ).
- [ ] Giải thích được **bằng chính capstone** năm cụm hay hỏi nhất: ma trận durability (Bước 3) · JBOD và `log.dirs` (Bước 4) · ACL tối thiểu và hai exception (Bước 5) · reassignment + throttle + preferred election (Bước 6) · MM2 vs Cluster Linking (Bước 7).

**Hậu cần thi**

- [ ] Đối chiếu [confluent.io/certification](https://www.confluent.io/certification/) về proctor, số câu, lệ phí — xem [resources/ccaak-official-exam-page.md](resources/ccaak-official-exam-page.md) và [resources/confluent-certification-policies.md](resources/confluent-certification-policies.md).
- [ ] Cài **Honorlock Chrome Extension**, chạy **System Check** ≥1 ngày trước **và** lại vào sáng ngày thi; Chrome bản mới, tắt VPN + mọi extension khác.
- [ ] **Government ID** còn hạn, tên **khớp** tài khoản `training.confluent.io`; phòng trống, một mình, khoá cửa, sẵn sàng quay 360°.
- [ ] Máy đã `docker compose down -v` toàn bộ; ngủ đủ; trước giờ thi chỉ đọc **cram sheet 60 fact** + **15 bẫy**.

> 🎓 Đủ **cả 4 tiêu chí** → đặt lịch tại [training.confluent.io](https://training.confluent.io/). Chưa đủ → lùi lịch, không "thử vận may": trượt là phải **chờ 7 ngày** mới được thi lại.

> ✅ Xong capstone thì quay lại **[Lab checklist trong README](README.md#-lab-checklist)** tick đủ 8 dòng, rồi làm **[questions.md](questions.md)** (30 câu / 45 phút) như bài khởi động trước full mock tiếp theo.
