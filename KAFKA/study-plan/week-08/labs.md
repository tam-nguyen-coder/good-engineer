# 🧪 Hands-on Labs — Tuần 8: Observability & Operations

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab (trừ khi lab sau nói "giữ").
> ⚙️ Yêu cầu chung: Docker Desktop, **Node.js 24**, cluster 3 node từ Tuần 1 (Lab 1.2), ~6 GB RAM trống (4 container Kafka + Prometheus + Grafana + cluster B ở Lab 8.6). Tổng ~3.5h.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../KAFKA-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab)

### 1) Khởi động cluster 3 broker + 1 controller (dùng lại compose của Tuần 1)

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d     # Lab 8.1 sẽ up lại kèm file monitoring
export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092        # cluster 3 node
```

> 📌 2 file compose chuẩn được định nghĩa ở [Tuần 1 — Lab 1.1 / 1.2](../week-01/labs.md). Tuần này **không in lại** cluster; phần thêm (JMX Exporter + Prometheus + Grafana) nằm trong file **override** `docker-compose.monitoring.yml` (Lab 8.1) và chạy chồng lên cluster bằng nhiều `-f`. Để khỏi gõ dài, đặt `COMPOSE_FILE` như Tuần 5:
>
> ```bash
> export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.monitoring.yml
> docker compose up -d        # = docker compose -f docker-compose.cluster.yml -f docker-compose.monitoring.yml up -d
> ```
>
> Mọi lệnh `docker compose` từ Lab 8.1 trở đi giả định đã `export COMPOSE_FILE` như trên. Cluster B (Lab 8.6) dùng project riêng `-p kafka-b -f docker-compose.cluster-b.yml` nên không bị ảnh hưởng.

### 2) Alias CLI — tuần này chạy từ container `controller`

Alias `kt/kcp/kcc/kcg/kcfg/kq/ksh` **giữ nguyên định nghĩa Tuần 1** (đọc `$KAFKA_CTR` và `$KAFKA_BS`). Nhưng từ Lab 8.1, 3 broker sẽ có `KAFKA_OPTS=-javaagent:...=7071:...` và `JMX_PORT=9999` trong môi trường container → **mọi JVM khởi động trong container broker** (kể cả `docker exec kafka-1 kafka-topics.sh` — vì `docker exec` kế thừa env của container và `kafka-run-class.sh` đọc `KAFKA_OPTS`/`JMX_PORT`) sẽ cố bind lại port 7071/9999 → `Address already in use` → tool chết. Cách gọn nhất: **chạy CLI từ container `controller`** (cùng image, cùng Docker network, không gắn javaagent):

```bash
export KAFKA_CTR=controller KAFKA_BS=kafka-1:19092    # CLI chạy trong controller, bootstrap tới broker kafka-1
kt --list                                             # kiểm tra kết nối (có thể rỗng)

# Alias thêm riêng cho tuần này (tool chưa có alias ở Tuần 1)
alias kperf='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh'
alias krp='docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-reassign-partitions.sh --bootstrap-server $KAFKA_BS'   # -i (không -t) để output không dính \r khi tee ra file
alias kle='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-leader-election.sh --bootstrap-server $KAFKA_BS'
alias kfeat='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-features.sh --bootstrap-server $KAFKA_BS'
alias koff='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_BS'
```

> 🧠 Đây chính là bẫy vận hành thật: `KAFKA_OPTS`/`JMX_PORT` áp cho **mọi** script trong `bin/`, không riêng broker. Production hay gặp lỗi "chạy `kafka-topics.sh` trên máy broker báo port 9999 đã dùng" — nguyên nhân là `JMX_PORT` đang export trong shell. Fix: `JMX_PORT= KAFKA_OPTS= kafka-topics.sh ...` hoặc chạy tool từ máy khác.

### 3) Project Node.js

```bash
mkdir -p ~/kafka-labs/week-08 && cd ~/kafka-labs/week-08
node -v                                   # v24.x
node -e "import('kafkajs').then(() => console.log('kafkajs OK'))"   # resolve từ ~/kafka-labs/node_modules (Tuần 1 đã npm i kafkajs@2)
```

Mọi file `.mjs` tuần này nằm trong `~/kafka-labs/week-08/`, dùng `brokers: ['localhost:9092','localhost:9094','localhost:9096']` khi chạy từ host. `kafkajs` không có JMX — metric phía client trong lab sẽ tự tính bằng Admin API (Lab 8.2); tên metric Java tương ứng được ghi trong comment để đối chiếu với đề.

---

## Lab 8.1 — JMX → Prometheus JMX Exporter → Prometheus → Grafana ⭐

**🎯 Mục tiêu:** Gắn `jmx_prometheus_javaagent` vào JVM của 3 broker (port **7071**) bằng file override `docker-compose.monitoring.yml`, viết rules YAML tối thiểu cho 6 nhóm metric "sống còn", thêm `prometheus` (9090) + `grafana` (3000), rồi **nhìn thấy** `UnderReplicatedPartitions`, `BytesInPerSec`, `TotalTimeMs{request="Produce"}` trên Grafana. Stack này **giữ chạy suốt tuần** (Lab 8.3 dùng lại) và giữ file cho Tuần 9–10.
**🧩 Luyện kỹ năng (liên quan đề):**

- Cách bật metric: `KAFKA_OPTS=-javaagent:<jar>=<port>:<rules.yml>` (không cần mở remote JMX ra ngoài) vs `JMX_PORT` (remote JMX cho `jconsole`/`JmxTool`).
- Đọc tên MBean `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` → viết rule regex `pattern` → `name`/`labels`/`type`.
- Phân biệt attribute: Gauge có `Value`; Meter (`*PerSec`) có `Count`/`OneMinuteRate`; Histogram/Timer (`TotalTimeMs`) có `Mean`/`99thPercentile`.
- `ActiveControllerCount` trong KRaft nằm trên **node controller**, không phải broker.

**⏱️ ~40 phút** · **Yêu cầu trước:** Chuẩn bị chung (cluster có thể đang chạy — bước 5 sẽ recreate).

### Các bước

1. Tải JMX Exporter (Java agent) từ Maven Central vào `~/kafka-labs/jmx/`.

   ```bash
   mkdir -p ~/kafka-labs/jmx ~/kafka-labs/prometheus ~/kafka-labs/grafana
   JMX_VER=1.0.1
   curl -fL -o ~/kafka-labs/jmx/jmx_prometheus_javaagent.jar \
     https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/${JMX_VER}/jmx_prometheus_javaagent-${JMX_VER}.jar
   ls -la ~/kafka-labs/jmx/           # jar ~1 MB
   ```

   > 📌 Muốn version mới hơn: xem https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/ và đổi `JMX_VER`. Từ 1.0.0 exporter yêu cầu Java 11+ — image `apache/kafka:4.3.1` chạy Java 21, OK.
2. Viết rules `~/kafka-labs/jmx/kafka-jmx.yml` (in đầy đủ — copy nguyên văn). Chỉ MBean **khớp rule** mới được export; phần còn lại bị bỏ → scrape nhẹ.

   ```yaml
   # ~/kafka-labs/jmx/kafka-jmx.yml — rules tối thiểu cho JMX Exporter (Lab 8.1)
   # Cú pháp pattern: <domain><key=value, key=value><>attribute  (thứ tự key = thứ tự trong ObjectName của Kafka: type rồi name)
   # $1/$2/$3 = nhóm bắt được trong regex. lowercaseOutputName → tên metric toàn chữ thường.
   lowercaseOutputName: true
   lowercaseOutputLabelNames: true
   rules:
     # 1) ReplicaManager (Gauge → attribute Value)
     #    kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions → kafka_server_replicamanager_underreplicatedpartitions
     - pattern: kafka.server<type=ReplicaManager, name=(UnderReplicatedPartitions|UnderMinIsrPartitionCount|AtMinIsrPartitionCount|PartitionCount|LeaderCount)><>Value
       name: kafka_server_replicamanager_$1
       type: GAUGE

     # 2) ISR shrink/expand (Meter → Count là COUNTER, OneMinuteRate là GAUGE)
     - pattern: kafka.server<type=ReplicaManager, name=(IsrShrinksPerSec|IsrExpandsPerSec)><>Count
       name: kafka_server_replicamanager_$1_count
       type: COUNTER
     - pattern: kafka.server<type=ReplicaManager, name=(IsrShrinksPerSec|IsrExpandsPerSec)><>OneMinuteRate
       name: kafka_server_replicamanager_$1_oneminuterate
       type: GAUGE

     # 3) Controller (KRaft: MBean này chỉ có trên node process.roles=controller — broker sẽ KHÔNG có)
     - pattern: kafka.controller<type=KafkaController, name=(OfflinePartitionsCount|ActiveControllerCount|PreferredReplicaImbalanceCount|FencedBrokerCount|ActiveBrokerCount)><>Value
       name: kafka_controller_kafkacontroller_$1
       type: GAUGE

     # 4) Thread idle — io thread (Meter, đọc OneMinuteRate) và network thread (Gauge)
     - pattern: kafka.server<type=KafkaRequestHandlerPool, name=RequestHandlerAvgIdlePercent><>OneMinuteRate
       name: kafka_server_kafkarequesthandlerpool_requesthandleravgidlepercent
       type: GAUGE
     - pattern: kafka.network<type=SocketServer, name=NetworkProcessorAvgIdlePercent><>Value
       name: kafka_network_socketserver_networkprocessoravgidlepercent
       type: GAUGE

     # 5) Throughput — toàn broker (không có topic=) và theo từng topic (label topic)
     - pattern: kafka.server<type=BrokerTopicMetrics, name=(BytesInPerSec|BytesOutPerSec|MessagesInPerSec)><>Count
       name: kafka_server_brokertopicmetrics_$1_count
       type: COUNTER
     - pattern: kafka.server<type=BrokerTopicMetrics, name=(BytesInPerSec|BytesOutPerSec|MessagesInPerSec)><>OneMinuteRate
       name: kafka_server_brokertopicmetrics_$1_oneminuterate
       type: GAUGE
     - pattern: kafka.server<type=BrokerTopicMetrics, name=(BytesInPerSec|BytesOutPerSec|MessagesInPerSec), topic=(.+)><>OneMinuteRate
       name: kafka_server_brokertopicmetrics_$1_oneminuterate
       labels:
         topic: "$2"
       type: GAUGE

     # 6) Request latency 5 pha (Histogram → Mean / 99thPercentile), label request=Produce|FetchConsumer|FetchFollower
     - pattern: kafka.network<type=RequestMetrics, name=(TotalTimeMs|RequestQueueTimeMs|LocalTimeMs|RemoteTimeMs|ResponseQueueTimeMs|ResponseSendTimeMs), request=(Produce|FetchConsumer|FetchFollower)><>(Mean|99thPercentile)
       name: kafka_network_requestmetrics_$1_$3
       labels:
         request: "$2"
       type: GAUGE
   ```
3. Viết config Prometheus (scrape 3 broker qua Docker network, port 7071 trong container) và datasource Grafana (provisioning tự động).

   ```yaml
   # ~/kafka-labs/prometheus/prometheus.yml
   global:
     scrape_interval: 5s
     evaluation_interval: 5s
   scrape_configs:
     - job_name: kafka-broker
       static_configs:
         - targets: ["kafka-1:7071", "kafka-2:7071", "kafka-3:7071"]
           labels:
             cluster: A
   ```

   ```yaml
   # ~/kafka-labs/grafana/datasource.yml — Grafana tự thêm datasource Prometheus khi khởi động
   apiVersion: 1
   datasources:
     - name: Prometheus
       type: prometheus
       access: proxy
       url: http://prometheus:9090
       isDefault: true
   ```
4. Tạo file override `~/kafka-labs/docker-compose.monitoring.yml` (in đầy đủ). File này **chỉ chứa phần thêm**: env + volume cho 3 broker, 2 service mới.

   ```yaml
   # ~/kafka-labs/docker-compose.monitoring.yml — override: JMX Exporter (javaagent) trên 3 broker + Prometheus + Grafana
   # Chạy chồng lên cluster Tuần 1:
   #   docker compose -f docker-compose.cluster.yml -f docker-compose.monitoring.yml up -d
   # Exporter: kafka-1 → http://localhost:7071/metrics · kafka-2 → :7072 · kafka-3 → :7073
   # Prometheus: http://localhost:9090 · Grafana: http://localhost:3000 (admin/admin)
   x-jmx-env: &jmx-env
     # Java agent đọc MBean trong JVM broker → HTTP /metrics port 7071 (không cần remote JMX)
     KAFKA_OPTS: -javaagent:/opt/jmx/jmx_prometheus_javaagent.jar=7071:/opt/jmx/kafka-jmx.yml
     # Remote JMX cho jconsole/JmxTool (Lab 8.3). Mặc định Kafka TẮT; bật bằng JMX_PORT. Không auth — chỉ dùng trong lab.
     JMX_PORT: "9999"

   x-jmx-volumes: &jmx-volumes
     - ./jmx:/opt/jmx:ro

   services:
     kafka-1:
       environment:
         <<: *jmx-env
         KAFKA_JMX_OPTS: -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=kafka-1
       volumes: *jmx-volumes
       ports:
         - "7071:7071"
     kafka-2:
       environment:
         <<: *jmx-env
         KAFKA_JMX_OPTS: -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=kafka-2
       volumes: *jmx-volumes
       ports:
         - "7072:7071"
     kafka-3:
       environment:
         <<: *jmx-env
         KAFKA_JMX_OPTS: -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=kafka-3
       volumes: *jmx-volumes
       ports:
         - "7073:7071"

     prometheus:
       image: prom/prometheus:v3.5.0
       container_name: prometheus
       ports:
         - "9090:9090"
       volumes:
         - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
       depends_on:
         - kafka-1
         - kafka-2
         - kafka-3

     grafana:
       image: grafana/grafana:12.1.0
       container_name: grafana
       ports:
         - "3000:3000"
       environment:
         GF_SECURITY_ADMIN_USER: admin
         GF_SECURITY_ADMIN_PASSWORD: admin
       volumes:
         - ./grafana/datasource.yml:/etc/grafana/provisioning/datasources/datasource.yml:ro
       depends_on:
         - prometheus
   ```

   > 📌 Compose **merge** override với file gốc: `environment` (map) được gộp thêm key, `ports`/`volumes` (list) được nối thêm. Image `apache/kafka` biến mọi env `KAFKA_*` thành `server.properties` **trừ** danh sách loại trừ gồm `KAFKA_OPTS`, `KAFKA_JMX_OPTS`, `KAFKA_HEAP_OPTS`… nên 2 biến này đi thẳng vào JVM như mong muốn.
5. Khởi động (3 broker sẽ được **recreate** vì env đổi → dữ liệu topic cũ trong `/tmp` container mất — đầu tuần nên không sao).

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.monitoring.yml
   docker compose up -d
   docker compose ps                                  # controller, kafka-1/2/3, prometheus, grafana đều running
   docker compose logs kafka-1 | grep -iE "Kafka Server started|jmx|javaagent" | tail -3
   ```
