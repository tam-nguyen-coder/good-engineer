# ✅ Answers & Explanations — Week 1: Operational Foundations + KRaft in Production

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-C · 4-B · 5-D · 6-A · 7-A · 8-AC · 9-C · 10-A · 11-B · 12-D · 13-AD · 14-A · 15-A · 16-C · 17-D · 18-C · 19-AC · 20-A · 21-B · 22-AC · 23-AE · 24-B · 25-C · 26-AE · 27-B · 28-A

---

### Question 1 — Answer: **B**

- **Why correct:** a Raft quorum stays available only while a **majority** of voters is alive, so `2N+1` voters tolerate `N` failures. Four voters need a majority of three, which means they survive exactly **one** failure — the same as three voters, at the cost of an extra machine and an extra vote on every metadata append. To survive two simultaneous losses you need **five**.
- **Why the others are wrong:** A — "two left out of four" is not a majority of four, so the quorum is dead. C — there is no `observer` value for `process.roles`; the valid values are `broker`, `controller` and `broker,controller`, and brokers become metadata observers automatically. D — six is even, so it needs a majority of four and still tolerates only two failures while being more expensive and slower than five.
- 🧠 **Key point / trap:** even numbers are always the wrong answer for quorum sizing. Memorise the ladder: **3 → survives 1**, **5 → survives 2**, and **4 → survives 1** (the trap option).
- 📎 Source: `resources/kraft-operations-production.md` (quorum sizing, `2N+1`).

### Question 2 — Answer: **C**

- **Why correct:** in KRaft, the active controller is the **leader** of the single partition of `__cluster_metadata`, other controllers are **followers**, and **brokers are observers**: they replicate the metadata log so they always hold a fresh cache, but they do not vote in controller elections. Nodes appearing under `CurrentObservers` are therefore the brokers.
- **Why the others are wrong:** A — standby controllers appear in `CurrentVoters`, not `CurrentObservers`. B — observers never "graduate" into voters; membership changes only through `add-controller` on a dynamic quorum. D — fencing is a broker-registration state and has nothing to do with the observer list; a mismatched `directory.id` would not show the node here at all.
- 🧠 **Key point / trap:** three words, three roles — **Leader** (active controller), **Follower** (standby controller), **Observer** (broker). They are literally the values of the `Status` column in `describe --replication`.
- 📎 Source: `resources/confluent-control-plane-course.md` ("The active controller is the leader of this internal metadata topic's single partition. Other controllers are replica followers. Brokers are replica observers.").

### Question 3 — Answer: **C**

- **Why correct:** `InconsistentClusterIdException` means the `cluster.id` recorded in this node's `meta.properties` does not match the cluster it is trying to join. The diagnosis is mechanical: read `meta.properties`, read the real `ClusterId` from `kafka-metadata-quorum.sh describe --status`, and re-format the log directory with the cluster's actual ID (using `--no-initial-controllers` for a node joining an existing cluster). The usual root cause is a provisioning script that calls `kafka-storage.sh random-uuid` on every machine instead of once.
- **Why the others are wrong:** A — there is no ZooKeeper in Kafka 4.x; this is the version trap. B — `broker.id.generation.enable` was removed in KRaft, and the problem is the cluster ID, not the node ID. D — `controller.quorum.fetch.timeout.ms` is a liveness timer inside the quorum; no timeout value will make a mismatched cluster ID acceptable.
- 🧠 **Key point / trap:** the exception names the exact comparison it failed. Read the two IDs in the message before touching anything — one of them is the cluster's, the other is the node's.
- 📎 Source: `resources/kafka-quickstart-and-storage-format.md` (contents of `meta.properties`, diagnosis procedure) and `resources/kraft-operations-production.md`.

### Question 4 — Answer: **B**

