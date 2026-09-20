# 🧪 Hands-on Labs — Tuần 3: Producer chuyên sâu + Transactions

> Lab cầm tay chỉ việc, chạy hoàn toàn local bằng Docker (không tốn phí). LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: Docker Desktop, Node.js 24, cluster 3 node từ Tuần 1 (Lab 1.2). Tổng ~3.5h.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab)

### 1) Khởi động cluster 3 broker (dùng lại `docker-compose.cluster.yml` của Tuần 1)

```bash
# Đứng ở thư mục chứa compose của Tuần 1 (Lab 1.2)
docker compose -f docker-compose.cluster.yml up -d
docker compose -f docker-compose.cluster.yml ps        # 3 broker + 1 controller đều "running"
```

> Nếu bạn làm tuần này độc lập, đây là bản **rút gọn** đủ chạy (bản đầy đủ + giải thích ở Tuần 1). Điểm cần khớp với Tuần 1: tên container `kafka-1`/`kafka-2`/`kafka-3`/`controller-1`, port host 9092/9094/9096, `min.insync.replicas=2`, RF mặc định 3, và **listener nội bộ `kafka-N:19092`** dùng cho lệnh chạy bên trong container.

<details>
<summary>docker-compose.cluster.yml (rút gọn)</summary>

```yaml
services:
  controller-1:
    image: apache/kafka:4.3.1
    container_name: controller-1
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: controller
      KAFKA_LISTENERS: CONTROLLER://:9093
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@controller-1:9093
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk

  kafka-1: &broker
    image: apache/kafka:4.3.1
    container_name: kafka-1
    depends_on: [controller-1]
    ports: ["9092:9092"]
    environment: &broker-env
      KAFKA_NODE_ID: 2
      KAFKA_PROCESS_ROLES: broker
      KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:19092,PLAINTEXT_HOST://localhost:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@controller-1:9093
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk

  kafka-2:
    <<: *broker
    container_name: kafka-2
    ports: ["9094:9094"]
    environment:
      <<: *broker-env
      KAFKA_NODE_ID: 3
      KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9094
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-2:19092,PLAINTEXT_HOST://localhost:9094

  kafka-3:
    <<: *broker
    container_name: kafka-3
    ports: ["9096:9096"]
    environment:
      <<: *broker-env
      KAFKA_NODE_ID: 4
      KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9096
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-3:19092,PLAINTEXT_HOST://localhost:9096
```

</details>

### 2) Alias CLI (như Tuần 1, trỏ vào `kafka-1`)

```bash
export BS=kafka-1:19092          # bootstrap dùng BÊN TRONG container
export BS_HOST=localhost:9092,localhost:9094,localhost:9096   # bootstrap dùng từ máy host (kafkajs)
alias kt='docker exec -it kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server $BS'
alias kcp='docker exec -it kafka-1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $BS'
alias kcc='docker exec -it kafka-1 /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $BS'
alias kcg='docker exec -it kafka-1 /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $BS'
alias kperf='docker exec -it kafka-1 /opt/kafka/bin/kafka-producer-perf-test.sh'
alias koff='docker exec -it kafka-1 /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $BS'
kt --list      # kiểm tra kết nối
```

### 3) Project Node.js

```bash
mkdir -p ~/kafka-labs/week-03 && cd ~/kafka-labs/week-03
npm init -y >/dev/null && npm pkg set type=module && npm i kafkajs
node -v      # v24.x
```

> 🧠 **Ghi chú client (đọc 1 lần):** client production do Confluent hỗ trợ cho Node là `@confluentinc/kafka-javascript` (API tương thích KafkaJS, hỗ trợ KIP-848 & share groups). Labs dùng `kafkajs` vì cài nhẹ, không cần native build. **Khác biệt phải nhớ khi thi:** `kafkajs` không expose `linger.ms`/`batch.size` (batch = mảng `messages` trong 1 `send()`), yêu cầu `maxInFlightRequests: 1` khi `idempotent: true` (Java cho phép ≤5), và consumer **mặc định `readUncommitted: false`** (= `read_committed`, ngược với Java mặc định `read_uncommitted`). Đề CCDAK hỏi theo **tên config Java** → mỗi lab đều ghi tên Java tương ứng.

File dùng chung `kafka.mjs`:

```javascript
// kafka.mjs — client dùng chung cho mọi lab tuần 3
import { Kafka, logLevel } from "kafkajs";

export const BROKERS = ["localhost:9092", "localhost:9094", "localhost:9096"];

export const kafka = new Kafka({
  clientId: "week03-lab",            // Java: client.id
  brokers: BROKERS,                  // Java: bootstrap.servers
  requestTimeout: 30000,             // Java: request.timeout.ms (mặc định 30.000)
  retry: { initialRetryTime: 100, retries: 8 }, // Java: retry.backoff.ms / retries
  logLevel: logLevel.WARN,
});

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export function percentile(arr, p) {
  const s = [...arr].sort((a, b) => a - b);
  return s[Math.min(s.length - 1, Math.floor((p / 100) * s.length))];
}
```

---

