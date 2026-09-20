# 🧪 Hands-on Labs — Tuần 4: Deployment Architecture (sizing · rack · multi-DC · DR)

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab (trừ khi lab sau nói "giữ").
> ⚙️ Yêu cầu chung: Docker Desktop (hoặc Docker Engine + Compose v2), **Node.js 24**, ~6 GB RAM trống (4 container cluster A + 1 broker thêm ở Lab 4.5 + 1 container cluster B ở Lab 4.4). Tổng ~3.5h.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung

### 1) Khởi động cluster chuẩn (KHÔNG định nghĩa lại compose gốc)

Hai file compose chuẩn đã dựng ở [CCDAK Tuần 1 — Lab 1.1 / 1.2](../../../CCDAK/study-plan/week-01/labs.md). Tuần này dùng **`docker-compose.cluster.yml`**: container `controller` (`node.id` 1, `process.roles=controller`) + `kafka-1` (2), `kafka-2` (3), `kafka-3` (4); host port **9092 / 9094 / 9096**; listener nội bộ **`kafka-1:19092`**; `default.replication.factor=3`, `min.insync.replicas=2`.

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d
docker compose -f docker-compose.cluster.yml ps        # 4 container running
mkdir -p ~/kafka-labs/week-04
```

Mọi phần **thêm** của tuần này nằm trong **file override riêng** (`docker-compose.rack.yml`, `docker-compose.broker4.yml`) hoặc **project riêng** (`docker-compose.cluster-b.yml` cho cluster B). Không sửa `docker-compose.cluster.yml`.

### 2) Alias CLI — chạy từ container `controller`

Alias `kt`/`kcp`/`kcc`/`kcg`/`kcfg`/`kq`/`ksh` **giữ nguyên định nghĩa Tuần 1** (đọc `$KAFKA_CTR` và `$KAFKA_BS`). Tuần này CLI chạy từ container `controller` — cùng image, cùng network, và **không** bị dính `JMX_PORT` mà Lab 4.3 gắn vào broker.

```bash
export KAFKA_CTR=controller
export KAFKA_BS=kafka-1:19092,kafka-2:19092,kafka-3:19092    # bootstrap cả 3 để không phụ thuộc broker đang tắt
kt --list                                                    # kiểm tra kết nối (có thể rỗng)

