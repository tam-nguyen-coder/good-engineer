# 🧪 Hands-on Labs — Tuần 1: Kiến trúc Kafka & `KRaft` + Dựng cluster + CLI

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab (trừ khi lab sau nói "giữ cluster").
> ⚙️ Yêu cầu chung: macOS/Linux/WSL2, **Docker Desktop** (hoặc Docker Engine + Compose v2), **Node.js 24** (`node -v`), ~4 GB RAM trống cho cluster 4 container.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../KAFKA-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab và mọi tuần sau)

### 1) Thư mục lab + kiểm tra công cụ

```bash
mkdir -p ~/kafka-labs && cd ~/kafka-labs
docker --version            # >= 24
docker compose version      # v2.x
node -v                     # v24.x
```

> 📌 Toàn bộ 10 tuần dùng chung thư mục `~/kafka-labs/` (ngoài repo) để chứa 2 file compose chuẩn và code Node.js. Tuần sau chỉ cần `cd ~/kafka-labs && docker compose -f docker-compose.cluster.yml up -d`.

### 2) Alias CLI (thêm vào `~/.zshrc` hoặc chạy mỗi phiên)

Mọi CLI của Kafka nằm trong container tại `/opt/kafka/bin/`. Alias dùng 2 biến để đổi nhanh giữa cluster 1 node và 3 node:

```bash
# Mặc định: cluster 1 node (Lab 1.1). Sang cluster 3 node (Lab 1.2) thì:
#   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
export KAFKA_CTR=kafka
export KAFKA_BS=localhost:9092

alias kt='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_BS'
alias kcp='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS'
alias kcc='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BS'
alias kcg='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_BS'
alias kcfg='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-configs.sh --bootstrap-server $KAFKA_BS'
alias kq='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-metadata-quorum.sh --bootstrap-server $KAFKA_BS'
alias ksh='docker exec -it $KAFKA_CTR bash'   # vào shell container để chạy tool khác
```

> 🧠 Vì sao alias có `$KAFKA_BS`? Với cluster 3 node, nếu đứng **trong** container `kafka-1` mà bootstrap `localhost:9092`, broker trả metadata `localhost:9094`/`localhost:9096` cho 2 broker kia — **không tồn tại bên trong container** → produce vào partition do broker khác làm leader sẽ timeout. Đây chính là bẫy `advertised.listeners` (mục 7 README). Bên trong Docker network phải dùng listener nội bộ `kafka-1:19092`.

### 3) Project Node.js

```bash
cd ~/kafka-labs
npm init -y >/dev/null
npm i kafkajs@2
node -e "import('kafkajs').then(m => console.log('kafkajs OK', Object.keys(m).slice(0,3)))"
```

> 📌 **Ghi chú 1 lần cho cả 10 tuần:** client Node.js được Confluent hỗ trợ chính thức là `@confluentinc/kafka-javascript` (API tương thích KafkaJS, hỗ trợ KIP-848 & share groups, dựa trên librdkafka). Labs dùng `kafkajs` vì cài nhẹ, không cần native build, đủ để học khái niệm. Tính năng `kafkajs` không có (KIP-848, share groups, một số metric) sẽ dùng CLI hoặc "chỉ mô tả".

---

## Lab 1.1 — Cài Docker + `docker-compose.single.yml` (1 node `KRaft` combined)

**🎯 Mục tiêu:** Có cluster Kafka 1 node chạy `apache/kafka:4.3.1` ở chế độ `KRaft` combined (`process.roles=broker,controller`), truy cập được **cả từ trong container lẫn từ host** qua `localhost:9092`. File compose này là **FILE CHUẨN**, các tuần sau tham chiếu "cluster 1 node từ Lab 1.1".
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc hiểu từng dòng config `KRaft`: `process.roles`, `node.id`, `controller.quorum.voters`, `controller.listener.names`, `CLUSTER_ID`.
- Hiểu vì sao cần **2 listener** (`PLAINTEXT` nội bộ + `PLAINTEXT_HOST` cho host) và `advertised.listeners`.
- Đọc output `kafka-metadata-quorum.sh describe --status`.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo file `~/kafka-labs/docker-compose.single.yml` (in đầy đủ — copy nguyên văn).

   ```yaml
   # ~/kafka-labs/docker-compose.single.yml
   # Kafka 4.3.1 — 1 node KRaft "combined" (broker + controller). Chỉ dùng cho dev/lab.
   # Host connect: localhost:9092 · Trong docker network: kafka:19092 · Controller: kafka:9093
   services:
     kafka:
       image: apache/kafka:4.3.1
       container_name: kafka
       hostname: kafka
       ports:
         - "9092:9092"
       environment:
         # ---- Định danh cluster & node (KRaft) ----
         CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"            # 22 ký tự base64; image tự chạy kafka-storage.sh format
         KAFKA_NODE_ID: 1
         KAFKA_PROCESS_ROLES: broker,controller           # combined: chỉ dev/test
         KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093     # static quorum 1 voter (dynamic quorum: xem README mục 5)
         KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
         # ---- Listeners: bind vs advertise ----
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9092,CONTROLLER://:9093
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:19092,PLAINTEXT_HOST://localhost:9092
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
         KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
         # ---- Topic nội bộ phải RF=1 vì chỉ có 1 broker ----
         KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
         KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
         KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
         KAFKA_SHARE_COORDINATOR_STATE_TOPIC_REPLICATION_FACTOR: 1
         # ---- Tiện cho lab ----
         KAFKA_NUM_PARTITIONS: 3                          # mặc định Kafka là 1
         KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0        # mặc định 3000 — consumer join nhanh hơn khi demo
         KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
       # Muốn giữ dữ liệu qua `docker compose down` thì bỏ comment 2 dòng dưới + khối volumes cuối file:
       # volumes:
       #   - kafka-single-data:/tmp/kraft-combined-logs
   # volumes:
   #   kafka-single-data:
   ```
