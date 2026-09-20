# ✅ Answers & Explanations — Week 1: Kafka Architecture, KRaft, Cluster Setup & CLI

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-C · 2-D · 3-B · 4-BD · 5-A · 6-C · 7-D · 8-B · 9-AC · 10-C · 11-A · 12-AD · 13-D · 14-BE · 15-AC · 16-C · 17-B · 18-A · 19-D · 20-BE · 21-C · 22-BC · 23-B · 24-A · 25-C · 26-B · 27-D · 28-AC · 29-AD · 30-BD

---

### Question 1 — Answer: **C**

- **Why correct:** Kafka is a **distributed commit log**. Records are appended, never modified, and are retained by time (`log.retention.hours=168`, i.e. 7 days by default) or size (`log.retention.bytes=-1`, disabled), completely independent of consumption. Reading does not delete anything; each consumer group only stores its own position in `__consumer_offsets`. A new `group.id` starts wherever `auto.offset.reset` says (default `latest`, or `earliest` / `--from-beginning`) and can therefore replay everything still retained.
- **Why the others are wrong:** A — Kafka has no per-message acknowledgement in classic consumer groups; consumers commit offsets, and an un-committed offset never triggers redelivery to another group. B — there is one copy of the data per replica, not one per group; groups differ only in their offsets. D — compaction is not involved; a `delete` topic behaves exactly the same way within its retention window.
- 🧠 **Key point / trap:** "topic is a **log**, not a queue". A queue deletes on consume; Kafka deletes on retention. Multiple groups reading the same data independently is Kafka's pub/sub fan-out.
- 📎 Source: `resources/kafka-intro-and-quickstart.md` ("events are not deleted after consumption"), `resources/kafka-broker-configs-listeners.md` (`log.retention.hours` 168).

### Question 2 — Answer: **D**

- **Why correct:** Kafka guarantees ordering **only within a partition**. The default partitioner maps a non-null key with `murmur2(key) mod numPartitions`, so every event of one `orderId` lands in the same partition and is appended in send order. The other 11 partitions keep serving other orders in parallel. The caveat is that the mapping only holds while the partition count stays at 12.
- **Why the others are wrong:** A — a single partition does give total ordering, but it caps the consumer group at one active consumer, violating the parallelism requirement. B — `LogAppendTime` only changes which clock stamps the record; records in different partitions still arrive interleaved and consumers do not sort. C — `max.in.flight.requests.per.connection=1` only affects retries of batches to the **same** partition; with `null` keys the sticky partitioner still spreads consecutive records across partitions, so per-order ordering is not achieved.
- 🧠 **Key point / trap:** "ordering per customer / device / order" → **same key → same partition**. "Ordering across the whole topic" → 1 partition. Never answer "add partitions" to an ordering question.
- 📎 Source: `resources/kafka-intro-and-quickstart.md` ("same key → same partition", "order within a topic-partition").

### Question 3 — Answer: **B**

- **Why correct:** inside one consumer group each partition is owned by **exactly one** consumer. Three partitions can therefore feed at most three consumers; members four to seven receive no assignment and sit idle. Partitions are the **unit of parallelism**: to use seven consumers the topic needs at least seven partitions (`kafka-topics.sh --alter --partitions`).
- **Why the others are wrong:** A — a partition is never split among members of the same group. C — no such error; over-subscribed groups are legal, just wasteful. D — a group is defined solely by `group.id`; consumers with the same id always join the same group and never reprocess from the start on their own.
- 🧠 **Key point / trap:** consumers ≤ partitions is the rule of thumb; extra consumers are only useful as hot standbys. The one exception is **share groups** (KIP-932, GA 4.2), where consumers may exceed partitions.
- 📎 Source: `resources/kafka-intro-and-quickstart.md` (partitions and consumer groups) and `README.md` §3.

### Question 4 — Answer: **B, D**

- **Why correct:** B is the fundamental rule: one partition → at most one consumer **within** a group, while every group has its own independent view of the full topic. D: since 0.9 offsets are committed to the internal compacted topic `__consumer_offsets`, created with `offsets.topic.num.partitions=50` by default, and kept for `offsets.retention.minutes=10080` (7 days) after a group becomes empty.
- **Why the others are wrong:** A — groups do **not** split records; each group receives every record (that is the pub/sub side of Kafka). C — Kafka consumers **pull** with fetch requests; the broker never pushes. E — ZooKeeper-based offset storage was removed long ago and ZooKeeper itself no longer exists in 4.0.
- 🧠 **Key point / trap:** "one record → one consumer" is true **inside** a group and false **across** groups. Remember the number 50 for `__consumer_offsets` (and also for `__transaction_state`) versus **1** for `__cluster_metadata`.
- 📎 Source: `resources/kafka-broker-configs-listeners.md` (`offsets.topic.num.partitions` 50), `resources/kafka-design-persistence-replication.md` (pull-based consumer).

