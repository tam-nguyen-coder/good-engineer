# 📝 Practice Questions — Week 2: Cluster Config I (broker config, `log.dirs` & storage, retention, compaction)

> **30 questions** · real CCAAK exam style — scenario first, "what should the administrator do" — difficulty ≥ real exam · covers the full Week 2 material + 2 review questions from Week 1.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[DOMAIN · Topic · type]`. Multi = multiple-response (number to choose is stated). Domains: `CFG` (Cluster Configuration), `TROUBLE` (Troubleshooting), `FUND` (Fundamentals).
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[CFG · Thread tuning · Single]`

A broker in a 5-node Kafka 4.3 cluster reports `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` at **0.08** while host CPU sits at 40% and disk utilisation is moderate. Produce p99 latency has tripled over the last hour. What should the administrator do FIRST?

- A. Increase `num.io.threads` cluster-wide with `kafka-configs.sh --entity-type brokers --entity-default --alter --add-config num.io.threads=16`, which takes effect without a restart
- B. Increase `num.network.threads` in `server.properties` on every broker and perform a rolling restart
- C. Raise `queued.max.requests` from 500 to 2000 with `kafka-configs.sh`, since the request queue is the bottleneck
- D. Update the broker configuration znode in ZooKeeper at `/config/brokers/<id>` so the change propagates without a restart

### Question 2 — `[CFG · Update mode · Single]`

An administrator tries to widen the request queue on a running cluster and gets:

```
$ kafka-configs.sh --bootstrap-server kafka-1:19092 --alter \
    --entity-type brokers --entity-default --add-config queued.max.requests=2000
Error while executing config command with args '...'
org.apache.kafka.common.errors.InvalidRequestException: Cannot update these configs dynamically: Set(queued.max.requests)
```

What is the correct interpretation and next step?

- A. The command needs `--entity-name <broker-id>` instead of `--entity-default`; per-broker updates are always allowed
- B. `queued.max.requests` has update mode **read-only**, so it must be set in `server.properties` and applied with a rolling restart
- C. The cluster is missing the `--bootstrap-controller` flag, which is required for all broker-level configuration changes in KRaft
- D. Dynamic broker configuration must be enabled first by setting `dynamic.config.enable=true` on every broker

### Question 3 — `[CFG · Config precedence · Single]`

`kafka-configs.sh --describe --all --entity-type topics --entity-name payments` prints, among other lines:

```
  retention.ms=7200000 sensitive=false synonyms={DYNAMIC_BROKER_CONFIG:log.retention.ms=7200000,
    DYNAMIC_DEFAULT_BROKER_CONFIG:log.retention.ms=259200000, STATIC_BROKER_CONFIG:log.retention.ms=604800000,
    DEFAULT_CONFIG:log.retention.hours=168}
```

Which statement is correct?

- A. The topic has an explicit `retention.ms` override of 7200000 that was set with `--entity-type topics`
- B. The effective value 7200000 comes from a **per-broker dynamic** setting on the broker that answered the request; removing it would make the effective value fall back to 259200000
- C. The effective value comes from `server.properties` (604800000) because static configuration always wins over dynamic configuration
- D. The four synonyms are applied additively, so the real retention is the sum of the listed values

### Question 4 — `[CFG · Config precedence · Multi — Choose 2]`

After a capacity review, an administrator runs:

```
kafka-configs.sh --bootstrap-server kafka-1:19092 --alter \
  --entity-type brokers --entity-default --add-config log.retention.ms=86400000
```

Three days later, five of the forty topics still keep data for a week. Which two statements explain this and describe the correct fix? (Choose two.)

- A. Those five topics carry a `DYNAMIC_TOPIC_CONFIG` override for `retention.ms`, which has higher precedence than any broker-level setting
- B. Cluster-wide defaults only apply to topics created **after** the change; existing topics always keep the value they were created with, regardless of overrides
- C. Run `kafka-configs.sh --describe --all --entity-type topics --entity-name <topic>` on each topic and read the first entry of `synonyms` to confirm where the effective value comes from
- D. The change requires a rolling restart before it becomes effective, because `log.retention.ms` is read-only
- E. `--entity-default` only affects the broker that served the request; it must be repeated once per broker id

