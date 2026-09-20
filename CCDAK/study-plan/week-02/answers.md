# ✅ Answers & Explanations — Week 2: Reliability & Storage

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-BD · 4-AC · 5-C · 6-AD · 7-B · 8-D · 9-A · 10-C · 11-BE · 12-B · 13-AD · 14-AC · 15-B · 16-C · 17-D · 18-AD · 19-B · 20-AD · 21-C · 22-AC · 23-BD · 24-AD · 25-A · 26-C · 27-B · 28-D

---

### Question 1 — Answer: **B**

- **Why correct:** since Kafka 0.9 ISR membership is purely **time-based**. A follower stays in sync as long as it has fully caught up to the leader's log end offset at some point within the last `replica.lag.time.max.ms` (default **30000 ms**). A follower that is temporarily 8,000 records behind but keeps fetching and catching up is still in sync.
- **Why the others are wrong:** A — `replica.lag.max.messages` was removed in 0.9; no record-count threshold exists. C — momentary lag is normal; only lag persisting for 30 s matters. D — the controller session (`broker.session.timeout.ms`) is a second, independent condition; the leader itself removes lagging followers, so lag does affect membership.
- 🧠 **Key point / trap:** "out of sync" = "has not caught up for 30 s", never "N messages behind". The only number to remember is 30 000 ms.
- 📎 Source: `resources/kafka-replication-isr.md` (two conditions for in-sync, `replica.lag.time.max.ms`).

### Question 2 — Answer: **C**

- **Why correct:** a record is **committed** when every replica in the ISR has written it, and the **high watermark (HW)** is the minimum log end offset across the ISR. Consumers are only served records **below the HW**. With `acks=1` the leader acknowledges as soon as it has appended locally, so for a short window the leader's log end offset (LEO) is ahead of the HW and the record is invisible to consumers.
- **Why the others are wrong:** A — `fetch.min.bytes` defaults to 1 and would not hide a specific offset. B — the broker serves compressed batches as stored; no decompression step delays visibility. D — writes always go to the leader.
- 🧠 **Key point / trap:** LEO = next offset a replica will write; HW = committed offset = min(LEO over ISR); **consumers read up to HW**. With `acks=all` the ack itself implies the record is already committed, so the gap vanishes.
- 📎 Source: `resources/kafka-replication-isr.md` (committed messages, consumers only read committed data).

### Question 3 — Answer: **B, D**

- **Why correct:** with RF=3 and two brokers down the ISR is 1, which is below `min.insync.replicas=2`. `acks=all` producers get `NotEnoughReplicasException` (retriable) until the ISR recovers (B). `min.insync.replicas` gates **writes only**; the surviving leader still serves fetches up to the high watermark, and everything that was committed is on that replica (D).
- **Why the others are wrong:** A — being in the ISR is not enough; the ISR must also be ≥ `min.insync.replicas`. C — reads are never blocked by the min-ISR rule. E — the default `unclean.leader.election.enable=false` never elects outside the ISR, and here the ISR is not even empty.
- 🧠 **Key point / trap:** RF=3 + min.isr=2 + `acks=all` survives **one** broker loss with writes continuing; with **two** lost it trades availability for durability: writes stop, reads continue, nothing committed is lost.
- 📎 Source: `resources/kafka-replication-isr.md` (Availability and Durability Guarantees; `min.insync.replicas`).

### Question 4 — Answer: **A, C**

- **Why correct:** A — `min.insync.replicas` equal to the replication factor means a **single** broker restart drops the ISR to 2 < 3 and stops all `acks=all` writes; the very restart they want to survive causes an outage. C — `min.insync.replicas` is evaluated **only for `acks=all`**; a producer with `acks=1` is acknowledged by the leader alone and can lose data if that leader dies before followers fetch, so the min-ISR setting gives no protection.
- **Why the others are wrong:** B and D — `acks=all` and `acks=-1` are the same value; RF=3 / min.isr=2 / `acks=all` is the standard production triple. E — since Kafka 3.0 the client default is `acks=all` (with idempotence), so defaults are fine.
- 🧠 **Key point / trap:** two classic traps in one question: "min.isr = RF" (bulletproof but unavailable during maintenance) and "min.isr with `acks=1`" (meaningless).
- 📎 Source: `resources/kafka-replication-isr.md` (acks × min.insync.replicas matrix) and `resources/kafka-topic-configs.md` (`min.insync.replicas` applies to `acks=all`).