### Question 5 — Answer: **A**

- **Why correct:** every segment file is named after the **base offset** of its first record, zero-padded to 20 digits. `00000000000000524288.log` therefore starts at offset 524 288, meaning the previous segment covers offsets 0 – 524 287. The segment with the highest base offset is the **active segment** receiving new writes. Each segment has a companion `.index` (offset → byte position) and `.timeindex` (timestamp → offset).
- **Why the others are wrong:** B — segments roll at `log.segment.bytes` (1 GB = 1 073 741 824 bytes) or `log.roll.hours` (168), not at a size encoded in the name; a segment size of 512 KB would be far below the 1 MB minimum allowed for `segment.bytes` since KIP-1030. C — record count is not stored in the name; 524 288 records could span any number of bytes. D — timestamps live in `.timeindex`, not in file names.
- 🧠 **Key point / trap:** "file `00000000000000012345.log`" → **segment**, name = **base offset**. Retention removes whole segments starting from the lowest base offset, never the active one.
- 📎 Source: `resources/kafka-implementation-log-message-format.md` (segment file = base offset).

### Question 6 — Answer: **C**

- **Why correct:** the broker first binary-searches its in-memory list of segment base offsets to pick the segment containing offset 700 000. It then reads that segment's **sparse** `.index`, which has one entry every `log.index.interval.bytes` = **4096 bytes**, finds the greatest indexed offset ≤ 700 000 and its byte position, seeks there in the `.log` file and scans forward a few kilobytes at most.
- **Why the others are wrong:** A — sequential scanning of a 1 GB file per fetch would make random reads O(n); the whole point of the index is O(log n) lookups. B — the index is sparse, not dense; a dense index would cost far more disk and memory. D — `.timeindex` is used only for time-based lookups such as `offsetsForTimes()` or `--to-datetime` resets.
- 🧠 **Key point / trap:** "find offset quickly inside a segment" → `.index`, **sparse every 4 KB** + binary search. Do not confuse 4096 (index interval) with 4 KB of anything else in the PHẢI NHỚ table.
- 📎 Source: `resources/kafka-implementation-log-message-format.md` (read path, binary search, `log.index.interval.bytes` 4096).

### Question 7 — Answer: **D**

- **Why correct:** the log cleaner works at **segment** granularity. A segment becomes eligible for deletion only when its **largest** record timestamp is older than `retention.ms`, and the **active segment** is never deleted. On a quiet topic the active segment can stay open for a long time because it neither reaches `log.segment.bytes` (1 GB) nor `log.roll.hours` (168 h = 7 days) quickly, so a 9-day-old record legitimately survives.
- **Why the others are wrong:** A — the retention check runs every `log.retention.check.interval.ms` = 300 000 ms (5 minutes), not daily. B — Kafka has no knowledge of consumer positions when deleting; a slow consumer simply gets `OffsetOutOfRangeException` later. C — retention applies to `cleanup.policy=delete` topics (the default); `log.retention.bytes` defaults to -1 (disabled).
- 🧠 **Key point / trap:** retention is a **lower bound**: records can live longer than `retention.ms`, never shorter. Expect the trap "Kafka deletes exactly the records older than 7 days" to be wrong.
- 📎 Source: `resources/kafka-implementation-log-message-format.md` ("data is deleted one log segment at a time", largest timestamp), `resources/kafka-broker-configs-listeners.md` (`log.retention.check.interval.ms` 300000).

### Question 8 — Answer: **B**

- **Why correct:** `message.timestamp.type` (topic level) / `log.message.timestamp.type` (broker default) accepts `CreateTime` or `LogAppendTime`. The default is **`CreateTime`**, meaning the producer's clock is recorded. With `LogAppendTime` the partition leader overwrites the batch timestamp with its own clock when it appends the batch, which is exactly "when the broker received it".
- **Why the others are wrong:** A — the default is `CreateTime`; the broker does **not** overwrite timestamps unless told to. C — there is no producer configuration named `timestamp.type`; the producer can only set the timestamp value in `ProducerRecord`. D — `message.timestamp.difference.max.ms` rejects records whose timestamp is too far from broker time, which drops data instead of correcting it (and it is ignored when `LogAppendTime` is used).
- 🧠 **Key point / trap:** "timestamp reflects when the broker wrote it" → **`LogAppendTime`**; default is **`CreateTime`** = producer time (may drift).
- 📎 Source: `resources/kafka-broker-configs-listeners.md` (`log.message.timestamp.type` default CreateTime), `resources/kafka-implementation-log-message-format.md` (attributes bit 3 timestampType).