### Question 5 — `[CFG · Retention · Single]`

A team sets `retention.ms=3600000` on a low-volume `audit-events` topic (roughly 2 MB per day, 1 partition). Four days later consumers can still read records from day one. Broker logs show no errors and `log.retention.check.interval.ms` is at its default. What is the cause, and what is the correct fix?

- A. `log.retention.check.interval.ms` of 300000 ms is too long; lower it so the retention sweep runs more often
- B. Retention only deletes **closed** log segments, and with the default `segment.bytes` of 1 GiB the active segment has never rolled — set `segment.ms` (for example 600000) on the topic
- C. `retention.ms` is ignored unless `retention.bytes` is also set to a positive value
- D. The topic must be restarted by running `kafka-topics.sh --alter --topic audit-events` before the new retention takes effect

### Question 6 — `[CFG · Capacity · Single]`

A topic has **6 partitions**, `replication.factor=3`, and `retention.bytes=10737418240` (10 GiB). Ignoring index files and compression, what is the maximum amount of disk this topic can consume across the whole cluster?

- A. 10 GiB — `retention.bytes` is a per-topic limit
- B. 60 GiB — 10 GiB per partition, replication does not multiply disk usage because followers share the leader's segments
- C. 180 GiB — `retention.bytes` applies **per partition per replica**: 6 × 10 GiB × 3
- D. 30 GiB — 10 GiB per replica of the topic

### Question 7 — `[CFG · log.dirs / JBOD · Single]`

A broker is configured with `log.dirs=/data/d1,/data/d2,/data/d3`. Monitoring shows `/data/d1` at 94% full while `/data/d3` is at 22%, even though all three disks are identical in size. The number of partition directories is 41, 40 and 40 respectively. What explains this, and what is the correct first action?

- A. Kafka balances log directories by free space, so one of the disks must be reporting its capacity incorrectly; replace the disk
- B. Kafka places each new partition in the directory with the **fewest partitions**, not the most free space, and a partition lives entirely in one directory — so a few large partitions skew byte usage. Run `kafka-log-dirs.sh --describe` to find the largest partitions on `/data/d1`
- C. Kafka stripes each partition across all configured log directories, so the imbalance indicates a corrupted segment index; run `kafka-dump-log.sh --index-sanity-check`
- D. Log directory balancing is handled by the active controller every `leader.imbalance.check.interval.seconds`; trigger it early with `kafka-leader-election.sh`

### Question 8 — `[TROUBLE · Log directory failure · Single]`

A broker with `log.dirs=/data/d1,/data/d2` logs the following while continuing to run:

```
ERROR Error while writing to checkpoint file /data/d2/recovery-point-offset-checkpoint (kafka.server.LogDirFailureChannel)
java.io.IOException: Input/output error
WARN Stopping serving logs in dir /data/d2 (kafka.log.LogManager)
ERROR Uncaught exception in scheduled task 'flush-log' (kafka.utils.KafkaScheduler)
org.apache.kafka.common.errors.KafkaStorageException: Error while writing to checkpoint file
```

`kafka-topics.sh --describe` shows 37 partitions with `Leader: -1` and empty ISR; the remaining partitions on this broker are healthy. What happened?

- A. The broker has lost quorum with the KRaft controller and will shut itself down after `controller.quorum.election.timeout.ms`
- B. The disk backing `/data/d2` failed. Only the partitions stored in that directory went offline; the broker keeps serving partitions in `/data/d1`. The broker would only shut down if **all** of its log directories failed
- C. The `__cluster_metadata` log is corrupt and the broker must be re-formatted with `kafka-storage.sh format`
- D. The broker ran out of file descriptors; raise the `nofile` ulimit and the partitions will come back automatically

### Question 9 — `[TROUBLE · Log directory recovery · Multi — Choose 2]`

Following the situation in Question 8, the failed disk has been replaced and the filesystem is mounted again at `/data/d2` with the correct ownership. Which two statements are correct? (Choose two.)

