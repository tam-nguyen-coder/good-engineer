# 📝 Practice Questions — Week 8: Observability & Operations

> **28 questions** · real CCDAK exam style, difficulty ≥ real exam · covers JMX & broker/producer/consumer metrics, request latency breakdown, consumer lag diagnosis, rebalance & exception troubleshooting, partition reassignment, leader election, rolling restart/upgrade, tiered storage, MirrorMaker 2 and capacity planning — plus 2 review questions (Week 2, Week 4).
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (number to choose is stated). Metric and config names are the **Java client / broker** names, as on the real exam.
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

---

### Question 1 — `[OBS · JMX · Single]`

An operations engineer wants to connect `jconsole` from a bastion host to a Kafka 4.3 broker that was started with `bin/kafka-server-start.sh config/server.properties`. The connection is refused on every port they try. Nothing about JMX has been configured yet. What is the MINIMUM change required to make the broker's MBeans reachable remotely?

- A. Add `jmx.enable=true` and `jmx.port=9999` to `server.properties` and restart the broker
- B. Set the environment variable `JMX_PORT=9999` before starting the broker; remote JMX is disabled by default
- C. Install the Prometheus JMX Exporter as a Java agent, because Kafka only exposes metrics through Prometheus
- D. Run `kafka-configs.sh --alter --entity-type brokers --add-config metric.reporters=JmxReporter`

### Question 2 — `[OBS · Broker metrics · Multi — Choose 2]`

A 3-broker KRaft cluster (separate 3-node controller quorum) hosts topics with `replication.factor=3` and `min.insync.replicas=2`. Broker 3 crashes because of a disk failure. Five minutes later the on-call engineer inspects JMX on the remaining brokers and the controllers. Which TWO observations are expected? (Choose two.)

- A. `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` is greater than 0 on brokers that lead partitions whose replica set includes broker 3
- B. `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` is greater than 0 for every partition that had a replica on broker 3
- C. The sum of `ActiveControllerCount` across all nodes is still exactly 1
- D. `UncleanLeaderElectionsPerSec` is greater than 0, because leaders had to be elected for broker 3's partitions
- E. `UnderMinIsrPartitionCount` is greater than 0, so all producers using `acks=all` are receiving `NotEnoughReplicasException`

### Question 3 — `[OBS · Request latency · Single]`

Producers report `request-latency-avg` of 180 ms against a target of 20 ms. On the brokers, `kafka.network:type=RequestMetrics,request=Produce` shows `RequestQueueTimeMs` ≈ 1 ms, `LocalTimeMs` ≈ 3 ms, `RemoteTimeMs` ≈ 170 ms, `ResponseQueueTimeMs` ≈ 1 ms, and `ResponseSendTimeMs` ≈ 1 ms. The producers use `acks=all`. Where is the time being spent?

- A. The request handler (I/O) thread pool is saturated; increase `num.io.threads`
- B. The leader is waiting for in-sync follower replicas to acknowledge the write; investigate follower brokers and inter-broker network
- C. The network threads cannot send responses fast enough; increase `num.network.threads`
- D. The leader's disk is slow to append; check `LogFlushRateAndTimeMs`

### Question 4 — `[OBS · Request latency · Single]`

A monitoring dashboard alerts because `kafka.network:type=RequestMetrics,name=RemoteTimeMs,request=FetchConsumer` has a mean of about 480 ms on every broker. Consumers are keeping up (lag is near zero), and producers are unaffected. The consumers use `fetch.min.bytes=1048576` and the default `fetch.max.wait.ms`. What should the engineer conclude?

- A. Follower replicas are lagging and the broker is waiting for replication before serving fetches
- B. This is expected: the broker intentionally parks the fetch until `fetch.min.bytes` is available or `fetch.max.wait.ms` (500 ms) elapses; the alert threshold is wrong
- C. The consumers are sending too many fetch requests; increase `max.poll.records`
- D. The brokers are running out of page cache and reading from disk; add RAM

### Question 5 — `[OBS · Broker threads · Single]`

During peak load a broker's `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` drops to 0.12 and `kafka.network:type=RequestChannel,name=RequestQueueSize` grows steadily, while `NetworkProcessorAvgIdlePercent` stays at 0.7. Which configuration change directly addresses the bottleneck?

- A. Increase `num.network.threads` from 3 to 8
- B. Increase `num.replica.fetchers` from 1 to 4
- C. Increase `num.io.threads` from 8 to 16
- D. Increase `socket.request.max.bytes`

