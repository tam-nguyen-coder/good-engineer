# 🧪 Hands-on Labs — Tuần 6: Kafka Connect operations

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: cluster 3 broker + 1 controller từ [CCDAK Tuần 1 — Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md) (`~/kafka-labs/docker-compose.cluster.yml`) và các alias `kt`/`kcp`/`kcc`/`kcg`/`kcfg`. **Không định nghĩa lại file compose gốc** — tuần này chỉ thêm **file override riêng**.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung

```bash
cd ~/kafka-labs
mkdir -p week-06/connect-data
export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
docker compose -f docker-compose.cluster.yml up -d
docker compose -f docker-compose.cluster.yml ps        # 4 container: controller, kafka-1, kafka-2, kafka-3
```

Hai biến rút gọn cho REST của hai worker (dùng suốt tuần):

```bash
export W1=http://localhost:8083     # worker connect-1
export W2=http://localhost:8084     # worker connect-2 (host 8084 → container 8083)
```

> ⚠️ **Sơ đồ cổng tuần này.** Cluster CCDAK Tuần 1 đã chiếm `9092` / `9094` / `9096` (broker) và `9093` (**CONTROLLER — tuyệt đối không dùng lại**). Tuần này thêm:
>
> | Cổng host | Dùng cho |
> |---|---|
> | `8083` | REST của `connect-1` |
> | `8084` | REST của `connect-2` (map sang `8083` trong container) |
> | `19093` | listener `SASL_PLAINTEXT` của broker — **chỉ Lab 6.6** |
>
> Nếu bạn còn container `connect` của [CCDAK Tuần 5](../../../CCDAK/study-plan/week-05/labs.md) đang chạy thì `docker rm -f connect` trước, nó cũng giữ 8083.

Cần `jq` để đọc JSON cho dễ:

```bash
jq --version || brew install jq
```

---

## Lab 6.1 — Dựng Connect distributed 2 worker và kiểm 3 internal topic ⭐

**🎯 Mục tiêu:** Có một **Connect cluster thật sự** gồm 2 worker cùng `group.id`, tự tay xác nhận 3 internal topic đúng **1 / 25 / 5 partition**, đều `cleanup.policy=compact`, RF 3 — và chứng minh gọi REST vào worker nào cũng cho cùng một kết quả.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc và viết worker config distributed: `group.id`, 3 `*.storage.topic`, `*.storage.replication.factor`, `plugin.path`, `offset.flush.interval.ms`, `rest.advertised.*`.
- Nhận ra Connect worker group là **một group riêng của Kafka**, không phải consumer group — và vì sao `group.id` không được trùng.
- `GET /`, `GET /connector-plugins`, `GET /connectors` trên nhiều worker.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo file override `~/kafka-labs/docker-compose.connect2.yml`. Hai worker dùng **cùng** `group.id` và **cùng** 3 tên topic — đó là điều kiện đủ để chúng thành một cluster.

   ```yaml
   # ~/kafka-labs/docker-compose.connect2.yml
   # Override: thêm 2 worker Kafka Connect distributed lên cluster 3 broker của CCDAK Tuần 1.
   # REST: connect-1 → http://localhost:8083 · connect-2 → http://localhost:8084 (container vẫn 8083)
   x-connect-common: &connect-common
     image: confluentinc/cp-kafka-connect:8.0.0
     depends_on: [kafka-1, kafka-2, kafka-3]
     volumes:
       - ./week-06/connect-data:/data

   x-connect-env: &connect-env
     CONNECT_BOOTSTRAP_SERVERS: kafka-1:19092,kafka-2:19092,kafka-3:19092
     # ---- Cái gì làm nên MỘT Connect cluster: group.id + 3 tên topic giống hệt nhau ----
     CONNECT_GROUP_ID: w6-connect-cluster          # KHÔNG được trùng bất kỳ consumer group id nào
     CONNECT_CONFIG_STORAGE_TOPIC: w6-connect-configs
     CONNECT_OFFSET_STORAGE_TOPIC: w6-connect-offsets
     CONNECT_STATUS_STORAGE_TOPIC: w6-connect-status
     CONNECT_CONFIG_STORAGE_REPLICATION_FACTOR: 3  # mặc định đã là 3; ghi ra để nhớ
     CONNECT_OFFSET_STORAGE_REPLICATION_FACTOR: 3
     CONNECT_STATUS_STORAGE_REPLICATION_FACTOR: 3
     # ---- Converter mặc định của worker (connector override được) ----
     CONNECT_KEY_CONVERTER: org.apache.kafka.connect.storage.StringConverter
     CONNECT_VALUE_CONVERTER: org.apache.kafka.connect.json.JsonConverter
     CONNECT_VALUE_CONVERTER_SCHEMAS_ENABLE: "false"
     # ---- Plugin: FileStream connector KHÔNG nằm trên classpath mặc định từ Kafka 3.2 ----
     CONNECT_PLUGIN_PATH: /usr/share/java,/usr/share/confluent-hub-components,/usr/share/filestream-connectors
     # ---- Tiện lab: flush offset source mỗi 10 s thay vì 60 s mặc định ----
     CONNECT_OFFSET_FLUSH_INTERVAL_MS: 10000

   services:
     connect-1:
       <<: *connect-common
       container_name: connect-1
       hostname: connect-1
       ports:
         - "8083:8083"
       environment:
         <<: *connect-env
         CONNECT_REST_ADVERTISED_HOST_NAME: connect-1   # worker khác dùng địa chỉ này để forward
         CONNECT_REST_ADVERTISED_PORT: 8083
         KAFKA_JMX_PORT: 9585
         KAFKA_JMX_HOSTNAME: connect-1

     connect-2:
       <<: *connect-common
       container_name: connect-2
       hostname: connect-2
       ports:
         - "8084:8083"                                  # host 8084 → container 8083
       environment:
         <<: *connect-env
         CONNECT_REST_ADVERTISED_HOST_NAME: connect-2
         CONNECT_REST_ADVERTISED_PORT: 8083
         KAFKA_JMX_PORT: 9585
         KAFKA_JMX_HOSTNAME: connect-2
   ```