## Lab 3.1 — Callback + đo latency theo `acks` và batching ⭐

**🎯 Mục tiêu:** Gửi 500 message với `acks` = `0` / `1` / `-1` (all), in p50/p99 latency và `baseOffset` trả về; sau đó so sánh 1 message/`send()` với 100 message/`send()` để thấy batching giảm số request.
**🧩 Luyện kỹ năng (liên quan đề):**

- `send()` là async, kết quả về qua Promise/callback (`RecordMetadata`: partition, offset). `acks=0` → **offset = -1**.
- Trục **latency ↔ durability** của `acks` (Java `acks`, kafkajs `acks` per-send).
- Batching: nhiều record cùng partition đi chung 1 request (Java `linger.ms`/`batch.size`; kafkajs = mảng `messages`).

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic 3 partition, RF 3 (min.isr = 2 theo broker).

   ```bash
   kt --create --topic lab31-acks --partitions 3 --replication-factor 3
   kt --describe --topic lab31-acks
   ```
2. Viết `lab31-acks.mjs`.

   ```javascript
   // lab31-acks.mjs — đo latency theo acks
   import { kafka, percentile } from "./kafka.mjs";

   const topic = "lab31-acks";
   const N = 500;
   const producer = kafka.producer();       // Java: enable.idempotence=false ở đây để acks=0/1 hợp lệ
   await producer.connect();

   for (const acks of [0, 1, -1]) {         // Java: acks=0 / acks=1 / acks=all
     const lat = [];
     let lastMeta;
     for (let i = 0; i < N; i++) {
       const t0 = performance.now();
       const [meta] = await producer.send({
         topic,
         acks,                               // kafkajs: per-send; Java: per-producer
         messages: [{ key: `k-${i % 10}`, value: JSON.stringify({ i, acks, ts: Date.now() }) }],
       });
       lat.push(performance.now() - t0);
       lastMeta = meta;
     }
     console.log(
       `acks=${String(acks).padStart(2)}  p50=${percentile(lat, 50).toFixed(2)}ms  ` +
       `p99=${percentile(lat, 99).toFixed(2)}ms  lastBaseOffset=${lastMeta.baseOffset} partition=${lastMeta.partition}`
     );
   }
   await producer.disconnect();
   ```
3. Chạy và đọc kết quả.

   ```bash
   node lab31-acks.mjs
   ```
4. Viết `lab31-batch.mjs` — so sánh 1 msg/request vs 100 msg/request (cùng 1.000 message, `acks=-1`).

   ```javascript
   // lab31-batch.mjs — batching bằng mảng messages
   import { kafka } from "./kafka.mjs";

   const topic = "lab31-acks";
   const producer = kafka.producer();
   await producer.connect();

   let requests = 0;
   producer.on(producer.events.REQUEST, (e) => {       // đếm request thực sự ra broker
     if (e.payload.apiName === "Produce") requests++;
   });

   const msgs = Array.from({ length: 1000 }, (_, i) => ({ key: `k-${i % 10}`, value: `v-${i}` }));

   // (a) 1 message / send()
   requests = 0;
   let t0 = performance.now();
   for (const m of msgs) await producer.send({ topic, acks: -1, messages: [m] });
   console.log(`1 msg/send : ${(performance.now() - t0).toFixed(0)} ms, Produce requests = ${requests}`);

   // (b) 100 message / send() → producer gom theo partition, ít request hơn hẳn
   requests = 0;
   t0 = performance.now();
   for (let i = 0; i < msgs.length; i += 100) {
     await producer.send({ topic, acks: -1, messages: msgs.slice(i, i + 100) });
   }
   console.log(`100 msg/send: ${(performance.now() - t0).toFixed(0)} ms, Produce requests = ${requests}`);

   await producer.disconnect();
   ```

   ```bash
   node lab31-batch.mjs
   ```

### ✅ Kiểm chứng

- Kết quả kiểu (số tuỳ máy): `acks=0 p50≈1ms lastBaseOffset=-1` · `acks=1 p50≈2–4ms` · `acks=-1 p50≈4–8ms` (phải chờ 2 ISR). **`acks=0` luôn cho `baseOffset=-1`** vì không chờ broker.
- Ở `lab31-batch.mjs`: (a) ≈ 1.000 Produce request; (b) ≈ 30 request (10 lô × 3 partition) và nhanh hơn nhiều lần. Đây chính là hiệu ứng `linger.ms`/`batch.size` của Java, chỉ khác cơ chế gom.
- Xác nhận message đã ghi: `koff --topic lab31-acks` (end offset mỗi partition).

### 🧹 Dọn dẹp

```bash
kt --delete --topic lab31-acks
```

### 🧠 Ý nghĩa với đề thi

- "Lowest latency, tolerate loss" → `acks=0` (offset -1, `retries` vô nghĩa). "No loss" → `acks=all` **và** `min.insync.replicas=2`.
- Batching là đòn bẩy throughput số 1: đề hỏi "reduce number of requests" → tăng `linger.ms`/`batch.size`, không phải thêm producer.
- `send()` không block trừ khi chờ metadata lần đầu hoặc buffer đầy (`max.block.ms`).

