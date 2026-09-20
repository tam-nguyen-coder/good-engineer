# 📝 Practice Questions — Week 7: Observability + Troubleshooting playbook

> **30 questions** · real CCAAK exam style (scenario-driven: *"which action would a competent administrator take?"*) · covers the full Week 7 material + 2 review questions from Week 6 (Kafka Connect).
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first, timed at ~90 seconds per question.
> Tag: `[DOMAIN · Topic · type]`. Domains: `OBS` (Observability), `TROUBLE` (Troubleshooting), `CONNECT` (Kafka Connect). Multi = multiple-response, the number to choose is stated.
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[OBS · Red-line metrics · Single]`

A monitoring dashboard for a Kafka 4.3 cluster shows the following aggregated values, sustained for the last ten minutes:

```
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions     = 140
kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount     = 0
kafka.controller:type=KafkaController,name=OfflinePartitionsCount   = 0
```

All topics use `replication.factor=3` and `min.insync.replicas=2`. What is the current impact on client applications?

- A. Producers using `acks=all` are being rejected with `NotEnoughReplicasException`, but consumers are unaffected
- B. Both producers and consumers are failing for the 140 affected partitions because they have no leader
- C. Producers and consumers continue to work normally; the cluster has lost durability headroom but not availability
- D. Consumers can still read, but all producers regardless of `acks` are blocked until the ISR recovers

### Question 2 — `[TROUBLE · min.insync.replicas · Single]`

Two of five brokers have crashed. A payments producer configured with `acks=all` starts failing, and the cluster reports `UnderMinIsrPartitionCount = 12`. The on-call engineer proposes setting `min.insync.replicas=1` on the affected topics to "get writes flowing again immediately". What should the administrator do FIRST?

- A. Apply the proposed change; `min.insync.replicas` is a dynamic topic config and can be raised again later
- B. Increase `replica.lag.time.max.ms` so that the lagging replicas are counted as in-sync again
- C. Set `unclean.leader.election.enable=true` so a new leader can be elected from outside the ISR
- D. Restore the failed brokers so the ISR returns to at least `min.insync.replicas`, because lowering the minimum removes the exact guarantee that is currently protecting acknowledged writes

### Question 3 — `[OBS · Controller metrics · Single]`

A cluster runs three dedicated controller nodes (`process.roles=controller`) and three brokers (`process.roles=broker`). A new engineer reports an incident: *"`ActiveControllerCount` is 0 on every one of our three brokers."* Cluster operations such as topic creation are working fine. What is the correct assessment?

- A. This is a genuine split-brain and the cluster must be restarted
- B. This is expected: in KRaft the metric is valid as 0 or 1 per node and only a dedicated controller holds the value 1, so the administrator should verify the *aggregated sum across the cluster* equals 1
- C. The brokers have lost their ZooKeeper session, so the controller znode is unowned; check `zookeeper.connect` on each broker
- D. `ActiveControllerCount` is only emitted by brokers, so a value of 0 everywhere means the controller quorum has no leader

### Question 4 — `[OBS · Request latency phases · Single]`

Produce p99 latency on one broker has tripled. The administrator breaks down `kafka.network:type=RequestMetrics,...,request=Produce` and finds:

```
TotalTimeMs          p99 = 840 ms
RequestQueueTimeMs   p99 = 790 ms
LocalTimeMs          p99 =  12 ms
RemoteTimeMs         p99 =  22 ms
ResponseQueueTimeMs  p99 =   3 ms
ResponseSendTimeMs   p99 =   4 ms
RequestHandlerAvgIdlePercent = 0.06     NetworkProcessorAvgIdlePercent = 0.71
```

Broker CPU is at 45%. Which change should the administrator make FIRST?

- A. Increase `num.network.threads` from its default of 3
- B. Increase `num.replica.fetchers` from its default of 1
- C. Increase `num.io.threads` from its default of 8
- D. Move the broker's `log.dirs` onto faster disks

### Question 5 — `[OBS · Request latency phases · Multi — Choose 2]`

An administrator is reviewing `RemoteTimeMs` across request types on a healthy cluster. Which two observations are expected behaviour that requires no action? (Choose two.)

- A. `RemoteTimeMs` for `request=Produce` is consistently non-zero on topics whose producers use `acks=all`
- B. `RemoteTimeMs` for `request=FetchConsumer` is close to `fetch.max.wait.ms` on a low-traffic topic
- C. `RemoteTimeMs` for `request=Produce` is non-zero on topics whose producers use `acks=1`
- D. `RemoteTimeMs` for `request=FetchFollower` is the dominant component of `TotalTimeMs` while a broker is being decommissioned
- E. `RemoteTimeMs` is zero for every request type on a broker that is serving traffic normally

### Question 6 — `[TROUBLE · ISR flapping · Multi — Choose 2]`

On one broker, `IsrShrinksPerSec` and `IsrExpandsPerSec` are both elevated and roughly equal, and `UnderReplicatedPartitions` oscillates between 0 and about 30. No broker has restarted in three days. The JVM garbage collection log on that broker shows repeated pauses of 1.8–3.2 seconds, and the broker was recently given a 48 GB heap on a 64 GB machine. Which two statements are correct? (Choose two.)

- A. The pattern of matched shrinks and expansions is ISR flapping: a follower repeatedly exceeds `replica.lag.time.max.ms` (default 30000) and is evicted, then catches up and rejoins
- B. The oversized heap is a likely root cause — Kafka serves reads and writes through the OS page cache, so a broker heap of roughly 6 GB with G1GC is the usual recommendation and the remaining RAM should be left to the OS
- C. Raising `replica.lag.time.max.ms` to 90000 is the correct fix, because it removes the eviction and therefore removes the flapping
- D. Reducing `min.insync.replicas` to 1 on the affected topics resolves the flapping at its source
- E. Flapping of this kind cannot be caused by garbage collection, because the heartbeat to the controller runs on a separate thread

### Question 7 — `[TROUBLE · Controller quorum · Single]`

Producers and consumers on an existing topic are working, but every administrative command (`kafka-topics.sh --create`, `kafka-configs.sh --alter`) hangs and times out. The administrator runs:

```
$ kafka-metadata-quorum.sh --bootstrap-server kafka-1:9092 describe --status
ClusterId:              fMCL8kv1SWm87L_Md-I2hg
LeaderId:               -1
LeaderEpoch:            41
HighWatermark:          -1
MaxFollowerLag:         -1
CurrentVoters:          [{"id": 3000, ...}, {"id": 3001, ...}, {"id": 3002, ...}]
CurrentObservers:       [{"id": 1, ...}, {"id": 2, ...}, {"id": 3, ...}]
```

Two of the three controller nodes are powered off. What is happening and what should be done?

- A. The brokers have been fenced; restart all brokers to re-register them with the quorum
- B. `CurrentObservers` should be empty — the brokers have been misconfigured as observers and must be added with `add-controller`
- C. The metadata quorum has lost its majority, so the control plane is frozen while the data plane keeps serving cached metadata; bring at least one of the two down controllers back to restore a majority
- D. The controller znode has been deleted; recreate it and restart the controllers

### Question 8 — `[TROUBLE · Broker startup · Single]`

A replacement broker refuses to start. `server.log` contains:

```
ERROR Encountered fatal fault: Unable to start server (org.apache.kafka.server.fault.ProcessTerminatingFaultHandler)
org.apache.kafka.common.KafkaException: org.apache.kafka.common.errors.InconsistentClusterIdException:
  The Cluster ID D3SdRy0uTj6ZtqXKEHSGtQ doesn't match stored clusterId Optional[fMCL8kv1SWm87L_Md-I2hg] in meta.properties.
  The broker is trying to join the wrong cluster. Configured controller.quorum.voters may be unaware of this broker.