2. Khởi động và chờ cả hai REST lên (~45–90 s cho lần đầu).

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.connect2.yml
   docker compose up -d
   for U in $W1 $W2; do until curl -s $U/ >/dev/null; do sleep 3; echo "waiting $U ..."; done; done
   curl -s $W1/ | jq
   curl -s $W2/ | jq
   # cả hai in cùng "kafka_cluster_id": "MkU3OEVBNTcwNTJENDM2Qk"
   ```
3. Kiểm 3 internal topic — **đây là phần phải thuộc lòng**.

   ```bash
   kt --list | grep '^w6-connect-'
   for t in w6-connect-configs w6-connect-offsets w6-connect-status; do
     kt --describe --topic $t | head -1
   done
   ```

   Kết quả mong đợi (partition **1 / 25 / 5**, tất cả `cleanup.policy=compact`, RF 3):

   ```
   Topic: w6-connect-configs   PartitionCount: 1    ReplicationFactor: 3   Configs: cleanup.policy=compact
   Topic: w6-connect-offsets   PartitionCount: 25   ReplicationFactor: 3   Configs: cleanup.policy=compact
   Topic: w6-connect-status    PartitionCount: 5    ReplicationFactor: 3   Configs: cleanup.policy=compact
   ```

   > 📌 Cột `Configs` chỉ liệt kê **override ở mức topic**. `min.insync.replicas=2` của cluster là default mức broker nên có thể không xuất hiện ở đây — kiểm bằng `kt --describe --topic w6-connect-configs --all` nếu muốn thấy giá trị hiệu lực và nguồn gốc của nó.
4. Xác nhận Connect worker group **không phải** consumer group.

   ```bash
   # Kafka 4.x: kafka-groups.sh liệt kê mọi group kèm cột TYPE/PROTOCOL (KIP-1043)
   docker exec kafka-1 /opt/kafka/bin/kafka-groups.sh --bootstrap-server kafka-1:19092 --list
   # w6-connect-cluster   <protocol type: connect>

   # Dự phòng nếu bản của bạn không có kafka-groups.sh:
   kcg --list          # chưa có group nào — sink connector chưa tạo
   ```
5. Xem plugin đã cài, trên **cả hai** worker.

   ```bash
   curl -s $W1/connector-plugins | jq -r '.[] | "\(.type)\t\(.class)"' | sort
   curl -s $W2/connector-plugins | jq -r '.[] | "\(.type)\t\(.class)"' | sort
   # sink    org.apache.kafka.connect.file.FileStreamSinkConnector
   # source  org.apache.kafka.connect.file.FileStreamSourceConnector
   # source  org.apache.kafka.connect.mirror.MirrorCheckpointConnector / MirrorHeartbeatConnector / MirrorSourceConnector

   curl -s "$W1/connector-plugins?connectorsOnly=false" \
     | jq -r '.[] | select(.type=="converter" or .type=="transformation") | "\(.type)\t\(.class)"' | sort | head -20
   curl -s $W1/connectors            # []
   ```
6. Thấy ai đang làm **leader** của cluster.

   ```bash
   docker logs connect-1 2>&1 | grep -iE "Joined group|assigned tasks|leaderUrl" | tail -5
   docker logs connect-2 2>&1 | grep -iE "Joined group|assigned tasks|leaderUrl" | tail -5
   # Một trong hai dòng sẽ có leaderUrl trỏ tới http://connect-1:8083/ hoặc http://connect-2:8083/
   ```

### ✅ Kiểm chứng

- `GET /` trên 8083 và 8084 trả **cùng** `kafka_cluster_id` → hai worker nói chuyện với cùng một Kafka cluster.
- `w6-connect-configs` có **đúng 1** partition. Nếu bạn thấy 3, tức là topic đã bị auto-create theo `num.partitions=3` của broker trước khi worker kịp tạo — xoá topic và khởi động lại worker.
- Cả 3 topic đều có `cleanup.policy=compact`. Nếu một cái là `delete`, connector sẽ "quên" config/offset sau khi retention hết hạn.
- `GET /connector-plugins` trên hai worker trả **danh sách giống hệt nhau** → cùng `plugin.path`, cùng bộ plugin. Danh sách khác nhau = hai worker cài plugin lệch, và task sẽ FAILED ngẫu nhiên tuỳ nó rơi vào worker nào.
- `kafka-groups.sh --list` cho thấy `w6-connect-cluster` là group **protocol type `connect`**, tách biệt hoàn toàn với consumer group.

### 🧹 Dọn dẹp

```bash
# GIỮ nguyên stack cho Lab 6.2 → 6.5.
```

### 🧠 Ý nghĩa với đề thi

- Một Connect cluster được định nghĩa bởi **`group.id` + 3 tên internal topic**. Hai worker lệch bất kỳ giá trị nào trong bốn thứ đó = **hai cluster riêng biệt** dù chạy cạnh nhau, dùng chung Kafka, nhìn bề ngoài y hệt.
- Bộ số **1 / 25 / 5** và **RF 3** là câu hỏi trực tiếp. Riêng config topic, "1 partition" là **bắt buộc** chứ không phải mặc định chỉnh được — không tồn tại `config.storage.partitions`.
- `rest.advertised.host.name`/`.port` là địa chỉ để worker **forward request cho nhau**, không phải địa chỉ cho client bên ngoài. Sai nó thì `POST /connectors` chỉ chạy khi trúng leader.

---

## Lab 6.2 — Kill 1 worker: task chuyển đi đâu, và vì sao phải chờ 5 phút ⭐

> 🔥 **Lab "gây hỏng rồi sửa" số 1.**

**🎯 Mục tiêu:** Tự tay giết một worker, quan sát task **không chuyển ngay**, hiểu đó là `scheduled.rebalance.max.delay.ms` đang làm đúng việc, rồi chứng minh hai đường khôi phục: (a) bật worker lại trong thời gian hoãn → task về đúng chỗ cũ; (b) hạ tham số hoãn → failover nhanh, đổi lại cluster nhạy cảm hơn với restart.
**🧩 Luyện kỹ năng (liên quan đề):**

- Phân biệt **worker chết** (Connect tự rebalance) và **task chết** (người vận hành phải can thiệp).
- Đọc `worker_id` trong `/status` để biết task đang nằm ở worker nào.
- Hiểu ba mốc thời gian: `session.timeout.ms` **10000** → phát hiện worker chết; `scheduled.rebalance.max.delay.ms` **300000** → hoãn giao lại; `rebalance.timeout.ms` **60000** → trần cho một vòng rebalance.

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 6.1 (stack đang chạy).

### Các bước

1. Tạo dữ liệu và một sink connector đủ nhiều task để trải ra cả hai worker.

   ```bash
   kt --create --topic w6-orders --partitions 6 --replication-factor 3
   for i in $(seq 1 60); do echo "{\"id\":$i,\"amount\":$((RANDOM%500))}"; done \
     | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
         --bootstrap-server kafka-1:19092 --topic w6-orders

   cat > ~/kafka-labs/week-06/orders-sink.json <<'EOF'
   {
     "name": "w6-orders-sink",
     "config": {
       "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
       "tasks.max": "4",
       "topics": "w6-orders",
       "file": "/data/orders-sink.out",
       "key.converter": "org.apache.kafka.connect.storage.StringConverter",
       "value.converter": "org.apache.kafka.connect.storage.StringConverter"
     }
   }
   EOF
   curl -s -X POST -H "Content-Type: application/json" \
     --data @~/kafka-labs/week-06/orders-sink.json $W1/connectors | jq .name
   ```
2. Xem task đang nằm ở worker nào. Đây là output bạn phải quen mắt.

   ```bash
   sleep 10
   curl -s $W1/connectors/w6-orders-sink/status | jq
   ```

   ```json
   {
     "name": "w6-orders-sink",
     "connector": { "state": "RUNNING", "worker_id": "connect-1:8083" },
     "tasks": [
       { "id": 0, "state": "RUNNING", "worker_id": "connect-1:8083" },
       { "id": 1, "state": "RUNNING", "worker_id": "connect-2:8083" },
       { "id": 2, "state": "RUNNING", "worker_id": "connect-1:8083" },
       { "id": 3, "state": "RUNNING", "worker_id": "connect-2:8083" }
     ],
     "type": "sink"
   }
   ```

   Đếm gọn số task mỗi worker giữ:

   ```bash
   curl -s $W1/connectors/w6-orders-sink/status | jq -r '.tasks[].worker_id' | sort | uniq -c
   #  2 connect-1:8083
   #  2 connect-2:8083
   ```
3. **Gây hỏng:** giết `connect-2` (mô phỏng node chết, không phải shutdown êm).

   ```bash
   docker kill connect-2
   date +%T
   ```
4. Theo dõi trạng thái mỗi 15 s trong 2 phút. **Đừng sửa gì cả — chỉ nhìn.**

   ```bash
   for i in $(seq 1 8); do
     echo "--- $(date +%T)"
     curl -s $W1/connectors/w6-orders-sink/status \
       | jq -c '[.tasks[] | {id, state, worker_id}]'
     sleep 15
   done
   ```

   Bạn sẽ thấy hai giai đoạn:

   ```
   --- 10:12:05   (ngay sau khi kill, chưa hết session.timeout.ms 10 s)
   [{"id":0,"state":"RUNNING","worker_id":"connect-1:8083"},{"id":1,"state":"RUNNING","worker_id":"connect-2:8083"}, ...]
   --- 10:12:35   (đã phát hiện worker chết → task của nó thành UNASSIGNED, KHÔNG chuyển)
   [{"id":0,"state":"RUNNING","worker_id":"connect-1:8083"},{"id":1,"state":"UNASSIGNED","worker_id":"connect-1:8083"}, ...]
   ```

   Task `UNASSIGNED` sẽ **đứng yên tới 5 phút**. Đây không phải lỗi — đó là `scheduled.rebalance.max.delay.ms` mặc định **300000 ms**.
5. **Sửa cách 1 — bật lại worker trong thời gian hoãn.** Chạy trong vòng 5 phút kể từ bước 3:

   ```bash
   docker start connect-2
   until curl -s $W2/ >/dev/null; do sleep 3; done
   sleep 15
   curl -s $W1/connectors/w6-orders-sink/status | jq -r '.tasks[].worker_id' | sort | uniq -c
   #  2 connect-1:8083
   #  2 connect-2:8083      ← task trở về đúng worker cũ, cluster không bị xáo trộn
   ```
6. **Sửa cách 2 — hạ thời gian hoãn khi SLA đòi failover nhanh.** Tạo override thứ hai và khởi động lại 2 worker:

   ```yaml
   # ~/kafka-labs/docker-compose.connect2-fastfail.yml
   services:
     connect-1:
       environment:
         CONNECT_SCHEDULED_REBALANCE_MAX_DELAY_MS: 10000
     connect-2:
       environment:
         CONNECT_SCHEDULED_REBALANCE_MAX_DELAY_MS: 10000
   ```

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.connect2.yml:docker-compose.connect2-fastfail.yml
   docker compose up -d connect-1 connect-2
   for U in $W1 $W2; do until curl -s $U/ >/dev/null; do sleep 3; done; done

   docker kill connect-2 && date +%T
   sleep 30 && date +%T
   curl -s $W1/connectors/w6-orders-sink/status | jq -c '[.tasks[] | {id, state, worker_id}]'
   # 4 task đều RUNNING trên connect-1:8083 — chuyển trong ~20–25 s thay vì 5 phút
   ```