6. Kiểm chứng exporter trực tiếp bằng `curl`.

   ```bash
   curl -s localhost:7071/metrics | grep -E "^kafka_server" | head -20
   curl -s localhost:7071/metrics | grep underreplicated
   # kafka_server_replicamanager_underreplicatedpartitions 0.0
   for p in 7071 7072 7073; do echo -n "$p: "; curl -s localhost:$p/metrics | grep -E "^kafka_server_replicamanager_(partitioncount|leadercount) " | tr '\n' ' '; echo; done
   curl -s localhost:7071/metrics | grep -c "^jvm_"          # exporter kèm sẵn metric JVM (heap, GC)
   ```
7. Kiểm tra Prometheus đã scrape đủ 3 target và thử PromQL qua API.

   ```bash
   curl -s localhost:9090/api/v1/targets | grep -o '"health":"[a-z]*"' | sort | uniq -c     # 3 "up"
   curl -s 'localhost:9090/api/v1/query?query=sum(kafka_server_replicamanager_underreplicatedpartitions)' | head -c 300; echo
   ```
   Hoặc mở http://localhost:9090 → **Status → Target health** → 3 target UP; tab **Query** gõ `kafka_server_replicamanager_leadercount` → 3 series theo `instance`.
8. Bơm traffic để metric throughput/latency có số, rồi vẽ Grafana.

   ```bash
   kt --create --topic mon-demo --partitions 6 --replication-factor 3
   kperf --topic mon-demo --num-records 200000 --record-size 512 --throughput 20000 \
     --producer-props bootstrap.servers=$KAFKA_BS acks=all linger.ms=5      # chạy ~10 s
   ```
   Mở http://localhost:3000 (admin/admin) → **Dashboards → New → New dashboard → Add visualization** → chọn datasource `Prometheus` → dán từng PromQL (4 panel, đặt tên đúng metric để nhớ):

   | Panel | PromQL | Kiểu |
   |---|---|---|
   | `UnderReplicatedPartitions` (cluster) | `sum(kafka_server_replicamanager_underreplicatedpartitions)` | Stat, threshold đỏ khi > 0 |
   | `BytesInPerSec` theo broker | `kafka_server_brokertopicmetrics_bytesinpersec_oneminuterate` | Time series, legend `{{instance}}` |
   | `TotalTimeMs{request="Produce"}` p99 | `kafka_network_requestmetrics_totaltimems_99thpercentile{request="Produce"}` | Time series |
   | `RequestHandlerAvgIdlePercent` | `kafka_server_kafkarequesthandlerpool_requesthandleravgidlepercent` | Gauge, min 0 max 1, threshold 0.3 |

   Thêm panel thứ 5 (tùy chọn) mổ xẻ 5 pha: `kafka_network_requestmetrics_remotetimems_mean{request="Produce"}` cạnh `..._localtimems_mean` và `..._requestqueuetimems_mean` → thấy `RemoteTimeMs` chiếm phần lớn với `acks=all`.

### ✅ Kiểm chứng

- `curl localhost:7071/metrics | grep underreplicated` trả `kafka_server_replicamanager_underreplicatedpartitions 0.0`; `partitioncount` cộng 3 broker = tổng replica (mon-demo 6×3 = 18 + topic nội bộ).
- Prometheus **3 target UP**; PromQL `sum(...underreplicatedpartitions)` = 0.
- Grafana vẽ được `BytesInPerSec` nhảy lên ~10 MB/s trên 3 broker trong lúc `kperf` chạy và `TotalTimeMs{request="Produce"}` p99 có giá trị (vài ms → vài chục ms).
- `curl localhost:7071/metrics | grep activecontroller` **rỗng** trên cả 3 broker — đúng, vì cluster tách vai trò: active controller là node `controller` (KRaft), broker không có MBean `kafka.controller:type=KafkaController`. Muốn thấy `ActiveControllerCount = 1`: thêm cùng `environment`/`volumes`/port `7074:7071` cho service `controller` trong file override — nhưng khi đó CLI trong controller cũng bị javaagent → phải chạy `docker exec -e KAFKA_OPTS= -e JMX_PORT= controller ...`. Lab giữ controller sạch để CLI dùng được.
- **Thí nghiệm bẫy (2 phút):** `docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 --list` → lỗi `Address already in use`/`Port already in use: 9999` (JVM tool cố bind 7071 và 9999). `docker exec -e KAFKA_OPTS= -e JMX_PORT= kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 --list` → chạy được.

### 🧹 Dọn dẹp

```bash
kt --delete --topic mon-demo
# GIỮ stack monitoring chạy cho Lab 8.2–8.7. Cuối tuần mới: docker compose down -v (xem Lab 8.7)
```

### 🧠 Ý nghĩa với đề thi

- "Scrape Kafka metrics into Prometheus" → **JMX Exporter javaagent** (`-javaagent:...=7071:rules.yml`), không phải mở `JMX_PORT` cho Prometheus; `JMX_PORT`/`KAFKA_JMX_OPTS` là cho `jconsole`/`JmxTool`/remote JMX (mặc định **tắt**, **không auth**).
- Tên MBean phải thuộc: `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` (0), `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` (0) / `ActiveControllerCount` (tổng = 1), `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` (> 0.3), `kafka.network:type=RequestMetrics,name=TotalTimeMs,request=Produce`.
- Broker dùng Yammer Metrics (Gauge `Value`, Meter `Count`/`OneMinuteRate`, Histogram `Mean`/`99thPercentile`); client Java dùng Kafka Metrics (`*-rate` + `*-total`). `kafkajs` không có JMX.
- `KAFKA_OPTS` áp cho mọi script `bin/*.sh` → bẫy "port đã dùng" khi chạy CLI trên máy broker.

---

## Lab 8.2 — Tạo consumer lag & chẩn đoán bằng `kafka-consumer-groups.sh` + Admin API ⭐

**🎯 Mục tiêu:** Bơm 100.000 record bằng `kafka-producer-perf-test.sh`, chạy consumer `kafkajs` **cố tình chậm** (sleep 100 ms/record) → xem `LAG` tăng trong `kcg --describe`; viết `lag-watch.mjs` tính lag = LEO − committed bằng Admin API (khớp CLI); thêm instance thứ 2, 3 → tốc độ tiêu thụ tăng, lag giảm; chạy **5 consumer / 3 partition** → chứng minh 2 consumer idle (`#PARTITIONS 0`).
**🧩 Luyện kỹ năng (liên quan đề):**

- Định nghĩa lag = `LOG-END-OFFSET − CURRENT-OFFSET` (committed); đọc `kcg --describe`, `--state`, `--members --verbose`.
- CLI (committed offset) vs client `records-lag-max` (position đã fetch) — vì sao 2 số lệch nhau.
- Bảng nguyên nhân → xử lý: consumer chậm → thêm consumer **đến bằng số partition**; nhiều consumer hơn partition → **idle**, phải tăng partition.

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 8.1 đang chạy (để nhìn `BytesInPerSec`/`BytesOutPerSec` song song — không bắt buộc).

### Các bước

