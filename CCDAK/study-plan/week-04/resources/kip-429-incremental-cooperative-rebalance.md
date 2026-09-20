# KIP-429 — Kafka Consumer Incremental (Cooperative) Rebalance Protocol + `CooperativeStickyAssignor`

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-429%3A+Kafka+Consumer+Incremental+Rebalance+Protocol · https://kafka.apache.org/43/javadoc/org/apache/kafka/clients/consumer/CooperativeStickyAssignor.html
> **Tuần:** 4 — Consumer chuyên sâu: group, rebalance, offset · **Loại:** KIP + Apache Kafka Docs (Javadoc)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Released **Kafka 2.4**. Giải quyết **stop-the-world** của eager rebalance: mọi member phải **revoke toàn bộ** partition trước khi rejoin, kể cả partition sau đó được giao lại cho chính nó → dừng xử lý vô ích (đặc biệt tệ với Kafka Streams có state).
- Cooperative = **2 rebalance liên tiếp**: (1) leader tính assignment mới, chỉ **revoke các partition phải đổi chủ** (member giữ phần còn lại và tiếp tục xử lý); (2) rebalance thứ hai **assign** các partition vừa revoke cho chủ mới. Chìa khoá: subscription mang thêm **`ownedPartitions`** để leader biết ai đang giữ gì.
- `ConsumerRebalanceListener`: `onPartitionsRevoked` chỉ nhận **partition thực sự bị lấy đi**; `onPartitionsAssigned` chỉ nhận partition **mới**; thêm **`onPartitionsLost`** cho partition mất **không qua revoke** (member bị đá khỏi group, hết session) → **không commit** trong `onPartitionsLost`.
- `RebalanceProtocol`: **EAGER** (Range/RoundRobin/Sticky) vs **COOPERATIVE** (`CooperativeStickyAssignor`). Group chỉ dùng COOPERATIVE khi **mọi member** đều hỗ trợ; nếu trộn → chọn EAGER (an toàn).
- **Nâng cấp = 2 rolling bounce:** bounce 1 đặt `partition.assignment.strategy = [CooperativeStickyAssignor, <assignor cũ>]` (group vẫn eager); bounce 2 **bỏ assignor cũ** → group chuyển cooperative. Sai quy trình → có thể 2 consumer cùng giữ 1 partition hoặc lỗi fatal.
- Mặc định 4.3 `[RangeAssignor, CooperativeStickyAssignor]` → thực tế chạy Range (eager); chỉ cần **1 bounce** bỏ `RangeAssignor` để lên cooperative (vì assignor cooperative đã có sẵn trong list).
- Streams có quy trình tương tự bằng config `upgrade.from`. `commitSync` trong lúc rebalance → `RebalanceInProgressException`; `poll()` có thể trả record **trong khi** rebalance (với cooperative).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Part A — KIP-429

#### Status

Accepted; released in **Apache Kafka 2.4.0**. This KIP introduces cooperative rebalancing to address the stop-the-world effect of eager rebalancing, particularly benefiting stateful applications such as Kafka Streams.

#### Motivation

The existing (eager) rebalance protocol requires all consumers to **revoke all of their partitions** before re-joining the group, then wait for the new assignment. During this window no processing happens for any partition of the group. Partitions are frequently revoked and then immediately re-assigned to the same consumer, which is avoidable disruption — and for stateful consumers (Streams) it can mean tearing down and rebuilding local state for nothing. As a consumer group grows, and in cloud deployments with frequent scaling / rolling restarts, this "stop-the-world" cost dominates.

#### Proposed Changes — Incremental Cooperative Rebalancing

Instead of a single synchronized rebalance in which everything is revoked, the protocol uses **consecutive rebalances**:

1. **First rebalance:** members join carrying the partitions they currently own (`ownedPartitions`). The leader computes the new assignment but a member may only be assigned partitions that are **not owned by anyone else**. Each member compares the new assignment with what it owns and **revokes only the partitions that must move** to a different consumer; it keeps processing everything else.
2. **Second rebalance:** members that revoked partitions trigger a follow-up rebalance; the previously revoked partitions are now unowned and are **assigned to their new owners**.

This minimizes partition churn when a member joins or fails, and processing continues for all partitions that do not move.