### Question 5 — Answer: **C**

- **Why correct:** `acks=all` means "all replicas in the **current ISR**", not "all assigned replicas". With one of two brokers down the ISR is just the leader; since 1 ≥ `min.insync.replicas=1` the write is acknowledged with a single copy. If that broker then fails, the acknowledged record is gone.
- **Why the others are wrong:** A — the ISR shrinks around failed replicas precisely so that writes can continue; `acks=all` never waits for offline replicas. B — `min.insync.replicas` applies to `acks=all`, not `acks=1`. D — `acks=all` is valid for any RF.
- 🧠 **Key point / trap:** RF=2 gives you at most **one** spare copy, and with min.isr=1 that spare is optional. Durable writes require **RF=3 + `min.insync.replicas=2`**.
- 📎 Source: `resources/kafka-replication-isr.md` (Availability and Durability Guarantees: "acks=all does not guarantee the full set of assigned replicas").

### Question 6 — Answer: **A, D**

- **Why correct:** A — the default is `false`: when the whole ISR is gone the controller waits for an ISR replica (consistency over availability). D — `true` lets an out-of-sync replica become leader, restoring availability but discarding committed records that replica never received.
- **Why the others are wrong:** B — the default is `false`. C — the config exists at both broker and topic level (`unclean.leader.election.enable` in topic configs), and a one-off unclean election can be forced with `kafka-leader-election.sh --election-type UNCLEAN`. E — it has nothing to do with the min-ISR write check.
- 🧠 **Key point / trap:** the exam phrases this as "availability vs consistency". Default = consistency (`false`). "Accept data loss to come back online" = `true`.
- 📎 Source: `resources/kafka-replication-isr.md` (Unclean leader election: what if they all die?) and `resources/kafka-topic-configs.md`.

### Question 7 — Answer: **B**

- **Why correct:** because the high watermark cannot advance while ISR size < `min.insync.replicas` ("strict min ISR"), any follower that was removed from the ISR **after** the ISR had already fallen below min.isr still holds every committed record. The controller keeps such replicas in the **ELR**. Election order with ELR enabled: (1) a replica in the ISR, (2) an unfenced replica in the ELR, (3) the last known leader if unfenced. Replica 3 is elected with no data loss.
- **Why the others are wrong:** A — that was the pre-4.0 behaviour when the ISR was empty; ELR (default on new clusters since 4.1) exists to avoid it. C — ELR does not replace or override `unclean.leader.election.enable`; it only adds safe candidates. D — the last known leader is the **last** fallback, not the first.
- 🧠 **Key point / trap:** `Elr:` and `LastKnownElr:` columns in `kafka-topics.sh --describe` are the tell. Feature flag `eligible.leader.replicas.version=1` (manual in 4.0, default from 4.1).
- 📎 Source: `resources/kafka-eligible-leader-replicas.md` (election order, strict min ISR).

### Question 8 — Answer: **D**

- **Why correct:** with ELR enabled, `min.insync.replicas` becomes a **cluster-level** config managed via `kafka-configs.sh --entity-type brokers --entity-default`. Altering or removing it at broker level is rejected, previously set broker-level values are removed, and any update to the value at cluster level (even to the same value) or at topic level **clears the ELR state** of the affected partitions.
- **Why the others are wrong:** A — broker-level alteration is explicitly disallowed and ELR state is cleared. B — dynamic cluster-level config is the documented way; no restart. C — it can be changed, just at the right level and with the ELR-reset side effect.
- 🧠 **Key point / trap:** "ELR" + "min.insync.replicas" in the same question → answer mentions **cluster-level** and **ELR reset**.
- 📎 Source: `resources/kafka-eligible-leader-replicas.md` (min.insync.replicas constraints when ELR is enabled).