1. Tạo topic 3 partition và viết consumer chậm `slow-consumer.mjs`.

   ```bash
   kt --create --topic lag-demo --partitions 3 --replication-factor 3
   ```

   ```javascript
   // ~/kafka-labs/week-08/slow-consumer.mjs — Lab 8.2: consumer cố tình chậm để tạo lag
   import { Kafka, logLevel } from "kafkajs";

   const TOPIC = process.env.TOPIC ?? "lag-demo";
   const GROUP = process.env.GROUP ?? "lag-app";
   const SLEEP_MS = Number(process.env.SLEEP_MS ?? 100);          // "xử lý" 100 ms/record → tối đa ~10 rec/s mỗi consumer

   const kafka = new Kafka({
     clientId: `slow-consumer-${process.pid}`,                    // Java: client.id — hiện ở cột CLIENT-ID của kcg
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.WARN,
   });

   const consumer = kafka.consumer({
     groupId: GROUP,
     maxBytesPerPartition: 32 * 1024,   // Java: max.partition.fetch.bytes (mặc định 1 MB) — batch nhỏ để commit thường hơn
     sessionTimeout: 45000,             // Java: session.timeout.ms (mặc định 45 s từ 3.0)
     heartbeatInterval: 3000,           // Java: heartbeat.interval.ms
   });
   await consumer.connect();
   await consumer.subscribe({ topic: TOPIC, fromBeginning: true });

   consumer.on(consumer.events.GROUP_JOIN, ({ payload }) => {
     const assigned = payload.memberAssignment[TOPIC] ?? [];
     console.log(`[pid ${process.pid}] joined generation=${payload.generationId} partitions=[${assigned}]${assigned.length ? "" : "  <-- IDLE"}`);
   });

   let processed = 0;
   const t0 = Date.now();
   setInterval(() => {
     const rate = processed / ((Date.now() - t0) / 1000);
     console.log(`[pid ${process.pid}] processed=${processed} rate=${rate.toFixed(1)} rec/s`);
   }, 5000);

   await consumer.run({
     autoCommitInterval: 5000,          // Java: auto.commit.interval.ms (5 s) — CLI LAG chỉ nhích khi commit
     autoCommitThreshold: 50,
     eachMessage: async () => {
       await new Promise((r) => setTimeout(r, SLEEP_MS));         // mô phỏng user code chậm (poll-idle-ratio-avg ≈ 0)
       processed++;
     },
   });

   process.on("SIGINT", async () => { await consumer.disconnect(); process.exit(0); });
   ```
2. Viết `lag-watch.mjs` — tính lag từng partition bằng Admin API, in mỗi 2 giây.

   ```javascript
   // ~/kafka-labs/week-08/lag-watch.mjs — Lab 8.2: lag = LOG-END-OFFSET − committed offset (đúng như kcg --describe)
   import { Kafka, logLevel } from "kafkajs";

   const TOPIC = process.env.TOPIC ?? "lag-demo";
   const GROUP = process.env.GROUP ?? "lag-app";
   const kafka = new Kafka({ clientId: "lag-watch", brokers: ["localhost:9092", "localhost:9094", "localhost:9096"], logLevel: logLevel.ERROR });
   const admin = kafka.admin();
   await admin.connect();

   async function tick() {
     const [ends, committed] = await Promise.all([
       admin.fetchTopicOffsets(TOPIC),                              // high = LEO (log end offset) từng partition
       admin.fetchOffsets({ groupId: GROUP, topics: [TOPIC] }),     // committed offset của group ("-1" = chưa commit)
     ]);
     const cur = Object.fromEntries((committed[0]?.partitions ?? []).map((p) => [p.partition, Number(p.offset)]));
     let total = 0;
     const cols = ends
       .sort((a, b) => a.partition - b.partition)
       .map((e) => {
         const leo = Number(e.high);
         const c = cur[e.partition] ?? -1;
         const lag = c < 0 ? leo : leo - c;                          // chưa commit → lag = toàn bộ log
         total += lag;
         return `p${e.partition} LEO=${leo} committed=${c < 0 ? "-" : c} lag=${lag}`;
       });
     console.log(new Date().toISOString().slice(11, 19), cols.join(" | "), `TOTAL LAG=${total}`);
   }
   await tick();
   setInterval(tick, 2000);
   process.on("SIGINT", async () => { await admin.disconnect(); process.exit(0); });
   ```
3. **Terminal 1:** chạy 1 consumer. **Terminal 2:** chạy `lag-watch.mjs`.

   ```bash
   cd ~/kafka-labs/week-08 && node slow-consumer.mjs        # [pid ...] joined generation=1 partitions=[0,1,2]
   cd ~/kafka-labs/week-08 && node lag-watch.mjs            # TOTAL LAG=0
   ```
4. **Terminal 3:** bơm 100.000 record (khoảng 5–10 giây), rồi xem lag bằng CLI.

   ```bash
   kperf --topic lag-demo --num-records 100000 --record-size 200 --throughput -1 \
     --producer-props bootstrap.servers=$KAFKA_BS acks=all
   kcg --describe --group lag-app
   kcg --describe --group lag-app --state
   ```
   Output mẫu `--describe` (1 consumer giữ cả 3 partition, LAG tổng ≈ 100.000 và **giảm cực chậm** ~10 record/giây):
   ```
   GROUP    TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG    CONSUMER-ID                                  HOST            CLIENT-ID
   lag-app  lag-demo  0          51              33412           33361  slow-consumer-4101-9c2e...                   /192.168.65.1   slow-consumer-4101
   lag-app  lag-demo  1          50              33290           33240  slow-consumer-4101-9c2e...                   /192.168.65.1   slow-consumer-4101
   lag-app  lag-demo  2          50              33298           33248  slow-consumer-4101-9c2e...                   /192.168.65.1   slow-consumer-4101
   ```
   `--state` → `COORDINATOR (ID)  ASSIGNMENT-STRATEGY  STATE   #MEMBERS` = `... roundrobin Stable 1`.
   Terminal 2: `TOTAL LAG` khớp cột LAG của CLI (cùng nguồn: committed offset) — và **đứng yên tới 5 giây rồi nhảy một cục** (auto commit 5 s) dù consumer xử lý đều: đây là chênh lệch CLI vs `records-lag-max` phía client.
5. **Chẩn đoán → xử lý:** thêm consumer thứ 2 và thứ 3 (Terminal 4, 5 — hoặc chạy nền).

   ```bash
   cd ~/kafka-labs/week-08 && node slow-consumer.mjs &      # instance 2 → rebalance, generation=2, mỗi consumer 1–2 partition
   cd ~/kafka-labs/week-08 && node slow-consumer.mjs &      # instance 3 → generation=3, mỗi consumer đúng 1 partition
   kcg --describe --group lag-app --members --verbose
   ```
   Terminal 2: tốc độ giảm lag tăng từ ~20/2 s lên ~60/2 s (gấp 3). `--members --verbose` → 3 dòng, `#PARTITIONS` = 1/1/1, `ASSIGNMENT` = `lag-demo(0)`, `lag-demo(1)`, `lag-demo(2)`.
6. **Bẫy "nhiều consumer hơn partition":** thêm 2 instance nữa (tổng 5).

   ```bash
   cd ~/kafka-labs/week-08 && node slow-consumer.mjs &
   cd ~/kafka-labs/week-08 && node slow-consumer.mjs &
   sleep 5
   kcg --describe --group lag-app --members --verbose
   ```
   Output mẫu:
   ```
   CONSUMER-ID                 HOST            CLIENT-ID            #PARTITIONS  ASSIGNMENT
   slow-consumer-4101-...      /192.168.65.1   slow-consumer-4101   1            lag-demo(2)
   slow-consumer-4188-...      /192.168.65.1   slow-consumer-4188   1            lag-demo(0)
   slow-consumer-4190-...      /192.168.65.1   slow-consumer-4190   1            lag-demo(1)
   slow-consumer-4250-...      /192.168.65.1   slow-consumer-4250   0            -
   slow-consumer-4252-...      /192.168.65.1   slow-consumer-4252   0            -
   ```
   Hai tiến trình mới in `partitions=[]  <-- IDLE`; tốc độ giảm lag **không đổi** so với bước 5.
7. **Xử lý đúng:** tăng partition (nhớ bẫy phá key ordering — topic này không key nên OK) → 5 consumer đều có việc.

   ```bash
   kt --alter --topic lag-demo --partitions 5
   sleep 10      # consumer refresh metadata (kafkajs metadataMaxAge mặc định 5 phút — kafkajs thường rebalance khi thấy partition mới; nếu không, Ctrl+C 1 consumer để ép rebalance)
   kcg --describe --group lag-app --members --verbose        # 5 dòng #PARTITIONS = 1
   ```
   > 📌 Record cũ vẫn nằm ở partition 0–2; partition 3–4 chỉ có record **mới**. Tăng partition giúp consumer mới có việc với dữ liệu tới sau, không chia lại backlog cũ.
8. (Tùy chọn, 1 phút) Xả lag nhanh để thấy `TOTAL LAG` về 0: Ctrl+C/`kill` mọi consumer, chạy 1 consumer nhanh `SLEEP_MS=0 node slow-consumer.mjs` — hết trong ~10–20 giây.

### ✅ Kiểm chứng

- Sau bước 4: `kcg --describe` LAG tổng ≈ 100.000, `CONSUMER-ID` có giá trị (group active), `lag-watch.mjs` in **cùng số** với CLI (±1 chu kỳ commit).
- Sau bước 5: tốc độ tiêu thụ tổng gấp ~3 (nhìn `rate=` của 3 tiến trình cộng lại ≈ 30 rec/s) → lag giảm nhanh gấp 3.
- Sau bước 6: đúng **2 dòng `#PARTITIONS 0`** / `partitions=[]`, tổng tốc độ **không tăng**.
- Sau bước 7: 5 consumer đều có 1 partition.

### 🧹 Dọn dẹp

```bash
pkill -f slow-consumer.mjs; pkill -f lag-watch.mjs    # hoặc Ctrl+C từng terminal
kt --delete --topic lag-demo
kcg --delete --group lag-app
```

### 🧠 Ý nghĩa với đề thi

- **Lag = LEO − committed offset**, đo per partition; CLI `kcg --describe` là snapshot theo committed → luôn "trễ" hơn client `records-lag-max` (theo position) tối đa 1 chu kỳ `auto.commit.interval.ms` (5 s). Không đo được lag của consumer dùng `assign()`.
- "Lag tăng đều, consumer xử lý chậm" → thêm consumer **tới bằng số partition**, tối ưu user code (`poll-idle-ratio-avg` ≈ 0). "Đã thêm consumer mà không nhanh hơn" → kiểm tra `assigned-partitions = 0` / `#PARTITIONS 0` → **tăng partition** (hoặc bớt consumer).
- Hot partition (1 key chiếm đa số) không giải được bằng thêm consumer — sửa key/partitioner (Lab 3.3).
- `CONSUMER-ID` = `-` → không ai giữ partition (group inactive) — khác với consumer idle (có ID nhưng `#PARTITIONS 0`).

---

## Lab 8.3 — `UnderReplicatedPartitions` & ISR shrink khi kill broker

**🎯 Mục tiêu:** Đọc **cùng một metric** bằng 3 cách: `curl` JMX Exporter, `JmxTool` qua remote JMX (`JMX_PORT=9999`), và Grafana; thấy `UnderReplicatedPartitions` từ 0 → >0 khi `docker stop kafka-3`, `IsrShrinksPerSec` nhích lên, `kt --describe` ISR co lại; bật lại → ISR hồi, URP về 0, `IsrExpandsPerSec` nhích.
**🧩 Luyện kỹ năng (liên quan đề):**