- A. The broker must be restarted; a log directory that has been marked offline is not brought back online while the broker is running
- B. The broker detects the healthy mount within `log.dir.failure.timeout.ms` and re-registers the directory automatically without a restart
- C. Partitions that had `replication.factor=3` will be re-replicated from their leaders after the restart, and `UnderReplicatedPartitions` returns to 0 once they catch up
- D. Every partition that lived on `/data/d2` is permanently lost regardless of replication factor, because the directory identity changed
- E. Running `kafka-configs.sh --alter --entity-type brokers --entity-name <id> --delete-config cordoned.log.dirs` brings the directory back online

### Question 10 — `[CFG · kafka-log-dirs · Single]`

An administrator runs `kafka-log-dirs.sh --bootstrap-server kafka-1:19092 --describe --broker-list 4` and gets:

```json
{"version":1,"brokers":[{"broker":4,"logDirs":[
  {"logDir":"/data/d1","error":null,"partitions":[
     {"partition":"orders-0","size":8912896,"offsetLag":0,"isFuture":false},
     {"partition":"orders-3","size":9437184,"offsetLag":0,"isFuture":true}]},
  {"logDir":"/data/d2","error":"KAFKA_STORAGE_ERROR","partitions":[]}]}]}
```

Which two facts does this output establish? *(Single answer — pick the option where both statements are correct.)*

- A. `/data/d2` is offline, and `orders-3` is currently being moved into `/data/d1` from another log directory on the same broker
- B. `/data/d2` is simply empty, and `orders-3` is a future partition that will be created when the topic is expanded
- C. `/data/d2` is cordoned, and `orders-3` has an `offsetLag` problem that requires a leader election
- D. `/data/d2` failed, and `orders-0` is the replica that must be reassigned first because it has the largest `offsetLag`

### Question 11 — `[CFG · Cordoning · Single]`

A broker has four log directories. One SSD is showing SMART warnings and must be swapped out during the next maintenance window, but the partitions on it are still serving traffic and must keep doing so until the move is complete. Which action correctly prevents **new** partitions from landing on that disk while leaving current traffic untouched?

- A. `kafka-configs.sh --alter --entity-type brokers --entity-name 3 --add-config cordoned.log.dirs=/data/d2`
- B. Remove `/data/d2` from `log.dirs` with `kafka-configs.sh` and let the broker migrate the partitions automatically
- C. `kafka-configs.sh --alter --entity-type brokers --entity-name 3 --add-config log.dirs.offline=/data/d2`
- D. `kafka-cluster.sh unregister --id 3`, then re-register the broker with the remaining three directories

### Question 12 — `[CFG · Cordoning · Multi — Choose 2]`

Which two statements about cordoned log directories (KIP-1066) in Kafka 4.3 are correct? (Choose two.)

- A. A cordoned log directory continues to serve reads and writes for the partitions it already holds; it is only excluded from **new** partition placement
- B. Cordoning a directory triggers an automatic migration of its partitions to the remaining directories on the same broker
- C. Setting `cordoned.log.dirs="*"` on a broker effectively cordons the whole broker, and a partition reassignment that targets it returns `INELIGIBLE_REPLICA`
- D. `cordoned.log.dirs` is a read-only configuration and therefore requires a broker restart
- E. Cordoning is the supported way to permanently delete the data in a log directory

### Question 13 — `[CFG · Compaction · Single]`

A `customer-profile` topic is configured with `cleanup.policy=compact`. The application writes about 5,000 distinct keys, each updated a few times per hour. After three weeks the partition directories have grown to 60 GiB and keep growing. No errors appear in the broker logs. All other topic settings are at their defaults. What is the MOST likely cause?

- A. `cleanup.policy=compact` has to be combined with `delete` to reclaim any space at all
- B. The log cleaner only processes **closed** segments and only when the dirty ratio reaches `min.cleanable.dirty.ratio` (0.5); with the default `segment.bytes` of 1 GiB, segments rarely roll — lower `segment.ms` on the topic
- C. `log.cleaner.enable` defaults to `false` in Kafka 4.x and must be set to `true` on every broker
- D. Compaction never reduces size on disk; it only hides superseded records from consumers

