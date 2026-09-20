# KIP-345 — Static Membership Protocol (`group.instance.id`) to Reduce Consumer Rebalances

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-345%3A+Introduce+static+membership+protocol+to+reduce+consumer+rebalances
> **Tuần:** 4 — Consumer chuyên sâu: group, rebalance, offset · **Loại:** KIP
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Released **Kafka 2.3 (broker) / 2.4 (hoàn thiện client)**; yêu cầu broker ≥ 2.3.
- **Dynamic membership** (mặc định): mỗi lần start consumer được cấp `member.id` **mới**; `close()` gửi `LeaveGroup` → **1 restart = 2 rebalance** (rời + vào lại). Rolling bounce N pod → ~2N rebalance.
- **Static membership**: đặt **`group.instance.id`** duy nhất & ổn định cho từng instance → coordinator lưu map `group.instance.id → member.id`; member **không gửi `LeaveGroup` khi shutdown**; quay lại **trong `session.timeout.ms`** thì nhận lại **cached assignment cũ, không rebalance**.
- Đi kèm phải **tăng `session.timeout.ms`** (đủ cho thời gian restart; broker nâng `group.max.session.timeout.ms` lên **30 phút**) — đổi lại **phát hiện crash chậm hơn**.
- 2 instance cùng `group.instance.id` nhưng khác `member.id` → request bị từ chối với **`FENCED_INSTANCE_ID`** (`FencedInstanceIdException`) — instance cũ bị fence.
- Gỡ static member offline mà không chờ session timeout: Admin API **`removeMembersFromConsumerGroup`** (hoặc `kafka-consumer-groups.sh`) → rebalance ngay.
- Static + dynamic member **có thể cùng tồn tại** trong 1 group. Downgrade: bỏ `group.instance.id`, giảm session timeout, rolling bounce. `group.instance.id` được ghi vào `__consumer_offsets` để coordinator failover không mất.
- Bẫy đề: "muốn restart pod không gây rebalance" → **`group.instance.id` + session timeout dài**, không phải `assign()`, không phải tăng `max.poll.interval.ms`. Với KIP-848 (`group.protocol=consumer`) static membership vẫn dùng được (member epoch -2 khi tạm rời).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Status

Accepted; released in Apache Kafka **2.3** (broker support, `group.instance.id`) with remaining client/admin pieces in **2.4**.

### Motivation

The KIP addresses two performance problems caused by the current (dynamic) group membership:

1. **Heavy-state applications.** For applications such as Kafka Streams with large local state, every rebalance may shuffle partitions (and therefore state) between instances. At scale, state shuffling causes severe performance degradation and long recovery.
2. **Rolling bounces.** A normal process restart triggers **unnecessary rebalances**: the member leaves (`LeaveGroup`) and later re-joins with a new identity, so each bounced instance causes two rebalances. The goal is a **constant number of rebalances** (e.g. only for a leader restart) for an entire rolling bounce.

### Static vs. Dynamic Membership

- **Dynamic membership** (existing): prioritizes *liveness*. Each time a consumer starts it receives a fresh `member.id` from the coordinator; a leaving member triggers an immediate rebalance so that its partitions can be redistributed quickly.
- **Static membership** (proposed): prioritizes *stability of state*. A consumer keeps a persistent identity across restarts via `group.instance.id`. Temporary unavailability (restart, short network partition) does **not** trigger a rebalance as long as the member returns within the session timeout.

### New Configuration

**Consumer config `group.instance.id`**

- Default `null` → the consumer is a **dynamic** member (existing behavior).
- Non-null → the consumer is a **static** member. The user is responsible for making the value **unique per instance** within the group (e.g. derived from the pod / host name).

### Client-Side Changes

- `group.instance.id` is added to `JoinGroup`, `SyncGroup`, `Heartbeat` and `OffsetCommit` requests.
- `LeaveGroupRequest` is extended to carry a list of member identities (`group.instance.id` + `member.id`) so that an admin can remove several members at once.
- **Static members do not send `LeaveGroup` on shutdown.** A rebalance is only triggered if the member does not come back before `session.timeout.ms` expires (or when an admin removes it explicitly).
- New error `FENCED_INSTANCE_ID` (`FencedInstanceIdException`): returned when a request carries a known `group.instance.id` with a **different** `member.id` — i.e. a duplicate instance ID. The older instance is fenced and must shut down.

### Server-Side Changes

- The group coordinator keeps an in-memory mapping **`group.instance.id → member.id`**, persisted in `__consumer_offsets` for fail-over.
- **Join logic:** a known static member re-joining (same `group.instance.id`) gets its **cached assignment returned without triggering a rebalance**; an unknown `group.instance.id` receives a newly generated `member.id`. Requests with a mismatched `member.id` are rejected with `FENCED_INSTANCE_ID`.
- **Session timeout:** the broker-side upper bound (`group.max.session.timeout.ms`) is raised to **30 minutes (1800000 ms)** so that static members can use a relaxed liveness window.

### Administrative Operations

New Admin API **`removeMembersFromConsumerGroup(groupId, options)`** lets operators:

- batch-remove offline static members (by `group.instance.id`) without waiting for the session timeout;
- trigger an immediate rebalance (e.g. permanent scale-down).

Exposed through `kafka-consumer-groups.sh`; deleting the whole group (`--delete`) still requires the group to be empty.

### Configuration Recommendations

1. Give every consumer instance a unique, **stable** `group.instance.id`.
2. Increase `session.timeout.ms` to cover the expected restart / redeploy window (the historical default of 10 s is far too aggressive for this purpose; the current default is 45 s). Trade-off: a genuinely dead static member is only detected after this timeout.
3. Ensure brokers run a version supporting the new protocol versions (≥ 2.3).

### Compatibility

- Static and dynamic members can **coexist** in the same group.
- Downgrade path: unset `group.instance.id`, lower `session.timeout.ms`, rolling bounce.
- No behavior change for existing dynamic-membership deployments.

### Non-Goals

Leader re-join handling for subscription changes is addressed separately (KAFKA-7728).
