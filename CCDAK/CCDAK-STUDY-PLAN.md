# 🎯 Kế hoạch học Apache Kafka chuyên sâu — đích thi CCDAK (Confluent Certified Developer for Apache Kafka)

> Tài liệu này là **lộ trình học + checklist toàn diện** cho Apache Kafka, xây theo đúng phương pháp đã dùng cho `DVA-C02`.
> Bạn đã đậu `SAA-C03` và đang học `DVA-C02` → đã quen `SQS`/`SNS`/`Kinesis`, consumer group của `Kinesis`, event source mapping của `Lambda`. Kafka **là bước tiếp theo tự nhiên**: một hệ thống streaming mã nguồn mở, mạnh hơn `Kinesis` về ecosystem (Connect, Streams, Schema Registry) và là nền của `Amazon MSK`.
> Đích đo được: **CCDAK** — chứng chỉ developer của Confluent (đơn vị thương mại hoá Kafka). CCDAK **KHÔNG** hỏi "cài Kafka thế nào" mà hỏi **"config nào / hành vi nào / guarantee nào khi code producer, consumer, Connect, Streams"** — rất giống tư duy DVA.
>
> **📅 Kế hoạch đã chốt:** **10 tuần × ~10–12h/tuần (~110 giờ)**. Mục tiêu: **hiểu sâu Kafka để dùng được ở production** và **đậu CCDAK chắc chắn** — mỗi tuần có *cổng tự kiểm tra*, và một *cơ chế đảm bảo đậu* dựa trên ngưỡng điểm mock (xem [§3](#3-lộ-trình-học-theo-tuần)).
>
> **Phiên bản neo:** Apache Kafka **4.3.x** (KRaft-only; ZooKeeper đã bị gỡ từ 4.0). Ngày lập kế hoạch: 2026-09-15.

---

## 📑 Mục lục

1. [Tổng quan kỳ thi CCDAK](#1-tổng-quan-kỳ-thi)
2. [Kafka nhìn từ người đã học AWS — tận dụng cái đã biết](#2-kafka-nhìn-từ-người-đã-học-aws)
3. [Lộ trình học chi tiết 10 tuần (~10–12h/tuần) + Cơ chế đảm bảo đậu](#3-lộ-trình-học-theo-tuần)
4. [Kiến thức theo Domain CCDAK](#4-kiến-thức-theo-domain)
5. [Deep-dive từng thành phần trọng tâm](#5-deep-dive-từng-thành-phần-trọng-tâm)
6. [Những con số PHẢI thuộc lòng](#6-những-con-số-phải-thuộc-lòng)
7. [Bảng phản xạ: Keyword → Config/Đáp án](#7-bảng-phản-xạ-keyword--configđáp-án)
8. [Thực hành hands-on (labs bắt buộc)](#8-thực-hành-hands-on)
9. [Tài nguyên học tập](#9-tài-nguyên-học-tập)
10. [Chiến lược làm bài thi](#10-chiến-lược-làm-bài-thi)
11. [✅ CHECKLIST TOÀN DIỆN](#11-checklist-toàn-diện)

---

## 1. Tổng quan kỳ thi

| Hạng mục | Chi tiết |
|---|---|
| **Tên** | Confluent Certified Developer for Apache Kafka (**CCDAK**) |
| **Số câu hỏi** | **60 câu** |
| **Thời gian** | **90 phút** (~90 giây/câu — nhanh hơn DVA đáng kể) |
| **Loại câu** | Multiple choice, multiple select, matching, list order *(theo trang Confluent Certification)* |
| **Điểm đậu** | **Pass/Fail — Confluent không công bố ngưỡng**; cộng đồng ước ~65–70%. Đặt ngưỡng cá nhân **≥80%** |
| **Chi phí** | **150 USD** |
| **Hình thức** | Online proctored (webcam, phòng riêng, giấy tờ tuỳ thân) |
| **Hiệu lực** | 2 năm *(đối chiếu trang chính thức trước khi đăng ký)* |
| **Yêu cầu tiên quyết** | Không bắt buộc; khuyến nghị 6–12 tháng kinh nghiệm dev với Kafka |
| **Chứng chỉ anh em** | **CCAAK** (Administrator — vận hành cluster), **CCAC** (Confluent Cloud). Plan này phủ ~70% CCAAK ở Tuần 1–2, 7–8 |

### Tỉ trọng 6 Domain CCDAK (phân bổ thời gian học theo đây)

| Domain | Tên | Tỉ trọng | ~Số câu | Ưu tiên |
|---|---|---|---|---|
| **1** | Apache Kafka Application Development (producer/consumer, serialization, delivery semantics) | **28%** | ~17 | ⭐⭐⭐ Cao nhất |
| **2** | Apache Kafka Fundamentals (broker, partition, offset, replication, retention, ordering) | **23%** | ~14 | ⭐⭐⭐ Cao |
| **3** | Kafka Connect (connector, worker, task, converter, SMT) | **15%** | ~9 | ⭐⭐ Trung-cao |
| **4** | Application Observability (metrics, consumer lag, rebalance diagnostics) | **13%** | ~8 | ⭐⭐ Trung |
| **5** | Apache Kafka Streams (KStream/KTable, windowing, joins, state stores) | **12%** | ~7 | ⭐⭐ Trung |
| **6** | Application Testing (mock vs real broker, TopologyTestDriver) | **8%** | ~5 | ⭐ Thấp |

> 💡 **Domain 1 + 2 = 51%.** Nắm chắc **producer configs, consumer group/offset/rebalance, replication/ISR/acks, retention/compaction** là đã qua ngưỡng đậu. Người học hay **đầu tư quá nhiều vào Streams (12%)** mà hụt phần producer/consumer — plan này dành **Tuần 3–4 (2 tuần)** cho producer/consumer và chỉ **1 tuần** cho Streams.

> ⚠️ **Ngoài phạm vi CCDAK nhưng trong plan:** `Amazon MSK` + design patterns (Tuần 9). Đây là phần "dùng Kafka thật trong công việc trên AWS" — không bỏ, nhưng không tính vào mock CCDAK.

---

## 2. Kafka nhìn từ người đã học AWS

### ✅ Cái bạn ĐÃ CÓ (chỉ cần đối chiếu)

| Khái niệm AWS đã biết | Tương đương Kafka | Khác biệt cần chú ý |
|---|---|---|
| `Kinesis Data Streams` **shard** | **partition** | Kafka không giới hạn 1 MB/s/partition; partition **không giảm** được; số partition quyết định parallel tối đa của consumer group |
| `Kinesis` **partition key** → shard | **record key** → partition (murmur2 hash) | Kafka: key null → **sticky partitioner** (round-robin theo batch) |
| `Kinesis` **sequence number** | **offset** (per partition, tăng đơn điệu) | Consumer tự quản offset; commit vào `__consumer_offsets` |
| `Kinesis` **KCL** + DynamoDB checkpoint | **consumer group** + `__consumer_offsets` | Kafka tự có group coordinator trên broker, không cần DynamoDB |
| `Kinesis` retention 24h→365 ngày | `log.retention.hours` mặc định **7 ngày**, có thể **vô hạn** (`-1`) + **tiered storage** + **log compaction** | Compaction = giữ giá trị cuối theo key — `Kinesis` không có |
| `Kinesis` **enhanced fan-out** | Mỗi consumer group đọc độc lập, mặc định đã "fan-out" | Không cần đăng ký consumer riêng; giới hạn là băng thông broker |
| `SQS` queue (1 message → 1 consumer) | **Queues for Kafka / share group** (GA 4.2) hoặc consumer group | Consumer group truyền thống gán **partition** cho consumer, không gán message |
| `SQS` visibility timeout / DLQ | `max.poll.interval.ms` (liveness) / **DLQ topic tự xây** hoặc Connect `errors.deadletterqueue` | Kafka **không** có DLQ built-in cho consumer thường |
| `SNS` fan-out | Không cần — mỗi service dùng **consumer group riêng** trên cùng topic | |
| `SQS` Extended Client (payload lớn → S3) | **Claim-check pattern** (tự xây) | `message.max.bytes` mặc định ~1 MB |
| `Lambda` event source mapping (`Kinesis`) | `Lambda` ESM cho **MSK / self-managed Kafka** — Lambda **poll** | Tuần 9 |
| `Amazon Data Firehose` (load vào S3/Redshift) | **Kafka Connect sink** (S3 sink, JDBC sink…) | Connect có source connector (CDC) — Firehose không |
| `Kinesis Data Analytics` / Managed Flink | **Kafka Streams** (library), **ksqlDB**, Flink | Streams chạy trong app của bạn, không có cluster riêng |
| `Glue Schema Registry` | **Confluent Schema Registry** (Avro/Protobuf/JSON Schema) | Wire format 5 byte; compatibility modes |
| IAM policy | **ACL** (`kafka-acls.sh`, `StandardAuthorizer`), MSK IAM access control | Deny thắng Allow (giống IAM) |
| `CloudWatch` metrics | **JMX metrics** → Prometheus/Grafana | Phải tự dựng; `UnderReplicatedPartitions`, `records-lag-max` |

### 🔥 Cái MỚI / SÂU HƠN nhiều (đầu tư nhiều nhất)

- **Bộ config producer** (`acks`, `enable.idempotence`, `linger.ms`, `batch.size`, `max.in.flight.requests.per.connection`, `delivery.timeout.ms`, `compression.type`) và **tương tác giữa chúng** — CCDAK hỏi thẳng tên config.
- **Consumer group protocol**: rebalance eager vs cooperative, **KIP-848** (protocol mới, GA 4.0), static membership, `session.timeout.ms` vs `max.poll.interval.ms`, offset commit sync/async, `auto.offset.reset`.
- **Replication & durability**: ISR, `min.insync.replicas`, high watermark, `unclean.leader.election.enable`, ELR (opt-in 4.0, mặc định cho cluster mới từ 4.1).
- **Log storage**: segment, retention, **compaction** (tombstone, dirty ratio), tiered storage.
- **Exactly-once**: idempotent producer, **transactions** (`transactional.id`, zombie fencing), `isolation.level=read_committed`, Streams `exactly_once_v2`.
- **Schema Registry**: Avro/Protobuf/JSON Schema, **compatibility BACKWARD/FORWARD/FULL**, subject naming strategies.
- **Kafka Connect**: worker/connector/task, **converter ≠ SMT**, internal topics, REST API, DLQ (chỉ sink), exactly-once source.
- **Kafka Streams**: KStream/KTable/GlobalKTable, **4 loại window**, **join matrix**, state store + changelog, `TopologyTestDriver`.
- **Security**: TLS/mTLS, SASL (PLAIN/SCRAM/GSSAPI/OAUTHBEARER), ACL, quotas.
- **Observability**: JMX metrics broker/producer/consumer, consumer lag, exception → nguyên nhân → fix.
- **KRaft** (không còn ZooKeeper): controller quorum, `__cluster_metadata`, `kafka-storage.sh format`.

> 🧠 **Câu thần chú chuyển tư duy:** `Kinesis` là "AWS quản mọi thứ, bạn chỉ ghi/đọc" — Kafka là **"bạn quyết định mọi trade-off bằng config"**: durability (`acks`/`min.isr`) ↔ latency (`linger.ms`) ↔ throughput (`batch.size`/compression) ↔ ordering (`max.in.flight`/key) ↔ semantics (idempotence/transactions/commit). Mọi câu hỏi CCDAK đều xoay quanh **một trade-off cụ thể + config điều khiển nó**.

---

## 3. Lộ trình học theo tuần

> **Kế hoạch: 10 tuần × ~10–12h/tuần (~110 giờ).** Học phủ hết kiến thức trong **Tuần 1–8**, **Tuần 9** dành cho Kafka-trên-AWS + patterns + FULL MOCK #1, **Tuần 10** mock dồn + capstone + thi. Thứ tự theo tỉ trọng và phụ thuộc kiến thức: Fundamentals (Tuần 1–2) → Application Development (Tuần 3–4) → Connect + Schema (Tuần 5) → Streams (Tuần 6) → Security + Testing (Tuần 7) → Observability + Ops (Tuần 8) → MSK + Patterns (Tuần 9) → chốt (Tuần 10).

### ⏱️ Nhịp học mỗi tuần (~11h — chia 4 buổi)

| Buổi | Thời lượng | Nội dung |
|---|---|---|
| **A — Lý thuyết** | ~3h | Đọc docs Kafka/Confluent + khoá video chủ đề tuần, ghi note theo bảng "PHẢI NHỚ" |
| **B — Hands-on** | ~3.5h | Tự tay làm lab trên cluster Docker local (CLI + Node.js `kafkajs`; Java cho Streams) |
| **C — Bổ sung** | ~2.5h | Bảng so sánh/quyết định + đọc KIP/FAQ + phần còn lại của lý thuyết |
| **D — Practice + Review** | ~2h | 25–30 câu practice đúng chủ đề → **ghi câu sai** + ôn lại (spaced repetition) |

> 📌 **Tỉ lệ vàng: Lý thuyết 35% – Hands-on 45% – Practice 20%.** Kafka thắng bằng **thí nghiệm trên cluster thật** (tắt broker, xem ISR co lại, đo lag) — không phải học vẹt config.

---

### 🗓️ Chi tiết 10 tuần — mỗi tuần 1 thư mục riêng

> 👉 Mỗi tuần là **1 thư mục** trong [`study-plan/`](study-plan/) gồm: `README.md` (plan chi tiết: mục tiêu, nội dung từng buổi, lab từng bước, điểm phải nhớ, bẫy đề, cổng tự kiểm tra, checklist), `questions.md` + `answers.md` (25–30 câu văn phong CCDAK), `labs.md` (lab cầm tay chỉ việc) và thư mục **`resources/`** (tài liệu Kafka/Confluent/AWS đã crawl sẵn để đọc offline). Bấm vào tên tuần để mở.

| Tuần | Trọng tâm | Domain | Mốc quan trọng | File |
|---|---|---|---|---|
| **1** | Kiến trúc Kafka & **KRaft** + dựng cluster Docker + CLI + producer/consumer đầu tiên | FUND | — | [week-01/](study-plan/week-01/README.md) |
| **2** | Độ tin cậy & lưu trữ: **replication/ISR/acks/min.isr**, retention, **log compaction**, delivery semantics, share groups | FUND | — | [week-02/](study-plan/week-02/README.md) |
| **3** | **Producer chuyên sâu**: idempotence, batching, compression, partitioner, retries, **Transactions/EOS** | DEV | — | [week-03/](study-plan/week-03/README.md) |
| **4** | **Consumer chuyên sâu**: consumer group, rebalance (eager/cooperative/**KIP-848**), offset commit, `auto.offset.reset`, lag | DEV ✅ | 🎯 mini-mock FUND+DEV ≥70% | [week-04/](study-plan/week-04/README.md) |
| **5** | **Schema Registry** (Avro/Protobuf/JSON, compatibility) + **Kafka Connect** (worker/task/converter/SMT/DLQ/CDC) | CONNECT ✅ | — | [week-05/](study-plan/week-05/README.md) |
| **6** | **Kafka Streams**: KStream/KTable, windowing, joins, state store, EOS v2, `TopologyTestDriver`; ksqlDB | STREAMS ✅ | — | [week-06/](study-plan/week-06/README.md) |
| **7** | **Security** (TLS/SASL/ACL/quotas) + **Testing** (Mock*, Testcontainers, contract test) | TEST ✅ | 🎯 mini-mock CONNECT+STREAMS+TEST ≥70% | [week-07/](study-plan/week-07/README.md) |
| **8** | **Observability & Operations**: JMX metrics, consumer lag, exception cheat-sheet, reassignment, MM2, tiered storage | OBS ✅ | 🎯 mini-mock toàn domain ≥72% | [week-08/](study-plan/week-08/README.md) |
| **9** | **Kafka trên AWS** (`Amazon MSK`, MSK Connect, IAM auth, Lambda ESM) + **Design patterns** (outbox, retry/DLQ, idempotent consumer) | AWS + ARCH | 🎯 **FULL MOCK #1** | [week-09/](study-plan/week-09/README.md) |
| **10** | Tuần chốt: Mock dồn + Review + Cram + **Capstone pipeline** + Thi | Tất cả | 🏁 **Full mock #2–4 → Thi** | [week-10/](study-plan/week-10/README.md) |

> 📈 Tiến trình phủ Domain: **FUND** (Tuần 1–2, 23%) → **DEV** (Tuần 3–4, 28%) → **CONNECT** (Tuần 5, 15%) → **STREAMS** (Tuần 6, 12%) → **TEST** (Tuần 7, 8%) → **OBS** (Tuần 8, 13%) → bổ trợ AWS/ARCH (Tuần 9) → **chốt** (Tuần 10).

---

### ✅ Cơ chế ĐẢM BẢO ĐẬU (bắt buộc tuân thủ)

1. **Cổng tự kiểm tra:** Không sang tuần mới nếu **chưa trả lời trôi chảy** các câu hỏi ở cổng tuần hiện tại. Chưa qua → dành buổi D tuần sau ôn lại phần yếu.
2. **Sổ câu sai + Spaced repetition:** Mọi câu practice/mock sai → ghi lại (đề, đáp án đúng, **lý do mình sai**). Ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Viết file phân tích 6 mục trong `CCDAK/questions/` theo đúng format `aws-saa-c03-analysis-format.md` của repo.
3. **Ngưỡng checkpoint:** Mini-mock cuối mỗi cụm domain **phải đạt ngưỡng** (FUND+DEV ≥70%, CONNECT+STREAMS+TEST ≥70%, toàn domain ≥72%) mới đi tiếp. Không đạt → lùi lịch, cày lại cụm đó.
4. **Ngưỡng đăng ký thi thật — CHỈ đặt lịch khi ĐỦ CẢ 4:**
   - ✅ **≥ 3 bộ practice CCDAK KHÁC NHAU đạt ≥ 80%** (ổn định, không phải may mắn) — dùng [3 bộ mock trong repo](mock-exams/README.md) làm nền, cộng thêm ít nhất 1 bộ ngoài.
   - ✅ Đã **review hết 100% câu sai** và hiểu vì sao sai.
   - ✅ Đọc trôi chảy toàn bộ **bảng số §6** và **bảng phản xạ §7**.
   - ✅ Hoàn thành **toàn bộ hands-on nhóm Producer/Consumer & Connect/Streams** ở [§8](#8-thực-hành-hands-on) + **Capstone** Tuần 10.
5. **Van an toàn:** Nếu một full mock **< 70%** → **lùi lịch thi 1 tuần**, tập trung 100% vào vùng yếu (domain điểm thấp nhất) trước khi mock lại.

> 🎯 Vì sao cách này đảm bảo đậu: CCDAK không công bố điểm đậu; ước tính cộng đồng **~65–70%**. Đặt ngưỡng cá nhân **≥80% ổn định trên nhiều bộ đề khác nhau** tạo **biên an toàn ≥10%** — đủ hấp thụ độ khó dao động, câu dạng matching/list-order lạ, và áp lực 90 giây/câu.

---

## 4. Kiến thức theo Domain

> Dưới đây là **các mảng kiến thức theo 6 domain CCDAK**, kèm những gì cần **học / nhớ / phản xạ**. Tên domain theo trang Confluent; chi tiết task do Confluent không công bố dạng task statement như AWS, nên đây là tổng hợp từ syllabus khoá học Confluent Developer + kinh nghiệm đề.

### 🟦 Domain 1 — Application Development (28%)

**Producer**
- Vòng đời `send()`: serializer → partitioner → record accumulator (batch per partition) → sender thread → broker; `Future`/callback; `flush()`/`close()`.
- Durability: `acks=0/1/all` × `min.insync.replicas`; `NotEnoughReplicasException`.
- Reliability: `retries`, `delivery.timeout.ms`, `request.timeout.ms`, `retry.backoff.ms`; lỗi **retriable vs non-retriable**.
- **Idempotent producer** (mặc định từ 3.0): PID + sequence; yêu cầu `acks=all`, `max.in.flight ≤ 5`.
- Throughput/latency: `linger.ms` (mặc định **5 ms** từ 4.0), `batch.size`, `buffer.memory`, `max.block.ms`, `compression.type`.
- Partitioner: key hash (murmur2) / sticky khi key null / custom; thêm partition phá mapping key.
- **Transactions**: `transactional.id`, `initTransactions` → `beginTransaction` → `send` + `sendOffsetsToTransaction` → `commitTransaction`/`abortTransaction`; zombie fencing (epoch); consume-transform-produce EOS.

**Consumer**
- Poll loop; `subscribe()` (group, rebalance) vs `assign()` (standalone).
- Consumer group, group coordinator, assignors (Range/RoundRobin/Sticky/CooperativeSticky), **eager vs cooperative**, **KIP-848** (`group.protocol=consumer`), static membership (`group.instance.id`).
- Liveness: `session.timeout.ms` (45 s) + `heartbeat.interval.ms` (3 s) [heartbeat thread] vs `max.poll.interval.ms` (5 phút) [processing thread].
- Offset: auto commit (at-least-once), `commitSync`/`commitAsync`, commit **offset + 1**, `auto.offset.reset` (earliest/latest/none), `seek*`, `ConsumerRebalanceListener`, `CommitFailedException`.
- `isolation.level=read_committed`; consumer **không thread-safe**; pause/resume; share group consumer (Queues for Kafka).

**Serialization & Schema**
- Built-in serdes; Avro/Protobuf/JSON Schema qua Schema Registry; wire format 5 byte; compatibility BACKWARD/FORWARD/FULL (+TRANSITIVE); subject naming strategies; `auto.register.schemas`.

**Delivery semantics**
- At-most-once / at-least-once / exactly-once — vị trí commit offset so với xử lý; idempotent consumer; EOS Kafka→Kafka bằng transactions.

### 🟩 Domain 2 — Fundamentals (23%)

- Broker, cluster, topic, partition, offset, segment (`.log/.index/.timeindex`), record (key/value/headers/timestamp).
- **KRaft**: controller quorum (3/5), `process.roles`, `__cluster_metadata`, `kafka-storage.sh format`, dynamic quorum (KIP-853).
- **Replication**: leader/follower, **ISR**, `replica.lag.time.max.ms`, **high watermark** (consumer chỉ đọc tới HW), leader election, `unclean.leader.election.enable`, ELR, preferred leader, rack awareness.
- **Retention**: theo thời gian/kích cỡ, áp lên segment đã đóng; **compaction** (tombstone, `delete.retention.ms`, `min.cleanable.dirty.ratio`), `compact,delete`; tiered storage.
- Ordering: chỉ trong 1 partition; key → partition; `max.in.flight` với retry.
- Message size: `message.max.bytes` (broker/topic) vs `max.request.size` (producer) vs `max.partition.fetch.bytes` (consumer).
- Kafka vs `SQS`/`Kinesis`/RabbitMQ; Queues for Kafka (share groups, GA 4.2).

### 🟨 Domain 3 — Kafka Connect (15%)

- Worker (standalone vs distributed), connector, task (`tasks.max`), source vs sink.
- **Converter** (`key/value.converter`, ranh giới Connect↔Kafka) **≠ SMT** (`transforms`, chỉnh từng record) **≠ serializer**.
- Internal topics `connect-configs/offsets/status` (1/25/5 partition, compacted); REST API (8083): create/update/status/restart/pause/resume.
- Error handling: `errors.tolerance=all`, `errors.log.enable`, **DLQ chỉ cho sink** (`errors.deadletterqueue.topic.name`).
- Offsets: source tự quản trong `connect-offsets`; sink dùng consumer group `connect-<name>`; exactly-once source (3.3+).
- Connector phổ biến: JDBC, S3, Elasticsearch, **Debezium CDC**; MirrorMaker 2 chạy trên Connect.

### 🟥 Domain 4 — Application Observability (13%)

- JMX metrics: broker (`UnderReplicatedPartitions`, `OfflinePartitionsCount`, `ActiveControllerCount`, `RequestHandlerAvgIdlePercent`, `TotalTimeMs`), producer (`record-error-rate`, `batch-size-avg`, `record-queue-time-avg`, `buffer-available-bytes`), consumer (`records-lag-max`, `fetch-latency-avg`, `commit-latency-avg`, `rebalance-latency-avg`, `time-between-poll-max`).
- **Consumer lag** = LEO − committed offset; `kafka-consumer-groups.sh --describe`; nguyên nhân & xử lý.
- Rebalance diagnostics; exception cheat-sheet (`TimeoutException`, `CommitFailedException`, `OffsetOutOfRange`, `RecordTooLarge`, `ProducerFenced`, `SerializationException` poison pill).
- Prometheus JMX exporter + Grafana; logs (`log4j2`, `state-change.log`, `kafka-authorizer.log`).

### 🟪 Domain 5 — Kafka Streams (12%)

- Library (không cluster); topology, task = số partition, `num.stream.threads`, scale bằng instance cùng `application.id`.
- **KStream / KTable / GlobalKTable**, stream-table duality; stateless vs stateful; `groupByKey` vs `groupBy` (repartition).
- State store (RocksDB) + changelog topic + standby replicas; cache (`statestore.cache.max.bytes`), `commit.interval.ms`.
- **Windows**: tumbling / hopping / sliding / session; grace period; `suppress`.
- **Joins**: KStream-KStream (windowed, co-partition), KStream-KTable, KTable-KTable (+FK), KStream-GlobalKTable (không co-partition).
- `processing.guarantee=exactly_once_v2`; exception handlers; `TopologyTestDriver`; Processor API + punctuate; Interactive Queries; ksqlDB.

### 🟫 Domain 6 — Application Testing (8%)

- `MockProducer` / `MockConsumer` (unit), `TopologyTestDriver` (Streams, không cần broker), `MockSchemaRegistryClient` (`mock://`).
- Integration: Testcontainers `KafkaContainer` / EmbeddedKafka; bảng mock vs embedded vs container vs real.
- Contract test schema compatibility trong CI; test idempotency, rebalance, retry.

### ➕ Bổ trợ (ngoài CCDAK) — Kafka trên AWS & Patterns (Tuần 9)

- `Amazon MSK` Provisioned (Standard/**Express brokers**) vs **Serverless**; MSK Connect; MSK Replicator; **IAM access control** (SASL/OAUTHBEARER, `aws-msk-iam-auth`), SCRAM + `Secrets Manager`, mTLS + `ACM PCA`; ports 9092/9094/9096/9098.
- `Lambda` event source mapping cho MSK/self-managed Kafka (poll, `StartingPosition`, batch, filter); `EventBridge Pipes`; `Glue Schema Registry`; MSK vs `Kinesis`.
- Patterns: outbox + CDC, event sourcing/CQRS, saga, idempotent consumer, retry/DLQ topics, claim-check, key & partition sizing, EOS end-to-end.

---

## 5. Deep-dive từng thành phần trọng tâm

> Sắp xếp theo mức độ xuất hiện trong đề. Với mỗi thành phần: **cần nhớ gì** + **bẫy đề hay gặp**.

### ⭐ Producer (thành phần #1 của đề)
- **`acks`**: `0` (fire-and-forget, có thể mất), `1` (leader ghi xong — mất nếu leader chết trước replicate), `all/-1` (đủ `min.insync.replicas` xác nhận). Mặc định **`all`** từ 3.0.
- **`min.insync.replicas`** chỉ có ý nghĩa khi `acks=all`. RF=3 + min.isr=2 + acks=all = **chịu mất 1 broker, không mất data**. ISR < min.isr → producer nhận `NotEnoughReplicasException` (retriable), consumer vẫn đọc được.
- **Idempotence** (`enable.idempotence=true` mặc định): loại duplicate do retry **trong 1 session producer, 1 partition**; **không** thay thế transactions (đa partition/đa session).
- **Ordering khi retry**: không idempotence + `max.in.flight > 1` + retry → có thể đảo thứ tự. Với idempotence, `max.in.flight ≤ 5` vẫn giữ thứ tự.
- **`delivery.timeout.ms`** (120 s) là **trần tổng** cho send (gồm linger + retry); phải ≥ `linger.ms + request.timeout.ms`. `retries` gần vô hạn — thực tế bị chặn bởi delivery timeout.
- **Batching**: `linger.ms` chờ gom batch (mặc định **5 ms** từ 4.0, đề cũ ghi 0); `batch.size` trần byte per partition batch; batch gửi khi **đầy HOẶC hết linger**. Nén theo batch → batch to → tỉ lệ nén tốt.
- **`buffer.memory`** đầy → `send()` block tới `max.block.ms` → `TimeoutException` (BufferExhausted).
- **Partitioner**: key → murmur2 % partitions; key null → sticky (gom batch 1 partition rồi đổi). **Thêm partition** → key cũ có thể sang partition khác → **phá ordering theo key**.
- **Transactions**: `transactional.id` cố định per instance để **fence zombie** (epoch tăng; `ProducerFencedException`); `transaction.timeout.ms` ≤ broker `transaction.max.timeout.ms` (15 phút); consumer phía sau cần `read_committed`; `sendOffsetsToTransaction` để offset commit **trong** transaction.
- **Bẫy:** "guarantee no duplicates across restarts" → idempotence **không đủ**, cần **transactions** hoặc idempotent consumer. "`acks=all` nhưng vẫn mất data" → `min.insync.replicas=1` (mặc định!). "Latency cao nhưng throughput thấp" → `linger.ms` quá lớn / `batch.size` quá nhỏ.

### ⭐ Consumer & Consumer Group (thành phần #2)
- **1 partition ↔ tối đa 1 consumer trong group**; consumer > partition → idle. Nhiều group đọc độc lập cùng topic.
- **Rebalance** kích hoạt khi: consumer join/leave/crash, partition thêm, subscription đổi. **Eager** (revoke all → stop-the-world) vs **Cooperative** (`CooperativeStickyAssignor`, chỉ revoke phần cần chuyển). **KIP-848** (`group.protocol=consumer`): broker tính assignment, incremental, không còn JoinGroup/SyncGroup; classic protocol **deprecated ở 4.3**.
- **Assignors**: `Range` (mặc định đầu, gán theo thứ tự partition từng topic — mất cân bằng khi nhiều topic), `RoundRobin`, `Sticky`, `CooperativeSticky`. Mặc định classic: `[Range, CooperativeSticky]` (để upgrade an toàn).
- **Liveness 2 tầng**: heartbeat thread (`session.timeout.ms` 45 s, `heartbeat.interval.ms` 3 s) vs poll (`max.poll.interval.ms` 5 phút). **Xử lý lâu** → vượt max.poll.interval → consumer bị coi chết → rebalance + `CommitFailedException`, dù heartbeat vẫn ok. Fix: giảm `max.poll.records`, tăng interval, xử lý async + pause/resume.
- **Static membership** (`group.instance.id`): restart trong `session.timeout.ms` **không** gây rebalance.
- **Offset commit**: auto commit (mỗi 5 s **tại lần poll kế**) → at-least-once (duplicate khi crash); commit **trước** xử lý → at-most-once; commit sau xử lý thủ công → at-least-once; offset commit = **offset xử lý cuối + 1**. `commitSync` (block, retry) vs `commitAsync` (không retry — tránh commit cũ ghi đè mới; dùng callback). Commit trong `onPartitionsRevoked`.
- **`auto.offset.reset`** chỉ áp dụng khi **không có committed offset** hoặc offset **out of range**: `latest` (mặc định — consumer mới bỏ qua data cũ), `earliest`, `none` (throw). Committed offset hết hạn sau **7 ngày** không hoạt động (`offsets.retention.minutes`).
- **`assign()`** không có group coordination → tự quản offset; **`seek()`** để replay/skip.
- **Lag** = log end offset − committed offset; theo partition; tool `kafka-consumer-groups.sh`; reset offsets khi group **inactive**.
- **Bẫy:** "add consumers to speed up but no improvement" → consumer đã ≥ partition → **tăng partition**. "consumer mới không thấy message cũ" → `auto.offset.reset=latest`. "duplicate sau crash" → at-least-once bình thường → idempotent consumer. "rebalance mỗi lần deploy" → static membership / cooperative / KIP-848.

### ⭐ Replication, ISR & Storage (Fundamentals)
- **ISR** = replicas bắt kịp leader trong `replica.lag.time.max.ms` (30 s). Follower tụt → rời ISR → **ISR shrink**; bắt kịp → **expand**. Leader luôn trong ISR.
- **High watermark** = offset nhỏ nhất đã replicate tới **toàn bộ ISR**; consumer chỉ đọc **tới HW** → data chưa đủ ISR không thấy được (không mất consistency).
- **Leader election**: thứ tự **ISR → ELR → last known leader** (ELR opt-in ở 4.0, mặc định cho cluster mới từ 4.1). `unclean.leader.election.enable=true` → chọn replica ngoài ISR → **mất data nhưng available**. Mặc định `false`.
- **Retention** xoá **segment đã đóng** (không xoá segment active) → "đặt `retention.ms=60000` mà data còn" vì segment chưa roll (`segment.bytes` 1 GB / `segment.ms` 7 ngày).
- **Compaction** (`cleanup.policy=compact`): giữ **giá trị cuối theo key**, xoá bằng **tombstone** (value null) giữ `delete.retention.ms` (24 h) để consumer kịp thấy; chạy khi dirty ratio ≥ `min.cleanable.dirty.ratio` (0.5); **không** compact segment active; dùng cho `__consumer_offsets`, changelog Streams, KTable, CDC snapshot.
- **`compact,delete`**: vừa compact vừa xoá theo retention.
- **Message size chain**: producer `max.request.size` ≤ topic `max.message.bytes` (≈ broker `message.max.bytes` 1 MB) ≤ `replica.fetch.max.bytes`; consumer `max.partition.fetch.bytes` ≥ message size (từ 2.x consumer vẫn đọc được message lớn hơn — first batch luôn trả).
- **Bẫy:** "RF=3 min.isr=3" → mất 1 broker là **không ghi được** (trade availability). "Consumer thấy message rồi biến mất" → unclean election / đọc quá HW là không thể — thường là compaction/retention. "Số partition giảm" → **không thể**, chỉ tạo topic mới.

### `KRaft` & Cluster
- `process.roles=broker|controller|broker,controller`; controller quorum **3 hoặc 5** (Raft, chịu mất (n-1)/2); metadata trong topic nội bộ `__cluster_metadata`; `kafka-storage.sh random-uuid` + `format` trước khi start; `controller.quorum.voters` (static) hoặc `controller.quorum.bootstrap.servers` (dynamic quorum, `kafka-metadata-quorum.sh add-controller`).
- Không còn `zookeeper.connect`; **Kafka 4.0** yêu cầu Java 17 (broker/Connect), Java 11 (clients/Streams); bỏ client protocol cũ (baseline 2.1) — client < 2.1 không kết nối được.
- `bootstrap.servers` chỉ để lấy metadata; client sau đó kết nối **trực tiếp leader** từng partition qua `advertised.listeners` → bẫy Docker "kết nối được nhưng produce timeout" = advertised listener sai.

### Schema Registry
- Wire format **[0x00][schema id 4 byte][payload]**; consumer thường thấy 5 byte đầu lạ.
- **BACKWARD** (mặc định): schema mới đọc data cũ → **xoá field, thêm field có default**; **upgrade consumer trước**. **FORWARD**: data mới đọc bằng schema cũ → **thêm field, xoá field có default**; **upgrade producer trước**. **FULL** = cả hai → chỉ thêm/xoá **field có default**. `*_TRANSITIVE` so với **mọi** version trước, không chỉ version cuối. `NONE` = không kiểm.
- Subject: `TopicNameStrategy` (`<topic>-value`, 1 schema/topic), `RecordNameStrategy` (theo tên record — nhiều event type 1 topic), `TopicRecordNameStrategy`.
- `auto.register.schemas=false` + `use.latest.version=true` ở production; schema lưu trong topic `_schemas` (compacted, 1 partition).
- **Bẫy:** "thêm field bắt buộc (không default) ở BACKWARD" → **incompatible (409)**. "Avro dùng field type `string` đổi sang `int`" → không tương thích ở mọi mode.

### Kafka Connect
- **Converter ≠ SMT ≠ Serializer**: converter đổi Connect internal record ↔ byte trên Kafka (`JsonConverter` + `schemas.enable`, `AvroConverter`, `StringConverter`); SMT sửa record (`InsertField`, `MaskField`, `RegexRouter`, `ExtractField`, `Cast`, `Filter` + predicate) theo chuỗi thứ tự; connector **không** dùng serializer của producer.
- Distributed worker: `group.id`, REST 8083, 3 internal topic **phải RF cao & compacted**; task phân bổ giữa worker; rebalance connector (incremental từ 2.3).
- **DLQ chỉ có ở sink** (`errors.deadletterqueue.topic.name`, `errors.tolerance=all`, `...context.headers.enable=true` gắn nguyên nhân vào header). Source lỗi convert → chỉ log/skip.
- Source offset lưu `connect-offsets` (theo source partition tuỳ connector: file, table, binlog position) → xoá connector **không** xoá offset (dùng REST `DELETE /connectors/<n>/offsets` từ 3.6). Sink = consumer group `connect-<name>` → reset bằng `kafka-consumer-groups.sh`.
- `tasks.max` là **trần**, connector tự quyết số task thực (`FileStreamSource` luôn 1).
- Exactly-once source: worker `exactly.once.source.support=enabled` + connector `exactly.once.support=required` (3.3+).
- **Bẫy:** "sink JSON không có schema nhưng converter `schemas.enable=true`" → lỗi `JsonConverter with schemas.enable requires "schema" and "payload" fields`. "muốn đổi tên topic đích" → SMT `RegexRouter`, không phải converter.

### Kafka Streams
- **Task** = đơn vị parallel = **số partition lớn nhất của input topics** trong sub-topology; thread chạy nhiều task; instance thêm quá số task → idle. Scale = thêm instance cùng `application.id` (chính là consumer `group.id`).
- **KStream** (mỗi record là event độc lập, insert) vs **KTable** (upsert theo key, null = delete) vs **GlobalKTable** (bản sao đầy đủ mỗi instance, không cần co-partition, cho lookup nhỏ).
- **Repartition** xảy ra khi đổi key (`selectKey`/`map`/`groupBy`) rồi làm stateful; `groupByKey` không repartition. Topic `<app>-<name>-repartition`.
- **State store** RocksDB (persistent) / in-memory; **changelog topic** compacted để restore; `num.standby.replicas` giảm thời gian failover; `state.dir`.
- **Windows**: tumbling (không chồng), hopping (chồng, `advanceBy`), sliding (theo khoảng cách record, join), session (gap không hoạt động). **Grace period** cho late record; `suppress(untilWindowCloses)` để emit 1 kết quả cuối; cache + `commit.interval.ms` làm output không emit từng record.
- **Join matrix**: KStream-KStream **cần window + co-partition**; KStream-KTable không window, co-partition; KTable-KTable không window (+ FK join); KStream-GlobalKTable **không cần co-partition**, chọn key tuỳ ý.
- **Co-partitioning** = cùng số partition + cùng partitioner/key → nếu không, Streams tự repartition (KStream) hoặc báo lỗi `TopologyException` (KTable).
- `processing.guarantee=exactly_once_v2` (dùng 1 transactional producer/thread, broker ≥ 2.5); `commit.interval.ms` 30 s → 100 ms khi EOS.
- Exception handlers: deserialization (`LogAndContinue`/`LogAndFail`), production, processing (3.9+); DLQ trong handler (4.2). `StreamsUncaughtExceptionHandler` → REPLACE_THREAD / SHUTDOWN_CLIENT / SHUTDOWN_APPLICATION.
- `TopologyTestDriver` test topology không cần broker; `TestInputTopic.pipeInput`, `advanceWallClockTime` cho punctuator.
- **Bẫy:** "join 2 KStream khác số partition" → repartition hoặc lỗi. "count không ra kết quả ngay" → cache/commit interval, không phải bug. "GlobalKTable cho bảng lớn" → tốn RAM/disk mỗi instance → dùng KTable.

### Security
- 3 lớp: **encryption** (TLS), **authentication** (SSL cert / SASL), **authorization** (ACL). `security.protocol` = PLAINTEXT / SSL / SASL_PLAINTEXT / SASL_SSL.
- SASL: **PLAIN** (user/pass tĩnh trong JAAS, cần TLS), **SCRAM-SHA-256/512** (credential trong metadata, đổi runtime bằng `kafka-configs.sh`), **GSSAPI** (Kerberos), **OAUTHBEARER** (JWT/OIDC — MSK IAM dùng cơ chế này). `sasl.mechanism` client phải nằm trong `sasl.enabled.mechanisms` của listener.
- **mTLS**: `ssl.client.auth=required`, principal = DN của cert.
- **ACL** (`StandardAuthorizer` KRaft): principal + operation + resource (Topic/Group/Cluster/TransactionalId) + pattern (LITERAL/PREFIXED) + host + Allow/Deny; **Deny thắng**; không ACL → từ chối (trừ `allow.everyone.if.no.acl.found=true` hoặc `super.users`). `--producer` = Write+Describe+Create; `--consumer --group` = Read+Describe topic + Read group; idempotent producer cần `IdempotentWrite` (Cluster) hoặc Write topic (2.8+); transactional cần Write on TransactionalId.
- **Quotas**: `producer_byte_rate`, `consumer_byte_rate`, `request_percentage` theo user/client-id → broker **trì hoãn response** (throttle), client thấy `produce-throttle-time-avg`.
- Kafka **không** mã hoá at rest built-in → mã hoá disk / end-to-end payload.

### Observability & Operations
- **Broker**: `UnderReplicatedPartitions` > 0 (follower chậm/broker down), `OfflinePartitionsCount` > 0 (mất availability — không có leader), `ActiveControllerCount` ≠ 1 (bất thường), `IsrShrinksPerSec` cao (flapping), `RequestHandlerAvgIdlePercent` < 0.3 (thiếu I/O thread), `TotalTimeMs` Produce cao phần `RemoteTimeMs` = chờ replica (`acks=all`).
- **Producer**: `record-error-rate`, `record-retry-rate`, `batch-size-avg` (nhỏ so với `batch.size` → tăng `linger.ms`), `record-queue-time-avg`, `buffer-available-bytes` → 0 (block), `produce-throttle-time-avg` > 0 (quota).
- **Consumer**: `records-lag-max`, `records-lead-min` (gần 0 → sắp mất data vì retention), `fetch-latency-avg`, `commit-latency-avg`, `rebalance-latency-avg`, `failed-rebalance-total`, `time-between-poll-max` (gần `max.poll.interval.ms` → nguy cơ bị kick), `last-rebalance-seconds-ago`.
- **Lag tăng**: consumer chậm / ít consumer hơn partition / rebalance liên tục / hot partition → thêm consumer (≤ partition), tăng partition, tối ưu xử lý, sửa key skew.
- Ops: `kafka-reassign-partitions.sh` (`--generate/--execute --throttle/--verify`) khi thêm/bớt broker (broker mới **không** tự nhận partition); `kafka-leader-election.sh --election-type preferred`; Cruise Control tự cân bằng; rolling restart chờ URP = 0; `kafka-features.sh upgrade --metadata`; **MirrorMaker 2** (3 connector trên Connect: Source/Checkpoint/Heartbeat; topic đổi tên `A.topic` với `DefaultReplicationPolicy`, giữ tên với `IdentityReplicationPolicy`; offset translation).
- **Tiered storage** (`remote.storage.enable=true`, `local.retention.ms`): segment cũ đẩy lên object storage, retention dài rẻ, không hỗ trợ compacted topic.

### `Amazon MSK` (góc AWS — Tuần 9)
- **Provisioned** (Standard brokers + EBS, hoặc **Express brokers**: storage AWS quản, throughput 3×, scale 20× nhanh) vs **Serverless** (không quản broker, trả theo dùng, **chỉ IAM auth**).
- Auth: **IAM access control** (`sasl.mechanism=AWS_MSK_IAM`, port **9098**), SASL/SCRAM + `Secrets Manager` (`AmazonMSK_*`, port **9096**), mTLS + `ACM Private CA` (port **9094**), plaintext 9092.
- **MSK Connect** (managed Connect; plugin zip trên S3; capacity autoscaling/provisioned); **MSK Replicator** (managed cross-region replication); tiered storage; Open Monitoring (Prometheus JMX 11001 / Node 11002); CloudWatch metrics levels.
- **`Lambda` ESM** cho MSK / self-managed Kafka: Lambda **poll** theo consumer group, `StartingPosition` TRIM_HORIZON/LATEST/AT_TIMESTAMP, batch size mặc định 100 (max 10.000), batching window ≤ 300 s, event filtering, payload base64; `EventBridge Pipes`; `Glue Schema Registry`.
- **MSK vs `Kinesis`**: Kinesis đơn giản/fully managed/shard 1 MB/s/retention ≤ 365 ngày; MSK = Kafka API + ecosystem (Connect/Streams/SR), retention vô hạn (tiered), throughput cao, cần tuning topic/partition.

---

## 6. Những con số PHẢI thuộc lòng

> Đề rất hay dựa vào các mặc định này. **Chú ý version:** nhiều mặc định đã đổi ở **3.0** (`acks=all`, idempotence, `session.timeout=45 s`) và **4.0** (`linger.ms=5`). Đề/khoá cũ có thể ghi số cũ — ghi nhớ cả hai.

### Producer
- `acks`: mặc định **`all`** (3.0+; cũ: `1`).
- `enable.idempotence`: **true** (3.0+); yêu cầu `acks=all`, `retries > 0`, `max.in.flight.requests.per.connection ≤ 5`.
- `retries`: **Integer.MAX_VALUE**; `delivery.timeout.ms`: **120.000** (2 phút); `request.timeout.ms`: **30.000**; `retry.backoff.ms`: 100.
- `linger.ms`: **5** (4.0+; cũ: 0); `batch.size`: **16.384** (16 KB); `buffer.memory`: **32 MB**; `max.block.ms`: **60.000**.
- `max.in.flight.requests.per.connection`: **5**; `max.request.size`: **1 MB**; `compression.type`: **none** (gzip/snappy/lz4/zstd).
- Transactions: `transaction.timeout.ms` **60.000**; broker `transaction.max.timeout.ms` **15 phút**; `transactional.id.expiration.ms` **7 ngày**; `__transaction_state` **50 partition**.

### Consumer
- `max.poll.records`: **500**; `max.poll.interval.ms`: **300.000** (5 phút).
- `session.timeout.ms`: **45.000** (3.0+; cũ: 10.000); `heartbeat.interval.ms`: **3.000** (≤ 1/3 session).
- `fetch.min.bytes`: **1**; `fetch.max.wait.ms`: **500**; `fetch.max.bytes`: **50 MB**; `max.partition.fetch.bytes`: **1 MB**.
- `enable.auto.commit`: **true**; `auto.commit.interval.ms`: **5.000**; `auto.offset.reset`: **latest**.
- `partition.assignment.strategy`: **[Range, CooperativeSticky]**; `group.protocol`: **classic** (đặt `consumer` để dùng KIP-848).
- `isolation.level`: **read_uncommitted**.
- `__consumer_offsets`: **50 partition**, compacted; `offsets.retention.minutes`: **10.080** (7 ngày); `group.initial.rebalance.delay.ms`: **3.000**.

### Broker / Topic / Log
- `num.partitions`: **1**; `default.replication.factor`: **1**; `min.insync.replicas`: **1** (production: RF 3 / min.isr 2 / acks all).
- `message.max.bytes`: **1.048.588** (~1 MB); `replica.fetch.max.bytes`: 1 MB.
- `log.retention.hours`: **168** (7 ngày); `log.retention.bytes`: **-1**; `log.segment.bytes`: **1 GB**; `log.roll.hours`: **168**; `log.retention.check.interval.ms`: 300.000.
- `log.cleanup.policy`: **delete**; `min.cleanable.dirty.ratio`: **0.5**; `log.cleaner.delete.retention.ms`: **24 h** (tombstone); `log.cleaner.min.compaction.lag.ms`: 0.
- `replica.lag.time.max.ms`: **30.000**; `unclean.leader.election.enable`: **false**.
- `num.network.threads`: 3; `num.io.threads`: 8; `num.recovery.threads.per.data.dir`: 2 (4.0+).
- Port: broker **9092**, controller **9093**, Schema Registry **8081**, Connect **8083**, ksqlDB **8088**.
- KRaft quorum: **3 hoặc 5** controller; Kafka 4.0: **Java 17** (broker/Connect), **Java 11** (clients/Streams); baseline client protocol **2.1**.

### Schema Registry / Connect
- Wire format: **5 byte** overhead (1 magic + 4 schema id).
- Compatibility mặc định: **BACKWARD**.
- Connect internal topics: `connect-configs` **1**, `connect-offsets` **25**, `connect-status` **5** partition — đều compacted.
- DLQ: **chỉ sink connector**.

### Kafka Streams
- `processing.guarantee`: **at_least_once** (→ `exactly_once_v2`); `commit.interval.ms`: **30.000** (→ **100** khi EOS).
- `statestore.cache.max.bytes`: **10 MB**; `num.stream.threads`: **1**; `num.standby.replicas`: **0**.
- Số task = **max partition** của input topics trong sub-topology.
- Window types: **4** (tumbling / hopping / sliding / session).

### Share groups (Queues for Kafka) / MSK
- KIP-932: early access 4.0 → preview 4.1 → **GA 4.2**. Acquisition lock mặc định **30 s** — group config **`share.record.lock.duration.ms`** (broker default `group.share.record.lock.duration.ms`, chặn trong khoảng 15–60 s). ⚠️ Khái niệm gọi là *acquisition lock* nhưng tên config **không** chứa chữ `acquisition`.
- MSK ports: **9092** plaintext / **9094** TLS / **9096** SCRAM / **9098** IAM; Lambda ESM batch mặc định **100** (max 10.000), batching window ≤ **300 s**.

---

## 7. Bảng phản xạ: Keyword → Config/Đáp án

> Luyện đọc đề → **bật ngay** đáp án. CCDAK chỉ cho ~90 giây/câu — phản xạ quyết định.

| Từ khoá trong đề | Phản xạ tới |
|---|---|
| "no data loss", "durability", "survive 1 broker failure" | **`acks=all` + `min.insync.replicas=2` + RF=3** |
| "lowest latency, can tolerate loss" | **`acks=0`** (hoặc `acks=1`) |
| "duplicates due to retries", "exactly-once per partition" | **`enable.idempotence=true`** |
| "atomic write to multiple partitions/topics", "consume-transform-produce exactly-once" | **Transactions** (`transactional.id`, `sendOffsetsToTransaction`) + consumer **`read_committed`** |
| "zombie producer", "fencing", `ProducerFencedException` | **`transactional.id` cố định + epoch** |
| "increase throughput / better compression" | **↑ `linger.ms`, ↑ `batch.size`, `compression.type=lz4/zstd`** |
| "reduce end-to-end latency for producer" | **↓ `linger.ms`** |
| `TimeoutException` khi `send()` / "buffer full" | **`buffer.memory` / `max.block.ms`** hoặc `delivery.timeout.ms` |
| "ordering with retries enabled" | **idempotence + `max.in.flight ≤ 5`** (hoặc `max.in.flight=1` nếu không idempotent) |
| "same key to same partition", "ordering per customer" | **record key** (murmur2) — không thêm partition sau |
| "messages with null key" | **sticky partitioner** |
| `RecordTooLargeException` | **`max.request.size` (producer) / `message.max.bytes` (broker/topic) / `max.partition.fetch.bytes` (consumer)** |
| "consumer processing takes long, group rebalances" | **`max.poll.interval.ms`** (↑) hoặc ↓ **`max.poll.records`** |
| "consumer crashes detected slowly" | **`session.timeout.ms` / `heartbeat.interval.ms`** |
| "avoid rebalance on rolling restart" | **static membership `group.instance.id`** |
| "minimize stop-the-world during rebalance" | **`CooperativeStickyAssignor`** hoặc **KIP-848 `group.protocol=consumer`** |
| "new consumer group reads from beginning" | **`auto.offset.reset=earliest`** |
| "committed offset deleted / OffsetOutOfRange" | **`offsets.retention.minutes` (7 ngày)** / retention xoá → `auto.offset.reset` |
| "at-most-once" | **commit trước xử lý** |
| "at-least-once" | **commit sau xử lý** (auto commit cũng vậy) + idempotent consumer |
| `CommitFailedException` | **rebalance xảy ra vì vượt `max.poll.interval.ms`** |
| "adding consumers doesn't help" | **consumer ≥ partition → tăng partition** |
| "replay / reprocess from timestamp" | **`seek()` / `offsetsForTimes` / `kafka-consumer-groups --reset-offsets --to-datetime`** |
| "read from specific partition, no group" | **`assign()`** |
| "queue semantics, more consumers than partitions, per-message ack" | **Share group (Queues for Kafka, KIP-932)** |
| "follower out of sync" | **`replica.lag.time.max.ms` → ISR shrink** |
| "consumer can't see latest messages yet" | **high watermark** (chưa replicate đủ ISR) |
| "availability over consistency, accept data loss" | **`unclean.leader.election.enable=true`** |
| "keep only latest value per key", "changelog", "KV store" | **`cleanup.policy=compact`** |
| "delete a key in compacted topic" | **tombstone** (value null) + `delete.retention.ms` |
| "retention set but old data still present" | **segment active chưa roll** (`segment.bytes`/`segment.ms`) |
| "long retention cheaply" | **tiered storage** |
| "no ZooKeeper", "metadata quorum" | **KRaft** (`process.roles`, `__cluster_metadata`) |
| "client connects to bootstrap but times out on produce" | **`advertised.listeners`** sai |
| "consumer sees 5 garbage bytes before JSON" | **Schema Registry wire format** (magic + schema id) |
| "add optional field, upgrade consumers first" | **BACKWARD** |
| "upgrade producers first" | **FORWARD** |
| "both directions compatible" | **FULL** (chỉ field có default) |
| "multiple event types in one topic" | **`RecordNameStrategy`** / `TopicRecordNameStrategy` |
| "change data format between Connect and Kafka" | **Converter** (`key/value.converter`) |
| "modify/rename field, route to another topic in Connect" | **SMT** (`transforms`, `RegexRouter`, `ReplaceField`) |
| "skip bad records in sink, keep originals" | **`errors.tolerance=all` + `errors.deadletterqueue.topic.name`** (sink only) |
| "Connect config storage / scale workers" | **distributed mode + `connect-configs/offsets/status`** |
| "database changes to Kafka without app change" | **CDC (Debezium source connector)** |
| "Kafka → S3/JDBC/Elasticsearch without code" | **Connect sink connector** |
| "replicate cluster to another DC" | **MirrorMaker 2** (`A.topic`) / **MSK Replicator** |
| "stream processing library, no cluster" | **Kafka Streams** |
| "table of latest value per key" | **KTable**; "small reference data on every instance" → **GlobalKTable** |
| "join two streams within 5 minutes" | **KStream-KStream windowed join** (co-partitioned) |
| "enrich stream with lookup table, different key" | **KStream-GlobalKTable join** |
| "count per 1 minute non-overlapping" | **tumbling window** |
| "overlapping windows every 10 s of 1 min" | **hopping window** |
| "user session, inactivity gap" | **session window** |
| "emit only final window result" | **`suppress(untilWindowCloses)`** + grace |
| "Streams parallelism limit" | **số partition input** (tasks) |
| "Streams recovers state quickly after failure" | **`num.standby.replicas`** |
| "exactly-once in Streams" | **`processing.guarantee=exactly_once_v2`** |
| "test topology without broker" | **`TopologyTestDriver`** |
| "unit test producer callback without broker" | **`MockProducer`** |
| "integration test with real broker in CI" | **Testcontainers `KafkaContainer`** |
| "encrypt in transit" | **SSL / SASL_SSL** |
| "username/password stored on broker, change at runtime" | **SASL/SCRAM** |
| "Kerberos" | **SASL/GSSAPI**; "JWT/OIDC/IAM" → **SASL/OAUTHBEARER** |
| "authenticate with certificates" | **mTLS `ssl.client.auth=required`** |
| "allow app to produce only to topics starting with `orders-`" | **ACL PREFIXED pattern** |
| "limit client bandwidth" | **quotas `producer_byte_rate`/`consumer_byte_rate`** |
| `UnderReplicatedPartitions > 0` | follower tụt / broker down |
| `OfflinePartitionsCount > 0` | partition không leader → mất availability |
| `ActiveControllerCount ≠ 1` | controller bất thường |
| `records-lag-max` tăng | consumer chậm / thiếu consumer / hot partition |
| `records-lead-min` → 0 | sắp mất data vì retention |
| "new broker has no partitions" | **`kafka-reassign-partitions.sh`** |
| "Kafka on AWS, no broker management, IAM only" | **MSK Serverless** |
| "Kafka on AWS, 3× throughput, no storage management" | **MSK Express brokers** |
| "Lambda consume from Kafka" | **event source mapping** (poll, `StartingPosition`) |
| "dual-write DB + Kafka inconsistency" | **Outbox pattern + CDC** |
| "payload too large for Kafka" | **claim-check (S3 + pointer)** |
| "retry without blocking partition" | **retry topics + DLQ topic** |

---

## 8. Thực hành hands-on

> **Bắt buộc tự tay làm** — CCDAK đầy câu về "hành vi thực tế khi config X". Toàn bộ chạy **local bằng Docker** (miễn phí), trừ phần MSK (tuỳ chọn, có phí).

### Nhóm Cluster & Fundamentals
- [ ] Dựng cluster **KRaft 1 node** và **3 broker + 1 controller** bằng Docker Compose (`apache/kafka:4.3.1`).
- [ ] Tạo topic, produce có key, consume in partition/offset bằng **CLI**; soi segment bằng `kafka-dump-log.sh`.
- [ ] Tắt 1 broker → quan sát **leader đổi, ISR co lại**, bật lại → ISR hồi.
- [ ] Thí nghiệm **`acks` × `min.insync.replicas`**: tắt 2 broker → `NotEnoughReplicas`.
- [ ] Topic **compacted**: cùng key nhiều giá trị + tombstone → chỉ còn giá trị cuối.
- [ ] Retention ngắn + `segment.ms` nhỏ → thấy earliest offset dời.
- [ ] Gửi record > 1 MB → `RecordTooLarge` → sửa 3 tầng config.

### Nhóm Producer / Consumer (ưu tiên cao nhất)
- [ ] Producer Node.js: callback, `acks` 0/1/all, đo latency.
- [ ] `kafka-producer-perf-test.sh` so `linger.ms`/`batch.size`/`compression.type` → bảng throughput.
- [ ] Phân bố partition: key vs null key; **thêm partition** → key đổi partition.
- [ ] **Idempotent producer** + pause/unpause broker → không duplicate.
- [ ] **Transactions** EOS: abort → `read_committed` không thấy, `read_uncommitted` thấy.
- [ ] Consumer group scale 1→2→3→7 (idle) trên topic 6 partition.
- [ ] Rebalance **eager vs cooperative** vs **KIP-848** (`group.protocol=consumer`) qua log.
- [ ] Manual commit: crash giữa xử lý → duplicate; commit trước → mất message.
- [ ] Vượt **`max.poll.interval.ms`** → rebalance + `CommitFailedException`.
- [ ] `kafka-consumer-groups.sh --reset-offsets` (earliest / shift / datetime) + `seek()`.

### Nhóm Schema Registry & Connect
- [ ] Đăng ký Avro schema, produce/consume Avro, soi 5 byte wire format.
- [ ] Schema evolution: thêm field không default ở BACKWARD → **409**; đổi mode FORWARD/FULL.
- [ ] Connect distributed: 3 internal topic, REST API, `FileStreamSource` → `FileStreamSink` + **SMT**.
- [ ] Sink **DLQ** với `errors.tolerance=all`.
- [ ] (Tuỳ chọn) **Debezium Postgres CDC** → event `op=c/u/d`.

### Nhóm Kafka Streams (Java)
- [ ] WordCount: 2 instance chia task; soi `-repartition`/`-changelog`.
- [ ] Windowed aggregation tumbling + `suppress`.
- [ ] Join KStream-KTable + KStream-GlobalKTable.
- [ ] `exactly_once_v2` vs at_least_once: kill -9 → đếm duplicate.
- [ ] Unit test bằng **`TopologyTestDriver`**.

### Nhóm Security & Testing
- [ ] TLS listener + truststore client; **SASL/SCRAM** user; sai password → `SaslAuthenticationException`.
- [ ] **ACL**: `TopicAuthorizationException` → `--producer` / `--consumer --group` / PREFIXED.
- [ ] Quota `producer_byte_rate` → throughput bị kìm.
- [ ] `MockProducer`/`MockConsumer` unit test; Testcontainers integration test.

### Nhóm Observability & Ops
- [ ] JMX → **Prometheus JMX exporter → Grafana** dashboard.
- [ ] Tạo **lag** → chẩn đoán → thêm consumer → lag giảm.
- [ ] `UnderReplicatedPartitions` khi tắt broker.
- [ ] **Partition reassignment** (`--generate/--execute --throttle/--verify`) + preferred leader election.
- [ ] Poison pill → DLQ topic tự xây.
- [ ] **MirrorMaker 2** giữa 2 cluster local.

### Nhóm AWS & Patterns (Tuần 9) + Capstone (Tuần 10)
- [ ] (Tuỳ chọn, có phí) MSK Serverless + IAM auth + `Lambda` ESM; **xoá ngay sau lab**.
- [ ] Outbox + Debezium EventRouter; idempotent consumer; retry topics + DLQ.
- [ ] **Capstone "Order Pipeline"**: Avro producer → consumer group + dedup + DLQ → Streams join/window EOS → Connect sink → Grafana; kill broker/instance chứng minh không mất data; replay không trùng.

---

## 9. Tài nguyên học tập

### Chính thức
- **Apache Kafka Documentation** — https://kafka.apache.org/documentation/ (đặc biệt §Design, §Configuration producer/consumer/broker/topic, §Connect, §Monitoring, §Security, §Operations).
- **Kafka Streams docs** — https://kafka.apache.org/documentation/streams/ (Core concepts, DSL developer guide, Testing).
- **KIPs quan trọng** (đọc phần Motivation + Public Interfaces): KIP-98 (transactions), KIP-429 (cooperative rebalance), KIP-345 (static membership), KIP-848 (new consumer protocol), KIP-932 (Queues), KIP-966 (ELR), KIP-853 (dynamic quorum), KIP-405 (tiered storage), KIP-298 (Connect error handling), KIP-618 (EOS source), KIP-1030 (4.0 defaults).
- **Confluent Documentation** — https://docs.confluent.io/platform/current/ (Schema Registry, Connect, Security, Monitoring).
- **Confluent Developer (miễn phí)** — https://developer.confluent.io/courses/ : *Apache Kafka 101*, *Kafka Internals*, *Kafka Connect 101*, *Kafka Streams 101*, *Schema Registry 101*, *Security*, *Monitoring*.
- **CCDAK trang chính thức** — https://www.confluent.io/certification/ (format, đăng ký, policy).
- **Amazon MSK Developer Guide** — https://docs.aws.amazon.com/msk/latest/developerguide/ ; **Lambda with MSK** — https://docs.aws.amazon.com/lambda/latest/dg/with-msk.html.

### Sách
- **Kafka: The Definitive Guide, 2nd ed.** (Shapira, Palino, Sivaram, Petty — O'Reilly 2021; Confluent phát hành miễn phí PDF) — sách nền tảng, map chương → tuần trong `week-10/resources/`.
- *Kafka Streams in Action, 2nd ed.* (Bill Bejeck) — cho Tuần 6.
- *Designing Event-Driven Systems* (Ben Stopford, Confluent miễn phí) — cho Tuần 9 patterns.

### Khoá học video (chọn 1–2)
- **Stephane Maarek** — *Apache Kafka Series* (Udemy): Kafka for Beginners → Connect → Streams → Schema Registry → **CCDAK practice exams**.
- **Confluent Developer** courses (video ngắn, miễn phí).
- **Conduktor Kafkademy** (miễn phí, text) — https://learn.conduktor.io/kafka/.

### Practice exams (luyện phản xạ 90 giây/câu)

**Trong repo này — dùng trước tiên:**
- 🎯 **[3 bộ mock full-length 60 câu / 90 phút](mock-exams/README.md)** — tự viết, neo Kafka 4.3, có đủ 4 dạng câu của đề thật gồm **matching** và **list order**. Mock 01 *nền tảng & bẫy version* · Mock 02 *chẩn đoán sự cố* · Mock 03 *thiết kế & đánh đổi*.
- **291 câu theo chủ đề** trong `study-plan/week-NN/questions.md` — luyện từng mảng trước khi vào mock.

**Bên ngoài:**
- **Confluent sample questions** (trên trang certification) — nguồn duy nhất phản ánh đúng văn phong đề thật.
- **Stephane Maarek — CCDAK Practice Exams** (Udemy, 3 bộ).
- **Whizlabs / OpenExamPrep CCDAK** (bổ sung, chất lượng dao động — đối chiếu docs khi nghi ngờ).

> ⚠️ **Cảnh báo về đề công khai.** Kho câu hỏi CCDAK lớn nhất trên GitHub có 356 câu và **không câu nào** chạm tới cooperative rebalancing, KIP-848, share groups, tiered storage hay ELR; một số tài liệu ôn còn dạy znode và cổng ZooKeeper như kiến thức thi. Số liệu đo được và danh sách nguồn: [`mock-exams/SOURCES-AND-VALIDATION.md`](mock-exams/SOURCES-AND-VALIDATION.md).

> 💡 **Tận dụng repo này:** mỗi câu practice sai → viết 1 file phân tích trong `CCDAK/questions/` theo format 6 mục (xem `aws-saa-c03-analysis-format.md`), đặt tên `CCDAK-NNNN.md`.

---

## 10. Chiến lược làm bài thi

- **Ngân sách thời gian:** **~90 giây/câu** (60 câu/90 phút) — nhanh hơn AWS. Câu khó → đánh dấu & bỏ qua, quay lại sau. Đừng để 1 câu ăn hết 3 phút.
- **Đọc câu hỏi TRƯỚC, đáp án SAU:** xác định **trade-off đang hỏi** (durability / latency / throughput / ordering / semantics) rồi mới nhìn config.
- **Nhận diện version:** đề ghi số mặc định cũ (`acks=1`, `linger.ms=0`, `session.timeout=10 s`) → hiểu đề theo ngữ cảnh, chọn đáp án **đúng về cơ chế**, không sa vào tranh cãi số.
- **Loại trừ:** thường 2 đáp án nhắc config **không liên quan** (ví dụ hỏi ordering mà đáp án nói `fetch.min.bytes`) → gạch ngay.
- **Chú ý qualifier:** *"guarantee"*, *"exactly-once"*, *"without changing producer code"*, *"minimize latency"*, *"strict ordering"*, *"across restarts"* → quyết định đáp án (idempotence vs transactions; consumer group vs assign).
- **Dạng matching / list order:** kéo thả config ↔ hành vi, hoặc sắp thứ tự (ví dụ luồng `send()`, thứ tự rebalance, thứ tự upgrade producer/consumer theo compatibility). Luyện bằng cách **tự vẽ lại luồng** trong lab.
- **Multiple select:** đọc kỹ "select TWO/THREE/all that apply" — chọn đủ, không thừa.
- **Bẫy phổ biến:** đáp án đúng về kỹ thuật nhưng **sai thành phần** (đặt config consumer cho producer; dùng SMT thay converter; dùng KTable thay GlobalKTable khi không co-partition).
- **Đừng đổi đáp án** trừ khi phát hiện đọc sót qualifier.
- **Phòng thi online:** kiểm tra webcam/mic/mạng, dọn bàn, giấy tờ tuỳ thân trùng tên đăng ký; đọc policy proctoring của Confluent trước 1 tuần.

---

## 11. CHECKLIST TOÀN DIỆN

> Tick từng mục khi **hiểu + tự tay làm được**. Nhóm theo Domain để dễ theo dõi.

### 📋 A. Chuẩn bị & Nền tảng
- [ ] Đọc trang CCDAK chính thức: format, giá, policy, cách đăng ký.
- [ ] Nắm bảng tỉ trọng Domain (28/23/15/13/12/8) để phân bổ thời gian.
- [ ] Chọn 1 khoá video + 1 bộ practice test.
- [ ] Cài Docker, Node.js 24, Java 17+ (cho Streams), `kafkajs`.
- [ ] Dựng được cluster KRaft 1 node & 3 node bằng Compose; dùng trôi CLI (`kafka-topics`, `kafka-console-*`, `kafka-consumer-groups`, `kafka-configs`).
- [ ] Hiểu `bootstrap.servers` vs `advertised.listeners`.

### 🟩 B. Fundamentals (23%)
- [ ] Giải thích được broker / topic / partition / offset / segment / record.
- [ ] Vẽ được KRaft: controller quorum, `__cluster_metadata`, `process.roles`.
- [ ] Replication: leader/follower, **ISR**, `replica.lag.time.max.ms`, **high watermark**, leader election, `unclean.leader.election.enable`, ELR.
- [ ] Ma trận `acks` × `min.insync.replicas` × RF → khi nào mất data / không ghi được.
- [ ] Retention (time/size, theo segment đã đóng), `segment.bytes/ms`.
- [ ] **Compaction**: tombstone, `delete.retention.ms`, dirty ratio, use case.
- [ ] Ordering chỉ trong partition; key → partition; tăng partition phá mapping.
- [ ] Chuỗi message size 3 tầng.
- [ ] Delivery semantics 3 loại ở góc producer và consumer.
- [ ] Consumer group vs share group (Queues for Kafka).
- [ ] So sánh Kafka vs `SQS`/`Kinesis`/RabbitMQ.

### 🟦 C. Application Development (28%)
- [ ] Vẽ luồng `send()`: serializer → partitioner → accumulator → sender.
- [ ] Thuộc & giải thích: `acks`, `retries`, `delivery.timeout.ms`, `request.timeout.ms`, `enable.idempotence`, `max.in.flight`, `linger.ms`, `batch.size`, `buffer.memory`, `max.block.ms`, `compression.type`, `max.request.size`.
- [ ] Retriable vs non-retriable exceptions.
- [ ] Idempotent producer: cơ chế, giới hạn, ràng buộc config.
- [ ] Transactions: API 6 bước, zombie fencing, `read_committed`, consume-transform-produce.
- [ ] Partitioner mặc định & custom; sticky.
- [ ] Poll loop; `subscribe` vs `assign`; consumer không thread-safe.
- [ ] Group coordinator, assignors, eager vs cooperative, **KIP-848**, static membership.
- [ ] `session.timeout.ms` / `heartbeat.interval.ms` vs `max.poll.interval.ms`.
- [ ] Offset commit: auto / sync / async / specific (+1) / rebalance listener; `CommitFailedException`.
- [ ] `auto.offset.reset` 3 giá trị và khi nào áp dụng; `offsets.retention.minutes`.
- [ ] `seek*`, `offsetsForTimes`, reset offsets CLI.
- [ ] Serialization: built-in, Avro/Protobuf/JSON Schema, wire format.
- [ ] Compatibility modes + thứ tự upgrade; subject naming strategies.
- [ ] Idempotent consumer & at-least-once thực tế.

### 🟨 D. Kafka Connect (15%)
- [ ] Worker / connector / task; standalone vs distributed; `tasks.max`.
- [ ] Converter ≠ SMT ≠ serializer; `JsonConverter schemas.enable`.
- [ ] 3 internal topics + partition count; REST API endpoints.
- [ ] Error handling: `errors.tolerance`, `errors.log.*`, DLQ (sink only), headers.
- [ ] Source offset vs sink consumer group; reset offsets.
- [ ] Exactly-once source (3.3+).
- [ ] CDC / Debezium; MirrorMaker 2 chạy trên Connect.

### 🟪 E. Kafka Streams (12%)
- [ ] Topology, task = partition, thread, scale bằng instance.
- [ ] KStream / KTable / GlobalKTable; stream-table duality.
- [ ] Stateless vs stateful; `groupByKey` vs `groupBy` (repartition).
- [ ] State store, changelog, standby, cache + commit interval.
- [ ] 4 window types + grace + suppress.
- [ ] Join matrix (window? co-partition?).
- [ ] `exactly_once_v2`; exception handlers; uncaught handler 3 lựa chọn.
- [ ] Processor API + punctuate; Interactive Queries.
- [ ] `TopologyTestDriver`.

### 🟫 F. Testing (8%)
- [ ] `MockProducer` / `MockConsumer` use cases.
- [ ] `MockSchemaRegistryClient` (`mock://`).
- [ ] Testcontainers vs EmbeddedKafka vs mock — khi nào dùng.
- [ ] Contract test compatibility trong CI.

### 🟥 G. Observability (13%)
- [ ] Bật JMX, Prometheus exporter, Grafana.
- [ ] Thuộc bảng metric broker / producer / consumer + ngưỡng.
- [ ] Consumer lag: định nghĩa, đo, nguyên nhân, xử lý.
- [ ] Rebalance diagnostics.
- [ ] Exception cheat-sheet → nguyên nhân → fix.

### 🔐 H. Security & Ops
- [ ] `security.protocol` 4 giá trị; TLS keystore/truststore; mTLS.
- [ ] SASL 4 mechanism + khi nào dùng; JAAS.
- [ ] ACL model, `--producer/--consumer` shortcut, PREFIXED, Deny thắng, super.users.
- [ ] Quotas 3 loại.
- [ ] Partition reassignment, preferred leader election, Cruise Control, rolling restart, feature upgrade.
- [ ] Tiered storage; MirrorMaker 2 (3 connector, replication policy).
- [ ] Capacity planning: partition count, RF, disk, threads.

### ☁️ I. Kafka trên AWS & Patterns (bổ trợ)
- [ ] MSK Provisioned (Standard/Express) vs Serverless; ports & auth 3 loại.
- [ ] MSK Connect, MSK Replicator, tiered storage, Open Monitoring.
- [ ] `Lambda` ESM cho Kafka; `EventBridge Pipes`; `Glue Schema Registry`.
- [ ] MSK vs `Kinesis` quyết định.
- [ ] Outbox + CDC, event sourcing/CQRS, saga, idempotent consumer, retry/DLQ topics, claim-check, partition sizing.

### 🏁 J. Đủ điều kiện thi
- [ ] Hoàn thành **toàn bộ lab** [§8](#8-thực-hành-hands-on) + Capstone Tuần 10.
- [ ] Qua **mọi cổng tự kiểm tra** Tuần 1–9.
- [ ] Mini-mock: FUND+DEV ≥70%, CONNECT+STREAMS+TEST ≥70%, toàn domain ≥72%.
- [ ] **≥ 3 bộ practice CCDAK khác nhau ≥ 80%** — [Mock 01](mock-exams/mock-01/questions.md) · [Mock 02](mock-exams/mock-02/questions.md) · [Mock 03](mock-exams/mock-03/questions.md).
- [ ] Review 100% câu sai; viết file phân tích `CCDAK/questions/CCDAK-NNNN.md`.
- [ ] Đọc trôi **§6** và **§7** không cần tra.
- [ ] Đặt lịch thi, kiểm tra thiết bị/phòng, giấy tờ.
