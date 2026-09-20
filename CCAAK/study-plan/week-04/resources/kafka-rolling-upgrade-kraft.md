# Apache Kafka 4.3 — Rolling upgrade, `metadata.version` và `kafka-features.sh`

> **Nguồn (official):** https://kafka.apache.org/43/getting-started/upgrade/ · bổ sung từ https://kafka.apache.org/43/operations/kraft/
> **Tuần:** 4 — Deployment Architecture · **Loại:** Apache Kafka 4.3 Docs (Upgrading)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ và cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Quy trình nâng cấp KRaft chỉ có **2 giai đoạn**: (1) *"Upgrade the brokers one at a time: shut down the broker, update the code, and restart it"* → (2) sau khi mọi broker chạy bản mới **và** hành vi đã được xác minh, **finalize** bằng `kafka-features.sh upgrade --release-version 4.3`.
- **`metadata.version` thay hoàn toàn `inter.broker.protocol.version`.** Trong KRaft, `inter.broker.protocol.version` **không còn tồn tại** — mọi phương án đề nhắc nó để "chốt version sau upgrade" đều sai với 4.x.
- Mỗi `MetadataVersion` mang một cờ **có/không thay đổi metadata**. Có thay đổi → **chặn downgrade**. Cụ thể: **4.3.0 và 4.0.x không downgrade được** (*"Cluster metadata downgrade is not supported in this version since it has metadata changes"*); **4.2.0 downgrade được** vì không có metadata change.
- Điều kiện nâng lên 4.x: software và metadata version phải **≥ 3.3.x**. Cluster KRaft cũ hơn → nâng qua **3.9.x** trước. Cluster còn ZooKeeper → **migrate sang KRaft trước** (qua 3.9), 4.x không còn ZooKeeper.
- Thứ tự an toàn trong thực tế: nâng **controller trước hay sau** đều phải **1 node/lần**; giữa 2 node phải **chờ `UnderReplicatedPartitions` về 0** và `ActiveControllerCount` tổng = 1. RF 3 / `min.insync.replicas` 2 chỉ chịu **1** broker vắng — tắt 2 broker cùng lúc là `NotEnoughReplicas`.
- `controlled.shutdown.enable=true` (mặc định) là thứ khiến rolling upgrade "zero-downtime": broker chuyển leadership rồi mới tắt. `kill -9` thì không.
- `kafka-features.sh describe` là lệnh đọc trạng thái feature: `metadata.version`, `kraft.version`, `group.version`, `share.version`, `transaction.version`, `eligible.leader.replicas.version`. `kraft.version` = **1** nghĩa là **dynamic quorum** (KIP-853); **0** là static quorum.
- Mốc version cần thuộc: **4.0** KRaft-only, bỏ ZooKeeper, Java **17** cho broker / **11** cho client · **4.1** Consumer Rebalance Protocol (KIP-848) GA, share group preview, new group coordinator · **4.2** share group production-ready (KIP-932), Streams Rebalance Protocol GA, bỏ `log.message.format.version` · **4.3** dynamic quorum controller config changes, coordinator config mới.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Upgrading to 4.3.0 from any version 3.3.x through 4.2.0

If you are upgrading from a version prior to 3.3.0, please see the note below. Once you have changed the metadata version to at least 3.3, you should not downgrade to a version prior to 3.3.

**For a rolling upgrade:**

1. Upgrade the brokers one at a time: shut down the broker, update the code, and restart it. Once you have done so, the brokers will be running the latest version and you can verify that the cluster's behavior and performance meet expectations.

2. Once the cluster's behavior and performance have been verified, finalize the upgrade by running:

   ```bash
   bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3
   ```

3. Note that cluster metadata downgrade is not supported in this version since it has metadata changes. Every `MetadataVersion` has a boolean parameter that indicates if there are metadata changes (i.e. `IBP_4_3_IV0(26, "4.3", "IV0", true)` means this version has metadata changes). Given your current and target versions, a downgrade is only possible if there are no metadata changes in the versions between.

### Upgrading to 4.2.0 from any version 3.3.x through 4.1.0

