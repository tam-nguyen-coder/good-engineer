# Confluent Developer — Apache Kafka Architecture course: *Consumer Group Protocol*

> **Nguồn (official):** https://developer.confluent.io/courses/architecture/consumer-group-protocol/
> **Tuần:** 4 — Consumer chuyên sâu: group, rebalance, offset · **Loại:** Confluent Docs (Confluent Developer course)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc (có video) để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kafka tách **storage (broker)** và **compute (consumer)**; **đơn vị song song là partition** → số consumer active tối đa = số partition; consumer dư sẽ **idle**.
- Group coordinator = broker giữ **leader replica** của partition `hash(group.id) % số partition __consumer_offsets` (**50**).
- Khởi động group (classic): **`FindCoordinator`** → **`JoinGroup`** (kèm subscription; coordinator chọn **group leader**, thường member đầu) → leader chạy assignor → **`SyncGroup`** (leader gửi assignment, coordinator trả cho mọi member).
- Assignor: **Range** (theo từng topic, partition 0 của mọi topic về consumer đầu → tiện join co-partition, dễ lệch), **RoundRobin** (rải đều mọi partition), **Sticky** (RoundRobin + cố giữ assignment cũ), **CooperativeSticky** (2 bước, chỉ revoke partition cần thiết).
- Tiến độ: `OffsetCommitRequest` → `__consumer_offsets`; restart → `OffsetFetchRequest`; không có offset → `auto.offset.reset` (earliest/latest).
- Rebalance kích hoạt khi: member chết (mất heartbeat), member mới join, thêm partition, topic mới khớp regex subscription, khi khởi động.
- Stop-the-world: dừng toàn bộ xử lý + rebuild state vô ích khi partition quay lại chính consumer cũ. Cải tiến: **StickyAssignor** (trì hoãn dọn state), **CooperativeStickyAssignor** (chỉ revoke partition đổi chủ, phần còn lại tiếp tục), **static membership** (`group.instance.id`: không `LeaveGroup` khi tắt, quay lại trong session timeout → nhận lại assignment, **không rebalance**).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Consumer Group Protocol: Scalability and Fault Tolerance

Kafka separates storage (the brokers) from compute (the consumers). Consumer groups enable parallel processing by distributing partitions across consumer instances, where **"the unit of parallelism is the partition."** Adding consumer instances to a group increases throughput up to the number of partitions; beyond that, extra instances sit idle.

### Consumer Groups

A consumer group is defined by setting `group.id` in the consumer configuration. Once established, the partitions of the subscribed topics are **"evenly distributed between the instances in the group."** If an instance fails, its partitions are redistributed to the remaining instances (fault tolerance); if instances are added, partitions are moved to them (scalability).

### Group Coordinator

The group coordinator manages this distribution using the internal `__consumer_offsets` topic. The coordinator for a given group is **"the broker that hosts the leader replica"** of the `__consumer_offsets` partition determined by hashing the group ID. Because that topic is replicated, if the coordinator broker fails, the new leader of that partition takes over as coordinator.

### Group Startup

**Step 1 — Find the group coordinator.** A consumer sends a `FindCoordinator` request to any broker. The broker hashes the group ID against the number of `__consumer_offsets` partitions to identify the coordinator broker and returns its address.

**Step 2 — Members join.** Each consumer sends a `JoinGroup` request with its subscription information (topics, supported assignors). The coordinator designates **"one consumer, usually the first one"** as the **group leader** and returns the full membership and subscriptions to that leader only.

**Step 3 — Partitions assigned.** The group leader uses the configured assignor to distribute partitions and sends the result to the coordinator in a `SyncGroup` request; the other members send empty `SyncGroup` requests and receive their assignment in the response.

### Partition Assignment Strategies

- **Range** — assigns partitions per topic sequentially: **"the first partition of each topic will be assigned to the first consumer,"** and so on. Useful for co-locating joins across topics that share keys and partition counts, but can leave the first consumers with more partitions when several topics are subscribed.
- **Round Robin** — spreads all partitions of all topics uniformly across consumers, enabling a **"higher degree of parallelism."**
- **Sticky** — a variant of round robin that **"makes a best effort at sticking to the previous assignment during a rebalance,"** reducing partition movement.
- **Cooperative Sticky** — same balancing logic in a **two-step** process that minimizes paused processing by revoking only the partitions that actually need to move.

### Tracking Partition Consumption

Consumers track their progress by committing the last offset consumed via an `OffsetCommitRequest` to the coordinator, which stores it in `__consumer_offsets`. On restart (or when a partition is reassigned), the consumer issues an `OffsetFetchRequest` to retrieve the last committed offset and resumes from there. If no committed offset is available, `auto.offset.reset` determines the starting point (`earliest` or `latest`).

### Heartbeats and Liveness

Each consumer sends heartbeats to the coordinator on a background thread. If the coordinator does not receive a heartbeat within the session timeout, the member is considered dead and a rebalance is triggered. Separately, the consumer must keep calling `poll()` within `max.poll.interval.ms`; otherwise it leaves the group so that its partitions can be reassigned.

### Rebalance Triggers

Rebalances occur when: an instance fails (missing heartbeat), a new instance joins, partitions are added to a subscribed topic, a new topic matching a wildcard subscription is created, or on group startup.

### Stop-the-World Rebalance and Its Improvements

**Problems with the eager ("stop-the-world") approach:**

- Unnecessary state rebuilding when partitions are reassigned to the same consumer that had them.
- Complete processing pause for the whole group during the rebalance.

**Improvements:**

- **StickyAssignor** — keeps as much of the previous assignment as possible and defers state cleanup until after reassignment, avoiding needless state rebuilds.
- **CooperativeStickyAssignor** — revokes only the partitions that must move; all other partitions continue to be processed during the (two-phase) rebalance.
- **Static group membership** — avoids rebalances entirely for restarts: consumers with a static `group.instance.id` skip `LeaveGroup` on graceful shutdown and, when they rejoin within the session timeout, get their existing assignment back without a rebalance.

### Note on the next-generation protocol (KIP-848)

Newer Kafka versions (GA in 4.0) move the assignment computation from the client-side group leader to the group coordinator and replace the `JoinGroup`/`SyncGroup` round-trips with a single `ConsumerGroupHeartbeat` API, making rebalances fully incremental (see the Week 4 KIP-848 resource).
