# Apache Kafka 4.3 — Broker Configs: threads, socket, storage, log & retention

> **Nguồn (official):** https://kafka.apache.org/43/generated/kafka_config.html (bản có mục lục: https://kafka.apache.org/43/configuration/broker-configs/)
> **Tuần:** 2 — Cluster Config I: broker config, storage & `log.dirs`, retention, compaction · **Loại:** Apache Kafka Docs (config reference)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn — chỉ giữ các config hay bị hỏi trong CCAAK) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Nhóm thread:** `num.network.threads` **3** · `num.io.threads` **8** · `num.replica.fetchers` **1** · `background.threads` **10** · `num.recovery.threads.per.data.dir` **2** (đổi từ 1 ở Kafka 4.0). **Cả 5 đều là `cluster-wide`** → sửa được lúc chạy bằng `kafka-configs.sh`, **không cần restart**. Đây là lý do đáp án "restart cả cluster để tăng `num.io.threads`" luôn sai.
- **Nhóm socket lại ngược:** `queued.max.requests` **500**, `socket.send.buffer.bytes` / `socket.receive.buffer.bytes` **102400** (100 KiB), `socket.request.max.bytes` **104857600** (100 MiB) đều là **`read-only`** → **phải restart broker**. Nhớ cặp đối lập này: *thread đổi nóng, socket đổi nguội*.
- **`log.dirs` là `read-only`** (default `null`; khi null thì rơi về `log.dir` = `/tmp/kafka-logs`). Thêm ổ đĩa vào JBOD **bắt buộc restart broker** — không có đường tắt dynamic.
- **Segment:** `log.segment.bytes` **1073741824** (1 GiB, cluster-wide) · `log.roll.hours` **168** (7 ngày, **read-only**) · `log.roll.ms` `null` (cluster-wide, thắng `log.roll.hours` khi được đặt) · `log.index.interval.bytes` **4096** · `log.index.size.max.bytes` **10485760** (10 MiB).
- **Retention:** `log.retention.hours` **168** (read-only) · `log.retention.minutes` `null` (read-only) · `log.retention.ms` `null` (**cluster-wide** — đây là cái sửa nóng được) · `log.retention.bytes` **-1** (không giới hạn, tính **per partition**) · `log.retention.check.interval.ms` **300000** (5 phút, read-only).
- **Compaction:** `log.cleanup.policy` **delete** · `log.cleaner.threads` **1** · `log.cleaner.min.cleanable.ratio` **0.5** · `log.cleaner.delete.retention.ms` **86400000** (24 h) · `log.cleaner.min.compaction.lag.ms` **0** · `log.cleaner.max.compaction.lag.ms` **Long.MAX** · `log.cleaner.backoff.ms` **15000** · `log.cleaner.dedupe.buffer.size` **134217728** (128 MiB) · `log.cleaner.io.buffer.size` **524288**. `log.cleaner.enable` **true** và **đã deprecated, sẽ gỡ ở Kafka 5.0** — đừng đặt `false`.
- **Kích cỡ message:** `message.max.bytes` **1048588** (KHÔNG phải tròn 1 MiB) — dễ nhầm với producer `max.request.size` **1048576**. Topic override là `max.message.bytes`, cùng mặc định 1048588.
- **Xoá file thật:** `log.segment.delete.delay.ms` **60000** (1 phút) — segment bị đổi tên `.deleted` rồi mới xoá sau ngần này. Ở tầng topic tên của nó là **`file.delete.delay.ms`** (đây là cặp tên khác nhau giữa 2 tầng, rất hay bị hỏi).
- **Tiered storage ở góc broker:** `log.local.retention.ms` **-2** và `log.local.retention.bytes` **-2** (`-2` = "dùng luôn giá trị retention tổng"). Bật toàn cluster bằng `remote.log.storage.system.enable`.
- **Vận hành khác:** `auto.create.topics.enable` **true** (read-only — production nên tắt) · `delete.topic.enable` **true** (read-only) · `num.partitions` **1** (read-only) · `compression.type` **producer** (cluster-wide) · `controlled.shutdown.enable` **true** (read-only) · `cordoned.log.dirs` **""** (per-broker, KIP-1066).
- **Fsync mặc định tắt:** `log.flush.interval.messages` **Long.MAX**, `log.flush.interval.ms` `null` → độ bền đến từ **replication + page cache**, không từ fsync.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Update Mode — ba giá trị và ý nghĩa

