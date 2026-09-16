# 📝 Practice Questions — Week 1: Kafka Architecture, KRaft, Cluster Setup & CLI

> **30 questions** · real CCDAK exam style, difficulty ≥ real exam · covers the full Week 1 material (Kafka 4.3 defaults): commit-log fundamentals, partitions/segments/records, consumer-group basics, replication & ISR, `KRaft`, Kafka 4.0 changes, `bootstrap.servers` / `advertised.listeners`, the standard CLI, and Kafka vs `SQS` / `Kinesis` / RabbitMQ.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (number to choose is stated). Config names are the **broker / Java client** names, as on the real exam.
> Back to [week plan](README.md) · [master plan](../../KAFKA-STUDY-PLAN.md)

---

### Question 1 — `[FUND · Commit log vs queue · Single]`

A team migrating from a traditional message queue is surprised: a consumer application read every record of the `orders` topic yesterday, yet today a **second** application, started with a different `group.id`, still receives all of yesterday's records. The topic uses default settings. Which statement explains this behavior?

- A. The first consumer never acknowledged the records, so the broker redelivered them to the next available consumer
- B. Kafka copies every record into a separate queue for each consumer group at produce time, so each group has its own copy to delete
- C. A Kafka topic is an append-only, immutable log. Records are kept according to the retention policy (`log.retention.hours=168` by default) regardless of whether they were read, and each consumer group only tracks its own offsets
- D. This only happens because the topic was created with `cleanup.policy=compact`, which keeps the latest value per key forever

### Question 2 — `[FUND · Ordering & keys · Single]`

An e-commerce platform publishes `OrderCreated`, `OrderPaid` and `OrderShipped` events for each order to a 12-partition topic. Producers currently send records with a `null` key, and downstream consumers sometimes see `OrderShipped` before `OrderPaid` for the same order. The team must guarantee per-order ordering **without giving up consumer parallelism**. What should they do?

- A. Recreate the topic with a single partition so that Kafka guarantees total ordering across the topic
- B. Set `message.timestamp.type=LogAppendTime` so consumers can sort events by broker timestamp
- C. Keep `null` keys but set `max.in.flight.requests.per.connection=1` on every producer
- D. Use `orderId` as the record key, so the default partitioner routes all events of one order to the same partition via `murmur2(key) mod 12`, and avoid increasing the partition count afterwards

### Question 3 — `[FUND · Consumer groups · Single]`

A consumer group with 5 instances reads a topic that has **3 partitions**. Processing is too slow, so the team deploys 2 more instances (7 in total) with the same `group.id`. What is the result?

- A. Throughput rises roughly proportionally because the broker splits each partition's records round-robin across all 7 consumers
- B. Nothing improves: at most 3 consumers hold a partition each, the other 4 stay idle. To use more consumers the topic needs more partitions
- C. The rebalance fails with `InconsistentGroupProtocolException` because a group cannot have more members than partitions
- D. The 4 extra consumers automatically form a second consumer group and reprocess all data from the beginning

### Question 4 — `[FUND · Consumer groups & offsets · Multi — Choose 2]`

Which two statements about consumer groups and offsets in Kafka 4.3 are correct? (Choose two.)

- A. Two consumer groups subscribed to the same topic split the records between them, so each record is delivered to exactly one group
- B. Within a single consumer group a partition is assigned to at most one consumer at a time, while consumers in **different** groups can read the same partition independently
- C. Kafka pushes records to consumers as soon as they are appended; the consumer only acknowledges them
- D. Committed offsets are stored in the internal compacted topic `__consumer_offsets`, which has **50** partitions by default
- E. Committed offsets are stored per consumer instance in ZooKeeper under `/consumers/<group>/offsets`

### Question 5 — `[FUND · Segments on disk · Single]`

An operator lists the directory of partition 0 of the `orders` topic and sees:

```
00000000000000000000.log        00000000000000000000.index      00000000000000000000.timeindex
00000000000000524288.log        00000000000000524288.index      00000000000000524288.timeindex
leader-epoch-checkpoint         partition.metadata
```

What does the number `524288` in the second set of files represent?

- A. The **base offset**: the offset of the first record stored in that segment. The first segment therefore holds offsets 0 through 524287, and the second one is the active segment currently being written
- B. The size in bytes of the segment; Kafka rolls a new segment every 524288 bytes
- C. The number of records stored in the first segment before it was rolled
- D. The timestamp (in seconds since epoch) of the first record in that segment

### Question 6 — `[FUND · Offset index · Single]`

