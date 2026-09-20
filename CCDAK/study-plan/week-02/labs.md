# 🧪 Hands-on Labs — Tuần 2: Độ tin cậy & lưu trữ: replication, retention, log compaction, delivery semantics

> Lab cầm tay chỉ việc, chạy hoàn toàn local bằng Docker (không tốn phí). LUÔN chạy phần Dọn dẹp cuối mỗi lab (trừ khi lab nói "giữ topic cho lab sau").
> ⚙️ Yêu cầu chung: Docker Desktop, Node.js 24, **cluster 3 node từ Tuần 1 (Lab 1.2)**. Tổng ~3.5h (Lab 2.3 và 2.4 có thời gian chờ — mở lab khác trong lúc chờ).
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab)

### 1) Khởi động cluster 3 broker + 1 controller

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d
docker compose -f docker-compose.cluster.yml ps          # controller, kafka-1, kafka-2, kafka-3 đều "running"
export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092          # cluster 3 node: lệnh CLI chạy trong kafka-1, listener nội bộ
```

> 📌 2 file compose chuẩn (`docker-compose.single.yml`, `docker-compose.cluster.yml`) được định nghĩa ở [Tuần 1 — Lab 1.1 / 1.2](../week-01/labs.md). Cluster này đã có `min.insync.replicas=2`, `default.replication.factor=3`, host port **9092 / 9094 / 9096** ↔ container `kafka-1 / kafka-2 / kafka-3` (node.id **2 / 3 / 4**; controller là node 1). Toàn bộ số liệu quan sát trong tuần dựa trên cấu hình này.

### 2) Alias CLI (đã định nghĩa ở Tuần 1 — chỉ nhắc lại)

```bash
# kt / kcp / kcc / kcg / kcfg / kq đã có trong ~/.zshrc từ Tuần 1. Kiểm tra:
kt --list
# Alias mới cho tuần này (kafka-get-offsets.sh dùng ở 4 lab):
alias koff='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_BS'
```

Tool chưa có alias (`kafka-log-dirs.sh`, `kafka-leader-election.sh`, `kafka-delete-records.sh`, `kafka-dump-log.sh`, `kafka-features.sh`, `kafka-share-groups.sh`, `kafka-console-share-consumer.sh`) viết dạng đầy đủ `docker exec -it $KAFKA_CTR /opt/kafka/bin/<tool>.sh --bootstrap-server $KAFKA_BS ...`.

> ⚠️ Khi **pipe stdin** vào console producer (`seq 1 20 | ...`), dùng `docker exec -i` (không `-t`), vì `-t` đòi TTY và sẽ báo `the input device is not a TTY`. Các lab bên dưới viết rõ dạng này khi cần.

### 3) Project Node.js cho tuần 2

```bash
mkdir -p ~/kafka-labs/week-02 && cd ~/kafka-labs/week-02
npm init -y >/dev/null && npm pkg set type=module && npm i kafkajs@2
```

File dùng chung `kafka.mjs`:

```javascript
// ~/kafka-labs/week-02/kafka.mjs — client dùng chung cho mọi lab tuần 2
import { Kafka, logLevel } from "kafkajs";

export const BROKERS = ["localhost:9092", "localhost:9094", "localhost:9096"]; // Java: bootstrap.servers