- URP là metric **per-broker** đếm partition mà broker này làm leader và |ISR| < |replicas| → cluster URP = **sum**.
- `kafka-run-class.sh org.apache.kafka.tools.JmxTool --jmx-url ... --object-name ...` (tên cũ `kafka.tools.JmxTool` đã bỏ ở 4.0).
- `kt --describe --under-replicated-partitions` là "URP bằng CLI" — dùng trong rolling restart (Lab 8.7).

**⏱️ ~20 phút** · **Yêu cầu trước:** Lab 8.1 đang chạy; `KAFKA_CTR=controller`.

### Các bước

1. Tạo topic, ghi ít dữ liệu, ghi nhận baseline URP = 0 trên cả 3 exporter.

   ```bash
   kt --create --topic urp-demo --partitions 3 --replication-factor 3
   kperf --topic urp-demo --num-records 20000 --record-size 256 --throughput -1 --producer-props bootstrap.servers=$KAFKA_BS acks=all | tail -1
   kt --describe --topic urp-demo                     # Isr đủ 3 node (2,3,4)
   for p in 7071 7072 7073; do echo -n "exporter $p: "; curl -s localhost:$p/metrics | grep "^kafka_server_replicamanager_underreplicatedpartitions "; done
   ```
2. Đọc cùng metric bằng `JmxTool` (remote JMX của kafka-1, chạy từ container `controller` — không có `JMX_PORT` nên tool không bị đụng port).

   ```bash
   docker exec controller /opt/kafka/bin/kafka-run-class.sh org.apache.kafka.tools.JmxTool \
     --jmx-url service:jmx:rmi:///jndi/rmi://kafka-1:9999/jmxrmi \
     --object-name kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions \
     --one-time true
   ```
   Output mẫu (CSV: header rồi 1 dòng giá trị):
   ```
   "time","kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions:Value"
   1757900000123,0
   ```
   Xem thêm ISR shrink/expand (Meter có nhiều attribute → lọc bằng `--attributes`):
   ```bash
   docker exec controller /opt/kafka/bin/kafka-run-class.sh org.apache.kafka.tools.JmxTool \
     --jmx-url service:jmx:rmi:///jndi/rmi://kafka-1:9999/jmxrmi \
     --object-name kafka.server:type=ReplicaManager,name=IsrShrinksPerSec --attributes Count,OneMinuteRate --one-time true
   ```
3. **Kill broker `kafka-3`** (node 4) rồi quan sát trong 30 giây.

   ```bash
   docker stop kafka-3
   sleep 8
   kt --describe --topic urp-demo                     # mọi partition Isr: 2,3 (mất 4); partition từng có Leader: 4 giờ Leader 2 hoặc 3
   kt --describe --under-replicated-partitions        # liệt kê MỌI partition thiếu ISR trong cluster (kể cả __consumer_offsets, mon-demo…)
   for p in 7071 7072; do echo -n "exporter $p: "; curl -s localhost:$p/metrics | grep "^kafka_server_replicamanager_underreplicatedpartitions "; done
   curl -s localhost:7073/metrics >/dev/null || echo "exporter 7073: kafka-3 đã tắt → Prometheus target DOWN"
   curl -s localhost:7071/metrics | grep -E "^kafka_server_replicamanager_isr(shrinks|expands)persec_(count|oneminuterate)"
   ```
   Output mẫu: `7071: ... 34.0`, `7072: ... 31.0` — hai broker sống chia nhau làm leader của mọi partition có replica trên node 4; tổng = số partition thiếu ISR toàn cluster (≥ 3 của `urp-demo` + 50 của `__consumer_offsets` + …). `isrshrinkspersec_count` tăng đúng bằng số partition mà broker đó làm leader và vừa co ISR; `oneminuterate` > 0 rồi tự trôi về 0.
4. Lặp lại `JmxTool` bước 2 → giá trị > 0. Trong Grafana, panel `sum(kafka_server_replicamanager_underreplicatedpartitions)` nhảy lên (Stat đỏ); **Status → Target health** trên Prometheus: `kafka-3:7071` DOWN.
5. Xem URP với PromQL theo broker: `kafka_server_replicamanager_underreplicatedpartitions` (2 series) và `kafka_controller_kafkacontroller_...` **không có** (controller không gắn exporter). Thay vào đó xem log controller:

   ```bash
   docker logs controller 2>&1 | grep -iE "fenc|unregister|shutdown" | tail -5     # broker 4 bị fence sau khi hết broker.session.timeout.ms (9 s) / controlled shutdown
   ```
6. **Bật lại** broker, đợi follower đuổi kịp.

   ```bash
   docker start kafka-3
   sleep 15
   kt --describe --topic urp-demo                     # Isr: 2,3,4 đủ; Leader CHƯA quay về 4 (đợi 300 s hoặc Lab 8.4 bước preferred election)
   kt --describe --under-replicated-partitions        # rỗng
   for p in 7071 7072 7073; do echo -n "exporter $p: "; curl -s localhost:$p/metrics | grep "^kafka_server_replicamanager_underreplicatedpartitions "; done
   curl -s localhost:7071/metrics | grep -E "^kafka_server_replicamanager_isrexpandspersec_count"    # tăng bằng số partition vừa nở ISR
   ```

### ✅ Kiểm chứng

- Trước: URP = 0 trên cả 3 exporter và `JmxTool`. Sau `docker stop kafka-3` (≤ 10 s): URP > 0 trên 2 broker sống, `--under-replicated-partitions` liệt kê nhiều dòng, `IsrShrinksPerSec.Count` tăng, Grafana Stat đỏ, target `kafka-3` DOWN.
- Sau `docker start kafka-3` (≤ 30 s): URP về 0 ở mọi nơi, `IsrExpandsPerSec.Count` tăng, `--under-replicated-partitions` rỗng.
- Cùng một MBean cho **cùng số** ở exporter (`curl`) và `JmxTool` — exporter chỉ là cách đọc MBean qua HTTP, không phải nguồn khác.

### 🧹 Dọn dẹp

```bash
docker start kafka-3 2>/dev/null || true
kt --delete --topic urp-demo
```

### 🧠 Ý nghĩa với đề thi

- `UnderReplicatedPartitions` > 0 kéo dài = broker chết hoặc follower tụt quá `replica.lag.time.max.ms` (30 s); là **metric số 1 phải alert**. Phân biệt với `UnderMinIsrPartitionCount` (chặn ghi `acks=all`) và `OfflinePartitionsCount` (không có leader → mất cả đọc).
- `IsrShrinksPerSec`/`IsrExpandsPerSec` bình thường 0; nhích lúc broker up/down là bình thường; **dao động liên tục** = ISR flapping (GC pause, disk/network chậm).
- Broker sống lại **tự vào ISR**, nhưng leadership **không** tự quay về ngay (`leader.imbalance.check.interval.seconds` = 300).
- Trong KRaft, `ActiveControllerCount`/`OfflinePartitionsCount` là MBean của **controller node**; cluster tách vai trò phải monitor cả controller.

---

## Lab 8.4 — Partition reassignment: `--generate` → `--execute --throttle` → `--verify` ⭐

**🎯 Mục tiêu:** Topic 6 partition RF 2 rải trên 3 broker; **giả lập decommission broker node 4** (`kafka-3`): sinh plan bằng `--generate --topics-to-move-json-file --broker-list 2,3`, chạy `--execute --throttle 1000000` (1 MB/s) và **nhìn thấy** config throttle động, theo dõi `--verify` tới `completed` + `Clearing ... throttles`, rồi trả leader về preferred bằng `kafka-leader-election.sh`.
**🧩 Luyện kỹ năng (liên quan đề):**

- 3 mode loại trừ nhau của `kafka-reassign-partitions.sh`; output `--generate` in **current** (lưu để rollback) + **proposed**.
- Throttle sinh config động `leader.replication.throttled.rate`/`follower.replication.throttled.rate` (broker) + `*.replication.throttled.replicas` (topic); **`--verify` mới gỡ**.
- Node id của cluster này: controller = 1, broker = **2, 3, 4** (docs ví dụ `--broker-list "5,6"`; đừng gõ `1,2` — node 1 là controller-only, không nhận partition).

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 8.1 đang chạy, 3 broker sống; `KAFKA_CTR=controller`.

### Các bước

1. Tạo topic 6 partition RF 2, bơm ~60 MB để reassignment **có gì để copy** (nhìn thấy throttle), ghi nhận assignment ban đầu.

   ```bash
   kt --create --topic reassign-demo --partitions 6 --replication-factor 2
   kperf --topic reassign-demo --num-records 60000 --record-size 1024 --throughput -1 \
     --producer-props bootstrap.servers=$KAFKA_BS acks=all | tail -1
   kt --describe --topic reassign-demo
   ```
   Output mẫu — 12 replica rải 3 broker, mỗi broker ~4 replica, node 4 xuất hiện ở ~4 partition:
   ```
   Topic: reassign-demo  Partition: 0  Leader: 2  Replicas: 2,3  Isr: 2,3 ...
   Topic: reassign-demo  Partition: 1  Leader: 3  Replicas: 3,4  Isr: 3,4 ...
   Topic: reassign-demo  Partition: 2  Leader: 4  Replicas: 4,2  Isr: 4,2 ...
   ...
   ```
2. Viết `topics-to-move.json` **trong container** `controller` (tool đọc file trong container) và chạy `--generate` với `--broker-list 2,3` (bỏ node 4).

   ```bash
   docker exec -i controller bash -c 'cat > /tmp/topics-to-move.json' <<'EOF'
   {"version":1,"topics":[{"topic":"reassign-demo"}]}
   EOF
   krp --topics-to-move-json-file /tmp/topics-to-move.json --broker-list 2,3 --generate | tee ~/kafka-labs/week-08/gen.txt
   ```
   Output mẫu:
   ```
   Current partition replica assignment
   {"version":1,"partitions":[{"topic":"reassign-demo","partition":0,"replicas":[2,3],"log_dirs":["any","any"]},...]}

   Proposed partition reassignment configuration
   {"version":1,"partitions":[{"topic":"reassign-demo","partition":0,"replicas":[3,2],"log_dirs":["any","any"]},...]}
   ```
   **Chưa có gì di chuyển** — `--generate` chỉ in. Tách 2 JSON ra file (current = bản rollback):
   ```bash
   cd ~/kafka-labs/week-08
   awk '/^Current partition replica assignment/{f=1;next} /^Proposed partition reassignment/{f=0} f && NF' gen.txt > current.json
   awk '/^Proposed partition reassignment/{f=1;next} f && NF' gen.txt > reassign.json
   node -e "for (const f of ['current.json','reassign.json']) { const j = JSON.parse(require('fs').readFileSync(f,'utf8')); console.log(f, j.partitions.length, 'partitions; brokers used:', [...new Set(j.partitions.flatMap(p => p.replicas))].sort()); }"
   # current.json 6 partitions; brokers used: [ 2, 3, 4 ]
   # reassign.json 6 partitions; brokers used: [ 2, 3 ]
   docker cp reassign.json controller:/tmp/reassign.json
   docker cp current.json  controller:/tmp/current.json
   ```