### Question 9 — Answer: **A**

- **Why correct:** the **preferred leader** is the first replica in `Replicas`. After failures, leadership piles onto the surviving brokers and does not move back instantly. `auto.leader.rebalance.enable=true` (default) rebalances only when the check fires (every `leader.imbalance.check.interval.seconds` = **300 s**) and the imbalance is above `leader.imbalance.per.broker.percentage` = **10%**. `kafka-leader-election.sh --election-type PREFERRED --all-topic-partitions` forces it immediately.
- **Why the others are wrong:** B — automatic rebalance exists; reassignment changes the replica set, which is unnecessary here. C — preferred replicas are in the ISR; unclean election is unrelated. D — leadership is dynamic.
- 🧠 **Key point / trap:** "leaders did not return after restart" → preferred leader election, 300 s, `kafka-leader-election.sh`. Do **not** reach for partition reassignment.
- 📎 Source: `resources/kafka-replication-isr.md` (Replica Management, preferred leader / `auto.leader.rebalance.enable`).

### Question 10 — Answer: **C**

- **Why correct:** `broker.rack` labels each broker with its rack / zone. When the controller assigns replicas for a new topic it places the replicas of each partition on **different racks** as far as possible (a rack is reused only when all racks already hold a replica). With 3 zones and RF=3 each partition has one replica per zone, so losing a zone leaves two in-sync replicas.
- **Why the others are wrong:** A — `min.insync.replicas` controls acknowledgement, not placement. B — works but is manual and error-prone; rack awareness automates it. D — unclean election is about electing out-of-sync replicas after the fact, not about surviving without data loss.
- 🧠 **Key point / trap:** `broker.rack` = **placement** (broker side). `client.rack` + `replica.selector.class` = follower **fetching** (Week 4). Different problems.
- 📎 Source: `resources/kafka-replication-isr.md` (rack awareness in replica placement).

### Question 11 — Answer: **B, E**

- **Why correct:** B — the active segment rolls on whichever comes first: `segment.bytes` (default **1073741824**, 1 GiB) or `segment.ms` (default **604800000**, 7 days). E — the docs are explicit: "retention and cleaning is always done a file at a time". Only **closed** segments are deleted or compacted; the active segment is untouched.
- **Why the others are wrong:** A — segments hold many batches; rolling per batch would create millions of files. C — Kafka never deletes individual records by retention; a segment is deleted when its **newest** record is past `retention.ms`. D — the active segment is exempt.
- 🧠 **Key point / trap:** everything storage-related is **per segment**. That single fact explains Question 12 and why compaction labs must lower `segment.ms`.
- 📎 Source: `resources/kafka-topic-configs.md` (`segment.bytes`, `segment.ms`, `retention.ms`).

### Question 12 — Answer: **B**

- **Why correct:** a few KB per day never reaches `segment.bytes` = 1 GiB, and `segment.ms` = 7 days has not elapsed, so all records are still in the **active segment**, which retention never touches. Lowering `segment.ms` (for example to 1 hour) closes segments regularly; the deletion scan then runs every `log.retention.check.interval.ms` = **300000 ms** and removes closed segments whose newest record is older than `retention.ms`. `kafka-delete-records.sh` can also advance the log start offset immediately.
- **Why the others are wrong:** A — the log cleaner is for compaction; `delete` retention is done by the log manager scheduler and is always on. C — `retention.ms` applies to `delete` (and `compact,delete`) policies. D — consumers read from the leader by default, and replicas hold the same segments anyway.
- 🧠 **Key point / trap:** "data older than retention still readable" → **active segment not rolled yet** (+ 5-minute scan), not a bug.
- 📎 Source: `resources/kafka-topic-configs.md` (`segment.ms` description: "force the log to roll ... to ensure that retention can delete or compact old data"; `log.retention.check.interval.ms`).

