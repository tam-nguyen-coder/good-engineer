# 🧪 Hands-on Labs — Tuần 4: Consumer chuyên sâu (group, rebalance, offset, lag)

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab (trừ khi lab sau nói "giữ nguyên").
> ⚙️ Yêu cầu chung: đã dựng 2 file compose chuẩn ở [Tuần 1 — Lab 1.1 / 1.2](../week-01/labs.md) và cài `kafkajs` trong `~/kafka-labs/`.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../KAFKA-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần cho cả tuần)

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d
docker compose -f docker-compose.cluster.yml ps        # 4 container: controller, kafka-1, kafka-2, kafka-3

# Alias trỏ vào cluster 3 node (xem Tuần 1 — Chuẩn bị chung)
export KAFKA_CTR=kafka-1
export KAFKA_BS=kafka-1:19092
```

Nếu shell mới chưa có alias, nạp lại 6 dòng alias từ [Tuần 1](../week-01/labs.md#2-alias-cli-thêm-vào-zshrc-hoặc-chạy-mỗi-phiên) (`kt`, `kcp`, `kcc`, `kcg`, `kcfg`, `ksh`).

Tạo topic dùng chung cho cả tuần — **6 partition** để quan sát việc chia partition:

```bash
kt --create --topic orders --partitions 6 --replication-factor 3
kt --describe --topic orders
```

> 🧠 **Hai đồng hồ sống phải nhớ trước khi vào lab** (Tuần 4 xoay quanh chúng):
>
> - `session.timeout.ms` **45000** + `heartbeat.interval.ms` **3000** → **heartbeat thread**, phát hiện *tiến trình chết*.
> - `max.poll.interval.ms` **300000** → **processing thread**, phát hiện *xử lý quá lâu*.
> - Trong `kafkajs` hai giá trị này là `sessionTimeout` và **`rebalanceTimeout`** (tương đương `max.poll.interval.ms`).

---

## Lab 4.1 — Consumer group scaling: 1 → 2 → 3 → 7 consumer ⭐

**🎯 Mục tiêu:** Chứng minh bằng mắt rằng **1 partition chỉ thuộc tối đa 1 consumer trong group**, và consumer thứ 7 trên topic 6 partition sẽ **idle** hoàn toàn.
**🧩 Luyện kỹ năng (liên quan đề):**

- Trần song song của consumer group = **số partition** (bẫy kinh điển: "thêm consumer mà lag không giảm").
- Đọc `kcg --describe --members --verbose` để thấy cột `#PARTITIONS` và `ASSIGNMENT`.
- Quan sát rebalance xảy ra mỗi lần member join/leave.

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Viết consumer in rõ partition nó đang giữ.

   ```javascript
   // ~/kafka-labs/w4-consumer.mjs
   import { Kafka, logLevel } from "kafkajs";

   const id = process.argv[2] ?? "c1";
   const kafka = new Kafka({
     clientId: `w4-${id}`,
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.NOTHING,
   });

   const consumer = kafka.consumer({ groupId: "w4-scaling" });
   await consumer.connect();
   await consumer.subscribe({ topic: "orders", fromBeginning: false });

   // In assignment mỗi khi group ổn định lại sau rebalance
   consumer.on(consumer.events.GROUP_JOIN, ({ payload }) => {
     const parts = payload.memberAssignment["orders"] ?? [];
     console.log(`[${id}] GROUP_JOIN → giữ ${parts.length} partition: [${parts.join(", ")}]`);
   });

   await consumer.run({
     eachMessage: async ({ partition, message }) => {
       console.log(`[${id}] p${partition} offset=${message.offset} key=${message.key}`);
     },
   });
   ```
2. Mở **terminal 1**, chạy consumer đầu tiên và đọc dòng `GROUP_JOIN`.

   ```bash
   cd ~/kafka-labs && node w4-consumer.mjs c1
   # [c1] GROUP_JOIN → giữ 6 partition: [0, 1, 2, 3, 4, 5]
   ```
3. Mở **terminal 2**, thêm consumer thứ hai. Cả hai terminal đều in lại `GROUP_JOIN` (đó là rebalance).

   ```bash
   node w4-consumer.mjs c2      # mỗi bên giữ 3 partition
   ```
