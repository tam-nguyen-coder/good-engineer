# 📝 Practice Questions — Week 3: Replication & durability, quotas, throughput and JVM/OS tuning

> **30 questions** · real CCAAK exam style — scenario-first, "what does a competent administrator do next?" · covers the whole of Week 3 plus 2 review questions from Week 2.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (4 options) · `Multi` (choose the stated number) · `Matching` · `Ordering`.
> Tag: `[Domain · Topic · Format]`. Domains: `CFG` (Cluster Configuration), `FUND` (Fundamentals), `TROUBLE` (Troubleshooting), `OBS` (Observability).
> Anchored to **Apache Kafka 4.3** (KRaft-only) — where a default changed in 3.0 / 4.0, the current value is the correct one.
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[CFG · Durability matrix · Single]`

A 3-broker cluster hosts a topic that an administrator "hardened" after an incident review. `kafka-topics.sh --describe` prints:

```
Topic: payments  TopicId: 5Yk...  PartitionCount: 3  ReplicationFactor: 3  Configs: min.insync.replicas=3
  Topic: payments  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2,3,4  Elr:      LastKnownElr:
  Topic: payments  Partition: 1  Leader: 3  Replicas: 3,4,2  Isr: 3,4,2  Elr:      LastKnownElr:
  Topic: payments  Partition: 2  Leader: 4  Replicas: 4,2,3  Isr: 4,2,3  Elr:      LastKnownElr:
```

Broker 4 is then taken down for a routine kernel patch. Producers using `acks=all` immediately start failing for every partition. What is the correct assessment?

- A. The cluster is behaving correctly: `min.insync.replicas=3` with `replication.factor=3` leaves zero tolerance, so losing any single broker stops all `acks=all` writes. The durable-and-available setting for RF=3 is `min.insync.replicas=2`.
- B. The failure is caused by `unclean.leader.election.enable=false`; enabling it would let the writes continue.
- C. The partitions have no preferred leader available, so `auto.leader.rebalance.enable` must be turned on before writes can resume.
- D. Three partitions across three brokers is an unsupported layout; the topic needs at least six partitions so that a broker outage never removes a whole replica set.

### Question 2 — `[TROUBLE · min.insync.replicas · Single]`

At 02:14 an on-call administrator is paged. Producers on the `orders` topic (RF=3, `min.insync.replicas=2`) are failing with `NotEnoughReplicasException`, and `UnderMinIsrPartitionCount` is 8 on two brokers. One broker went offline five minutes earlier because of a disk controller fault. Which action should the administrator take FIRST?

- A. Set `min.insync.replicas=1` on the `orders` topic so that producers recover immediately.
- B. Set `unclean.leader.election.enable=true` cluster-wide to force new leaders for the affected partitions.
- C. Bring the failed broker back (or start a replacement and reassign its replicas) so the ISR returns to at least 2; the configuration is correct and is doing exactly what it was designed to do.
- D. Increase `replica.lag.time.max.ms` from 30000 to 120000 so the offline replica is not removed from the ISR.

### Question 3 — `[FUND · Replication exceptions · Single]`

Two different producer applications write to the same partition. During an ISR shrink, one logs:

```
org.apache.kafka.common.errors.NotEnoughReplicasException: Messages are rejected since there are fewer in-sync replicas than required.
```

and the other logs:

```
org.apache.kafka.common.errors.NotEnoughReplicasAfterAppendException: Messages are written to the log, but to fewer in-sync replicas than required.
```

What is the practical difference between the two?

- A. The first is thrown by the producer client before the request leaves; the second is thrown by the broker.
- B. The first means the leader rejected the write before appending anything to its log, so a retry is clean. The second means the leader had already appended the record to its own log when the ISR dropped below the minimum, so a retry can create a duplicate unless idempotence is enabled.
- C. The first applies to `acks=all` and the second to `acks=1`.
- D. The first is retriable and the second is fatal; the second requires restarting the producer.

### Question 4 — `[TROUBLE · ISR stability · Single]`

`IsrShrinksPerSec` and `IsrExpandsPerSec` on a 6-broker cluster oscillate several times a minute. No broker has restarted, `UnderMinIsrPartitionCount` is 0, and produce throughput is unchanged. What should the administrator investigate FIRST?

- A. Raise `replica.lag.max.messages` so followers are given more headroom before leaving the ISR.
- B. Lower `replica.lag.time.max.ms` so that flapping replicas are removed permanently instead of rejoining.
- C. Increase `min.insync.replicas` so that flapping replicas are no longer counted in the ISR.
- D. GC pause duration and disk write latency on the brokers whose replicas keep leaving the ISR, because both stall the fetcher threads long enough to exceed `replica.lag.time.max.ms` (30000 ms).

### Question 5 — `[FUND · High watermark · Single]`

A topic has RF=3 and `min.insync.replicas=2`. Two of the three replicas become unavailable, leaving a single in-sync replica. A producer configured with `acks=1` and `enable.idempotence=false` keeps writing successfully. A consumer reading the same partition reports no new records. Which explanation is correct?

- A. The consumer must set `isolation.level=read_committed` to see records written while the ISR is degraded.
- B. Consumers only read up to the high watermark, and under the strict-min-ISR rule the high watermark cannot advance while the ISR size is below `min.insync.replicas` — so the records exist in the leader's log but are not yet visible.
- C. The records were discarded by the leader because `min.insync.replicas` was not satisfied.
- D. The consumer group needs a rebalance; the records will appear once `auto.leader.rebalance.enable` moves leadership.

### Question 6 — `[CFG · Unclean leader election · Single]`

Every replica of the non-critical `clickstream-raw` partitions is offline after a rack power failure, `OfflinePartitionsCount` is 14, and the business accepts losing recent data to restore ingestion now. The administrator runs:

```
kafka-configs.sh --bootstrap-server kafka-1:9092 --alter \
  --entity-type topics --entity-name clickstream-raw \
  --add-config unclean.leader.election.enable=true
