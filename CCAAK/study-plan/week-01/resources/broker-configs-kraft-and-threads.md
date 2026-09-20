# Apache Kafka — Broker Configs: nhóm `KRaft`, nhóm thread/socket, nhóm durability (bảng số gốc)

> **Nguồn (official):** https://kafka.apache.org/43/generated/kafka_config.html · https://kafka.apache.org/43/configuration/broker-configs/
> **Tuần:** 1 — Nền tảng vận hành + `KRaft` in production · **Loại:** Apache Kafka Docs (generated config reference)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Đây là bảng số gốc của cả bộ CCAAK.** Mọi con số trong `CCAAK-STUDY-PLAN.md` §6 đều tra được ở trang này. Đối chiếu lại ngày **2026-09-20** với Kafka **4.3**.
- Nhóm KRaft: `process.roles` (list, mặc định **rỗng**), `node.id` (int, **bắt buộc**, `[0,...]`), `controller.quorum.voters` (list, mặc định `""`), `controller.quorum.bootstrap.servers` (list, mặc định `""`), `controller.listener.names` (list, **bắt buộc với controller**).
- **Đồng hồ của quorum** — nhỏ hơn nhiều so với đồng hồ của data plane: `controller.quorum.fetch.timeout.ms` **2000**, `controller.quorum.election.timeout.ms` **1000**, `controller.quorum.election.backoff.max.ms` **1000**, `controller.quorum.request.timeout.ms` **2000**, `controller.quorum.append.linger.ms` **25**. So sánh: `replica.lag.time.max.ms` của data plane là **30000**. Quorum phát hiện leader chết trong **2 giây**, ISR phát hiện follower tụt trong **30 giây**.
- `controller.quorum.fetch.timeout.ms` có **hai vế** và cả hai đều đáng nhớ: voter không fetch được từ leader trong 2 s thì **tự ứng cử**; *và* leader không nhận được fetch từ **đa số** quorum trong 2 s thì **tự từ chức**. Vế thứ hai là cơ chế chống split-brain — một controller bị cô lập sẽ tự bỏ vai trò leader thay vì tiếp tục ghi metadata.
- Metadata log: `metadata.log.dir` mặc định **`null`** → dùng thư mục **đầu tiên** trong `log.dirs`. Production nên trỏ sang **ổ đĩa riêng** để metadata không tranh I/O với data. `metadata.log.segment.bytes` **1 GiB**, `metadata.max.retention.bytes` **100 MiB**, `metadata.max.retention.ms` **7 ngày**, `metadata.log.max.record.bytes.between.snapshots` **20971520** (20 MiB → cứ 20 MiB record thì chụp snapshot).
- Nhóm thread (đề CCAAK hỏi rất nhiều, Tuần 3 khai thác sâu): `num.network.threads` **3**, `num.io.threads` **8**, `num.replica.fetchers` **1**, `background.threads` **10**, `num.recovery.threads.per.data.dir` **2** (**đổi từ 1 ở Kafka 4.0**).
- Nhóm socket: `socket.send.buffer.bytes` = `socket.receive.buffer.bytes` = **102400** (100 KiB), `socket.request.max.bytes` **104857600** (100 MiB), `queued.max.requests` **500**.
- Nhóm durability: `min.insync.replicas` **1**, `default.replication.factor` **1**, `num.partitions` **1** — **cả ba đều là số "dev"**, production phải nâng lên 2/3/nhiều-hơn. `unclean.leader.election.enable` **false**, `replica.lag.time.max.ms` **30000**.
- Internal topic: `offsets.topic.num.partitions` **50**, `offsets.topic.replication.factor` **3**, `transaction.state.log.replication.factor` **3**, `transaction.state.log.min.isr` **2**. Cluster 1 broker **không tạo được** `__consumer_offsets` nếu không hạ RF xuống 1 — đây là lỗi kinh điển khi dựng lab.
- Bảo trì: `controlled.shutdown.enable` **true**, `auto.leader.rebalance.enable` **true**, `leader.imbalance.check.interval.seconds` **300** (5 phút) — nghĩa là sau một rolling restart, leader **tự** quay về preferred replica trong vòng 5 phút, không cần chạy tay `kafka-leader-election.sh`.
- `broker.rack` mặc định **`null`**; `inter.broker.listener.name` mặc định **`null`**; `log.dirs` mặc định **`null`** (khi null thì dùng `log.dir`, mặc định `/tmp/kafka-logs`).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### KRaft / controller quorum