4. Thêm **terminal 3** (mỗi bên 2 partition), rồi lần lượt mở tới **terminal 7**.

   ```bash
   node w4-consumer.mjs c3
   # ... c4, c5, c6, c7
   ```
5. Trong terminal thứ 8, xem trạng thái group từ phía broker.

   ```bash
   kcg --describe --group w4-scaling --members --verbose
   kcg --describe --group w4-scaling --state
   ```

### ✅ Kiểm chứng

- Với 7 consumer, `--members --verbose` cho thấy **6 member có 1 partition** và **1 member có `#PARTITIONS 0`, cột `ASSIGNMENT` rỗng** — đó là consumer idle.
- Bơm dữ liệu và xác nhận consumer idle **không nhận record nào**:
  ```bash
  kafka-producer-perf-test() { docker exec -it kafka-1 /opt/kafka/bin/kafka-producer-perf-test.sh "$@"; }
  kafka-producer-perf-test --topic orders --num-records 600 --record-size 200 \
    --throughput 200 --producer-props bootstrap.servers=kafka-1:19092
  ```
- Tắt 1 consumer (Ctrl+C) → các consumer còn lại in `GROUP_JOIN` mới với nhiều partition hơn.

### 🧹 Dọn dẹp

```bash
# Ctrl+C tất cả terminal consumer
kcg --delete --group w4-scaling     # chỉ chạy được khi group không còn member
```

### 🧠 Ý nghĩa với đề thi

- "Thêm consumer nhưng lag không giảm" → consumer **đã bằng hoặc vượt số partition** → phải **tăng partition** (và chấp nhận phá ordering theo key).
- Consumer dư không gây lỗi, chỉ **nằm không** — nhưng vẫn tham gia rebalance, nên vẫn tốn chi phí.

---

## Lab 4.2 — Eager vs Cooperative vs KIP-848

**🎯 Mục tiêu:** Nhìn thấy khác biệt giữa 3 chế độ rebalance bằng chính công cụ dòng lệnh, và xác nhận **group type** phía broker.
**🧩 Luyện kỹ năng (liên quan đề):**

- `partition.assignment.strategy` (classic) vs `group.protocol=consumer` (KIP-848).
- Đọc `kcg --describe --state` để biết group đang chạy protocol nào.
- Hiểu vì sao nâng cấp lên cooperative cần **2 rolling bounce**.

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 4.1 (topic `orders` 6 partition).

### Các bước

1. Chạy **2 console consumer** dùng `CooperativeStickyAssignor` (classic protocol, cooperative rebalance). Mỗi lệnh ở một terminal.

   ```bash
   docker exec -it kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic orders --group w4-coop \
     --consumer-property partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
   ```
2. Xem protocol group đang dùng.

   ```bash
   kcg --describe --group w4-coop --state
   # ASSIGNMENT-STRATEGY hiển thị cooperative-sticky
   ```
3. Bây giờ thử **protocol mới KIP-848**: chạy 2 console consumer với `group.protocol=consumer` ở group khác.

   ```bash
   docker exec -it kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic orders --group w4-kip848 \
     --consumer-property group.protocol=consumer
   ```
4. So sánh 2 group.

   ```bash
   kcg --describe --group w4-coop    --state
   kcg --describe --group w4-kip848  --state
   docker exec -it kafka-1 /opt/kafka/bin/kafka-groups.sh --bootstrap-server kafka-1:19092 --list
   ```
5. Thử đặt **cả hai** cho cùng một consumer để thấy client config bị bỏ qua:

   ```bash
   docker exec -it kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic orders --group w4-kip848 \
     --consumer-property group.protocol=consumer \
     --consumer-property partition.assignment.strategy=org.apache.kafka.clients.consumer.RangeAssignor
   ```

### ✅ Kiểm chứng

- Group `w4-coop` hiển thị **`GROUP-PROTOCOL` / `ASSIGNMENT-STRATEGY` = cooperative-sticky** (classic + cooperative).
- Group `w4-kip848` hiển thị group type **`consumer`**; cột assignment strategy trống hoặc ghi assignor phía broker (`uniform`).
- Bước 5 **không báo lỗi**: `partition.assignment.strategy` bị **bỏ qua trong im lặng** — đúng bẫy đề. Thêm consumer/bớt consumer ở group KIP-848, các consumer còn lại **không bị dừng toàn bộ** như eager.