### Question 13 — Answer: **A, D**

- **Why correct:** A — `retention.bytes` is the maximum size of **one partition**'s log; with 8 partitions the topic can hold about 8 GiB. D — `retention.ms=-1` removes the time limit; combining it with `retention.bytes=-1` (the default) means the data is retained indefinitely.
- **Why the others are wrong:** B — the limit is not topic-wide. C — `retention.ms=0` makes every closed segment immediately eligible for deletion, the opposite of forever. E — both limits are active at the same time; whichever is hit first triggers deletion.
- 🧠 **Key point / trap:** `retention.bytes` × number of partitions = topic footprint. `-1` = unlimited for both `retention.ms` and `retention.bytes`.
- 📎 Source: `resources/kafka-topic-configs.md` (`retention.bytes` "maximum size a partition can grow to", `retention.ms` -1).

### Question 14 — Answer: **A, C**

- **Why correct:** the documented guarantees are: a consumer that keeps up with the head sees every message; **ordering is always maintained** (A); the **offset never changes** and a read at a compacted-away offset returns the next available offset (C); and a read from the beginning sees at least the final state of every key.
- **Why the others are wrong:** B — compaction guarantees **at least** the latest value per key, not exactly one; the head (uncleaned) portion can still contain older duplicates, and cleaning only runs on closed segments once the dirty ratio is reached. D — the active segment is never compacted. E — compacted topics **require** a key; a `null`-key record is rejected by the broker.
- 🧠 **Key point / trap:** the "exactly one record per key at all times" claim is the most common wrong option. Remember "**at least** the last value".
- 📎 Source: `resources/kafka-log-compaction.md` (What guarantees does log compaction provide?).

### Question 15 — Answer: **B**

- **Why correct:** deletion in a compacted topic is a **tombstone**: the key with a **`null`** value. After compaction only the tombstone remains for that key, and it is kept for `delete.retention.ms` (default **86400000 ms**, 24 h) so that a consumer reading from offset 0 has that long to reach the head and observe the delete.
- **Why the others are wrong:** A — an empty string is a normal value; the key would keep an empty value forever. C — `kafka-delete-records.sh` truncates by **offset** (log start offset), not by key. D — with `cleanup.policy=compact` alone, `retention.ms` does not expire data.
- 🧠 **Key point / trap:** tombstone = `null` value, not `""`. 24 h is the tombstone lifetime and also the bound on how long a from-beginning consumer may take.
- 📎 Source: `resources/kafka-log-compaction.md` (tombstones, `delete.retention.ms`) and `resources/kafka-topic-configs.md`.

### Question 16 — Answer: **C**

- **Why correct:** the log cleaner only picks a log for compaction when its **dirty ratio** (uncleaned bytes / total bytes) is at least `min.cleanable.dirty.ratio`, default **0.5**. A slow topic with a large cleaned tail takes very long to become 50% dirty. Lowering the ratio (for example to 0.1) makes the cleaner run more often, at the cost of more I/O.
- **Why the others are wrong:** A — `min.compaction.lag.ms` (default 0) is the **minimum** time a record must stay uncompacted; raising it delays compaction. B — `delete.retention.ms` governs tombstone lifetime only. D — switching to `delete` abandons the "latest value per key" semantics entirely.
- 🧠 **Key point / trap:** `min.cleanable.dirty.ratio` ↓ = compact **sooner**; `min.compaction.lag.ms` ↑ = keep the head **longer**; `max.compaction.lag.ms` = deadline that forces compaction even if the ratio is not reached.
- 📎 Source: `resources/kafka-log-compaction.md` (Configuring the log cleaner) and `resources/kafka-topic-configs.md` (`min.cleanable.dirty.ratio` 0.5).

### Question 17 — Answer: **D**