### Question 6 — `[OBS · Prometheus / Grafana · Single]`

A platform team runs Kafka 4.3 brokers in containers and wants Prometheus to scrape broker metrics without exposing remote JMX outside the container. Which approach is the standard way to achieve this?

- A. Set `metric.reporters=io.prometheus.PrometheusReporter` in `server.properties`; Kafka ships a Prometheus reporter
- B. Start the broker JVM with `KAFKA_OPTS="-javaagent:/opt/jmx_prometheus_javaagent.jar=7071:/opt/kafka-jmx.yml"` and point Prometheus at port 7071; the YAML file maps MBean patterns to Prometheus metric names
- C. Enable `JMX_PORT=9999` and configure Prometheus with `scheme: jmx` to read the MBeans directly
- D. Run `kafka-run-class.sh org.apache.kafka.tools.JmxTool` as a sidecar and write the output to a file that Prometheus tails

### Question 7 — `[OBS · Producer metrics · Single]`

A producer sends about 20 000 small (100-byte) records per second with default configuration and `compression.type=lz4`. Its metrics show `batch-size-avg` ≈ 700 bytes, `records-per-request-avg` ≈ 7, `compression-rate-avg` ≈ 0.95 and `record-queue-time-avg` ≈ 5 ms. Broker CPU is elevated by the high request rate. Which single change would MOST improve batching and compression efficiency?

- A. Increase `linger.ms` from 5 to, for example, 50
- B. Increase `batch.size` from 16384 to 262144
- C. Decrease `max.in.flight.requests.per.connection` to 1
- D. Switch `compression.type` to `gzip`

### Question 8 — `[FUND · Week 2 review · min.insync.replicas · Single]`

A topic has `replication.factor=3` and `min.insync.replicas=2`. After two brokers go down simultaneously, the remaining broker reports `UnderMinIsrPartitionCount=12` for that topic. Two applications write to the topic: app X uses `acks=all`, app Y uses `acks=1`. What happens while the brokers are down?

- A. Both applications fail with `NotEnoughReplicasException`
- B. App X fails with `NotEnoughReplicasException` (retriable); app Y continues to write successfully to the lone leader, with no durability guarantee
- C. App Y fails because the leader refuses all writes when ISR is below `min.insync.replicas`; app X succeeds because it retries
- D. Both applications succeed; `min.insync.replicas` only affects consumers

### Question 9 — `[OBS · Consumer metrics · Single]`

A consumer application's `kafka.consumer:type=consumer-fetch-manager-metrics` shows `records-lag-max` at 8 million and `records-lead-min` decreasing steadily, now at 15 000. The topic has `retention.ms=3600000`. What is the MOST urgent risk indicated by `records-lead-min`?

- A. The consumer will soon exceed `max.poll.interval.ms` and be removed from the group
- B. Records will be deleted by retention before the consumer reads them, causing permanent data loss for this group
- C. The consumer's fetch buffer will exhaust `fetch.max.bytes`
- D. The consumer group coordinator will expire committed offsets after `offsets.retention.minutes`

### Question 10 — `[OBS · Rebalance diagnostics · Multi — Choose 2]`

A consumer processes each batch by calling a slow external API. Its logs show, several times per hour:

```
CommitFailedException: Commit cannot be completed since the group has already rebalanced and assigned the partitions to another member. This means that the time between subsequent calls to poll() was longer than the configured max.poll.interval.ms...
```

`time-between-poll-max` is around 320 000 ms. Which TWO changes directly address the root cause? (Choose two.)

- A. Decrease `max.poll.records` (default 500) so each `poll()` returns less work
- B. Increase `max.poll.interval.ms` (default 300 000) beyond the worst-case batch processing time
- C. Increase `session.timeout.ms` from 45 000 to 120 000
- D. Set `enable.auto.commit=false` and commit synchronously after each record
- E. Set `heartbeat.interval.ms` equal to `session.timeout.ms`

### Question 11 — `[DEV · Week 4 review · Static membership · Single]`

A consumer group of 12 pods on Kubernetes shows `rebalance-rate-per-hour` ≈ 40 and a sawtooth consumer-lag graph. Investigation shows that pods are frequently restarted by the orchestrator and come back within 20 seconds, and that each restart triggers two rebalances (leave + rejoin). The group uses the classic protocol with `CooperativeStickyAssignor`. Which change eliminates the rebalances caused by these quick restarts?

