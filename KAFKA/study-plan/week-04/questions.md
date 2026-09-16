# 📝 Practice Questions — Week 4: Consumer Deep Dive (poll loop, groups, rebalance, KIP-848, offsets, lag, share groups)

> **30 questions** · real CCDAK exam style, difficulty ≥ real exam · covers the full Week 4 material + 2 review questions from Weeks 2–3.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (number to choose is stated). Domains: `FUND` (Fundamentals), `DEV` (Application Development).
> Back to [week plan](README.md) · [master plan](../../KAFKA-STUDY-PLAN.md)

---

### Question 1 — `[DEV · Fetch tuning · Single]`

A consumer application reads from a topic that receives only a few small records per second. Broker CPU profiling shows that this consumer issues thousands of tiny fetch requests per minute, most of them returning almost no data. The team wants the broker to wait until at least 64 KB of data is available, but never longer than 1 second, before responding. Which configuration change on the consumer achieves this?

- A. `max.partition.fetch.bytes=65536` and `request.timeout.ms=1000`
- B. `fetch.min.bytes=65536` and `fetch.max.wait.ms=1000`
- C. `fetch.max.bytes=65536` and `max.poll.interval.ms=1000`
- D. `max.poll.records=64` and `heartbeat.interval.ms=1000`

### Question 2 — `[DEV · Poll loop · Single]`

A developer sets `max.poll.records=50` on a Java consumer, expecting the broker to send at most 50 records per fetch request and thereby reduce network usage. After deployment, network traffic between the broker and the consumer is unchanged. What is the correct explanation?

- A. `max.poll.records` must be set on the broker, not on the consumer
- B. The default value 500 is a hard minimum that cannot be lowered
- C. `max.poll.records` only limits how many records a single `poll()` call returns to the application from the consumer's internal buffer; it does not change the size of the underlying fetch requests, which are governed by `fetch.max.bytes` and `max.partition.fetch.bytes`
- D. The consumer ignores `max.poll.records` unless `enable.auto.commit=false`

### Question 3 — `[FUND · Group coordinator · Single]`

A Kafka 4.3 cluster has 3 brokers and a consumer group with `group.id=payments`. Which statement correctly describes how the group coordinator for this group is chosen?

- A. The broker that is the leader of the partition `hash("payments") % 50` of the internal topic `__consumer_offsets` (50 partitions by default) becomes the group coordinator
- B. The KRaft active controller always acts as the group coordinator for every group
- C. The first consumer to join the group is elected as the group coordinator
- D. The broker with the lowest `node.id` is the coordinator for all groups

### Question 4 — `[DEV · Classic protocol · Single]`

Under the classic consumer group protocol (`group.protocol=classic`), which component actually computes the partition assignment for the group during a rebalance?

- A. The group coordinator broker, using `group.remote.assignor`
- B. One consumer chosen as the group leader (usually the first to send `JoinGroup`), running the configured `partition.assignment.strategy` and sending the result to the coordinator in `SyncGroup`
- C. The KRaft controller, which persists the assignment in `__cluster_metadata`
- D. Each consumer independently, by hashing its `client.id` against the partition count

### Question 5 — `[DEV · Assignors · Single]`

Three consumers with identical subscriptions consume from 4 topics, each with 4 partitions (16 partitions total). Monitoring shows that one consumer consistently owns 8 partitions while the other two own 4 each, even after several rebalances. The consumers use the default `partition.assignment.strategy`. What is the MOST likely cause?

- A. The broker-side `uniform` assignor is misconfigured
- B. Two of the consumers exceed `max.poll.interval.ms` and are periodically kicked out
- C. The `RangeAssignor` assigns partitions per topic and gives the remainder of each topic to the first consumer, so the imbalance accumulates across topics; use `RoundRobinAssignor` or `CooperativeStickyAssignor` instead
- D. `group.initial.rebalance.delay.ms` is too low, so the assignment is computed before all members have joined

### Question 6 — `[DEV · Cooperative rebalance · Single]`

A consumer group currently runs with `partition.assignment.strategy=RangeAssignor` and suffers from stop-the-world rebalances. The team wants to move to `CooperativeStickyAssignor` **without stopping the whole group**. What is the correct procedure?