---

## Lab 3.2 — `kafka-producer-perf-test.sh`: `linger.ms` × `batch.size` × `compression.type`

**🎯 Mục tiêu:** Đo throughput/latency thật của Java producer với 6 cấu hình, điền bảng, rút ra quy luật "batch to + nén = throughput cao, latency tăng nhẹ".
**🧩 Luyện kỹ năng (liên quan đề):**

- Ý nghĩa **số** của `linger.ms` (mặc định 5 ở 4.x), `batch.size` (16.384), `compression.type` (none → lz4/zstd).
- Nén theo **batch** → batch to nén tốt hơn.
- Đọc output perf-test: records/sec, MB/sec, avg latency, 99th latency.

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic 6 partition.

   ```bash
   kt --create --topic lab32-perf --partitions 6 --replication-factor 3
   ```
2. Chạy lần lượt 6 cấu hình (mỗi lần 200.000 record × 1 KB, không giới hạn tốc độ `--throughput -1`). Ghi lại dòng cuối của mỗi lần.

   ```bash
   run() {   # $1 = linger.ms  $2 = batch.size  $3 = compression.type
     echo "=== linger.ms=$1 batch.size=$2 compression.type=$3 ==="
     kperf --topic lab32-perf --num-records 200000 --record-size 1024 --throughput -1 \
       --producer-props bootstrap.servers=$BS acks=all \
         linger.ms=$1 batch.size=$2 compression.type=$3 | tail -1
   }
   run 0  16384  none
   run 50 16384  none
   run 0  262144 none
   run 50 262144 none
   run 50 262144 lz4
   run 50 262144 zstd
   ```
3. Điền bảng (ví dụ số thu được trên laptop; **số của bạn sẽ khác**, quan trọng là **xu hướng**):

   | `linger.ms` | `batch.size` | `compression.type` | records/sec | MB/sec | avg latency (ms) | 99th (ms) |
   |---|---|---|---|---|---|---|
   | 0 | 16384 | none | | | | |
   | 50 | 16384 | none | | | | |
   | 0 | 262144 | none | | | | |
   | 50 | 262144 | none | | | | |
   | 50 | 262144 | lz4 | | | | |
   | 50 | 262144 | zstd | | | | |

4. (Tùy chọn) Thử payload nén được vs không nén được: perf-test sinh payload ngẫu nhiên nên tỉ lệ nén thấp; dùng `--payload-file` với file text lặp để thấy `zstd`/`gzip` giảm MB/sec network mạnh hơn.

### ✅ Kiểm chứng

- Hàng 4 (linger 50 + batch 256 KB) phải có records/sec **cao hơn** hàng 1 (linger 0 + batch 16 KB) và avg latency **cao hơn** (đổi latency lấy throughput).
- Với payload random, `lz4`/`zstd` có thể **không** tăng records/sec đáng kể (CPU nén > lợi ích) — đó là bài học: **nén chỉ lợi khi dữ liệu nén được** (JSON/text).
- Broker log không báo lỗi `NotEnoughReplicas` (min.isr=2 đủ vì 3 broker sống).

### 🧹 Dọn dẹp

```bash
kt --delete --topic lab32-perf
unset -f run
```

### 🧠 Ý nghĩa với đề thi

- Đề "increase throughput" → **tăng `linger.ms`, tăng `batch.size`, bật `compression.type`** (thường lz4/zstd). Đề "reduce latency" → ngược lại.
- `batch.size` là **cận trên**; tăng `batch.size` mà `linger.ms=0` và tốc độ gửi thấp thì batch vẫn nhỏ → phải tăng `linger.ms` cùng.
- 4.0 đổi `linger.ms` mặc định 0 → **5** (KIP-1030); đề cũ ghi 0.

---

## Lab 3.3 — Partitioner: key null vs key, thêm partition (bẫy), custom partitioner

**🎯 Mục tiêu:** Quan sát phân bố partition khi key = null (sticky) và key = `user-N` (murmur2); thấy **cùng key sang partition khác** sau khi tăng số partition; viết custom partitioner đưa key `vip-*` vào partition 0.
**🧩 Luyện kỹ năng (liên quan đề):**

