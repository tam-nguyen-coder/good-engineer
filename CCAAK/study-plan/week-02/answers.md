# ✅ Answers & Explanations — Week 2: Cluster Config I (broker config, `log.dirs` & storage, retention, compaction)

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

**Answer key:** 1-A · 2-B · 3-B · 4-AC · 5-B · 6-C · 7-B · 8-B · 9-AC · 10-A · 11-A · 12-AC · 13-B · 14-BD · 15-B · 16-C · 17-B · 18-A · 19-B · 20-B · 21-ABD · 22-A · 23-A · 24-A · 25-A · 26-A · 27-B · 28-B · 29-A · 30-AB

---

### Question 1 — Answer: **A**

- **Why correct:** `RequestHandlerAvgIdlePercent` measures how idle the **request handler (I/O) thread pool** is; healthy clusters sit above 0.3. At 0.08 the pool is saturated while CPU is only 40%, which is the textbook signature of too few `num.io.threads` (default **8**). `num.io.threads` has update mode **cluster-wide**, so `kafka-configs.sh --entity-type brokers --entity-default` applies it to the whole cluster with no restart — the cheapest, most reversible action available.
- **Why the others are wrong:** B — `num.network.threads` is measured by `NetworkProcessorAvgIdlePercent`, a different metric that the scenario does not mention; and it is also dynamic, so the rolling restart is unnecessary either way. C — `queued.max.requests` (500) is the depth of the queue **in front of** the handler pool; enlarging it would let more requests wait rather than making them complete faster, and it is read-only so the command would be rejected. D — Kafka 4.x is KRaft-only; ZooKeeper and its `/config/brokers/<id>` znodes were removed in 4.0, and dynamic configuration lives in the metadata log.
- 🧠 **Key point / trap:** learn the metric → config mapping as a pair. `RequestHandlerAvgIdlePercent` → `num.io.threads`; `NetworkProcessorAvgIdlePercent` → `num.network.threads`. Both are dynamic.
- 📎 Source: `resources/kafka-broker-configs-storage-threads.md` (threads table, all cluster-wide) and `resources/kafka-hardware-os-disks-jbod.md` (MBean names).

### Question 2 — Answer: **B**

- **Why correct:** the error message names the mechanism exactly: `Cannot update these configs dynamically`. `queued.max.requests` is documented with update mode **read-only**, together with the rest of the socket group (`socket.send.buffer.bytes`, `socket.receive.buffer.bytes`, `socket.request.max.bytes`). Read-only means the value is only read at broker startup, so it must go in `server.properties` and be rolled out.
- **Why the others are wrong:** A — `--entity-name` changes the **scope**, not the update mode; a read-only config is refused for both scopes. C — `--bootstrap-controller` exists for talking to controllers when brokers are down; it does not unlock read-only configs. D — there is no `dynamic.config.enable` configuration in Kafka; dynamic configuration is always available for the configs that support it.
- 🧠 **Key point / trap:** the mental shortcut for this week is **"threads change hot, sockets change cold"**. Every config in the thread group is cluster-wide; every config in the socket group is read-only.
- 📎 Source: `resources/kafka-broker-configs-storage-threads.md` (socket table) and `resources/confluent-dynamic-config-precedence.md` (update mode definitions).

### Question 3 — Answer: **B**

- **Why correct:** in `--describe --all` output the **first** entry of `synonyms` is the source that currently wins. Here it is `DYNAMIC_BROKER_CONFIG:log.retention.ms=7200000`, i.e. a per-broker dynamic override, which sits second in the precedence chain (below topic overrides, above cluster-wide defaults). Deleting it would let the next surviving entry take over — `DYNAMIC_DEFAULT_BROKER_CONFIG` at 259200000.
- **Why the others are wrong:** A — if there were a topic override, the first synonym would read `DYNAMIC_TOPIC_CONFIG:retention.ms=...`; it does not appear in the list at all. C — precedence runs the other way: dynamic sources beat `STATIC_BROKER_CONFIG`. D — synonyms are alternatives, never summed; the effective value is printed on the left of the line.
- 🧠 **Key point / trap:** read `synonyms` left to right as "who wins now, and who would win next". That single habit answers most precedence questions on the exam.
- 📎 Source: `resources/confluent-dynamic-config-precedence.md` (5-level order + how to read `synonyms`).

### Question 4 — Answer: **A, C**