- A. Set `partition.assignment.strategy=CooperativeStickyAssignor` on all instances and do one rolling restart
- B. Set `group.remote.assignor=cooperative-sticky` and restart the brokers
- C. Stop all consumers, delete the group, and restart with `CooperativeStickyAssignor`
- D. Perform two rolling bounces: first set the strategy to `[CooperativeStickyAssignor, RangeAssignor]` on every instance, then remove `RangeAssignor` from the list in a second rolling bounce

### Question 7 — `[DEV · Eager vs cooperative · Multi — Choose 2]`

Which two statements correctly describe the difference between eager and cooperative (incremental) rebalancing in the classic protocol? (Choose two.)

- A. In eager rebalancing, only the partitions that change owner are revoked
- B. In eager rebalancing, every member revokes all of its partitions before rejoining, so processing stops for the whole group until the new assignment is distributed
- C. Cooperative rebalancing requires the `StickyAssignor`
- D. Cooperative rebalancing typically completes in two consecutive rebalances: the first revokes only the partitions that must move, the second assigns them to their new owners, while unaffected partitions keep being processed
- E. Cooperative rebalancing is only available when `group.protocol=consumer`

### Question 8 — `[DEV · KIP-848 · Multi — Choose 2]`

A team migrates a consumer application to Kafka 4.3 and sets `group.protocol=consumer` (the KIP-848 protocol). Their existing `consumer.properties` also contains `session.timeout.ms=60000`, `heartbeat.interval.ms=20000`, `partition.assignment.strategy=org.apache.kafka.clients.consumer.RoundRobinAssignor`, `max.poll.interval.ms=600000`. Which two statements are correct? (Choose two.)

- A. `session.timeout.ms`, `heartbeat.interval.ms` and `partition.assignment.strategy` are ignored with the new protocol; the session timeout and heartbeat interval are now group configurations on the broker (`consumer.session.timeout.ms` default 45000 ms, `consumer.heartbeat.interval.ms` default 5000 ms)
- B. The consumer fails to start because `partition.assignment.strategy` is incompatible with `group.protocol=consumer`
- C. `max.poll.interval.ms` is still a client-side configuration and still applies with the new protocol
- D. `heartbeat.interval.ms=20000` will be honored because the consumer still sends heartbeats
- E. The `RoundRobinAssignor` will run on the broker as the server-side assignor

### Question 9 — `[DEV · KIP-848 · Single]`

A developer wants a consumer group to use the next-generation rebalance protocol with the broker-side assignor that balances partitions evenly and minimizes partition movement. Which consumer configuration is correct?

- A. `group.protocol=classic` and `partition.assignment.strategy=CooperativeStickyAssignor`
- B. `group.protocol=consumer` and `group.remote.assignor=uniform` (which is also the default server-side assignor)
- C. `group.protocol=consumer` and `partition.assignment.strategy=StickyAssignor`
- D. `group.protocol=incremental` and `group.remote.assignor=sticky`

### Question 10 — `[DEV · Static membership · Single]`

A consumer group of 12 instances runs on Kubernetes. Every rolling deployment triggers two rebalances per pod (one when the pod leaves, one when it rejoins), causing 24 rebalances and minutes of lag. The team wants a restarted pod to get back its previous partitions without triggering a rebalance, as long as it returns within a few minutes. Which approach is correct?

- A. Set `enable.auto.commit=false` so that leaving the group does not commit offsets
- B. Increase `max.poll.interval.ms` to 10 minutes on every pod
- C. Assign each pod a unique, stable `group.instance.id` (static membership, KIP-345) and set `session.timeout.ms` high enough to cover the restart window
- D. Use `assign()` with a fixed partition list per pod instead of `subscribe()`

### Question 11 — `[DEV · Liveness · Multi — Choose 2]`

A consumer processes each batch of 500 records by calling a slow external API; a batch sometimes takes 7 minutes. The consumer logs show heartbeats are sent every 3 seconds, yet the consumer is regularly removed from the group and later throws `CommitFailedException`. Which two changes would directly address the root cause? (Choose two.)

- A. Increase `session.timeout.ms` from 45000 to 600000
- B. Reduce `max.poll.records` (for example to 50) so each `poll()` loop iteration finishes well within `max.poll.interval.ms`
- C. Decrease `heartbeat.interval.ms` to 1000
- D. Increase `max.poll.interval.ms` (default 300000 ms) above the worst-case processing time of one batch
- E. Set `enable.auto.commit=true` so commits are handled by the heartbeat thread