- Thứ tự quyết định partition: chỉ định tay > key hash > sticky.
- **Bẫy thêm partition** phá ordering theo key.
- `Partitioner` interface (Java `partitioner.class`; kafkajs `createPartitioner`).

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic 3 partition và viết `lab33-partitioner.mjs`.

   ```bash
   kt --create --topic lab33-part --partitions 3 --replication-factor 3
   ```

   ```javascript
   // lab33-partitioner.mjs — gửi 1000 msg key null hoặc key user-N, in partition từng key
   import { kafka } from "./kafka.mjs";

   const topic = "lab33-part";
   const mode = process.argv[2] ?? "keyed";        // "null" | "keyed"
   const producer = kafka.producer();               // Partitioners.DefaultPartitioner = murmur2 tương thích Java
   await producer.connect();

   const msgs = Array.from({ length: 1000 }, (_, i) => ({
     key: mode === "null" ? null : `user-${i % 20}`,   // 20 key khác nhau
     value: `m-${i}`,
   }));
   const res = await producer.send({ topic, acks: -1, messages: msgs });
   console.log("partitions used:", res.map((r) => `${r.partition}:+${res.length}`).join(" "));

   // In map key → partition dựa trên message thứ nhất của mỗi key (chỉ với mode keyed)
   if (mode === "keyed") {
     const { Partitioners } = await import("kafkajs");
     const part = Partitioners.DefaultPartitioner();
     const admin = kafka.admin(); await admin.connect();
     const [{ partitions }] = (await admin.fetchTopicMetadata({ topics: [topic] })).topics;
     const partitionMetadata = partitions.map((p) => ({ partitionId: p.partitionId, leader: p.leader }));
     for (let k = 0; k < 20; k++) {
       const key = `user-${k}`;
       console.log(key, "→ partition", part({ topic, partitionMetadata, message: { key } }));
     }
     await admin.disconnect();
   }
   await producer.disconnect();
   ```
2. Gửi key null và xem phân bố bằng end offset từng partition.

   ```bash
   node lab33-partitioner.mjs null
   koff --topic lab33-part          # lab33-part:0:xxx  lab33-part:1:xxx  lab33-part:2:xxx
   ```
3. Gửi keyed và lưu lại bảng `user-k → partition`.

   ```bash
   node lab33-partitioner.mjs keyed | tee before.txt
   ```
4. **Thêm partition** rồi gửi lại → so sánh mapping.

   ```bash
   kt --alter --topic lab33-part --partitions 6
   node lab33-partitioner.mjs keyed | tee after.txt
   diff <(grep '→' before.txt) <(grep '→' after.txt)
   ```
5. Custom partitioner `lab33-custom.mjs`: key `vip-*` luôn vào partition 0, còn lại theo mặc định.

   ```javascript
   // lab33-custom.mjs — custom partitioner (Java: implements Partitioner + partitioner.class)
   import { Partitioners } from "kafkajs";
   import { kafka } from "./kafka.mjs";

   const VipFirstPartitioner = () => {
     const fallback = Partitioners.DefaultPartitioner();
     return ({ topic, partitionMetadata, message }) => {
       const key = message.key?.toString() ?? "";
       if (key.startsWith("vip-")) return 0;                 // partition dành riêng
       return fallback({ topic, partitionMetadata, message });
     };
   };

   const producer = kafka.producer({ createPartitioner: VipFirstPartitioner });
   await producer.connect();
   const res = await producer.send({
     topic: "lab33-part", acks: -1,
     messages: [
       { key: "vip-1", value: "gold" }, { key: "vip-2", value: "platinum" },
       { key: "user-3", value: "normal" }, { key: "user-7", value: "normal" },
     ],
   });
   console.log(res.map((r) => `partition ${r.partition} ← ${r.baseOffset}`));
   await producer.disconnect();
   ```

   ```bash
   node lab33-custom.mjs
   kcc --topic lab33-part --partition 0 --from-beginning --property print.key=true --timeout-ms 5000 | grep vip
   ```

### ✅ Kiểm chứng

- Bước 2: với key null, 1.000 message trong **1 `send()`** thường rơi chủ yếu vào **1–2 partition** (sticky/lô gửi), không rải đều từng message như round-robin — tổng thể nhiều lần gửi mới đều.
- Bước 4: `diff` cho thấy **một số `user-k` đổi partition** (ví dụ `user-4 → 1` thành `user-4 → 4`). Đây là bẫy: message cũ của `user-4` nằm partition 1, message mới nằm partition 4 → **mất ordering theo key**.
- Bước 5: 2 record `vip-*` có `partition 0`; consumer `--partition 0` in ra `vip-1`, `vip-2`.

### 🧹 Dọn dẹp

```bash
kt --delete --topic lab33-part
rm -f before.txt after.txt
```

### 🧠 Ý nghĩa với đề thi

- "Same key must stay in order" → key hash murmur2 mod N, **không thêm partition**; nếu buộc phải scale → topic mới + migrate.
- "Null key, batches too small" → sticky partitioner đã lo (KIP-480/794); tăng `linger.ms` để batch đầy.
- "Route special keys to a dedicated partition" → **custom `Partitioner`** (`partitioner.class`), không phải đổi topic.
- `partitioner.ignore.keys=true` / `RoundRobinPartitioner` phân bố đều nhưng **mất ordering theo key**.

---

## Lab 3.4 — Idempotent producer sống qua lỗi mạng (`docker pause` leader)

**🎯 Mục tiêu:** Bật `idempotent: true`, gửi liên tục 2.000 message có số thứ tự; giữa chừng **pause** container leader của partition rồi **unpause**; consumer đếm được đúng 2.000 message, **không duplicate, không lệch thứ tự**.
**🧩 Luyện kỹ năng (liên quan đề):**