- A. Increase `max.poll.interval.ms` to 600 000
- B. Configure a stable `group.instance.id` per pod (static membership) and set `session.timeout.ms` higher than the typical restart time
- C. Switch back to `RangeAssignor`, which does not rebalance on member restart
- D. Set `group.initial.rebalance.delay.ms=0` on the brokers

### Question 12 — `[OBS · Consumer lag · Single]`

`kafka-consumer-groups.sh --bootstrap-server broker:9092 --describe --group billing` prints:

```
GROUP    TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG    CONSUMER-ID  HOST  CLIENT-ID
billing  invoices  0          40210           58900           18690  -            -     -
billing  invoices  1          39877           58311           18434  -            -     -
billing  invoices  2          40105           58720           18615  -            -     -
```

The LAG column grows every time the command is re-run. What does the output indicate?

- A. The consumers are running but are slower than the producers; add more consumer instances
- B. The group coordinator has not yet completed the rebalance; wait for `group.initial.rebalance.delay.ms`
- C. The consumers are assigned but are using `assign()` instead of `subscribe()`, so their IDs are hidden
- D. No consumer currently holds any partition of the group (the group is empty/inactive); the application is down or has left the group

### Question 13 — `[OBS · Consumer lag · Single]`

Topic `clicks` has 3 partitions. The `analytics` consumer group has been scaled from 3 to 5 instances to reduce a steadily growing lag, but lag keeps growing at the same rate. `kafka-consumer-groups.sh --describe --group analytics --members` shows two members with `#PARTITIONS = 0`. What should be done to actually increase consumption throughput?

- A. Scale the consumer group to 8 instances
- B. Increase the number of partitions of `clicks` (for example to 6 or more) and keep the consumer count ≤ the partition count; alternatively optimize the per-record processing in the three active consumers
- C. Set `partition.assignment.strategy=RoundRobinAssignor` so partitions are shared between all five members
- D. Increase `fetch.max.bytes` so each idle consumer can fetch from other consumers' partitions

### Question 14 — `[OBS · Consumer lag / hot partition · Single]`

A topic has 12 partitions and the consumer group has 12 instances, each assigned exactly one partition. Lag is near zero on 11 partitions but grows continuously on partition 7. `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec,topic=orders` on the broker leading partition 7 is roughly 10× higher than on other brokers. Records are keyed by `tenantId`, and one tenant generates most of the traffic. What is the correct remediation?

- A. Change the partitioning key (for example `tenantId` + a bucket suffix) or use a custom partitioner to spread the hot tenant across several partitions; adding consumers cannot help because a partition is consumed by at most one member
- B. Add more consumers to the group so that partition 7 is shared
- C. Increase `max.poll.records` on the consumer of partition 7
- D. Run `kafka-reassign-partitions.sh` to move partition 7 to a less loaded broker

### Question 15 — `[OBS · Consumer lag · Single]`

A developer compares two lag readings for the same consumer group taken at the same moment: the consumer's JMX metric `records-lag-max` reports 0, while `kafka-consumer-groups.sh --describe` reports `LAG` between 150 and 400 on each partition. The consumer uses `enable.auto.commit=true` with default settings. What explains the difference?

- A. The CLI tool is reading stale metadata and should be run with `--bootstrap-server` pointing to the group coordinator
- B. `records-lag-max` is computed from the consumer's current fetch position, whereas the CLI computes LAG from the last **committed** offset, which trails the position by up to `auto.commit.interval.ms` (5 s)
- C. The JMX metric is only updated on rebalance, so it is always stale
- D. The CLI counts uncommitted transactional records, which the consumer skips

### Question 16 — `[OBS · Exceptions / poison pill · Multi — Choose 2]`

A consumer deserializes JSON values. A producer bug wrote one malformed record to partition 4. Since then the consumer throws `RecordDeserializationException` on every `poll()`, crashes, is restarted by its supervisor, and immediately fails again; the group's lag on partition 4 keeps growing while other partitions are fine. Which TWO approaches let the consumer make progress without losing the rest of the partition? (Choose two.)