### 🧹 Dọn dẹp

```bash
# Ctrl+C mọi console consumer
kcg --delete --group w4-coop
kcg --delete --group w4-kip848
```

### 🧠 Ý nghĩa với đề thi

- **Ai tính assignment**: classic = một consumer (group leader) · KIP-848 = **group coordinator (broker)**.
- Với `group.protocol=consumer`, ba config client **bị bỏ qua**: `session.timeout.ms`, `heartbeat.interval.ms`, `partition.assignment.strategy` — thay bằng group config phía broker (`consumer.session.timeout.ms` 45000, `consumer.heartbeat.interval.ms` 5000). `max.poll.interval.ms` **vẫn còn tác dụng**.
- Nâng cấp classic → cooperative: **2 rolling bounce** (thêm `CooperativeStickyAssignor` vào đầu list, rồi bỏ assignor cũ).

---

## Lab 4.3 — Commit thủ công: tạo duplicate và tạo mất message ⭐

**🎯 Mục tiêu:** Tự tay sản xuất ra **cả hai** sự cố kinh điển — xử lý trùng (at-least-once) và mất message (at-most-once) — chỉ bằng cách đổi **vị trí commit**.
**🧩 Luyện kỹ năng (liên quan đề):**

- `enable.auto.commit=false` → `eachBatch` + `resolveOffset` + `commitOffsetsIfNecessary` trong `kafkajs`.
- Quy tắc **commit = offset đã xử lý + 1**.
- Vì sao delivery semantics là **thuộc tính của code**, không phải của Kafka.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic nhỏ và bơm 20 record đánh số.

   ```bash
   kt --create --topic commit-demo --partitions 1 --replication-factor 3
   for i in $(seq 1 20); do echo "msg-$i"; done | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
       --bootstrap-server kafka-1:19092 --topic commit-demo
   ```
2. **Phiên bản A — commit SAU khi xử lý** (at-least-once, sinh duplicate khi crash).

   ```javascript
   // ~/kafka-labs/w4-commit-after.mjs
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w4-commit-after",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.NOTHING,
   });
   const consumer = kafka.consumer({ groupId: "w4-commit-after" });

   await consumer.connect();
   await consumer.subscribe({ topic: "commit-demo", fromBeginning: true });

   let processed = 0;
   await consumer.run({
     autoCommit: false,
     eachBatch: async ({ batch, resolveOffset, commitOffsetsIfNecessary, heartbeat }) => {
       for (const message of batch.messages) {
         console.log(`XỬ LÝ ${message.value.toString()} (offset ${message.offset})`);
         processed++;
         if (processed === 5) {
           console.log(">>> CRASH giả lập TRƯỚC khi commit");
           process.exit(1);            // chưa commit gì cả
         }
         resolveOffset(message.offset);
         await heartbeat();
       }
       await commitOffsetsIfNecessary();   // commit sau khi xử lý xong batch
     },
   });
   ```

   ```bash
   node w4-commit-after.mjs     # crash sau 5 record
   node w4-commit-after.mjs     # chạy lại
   ```
3. **Phiên bản B — commit TRƯỚC khi xử lý** (at-most-once, mất message khi crash).

   ```javascript
   // ~/kafka-labs/w4-commit-before.mjs
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w4-commit-before",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.NOTHING,
   });
   const consumer = kafka.consumer({ groupId: "w4-commit-before" });

   await consumer.connect();
   await consumer.subscribe({ topic: "commit-demo", fromBeginning: true });

   let seen = 0;
   await consumer.run({
     autoCommit: false,
     eachMessage: async ({ topic, partition, message }) => {
       // COMMIT TRƯỚC: offset đã xử lý + 1
       await consumer.commitOffsets([
         { topic, partition, offset: (BigInt(message.offset) + 1n).toString() },
       ]);
       console.log(`ĐÃ COMMIT tới ${Number(message.offset) + 1}, giờ mới xử lý ${message.value}`);
       seen++;
       if (seen === 5) {
         console.log(">>> CRASH giả lập SAU commit, TRƯỚC khi xử lý xong");
         process.exit(1);
       }
     },
   });
   ```

   ```bash
   node w4-commit-before.mjs
   node w4-commit-before.mjs
   ```