```

What is the correct fix?

- A. Delete the contents of `log.dirs` on every broker in the cluster and restart them so all nodes agree on one cluster ID
- B. The storage directory of this node was formatted with a different cluster ID; re-run `kafka-storage.sh format` for this node using the cluster's actual cluster ID, and leave the other brokers untouched
- C. Set `allow.everyone.if.no.acl.found=true` so the new broker can register with the controller
- D. Add the broker to `controller.quorum.voters` on every node and perform a rolling restart of the cluster

### Question 9 — `[TROUBLE · Disk full · Single]`

One broker in a JBOD deployment (`log.dirs=/data/d1,/data/d2,/data/d3`) logs:

```
ERROR Error while writing to checkpoint file /data/d2/replication-offset-checkpoint (kafka.server.LogDirFailureChannel)
java.io.IOException: No space left on device
ERROR Uncaught exception in scheduled task 'flush-log' (org.apache.kafka.server.util.KafkaScheduler)
org.apache.kafka.common.errors.KafkaStorageException: Error while writing to log for partition events-17
```

`/data/d1` and `/data/d3` are at 40% usage. Which sequence reflects correct operational priority?

- A. Immediately stop the broker and delete the oldest segment files from `/data/d2` by hand, then restart it
- B. Increase `log.retention.bytes` so Kafka enforces a size cap and cleans up automatically
- C. Set `unclean.leader.election.enable=true` so leadership moves off the failing broker
- D. Temporarily reduce `retention.ms` on the largest topics on that log dir to reclaim space, then plan a throttled reassignment; use `cordoned.log.dirs` if the directory is to be removed permanently

### Question 10 — `[TROUBLE · Consumer lag decision tree · Single]`

A consumer group with 6 members reads a 6-partition topic. `kafka-consumer-groups.sh --describe` shows lag of ~4,000,000 on partition 3 and lag of 0 on the other five partitions. All six members are assigned exactly one partition each and none is idle. What should the administrator recommend?

- A. Add six more consumer instances to the group so the backlog is drained faster
- B. Increase the topic to 12 partitions so the load is spread more evenly
- C. Investigate key skew — a small number of record keys is hashing to partition 3; adding consumers cannot help because a partition has at most one owner in the group
- D. Increase `max.poll.records` on the consumers so each poll processes more records

### Question 11 — `[TROUBLE · Consumer group state · Single]`

An administrator investigating a stalled pipeline runs:

```
$ kafka-consumer-groups.sh --bootstrap-server kafka-1:9092 --describe --group invoice-sink

