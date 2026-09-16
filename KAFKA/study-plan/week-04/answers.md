# ✅ Answers & Explanations — Week 4: Consumer Deep Dive

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../KAFKA-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-A · 4-B · 5-C · 6-D · 7-BD · 8-AC · 9-B · 10-C · 11-BD · 12-A · 13-C · 14-B · 15-A · 16-D · 17-AC · 18-B · 19-C · 20-BE · 21-A · 22-C · 23-B · 24-AD · 25-B · 26-D · 27-AC · 28-A · 29-C · 30-BD

---

### Question 1 — Answer: **B**

- **Why correct:** `fetch.min.bytes` (default **1**) tells the broker to hold the fetch response until at least that many bytes are available, and `fetch.max.wait.ms` (default **500**) caps how long it may wait. Setting them to 65536 and 1000 expresses exactly "wait for 64 KB, but never more than 1 second" and collapses thousands of tiny fetches into a few large ones.
- **Why the others are wrong:** A — `max.partition.fetch.bytes` (default 1 MB) is an upper bound per partition, not a minimum trigger, and `request.timeout.ms` is the client-side RPC timeout. C — `fetch.max.bytes` (default 50 MB) is also an upper bound; `max.poll.interval.ms` is the processing liveness clock and has nothing to do with fetching. D — `max.poll.records` only slices the internal buffer, and `heartbeat.interval.ms` concerns group liveness.
- 🧠 **Key point / trap:** the only two knobs that make the broker **wait** are `fetch.min.bytes` and `fetch.max.wait.ms`. Every other fetch config is a ceiling.
- 📎 Source: `resources/kafka-consumer-configs.md` (fetch group: 1 / 500 / 50 MB / 1 MB).

### Question 2 — Answer: **C**

- **Why correct:** `max.poll.records` operates entirely on the client side. The fetcher pulls batches from the broker according to `fetch.max.bytes` and `max.partition.fetch.bytes`, stores them in an internal buffer, and `poll()` hands the application at most `max.poll.records` of them. Network traffic is therefore unchanged.
- **Why the others are wrong:** A — it is a consumer config, not a broker config. B — 500 is the default, not a minimum; any positive value is allowed. D — it applies regardless of the auto-commit setting.
- 🧠 **Key point / trap:** `max.poll.records` shapes the **processing loop** (and thus how long one iteration takes relative to `max.poll.interval.ms`), never the fetch request size.
- 📎 Source: `resources/kafka-consumer-configs.md` (`max.poll.records` 500 limits records returned to the application only).

### Question 3 — Answer: **A**

- **Why correct:** the coordinator for a group is the broker hosting the **leader replica** of the `__consumer_offsets` partition selected by `hash(group.id) % numPartitions`, where the internal topic has **50** partitions by default. Different groups therefore spread their coordinators across the cluster.
- **Why the others are wrong:** B — the KRaft controller manages cluster metadata, not consumer groups. C — under the classic protocol a consumer can be the **group leader** (it computes the assignment), which is a different role from the coordinator; under KIP-848 even that role disappears. D — no such rule; that would make one broker a bottleneck for every group.
- 🧠 **Key point / trap:** distinguish **group coordinator** (a broker) from **group leader** (a consumer, classic protocol only) from **cluster controller** (KRaft).
- 📎 Source: `resources/confluent-consumer-group-protocol-course.md` (coordinator selection, 50 partitions).

### Question 4 — Answer: **B**

- **Why correct:** in the classic protocol the coordinator picks one member as group leader (typically the first to send `JoinGroup`) and forwards every member's subscription to it. The leader runs the configured `partition.assignment.strategy` locally and returns the assignment in `SyncGroup`; the coordinator then distributes each member's share.
- **Why the others are wrong:** A — broker-side assignment with `group.remote.assignor` is the **KIP-848** (`group.protocol=consumer`) behaviour, not classic. C — `__cluster_metadata` holds cluster metadata, not group assignments. D — assignment is computed once by one member, not independently by each.
- 🧠 **Key point / trap:** "who computes the assignment" is the single cleanest way to tell the two protocols apart: **client (group leader)** = classic, **broker (coordinator)** = KIP-848.
- 📎 Source: `resources/kip-848-consumer-rebalance-protocol.md` (problems of the client-side leader) and `resources/confluent-consumer-group-protocol-course.md`.