- **Why correct:** A states the rule — `DYNAMIC_TOPIC_CONFIG` is the highest of the five precedence levels, so a topic override is immune to any broker-level change. C is the correct diagnostic step: `--describe --all` plus the first entry of `synonyms` proves where the effective value comes from, per topic.
- **Why the others are wrong:** B — cluster-wide defaults **do** apply retroactively to existing topics that have no override; the five topics are special because they carry overrides, not because of their creation date. D — `log.retention.ms` is cluster-wide (dynamic); it is `log.retention.hours` that is read-only. E — `--entity-default` writes one cluster-wide record; it is not per broker.
- 🧠 **Key point / trap:** "I changed the broker default and nothing happened" is a scripted exam scenario. The answer is always a topic override, and the proof is always `--describe --all`.
- 📎 Source: `resources/confluent-dynamic-config-precedence.md` and [`labs.md`](labs.md) Lab 2.1 step 6.

### Question 5 — Answer: **B**

- **Why correct:** the Kafka design documentation is explicit — *"Data is deleted one log segment at a time."* Retention removes **closed** segments only, and never the active segment. A topic writing ~2 MB/day with the default `segment.bytes` of 1 GiB will not roll a segment for well over a year, so there is simply nothing eligible for deletion. Setting `segment.ms` on the topic forces regular rolls and retention starts working within a check interval.
- **Why the others are wrong:** A — the sweep already runs every 5 minutes; running it more often does not create eligible segments. C — `retention.ms` and `retention.bytes` are independent; whichever is hit first triggers deletion, and `retention.bytes=-1` simply means "no size limit". D — `kafka-topics.sh --alter` only changes partition count; topic configs are changed with `kafka-configs.sh`, and neither requires any restart.
- 🧠 **Key point / trap:** this is the single most repeated storage trap in the domain. Whenever a scenario says "retention is short but old data is still there", the answer involves **`segment.ms` / `segment.bytes`**, not the retention setting itself.
- 📎 Source: `resources/kafka-design-log-compaction.md` (Deletes: "one log segment at a time") and [`labs.md`](labs.md) Lab 2.3.

### Question 6 — Answer: **C**

- **Why correct:** `retention.bytes` is a **per-partition** limit, and every replica of a partition stores the full data independently. Worst case is therefore `partitions × retention.bytes × replication.factor` = 6 × 10 GiB × 3 = **180 GiB** across the cluster.
- **Why the others are wrong:** A — it is not a topic-wide budget. B — replicas do not share storage; each of the three replicas is a complete copy on a different broker's disk. D — this omits the partition multiplier entirely.
- 🧠 **Key point / trap:** the same multiplication is the basis of the capacity formula you will use in Week 4: `disk ≈ write throughput × retention × RF × 1.2`. Anyone who forgets the RF factor under-provisions by a factor of three.
- 📎 Source: `resources/kafka-topic-configs-overrides.md` (`retention.bytes` per partition) and [`../../CCAAK-STUDY-PLAN.md`](../../CCAAK-STUDY-PLAN.md) §5 (capacity planning).

### Question 7 — Answer: **B**

- **Why correct:** the Kafka hardware documentation states *"partitions will be assigned round-robin to data directories. Each partition will be entirely in one of the data directories."* The selection criterion is the **number of partition directories**, never free space — which is exactly why 41/40/40 can coexist with 94%/…/22% usage: a handful of high-volume partitions landed on `/data/d1`. The correct first action is to look, not to guess: `kafka-log-dirs.sh --describe` reports `size` per partition per directory (and `totalBytes`/`usableBytes` per directory since KIP-849).
- **Why the others are wrong:** A — Kafka never looks at free space when placing a partition, so the disks are fine; replacing hardware solves nothing. C — a partition is **never** striped across directories; it lives entirely in one. D — `auto.leader.rebalance.enable` and `kafka-leader-election.sh` move **leadership**, not data, and they operate across brokers, not across log directories.
- 🧠 **Key point / trap:** "even by count, uneven by bytes" is the defining property of Kafka's JBOD placement. Remember the follow-up too: to fix it you cordon the full directory and reassign with a `log_dirs` entry.
- 📎 Source: `resources/kafka-hardware-os-disks-jbod.md` and `resources/kafka-log-dirs-tool.md`.

### Question 8 — Answer: **B**