### Question 14 — `[CFG · Compaction guarantees · Multi — Choose 2]`

Which two statements about log compaction in Kafka 4.3 are correct? (Choose two.)

- A. After compaction, a consumer reading the partition from offset 0 is guaranteed to see exactly one record per key
- B. Compaction never changes the offset of a record; a consumer that asks for an offset that has been cleaned receives the next offset that still exists
- C. Compaction may reorder records so that the newest value for each key appears first
- D. A consumer that stays caught up with the head of the log sees every record that was written, with sequential offsets
- E. A record with a `null` key is compacted into a tombstone and removed after `delete.retention.ms`

### Question 15 — `[CFG · Tombstones · Single]`

A cache-loader service rebuilds its in-memory state by reading a compacted `entitlements` topic from offset 0 on every start. After an incident the service was down for three days; when it came back, a rebuild took **31 hours**, and afterwards several accounts that had been revoked weeks earlier were active again. Topic settings are at their defaults. What is the root cause?

- A. The revocation records were written with `acks=1` and were lost during the incident
- B. Tombstones are retained only for `delete.retention.ms` (default 86,400,000 ms = 24 hours) after the cleaner processes them; a bootstrap that takes longer than that can miss tombstones and resurrect deleted keys
- C. The compacted topic reached `max.compaction.lag.ms` and the cleaner discarded the tombstones early
- D. `min.compaction.lag.ms` defaults to 24 hours, so tombstones younger than a day are never applied

### Question 16 — `[CFG · cleanup.policy · Single]`

A `session-state` topic must keep the latest value for each session key so that a restarted service can rebuild state, but sessions older than 14 days are worthless and the team wants that storage back. Which topic configuration expresses this?

- A. `cleanup.policy=delete` with `retention.ms=1209600000`
- B. `cleanup.policy=compact` with `retention.ms=1209600000`
- C. `cleanup.policy=compact,delete` with `retention.ms=1209600000`
- D. `cleanup.policy=compact` with `delete.retention.ms=1209600000`

### Question 17 — `[CFG · Message size · Single]`

A producer application starts failing for a subset of records with:

```
org.apache.kafka.common.errors.RecordTooLargeException: The message is 2097258 bytes when serialized
which is larger than 1048576, which is the value of the max.request.size configuration.
```

Broker logs contain no corresponding entry at all. What does this tell the administrator?

- A. The topic's `max.message.bytes` must be raised; the broker rejected the batch and the client translated the error
- B. The record never left the client. The producer's own `max.request.size` (default 1,048,576) rejected it before any network call, so the fix belongs in the **producer** configuration — and `max.message.bytes` on the topic will need raising too, or the next attempt fails at the broker
- C. `replica.fetch.max.bytes` is too small, so followers refused the batch and the leader propagated the error to the producer
- D. `socket.request.max.bytes` (104,857,600) was exceeded and the broker closed the connection silently

### Question 18 — `[CFG · Message size · Single]`

After the producer in Question 17 was reconfigured with `max.request.size=5242880`, the same records now fail differently:

```
org.apache.kafka.common.errors.RecordTooLargeException: The request included a message larger than
the max message size the server will accept.
```

and the broker log shows the corresponding `MESSAGE_TOO_LARGE` responses. Which change fixes this correctly?

- A. `kafka-configs.sh --alter --entity-type topics --entity-name <topic> --add-config max.message.bytes=5242880`, and verify `replica.fetch.max.bytes` is at least as large so followers fetch efficiently
- B. Set `message.max.bytes=1048576` on every broker, which is the documented default for the broker-side limit
- C. Set `max.partition.fetch.bytes=5242880` on the consumers; the limit is enforced on the read path
- D. Nothing on the server side — increase `buffer.memory` on the producer so the larger batch fits in the accumulator

### Question 19 — `[CFG · Segment structure · Single]`

An administrator inspects a partition directory on a broker:

```
$ ls /data/d1/orders-0/
00000000000000000000.index      00000000000000000000.log       00000000000000000000.timeindex
00000000000004718592.index      00000000000004718592.log       00000000000004718592.timeindex
00000000000009437184.index      00000000000009437184.log       00000000000009437184.timeindex
leader-epoch-checkpoint         partition.metadata
```

Which statement is correct?

- A. Each `.index` file contains one entry per record, which is why `segment.index.bytes` defaults to 10 MiB
- B. Segment files are named after the offset of the **first** record they contain; `00000000000009437184.log` is the active segment, and it is never deleted by retention nor touched by the log cleaner
- C. The three `.log` files are replicas of the same data kept for crash recovery, governed by `num.recovery.threads.per.data.dir`
- D. `00000000000000000000.log` is the active segment because Kafka always appends to the lowest-numbered file

### Question 20 — `[CFG · Tiered storage · Single]`

A compliance requirement forces a `transactions` topic to retain 13 months of data. At current throughput that is roughly 400 TB across the cluster, and the team cannot justify that much broker-attached SSD. Consumers almost always read data from the last 12 hours; historical reads are rare and may be slower. Which configuration addresses this?

- A. Increase `retention.ms` to 13 months and add `log.dirs` entries backed by cheaper spinning disks on every broker
- B. Enable tiered storage — `remote.log.storage.system.enable=true` on the brokers (a rolling restart, it is read-only) plus `remote.storage.enable=true` on the topic — and set `local.retention.ms` to about 12 hours while `retention.ms` covers 13 months
- C. Set `cleanup.policy=compact,delete` so older duplicate records are compacted away and only the last 13 months of unique keys remain
- D. Mirror the topic to a second, cheaper cluster with MirrorMaker 2 and set `retention.ms=43200000` on the primary

### Question 21 — `[CFG · Tiered storage · Multi — Choose 3]`

A team is rolling out tiered storage. Which three statements are correct for Kafka 4.3? (Choose three.)

- A. Tiered storage cannot be enabled on a topic whose `cleanup.policy` includes `compact`
- B. If `local.retention.ms` is left unset it defaults to `-2`, which means it inherits `retention.ms` — so enabling tiered storage without lowering it frees no local disk
- C. `remote.log.storage.system.enable` can be changed at runtime with `kafka-configs.sh --entity-type brokers --entity-default`
- D. Only closed log segments are copied to remote storage; the active segment always stays local
- E. Once a topic has tiered storage enabled it can be disabled instantly by setting `remote.storage.enable=false`, and all remote segments are copied back to the brokers

### Question 22 — `[CFG · Topic auto-creation · Single]`

During a routine audit an administrator finds 14 topics nobody recognises, all with exactly **1 partition** and **replication factor 1**, and all named like slightly misspelled versions of real topics (`ordrs`, `payment-evnts`). The cluster runs Kafka 4.3 with mostly default broker settings. What happened, and what is the correct preventive action?

- A. A client with `allow.auto.create.topics=true` triggered broker-side auto-creation because `auto.create.topics.enable` defaults to **true**; set it to `false` in `server.properties` and roll the cluster, then create topics explicitly
- B. `delete.topic.enable` defaults to `false`, so topics deleted earlier reappeared after the last restart; set it to `true`
- C. The KRaft controller recreated the topics from a stale snapshot in `__cluster_metadata`; re-format the metadata log
- D. `num.partitions` was temporarily lowered to 1; raise it back to 3 and the affected topics will be expanded automatically

### Question 23 — `[CFG · Update mode · Matching]`

*(Matching-style.)* An administrator is classifying broker configurations by whether they can be changed on a running cluster. Which set of pairings is entirely correct for Kafka 4.3?