- Idempotence = PID + sequence number, chống duplicate do **retry nội bộ** (Java `enable.idempotence=true`, mặc định).
- Ràng buộc: `acks=all`, `retries>0`, `max.in.flight ≤ 5` (kafkajs: `maxInFlightRequests: 1`).
- Lỗi retriable (`NotLeaderOrFollower`, `NetworkException`, request timeout) được producer tự retry.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic **1 partition** RF 3 (để biết chắc leader) và xem leader.

   ```bash
   kt --create --topic lab34-idem --partitions 1 --replication-factor 3
   kt --describe --topic lab34-idem      # ghi lại Leader: <node id>  (2→kafka-1, 3→kafka-2, 4→kafka-3)
   ```
2. Viết `lab34-idempotent.mjs`.

   ```javascript
   // lab34-idempotent.mjs — idempotent producer + retry qua lỗi mạng
   import { Kafka, logLevel } from "kafkajs";
   import { BROKERS, sleep } from "./kafka.mjs";

   const kafka = new Kafka({
     clientId: "lab34-idem", brokers: BROKERS, logLevel: logLevel.INFO,
     requestTimeout: 5000,                       // Java: request.timeout.ms (ngắn để thấy retry nhanh)
     retry: { initialRetryTime: 300, retries: 30, maxRetryTime: 5000 }, // Java: retry.backoff.ms / retries
   });
   const producer = kafka.producer({
     idempotent: true,                            // Java: enable.idempotence=true (kéo theo acks=all)
     maxInFlightRequests: 1,                      // kafkajs bắt buộc 1; Java cho phép ≤5
   });
   await producer.connect();

   const topic = "lab34-idem";
   const TOTAL = 2000;
   let sent = 0, retriedErrors = 0;
   for (let i = 0; i < TOTAL; i += 50) {
     const messages = Array.from({ length: 50 }, (_, j) => ({ key: "seq", value: String(i + j) }));
     while (true) {
       try {
         await producer.send({ topic, acks: -1, messages });   // acks=all bắt buộc với idempotent
         sent += messages.length;
         break;
       } catch (e) {                                           // chỉ tới đây khi kafkajs đã hết retry nội bộ
         retriedErrors++;
         console.log(`send failed (${e.name}: ${e.message}) — retry lô ${i}`);
         await sleep(1000);
       }
     }
     if (sent % 500 === 0) console.log(`sent ${sent}/${TOTAL}`);
     await sleep(20);
   }
   console.log(`DONE sent=${sent} appErrors=${retriedErrors}`);
   await producer.disconnect();
   ```
3. Viết `lab34-verify.mjs` — đọc lại toàn bộ, kiểm tra duplicate và thứ tự.

   ```javascript
   // lab34-verify.mjs — kiểm tra không duplicate, không lệch thứ tự
   import { kafka } from "./kafka.mjs";

   const consumer = kafka.consumer({ groupId: `lab34-verify-${Date.now()}` });
   await consumer.connect();
   await consumer.subscribe({ topic: "lab34-idem", fromBeginning: true });

   const seen = [];
   const timer = setTimeout(async () => {
     const set = new Set(seen);
     const ordered = seen.every((v, i) => i === 0 || v > seen[i - 1]);
     console.log(`total=${seen.length} unique=${set.size} duplicates=${seen.length - set.size} inOrder=${ordered}`);
     await consumer.disconnect(); process.exit(0);
   }, 8000);

   await consumer.run({
     eachMessage: async ({ message }) => { seen.push(Number(message.value.toString())); timer.refresh(); },
   });
   ```
4. Chạy producer ở terminal 1; khi thấy `sent 500/2000`, ở terminal 2 **pause leader** ~8 giây rồi unpause.

   ```bash
   # Terminal 1
   node lab34-idempotent.mjs

   # Terminal 2 (thay kafka-2 bằng container đang là leader ở bước 1)
   docker pause kafka-2 && sleep 8 && docker unpause kafka-2
   ```
5. Khi producer in `DONE sent=2000`, chạy verify.

   ```bash
   node lab34-verify.mjs
   kt --describe --topic lab34-idem     # leader có thể đã đổi sang broker khác (controller bầu lại)
   ```

### ✅ Kiểm chứng

- Terminal 1 in log kafkajs kiểu `Request Produce timed out` / `The request timed out` / `NOT_LEADER_OR_FOLLOWER` rồi **tự retry**; `appErrors` thường = 0.
- `lab34-verify.mjs`: `total=2000 unique=2000 duplicates=0 inOrder=true`.
- **Đối chứng (tùy chọn):** đổi `idempotent: false` và bỏ `maxInFlightRequests`, lặp lại pause → có thể thấy `duplicates>0` (batch được retry sau khi broker đã ghi nhưng ack bị mất).

### 🧹 Dọn dẹp

```bash
docker unpause kafka-2 2>/dev/null || true
kt --delete --topic lab34-idem
```

### 🧠 Ý nghĩa với đề thi

- Idempotence chống duplicate do **retry của chính producer** (ack mất trên đường về). Không chống app tự gọi `send()` lại.
- Với idempotence, `max.in.flight=5` vẫn giữ order (broker cache 5 batch seq). Đề cũ đòi `=1` là thời chưa có idempotence.
- Leader đổi khi broker chết → `NotLeaderOrFollowerException` (retriable) → producer refresh metadata rồi gửi tới leader mới; app không cần làm gì.