# Alias thêm riêng cho tuần này
alias kperf='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-producer-perf-test.sh'
alias krp='docker exec -i  $KAFKA_CTR /opt/kafka/bin/kafka-reassign-partitions.sh --bootstrap-server $KAFKA_BS'  # -i (không -t) để output không dính \r khi tee ra file
alias kle='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-leader-election.sh   --bootstrap-server $KAFKA_BS'
alias kfeat='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-features.sh        --bootstrap-server $KAFKA_BS'
alias koff='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-get-offsets.sh      --bootstrap-server $KAFKA_BS'
alias kldir='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-log-dirs.sh        --bootstrap-server $KAFKA_BS'
```

> 🧠 **Bẫy vận hành thật (cũng là bẫy đề):** `JMX_PORT` và `KAFKA_OPTS` áp cho **mọi** script trong `bin/`, không riêng tiến trình broker. Chạy `kafka-topics.sh` ngay trên máy broker đang export `JMX_PORT=9999` sẽ chết với `Address already in use`. Cách sửa: chạy tool từ máy khác, hoặc `JMX_PORT= KAFKA_OPTS= kafka-topics.sh ...`.

### 3) Node.js

```bash
cd ~/kafka-labs/week-04
node -v                                                             # v24.x
node -e "import('kafkajs').then(() => console.log('kafkajs OK'))"    # resolve từ ~/kafka-labs/node_modules
```

---

## Lab 4.1 — Sizing trên giấy rồi kiểm bằng thực nghiệm ⭐

**🎯 Mục tiêu:** Nhận một đề bài sizing, tính **số partition · dung lượng disk · số broker** hoàn toàn trên giấy bằng công thức, rồi **đo thực tế** trên cluster để xem giả định của mình lệch bao nhiêu, và rút ra vì sao đề luôn bắt cộng biên dự phòng.
**🧩 Luyện kỹ năng (liên quan đề):**

- Công thức **`max(t/p, t/c)`** và lý do `c` (consumer) hầu như luôn là cái chặn.
- Công thức disk `throughput ghi × retention × RF × 1.2` và chỗ tiered storage cắt vào.
- Đọc `kafka-log-dirs.sh` để biết dung lượng **thật** một partition chiếm, kể cả overhead.
- Kiểm tra trần thực tế: `2000–4000` partition/broker, và sizing theo nguyên tắc **mất 1 broker vẫn đủ công suất**.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. **Đề bài (làm trên giấy trước khi gõ lệnh nào).**

   > Topic `payments`. Throughput ghi đỉnh **60 MB/s**. Retention **7 ngày**. `replication.factor = 3`, `min.insync.replicas = 2`. Một consumer instance xử lý được **12 MB/s**. Đo được producer đạt **50 MB/s** trên một partition. Máy broker: 12 × 1 TB (dùng được ~11 TB/broker sau khi trừ OS và chỗ trống cho compaction).
   >
   > Hỏi: bao nhiêu **partition**, bao nhiêu **TB** disk toàn cluster, bao nhiêu **broker**?

   Lời giải mẫu — tự làm trước rồi mới so:

   ```text
   PARTITION
     t = 60 MB/s ; p = 50 MB/s ; c = 12 MB/s
     max(t/p, t/c) = max(60/50, 60/12) = max(1.2, 5) = 5  -> làm tròn lên 5
     biên tăng trưởng x2 (12-24 tháng)                    -> 10
     làm tròn lên số "đẹp" chia hết cho số broker         -> 12 partition
     => c (consumer) quyết định, không phải p. Ghi nhớ: KHÔNG giảm được partition.

   DISK
     1 bản  = 60e6 B/s x 604800 s          = 3.6288e13 B = 36.3 TB
     x RF 3                                = 108.9 TB
     x 1.2 dự phòng                        = 130.6 TB toàn cluster

   BROKER
     130.6 TB / 11 TB mỗi broker           = 11.9  -> 12 broker về mặt dung lượng
     kiểm tra N-1: mất 1 broker thì 11 broker phải gánh 130.6 TB -> 11.9 TB/broker > 11 TB  => KHÔNG đủ
     => 13 broker (mất 1 còn 12 x 11 = 132 TB >= 130.6 TB)
     kiểm tra partition/broker: 12 partition x RF 3 = 36 replica / 13 broker ~ 3 replica  -> xa trần 2000-4000, OK

   NẾU BẬT TIERED STORAGE (local.retention.ms = 1 ngày)
     disk local = 60e6 x 86400 x 3 x 1.2   = 18.7 TB toàn cluster  -> 2-3 broker là đủ về dung lượng
     (phần 7 ngày vẫn còn, nhưng nằm ở remote tier)
   ```
2. **Đo `p` thật** — throughput một partition trên cluster của bạn.

   ```bash
   kt --create --topic sizing-1p --partitions 1 --replication-factor 3
   kperf --topic sizing-1p --num-records 300000 --record-size 1024 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 acks=all compression.type=none
   ```
   Output mẫu (máy laptop, số của bạn sẽ khác):
   ```
   300000 records sent, 61856.1 records/sec (60.41 MB/sec), 212.34 ms avg latency, 883.00 ms max latency
   ```
   > 📌 Đây chính là `p`. Đổi `compression.type=lz4` rồi chạy lại: `p` tăng rõ — **compression làm đổi kết quả sizing**, nên đề luôn nói "đo được", không đưa hằng số.
3. **Đo overhead trên disk** — 1024 byte payload chiếm bao nhiêu byte thật.

   ```bash
   kldir --topic-list sizing-1p --describe | python3 -m json.tool | grep -E '"partition"|"size"'
   ```
   Output mẫu (xuất hiện 3 lần — một lần cho mỗi broker giữ replica):
   ```
           "partition": "sizing-1p-0",
           "size": 331350016,
   ```
   > 📌 `300.000 × 1024 byte = 307.200.000 byte` payload, nhưng trên đĩa là **331.350.016 byte** → **overhead ~8%** (header record, CRC, timestamp, index). Đây là lý do công thức disk phải có hệ số dự phòng, và là lý do "tính chay theo payload" luôn thiếu.
   ```bash
   # Cùng con số nhưng nhìn theo từng broker (thấy cả 3 replica đều chiếm chỗ)
   kldir --topic-list sizing-1p --describe | python3 -c "
   import json,sys
   d=json.load(sys.stdin)
   for b in d['brokers']:
       tot=sum(p['size'] for ld in b['logDirs'] for p in ld['partitions'])
       print(f\"broker {b['broker']}: {tot/1024/1024:.1f} MiB\")"
   ```
   Cả **3** broker đều báo dung lượng gần bằng nhau → đó là ý nghĩa của **× RF** trong công thức disk.
4. **Kiểm nguyên tắc "mất 1 broker vẫn đủ"** bằng cách nhìn phân bố hiện tại.

   ```bash
   kt --create --topic sizing-12p --partitions 12 --replication-factor 3
   kt --describe --topic sizing-12p | awk '/Partition:/{print $6}' | sort | uniq -c
   # 4 kafka-? ... mỗi broker làm leader 4 partition  -> mất 1 broker thì 2 broker còn lại gánh 6 partition mỗi cái (+50% tải)
   ```
5. **Đối chiếu số giấy với số đo** và ghi vào sổ: `p` đo được bao nhiêu, overhead disk bao nhiêu phần trăm, và nếu dùng `p` đo được thì số partition có đổi không (gợi ý: không, vì `c` mới là cái chặn).

### ✅ Kiểm chứng

- Bạn viết ra được **12 partition / ~131 TB / 13 broker** (hoặc con số gần đó) **trước khi** chạy lệnh nào, và giải thích được vì sao `c` quyết định chứ không phải `p`.
- `kafka-producer-perf-test.sh` trên topic 1 partition cho một con số MB/sec cụ thể — đó là `p` của môi trường bạn.
- `kafka-log-dirs.sh` cho thấy **cả 3 broker** đều chiếm dung lượng tương đương → hệ số RF trong công thức là có thật, không phải lý thuyết.
- Với `local.retention.ms` 1 ngày, phép tính disk giảm **7 lần** — bạn nêu được đúng con số này.

### 🧹 Dọn dẹp

```bash
kt --delete --topic sizing-1p
kt --delete --topic sizing-12p
```

### 🧠 Ý nghĩa với đề thi

- Đề CCAAK cho `t`, `p`, `c` rồi hỏi số partition → luôn là **`max(t/p, t/c)`**, và đáp án đúng gần như luôn xuất phát từ **`t/c`**.
- Đề cho throughput + retention + RF rồi hỏi disk → nhân **cả ba**, đừng quên RF. Quên RF là phương án nhiễu kinh điển (chia 3 lần con số đúng).
- Hỏi "bao nhiêu broker" mà đề có chữ *"vẫn phục vụ được khi mất một broker"* → tính theo **N-1**, không phải N.
- Thấy "retention 1 năm nhưng disk broker đắt" → **tiered storage**, và nhớ rằng nó chỉ cắt phần **local**.

---

## Lab 4.2 — `broker.rack`: rải replica qua rack, rồi **tắt cả một rack** ⭐ (gây hỏng rồi sửa)

**🎯 Mục tiêu:** Gán rack cho 3 broker theo **hai cách khác nhau**, quan sát replica placement đổi ra sao, rồi tắt **cả một rack** ở từng cách để thấy một cách vẫn ghi được còn cách kia thì `NotEnoughReplicas` — và biết đó là lỗi **thiết kế rack**, không phải lỗi Kafka.
**🧩 Luyện kỹ năng (liên quan đề):**

- `broker.rack` là **read-only** → đổi phải restart broker.
- Quy tắc `min(#racks, replication-factor)`: RF 3 trên 3 rack an toàn, RF 3 trên **2** rack thì một rack giữ 2 replica.
- Đọc triệu chứng đúng thứ tự: `--under-replicated-partitions` → `--under-min-isr-partitions` → `--unavailable-partitions`.
- Khôi phục mà **không** hạ `min.insync.replicas` trong lúc hoảng loạn.

**⏱️ ~40 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo file override gán rack **cân** (mỗi broker một rack) và bật sẵn `replica.selector.class` cho Lab 4.3, cộng `JMX_PORT` để Lab 4.3 đọc metric.

   ```yaml
   # ~/kafka-labs/docker-compose.rack.yml — override: broker.rack + RackAwareReplicaSelector + JMX
   # Dùng chồng lên docker-compose.cluster.yml:
   #   docker compose -f docker-compose.cluster.yml -f docker-compose.rack.yml up -d
   services:
     kafka-1:
       environment:
         KAFKA_BROKER_RACK: rack-a
         KAFKA_REPLICA_SELECTOR_CLASS: org.apache.kafka.common.replica.RackAwareReplicaSelector
         JMX_PORT: 9999
     kafka-2:
       environment:
         KAFKA_BROKER_RACK: rack-b
         KAFKA_REPLICA_SELECTOR_CLASS: org.apache.kafka.common.replica.RackAwareReplicaSelector
         JMX_PORT: 9999
     kafka-3:
       environment:
         KAFKA_BROKER_RACK: rack-c
         KAFKA_REPLICA_SELECTOR_CLASS: org.apache.kafka.common.replica.RackAwareReplicaSelector
         JMX_PORT: 9999
   ```

   > ⚠️ Compose **merge** khối `environment` của override vào service gốc, không xoá biến cũ — nên `KAFKA_NODE_ID`, listener… của `docker-compose.cluster.yml` vẫn còn nguyên.

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.rack.yml up -d
   docker exec controller /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server kafka-1:19092 | grep -E "^kafka-[0-9]"
   ```
   Output mẫu — rack giờ hiện ra trong metadata:
   ```
   kafka-1:19092 (id: 2 rack: rack-a) -> ...
   kafka-2:19092 (id: 3 rack: rack-b) -> ...
   kafka-3:19092 (id: 4 rack: rack-c) -> ...
   ```
2. Tạo topic RF 3 và xác nhận **mỗi partition trải đủ 3 rack**.

   ```bash
   kt --create --topic rack-balanced --partitions 6 --replication-factor 3
   kt --describe --topic rack-balanced
   ```
   ```bash
   # Ánh xạ replica id -> rack và kiểm tra tự động
   docker exec controller bash -lc '
   /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 --describe --topic rack-balanced |
   awk "/Partition:/ {print \$4, \$8}"' | while read p reps; do
     racks=$(echo "$reps" | tr ',' '\n' | sed 's/2/rack-a/;s/3/rack-b/;s/4/rack-c/' | sort -u | tr '\n' ' ')
     echo "partition $p -> $racks"
   done
   ```
   Output mong đợi: **mọi** partition in ra đủ `rack-a rack-b rack-c`.
3. **Tắt một rack (rack-c = kafka-3)** trong lúc producer đang ghi, và đọc triệu chứng.

   ```bash
   # Terminal 2 — producer chạy liên tục
   cat > ~/kafka-labs/week-04/rack-producer.mjs <<'MJSEOF'
   import { Kafka, logLevel } from "kafkajs";
   const topic = process.env.TOPIC ?? "rack-balanced";
   const kafka = new Kafka({
     clientId: "rack-producer",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.ERROR,
     retry: { initialRetryTime: 300, retries: 5, maxRetryTime: 3000 },
   });
   const producer = kafka.producer({ idempotent: true, maxInFlightRequests: 1 });
   await producer.connect();
   let i = 0, ok = 0, fail = 0;
   const timer = setInterval(async () => {
     const n = ++i;
     try { await producer.send({ topic, acks: -1, messages: [{ key: `k${n % 6}`, value: `msg-${n}` }] }); ok++; }
     catch (e) { fail++; console.log(`FAIL msg-${n}: ${e.name}: ${e.message}`); }
     if (n % 10 === 0) console.log(`ok=${ok} fail=${fail}`);
   }, 300);
   process.on("SIGINT", async () => { clearInterval(timer); console.log(`TOTAL sent=${i} ok=${ok} fail=${fail}`); await producer.disconnect(); process.exit(0); });
   MJSEOF
   cd ~/kafka-labs/week-04 && node rack-producer.mjs
   ```
   ```bash
   # Terminal 1 — tắt cả rack-c
   docker stop kafka-3
   kt --describe --under-replicated-partitions            # 6 partition URP
   kt --describe --under-min-isr-partitions               # RỖNG — ISR còn 2 >= min.isr 2
   kt --describe --unavailable-partitions                 # RỖNG — mọi partition vẫn có leader
   ```
   Terminal 2: `fail=0` — **vẫn ghi được**. Đây là kết quả đúng của rack cân với RF 3 / 3 rack.
   ```bash
   docker start kafka-3
   until [ "$(kt --describe --under-replicated-partitions | grep -c 'Partition:')" = "0" ]; do echo "chờ URP về 0..."; sleep 5; done
   ```
4. **GÂY HỎNG — thiết kế rack lệch.** Gán `kafka-1` và `kafka-2` **cùng** `rack-a`, `kafka-3` ở `rack-b`. Đây chính là tình huống "RF 3 trên 2 rack".

   ```yaml
   # ~/kafka-labs/docker-compose.rack-bad.yml — CỐ TÌNH SAI: 2 broker cùng rack
   services:
     kafka-1:
       environment: { KAFKA_BROKER_RACK: rack-a }
     kafka-2:
       environment: { KAFKA_BROKER_RACK: rack-a }
     kafka-3:
       environment: { KAFKA_BROKER_RACK: rack-b }
   ```
   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.rack.yml -f docker-compose.rack-bad.yml up -d
   kt --create --topic rack-skewed --partitions 6 --replication-factor 3
   kt --describe --topic rack-skewed
   ```
   Đọc cột `Replicas`: mọi partition đều có **2 replica nằm trong `{2,3}` (rack-a)** và 1 replica là `4` (rack-b) — vì `min(#racks, RF) = min(2, 3) = 2`, Kafka chỉ hứa trải **2** rack.
5. **Tắt cả rack-a** (2 broker cùng lúc) trong lúc producer ghi vào `rack-skewed`.

   ```bash
   # Terminal 2
   TOPIC=rack-skewed node ~/kafka-labs/week-04/rack-producer.mjs
   # Terminal 1
   docker stop kafka-1 kafka-2
   kt --describe --topic rack-skewed --under-min-isr-partitions
   ```
   Terminal 2 báo lỗi ngay:
   ```
   FAIL msg-41: KafkaJSProtocolError: Messages are rejected since there are fewer in-sync replicas than required
   ```
   (tương ứng `org.apache.kafka.common.errors.NotEnoughReplicasException` ở phía Java)
   ```bash
   docker logs kafka-3 2>&1 | grep -iE "NotEnoughReplicas|below required minimum" | tail -3
   ```
6. **SỬA.** Thứ tự đúng: khôi phục rack trước, **không** hạ `min.insync.replicas`.

   ```bash
   docker start kafka-1 kafka-2
   until [ "$(kt --describe --under-replicated-partitions | grep -c 'Partition:')" = "0" ]; do echo "chờ URP về 0..."; sleep 5; done
   kt --describe --under-min-isr-partitions      # rỗng trở lại; Terminal 2 tự hết FAIL
   ```
   Sửa **gốc rễ**: trả rack về cân (bỏ file `rack-bad`) rồi rải lại replica của topic cũ.
   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.rack.yml up -d     # bỏ -f docker-compose.rack-bad.yml
   docker exec controller bash -lc 'echo "{\"version\":1,\"topics\":[{\"topic\":\"rack-skewed\"}]}" > /tmp/move.json'
   krp --topics-to-move-json-file /tmp/move.json --broker-list "2,3,4" --generate | tee ~/kafka-labs/week-04/rack-gen.txt
   awk '/^Proposed partition reassignment/{f=1;next} f && NF' ~/kafka-labs/week-04/rack-gen.txt > ~/kafka-labs/week-04/rack-fix.json
   docker cp ~/kafka-labs/week-04/rack-fix.json controller:/tmp/rack-fix.json
   krp --reassignment-json-file /tmp/rack-fix.json --execute
   krp --reassignment-json-file /tmp/rack-fix.json --verify
   kt --describe --topic rack-skewed             # giờ mỗi partition trải rack-a / rack-b / rack-c
   ```

### ✅ Kiểm chứng

- Bước 1: `kafka-broker-api-versions.sh` in `rack: rack-a/b/c` — trước khi đặt `broker.rack` nó in `rack: null`.
- Bước 2: **mọi** partition của `rack-balanced` trải đủ 3 rack.
- Bước 3: tắt 1 rack → **URP > 0 nhưng `--under-min-isr-partitions` rỗng** và producer `fail=0`.
- Bước 4: `rack-skewed` có 2 replica cùng rack-a ở **mọi** partition — đúng như `min(2,3) = 2`.
- Bước 5: tắt rack-a → producer báo lỗi "fewer in-sync replicas than required" **ngay lập tức**; `--under-min-isr-partitions` liệt kê cả 6 partition.
- Bước 6: sau khi start lại và reassign, `--under-min-isr-partitions` rỗng và replica lại trải 3 rack.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
kt --delete --topic rack-skewed
# GIỮ topic rack-balanced và GIỮ override docker-compose.rack.yml — Lab 4.3 dùng lại
rm -f docker-compose.rack-bad.yml ~/kafka-labs/week-04/rack-gen.txt ~/kafka-labs/week-04/rack-fix.json
```

### 🧠 Ý nghĩa với đề thi

- Đề hỏi "cluster phải sống sót khi **mất một rack**" → điều kiện là **số rack ≥ RF** (hoặc ít nhất đủ để không rack nào giữ ≥ 2 replica), chứ không phải tăng RF.
- **RF 4 trên 3 rack không tốt hơn RF 3**: vẫn có một rack giữ 2 replica, mà tốn thêm 33% disk và băng thông replication.
- Rack **lệch số broker** → rack ít broker gánh nhiều replica hơn (docs nói thẳng). Khuyến nghị: **số broker mỗi rack bằng nhau**.
- Triệu chứng phân biệt: `UnderReplicatedPartitions` > 0 = *đang thiếu bản sao nhưng vẫn ghi được*; `UnderMinIsrPartitionCount` > 0 = **producer `acks=all` đang bị chặn**; `OfflinePartitionsCount` > 0 = *không còn leader*.
- Trong sự cố, **không hạ `min.insync.replicas`** — đó là phương án "đúng nhưng quá tay" mà đề luôn cài.

---

## Lab 4.3 — Follower fetching: `client.rack` + `RackAwareReplicaSelector`

**🎯 Mục tiêu:** Chứng minh bằng metric rằng consumer đặt `client.rack` đúng sẽ được **follower cùng rack** phục vụ chứ không phải leader, và consumer không đặt `client.rack` vẫn đọc từ leader.
**🧩 Luyện kỹ năng (liên quan đề):**

- Bộ ba `broker.rack` + `replica.selector.class` + `client.rack`, thiếu 1 là vô hiệu.
- Đọc metric `kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec` — **không** tính traffic replication (cái đó là `ReplicationBytesOutPerSec`), nên tăng ở broker nào nghĩa là **client** đang đọc ở broker đó.
- Hiểu vì sao follower fetching giảm **chi phí**, không giảm latency ghi.

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 4.2 (override `docker-compose.rack.yml` đang chạy, rack cân, topic `rack-balanced` còn đó).

### Các bước

1. Xác nhận `replica.selector.class` đã có hiệu lực và tìm **leader** của một partition cụ thể.

   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 --all | grep -i "replica.selector.class"
   # replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector sensitive=false synonyms={STATIC_BROKER_CONFIG:...}

   kt --create --topic ff-demo --partitions 1 --replication-factor 3
   kt --describe --topic ff-demo
   # Topic: ff-demo  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3,4
   ```
   Ghi lại: **leader = broker 2 (kafka-1, rack-a)**; follower có broker 3 (kafka-2, **rack-b**) và broker 4 (kafka-3, **rack-c**). Nếu leader của bạn khác, đổi rack tương ứng ở các bước sau.
2. Bơm ~200 MB dữ liệu để traffic đọc đủ lớn cho metric nhìn thấy rõ.

   ```bash
   kperf --topic ff-demo --num-records 200000 --record-size 1024 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 acks=all
   ```
3. Viết hàm đọc `BytesOutPerSec` của từng broker qua JMX (chạy từ container `controller`, nơi **không** có `JMX_PORT`).

   ```bash
   cat > ~/kafka-labs/week-04/bytesout.sh <<'SHEOF'
   #!/usr/bin/env bash
   # In tổng BytesOutPerSec (Count) của topic ff-demo trên từng broker
   for h in kafka-1 kafka-2 kafka-3; do
     v=$(docker exec controller /opt/kafka/bin/kafka-run-class.sh org.apache.kafka.tools.JmxTool \
           --jmx-url "service:jmx:rmi:///jndi/rmi://${h}:9999/jmxrmi" \
           --object-name 'kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec,topic=ff-demo' \
           --attributes Count --one-time 2>/dev/null | tail -1 | awk -F, '{print $NF}')
     printf "%-8s BytesOutPerSec.Count = %s\n" "$h" "${v:-0}"
   done
   SHEOF
   chmod +x ~/kafka-labs/week-04/bytesout.sh
   ~/kafka-labs/week-04/bytesout.sh
   ```
   > ⚠️ Cú pháp cờ của `JmxTool` đổi giữa các bản (`--one-time` vs `--one-time true`). Nếu lệnh trên không ra số, chạy `docker exec controller /opt/kafka/bin/kafka-run-class.sh org.apache.kafka.tools.JmxTool --help` rồi chỉnh. Phương án dự phòng không cần JMX: bật `docker stats` và nhìn **NET I/O** của từng container trong lúc consumer chạy — broker phục vụ sẽ tăng rõ.
4. **Đọc KHÔNG có `client.rack`** (mặc định) — kỳ vọng leader gánh hết.

   ```bash
   ~/kafka-labs/week-04/bytesout.sh > /tmp/before.txt
   docker exec controller /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-1:19092 \
     --topic ff-demo --from-beginning --max-messages 200000 > /dev/null
   ~/kafka-labs/week-04/bytesout.sh > /tmp/after-noRack.txt
   paste /tmp/before.txt /tmp/after-noRack.txt
   ```
   Kỳ vọng: **chỉ `kafka-1` (leader)** tăng ~200 MB; `kafka-2`/`kafka-3` gần như không đổi.
5. **Đọc CÓ `client.rack=rack-c`** — kỳ vọng `kafka-3` gánh.

   ```bash
   ~/kafka-labs/week-04/bytesout.sh > /tmp/before2.txt
   docker exec controller /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-1:19092 \
     --topic ff-demo --from-beginning --max-messages 200000 \
     --consumer-property client.rack=rack-c > /dev/null
   ~/kafka-labs/week-04/bytesout.sh > /tmp/after-rackC.txt
   paste /tmp/before2.txt /tmp/after-rackC.txt
   ```
   Kỳ vọng: **`kafka-3` (rack-c, follower)** tăng ~200 MB; leader `kafka-1` gần như không đổi.
6. **Gỡ một mảnh để thấy nó vô hiệu.** Bỏ `replica.selector.class` khỏi broker, giữ nguyên `client.rack` của consumer.

   ```bash
   cat > ~/kafka-labs/docker-compose.noselector.yml <<'YMLEOF'
   services:
     kafka-1: { environment: { KAFKA_REPLICA_SELECTOR_CLASS: "" } }
     kafka-2: { environment: { KAFKA_REPLICA_SELECTOR_CLASS: "" } }
     kafka-3: { environment: { KAFKA_REPLICA_SELECTOR_CLASS: "" } }
   YMLEOF
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.rack.yml -f docker-compose.noselector.yml up -d
   # chờ URP về 0 rồi lặp lại bước 5 -> lần này LEADER lại gánh, dù client.rack vẫn đặt
   ```
   Xong thì trả lại:
   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.rack.yml up -d
   rm -f docker-compose.noselector.yml
   ```

### ✅ Kiểm chứng

- Bước 1: `kafka-configs.sh --all` in đúng `replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector`.
- Bước 4: chỉ broker **leader** tăng `BytesOutPerSec`.
- Bước 5: broker ở **rack khớp `client.rack`** tăng, leader gần như đứng yên — đây là bằng chứng follower fetching hoạt động.
- Bước 6: bỏ `replica.selector.class` → hành vi quay về leader, **dù `client.rack` vẫn đặt**. Đó là ý nghĩa "thiếu 1 mảnh là vô hiệu".
- Trong suốt lab, mọi lần **produce** đều đi tới leader — không có cách nào để producer ghi vào follower.

### 🧹 Dọn dẹp

```bash
kt --delete --topic ff-demo
rm -f /tmp/before.txt /tmp/after-noRack.txt /tmp/before2.txt /tmp/after-rackC.txt
# GIỮ docker-compose.rack.yml (Lab 4.5 và 4.6 dùng lại cluster này)
```

### 🧠 Ý nghĩa với đề thi

- Đề mô tả *"consumer ở AZ khác leader, hoá đơn cross-AZ cao"* → đáp án là **đủ 3 mảnh** KIP-392. Phương án chỉ nêu `client.rack` là **thiếu**.
- Không có config nào tên `fetch.from.follower` — đó là phương án bịa mà đề hay cài.
- Follower chỉ trả tới **high watermark** → không có chuyện đọc được dữ liệu chưa commit; đổi lại có thể **chậm hơn leader một nhịp fetch**.
- Consumer quay lại leader sau `metadata.max.age.ms` (**300000** ms) hoặc khi follower trả lỗi.

---

## Lab 4.4 — MirrorMaker 2 giữa 2 cluster local ⭐

**🎯 Mục tiêu:** Dựng **cluster B** 1 node (`kafka-b`, host `localhost:9192`) chung Docker network với cluster A; viết `mm2.properties` đầy đủ; chạy `connect-mirror-maker.sh` (dedicated mode); kiểm chứng ở B có **`A.orders`**, **`heartbeats`**, **`A.checkpoints.internal`**; xác nhận **offset consumer group đã được dịch**; rồi đổi sang **`IdentityReplicationPolicy`** và giải thích vì sao topic mới chỉ có record từ đó về sau.
**🧩 Luyện kỹ năng (liên quan đề):**

- 3 connector và vai trò từng cái; flow **mặc định tắt**.
- `DefaultReplicationPolicy` (`{source}.{topic}`, chống loop) vs `IdentityReplicationPolicy` (giữ tên, chỉ active-passive/migration).
- Offset translation qua checkpoint topic và `sync.group.offsets.enabled`.
- `groups.exclude` mặc định loại **console consumer** — bẫy lab kinh điển.

**⏱️ ~45 phút** · **Yêu cầu trước:** Cluster A đang chạy; `KAFKA_CTR=controller`.

### Các bước

1. Tạo `~/kafka-labs/docker-compose.cluster-b.yml` (project riêng, join network của cluster A).

   ```yaml
   # ~/kafka-labs/docker-compose.cluster-b.yml — cluster B: 1 node KRaft combined, đích cho MM2
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
         CLUSTER_ID: "5L6g3nShT-eMCtK--X86sw"          # KHÁC cluster A
         KAFKA_NODE_ID: 1
         KAFKA_PROCESS_ROLES: broker,controller        # combined: chỉ dev/lab
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
   docker network ls | grep kafka-labs_default          # phải có; tên khác thì sửa dòng name:
   docker compose -p kafka-b -f docker-compose.cluster-b.yml up -d
   export KAFKA_B=kafka-b:19092
   docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_B --list   # rỗng nhưng kết nối OK
   ```
2. Chuẩn bị dữ liệu và **một consumer group có tên thật** ở A (không dùng console consumer mặc định — sẽ bị `groups.exclude` loại).

   ```bash
   kt --create --topic orders --partitions 3 --replication-factor 3
   docker exec -i controller bash -c 'for i in $(seq 1 30); do echo "u$((i % 5)):{\"id\":$i}"; done | \
     /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic orders \
     --property parse.key=true --property key.separator=:'
   koff --topic orders | awk -F: '{s+=$3} END{print "A/orders total:", s}'      # 30

   # group "orders-app" đọc 10 record rồi thoát -> có offset để checkpoint dịch
   kcc --topic orders --group orders-app --from-beginning --max-messages 10 > /dev/null
   kcg --describe --group orders-app
   ```
3. Viết `~/kafka-labs/mm2/mm2.properties` (in đầy đủ).

   ```properties
   # ~/kafka-labs/mm2/mm2.properties — MirrorMaker 2 dedicated mode, flow A -> B (Lab 4.4)
   clusters = A, B
   A.bootstrap.servers = kafka-1:19092,kafka-2:19092,kafka-3:19092
   B.bootstrap.servers = kafka-b:19092

   # --- Flow: MẶC ĐỊNH MỌI FLOW ĐỀU TẮT, phải bật tường minh ---
   A->B.enabled = true
   A->B.topics  = orders.*
   B->A.enabled = false
   # Không emit heartbeat ngược về A: topic MM2 tạo ra dùng RF dưới đây (=1), mà A có min.insync.replicas=2
   # -> producer acks=all vào topic RF1 sẽ NotEnoughReplicas. Tắt để cluster A "sạch".
   B->A.emit.heartbeats.enabled = false

   # --- Cluster B chỉ có 1 broker -> mọi topic MM2 tạo ở B phải RF 1 ---
   replication.factor = 1                       # remote topic A.orders trên B
   checkpoints.topic.replication.factor = 1     # A.checkpoints.internal (trên B)
   heartbeats.topic.replication.factor = 1      # heartbeats (trên B)
   offset-syncs.topic.replication.factor = 1
   offset-syncs.topic.location = target         # mặc định "source" (=A); dời sang B để không tạo topic RF1 trên A
   config.storage.replication.factor = 1        # 3 topic nội bộ của Connect worker (trên B)
   offset.storage.replication.factor = 1
   status.storage.replication.factor = 1

   # --- Offset translation ---
   sync.group.offsets.enabled = true            # ghi thẳng offset đã dịch vào __consumer_offsets của B
   sync.group.offsets.interval.seconds = 5
   emit.checkpoints.interval.seconds = 5
   emit.heartbeats.interval.seconds = 1

   # --- Tự phát hiện topic/group mới ---
   refresh.topics.interval.seconds = 10
   refresh.groups.interval.seconds = 10
   sync.topic.configs.enabled = true
   tasks.max = 3                                # mặc định 1 = KHÔNG scale; docs khuyên >= 2

   # --- Đổi tên topic đích: mặc định DefaultReplicationPolicy -> A.orders. Bước 7 bỏ comment dòng dưới. ---
   # replication.policy.class = org.apache.kafka.connect.mirror.IdentityReplicationPolicy
   ```
4. Chạy MM2 ở container riêng trên cùng network (dedicated mode tự dựng Connect worker). Giữ terminal này mở.

   ```bash
   mkdir -p ~/kafka-labs/mm2
   docker run --rm -it --name mm2 --network kafka-labs_default \
     -v ~/kafka-labs/mm2:/mm2 apache/kafka:4.3.1 \
     /opt/kafka/bin/connect-mirror-maker.sh /mm2/mm2.properties --clusters B
   ```
   Log đáng chú ý (30–60 giây): `Kafka MirrorMaker initializing`, `creating herder for A->B`, `Starting connector MirrorSourceConnector` / `MirrorCheckpointConnector` / `MirrorHeartbeatConnector`, `replicating 3 topic-partitions A->B: [orders-0, orders-1, orders-2]`, `Kafka MirrorMaker started`.
   > 📌 `--clusters B` = *"consume from remote, produce to local"*: chỉ chạy herder có **đích là B**.
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
   # Đủ 30 record và GIỮ NGUYÊN partition
   docker exec controller /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_B --topic A.orders
   koff --topic orders
   # heartbeats tăng đều mỗi giây
   docker exec controller /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_B --topic heartbeats; sleep 3
   docker exec controller /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_B --topic heartbeats
   # Đọc checkpoint bằng formatter có sẵn trong connect-mirror-client
   docker exec controller /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_B \
     --topic A.checkpoints.internal --from-beginning --max-messages 3 \
     --formatter org.apache.kafka.connect.mirror.formatters.CheckpointFormatter
   # Checkpoint{consumerGroupId=orders-app, topicPartition=A.orders-0, upstreamOffset=4, downstreamOffset=4, metadata=}
   ```
6. **Offset consumer group đã được dịch sang B** (chờ ≤ 15 giây).

   ```bash
   docker exec controller /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_B --list
   docker exec controller /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_B --describe --group orders-app
   ```
   Output mẫu — group tồn tại ở B **dù chưa consumer nào từng nối B**:
   ```
   GROUP       TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID  HOST  CLIENT-ID
   orders-app  A.orders  0          4               10              6    -            -     -
   orders-app  A.orders  1          3               10              7    -            -     -
   orders-app  A.orders  2          3               10              7    -            -     -
   ```
   Thử failover — consumer ở B đọc **tiếp**, không đọc lại 10 record đầu:
   ```bash
   docker exec controller /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_B \
     --topic A.orders --group orders-app --timeout-ms 5000 | wc -l     # ~20
   ```
   **Bẫy `groups.exclude`:** tạo thêm một group console mặc định ở A rồi kiểm ở B — nó **không** sang.
   ```bash
   kcc --topic orders --from-beginning --max-messages 5 > /dev/null     # group console-consumer-<random>
   sleep 15
   docker exec controller /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_B --list | grep console || \
     echo "ĐÚNG NHƯ DỰ ĐOÁN: groups.exclude = console-consumer-.*, connect-.*, __.* loại nó ra"
   ```
7. **`IdentityReplicationPolicy`** — giữ nguyên tên topic. `Ctrl+C` MM2, bỏ comment, chạy lại, rồi produce thêm 10 record ở A.

   ```bash
   sed -i.bak 's/^# replication.policy.class/replication.policy.class/' ~/kafka-labs/mm2/mm2.properties
   grep replication.policy.class ~/kafka-labs/mm2/mm2.properties
   docker run --rm -it --name mm2 --network kafka-labs_default -v ~/kafka-labs/mm2:/mm2 \
     apache/kafka:4.3.1 /opt/kafka/bin/connect-mirror-maker.sh /mm2/mm2.properties --clusters B
   ```
   Terminal khác:
   ```bash
   docker exec -i controller bash -c 'for i in $(seq 31 40); do echo "u$((i % 5)):{\"id\":$i}"; done | \
     /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic orders \
     --property parse.key=true --property key.separator=:'
   sleep 12
   docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_B --list | grep -E "^(A\.)?orders$"
   # A.orders  VÀ  orders
   docker exec controller /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server $KAFKA_B --topic orders
   # tổng 10 — chỉ record MỚI
   ```
   > 📌 Vì sao `orders` ở B chỉ có 10 record chứ không phải 40? Offset của `MirrorSourceConnector` (đã copy tới đâu của `orders-N` **nguồn**) nằm trong `mm2-offsets.A.internal` trên B và **không phụ thuộc tên topic đích** → đổi policy chỉ đổi đích cho record **từ đây về sau**. Muốn copy lại từ đầu phải reset offset của connector (xoá `mm2-offsets.A.internal`, hoặc `DELETE /connectors/<name>/offsets` khi chạy trên Connect cluster).

### ✅ Kiểm chứng

- B có **`A.orders` đủ 30 record**, cùng số partition và cùng phân bố key→partition như A; có `heartbeats` (end offset tăng ~1/giây) và `A.checkpoints.internal` đọc được `Checkpoint{consumerGroupId=orders-app, ...}`.
- `mm2-offset-syncs.A.internal` nằm ở **B** (nhờ `offset-syncs.topic.location=target`), và cluster A **không** có topic lạ nào do MM2 tạo.
- `kafka-consumer-groups.sh --describe --group orders-app` **trên B** có offset cho `A.orders` mà chưa consumer nào commit ở B.
- Group `console-consumer-*` **không** xuất hiện ở B — đúng với `groups.exclude` mặc định.
- Sau bước 7: B có thêm topic **`orders`** (giữ nguyên tên) chứa đúng **10** record mới.

### 🧹 Dọn dẹp

```bash
docker rm -f mm2 2>/dev/null
docker compose -p kafka-b -f ~/kafka-labs/docker-compose.cluster-b.yml down -v
kt --delete --topic orders
kcg --delete --group orders-app 2>/dev/null
mv ~/kafka-labs/mm2/mm2.properties.bak ~/kafka-labs/mm2/mm2.properties 2>/dev/null   # trả về DefaultReplicationPolicy
unset KAFKA_B
```

### 🧠 Ý nghĩa với đề thi

- **3 connector**: `MirrorSourceConnector` (record + config topic + ACL, tự phát hiện topic mới) · `MirrorCheckpointConnector` (dịch offset → `{source}.checkpoints.internal`) · `MirrorHeartbeatConnector` (`heartbeats`, đo `replication-latency-ms`).
- **`A->B.enabled = true` là bắt buộc** — flow mặc định tắt. Đây là câu hỏi "MM2 chạy mà không có gì sang đích, thiếu gì?".
- `DefaultReplicationPolicy` → `A.orders`, **chống loop**, bắt buộc cho active-active. `IdentityReplicationPolicy` giữ tên → **chỉ** active-passive/migration.
- Offset dịch **conservative** (không vượt) → consumer ở đích có thể đọc lặp vài record → phải **idempotent**.
- `groups.exclude = console-consumer-.*, connect-.*, __.*` là mặc định — console consumer **không** được replicate.
- MM2 tạo nhiều topic nội bộ ở **cả hai** cluster theo RF trong config; cluster có `min.insync.replicas=2` mà RF 1 sẽ chặn ghi (`NotEnoughReplicas`).

---

## Lab 4.5 — Thêm broker thứ 4, reassignment có throttle, và **gỡ throttle**

**🎯 Mục tiêu:** Thêm `kafka-4` vào cluster, chứng minh nó **không tự nhận partition**, rồi chạy trọn chu trình `--generate` → `--execute --throttle` → soi 4 config throttle → `--verify` (gỡ throttle) → preferred leader election.
**🧩 Luyện kỹ năng (liên quan đề):**

- 3 mode loại trừ nhau của `kafka-reassign-partitions.sh`, và **lưu current assignment để rollback**.
- 4 config throttle: 2 ở broker (`*.replication.throttled.rate`), 2 ở topic (`*.replication.throttled.replicas`).
- **`--verify` là lệnh gỡ throttle** — quên nó là bóp replication vĩnh viễn.
- Reassignment đổi **replica**; leader election chỉ đổi **leader**.

**⏱️ ~35 phút** · **Yêu cầu trước:** Cluster A đang chạy (kèm `docker-compose.rack.yml` nếu bạn còn giữ).

### Các bước

1. Tạo override thêm broker thứ 4 (`node.id` 5, host port **9098**, rack-a cho cân với rack-b/rack-c).

   ```yaml
   # ~/kafka-labs/docker-compose.broker4.yml — thêm broker thứ 4 vào cluster A
   services:
     kafka-4:
       image: apache/kafka:4.3.1
       container_name: kafka-4
       hostname: kafka-4
       depends_on: [controller]
       ports:
         - "9098:9098"
       environment:
         CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"        # PHẢI trùng cluster A
         KAFKA_NODE_ID: 5
         KAFKA_PROCESS_ROLES: broker
         KAFKA_CONTROLLER_QUORUM_VOTERS: 1@controller:9093
         KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
         KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
         KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
         KAFKA_LISTENERS: PLAINTEXT://:19092,PLAINTEXT_HOST://:9098
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-4:19092,PLAINTEXT_HOST://localhost:9098
         KAFKA_BROKER_RACK: rack-a
         KAFKA_DEFAULT_REPLICATION_FACTOR: 3
         KAFKA_MIN_INSYNC_REPLICAS: 2
         KAFKA_NUM_PARTITIONS: 3
         KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
         KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
         KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
         KAFKA_SHARE_COORDINATOR_STATE_TOPIC_REPLICATION_FACTOR: 3
         KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
         KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
   ```
2. Tạo topic **trước khi** thêm broker, bơm dữ liệu, rồi mới thêm broker — để thấy đúng hiện tượng.

   ```bash
   cd ~/kafka-labs
   kt --create --topic expand-demo --partitions 6 --replication-factor 3
   kperf --topic expand-demo --num-records 60000 --record-size 1024 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 acks=all
   kt --describe --topic expand-demo | head -3

   docker compose -f docker-compose.cluster.yml -f docker-compose.rack.yml -f docker-compose.broker4.yml up -d
   docker exec controller /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server kafka-1:19092 | grep -E "^kafka-[0-9]"
   # 4 dòng: id 2,3,4 và id 5 (kafka-4, rack-a)
   ```
3. **Chứng minh broker mới không nhận gì.**

   ```bash
   kldir --topic-list expand-demo --describe | python3 -c "
   import json,sys
   d=json.load(sys.stdin)
   for b in d['brokers']:
       n=sum(1 for ld in b['logDirs'] for p in ld['partitions'])
       print(f\"broker {b['broker']}: {n} replica cua expand-demo\")"
   ```
   Output mẫu:
   ```
   broker 2: 5 replica cua expand-demo
   broker 3: 6 replica cua expand-demo
   broker 4: 7 replica cua expand-demo
   broker 5: 0 replica cua expand-demo     <-- broker mới, KHÔNG có gì
   ```
4. `--generate` và **lưu current assignment** (để rollback).

   ```bash
   docker exec controller bash -lc 'echo "{\"version\":1,\"topics\":[{\"topic\":\"expand-demo\"}]}" > /tmp/topics-to-move.json'
   krp --topics-to-move-json-file /tmp/topics-to-move.json --broker-list "2,3,4,5" --generate \
     | tee ~/kafka-labs/week-04/gen.txt
   awk '/^Current partition replica assignment/{f=1;next} /^Proposed partition reassignment/{f=0} f && NF' \
     ~/kafka-labs/week-04/gen.txt > ~/kafka-labs/week-04/current.json
   awk '/^Proposed partition reassignment/{f=1;next} f && NF' \
     ~/kafka-labs/week-04/gen.txt > ~/kafka-labs/week-04/reassign.json
   cd ~/kafka-labs/week-04 && node -e '
   const fs = require("fs");
   for (const f of ["current.json", "reassign.json"]) {
     const j = JSON.parse(fs.readFileSync(f, "utf8"));
     const brokers = [...new Set(j.partitions.flatMap(p => p.replicas))].sort((a, b) => a - b);
     console.log(f, j.partitions.length, "partition; brokers:", brokers.join(","));
   }'
   # current.json  6 partition; brokers: 2,3,4
   # reassign.json 6 partition; brokers: 2,3,4,5
   docker cp ~/kafka-labs/week-04/reassign.json controller:/tmp/reassign.json
   docker cp ~/kafka-labs/week-04/current.json  controller:/tmp/current.json
   ```
5. `--execute` với throttle **cố tình thấp** (1 MB/s) để kịp quan sát.

   ```bash
   krp --reassignment-json-file /tmp/reassign.json --execute --throttle 1000000
   ```
   Output mẫu:
   ```
   Current partition replica assignment
   {"version":1,"partitions":[...]}
   Save this to use as the --reassignment-json-file option during rollback
   Warning: You must run --verify periodically, until the reassignment completes, to ensure the throttle is removed.
   The inter-broker throttle limit was set to 1000000 B/s
   Successfully started partition reassignments for expand-demo-0,...,expand-demo-5
   ```
6. **Trong lúc đang chạy** (mở terminal khác thật nhanh), soi đủ **4** config throttle.

   ```bash
   # 2 config ở BROKER
   kcfg --describe --entity-type brokers --entity-name 2 | grep -i throttled
   # leader.replication.throttled.rate=1000000, follower.replication.throttled.rate=1000000
   # 2 config ở TOPIC
   kcfg --describe --entity-type topics --entity-name expand-demo | grep -i throttled
   # leader.replication.throttled.replicas=0:2,1:3,...  follower.replication.throttled.replicas=0:5,...

   kt --describe --topic expand-demo    # partition đang chuyển có 4 replica tạm thời + dòng "Adding/Removing replicas"
   krp --reassignment-json-file /tmp/reassign.json --verify   # "is still in progress" cho vài partition
   ```
7. Chờ xong rồi **`--verify`** — đây mới là lệnh **gỡ throttle**.

   ```bash
   while krp --reassignment-json-file /tmp/reassign.json --verify | tee /dev/stderr | grep -q "still in progress"; do sleep 5; done
   ```
   Output mẫu cuối:
   ```
   Status of partition reassignment:
   Reassignment of partition expand-demo-0 is completed.
   ...
   Clearing broker-level throttles on brokers 2,3,4,5
   Clearing topic-level throttles on topic expand-demo
   ```
   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 | grep -i throttled || echo "OK: không còn throttle ở broker"
   kcfg --describe --entity-type topics  --entity-name expand-demo | grep -i throttled || echo "OK: không còn throttle ở topic"
   ```
8. Broker 5 giờ đã có replica; trả leader về preferred.

   ```bash
   kldir --topic-list expand-demo --describe | python3 -c "
   import json,sys
   d=json.load(sys.stdin)
   for b in d['brokers']:
       n=sum(1 for ld in b['logDirs'] for p in ld['partitions'])
       print(f\"broker {b['broker']}: {n} replica\")"
   kt --describe --topic expand-demo | awk '/Partition:/{print "p"$4" leader="$6" replicas="$8}'
   kle --election-type preferred --all-topic-partitions
   kt --describe --topic expand-demo | awk '/Partition:/{print "p"$4" leader="$6" replicas="$8}'   # leader = replica đầu tiên
   ```
9. *(Tuỳ chọn 5 phút)* **Decommission** broker 5 theo đúng quy trình 4.x.

   ```bash
   kcfg --alter --entity-type brokers --entity-name 5 --add-config 'cordoned.log.dirs=*'
   kcfg --describe --entity-type brokers --entity-name 5 | grep cordoned
   docker cp ~/kafka-labs/week-04/current.json controller:/tmp/current.json
   krp --reassignment-json-file /tmp/current.json --execute            # đưa mọi replica về broker 2,3,4
   krp --reassignment-json-file /tmp/current.json --verify
   docker stop kafka-4
   docker exec controller /opt/kafka/bin/kafka-cluster.sh unregister --bootstrap-server kafka-1:19092 --id 5
   ```

### ✅ Kiểm chứng

- Bước 3: broker 5 có **0** replica dù đã join cluster — bằng chứng "broker mới không tự nhận partition".
- Bước 4: `--generate` in **2 JSON**; `current.json` chỉ dùng broker `[2,3,4]`, `reassign.json` dùng `[2,3,4,5]`.
- Bước 6: thấy đủ **4** config throttle (2 broker-level, 2 topic-level) và partition đang chuyển có **nhiều hơn RF** replica tạm thời.
- Bước 7: `--verify` in `Clearing broker-level throttles` + `Clearing topic-level throttles`, và grep sau đó **không còn** config throttle nào.
- Bước 8: broker 5 có replica; sau `kle` thì `Leader` = phần tử **đầu tiên** của `Replicas` ở mọi partition.

### 🧹 Dọn dẹp

```bash
cd ~/kafka-labs
kt --delete --topic expand-demo
docker rm -f kafka-4 2>/dev/null
docker exec controller rm -f /tmp/topics-to-move.json /tmp/reassign.json /tmp/current.json
rm -f ~/kafka-labs/week-04/gen.txt ~/kafka-labs/week-04/current.json ~/kafka-labs/week-04/reassign.json
# GIỮ docker-compose.broker4.yml để thử lại khi ôn
```

### 🧠 Ý nghĩa với đề thi

- *"Thêm broker rồi mà nó vẫn rảnh"* → luôn là **reassignment**, không phải restart, không phải `auto.leader.rebalance`.
- *"Reassignment xong rồi mà URP vẫn cao nhiều ngày"* → **throttle chưa gỡ**; `--verify` là lệnh gỡ.
- Cùng tool này còn: **tăng RF** (thêm replica vào JSON), đổi log dir (`log_dirs` + `--replica-alter-log-dirs-throttle`), **decommission** (`cordoned.log.dirs` → reassign → `kafka-cluster.sh unregister`).
- Reassignment **copy data**; `kafka-leader-election.sh --election-type preferred` **không** copy gì cả, chỉ đổi leader. Đề rất hay hỏi phân biệt hai cái này.

---

## Lab 4.6 — Rolling upgrade mô phỏng + `kafka-features.sh` (gây hỏng rồi sửa)

**🎯 Mục tiêu:** Đọc feature version trước/sau; chạy **rolling restart đúng cách** (1 broker/lần, chờ URP = 0) trong khi producer ghi liên tục **không lỗi**; rồi **cố tình làm sai** (tắt 2 broker cùng lúc) để thấy `NotEnoughReplicas`, và sửa.
**🧩 Luyện kỹ năng (liên quan đề):**

- `kafka-features.sh describe` → `metadata.version`, `kraft.version`, `group.version`…; `upgrade --release-version` để finalize.
- Điều kiện chuyển sang broker kế: **URP = 0**.
- `controlled.shutdown.enable=true` chuyển leadership trước khi tắt.
- RF 3 / min.isr 2 chỉ chịu **1** broker vắng.

**⏱️ ~30 phút** · **Yêu cầu trước:** Cluster A 3 broker đang chạy.

### Các bước

1. Đọc feature và quorum.

   ```bash
   kfeat describe
   kq describe --status | head -6
   ```
   Output mẫu:
   ```
   Feature: eligible.leader.replicas.version  SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1
   Feature: group.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1
   Feature: kraft.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 0
   Feature: metadata.version                  SupportedMinVersion: 3.3-IV3  SupportedMaxVersion: 4.3-IV0  FinalizedVersionLevel: 4.3-IV0
   Feature: share.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1
   Feature: transaction.version               SupportedMinVersion: 0        SupportedMaxVersion: 2        FinalizedVersionLevel: 2
   ```
   > 📌 `kraft.version` = **0** vì cluster dùng **static quorum** (`controller.quorum.voters`); dynamic quorum (KIP-853) mới lên 1. `metadata.version` đã ở mức cao nhất image hỗ trợ nên không có gì để nâng — xem thử lệnh mà không đổi gì:
   > ```bash
   > kfeat upgrade --release-version 4.3 --dry-run
   > ```
2. Xác nhận `controlled.shutdown.enable` và tạo topic + producer ghi liên tục.

   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 --all | grep -E "controlled.shutdown.enable|broker.session.timeout.ms"
   # controlled.shutdown.enable=true ...   broker.session.timeout.ms=9000
   kt --create --topic rolling-demo --partitions 6 --replication-factor 3
   ```
   ```bash
   # Terminal 2 — producer acks=all, idempotent, chạy suốt quá trình
   TOPIC=rolling-demo node ~/kafka-labs/week-04/rack-producer.mjs
   ```
3. Script rolling restart (chạy từ host, CLI qua container `controller`, bootstrap **cả 3 broker**).

   ```bash
   cat > ~/kafka-labs/week-04/rolling-restart.sh <<'SHEOF'
   #!/usr/bin/env bash
   # Rolling restart 3 broker: 1 broker/lần — stop (SIGTERM -> controlled shutdown) -> start -> chờ URP = 0
   set -u
   BS=kafka-1:19092,kafka-2:19092,kafka-3:19092
   urp() {
     local out
     out=$(docker exec controller /opt/kafka/bin/kafka-topics.sh --bootstrap-server "$BS" \
             --describe --under-replicated-partitions 2>&1) || { echo 999; return; }
     echo "$out" | grep -c 'Partition:'
   }
   for b in kafka-1 kafka-2 kafka-3; do
     echo "== [$b] stop (controlled shutdown: chuyển leader trước khi tắt)"; docker stop "$b" >/dev/null
     echo "   URP khi $b đang tắt: $(urp)"
     echo "== [$b] start"; docker start "$b" >/dev/null
     until [ "$(urp)" = "0" ]; do echo "   chờ URP về 0 (hiện $(urp))..."; sleep 5; done
     echo "== [$b] URP = 0 -> OK, nghỉ 5 s rồi sang broker kế tiếp"; sleep 5
   done
   echo "== Xong 3 broker. Preferred leader election:"
   docker exec controller /opt/kafka/bin/kafka-leader-election.sh --bootstrap-server "$BS" \
     --election-type preferred --all-topic-partitions
   SHEOF
   chmod +x ~/kafka-labs/week-04/rolling-restart.sh
   ~/kafka-labs/week-04/rolling-restart.sh
   ```
   Output mẫu:
   ```
   == [kafka-1] stop (controlled shutdown: chuyển leader trước khi tắt)
      URP khi kafka-1 đang tắt: 14
   == [kafka-1] start
      chờ URP về 0 (hiện 14)...
      chờ URP về 0 (hiện 3)...
   == [kafka-1] URP = 0 -> OK, nghỉ 5 s rồi sang broker kế tiếp
   ...
   Successfully completed leader election (PREFERRED) for partitions rolling-demo-0, rolling-demo-3
   ```
   Terminal 2: `ok=... fail=0` đều đặn suốt quá trình.
4. Soi log controlled shutdown.

   ```bash
   docker logs kafka-1 2>&1 | grep -iE "controlled shutdown|PENDING_CONTROLLED_SHUTDOWN|SHUTTING_DOWN" | tail -5
   docker logs controller 2>&1 | grep -iE "controlled shutdown|fenc|unfenc" | tail -6
   ```
   Thấy broker đi qua `RUNNING → PENDING_CONTROLLED_SHUTDOWN → SHUTTING_DOWN`; controller nhận `BrokerHeartbeat` có `wantShutDown=true`, chuyển leadership **rồi mới** cho tắt.
5. **GÂY HỎNG — làm sai quy trình.** Tắt 2 broker cùng lúc (đúng cái mà "chờ URP = 0" ngăn không cho xảy ra).

   ```bash
   docker stop kafka-2 kafka-3
   kt --describe --under-min-isr-partitions | head -5
   ```
   Terminal 2 báo ngay:
   ```
   FAIL msg-137: KafkaJSProtocolError: Messages are rejected since there are fewer in-sync replicas than required
   ```
6. **SỬA** và rút ra quy tắc.

   ```bash
   docker start kafka-2 kafka-3
   until [ "$(kt --describe --under-replicated-partitions | grep -c 'Partition:')" = "0" ]; do echo "chờ URP về 0..."; sleep 5; done
   kt --describe --under-min-isr-partitions || true      # rỗng; Terminal 2 tự hết FAIL
   kfeat describe | grep metadata.version                # không đổi — restart không đụng tới feature version
   ```

### ✅ Kiểm chứng

- `kfeat describe` đọc được `metadata.version` (`4.3-IV0`), `kraft.version` (0 = static quorum), và 4 feature còn lại.
- Script rolling restart chờ URP về 0 **trước** mỗi broker kế tiếp; producer in `fail=0` suốt quá trình; `Ctrl+C` producer in `TOTAL ... fail=0`.
- Log của `kafka-1` có dấu vết controlled shutdown; log `controller` có `wantShutDown`/fence.
- Bước 5 cho `NotEnoughReplicas` **ngay lập tức** — đó là lý do quy trình bắt buộc 1 broker/lần.
- Sau bước 6, `--under-min-isr-partitions` rỗng và `metadata.version` không đổi.

### 🧹 Dọn dẹp

```bash
# Ctrl+C producer ở Terminal 2
kt --delete --topic rolling-demo
docker start kafka-2 kafka-3 2>/dev/null || true
```

### 🧠 Ý nghĩa với đề thi

- **Rolling upgrade KRaft = 2 giai đoạn**: nâng từng node chờ URP = 0 → **finalize** `kafka-features.sh upgrade --release-version 4.3`. `inter.broker.protocol.version` **không còn tồn tại**.
- **Downgrade**: chỉ khi không có metadata change. **4.3.0 và 4.0.x không downgrade được**; 4.2.0 thì được.
- `controlled.shutdown.enable=true` (mặc định) là thứ biến rolling restart thành "zero-downtime" cho client; `kill -9` thì không, và lần lên lại phải log recovery.
- Dạng **list order** của đề rất hay hỏi đúng chuỗi này — tập viết lại từ trí nhớ.

---

## Lab 4.7 — (Concept) Cluster Linking: vì sao không chạy được ở đây, và khác MM2 chỗ nào

**🎯 Mục tiêu:** Chứng minh bằng lệnh rằng Cluster Linking **không tồn tại** trong Apache Kafka thuần, đọc cấu hình mẫu của Confluent Platform, và đối chiếu từng dòng với `mm2.properties` của Lab 4.4.
**🧩 Luyện kỹ năng (liên quan đề):**

- Nhận diện tính năng **Confluent-only** giữa một danh sách phương án.
- "Giữ nguyên offset" là dấu hiệu nhận biết Cluster Linking, không phải `IdentityReplicationPolicy`.
- Mirror topic **read-only** và quy trình `--promote` / `--failover`.

**⏱️ ~15 phút** · **Yêu cầu trước:** Cluster A đang chạy; đã làm Lab 4.4.

### Các bước

1. **Chứng minh nó không có trong Apache Kafka.**

   ```bash
   docker exec controller ls /opt/kafka/bin | sort
   docker exec controller ls /opt/kafka/bin | grep -iE "cluster-link|mirrors" || echo "KHÔNG có kafka-cluster-links / kafka-mirrors -> Cluster Linking là tính năng Confluent Server"
   docker exec controller ls /opt/kafka/bin | grep -iE "mirror"
   # connect-mirror-maker.sh  <- chỉ có MM2
   ```
   Tìm cả ở phía config broker:
   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 --all | grep -iE "cluster.link|confluent" || \
     echo "KHÔNG có config cluster.link.* -> broker Apache Kafka không biết khái niệm cluster link"
   ```
2. Đọc cấu hình mẫu của Confluent Platform (chỉ để **nhận diện cú pháp**, không chạy được ở đây) trong [`resources/confluent-cluster-linking.md`](resources/confluent-cluster-linking.md), phần "Cấu hình mẫu". Chú ý 4 dòng quan trọng: `link.mode=DESTINATION`, `consumer.offset.sync.enable=true`, `acl.sync.enable=true`, `auto.create.mirror.topics.enable=true`.
3. Tự điền bảng đối chiếu (che cột phải rồi mới mở ra so):

   | Câu hỏi | MirrorMaker 2 (Lab 4.4 bạn vừa chạy) | Cluster Linking |
   |---|---|---|
   | Chạy ở đâu | **Kafka Connect** (`connect-mirror-maker.sh` dựng worker riêng) | **Bên trong broker** đích, không cần Connect |
   | Chiều dữ liệu | Connect **consume** từ nguồn rồi **produce** vào đích | Broker đích **kéo** trực tiếp từ broker nguồn |
   | Tên topic đích | `A.orders` (Default) hoặc `orders` (Identity) | **`orders`** — luôn giữ tên |
   | Offset | **Khác** → dịch qua `A.checkpoints.internal` | **Bằng nhau byte-for-byte** |
   | Ghi vào topic đích | Được (topic bình thường) | **Không** — mirror topic **read-only** cho tới khi `--promote`/`--failover` |
   | Hai chiều | Một file config, 2 flow `A->B, B->A` | **2 link đơn hướng** riêng |
   | Có trên Apache Kafka | **Có** | **Không** (Confluent Server ≥ 7.8.0) |
   | Transaction | Copy được record (state transaction thì không) | **Không mirror được message transaction** |

4. Trả lời nhanh 3 tình huống (tự làm rồi so với [answers.md](answers.md) của tuần):
   - Cluster Apache Kafka 4.3 on-prem, cần DR sang một cluster Apache Kafka khác, consumer phải tiếp tục gần đúng vị trí cũ → ?
   - Confluent Platform 7.9, cần migrate toàn bộ sang Confluent Cloud, ứng dụng **không được sửa tên topic và không được đọc lại từ đầu** → ?
   - Hai DC cách nhau 8 km, đường dark fiber 2 ms, yêu cầu **không mất một message nào** → ?

### ✅ Kiểm chứng

- `ls /opt/kafka/bin` **không** có `kafka-cluster-links.sh` hay `kafka-mirrors.sh`, chỉ có `connect-mirror-maker.sh`.
- Không có config broker nào bắt đầu bằng `cluster.link.`.
- Bạn điền được **≥ 6/8** dòng của bảng đối chiếu mà không mở tài liệu.
- Ba tình huống ở bước 4: **MM2** · **Cluster Linking** · **stretch cluster**.

### 🧹 Dọn dẹp

```bash
# Không có gì để dọn — lab này chỉ đọc. Kết thúc tuần thì tắt toàn bộ:
cd ~/kafka-labs
docker compose -p kafka-b -f docker-compose.cluster-b.yml down -v 2>/dev/null || true
docker rm -f kafka-4 mm2 2>/dev/null || true
docker compose -f docker-compose.cluster.yml -f docker-compose.rack.yml down
# GIỮ: docker-compose.rack.yml, docker-compose.broker4.yml, docker-compose.cluster-b.yml, mm2/, week-04/*.mjs, week-04/*.sh
```

### 🧠 Ý nghĩa với đề thi

- Phương án nhắc **Cluster Linking** trong ngữ cảnh *"cluster Apache Kafka thuần"* là **sai** — đó là bẫy nhận diện sản phẩm.
- *"Giữ nguyên offset"* → Cluster Linking. *"Giữ nguyên tên topic"* → `IdentityReplicationPolicy` của MM2 **hoặc** Cluster Linking. Hai vế này **không** giống nhau.
- Mirror topic **read-only** là lý do quy trình failover phải có bước `--promote` (nguồn còn sống, không mất dữ liệu) hoặc `--failover` (nguồn đã chết, RPO > 0).
- Cả MM2 lẫn Cluster Linking đều **bất đồng bộ** → RPO > 0. Muốn **RPO = 0** chỉ có **stretch cluster**.

---

> ✅ Xong 7 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist) — nhớ **Lab 4.1, 4.2, 4.4 là bắt buộc** — rồi làm [bộ 28 câu luyện tập](questions.md) trong 42 phút và ghi sổ câu sai theo 6 nhóm. Giữ lại `docker-compose.rack.yml`, `docker-compose.broker4.yml`, `docker-compose.cluster-b.yml` và `mm2/` cho Tuần 7 (chẩn đoán) và Tuần 8 (capstone).