The rolling procedure is identical, finalized with:

```bash
bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.2
```

Cluster metadata downgrade **is** supported in this version since it has no metadata changes.

### Upgrading to 4.0.0 from any version 3.3.x through 3.9.x

Note: Apache Kafka 4.0 only supports KRaft mode — ZooKeeper mode has been removed. If you are upgrading from a ZooKeeper-based cluster, you must first migrate to KRaft (available from 3.4 as early access, production-ready in 3.6, with 3.9 being the recommended bridge release) before upgrading to 4.0.

Note: Before upgrading to Apache Kafka 4.0, please ensure that the metadata version (`metadata.version`) is set to at least 3.3. This can be verified with `bin/kafka-features.sh describe` and set with `bin/kafka-features.sh upgrade --metadata 3.3` if required.

Cluster metadata downgrade is not supported in this version since it has metadata changes.

### Notable changes in 4.3.0

- ZooKeeper support has been fully removed; KRaft is the only metadata mode.
- New group coordinator and share coordinator configurations.
- Changes to dynamic quorum controller configuration.
- Headers-aware state stores in Kafka Streams.

### Notable changes in 4.2.0

- Share groups (KIP-932, "Queues for Kafka") are production-ready.
- The Streams Rebalance Protocol (KIP-1071) reached GA.
- `log.message.format.version` and related message-format downgrade configurations were removed.

### Notable changes in 4.1.0

- Share groups available as preview.
- The next-generation Consumer Rebalance Protocol (KIP-848) reached GA.
- New group coordinator enabled by default.

### Notable changes in 4.0.0

- ZooKeeper mode removed; KRaft only.
- Old protocol API versions removed; the client protocol baseline moved forward.
- Java 11 is the minimum for clients, Java 17 the minimum for brokers, Connect and tools.
- MirrorMaker 1 (`kafka-mirror-maker.sh`) removed — use MirrorMaker 2.

---

## 📄 Bổ sung — `kafka-features.sh describe` (từ trang KRaft operations)

Quorum kiểu nào là do feature `kraft.version` quyết định:

```bash
bin/kafka-features.sh --bootstrap-controller localhost:9093 describe
```

> If `kraft.version` is at `FinalizedVersionLevel` 1 or above, the cluster is using a **dynamic** controller quorum (`controller.quorum.bootstrap.servers`). Otherwise it is a **static** quorum configured with `controller.quorum.voters`.

Output mẫu trên cluster 4.3 dựng bằng static quorum:

```
Feature: eligible.leader.replicas.version  SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1
Feature: group.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1
Feature: kraft.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 0
Feature: metadata.version                  SupportedMinVersion: 3.3-IV3  SupportedMaxVersion: 4.3-IV0  FinalizedVersionLevel: 4.3-IV0
Feature: share.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1
Feature: transaction.version               SupportedMinVersion: 0        SupportedMaxVersion: 2        FinalizedVersionLevel: 2
```

> 📌 `kafka-features.sh upgrade --release-version <X>` nâng **toàn bộ** feature lên mức mà bản `<X>` định nghĩa. Thêm `--dry-run` để xem sẽ đổi gì mà không áp dụng. Có `downgrade` và `disable` nhưng chỉ chạy được khi các version liên quan không mang metadata change (và `--unsafe` cho downgrade có mất mát — không dùng ở production).

### Config bị gỡ trong KRaft (liên quan trực tiếp tới upgrade và maintenance)

- `inter.broker.protocol.version` — thay bằng **`metadata.version`**, quản lý bằng `bin/kafka-features.sh`.
- `controlled.shutdown.max.retries` và `controlled.shutdown.retry.backoff.ms` — controlled shutdown giờ đi qua **broker heartbeat** với controller.
- `leader.imbalance.per.broker.percentage` — **không dùng trong KRaft** (`leader.imbalance.check.interval.seconds` vẫn còn).
- `broker.id.generation.enable`, `reserved.broker.max.id` — thay bằng `node.id`.
- `zookeeper.connect` và mọi `zookeeper.*`.