A consumer issues a fetch request for offset `700000` in a partition whose active segment is close to 1 GB. How does the broker locate the record efficiently?

- A. It scans the `.log` file sequentially from the beginning until it reaches offset 700000
- B. It looks up the exact byte position in the `.index` file, which contains one entry for every record in the segment
- C. It binary-searches the in-memory segment list to find the segment whose base offset is ≤ 700000, then consults the **sparse** `.index` file (one entry roughly every `log.index.interval.bytes` = 4096 bytes) to find the nearest indexed offset, seeks to that byte position in the `.log` file and scans forward
- D. It uses the `.timeindex` file, because offsets are always looked up by timestamp internally

### Question 7 — `[FUND · Retention · Single]`

A low-traffic topic is configured with `retention.ms=604800000` (7 days). Nine days after a record was written, a consumer running `--from-beginning` still receives it. Brokers are healthy and no configuration was changed. What is the MOST likely explanation?

- A. The retention check runs only once every 24 hours, so the record will disappear at the next check
- B. A consumer group still has a committed offset pointing at that record, and Kafka never deletes records that have an uncommitted consumer behind them
- C. Retention applies only to compacted topics; a `delete` topic keeps data until `log.retention.bytes` is reached
- D. Retention deletes **whole segments**, never individual records, and only when the segment's largest timestamp is past the retention limit. The **active segment** is never deleted, and with little traffic it has not rolled yet (`log.segment.bytes` = 1 GB or `log.roll.hours` = 168)

### Question 8 — `[FUND · Timestamps · Single]`

An audit team requires that the timestamp stored on every record of the `payments` topic reflects **when the broker received the record**, because producer hosts have unreliable clocks. Which configuration achieves this?

- A. Nothing needs to change; by default the broker overwrites the timestamp at append time
- B. Set the topic configuration `message.timestamp.type=LogAppendTime` (or the broker default `log.message.timestamp.type`), so the leader overwrites the producer-supplied timestamp when appending the batch
- C. Set `timestamp.type=broker` in the producer configuration
- D. Enable `log.message.timestamp.difference.max.ms=0` so records with a wrong timestamp are rejected

### Question 9 — `[FUND · Record format v2 · Multi — Choose 2]`

Which two statements about the Kafka message format v2 (`RecordBatch`, `magic=2`) used by Kafka 4.3 are correct? (Choose two.)

- A. Compression (gzip, snappy, lz4, zstd) is applied to the **whole batch** of records, not to each record individually, which is why larger batches compress better
- B. Every record stores its own absolute 64-bit offset and absolute timestamp, so records can be moved between batches without rewriting them
- C. A record consists of an optional (nullable) key, a value, an optional list of headers, and a timestamp; the `producerId`, `producerEpoch` and `baseSequence` fields used for idempotence live once in the **batch header**, not in each record
- D. The broker-side limit `message.max.bytes` defaults to exactly 1 048 576 bytes (1 MiB) and is applied to every record **before** compression
- E. The batch CRC covers the entire batch including the `partitionLeaderEpoch` field, so a leader change requires rewriting every batch

### Question 10 — `[FUND · Increasing partitions · Single]`

The `customer-events` topic has 6 partitions and every record is keyed by `customerId`. To add more consumers, an operator plans to run `kafka-topics.sh --bootstrap-server kafka-1:9092 --alter --topic customer-events --partitions 12`. Which statement is correct?

- A. The change is safe: the default partitioner remembers previous key-to-partition assignments, so existing customers stay on their partitions
- B. Kafka rejects the command, because the partition count of a topic with keyed records cannot be changed
- C. The command succeeds, but from then on records for a given `customerId` may land in a **different** partition than the earlier records with the same key (`murmur2(key) mod 12` instead of `mod 6`), breaking per-key ordering across old and new data. If ordering per key matters, create a new topic with enough partitions and migrate
- D. Only records with a `null` key are affected, because keyed records always use partition `hash(key) mod 6` regardless of the partition count

### Question 11 — `[FUND · Decreasing partitions · Single]`

A topic was created with 24 partitions but traffic turned out to be low, and each partition now holds very little data. The operator runs:

```
kafka-topics.sh --bootstrap-server kafka-1:9092 --alter --topic clicks --partitions 8
```

What happens?