### Question 5 — Answer: **C**

- **Why correct:** the default strategy list is `[RangeAssignor, CooperativeStickyAssignor]`, so a group of identical members runs **Range**. Range assigns each topic independently, in partition order, giving any remainder to the first consumers. With 4 partitions and 3 consumers the split per topic is 2/1/1, and because it repeats identically for all 4 topics the first consumer accumulates 8 partitions while the others get 4. `RoundRobinAssignor` or `CooperativeStickyAssignor` spreads all 16 partitions globally instead.
- **Why the others are wrong:** A — the `uniform` server-side assignor only exists with `group.protocol=consumer`, which is not the default. B — members exceeding `max.poll.interval.ms` would be removed and the count would fluctuate, not stay stable at 8/4/4. D — `group.initial.rebalance.delay.ms` only delays the first rebalance; it does not create a permanent skew.
- 🧠 **Key point / trap:** persistent, reproducible imbalance across **many topics with the same partition count** is the signature of `RangeAssignor`. Range is kept as the default because it co-locates same-numbered partitions, which matters for co-partitioned joins.
- 📎 Source: `resources/confluent-consumer-group-protocol-course.md` (assignor comparison).

### Question 6 — Answer: **D**

- **Why correct:** eager and cooperative members cannot safely coexist, so the upgrade is a **two-bounce** procedure. Bounce 1 sets `[CooperativeStickyAssignor, RangeAssignor]` everywhere: the group still negotiates the common protocol (eager via Range) but every member now supports cooperative. Bounce 2 removes `RangeAssignor`, and the group switches to `COOPERATIVE` with no downtime.
- **Why the others are wrong:** A — a single bounce means members with only the cooperative assignor coexist with members that still revoke everything, which can leave two consumers owning the same partition. B — `group.remote.assignor` belongs to KIP-848 and takes different values; brokers are not restarted for this. C — this works but violates the "without stopping the whole group" requirement.
- 🧠 **Key point / trap:** with the Kafka 4.3 default list, `CooperativeStickyAssignor` is **already present**, so in practice you only need the bounce that removes `RangeAssignor`.
- 📎 Source: `resources/kip-429-incremental-cooperative-rebalance.md` (two rolling bounces; default list in 4.3).

### Question 7 — Answer: **B, D**

- **Why correct:** B describes eager rebalancing precisely: every member revokes its entire assignment before rejoining, which is the stop-the-world behaviour. D describes the cooperative protocol: the assignment converges over two consecutive rebalances, only partitions that change owner are revoked in the first, and untouched partitions keep being processed throughout.
- **Why the others are wrong:** A — inverted; revoking only the partitions that move is the cooperative behaviour. C — cooperative requires `CooperativeStickyAssignor`; plain `StickyAssignor` uses the EAGER protocol (it only delays state cleanup). E — cooperative rebalancing exists in the **classic** protocol from Kafka 2.4; KIP-848 is a separate, later redesign.
- 🧠 **Key point / trap:** `StickyAssignor` ≠ `CooperativeStickyAssignor`. Only the latter reports `RebalanceProtocol.COOPERATIVE`.
- 📎 Source: `resources/kip-429-incremental-cooperative-rebalance.md`.

### Question 8 — Answer: **A, C**

- **Why correct:** with `group.protocol=consumer` the broker owns failure detection and assignment, so `session.timeout.ms`, `heartbeat.interval.ms` and `partition.assignment.strategy` are ignored; the equivalents are group configs on the broker (`consumer.session.timeout.ms` default **45000**, `consumer.heartbeat.interval.ms` default **5000**). `max.poll.interval.ms` remains a genuine client concern — it bounds how long application code may take between polls — so it still applies (C).
- **Why the others are wrong:** B — the ignored settings do not cause a startup failure; they are silently unused, which is exactly why this trips teams up. D — heartbeats now flow through `ConsumerGroupHeartbeat` at the broker-dictated interval. E — client assignors are not transferred to the broker; the server-side assignors are `uniform` and `range`, chosen with `group.remote.assignor`.
- 🧠 **Key point / trap:** the dangerous part is that the ignored configs fail **silently**. Remember the split: liveness-of-the-member moves to the broker, liveness-of-the-application (`max.poll.interval.ms`) stays on the client.
- 📎 Source: `resources/kip-848-consumer-rebalance-protocol.md` (ignored client configs, broker group configs).

