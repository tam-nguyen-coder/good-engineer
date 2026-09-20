# 🧪 Hands-on Labs — Tuần 7: Observability + Troubleshooting playbook

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ **Tuần này là tuần chẩn đoán:** 5 trong 7 lab là dạng **"gây hỏng rồi sửa"**. Mục tiêu không phải là chạy hết lệnh, mà là **quan sát đúng thứ tự**: metric → log → config → hành động.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung

### 1) Hai file compose chuẩn + stack giám sát

Tuần này **không định nghĩa lại** file nào đã có. Dùng nguyên:

| File | Định nghĩa ở | Nội dung |
|---|---|---|
| `~/kafka-labs/docker-compose.cluster.yml` | [CCDAK Tuần 1 — Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md) | `controller` (node.id **1**) + `kafka-1` (**2**) + `kafka-2` (**3**) + `kafka-3` (**4**); host port **9092 / 9094 / 9096**; listener nội bộ `kafka-N:19092`; RF mặc định 3, `min.insync.replicas` 2 |
| `~/kafka-labs/docker-compose.monitoring.yml` | [CCDAK Tuần 8 — Lab 8.1](../../../CCDAK/study-plan/week-08/labs.md) | JMX Exporter javaagent trên **3 broker** (7071/7072/7073) + `prometheus` (9090) + `grafana` (3000) |

```bash
cd ~/kafka-labs
export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.monitoring.yml
docker compose up -d
docker compose ps        # controller, kafka-1/2/3, prometheus, grafana đều running
```

> ⚠️ Nếu `~/kafka-labs/jmx/`, `~/kafka-labs/prometheus/` chưa tồn tại thì bạn chưa làm Lab 8.1 của CCDAK — quay lại làm nó trước, tuần này **xây tiếp lên nó**.

### 2) Alias CLI — chạy từ container `controller`

Ba broker đều có `KAFKA_OPTS=-javaagent:…` và `JMX_PORT=9999`, nên `docker exec kafka-1 kafka-topics.sh …` sẽ cố bind lại port đó và chết với `Address already in use`. Vì vậy **mọi CLI chạy từ `controller`** (cùng image, cùng network, không gắn agent) — đúng như CCDAK Tuần 8:

```bash
export KAFKA_CTR=controller KAFKA_BS=kafka-1:19092

alias kt='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_BS'
alias kcp='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS'
alias kcc='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BS'
alias kcg='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_BS'
alias kcfg='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-configs.sh --bootstrap-server $KAFKA_BS'
alias kq='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-metadata-quorum.sh --bootstrap-server $KAFKA_BS'

# Thêm riêng cho tuần này
alias kperf='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh'
alias kld='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-log-dirs.sh --bootstrap-server $KAFKA_BS'
alias kle='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-leader-election.sh --bootstrap-server $KAFKA_BS'
```

Hai hàm tiện dụng cho cả tuần (dán vào shell):

```bash
# Đọc nhanh 1 metric từ exporter của 1 broker: m 7071 underreplicated
m() { curl -s localhost:$1/metrics | grep -iE "$2" ; }

# Hỏi Prometheus bằng PromQL và in ra giá trị: pq 'sum(kafka_server_replicamanager_underreplicatedpartitions)'
pq() { curl -sG --data-urlencode "query=$1" localhost:9090/api/v1/query \
       | python3 -c 'import sys,json;[print(r["metric"].get("instance","(sum)"), r["value"][1]) for r in json.load(sys.stdin)["data"]["result"]]'; }
```

### 3) Thư mục làm việc

```bash
mkdir -p ~/kafka-labs/week-07 && cd ~/kafka-labs/week-07
node -e "import('kafkajs').then(() => console.log('kafkajs OK'))"   # đã cài từ CCDAK Tuần 1
```

---

## Lab 7.1 — Alert rule cho 4 metric đèn đỏ, và chứng minh nó thực sự kêu ⭐

**🎯 Mục tiêu:** Thêm **controller** vào Prometheus (không có bước này thì `OfflinePartitionsCount` và `ActiveControllerCount` **không tồn tại** trong Prometheus), viết `alerts.yml` cho 4 metric đèn đỏ + 2 alert phụ, rồi **nhìn thấy alert đi từ `inactive` → `pending` → `firing`**. Một alert chưa bao giờ được quan sát đổi trạng thái là một alert **chưa được kiểm chứng**.

**🧩 Luyện kỹ năng (liên quan đề):**

- Trong KRaft, `kafka.controller:type=KafkaController` MBean nằm trên **node controller**, không phải broker — đây là lý do dashboard "thiếu" metric mà nhiều người tưởng là lỗi exporter.
- Viết rule JMX Exporter cho MBean chưa có rule (`UncleanLeaderElectionsPerSec` thuộc `type=ControllerStats`, khác `type=KafkaController`).
- Phân biệt **PAGE** và **TICKET** bằng `for:` chứ không bằng ngưỡng.
- Trạng thái `pending` vs `firing`.

**⏱️ ~45 phút** · **Yêu cầu trước:** Chuẩn bị chung; stack CCDAK Lab 8.1 đang chạy.

### Các bước

1. Xác nhận vấn đề trước khi sửa: metric controller **chưa** có trong Prometheus.

   ```bash
   pq 'kafka_controller_kafkacontroller_activecontrollercount'     # -> không in gì
   m 7071 'activecontroller|offlinepartition'                      # -> không in gì (kafka-1 là broker, không phải controller)
   ```

2. Tạo override thêm exporter cho container `controller`. **Chỉ chứa phần thêm**, không lặp lại định nghĩa gốc.

   ```yaml
   # ~/kafka-labs/docker-compose.monitoring-controller.yml
   # Override PHỤ: gắn JMX Exporter lên node controller để lấy kafka.controller:* metrics.
   # Chạy chồng: docker compose -f docker-compose.cluster.yml \
   #                            -f docker-compose.monitoring.yml \
   #                            -f docker-compose.monitoring-controller.yml up -d
   services:
     controller:
       environment:
         KAFKA_OPTS: -javaagent:/opt/jmx/jmx_prometheus_javaagent.jar=7071:/opt/jmx/kafka-jmx.yml
       volumes:
         - ./jmx:/opt/jmx:ro
       ports:
         - "7074:7071"
   ```

   > 🧠 Hệ quả: từ giờ `docker exec controller kafka-topics.sh …` sẽ **chết** vì trùng port 7071. Alias phải thêm `JMX_PORT= KAFKA_OPTS=` vào trước lệnh. Cập nhật alias:
   >
   > ```bash
   > alias kt='docker exec -it -e KAFKA_OPTS= -e JMX_PORT= $KAFKA_CTR /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_BS'
   > alias kcg='docker exec -it -e KAFKA_OPTS= -e JMX_PORT= $KAFKA_CTR /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_BS'
   > alias kcfg='docker exec -it -e KAFKA_OPTS= -e JMX_PORT= $KAFKA_CTR /opt/kafka/bin/kafka-configs.sh --bootstrap-server $KAFKA_BS'
   > alias kq='docker exec -it -e KAFKA_OPTS= -e JMX_PORT= $KAFKA_CTR /opt/kafka/bin/kafka-metadata-quorum.sh --bootstrap-server $KAFKA_BS'
   > alias kperf='docker exec -it -e KAFKA_OPTS= -e JMX_PORT= $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh'
   > alias kld='docker exec -it -e KAFKA_OPTS= -e JMX_PORT= $KAFKA_CTR /opt/kafka/bin/kafka-log-dirs.sh --bootstrap-server $KAFKA_BS'
   > alias kle='docker exec -it -e KAFKA_OPTS= -e JMX_PORT= $KAFKA_CTR /opt/kafka/bin/kafka-leader-election.sh --bootstrap-server $KAFKA_BS'
   > alias kcp='docker exec -it -e KAFKA_OPTS= -e JMX_PORT= $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS'
   > alias kcc='docker exec -it -e KAFKA_OPTS= -e JMX_PORT= $KAFKA_CTR /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BS'
   > ```
   >
   > Đây **chính là bẫy vận hành thật** trong đề: `KAFKA_OPTS` áp cho **mọi** script trong `bin/`, không riêng broker.