- A. The command fails with an `InvalidPartitionsException`: the number of partitions can only be **increased**. To shrink, the team must create a new topic with 8 partitions and migrate the data
- B. The command succeeds and Kafka merges partitions 8–23 into partitions 0–7, preserving offsets
- C. The command succeeds only if `--force` is added, because data in the removed partitions is deleted
- D. The command succeeds because reducing partitions is allowed as long as no consumer group is active

### Question 12 — `[FUND · Replication factor · Multi — Choose 2]`

A 3-broker Kafka 4.3 cluster uses the broker defaults for `num.partitions` and `default.replication.factor`. A developer runs `kafka-topics.sh --bootstrap-server kafka-1:9092 --create --topic payments` with no other flags. Which two statements are correct? (Choose two.)

- A. The topic is created with **1 partition and 1 replica**. If the broker hosting that replica is down, the partition is unavailable, and if its disk is lost the data is gone
- B. Because the cluster has 3 brokers, Kafka automatically creates the topic with `replication.factor=3` to match the cluster size
- C. The replication factor can be raised later by running `kafka-topics.sh --alter --topic payments --replication-factor 3`
- D. Recreating the topic with `--replication-factor 4` would fail with `InvalidReplicationFactorException`, because the replication factor cannot exceed the number of live brokers
- E. Kafka adds replicas automatically whenever a new broker joins the cluster, so the replication factor grows on its own

### Question 13 — `[FUND · ISR · Single]`

During a rolling restart, `kafka-topics.sh --describe` for partition `orders-2` shows `Replicas: 1,2,3  Isr: 1,2` while broker 3 is down, and a few minutes after broker 3 returns it shows `Isr: 1,2,3` again. Which statement correctly describes how the ISR shrinks and recovers?

- A. ZooKeeper removes a follower from the ISR after 10 000 ms without a heartbeat, and an operator must re-add it with `kafka-topics.sh --alter --isr`
- B. A follower leaves the ISR when it falls more than `replica.lag.max.messages` records behind the leader, and rejoins after a preferred leader election
- C. A follower leaves the ISR only when the broker process dies; a slow but running follower always stays in the ISR
- D. A follower is removed from the ISR when it fails to catch up to the leader's log end within `replica.lag.time.max.ms` (default **30 000 ms**) or loses its session with the controller. When it fetches and catches up again, the leader adds it back to the ISR **automatically**

### Question 14 — `[FUND · Committed records & HW · Multi — Choose 2]`

A partition has `replication.factor=3`, all three replicas are in the ISR, and producers use `acks=all`. A new record has been appended to the leader and to **one** follower; the second follower has not fetched it yet. Which two statements are correct? (Choose two.)

- A. The record is committed as soon as the leader writes it to its own log
- B. The record is **not yet committed**, so it sits above the High Watermark and no consumer can read it, even with `isolation.level=read_uncommitted`
- C. The leader pushes the record to each follower and waits for their TCP acknowledgement
- D. A consumer with `isolation.level=read_uncommitted` can already read the record from the leader
- E. With this ISR-based design Kafka tolerates **f** replica failures with **f + 1** replicas, so 3 replicas survive 2 failures without losing committed data, whereas a majority-vote quorum would need 5 replicas for the same guarantee

### Question 15 — `[FUND · KRaft motivation (KIP-500) · Multi — Choose 2]`

Which two problems of the ZooKeeper-based architecture motivated the move to `KRaft` (KIP-500)? (Choose two.)

- A. Controller failover was **O(number of partitions)**: a newly elected controller had to load the full metadata from ZooKeeper before it could act, which in practice capped clusters at roughly 200 000 partitions
- B. ZooKeeper could not be secured with TLS or SASL, so Kafka metadata was always transmitted in plaintext
- C. Operators had to deploy, secure and monitor **two** different distributed systems, and metadata was split between ZooKeeper and the controller's in-memory cache, so the two views could diverge
- D. ZooKeeper only runs on Java 8, blocking the Kafka 4.0 move to Java 17
- E. Kafka wanted to replace consensus with a gossip protocol, which ZooKeeper does not support

### Question 16 — `[FUND · Controller quorum size · Single]`

An architect proposes running **4** dedicated `KRaft` controller nodes so that the cluster "can tolerate 2 controller failures". Which statement is correct?

- A. Correct: with 4 controllers any 2 can fail and the remaining 2 still form a quorum
- B. Incorrect: the controller quorum must always have exactly 3 members
- C. Incorrect: a quorum needs a **majority** of voters. With 4 voters the majority is 3, so only **1** failure is tolerated — the same as with 3 voters. To survive 2 failures use **5** controllers; even numbers add cost without adding fault tolerance
- D. Incorrect: only the active controller matters, so a single controller node offers the same availability as 4