3. `--execute` với throttle **1 MB/s** (cố tình thấp để reassignment kéo dài ~30–60 s, đủ thời gian quan sát).

   ```bash
   krp --reassignment-json-file /tmp/reassign.json --execute --throttle 1000000
   ```
   Output mẫu:
   ```
   Current partition replica assignment
   {...}
   Save this to use as the --reassignment-json-file option during rollback
   Warning: You must run --verify periodically, until the reassignment completes, to ensure the throttle is removed.
   The inter-broker throttle limit was set to 1000000 B/s
   Successfully started partition reassignments for reassign-demo-0,reassign-demo-1,...,reassign-demo-5
   ```
4. **Trong lúc đang chạy** (mở terminal khác thật nhanh), soi 3 thứ: config throttle động, ISR tạm thời có 3 replica (replica mới đang đuổi), metric reassignment.

   ```bash
   kcfg --describe --entity-type brokers --entity-name 2      # leader.replication.throttled.rate=1000000, follower.replication.throttled.rate=1000000 (DYNAMIC_BROKER_CONFIG)
   kcfg --describe --entity-type topics --entity-name reassign-demo
   # leader.replication.throttled.replicas=0:2,0:3,1:3,1:4,...  follower.replication.throttled.replicas=1:2,2:3,...
   kt --describe --topic reassign-demo                         # partition đang chuyển: Replicas: 3,2,4 (3 replica!) Isr: 3,4 hoặc 3,4,2 — "Adding replicas / Removing replicas" hiện ở dòng partition
   krp --reassignment-json-file /tmp/reassign.json --verify    # "is still in progress" cho vài partition
   curl -s localhost:7071/metrics | grep -iE "reassign" | head    # (chỉ có nếu bạn thêm rule cho ReassigningPartitions / ReassignmentBytesInPerSec — tùy chọn)
   ```
5. Lặp `--verify` tới khi mọi partition `completed` — **chính lệnh này gỡ throttle**.

   ```bash
   while krp --reassignment-json-file /tmp/reassign.json --verify | tee /dev/stderr | grep -q "still in progress"; do sleep 5; done
   # (hoặc đơn giản: chạy tay lệnh --verify mỗi 10 giây tới khi hết dòng "still in progress")
   ```
   Output mẫu khi xong:
   ```
   Status of partition reassignment:
   Reassignment of partition reassign-demo-0 is completed.
   ...
   Reassignment of partition reassign-demo-5 is completed.

   Clearing broker-level throttles on brokers 2,3,4
   Clearing topic-level throttles on topic reassign-demo
   ```
   Kiểm tra throttle đã biến mất:
   ```bash
   kcfg --describe --entity-type brokers --entity-name 2       # không còn *.replication.throttled.rate
   kcfg --describe --entity-type topics --entity-name reassign-demo   # không còn *.throttled.replicas
   kt --describe --topic reassign-demo                         # Replicas chỉ còn 2,3 — node 4 KHÔNG còn replica nào của topic
   ```
6. Leader sau reassignment thường không phải preferred (replica đầu danh sách). Trả leader về preferred bằng `kafka-leader-election.sh`.

   ```bash
   kt --describe --topic reassign-demo | grep -E "Leader" | awk '{print "p"$4" leader="$6" preferred="substr($8,1,1)}'
   kle --election-type preferred --all-topic-partitions
   kt --describe --topic reassign-demo                         # Leader == replica đầu tiên trong Replicas ở mọi partition
   ```
   Output `kle`: `Successfully completed leader election (PREFERRED) for partitions reassign-demo-1, ...` (hoặc `Valid replica already elected for partitions ...` với partition đã đúng).
7. (Tùy chọn 3 phút) **Rollback** để thấy `--execute` với file current: `docker cp` đã có `/tmp/current.json` → `krp --reassignment-json-file /tmp/current.json --execute` (không throttle) → `--verify` → node 4 có replica lại. Hoặc tăng RF lên 3 bằng JSON viết tay `"replicas":[2,3,4]` cho 1 partition rồi `--execute` — cùng tool, cùng flow.

### ✅ Kiểm chứng

- `--generate` in **2 JSON** (current + proposed); `reassign.json` chỉ dùng broker `[2,3]`.
- Trong lúc `--execute --throttle 1000000`: `kcfg --describe brokers` có `leader.replication.throttled.rate=1000000`; topic có `*.replication.throttled.replicas`; `--verify` báo `still in progress`; `kt --describe` có partition tạm 3 replica.
- `--verify` cuối báo `completed` cho 6 partition **và** `Clearing broker-level throttles on brokers 2,3,4` + `Clearing topic-level throttles`; config throttle biến mất; node 4 không còn replica.
- Sau `kle --election-type preferred --all-topic-partitions`: `Leader` = replica đầu tiên ở mọi partition.

### 🧹 Dọn dẹp

```bash
# ĐẢM BẢO throttle đã gỡ (nếu bạn bỏ qua --verify, chạy lại lệnh này — đây là "gỡ throttle" đúng cách)
krp --reassignment-json-file /tmp/reassign.json --verify | grep -E "Clearing|completed" | tail -3
# Nếu vẫn còn config throttle vì lý do nào đó → xoá tay:
kcfg --alter --entity-type brokers --entity-name 2 --delete-config leader.replication.throttled.rate,follower.replication.throttled.rate 2>/dev/null
kcfg --alter --entity-type brokers --entity-name 3 --delete-config leader.replication.throttled.rate,follower.replication.throttled.rate 2>/dev/null
kcfg --alter --entity-type brokers --entity-name 4 --delete-config leader.replication.throttled.rate,follower.replication.throttled.rate 2>/dev/null
kt --delete --topic reassign-demo
docker exec controller rm -f /tmp/topics-to-move.json /tmp/reassign.json /tmp/current.json
rm -f ~/kafka-labs/week-08/gen.txt ~/kafka-labs/week-08/current.json ~/kafka-labs/week-08/reassign.json
```

### 🧠 Ý nghĩa với đề thi

- Thêm/bớt broker **không** tự cân bằng partition; broker mới chỉ nhận topic **tạo sau**. Phải `--generate` → `--execute [--throttle]` → `--verify`, hoặc dùng **Cruise Control** (goal-based, REST 9090).
- `--throttle` là byte/giây **liên broker**; throttle < tốc độ ghi vào (`BytesInPerSec`) → **không bao giờ xong**; đổi giữa chừng bằng `--additional --execute --throttle N`. Quên `--verify` = throttle còn nguyên và bóp cả replication thường.
- Cùng tool làm được: tăng RF (thêm replica vào JSON), đổi log dir (`log_dirs` + `--replica-alter-log-dirs-throttle`), decommission (reassign hết ra rồi `kafka-cluster.sh unregister`; 4.3 có `cordoned.log.dirs` KIP-1066 chặn controller đặt partition mới lên broker sắp bỏ).
- Reassignment đổi **replica**; `kafka-leader-election.sh --election-type preferred` chỉ đổi **leader** (không copy data). "Sau rolling restart, 1 broker gánh hết leader" → election, không phải reassign.

---

## Lab 8.5 — Poison pill: consumer kẹt vòng lặp → DLQ với header lý do

**🎯 Mục tiêu:** Gửi 1 record JSON hỏng vào `orders`; consumer `kafkajs` v1 `JSON.parse` ném lỗi → quan sát kafkajs **retry rồi crash → restart → đọc lại đúng record đó** (kẹt vô hạn, offset không tiến, lag không giảm). Viết v2: `try/catch` → gửi record lỗi sang `orders-dlq` kèm header `error`, `originalTopic`, `originalPartition`, `originalOffset` rồi **đi tiếp**; xem DLQ bằng console consumer với `print.headers`.
**🧩 Luyện kỹ năng (liên quan đề):**

- Poison pill = `SerializationException`/`RecordDeserializationException` phía consumer (Java ném từ `poll()`); offset không commit → poll lại → crash loop. `auto.offset.reset` **không** cứu được (group đã có offset).
- 3 cách fix: `seek(offset+1)`, **DLQ + header lý do**, `ErrorHandlingDeserializer` (Spring) / try-catch quanh parse (kafkajs).
- Header không ảnh hưởng partition; mang metadata chẩn đoán (topic/partition/offset gốc, lỗi).

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung; `KAFKA_CTR=controller`.

### Các bước

1. Tạo topic `orders` và `orders-dlq`; nạp 5 record — record thứ 3 **hỏng**.

   ```bash
   kt --create --topic orders     --partitions 3 --replication-factor 3
   kt --create --topic orders-dlq --partitions 3 --replication-factor 3
   docker exec -i controller /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 \
     --topic orders --property parse.key=true --property key.separator=: <<'EOF'
   o1:{"id":1,"amount":10}
   o2:{"id":2,"amount":20}
   o3:{"id":3,"amount":  <<< NOT-JSON
   o4:{"id":4,"amount":40}
   o5:{"id":5,"amount":50}
   EOF
   kcc --topic orders --from-beginning --property print.key=true --property print.partition=true --timeout-ms 5000
   ```
2. Viết consumer **v1** (naive) `poison-consumer-v1.mjs`.

   ```javascript
   // ~/kafka-labs/week-08/poison-consumer-v1.mjs — Lab 8.5: consumer KHÔNG xử lý lỗi parse → poison pill
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "orders-consumer-v1",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.INFO,                          // để thấy log retry/crash của kafkajs
     retry: { initialRetryTime: 300, retries: 3 },     // rút ngắn để crash loop hiện nhanh (mặc định retries 5)
   });
   const consumer = kafka.consumer({ groupId: "orders-app-v1" });
   await consumer.connect();
   await consumer.subscribe({ topic: "orders", fromBeginning: true });

   consumer.on(consumer.events.CRASH, ({ payload }) => {
     console.log(`>>> CRASH: ${payload.error.name}: ${payload.error.message} — restart=${payload.restart}`);
   });

   await consumer.run({
     eachMessage: async ({ partition, message }) => {
       const order = JSON.parse(message.value.toString());   // record hỏng → SyntaxError → kafkajs coi là lỗi xử lý
       console.log(`ok  p${partition} off=${message.offset} key=${message.key} id=${order.id} amount=${order.amount}`);
     },
   });
   process.on("SIGINT", async () => { await consumer.disconnect(); process.exit(0); });
   ```
3. Chạy v1 và quan sát ~30 giây.

   ```bash
   cd ~/kafka-labs/week-08 && node poison-consumer-v1.mjs
   ```
   Output mẫu (rút gọn):
   ```
   ok  p1 off=0 key=o1 id=1 amount=10
   ok  p0 off=0 key=o2 id=2 amount=20
   {"level":"ERROR","logger":"kafkajs","message":"[Runner] Error when calling eachMessage","topic":"orders","partition":2,"offset":"0","stack":"SyntaxError: Unexpected token '<'...","retryCount":0,"retryTime":300}
   {"level":"ERROR",... "retryCount":1,"retryTime":6xx}
   {"level":"ERROR",... "retryCount":2 ...}
   {"level":"ERROR",... "retryCount":3 ...}
   {"level":"ERROR","logger":"kafkajs","message":"[Consumer] Crash: KafkaJSNumberOfRetriesExceeded: Unexpected token ...","groupId":"orders-app-v1","retryCount":3}
   >>> CRASH: KafkaJSNumberOfRetriesExceeded: Unexpected token ... — restart=true
   {"level":"INFO","logger":"kafkajs","message":"[Consumer] Restarting the consumer in 4xxms"}
   ... (join lại group, generation tăng) ...
   {"level":"ERROR",... "[Runner] Error when calling eachMessage" ... "offset":"0" ...}   ← ĐÚNG record đó, lặp lại mãi
   ```
   Mở terminal khác: `kcg --describe --group orders-app-v1` → partition chứa `o3`: `CURRENT-OFFSET` **không tiến** (`-` hoặc đứng), LAG không giảm; 2 partition kia đã xong. Ctrl+C sau khi thấy vòng lặp thứ 2.