- **Why correct:** `cleanup.policy=compact,delete` applies **both** mechanisms: compaction keeps the latest value per key, and time/size retention deletes whole segments once they are older than `retention.ms` (2592000000 ms = 30 days). Keys without recent updates fall out of the log entirely.
- **Why the others are wrong:** A — plain `delete` does not keep the latest value of an active session beyond 30 days. B — `compact` alone keeps the last value of every key forever. C — `delete.retention.ms` is the tombstone lifetime, not a TTL for keys.
- 🧠 **Key point / trap:** "latest per key" **and** "expire after N days" → `compact,delete`. This is also the pattern for state with a TTL.
- 📎 Source: `resources/kafka-topic-configs.md` (`cleanup.policy` accepts a comma-separated list) and `resources/kafka-log-compaction.md`.

### Question 18 — Answer: **A, D**

- **Why correct:** A — `__consumer_offsets` is compacted: each (group, topic, partition) key only needs its most recent committed offset. D — CDC / changelog topics are the textbook case: replaying a compacted topic yields the **current** row state without replaying every historical change.
- **Why the others are wrong:** B and C — these need every event, which compaction would discard; they belong to `cleanup.policy=delete` with time retention. E — compacted topics require a key, so unkeyed records are rejected.
- 🧠 **Key point / trap:** compaction = **snapshot of state** ("what is the latest value of X?"). Any "every event matters" wording rules it out.
- 📎 Source: `resources/kafka-log-compaction.md` (use cases: database change subscription, event sourcing, journaling; `__consumer_offsets`).

### Question 19 — Answer: **B**

- **Why correct:** committing the offset **before** processing means a crash mid-batch leaves the committed position past records that were never processed. On restart the consumer resumes after them, so those records are lost: **at-most-once**.
- **Why the others are wrong:** A — at-least-once requires **process first, commit after** (default auto-commit also behaves that way). C — synchronous commit changes nothing about ordering of commit vs processing. D — there is no transaction here.
- 🧠 **Key point / trap:** commit **before** processing = at-most-once (may lose); commit **after** = at-least-once (may duplicate); exactly-once needs idempotent producer + transactions + `read_committed`.
- 📎 Source: `resources/kafka-delivery-semantics.md` (consumer at-most-once vs at-least-once).

### Question 20 — Answer: **A, D**

- **Why correct:** A — Kafka's exactly-once for read-process-write between topics puts the output records **and** the input offsets in one atomic transaction (`sendOffsetsToTransaction`, or Kafka Streams `exactly_once_v2`). D — a downstream consumer must use `isolation.level=read_committed` (the Java default is `read_uncommitted`) or it would see records from aborted transactions.
- **Why the others are wrong:** B — transactions require `acks=all` (idempotence). C — offsets must be committed **inside** the transaction, so auto-commit must be off. E — compaction does not provide exactly-once; duplicates would still be visible in the head and could have different keys.
- 🧠 **Key point / trap:** exactly-once = 3 pieces: idempotent producer (dedup within a partition), **transactions** (atomic multi-partition + offsets), **`read_committed`** on the reader. Writing to an external system is outside this guarantee (Week 3).
- 📎 Source: `resources/kafka-delivery-semantics.md` (exactly-once read-process-write, `isolation.level`).

### Question 21 — Answer: **C**

- **Why correct:** Kafka guarantees ordering **within a partition only**. Keyed records are hashed (murmur2) to a partition, so every event for one `orderId` lands on the same partition in produce order while different orders spread across the 12 partitions.
- **Why the others are wrong:** A — a single partition gives total order but kills parallelism; only per-order order is required. B — `max.in.flight.requests.per.connection=1` addresses retry reordering, not the fact that `null`-key records are spread across partitions. D — compaction does not sort anything.
- 🧠 **Key point / trap:** "ordering per entity" → **key by that entity**; "total ordering" → **1 partition**. Adding partitions later remaps keys (Week 3).
- 📎 Source: Week 2 `README.md` §7 (Ordering) and `resources/kafka-delivery-semantics.md`.

### Question 22 — Answer: **A, C**

