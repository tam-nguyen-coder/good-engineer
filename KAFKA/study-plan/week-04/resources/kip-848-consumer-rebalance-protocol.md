# KIP-848 — The Next Generation of the Consumer Rebalance Protocol (`group.protocol=consumer`) + Kafka 4.3 Operations: Consumer Rebalance Protocol

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-848%3A+The+Next+Generation+of+the+Consumer+Rebalance+Protocol · https://kafka.apache.org/43/operations/consumer-rebalance-protocol/
> **Tuần:** 4 — Consumer chuyên sâu: group, rebalance, offset · **Loại:** KIP + Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất. Số mặc định `consumer.heartbeat.interval.ms` trong KIP gốc là 3000; **docs 4.3 hiện tại là 5000** — dùng 5000 khi thi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Timeline: Early Access **3.7** → **GA 4.0** → 4.3 log warning khuyến nghị bỏ classic (KIP-1274) → **5.0** `consumer` là mặc định → **6.0** client chỉ còn `consumer`.
- Vấn đề của classic: **group leader phía client** tính assignment, `JoinGroup`/`SyncGroup` tạo **synchronization barrier** — "một consumer hỏng có thể kéo cả group xuống"; bug rebalance phải sửa ở client; không commit được trong lúc cooperative rebalance.
- Giải pháp: **1 API duy nhất `ConsumerGroupHeartbeat`** (thay JoinGroup/SyncGroup/Heartbeat); **group coordinator (broker) tính target assignment**; member **hội tụ dần** (revoke → ack → nhận partition mới) theo **epoch** (group epoch / assignment epoch / member epoch) — hoàn toàn incremental, không barrier.
- Server-side assignor: **`uniform`** (mặc định, cân bằng + sticky, tương đương CooperativeSticky/Sticky/RoundRobin) và **`range`** (co-partition theo topic). Chọn qua client config **`group.remote.assignor`**; broker liệt kê trong `group.consumer.assignors`. Client-side assignor tuỳ biến **chưa hỗ trợ** (KAFKA-18327).
- Client config bị **bỏ qua** với `consumer`: `session.timeout.ms`, `heartbeat.interval.ms`, `partition.assignment.strategy`; `enforceRebalance()` thành no-op. Thay bằng **group config broker**: `consumer.session.timeout.ms` **45000**, `consumer.heartbeat.interval.ms` **5000** (giới hạn bởi `group.consumer.min/max.*`). **`max.poll.interval.ms` vẫn là client config.**
- Static membership (`group.instance.id`) vẫn hỗ trợ: member tạm rời gửi heartbeat với member epoch **-2**; quay lại trong session timeout nhận lại assignment cũ.
- Migration: **offline** (dừng hết → group rỗng → start với `consumer`, group tự đổi type) hoặc **online** rolling (member `consumer` đầu tiên **chuyển type group**; member classic còn lại được phục vụ qua lớp adapter dịch JoinGroup/SyncGroup — yêu cầu assignor classic không nhúng metadata tuỳ biến). Member `consumer` cuối rời → group quay về classic. Downgrade theo chiều ngược.
- Protocol mới **chỉ dùng topic ID** (OffsetCommit/OffsetFetch v9): xoá & tạo lại topic → topic ID mới → offset cũ không dùng lại. Bật phía broker qua feature flag `group.version`. Mapping assignor khi migrate: `RangeAssignor→range`, `CooperativeSticky/Sticky/RoundRobin→uniform`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Part A — KIP-848 (Apache Kafka wiki)

#### Status

Current state: **Accepted** / Released. The new consumer rebalance protocol with server-side assignors reached GA in Apache Kafka **4.0**. Client-side assignor implementation remains pending; topic ID support for offset operations arrived in Kafka 4.2.

#### Motivation

The existing consumer protocol, introduced eight years prior, relies on thick clients managing group membership through Kafka. While superior to the ZooKeeper-based approach that preceded it, operational challenges persist:

- Rebalance bugs historically required client-side fixes, which are slow to roll out (especially in cloud environments where the operator does not control the clients).
- Troubleshooting requires access to client logs, complicating support in managed services.
- The embedded protocol (subscription/assignment bytes opaque to the broker) allows protocol reuse (e.g. Connect, Streams) but obscures broker-side state inspection.
- Clients independently monitor metadata, causing inconsistent group views during transitions.

**Synchronization barrier:** "A single misbehaving consumer can take down or disturb the whole group because a rebalance of the whole group is required whenever a consumer joins, leaves or fails." This barrier limits scalability and prevents offset commits during cooperative rebalancing.

**Protocol complexity:** incremental extensions (KIP-429 cooperative rebalancing, KIP-345 static membership) accumulated complexity; "fake" rebalances used to propagate state confuse users and complicate metrics.

#### Design Goals

- True incrementalism without a global synchronization barrier.
- Move complexity from consumers to the group coordinator.
- Continue to support power users implementing custom assignors.
- Maintain at-least-once guarantees, exactly-once for clean handoffs.
- Upgrade without downtime.

#### Proposed Changes — Overview

**`ConsumerGroupHeartbeat` API** replaces `JoinGroup`/`SyncGroup`/`Heartbeat`, piggybacking assignment and revocation on the heartbeat mechanism. Members independently converge toward a declarative **target assignment** computed by the group coordinator.

**Epochs:**

- **Group Epoch** — incremented when the group metadata changes (member joins/leaves/fails, subscription updates, partition metadata updates).
- **Assignment Epoch** — a new target assignment is computed whenever the group epoch is larger than the current assignment epoch; the target assignment carries the assignment epoch.
- **Member Epoch** — tracks each member's convergence; a member's epoch is bumped to the assignment epoch once it has revoked the partitions it no longer owns. Offset commits carry the member epoch so that a member which lost a partition is **fenced**.

**Reconciliation (per member, incremental):**

1. Revoke partitions that are not in the target assignment (call `onPartitionsRevoked`, commit offsets).
2. Acknowledge via heartbeat; the coordinator bumps the member epoch.
3. Receive newly assigned partitions incrementally as other members release them (a partition is only assigned once its previous owner has revoked it — no double ownership).

**Server-side assignors:** "The group coordinator either directly computes the new target assignment for the group based on its default server-side assignor or requests a new assignment from one of the members in the group." Built-in:

- `range` — `org.apache.kafka.coordinator.group.assignor.RangeAssignor` (co-partitions topics with the same number of partitions).
- `uniform` — `org.apache.kafka.coordinator.group.assignor.UniformAssignor` (distributes evenly; sticky, minimizes movement).

**Client-side assignors** (`group.local.assignor`) — not yet implemented; future capability where a member computes the assignment while the coordinator still controls execution.

#### Configuration

Broker-side group-level configurations (settable via `IncrementalAlterConfigs` with resource type GROUP):

- `group.consumer.session.timeout.ms` — default 45000
- `group.consumer.heartbeat.interval.ms` — default 3000 in the KIP text (**current 4.3 docs: `consumer.heartbeat.interval.ms` = 5000**)
- `group.consumer.min.session.timeout.ms` / `group.consumer.max.session.timeout.ms`, `group.consumer.min.heartbeat.interval.ms` / `group.consumer.max.heartbeat.interval.ms`
- `group.consumer.assignors` — default `uniform, range`
- `group.consumer.max.size`

Consumer-side:

- `group.protocol` — `classic` (default) or `consumer`
- `group.remote.assignor` — name of the server-side assignor (null → coordinator default `uniform`)
- `group.local.assignor` — client-side assignor (future)

**No longer used / ignored with the new protocol:** `session.timeout.ms`, `heartbeat.interval.ms`, `partition.assignment.strategy`; `Consumer#enforceRebalance()` becomes a no-op with a warning.

#### Static Membership