GROUP         TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG      CONSUMER-ID  HOST  CLIENT-ID
invoice-sink  invoices  0          1048221         1902334         854113   -            -     -
invoice-sink  invoices  1          1047980         1901002         853022   -            -     -
invoice-sink  invoices  2          1048004         1900871         852867   -            -     -
```

What does this output tell the administrator?

- A. The consumers are running but are too slow, so the lag is growing
- B. No member of the group currently owns these partitions — the group has no live consumers (or is mid-rebalance), so the lag is frozen at the last committed offsets
- C. The `__consumer_offsets` topic is unavailable, which is why `CONSUMER-ID` cannot be resolved
- D. The consumers are using `assign()` instead of `subscribe()`, which is why their IDs are hidden

### Question 12 — `[TROUBLE · Rebalance loop · Multi — Choose 2]`

A consumer application logs the following repeatedly, roughly every four minutes:

```
WARN  [Consumer clientId=orders-3, groupId=orders] Attempt to heartbeat failed since group is rebalancing
ERROR Offset commit failed: org.apache.kafka.clients.consumer.CommitFailedException: Offset commit cannot be completed
      since the consumer is not part of an active group for auto partition assignment; it is likely that the consumer
      was kicked out of the group and the time between subsequent calls to poll() was longer than the configured
      max.poll.interval.ms