```

Ten seconds later the partitions are still offline. What is the MOST likely reason, and what should be done?

- A. Dynamic topic configs cannot change `unclean.leader.election.enable`; the value must be written to `zookeeper.connect` and the brokers restarted.
- B. `unclean.leader.election.enable` only exists as a broker-level setting; the topic-level override is silently ignored.
- C. In KRaft the unclean leader election thread runs on a periodic interval (5 minutes by default), so the change is correct but has not fired yet; running `kafka-leader-election.sh` with the unclean election type triggers it immediately.
- D. The topic must first be deleted and recreated, because unclean election is evaluated only at topic creation time.

### Question 7 — `[CFG · Unclean leader election · Multi — Choose 2]`

Which two statements about `unclean.leader.election.enable` in Kafka 4.3 are correct? (Choose two.)

- A. Its default value is `true`, which is why many clusters silently lose data during outages.
- B. Its default value is `false`, meaning a partition whose ISR is empty stays offline until an in-sync replica returns — availability is traded away in favour of consistency.
- C. It can be applied cluster-wide (`--entity-type brokers --entity-default`) or narrowed to a single topic (`--entity-type topics --entity-name <topic>`), so a low-value topic can be made available without exposing the whole cluster to data loss.
- D. When it is enabled and used, the elected replica's log becomes the source of truth, but Kafka first back-fills any committed messages that replica is missing from the other replicas.
- E. Its effect is visible in the metric `kafka.server:type=ReplicaManager,name=UncleanLeaderElectionsPerSec`.

### Question 8 — `[CFG · Eligible Leader Replicas · Single]`

An administrator describes a topic on a Kafka 4.3 cluster and sees:

```
Topic: ledger  PartitionCount: 1  ReplicationFactor: 3  Configs: min.insync.replicas=2
  Topic: ledger  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2  Elr: 3,4  LastKnownElr:
```

Broker 2 then fails. What happens to partition 0, and why?

- A. The partition goes offline, because only replicas listed in `Isr:` may be elected and broker 2 was the last one.
- B. The controller elects one of the unfenced replicas listed in `Elr:` (broker 3 or 4) as the new leader **without data loss**, because the strict-min-ISR rule guaranteed the high watermark could not advance past what those replicas already hold.
- C. The controller performs an unclean leader election automatically because ELR is enabled, accepting the risk of data loss.
- D. The partition stays writable on broker 2's log, which is replayed when broker 2 returns.

### Question 9 — `[CFG · Leader election order · Ordering]`

With the Eligible Leader Replicas feature enabled, put the sources the KRaft controller consults when electing a new partition leader into the order it tries them.

| # | Candidate source |
|---|---|
| 1 | The last known leader, if it is unfenced |
| 2 | The ELR set, choosing a replica that is not fenced |
| 3 | The ISR, if it is not empty |

- A. 1 → 3 → 2
- B. 2 → 3 → 1
- C. 3 → 2 → 1
- D. 3 → 1 → 2

### Question 10 — `[CFG · Preferred leader · Single]`

After patching and restarting broker 3 of a 5-broker cluster, monitoring shows broker 3 handling almost no produce or fetch traffic while the other four brokers are saturated. `UnderReplicatedPartitions` is 0 everywhere and broker 3 appears in the `Replicas:` and `Isr:` lists of many partitions. What is happening and what is the standard remedy?

- A. A restarted broker rejoins as a follower for all of its partitions, so it serves no client reads or writes until leadership is rebalanced. With `auto.leader.rebalance.enable=true` the controller fixes this within `leader.imbalance.check.interval.seconds` (300 s); otherwise run `kafka-leader-election.sh --election-type preferred --all-topic-partitions`.
- B. The broker did not re-register with the controller; it must be re-formatted with `kafka-storage.sh format`.
- C. Run `kafka-preferred-replica-election.sh --zookeeper zk:2181` to move leadership back, because the broker-side rebalance only covers internal topics.
- D. Broker 3's replicas are still catching up; the imbalance resolves once `replica.lag.time.max.ms` (30000 ms) elapses.

### Question 11 — `[CFG · Internal topics · Single]`

An engineer starts a single-broker Kafka 4.3 instance for a local integration test. The broker starts cleanly, but the first transactional producer fails and `server.log` contains:

```
org.apache.kafka.common.errors.InvalidReplicationFactorException: Replication factor: 3 larger than available brokers: 1.
```

Which change fixes this?

- A. Set `default.replication.factor=1`; internal topics inherit it.
- B. Set `min.insync.replicas=1`; the transaction state topic derives its replication factor from it.
- C. Create `__transaction_state` manually with `kafka-topics.sh --replication-factor 1` after the broker has started, then restart the producer.
- D. Set `offsets.topic.replication.factor=1`, `transaction.state.log.replication.factor=1` and `transaction.state.log.min.isr=1` in the broker configuration, because those internal-topic settings default to 3 / 3 / 2 and are evaluated when the internal topic is first created.

### Question 12 — `[CFG · Internal topics · Multi — Choose 2]`

Which two statements about the internal-topic durability settings in Kafka 4.3 are correct? (Choose two.)

- A. All three are dynamic, cluster-wide settings that can be changed with `kafka-configs.sh` while the brokers are running.
- B. `offsets.topic.replication.factor` and `transaction.state.log.replication.factor` both default to **3**, and `transaction.state.log.min.isr` defaults to **2**.
- C. `transaction.state.log.min.isr` applies to every internal topic, including `__consumer_offsets`.
- D. They are `read-only` configurations: changing them requires a broker restart, and the new value only affects the internal topic if that topic has not been created yet.
- E. Raising `offsets.topic.replication.factor` on an existing cluster automatically increases the replication factor of the existing `__consumer_offsets` partitions.

### Question 13 — `[CFG · Quota types · Single]`

A shared cluster is destabilised every morning by one tenant's CI pipeline, which creates and deletes several hundred short-lived topics in a few minutes. Controller request queue time spikes and unrelated topic operations time out. Bandwidth and CPU usage from that tenant are modest. Which quota should the administrator apply?

- A. `producer_byte_rate` on the tenant's user principal.
- B. `request_percentage` on the tenant's user principal.
- C. `controller_mutation_rate` on the tenant's user principal — the quota type introduced by KIP-599 specifically to rate-limit topic create / delete / partition-add operations.
- D. `consumer_byte_rate` on the tenant's user principal.

### Question 14 — `[CFG · Quota precedence · Matching]`

A cluster has exactly these four client quota entries configured:

| Letter | Quota entry as configured with `kafka-configs.sh` |
|---|---|
| V | `--entity-type users --entity-name analytics --entity-type clients --entity-name etl-01` |
| W | `--entity-type users --entity-name analytics` |
| X | `--entity-type clients --entity-name etl-01` |
| Y | `--entity-type clients --entity-default` |

Match each incoming connection to the entry whose quota the broker applies.

| # | Connection |
|---|---|
| 1 | user `analytics`, client-id `etl-01` |
| 2 | user `analytics`, client-id `etl-99` |
| 3 | user `reporting`, client-id `etl-01` |
| 4 | user `reporting`, client-id `adhoc-7` |

- A. 1-V · 2-W · 3-X · 4-Y
- B. 1-V · 2-X · 3-W · 4-Y
- C. 1-W · 2-W · 3-X · 4-Y
- D. 1-X · 2-Y · 3-X · 4-W

### Question 15 — `[TROUBLE · Quota symptoms · Single]`

A team reports that their producer cannot exceed a stubborn ceiling. `kafka-producer-perf-test.sh` run with their `client.id` prints:

```
20000 records sent, 1024.3 records/sec (0.98 MB/sec), 4871.22 ms avg latency, 9640.00 ms max latency, 4102 ms 50th, 8871 ms 95th, 9502 ms 99th, 9633 ms 99.9th.
```

Broker logs contain no ERROR or WARN lines for this client, the producer logs no exceptions, and `UnderReplicatedPartitions` is 0. What should the administrator check next?

- A. `max.request.size` and `buffer.memory` on the producer, since the latency profile indicates the accumulator is full.
- B. A client quota: throttling delays the response instead of raising an error, so the symptom is exactly "throughput capped, logs clean". Check `produce-throttle-time-avg` on the client and the broker MBean `kafka.server:type=Produce,user=…,client-id=…` attribute `throttle-time`, then `kafka-configs.sh --describe --entity-type users`.
- C. `num.io.threads`, because a saturated request handler pool always manifests as high produce latency.
- D. `message.max.bytes` on the broker, because oversized batches are silently dropped and re-sent.

### Question 16 — `[CFG · Quota enforcement · Single]`

How does a Kafka broker enforce a `producer_byte_rate` quota once a client group exceeds it?

- A. It returns `QuotaViolationException` to the producer, which retries after a back-off.
- B. It closes the client's connection and forces a metadata refresh, which spreads the load to other brokers.
- C. It silently drops the records that exceed the quota, which is why `FailedProduceRequestsPerSec` rises.
- D. It computes the delay needed to bring the client back under its quota, returns the response immediately carrying that delay, and mutes the client's socket channel until the delay expires — no error reaches the application.

### Question 17 — `[CFG · Quota scope · Multi — Choose 2]`

An administrator sets `producer_byte_rate=10485760` (10 MiB/s) for user `ingest` on a cluster of 8 brokers. Monitoring later shows that user producing at roughly 62 MiB/s across the cluster, and every broker reports a non-zero `throttle-time` for it. Which two statements are correct? (Choose two.)

- A. Client quotas are enforced **per broker**, so the cluster-wide ceiling for this user is approximately 10 MiB/s × 8 = 80 MiB/s; 62 MiB/s is therefore expected behaviour, not a bug.
- B. The quota is being ignored because `producer_byte_rate` must be expressed in kilobytes per second.
- C. The 10 MiB/s value is a cluster-wide ceiling, so 62 MiB/s proves quota enforcement has broken and the brokers need a rolling restart.
- D. All producer instances that share the same user principal and client-id share a single quota allocation on each broker.
- E. Quota entries are stored in ZooKeeper under `/config/users`, so the brokers need a rolling restart before a new value takes effect.

### Question 18 — `[CFG · Request rate quota · Single]`

A broker runs with the default `num.io.threads` and `num.network.threads`. An administrator wants to limit one tenant to the equivalent of two full request-handling threads. Which `request_percentage` value is correct, and what is the broker's total capacity?

- A. `request_percentage=200`; total capacity is `(8 + 3) × 100` = 1100%.
- B. `request_percentage=2`; total capacity is 100%.
- C. `request_percentage=18`; total capacity is 100%, because the quota is a share of the broker's whole CPU.
- D. `request_percentage=200`; total capacity is `8 × 100` = 800%, because network threads are exempt from request quotas.

### Question 19 — `[TROUBLE · Replication throughput · Single]`

A broker was down for 40 minutes during a hardware swap. It has been back for 12 minutes, is registered with the controller, and `UnderReplicatedPartitions` is slowly falling from 340 but is still at 290. Disk and network on the returning broker are far from saturated. Which action is the cheapest, most reversible way to speed up the catch-up?

- A. Increase `num.replica.fetchers` from 1 to 4 with `kafka-configs.sh --alter --entity-type brokers --entity-default`; it is a cluster-wide dynamic config, so no broker restart is needed.
- B. Increase `replica.fetch.max.bytes` from 1048576 to 10485760 and perform a rolling restart of every broker.
- C. Temporarily set `min.insync.replicas=1` so that the under-replicated partitions stop being reported.
- D. Run `kafka-reassign-partitions.sh` to move the lagging replicas onto brokers that are already in sync.

### Question 20 — `[CFG · Replica fetch sizing · Single]`

A topic is configured with `max.message.bytes=8388608` (8 MiB) to carry large payloads, and the brokers have `message.max.bytes` raised to match. An administrator worries that followers cannot replicate these records because `replica.fetch.max.bytes` is left at its default. Which statement is accurate for Kafka 4.3?

- A. Replication will stall permanently; `replica.fetch.max.bytes` must always be greater than or equal to the largest message.
- B. `replica.fetch.response.max.bytes` defaults to 1048576 (1 MiB), so the 8 MiB record can never be replicated.
- C. `replica.fetch.max.bytes` defaults to 1048576 (1 MiB) per partition and `replica.fetch.response.max.bytes` defaults to 10485760 (10 MiB) for the whole response, but neither is an absolute maximum: if the first record batch in the first non-empty partition is larger, it is still returned so that progress can be made. Raising them is a throughput optimisation, not a correctness fix.
- D. Followers bypass `replica.fetch.max.bytes` entirely and always use `socket.request.max.bytes` (100 MiB).

### Question 21 — `[CFG · Broker compression · Single]`

Grafana shows broker CPU on all five brokers climbing from 35% to 80% after a change window, while `BytesInPerSec` and `MessagesInPerSec` are flat and GC activity is unchanged. The change log shows exactly one broker configuration was altered cluster-wide: `compression.type`. What almost certainly happened?

- A. `compression.type` was set to `uncompressed`, so the brokers now spend CPU compressing every batch before writing it.
- B. `compression.type` was changed from the default `producer` to an explicit codec such as `zstd`, so every batch is now decompressed and re-compressed by the broker instead of being stored exactly as the producer sent it — which also breaks the zero-copy path when serving consumers.
- C. `compression.type` was set to `producer`, which forces the broker to validate each record's checksum individually.
- D. `compression.type` has no CPU impact on the broker; the cause must be `num.io.threads`.

### Question 22 — `[OBS · Thread tuning · Single]`

Produce p99 latency on one broker has tripled over two days. Host CPU is at 42%, disk utilisation is at 30%, and JMX reports:

```
kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent  = 0.08
kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent          = 0.61
kafka.network:type=RequestMetrics,name=RemoteTimeMs,request=Produce          = 4.2 (mean)
```

What should the administrator change FIRST?

- A. Increase `num.network.threads`, because the socket layer is the entry point for every request.
- B. Increase `queued.max.requests` from 500 so that requests stop being rejected while the handlers catch up.
- C. Increase `num.io.threads` (default 8): the request handler pool is 92% busy, far below the healthy `RequestHandlerAvgIdlePercent` guidance of > 0.3, while the network processors are comfortable and `RemoteTimeMs` shows followers are not the bottleneck. It is a cluster-wide dynamic config.
- D. Switch producers to `acks=1`, because `RemoteTimeMs` proves replication is the bottleneck.

### Question 23 — `[CFG · JVM heap · Single]`

A broker on a 64 GB host is started with `KAFKA_HEAP_OPTS="-Xms32g -Xmx32g"`. The team reports occasional 1.5–2 second stalls, `IsrShrinksPerSec` spikes that correlate with those stalls, and consumer fetches that increasingly hit disk instead of memory. What is the correct fix and the reasoning behind it?

- A. Raise the heap further, to 48 GB, so that garbage collection runs less often.
- B. Reduce the heap to about 6 GB and keep G1GC. Kafka keeps data in the OS page cache, not on the JVM heap, so a smaller heap both shortens GC pauses (which were long enough to push followers out of the ISR) and leaves far more RAM for the page cache.
- C. Keep the 32 GB heap but switch to the serial collector to make pauses predictable.
- D. Leave the heap alone and raise `replica.lag.time.max.ms` so that GC pauses stop removing replicas from the ISR.

### Question 24 — `[CFG · JVM tuning · Multi — Choose 2]`

Which two statements match the JVM guidance published in the Apache Kafka 4.3 operations documentation? (Choose two.)

- A. The documented argument set is `-Xmx6g -Xms6g -XX:MetaspaceSize=96m -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M` — a fixed 6 GB heap collected by G1GC.
- B. `-Xms` should be set well below `-Xmx` so the JVM can release memory back to the OS between load peaks.
- C. The reference LinkedIn cluster running those arguments (60 brokers, 50k partitions, 800k messages/sec) sees a 90th-percentile GC pause of about 21 ms and fewer than one young GC per second.
- D. Kafka requires the ZGC collector from Java 17 onwards; G1GC is no longer supported for brokers.
- E. Broker heap size is set in `server.properties` with the `broker.heap.bytes` property.

### Question 25 — `[CFG · OS tuning · Multi — Choose 2]`

A new broker fleet is being provisioned on Linux. Which two OS-level settings match the published recommendations for Kafka brokers? (Choose two.)

- A. Set `vm.swappiness=0` so that the kernel is forbidden from swapping under any circumstances.
- B. Allow at least **100,000** file descriptors for the broker process, because every log segment and every client connection consumes descriptors.
- C. Mount the Kafka data filesystem with `atime` enabled so that segment access times can be used to tune retention.
- D. Set `vm.swappiness` to a very low but **non-zero** value such as **1**: swapping hurts Kafka because it steals memory from the page cache, but 0 removes the safety net and lets the OS kill the process under memory pressure instead.
- E. Leave the default file-descriptor limit of 1,024, since Kafka memory-maps its index files and therefore needs very few descriptors.

### Question 26 — `[OBS · ISR metrics · Single]`

A dashboard for one broker shows:

```
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions  = 0
kafka.server:type=ReplicaManager,name=AtMinIsrPartitionCount     = 17
kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount  = 0
```

How should the administrator read this, and what is the appropriate response?

- A. Seventeen partitions are already rejecting `acks=all` writes; treat it as a page-worthy incident.
- B. The three metrics are mutually exclusive, so the data is inconsistent and JMX scraping must be misconfigured.
- C. Seventeen partitions are offline and need an unclean leader election.
- D. Every partition still has its full replica set, but seventeen partitions currently sit with `|ISR|` exactly equal to `min.insync.replicas` — one more replica loss stops `acks=all` writes on them. It is an early warning: investigate why those replicas are marginal, but writes are not blocked yet.

### Question 27 — `[CFG · Storage and filesystem · Single]`

A team is choosing the disk layout for new brokers. Which combination matches the Apache Kafka and Confluent guidance?

- A. Put the OS, application logs and Kafka data on one large RAID 5 volume so that a single disk failure never takes the broker down.
- B. Use network-attached storage so that a broker can be rebuilt on another host without copying data.
- C. Use XFS (measured "Request Local Time" of about 160 ms versus 250 ms+ for the best EXT4 configuration), mount with `noatime`, use multiple drives, and keep the OS and application-log disks separate from the Kafka data disks.
- D. Use a single EXT4 volume with journaling disabled and `data=writeback`, which the documentation describes as the safe default for production.

### Question 28 — `[CFG · Dynamic vs static config · Matching]`

An administrator must apply four changes to a running production cluster during business hours. Match each configuration change to how it can be applied.

| # | Configuration change |
|---|---|
| 1 | `num.replica.fetchers` from 1 to 4 on every broker |
| 2 | `replica.lag.time.max.ms` from 30000 to 45000 |
| 3 | `producer_byte_rate` for user `ingest` |
| 4 | Broker heap from 1 GB to 6 GB |

| Letter | How it is applied |
|---|---|
| V | `kafka-configs.sh --entity-type users`; written to the metadata log and effective immediately on every broker |
| W | `kafka-configs.sh --entity-type brokers --entity-default`; cluster-wide dynamic config, no restart |
| X | `read-only` broker config — requires editing the broker configuration and performing a rolling restart |
| Y | Environment variable (`KAFKA_HEAP_OPTS`) outside Kafka's own configuration — requires restarting each broker process |

- A. 1-X · 2-W · 3-V · 4-Y
- B. 1-W · 2-X · 3-V · 4-Y
- C. 1-W · 2-V · 3-X · 4-Y
- D. 1-W · 2-X · 3-Y · 4-V

### Question 29 — `[CFG · Week 2 review · Single]`

An administrator sets `retention.ms=3600000` (1 hour) on a low-traffic topic to control disk usage. Twelve hours later, `kafka-log-dirs.sh` still shows several hundred megabytes for that topic and the oldest records are still readable. Broker logs show no errors. What is the explanation?

- A. `retention.ms` only applies to compacted topics; a delete-policy topic needs `retention.bytes`.
- B. Retention is evaluated per **closed** log segment: the currently active segment is never deleted, and on a low-traffic topic it can stay open for a long time. Lowering `segment.ms` (or `segment.bytes`) makes segments roll — and therefore become eligible for deletion — sooner.
- C. `log.retention.check.interval.ms` defaults to 24 hours, so the cleanup thread has not run yet.
- D. Topic-level `retention.ms` is ignored unless `log.retention.hours` is also lowered on every broker.

### Question 30 — `[CFG · Week 2 review · Multi — Choose 2]`

A broker is configured with `log.dirs=/data/d1,/data/d2,/data/d3` (JBOD). Which two statements are correct? (Choose two.)

- A. Kafka spreads partitions across the configured directories by **partition count**, not by free space or bytes written, so uneven partition sizes lead to uneven disk usage.
- B. Kafka stripes each partition's segments across all configured directories to maximise throughput.
- C. Each partition's log lives entirely inside one of the directories; Kafka never splits a single partition across two log directories.
- D. Losing one of the three disks takes the whole broker offline, because a broker cannot run with a missing log directory.
- E. Adding a fourth directory to `log.dirs` makes the broker automatically redistribute existing partitions across all four directories.

---

> ✅ Done? Check your answers in [answers.md](answers.md), log every wrong answer under one of the five buckets (durability / ELR & leader election / quota / throughput tuning / JVM-OS), then build the **⭐ MINI-MOCK CFG** (~30 questions mixed from Weeks 2–3) described in the [week plan](README.md#-buổi-d--practice--review-2h). The gate to Week 4 is **≥ 70%**.