### Question 9 — Answer: **A, C**

- **Why correct:** A — in format v2 the compression codec is stored in `attributes` bits 0–2 of the **batch** header and the whole records array is compressed as one unit; that is why `linger.ms` / `batch.size` influence the compression ratio. C — each record carries `keyLength`/`key` (nullable), `valueLength`/`value`, `headersCount`/headers and a `timestampDelta`, while `producerId`, `producerEpoch` and `baseSequence` appear **once** in the `RecordBatch` header and are used for idempotence and transactions.
- **Why the others are wrong:** B — records store `offsetDelta` and `timestampDelta` relative to the batch's `baseOffset` / `baseTimestamp`, encoded as varints to save space; they are not self-contained. D — the default `message.max.bytes` is **1 048 588** (1 MiB + 12 bytes), it applies to the **batch** and is evaluated **after** compression. E — the CRC covers the batch from `attributes` to the end and deliberately **excludes** `partitionLeaderEpoch`, so the leader can stamp the epoch without recomputing checksums.
- 🧠 **Key point / trap:** "compression is per batch" answers half of the compression questions on the exam. And the odd number **1 048 588** is a favourite trick: "1 MB exactly" marks an outdated answer.
- 📎 Source: `resources/kafka-implementation-log-message-format.md` (RecordBatch v2 header, attributes bits, varint record fields), `resources/kafka-broker-configs-listeners.md` (`message.max.bytes` 1048588).

### Question 10 — Answer: **C**

- **Why correct:** `--alter --partitions` is allowed and only ever **adds** partitions. Because the default partitioner computes `murmur2(key) mod numPartitions`, changing the modulus from 6 to 12 re-routes many existing keys. Old records for `customerId=42` stay in, say, partition 1 while new ones may go to partition 7, so a consumer can no longer rely on one partition per customer. When per-key ordering matters, the safe path is a new topic sized correctly plus a migration.
- **Why the others are wrong:** A — the partitioner is stateless; it has no memory of previous assignments. B — Kafka has no notion of a "keyed topic"; the alter succeeds. D — keyed records are precisely the ones affected; `null`-key records use the sticky partitioner and have no ordering expectation anyway.
- 🧠 **Key point / trap:** "increase partitions on a keyed topic" → **breaks key → partition mapping**. Choose enough partitions up front (formula in README §C.2, add 20–30 % headroom).
- 📎 Source: `README.md` §C.2 and `resources/kafka-intro-and-quickstart.md` (key → partition).

### Question 11 — Answer: **A**

- **Why correct:** Kafka can only **increase** the partition count of an existing topic. Requesting fewer partitions makes the broker return `InvalidPartitionsException` ("Topic currently has 24 partitions, which is higher than the requested 8"). Shrinking would require deleting data and re-mapping offsets, which the log design does not support. The workaround is a new topic (`--partitions 8`) and a re-publish or MirrorMaker 2 copy.
- **Why the others are wrong:** B — offsets are per partition and cannot be merged; no such operation exists. C — there is no `--force` flag on `kafka-topics.sh`. D — group activity does not change the rule; decreasing is impossible in all cases.
- 🧠 **Key point / trap:** "reduce the number of partitions" → **impossible**; any option that alters downward is a distractor.
- 📎 Source: `README.md` §2 table (partitions "chỉ tăng, không giảm") and `resources/kafka-broker-configs-listeners.md` (`num.partitions` 1).

### Question 12 — Answer: **A, D**

- **Why correct:** A — with no flags the topic inherits `num.partitions=1` and `default.replication.factor=1`. A single replica means a single point of failure: when its broker is down the partition is offline for producers and consumers, and a lost disk means permanent data loss (nothing to promote). D — the controller refuses a replication factor larger than the number of live brokers with `InvalidReplicationFactorException`; RF ≤ broker count is a hard rule at creation time.
- **Why the others are wrong:** B — Kafka never infers RF from cluster size; production clusters set `default.replication.factor=3` explicitly (the Week 1 `docker-compose.cluster.yml` does exactly that). C — `kafka-topics.sh --alter` has no `--replication-factor` option for existing topics; RF is changed by a partition reassignment (`kafka-reassign-partitions.sh` with a new replica list). E — replicas are only placed when a topic is created or reassigned; new brokers receive nothing until an operator moves partitions there.
- 🧠 **Key point / trap:** "why is RF=1 dangerous" → no failover, no durability. Production baseline: **RF=3 + `min.insync.replicas=2` + `acks=all`**.
- 📎 Source: `resources/kafka-broker-configs-listeners.md` (`default.replication.factor` 1, `num.partitions` 1), `resources/kafka-intro-and-quickstart.md` ("replication factor of 3").