7. Khôi phục và (tuỳ chọn) đọc metric để xác nhận rebalance bằng số.

   ```bash
   docker start connect-2 && until curl -s $W2/ >/dev/null; do sleep 3; done

   # Tuỳ chọn — JMX. Nếu JmxTool báo sai tham số, chạy: docker exec connect-1 kafka-run-class org.apache.kafka.tools.JmxTool --help
   docker exec connect-1 kafka-run-class org.apache.kafka.tools.JmxTool \
     --jmx-url service:jmx:rmi:///jndi/rmi://connect-1:9585/jmxrmi \
     --object-name 'kafka.connect:type=connect-worker-metrics' \
     --attributes connector-count,task-count --one-time true
   docker exec connect-1 kafka-run-class org.apache.kafka.tools.JmxTool \
     --jmx-url service:jmx:rmi:///jndi/rmi://connect-1:9585/jmxrmi \
     --object-name 'kafka.connect:type=connect-worker-rebalance-metrics' \
     --attributes rebalancing,completed-rebalances-total,leader-name,epoch,time-since-last-rebalance-ms --one-time true
   ```

### ✅ Kiểm chứng

- Ngay sau `docker kill`, trạng thái **không đổi** trong ~10 s đầu (chưa hết `session.timeout.ms`).
- Sau đó task của worker chết chuyển sang **`UNASSIGNED`** và **đứng yên** — đó là bằng chứng trực tiếp của `scheduled.rebalance.max.delay.ms`.
- Bước 5: bật lại worker trong thời gian hoãn → phân bố task **trở về y như trước**, `completed-rebalances-total` tăng nhưng task không bị xáo.
- Bước 6: với delay 10 s, 4 task dồn hết về `connect-1` trong khoảng **20–25 s** (10 s phát hiện + 10 s hoãn + thời gian rebalance).
- `task-count` của `connect-1` tăng từ 2 lên 4 khi `connect-2` chết, và về lại 2 khi nó quay lại.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
# Quay về cấu hình mặc định (bỏ file fastfail) cho các lab sau:
export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.connect2.yml
docker compose up -d connect-1 connect-2
rm -f docker-compose.connect2-fastfail.yml
curl -s -X DELETE $W1/connectors/w6-orders-sink
# GIỮ cluster + topic w6-orders cho Lab 6.3.
```

### 🧠 Ý nghĩa với đề thi

- **Worker chết → Connect tự rebalance.** Đây là hành vi tự động duy nhất. Đừng chọn phương án "restart thủ công" cho tình huống worker chết.
- Câu hỏi "tôi kill worker 3 phút rồi mà task chưa chạy lại, cluster hỏng à?" có đáp án đúng là **`scheduled.rebalance.max.delay.ms` 5 phút**, không phải tăng `session.timeout.ms` hay restart cluster.
- Hạ delay = failover nhanh hơn nhưng mỗi lần rolling restart worker sẽ gây thêm một cặp rebalance thừa. Đây chính là dạng câu "đánh đổi nào" mà CCAAK thích hỏi.

---

## Lab 6.3 — `tasks.max` là TRẦN: chứng minh task dư nằm không

**🎯 Mục tiêu:** Đặt `tasks.max=6` cho một sink connector trên topic **3 partition** và chứng minh bằng ba nguồn độc lập rằng **6 task được tạo và RUNNING**, trong đó **3 task không sở hữu partition nào** — bác bỏ công thức `min(tasks.max, partitions)`.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc `GET /connectors/{n}/tasks` và `/status` để đếm task.
- Dùng `kcg --describe --group connect-<name> --members --verbose` để thấy member không có partition.
- Hiểu vì sao source connector lại khác (FileStream luôn 1 task).

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 6.1.

### Các bước

1. Tạo topic **3 partition** và bơm dữ liệu.

   ```bash
   kt --create --topic w6-narrow --partitions 3 --replication-factor 3
   for i in $(seq 1 30); do echo "line-$i"; done \
     | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
         --bootstrap-server kafka-1:19092 --topic w6-narrow
   ```
2. Tạo sink connector với `tasks.max=6`.

   ```bash
   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-wide-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "6",
     "topics": "w6-narrow",
     "file": "/data/narrow-sink.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.storage.StringConverter"
   }' | jq '{name, tasks: (.tasks | length)}'
   ```
3. **Bằng chứng 1 — REST:** đếm task.

   ```bash
   sleep 10
   curl -s $W1/connectors/w6-wide-sink/tasks | jq length            # 6
   curl -s $W1/connectors/w6-wide-sink/status | jq -c '[.tasks[] | {id, state}]'
   # [{"id":0,"state":"RUNNING"},{"id":1,"state":"RUNNING"},{"id":2,"state":"RUNNING"},
   #  {"id":3,"state":"RUNNING"},{"id":4,"state":"RUNNING"},{"id":5,"state":"RUNNING"}]
   ```
4. **Bằng chứng 2 — consumer group:** task sink là consumer, và 3 trong 6 member không được giao gì.

   ```bash
   kcg --describe --group connect-w6-wide-sink --members --verbose
   ```

   ```
   GROUP                    CONSUMER-ID                                   HOST          CLIENT-ID                     #PARTITIONS  ASSIGNMENT
   connect-w6-wide-sink     connector-consumer-w6-wide-sink-0-xxxxxxxx    /172.18.0.6   connector-consumer-...-0      1            w6-narrow(0)
   connect-w6-wide-sink     connector-consumer-w6-wide-sink-1-xxxxxxxx    /172.18.0.6   connector-consumer-...-1      1            w6-narrow(1)
   connect-w6-wide-sink     connector-consumer-w6-wide-sink-2-xxxxxxxx    /172.18.0.7   connector-consumer-...-2      1            w6-narrow(2)
   connect-w6-wide-sink     connector-consumer-w6-wide-sink-3-xxxxxxxx    /172.18.0.7   connector-consumer-...-3      0            -
   connect-w6-wide-sink     connector-consumer-w6-wide-sink-4-xxxxxxxx    /172.18.0.6   connector-consumer-...-4      0            -
   connect-w6-wide-sink     connector-consumer-w6-wide-sink-5-xxxxxxxx    /172.18.0.7   connector-consumer-...-5      0            -
   ```

   Đếm nhanh:

   ```bash
   kcg --describe --group connect-w6-wide-sink --members \
     | awk 'NR>1 && $NF=="0" {n++} END {print "Task khong co partition nao:", n+0}'
   # Task khong co partition nao: 3
   ```
5. **Bằng chứng 3 — metric:** `partition-count` của từng task.

   ```bash
   for T in 0 1 2 3 4 5; do
     docker exec connect-1 kafka-run-class org.apache.kafka.tools.JmxTool \
       --jmx-url service:jmx:rmi:///jndi/rmi://connect-1:9585/jmxrmi \
       --object-name "kafka.connect:type=sink-task-metrics,connector=\"w6-wide-sink\",task=\"$T\"" \
       --attributes partition-count --one-time true 2>/dev/null | tail -1
   done
   # Task nào nằm trên connect-1 sẽ in partition-count 1 hoặc 0; task trên connect-2 không có MBean ở đây.
   ```

   > 📌 MBean chỉ tồn tại trên **worker đang chạy task đó**. Đây cũng là bài học: metric Connect là **cục bộ theo worker**, phải gom từ mọi worker mới ra bức tranh cluster.
6. **Đối chứng với source:** FileStream source bỏ qua `tasks.max`.

   ```bash
   docker exec connect-1 bash -c 'printf "a\nb\nc\n" > /data/src.txt'
   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-file-source/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSourceConnector",
     "tasks.max": "5",
     "file": "/data/src.txt",
     "topic": "w6-src",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.storage.StringConverter"
   }' >/dev/null
   sleep 8
   curl -s $W1/connectors/w6-file-source/tasks | jq length     # 1  (tasks.max=5 nhưng connector chỉ tạo 1)
   ```
7. Thử cách **đúng** để tăng song song: tăng partition trước.

   ```bash
   kt --alter --topic w6-narrow --partitions 6
   sleep 20
   kcg --describe --group connect-w6-wide-sink --members \
     | awk 'NR>1 && $NF=="0" {n++} END {print "Task khong co partition nao:", n+0}'
   # Task khong co partition nao: 0     ← giờ cả 6 task đều có việc
   ```

### ✅ Kiểm chứng

- `GET /connectors/w6-wide-sink/tasks | jq length` trả **6**, không phải 3. Đây là bằng chứng gọn nhất bác bỏ `min(tasks.max, partitions)`.
- `kcg --describe --members --verbose` cho thấy **3 member với `#PARTITIONS = 0`** và cột `ASSIGNMENT` rỗng — chúng RUNNING mà không làm gì.
- Source connector chỉ tạo **1** task dù `tasks.max=5` → chứng minh "connector tự quyết", đúng cho cả hai chiều (ít hơn trần, hoặc bằng trần).
- Sau khi tăng partition lên 6, không còn task rỗng → cách tăng throughput đúng là **partition trước, `tasks.max` sau**.

