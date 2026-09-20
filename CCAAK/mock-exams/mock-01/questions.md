# 🎯 CCAAK Mock Exam 01 — 60 questions · 90 minutes

> **Exam-realistic full-length mock.** Distribution follows the official CCAAK domain weights.
> ⏱️ Set a timer for **90 minutes** (~90 seconds per question). No notes, no documentation, no pausing.
> 🔒 Answers, explanations and per-domain scoring: [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (4 options) · `Multi` (choose the stated number) · `Matching` · `Ordering`.
> Tag: `[Domain · Topic · Format]`. Domains: `CFG` `FUND` `SEC` `TROUBLE` `ARCH` `CONNECT` `OBS`.
> Anchored to **Apache Kafka 4.3** — ZooKeeper was removed in 4.0; any option that relies on it is wrong.
> 🧰 **Theme of this mock: configuration and foundations, heavy on version traps.** It leans on Cluster Configuration and Fundamentals, and deliberately plants options that were the *right answer two major versions ago* — an old default, or something from the ZooKeeper world. Run it as your baseline right after Week 7.
> Back to [mock index](../README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[CFG · Config precedence and synonyms · Single]`

A platform team set a cluster-wide retention default of one day and asked every team to confirm it took effect. One topic still keeps a week of data:

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type topics \
    --entity-name billing-events --describe --all | grep '^  retention.ms'
  retention.ms=604800000 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:retention.ms=604800000,
  DYNAMIC_DEFAULT_BROKER_CONFIG:log.retention.ms=86400000, DEFAULT_CONFIG:log.retention.ms=604800000}
```

What is the correct reading of this output, and what is the cheapest way to make the topic follow the cluster default?

- A. The cluster-wide default is queued and will apply after the next preferred leader election; no action is needed beyond waiting for `log.retention.check.interval.ms` to elapse.
- B. Synonyms are printed strongest-first, so `DYNAMIC_TOPIC_CONFIG` is the source in effect. Remove it with `kafka-configs.sh --entity-type topics --entity-name billing-events --alter --delete-config retention.ms`; the value then falls back to the next level that still exists — the dynamic cluster-wide default of 86,400,000 — not to the built-in default.
- C. The old value is cached in the `/config/topics/billing-events` znode; clear it with `kafka-configs.sh --zookeeper ... --alter --delete-config retention.ms` and the broker will reload it.
- D. `retention.ms` is a read-only configuration, so the cluster-wide default cannot reach an existing topic; every broker must be restarted with the new value in `server.properties`.

### Question 2 — `[TROUBLE · Retention vs segment roll · Single]`

To satisfy a data-deletion commitment, an operator set `retention.ms=3600000` on `audit-trail` — one partition, replication factor 3, roughly 5 MB of traffic per day. Three days later a consumer can still read records written before the change. Every other configuration on the topic and the brokers is at its 4.3 default, and `kafka-configs.sh --describe` confirms the override is present.

What is the FIRST action that will actually make the old data disappear?

- A. Lower `log.retention.check.interval.ms` from 300,000 ms so the retention thread runs more often.
- B. Set `log.roll.hours=1` on the brokers and perform a rolling restart.
- C. Set `segment.ms=3600000` on the topic. Retention only deletes **closed** segments; with `segment.bytes` at 1 GiB and `segment.ms` at seven days, a 5 MB/day topic is still writing into its first active segment, which is never eligible for deletion.
- D. Delete and re-create the topic with the correct retention, then replay the records that must be kept.

### Question 3 — `[FUND · Controller failover · Single]`

On a 4.3 cluster with three dedicated controllers and nine brokers, the node hosting the active controller is powered off. Within about two seconds a different controller node reports `ActiveControllerCount=1` and cluster administration works again.

Which description of what happened is correct?

- A. The broker with the lowest `node.id` takes over the controller role, which is why controller ids are conventionally the lowest numbers in the cluster.
- B. Whichever broker succeeds in re-creating the ephemeral `/controller` node first becomes the new controller.
- C. The remaining controllers replay the whole cluster state from the `__consumer_offsets` topic before one of them can accept writes, which is why failover takes a couple of seconds.
- D. The remaining **voters** in the controller quorum hold a Raft election once `controller.quorum.fetch.timeout.ms` expires. The winner already has the replicated metadata log on disk, so it can serve immediately. Brokers are observers of the quorum and can never be elected.

### Question 4 — `[SEC · ACL propagation · Single]`

An operator grants a new permission and immediately restarts the client:

```
$ kafka-acls.sh --bootstrap-server broker-1:9092 --add \
    --allow-principal User:svc-reports --operation Read --topic quarterly --group reporting
Adding ACLs for resource `ResourcePattern(resourceType=TOPIC, name=quarterly, patternType=LITERAL)`:
    (principal=User:svc-reports, host=*, operation=READ, permissionType=ALLOW)
```

The client logs `TopicAuthorizationException` on its first two fetch attempts and then works normally, with no further changes. What happened?

- A. ACL changes are written by the **active controller** into `__cluster_metadata`; every broker applies them asynchronously as it reads the log. The command returns as soon as the controller has committed the record, so for a few hundred milliseconds some brokers are still enforcing the old rule set. Retrying is the correct response, not re-issuing the ACL.
- B. The ZooKeeper watch that pushes ACL changes to brokers fires only on the session owner; the other brokers pick the change up on their next session refresh.
- C. `StandardAuthorizer` caches authorization decisions per principal for a fixed interval, so the first requests after a grant are always denied.
- D. The grant was incomplete — a `Group` ACL is required as well — and the client only succeeded because it fell back to an unauthenticated listener.

### Question 5 — `[CONNECT · Internal topics · Single]`

A team pre-created the three Connect internal topics with a standard script that gives every topic 25 partitions. The first distributed worker dies on startup:

```
[2026-09-12 08:41:02,517] ERROR Stopping due to error (org.apache.kafka.connect.cli.ConnectDistributed)
org.apache.kafka.common.config.ConfigException: Topic 'connect-configs' supplied via the
'config.storage.topic' property is required to have a single partition in order to be compatible
with the Kafka Connect framework, but found 25 partitions.
```

What must change?

- A. Add `config.storage.partitions=25` to `connect-distributed.properties` so the worker accepts the existing topic.
- B. Re-create `connect-configs` with exactly **one** partition and `cleanup.policy=compact`. The config topic is the only one whose partition count is fixed at 1; `connect-offsets` (default 25) and `connect-status` (default 5) are free to have more, and all three must be compacted.
- C. Delete all three topics and let the worker create them, because Connect refuses to start whenever any internal topic already exists.
- D. Raise `config.storage.replication.factor` to 25 so it matches the partition count, which is what the error is really complaining about.

### Question 6 — `[OBS · JMX exporter coverage · Single]`

An alert on unclean leader elections has never fired, even during a month in which the operations log records two forced recoveries. The Prometheus JMX exporter configuration contains a single controller rule:

```yaml
rules:
  - pattern: 'kafka.controller<type=KafkaController, name=(.+)><>Value'
    name: kafka_controller_$1
```

Why is the metric missing?

- A. `UncleanLeaderElectionsPerSec` is a rate, and rate metrics are exposed as `Count`, not `Value`, so the rule matches nothing.
- B. Unclean leader elections are recorded only in `state-change.log` and have never had a JMX metric in KRaft mode.
- C. `ActiveControllerCount` and `OfflinePartitionsCount` live under `kafka.controller:type=KafkaController`, but `UncleanLeaderElectionsPerSec` and `LeaderElectionRateAndTimeMs` live under `kafka.controller:type=**ControllerStats**`. A rule that matches only `KafkaController` silently drops them — and `UnderReplicatedPartitions` is elsewhere again, at `kafka.server:type=ReplicaManager`.
- D. Remote JMX is disabled by default, so the exporter can read only the metrics the broker pushes over the metrics reporter interface.

### Question 7 — `[CFG · Broker thread pools · Matching]`

Match each broker thread configuration to what those threads actually do.

| # | Configuration |
|---|---|
| 1 | `num.io.threads` |
| 2 | `num.replica.fetchers` |
| 3 | `num.recovery.threads.per.data.dir` |
| 4 | `background.threads` |

| Letter | What the threads do |
|---|---|
| W | Pull records from each source broker so that follower replicas keep up with their leaders |
| X | Replay and validate log segments when a broker starts up, and flush them at shutdown |
| Y | A general-purpose pool for assorted background housekeeping work |
| Z | Request handler threads that do the read and write work after a network thread has read the request off the socket |

- A. 1-W · 2-Z · 3-X · 4-Y
- B. 1-Z · 2-W · 3-X · 4-Y
- C. 1-Z · 2-X · 3-W · 4-Y
- D. 1-Y · 2-W · 3-X · 4-Z

### Question 8 — `[TROUBLE · Durability matrix · Single]`

A broker is taken down for an OS patch — one broker out of five, with controlled shutdown enabled. Producers to `ledger` immediately start failing:

```
org.apache.kafka.common.errors.NotEnoughReplicasException: The size of the current ISR Set(11, 14)
is insufficient to satisfy the min.isr requirement of 3 for partition ledger-12
```

`kafka-topics.sh --describe --topic ledger` shows `ReplicationFactor: 3  Configs: min.insync.replicas=3`. Every other topic kept writing throughout. What is the correct assessment and the right fix?

- A. The topic is under-replicated because `replica.lag.time.max.ms` is too low; raise it to 120,000 ms so the third replica is not evicted during a restart.
- B. Turn on `unclean.leader.election.enable` for `ledger` so the partition can elect a leader from outside the ISR and writes resume.
- C. Raise the replication factor to 5 with `kafka-reassign-partitions.sh`, so that losing one broker still leaves three in-sync replicas.
- D. `min.insync.replicas=3` on a topic with `replication.factor=3` leaves **zero** tolerance: any single replica loss stops every `acks=all` write. Finishing the patch restores the ISR right now; the durable fix is the planned change to `min.insync.replicas=2`, the standard pairing with RF=3.

### Question 9 — `[ARCH · Cross-cluster replication · Single]`

A bank runs Confluent Server in two data centres. The disaster-recovery requirement is that after a failover, every consumer group resumes at exactly the position it had on the primary, and the operations team — three people — wants as few moving parts as possible. Asynchronous replication is acceptable.

Which design meets the requirement with the least operational surface?

- A. **Cluster Linking.** The destination brokers pull directly from the source, so there is no Connect cluster to run; replication is byte-for-byte, offsets are identical on both sides, and consumer offsets and ACLs are synced for you. Mirror topics stay read-only until the link is promoted.
- B. MirrorMaker 2 with `IdentityReplicationPolicy` and `sync.group.offsets.enabled=true`, which makes the destination offsets identical to the source offsets.
- C. A single cluster stretched across both data centres with `broker.rack` set per site and `min.insync.replicas=2`.
- D. MirrorMaker 1 with `--whitelist '.*'`, which copies topics under their original names and preserves offsets because it writes with the same partitioner.

### Question 10 — `[CFG · Quota precedence · Single]`

A six-broker cluster has these quotas and nothing else:

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --describe --entity-type users --entity-type clients
Quota configs for user-principal 'svc-etl', default client-id are producer_byte_rate=5242880
Quota configs for the default user-principal are producer_byte_rate=20971520
Quota configs for client-id 'etl-writer' are producer_byte_rate=41943040
```

A producer authenticates as `svc-etl` with `client.id=etl-writer`. Which quota applies, and what is the most this single producer can write to the cluster as a whole?

- A. 40 MiB/s per broker, because a matching client-id quota is the most specific rule available.
- B. 5 MiB/s **per broker** — the (matching user, default client-id) rule is level 2 of the eight-level precedence list and beats both a default-user rule and a bare client-id rule. Quotas are enforced per broker, so the cluster-wide ceiling is 5 MiB/s × 6 = **30 MiB/s**.
- C. 20 MiB/s per broker, because the default user-principal rule always applies before any client-id rule.
- D. 5 MiB/s for the whole cluster, because quota accounting is aggregated by the active controller.

### Question 11 — `[FUND · Bootstrapping a KRaft cluster · Ordering]`

A new 4.3 cluster will use three dedicated controllers and five brokers, with SCRAM for inter-broker authentication. Put the bootstrap steps in the order they must be performed.

| # | Step |
|---|---|
| 1 | Run `kafka-storage.sh random-uuid` once and reuse that single `cluster.id` everywhere |
| 2 | Run `kafka-storage.sh format` on every node with that `cluster.id`, passing `--add-scram 'SCRAM-SHA-512=[name="admin",password=...]'` so the inter-broker credential exists before anything starts |
| 3 | Start the controller nodes and confirm a leader with `kafka-metadata-quorum.sh --bootstrap-controller controller-1:9093 describe --status` |
| 4 | Start the broker nodes, which register with the quorum as observers |

- A. 1 → 2 → 3 → 4
- B. 1 → 3 → 2 → 4
- C. 2 → 1 → 3 → 4
- D. 1 → 2 → 4 → 3

### Question 12 — `[SEC · SASL mechanisms · Matching]`

Match each SASL mechanism to where its credentials live and how they are changed.

| # | Mechanism |
|---|---|
| 1 | `SCRAM-SHA-512` |
| 2 | `PLAIN` |
| 3 | `GSSAPI` |
| 4 | `OAUTHBEARER` |

| Letter | Where the credentials live |
|---|---|
| W | Static entries in the broker's JAAS configuration — adding or removing a user means editing the file and bouncing the broker |
| X | An external KDC holds the identities; the broker authenticates itself with a keytab |
| Y | The broker holds no user list at all; it validates a bearer token minted by an external identity provider |
| Z | The KRaft metadata log holds the credentials; users are added, re-hashed or deleted with `kafka-configs.sh --entity-type users` while the cluster runs |

- A. 1-W · 2-Z · 3-X · 4-Y
- B. 1-Z · 2-W · 3-Y · 4-X
- C. 1-X · 2-W · 3-Z · 4-Y
- D. 1-Z · 2-W · 3-X · 4-Y

### Question 13 — `[CFG · Message size chain · Multi — Choose 2]`

A team must publish 3 MiB records to a new topic. Which **two** statements about the size limits involved are correct on Apache Kafka 4.3 with otherwise default settings?

- A. A record larger than `max.request.size` (default 1,048,576) is rejected inside `KafkaProducer.send()` before any bytes reach a broker, so no broker-side change alone can fix it.
- B. `replica.fetch.max.bytes` (1 MiB) is a hard ceiling on replication: a batch larger than it is never fetched, so followers fall permanently out of the ISR.
- C. `socket.request.max.bytes` defaults to 1,048,576 and must be raised alongside the message size limits.
- D. A topic's `max.message.bytes` overrides the broker's `message.max.bytes` (default 1,048,588) for that topic, and both can be raised while the cluster runs — neither needs a restart.
- E. Raising `message.max.bytes` requires a rolling restart because it is a read-only broker configuration.

### Question 14 — `[TROUBLE · Throttled throughput · Multi — Choose 2]`

An ETL producer has been pinned at almost exactly 10 MB/s per broker for a week. The broker logs contain no warnings, the producer's `record-error-rate` is 0, and no callback has ever received an exception. Which **two** steps correctly confirm the suspected cause?

- A. Conclude that quotas are not involved: a quota violation surfaces as `ThrottlingQuotaExceededException` in the producer callback, and no exception was ever raised.
- B. Read the producer-side metric `produce-throttle-time-avg`; a non-zero value means the broker is deliberately delaying responses.
- C. Read the broker MBean `kafka.server:type=Produce,user=...,client-id=...` and check its `throttle-time` attribute, which should be 0 on an unthrottled client.
- D. Assume the 10 MB/s is a cluster-wide total, since quotas are enforced by the active controller across all brokers.
- E. Raise `queued.max.requests` above 500 to relieve the back-pressure that is capping the producer.

### Question 15 — `[CFG · JBOD layout · Single]`

Broker 4 has three data directories of equal size. Disk usage is badly skewed although every directory holds the same number of partitions:

```
$ kafka-log-dirs.sh --bootstrap-server broker-4:9092 --describe --broker-list 4 | tail -1
{"version":1,"brokers":[{"broker":4,"logDirs":[
 {"logDir":"/data/1","error":null,"totalBytes":2000398934016,"usableBytes":130047882240,
  "partitions":[{"partition":"clickstream-3","size":1421000000000,"offsetLag":0,"isFuture":false}, ...]},
 {"logDir":"/data/2","error":null,"totalBytes":2000398934016,"usableBytes":1502279253504,"partitions":[...]},
 {"logDir":"/data/3","error":null,"totalBytes":2000398934016,"usableBytes":1488113920000,"partitions":[...]}]}]}
```

Why did this happen, and what is the correct remedy?

- A. One directory is failing; `usableBytes` dropping is how a dying disk reports itself. Remove `/data/1` from `log.dirs` and restart the broker.
- B. Kafka rebalances directories in the background every `leader.imbalance.check.interval.seconds`; the imbalance will clear itself once `auto.leader.rebalance.enable` next runs.
- C. New partitions are assigned to the directory holding the **fewest partitions** — the count, never the free space — and a partition lives entirely in one directory. A few very large partitions therefore skew bytes even when counts are even. Move specific replicas between directories with `kafka-reassign-partitions.sh` using a plan that includes the `log_dirs` field.
- D. Replace the JBOD layout with RAID-10 so the controller can spread bytes evenly across spindles.

### Question 16 — `[OBS · Consumer lag metrics · Single]`

`enrichment` consumes a topic with `retention.ms=21600000`. Over one hour its client metrics move like this:

```
records-lag-max   : 48,900  →  51,200   (roughly flat)
records-lead-min  : 2,140,000 → 4,100   (falling fast)
```

What is happening, and what is the cheapest first action?

- A. Nothing is wrong: lag is flat, so the consumer is keeping up and `records-lead-min` only reports fetch-buffer occupancy.
- B. Increase the topic's partition count so more consumer instances can share the load.
- C. Reset the group to `latest` so it stops chasing data it will never catch.
- D. `records-lead-min` is the distance between the consumer's position and the **log start offset**. It is approaching zero, so retention is about to delete records the group has not read — data loss is imminent even though lag looks stable. Buy time by raising `retention.ms` on the topic (dynamic and reversible), then fix consumer throughput.

### Question 17 — `[FUND · Producer defaults after 4.0 · Single]`

A service was rebuilt against the 4.3 client libraries with no code or configuration change. Afterwards, on a low-rate topic, median end-to-end latency rose by about 5 ms, average batch size grew, and request rate to the brokers fell. Throughput is unchanged or slightly better.

What changed, and what is the minimal correction if latency matters more than batching?

- A. `linger.ms` changed from **0** to **5** in Kafka 4.0, so the producer now waits up to 5 ms to fill a batch. Set `linger.ms=0` explicitly on this client.
- B. `acks` changed from `1` to `all` in Kafka 4.0, so every write now waits for the followers; set `acks=1` for this service.
- C. `batch.size` was raised from 16,384 to 65,536 in 4.0; set it back on this client.
- D. The brokers now flush to disk on every append because `log.flush.interval.messages` changed; set it back to its 3.x value.

### Question 18 — `[CONNECT · Failed task recovery · Single]`

```
$ curl -s localhost:8083/connectors/pg-sink/status
{"name":"pg-sink",
 "connector":{"state":"RUNNING","worker_id":"connect-2:8083"},
 "tasks":[{"id":0,"state":"RUNNING","worker_id":"connect-2:8083"},
          {"id":1,"state":"FAILED","worker_id":"connect-3:8083",
           "trace":"org.apache.kafka.connect.errors.ConnectException: Exiting WorkerSinkTask due to unrecoverable exception.\n\tat ..."}],
 "type":"sink"}
```

The underlying database problem has been fixed. Records are still only flowing through task 0, and no rebalance has occurred. What is the correct next action?

- A. Wait: the herder restarts failed tasks automatically once `scheduled.rebalance.max.delay.ms` elapses.
- B. `POST /connectors/pg-sink/restart?includeTasks=true&onlyFailed=true`. A FAILED task is never restarted on its own and does not trigger a rebalance, and a plain `POST /restart` restarts only the connector object, leaving task 1 FAILED.
- C. Restart the `connect-3` worker process so its tasks are redistributed and re-created.
- D. `DELETE /connectors/pg-sink` and re-create it from the saved configuration, which is the only way to clear a FAILED task state.

### Question 19 — `[CFG · Configuration precedence · Ordering]`

Rank these four configuration sources from the one that **wins** to the one that loses. (Kafka's built-in `DEFAULT_CONFIG` is always last and is not listed.)

| # | Source |
|---|---|
| 1 | `DYNAMIC_DEFAULT_BROKER_CONFIG` — set with `kafka-configs.sh --entity-type brokers --entity-default` |
| 2 | `STATIC_BROKER_CONFIG` — the value present in `server.properties` when the node started |
| 3 | `DYNAMIC_TOPIC_CONFIG` — an override set on the topic itself |
| 4 | `DYNAMIC_BROKER_CONFIG` — set with `kafka-configs.sh --entity-type brokers --entity-name <id>` |

- A. 4 → 3 → 1 → 2
- B. 3 → 1 → 4 → 2
- C. 3 → 4 → 1 → 2
- D. 2 → 3 → 4 → 1

### Question 20 — `[SEC · Authorizer class · Single]`

A cluster is rebuilt on 4.3 reusing the security block of an old 3.6 `server.properties`. Every node refuses to start:

```
[2026-09-11 04:02:19,551] ERROR Exiting Kafka due to fatal exception (kafka.Kafka$)
org.apache.kafka.common.config.ConfigException: Invalid value kafka.security.authorizer.AclAuthorizer
for configuration authorizer.class.name: Class kafka.security.authorizer.AclAuthorizer could not be found.
```

What is the correct fix?

- A. Add the `zookeeper.connect` property back; `AclAuthorizer` cannot initialise without a metadata store and fails class loading as a side effect.
- B. Copy `kafka-security_2.13.jar` into `libs/`; the class was moved to an optional package in 4.0.
- C. Set `authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer` on **every broker and every controller**. `AclAuthorizer` stored ACLs in ZooKeeper znodes and was removed from the binary with ZooKeeper in 4.0; `StandardAuthorizer` keeps ACLs in `__cluster_metadata`.
- D. Set `authorizer.class.name=kafka.security.authorizer.StandardAuthorizer` — only the class name changed, the package is unchanged.

### Question 21 — `[ARCH · Controller quorum sizing · Multi — Choose 2]`

A 12-broker cluster is being re-architected onto dedicated controller nodes. The requirement is to survive the simultaneous loss of **two** controllers. Which **two** statements are correct?

- A. Five controllers are needed: a quorum of 2N+1 voters tolerates N concurrent failures, so 3 tolerates 1 and 5 tolerates 2.
- B. Controllers must be sized like brokers — roughly 6 GB heap and large disks — because each one holds a replica of every partition's data.
- C. A fourth controller would tolerate exactly the same number of failures as three, so an even quorum size only adds cost.
- D. All twelve brokers must also be listed as voters so they can stand for election if every controller is lost.
- E. Adding controllers raises metadata write throughput, because metadata records are sharded across the voters.

### Question 22 — `[TROUBLE · Moving partitions off a full disk · Ordering]`

Broker 5 is at 92% disk. Two empty brokers, 7 and 8, have just joined and are receiving nothing. Put the steps of a throttled rescue in order.

| # | Step |
|---|---|
| 1 | `kafka-reassign-partitions.sh --execute --reassignment-json-file plan.json --throttle 52428800` |
| 2 | Confirm with `kafka-log-dirs.sh --describe` that broker 5 has recovered space and that `UnderReplicatedPartitions` is back to 0 |
| 3 | `kafka-reassign-partitions.sh --generate --topics-to-move-json-file topics.json --broker-list "7,8"`, saving both the current assignment (for rollback) and the proposed one |
| 4 | Re-run `kafka-reassign-partitions.sh --verify --reassignment-json-file plan.json` until every partition reports completed — this is also what removes the replication throttle |

- A. 1 → 3 → 4 → 2
- B. 3 → 1 → 4 → 2
- C. 3 → 1 → 2 → 4
- D. 3 → 4 → 1 → 2

### Question 23 — `[CFG · Tiered storage · Single]`

Compliance requires 400 days of `payments-audit`; broker disks hold about ten days of it. An engineer enabled `remote.log.storage.system.enable=true` on the brokers, `remote.storage.enable=true` on the topic, and set `retention.ms=34560000000`. Two weeks later the broker disks are full again and remote storage holds a copy of everything.

Why is local disk not shrinking?

- A. Tiered storage only uploads segments; local deletion requires `remote.log.copy.disable=true`, which is what actually frees the disk.
- B. `retention.ms` above 30 days is silently clamped, so the local log keeps growing until the cluster default of seven days finally applies.
- C. Tiered storage does not support a replication factor above 1, so the follower replicas are keeping full local copies.
- D. `local.retention.ms` was never set. Its default is **-2**, which means *inherit `retention.ms`* — not "unlimited" and not "a few hours". With that default the brokers keep all 400 days locally as well. Set `local.retention.ms` to a few hours or days and the disk drains.

### Question 24 — `[FUND · Leader election order · Ordering]`

On a 4.3 cluster with `eligible.leader.replicas.version=1` finalized, a partition's leader has just failed. Put the controller's leader-selection rules in the order it applies them.

| # | Rule |
|---|---|
| 1 | Pick the last known leader, if it is unfenced |
| 2 | Pick a replica from the ISR |
| 3 | Leave the partition without a leader and let `OfflinePartitionsCount` rise |
| 4 | Pick an unfenced replica from the Eligible Leader Replicas set |

- A. 4 → 2 → 1 → 3
- B. 2 → 1 → 4 → 3
- C. 2 → 4 → 3 → 1
- D. 2 → 4 → 1 → 3

### Question 25 — `[OBS · Controller metric · Single]`

A dashboard panel that sums `ActiveControllerCount` across every scraped node has been reading **0** ever since the cluster was rebuilt with dedicated controller nodes. Topic creation works, producers and consumers are fine, and nobody has reported an incident.

What is the correct interpretation and first step?

- A. A sum of 0 has two plausible causes: there really is no active controller right now, or — far more likely given that administration works — the JMX exporter is simply not attached to the controller nodes, so the metric is never scraped. Run `kafka-metadata-quorum.sh --bootstrap-controller controller-1:9093 describe --status` and look at `LeaderId` to tell the two apart.
- B. With dedicated controllers the sum should equal the number of controllers, so 0 means the quorum has no voters configured.
- C. `ActiveControllerCount` was a ZooKeeper-era metric; in KRaft it was replaced by the `kafka.controller:type=ControllerStats` MBean and a sum of 0 is expected.
- D. A sum of 0 always means split brain — two controllers each fenced the other — and the quorum must be re-formatted.

### Question 26 — `[CFG · Compaction and tombstones · Single]`

`user-profile` is a compacted topic that a downstream cache rebuilds from offset 0 on every cold start. The rebuild takes about three days on a large deployment. Operators notice that after a slow rebuild, users deleted weeks ago reappear in the cache; after a fast rebuild they do not.

What is the cause, and what is the cheapest fix?

- A. The cache is reading the head of the log, which is never compacted; pin it to the tail with `isolation.level=read_committed`.
- B. Tombstones — records with a `null` value — are themselves removed `delete.retention.ms` after they have been compacted, and that default is **86,400,000 ms (24 h)**. A rebuild slower than that window misses the delete markers entirely. Raise `delete.retention.ms` on the topic to comfortably exceed the worst-case rebuild; it is a dynamic topic override.
- C. `min.cleanable.dirty.ratio` of 0.5 lets half the log stay dirty, so half the deletions are never applied; lower it to 0.1.
- D. Add `delete` to the cleanup policy (`cleanup.policy=compact,delete`) so that deleted keys age out of the log entirely.

### Question 27 — `[SEC · Super users · Multi — Choose 2]`

A cluster has `super.users=User:ops-admin;User:mirror-maker`. After an audit finding, an operator adds a Deny ACL for `User:ops-admin` on topic `pii-events` and verifies with `kafka-acls.sh --list` that it is present. `ops-admin` can still consume the topic. Which **two** statements are correct?

- A. Deny always beats Allow, so the rule must simply not have propagated yet; retrying in a few seconds will show it taking effect.
- B. A super user bypasses the authorizer entirely, including Deny rules — no ACL of any kind can constrain a principal listed in `super.users`.
- C. Entries in `super.users` are separated by commas; the semicolons mean the whole string was parsed as one principal name and neither account is actually privileged.
- D. The only way to make the Deny effective is to remove `User:ops-admin` from `super.users` on every broker and controller.
- E. `super.users` supports wildcards, so `User:ops-*` would have scoped the privilege more safely.

### Question 28 — `[CONNECT · Client config overrides · Single]`

A reviewer rejects a connector configuration containing `consumer.override.sasl.jaas.config=...`, citing the Confluent *Connect Security* page which states that client overrides are disabled by default. On the team's Apache Kafka 4.3 cluster the override demonstrably works.

Which statement is correct for Apache Kafka 4.3?

- A. The override works only because the worker runs in standalone mode; distributed workers enforce the policy.
- B. Only `producer.override.*` is honoured by default; the `consumer.override.*` prefix requires an explicit policy change.
- C. `connector.client.config.override.policy` defaults to **`All`** in Apache Kafka — it was changed from `None` in 3.0 by KIP-722, and the Confluent page still prints the old value. Restricting it means setting `Allowlist` (recommended since 4.2, and the default from 5.0), `Principal`, or `None`.
- D. The policy is evaluated only for connectors created after the worker starts, so an override in an existing connector is grandfathered in.

### Question 29 — `[FUND · Internal topic replication · Single]`

A brand-new two-broker staging cluster is built from stock 4.3 configuration. The first application to start a consumer group fails:

```
org.apache.kafka.common.errors.GroupCoordinatorNotAvailableException: The group coordinator is not available.
```

and on the broker:

```
[2026-09-15 11:07:32,448] ERROR [KafkaApi-2] Number of alive brokers '2' does not meet the required
replication factor '3' for the offsets topic (configured via 'offsets.topic.replication.factor').
This error can be ignored if the cluster is starting up and not all brokers are up yet.
```

What is the cause and the correct fix for this staging cluster?

- A. `default.replication.factor` is 3 by default; lower it to 2 and the offsets topic will be created.
- B. `min.insync.replicas` is 3 on this cluster, which blocks creation of `__consumer_offsets`; set it to 1.
- C. The group coordinator is elected through the controller quorum, so a two-node cluster cannot host one; add a third node.
- D. `offsets.topic.replication.factor` defaults to **3**, so `__consumer_offsets` cannot be created on two brokers. Set it to 2 (or add a broker). Note that the setting is consulted **only at creation time** — once the topic exists, changing it does nothing, and the replication factor must then be raised with `kafka-reassign-partitions.sh`.

### Question 30 — `[TROUBLE · Configuration validation in 4.3 · Single]`

An integration-test harness that has run unchanged for two years fails after the cluster is upgraded to 4.3:

```
$ kafka-topics.sh --bootstrap-server broker-1:9092 --create --topic roll-test \
    --partitions 1 --replication-factor 1 --config segment.bytes=1024
Error while executing topic command : Invalid value 1024 for configuration segment.bytes:
Value must be at least 1048576
```

What changed, and what should the harness do instead?

- A. Kafka 4.3 raised the minimum allowed `segment.bytes` from 14 bytes to **1 MiB**. A test that wants frequent segment rolls should drive them with `segment.ms` (or `segment.jitter.ms`) instead of a tiny segment size.
- B. The log directory has been cordoned by KIP-1066, and cordoned directories reject non-default topic configurations.
- C. `segment.bytes` may not be smaller than `message.max.bytes` (1,048,588), which is the constraint being reported.
- D. Tiered storage requires a minimum segment size of 1 MiB, and `remote.log.storage.system.enable` is now on by default in 4.3.

### Question 31 — `[ARCH · Follower fetching · Single]`

A cluster spans three availability zones. The finance team reports a large cross-zone data-transfer bill driven by consumers reading from leaders that happen to sit in other zones. The requirement is to cut the cross-zone read traffic without weakening any delivery guarantee.

What is the correct configuration?

- A. Set `client.rack` on every consumer. Kafka then routes fetches to a local replica automatically, because the broker derives rack topology from the client's advertised address.
- B. Set `broker.rack` on every broker (a read-only setting, so it needs a restart), set `replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector` on the brokers, and set `client.rack` on the consumers. Followers only serve reads up to the high watermark, so no consumer can see uncommitted data; producers still write to the leader.
- C. Create one Cluster Link per availability zone so each zone gets a local read-only mirror of every topic.
- D. Enable `unclean.leader.election.enable` so the controller can elect a leader in the zone with the most consumers.

### Question 32 — `[CFG · acks, min.insync.replicas and RF · Multi — Choose 2]`

During a single broker restart an operator watches `UnderReplicatedPartitions` climb to 40 and stay there for four minutes, while every producer keeps writing without a single error. The affected topics have `replication.factor=3` and `min.insync.replicas=2`, and their producers use `acks=all` with the 4.3 defaults. Which **two** statements explain why the writes were never interrupted?

- A. A write is acknowledged once the leader plus one follower hold it — two in-sync replicas in total, not all three.
- B. The partition can lose one replica and still accept `acks=all` writes.
- C. `min.insync.replicas` is also enforced for producers using `acks=1`, which is why lowering it is a valid emergency lever for any producer.
- D. If the ISR drops to one, the leader returns a fatal error and the producer discards the batch immediately.
- E. `acks=all` guarantees the record survives the simultaneous loss of all three brokers hosting the partition.

### Question 33 — `[SEC · Certificate rotation · Single]`

Every broker certificate is signed by a CA that expires in three weeks. A new CA has been created. The listeners already exist and are in use, and no downtime is acceptable.

What is the correct procedure?

- A. Swap each broker's keystore to the new certificate first with `kafka-configs.sh --entity-type brokers --entity-name <id>`, then add the new CA to the truststores once all brokers present the new chain.
- B. Certificates can only be changed at startup; add the new CA to the truststore files on disk and perform a rolling restart, then repeat the roll for the keystores.
- C. Add the new CA to every broker's **truststore** first, then swap the keystores — both as per-broker dynamic configuration (`listener.name.<name>.ssl.truststore.location`, then `...ssl.keystore.location`), with no restart. For the inter-broker listener Kafka validates each change: a new truststore must still trust the current keystore, and a new keystore must be trusted by the current truststore, so the reverse order is rejected or breaks replication.
- D. Update the `/config/brokers/<id>` znode with the new store locations; the brokers pick the change up through their ZooKeeper watch without a restart.

### Question 34 — `[OBS · Reading replication metrics · Multi — Choose 2]`

During a broker outage the cluster reports:

```
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions   = 214
kafka.controller:type=KafkaController,name=OfflinePartitionsCount = 0
kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount   = 0
```

Which **two** readings of this combination are correct?

- A. The combination is impossible: `UnderReplicatedPartitions > 0` always implies `UnderMinIsrPartitionCount > 0`.
- B. `UnderMinIsrPartitionCount = 0` means replication has already caught up and the 214 figure is stale.
- C. Every affected partition still has a leader, so consumers and producers are still being served.
- D. The correct immediate response is to enable `unclean.leader.election.enable` so the missing replicas can be replaced from outside the ISR.
- E. Producers using `acks=all` are still being accepted, because no partition has fallen below its `min.insync.replicas`.

### Question 35 — `[FUND · The metadata log · Multi — Choose 2]`

A 4.3 cluster runs three dedicated controllers and nine brokers. Which **two** statements about `__cluster_metadata` are correct?

- A. It has exactly **one** partition and is replicated by Raft among the controller voters.
- B. It is an ordinary replicated topic whose replication factor comes from `offsets.topic.replication.factor`.
- C. Each node stores its copy in the directory named by `metadata.log.dir`, which defaults to `/tmp/kraft-metadata`.
- D. Brokers replicate it as **observers**: they fetch and apply the log but never vote and can never be elected controller.
- E. It is trimmed by the log cleaner according to `min.cleanable.dirty.ratio`, exactly like any other compacted topic.

### Question 36 — `[CONNECT · Worker group timing · Multi — Choose 2]`

A distributed Connect worker is killed. Its six tasks stay unassigned for about five minutes, then appear on the surviving workers. Which **two** statements explain this correctly?

- A. The gap is the Connect worker group's `session.timeout.ms`, which defaults to 45,000 ms exactly as it does for a consumer.
- B. `scheduled.rebalance.max.delay.ms` defaults to **300,000 ms**: the leader deliberately holds a departed worker's tasks unassigned for up to five minutes so that a quick restart does not cost two rebalances.
- C. Lowering `scheduled.rebalance.max.delay.ms` shortens the gap, at the cost of more rebalances whenever a worker merely restarts.
- D. Connect uses eager rebalancing by default, which is why every task in the cluster stops during the gap.
- E. Restarting the remaining workers is the supported way to force an immediate reassignment.

### Question 37 — `[CFG · Startup recovery · Single]`

After a power loss, a broker with eight data directories and 32 cores takes 70 minutes to come back, logging log-recovery progress the whole time. An engineer recalls that "the recovery thread default is one per data directory" and proposes editing `server.properties`.

What is accurate on 4.3, and what is the cheapest change?

- A. `num.recovery.threads.per.data.dir` is read-only, so the only option is to edit `server.properties` and restart — which is acceptable since the broker is down anyway.
- B. Recovery speed is governed by `num.io.threads` (default 8); raise it and recovery parallelises across directories.
- C. Recovery uses the `background.threads` pool (default 10), which is shared with other housekeeping; raise it to 32.
- D. The default changed from 1 to **2** in Kafka 4.0, so the recalled figure is out of date. `num.recovery.threads.per.data.dir` is a cluster-wide **dynamic** config, so it can be raised with `kafka-configs.sh` without touching files — but it only affects the **next** startup, so set it now for the whole cluster.

### Question 38 — `[TROUBLE · Adding a controller · Single]`

A failed controller node was replaced. The new node, 3004, starts cleanly and its logs show it fetching metadata, but administration still reports a three-voter quorum:

```
$ kafka-metadata-quorum.sh --bootstrap-controller controller-1:9093 describe --status
ClusterId:              M8s2Xr1rTZauRoYUbCLSfw
LeaderId:               3001
LeaderEpoch:            42
HighWatermark:          918342
MaxFollowerLag:         0
MaxFollowerLagTimeMs:   0
CurrentVoters:          [3001,3002,3003]
CurrentObservers:       [1,2,3,4,5,6,3004]
```

The cluster runs `kraft.version=1`. Why is 3004 an observer, and what is the fix with the fewest changes?

- A. `controller.quorum.auto.join.enable` defaults to **false** in 4.3, so a new controller deliberately joins as an observer until an operator promotes it. Run `kafka-metadata-quorum.sh --bootstrap-controller controller-1:9093 add-controller` on the new node once it has caught up (its lag is already 0).
- B. The node must be added to `controller.quorum.voters` on every broker and controller, followed by a full cluster restart.
- C. The replacement has not registered its ephemeral node yet; restart it so it re-registers and the controller promotes it.
- D. `controller.quorum.fetch.timeout.ms` (2,000 ms) is too low for the new node to be counted; raise it and the node is promoted on the next election.

### Question 39 — `[SEC · Default authorization behaviour · Single]`

A cluster runs `StandardAuthorizer` with `allow.everyone.if.no.acl.found=true`, inherited from an older deployment. A team adds one ACL — Allow `User:reader` Read on topic `orders` — and immediately every other principal loses access to `orders`, while still writing freely to the fifty topics that have no ACLs at all.

Which explanation is correct?

- A. The new ACL implicitly created a Deny for all other principals, which is why they lost access; adding an explicit Allow for each of them restores service.
- B. `allow.everyone.if.no.acl.found` relaxes access **only for resources that have no ACL whatsoever**. The moment `orders` gained one ACL it returned to normal deny-by-default, while untouched topics stayed open. The safe posture is to set the flag to `false` and grant explicit ACLs everywhere.
- C. The flag only applies to `Cluster` resources, so it never affected topics; the fifty open topics are open because of `super.users`.
- D. ACL evaluation is eventually consistent, so the other principals will regain access as soon as every broker has applied the record.

### Question 40 — `[ARCH · Rack awareness · Single]`

Nine brokers are split across two availability zones — five in AZ-a and four in AZ-b — with `broker.rack` set correctly. All topics use `replication.factor=3` and `min.insync.replicas=2`.

What does Kafka actually guarantee here, and what is the residual risk?

- A. With RF=3 and two racks, Kafka places exactly one replica per rack and spreads the third evenly, so losing either AZ always leaves two in-sync replicas.
- B. `broker.rack` is a dynamic per-broker configuration, so replicas are re-spread automatically whenever a rack label changes.
- C. Kafka spreads a partition's replicas over `min(#racks, replication.factor)` racks — here **two** — so each partition has at least one replica in each AZ, but many will have two in one AZ and one in the other. Losing the AZ holding two replicas leaves a single replica, below `min.insync.replicas=2`, and those partitions stop accepting `acks=all` writes. Three zones, or a min.isr plan that accepts this, is the real answer.
- D. Rack awareness only influences leader election, not replica placement, so the AZ split has no effect on durability.

### Question 41 — `[CFG · Cleanup policy behaviour · Matching]`

Match each topic setting to the behaviour it produces.

| # | Setting |
|---|---|
| 1 | `cleanup.policy=delete` with `retention.ms=604800000` |
| 2 | `cleanup.policy=compact` |
| 3 | `cleanup.policy=compact,delete` |
| 4 | A record with a `null` value on a compacted topic |

| Letter | Behaviour |
|---|---|
| W | Keeps at least the latest value for every key indefinitely; whole segments are never dropped just because they are old |
| X | Marks the key as deleted, and the marker itself is removed `delete.retention.ms` after it has been compacted |
| Y | Closed segments are discarded once they are older than the retention window; the active segment is never touched |
| Z | Keeps the latest value per key **and** still drops whole segments once they age out of the retention window |

- A. 1-Y · 2-W · 3-Z · 4-X
- B. 1-W · 2-Y · 3-Z · 4-X
- C. 1-Y · 2-Z · 3-W · 4-X
- D. 1-Z · 2-W · 3-Y · 4-X

### Question 42 — `[OBS · Unclean leader elections · Single]`

A monthly review of `kafka.controller:type=ControllerStats,name=UncleanLeaderElectionsPerSec` shows seven counted events in the last thirty days. Nobody on the team remembers enabling anything, and there were no reported outages.

What does this mean and what should be done?

- A. The metric counts preferred leader elections triggered by `auto.leader.rebalance.enable`, which is on by default; seven a month on a busy cluster is normal.
- B. It counts leader elections served from the Eligible Leader Replicas set, which is exactly the mechanism working as designed.
- C. In KRaft the counter is incremented whenever the controller fails over, so seven events means seven controller elections.
- D. The documented target for this metric is **0**. A non-zero count means `unclean.leader.election.enable=true` is set somewhere — as a cluster-wide default or a topic override — and the cluster has silently accepted data loss seven times. Audit both levels with `kafka-configs.sh --describe --all`; the setting is dynamic, so it can be put back to `false` without a restart.

### Question 43 — `[TROUBLE · ISR instability · Multi — Choose 2]`

One broker in a nine-broker cluster shows `IsrShrinksPerSec` and `IsrExpandsPerSec` oscillating every few minutes. No broker has restarted, `UnderReplicatedPartitions` briefly rises and falls, and `OfflinePartitionsCount` stays 0. Which **two** are the right first moves?

- A. Inspect that broker's GC pause log and disk write latency. `replica.lag.time.max.ms` (30,000 ms) is only exceeded when a follower genuinely stalls, so the cause is a stall, not the threshold.
- B. Raise `replica.lag.time.max.ms` to 120,000 ms so the follower stops being evicted from the ISR.
- C. Enable `unclean.leader.election.enable` so leadership can move away from the unstable replica.
- D. Verify that `replica.fetch.wait.max.ms` (500 ms) is still well below `replica.lag.time.max.ms`; on very low-throughput topics an inverted relationship between the two makes the ISR churn constantly.
- E. Increase the partition count of the affected topics so replication work is spread more thinly.

### Question 44 — `[CFG · Replica fetch sizing · Multi — Choose 2]`

A topic will carry 4 MiB record batches, and `max.message.bytes` has been raised to 8 MiB on it. A reviewer objects that "replication will break, because the replica fetch response is capped at 1 MiB". Which **two** statements are correct on 4.3?

- A. The reviewer is right: `replica.fetch.response.max.bytes` defaults to 1,048,576 and must be raised to at least 8 MiB.
- B. `replica.fetch.response.max.bytes` defaults to **10,485,760 (10 MiB)**, not 1 MiB — third-party study material prints the wrong figure often enough that it is worth memorising.
- C. Neither `replica.fetch.max.bytes` (1 MiB, per partition) nor `replica.fetch.response.max.bytes` is an absolute maximum: if the first record batch of the first non-empty partition is larger, it is returned anyway so replication can make progress.
- D. Both settings are cluster-wide dynamic configurations and can be raised without a restart.
- E. `socket.request.max.bytes` defaults to 1 MiB and caps the whole fetch response, so it must be raised too.

### Question 45 — `[CONNECT · Dead letter queues · Multi — Choose 3]`

A malformed record vanished from an Elasticsearch index without any task failing, and nobody noticed for three days. The pipeline has one source connector polling a REST API and one sink connector writing to Elasticsearch, and operations now want bad records quarantined rather than dropped. Which **three** statements are correct?

- A. The dead letter queue is a **sink-only** feature; `errors.deadletterqueue.topic.name` on a source connector has no effect.
- B. With `errors.tolerance=all` and no DLQ topic configured, a sink connector discards bad records silently — the failure mode operations usually discover far too late.
- C. `errors.deadletterqueue.topic.replication.factor` defaults to **3**, so on a single-broker development cluster it must be lowered or the DLQ topic cannot be created.
- D. The DLQ captures only converter and deserialization failures; failures raised inside an SMT bypass it.
- E. `errors.tolerance=none` routes failing records to the DLQ while keeping the task running.

### Question 46 — `[FUND · KRaft feature levels · Single]`

An operator wants to add a fourth controller to a running cluster without restarting every node, and checks the feature levels first:

```
$ kafka-features.sh --bootstrap-controller controller-1:9093 describe
Feature: eligible.leader.replicas.version  SupportedMinVersion: 0  SupportedMaxVersion: 1  FinalizedVersionLevel: 1
Feature: kraft.version                     SupportedMinVersion: 0  SupportedMaxVersion: 1  FinalizedVersionLevel: 0
(other features omitted)
```

What does this tell them?

- A. `kraft.version` is finalized at **0**, which means a **static** quorum: membership comes from `controller.quorum.voters`, listed identically on every node, and changing it means editing the configuration everywhere and restarting. Dynamic membership needs the feature upgraded to `kraft.version=1` (KIP-853), after which `controller.quorum.bootstrap.servers` and `add-controller` / `remove-controller` become available.
- B. `kraft.version=0` simply means the feature has never been queried; controllers can always be added dynamically in 4.x.
- C. Eligible Leader Replicas must be disabled before any quorum membership change, so `eligible.leader.replicas.version` has to go back to 0 first.
- D. Quorum membership is governed by `metadata.version`, not `kraft.version`; finalize the latest `metadata.version` and the new controller joins automatically.

### Question 47 — `[SEC · Credential revocation · Multi — Choose 2]`

A SCRAM credential leaks. Operations delete the user:

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --alter \
    --delete-config 'SCRAM-SHA-512' --entity-type users --entity-name svc-partner
Completed updating config for user svc-partner.
```

Twenty minutes later the compromised client is still producing. Which **two** statements are correct?

- A. Deleting a SCRAM credential only takes effect after a rolling restart of the brokers, which is why the client is still connected.
- B. The credential is also stored in `kafka_server_jaas.conf` on each broker and must be removed there as well.
- C. `connections.max.reauth.ms` defaults to **0**, which disables SASL re-authentication entirely: an already-authenticated connection is never re-checked, so revoking the credential does not close it.
- D. Adding a Deny ACL for the principal would likewise have no effect on the open connection, because authorization is evaluated only at connection time.
- E. Setting `connections.max.reauth.ms` on the listener — 3,600,000 for example — forces clients to re-authenticate periodically, which is what makes a revocation actually bite.

### Question 48 — `[ARCH · Replication mechanisms · Matching]`

Match each mechanism to the characteristic that distinguishes it.

| # | Mechanism |
|---|---|
| 1 | MirrorMaker 2 with the default `DefaultReplicationPolicy` |
| 2 | Cluster Linking on Confluent Server |
| 3 | One cluster stretched across three availability zones with `broker.rack` |
| 4 | `MirrorCheckpointConnector` |

| Letter | Characteristic |
|---|---|
| W | Topics land on the target renamed `{source}.{topic}`, and consumer offsets do not line up, so they must be translated |
| X | Writes translated offset pairs into `{source}.checkpoints.internal` so a failed-over consumer can find its position |
| Y | Offsets are identical on both sides byte for byte, mirror topics are read-only until the link is promoted, and no Connect cluster is involved |
| Z | Replication is synchronous within one cluster: RPO is zero for `acks=all` writes, paid for with inter-AZ latency on every produce |

- A. 1-Y · 2-W · 3-Z · 4-X
- B. 1-W · 2-Y · 3-X · 4-Z
- C. 1-W · 2-Y · 3-Z · 4-X
- D. 1-X · 2-Y · 3-Z · 4-W

### Question 49 — `[FUND · Metadata log placement · Single]`

Broker nodes are configured with `log.dirs=/data/1,/data/2,/data/3` and no `metadata.log.dir`. `/data/1` is an older, smaller and slower device that was kept only to avoid wasting a bay.

What is the consequence?

- A. Nothing: the metadata log is replicated across all three directories, so the slow device is used only as one of three copies.
- B. `metadata.log.dir` defaults to `null`, which means the **first entry of `log.dirs`** — so every node's metadata log sits on the slow `/data/1`. Metadata writes then run at the speed of the worst disk, and a failure of `/data/1` costs the node its metadata log, which is far worse than losing an ordinary data directory. Point `metadata.log.dir` at a dedicated, fast, reliable device.
- C. `metadata.log.dir` defaults to the **last** entry of `log.dirs`, so `/data/3` is used and the slow disk only holds partition data.
- D. Brokers do not keep a metadata log at all; only controllers do, so `log.dirs` ordering is irrelevant on a broker-only node.

### Question 50 — `[TROUBLE · Timestamp validation · Single]`

An IoT ingestion topic worked for years. Days after the cluster moved from 3.9 to 4.3, a minority of devices start being rejected:

```
org.apache.kafka.common.errors.InvalidTimestampException: One or more records have been rejected
due to an invalid timestamp
```

Investigation shows the failing devices have clocks running several hours **ahead** of real time. Nothing on the topic was changed.

What happened, and what is the targeted, reversible fix while the fleet's clocks are corrected?

- A. `log.message.timestamp.type` now defaults to `LogAppendTime`, so client-supplied timestamps are rejected outright; set it back to `CreateTime`.
- B. `message.timestamp.before.max.ms` was introduced in 4.0 with a one-hour default, and it is what rejects skewed clocks.
- C. `message.timestamp.after.max.ms` changed from `Long.MAX_VALUE` to **one hour** in Kafka 4.0, so records dated more than an hour in the future are now rejected. Raise `message.timestamp.after.max.ms` on this topic to cover the observed skew — a topic-level override that can be reverted once the clocks are fixed. Switching the topic to `message.timestamp.type=LogAppendTime` is the other option, but it discards the producer's own timestamps.
- D. Retention now evaluates record timestamps rather than segment timestamps, so future-dated records are rejected to protect the retention calculation; raise `retention.ms`.

### Question 51 — `[OBS · Metric names across versions · Single]`

Straight after a 3.9 → 4.3 upgrade, one row of a Grafana dashboard goes blank. The panels in that row query metrics that the JMX exporter used to publish from `org.apache.kafka.server:type=AssignmentsManager`. The brokers are healthy, other rows are fine, and an on-call engineer is about to declare a broker-side incident.

What is the explanation?

- A. Remote JMX is disabled by default and must be re-enabled with `JMX_PORT` after every upgrade.
- B. The metric now requires `metrics.recording.level=DEBUG`, which was reset to `INFO` by the upgrade.
- C. The metrics were removed in 4.0 along with ZooKeeper, since assignment bookkeeping moved into the controller.
- D. KIP-1100 (Kafka 4.2) standardised MBean names onto the `kafka.COMPONENT:type=...` form, so `org.apache.kafka.server:type=AssignmentsManager` became `kafka.server:type=AssignmentsManager`. Exporter patterns and dashboards must be updated. The real hazard is that a renamed metric produces a **silent** observability gap that reads exactly like an outage.

### Question 52 — `[CONNECT · Resetting a connector's offsets · Single]`

A sink connector must reprocess its source topic from the beginning. The connector name, its configuration and its DLQ must all be preserved.

What is the correct sequence on Apache Kafka 4.3?

- A. `PUT /connectors/es-sink/stop`, then `DELETE /connectors/es-sink/offsets`, then `PUT /connectors/es-sink/resume`. The offsets endpoints accept `PATCH` and `DELETE` **only** while the connector is `STOPPED`; pausing is not enough, because paused tasks still exist and still own their offsets.
- B. `PUT /connectors/es-sink/pause`, then `DELETE /connectors/es-sink/offsets`, then `PUT /connectors/es-sink/resume`.
- C. Run `kafka-consumer-groups.sh --reset-offsets --to-earliest --group connect-es-sink --execute` while the connector keeps running, so there is no interruption.
- D. `DELETE /connectors/es-sink` and re-create it under a new name, which is the only supported way to make a sink re-read a topic.

### Question 53 — `[FUND · Log compaction guarantees · Multi — Choose 2]`

A service rebuilding state from a compacted topic finds two different values for the same key, a few thousand offsets apart near the end of the log. An engineer opens a bug report claiming the log cleaner is broken. Which **two** properties does log compaction actually guarantee?

- A. After the cleaner has run, each key appears exactly once in the log.
- B. The offset of a message never changes; it stays the permanent identifier of that position in the log.
- C. Compaction groups all records sharing a key together so that a key's history is contiguous on disk.
- D. A consumer reading from the start of the log sees at least the final state of every record, in the order the records were written.
- E. The active segment is compacted as soon as `min.cleanable.dirty.ratio` is exceeded.

### Question 54 — `[SEC · TLS hostname verification · Single]`

A newly onboarded application cannot connect:

```
javax.net.ssl.SSLHandshakeException: No subject alternative DNS name matching
broker-3.kafka.internal found.
```

The broker certificate has `CN=broker-3.kafka.internal` and no SAN extension. Older applications connect fine. A 3.x-era runbook says "set `ssl.endpoint.identification.algorithm=https` on the client".

What is the correct assessment?

- A. The older applications work because they were issued client certificates by the same CA; re-issuing a client certificate for the new application resolves it.
- B. Hostname verification has been **on by default since Kafka 2.0** (`ssl.endpoint.identification.algorithm=https`), so the runbook step is a no-op. The real fix is to re-issue the broker certificates with SAN entries covering every advertised hostname; the older applications only work because they pin an older configuration that disables verification. Setting the property to an empty string would "fix" it by turning the check off, which is not acceptable.
- C. `ssl.client.auth` must be set to `required` on the listener so the broker presents its full chain including the SAN extension.
- D. The client is missing the CA in its truststore; adding it removes the SAN requirement, because a trusted chain short-circuits hostname verification.

### Question 55 — `[CFG · Topic auto-creation · Single]`

An audit finds a dozen production topics named after typos (`ordres`, `paymnets`), each with one partition and one replica. Applications created them by producing to them.

Which statement correctly explains the shape of those topics and the right remedy?

- A. Auto-created topics inherit `offsets.topic.replication.factor` (3), so the RF=1 topics must have been created by hand.
- B. Setting `delete.topic.enable=false` prevents the junk topics from being created in the first place.
- C. `auto.create.topics.enable` defaults to **true**, and an auto-created topic is shaped by `num.partitions` (default **1**) and `default.replication.factor` (default **1**) — which is exactly why the junk topics are single-replica and cannot survive a broker loss. Turn auto-creation off in production and create topics through a governed process. *(Note: Apache 4.3 lists this setting as read-only while Confluent's reference lists it as cluster-wide, so plan on a rolling restart.)*
- D. Auto-created topics always use `min.insync.replicas=2`, so they are safe; the only problem is the naming, which a `CreateTopicPolicy` on the brokers would have blocked.

### Question 56 — `[TROUBLE · ELR and min.insync.replicas · Single]`

A cluster has finalized `eligible.leader.replicas.version=1`. An operator tries to tune one broker and is refused:

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type brokers --entity-name 3 \
    --alter --add-config min.insync.replicas=2
Error while executing config command with args '--bootstrap-server broker-1:9092 ...'
java.util.concurrent.ExecutionException: org.apache.kafka.common.errors.InvalidConfigurationException: ...
```

What is going on, and what should the operator do?

- A. `min.insync.replicas` has always been topic-only; broker-level values have never existed, and the 3.x runbook that says otherwise was simply wrong.
- B. Enabling ELR made every configuration read-only until the feature is finalized on all nodes; restart broker 3 and retry.
- C. The command must be sent to the active controller with `--bootstrap-controller`, because feature-gated configurations are not accepted by brokers.
- D. When ELR is enabled, **broker-level** `min.insync.replicas` is removed and can no longer be modified. Set it at the **cluster** level (`--entity-type brokers --entity-default`) or per topic. Be aware that any update to the cluster-level value — even rewriting the identical value — **clears all ELR state**, so make the change deliberately rather than as part of a routine sweep.

### Question 57 — `[ARCH · Process roles · Multi — Choose 2]`

Which **two** reasons do the Apache Kafka and Confluent documentation give for separating `process.roles` in production instead of running combined `broker,controller` nodes?

- A. Controllers can be rolled, patched and scaled independently of the brokers.
- B. Combined mode caps a cluster at three brokers.
- C. A dedicated controller is isolated from the broker's page-cache pressure, garbage collection and disk I/O, so metadata handling is not affected by data-plane load.
- D. Combined mode still stores its metadata in ZooKeeper, which is why it is unsupported from 4.0.
- E. Only dedicated controller nodes can run `StandardAuthorizer`, so ACLs are impossible in combined mode.

### Question 58 — `[SEC · Authorizer placement · Single]`

`authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer` is set on all nine brokers, with a full ACL set in place. It was never added to the three controller nodes, which use a separate configuration file.

What is the consequence?

- A. Administrative requests — `CreateTopics`, `AlterConfigs`, ACL changes — are forwarded from a broker to the active controller inside an Envelope request, and the controller authorizes **both** the envelope (by the broker's principal) and the inner request (by the client's principal). With no authorizer configured on the controllers, those forwarded operations are not subject to authorization. Set the property on every controller and restart them.
- B. Nothing: controllers never evaluate ACLs, because all client traffic terminates on brokers.
- C. ACLs would be stored in two different places, so `kafka-acls.sh --list` returns inconsistent results depending on which node answers.
- D. The controllers fall back to `super.users`, so the only principals able to perform administrative operations are the super users — a safe default that needs no change.

### Question 59 — `[ARCH · Rolling upgrade · Single]`

A cluster is being taken from 4.1 to 4.3. The team's upgrade runbook, written in the 2.x era, says: roll the brokers with the new binaries, then set `inter.broker.protocol.version=4.3` in `server.properties` and roll a second time.

What is the correct 4.x procedure?

- A. The runbook is still correct in substance; only the property name changed, to `metadata.version=4.3` in `server.properties`.
- B. `inter.broker.protocol.version` was removed together with ZooKeeper; feature levels are managed with `kafka-features.sh`. Roll one node at a time onto the new binaries, waiting for `UnderReplicatedPartitions` to return to 0 between nodes, and only once **every** node runs 4.3 finalize with `kafka-features.sh --bootstrap-server broker-1:9092 upgrade --release-version 4.3`. Finalizing is one-way here: 4.3 changed metadata, so it cannot be downgraded afterwards.
- C. Finalize the feature level first so the cluster knows what to expect, then roll the nodes onto the new binaries.
- D. `metadata.version` is raised automatically the moment the last node restarts on the new binaries, so no explicit finalize step exists in 4.x.

### Question 60 — `[CONNECT · MirrorMaker 2 setup · Single]`

A dedicated MirrorMaker 2 process starts without error using:

```properties
clusters = primary, dr
primary.bootstrap.servers = primary-1:9092
dr.bootstrap.servers = dr-1:9092
topics = .*
tasks.max = 8
```

No topics appear on `dr` at all, and the MM2 log shows that no source connector was ever started.

What is missing?

- A. `topics = .*` is rejected as too broad; an explicit topic list is required before any connector starts.
- B. `replication.policy.class` must be set to `IdentityReplicationPolicy`, otherwise the source connector refuses to start because it cannot compute target topic names.
- C. Replication flows are **disabled by default**. The configuration must declare the direction explicitly: `primary->dr.enabled = true`. Nothing is copied until a flow is enabled, which is the single most common first-time MM2 mistake.
- D. MirrorMaker requires the legacy `--whitelist '.*'` argument on the command line; the `topics` property alone only filters what the whitelist already allows.

---

> ✅ Hết giờ? Chấm bài ở [answers.md](answers.md) và điền bảng điểm theo domain trước khi xem giải thích.