4. Viết **v2** `poison-consumer-v2.mjs`: try/catch quanh parse + validate, lỗi → gửi DLQ với header rồi `return` (offset tiến bình thường).

   ```javascript
   // ~/kafka-labs/week-08/poison-consumer-v2.mjs — Lab 8.5: try/catch + Dead Letter Queue kèm header lý do
   import { Kafka, logLevel } from "kafkajs";

   const TOPIC = "orders", DLQ = "orders-dlq";
   const kafka = new Kafka({
     clientId: "orders-consumer-v2",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.WARN,
   });
   const consumer = kafka.consumer({ groupId: "orders-app-v2" });       // group MỚI → đọc lại từ đầu (fromBeginning)
   const producer = kafka.producer();                                    // producer riêng để ghi DLQ
   await Promise.all([consumer.connect(), producer.connect()]);
   await consumer.subscribe({ topic: TOPIC, fromBeginning: true });

   function parseOrder(buf) {                                            // "deserializer" + validate nghiệp vụ
     const o = JSON.parse(buf.toString());                               // ném SyntaxError nếu không phải JSON
     if (typeof o.id !== "number" || typeof o.amount !== "number") throw new Error("schema violation: id/amount must be numbers");
     return o;
   }

   let ok = 0, dead = 0;
   await consumer.run({
     eachMessage: async ({ topic, partition, message }) => {
       let order;
       try {
         order = parseOrder(message.value);
       } catch (err) {
         dead++;
         await producer.send({                                           // Java: KafkaProducer.send(new ProducerRecord(DLQ, key, value, headers))
           topic: DLQ,
           acks: -1,
           messages: [{
             key: message.key,                                           // giữ key/value gốc nguyên vẹn để replay sau
             value: message.value,
             headers: {
               ...message.headers,                                       // giữ header gốc (nếu có)
               error: `${err.name}: ${err.message}`,
               originalTopic: topic,
               originalPartition: String(partition),
               originalOffset: String(message.offset),
               failedAt: new Date().toISOString(),
             },
           }],
         });
         console.log(`DLQ p${partition} off=${message.offset} key=${message.key} -> ${DLQ}: ${err.message}`);
         return;                                                         // return bình thường → kafkajs resolve offset → đi tiếp record kế
       }
       ok++;
       console.log(`ok  p${partition} off=${message.offset} key=${message.key} id=${order.id} amount=${order.amount}`);
     },
   });

   setInterval(() => console.log(`--- ok=${ok} dlq=${dead}`), 10000);
   process.on("SIGINT", async () => { await consumer.disconnect(); await producer.disconnect(); process.exit(0); });
   ```
5. Chạy v2; xem DLQ với header; xem lag của group v2.

   ```bash
   cd ~/kafka-labs/week-08 && node poison-consumer-v2.mjs
   # ok  p1 off=0 key=o1 id=1 amount=10
   # ok  p0 off=0 key=o2 id=2 amount=20
   # DLQ p2 off=0 key=o3 -> orders-dlq: Unexpected token '<', ... is not valid JSON
   # ok  ... id=4 ... / ok ... id=5 ...
   ```
   Terminal khác:
   ```bash
   kcc --topic orders-dlq --from-beginning --property print.headers=true --property print.key=true --property print.partition=true --timeout-ms 5000
   # error:SyntaxError: Unexpected token '<'...,originalTopic:orders,originalPartition:2,originalOffset:0,failedAt:2026-...  Partition:2  o3  {"id":3,"amount":  <<< NOT-JSON
   kcg --describe --group orders-app-v2      # LAG = 0 ở cả 3 partition — consumer đã đi qua record hỏng
   ```
6. Gửi thêm 1 record hỏng kiểu **schema sai** (JSON hợp lệ nhưng `amount` là string) → cũng vào DLQ với `error: Error: schema violation...` — chứng minh DLQ bắt cả lỗi nghiệp vụ, không chỉ lỗi parse.

   ```bash
   echo 'o6:{"id":6,"amount":"sixty"}' | docker exec -i controller /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic orders --property parse.key=true --property key.separator=:
   ```

### ✅ Kiểm chứng

- v1: log `[Runner] Error when calling eachMessage` với `retryCount` 0→3, rồi `Crash: KafkaJSNumberOfRetriesExceeded`, `Restarting the consumer`, và lỗi lặp lại **cùng `offset`** — `kcg --describe` cho partition đó LAG không giảm.
- v2: đi qua toàn bộ 5 (rồi 6) record; `orders-dlq` có 2 record với header `error`, `originalTopic=orders`, `originalPartition`, `originalOffset`; group `orders-app-v2` LAG = 0.
- Record DLQ giữ **nguyên key + value gốc** → có thể sửa dữ liệu và replay về `orders` sau.

### 🧹 Dọn dẹp

```bash
# Ctrl+C consumer v2
kt --delete --topic orders-dlq
kcg --delete --group orders-app-v1
kcg --delete --group orders-app-v2
kt --delete --topic orders            # Lab 8.6 sẽ tạo lại orders sạch
```

### 🧠 Ý nghĩa với đề thi

- "Consumer crash, restart, crash lại trên cùng record" = **poison pill**; nguyên nhân gốc `SerializationException`/`RecordDeserializationException` (Java) hoặc lỗi trong handler; offset không tiến vì không commit được qua record đó.
- Fix trong đề: **DLQ topic + header lý do** (pattern chuẩn, cũng là cách Kafka Connect sink làm với `errors.tolerance=all` + `errors.deadletterqueue.topic.name`), `seek(partition, offset+1)`, hoặc `ErrorHandlingDeserializer` (Spring Kafka). `auto.offset.reset=latest` **không** tác dụng vì group đã có committed offset.
- Metric nhận diện: lag tăng nhưng `records-consumed-rate` = 0 trên 1 partition; `last-poll-seconds-ago` nhỏ (vẫn poll) — consumer "sống" nhưng kẹt.
- Header **không** tham gia partitioner; dùng để truyền metadata (lý do lỗi, `traceparent` cho tracing).

---

## Lab 8.6 — MirrorMaker 2 local: cluster A (3 node) → cluster B (1 node, port 9192)

**🎯 Mục tiêu:** Dựng **cluster B** 1 node (`kafka-b`, host `localhost:9192`) chung Docker network với cluster A; viết `mm2.properties` (`clusters=A,B`, `A->B.enabled=true`, `A->B.topics=orders.*`, RF 1 cho mọi topic nội bộ), chạy `connect-mirror-maker.sh` (dedicated mode) trong container riêng; kiểm chứng ở B có `A.orders` (đủ record), `heartbeats`, `A.checkpoints.internal`, và **offset consumer group được dịch** sang B; đổi sang `IdentityReplicationPolicy` để giữ nguyên tên topic.
**🧩 Luyện kỹ năng (liên quan đề):**

- MM2 = 3 connector trên Kafka Connect: `MirrorSourceConnector` (data + config), `MirrorCheckpointConnector` (dịch offset group), `MirrorHeartbeatConnector` (liveness/latency).
- `DefaultReplicationPolicy` → topic đích **`A.orders`** (chống loop); `IdentityReplicationPolicy` giữ tên — chỉ active/passive/migration.
- Flow mặc định **tắt** (`A->B.enabled=true` bắt buộc); `--clusters B` = "consume từ xa, produce gần".

**⏱️ ~35 phút** · **Yêu cầu trước:** Cluster A (Lab 8.1) đang chạy; `KAFKA_CTR=controller`.

### Các bước

1. Tạo `~/kafka-labs/docker-compose.cluster-b.yml` — bản sao của `docker-compose.single.yml` (Lab 1.1) đổi **tên container/hostname/port/CLUSTER_ID** và **join network của cluster A** để MM2 gọi được cả hai bằng hostname. (Không dùng override lên `single.yml` vì `container_name: kafka` và port `9092` đang bị cluster A chiếm.)

   ```yaml
   # ~/kafka-labs/docker-compose.cluster-b.yml — cluster B: 1 node KRaft combined, đích cho MirrorMaker 2 (Lab 8.6)
   # Chạy: docker compose -p kafka-b -f docker-compose.cluster-b.yml up -d
   # Host: localhost:9192 · Trong docker network (chung với cluster A): kafka-b:19092
   services:
     kafka-b:
       image: apache/kafka:4.3.1
       container_name: kafka-b
       hostname: kafka-b
       ports:
         - "9192:9192"
       environment:
         CLUSTER_ID: "5L6g3nShT-eMCtK--X86sw"           # KHÁC cluster A
         KAFKA_NODE_ID: 1
         KAFKA_PROCESS_ROLES: broker,controller
         KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-b:9093
         KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9192,CONTROLLER://:9093
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-b:19092,PLAINTEXT_HOST://localhost:9192
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
         KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
         KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
         KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
         KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
         KAFKA_SHARE_COORDINATOR_STATE_TOPIC_REPLICATION_FACTOR: 1
         KAFKA_NUM_PARTITIONS: 3
         KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
         KAFKA_LOG_DIRS: /tmp/kraft-combined-logs

   networks:
     default:
       name: kafka-labs_default        # network do project cluster A (thư mục ~/kafka-labs) tạo ra
       external: true
   ```

   ```bash
   cd ~/kafka-labs
   docker network ls | grep kafka-labs_default            # phải có (cluster A đang chạy); nếu tên khác → sửa dòng name: ở trên
   docker compose -p kafka-b -f docker-compose.cluster-b.yml up -d
   export KAFKA_B=kafka-b:19092
   docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_B --list     # rỗng, nhưng kết nối OK
   BROKERS=localhost:9192 node ~/kafka-labs/ping.mjs                                            # từ host: brokers advertised: 1=localhost:9192
   ```
2. Chuẩn bị dữ liệu ở **A**: topic `orders` 30 record có key + consumer group `orders-app` đã đọc **10 record** (để có offset cho checkpoint dịch).

   ```bash
   kt --create --topic orders --partitions 3 --replication-factor 3 --config retention.ms=86400000
   docker exec -i controller bash -c 'for i in $(seq 1 30); do echo "u$((i % 5)):{\"id\":$i,\"amount\":$((i*10))}"; done | \
     /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic orders --property parse.key=true --property key.separator=:'
   koff --topic orders | awk -F: '{s+=$3} END{print "A/orders total records:", s}'      # 30
   kcc --topic orders --group orders-app --from-beginning --max-messages 10 >/dev/null
   kcg --describe --group orders-app                     # CURRENT-OFFSET cộng 3 partition = 10, CONSUMER-ID = - (đã thoát)
   ```