- **Why correct:** the record has to pass two gates. A — the producer refuses to serialize anything larger than `max.request.size` (default **1048576**), throwing `RecordTooLargeException` client-side. C — the broker rejects batches larger than topic `max.message.bytes` / broker `message.max.bytes` (default **1048588**, 1 MiB + 12 B record-batch overhead) with `MESSAGE_TOO_LARGE`, which the client also surfaces as `RecordTooLargeException`. Both must be raised.
- **Why the others are wrong:** B — `batch.size` is a batching target; a single record larger than it is still sent in its own batch. D — `segment.bytes` (1 GiB) is far larger than 2 MB and controls file rolling. E — `fetch.min.bytes` is a consumer wait threshold, unrelated to size limits.
- 🧠 **Key point / trap:** the four-link chain: producer `max.request.size` → topic `max.message.bytes` / broker `message.max.bytes` → follower `replica.fetch.max.bytes` → consumer `max.partition.fetch.bytes`. The last two do not block (KIP-74 returns the first batch even if oversized) but should be raised for throughput. Prefer compression or a claim-check pattern over huge records.
- 📎 Source: `resources/kafka-topic-configs.md` (`max.message.bytes` 1048588, `replica.fetch.max.bytes`) and Week 2 `README.md` §8.

### Question 23 — Answer: **B, D**

- **Why correct:** B — topic `compression.type` defaults to **`producer`**: the broker keeps the producer's codec and stores the batch as received (no recompression, CPU-cheap). D — `LogAppendTime` makes the broker stamp each record with its own clock at append time, useful when producer clocks are unreliable or when retention / time-index must follow broker time.
- **Why the others are wrong:** A — default is `producer`, not `gzip`; only an explicit codec (`gzip`, `snappy`, `lz4`, `zstd`, `uncompressed`) makes the broker recompress. C — `CreateTime` keeps the timestamp set by the **producer**. E — `message.timestamp.type` is a topic-level config (broker default `log.message.timestamp.type`).
- 🧠 **Key point / trap:** "broker CPU jumped after enabling producer compression" → topic `compression.type` was set to a codec; set it back to `producer`. "Timestamp = when the broker wrote it" → `LogAppendTime`.
- 📎 Source: `resources/kafka-topic-configs.md` (`compression.type=producer`, `message.timestamp.type`).

### Question 24 — Answer: **A, D**

- **Why correct:** A — share groups (KIP-932, early access 4.0, preview 4.1, **GA 4.2**) let multiple consumers consume the **same** partition, so consumer count is no longer bounded by partition count. D — records are acknowledged individually with `ACCEPT`, `RELEASE` (make available again) or `REJECT` (do not redeliver); there is no offset commit.
- **Why the others are wrong:** B — in a classic consumer group a partition goes to **one** member, so 16 of 20 consumers would idle. C — share groups explicitly give up per-partition ordering ("at the expense of record ordering"). E — share group state lives in the internal topic **`__share_group_state`** managed by the share coordinator, not in `__consumer_offsets`.
- 🧠 **Key point / trap:** "queue", "more consumers than partitions", "per-record ack", "no ordering needed" → share group (`kafka-console-share-consumer.sh`, `kafka-share-groups.sh`, feature `share.version=1`). Any requirement for ordering or replay → consumer group.
- 📎 Source: `resources/kafka-share-groups.md` (differences from consumer groups, acknowledgement types, `__share_group_state`).

### Question 25 — Answer: **A**

- **Why correct:** a fetched record is held under an **acquisition lock** for `group.share.record.lock.duration.ms` (default **30000 ms**, bounded 15–60 s). `RELEASE` returns it to the pool immediately for another delivery attempt; doing nothing has the same effect once the lock expires. Each delivery increments the record's delivery count; when it reaches `group.share.delivery.count.limit` (default **5**) the record is archived and never delivered again, which is how poison records stop cycling.
- **Why the others are wrong:** B — `ACCEPT` marks success; the record is never redelivered. C — `REJECT` marks the record as unprocessable and it is **not** redelivered. D — share consumers do not support `seek()`; positions are managed by the share coordinator.
- 🧠 **Key point / trap:** the two share-group numbers: **30 s** lock and **5** deliveries. `RELEASE` = "try again", `REJECT` = "give up on this one", `ACCEPT` = "done".
- 📎 Source: `resources/kafka-share-groups.md` (acquisition lock, `share.record.lock.duration.ms`, `share.delivery.count.limit`).