export const kafka = new Kafka({
  clientId: "week02-lab",                       // Java: client.id
  brokers: BROKERS,
  logLevel: logLevel.ERROR,
  retry: { initialRetryTime: 200, retries: 3 }, // retry ngắn để lỗi NotEnoughReplicas nổi lên nhanh (Java: retries / delivery.timeout.ms)
});

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
```

> 🧠 Nhắc 1 dòng: `kafkajs` không hỗ trợ share group và không có `max.request.size` phía client — Lab 2.5 / 2.6 dùng CLI Java cho các phần đó (client Node đầy đủ là `@confluentinc/kafka-javascript`, đã ghi chú ở Tuần 1).

---

## Lab 2.1 — `acks` × `min.insync.replicas`: tự tay tạo `NotEnoughReplicasException` ⭐

**🎯 Mục tiêu:** Topic RF=3, `min.insync.replicas=2`. Producer gửi song song `acks=all` và `acks=1`. Dừng `kafka-2` + `kafka-3` → `acks=all` FAIL với `NotEnoughReplicas`, `acks=1` vẫn `ok`; consumer vẫn đọc dữ liệu cũ nhưng **không thấy** record `acks=1` mới (high watermark không tiến); bật lại → mọi thứ hồi.
**🧩 Luyện kỹ năng (liên quan đề):**

- Ma trận `acks` × `min.insync.replicas` (Java `acks`, `min.insync.replicas` topic-level).
- `NotEnoughReplicasException` là lỗi **ghi**; **đọc** không bị chặn bởi min.isr.
- LEO vs HW: `acks=1` được ack với offset tăng, nhưng `koff --time -1` (HW) đứng yên khi ISR < min.isr ("strict min ISR").

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic 1 partition, **ép replica assignment `2:3:4`** để leader (preferred = replica đầu) là `kafka-1` — lab trở nên tất định.

   ```bash
   kt --create --topic lab21-acks --replica-assignment 2:3:4 --config min.insync.replicas=2
   kt --describe --topic lab21-acks
   # Topic: lab21-acks  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3,4  Elr:  LastKnownElr:
   ```
2. Viết `acks-probe.mjs` — mỗi giây gửi 1 record `acks=all` và 1 record `acks=1`, in `ok`/`FAIL` + offset (GIỮ file này cho Tuần 3).

   ```javascript
   // ~/kafka-labs/week-02/acks-probe.mjs — so sánh acks=all vs acks=1 khi ISR co lại
   import { kafka, sleep } from "./kafka.mjs";

   const topic = process.env.TOPIC ?? "lab21-acks";
   const producer = kafka.producer();        // kafkajs mặc định idempotent=false → acks=1 hợp lệ (Java: enable.idempotence=false)
   await producer.connect();

   let i = 0;
   while (true) {
     i++;
     for (const acks of [-1, 1]) {            // Java: acks=all (-1) và acks=1
       const label = acks === -1 ? "acks=all" : "acks=1  ";
       try {
         const [m] = await producer.send({
           topic,
           acks,                                // kafkajs: acks per-send
           messages: [{ key: `k-${i}`, value: `${label.trim()} msg-${i} ${new Date().toISOString()}` }],
         });
         console.log(`ok   ${label} msg-${i} -> offset ${m.baseOffset}`);
       } catch (e) {
         console.log(`FAIL ${label} msg-${i}: ${e.message}`);
       }
     }
     await sleep(1000);
   }
   ```
3. **Terminal 2** — consumer đọc từ đầu, in offset (giữ chạy suốt lab).

   ```bash
   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
   kcc --topic lab21-acks --from-beginning --property print.offset=true --property print.value=true
   ```
4. **Terminal 3** — chạy probe; xác nhận cả 2 dòng `ok`, offset tăng đều, terminal 2 nhận từng record.

   ```bash
   cd ~/kafka-labs/week-02 && node acks-probe.mjs
   ```
5. **Terminal 1** — dừng **2 follower**, chờ ~10 s, đọc lại metadata và HW.

   ```bash
   docker stop kafka-2 kafka-3
   sleep 10
   kt --describe --topic lab21-acks        # Leader: 2  Isr: 2   (có thể thấy Elr: 3 hoặc 4 — ISR đã tụt dưới min.isr)
   koff --topic lab21-acks --time -1       # lab21-acks:0:<HW>  → ghi lại con số này
   ```
   **Terminal 3:** dòng `acks=all` → `FAIL ... Messages are rejected since there are fewer in-sync replicas than required` (mã lỗi `NOT_ENOUGH_REPLICAS`, Java: `NotEnoughReplicasException`); dòng `acks=1` → vẫn `ok` với **offset tiếp tục tăng** (leader đã append = LEO tăng).
   **Terminal 2:** consumer **không nhận thêm** record nào — kể cả record `acks=1` vừa được ack — vì HW **không tiến** khi `|ISR| < min.insync.replicas`.
6. Chạy lại `koff --time -1` sau 20 s: **HW vẫn y nguyên** dù offset trong terminal 3 đã tăng ~20 → đây chính là khoảng cách **LEO > HW**.
7. Bật lại 2 broker, quan sát hồi phục.

   ```bash
   docker start kafka-2 kafka-3
   sleep 10
   kt --describe --topic lab21-acks        # Isr: 2,3,4 trở lại (follower fetch đuổi kịp → ISR expand)
   koff --topic lab21-acks --time -1       # HW nhảy lên bằng LEO
   ```
   **Terminal 3:** `acks=all` → `ok` ngay khi ISR ≥ 2. **Terminal 2:** consumer nhận **một loạt** record `acks=1` dồn lại (đã nằm trên leader từ lâu, giờ mới committed).

### ✅ Kiểm chứng

- Khi 2 broker dừng: `acks=all` FAIL `NotEnoughReplicas`, `acks=1` `ok`, `kt --describe` in `Isr: 2`.
- `koff --time -1` **đứng yên** trong lúc offset `acks=1` tăng → LEO ≠ HW; consumer im lặng nhưng **không lỗi**.
- Sau `docker start`: ISR đủ 3, HW nhảy vọt, consumer nhận backlog, cả 2 dòng `ok`.
- Không mất record `acks=all` nào đã được `ok` trước sự cố (so số `ok acks=all` với record trong terminal 2).

### 🧹 Dọn dẹp

```bash
# Ctrl+C terminal 2 và 3. GIỮ acks-probe.mjs (Tuần 3 dùng lại). GIỮ topic lab21-acks cho Lab 2.7 (xoá ở đó).
docker compose -f ~/kafka-labs/docker-compose.cluster.yml ps   # chắc chắn 4 container đang chạy trước khi sang Lab 2.2
```

### 🧠 Ý nghĩa với đề thi

- "RF=3, min.isr=2, acks=all, mất 2 broker" → **ghi dừng** (`NotEnoughReplicasException`, retriable), **đọc vẫn được**, **không mất dữ liệu committed**.
- `min.insync.replicas` **chỉ** có tác dụng với `acks=all`; `acks=1` phớt lờ nó — đề hay đặt bẫy "đã đặt min.isr=2 nhưng producer acks=1".
- Consumer chỉ đọc tới **high watermark**; HW = min LEO của ISR và **không tiến** khi ISR < min.isr — nền tảng cho ELR (KIP-966).
- Record `acks=1` được ack nhưng chưa committed: nếu leader chết lúc này → **mất record đã ack**.

---

## Lab 2.2 — ISR shrink/expand, high watermark, `offsetLag`

**🎯 Mục tiêu:** Đọc `Leader / Replicas / Isr / Elr` và `kafka-log-dirs.sh` (`size`, `offsetLag`) trước–trong–sau khi 1 follower "đứng hình" (`docker pause`); thấy ISR co trong ≤ 30 s, `acks=all` bị **khựng** rồi chạy tiếp khi ISR co, và follower tự vào lại ISR khi `offsetLag` về 0.
**🧩 Luyện kỹ năng (liên quan đề):**

- `replica.lag.time.max.ms` = 30 000 ms — ISR theo **thời gian**, không theo số message.
- `kafka-get-offsets.sh --time -1` = latest (= **HW**, offset consumer sẽ nhận kế tiếp), `--time -2` = earliest (log start offset).
- ELR chỉ xuất hiện khi ISR **tụt dưới** min.isr (ở lab này ISR còn 2 = min.isr → `Elr:` trống).

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 2.1 xong, 4 container đang chạy.

### Các bước

1. Tạo topic, leader `kafka-1` (node 2), follower `kafka-2` (3) và `kafka-3` (4).

   ```bash
   kt --create --topic lab22-isr --replica-assignment 2:3:4
   kt --describe --topic lab22-isr           # Leader: 2  Replicas: 2,3,4  Isr: 2,3,4
   ```
2. Ghi 1 000 record, đọc earliest / latest.

   ```bash
   seq 1 1000 | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS --topic lab22-isr
   koff --topic lab22-isr --time -2          # lab22-isr:0:0     (earliest = log start offset)
   koff --topic lab22-isr --time -1          # lab22-isr:0:1000  (latest = HW; LEO của leader cũng = 1000 vì mọi replica đã đồng bộ)
   ```
3. Xem `size` / `offsetLag` từng replica bằng `kafka-log-dirs.sh` (output JSON 1 dòng → grep gọn).

   ```bash
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-log-dirs.sh --bootstrap-server $KAFKA_BS \
     --describe --topic-list lab22-isr | tail -1 | grep -oE '"broker":[0-9]+|"partition":"lab22-isr-0","size":[0-9]+,"offsetLag":[0-9]+'
   # "broker":2 ... "offsetLag":0   "broker":3 ... "offsetLag":0   "broker":4 ... "offsetLag":0
   ```
4. **Đóng băng** follower `kafka-3` (process dừng nhưng container còn) rồi bơm 100 000 record × 1 KB với `acks=all`.

   ```bash
   docker pause kafka-3
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh --topic lab22-isr \
     --num-records 100000 --record-size 1000 --throughput -1 \
     --producer-props bootstrap.servers=$KAFKA_BS acks=all
   ```
   Quan sát: vài giây đầu perf-test **khựng** (leader chờ replica 4 đang trong ISR ack) rồi **bùng lên** khi replica 4 bị loại — `acks=all` chỉ chờ **ISR hiện tại**, và ISR = {2,3} = 2 ≥ min.isr nên ghi tiếp bình thường.
5. Xem ISR đã co.

   ```bash
   kt --describe --topic lab22-isr           # Isr: 2,3   Elr: (trống — ISR vẫn ≥ min.isr)
   koff --topic lab22-isr --time -1          # 101000
   ```
   > 📌 Broker bị `pause` rời ISR bằng **2 con đường** song song: (a) controller không nhận heartbeat → **fence** sau `broker.session.timeout.ms` = 9 s; (b) leader không thấy fetch đuổi kịp LEO trong `replica.lag.time.max.ms` = 30 s → shrink. Đề thi hỏi con đường (b) — con số **30 s**. Một follower **sống nhưng chậm** (đĩa/net nghẽn) chỉ đi con đường (b).
6. Thả `kafka-3`, theo dõi `offsetLag` giảm về 0 và ISR nở lại (chạy vòng lặp ngay lập tức).

   ```bash
   docker unpause kafka-3
   for i in 1 2 3 4 5 6; do
     docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-log-dirs.sh --bootstrap-server $KAFKA_BS \
       --describe --topic-list lab22-isr | tail -1 | grep -oE '"broker":4|"partition":"lab22-isr-0","size":[0-9]+,"offsetLag":[0-9]+' | tail -2 | tr '\n' ' '; echo
     sleep 2
   done
   kt --describe --topic lab22-isr           # Isr: 2,3,4 (expand — không cần lệnh nào)
   ```
   Nếu đuổi kịp quá nhanh không thấy `offsetLag > 0`, tăng `--num-records 300000` ở bước 4.
7. (Tuỳ chọn) Ép leader về preferred nếu bạn dừng nhầm leader ở lab nào đó: `kafka-leader-election.sh --election-type PREFERRED --all-topic-partitions` (Tuần 1 Lab 1.6 đã làm).

### ✅ Kiểm chứng

- Bước 4–5: sau khi pause, `Isr` mất node 4 trong ≤ 30 s; perf-test khựng rồi chạy tiếp; latest = 101 000.
- Bước 6: broker 4 có `offsetLag` > 0 rồi về 0; `Isr: 2,3,4` tự trở lại — **ISR expand không cần thao tác**.
- `Elr:` trống suốt lab (ISR chưa bao giờ < 2). So với Lab 2.1 bước 5 khi ISR = 1 < 2 thì `Elr:` có giá trị.

### 🧹 Dọn dẹp

```bash
kt --delete --topic lab22-isr
docker ps --format '{{.Names}} {{.Status}}' | grep kafka     # 3 broker "Up", không còn "(Paused)"
```

### 🧠 Ý nghĩa với đề thi

- "Follower tụt N message thì bị loại ISR" → **sai**; chỉ có ngưỡng thời gian `replica.lag.time.max.ms` (30 000 ms).
- `acks=all` = chờ **ISR hiện tại**, nên khi ISR co lại thì latency giảm — đổi lại độ bền chỉ còn bằng số replica trong ISR.
- ISR co/giãn **tự động**; không có lệnh "thêm lại follower vào ISR".
- `kafka-log-dirs.sh` là tool xem `offsetLag` từng replica; `kafka-get-offsets.sh` xem earliest/latest — cả hai hay xuất hiện ở đề OPS.

---

## Lab 2.3 — Retention nhanh: segment roll, `.deleted`, và bẫy "data quá hạn vẫn còn"

**🎯 Mục tiêu:** Topic A `retention.ms=60000 segment.ms=10000` → thấy segment roll theo thời gian, lần quét 5 phút xoá segment quá hạn, earliest offset (`--time -2`) dời lên. Topic B chỉ `retention.ms=60000` (segment.ms mặc định 7 ngày) + ghi lai rai → **record quá hạn vẫn còn** vì nằm trong active segment. So với `kafka-delete-records.sh` dời log start offset ngay lập tức.
**🧩 Luyện kỹ năng (liên quan đề):**

- Retention làm việc **theo segment**: xoá segment khi record **mới nhất** trong đó quá `retention.ms`; quét mỗi `log.retention.check.interval.ms` = 300 000 ms.
- `segment.ms` / `segment.bytes` quyết định khi nào segment **đóng** → quyết định retention "đúng hạn" tới đâu.
- `file.delete.delay.ms` = 60 000: file đổi tên `.deleted` rồi mới xoá thật.

**⏱️ ~35 phút (trong đó ~6 phút chờ — làm song song Lab 2.4)** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo 2 topic.

   ```bash
   kt --create --topic lab23-ret   --partitions 1 --replication-factor 3 --config retention.ms=60000 --config segment.ms=10000
   kt --create --topic lab23-ret-b --partitions 1 --replication-factor 3 --config retention.ms=60000
   kcfg --describe --entity-type topics --entity-name lab23-ret     # thấy retention.ms=60000, segment.ms=10000
   ```
2. Topic A: ghi 3 đợt cách nhau > 10 s để **ép roll** (roll xảy ra ở lần **append kế tiếp** sau khi segment đã quá `segment.ms`).

   ```bash
   P="docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS"
   seq 1 10  | $P --topic lab23-ret ; sleep 12
   seq 11 20 | $P --topic lab23-ret ; sleep 12
   seq 21 30 | $P --topic lab23-ret
   docker exec $KAFKA_CTR ls -l /tmp/kraft-combined-logs/lab23-ret-0/ | grep -E '\.log$'
   # 00000000000000000000.log   00000000000000000010.log   00000000000000000020.log  (segment 20 là active)
   koff --topic lab23-ret --time -2      # lab23-ret:0:0
   ```
3. Topic B: ghi đợt đầu, rồi chạy **trickle** 1 record / 20 s trong ~6 phút (terminal 2) để active segment luôn có record "trẻ".

   ```bash
   seq 1 10 | $P --topic lab23-ret-b
   cat > ~/kafka-labs/week-02/trickle.mjs <<'EOF'
   // trickle.mjs — 1 record mỗi 20 s vào topic (mặc định lab23-ret-b)
   import { kafka, sleep } from "./kafka.mjs";
   const topic = process.argv[2] ?? "lab23-ret-b";
   const producer = kafka.producer();
   await producer.connect();
   for (let i = 1; i <= 20; i++) {
     await producer.send({ topic, messages: [{ value: `trickle-${i} ${new Date().toISOString()}` }] });
     console.log(`sent trickle-${i}`);
     await sleep(20000);
   }
   await producer.disconnect();
   EOF
   # Terminal 2:
   cd ~/kafka-labs/week-02 && node trickle.mjs
   ```
4. **Chờ lần quét retention** (tối đa 5 phút — `log.retention.check.interval.ms` là config **read-only**, không hạ được lúc chạy; trong lúc chờ làm Lab 2.4). Theo dõi earliest offset của cả 2 topic mỗi 30 s.

   ```bash
   for i in $(seq 1 12); do date +%T; koff --topic lab23-ret --time -2; koff --topic lab23-ret-b --time -2; sleep 30; done
   ```
   Kết quả mong đợi sau lần quét đầu (khi mọi record đã > 60 s):
   - **Topic A:** earliest nhảy thẳng lên **30** (= latest). Cả 3 segment đều có record mới nhất quá hạn → Kafka **roll một segment rỗng mới** (`00000000000000000030.log`) rồi xoá cả 3 — kể cả segment 20 vốn đang active. Xem thư mục: file cũ mang hậu tố `.deleted` trong 60 s (`file.delete.delay.ms`) rồi biến mất.
   - **Topic B:** earliest **vẫn là 0** dù 10 record đầu đã 5–6 phút tuổi > 60 s: chúng nằm chung active segment với record `trickle-N` vừa ghi; segment được xét theo record **mới nhất** → không đủ điều kiện.

   ```bash
   docker exec $KAFKA_CTR ls -l /tmp/kraft-combined-logs/lab23-ret-0/      # .deleted rồi chỉ còn 00000000000000000030.*
   docker exec $KAFKA_CTR ls -l /tmp/kraft-combined-logs/lab23-ret-b-0/    # vẫn 1 segment 00000000000000000000.log
   ```
5. Xoá **chủ động** trên topic B bằng `kafka-delete-records.sh` — dời log start offset tới 10 **ngay lập tức**, không chờ retention, không cần segment đóng.

   ```bash
   docker exec -i $KAFKA_CTR sh -c 'cat > /tmp/del.json' <<'EOF'
   {"partitions":[{"topic":"lab23-ret-b","partition":0,"offset":10}],"version":1}
   EOF
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-delete-records.sh --bootstrap-server $KAFKA_BS --offset-json-file /tmp/del.json
   koff --topic lab23-ret-b --time -2      # lab23-ret-b:0:10
   kcc --topic lab23-ret-b --from-beginning --timeout-ms 5000 | head -3    # bắt đầu từ trickle-1, không còn 1..10
   ```
6. (Tuỳ chọn) Muốn topic B xoá đúng hạn: `kcfg --alter --entity-type topics --entity-name lab23-ret-b --add-config segment.ms=10000` — đúng cách sửa "retention 1 giờ mà data 2 ngày vẫn còn".

### ✅ Kiểm chứng

- Topic A có 3 file `.log` sau bước 2; sau lần quét earliest = 30 và thư mục chỉ còn segment `...30.*`.
- Topic B earliest = 0 suốt thời gian trickle chạy, dù record đầu đã quá hạn nhiều lần.
- `kafka-delete-records.sh` dời earliest lên 10 **tức thì**; consumer `--from-beginning` bắt đầu từ offset 10.

### 🧹 Dọn dẹp

```bash
# Ctrl+C terminal 2 (trickle) nếu còn chạy
kt --delete --topic lab23-ret
kt --delete --topic lab23-ret-b
rm -f ~/kafka-labs/week-02/trickle.mjs
```

### 🧠 Ý nghĩa với đề thi

- "Retention 1 giờ nhưng data 2 ngày vẫn đọc được" → segment chưa đủ điều kiện xoá (xét theo record **mới nhất**; active segment còn nhận ghi thì mãi "trẻ") + quét mỗi **5 phút** → hạ `segment.ms`/`segment.bytes`, hoặc `kafka-delete-records.sh`.
- Câu "active segment không bao giờ bị xoá" trong tài liệu/đề là **cách nói gọn**: chính xác là "segment chỉ bị xoá khi toàn bộ record trong nó quá hạn"; topic ngừng ghi hẳn thì Kafka roll segment rỗng rồi xoá cả active segment cũ (bạn vừa thấy ở topic A). Với đề thi, chọn đáp án nói về **segment chưa roll / hạ `segment.ms`**.
- `retention.ms` là **SLA cho consumer** ("how soon consumers must read their data"); `retention.bytes` tính **per partition**; `-1` = không giới hạn.
- Xoá theo **offset** = `kafka-delete-records.sh`; xoá theo **key** = tombstone trong compacted topic (Lab 2.4).

---

## Lab 2.4 — Log compaction bằng `kafkajs`: giữ giá trị cuối theo key + tombstone ⭐

**🎯 Mục tiêu:** Topic `cleanup.policy=compact` với `segment.ms=5000`, `min.cleanable.dirty.ratio=0.01`, `delete.retention.ms=10000`. Gửi `user-1` 5 lần, `user-2` 2 lần + **tombstone** (`value: null`), `user-3` 1 lần; ép roll; đọc `--from-beginning` **trước** và **sau** khi cleaner chạy: chỉ còn giá trị cuối, **offset giữ nguyên có lỗ**, tombstone biến mất sau lần dọn thứ hai.
**🧩 Luyện kỹ năng (liên quan đề):**

- Tombstone = key + value **`null`** (không phải `""`); sống `delete.retention.ms` (mặc định 24 h).
- Cleaner chỉ dọn **segment đã đóng** và chỉ khi dirty ratio ≥ `min.cleanable.dirty.ratio` (mặc định 0.5).
- 4 đảm bảo của compaction: thứ tự, offset không đổi, thấy mọi message nếu bám head, đọc từ đầu thấy ít nhất giá trị cuối mỗi key.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung (có thể chạy trong lúc chờ Lab 2.3).

### Các bước

1. Tạo topic compact với các ngưỡng "lab" (production giữ mặc định: 0.5 / 24 h / 7 ngày).

   ```bash
   kt --create --topic lab24-compact --partitions 1 --replication-factor 3 \
     --config cleanup.policy=compact --config segment.ms=5000 \
     --config min.cleanable.dirty.ratio=0.01 --config delete.retention.ms=10000
   kcfg --describe --entity-type topics --entity-name lab24-compact
   ```
2. Viết `compaction.mjs` (GIỮ file này cho Tuần 3) — 2 pha: `seed` gửi dữ liệu + tombstone rồi ép roll; `roll` gửi 2 record cách 6 s để đóng thêm 1 segment (kích cleaner chạy lần nữa).

   ```javascript
   // ~/kafka-labs/week-02/compaction.mjs — node compaction.mjs seed | roll
   import { kafka, sleep } from "./kafka.mjs";

   const topic = "lab24-compact";
   const phase = process.argv[2] ?? "seed";
   const producer = kafka.producer();
   await producer.connect();

   const send = async (key, value) => {
     const [m] = await producer.send({ topic, messages: [{ key, value }] }); // value: null → tombstone (Java: new ProducerRecord<>(topic, key, null))
     console.log(`offset ${String(m.baseOffset).padStart(2)}  key=${key}  value=${value === null ? "<TOMBSTONE null>" : value}`);
   };

   if (phase === "seed") {
     for (let v = 1; v <= 5; v++) await send("user-1", `user-1 v${v}`);   // offset 0..4
     await send("user-2", "user-2 v1");                                     // 5
     await send("user-2", "user-2 v2");                                     // 6
     await send("user-3", "user-3 v1");                                     // 7
     await send("user-2", null);                                            // 8  ← tombstone xoá user-2
     await sleep(6000);                                                     // > segment.ms=5000
     await send("user-9", "roll-1");                                        // 9  ← append này ép ROLL: segment 0..8 đóng, dirty 100%
     console.log("Segment 0..8 đã đóng. Cleaner sẽ chạy trong ~15 s (log.cleaner.backoff.ms).");
   } else {
     await send("user-9", "roll-2");                                        // vào segment active hiện tại
     await sleep(6000);
     await send("user-9", "roll-3");                                        // ép roll lần nữa → cleaner dọn lần 2
   }
   await producer.disconnect();
   ```
3. Chạy pha `seed`, **ngay lập tức** đọc từ đầu (trước khi cleaner chạy).

   ```bash
   cd ~/kafka-labs/week-02 && node compaction.mjs seed
   kcc --topic lab24-compact --from-beginning --timeout-ms 5000 \
     --property print.key=true --property print.offset=true --property key.separator=' | '
   # Offset:0 | user-1 | user-1 v1 ... Offset:8 | user-2 | null   Offset:9 | user-9 | roll-1   (đủ 10 dòng)
   ```
4. Chờ ~20–30 s, xem log cleaner đã chạy trên leader, đọc lại từ đầu.

   ```bash
   docker logs kafka-1 2>&1 | grep -E "cleaned log lab24-compact|Beginning cleaning of log lab24-compact" | tail -2
   kcc --topic lab24-compact --from-beginning --timeout-ms 5000 \
     --property print.key=true --property print.offset=true --property key.separator=' | '
   # Offset:4 | user-1 | user-1 v5
   # Offset:7 | user-3 | user-3 v1
   # Offset:8 | user-2 | null          ← tombstone còn (chưa quá delete.retention.ms kể từ lần dọn đầu)
   # Offset:9 | user-9 | roll-1        ← active segment, không bị dọn
   ```
   Nhận xét: **thứ tự** không đổi, **offset giữ nguyên** (0–3, 5–6 thành "lỗ"), mỗi key chỉ còn **giá trị cuối**.
   > 📌 Mỗi replica **tự compact bản của mình** (cleaner chạy trên cả 3 broker, thời điểm hơi khác nhau); consumer đọc từ leader nên hãy `grep` log của broker đang là leader (`kt --describe`).
5. Chờ **> 10 s** (`delete.retention.ms`) rồi chạy pha `roll` để tạo segment đóng mới → cleaner dọn lần 2 → tombstone bị gỡ.

   ```bash
   sleep 12
   node compaction.mjs roll
   sleep 25
   kcc --topic lab24-compact --from-beginning --timeout-ms 5000 \
     --property print.key=true --property print.offset=true --property key.separator=' | '
   # Offset:4  | user-1 | user-1 v5
   # Offset:7  | user-3 | user-3 v1
   # Offset:10 | user-9 | roll-2        ← roll-1 (9) bị dọn vì có bản mới hơn cùng key
   # Offset:11 | user-9 | roll-3        ← active segment
   #   → user-2 biến mất hoàn toàn (tombstone đã quá delete.retention.ms)
   ```
6. Soi đĩa để thấy segment sau compaction: file `.log` đầu đã được thay bằng bản dọn (kích cỡ nhỏ hơn), offset đầu file vẫn là `00000000000000000000`.

   ```bash
   docker exec $KAFKA_CTR ls -l /tmp/kraft-combined-logs/lab24-compact-0/ | grep -E '\.log$'
   docker exec $KAFKA_CTR /opt/kafka/bin/kafka-dump-log.sh --print-data-log \
     --files /tmp/kraft-combined-logs/lab24-compact-0/00000000000000000000.log | grep -E 'offset:' | head
   ```
7. Thử gửi record **không key** vào compacted topic → broker từ chối.

   ```bash
   echo "no-key" | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS --topic lab24-compact
   # ERROR ... InvalidRecordException: ... Compacted topic cannot accept message without key
   ```

### ✅ Kiểm chứng

- Bước 3 thấy đủ 10 offset; bước 4 chỉ còn offset **4, 7, 8, 9** (tombstone `user-2 | null` còn); bước 5 còn **4, 7, 10, 11** — `user-2` biến mất.
- Offset **không bao giờ đổi** và thứ tự giữ nguyên; record trong active segment (`roll-1` rồi `roll-3`) luôn còn nguyên.
- Record không key bị `InvalidRecordException`.

### 🧹 Dọn dẹp

```bash
kt --delete --topic lab24-compact
# GIỮ compaction.mjs và acks-probe.mjs cho Tuần 3
```

### 🧠 Ý nghĩa với đề thi

- "Chỉ cần trạng thái mới nhất mỗi key / changelog / CDC / `__consumer_offsets`" → `cleanup.policy=compact`; "xoá key" → **tombstone** `null`, sống `delete.retention.ms` = **24 h**.
- Compaction **không** đảm bảo "đúng 1 record/key" mọi lúc — head (active segment) còn trùng; đảm bảo là "**ít nhất** giá trị cuối".
- Cleaner chỉ chạy khi dirty ≥ `min.cleanable.dirty.ratio` (**0.5**) và chỉ trên segment **đã đóng** → topic ít dữ liệu cần hạ `segment.ms`; "compaction quá thưa" → hạ dirty ratio; "consumer cần thấy mọi bản trong X phút" → `min.compaction.lag.ms`.
- Compacted topic **bắt buộc có key**; `compact,delete` kết hợp được với `retention.ms` (state có TTL).

---

## Lab 2.5 — `RecordTooLargeException`: lỗi ở client vs ở broker, sửa đúng chỗ

**🎯 Mục tiêu:** Gửi record 2 MB: (a) console producer Java lỗi **ở client** (`max.request.size`); (b) `kafkajs` (không có giới hạn client) lỗi **ở broker** (`MESSAGE_TOO_LARGE`); sửa `max.message.bytes` topic bằng `kcfg --alter` + `max.request.size` phía Java → thành công; consumer mặc định vẫn đọc được (KIP-74); cuối cùng thấy **nén** giải quyết mà không cần đổi config.
**🧩 Luyện kỹ năng (liên quan đề):**

- Chuỗi 4 giới hạn: producer `max.request.size` (1 048 576) → topic `max.message.bytes` / broker `message.max.bytes` (1 048 588) → follower `replica.fetch.max.bytes` → consumer `max.partition.fetch.bytes`.
- Phân biệt thông điệp lỗi client (`...larger than 1048576, which is the value of the max.request.size configuration`) và broker (`...larger than the max message size the server will accept`).
- `message.max.bytes` tính **sau nén**.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic và file 2 MB trong container.

   ```bash
   kt --create --topic lab25-big --partitions 1 --replication-factor 3
   docker exec -it $KAFKA_CTR sh -c "head -c 2000000 /dev/zero | tr '\0' a > /tmp/big.txt; wc -c /tmp/big.txt"
   ```
2. **Lỗi ở client (Java):** console producer mặc định `max.request.size=1048576` → `RecordTooLargeException` **trước khi gửi**.

   ```bash
   docker exec -it $KAFKA_CTR sh -c "/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS --topic lab25-big < /tmp/big.txt"
   # ERROR ... RecordTooLargeException: The message is 2000088 bytes when serialized which is larger than 1048576,
   #   which is the value of the max.request.size configuration.
   ```
3. **Lỗi ở broker (Java):** nới client lên 3 MB nhưng topic vẫn 1 048 588 → broker trả `MESSAGE_TOO_LARGE`.

   ```bash
   docker exec -it $KAFKA_CTR sh -c "/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS --topic lab25-big \
     --producer-property max.request.size=3000000 < /tmp/big.txt"
   # ERROR ... RecordTooLargeException: The request included a message larger than the max message size the server will accept.
   ```
4. **Lỗi ở broker (kafkajs):** viết `big-record.mjs` — `kafkajs` **không có** `max.request.size` nên gửi thẳng, broker từ chối.

   ```javascript
   // ~/kafka-labs/week-02/big-record.mjs — node big-record.mjs <MB> [gzip]
   import { CompressionTypes } from "kafkajs";
   import { kafka } from "./kafka.mjs";

   const mb = Number(process.argv[2] ?? 2);
   const gzip = process.argv[3] === "gzip";
   const topic = "lab25-big";
   const producer = kafka.producer();
   await producer.connect();
   try {
     const [m] = await producer.send({
       topic,
       compression: gzip ? CompressionTypes.GZIP : CompressionTypes.None, // Java: compression.type=gzip
       messages: [{ key: "big", value: Buffer.alloc(mb * 1024 * 1024, "a") }],
     });
     console.log(`ok: ${mb} MB${gzip ? " (gzip)" : ""} -> partition ${m.partition} offset ${m.baseOffset}`);
   } catch (e) {
     console.log(`FAIL: ${e.type ?? e.name} — ${e.message}`);           // type: MESSAGE_TOO_LARGE, retriable=false
   }
   await producer.disconnect();
   ```

   ```bash
   cd ~/kafka-labs/week-02 && node big-record.mjs 2
   # FAIL: MESSAGE_TOO_LARGE — The request included a message larger than the max message size the server will accept
   ```
5. **Sửa đúng chỗ:** nới `max.message.bytes` ở **topic** (dynamic, không restart) rồi gửi lại cả 2 client.

   ```bash
   kcfg --alter --entity-type topics --entity-name lab25-big --add-config max.message.bytes=3000000
   kcfg --describe --entity-type topics --entity-name lab25-big        # max.message.bytes=3000000 ... DYNAMIC_TOPIC_CONFIG
   node big-record.mjs 2                                                # ok: 2 MB -> offset 0
   docker exec -it $KAFKA_CTR sh -c "/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS --topic lab25-big \
     --producer-property max.request.size=3000000 < /tmp/big.txt" && echo JAVA-OK   # offset 1
   koff --topic lab25-big --time -1                                     # lab25-big:0:2
   ```
   > 📌 `kafka-topics.sh --alter --config ...` **không** dùng được với `--bootstrap-server` — đổi config topic phải qua `kafka-configs.sh` (Lab 2.7).
6. Consumer mặc định (`max.partition.fetch.bytes`=1 048 576) vẫn nhận được record 2 MB, follower vẫn replicate (KIP-74: batch đầu luôn được trả dù vượt giới hạn).

   ```bash
   kcc --topic lab25-big --from-beginning --max-messages 1 --timeout-ms 10000 | wc -c   # ≈ 2 097 153 byte
   kt --describe --topic lab25-big                                                        # Isr: đủ 3 → replication không kẹt
   ```
7. **Cách tốt hơn — nén:** đưa topic về mặc định rồi gửi 2 MB **gzip** → 2 MB toàn chữ `a` nén còn vài KB → qua được giới hạn 1 048 588 **mà không đổi config** (`message.max.bytes` tính sau nén).

   ```bash
   kcfg --alter --entity-type topics --entity-name lab25-big --delete-config max.message.bytes
   node big-record.mjs 2            # FAIL lại (không nén)
   node big-record.mjs 2 gzip       # ok: 2 MB (gzip) -> offset 2
   ```

### ✅ Kiểm chứng

- Bước 2 và 3 in **2 thông điệp khác nhau** của cùng `RecordTooLargeException` (client: nhắc `max.request.size`; broker: "the server will accept").
- Bước 5: sau `kcfg --alter` cả `kafkajs` và Java gửi thành công; latest = 2.
- Bước 6: consumer đọc được ~2 MB dù `max.partition.fetch.bytes` mặc định 1 MiB; ISR đủ 3.
- Bước 7: gzip qua được giới hạn mặc định.

### 🧹 Dọn dẹp

```bash
kt --delete --topic lab25-big
docker exec $KAFKA_CTR rm -f /tmp/big.txt
rm -f ~/kafka-labs/week-02/big-record.mjs
```

### 🧠 Ý nghĩa với đề thi

- `RecordTooLargeException` → phải sửa **cả** `max.request.size` (producer) **và** `max.message.bytes` (topic) / `message.max.bytes` (broker); chỉ sửa 1 bên là còn lỗi.
- Consumer / follower **không kẹt** nhờ KIP-74 nhưng nên nâng `max.partition.fetch.bytes` / `replica.fetch.max.bytes` cho throughput.
- Đề hỏi "cách tốt nhất gửi payload lớn" → **nén** (`compression.type`) hoặc **claim-check** (đẩy file lên object storage, gửi URL) — không phải nâng giới hạn lên 50 MB.
- Topic `compression.type=producer` (mặc định) → broker giữ codec gzip bạn gửi, không nén lại.

---

## Lab 2.6 — Share group (Queues for Kafka, KIP-932): 2 consumer chia nhau **1 partition**

**🎯 Mục tiêu:** 2 `kafka-console-share-consumer.sh` cùng group trên topic **1 partition** **cùng nhận** message; `kafka-share-groups.sh --describe` (cột `START-OFFSET` / `LAG`), `--members` (2 member cùng `lab26-queue:0`); so với consumer group cùng cấu hình → 1 consumer idle.
**🧩 Luyện kỹ năng (liên quan đề):**

- Nhận diện khi nào chọn share group thay consumer group (queue, consumer > partition, ack từng record, không cần thứ tự).
- Feature flag `share.version=1`; tool `kafka-share-groups.sh`; state ở `__share_group_state`.
- 3 loại acknowledge ACCEPT / RELEASE / REJECT; lock 30 s; delivery count limit 5.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung. Cần **3 terminal**.

### Các bước

1. Kiểm tra feature `share.version` (cluster mới 4.3.1 thường đã `FinalizedVersionLevel: 1`; nếu là `0` thì bật).

   ```bash
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-features.sh --bootstrap-server $KAFKA_BS describe | grep share.version
   # Feature: share.version  SupportedMinVersion: 0  SupportedMaxVersion: 1  FinalizedVersionLevel: 1 ...
   # Nếu FinalizedVersionLevel: 0 →
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-features.sh --bootstrap-server $KAFKA_BS upgrade --feature share.version=1
   ```
2. Tạo topic **1 partition**.

   ```bash
   kt --create --topic lab26-queue --partitions 1 --replication-factor 3
   ```
3. **Terminal 2 và 3** — mỗi terminal 1 share consumer, **cùng group** `lab26-share` (implicit ack: `poll()` kế = ACCEPT cả batch trước).

   ```bash
   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-console-share-consumer.sh --bootstrap-server $KAFKA_BS \
     --topic lab26-queue --group lab26-share
   ```
4. **Terminal 1** — bơm 20 message rồi nhìn 2 terminal kia.

   ```bash
   seq 1 20 | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS --topic lab26-queue
   ```
   Cả **2** terminal đều in message (chia theo lô record được acquire, ví dụ T2: 1–10, T3: 11–20; không phải round-robin từng record, và **không đảm bảo thứ tự** giữa 2 consumer). Bơm thêm vài lần để thấy phân phối đổi.
5. Mô tả share group.

   ```bash
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-share-groups.sh --bootstrap-server $KAFKA_BS --list
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-share-groups.sh --bootstrap-server $KAFKA_BS --describe --group lab26-share
   # GROUP        TOPIC        PARTITION  START-OFFSET  LAG
   # lab26-share  lab26-queue  0          20            0        ← START-OFFSET = offset sớm nhất còn in-flight; KHÔNG có CURRENT-OFFSET
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-share-groups.sh --bootstrap-server $KAFKA_BS --describe --group lab26-share --members
   # 2 dòng member, cùng ASSIGNMENT lab26-queue:0                 ← 1 partition gán cho 2 consumer
   docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-share-groups.sh --bootstrap-server $KAFKA_BS --describe --group lab26-share --state
   # STATE Stable
   kt --list | grep share                                          # __share_group_state (50 partition, RF 3)
   ```
6. **Đối chứng với consumer group:** Ctrl+C 2 share consumer; chạy 2 `kcc` cùng group ở terminal 2 và 3, rồi bơm 10 message.

   ```bash
   # Terminal 2 và 3:
   kcc --topic lab26-queue --group lab26-cg
   # Terminal 1:
   seq 21 30 | docker exec -i $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS --topic lab26-queue
   kcg --describe --group lab26-cg --members --verbose    # 1 member giữ lab26-queue:0, member kia ASSIGNMENT trống (idle)
   ```
   Chỉ **1** terminal nhận message: 1 partition → **đúng 1** consumer trong group.
7. Đọc lại bảng so sánh trong [README §9](README.md) và ghi vào sổ: lock `share.record.lock.duration.ms` = **30 s**, `share.delivery.count.limit` = **5**, ack `ACCEPT` / `RELEASE` / `REJECT`, mode `implicit` / `explicit`. (`kafkajs` không có share consumer; API `KafkaShareConsumer` Java / `@confluentinc/kafka-javascript`.)

### ✅ Kiểm chứng

- Bước 4: **cả 2** share consumer đều in message từ **1** partition.
- `--describe` in `START-OFFSET` / `LAG` (không có `CURRENT-OFFSET`); `--members` in 2 member cùng `lab26-queue:0`.
- Bước 6: với consumer group chỉ 1 terminal nhận; `kcg --describe --members --verbose` cho thấy 1 member không có partition.

### 🧹 Dọn dẹp

```bash
# Ctrl+C mọi consumer ở terminal 2, 3 trước (group phải rỗng mới xoá được)
docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-share-groups.sh --bootstrap-server $KAFKA_BS --delete --group lab26-share
kcg --delete --group lab26-cg
kt --delete --topic lab26-queue
```

### 🧠 Ý nghĩa với đề thi

- "Cần nhiều consumer hơn partition, ack từng message, kiểu queue (SQS/RabbitMQ), không cần thứ tự" → **share group** (KIP-932, GA **4.2**), không phải "tăng partition".
- Share group **mất thứ tự**, ack theo **record** (không commit offset), state ở **`__share_group_state`**, tool **`kafka-share-groups.sh`** / **`kafka-console-share-consumer.sh`**.
- Record lỗi tạm → `RELEASE` (hoặc để lock 30 s hết hạn); record độc → `REJECT`; quá **5** lần giao → archive.
- Consumer group vẫn là lựa chọn khi cần **thứ tự theo key**, replay, hoặc Kafka Streams.

---

## Lab 2.7 — `kafka-configs.sh`: config động topic / broker / cluster-default, `--describe --all`

**🎯 Mục tiêu:** Alter config **topic** và **broker** lúc chạy, đọc `--describe --all` để phân biệt nguồn giá trị (`DYNAMIC_TOPIC_CONFIG` / `DYNAMIC_BROKER_CONFIG` / `DYNAMIC_DEFAULT_BROKER_CONFIG` / `STATIC_BROKER_CONFIG` / `DEFAULT_CONFIG`), thử sửa config **read-only** bị từ chối, và thấy ràng buộc ELR với `min.insync.replicas` ở broker-level.
**🧩 Luyện kỹ năng (liên quan đề):**

- Thứ tự ưu tiên: topic dynamic > broker dynamic > cluster-default dynamic > static (`server.properties`) > default.
- Cặp tên topic ↔ broker: `retention.ms` ↔ `log.retention.ms`, `max.message.bytes` ↔ `message.max.bytes`, `segment.ms` ↔ `log.roll.ms`, `min.insync.replicas` ↔ `min.insync.replicas`.
- Config broker có 3 chế độ update: `read-only` (restart), `per-broker`, `cluster-wide`.

**⏱️ ~20 phút** · **Yêu cầu trước:** Lab 2.1 (topic `lab21-acks` còn) hoặc tạo topic mới ở bước 1.

### Các bước

1. Đọc config topic với `--all`: giá trị hiệu lực + **synonyms** cho biết nó đến từ tầng nào.

   ```bash
   kt --create --topic lab27-cfg --partitions 1 --replication-factor 3 --config retention.ms=3600000 2>/dev/null
   kcfg --describe --entity-type topics --entity-name lab27-cfg --all \
     | grep -E "^\s+(retention.ms|min.insync.replicas|segment.ms|max.message.bytes|compression.type|cleanup.policy)="
   #  retention.ms=3600000        synonyms={DYNAMIC_TOPIC_CONFIG:retention.ms=3600000, DEFAULT_CONFIG:log.retention.hours=168}
   #  min.insync.replicas=2       synonyms={STATIC_BROKER_CONFIG:min.insync.replicas=2, DEFAULT_CONFIG:min.insync.replicas=1}
   #  segment.ms=604800000        synonyms={DEFAULT_CONFIG:log.roll.hours=168}
   #  max.message.bytes=1048588   synonyms={DEFAULT_CONFIG:message.max.bytes=1048588}
   #  compression.type=producer   synonyms={DEFAULT_CONFIG:compression.type=producer}
   ```
   `kcfg --describe` **không** `--all` chỉ in config **đã override** ở topic (ở đây: `retention.ms`).
2. Alter topic động (không restart, không cần `kafka-topics.sh`), rồi xoá override để giá trị **rơi về tầng dưới**.

   ```bash
   kcfg --alter --entity-type topics --entity-name lab27-cfg --add-config segment.ms=60000,max.message.bytes=2000000
   kcfg --describe --entity-type topics --entity-name lab27-cfg            # 3 override: retention.ms, segment.ms, max.message.bytes
   kcfg --alter --entity-type topics --entity-name lab27-cfg --delete-config segment.ms
   kcfg --describe --entity-type topics --entity-name lab27-cfg --all | grep -E "^\s+segment.ms="   # về DEFAULT_CONFIG:log.roll.hours=168
   ```
3. Config **broker** (`--entity-name <node.id>`; broker kafka-1 = node **2**): xem chế độ update của vài config quen.

   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 --all \
     | grep -E "^\s+(message.max.bytes|log.retention.ms|log.retention.check.interval.ms|min.insync.replicas|num.io.threads|unclean.leader.election.enable)="
   ```
