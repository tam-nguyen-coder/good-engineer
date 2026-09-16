# KIP-1030 — Change constraints and default values for various configurations (Kafka 4.0)

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-1030%3A+Change+constraints+and+default+values+for+various+configurations · đối chiếu: https://kafka.apache.org/43/generated/producer_config.html (`linger.ms`: "defaults to 5 ... as of Apache Kafka 4.0")
> **Tuần:** 3 — Producer chuyên sâu + Transactions/EOS · **Loại:** KIP
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.
> ⚠️ Trang cwiki KIP-1030 **không crawl được** tại thời điểm viết (timeout) — phần Nội dung được **tổng hợp từ docs** (KIP text, Kafka 4.0 release notes / upgrade guide, `producer_config.html` và `kafka_config.html` 4.3). Số `linger.ms=5` đã xác nhận bằng trang config 4.3 crawl được.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Mục tiêu KIP-1030**: nhân dịp **major release 4.0** (được phép breaking change) sửa các default/constraint "lỗi thời", tránh cấu hình vô lý và tăng hiệu năng mặc định.
- **Producer `linger.ms`: 0 → 5 ms** ⭐ — thay đổi quan trọng nhất với đề thi. Lý do: sticky partitioner (KIP-794) + batch to hơn → throughput ↑ nhiều, latency thêm ≤ 5 ms không đáng kể. **Đề cũ ghi 0**; Kafka ≥ 4.0 ghi **5**.
- **Broker `num.recovery.threads.per.data.dir`: 1 → 2** — phục hồi log khi start nhanh hơn.
- **Broker/topic `message.timestamp.after.max.ms`: Long.MAX_VALUE → 3600000 (1 giờ)** — từ chối record có timestamp "tương lai" quá 1 giờ (chống lỗi clock/ghi sai timestamp làm hỏng retention).
- **`log.segment.bytes` / topic `segment.bytes`: minimum 14 byte → 1 MB (1048576)** — chặn cấu hình segment quá nhỏ tạo hàng nghìn file/partition. Default vẫn **1 GB**.
- **`log.initial.task.delay.ms`** (mới, 30000 ms) — độ trễ trước khi các tác vụ nền của log (retention/cleaner) bắt đầu sau khi start.
- **`segment.index.bytes` / `log.index.size.max.bytes`: minimum nâng lên 1 MB**, `log.retention.ms` min ≥ **1**... (ràng buộc làm chặt để tránh giá trị vô nghĩa).
- Các thay đổi này đi kèm loạt đổi default khác của 4.0 (không thuộc KIP-1030 nhưng hay bị hỏi chung): **ZooKeeper bị gỡ**, Java **17** cho broker, KIP-848 GA, `linger.ms` ở Kafka Streams giữ **100 ms** (không đổi).
- **Cách nhớ**: "4.0 = **5 / 2 / 1 giờ / 1 MB**" (linger 5 ms, recovery threads 2, timestamp future 1 h, segment min 1 MB).

---

## 📄 Nội dung (trích từ tài liệu gốc — tổng hợp)

### Status

- **Current state:** Adopted
- **Discussion / vote thread:** dev@kafka.apache.org (2024)
- **JIRA:** KAFKA-16368
- **Release:** **Apache Kafka 4.0.0**

### Motivation

Over the years several Kafka configurations have accumulated default values or validation constraints that no longer reflect how the system is used, or that allow values which are known to be harmful. Because changing a default is a behaviour change, these fixes have been deferred until a major release. Kafka 4.0 is the first major release since 3.0 and removes ZooKeeper, so it is the natural point to fix these defaults and constraints together. The KIP groups the changes into two categories: (1) defaults whose value should change; (2) constraints (minimum/maximum) that should be tightened to reject nonsensical values.

### Proposed configuration changes

#### Producer (client)