### Question 26 — Answer: **C**

- **Why correct:** **tiered storage** (KIP-405, GA since Kafka 3.9) copies closed segments to remote storage (S3, HDFS, ...) through a `RemoteStorageManager`. Brokers keep only `local.retention.ms` / `local.retention.bytes` worth of data locally (default **-2** = same as `retention.*`), while total retention follows `retention.ms`. Enable per topic with `remote.storage.enable=true` (broker: `remote.log.storage.system.enable=true`).
- **Why the others are wrong:** A — compaction changes semantics (latest value per key) and is not even supported with tiered storage. B — `retention.bytes=-1` removes the size limit; the page cache is not storage. D — larger segments do not reduce total disk usage.
- 🧠 **Key point / trap:** "long retention, cheap, no extra brokers" → tiered storage. Remember the exceptions: **not for compacted topics**, and disabling requires `remote.log.delete.on.disable=true`.
- 📎 Source: `resources/kafka-topic-configs.md` (`remote.storage.enable`, `local.retention.ms` -2, `remote.log.delete.on.disable`) and Week 2 `README.md` §10.

### Question 27 — Answer: **B**

- **Why correct:** in KRaft mode the **active controller** (one of the controller quorum nodes) owns cluster metadata and performs leader election for affected partitions when a broker is fenced, choosing from the ISR (or the ELR when enabled). Metadata is an event log in the internal `__cluster_metadata` topic replicated with Raft; brokers fetch it as **observers**. Kafka 4.0 removed ZooKeeper entirely.
- **Why the others are wrong:** A — ZooKeeper mode no longer exists in 4.x. C — brokers do not self-elect; `__consumer_offsets` holds consumer group offsets. D — producers play no role in leadership; `__transaction_state` holds transaction coordinator state.
- 🧠 **Key point / trap:** three internal topics, three jobs: `__cluster_metadata` (KRaft metadata), `__consumer_offsets` (group offsets, compacted), `__transaction_state` (transactions). Week 2 adds a fourth: `__share_group_state`.
- 📎 Source: Week 1 `resources/kafka-operations-kraft.md` and `resources/kip-500-kip-853-kraft-confluent.md`.

### Question 28 — Answer: **D**

- **Why correct:** within a consumer group each partition is assigned to **at most one** consumer instance. With 6 partitions and 8 members, 6 members get one partition each and 2 members receive nothing. Parallelism is capped by the partition count, so the fixes are more partitions or, when per-record queue semantics are acceptable, a **share group** (Week 2 §9) where several consumers share a partition.
- **Why the others are wrong:** A — key-based splitting inside a partition does not exist for consumer groups. B — Kafka never changes partition counts automatically. C — extra members are allowed; they simply idle as hot standbys.
- 🧠 **Key point / trap:** partitions = maximum useful consumers **per group**. Different groups each get the full topic independently.
- 📎 Source: Week 1 `resources/kafka-intro-and-quickstart.md` (consumer groups and partitions) and Week 2 `resources/kafka-share-groups.md` (contrast).

---

> ✅ Logged every wrong answer? Group them by topic (ISR / high watermark, `acks` × `min.insync.replicas`, ELR & leader election, segments & retention, compaction, delivery semantics, message size, share groups) and re-read the matching section of the [week plan](README.md). The bar to move on to Week 3 is **≥ 70%** plus a fluent pass through the 8-question self-check gate; the Week 4 FUND + DEV mini-mock draws its FUND questions from Weeks 1–2.