- **Why correct:** in combined mode the controller runs inside the same JVM and on the same disks as the broker, so a broker-side GC pause or an I/O stall directly delays the controller's Raft traffic. The quorum's liveness timer is `controller.quorum.fetch.timeout.ms`, **2000 ms** — an order of magnitude tighter than anything on the data plane — so a compaction-induced stall easily triggers a new election. This is exactly why the documentation says combined mode is "not recommended in critical deployment environments" and Confluent does not support it in production.
- **Why the others are wrong:** A — a fourth combined node adds the same interference and does not raise the failure tolerance above one. C — `replica.lag.time.max.ms` governs ISR membership on the data plane; it has no effect on controller elections. D — `auto.leader.rebalance.enable` moves **partition** leadership towards preferred replicas; it never triggers a controller election.
- 🧠 **Key point / trap:** whenever a question mixes a data-plane symptom with a control-plane symptom, ask which timer is involved. Controller problems are measured in **seconds** (1000 / 2000 ms), ISR problems in **tens of seconds** (30000 ms).
- 📎 Source: `resources/kraft-operations-production.md` (combined mode wording) and `resources/broker-configs-kraft-and-threads.md` (quorum timers).

### Question 5 — Answer: **D**

- **Why correct:** metadata mutations — creating a topic, altering a config, registering a broker — must be appended to `__cluster_metadata` by the **active controller**. With no controller majority there is no active controller, so `CreateTopics` is forwarded and then times out. Meanwhile each broker still holds a complete metadata cache, so it keeps serving produce and fetch for partitions whose leadership has not changed. The correct first action is to restore controller majority; reconfiguring anything else is both impossible and dangerous.
- **Why the others are wrong:** A — no data was lost; the log directories on the brokers are untouched. B — `unclean.leader.election.enable` affects partition-leader selection, which itself requires a controller; it cannot create a topic. C — the cluster is **not** healthy: it is one broker failure away from offline partitions, because no new leader can be elected. Changing the bootstrap flag would not help either, since the controllers are down.
- 🧠 **Key point / trap:** "writes still work but admin commands time out" is the signature of **quorum loss**. The danger is not what is broken now but what breaks next — with no controller, a single broker failure becomes permanent partition unavailability.
- 📎 Source: `resources/confluent-control-plane-course.md` (⚖️ ghi chú kiểm chứng) and `resources/kraft-operations-production.md` ("A majority of the controllers must be alive in order to maintain availability").

### Question 6 — Answer: **A**

- **Why correct:** `Observer` is the status of a node that replicates the metadata log without being a voter. In practice these are the brokers: any node whose `process.roles` does not include `controller` fetches `__cluster_metadata` like a follower but is excluded from elections and from the majority calculation.
- **Why the others are wrong:** B — `replica.lag.time.max.ms` governs ISR membership for ordinary partitions and has nothing to do with the Raft quorum; a lagging controller is still a `Follower`. C — a node that cannot find the quorum does not appear in the output at all. D — a controller that lost an election becomes a `Follower`, not an `Observer`.
- 🧠 **Key point / trap:** voter count is decided by `process.roles`, not by health. Adding brokers never changes the size of the quorum.
- 📎 Source: `resources/confluent-control-plane-course.md` and `resources/kraft-operations-production.md` (`describe --replication`).

### Question 7 — Answer: **A**

- **Why correct:** the documentation states it explicitly: if `kraft.version` shows `FinalizedVersionLevel: 0`, the cluster is using a **static** quorum. With a static quorum the voter set lives in `controller.quorum.voters` on every node — brokers included — so replacing a controller means editing that property everywhere and restarting. The online `add-controller` / `remove-controller` commands require `kraft.version=1` (KIP-853).
- **Why the others are wrong:** B — `kraft.version` is a KRaft **feature level**, not an on/off switch for KRaft itself; ZooKeeper does not exist in 4.x at all. C — `metadata.version` tracks the metadata record format, not quorum membership; being at 4.3 says nothing about dynamic voters. D — `kafka-metadata-shell.sh` is a read-only inspection tool; you cannot edit quorum membership with it.
- 🧠 **Key point / trap:** two different feature levels, two different meanings. `metadata.version` = "which metadata records may be written" (upgrades). `kraft.version` = "static or dynamic quorum" (membership).
- 📎 Source: `resources/kraft-operations-production.md` (`kafka-features.sh` check) and `resources/kip-500-kip-853-kraft-evolution.md`.

### Question 8 — Answer: **A, C**