### 🧹 Dọn dẹp

```bash
curl -s -X DELETE $W1/connectors/w6-wide-sink
curl -s -X DELETE $W1/connectors/w6-file-source
# GIỮ cluster cho Lab 6.4.
```

### 🧠 Ý nghĩa với đề thi

- `tasks.max` là **trần**; runtime gọi `taskConfigs(maxTasks)` và **connector** trả về số task thật.
- Sink task = consumer trong group `connect-<connector-name>` → thừa task là thừa **consumer idle**, tốn connection và thread, không tăng throughput một chút nào.
- Đề dump bên thứ ba dạy `min(tasks.max, partitions)`. Nó mô tả số task **có việc**, không phải số task **được tạo**. Khi đề hỏi "bao nhiêu task sẽ chạy", câu trả lời với sink connector phổ biến là **`tasks.max`**.

---

## Lab 6.4 — Task FAILED vì record hỏng → đọc trace → DLQ ⭐

> 🔥 **Lab "gây hỏng rồi sửa" số 2.** Đây là lab quan trọng nhất tuần.

**🎯 Mục tiêu:** Cố tình đưa một record hỏng vào topic để sink task chết, đọc `trace` trong `/status`, rồi đi qua **ba mức xử lý** theo đúng thứ tự mà đề hay hỏi: `errors.tolerance=none` (chết) → `all` **không** DLQ (mất im lặng) → `all` **+** DLQ (bắt được record kèm lý do).
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc stack trace trong `/status` và nhận ra giai đoạn lỗi là **converter**.
- `POST /connectors/{n}/restart?includeTasks=true&onlyFailed=true` và mã trả về 202.
- `errors.tolerance`, `errors.log.*`, `errors.deadletterqueue.*` và header `__connect.errors.*`.

**⏱️ ~45 phút** · **Yêu cầu trước:** Lab 6.1.

### Các bước

1. Tạo topic và một sink connector dùng `JsonConverter` (đòi value là JSON hợp lệ).

   ```bash
   kt --create --topic w6-payments --partitions 3 --replication-factor 3

   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-pay-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "3",
     "topics": "w6-payments",
     "file": "/data/payments.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.json.JsonConverter",
     "value.converter.schemas.enable": "false"
   }' | jq .name

   sleep 8
   curl -s $W1/connectors/w6-pay-sink/status | jq -c '[.connector.state] + [.tasks[].state]'
   # ["RUNNING","RUNNING","RUNNING","RUNNING"]
   ```
2. Gửi vài record **hợp lệ** để chắc chắn pipeline chạy.

   ```bash
   for i in 1 2 3; do echo "{\"id\":$i,\"amount\":10}"; done \
     | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
         --bootstrap-server kafka-1:19092 --topic w6-payments
   sleep 5
   docker exec connect-1 cat /data/payments.out 2>/dev/null; docker exec connect-2 cat /data/payments.out 2>/dev/null
   ```
3. **Gây hỏng:** gửi một record **không phải JSON** vào đúng partition 0.

   ```bash
   echo 'THIS-IS-NOT-JSON' \
     | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
         --bootstrap-server kafka-1:19092 --topic w6-payments \
         --property parse.key=false
   sleep 10
   ```
4. **Chẩn đoán:** đọc `/status`. Chú ý `connector.state` vẫn `RUNNING`.

   ```bash
   curl -s $W1/connectors/w6-pay-sink/status | jq '{connector: .connector.state, tasks: [.tasks[] | {id, state}]}'
   ```

   ```json
   {
     "connector": "RUNNING",
     "tasks": [
       { "id": 0, "state": "FAILED" },
       { "id": 1, "state": "RUNNING" },
       { "id": 2, "state": "RUNNING" }
     ]
   }
   ```

   Đọc `trace` của task chết:

   ```bash
   curl -s $W1/connectors/w6-pay-sink/status \
     | jq -r '.tasks[] | select(.state=="FAILED") | .trace' | head -20
   ```

   ```
   org.apache.kafka.connect.errors.ConnectException: Tolerance exceeded in error handler
       at org.apache.kafka.connect.runtime.errors.RetryWithToleranceOperator.execAndHandleError(RetryWithToleranceOperator.java:245)
       ...
   Caused by: org.apache.kafka.connect.errors.DataException: Converting byte[] to Kafka Connect data failed due to serialization error:
       at org.apache.kafka.connect.json.JsonConverter.toConnectData(JsonConverter.java:333)
       ...
   Caused by: com.fasterxml.jackson.core.JsonParseException: Unrecognized token 'THIS': was expecting (JSON String, Number, Array, Object or token 'null', 'true' or 'false')
    at [Source: (byte[])"THIS-IS-NOT-JSON"; line: 1, column: 6]
   ```

   Ba dòng này nói đúng ba điều: `Tolerance exceeded` = `errors.tolerance=none`; `DataException … serialization error` = giai đoạn **converter**; `JsonParseException` = nguyên nhân gốc.
5. **Thử restart mà chưa sửa gì** — để thấy vì sao restart suông vô ích.

   ```bash
   curl -s -X POST "$W1/connectors/w6-pay-sink/restart" -w "\nHTTP %{http_code}\n"
   # HTTP 204 — chỉ restart đối tượng connector
   sleep 8
   curl -s $W1/connectors/w6-pay-sink/status | jq -c '[.tasks[] | {id, state}]'
   # task 0 vẫn FAILED

   curl -s -X POST "$W1/connectors/w6-pay-sink/restart?includeTasks=true&onlyFailed=true" -w "\nHTTP %{http_code}\n"
   # HTTP 202
   sleep 10
   curl -s $W1/connectors/w6-pay-sink/status | jq -c '[.tasks[] | {id, state}]'
   # task 0 lại FAILED — restart không xoá record hỏng, nó vẫn nằm ở đó
   ```
6. **Sửa sai cách (để biết vì sao sai):** chỉ bật `errors.tolerance=all`, không DLQ.

   ```bash
   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-pay-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "3",
     "topics": "w6-payments",
     "file": "/data/payments.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.json.JsonConverter",
     "value.converter.schemas.enable": "false",
     "errors.tolerance": "all"
   }' >/dev/null
   sleep 12
   curl -s $W1/connectors/w6-pay-sink/status | jq -c '[.tasks[] | {id, state}]'
   # tất cả RUNNING — nhưng record "THIS-IS-NOT-JSON" đã BIẾN MẤT, không ai biết
   ```

   Gửi thêm một record hỏng nữa và xác nhận: task vẫn RUNNING, file đích không có gì mới, **không có log**, không có dấu vết.

   ```bash
   echo 'ALSO-BROKEN' | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic w6-payments
   sleep 8
   docker logs connect-1 2>&1 | tail -5     # không có gì về record hỏng
   ```
7. **Sửa đúng cách:** `errors.tolerance=all` + DLQ + log + header ngữ cảnh.

   ```bash
   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-pay-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "3",
     "topics": "w6-payments",
     "file": "/data/payments.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.json.JsonConverter",
     "value.converter.schemas.enable": "false",
     "errors.tolerance": "all",
     "errors.log.enable": "true",
     "errors.log.include.messages": "true",
     "errors.deadletterqueue.topic.name": "w6-payments-dlq",
     "errors.deadletterqueue.topic.replication.factor": "3",
     "errors.deadletterqueue.context.headers.enable": "true"
   }' >/dev/null
   sleep 12
   curl -s $W1/connectors/w6-pay-sink/status | jq -c '[.tasks[] | {id, state}]'
   ```