4. Xem offset đã commit của từng group.

   ```bash
   kcg --describe --group w4-commit-after
   kcg --describe --group w4-commit-before
   ```

### ✅ Kiểm chứng

- **Phiên bản A:** lần chạy thứ hai in lại **`msg-1` … `msg-5`** → **xử lý trùng**. `CURRENT-OFFSET` sau lần 1 vẫn là 0.
- **Phiên bản B:** lần chạy thứ hai bắt đầu từ **`msg-6`**, nghĩa là `msg-5` đã được commit nhưng **chưa bao giờ xử lý xong** → **mất message**.
- Chú ý con số trong `commitOffsets`: phải là `offset + 1`. Thử bỏ `+ 1n` và chạy lại để thấy `msg-5` bị đọc lại mãi.

### 🧹 Dọn dẹp

```bash
kcg --delete --group w4-commit-after
kcg --delete --group w4-commit-before
kt --delete --topic commit-demo
rm -f w4-commit-after.mjs w4-commit-before.mjs
```

### 🧠 Ý nghĩa với đề thi

- **Commit sau xử lý = at-least-once** (mặc định, kể cả auto-commit) → downstream phải **idempotent**.
- **Commit trước xử lý = at-most-once** → chấp nhận mất dữ liệu để không bao giờ trùng.
- Muốn exactly-once: transaction + `sendOffsetsToTransaction` (Tuần 3) hoặc **idempotent consumer** với khoá dedup (Tuần 9).

---

## Lab 4.4 — Bẫy `max.poll.interval.ms`

**🎯 Mục tiêu:** Ép consumer bị **đá khỏi group vì xử lý lâu** dù heartbeat vẫn đều, và thấy đúng thông báo `The group is rebalancing`.
**🧩 Luyện kỹ năng (liên quan đề):**

- Phân biệt `sessionTimeout` (heartbeat thread) và `rebalanceTimeout` (= `max.poll.interval.ms`, processing thread).
- Nhận diện triệu chứng `CommitFailedException` / rebalance lặp.
- Hai cách sửa: **giảm khối lượng mỗi vòng** hoặc **tăng giới hạn**.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic và bơm vài record.

   ```bash
   kt --create --topic slow-demo --partitions 1 --replication-factor 3
   for i in $(seq 1 10); do echo "job-$i"; done | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
       --bootstrap-server kafka-1:19092 --topic slow-demo
   ```
2. Consumer cố tình xử lý **15 giây/record** trong khi `rebalanceTimeout` chỉ **10 giây**.

   ```javascript
   // ~/kafka-labs/w4-slow.mjs
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w4-slow",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.WARN,          // để nhìn thấy cảnh báo rebalance
   });

   const consumer = kafka.consumer({
     groupId: "w4-slow",
     sessionTimeout: 10000,            // heartbeat thread
     rebalanceTimeout: 10000,          // tương đương max.poll.interval.ms
     heartbeatInterval: 3000,
   });

   await consumer.connect();
   await consumer.subscribe({ topic: "slow-demo", fromBeginning: true });

   await consumer.run({
     eachMessage: async ({ message }) => {
       console.log(`Bắt đầu xử lý ${message.value} lúc ${new Date().toISOString()}`);
       await new Promise((r) => setTimeout(r, 15000));   // 15s > rebalanceTimeout 10s
       console.log(`Xong ${message.value}`);
     },
   });
   ```

   ```bash
   node w4-slow.mjs
   ```
3. Quan sát log: sau ~10 giây, client bị coi là chết và xuất hiện cảnh báo rebalance / lỗi commit. Ghi lại thông điệp chính xác.
4. **Sửa cách 1 — tăng giới hạn:** đổi `rebalanceTimeout: 60000`, chạy lại.
5. **Sửa cách 2 — giảm khối lượng:** giữ `rebalanceTimeout: 10000` nhưng rút thời gian xử lý xuống 2 giây và thêm `maxBytesPerPartition`/`eachBatchAutoResolve` nếu cần; trong Java tương đương là **giảm `max.poll.records`**.

