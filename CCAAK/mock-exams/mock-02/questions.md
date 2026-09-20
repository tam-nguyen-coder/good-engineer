# 🎯 CCAAK Mock Exam 02 — 60 questions · 90 minutes

> **Exam-realistic full-length mock.** Distribution follows the official CCAAK domain weights.
> ⏱️ Set a timer for **90 minutes** (~90 seconds per question). No notes, no documentation, no pausing.
> 🔒 Answers, explanations and per-domain scoring: [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (4 options) · `Multi` (choose the stated number) · `Matching` · `Ordering`.
> Tag: `[Domain · Topic · Format]`. Domains: `CFG` `FUND` `SEC` `TROUBLE` `ARCH` `CONNECT` `OBS`.
> Anchored to **Apache Kafka 4.3** — ZooKeeper was removed in 4.0; any option that relies on it is wrong.
> 🩺 **Theme of this mock: the on-call shift.** Almost every question opens with a real symptom — a verbatim log line, a CLI output, a metric reading — and asks you to reason backwards to the cause and pick the **first** action. The cheapest reversible action is usually right; the tempting wrong answer is usually the irreversible one.
> Back to [mock index](../README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[CFG · Durability under min ISR · Single]`

A six-broker, rack-aware cluster runs `payments` with `replication.factor=3` and `min.insync.replicas=2`. A top-of-rack switch fails and both brokers in rack B go offline. Producers start failing, and the leader logs:

```
[2026-09-18 03:41:22,904] ERROR [ReplicaManager broker=4] Error processing append operation on partition payments-11
org.apache.kafka.common.errors.NotEnoughReplicasException: The size of the current ISR Set(4) is insufficient to satisfy the min.isr requirement of 2 for partition payments-11
```

`OfflinePartitionsCount` is 0. Which is the FIRST action a competent administrator takes?

- A. Lower `min.insync.replicas` to 1 on `payments` with `kafka-configs.sh` so producers can write again, then raise it once the switch is repaired.
- B. Set `unclean.leader.election.enable=true` cluster-wide so a replica outside the ISR can take leadership of the affected partitions.
- C. Restore the two rack-B brokers. The partition still has a live leader on broker 4 — the only thing missing is a second in-sync replica, so nothing on the Kafka side needs changing.
- D. Raise `num.replica.fetchers` on broker 4 so its followers catch up faster.

### Question 2 — `[OBS · Broker saturation · Single]`

During the evening peak one broker reports:

```
kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent  = 0.06
kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent          = 0.71
kafka.network:type=RequestMetrics,name=TotalTimeMs,request=Produce   99th = 1840 ms
   RequestQueueTimeMs  99th = 1610 ms
   LocalTimeMs         99th =    9 ms
   RemoteTimeMs        99th =   22 ms
   ResponseQueueTimeMs 99th =    2 ms
   ResponseSendTimeMs  99th =    7 ms
```

`UnderReplicatedPartitions` is 0 across the cluster and the disks are 40 % full. What do you change?

- A. Raise `num.network.threads` above its default of 3 — 0.71 idle shows the network layer is the bottleneck.
- B. Raise `num.io.threads` above its default of 8: 1,610 ms of the 1,840 ms is spent **queued waiting for an I/O thread**, and `RequestHandlerAvgIdlePercent` of 0.06 is far under the documented 0.3 floor.
- C. Raise `queued.max.requests` above 500 so fewer produce requests are rejected while the handlers catch up.
- D. Raise `replica.lag.time.max.ms` — the 22 ms `RemoteTimeMs` shows the followers are the slow party.

### Question 3 — `[SEC · TLS hostname verification · Single]`

A new consumer service in a different subnet fails at startup. The brokers were not changed and every existing client still works.

```
org.apache.kafka.common.errors.SslAuthenticationException: SSL handshake failed
Caused by: javax.net.ssl.SSLHandshakeException: No subject alternative names present
	at sun.security.ssl.Alert.createSSLException(Alert.java:131)
	at sun.security.ssl.TransportContext.fatal(TransportContext.java:370)
```

The new service uses `bootstrap.servers=10.42.7.11:9093`; every working client uses `broker-1.kafka.internal:9093`. What is the cause and the correct fix?

- A. Hostname verification has been on by default since 2.0 and compares the address the client dialled against the certificate's SAN entries. The broker certificate carries DNS SANs but no `IP:10.42.7.11`, so connecting by IP fails. Point the new service at the DNS name that is already in the SAN list.
- B. The client truststore is missing the intermediate CA; import the full chain into the client truststore.
- C. The broker listener has `ssl.client.auth=required` and the new service has no keystore; issue it a client certificate.
- D. Set `ssl.endpoint.identification.algorithm=HTTPS` on the new client so it matches the algorithm the brokers use.

### Question 4 — `[CONNECT · Task failure triage · Single]`

```
$ curl -s localhost:8083/connectors/orders-jdbc-sink/status | jq .
{
  "name": "orders-jdbc-sink",
  "connector": { "state": "RUNNING", "worker_id": "10.0.3.14:8083" },
  "tasks": [
    { "id": 0, "state": "RUNNING", "worker_id": "10.0.3.14:8083" },
    { "id": 1, "state": "FAILED",  "worker_id": "10.0.3.15:8083",
      "trace": "org.apache.kafka.connect.errors.ConnectException: Exiting WorkerSinkTask due to unrecoverable exception.\n\tCaused by: java.sql.SQLException: ORA-00001: unique constraint (ORDERS.PK_ORDERS) violated\n" },
    { "id": 2, "state": "RUNNING", "worker_id": "10.0.3.15:8083" }
  ]
}
```

Nothing has changed for 40 minutes and a third of the partitions have not been written to since. Which statement is correct?

- A. The connector object is `RUNNING`, so the framework will restart task 1 on the next heartbeat; the 40-minute gap means the worker on `10.0.3.15` is partitioned from the group.
- B. `DELETE /connectors/orders-jdbc-sink` followed by a fresh `POST` is required, because a task that has recorded a `trace` cannot be restarted in place.
- C. `POST /connectors/orders-jdbc-sink/restart` with no query parameters is enough: restarting the connector object always cascades to its tasks.
- D. A failed **task** triggers no rebalance and is never restarted automatically — only a failed **worker** is. The task stays FAILED until `POST /connectors/orders-jdbc-sink/restart?includeTasks=true&onlyFailed=true` is called, and the duplicate-key cause must be fixed first or it will fail again.

### Question 5 — `[FUND · Node identity · Single]`

A fourth broker is added to a three-node KRaft cluster. The operator ran:

```
$ kafka-storage.sh random-uuid
q1Zt8TdmSgy8Ff8p6sQ3wA
$ kafka-storage.sh format --cluster-id q1Zt8TdmSgy8Ff8p6sQ3wA \
    --config /etc/kafka/server.properties --no-initial-controllers
```

The broker dies at startup:

```
[2026-09-19 09:02:55,118] ERROR [BrokerLifecycleManager id=4] Shutting down because of fatal error
org.apache.kafka.common.errors.InconsistentClusterIdException: The cluster ID q1Zt8TdmSgy8Ff8p6sQ3wA in the
broker's storage does not match the cluster ID Ky7sJm2CTQ6kR0lNwUeT1g reported by the controller quorum.
```

What went wrong, and what is the remedy?

- A. `kafka-storage.sh random-uuid` minted a **new** cluster id. Every node of one cluster must be formatted with the **same** `cluster.id`. Read the existing id (from a running node's `meta.properties`, or from `kafka-metadata-quorum.sh describe --status`), wipe the new broker's log directories, and re-format with that id.
- B. `--no-initial-controllers` is wrong for a broker-only node; re-format with `--standalone` so the broker registers itself with the quorum.
- C. The broker has not yet recreated its `/brokers/ids/4` ephemeral node; restart the active controller so the registration is replayed.
- D. `node.id` 4 collides with a controller id. Renumber the broker to 1004 and restart — cluster ids are derived from node ids.

### Question 6 — `[TROUBLE · Exception to root cause · Matching]`

Match each exception, exactly as the client logs it, to the condition that produced it.

| # | Exception |
|---|---|
| 1 | `org.apache.kafka.common.errors.NotEnoughReplicasException` on every `send()` to one topic while other topics are fine |
| 2 | `org.apache.kafka.common.errors.TimeoutException: Topic orders not present in metadata after 60000 ms` from a client that reached the bootstrap server without error |
| 3 | `org.apache.kafka.common.errors.OffsetOutOfRangeException` on a consumer group restarted after a long outage |
| 4 | `org.apache.kafka.clients.consumer.CommitFailedException` from a consumer whose group rebalances every few minutes |

| Letter | Condition |
|---|---|
| W | The committed position no longer exists in the log — retention deleted the segments that held it |
| X | The application spent longer than `max.poll.interval.ms` between polls, so the coordinator evicted the member before its commit landed |
| Y | The ISR of that topic's partitions is below its `min.insync.replicas`, so the leader refuses `acks=all` appends |
| Z | `advertised.listeners` returns an address the client cannot reach, so metadata never completes |

- A. 1-Y · 2-W · 3-Z · 4-X
- B. 1-Z · 2-Y · 3-X · 4-W
- C. 1-Y · 2-Z · 3-W · 4-X
- D. 1-X · 2-Z · 3-W · 4-Y

### Question 7 — `[CFG · Log directory skew · Multi — Choose 2]`

```
$ kafka-log-dirs.sh --bootstrap-server broker-3:9092 --describe --broker-list 3 \
    | jq '.brokers[0].logDirs[] | {logDir, totalBytes, usableBytes, error, partitions: (.partitions|length)}'
{ "logDir": "/data/d1", "totalBytes": 2000398934016, "usableBytes":   63887523840, "error": null, "partitions": 611 }
{ "logDir": "/data/d2", "totalBytes": 2000398934016, "usableBytes": 1402331791360, "error": null, "partitions": 118 }
```

`/data/d1` is 97 % full and growing at ~40 GB/day. `UnderReplicatedPartitions` is 0. Which **two** actions relieve the pressure **without taking the broker down**? (Choose two.)

- A. Cordon the full directory — `kafka-configs.sh --entity-type brokers --entity-name 3 --alter --add-config cordoned.log.dirs=/data/d1` — so the controller stops placing **new** partitions there while you work.
- B. Delete the oldest `.log` segment files under `/data/d1` with `rm`, then restart the broker so it re-reads the directory.
- C. Set `log.retention.bytes` on the brokers to cap every partition; the new value applies to partitions already on disk within `log.retention.check.interval.ms`.
- D. Move a batch of partitions from `/data/d1` to `/data/d2` with `kafka-reassign-partitions.sh`, using a plan whose `log_dirs` array names the destination directory, throttled with `--replica-alter-log-dirs-throttle`.
- E. Remove `/data/d1` from `log.dirs` and restart the broker; Kafka re-replicates its partitions from the other replicas.

### Question 8 — `[ARCH · DR mechanism selection · Single]`

A failover drill on the DR cluster, fed by MirrorMaker 2, took three hours: every consumer group had to be repointed and its offsets translated, and two teams replayed hours of duplicates because `orders` is called `prod.orders` on the DR side. Both sides run **Confluent Server**. Management wants the next drill under 15 minutes at the same RPO. What do you propose?

- A. Keep MM2 but set `sync.group.offsets.enabled=true` and `replication.policy.class` to `IdentityReplicationPolicy`, so topic names and offsets line up.
- B. Replace MM2 with **Cluster Linking**: the destination brokers pull directly from the source, mirror topics keep the source **name** and byte-for-byte **offsets**, and consumer offsets and ACLs are synced — so failover is a promote plus a client repoint, with no offset translation and no Connect fleet to operate.
- C. Stretch the existing cluster across both sites with `broker.rack` per site and `min.insync.replicas=2`, removing the failover step entirely.
- D. Run MirrorMaker 1 in the DR direction; unlike MM2 it does not rename topics and therefore needs no offset translation.

### Question 9 — `[OBS · Early-warning metrics · Single]`

A nightly batch group's `records-lag-max` has always oscillated between 200k and 2M, which the team considers normal. Overnight, `records-lead-min` on three of its 24 partitions fell from ~9,000,000 to under 50,000 and is still dropping. `UnderReplicatedPartitions` is 0, no exception has been logged, and every partition is assigned. What is about to happen, and what do you do first?

- A. Nothing is wrong — `records-lead-min` falling means the consumer is catching up with the head of the log.
- B. The group is about to be evicted for exceeding `max.poll.interval.ms`; lower `max.poll.records`.
- C. Those partitions are about to **lose unread data**. `records-lead-min` is the distance from the consumer's position to the **log start offset**, so a value near 0 means retention is deleting records the group has not read. The immediate, reversible action is to raise `retention.ms` on that topic to buy time, then fix the consumer's throughput.
- D. The three partitions have a hot key; add partitions so the load spreads.

### Question 10 — `[SEC · Group authorization · Single]`

A new consumer authenticates fine over SASL_SSL and can read with `kafka-console-consumer.sh --topic billing-events --partition 0 --offset earliest`, but the application dies at startup:

```
org.apache.kafka.common.errors.GroupAuthorizationException: Not authorized to access group: billing-reconciler
```

`kafka-acls.sh --list --topic billing-events` shows `Read` and `Describe` allowed for `User:billing-svc`. What is missing?

- A. `Read` on the **Group** resource: `kafka-acls.sh --add --allow-principal User:billing-svc --operation Read --group billing-reconciler`. The console consumer worked because `--partition` makes it a standalone `assign()` consumer, which joins no group and therefore needs no Group ACL.
- B. `Describe` on the **Cluster** resource, which the coordinator lookup requires before a group can be joined.
- C. `Write` on `__consumer_offsets`, so the member can commit; Group ACLs are derived from that topic's ACLs.
- D. The group must be listed in `allow.everyone.if.no.acl.found`; add `billing-reconciler` to that broker property and restart.

### Question 11 — `[CFG · Eligible Leader Replicas · Single]`

A cluster created new on Kafka 4.3 with default features, `unclean.leader.election.enable=false`:

```
$ kafka-topics.sh --bootstrap-server broker-1:9092 --describe --topic settlements
Topic: settlements  TopicId: 5xQm...  PartitionCount: 6  ReplicationFactor: 3  Configs: min.insync.replicas=2
	Topic: settlements  Partition: 3  Leader: none  Replicas: 2,5,8  Isr:   Elr: 5  LastKnownElr: 2
```

Broker 5 has just come back online and is unfenced. Broker 2 (the previous leader) is still down; broker 8 has been offline for a day. `OfflinePartitionsCount` is 1. What happens, and what should the operator do?

- A. Nothing can happen until broker 2 returns — only the last known leader may take over when the ISR is empty. Enable `unclean.leader.election.enable` if the outage cannot wait.
- B. The controller elects broker **5** from the **ELR**. The strict-min-ISR rule guarantees an ELR member holds every committed record, so this is a clean election with no data loss. Let it complete, then restore brokers 2 and 8; no config change is needed.
- C. Run `kafka-leader-election.sh --election-type unclean --topic settlements --partition 3`, because ELR members are only candidates and are never elected automatically.
- D. `Elr: 5` means broker 5 is **excluded** from election until its replica is re-synced with `kafka-reassign-partitions.sh`.

### Question 12 — `[TROUBLE · Lag diagnosis · Ordering]`

A consumer group's lag has climbed steadily for 40 minutes. Put the diagnostic steps in the order that spends the least and learns the most first.

| # | Step |
|---|---|
| 1 | Add consumers up to the partition count; if the group is already at that ceiling, increase the topic's partition count |
| 2 | Compare per-partition lag — every partition behind points at the consumers or the brokers, one partition behind points at a hot key |
| 3 | Check `RequestHandlerAvgIdlePercent` and the `TotalTimeMs` breakdown on the brokers leading those partitions, to decide whether the cluster or the application is slow |
| 4 | Run `kafka-consumer-groups.sh --describe --group g --state` and `--members` to confirm the group has live members and is not stuck rebalancing |

- A. 2 → 4 → 1 → 3
- B. 4 → 3 → 2 → 1
- C. 3 → 4 → 2 → 1
- D. 4 → 2 → 3 → 1

### Question 13 — `[CONNECT · Silent data loss · Multi — Choose 2]`

An S3 sink has been `RUNNING` for six weeks with no failed tasks and no alerts. An audit finds ~0.4 % of records never reached S3. The connector configuration contains:

```json
"errors.tolerance": "all",
"errors.log.enable": "false",
"errors.retry.timeout": "0"
```

Which **two** statements are correct? (Choose two.)

- A. `errors.tolerance=none` would have routed the bad records to the connector's `__connect_errors` topic automatically.
- B. `errors.tolerance=all` with no dead letter queue makes Connect **discard** every record that fails conversion, transformation or delivery — and with `errors.log.enable=false` it does so without a log line. That is exactly why the task stayed `RUNNING` and nothing alerted.
- C. Adding `errors.deadletterqueue.topic.name` together with `errors.deadletterqueue.context.headers.enable=true` captures the failing records **and** the reason they failed; without the headers flag the DLQ holds the payload but not the cause.
- D. `errors.retry.timeout=0` is what discards the records; setting it to `-1` retries them until they succeed, which removes the loss.
- E. `total-records-skipped` in `task-error-metrics` would have shown the loss, but it is published only for **source** connectors.

### Question 14 — `[FUND · Controller quorum · Single]`

`kafka-topics.sh --create` hangs, but the payments service produces and consumes normally.

```
$ kafka-metadata-quorum.sh --bootstrap-controller controller-1:9093 describe --status
ClusterId:              Ky7sJm2CTQ6kR0lNwUeT1g
LeaderId:               -1
LeaderEpoch:            412
HighWatermark:          -1
MaxFollowerLag:         -1
CurrentVoters:          [{"id": 3001, ...}, {"id": 3002, ...}, {"id": 3003, ...}]
CurrentObservers:       [{"id": 1, ...}, {"id": 2, ...}, {"id": 3, ...}, {"id": 4, ...}]
```

Controllers 3002 and 3003 are unreachable. Which reading is correct?

- A. `LeaderId: -1` means the quorum has no elected leader. With 2 of 3 voters down there is no majority, so the **control plane is frozen** — no topic creation, no new leader elections, no broker registration — while the **data plane** keeps serving partitions whose leaders have not changed, from each broker's already-applied metadata. Restore a second controller to regain the majority.
- B. The brokers under `CurrentObservers` are misconfigured: a broker must be a voter to serve traffic, which is why metadata operations fail.
- C. `LeaderId: -1` is normal during an election; the create hung only because `controller.quorum.election.timeout.ms` (1000 ms) is too low for this network. Raise it and retry.
- D. Controller 3001 promotes itself once `controller.quorum.fetch.timeout.ms` (2000 ms) expires; the cluster is self-healing and no action is needed.

### Question 15 — `[CFG · Tiered storage · Single]`

Finance asked for 400 days of `audit-trail`. The team set `remote.log.storage.system.enable=true` on every broker with the three required manager properties, then ran:

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type topics --entity-name audit-trail \
    --alter --add-config remote.storage.enable=true,retention.ms=34560000000
```

Six weeks later objects **are** appearing in the object store, but broker disk usage for `audit-trail` has not dropped at all. What is wrong?

- A. Segments are copied to remote storage but deleted locally only after `log.retention.check.interval.ms` × the segment count; the disk will drain on its own.
- B. `local.retention.ms` was never set. Its default is **-2**, meaning "inherit the total retention", so the local tier is also keeping 400 days. Set `local.retention.ms` (or `local.retention.bytes`) to a small value such as a few hours.
- C. `remote.log.storage.system.enable` is read-only and the brokers were never restarted; the objects in the store were written by a different topic.
- D. The topic must also set `cleanup.policy=compact,delete` before the remote tier takes ownership of closed segments.

### Question 16 — `[CFG · ELR and min ISR · Single]`

A cluster was upgraded 4.0 → 4.3. Every broker's `server.properties` has carried `min.insync.replicas=2` for years. Last week the team finalized the ELR feature (`eligible.leader.replicas.version=1`). A durability audit now reports that topics which never had a topic-level override are accepting `acks=all` writes with a single replica in sync.

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type topics \
    --entity-name clickstream --describe --all | grep min.insync
  min.insync.replicas=1 sensitive=false synonyms={DEFAULT_CONFIG:min.insync.replicas=1}
```

What happened, and what is the remedy?

- A. `--describe --all` prints the shipped default rather than the effective value; the topic really is at 2. Re-run the command without `--all` to see the truth.
- B. Finalizing a feature flag resets topic-level configuration to defaults. Restore the topic configs from the last `kafka-configs.sh --describe` snapshot taken before the upgrade.
- C. Enabling ELR **removes `min.insync.replicas` as a broker-level property**. It must now be set at the **cluster** level (`--entity-type brokers --entity-default`) or per topic; anything that relied on each broker's `server.properties` value silently fell back to the default of 1. Set it at cluster level, then re-audit every topic.
- D. ELR supersedes `min.insync.replicas`: the controller now guarantees that no committed record is lost, so an effective value of 1 is harmless and the audit finding can be closed.

### Question 17 — `[TROUBLE · Rebalance loop · Single]`

A consumer group processes images by calling an external API. That API slowed down last night and now takes 4–9 s per image. CPU on the six consumer hosts is 18 %.

```
$ kafka-consumer-groups.sh --bootstrap-server broker-1:9092 --describe --group image-resizer --state
GROUP          COORDINATOR (ID)    ASSIGNMENT-STRATEGY  STATE                #MEMBERS
image-resizer  broker-3:9092 (3)   range                PreparingRebalance   6
```

Thirty seconds later the same command prints `CompletingRebalance`, then `PreparingRebalance` again. On the consumers:

```
[2026-09-19 14:08:31,442] WARN [Consumer clientId=img-4, groupId=image-resizer] consumer poll timeout has expired.
This means the time between subsequent calls to poll() was longer than the configured max.poll.interval.ms,
which typically implies that the poll loop is spending too much time processing messages.
```

What is the FIRST action?

- A. Increase the topic from 6 to 24 partitions so each consumer handles fewer records per poll.
- B. Lower `max.poll.records` (default 500) so one batch finishes well inside `max.poll.interval.ms` (default 300,000 ms), and raise that interval if the work genuinely needs longer. The group is evicting itself, not failing.
- C. Raise `session.timeout.ms` and `heartbeat.interval.ms`; the members are being declared dead between heartbeats.
- D. Restart broker 3 so a new coordinator takes over and the stuck rebalance clears.

### Question 18 — `[SEC · Prefixed ACLs · Single]`

Every service of one tenant authenticates as `User:team-ads`. Nine topics named `ads.<something>` work. A tenth, `ads_dlq`, fails:

```
org.apache.kafka.common.errors.TopicAuthorizationException: Not authorized to access topics: [ads_dlq]
```

```
$ kafka-acls.sh --bootstrap-server broker-1:9092 --list --principal User:team-ads
Current ACLs for resource `ResourcePattern(resourceType=TOPIC, name=ads., patternType=PREFIXED)`:
	(principal=User:team-ads, host=*, operation=READ, permissionType=ALLOW)
	(principal=User:team-ads, host=*, operation=WRITE, permissionType=ALLOW)
	(principal=User:team-ads, host=*, operation=DESCRIBE, permissionType=ALLOW)
```

What is the cause and the minimal fix?

- A. A `PREFIXED` pattern is evaluated as a regular expression, so `.` used to match any character; 4.0 tightened it. Re-add the ACL with `--resource-pattern-type literal` for `ads_dlq`.
- B. `allow.everyone.if.no.acl.found` is `true` by default, which is why the nine `ads.` topics work at all. Set it to `false` and write explicit ACLs for all ten topics.
- C. The principal is missing `Describe` on the **Cluster** resource, which the client needs before any topic name can be resolved.
- D. The prefix is the literal string `ads.` — including the dot. `ads_dlq` does not start with it, no ACL matches, and the default is to deny. Either rename the topic to `ads.dlq` so the tenant's single prefixed ACL covers it, or add one literal ACL for `ads_dlq`.

### Question 19 — `[FUND · Controller election · Single]`

The active controller node (3001) is powered off during a rack move. A few seconds later:

```
$ kafka-metadata-quorum.sh --bootstrap-controller controller-2:9093 describe --status
ClusterId:      Ky7sJm2CTQ6kR0lNwUeT1g
LeaderId:       3002
LeaderEpoch:    77
HighWatermark:  9481233
CurrentVoters:  [{"id": 3001, ...}, {"id": 3002, ...}, {"id": 3003, ...}]
```

Partition leaders did not move for any topic whose leaders were already on healthy brokers. Which statement describes what happened?

- A. The surviving controllers raced to recreate the `/controller` ephemeral node and 3002 won the race; that is how a new controller is chosen.
- B. A majority of the **voters** elected 3002 as **Raft leader** of the metadata log; it then became the active controller using the log it had already replicated. Moving a **partition** leader is a different decision that the controller makes separately, which is why nothing moved for partitions whose leaders were still alive.
- C. The broker with the lowest `node.id` takes over the controller role until 3001 returns.
- D. Every controller reports `ActiveControllerCount=1` once a leader exists; the metric is per node, so summing it across the cluster is meaningless.

### Question 20 — `[OBS · Alert triage · Single]`

One page fires at 02:14 carrying four readings:

```
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions       = 61
kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount       = 7
kafka.controller:type=KafkaController,name=OfflinePartitionsCount     = 0
kafka.controller:type=KafkaController,name=ActiveControllerCount (sum)= 1
```

Which reading should drive the next five minutes?

- A. `UnderReplicatedPartitions = 61` — it is by far the largest number, so it is the biggest problem.
- B. `OfflinePartitionsCount = 0` — every partition still has a leader, so nothing is actually broken; downgrade the page to a ticket and look at it in the morning.
- C. `UnderMinIsrPartitionCount = 7` — those seven partitions have an ISR below their `min.insync.replicas`, so every `acks=all` producer writing to them is **being rejected right now**. `OfflinePartitionsCount = 0` says reads are fine and `ActiveControllerCount = 1` rules out the control plane. Identify those seven partitions and restore a replica.
- D. `ActiveControllerCount (sum) = 1` — on a three-controller cluster this should be 3; the quorum has lost two controllers.

### Question 21 — `[CONNECT · Distributed REST behaviour · Single]`

A deployment pipeline posts a new connector to whichever worker the load balancer picks:

```
$ curl -s -w '\n%{http_code}\n' -X POST http://connect-2:8083/connectors \
    -H 'Content-Type: application/json' -d @s3-sink.json
{"error_code":409,"message":"Cannot complete request momentarily due to no known leader URL"}
409
```

A retry twenty seconds later succeeds, and the connector runs normally afterwards. Which explanation is correct?

- A. Write operations must be sent to the leader worker. `connect-2` is a follower and cannot forward them, so the pipeline must first resolve the leader from `GET /`.
- B. In distributed mode **any** worker accepts the request and forwards writes to the group leader. A `409` means the worker group was **rebalancing** at that instant and had no leader to forward to. It is transient; the correct handling is a bounded retry with backoff, not a change to the topology.
- C. `409 Conflict` means a connector with that name already exists. The pipeline must `DELETE` it before posting again.
- D. `connect-2` has a different `group.id` from the other workers, so it belongs to no Connect cluster and has no leader. Align `group.id` across all workers.

### Question 22 — `[CFG · Retention sizing · Single]`

A team set `retention.bytes=107374182400` (100 GB) on `telemetry`, expecting the topic to stop growing at 100 GB. Two weeks later `/data` is 93 % full and the topic alone accounts for roughly 4.8 TB across the cluster.

```
$ kafka-topics.sh --bootstrap-server broker-1:9092 --describe --topic telemetry | head -1
Topic: telemetry  TopicId: pQ2...  PartitionCount: 48  ReplicationFactor: 3  Configs: retention.bytes=107374182400,retention.ms=604800000
```

What went wrong?

- A. `retention.bytes` is a **per-partition** limit applied to **each replica**, not a topic-wide budget. 48 partitions × 3 replicas × 100 GB is up to 14.4 TB of stored replicas. Divide the intended topic budget by the partition count and set that, or control the size with `retention.ms` instead.
- B. When both `retention.bytes` and `retention.ms` are set, only the time limit is enforced; the size limit is ignored.
- C. `log.retention.check.interval.ms` is 300,000 ms, so deletion runs only every five minutes and cannot keep up with this ingest rate. Lower it to 10,000 ms.
- D. Delete the oldest `.log` files under the topic's directories with `rm` and restart each broker so it re-reads the directory.

### Question 23 — `[ARCH · Controller placement · Single]`

A cluster is being designed across two availability zones: six brokers (3 + 3) and three controllers. The draft places controllers 3001 and 3002 in AZ-A and 3003 in AZ-B, with the note *"we can afford to lose AZ-B"*. Which assessment is correct?

- A. The draft is correct as drawn. A three-voter quorum tolerates one failure, and AZ-B holds exactly one voter.
- B. Use four controllers, two per AZ. An even number lets each zone keep half the quorum, so either zone can be lost.
- C. Set `unclean.leader.election.enable=true` so the surviving zone can keep electing leaders whichever AZ is lost; the controller placement then does not matter.
- D. The draft survives the loss of AZ-B but **not** the loss of AZ-A, which removes 2 of 3 voters and freezes the control plane — no leader elections, no topic administration, no broker registration. A three-voter quorum cannot be made zone-fault-tolerant across only **two** zones. Put the controllers in three failure domains (a controller-only node is small — roughly 5 GB RAM and 5 GB disk), or document AZ-A as a single point of failure and accept it deliberately.

### Question 24 — `[TROUBLE · ISR flapping · Multi — Choose 2]`

```
kafka.server:type=ReplicaManager,name=IsrShrinksPerSec (broker 5, 1-min rate)  = 0.42
kafka.server:type=ReplicaManager,name=IsrExpandsPerSec (broker 5, 1-min rate)  = 0.41
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions (broker 5)     = 0 → 18 → 0 → 22
```

Broker 5 was given a 48 GB heap when it was commissioned. Its GC log shows `Pause Full (G1 Compaction Pause)` entries of **25–41 s** roughly every two minutes. Disk `await` on its data volumes is 1.8 ms and the NIC runs at 20 % of line rate. No other broker flaps. Which **two** statements are correct? (Choose two.)

- A. Broker 5's JVM is stalling. During a stop-the-world pause it neither serves follower fetches nor issues its own, so its replicas fall out of the ISR and rejoin when the pause ends. The fix is the heap: Kafka relies on the page cache, and the working recommendation is roughly a **6 GB** heap with **G1GC**, leaving the rest of the RAM to the OS.
- B. Raise `replica.lag.time.max.ms` from 30,000 ms to 120,000 ms so the flapping stops appearing in the metrics.
- C. A follower is judged by the **time** since it was last caught up (`replica.lag.time.max.ms`, default 30,000 ms), not by an offset distance — so a pause longer than that window ejects a replica that was byte-for-byte current a moment earlier.
- D. Raise `num.replica.fetchers` on broker 5 so its fetcher threads can outrun the pauses.
- E. Enable `unclean.leader.election.enable` so the affected partitions always keep a leader while the ISR churns.

### Question 25 — `[SEC · SASL mechanisms · Matching]`

Match each SASL mechanism to where the credential the broker checks actually lives.

| # | Mechanism |
|---|---|
| 1 | `PLAIN` |
| 2 | `SCRAM-SHA-512` |
| 3 | `GSSAPI` |
| 4 | `OAUTHBEARER` |

| Letter | Where the credential lives |
|---|---|
| W | In the cluster's own metadata; created, rotated and revoked online with `kafka-configs.sh --entity-type users`, with nothing to restart |
| X | In a static JAAS entry on every broker (or `listener.name.<l>.plain.sasl.jaas.config`) — adding or removing a user is a broker configuration change |
| Y | In a Kerberos KDC; the broker authenticates itself from a keytab and never handles the user's password |
| Z | With an external identity provider; the broker validates a signed token and derives the principal from a claim inside it |

- A. 1-W · 2-X · 3-Y · 4-Z
- B. 1-X · 2-W · 3-Z · 4-Y
- C. 1-X · 2-W · 3-Y · 4-Z
- D. 1-Y · 2-Z · 3-W · 4-X

### Question 26 — `[CFG · Log compaction · Multi — Choose 2]`

`customer-state` is a compacted topic with 3 partitions. The application rewrites the same ~200,000 keys all day, and the topic has grown for months without the cleaner ever reclaiming anything.

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type topics \
    --entity-name customer-state --describe --all | grep -E 'cleanup|cleanable|segment.bytes'
  cleanup.policy=compact sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:cleanup.policy=compact, DEFAULT_CONFIG:log.cleanup.policy=delete}
  min.cleanable.dirty.ratio=0.5 sensitive=false synonyms={DEFAULT_CONFIG:min.cleanable.dirty.ratio=0.5}
  segment.bytes=1073741824 sensitive=false synonyms={DEFAULT_CONFIG:log.segment.bytes=1073741824}
```

Which **two** changes will make the cleaner reclaim space? (Choose two.)

- A. Change `cleanup.policy` to `compact,delete` and add a `retention.ms`, so old records are removed on a timer.
- B. Lower `segment.bytes` (or set `segment.ms`) so the active segment rolls more often. The **active segment is never compacted**, and with a 1 GiB segment a moderate-volume partition can keep months of updates inside it, permanently out of the cleaner's reach.
- C. Raise `log.cleaner.threads` above its default of 1 so the cleaner keeps up with three partitions.
- D. Lower `min.cleanable.dirty.ratio` from its default of 0.5 to, say, 0.1, so a partition becomes eligible for cleaning when only 10 % of the log is dirty instead of 50 %.
- E. Set `min.compaction.lag.ms` to 0 so records become eligible immediately.

### Question 27 — `[FUND · Partition count change · Single]`

During a lag incident an operator doubled `orders` from 12 to 24 partitions. Lag cleared within the hour. The next morning the downstream state store shows customers whose **old** address has overwritten their **new** one.

What happened, and what is the way out?

- A. Kafka orders records per **partition**, and the default partitioner maps a keyed record with `hash(key) % numPartitions`. Raising the partition count re-maps keys, so a given customer's history now lives in two partitions consumed by two different consumers with no ordering between them. Adding partitions is **one-way**. The way out is a new topic with the intended partition count plus a migration — not an attempt to shrink this one.
- B. The consumer group rebalanced while the partition count changed, and the range assignor handed the same partition to two members at once; a restart of the group restores ordering.
- C. The producer has `enable.idempotence=false` and `max.in.flight.requests.per.connection=5`, so a retry reordered two batches on the same partition.
- D. Shrink the topic back with `kafka-topics.sh --alter --partitions 12`; the key mapping is restored and the state store self-heals on the next full replay.

### Question 28 — `[TROUBLE · Stalled reassignment · Single]`

A reassignment moving 340 partitions onto three new brokers started nine hours ago. The partitions average 180 GB.

```
$ kafka-reassign-partitions.sh --bootstrap-server broker-1:9092 \
    --reassignment-json-file plan.json --verify
Status of partition reassignment:
Reassignment of partition clickstream-17 is still in progress.
Reassignment of partition clickstream-18 is still in progress.
Reassignment of partition clickstream-19 is still in progress.
...
```

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type brokers --entity-name 7 --describe
Dynamic configs for broker 7 are:
  follower.replication.throttled.rate=1048576 sensitive=false synonyms={DYNAMIC_BROKER_CONFIG:follower.replication.throttled.rate=1048576}
  leader.replication.throttled.rate=1048576 sensitive=false synonyms={DYNAMIC_BROKER_CONFIG:leader.replication.throttled.rate=1048576}
```

`UnderReplicatedPartitions` sits at 340 and is steady; no broker has failed and the network is idle. What is the FIRST action?

- A. Cancel the reassignment with `--cancel` and re-run it with no throttle at all, so the move finishes tonight.
- B. 340 under-replicated partitions means the new brokers are failing to keep up because they are unhealthy; restart brokers 7, 8 and 9.
- C. Raise the throttle. At 1,048,576 B/s — 1 MiB/s per broker — moving 180 GB partitions takes weeks. Set `leader.replication.throttled.rate` and `follower.replication.throttled.rate` with `kafka-configs.sh` to a rate the disks and network can actually absorb; the in-flight reassignment picks the new value up without any restart.
- D. `--verify` removes the throttles as part of its run, so throttling cannot be the cause any more. Raise `num.replica.fetchers` on the destination brokers instead.

### Question 29 — `[OBS · Fetch latency phases · Multi — Choose 2]`

```
kafka.network:type=RequestMetrics,name=TotalTimeMs,request=Fetch   99th = 512 ms
   RequestQueueTimeMs  99th =   3 ms
   LocalTimeMs         99th =   2 ms
   RemoteTimeMs        99th = 498 ms
   ResponseQueueTimeMs 99th =   1 ms
   ResponseSendTimeMs  99th =   4 ms
```

Consumers report no problem whatsoever. `RequestHandlerAvgIdlePercent` is 0.78 and `UnderReplicatedPartitions` is 0. Which **two** statements are correct? (Choose two.)

- A. On a **Fetch** request, `RemoteTimeMs` is the time the request waited in purgatory for `fetch.min.bytes` worth of data to accumulate, bounded by the consumer's `fetch.max.wait.ms` (default 500 ms). A 99th percentile of 498 ms on a partly idle topic is the expected shape, not a fault.
- B. The same phase means something different on a **Produce** request, where it is the wait for followers to acknowledge under `acks=all`. `TotalTimeMs` phases must always be read together with the request type.
- C. `RemoteTimeMs` always measures a read from **remote (tiered) storage**; disable `remote.storage.enable` on this topic to bring the latency down.
- D. Raise `num.network.threads`: 498 ms of the 512 ms is spent outside the I/O thread, which is the network layer's responsibility.
- E. Lower `replica.fetch.wait.max.ms` from 500 ms to 50 ms so brokers stop parking fetch requests.

### Question 30 — `[CFG · Segment sizing · Single]`

A nightly compaction-probe script that has run unchanged since 3.6 fails on a freshly upgraded 4.3 cluster:

```
$ kafka-topics.sh --bootstrap-server broker-1:9092 --create --topic compaction-probe \
    --partitions 1 --replication-factor 3 \
    --config segment.bytes=4096 --config cleanup.policy=compact
Error while executing topic command : Invalid value 4096 for configuration segment.bytes: Value must be at least 1048576
```

What is the cause, and what is the correct response?

- A. A topic must exist before `segment.bytes` can be applied. Create it with defaults, then set the value with `kafka-configs.sh --alter`.
- B. Kafka **4.3 raised the minimum allowed `segment.bytes` from 14 bytes to 1 MiB**. The script's trick of using a tiny segment to force a roll is no longer legal. Rewrite the probe to roll the active segment with `segment.ms`, or to write at least 1 MiB.
- C. `segment.bytes` is a broker-only property; at topic level only `log.segment.bytes` is accepted.
- D. Compaction requires `min.cleanable.dirty.ratio` to be lowered before small segments are accepted; set it to 0.01 and retry.

### Question 31 — `[ARCH · MirrorMaker 2 topology · Single]`

Two clusters, `dc1` and `dc2`, run MirrorMaker 2 in **both** directions for active/active. To stop the DR team complaining about the `dc1.` prefix on mirrored topics, an engineer set `replication.policy.class=org.apache.kafka.connect.mirror.IdentityReplicationPolicy` on both flows. Within minutes both clusters' disks began filling and `orders` grew without bound on both sides.

What happened?

- A. `IdentityReplicationPolicy` keeps the source topic name, so `dc1`'s `orders` lands in `dc2` as `orders`, which the reverse flow then copies back into `dc1` as `orders` — an endless loop. The renaming done by `DefaultReplicationPolicy` is exactly what lets MM2 recognise an already-mirrored topic and not mirror it again. Keep `DefaultReplicationPolicy` for bidirectional replication; `IdentityReplicationPolicy` is only safe on a strictly **one-way** flow.
- B. Retention settings are not mirrored, so the destination topics were created with infinite retention. Set `sync.topic.configs.enabled=true` on both flows.
- C. `sync.topic.configs.enabled` copied `retention.ms=-1` from a misconfigured source topic to every mirrored topic on both sides.
- D. MirrorMaker 2 deduplicates mirrored records by header, so an endless loop is impossible; the growth must come from a producer that is writing to both clusters.

### Question 32 — `[SEC · mTLS rollout · Multi — Choose 2]`

A cluster runs `SSL` listeners for encryption only; `ssl.client.auth` has never been set. The security team wants client-certificate authentication for roughly 200 applications owned by 14 teams, with no outage. Which **two** statements are correct? (Choose two.)

- A. The default is `ssl.client.auth=none`, so today every client is authenticated as `User:ANONYMOUS`. The moment an authorizer is switched on, ACLs written against real principals would deny everyone.
- B. `ssl.client.auth=required` can be rolled out immediately: clients without a keystore simply fall back to the `requested` behaviour and keep working.
- C. `ssl.client.auth` is a client-side property; each application decides for itself whether to present a certificate.
- D. `ssl.client.auth=requested` is the right **migration** state: clients that already have a keystore authenticate with their real principal while the rest keep connecting. It is not an end state — the docs call it a *"false sense of security"*, because a misconfigured client still gets in as `ANONYMOUS`.
- E. `ssl.endpoint.identification.algorithm` must be set to the empty string on the brokers before client certificates can be validated.

### Question 33 — `[CONNECT · Worker cluster identity · Multi — Choose 2]`

A second Connect cluster was stood up for a new team by copying the first cluster's `connect-distributed.properties` and changing only `rest.port`. Both worker sets now list each other's connectors in `GET /connectors`, and a connector deployed by one team was rebalanced onto the other team's workers. Which **two** statements are correct? (Choose two.)

- A. Giving the second worker set a different `rest.port` is enough to separate two Connect clusters running on the same hosts; the symptom must have another cause.
- B. A Connect cluster's identity is its `group.id` **together with** its three internal topics (`config.storage.topic`, `offset.storage.topic`, `status.storage.topic`). Sharing them makes the two worker sets one cluster, whatever host or port they run on.
- C. `config.storage.topic` must have exactly **one** partition; `offset.storage.topic` defaults to **25** partitions and `status.storage.topic` to **5**, and all three must be **compacted**. The second cluster needs its own set.
- D. Changing only `group.id` on the second worker set, while leaving the internal topic names identical, is a complete separation.
- E. The internal topics should use `cleanup.policy=delete` with a seven-day retention so obsolete connector configurations are cleaned up automatically.

### Question 34 — `[FUND · Broker fencing · Multi — Choose 2]`

A broker's host loses network connectivity for twelve seconds during a switch upgrade. The broker process itself never dies.

```
[2026-09-19 22:41:08,551] INFO [BrokerLifecycleManager id=6] Unable to send a heartbeat because the RPC got timed out before it could be sent.
[2026-09-19 22:41:17,602] WARN [BrokerLifecycleManager id=6] Broker 6 sent a heartbeat request but received error BROKER_ID_NOT_REGISTERED
```

Which **two** statements are correct? (Choose two.)

- A. A broker heartbeats the controller quorum every `broker.heartbeat.interval.ms` (default 2,000 ms). If the controller sees no heartbeat for `broker.session.timeout.ms` (default 9,000 ms) it **fences** the broker: the broker is dropped from every ISR and loses all of its leaderships.
- B. When the session lapses the broker's `/brokers/ids/6` ephemeral node disappears, and the broker recreates it when the network returns.
- C. Raise `broker.session.timeout.ms` to 60,000 ms cluster-wide so that brief network blips can never fence a broker again.
- D. Fencing also removes the node from the controller quorum, so the quorum temporarily drops from three voters to two.
- E. A fenced broker must re-register and then catch its replicas back up before it rejoins the ISRs, which is why `UnderReplicatedPartitions` stays above 0 for a while **after** the network has recovered.

### Question 35 — `[TROUBLE · Log directory failure · Ordering]`

```
$ kafka-log-dirs.sh --bootstrap-server broker-4:9092 --describe --broker-list 4 \
    | jq '.brokers[0].logDirs[] | {logDir, error}'
{ "logDir": "/data/d2", "error": "org.apache.kafka.common.errors.KafkaStorageException" }
{ "logDir": "/data/d1", "error": null }
{ "logDir": "/data/d3", "error": null }
```

Broker 4 is still running and still serving the partitions on `d1` and `d3`. `UnderReplicatedPartitions` is 96 and every affected partition still has two healthy replicas elsewhere. Put the recovery steps in the safest order.

| # | Step |
|---|---|
| 1 | Start the broker and let it re-replicate the lost directory's partitions from their leaders, with a throttle if the cluster is busy |
| 2 | Confirm that every partition which lived on `/data/d2` still has at least `min.insync.replicas` in-sync replicas elsewhere, before touching this broker at all |
| 3 | Shut the broker down with controlled shutdown so its remaining leaderships move cleanly to other replicas |
| 4 | Replace the failed disk, recreate the mount point, and format the empty directory with the cluster's existing id (`kafka-storage.sh format --ignore-formatted`) so it carries a valid `meta.properties` |

- A. 3 → 4 → 1 → 2
- B. 2 → 4 → 3 → 1
- C. 2 → 3 → 4 → 1
- D. 4 → 3 → 1 → 2

### Question 36 — `[CFG · Startup recovery · Single]`

After a data-centre power cut, broker 2 (12 × 4 TB JBOD, about 9,000 partition replicas) takes 71 minutes to reach `started`:

```
[2026-09-20 04:12:03,881] INFO [LogLoader partition=events-233, dir=/data/d7] Recovering unflushed segment 4718592000 (kafka.log.LogLoader)
[2026-09-20 04:12:04,402] INFO [LogLoader partition=events-234, dir=/data/d7] Recovering unflushed segment 4718592000 (kafka.log.LogLoader)
...
[2026-09-20 05:23:44,120] INFO [KafkaServer id=2] started (kafka.server.KafkaServer)
```

`num.recovery.threads.per.data.dir` appears nowhere in `server.properties`. Which change shortens the next unclean start the most, and what must you know about it?

- A. Set `log.flush.interval.messages=1` so segments are always flushed to disk and there is nothing to recover after a crash.
- B. Lower `log.segment.bytes` so each segment that has to be recovered is smaller.
- C. `num.recovery.threads.per.data.dir` defaults to **1** and applies to the broker as a whole, so raising it to 24 gives the broker 24 recovery threads across all directories.
- D. Raise `num.recovery.threads.per.data.dir`. It defaults to **2** in 4.x (it was 1 before 4.0) and is counted **per log directory**, so with 12 directories this broker already recovers 24 segments in parallel; setting it to 8 gives 96. The value matters only during start-up, so apply it and pick it up on the next planned roll.

### Question 37 — `[SEC · Enabling the authorizer · Single]`

A team set `authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer` on every node and began a rolling restart. The first broker came back and replication to it stopped:

```
[2026-09-19 10:02:11,704] ERROR [ReplicaFetcher replicaId=2, leaderId=1, fetcherId=0] Error for partition orders-4
org.apache.kafka.common.errors.ClusterAuthorizationException: Request Request(processor=3,
  connectionId=10.0.1.11:9094-10.0.1.12:51820-7, listenerName=ListenerName(INTERNAL),
  principal=User:CN=broker-2,OU=Platform,O=Acme,C=VN) is not authorized.
```

What was skipped, and what is the fix?

- A. Set `allow.everyone.if.no.acl.found=true`. It exempts every principal on resources that already have ACLs as well, so inter-broker traffic will flow again immediately.
- B. `StandardAuthorizer` stores its ACLs in ZooKeeper; add `zookeeper.connect` to the broker configuration and restart.
- C. With an authorizer enabled and `allow.everyone.if.no.acl.found` at its default of `false`, **every** principal needs an explicit grant — including the brokers and controllers themselves. The inter-broker principal must be in `super.users` (semicolon-separated, because DNs contain commas) or hold `ClusterAction` on the Cluster resource, and that must be in place **before** the authorizer is switched on.
- D. Roll the cluster back to `AclAuthorizer`, which exempts inter-broker traffic automatically, and plan the migration to `StandardAuthorizer` separately.

### Question 38 — `[OBS · JMX object names · Matching]`

A Prometheus JMX exporter rule set matches only `kafka.controller:type=KafkaController,name=(.+)` and `kafka.server:type=ReplicaManager,name=(.+)`. Two alerts have never fired even during incidents that should have triggered them. Match each metric to the MBean it is actually published under.

| # | Metric |
|---|---|
| 1 | `UnderReplicatedPartitions` |
| 2 | `UncleanLeaderElectionsPerSec` |
| 3 | `ActiveControllerCount` |
| 4 | `RequestHandlerAvgIdlePercent` |

| Letter | MBean |
|---|---|
| W | `kafka.controller:type=ControllerStats` |
| X | `kafka.server:type=KafkaRequestHandlerPool` |
| Y | `kafka.server:type=ReplicaManager` |
| Z | `kafka.controller:type=KafkaController` |

- A. 1-Y · 2-Z · 3-W · 4-X
- B. 1-Y · 2-W · 3-Z · 4-X
- C. 1-Z · 2-W · 3-Y · 4-X
- D. 1-Y · 2-X · 3-Z · 4-W

### Question 39 — `[ARCH · Follower fetching · Single]`

Cross-AZ transfer charges did not move after `RackAwareReplicaSelector` was rolled out on every broker. Producers write about 1 TB/day; consumers read about 4 TB/day.

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type brokers --entity-name 3 \
    --describe --all | grep -E 'broker.rack|replica.selector.class'
  broker.rack=eu-west-1b sensitive=false synonyms={STATIC_BROKER_CONFIG:broker.rack=eu-west-1b}
  replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector sensitive=false synonyms={STATIC_BROKER_CONFIG:replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector}
```

The consumer teams were not asked to change anything. What is missing, and what will still cross zones afterwards?

- A. `replica.selector.class` also has to be set on the consumers so they agree with the brokers on which replica to prefer.
- B. `client.rack` on the **consumers** is missing — it defaults to empty, so the selector has nothing to match and every consumer keeps reading from the leader. Once each consumer sets `client.rack` to its own zone, reads are served by a same-zone follower. Writes are unaffected: **producers always write to the leader**, so the ~1 TB/day of ingest and the replication behind it still crosses zones.
- C. Follower fetching only applies to consumers using `acks=1`; the consumers must be reconfigured for it to take effect.
- D. `broker.rack` must also be set on the consumers so they declare which zone they are in.

### Question 40 — `[CFG · Config precedence · Multi — Choose 2]`

An operator is asked why `retention.ms` on `audit-events` is three days, when `server.properties` says seven and a colleague "set it to 30 days last month".

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type topics \
    --entity-name audit-events --describe --all | grep retention.ms
  retention.ms=259200000 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:retention.ms=259200000, STATIC_BROKER_CONFIG:log.retention.ms=2592000000, DEFAULT_CONFIG:log.retention.ms=604800000}
```

Which **two** statements are correct? (Choose two.)

- A. Running the command without `--all` would have printed the same three synonyms; the flag only changes the formatting.
- B. Editing `log.retention.ms` in `server.properties` and rolling the brokers fixes it, because a static broker config always wins over a dynamic topic config.
- C. The `synonyms` list is printed in **precedence order** and the first entry wins: `DYNAMIC_TOPIC_CONFIG` beats `STATIC_BROKER_CONFIG`, which beats `DEFAULT_CONFIG`. The three-day topic override is the effective value and it is masking the 30-day broker setting.
- D. `kafka-configs.sh --alter --entity-type topics --entity-name audit-events --delete-config retention.ms` removes the override, and the topic immediately falls back to the next synonym — 30 days — with no restart.
- E. The `DEFAULT_CONFIG` entry of 604,800,000 proves the brokers never read `server.properties` at start-up.

### Question 41 — `[TROUBLE · Transient metadata errors · Single]`

Immediately after broker 6 was restarted for a kernel patch, application logs across the fleet filled with:

```
WARN [Producer clientId=checkout-3] Received invalid metadata error in produce request on partition orders-9
due to org.apache.kafka.common.errors.LeaderNotAvailableException: There is no leader for this topic-partition
as we are in the middle of a leadership election. Going to request metadata update now
```

The warnings stopped on their own after about 25 seconds. `OfflinePartitionsCount` peaked at 3 and returned to 0, `record-error-rate` stayed at 0 throughout, and no send ever failed. What is the correct response?

- A. Set `unclean.leader.election.enable=true` so a leader is always available and restarts stop producing these warnings.
- B. The restart bypassed controlled shutdown. Set `controlled.shutdown.enable=true` — it is `false` by default — and restart the remaining brokers properly.
- C. Add `retries=Integer.MAX_VALUE` to every producer; without it `LeaderNotAvailableException` is fatal and the next restart will drop records.
- D. Nothing beyond confirming that the burst was short. `LeaderNotAvailableException` is **retriable**: the producer refreshes metadata and retries well inside `delivery.timeout.ms`, which is why nothing failed. A brief burst is the normal shape of a leader handover; what deserves investigation is a burst that does **not** end.

### Question 42 — `[FUND · Group coordinator · Single]`

During a rolling restart, exactly one team's consumer group stalls each time one particular broker is down, while dozens of other groups carry on.

```
$ kafka-consumer-groups.sh --bootstrap-server broker-1:9092 --describe --group ledger-sync --state
Error: Executing consumer group command failed due to org.apache.kafka.common.errors.CoordinatorNotAvailableException
```

`__consumer_offsets` has 50 partitions with `ReplicationFactor: 3`, and `UnderReplicatedPartitions` is 0 whenever all brokers are up. Which explanation is correct?

- A. A group's coordinator is the **leader of the `__consumer_offsets` partition** selected by `hash(group.id) % 50`. During the restart that partition's leader is on the broker being bounced and leadership has not yet moved, so only the groups hashing to those partitions are affected. With RF 3 leadership does move — the real defect is a restart procedure that does not wait for `UnderReplicatedPartitions` to return to 0 (and for leadership to rebalance) between brokers.
- B. `ledger-sync` uses static membership, so its member ids survive the restart and the coordinator refuses to reassign them until `session.timeout.ms` expires.
- C. The group coordinator is the active controller, so restarting the controller node is what breaks the group; the other groups were simply idle at the time.
- D. `offsets.topic.replication.factor` must be raised to 3 and the brokers rolled so that `__consumer_offsets` gains replicas.

### Question 43 — `[CONNECT · Source offsets · Single]`

A JDBC source connector in incrementing mode had been steady at about 340 M rows for months. During a naming cleanup, a colleague deleted the connector `oracle-billing-src` and re-created it — byte-for-byte the same configuration — under the name `oracle-billing-source`. Within an hour the destination topic doubled in size and the downstream sink's lag hit 300 M. What happened, and how do you avoid a second full re-ingest?

- A. `DELETE /connectors/{name}` deletes the connector's offsets along with it, so the new connector had nothing to resume from. Recovering means restoring `connect-offsets` from a backup.
- B. `errors.tolerance=all` caused the framework to re-deliver every record that had previously been skipped.
- C. A source connector's offsets live in `connect-offsets` under a key that includes the **connector name**. Renaming the connector orphaned the old offsets and the new one started from the beginning. Remove the duplicate, restore the original name, and in future move offsets deliberately — `PUT /connectors/{n}/stop` followed by `PATCH /connectors/{n}/offsets` — rather than by renaming.
- D. A source connector needs `tasks.max=1` for its offset key to stay stable across restarts; with more than one task the key includes the task id.

### Question 44 — `[CFG · Timestamp validation · Single]`

After a 4.1 → 4.3 upgrade, one producer fleet — an IoT gateway that stamps `CreateTime` from each device's own clock — starts logging:

```
org.apache.kafka.common.errors.InvalidTimestampException: One or more records have been rejected due to invalid timestamp
```

Only devices whose clocks run fast are affected. Every other producer is fine. What is the cause and the correct operator response?

- A. Switch the topic to `message.timestamp.type=LogAppendTime`. That is the only supported fix, and it removes the dependency on device clocks entirely.
- B. Kafka 4.3 changed `message.timestamp.after.max.ms` from `Long.MAX_VALUE` to **one hour**, so a record whose `CreateTime` is more than an hour in the future is now rejected at the broker. Fix the device clocks — that is the real defect — and, if you need breathing room, raise `message.timestamp.after.max.ms` on that one topic as a temporary measure.
- C. `message.timestamp.difference.max.ms` was renamed during the upgrade and the old value did not carry over, so the effective allowance is now 0.
- D. The **brokers'** clocks drifted during the upgrade. Resynchronise NTP on the brokers and restart them.

### Question 45 — `[SEC · Credential compromise · Ordering]`

The SCRAM password for `User:etl-prod` was pasted into a public ticket twenty minutes ago. The legitimate ETL job must keep running, and the listener has `connections.max.reauth.ms` at its default. Put the response in the order that stops the exposure soonest while keeping the ETL job alive.

| # | Step |
|---|---|
| 1 | Change the password with `kafka-configs.sh --alter --entity-type users --entity-name etl-prod --add-config 'SCRAM-SHA-512=[password=...]'` and publish the new one to the owning team through the secret store |
| 2 | Add a `DENY` ACL for `User:etl-prod` from every host except the ETL job's own — authorization is evaluated on **every request**, so it bites on connections that are already open |
| 3 | Remove the temporary `DENY` ACL and set `connections.max.reauth.ms` on the listener, so that the next revocation takes effect within a bounded time instead of never |
| 4 | Restart the ETL job onto the new password and confirm that it authenticates and resumes committing |

- A. 1 → 4 → 2 → 3
- B. 2 → 1 → 4 → 3
- C. 1 → 2 → 4 → 3
- D. 2 → 4 → 1 → 3

### Question 46 — `[ARCH · Cluster Linking scope · Multi — Choose 2]`

After the decision to replace MirrorMaker 2 with Cluster Linking, a design review proposes three things: (i) drop two PII columns during replication with an SMT, (ii) let the DR-side applications write to the mirror topics during the next failover drill, (iii) run a link between the Confluent Server production cluster and an `apache/kafka` 4.3 cluster in the lab. Which **two** statements are correct? (Choose two.)

- A. A mirror topic is **read-only** on the destination until it is promoted. Applications cannot produce to it while it is mirroring — that restriction is exactly what keeps the offsets byte-for-byte identical to the source.
- B. Cluster Linking moves bytes as they are. There is no converter, no SMT and no transformation stage, so masking or filtering during replication is a MirrorMaker 2 / Connect capability, not a Cluster Linking one.
- C. Cluster Linking became part of Apache Kafka in 4.3, so the `apache/kafka` lab cluster can serve as the destination.
- D. Cluster Linking still needs a Connect cluster on the destination side, sized roughly like the MM2 fleet it replaces.
- E. Because offsets are preserved exactly, a consumer group can commit on both clusters at the same time during the drill without any coordination.

### Question 47 — `[TROUBLE · Quota throttling · Multi — Choose 2]`

A batch loader that has run at about 180 MB/s for a year now plateaus at exactly 20 MB/s. Broker logs are clean, `UnderReplicatedPartitions` is 0, `RequestHandlerAvgIdlePercent` is 0.72 and the disks are 45 % full. The producer reports:

```
produce-throttle-time-avg = 611.4 ms
produce-throttle-time-max = 982.0 ms
```

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type clients --entity-default --describe
Dynamic configs for the default client-id are:
  producer_byte_rate=20971520 sensitive=false synonyms={DYNAMIC_DEFAULT_CLIENT_CONFIG:producer_byte_rate=20971520}
```

Which **two** statements are correct? (Choose two.)

- A. A quota is enforced **per cluster**, so 20 MiB/s is the total across all brokers and adding brokers cannot help.
- B. A non-zero `produce-throttle-time-avg` is the decisive signal that a **quota**, not the cluster, is the limit: the broker is deliberately delaying its responses rather than failing them, which is why nothing is logged anywhere.
- C. Somebody applied a **default** client-id quota of 20 MiB/s, which covers every client that has no more specific quota. The narrow fix is an explicit quota for this loader's own `client.id`; the broad fix is to remove the accidental default and set quotas deliberately.
- D. Delete the default quota with `--delete-config producer_byte_rate` so that nothing on the cluster is ever throttled again.
- E. Raise `queued.max.requests` above its default of 500 so that throttled produce requests stop queueing on the broker.

### Question 48 — `[FUND · Partition count limits · Multi — Choose 2]`

A six-broker cluster carries 41,000 partition replicas — about 6,800 per broker. A controlled restart of one broker now takes 11 minutes to bring `UnderReplicatedPartitions` back to 0, up from 90 seconds two years ago, and broker heap usage climbs steadily month by month. A team has just requested a topic with 5,000 partitions. Which **two** statements are correct? (Choose two.)

- A. There is no cap the broker enforces, but every replica costs file handles, memory for its index and fetcher state, and time in every leader election and metadata refresh — which is precisely why restart and failover times grow with the replica count.
- B. Kafka 4.3 refuses to create a topic that pushes a broker past 4,000 partitions unless `max.partitions.per.broker` is raised.
- C. Raise `num.io.threads` in proportion to the partition count; the restart time is bounded by the request handler pool.
- D. The often-quoted 2,000–4,000 partitions per broker comes from the **ZooKeeper era**, when leader election scaled badly with partition count. KRaft elects leaders far faster, so treat it as a cautious planning figure rather than a hard ceiling.
- E. Partition count has no bearing on restart time under KRaft, because every broker already holds the metadata log locally.

### Question 49 — `[CFG · Internal topic replication · Single]`

A two-broker staging cluster. A team enables transactions in their producer and the application hangs inside `initTransactions()`. On the broker:

```
[2026-09-19 16:20:44,003] ERROR [KafkaApi-1] Error while creating topic __transaction_state
org.apache.kafka.common.errors.InvalidReplicationFactorException: Replication factor: 3 larger than available brokers: 2.
```

What is happening, and what is the correct fix for a staging cluster?

- A. Lower `min.insync.replicas` to 1 on both brokers; `__transaction_state` inherits the broker value and will then be created.
- B. Create `__transaction_state` by hand with `kafka-topics.sh --create --replication-factor 2 --partitions 50` before starting the application.
- C. Add a third broker. `transaction.state.log.replication.factor` is read-only and cannot be lowered once a cluster exists.
- D. `transaction.state.log.replication.factor` defaults to **3** and `transaction.state.log.min.isr` to **2**, so the coordinator topic cannot be created on two brokers and `initTransactions()` never completes. On staging, set both to 1 **before** the topic is first created — and remember the same shape applies to `offsets.topic.replication.factor` (3) and `share.coordinator.state.topic.replication.factor` (3).

### Question 50 — `[CONNECT · Symptom to cause · Matching]`

Match each Kafka Connect symptom to the condition that produced it.

| # | Symptom |
|---|---|
| 1 | A sink connector is configured `tasks.max=12`, but `GET /connectors/{n}/status` consistently lists exactly 4 tasks, all `RUNNING` |
| 2 | A freshly installed connector's tasks fail on two of three workers with `ClassNotFoundException`, and run fine on the third |
| 3 | After one worker was restarted, every connector in the cluster sat `UNASSIGNED` for five minutes and then recovered by itself |
| 4 | A source connector is `RUNNING` with a healthy `source-record-poll-rate`, but `source-record-write-rate` is 0 and the destination topic stays empty |

| Letter | Condition |
|---|---|
| W | The connector's jar was unpacked into only one worker's `plugin.path` |
| X | A `Filter` transform with a predicate is dropping every record before it reaches the producer |
| Y | The task count is capped by how many partitions there are to assign, so the extra tasks would have nothing to do |
| Z | `scheduled.rebalance.max.delay.ms` (default 300,000 ms) deliberately defers reassigning a departed worker's tasks so that a quick restart does not churn the cluster |

- A. 1-W · 2-Y · 3-Z · 4-X
- B. 1-Y · 2-W · 3-X · 4-Z
- C. 1-Z · 2-W · 3-Y · 4-X
- D. 1-Y · 2-W · 3-Z · 4-X

### Question 51 — `[OBS · Lag monitoring blind spot · Single]`

At 03:00 the lag panel for `fraud-scoring` dropped from 40,000 to 0 and stayed there all night. At 09:00 the business reports six hours of unscored transactions. The dashboard scrapes `records-lag-max` from the consumers' JMX endpoints. What happened, and what should the dashboard do instead?

- A. `records-lag-max` is a **client** metric. When the consumer JVMs died it simply stopped being exported, and the panel rendered "no data" as 0. Lag has to be measured from the broker side — committed offset versus log end offset, via `kafka-consumer-groups.sh --describe` or an exporter that reads `__consumer_offsets` — and the alert must fire on the **absence** of the metric as well as on its value.
- B. `records-lag-max` only covers partitions currently assigned to the member, so it collapses to 0 during a rebalance. Lengthen the scrape interval so short rebalances are not sampled.
- C. Retention deleted the backlog overnight, so the lag genuinely fell to 0. Raise `retention.ms` on the topic.
- D. The consumers were configured with `auto.offset.reset=latest` and skipped to the head of the log at 03:00, which zeroed the lag. Change it to `earliest`.

### Question 52 — `[SEC · KRaft controller listener · Multi — Choose 2]`

An audit finds that although client and inter-broker traffic is `SASL_SSL`, a `tcpdump` on port 9093 between the controller nodes shows readable metadata records.

```
listeners=SASL_SSL://:9092,CONTROLLER://:9093
listener.security.protocol.map=SASL_SSL:SASL_SSL,CONTROLLER:PLAINTEXT
controller.listener.names=CONTROLLER
inter.broker.listener.name=SASL_SSL
```

Which **two** statements are correct? (Choose two.)

- A. Controller traffic is encrypted by the Raft protocol itself, so the readable bytes must belong to a different service on that port.
- B. The controller listener is a listener like any other: its security protocol comes from `listener.security.protocol.map`, and here `CONTROLLER` is mapped to `PLAINTEXT`. Every metadata record on the Raft log — topic definitions, ACLs, SCRAM credential metadata — crosses the wire in the clear.
- C. `inter.broker.listener.name=SASL_SSL` already governs the controller listener, so the mapping line is cosmetic.
- D. In KRaft the controller listener must be `PLAINTEXT`; securing it is only possible on Confluent Platform.
- E. Securing it means mapping `CONTROLLER` to `SSL` or `SASL_SSL`, adding the listener-prefixed `ssl.*` / `sasl.*` properties for it (including `sasl.mechanism.controller.protocol` when SASL is used), and rolling **both** the controllers and the brokers — brokers dial the controller listener too.

### Question 53 — `[TROUBLE · TLS trust chain · Single]`

Three weeks after a new internal CA was introduced, one legacy service — untouched since 2024 — starts failing, while every other client is fine:

```
org.apache.kafka.common.errors.SslAuthenticationException: SSL handshake failed
Caused by: javax.net.ssl.SSLHandshakeException: PKIX path building failed:
  sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
```

The brokers were re-keyed overnight with certificates signed by `ca-2026`; the broker keystores and the brokers' own truststores were both updated. What is the cause and the correct fix?

- A. That client's keystore has expired; issue it a new client certificate from `ca-2026`.
- B. The broker certificate is missing an IP SAN for this client's source address, so the path cannot be validated.
- C. That client's **truststore** still contains only `ca-2024`, so it cannot build a chain to the new broker certificate. Add `ca-2026` to that truststore. The lesson for the runbook: distribute the **combined** truststore (`ca-2024` + `ca-2026`) to every client and confirm the rollout **before** replacing the first broker keystore.
- D. Set `ssl.endpoint.identification.algorithm=` (empty) on that client so it stops validating the server certificate.

### Question 54 — `[ARCH · Replacing a controller · Ordering]`

```
$ kafka-metadata-quorum.sh --bootstrap-controller controller-1:9093 describe --status
ClusterId:      Ky7sJm2CTQ6kR0lNwUeT1g
LeaderId:       3001
LeaderEpoch:    58
HighWatermark:  20114773
CurrentVoters:  [{"id": 3001, ...}, {"id": 3002, ...}, {"id": 3003, ...}]
```

Controller 3003's motherboard is dead and will not come back. `kafka-features.sh describe` reports `kraft.version: 1`. Put the replacement steps in order for a swap with no downtime.

| # | Step |
|---|---|
| 1 | Format the replacement machine with the cluster's **existing** cluster id and `--no-initial-controllers`, then start it |
| 2 | Run `kafka-metadata-quorum.sh ... add-controller` from the new node, then re-check `describe --status` until three voters are listed again |
| 3 | Confirm the surviving quorum still holds a majority (2 of 3) and has an elected leader, before changing the voter set at all |
| 4 | Run `kafka-metadata-quorum.sh ... remove-controller` for 3003's node id and directory id, so the voter set becomes 3001 and 3002 |

- A. 1 → 3 → 4 → 2
- B. 3 → 1 → 2 → 4
- C. 4 → 3 → 1 → 2
- D. 3 → 4 → 1 → 2

### Question 55 — `[CFG · Unclean leader election · Multi — Choose 2]`

At 02:40, trying to clear `OfflinePartitionsCount=14`, an operator runs:

```
$ kafka-configs.sh --bootstrap-server broker-1:9092 --entity-type brokers --entity-default \
    --alter --add-config unclean.leader.election.enable=true
Completed updating default config for brokers in the cluster.
```

Which **two** statements are correct? (Choose two.)

- A. Because the default is `false`, the new value applies only to topics created after the change; the 14 offline partitions are unaffected.
- B. `unclean.leader.election.enable` is a read-only property, so the command is recorded but nothing happens until every broker is restarted.
- C. This is a **cluster-wide dynamic** config: it takes effect with no restart, and the controller immediately elects out-of-ISR replicas for the affected partitions, so `OfflinePartitionsCount` falls within seconds.
- D. Every partition that gains a leader this way **truncates** to the new leader's log end offset. Records that were committed and acknowledged to `acks=all` producers are gone, and consumers that had read past that point will see `OffsetOutOfRangeException` or silently re-read. Setting the flag back to `false` afterwards restores nothing.
- E. With ELR enabled — the default for clusters created on 4.1 or later — unclean election is no longer possible, so the command is a no-op.

### Question 56 — `[FUND · Share groups · Single]`

A team runs a work queue on Kafka 4.3: one topic, 12 partitions, each record taking 2–30 minutes of OCR work. A single slow record blocks everything behind it in its partition, and adding consumers beyond 12 changes nothing.

```
$ kafka-consumer-groups.sh --bootstrap-server broker-1:9092 --describe --group ocr-workers
GROUP        TOPIC  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG    CONSUMER-ID
ocr-workers  scans  4          88213           132904          44691  ocr-9-a1f...
ocr-workers  scans  7          131998          132011          13     ocr-3-77c...
```

Which option fits the shape of this workload on 4.3, and what does it cost?

- A. Raise `scans` to 200 partitions so far more consumers can join the group.
- B. Use a **share group** (KIP-932, production-ready since 4.2): many consumers may read the **same** partition, records are acknowledged individually and redelivered on failure, so a slow record stops blocking the ones behind it. The cost is that a share group offers no per-partition ordering and no offset-based rewind in the consumer-group sense, and it needs the internal topic `__share_group_state` — replication factor **3** by default, so a cluster with fewer than three brokers must lower `share.coordinator.state.topic.replication.factor` and `share.coordinator.state.topic.min.isr` to 1 first. Inspect it with `kafka-share-groups.sh`.
- C. Set `max.poll.interval.ms=3600000` and `max.poll.records=1` so a single long record never evicts the member.
- D. Switch the group to the KIP-848 protocol with `group.protocol=consumer`; cooperative assignment removes head-of-line blocking.

### Question 57 — `[SEC · SASL mechanism negotiation · Single]`

A new service cannot authenticate. The credential was created an hour ago, and `kafka-configs.sh --describe --entity-type users --entity-name reporting-svc` confirms it exists.

```
org.apache.kafka.common.errors.SaslAuthenticationException: Client SASL mechanism 'SCRAM-SHA-256'
not enabled in the server, enabled mechanisms are [SCRAM-SHA-512]
```

Which is the correct minimal fix?

- A. Add `SCRAM-SHA-256` to `sasl.enabled.mechanisms` on every broker and roll the cluster so both mechanisms are offered.
- B. Re-create the credential with `kafka-configs.sh --zookeeper zk-1:2181 --alter --entity-type users ...`; SCRAM credentials live in ZooKeeper and the client-side tool wrote it to the wrong place.
- C. Grant the principal `Describe` on the Cluster resource — the message is a masked authorization failure, which Kafka reports as an authentication error to avoid leaking information.
- D. Set `sasl.mechanism=SCRAM-SHA-512` on the client, and make sure the credential was stored **for that mechanism** (`--add-config 'SCRAM-SHA-512=[password=...]'`). A SCRAM credential is stored per mechanism, so a user that only has a SHA-256 entry still cannot authenticate over SHA-512.

### Question 58 — `[ARCH · Upgrade finalization · Single]`

A rolling 4.2.x → 4.3.0 binary upgrade finished at 04:00. Every broker is up and `UnderReplicatedPartitions` is 0. The last line of the change ticket reads *"run `kafka-features.sh upgrade --release-version 4.3`"*, and a junior engineer wants to run it now to finish the job. What do you advise?

- A. Run it now. Until `metadata.version` is finalized the cluster is still writing 4.2 metadata and is running in an unsupported mixed state.
- B. Hold it until the new binaries have soaked. A rolling **binary** downgrade is only available while `metadata.version` is still at the old level; once finalized, whether a downgrade is possible depends on the metadata changes in that release — and **4.3.0 cannot be downgraded**. Finalize after the soak window and verify with `kafka-features.sh describe`.
- C. Finalization happens automatically once every broker reports the new software version; the command has been a no-op since 4.0.
- D. It makes no difference either way, because `kafka-features.sh downgrade --release-version 4.2` can always undo it.

### Question 59 — `[FUND · Metadata replication · Single]`

Topic creations succeed but take up to 40 seconds to become visible to producers connected to one particular broker, and that broker also enforces an ACL a few seconds after every other broker has it.

```
$ kafka-metadata-quorum.sh --bootstrap-controller controller-1:9093 describe --replication
NodeId  DirectoryId  LogEndOffset  Lag     LastFetchTimestamp  LastCaughtUpTimestamp  Status
3001    dir-a...     20115402      0       1758358921112       1758358921112          Leader
3002    dir-b...     20115402      0       1758358921008       1758358921008          Follower
3003    dir-c...     20115399      3       1758358920994       1758358920994          Follower
1       dir-d...     20115401      1       1758358921050       1758358921050          Observer
2       dir-e...     20115400      2       1758358921044       1758358921044          Observer
5       dir-f...     19908114      207288  1758358883517       1758358694120          Observer
```

What does this show, and where do you look next?

- A. Broker 5 is an **observer** of the metadata log that is 207,288 records behind and last caught up roughly four minutes ago. Brokers apply topic creations, ACLs and leadership changes from their own replica of `__cluster_metadata`, so a lagging broker serves stale decisions until it catches up. Investigate broker 5's disk and its network path to the controllers — the topic is not the problem.
- B. Broker 5 should be promoted to a voter with `add-controller`; observers are best-effort replicas and are expected to drift.
- C. Observers do not replicate the metadata log at all — they query the controller on demand — so the `Lag` column is meaningless for node 5 and the delay must come from `metadata.max.age.ms` on the clients.
- D. The quorum has lost its majority: follower 3003 is three records behind the leader. Restart 3003 to restore the quorum.

### Question 60 — `[CONNECT · Rewinding a sink · Single]`

A bad transform shipped at 11:00 wrote three hours of mangled rows through `warehouse-sink` into the data warehouse. The table has been truncated for that window and the connector must now replay from 11:00. The connector is still `RUNNING`.

```
$ kafka-consumer-groups.sh --bootstrap-server broker-1:9092 --reset-offsets \
    --group connect-warehouse-sink --topic events \
    --to-datetime 2026-09-20T11:00:00.000 --execute
Error: Assignments can only be reset if the group 'connect-warehouse-sink' is inactive, but the current state is Stable.
```

What is the correct procedure?

- A. `PUT /connectors/warehouse-sink/pause` is enough: a paused connector stops consuming, so its group becomes inactive and the reset succeeds.
- B. Delete the connector and re-create it with the same configuration; a newly created connector always starts from its `auto.offset.reset` position.
- C. `PUT /connectors/warehouse-sink/stop` first — `STOPPED` shuts the tasks down and deassigns them, which empties the consumer group — then rewind, either with `PATCH /connectors/warehouse-sink/offsets` or with the `kafka-consumer-groups.sh` command above now that the group is inactive, and finally `PUT /connectors/warehouse-sink/resume`.
- D. A sink connector's offsets live in `connect-offsets`, not in a consumer group, so the CLI is the wrong tool entirely; call `DELETE /connectors/warehouse-sink/offsets` to rewind to 11:00.

---

> ✅ Hết giờ? Chấm bài ở [answers.md](answers.md) và điền bảng điểm theo domain trước khi xem giải thích.