2. Khởi động và xem log format storage + broker start.

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.single.yml up -d
   docker compose -f docker-compose.single.yml logs -f kafka | grep -E "Formatting|KafkaRaftServer|started \(kafka.server" 
   # Ctrl+C khi thấy "Kafka Server started" (khoảng 5–10 giây)
   ```
3. Kiểm tra quorum và broker từ **trong container**.

   ```bash
   export KAFKA_CTR=kafka KAFKA_BS=localhost:9092
   kq describe --status
   docker exec kafka /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092 | head -1
   ```
4. Kiểm tra từ **host** bằng Node.js — đây là phép thử `advertised.listeners`.

   ```bash
   cat > ~/kafka-labs/ping.mjs <<'EOF'
   import { Kafka, logLevel } from "kafkajs";
   const brokers = (process.env.BROKERS ?? "localhost:9092").split(",");
   const kafka = new Kafka({ clientId: "ping", brokers, logLevel: logLevel.ERROR });
   const admin = kafka.admin();
   await admin.connect();
   const cluster = await admin.describeCluster();
   console.log("controller:", cluster.controller, "| brokers advertised:", cluster.brokers.map(b => `${b.nodeId}=${b.host}:${b.port}`).join(" "));
   await admin.disconnect();
   EOF
   node ~/kafka-labs/ping.mjs
   ```

### ✅ Kiểm chứng

- `kq describe --status` in `ClusterId: MkU3OEVBNTcwNTJENDM2Qk`, `LeaderId: 1`, `CurrentVoters` có node 1, `HighWatermark` > 0 (metadata log đã có record).
- `ping.mjs` in `brokers advertised: 1=localhost:9092` — vì client từ host gõ cửa listener `PLAINTEXT_HOST`, broker trả về đúng địa chỉ advertise của listener đó.
- **Thí nghiệm bẫy Docker (5 phút, rất đáng làm):** sửa `KAFKA_ADVERTISED_LISTENERS` thành `PLAINTEXT://kafka:19092,PLAINTEXT_HOST://kafka:9092`, `up -d` lại, chạy `node ping.mjs` → kết nối bootstrap **thành công** nhưng tool báo lỗi `getaddrinfo ENOTFOUND kafka` khi cố nối tới broker — vì host không resolve được hostname `kafka`. Đổi lại `localhost:9092` rồi `up -d`.

### 🧹 Dọn dẹp

```bash
# GIỮ cluster nếu làm tiếp Lab 1.2 ngay (Lab 1.2 sẽ down nó). Nếu nghỉ:
docker compose -f ~/kafka-labs/docker-compose.single.yml down   # thêm -v nếu đã bật volumes
```

### 🧠 Ý nghĩa với đề thi

- `process.roles=broker,controller` = **combined mode**, docs nói rõ **chỉ dev/test**; production tách `broker` và `controller`.
- Broker **không start** nếu log dir chưa `kafka-storage.sh format` với đúng `cluster.id` — image làm hộ nhờ `CLUSTER_ID`.
- `listeners` = **bind**, `advertised.listeners` = địa chỉ trong **MetadataResponse**. Client luôn dùng advertised → lỗi "connect được bootstrap nhưng không produce/consume được" gần như luôn là advertised sai.
- Controller có listener riêng (`CONTROLLER`, port **9093**) và không được trùng `inter.broker.listener.name`.

---

## Lab 1.2 — `docker-compose.cluster.yml` 3 broker + 1 controller ⭐

**🎯 Mục tiêu:** Dựng cluster **3 broker** (host port 9092/9094/9096) + **1 controller** tách riêng (`process.roles=controller`), `default.replication.factor=3`, `min.insync.replicas=2`. Đây là **FILE CHUẨN THỨ 2**, dùng cho hầu hết lab từ Tuần 2 trở đi ("dùng cluster 3 node từ Lab 1.2").
**🧩 Luyện kỹ skill (liên quan đề):**

- Tách vai trò broker/controller; broker-only vẫn phải khai `controller.listener.names` + `controller.quorum.voters`.
- Mỗi broker có `node.id` riêng, `advertised.listeners` riêng (port host khác nhau).
- Cấu hình production-like: RF=3, min.isr=2 (Tuần 2 khai thác sâu).

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 1.1 (đã có alias + thư mục).

### Các bước

1. Tắt cluster 1 node để tránh trùng port 9092.

   ```bash
   cd ~/kafka-labs && docker compose -f docker-compose.single.yml down
   ```