### Question 9 — Answer: **B**

- **Why correct:** the next-generation protocol is selected with `group.protocol=consumer`, and the server-side assignor that balances evenly while keeping assignments sticky is `uniform`, which is also the default when `group.remote.assignor` is unset.
- **Why the others are wrong:** A — this stays on the classic protocol. C — `partition.assignment.strategy` is ignored under the new protocol. D — there is no `incremental` protocol value and no `sticky` server-side assignor; the two valid server-side assignors are `uniform` and `range`.
- 🧠 **Key point / trap:** two valid values for `group.protocol` (`classic`, `consumer`) and two for `group.remote.assignor` (`uniform`, `range`). Anything else in an option is a distractor.
- 📎 Source: `resources/kip-848-consumer-rebalance-protocol.md` (server-side assignors).

### Question 10 — Answer: **C**

- **Why correct:** static membership (KIP-345) gives each instance a stable `group.instance.id`. The coordinator then remembers the mapping to its member id, the consumer does **not** send `LeaveGroup` on shutdown, and if it returns within `session.timeout.ms` it receives its previous assignment with no rebalance at all. Raising `session.timeout.ms` to cover the restart window is the required companion change (brokers allow up to 30 minutes via `group.max.session.timeout.ms`).
- **Why the others are wrong:** A — auto-commit affects offsets, not membership; the rebalances still happen. B — `max.poll.interval.ms` bounds processing time, not restart time. D — `assign()` removes rebalances but also removes automatic failover and rebalancing entirely, so a dead pod's partitions would simply stop being consumed.
- 🧠 **Key point / trap:** the trade-off is explicit — a long session timeout means **genuine crashes are detected more slowly**.
- 📎 Source: `resources/kip-345-static-membership.md`.

### Question 11 — Answer: **B, D**

- **Why correct:** heartbeats are healthy, so the failing clock is `max.poll.interval.ms` (default **300000** = 5 minutes) while a batch takes 7 minutes. Either shrink the work per iteration so the loop returns in time (B, fewer records per poll) or raise the limit above the worst-case batch duration (D). Both attack the root cause; in production they are usually combined.
- **Why the others are wrong:** A — `session.timeout.ms` governs the heartbeat thread, which is already fine; raising it does not stop the member from leaving because of a slow poll loop. C — more frequent heartbeats change nothing for the same reason. E — enabling auto-commit does not move commits to the heartbeat thread and would not prevent the eviction.
- 🧠 **Key point / trap:** "heartbeats OK but kicked out anyway, then `CommitFailedException`" always points at `max.poll.interval.ms`, never at the session timeout.
- 📎 Source: `resources/kafka-consumer-configs.md` (two liveness clocks) and `resources/kafka-consumer-javadoc.md`.

### Question 12 — Answer: **A**

- **Why correct:** these are the Kafka 4.3 defaults: `session.timeout.ms` **45000** (raised from 10000 in 3.0), `heartbeat.interval.ms` **3000**, `max.poll.interval.ms` **300000**, `max.poll.records` **500**, `auto.offset.reset` **latest**.
- **Why the others are wrong:** B — 10000 is the pre-3.0 session timeout and the default reset is `latest`, not `earliest`. C — heartbeat 15000, poll interval 60000 and 1000 records are all invented values. D — 30000 is not the session timeout default and `none` is not the default reset policy.
- 🧠 **Key point / trap:** older courses and exam dumps still print `session.timeout.ms=10000`. Anchor on **45 s / 3 s / 5 min / 500 / latest**.
- 📎 Source: `resources/kafka-consumer-configs.md`.

