# ✅ Nhật ký Validate kiến thức — Kafka Study Plan (CCDAK)

> **Ngày lập:** 2026-09-15 · **Phiên bản neo:** Apache Kafka **4.3.1** (bản mới nhất tại thời điểm viết; 4.3.0 phát hành 2026-05-22, 4.2.0 phát hành 2026-02-17).
> **Phương pháp:** đối chiếu số liệu mặc định với `kafka.apache.org/documentation` (producer/consumer/broker/topic configs), release announcement 4.0 → 4.3, và docs Confluent/AWS đã crawl trong `week-NN/resources/`.
> Mục tiêu: **tránh học số cũ** (nhiều mặc định đã đổi ở 3.0 và 4.0) và **ghi rõ chỗ nào cần đối chiếu lại trước ngày thi**.

---

## 🔴 Mặc định ĐÃ ĐỔI theo version — đề/khoá cũ hay ghi số cũ

| # | Config | Cũ (đề/khoá cũ) | Hiện hành (4.3) | Đổi từ | Ghi chú |
|---|---|---|---|---|---|
| 1 | Producer `acks` | `1` | **`all`** | 3.0 (KIP-679) | Đi kèm bật idempotence mặc định |
| 2 | Producer `enable.idempotence` | `false` | **`true`** | 3.0 | Yêu cầu `acks=all`, `max.in.flight ≤ 5` |
| 3 | Producer `linger.ms` | `0` | **`5`** | 4.0 (KIP-1030) | Đề CCDAK cũ hỏi "mặc định linger là 0" — hiểu theo cơ chế |
| 4 | Consumer `session.timeout.ms` | `10000` | **`45000`** | 3.0 (KIP-735) | `heartbeat.interval.ms` vẫn 3000 |
| 5 | Consumer `partition.assignment.strategy` | `RangeAssignor` | **`[Range, CooperativeSticky]`** | 3.0 | Classic protocol; KIP-848 dùng `group.remote.assignor` |
| 6 | Consumer protocol | classic (JoinGroup/SyncGroup) | **KIP-848 GA** (`group.protocol=consumer`, opt-in) | 4.0 GA; classic **deprecated 4.3** | Mặc định vẫn `classic` — kiểm tra lại nếu 4.4+ đổi mặc định |
| 7 | Broker metadata | ZooKeeper | **KRaft-only** | 4.0 | `zookeeper.connect` không còn; Java 17 cho broker |
| 8 | Broker `num.recovery.threads.per.data.dir` | `1` | **`2`** | 4.0 (KIP-1030) | — |
| 9 | Queues for Kafka (share groups, KIP-932) | không có | **GA** | 4.2 (EA 4.0, preview 4.1) | `kafka-console-share-consumer.sh`, `group.type=share` |
| 10 | Streams rebalance protocol (KIP-1071) | client-side | **GA broker-side** (`group.protocol=streams`) | 4.2 | Không bắt buộc cho CCDAK |
| 11 | ELR — Eligible Leader Replicas (KIP-966 Part 1) | không có | **Khả dụng, opt-in** ở 4.0 (`eligible.leader.replicas.version=1`); **bật mặc định cho cluster mới từ 4.1** | 4.0 → 4.1 | Giảm mất data khi ISR co về 1 replica; đề/tài liệu 4.0 gọi là *preview* |
| 12 | Logging framework | log4j 1.x / reload4j | **log4j2** | 4.0 | File config `log4j2.yaml` |
| 13 | CLI tools | `--zookeeper` | **`--bootstrap-server`** thống nhất (KIP-1147) | 4.2 | Một số tool cũ chấp nhận `--bootstrap-controller` |

---

## 🟡 Chỗ cần ĐỐI CHIẾU LẠI trước ngày thi (dữ liệu thay đổi nhanh)

**CCDAK**
- Số câu **60** / **90 phút** / **150 USD** / pass-fail không công bố ngưỡng — xác nhận lại trên https://www.confluent.io/certification/ (trang này đôi khi đổi URL con; trang `/certification/developer/` trả 404 tại thời điểm viết).
- Hiệu lực chứng chỉ **2 năm** và policy retake — chưa crawl được chính thức; đối chiếu khi đăng ký.
- Dạng câu **matching / list order** — theo trang Confluent tổng quan; practice test bên thứ ba thường chỉ có multiple choice.
- Tỉ trọng domain (28/23/15/13/12/8) lấy từ tổng hợp cộng đồng 2026, không phải tài liệu Confluent công bố dạng exam guide — dùng để phân bổ thời gian, không dùng để "đoán đề".

**Kafka**
- Kiểm tra bản Kafka mới nhất (`kafka.apache.org/downloads`) — nếu **4.4+** ra mắt, xem release notes phần *"Notable changes"* cho mặc định mới (đặc biệt `group.protocol` mặc định có đổi sang `consumer` chưa).
- Share groups: các config `share.*` còn thay đổi giữa 4.2 → 4.3 (`share.acquisition.lock.duration.ms` 30 s).
- Số liệu `message.max.bytes` **1.048.588** (không phải tròn 1 MiB) — dễ nhầm với `max.request.size` 1.048.576.

**Confluent Platform / Schema Registry / Connect**
- Image Docker trong labs dùng `confluentinc/cp-schema-registry:8.0.x` và `cp-kafka-connect:8.0.x` — kiểm tra tag mới nhất trên Docker Hub trước khi chạy.
- Partition count internal topics Connect (1/25/5) là **mặc định** của `connect-distributed.properties` mẫu, không phải hằng số cứng.