2. Tạo `~/kafka-labs/docker-compose.cluster.yml` (in đầy đủ; dùng YAML anchor để 3 broker không lặp 15 dòng).

   ```yaml
   # ~/kafka-labs/docker-compose.cluster.yml
   # Kafka 4.3.1 — 1 controller (node 1) + 3 broker (node 2,3,4). RF mặc định 3, min.insync.replicas 2.
   # Host connect: localhost:9092,localhost:9094,localhost:9096 · Trong docker network: kafka-1:19092,kafka-2:19092,kafka-3:19092
   x-broker-common: &broker-common
     image: apache/kafka:4.3.1
     depends_on:
       - controller

   x-broker-env: &broker-env
     CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"
     KAFKA_PROCESS_ROLES: broker
     KAFKA_CONTROLLER_QUORUM_VOTERS: 1@controller:9093
     KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
     KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
     KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
     # ---- production-like defaults ----
     KAFKA_DEFAULT_REPLICATION_FACTOR: 3
     KAFKA_MIN_INSYNC_REPLICAS: 2
     KAFKA_NUM_PARTITIONS: 3
     KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
     KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
     KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
     KAFKA_SHARE_COORDINATOR_STATE_TOPIC_REPLICATION_FACTOR: 3
     KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
     KAFKA_LOG_DIRS: /tmp/kraft-combined-logs

   services:
     controller:
       image: apache/kafka:4.3.1
       container_name: controller
       hostname: controller
       environment:
         CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"
         KAFKA_NODE_ID: 1
         KAFKA_PROCESS_ROLES: controller                 # controller thuần, không nhận produce/fetch
         KAFKA_LISTENERS: CONTROLLER://:9093
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT
         KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
         KAFKA_CONTROLLER_QUORUM_VOTERS: 1@controller:9093
         KAFKA_LOG_DIRS: /tmp/kraft-combined-logs        # chứa __cluster_metadata-0

     kafka-1:
       <<: *broker-common
       container_name: kafka-1
       hostname: kafka-1
       ports:
         - "9092:9092"
       environment:
         <<: *broker-env
         KAFKA_NODE_ID: 2
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9092
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:19092,PLAINTEXT_HOST://localhost:9092

     kafka-2:
       <<: *broker-common
       container_name: kafka-2
       hostname: kafka-2
       ports:
         - "9094:9094"
       environment:
         <<: *broker-env
         KAFKA_NODE_ID: 3
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9094
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-2:19092,PLAINTEXT_HOST://localhost:9094

     kafka-3:
       <<: *broker-common
       container_name: kafka-3
       hostname: kafka-3
       ports:
         - "9096:9096"
       environment:
         <<: *broker-env
         KAFKA_NODE_ID: 4
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9096
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-3:19092,PLAINTEXT_HOST://localhost:9096
   ```

   > 📌 Vì sao port host của broker 2 là `9094` mà listener trong container cũng `:9094`? Vì `advertised.listeners` phải là địa chỉ **client trên host gõ được**: `localhost:9094`. Nếu bind `:9092` trong container rồi map `9094:9092`, broker vẫn advertise `localhost:9094` được — nhưng bind cùng số cho dễ debug.
3. Khởi động, chờ 4 container `running`.

   ```bash
   docker compose -f docker-compose.cluster.yml up -d
   docker compose -f docker-compose.cluster.yml ps
   docker compose -f docker-compose.cluster.yml logs kafka-1 | grep -E "Kafka Server started|Registered broker" | tail -3
   ```
4. Đổi alias sang cluster 3 node (nhớ: **listener nội bộ**).

   ```bash
   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
   kq describe --status
   kq describe --replication
   docker exec kafka-1 /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server kafka-1:19092 | grep -E "^kafka-[0-9]"
   ```
5. Từ host, chạy lại `ping.mjs` với 3 bootstrap.

   ```bash
   BROKERS=localhost:9092,localhost:9094,localhost:9096 node ~/kafka-labs/ping.mjs
   ```