### Question 13 — Answer: **C**

- **Why correct:** the message text says the consumer is no longer part of an active group. That happens when the gap between two `poll()` calls exceeds `max.poll.interval.ms`: the client proactively leaves the group, its partitions are reassigned, and the later `commitSync()` is rejected because those partitions now belong to someone else.
- **Why the others are wrong:** A — offset retention expiry affects an **empty** group over days, and produces a reset to `auto.offset.reset`, not this exception. B — `isolation.level` controls which records are visible to the consumer; it never blocks offset commits. D — `assign()` consumers can commit offsets; they simply do not rebalance, and the exception text explicitly mentions "auto partition assignment".
- 🧠 **Key point / trap:** `CommitFailedException` is almost always a **rebalance** symptom. Fix the poll loop duration, do not retry the commit.
- 📎 Source: `resources/kafka-consumer-javadoc.md` (failure detection, manual commit).

### Question 14 — Answer: **B**

- **Why correct:** a committed offset is the offset the consumer will **read next**, not the last one it processed. Having finished offset 41, it must commit **42**; otherwise record 41 is delivered again after a restart.
- **Why the others are wrong:** A — committing 41 replays record 41. C — committing 40 replays records 40 and 41. D — metadata is a free-form string for the application; it does not change the offset semantics, and 41 is still the wrong number.
- 🧠 **Key point / trap:** the rule is **commit = last processed offset + 1**. This is one of the most frequently tested details of the consumer API.
- 📎 Source: `resources/kafka-consumer-javadoc.md` (position vs committed position).

### Question 15 — Answer: **A**

- **Why correct:** auto-commit runs during `poll()` and only commits offsets that were returned by **previous** polls. Crashing 3 seconds after a commit means the records handed out since then were processed but their offsets were never stored, so the restarted consumer replays them. This is the textbook at-least-once outcome.
- **Why the others are wrong:** B — auto-commit does not commit before processing; a commit for the current batch happens on the next `poll()`, after processing. C — auto-commit is never exactly-once. D — `auto.offset.reset` is irrelevant because committed offsets exist.
- 🧠 **Key point / trap:** default consumer behaviour is **at-least-once**, so downstream effects must be idempotent. You only get at-most-once by deliberately committing before processing.
- 📎 Source: `resources/confluent-kafka-consumer.md` (commit policy determines delivery guarantee).

### Question 16 — Answer: **D**

- **Why correct:** commits are asynchronous and can complete out of order. If a failed commit for offset 100 were retried automatically, it could land after a successful commit for offset 200 and move the committed position backwards, causing a large replay. `commitSync()` blocks until completion, so ordering is guaranteed and retrying a retriable error is safe.
- **Why the others are wrong:** A — `commitAsync()` works with `subscribe()` as well. B — no such broker behaviour. C — `commitAsync()` does surface exceptions, through its `OffsetCommitCallback`.
- 🧠 **Key point / trap:** the standard pattern is `commitAsync()` in the loop for throughput plus a final `commitSync()` on shutdown, which is exactly what Question 17 asks about.
- 📎 Source: `resources/confluent-kafka-consumer.md` (`commitAsync` does not retry).

### Question 17 — Answer: **A, C**

- **Why correct:** A keeps the poll loop fast because asynchronous commits do not block. C closes the two gaps that A leaves open: a `commitSync()` in a `finally` block at shutdown, and one inside `onPartitionsRevoked()` before partitions move to another member, so the last processed offsets are durable in both cases. Together they give at-least-once with no loss and good throughput.
- **Why the others are wrong:** B — committing before processing turns the application into at-most-once, which loses messages. D — a `KafkaConsumer` is **not thread-safe**; committing from another thread is unsafe. E — retrying the same offset from an async callback re-introduces exactly the out-of-order overwrite that Question 16 describes.
- 🧠 **Key point / trap:** remember the pair — **`commitAsync()` while running, `commitSync()` when stopping or losing partitions**.
- 📎 Source: `resources/kafka-consumer-javadoc.md` (rebalance listener, manual commit) and `resources/confluent-kafka-consumer.md`.

### Question 18 — Answer: **B**