- **Why correct:** A — brokers keep an in-memory metadata cache built by replaying the metadata log, so a partition whose leader has not changed continues to accept produce and fetch requests without consulting a controller. C — every metadata mutation (`--create`, `--alter`, ACL changes, quota changes, broker registration) must be committed to `__cluster_metadata` by the active controller, and with no majority there is no active controller.
- **Why the others are wrong:** B — offset commits are **data plane**: the client writes to `__consumer_offsets` via its group coordinator, which is an ordinary broker. They keep working. D — brokers do not drop client connections when the controller is unreachable; that is the whole point of the cached metadata. E — this is exactly what **cannot** happen: electing a new partition leader is a metadata change and requires the controller.
- 🧠 **Key point / trap:** option E is the most dangerous distractor because it sounds like normal Kafka behaviour. During quorum loss, replication and failover are frozen — the cluster is running on borrowed time.
- 📎 Source: `resources/confluent-control-plane-course.md` (⚖️ ghi chú kiểm chứng) and `resources/kafka-design-replication-isr.md`.

### Question 9 — Answer: **C**

- **Why correct:** ZooKeeper was removed in Kafka **4.0**; **3.9** was the last bridge release that could migrate a ZooKeeper cluster to KRaft. Every admin CLI now uses `--bootstrap-server`, and commands that must talk to a controller directly use `--bootstrap-controller`. KIP-1147 completed this unification.
- **Why the others are wrong:** A — there is no `--zk-connect` option; the whole ZooKeeper code path is gone, so the rest of the 2.x runbook needs review too. B — `zookeeper.connect` was removed along with every other `zookeeper.*` configuration. D — controllers do not ship ZooKeeper client libraries; nothing in a 4.x distribution speaks the ZooKeeper protocol.
- 🧠 **Key point / trap:** this is the single most common way public CCAAK question banks are wrong. Any option mentioning `--zookeeper`, a znode, or `zookeeper.connect` is a guaranteed distractor on a 4.x cluster.
- 📎 Source: `resources/zk2kraft-removed-configs-and-cli.md` and `CCDAK/study-plan/VALIDATION.md` (row 13: CLI unified on `--bootstrap-server`, KIP-1147).

### Question 10 — Answer: **A**

- **Why correct:** `metadata.log.dir` defaults to `null`, and the documentation states that when it is unset the metadata log is placed in the **first** directory listed in `log.dirs` — here `/data/1`, the very device that is busy with compaction. Pointing `metadata.log.dir` at a dedicated device removes the contention at its source, which is the cheapest and most reversible fix.
- **Why the others are wrong:** B — smaller metadata segments do not reduce contention; they increase the number of files. C — controllers can have several log directories; the problem is *which* directory holds the metadata log, not how many exist. D — raising `controller.quorum.append.linger.ms` from 25 to 1000 batches appends more aggressively and makes every metadata operation slower, masking the symptom while hurting the control plane.
- 🧠 **Key point / trap:** "defaults to the **first** entry of `log.dirs`" is the detail the question is really testing. On a combined node this silently puts the Raft log on the same spindle as the hottest partitions.
- 📎 Source: `resources/broker-configs-kraft-and-threads.md` (`metadata.log.dir` default `null`).

### Question 11 — Answer: **B**

- **Why correct:** `kafka-dump-log.sh --cluster-metadata-decoder` is the documented way to decode the metadata log's binary records into readable metadata events, pointed at the segment file under `__cluster_metadata-0/`. The same tool with the same flag also decodes snapshot (`.checkpoint`) files.
- **Why the others are wrong:** A — `__cluster_metadata` is not a normal topic served to clients; the console consumer cannot read it and it is not exposed through the broker's fetch path for clients. C — `kafka-log-dirs.sh` reports sizes and offsets per log directory, not record contents. D — `describe --replication` reports per-node replication progress of the quorum; there is no `--verbose` record dump.
- 🧠 **Key point / trap:** for reading metadata **records** use `kafka-dump-log.sh --cluster-metadata-decoder`; for browsing the resulting **state** use `kafka-metadata-shell.sh --snapshot`. Two tools, two jobs.
- 📎 Source: `resources/kraft-operations-production.md` (Debugging Tools).

### Question 12 — Answer: **D**

- **Why correct:** `ActiveControllerCount` is 1 on the node that currently holds metadata-log leadership and 0 everywhere else, so the cluster-wide sum should be exactly 1. A sustained sum of 0 means no active controller has been elected — normally because the quorum has lost its majority or is stuck in an election. The next command is `kafka-metadata-quorum.sh describe --status` to see `LeaderId` and `CurrentVoters`.
- **Why the others are wrong:** A — controllers do expose the metric; the panel is fine. B — two active controllers would make the sum 2, not 0, and a sum above 1 is its own (split-brain) alarm. C — inverted logic; 0 is precisely the failure condition.
- 🧠 **Key point / trap:** alert on the **sum across nodes ≠ 1**, not on a single node's value. A brief 0 during failover is normal; four minutes of 0 is an outage.
- 📎 Source: `CCAAK-STUDY-PLAN.md` §7 (`ActiveControllerCount` row) and `resources/kraft-operations-production.md`.