8. Gửi record hỏng thứ ba và **đọc DLQ kèm header**.

   ```bash
   echo 'BROKEN-WITH-DLQ' | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic w6-payments
   sleep 10

   kt --list | grep w6-payments-dlq
   kt --describe --topic w6-payments-dlq | head -1
   # Topic: w6-payments-dlq   PartitionCount: 3   ReplicationFactor: 3

   docker exec kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic w6-payments-dlq \
     --from-beginning --timeout-ms 10000 \
     --property print.headers=true --property print.value=true
   ```

   Output (đã xuống dòng cho dễ đọc):

   ```
   __connect.errors.topic:w6-payments,__connect.errors.partition:1,__connect.errors.offset:4,
   __connect.errors.connector.name:w6-pay-sink,__connect.errors.task.id:1,
   __connect.errors.stage:VALUE_CONVERTER,
   __connect.errors.class.name:org.apache.kafka.connect.json.JsonConverter,
   __connect.errors.exception.class.name:org.apache.kafka.connect.errors.DataException,
   __connect.errors.exception.message:Converting byte[] to Kafka Connect data failed due to serialization error:,
   __connect.errors.exception.stacktrace:org.apache.kafka.connect.errors.DataException: ...
        BROKEN-WITH-DLQ
   ```
9. Xem bộ đếm lỗi.

   ```bash
   docker exec connect-1 kafka-run-class org.apache.kafka.tools.JmxTool \
     --jmx-url service:jmx:rmi:///jndi/rmi://connect-1:9585/jmxrmi \
     --object-name 'kafka.connect:type=task-error-metrics,connector="w6-pay-sink",task="1"' \
     --attributes total-record-errors,total-records-skipped,deadletterqueue-produce-requests,deadletterqueue-produce-failures \
     --one-time true
   ```

### ✅ Kiểm chứng

- Bước 4: `connector.state` là **RUNNING** trong khi một task **FAILED** — nhìn mỗi `connector.state` là bỏ sót sự cố. `trace` chỉ đúng ba tầng nguyên nhân.
- Bước 5: `restart` suông trả **204** và task vẫn FAILED; `restart?includeTasks=true&onlyFailed=true` trả **202**. Cả hai đều không cứu được vì record hỏng vẫn nằm ở offset đó — **restart không phải cách sửa lỗi dữ liệu**.
- Bước 6: task RUNNING, file đích không có record hỏng, log sạch trơn. Đây chính là "mất dữ liệu im lặng".
- Bước 8: topic `w6-payments-dlq` được tạo tự động với RF 3, record hỏng nằm trong đó **kèm 10 header `__connect.errors.*`**, trong đó `stage` = `VALUE_CONVERTER` và bộ ba `topic`/`partition`/`offset` cho phép truy ngược record gốc.
- Bước 9: `deadletterqueue-produce-requests` ≥ 1 và `deadletterqueue-produce-failures` = 0.

### 🧹 Dọn dẹp

```bash
curl -s -X DELETE $W1/connectors/w6-pay-sink
kt --delete --topic w6-payments-dlq
# GIỮ topic w6-payments và cluster cho Lab 6.5.
```

### 🧠 Ý nghĩa với đề thi

- **Ba mức xử lý lỗi** là câu hỏi lặp đi lặp lại: `none` (chết, mặc định) → `all` không DLQ (**mất im lặng** — phương án bẫy) → `all` + DLQ (đúng).
- **DLQ chỉ có ở sink connector.** Source connector không có bất kỳ key `errors.deadletterqueue.*` nào.
- `errors.deadletterqueue.context.headers.enable` mặc định **false**. DLQ không header = một đống byte vô nghĩa. Bật nó gần như luôn là đáp án đúng.
- `errors.deadletterqueue.topic.replication.factor` mặc định **3**: trên cluster nhỏ hơn 3 broker, connector sẽ chết đúng lúc cần DLQ nhất.
- `connector.state=RUNNING` **không** bảo đảm gì. Luôn đọc mảng `tasks[]`.

---

## Lab 6.5 — Quản lý offset: đọc, reset sink bằng CLI, xoá offset source bằng REST

**🎯 Mục tiêu:** Thấy tận mắt hai hình dạng offset khác nhau của source và sink, reset offset sink bằng `kafka-consumer-groups.sh`, xoá offset source bằng `DELETE /offsets` — và chứng minh **xoá connector không xoá offset**.
**🧩 Luyện kỹ năng (liên quan đề):**

- `GET /connectors/{n}/offsets` cho cả hai loại connector.
- Quy trình `PUT /stop` → `DELETE /offsets` → `PUT /resume`, và vì sao `PAUSED` không đủ.
- `kafka-consumer-groups.sh --reset-offsets` với group `connect-<name>`: cần **inactive** và cần **`--execute`**.

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 6.1 (cluster đang chạy), topic `w6-payments` từ Lab 6.4.

### Các bước

1. Dựng lại một cặp source + sink sạch.

   ```bash
   docker exec connect-1 bash -c 'printf "alpha\nbravo\ncharlie\ndelta\n" > /data/offsets-src.txt'
   docker exec connect-2 bash -c 'printf "alpha\nbravo\ncharlie\ndelta\n" > /data/offsets-src.txt'

   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-off-source/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSourceConnector",
     "tasks.max": "1",
     "file": "/data/offsets-src.txt",
     "topic": "w6-lines",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.storage.StringConverter"
   }' >/dev/null

   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-off-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "1",
     "topics": "w6-lines",
     "file": "/data/offsets-sink.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.storage.StringConverter"
   }' >/dev/null
   sleep 20
   kcc --topic w6-lines --from-beginning --timeout-ms 8000     # alpha bravo charlie delta
   ```
2. Đọc offset của **cả hai** — chú ý hai shape hoàn toàn khác nhau.

   ```bash
   curl -s $W1/connectors/w6-off-source/offsets | jq
   ```

   ```json
   {
     "offsets": [
       {
         "partition": { "filename": "/data/offsets-src.txt" },
         "offset": { "position": 25 }
       }
     ]
   }
   ```

   ```bash
   curl -s $W1/connectors/w6-off-sink/offsets | jq
   ```

   ```json
   {
     "offsets": [
       {
         "partition": { "kafka_topic": "w6-lines", "kafka_partition": 0 },
         "offset": { "kafka_offset": 4 }
       }
     ]
   }
   ```

   Source: cặp key/value **do connector định nghĩa** (`filename` → `position` byte). Sink: luôn là **toạ độ Kafka**.
3. Xác nhận offset sink cũng là một **consumer group bình thường**.

   ```bash
   kcg --list | grep connect-
   # connect-w6-off-sink
   kcg --describe --group connect-w6-off-sink
   # TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
   # w6-lines  0          4               4               0
   ```
4. **Chứng minh xoá connector không xoá offset.**

   ```bash
   curl -s -X DELETE $W1/connectors/w6-off-sink -w "HTTP %{http_code}\n"     # 204
   sleep 5
   kcg --describe --group connect-w6-off-sink        # group VẪN CÒN với offset 4
   docker exec connect-1 rm -f /data/offsets-sink.out; docker exec connect-2 rm -f /data/offsets-sink.out

   # Tạo lại y hệt, cùng tên
   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-off-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "1",
     "topics": "w6-lines",
     "file": "/data/offsets-sink.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.storage.StringConverter"
   }' >/dev/null
   sleep 15
   docker exec connect-1 cat /data/offsets-sink.out 2>/dev/null
   docker exec connect-2 cat /data/offsets-sink.out 2>/dev/null
   # RỖNG — connector mới tiếp tục từ offset 4, không đọc lại 4 dòng cũ
   ```