**Consumer protocol changes:** the `Subscription` and `Assignment` structures gain an `ownedPartitions` field (protocol version bump; older leaders ignore unknown appended fields). The assignor interface exposes `supportedProtocols()` returning `EAGER` and/or `COOPERATIVE`.

**Rebalance listener semantics (cooperative):**

- `onPartitionsRevoked(Collection)` — called **only for partitions that are actually being reassigned** to another member, before they are given away (last chance to commit offsets for them).
- `onPartitionsAssigned(Collection)` — called with **newly acquired** partitions only (may be empty).
- `onPartitionsLost(Collection)` — **new**: called when partitions were lost without a normal revocation (member kicked out of the group, session timeout, fenced); the member should **not** commit for them. Default implementation delegates to `onPartitionsRevoked` for backward compatibility.

Callbacks may be skipped entirely when a member's assignment does not change.

#### `RebalanceProtocol`

- **EAGER** — original behavior: all partitions revoked before re-joining (`RangeAssignor`, `RoundRobinAssignor`, `StickyAssignor`).
- **COOPERATIVE** — partitions retained across rebalances whenever possible; only the ones that move are revoked (`CooperativeStickyAssignor`, or a custom assignor declaring COOPERATIVE).

The group uses the **most preferred protocol supported by every member**. If any member only supports EAGER, the whole group runs EAGER. A custom cooperative assignor must guarantee a partition is revoked before being reassigned, otherwise two consumers could own the same partition.

#### `CooperativeStickyAssignor`

A new built-in assignor combining the `StickyAssignor` balancing logic with the cooperative protocol. It uses the `ownedPartitions` information from the consumer protocol to keep assignments stable and to compute which partitions need to move.

#### Upgrade Path — two rolling bounces

**Bounce 1:** upgrade the client bytecode and set `partition.assignment.strategy` to **both** assignors, e.g. `"cooperative-sticky, range"` (the cooperative one first). Because some members still only support the old assignor, the group keeps selecting the **EAGER** protocol during this phase — safe.

**Bounce 2:** remove the legacy assignor, keeping only `"cooperative-sticky"`. Once every member supports the cooperative protocol, the group switches to **COOPERATIVE**.

The two-bounce approach prevents a situation where an old (eager) leader misinterprets the new protocol data sent by upgraded consumers, which could otherwise lead to partitions being owned by two consumers. Kafka Streams applications need an analogous two-bounce process using the `upgrade.from` configuration set to the previous version during the first bounce.

#### Compatibility and extras

- Protocol additions are backward compatible (fields appended); mismatched protocols across members result in a fatal error rather than undefined behavior.
- New consumer metrics: rebalance rate/latency, time spent in rebalance listener callbacks.
- `poll()` may return records while a cooperative rebalance is in progress; `commitSync()` during a rebalance throws `RebalanceInProgressException`.

### Part B — Javadoc `CooperativeStickyAssignor` (Kafka 4.3)

`public class CooperativeStickyAssignor extends AbstractStickyAssignor` — A cooperative version of the `AbstractStickyAssignor`. This follows the same (sticky) assignment logic as `StickyAssignor` but allows for cooperative rebalancing while the `StickyAssignor` follows the eager rebalancing protocol. See `ConsumerPartitionAssignor.RebalanceProtocol` for an explanation of the rebalancing protocols.

Users should prefer this assignor for newer clusters. To turn on cooperative rebalancing you must set all your consumers to use this `PartitionAssignor`, or implement a custom one that returns `RebalanceProtocol.COOPERATIVE` in `supportedProtocols()`.

**Important:** if upgrading from 2.3 or earlier, you must follow a specific upgrade path in order to safely turn on cooperative rebalancing. See the upgrade guide for details (two rolling bounces: add the cooperative assignor alongside the existing one, then remove the old one).

| Method | Purpose |
|--------|---------|
| `name()` | Returns `"cooperative-sticky"` |
| `supportedProtocols()` | Returns `[COOPERATIVE]` (and EAGER for compatibility during upgrade) |
| `subscriptionUserData(Set<String> topics)` | Encodes the generation used to resolve stale owned-partition claims |
| `assignPartitions(...)` | Sticky assignment; partitions moving to a new owner are removed from the assignment of the current owner first (they are assigned in the follow-up rebalance) |
| `onAssignment(Assignment, ConsumerGroupMetadata)` | Records the generation for the next rebalance |
