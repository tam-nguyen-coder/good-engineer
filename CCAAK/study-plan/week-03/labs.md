# 🧪 Hands-on Labs — Tuần 3: Replication & durability · Quotas · Throughput · JVM/OS

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: cluster **3 broker + 1 controller** từ [CCDAK Tuần 1 — Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md) (`~/kafka-labs/docker-compose.cluster.yml`) và bộ alias `kt`/`kcp`/`kcc`/`kcg`/`kcfg`/`kq`.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung

### 1) Khởi động cluster 3 broker và trỏ alias đúng listener

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d
docker compose -f docker-compose.cluster.yml ps          # 4 container: controller, kafka-1, kafka-2, kafka-3

export KAFKA_CTR=kafka-1
export KAFKA_BS=kafka-1:19092
kq describe --status                                      # LeaderId: 1, CurrentObservers: 2,3,4
```

> 🧠 **Nhắc lại sơ đồ node** (đừng nhầm `node.id` với tên container):
>
> | Container | `node.id` | Vai trò | Host port | Listener nội bộ |
> |---|---|---|---|---|
> | `controller` | **1** | `process.roles=controller` | — | `controller:9093` |
> | `kafka-1` | **2** | broker | `9092` | `kafka-1:19092` |
> | `kafka-2` | **3** | broker | `9094` | `kafka-2:19092` |
> | `kafka-3` | **4** | broker | `9096` | `kafka-3:19092` |
>
> Cluster này đã có sẵn `KAFKA_DEFAULT_REPLICATION_FACTOR=3` và `KAFKA_MIN_INSYNC_REPLICAS=2` — đúng bộ ba production để Tuần 3 khai thác.

### 2) File override JMX cho Lab 3.4 / 3.6 / 3.7

Ba lab cuối cần đọc MBean và GC log. Tạo **file override riêng** (không sửa `docker-compose.cluster.yml` gốc):

```yaml
# ~/kafka-labs/docker-compose.w3-jmx.yml
# Chỉ gắn JMX + GC log cho kafka-1. Không gắn cho controller để CLI vẫn chạy được từ đó.
services:
  kafka-1:
    ports:
      - "9092:9092"
      - "9999:9999"
    environment:
      JMX_PORT: "9999"
      KAFKA_JMX_OPTS: >-
        -Dcom.sun.management.jmxremote
        -Dcom.sun.management.jmxremote.authenticate=false
        -Dcom.sun.management.jmxremote.ssl=false
        -Dcom.sun.management.jmxremote.local.only=false
        -Djava.rmi.server.hostname=kafka-1
      # GC log đổ thẳng ra stdout của container → đọc bằng `docker compose logs`
      KAFKA_OPTS: "-Xlog:gc*:stdout:time,uptime,level,tags"
```

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml -f docker-compose.w3-jmx.yml up -d kafka-1
docker compose -f docker-compose.cluster.yml -f docker-compose.w3-jmx.yml logs kafka-1 | grep -c "gc,"   # > 0 là GC log đã bật
```

> ⚠️ **Bẫy vận hành thật (đã gặp ở CCDAK Tuần 8):** `JMX_PORT` áp cho **mọi** script trong `bin/`, không riêng broker. Vì vậy từ đây trở đi **chạy CLI từ container `controller`**, không chạy trong `kafka-1`:
>
> ```bash
> export KAFKA_CTR=controller        # alias kt/kcfg/... vẫn bootstrap tới kafka-1:19092
> ```
>
> Nếu quên, bạn sẽ thấy `java.rmi.server.ExportException: Port already in use: 9999`. Cách chữa nhanh khác: `docker exec -e JMX_PORT= -e KAFKA_OPTS= kafka-1 ...`.

### 3) Thư mục làm việc của tuần

```bash
mkdir -p ~/kafka-labs/week-03
cd ~/kafka-labs/week-03
```

---

## Lab 3.1 — Ma trận durability: tắt 1 rồi 2 broker, đo `acks=all` vs `acks=1` ⭐

