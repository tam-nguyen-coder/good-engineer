# Apache Kafka 4.0 → 4.3 — Thay đổi ảnh hưởng NGƯỜI VẬN HÀNH

> **Nguồn (official):** https://kafka.apache.org/43/getting-started/upgrade/
> **Tuần:** 8 — Tuần chốt · **Loại:** Apache Kafka Official (Upgrade / Notable changes)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch ngày 2026-09-20) và **đã lọc theo góc nhìn admin** — bỏ phần thuần client/Streams API. Đối chiếu link gốc khi có bản 4.4+.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Kafka 4.0 chỉ chạy KRaft.** Nguyên văn: *"Apache Kafka 4.0 only supports KRaft mode - ZooKeeper mode has been removed."* Cluster còn ZooKeeper **phải migrate sang KRaft trước**, không nhảy thẳng lên 4.x được. Đây là nguồn gốc của **nhóm bẫy version** chiếm nhiều câu sai nhất trong CCAAK.
- **Java tối thiểu:** broker / Connect / tools **Java 17+**; clients và Kafka Streams **Java 11+**. Nâng Kafka lên 4.x mà JVM còn 11 trên broker là broker **không khởi động được**.
- **Trình tự rolling upgrade (4.0+), 3 bước:** (1) nâng **từng broker một** — shutdown, thay binary, khởi động lại; (2) xác nhận cluster chạy đúng và ổn định; (3) **finalize** bằng `bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3`. **Bước 3 là điểm hay bị hỏi**: chưa chạy thì cluster vẫn ở `metadata.version` cũ và tính năng mới chưa bật.
- **Downgrade không phải lúc nào cũng được:** **4.3.0, 4.1.0, 4.0.1 KHÔNG hỗ trợ downgrade** (có thay đổi metadata); **4.2.0 hỗ trợ** (không có thay đổi metadata). Suy ra quy tắc vận hành: finalize `metadata.version` là **hành động một chiều** — làm sau khi đã chạy ổn vài ngày, không làm ngay trong cửa sổ bảo trì.
- **Mặc định đã đổi (nhóm admin phải thuộc):** `num.recovery.threads.per.data.dir` **1 → 2**; `message.timestamp.after.max.ms` **Long.MAX → 1 giờ**; `segment.bytes` / `log.segment.bytes` **giá trị nhỏ nhất cho phép 14 byte → 1 MiB**; `remote.log.manager.thread.pool.size` **10 → 2**; `remote.log.manager.copier/expiration.thread.pool.size` **-1 → 10** (không còn nhận -1); phía client `linger.ms` **0 → 5**.
- **4.3: `controller.quorum.auto.join.enable` mặc định `false`.** Controller mới **không** tự join quorum — phải thêm voter tường minh. Đừng giả định "bật máy lên là vào quorum".
- **ELR (KIP-966) bật mặc định trên cluster mới từ 4.1.** Khi ELR bật, `min.insync.replicas` **ở mức broker bị gỡ bỏ**; muốn đặt thì đặt ở **mức cluster** (hoặc topic). Đây là thay đổi vận hành thật sự: script cũ `--entity-type brokers --add-config min.insync.replicas` không còn là nơi đúng.
- **Công cụ đã bị xoá ở 4.0:** **MirrorMaker 1** và toàn bộ class liên quan; `kafka.admin.ZkSecurityMigrator`; các tuỳ chọn CLI `--whitelist`, `--topic-white-list`, `--authorizer`, `--zk-tls-config-file`, **`--broker-list`**. Thấy phương án nào dùng chúng → sai.
- **Logging chuyển sang Log4j2 từ 4.0** (`log4j2.yaml`); có `log4j-transform-cli` để chuyển config cũ; `KafkaLog4jAppender` bị xoá, thay bằng `KafkaAppender` của Log4j2. Câu hỏi "bật DEBUG cho `kafka.controller` thế nào" phải trả lời theo log4j2, không phải `log4j.properties`.
- **Share groups (KIP-932):** 4.1 Early Access → **4.2 production-ready**. Internal topic `__share_group_state` mặc định **RF 3**; cluster **dưới 3 broker phải hạ** `share.coordinator.state.topic.replication.factor` và `.min.isr` xuống **1** trước khi dùng — đúng kiểu bẫy lab 1 broker.
- **4.3 có cordoning log dir (KIP-1066)** — chặn controller đặt partition mới lên một `log.dirs` sắp bị bỏ. Đây là công cụ đúng khi decommission một ổ đĩa mà không muốn dừng broker.
- **Config bị deprecate theo mốc:** `log.cleaner.enable` (4.1 — không nên đặt `false`); `org.apache.kafka.disallowed.login.modules` và `remote.log.manager.thread.pool.size` (4.2); `group.coordinator.rebalance.protocols` (4.3, dự kiến xoá ở 5.0).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### ZooKeeper removal

*"Apache Kafka 4.0 only supports KRaft mode - ZooKeeper mode has been removed."* Clusters still running in ZooKeeper mode must complete the **ZooKeeper-to-KRaft migration** before upgrading to 4.0 or later.