### Question 13 — Answer: **D**

- **Why correct:** a replica is in-sync when it has an active session with the controller **and** has caught up to the leader's log end within `replica.lag.time.max.ms` (default **30 000 ms**). Broker 3 lost its session, so it was dropped from the ISR. After restart its follower fetcher pulled the missing records; once it reached the leader's log end offset the leader expanded the ISR again with no operator action.
- **Why the others are wrong:** A — ZooKeeper is gone in 4.x, the interval is not 10 s, and there is no `--isr` flag; ISR changes are made by the leader and recorded through the controller. B — `replica.lag.max.messages` was removed in 0.9 because message-count lag misbehaves under bursty traffic; and a preferred leader election changes the leader, not ISR membership. C — a running but slow follower **is** removed once it lags beyond 30 s.
- 🧠 **Key point / trap:** "follower is 30 s behind" → **leaves ISR**; "catches up" → **rejoins automatically**. The trigger is time, not message count.
- 📎 Source: `resources/kafka-design-persistence-replication.md` (ISR definition, `replica.lag.time.max.ms`), `resources/kafka-broker-configs-listeners.md` (default 30000).

### Question 14 — Answer: **B, E**

- **Why correct:** B — a record is **committed** only when **every replica in the ISR** has written it. With one ISR follower still missing the record, it lies above the **High Watermark**, and brokers only serve consumers data up to the HW, whatever the `isolation.level`. E — the ISR model lets Kafka tolerate **f** failures with **f + 1** replicas, because any ISR member holds all committed data. A majority-vote design would need **2f + 1** replicas (5 to survive 2 failures).
- **Why the others are wrong:** A — leader-only persistence is what `acks=1` returns to the producer, but "committed" in Kafka terms means full-ISR replication. C — followers **fetch** from the leader like consumers; nothing is pushed. D — `read_uncommitted` refers to **transactions** (seeing aborted records), not to un-replicated records; the HW limit still applies.
- 🧠 **Key point / trap:** two different "committed" concepts: **replication-committed** (HW) vs **transaction-committed** (LSO, Week 3). f+1 vs 2f+1 is a classic "why Kafka is different from Raft/Paxos storage" question.
- 📎 Source: `resources/kafka-design-persistence-replication.md` ("committed when all replicas in the ISR", "f+1 replicas tolerate f failures", "only committed messages are ever given out").

### Question 15 — Answer: **A, C**

- **Why correct:** A — under ZooKeeper the new controller had to read the state of every topic, partition and broker from ZooKeeper before serving requests, making failover **O(partitions)** and limiting practical cluster size to about **200 000** partitions. C — Kafka required two systems with different configuration, security and monitoring, and the controller's cached metadata regularly disagreed with what was in ZooKeeper (ISR changes took seconds to propagate), causing divergence bugs. KRaft fixes both by putting metadata in one replicated log with hot-standby controllers.
- **Why the others are wrong:** B — ZooKeeper 3.5+ supports TLS and SASL; security complexity was the issue, not impossibility. D — ZooKeeper runs on modern JDKs; Java requirements were never the motivation. E — KRaft is an event-driven **Raft** variant, the opposite of a gossip protocol.
- 🧠 **Key point / trap:** the "why" question has three canonical answers: **two systems**, **metadata divergence**, **slow O(partition) failover / scale limit**. KRaft's benefits mirror them: single system, single source of truth, near-instant failover, millions of partitions.
- 📎 Source: `resources/kip-500-kip-853-kraft-confluent.md` (KIP-500 motivation section, controller failover paragraph).

### Question 16 — Answer: **C**

- **Why correct:** a Raft quorum needs a strict **majority** of voters to elect a leader and commit records. With 4 voters the majority is 3, so losing 2 leaves only 2 — no quorum. That is the same tolerance as a 3-node quorum (majority 2, one failure). The docs recommend **3 or 5** controllers: 3 tolerates 1 failure, 5 tolerates 2.
- **Why the others are wrong:** A — two survivors out of four are not a majority. B — 5 (and in rare cases 7) is also valid; only even numbers are pointless. D — the standby controllers are what makes failover near-instant; a single controller is a single point of failure for all metadata operations.
- 🧠 **Key point / trap:** "4 controllers tolerate 2 failures" is a planted arithmetic error. Majority of N = ⌊N/2⌋ + 1; tolerance = N − majority.
- 📎 Source: `resources/kafka-operations-kraft.md` (3 or 5 controllers), `resources/kip-500-kip-853-kraft-confluent.md` (quorum-based leader election).