3. Thêm rule cho `UncleanLeaderElectionsPerSec` — MBean này ở `type=ControllerStats`, rule cũ của Lab 8.1 chỉ khớp `type=KafkaController` nên **không bắt được nó**. Nối vào cuối `~/kafka-labs/jmx/kafka-jmx.yml`:

   ```yaml
     # 7) ControllerStats (Meter) — unclean election PHẢI luôn = 0
     - pattern: kafka.controller<type=ControllerStats, name=(UncleanLeaderElectionsPerSec|LeaderElectionRateAndTimeMs)><>Count
       name: kafka_controller_controllerstats_$1_count
       type: COUNTER
   ```

4. Viết file alert. **Đọc kỹ cột `for:`** — đây là chỗ thể hiện sự khác nhau giữa PAGE và TICKET.

   ```yaml
   # ~/kafka-labs/prometheus/alerts.yml
   groups:
   - name: kafka-red-lines            # ===== PAGE: đánh thức người lúc 3 giờ sáng =====
     rules:
     - alert: KafkaOfflinePartitions
       expr: sum(kafka_controller_kafkacontroller_offlinepartitionscount) > 0
       for: 30s                        # PRODUCTION: 1m
       labels: { severity: page }
       annotations:
         summary: "{{ $value }} partition khong co leader - mat ca doc lan ghi"
         runbook_url: "playbook#2"

     - alert: KafkaNoActiveController
       expr: sum(kafka_controller_kafkacontroller_activecontrollercount) != 1
       for: 30s                        # PRODUCTION: 2m
       labels: { severity: page }
       annotations:
         summary: "Tong ActiveControllerCount = {{ $value }} (phai bang 1)"
         runbook_url: "playbook#4"

     - alert: KafkaUnderMinIsr
       expr: sum(kafka_server_replicamanager_underminisrpartitioncount) > 0
       for: 30s                        # PRODUCTION: 2m
       labels: { severity: page }
       annotations:
         summary: "{{ $value }} partition duoi min.insync.replicas - producer acks=all DANG BI CHAN"
         runbook_url: "playbook#1"

     - alert: KafkaUncleanLeaderElection
       expr: increase(kafka_controller_controllerstats_uncleanleaderelectionspersec_count[5m]) > 0
       for: 0s                          # da mat du lieu roi - khong cho them giay nao
       labels: { severity: page }
       annotations:
         summary: "Da co unclean leader election - co kha nang mat du lieu da ack"

     - alert: KafkaMonitoringDown       # metamonitoring
       expr: up{job="kafka-broker"} == 0
       for: 1m
       labels: { severity: page }
       annotations:
         summary: "Khong scrape duoc {{ $labels.instance }} - moi alert Kafka dang IM LANG GIA"

   - name: kafka-capacity              # ===== TICKET: tao ticket, khong goi dien =====
     rules:
     - alert: KafkaUnderReplicated
       expr: sum(kafka_server_replicamanager_underreplicatedpartitions) > 0
       for: 2m                          # PRODUCTION: 10m - de rolling restart khong bao giờ cham toi
       labels: { severity: ticket }
       annotations:
         summary: "{{ $value }} partition under-replicated qua lau - giam do ben, client van chay"

     - alert: KafkaRequestHandlerSaturated
       expr: min(kafka_server_kafkarequesthandlerpool_requesthandleravgidlepercent) < 0.3
       for: 3m                          # PRODUCTION: 15m
       labels: { severity: ticket }
       annotations:
         summary: "io thread idle = {{ $value }} (<0.3) - can them num.io.threads hoac them broker"

     - alert: KafkaIsrFlapping
       expr: sum(rate(kafka_server_replicamanager_isrshrinkspersec_count[5m])) > 0
       for: 3m                          # PRODUCTION: 15m
       keep_firing_for: 2m              # chong flapping cua chinh alert
       labels: { severity: ticket }
       annotations:
         summary: "ISR dang co lien tuc - kiem GC / disk / network, DUNG noi replica.lag.time.max.ms"
   ```

   > ⚠️ **Mọi `for:` trong lab đã được rút ngắn** để bạn quan sát được trong vài phút. Con số production ghi ngay trong comment — **học con số production**, đề hỏi con số đó.

5. Nối alert file và thêm target `controller` vào Prometheus. Sửa `~/kafka-labs/prometheus/prometheus.yml` thành:

   ```yaml
   # ~/kafka-labs/prometheus/prometheus.yml
   global:
     scrape_interval: 5s
     evaluation_interval: 5s
   rule_files:
     - /etc/prometheus/alerts.yml          # <-- MỚI
   scrape_configs:
     - job_name: kafka-broker
       static_configs:
         - targets: ["kafka-1:7071", "kafka-2:7071", "kafka-3:7071"]
           labels:
             cluster: A
     - job_name: kafka-controller           # <-- MỚI
       static_configs:
         - targets: ["controller:7071"]
           labels:
             cluster: A
             role: controller
   ```

   File `alerts.yml` nằm cùng thư mục `prometheus/` đã được mount vào `/etc/prometheus/`? **Chưa** — compose gốc chỉ mount đúng 1 file. Thêm mount bằng chính override phụ:

   ```yaml
   # Nối thêm vào ~/kafka-labs/docker-compose.monitoring-controller.yml
     prometheus:
       volumes:
         - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
   ```

