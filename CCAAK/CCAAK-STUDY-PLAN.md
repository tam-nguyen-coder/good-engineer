# 🛠️ Kế hoạch học Kafka Administration — đích thi CCAAK (Confluent Certified Administrator for Apache Kafka)

> Tài liệu này là **lộ trình học + checklist toàn diện** cho vai trò **vận hành cluster Kafka**, xây theo đúng phương pháp đã dùng cho [`CCDAK/`](../CCDAK/CCDAK-STUDY-PLAN.md).
> Bạn vừa hoàn thành bộ **CCDAK (Developer)** → phần lớn nền tảng Kafka (topic, partition, offset, ISR, producer/consumer config, Connect, Streams) đã có sẵn.
> CCAAK **KHÔNG** hỏi "viết code producer thế nào" mà hỏi **"cluster đang hỏng ở đâu, sửa config nào, dựng kiến trúc ra sao để không mất dữ liệu"**.
> Tư duy chuyển đổi: từ **Developer (viết ứng dụng)** → **Administrator (giữ cluster sống, nhanh và an toàn)**.
>
> **📅 Kế hoạch: 8 tuần × ~11h/tuần (~88 giờ).** Ngắn hơn CCDAK 2 tuần vì bạn đã có nền — xem [§2](#2-ccaak-nhìn-từ-người-đã-học-ccdak) để biết cái gì được tái sử dụng.
>
> **Phiên bản neo:** Apache Kafka **4.3.x** (KRaft-only; ZooKeeper đã bị gỡ từ 4.0). Ngày lập: 2026-09-20.

---

## 📑 Mục lục

1. [Tổng quan kỳ thi CCAAK](#1-tổng-quan-kỳ-thi)
2. [CCAAK nhìn từ người đã học CCDAK](#2-ccaak-nhìn-từ-người-đã-học-ccdak)
3. [Lộ trình 8 tuần + Cơ chế đảm bảo đậu](#3-lộ-trình-học-theo-tuần)
4. [Kiến thức theo 7 Domain](#4-kiến-thức-theo-domain)
5. [Deep-dive từng mảng vận hành](#5-deep-dive-từng-mảng-vận-hành)
6. [Những con số PHẢI thuộc lòng](#6-những-con-số-phải-thuộc-lòng)
7. [Bảng phản xạ: Triệu chứng → Nguyên nhân → Hành động](#7-bảng-phản-xạ-triệu-chứng--hành-động)
8. [Thực hành hands-on](#8-thực-hành-hands-on)
9. [Tài nguyên học tập](#9-tài-nguyên-học-tập)
10. [Chiến lược làm bài thi](#10-chiến-lược-làm-bài-thi)
11. [✅ CHECKLIST TOÀN DIỆN](#11-checklist-toàn-diện)

---

## 1. Tổng quan kỳ thi

| Hạng mục | Chi tiết |
|---|---|
| **Tên** | Confluent Certified Administrator for Apache Kafka (**CCAAK**) |
| **Số câu hỏi** | **60 câu** |
| **Thời gian** | **90 phút** (~90 giây/câu) |
| **Loại câu** | Multiple choice, multiple select, matching, list order |
| **Điểm đậu** | **Pass/Fail** — Confluent không công bố ngưỡng. Đặt ngưỡng cá nhân **≥80%** |
| **Chi phí** | **150 USD** |
| **Hình thức** | Online proctored qua **Honorlock** (Chrome, webcam, micro, giấy tờ tuỳ thân) |
| **Hiệu lực** | 2 năm · thi lại phải chờ **7 ngày** |
| **Đối tượng** | "Professionals who manage and maintain Kafka cluster environments" |
| **Xác nhận kỹ năng** | "Configure, deploy, monitor, and support Apache Kafka clusters" |

### Tỉ trọng 7 Domain

| # | Domain | Tỉ trọng | ~Câu/60 | Tuần phụ trách |
|---|---|---|---|---|
| 1 | **Apache Kafka Cluster Configuration** | **22%** | 13 | Tuần 2–3 |
| 2 | **Apache Kafka Fundamentals** | **15%** | 9 | Tuần 1 |
| 3 | **Apache Kafka Security** | **15%** | 9 | Tuần 5 |
| 4 | **Troubleshooting** | **15%** | 9 | Tuần 7 |
| 5 | **Deployment Architecture** | **12%** | 7 | Tuần 4 |
| 6 | **Kafka Connect** | **12%** | 7 | Tuần 6 |
| 7 | **Observability** | **10%** | 6 | Tuần 7 |

> 📌 Tổng cộng là **101%** do Confluent làm tròn từng domain. Dùng bảng này để **phân bổ thời gian**, không dùng để đoán chính xác số câu.

> 🔄 **Mẹo nhận diện tài liệu cũ.** Syllabus CCAAK đã được cấu trúc lại. Bản cũ chia đề thành **4 domain** (Fundamentals 15% · Managing/Configuring/Optimizing **30%** · Security 15% · Designing/Troubleshooting/Integrating **40%**). Gặp tài liệu ôn nào chia theo 4 domain đó thì biết ngay nó thuộc thế hệ trước và nhiều khả năng còn dạy ZooKeeper.

> 💡 **Cluster Configuration + Troubleshooting + Observability = 47%.** Gần một nửa đề xoay quanh *"cluster đang có triệu chứng X, config nào sai, sửa thế nào"*. Đây là lý do plan này dành **2 tuần** cho Cluster Configuration và ghép Observability với Troubleshooting thành một tuần chẩn đoán.

### Văn phong đề — khác CCDAK rõ rệt

> *"The exam rarely asks you to define a term in isolation. Instead, it presents a scenario and asks which action a competent administrator would take."*

Nghĩa là: ít câu "config X là gì", nhiều câu "**cluster đang thế này, bạn làm gì tiếp theo**". Luyện bằng lab và bằng bảng phản xạ [§7](#7-bảng-phản-xạ-triệu-chứng--hành-động), không luyện bằng học vẹt định nghĩa.

---

## 2. CCAAK nhìn từ người đã học CCDAK

### ✅ Cái bạn ĐÃ CÓ — tái sử dụng trực tiếp

Bộ [`CCDAK/`](../CCDAK/CCDAK-STUDY-PLAN.md) đã phủ những phần sau. Ôn lại, **không học lại từ đầu**:

| Kiến thức | Đã có ở | Dùng cho domain CCAAK |
|---|---|---|
| Broker, topic, partition, offset, segment | CCDAK Tuần 1 | Fundamentals (15%) |
| ISR, high watermark, `acks` × `min.insync.replicas`, ELR | CCDAK Tuần 2 | Fundamentals + Cluster Config |
| Retention, log compaction, tombstone | CCDAK Tuần 2 | Cluster Configuration |
| KRaft: `process.roles`, controller quorum, `__cluster_metadata` | CCDAK Tuần 1 | Deployment Architecture |
| Consumer group, rebalance, lag | CCDAK Tuần 4 | Troubleshooting |
| Kafka Connect: worker, task, converter, SMT, DLQ | CCDAK Tuần 5 | Kafka Connect (12%) |
| TLS, SASL, ACL, quotas | CCDAK Tuần 7 | Security (15%) |
| JMX metrics, reassignment, MirrorMaker 2, tiered storage | CCDAK Tuần 8 | Observability + Architecture |
| Cluster Docker 3 broker + Prometheus/Grafana | CCDAK Tuần 1 & 8 labs | Toàn bộ lab tuần này |

> 🔁 **Nguyên tắc tái sử dụng:** mỗi tuần của plan này mở đầu bằng mục *"Ôn nhanh từ CCDAK"* liệt kê chính xác file cần đọc lại, rồi mới vào phần mới. Lab cũng dùng lại `~/kafka-labs/` và hai file compose chuẩn đã dựng.

### 🔥 Cái MỚI / SÂU HƠN nhiều — đầu tư chính

| Mảng | Vì sao mới với bạn |
|---|---|
| **Broker config toàn diện** | CCDAK chỉ chạm vài config broker. CCAAK hỏi cả `num.io.threads`, `num.network.threads`, `num.replica.fetchers`, `queued.max.requests`, `background.threads`, socket buffers, `log.dirs` nhiều ổ đĩa |
| **JVM & OS tuning** | Heap size, G1GC, page cache, file descriptor, `vm.swappiness`, filesystem — CCDAK không đụng |
| **Capacity planning & sizing** | Bao nhiêu broker, bao nhiêu partition, bao nhiêu disk cho throughput và retention cho trước |
| **Deployment topology** | Stretch cluster vs multi-cluster, rack awareness, controller tách riêng, sizing controller quorum |
| **Disaster recovery** | RPO/RTO, MirrorMaker 2 active-active vs active-passive, **Cluster Linking** (Confluent), backup/restore metadata |
| **Rolling upgrade & maintenance** | `kafka-features.sh`, metadata version, thứ tự nâng cấp, `controlled.shutdown`, drain broker |
| **Vận hành ACL và quota ở quy mô** | Không chỉ tạo ACL mà quản trị hàng trăm principal, prefix pattern, audit |
| **Chẩn đoán có phương pháp** | Từ triệu chứng → metric → log → config, thành *playbook* chứ không phải mẹo lẻ |
| **Cluster Linking & Confluent Platform** | Thành phần chỉ có ở Confluent Platform, xuất hiện trong đề CCAAK |

> 🧠 **Câu thần chú chuyển tư duy:** CCDAK hỏi *"ứng dụng của tôi nên gọi API nào"*. CCAAK hỏi **"cluster của tôi đang chịu tải gì, chịu được mất mát gì, và tôi phải chỉnh con số nào"**. Mọi câu hỏi đều quy về một trong bốn trục: **durability · availability · throughput · chi phí vận hành**.

---

## 3. Lộ trình học theo tuần

> **8 tuần × ~11h/tuần (~88 giờ).** Học phủ hết trong **Tuần 1–7**, **Tuần 8** dành cho mock dồn + capstone + thi.

### ⏱️ Nhịp học mỗi tuần (~11h — chia 4 buổi)

| Buổi | Thời lượng | Nội dung |
|---|---|---|
| **A — Lý thuyết** | ~3h | Đọc docs Kafka/Confluent chủ đề tuần; mở đầu bằng *Ôn nhanh từ CCDAK* |
| **B — Hands-on** | ~3.5h | Lab trên cluster Docker: đổi config, gây sự cố, quan sát, sửa |
| **C — Bổ sung** | ~2.5h | Bảng quyết định + playbook chẩn đoán + đọc KIP/FAQ |
| **D — Practice + Review** | ~2h | 25–30 câu practice + **ghi sổ câu sai** |

> 📌 **Tỉ lệ vàng cho CCAAK: Lý thuyết 30% – Hands-on 50% – Practice 20%.** Hands-on chiếm tỉ trọng cao hơn CCDAK vì đề hỏi *hành động của người vận hành*, thứ chỉ hình thành khi bạn đã tự tay làm hỏng và sửa một cluster.

### 🗓️ Chi tiết 8 tuần

| Tuần | Trọng tâm | Domain chính | Mốc | File |
|---|---|---|---|---|
| **1** | Nền tảng vận hành + **KRaft in production** (quorum, metadata, formatting, controller tách riêng) | FUND 15% | — | [week-01/](study-plan/week-01/README.md) |
| **2** | **Cluster Config I**: broker config toàn diện, `log.dirs` & storage, retention, compaction, topic override | CFG 22% | — | [week-02/](study-plan/week-02/README.md) |
| **3** | **Cluster Config II**: replication & durability, quotas, throughput tuning, JVM/OS tuning | CFG 22% ✅ | 🎯 mini-mock CFG ≥70% | [week-03/](study-plan/week-03/README.md) |
| **4** | **Deployment Architecture**: sizing & capacity planning, rack awareness, multi-DC, DR, MM2, Cluster Linking | ARCH 12% ✅ | — | [week-04/](study-plan/week-04/README.md) |
| **5** | **Security administration**: TLS/mTLS, SASL, ACL ở quy mô, quotas, audit, rotation | SEC 15% ✅ | 🎯 mini-mock SEC ≥70% | [week-05/](study-plan/week-05/README.md) |
| **6** | **Kafka Connect operations**: distributed worker, scaling, task failure, REST ops, DLQ, upgrade plugin | CONNECT 12% ✅ | — | [week-06/](study-plan/week-06/README.md) |
| **7** | **Observability + Troubleshooting**: JMX/Prometheus, alerting, và **playbook chẩn đoán** theo triệu chứng | OBS 10% + TROUBLE 15% ✅ | 🎯 **FULL MOCK #1** | [week-07/](study-plan/week-07/README.md) |
| **8** | Tuần chốt: mock dồn + capstone vận hành + cram + thi | Tất cả | 🏁 Mock #2–3 → Thi | [week-08/](study-plan/week-08/README.md) |

> 📈 Tiến trình phủ domain: **FUND** (T1) → **CFG** (T2–3, domain nặng nhất) → **ARCH** (T4) → **SEC** (T5) → **CONNECT** (T6) → **OBS + TROUBLE** (T7) → chốt (T8).

### ✅ Cơ chế ĐẢM BẢO ĐẬU

1. **Cổng tự kiểm tra:** không sang tuần mới nếu chưa trả lời trôi chảy câu hỏi ở cổng tuần hiện tại.
2. **Sổ câu sai + spaced repetition:** mọi câu sai → ghi đề, đáp án đúng, **lý do sai**; ôn lại theo mốc **1 / 3 / 7 ngày**. Viết file phân tích trong [`CCAAK/questions/`](questions/README.md).
3. **Ngưỡng checkpoint:** mini-mock CFG ≥70% (T3), SEC ≥70% (T5) mới đi tiếp.
4. **Ngưỡng đăng ký thi — chỉ đặt lịch khi đủ cả 4:**
   - ✅ **≥3 bộ mock khác nhau đạt ≥80%** ổn định.
   - ✅ Review hết **100% câu sai**.
   - ✅ Đọc trôi **bảng số §6** và **bảng phản xạ §7**.
   - ✅ Hoàn thành **capstone vận hành** Tuần 8.
5. **Van an toàn:** một full mock **<70%** → **lùi lịch thi 1 tuần**.

---

## 4. Kiến thức theo Domain

### 🟦 Domain 1 — Cluster Configuration (22%, nặng nhất)

- **Broker config theo nhóm:** threads (`num.network.threads` 3, `num.io.threads` 8, `num.replica.fetchers` 1, `background.threads` 10), socket (`socket.send/receive.buffer.bytes` 100 KiB, `socket.request.max.bytes` 100 MiB, `queued.max.requests` 500), storage (`log.dirs` nhiều ổ, JBOD), log (`log.retention.*`, `log.segment.bytes`, `log.roll.*`, `log.cleaner.*`).
- **Topic-level override** và thứ tự ưu tiên: `DYNAMIC_TOPIC_CONFIG` > `DYNAMIC_BROKER_CONFIG` > `DYNAMIC_DEFAULT_BROKER_CONFIG` > `STATIC_BROKER_CONFIG` > `DEFAULT_CONFIG`.
- **Config động vs tĩnh:** cái nào đổi được bằng `kafka-configs.sh` lúc chạy, cái nào cần restart.
- **Durability:** `default.replication.factor`, `min.insync.replicas`, `unclean.leader.election.enable`, internal topic RF (`offsets.topic.replication.factor` 3, `transaction.state.log.replication.factor` 3, `transaction.state.log.min.isr` 2).
- **Retention & compaction:** time vs size, `cleanup.policy` delete/compact/cả hai, `min.cleanable.dirty.ratio`, `delete.retention.ms`, và bẫy **segment active không bị xoá**.
- **Partition planning:** công thức `max(T/P, T/C)`, chi phí over-partition, **không giảm được partition**.
- **Quotas:** `producer_byte_rate`, `consumer_byte_rate`, `request_percentage`, `controller_mutation_rate`; 8 mức ưu tiên.
- **Throughput tuning nhìn từ broker:** compression, batch, `replica.fetch.max.bytes`, `num.replica.fetchers`.

### 🟩 Domain 2 — Fundamentals (15%)

- Topic/partition/offset (committed vs current), leader/follower, **ISR**, `replica.lag.time.max.ms`.
- `acks` và tương tác với `min.insync.replicas`; high watermark; ELR.
- Consumer group coordination, nguyên nhân rebalance, `__consumer_offsets`.
- Ordering chỉ trong partition; key → partition.
- **KRaft**: controller quorum, metadata log, `process.roles`, vì sao ZooKeeper bị gỡ.

### 🟥 Domain 3 — Security (15%)

- **3 lớp**: encryption (TLS) · authentication (mTLS, SASL PLAIN/SCRAM/GSSAPI/OAUTHBEARER) · authorization (ACL).
- Listener và `listener.security.protocol.map`, `inter.broker.listener.name`, `controller.listener.names`.
- **ACL vận hành ở quy mô**: `kafka-acls.sh`, pattern LITERAL vs PREFIXED, `super.users`, `allow.everyone.if.no.acl.found`, Deny thắng Allow, principal mapping từ DN.
- Quản lý credential: SCRAM lúc chạy, xoay chứng chỉ, hạn cert, `kafka-storage.sh format --add-scram`.
- Quotas như công cụ bảo vệ multi-tenant; audit log.
- Encryption at rest: Kafka **không có sẵn** → disk/volume encryption.

### 🟨 Domain 4 — Troubleshooting (15%)

- **Playbook theo triệu chứng**: URP > 0, offline partition, ISR flapping, lag tăng, rebalance lặp, disk đầy, broker không join, controller không bầu được, produce timeout, consumer bị kick.
- Đọc log: `server.log`, `controller.log`, `state-change.log`, `kafka-authorizer.log`, log4j2.
- Exception cheat-sheet ở góc admin: `NotEnoughReplicas`, `NotLeaderOrFollower`, `KafkaStorageException`, `OffsetOutOfRange`, `TimeoutException`, `UnknownTopicOrPartition`, `LeaderNotAvailable`, `InconsistentClusterId`.
- Công cụ: `kafka-log-dirs.sh`, `kafka-dump-log.sh`, `kafka-metadata-quorum.sh`, `kafka-leader-election.sh`, `kafka-reassign-partitions.sh`, `kafka-consumer-groups.sh`.

### 🟪 Domain 5 — Deployment Architecture (12%)

- **Sizing**: số broker, số partition, disk = throughput × retention × RF, network, page cache.
- **Controller**: tách riêng vs combined; quorum 3 hay 5; đặt ở đâu.
- **Rack awareness** `broker.rack` và ảnh hưởng tới replica placement; follower fetching (`client.rack`, KIP-392).
- **Multi-DC**: stretch cluster (2.5 DC) vs cluster tách rời + replication; độ trễ và quorum.
- **DR**: RPO/RTO, **MirrorMaker 2** (3 connector, `DefaultReplicationPolicy` vs `IdentityReplicationPolicy`, offset translation), **Cluster Linking** (Confluent, byte-for-byte, giữ nguyên offset).
- Tiered storage cho retention dài; JBOD và log dir cordoning.

### 🟫 Domain 6 — Kafka Connect (12%)

- Standalone vs distributed; worker config, `group.id`, 3 internal topic (**1/25/5**, compacted, RF cao).
- Scaling worker và task; `tasks.max` là **trần**, connector tự quyết; task dư ở sink sẽ **nằm không**.
- REST API ops: tạo, sửa, `/status`, `restart?includeTasks=true`, pause/resume, `DELETE /connectors/<n>/offsets`.
- Converter vs SMT; DLQ **chỉ sink**; `errors.tolerance`.
- Vận hành: `plugin.path`, nâng cấp plugin, `connector.client.config.override.policy`, rebalance của Connect.

### 🟧 Domain 7 — Observability (10%)

- JMX + Prometheus JMX Exporter + Grafana; MBean naming.
- Metric "đèn đỏ": `UnderReplicatedPartitions`, `OfflinePartitionsCount`, `ActiveControllerCount`, `UnderMinIsrPartitionCount`, `IsrShrinks/ExpandsPerSec`, `RequestHandlerAvgIdlePercent`, `TotalTimeMs` tách 5 pha.
- Consumer lag: theo **committed** (tool) vs theo **position** (client metric).
- Alerting: ngưỡng nào đáng gọi dậy lúc 3 giờ sáng, ngưỡng nào chỉ cần ticket.

---

## 5. Deep-dive từng mảng vận hành

### ⭐ Broker configuration — mảng lớn nhất của đề

- **Threads**: `num.network.threads` xử lý socket, `num.io.threads` xử lý request (đo bằng `NetworkProcessorAvgIdlePercent` và `RequestHandlerAvgIdlePercent`, lý tưởng > 0.3). `num.replica.fetchers` quyết định tốc độ follower bắt kịp — tăng khi URP lâu về 0.
- **`log.dirs` nhiều ổ đĩa (JBOD)**: Kafka rải partition theo số partition mỗi thư mục, **không** theo dung lượng. Một ổ hỏng → chỉ partition trên ổ đó offline (từ KRaft JBOD). `kafka-log-dirs.sh` để xem phân bố.
- **Config động**: `kafka-configs.sh --alter --entity-type brokers --entity-default` (cluster-wide) vs `--entity-name <id>` (một broker). Read-only config cần restart.
- **Bẫy**: đổi `min.insync.replicas` ở broker-level **không** áp cho topic đã có override; luôn kiểm bằng `--describe --all` và đọc cột synonyms.

### ⭐ Durability — bộ ba phải thuộc

`replication.factor=3` + `min.insync.replicas=2` + producer `acks=all` = chịu mất **1 broker** không mất dữ liệu, vẫn ghi được.
Đặt `min.insync.replicas=3` là **over-correction**: mất 1 broker là ngừng ghi. Đây là câu hỏi lặp lại nhiều lần trong đề.
Internal topic cũng cần RF cao: `offsets.topic.replication.factor=3`, `transaction.state.log.replication.factor=3`, `transaction.state.log.min.isr=2` — cluster 1 broker phải hạ xuống 1 nếu không sẽ lỗi khi tạo.

### ⭐ Capacity planning

- **Partition**: `max(throughput cần / throughput một producer, throughput cần / throughput một consumer)`; cộng biên tăng trưởng. Nhớ **không giảm được**.
- **Disk**: `throughput ghi × retention × RF × 1.2` (hệ số dự phòng). Cộng thêm nếu bật tiered storage thì local retention nhỏ hơn nhiều.
- **Broker**: đủ để một broker chết vẫn còn công suất; page cache quan trọng hơn heap (heap ~6 GB là đủ, phần RAM còn lại để OS làm page cache).
- **Giới hạn thực tế**: hàng nghìn partition mỗi broker; KRaft chịu được nhiều hơn ZooKeeper cũ, nhưng vẫn tốn file descriptor và thời gian leader election.

### ⭐ JVM & OS

- Heap **6 GB** là khuyến nghị phổ biến cho broker; **G1GC**; tránh heap quá lớn vì Kafka dựa vào **page cache** chứ không phải heap.
- **File descriptor**: đặt rất cao (100k+) — mỗi partition, mỗi segment, mỗi connection đều tốn.
- **`vm.swappiness` thấp** (1) để tránh swap; filesystem XFS thường được khuyến nghị.
- Tách ổ đĩa log Kafka khỏi ổ hệ điều hành.

### ⭐ Rolling upgrade & maintenance

- Nâng từng broker: `controlled.shutdown.enable=true` → tắt → thay binary → khởi động → **chờ URP về 0** → broker kế tiếp.
- Sau khi mọi broker lên bản mới: finalize bằng `kafka-features.sh upgrade --release-version 4.3`; `metadata.version` thay vai trò `inter.broker.protocol.version` cũ.
- **Thêm broker không tự nhận partition** → `kafka-reassign-partitions.sh --generate/--execute --throttle/--verify`, nhớ gỡ throttle.
- Preferred leader election để trả leader về đúng chỗ sau bảo trì.

### ⭐ Disaster recovery

| Cách | Cơ chế | Offset | Khi nào dùng |
|---|---|---|---|
| **MirrorMaker 2** | 3 connector trên Connect | **Đổi**, cần offset translation qua checkpoint | Apache Kafka thuần, active-active hoặc active-passive |
| **Cluster Linking** | Confluent Platform, broker kéo trực tiếp | **Giữ nguyên byte-for-byte** | Confluent Platform, DR và migration đơn giản hơn |
| **Stretch cluster** | Một cluster trải nhiều DC | Không cần | DC gần nhau, độ trễ thấp, cần RPO = 0 |

### ⭐ Chẩn đoán có phương pháp

Luôn theo thứ tự: **metric → log → config → hành động**, và ưu tiên hành động **rẻ, đảo ngược được** trước.
Ví dụ với lag tăng: kiểm skew trước (miễn phí) → thêm consumer (rẻ, đảo ngược được) → tăng partition (**một chiều**, phá ordering) → tối ưu code (chậm).

---

## 6. Những con số PHẢI thuộc lòng

> Đã đối chiếu https://kafka.apache.org/43/generated/kafka_config.html ngày 2026-09-20.

### Broker — threads & socket
- `num.network.threads` **3** · `num.io.threads` **8** · `num.replica.fetchers` **1** · `background.threads` **10**
- `queued.max.requests` **500** · `socket.send.buffer.bytes` / `socket.receive.buffer.bytes` **102400** (100 KiB) · `socket.request.max.bytes` **104857600** (100 MiB)
- `num.recovery.threads.per.data.dir` **2** (đổi từ 1 ở 4.0)

### Broker — durability & leader
- `default.replication.factor` **1** · `min.insync.replicas` **1** · `num.partitions` **1** *(production: RF 3 / min.isr 2)*
- `unclean.leader.election.enable` **false** · `replica.lag.time.max.ms` **30000** · `replica.socket.timeout.ms` **30000**
- `auto.leader.rebalance.enable` **true** · `leader.imbalance.check.interval.seconds` **300**
- `controlled.shutdown.enable` **true**
- `offsets.topic.replication.factor` **3** · `transaction.state.log.replication.factor` **3** · `transaction.state.log.min.isr` **2**
- `__consumer_offsets` **50** partition · `__transaction_state` **50** partition

### Broker — log & retention
- `log.retention.hours` **168** (7 ngày) · `log.retention.bytes` **-1** · `log.segment.bytes` **1 GiB** · `log.roll.hours` **168**
- `log.retention.check.interval.ms` **300000** · `log.cleaner.threads` **1** · `min.cleanable.dirty.ratio` **0.5** · `log.cleaner.delete.retention.ms` **86400000** (24 h)
- `log.index.interval.bytes` **4096** · `segment.index.bytes` **10485760** (10 MiB) · `log.segment.delete.delay.ms` **60000** · `segment.jitter.ms` **0**
- `min.compaction.lag.ms` **0** · `max.compaction.lag.ms` **Long.MAX** · `log.cleaner.backoff.ms` **15000** · `log.cleaner.dedupe.buffer.size` **128 MiB**
- Tiered storage: `log.local.retention.ms` / `log.local.retention.bytes` mặc định **-2** (nghĩa là *dùng theo `retention.ms`/`retention.bytes`*, không phải "vô hạn")
- `delete.topic.enable` **true** (read-only, cần restart) · `compression.type` ở broker **producer** (không nén lại)
- `message.max.bytes` **1048588** · `replica.fetch.max.bytes` **1048576**
- ⚠️ `replica.fetch.response.max.bytes` **10485760 (10 MiB)** — **không phải 1 MiB**; đề và tài liệu bên thứ ba hay ghi nhầm
- `replica.fetch.wait.max.ms` **500** · `replica.fetch.min.bytes` **1** · `replica.socket.receive.buffer.bytes` **65536** · `replica.high.watermark.checkpoint.interval.ms` **5000**
- `broker.session.timeout.ms` **9000** · `broker.heartbeat.interval.ms` **2000**
- Quota window: `quota.window.num` **11** × `quota.window.size.seconds` **1**
- `auto.create.topics.enable` **true** *(production nên tắt)*

### KRaft
- Quorum **3 hoặc 5** controller (lẻ); chịu mất `(N-1)/2`
- `process.roles` = `broker` | `controller` | `broker,controller` (combined **chỉ cho dev**)
- Metadata ở `__cluster_metadata` (**1 partition**); broker là **observer** của quorum
- Format bằng `kafka-storage.sh format` với **cùng `cluster.id`** — sai thì `InconsistentClusterIdException`
- **Timer của quorum**: `controller.quorum.election.timeout.ms` **1000** · `controller.quorum.fetch.timeout.ms` **2000** · `controller.quorum.request.timeout.ms` **2000** · `controller.quorum.election.backoff.max.ms` **1000** · `controller.quorum.append.linger.ms` **25**
- ⚠️ `fetch.timeout.ms` có **hai vế**: voter không fetch được thì **tự ứng cử**, và leader không nhận fetch từ đa số thì **tự từ chức** (chống split-brain)
- **Metadata log**: `metadata.log.dir` mặc định `null` → dùng **thư mục đầu tiên** của `log.dirs`; `metadata.log.segment.bytes` **1 GiB**; `metadata.max.retention.bytes` **100 MiB**; `metadata.max.retention.ms` **7 ngày**
- `kraft.version` **0** = static quorum (`controller.quorum.voters`) · **1** = dynamic quorum (`controller.quorum.bootstrap.servers`, KIP-853)
- Sizing controller: khoảng **5 GB RAM + 5 GB đĩa** — nhẹ hơn broker nhiều
- KRaft production-ready từ **3.3**; **bắt buộc** từ 4.0
- Kafka 4.0: Java **17** cho broker/Connect/tools, Java **11** cho client; baseline client protocol **2.1**

### Thay đổi đáng nhớ của Kafka 4.1 → 4.3 (góc vận hành)
- **ELR bật mặc định cho cluster mới từ 4.1** — và khi bật thì **`min.insync.replicas` ở mức broker bị gỡ**, phải đặt ở mức **cluster** hoặc **topic**. Đây là bẫy nâng cấp dễ dính nhất
- `controller.quorum.auto.join.enable` mặc định **false** (4.3) — controller mới **không** tự gia nhập quorum, phải thêm tay bằng `kafka-metadata-quorum.sh add-controller`
- `group.coordinator.background.threads` **1 → 2** (4.3)
- Giá trị nhỏ nhất cho phép của `segment.bytes`: **14 byte → 1 MiB** (4.3) — script cũ đặt segment siêu nhỏ để test sẽ bị từ chối
- `message.timestamp.after.max.ms`: **Long.MAX → 1 giờ** — record có timestamp tương lai quá 1 giờ bị từ chối
- `remote.log.metadata.topic.min.isr` mặc định **2** · `__share_group_state` RF mặc định **3**
- **Downgrade không phải lúc nào cũng được**: phụ thuộc có thay đổi metadata giữa hai bản hay không (4.2.0 downgrade được; 4.0.1, 4.1.0 và 4.3.0 thì không). Kiểm trước khi finalize `metadata.version`

### JVM & OS (khuyến nghị vận hành, không phải default)
- Heap broker **6 GB**, dùng **G1GC**; phần RAM còn lại để **page cache**
- File descriptor **100.000+** · `vm.swappiness` **1** · filesystem **XFS**

### Cổng
- Broker **9092** · Controller **9093** · JMX thường **9999** · Connect REST **8083** · Schema Registry **8081** · ksqlDB **8088**

### Connect
- `connect-configs` **1** partition · `connect-offsets` **25** · `connect-status` **5** — đều compacted
- DLQ **chỉ sink connector**

---

## 7. Bảng phản xạ: Triệu chứng → Hành động

> Đây là bảng quan trọng nhất cho CCAAK. Đề hỏi *"người vận hành làm gì tiếp theo"*.

| Triệu chứng quan sát được | Nguyên nhân khả dĩ | Hành động đầu tiên |
|---|---|---|
| `UnderReplicatedPartitions` > 0 kéo dài | Broker chết / follower tụt / mạng | Kiểm broker sống chưa, rồi tăng `num.replica.fetchers` |
| `OfflinePartitionsCount` > 0 | Không còn leader cho partition | Kiểm ISR; cân nhắc ELR; unclean election là lựa chọn cuối |
| `ActiveControllerCount` tổng ≠ 1 | Controller lỗi hoặc đang failover | `kafka-metadata-quorum.sh describe --status` |
| `UnderMinIsrPartitionCount` > 0 | ISR dưới `min.insync.replicas` | Producer `acks=all` **đang bị chặn** — khôi phục replica gấp |
| `IsrShrinks/ExpandsPerSec` dao động liên tục | GC, disk chậm, mạng | Kiểm GC log và disk latency, không vội chỉnh `replica.lag.time.max.ms` |
| `RequestHandlerAvgIdlePercent` < 0.3 | Thiếu I/O thread | Tăng `num.io.threads` |
| `NetworkProcessorAvgIdlePercent` thấp | Thiếu network thread | Tăng `num.network.threads` |
| `TotalTimeMs` cao ở `RemoteTimeMs` (Produce) | Chờ replica xác nhận | Bình thường với `acks=all`; kiểm follower |
| Consumer lag tăng, CPU thấp, rebalance liên tục | Vượt `max.poll.interval.ms` | Giảm `max.poll.records` hoặc tăng interval |
| Lag tăng, thêm consumer không đỡ | Consumer ≥ số partition | Tăng partition (một chiều!) hoặc sửa key skew |
| Disk gần đầy trên một broker | Phân bố partition lệch | `kafka-log-dirs.sh`, rồi reassign có throttle |
| Broker mới không nhận traffic | Kafka không tự chuyển partition | `kafka-reassign-partitions.sh` |
| Producer nhận `NotEnoughReplicas` | ISR < `min.insync.replicas` | Khôi phục broker; **không** hạ min.isr trong hoảng loạn |
| "Retention đặt 1 giờ mà data vẫn còn" | Segment active chưa đóng | Hạ `segment.ms` hoặc `segment.bytes` |
| Client nối được bootstrap nhưng produce timeout | `advertised.listeners` sai | Sửa advertised listener cho địa chỉ client tới được |
| `InconsistentClusterId` khi broker khởi động | Format sai `cluster.id` | Format lại đúng cluster id |
| Connect task FAILED | Lỗi trong connector | `/status` xem trace, `restart?includeTasks=true` |
| Sink connector bỏ record hỏng im lặng | `errors.tolerance=all` không có DLQ | Thêm `errors.deadletterqueue.topic.name` |
| Client báo `TopicAuthorizationException` | Thiếu ACL topic | `kafka-acls.sh --add --producer/--consumer` |
| Client báo `GroupAuthorizationException` | Thiếu ACL **Group** | Cấp `Read` trên resource Group |
| Throughput bị chặn trần, log sạch | Quota | Kiểm `produce-throttle-time-avg` |
| Cần DR giữ nguyên offset | MM2 đổi offset | **Cluster Linking** (Confluent) |
| Cần retention rất dài, chi phí thấp | Disk broker đắt | **Tiered storage** |

---

## 8. Thực hành hands-on

> Toàn bộ chạy **local bằng Docker**, dùng lại `~/kafka-labs/` và hai file compose chuẩn từ [CCDAK Tuần 1](../CCDAK/study-plan/week-01/labs.md).

### Nhóm Cluster & Config
- [ ] Đổi config động ở 3 mức (topic / broker / cluster-default), đọc synonyms để biết giá trị hiệu lực từ đâu.
- [ ] Dựng broker nhiều `log.dirs`, xem phân bố partition bằng `kafka-log-dirs.sh`, mô phỏng một ổ hỏng.
- [ ] Thí nghiệm ma trận `acks` × `min.insync.replicas` × RF, gây `NotEnoughReplicas` có chủ đích.
- [ ] Đo ảnh hưởng của `num.io.threads` và `num.replica.fetchers` tới thời gian URP về 0.
- [ ] Topic compaction với tombstone; retention với `segment.ms` nhỏ.

### Nhóm Architecture & DR
- [ ] Dựng controller **tách riêng** khỏi broker; tắt controller để xem quorum.
- [ ] Bật `broker.rack`, quan sát replica placement.
- [ ] MirrorMaker 2 giữa 2 cluster; so `DefaultReplicationPolicy` và `IdentityReplicationPolicy`; dịch offset.
- [ ] Rolling upgrade mô phỏng + `kafka-features.sh`.
- [ ] Tiered storage trên topic thử nghiệm.

### Nhóm Security
- [ ] TLS + mTLS với CA tự ký; principal mapping từ DN.
- [ ] SCRAM tạo/xoay/thu hồi user lúc chạy.
- [ ] ACL: gây `TopicAuthorizationException` rồi `GroupAuthorizationException`, sửa bằng prefix pattern.
- [ ] Quota băng thông và quota request rate.

### Nhóm Connect & Observability
- [ ] Connect distributed 2 worker; kill 1 worker xem task chuyển.
- [ ] Task FAILED → đọc `/status` → restart.
- [ ] Prometheus + Grafana; dựng alert cho URP, offline partition, lag.
- [ ] **Capstone Tuần 8:** nhận một cluster "bị phá" và khôi phục theo playbook.

---

## 9. Tài nguyên học tập

### Chính thức
- **Apache Kafka Documentation** — https://kafka.apache.org/documentation/ (§Configuration, §Operations, §Monitoring, §Security, §Geo-Replication, §Tiered Storage).
- **Confluent Documentation** — https://docs.confluent.io/platform/current/ (Kafka Operations, Cluster Linking, Security).
- **Trang chứng chỉ** — https://www.confluent.io/certification/ ; đăng ký tại https://training.confluent.io/.
- **KIP quan trọng cho admin**: KIP-500 (bỏ ZooKeeper), KIP-853 (dynamic quorum), KIP-966 (ELR), KIP-405 (tiered storage), KIP-392 (follower fetching), KIP-1147 (CLI thống nhất).

### Sách
- **Kafka: The Definitive Guide, 2nd ed.** — chương 2 (cài đặt), 6 (reliability), 10 (cross-cluster), 11 (security), 12 (administering), 13 (monitoring). Xem bản đồ chương trong [`../CCDAK/study-plan/week-10/resources/kafka-definitive-guide-chapter-map.md`](../CCDAK/study-plan/week-10/resources/kafka-definitive-guide-chapter-map.md).

### Khoá học
- **Confluent Developer** — https://developer.confluent.io/courses/ (Kafka Internals, Monitoring, Security).
- **Stephane Maarek** — *Kafka Cluster Setup & Administration*.

### Practice
- 🎯 **[3 bộ mock full-length trong repo](mock-exams/README.md)** — 60 câu / 90 phút, theo đúng tỉ trọng 7 domain.
- **Confluent sample questions** trên trang certification.

> ⚠️ **Cảnh báo về đề CCAAK công khai.** Hai kho câu hỏi CCAAK lớn nhất trên GitHub có tỉ lệ nhắc ZooKeeper so với KRaft là **118 trên 3**, và nhiều nơi đặt ZooKeeper làm **đáp án đúng**. Chi tiết đo đạc: [`mock-exams/SOURCES-AND-VALIDATION.md`](mock-exams/SOURCES-AND-VALIDATION.md).

---

## 10. Chiến lược làm bài thi

- **~90 giây/câu.** Câu khó thì đánh dấu và bỏ qua; không bỏ trống câu nào.
- **Đọc triệu chứng trước, đáp án sau.** Xác định đang hỏi trục nào: durability, availability, throughput hay chi phí vận hành.
- **Ưu tiên hành động rẻ và đảo ngược được.** Đề thường có một phương án "đúng nhưng quá tay" (tăng partition, bật unclean election, hạ min.isr) — đó là bẫy.
- **Nhận diện version.** Nếu phương án nhắc ZooKeeper, znode, `--zookeeper`, hoặc `zookeeper.connect` thì gần như chắc chắn sai với Kafka 4.x.
- **Qualifier quyết định:** *without data loss* · *with minimal downtime* · *fewest changes* · *survive the loss of one rack* · *without restarting brokers*.
- **Multiple select:** đọc kỹ số lượng cần chọn.
- **Dạng matching và list order:** luyện bằng cách tự vẽ lại thứ tự rolling upgrade, thứ tự chẩn đoán, các bước reassignment.

---

## 11. CHECKLIST TOÀN DIỆN

### 📋 A. Chuẩn bị
- [ ] Đọc trang chứng chỉ, nắm format và chính sách.
- [ ] Nắm bảng tỉ trọng 7 domain để phân bổ thời gian.
- [ ] Dựng lại cluster Docker 3 broker + Prometheus/Grafana từ CCDAK.
- [ ] Ôn nhanh CCDAK Tuần 1, 2, 7, 8 (xem [§2](#2-ccaak-nhìn-từ-người-đã-học-ccdak)).

### 🟦 B. Cluster Configuration (22%)
- [ ] Thuộc nhóm config threads, socket, log, durability và giá trị mặc định.
- [ ] Giải thích thứ tự ưu tiên config và đọc được synonyms.
- [ ] Phân biệt config động và config cần restart.
- [ ] Ma trận `acks` × `min.insync.replicas` × RF.
- [ ] Retention vs segment roll; compaction và tombstone.
- [ ] Partition sizing và hệ quả của việc tăng partition.
- [ ] Quotas 4 loại và 8 mức ưu tiên.

### 🟩 C. Fundamentals (15%)
- [ ] ISR, high watermark, ELR, leader election.
- [ ] Consumer group, rebalance, `__consumer_offsets`.
- [ ] KRaft: quorum, metadata log, formatting.

### 🟥 D. Security (15%)
- [ ] Listener và protocol map; 4 giá trị `security.protocol`.
- [ ] TLS, mTLS, principal mapping.
- [ ] 4 SASL mechanism và khi nào dùng.
- [ ] ACL: operation × resource, PREFIXED, Deny thắng, `super.users`.
- [ ] Xoay credential và chứng chỉ mà không downtime.

### 🟨 E. Troubleshooting (15%)
- [ ] Playbook cho 10 triệu chứng hàng đầu ở [§7](#7-bảng-phản-xạ-triệu-chứng--hành-động).
- [ ] Biết đọc `server.log`, `controller.log`, `state-change.log`.
- [ ] Exception cheat-sheet góc admin.

### 🟪 F. Deployment Architecture (12%)
- [ ] Sizing broker, partition, disk.
- [ ] Controller tách riêng, quorum 3/5.
- [ ] Rack awareness và follower fetching.
- [ ] MM2 vs Cluster Linking vs stretch cluster; RPO/RTO.
- [ ] Rolling upgrade và `kafka-features.sh`.

### 🟫 G. Kafka Connect (12%)
- [ ] Distributed worker, internal topic, scaling.
- [ ] `tasks.max` là trần; task sink dư nằm không.
- [ ] REST ops và khôi phục task lỗi.
- [ ] DLQ chỉ sink.

### 🟧 H. Observability (10%)
- [ ] Metric đèn đỏ và ngưỡng.
- [ ] Prometheus + Grafana + alert.
- [ ] Lag theo committed vs theo position.

### 🏁 I. Đủ điều kiện thi
- [ ] Hoàn thành toàn bộ lab [§8](#8-thực-hành-hands-on) + capstone Tuần 8.
- [ ] Qua mọi cổng tự kiểm tra Tuần 1–7.
- [ ] Mini-mock CFG ≥70%, SEC ≥70%.
- [ ] **≥3 bộ mock khác nhau ≥80%**.
- [ ] Review 100% câu sai; viết file phân tích trong `CCAAK/questions/`.
- [ ] Đọc trôi **§6** và **§7** không cần tra.
- [ ] Đặt lịch thi, chạy Honorlock System Check, chuẩn bị giấy tờ.