- A. `num.io.threads` → cluster-wide (dynamic) · `num.replica.fetchers` → cluster-wide (dynamic) · `log.retention.ms` → cluster-wide (dynamic) · `log.dirs` → read-only (restart) · `queued.max.requests` → read-only (restart)
- B. `num.io.threads` → read-only (restart) · `num.replica.fetchers` → cluster-wide (dynamic) · `log.retention.ms` → read-only (restart) · `log.dirs` → cluster-wide (dynamic) · `queued.max.requests` → cluster-wide (dynamic)
- C. `num.io.threads` → cluster-wide (dynamic) · `num.replica.fetchers` → read-only (restart) · `log.retention.ms` → cluster-wide (dynamic) · `log.dirs` → per-broker (dynamic) · `queued.max.requests` → read-only (restart)
- D. `num.io.threads` → cluster-wide (dynamic) · `num.replica.fetchers` → cluster-wide (dynamic) · `log.retention.hours` → cluster-wide (dynamic) · `log.dirs` → read-only (restart) · `queued.max.requests` → cluster-wide (dynamic)

### Question 24 — `[CFG · Config precedence · Matching]`

*(Matching-style.)* Match each configuration source with the command that writes it. Which set of pairings is entirely correct?

- A. `DYNAMIC_TOPIC_CONFIG` → `--entity-type topics --entity-name t --alter --add-config` · `DYNAMIC_BROKER_CONFIG` → `--entity-type brokers --entity-name 3 --alter --add-config` · `DYNAMIC_DEFAULT_BROKER_CONFIG` → `--entity-type brokers --entity-default --alter --add-config` · `STATIC_BROKER_CONFIG` → edit `server.properties` and restart
- B. `DYNAMIC_TOPIC_CONFIG` → `kafka-topics.sh --alter --config` · `DYNAMIC_BROKER_CONFIG` → `--entity-type brokers --entity-default` · `DYNAMIC_DEFAULT_BROKER_CONFIG` → `--entity-type brokers --entity-name 3` · `STATIC_BROKER_CONFIG` → `kafka-storage.sh format`
- C. `DYNAMIC_TOPIC_CONFIG` → `--entity-type topics --entity-default` · `DYNAMIC_BROKER_CONFIG` → write the znode `/config/brokers/3` · `DYNAMIC_DEFAULT_BROKER_CONFIG` → write the znode `/config/brokers/<default>` · `STATIC_BROKER_CONFIG` → edit `server.properties` and restart
- D. `DYNAMIC_TOPIC_CONFIG` → `--entity-type topics --entity-name t --alter --add-config` · `DYNAMIC_BROKER_CONFIG` → `--entity-type brokers --entity-default --alter --add-config` · `DYNAMIC_DEFAULT_BROKER_CONFIG` → `--entity-type brokers --entity-name 3 --alter --add-config` · `STATIC_BROKER_CONFIG` → `--bootstrap-controller` only

### Question 25 — `[TROUBLE · Disk full playbook · Ordering]`

*(List-order.)* A broker in a 6-node cluster reports one log directory offline with `KafkaStorageException: No space left on device`. Several partitions are offline; the broker itself is still running and serving its other directory. Put the administrator's actions in the correct order.

1. Restart the broker so the recovered log directory is brought back online
2. Run `kafka-log-dirs.sh --describe --broker-list <id>` to identify which directory failed and which partitions consume the most space
3. Set `retention.bytes` and a smaller `segment.ms` on the offending topic so the situation cannot recur
4. Free space — lower retention on the largest topic, delete unneeded topics, or reassign partitions to other brokers with `--throttle`
5. Confirm `UnderReplicatedPartitions` returns to 0 and every partition has a leader again

- A. 2 → 4 → 1 → 5 → 3
- B. 1 → 2 → 4 → 3 → 5
- C. 4 → 1 → 2 → 5 → 3
- D. 2 → 1 → 4 → 5 → 3

### Question 26 — `[TROUBLE · Recovery · Single]`

A broker holding roughly 3,000 partitions across two data directories was terminated with `kill -9`. On restart it takes 47 minutes before it logs `Kafka Server started`, and during that time `UnderReplicatedPartitions` stays high across the cluster. Which two-part answer is correct?