### Question 17 — Answer: **B**

- **Why correct:** cluster metadata lives in the internal topic `__cluster_metadata`, which has exactly **one partition**. The active controller is the leader of that partition and is the only node that writes to it; the other controllers are voting followers with the full state in memory; brokers are **observers** that fetch the log (pull model). Snapshots (`<offset>-<epoch>.checkpoint`) capture the in-memory image so old log records can be dropped, and `kafka-metadata-shell.sh --snapshot` can browse them.
- **Why the others are wrong:** A — 50 partitions and consumer offsets describe `__consumer_offsets`, not the metadata log. C — ZooKeeper is not involved at all; that is the point of KRaft. D — the old push model (`UpdateMetadataRequest` broadcast by the ZooKeeper-era controller) was replaced by brokers fetching an ordered log so every node sees the same timeline.
- 🧠 **Key point / trap:** `__cluster_metadata` = **1 partition**, replicated by **quorum**, not by ISR. Brokers **fetch**; the controller never pushes.
- 📎 Source: `resources/kip-500-kip-853-kraft-confluent.md` (single partition topic, observers, snapshots), `resources/kafka-operations-kraft.md` (metadata shell / dump-log on `__cluster_metadata-0`).

### Question 18 — Answer: **A**

- **Why correct:** `process.roles=broker,controller` is **combined mode**. The documentation states it is for development and testing: a heavy data workload on the same JVM can starve the controller, and a broker failure takes a voter down with it. Production should use dedicated controller nodes (`process.roles=controller`, usually 3) plus broker-only nodes (`process.roles=broker`). All nodes share one `node.id` namespace, so ids must be unique across brokers and controllers.
- **Why the others are wrong:** B — combined mode still needs `controller.listener.names` (port 9093 by convention); it is not recommended for production. C — combined mode is fully supported in 4.x; it is what the Week 1 single-node compose file and the quickstart use. D — combined nodes work with both static and dynamic quorums.
- 🧠 **Key point / trap:** "only for dev" → **combined mode**. The savings argument in the question is the bait.
- 📎 Source: `resources/kafka-operations-kraft.md` (process roles, combined mode not for production).

### Question 19 — Answer: **D**

- **Why correct:** every `KRaft` node must have each directory in `log.dirs` formatted with a `meta.properties` file containing the shared `cluster.id`, its `node.id` and a `directory.id`. `kafka-storage.sh random-uuid` is run **once** per cluster; new nodes reuse the existing id. In a dynamic quorum, a node that joins an already bootstrapped cluster is formatted with `--no-initial-controllers`. A broker whose `cluster.id` differs from the quorum's is rejected on registration.
- **Why the others are wrong:** A — a new random UUID creates a *different* cluster id; the broker would log an "inconsistent cluster ID" error and never join. B — a bare Kafka distribution never auto-formats (only the `apache/kafka` Docker image does so from the `CLUSTER_ID` environment variable). C — `add-controller` adds a **controller** voter that is already running and caught up; it does not format anything and is irrelevant for a broker.
- 🧠 **Key point / trap:** `random-uuid` → **once per cluster**; `format` → **every node, same id**. "Broker won't start" + "meta.properties" → formatting problem, not networking.
- 📎 Source: `resources/kafka-operations-kraft.md` (storage tool, `--no-initial-controllers`, "this cluster ID must be used by all the servers").

### Question 20 — Answer: **B, E**