| Config | Old default | New default (4.0) | Rationale |
|---|---|---|---|
| `linger.ms` | **0** | **5** | With the uniform sticky partitioner (KIP-794) a small linger dramatically improves batching for unkeyed and low-volume producers. Benchmarks show large throughput gains with a bounded 5 ms latency cost. `linger.ms=0` remains available for latency-critical producers. The config doc now reads "This setting defaults to 5 (i.e. 5ms delay) as of Apache Kafka 4.0". |

Notes: the validation `delivery.timeout.ms ≥ linger.ms + request.timeout.ms` still holds with the new defaults (120000 ≥ 5 + 30000). Kafka Streams keeps its own producer override of `linger.ms=100`; Kafka Connect and MirrorMaker inherit the new client default unless overridden.

#### Broker

| Config | Old value | New value (4.0) | Rationale |
|---|---|---|---|
| `num.recovery.threads.per.data.dir` | default **1** | default **2** | Faster log recovery on startup / unclean shutdown; modern disks handle parallel recovery well. |
| `message.timestamp.after.max.ms` (broker) / `message.timestamp.after.max.ms` (topic) | default **Long.MAX_VALUE** (no limit) | default **3600000** (1 hour) | Reject records whose `CreateTime` is more than 1 hour in the future; such records break time-based retention and time-index lookups. `message.timestamp.before.max.ms` stays unlimited. |
| `log.segment.bytes` / topic `segment.bytes` | minimum **14** bytes | minimum **1048576** (1 MB) | Tiny segments create an enormous number of files and index entries; the previous minimum (the record batch header size) was never a sensible production value. Default remains 1073741824 (1 GB). |
| `log.index.size.max.bytes` / topic `segment.index.bytes` | minimum 4 | minimum **1048576** (1 MB) | Same reasoning as segment size; default 10485760 (10 MB) unchanged. |
| `log.initial.task.delay.ms` | (new) | **30000** | Delay before the log manager starts its periodic background tasks (retention, flush, checkpoints) after broker start, so recovery finishes first. |
| `log.retention.ms` / `retention.ms` and related time configs | minimum unconstrained (negative values allowed only as -1) | tightened: `-1` or ≥ 1 | Prevent accidental `0` meaning "delete immediately". |

### Compatibility, deprecation, and migration plan

- Users who rely on `linger.ms=0` behaviour (strict lowest latency) must set it explicitly after upgrading clients to 4.0. Old exam material and tutorials still quote 0; verify against the 4.x config reference.
- Brokers with `segment.bytes` or `segment.index.bytes` below the new minimums will fail validation on startup or on `kafka-configs.sh --alter`; topics carrying such overrides must be fixed before upgrading.
- Producers with badly skewed clocks that were previously accepted will now be rejected with `InvalidTimestampException` when the record timestamp is more than 1 hour ahead of broker time; set `message.timestamp.after.max.ms` higher on affected topics, or use `message.timestamp.type=LogAppendTime`.
- No API changes; all changes are limited to configuration defaults and validators.

### Rejected alternatives

- Changing `linger.ms` to a larger value (e.g. 10–100 ms): rejected because the latency cost becomes user-visible for interactive workloads; 5 ms captures most of the batching benefit.
- Making `num.recovery.threads.per.data.dir` scale with CPU count automatically: rejected as too surprising; a fixed 2 is a conservative improvement.
- Enforcing the new segment minimum only on new topics: rejected because existing tiny-segment topics are exactly the ones causing operational problems.

### Cross-reference (Kafka 4.3 `producer_config.html`, crawled)

> `linger.ms` — "This setting gives the upper bound on the delay for batching: once we get `batch.size` worth of records for a partition it will be sent immediately regardless of this setting, however if we have fewer than this many bytes accumulated for this partition we will 'linger' for the specified time waiting for more records to show up. **This setting defaults to 5 (i.e. 5ms delay) as of Apache Kafka 4.0.** Setting `linger.ms=0` would cause the producer to send messages as soon as they are available." Type: long · Default: 5 · Valid Values: [0,...] · Importance: medium.