- **Why correct:** `KafkaStorageException` plus `Stopping serving logs in dir /data/d2` is the log-directory failure path. Since KRaft gained JBOD support, a broker with multiple log directories takes only the failed directory offline: the partitions stored there lose their replica on this broker (leader `-1` and empty ISR if no other replica can take over), while partitions in `/data/d1` keep serving. A broker only shuts itself down when **all** of its log directories have failed.
- **Why the others are wrong:** A — quorum loss produces controller/metadata errors, not `LogDirFailureChannel` and `IOException` on a data directory; and the broker is explicitly still running. C — `__cluster_metadata` corruption would prevent the broker from operating at all and would not selectively affect 37 partitions. D — file-descriptor exhaustion raises `Too many open files`, and nothing "comes back automatically" from an offline log directory.
- 🧠 **Key point / trap:** `KafkaStorageException` is the disk-layer exception. Seeing it should send you to `kafka-log-dirs.sh` and `OfflineLogDirectoryCount`, never to ISR or network tuning.
- 📎 Source: `resources/kafka-hardware-os-disks-jbod.md` (MBean `OfflineLogDirectoryCount`, `LogDirectoryOffline`) and [`labs.md`](labs.md) Lab 2.2.

### Question 9 — Answer: **A, C**

- **Why correct:** A — once a log directory has been marked offline, Kafka does not re-add it while the broker is running; a restart is required for the `LogManager` to scan and adopt the directory again. C — with `replication.factor=3` the partitions that lived on the failed disk still exist on two other brokers, so after the restart the broker re-replicates from the current leaders and `UnderReplicatedPartitions` drops back to 0 once it catches up.
- **Why the others are wrong:** B — there is no automatic re-adoption of a failed directory; `log.dir.failure.timeout.ms` governs how long the broker waits before reacting to a failure, not how it recovers. D — data loss only occurs where there was no other replica, i.e. `replication.factor=1`; a new directory identity is generated on restart and is not a problem. E — `cordoned.log.dirs` controls **new partition placement** and is unrelated to the offline state caused by a hardware failure.
- 🧠 **Key point / trap:** distinguish the three states of a log directory: **online**, **cordoned** (healthy, just excluded from new placement) and **offline** (failed, needs a restart). The exam mixes them deliberately.
- 📎 Source: `resources/kip-1066-cordoned-log-dirs.md` (cordon ≠ offline) and [`labs.md`](labs.md) Lab 2.2 step 9.

### Question 10 — Answer: **A**

- **Why correct:** the `error` field of `/data/d2` is `"KAFKA_STORAGE_ERROR"` instead of `null`, which is how `kafka-log-dirs.sh` reports an offline directory. And `"isFuture": true` on `orders-3` marks it as the **destination copy** of an in-progress inter-log-directory move (KIP-113): the broker is writing a future replica in `/data/d1` that will replace the original once it catches up.
- **Why the others are wrong:** B — an empty but healthy directory would still show `"error": null`; `isFuture` has nothing to do with future partition creation. C — a cordoned directory is healthy and reports `"error": null`; and `offsetLag` here is 0. D — `orders-0` has the *smaller* size and an `offsetLag` of 0, so nothing about it demands a reassignment.
- 🧠 **Key point / trap:** three fields carry all the diagnostic value in this JSON — `error` (is the directory alive?), `size` (who is eating the disk?) and `isFuture` (is a move already running?).
- 📎 Source: `resources/kafka-log-dirs-tool.md` (JSON shape and field meanings).

### Question 11 — Answer: **A**

- **Why correct:** this is exactly what KIP-1066 was designed for. `cordoned.log.dirs=/data/d2` is a **per-broker dynamic** configuration: the directory keeps serving every partition it already holds, but the controller stops placing new partitions on it. That buys the administrator a quiet window to reassign the existing replicas away before the disk is pulled.
- **Why the others are wrong:** B — `log.dirs` is **read-only**, so `kafka-configs.sh` refuses the change; and Kafka never migrates partitions off a directory by itself. C — `log.dirs.offline` is not a Kafka configuration. D — unregistering the broker removes it from the cluster entirely, which is far more disruptive than the requirement and would take the healthy directories down with it.
- 🧠 **Key point / trap:** the decommission order is fixed and worth memorising: **cordon → reassign away → `kafka-cluster.sh unregister`**. Doing it in any other order means new partitions keep landing on the thing you are removing.
- 📎 Source: `resources/kafka-ops-topics-cordoning-leadership.md` (exact commands) and `resources/kip-1066-cordoned-log-dirs.md`.

### Question 12 — Answer: **A, C**

- **Why correct:** A is the definition — *"When a log directory is cordoned, it still fully functions but no new partitions can be allocated on it."* C combines the two documented consequences: `"*"` cordons every directory and therefore the broker, and a reassignment that targets a broker with no uncordoned directory is rejected with `INELIGIBLE_REPLICA`.
- **Why the others are wrong:** B — cordoning is purely a placement filter; moving existing partitions is still the job of `kafka-reassign-partitions.sh`. D — `cordoned.log.dirs` is **per-broker** (dynamic); it can be set in the properties file at startup *and* changed at runtime through the Admin client or `kafka-configs.sh`. E — cordoning never deletes anything.
- 🧠 **Key point / trap:** "cordon" borrows the Kubernetes meaning: stop scheduling new work here, leave running work alone. Option B is the tempting mis-reading.
- 📎 Source: `resources/kip-1066-cordoned-log-dirs.md`.