- **Why correct:** B — a static quorum hard-codes `id@host:port` voters in `controller.quorum.voters` on every node; membership changes need config edits and full restarts, and the setting is **deprecated** in 4.x. E — KIP-853 (Kafka 3.9+, `kraft.version=1`) makes the voter set part of the metadata log itself: clients and brokers only need `controller.quorum.bootstrap.servers`, new controllers are formatted with `--no-initial-controllers` and, once caught up, joined with `kafka-metadata-quorum.sh add-controller`; leaving is `remove-controller --controller-id <id> --controller-directory-id <uuid>`.
- **Why the others are wrong:** A — dynamic voters are identified by `node.id` **plus** `directory.id` (a UUID of the log dir) so a re-imaged node with an empty disk cannot impersonate the old voter. C — `__cluster_metadata` replication is governed by the quorum, not by `kafka-topics.sh`; the command is rejected. D — inverted: level **0 or absent** means **static**; level **1 or above** means dynamic.
- 🧠 **Key point / trap:** "add a controller without restarting" → **dynamic quorum / KIP-853 / `add-controller`**. Static = `voters`; dynamic = `bootstrap.servers`. Both are for controllers; do not confuse `controller.quorum.bootstrap.servers` with the client's `bootstrap.servers`.
- 📎 Source: `resources/kafka-operations-kraft.md` (static vs dynamic, `kafka-features.sh describe` → `kraft.version`, add/remove-controller), `resources/kip-500-kip-853-kraft-confluent.md` (KIP-853 `directory.id`).

### Question 21 — Answer: **C**

- **Why correct:** Kafka 4.0 raised the server-side baseline: brokers, `Kafka Connect` workers and the shell tools require **Java 17+**. The client libraries and `Kafka Streams` keep a **Java 11+** requirement so applications are not forced to upgrade in lock-step with the platform team.
- **Why the others are wrong:** A — Java 11 brokers cannot start 4.0. B — Java 21 is supported but not required. D — reversed; it is the broker side that moved to 17.
- 🧠 **Key point / trap:** "Java 17 broker / Java 11 client" is a two-number fact the new exam likes; the asymmetry (server stricter than client) is the trick.
- 📎 Source: `resources/kafka-4.0-release-announcement.md` (Java requirements section).

### Question 22 — Answer: **B, C**

- **Why correct:** B — removing message formats v0/v1 (KIP-724) and the oldest request API versions (KIP-896) means the minimum compatible protocol on both sides is Kafka **2.1**: 4.0 brokers reject older clients and 4.0 clients need brokers ≥ 2.1. C — the original MirrorMaker (the standalone consumer/producer tool) was deleted in 4.0; MirrorMaker 2 running on `Kafka Connect` is the replacement.
- **Why the others are wrong:** A — 4.0 is **KRaft-only**; `zookeeper.connect` no longer exists. Migration must be completed on the **3.9 bridge release** before upgrading. D — KIP-848 became **GA** in 4.0 but stays **opt-in** via `group.protocol=consumer`; the default is still `classic` (deprecated in 4.3, not removed). E — KIP-1030 moved `linger.ms` **from 0 to 5 ms** (and `num.recovery.threads.per.data.dir` from 1 to 2), the opposite direction.
- 🧠 **Key point / trap:** anything that says 4.0 "still works with ZooKeeper" is wrong. Baseline **2.1**, `linger.ms` **5**, KIP-848 **GA but opt-in**.
- 📎 Source: `resources/kafka-4.0-release-announcement.md` (KIP-724/896 baseline 2.1, KIP-848 opt-in, KIP-1030); MirrorMaker 1 removal is documented in Week 8 `resources/kafka-upgrade-kraft.md` (Kafka 4.0 notable changes).

### Question 23 — Answer: **B**

- **Why correct:** **Share groups** (KIP-932, "Queues for Kafka") let many consumers cooperatively consume the same partitions: records are acquired for a limited time and each is explicitly acknowledged (accept / release / reject), and the number of consumers may exceed the number of partitions. Timeline: **early access 4.0 → preview 4.1 → GA 4.2**.
- **Why the others are wrong:** A — ELR (KIP-966) is about leader election safety when the ISR is empty; timeline preview 4.0 → GA 4.1, unrelated to queue semantics. C — KIP-848 speeds up rebalances but keeps one-partition-per-consumer semantics and offset-based acknowledgement. D — extra consumers in a classic group simply stay idle (Question 3).
- 🧠 **Key point / trap:** remember the two 4.x timelines side by side: **ELR** preview 4.0 → GA 4.1; **share groups** EA 4.0 → preview 4.1 → GA 4.2.
- 📎 Source: `resources/kafka-4.0-release-announcement.md` (KIP-932 early access, KIP-966 preview) and `README.md` §6 table (GA versions).

### Question 24 — Answer: **A**

