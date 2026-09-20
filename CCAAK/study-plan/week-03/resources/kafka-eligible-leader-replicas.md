# Eligible Leader Replicas (ELR) — KIP-966 Part 1

> **Nguồn (official):** https://kafka.apache.org/43/operations/eligible-leader-replicas/ · KIP-966: https://cwiki.apache.org/confluence/display/KAFKA/KIP-966%3A+Eligible+Leader+Replicas
> **Tuần:** 3 — Cluster Config II: replication & durability · **Loại:** Apache Kafka 4.3 Documentation (Operations) + KIP
> ⚠️ Nội dung dưới đây được crawl tự động từ trang docs chính thức. **Trang cwiki KIP-966 không crawl được** (cwiki.apache.org timeout lúc viết) — phần "KIP-966 tóm lược" bên dưới được tổng hợp từ trang Operations và bảng đối chiếu trong [`CCDAK/study-plan/VALIDATION.md`](../../../../CCDAK/study-plan/VALIDATION.md), không phải trích nguyên văn KIP.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **ELR = tập replica NGOÀI ISR nhưng vẫn an toàn để lên leader.** Có được là nhờ quy tắc **"strict min ISR"**: high watermark **không tiến** khi `|ISR| < min.insync.replicas`, nên những replica vừa rơi khỏi ISR vẫn chắc chắn có đủ dữ liệu đã commit.
- Timeline: **khả dụng từ 4.0 nhưng phải opt-in**; **bật mặc định cho cluster MỚI từ 4.1**. Cluster nâng cấp lên 4.1+ **không** tự bật.
- Bật: `eligible.leader.replicas.version=1` (đặt qua `kafka-features.sh`/feature version ở mức server). Tắt/downgrade an toàn: đặt về `0`.
- **Thứ tự bầu leader khi ELR bật (thuộc lòng, hay ra dạng list-order):**
  1. **ISR** không rỗng → chọn một replica trong ISR.
  2. **ELR** không rỗng → chọn một replica trong ELR **chưa bị fenced**.
  3. **Last known leader** nếu nó unfenced (đây là hành vi giống trước 4.0 khi mọi replica offline).
- KRaft controller lưu ELR trong trường **`Eligible Leader Replicas` của `PartitionRecord`**. Đọc qua API **`DescribeTopicPartitions`** → thực tế là cột **`Elr:`** và **`LastKnownElr:`** trong output `kafka-topics.sh --describe`.
- Khi ELR bật, **ngữ nghĩa `min.insync.replicas` đổi** và config này bị siết:
  - Cluster-level `min.insync.replicas` **tự động được thêm** nếu chưa có (lấy giá trị static của active controller).
  - **Không được xoá** `min.insync.replicas` ở cluster level.
  - Cập nhật `min.insync.replicas` ở cluster level (**kể cả đặt lại đúng giá trị cũ**) → **toàn bộ ELR state bị xoá**.
  - `min.insync.replicas` ở **broker level bị gỡ** và **không được sửa** — muốn chỉnh thì chỉnh ở cluster level.
  - Sửa `min.insync.replicas` của một **topic** → ELR state của topic đó bị xoá.
- **ELR không thay thế `unclean.leader.election.enable`.** ELR làm *giảm* số tình huống buộc phải dùng unclean election, nhưng khi ISR **và** ELR đều rỗng và last known leader cũng offline thì partition vẫn offline — lúc đó unclean election vẫn là lựa chọn cuối (và vẫn mất dữ liệu).
- Trong đề: thấy "partition offline dù vẫn còn broker sống có dữ liệu" → nghĩ tới **ELR** trước khi nghĩ tới unclean election.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Overview

Starting from Apache Kafka 4.0, Eligible Leader Replicas (KIP-966 Part 1) is available for the users to an improvement to Kafka replication (**ELR is enabled by default on new clusters starting 4.1**). As the "strict min ISR" rule has been generally applied, which means the high watermark for the data partition can't advance if the size of the ISR is smaller than the min ISR (`min.insync.replicas`), it makes some replicas that are not in the ISR safe to become the leader. The KRaft controller stores such replicas in the `PartitionRecord` field called **Eligible Leader Replicas**. During the leader election, the controller will select the leaders with the following order:

- If ISR is not empty, select one of them.
- If ELR is not empty, select one that is not fenced.
- Select the last known leader if it is unfenced. This is a similar behavior prior to the 4.0 when all the replicas are offline.

### Upgrade & Downgrade

The ELR is not enabled by default for 4.0. To enable the new protocol on the server, set **`eligible.leader.replicas.version=1`**. After that the upgrade, the KRaft controller will start tracking the ELR.

Downgrades are safe to perform by setting `eligible.leader.replicas.version=0`.

### Tool

The ELR fields can be checked through the API **`DescribeTopicPartitions`**. The admin client can fetch the ELR info by describing the topics.

Note that when the ELR feature is enabled:

- The cluster-level `min.insync.replicas` config will be added if there is not any. The value is the same as the static config in the active controller.
- The removal of `min.insync.replicas` config at the cluster-level is not allowed.
- If the cluster-level `min.insync.replicas` is updated, even if the value is unchanged, all the ELR state will be cleaned.
- The previously set `min.insync.replicas` value at the broker-level config will be removed. Please set at the cluster-level if necessary.
- The alteration of `min.insync.replicas` config at the broker-level is not allowed.
- If `min.insync.replicas` is updated for a topic, the ELR state will be cleaned.

### Liên quan — mô tả `min.insync.replicas` trong Broker Configs 4.3

> […] **Note that when the Eligible Leader Replicas feature is enabled, the semantics of this config changes. Please refer to the ELR section for more info.**

### Liên quan — Upgrading to 4.0 (Notable changes)

> **Eligible Leader Replicas (KIP-966 Part 1) enhances the replication protocol for the Apache Kafka 4.0. Now the KRaft controller keeps track of the data partition replicas that are not included in ISR but are safe to be elected as leader without data loss. Such replicas are stored in the partition metadata as the Eligible Leader Replicas (ELR).**

### Liên quan — Upgrading to 4.1 (Notable changes)

> **The KIP-966 part 1: Eligible Leader Replicas (ELR) will be enabled by default on the new clusters. After the ELR feature enabled, the previously set `min.insync.replicas` value at the broker-level config will be removed. Please set at the cluster-level if necessary.**

### Liên quan — cách đọc và đổi feature version (Operations → KRaft)

Feature version của KRaft được xem và nâng bằng `kafka-features.sh`, cùng cơ chế với `kraft.version` và `metadata.version`:

```
$ bin/kafka-features.sh --bootstrap-server localhost:9092 describe
Feature: kraft.version      SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 0        Epoch: 7
Feature: metadata.version   SupportedMinVersion: 3.3-IV3  SupportedMaxVersion: 4.0-IV3  FinalizedVersionLevel: 4.0-IV3  Epoch: 7
```

To upgrade all of the feature versions to the latest version:

```
$ bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.1
```

To upgrade just one feature version (the same form is used for `eligible.leader.replicas.version`):

```
$ bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --feature kraft.version=1
```

---

## KIP-966 tóm lược *(không crawl được cwiki — tổng hợp từ trang Operations ở trên + bảng version trong `CCDAK/study-plan/VALIDATION.md`)*

| Hạng mục | Nội dung |
|---|---|
| Tên đầy đủ | KIP-966: Eligible Leader Replicas |
| Vấn đề giải quyết | Trước 4.0, khi ISR co về rỗng, lựa chọn duy nhất còn lại là **chờ replica cũ quay lại** (partition offline) hoặc **unclean leader election** (mất dữ liệu). Không có khái niệm "replica này ngoài ISR nhưng vẫn đủ dữ liệu". |
| Cơ chế | Áp dụng **strict min ISR** → HW không tiến khi `|ISR| < min.insync.replicas` → mọi replica rời ISR **sau thời điểm đó** vẫn giữ đủ mọi message đã commit → controller ghi chúng vào **ELR** trong `PartitionRecord`. |
| Trạng thái theo version | 4.0: **Part 1 khả dụng, opt-in** (`eligible.leader.replicas.version=1`) · 4.1+: **bật mặc định cho cluster mới** · downgrade bằng `=0` |
| Ảnh hưởng tới admin | Thêm 2 cột `Elr:` / `LastKnownElr:` khi describe topic; `min.insync.replicas` chuyển hẳn về **cluster level** (broker level bị gỡ) |
| Điều KHÔNG thay đổi | `unclean.leader.election.enable` vẫn mặc định **false**; ELR **không** làm partition tự sống lại khi mọi replica đều offline/fenced |

### Ví dụ output `kafka-topics.sh --describe` khi ELR đã bật

```
Topic: orders  TopicId: xQ0k...  PartitionCount: 3  ReplicationFactor: 3  Configs: min.insync.replicas=2
  Topic: orders  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3,4  Elr:      LastKnownElr:
  Topic: orders  Partition: 1  Leader: 3  Replicas: 3,4,2  Isr: 3,4,2  Elr:      LastKnownElr:
  Topic: orders  Partition: 2  Leader: 4  Replicas: 4,2,3  Isr: 4,2     Elr: 3   LastKnownElr: 3
```

> Đọc dòng cuối: partition 2 có ISR co về `4,2`; replica `3` rơi khỏi ISR **nhưng nằm trong ELR** → nếu broker 4 và 2 cùng chết, controller vẫn được phép bầu **3** làm leader mà **không** cần bật unclean leader election.
> ⚠️ Khi feature **chưa bật**, hai cột này vẫn xuất hiện nhưng luôn rỗng hoặc `N/A` — đừng nhầm "có cột" với "đã bật ELR". Kiểm tra bằng `kafka-features.sh describe | grep eligible`.