### Question 17 — `[FUND · __cluster_metadata · Single]`

Which statement about the `__cluster_metadata` topic in a `KRaft` cluster is correct?

- A. It has 50 partitions and is compacted, and consumer offsets are stored alongside the cluster metadata
- B. It is a **single-partition** internal log replicated across the controller quorum: the active controller is its leader, the other controllers are followers, and brokers act as observers that **fetch** (pull) metadata records from the active controller. Periodic snapshots (`.checkpoint` files) let the log be truncated
- C. It is stored in ZooKeeper and mirrored into Kafka for read-only access by the `kafka-metadata-shell.sh` tool
- D. Brokers do not read it; the active controller pushes every metadata change to each broker through `UpdateMetadataRequest`

### Question 18 — `[FUND · process.roles · Single]`

To save on hardware, a startup plans to run a production cluster of 3 nodes, each configured with `process.roles=broker,controller`. What does the Apache Kafka documentation say about this configuration?

- A. It is **combined mode**, intended for development and testing; production deployments should run **isolated** controllers (`process.roles=controller`) on nodes separate from brokers, because combined mode removes the isolation between the metadata quorum and data traffic. Both roles share the same `node.id` space, so every node still needs a cluster-unique `node.id`
- B. It is the recommended production topology since Kafka 4.0, because it removes the need for a separate controller listener
- C. It is not supported: since Kafka 4.0 a node can only run one role
- D. It is allowed only together with the static `controller.quorum.voters` configuration, never with a dynamic quorum

### Question 19 — `[FUND · kafka-storage.sh · Single]`

An operator adds a new broker to an existing Kafka 4.3 `KRaft` cluster that uses a dynamic quorum. The broker refuses to start, logging that `meta.properties` is missing / the storage directory has not been formatted. Which action is correct?

- A. Run `kafka-storage.sh random-uuid` on the new broker to generate its own cluster ID, then format its log directories with that ID
- B. Delete the `log.dirs` directory and restart; a Kafka 4.x broker formats itself on first start
- C. Run `kafka-metadata-quorum.sh --bootstrap-server kafka-1:9092 add-controller` so the quorum registers the new node and formats it remotely
- D. Format the new broker's `log.dirs` with the **existing** cluster's ID: `kafka-storage.sh format -t <existing-cluster-id> -c server.properties --no-initial-controllers`. A freshly generated UUID would not match the quorum's `cluster.id`, and the broker would refuse to join

### Question 20 — `[FUND · Static vs dynamic quorum · Multi — Choose 2]`

A Kafka 4.3 cluster still runs with `controller.quorum.voters=1@c1:9093,2@c2:9093,3@c3:9093`. The team wants to grow the quorum to 5 controllers without restarting the existing nodes. Which two statements are correct? (Choose two.)

- A. Dynamic quorums identify a voter by `node.id` only, exactly like static quorums
- B. With a **static** quorum, changing membership means editing `controller.quorum.voters` on every node and restarting them; this configuration is **deprecated** in 4.x
- C. Running `kafka-topics.sh --alter --topic __cluster_metadata --replication-factor 5` adds two voters to the quorum
- D. If `kafka-features.sh describe` shows `kraft.version` at level 0 (or absent), the cluster is already using a dynamic quorum
- E. A **dynamic** quorum (KIP-853, `kraft.version=1`) replaces the voter list with `controller.quorum.bootstrap.servers=c1:9093,c2:9093`, formats new controllers with `kafka-storage.sh format ... --no-initial-controllers`, and adds or removes them online with `kafka-metadata-quorum.sh add-controller` / `remove-controller`

### Question 21 — `[FUND · Kafka 4.0 changes · Single]`

A company runs its brokers and its Java client applications on **Java 11** and plans to upgrade both to Kafka 4.0. What is required?

- A. Nothing: Kafka 4.0 supports Java 11 for every component
- B. Both brokers and clients must move to Java 21, which became the minimum in 4.0
- C. The **brokers** (as well as `Kafka Connect` and the command-line tools) must move to **Java 17+**; the **clients** and `Kafka Streams` applications may stay on **Java 11+**
- D. The clients must move to Java 17, while brokers can remain on Java 11

### Question 22 — `[FUND · Kafka 4.0 changes · Multi — Choose 2]`

Which two statements about Apache Kafka 4.0 are correct? (Choose two.)