6. Khởi động lại stack với cả 3 file compose.

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.monitoring.yml:docker-compose.monitoring-controller.yml
   docker compose up -d
   docker compose ps
   ```

7. Kiểm chứng exporter của controller và các rule đã nạp.

   ```bash
   m 7074 'activecontroller|offlinepartition|fencedbroker'
   # kafka_controller_kafkacontroller_activecontrollercount 1.0
   # kafka_controller_kafkacontroller_offlinepartitionscount 0.0

   curl -s localhost:9090/api/v1/rules | python3 -m json.tool | grep -E '"name"|"state"'
   # 8 rule, tất cả state = "inactive"
   curl -s localhost:9090/api/v1/targets | grep -o '"health":"[a-z]*"' | sort | uniq -c   # 4 up
   ```

8. **Bắt một alert kêu thật.** Tạo một topic đòi nhiều ISR hơn số broker đang sống → `UnderMinIsrPartitionCount` > 0 ngay lập tức:

   ```bash
   kt --create --topic paranoid --partitions 3 --replication-factor 3 \
      --config min.insync.replicas=3
   docker compose stop kafka-3                 # còn 2 ISR < min.isr 3

   pq 'sum(kafka_server_replicamanager_underminisrpartitioncount)'     # > 0
   # Quan sát alert đổi trạng thái (chạy 3 lần, cách nhau ~20 s)
   curl -s localhost:9090/api/v1/rules | python3 -c '
   import sys, json
   for g in json.load(sys.stdin)["data"]["groups"]:
       for r in g["rules"]:
           if r.get("state"):
               print("%-32s %s" % (r["name"], r["state"]))'
   ```

   Bạn phải thấy `KafkaUnderMinIsr` đi **`inactive` → `pending` → `firing`** (sau ~30 s), trong khi `KafkaUnderReplicated` vẫn còn `pending` (vì `for: 2m`). **Đó chính là ranh giới PAGE / TICKET, nhìn thấy bằng mắt.**

9. Khôi phục và xem alert tự tắt.

   ```bash
   docker compose start kafka-3
   # chờ ~30 s rồi kiểm lại -> cả hai về inactive
   ```

### ✅ Kiểm chứng

- Bước 1 **không in gì** và bước 7 in ra `activecontrollercount 1.0` — đó là bằng chứng metric controller chỉ có trên node controller.
- `curl :9090/api/v1/rules` liệt kê đủ **8** alert.
- Ở bước 8, `KafkaUnderMinIsr` đạt `firing` trong khi `KafkaUnderReplicated` mới chỉ `pending` — hai `for:` khác nhau cho hai hành vi khác nhau.
- Nếu `KafkaNoActiveController` firing ngay từ đầu → bạn chưa thêm target `controller`, `sum()` trên tập rỗng cho kết quả không có series và biểu thức `!= 1` không khớp gì; kiểm lại bước 5.

### 🧹 Dọn dẹp

```bash
kt --delete --topic paranoid
docker compose start kafka-3 2>/dev/null
# GIỮ alerts.yml, prometheus.yml và docker-compose.monitoring-controller.yml — Lab 7.2/7.3/7.7 dùng lại
```

### 🧠 Ý nghĩa với đề thi

- Câu "alert nào bắt buộc phải có" → **`OfflinePartitionsCount` > 0, tổng `ActiveControllerCount` ≠ 1, `UncleanLeaderElectionsPerSec` ≠ 0** (Confluent nêu thẳng 3 cái này là tối thiểu).
- Câu "alert URP kêu mỗi lần deploy, sửa thế nào" → thêm **`for:`**, **không** nâng ngưỡng.
- Câu "`ActiveControllerCount` = 0 trên mọi broker" → bình thường nếu controller tách riêng; chỉ **tổng cụm** mới có ý nghĩa.

---

## Lab 7.2 — Gây URP, đo thời gian hồi phục, rồi rút ngắn nó ⭐

**🎯 Mục tiêu:** Tắt một broker khi đang có dữ liệu chạy, xem alert URP kêu, **đo bằng giây** thời gian `UnderReplicatedPartitions` trở về 0 sau khi bật lại, rồi tăng `num.replica.fetchers` và đo lại để thấy con số thay đổi thật.

**🧩 Luyện kỹ năng (liên quan đề):**

- URP > 0 với `OfflinePartitionsCount` = 0 → **client không bị ảnh hưởng**, chỉ giảm độ bền.
- `num.replica.fetchers` mặc định **1** và là config **dynamic cluster-wide** — đổi được lúc chạy, không cần restart.
- Rolling restart phải **chờ URP về 0** giữa hai broker (`controlled.shutdown` chỉ thành công khi mọi partition còn ≥1 replica sống).

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 7.1.

### Các bước

1. Tạo topic đủ lớn để catch-up mất thời gian đo được, rồi bơm dữ liệu.

   ```bash
   kt --create --topic urp-demo --partitions 12 --replication-factor 3
   kperf --topic urp-demo --num-records 1500000 --record-size 512 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all linger.ms=5
   # ~750 MB, chạy 1-2 phút
   ```

2. Ghi lại baseline rồi **gây hỏng**: tắt `kafka-3`.

   ```bash
   pq 'sum(kafka_server_replicamanager_underreplicatedpartitions)'    # 0
   docker compose stop kafka-3
   sleep 40
   pq 'sum(kafka_server_replicamanager_underreplicatedpartitions)'    # > 0
   pq 'sum(kafka_controller_kafkacontroller_offlinepartitionscount)'  # 0  <- QUAN TRỌNG
   ```

3. **Chứng minh client không bị ảnh hưởng** — đây là trọng tâm của lab, không phải con số URP.

   ```bash
   kperf --topic urp-demo --num-records 50000 --record-size 512 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all
   # Chạy BÌNH THƯỜNG. RF=3, mất 1 broker -> ISR còn 2 = min.insync.replicas -> vẫn ghi được
   kt --describe --topic urp-demo --under-replicated-partitions | head -5
   ```

4. Bơm thêm dữ liệu **trong lúc broker đang chết** để follower phải đuổi một khoảng lớn.

   ```bash
   kperf --topic urp-demo --num-records 800000 --record-size 512 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all
   ```

5. **Đo lần 1** — bật lại broker và đếm giây tới khi URP về 0.

   ```bash
   cat > ~/kafka-labs/week-07/measure-urp.sh <<'EOS'
   #!/usr/bin/env bash
   # Đo số giây từ lúc gọi tới khi URP toàn cụm trở về 0
   start=$(date +%s)
   while true; do
     v=$(curl -sG --data-urlencode \
         'query=sum(kafka_server_replicamanager_underreplicatedpartitions)' \
         localhost:9090/api/v1/query \
         | python3 -c 'import sys,json;r=json.load(sys.stdin)["data"]["result"];print(r[0]["value"][1] if r else "NA")')
     now=$(date +%s)
     echo "t+$((now-start))s  URP=$v"
     [ "$v" = "0" ] && { echo ">>> URP ve 0 sau $((now-start)) giay"; break; }
     [ $((now-start)) -gt 300 ] && { echo ">>> qua 300s, dung do"; break; }
     sleep 2
   done
   EOS
   chmod +x ~/kafka-labs/week-07/measure-urp.sh

   docker compose start kafka-3 && ~/kafka-labs/week-07/measure-urp.sh
   ```

   Ghi lại con số. Ví dụ: `>>> URP ve 0 sau 46 giay`.

6. **Tăng `num.replica.fetchers`** ở mức cluster-default (dynamic, không restart) và xác nhận nó đã có hiệu lực.

   ```bash
   kcfg --alter --entity-type brokers --entity-default --add-config num.replica.fetchers=4
   kcfg --describe --entity-type brokers --entity-default
   # Sensitive config ... num.replica.fetchers=4
   ```

7. **Đo lần 2** — lặp lại đúng kịch bản.

   ```bash
   docker compose stop kafka-3
   kperf --topic urp-demo --num-records 800000 --record-size 512 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all
   docker compose start kafka-3 && ~/kafka-labs/week-07/measure-urp.sh
   ```

8. Đối chiếu hai con số, và xem alert đã kêu rồi tự tắt trong Prometheus UI (http://localhost:9090/alerts).

### ✅ Kiểm chứng

- Bước 2: `UnderReplicatedPartitions` > 0 **trong khi** `OfflinePartitionsCount` = **0**. Nếu OfflinePartitions cũng > 0 thì bạn đang tắt nhầm broker của một topic RF=1 còn sót từ lab khác.
- Bước 3: produce với `acks=all` **thành công** dù URP > 0 — đây là điểm phải tự tay thấy một lần.
- Bước 5 và 7 cho **hai con số khác nhau**, lần 2 nhỏ hơn. Nếu bằng nhau thì lượng dữ liệu quá nhỏ: tăng `--num-records` lên 2–3 lần rồi đo lại.
- `KafkaUnderReplicated` trong Prometheus có `for: 2m` nên chỉ **firing** nếu bước 4 kéo dài hơn 2 phút — nếu nó chỉ dừng ở `pending`, đó cũng là kết quả **đúng** và là bài học: `for:` quyết định alert có kêu hay không.

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type brokers --entity-default --delete-config num.replica.fetchers
kt --delete --topic urp-demo
docker compose start kafka-3 2>/dev/null
```