### Question 13 — Answer: **A, D**

- **Why correct:** A — a node joining an existing cluster is formatted with the cluster's **existing** cluster ID and `--no-initial-controllers`, which tells the storage tool that the quorum already exists. D — once the new controller has started and caught up on the metadata log, `kafka-metadata-quorum.sh add-controller` adds it to the voter set online. The order matters: catch up first, then add, so the quorum never depends on a voter that is behind.
- **Why the others are wrong:** B — `--standalone` bootstraps a **new** quorum with this node as the only voter; using it against an existing cluster creates a second, conflicting cluster. C — a fresh cluster ID is exactly what produces `InconsistentClusterIdException`; the cluster ID must be shared by all nodes. E — editing `controller.quorum.voters` and restarting brokers is the **static** quorum procedure; on a dynamic quorum the voter set lives in the metadata log.
- 🧠 **Key point / trap:** the three format flags are mutually exclusive and encode intent — `--standalone` = "I am the first", `--initial-controllers` = "here is the whole quorum", `--no-initial-controllers` = "the quorum already exists, I am joining".
- 📎 Source: `resources/kraft-operations-production.md` (Node Provisioning, Controller Membership Changes).

### Question 14 — Answer: **A**

- **Why correct:** the order is `random-uuid` → `format` → `server-start` → verify. The cluster ID must exist before formatting, formatting must happen before the server starts (a KRaft node refuses to start on an unformatted log directory), and the quorum can only be described once a process is listening.
- **Why the others are wrong:** B — you cannot format with a cluster ID that has not been generated. C and D — starting the server before formatting fails immediately; this is the single biggest behavioural difference from the ZooKeeper era, where a broker registered itself on first start.
- 🧠 **Key point / trap:** CCAAK uses *list order* questions, and this three-step sequence is the most likely one to appear. Say it out loud until it is automatic: **generate, format, start**.
- 📎 Source: `resources/kafka-quickstart-and-storage-format.md` (Step 2).

### Question 15 — Answer: **A**

- **Why correct:** 1-Y `kafka-log-dirs.sh --describe` reports, per broker and per log directory, which partitions live there and how many bytes each uses. 2-W `kafka-metadata-quorum.sh describe --status` reports `LeaderId`, `CurrentVoters` and `CurrentObservers`. 3-X `kafka-configs.sh --describe --all` prints the effective value plus the `synonyms` list showing which level it came from. 4-Z `kafka-features.sh describe` shows `kraft.version`, which distinguishes a static quorum (0) from a dynamic one (1).
- **Why the others are wrong:** B — swaps the quorum question onto `kafka-features.sh` and the feature question onto `kafka-metadata-quorum.sh`. C — swaps the disk question onto `kafka-configs.sh`. D — swaps the config-precedence question onto `kafka-features.sh`.
- 🧠 **Key point / trap:** CCAAK rewards knowing **which tool answers which question** far more than knowing every flag. Build the reflex: quorum → `metadata-quorum`, effective config → `configs --all`, disk → `log-dirs`, feature level → `features`.
- 📎 Source: `resources/basic-kafka-operations-admin-cli.md` and `resources/kraft-operations-production.md`.

### Question 16 — Answer: **C**

- **Why correct:** the `zk2kraft` page lists `advertised.listeners` among the configurations that **no longer support dynamic updates** in KRaft mode. The error message says so directly. The only way to change it is to edit the broker's properties file and restart that broker — which, done one broker at a time with `controlled.shutdown.enable=true`, is still a zero-downtime operation for the cluster as a whole.
- **Why the others are wrong:** A — listener configuration belongs to the broker, and the controller bootstrap does not make a read-only config writable. B — `listener.security.protocol.map` maps listener names to protocols; it does not change which configs are dynamically updatable. D — `meta.properties` holds identity (`cluster.id`, `node.id`, `directory.id`), not listeners; deleting it causes a far worse failure.
- 🧠 **Key point / trap:** "fix it without restarting" is a classic CCAAK qualifier, and for `advertised.listeners` on KRaft the honest answer is that you cannot. Recognise the small set of read-only configs rather than assuming everything is dynamic.
- 📎 Source: `resources/zk2kraft-removed-configs-and-cli.md` (Dynamic Configuration Removal).