6. Xem config mặc định thật của broker (đối chiếu số liệu PHẢI NHỚ).

   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 --all | grep -E "^\s+(num.partitions|default.replication.factor|min.insync.replicas|log.segment.bytes|log.retention.hours|message.max.bytes|replica.lag.time.max.ms|unclean.leader.election.enable|log.index.interval.bytes)="
   ```

### ✅ Kiểm chứng

- `kq describe --status` → `LeaderId: 1`, `CurrentVoters` = node 1, `CurrentObservers` = node 2,3,4 (broker là **observer** của metadata log — fetch nhưng không vote).
- `kafka-broker-api-versions.sh` liệt kê đúng 3 dòng `kafka-1:19092 (id: 2 rack: null)`, `kafka-2…(id: 3)`, `kafka-3…(id: 4)`.
- `ping.mjs` từ host in `controller: 2` *(đây là "controller" theo nghĩa client-visible — broker nào đó đại diện; KRaft controller thật ở node 1 không lộ ra client)* và 3 broker `localhost:9092/9094/9096`.
- Bước 6 in `min.insync.replicas=2`, `default.replication.factor=3`, `log.segment.bytes=1073741824`, `log.retention.hours=168`, `message.max.bytes=1048588`, `replica.lag.time.max.ms=30000`, `unclean.leader.election.enable=false`, `log.index.interval.bytes=4096`.

### 🧹 Dọn dẹp

```bash
# GIỮ cluster cho Lab 1.3 → 1.6. Khi kết thúc tuần:
docker compose -f ~/kafka-labs/docker-compose.cluster.yml down
```

### 🧠 Ý nghĩa với đề thi

- Production **tách** controller và broker; quorum thật cần **3 hoặc 5** controller (lab dùng 1 để nhẹ máy — 1 controller chết = cluster mất metadata service, dù broker vẫn phục vụ produce/fetch một lúc).
- Broker-only **vẫn cần** `controller.listener.names` + `controller.quorum.voters`/`bootstrap.servers` để tìm quorum.
- Broker là **observer** của `__cluster_metadata`: fetch metadata từ active controller giống consumer, không tham gia vote.
- `default.replication.factor` và `min.insync.replicas` là **broker config** áp cho topic tạo mới; topic có thể override (`min.insync.replicas` topic-level).

---

## Lab 1.3 — CLI: topic, produce có key, consume có partition/offset

**🎯 Mục tiêu:** Dùng 5 CLI cốt lõi để tạo topic 3 partition RF 3, produce message **có key**, consume in **key + partition + offset**, và chứng minh bằng mắt: **cùng key → cùng partition**, offset tăng dần trong partition.
**🧩 Luyện kỹ năng (liên quan đề):**

- `kafka-topics.sh --create/--describe/--alter`, đọc dòng `Leader / Replicas / Isr`.
- `kafka-console-producer.sh --property parse.key=true key.separator=:`.
- `kafka-console-consumer.sh --from-beginning --property print.key/print.partition/print.offset`.
- `kafka-consumer-groups.sh --describe` đọc `CURRENT-OFFSET / LOG-END-OFFSET / LAG`.
- `kafka-configs.sh` đổi config topic động.

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 1.2 đang chạy, `KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092`.

### Các bước

1. Tạo topic `orders` 3 partition RF 3 và describe.

   ```bash
   kt --create --topic orders --partitions 3 --replication-factor 3
   kt --describe --topic orders
   ```
   Output mẫu (leader mỗi partition rải đều 3 broker, `Isr` đủ 3):
   ```
   Topic: orders   TopicId: ...   PartitionCount: 3   ReplicationFactor: 3   Configs: min.insync.replicas=2
       Topic: orders   Partition: 0   Leader: 2   Replicas: 2,3,4   Isr: 2,3,4   Elr:   LastKnownElr:
       Topic: orders   Partition: 1   Leader: 3   Replicas: 3,4,2   Isr: 3,4,2   Elr:   LastKnownElr:
       Topic: orders   Partition: 2   Leader: 4   Replicas: 4,2,3   Isr: 4,2,3   Elr:   LastKnownElr:
   ```
2. Thử **sai** để nhớ: RF > số broker.

   ```bash
   kt --create --topic too-many-replicas --partitions 1 --replication-factor 4
   # → InvalidReplicationFactorException: Unable to replicate the partition 4 time(s): The target replication factor of 4 cannot be reached because only 3 broker(s) are registered.
   ```
3. Produce 9 message **có key** (3 key × 3 lần). Gõ từng dòng rồi Ctrl+D (hoặc Ctrl+C) để thoát.

   ```bash
   kcp --topic orders --property parse.key=true --property key.separator=:
   ```
   ```
   alice:order-1
   bob:order-2
   carol:order-3
   alice:order-4
   bob:order-5
   carol:order-6
   alice:order-7
   bob:order-8
   carol:order-9
   ```
   > ⚠️ Không có `parse.key=true` thì cả chuỗi `alice:order-1` thành **value**, key = null → sticky partitioner → không còn "cùng key cùng partition".
   > 📌 KIP-1147 (4.1+) đưa tên mới `--reader-property` (producer) / `--formatter-property` (consumer); `--property` vẫn chạy ở 4.3 kèm cảnh báo deprecated — đề có thể dùng cả hai.
4. Consume từ đầu, in key/partition/offset/timestamp.

   ```bash
   kcc --topic orders --from-beginning \
     --property print.key=true --property print.partition=true \
     --property print.offset=true --property print.timestamp=true \
     --timeout-ms 5000
   ```
   Output mẫu (thứ tự **giữa** partition không đảm bảo, nhưng **trong** partition thì đúng và offset liên tục 0,1,2):
   ```
   CreateTime:1757900000123   Partition:2   Offset:0   alice   order-1
   CreateTime:1757900000456   Partition:2   Offset:1   alice   order-4
   CreateTime:1757900000789   Partition:2   Offset:2   alice   order-7
   CreateTime:...             Partition:0   Offset:0   bob     order-2
   ...
   ```
5. Đọc **đúng 1 partition từ 1 offset** (không dùng group).

   ```bash
   kcc --topic orders --partition 2 --offset 1 --property print.offset=true --max-messages 2
   ```
6. Consume bằng **consumer group** rồi xem LAG.

   ```bash
   kcc --topic orders --group orders-cli --from-beginning --timeout-ms 5000 >/dev/null
   kcg --describe --group orders-cli
   ```
   Output mẫu: 3 dòng partition 0/1/2, `CURRENT-OFFSET` = `LOG-END-OFFSET` = 3, `LAG` = 0, `CONSUMER-ID` = `-` (group inactive vì consumer đã thoát).
7. Reset offset group về đầu (chỉ được khi group **inactive**) và xem LAG quay lại 9.

   ```bash
   kcg --group orders-cli --topic orders --reset-offsets --to-earliest --execute
   kcg --describe --group orders-cli
   ```
8. Đổi config topic **động** bằng `kafka-configs.sh`, rồi tăng partition (chỉ tăng được).

   ```bash
   kcfg --alter --entity-type topics --entity-name orders --add-config retention.ms=86400000,message.timestamp.type=LogAppendTime
   kcfg --describe --entity-type topics --entity-name orders
   kt --alter --topic orders --partitions 4
   kt --alter --topic orders --partitions 3   # → lỗi: Topic currently has 4 partitions, which is higher than the requested 3
   ```
   Produce thêm `alice:order-10` rồi consume `--from-beginning` với `print.partition` — có thể thấy `alice` **nhảy sang partition khác** (murmur2 mod 4 ≠ mod 3) và timestamp giờ là `LogAppendTime:`.

### ✅ Kiểm chứng

- Mỗi key (alice/bob/carol) xuất hiện ở **đúng 1** partition trong 9 message đầu; trong partition đó offset là `0,1,2` đúng thứ tự gõ.
- `kcg --describe` sau bước 6: LAG = 0; sau bước 7: LAG tổng = 9.
- Bước 8: sau khi tăng lên 4 partition, message mới của cùng key **có thể** rơi vào partition khác → minh hoạ bẫy "tăng partition phá key mapping".

### 🧹 Dọn dẹp

```bash
kt --delete --topic orders
kt --delete --topic too-many-replicas 2>/dev/null
kcg --delete --group orders-cli
```

### 🧠 Ý nghĩa với đề thi

- **Cùng key → cùng partition → có thứ tự**; không key → sticky partitioner → không có thứ tự theo nguồn.
- Offset là **per-partition**, bắt đầu **0**, tăng dần liên tục; `LOG-END-OFFSET − CURRENT-OFFSET = LAG`.
- Số partition **chỉ tăng**; tăng xong **phá** key→partition mapping với topic đã có dữ liệu.
- `--reset-offsets` cần group **inactive** và `--execute` (không có `--execute` = dry-run).
- `kafka-configs.sh --alter --add-config` đổi config topic **không cần restart**; `message.timestamp.type` là topic config.

---

## Lab 1.4 — Node.js `kafkajs`: producer + consumer đầu tiên ⭐

**🎯 Mục tiêu:** Viết `producer.mjs` (tạo topic bằng `admin.createTopics`, `send` có key/headers, in `partition/baseOffset`) và `consumer.mjs` (consumer group, `eachMessage` in partition/offset/key/value/timestamp/headers). Chạy **2 tiến trình consumer cùng group** để thấy Kafka **chia partition** và **1 partition chỉ 1 consumer**.
**🧩 Luyện kỹ năng (liên quan đề):**

- Vòng đời client: `new Kafka({ clientId, brokers })` → `connect` → thao tác → `disconnect`.
- `RecordMetadata` trả về sau `send`: `partition`, `baseOffset`.
- Consumer group: assignment, rebalance khi thêm/bớt consumer, `fromBeginning` chỉ có tác dụng khi group **chưa có offset committed** (tương đương `auto.offset.reset=earliest`).

**⏱️ ~45 phút** · **Yêu cầu trước:** Lab 1.2 đang chạy; `npm i kafkajs` xong.

### Các bước

1. Tạo `~/kafka-labs/producer.mjs`.

   ```javascript
   // ~/kafka-labs/producer.mjs — Lab 1.4
   import { Kafka, logLevel } from "kafkajs";

   const TOPIC = "payments";
   const kafka = new Kafka({
     clientId: "week1-producer",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"], // bootstrap: chỉ để lấy metadata
     logLevel: logLevel.WARN,
   });

   // 1) Admin API: tạo topic 3 partition, RF 3 (idempotent — đã có thì bỏ qua)
   const admin = kafka.admin();
   await admin.connect();
   const created = await admin.createTopics({
     waitForLeaders: true,
     topics: [{ topic: TOPIC, numPartitions: 3, replicationFactor: 3 }],
   });
   console.log(created ? `topic ${TOPIC} created` : `topic ${TOPIC} already exists`);
   const { topics } = await admin.fetchTopicMetadata({ topics: [TOPIC] });
   for (const p of topics[0].partitions) {
     console.log(`  partition ${p.partitionId}: leader=${p.leader} replicas=[${p.replicas}] isr=[${p.isr}]`);
   }
   await admin.disconnect();

   // 2) Producer API: 9 message, 3 key → quan sát key → partition
   const producer = kafka.producer(); // mặc định kafkajs: idempotent=false, acks=-1 (all), partitioner murmur2 tương thích Java
   await producer.connect();
   const users = ["alice", "bob", "carol"];
   for (let i = 1; i <= 9; i++) {
     const key = users[(i - 1) % 3];
     const [meta] = await producer.send({
       topic: TOPIC,
       acks: -1, // -1 = all ISR (mặc định); 1 = leader only; 0 = fire-and-forget
       messages: [
         {
           key,
           value: JSON.stringify({ id: i, user: key, amount: i * 10 }),
           headers: { source: "lab-1.4", schema: "v1" },
         },
       ],
     });
     console.log(`sent id=${i} key=${key} -> partition=${meta.partition} baseOffset=${meta.baseOffset}`);
   }
   await producer.disconnect();
   ```
2. Tạo `~/kafka-labs/consumer.mjs`.

   ```javascript
   // ~/kafka-labs/consumer.mjs — Lab 1.4
   import { Kafka, logLevel } from "kafkajs";

   const TOPIC = "payments";
   const GROUP = process.env.GROUP ?? "payments-app";
   const kafka = new Kafka({
     clientId: `week1-consumer-${process.pid}`,
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.WARN,
   });

   const consumer = kafka.consumer({ groupId: GROUP }); // mặc định: sessionTimeout 30000, heartbeat 3000, autoCommit bật
   await consumer.connect();
   await consumer.subscribe({ topic: TOPIC, fromBeginning: true }); // = auto.offset.reset=earliest (chỉ khi group chưa có offset)

   consumer.on(consumer.events.GROUP_JOIN, ({ payload }) => {
     const assigned = payload.memberAssignment[TOPIC] ?? [];
     console.log(`[pid ${process.pid}] joined group=${payload.groupId} generation=${payload.generationId} partitions=[${assigned}]`);
   });

   await consumer.run({
     eachMessage: async ({ topic, partition, message }) => {
       console.log(
         `[pid ${process.pid}] ${topic} p${partition} offset=${message.offset} ` +
           `key=${message.key?.toString()} value=${message.value.toString()} ` +
           `ts=${message.timestamp} source=${message.headers?.source?.toString()}`
       );
     },
   });

   process.on("SIGINT", async () => {
     await consumer.disconnect();
     process.exit(0);
   });
   ```
3. Chạy producer.

   ```bash
   cd ~/kafka-labs && node producer.mjs
   ```
   Output mẫu — mỗi key luôn cùng 1 partition, offset của partition đó 0,1,2:
   ```
   topic payments created
     partition 0: leader=3 replicas=[3,4,2] isr=[3,4,2]
     partition 1: leader=4 replicas=[4,2,3] isr=[4,2,3]
     partition 2: leader=2 replicas=[2,3,4] isr=[2,3,4]
   sent id=1 key=alice -> partition=1 baseOffset=0
   sent id=2 key=bob   -> partition=0 baseOffset=0
   sent id=3 key=carol -> partition=1 baseOffset=1
   sent id=4 key=alice -> partition=1 baseOffset=2
   ...
   ```
4. Mở **terminal 2** chạy 1 consumer → nó nhận **cả 3 partition**.

   ```bash
   cd ~/kafka-labs && node consumer.mjs
   # [pid 4101] joined group=payments-app generation=1 partitions=[0,1,2]
   # 9 dòng message
   ```
5. Mở **terminal 3** chạy consumer thứ 2 **cùng group** → cả hai in dòng `joined ... generation=2`, partition chia 2/1. Chạy `node producer.mjs` lần nữa ở terminal 1: message của `alice` chỉ in ở tiến trình giữ partition của alice.
6. Mở **terminal 4** chạy consumer thứ 3 và thứ 4 (2 tiến trình nữa, tổng 4) → tiến trình thứ 4 `partitions=[]` — **idle** vì chỉ có 3 partition.
7. Kiểm tra group bằng CLI trong khi consumer còn chạy.

   ```bash
   kcg --describe --group payments-app
   # 3 dòng, CONSUMER-ID = week1-consumer-<pid>-..., HOST = /172.x.x.x (IP host trong docker network), LAG = 0
   kcg --list
   ```
8. Chạy consumer với group **khác** → đọc lại **toàn bộ** từ đầu dù group cũ đã đọc (fan-out kiểu Kafka).

   ```bash
   GROUP=audit-app node consumer.mjs
   ```

### ✅ Kiểm chứng

- Producer in đúng `partition` cho từng key; cùng key → cùng partition; `baseOffset` của mỗi partition tăng 0,1,2… Đối chiếu với `kcc --topic payments --from-beginning --property print.partition=true --property print.key=true` → **cùng kết quả partition** (kafkajs mặc định dùng partitioner murmur2 tương thích Java).
- 2 consumer cùng group → tổng partition được gán = 3, không partition nào bị gán cho 2 consumer. 4 consumer → 1 consumer `partitions=[]`.
- Group `audit-app` đọc đủ 18 message (9 + 9) từ offset 0 dù `payments-app` đã đọc hết.

### 🧹 Dọn dẹp

```bash
# Ctrl+C mọi consumer
kt --delete --topic payments
kcg --delete --group payments-app
kcg --delete --group audit-app
```

### 🧠 Ý nghĩa với đề thi

- **Consumer ≤ partition** mới có ích; consumer dư idle. "Tăng throughput consumer" → tăng partition trước.
- 2 group `group.id` khác nhau = 2 ứng dụng độc lập, mỗi group giữ offset riêng trong `__consumer_offsets`.
- `fromBeginning` / `auto.offset.reset=earliest` chỉ áp dụng khi group **chưa có offset committed**; group đã có offset thì tiếp tục từ offset đó.
- `RecordMetadata` (`partition`, `baseOffset`) chỉ có khi `acks ≠ 0` — với `acks=0` producer không biết offset.
- `bootstrap.servers` ghi 3 broker nhưng client vẫn kết nối **trực tiếp leader** của từng partition sau khi có metadata.

---

## Lab 1.5 — Soi đĩa: segment, index và `__cluster_metadata`

**🎯 Mục tiêu:** Nhìn thấy "commit log" bằng mắt: thư mục partition, file `.log/.index/.timeindex`, nội dung record qua `kafka-dump-log.sh`, dung lượng qua `kafka-log-dirs.sh`; sau đó đọc **metadata log của KRaft** bằng `kafka-dump-log.sh --cluster-metadata-decoder` và duyệt bằng `kafka-metadata-shell.sh`.
**🧩 Luyện kỹ năng (liên quan đề):**

- Cấu trúc `log.dirs/<topic>-<partition>/<baseOffset>.log`, `.index` thưa, `.timeindex`, `leader-epoch-checkpoint`, `partition.metadata`.
- Segment roll theo `segment.bytes` / `segment.ms` (topic-level).
- `__cluster_metadata` là **topic 1 partition** chứa record kiểu `TOPIC_RECORD`, `PARTITION_RECORD`, `REGISTER_BROKER_RECORD`, `CONFIG_RECORD`…

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 1.2 đang chạy.

### Các bước

1. Tạo topic `logs` với **segment nhỏ (1 KB)** để ép roll segment nhanh, rồi bơm 200 message.

   ```bash
   kt --create --topic logs --partitions 1 --replication-factor 3 --config segment.bytes=1024 --config retention.ms=600000
   docker exec kafka-1 bash -c 'for i in $(seq 1 200); do echo "line-$i payload-$(head -c 20 /dev/urandom | base64)"; done | /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic logs'
   ```
2. Xem dung lượng partition trên từng broker.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-log-dirs.sh --bootstrap-server kafka-1:19092 --describe --topic-list logs | tail -1 | python3 -m json.tool | head -40
   # Mỗi broker 2,3,4 có 1 entry "logs-0" với "size" bằng nhau (đã replicate), "offsetLag": 0
   ```