### 🧠 Ý nghĩa với đề thi

- "URP = 140, Offline = 0 → client bị gì?" → **không bị gì**, chỉ giảm độ bền.
- "URP không về 0 sau 30 phút, mọi broker đều sống" → tăng **`num.replica.fetchers`** (mặc định **1**), **không** nới `replica.lag.time.max.ms`.
- "Rolling restart an toàn" → tắt mềm → chờ **URP về 0** → broker kế tiếp → active controller **sau cùng**.

---

## Lab 7.3 — Gây OfflinePartition thật, và thấy vì sao RF=1 không có đường cứu ⭐

**🎯 Mục tiêu:** Tạo một topic `replication.factor=1`, tắt đúng broker đang giữ partition đó, quan sát `OfflinePartitionsCount` > 0 và **so sánh trực tiếp** với một topic RF=3 trên cùng broker đó — để thấy rõ khác biệt giữa "mất độ bền" và "mất dịch vụ".

**🧩 Luyện kỹ năng (liên quan đề):**

- `OfflinePartitionsCount` > 0 = **không đọc được và không ghi được**.
- `kafka-topics.sh --describe --unavailable-partitions` là lệnh chẩn đoán chính xác.
- RF=1 **không có** đường khôi phục: unclean election, ELR, reassignment đều vô nghĩa khi không còn bản sao nào.

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 7.1.

### Các bước

1. Tạo **cặp đối chứng**: một topic RF=1 và một topic RF=3, rồi nạp dữ liệu vào cả hai.

   ```bash
   kt --create --topic fragile --partitions 3 --replication-factor 1
   kt --create --topic sturdy  --partitions 3 --replication-factor 3
   for t in fragile sturdy; do
     kperf --topic $t --num-records 20000 --record-size 256 --throughput -1 \
           --producer-props bootstrap.servers=$KAFKA_BS acks=all
   done
   ```

2. Tìm broker nào đang giữ partition 0 của `fragile`.

   ```bash
   kt --describe --topic fragile
   # Topic: fragile  Partition: 0  Leader: 3  Replicas: 3  Isr: 3   <- ghi lại Leader
   ```

   Ánh xạ `node.id` → container: **2 = kafka-1 · 3 = kafka-2 · 4 = kafka-3**.

3. **Gây hỏng:** tắt đúng container đó (ví dụ Leader = 3 → `kafka-2`).

   ```bash
   docker compose stop kafka-2
   sleep 30
   ```

4. Chẩn đoán đúng thứ tự playbook — **metric trước, rồi mới tới lệnh chi tiết**.

   ```bash
   # ① METRIC
   pq 'sum(kafka_controller_kafkacontroller_offlinepartitionscount)'      # > 0
   pq 'sum(kafka_server_replicamanager_underreplicatedpartitions)'        # > 0 (do sturdy)

   # ② Lệnh khoanh vùng
   kt --describe --topic fragile --unavailable-partitions
   # Topic: fragile  Partition: 0  Leader: none  Replicas: 3  Isr:
   kt --describe --topic sturdy --under-replicated-partitions
   # sturdy chỉ under-replicated, VẪN CÓ leader
   ```

5. **So sánh hành vi client** — đây là phần đắt giá nhất của lab.

   ```bash
   # sturdy: vẫn ghi được bình thường
   kperf --topic sturdy --num-records 5000 --record-size 256 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all

   # fragile: partition offline -> treo rồi lỗi
   kperf --topic fragile --num-records 5000 --record-size 256 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all max.block.ms=15000
   # org.apache.kafka.common.errors.TimeoutException: Topic fragile not present in metadata...
   # hoặc: Expiring N record(s) for fragile-0 ... / LEADER_NOT_AVAILABLE

   # Đọc cũng chết
   kcc --topic fragile --partition 0 --from-beginning --max-messages 1 --timeout-ms 10000
   ```

6. Thử **mọi cách "cứu"** để tự chứng minh chúng không hoạt động:

   ```bash
   kle --election-type unclean --topic fragile --partition 0
   # Không có replica nào ngoài ISR để bầu -> lệnh không cứu được gì
   ```

7. **Khôi phục** — cách duy nhất thật sự có tác dụng:

   ```bash
   docker compose start kafka-2
   sleep 30
   pq 'sum(kafka_controller_kafkacontroller_offlinepartitionscount)'   # 0
   kt --describe --topic fragile
   ```

### ✅ Kiểm chứng

- Bước 4: `OfflinePartitionsCount` > 0 **và** `--unavailable-partitions` in đúng `Leader: none`, `Isr:` rỗng.
- Bước 5: `sturdy` ghi thành công, `fragile` timeout. Hai kết quả khác nhau trên **cùng một sự cố broker** — đó là toàn bộ bài học.
- Bước 6: lệnh unclean election không khôi phục được partition. Nếu nó "thành công" thì bạn đang chạy trên topic RF>1, kiểm lại bước 1.
- Bước 7: alert `KafkaOfflinePartitions` trong Prometheus chuyển về `inactive`.

### 🧹 Dọn dẹp

```bash
kt --delete --topic fragile
kt --delete --topic sturdy
docker compose start kafka-2 2>/dev/null
```

### 🧠 Ý nghĩa với đề thi

- "RF=1, broker giữ partition chết vĩnh viễn — làm gì?" → **không có đường khôi phục nào**; chờ phần cứng hoặc tạo lại topic và chấp nhận mất dữ liệu.
- "`OfflinePartitionsCount` > 0 → hành động đầu tiên?" → **bật lại broker giữ replica**. Unclean election là bậc cuối, và chỉ có tác dụng khi **còn** replica ngoài ISR.
- Nhớ mặc định nguy hiểm: **`default.replication.factor` = 1**. Production phải override.

---

## Lab 7.4 — Ba kiểu lag, phân biệt bằng đúng cây quyết định ⭐

**🎯 Mục tiêu:** Tự tay dựng **cả ba** nguyên nhân lag (key skew · thiếu consumer · rebalance lặp) rồi phân biệt chúng **chỉ bằng dữ liệu quan sát được**, không dựa vào việc bạn biết trước mình vừa làm gì.

**🧩 Luyện kỹ năng (liên quan đề):**

