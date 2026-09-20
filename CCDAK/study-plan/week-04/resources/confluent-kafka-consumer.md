# Confluent Platform Docs — Kafka Consumer (concepts, group protocol, offset management, configuration)

> **Nguồn (official):** https://docs.confluent.io/platform/current/clients/consumer.html
> **Tuần:** 4 — Consumer chuyên sâu: group, rebalance, offset · **Loại:** Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất. Trang Confluent còn ghi `session.timeout.ms` mặc định 10 s (giá trị cũ); **Kafka ≥ 3.0 là 45 s** — dùng 45 s khi thi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `group.id` bắt buộc khi dùng `subscribe()` hoặc `commit`; **group coordinator** (1 broker) quản lý member + assignment; rebalance chia lại partition để mỗi member nhận phần cân đối.
- 2 protocol: **classic** (1 member — group leader — tính assignment) vs **consumer** (KIP-848, GA 4.0, coordinator tính assignment, "gỡ synchronization barrier, rebalance thật sự incremental"). Bật phía broker: feature `group.version=1` (`kafka-features upgrade --feature group.version=1`); phía client: `group.protocol=consumer`.
- Migration classic → consumer: **member đầu tiên join quyết định protocol của group**; 2 cách: rolling deployment (online) hoặc dừng hết rồi start lại (empty group restart).
- Offset commit policy quyết định delivery guarantee: auto commit (`enable.auto.commit=true`, mỗi **5 s**) = **at-least-once**; `commitSync()` block + retry; `commitAsync()` non-blocking, **không retry**. Giảm `auto.commit.interval.ms` → thu hẹp cửa sổ duplicate nhưng không loại bỏ.
- At-most-once = commit **trước** xử lý (và tắt retry); exactly-once = Kafka Streams / transactional producer-consumer.
- Coordinator "đá" member khi không nhận heartbeat trong session timeout; **`group.instance.id`** (static membership) giảm gián đoạn khi restart.
- Java consumer làm mọi I/O trong **thread gọi `poll()`** (foreground) → phải `poll()` đều; client librdkafka (C/C++, Python, Go, .NET) có thread nền.
- Đo lag: `kafka-consumer-groups --describe --group g` → `CURRENT-OFFSET`, `LOG-END-OFFSET`, `LAG`.
- `ConsumerRebalanceListener`: `onPartitionsRevoked` là **cơ hội cuối để `commitSync`** trước khi mất partition; `onPartitionsAssigned` sau khi nhận.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Concepts

The Kafka consumer works by issuing "fetch" requests to the brokers leading the partitions it wants to consume. The consumer offset is specified in the log with each request. The consumer receives back a chunk of log beginning from the offset position. The consumer thus has significant control over this position and can rewind it to re-consume data if desired.

A consumer group is a set of consumers which cooperate to consume data from some topics. The partitions of all the topics are divided among the consumers in the group. As new group members arrive and old members leave, the partitions are re-assigned so that each member receives a proportional share of the partitions. This is known as **rebalancing the group**. The group ID must be configured via `group.id` to use the `subscribe()` API or to commit offsets.

The main difference between the older "high-level" consumer and the new consumer is that the former depended on ZooKeeper for group management, while the latter uses a **group coordination protocol built into Kafka itself**. In this protocol, one of the brokers is designated as the group's **coordinator** and is responsible for managing the members of the group as well as their partition assignments.

### Consumer Group Protocol

Confluent Platform supports two rebalance protocols:

- **Classic** — the original protocol: one group member (the group leader) performs the partition assignment and sends it to the coordinator.
- **Consumer** — the next-generation protocol (KIP-848, **GA in Apache Kafka 4.0**): the group coordinator (broker) computes assignments. "The consumer rebalance protocol improves consumer group scalability by removing the group-wide synchronization barrier, making rebalancing truly incremental."

**Enabling the consumer protocol on the brokers:** the `group.version` feature flag must be at level 1, e.g.

```bash
kafka-features --bootstrap-server localhost:9092 upgrade --feature group.version=1
```

**Client:** set `group.protocol=consumer`. The **first consumer joining a group determines which protocol the group uses**; a group can therefore be migrated in two ways:

1. **Rolling deployment** — deploy the new configuration one consumer at a time; the group converts to the consumer protocol when the first upgraded member joins, while remaining classic members are still served.
2. **Empty group restart** — shut down all consumers, then restart them with the new configuration.

Limitations: client-side custom assignors are not supported with the consumer protocol; use the server-side assignors (`uniform`, `range`) via `group.remote.assignor`.

### Offset Management