| Config Name | Type | Default | Valid Values |
|---|---|---|---|
| `process.roles` | list | (empty) | `[broker, controller]` |
| `node.id` | int | (required) | `[0,...]` |
| `controller.quorum.voters` | list | `""` | non-empty list |
| `controller.quorum.bootstrap.servers` | list | `""` | non-empty list |
| `controller.listener.names` | list | (empty) | — |
| `controller.quorum.election.timeout.ms` | int | `1000` (1 second) | `[0,...]` |
| `controller.quorum.fetch.timeout.ms` | int | `2000` (2 seconds) | `[0,...]` |

> Exact descriptions from the generated reference:
> - `controller.quorum.election.timeout.ms` — "Maximum time in milliseconds to wait without being able to fetch from the leader before triggering a new election"
> - `controller.quorum.fetch.timeout.ms` — "Maximum time without a successful fetch from the current leader before becoming a candidate and triggering an election for voters; Maximum time a leader can go without receiving valid fetch or fetchSnapshot request from a majority of the quorum before resigning."
> - `controller.quorum.election.backoff.max.ms` — "Maximum time in milliseconds before starting new elections. This is used in the binary exponential backoff mechanism that helps prevent gridlocked elections"
> - `controller.quorum.append.linger.ms` — "The duration in milliseconds that the leader will wait for writes to accumulate before flushing them to disk."

| `controller.quorum.election.backoff.max.ms` | int | `1000` (1 second) | `[0,...]` |
| `controller.quorum.request.timeout.ms` | int | `2000` (2 seconds) | `[0,...]` |
| `controller.quorum.append.linger.ms` | int | `25` | `[0,...]` |

### Metadata log

| Config Name | Type | Default | Valid Values |
|---|---|---|---|
| `metadata.log.dir` | string | `null` | — |
| `metadata.log.segment.bytes` | int | `1073741824` (1 gibibyte) | `[8388608,...]` |
| `metadata.log.max.record.bytes.between.snapshots` | long | `20971520` | `[1,...]` |
| `metadata.max.retention.bytes` | long | `104857600` (100 mebibytes) | — |
| `metadata.max.retention.ms` | long | `604800000` (7 days) | — |

> `metadata.log.dir`: "This configuration determines where we put the metadata log. If it is not set, the metadata log is placed in the first log directory from `log.dirs`."

### Threads and sockets

| Config Name | Type | Default | Valid Values |
|---|---|---|---|
| `num.network.threads` | int | `3` | `[1,...]` |
| `num.io.threads` | int | `8` | `[1,...]` |
| `num.replica.fetchers` | int | `1` | `[1,...]` |
| `background.threads` | int | `10` | `[1,...]` |
| `queued.max.requests` | int | `500` | `[1,...]` |
| `num.recovery.threads.per.data.dir` | int | `2` | `[1,...]` |
| `socket.send.buffer.bytes` | int | `102400` (100 kibibytes) | — |
| `socket.receive.buffer.bytes` | int | `102400` (100 kibibytes) | — |
| `socket.request.max.bytes` | int | `104857600` (100 mebibytes) | `[1,...]` |

### Durability, leadership and internal topics

| Config Name | Type | Default | Valid Values |
|---|---|---|---|
| `min.insync.replicas` | int | `1` | `[1,...]` |
| `default.replication.factor` | int | `1` | — |
| `num.partitions` | int | `1` | `[1,...]` |
| `unclean.leader.election.enable` | boolean | `false` | — |
| `replica.lag.time.max.ms` | long | `30000` (30 seconds) | — |
| `controlled.shutdown.enable` | boolean | `true` | — |
| `auto.leader.rebalance.enable` | boolean | `true` | — |
| `leader.imbalance.check.interval.seconds` | long | `300` | `[1,...]` |
| `offsets.topic.num.partitions` | int | `50` | `[1,...]` |
| `offsets.topic.replication.factor` | short | `3` | `[1,...]` |
| `transaction.state.log.replication.factor` | short | `3` | `[1,...]` |
| `transaction.state.log.min.isr` | int | `2` | `[1,...]` |

### Storage and listeners

| Config Name | Type | Default | Valid Values |
|---|---|---|---|
| `log.dirs` | list | `null` | — |
| `inter.broker.listener.name` | string | `null` | — |
| `broker.rack` | string | `null` | — |

> **Ghi chú kiểm chứng:** `metadata.max.idle.interval.ms` không xuất hiện trong trang generated config đã crawl ngày 2026-09-20. Nếu gặp tên này trong tài liệu ôn khác, hãy tra lại trước khi tin.