### Question 17 — Answer: **D**

- **Why correct:** KRaft removed `broker.id.generation.enable` and `reserved.broker.max.id`. Identity is now explicit: every node needs a stable `node.id`, chosen by the operator and written into `meta.properties` at format time. Automatic identifier allocation no longer exists, because there is no ZooKeeper sequence to allocate from.
- **Why the others are wrong:** A — `reserved.broker.max.id` was removed along with the generation feature. B — passing a removed configuration on the command line does not resurrect it. C — `broker.id=-1` was the ZooKeeper-era way to request generation; `directory.id` identifies a **log directory** for quorum membership, not the node.
- 🧠 **Key point / trap:** this is a version trap disguised as a configuration-management question. Stable, operator-assigned identity is a deliberate design choice in KRaft, not an oversight.
- 📎 Source: `resources/zk2kraft-removed-configs-and-cli.md` (Broker Identification).

### Question 18 — Answer: **C**

- **Why correct:** the preferred leader is the **first** entry of each `Replicas` list — 2, 3 and 4 respectively — but broker 4 leads all three partitions, so the cluster is leader-imbalanced after the restart. `kafka-leader-election.sh --election-type preferred --all-topic-partitions` restores it immediately, and because `auto.leader.rebalance.enable` defaults to `true` the broker would also do it on its own within `leader.imbalance.check.interval.seconds` (default **300**).
- **Why the others are wrong:** A — leadership concentration is a real problem: broker 4 now handles every produce request and every follower fetch for this topic. B — reassignment moves **replicas** (expensive, copies data); the replicas are already correctly placed, only leadership is wrong. D — unclean election allows an out-of-sync replica to become leader and can lose data; the ISR here is complete, so there is nothing for it to fix.
- 🧠 **Key point / trap:** read the `Replicas` list left to right. Preferred leader = first element. Fixing leadership is cheap and instant; fixing placement is expensive and copies bytes — never confuse the two.
- 📎 Source: `resources/basic-kafka-operations-admin-cli.md` (Balancing Leadership) and `resources/broker-configs-kraft-and-threads.md` (`leader.imbalance.check.interval.seconds` 300).

### Question 19 — Answer: **A, C**

- **Why correct:** A — the `synonyms` list is printed in **precedence order**, and `DYNAMIC_TOPIC_CONFIG` sits at the top, so the topic-level override of 3 is what the broker enforces. C — because the topic override wins, editing the broker-level value has no effect on this topic until the override is deleted with `kafka-configs.sh --alter --delete-config min.insync.replicas --entity-type topics --entity-name payments`.
- **Why the others are wrong:** B — the precedence is the opposite: `DYNAMIC_TOPIC_CONFIG` > `DYNAMIC_BROKER_CONFIG` > `DYNAMIC_DEFAULT_BROKER_CONFIG` > `STATIC_BROKER_CONFIG` > `DEFAULT_CONFIG`. D — `DEFAULT_CONFIG` is always listed as the built-in fallback; its presence says nothing about whether the broker was configured, and in fact `STATIC_BROKER_CONFIG:min.insync.replicas=2` proves it was. E — the `synonyms` column is printed for topic entities too; that is exactly what this output shows.
- 🧠 **Key point / trap:** the real CCAAK skill here is not memorising the precedence list but knowing that `--all` prints it and that **you should read it before changing anything**. Most "I changed the config and nothing happened" incidents are an override one level up.
- 📎 Source: `CCAAK-STUDY-PLAN.md` §4 (config precedence order) and `resources/basic-kafka-operations-admin-cli.md` (`kafka-configs.sh`).

### Question 20 — Answer: **A**