- **Why correct:** `auto.offset.reset` is a fallback, consulted only when the group has **no valid committed offset** for a partition or the stored offset is out of range. A long-running group like `analytics` has committed offsets, so the consumer resumes from them and the setting is never used.
- **Why the others are wrong:** A — the two settings are independent. C — `auto.offset.reset` applies to `subscribe()` consumers as well; it is not restricted to `assign()`. D — `log.retention.hours` is a broker log setting and does not override a client policy.
- 🧠 **Key point / trap:** to actually reprocess from the beginning you must either use a **new `group.id`** or reset the existing group's offsets with the CLI (Question 24).
- 📎 Source: `resources/kafka-consumer-configs.md` (`auto.offset.reset` applies only without a committed offset).

### Question 19 — Answer: **C**

- **Why correct:** the broker expires committed offsets for groups that have been empty longer than `offsets.retention.minutes`, whose default is **10080 minutes = 7 days**. A group that only runs monthly is empty for about 30 days, so its offsets are gone by the next run; with no committed offset the consumer falls back to `auto.offset.reset`, which defaults to `latest`, and the month of data is skipped.
- **Why the others are wrong:** A — committed offsets always win when they exist; that is the point of Question 18. B — `log.retention.hours` governs topic data, not the offsets in `__consumer_offsets`. D — offsets live in the `__consumer_offsets` topic on the brokers, not on the consumer's disk.
- 🧠 **Key point / trap:** the fix is to raise `offsets.retention.minutes`, keep a member alive, or set `auto.offset.reset=earliest` for this workload. Note the interaction of **two independent retentions**: 7 days for offsets, 7 days by default for log data.
- 📎 Source: `resources/kafka-consumer-configs.md` and Week 4 `README.md` (offset retention).

### Question 20 — Answer: **B, E**

- **Why correct:** `assign()` is manual partition assignment: no group coordination, no rebalancing, and the consumer keeps exactly the partitions it was given (B). Because nothing watches the topic for it, partitions added later are not picked up automatically; the application must discover them, for example with `partitionsFor()`, and call `assign()` again (E).
- **Why the others are wrong:** A — it does not join the group protocol even though `group.id` is set. C — offsets can still be committed; `group.id` is what makes commits possible. D — `assign()` and `subscribe()` are mutually exclusive on one consumer instance; mixing them throws `IllegalStateException`.
- 🧠 **Key point / trap:** `assign()` gives you determinism and loses you failover. Also remember that consumer lag tooling, which reads group metadata, cannot report lag for `assign()` consumers.
- 📎 Source: `resources/kafka-consumer-javadoc.md` (manual partition assignment).

### Question 21 — Answer: **A**

- **Why correct:** `onPartitionsRevoked()` runs **before** the new assignment takes effect and receives exactly the partitions that are about to be taken away. Committing there means the new owner starts from the last processed offset, which minimizes duplicates.
- **Why the others are wrong:** B — `onPartitionsAssigned()` runs too late; the other member may already be consuming. C — `onPartitionsLost()` is the path for partitions lost **without** a clean revoke (the member was fenced), so a commit there typically fails; it is meant for cleaning up local state. D — the new owner has no knowledge of what the previous owner processed.
- 🧠 **Key point / trap:** with cooperative rebalancing, `onPartitionsRevoked()` receives **only the partitions that actually move**, not the whole assignment.
- 📎 Source: `resources/kip-429-incremental-cooperative-rebalance.md` (listener semantics).

### Question 22 — Answer: **C**

- **Why correct:** `isolation.level=read_committed` makes the consumer skip aborted records and, crucially, stop at the **Last Stable Offset**: records belonging to a transaction that is still open are withheld until that transaction commits or aborts. That is the visible-end side effect the question asks about.
- **Why the others are wrong:** A — `enable.idempotence` is a producer setting. B — `read_uncommitted` is indeed the default but it returns aborted records rather than filtering them. D — `transactional.id` is a producer setting; consumers never fence producers.
- 🧠 **Key point / trap:** `read_committed` trades latency for correctness. A long-running transaction stalls the LSO and therefore stalls those consumers, which shows up as growing lag with an idle-looking topic.
- 📎 Source: `resources/kafka-consumer-configs.md` (`isolation.level`) and Week 3 `README.md` (transactions, LSO).