- `kcg --describe --members --verbose` là lệnh phân biệt skew với thiếu consumer.
- Thêm consumer **không** giúp khi nguyên nhân là skew hoặc khi số consumer đã bằng số partition.
- Rebalance lặp có chữ ký riêng: lag **răng cưa** + log `group is rebalancing`.

**⏱️ ~50 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic và bộ sinh dữ liệu điều khiển được độ lệch khoá.

   ```bash
   kt --create --topic lag-lab --partitions 6 --replication-factor 3
   ```

   ```javascript
   // ~/kafka-labs/week-07/producer.mjs
   // node producer.mjs skew   -> 95% record dung 1 key duy nhat (gay hot partition)
   // node producer.mjs even   -> key ngau nhien, trai deu
   import { Kafka, logLevel } from "kafkajs";

   const mode = process.argv[2] ?? "even";
   const kafka = new Kafka({
     clientId: "w7-prod",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.NOTHING,
   });
   const producer = kafka.producer();
   await producer.connect();

   let sent = 0;
   const total = 300_000;
   while (sent < total) {
     const batch = Array.from({ length: 1000 }, (_, i) => {
       const key = mode === "skew" && Math.random() < 0.95
         ? "HOT-CUSTOMER"
         : `cust-${Math.floor(Math.random() * 10_000)}`;
       return { key, value: JSON.stringify({ n: sent + i, ts: Date.now() }) };
     });
     await producer.send({ topic: "lag-lab", messages: batch });
     sent += 1000;
     if (sent % 50_000 === 0) console.log(`đã gửi ${sent}`);
   }
   await producer.disconnect();
   console.log(`xong: ${total} record, mode=${mode}`);
   ```

2. Consumer có tốc độ xử lý điều chỉnh được, và tuỳ chọn ép rebalance lặp.

   ```javascript
   // ~/kafka-labs/week-07/consumer.mjs
   // node consumer.mjs <id> <msPerRecord> [slowloop]
   //   slowloop -> dat rebalanceTimeout ngan + xu ly 1 batch rat lau => bi kick lien tuc
   import { Kafka, logLevel } from "kafkajs";

   const [, , id = "c1", msPerRecord = "0", mode = ""] = process.argv;
   const slow = mode === "slowloop";

   const kafka = new Kafka({
     clientId: `w7-${id}`,
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.WARN,          // de nhin thay canh bao rebalance
   });
   const consumer = kafka.consumer({
     groupId: "lag-group",
     sessionTimeout: slow ? 10_000 : 45_000,
     rebalanceTimeout: slow ? 12_000 : 60_000,
   });

   await consumer.connect();
   await consumer.subscribe({ topic: "lag-lab", fromBeginning: true });

   let n = 0;
   await consumer.run({
     eachBatchAutoResolve: true,
     eachBatch: async ({ batch, resolveOffset, heartbeat }) => {
       for (const msg of batch.messages) {
         if (Number(msPerRecord) > 0) {
           await new Promise((r) => setTimeout(r, Number(msPerRecord)));
         }
         resolveOffset(msg.offset);
         if (++n % 2000 === 0) console.log(`[${id}] p${batch.partition} đã xử lý ${n}`);
         if (!slow) await heartbeat();      // slowloop: CO TINH khong heartbeat
       }
     },
   });
   ```

3. **Tình huống A — KEY SKEW.** Sinh dữ liệu lệch, chạy đúng 6 consumer (bằng số partition).

   ```bash
   cd ~/kafka-labs/week-07
   node producer.mjs skew
   for i in 1 2 3 4 5 6; do node consumer.mjs c$i 1 & done
   sleep 45
   kcg --describe --group lag-group
   ```

   Đọc output: LAG lớn ở **đúng một** partition, các partition khác ≈ 0, và **mỗi consumer giữ 1 partition** (không ai idle).

   ```bash
   kcg --describe --group lag-group --members --verbose
   kill %1 %2 %3 %4 %5 %6 2>/dev/null; wait 2>/dev/null
   kcg --delete --group lag-group
   ```

4. **Tình huống B — THIẾU CONSUMER.** Dữ liệu trải đều, chỉ 1 consumer xử lý chậm.

   ```bash
   node producer.mjs even
   node consumer.mjs solo 2 &
   sleep 45
   kcg --describe --group lag-group
   kcg --describe --group lag-group --members --verbose
   ```

   Đọc output: LAG lớn ở **mọi** partition, và **một** member giữ cả **6** partition.

   ```bash
   # Áp dụng hành động RẺ, ĐẢO NGƯỢC ĐƯỢC: thêm consumer
   for i in 2 3 4 5 6; do node consumer.mjs c$i 2 & done
   sleep 60
   kcg --describe --group lag-group     # LAG phải giảm rõ rệt
   kill $(jobs -p) 2>/dev/null; wait 2>/dev/null
   kcg --delete --group lag-group
   ```

5. **Tình huống C — REBALANCE LẶP.** Consumer vi phạm hạn xử lý một vòng.

   ```bash
   node producer.mjs even
   node consumer.mjs loop1 60 slowloop &     # 60ms/record x batch lon >> rebalanceTimeout 12s
   node consumer.mjs loop2 60 slowloop &
   sleep 90
   kcg --describe --group lag-group --state
   # STATE luân phiên PreparingRebalance / CompletingRebalance / Stable
   ```

   Xem log của consumer: lặp lại `The group is rebalancing, so a rejoin is needed` / `Consumer group is rebalancing`.

   ```bash
   kill $(jobs -p) 2>/dev/null; wait 2>/dev/null
   kcg --delete --group lag-group
   ```

6. **Tự kiểm tra:** che lại phần bạn vừa làm và điền bảng này chỉ từ output đã lưu.

   | Dấu hiệu quan sát được | Tình huống | Hành động đúng |
   |---|---|---|
   | LAG chỉ ở 1 partition, 6/6 consumer đều có partition | ______ | ______ |
   | LAG ở mọi partition, 1 member giữ 6 partition | ______ | ______ |
   | STATE nhảy liên tục, LAG lên xuống răng cưa | ______ | ______ |

   *(Đáp án: A skew → sửa key/partitioner · B thiếu consumer → thêm instance · C rebalance lặp → giảm `max.poll.records` / tăng `max.poll.interval.ms` / static membership.)*

### ✅ Kiểm chứng

- Tình huống A: `--members --verbose` cho thấy **6 member, mỗi member 1 partition, không ai idle** — chứng minh thêm consumer là vô ích.
- Tình huống B: **1 member giữ 6 partition**; sau khi thêm 5 consumer, LAG giảm rõ trong 60 giây.
- Tình huống C: `--state` **không ổn định ở `Stable`**; đây là chữ ký duy nhất phân biệt C với B.
- Nếu tình huống A cho LAG trải đều: `producer.mjs skew` chưa chạy, hoặc bạn đã xoá group giữa chừng.

### 🧹 Dọn dẹp

```bash
kill $(jobs -p) 2>/dev/null; wait 2>/dev/null
kcg --delete --group lag-group 2>/dev/null
kt --delete --topic lag-lab
```

### 🧠 Ý nghĩa với đề thi