**Amazon MSK**
- Quota MSK Serverless (partition/throughput per cluster), giá Express brokers, và `Lambda` ESM (`BatchSize` max 10.000, batching window 300 s) — đối chiếu docs AWS vì đổi thường xuyên.
- MSK Replicator "identical topic name" và tiered storage cho Express brokers — tính năng 2024–2025, kiểm tra region support.

---

## 🧪 LAB — chưa chạy thật, cần đối chiếu khi thực hành

Các lab local (Docker) đã được kiểm cú pháp và chạy được về mặt logic. Phần chạy trên AWS và vài hành vi client **chưa test trên hạ tầng thật** — kiểm lại khi bạn làm lab:

| Tuần · Lab | Điểm chưa kiểm chứng | Cách xác minh nhanh |
|---|---|---|
| 9.1 | URL/phiên bản jar `aws-msk-iam-auth` (2.3.0) và gói `nodejs22`/`nodejs22-npm` trên Amazon Linux 2023 | Đối chiếu [releases trên GitHub](https://github.com/aws/aws-msk-iam-auth/releases) và `dnf search nodejs` trên EC2 |
| 9.1 | Phí `MSK Serverless` ~0,75 USD/giờ cluster-hour (us-east-1) | Trang pricing MSK — giá đổi theo region và theo thời điểm |
| 9.2 | Runtime Lambda `nodejs22.x` (lab có ghi chú đổi sang `nodejs24.x`) | `aws lambda list-runtimes` hoặc trang runtimes của Lambda |
| 9.2 | Default VPC cần 2 interface endpoint (`lambda`, `sts`) cho ESM — suy luận từ docs | Tạo ESM và xem `LastProcessingResult` nếu poller không kết nối được |
| 9.7 | `EventBridge Pipes` hỗ trợ **MSK Serverless** làm source, và shape body đẩy sang SQS | Trang Pipes source MSK; script decode trong lab đã viết chịu được cả object lẫn array |
| 9.5 | Hành vi `kafkajs` `pause()` + `resume()` trong `eachBatch`: record chưa `resolveOffset` có được fetch lại sau resume không | Chạy Lab 9.5 và quan sát log; nếu khác, chuyển sang `eachMessage` + commit thủ công |
| 8.1 | `jmx_prometheus_javaagent` pin 1.0.1; image `prom/prometheus:v3.5.0`, `grafana/grafana:12.1.0` | Tag đã kiểm trên Maven Central / Docker Hub lúc viết — `docker pull` trước khi chạy |
| 8.3 | Cú pháp `JmxTool --one-time true` và định dạng output CSV | Chạy `kafka-run-class.sh org.apache.kafka.tools.JmxTool --help` trong container |
| 8.5 | Chuỗi retry của `kafkajs` với poison pill (`KafkaJSNumberOfRetriesExceeded`) — log mẫu có thể khác | Chạy Lab 8.5 v1 và so log thực tế |
| 8.2 | `kafkajs` có tự rebalance khi topic tăng partition hay không | Lab đã có phương án dự phòng: Ctrl+C một consumer để ép rebalance |
| 8.6 | `HeartbeatFormatter` / `CheckpointFormatter` của MM2 trên console consumer 4.3 | `--formatter` sẽ báo lỗi ngay nếu class không có trong `libs/` |
| 8.7 | `kafka-features.sh upgrade --release-version 4.3 --dry-run` khi đã ở đúng version; giá trị `kraft.version=0` với static quorum | So với output `kafka-features.sh describe` |
| 5.6 · 9.3 | Image Debezium dùng `quay.io/debezium/connect:3.1` (REST 8084) | `docker pull` và `curl localhost:8084/connector-plugins` |

> 📌 Tên topic outbox trong Lab 9.3 là **`outbox.event.Order`** — giá trị mặc định của `EventRouter` (`route.topic.replacement=outbox.event.${routedByValue}`). Muốn tên `Order-events` thì đổi thành `${routedByValue}-events`.

---

## 🟢 ĐÃ KIỂM — chính xác, ổn định

Các số liệu/khái niệm cốt lõi ít thay đổi và đã đối chiếu docs: consumer `max.poll.records` 500 / `max.poll.interval.ms` 300.000 / `auto.commit.interval.ms` 5.000 / `auto.offset.reset` latest / `fetch.max.bytes` 50 MB / `max.partition.fetch.bytes` 1 MB; producer `batch.size` 16.384 / `buffer.memory` 32 MB / `max.block.ms` 60.000 / `delivery.timeout.ms` 120.000 / `request.timeout.ms` 30.000 / `max.in.flight` 5; broker `log.retention.hours` 168 / `log.segment.bytes` 1 GB / `min.cleanable.dirty.ratio` 0.5 / `log.cleaner.delete.retention.ms` 24 h / `replica.lag.time.max.ms` 30.000 / `unclean.leader.election.enable` false / `min.insync.replicas` 1 / `offsets.retention.minutes` 10.080 / `__consumer_offsets` 50 partition / `transaction.max.timeout.ms` 15 phút; Schema Registry wire format 5 byte + BACKWARD mặc định + 3 subject naming strategies; Streams `commit.interval.ms` 30.000 (100 với EOS) / `statestore.cache.max.bytes` 10 MB / `num.standby.replicas` 0 / task = max partition; ports 9092/9093/8081/8083/8088; MSK ports 9092/9094/9096/9098.

---

> ⚠️ **Lưu ý về độ tươi của dữ liệu:** các file trong `week-NN/resources/` được crawl từ docs Kafka/Confluent/AWS tại thời điểm 2026-09. Trước ngày thi nên đối chiếu nhanh lại **bảng §6 trong `KAFKA-STUDY-PLAN.md`** với link nguồn ghi ở đầu mỗi file resource, đặc biệt các mặc định có gắn nhãn "đổi từ 3.0 / 4.0".