### Question 13 — Answer: **B**

- **Why correct:** two default-driven gates hold the cleaner back. First, the log cleaner — like retention — only works on **closed** segments, and with `segment.bytes` at 1 GiB a moderately busy partition can go a long time without rolling. Second, a log is only eligible once its dirty ratio reaches `min.cleanable.dirty.ratio` = **0.5**. Lowering `segment.ms` on the topic (and optionally `min.cleanable.dirty.ratio`) makes the cleaner engage.
- **Why the others are wrong:** A — `compact` alone reclaims space perfectly well; `compact,delete` additionally applies time/size retention, which is a different requirement. C — `log.cleaner.enable` defaults to **true**, and in 4.3 it is deprecated and slated for removal in Kafka 5.0 precisely so nobody turns it off. D — compaction genuinely rewrites segments and shrinks the log on disk; it is not a read-time filter.
- 🧠 **Key point / trap:** the phrase "only closed segments" is the single sentence that explains Lab 2.3 (retention) *and* Lab 2.4 (compaction) *and* the tiered-storage quick-start using a 1 MiB `segment.bytes`.
- 📎 Source: `resources/kafka-design-log-compaction.md` and `resources/kafka-broker-configs-storage-threads.md` (`log.cleaner.enable` deprecation note).

### Question 14 — Answer: **B, D**

- **Why correct:** B and D are two of the four documented guarantees — *"The offset for a message never changes. It is the permanent identifier for a position in the log."* and *"Any consumer that stays caught-up to within the head of the log will see every message that is written; these messages will have sequential offsets."*
- **Why the others are wrong:** A — the guarantee is weaker and precisely worded: a consumer reading from the start sees **at least** the final state of every key. The uncompacted head can still contain several versions of the same key, so "exactly one record per key" is false. C — *"Compaction will never re-order messages, just remove some."* E — inverted twice over: a tombstone is a record with a **non-null key and a null value**; records with a null **key** are rejected outright on a compacted topic.
- 🧠 **Key point / trap:** option A is the classic distractor for this whole domain. If an answer claims compaction leaves exactly one record per key, it is wrong.
- 📎 Source: `resources/kafka-design-log-compaction.md` (the four guarantees) and [`../../../CCDAK/study-plan/week-02/resources/kafka-log-compaction.md`](../../../CCDAK/study-plan/week-02/resources/kafka-log-compaction.md).

### Question 15 — Answer: **B**

- **Why correct:** a tombstone deletes the key, and then the tombstone itself is retained only for `delete.retention.ms` — default **86,400,000 ms (24 hours)** — before the cleaner removes it. A full rebuild that takes 31 hours can start reading a key's old value near the beginning of the log and reach the head after the corresponding tombstone has already been cleaned, so the deletion is never observed and the account comes back to life.
- **Why the others are wrong:** A — `acks` affects whether a write is durable at the moment it is made; these revocations were written weeks earlier and were clearly compacted into the log. C — `max.compaction.lag.ms` forces the cleaner to run *sooner* on slow topics; it does not shorten tombstone retention. D — `min.compaction.lag.ms` defaults to **0**, and it delays compaction of recent records rather than governing tombstones.
- 🧠 **Key point / trap:** the operational rule is "your bootstrap must finish well inside `delete.retention.ms`". The two fixes are to raise `delete.retention.ms` on the changelog topic or to make the rebuild faster.
- 📎 Source: `resources/kafka-design-log-compaction.md` (delete markers) and `resources/kafka-topic-configs-overrides.md` (`delete.retention.ms` 1 day).

### Question 16 — Answer: **C**

- **Why correct:** the requirement has two halves. "Keep the latest value per key so state can be rebuilt" is compaction; "reclaim storage for sessions older than 14 days" is time-based deletion. `cleanup.policy=compact,delete` runs both: the cleaner keeps the newest value per key, and retention still discards whole segments once they pass `retention.ms` = 1,209,600,000 ms (14 days).
- **Why the others are wrong:** A — plain `delete` would drop a session's latest value 14 days after it was *written*, even for sessions still being updated, and offers no per-key snapshot semantics. B — with `cleanup.policy=compact` alone, `retention.ms` is not applied, so old keys live forever. D — `delete.retention.ms` controls how long **tombstones** survive; it has nothing to do with expiring ordinary records.
- 🧠 **Key point / trap:** `delete.retention.ms` and `retention.ms` sound alike and mean completely different things. Whenever a scenario combines "latest value per key" with "and expire it eventually", the answer is `compact,delete`.
- 📎 Source: `resources/kafka-topic-configs-overrides.md` and [README.md](README.md) (the delete / compact / compact,delete table).