### Java version requirements

| Component | Minimum Java |
| --- | --- |
| Clients, Kafka Streams | **11+** (raised from 8) |
| Brokers, Connect, tools | **17+** (new requirement) |

Java 23 support was added in 4.0.

### Rolling upgrade procedure (4.0+)

1. Upgrade the brokers **one at a time**: shut the broker down, update the code, and restart it.
2. Verify cluster behaviour and performance once the whole cluster runs the new binaries.
3. Finalize the upgrade:

   ```bash
   bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3
   ```

### Metadata downgrade support

| Release | Downgrade supported? | Reason |
| --- | --- | --- |
| **4.0.1** | No | metadata changes present |
| **4.1.0** | No | metadata changes present |
| **4.2.0** | **Yes** | no metadata changes |
| **4.3.0** | No | metadata changes present |

`MetadataVersion` flags indicate whether a version contains metadata changes, which determines downgrade feasibility.

### Removed tools, classes and CLI options (4.0)

- **MirrorMaker 1 (MM1)** and all related classes.
- `kafka.common.MessageReader`.
- Formatter classes: `DefaultMessageFormatter`, `LoggingMessageFormatter`, `NoOpMessageFormatter`.
- `kafka.admin.ZkSecurityMigrator`.
- Command-line options: `--whitelist`, `--topic-white-list`, `--authorizer`, `--zk-tls-config-file`, `--broker-list`.

### Changed defaults

| Config | Old | New |
| --- | --- | --- |
| `num.recovery.threads.per.data.dir` | 1 | **2** |
| `message.timestamp.after.max.ms` | `Long.MAX_VALUE` | **1 hour** |
| `remote.log.manager.copier.thread.pool.size` | -1 | **10** (−1 no longer accepted) |
| `remote.log.manager.expiration.thread.pool.size` | -1 | **10** |
| `remote.log.manager.thread.pool.size` | 10 | **2** (deprecated in 4.2) |
| `segment.bytes` / `log.segment.bytes` **minimum** | 14 bytes | **1 MiB** |
| `linger.ms` (producer, client-side) | 0 | **5** |
| `controller.quorum.auto.join.enable` (**4.3**) | — | **`false`** |
| `group.coordinator.background.threads` (**4.3**) | 1 | **2** |

### Deprecated configs by release

- **4.1:** `log.cleaner.enable` — users should not set it to `false`.
- **4.2:** `org.apache.kafka.disallowed.login.modules`; `remote.log.manager.thread.pool.size`.
- **4.3:** `group.coordinator.rebalance.protocols` (removal planned for 5.0).

### Eligible Leader Replicas (ELR, KIP-966 part 1)

Enabled **by default on new clusters from 4.1**. When ELR is enabled, a previously set **broker-level** `min.insync.replicas` is **removed**; administrators must set the **cluster-level** value if one is required.

### Share groups — Queues for Kafka (KIP-932)

- **4.1:** preview / Early Access, disabled by default.
- **4.2:** production-ready.

Share groups use the internal topic `__share_group_state`, created with **3 replicas** by default. Clusters with fewer than 3 brokers must set `share.coordinator.state.topic.replication.factor` and `share.coordinator.state.topic.min.isr` to **1** before enabling the feature.

### Streams rebalance protocol (KIP-1071)

- **4.1:** Early Access, disabled by default.
- **4.2+:** production-ready for the core feature set.
- **4.2.1 note:** a broker-side migration bug (KAFKA-20254) affected 4.2.0; `classic` → `streams` group migrations are safe from **4.2.1** onward.

### Logging: Log4j → Log4j2 (4.0)

The logging framework moved from Log4j to **Log4j2**. Kafka ships the **`log4j-transform-cli`** tool to convert existing configurations. **`KafkaLog4jAppender` was removed**; use Log4j2's `KafkaAppender` instead.

### Scala support (4.0 / 4.3)

Scala 2.12 support was removed per **KIP-751**. The `kafka-streams-scala` library is **deprecated in 4.3**, with removal planned for 5.0.

### New configurations in 4.3

- `group.coordinator.cached.buffer.max.bytes`, `share.coordinator.cached.buffer.max.bytes`.
- `remote.log.metadata.topic.min.isr` (default **2**).
- `remote.log.metadata.admin.*` prefix — independent admin-client configuration for the remote-log metadata manager.
- `follower.fetch.last.tiered.offset.enable` — tiered-storage bootstrap optimisation for followers.
- `group.coordinator.background.threads` (default **2**, previously 1).
- Assignment interval configs with 1-second defaults, e.g. `group.consumer.assignment.interval.ms`.

### Log directory cordoning (4.3, KIP-1066)

Kafka 4.3 supports **cordoning log directories**, so the controller stops placing new partitions on a directory that is being retired.

### ListOffsets API (4.3, KIP-1023)

`ListOffsets` is extended to **version 11**, adding the `EARLIEST_PENDING_UPLOAD_TIMESTAMP` (**-6**) timestamp type for tiered-storage queries.