- **Why correct:** the JSON shows one partition, `clickstream-0`, holding roughly 41 GB while `orders-1` holds about 104 MB — the imbalance is caused by partition placement, not by retention or corruption. The correct remedy is to move partitions with `kafka-reassign-partitions.sh`, throttled so that the migration does not saturate replication bandwidth, and to remember that `--verify` is the step that **removes** the throttle once the move completes.
- **Why the others are wrong:** B — `offsetLag: 0` means the replica is caught up; it is a health indicator, not a corruption flag. C — Kafka assigns **new** partitions to log directories by partition count, and adding a directory does not retroactively rebalance existing partitions. D — cutting retention cluster-wide to fix one broker's skew punishes every topic and destroys data that other consumers may still need; it is neither targeted nor reversible.
- 🧠 **Key point / trap:** forgetting `--verify` leaves `leader.replication.throttled.rate` and `follower.replication.throttled.rate` in place, quietly capping replication for weeks. This shows up later as "URP takes forever to clear".
- 📎 Source: `resources/basic-kafka-operations-admin-cli.md` (Limiting Bandwidth During Data Migration, `--generate`/`--execute`/`--verify`).

### Question 21 — Answer: **B**

- **Why correct:** the `zk2kraft` documentation states that dynamic log levels use a different syntax for controllers: target them with `--bootstrap-controller <controller-host>:9093`, while the entity type remains `broker-loggers`. Controllers listen only on the `CONTROLLER` listener and are not reachable through a broker's client bootstrap.
- **Why the others are wrong:** A — entity name 1 refers to the node ID, but the request is sent through a broker bootstrap, which cannot reach a controller-only node. C — `--bootstrap-server` cannot be pointed at the controller listener, and there is no `controller-loggers` entity type. D — controller log levels **are** changeable at runtime; a restart is unnecessary and would disturb the quorum.
- 🧠 **Key point / trap:** remember the pair — the **flag** changes (`--bootstrap-controller`), the **entity type** does not (`broker-loggers`). This asymmetry is exactly what makes it a good exam question.
- 📎 Source: `resources/zk2kraft-removed-configs-and-cli.md` (CLI Tool Changes).

### Question 22 — Answer: **A, C**

- **Why correct:** A — the data plane uses the ISR model. "A write is committed only when all in-sync replicas have received it", and **any** ISR member is eligible for leadership, which is why `f+1` replicas tolerate `f` failures without any voting round. C — the control plane uses Raft: candidates increment the epoch and send `VoteRequest` including their last offset and its epoch; a follower grants the vote only if the candidate's log is "the same or higher than its own", and the candidate needs a **majority**.
- **Why the others are wrong:** B — partition leadership involves no vote at all, and `replication.factor` has no odd/even requirement (RF 2 and RF 4 are legal, just unwise). D — the lowest-`node.id` rule does not exist; Raft elections are driven by epochs and log completeness. E — `replica.lag.time.max.ms` is a data-plane-only timer; the quorum uses `controller.quorum.fetch.timeout.ms` (2000 ms).
- 🧠 **Key point / trap:** one cluster, two consistency mechanisms. Mixing them up is the most reliable way to lose Fundamentals points — the phrase "majority" belongs to the controller quorum and **never** to partition replication.
- 📎 Source: `resources/kafka-design-replication-isr.md` (ISR, f+1) and `resources/confluent-control-plane-course.md` (VoteRequest, epoch).

### Question 23 — Answer: **A, E**

- **Why correct:** A — `offsets.topic.replication.factor` defaults to **3**, so on a single-broker cluster the controller cannot create `__consumer_offsets` and every consumer group fails; the fix is to lower it to 1. E — `transaction.state.log.replication.factor` (default **3**) and `transaction.state.log.min.isr` (default **2**) fail for exactly the same reason as soon as a transactional producer appears, so a single-broker setup must lower those too.
- **Why the others are wrong:** B — inverted: `offsets.topic.num.partitions` defaults to **50**, not 1. C — `__consumer_offsets` has 50 partitions; the single-partition internal topic is `__cluster_metadata`. D — `min.insync.replicas` has a valid range starting at 1, so 0 is rejected, and it is not what blocks topic creation here.
- 🧠 **Key point / trap:** this is the number-one reason a hand-built single-node lab "starts fine but nothing works". The broker comes up healthy because internal topics are created **lazily**, on first use.
- 📎 Source: `resources/broker-configs-kraft-and-threads.md` (internal topic defaults 50 / 3 / 3 / 2).

### Question 24 — Answer: **B**