After the consumer receives its assignment from the coordinator, it must determine the initial position for each assigned partition. When the group is first created, before any messages have been consumed, the position is set according to the `auto.offset.reset` policy (`earliest` / `latest`). Typically, consumption starts either at the earliest offset or the latest offset.

As a consumer in the group reads messages from the partitions assigned by the coordinator, it must **commit** the offsets corresponding to the messages it has read. If the consumer crashes or is shut down, its partitions will be re-assigned to another member, which will begin consumption from the **last committed offset** of each partition. If the consumer crashes before any offset has been committed, the consumer which takes over its partitions will use the reset policy.

"The offset commit policy is crucial to providing the message delivery guarantees needed by your application." By default, the consumer is configured to use an **automatic commit policy**, which triggers a commit on a periodic interval. The consumer also supports a commit API which can be used for manual offset management.

**Auto commit** (`enable.auto.commit=true`, default): offsets are committed periodically, every `auto.commit.interval.ms` (default **5 seconds**), from inside `poll()`. In this case Kafka provides **at-least-once** delivery: if the consumer crashes after processing but before the next auto-commit, the records since the last commit are processed again. "If you want to reduce the window for duplicates, you can reduce the auto-commit interval, but some users may want even finer control over offsets."

**Manual commit** (`enable.auto.commit=false`):

- `commitSync()` — blocks until the commit succeeds or hits a non-retriable error; **retries** retriable failures. Simple and safe; throughput suffers slightly because the poll loop pauses.
- `commitAsync()` — non-blocking, returns immediately; results delivered to an optional `OffsetCommitCallback`. It does **not retry** on failure, because a retried commit could complete after a later commit and move the position backwards; the usual pattern is `commitAsync` in the loop plus a final `commitSync` on shutdown / in `onPartitionsRevoked`.

**Delivery semantics summary**

- **At-least-once** (default): auto commit, or commit *after* processing (`commitSync` / `commitAsync`).
- **At-most-once**: commit *before* processing (and disable retries) — a crash mid-processing loses the in-flight records.
- **Exactly-once**: use Kafka Streams or the transactional producer/consumer (`isolation.level=read_committed`, `sendOffsetsToTransaction`).

### Configuration

| Property | Purpose | Default |
|----------|---------|---------|
| `bootstrap.servers` | Kafka broker addresses | Required |
| `group.id` | Consumer group identifier | Optional (required for `subscribe()` / commits) |
| `client.id` | Client identifier for logging/metrics/quotas | auto-generated |
| `group.protocol` | Rebalance protocol (`classic` / `consumer`) | `classic` |
| `group.instance.id` | Static membership identifier | null (dynamic) |
| `enable.auto.commit` | Periodic background commit | `true` |
| `auto.commit.interval.ms` | Auto-commit frequency | 5000 |
| `auto.offset.reset` | Position when no committed offset / out of range | `latest` |
| `session.timeout.ms` | Session timeout (heartbeat-based liveness) | 10 s in this page (Kafka ≥ 3.0: **45 s**) |
| `heartbeat.interval.ms` | Heartbeat frequency (≤ 1/3 session timeout) | 3 s |
| `max.poll.interval.ms` | Max time between `poll()` calls | 300 s |

**Session management.** Consumers must send heartbeats to remain group members. "If no heartbeat is received before expiration of the configured session timeout, then the coordinator will kick the member out of the group" and re-assign its partitions. Static membership via `group.instance.id` reduces disruption during restarts: a static member that returns within the session timeout keeps its assignment without a rebalance.

### Message Handling and Threading

The Java consumer performs all I/O and processing in the **foreground thread** — the thread calling `poll()`. Heartbeats are sent from a background thread, but progress (and `max.poll.interval.ms`) is tied to calling `poll()`. The consumer is not thread-safe; use `wakeup()` to interrupt it from another thread. librdkafka-based clients (C/C++, Python, Go, .NET) perform I/O in background threads, which makes multi-threaded polling patterns easier.

### Consumer Lag

Use the `kafka-consumer-groups` tool to monitor lag:

```bash
bin/kafka-consumer-groups --bootstrap-server host:9092 --describe --group test-1234
```

The output includes, per partition, `CURRENT-OFFSET` (last committed), `LOG-END-OFFSET` and the computed `LAG` (difference between the two).

### Rebalance Listeners

Implement `ConsumerRebalanceListener` and pass it to `subscribe(topics, listener)` to handle partition **revocation** (`onPartitionsRevoked`, invoked before the rebalance completes — the final opportunity to commit offsets synchronously for the partitions being taken away) and **assignment** (`onPartitionsAssigned`, invoked after the new assignment, e.g. to `seek` to an externally stored offset).
