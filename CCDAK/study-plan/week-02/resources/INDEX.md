# 📂 Tài nguyên Tuần 2 — Độ tin cậy & lưu trữ: replication, retention, log compaction, delivery semantics

> Crawl từ tài liệu Apache Kafka chính thức (bản 4.3). Về [file học Tuần 2](../README.md) · [Kế hoạch tổng](../../../CCDAK-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn |
| - | --- | --- | --- |
| 1 | [kafka-replication-isr.md](kafka-replication-isr.md) | Replication: leader/follower, **ISR**, `replica.lag.time.max.ms` 30 s, committed & high watermark, `acks` 0/1/all × `min.insync.replicas`, f+1 vs 2f+1, unclean leader election, preferred leader, `broker.rack` | https://kafka.apache.org/43/design/design/#replication |
| 2 | [kafka-eligible-leader-replicas.md](kafka-eligible-leader-replicas.md) | **ELR (KIP-966)**: thứ tự bầu leader ISR → ELR → last known leader, `eligible.leader.replicas.version`, ràng buộc `min.insync.replicas` cluster-level, durability guarantees, replica management | https://kafka.apache.org/43/operations/eligible-leader-replicas/ |
| 3 | [kafka-topic-configs.md](kafka-topic-configs.md) | Topic-level configs: `retention.ms/bytes`, `segment.bytes/ms`, `cleanup.policy`, `delete.retention.ms`, `min.cleanable.dirty.ratio`, `max.message.bytes` 1 048 588, `compression.type=producer`, `message.timestamp.type`, tiered storage `remote.storage.enable`, lệnh `kafka-configs.sh` | https://kafka.apache.org/43/generated/topic_config.html |
| 4 | [kafka-log-compaction.md](kafka-log-compaction.md) | **Log compaction**: head/tail, tombstone, 4 đảm bảo, `delete.retention.ms` 24 h, dirty ratio 0.5, `min/max.compaction.lag.ms`, log cleaner threads, use case `__consumer_offsets`/changelog/CDC | https://kafka.apache.org/43/design/design/#log-compaction |
| 5 | [kafka-delivery-semantics.md](kafka-delivery-semantics.md) | **Delivery semantics**: at-most/at-least/exactly-once, commit trước vs sau xử lý, idempotent producer (PID + sequence), transactions + `read_committed`, ghi ra hệ thống ngoài | https://kafka.apache.org/43/design/design/#message-delivery-semantics |
| 6 | [kafka-share-groups.md](kafka-share-groups.md) | **Share groups / Queues for Kafka (KIP-932, GA 4.2)**: acquisition lock 30 s (`share.record.lock.duration.ms`), ACCEPT/RELEASE/REJECT, `share.delivery.count.limit` 5, implicit/explicit ack, `kafka-share-groups.sh`, `kafka-console-share-consumer.sh`, `__share_group_state` | https://kafka.apache.org/43/design/design/#share-groups |

> 📌 2 KIP gốc (KIP-932, KIP-966) trên `cwiki.apache.org` **không crawl được** lúc viết (timeout) — 2 file #2 và #6 dùng docs 4.3 đã GA làm nguồn chính và ghi link KIP để đọc thêm.

## Gợi ý thứ tự đọc

1. **Replication trước hết (1 → 2):** đọc `kafka-replication-isr.md` để nắm ISR / committed / HW / `acks` × `min.insync.replicas` — đây là cụm hỏi nặng nhất của tuần và của toàn domain FUND. Rồi đọc `kafka-eligible-leader-replicas.md` để hiểu 4.x đổi gì trong bầu leader (ISR → ELR → last known leader) và vì sao `min.insync.replicas` giờ là cluster-level.
2. **Lưu trữ (3 → 4):** đọc bảng topic config trong `kafka-topic-configs.md` (nhớ 3 cặp topic ↔ broker: `retention.ms` ↔ `log.retention.ms`, `max.message.bytes` ↔ `message.max.bytes`, `segment.ms` ↔ `log.roll.ms`), rồi `kafka-log-compaction.md` — chú ý "compact chỉ đụng segment đã đóng" và "tombstone sống 24 h".
3. **Delivery semantics (5):** đọc trước Lab 2.1; ghi nhớ bảng 2 nửa producer / consumer. Phần transactions chỉ cần nhận diện — Tuần 3 đi sâu.
4. **Share groups (6):** đọc cuối, ngay trước Lab 2.6. Mục tiêu tuần này là **nhận diện**: khi nào chọn share group thay consumer group + 3 loại acknowledge + số 30 s / 5 lần. Consumer chuyên sâu để Tuần 4.
