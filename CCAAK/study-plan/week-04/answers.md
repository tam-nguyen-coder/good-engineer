# ✅ Answers & Explanations — Week 4: Deployment Architecture

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [labs](labs.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-AB · 4-B · 5-B · 6-B · 7-A · 8-B · 9-A · 10-B · 11-AC · 12-B · 13-B · 14-C · 15-B · 16-A · 17-A · 18-AB · 19-A · 20-AC · 21-AC · 22-B · 23-AC · 24-B · 25-A · 26-(1-D, 2-A, 3-C, 4-E, 5-B) · 27-A · 28-B

---

### Question 1 — Answer: **B**

- **Why correct:** the throughput-based rule is `max(t/p, t/c)` where `t` is the target throughput, `p` the per-partition producer throughput and `c` the per-partition consumer throughput. Here `450/60 = 7.5` and `450/25 = 18`, so **18** partitions. In practice the consumer side almost always dominates, because a single partition can absorb tens of MB/s of produce traffic while application processing is much slower.
- **Why the others are wrong:** A — uses only the producer term and ignores the consumer term, which is the binding constraint. C — "one partition per MB/s" is not a rule; it conflates a throughput figure with a count. D — replication factor creates copies for durability, not parallel readers; only the leader serves produce traffic and, without follower fetching, consumers too.
- 🧠 **Key point / trap:** the exam gives you both `p` and `c` precisely so you pick the **larger** quotient. And remember the follow-up that always comes next: partitions can be increased but **never decreased**, so add growth headroom now.
- 📎 Source: `resources/confluent-sizing-capacity-planning.md` (formula `max(t/p, t/c)`).

### Question 2 — Answer: **C**

- **Why correct:** `80 MB/s × 259,200 s (3 days) = 20.7 TB` for one copy. Multiply by `replication.factor = 3` → **62.2 TB**, then apply the 20% headroom factor → **≈ 75 TB**.
- **Why the others are wrong:** A — 21 TB is a single copy with no replication and no headroom; this is the classic "forgot RF" distractor. B — 62 TB applies RF but skips the headroom the question explicitly mentions. D — 249 TB multiplies by 4 somewhere (e.g. treating RF=3 as "3 followers plus the leader").
- 🧠 **Key point / trap:** the disk formula is `throughput × retention × RF × headroom`. Forgetting RF gives exactly one third of the right answer, which is always one of the options. If the question mentions **tiered storage**, the local disk figure uses `local.retention.*` instead of the full retention.
- 📎 Source: `resources/confluent-sizing-capacity-planning.md` (disk sizing) and [week plan](README.md) Buổi A mục 2.

### Question 3 — Answer: **A, B**

- **Why correct:** A is the documented file-handle cost — each partition is a directory and each segment contributes an index file and a log file, with real clusters reported running *"more than 30 thousand open file handles per broker"*. B is the one-way-door property: `--alter --partitions` only increases, so an over-sized topic keeps paying metadata, replication and leader-election cost forever.
- **Why the others are wrong:** C — `min.insync.replicas` is an independent static/dynamic configuration and is never derived from partition count. D — a consumer group can own many partitions per member; 500 partitions merely set the **upper bound** on parallelism, they do not require 500 consumers. E — replication factor is bounded by the number of **brokers**, not by any ratio to partitions; 500 partitions with RF=3 on 6 brokers is perfectly legal.
- 🧠 **Key point / trap:** the four real costs are **file descriptors · unavailability during unclean broker failure (~5 ms per partition, 1000 partitions ≈ 5 s) · end-to-end latency (~20 ms per 1000 replicated partitions) · client memory (tens of KB per partition)**. Documented practical ceilings: 2,000–4,000 partitions per broker and low tens of thousands per cluster.
- 📎 Source: `resources/confluent-sizing-capacity-planning.md` (costs of excessive partitions).

### Question 4 — Answer: **B**

- **Why correct:** capacity must hold **after** losing one broker, so `(N − 1) × 10 TB ≥ 120 TB` → `N − 1 ≥ 12` → `N ≥ 13`.
- **Why the others are wrong:** A — 12 brokers gives exactly 120 TB **only while all 12 are alive**; losing one leaves 110 TB and the cluster runs out of space. C — 14 works but the question asks for the **minimum**. D — the 120 TB figure already includes replication ("including replication and headroom"), so multiplying by 3 again double-counts.
- 🧠 **Key point / trap:** whenever the stem says *"must still work if one broker/rack is lost"*, size for **N − 1** (or for the loss of a whole rack), not for N. The same reasoning applies to CPU and network, not just disk.
- 📎 Source: `resources/confluent-sizing-capacity-planning.md` (cluster configuration) and [week plan](README.md) Buổi A mục 2.

### Question 5 — Answer: **B**

- **Why correct:** three symptoms line up into one story. A 48 GB heap leaves only ~16 GB for the OS page cache, so reads that used to be served from memory now hit disk (rising disk read throughput). The oversized heap also produces multi-second full GCs, during which the broker stops sending and answering fetch requests, so followers fall outside `replica.lag.time.max.ms` and the ISR shrinks and expands repeatedly. Confluent's guidance is explicit: Kafka *"does not require setting heap sizes more than 6 GB"*, leaving the rest of RAM for the file system cache.
- **Why the others are wrong:** A — raising `replica.lag.time.max.ms` hides the ISR churn without fixing the pauses, and makes genuine follower failures take four times longer to detect. C — more fetcher threads do not shorten a stop-the-world GC; the broker is not running during the pause. D — unclean leader election trades data loss for availability and does nothing about GC; it is the classic "correct-sounding but far too aggressive" distractor.
- 🧠 **Key point / trap:** Kafka's performance comes from **page cache**, not heap. "More heap = faster" is backwards, and ISR flapping plus long GC is the signature of an over-sized heap.
- 📎 Source: `resources/confluent-sizing-capacity-planning.md` (memory: 6 GB heap, 28–30 GB page cache).

### Question 6 — Answer: **B**

- **Why correct:** the root cause is that broker work and controller work share a JVM. The KRaft documentation states that combined servers are *"simpler to operate for small use cases like a development environment"* but that *"the controller will be less isolated from the rest of the system"* and that **"combined mode is not recommended in critical deployment environments"**. Dedicated controller nodes mean a broker-side GC pause can never trigger a controller failover.
- **Why the others are wrong:** A — adding more combined nodes multiplies the problem; every new node still couples a broker to a voter. C — raising the election timeout masks the coupling and delays genuine controller failover detection. D — turning every node into a controller leaves no brokers at all; controllers do not serve produce or fetch requests.
- 🧠 **Key point / trap:** the exam phrase to recognise is *"a single event caused both a controller failover and a leader change"* — that is combined mode. Production minimum is **3 brokers + 3 controllers**, and controller machines are much smaller (~4–5 GB RAM).
- 📎 Source: `resources/kafka-kraft-controller-topology.md` (process roles, deployment considerations).

### Question 7 — Answer: **A**

- **Why correct:** a KRaft quorum needs a majority of voters alive. With 5 controllers the majority is 3, so up to **2** may fail — the documented rule is that tolerating N concurrent failures requires **2N + 1** controllers. A 2/2/1 layout means the largest single-AZ loss removes 2 controllers, still leaving 3, which is a majority.
- **Why the others are wrong:** B — availability depends on the **quorum**, not on how many active controllers are needed; losing 4 of 5 leaves 1, far below a majority. C — the majority rule counts voters, not their locations; two failures anywhere are survivable. D — there is no requirement that the number of AZs equals the number of controllers; spreading 5 controllers over 3 AZs is the normal cloud pattern.
- 🧠 **Key point / trap:** always check the *worst single-AZ loss* as well as the raw count. A 3/1/1 layout of 5 controllers would still tolerate 2 failures in the abstract, but losing the AZ holding 3 controllers would break the quorum.
- 📎 Source: `resources/kafka-kraft-controller-topology.md` (controllers, 2N+1 rule).

### Question 8 — Answer: **B**

- **Why correct:** the controller quorum is a Raft group. Without a majority it cannot commit new metadata records, so anything that *writes* metadata — creating topics, electing new leaders, registering a restarted broker — blocks. Brokers, however, keep serving produce and fetch from the metadata they already have cached, so partitions whose leadership is unchanged continue to work. That is exactly the split reported.
- **Why the others are wrong:** A — the cached metadata is not stale for unchanged partitions, and stopping producers is unnecessary panic. C — `auto.create.topics.enable` affects implicit creation by clients, not an explicit `--create` call, and would return an error rather than hang. D — brokers are **observers** of the metadata log; they never vote and can never promote themselves to controller.
- 🧠 **Key point / trap:** memorise the split — **control plane frozen, data plane alive**. The first diagnostic command is `kafka-metadata-quorum.sh describe --status` to see `LeaderId` and `CurrentVoters`.
- 📎 Source: `resources/kafka-kraft-controller-topology.md` (majority rule, observers) and [week plan](README.md) Buổi A mục 3.

### Question 9 — Answer: **A**

- **Why correct:** the documentation says to determine the quorum type from this feature: if `kraft.version` is at `FinalizedVersionLevel` **1 or above** the cluster uses **dynamic** quorums (`controller.quorum.bootstrap.servers`, KIP-853); level **0** means a **static** quorum defined by `controller.quorum.voters`. With a static quorum, the voter set lives in configuration files, so adding a controller means editing the voter list on every node and restarting — `kafka-metadata-quorum.sh add-controller` is only available with dynamic quorums.
- **Why the others are wrong:** B — inverted; level 0 is static, not dynamic. C — `metadata.version` is unrelated to quorum membership, and downgrading it is not supported here anyway. D — there is no ZooKeeper in Kafka 4.x; `/controller` znodes stopped existing when ZooKeeper support was removed in 4.0.
- 🧠 **Key point / trap:** a single number in `kafka-features.sh describe` tells you which whole operational procedure applies. Option D is the version trap: any answer mentioning znodes, `--zookeeper` or `zookeeper.connect` is wrong on a 4.x cluster.
- 📎 Source: `resources/kafka-kraft-controller-topology.md` (static versus dynamic quorums) and `resources/kafka-rolling-upgrade-kraft.md`.

### Question 10 — Answer: **B**

- **Why correct:** the `kafka-broker-api-versions.sh` output shows only **two** racks: brokers 2 and 3 are both in `az-a`, broker 4 is alone in `az-b`. Rack-aware placement guarantees a partition spans `min(#racks, replication.factor)` racks, which here is `min(2, 3) = 2`. Every replica list (`2,3,4`) therefore puts two replicas in `az-a`. Losing `az-a` leaves one in-sync replica, below `min.insync.replicas=2`, so `acks=all` writes are rejected with `NotEnoughReplicasException`.
- **Why the others are wrong:** A — rack awareness guarantees *as many racks as possible*, not one replica per rack; with only two racks it cannot do better. C — broker 4 in `az-b` is a replica of every partition, so a leader can always be elected; partitions are under-min-ISR, not offline. D — Kafka never auto-creates replacement replicas; replica lists change only through reassignment.
- 🧠 **Key point / trap:** read the **rack list**, not the replica list. The rule to survive the loss of one rack is "number of racks ≥ RF" (or at least no rack holding two or more replicas), and `min(#racks, RF)` is the formula that tells you whether you have it.
- 📎 Source: `resources/kafka-ops-expanding-reassignment.md` (balancing replicas across racks) and [Lab 4.2](labs.md#lab-42--brokerrack-rải-replica-qua-rack-rồi-tắt-cả-một-rack--gây-hỏng-rồi-sửa).

### Question 11 — Answer: **A, C**

- **Why correct:** A quotes the placement guarantee directly. C quotes the documented consequence of uneven racks: *"Racks with fewer brokers will get more replicas, meaning they will use more storage and put more resources into replication. Hence it is sensible to configure an equal number of brokers per rack."*
- **Why the others are wrong:** B — the opposite of C; Kafka balances **leaders** per broker, not replicas per rack. D — `broker.rack` is a **read-only** broker configuration, so it requires a restart; it cannot be altered dynamically. E — RF=4 on 3 racks still puts two replicas in one rack, so losing two racks can leave you with a single replica or none; the extra copy costs 33% more storage without buying two-rack tolerance.
- 🧠 **Key point / trap:** "increase RF" is the seductive wrong answer to every rack question. Surviving the loss of *k* racks needs enough **racks**, not more replicas in the same racks.
- 📎 Source: `resources/kafka-ops-expanding-reassignment.md` (rack awareness) and Apache Kafka 4.3 broker configs (`broker.rack`, update-mode read-only).

### Question 12 — Answer: **B**

- **Why correct:** follower fetching (KIP-392) needs all three pieces. `broker.rack` lets each broker declare its zone; `replica.selector.class=RackAwareReplicaSelector` replaces the default leader-only selector so the broker can nominate a `PreferredReadReplica`; `client.rack` tells the broker where the consumer is. With any one missing the leader keeps serving every fetch.
- **Why the others are wrong:** A — `client.rack` alone changes nothing, because the broker's default selector always returns the leader. This is the most commonly chosen wrong answer. C — neither `fetch.from.follower` nor `follower.fetching.enable` is a Kafka configuration; they are invented names. D — preferred leader election moves leaders to the **first replica in each list**, which is a placement decision, not a per-consumer one, and would simply move the cross-zone cost onto producers.
- 🧠 **Key point / trap:** three pieces, two of them on the **broker**. If an option only touches the client, it is incomplete.
- 📎 Source: `resources/kip-392-follower-fetching.md` (public interfaces) and `resources/confluent-multi-dc-architectures.md` (follower fetching section).

### Question 13 — Answer: **B**

- **Why correct:** KIP-392 changes only the **fetch** path. Produce requests always go to the partition leader, because the leader owns the log-end offset and the ISR. On the read side, only replicas in the ISR are eligible to be a preferred read replica, and a follower serves records only up to the high watermark it knows about — so consumers never see uncommitted data, but may see it a fetch round later than a leader reader would.
- **Why the others are wrong:** A — no replica forwards writes to the leader; clients route produce requests to the leader themselves using metadata. C — only one replica accepts writes for a partition at any time; that is the core of Kafka's ordering guarantee. D — follower fetching does not interact with `acks` at all; durability is unchanged.
- 🧠 **Key point / trap:** follower fetching buys **cost**, not speed. It may even add a little read latency. Any option framing it as a throughput or write-latency optimisation is wrong.
- 📎 Source: `resources/kip-392-follower-fetching.md` (correctness constraints).

### Question 14 — Answer: **C**

- **Why correct:** RPO = 0 requires synchronous replication, which only a single (stretched) cluster provides — and Confluent's guidance allows a stretched cluster when the link is stable and sub-100 ms, which a 2 ms dark fibre satisfies. But two datacenters give an even split of the controller quorum: losing either site can leave exactly half the voters, so no majority survives. The documented answer is the **2.5-datacenter** topology — a third, lightweight site running only KRaft controllers — which keeps the quorum odd and guarantees a majority survives the loss of either full datacenter.
- **Why the others are wrong:** A — this is the trap: it satisfies the latency requirement but not the quorum requirement. B and D — MirrorMaker 2 and Cluster Linking are both **asynchronous**; Confluent's own comparison table lists RPO > 0 and RTO > 0 for both, so neither can meet RPO = 0.
- 🧠 **Key point / trap:** "two datacenters" plus "RPO = 0" is always the 2.5-DC question. The third site needs no brokers and no application traffic — only controllers.
- 📎 Source: `resources/confluent-multi-dc-architectures.md` (stretched 2.5-datacenter cluster, comparison table).

### Question 15 — Answer: **B**

- **Why correct:** Cluster Linking is built into Confluent Server, so the destination brokers pull directly from the source with *"byte-for-byte replication"* and *"globally consistent offsets"*. No Connect cluster, no connectors, no tasks — that is the "fewest components to operate" requirement. Because offsets are identical, consumers resume at exactly the same position with no translation step.
- **Why the others are wrong:** A — `IdentityReplicationPolicy` preserves **topic names**, not offsets; this is the single most common confusion in this topic. C — `sync.group.offsets.enabled` writes **translated** offsets, and translation is deliberately conservative (never ahead of the true position), so equality is not guaranteed; it also still requires the whole MirrorMaker 2 / Connect stack. D — a stretched cluster is not a DR *site* design here and imposes latency constraints the question never mentions.
- 🧠 **Key point / trap:** map the words directly — *"identical offsets"* → **Cluster Linking**; *"identical topic names"* → `IdentityReplicationPolicy` **or** Cluster Linking. They are not the same requirement.
- 📎 Source: `resources/confluent-cluster-linking.md` (byte-for-byte, no Connect) and `resources/kafka-geo-replication-mm2.md` (offset translation).

### Question 16 — Answer: **A**

- **Why correct:** on plain Apache Kafka the only cross-cluster replication tool is MirrorMaker 2, and active-active means two flows, `A->B` and `B->A`. `DefaultReplicationPolicy` renames replicated topics to `{source}.{topic}`, which is precisely what prevents a record from being mirrored back and forth forever. Applications in each region read the local topic plus the remote-prefixed one.
- **Why the others are wrong:** B — `IdentityReplicationPolicy` keeps the same topic name on both sides, so `A->B` and `B->A` would feed each other in an infinite loop; the docs restrict it to migration and active-passive. C — Cluster Linking does not exist on Apache Kafka; it requires Confluent Server (destination 7.8.0 or later). D — a stretched cluster is one cluster, not two regions accepting writes independently, and the question gives no latency guarantee.
- 🧠 **Key point / trap:** the renaming in `DefaultReplicationPolicy` is a **loop-prevention mechanism**, not a cosmetic choice. Whenever the stem says active-active, the answer keeps the default policy.
- 📎 Source: `resources/kafka-geo-replication-mm2.md` (replication flows, topic naming).

### Question 17 — Answer: **A**

- **Why correct:** the log shows MirrorMaker started and configured both clusters, but no `creating herder for A->B` line and no connector startup — because **replication flows are disabled by default**. The documented default is `{source}->{target}.enabled = false`, and the flow must be enabled explicitly. Setting `A->B.topics` alone does nothing if the flow itself is off.
- **Why the others are wrong:** B — per-flow `topics` settings are fully supported and take precedence; the top-level default is already `.*`. C — `replication.policy.class` has a default (`DefaultReplicationPolicy`) and is optional. D — `--whitelist` belongs to MirrorMaker **1**, which was removed in Kafka 4.0; `connect-mirror-maker.sh` takes a properties file and an optional `--clusters`.
- 🧠 **Key point / trap:** this is the number-one first-time MirrorMaker 2 mistake and a recurring exam item. Option D is the version trap.
- 📎 Source: `resources/kafka-geo-replication-mm2.md` (`{source}->{target}.enabled` default `false`) and [Lab 4.4](labs.md#lab-44--mirrormaker-2-giữa-2-cluster-local-).

### Question 18 — Answer: **A, B**

- **Why correct:** A is the documented default exclusion list — `groups.exclude = console-consumer-.*, connect-.*, __.*` — so a console consumer's auto-generated group id is filtered out before replication. B is the documented safety rule for `sync.group.offsets.enabled`: translated offsets are written into the destination's `__consumer_offsets` only while the group is **not active** there, so an already-running consumer group on B is never overwritten underneath it.
- **Why the others are wrong:** C — offset replication is handled by `MirrorCheckpointConnector` and is independent of the replication policy. D — exactly-once source support (3.5.0+) concerns duplicate-free record replication, not whether offsets are translated. E — inverted: `MirrorSourceConnector` copies records and topic configuration, `MirrorCheckpointConnector` handles offsets, and `MirrorHeartbeatConnector` produces heartbeats.
- 🧠 **Key point / trap:** when testing MirrorMaker 2 offset translation, always use a **named** consumer group and make sure the group is **idle on the destination**. Both mistakes look like "offset sync is broken".
- 📎 Source: `resources/kafka-geo-replication-mm2.md` (`groups.exclude`, consumer offset translation) and [Lab 4.4](labs.md#lab-44--mirrormaker-2-giữa-2-cluster-local-) bước 6.

### Question 19 — Answer: **A**

- **Why correct:** `IdentityReplicationPolicy` is exactly the policy the documentation recommends for migration and active-passive: replicated topics keep their original names so application configuration does not change. What it does **not** change is offsets — the destination is a different log, so committed offsets differ and must still come from checkpoints or `sync.group.offsets.enabled`.
- **Why the others are wrong:** B — an empty separator would make `{source}{topic}` = `Aorders`, not `orders`, and the source alias is not removable. C — the false half of the classic confusion: identical names do not imply identical offsets; that property belongs to Cluster Linking. D — MirrorMaker 2 explicitly supports name preservation through the replication policy; a hand-written consumer/producer pair would also lose partitioning and configuration replication.
- 🧠 **Key point / trap:** `IdentityReplicationPolicy` must not be used for active-active, because without the source prefix nothing breaks the replication loop.
- 📎 Source: `resources/kafka-geo-replication-mm2.md` (topic naming, replication policy).

### Question 20 — Answer: **A, C**

- **Why correct:** A is the defining operational property — mirror topics are read-only on the destination and become writable only after a promote or failover. C is the defining data property: byte-for-byte replication with globally consistent offsets, which is why no translation step exists.
- **Why the others are wrong:** B — Cluster Linking is a Confluent Server / Confluent Cloud feature; there is no `kafka-cluster-links.sh` in an Apache Kafka distribution (verify it yourself with `ls /opt/kafka/bin`). D — there is no bidirectional link mode; *"bidirectional replication requires two separate unidirectional links."* E — inverted: the documented limitations state that **transactional messages cannot be mirrored**.
- 🧠 **Key point / trap:** option B is the product-identification trap. If the stem says "Apache Kafka", every Cluster Linking option is wrong; if the stem says "Confluent Platform 7.8+", Cluster Linking becomes the strongest DR answer.
- 📎 Source: `resources/confluent-cluster-linking.md` (mirror topics, limitations) and [Lab 4.7](labs.md#lab-47--concept-cluster-linking-vì-sao-không-chạy-được-ở-đây-và-khác-mm2-chỗ-nào).

### Question 21 — Answer: **A, C**

- **Why correct:** A is the documented finalization step: once every node runs the new binaries and behaviour has been verified, run `kafka-features.sh ... upgrade --release-version 4.3`. C is the documented downgrade restriction: *"Cluster metadata downgrade is not supported in this version since it has metadata changes"* for 4.3.0 (each `MetadataVersion` carries a flag indicating whether it introduced metadata changes).
- **Why the others are wrong:** B — `inter.broker.protocol.version` **does not exist in KRaft**; it was replaced by `metadata.version`, managed through `kafka-features.sh`. This is the version trap of the question. D — downgrades are not "always supported"; 4.2.0 happens to be downgradeable because it introduced no metadata changes, but 4.3.0 and 4.0.x are not. E — nothing is finalized automatically; the two-phase design exists precisely so that you can roll back the software before committing to the new metadata version.
- 🧠 **Key point / trap:** rolling upgrade in KRaft is always **two phases** — restart every node one at a time waiting for URP = 0, then finalize. Anything mentioning IBP belongs to the ZooKeeper era.
- 📎 Source: `resources/kafka-rolling-upgrade-kraft.md` (rolling upgrade, downgrade rules, removed configs).

### Question 22 — Answer: **B**

- **Why correct:** the documentation is explicit: *"these new servers will not automatically be assigned any data partitions, so unless partitions are moved to them they won't be doing any work until new topics are created."* The `kafka-log-dirs.sh` output showing 0 bytes on brokers 5 and 6 is exactly that state. The remedy is the three-step reassignment flow, with a throttle so the copy does not saturate replication, followed by `--verify`.
- **Why the others are wrong:** A — restarting brokers changes leadership at most, never replica placement. C — `auto.leader.rebalance.enable` moves **leadership** between existing replicas; a broker with no replicas can never become a leader. D — deleting and recreating a production topic destroys the data the question is trying to preserve.
- 🧠 **Key point / trap:** replica placement in Kafka changes only through **reassignment** (or a tool such as Cruise Control that drives reassignment for you). Nothing rebalances data by itself.
- 📎 Source: `resources/kafka-ops-expanding-reassignment.md` (expanding your cluster) and [Lab 4.5](labs.md#lab-45--thêm-broker-thứ-4-reassignment-có-throttle-và-gỡ-throttle).

### Question 23 — Answer: **A, C**

- **Why correct:** A — `--execute` prints the current assignment together with the line *"Save this to use as the --reassignment-json-file option during rollback"*; that JSON is the only easy way back. C — the documentation warns that *"it is important that administrators remove the throttle in a timely manner once rebalancing completes by running the command with the `--verify` option"*, and lists the broker-level `leader.replication.throttled.rate` / `follower.replication.throttled.rate` plus the topic-level throttled-replica lists that stay behind otherwise.
- **Why the others are wrong:** B — the throttle is not removed on completion; that is precisely the trap, and the residue shows up weeks later as replication that can never catch up. D — the throttle can be changed mid-flight by re-running `--execute` with `--additional` and the same JSON file. E — replication throttles apply to **replication** traffic only; client quotas are a separate mechanism (`producer_byte_rate`, `consumer_byte_rate`).
- 🧠 **Key point / trap:** remember the sentence "`--verify` is the command that removes the throttle". A cluster with mysterious, persistent `UnderReplicatedPartitions` after a migration almost always has a forgotten throttle.
- 📎 Source: `resources/kafka-ops-expanding-reassignment.md` (limiting bandwidth during data migration).

### Question 24 — Answer: **B**

- **Why correct:** the replica lists are unchanged, so no data needs to move — only leadership. `kafka-leader-election.sh --election-type preferred --all-topic-partitions` restores leadership to the first replica in each list and completes in seconds with zero data transfer. That makes it both the correct and the cheapest first action.
- **Why the others are wrong:** A — reassignment copies partition data across the network to solve a problem that is purely about leadership; it is the "correct-sounding but far too expensive" option. C — `leader.imbalance.per.broker.percentage` is **not used in KRaft**, so tuning it has no effect; the background rebalance is driven by `auto.leader.rebalance.enable` and `leader.imbalance.check.interval.seconds` (300 s), which would also be slower than acting now. D — Kafka 4.x has no ZooKeeper and no `--zookeeper` flag.
- 🧠 **Key point / trap:** two version traps in one question. Learn the split: **reassignment moves replicas (copies data); leader election moves leadership (copies nothing)**.
- 📎 Source: `resources/kafka-ops-expanding-reassignment.md` (balancing leadership) and `resources/kafka-rolling-upgrade-kraft.md` (configs removed in KRaft).

### Question 25 — Answer: **A** (4 → 3 → 2 → 1)

- **Why correct:** the documented decommission sequence is: **(4)** cordon the broker's log directories with `cordoned.log.dirs="*"` so the controller stops placing new partitions on it; **(3)** reassign every replica off the broker and `--verify` that it finished, so no partition ever drops below `min.insync.replicas`; **(2)** stop the Kafka process, which performs a controlled shutdown; **(1)** unregister the node with `kafka-cluster.sh unregister --id 7` so the controller forgets it.
- **Why the others are wrong:** B — stopping the broker first makes every partition it hosts under-replicated during the whole reassignment, exactly what the requirement forbids. C — reassigning before cordoning lets the controller place new partitions back onto broker 7 while you are draining it, and unregistering a running broker is wrong. D — unregistering first, while the broker is alive and holds data, is the most destructive ordering of all.
- 🧠 **Key point / trap:** the mental model is **drain, then remove**: stop new work arriving → move existing work away → shut down → deregister. The exam's list-order questions on Kafka maintenance almost always reward this pattern.
- 📎 Source: `resources/kafka-ops-expanding-reassignment.md` (decommissioning brokers) and [Lab 4.5](labs.md#lab-45--thêm-broker-thứ-4-reassignment-có-throttle-và-gỡ-throttle) bước 9.

### Question 26 — Answer: **1-D · 2-A · 3-C · 4-E · 5-B**

- **Why correct:**
  - **1 → D.** Aggregation across several Apache Kafka clusters is the `A->K, B->K, C->K` MirrorMaker 2 pattern, and `DefaultReplicationPolicy` prefixes each remote topic with its source alias, which is how the origin stays visible in the name.
  - **2 → A.** "No acknowledged message is ever lost" is RPO = 0, and only a stretched cluster replicates synchronously; both asynchronous tools are documented as RPO > 0.
  - **3 → C.** Confluent Platform to Confluent Cloud with identical names **and** identical committed offsets is the byte-for-byte, offset-preserving property of Cluster Linking.
  - **4 → E.** Reading without cross-zone charges **inside one cluster** is follower fetching, which needs all three settings.
  - **5 → B.** Moving existing partitions onto newly added brokers is partition reassignment.
- **Why the others are wrong:** the common mis-pairings are 1→C (Cluster Linking keeps names identical, so five sources would collide on the destination and it is not available on Apache Kafka anyway), 3→D (MirrorMaker 2 changes offsets and, with the default policy, names too), and 2→C or 2→D (both asynchronous, so neither can reach RPO = 0).
- 🧠 **Key point / trap:** each requirement carries one decisive keyword — *origin visible in the name* · *no acknowledged message lost* · *identical offsets* · *inside a single cluster* · *newly added brokers*. Find that word first, then pick the mechanism.
- 📎 Source: `resources/confluent-multi-dc-architectures.md`, `resources/confluent-cluster-linking.md`, `resources/kafka-geo-replication-mm2.md`, `resources/kip-392-follower-fetching.md`, `resources/kafka-ops-expanding-reassignment.md`.

### Question 27 — Answer: **A**

- **Why correct:** with `replication.factor=3`, `min.insync.replicas=3` means every single replica must be in the ISR for an `acks=all` write to succeed — so taking any one broker down stops writes immediately. Setting `min.insync.replicas=2` keeps the durability guarantee (two copies of every acknowledged record) while tolerating exactly one missing replica. RF 3 + min.isr 2 + `acks=all` is the canonical production triple.
- **Why the others are wrong:** B — `acks=1` acknowledges after the leader alone writes, so a leader failure loses acknowledged data; the requirement says no data loss. C — unclean leader election deliberately allows an out-of-sync replica to become leader, which is data loss by design, and it is not even relevant here since a leader still exists. D — RF 5 with min.isr 3 would work, but it costs 67% more storage and network than simply lowering min.isr, and the question asks what to change, not what to rebuild.
- 🧠 **Key point / trap:** `min.insync.replicas` equal to the replication factor is the classic over-correction. With RF=3 the answer for surviving one failure is always **2**.
- 📎 Source: [CCDAK Week 2 — `kafka-replication-isr.md`](../../../CCDAK/study-plan/week-02/resources/kafka-replication-isr.md) and [CCAAK master plan §5 — Durability](../../CCAAK-STUDY-PLAN.md#5-deep-dive-từng-mảng-vận-hành).

### Question 28 — Answer: **B**

- **Why correct:** retention is evaluated per **log segment**, and the **active** segment — the one currently being appended to — is never eligible for deletion. A segment only rolls when it reaches `segment.bytes` (1 GiB by default) or `segment.ms`. On a low-traffic topic neither happens for a long time, so nothing is ever deleted despite a one-hour retention. Lowering `segment.ms` (or `segment.bytes`) on the topic makes the retention effective.
- **Why the others are wrong:** A — `log.retention.check.interval.ms` (300000 ms) is how often the cleaner runs; it has run many times already and correctly found nothing deletable. C — `retention.ms` is a genuine topic-level configuration with no 168-hour floor; 168 hours is merely the broker default expressed as `log.retention.hours`. D — `cleanup.policy=compact` is a different mechanism entirely; time-based deletion needs `cleanup.policy=delete` (the default).
- 🧠 **Key point / trap:** *"I set retention to one hour and the data is still there"* is one of the most repeated administrator questions, and the answer is always the **active segment**.
- 📎 Source: [CCDAK Week 2 — `kafka-topic-configs.md`](../../../CCDAK/study-plan/week-02/resources/kafka-topic-configs.md) and [CCAAK master plan §6 — log & retention](../../CCAAK-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng).

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (23+/28) | Đạt ngưỡng cá nhân cho domain ARCH. | Review 100% câu sai và viết phân tích vào `CCAAK/questions/`. Sang [Tuần 5](../week-05/README.md) ngay. Trước khi sang, tự dựng lại **từ trí nhớ** bảng *MM2 vs Cluster Linking vs stretch cluster* — nếu còn phải tra thì chưa thuộc. |
| **70–79%** (20–22/28) | Gần đạt, còn lỗ hổng cục bộ. | Xác định nhóm sai nhiều nhất trong 6 nhóm (sizing · controller topology · rack & follower fetching · multi-DC & DR · MM2 & Cluster Linking · upgrade & reassignment), đọc lại đúng mục đó ở [Buổi A](README.md#-buổi-a--lý-thuyết-3h) và **làm lại lab tương ứng** (nhóm rack → Lab 4.2; nhóm MM2 → Lab 4.4; nhóm reassignment → Lab 4.5). Rồi làm lại bộ câu hỏi sau 2 ngày. Vẫn sang được Tuần 5. |
| **< 70%** (≤ 19/28) | Chưa nắm domain ARCH. | Học lại **toàn bộ Buổi A** và làm đủ Lab 4.1, 4.2, 4.4, 4.5. ARCH chỉ chiếm 12% nên **không** phải van an toàn lùi lịch thi, nhưng phải ghi vào sổ để quay lại ở [Tuần 8](../week-08/README.md) trước khi làm full mock. Đặc biệt kiểm tra xem bạn sai vì **thiếu kiến thức** hay vì **dính bẫy version** (ZooKeeper / `inter.broker.protocol.version` / `leader.imbalance.per.broker.percentage`) — hai nguyên nhân này cần hai cách chữa khác nhau. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / dính bẫy / hết giờ), và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may cũng tính là câu sai.
>
> 🧠 Riêng với ARCH, hãy đếm xem bạn sai bao nhiêu câu vì **không đọc kỹ qualifier** — *"Apache Kafka thuần"*, *"fewest components to operate"*, *"if one broker is lost"*, *"without data loss"*, *"cheapest first action"*. Domain này thiết kế đúng hay sai phần lớn nằm ở một cụm từ trong đề bài.
