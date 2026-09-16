# Apache Kafka — Topic-Level Configs (retention, segment, compaction, message size, timestamps)

> **Nguồn (official):** https://kafka.apache.org/43/generated/topic_config.html (trang đầy đủ: https://kafka.apache.org/43/configuration/topic-configs/) · bổ sung lệnh từ https://kafka.apache.org/43/operations/basic-kafka-operations/
> **Tuần:** 2 — Độ tin cậy & lưu trữ · **Loại:** Apache Kafka Docs (4.3)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch + curl, rút gọn còn các config liên quan Tuần 2) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Mỗi topic config có **"Server Default Property"** tương ứng ở broker (vd `retention.ms` ↔ `log.retention.ms`, `max.message.bytes` ↔ `message.max.bytes`, `segment.ms` ↔ `log.roll.ms`, `cleanup.policy` ↔ `log.cleanup.policy`). Topic config **ghi đè** broker default; đổi lúc chạy bằng `kafka-configs.sh --alter --add-config` / `--delete-config` (xoá override → quay về default broker).
- **Retention (policy `delete`):** `retention.ms` = **604 800 000 (7 ngày)**; `retention.bytes` = **-1** (không giới hạn size, tính **per partition**); `retention.ms=-1` = giữ vĩnh viễn. Retention **áp theo segment đã đóng** ("Retention and cleaning is always done a file at a time") → data trong **active segment không bao giờ bị xoá** dù quá hạn. Broker kiểm tra mỗi `log.retention.check.interval.ms` = **300 000 (5 phút)**.
- **Segment:** `segment.bytes` = **1 GiB** (min 1 MiB); `segment.ms` = **7 ngày** ("force the log to roll even if the segment file isn't full to ensure that retention can delete or compact old data"); `segment.jitter.ms` = 0; `segment.index.bytes` = 10 MiB; `file.delete.delay.ms` = 60 000.
- **Compaction:** `cleanup.policy` = `delete` | `compact` | `compact,delete`; `min.cleanable.dirty.ratio` = **0.5**; `delete.retention.ms` = **86 400 000 (1 ngày)**; `min.compaction.lag.ms` = **0**; `max.compaction.lag.ms` = MAX_LONG.
- **Message size:** `max.message.bytes` = **1 048 588** (batch size **sau nén**, topic-level của broker `message.max.bytes`). Producer có `max.request.size` (1 048 576) riêng; consumer `max.partition.fetch.bytes` (1 MB) / `fetch.max.bytes` (50 MB); follower `replica.fetch.max.bytes` (1 MB).
- **Durability:** `min.insync.replicas` = **1** (chỉ tác dụng với `acks=all`); `unclean.leader.election.enable` = **false**.
- **Compression:** `compression.type` = **`producer`** (giữ codec producer gửi lên; broker không nén lại); các giá trị: `uncompressed`, `gzip`, `snappy`, `lz4`, `zstd`; có `compression.<codec>.level`.
- **Timestamp:** `message.timestamp.type` = **`CreateTime`** (producer đặt) | `LogAppendTime` (broker ghi đè lúc append). `message.timestamp.after.max.ms` = 1 h; `message.timestamp.before.max.ms` = MAX_LONG.
- **Tiered storage:** `remote.storage.enable` (false), `local.retention.ms/bytes` = **-2** (= dùng giá trị `retention.*`), `remote.log.copy.disable`, `remote.log.delete.on.disable`.
- **Flush:** `flush.messages` / `flush.ms` = MAX_LONG (Kafka dựa vào replication + OS page cache, **không fsync mỗi message**).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Topic-Level Configs

Configurations pertinent to topics have both a server default as well an optional per-topic override. If no per-topic configuration is given the server default is used. The override can be set at topic creation time by giving one or more `--config` options. Overrides can also be changed or set later using the alter configs command:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my_topic_name --alter --add-config max.message.bytes=128000
```

To check overrides set on the topic you can do

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my_topic_name --describe
```