3. Viết `~/kafka-labs/mm2/mm2.properties` (in đầy đủ).

   ```properties
   # ~/kafka-labs/mm2/mm2.properties — MirrorMaker 2 dedicated mode, flow A -> B (Lab 8.6)
   clusters = A, B
   A.bootstrap.servers = kafka-1:19092,kafka-2:19092,kafka-3:19092
   B.bootstrap.servers = kafka-b:19092

   # Flow: mặc định MỌI flow tắt — phải bật tường minh
   A->B.enabled = true
   A->B.topics = orders.*
   B->A.enabled = false
   # Không tạo herder B->A (chỉ để emit heartbeat vào A). Lý do: mọi topic MM2 tự tạo dùng RF bên dưới (=1),
   # mà cluster A có min.insync.replicas=2 → producer acks=all vào topic RF1 sẽ NotEnoughReplicas. Tắt để A "sạch".
   B->A.emit.heartbeats.enabled = false

   # Cluster B chỉ có 1 broker → mọi topic do MM2 tạo ở B phải RF 1
   replication.factor = 1                        # remote topic (A.orders) trên B
   checkpoints.topic.replication.factor = 1      # A.checkpoints.internal (trên B)
   heartbeats.topic.replication.factor = 1       # heartbeats (trên B)
   offset-syncs.topic.replication.factor = 1
   offset-syncs.topic.location = target          # mặc định "source" (=A). Dời sang B để không tạo topic RF1 trên A
   config.storage.replication.factor = 1         # 3 topic nội bộ của Connect worker: mm2-configs/offsets/status.A.internal (trên B)
   offset.storage.replication.factor = 1
   status.storage.replication.factor = 1

   # Dịch offset consumer group A -> B và ghi thẳng vào __consumer_offsets của B (khi group ở B inactive)
   sync.group.offsets.enabled = true
   sync.group.offsets.interval.seconds = 5
   emit.checkpoints.interval.seconds = 5
   emit.heartbeats.interval.seconds = 1
   refresh.topics.interval.seconds = 10          # tự phát hiện topic mới khớp orders.*
   refresh.groups.interval.seconds = 10
   sync.topic.configs.enabled = true             # copy config topic (trừ danh sách exclude: min.insync.replicas, *.throttled.*, …)
   tasks.max = 3

   # Đổi tên topic đích: mặc định DefaultReplicationPolicy → A.orders. Bước 7 đổi sang IdentityReplicationPolicy.
   # replication.policy.class = org.apache.kafka.connect.mirror.IdentityReplicationPolicy
   ```
4. Chạy MM2 trong **container riêng** trên cùng network (không cần Connect cluster sẵn có — dedicated mode tự dựng worker). Giữ terminal này mở.

   ```bash
   mkdir -p ~/kafka-labs/mm2   # (đã có nếu bạn vừa tạo file)
   docker run --rm -it --name mm2 --network kafka-labs_default \
     -v ~/kafka-labs/mm2:/mm2 apache/kafka:4.3.1 \
     /opt/kafka/bin/connect-mirror-maker.sh /mm2/mm2.properties
   # Có thể thêm "--clusters B" ở cuối = chỉ chạy herder có đích B (best practice đặt MM2 cạnh cluster đích).
   ```
   Log đáng chú ý (30–60 giây): `Kafka MirrorMaker initializing ...`, `creating herder for A->B`, `Starting connector MirrorSourceConnector` / `MirrorCheckpointConnector` / `MirrorHeartbeatConnector`, `replicating 3 topic-partitions A->B: [orders-0, orders-1, orders-2]`, `Kafka MirrorMaker started`.
5. Kiểm chứng ở **B**.

   ```bash
   docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_B --list
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
   # Đủ record? (30) và giữ nguyên partition (mỗi partition đích = partition nguồn)
   docker exec controller /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_B --topic A.orders
   koff --topic orders
   # Heartbeat mỗi giây → end offset của heartbeats tăng liên tục
   docker exec controller /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_B --topic heartbeats; sleep 3
   docker exec controller /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_B --topic heartbeats
   # Đọc heartbeat / checkpoint bằng formatter có sẵn trong connect-mirror-client
   docker exec controller /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_B --topic heartbeats --from-beginning --max-messages 2 \
     --formatter org.apache.kafka.connect.mirror.formatters.HeartbeatFormatter
   # Heartbeat{sourceClusterAlias=A, targetClusterAlias=B, timestamp=1757900000123}
   docker exec controller /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_B --topic A.checkpoints.internal --from-beginning --max-messages 3 \
     --formatter org.apache.kafka.connect.mirror.formatters.CheckpointFormatter
   # Checkpoint{consumerGroupId=orders-app, topicPartition=A.orders-0, upstreamOffset=4, downstreamOffset=4, metadata=}
   ```
   Data với `print.key`/`print.partition` để thấy key và partition **giữ nguyên**:
   ```bash
   docker exec controller /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_B --topic A.orders --from-beginning \
     --property print.key=true --property print.partition=true --timeout-ms 5000 | sort | head -5
   ```
6. **Offset consumer group đã dịch sang B** (chờ ≤ 15 giây sau khi MM2 start).

   ```bash
   docker exec controller /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_B --list                        # orders-app
   docker exec controller /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_B --describe --group orders-app
   ```
   Output mẫu — group `orders-app` tồn tại ở B **dù chưa consumer nào từng nối B**, offset trên `A.orders` ≈ offset ở A (có thể **thấp hơn** vì offset-sync chỉ ghi mỗi `offset.lag.max`=100 record → dịch conservative, không bao giờ vượt):
   ```
   GROUP       TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID  HOST  CLIENT-ID
   orders-app  A.orders  0          4               10              6    -            -     -
   orders-app  A.orders  1          3               10              7    -            -     -
   orders-app  A.orders  2          3               10              7    -            -     -
   ```
   Failover thử: consumer ở B đọc tiếp từ offset đã dịch (không đọc lại 10 record đầu):
   ```bash
   docker exec controller /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_B --topic A.orders --group orders-app --timeout-ms 5000 | wc -l   # ≈ 20
   ```
7. **`IdentityReplicationPolicy`** — giữ nguyên tên topic. Ctrl+C MM2, bỏ comment dòng `replication.policy.class`, chạy lại, rồi produce thêm 10 record ở A.

   ```bash
   sed -i.bak 's/^# replication.policy.class/replication.policy.class/' ~/kafka-labs/mm2/mm2.properties
   grep replication.policy.class ~/kafka-labs/mm2/mm2.properties
   docker run --rm -it --name mm2 --network kafka-labs_default -v ~/kafka-labs/mm2:/mm2 apache/kafka:4.3.1 /opt/kafka/bin/connect-mirror-maker.sh /mm2/mm2.properties
   ```
   Terminal khác:
   ```bash
   docker exec -i controller bash -c 'for i in $(seq 31 40); do echo "u$((i % 5)):{\"id\":$i,\"amount\":$((i*10))}"; done | \
     /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic orders --property parse.key=true --property key.separator=:'
   sleep 10
   docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_B --list | grep -E "^(A\.)?orders$"     # A.orders  VÀ  orders
   docker exec controller /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_B --topic orders                     # tổng 10 — chỉ record MỚI
   ```
   > 📌 Vì sao `orders` ở B chỉ có 10 record, không phải 40? Offset của `MirrorSourceConnector` (đã copy tới đâu của `orders-N` nguồn) lưu trong `mm2-offsets.A.internal` trên B, **không phụ thuộc tên topic đích** → đổi policy chỉ đổi đích cho record **từ đây về sau**. Muốn copy lại từ đầu phải reset offset connector (xoá `mm2-offsets.A.internal` hoặc dùng REST `DELETE /connectors/<name>/offsets` khi chạy trên Connect cluster).

### ✅ Kiểm chứng

- B có `A.orders` với **30 record**, cùng số partition và cùng phân bố key→partition như A; có `heartbeats` (end offset tăng ~1/giây) và `A.checkpoints.internal` (đọc được `Checkpoint{consumerGroupId=orders-app, ...}`); `mm2-offset-syncs.A.internal` nằm ở B vì `offset-syncs.topic.location=target`.
- `kafka-consumer-groups.sh --describe --group orders-app` **trên B** có offset cho `A.orders` (≈ 10 tổng, có thể thấp hơn) mà không consumer nào từng commit ở B.
- Cluster A **không** có topic mới nào do MM2 tạo (`kt --list` trên A chỉ có `orders` + nội bộ) — nhờ tắt heartbeat B->A và dời offset-syncs.
- Sau bước 7: B có thêm topic **`orders`** (tên giữ nguyên) chứa đúng 10 record mới.

### 🧹 Dọn dẹp

```bash
# Ctrl+C MM2 (container --rm tự xoá)
docker rm -f mm2 2>/dev/null
docker compose -p kafka-b -f ~/kafka-labs/docker-compose.cluster-b.yml down -v
kt --delete --topic orders
kcg --delete --group orders-app
mv ~/kafka-labs/mm2/mm2.properties.bak ~/kafka-labs/mm2/mm2.properties 2>/dev/null   # trả về DefaultReplicationPolicy; GIỮ file cho Tuần 9 (MSK Replicator so sánh)
unset KAFKA_B
```

### 🧠 Ý nghĩa với đề thi

- MM2 xây trên **Kafka Connect** (MM1 xoá ở 4.0): `MirrorSourceConnector` (record + partition + topic config + ACL, tự phát hiện topic mới), `MirrorCheckpointConnector` (dịch offset → `A.checkpoints.internal`; `sync.group.offsets.enabled=true` ghi thẳng `__consumer_offsets` đích khi group inactive), `MirrorHeartbeatConnector` (`heartbeats` → đo liveness/latency `replication-latency-ms`).
- `A->B.enabled=true` bắt buộc; `A->B.topics` regex; `connect-mirror-maker.sh mm2.properties [--clusters B]` (dedicated) hoặc deploy 3 connector lên Connect có sẵn qua REST.
- `DefaultReplicationPolicy` → `A.orders` (chống loop, active/active OK; consumer đọc `orders` + `B.orders`). `IdentityReplicationPolicy` giữ tên → migration/active-passive, **không** active/active.
- Failover: consumer ở đích dùng offset đã dịch (`RemoteClusterUtils.translateOffsets()` hoặc offset đã sync) — dịch **conservative** (không vượt), có thể đọc lặp vài record → consumer phải idempotent.
- Bài học vận hành thật: MM2 tạo nhiều topic nội bộ **ở cả 2 cluster** với RF từ config → cluster có `min.insync.replicas=2` mà RF 1 sẽ chặn ghi (`NotEnoughReplicas`) — chỉnh `*.replication.factor` theo từng cluster.

---

## Lab 8.7 — Rolling restart đúng cách + `kafka-features.sh describe`

**🎯 Mục tiêu:** Đọc feature/metadata version của cluster bằng `kafka-features.sh describe`; **rolling restart** 3 broker theo đúng quy trình (1 broker/lần → `docker stop` kích hoạt controlled shutdown → start → **chờ `--under-replicated-partitions` rỗng** → broker kế tiếp) trong khi producer `kafkajs` ghi liên tục **không lỗi**; giải thích `controlled.shutdown.enable`; kết thúc bằng preferred election.
**🧩 Luyện kỹ năng (liên quan đề):**