3. `ls` thư mục partition trên broker leader — đếm segment.

   ```bash
   kt --describe --topic logs | grep Leader        # xem Leader: N → container kafka-(N-1)
   docker exec kafka-1 ls -la /tmp/kraft-combined-logs/logs-0/
   ```
   Output mẫu: nhiều bộ `<baseOffset>.log/.index/.timeindex` (ví dụ `00000000000000000000.*`, `00000000000000000011.*`, `00000000000000000023.*` …), cộng `leader-epoch-checkpoint`, `partition.metadata`. Segment **cuối** = active segment.
4. Dump nội dung 1 segment (record thật) và index.

   ```bash
   SEG=$(docker exec kafka-1 bash -c 'ls /tmp/kraft-combined-logs/logs-0/*.log | head -1')
   docker exec kafka-1 /opt/kafka/bin/kafka-dump-log.sh --files $SEG --print-data-log | head -20
   docker exec kafka-1 /opt/kafka/bin/kafka-dump-log.sh --files ${SEG%.log}.index | head
   docker exec kafka-1 /opt/kafka/bin/kafka-dump-log.sh --files ${SEG%.log}.timeindex | head
   ```
   Đọc output: dòng `baseOffset: 0 lastOffset: 0 count: 1 baseSequence: -1 ... producerId: -1 ... magic: 2 compresscodec: none crc: ... isvalid: true` là **RecordBatch header** (v2); dòng `| offset: 0 CreateTime: 175... keySize: -1 valueSize: 53 ... payload: line-1 ...` là record. `keySize: -1` = key null. `.index` in `offset: X position: Y` (thưa — không phải mọi offset đều có).