To remove an override you can do

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my_topic_name --alter --delete-config max.message.bytes
```

| Name | Type | Default | Valid values | Server default property | Description |
|---|---|---|---|---|---|
| `cleanup.policy` | list | `delete` | [compact, delete] | `log.cleanup.policy` | This config designates the retention policy to use on log segments. The "delete" policy (which is the default) will discard old segments when their retention time or size limit has been reached. The "compact" policy will enable log compaction, which retains the latest value for each key. It is also possible to specify both policies in a comma-separated list (e.g. "delete,compact"). |
| `compression.type` | string | `producer` | [uncompressed, zstd, lz4, snappy, gzip, producer] | `compression.type` | Specify the final compression type for a given topic. This configuration accepts the standard compression codecs ('gzip', 'snappy', 'lz4', 'zstd'). It additionally accepts 'uncompressed' which is equivalent to no compression; and 'producer' which means retain the original compression codec set by the producer. |
| `compression.gzip.level` / `compression.lz4.level` / `compression.zstd.level` | int | -1 / 9 / 3 | | | The compression level to use if compression.type is set to the given codec. |
| `delete.retention.ms` | long | 86400000 (1 day) | [0,...] | `log.cleaner.delete.retention.ms` | The amount of time to retain delete tombstone markers for log compacted topics. This setting also gives a bound on the time in which a consumer must complete a read if they begin from offset 0. |
| `file.delete.delay.ms` | long | 60000 (1 minute) | [0,...] | `log.segment.delete.delay.ms` | The time to wait before deleting a file from the filesystem. |
| `flush.messages` | long | 9223372036854775807 | [1,...] | `log.flush.interval.messages` | Interval at which we will force an fsync of data written to the log. |
| `flush.ms` | long | 9223372036854775807 | [0,...] | `log.flush.interval.ms` | Time interval at which we will force an fsync of data written to the log. |
| `index.interval.bytes` | int | 4096 (4 KiB) | [0,...] | `log.index.interval.bytes` | How frequently Kafka adds entries to its offset index and, conditionally, to its time index. |
| `local.retention.bytes` | long | -2 | [-2,...] | `log.local.retention.bytes` | The maximum size of local log segments that can grow for a partition before it deletes the old segments. Default value is -2, it represents `retention.bytes` value to be used. |
| `local.retention.ms` | long | -2 | [-2,...] | `log.local.retention.ms` | The number of milliseconds to keep the local log segment before it gets deleted. Default value is -2, it represents `retention.ms` value is to be used. |
| `max.compaction.lag.ms` | long | 9223372036854775807 | [1,...] | `log.cleaner.max.compaction.lag.ms` | The maximum time a message will remain ineligible for compaction in the log. Only applicable for logs that are being compacted. |
| `max.message.bytes` | int | 1048588 | [0,...] | `message.max.bytes` | The largest record batch size allowed by Kafka (after compression if compression is enabled). |
| `message.timestamp.after.max.ms` | long | 3600000 (1 hour) | [0,...] | `log.message.timestamp.after.max.ms` | Allowable timestamp difference between the message timestamp and the broker's timestamp. The message timestamp can be later than or equal to the broker's timestamp. |
| `message.timestamp.before.max.ms` | long | 9223372036854775807 | [0,...] | `log.message.timestamp.before.max.ms` | Allowable difference between the broker's timestamp and the message timestamp when the message timestamp is earlier. |
| `message.timestamp.type` | string | `CreateTime` | [CreateTime, LogAppendTime] | `log.message.timestamp.type` | Define whether the timestamp in the message is message create time or log append time. |
| `min.cleanable.dirty.ratio` | double | 0.5 | [0,...,1] | `log.cleaner.min.cleanable.ratio` | This configuration controls how frequently the log compactor will attempt to clean the log (assuming log compaction is enabled). By default we will avoid cleaning a log where more than 50% of the log has been compacted. |
| `min.compaction.lag.ms` | long | 0 | [0,...] | `log.cleaner.min.compaction.lag.ms` | The minimum time a message will remain uncompacted in the log. Only applicable for logs that are being compacted. |
| `min.insync.replicas` | int | 1 | [1,...] | `min.insync.replicas` | Specifies the minimum number of in-sync replicas (including the leader) required for a write to succeed when a producer sets `acks` to "all" (or "-1"). In the `acks=all` case, every in-sync replica must acknowledge a write for it to be considered successful. |
| `preallocate` | boolean | false | | `log.preallocate` | True if we should preallocate the file on disk when creating a new log segment. |
| `remote.log.copy.disable` | boolean | false | | null | Determines whether tiered data for a topic should become read only, and no more data uploading on a topic. Once this config is set to true, the local retention configuration becomes irrelevant. |
| `remote.log.delete.on.disable` | boolean | false | | null | Determines whether tiered data for a topic should be deleted after tiered storage is disabled on a topic. This configuration should be enabled when trying to set `remote.storage.enable` from true to false. |
| `remote.storage.enable` | boolean | false | | null | To enable tiered storage for a topic, set this configuration to true. To disable tiered storage for a topic that has it enabled, set this configuration to false. When disabling, you must also set `remote.log.delete.on.disable` to true. |
| `retention.bytes` | long | -1 | | `log.retention.bytes` | This configuration controls the maximum size a partition can grow to before we will discard old log segments to free up space if we are using the "delete" retention policy. By default there is no size limit only a time limit. |
| `retention.ms` | long | 604800000 (7 days) | [-1,...] | `log.retention.ms` | This configuration controls the maximum time we will retain a log before we will discard old log segments to free up space if we are using the "delete" retention policy. This represents an SLA on how soon consumers must read their data. If set to -1, no time limit is applied. |
| `segment.bytes` | int | 1073741824 (1 GiB) | [1048576,...] | `log.segment.bytes` | This configuration controls the segment file size for the log. Retention and cleaning is always done a file at a time so a larger segment size means fewer files but less granular control over retention. |
| `segment.index.bytes` | int | 10485760 (10 MiB) | [4,...] | `log.index.size.max.bytes` | Size of the index that maps offsets to file positions. |
| `segment.jitter.ms` | long | 0 | [0,...] | `log.roll.jitter.ms` | The maximum random jitter subtracted from the scheduled segment roll time to avoid thundering herds of segment rolling. |
| `segment.ms` | long | 604800000 (7 days) | [1,...] | `log.roll.ms` | This configuration controls the period of time after which Kafka will force the log to roll even if the segment file isn't full to ensure that retention can delete or compact old data. |
| `unclean.leader.election.enable` | boolean | false | | `unclean.leader.election.enable` | Indicates whether to enable replicas not in the ISR set to be elected as leader as a last resort, even though doing so may result in data loss. |

### Related broker-only configs (from `kafka_config.html`)

| Name | Default | Description |
|---|---|---|
| `log.retention.hours` | 168 | Hours to keep a log file before deleting it; tertiary to `log.retention.ms` (ms > minutes > hours) |
| `log.retention.check.interval.ms` | 300000 (5 minutes) | Frequency the log cleaner checks whether any log is eligible for deletion |
| `log.roll.hours` | 168 | Maximum time before a new log segment is rolled out, secondary to `log.roll.ms` |
| `message.max.bytes` | 1048588 | Largest record batch size allowed (after compression). Can be set per topic with `max.message.bytes` |
| `replica.fetch.max.bytes` | 1048576 | Bytes of messages to attempt to fetch for each partition (follower replication). Not an absolute maximum: the first record batch is returned even if larger |
| `compression.type` | producer | Final compression type for a topic ("producer" retains the codec set by the producer) |
| `log.message.timestamp.type` | CreateTime | CreateTime or LogAppendTime |
| `num.partitions` / `default.replication.factor` | 1 / 1 | Defaults for auto-created topics |