### Question 12 — `[DEV · Consumer configs · Single]`

Which set of values matches the **default** Kafka 4.3 Java consumer configuration?

- A. `session.timeout.ms=45000`, `heartbeat.interval.ms=3000`, `max.poll.interval.ms=300000`, `max.poll.records=500`, `auto.offset.reset=latest`
- B. `session.timeout.ms=10000`, `heartbeat.interval.ms=3000`, `max.poll.interval.ms=300000`, `max.poll.records=500`, `auto.offset.reset=earliest`
- C. `session.timeout.ms=45000`, `heartbeat.interval.ms=15000`, `max.poll.interval.ms=60000`, `max.poll.records=1000`, `auto.offset.reset=latest`
- D. `session.timeout.ms=30000`, `heartbeat.interval.ms=3000`, `max.poll.interval.ms=300000`, `max.poll.records=500`, `auto.offset.reset=none`

### Question 13 — `[DEV · Exceptions · Single]`

A consumer with `enable.auto.commit=false` calls `commitSync()` after processing a large batch and receives:

```
org.apache.kafka.clients.consumer.CommitFailedException: Offset commit cannot be completed since the consumer is not part of an active group for auto partition assignment; it is likely that the consumer was kicked out of the group.
```

What is the MOST likely cause?

- A. The broker's `offsets.retention.minutes` expired while the batch was being processed
- B. `isolation.level=read_committed` prevents committing offsets of uncommitted transactions
- C. The time between two consecutive `poll()` calls exceeded `max.poll.interval.ms`, so the consumer proactively left the group and its partitions were reassigned before the commit
- D. The consumer used `assign()` and therefore cannot commit offsets

### Question 14 — `[DEV · Offset semantics · Single]`

A consumer processes records from partition 3 of topic `orders` and the last record it successfully processed has offset **41**. It uses manual commits with `commitSync(Map<TopicPartition, OffsetAndMetadata>)`. Which offset should it commit so that, after a restart, it resumes without reprocessing or skipping any record?

- A. 41
- B. 42
- C. 40
- D. 41 with the metadata string `"processed"`

### Question 15 — `[DEV · Auto commit · Single]`

A consumer uses the defaults (`enable.auto.commit=true`, `auto.commit.interval.ms=5000`) and processes records synchronously inside the poll loop. It crashes 3 seconds after the last automatic commit, while processing records returned by the most recent `poll()`. What happens after the consumer restarts?

- A. Some records are processed a second time (at-least-once): the offsets of records returned by the last polls were not yet committed, so the consumer resumes from the last committed offset
- B. Some records are lost (at-most-once): the auto-commit committed offsets before processing completed
- C. Nothing is duplicated or lost, because auto commit is exactly-once
- D. The consumer restarts from the beginning of every partition because `auto.offset.reset=latest`

### Question 16 — `[DEV · commitAsync · Single]`

Why does `commitAsync()` **not** retry a failed commit by default, whereas `commitSync()` does?

- A. Because `commitAsync()` is only allowed with `assign()`, where retries are meaningless
- B. Because the broker rejects asynchronous commits with `UnsupportedVersionException` on retry
- C. Because `commitAsync()` cannot return exceptions to the caller
- D. Because a retried asynchronous commit for an older offset could complete after a later commit for a newer offset and overwrite it, moving the committed position backwards; `commitSync()` blocks, so ordering is preserved and it can retry retriable errors safely

### Question 17 — `[DEV · Commit patterns · Multi — Choose 2]`

A team wants high throughput and no message loss for a consumer with `enable.auto.commit=false`. Duplicates during failures are acceptable. Which two practices together form the recommended pattern? (Choose two.)

- A. Call `commitAsync()` after each batch inside the poll loop for throughput
- B. Call `commitSync()` before processing each batch so the offsets are always durable
- C. Call `commitSync()` in a `finally` block on shutdown and in `ConsumerRebalanceListener.onPartitionsRevoked()` to make sure the last offsets are committed before losing partitions
- D. Commit offsets from a separate thread every second to avoid blocking the poll loop
- E. Call `commitAsync()` with a callback that retries the same offset until it succeeds

### Question 18 — `[DEV · auto.offset.reset · Single]`