### ✅ Kiểm chứng

- Ở bước 3 consumer **liên tục rejoin**: cùng một record được xử lý lại nhiều lần, và `kcg --describe --group w4-slow --state` cho thấy group ở trạng thái rebalance thường xuyên.
- Sau bước 4 hoặc 5, group ổn định (`Stable`) và mỗi record chỉ xử lý một lần.

### 🧹 Dọn dẹp

```bash
kcg --delete --group w4-slow
kt --delete --topic slow-demo
rm -f w4-slow.mjs
```

### 🧠 Ý nghĩa với đề thi

- **Heartbeat đều nhưng vẫn bị kick** → luôn là `max.poll.interval.ms`, không bao giờ là `session.timeout.ms`.
- Triệu chứng đi kèm: `CommitFailedException` khi commit sau rebalance, lag tăng dù CPU thấp.
- Với công việc dài thật sự: đẩy sang worker pool + `pause()`/`resume()` để vòng `poll()` luôn quay đều.

---

## Lab 4.5 — Reset offsets bằng CLI ⭐

**🎯 Mục tiêu:** Thành thạo `kafka-consumer-groups.sh --reset-offsets` với 3 scenario hay dùng, và tự gặp lỗi khi group còn active.
**🧩 Luyện kỹ năng (liên quan đề):**

- Hai điều kiện bắt buộc: **group inactive** và **`--execute`** (mặc định là dry-run).
- Các scenario `--to-earliest`, `--shift-by`, `--to-datetime`, `--export`/`--from-file`.
- Vì sao reset offset là cách "replay" chuẩn thay vì đổi `auto.offset.reset`.

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic, bơm 50 record, chạy consumer một lát rồi **dừng hẳn**.

   ```bash
   kt --create --topic reset-demo --partitions 3 --replication-factor 3
   for i in $(seq 1 50); do echo "r-$i"; done | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
       --bootstrap-server kafka-1:19092 --topic reset-demo

   docker exec -it kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic reset-demo \
     --group w4-reset --from-beginning --timeout-ms 8000
   kcg --describe --group w4-reset        # CURRENT-OFFSET đã ở cuối
   ```
2. **Thử khi group còn active** (mở console consumer ở terminal khác rồi chạy lệnh dưới) để thấy lỗi.

   ```bash
   kcg --group w4-reset --topic reset-demo --reset-offsets --to-earliest --execute
   # Error: Assignments can only be reset if the group 'w4-reset' is inactive
   ```
3. Dừng mọi consumer, chạy **dry-run** (không có `--execute`).

   ```bash
   kcg --group w4-reset --topic reset-demo --reset-offsets --to-earliest
   # Chỉ in bảng TOPIC PARTITION NEW-OFFSET — chưa thay đổi gì
   kcg --describe --group w4-reset        # xác nhận offset chưa đổi
   ```
4. Áp dụng thật với `--execute`, rồi thử 2 scenario còn lại.

   ```bash
   kcg --group w4-reset --topic reset-demo --reset-offsets --to-earliest --execute
   kcg --group w4-reset --topic reset-demo --reset-offsets --shift-by -5 --execute
   kcg --group w4-reset --topic reset-demo --reset-offsets \
       --to-datetime "$(date -u -v-1H '+%Y-%m-%dT%H:%M:%S.000')" --execute
   # Linux thay bằng: --to-datetime "$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%S.000')"
   ```
5. Xuất và nạp lại bằng CSV (cách an toàn khi cần rollback).

   ```bash
   kcg --group w4-reset --topic reset-demo --reset-offsets --to-current --export --dry-run > /tmp/offsets.csv
   cat /tmp/offsets.csv
   ```

### ✅ Kiểm chứng

- Bước 2 báo lỗi **group không inactive** — đây là câu hỏi hay gặp.
- Bước 3 in bảng nhưng `kcg --describe` cho thấy `CURRENT-OFFSET` **không đổi** → dry-run.
- Sau `--to-earliest --execute`, `CURRENT-OFFSET` về 0 và `LAG` bằng tổng số record; chạy lại console consumer thấy đọc lại từ đầu.

### 🧹 Dọn dẹp