5. **Reset sink bằng CLI** (cách "cổ điển", vẫn được hỏi trong đề). Group phải **inactive** → dừng connector trước.

   ```bash
   # Thử reset khi connector còn chạy → lỗi
   kcg --group connect-w6-off-sink --topic w6-lines --reset-offsets --to-earliest --execute
   # Error: Assignments can only be reset if the group 'connect-w6-off-sink' is inactive...

   curl -s -X PUT $W1/connectors/w6-off-sink/stop -w "HTTP %{http_code}\n"    # 202
   sleep 8
   curl -s $W1/connectors/w6-off-sink/status | jq -c '[.connector.state, (.tasks|length)]'
   # ["STOPPED",0]   ← task bị huỷ hẳn, group không còn member

   kcg --group connect-w6-off-sink --topic w6-lines --reset-offsets --to-earliest       # dry-run
   kcg --group connect-w6-off-sink --topic w6-lines --reset-offsets --to-earliest --execute

   curl -s -X PUT $W1/connectors/w6-off-sink/resume -w "HTTP %{http_code}\n"
   sleep 15
   docker exec connect-1 cat /data/offsets-sink.out 2>/dev/null
   docker exec connect-2 cat /data/offsets-sink.out 2>/dev/null
   # alpha bravo charlie delta  ← đã đọc lại từ đầu
   ```
6. **Reset source bằng REST** — và thử sai trước để thấy lỗi.

   ```bash
   # Sai: gọi khi đang RUNNING
   curl -s -X DELETE $W1/connectors/w6-off-source/offsets -w "\nHTTP %{http_code}\n"
   # {"error_code":400,"message":"Connectors must be in a stopped state before their offsets can be modified..."}

   # Sai: PAUSED là chưa đủ
   curl -s -X PUT $W1/connectors/w6-off-source/pause >/dev/null; sleep 6
   curl -s -X DELETE $W1/connectors/w6-off-source/offsets -w "\nHTTP %{http_code}\n"
   # vẫn bị từ chối

   # Đúng: STOPPED
   curl -s -X PUT $W1/connectors/w6-off-source/stop >/dev/null; sleep 8
   curl -s $W1/connectors/w6-off-source/status | jq -c '[.connector.state, (.tasks|length)]'   # ["STOPPED",0]
   curl -s -X DELETE $W1/connectors/w6-off-source/offsets | jq
   # {"message":"The offsets for this connector have been reset successfully"}

   curl -s $W1/connectors/w6-off-source/offsets | jq        # {"offsets":[]}
   curl -s -X PUT $W1/connectors/w6-off-source/resume >/dev/null
   sleep 20
   kcc --topic w6-lines --from-beginning --timeout-ms 8000 | wc -l
   # 8 — source đã đọc lại toàn bộ file và ghi thêm 4 dòng nữa (duplicate có chủ đích)
   ```
7. (Tuỳ chọn) Sửa **một** partition bằng `PATCH` thay vì xoá hết.

   ```bash
   curl -s -X PUT $W1/connectors/w6-off-sink/stop >/dev/null; sleep 8
   curl -s -X PATCH -H "Content-Type: application/json" $W1/connectors/w6-off-sink/offsets --data '{
     "offsets": [
       { "partition": {"kafka_topic":"w6-lines","kafka_partition":0}, "offset": {"kafka_offset": 2} }
     ]
   }' | jq
   curl -s -X PUT $W1/connectors/w6-off-sink/resume >/dev/null
   ```

### ✅ Kiểm chứng

- Shape offset của source là `{"filename": …} → {"position": …}`; của sink là `{"kafka_topic","kafka_partition"} → {"kafka_offset"}`. Hai thế giới khác nhau, và đây là câu hỏi Matching điển hình.
- Bước 4: xoá connector rồi tạo lại cùng tên → file đích **rỗng**, group `connect-w6-off-sink` vẫn giữ offset cũ. Đây là bằng chứng "`DELETE` không xoá offset".
- Bước 5: reset khi group còn active báo lỗi `Assignments can only be reset if the group … is inactive`; `--reset-offsets` không có `--execute` chỉ **in ra** chứ không đổi gì.
- Bước 6: `DELETE /offsets` bị từ chối cả khi `RUNNING` **và** khi `PAUSED`; chỉ chấp nhận khi `STOPPED` (`tasks` length = 0).

### 🧹 Dọn dẹp

```bash
curl -s -X DELETE $W1/connectors/w6-off-source
curl -s -X DELETE $W1/connectors/w6-off-sink
kcg --group connect-w6-off-sink --delete 2>/dev/null
kt --delete --topic w6-lines
# GIỮ cluster cho Lab 6.7. (Lab 6.6 sẽ dựng lại stack có SASL.)
```

### 🧠 Ý nghĩa với đề thi

- Câu hỏi *"connector đã bị xoá, tạo lại cùng tên, vì sao không đọc lại dữ liệu cũ?"* → **offset không bị xoá cùng connector**.
- Câu hỏi *"trước khi reset offset phải làm gì?"* → **`PUT /stop`** (STOPPED), **không** phải `pause`.
- Reset sink có **hai** cách đúng: REST (`stop` → `DELETE /offsets` → `resume`) và CLI (`kafka-consumer-groups.sh --reset-offsets … --execute` trên group `connect-<name>`, group phải inactive). Reset source **chỉ có REST**.

---

## Lab 6.6 — Cho một connector chạy bằng credential SCRAM riêng

**🎯 Mục tiêu:** Bật SASL/SCRAM trên cluster, cho worker chạy bằng `User:connect-worker`, rồi cho **một** connector dùng `User:connect-payments` qua `consumer.override.sasl.jaas.config` với policy `Principal` — và chứng minh thu hồi quyền của user đó chỉ giết connector đó, không ảnh hưởng connector khác.
**🧩 Luyện kỹ năng (liên quan đề):**

- `connector.client.config.override.policy`: `None` / `Principal` / `All` / `Allowlist`, và mặc định thật ở Kafka 4.3 là **`All`**.
- Prefix `consumer.override.*` / `producer.override.*` / `admin.override.*`.
- ACL mà sink connector cần: `Read` trên **topic** *và* `Read` trên **Group `connect-<name>`**.

**⏱️ ~50 phút** · **Yêu cầu trước:** Đã xong Lab 6.1 → 6.5.
> ⚠️ Lab này **dựng lại cluster** với listener SASL mới → dữ liệu và connector của các lab trước sẽ mất. Làm lab này sau cùng trong nhóm 6.1–6.5.

### Các bước