```

CPU on the consumer hosts sits at 20% and the heartbeat thread is healthy. Which two actions address the root cause? (Choose two.)

- A. Reduce `max.poll.records` from its default of 500 so a single processing loop finishes faster
- B. Increase `session.timeout.ms` from 45000 to 180000
- C. Increase `max.poll.interval.ms` above the worst-case processing time of one batch
- D. Reduce `heartbeat.interval.ms` from 3000 to 1000 so the coordinator sees the member more often
- E. Set `enable.auto.commit=false` so the failing commit no longer throws

### Question 13 — `[TROUBLE · advertised.listeners · Single]`

A new client running outside the Kubernetes cluster can list topics successfully:

```
$ kafka-topics.sh --bootstrap-server kafka.example.com:9092 --list
orders
payments
```

but every produce attempt ends with:

```
org.apache.kafka.common.errors.TimeoutException: Expiring 3 record(s) for orders-1:120000 ms has passed since batch creation
```

The broker's `server.log` shows no incoming produce requests at all. What is the most likely cause?

- A. `advertised.listeners` returns internal addresses (for example `kafka-1.kafka-headless.svc:9092`) that the external client cannot reach, so the client connects to the bootstrap endpoint but fails to reach the partition leader
- B. The topic `orders` has `min.insync.replicas` higher than the number of live replicas
- C. `request.timeout.ms` on the client is too low and must be raised above 120000
- D. The client is missing the `Describe` ACL on the topic

### Question 14 — `[TROUBLE · Quotas · Single]`

A team reports that their producer throughput flatlines at exactly 20 MB/s no matter how many instances they add. There are no exceptions in the application logs, no errors in `server.log`, `UnderReplicatedPartitions` is 0, and `RequestHandlerAvgIdlePercent` is 0.68. Which metric should the administrator check next?

- A. `records-lead-min` on the consumer side
- B. `produce-throttle-time-avg` on the producer, then `kafka-configs.sh --describe --entity-type clients` to inspect `producer_byte_rate`
- C. `LogFlushRateAndTimeMs` on each broker
- D. `IsrShrinksPerSec` on the partition leaders

### Question 15 — `[OBS · Consumer lag measurement · Single]`

For the same consumer group at the same moment, `kafka-consumer-groups.sh --describe` reports a total lag of 12,000 while the client's JMX metric `records-lag-max` reports 3,500. Which explanation is correct?

- A. The CLI is stale because it reads from `__consumer_offsets`, which is compacted; the client metric is authoritative
- B. The client metric excludes partitions in the `read_committed` isolation level, so it is always lower
- C. Both values are correct: the CLI measures lag from the last **committed** offset (auto-commit runs every 5,000 ms by default), while `records-lag-max` measures lag from the consumer's current **fetch position**; the difference is the records already fetched but not yet committed
- D. `records-lag-max` reports lag for a single partition while the CLI sums all partitions, so the two can never be compared

### Question 16 — `[OBS · Lag monitoring limits · Single]`

An operations team wants a lag alert for a legacy service that calls `consumer.assign(Arrays.asList(new TopicPartition("audit", 0)))` and never calls `subscribe()`. The service does set a `group.id`. What should the administrator tell them?

- A. Run `kafka-consumer-groups.sh --describe --group <id>`; it reports lag for any consumer that sets a `group.id`
- B. Broker-side lag monitoring does not work for consumers that use `assign()`, because the group coordinator does not manage their assignment; the service must expose its own lag (for example the client metric `records-lag-max`)
- C. Enable `confluent.consumer.lag.emitter.enabled=true`, which adds lag tracking for standalone consumers
- D. Switch the consumers to `read_committed` so their positions are recorded in `__consumer_offsets`

### Question 17 — `[OBS · Early-warning metrics · Single]`

A consumer group is 6 hours behind on a topic with `retention.ms=86400000` (24 hours). The client metric `records-lead-min` has been falling steadily and is now close to 0 on two partitions. What does this mean, and what is the most urgent action?

- A. The consumer is about to catch up; no action is needed
- B. The group has committed offsets outside the valid range and will throw `OffsetOutOfRangeException` on the next poll
- C. The broker is about to run out of disk on those partitions — reduce `retention.ms`
- D. The consumer's fetch position is approaching the topic's log start offset, so retention is about to delete records the group has not read yet — temporarily increase `retention.ms` while scaling the consumers

### Question 18 — `[OBS · Alert design · Single]`

The on-call rotation is being woken up during every deployment because the alert `UnderReplicatedPartitions > 0` fires for two to three minutes during each rolling broker restart. The team wants to keep detecting genuine replication failures. What is the best change?

- A. Keep the expression as is and add `for: 10m` so the alert stays in the pending state during normal rolling restarts and only fires when the condition persists
- B. Raise the alert threshold to `UnderReplicatedPartitions > 50`
- C. Delete the alert, since `OfflinePartitionsCount` already covers replication problems
- D. Change the alert to evaluate only outside business hours

### Question 19 — `[OBS · Alert design · Multi — Choose 2]`

Which two conditions justify a **paging** alert that wakes an engineer at 03:00, rather than a ticket for the next business day? (Choose two.)

- A. `RequestHandlerAvgIdlePercent` has been below 0.3 for the last 20 minutes on one broker
- B. The aggregated `OfflinePartitionsCount` across the cluster has been greater than 0 for one minute
- C. `IsrShrinksPerSec` has been non-zero for 15 minutes on a single broker
- D. Free space on a broker's `log.dirs` filesystem has dropped below 15% and continues to fall
- E. `UnderReplicatedPartitions` is 4 and has been non-zero for three minutes

### Question 20 — `[OBS · Prometheus alerting rules · Single]`

An administrator writes the following rule:

```yaml
groups:
- name: kafka
  rules:
  - alert: KafkaUnderMinIsr
    expr: sum(kafka_server_replicamanager_underminisrpartitioncount) > 0
    for: 2m
    labels:
      severity: page
    annotations:
      summary: "{{ $labels.instance }} has {{ $value }} partitions below min.insync.replicas"