| Update Mode | Ý nghĩa (theo docs) |
|---|---|
| `read-only` | "Cannot be changed after broker startup" — đổi trong file properties rồi **restart**. |
| `per-broker` | "Can be changed per individual broker without cluster restart" — `--entity-type brokers --entity-name <id>`. |
| `cluster-wide` | "Changes apply across the entire cluster dynamically" — `--entity-type brokers --entity-default`; vẫn có thể đặt per-broker để thử nghiệm. |

### Threads

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `num.network.threads` | 3 | cluster-wide | "Number of threads that the server uses for receiving requests from the network and sending responses" |
| `num.io.threads` | 8 | cluster-wide | "Number of threads that the server uses for processing requests, which may include disk I/O" |
| `num.replica.fetchers` | 1 | cluster-wide | "Fetcher threads used to replicate records from each source broker" |
| `background.threads` | 10 | cluster-wide | "Number of threads to use for various background processing tasks" |
| `num.recovery.threads.per.data.dir` | 2 | cluster-wide | "The number of threads per data directory to be used for log recovery at startup and flushing at shutdown" (int, valid values `[1,...]`, importance high) |

### Socket & request queue

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `queued.max.requests` | 500 | read-only | "Number of queued requests allowed for data-plane, before blocking network threads" |
| `socket.send.buffer.bytes` | 102400 | read-only | "The SO_SNDBUF buffer of the socket server sockets" |
| `socket.receive.buffer.bytes` | 102400 | read-only | "The SO_RCVBUF buffer of the socket server sockets" |
| `socket.request.max.bytes` | 104857600 | read-only | "Maximum number of bytes in a socket request" |

### Storage / log directories

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `log.dirs` | null | read-only | "Comma-separated list of directories where log data is stored" |
| `log.dir` | /tmp/kafka-logs | read-only | "Comma-separated list of directories where log data is stored (supplemental)" — chỉ dùng khi `log.dirs` không được đặt |
| `cordoned.log.dirs` | "" (list) | per-broker | KIP-1066 — log dir bị cordon vẫn phục vụ partition cũ nhưng **không nhận partition mới**; `*` để cordon cả broker |
| `num.recovery.threads.per.data.dir` | 2 | cluster-wide | xem bảng thread |

### Segment & index

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `log.segment.bytes` | 1073741824 | cluster-wide | "Maximum size of a single log file" |
| `log.roll.hours` | 168 | read-only | "Maximum time before a new log segment is rolled out (in hours)" |
| `log.roll.ms` | null | cluster-wide | "Maximum time before a new log segment is rolled out (in milliseconds)" |
| `log.index.interval.bytes` | 4096 | cluster-wide | "Interval with which an entry is added to the offset index" |
| `log.index.size.max.bytes` | 10485760 | cluster-wide | "Maximum size in bytes of the offset index" |
| `log.segment.delete.delay.ms` | 60000 | cluster-wide | "The amount of time to wait before deleting a file from the filesystem. If the value is 0 and there is no file to delete, the system will wait 1 millisecond." |
| `preallocate` (topic) / `log.preallocate` | false | cluster-wide | Preallocate file space khi tạo segment mới |

### Retention (policy `delete`)

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `log.retention.hours` | 168 | read-only | "Number of hours to keep a log file before deleting it" |
| `log.retention.minutes` | null | read-only | "Number of minutes to keep a log file before deleting it (secondary to ms)" |
| `log.retention.ms` | null | cluster-wide | "Number of milliseconds to keep a log file before deleting it" |
| `log.retention.bytes` | -1 | cluster-wide | "Maximum size of the log before deleting it" |
| `log.retention.check.interval.ms` | 300000 | read-only | "Frequency in milliseconds that the log cleaner checks for deletion eligibility" |