- Đề luôn hỏi *"thêm consumer có giúp không?"*. Câu trả lời phụ thuộc **đúng một** thứ: assignment đang thế nào — và `--members --verbose` là lệnh trả lời.
- Rebalance lặp: thủ phạm là **`max.poll.interval.ms`** (300000 ms), **không** phải `session.timeout.ms`, vì heartbeat vẫn đều.
- Tăng partition là hành động **một chiều**; nó nằm dưới cùng trong thang ưu tiên.

---

## Lab 7.5 — `advertised.listeners` sai: bootstrap OK nhưng produce timeout

**🎯 Mục tiêu:** Tái hiện chính xác triệu chứng "liệt kê topic được nhưng gửi thì timeout", rồi tìm ra nguyên nhân **bằng log** thay vì bằng phỏng đoán.

**🧩 Luyện kỹ năng (liên quan đề):**

- Client dùng bootstrap **chỉ để lấy metadata**, rồi kết nối **thẳng tới leader** bằng địa chỉ broker **tự khai**.
- `advertised.listeners` là config **dynamic per-broker** — đổi được lúc chạy, nên cũng **phá** được lúc chạy.
- Phân biệt lỗi "không tới được leader" với lỗi ISR hoặc lỗi ACL.

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic và xác nhận mọi thứ đang tốt **từ host** (không qua container).

   ```bash
   kt --create --topic listener-demo --partitions 6 --replication-factor 3
   docker exec -e KAFKA_OPTS= -e JMX_PORT= controller /opt/kafka/bin/kafka-topics.sh \
     --bootstrap-server localhost:9092 --list 2>/dev/null || true

   # Chạy từ HOST bằng kafkajs để mô phỏng client bên ngoài
   cat > ~/kafka-labs/week-07/probe.mjs <<'EOS'
   import { Kafka, logLevel } from "kafkajs";
   const kafka = new Kafka({ clientId: "w7-probe", brokers: ["localhost:9092"], logLevel: logLevel.NOTHING });
   const admin = kafka.admin();
   await admin.connect();
   console.log("BOOTSTRAP OK — topics:", (await admin.listTopics()).filter(t => !t.startsWith("__")));
   await admin.disconnect();

   const producer = kafka.producer();
   await producer.connect();
   try {
     const res = await producer.send({
       topic: "listener-demo",
       messages: Array.from({ length: 12 }, (_, i) => ({ key: `k${i}`, value: `v${i}` })),
       timeout: 15000,
     });
     console.log("PRODUCE OK —", res.map(r => `p${r.partition}`).join(" "));
   } catch (e) {
     console.log("PRODUCE FAILED —", e.constructor.name, ":", e.message);
   }
   await producer.disconnect();
   EOS
   cd ~/kafka-labs/week-07 && node probe.mjs
   # BOOTSTRAP OK — topics: [ 'listener-demo' ]
   # PRODUCE OK — p0 p1 p2 p3 p4 p5
   ```

2. **Gây hỏng:** đổi `advertised.listeners` của `kafka-2` (node.id **3**) sang một cổng host không có ai nghe.

   ```bash
   kcfg --alter --entity-type brokers --entity-name 3 \
        --add-config 'advertised.listeners=PLAINTEXT://kafka-2:19092,PLAINTEXT_HOST://localhost:19999'
   kcfg --describe --entity-type brokers --entity-name 3
   sleep 10
   ```

3. Quan sát triệu chứng **từ host**.

   ```bash
   cd ~/kafka-labs/week-07 && node probe.mjs
   # BOOTSTRAP OK — topics: [ 'listener-demo' ]        <- vẫn liệt kê được!
   # PRODUCE FAILED — KafkaJSNumberOfRetriesExceeded : Connection error: connect ECONNREFUSED 127.0.0.1:19999
   #   (hoặc timeout, tuỳ partition nào do kafka-2 làm leader)
   ```

   ⚠️ **Đây là toàn bộ bài học:** bootstrap đi tới `localhost:9092` (kafka-1) và trả về **metadata**; trong metadata đó, kafka-2 tự khai là `localhost:19999`. Client tin và kết nối tới đó.

4. Chẩn đoán theo playbook — **không đoán, đọc**.

   ```bash
   # ① Broker có khoẻ không? Loại trừ tầng 1 trước
   pq 'sum(kafka_controller_kafkacontroller_offlinepartitionscount)'      # 0
   pq 'sum(kafka_server_replicamanager_underminisrpartitioncount)'        # 0
   #    -> cluster HOÀN TOÀN khoẻ => lỗi nằm ở đường client tới broker

   # ② Broker có nhận được produce request nào không?
   docker compose logs --since 3m kafka-2 | grep -iE "produce|error" | tail -20
   #    -> KHÔNG có produce request nào tới. Lỗi xảy ra TRƯỚC broker.

   # ③ Broker đang tự khai địa chỉ nào?
   kcfg --describe --entity-type brokers --entity-name 3 --all | grep -i advertised
   #    advertised.listeners=PLAINTEXT://kafka-2:19092,PLAINTEXT_HOST://localhost:19999
   #                                                                            ^^^^^ thủ phạm
   ```

5. **Sửa:** xoá config động để broker quay về giá trị tĩnh trong compose.

   ```bash
   kcfg --alter --entity-type brokers --entity-name 3 --delete-config advertised.listeners
   sleep 10
   cd ~/kafka-labs/week-07 && node probe.mjs      # PRODUCE OK trở lại
   ```

### ✅ Kiểm chứng