### Question 17 — Answer: **B**

- **Why correct:** the exception text names the configuration that rejected the record — `max.request.size` — and the absence of any broker-side log entry confirms the record was never transmitted. `max.request.size` (default **1,048,576**) is a producer-side guard. The complete fix has two parts, because the topic-side limit `max.message.bytes` (default **1,048,588**) will reject the record on the very next attempt.
- **Why the others are wrong:** A — a broker rejection produces a different message ("larger than the max message size the server will accept") **and** a broker log entry; neither is present. C — `replica.fetch.max.bytes` affects follower replication and never surfaces as a producer error; the first batch is always returned even if oversized, so replication does not stall. D — `socket.request.max.bytes` is 100 MiB and would not be reached by a 2 MiB record.
- 🧠 **Key point / trap:** the same exception class appears on both sides of the wire. Read the **message text**: if it quotes `max.request.size`, the fix is on the client; if it says "the server will accept", the fix is on the topic or broker.
- 📎 Source: `resources/kafka-broker-configs-storage-threads.md` (1048588 vs 1048576) and [`labs.md`](labs.md) Lab 2.5.

### Question 18 — Answer: **A**

- **Why correct:** the message and the broker-side `MESSAGE_TOO_LARGE` responses both point at the server-side limit. The narrowest, most reversible fix is a topic override: `max.message.bytes=5242880` applied with `kafka-configs.sh --entity-type topics`, which takes effect immediately with no restart. Raising `replica.fetch.max.bytes` (1,048,576) to at least the same value is the recommended follow-up so followers do not have to fetch one oversized batch at a time.
- **Why the others are wrong:** B — 1,048,576 is the **producer** default (`max.request.size`); the broker default is **1,048,588**, and setting the limit to 1,048,576 would make the problem worse. C — `max.partition.fetch.bytes` is a consumer-side ceiling and cannot influence whether the broker accepts a produce request. D — `buffer.memory` governs how much unsent data the producer may accumulate, not the maximum record size.
- 🧠 **Key point / trap:** memorise the pair **1,048,576 (producer `max.request.size`) vs 1,048,588 (broker `message.max.bytes` / topic `max.message.bytes`)**. The 12-byte difference is record-batch overhead, and an option that gives both the same value is a giveaway distractor.
- 📎 Source: `resources/kafka-broker-configs-storage-threads.md` and `resources/kafka-topic-configs-overrides.md`.

### Question 19 — Answer: **B**

- **Why correct:** *"Each log file is named with the offset of the first message it contains."* The highest-numbered segment is the one currently being appended to — the **active segment** — and it is exempt from retention, from the log cleaner, and from tiered-storage upload. The `.index` and `.timeindex` siblings carry the offset and timestamp indexes for the same segment.
- **Why the others are wrong:** A — the offset index is **sparse**: one entry roughly every `index.interval.bytes` (default 4096) of data, which is exactly why a 10 MiB index can cover a 1 GiB segment. C — the three `.log` files are consecutive ranges of the same partition, not copies; `num.recovery.threads.per.data.dir` concerns startup index rebuilding, not redundancy. D — Kafka appends to the **highest** offset, so the newest file is active.
- 🧠 **Key point / trap:** "active segment is untouchable" links four separate exam topics: retention, compaction, tiered storage and `kafka-dump-log.sh` output.
- 📎 Source: `resources/kafka-design-log-compaction.md` (Log implementation section) and `resources/kafka-topic-configs-overrides.md` (`index.interval.bytes`, `segment.index.bytes`).

### Question 20 — Answer: **B**

- **Why correct:** the access pattern — hot recent data, rare cold reads — is the canonical case for tiered storage. It needs **both** switches: `remote.log.storage.system.enable=true` at the broker level (read-only, so a rolling restart) and `remote.storage.enable=true` on the topic. Splitting retention into `local.retention.ms` ≈ 12 hours and `retention.ms` ≈ 13 months is what actually shrinks the broker disks.
- **Why the others are wrong:** A — this buys the 400 TB anyway, just on slower disks, and multiplies it by the replication factor. C — compaction keeps the latest value **per key**; a transaction log has effectively unique keys, so nothing would be reclaimed, and `compact` also makes the topic ineligible for tiered storage. D — MirrorMaker 2 gives you a second full copy to pay for and operate, and the compliance data would then live only on the mirror.
- 🧠 **Key point / trap:** every tiered-storage question hides one of two traps — forgetting the broker-level switch, or forgetting to lower `local.retention.ms` (default `-2` = inherit `retention.ms`).
- 📎 Source: `resources/kafka-tiered-storage.md`.