### Question 23 — Answer: **B**

- **Why correct:** the tool computes `LAG = LOG-END-OFFSET − CURRENT-OFFSET`, where `CURRENT-OFFSET` is the group's **committed** offset. Here 1850 − 1200 = **650** records are not yet accounted for by a commit.
- **Why the others are wrong:** A — 1850 is the end of the log, not the backlog, and a `CURRENT-OFFSET` of 1200 proves commits did happen. C — `CURRENT-OFFSET` is a position, not a count of unconsumed records. D — a `CONSUMER-ID` is present, so a member owns the partition; the group is active.
- 🧠 **Key point / trap:** this tool-side lag is based on **committed** offsets, while the client metric `records-lag-max` is based on the consumer's current **position**. The two legitimately differ, which is a classic source of confusion between Grafana and the CLI.
- 📎 Source: `resources/kafka-ops-consumer-groups-share-groups.md` (LAG formula) and Week 8 `resources/confluent-consumer-lag.md`.

### Question 24 — Answer: **A, D**

- **Why correct:** `--reset-offsets` is a dry run unless `--execute` is supplied, so the command only printed what it would do (A). It also refuses to change anything while the group has active members, because two writers of the same committed offset would race; every consumer must be stopped first (D).
- **Why the others are wrong:** B — `--to-earliest` is one of the eight valid scenarios. C — the CLI is a supported way to reset offsets, and it uses the Admin API underneath. E — `--topic` and `--all-topics` are alternatives; requiring both is invented.
- 🧠 **Key point / trap:** two preconditions, both tested often: **group inactive** and **`--execute`**. Use `--export` first if you want a rollback file.
- 📎 Source: `resources/kafka-ops-consumer-groups-share-groups.md` (reset scenarios and preconditions).

### Question 25 — Answer: **B**

- **Why correct:** `wakeup()` is the only `KafkaConsumer` method that is safe to call from another thread. It makes the in-flight `poll()` throw `WakeupException`, which the poll thread catches to commit any pending offsets and call `close()` in a `finally` block — a clean, race-free shutdown.
- **Why the others are wrong:** A — `close()` from a foreign thread violates the consumer's threading contract and throws `ConcurrentModificationException`. C — `unsubscribe()` and `commitSync()` are equally unsafe from another thread. D — `pause()` has the same threading problem and does not terminate the loop.
- 🧠 **Key point / trap:** "`KafkaConsumer` is not thread-safe; `wakeup()` is the single exception" is a standing exam fact.
- 📎 Source: `resources/kafka-consumer-javadoc.md` (multi-threading section).

### Question 26 — Answer: **D**

- **Why correct:** the requirements are more consumers than partitions, per-record acknowledgement, automatic redelivery after a timeout and no ordering guarantee. That is exactly the share group model introduced by KIP-932 and generally available in Kafka 4.2: several `KafkaShareConsumer` instances cooperate on the **same** partition, each record is acquired under a lock and acknowledged individually as ACCEPT, RELEASE or REJECT.
- **Why the others are wrong:** A and B — in any consumer group a partition is owned by at most one member, so 24 of the 30 instances would sit idle and acknowledgement is per-partition offset, not per record. C — raising the topic to 30 partitions is a costly workaround that still gives no per-record acknowledgement or redelivery, and `assign()` removes failover.
- 🧠 **Key point / trap:** the keyword cluster "queue semantics / more workers than partitions / per-message ack / redelivery" maps to **share groups**, which is Kafka's answer to the SQS-style workload you know from AWS.
- 📎 Source: `resources/kafka-ops-consumer-groups-share-groups.md` (share group tooling) and Week 2 `resources/kafka-share-groups.md`.

### Question 27 — Answer: **A, C**

