# 🎯 CCAAK Mock Exam 03 — 60 questions · 90 minutes

> **Exam-realistic full-length mock.** Distribution follows the official CCAAK domain weights.
> ⏱️ Set a timer for **90 minutes** (~90 seconds per question). No notes, no documentation, no pausing.
> 🔒 Answers, explanations and per-domain scoring: [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (4 options) · `Multi` (choose the stated number) · `Matching` · `Ordering`.
> Tag: `[Domain · Topic · Format]`. Domains: `CFG` `FUND` `SEC` `TROUBLE` `ARCH` `CONNECT` `OBS`.
> Anchored to **Apache Kafka 4.3** — ZooKeeper was removed in 4.0; any option that relies on it is wrong.
> 🏛️ **Theme of this mock: architecture and trade-offs.** In most questions **all four options work**. Only the qualifier in the stem — *without data loss · with minimal downtime · with the fewest changes · without restarting brokers · survive the loss of one rack · while keeping producers writing · the most cost-effective · the FIRST action* — decides which one is right. Read the qualifier before you read the options.
> Back to [mock index](../README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[CFG · Durability vs availability · Single]`

A 6-broker cluster is split across two availability zones, three brokers in each. The payments topic looks like this:

```
$ kafka-topics.sh --bootstrap-server broker-1:9092 --describe --topic payments

Topic: payments  PartitionCount: 12  ReplicationFactor: 3  Configs: min.insync.replicas=2
  Partition: 0  Leader: 1  Replicas: 1,2,3  Isr: 1,2,3
  Partition: 1  Leader: 2  Replicas: 2,3,1  Isr: 2,3,1
  ...
```

Brokers 1, 2 and 3 are all in `az-a`; brokers 4, 5 and 6 are all in `az-b`. No broker declares `broker.rack`. Producers use `acks=all`. The requirement is to **survive the loss of one entire availability zone without losing acknowledged data and while keeping producers writing throughout**, using the **fewest configuration changes**. What do you do?

- A. Raise `min.insync.replicas` to 3 on `payments` so every acknowledged write is on three replicas before the zone is lost.
- B. Set `broker.rack` on every broker and restart them one at a time, then reassign `payments` so each partition's three replicas land in three different zones; `min.insync.replicas=2` then still holds after a zone failure.
- C. Raise the replication factor of `payments` to 6 with a reassignment plan so every broker holds a replica of every partition.
- D. Set `unclean.leader.election.enable=true` at the cluster level so a surviving replica can take leadership immediately when a zone disappears.

### Question 2 — `[TROUBLE · min.insync.replicas vs RF · Single]`

A planned kernel patch takes broker 4 out of a 4-broker cluster. Within seconds, producers to `audit-trail` start failing:

```
org.apache.kafka.common.errors.NotEnoughReplicasException: The size of the current ISR Set(3) is insufficient
to satisfy the min.isr requirement of 2 for partition audit-trail-9
```

`audit-trail` was created with `replication.factor=2` and `min.insync.replicas=2`. Every other topic is unaffected. Ops needs **the FIRST action that restores writes without accepting the loss of acknowledged data**. What is it?

- A. Set `min.insync.replicas=1` on `audit-trail` with `kafka-configs.sh` — it is a dynamic topic override and can be raised again later.
- B. Abort the patch and bring broker 4 back so the second replica rejoins the ISR, then raise `audit-trail` to `replication.factor=3` with a reassignment plan before the next maintenance window.
- C. Set `unclean.leader.election.enable=true` on `audit-trail` so the out-of-sync replica can serve writes.
- D. Increase the partition count of `audit-trail` so the new partitions are placed on the three healthy brokers.

### Question 3 — `[ARCH · DR mechanism selection · Single]`

A bank runs Confluent Platform 7.9 in two data centres 900 km apart; the measured round-trip latency between them is **41 ms** and occasionally spikes to 300 ms. They need a standby cluster so that, after a regional failure, **consumer applications restart in the second site and resume from the offsets they had already committed, with no offset-translation code and no extra service to operate**. Which architecture meets the requirement?

- A. A stretch cluster across both sites with `broker.rack` set per site and `min.insync.replicas=2`, giving RPO = 0.
- B. MirrorMaker 2 with `MirrorSourceConnector` and `MirrorCheckpointConnector`, plus `sync.group.offsets.enabled=true` so the checkpoints are written into the destination's `__consumer_offsets`.
- C. A Cluster Link from the primary to the standby with `consumer.offset.sync.enable=true`; mirror topics keep the source topic names and byte-for-byte identical offsets.
- D. A nightly `kafka-dump-log.sh` export of each partition shipped to object storage and replayed by a producer on failover.

### Question 4 — `[SEC · SASL mechanism choice · Single]`

A platform team must authenticate roughly 300 internal services against a Kafka 4.3 cluster. The constraints are: **credentials must be created and revoked while the cluster is running, with no broker restart**; there is **no Kerberos KDC** in the environment; and the security team will not accept passwords traversing the network in a form an on-path observer could read. Which mechanism satisfies all three constraints with the least operational machinery?

- A. `SASL/PLAIN` over `SASL_SSL`, with the service accounts declared in the broker JAAS file.
- B. `SASL/GSSAPI` over `SASL_SSL`, with one service principal per application in the enterprise directory.
- C. `SASL/SCRAM-SHA-512` over `SASL_SSL`, with credentials managed through `kafka-configs.sh --entity-type users`.
- D. `SASL/OAUTHBEARER` with the unsecured JWT login module, over `SASL_PLAINTEXT`.

### Question 5 — `[CONNECT · Deployment mode · Single]`

A retailer wants to ship application log files from **140 edge store servers** into Kafka. Each server produces its own files; the files never move between servers; the stores have unreliable WAN links and the central team wants **no additional cluster-wide state to operate** for this pipeline. A second pipeline — a JDBC source reading the central order database — must survive the loss of any single worker. Which deployment matches each pipeline?

- A. Standalone workers on the 140 edge servers, and a distributed Connect cluster for the JDBC source.
- B. One distributed Connect cluster of 140 workers sharing `group.id=edge-logs`, plus the JDBC connector on the same cluster.
- C. Standalone workers everywhere, with the JDBC source duplicated on three standalone workers for redundancy.
- D. A distributed Connect cluster at the edge and a standalone worker for the JDBC source, because JDBC sources always produce exactly one task.

### Question 6 — `[FUND · One-way operations · Single]`

A topic `clickstream` has 24 partitions, is keyed by `userId`, and feeds a consumer group whose members maintain per-user state. Lag has been growing for a week. The team proposes raising the partition count to 48. Which statement most accurately describes the consequence they must weigh before doing it?

- A. Adding partitions is reversible: `kafka-topics.sh --alter --partitions 24` restores the original layout, and existing records are redistributed by the new hash.
- B. Adding partitions changes `hash(userId) % partitions`, so records for a given user after the change can land on a different partition from the ones already stored; ordering per key is broken across the boundary and the partition count cannot be lowered again.
- C. Adding partitions triggers a rebalance that re-keys the existing data, so ordering per key is preserved and only the in-flight batches are affected.
- D. Adding partitions is safe for ordering because Kafka stores the original partition in a record header and consumers replay in that order.

### Question 7 — `[OBS · Trade-off axis to configuration · Matching]`

Match each trade-off an administrator is being asked to make to the configuration that most directly controls it.

| # | Trade-off being made |
|---|---|
| 1 | Accept a slower recovery after a broker restart in exchange for less CPU and network pressure on healthy brokers |
| 2 | Accept longer retention of acknowledged data in exchange for producers blocking when replicas are lost |
| 3 | Accept higher end-to-end latency in exchange for fewer, larger requests on the wire |
| 4 | Accept a larger memory footprint per request in exchange for higher throughput on a high-latency link |

| Letter | Configuration |
|---|---|
| W | `linger.ms` together with `batch.size` |
| X | `socket.send.buffer.bytes` / `socket.receive.buffer.bytes` |
| Y | `num.replica.fetchers` |
| Z | `min.insync.replicas` together with `acks=all` |

- A. 1-Y · 2-Z · 3-W · 4-X
- B. 1-Z · 2-Y · 3-X · 4-W
- C. 1-Y · 2-W · 3-Z · 4-X
- D. 1-X · 2-Z · 3-W · 4-Y

### Question 8 — `[CFG · Cost vs retention · Single]`

A compliance rule forces the `transactions` topic to keep **13 months** of history. Today it retains 7 days and already consumes 62 % of the broker disks. Reads older than 48 hours happen a handful of times per quarter, during audits. The cluster runs Apache Kafka 4.3; `transactions` uses `cleanup.policy=delete` and a single `log.dirs` entry per broker. Which plan meets the requirement **most cost-effectively without adding a new service for the team to operate**?

- A. Attach 40× more disk to every broker and set `retention.ms` to 13 months.
- B. Set `remote.log.storage.system.enable=true` on the brokers, restart them one at a time, then set `remote.storage.enable=true`, `retention.ms=34128000000` and `local.retention.ms=172800000` on `transactions`.
- C. Set `cleanup.policy=compact` on `transactions` so the newest record per key is kept forever without growing the disk.
- D. Run a MirrorMaker 2 flow into a second, cheap "archive" cluster with 13-month retention, and point auditors at that cluster.

### Question 9 — `[TROUBLE · Disk pressure · Multi — Choose 2]`

One broker in a 5-broker cluster is at 94 % disk while the others sit near 40 %. `kafka-log-dirs.sh` shows the imbalance is caused by four very large partitions of one topic that all landed in the same data directory:

```
$ kafka-log-dirs.sh --bootstrap-server broker-3:9092 --describe --broker-list 3 | jq '.brokers[].logDirs[].partitions[] | select(.size > 200000000000)'
{"partition":"events-11","size":412000000000,"offsetLag":0,"isFuture":false}
{"partition":"events-17","size":401000000000,"offsetLag":0,"isFuture":false}
{"partition":"events-23","size":398000000000,"offsetLag":0,"isFuture":false}
{"partition":"events-29","size":404000000000,"offsetLag":0,"isFuture":false}
```

Which **two** actions relieve the pressure without deleting data that is still inside its retention window? (Choose two.)

- A. Set `log.retention.bytes` to a small value cluster-wide so old segments are deleted immediately.
- B. Move two of the four partitions to other brokers with `kafka-reassign-partitions.sh --execute --throttle`, then release the throttle with `--verify`.
- C. Raise `log.segment.bytes` from 1 GiB to 8 GiB on `events` so fewer segment files are open.
- D. Move two of the four partitions to a second data directory on the same broker with a reassignment plan that names `logDirs`.
- E. Set `cleanup.policy=compact,delete` on `events` so compaction reclaims the space.

### Question 10 — `[SEC · TLS certificate rotation · Ordering]`

The broker certificates of a live cluster expire in six days. They were issued by an old internal CA; the new certificates come from a new CA. Clients and brokers both use mutual TLS on the inter-broker listener. Put the steps in the order that rotates every certificate **without any downtime and without a rolling restart**.

| # | Step |
|---|---|
| 1 | Update `listener.name.internal.ssl.keystore.location` (and its password properties) per broker with `kafka-configs.sh --entity-type brokers --entity-name <id>`, one broker at a time |
| 2 | Distribute a truststore containing **both** the old and the new CA to every broker and update `listener.name.internal.ssl.truststore.location` dynamically on each of them |
| 3 | Remove the old CA from the truststores and apply the trimmed truststore dynamically |
| 4 | Confirm that clients have been issued certificates from the new CA and that their truststores also contain both CAs |

- A. 2 → 4 → 1 → 3
- B. 1 → 2 → 4 → 3
- C. 4 → 1 → 2 → 3
- D. 2 → 1 → 3 → 4

### Question 11 — `[CFG · Throughput vs latency · Single]`

Broker 7 was rebuilt after a disk failure and is re-replicating 1,900 partitions. At the current rate it will rejoin every ISR in about **nine hours**, and `UnderReplicatedPartitions` across the cluster stays in the hundreds the whole time. The brokers run the 4.3 defaults for replication threads. Produce latency on the healthy brokers is already at the edge of the SLA. Which change shortens the catch-up **without restarting any broker** and **without pushing extra fetch load onto the healthy brokers**?

- A. Set `replica.lag.time.max.ms` to 5000 cluster-wide so lagging replicas are evicted from the ISR faster and the metric clears.
- B. Raise `num.replica.fetchers` from 1 to 8 as a cluster-wide dynamic default so every broker fetches in parallel.
- C. Raise `replica.fetch.max.bytes` from 1,048,576 to 16,777,216 in `server.properties` on all brokers and roll them.
- D. Raise `num.replica.fetchers` from 1 to 8 as a **per-broker** dynamic config on broker 7 only, then remove the override once it has caught up.

### Question 12 — `[FUND · Durability over-correction · Multi — Choose 2]`

After an incident, an architect proposes standardising every production topic on `replication.factor=3` **and** `min.insync.replicas=3`, arguing that "three copies means three acknowledgements". Which **two** consequences must the team accept? (Choose two.)

- A. `unclean.leader.election.enable` is implicitly enabled to compensate for the stricter setting.
- B. Consumers also lose read availability, because a fetch below the high watermark is refused while `|ISR| < min.insync.replicas`.
- C. Producers using `acks=all` are rejected the moment a single replica leaves the ISR, so the topic has no write fault tolerance at all.
- D. The ISR can no longer shrink below three replicas, so `UnderReplicatedPartitions` stays at 0 permanently.
- E. A rolling restart produces `NotEnoughReplicasException` on the topic's partitions as each broker is bounced, because one replica is always absent during the roll.

### Question 13 — `[CONNECT · tasks.max and partitions · Single]`

A sink connector reads a 6-partition topic. To double throughput the team raised `tasks.max` from 6 to 12 and restarted the connector. The status endpoint reports:

```
$ curl -s localhost:8083/connectors/s3-orders/status | jq '.tasks | length, (.tasks[] | .state) ' | sort | uniq -c
  12 "RUNNING"
```

Throughput did not change. The consumer group `connect-s3-orders` shows six members with one partition each and six members with none. Which reading is correct, and what is the appropriate follow-up?

- A. Connect creates `min(tasks.max, partitions)` tasks, so the six extra tasks in the status output are a reporting artefact; restart the connector with `?includeTasks=true` to clear them.
- B. The six idle tasks are waiting for a cooperative rebalance; lowering `scheduled.rebalance.max.delay.ms` from 300000 to 0 will hand them partitions.
- C. `tasks.max` is a **ceiling**, not an instruction, and most sink connectors return the full number requested — so twelve consumers joined a group that can assign at most six partitions. Set `tasks.max` back to 6, and only raise the partition count if more parallelism is genuinely required, accepting that the count cannot be lowered again.
- D. Sink task parallelism is governed by `consumer.override.max.poll.records`; raise it so each of the twelve tasks processes more records per poll.

### Question 14 — `[ARCH · Cluster expansion · Ordering]`

A 3-broker cluster is being expanded to 5 brokers. Put the steps in the order a careful administrator performs them.

| # | Step |
|---|---|
| 1 | Apply the plan with `kafka-reassign-partitions.sh --execute --reassignment-json-file plan.json --throttle 50000000` |
| 2 | Start the two new brokers with new node ids and the same `cluster.id`, and confirm the cluster now lists five brokers |
| 3 | Run `kafka-reassign-partitions.sh --verify --reassignment-json-file plan.json` until it reports completion, which also removes the throttle configurations |
| 4 | Run `kafka-reassign-partitions.sh --generate --topics-to-move-json-file topics.json --broker-list "1,2,3,4,5"` and keep the printed *current* assignment as a rollback plan |

- A. 4 → 2 → 1 → 3
- B. 2 → 1 → 4 → 3
- C. 2 → 4 → 3 → 1
- D. 2 → 4 → 1 → 3

### Question 15 — `[CFG · Reversibility of operational decisions · Matching]`

Match each operational decision to an accurate statement about undoing it.

| # | Decision |
|---|---|
| 1 | Raising a topic from 12 to 24 partitions |
| 2 | Finalizing the cluster with `kafka-features.sh upgrade --release-version 4.3` |
| 3 | Setting `cordoned.log.dirs="*"` on a broker that is being drained |
| 4 | Setting `unclean.leader.election.enable=true` on a topic whose ISR is empty |

| Letter | Statement |
|---|---|
| W | Fully reversible with `--delete-config`; nothing is destroyed while it is in force |
| X | Not reversible in this release — that metadata version carries metadata changes, so there is no downgrade path |
| Y | The switch can be turned off again, but records that were lost when an out-of-sync replica became leader never come back |
| Z | Not reversible — the count can only increase, and the key-to-partition mapping changes from that moment on |

- A. 1-X · 2-Z · 3-W · 4-Y
- B. 1-Z · 2-X · 3-Y · 4-W
- C. 1-Z · 2-X · 3-W · 4-Y
- D. 1-W · 2-X · 3-Z · 4-Y

### Question 16 — `[TROUBLE · Offline partition recovery · Single]`

A Kafka 4.3 cluster created with default features loses two brokers in quick succession. One partition is offline:

```
$ kafka-topics.sh --bootstrap-server broker-1:9092 --describe --topic ledger

Topic: ledger  Partition: 3  Leader: none  Replicas: 6,7,8  Isr:   Elr: 8  LastKnownElr: 6
```

Broker **8** is online and unfenced. Brokers 6 and 7 are still down. `unclean.leader.election.enable` is `false`. The business wants the partition writable again **without losing acknowledged records**. What is the correct action?

- A. Set `unclean.leader.election.enable=true` on `ledger`; broker 8 is the only survivor, so the election is effectively clean anyway.
- B. Run `kafka-leader-election.sh --election-type PREFERRED --topic ledger --partition 3`; the preferred replica is broker 6 and the election will queue until it returns.
- C. Lower the cluster-level `min.insync.replicas` from 2 to 1 so the controller can accept broker 8 back into the ISR and elect it.
- D. Nothing destructive is needed: broker 8 is in the **ELR** set, so the controller elects it as leader without unclean election, because the strict-min-ISR rule guarantees it holds every acknowledged record.

### Question 17 — `[OBS · Reading the latency breakdown · Single]`

Produce p99 on a 6-broker cluster has climbed to 380 ms. The broker JMX readings are:

```
RequestHandlerAvgIdlePercent          = 0.62
NetworkProcessorAvgIdlePercent        = 0.08
TotalTimeMs{request=Produce} p99      = 381 ms
  RequestQueueTimeMs p99              =   4 ms
  LocalTimeMs p99                     =   6 ms
  RemoteTimeMs p99                    =   9 ms
  ResponseQueueTimeMs p99             = 344 ms
  ResponseSendTimeMs p99              =  18 ms
```

Which single change addresses the bottleneck these numbers point to?

- A. Raise `num.io.threads` from 8 to 16, because `TotalTimeMs` is dominated by broker-side processing.
- B. Raise `num.network.threads` from 3 to 8, because responses are queuing for a network thread that is busy 92 % of the time.
- C. Lower `min.insync.replicas` to 1, because `RemoteTimeMs` shows producers waiting on follower acknowledgements.
- D. Raise `queued.max.requests` from 500 to 5000 so fewer requests are rejected at the socket layer.

### Question 18 — `[SEC · ACL strategy at scale · Single]`

A platform team is defining the topic naming convention for a new multi-tenant cluster: roughly 60 teams, several hundred topics, growing weekly. Each team must read and write only its own topics. The team wants **the smallest number of ACLs to maintain over time** and no per-topic administrative work when a team adds a topic. Which convention supports that?

- A. `<team>.<domain>.<dataset>` — the team identifier is the leading segment, so one `PREFIXED` ACL per team on `<team>.` covers every topic that team will ever create.
- B. `<env>.<team>.<dataset>` — putting the environment first keeps production and staging clearly separated, and `PREFIXED` ACLs are written against `<env>.`.
- C. `<dataset>-<team>-<env>` — the dataset leads so related topics sort together, and access is granted with `LITERAL` ACLs created by automation on each topic creation.
- D. Any convention will do, because `allow.everyone.if.no.acl.found=true` lets new topics be used immediately and ACLs are only added where access must be restricted.

### Question 19 — `[FUND · Controller quorum sizing · Single]`

A 9-broker Kafka 4.3 cluster is spread evenly over three availability zones and uses **dedicated** controller nodes. The requirement is that the **control plane stays available through the loss of one entire availability zone**, at the lowest operating cost. Which topology is correct?

- A. Five controllers — two in `az-a`, two in `az-b`, one in `az-c` — because a five-node quorum tolerates two failures.
- B. Three controllers, all in `az-a`, on the same rack as the active controller for the lowest election latency.
- C. Three controllers, one per availability zone, plus a three-node ZooKeeper ensemble in the third zone as the tie-breaker.
- D. Three controllers, one per availability zone: losing one zone leaves two of three voters, which is still a majority, and three controllers cost less to run than five.

### Question 20 — `[CFG · Making a running cluster rack-aware · Ordering]`

An existing 6-broker cluster has no `broker.rack` set. Put the steps of converting it to a rack-aware layout into the correct order.

| # | Step |
|---|---|
| 1 | Generate a reassignment for the existing topics and apply it with `--execute --throttle`, so the already-created partitions are spread across the racks |
| 2 | Add `broker.rack=<zone>` to `server.properties` on every broker |
| 3 | Restart the brokers one at a time, waiting for `UnderReplicatedPartitions` to return to 0 between restarts |
| 4 | Run `--verify` to confirm completion and remove the throttle configurations |

- A. 1 → 2 → 3 → 4
- B. 2 → 1 → 3 → 4
- C. 2 → 3 → 1 → 4
- D. 3 → 2 → 1 → 4

### Question 21 — `[CONNECT · Multi-tenant topology · Single]`

Three tenants share one distributed Connect cluster (`group.id=connect-shared`, workers run as `User:connect-worker`). Tenant B now needs a newer JDBC plugin, and each tenant insists that its own Kafka credentials must not be usable by the other two. Each tenant can `POST` connectors to the REST API. Which plan actually delivers the credential isolation they are asking for?

- A. Give each tenant its own Connect cluster — its own `group.id`, its own three internal topics and its own worker principal. On a shared cluster any principal that can create a connector can set `producer.override.sasl.jaas.config` and act as another tenant, so the cluster boundary is the only real isolation boundary.
- B. Keep one cluster and set `connector.client.config.override.policy=None`, then scope each tenant with `topics.regex` in its connector configurations.
- C. Keep one cluster and have each tenant set its own `group.id` inside its connector configuration so the tenants land in different rebalance groups.
- D. Keep one cluster and write `PREFIXED` ACLs per tenant on `connect-configs`, `connect-offsets` and `connect-status` so each tenant sees only its own records.

### Question 22 — `[TROUBLE · One-way upgrade · Single]`

A cluster was upgraded from 4.2 to 4.3. After every node ran the new binaries cleanly for a week, an engineer finalized it:

```
$ kafka-features.sh --bootstrap-controller controller-1:9093 describe
Feature: metadata.version  SupportedMinVersion: 3.3-IV3  SupportedMaxVersion: 4.3-IV0  FinalizedVersionLevel: 4.3-IV0
Feature: kraft.version     SupportedMinVersion: 0        SupportedMaxVersion: 1        FinalizedVersionLevel: 1
```

Two days later a regression is found in an internal tool and management asks to "go back to 4.2 until it is fixed". What do you tell them?

- A. Run `kafka-features.sh downgrade --release-version 4.2` on the controller; metadata downgrades are online operations and the brokers pick up the lower level automatically.
- B. The cluster cannot go back. The 4.3 metadata version carries metadata changes, so no downgrade path exists; the brokers must stay on 4.3 and the regression has to be fixed forward. The rollback window was the period *before* finalizing, while the new binaries ran at the old metadata version.
- C. Set `inter.broker.protocol.version=4.2` in `server.properties` and roll the brokers; that is the supported way to pin protocol behaviour after an upgrade.
- D. Downgrade is possible but requires a full cluster stop: shut every node down, run `kafka-storage.sh format --release-version 4.2`, and restart.

### Question 23 — `[ARCH · Replication mechanisms · Matching]`

Match each cross-site mechanism to the statement that describes its offset behaviour and recovery characteristics.

| # | Mechanism |
|---|---|
| 1 | A stretch cluster spanning three data centres with `min.insync.replicas=2` |
| 2 | MirrorMaker 2 with `DefaultReplicationPolicy` |
| 3 | Cluster Linking from a primary to a standby cluster |
| 4 | A Confluent Multi-Region Cluster with observers in the remote region |

| Letter | Statement |
|---|---|
| W | Asynchronous; the destination topics are renamed `{source}.{topic}` and consumer offsets have to be translated from the checkpoints topic |
| X | Synchronous ISR replication inside a single cluster — RPO = 0 and RTO ≈ 0, paid for by every `acks=all` write crossing a site boundary |
| Y | Asynchronous by default, but the remote replicas can be promoted into the ISR automatically, so RPO = 0 is achievable for chosen topics — Confluent Platform only |
| Z | Asynchronous broker-native pull; topic names and offsets are byte-for-byte identical at the destination, and the mirror topics stay read-only until they are promoted |

- A. 1-X · 2-Z · 3-W · 4-Y
- B. 1-X · 2-W · 3-Y · 4-Z
- C. 1-Y · 2-W · 3-Z · 4-X
- D. 1-X · 2-W · 3-Z · 4-Y

### Question 24 — `[CFG · Compression placement · Multi — Choose 2]`

A cluster's inter-zone network is saturated while broker CPU sits around 45 %. Producers already send `compression.type=lz4`. An engineer proposes setting `compression.type=zstd` on the busiest topics. Which **two** statements about that proposal are correct? (Choose two.)

- A. When a topic's `compression.type` differs from the codec the producer used, the broker must decompress and recompress every batch, spending CPU it was not spending before.
- B. Broker-side compression also compresses the replication traffic a second time, so inter-broker bandwidth falls by roughly the same ratio again.
- C. Setting `compression.type` on a topic forces every consumer to configure the same codec, otherwise it cannot read the topic.
- D. With the broker default `compression.type=producer`, the broker stores the batch exactly as the producer sent it, so no broker CPU is spent on compression at all.
- E. Compression is applied per record, so topics with many small records benefit the least from any codec change.

### Question 25 — `[SEC · mTLS vs SCRAM · Multi — Choose 2]`

A team is choosing between mutual TLS and `SASL/SCRAM-SHA-512` for service-to-service authentication on a Kafka 4.3 cluster. Which **two** statements should drive the decision? (Choose two.)

- A. Revoking an mTLS certificate takes effect on already-established connections immediately, because the broker re-validates the chain on every request.
- B. With mTLS the principal is the certificate's full distinguished name unless a mapping rule is configured, so every ACL must be written against that DN and every certificate reissue risks invalidating the ACLs.
- C. SCRAM never puts the password on the wire, so `SASL_PLAINTEXT` is an acceptable transport for service-to-service traffic.
- D. mTLS requires `AclAuthorizer`, because certificate principals cannot be represented in the metadata log.
- E. SCRAM credentials live in the metadata log, so a service account can be added or revoked with `kafka-configs.sh` while the cluster runs — no broker restart and no file to distribute.

### Question 26 — `[FUND · ELR and min.insync.replicas · Single]`

A cluster runs with `eligible.leader.replicas.version=1`. A configuration-management run re-applies the cluster-level `min.insync.replicas`, writing the value **2** where **2** was already set. What is the effect?

- A. None — applying an identical value is a no-op and the controller discards the request.
- B. The ELR feature is downgraded to version 0 and has to be re-enabled with `kafka-features.sh`.
- C. Every partition's ELR set is discarded. Updating the cluster-level `min.insync.replicas` clears ELR state even when the value does not change; the sets rebuild only as replicas subsequently drop out of the ISR.
- D. The request is rejected: with ELR enabled, `min.insync.replicas` may only be set at topic level.

### Question 27 — `[OBS · Alert design · Multi — Choose 2]`

You are defining the alerts that wake someone at 03:00 for a new cluster, as distinct from the alerts that merely open a ticket. Which **two** belong in the wake-someone-up tier? (Choose two.)

- A. `UnderReplicatedPartitions > 0` sustained for 1 minute.
- B. `IsrShrinksPerSec > 0` sustained for 1 minute.
- C. `OfflinePartitionsCount > 0` sustained for 1 minute.
- D. The sum of `ActiveControllerCount` across all nodes ≠ 1 sustained for 1 minute.
- E. `RequestHandlerAvgIdlePercent < 0.3` sustained for 1 minute.

### Question 28 — `[CFG · Storage layout · Single]`

New brokers ship with **twelve 2 TB NVMe devices** each. The cluster will run `replication.factor=3`. The storage team wants RAID; the Kafka team wants JBOD. Which layout **maximises usable capacity and write throughput while keeping a single device failure from taking the whole broker out of service**?

- A. RAID 10 across the twelve devices with a single `log.dirs` entry, so a device failure is invisible to Kafka.
- B. RAID 5 across the twelve devices, giving parity protection at the cost of one device's capacity.
- C. JBOD — twelve `log.dirs` entries. Kafka's own replication already provides redundancy, RAID would cost capacity and write throughput, and because KRaft supports JBOD a failed log directory takes only the partitions on that device offline while the broker keeps serving the rest.
- D. JBOD with twelve `log.dirs` entries plus `remote.storage.enable=true` on every topic, so a failed device loses nothing that matters.

### Question 29 — `[TROUBLE · Left-over throttles · Single]`

Three weeks after a partition reassignment, every broker restart now leaves `UnderReplicatedPartitions` elevated for close to an hour, where it used to clear in two minutes. Nothing else changed.

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --describe --entity-type brokers --entity-name 4
Dynamic configs for broker 4 are:
  leader.replication.throttled.rate=10485760 sensitive=false synonyms={DYNAMIC_BROKER_CONFIG:leader.replication.throttled.rate=10485760}
  follower.replication.throttled.rate=10485760 sensitive=false synonyms={DYNAMIC_BROKER_CONFIG:follower.replication.throttled.rate=10485760}
```

What happened, and what is the correct fix?

- A. A quota was applied to the replication client id; remove it with `kafka-configs.sh --entity-type clients --delete-config`.
- B. `auto.leader.rebalance.enable` is throttling leader movement; disable it and run a preferred leader election by hand.
- C. The brokers were restarted with `--zookeeper` throttle settings left in `/config/brokers/4`; delete the znode and restart.
- D. The reassignment was executed with `--throttle` but `--verify` was never run, so the four throttle configurations were never removed and replication has been capped at 10 MB/s ever since. Run `--verify` with the original plan, or delete the two broker-level and two topic-level throttle configurations directly.

### Question 30 — `[CONNECT · Error handling design · Multi — Choose 2]`

A JDBC **source** connector is silently skipping rows; the destination topic is missing records that exist in the database. The connector configuration contains `errors.tolerance=all` and nothing else from the `errors.*` family. The team asks for a dead letter queue. Which **two** statements are correct? (Choose two.)

- A. Adding `errors.deadletterqueue.topic.name=dlq-jdbc` to this connector will route the failed rows to that topic now that `errors.tolerance=all` is set.
- B. Dead letter queues exist only for **sink** connectors; the source connector configuration has no `errors.deadletterqueue.*` properties, so the failed rows must be captured another way.
- C. `errors.tolerance=all` with no dead letter queue discards bad records silently, which is exactly the behaviour being observed.
- D. `errors.deadletterqueue.context.headers.enable` defaults to `true`, so the failure reason is already being recorded on each skipped row.
- E. `errors.retry.timeout` defaults to `-1`, so Connect has in fact been retrying each failed row indefinitely rather than skipping it.

### Question 31 — `[ARCH · Stretch topology · Single]`

Two data centres sit **8 km apart** on dedicated dark fibre; the measured round-trip latency is **1.2 ms** and has never exceeded 4 ms. The requirement is **RPO = 0** — no acknowledged record may be lost — **and the cluster must keep a controller majority through the loss of either data centre**. A third site is available but can only host small virtual machines. What do you build?

- A. One stretch cluster across the two data centres, brokers and controllers split evenly, `min.insync.replicas=2`.
- B. Two independent clusters with a Cluster Link from the primary to the secondary, failing over by promoting the mirror topics.
- C. A "2.5 data centre" stretch cluster: full brokers **and** controllers in both main sites, plus a **third site running controller nodes only**, so the quorum keeps a majority when either main site is lost. With replicas in both sites and `min.insync.replicas=2`, every acknowledged write is already in both sites.
- D. One stretch cluster across the two data centres with five controllers — three in DC1, two in DC2 — so the odd number prevents split brain.

### Question 32 — `[CFG · Partition sizing · Single]`

A new topic `telemetry` must sustain **240 MB/s** of ingest. Measurements on the same hardware show a single partition accepts about **40 MB/s** from producers, and one consumer instance processes about **8 MB/s**. The consuming service can run at most **48 instances**. How many partitions do you create, and why?

- A. At least 30 — `max(t/p, t/c)` = `max(240/40, 240/8)` = 30 — and because the count can only ever be raised, create 48 now so the consumer group can also reach its 48-instance ceiling without a second irreversible change.
- B. 6 — `240/40` is the producer-side requirement; consumers scale independently of the partition count.
- C. 240 — one partition per MB/s, so each partition carries a light, uniform load and rebalances stay cheap.
- D. 3 — matching the replication factor; parallelism then comes from `num.replica.fetchers` and `num.io.threads`.

### Question 33 — `[SEC · SASL mechanisms · Matching]`

Match each SASL mechanism to the operational property that distinguishes it.

| # | Mechanism |
|---|---|
| 1 | `SASL/SCRAM-SHA-512` |
| 2 | `SASL/PLAIN` |
| 3 | `SASL/GSSAPI` |
| 4 | `SASL/OAUTHBEARER` |

| Letter | Operational property |
|---|---|
| W | Credentials are static entries in the broker JAAS file, so adding or revoking a user means editing a file and restarting the broker |
| X | Credentials live in the metadata log; users are created and revoked at runtime with `kafka-configs.sh --entity-type users`, with no restart |
| Y | Requires an external Kerberos KDC and a keytab per principal; the authenticated principal looks like `service@REALM` |
| Z | The broker validates a bearer token minted by an external identity provider; production use requires a real callback handler or JWT retriever, not the unsecured dev module |

- A. 1-W · 2-X · 3-Y · 4-Z
- B. 1-X · 2-W · 3-Y · 4-Z
- C. 1-X · 2-W · 3-Z · 4-Y
- D. 1-X · 2-Y · 3-W · 4-Z

### Question 34 — `[FUND · Choosing the reversible action · Single]`

Every broker is at **88 %** disk. The growth comes from one topic, `debug-events`, whose `retention.ms` is 30 days and which no consumer group has read for three weeks. You need space within the hour, and you want to be able to **restore normal behaviour with a single command** if the decision turns out to be wrong.

- A. `kafka-topics.sh --delete --topic debug-events` — the fastest reclaim, and the topic can simply be recreated with the same name afterwards.
- B. Set `retention.ms=259200000` as a topic override on `debug-events`, let the retention checker (`log.retention.check.interval.ms`, 300000 ms) delete the expired segments, and remove the override later with `--delete-config`. The expired segments are gone either way, but the topic, its topic id, its ACLs and every committed offset survive.
- C. Set `log.retention.bytes=1073741824` as a cluster-wide dynamic default so every topic is trimmed at once and the whole cluster gets headroom.
- D. Set `cleanup.policy=compact` on `debug-events` so only the latest record per key is kept and the disk usage collapses.

### Question 35 — `[TROUBLE · Lag with a full consumer group · Single]`

A group has been lagging for six hours. The topic has 24 partitions and the group has 24 members.

```
$ kafka-consumer-groups.sh --bootstrap-server broker-1:9092 --describe --group enrich

GROUP   TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG       CONSUMER-ID
enrich  events   0          884211          884902          691       enrich-3-a1b2
enrich  events   1          871004          871655          651       enrich-7-c3d4
enrich  events   2          402118          9915402         9513284   enrich-1-e5f6
enrich  events   3          883977          884610          633       enrich-9-g7h8
...      (partitions 4-23 all show LAG between 600 and 900)
```

Every member is alive and CPU across the fleet is under 20 %. What is the FIRST action, given that the team wants to avoid an irreversible change?

- A. Raise the partition count from 24 to 48 so the work can be spread over more consumers.
- B. Add 24 more consumer instances so each partition is served by two members.
- C. Stop and look at the key distribution: the lag is concentrated in **one** partition while the other 23 are healthy, so neither more partitions nor more consumers can help. A hot key — or a producer that pins a large share of traffic to one key — is serialising the work; fix the key or the partitioner.
- D. Raise `max.poll.records` on the consumers so each poll does more work per round trip.

### Question 36 — `[CFG · Configuration precedence · Multi — Choose 3]`

Topic `sessions` currently resolves `retention.ms` from three places: `log.retention.hours=168` in every broker's `server.properties`; a cluster-wide dynamic default `log.retention.ms=259200000`; and a topic override `retention.ms=604800000` on `sessions` itself. Which **three** statements are correct? (Choose three.)

- A. The static `log.retention.hours=168` outranks the dynamic cluster-wide default, because static configuration is applied when the broker starts.
- B. The value in force on `sessions` is 604800000, because a dynamic **topic** config outranks every broker-level source.
- C. Only the broker log can reveal which source is winning; `kafka-configs.sh` reports the effective value without its provenance.
- D. Writing a new cluster-wide dynamic default will not change `sessions` at all, because the topic override still wins.
- E. Removing the topic override with `--delete-config` leaves `sessions` on the cluster-wide dynamic default of 3 days — not on the documented 7-day default.

### Question 37 — `[OBS · Proving a tuning change worked · Single]`

`num.io.threads` was raised from 8 to 16 on one broker as a per-broker dynamic config, deliberately leaving the other five brokers untouched as a control group. Which pair of readings decides whether the change helped?

- A. `RequestHandlerAvgIdlePercent` climbing back above 0.3 on the changed broker, together with the `RequestQueueTimeMs` component of `TotalTimeMs` falling relative to the control brokers.
- B. `NetworkProcessorAvgIdlePercent` and `BytesInPerSec` on the changed broker.
- C. `UnderReplicatedPartitions` and `IsrShrinksPerSec` across the cluster.
- D. `queued.max.requests` and `ResponseSendTimeMs` on the changed broker.

### Question 38 — `[CONNECT · Setting up MirrorMaker 2 · Ordering]`

Cluster **A** must be mirrored to standby cluster **B** with MirrorMaker 2. Put the steps in the order they are performed.

| # | Step |
|---|---|
| 1 | Verify the flow: check the `heartbeats` topic, the `replication-latency-ms` metric and that `A.checkpoints.internal` is being written on B |
| 2 | Declare `clusters = A, B` in `mm2.properties` with `A.bootstrap.servers` and `B.bootstrap.servers` |
| 3 | Set `A->B.enabled = true` with the topic and group filters, then start the MirrorMaker 2 processes **close to cluster B**, passing `--clusters B` |
| 4 | Decide the replication policy — keep `DefaultReplicationPolicy` (destination topics named `A.<topic>`) or switch to `IdentityReplicationPolicy` for an active/passive migration |

- A. 2 → 3 → 4 → 1
- B. 4 → 2 → 3 → 1
- C. 2 → 4 → 3 → 1
- D. 2 → 4 → 1 → 3

### Question 39 — `[ARCH · Cross-zone read cost · Single]`

A cluster runs across three availability zones with consumers in each zone. To cut the cross-zone egress bill, the team set `broker.rack` on every broker (with a rolling restart) and `client.rack` on every consumer. Three weeks later the bill is unchanged and every consumer still fetches from the partition leader. What is missing?

- A. `client.rack` must also be set on the producers so that writes stay inside a zone.
- B. The replication factor must be raised so that every zone holds a replica of every partition.
- C. `metadata.max.age.ms` on the consumers is too high, so they have not yet picked up the preferred read replica.
- D. `replica.selector.class` was never changed. The default selector always returns the leader, so `broker.rack` and `client.rack` on their own do nothing; the brokers need `replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector`.

### Question 40 — `[CFG · Controller topology migration · Single]`

A 3-node cluster started life as a pilot with `process.roles=broker,controller` and now carries production traffic for 40 teams. The team wants dedicated controllers so that a broker-side incident — a garbage-collection pause, a full disk, a runaway client — can no longer destabilise the control plane. Which plan gets there with the least downtime?

- A. Leave combined mode and raise `controller.quorum.fetch.timeout.ms` and `controller.quorum.election.timeout.ms` so the quorum rides out broker-side pauses.
- B. Check `kafka-features.sh describe` first: if `kraft.version` is **1** (dynamic quorum), format three new controller-only nodes, add them with `kafka-metadata-quorum.sh add-controller`, wait for each to catch up, then remove the controller role from the three combined nodes one at a time with `remove-controller` and a restart of each node as `process.roles=broker`.
- C. Reformat all three nodes with `kafka-storage.sh format --standalone` against three new controller nodes, and restore the topics from a backup.
- D. Set `process.roles=broker` on the three nodes and restart them; the controller quorum re-forms automatically on whichever nodes are reachable.

### Question 41 — `[SEC · Credential revocation · Multi — Choose 2]`

A contractor leaves the company today. Their service account authenticates with `SASL/SCRAM-SHA-512` and currently holds an **open, authenticated connection** to the cluster. Security requires that the credential stop working immediately, not at the next reconnect. Which **two** steps are required? (Choose two.)

- A. Delete the credential with `kafka-configs.sh --bootstrap-server ... --alter --delete-config 'SCRAM-SHA-512' --entity-type users --entity-name contractor`.
- B. Perform a rolling restart of every broker so the in-memory credential cache is discarded.
- C. Delete the `/config/users/contractor` znode as well, because `kafka-configs.sh` only updates the broker cache.
- D. Rotate the cluster's `delegation.token.secret.key`, which also invalidates SCRAM credentials derived from it.
- E. Set a non-zero `connections.max.reauth.ms` on the listener — it defaults to **0**, which disables re-authentication, so an already-authenticated connection keeps working indefinitely after the credential is deleted.

### Question 42 — `[TROUBLE · Listener advertisement · Single]`

A new `EXTERNAL` listener was added for partner traffic. Partners reach the bootstrap address, receive metadata, and then hang:

```
org.apache.kafka.common.errors.TimeoutException: Topic feed not present in metadata after 60000 ms
```

A packet capture shows the metadata response naming `broker-2.internal.corp:9094`, which partners cannot resolve. An engineer tried to correct it live and got:

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type brokers --entity-name 2 \
    --alter --add-config 'advertised.listeners=EXTERNAL://partner-2.example.com:9094,INTERNAL://broker-2.internal.corp:9092'
Error while executing config command with args ...
java.lang.IllegalArgumentException: Cannot update these configs dynamically: Set(advertised.listeners)
```

What is the correct fix?

- A. The diagnosis is right but the method is not: in KRaft, `advertised.listeners` is no longer a dynamically updatable config. Correct it in each broker's `server.properties` and perform a rolling restart, waiting for `UnderReplicatedPartitions` to return to 0 between brokers.
- B. Add `control.plane.listener.name=EXTERNAL` so the external listener is allowed to carry metadata responses.
- C. The rejection means the property name is wrong; in KRaft the equivalent is `advertised.listener.names`, which is dynamically updatable.
- D. Raise `socket.request.max.bytes`; the metadata response for this cluster exceeds the 100 MiB default and is being truncated.

### Question 43 — `[FUND · Ordering guarantees · Multi — Choose 2]`

A platform team advertises "records for the same `customerId` are processed in order". Which **two** operations can break that promise? (Choose two.)

- A. A preferred leader election that moves leadership of a partition to another replica.
- B. A partition reassignment that moves a partition's replicas to different brokers.
- C. Raising the topic's partition count, because `hash(customerId) % partitions` then maps the same customer to a different partition than the records already stored.
- D. A producer running with `enable.idempotence=false` and `max.in.flight.requests.per.connection=5` retrying a batch that failed while later batches succeeded.
- E. Turning on `compression.type=zstd` at the topic level.

### Question 44 — `[SEC · Connect credential isolation · Single]`

On a shared Connect cluster, a tenant submitted a connector containing `consumer.override.sasl.jaas.config` naming **another** team's SCRAM user, and it worked. Tenants legitimately need to override throughput properties such as `consumer.override.max.poll.records`. Which worker-level change stops the impersonation while keeping the legitimate overrides?

- A. Set `connector.client.config.override.policy=None`, which removes the whole override mechanism.
- B. Add a `Deny` ACL for `User:connect-worker` on every other tenant's topics.
- C. Set `connector.client.config.override.policy=Principal`, which restricts overrides to the connector's own principal.
- D. Set `connector.client.config.override.policy=Allowlist` on every worker and enumerate only the properties tenants may override; anything outside the list — including `sasl.jaas.config` — is then rejected when the connector is created. This has been the recommendation since 4.2 and becomes the default in 5.0.

### Question 45 — `[CFG · Long fat links · Single]`

A MirrorMaker 2 flow between two regions with **80 ms** round-trip latency tops out at 40 MB/s even though the link is provisioned at 1 Gbps. Neither cluster is CPU-bound, disks are idle, and `replication-latency-ms` grows steadily. What is the cause, and what is the fix?

- A. The TCP window is the limit: at the 102400-byte default for `socket.send.buffer.bytes` / `socket.receive.buffer.bytes`, one connection can only carry about 1.25 MB/s over an 80 ms path. Raise the socket buffers on the brokers and the corresponding client properties on the MirrorMaker workers; because those broker configs are **read-only**, the change needs a rolling restart.
- B. `num.replica.fetchers` is 1; raise it on both clusters so replication fetches in parallel across the link.
- C. `replica.fetch.max.bytes` caps each fetch response at 1 MiB; raise it on the destination cluster.
- D. The destination brokers need `compression.type=zstd` so less data crosses the link.

### Question 46 — `[OBS · Early warning before data loss · Single]`

Topic `events` retains 24 hours. A consumer group runs a nightly batch that occasionally takes far longer than planned. Operations wants an alert that fires **before** unread records are deleted by retention, not after. Which signal do they alert on?

- A. `records-lag-max` with a threshold of 1,000,000 records.
- B. The `LAG` column from `kafka-consumer-groups.sh --describe`, scraped every minute.
- C. The consumer's **`records-lead-min`**: it measures the distance between the consumer's position and the partition's **log start offset**, so it falls toward 0 exactly as retention catches up with the consumer. Lag measures the distance to the head of the log, which says nothing about how close the tail is.
- D. The broker's `UnderMinIsrPartitionCount`, since unread data is at risk whenever the ISR is short.

### Question 47 — `[SEC · Authorization and encryption baseline · Single]`

An auditor asks two questions about a Kafka 4.3 cluster: *who can currently read the `payroll` topic*, and *is the data encrypted at rest*. The cluster's brokers have `listeners=SASL_SSL://:9093`, `sasl.enabled.mechanisms=SCRAM-SHA-512`, no value for `authorizer.class.name`, and unencrypted block devices. What is the accurate answer?

- A. Only super users can read `payroll`, because a resource with no ACLs is denied by default; the data is encrypted at rest because the listener uses SSL.
- B. Any authenticated principal can read `payroll` because `allow.everyone.if.no.acl.found` defaults to `true`; the data is encrypted at rest by the broker keystore.
- C. Only super users can read `payroll`; encryption at rest must be supplied by the filesystem or the block device.
- D. **Every** authenticated principal can read `payroll`: with `authorizer.class.name` unset there is no authorizer at all, so the deny-by-default rule never comes into play. And Kafka has no built-in encryption at rest — it must come from the filesystem, the block device or the application. To begin enforcing, set `authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer` on every broker **and** every controller.

### Question 48 — `[ARCH · Sizing from numbers · Multi — Choose 2]`

A new cluster must absorb **60 MB/s** of ingest with `replication.factor=3` and **7 days** of retention. The standard machine has 64 GB RAM and 12 TB of usable disk. Which **two** statements are correct? (Choose two.)

- A. The broker heap should be set to about 48 GB so that most of the 64 GB is actually used by Kafka rather than sitting idle.
- B. The storage requirement is roughly 131 TB — `60 MB/s × 604,800 s × 3 × 1.2` — so on storage grounds alone the cluster needs at least 11 brokers.
- C. Enabling tiered storage removes the disk constraint by itself, because segments are uploaded as soon as they roll and the local copy is deleted.
- D. Because `replication.factor=3`, only a third of the 131 TB is real data, so four brokers are sufficient.
- E. The cluster must still carry the full load with one broker — or one rack — missing, so sizing it to run at 90 % of capacity when everything is healthy guarantees that the first failure cascades.

### Question 49 — `[TROUBLE · Loss of controller majority · Single]`

A cluster with three dedicated controllers loses two of them in a rack failure:

```
$ kafka-metadata-quorum.sh --bootstrap-controller controller-1:9093 describe --status
ClusterId:              M8x2wG7ZQ0-Wm1nQ4pQhVA
LeaderId:               -1
LeaderEpoch:            412
HighWatermark:          -1
CurrentVoters:          [1,2,3]
CurrentObservers:       [101,102,103,104,105,106]
```

Producers to existing partitions are still succeeding. Which description and first action are correct?

- A. The control plane is frozen — no leader elections, no topic creation, no broker registration — while the data plane keeps serving produce and fetch for partitions whose leader has not changed, using metadata the brokers already cached. The first action is to restore a second controller so the quorum regains its majority; nothing needs changing on the brokers.
- B. Produce requests will start failing with `NotControllerException` once `controller.quorum.fetch.timeout.ms` elapses, so traffic must be drained now.
- C. Promote one of the observers with `kafka-metadata-quorum.sh add-controller` to restore the majority immediately.
- D. Restart the surviving controller with `kafka-storage.sh format --standalone` so it forms a new single-node quorum and the cluster recovers at once.

### Question 50 — `[CFG · Recovery after an unclean stop · Single]`

A broker with **12 data directories** was killed with `kill -9` during an emergency and took 50 minutes in log recovery on the next start. The runbook — written for Kafka 2.x — states that `num.recovery.threads.per.data.dir` defaults to **1** and that "recovery time is what it is". What should the team change?

- A. Nothing: log recovery is single-threaded per broker by design and cannot be parallelised.
- B. Raise `num.io.threads` from 8 to 32, because recovery is performed by the request handler pool.
- C. The runbook is out of date — the default became **2** in Kafka 4.0, and the config is `cluster-wide` so it can be raised with `kafka-configs.sh` before the next start; with 12 data directories a value of 4–8 recovers many directories in parallel. The bigger win is procedural: `controlled.shutdown.enable` is `true` by default, so a clean stop avoids the recovery pass entirely — reserve `kill -9` for the case where the broker will not stop.
- D. Set `log.flush.interval.messages=1` so every record is fsynced and recovery is never needed.

### Question 51 — `[FUND · High watermark and follower reads · Single]`

After enabling follower fetching, a team measures that consumers reading from an in-zone follower see records on average **200 ms** later than consumers reading from the leader. The risk owner asks whether this weakens any guarantee. What is the accurate answer?

- A. It does: a follower serves records it has not yet had confirmed, so a consumer may read data that is later lost if the leader fails.
- B. It does not: a follower serves records only up to the **high watermark**, exactly as the leader does, and the follower's high watermark advances one fetch round later. The records are never uncommitted — only slightly older. Follower fetching trades freshness for cross-zone cost, not correctness.
- C. It does: the follower applies `min.insync.replicas` locally and withholds records until every replica is in sync, which can stall reads indefinitely.
- D. It does not, and the delay disappears if `replica.lag.time.max.ms` is lowered from 30000 to 5000 so followers are kept tighter to the leader.

### Question 52 — `[CONNECT · Internal topic durability · Single]`

A Connect cluster grew from a one-broker sandbox to three brokers. Its internal topics were auto-created back on the sandbox:

```
$ kafka-topics.sh --bootstrap-server broker-1:9092 --describe --topic connect-configs --topic connect-offsets --topic connect-status
Topic: connect-configs  PartitionCount: 1   ReplicationFactor: 1  Configs: cleanup.policy=compact
Topic: connect-offsets  PartitionCount: 25  ReplicationFactor: 1  Configs: cleanup.policy=compact
Topic: connect-status   PartitionCount: 5   ReplicationFactor: 1  Configs: cleanup.policy=compact
```

What is the risk, and what is the correct remediation?

- A. Every internal topic has `replication.factor=1`, so losing the broker that leads `connect-configs` costs the cluster its entire connector configuration and it cannot be rebuilt. Raise the replication factor of the **existing** topics with a `kafka-reassign-partitions.sh` plan — the worker's `config.storage.replication.factor` is consulted only when the topic is created.
- B. The partition counts are swapped: `connect-configs` must have 25 partitions and `connect-offsets` exactly 1. Recreate them with the correct counts.
- C. Set `config.storage.replication.factor=3`, `offset.storage.replication.factor=3` and `status.storage.replication.factor=3` in `connect-distributed.properties` and restart the workers; Connect recreates the topics with the new factor.
- D. Delete the three topics and let Connect recreate them correctly on the three-broker cluster; connector configurations are re-read from the REST API at startup, so nothing is lost.

### Question 53 — `[SEC · Adding security to a live cluster · Single]`

A cluster serves 200 client applications over `PLAINTEXT://:9092`. Security must become `SASL_SSL` with `SCRAM-SHA-512`. Application teams cannot all be changed on the same day, and **no downtime is acceptable**. What is the correct approach?

- A. Change `listeners` to `SASL_SSL://:9092` and roll the brokers; clients that have been updated reconnect immediately and the rest are fixed as they fail.
- B. Enable `authorizer.class.name` first with `allow.everyone.if.no.acl.found=true`, then change the protocol once ACLs are in place.
- C. Keep the single port and map the new protocol onto it with `listener.security.protocol.map`, then roll the brokers — one port keeps the client configuration simple and the migration short.
- D. Add a **second** listener, e.g. `SASL_SSL://:9093`, alongside the existing `PLAINTEXT://:9092` using `listener.security.protocol.map`, and roll the brokers. Migrate clients to 9093 at their own pace, then move `inter.broker.listener.name` to the secure listener in another roll, and only then remove the plaintext listener. A cluster is allowed to run listeners at different security levels simultaneously.

### Question 54 — `[CFG · Decommissioning a broker · Multi — Choose 2]`

Broker 6 is being removed from a 6-broker Kafka 4.3 cluster. Which **two** steps belong in the procedure? (Choose two.)

- A. Set `cordoned.log.dirs="*"` on broker 6 with `kafka-configs.sh`, so the controller stops placing new partitions on it while the drain is in progress.
- B. Delete broker 6's `meta.properties` and restart it, so it re-registers as an observer and stops receiving partitions.
- C. Move every partition off broker 6 with `kafka-reassign-partitions.sh`, confirm with `--verify`, stop the broker, and then run `kafka-cluster.sh unregister --id 6`.
- D. Lower `default.replication.factor` to 2 first, so fewer replicas have to be moved off the broker.
- E. Remove broker 6 from `controller.quorum.voters` on every node and restart them.

### Question 55 — `[OBS · Metadata propagation · Single]`

A monitoring dashboard shows these readings on a healthy-looking cluster:

```
controller-1 (active)   kafka.controller:type=KafkaController,name=LastAppliedRecordLagMs   = 0
controller-2 (standby)  kafka.controller:type=KafkaController,name=LastAppliedRecordLagMs   = 4
controller-3 (standby)  kafka.controller:type=KafkaController,name=LastAppliedRecordLagMs   = 6
broker-104              kafka.server:type=broker-metadata-metrics,name=last-applied-record-lag-ms = 41000
```

What do these numbers say?

- A. Everything is healthy; the 0 on controller-1 proves the active controller is keeping up with the metadata log.
- B. Controller-1 is the problem: a lag of 0 means it has stopped applying records at all.
- C. Broker-104 is applying metadata **41 seconds** behind the controller, so it is answering clients from stale metadata — old leader information, topics and ACL changes it has not seen yet. The 0 on the active controller carries no information at all: it is zero by definition and can never be used as a health signal.
- D. The two standby controllers are unhealthy, because any non-zero lag on a voter blocks commits in the quorum.

### Question 56 — `[TROUBLE · ISR instability · Multi — Choose 2]`

For six hours `IsrShrinksPerSec` and `IsrExpandsPerSec` have both oscillated around 3 per second, and `UnderReplicatedPartitions` swings between 0 and 40. No broker has restarted, no deployment happened, and produce volume is flat. Which **two** causes are worth investigating first? (Choose two.)

- A. `replica.lag.time.max.ms` is too high at 30000 ms; lowering it to 5000 ms will stabilise the ISR.
- B. `unclean.leader.election.enable` is `false`, which prevents replicas from rejoining the ISR once they have fallen behind.
- C. `__consumer_offsets` has too few partitions for the number of consumer groups.
- D. Stop-the-world garbage-collection pauses on the follower brokers long enough for them to miss fetches past `replica.lag.time.max.ms`.
- E. Disk write-latency spikes on a subset of brokers, so followers cannot keep pace with the leader's append rate.

### Question 57 — `[FUND · Mirror topic semantics · Single]`

During a disaster-recovery drill, applications were failed over to a Cluster Linking standby. Consumers resumed at the right offsets, but every producer failed:

```
org.apache.kafka.common.errors.InvalidRequestException: Topic 'orders' is a mirror topic and is read-only
```

What went wrong, and what is the correct step?

- A. The ACLs synced from the source did not include the DR principals; grant `Write` on `orders` at the standby with `kafka-acls.sh`.
- B. Nothing is broken — mirror topics are read-only by design. The drill skipped a step: the mirror topic must be **promoted** (failed over), at which point it stops mirroring and becomes an ordinary writable topic. Until then a Cluster Linking standby is a read-only copy.
- C. Restart the standby brokers with `mirror.topic.read.only=false` so the mirror topics accept writes.
- D. Cluster Linking cannot support failover; switch the DR mechanism to `kafka-mirror-maker.sh --whitelist 'orders'`, whose destination topics are ordinary writable topics.

### Question 58 — `[ARCH · Active/active replication · Multi — Choose 2]`

A team is deploying MirrorMaker 2 in an active/active topology (`A->B, B->A`) with the default replication policy. Which **two** consequences must they design for? (Choose two.)

- A. Offsets are identical in both clusters, so a consumer can fail over and `seek` to the same numeric offset it last committed.
- B. Each site ends up holding both the locally produced topic (`orders`) and the remote copy under a prefixed name (`B.orders` at A, `A.orders` at B), so consumers that must see all traffic have to subscribe to both — usually with a subscription pattern.
- C. Console consumer groups are mirrored by default, so consumer-lag dashboards work in both sites without extra configuration.
- D. The prefixing performed by `DefaultReplicationPolicy` is precisely what prevents an infinite replication loop; switching to `IdentityReplicationPolicy` in an active/active topology would make records bounce between the clusters forever.
- E. MirrorMaker 2 runs as its own daemon, so no Kafka Connect infrastructure has to be operated.

### Question 59 — `[CONNECT · Worker restart behaviour · Multi — Choose 2]`

A Connect worker is restarted for a JVM upgrade. Its 30 tasks show no assignment for about five minutes, then reappear on the same worker. Connectors on the other two workers kept running throughout. Which **two** statements explain this? (Choose two.)

- A. The delay means the tasks were lost and rebuilt from `connect-offsets`, so source records between the last committed offset and the restart are replayed.
- B. Setting `connect.protocol=eager` would remove the delay while still leaving the other workers' tasks running.
- C. `scheduled.rebalance.max.delay.ms` defaults to 300000 ms: when a worker leaves the group, the leader deliberately delays reassigning its tasks so that a worker returning inside the window gets them back without disturbing the rest of the cluster.
- D. The five minutes is the `rebalance.timeout.ms` of each connector's consumer group and has to be lowered per connector.
- E. Connect has used incremental cooperative rebalancing since Kafka 2.3 (KIP-415), so only the tasks that need to change owner are stopped; everything else keeps running through the rebalance.

### Question 60 — `[FUND · Retention and segment roll · Single]`

`retention.ms=3600000` was set on `sensor-raw` yesterday. Eighteen hours later `kafka-log-dirs.sh` still reports 40 GB for the topic and consumers can still read records that are 14 hours old. `segment.bytes` is the 1 GiB default, `segment.ms` is not set on the topic, and each partition receives about 12 MB per hour. What is happening?

- A. `log.retention.check.interval.ms` is 300000 ms and the checker has simply not run yet on those partitions; the space will be reclaimed shortly.
- B. `retention.ms` was applied at broker level where a topic override already exists, and the topic override wins; re-apply it with `--entity-type topics`.
- C. Time-based deletion only runs when `cleanup.policy` is `delete,compact`; the topic is currently `delete` only.
- D. Retention deletes whole **closed** segments, never the active one. At 12 MB per hour a partition needs roughly 85 hours to fill the 1 GiB `segment.bytes`, so nothing has been eligible for deletion yet. Set `segment.ms` on the topic — or lower `segment.bytes` — so segments roll often enough for retention to act on them.

---

> ✅ Hết giờ? Chấm bài ở [answers.md](answers.md) và điền bảng điểm theo domain trước khi xem giải thích.