- `kafka-features.sh describe` → `metadata.version` (thay `inter.broker.protocol.version`), `kraft.version`, `group.version`, `share.version`, `transaction.version`, `eligible.leader.replicas.version`; `upgrade --release-version X` để finalize.
- Rolling restart: 1 broker/lần, chờ URP = 0 và `ActiveControllerCount` = 1; `controlled.shutdown.enable=true` (mặc định) chuyển leadership trước khi tắt.
- Sau vòng restart leader dồn về broker khởi động sớm → `kafka-leader-election.sh --election-type preferred`.

**⏱️ ~20 phút** · **Yêu cầu trước:** Lab 8.1 đang chạy, 3 broker sống; cluster B đã down.

### Các bước

1. Đọc feature version và quorum.

   ```bash
   kfeat describe
   kq describe --status | head -6
   ```
   Output mẫu `kfeat describe` (tên/số version có thể lệch nhẹ theo bản 4.3.x):
   ```
   Feature: eligible.leader.replicas.version  SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1        Epoch: 5
   Feature: group.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1        Epoch: 5
   Feature: kraft.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 0        Epoch: 5
   Feature: metadata.version                  SupportedMinVersion: 3.3-IV3  SupportedMaxVersion: 4.3-IV0  FinalizedVersionLevel: 4.3-IV0  Epoch: 5
   Feature: share.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1        Epoch: 5
   Feature: transaction.version               SupportedMinVersion: 0        SupportedMaxVersion: 2        FinalizedVersionLevel: 2        Epoch: 5
   ```
   > 📌 `kraft.version` finalized **0** vì cluster dùng **static quorum** (`controller.quorum.voters`); dynamic quorum (KIP-853, `controller.quorum.bootstrap.servers` + `kafka-storage.sh format --standalone`) mới lên 1. `metadata.version` = `4.3-IV0` là mức cao nhất image hỗ trợ — không có gì để upgrade; xem thử lệnh (dry-run, không đổi gì):
   > ```bash
   > kfeat upgrade --release-version 4.3 --dry-run     # báo đã ở version này / không thay đổi
   > ```
2. Kiểm tra `controlled.shutdown.enable` và tạo topic + producer ghi liên tục.

   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 --all | grep -E "controlled.shutdown|broker.session.timeout.ms"
   # controlled.shutdown.enable=true ...   broker.session.timeout.ms=9000
   kt --create --topic rolling-demo --partitions 3 --replication-factor 3
   ```

   ```javascript
   // ~/kafka-labs/week-08/rolling-producer.mjs — Lab 8.7: producer ghi liên tục trong rolling restart
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "rolling-producer",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.ERROR,
     retry: { initialRetryTime: 300, retries: 10, maxRetryTime: 5000 },   // Java: retries / retry.backoff.ms — leader đổi là lỗi retriable
   });
   const producer = kafka.producer({ idempotent: true, maxInFlightRequests: 1 }); // Java: enable.idempotence=true → không duplicate khi retry
   await producer.connect();

   let i = 0, ok = 0, fail = 0;
   const timer = setInterval(async () => {
     const n = ++i;
     try {
       const [m] = await producer.send({ topic: "rolling-demo", acks: -1, messages: [{ key: `k${n % 3}`, value: `msg-${n} ${new Date().toISOString()}` }] });
       ok++;
       if (n % 10 === 0) console.log(`ok=${ok} fail=${fail}  last msg-${n} -> p${m.partition} off=${m.baseOffset}`);
     } catch (e) {
       fail++;
       console.log(`FAIL msg-${n}: ${e.name}: ${e.message}`);
     }
   }, 200);

   process.on("SIGINT", async () => { clearInterval(timer); console.log(`TOTAL sent=${i} ok=${ok} fail=${fail}`); await producer.disconnect(); process.exit(0); });
   ```

   ```bash
   cd ~/kafka-labs/week-08 && node rolling-producer.mjs      # Terminal 2 — giữ chạy
   ```
3. Viết script rolling restart `~/kafka-labs/week-08/rolling-restart.sh` (chạy từ host, CLI qua container `controller`, bootstrap **cả 3 broker** để không phụ thuộc broker đang tắt).

   ```bash
   cat > ~/kafka-labs/week-08/rolling-restart.sh <<'EOF'
   #!/usr/bin/env bash
   # Rolling restart 3 broker: 1 broker/lần — stop (SIGTERM → controlled shutdown) → start → chờ URP = 0 → broker kế tiếp
   set -u
   BS=kafka-1:19092,kafka-2:19092,kafka-3:19092
   urp() {   # số partition under-replicated toàn cluster; 999 nếu CLI không nối được
     local out
     out=$(docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server "$BS" --describe --under-replicated-partitions 2>&1) || { echo 999; return; }
     echo "$out" | grep -c 'Partition:'
   }
   for b in kafka-1 kafka-2 kafka-3; do
     echo "== [$b] stop (controlled shutdown: chuyển leader trước khi tắt)"; docker stop "$b" >/dev/null
     echo "   URP khi $b đang tắt: $(urp)"
     echo "== [$b] start"; docker start "$b" >/dev/null
     until [ "$(urp)" = "0" ]; do echo "   chờ URP về 0 (hiện $(urp))..."; sleep 5; done
     echo "== [$b] URP = 0 → OK, nghỉ 5 s rồi sang broker kế tiếp"; sleep 5
   done
   echo "== Xong 3 broker. Leader hiện tại:"
   docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server "$BS" --describe --topic rolling-demo
   echo "== Preferred leader election"
   docker exec controller /opt/kafka/bin/kafka-leader-election.sh --bootstrap-server "$BS" --election-type preferred --all-topic-partitions
   docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server "$BS" --describe --topic rolling-demo
   EOF
   chmod +x ~/kafka-labs/week-08/rolling-restart.sh
   ```
4. Chạy rolling restart (Terminal 1) và theo dõi producer (Terminal 2) + Grafana panel URP.

   ```bash
   ~/kafka-labs/week-08/rolling-restart.sh
   ```
   Output mẫu:
   ```
   == [kafka-1] stop (controlled shutdown: chuyển leader trước khi tắt)
      URP khi kafka-1 đang tắt: 61
   == [kafka-1] start
      chờ URP về 0 (hiện 61)...
      chờ URP về 0 (hiện 12)...
   == [kafka-1] URP = 0 → OK, nghỉ 5 s rồi sang broker kế tiếp
   == [kafka-2] stop ...
   ...
   == Preferred leader election
   Successfully completed leader election (PREFERRED) for partitions rolling-demo-0, rolling-demo-2
   Valid replica already elected for partitions rolling-demo-1
   ```
   Terminal 2: dòng `ok=... fail=0` đều đặn; có thể vài `send` chậm 1–3 giây lúc leader chuyển nhưng **không `FAIL`** (kafkajs nhận `NOT_LEADER_OR_FOLLOWER`/timeout → refresh metadata → retry). Grafana: URP nhảy lên 3 lần rồi về 0.
5. Soi log controlled shutdown của broker vừa tắt và sự kiện trong metadata log.

   ```bash
   docker logs kafka-1 2>&1 | grep -iE "controlled shutdown|PENDING_CONTROLLED_SHUTDOWN|SHUTTING_DOWN|shut down completed" | tail -5
   docker logs controller 2>&1 | grep -iE "controlled shutdown|fenc|unfenc" | tail -6
   ```
   Thấy broker chuyển trạng thái `RUNNING → PENDING_CONTROLLED_SHUTDOWN → SHUTTING_DOWN`; controller nhận `BrokerHeartbeat` có `wantShutDown=true`, chuyển leadership rồi mới cho broker tắt ("controlled shutdown ... completed").
6. **Đối chứng sai cách (tùy chọn, 1 phút):** `docker stop kafka-2 kafka-3` cùng lúc → Terminal 2 lập tức `FAIL ... NotEnoughReplicas` (ISR = 1 < min.isr 2) → `docker start kafka-2 kafka-3`. Đây là lý do "1 broker/lần".

### ✅ Kiểm chứng

- `kfeat describe` đọc được `metadata.version` (`4.3-IV0`), `kraft.version`, `share.version`, `group.version`, `transaction.version`.
- Rolling restart: script chờ URP về 0 **trước** mỗi broker kế tiếp; producer `fail=0` suốt quá trình; Ctrl+C producer in `TOTAL ... fail=0`.
- Sau `kafka-leader-election.sh --election-type preferred`, `Leader` = replica đầu danh sách ở mọi partition.
- Đối chứng bước 6 cho `NotEnoughReplicasException` ngay lập tức.

### 🧹 Dọn dẹp (kết thúc tuần)

```bash
# Ctrl+C rolling-producer.mjs
kt --delete --topic rolling-demo
docker start kafka-2 kafka-3 2>/dev/null || true

# Tắt toàn bộ stack tuần 8 (cluster A + monitoring). -v xoá volume của Prometheus/Grafana nếu bạn đã thêm.
cd ~/kafka-labs
docker compose -p kafka-b -f docker-compose.cluster-b.yml down -v 2>/dev/null     # nếu Lab 8.6 chưa dọn
docker compose -f docker-compose.cluster.yml -f docker-compose.monitoring.yml down -v
unset COMPOSE_FILE
# GIỮ: docker-compose.monitoring.yml, jmx/, prometheus/, grafana/, docker-compose.cluster-b.yml, mm2/ và week-08/*.mjs — Tuần 9 (MSK Open Monitoring so sánh) & Tuần 10 (capstone) dùng lại.
```

### 🧠 Ý nghĩa với đề thi

- **Rolling restart:** 1 broker/lần; điều kiện sang broker kế: `UnderReplicatedPartitions` = 0 (hoặc `--under-replicated-partitions` rỗng) và `ActiveControllerCount` = 1; RF 3 / min.isr 2 chỉ chịu **1** broker vắng. Restart controller (KRaft) sau cùng; quorum 3 node chịu 1 lỗi.
- **`controlled.shutdown.enable=true`** (mặc định): sync log + chuyển leadership trước khi tắt → downtime vài ms; chỉ thành công khi partition có replica khác sống. `kill -9` = không controlled → leader mất đột ngột, log recovery khi lên lại.
- Sau vòng restart, leader dồn về broker khởi động sớm → `kafka-leader-election.sh --election-type preferred --all-topic-partitions` (hoặc chờ `auto.leader.rebalance.enable` mỗi 300 s, lệch > 10%).
- **Upgrade KRaft:** rolling restart code mới → verify → finalize `kafka-features.sh upgrade --release-version 4.3`; `metadata.version` thay IBP cũ; **downgrade chỉ khi không có metadata change** (4.3 → 4.2 không được). 4.x chỉ KRaft; từ ZK phải qua 3.9 migrate.
- Client đúng cấu hình (`retries` > 0, idempotence, `acks=all`) sống qua leader change mà **không mất/duplicate** — đó là lý do đề gọi rolling restart là "zero-downtime" cho client.

---

> ✅ Xong 7 lab? Đối chiếu [Lab checklist trong README](README.md#-lab-checklist) — nhớ **Lab 8.1, 8.2, 8.4 là bắt buộc** — rồi làm [bộ câu hỏi luyện tập](questions.md) (28 câu) và **MINI-MOCK toàn domain Tuần 1–8 (≥72%)** ở Buổi D trước khi sang Tuần 9. Giữ lại `docker-compose.monitoring.yml` + `jmx/` + `prometheus/` + `grafana/` cho Tuần 9–10.
