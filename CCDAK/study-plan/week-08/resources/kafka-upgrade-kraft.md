# Apache Kafka — Upgrading (Rolling Upgrade KRaft, `kafka-features.sh`, Notable Changes 4.x)

> **Nguồn (official):** https://kafka.apache.org/43/getting-started/upgrade/ (mục 1.5 Upgrading)
> **Tuần:** 8 — Observability & Operations · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua HTTP + chuyển HTML → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kafka **4.x chỉ hỗ trợ KRaft**; nâng cấp lên 4.x yêu cầu cluster đã ở KRaft với **software + metadata version ≥ 3.3.x**; cluster ZooKeeper phải **migrate sang KRaft** (khuyến nghị qua 3.9.x) trước.
- **Rolling upgrade** = nâng **từng broker một** (tắt → thay code → khởi động lại), đợi cluster ổn định (URP = 0), rồi **finalize** bằng `bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3` (hoặc `--metadata 4.3` / `--feature metadata.version=X`). Xem trạng thái: `kafka-features.sh describe`.
- **`metadata.version`** thay vai trò `inter.broker.protocol.version` cũ; **downgrade chỉ khả thi nếu không có metadata change** giữa 2 version (4.3 = `IBP_4_3_IV0(30, "4.3", "IV0", true)` → **không** downgrade được; 4.2 `IBP_4_2_IV1(29, ..., false)` → được).
- Sau khi finalize 4.0+: **KIP-848** consumer protocol tự bật (cluster chỉ downgrade được về ≥ 3.4.1 nếu group đã dùng protocol mới); **KIP-890** transaction server-side defense bật (producer epoch bump mỗi transaction); **ELR** (KIP-966) theo dõi trong metadata.
- Kafka 4.0 notable: xoá **ZooKeeper**, xoá protocol API cũ (client ≥ 2.1 mới nói chuyện được), xoá **MirrorMaker 1**, config KRaft chuyển hết vào `config/`, `metric.reporters` mặc định `JmxReporter`, xoá `log.message.format.version`, `NotLeaderForPartitionException` → **`NotLeaderOrFollowerException`**, `--bootstrap-server` chỉ nhận dạng **phân cách bằng dấu phẩy**, remote log thread pool defaults đổi (KIP-1030), `segment.bytes` tối thiểu **1 MB**.
- Kafka 4.1: **`log.cleaner.enable` deprecated**; ELR bật mặc định trên cluster mới (min.isr cấp broker bị bỏ → set cấp cluster); logger LogCleaner đổi sang `org.apache.kafka.storage.internals.log.LogCleaner` (log4j2.yaml); file rotate `state-change.log.[date]`; share groups **preview** (`share.version=1`); Streams rebalance protocol **early access**.
- Kafka 4.2: **Queues for Kafka (KIP-932) GA** (`__share_group_state`, cluster < 3 broker phải set RF/min.isr = 1); **Streams Rebalance Protocol (KIP-1071) GA** (migration classic→streams chỉ an toàn từ 4.2.1); `RecordHeader` read thread-safe.
- Kafka 4.3: `group.coordinator.rebalance.protocols` deprecated (5.0 điều khiển hoàn toàn bằng `group.version`/`streams.version`/`share.version` qua `kafka-features.sh`); `kafka-streams-scala` deprecated; **cordoning log dirs** (KIP-1066) cho decommission; `--delete-config` không còn lỗi khi key không tồn tại (quản lý broker offline qua `--bootstrap-controller`); `remote.log.metadata.topic.min.isr` mặc định 2; `follower.fetch.last.tiered.offset.enable`; `group.*.assignment.interval.ms` mặc định 1 s.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Upgrading to 4.3.0

#### Upgrading Servers to 4.3.0 from any version 3.3.x through 4.2.0

Note: Apache Kafka 4.3 only supports KRaft mode - ZooKeeper mode has been removed. As such, **broker upgrades to 4.3.0 (and higher) require KRaft mode and the software and metadata versions must be at least 3.3.x** (the first version when KRaft mode was deemed production ready). For clusters in KRaft mode with versions older than 3.3.x, we recommend upgrading to 3.9.x before upgrading to 4.3.x. Clusters in ZooKeeper mode have to be migrated to KRaft mode before they can be upgraded to 4.3.x.

**For a rolling upgrade:**

