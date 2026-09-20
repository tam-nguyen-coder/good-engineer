# Apache Kafka 4.3 — Topic Configs và quan hệ với broker default

> **Nguồn (official):** https://kafka.apache.org/43/generated/topic_config.html (bản có mục lục: https://kafka.apache.org/43/configuration/topic-configs/)
> **Tuần:** 2 — Cluster Config I: broker config, storage & `log.dirs`, retention, compaction · **Loại:** Apache Kafka Docs (config reference)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Mỗi topic config có một **"server default property"** tương ứng ở broker. Broker default chỉ là **giá trị khởi tạo** khi topic **được tạo mà không khai** config đó. Topic đã có override rồi thì **đổi broker default không ảnh hưởng gì** — đây là bẫy vận hành số 1 của tuần.
- **Cặp tên khác nhau giữa 2 tầng** (rất hay bị hỏi): topic `segment.bytes` ↔ broker `log.segment.bytes`; topic `segment.ms` ↔ broker **`log.roll.ms`** (không phải `log.segment.ms`); topic `retention.ms` ↔ `log.retention.ms`; topic `min.cleanable.dirty.ratio` ↔ broker **`log.cleaner.min.cleanable.ratio`**; topic `delete.retention.ms` ↔ broker **`log.cleaner.delete.retention.ms`**; topic `max.message.bytes` ↔ broker **`message.max.bytes`**; topic `file.delete.delay.ms` ↔ broker **`log.segment.delete.delay.ms`**; topic `index.interval.bytes` ↔ broker `log.index.interval.bytes`; topic `segment.index.bytes` ↔ broker `log.index.size.max.bytes`.
- **Con số phải thuộc:** `segment.bytes` **1 GiB** · `segment.ms` **7 ngày** · `segment.index.bytes` **10 MiB** · `retention.ms` **7 ngày** · `retention.bytes` **-1** · `delete.retention.ms` **1 ngày (86400000)** · `min.cleanable.dirty.ratio` **0.5** · `min.compaction.lag.ms` **0** · `max.compaction.lag.ms` **Long.MAX** · `max.message.bytes` **1048588** · `index.interval.bytes` **4 KiB** · `file.delete.delay.ms` **1 phút** · `min.insync.replicas` **1** · `unclean.leader.election.enable` **false**.
- `cleanup.policy` nhận **`delete`** (mặc định), **`compact`**, hoặc **`compact,delete`**. Danh sách rỗng = giữ vô hạn, không xoá cũng không compact.
- `retention.bytes` tính **trên từng partition**, không phải cả topic: topic 6 partition với `retention.bytes=1073741824` chiếm tối đa ~6 GiB mỗi bản replica.
- **Tiered storage ở tầng topic:** `remote.storage.enable` **false** (không có server default property — phải bật per-topic), `local.retention.ms` / `local.retention.bytes` mặc định **-2** = "kế thừa `retention.ms`/`retention.bytes`".
- `flush.messages` / `flush.ms` mặc định **Long.MAX** → Kafka **không fsync theo message**; đừng hạ xuống trừ khi có lý do rất cụ thể.
- `message.timestamp.type` **CreateTime** (producer gán) vs `LogAppendTime` (broker ghi đè) — ảnh hưởng trực tiếp tới việc retention theo thời gian tính theo đồng hồ nào.

---

## 📄 Nội dung (trích từ tài liệu gốc)

| Name | Default | Server Default Property | Description |
|------|---------|------------------------|-------------|
| `cleanup.policy` | delete | `log.cleanup.policy` | "Retention policy to use on log segments" — `delete`, `compact`, hoặc cả hai |
| `segment.bytes` | 1 GiB | `log.segment.bytes` | Controls the size of individual log segment files |
| `segment.ms` | 7 days | `log.roll.ms` | Period after which Kafka forces log rolling |
| `segment.index.bytes` | 10 MiB | `log.index.size.max.bytes` | Size of the index mapping offsets to file positions |
| `segment.jitter.ms` | 0 | `log.roll.jitter.ms` | Maximum random jitter subtracted from segment roll time |
| `retention.ms` | 7 days | `log.retention.ms` | "Maximum time to retain a log before discarding old segments" |
| `retention.bytes` | -1 | `log.retention.bytes` | Maximum partition size before discarding old segments |
| `delete.retention.ms` | 1 day | `log.cleaner.delete.retention.ms` | Time to retain delete tombstone markers for compacted topics |
| `min.cleanable.dirty.ratio` | 0.5 | `log.cleaner.min.cleanable.ratio` | Threshold controlling log compactor cleaning frequency |
| `min.compaction.lag.ms` | 0 | `log.cleaner.min.compaction.lag.ms` | Minimum time message remains uncompacted in log |
| `max.compaction.lag.ms` | Long.MAX | `log.cleaner.max.compaction.lag.ms` | Maximum time message remains ineligible for compaction |
| `max.message.bytes` | 1,048,588 | `message.max.bytes` | "Largest record batch size allowed by Kafka" |
| `index.interval.bytes` | 4 KiB | `log.index.interval.bytes` | Controls how frequently offset index entries are added |
| `file.delete.delay.ms` | 1 minute | `log.segment.delete.delay.ms` | Time to wait before deleting a file from the filesystem |
| `min.insync.replicas` | 1 | `min.insync.replicas` | Minimum in-sync replicas required for `acks=all` writes |
| `compression.type` | producer | `compression.type` | Final compression codec for the topic |
| `message.timestamp.type` | CreateTime | `log.message.timestamp.type` | Whether timestamp is message create time or log append time |
| `remote.storage.enable` | false | *(null — không có)* | Enables tiered storage for the topic |
| `local.retention.ms` | -2 | `log.local.retention.ms` | Milliseconds to keep local log segment before deletion |
| `local.retention.bytes` | -2 | `log.local.retention.bytes` | Maximum size of local log segments before deletion |
| `flush.messages` | Long.MAX | `log.flush.interval.messages` | Interval at which fsync is forced after message count |
| `flush.ms` | Long.MAX | `log.flush.interval.ms` | Time interval at which fsync is forced on log data |
| `preallocate` | false | `log.preallocate` | Whether to preallocate file space when creating segment |
| `unclean.leader.election.enable` | false | `unclean.leader.election.enable` | Allow out-of-ISR replicas as leader as last resort |

### Đặt và gỡ override ở tầng topic

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics \
  --entity-name my_topic_name --alter --add-config x=y

$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics \
  --entity-name my_topic_name --alter --delete-config x
```

> 📌 Gỡ override (`--delete-config`) **không** đặt config về giá trị mặc định in trong bảng trên — nó trả topic về **giá trị broker đang hiệu lực** (có thể là dynamic cluster default, có thể là static). Đây là điểm khiến `--describe --all` và cột **synonyms** trở thành công cụ bắt buộc: xem [confluent-dynamic-config-precedence.md](confluent-dynamic-config-precedence.md).