4. Alter **per-broker** (`num.io.threads` là config cluster-wide, đặt riêng 1 broker vẫn được) và **cluster-default** (`--entity-default`, áp cho mọi broker chưa override).

   ```bash
   kcfg --alter --entity-type brokers --entity-name 2 --add-config num.io.threads=12
   kcfg --alter --entity-type brokers --entity-default --add-config message.max.bytes=2000000
   kcfg --describe --entity-type brokers --entity-name 2 --all | grep -E "^\s+(num.io.threads|message.max.bytes)="
   #  num.io.threads=12         synonyms={DYNAMIC_BROKER_CONFIG:num.io.threads=12, DEFAULT_CONFIG:num.io.threads=8}
   #  message.max.bytes=2000000 synonyms={DYNAMIC_DEFAULT_BROKER_CONFIG:message.max.bytes=2000000, DEFAULT_CONFIG:message.max.bytes=1048588}
   kcfg --describe --entity-type brokers --entity-name 3 --all | grep -E "^\s+message.max.bytes="   # broker 3 cũng nhận cluster-default
   kcfg --describe --entity-type brokers --entity-default                                             # chỉ in config cluster-default
   ```
   Topic `lab27-cfg` có `max.message.bytes=2000000` **riêng** nên không đổi; topic khác giờ hiệu lực 2 000 000 qua broker default → xem lại bằng `--describe --entity-type topics --entity-name lab21-acks --all | grep max.message.bytes` (thấy `DYNAMIC_DEFAULT_BROKER_CONFIG`).
