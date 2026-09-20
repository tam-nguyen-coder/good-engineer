# 📝 Practice Questions — Week 4: Deployment Architecture (sizing · rack awareness · multi-DC · DR)

> **28 questions** · real CCAAK exam style — scenario first, "what should the administrator do next" — difficulty ≥ real exam. Covers the full Week 4 material + 2 review questions from Weeks 2–3.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first, timed: **42 minutes** (~90 s/question, same pace as the real exam).
> Tag: `[<DOMAIN> · <Topic> · <type>]`. Multi = multiple-response (the number to choose is stated). Domains: `ARCH` (Deployment Architecture), `CFG` (Cluster Configuration).
> Back to [week plan](README.md) · [labs](labs.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[ARCH · Capacity planning · Single]`

A team is provisioning a new topic. Measured on the existing cluster, a single partition sustains **60 MB/s** of produce traffic, and one consumer instance of the downstream application processes **25 MB/s**. The business requires the topic to sustain **450 MB/s** end to end. Ignoring growth headroom for the moment, what is the MINIMUM number of partitions the administrator should create?

- A. 8 partitions, because `450 / 60 = 7.5` rounded up
- B. 18 partitions, because the partition count must satisfy `max(t/p, t/c) = max(450/60, 450/25) = max(7.5, 18)`
- C. 25 partitions, one per MB/s of consumer throughput
- D. 3 partitions, because the replication factor of 3 already provides three parallel readers

### Question 2 — `[ARCH · Capacity planning · Single]`

A topic ingests **80 MB/s** of compressed data, `retention.ms` is set to **3 days**, and `replication.factor=3`. The team applies the usual **20% headroom** factor. Approximately how much raw disk must the cluster provide in total for this topic?

- A. ~21 TB
- B. ~62 TB
- C. ~75 TB
- D. ~249 TB

### Question 3 — `[ARCH · Partition count · Multi — Choose 2]`

A platform team proposes creating every new topic with 500 partitions "so we never have to increase them later". The cluster has 6 brokers. Which **two** consequences should the administrator raise as genuine costs of this policy? (Choose two.)

- A. Each partition directory holds an index and a log file per segment, so the open file-descriptor count per broker grows substantially; production clusters are documented running with more than 30,000 open file handles per broker
- B. Partition count cannot be reduced later, so an over-sized topic permanently carries its metadata and replication overhead
- C. `min.insync.replicas` is automatically raised in proportion to the partition count
- D. Consumers in the group are limited to one partition each, so 500 partitions force the group to run 500 consumer instances
- E. The replication factor is capped at `partitions / brokers`, so 500 partitions on 6 brokers would force RF=1

### Question 4 — `[ARCH · Capacity planning · Single]`

Capacity planning determined that a topic set needs **120 TB** of total storage including replication and headroom. Each broker provides **10 TB** of usable Kafka storage. The requirement states the cluster must still hold all data **if one broker is lost**. What is the minimum number of brokers?

- A. 12
- B. 13
- C. 14
- D. 36, because each of the three replicas needs its own dedicated set of 12 brokers

### Question 5 — `[ARCH · Broker sizing / JVM · Single]`

A broker runs on a 64 GB machine configured with `-Xms48g -Xmx48g`. Monitoring shows `IsrShrinksPerSec` and `IsrExpandsPerSec` oscillating several times per minute, GC logs show full collections lasting 4–9 seconds, and disk read throughput has increased sharply since last month even though the consumer set has not changed. What should the administrator change FIRST?

- A. Raise `replica.lag.time.max.ms` from 30000 to 120000 so followers are not evicted during GC pauses
- B. Reduce the broker heap to around 6 GB so most of the 64 GB is available to the OS page cache, then re-observe ISR churn and disk reads
- C. Increase `num.replica.fetchers` from 1 to 8 so followers catch up faster after each pause
- D. Enable `unclean.leader.election.enable` so leadership moves away from the pausing broker automatically

### Question 6 — `[ARCH · Controller topology · Single]`

A production cluster runs three nodes with `process.roles=broker,controller`. During a heavy compaction window, one node's long GC pause caused a controller failover **and** a partition leader change at the same time, doubling the impact of a single event. What change addresses the root cause?

- A. Add two more nodes with `process.roles=broker,controller` so the quorum becomes 5
- B. Move the controller quorum onto dedicated nodes running `process.roles=controller`, leaving the brokers with `process.roles=broker`
- C. Set `controller.quorum.election.timeout.ms` to a higher value so a GC pause does not trigger an election
- D. Set `process.roles=controller` on all three existing nodes and let clients connect to the controller listener

### Question 7 — `[ARCH · Controller quorum · Single]`

A cluster is designed with **5 KRaft controllers** spread across three availability zones as **2 / 2 / 1**. Which statement about this topology is correct?

- A. It tolerates the loss of any 2 controllers, and losing an entire AZ (at most 2 controllers) still leaves a majority of 3
- B. It tolerates the loss of any 4 controllers, because only one active controller is needed at a time
- C. It tolerates the loss of 2 controllers only if they are in the same AZ; losing 2 controllers in different AZs halts the cluster
- D. A 5-controller quorum requires 5 availability zones; a 2/2/1 layout is invalid and the cluster will refuse to form

### Question 8 — `[ARCH · Controller quorum · Single]`

A network partition isolates two of three KRaft controllers. Operators report that existing producers and consumers keep working on topics whose leaders did not change, but `kafka-topics.sh --create` hangs and a broker that was restarted cannot rejoin. Which explanation is correct?

- A. The brokers have lost their cached metadata and are serving stale data; producers should be stopped immediately to prevent corruption
- B. The controller quorum has lost its majority, so the control plane cannot commit metadata changes, while the data plane keeps serving partitions whose leadership is unchanged from the brokers' cached metadata
- C. Losing controllers has no effect on topic creation; the hang must be caused by `auto.create.topics.enable=false`
- D. Brokers automatically elect one of themselves as a replacement controller after `controller.quorum.election.timeout.ms`, so the cluster will self-heal within one second

### Question 9 — `[ARCH · KRaft quorum · Single]`

An administrator runs a feature check before planning a controller expansion:

```
$ bin/kafka-features.sh --bootstrap-controller localhost:9093 describe
Feature: eligible.leader.replicas.version  SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1
Feature: group.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1
Feature: kraft.version                     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 0
Feature: metadata.version                  SupportedMinVersion: 3.3-IV3  SupportedMaxVersion: 4.3-IV0  FinalizedVersionLevel: 4.3-IV0
Feature: transaction.version               SupportedMinVersion: 0        SupportedMaxVersion: 2        FinalizedVersionLevel: 2
```

What does this output tell the administrator about adding a fourth controller?

- A. `kraft.version` at level 0 means the cluster uses a **static** controller quorum defined by `controller.quorum.voters`, so a new voter cannot be added with `kafka-metadata-quorum.sh add-controller`; the voter list must be changed in configuration and the controllers restarted
- B. `kraft.version` at level 0 means dynamic quorums are active, so `kafka-metadata-quorum.sh add-controller` will work immediately
- C. `metadata.version 4.3-IV0` must first be downgraded to `3.3-IV3` before a controller can be added
- D. The new controller should be registered by creating its znode under `/controller` before starting the process

### Question 10 — `[ARCH · Rack awareness · Single]`

A cluster has `broker.rack` configured and a topic was created with `--replication-factor 3`:

```
$ bin/kafka-topics.sh --bootstrap-server kafka-1:9092 --describe --topic payments
Topic: payments  PartitionCount: 6  ReplicationFactor: 3
  Topic: payments  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3,4
  Topic: payments  Partition: 1  Leader: 3  Replicas: 3,2,4  Isr: 3,2,4
  Topic: payments  Partition: 2  Leader: 4  Replicas: 4,2,3  Isr: 4,2,3
...
$ bin/kafka-broker-api-versions.sh --bootstrap-server kafka-1:9092 | grep -E "^kafka-"
kafka-1:9092 (id: 2 rack: az-a) -> ...
kafka-2:9092 (id: 3 rack: az-a) -> ...
kafka-3:9092 (id: 4 rack: az-b) -> ...
```

The topic has `min.insync.replicas=2` and producers use `acks=all`. What happens if availability zone `az-a` is lost entirely?

- A. Nothing changes; rack awareness guarantees one replica per rack, so two replicas survive
- B. Every partition drops to a single in-sync replica, which is below `min.insync.replicas=2`, so `acks=all` producers start failing with `NotEnoughReplicasException`; the cluster only has 2 racks, so Kafka could only spread replicas over `min(2, 3) = 2` racks
- C. Partitions become offline because their leaders were all in `az-a`
- D. Kafka automatically re-creates the missing replicas on `az-b` within `replica.lag.time.max.ms`, so writes continue

### Question 11 — `[ARCH · Rack awareness · Multi — Choose 2]`

A cluster is being redesigned for rack awareness across 3 availability zones. Which **two** statements are correct? (Choose two.)

- A. With `broker.rack` set, a partition's replicas will span `min(#racks, replication.factor)` different racks
- B. Assigning different numbers of brokers per rack is harmless, because Kafka normalizes the load by placing an equal number of replicas on every broker regardless of rack size
- C. If the number of brokers per rack is uneven, racks with fewer brokers receive more replicas and therefore use more storage and more replication bandwidth, so an equal number of brokers per rack is recommended
- D. `broker.rack` can be changed at runtime with `kafka-configs.sh --alter --entity-type brokers`, so no restart is needed
- E. Increasing `replication.factor` from 3 to 4 on a 3-rack cluster guarantees the topic survives the loss of two racks

### Question 12 — `[ARCH · Follower fetching · Single]`

A consumer fleet runs in `az-c`. The cloud bill shows a steep rise in cross-zone data transfer, and the administrator confirms that most partition leaders currently live in `az-a`. Producers are unaffected. What is the correct configuration to cut the cross-zone read cost?

- A. Set `client.rack=az-c` on the consumers; brokers pick the closest replica automatically from that point on
- B. Set `broker.rack` on every broker, set `replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector` on the brokers, and set `client.rack=az-c` on the consumers
- C. Set `fetch.from.follower=true` on the consumers and `follower.fetching.enable=true` on the brokers
- D. Run `kafka-leader-election.sh --election-type preferred` so that all leaders move to `az-c`

### Question 13 — `[ARCH · Follower fetching · Single]`

After follower fetching is correctly enabled, a developer claims it will also reduce produce latency and increase total write throughput. Which statement is correct?

- A. Correct — with `RackAwareReplicaSelector` the producer also writes to the nearest replica, which then forwards to the leader
- B. Incorrect — producers always write to the partition **leader**; follower fetching only changes which replica serves **fetch** requests, and only in-sync replicas are eligible, serving data up to the high watermark
- C. Correct — follower fetching doubles write throughput because two replicas accept writes concurrently
- D. Incorrect — follower fetching also disables `acks=all`, so writes become less durable rather than faster

### Question 14 — `[ARCH · Multi-DC · Single]`

A bank has exactly **two** datacenters, 20 km apart, connected by a stable 2 ms dark-fibre link. The requirement is **RPO = 0** — not a single acknowledged message may be lost if one datacenter is destroyed. What deployment should the administrator propose?

- A. One stretched cluster with brokers and controllers evenly split between the two datacenters
- B. Two separate clusters with MirrorMaker 2 running `A->B` and `B->A`
- C. A stretched cluster across the two datacenters **plus a third, lightweight site running only KRaft controllers** so the quorum stays odd and a majority survives the loss of either full datacenter ("2.5 datacenter" topology)
- D. Two separate clusters with Cluster Linking and `consumer.offset.sync.enable=true`

### Question 15 — `[ARCH · DR selection · Single]`

A company runs **Confluent Platform 7.9** and must build a DR site. The strict requirement is that after failover, every consumer group resumes at exactly the offsets it had on the primary, with the **fewest additional components to operate**. Which option meets this best?

- A. MirrorMaker 2 with `IdentityReplicationPolicy`, because keeping the topic names identical also keeps the offsets identical
- B. Cluster Linking, because the destination brokers pull directly from the source with byte-for-byte replication and globally consistent offsets, requiring no Connect cluster
- C. MirrorMaker 2 with `sync.group.offsets.enabled=true`, which guarantees exact offset equality on the destination
- D. A stretched cluster, because it is the only option that preserves offsets

### Question 16 — `[ARCH · DR selection · Single]`

A company runs **Apache Kafka 4.3** (no Confluent Platform) in two regions. Both regions must accept writes at the same time, and each region must be able to read the other region's data. Which design is correct?

- A. MirrorMaker 2 with flows `A->B` and `B->A` using the default `DefaultReplicationPolicy`, so remote topics are named `A.<topic>` and `B.<topic>` and replication loops are prevented
- B. MirrorMaker 2 with flows `A->B` and `B->A` using `IdentityReplicationPolicy`, so applications see the same topic names in both regions
- C. Cluster Linking in both directions with `auto.create.mirror.topics.enable=true`
- D. A single stretched cluster with `broker.rack` set to the region name

### Question 17 — `[ARCH · MirrorMaker 2 · Single]`

An administrator starts MirrorMaker 2 and sees this in the log, but after 20 minutes the destination cluster still contains no replicated topics:

```
[2026-09-20 10:14:02,881] INFO Kafka MirrorMaker initializing (org.apache.kafka.connect.mirror.MirrorMaker:...)
[2026-09-20 10:14:03,145] INFO Configuring clusters [A, B] (org.apache.kafka.connect.mirror.MirrorMaker:...)
[2026-09-20 10:14:07,902] INFO Kafka MirrorMaker started (org.apache.kafka.connect.mirror.MirrorMaker:...)
```

The properties file contains:

```properties
clusters = A, B
A.bootstrap.servers = a-broker-1:9092
B.bootstrap.servers = b-broker-1:9092
A->B.topics = orders.*
tasks.max = 3
```

What is missing?

- A. `A->B.enabled = true` — replication flows are disabled by default, so no herder or connector is created for the flow
- B. `topics = .*` must be set at the top level; per-flow `topics` settings are ignored
- C. `replication.policy.class` must always be set explicitly; MirrorMaker refuses to replicate without it
- D. MirrorMaker 2 needs `--whitelist orders.*` on the command line, as with `kafka-mirror-maker.sh`

### Question 18 — `[ARCH · MirrorMaker 2 · Multi — Choose 2]`

MirrorMaker 2 is replicating `A->B` correctly: records appear in `A.orders` on cluster B. However, the operations team reports that no consumer group offsets are visible on cluster B. Their test used `kafka-console-consumer.sh --topic orders --from-beginning` on cluster A without a `--group` flag, and on cluster B an application with the same group id is already running and consuming. Which **two** statements explain this? (Choose two.)

- A. The console consumer without `--group` generates a group named `console-consumer-<n>`, which matches the default `groups.exclude = console-consumer-.*, connect-.*, __.*` and is therefore not replicated
- B. `MirrorCheckpointConnector` writes translated offsets into the destination's `__consumer_offsets` only while the group is **not active** on the destination, so a group already consuming on B will not be overwritten
- C. Consumer offsets are only replicated when `replication.policy.class=IdentityReplicationPolicy` is used
- D. Offset translation requires `exactly.once.source.support = enabled`, which is disabled by default
- E. `MirrorSourceConnector` replicates offsets; `MirrorCheckpointConnector` only produces heartbeats

### Question 19 — `[ARCH · MirrorMaker 2 · Single]`

A team is migrating applications from an old Apache Kafka cluster to a new one. The applications must keep their existing topic names and configuration files unchanged after the cutover. Which statement is correct about using MirrorMaker 2 for this?

- A. Use `IdentityReplicationPolicy` so topics keep their original names on the destination; note that consumer offsets are still different and must be translated via checkpoints or `sync.group.offsets.enabled`
- B. Use `DefaultReplicationPolicy` and configure `replication.policy.separator = ""` so that `{source}{topic}` equals the original name
- C. Use `IdentityReplicationPolicy`, which also makes the destination offsets byte-for-byte identical to the source
- D. Topic names cannot be preserved with MirrorMaker 2; the only option is to recreate topics manually and replay data with a custom consumer/producer pair

### Question 20 — `[ARCH · Cluster Linking · Multi — Choose 2]`

Which **two** statements about Cluster Linking are correct? (Choose two.)

- A. A mirror topic on the destination cluster is read-only; it must be promoted or failed over before producers can write to it
- B. Cluster Linking is part of Apache Kafka from version 4.0 and is started with `bin/kafka-cluster-links.sh` on any Kafka broker
- C. Cluster Linking replicates byte-for-byte and preserves offsets, so consumers failing over to the destination do not need offset translation
- D. Bidirectional replication is configured on a single link by setting `link.mode=BIDIRECTIONAL`
- E. Cluster Linking mirrors transactional messages transparently, which is why it is preferred over MirrorMaker 2 for exactly-once pipelines

### Question 21 — `[ARCH · Rolling upgrade · Multi — Choose 2]`

A 4.2.0 KRaft cluster is being upgraded to 4.3.0. Every broker and controller has been restarted onto the new binaries, one node at a time, waiting for `UnderReplicatedPartitions` to return to 0 between nodes. Which **two** statements are correct about what happens next? (Choose two.)

- A. The upgrade is finalized by running `bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3`
- B. The upgrade is finalized by setting `inter.broker.protocol.version=4.3` in every broker's `server.properties` and performing a second rolling restart
- C. After finalizing, a cluster metadata downgrade back to 4.2 is **not** supported, because 4.3.0 introduces metadata changes
- D. After finalizing, the cluster can be downgraded to 4.2 at any time with `kafka-features.sh downgrade --release-version 4.2`, since downgrades are always supported within the same major version
- E. Finalizing is unnecessary; `metadata.version` is raised automatically once the last node reports the new software version

### Question 22 — `[ARCH · Cluster expansion · Single]`

Two brokers were added to a 4-broker cluster three days ago. Disk usage on the original brokers is still at 88% while the new brokers are nearly empty:

```
$ bin/kafka-log-dirs.sh --bootstrap-server kafka-1:9092 --describe --topic-list events | jq -r \
    '.brokers[] | "broker \(.broker): \([.logDirs[].partitions[].size] | add // 0) bytes"'
broker 1: 1932735283 bytes
broker 2: 2040109465 bytes
broker 3: 1825361100 bytes
broker 4: 1932735283 bytes
broker 5: 0 bytes
broker 6: 0 bytes
```

What should the administrator do?

- A. Restart brokers 1–4 so the controller redistributes partitions to the new brokers
- B. Run `kafka-reassign-partitions.sh --generate` with `--broker-list "1,2,3,4,5,6"`, then `--execute` the proposed plan with a `--throttle`, then `--verify` — Kafka does not move existing partitions to new brokers automatically
- C. Set `auto.leader.rebalance.enable=true`, which will migrate partitions to the empty brokers within `leader.imbalance.check.interval.seconds`
- D. Delete and recreate the topic so that the controller places replicas across all six brokers

### Question 23 — `[ARCH · Reassignment · Multi — Choose 2]`

An administrator executes a large reassignment:

```
$ bin/kafka-reassign-partitions.sh --bootstrap-server kafka-1:9092 \
    --reassignment-json-file plan.json --execute --throttle 50000000
```

Which **two** statements are correct? (Choose two.)

- A. The `Current partition replica assignment` block printed by `--execute` should be saved, because it is the input needed to roll the change back
- B. The throttle is removed automatically when the last partition finishes copying, so no further action is needed
- C. The throttle is only removed when `kafka-reassign-partitions.sh ... --verify` is run after completion; failing to do so leaves `leader.replication.throttled.rate` and `follower.replication.throttled.rate` in place and permanently slows normal replication
- D. The throttle value can only be set before the reassignment starts and cannot be changed while it is in progress
- E. `--throttle` applies to client produce and fetch traffic as well, so it doubles as a quota for producers during the migration

### Question 24 — `[ARCH · Leader balance · Single]`

After a planned rolling restart of a 3-broker KRaft cluster, `kafka-topics.sh --describe` shows that broker 2 is the leader for 80% of the partitions and its CPU sits at 85% while the other two brokers idle. The replica lists themselves are unchanged. What is the correct, cheapest first action?

- A. Run `kafka-reassign-partitions.sh` to redistribute replicas evenly across the three brokers
- B. Run `kafka-leader-election.sh --bootstrap-server ... --election-type preferred --all-topic-partitions`, which moves leadership back to the first replica in each list without copying any data
- C. Lower `leader.imbalance.per.broker.percentage` so the controller rebalances leadership sooner
- D. Restart broker 2 with `--zookeeper` pointed at the ensemble so the controller recomputes the leader map

### Question 25 — `[ARCH · Decommissioning · Ordering]`

A broker with `node.id=7` must be permanently removed from a Kafka 4.3 KRaft cluster with no data loss and no period below `min.insync.replicas`. Put the following steps in the correct order.

1. Run `bin/kafka-cluster.sh unregister --bootstrap-server <bs> --id 7`
2. Stop the Kafka process on broker 7
3. Run `kafka-reassign-partitions.sh --execute` with a plan that places every replica currently on broker 7 onto other brokers, then `--verify` until it completes
4. Set `cordoned.log.dirs="*"` on broker 7 with `kafka-configs.sh` so the controller stops placing new partitions on it

- A. 4 → 3 → 2 → 1
- B. 2 → 3 → 4 → 1
- C. 3 → 4 → 1 → 2
- D. 1 → 4 → 3 → 2

### Question 26 — `[ARCH · Cross-cluster tooling · Matching]`

Match each requirement (1–5) with the single most appropriate mechanism (A–E). Each mechanism is used exactly once.

| # | Requirement |
|---|---|
| 1 | Aggregate events from five regional Apache Kafka clusters into one central analytics cluster, with the origin visible in the topic name |
| 2 | Guarantee that no acknowledged message is ever lost when one of three nearby datacenters is destroyed |
| 3 | Move a Confluent Platform workload to Confluent Cloud with identical topic names and identical committed offsets |
| 4 | Let consumers in `az-c` read without paying for cross-zone traffic, inside a single cluster |
| 5 | Move existing partitions onto two brokers that were just added to the cluster |

| Letter | Mechanism |
|---|---|
| A | Stretched cluster across the three datacenters |
| B | `kafka-reassign-partitions.sh --generate/--execute/--verify` |
| C | Cluster Linking |
| D | MirrorMaker 2 with `DefaultReplicationPolicy` |
| E | `broker.rack` + `replica.selector.class=RackAwareReplicaSelector` + `client.rack` |

### Question 27 — `[CFG · Week 3 review · Single]`

A topic in a 5-broker cluster is configured with `replication.factor=3` and `min.insync.replicas=3`, and its producers use `acks=all`. During a routine single-broker restart, producers immediately fail with `NotEnoughReplicasException`. The requirement is "no data loss, and writes must continue while one broker is being restarted". What should the administrator change?

- A. Set `min.insync.replicas=2`, so that with RF=3 the topic tolerates exactly one missing replica while still guaranteeing two copies of every acknowledged write
- B. Set `acks=1` on the producers so writes no longer depend on the in-sync replica count
- C. Set `unclean.leader.election.enable=true` so a lagging replica can take over during the restart
- D. Raise `replication.factor` to 5 and keep `min.insync.replicas=3`

### Question 28 — `[CFG · Week 2 review · Single]`

An administrator sets `retention.ms=3600000` (1 hour) on a low-traffic topic that receives a few small records per hour. Twelve hours later, `kafka-log-dirs.sh` still reports the same data on disk and consumers can still read records from this morning. What is the explanation?

- A. `retention.ms` only applies after `log.retention.check.interval.ms` has elapsed 12 times; the data will disappear on the next check
- B. Retention is enforced per **closed** log segment; the active segment is never deleted, and with low traffic the segment has neither reached `segment.bytes` (1 GiB default) nor `segment.ms`, so nothing has rolled yet. Lower `segment.ms` (or `segment.bytes`) on the topic to make retention effective
- C. `retention.ms` is a topic-level alias of `log.retention.hours` and cannot be lower than 168 hours
- D. The topic must have `cleanup.policy=compact` for `retention.ms` to take effect

---

> ✅ Done? Check your answers in [answers.md](answers.md), log every wrong answer with the **reason** you got it wrong (missing knowledge / skipped a qualifier / fell for a trap / ran out of time), and group them into the six Week 4 buckets: sizing · controller topology · rack & follower fetching · multi-DC & DR selection · MirrorMaker 2 & Cluster Linking · upgrade & reassignment.