5. Xem **metadata log KRaft**. Broker cũng lưu bản sao `__cluster_metadata-0` (observer), controller là bản gốc.

   ```bash
   docker exec controller ls -la /tmp/kraft-combined-logs/__cluster_metadata-0/
   docker exec controller /opt/kafka/bin/kafka-dump-log.sh --cluster-metadata-decoder \
     --files /tmp/kraft-combined-logs/__cluster_metadata-0/00000000000000000000.log \
     | grep -oE '"type":"[A-Z_]+"' | sort | uniq -c | sort -rn | head -12
   ```
   Thấy các loại record: `REGISTER_BROKER_RECORD` (broker đăng ký), `BROKER_REGISTRATION_CHANGE_RECORD` (fence/unfence), `TOPIC_RECORD`, `PARTITION_RECORD`, `PARTITION_CHANGE_RECORD` (ISR/leader đổi), `CONFIG_RECORD`, `FEATURE_LEVEL_RECORD`, `NO_OP_RECORD` (heartbeat của Raft leader)…
6. Tìm chính topic `logs` trong metadata log.

   ```bash
   docker exec controller /opt/kafka/bin/kafka-dump-log.sh --cluster-metadata-decoder \
     --files /tmp/kraft-combined-logs/__cluster_metadata-0/00000000000000000000.log \
     | grep -E 'TOPIC_RECORD.*"name":"logs"' | head -2
   ```