### Question 21 — Answer: **A, B, D**

- **Why correct:** A — the documentation lists compacted topics under unsupported features. B — `local.retention.ms` and `local.retention.bytes` default to `-2`, meaning "fall back to `retention.ms` / `retention.bytes`", so an operator who only flips the switches sees no disk savings at all. D — only closed segments are eligible for upload, which is why the official quick-start sets `segment.bytes=1048576` on the demo topic.
- **Why the others are wrong:** C — `remote.log.storage.system.enable` is **read-only**; turning tiered storage on for a running cluster means a rolling restart. E — disabling is the opposite of instant: the documentation requires deleting (or disabling) every tiered topic before the broker-level setting can be turned off, and remote segments are not copied back automatically.
- 🧠 **Key point / trap:** `remote.log.copy.disable=true` is the intermediate step people forget — it stops new uploads while the already-uploaded data stays readable.
- 📎 Source: `resources/kafka-tiered-storage.md` (limitations and quick-start) and [`labs.md`](labs.md) Lab 2.7.

### Question 22 — Answer: **A**

- **Why correct:** `auto.create.topics.enable` defaults to **true**. When a client produces to or fetches from a topic that does not exist, the broker creates it using `num.partitions` (default **1**) and `default.replication.factor` (default **1**) — which is exactly the fingerprint described. The fix is to set `auto.create.topics.enable=false`; because it is **read-only**, that means editing `server.properties` and rolling the cluster.
- **Why the others are wrong:** B — `delete.topic.enable` has defaulted to **true** since Kafka 1.0, and deleted topics do not resurrect on restart. C — the KRaft controller does not spontaneously recreate topics from a snapshot, and re-formatting the metadata log would destroy the cluster. D — `num.partitions` is read-only and applies only to topics created after the change; existing topics are never expanded automatically.
- 🧠 **Key point / trap:** "1 partition, RF 1, odd name" is the signature of auto-creation. And note the second half of the answer: the fix requires a restart, which is why production clusters should be built with it disabled from day one.
- 📎 Source: `resources/kafka-broker-configs-storage-threads.md` (`auto.create.topics.enable`, `delete.topic.enable`, `num.partitions`).

### Question 23 — Answer: **A**

- **Why correct:** every pairing matches the Kafka 4.3 configuration reference. The thread group (`num.io.threads` 8, `num.replica.fetchers` 1) is **cluster-wide**; `log.retention.ms` is **cluster-wide**; `log.dirs` and `queued.max.requests` are **read-only**.
- **Why the others are wrong:** B — inverts almost everything: `num.io.threads` and `log.retention.ms` are dynamic, `log.dirs` and `queued.max.requests` are not. C — `num.replica.fetchers` is cluster-wide, not read-only, and `log.dirs` cannot be changed per broker at runtime. D — the trap is `log.retention.hours`: the **`.hours`** variant is read-only, only the **`.ms`** variant is cluster-wide (and `queued.max.requests` is still read-only).
- 🧠 **Key point / trap:** the `.hours` / `.ms` pair appears twice — `log.retention.hours` (read-only) vs `log.retention.ms` (cluster-wide), and `log.roll.hours` (read-only) vs `log.roll.ms` (cluster-wide). To change either value on a live cluster you must use the `.ms` form.
- 📎 Source: `resources/kafka-broker-configs-storage-threads.md` (update mode columns).

### Question 24 — Answer: **A**

- **Why correct:** each of the four sources maps to exactly one way of writing it: topic overrides through `--entity-type topics --entity-name`, per-broker dynamic through `--entity-type brokers --entity-name <id>`, cluster-wide dynamic through `--entity-type brokers --entity-default`, and static through `server.properties` plus a restart.
- **Why the others are wrong:** B — `kafka-topics.sh --alter --config` no longer exists (topic configs moved to `kafka-configs.sh`), and it swaps `--entity-name` with `--entity-default`; `kafka-storage.sh format` initialises storage, it does not write configuration. C — ZooKeeper znodes were removed in Kafka 4.0; in KRaft these records live in the metadata log. D — swaps the per-broker and cluster-default commands, and `--bootstrap-controller` is a connection option, not a configuration source.
- 🧠 **Key point / trap:** `--entity-name` = *this one entity*; `--entity-default` = *everything that has no override*. Options that swap these two are the standard distractor.
- 📎 Source: `resources/confluent-dynamic-config-precedence.md` (all command variants).