A consumer application is deployed with `auto.offset.reset=earliest` and `group.id=analytics`, a group that has been running and committing offsets for months. The team expects the new deployment to reprocess the topic from the beginning, but it continues from where the previous deployment stopped. Why?

- A. `auto.offset.reset=earliest` requires `enable.auto.commit=false`
- B. `auto.offset.reset` only applies when the group has **no committed offset** for a partition (or the committed offset is out of range); because `analytics` already has committed offsets, the consumer resumes from them
- C. `earliest` is only valid for `assign()` consumers
- D. The brokers override the client value with `log.retention.hours`

### Question 19 — `[DEV · Offset retention · Single]`

A batch consumer group runs once a month, commits its offsets and then shuts down all members. The next month it unexpectedly starts consuming from the **latest** offset and skips the month of data. All consumer configurations are default. What is the cause?

- A. `auto.offset.reset=latest` always wins over committed offsets for inactive groups
- B. `log.retention.hours=168` deleted the committed offsets together with the data
- C. The group was empty for longer than `offsets.retention.minutes` (default 10080 = 7 days), so the broker expired its committed offsets; on restart the consumer fell back to `auto.offset.reset=latest`
- D. Committed offsets are stored in the consumer's local file system and were lost when the containers were recreated

### Question 20 — `[DEV · assign vs subscribe · Multi — Choose 2]`

A developer uses `consumer.assign(List.of(new TopicPartition("events", 0), new TopicPartition("events", 1)))` with `group.id=audit`. Which two statements are correct? (Choose two.)

- A. The consumer will participate in rebalances with other members of `audit`
- B. The consumer will **not** participate in group coordination or rebalancing; it reads exactly the assigned partitions
- C. The consumer cannot commit offsets because `assign()` disables offset storage
- D. Calling `subscribe()` later on the same consumer instance will merge both subscription modes
- E. If partitions are later added to `events`, this consumer will not automatically pick them up; the application must detect them (for example with `partitionsFor()`) and call `assign()` again

### Question 21 — `[DEV · Rebalance listener · Single]`

A consumer commits offsets manually and wants to minimize duplicate processing when a cooperative rebalance moves some of its partitions to another member. Where should it commit the offsets of the records it has already processed for those partitions?

- A. In `ConsumerRebalanceListener.onPartitionsRevoked()`, which is called with the partitions about to be taken away, before the assignment is finalized
- B. In `ConsumerRebalanceListener.onPartitionsAssigned()`, which is called after the new owner has the partitions
- C. In `ConsumerRebalanceListener.onPartitionsLost()`, which guarantees the commit succeeds
- D. In the `commitAsync()` callback of the new owner

### Question 22 — `[DEV · Transactions · Single]`

A downstream consumer must never see records written by producer transactions that were later aborted. Which consumer setting is required, and what is its side effect on the visible end of the partition?

- A. `enable.idempotence=true`; the consumer reads up to the high watermark
- B. `isolation.level=read_uncommitted` (default); the consumer filters aborted records client-side
- C. `isolation.level=read_committed`; the consumer only reads up to the Last Stable Offset (LSO), so records of an open transaction are not returned until it commits or aborts
- D. `transactional.id` on the consumer; the consumer fences aborted producers

### Question 23 — `[DEV · Consumer lag · Single]`

`kafka-consumer-groups.sh --describe --group billing` prints, for partition `invoices-2`: `CURRENT-OFFSET 1200`, `LOG-END-OFFSET 1850`, `CONSUMER-ID consumer-billing-1-…`. Which statement is correct?

- A. 1,850 records are still unprocessed and the consumer has committed nothing
- B. The lag for this partition is 650 records: the difference between the log-end offset and the last committed offset
- C. The lag is 1,200 records because `CURRENT-OFFSET` counts unconsumed records
- D. The lag cannot be computed because the consumer is inactive

### Question 24 — `[DEV · Offset reset CLI · Multi — Choose 2]`

An operator runs the following while 3 consumers of the group are still running:

```
kafka-consumer-groups.sh --bootstrap-server broker:9092 --group billing \
  --topic invoices --reset-offsets --to-earliest
```

Nothing changes. Which two statements explain what is needed for the reset to take effect? (Choose two.)

- A. Without `--execute` the command only runs in dry-run mode and prints the offsets that **would** be set
- B. `--to-earliest` is not a valid scenario; `--to-offset 0` must be used
- C. The group's committed offsets can only be changed through the `Admin` API, not the CLI
- D. All members of the group must be stopped first: offsets can only be reset when the group is inactive
- E. `--reset-offsets` requires `--all-topics` even when `--topic` is given