- A. Catch the deserialization error, publish the raw bytes plus headers (source topic, partition, offset, error reason) to a dead-letter topic, and continue
- B. Catch the error and `seek()` the partition to `failedOffset + 1` (Java `RecordDeserializationException` exposes the offset), optionally logging the record
- C. Set `auto.offset.reset=latest` so the consumer skips the bad record on the next restart
- D. Increase `max.poll.interval.ms` so the consumer has more time to deserialize
- E. Set `enable.idempotence=true` on the consumer

### Question 17 — `[OBS · Exceptions · Multi — Choose 2]`

A producer's callback receives various exceptions during a week of operation. Which TWO of the following are **non-retriable (fatal)** for the producer, meaning the client will NOT automatically retry the send and the application must react (fix the data, ACL, or recreate the producer)? (Choose two.)

- A. `NotLeaderOrFollowerException`
- B. `RecordTooLargeException`
- C. `NotEnoughReplicasException`
- D. `ProducerFencedException`
- E. `LeaderNotAvailableException`

### Question 18 — `[OBS · Exceptions · Single]`

A consumer group was stopped for 10 days for a project freeze. Its committed offsets are still present in `__consumer_offsets`. When it restarts against a topic with `retention.ms=604800000` (7 days), the consumer logs `OffsetOutOfRangeException` and, by default, starts reading from the newest records. Which setting caused that default behavior, and how would you make it read all remaining data instead?

- A. `auto.offset.reset` defaults to `latest`; set it to `earliest` to start from the oldest retained record
- B. `offsets.retention.minutes` expired the offsets; set it to `-1` to keep them forever
- C. `isolation.level=read_uncommitted` skipped the old records; set it to `read_committed`
- D. `fetch.max.wait.ms` timed out; increase it to 60 000

### Question 19 — `[OBS · Logging · Single]`

At 03:12 a partition briefly went offline and came back with a new leader. The team needs to reconstruct the exact sequence of leader and ISR changes for that partition on a Kafka 4.3 broker. Which log file should they read first?

- A. `kafka-authorizer.log`
- B. `state-change.log`
- C. `kafka-request.log`
- D. `log-cleaner.log`

### Question 20 — `[OBS · Operations · Single]`

A team adds broker 5 to a 4-broker KRaft cluster to relieve disk pressure. A week later `kafka.server:type=ReplicaManager,name=PartitionCount` on broker 5 is still 0, and `BytesInPerSec` on brokers 1–4 has not changed. Existing topics were not modified. Why, and what is the fix?

- A. Broker 5 registered as a controller-only node; change `process.roles=broker` and restart
- B. Broker 5 has a different `cluster.id`; reformat its storage with `kafka-storage.sh format`
- C. `auto.leader.rebalance.enable` is `false`; set it to `true` so leaders migrate to broker 5
- D. Kafka never moves existing partitions to new brokers automatically; generate and execute a plan with `kafka-reassign-partitions.sh` (`--generate`, `--execute`, `--verify`) or use Cruise Control

### Question 21 — `[OBS · Partition reassignment · Multi — Choose 2]`

An operator runs `kafka-reassign-partitions.sh --execute --reassignment-json-file move.json --throttle 10000000` to move several large partitions between brokers during business hours. Which TWO statements about this operation are correct? (Choose two.)

- A. The throttle (10 MB/s) is applied as dynamic broker configs `leader.replication.throttled.rate` / `follower.replication.throttled.rate`, and it is **removed only when `--verify` is run** after the reassignment completes
- B. If the throttled partitions receive more than 10 MB/s of new writes, the reassignment can never catch up; the throttle must be raised with `--execute --additional --throttle <higher value>`
- C. The throttle is automatically removed as soon as the reassignment finishes
- D. `--throttle` limits client produce throughput to the topic until the move completes
- E. Reassignment requires the affected topics to be paused for producers and consumers

### Question 22 — `[OBS · Leader election · Single]`

After a rolling restart of a 3-broker cluster, `kafka.server:type=ReplicaManager,name=LeaderCount` shows 90 leaders on broker 1 and 15 each on brokers 2 and 3, although every partition's replica list still starts with a different preferred broker. `auto.leader.rebalance.enable=true` with default settings. What is the FASTEST way to restore balanced leadership right now?

- A. Run `kafka-leader-election.sh --bootstrap-server broker:9092 --election-type preferred --all-topic-partitions`
- B. Run `kafka-reassign-partitions.sh --generate --broker-list 1,2,3` and execute the plan
- C. Run `kafka-leader-election.sh --election-type unclean --all-topic-partitions`
- D. Restart broker 1 so its leaders move to other brokers