### Question 25 — Answer: **A**

- **Why correct:** the sequence is **2 → 4 → 1 → 5 → 3**. Diagnose first (`kafka-log-dirs.sh` tells you which directory failed and which partitions are large — free information, zero risk), then free space, then restart the broker because an offline log directory is only re-adopted at startup, then verify that `UnderReplicatedPartitions` is back to 0, and finally add the guard rails (`retention.bytes`, smaller `segment.ms`) so it cannot recur.
- **Why the others are wrong:** B — restarting first is the most common panic move and achieves nothing: the disk is still full, so the directory fails again immediately. C — freeing space before knowing which topic is responsible means guessing, and it still restarts before diagnosing. D — restarting before freeing space has the same flaw as B.
- 🧠 **Key point / trap:** CCAAK repeatedly rewards the cheap, reversible, information-gathering step first. "Look with `kafka-log-dirs.sh`" beats "restart the broker" in essentially every storage scenario.
- 📎 Source: [README.md](README.md) (Playbook table) and [`labs.md`](labs.md) Lab 2.6 step 6.

### Question 26 — Answer: **A**

- **Why correct:** `kill -9` skips controlled shutdown, so logs are not flushed and segments are not cleanly closed; on restart the broker must run **log recovery**, rebuilding indexes for every unclean segment. That work is parallelised by `num.recovery.threads.per.data.dir`, whose default changed to **2** in Kafka 4.0 and whose update mode is **cluster-wide**, so it can be raised without another restart. The durable fix is graceful shutdown (`controlled.shutdown.enable=true`, the default), which both flushes logs and migrates leadership before the process exits.
- **Why the others are wrong:** B — leader election in KRaft takes seconds, not 47 minutes, and `controller.quorum.election.timeout.ms` is about controller elections, not broker startup. C — the default is **2**, not 1 (that was the pre-4.0 value), and the config is cluster-wide rather than read-only — both halves are wrong. D — the log cleaner runs after startup and does not block `Kafka Server started`.
- 🧠 **Key point / trap:** the pre-4.0 default of **1** for `num.recovery.threads.per.data.dir` is a documented version trap; older courses and dumps still quote it.
- 📎 Source: `resources/kafka-broker-configs-storage-threads.md` (default 2, cluster-wide) and `resources/kafka-ops-topics-cordoning-leadership.md` (graceful shutdown).

### Question 27 — Answer: **B**

- **Why correct:** the operations documentation is unambiguous: *"Kafka does not currently support reducing the number of partitions for a topic."* Reducing partitions would break key-to-partition mapping and force the broker to decide what to do with data in the removed partitions. The practical route is a new topic with the desired partition count plus a copy (MirrorMaker 2, a Streams job, or a simple consume-produce application) and a planned consumer cutover.
- **Why the others are wrong:** A — the command is rejected; there is no merge mechanism. C — `--zookeeper` was removed in Kafka 4.0 (KRaft-only) and never supported shrinking partitions anyway; this option is doubly wrong and is the version trap in this question. D — `num.partitions` is read-only and only affects topics created afterwards; preferred leader election moves leadership, not partition counts.
- 🧠 **Key point / trap:** partition count is a **one-way door**. That is also why Week 4's sizing formula deliberately adds growth headroom — you can add partitions later, but never remove them.
- 📎 Source: `resources/kafka-ops-topics-cordoning-leadership.md` (Modifying topics).

### Question 28 — Answer: **B**

- **Why correct:** `--delete-config` removes one entry from the precedence chain; the effective value then comes from the **next surviving source**. Here the chain below the deleted topic override is `DYNAMIC_DEFAULT_BROKER_CONFIG:log.retention.ms=259200000`, then the static 604,800,000, then the built-in default. So the answer is **259,200,000 ms** (3 days).
- **Why the others are wrong:** A and C — both assume `--delete-config` jumps straight to a fixed value (static or shipped default), skipping the dynamic cluster-wide entry that is still in place. D — the override really is removed and takes effect immediately; no topic recreation is involved.
- 🧠 **Key point / trap:** "delete an override" does not mean "restore the documented default". Always re-run `--describe --all` afterwards and read the new first entry of `synonyms`.
- 📎 Source: `resources/confluent-dynamic-config-precedence.md` and [`labs.md`](labs.md) Lab 2.1 step 7.

### Question 29 — Answer: **A**