- **Why correct:** an acquired record is locked for `group.share.record.lock.duration.ms`, default **30000 ms**; if the consumer does not acknowledge before the lock expires the record becomes available for redelivery (A). A record that has been delivered up to the delivery-count limit (default **5**) without being accepted is archived and no longer delivered (C).
- **Why the others are wrong:** B — share groups explicitly give up strict per-partition ordering; that is the price of letting several consumers share a partition. D — share consumers acknowledge individual records; they do not commit one offset per partition, which is why `kafka-share-groups.sh --describe` shows `START-OFFSET` and `LAG` but no `CURRENT-OFFSET`. E — share groups reached general availability in **4.2** (early access 4.0, preview 4.1), not 3.7.
- 🧠 **Key point / trap:** the lock duration is the share-group analogue of the SQS visibility timeout, and the delivery-count limit is its analogue of `maxReceiveCount`.
- 📎 Source: Week 2 `resources/kafka-share-groups.md` (`group.share.*` configs) and `resources/kafka-ops-consumer-groups-share-groups.md`.

### Question 28 — Answer: **A**

- **Why correct:** follower fetching (KIP-392) needs all three pieces: `broker.rack` so brokers declare their zone, `replica.selector.class=RackAwareReplicaSelector` so the broker can choose a replica for the client, and `client.rack` on the consumer so it advertises its own zone. The consumer is then served by an in-sync replica in `az-b` and cross-zone traffic disappears.
- **Why the others are wrong:** B — `fetch.from.follower` is not a Kafka configuration. C — `group.remote.assignor` distributes partitions among members; it knows nothing about zones. D — `isolation.level` controls transactional visibility only.
- 🧠 **Key point / trap:** followers serve **reads** here, but producers always write to the **leader**. Follower fetching reduces cost, not write latency.
- 📎 Source: `resources/kafka-consumer-configs.md` (`client.rack`, KIP-392).

### Question 29 — Answer: **C**

- **Why correct:** since Kafka 3.0 `enable.idempotence` defaults to **true**, and the idempotent producer requires `acks=all`, `retries > 0` and `max.in.flight.requests.per.connection` **≤ 5** so the broker can deduplicate by sequence number while preserving order. Requesting 8 in-flight requests contradicts that and the producer refuses to start.
- **Why the others are wrong:** A — values above 5 are legal if you explicitly set `enable.idempotence=false`, so the limit is not unconditional. B — `acks=all` does not by itself force a single in-flight request; that was the old advice for **non**-idempotent producers that needed ordering. D — `linger.ms` is unrelated to in-flight limits.
- 🧠 **Key point / trap:** the constraint set is `acks=all` + `retries > 0` + `max.in.flight ≤ 5`. Under the old defaults (`acks=1`, idempotence off) this configuration would have started fine, which is why older material disagrees.
- 📎 Source: Week 3 `resources/producer-configs.md` and Week 3 `README.md` (idempotence constraints).

### Question 30 — Answer: **B, D**

- **Why correct:** with `replication.factor=3` and one broker down the ISR holds 2 replicas, which still satisfies `min.insync.replicas=2`, so writes succeed. After the second failure the ISR drops to 1, below the minimum, and the leader rejects `acks=all` writes with `NotEnoughReplicasException` (B). A producer using `acks=1` only needs the leader to persist the record, so it keeps writing — at the cost of losing data if that leader also fails (D).
- **Why the others are wrong:** A — this is exactly what stops working; `min.insync.replicas` is evaluated on every `acks=all` write. C — reads continue normally; consumers read up to the high watermark and are unaffected by the minimum-ISR rule. E — `min.insync.replicas` is a static configuration and is never lowered automatically.
- 🧠 **Key point / trap:** `min.insync.replicas` only has teeth together with `acks=all`. The classic production triple RF=3 / min.isr=2 / acks=all survives exactly **one** broker failure without losing availability for writes.
- 📎 Source: Week 2 `resources/kafka-replication-isr.md` (acks and min.insync.replicas matrix).

---

> ✅ Logged every wrong answer? Group them by topic (fetch tuning, rebalance protocols, offset semantics, share groups) and re-read the matching section of the [week plan](README.md) before attempting the **FUND + DEV mini-mock**. The checkpoint to clear Week 4 is **≥ 70%**.