- **Why correct:** a client uses `bootstrap.servers` only to open its **first** connection and send a `MetadataRequest`. The response lists **every** broker (with its `advertised.listeners` address) and the leader of each partition, and the client then connects **directly** to those leaders; later metadata refreshes go to any known broker. Running clients therefore survive the loss of the bootstrap broker. A brand-new client, however, knows nothing yet; if its only bootstrap address is dead it cannot obtain metadata, hence the guidance to list **2–3** brokers.
- **Why the others are wrong:** B — the list never has to be complete; one reachable broker is enough to discover the rest. C — metadata refreshes are sent to any connected broker, not necessarily a bootstrap one; the running clients keep working. D — the controller listener (9093) serves controller RPCs; clients do not bootstrap through it (`--bootstrap-controller` is for admin tools only).
- 🧠 **Key point / trap:** "bootstrap is only for the first hop". The exam contrasts *running* clients (fine) with *new* clients (fail) exactly like this question.
- 📎 Source: `resources/kafka-broker-configs-listeners.md` (3-step client connection flow).

### Question 25 — Answer: **C**

- **Why correct:** `listeners` is where the broker **binds**; `advertised.listeners` is what it **tells clients** in metadata. The docs state that when `advertised.listeners` is not set, "the value for `listeners` will be used", so metadata returns `10.0.1.5:9092`. Office clients succeed at the bootstrap step (they used the DNS name) and then time out connecting to the private IP for the actual partition leader. Setting `advertised.listeners=PLAINTEXT://kafka-1.example.com:9092` while leaving `listeners` on the bind address fixes it.
- **Why the others are wrong:** A — the broker cannot bind to a name that resolves to a public address not present on its interface; `listeners` should stay on the local IP (or `0.0.0.0`). B — this is a routing failure, not slowness; timeouts would persist. D — `bootstrap.servers` is a **client** setting, not a broker one.
- 🧠 **Key point / trap:** "can bootstrap, then times out" → **`advertised.listeners`**, every time. Also remember: advertising `0.0.0.0` is invalid.
- 📎 Source: `resources/kafka-broker-configs-listeners.md` (`advertised.listeners` definition: "if this is not set, the value for `listeners` will be used"; cloud-VM example).

### Question 26 — Answer: **B**

- **Why correct:** the host application connects to `localhost:9092` (the published port), receives `kafka-1:9092` from metadata, and cannot resolve `kafka-1` outside the Docker network. Brokers inside the network **do** need `kafka-1` to reach each other, so a single advertised address can never satisfy both audiences. The standard pattern is **two listeners** with two names: `PLAINTEXT` on 19092 advertised as the container hostname (inter-broker, `KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT`) and `PLAINTEXT_HOST` on 9092/9094/9096 advertised as `localhost:<port>`. Since `PLAINTEXT_HOST` is not itself a security protocol name, `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP` must map it (and `CONTROLLER`) to `PLAINTEXT`.
- **Why the others are wrong:** A — container names are not resolvable from the host by default; hacking `/etc/hosts` to `127.0.0.1` also breaks with 3 brokers on the same host port. C — advertising `localhost:9092` fixes the host app but the brokers now believe their peers live at `localhost:9092`, i.e. themselves: replication, `kafka-2`/`kafka-3` connections and every in-network client break. D — clients never talk to the controller listener; 9093 is for brokers and controllers only.
- 🧠 **Key point / trap:** "works in `docker exec`, fails from host" → `advertised.listeners` returns an internal hostname. The fix is **one listener per network audience**, not a different port mapping. This is the reason the Week 1 aliases must use `kafka-1:19092` inside the container.
- 📎 Source: `resources/kafka-broker-configs-listeners.md` ("Kafka Listeners — Explained" Docker trap and two-listener example), `labs.md` Lab 1.2.

### Question 27 — Answer: **D**

- **Why correct:** the console producer treats each line as a value unless `parse.key=true` is set; `key.separator` defaults to a **tab**, so it must be set to `:` to split `user-42:{"event":"login"}` correctly. The console consumer prints only values unless asked: `print.key=true`, `print.partition=true`, `print.offset=true` (plus `print.timestamp=true` if needed), and `--from-beginning` is required to see records produced before the consumer started. All tools use `--bootstrap-server` (KIP-1147); Kafka 4.3 still accepts `--property` alongside the newer `--formatter-property` name.
- **Why the others are wrong:** A — `--broker-list` was removed from the console producer, and `--key` / `--print-key` flags do not exist. B — `--zookeeper` was removed in 4.0 for every tool. C — with `parse.key=true` but no `key.separator` the producer looks for a tab and fails with "No key separator found on line"; the consumer also lacks `--from-beginning` and the partition/offset properties requested.
- 🧠 **Key point / trap:** `parse.key=true` + `key.separator=:` on the producer; `print.key=true` + `print.partition=true` on the consumer. Any option containing `--zookeeper` or `--broker-list` is eliminated immediately.
- 📎 Source: `README.md` §8 CLI table, `resources/kafka-intro-and-quickstart.md` (console producer / consumer with `--bootstrap-server`).

