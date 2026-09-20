# 🟦 Tuần 2 — Độ tin cậy & lưu trữ: replication, retention, log compaction, delivery semantics

> **Domain CCDAK:** Fundamentals (FUND, 23%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 2/10 — khép lại phần Fundamentals lý thuyết, chưa có checkpoint (mini-mock FUND+DEV ở Tuần 4)
>
> **Điều hướng:** [⬅️ Tuần 1](../week-01/README.md) · [🏠 Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md) · [Tuần 3 ➡️](../week-03/README.md)

## 🎯 Mục tiêu tuần này

- **Giải thích được** record "committed" là gì, vì sao consumer chỉ đọc tới **high watermark**, và follower rời/vào lại ISR theo `replica.lag.time.max.ms` = 30 s như thế nào.
- **Điền được từ trí nhớ** ma trận **`acks` × `min.insync.replicas`**: với RF=3 + min.isr=2 + `acks=all` thì mất 1 broker vẫn ghi, mất 2 broker nhận `NotEnoughReplicasException`.
- **Phân biệt được** unclean leader election vs **ELR (KIP-966)** vs preferred leader — ai được bầu, theo thứ tự nào, và config nào bật/tắt.
- **Tự tay** ép segment roll, quan sát retention xoá **cả segment đã đóng** (trả lời được "vì sao data quá hạn vẫn còn") và chạy **log compaction** thấy chỉ còn giá trị cuối theo key + tombstone biến mất.
- **Cấu hình được** chuỗi giới hạn kích cỡ message (`max.request.size` → `max.message.bytes`/`message.max.bytes` → `max.partition.fetch.bytes`) và sửa `RecordTooLargeException` đúng chỗ.
- **Nhận diện được** khi nào chọn **share group (Queues for Kafka, KIP-932)** thay consumer group; thuộc 3 loại acknowledge và 2 con số 30 s / 5 lần.
- **Chốt nền FUND:** trả lời trôi chảy 8 câu Cổng tự kiểm tra và đạt ≥ 70% bộ [questions.md](questions.md) trước khi sang Tuần 3.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Replication sâu — leader / follower / ISR / high watermark (hỏi nhiều nhất tuần)**

- Đơn vị replication = **partition**. Mỗi partition có **1 leader** nhận mọi ghi (và đọc mặc định), **N−1 follower** **kéo** (fetch) từ leader như một consumer — không phải leader đẩy. RF = tổng replica kể cả leader.
- **ISR (In-Sync Replicas)** = leader + follower thoả 2 điều kiện: (1) còn **session** với KRaft controller (`broker.session.timeout.ms`), (2) không tụt quá **`replica.lag.time.max.ms` = 30 000 ms** so với **log end offset (LEO)** của leader — "không gửi fetch" hoặc "chưa đuổi kịp LEO" trong 30 s đều bị loại. Tụt → **ISR shrink** (leader loại); đuổi kịp → **ISR expand** (tự vào lại). Không có ngưỡng theo *số message* (config `replica.lag.max.messages` đã bị gỡ từ 0.9).
- **LEO** = offset kế tiếp sẽ ghi trên một replica. **High watermark (HW)** = offset **committed** = min(LEO) của mọi replica trong ISR. Record **committed** khi **mọi** replica trong ISR đã ghi nó. **Consumer chỉ đọc tới HW** — dữ liệu đã ở leader nhưng chưa được ISR sao chép thì consumer **chưa thấy** (đề: "producer nhận ack rồi mà consumer chưa đọc được" khi `acks=1`).
- Kafka đảm bảo: record committed **không mất** miễn còn **≥ 1 replica trong ISR sống**. Với **f+1** replica chịu **f** lỗi (majority quorum cần **2f+1**) — đổi lại phải chờ replica chậm nhất trong ISR (nhưng chậm quá thì bị loại).
- HW **không tiến** khi `|ISR| < min.insync.replicas` ("strict min ISR") — đây là nền để ELR hoạt động (mục 3).

**2. `acks` × `min.insync.replicas` — ma trận durability (BẮT BUỘC thuộc)**

| Producer `acks` | Broker chờ gì trước khi trả lời | `min.insync.replicas` có tác dụng? | Rủi ro |
| --- | --- | --- | --- |
| `0` | Không chờ (fire-and-forget); không có offset trả về | ❌ | Mất khi mạng lỗi / leader chết; latency thấp nhất |
| `1` | **Leader** ghi vào log local | ❌ | Leader ack xong chết trước khi follower fetch → **mất record đã ack** |
| `all` / `-1` (**mặc định từ 3.0**) | **Mọi replica trong ISR hiện tại** ghi xong **và** `|ISR| ≥ min.insync.replicas` | ✅ **chỉ** ở mức này | ISR < min.isr → `NotEnoughReplicasException` (retriable) / `NotEnoughReplicasAfterAppendException` |

| Cấu hình topic | 1 broker chết | 2 broker chết | Nhận xét |
| --- | --- | --- | --- |
| RF=3, min.isr=**1**, `acks=all` | Ghi được | **Vẫn ghi được** với ISR=1 → có thể mất dữ liệu nếu broker cuối chết | `acks=all` ≠ "mọi replica được gán"; chỉ là ISR **hiện tại** |
| RF=3, min.isr=**2**, `acks=all` ⭐ | **Ghi được** (ISR=2 ≥ 2) | **Ngừng ghi** (`NotEnoughReplicas`), **đọc vẫn được**, không mất dữ liệu committed | Chuẩn production |
| RF=3, min.isr=**3**, `acks=all` | **Ngừng ghi** ngay | Ngừng ghi | Bền nhất nhưng 1 broker bảo trì là dừng |
| RF=2, min.isr=1, `acks=all` | Ghi được với ISR=1, mất bản dự phòng | Mất topic | Bẫy đề "RF=2 có an toàn không?" |
| RF=3, min.isr=2, `acks=1` | Ghi được | **Vẫn ghi được** (min.isr không áp cho `acks=1`) | Bẫy: đặt min.isr mà producer `acks=1` = vô nghĩa |

- **`min.insync.replicas`** là config **topic-level** (override broker/cluster default; mặc định **1**, cluster lab của ta đặt **2**). Với ELR bật, giá trị dùng chung phải đặt ở **cluster-level** (`--entity-type brokers --entity-default`), không alter được ở **broker-level**.
- Ghi bị chặn nhưng **đọc không bị chặn** bởi `min.isr`; consumer vẫn đọc tới HW cũ.

**3. Bầu leader: unclean election → ELR (KIP-966) → preferred leader → rack awareness**

- **Mặc định** controller chỉ bầu leader **trong ISR**. Cả ISR chết → 2 lựa chọn: **chờ** replica ISR sống lại (consistency, mặc định `unclean.leader.election.enable=false`) hoặc **bầu replica ngoài ISR** (`true`, availability, **mất dữ liệu committed**). Config có ở cả broker và topic-level; ép tay một lần bằng `kafka-leader-election.sh --election-type UNCLEAN`.
- **ELR — Eligible Leader Replicas (KIP-966 Part 1):** vì HW không tiến khi ISR < min.isr, follower bị loại khỏi ISR **sau khi** ISR đã dưới min.isr vẫn giữ đủ mọi record committed → controller ghi chúng vào tập **ELR**. Thứ tự bầu: **(1) ISR** → **(2) ELR chưa fenced** → **(3) last known leader** unfenced. Có từ **4.0** (bật tay `eligible.leader.replicas.version=1`), **bật mặc định cluster mới từ 4.1**. `kafka-topics.sh --describe` in `Elr:` / `LastKnownElr:`. Đổi `min.insync.replicas` (cluster hoặc topic) → **xoá trạng thái ELR**. ELR **không** thay `unclean.leader.election.enable` — chỉ mở rộng tập ứng viên an toàn.
- **Preferred leader** = replica **đầu tiên** trong `Replicas`. Sau sự cố leader dồn về broker sống; `auto.leader.rebalance.enable=true` kiểm tra mỗi **`leader.imbalance.check.interval.seconds=300`**, chỉ cân bằng khi lệch > `leader.imbalance.per.broker.percentage=10`%. Ép ngay: `kafka-leader-election.sh --election-type PREFERRED --all-topic-partitions`.
- **Rack awareness:** đặt `broker.rack=us-east-1a` cho từng broker → khi tạo topic, controller rải replica của mỗi partition lên **các rack khác nhau** (hết rack mới lặp) → mất 1 AZ vẫn còn replica. Bảo đảm chỉ khi RF ≤ số rack hoặc phân bố đều. (Đọc từ follower cùng rack: `client.rack` + `replica.selector.class` — Tuần 4.)

**4. Lưu trữ: segment, retention và cái bẫy "vì sao data quá hạn chưa xoá"**

- Partition = thư mục; **segment** = file `.log` + `.index` + `.timeindex`. **Roll** segment mới khi đạt **`segment.bytes` = 1 GiB** (`log.segment.bytes`; min 1 MiB) **hoặc** quá **`segment.ms` = 7 ngày** (`log.roll.ms` / `log.roll.hours=168`) — cái nào tới trước. Segment đang ghi = **active segment**.
- **Retention (policy `delete`)** xoá theo **thời gian** `retention.ms` = **604 800 000 (7 ngày)** — thứ tự ưu tiên broker `log.retention.ms` > `log.retention.minutes` > `log.retention.hours` — **hoặc** theo **kích cỡ** `retention.bytes` = **-1** (không giới hạn; tính **per partition**, topic 6 partition × 1 GB = 6 GB). `retention.ms=-1` = giữ vĩnh viễn. Cả hai đặt → cái nào chạm trước xoá trước.
- ⚠️ **Retention và compaction luôn làm việc theo file** ("Retention and cleaning is always done a file at a time"): chỉ xoá **segment đã đóng** khi record **mới nhất** trong segment quá hạn; **không bao giờ đụng active segment**. Vì vậy topic ít dữ liệu với `segment.bytes` 1 GB có thể giữ record **lâu hơn** `retention.ms` rất nhiều → muốn retention đúng hạn phải hạ `segment.ms`/`segment.bytes`. Broker chỉ **quét** mỗi **`log.retention.check.interval.ms` = 300 000 (5 phút)**; file bị đổi tên `.deleted` rồi xoá thật sau `file.delete.delay.ms` = 60 s.
- Consumer đọc offset đã bị xoá → `OffsetOutOfRangeException` → `auto.offset.reset` quyết định (Tuần 4). Xoá chủ động bằng `kafka-delete-records.sh` (dời log start offset, không cần chờ retention).
- Kafka **không fsync mỗi message** (`flush.messages`/`flush.ms` = MAX) — độ bền đến từ **replication + page cache**, không từ đĩa của 1 broker.

**5. Log compaction — giữ giá trị cuối theo key**

- Bật bằng topic config **`cleanup.policy=compact`** (broker `log.cleanup.policy` mặc định `delete`). Ý nghĩa: partition giữ **ít nhất giá trị cuối cùng cho mỗi key** → topic thành **snapshot KV** có thể replay để dựng lại state. Dùng cho **`__consumer_offsets`**, changelog của `Kafka Streams`, **CDC / database change subscription**, event sourcing, cache reload.
- **Compacted topic bắt buộc có key**; record key null bị broker từ chối. **Tombstone** = key + **value `null`** → xoá key; tombstone được giữ **`delete.retention.ms` = 86 400 000 (24 h)** rồi mới dọn → consumer đọc từ offset 0 phải tới head **trong 24 h** mới thấy đủ tombstone.
- **Head** (chưa compact, offset dày) vs **tail** (đã compact, offset **giữ nguyên**, có lỗ). **4 đảm bảo:** consumer bám head thấy mọi message; **thứ tự không đổi**; **offset không đổi** (đọc offset đã bị dọn → nhận offset kế tiếp còn tồn tại); đọc từ đầu thấy **ít nhất** trạng thái cuối mọi key. ⚠️ **Không** đảm bảo "đúng 1 record/key" tại mọi thời điểm (head còn trùng).
- Compaction chạy **nền** bởi **log cleaner threads** (`log.cleaner.threads` = 1, `log.cleaner.enable` = true — deprecated, luôn bật từ 5.0), **chỉ trên segment đã đóng** → lab phải hạ `segment.ms`. Điều kiện: **`min.cleanable.dirty.ratio` = 0.5** (dirty ≥ 50% mới dọn); **`min.compaction.lag.ms` = 0** (thời gian tối thiểu record ở head chưa bị dọn — dùng khi consumer cần thấy mọi bản); `max.compaction.lag.ms` = MAX (deadline ép dọn cho topic produce chậm).
- **`cleanup.policy=compact,delete`**: giữ giá trị cuối theo key **và** xoá segment quá `retention.ms`/`retention.bytes` — dùng khi key cũ không còn ý nghĩa sau X ngày (session state, TTL).

| Tiêu chí | `delete` (mặc định) | `compact` | `compact,delete` |
| --- | --- | --- | --- |
| Xoá theo | Thời gian / kích cỡ, **cả segment** | Key trùng (giữ bản cuối), tombstone | Cả hai |
| Cần key? | Không | **Bắt buộc** | Bắt buộc |
| Kích cỡ log | Bị chặn bởi retention | Tỉ lệ số key **distinct** | Bị chặn bởi cả hai |
| Đọc từ đầu thấy gì | Mọi record còn trong retention | Ít nhất giá trị cuối mỗi key (+ tombstone < 24 h) | Giá trị cuối của key còn trong retention |
| Dùng cho | Event stream, log, metrics | Changelog, CDC snapshot, `__consumer_offsets`, KV store | State có TTL |
| Tiered storage | ✅ | ❌ không hỗ trợ | ❌ |

**6. Delivery semantics — 2 nửa: producer ghi bền + consumer commit khi nào**

| Mức | Nghĩa | Producer đạt bằng | Consumer đạt bằng |
| --- | --- | --- | --- |
| **At-most-once** | Có thể **mất**, không bao giờ trùng | `acks=0` hoặc `retries=0` | **Commit offset trước** khi xử lý (crash → bỏ qua record) |
| **At-least-once** (mặc định Kafka) | Không mất, **có thể trùng** | `acks=all` + retries (mặc định) | **Xử lý trước, commit sau** (crash → xử lý lại); auto-commit cũng thuộc nhóm này |
| **Exactly-once** | Mỗi record ảnh hưởng đúng 1 lần | **Idempotent producer** (PID + sequence, mặc định từ 3.0) chống trùng **trong partition**; **transactions** (`transactional.id`) ghi atomic nhiều partition + offset | `isolation.level=read_committed` (mặc định `read_uncommitted`); hoặc **idempotent consumer** (upsert theo key) khi ghi ra hệ thống ngoài |

- Producer không nhận ack vì lỗi mạng → **không biết** record đã committed chưa → retry → **trùng** nếu không idempotent. Kafka ≥ 3.0 mặc định `enable.idempotence=true` + `acks=all` nên at-least-once **không trùng trong partition** ở lớp producer; trùng còn lại đến từ **consumer** xử lý lại.
- Exactly-once "read-process-write" **giữa các topic Kafka**: offset consumer được ghi **trong cùng transaction** với output (`Kafka Streams` `exactly_once_v2` hoặc `sendOffsetsToTransaction`). Ghi ra **hệ thống ngoài** không có 2PC → lưu offset **cùng chỗ** với output hoặc dedup theo key. Chi tiết Tuần 3.

**7. Ordering — chỉ trong partition, theo key**

- Kafka đảm bảo thứ tự **trong 1 partition**; giữa các partition **không**. Cùng key → murmur2 → cùng partition (miễn số partition không đổi). Toàn topic có thứ tự ⇔ **1 partition**.
- Retry của producer có thể **đảo thứ tự** nếu `max.in.flight.requests.per.connection` > 1 **và** không idempotent; idempotent producer giữ thứ tự với `max.in.flight ≤ 5` (Tuần 3). Consumer đọc 1 partition = 1 thread → thứ tự giữ; share group **bỏ** đảm bảo thứ tự.

**8. Kích cỡ message — chuỗi 4 giới hạn và `RecordTooLargeException`**

| Tầng | Config | Mặc định | Ghi chú |
| --- | --- | --- | --- |
| Producer | `max.request.size` | **1 048 576** (1 MiB) | Kích cỡ **1 request** (batch) và cũng chặn 1 record quá lớn → **`RecordTooLargeException` ở client** (chưa gửi đi) |
| Broker | `message.max.bytes` | **1 048 588** (1 MiB + 12 B) | Kích cỡ **record batch sau nén**; topic override **`max.message.bytes`** (cùng mặc định) → vượt → broker trả `MESSAGE_TOO_LARGE` → client thấy `RecordTooLargeException` |
| Follower | `replica.fetch.max.bytes` | 1 048 576 | **Không phải trần tuyệt đối**: batch đầu vẫn được trả dù lớn hơn → replication không kẹt |
| Consumer | `max.partition.fetch.bytes` / `fetch.max.bytes` | 1 048 576 / 52 428 800 (50 MiB) | Từ KIP-74 (0.10.1) batch đầu vẫn trả dù vượt → consumer **không kẹt**, nhưng nên tăng cho throughput |

- Sửa `RecordTooLargeException` **đúng thứ tự**: tăng **`max.request.size`** (producer) **và** **`max.message.bytes`** (topic) hoặc `message.max.bytes` (broker); cân nhắc `replica.fetch.max.bytes` ≥ `message.max.bytes` để replication hiệu quả. Cách tốt hơn: **nén** (`compression.type`) hoặc **claim-check** (đẩy payload lên object storage, gửi URL).
- **`compression.type` ở broker/topic = `producer`** (mặc định): giữ nguyên codec producer gửi, broker **không giải/nén lại** (zero-copy). Đặt `gzip/snappy/lz4/zstd/uncompressed` → broker nén lại theo codec đó (tốn CPU broker).
- **`message.timestamp.type`**: `CreateTime` (mặc định — producer gán, có thể lệch; `message.timestamp.after.max.ms` = 1 h chặn timestamp tương lai) vs `LogAppendTime` (broker ghi đè lúc append — cần khi muốn retention/time-index theo giờ broker).

**9. Queues for Kafka — share groups (KIP-932, GA 4.2) — nhận diện**

| Tiêu chí | Consumer group (classic / KIP-848) | **Share group** (`KafkaShareConsumer`) |
| --- | --- | --- |
| Gán | **Partition → đúng 1 consumer**; consumer dư idle | Partition **chia sẻ** cho nhiều consumer; số consumer **> số partition** vẫn hữu ích |
| Đơn vị ack | **Offset** (commit vị trí) | **Từng record**: `ACCEPT` / `RELEASE` (giao lại) / `REJECT` (bỏ hẳn); renew để gia hạn |
| Thứ tự | Trong partition | **Không đảm bảo** |
| Record lỗi | Tự viết retry/DLQ | **Delivery count** — quá `share.delivery.count.limit` = **5** → archive |
| Khoá | — | **Acquisition lock** `share.record.lock.duration.ms` = **30 s** (15–60 s); tối đa `share.partition.max.record.locks` = 2000 lock/partition |
| Ack mode client | — | `share.acknowledgement.mode` = `implicit` (poll kế = ACCEPT cả batch) / `explicit` (`acknowledge()` từng record) |
| Bắt đầu đọc | `auto.offset.reset=latest` | `share.auto.offset.reset=latest` (earliest / `by_duration:`) |
| State lưu ở | `__consumer_offsets` (50 partition) | **`__share_group_state`** (50 partition, share coordinator) |
| Tool | `kafka-consumer-groups.sh`, `kafka-console-consumer.sh` | **`kafka-share-groups.sh`**, **`kafka-console-share-consumer.sh`** |
| Bật | Luôn | Feature **`share.version=1`** (`kafka-features.sh`) |
| Dùng khi | Stream processing, cần thứ tự theo key, replay | **Job queue** kiểu `SQS`/RabbitMQ: nhiều worker, ack lẻ, không cần thứ tự |

- Lộ trình: early access **4.0** → preview **4.1** → **GA 4.2**. `kafkajs` **không** hỗ trợ; `@confluentinc/kafka-javascript` và Java client 4.x có.

**10. Tiered storage (KIP-405) — nhận diện, Tuần 8 đi sâu**

- Segment **đã đóng** được copy lên **remote storage** (S3/HDFS…) qua `RemoteStorageManager`; local chỉ giữ `local.retention.ms/bytes` (mặc định **-2** = bằng `retention.*`), tổng retention theo `retention.*`. Bật per topic `remote.storage.enable=true` (broker `remote.log.storage.system.enable=true`). GA từ **3.9**. **Không hỗ trợ compacted topic**; tắt phải kèm `remote.log.delete.on.disable=true`. Đề: "retention dài, rẻ, không thêm broker" → tiered storage.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 Chi tiết từng bước trong [labs.md](labs.md). Dùng lại **cluster 3 node** `docker-compose.cluster.yml` từ Tuần 1 (`min.insync.replicas=2`, RF=3).

- **Lab 2.1 ⭐** — Thí nghiệm `acks` × `min.isr`: topic RF3 min.isr 2; `docker stop kafka-2 kafka-3` → producer `acks=all` nhận `NotEnoughReplicas`, `acks=1` vẫn ghi; đọc vẫn được; bật lại → hồi.
- **Lab 2.2** — Quan sát ISR / HW / LEO: `kt --describe` (cột `Isr`, `Elr`), `kafka-get-offsets.sh`, `kafka-log-dirs.sh` (`offsetLag`) khi dừng follower rồi bật lại — thấy shrink sau 30 s và expand khi đuổi kịp.
- **Lab 2.3** — Retention nhanh: topic `retention.ms=60000 segment.ms=10000`, chờ quét 5 phút, earliest offset dời (`--time -2`); so với `kafka-delete-records.sh`.
- **Lab 2.4 ⭐** — Log compaction bằng `kafkajs`: produce cùng key nhiều lần + tombstone `value: null`, ép roll `segment.ms=5000`, đọc `--from-beginning` chỉ còn giá trị cuối; tombstone biến mất sau `delete.retention.ms`.
- **Lab 2.5** — `RecordTooLargeException`: record 2 MB fail ở client (console producer) và ở broker (kafkajs) → sửa `max.request.size` + `max.message.bytes`.
- **Lab 2.6** — Share group: 2 `kafka-console-share-consumer.sh` cùng group trên topic **1 partition** cùng nhận message; `kafka-share-groups.sh --describe --members`; so với consumer group (1 consumer idle).
- **Lab 2.7** — `kafka-configs.sh`: alter động topic/broker/cluster-default, đọc `--describe --all` (DYNAMIC vs STATIC vs DEFAULT), thử config read-only bị từ chối.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**1. Bảng quyết định "độ bền cần bao nhiêu" (đọc đề → chọn combo)**

| Yêu cầu đề | Combo đúng | Vì sao không phải cái khác |
| --- | --- | --- |
| "no data loss", "survive 1 broker failure", vẫn ghi được | **RF=3 + `min.insync.replicas=2` + `acks=all`** (+ idempotence mặc định) | RF=2 chỉ còn 1 bản khi mất 1 broker; min.isr=3 ngừng ghi khi mất 1 |
| "lowest latency, loss acceptable" (metrics, click) | `acks=0` (hoặc `acks=1`) | `acks=all` chờ ISR → chậm hơn |
| "availability over consistency", chấp nhận mất | `unclean.leader.election.enable=true` | ELR không thay được khi cả ISR + ELR trống |
| "leader chết khi ISR đã co về 1, không muốn unclean" | **ELR** (bật mặc định 4.1+) | ISR trống → không unclean thì chờ; ELR cho ứng viên an toàn |
| "mất cả AZ vẫn còn replica" | `broker.rack` + RF ≥ số AZ cần chịu | Partition reassignment thủ công không tự rack-aware |
| "sau bảo trì leader dồn 1 broker" | `auto.leader.rebalance.enable` (300 s) hoặc `kafka-leader-election.sh --election-type PREFERRED` | Reassign partition là quá tay |

**2. Bảng quyết định lưu trữ**

| Đề nói | Chọn |
| --- | --- |
| "event log, replay 7 ngày" | `cleanup.policy=delete`, `retention.ms` |
| "chỉ cần trạng thái mới nhất mỗi entity", "KV snapshot", "changelog/CDC" | `cleanup.policy=compact` (+ tombstone để xoá) |
| "state theo key nhưng hết hạn sau 30 ngày" | `compact,delete` + `retention.ms` |
| "retention đặt 1 h mà data 1 ngày vẫn còn" | active segment chưa roll → hạ `segment.ms`/`segment.bytes`; nhớ quét mỗi 5 phút |
| "giữ vĩnh viễn" | `retention.ms=-1` (và `retention.bytes=-1`) |
| "giữ 1 năm, rẻ, không thêm đĩa broker" | **tiered storage** (`remote.storage.enable=true`) — trừ compacted topic |
| "consumer phải xử lý hết tombstone" | tăng `delete.retention.ms` (24 h) |
| "compaction chạy quá thưa/quá dày" | `min.cleanable.dirty.ratio` (0.5 ↓ để dọn sớm), `min.compaction.lag.ms` (giữ head lâu hơn) |

**3. Đọc thêm (30–40 phút)**

- Docs *Design → Replication* trọn mục (đặc biệt "Availability and Durability Guarantees" — nguồn câu hỏi `acks=all` với RF=2).
- Docs *Operations → Eligible Leader Replicas* + KIP-966 (Motivation) — hiểu "strict min ISR" là gì.
- Docs *Design → Log Compaction* mục "What guarantees does log compaction provide?" — 4 đảm bảo ra đề nguyên văn.
- Docs *Design → The Share Consumer* + Javadoc `KafkaShareConsumer` — đủ cho câu nhận diện.
- Sách *Kafka: The Definitive Guide* 2nd ed. — Chương 7 (Reliable Data Delivery: replication, broker config, producer/consumer reliability), Chương 6 phần Physical Storage (segments, retention, compaction), Chương 8 phần đầu (Exactly-Once: idempotent producer).

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(bằng tiếng Anh — văn phong đề CCDAK để làm quen.)*

- Làm hết **28 câu** không tra tài liệu, tự chấm, **ghi sổ câu sai** kèm loại lỗi (nhầm số / nhầm tầng config / đọc sót "NOT").
- Vẽ lại **từ trí nhớ**: (a) ma trận `acks` × `min.isr` 5 dòng; (b) chuỗi 4 giới hạn kích cỡ message; (c) timeline compaction head/tail + tombstone 24 h.
- **Spaced repetition:** ôn bảng PHẢI NHỚ ở mốc **1 / 3 / 7 ngày** (30 000 ms / 1 048 588 / 86 400 000 / 0.5 / 300 s / 30 s / 5 lần rất dễ lẫn).
- Chỉ sang Tuần 3 khi ≥ **70%** bộ câu hỏi và vượt Cổng tự kiểm tra. Tuần 4 sẽ có **mini-mock FUND+DEV** — câu FUND lấy từ Tuần 1–2.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
| --- | --- |
| ISR shrink | Follower không fetch / không đuổi kịp LEO trong `replica.lag.time.max.ms` = **30 000 ms** → rời ISR; đuổi kịp → tự vào lại |
| Committed / HW | Record committed khi **mọi replica trong ISR** đã ghi; HW = min LEO của ISR; **consumer chỉ đọc tới HW**; HW không tiến khi ISR < min.isr |
| `acks` | `0` không chờ · `1` leader · `all/-1` toàn ISR **và** ISR ≥ `min.insync.replicas` (mặc định **`all`** từ 3.0) |
| `min.insync.replicas` | Mặc định **1**; **chỉ tác dụng với `acks=all`**; RF=3 + min.isr=2 + acks=all chịu mất **1** broker; ISR < min.isr → `NotEnoughReplicasException` |
| Bẫy RF=2 | `acks=all` với ISR=1 vẫn thành công nếu min.isr=1 → có thể mất dữ liệu |
| Fault tolerance | **f+1** replica chịu **f** lỗi (quorum cần 2f+1) |
| Unclean election | `unclean.leader.election.enable` = **false** (chờ ISR; bật `true` = availability, mất dữ liệu) |
| ELR (KIP-966) | Thứ tự bầu **ISR → ELR → last known leader**; `eligible.leader.replicas.version=1`; **mặc định từ 4.1**; đổi `min.insync.replicas` → reset ELR; min.isr phải ở **cluster-level** |
| Preferred leader | Replica đầu trong `Replicas`; `auto.leader.rebalance.enable=true`, kiểm tra **300 s**, lệch > **10%**; ép bằng `kafka-leader-election.sh` |
| Rack | `broker.rack` → replica rải khác rack khi tạo topic |
| Segment | `segment.bytes` **1 GiB** (`log.segment.bytes`), `segment.ms` **7 ngày** (`log.roll.hours=168`); active segment không bị xoá/compact |
| Retention | `retention.ms` **604 800 000** (7 ngày), `retention.bytes` **-1** (per partition), `-1` = vĩnh viễn; quét mỗi **300 000 ms** (5 phút); xoá **cả segment đã đóng** |
| Compaction | `cleanup.policy=compact`; `min.cleanable.dirty.ratio` **0.5**; `delete.retention.ms` **86 400 000** (24 h tombstone); `min.compaction.lag.ms` **0**; bắt buộc có key; `compact,delete` được |
| 4 đảm bảo compaction | Thấy mọi message nếu bám head · thứ tự không đổi · offset không đổi · đọc từ đầu thấy ít nhất giá trị cuối mỗi key |
| Delivery semantics | At-most-once = commit **trước** xử lý / `acks=0`; at-least-once = commit **sau** (mặc định); exactly-once = idempotent + transactions + `read_committed` |
| Message size | Producer `max.request.size` **1 048 576** → topic `max.message.bytes` / broker `message.max.bytes` **1 048 588** → consumer `max.partition.fetch.bytes` 1 048 576 (`fetch.max.bytes` 50 MiB) |
| Compression / timestamp | Topic `compression.type` = **`producer`** (giữ codec producer); `message.timestamp.type` **`CreateTime`** / `LogAppendTime` |
| Share group | KIP-932 GA **4.2**; lock `share.record.lock.duration.ms` **30 s** (15–60); `share.delivery.count.limit` **5**; ACCEPT / RELEASE / REJECT; `__share_group_state`; `share.version=1`; **không thứ tự** |
| Tiered storage | `remote.storage.enable=true`; `local.retention.ms` **-2** (= retention); GA 3.9; **không** cho compacted topic |

## ⚠️ Bẫy đề hay gặp

- Thấy "`acks=all` nên mọi replica đã có dữ liệu" → dễ chọn "an toàn tuyệt đối", nhưng đúng là chỉ **ISR hiện tại**; RF=2 mất 1 broker thì `acks=all` = 1 bản.
- Thấy "đặt `min.insync.replicas=2` để chống mất dữ liệu" nhưng producer `acks=1` → dễ nghĩ đã đủ, nhưng đúng là **min.isr không áp cho `acks=1`** — vô nghĩa.
- Thấy "ISR < min.isr thì consumer cũng không đọc được" → sai: chỉ **ghi** bị chặn, **đọc** tới HW vẫn được.
- Thấy "record đã được leader ack, consumer phải thấy ngay" → sai với `acks=1`: consumer chỉ thấy tới **HW** (sau khi ISR sao chép).
- Thấy "follower tụt 1000 message thì bị loại ISR" → sai: chỉ theo **thời gian** `replica.lag.time.max.ms` (30 s); ngưỡng theo số message đã bị gỡ.
- Thấy "leader chết, không còn ISR, cluster tự bầu follower cũ" → mặc định **không** (`unclean=false`, chờ); nhưng nếu 4.1+ có **ELR** thì bầu trong ELR **không mất dữ liệu** — đọc kỹ đề có nói ELR/phiên bản không.
- Thấy "retention 1 giờ nhưng dữ liệu 2 ngày vẫn còn" → dễ nghĩ bug, nhưng đúng là **active segment chưa roll** (1 GB / 7 ngày) + quét 5 phút một lần.
- Thấy "`retention.bytes=1GB` nên topic tối đa 1 GB" → sai: **per partition** → × số partition.
- Thấy "compacted topic luôn có đúng 1 record mỗi key" → sai: **ít nhất** giá trị cuối; head còn trùng; chỉ dọn segment đã đóng khi dirty ≥ 0.5.
- Thấy "xoá key trong compacted topic bằng cách gửi value rỗng `""`" → sai: phải **`null`** (tombstone); và tombstone sống **24 h** (`delete.retention.ms`).
- Thấy `RecordTooLargeException` → chỉ tăng `message.max.bytes` broker là chưa đủ nếu lỗi ở **client** (`max.request.size`); đề hay hỏi "cần đổi ở đâu" → cả producer **và** topic/broker.
- Thấy "cần nhiều consumer hơn partition, ack từng message, kiểu queue" → dễ chọn "tăng partition", nhưng đúng là **share group (KIP-932)** — trừ khi đề cần **thứ tự**.
- Thấy "share group đảm bảo thứ tự trong partition như consumer group" → **sai**, share group đánh đổi thứ tự lấy chia sẻ.
- Thấy "commit offset rồi mới xử lý để không xử lý trùng" → đúng là **at-most-once** (có thể mất), không phải exactly-once.

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
| --- | --- |
| "no data loss + survive 1 broker + keep writing" | **RF=3, `min.insync.replicas=2`, `acks=all`** |
| "`NotEnoughReplicasException`" | ISR < `min.insync.replicas` với `acks=all` → chờ broker hồi / hạ min.isr |
| "consumer can't see records the producer already got ack for" | **High watermark** (chưa replicate đủ ISR) |
| "follower out of sync after 30 s" | **`replica.lag.time.max.ms`** → ISR shrink |
| "all ISR down, prefer availability, accept loss" | **`unclean.leader.election.enable=true`** |
| "all ISR down, still elect safely, 4.1+" | **ELR (KIP-966)** — `Elr:` trong describe |
| "leaders not returning to original broker after restart" | **`auto.leader.rebalance.enable`** (300 s) / `kafka-leader-election.sh --election-type PREFERRED` |
| "spread replicas across AZs" | **`broker.rack`** |
| "old data not deleted despite retention" | **Active segment** chưa roll → `segment.ms` / `segment.bytes`; quét 5 phút |
| "keep data forever" | **`retention.ms=-1`** |
| "keep only latest value per key" / "changelog" / "CDC snapshot" | **`cleanup.policy=compact`** |
| "delete a key in compacted topic" | **Tombstone** (value `null`) + `delete.retention.ms` 24 h |
| "compaction happens too rarely" | **↓ `min.cleanable.dirty.ratio`** (0.5) |
| "latest per key but expire after N days" | **`cleanup.policy=compact,delete`** |
| "commit before processing" / "commit after processing" | **At-most-once** / **at-least-once** |
| "resend without duplicates within a partition" | **Idempotent producer** (PID + sequence) |
| "`RecordTooLargeException`" | **`max.request.size`** (producer) + **`max.message.bytes`** (topic) / `message.max.bytes` (broker) |
| "broker should not recompress" | **`compression.type=producer`** |
| "timestamp = when broker wrote it" | **`LogAppendTime`** |
| "queue semantics, more consumers than partitions, per-record ack" | **Share group (Queues for Kafka, KIP-932)** — `kafka-console-share-consumer.sh` |
| "share consumer failed transiently / poison record" | **`RELEASE`** / **`REJECT`**; quá 5 lần → archive |
| "cheap long retention, no compaction" | **Tiered storage** (`remote.storage.enable=true`) |

## 🧪 Lab checklist

- [ ] Lab 2.1 ⭐ — Dừng `kafka-2` + `kafka-3`: producer `acks=all` báo `NotEnoughReplicas`, `acks=1` vẫn ghi; `kcc` vẫn đọc; bật lại → `ok` ngay khi ISR ≥ 2.
- [ ] Lab 2.2 — Dừng 1 follower: `Isr` mất node đó sau ≤ 30 s, `kafka-log-dirs.sh` thấy `offsetLag` > 0 khi bật lại rồi về 0 và ISR đủ 3; `kafka-get-offsets.sh --time -1` = HW.
- [ ] Lab 2.3 — Topic `retention.ms=60000 segment.ms=10000`: sau lần quét, earliest offset (`--time -2`) dời lên; `kafka-delete-records.sh` dời ngay lập tức.
- [ ] Lab 2.4 ⭐ — Compacted topic: produce `user-1` 5 lần + tombstone `user-2`; sau roll + compaction đọc `--from-beginning` chỉ còn giá trị cuối; tombstone biến mất sau `delete.retention.ms=10000`.
- [ ] Lab 2.5 — Record 2 MB: console producer lỗi `max.request.size`; kafkajs lỗi `MESSAGE_TOO_LARGE`; sửa `max.message.bytes` topic + `max.request.size` → thành công.
- [ ] Lab 2.6 — 2 `kafka-console-share-consumer.sh` cùng group trên topic 1 partition **cùng nhận** message; `kafka-share-groups.sh --describe --members` in 2 member cùng `tasks:0`.
- [ ] Lab 2.7 — `kcfg --alter` topic/broker/`--entity-default`; `--describe --all` phân biệt DYNAMIC/STATIC/DEFAULT; config read-only bị từ chối.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **RF=3, `min.insync.replicas=2`, `acks=all`: mất 1 broker thì sao, mất 2 thì sao, consumer thì sao?**
  **Đáp án gọn:** mất 1 → ISR=2 ≥ 2, vẫn ghi; mất 2 → ISR=1 < 2 → `NotEnoughReplicasException`, ngừng ghi nhưng **không mất dữ liệu committed**; consumer vẫn đọc tới HW.
- **Vì sao `acks=all` với RF=2 không đủ an toàn?**
  **Đáp án gọn:** `acks=all` chỉ chờ **ISR hiện tại**; mất 1 broker ISR=1 → ghi vẫn thành công (nếu min.isr=1) → broker cuối chết là mất. Cần RF=3 + min.isr=2.
- **High watermark là gì, khác LEO thế nào, ai bị giới hạn bởi nó?**
  **Đáp án gọn:** LEO = offset kế tiếp của 1 replica; HW = offset committed = min LEO của ISR; **consumer chỉ đọc tới HW**; HW không tiến khi ISR < min.isr.
- **Thứ tự bầu leader khi ELR bật? ELR có thay `unclean.leader.election.enable` không?**
  **Đáp án gọn:** ISR → ELR (chưa fenced) → last known leader; không thay — unclean vẫn mặc định `false`, ELR chỉ thêm ứng viên an toàn (mặc định từ 4.1, đổi `min.insync.replicas` là reset ELR).
- **Retention 1 giờ nhưng data 2 ngày vẫn đọc được — vì sao, sửa sao?**
  **Đáp án gọn:** retention xoá **cả segment đã đóng**, không đụng active segment (1 GB / 7 ngày mới roll) và chỉ quét mỗi 5 phút; hạ `segment.ms`/`segment.bytes` hoặc dùng `kafka-delete-records.sh`.
- **Kể 4 đảm bảo của log compaction và cách xoá 1 key.**
  **Đáp án gọn:** bám head thấy mọi message; thứ tự không đổi; offset không đổi; đọc từ đầu thấy ít nhất giá trị cuối mỗi key. Xoá = gửi **tombstone** (key + value `null`), giữ `delete.retention.ms` = 24 h; compacted topic bắt buộc có key.
- **Producer báo `RecordTooLargeException` với record 2 MB — đổi gì, ở đâu?**
  **Đáp án gọn:** `max.request.size` (producer, 1 048 576) **và** `max.message.bytes` topic / `message.max.bytes` broker (1 048 588); consumer/follower không kẹt nhờ KIP-74 nhưng nên nâng `max.partition.fetch.bytes`/`replica.fetch.max.bytes`; tốt hơn: nén hoặc claim-check.
- **Share group khác consumer group ở 4 điểm nào, và mất gì?**
  **Đáp án gọn:** partition chia sẻ nhiều consumer; consumer > partition vẫn có việc; ack **từng record** (ACCEPT/RELEASE/REJECT) với lock 30 s; đếm delivery (limit 5). Mất **thứ tự**. Tool `kafka-console-share-consumer.sh` / `kafka-share-groups.sh`, GA 4.2.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được (6 file: replication/ISR, ELR, topic configs, log compaction, delivery semantics, share groups).

- Apache Kafka Docs 4.3: *Design → Replication* (ISR, committed, unclean election, availability & durability guarantees, replica management).
- Apache Kafka Docs 4.3: *Operations → Eligible Leader Replicas*; KIP-966 (cwiki) phần Motivation.
- Apache Kafka Docs 4.3: *Configuration → Topic-Level Configs* + *Broker Configs* (`log.*`, `message.max.bytes`, `replica.lag.time.max.ms`, `group.share.*`).
- Apache Kafka Docs 4.3: *Design → Log Compaction*, *Message Delivery Semantics*, *The Share Consumer*; *Operations → Managing share groups*; Javadoc `KafkaShareConsumer`.
- KIP-932 (Queues for Kafka), KIP-405 (Tiered Storage), KIP-74 (fetch response size) trên cwiki.apache.org.
- Khoá học: Confluent Developer — *Apache Kafka 101* (Replication, Storage & Retention), *Kafka Internals* (Data Durability and Availability Guarantees, Log Compaction — miễn phí); Stephane Maarek — *Learn Apache Kafka for Beginners v3* (Topic Replication, ISR, acks, Log Cleanup Policies); sách *Kafka: The Definitive Guide* 2nd ed. chương 6 (Physical Storage), 7 (Reliable Data Delivery), 8 (Exactly-Once).

## ✅ Checklist hoàn thành Tuần 2

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (30 000 ms / 1 048 588 / 604 800 000 / 86 400 000 / 0.5 / 300 s / 30 s / 5 lần)
- [ ] Vẽ lại được ma trận `acks` × `min.insync.replicas` và chuỗi 4 giới hạn kích cỡ message từ trí nhớ
- [ ] Hoàn thành 7 lab, giữ lại `compaction.mjs` và `acks-probe.mjs` cho Tuần 3
- [ ] Làm xong 28 câu [questions.md](questions.md) ≥ 70%, ghi sổ câu sai
- [ ] Vượt Cổng tự kiểm tra (8 câu)