1. Tắt stack hiện tại và tạo override thêm listener `SASL_PLAINTEXT://:19093` cho cả 3 broker.

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.connect2.yml
   docker compose down
   ```

   ```yaml
   # ~/kafka-labs/docker-compose.sasl-brokers.yml
   # Thêm listener SASL_PLAINTEXT://:19093 và bật authorizer.
   # super.users = User:ANONYMOUS để traffic PLAINTEXT cũ (inter-broker, controller, CLI) không bị chặn.
   x-sasl-common: &sasl-common
     KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,SASL:SASL_PLAINTEXT
     KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
     KAFKA_AUTHORIZER_CLASS_NAME: org.apache.kafka.metadata.authorizer.StandardAuthorizer
     KAFKA_SUPER_USERS: User:ANONYMOUS

   services:
     kafka-1:
       environment:
         <<: *sasl-common
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9092,SASL://:19093
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:19092,PLAINTEXT_HOST://localhost:9092,SASL://kafka-1:19093
     kafka-2:
       environment:
         <<: *sasl-common
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9094,SASL://:19093
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-2:19092,PLAINTEXT_HOST://localhost:9094,SASL://kafka-2:19093
     kafka-3:
       environment:
         <<: *sasl-common
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9096,SASL://:19093
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-3:19092,PLAINTEXT_HOST://localhost:9096,SASL://kafka-3:19093
   ```

   ```bash
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.sasl-brokers.yml
   docker compose up -d
   sleep 25
   docker compose logs kafka-1 | grep -iE "SASL|started" | tail -3
   ```
2. Tạo 2 user SCRAM **lúc cluster đang chạy** (qua listener PLAINTEXT nội bộ).

   ```bash
   for U in connect-worker:worker-secret connect-payments:payments-secret; do
     NAME=${U%%:*}; PW=${U##*:}
     docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 \
       --alter --add-config "SCRAM-SHA-512=[password=$PW]" --entity-type users --entity-name $NAME
   done
   docker exec kafka-1 /opt/kafka/bin/kafka-configs.sh --bootstrap-server kafka-1:19092 \
     --describe --entity-type users
   ```
3. Cấp ACL. `connect-worker` cần quyền rộng (internal topic + group của worker); `connect-payments` chỉ được đọc đúng một topic và một group.

   ```bash
   ACL() { docker exec kafka-1 /opt/kafka/bin/kafka-acls.sh --bootstrap-server kafka-1:19092 "$@"; }

   # Worker: tạo topic + đọc/ghi mọi thứ nó cần
   ACL --add --allow-principal User:connect-worker --operation All --cluster
   ACL --add --allow-principal User:connect-worker --operation All --topic '*'
   ACL --add --allow-principal User:connect-worker --operation All --group '*'

   # Connector payments: CHỈ đọc topic w6-secure và group connect-w6-secure-sink
   ACL --add --allow-principal User:connect-payments --operation Read --operation Describe --topic w6-secure
   ACL --add --allow-principal User:connect-payments --operation Read --group connect-w6-secure-sink

   ACL --list --principal User:connect-payments
   ```
4. Tạo override cho worker: dùng listener SASL và bật policy **`Principal`**.

   ```yaml
   # ~/kafka-labs/docker-compose.connect2-sasl.yml
   x-connect-sasl: &connect-sasl
     CONNECT_BOOTSTRAP_SERVERS: kafka-1:19093,kafka-2:19093,kafka-3:19093
     CONNECT_SECURITY_PROTOCOL: SASL_PLAINTEXT
     CONNECT_SASL_MECHANISM: SCRAM-SHA-512
     CONNECT_SASL_JAAS_CONFIG: 'org.apache.kafka.common.security.scram.ScramLoginModule required username="connect-worker" password="worker-secret";'
     # Lặp lại cho 3 client mà worker tạo ra — cách an toàn nhất, không phụ thuộc kế thừa
     CONNECT_PRODUCER_SECURITY_PROTOCOL: SASL_PLAINTEXT
     CONNECT_PRODUCER_SASL_MECHANISM: SCRAM-SHA-512
     CONNECT_PRODUCER_SASL_JAAS_CONFIG: 'org.apache.kafka.common.security.scram.ScramLoginModule required username="connect-worker" password="worker-secret";'
     CONNECT_CONSUMER_SECURITY_PROTOCOL: SASL_PLAINTEXT
     CONNECT_CONSUMER_SASL_MECHANISM: SCRAM-SHA-512
     CONNECT_CONSUMER_SASL_JAAS_CONFIG: 'org.apache.kafka.common.security.scram.ScramLoginModule required username="connect-worker" password="worker-secret";'
     CONNECT_ADMIN_SECURITY_PROTOCOL: SASL_PLAINTEXT
     CONNECT_ADMIN_SASL_MECHANISM: SCRAM-SHA-512
     CONNECT_ADMIN_SASL_JAAS_CONFIG: 'org.apache.kafka.common.security.scram.ScramLoginModule required username="connect-worker" password="worker-secret";'
     # ---- Cổng chính sách: Principal chỉ cho override security.protocol / sasl.mechanism / sasl.jaas.config ----
     CONNECT_CONNECTOR_CLIENT_CONFIG_OVERRIDE_POLICY: Principal

   services:
     connect-1:
       environment:
         <<: *connect-sasl
     connect-2:
       environment:
         <<: *connect-sasl
   ```

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.sasl-brokers.yml:docker-compose.connect2.yml:docker-compose.connect2-sasl.yml
   docker compose up -d
   for U in $W1 $W2; do until curl -s $U/ >/dev/null; do sleep 3; done; done
   kt --create --topic w6-secure --partitions 3 --replication-factor 3
   kt --create --topic w6-open --partitions 3 --replication-factor 3
   ```
5. Tạo **hai** connector: một dùng credential riêng, một dùng credential của worker.

   ```bash
   # (a) Connector dùng principal RIÊNG
   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-secure-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "1",
     "topics": "w6-secure",
     "file": "/data/secure.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.storage.StringConverter",
     "consumer.override.security.protocol": "SASL_PLAINTEXT",
     "consumer.override.sasl.mechanism": "SCRAM-SHA-512",
     "consumer.override.sasl.jaas.config": "org.apache.kafka.common.security.scram.ScramLoginModule required username=\"connect-payments\" password=\"payments-secret\";"
   }' | jq .name

   # (b) Connector dùng credential mặc định của worker
   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-open-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "1",
     "topics": "w6-open",
     "file": "/data/open.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.storage.StringConverter"
   }' | jq .name

   sleep 12
   for C in w6-secure-sink w6-open-sink; do
     echo -n "$C: "; curl -s $W1/connectors/$C/status | jq -c '[.connector.state] + [.tasks[].state]'
   done
   # w6-secure-sink: ["RUNNING","RUNNING"]
   # w6-open-sink:   ["RUNNING","RUNNING"]
   ```

   Bơm dữ liệu và kiểm cả hai chạy:

   ```bash
   for i in 1 2 3; do echo "secure-$i"; done | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic w6-secure
   for i in 1 2 3; do echo "open-$i"; done   | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic w6-open
   sleep 10
   docker exec connect-1 cat /data/secure.out /data/open.out 2>/dev/null
   docker exec connect-2 cat /data/secure.out /data/open.out 2>/dev/null
   ```
6. **Gây hỏng có chủ đích:** thu hồi ACL Group của `connect-payments` và xem **chỉ** connector đó chết.

   ```bash
   ACL --remove --allow-principal User:connect-payments --operation Read --group connect-w6-secure-sink --force
   curl -s -X POST "$W1/connectors/w6-secure-sink/restart?includeTasks=true" >/dev/null
   sleep 15

   curl -s $W1/connectors/w6-secure-sink/status | jq -r '.tasks[0].trace' | head -3
   # org.apache.kafka.common.errors.GroupAuthorizationException: Not authorized to access group: connect-w6-secure-sink

   curl -s $W1/connectors/w6-open-sink/status | jq -c '[.tasks[].state]'
   # ["RUNNING"]   ← connector kia không hề bị ảnh hưởng
   ```
7. **Sửa:** cấp lại ACL rồi restart.

   ```bash
   ACL --add --allow-principal User:connect-payments --operation Read --group connect-w6-secure-sink
   curl -s -X POST "$W1/connectors/w6-secure-sink/restart?includeTasks=true&onlyFailed=true" -w "\nHTTP %{http_code}\n"
   sleep 12
   curl -s $W1/connectors/w6-secure-sink/status | jq -c '[.tasks[].state]'     # ["RUNNING"]
   ```
8. Thấy **cổng chính sách** hoạt động: thử override một config **ngoài** danh sách của `Principal`.

   ```bash
   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-secure-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "1",
     "topics": "w6-secure",
     "file": "/data/secure.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.storage.StringConverter",
     "consumer.override.max.poll.records": "10"
   }' | jq '{error_code, message}'
   # {"error_code":400,"message":"Connector configuration is invalid ... The 'Principal' policy does not allow 'max.poll.records' to be overridden ..."}
   ```

### ✅ Kiểm chứng

- Bước 5: cả hai connector RUNNING, nhưng chúng **xác thực bằng hai principal khác nhau**. Kiểm bằng log broker: `docker compose logs kafka-1 | grep -i "connect-payments"`.
- Bước 6: thu hồi quyền của một principal → **đúng một** connector chuyển FAILED với `GroupAuthorizationException`; connector còn lại RUNNING. Đó chính là giá trị của việc tách credential.
- Bước 8: policy `Principal` **từ chối** override `max.poll.records` ngay ở bước validate config (400) — REST trả lỗi trước khi connector được tạo.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
curl -s -X DELETE $W1/connectors/w6-secure-sink
curl -s -X DELETE $W1/connectors/w6-open-sink
docker compose down
rm -f docker-compose.sasl-brokers.yml docker-compose.connect2-sasl.yml
# Dựng lại stack thường cho Lab 6.7:
export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.connect2.yml
docker compose up -d
```

### 🧠 Ý nghĩa với đề thi

- Mặc định **mọi connector dùng chung principal của worker**. Tách credential bằng `consumer.override.*` / `producer.override.*` là cách giới hạn bán kính thiệt hại — nhưng chỉ chạy được khi worker đã bật `connector.client.config.override.policy`.
- Bốn giá trị policy: `None` · `Principal` (đúng 3 config: `security.protocol`, `sasl.mechanism`, `sasl.jaas.config`) · `All` · `Allowlist` (4.2+). **Mặc định Apache Kafka 4.3 là `All`**, và docs khuyến nghị chuyển sang `Allowlist` — sẽ thành mặc định ở 5.0.
- Sink connector cần **hai** ACL: `Read` trên topic **và** `Read` trên Group `connect-<connector-name>`. Thiếu cái thứ hai cho ra `GroupAuthorizationException`, không phải `TopicAuthorizationException`.

---

## Lab 6.7 — Pause/resume và rolling restart worker không mất dữ liệu

**🎯 Mục tiêu:** Phân biệt `pause` (task còn sống) với `stop` (task bị huỷ) bằng số liệu, rồi thực hiện **rolling restart** cả hai worker trong khi producer vẫn bơm dữ liệu — và chứng minh bằng phép đếm rằng không mất record nào.
**🧩 Luyện kỹ năng (liên quan đề):**

- `PUT /pause` vs `PUT /stop` vs `PUT /resume`, và tính **bất đồng bộ** của pause.
- Thứ tự rolling restart an toàn: tắt êm → chờ `/status` về RUNNING → worker tiếp theo.
- Tại sao at-least-once nghĩa là "không mất, có thể trùng".

**⏱️ ~30 phút** · **Yêu cầu trước:** stack thường đang chạy (Lab 6.1, hoặc phần dọn dẹp của Lab 6.6).

### Các bước

1. Dựng pipeline đếm được: topic 3 partition + sink ghi ra file.

   ```bash
   kt --create --topic w6-roll --partitions 3 --replication-factor 3
   docker exec connect-1 bash -c 'rm -f /data/roll.out'; docker exec connect-2 bash -c 'rm -f /data/roll.out'

   curl -s -X PUT -H "Content-Type: application/json" $W1/connectors/w6-roll-sink/config --data '{
     "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
     "tasks.max": "3",
     "topics": "w6-roll",
     "file": "/data/roll.out",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.storage.StringConverter"
   }' >/dev/null
   sleep 10
   curl -s $W1/connectors/w6-roll-sink/status | jq -c '[.tasks[] | {id, state, worker_id}]'
   ```
2. **`pause` — task còn sống.**

   ```bash
   curl -s -X PUT $W1/connectors/w6-roll-sink/pause -w "HTTP %{http_code}\n"     # 202
   sleep 2
   curl -s $W1/connectors/w6-roll-sink/status | jq -c '[.connector.state] + [.tasks[].state]'
   # Ngay lập tức có thể vẫn là ["PAUSED","RUNNING","RUNNING","RUNNING"] — pause là BẤT ĐỒNG BỘ
   sleep 8
   curl -s $W1/connectors/w6-roll-sink/status | jq -c '[.connector.state] + [.tasks[].state]'
   # ["PAUSED","PAUSED","PAUSED","PAUSED"] — nhưng số task VẪN LÀ 3
   curl -s $W1/connectors/w6-roll-sink/tasks | jq length      # 3
   ```

   Bơm dữ liệu khi đang PAUSED — nó sẽ nằm chờ trong topic:

   ```bash
   for i in $(seq 1 30); do echo "p-$i"; done | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic w6-roll
   sleep 6
   docker exec connect-1 wc -l /data/roll.out 2>/dev/null; docker exec connect-2 wc -l /data/roll.out 2>/dev/null
   # 0 dòng (hoặc file chưa tồn tại)
   kcg --describe --group connect-w6-roll-sink        # LAG = 30
   ```
3. **`resume` — bắt kịp, không mất gì.**

   ```bash
   curl -s -X PUT $W1/connectors/w6-roll-sink/resume >/dev/null
   sleep 15
   docker exec connect-1 wc -l /data/roll.out 2>/dev/null; docker exec connect-2 wc -l /data/roll.out 2>/dev/null
   kcg --describe --group connect-w6-roll-sink        # LAG = 0
   ```
4. **Đối chứng `stop` — task bị huỷ hẳn.**

   ```bash
   curl -s -X PUT $W1/connectors/w6-roll-sink/stop >/dev/null; sleep 8
   curl -s $W1/connectors/w6-roll-sink/status | jq -c '[.connector.state, (.tasks|length)]'
   # ["STOPPED",0]        ← khác hẳn PAUSED (vẫn 3 task)
   kcg --list | grep connect-w6-roll-sink       # group vẫn tồn tại nhưng không còn member
   curl -s -X PUT $W1/connectors/w6-roll-sink/resume >/dev/null; sleep 12
   curl -s $W1/connectors/w6-roll-sink/status | jq -c '[.connector.state, (.tasks|length)]'   # ["RUNNING",3]
   ```
5. **Rolling restart trong khi dữ liệu vẫn chảy.** Mở terminal thứ hai cho producer:

   ```bash
   # Terminal 2 — bơm 300 record trong ~60 s
   for i in $(seq 1 300); do echo "r-$i"; sleep 0.2; done \
     | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
         --bootstrap-server kafka-1:19092 --topic w6-roll
   ```

   ```bash
   # Terminal 1 — rolling restart ĐÚNG THỨ TỰ
   docker stop connect-1                 # tắt ÊM, không kill -9
   until curl -s $W2/connectors/w6-roll-sink/status | jq -e '[.tasks[].state] | all(. == "RUNNING")' >/dev/null; do
     echo "cho task on dinh tren connect-2..."; sleep 5
   done
   docker start connect-1
   until curl -s $W1/ >/dev/null; do sleep 3; done
   sleep 20

   docker stop connect-2
   until curl -s $W1/connectors/w6-roll-sink/status | jq -e '[.tasks[].state] | all(. == "RUNNING")' >/dev/null; do
     echo "cho task on dinh tren connect-1..."; sleep 5
   done
   docker start connect-2
   until curl -s $W2/ >/dev/null; do sleep 3; done
   ```
6. **Đếm để chứng minh không mất dữ liệu.**

   ```bash
   sleep 25
   kcg --describe --group connect-w6-roll-sink                 # LAG phải về 0

   # Số record trong topic
   docker exec kafka-1 /opt/kafka/bin/kafka-run-class.sh org.apache.kafka.tools.GetOffsetShell \
     --bootstrap-server kafka-1:19092 --topic w6-roll | awk -F: '{s+=$3} END {print "Topic co", s, "record"}'

   # Số dòng đã ghi ra file (file nằm trên worker đang giữ task — cộng cả hai)
   A=$(docker exec connect-1 sh -c 'wc -l < /data/roll.out 2>/dev/null || echo 0')
   B=$(docker exec connect-2 sh -c 'wc -l < /data/roll.out 2>/dev/null || echo 0')
   echo "File ghi duoc: $((A+B)) dong"
   ```

### ✅ Kiểm chứng

- `pause` giữ nguyên **3 task** (`/tasks` trả 3) và LAG tăng dần; `stop` cho `tasks` length = **0**. Đây là khác biệt phải nói được không cần tra.
- Ngay sau `PUT /pause`, có thể connector đã `PAUSED` mà task còn `RUNNING` vài giây — chứng minh docs nói đúng: *"This call asynchronous and the tasks will not transition to `PAUSED` state at the same time."*
- Sau rolling restart, `LAG = 0` và **số dòng ghi ra ≥ số record trong topic**. Bằng nhau là lý tưởng; lớn hơn là **duplicate** ở ranh giới commit — đúng semantics at-least-once, **không phải lỗi**.
- Không có lúc nào cả hai worker cùng tắt → luôn còn worker nhận task.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
curl -s -X DELETE $W1/connectors/w6-roll-sink
kt --delete --topic w6-roll
kt --delete --topic w6-orders
kt --delete --topic w6-narrow
kt --delete --topic w6-src
kt --delete --topic w6-payments
docker compose down
rm -rf ~/kafka-labs/week-06/connect-data
unset COMPOSE_FILE W1 W2
# GIỮ docker-compose.connect2.yml — capstone Tuần 8 dùng lại nguyên file này.
```

### 🧠 Ý nghĩa với đề thi

- `pause` = **task còn sống**, ngừng poll/put, chuyển trạng thái **bất đồng bộ**. `stop` = **huỷ task**, giữ config + offset, là điều kiện bắt buộc để sửa offset.
- Rolling restart an toàn = tắt **êm** từng worker, **chờ mọi task RUNNING** rồi mới sang worker tiếp theo. Không bao giờ restart song song.
- Connect cho **at-least-once** mặc định: rolling restart không mất record, nhưng có thể trùng ở ranh giới commit. Muốn exactly-once cho source thì cần `exactly.once.source.support` (worker) + `exactly.once.support` (connector) — và vẫn không có exactly-once cho sink phía hệ đích.

---

> ✅ Xong 7 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist), rồi làm [bộ 28 câu luyện tập](questions.md). Hai lab bạn nên làm **lần thứ hai mà không nhìn hướng dẫn** là **6.2** (worker chết) và **6.4** (task chết → DLQ) — đó là hai tình huống mà đề CCAAK hỏi dưới dạng "người vận hành làm gì tiếp theo". Giữ lại `docker-compose.connect2.yml` nếu bạn muốn dùng lại Connect ở capstone Tuần 8.