- **Why correct:** the documented order is `remove-controller` **before** shutting the node down. Removing it while a majority is still available shrinks the voter set cleanly — a three-voter quorum becomes a two-voter quorum — so the cluster never passes through a state where the remaining voters cannot reach a majority. The command needs both `--controller-id` and `--controller-directory-id`, because KIP-853 identifies a voter by the pair.
- **Why the others are wrong:** A — shutting down first is exactly the failure mode the ordering exists to prevent: with 3 voters, losing one leaves 2 of 3 (still a majority, but with zero margin), and the removal call itself may not be servable if the timing is unlucky. C — deleting `meta.properties` destroys the node's identity including its `directory.id`, which makes clean removal harder, not easier. D — editing `controller.quorum.bootstrap.servers` only changes **discovery**; membership lives in the metadata log on a dynamic quorum.
- 🧠 **Key point / trap:** the two membership commands are mirror images with opposite timing — `add-controller` **after** the node has caught up, `remove-controller` **before** the node goes away.
- 📎 Source: `resources/kraft-operations-production.md` (Controller Membership Changes) and `resources/kip-500-kip-853-kraft-evolution.md`.

### Question 25 — Answer: **C**

- **Why correct:** KRaft replaced `inter.broker.protocol.version` with `metadata.version`, a cluster-wide **feature level** finalised with `kafka-features.sh upgrade --release-version 4.3`. It is a single online operation applied through the controller; there is no second rolling restart.
- **Why the others are wrong:** A — `inter.broker.protocol.version` was removed; setting it does nothing (and on some paths is rejected as an unknown config). B — the metadata version is **not** derived from the binaries: it stays at the old level deliberately, so that a downgrade remains possible until you finalise. Skipping the finalisation leaves new features permanently disabled. D — re-running `kafka-storage.sh format` on a populated log directory is destructive and is not how versions are managed.
- 🧠 **Key point / trap:** the upgrade has two halves — roll the binaries, then **finalise the feature level**. Teams that forget the second half spend months wondering why a 4.3 feature "does not exist" on their 4.3 cluster.
- 📎 Source: `resources/zk2kraft-removed-configs-and-cli.md` (Protocol Versioning) and `CCAAK-STUDY-PLAN.md` §5 (rolling upgrade).

### Question 26 — Answer: **A, E**

- **Why correct:** A — with RF 3 and one broker down the ISR holds 2 replicas, which still satisfies `min.insync.replicas=2`, so `acks=all` writes keep succeeding. This is precisely the guarantee the RF 3 / min.isr 2 / `acks=all` triple buys: survive **one** broker failure without losing either data or write availability. E — `auto.leader.rebalance.enable` defaults to `true`, so once broker 3 rejoins and catches up, leadership returns to its preferred partitions within `leader.imbalance.check.interval.seconds` (default 300).
- **Why the others are wrong:** B — `UnderReplicatedPartitions` counts partitions whose ISR is smaller than the replica set, so it is now greater than 0 even though `min.insync.replicas` is still satisfied. These are two different thresholds: URP compares ISR to **RF**, `UnderMinIsrPartitionCount` compares ISR to **min.isr**. C — leadership moved to a replica that was already **in** the ISR; `unclean.leader.election.enable=false` is what guarantees that. D — a broker stopped with controlled shutdown migrates leadership and leaves the ISR promptly; the 30-second lag timer applies to a replica that falls behind, not to a clean stop.
- 🧠 **Key point / trap:** distinguishing `UnderReplicatedPartitions` from `UnderMinIsrPartitionCount` is a recurring Observability question. URP > 0 means "degraded"; `UnderMinIsrPartitionCount` > 0 means "`acks=all` writes are being rejected right now".
- 📎 Source: `resources/kafka-design-replication-isr.md` and `CCAAK-STUDY-PLAN.md` §7 (metric rows).

### Question 27 — Answer: **B**

- **Why correct:** the exception says the ISR is down to a single replica. Lowering `min.insync.replicas` to 1 would restore writes, but it removes the durability guarantee at the exact moment the cluster is least able to protect data: with one replica holding the only copy, an acknowledged write is lost outright if that broker dies. The administrator's first action is to bring a failed broker back so the ISR recovers. Lowering the minimum is a deliberate, time-boxed availability-over-durability trade-off that someone must own — not a reflex.
- **Why the others are wrong:** A — "no risk" is false; the risk is unacknowledged data loss. C — `acks=1` makes it worse, not better: it bypasses `min.insync.replicas` entirely and acknowledges on the leader alone. D — unclean leader election permits an out-of-sync replica to become leader, which **discards** committed records; it trades away more durability than lowering the minimum, not less.
- 🧠 **Key point / trap:** CCAAK repeatedly tests whether you reach for the cheap, reversible action first. "Restore the broker" is reversible; "lower the durability floor during an incident" is how data actually gets lost.
- 📎 Source: `CCDAK/study-plan/week-02/resources/kafka-replication-isr.md` and `CCAAK-STUDY-PLAN.md` §7 (`NotEnoughReplicas` row).