```

The condition becomes true at 10:00:00 and is still true at 10:01:30. What is the state of the alert at 10:01:30?

- A. `firing`, because the expression evaluated true on the first evaluation cycle
- B. `pending`, because the `for` duration of 2 minutes has not yet elapsed
- C. `inactive`, because `sum()` removes the `instance` label used in the annotation
- D. `resolved`, because `keep_firing_for` was not specified

### Question 21 — `[OBS · Metric naming across versions · Single]`

After a rolling upgrade from Kafka 4.1 to 4.3, every panel on the operations Grafana dashboard shows "No data", although `kafka-topics.sh`, produce and consume all work and the JMX exporter targets are `up` in Prometheus. What is the most likely cause?

- A. The brokers must be restarted a second time before JMX metrics are re-registered
- B. KIP-1100 standardised MBean names on the `kafka.<component>` domain in 4.2, so dashboards and exporter rules written against the older names no longer match; verify the current names with `curl <exporter>:7071/metrics` and update the rules and PromQL
- C. `inter.broker.protocol.version` was not raised after the upgrade, so the brokers do not publish metrics
- D. The ZooKeeper JMX bridge was removed, so broker metrics must now be collected from the controller znode

### Question 22 — `[OBS · Broker log files · Multi — Choose 2]`

An administrator must reconstruct exactly when and why leadership for `payments-7` moved from broker 2 to broker 4 during last night's incident, and must also confirm whether a client was denied access during the same window. Which two log files are the right places to look? (Choose two.)

- A. `state-change.log`, which records every leader/ISR state transition ordered by the controller and defaults to TRACE level
- B. `log-cleaner.log`, which records all partition leadership decisions taken by the log cleaner thread
- C. `kafka-authorizer.log`, which records authorization decisions — denials at INFO by default, allowed requests only at DEBUG
- D. `log.dirs/server.properties`, which stores the historical leader for each partition
- E. `kafka-request.log`, which is enabled by default and contains the leadership change requests

### Question 23 — `[OBS · Dynamic logging · Single]`

While diagnosing a latency problem, an administrator needs `kafka.request.logger` at DEBUG on the broker with `node.id=2` for about 60 seconds, without restarting it. Which command is correct?

- A. `kafka-configs.sh --bootstrap-server kafka-1:9092 --alter --entity-type broker-loggers --entity-name 2 --add-config kafka.request.logger=DEBUG`
- B. Edit `config/log4j2.yaml` on broker 2 and send `SIGHUP` to the broker process
- C. `zookeeper-shell.sh localhost:2181 set /config/brokers/2 '{"kafka.request.logger":"DEBUG"}'`
- D. `kafka-configs.sh --bootstrap-server kafka-1:9092 --alter --entity-type brokers --entity-name 2 --add-config log4j.logger.kafka.request=DEBUG`

### Question 24 — `[TROUBLE · Offline partitions · Single]`

A topic created for a proof of concept has `replication.factor=1`. The single broker holding partition 4 has suffered a disk controller failure and will not come back for several hours. `OfflinePartitionsCount` is 1 and the owning application is down. Which statement describes the administrator's real options?

- A. Run `kafka-leader-election.sh --election-type unclean` to elect a new leader from the remaining brokers
- B. Increase `replication.factor` to 3 with `kafka-reassign-partitions.sh`, which will rebuild the missing data from the other brokers
- C. There is no replica of the data anywhere else, so no election of any kind can restore the partition; the choice is to wait for the broker, or to recreate the topic and accept the data loss — and the real lesson is that `replication.factor=1` has no recovery path
- D. Enable ELR (`eligible.leader.replicas.version=1`) so an eligible leader replica takes over

### Question 25 — `[TROUBLE · Exception cheat-sheet · Matching]`

Match each client-side error to the root cause an administrator should investigate.

| # | Error observed by the client |
|---|---|
| 1 | `org.apache.kafka.common.errors.NotEnoughReplicasException` |
| 2 | `org.apache.kafka.common.errors.NotLeaderOrFollowerException` |
| 3 | `org.apache.kafka.common.errors.GroupAuthorizationException: Not authorized to access group: etl-loader` |
| 4 | `org.apache.kafka.common.errors.OffsetOutOfRangeException` |

| Letter | Root cause |
|---|---|
| W | The committed or requested offset no longer exists in the log — retention deleted it, or the topic was recreated |
| X | The ISR has fallen below `min.insync.replicas` while the producer uses `acks=all`; the broker is deliberately refusing the write |
| Y | The principal has topic permissions but is missing a `Read` ACL on the **Group** resource |
| Z | Leadership for the partition has just moved and the client's cached metadata is stale; the client refreshes and retries on its own |

- A. 1-X · 2-Z · 3-Y · 4-W
- B. 1-X · 2-W · 3-Y · 4-Z
- C. 1-Z · 2-X · 3-W · 4-Y
- D. 1-X · 2-Z · 3-W · 4-Y

### Question 26 — `[TROUBLE · Diagnostic method · Ordering]`

An alert fires: consumer lag on a business-critical group is growing. Put the administrator's diagnostic steps in the order a methodical troubleshooting process requires.

| # | Step |
|---|---|
| 1 | Inspect the effective configuration with `kafka-configs.sh --describe --all`, reading the synonyms column to see where each value comes from |
| 2 | Check cluster-health metrics first — `OfflinePartitionsCount`, `ActiveControllerCount`, `UnderMinIsrPartitionCount` — to rule out a broker-side outage |
| 3 | Apply the cheapest reversible remedy that matches the finding, keeping one-way actions such as increasing the partition count as a last resort |
| 4 | Read the relevant logs — `server.log` on the suspect broker, then `controller.log` / `state-change.log` if leadership is involved |

- A. 2 → 4 → 1 → 3
- B. 4 → 2 → 1 → 3
- C. 2 → 1 → 4 → 3
- D. 3 → 2 → 4 → 1

### Question 27 — `[OBS · JMX exporter · Multi — Choose 2]`

A team is instrumenting brokers with the Prometheus JMX Exporter. Which two statements are correct? (Choose two.)

- A. Running the exporter as a Java agent (`KAFKA_OPTS=-javaagent:<jar>=7071:<rules.yml>`) is recommended because it avoids exposing remote JMX/RMI, and only MBeans matching a rule are exported
- B. Because `KAFKA_OPTS` is read by every script in `bin/`, running `kafka-topics.sh` on the broker host itself can fail with `Address already in use` as the CLI's JVM tries to bind the same agent port
- C. The standalone HTTP server mode is preferred in production because it does not require the target JVM to expose remote JMX
- D. The exporter creates new metrics that are not available through JMX, such as end-to-end producer latency
- E. Remote JMX is enabled by default in Kafka, so no extra configuration is needed for the standalone mode

### Question 28 — `[OBS · Latency phases · Matching]`

Match each dominant latency phase to the bottleneck it points at.

| # | Dominant phase of `TotalTimeMs` |
|---|---|
| 1 | `RequestQueueTimeMs` |
| 2 | `LocalTimeMs` |
| 3 | `RemoteTimeMs` on `request=Produce` |
| 4 | `ResponseSendTimeMs` |

| Letter | Bottleneck |
|---|---|
| W | The leader itself is slow to append and flush — look at disk latency and `LogFlushRateAndTimeMs` |
| X | Requests are queuing for the I/O (request handler) thread pool — look at `RequestHandlerAvgIdlePercent` and `num.io.threads` |
| Y | The network path back to the client is slow, or the client reads the response slowly |
| Z | The leader is waiting for in-sync followers to acknowledge the write, which is normal with `acks=all` |

- A. 1-X · 2-W · 3-Z · 4-Y
- B. 1-W · 2-X · 3-Y · 4-Z
- C. 1-X · 2-Z · 3-W · 4-Y
- D. 1-Y · 2-W · 3-Z · 4-X

### Question 29 — `[CONNECT · Week 6 review · Single]`

A sink connector named `s3-archive` shows `"state": "RUNNING"` at the connector level while two of its four tasks report `"state": "FAILED"` with a stack trace in the REST response. The underlying cause (an expired credential) has already been fixed. What is the correct way to bring the tasks back?

- A. `DELETE /connectors/s3-archive` and recreate the connector with the same configuration
- B. `POST /connectors/s3-archive/restart?includeTasks=true&onlyFailed=true`, which restarts the failed tasks without recreating the connector
- C. `PUT /connectors/s3-archive/pause` followed by `PUT /connectors/s3-archive/resume`, which is the only way to reset task state
- D. Restart every Connect worker in the cluster so the tasks are reassigned

### Question 30 — `[CONNECT · Week 6 review · Single]`

During an incident review it emerges that a source connector has been silently dropping malformed records for two weeks. Its configuration contains `errors.tolerance=all` and `errors.log.enable=false`, and the team asks why the dead letter queue did not capture them. What is the correct explanation?

- A. Dead letter queues in Kafka Connect apply to **sink** connectors only; a source connector has no DLQ, so with `errors.tolerance=all` the bad records were discarded — enabling `errors.log.enable=true` is what makes them visible
- B. The DLQ topic was not created because `auto.create.topics.enable=false` on the cluster
- C. `errors.deadletterqueue.topic.name` defaults to the connector name, so the records went to a topic nobody was watching
- D. `errors.tolerance=all` disables the DLQ; it must be set to `none` for the DLQ to receive records

---

> ✅ Done? Check your answers in [answers.md](answers.md), log every wrong answer with the reason you got it wrong, then run **🎯 FULL MOCK #1 — 60 questions in 90 minutes** from [`CCAAK/mock-exams/`](../../mock-exams/README.md) and fill in the per-domain scoring table in the [week plan](README.md) (Buổi D).