5. Config **read-only** → bị từ chối, phải sửa `server.properties` (biến `KAFKA_*` trong compose) + restart.

   ```bash
   kcfg --alter --entity-type brokers --entity-name 2 --add-config log.retention.check.interval.ms=60000
   # ERROR ... InvalidRequestException: Cannot update these configs dynamically: Set(log.retention.check.interval.ms)
   ```
6. Ràng buộc **ELR**: với ELR bật (mặc định cluster mới 4.1+), `min.insync.replicas` **không được** alter ở broker-level; đặt ở cluster-level thì được (và **reset ELR**).

   ```bash
   kcfg --alter --entity-type brokers --entity-name 2 --add-config min.insync.replicas=1
   # ERROR ... (bị từ chối khi ELR bật — thông điệp nhắc min.insync.replicas broker-level không được phép)
   kcfg --describe --entity-type brokers --entity-default | grep min.insync.replicas    # controller đã tự thêm min.insync.replicas=2 ở cluster-level khi bật ELR
   ```
   Nếu lệnh đầu **thành công** thì cluster của bạn chưa bật ELR (`kafka-features.sh describe | grep eligible.leader.replicas.version`) — xoá lại ngay bằng `--delete-config min.insync.replicas`.

### ✅ Kiểm chứng

- Bước 1–2: synonyms đổi từ `DYNAMIC_TOPIC_CONFIG` → `DEFAULT_CONFIG` khi `--delete-config`; `kcfg --describe` không `--all` chỉ in override.
- Bước 4: `num.io.threads` mang nhãn `DYNAMIC_BROKER_CONFIG`; `message.max.bytes` mang `DYNAMIC_DEFAULT_BROKER_CONFIG` trên **mọi** broker.
- Bước 5: `Cannot update these configs dynamically`. Bước 6: broker-level `min.insync.replicas` bị từ chối (ELR bật).

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type brokers --entity-name 2 --delete-config num.io.threads
kcfg --alter --entity-type brokers --entity-default --delete-config message.max.bytes
kt --delete --topic lab27-cfg
kt --delete --topic lab21-acks            # topic giữ từ Lab 2.1
# Kết thúc tuần: tắt cluster (GIỮ 2 file compose, acks-probe.mjs, compaction.mjs, kafka.mjs cho Tuần 3)
docker compose -f ~/kafka-labs/docker-compose.cluster.yml down
```

### 🧠 Ý nghĩa với đề thi

- Đổi config topic lúc chạy → **`kafka-configs.sh --alter --entity-type topics`** (`kafka-topics.sh --alter --config` không dùng với `--bootstrap-server`).
- `--entity-type brokers --entity-default` = cluster-wide dynamic default; `--entity-name <id>` = per-broker; read-only (ví dụ `log.retention.check.interval.ms`, `log.dirs`, `process.roles`) cần restart.
- Đọc synonyms để trả lời "giá trị hiệu lực đến từ đâu": `DYNAMIC_TOPIC_CONFIG` > `DYNAMIC_BROKER_CONFIG` > `DYNAMIC_DEFAULT_BROKER_CONFIG` > `STATIC_BROKER_CONFIG` > `DEFAULT_CONFIG`.
- ELR + `min.insync.replicas`: đặt ở **cluster-level**, đổi giá trị = **reset ELR**.

---

> ✅ Xong 7 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist) — đặc biệt 2 lab ⭐ (2.1 `acks` × `min.isr`, 2.4 compaction) là nguồn câu hỏi FUND nặng nhất. Giữ `acks-probe.mjs`, `compaction.mjs`, `kafka.mjs` trong `~/kafka-labs/week-02/` cho Tuần 3. Rồi làm [bộ câu hỏi luyện tập](questions.md) (28 câu, mục tiêu ≥ 70%) và trả lời trôi chảy 8 câu Cổng tự kiểm tra trước khi sang Tuần 3.