### Question 28 — Answer: **A**

- **Why correct:** the group coordinator for a group is the broker hosting the **leader** of the `__consumer_offsets` partition selected by `hash(group.id) % 50`. If that broker goes down, commits fail until a new leader is elected for that internal partition and the clients re-issue `FindCoordinator`. The group's own data partitions being healthy is irrelevant — the coordinator is chosen by the group name, not by where the data lives.
- **Why the others are wrong:** B — offset commits never go to the KRaft controller; they are ordinary writes to an ordinary (internal) topic. C — `__consumer_offsets` has **50** partitions, not one, which is precisely why only some groups are affected by a given broker failure. D — deleting and re-creating the group would discard committed offsets and cause reprocessing or data skipping; the coordinator recovers on its own.
- 🧠 **Key point / trap:** three different "leader/controller" concepts live in one cluster — **group coordinator** (a broker, chosen per group), **partition leader** (a broker, chosen per partition), **active controller** (a controller, one per cluster). Questions that blur them are common.
- 📎 Source: `CCDAK/study-plan/week-04/resources/confluent-consumer-group-protocol-course.md` (coordinator selection, 50 partitions).

---

## 🧭 Chấm điểm theo chủ đề

Đếm số câu đúng theo nhóm để biết phải quay lại mục nào của [README](README.md):

| Nhóm | Câu | Quay lại đọc |
|---|---|---|
| Quorum sizing & topology | 1, 4, 13, 24 | Buổi A mục 3–5, Bảng quyết định 1 |
| Format storage & cluster id | 3, 14, 17 | Buổi A mục 6, Lab 1.2 |
| Control plane vs data plane | 2, 5, 6, 8, 12, 22 | Buổi A mục 2, 7, 8, 10 · Lab 1.3 |
| Di sản ZooKeeper (bẫy version) | 9, 16, 21, 25 | Buổi A mục 9, `resources/zk2kraft-removed-configs-and-cli.md` |
| Chọn đúng công cụ CLI | 7, 10, 11, 15, 19, 20 | Buổi A mục 11 · Lab 1.4, 1.5 |
| Replication & ISR ở góc admin | 18, 23, 26, 27, 28 | Buổi A mục 10 · Lab 1.6 |

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (23+/28) | Đạt ngưỡng cá nhân. | Review 100% câu sai, ghi sổ kèm **lý do sai**. Làm xong 6 lab (đặc biệt 1.2 và 1.3 phải làm lại **không nhìn hướng dẫn**) rồi sang Tuần 2. |
| **70–79%** (20–22/28) | Gần đạt, còn lỗ hổng cục bộ. | Xác định nhóm yếu nhất ở bảng *Chấm điểm theo chủ đề*, đọc lại đúng mục đó trong Buổi A + làm lại lab tương ứng. Làm lại bộ câu hỏi sau **2 ngày**. Vẫn được sang Tuần 2 nếu qua được Cổng tự kiểm tra. |
| **< 70%** (≤ 19/28) | Chưa sẵn sàng. | **Chưa sang Tuần 2.** Đọc lại toàn bộ Buổi A, làm lại cả 6 lab, rồi làm lại bộ câu hỏi. Tuần 1 là nền của cả 7 tuần sau — hổng ở đây thì Tuần 2–3 (Cluster Config, 22%) sẽ không đứng được. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / dính bẫy / hết giờ), và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may cũng tính là câu sai.

---

> ✅ Xong phần lý thuyết? Quay lại [Lab checklist trong README](README.md#-lab-checklist) và hoàn thành 6 lab trong [labs.md](labs.md) trước khi mở Tuần 2 — đề CCAAK hỏi *hành động của người vận hành*, thứ chỉ hình thành khi bạn đã tự tay làm hỏng và sửa một cluster.