7. Duyệt metadata như filesystem bằng `kafka-metadata-shell.sh` (đọc trực tiếp thư mục log; nếu đã có file `.checkpoint` có thể dùng `--snapshot <file>`).

   ```bash
   docker exec -it controller /opt/kafka/bin/kafka-metadata-shell.sh --directory /tmp/kraft-combined-logs/__cluster_metadata-0
   ```
   Trong shell:
   ```
   >> ls /
   >> ls /image
   >> ls /image/topics/byName
   >> cat /image/topics/byName/logs
   >> ls /image/brokers
   >> cat /image/brokers/2
   >> exit
   ```
   > 📌 Cây thư mục có thể khác nhẹ giữa phiên bản — cứ `ls` từng cấp để khám phá. Điểm cần thấy: metadata cluster (topics, brokers, configs, features) là **trạng thái dựng lại từ event log**, không phải lưu ở đâu khác.
8. (Tuỳ chọn) Quan sát retention xoá **cả segment**: đợi > 10 phút (`retention.ms=600000`) rồi `ls` lại thư mục — segment cũ biến mất, **active segment vẫn còn** dù record trong đó cũng đã quá hạn.

### ✅ Kiểm chứng

- Thư mục `logs-0` có ≥ 5 bộ segment vì `segment.bytes=1024`; tên file = base offset của record đầu tiên (không liên tục: 0, 11, 23…).
- `kafka-dump-log.sh` in được `payload: line-1`; `.index` có ít entry hơn số record (thưa theo `log.index.interval.bytes=4096` — với segment 1 KB thường chỉ 0–1 entry).
- `kafka-log-dirs.sh` cho `size` bằng nhau trên 3 broker → replication hoạt động.
- Metadata log có `TOPIC_RECORD` với `"name":"logs"` và `PARTITION_RECORD` với `replicas` 3 broker.

### 🧹 Dọn dẹp

```bash
kt --delete --topic logs
```

### 🧠 Ý nghĩa với đề thi

- Partition = thư mục; segment = file; record chỉ **append** vào active segment; đọc = binary search `.index` → seek vị trí byte trong `.log`.
- Retention/compaction thao tác trên **segment đã đóng**, không đụng active segment → dữ liệu có thể tồn tại lâu hơn `retention.ms`.
- `__cluster_metadata` = nguồn sự thật duy nhất của KRaft; controller mới bầu lên đã có sẵn state trong RAM (không load từ ZooKeeper) → failover nhanh.
- `kafka-dump-log.sh --cluster-metadata-decoder` và `kafka-metadata-shell.sh` là 2 tool debug KRaft được nêu trong docs Operations.

---

## Lab 1.6 — Kill 1 broker: leader đổi, ISR co lại rồi hồi

**🎯 Mục tiêu:** Tắt 1 broker đang làm leader → thấy controller bầu **leader mới trong ISR**, `Isr` còn 2, producer/consumer vẫn chạy (2 ≥ `min.insync.replicas=2`); tắt broker thứ 2 → producer `acks=all` **bị chặn** (`NotEnoughReplicas`); bật lại → ISR hồi đủ 3, leader **không tự quay về** ngay.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc `Leader / Replicas / Isr / Elr` trước–sau sự cố.
- Hiểu hành vi `min.insync.replicas` + `acks=all` (mở màn cho Tuần 2).
- Preferred leader & `auto.leader.rebalance.enable` (mặc định true, kiểm tra mỗi **300 s**).

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 1.2 đang chạy; đã dọn Lab 1.3–1.5.

### Các bước

1. Tạo topic thử nghiệm, ghi nhận leader ban đầu.

   ```bash
   kt --create --topic failover --partitions 3 --replication-factor 3
   kt --describe --topic failover
   ```
   Ghi lại `Leader` của từng partition (ví dụ p0→2, p1→3, p2→4; **preferred leader** = replica đầu tiên trong `Replicas`).
2. Mở **terminal 2**, chạy consumer CLI theo dõi liên tục.

   ```bash
   kcc --topic failover --group failover-watch --property print.partition=true --property print.offset=true
   ```