- A. The delay is log recovery — index rebuilding for segments that were not cleanly closed. Raise `num.recovery.threads.per.data.dir` (default **2** since Kafka 4.0, cluster-wide so it can be changed dynamically) and, going forward, shut brokers down with `controlled.shutdown.enable=true` rather than `kill -9`
- B. The delay is the controller re-electing leaders. Lower `controller.quorum.election.timeout.ms` from its default of 1000 ms
- C. The delay is caused by `num.recovery.threads.per.data.dir` defaulting to **1**; it is read-only, so the broker must be restarted again after editing `server.properties`
- D. The delay is the log cleaner rebuilding its dedupe buffer. Raise `log.cleaner.dedupe.buffer.size` above 128 MiB

### Question 27 — `[CFG · Partitions · Single]`

A topic was over-provisioned at creation with 96 partitions; the team now wants 24 to reduce open file handles and metadata overhead. What should the administrator tell them?

- A. Run `kafka-topics.sh --bootstrap-server ... --alter --topic t --partitions 24`; Kafka merges the surplus partitions in the background
- B. Kafka does not support reducing the number of partitions for a topic. The only route is to create a new topic with 24 partitions and copy the data across, then cut consumers over
- C. Run `kafka-topics.sh --zookeeper ... --alter --topic t --partitions 24`, which is still the supported path for shrinking a topic
- D. Set `num.partitions=24` as a cluster-wide dynamic default; existing topics are resized on the next preferred leader election

### Question 28 — `[CFG · Topic overrides · Single]`

A topic `metrics-raw` has `retention.ms=3600000` set as a topic override. The cluster has `log.retention.ms=259200000` as a dynamic cluster-wide default and `log.retention.hours=168` in `server.properties`. An administrator runs:

```
kafka-configs.sh --bootstrap-server kafka-1:19092 --alter \
  --entity-type topics --entity-name metrics-raw --delete-config retention.ms
```

What is the effective retention for `metrics-raw` afterwards?

- A. 604,800,000 ms — the static `server.properties` value, because deleting an override restores the broker's startup configuration
- B. 259,200,000 ms — the next source down the precedence chain, `DYNAMIC_DEFAULT_BROKER_CONFIG`
- C. 604,800,000 ms — the documented `DEFAULT_CONFIG` value, because `--delete-config` always restores the shipped default
- D. 3,600,000 ms — deleting the override only stops future updates; the current value is retained until the topic is recreated

### Question 29 — `[FUND · Week 1 review · Single]`

On a Kafka 4.3 cluster with three dedicated controllers, the administrator wants to confirm that the metadata quorum is healthy and identify the current leader before starting a rolling restart of the brokers. Which command gives that answer?

- A. `kafka-metadata-quorum.sh --bootstrap-server kafka-1:9092 describe --status`
- B. `zookeeper-shell.sh localhost:2181 get /controller`
- C. `kafka-configs.sh --describe --entity-type brokers --entity-default`
- D. `kafka-cluster.sh cluster-id --bootstrap-server kafka-1:9092`

### Question 30 — `[FUND · Week 1 review · Multi — Choose 2]`

A new broker is added to an existing Kafka 4.3 cluster. It starts, registers, and appears in `kafka-broker-api-versions.sh`, but after two days it is still holding no partitions and its disks are empty. Which two statements are correct? (Choose two.)

- A. Kafka never moves existing partitions onto a new broker automatically; the administrator must run `kafka-reassign-partitions.sh --generate` / `--execute`, ideally with `--throttle`, and then `--verify` to remove the throttle
- B. New topics and new partitions created after the broker joined can be placed on it, which is why an idle broker is normal right after scale-out but not after two days of topic creation
- C. `auto.leader.rebalance.enable=true` will migrate partitions to the new broker within `leader.imbalance.check.interval.seconds`
- D. The broker must be added to `controller.quorum.voters` on every existing node before it can hold partitions
- E. Setting `cordoned.log.dirs=""` on the new broker forces the controller to start assigning partitions to it

---

> ✅ Done? Check your answers in [answers.md](answers.md), log every wrong answer, and group them into the five buckets from the [week plan](README.md#-buổi-d--practice--review-2h): config precedence / update mode / `log.dirs` & JBOD / retention & segment / compaction. Then re-read the matching section before moving on to Week 3.