---

## Lab 3.5 — Transactions EOS: consume-transform-produce, commit vs abort ⭐

**🎯 Mục tiêu:** Đọc từ `lab35-in`, biến đổi, ghi vào `lab35-out` và commit offset **trong cùng transaction**; cố tình abort một transaction; chứng minh consumer `read_committed` **không thấy** record của transaction abort/đang mở trong khi `read_uncommitted` **thấy**.
**🧩 Luyện kỹ năng (liên quan đề):**

- `transactional.id`, `initTransactions/begin/send/sendOffsetsToTransaction/commit/abort` (kafkajs `producer.transaction()`).
- `isolation.level=read_committed` + LSO; control marker COMMIT/ABORT; `__transaction_state`.
- EOS chỉ Kafka → Kafka.

**⏱️ ~45 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo 2 topic.

   ```bash
   kt --create --topic lab35-in  --partitions 1 --replication-factor 3
   kt --create --topic lab35-out --partitions 1 --replication-factor 3
   kt --list | grep __transaction_state || echo "(sẽ tự tạo khi có transaction đầu tiên)"
   ```
2. Nạp 10 order vào `lab35-in`.

   ```bash
   for i in $(seq 1 10); do echo "order-$i:{\"id\":$i,\"amount\":$((i*10))}"; done | \
     kcp --topic lab35-in --property parse.key=true --property key.separator=:
   ```
3. Viết `lab35-eos.mjs` — mỗi batch input = 1 transaction; batch chứa `id=7` sẽ **abort** để mô phỏng lỗi xử lý.

   ```javascript
   // lab35-eos.mjs — consume-transform-produce với transactions (EOS trong Kafka)
   import { kafka, sleep } from "./kafka.mjs";

   const IN = "lab35-in", OUT = "lab35-out", GROUP = "lab35-processor";

   const producer = kafka.producer({
     transactionalId: "lab35-processor-p0",   // Java: transactional.id — unique + ổn định theo shard/partition
     idempotent: true,                         // Java: set transactional.id → idempotence tự bật
     maxInFlightRequests: 1,
     transactionTimeout: 60000,                // Java: transaction.timeout.ms (mặc định 60.000)
   });
   const consumer = kafka.consumer({ groupId: GROUP, readUncommitted: false }); // Java: isolation.level=read_committed

   await producer.connect();                    // Java: initTransactions() xảy ra khi gọi transaction() lần đầu
   await consumer.connect();
   await consumer.subscribe({ topic: IN, fromBeginning: true });

   let abortedOnce = false;                     // abort đúng 1 lần để bạn quan sát, lần đọc lại sẽ commit
   await consumer.run({
     autoCommit: false,                         // KHÔNG auto-commit: offset đi chung transaction
     eachBatchAutoResolve: false,               // tự quyết định khi nào coi batch là "đã xử lý"
     eachBatch: async ({ batch, resolveOffset, heartbeat }) => {
       const txn = await producer.transaction();          // Java: beginTransaction()
       try {
         const outMsgs = [];
         let poison = false;
         for (const m of batch.messages) {
           const order = JSON.parse(m.value.toString());
           if (order.id === 7 && !abortedOnce) poison = true; // mô phỏng lỗi nghiệp vụ (chỉ lần đầu)
           outMsgs.push({ key: m.key, value: JSON.stringify({ ...order, total: order.amount * 1.1, txn: true }) });
         }
         await txn.send({ topic: OUT, messages: outMsgs });   // ghi output (chưa commit → read_committed chưa thấy)
         await txn.sendOffsets({                                // Java: sendOffsetsToTransaction(offsets, groupMetadata)
           consumerGroupId: GROUP,
           topics: [{ topic: batch.topic, partitions: [{ partition: batch.partition, offset: (Number(batch.lastOffset()) + 1).toString() }] }],
         });
         if (poison) {
           console.log(`OPEN  txn offsets ${batch.firstOffset()}..${batch.lastOffset()} — giữ 15s, xem 2 console consumer`);
           await sleep(15000);                                 // transaction ĐANG MỞ: read_uncommitted thấy, read_committed không
           console.log("ABORT txn (chứa id=7)");
           await txn.abort();                                  // Java: abortTransaction() → marker ABORT
           abortedOnce = true;
           consumer.seek({ topic: batch.topic, partition: batch.partition, offset: batch.firstOffset() }); // đọc lại batch
           return;                                             // KHÔNG resolveOffset → xử lý lại từ đầu batch
         }
         await txn.commit();                                   // Java: commitTransaction() → marker COMMIT
         resolveOffset(batch.lastOffset());
         console.log(`COMMIT batch ${batch.firstOffset()}..${batch.lastOffset()} (${batch.messages.length} msgs)`);
       } catch (e) {
         console.error("txn error → abort:", e.message);
         if (txn.isActive()) await txn.abort();
       }
       await heartbeat();
     },
   });
   ```

   > Luồng: batch đầu (10 order, có `id=7`) → mở transaction 15 giây → **abort** → `seek` về đầu → đọc lại → lần này **commit**. Vì vậy `lab35-out` cuối cùng có 10 record committed + 10 record aborted (bị `read_committed` lọc bỏ).