```bash
kcg --delete --group w4-reset
kt --delete --topic reset-demo
rm -f /tmp/offsets.csv
```

### 🧠 Ý nghĩa với đề thi

- Reset offset là cách **replay** đúng chuẩn. Đổi `auto.offset.reset` **không** có tác dụng khi group đã có committed offset.
- Nhớ 2 điều kiện: **inactive** + **`--execute`**. Thiếu `--execute` là bẫy xuất hiện rất thường xuyên.

---

## Lab 4.6 — `seek()` và đọc theo timestamp

**🎯 Mục tiêu:** Điều khiển vị trí đọc trong code (`seek`) và tra offset theo mốc thời gian, đồng thời thử chế độ `assign` qua console consumer.
**🧩 Luyện kỹ năng (liên quan đề):**

- `consumer.seek()` và `admin.fetchTopicOffsetsByTimestamp()` (tương đương `offsetsForTimes` của Java).
- `assign()` vs `subscribe()`: không group coordination, không rebalance.
- Khi nào dùng seek thay vì reset offset bằng CLI.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic 1 partition và bơm dữ liệu theo 2 đợt, cách nhau 1 phút (để timestamp khác nhau rõ rệt).

   ```bash
   kt --create --topic seek-demo --partitions 1 --replication-factor 3
   for i in $(seq 1 10); do echo "batch1-$i"; done | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic seek-demo
   echo "Chờ 60 giây..." && sleep 60
   for i in $(seq 1 10); do echo "batch2-$i"; done | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic seek-demo
   ```
2. `seek()` tới một offset cụ thể.

   ```javascript
   // ~/kafka-labs/w4-seek.mjs
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w4-seek",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.NOTHING,
   });
   const consumer = kafka.consumer({ groupId: "w4-seek" });

   await consumer.connect();
   await consumer.subscribe({ topic: "seek-demo", fromBeginning: true });

   await consumer.run({
     eachMessage: async ({ partition, message }) => {
       console.log(`p${partition} offset=${message.offset} ${message.value}`);
     },
   });

   // seek phải gọi SAU khi run() đã bắt đầu
   consumer.seek({ topic: "seek-demo", partition: 0, offset: "12" });
   ```

   ```bash
   node w4-seek.mjs      # bắt đầu từ offset 12, không phải 0
   ```
3. Tra offset theo timestamp bằng admin client.

   ```javascript
   // ~/kafka-labs/w4-by-time.mjs
   import { Kafka } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w4-by-time",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
   });
   const admin = kafka.admin();
   await admin.connect();

   const since = Date.now() - 30_000;     // 30 giây trước
   const offsets = await admin.fetchTopicOffsetsByTimestamp("seek-demo", since);
   console.log("Offset đầu tiên có timestamp >= 30s trước:", offsets);

   await admin.disconnect();
   ```

   ```bash
   node w4-by-time.mjs
   ```
4. Chế độ `assign` qua console consumer: đọc đúng 1 partition từ 1 offset, **không dùng group**.

   ```bash
   docker exec -it kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic seek-demo \
     --partition 0 --offset 3 --max-messages 5
   ```

### ✅ Kiểm chứng

- Bước 2 in record từ `offset=12` trở đi (tức `batch2-3` trở đi), bỏ qua 12 record đầu.
- Bước 3 trả về offset tương ứng ranh giới giữa hai đợt bơm — chứng minh có thể "tua" theo thời gian.
- Bước 4 chạy **không cần `--group`** và `kcg --list` **không** xuất hiện group mới → đó là `assign()`.

### 🧹 Dọn dẹp

```bash
kcg --delete --group w4-seek
kt --delete --topic seek-demo
rm -f w4-seek.mjs w4-by-time.mjs
```

### 🧠 Ý nghĩa với đề thi

- `seek()` dùng khi ứng dụng **tự quản vị trí** (ví dụ lưu offset trong DB cùng kết quả → exactly-once phía consumer).
- `assign()` cho quyền kiểm soát tuyệt đối nhưng **mất failover** và **không đo được consumer lag** bằng công cụ group.

---

## Lab 4.7 — Share group + đo consumer lag (tuỳ chọn)