- **Why correct:** `kafka-metadata-quorum.sh describe --status` reports the KRaft metadata quorum: the current leader id, leader epoch, high watermark, and the lag of each voter and observer. That is exactly the health check to run before a rolling restart on a KRaft cluster.
- **Why the others are wrong:** B — ZooKeeper was removed in Kafka 4.0, so `zookeeper-shell.sh` and the `/controller` znode no longer exist; this is the version trap. C — `kafka-configs.sh` reports configuration, not quorum health. D — `kafka-cluster.sh cluster-id` returns only the cluster identifier.
- 🧠 **Key point / trap:** the Week 1 reflex carries into every later week — any answer that reaches for ZooKeeper on Kafka 4.x is wrong by construction.
- 📎 Source: [`../../CCAAK-STUDY-PLAN.md`](../../CCAAK-STUDY-PLAN.md) §7 (symptom table, `ActiveControllerCount`) and [`../../../CCDAK/study-plan/week-01/resources/kafka-operations-kraft.md`](../../../CCDAK/study-plan/week-01/resources/kafka-operations-kraft.md).

### Question 30 — Answer: **A, B**

- **Why correct:** A — Kafka never rebalances existing partitions onto a newly added broker; that is a deliberate operator action via `kafka-reassign-partitions.sh`, and the throttle should be removed with `--verify` once the move completes. B — placement of **new** topics and **new** partitions does consider the new broker, so an empty broker is expected immediately after scale-out and suspicious only if topics have been created since.
- **Why the others are wrong:** C — `auto.leader.rebalance.enable` redistributes **leadership** among existing replicas; it cannot create a replica where none exists. D — `controller.quorum.voters` lists controllers, not brokers; a broker-only node is not a voter, and partition placement does not depend on it. E — `cordoned.log.dirs=""` is already the default (no directory cordoned), so setting it changes nothing.
- 🧠 **Key point / trap:** "new broker sits idle" is one of the most frequently recycled CCAAK scenarios, and the answer is always `kafka-reassign-partitions.sh` with a throttle — never an automatic mechanism.
- 📎 Source: [`../../../CCDAK/study-plan/week-08/resources/kafka-basic-ops-reassignment.md`](../../../CCDAK/study-plan/week-08/resources/kafka-basic-ops-reassignment.md) and [`../../CCAAK-STUDY-PLAN.md`](../../CCAAK-STUDY-PLAN.md) §7.

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (24+/30) | Đạt ngưỡng cá nhân cho domain nặng nhất của đề. | Review 100% câu sai, ghi vào sổ câu sai kèm *lý do sai*. Sang [Tuần 3](../week-03/README.md) và giữ nhịp — nhớ rằng **mini-mock CFG ≥70% là checkpoint bắt buộc cuối Tuần 3**. |
| **70–79%** (21–23/30) | Gần đạt, còn lỗ hổng cục bộ. | Xác định nhóm yếu nhất trong 5 nhóm (ưu tiên config / update mode / `log.dirs` & JBOD / retention & segment / compaction), đọc lại đúng mục đó ở [Buổi A](README.md#-buổi-a--lý-thuyết-3h) và **làm lại lab tương ứng**. Sang Tuần 3 được, nhưng đánh dấu nhóm yếu để ôn thêm trước checkpoint. |
| **< 70%** (≤ 20/30) | Chưa sẵn sàng đi tiếp. | **Đừng sang Tuần 3.** CFG chiếm **22%** đề và Tuần 3 xây tiếp trên đúng nền này. Học lại toàn bộ Buổi A, làm lại **cả 7 lab** (đặc biệt 2.1, 2.2, 2.6), rồi làm lại bộ 30 câu này sau 2 ngày. |

### Bảng chấm theo nhóm — khoanh vùng chỗ yếu

| Nhóm | Câu hỏi | Đạt khi đúng |
| --- | --- | --- |
| Thứ tự ưu tiên config & synonyms | 3, 4, 24, 28 | ≥ 3/4 |
| Update mode (động vs restart) | 1, 2, 23, 26 | ≥ 3/4 |
| `log.dirs`, JBOD, cordon | 7, 8, 9, 10, 11, 12 | ≥ 5/6 |
| Retention, segment, dung lượng | 5, 6, 19, 25 | ≥ 3/4 |
| Compaction & tombstone | 13, 14, 15, 16 | ≥ 3/4 |
| Message size & tiered storage | 17, 18, 20, 21 | ≥ 3/4 |
| Vận hành chung + ôn Tuần 1 | 22, 27, 29, 30 | ≥ 3/4 |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / dính bẫy / hết giờ), và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may cũng tính là câu sai.