### Question 28 — Answer: **A, C**

- **Why correct:** A — topic configs are changed dynamically with `kafka-configs.sh --entity-type topics --entity-name <topic> --alter --add-config retention.ms=<ms>`; 3 days = 3 × 86 400 000 = **259 200 000 ms**. The new retention takes effect at the next retention check (every 5 minutes). C — `kafka-consumer-groups.sh --reset-offsets` supports `--to-earliest`, `--to-latest`, `--shift-by`, `--to-datetime`, `--to-offset` and requires `--execute` to actually apply (otherwise it only prints the plan); the group must be **inactive** or the command fails.
- **Why the others are wrong:** B — `--zookeeper` was removed; `kafka-topics.sh --alter --config` was itself deprecated in favour of `kafka-configs.sh` long ago. D — `--delete-offsets` removes committed offsets for a topic; it does not take a reset target and is not the way to rewind. E — `--broker-list` is not accepted by `kafka-configs.sh` (KIP-1147 standardises on `--bootstrap-server`), and `retention.hours` is not a topic-level config (`retention.ms` is; the broker-level default is `log.retention.hours`).
- 🧠 **Key point / trap:** "change retention on a live topic" → `kafka-configs.sh --alter --add-config retention.ms`. "reset offsets" → `kafka-consumer-groups.sh --reset-offsets … --execute` with the group stopped.
- 📎 Source: `README.md` §8 CLI table and `resources/kafka-broker-configs-listeners.md` (dynamic topic configs).

### Question 29 — Answer: **A, D**

- **Why correct:** A — `kafka-metadata-quorum.sh describe --status` prints `LeaderId` (the active controller), `LeaderEpoch`, `HighWatermark`, `MaxFollowerLag`, and the lists of `CurrentVoters` and `CurrentObservers`. D — `kafka-dump-log.sh --files <segment>.log --print-data-log` decodes the batches and records in a segment file on the local disk, showing offsets, timestamps, keys and payloads; with `--cluster-metadata-decoder` it can decode `__cluster_metadata` segments as well.
- **Why the others are wrong:** B — `kafka-log-dirs.sh` reports **sizes** and `offsetLag` per partition per broker as JSON; it does not show record contents. C — `kafka-topics.sh --describe` shows partition leaders, replicas and ISR, not the KRaft active controller or metadata high watermark. E — the console consumer reads through the broker API and shows values, not the raw on-disk batch structure the task asks for.
- 🧠 **Key point / trap:** three "look inside" tools: **quorum state** → `kafka-metadata-quorum.sh`; **segment bytes** → `kafka-dump-log.sh`; **metadata as a filesystem** → `kafka-metadata-shell.sh`. `kafka-log-dirs.sh` is about **disk usage**.
- 📎 Source: `resources/kafka-operations-kraft.md` (three KRaft debug tools) and `README.md` §8 CLI table.

### Question 30 — Answer: **B, D**

- **Why correct:** B — `SQS` is a queue: a message received and deleted by one consumer is gone; fanning out to three services requires `SNS` → three queues (or `EventBridge`), and consumed messages cannot be replayed. D — Kafka's log model handles all three needs natively: independent consumer groups each read 100 % of the data, retention set to 30 days (`retention.ms=2592000000`) lets analysts reset offsets `--to-datetime` or `--to-earliest`, and keying by `customerId` guarantees per-customer order inside a partition.
- **Why the others are wrong:** A — `Kinesis Data Streams` retention defaults to 24 hours but can be extended up to **365 days**, so replay is possible; Kinesis is also a valid managed alternative here. C — RabbitMQ (AMQP) deletes messages after acknowledgement; replay exists only with the separate Streams feature, not by default. E — Kafka 4.2 offers share groups (KIP-932) precisely for work-queue semantics.
- 🧠 **Key point / trap:** the decision row that matters on interviews: **replay + multiple independent readers + ordering by key** → Kafka (or Kinesis inside AWS); **simple decoupled job queue** → `SQS`; **complex routing / per-message TTL** → RabbitMQ.
- 📎 Source: `README.md` §C.1 comparison table (Kafka vs `SQS` vs `Kinesis` vs RabbitMQ).

---

> ✅ Logged every wrong answer? Group them by topic (log & segments, partitions & ordering, replication & ISR, KRaft, 4.0 changes, listeners, CLI) and re-read the matching section of the [week plan](README.md) plus the **PHẢI NHỚ** table before moving on. The gate to leave Week 1 is **≥ 70%** and a fluent pass through the 8 self-check questions.