- Bước 3 in **`BOOTSTRAP OK`** và **`PRODUCE FAILED`** trong cùng một lần chạy — nếu cả hai đều fail thì bạn đã phá nhầm `kafka-1` (broker bootstrap).
- Bước 4 ② **không** thấy produce request nào trong log `kafka-2`: bằng chứng lỗi nằm ở phía client, không phải trong broker.
- Bước 5 khôi phục mà **không cần restart container** — chứng minh `advertised.listeners` là dynamic per-broker.

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type brokers --entity-name 3 --delete-config advertised.listeners 2>/dev/null
kt --delete --topic listener-demo
```

### 🧠 Ý nghĩa với đề thi

- Chữ ký cần thuộc: **"bootstrap/`--list` OK nhưng produce timeout" → `advertised.listeners`**. Không phải `request.timeout.ms`, không phải ACL, không phải ISR.
- Cluster metric hoàn toàn sạch mà client vẫn đau → nguyên nhân ở **tầng 3 hoặc đường mạng**, không ở broker.
- Trong Docker/Kubernetes, lỗi này xuất hiện khi broker advertise hostname **nội bộ** cho client **bên ngoài**.

---

## Lab 7.6 — Đọc log có phương pháp: đổi level lúc chạy và bám theo leader election

**🎯 Mục tiêu:** Tìm đúng file log trong container, nâng level **lúc chạy** bằng `--entity-type broker-loggers`, rồi bám theo `state-change.log` trong lúc leader thực sự đổi.

**🧩 Luyện kỹ năng (liên quan đề):**

- 4 file log và câu hỏi mỗi file trả lời.
- `kafka-configs.sh --entity-type broker-loggers --entity-name <node.id>` — không restart, **không bền qua restart**.
- `log.dirs` (dữ liệu partition) ≠ thư mục log ứng dụng.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tìm thư mục log ứng dụng **và** thư mục dữ liệu — hai thứ khác nhau.

   ```bash
   docker exec kafka-1 ls -la /opt/kafka/logs          # server.log, controller.log, state-change.log...
   docker exec kafka-1 ls -la /tmp/kraft-combined-logs # đây là log.dirs: dữ liệu partition
   docker exec controller ls -la /tmp/kraft-combined-logs/__cluster_metadata-0 | head
   ```

   > 🧠 Nếu `/opt/kafka/logs` trống hoặc thiếu file: image đang ghi log ra stdout. Khi đó dùng `docker compose logs <service>` cho `server.log`, và bước 4 vẫn hoạt động vì `state-change` cũng đi ra stdout với cùng nội dung.

2. Liệt kê logger hiện tại của broker `kafka-1` (**node.id = 2**).

   ```bash
   kcfg --describe --entity-type broker-loggers --entity-name 2 | tr ',' '\n' | head -25
   # kafka=INFO, kafka.controller=TRACE, state.change.logger=TRACE, kafka.request.logger=WARN, ...
   ```

3. Bật request logger ở DEBUG **trong thời gian ngắn** rồi xem lượng log nó sinh ra.

   ```bash
   kcfg --alter --entity-type broker-loggers --entity-name 2 \
        --add-config kafka.request.logger=DEBUG

   kt --create --topic log-demo --partitions 6 --replication-factor 3
   kperf --topic log-demo --num-records 5000 --record-size 256 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all

   docker compose logs --since 1m kafka-1 | grep -c "Completed request"
   # hàng nghìn dòng chỉ trong vài giây -> đây là lý do CHỈ bật vài chục giây
   ```

   **Tắt ngay:**

   ```bash
   kcfg --alter --entity-type broker-loggers --entity-name 2 --delete-config kafka.request.logger
   ```

4. Bám theo `state-change` trong lúc **leader thật sự đổi**. Mở 2 terminal.

   *Terminal 1 — theo dõi:*

   ```bash
   docker compose logs -f --since 10s kafka-1 | grep -iE "state change|leader|isr|became"
   ```

   *Terminal 2 — gây đổi leader:*

   ```bash
   kt --describe --topic log-demo | head       # ghi lại Leader hiện tại của từng partition
   docker compose stop kafka-3                 # buộc controller bầu leader mới
   sleep 20
   kt --describe --topic log-demo | head       # Leader đã đổi
   docker compose start kafka-3
   sleep 25
   kle --election-type preferred --all-topic-partitions   # trả leader về preferred replica
   kt --describe --topic log-demo | head       # Leader trở lại như ban đầu
   ```

5. Đọc `controller.log` để thấy góc nhìn của controller về cùng sự kiện.

   ```bash
   docker compose logs --since 5m controller | grep -iE "fenc|unfenc|regist|election|heartbeat" | tail -20
   ```

6. Xác nhận tính **không bền** của thay đổi logger.

   ```bash
   kcfg --alter --entity-type broker-loggers --entity-name 2 --add-config kafka.request.logger=DEBUG
   docker compose restart kafka-1 && sleep 25
   kcfg --describe --entity-type broker-loggers --entity-name 2 | tr ',' '\n' | grep request.logger
   # -> đã quay về mức trong log4j2.yaml, KHÔNG còn DEBUG
   ```

### ✅ Kiểm chứng

- Bước 1 phân biệt rõ hai thư mục: log ứng dụng vs `log.dirs`.
- Bước 3: số dòng `Completed request` là **hàng nghìn** trong ~10 giây produce.
- Bước 4: Terminal 1 in các dòng leader/ISR **đúng vào thời điểm** Terminal 2 tắt broker, và `kt --describe` xác nhận Leader đã đổi rồi quay về sau preferred election.
- Bước 6: sau restart, `kafka.request.logger` **không còn** DEBUG.

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type broker-loggers --entity-name 2 --delete-config kafka.request.logger 2>/dev/null
kt --delete --topic log-demo
docker compose start kafka-3 2>/dev/null
```

### 🧠 Ý nghĩa với đề thi

- "Bật DEBUG cho request logger trên broker 2 mà không restart" → `--entity-type broker-loggers --entity-name 2`. Không phải `--entity-type brokers`, và **chắc chắn** không phải `zookeeper-shell.sh`.
- "Truy vết leader đổi lúc nào" → **`state-change.log`**; "controller quyết định gì" → **`controller.log`**.
- "Đổi nơi ghi `server.log`" → **không** phải `log.dirs`.

---

## Lab 7.7 — Bài tập tổng hợp: cluster bị phá ngẫu nhiên, bạn chẩn đoán

**🎯 Mục tiêu:** Chạy một script phá cluster theo **1 trong 4 cách** mà bạn không biết trước, rồi chẩn đoán bằng đúng quy trình **metric → log → config → hành động** và ghi lại **thứ tự** lệnh đã dùng. Đây là bản thu nhỏ của capstone Tuần 8.

**🧩 Luyện kỹ năng (liên quan đề):** toàn bộ playbook của tuần, dưới áp lực không biết trước câu trả lời.

**⏱️ ~45 phút** · **Yêu cầu trước:** Lab 7.1 → 7.6 (cần alert stack và các kỹ năng đọc log).

### Các bước

1. Chuẩn bị nền: một topic "production" khoẻ mạnh đang chạy.

   ```bash
   kt --create --topic prod-orders --partitions 6 --replication-factor 3
   kperf --topic prod-orders --num-records 100000 --record-size 256 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all
   ```

2. Tạo script phá. **Đọc script một lần cho hiểu cơ chế, rồi đừng mở lại file đáp án cho tới khi chẩn đoán xong.**

   ```bash
   cat > ~/kafka-labs/week-07/break-me.sh <<'EOS'
   #!/usr/bin/env bash
   # Pha cluster theo 1 trong 4 cach, ghi lua chon vao file AN.
   set -e
   cd ~/kafka-labs
   K="docker exec -e KAFKA_OPTS= -e JMX_PORT= controller /opt/kafka/bin"
   BS="kafka-1:19092"
   CHOICE=$((RANDOM % 4 + 1))

   case $CHOICE in
     1) # Offline partition: topic RF=1 roi tat broker giu no
        $K/kafka-topics.sh --bootstrap-server $BS --create --topic canary \
           --partitions 1 --replication-factor 1 >/dev/null
        LEADER=$($K/kafka-topics.sh --bootstrap-server $BS --describe --topic canary \
                 | grep -o 'Leader: [0-9]*' | awk '{print $2}')
        case $LEADER in 2) C=kafka-1;; 3) C=kafka-2;; 4) C=kafka-3;; esac
        docker compose stop $C >/dev/null
        echo "1|offline-partition|broker $C (node $LEADER) da bi tat, topic canary RF=1" ;;

     2) # advertised.listeners sai tren kafka-2 (node 3)
        $K/kafka-configs.sh --bootstrap-server $BS --alter --entity-type brokers --entity-name 3 \
           --add-config 'advertised.listeners=PLAINTEXT://kafka-2:19092,PLAINTEXT_HOST://localhost:19999' >/dev/null
        echo "2|bad-advertised-listeners|node 3 (kafka-2) advertise localhost:19999" ;;

     3) # Quota that chat cho client-id 'w7-probe'
        $K/kafka-configs.sh --bootstrap-server $BS --alter --entity-type clients --entity-name w7-probe \
           --add-config 'producer_byte_rate=8192' >/dev/null
        echo "3|producer-quota|client-id w7-probe bi gioi han 8192 B/s" ;;

     4) # min.insync.replicas = 4 tren topic prod-orders (> so broker)
        $K/kafka-configs.sh --bootstrap-server $BS --alter --entity-type topics --entity-name prod-orders \
           --add-config 'min.insync.replicas=4' >/dev/null
        echo "4|min-isr-too-high|prod-orders co min.insync.replicas=4 nhung chi co 3 broker" ;;
   esac > ~/kafka-labs/week-07/.what-broke

   echo "Da pha xong. Dung mo file .what-broke. Bat dau chan doan."
   EOS
   chmod +x ~/kafka-labs/week-07/break-me.sh
   ```