- Upgrade the brokers one at a time: shut down the broker, update the code, and restart it. Once you have done so, the brokers will be running the latest version and you can verify that the cluster's behavior and performance meet expectations.
- Once the cluster's behavior and performance have been verified, finalize the upgrade by running `bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3`
- Note that cluster metadata downgrade is not supported in this version since it has metadata changes. Every MetadataVersion has a boolean parameter that indicates if there are metadata changes (i.e. `IBP_4_3_IV0(30, "4.3", "IV0", true)` means this version has metadata changes). Given your current and target versions, a downgrade is only possible if there are no metadata changes in the versions between.

#### Notable changes in 4.3.0

- `kafka-configs.sh --alter --delete-config` no longer requires the specified config keys to exist on the target resource. Previously, attempting to delete a non-existent config key raised an `InvalidConfigurationException`. The deletion is now a no-op when the key does not exist, which allows managing configs for offline brokers via `--bootstrap-controller`.
- Support dynamically changing configs for dynamic quorum controllers. Previously only brokers and static quorum controllers were supported.
- The new config `remote.log.metadata.topic.min.isr` with 2 as default value has been introduced (KIP-1235). The new config prefix `remote.log.metadata.admin.` allows independent configuration of the admin client used by `TopicBasedRemoteLogMetadataManager` (KIP-1208).
- The `kafka-streams-scala` library is deprecated as of Kafka 4.3 and will be removed in Kafka 5.0.
- Kafka Streams now supports opt-in headers-aware state stores for DSL operators via the new `dsl.store.format` config (KIP-1285).
- Support for cordoning log directories (KIP-1066).
- The `group.coordinator.rebalance.protocols` configuration is deprecated and will be removed in Kafka 5.0. In Kafka 5.0, all protocols will always be enabled and controlled solely by feature versions (`group.version`, `streams.version`, `share.version`) via `kafka-features.sh` (KIP-1237).
- New group configs: `share.delivery.count.limit`, `share.partition.max.record.locks` and `share.renew.acknowledge.enable` (KIP-1240).
- New `group.consumer.assignment.interval.ms`, `group.share.assignment.interval.ms` and `group.streams.assignment.interval.ms` configs default to an interval of 1 second and previously had an effective value of 0 (KIP-1263).
- A new dynamic broker configuration `follower.fetch.last.tiered.offset.enable` (default: `false`) has been added. When enabled on a cluster with tiered storage, a newly added follower replica that has no local data will skip directly to the earliest pending upload offset on the leader (KIP-1023). The `ListOffsets` API has been extended to version 11, adding support for the `EARLIEST_PENDING_UPLOAD_TIMESTAMP` (-6) timestamp type.

### Upgrading to 4.2.0

- For a rolling upgrade: upgrade the brokers one at a time; then finalize by running `bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.2`.
- Note that cluster metadata downgrade is supported in this version since it has no metadata changes (`IBP_4_2_IV1(29, "4.2", "IV1", false)`).
- If you wish to use share groups in a cluster with fewer than 3 brokers, you must set the broker configurations `share.coordinator.state.topic.replication.factor` and `share.coordinator.state.topic.min.isr` to 1 before you start using share groups, because share groups make use of a new internal topic called `__share_group_state`.

#### Notable changes in 4.2.0

- Queues for Kafka (KIP-932) is production-ready in Apache Kafka 4.2. This feature introduces a new kind of group called share groups, as an alternative to consumer groups. Consumers in a share group cooperatively consume records from topics, without assigning each partition to just one consumer. Share groups also introduce per-record acknowledgement and counting of delivery attempts.
- The Streams Rebalance Protocol (KIP-1071) is now production-ready for its core feature set. Due to a critical broker-side bug in the offline migration code (KAFKA-20254), we recommend against doing migrations from classic to streams groups in 4.2.0. The fix is available in 4.2.1.
- The `org.apache.kafka.common.header.internals.RecordHeader` class has been updated to be read thread-safe (KIP-1205).

### Upgrading to 4.1.0

- Apache Kafka 4.1 ships with a preview of Queues for Kafka (KIP-932). To enable share groups, use the `kafka-features.sh` tool to upgrade to `share.version=1`.
- The logger class name for LogCleaner has been updated from `kafka.log.LogCleaner` to `org.apache.kafka.storage.internals.log.LogCleaner` in the log4j2.yaml configuration file.
- The filename for rotated `state-change.log` files has been updated from `stage-change.log.[date]` to `state-change.log.[date]` in the log4j2.yaml configuration file.
- The configuration `log.cleaner.enable` is deprecated (KIP-1148).
- The KIP-966 part 1: Eligible Leader Replicas (ELR) will be enabled by default on the new clusters. After the ELR feature enabled, the previously set `min.insync.replicas` value at the broker-level config will be removed. Please set at the cluster-level if necessary.
- The producer `flush` method now detects potential deadlocks and prohibits its use inside a callback.
- Early Access for the Streams rebalance protocol (KIP-1071): broker side task assignment for Kafka Streams applications.