### Question 25 — `[DEV · Threading · Single]`

A `KafkaConsumer` runs its poll loop on a dedicated thread. A shutdown hook running on the main thread needs to stop it gracefully. Which approach is correct and thread-safe?

- A. Call `consumer.close()` directly from the shutdown hook thread
- B. Call `consumer.wakeup()` from the shutdown hook; the poll thread catches `WakeupException`, commits if needed and calls `close()` in a `finally` block
- C. Call `consumer.unsubscribe()` from the shutdown hook, then `commitSync()`
- D. Call `consumer.pause()` for all partitions from the shutdown hook and let the poll thread exit

### Question 26 — `[DEV · Share groups · Single]`

An order-processing topic has 6 partitions. The team needs 30 worker instances to process records concurrently, each record must be acknowledged individually, a failed record should be redelivered to another worker after a timeout, and ordering is not required. Which Kafka 4.3 feature fits BEST?

- A. A classic consumer group with `RoundRobinAssignor` and 30 consumers
- B. A KIP-848 consumer group with `group.remote.assignor=uniform` and 30 consumers
- C. Increase the topic to 30 partitions and use `assign()` on each worker
- D. A share group (Queues for Kafka, KIP-932) consumed with `KafkaShareConsumer`: several consumers can read the same partition, records are acquired with a lock and acknowledged ACCEPT / RELEASE / REJECT

### Question 27 — `[DEV · Share groups · Multi — Choose 2]`

Which two statements about share groups in Kafka 4.3 are correct? (Choose two.)

- A. A record acquired by a share consumer is locked for `group.share.record.lock.duration.ms` (default 30,000 ms); if not acknowledged before the lock expires it becomes available again for another delivery
- B. Share groups preserve strict per-partition ordering exactly like consumer groups
- C. After a record has been delivered `share.delivery.count.limit` times (default 5) without being accepted, it is archived and not delivered again
- D. A share consumer commits offsets with `commitSync()` exactly like `KafkaConsumer`, one offset per partition
- E. Share groups became generally available in Kafka 3.7

### Question 28 — `[DEV · Follower fetching · Single]`

A consumer fleet runs in availability zone `az-b` while all partition leaders happen to be in `az-a`, generating expensive cross-zone traffic. Which combination lets consumers fetch from the closest replica?

- A. Set `client.rack=az-b` on the consumers and `broker.rack` on each broker, and configure `replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector` on the brokers (KIP-392)
- B. Set `fetch.from.follower=true` on the consumers
- C. Set `group.remote.assignor=range` so that partitions are assigned by zone
- D. Set `isolation.level=read_committed`, which reads from followers

### Question 29 — `[DEV · Week 3 review · Single]`

A Kafka 4.3 producer uses default settings except `max.in.flight.requests.per.connection=8`. On startup it fails with a `ConfigException`. Why?

- A. The maximum allowed value is 5 regardless of other settings
- B. `acks=all` requires `max.in.flight.requests.per.connection=1`
- C. `enable.idempotence` defaults to `true` and requires `max.in.flight.requests.per.connection` ≤ 5 (plus `acks=all` and `retries` > 0)
- D. `linger.ms=5` is incompatible with more than 5 in-flight requests

### Question 30 — `[FUND · Week 2 review · Multi — Choose 2]`

A topic has `replication.factor=3` and `min.insync.replicas=2`. One broker is down and a producer with `acks=all` keeps writing successfully. A second broker then goes down. Which two statements are correct? (Choose two.)

- A. Writes with `acks=all` continue because the leader is still alive
- B. Writes with `acks=all` now fail with `NotEnoughReplicasException` because only 1 replica is in the ISR, which is below `min.insync.replicas=2`
- C. Consumers can no longer read the partition until the ISR is restored
- D. A producer using `acks=1` could still write successfully to the remaining leader
- E. The leader automatically lowers `min.insync.replicas` to 1 to keep accepting writes

---

> ✅ Done? Check your answers in [answers.md](answers.md), log every wrong answer, then build the **FUND + DEV mini-mock** (~30 questions mixed from Weeks 1–4) described in the [week plan](README.md#-buổi-d--practice--review-2h).