Preserved from KIP-345. A static member that leaves temporarily sends a heartbeat with member epoch **-2** (the coordinator keeps its assignment). Rejoining with the same `group.instance.id` within the session timeout reinstates the previous assignment without a rebalance. A second instance with the same `group.instance.id` fences the first (`FencedInstanceIdException`).

#### Upgrade and Compatibility

**Online migration:** groups transition automatically — the first new-protocol consumer converts the group from `classic` type to `consumer` type; the last new-protocol consumer leaving reverts it. Non-upgraded (classic) consumers keep working through an **adapter layer** that translates legacy `JoinGroup`/`SyncGroup`/`Heartbeat` calls onto the new protocol (only when the classic assignor does not embed custom metadata).

**Offline migration:** shut down every consumer so that the group becomes empty, then restart with `group.protocol=consumer`.

Consumers requesting a protocol the broker does not support fail fast at startup. **Topic IDs are mandatory:** "The new consumer rebalance protocol works only with topic ids and the OffsetFetch and OffsetCommit APIs are updated to use topic ids as well." Recreating a topic yields a new topic ID, so stale offsets are not reused.

#### API Changes

- `ConsumerGroupHeartbeat` (new) — membership, assignment and liveness in one request: subscriptions, server assignor, owned partitions → target assignment, member epoch, heartbeat interval.
- `ConsumerGroupDescribe` (new) — group state, member assignments, epochs, assignor.
- `OffsetCommit` / `OffsetFetch` v9 — topic IDs, `GenerationIdOrMemberEpoch` + `MemberId` for fencing.
- `ListGroups` — new `TypesFilter` (consumer / classic).

### Part B — Kafka 4.3 docs: Operations → Consumer Rebalance Protocol

The Next Generation Consumer Rebalance Protocol (KIP-848) became generally available in Apache Kafka 4.0. It addresses scalability limitations by eliminating the global synchronization barrier of the classic protocol, reducing rebalance times through a fully incremental design. Two consumer group types now exist: groups using the new **consumer** protocol and groups using the legacy **classic** protocol.

**Server:** the protocol is enabled via the `group.version` feature flag. Key configurations: `group.consumer.heartbeat.interval.ms`, `group.consumer.session.timeout.ms`, `group.consumer.assignors` (available strategies; defaults `uniform` and `range`). Custom server assignors implement `ConsumerGroupPartitionAssignor`.

| Client-side (classic) assignor | Server-side (consumer) assignor |
|---|---|
| `RangeAssignor` | `range` |
| `CooperativeStickyAssignor` | `uniform` |
| `StickyAssignor` | `uniform` |
| `RoundRobinAssignor` | `uniform` |

**Consumer:** enable with `group.protocol=consumer`. New `subscribe` methods accept RE2J regex evaluated server-side; new metrics expose the threading model. **Unavailable** with the new protocol: `heartbeat.interval.ms`, `session.timeout.ms`, `partition.assignment.strategy`, `enforceRebalance()`.

**Upgrade / downgrade:**

- *Offline migration* — shut down all consumers, set `group.protocol=consumer`, restart; an empty group is converted automatically.
- *Online migration* — roll the new configuration out one consumer at a time; the first `consumer`-protocol member converts the group without downtime (requires classic assignors without embedded custom metadata).
- *Downgrade* — the reverse: when the last `consumer`-protocol member leaves, the group reverts to classic.

**Evolution timeline (KIP-1274):** Kafka 3.7 Early Access · Kafka 4.0 GA · Kafka 5.0 `consumer` becomes the default (classic still supported) · Kafka 6.0 clients support `consumer` only (brokers keep classic for backward compatibility).

**Current limitations:** client-side custom assignors unsupported (KAFKA-18327); rack-aware assignment incomplete (KAFKA-19387).

**Inspecting groups:** `kafka-consumer-groups.sh --list --type consumer|classic`, `kafka-consumer-groups.sh --describe --group g --state` (ASSIGNMENT-STRATEGY shows `uniform`/`range` for consumer-type groups), `kafka-groups.sh --list` (KIP-1043, all group types with TYPE / PROTOCOL columns).