4. Mở 2 consumer console **trước** khi chạy processor:

   ```bash
   # Terminal A — read_committed (Java mặc định là read_uncommitted, phải chỉ định)
   kcc --topic lab35-out --from-beginning --property print.key=true \
       --isolation-level read_committed

   # Terminal B — read_uncommitted
   kcc --topic lab35-out --from-beginning --property print.key=true \
       --isolation-level read_uncommitted
   ```
5. Chạy processor ở terminal C.

   ```bash
   node lab35-eos.mjs
   ```
6. Xem transaction state và LSO.

   ```bash
   kt --describe --topic __transaction_state | head -3           # 50 partitions, compact
   docker exec -it kafka-1 /opt/kafka/bin/kafka-transactions.sh --bootstrap-server $BS list
   docker exec -it kafka-1 /opt/kafka/bin/kafka-transactions.sh --bootstrap-server $BS \
     describe --transactional-id lab35-processor-p0
   kcg --describe --group lab35-processor                        # offset đã commit qua sendOffsets
   ```

### ✅ Kiểm chứng

- Trong 15 giây transaction chứa `order-7` đang mở/abort: **Terminal B (`read_uncommitted`) in record ngay**, **Terminal A (`read_committed`) không in gì** — LSO đứng tại đầu transaction đó.
- Sau `abort`: Terminal A **vĩnh viễn không thấy** các record của transaction đó; Terminal B đã in (và không có cách "rút lại") → vì sao downstream phải dùng `read_committed`.
- `kafka-consumer-groups.sh --describe` cho `CURRENT-OFFSET` chỉ nhích **khi commit**, không nhích sau abort (offset đi chung transaction).
- `kafka-transactions.sh describe` cho `TransactionState` (`Ongoing`/`CompleteCommit`/`CompleteAbort`) và `ProducerEpoch`. Chạy `lab35-eos.mjs` lần 2 (cùng `transactionalId`) → epoch **tăng**; nếu tiến trình cũ còn sống nó sẽ nhận `ProducerFencedException` (kafkajs: `PRODUCER_FENCED`).

### 🧹 Dọn dẹp

```bash
# Ctrl+C các terminal A/B/C
kt --delete --topic lab35-in
kt --delete --topic lab35-out
kcg --delete --group lab35-processor
```

### 🧠 Ý nghĩa với đề thi

- Read-process-write exactly-once = **`sendOffsetsToTransaction` + `commitTransaction`** + consumer **`read_committed`** + `enable.auto.commit=false`.
- `transactional.id` phải **ổn định** để epoch fencing hoạt động; random mỗi lần start = mất fencing.
- `read_committed` đọc tới **LSO**; transaction mở lâu → lag tăng giả; coordinator tự abort sau `transaction.timeout.ms` (60 s).
- Nếu output là DB ngoài Kafka → transaction này **không** bảo vệ → idempotent upsert/outbox.

---

## Lab 3.6 — Bảng lỗi thực nghiệm: `RecordTooLarge`, `TimeoutException`, `InvalidTopic`, `ConfigException`

**🎯 Mục tiêu:** Cố tình gây 4 lỗi bằng console producer Java (đúng tên exception như đề), phân loại retriable/fatal và cách sửa.
**🧩 Luyện kỹ năng (liên quan đề):**

- `max.request.size` (client) vs `message.max.bytes` (broker) vs `max.message.bytes` (topic).
- `delivery.timeout.ms` ≥ `linger.ms` + `request.timeout.ms` (`ConfigException`).
- Đọc message lỗi → biết loại lỗi.

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic và file 2 MB.

   ```bash
   kt --create --topic lab36-err --partitions 1 --replication-factor 3
   docker exec -it kafka-1 sh -c "head -c 2000000 /dev/zero | tr '\0' a > /tmp/big.txt; wc -c /tmp/big.txt"
   ```
2. **Lỗi 1a — `RecordTooLargeException` phía client** (vượt `max.request.size`=1 MB mặc định).

   ```bash
   docker exec -it kafka-1 sh -c "/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $BS \
     --topic lab36-err < /tmp/big.txt"
   # → org.apache.kafka.common.errors.RecordTooLargeException: The message is 2000088 bytes when serialized
   #   which is larger than 1048576, which is the value of the max.request.size configuration.
   ```
3. **Lỗi 1b — `RecordTooLargeException` phía broker** (đã nới client, broker `message.max.bytes`=1.048.588 vẫn chặn).

   ```bash
   docker exec -it kafka-1 sh -c "/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $BS \
     --topic lab36-err --producer-property max.request.size=3000000 < /tmp/big.txt"
   # → ERROR ... RecordTooLargeException: The request included a message larger than the max message size
   #   the server will accept.  (mã lỗi MESSAGE_TOO_LARGE, KHÔNG retry)
   ```