### Upgrading Servers to 4.0.1 from any version 3.3.x through 3.9.x

- Upgrade the brokers one at a time: shut down the broker, update the code, and restart it.
- Once the cluster's behavior and performance have been verified, finalize the upgrade by running `bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.0`
- Note that cluster metadata downgrade is not supported in this version since it has metadata changes (`IBP_4_0_IV1(23, "4.0", "IV1", true)`).

#### Notable changes in 4.0.0

- Old protocol API versions have been removed. Users should ensure brokers are version 2.1 or higher before upgrading Java clients (including Connect and Kafka Streams which use the clients internally) to 4.0. Similarly, users should ensure their Java clients version is 2.1 or higher before upgrading brokers to 4.0 (KIP-896).
- Apache Kafka 4.0 only supports KRaft mode - ZooKeeper mode has been removed.
- Apache Kafka 4.0 ships with a brand-new group coordinator implementation. The behavior of the new group coordinator can be tuned by setting the configurations with prefix `group.coordinator`.
- The Next Generation of the Consumer Rebalance Protocol (KIP-848) is now Generally Available (GA) in Apache Kafka 4.0. The protocol is automatically enabled on the server when the upgrade to 4.0 is finalized. Note that once the new protocol is used by consumer groups, the cluster can only be downgraded to version 3.4.1 or newer.
- Transactions Server-Side Defense (KIP-890) brings a strengthened transactional protocol to Apache Kafka 4.0. When using 4.0 producer clients, the producer epoch is bumped on every transaction to ensure every transaction includes the intended messages and duplicates are not written as part of the next transaction. Downgrading the protocol is safe.
- Eligible Leader Replicas (KIP-966 Part 1) enhances the replication protocol. Now the KRaft controller keeps track of the data partition replicas that are not included in ISR but are safe to be elected as leader without data loss. Such replicas are stored in the partition metadata as the `Eligible Leader Replicas` (ELR).
- **Common**: `metrics.jmx.blacklist`/`whitelist` removed → use `metrics.jmx.exclude`/`metrics.jmx.include`. `auto.include.jmx.reporter` removed; `metric.reporters` is now set to `org.apache.kafka.common.metrics.JmxReporter` by default. `bufferpool-wait-time-total`, `io-waittime-total`, `iotime-total` metrics removed → use `bufferpool-wait-time-ns-total`, `io-wait-time-ns-total`, `io-time-ns-total`. `NotLeaderForPartitionException` removed; `NotLeaderOrFollowerException` is returned if a request could not be processed because the broker is not the leader or follower for a topic partition. `DefaultPartitioner` and `UniformStickyPartitioner` classes removed. `log.message.format.version` and `message.format.version` configs removed. All configuration files are now in the `config` directory (no separate `config/kraft`). `--bootstrap-server` only supports comma-separated values.
- **Broker**: `offsets.commit.required.acks` removed (KIP-1041). `log.message.timestamp.difference.max.ms` removed → `log.message.timestamp.before.max.ms` / `after.max.ms`. `remote.log.manager.copier.thread.pool.size` and `expiration.thread.pool.size` default changed to 10 from -1; `remote.log.manager.thread.pool.size` default changed to 2 from 10 (KIP-1030). The minimum `segment.bytes`/`log.segment.bytes` has changed from 14 bytes to 1MB.
- **MirrorMaker**: The original MirrorMaker (MM1) and related classes were removed. Please use the Connect-based MirrorMaker (MM2). `topics.blacklist`/`groups.blacklist`/`config.properties.blacklist` removed → `*.exclude`.
- **Tools**: Redirections from the old tools packages have been removed: `kafka.admin.FeatureCommand`, `kafka.tools.ClusterTool`, `kafka.tools.StateChangeLogMerger`, `kafka.tools.StreamsResetter`, `kafka.tools.JmxTool` (use `org.apache.kafka.tools.JmxTool`). `--whitelist` removed from `kafka-console-consumer` → `--include`. `--authorizer`, `--authorizer-properties`, `--zk-tls-config-file` removed from `kafka-acls` → `--bootstrap-server` or `--bootstrap-controller`. `kafka-configs.sh` now uses incrementalAlterConfigs API (broker ≥ 2.3).
- **Connect**: `whitelist`/`blacklist` removed from `ReplaceField` SMT → `include`/`exclude`. `onPartitionsRevoked`/`onPartitionsAssigned(Collection<TopicPartition>)` removed from `SinkTask`; `commitRecord(SourceRecord)` removed from `SourceTask`.