- A. Kafka 4.0 can still be started in ZooKeeper mode by setting `zookeeper.connect`, which is how clusters migrate to `KRaft`
- B. Because message format versions v0/v1 (KIP-724) and old API versions (KIP-896) were removed, Kafka 4.0 brokers cannot be contacted by clients older than **2.1**, and 4.0 clients require brokers **≥ 2.1**
- C. MirrorMaker 1 was **removed**; MirrorMaker 2 (based on `Kafka Connect`) is the only replication tool shipped with the distribution
- D. The KIP-848 consumer rebalance protocol became the **default** for all consumers, so no client configuration is needed to use it
- E. KIP-1030 lowered the producer default `linger.ms` from 5 ms to 0 to reduce latency

### Question 23 — `[FUND · Kafka 4.x features · Single]`

A team wants **`SQS`-style queue semantics** on a Kafka topic: more consumers than partitions, each record acknowledged individually, and no fixed partition assignment. Which Kafka feature provides this, and in which release did it become generally available?

- A. Eligible Leader Replicas (KIP-966): preview in 4.0, GA in 4.1
- B. **Share groups** — "Queues for Kafka" (KIP-932): early access in 4.0, preview in 4.1, **GA in 4.2**
- C. The KIP-848 consumer rebalance protocol, GA in 4.0 with `group.protocol=consumer`
- D. Classic consumer groups; simply set the number of consumers higher than the number of partitions

### Question 24 — `[FUND · bootstrap.servers · Single]`

A consumer application is configured with `bootstrap.servers=kafka-1:9092` only. Broker `kafka-1` suffers a permanent hardware failure. The **running** consumer instances keep processing without errors, but **newly started** instances fail with a connection timeout. Which explanation is correct?

- A. `bootstrap.servers` is used only for the **initial** metadata request. Running clients already learned every broker's `advertised.listeners` address and each partition leader from metadata, so they connect directly to the surviving leaders. A new client has no metadata yet and cannot reach its only bootstrap address; list **2–3** brokers to avoid this
- B. `bootstrap.servers` must list **every** broker, otherwise clients only ever talk to the brokers in the list
- C. The running consumers will also fail as soon as `metadata.max.age.ms` (5 minutes) elapses, because a metadata refresh always goes through the bootstrap address
- D. The new instances should point `bootstrap.servers` at the active `KRaft` controller on port 9093, which is always available

### Question 25 — `[FUND · listeners vs advertised.listeners · Single]`

A broker runs on a cloud VM whose network interface has the private IP `10.0.1.5`; the VM is also reachable from the office through the public DNS name `kafka-1.example.com`. The broker is configured with:

```
listeners=PLAINTEXT://10.0.1.5:9092
```

and `advertised.listeners` is unset. Clients in the office can bootstrap against `kafka-1.example.com:9092` but then time out. Why, and what is the fix?

- A. The broker is bound to the wrong interface; change `listeners=PLAINTEXT://kafka-1.example.com:9092`
- B. The clients need a longer `request.timeout.ms` because cross-network metadata requests are slow
- C. When `advertised.listeners` is unset it defaults to the value of `listeners`, so metadata returns `10.0.1.5:9092`, which office clients cannot reach. Keep `listeners` as the bind address and set `advertised.listeners=PLAINTEXT://kafka-1.example.com:9092`
- D. The public DNS name must also be added to `bootstrap.servers` on the broker side

### Question 26 — `[FUND · Docker listeners scenario · Single]`

A 3-broker `docker-compose` cluster defines, on each broker:

```
KAFKA_LISTENERS: PLAINTEXT://:9092
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:9092      # kafka-2 / kafka-3 on the other brokers
ports: ["9092:9092"]
```

`docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list` works. A Node.js `kafkajs` application on the **host**, configured with `brokers: ['localhost:9092']`, connects and then fails with `ENOTFOUND kafka-1` / connection timeout. What is the correct fix?

- A. Change the application to `brokers: ['kafka-1:9092']`; Docker Desktop resolves container names on the host automatically
- B. Add a second listener per broker: keep `PLAINTEXT://:19092` advertised as `kafka-1:19092` for inter-broker and in-network traffic, add `PLAINTEXT_HOST://:9092` advertised as `localhost:9092` (with a distinct host port per broker), map both in `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP` (`PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,CONTROLLER:PLAINTEXT`) and set `KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT`
- C. Set `KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092` on every broker so the host application receives an address it can resolve
- D. Publish port 9093 as well, because the client needs to reach the `KRaft` controller listener to fetch metadata

