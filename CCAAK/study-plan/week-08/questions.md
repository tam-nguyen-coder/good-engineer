# 📝 Practice Questions — Week 8: Final Cumulative Mock Exam (Cross-Domain)

> **30 questions** · **cross-domain mini mock** in real CCAAK exam style, difficulty ≥ real exam · covers **all 7 CCAAK domains** (not scoped to a single week like previous weeks).
> ⏱️ **Run it timed: 45 minutes for 30 questions (pace ~90 seconds/question), straight through, no reference material**, then self-grade with [answers.md](answers.md). It is a half-size version of the real 60-question / 90-minute exam — use it as the **warm-up** before the full 60-question mocks in [`mock-exams/`](../../mock-exams/README.md).
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first. answers.md includes a **per-domain score table across all 7 domains** → find the weak domain and go back to the matching week.
> Exam-weighted mix: **CFG 7 (22%) · FUND 4 (15%) · SEC 5 (15%) · TROUBLE 4 (15%) · ARCH 4 (12%) · CONNECT 3 (12%) · OBS 3 (10%)**. Domain order is **shuffled**, like the real exam.
> Format mix: **20 single** · **6 multiple-select** · **2 matching** (Q11, Q24) · **2 list-order** (Q17, Q20). Over 60% of the questions open with a **symptom, log line, CLI output or metric** — that is the CCAAK house style: *it rarely asks you to define a term, it asks which action a competent administrator would take*.
> Version anchor: **Apache Kafka 4.3** (KRaft-only) defaults unless a version is stated in the question. Cluster in the scenarios: node 1 = dedicated controller, nodes 2/3/4 = brokers, unless stated otherwise.
> Tag: `[DOMAIN · Topic · type]`. Multi = multiple-select (the number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[TROUBLE · Under-replicated partitions · Single]`
An on-call administrator is paged. `kafka-topics.sh --bootstrap-server kafka-1:19092 --describe --topic payments` prints:

```
Topic: payments  TopicId: 8c1QeR3wQ9qGm3xMQZ9nZQ  PartitionCount: 6  ReplicationFactor: 3  Configs: min.insync.replicas=2
  Topic: payments  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3  Elr:   LastKnownElr:
  Topic: payments  Partition: 1  Leader: 3  Replicas: 3,4,2  Isr: 3,2  Elr:   LastKnownElr:
  Topic: payments  Partition: 2  Leader: 2  Replicas: 4,2,3  Isr: 2,3  Elr:   LastKnownElr:
  Topic: payments  Partition: 3  Leader: 3  Replicas: 2,3,4  Isr: 3,2  Elr:   LastKnownElr:
  Topic: payments  Partition: 4  Leader: 2  Replicas: 3,4,2  Isr: 2,3  Elr:   LastKnownElr:
  Topic: payments  Partition: 5  Leader: 3  Replicas: 4,2,3  Isr: 3,2  Elr:   LastKnownElr:
```

`UnderReplicatedPartitions` is 6 and has been non-zero for four minutes. Producers are still writing successfully. What should the administrator do **FIRST**?
- A. Set `unclean.leader.election.enable=true` cluster-wide so leadership can move immediately.
- B. Check whether broker 4 is actually alive (process, disk, `server.log`, network) — the same node id is missing from every ISR, which points at broker availability, not at replication tuning. Only if broker 4 is healthy and merely lagging should `num.replica.fetchers` be raised.
- C. Lower `min.insync.replicas` from 2 to 1 on `payments` so the partitions stop counting as under-replicated.
- D. Run `kafka-reassign-partitions.sh` immediately to move every replica off broker 4.

### Question 2 — `[CFG · Configuration precedence · Single]`
An administrator raises durability cluster-wide with:

```
kafka-configs.sh --bootstrap-server kafka-1:19092 --alter \
  --entity-type brokers --entity-default --add-config min.insync.replicas=2
```

The command is accepted, but topic `legacy-events` keeps accepting `acks=all` writes with only one in-sync replica. `kafka-configs.sh --describe --all --entity-type topics --entity-name legacy-events` lists `min.insync.replicas=1` with `DYNAMIC_TOPIC_CONFIG` first in the synonyms list. What is the correct explanation?
- A. `--entity-default` only applies to brokers that are restarted after the change, so a rolling restart is required for it to take effect.
- B. `min.insync.replicas` is a read-only broker config and cannot be set dynamically at all; the command silently did nothing.
- C. Configuration resolves through five levels — `DYNAMIC_TOPIC_CONFIG` > `DYNAMIC_BROKER_CONFIG` > `DYNAMIC_DEFAULT_BROKER_CONFIG` > `STATIC_BROKER_CONFIG` > `DEFAULT_CONFIG` — so the topic-level override wins and must be changed or deleted on the topic itself.
- D. `--entity-default` writes the value to the `/config/brokers/<default>` znode, which KRaft-mode brokers no longer read; the value must be set through `zookeeper-shell.sh`.

### Question 3 — `[SEC · ACL troubleshooting · Single]`
A consumer application stopped working after a security change. Producing to the same topic still works. `kafka-authorizer.log` on the leader broker shows:

```
[2026-09-18 03:12:44,901] INFO Principal = User:orders-svc is Denied operation = Read from host = 10.4.2.19
  on resource = Group:LITERAL:fulfillment for request = OffsetFetch with resourceRefCount = 1 (kafka.authorizer.logger)
```

What is the **minimum** correct fix?
- A. Grant `Read` on the **Group** resource `fulfillment` to `User:orders-svc`, for example `kafka-acls.sh --add --allow-principal User:orders-svc --operation Read --group fulfillment`.
- B. Add `User:orders-svc` to `super.users` on every broker and restart them.
- C. Set `allow.everyone.if.no.acl.found=true` so requests without a matching ACL are permitted.
- D. Switch `authorizer.class.name` to `kafka.security.authorizer.AclAuthorizer`, because `StandardAuthorizer` does not evaluate Group ACLs.

### Question 4 — `[ARCH · Rack awareness · Multi — Choose 2]`
A post-incident review of a cluster spread over three availability zones shows that losing AZ-b took 40% of the partitions offline: all three replicas of those partitions happened to live in AZ-b. The team also wants to cut the cross-AZ data-transfer bill generated by consumers. Which **two** changes address these goals? (Choose two.)
- A. Set `broker.rack` on each broker to its AZ identifier, so the controller spreads the replicas of each partition across racks when partitions are created or reassigned.
- B. Set `min.insync.replicas=3` so that every availability zone must acknowledge each write.
- C. Set `client.rack` on the consumers and use follower fetching (KIP-392) so a consumer reads from a replica in its own rack instead of always from the leader.
- D. Raise `num.replica.fetchers` to 3, one fetcher per availability zone.
- E. Enable `unclean.leader.election.enable=true` so a leader is always available in the surviving zones.

### Question 5 — `[OBS · Broker saturation · Single]`
Produce p99 latency has tripled over two days. On every broker:

```
kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent   = 0.08
kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent           = 0.65
kafka.network:type=RequestMetrics,name=TotalTimeMs,request=Produce            -> dominated by RequestQueueTimeMs
```

Host CPU sits at 40% and the disks are not saturated. What should the administrator change **FIRST**?
- A. Increase `num.network.threads` (default 3), because `TotalTimeMs` is high.
- B. Increase `queued.max.requests` from 500 so requests stop waiting in the queue.
- C. Add two brokers and reassign partitions to spread the load.
- D. Increase `num.io.threads` (default **8**) — the request handler pool is the saturated resource, and this is a dynamic, per-broker, reversible change.

### Question 6 — `[CFG · Retention vs segment roll · Single]`
Compliance requires that topic `audit-trail` keeps nothing older than one hour. The topic is configured with `retention.ms=3600000`; segment settings are left at their defaults (`segment.bytes=1073741824`, and the broker default `log.roll.hours=168`). Traffic is about 8 MB/day. Five days later, records from day one are still readable. What is the correct explanation and fix?
- A. Retention is enforced only on **closed** segments, and at this traffic level the single active segment never reaches 1 GiB or 7 days; lower `segment.ms` (or `segment.bytes`) on the topic so segments roll and become eligible for deletion.
- B. A topic-level `retention.ms` cannot be lower than the broker's `log.retention.hours` (168), so the broker silently uses 7 days.
- C. `log.retention.check.interval.ms` defaults to 300000 ms, which is far too long to enforce a one-hour retention; lower it to 1000 ms.
- D. The log cleaner only deletes data when `cleanup.policy=compact`; with `delete` the segments must be removed manually.

### Question 7 — `[CONNECT · Task failure · Single]`
`GET /connectors/es-sink/status` on the Connect REST API returns:

```json
{"name":"es-sink",
 "connector":{"state":"RUNNING","worker_id":"10.0.0.7:8083"},
 "tasks":[{"id":0,"state":"RUNNING","worker_id":"10.0.0.7:8083"},
          {"id":1,"state":"FAILED","worker_id":"10.0.0.8:8083",
           "trace":"org.apache.kafka.connect.errors.DataException: Converting byte[] to Kafka Connect data failed due to serialization error ..."}],
 "type":"sink"}
```

Monitoring reported the connector as healthy. What is the correct administrator response?
- A. Delete and recreate the connector, since a `DataException` means its configuration is permanently corrupted.
- B. A `RUNNING` connector state says nothing about its tasks; restart the failed task (`POST /connectors/es-sink/tasks/1/restart`, or `POST /connectors/es-sink/restart?includeTasks=true`), and stop the same record from killing it again by setting `errors.tolerance=all` together with `errors.deadletterqueue.topic.name`.
- C. Do nothing: the worker automatically restarts failed tasks once `task.shutdown.graceful.timeout.ms` elapses.
- D. Increase `tasks.max` so that the healthy task takes over the partitions of the failed one.

### Question 8 — `[FUND · KRaft controller · Single]`
On an Apache Kafka 4.3 cluster with three dedicated controllers, Grafana shows `ActiveControllerCount` (summed across the cluster) dropping to 0 for about six seconds and then returning to 1. `controller.log` on a surviving node records a new leader epoch. Which statement correctly describes what happened?
- A. The first broker to successfully recreate the ZooKeeper ephemeral node `/controller` became the new controller.
- B. All brokers entered read-only mode until the failed controller restarted with the same `node.id`.
- C. The remaining controllers elected a new leader for the metadata log through the Raft protocol over `__cluster_metadata`; brokers kept serving reads and writes throughout the short election.
- D. The broker with the lowest `node.id` was promoted automatically by the coordination service configured in `zookeeper.connect`.

### Question 9 — `[CFG · Quotas · Multi — Choose 2]`
A tenant complains that its producer throughput plateaus at exactly 10 MB/s during business hours. The producer logs contain no errors, the broker logs are clean, and no partition is under-replicated. The client metric `produce-throttle-time-avg` is consistently above 300 ms. Which **two** statements are correct? (Choose two.)
- A. The producer has exhausted `buffer.memory` and is blocking in `max.block.ms`; raising `buffer.memory` will lift the plateau.
- B. The broker enforces quotas by **delaying responses**, not by returning an error, which is exactly why both the client and the broker logs look clean.
- C. A quota breach returns `QuotaViolationException` to the client, so the application must be catching and swallowing it.
- D. A `producer_byte_rate` quota is in effect; quota lookup follows an **8-level precedence**, from the most specific match (user + client-id) down to the cluster-wide default.
- E. Quotas can only be defined statically in `server.properties` and require a rolling restart to change.

### Question 10 — `[TROUBLE · Log directories · Single]`
Broker 3 is configured with `log.dirs=/data/disk1/kafka,/data/disk2/kafka`. `server.log` shows:

```
[2026-09-19 02:41:07,338] ERROR Error while writing to checkpoint file /data/disk2/kafka/recovery-point-offset-checkpoint (kafka.server.LogDirFailureChannel)
java.io.IOException: No space left on device
[2026-09-19 02:41:07,402] WARN  Stopping serving logs in dir /data/disk2/kafka (kafka.log.LogManager)
[2026-09-19 02:41:09,110] ERROR [ReplicaManager broker=3] Error processing append operation on partition clicks-7 (kafka.server.ReplicaManager)
org.apache.kafka.common.errors.KafkaStorageException: Log directory /data/disk2/kafka is offline
```

The broker process is still running and most partitions are unaffected. What is the correct **first** diagnostic step?
- A. Run `kafka-log-dirs.sh --bootstrap-server kafka-1:19092 --describe --broker-list 3` to see exactly which partitions lived on the failed directory and how space is distributed across the remaining one — with JBOD, a single failed `log.dirs` entry takes only its own partitions offline while the broker keeps serving the rest.
- B. Restart broker 3 immediately; a restart re-mounts the log directory and recovers the partitions.
- C. Set `unclean.leader.election.enable=true` so the offline partitions can elect a leader on the other brokers.
- D. Free space by deleting the oldest `.log` segment files on `/data/disk2` with `rm`, then let the broker re-index them.

### Question 11 — `[SEC · Exception mapping · Matching]`
*(Matching-style.)* An administrator is mapping client-side exceptions to their root cause on a cluster using `SASL_SSL` with SCRAM-SHA-512 and `StandardAuthorizer`. Which set of pairings is **entirely** correct?
- A. `TopicAuthorizationException` → missing `Read` on the Group · `GroupAuthorizationException` → missing `Write` on the Topic · `SaslAuthenticationException` → expired broker certificate · `SSLHandshakeException` → wrong SCRAM password.
- B. `TopicAuthorizationException` → the topic does not exist · `GroupAuthorizationException` → the group is rebalancing · `SaslAuthenticationException` → the mechanism is missing from `sasl.enabled.mechanisms` · `SSLHandshakeException` → `ssl.client.auth=none` on the broker.
- C. `TopicAuthorizationException` → the principal has **no matching ACL on the Topic resource** · `GroupAuthorizationException` → the principal lacks **`Read` on the Group resource** · `SaslAuthenticationException` → the **credential itself was rejected** (unknown user or wrong SCRAM password), so authentication failed · `SSLHandshakeException` → the **TLS handshake failed** (untrusted or expired certificate, or a missing client certificate when mTLS is required).
- D. All four exceptions indicate an authorization failure and are all fixed with `kafka-acls.sh --add`; the only difference is which resource type appears in the message.

### Question 12 — `[ARCH · Disaster recovery · Single]`
During a failover drill, consumers were restarted against the DR cluster and reprocessed roughly nine hours of data. The business requires that after a failover consumers resume at **the same offsets**, and the platform team wants **the fewest moving parts to operate**. The company runs Confluent Platform on both sites. Which option meets the requirement?
- A. MirrorMaker 2 with `IdentityReplicationPolicy`, because keeping the topic names identical also keeps the offsets identical.
- B. **Cluster Linking** — the destination broker fetches directly from the source and preserves offsets **byte-for-byte**, with no Connect cluster to operate.
- C. MirrorMaker 1, which mirrors offsets natively and is simpler than MirrorMaker 2.
- D. A stretch cluster across both data centres with `min.insync.replicas=3`, so no replication tool is needed at all.

### Question 13 — `[CFG · Replica fetchers · Single]`
A failed broker was replaced 40 minutes ago. `UnderReplicatedPartitions` has fallen only from 430 to 412. On the recovering broker the NIC is at 15% utilisation, disk `await` is low, CPU is 20%, and `num.replica.fetchers` is at its default. Which change should the administrator make **FIRST**?
- A. Raise `num.replica.fetchers` (default **1**) on the recovering broker — a dynamic per-broker config that takes effect without a restart and can be lowered again afterwards.
- B. Raise `replica.lag.time.max.ms` above 30000 so the catching-up replicas count as in-sync sooner.
- C. Run `kafka-leader-election.sh --election-type unclean` to force leadership onto the new broker.
- D. Raise `num.io.threads` above 8, because replication traffic is served by the request handler pool.

### Question 14 — `[OBS · Metrics during broker loss · Multi — Choose 2]`
In a three-broker cluster where every topic uses RF 3 and `min.insync.replicas=2`, one broker crashes. Which **two** observations are expected while it is down? (Choose two.)
- A. `UnderReplicatedPartitions` is greater than 0 on the surviving leaders of partitions that had a replica on the dead broker.
- B. `ActiveControllerCount` summed across the cluster drops to 0 until the broker rejoins.
- C. `OfflinePartitionsCount` immediately rises above 0 for every partition that had a replica on the dead broker.
- D. `UnderMinIsrPartitionCount` stays at 0 as long as two replicas remain in sync, so `acks=all` producers keep writing successfully.
- E. `records-lag-max` rises on the brokers, because brokers track consumer lag internally.

### Question 15 — `[FUND · min.insync.replicas · Single]`
One broker of a three-broker cluster is down for planned maintenance. A producer using `acks=all` starts failing:

```
org.apache.kafka.common.errors.NotEnoughReplicasException: Messages are rejected since there are fewer in-sync replicas than required.
```

`kafka-configs.sh --describe --entity-type topics --entity-name payments` shows `min.insync.replicas=3` on a topic whose replication factor is 3. Which remediation restores writes **without** weakening durability below the standard production setting?
- A. Set the topic's `min.insync.replicas=1` so writes never block again.
- B. Change the producer to `acks=1` until the maintenance window ends.
- C. Set the topic's `min.insync.replicas=2`; RF 3 + `min.insync.replicas=2` + `acks=all` is the standard production triple and tolerates the loss of exactly one broker with no data loss.
- D. Set `unclean.leader.election.enable=true` so a leader is always available.

### Question 16 — `[CONNECT · Distributed worker · Multi — Choose 2]`
An administrator inherits a three-worker Kafka Connect cluster with `group.id=connect-prod` and lists the topics on the cluster that stores its state. Which **two** statements are correct? (Choose two.)
- A. Connect keeps connector configs, source offsets and statuses in three **compacted** internal topics, whose defaults are `connect-configs` **1** partition, `connect-offsets` **25** partitions and `connect-status` **5** partitions; in production all three should have a replication factor of 3.
- B. Sink connector consumer offsets are stored in `connect-offsets` together with the source offsets.
- C. `tasks.max` is an **upper bound**: if a sink connector is given more tasks than the source topic has partitions, the extra tasks are assigned no partitions and sit idle.
- D. The three workers elect their leader through ZooKeeper, which is why `zookeeper.connect` must be present in `connect-distributed.properties`.
- E. Each worker must list the connectors it is responsible for in its own `connect-distributed.properties`.

### Question 17 — `[CFG · Partition reassignment · Ordering]`
*(List-order style.)* A fifth node was added to the cluster three days ago and still holds zero partitions of the existing topic `events`. The administrator must move replicas onto it while **bounding the replication traffic**, and then return leadership to the preferred replicas. Which ordered procedure is correct?
- A. `--execute` to start the move → `--generate` to produce the plan that documents it → `--verify` → rolling restart of all brokers so they pick up the new assignment.
- B. `kafka-topics.sh --zookeeper ... --alter --partitions` to add partitions on the new broker → `--generate` → `--execute` → `--verify`.
- C. `--generate` → `--execute --throttle <bytes/s>` → `kafka-leader-election.sh --election-type preferred` → nothing further, because the throttle configuration is removed automatically once the reassignment finishes.
- D. `kafka-reassign-partitions.sh --topics-to-move-json-file ... --broker-list ... --generate` → `--reassignment-json-file ... --execute --throttle <bytes/s>` → repeat `--verify` until every partition reports `completed` (this is also the step that **clears the throttle**) → `kafka-leader-election.sh --election-type preferred --all-topic-partitions`.

### Question 18 — `[SEC · Credential rotation · Single]`
An audit flags that `User:etl-svc` has used the same SCRAM-SHA-512 password for 14 months. The password must be rotated on a six-broker KRaft cluster **without restarting any broker** and without a maintenance window. Which procedure is correct?
- A. Run `kafka-configs.sh --bootstrap-server ... --alter --add-config 'SCRAM-SHA-512=[password=<new>]' --entity-type users --entity-name etl-svc`; SCRAM credentials live in the KRaft metadata log, so the change propagates cluster-wide immediately, after which the clients are rolled onto the new password.
- B. Edit `kafka_server_jaas.conf` on each broker with the new password and perform a rolling restart.
- C. Re-run `kafka-storage.sh format --add-scram 'SCRAM-SHA-512=[name=etl-svc,password=<new>]'` on every broker's log directory.
- D. Update the credential under the `/config/users/etl-svc` znode with `zookeeper-shell.sh`; the brokers pick the change up through a watch.

### Question 19 — `[TROUBLE · Listeners · Single]`
A newly deployed application in another subnet fails on every produce attempt:

```
org.apache.kafka.common.errors.TimeoutException: Topic orders not present in metadata after 60000 ms
```

Diagnostics show: the client can open a TCP connection to the bootstrap port; the topic exists (`kafka-topics.sh --describe --topic orders` run inside the broker container works); applications already running on the broker subnet produce to `orders` normally. What is the most likely cause?
- A. `auto.create.topics.enable=false` on the brokers, so the client cannot create the topic it needs.
- B. `advertised.listeners` publishes an address (for example the container hostname) that the new client cannot resolve or route to, so the client receives metadata pointing at brokers it cannot reach.
- C. `metadata.max.age.ms` on the client is too high, so it has not yet fetched the topic metadata.
- D. The controller quorum has lost its majority, so metadata requests are rejected.

### Question 20 — `[ARCH · Rolling upgrade · Ordering]`
*(List-order style.)* A five-broker KRaft cluster with three dedicated controllers is being upgraded from Apache Kafka 4.2 to 4.3. Which ordered procedure is correct?
- A. Upgrade the nodes **one at a time** (controlled shutdown → replace the binaries → start → **wait for `UnderReplicatedPartitions` to return to 0** before touching the next node) → confirm the whole cluster runs 4.3 and behaves normally → finalize with `kafka-features.sh --bootstrap-server ... upgrade --release-version 4.3`.
- B. Finalize the metadata version first with `kafka-features.sh upgrade --release-version 4.3`, then roll the nodes one at a time.
- C. Set `inter.broker.protocol.version=4.3` in every `server.properties`, restart all brokers simultaneously to avoid a mixed-version window, then remove the setting.
- D. Stop ZooKeeper, run the ZooKeeper-to-KRaft migration, then roll the brokers onto the 4.3 binaries.

### Question 21 — `[CFG · JBOD storage balance · Single]`
A broker is configured with four equally sized `log.dirs`. `kafka-log-dirs.sh --describe` shows `/data/disk4` at 91% used while the other three sit near 40%; no directory has failed. What explains this, and what is the cheapest correct remedy?
- A. Kafka balances log directories by free space, so disk4 must have a filesystem error; replace the disk.
- B. Nothing can be rebalanced inside a broker; the only fix is to add a broker and reassign partitions off this one.
- C. Kafka places a new partition in the log directory that currently holds the **fewest partitions**, not the one with the most free space, so a few high-volume partitions can end up together. Move specific replicas between directories with `kafka-reassign-partitions.sh` using the `log_dirs` field of the reassignment JSON; on 4.3 the full directory can also be **cordoned** (KIP-1066) so no new partition is placed on it.
- D. Set `log.retention.bytes` on the busiest topics so that the oldest segments on disk4 are deleted first.

### Question 22 — `[FUND · ISR semantics · Multi — Choose 2]`
While investigating flapping replication, an administrator watches `kafka-topics.sh --describe` and sees the `Isr` list for a partition shrink from `2,3,4` to `2,3` and expand again every few minutes. Which **two** statements about the in-sync replica set are correct? (Choose two.)
- A. The high watermark is the highest offset replicated to every replica in the replica set, including replicas that are currently out of sync.
- B. A follower is removed from the ISR when it has not caught up with the leader within `replica.lag.time.max.ms`, whose default is **30000** ms.
- C. `acks=all` waits for acknowledgement from **all replicas currently in the ISR**, not from every replica in the replica set.
- D. A follower that falls out of the ISR is removed from the replica set, and the controller automatically creates a replacement replica on another broker.
- E. The modern way to measure follower lag is the message-count threshold `replica.lag.max.messages`.

### Question 23 — `[SEC · ACLs at scale · Multi — Choose 2]`
A platform team must grant one principal access to several hundred topics, all named with the prefix `team-a.`, including topics that do not exist yet. Which **two** statements are correct? (Choose two.)
- A. A **PREFIXED** ACL on the resource pattern `team-a.` grants the operation on every topic whose name starts with that prefix, including topics created later.
- B. If any matching **DENY** ACL exists, it takes precedence over every matching ALLOW ACL, regardless of which is more specific or which was added first.
- C. Adding the principal to `super.users` is the recommended way to express prefix-based access, because it avoids maintaining ACLs.
- D. When an authorizer is configured, `allow.everyone.if.no.acl.found` defaults to `true`, so only DENY rules actually need to be written.
- E. A LITERAL ACL supports shell-style wildcards inside the name, so `team-a.*` as a LITERAL pattern matches the same set of topics.

### Question 24 — `[OBS · Metric meaning · Matching]`
*(Matching-style.)* An administrator is building an on-call runbook and maps broker metrics to what they mean. Which set of pairings is **entirely** correct?
- A. `UnderReplicatedPartitions` > 0 → no leader is available · `OfflinePartitionsCount` > 0 → redundancy is degraded · `ActiveControllerCount` = 2 → a healthy failover is in progress · `RequestHandlerAvgIdlePercent` = 0.05 → the network threads are saturated.
- B. `UnderReplicatedPartitions` > 0 → **redundancy is degraded**: the replicas exist but are not all in sync · `OfflinePartitionsCount` > 0 → **availability is lost**: no leader can be elected for those partitions · `ActiveControllerCount` summed across the cluster must equal **1** · `RequestHandlerAvgIdlePercent` below **0.3** → the **request handler (I/O) thread pool is saturated**, raise `num.io.threads`.
- C. `UnderReplicatedPartitions` > 0 → producers with `acks=all` are already blocked · `OfflinePartitionsCount` > 0 → consumers are lagging · `ActiveControllerCount` = 0 is normal on a non-controller broker, so the per-broker value is what should be alerted on · `RequestHandlerAvgIdlePercent` above 0.3 → the broker is overloaded.
- D. `UnderReplicatedPartitions` and `OfflinePartitionsCount` are the same condition measured on the leader and on the follower respectively · `ActiveControllerCount` counts the controllers in the quorum, so 3 is correct for a 3-node quorum · `RequestHandlerAvgIdlePercent` measures disk idle time.

### Question 25 — `[CFG · Message size · Single]`
An application must publish 4 MB records. Producers currently fail with:

```
org.apache.kafka.common.errors.RecordTooLargeException: The request included a message larger than the max message size the server will accept.
```

Which set of changes is required so that the records are produced, replicated and consumed successfully?
- A. Only the producer's `max.request.size`; the broker accepts whatever the producer sends once the client limit is raised.
- B. Nothing on the broker: `socket.request.max.bytes` is already 104857600 (100 MiB), which is the effective limit on record size.
- C. Raise `log.segment.bytes`, because a record can never exceed the segment size.
- D. Raise the broker/topic limit (`message.max.bytes`, default **1048588**, or the topic-level `max.message.bytes`) **and** `replica.fetch.max.bytes` (default **1048576**) — otherwise followers cannot fetch the oversized records and the partition becomes permanently under-replicated — plus the producer's `max.request.size` and the consumer's `max.partition.fetch.bytes`.

### Question 26 — `[CONNECT · Plugin operations · Single]`
A team upgrades a connector plugin by copying the new JAR into `plugin.path` on all three Connect workers and then calls `POST /connectors/es-sink/restart?includeTasks=true`. The connector keeps reporting the old plugin version. Why?
- A. Plugin JARs are discovered and loaded by the worker's plugin classloader **at worker startup**; restarting a connector or its tasks does not reload classes from disk, so a **rolling restart of the workers** is required.
- B. The REST restart only restarts tasks, so the connector must additionally be paused with `PUT /connectors/es-sink/pause` and then resumed.
- C. `plugin.path` must be declared in the connector configuration rather than in the worker configuration.
- D. The old plugin version is cached in the `connect-configs` topic; deleting and recreating that topic clears the cache.

### Question 27 — `[TROUBLE · Consumer group rebalance · Single]`
Lag on consumer group `billing` climbs steadily. `kafka-consumer-groups.sh --describe --group billing` prints the assignment table and then:

```
Warning: Consumer group 'billing' is rebalancing.
```

The application log on one member shows:

```
[Consumer clientId=billing-3, groupId=billing] Member billing-3-a41c sending LeaveGroup request to coordinator
due to consumer poll timeout has expired. This means the time between subsequent calls to poll() was longer than
the configured max.poll.interval.ms, which typically implies that the poll loop is spending too much time
processing messages.
```

Host CPU on the consumer nodes is at 25%. What should the administrator recommend **FIRST**?
- A. Increase the topic's partition count so each consumer receives fewer records per poll.
- B. Raise `session.timeout.ms` above its 45000 ms default so the coordinator waits longer before evicting the member.
- C. Have the application team lower `max.poll.records` (default **500**) or raise `max.poll.interval.ms` (default **300000** ms) — the heartbeat thread is alive, so this is a slow poll loop, not a dead process.
- D. Add more consumers to the group so the work is spread more thinly.

### Question 28 — `[ARCH · Capacity planning · Single]`
A new cluster must ingest a sustained **60 MB/s**, keep **7 days** of retention, and use **replication factor 3**, with a 20% headroom factor. Which statement about the raw storage the cluster must provide is correct?
- A. About **36 TB** — throughput × retention is the figure that matters; replication does not multiply stored bytes because followers share the leader's segments.
- B. About **131 TB** — `throughput × retention × RF × 1.2`; enabling **tiered storage** would cut the *local* disk requirement substantially, because `local.retention.ms` can be far shorter than the topic's total retention.
- C. About **109 TB** — replication is included, but a headroom factor is unnecessary because `log.retention.bytes` caps usage per partition.
- D. About **44 TB** — throughput × retention × 1.2; the replication factor affects network bandwidth, not disk.

### Question 29 — `[FUND · Internal topics · Single]`
An administrator disables `auto.create.topics.enable` on a new **two-broker** staging cluster. The first client that commits an offset triggers:

```
org.apache.kafka.common.errors.InvalidReplicationFactorException: Replication factor: 3 larger than available brokers: 2.
```

Which statement correctly explains the internal-topic defaults involved?
- A. `__consumer_offsets` is created with **50** partitions and the replication factor from `offsets.topic.replication.factor` (default **3**); `__transaction_state` likewise uses **50** partitions with `transaction.state.log.replication.factor` **3** and `transaction.state.log.min.isr` **2**. On a cluster with fewer than three brokers these values must be lowered before the internal topics can be created.
- B. Internal topics are created using `num.partitions` (default 1) and `default.replication.factor` (default 1), so the error must come from an application topic instead.
- C. `__consumer_offsets` uses `cleanup.policy=delete` with a 7-day retention, so lowering `offsets.retention.minutes` avoids the error.
- D. Setting `auto.create.topics.enable=false` also blocks the creation of internal topics, so the fix is to re-enable it.

### Question 30 — `[SEC · Listeners & encryption · Single]`
An auditor requires three things: (1) all Kafka traffic encrypted in transit, **including inter-broker traffic**, (2) data encrypted **at rest**, and (3) clients authenticated by **certificate**. Which plan satisfies all three?
- A. Enabling SSL listeners also encrypts the log segments written to `log.dirs`, so requirements (1) and (2) are both covered by TLS alone.
- B. Configure `sasl.mechanism=GSSAPI`, which is how certificate-based client authentication is expressed in Kafka, and rely on it for requirement (3).
- C. Use SASL/SCRAM for requirement (3), because certificate-based client authentication is not supported on KRaft clusters.
- D. Map the client and inter-broker listeners to `SSL` in `listener.security.protocol.map`, point `inter.broker.listener.name` at that listener, set `ssl.client.auth=required` for mTLS, and satisfy the at-rest requirement with **disk or volume encryption** — Apache Kafka has no built-in encryption of log segments at rest.