3. **Phá:**

   ```bash
   ~/kafka-labs/week-07/break-me.sh
   ```

4. **Chẩn đoán.** Ghi từng lệnh bạn chạy vào một file, theo đúng thứ tự — cuối lab bạn sẽ chấm chính cái thứ tự đó.

   ```bash
   # ① METRIC — tầng 1 trước, LUÔN LUÔN
   pq 'sum(kafka_controller_kafkacontroller_offlinepartitionscount)'
   pq 'sum(kafka_controller_kafkacontroller_activecontrollercount)'
   pq 'sum(kafka_server_replicamanager_underminisrpartitioncount)'
   pq 'sum(kafka_server_replicamanager_underreplicatedpartitions)'
   curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'

   # ② Nếu tầng 1 sạch: thử từ góc nhìn client
   cd ~/kafka-labs/week-07 && node probe.mjs          # dùng lại từ Lab 7.5
   kperf --topic prod-orders --num-records 2000 --record-size 256 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all

   # ③ LOG
   docker compose logs --since 5m kafka-1 kafka-2 kafka-3 controller | grep -iE "error|warn" | tail -30

   # ④ CONFIG — đọc cả 3 mức
   kcfg --describe --entity-type topics --entity-name prod-orders
   kcfg --describe --entity-type brokers --entity-name 3
   kcfg --describe --entity-type clients
   docker compose ps
   ```

5. **Đối chiếu với bảng chẩn đoán này** trước khi mở đáp án:

   | Bạn quan sát thấy | Kết luận | Hành động sửa |
   |---|---|---|
   | `OfflinePartitionsCount` > 0, `docker compose ps` thiếu 1 broker | **① offline partition** | `docker compose start <broker>` |
   | Tầng 1 sạch; `node probe.mjs` in `BOOTSTRAP OK` + `PRODUCE FAILED`; không có produce request trong log broker | **② `advertised.listeners`** | `kcfg --entity-type brokers --entity-name 3 --delete-config advertised.listeners` |
   | Tầng 1 sạch; không lỗi gì; throughput đụng trần cố định; `kafka-configs --entity-type clients` có `producer_byte_rate` | **③ quota** | `kcfg --entity-type clients --entity-name w7-probe --delete-config producer_byte_rate` |
   | `UnderMinIsrPartitionCount` > 0 với **mọi broker đều sống**; producer báo `NotEnoughReplicas` | **④ min.isr quá cao** | `kcfg --entity-type topics --entity-name prod-orders --delete-config min.insync.replicas` |

6. **Sửa**, rồi xác nhận mọi alert về `inactive` và produce chạy lại.

   ```bash
   pq 'sum(kafka_controller_kafkacontroller_offlinepartitionscount)'      # 0
   pq 'sum(kafka_server_replicamanager_underminisrpartitioncount)'        # 0
   kperf --topic prod-orders --num-records 5000 --record-size 256 --throughput -1 \
         --producer-props bootstrap.servers=$KAFKA_BS acks=all
   ```

7. **Mở đáp án và tự chấm:**

   ```bash
   cat ~/kafka-labs/week-07/.what-broke
   ```

   | Tiêu chí tự chấm | Đạt? |
   |---|---|
   | Lệnh **đầu tiên** của bạn là một metric tầng 1 (không phải `docker compose logs`) | ☐ |
   | Bạn loại trừ được tầng 1 **trước khi** thử từ phía client | ☐ |
   | Bạn đọc config **sau** khi đã có giả thuyết, không phải đọc mò từ đầu | ☐ |
   | Hành động sửa của bạn là **đảo ngược được** (không tắt broker, không xoá topic, không hạ min.isr) | ☐ |
   | Bạn chẩn đoán đúng **trước khi** mở `.what-broke` | ☐ |

8. Chạy lại toàn bộ lab **ít nhất 4 lần** — đủ để gặp cả bốn kịch bản. Mục tiêu: lần thứ tư chẩn đoán xong trong **dưới 3 phút**.

### ✅ Kiểm chứng

- Với kịch bản **④**, `UnderMinIsrPartitionCount` > 0 **trong khi `docker compose ps` cho thấy đủ 3 broker sống** — đây là chữ ký phân biệt "config sai" với "broker chết", và là điểm nhiều người chẩn đoán nhầm nhất.
- Với kịch bản **③**, mọi metric broker đều sạch và **không** có dòng lỗi nào trong log; chỉ có throughput bị chặn. Cluster khoẻ + client bị chặn = quota.
- Sau bước 6, cả 8 alert trong `/api/v1/rules` đều về `inactive`.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
kcfg --alter --entity-type topics  --entity-name prod-orders --delete-config min.insync.replicas 2>/dev/null
kcfg --alter --entity-type brokers --entity-name 3 --delete-config advertised.listeners 2>/dev/null
kcfg --alter --entity-type clients --entity-name w7-probe --delete-config producer_byte_rate 2>/dev/null
kt --delete --topic canary 2>/dev/null
kt --delete --topic prod-orders 2>/dev/null
docker compose start kafka-1 kafka-2 kafka-3 2>/dev/null
rm -f ~/kafka-labs/week-07/.what-broke

# Tắt hẳn cả stack khi học xong tuần (GIỮ lại file cấu hình cho Tuần 8)
# docker compose down
```

### 🧠 Ý nghĩa với đề thi

- Đề CCAAK hỏi *"what should the administrator do FIRST?"* — lab này luyện đúng chữ **FIRST**: metric tầng 1 trước, hành động đảo ngược được trước.
- Bốn kịch bản trong script phủ đúng bốn dạng câu hỏi hay gặp nhất: **mất leader** · **client không tới được broker** · **bị chặn im lặng** · **config quá tay**.
- Kịch bản ④ là phiên bản đảo ngược của bẫy kinh điển: đề thường hỏi "có nên hạ `min.insync.replicas` không"; ở đây bạn thấy tận mắt điều gì xảy ra khi ai đó **nâng** nó quá số broker.

---

> ✅ Xong 7 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist), rồi làm [bộ 30 câu luyện tập](questions.md) và **🎯 FULL MOCK #1 (60 câu / 90 phút)**. Ngưỡng qua cổng sang Tuần 8: **≥75%**; dưới **70%** thì lùi lịch thi 1 tuần. Giữ nguyên `~/kafka-labs/prometheus/alerts.yml` và `docker-compose.monitoring-controller.yml` — capstone Tuần 8 dùng lại chính stack này.