**🎯 Mục tiêu:** Tự tay dựng lại **Bảng 1** của [README](README.md#-buổi-a--lý-thuyết-3h) bằng số liệu thực nghiệm trên cluster của bạn: với RF=3 / `min.insync.replicas=2`, mất **1** broker thì `acks=all` vẫn ghi được, mất **2** thì không — còn `acks=1` thì "ghi được" trong cả hai trường hợp nhưng **đánh đổi bằng dữ liệu**.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc được `Isr:` co lại trong `kafka-topics.sh --describe` và ba bộ lọc `--under-replicated-partitions` / `--under-min-isr-partitions` / `--at-min-isr-partitions`.
- Nhận diện **nguyên văn** `NotEnoughReplicasException` và biết nó nghĩa là gì với dữ liệu.
- Hiểu vì sao `min.insync.replicas` **vô hiệu** khi `acks≠all` — và vì sao đặt `acks=1` trên producer 4.x lại **ném `ConfigException`** nếu quên tắt idempotence.

**⏱️ ~45 phút** · **Yêu cầu trước:** Chuẩn bị chung bước 1. *(Đây là lab "gây hỏng rồi sửa" số 1 của tuần.)*

### Các bước

1. Tạo topic **1 partition** (dễ suy luận leader) với RF=3 và `min.insync.replicas=2`.

   ```bash
   kt --create --topic dur-lab --partitions 1 --replication-factor 3 \
      --config min.insync.replicas=2
   kt --describe --topic dur-lab
   ```

   Kết quả mong đợi — nhớ **thứ tự** trong `Replicas:`, phần tử đầu là **preferred leader**:

   ```
   Topic: dur-lab  TopicId: ...  PartitionCount: 1  ReplicationFactor: 3  Configs: min.insync.replicas=2
     Topic: dur-lab  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3,4  Elr:  LastKnownElr:
   ```
2. **Trạng thái 0 broker chết** — ghi thử với `acks=all`.

   ```bash
   echo "msg-full-isr" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic dur-lab \
     --producer-property acks=all
   ```

   Không in lỗi = ghi thành công. Ghi vào bảng thực nghiệm của bạn: `0 broker down · acks=all · OK`.
3. **Tắt 1 broker** (chọn broker **không** phải leader trước để thấy ISR co mà leader không đổi; ở ví dụ trên leader là node 2 = `kafka-1`, nên tắt `kafka-3` = node 4).

   ```bash
   docker compose -f docker-compose.cluster.yml stop kafka-3
   sleep 15
   kt --describe --topic dur-lab
   ```

   ```
     Topic: dur-lab  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3  Elr:  LastKnownElr:
   ```

   Ba bộ lọc chẩn đoán — chú ý **cái nào có kết quả, cái nào rỗng**:

   ```bash
   kt --describe --under-replicated-partitions     # dur-lab XUẤT HIỆN (|ISR| 2 < |replicas| 3)
   kt --describe --at-min-isr-partitions           # dur-lab XUẤT HIỆN (|ISR| 2 = min.isr 2) → cảnh báo sớm
   kt --describe --under-min-isr-partitions        # RỖNG (chưa < min.isr) → acks=all vẫn chạy
   ```
4. Ghi lại với `acks=all` khi **còn 1 broker chết**.

   ```bash
   echo "msg-1-down" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic dur-lab --producer-property acks=all
   ```

   Vẫn **thành công**. Đây chính là ô ⭐ của Bảng 1: `RF−min.isr = 3−2 = 1` broker được phép chết.
5. **Tắt broker thứ hai** → ISR co về 1 → `acks=all` phải **thất bại**.

   ```bash
   docker compose -f docker-compose.cluster.yml stop kafka-2
   sleep 15
   kt --describe --topic dur-lab
   kt --describe --under-min-isr-partitions        # BÂY GIỜ dur-lab mới xuất hiện

   echo "msg-2-down" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic dur-lab --producer-property acks=all
   ```

   Lỗi mong đợi (đọc **nguyên văn**, đây là dòng hay xuất hiện trong đề):

   ```
   [2026-09-20 10:12:44,918] ERROR Error when sending message to topic dur-lab with key: null, value: 10 bytes with error: (org.apache.kafka.clients.producer.internals.ErrorLoggingCallback)
   org.apache.kafka.common.errors.NotEnoughReplicasException: Messages are rejected since there are fewer in-sync replicas than required.
   ```
6. **Đổi sang `acks=1`** trong đúng tình huống đó — và gặp bẫy config của Kafka 4.x.

   ```bash
   # Lần 1: CHỈ đặt acks=1 → producer không khởi động được
   echo "msg-acks1" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic dur-lab --producer-property acks=1
   ```

   ```
   org.apache.kafka.common.config.ConfigException: Must set acks to all in order to use the idempotent producer.
   Otherwise we cannot guarantee idempotence.
   ```

   ```bash
   # Lần 2: tắt idempotence rồi mới hạ acks
   echo "msg-acks1" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic dur-lab \
     --producer-property acks=1 --producer-property enable.idempotence=false
   ```

   Lần này **ghi thành công** dù ISR chỉ còn 1 → `min.insync.replicas=2` **không được kiểm tra**.
7. **Sửa lại cluster** và kiểm tra dữ liệu.

   ```bash
   docker compose -f docker-compose.cluster.yml start kafka-2 kafka-3
   sleep 25
   kt --describe --topic dur-lab                   # Isr quay về 2,3,4
   kt --describe --under-replicated-partitions     # rỗng

   docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic dur-lab --from-beginning --timeout-ms 8000
   ```
8. Điền bảng thực nghiệm của riêng bạn rồi so với Bảng 1 trong README:

   | Broker down | `acks` | Kết quả ghi | Lỗi (nếu có) |
   |---|---|---|---|
   | 0 | `all` | | |
   | 1 | `all` | | |
   | 2 | `all` | | |
   | 2 | `1` (+ `enable.idempotence=false`) | | |

### ✅ Kiểm chứng

- Bước 3: `--under-replicated-partitions` **có** `dur-lab`, `--under-min-isr-partitions` **rỗng**. Nếu cả hai đều rỗng thì ISR chưa kịp co — chờ thêm (`broker.session.timeout.ms` 9000 ms + thời gian controller cập nhật metadata) rồi describe lại.
- Bước 5: bắt được đúng chuỗi `NotEnoughReplicasException: Messages are rejected since there are fewer in-sync replicas than required.`
- Bước 6 lần 1: bắt được đúng `ConfigException: Must set acks to all in order to use the idempotent producer.`
- Bước 7: `Isr: 2,3,4` trở lại đầy đủ và consumer đọc được **cả** `msg-acks1` (nó đã được ghi thật, chỉ là ghi **không an toàn**).

### 🧹 Dọn dẹp

```bash
kt --delete --topic dur-lab
docker compose -f docker-compose.cluster.yml start kafka-2 kafka-3   # chắc chắn cả 3 broker đã sống
```

### 🧠 Ý nghĩa với đề thi

- Nhớ công thức: **số broker được phép chết mà vẫn ghi được = `RF − min.insync.replicas`**. RF 3 / min.isr 2 → **đúng 1**.
- `min.insync.replicas` **chỉ sống cùng `acks=all`**. Câu hỏi "đã đặt min.isr=2 mà sao vẫn mất dữ liệu" gần như luôn có đáp án là producer đang dùng `acks=1`.
- Ba bộ lọc `--under-replicated-partitions` / `--at-min-isr-partitions` / `--under-min-isr-partitions` tương ứng ba metric `UnderReplicatedPartitions` / `AtMinIsrPartitionCount` / `UnderMinIsrPartitionCount`. **Chỉ cái cuối** nghĩa là "`acks=all` đang bị chặn".

---

## Lab 3.2 — Over-correction: `min.insync.replicas=3` làm ngừng ghi, rồi sửa nóng về 2

**🎯 Mục tiêu:** Tái hiện đúng sai lầm mà đề CCAAK hỏi đi hỏi lại — "muốn an toàn hơn nên đặt `min.isr` bằng RF" — rồi chữa lại **mà không restart broker nào**.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đặt và gỡ override `min.insync.replicas` ở **mức topic** bằng `kafka-configs.sh` (dynamic).
- Phân biệt `--add-config` (đè giá trị) và `--delete-config` (xoá override, rơi về giá trị broker).
- Đọc cột **synonyms** trong `--describe --all` để biết giá trị hiệu lực đến từ đâu.

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 3.1 (cluster đã đủ 3 broker). *(Đây là lab "gây hỏng rồi sửa" số 2 của tuần.)*

### Các bước

1. Tạo topic mô phỏng "topic thanh toán rất quan trọng".

   ```bash
   kt --create --topic payments-strict --partitions 3 --replication-factor 3
   kcfg --describe --entity-type topics --entity-name payments-strict
   ```

   Chưa có override nào → topic đang dùng `min.insync.replicas` **của broker (2)**.
2. **Gây hỏng:** một kỹ sư "cẩn thận quá" đặt `min.insync.replicas=3`.

   ```bash
   kcfg --alter --entity-type topics --entity-name payments-strict \
        --add-config min.insync.replicas=3
   kcfg --describe --entity-type topics --entity-name payments-strict
   ```

   ```
   Dynamic configs for topic payments-strict are:
     min.insync.replicas=3 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:min.insync.replicas=3, STATIC_BROKER_CONFIG:min.insync.replicas=2, DEFAULT_CONFIG:min.insync.replicas=1}
   ```

   > 🧠 Đọc dòng `synonyms` từ **trái sang phải**: giá trị hiệu lực là cái **đầu tiên** — `DYNAMIC_TOPIC_CONFIG` thắng `STATIC_BROKER_CONFIG` thắng `DEFAULT_CONFIG`.
3. Ghi thử khi cluster **khoẻ mạnh hoàn toàn** — vẫn OK (ISR = 3 = min.isr).

   ```bash
   echo "pay-ok" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic payments-strict --producer-property acks=all
   ```
4. **Tắt đúng 1 broker** — thứ mà cluster RF=3 lẽ ra phải chịu được.

   ```bash
   docker compose -f docker-compose.cluster.yml stop kafka-3
   sleep 15
   kt --describe --under-min-isr-partitions
   ```

   ```
   Topic: payments-strict  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3  Elr:  LastKnownElr:
   Topic: payments-strict  Partition: 1  Leader: 3  Replicas: 3,4,2  Isr: 3,2  Elr:  LastKnownElr:
   Topic: payments-strict  Partition: 2  Leader: 4  ...
   ```

   ```bash
   echo "pay-fail" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic payments-strict --producer-property acks=all
   ```

   ```
   org.apache.kafka.common.errors.NotEnoughReplicasException: Messages are rejected since there are fewer in-sync replicas than required.
   ```

   👉 **Toàn bộ topic ngừng nhận ghi chỉ vì mất 1 broker.** Đây đúng là hậu quả của over-correction.
5. **Sai lầm thường gặp khi chữa cháy:** hạ min.isr xuống 1. Thử để thấy nó "chạy được" — rồi hiểu vì sao đó là sai.

   ```bash
   kcfg --alter --entity-type topics --entity-name payments-strict --add-config min.insync.replicas=1
   echo "pay-danger" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic payments-strict --producer-property acks=all
   ```

   Ghi được — nhưng giờ một ghi `acks=all` chỉ cần **1 bản sao** là được xác nhận. Đúng thứ mà `min.insync.replicas` sinh ra để ngăn.
6. **Sửa đúng cách:** xoá override để topic quay về giá trị broker (**2**), rồi khôi phục broker.

   ```bash
   kcfg --alter --entity-type topics --entity-name payments-strict --delete-config min.insync.replicas
   kcfg --describe --entity-type topics --entity-name payments-strict    # không còn dynamic config

   echo "pay-ok-2" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic payments-strict --producer-property acks=all

   docker compose -f docker-compose.cluster.yml start kafka-3
   sleep 25
   kt --describe --under-replicated-partitions      # rỗng
   ```
7. Xác nhận **không broker nào bị restart** trong cả bài:

   ```bash
   docker inspect -f '{{.Name}} started={{.State.StartedAt}}' kafka-1 kafka-2
   ```

### ✅ Kiểm chứng

- Bước 2: dòng `synonyms` in ra đúng 3 nguồn theo thứ tự `DYNAMIC_TOPIC_CONFIG` → `STATIC_BROKER_CONFIG` → `DEFAULT_CONFIG`.
- Bước 4: `--under-min-isr-partitions` liệt kê **cả 3 partition** và producer `acks=all` ném `NotEnoughReplicasException` — dù cluster vẫn còn **2/3 broker sống**.
- Bước 6: sau `--delete-config`, ghi `acks=all` thành công ngay lập tức **khi vẫn còn 1 broker đang tắt** (vì min.isr đã về 2, ISR = 2).
- Bước 7: `StartedAt` của kafka-1 và kafka-2 **không đổi** so với lúc bắt đầu lab.

### 🧹 Dọn dẹp

```bash
kt --delete --topic payments-strict
docker compose -f docker-compose.cluster.yml start kafka-3
```

### 🧠 Ý nghĩa với đề thi

- `min.insync.replicas = RF` là **over-correction** kinh điển. Với RF=3, đáp án đúng luôn là **2**.
- Khi gặp `NotEnoughReplicasException` trong đề, hành động đầu tiên là **khôi phục replica**, không phải hạ min.isr. Hạ min.isr chỉ hợp lệ khi giá trị đang **sai** (ví dụ min.isr > RF).
- `min.insync.replicas` đổi được **nóng** ở cả mức topic lẫn mức broker/cluster — đây là điểm phân biệt với `replica.lag.time.max.ms` hay `auto.leader.rebalance.enable` (`read-only`, phải restart).

---

## Lab 3.3 — ELR: bật `eligible.leader.replicas.version`, đọc cột `Elr:`

**🎯 Mục tiêu:** Nhìn thấy tận mắt hai cột `Elr:` và `LastKnownElr:` được điền khi ISR co lại, và hiểu vì sao ELR **không phải** unclean leader election.
**🧩 Luyện kỹ năng (liên quan đề):**

- Dùng `kafka-features.sh describe` / `upgrade --feature` / `downgrade --feature` — cơ chế feature version của KRaft.
- Đọc `kafka-topics.sh --describe` ở Kafka 4.x với đủ 2 cột ELR.
- Nhớ **thứ tự bầu leader**: ISR → ELR → last known leader.

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 3.1.

### Các bước

1. Xem cluster đang ở feature version nào.

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-features.sh \
     --bootstrap-server kafka-1:19092 describe
   ```

   ```
   Feature: eligible.leader.replicas.version  SupportedMinVersion: 0  SupportedMaxVersion: 1  FinalizedVersionLevel: 1  Epoch: 12
   Feature: kraft.version                     SupportedMinVersion: 0  SupportedMaxVersion: 1  FinalizedVersionLevel: 0  Epoch: 12
   Feature: metadata.version                  SupportedMinVersion: 3.3-IV3  SupportedMaxVersion: 4.3-IV1  FinalizedVersionLevel: 4.3-IV1  Epoch: 12
   ...
   ```

   > 📌 Cluster **mới format** bằng Kafka ≥ 4.1 thường đã có `eligible.leader.replicas.version=1` **sẵn**. Nếu `FinalizedVersionLevel` của nó là **0** thì đi tiếp bước 2; nếu đã là **1** thì làm bước 2' (hạ xuống 0 trước) để thấy rõ khác biệt trước/sau.
2. **Bật ELR** (khi đang là 0):

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-features.sh \
     --bootstrap-server kafka-1:19092 upgrade --feature eligible.leader.replicas.version=1
   ```

   2'. **Hoặc hạ rồi bật lại** (khi đang là 1) để quan sát cả hai trạng thái:

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-features.sh \
     --bootstrap-server kafka-1:19092 downgrade --feature eligible.leader.replicas.version=0
   ```
3. Tạo topic thử và xem hai cột ELR khi cluster khoẻ.

   ```bash
   kt --create --topic elr-lab --partitions 1 --replication-factor 3 --config min.insync.replicas=2
   kt --describe --topic elr-lab
   ```

   ```
     Topic: elr-lab  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3,4  Elr:      LastKnownElr:
   ```

   Hai cột **rỗng** vì ISR còn đầy đủ — ELR chỉ có nghĩa khi ISR đã co.
4. **Ép ISR co xuống dưới `min.insync.replicas`**: tắt 2 broker không phải leader.

   ```bash
   docker compose -f docker-compose.cluster.yml stop kafka-2 kafka-3
   sleep 20
   kt --describe --topic elr-lab
   ```

   Kết quả mong đợi khi ELR **đã bật** — replica rời ISB **sau khi** HW bị đóng băng sẽ rơi vào `Elr:`:

   ```
     Topic: elr-lab  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2  Elr: 3,4  LastKnownElr:
   ```

   Nếu ELR **chưa bật** (bước 2'), hai cột vẫn rỗng:

   ```
     Topic: elr-lab  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2  Elr:      LastKnownElr:
   ```
5. Xem metric riêng của ELR (cần override JMX ở Chuẩn bị chung bước 2 — có thể bỏ qua nếu chưa bật):

   ```bash
   docker exec -e JMX_PORT= -e KAFKA_OPTS= kafka-1 /opt/kafka/bin/kafka-run-class.sh \
     org.apache.kafka.tools.JmxTool \
     --jmx-url service:jmx:rmi:///jndi/rmi://kafka-1:9999/jmxrmi \
     --object-name 'kafka.controller:type=ControllerStats,name=ElectionFromEligibleLeaderReplicasPerSec' \
     --one-time
   ```

   > ⚠️ Cú pháp `--one-time` / `--one-time true` khác nhau giữa các bản. Chạy `... JmxTool --help` một lần để lấy đúng cú pháp trên image của bạn. Metric này **chỉ tăng ở active controller** — ở cluster lab, controller là container `controller`, nên số này ở `kafka-1` sẽ luôn là 0.
6. Khôi phục và xác nhận `Elr:` trống trở lại.

   ```bash
   docker compose -f docker-compose.cluster.yml start kafka-2 kafka-3
   sleep 30
   kt --describe --topic elr-lab
   ```
7. Xác nhận ràng buộc mới của `min.insync.replicas` khi ELR bật — thử sửa ở **mức broker** (phải bị từ chối):

   ```bash
   kcfg --alter --entity-type brokers --entity-name 2 --add-config min.insync.replicas=2
   ```

   Nếu ELR đang bật, lệnh trả về lỗi vì "alteration of `min.insync.replicas` config at the broker-level is not allowed" — muốn đổi thì đổi ở **cluster level** (`--entity-default`) hoặc ở **topic**.

### ✅ Kiểm chứng

- Bước 1: `kafka-features.sh describe` in ra dòng `eligible.leader.replicas.version` với `SupportedMaxVersion: 1`.
- Bước 4: với ELR **bật**, cột `Elr:` có ít nhất một node id sau khi ISR co xuống 1. Với ELR **tắt**, cột luôn rỗng. (Nếu ELR bật mà `Elr:` vẫn rỗng: ISR chưa xuống **dưới** `min.insync.replicas`, hoặc replica bị coi là *fenced* vì broker tắt hẳn — thử tắt chỉ **một** broker khi `min.insync.replicas=3` để HW đóng băng sớm hơn.)
- Bước 6: `Isr: 2,3,4`, `Elr:` rỗng.
- Bước 7: lệnh sửa broker-level bị từ chối khi ELR bật, chạy được khi ELR tắt.

### 🧹 Dọn dẹp

```bash
kt --delete --topic elr-lab
# Trả feature về trạng thái ban đầu nếu bạn đã downgrade ở bước 2'
docker exec $KAFKA_CTR /opt/kafka/bin/kafka-features.sh \
  --bootstrap-server kafka-1:19092 upgrade --feature eligible.leader.replicas.version=1
docker compose -f docker-compose.cluster.yml start kafka-2 kafka-3
```

### 🧠 Ý nghĩa với đề thi

- Thứ tự bầu leader khi ELR bật: **① ISR → ② ELR (replica chưa fenced) → ③ last known leader (unfenced)**. Dạng câu *list order* rất hay dùng đúng ba dòng này.
- ELR **không mất dữ liệu**; unclean leader election **mất dữ liệu**. Thấy "cần partition sống lại mà không mất dữ liệu" → ELR; "chấp nhận mất dữ liệu để có uptime" → unclean.
- Khi ELR bật, `min.insync.replicas` **phải đặt ở cluster level hoặc topic level** — broker level bị gỡ. Và mọi lần sửa cluster-level đều **xoá sạch ELR state**.

---

## Lab 3.4 — Quota băng thông: bị kìm mà không có lỗi, và chứng minh mức ưu tiên ⭐

**🎯 Mục tiêu:** Thấy tận mắt triệu chứng kinh điển nhất của quota — **throughput đụng trần, log hoàn toàn sạch** — rồi chồng thêm một quota `(user, client-id)` để chứng minh **mức 1 thắng mức 3**, và kiểm tra bằng phép nhân "quota là per-broker".
**🧩 Luyện kỹ năng (liên quan đề):**

- Viết đúng lệnh `kafka-configs.sh` cho từng mức ưu tiên (`--entity-name` vs `--entity-default`).
- Biết principal của client **không xác thực** là `ANONYMOUS`.
- Đọc `throttle-time` / `byte-rate` trên MBean `kafka.server:type=Produce,user=…,client-id=…`.

**⏱️ ~50 phút** · **Yêu cầu trước:** Chuẩn bị chung bước 2 (JMX), `export KAFKA_CTR=controller`.

### Các bước

1. Tạo topic **1 partition** để toàn bộ traffic đổ vào **một broker** — giúp quan sát quota per-broker không bị nhiễu.

   ```bash
   export KAFKA_CTR=controller
   kt --create --topic quota-lab --partitions 1 --replication-factor 3
   ```
2. **Đo đường cơ sở** khi chưa có quota nào.

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic quota-lab --num-records 200000 --record-size 1000 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=perf-a acks=all
   ```

   ```
   200000 records sent, 41981.2 records/sec (40.04 MB/sec), 128.55 ms avg latency, 612.00 ms max latency, ...
   ```

   Con số cụ thể phụ thuộc máy bạn — chỉ cần ghi lại làm mốc.
3. Xác nhận principal của client PLAINTEXT là `ANONYMOUS`, rồi **đặt quota ở mức user (mức 3)**: 1 MB/s.

   ```bash
   kcfg --alter --entity-type users --entity-name ANONYMOUS \
        --add-config 'producer_byte_rate=1048576'
   kcfg --describe --entity-type users --entity-name ANONYMOUS
   ```

   ```
   Quota configs for user-principal 'ANONYMOUS' are producer_byte_rate=1048576.0
   ```
4. Chạy lại perf test — **giảm `--num-records`** vì bây giờ chỉ đi được ~1 MB/s.

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic quota-lab --num-records 20000 --record-size 1000 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=perf-a acks=all
   ```

   ```
   20000 records sent, 1024.3 records/sec (0.98 MB/sec), 4871.22 ms avg latency, 9640.00 ms max latency, ...
   ```

   👉 **~1 MB/s, đúng bằng quota.** Latency trung bình vọt lên hàng giây — đó là **thời gian bị trì hoãn response**, không phải lỗi.
5. **Chứng minh không có exception nào**: soi log broker và log client.

   ```bash
   docker compose -f docker-compose.cluster.yml logs --since 3m kafka-1 \
     | grep -iE "error|exception|throttle" | head
   ```

   Kết quả: **rỗng** (hoặc chỉ có dòng không liên quan). Đây chính là lý do đề mô tả triệu chứng là *"throughput bị chặn trần, log sạch"*.
6. Đọc bằng chứng thật — MBean quota phía broker.

   ```bash
   docker exec -e JMX_PORT= -e KAFKA_OPTS= kafka-1 /opt/kafka/bin/kafka-run-class.sh \
     org.apache.kafka.tools.JmxTool \
     --jmx-url service:jmx:rmi:///jndi/rmi://kafka-1:9999/jmxrmi \
     --object-name 'kafka.server:type=Produce,user=ANONYMOUS,client-id=perf-a' \
     --one-time
   ```

   ```
   kafka.server:type=Produce,user=ANONYMOUS,client-id=perf-a:byte-rate=1048400.7
   kafka.server:type=Produce,user=ANONYMOUS,client-id=perf-a:throttle-time=94.0
   ```

   `throttle-time` khác 0 = **đang bị throttle**. Phía client, metric tương đương là `produce-throttle-time-avg` / `produce-throttle-time-max`.
7. **Chứng minh mức ưu tiên**: thêm quota `(user=ANONYMOUS, client-id=perf-a)` = 4 MB/s (**mức 1**), giữ nguyên quota mức user 1 MB/s (**mức 3**).

   ```bash
   kcfg --alter --entity-type users --entity-name ANONYMOUS \
        --entity-type clients --entity-name perf-a \
        --add-config 'producer_byte_rate=4194304'

   kcfg --describe --entity-type users --entity-type clients
   ```

   ```
   Quota configs for user-principal 'ANONYMOUS', client-id 'perf-a' are producer_byte_rate=4194304.0
   ```

   ```bash
   # client-id perf-a → khớp mức 1 → 4 MB/s
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic quota-lab --num-records 60000 --record-size 1000 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=perf-a acks=all

   # client-id perf-b → KHÔNG khớp mức 1 → rơi về mức 3 → vẫn 1 MB/s
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic quota-lab --num-records 20000 --record-size 1000 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=perf-b acks=all
   ```
8. **Chứng minh quota là per-broker**: tạo topic 3 partition (trải trên 3 broker) rồi chạy lại với quota mức user 1 MB/s.

   ```bash
   kcfg --alter --entity-type users --entity-name ANONYMOUS \
        --entity-type clients --entity-name perf-a --delete-config 'producer_byte_rate'

   kt --create --topic quota-lab-3p --partitions 3 --replication-factor 3
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic quota-lab-3p --num-records 60000 --record-size 1000 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=perf-a acks=all
   ```

   ```
   60000 records sent, 3050.1 records/sec (2.91 MB/sec), ...
   ```

   👉 **≈3 MB/s = 1 MB/s × 3 broker.** Quota **không** phải giới hạn toàn cluster.

### ✅ Kiểm chứng

- Bước 4: throughput in ra **≈ 0.95–1.05 MB/sec**, sát giá trị `producer_byte_rate`.
- Bước 5: grep log broker **không** ra exception nào liên quan producer.
- Bước 6: `throttle-time` > 0 và `byte-rate` ≈ quota.
- Bước 7: `perf-a` đạt ≈ **4 MB/s**, `perf-b` vẫn ≈ **1 MB/s** — đúng thứ tự ưu tiên mức 1 > mức 3.
- Bước 8: throughput ≈ **3 ×** quota trên topic 3 partition.

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type users --entity-name ANONYMOUS --delete-config 'producer_byte_rate'
kcfg --describe --entity-type users            # phải rỗng
kt --delete --topic quota-lab
kt --delete --topic quota-lab-3p
```

### 🧠 Ý nghĩa với đề thi

- **Throttle = trì hoãn response + mute channel.** Không có exception, không có dòng log. Bằng chứng duy nhất là **metric throttle-time**. Đây là một trong những câu "triệu chứng" dễ nhận nhất của CCAAK.
- **Quota là per-broker.** Bài toán "đặt bao nhiêu để tenant này tối đa 300 MB/s trên cluster 10 broker" → `producer_byte_rate = 30 MB/s`.
- Mức ưu tiên: **user thắng client-id**; trong cùng cấp, **tên cụ thể thắng default**. Đặt quota cho user rồi mà một client vẫn vượt → chắc chắn có quota `(user, client-id)` cụ thể hơn đang thắng.
- Mặc định **không có quota nào** — client được dùng vô hạn cho tới khi admin đặt.

---

## Lab 3.5 — `num.replica.fetchers`: đo thời gian URP về 0 với 1 fetcher so với 4

**🎯 Mục tiêu:** Đo bằng đồng hồ tác dụng của `num.replica.fetchers` — con số rẻ nhất, đảo ngược được, **không cần restart** để kéo `UnderReplicatedPartitions` về 0 nhanh hơn.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đổi config **cluster-wide** động bằng `kafka-configs.sh --entity-type brokers --entity-default`.
- Viết vòng lặp đo URP — đúng cách người vận hành theo dõi rolling restart.
- Phân biệt `BytesInPerSec` (từ client) và `ReplicationBytesInPerSec` (từ broker khác).

**⏱️ ~45 phút** · **Yêu cầu trước:** Lab 3.1. Cần khoảng **1 GB** dung lượng trống cho Docker.

### Các bước

1. Tạo topic nhiều partition và xác nhận `num.replica.fetchers` đang là mặc định.

   ```bash
   kt --create --topic fetcher-lab --partitions 12 --replication-factor 3
   kcfg --describe --entity-type brokers --entity-name 2 --all | grep "num.replica.fetchers"
   ```

   ```
     num.replica.fetchers=1 sensitive=false synonyms={DEFAULT_CONFIG:num.replica.fetchers=1}
   ```
2. **Tắt một broker**, rồi nạp dữ liệu trong lúc nó đang chết → khi bật lại nó sẽ phải đuổi một khoảng lớn.

   ```bash
   docker compose -f docker-compose.cluster.yml stop kafka-3
   sleep 10

   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic fetcher-lab --num-records 300000 --record-size 1024 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=filler acks=1 enable.idempotence=false
   ```

   (≈ 300 MB. Máy yếu thì giảm còn 150000 records.)
3. Chuẩn bị script đo — lưu lại để chạy lại ở bước 5.

   ```bash
   cat > ~/kafka-labs/week-03/wait-urp.sh <<'EOF'
   #!/usr/bin/env bash
   # Đo số giây đến khi UnderReplicatedPartitions về 0
   start=$(date +%s)
   while true; do
     n=$(docker exec controller /opt/kafka/bin/kafka-topics.sh \
           --bootstrap-server kafka-1:19092 \
           --describe --under-replicated-partitions 2>/dev/null | grep -c "Topic:")
     printf "\r[%3ds] URP = %s " "$(( $(date +%s) - start ))" "$n"
     [ "$n" = "0" ] && break
     sleep 1
   done
   echo ""
   echo "URP về 0 sau $(( $(date +%s) - start )) giây"
   EOF
   chmod +x ~/kafka-labs/week-03/wait-urp.sh
   ```
4. **Lần đo 1 — `num.replica.fetchers=1`.**

   ```bash
   docker compose -f docker-compose.cluster.yml start kafka-3 && ~/kafka-labs/week-03/wait-urp.sh
   ```

   Ghi lại con số (ví dụ: `URP về 0 sau 58 giây`).
5. **Tăng lên 4 — cluster-wide, không restart** — rồi lặp lại đúng kịch bản.

   ```bash
   kcfg --alter --entity-type brokers --entity-default --add-config num.replica.fetchers=4
   kcfg --describe --entity-type brokers --entity-default

   docker compose -f docker-compose.cluster.yml stop kafka-3
   sleep 10
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic fetcher-lab --num-records 300000 --record-size 1024 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=filler acks=1 enable.idempotence=false

   docker compose -f docker-compose.cluster.yml start kafka-3 && ~/kafka-labs/week-03/wait-urp.sh
   ```
6. Xác nhận config mới đã áp **mà broker không hề restart**:

   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 --all | grep "num.replica.fetchers"
   ```

   ```
     num.replica.fetchers=4 sensitive=false synonyms={DYNAMIC_DEFAULT_BROKER_CONFIG:num.replica.fetchers=4, DEFAULT_CONFIG:num.replica.fetchers=1}
   ```

   ```bash
   docker inspect -f '{{.Name}} started={{.State.StartedAt}}' kafka-1 kafka-2
   ```
7. (Tuỳ chọn, cần JMX) So `ReplicationBytesInPerSec` giữa hai lần đo — chạy **trong lúc** catch-up:

   ```bash
   docker exec -e JMX_PORT= -e KAFKA_OPTS= kafka-1 /opt/kafka/bin/kafka-run-class.sh \
     org.apache.kafka.tools.JmxTool \
     --jmx-url service:jmx:rmi:///jndi/rmi://kafka-1:9999/jmxrmi \
     --object-name 'kafka.server:type=BrokerTopicMetrics,name=ReplicationBytesInPerSec' \
     --one-time
   ```

### ✅ Kiểm chứng

- Bước 4 và 5 in ra **hai con số giây khác nhau**, với 4 fetcher nhanh hơn.
- Bước 6: dòng synonyms có `DYNAMIC_DEFAULT_BROKER_CONFIG:num.replica.fetchers=4` **đứng trước** `DEFAULT_CONFIG:num.replica.fetchers=1`, và `StartedAt` của kafka-1/kafka-2 không đổi.

> ⚠️ **Đọc kết quả một cách trung thực.** Trên laptop, cả 4 broker dùng **chung một ổ đĩa và chung CPU**, nên nút thắt rất dễ là disk chứ không phải số fetcher thread — khoảng cách giữa 1 và 4 fetcher có thể rất nhỏ, thậm chí đảo chiều. Điều lab này dạy là **cách đo** và **cách đổi config nóng**; còn con số thật chỉ có ý nghĩa trên cluster mỗi broker một máy. Nếu muốn khuếch đại khác biệt: tăng số partition lên 30–50 và nạp nhiều dữ liệu hơn.

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type brokers --entity-default --delete-config num.replica.fetchers
kt --delete --topic fetcher-lab
rm -f ~/kafka-labs/week-03/wait-urp.sh
```

### 🧠 Ý nghĩa với đề thi

- "Broker đã sống lại nhưng URP mãi không về 0" → hành động **đầu tiên, rẻ nhất, đảo ngược được** là tăng `num.replica.fetchers`. Nó là `cluster-wide` → **không cần restart**.
- Đừng nhầm với `replica.fetch.max.bytes` (kích thước mỗi lần fetch, **`read-only`**, phải restart) hay với throttle của reassignment (`leader/follower.replication.throttled.rate`).
- Tổng fetcher trên mỗi broker = `num.replica.fetchers × số broker` — tăng vô tội vạ sẽ đốt CPU và bộ nhớ.

---

## Lab 3.6 — JVM: heap thật của broker, GC log, và page cache

**🎯 Mục tiêu:** Nhìn thấy heap mà broker **đang thực sự chạy**, đọc GC log, đổi `KAFKA_HEAP_OPTS`, và nhìn page cache trong container — để hiểu bằng trực giác vì sao **6 GB heap + G1GC** là khuyến nghị, không phải "càng to càng tốt".
**🧩 Luyện kỹ năng (liên quan đề):**

- Biết heap broker được đặt bằng biến môi trường **`KAFKA_HEAP_OPTS`**, không phải bằng config trong `server.properties`.
- Đọc được flag JVM đang chạy và dòng GC log.
- Giải thích **page cache vs heap** bằng số liệu thật.

**⏱️ ~40 phút** · **Yêu cầu trước:** Chuẩn bị chung bước 2 (override JMX/GC cho kafka-1).

### Các bước

1. Xem **flag JVM thật** mà broker đang chạy (không đoán từ tài liệu).

   ```bash
   docker exec kafka-1 sh -c "tr '\0' '\n' < /proc/1/cmdline | grep -E '^-X'"
   ```

   ```
   -Xmx1G
   -Xms1G
   -XX:+UseG1GC
   -XX:MaxGCPauseMillis=20
   -XX:InitiatingHeapOccupancyPercent=35
   -XX:+ExplicitGCInvokesConcurrent
   -Xlog:gc*:stdout:time,uptime,level,tags
   ```

   👉 Mặc định của script `kafka-server-start.sh` là **`-Xmx1G -Xms1G`** — **không** phải 6 GB. Con số 6 GB là **khuyến nghị vận hành**, phải tự đặt.
2. Đọc GC log (đã đổ ra stdout nhờ override ở Chuẩn bị chung).

   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.w3-jmx.yml logs kafka-1 \
     | grep -E "Pause Young|Pause Full" | tail -10
   ```

   ```
   [2026-09-20T03:11:42.905+0000][12.418s][info][gc] GC(7) Pause Young (Normal) (G1 Evacuation Pause) 92M->21M(1024M) 6.318ms
   ```

   Đọc: `92M->21M(1024M)` = heap trước → sau, tổng heap; `6.318ms` = độ dài pause. Đối chiếu mục tiêu `MaxGCPauseMillis=20`.
3. Kiểm tra công cụ JDK có sẵn trong image (khác nhau giữa image JRE và JDK):

   ```bash
   docker exec kafka-1 sh -c 'command -v jcmd jmap jstat 2>/dev/null; ls "$JAVA_HOME/bin" 2>/dev/null | head -20'
   ```

   Nếu có `jcmd`, xem heap và flag chi tiết:

   ```bash
   docker exec kafka-1 sh -c 'jcmd 1 GC.heap_info'
   docker exec kafka-1 sh -c 'jcmd 1 VM.flags | tr " " "\n" | grep -iE "heap|g1|gc"'
   ```

   Nếu **không** có (image chỉ đóng gói JRE) thì bước 1 + bước 2 đã đủ — đừng cài thêm gì vào container.
4. **Đổi `KAFKA_HEAP_OPTS`** cho một broker và quan sát hậu quả. Tạo override riêng:

   ```yaml
   # ~/kafka-labs/docker-compose.w3-heap.yml
   # CỐ TÌNH đặt heap rất nhỏ trên kafka-3 để thấy áp lực GC. KHÔNG dùng ở production.
   services:
     kafka-3:
       environment:
         KAFKA_HEAP_OPTS: "-Xms256m -Xmx256m -XX:+UseG1GC"
         KAFKA_OPTS: "-Xlog:gc*:stdout:time,uptime,level,tags"
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.w3-heap.yml up -d kafka-3
   docker exec kafka-3 sh -c "tr '\0' '\n' < /proc/1/cmdline | grep -E '^-Xm'"      # -Xms256m -Xmx256m
   ```

   Nạp tải rồi đếm số lần GC:

   ```bash
   docker exec controller /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic heap-lab --num-records 200000 --record-size 1024 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=heap-test acks=all 2>/dev/null \
     || kt --create --topic heap-lab --partitions 6 --replication-factor 3

   docker compose -f docker-compose.cluster.yml -f docker-compose.w3-heap.yml logs --since 3m kafka-3 \
     | grep -c "Pause Young"
   ```

   So với `kafka-1` (heap 1 GB) trong cùng khoảng thời gian:

   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.w3-jmx.yml logs --since 3m kafka-1 \
     | grep -c "Pause Young"
   ```
5. **Page cache** — nhìn phần RAM mà OS đang dùng để cache file log của Kafka.

   ```bash
   docker exec kafka-1 sh -c "grep -E 'MemTotal|MemFree|MemAvailable|^Cached|Buffers|Dirty' /proc/meminfo"
   ```

   ```
   MemTotal:        8123456 kB
   MemFree:          412332 kB
   MemAvailable:    5233112 kB
   Buffers:           28100 kB
   Cached:          4890220 kB
   Dirty:              6212 kB
   ```

   Chạy một consumer đọc lại từ đầu rồi đo lại — `Cached` sẽ tăng vì segment được nạp vào page cache:

   ```bash
   docker exec controller /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic fetcher-lab --from-beginning \
     --max-messages 200000 > /dev/null 2>&1 || true
   docker exec kafka-1 sh -c "grep -E '^Cached' /proc/meminfo"
   ```

   > 📌 **Trên macOS/Windows**, container chạy trong một VM Linux của Docker Desktop, nên `/proc/meminfo` phản ánh **VM đó**, không phải máy thật của bạn. Con số vẫn dùng được để thấy xu hướng `Cached` tăng, nhưng đừng đem so với RAM laptop.
6. Trả `kafka-3` về mặc định:

   ```bash
   docker compose -f docker-compose.cluster.yml up -d kafka-3
   docker exec kafka-3 sh -c "tr '\0' '\n' < /proc/1/cmdline | grep -E '^-Xm'"      # quay lại -Xmx1G
   ```
7. Ghi lại công thức production để nhớ: trên máy **32 GB RAM**, đặt heap **6 GB** → còn **~26 GB** cho page cache (Confluent ghi 28–30 GB). Đặt heap 24 GB → page cache chỉ còn vài GB, đọc lệch khỏi tail sẽ **chạm đĩa** và GC pause dài đủ để **đẩy follower ra khỏi ISR**.

### ✅ Kiểm chứng

- Bước 1: thấy rõ `-Xmx1G -Xms1G` và `-XX:+UseG1GC` — xác nhận Kafka **mặc định đã dùng G1GC**, còn heap thì **không** phải 6 GB.
- Bước 2: có ít nhất một dòng `Pause Young … ms`.
- Bước 4: số dòng `Pause Young` trên `kafka-3` (heap 256 MB) **lớn hơn rõ rệt** so với `kafka-1` (heap 1 GB) trong cùng khoảng `--since`.
- Bước 5: `Cached` tăng sau khi consumer đọc lại toàn bộ topic.
- Bước 6: `kafka-3` quay về `-Xmx1G`.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d kafka-3      # bỏ override heap
kt --delete --topic heap-lab 2>/dev/null || true
rm -f ~/kafka-labs/docker-compose.w3-heap.yml
```

### 🧠 Ý nghĩa với đề thi

- Heap broker đặt bằng **`KAFKA_HEAP_OPTS`** (biến môi trường), **không** có trong `server.properties`. Đổi nó **bắt buộc restart** broker.
- Khuyến nghị: **`-Xms6g -Xmx6g -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M`**. `-Xms` = `-Xmx`.
- "Broker chậm → tăng heap" là **bẫy**. Kafka dựa **page cache**; heap to = page cache nhỏ + GC pause dài → **ISR flapping**.
- GC pause dài là một trong hai nghi phạm đầu tiên khi `IsrShrinksPerSec`/`IsrExpandsPerSec` dao động (nghi phạm còn lại là disk latency).

---

## Lab 3.7 — `request_percentage`: quota CPU và metric throttle tương ứng

**🎯 Mục tiêu:** Đặt loại quota thứ ba — quota **thời gian CPU của broker** — và đọc đúng cặp metric `throttle-time` + `request-time` trên MBean `kafka.server:type=Request`.
**🧩 Luyện kỹ năng (liên quan đề):**

- Hiểu `request_percentage` là **% của một thread**, trần là `(num.io.threads + num.network.threads) × 100`%.
- Biết khi nào quota CPU hiệu quả hơn quota băng thông.
- Đọc MBean `Request` khác với MBean `Produce`/`Fetch`.

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung bước 2 (JMX), `export KAFKA_CTR=controller`.

### Các bước

1. Tính trần request quota của broker này.

   ```bash
   export KAFKA_CTR=controller
   kcfg --describe --entity-type brokers --entity-name 2 --all \
     | grep -E "^\s+(num.io.threads|num.network.threads)="
   ```

   ```
     num.io.threads=8 sensitive=false synonyms={DEFAULT_CONFIG:num.io.threads=8}
     num.network.threads=3 sensitive=false synonyms={DEFAULT_CONFIG:num.network.threads=3}
   ```

   👉 Trần = `(8 + 3) × 100` = **1100%**. Một client dùng hết `request_percentage=100` nghĩa là chiếm trọn **1 thread**.
2. Tạo topic và đo đường cơ sở với **record rất nhỏ** — nhiều request bé là cách nhanh nhất đốt CPU broker.

   ```bash
   kt --create --topic reqquota-lab --partitions 3 --replication-factor 3

   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic reqquota-lab --num-records 300000 --record-size 64 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=cpu-hog acks=all \
                      linger.ms=0 batch.size=1
   ```

   `linger.ms=0 batch.size=1` cố tình **phá batching** → mỗi record gần như một request.
3. Đặt `request_percentage` rất thấp cho cặp `(ANONYMOUS, cpu-hog)` — **mức ưu tiên 1**.

   ```bash
   kcfg --alter --entity-type users --entity-name ANONYMOUS \
        --entity-type clients --entity-name cpu-hog \
        --add-config 'request_percentage=5'
   kcfg --describe --entity-type users --entity-name ANONYMOUS --entity-type clients --entity-name cpu-hog
   ```

   ```
   Quota configs for user-principal 'ANONYMOUS', client-id 'cpu-hog' are request_percentage=5.0
   ```
4. Chạy lại (giảm `--num-records` vì sẽ rất chậm) và so throughput.

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic reqquota-lab --num-records 30000 --record-size 64 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=cpu-hog acks=all \
                      linger.ms=0 batch.size=1
   ```

   Throughput sụt mạnh, latency trung bình tăng — **vẫn không có exception nào**.
5. Đọc MBean `Request` (khác MBean `Produce` của Lab 3.4):

   ```bash
   docker exec -e JMX_PORT= -e KAFKA_OPTS= kafka-1 /opt/kafka/bin/kafka-run-class.sh \
     org.apache.kafka.tools.JmxTool \
     --jmx-url service:jmx:rmi:///jndi/rmi://kafka-1:9999/jmxrmi \
     --object-name 'kafka.server:type=Request,user=ANONYMOUS,client-id=cpu-hog' \
     --one-time
   ```

   ```
   kafka.server:type=Request,user=ANONYMOUS,client-id=cpu-hog:request-time=4.97
   kafka.server:type=Request,user=ANONYMOUS,client-id=cpu-hog:throttle-time=310.0
   ```

   `request-time` bám sát **5.0** = đúng `request_percentage=5`; `throttle-time` > 0 xác nhận đang bị kìm.
6. **Đối chứng**: bật lại batching cho chính client đó, giữ nguyên quota.

   ```bash
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic reqquota-lab --num-records 30000 --record-size 64 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 client.id=cpu-hog acks=all \
                      linger.ms=20 batch.size=65536
   ```

   Với cùng quota CPU, throughput **cao hơn hẳn** — vì cùng lượng dữ liệu đi trong **ít request hơn**. Đây là minh hoạ trực tiếp cho câu "batch/linger phía client đổi tải trên broker".

### ✅ Kiểm chứng

- Bước 1: đọc được `num.io.threads=8` và `num.network.threads=3` → tự tính được trần 1100%.
- Bước 4: throughput ở bước 4 thấp hơn nhiều so với bước 2, log broker vẫn **không** có exception.
- Bước 5: `request-time` ≈ 5, `throttle-time` > 0.
- Bước 6: cùng `request_percentage=5` nhưng throughput cao hơn bước 4 rõ rệt.

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type users --entity-name ANONYMOUS \
     --entity-type clients --entity-name cpu-hog --delete-config 'request_percentage'
kcfg --describe --entity-type users --entity-type clients     # phải rỗng
kt --delete --topic reqquota-lab

# Gỡ hẳn override JMX khi đã xong 3 lab cuối
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d kafka-1
export KAFKA_CTR=kafka-1
```

### 🧠 Ý nghĩa với đề thi

- `request_percentage=n` = **n% của MỘT thread**, không phải n% tổng CPU broker. Trần là `(num.io.threads + num.network.threads) × 100`%.
- Trong cluster multi-tenant, docs nói thẳng: **request rate quota thường hiệu quả hơn bandwidth quota**, vì CPU broker bị chiếm mới là thứ làm giảm băng thông thực tế phục vụ được.
- MBean khác nhau: **`kafka.server:type=Produce|Fetch`** cho bandwidth quota (`byte-rate` + `throttle-time`), **`kafka.server:type=Request`** cho request quota (`request-time` + `throttle-time`).
- Client gửi hàng vạn request bé (`linger.ms=0`, `batch.size` nhỏ) là thủ phạm phổ biến làm `RequestHandlerAvgIdlePercent` tụt dưới **0.3**. Admin không sửa được code client thì dùng **quota** để bảo vệ cluster.

---

> ✅ Xong 7 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist), rồi làm [bộ 30 câu luyện tập](questions.md) và **⭐ MINI-MOCK CFG (~30 câu trộn Tuần 2 + Tuần 3)**. Ngưỡng qua cổng sang Tuần 4: **≥70%**. Giữ lại `~/kafka-labs/docker-compose.w3-jmx.yml` — Tuần 7 (Observability) sẽ dùng lại đúng cơ chế JMX này.