> 📌 Thứ tự ưu tiên trong nhóm retention thời gian: `log.retention.ms` > `log.retention.minutes` > `log.retention.hours`. Đặt `log.retention.ms=-1` = giữ vĩnh viễn.

### Compaction (log cleaner)

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `log.cleanup.policy` | delete | cluster-wide | "Retention policy: 'delete', 'compact', or both; empty list means infinite retention" |
| `log.cleaner.threads` | 1 | cluster-wide | "Number of background threads to use for log cleaning" |
| `log.cleaner.min.cleanable.ratio` | 0.5 | cluster-wide | "Minimum dirty log ratio for a log to be eligible for cleaning" |
| `log.cleaner.delete.retention.ms` | 86400000 | cluster-wide | "Time to retain tombstone markers for log compacted topics" |
| `log.cleaner.min.compaction.lag.ms` | 0 | cluster-wide | "Minimum time a message remains uncompacted in the log" |
| `log.cleaner.max.compaction.lag.ms` | 9223372036854775807 | cluster-wide | "Maximum time a message remains ineligible for compaction" |
| `log.cleaner.backoff.ms` | 15000 | cluster-wide | "Sleep duration when there are no logs to clean" |
| `log.cleaner.dedupe.buffer.size` | 134217728 | cluster-wide | "Total memory used for log deduplication across all cleaner threads" |
| `log.cleaner.io.buffer.size` | 524288 | cluster-wide | "Total memory used for log cleaner I/O buffers across all threads" |
| `log.cleaner.io.max.bytes.per.second` | 1.7976931348623157E308 | cluster-wide | "Log cleaner is throttled so read and write I/O is less than this value" |
| `log.cleaner.enable` | true | read-only | "This configuration has been deprecated and will be removed in Kafka 5.0. Users should not set it to false to prepare for its future removal." |

### Message size & replication fetch

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `message.max.bytes` | 1048588 | cluster-wide | "Largest record batch size allowed by Kafka after compression" |
| `replica.fetch.max.bytes` | 1048576 | read-only | Kích cỡ tối đa mỗi partition trong một fetch của follower — **không phải trần tuyệt đối**: batch đầu vẫn được trả để replication không kẹt |
| `compression.type` | producer | cluster-wide | "Final compression type for a topic (gzip, snappy, lz4, zstd, uncompressed, producer)" |

### Flush (fsync) — mặc định là "để OS lo"

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `log.flush.interval.messages` | 9223372036854775807 | cluster-wide | "Number of messages accumulated before flushing to disk" |
| `log.flush.interval.ms` | null | cluster-wide | "Maximum time in ms before messages are flushed to disk" |

### Tiered storage (góc broker)

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `log.local.retention.ms` | -2 | cluster-wide | "Milliseconds to keep local log segments before deletion eligibility" (`-2` = dùng giá trị `log.retention.ms`) |
| `log.local.retention.bytes` | -2 | cluster-wide | "Maximum size of local log segments before deletion eligibility" (`-2` = dùng `log.retention.bytes`) |
| `remote.log.storage.system.enable` | false | read-only | Bật tiered storage ở mức cluster (xem [kafka-tiered-storage.md](kafka-tiered-storage.md)) |

### Topic lifecycle & khác

| Config | Default | Update Mode | Description |
|---|---|---|---|
| `auto.create.topics.enable` | true | read-only | "Enable auto creation of topic on the server" |
| `delete.topic.enable` | true | read-only | "When true, topics can be deleted by the admin client" |
| `num.partitions` | 1 | read-only | "Default number of log partitions per topic at creation" |
| `controlled.shutdown.enable` | true | read-only | "Enable controlled shutdown of the server." |

> ⚠️ **Một điểm lệch giữa hai nguồn:** trang Confluent *Kafka Broker and Controller Configuration Reference* ghi `auto.create.topics.enable` và `socket.send.buffer.bytes` là `cluster-wide`, trong khi trang generated của Apache Kafka 4.3 ghi `read-only`. Bản neo của bộ tài liệu này là **Apache Kafka 4.3** → theo Apache. Nếu đề hỏi thẳng, ưu tiên trả lời theo cơ chế: muốn chắc thì đổi trong `server.properties` + rolling restart.