### Question 27 — `[FUND · Console producer / consumer · Single]`

A developer wants to produce the line `user-42:{"event":"login"}` so that `user-42` becomes the record **key**, and then verify with the console consumer that the key, the partition and the offset are printed. Which pair of Kafka 4.3 commands is correct?

- A. `kafka-console-producer.sh --broker-list localhost:9092 --topic events --key user-42` and `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic events --from-beginning --print-key`
- B. `kafka-console-producer.sh --zookeeper localhost:2181 --topic events --property parse.key=true` and `kafka-console-consumer.sh --zookeeper localhost:2181 --topic events --from-beginning`
- C. `kafka-console-producer.sh --bootstrap-server localhost:9092 --topic events --property parse.key=true` and `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic events --property print.key=true`
- D. `kafka-console-producer.sh --bootstrap-server localhost:9092 --topic events --property parse.key=true --property key.separator=:` and `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic events --from-beginning --property print.key=true --property print.partition=true --property print.offset=true`

### Question 28 — `[FUND · Admin CLI · Multi — Choose 2]`

An operator must (1) change the retention of the running topic `orders` to 3 days without recreating it, and (2) reset the committed offsets of the consumer group `billing` to the beginning of `orders`. Which two Kafka 4.3 commands are valid for these tasks? (Choose two.)

- A. `kafka-configs.sh --bootstrap-server kafka-1:9092 --entity-type topics --entity-name orders --alter --add-config retention.ms=259200000`
- B. `kafka-topics.sh --zookeeper zk-1:2181 --alter --topic orders --config retention.ms=259200000`
- C. `kafka-consumer-groups.sh --bootstrap-server kafka-1:9092 --group billing --topic orders --reset-offsets --to-earliest --execute` (run while the group has **no active members**)
- D. `kafka-consumer-groups.sh --bootstrap-server kafka-1:9092 --group billing --delete-offsets --to-earliest`
- E. `kafka-configs.sh --broker-list kafka-1:9092 --entity-type topics --entity-name orders --alter --add-config retention.hours=72`

### Question 29 — `[FUND · Diagnostic CLI · Multi — Choose 2]`

An operator needs to (1) find out which `KRaft` controller is currently **active** and what the metadata log's high watermark is, and (2) inspect the **actual records** stored in a segment file of `orders-0` directly on the broker's disk. Which two commands accomplish these tasks? (Choose two.)

- A. `kafka-metadata-quorum.sh --bootstrap-server kafka-1:9092 describe --status`
- B. `kafka-log-dirs.sh --bootstrap-server kafka-1:9092 --describe --topic-list orders`
- C. `kafka-topics.sh --bootstrap-server kafka-1:9092 --describe --topic orders`
- D. `kafka-dump-log.sh --files /var/lib/kafka/data/orders-0/00000000000000000000.log --print-data-log`
- E. `kafka-console-consumer.sh --bootstrap-server kafka-1:9092 --topic orders --partition 0 --offset 0`

### Question 30 — `[FUND · Kafka vs SQS / Kinesis / RabbitMQ · Multi — Choose 2]`

A team on AWS currently pushes order events through an `Amazon SQS` standard queue. New requirements: **three** independent downstream services must each receive **every** order, analysts must be able to **replay** the last 30 days, and events of the same customer must be processed **in order**. Which two statements are correct? (Choose two.)

- A. `Amazon Kinesis Data Streams` cannot meet the replay requirement, because its retention is fixed at 24 hours
- B. `SQS` alone cannot meet the requirements: a message is deleted once one consumer processes it, fan-out to several services needs `SNS` (or one queue per service), and there is no replay of already-consumed messages
- C. RabbitMQ keeps every acknowledged message on disk by default, so it offers the same replay capability as Kafka
- D. Kafka meets all three: several consumer groups (different `group.id`) read the whole topic independently, retention (for example `retention.ms=2592000000`) allows replaying by offset or timestamp, and keying records by `customerId` keeps each customer's events in order within one partition
- E. Kafka cannot offer single-consumer queue semantics at all, so any workload that needs a work queue must stay on `SQS`

---

> ✅ Done? Check your answers in [answers.md](answers.md), log every wrong answer with the reason (wrong number? wrong concept? missed a "NOT"?), then redo the **Cổng tự kiểm tra** in the [week plan](README.md#-cổng-tự-kiểm-tra-phải-trả-lời-trôi-chảy-mới-sang-tuần-sau). Move on to Week 2 only at **≥ 70%**.
