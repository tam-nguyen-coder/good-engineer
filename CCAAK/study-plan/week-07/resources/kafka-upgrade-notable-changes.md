# Apache Kafka 4.3 — Upgrade & Notable Changes: cái gì đổi khiến tài liệu cũ sai

> **Nguồn (official):** https://kafka.apache.org/43/getting-started/upgrade/
> **Tuần:** 7 — Observability + Troubleshooting playbook · **Loại:** Apache Kafka Docs (Upgrading + Notable Changes)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Thứ tự rolling upgrade 4.x:** tắt mềm broker → thay binary → khởi động → **xác minh cluster khoẻ (URP về 0)** → broker kế tiếp. Chỉ khi **mọi** node đã lên bản mới mới chạy `kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.X` để **finalize**.
- **`inter.broker.protocol.version` đã bị thay** bằng quản lý feature/`metadata.version` qua `kafka-features.sh`. Đáp án nào nhắc `inter.broker.protocol.version` trong ngữ cảnh 4.x là **đáp án của thế hệ trước**.
- **Downgrade metadata:** bản có thay đổi metadata (**4.0, 4.1, 4.3**) **không** downgrade được; chỉ bản không đổi metadata (**4.2**) mới hỗ trợ. Đây là lý do finalize là bước **một chiều** và phải làm sau cùng.
- Cluster phải ở **3.3.x trở lên** trước khi nâng lên 4.x, và 4.x là **KRaft-only** — ZooKeeper đã bị gỡ hoàn toàn ở 4.0.
- **Java tối thiểu (4.0):** client/Streams **Java 11**, broker/Connect/tools **Java 17**.
- **Log4j → Log4j2 ở 4.0**; `KafkaLog4jAppender` bị gỡ. File config là `log4j2.yaml`.
- **Mặc định đã đổi ở 4.0:** `linger.ms` 0 → **5**; `num.recovery.threads.per.data.dir` 1 → **2**; `message.timestamp.after.max.ms` Long.MAX → **1 giờ**.
- **Flag CLI đã đổi ở 4.0:** `kafka-console-consumer --whitelist` → **`--include`**; `kafka-replica-verification --topic-white-list` → **`--topics-include`**; `kafka-verifiable-consumer --broker-list` → **`--bootstrap-server`**; `--bootstrap-server` chỉ nhận danh sách **ngăn cách bằng dấu phẩy, không có khoảng trắng**.
- **KIP-1100 (4.2)** chuẩn hoá tên MBean về `kafka.COMPONENT:type=...` — ví dụ `org.apache.kafka.server:type=AssignmentsManager...` → `kafka.server:type=AssignmentsManager...`. Dashboard cũ dựa trên tên legacy sẽ **im lặng không có dữ liệu** sau nâng cấp: một sự cố observability rất dễ bị chẩn đoán nhầm thành "broker không chạy".
- **Config mới ở 4.3:** `group.coordinator.cached.buffer.max.bytes`, `share.coordinator.cached.buffer.max.bytes`, `remote.log.metadata.topic.min.isr` (mặc định **2**), Streams `dsl.store.format`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Upgrading to 4.3.x from any version 3.3.x through 4.2.x

> Note: Apache Kafka 4.0 removed ZooKeeper support. If your cluster is older than 3.3.x, you must first upgrade to at least 3.3.x and migrate to KRaft before upgrading to 4.x.

For a rolling upgrade:

1. Upgrade the brokers one at a time: shut down the broker, update the code, and restart it.
2. Once the cluster's behavior and performance have been verified, finalize the upgrade by running:

```bash
$ bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3
```

3. Note that cluster metadata downgrade is not supported in versions 4.0, 4.1 and 4.3 since they have metadata changes. Only version 4.2 supports cluster metadata downgrade, use `bin/kafka-features.sh downgrade --release-version 4.2`.

### Notable changes in 4.0.0