3. Mở **terminal 3**, chạy producer Node.js gửi 1 message/giây (giữ chạy suốt lab).

   ```bash
   cat > ~/kafka-labs/steady-producer.mjs <<'EOF'
   import { Kafka, logLevel } from "kafkajs";
   const kafka = new Kafka({ clientId: "steady", brokers: ["localhost:9092","localhost:9094","localhost:9096"], logLevel: logLevel.ERROR, retry: { retries: 3 } });
   const producer = kafka.producer();
   await producer.connect();
   let i = 0;
   setInterval(async () => {
     i++;
     try {
       const [m] = await producer.send({ topic: "failover", acks: -1, messages: [{ key: `k${i % 3}`, value: `msg-${i} ${new Date().toISOString()}` }] });
       console.log(`ok   msg-${i} -> p${m.partition} off=${m.baseOffset}`);
     } catch (e) {
       console.log(`FAIL msg-${i}: ${e.message}`);
     }
   }, 1000);
   EOF
   node ~/kafka-labs/steady-producer.mjs
   ```
4. **Terminal 1:** kill broker `kafka-3` (node 4) — cố tình chọn broker đang là leader của 1 partition.

   ```bash
   docker stop kafka-3
   sleep 5
   kt --describe --topic failover
   ```
   Output mẫu: partition từng có `Leader: 4` giờ `Leader: 2` (hoặc 3) — **chọn trong ISR**; mọi partition `Isr: 2,3` (mất 4); có thể thấy `Elr: 4` hoặc `LastKnownElr` nếu ELR bật.
   **Terminal 3:** vài giây có thể `FAIL ... leader not available`/timeout rồi tự phục hồi `ok` (kafkajs refresh metadata). **Terminal 2:** vẫn nhận message đều.
5. Kill thêm `kafka-2` (node 3) → chỉ còn 1 broker sống.

   ```bash
   docker stop kafka-2
   sleep 5
   kt --describe --topic failover      # Leader: 2 cho cả 3 partition, Isr: 2
   ```
   **Terminal 3:** mọi message **FAIL** với `NotEnoughReplicasException` (ISR=1 < `min.insync.replicas`=2, producer `acks=all`). **Terminal 2:** consumer vẫn **đọc được** dữ liệu cũ (đọc không bị `min.isr` chặn).
6. Bật lại 2 broker, quan sát ISR hồi.

   ```bash
   docker start kafka-2 kafka-3
   sleep 10
   kt --describe --topic failover      # Isr: 2,3,4 đủ lại, nhưng Leader vẫn 2 cho cả 3 partition
   ```
   **Terminal 3:** producer `ok` trở lại ngay khi ISR ≥ 2.
7. Leader **không tự cân bằng ngay**: `auto.leader.rebalance.enable=true` chỉ kiểm tra mỗi `leader.imbalance.check.interval.seconds=300`. Ép bầu lại preferred leader thủ công.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-leader-election.sh --bootstrap-server kafka-1:19092 \
     --election-type PREFERRED --all-topic-partitions
   kt --describe --topic failover      # Leader về đúng replica đầu trong Replicas
   ```
8. Xem lại sự kiện trong metadata log: mỗi lần ISR/leader đổi là 1 `PARTITION_CHANGE_RECORD`, mỗi lần broker chết/sống là `BROKER_REGISTRATION_CHANGE_RECORD`.

   ```bash
   docker exec controller bash -c '/opt/kafka/bin/kafka-dump-log.sh --cluster-metadata-decoder --files /tmp/kraft-combined-logs/__cluster_metadata-0/*.log' \
     | grep -cE 'PARTITION_CHANGE_RECORD|BROKER_REGISTRATION_CHANGE_RECORD'
   ```

### ✅ Kiểm chứng

- Sau bước 4: `Isr` mất node 4 trên **mọi** partition; leader mới **luôn** nằm trong ISR cũ; producer chỉ lỗi thoáng qua; consumer không mất message (offset liên tục).
- Sau bước 5: producer `acks=all` **fail 100%** vì ISR=1 < min.isr=2; consumer vẫn đọc.
- Sau bước 6: ISR về `2,3,4` trong < 30 s; bước 7 đưa leader về preferred.
- Không mất message: đếm `kcc --from-beginning --group verify --timeout-ms 5000 | wc -l` bằng số `ok` ở terminal 3.

### 🧹 Dọn dẹp

```bash
# Ctrl+C terminal 2 và 3
kt --delete --topic failover
kcg --delete --group failover-watch
kcg --delete --group verify 2>/dev/null
rm -f ~/kafka-labs/steady-producer.mjs
# Kết thúc tuần: tắt cluster (GIỮ 2 file compose + producer.mjs/consumer.mjs cho tuần sau)
docker compose -f ~/kafka-labs/docker-compose.cluster.yml down
```

### 🧠 Ý nghĩa với đề thi

- Broker chết → controller bầu leader **trong ISR** (không unclean); client tự refresh metadata và nối tới leader mới — không cần đổi `bootstrap.servers`.
- **Ghi** bị chặn khi `|ISR| < min.insync.replicas` với `acks=all` (`NotEnoughReplicasException` — retriable); **đọc** không bị ảnh hưởng.
- RF=3 + min.isr=2 → chịu **1** broker chết mà vẫn ghi được, **2** broker chết vẫn không mất dữ liệu committed nhưng ngừng ghi.
- Broker sống lại → follower fetch đuổi kịp → **tự vào lại ISR**; leader **không** tự quay về preferred ngay (đợi 300 s hoặc `kafka-leader-election.sh`).

---

> ✅ Xong 6 lab? Giữ lại `~/kafka-labs/docker-compose.single.yml`, `docker-compose.cluster.yml`, `producer.mjs`, `consumer.mjs` — Tuần 2 dùng tiếp. Đối chiếu [Lab checklist trong README](README.md#-lab-checklist) rồi làm [bộ câu hỏi luyện tập](questions.md) trước khi sang Tuần 2.