4. **Sửa đúng** — nới `max.message.bytes` ở **topic** rồi gửi lại (thành công).

   ```bash
   kt --alter --topic lab36-err --config max.message.bytes=3000000
   docker exec -it kafka-1 sh -c "/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $BS \
     --topic lab36-err --producer-property max.request.size=3000000 < /tmp/big.txt" && echo OK
   koff --topic lab36-err     # end offset = 1
   ```
5. **Lỗi 2 — `ConfigException`** (vi phạm `delivery.timeout.ms` ≥ `linger.ms` + `request.timeout.ms`).

   ```bash
   echo hi | kcp --topic lab36-err \
     --producer-property delivery.timeout.ms=20000 \
     --producer-property linger.ms=5000 \
     --producer-property request.timeout.ms=30000
   # → org.apache.kafka.common.config.ConfigException: delivery.timeout.ms should be equal to or larger
   #   than linger.ms + request.timeout.ms   (producer KHÔNG khởi tạo được)
   ```
6. **Lỗi 3 — `TimeoutException` (Expiring records)**: `delivery.timeout.ms` ngắn + pause **cả 3 broker**.

   ```bash
   docker pause kafka-1 kafka-2 kafka-3
   # producer chạy từ host bằng image apache/kafka, network host để tới localhost:9092
   docker run --rm -i --network host apache/kafka:4.3.1 \
     /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092,localhost:9094,localhost:9096 \
     --topic lab36-err --producer-property delivery.timeout.ms=8000 \
     --producer-property request.timeout.ms=3000 --producer-property max.block.ms=5000 <<< "will-expire"
   # → TimeoutException: Topic lab36-err not present in metadata after 5000 ms  (max.block.ms — chưa có metadata)
   #   hoặc: Expiring 1 record(s) for lab36-err-0: 8xxx ms has passed since batch creation (delivery.timeout.ms)
   docker unpause kafka-1 kafka-2 kafka-3
   ```
7. **Lỗi 4 — `InvalidTopicException`** (tên topic không hợp lệ).

   ```bash
   echo hi | kcp --topic 'bad topic!'
   # → org.apache.kafka.common.errors.InvalidTopicException: Invalid topics: [bad topic!]  (fatal, không retry)
   ```
8. Điền bảng tổng kết:

   | Lỗi | Xuất hiện ở đâu | Retriable? | Config/sửa |
   |---|---|---|---|
   | `RecordTooLargeException` (client) | ném ngay tại `send()` (Future fail) | ❌ | `max.request.size` |
   | `RecordTooLargeException` (broker, `MESSAGE_TOO_LARGE`) | callback | ❌ | `message.max.bytes` (broker) / `max.message.bytes` (topic) + `replica.fetch.max.bytes` |
   | `ConfigException` | lúc `new KafkaProducer` | ❌ (khởi tạo) | `delivery.timeout.ms` ≥ `linger.ms` + `request.timeout.ms` |
   | `TimeoutException` (metadata) | `send()` block hết `max.block.ms` | — | broker up / `max.block.ms` |
   | `TimeoutException` (Expiring records) | callback sau `delivery.timeout.ms` | (đã retry hết) | broker/ISR; `delivery.timeout.ms` |
   | `InvalidTopicException` | callback/ném | ❌ | tên topic hợp lệ `[a-zA-Z0-9._-]`, ≤ 249 ký tự |
   | `NotLeaderOrFollower` / `NotEnoughReplicas` / `NetworkException` (Lab 3.4) | callback nội bộ | ✅ tự retry | không cần |

### ✅ Kiểm chứng

- Bạn nhìn thấy **đúng tên exception** 4 loại trên terminal; bước 4 gửi thành công sau khi nới `max.message.bytes` ở topic.
- Nhớ: nới `max.request.size` **không đủ**; nới `message.max.bytes`/`max.message.bytes` mà **không** nới `max.request.size` cũng không đủ (lỗi 1a).

### 🧹 Dọn dẹp

```bash
docker unpause kafka-1 kafka-2 kafka-3 2>/dev/null || true
kt --delete --topic lab36-err
docker exec -it kafka-1 rm -f /tmp/big.txt
```

### 🧠 Ý nghĩa với đề thi

- Đề "record 2 MB rejected" → chỉnh **cả** client `max.request.size` **và** broker/topic `message.max.bytes`/`max.message.bytes` (+ `replica.fetch.max.bytes`, consumer `max.partition.fetch.bytes`), hoặc claim-check.
- `ConfigException` lúc khởi tạo là bẫy số: kiểm tra bất đẳng thức timeout trước khi chọn đáp án.
- `TimeoutException "Expiring N record(s)"` = `delivery.timeout.ms` hết, **không** phải `request.timeout.ms`; nguyên nhân gốc thường là broker/ISR.

---

> ✅ Xong 6 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist) và làm tiếp [bộ câu hỏi luyện tập](questions.md) — tuần này không có checkpoint nhưng mini-mock FUND+DEV ở Tuần 4 sẽ hỏi lại toàn bộ producer.