- Java 11 is the minimum for clients and Streams; **Java 17** is the minimum for brokers, Connect and tools.
- ZooKeeper mode has been removed. All ZooKeeper-related configurations and tools were deleted. The configuration files were consolidated from `config/kraft` into `config`.
- The `log4j` 1.x dependency has been replaced with **log4j2**. The `KafkaLog4jAppender` was removed.
- `inter.broker.protocol.version` is no longer used; the cluster metadata version is managed with `kafka-features.sh`.
- Default value changes:
  - `linger.ms` changed from `0` to `5`.
  - `num.recovery.threads.per.data.dir` changed from `1` to `2`.
  - `message.timestamp.after.max.ms` changed from `Long.MAX_VALUE` to `3600000` (1 hour).
- Command-line option changes:
  - `kafka-console-consumer.sh`: `--whitelist` replaced by `--include`.
  - `kafka-replica-verification.sh`: `--topic-white-list` replaced by `--topics-include`.
  - `kafka-verifiable-consumer.sh`: `--broker-list` replaced by `--bootstrap-server`.
  - `--bootstrap-server` now accepts only a comma-separated list without spaces.

### Notable changes in 4.2.0

- **KIP-1100**: metric names were standardised on the `kafka.<component>` domain. The deprecated names are replaced, for example `org.apache.kafka.server:type=AssignmentsManager,...` becomes `kafka.server:type=AssignmentsManager,...`, and the `kafka.log.remote` metrics were updated in the same way.
- Cluster metadata downgrade is supported for this release because it introduces no metadata changes.

### Notable changes in 4.3.0

- New broker configurations: `group.coordinator.cached.buffer.max.bytes` and `share.coordinator.cached.buffer.max.bytes`.
- New configuration `remote.log.metadata.topic.min.isr` with a default of `2`.
- Kafka Streams adds `dsl.store.format` for headers-aware stores.

### Notable changes in 4.1.0

- Cluster metadata downgrade is **not** supported from this release because it introduces metadata changes.
- Eligible Leader Replicas (KIP-966 Part 1) are enabled by default for newly created clusters (`eligible.leader.replicas.version=1`). ELR tracks replicas that were in the ISR and remain eligible to become leader, reducing the cases in which an unclean leader election is the only option.
- Queues for Kafka (share groups, KIP-932) moved from early access to preview.

### Upgrade checklist for a KRaft cluster

1. Confirm the cluster is healthy: `UnderReplicatedPartitions` is 0 and `OfflinePartitionsCount` is 0.
2. Identify the active controller; it is upgraded last.
3. For each node in turn: stop it gracefully (`controlled.shutdown.enable=true`), replace the binaries, start it, then **wait for the under-replicated partition count to return to zero** before moving to the next node.
4. Verify the whole cluster is on the new software before touching feature levels.
5. Finalize:

```bash
# Xem feature level đang finalize (in ra SupportedMinVersion / SupportedMaxVersion / FinalizedVersionLevel
# cho metadata.version và các feature khác — con số cụ thể tuỳ phiên bản, đọc trực tiếp trên cluster của bạn)
$ bin/kafka-features.sh --bootstrap-server localhost:9092 describe

# Nâng feature level lên mức của 4.3 (một chiều với các bản có thay đổi metadata)
$ bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3

# Thử trước khi làm thật
$ bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3 --dry-run
```

6. Confirm with `kafka.server:type=MetadataLoader,name=CurrentMetadataVersion` or by re-running `kafka-features.sh describe`.

### Things that break monitoring across an upgrade

- **Metric names (KIP-1100, 4.2).** Exporter rules and dashboards keyed on the deprecated `org.apache.kafka.*` domains stop matching. The exporter target stays healthy, so this presents as "no data" rather than as an error.
- **`inter.broker.protocol.version` is gone.** Any automation that still sets it in `server.properties` is writing an unknown configuration.
- **Logging.** Kafka 4.0 uses `log4j2.yaml`; a `log4j.properties` carried over from a 3.x installation is ignored, which silently disables custom appenders such as a separate authorizer log.
- **Java version.** Brokers, Connect and tools require Java 17; an agent or JMX exporter jar built for Java 8 may need updating at the same time.
