# 🟦 Tuần 1 — Kiến trúc Kafka & `KRaft` + Dựng cluster + CLI

> **Domain CCDAK:** Fundamentals (FUND, 23%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 1/10 — nền tảng cho toàn bộ 9 tuần sau, chưa có checkpoint
>
> **Điều hướng:** [🏠 Kế hoạch tổng](../../KAFKA-STUDY-PLAN.md) · [Tuần 2 ➡️](../week-02/README.md)

## 🎯 Mục tiêu tuần này

- **Giải thích được** Kafka là gì trong 30 giây: *distributed commit log* = pub/sub + lưu trữ bền + xử lý stream, và vì sao "topic là log, không phải queue".
- **Phân biệt được** broker / cluster / topic / partition / offset / segment / record — chỉ ra từng thứ nằm ở đâu trên đĩa (`.log` / `.index` / `.timeindex`).
- **Tự tay** dựng 2 cluster chuẩn bằng Docker (`docker-compose.single.yml` 1 node và `docker-compose.cluster.yml` 3 broker + 1 controller) — mọi tuần sau dùng lại.
- **Cấu hình được** `KRaft` cơ bản: `process.roles`, `node.id`, `controller.quorum.voters` / `controller.quorum.bootstrap.servers`, `kafka-storage.sh format`, và đọc được `__cluster_metadata`.
- **Thao tác trôi chảy** 8 CLI tool chuẩn với `--bootstrap-server`, kèm alias `kt` / `kcp` / `kcc` / `kcg`.
- **Viết được** producer + consumer đầu tiên bằng Node.js (`kafkajs`) và **thấy bằng mắt** key → cùng partition, offset tăng dần, leader đổi khi broker chết.
- **Chốt nền:** trả lời trôi chảy 8 câu ở Cổng tự kiểm tra và đạt ≥ 70% bộ [questions.md](questions.md) trước khi sang Tuần 2.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Kafka là gì — 3 khả năng trong 1 nền tảng (hay hỏi dạng định nghĩa)**

- Kafka = **distributed commit log**: dữ liệu ghi **append-only**, **bất biến** (immutable), đọc theo **offset**, giữ lại theo **retention** — KHÔNG xoá khi đã đọc. Đọc 1 record xong nó vẫn còn đó, consumer khác đọc lại được → **replay**.
- 3 khả năng lõi (docs gọi là *event streaming platform*): **publish/subscribe** (Producer/Consumer API), **store** bền vững theo thời gian tuỳ ý, **process** (`Kafka Streams`, `ksqlDB`). Cộng thêm `Kafka Connect` để nối hệ thống ngoài và `Admin API` để quản trị → **5 API**.
- Use case chuẩn: messaging decouple, activity tracking, log aggregation, metrics, stream processing, event sourcing / CDC, commit log cho hệ phân tán.
- ⚠️ "Topic là **log**, không phải queue": queue xoá message sau khi consume; Kafka giữ theo retention (mặc định **7 ngày**), nhiều consumer group đọc **độc lập** cùng dữ liệu.

**2. Bộ thuật ngữ cấu trúc — nhớ theo tầng từ to xuống nhỏ**

| Tầng | Khái niệm | Điểm cần thuộc |
| --- | --- | --- |
| Cluster | Nhóm **broker** + **controller quorum** dùng chung `cluster.id` | Client chỉ cần biết 1–3 địa chỉ trong `bootstrap.servers` |
| Broker | 1 tiến trình Kafka server (`process.roles=broker`), định danh `node.id` | Lưu partition, phục vụ produce/fetch; **không** biết gì về nhau ngoài metadata từ controller |
| Topic | Tên logic của luồng sự kiện (như "folder") | Multi-producer, multi-subscriber; `auto.create.topics.enable=true` mặc định (production nên tắt) |
| Partition | Log **có thứ tự** con của topic, đơn vị **song song + phân tán** | Thứ tự **chỉ đảm bảo trong 1 partition**; số partition **chỉ tăng, không giảm**; `num.partitions` mặc định **1** |
| Replica | Bản sao partition trên broker khác; **1 leader** + N−1 follower | `default.replication.factor` mặc định **1**; production **RF=3**; RF ≤ số broker |
| Segment | File vật lý trên đĩa của 1 partition | Lăn (roll) khi đủ **1 GB** (`log.segment.bytes`) hoặc **7 ngày** (`log.roll.hours=168`) |
| Record | 1 sự kiện: key / value / headers / timestamp / offset | Offset = số nguyên 64-bit tăng dần **trong partition**, bắt đầu từ 0 |

- **Đường dẫn trên đĩa:** `log.dirs/<topic>-<partition>/` chứa `00000000000000000000.log` (dữ liệu), `.index` (offset → vị trí byte, thưa: 1 entry mỗi `log.index.interval.bytes` = **4096 B**), `.timeindex` (timestamp → offset), `leader-epoch-checkpoint`, `partition.metadata`. Tên file = **base offset** của record đầu tiên trong segment.
- Segment đang ghi = **active segment**, KHÔNG bao giờ bị retention xoá; retention xoá **cả segment** (không xoá lẻ record) khi timestamp lớn nhất của segment quá hạn.
- **Record (message format v2 / RecordBatch):** batch header (baseOffset, partitionLeaderEpoch, magic=2, CRC, attributes, producerId/epoch/baseSequence cho idempotence) + danh sách record (offsetDelta, timestampDelta, key, value, headers). Compression áp lên **cả batch**.
- **Timestamp:** `message.timestamp.type` = **`CreateTime`** (mặc định — producer gán, có thể lệch giờ) hoặc **`LogAppendTime`** (broker gán lúc ghi). Đề hỏi "muốn timestamp phản ánh lúc broker nhận" → `LogAppendTime`.
- **Key:** có key → **murmur2(key) mod số partition** → cùng key luôn cùng partition (miễn số partition không đổi ⚠️). Không key → **sticky partitioner** (dồn vào 1 partition cho tới khi batch đầy rồi đổi).

**3. Producer / Consumer / Consumer group — tổng quan (Tuần 3–4 đi sâu)**

- **Producer** gửi tới **leader** của partition; `acks` mặc định **`all`**, `enable.idempotence` mặc định **true** (từ 3.0). Producer tự batch (`linger.ms` **5 ms** ở 4.0, `batch.size` **16 KB**).
- **Consumer** kéo (pull) từ leader theo offset; tự quản offset của mình; commit vào topic nội bộ **`__consumer_offsets`** (**50 partitions**, compacted).
- **Consumer group** (`group.id`): mỗi partition được gán cho **đúng 1 consumer** trong group; số consumer > số partition → consumer dư **ngồi chơi**. Hai group khác nhau đọc **độc lập** toàn bộ dữ liệu → đây chính là pub/sub fan-out của Kafka.
- Cả producer và consumer đều **không biết nhau** (fully decoupled) — Kafka giữ dữ liệu, không giữ trạng thái của consumer ngoài offset.

**4. Replication cơ bản — nhận diện `leader` / `follower` / `ISR` (Tuần 2 đi sâu)**

- Mỗi partition có **1 leader** nhận mọi ghi/đọc (từ 2.4 có thể đọc từ follower gần nhất, tuỳ chọn) và **follower** fetch từ leader như một consumer.
- **ISR (In-Sync Replicas)** = leader + các follower "đuổi kịp" trong `replica.lag.time.max.ms` = **30 000 ms**. Follower tụt quá → controller bỏ khỏi ISR. Broker sống lại → fetch đuổi kịp → **tự quay lại ISR**.
- Record **committed** = mọi replica trong ISR đã ghi. Consumer chỉ đọc tới **High Watermark** (offset committed).
- Kafka chịu được **f** lỗi với **f+1** replica (khác majority quorum cần 2f+1). Broker chết → controller chọn leader mới **trong ISR**; `unclean.leader.election.enable=false` mặc định (thà mất availability còn hơn mất dữ liệu).
- `min.insync.replicas` mặc định **1**; production chuẩn: **RF=3 + min.isr=2 + acks=all**.

**5. `KRaft` — Kafka tự quản metadata, không còn `ZooKeeper` (rất hay hỏi ở 4.x)**

- **Tại sao bỏ ZooKeeper (KIP-500):** 2 hệ thống phải cài/bảo mật/giám sát riêng; metadata bị chia đôi (ZK vs controller cache) → dễ lệch; controller failover chậm vì phải **load toàn bộ metadata từ ZK** (O(số partition)); giới hạn ~200k partition. `KRaft` gom metadata vào **1 event log** trong Kafka, controller mới đã có sẵn metadata trong RAM → **failover gần tức thời**, mục tiêu **hàng triệu partition**.
- **Controller quorum:** 3 hoặc 5 node chạy `process.roles=controller`, bầu **1 active controller** bằng Raft (biến thể event-based). Quorum sống khi **đa số** còn: 3 chịu 1 lỗi, 5 chịu 2 lỗi. Không dùng số chẵn.
- **`__cluster_metadata`:** topic nội bộ **1 partition**, replicate giữa các controller; broker **fetch** metadata từ active controller (giống consumer) thay vì bị push. Có snapshot (`.checkpoint`) để log không phình vô hạn. Mọi thay đổi (tạo topic, đổi leader, đăng ký broker, ISR đổi) là 1 record trong log này.
- **`process.roles`:** `broker` | `controller` | `broker,controller` (**combined** — chỉ dùng dev/test, docs khuyên **không** cho production vì mất cách ly). Mỗi node có `node.id` duy nhất toàn cluster (dùng chung không gian số giữa broker và controller).
- **Listener riêng cho controller:** `controller.listener.names=CONTROLLER` (mặc định port **9093**), không được trùng `inter.broker.listener.name`. Broker-only vẫn phải khai `controller.listener.names` + `controller.quorum.*` để biết đường tới quorum.
- **Static vs dynamic quorum:**

| | Static quorum (cũ) | Dynamic quorum (KIP-853, 3.9+, mặc định khi format mới) |
| --- | --- | --- |
| Config | `controller.quorum.voters=1@c1:9093,2@c2:9093,3@c3:9093` (mọi node phải khai đủ, **deprecated** ở 4.x) | `controller.quorum.bootstrap.servers=c1:9093,c2:9093` (chỉ cần địa chỉ để tìm quorum) |
| Đổi thành viên | Phải sửa config + restart toàn bộ | `kafka-metadata-quorum.sh add-controller` / `remove-controller` online |
| Format | `kafka-storage.sh format -t <id> -c server.properties` | `format --standalone` (1 voter đầu) hoặc `--initial-controllers "id@host:port:dirUUID,..."`; node vào sau dùng `--no-initial-controllers` |
| Định danh voter | `node.id` | `node.id` + **directory.id** (UUID của log dir, tránh voter "hồi sinh" với đĩa trống) |
| Kiểm tra | — | `kafka-features.sh describe` → `kraft.version=1` là dynamic |

- **`kafka-storage.sh`:** `random-uuid` sinh `cluster.id` (22 ký tự base64); `format` ghi `meta.properties` (cluster.id, node.id, directory.id) vào **mọi** `log.dirs` — broker **từ chối start** nếu chưa format hoặc `cluster.id` lệch với quorum. Docker image `apache/kafka` tự format khi có env `CLUSTER_ID`.
- **Lộ trình:** KRaft production-ready **3.3**; 3.9 là **bridge release** cuối cùng còn ZooKeeper (migration ZK→KRaft phải qua 3.9); **4.0 gỡ hẳn ZooKeeper**.

**6. Kafka 4.0 → 4.3 — điều gì đổi (đề CCDAK mới đã cập nhật)**

| Thay đổi | Chi tiết cần nhớ |
| --- | --- |
| Gỡ `ZooKeeper` | Chỉ còn `KRaft`; không có `--zookeeper` ở bất kỳ CLI nào |
| Java | Broker / `Connect` / tools: **Java 17+**; clients / `Streams`: **Java 11+** |
| Protocol baseline | Bỏ message format v0/v1 (KIP-724), bỏ API version cũ (KIP-896) → client/broker phải **≥ 2.1** mới nói chuyện được với 4.0 |
| KIP-848 | Consumer rebalance protocol mới **GA 4.0**, opt-in `group.protocol=consumer`; classic protocol **deprecated 4.3** |
| KIP-966 ELR | *Eligible Leader Replicas*: preview 4.0 → GA 4.1 — thêm tập replica đủ điều kiện làm leader dù rời ISR, giảm mất dữ liệu khi `min.isr` bị vi phạm |
| KIP-932 Queues | *Share groups* (cooperative consumption, ack từng record, không gán partition cứng): early access 4.0 → preview 4.1 → **GA 4.2** |
| KIP-1030 defaults | `linger.ms` **0 → 5 ms**; `num.recovery.threads.per.data.dir` **1 → 2**; siết validation nhiều config |
| KIP-853 | Dynamic controller quorum (từ 3.9), 4.x khuyến nghị dùng thay `controller.quorum.voters` |
| KIP-1147 | Thống nhất tham số CLI: mọi tool dùng `--bootstrap-server`; `--property`/`--producer-property` dần đổi tên (xem mục 8) |
| Log4j2, Jakarta EE 10 | Broker chuyển Log4j → **Log4j2** (KIP-653); Connect REST dùng Jakarta |

**7. `bootstrap.servers`, metadata discovery và bẫy `advertised.listeners`**

- Client mở kết nối tới **1** địa chỉ bất kỳ trong `bootstrap.servers` → gửi **MetadataRequest** → nhận danh sách **toàn bộ broker** (theo `advertised.listeners`) + leader từng partition → **kết nối thẳng tới leader**. Bootstrap list chỉ để "gõ cửa"; nên ghi **2–3 broker** để chịu lỗi, không cần ghi hết.
- `listeners` = nơi broker **bind** (`PLAINTEXT://:9092`); `advertised.listeners` = địa chỉ broker **tự giới thiệu** cho client trong metadata. Client dùng địa chỉ advertised, **không** dùng địa chỉ trong bootstrap.
- ⚠️ **Bẫy Docker kinh điển:** trong container connect được (`localhost:9092`), từ host `docker exec` xong nhưng app trên host báo `ECONNREFUSED`/timeout tới `kafka:19092` — vì broker advertise hostname nội bộ Docker. Cách chuẩn: **2 listener** — `PLAINTEXT://:19092` advertise `kafka:19092` (nội bộ) + `PLAINTEXT_HOST://:9092` advertise `localhost:9092` (cho host), map qua `listener.security.protocol.map`, chọn `inter.broker.listener.name=PLAINTEXT`.
- Tên listener tuỳ ý (`INTERNAL`, `EXTERNAL`…); 4 security protocol: `PLAINTEXT`, `SSL`, `SASL_PLAINTEXT`, `SASL_SSL` (Tuần 7).

**8. Bộ CLI chuẩn — thuộc tên tool và tham số hay gặp**

| Tool (`/opt/kafka/bin/`) | Việc chính | Tham số cần nhớ |
| --- | --- | --- |
| `kafka-topics.sh` | `--create/--list/--describe/--alter/--delete` | `--partitions`, `--replication-factor`, `--config retention.ms=…`; `--alter --partitions` chỉ **tăng** |
| `kafka-console-producer.sh` | Gõ tay message | `--property parse.key=true --property key.separator=:` (KIP-1147 đổi sang `--formatter-property`, 4.3 vẫn nhận `--property`); `--producer-property acks=all` |
| `kafka-console-consumer.sh` | Đọc topic ra màn hình | `--from-beginning`, `--group`, `--partition N --offset M`, `--property print.key=true`/`print.partition=true`/`print.offset=true`/`print.timestamp=true`, `--max-messages` |
| `kafka-consumer-groups.sh` | Xem/reset offset group | `--describe --group g` (LAG), `--reset-offsets --to-earliest/--to-latest/--shift-by/--to-datetime --execute` (group phải **inactive**), `--delete` |
| `kafka-configs.sh` | Xem/đổi config động | `--entity-type topics|brokers|clients|users --entity-name x --alter --add-config k=v` / `--delete-config k`; `--describe --all` |
| `kafka-metadata-quorum.sh` | Trạng thái quorum KRaft | `describe --status` (LeaderId, HighWatermark, voters/observers), `describe --replication`, `add-controller`/`remove-controller` |
| `kafka-metadata-shell.sh` | Duyệt `__cluster_metadata` như filesystem | `--snapshot <dir>/__cluster_metadata-0/*.checkpoint` rồi `ls /image/topics/…` |
| `kafka-log-dirs.sh` | Dung lượng từng partition trên từng broker | `--describe --topic-list orders --broker-list 2,3` → JSON size/offsetLag |
| `kafka-dump-log.sh` | Soi file segment | `--files x.log --print-data-log`; `--files x.index`; `--cluster-metadata-decoder` cho metadata log |
| `kafka-storage.sh` | Format log dir KRaft | `random-uuid`, `format -t <id> -c server.properties [--standalone]` |

- KIP-1147: mọi tool nhận **`--bootstrap-server`** (danh sách `host:port,host:port`); `--broker-list` (console producer cũ) và `--zookeeper` đã **bị gỡ**. Tool quản trị controller dùng `--bootstrap-controller host:9093`.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 Chi tiết từng bước trong [labs.md](labs.md). Tuần này lab **tạo ra 2 file compose chuẩn** mà mọi tuần sau tham chiếu — đừng bỏ qua.

- **Lab 1.1** — Cài Docker + `docker-compose.single.yml` (`apache/kafka:4.3.1`, `KRaft` combined, port 9092). Kiểm chứng bằng `kafka-metadata-quorum.sh describe --status`.
- **Lab 1.2 ⭐** — `docker-compose.cluster.yml` 3 broker (9092/9094/9096) + 1 controller, `min.insync.replicas=2`, `default.replication.factor=3`. Hiểu vì sao alias phải đổi `bootstrap` sang listener nội bộ.
- **Lab 1.3** — CLI: topic 3 partition RF 3 → describe → produce có key → consume `--from-beginning` in key/partition/offset → chứng minh cùng key → cùng partition.
- **Lab 1.4 ⭐** — Node.js `kafkajs`: `admin.createTopics`, producer `send` in `partition/baseOffset`, consumer group `eachMessage`; chạy 2 consumer cùng group thấy chia partition.
- **Lab 1.5** — Soi đĩa: `kafka-log-dirs.sh`, `ls` thư mục partition, `kafka-dump-log.sh` đọc `.log`/`.index`, `kafka-dump-log.sh --cluster-metadata-decoder` + `kafka-metadata-shell.sh` đọc `__cluster_metadata`.
- **Lab 1.6** — Kill 1 broker → `describe` thấy leader đổi, ISR co lại, producer vẫn ghi (ISR=2 ≥ min.isr) → bật lại → ISR hồi đủ 3.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**1. Kafka vs `SQS` vs `Kinesis` vs `RabbitMQ` — bảng quyết định (CCDAK không hỏi AWS, nhưng phỏng vấn và Tuần 9 có)**

| Tiêu chí | Apache Kafka | `Amazon SQS` | `Amazon Kinesis Data Streams` | `RabbitMQ` (AMQP) |
| --- | --- | --- | --- | --- |
| Mô hình | Log phân tán, pull, consumer group | Queue, pull, 1 message → 1 consumer | Log phân tán managed, shard | Broker push tới queue qua exchange/routing key |
| Thứ tự | Trong partition (theo key) | FIFO queue: trong message group; Standard: best-effort | Trong shard (theo partition key) | Trong queue (1 consumer) |
| Replay | ✅ theo offset, retention tuỳ ý (tiered → không giới hạn) | ❌ (đọc xong xoá) | ✅ 24h mặc định → 365 ngày | ❌ (ack xong xoá; Streams plugin thì có) |
| Nhiều consumer đọc cùng data | ✅ nhiều group độc lập | ❌ (cần `SNS` fan-out) | ✅ nhiều app / enhanced fan-out | ✅ qua exchange fan-out (mỗi queue 1 bản) |
| Scale đơn vị | partition | tự động | shard (1 MB/s ghi, 2 MB/s đọc) | queue / node |
| Đơn vị lưu | byte record ≤ `message.max.bytes` ~1 MB | 256 KB (1 MiB mới) | 1 MB | không giới hạn cứng |
| Ecosystem | `Connect`, `Streams`, `Schema Registry` | Tích hợp AWS (Lambda ESM) | Firehose, Lambda, Managed Flink | Routing linh hoạt, plugin |
| Vận hành | Tự quản (hoặc `MSK` / Confluent Cloud) | Serverless hoàn toàn | Managed | Tự quản (hoặc `Amazon MQ`) |
| Chọn khi | Throughput lớn, replay, nhiều consumer, stream processing | Job queue đơn giản, decouple | Streaming trong AWS, ít vận hành | Routing phức tạp, RPC, per-message TTL/priority |

**2. Quyết định số partition & RF ban đầu**

- Partition = giới hạn **song song tối đa** của 1 consumer group. Công thức thô: `max(throughput_ghi / throughput_1_partition, throughput_đọc / throughput_1_consumer)`, thêm dư 20–30%. Ví dụ ghi 60 MB/s, 1 partition ~10 MB/s → tối thiểu 6, chọn 8–12.
- Quá nhiều partition → nhiều file mở, leader election lâu hơn, latency end-to-end tăng (leader phải replicate nhiều hơn), producer buffer nhiều batch. Quá ít → không scale consumer.
- ⚠️ Tăng partition sau này **phá vỡ key → partition mapping** (record cũ key K ở partition 1, record mới key K có thể sang partition 5). Nếu ordering theo key quan trọng → chọn đủ ngay từ đầu hoặc tạo topic mới + migrate.
- RF: dev **1**, production **3** (chịu 2 broker chết vẫn còn 1 bản; kết hợp `min.isr=2` chịu 1 broker chết mà vẫn ghi được). RF không thể > số broker khi tạo.

**3. Đọc thêm (30–40 phút)**

- Docs `Design → Persistence & Efficiency`: vì sao ghi tuần tự vào đĩa + pagecache + `sendfile` zero-copy nhanh hơn giữ trong RAM JVM.
- Docs `Implementation → Log`: format file segment, cách tìm offset (binary search trên `.index`), recovery bằng CRC.
- Kafka 4.0 release announcement + Confluent "KRaft" learn page — hiểu tường tận vì sao bỏ ZooKeeper (câu hỏi "lý do" xuất hiện ở đề).
- Sách *Kafka: The Definitive Guide* 2nd ed. — Chương 1 (Meet Kafka), Chương 2 (Installing Kafka: hardware, số partition, `log.dirs`), Chương 6 phần đầu (Kafka Internals: controller, replication, request processing, physical storage).

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(bằng tiếng Anh — văn phong đề CCDAK để làm quen.)*

- Làm hết 30 câu **không tra tài liệu**, tự chấm, **ghi sổ câu sai** kèm lý do (nhầm số? nhầm khái niệm? đọc sót "NOT"?).
- Vẽ lại **từ trí nhớ** sơ đồ: client → bootstrap → metadata → leader; và cây thư mục `log.dirs/orders-0/`.
- **Spaced repetition:** ôn bảng PHẢI NHỚ ở mốc **1 / 3 / 7 ngày** (các số 1 GB / 7 ngày / 4096 / 30 000 ms / 9092 / 9093 / 50 partitions rất dễ lẫn).
- Chỉ sang Tuần 2 khi ≥ **70%** bộ câu hỏi và vượt Cổng tự kiểm tra.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
| --- | --- |
| Kafka là gì | **Distributed commit log**: append-only, immutable, đọc theo offset, giữ theo retention — "topic là log, không phải queue" |
| 5 API | `Admin`, `Producer`, `Consumer`, `Kafka Streams`, `Kafka Connect` |
| Thứ tự đảm bảo | **Chỉ trong 1 partition**; cùng key → cùng partition (murmur2 mod N) miễn N không đổi |
| Số partition | Mặc định `num.partitions` **1**; chỉ **tăng** được, không giảm; tăng → phá mapping key |
| Replication factor | Mặc định **1**; production **3**; RF ≤ số broker; `min.insync.replicas` mặc định **1** (prod **2**) |
| ISR | Follower tụt quá `replica.lag.time.max.ms` = **30 000 ms** → rời ISR; đuổi kịp → tự vào lại |
| Unclean election | `unclean.leader.election.enable` = **false** (ưu tiên nhất quán hơn availability) |
| Segment | `log.segment.bytes` **1 GB** (1 073 741 824); `log.roll.hours` **168**; file `.log` / `.index` / `.timeindex`, tên = base offset |
| Offset index | Thưa, 1 entry mỗi `log.index.interval.bytes` = **4096 B** (4 KB) |
| Retention | `log.retention.hours` **168** (7 ngày); `log.retention.bytes` **-1**; xoá **cả segment**, không xoá active segment; kiểm tra mỗi **5 phút** |
| Kích cỡ record | `message.max.bytes` **1 048 588 B** (~1 MB); topic-level `max.message.bytes` |
| Timestamp | `message.timestamp.type` **`CreateTime`** (producer) / `LogAppendTime` (broker) |
| Port | Broker **9092**, controller **9093**, Schema Registry 8081, Connect 8083 |
| KRaft quorum | **3 hoặc 5** controller; đa số phải sống (3→1 lỗi, 5→2 lỗi); metadata trong `__cluster_metadata` **1 partition** |
| `process.roles` | `broker` / `controller` / `broker,controller` (combined chỉ dev) |
| Static vs dynamic | `controller.quorum.voters` (deprecated) vs `controller.quorum.bootstrap.servers` (KIP-853, 3.9+, `kraft.version=1`) |
| Format | `kafka-storage.sh random-uuid` → `format -t <id> -c … [--standalone]`; broker không start nếu chưa format |
| Java 4.0 | Broker/Connect/tools **17+**; clients/Streams **11+**; baseline protocol **2.1** |
| Kafka 4.x KIP | 848 consumer protocol GA 4.0; 932 share groups GA **4.2**; 966 ELR; 1030 `linger.ms=5`; 500 bỏ ZK; 853 dynamic quorum |
| `__consumer_offsets` | **50 partitions**, compacted; `offsets.retention.minutes` **10080** (7 ngày) |
| Listener | `listeners` = bind; `advertised.listeners` = địa chỉ trả trong metadata → client dùng cái này |

## ⚠️ Bẫy đề hay gặp

- Thấy "đảm bảo thứ tự **toàn topic**" → dễ chọn "tăng partition", nhưng đúng là **1 partition** (hoặc cùng key vào 1 partition) — Kafka chỉ đảm bảo thứ tự trong partition.
- Thấy "consumer nhiều hơn partition để tăng tốc" → dễ nghĩ tốt, nhưng đúng là consumer dư **idle**; muốn song song hơn phải **tăng partition**.
- Thấy "tăng partition cho topic đã có key" → dễ coi vô hại, nhưng đúng là **phá key→partition mapping**, record cũ và mới cùng key có thể ở partition khác.
- Thấy "giảm số partition" → dễ chọn `kafka-topics.sh --alter --partitions 3`, nhưng đúng là **không thể giảm**; phải tạo topic mới.
- Thấy "connect được từ trong container, không được từ host" → dễ nghĩ firewall/port, nhưng đúng là **`advertised.listeners`** trả hostname nội bộ.
- Thấy "client chỉ cấu hình 1 broker trong `bootstrap.servers`, broker đó chết" → dễ nghĩ client vẫn chạy vì đã có metadata, nhưng đúng là **client mới không bootstrap được**; nên ghi 2–3 broker. (Client đang chạy vẫn ổn vì đã biết các broker khác.)
- Thấy "Kafka 4.0 vẫn có thể chạy với ZooKeeper nếu cấu hình" → **sai**, 4.0 gỡ hẳn; migrate phải qua **3.9**.
- Thấy "combined mode `broker,controller` cho production để tiết kiệm máy" → dễ chấp nhận, nhưng docs nói **chỉ dev/test**.
- Thấy "quorum 4 controller chịu 2 lỗi" → sai: 4 node đa số là 3 → chịu **1** lỗi, y như 3 node; luôn dùng **số lẻ**.
- Thấy "retention xoá đúng record quá 7 ngày" → sai: xoá **cả segment** khi record mới nhất trong segment quá hạn; record có thể sống lâu hơn retention.
- Thấy `message.max.bytes` = 1 MB tròn → đề cũ; giá trị thật **1 048 588** (1 MB + 12 B header).
- Thấy "record timestamp là lúc broker nhận" → sai mặc định; `CreateTime` là lúc **producer** tạo; cần broker gán thì đặt `LogAppendTime`.
- Thấy "`--zookeeper localhost:2181`" trong đáp án CLI → **loại ngay** (đã gỡ), dùng `--bootstrap-server`.

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
| --- | --- |
| "append-only, immutable, replay, retention" | **Commit log** — topic là log không phải queue |
| "thứ tự theo customer / device" | **Cùng key → cùng partition** |
| "muốn nhiều consumer song song hơn" | **Tăng số partition** (consumer ≤ partition) |
| "2 ứng dụng cùng đọc toàn bộ dữ liệu" | **2 consumer group khác `group.id`** |
| "unit of parallelism / scalability" | **Partition** |
| "unit of replication / fault tolerance" | **Replica (leader + follower), RF** |
| "follower tụt 30 s" | **Rời ISR** (`replica.lag.time.max.ms`) |
| "file 00000000000000012345.log" | **Segment**, tên = base offset |
| "tìm offset nhanh trong segment" | **`.index` thưa mỗi 4 KB** + binary search |
| "timestamp lúc broker ghi" | **`LogAppendTime`** |
| "ai quản metadata / bầu leader" | **Active controller trong KRaft quorum** |
| "log metadata nội bộ" | **`__cluster_metadata`** (1 partition) |
| "thêm controller không restart" | **Dynamic quorum KIP-853**, `kafka-metadata-quorum.sh add-controller` |
| "tạo cluster.id" | **`kafka-storage.sh random-uuid` → `format`** |
| "chỉ dev mới dùng" | **`process.roles=broker,controller`** |
| "client dùng địa chỉ nào để kết nối leader" | **`advertised.listeners`** trong metadata |
| "Java tối thiểu broker 4.0" | **17** (client 11) |
| "hàng đợi kiểu SQS trên Kafka, ack từng record" | **Queues for Kafka / share groups (KIP-932, GA 4.2)** |
| "xem LAG của group" | **`kafka-consumer-groups.sh --describe --group`** |
| "đổi retention topic đang chạy" | **`kafka-configs.sh --alter --add-config retention.ms=`** |

## 🧪 Lab checklist

- [ ] Lab 1.1 — Docker chạy, `docker-compose.single.yml` lưu vào `KAFKA/labs/`, `kafka-metadata-quorum.sh describe --status` in `LeaderId: 1`.
- [ ] Lab 1.2 ⭐ — Cluster 3 broker + 1 controller lên, `kafka-broker-api-versions.sh` liệt kê 3 broker, alias trỏ `kafka-1:19092`.
- [ ] Lab 1.3 — Topic `orders` 3 partition RF 3; produce 6 message có key; consume thấy cùng key cùng partition, offset tăng dần.
- [ ] Lab 1.4 ⭐ — `producer.mjs` in `partition/baseOffset`; 2 tiến trình `consumer.mjs` cùng group chia 3 partition; `kcg --describe` thấy LAG = 0.
- [ ] Lab 1.5 — Đọc được 1 record từ `.log` bằng `kafka-dump-log.sh`; thấy record `TOPIC_RECORD` trong `__cluster_metadata`.
- [ ] Lab 1.6 — Kill broker leader → leader đổi, ISR còn 2; bật lại → ISR về 3; producer không lỗi trong lúc đó.
- [ ] Tự viết lại bảng Kafka vs `SQS` vs `Kinesis` vs `RabbitMQ` (4 dòng: thứ tự / replay / nhiều consumer / scale) bằng trí nhớ.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Kafka đảm bảo thứ tự ở mức nào? Muốn mọi event của 1 khách hàng đúng thứ tự thì làm gì?**
  **Đáp án gọn:** chỉ trong 1 partition; dùng `customerId` làm key → murmur2 hash → luôn vào cùng partition (đừng tăng partition sau đó).
- **Chuyện gì xảy ra khi 1 consumer group có 5 consumer đọc topic 3 partition?**
  **Đáp án gọn:** 3 consumer mỗi người 1 partition, 2 consumer idle. Muốn dùng 5 → tăng partition lên ≥ 5.
- **Kể tên 3 file trong thư mục partition và vai trò.**
  **Đáp án gọn:** `.log` (record), `.index` (offset → byte position, thưa 4 KB), `.timeindex` (timestamp → offset); tên = base offset; roll ở 1 GB / 7 ngày.
- **ISR là gì, follower rời ISR khi nào, và record "committed" khi nào?**
  **Đáp án gọn:** tập replica đồng bộ với leader; rời khi tụt quá `replica.lag.time.max.ms` (30 s); committed = mọi replica trong ISR đã ghi (consumer chỉ đọc tới HW).
- **Vì sao bỏ ZooKeeper? KRaft thay bằng gì?**
  **Đáp án gọn:** 2 hệ thống, metadata lệch, failover chậm O(partition); KRaft = controller quorum (3/5 node, Raft) ghi metadata vào `__cluster_metadata`, broker fetch metadata, failover tức thời.
- **Khác nhau `controller.quorum.voters` và `controller.quorum.bootstrap.servers`?**
  **Đáp án gọn:** voters = static quorum, khai `id@host:port`, đổi thành viên phải restart, deprecated; bootstrap.servers = dynamic quorum (KIP-853), chỉ khai địa chỉ, `add-controller`/`remove-controller` online, format bằng `--standalone`/`--initial-controllers`.
- **App trên host không connect được Kafka trong Docker dù `docker exec` chạy ổn — nguyên nhân số 1?**
  **Đáp án gọn:** `advertised.listeners` trả hostname nội bộ container; cần listener thứ 2 advertise `localhost:9092` cho host.
- **Client cần biết bao nhiêu broker trong `bootstrap.servers`? Sau đó kết nối ai?**
  **Đáp án gọn:** ≥ 1 (nên 2–3); nhận metadata (toàn bộ broker + leader) rồi kết nối **trực tiếp leader** của từng partition.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- Apache Kafka Docs: *Introduction — Main Concepts and Terminology* + *Quickstart* (`kafka-storage.sh`, console producer/consumer).
- Apache Kafka Docs: *Design* — Persistence, Efficiency, Replication (ISR, committed, unclean election, `min.insync.replicas`).
- Apache Kafka Docs: *Implementation — Log* (segment, index, retention, recovery).
- Apache Kafka Docs: *Operations — KRaft* (process roles, static/dynamic quorum, `kafka-storage.sh`, `kafka-metadata-quorum.sh`, `kafka-metadata-shell.sh`).
- Apache Kafka Docs: *Configuration — Broker Configs* (`listeners`, `advertised.listeners`, `log.*`, `num.partitions`, `min.insync.replicas`…) và *Security — Listener Configuration*.
- Apache Kafka Blog: *Apache Kafka 4.0.0 Release Announcement* (18/03/2025).
- KIP-500 (Replace ZooKeeper) & KIP-853 (KRaft Controller Membership Changes) trên cwiki.apache.org; Confluent Developer *KRaft* learn page.
- Khoá học: Confluent Developer — *Apache Kafka 101* (Topics, Partitions, Brokers, Replication, Producers, Consumers — miễn phí); Stephane Maarek — *Apache Kafka Series: Learn Apache Kafka for Beginners v3* (phần Theory + CLI); sách *Kafka: The Definitive Guide* 2nd ed. chương 1, 2, 6.

## ✅ Checklist hoàn thành Tuần 1

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (1 GB / 168 h / 4096 B / 30 000 ms / 9092–9093 / 50 partitions / Java 17)
- [ ] Giải thích được KRaft và lý do bỏ ZooKeeper trong 1 phút
- [ ] Hoàn thành 6 lab, giữ lại `docker-compose.single.yml` và `docker-compose.cluster.yml` cho các tuần sau
- [ ] Làm xong 30 câu [questions.md](questions.md) ≥ 70%, ghi sổ câu sai
- [ ] Vượt Cổng tự kiểm tra (8 câu)