**🎯 Mục tiêu:** So sánh trực tiếp **consumer group** (1 partition → 1 consumer) với **share group** (nhiều consumer cùng 1 partition), và đọc cột LAG khi tải đang chạy.
**🧩 Luyện kỹ năng (liên quan đề):**

- Queues for Kafka (KIP-932, GA 4.2) và lệnh `kafka-console-share-consumer.sh` / `kafka-share-groups.sh`.
- `LAG = LOG-END-OFFSET − CURRENT-OFFSET` và ý nghĩa cột `CONSUMER-ID`.
- Vì sao share group **không** báo `CURRENT-OFFSET`.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Kiểm tra feature share group đã bật chưa; nếu chưa thì nâng.

   ```bash
   docker exec -it kafka-1 /opt/kafka/bin/kafka-features.sh --bootstrap-server kafka-1:19092 describe
   # Nếu share.version ở mức 0:
   docker exec -it kafka-1 /opt/kafka/bin/kafka-features.sh --bootstrap-server kafka-1:19092 \
     upgrade --feature share.version=1
   ```
2. Tạo topic **1 partition** để chứng minh nhiều consumer cùng đọc một partition.

   ```bash
   kt --create --topic jobs --partitions 1 --replication-factor 3
   ```
3. Mở **2 terminal**, mỗi terminal 1 share consumer **cùng group**.

   ```bash
   docker exec -it kafka-1 /opt/kafka/bin/kafka-console-share-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic jobs --group workers
   ```
4. Bơm 20 job và quan sát chúng được **chia** cho 2 consumer.

   ```bash
   for i in $(seq 1 20); do echo "job-$i"; done | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic jobs
   ```
5. Xem trạng thái share group và so với consumer group thường.

   ```bash
   docker exec -it kafka-1 /opt/kafka/bin/kafka-share-groups.sh --bootstrap-server kafka-1:19092 --describe --group workers
   docker exec -it kafka-1 /opt/kafka/bin/kafka-share-groups.sh --bootstrap-server kafka-1:19092 --describe --group workers --members
   ```
6. Đo lag của một consumer group thường trong lúc tải chạy.

   ```bash
   # Terminal A: bơm liên tục
   docker exec -it kafka-1 /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic orders --num-records 200000 --record-size 200 --throughput 5000 \
     --producer-props bootstrap.servers=kafka-1:19092

   # Terminal B: consumer chậm (Lab 4.1) + theo dõi lag
   watch -n 2 "docker exec kafka-1 /opt/kafka/bin/kafka-consumer-groups.sh \
     --bootstrap-server kafka-1:19092 --describe --group w4-scaling"
   ```

### ✅ Kiểm chứng

- Với **1 partition**, hai share consumer **đều nhận job** — điều không thể xảy ra với consumer group thường.
- `kafka-share-groups.sh --describe --members` cho thấy **cùng một partition xuất hiện ở nhiều member**.
- Output của share group có `START-OFFSET` và `LAG` nhưng **không có `CURRENT-OFFSET`**, vì share group không commit offset theo kiểu cũ.
- Ở bước 6, cột `LAG` tăng khi consumer chậm hơn producer và giảm khi thêm consumer.

### 🧹 Dọn dẹp

```bash
# Ctrl+C mọi consumer
kt --delete --topic jobs
kt --delete --topic orders
kcg --delete --group w4-scaling
cd ~/kafka-labs && docker compose -f docker-compose.cluster.yml down
rm -f w4-consumer.mjs
```

### 🧠 Ý nghĩa với đề thi

- Từ khoá "**nhiều worker hơn số partition**, ack từng record, redelivery khi lỗi, không cần thứ tự" → **share group**, không phải consumer group.
- `group.share.record.lock.duration.ms` (30 s) đóng vai trò như visibility timeout của `SQS`; giới hạn số lần giao đóng vai trò như `maxReceiveCount`.
- Lag của tool tính theo **committed offset**, còn metric client `records-lag-max` tính theo **position** — hai con số có thể lệch nhau (chi tiết ở Tuần 8).

---

> ✅ Xong 7 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist), rồi làm [bộ 30 câu luyện tập](questions.md) và **MINI-MOCK FUND + DEV** trước khi sang Tuần 5. Ngưỡng qua cổng: **≥ 70%**.