### Question 23 — `[OBS · Operations · Single]`

A topic was created with 24 partitions but only ever needs 6. The team wants to reduce it to 6 partitions to lower the number of open files and the per-partition overhead. What is the correct approach in Kafka 4.3?

- A. `kafka-topics.sh --alter --topic t --partitions 6`
- B. `kafka-reassign-partitions.sh` with a JSON file listing only 6 partitions
- C. Partition count cannot be reduced; create a new topic with 6 partitions, mirror or re-produce the data into it (for example with MirrorMaker 2 or a Kafka Streams job), and switch clients over
- D. `kafka-delete-records.sh` for partitions 6–23, then `--alter --partitions 6`

### Question 24 — `[OBS · Rolling restart & upgrade · Multi — Choose 2]`

A team upgrades a 6-broker KRaft cluster from Kafka 4.2 to 4.3 with `replication.factor=3` and `min.insync.replicas=2`. Which TWO practices are required for a safe rolling upgrade? (Choose two.)

- A. Restart brokers one at a time, waiting until `UnderReplicatedPartitions` returns to 0 cluster-wide before stopping the next broker
- B. After all brokers run 4.3 and the cluster is verified, finalize with `kafka-features.sh --bootstrap-server ... upgrade --release-version 4.3`
- C. Restart brokers in pairs to halve the maintenance window; `min.insync.replicas=2` guarantees no write is rejected
- D. Set `inter.broker.protocol.version=4.3` in every `server.properties` before restarting
- E. Finalize the metadata version first, then restart the brokers with the new binaries

### Question 25 — `[OBS · Tiered storage · Multi — Choose 2]`

A company wants to retain a high-volume topic for 2 years while keeping broker disks small. The brokers already have `remote.log.storage.system.enable=true` and a `RemoteStorageManager` plugin configured. Which TWO statements are correct about enabling this at the topic level? (Choose two.)

- A. Set `remote.storage.enable=true` on the topic and use `local.retention.ms` (or `local.retention.bytes`) to control how long closed segments stay on local disk after being uploaded; `retention.ms` governs total retention including the remote tier
- B. The active segment is uploaded to remote storage immediately after each write
- C. Tiered storage cannot be enabled on a topic with `cleanup.policy=compact`
- D. `local.retention.ms` must be greater than `retention.ms`
- E. Consumers must set `remote.fetch.enable=true` to read segments that were tiered

### Question 26 — `[OBS · MirrorMaker 2 · Single]`

A team configures MirrorMaker 2 with `clusters = primary, dr` and `primary->dr.enabled = true`. After startup they see topic `primary.orders` on the `dr` cluster instead of `orders`. Later they plan an active/active setup (`dr->primary.enabled = true` as well). Which statement is correct?

- A. The rename is a bug; set `replication.policy.class=org.apache.kafka.connect.mirror.IdentityReplicationPolicy` for both flows to keep the name `orders` in active/active mode
- B. MirrorMaker 2 always uses the `<alias>.<topic>` naming and it cannot be changed
- C. The rename comes from `DefaultReplicationPolicy`, which prefixes the source cluster alias; it is required for active/active because it prevents replication loops and keeps local and remote writes in separate topics. `IdentityReplicationPolicy` keeps names but is only safe for one-way (active/passive or migration) flows
- D. The prefix appears because `topics` was set to `primary.*` instead of `.*`

### Question 27 — `[OBS · MirrorMaker 2 · Multi — Choose 2]`

A disaster-recovery design requires that, after failover, consumer groups on the DR cluster resume from offsets equivalent to where they stopped on the primary, and that the operations team can measure end-to-end replication latency. Which TWO MirrorMaker 2 connectors provide these capabilities? (Choose two.)

- A. `MirrorSourceConnector`
- B. `MirrorCheckpointConnector`
- C. `MirrorHeartbeatConnector`
- D. `MirrorOffsetConnector`
- E. `MirrorSinkConnector`

### Question 28 — `[OBS · Capacity planning · Single]`

A new topic must sustain 200 MB/s of produce throughput. Benchmarks show a single partition can absorb about 10 MB/s of writes on the chosen hardware, and a single consumer instance of the downstream application can process about 4 MB/s. The design should leave roughly 20% headroom. Approximately how many partitions should the topic have?

- A. 20
- B. 24
- C. 50
- D. 60
