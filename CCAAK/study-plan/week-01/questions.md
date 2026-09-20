# 📝 Practice Questions — Week 1: Operational Foundations + KRaft in Production

> **28 questions** · real CCAAK exam style: most questions start from a symptom, a log line, a CLI output or a metric and ask **what a competent administrator does next**.
> ⏱️ Target: **42 minutes** (~90 s/question), closed book. 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Domains used this week: `FUND` (Apache Kafka Fundamentals), `ARCH` (Deployment Architecture), `CFG` (Cluster Configuration), `TROUBLE` (Troubleshooting), `OBS` (Observability).
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[ARCH · Controller quorum sizing · Single]`

A platform team is designing a Kafka 4.3 cluster that spans three availability zones. The requirement from the architecture review is: *"the control plane must survive the simultaneous loss of two controller nodes"*. The team proposes running four dedicated controllers, one in AZ-a, one in AZ-b and two in AZ-c. What should the administrator recommend?

- A. Four controllers are correct, because four nodes can lose two and still have two left
- B. Five dedicated controllers, because a quorum of `2N+1` tolerates `N` failures; four controllers still require a majority of three and therefore tolerate only one failure
- C. Three dedicated controllers plus one observer controller configured with `process.roles=controller,observer`
- D. Six controllers, so that each availability zone holds exactly two

### Question 2 — `[FUND · Metadata quorum roles · Single]`

An administrator runs the following on a newly built cluster:

```
$ kafka-metadata-quorum.sh --bootstrap-server kafka-1:19092 describe --status
ClusterId:              q1Sh-9_ISia_zwGINzRvyQ
LeaderId:               1
LeaderEpoch:            4
HighWatermark:          1183
MaxFollowerLag:         0
MaxFollowerLagTimeMs:   0
CurrentVoters:          [{"id": 1, "directoryId": "TmVDOTFaQ1FTSGlmU0Vad", "endpoints": ["CONTROLLER://controller:9093"]}]
CurrentObservers:       [{"id": 2, "directoryId": "..."}, {"id": 3, "directoryId": "..."}, {"id": 4, "directoryId": "..."}]
```

Which statement about nodes 2, 3 and 4 is correct?

- A. They are standby controllers that will take over if node 1 fails
- B. They are brokers that have not finished registering and will move into `CurrentVoters` once they catch up
- C. They are brokers; they replicate `__cluster_metadata` as observers and never vote in a controller election
- D. They are controllers that were fenced because their `directory.id` does not match the one recorded at format time

### Question 3 — `[TROUBLE · Cluster ID · Single]`

A broker that was rebuilt from a machine image fails to start. Its `server.log` contains:

```
[2026-09-20 09:31:07,412] ERROR Exiting Kafka due to fatal exception during startup. (kafka.Kafka$)
org.apache.kafka.common.errors.InconsistentClusterIdException: Expected cluster ID q1Sh-9_ISia_zwGINzRvyQ
        but got 4L6g3nShT-eMCtK--X86sw
```

What is the correct first action?

- A. Delete the topic metadata in ZooKeeper so the broker can re-register with the cluster
- B. Set `broker.id.generation.enable=true` so the broker picks a free identifier automatically
- C. Compare `cluster.id` in the broker's `meta.properties` with the `ClusterId` reported by `kafka-metadata-quorum.sh describe --status`, then re-run `kafka-storage.sh format` on that log directory with the cluster's real cluster ID
- D. Raise `controller.quorum.fetch.timeout.ms` so the broker has longer to join the quorum

### Question 4 — `[ARCH · Combined vs separated roles · Single]`

A three-node production cluster runs every node with `process.roles=broker,controller` to save hardware. During heavy compaction the operators observe repeated controller elections; the metadata leader changes several times per hour even though the network is healthy. Which explanation and remedy should the administrator give?

- A. The quorum is too small; adding a fourth combined node will stabilise the elections
- B. In combined mode the controller shares the JVM and the disk with the broker, so broker GC pauses and I/O stalls make it miss `controller.quorum.fetch.timeout.ms` (2000 ms); the documented production layout is dedicated `controller` nodes separated from `broker` nodes
- C. `replica.lag.time.max.ms` is too low at 30000 ms and should be raised to 120000 ms
- D. `auto.leader.rebalance.enable` is triggering the elections and should be set to `false`

### Question 5 — `[TROUBLE · Quorum loss · Single]`

All three controllers of a cluster are unreachable after a rack power failure. The brokers are still up. An administrator tries to create a topic and sees:

```
$ kafka-topics.sh --bootstrap-server kafka-1:19092 --create --topic incident-notes --partitions 3 --replication-factor 3
Error while executing topic command : The request timed out.
[2026-09-20 11:02:44,117] ERROR org.apache.kafka.common.errors.TimeoutException: The request timed out.
 (org.apache.kafka.tools.TopicCommand)
```

Meanwhile, an existing application keeps producing to and consuming from `orders` without errors. What is happening, and what should the administrator do first?

- A. The brokers have lost their data; restore from backup before doing anything else
- B. Enable `unclean.leader.election.enable=true` on all brokers so topic creation can proceed without the controller
- C. Producing still works, so the cluster is healthy; the CLI simply needs `--bootstrap-controller` instead of `--bootstrap-server`
- D. The control plane is frozen because the controller quorum has no majority, while brokers keep serving partitions from their cached metadata. Restore controller majority first — do not start reconfiguring topics or brokers

### Question 6 — `[FUND · Metadata replication · Single]`

An administrator runs `kafka-metadata-quorum.sh describe --replication` on a five-controller cluster and sees one line per node with a `Status` column containing `Leader`, `Follower` or `Observer`. What determines whether a given node appears as `Observer`?

- A. The node has `process.roles=broker` only, so it replicates `__cluster_metadata` but does not participate in voting
- B. The node is a controller whose log has fallen behind the leader by more than `replica.lag.time.max.ms`
- C. The node has `controller.quorum.voters` unset and therefore cannot find the quorum
- D. The node is a controller that lost the most recent election and is waiting for the next election timeout

### Question 7 — `[CFG · Static vs dynamic quorum · Single]`

An administrator must replace a failed controller in a running cluster and runs:

```
$ kafka-features.sh --bootstrap-controller controller-1:9093 describe
Feature: eligible.leader.replicas.version  SupportedMinVersion: 0       SupportedMaxVersion: 1       FinalizedVersionLevel: 1       Epoch: 12
Feature: group.version                     SupportedMinVersion: 0       SupportedMaxVersion: 1       FinalizedVersionLevel: 1       Epoch: 12
Feature: kraft.version                     SupportedMinVersion: 0       SupportedMaxVersion: 1       FinalizedVersionLevel: 0       Epoch: 12
Feature: metadata.version                  SupportedMinVersion: 3.3-IV3 SupportedMaxVersion: 4.3-IV1 FinalizedVersionLevel: 4.3-IV1 Epoch: 12
```

What does this output tell the administrator about the replacement procedure?

- A. `kraft.version` is 0, so the cluster uses a static quorum: the voter set lives in `controller.quorum.voters` on every node, and swapping a controller requires editing that property everywhere and restarting the nodes — `kafka-metadata-quorum.sh add-controller` is not available
- B. `kraft.version` is 0, meaning KRaft is disabled and the cluster is still using ZooKeeper for controller election
- C. The replacement can be done online with `add-controller` / `remove-controller` because `metadata.version` is already at 4.3
- D. The controller must first be removed from `__cluster_metadata` with `kafka-metadata-shell.sh` before the new one is formatted

### Question 8 — `[TROUBLE · Quorum loss · Multi — Choose 2]`

A cluster has three dedicated controllers; two of them are down and cannot be recovered for another hour. Brokers and clients are untouched. Which two statements describe the cluster's behaviour during that hour? (Choose two.)

- A. Producers keep writing successfully to partitions whose leader has not changed, because brokers serve them from their cached metadata
- B. Consumer groups can no longer commit offsets, because offset commits are metadata operations handled by the controller
- C. `kafka-configs.sh --alter` and `kafka-topics.sh --create` fail, because every metadata mutation must be committed to the metadata log by the active controller
- D. All client connections are dropped immediately, because brokers refuse requests when they cannot reach a controller
- E. Any broker that fails during this window will have its partitions taken over automatically by a surviving replica

### Question 9 — `[FUND · Legacy tooling · Single]`

A runbook written for Kafka 2.x is being executed against a Kafka 4.3 cluster. The first command fails:

```
$ kafka-topics.sh --zookeeper zk-1:2181 --list
kafka-topics: ERROR: Unrecognized option: --zookeeper
```

Which statement correctly explains this and gives the modern equivalent?

- A. The option was renamed to `--zk-connect`; the rest of the runbook is still valid
- B. The option still exists but requires `zookeeper.connect` to be set in `server.properties` first
- C. ZooKeeper support was removed in Kafka 4.0 (3.9 was the last bridge release). All admin tools now take `--bootstrap-server`, or `--bootstrap-controller` when the command must reach a controller directly
- D. The command must be run on a controller node, where the ZooKeeper client libraries are still bundled

### Question 10 — `[CFG · Metadata log placement · Single]`

A controller node has two disks mounted at `/data/1` and `/data/2`, and its configuration contains only `log.dirs=/data/1,/data/2`. Monitoring shows that metadata append latency spikes whenever compaction runs against the partitions stored on `/data/1`. Which configuration change addresses the root cause?

- A. Set `metadata.log.dir` to a dedicated device, so the metadata log stops competing for I/O with partition data; with `metadata.log.dir` unset (the default `null`), the metadata log lives in the **first** directory of `log.dirs`
- B. Set `metadata.log.segment.bytes=8388608` so metadata segments roll more often
- C. Remove `/data/1` from `log.dirs`, because `log.dirs` must contain exactly one entry on controller nodes
- D. Increase `controller.quorum.append.linger.ms` from 25 to 1000 so appends are batched more aggressively

### Question 11 — `[TROUBLE · Metadata log inspection · Single]`

After an unexplained topic disappearance, an administrator wants to see the exact metadata records that were written around the time of the incident. Which command inspects the metadata log directly?

- A. `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic __cluster_metadata --from-beginning`
- B. `kafka-dump-log.sh --cluster-metadata-decoder --files /data/1/__cluster_metadata-0/00000000000000000000.log`
- C. `kafka-log-dirs.sh --bootstrap-server localhost:9092 --describe --topic-list __cluster_metadata`
- D. `kafka-metadata-quorum.sh --bootstrap-server localhost:9092 describe --replication --verbose`

### Question 12 — `[OBS · ActiveControllerCount · Single]`

A Grafana panel sums the JMX metric `ActiveControllerCount` across every node of a Kafka 4.3 cluster. The panel normally reads 1. For the last four minutes it has read 0, and no topic can be created. Which interpretation is correct?

- A. Every node reports 0 because the metric is only exposed by brokers, not controllers; the panel is misconfigured
- B. Two controllers are active simultaneously and their values cancel out
- C. A value of 0 means exactly one controller is active and healthy; the alert threshold is inverted
- D. The sum is 0 because no controller currently holds leadership of the metadata log — the quorum has not elected an active controller. Run `kafka-metadata-quorum.sh describe --status` and check whether a majority of voters is alive

### Question 13 — `[ARCH · Storage formatting · Multi — Choose 2]`

An administrator is adding a fourth controller to an existing cluster that already runs with a dynamic quorum. Which two steps are part of the correct procedure? (Choose two.)

- A. Format the new node with `kafka-storage.sh format --cluster-id <existing cluster id> --no-initial-controllers --config config/controller.properties`
- B. Format the new node with `kafka-storage.sh format --standalone`, which makes it join the existing quorum as an additional voter
- C. Generate a fresh cluster ID with `kafka-storage.sh random-uuid` for the new node so that it does not collide with the existing controllers
- D. After the node has started and caught up on the metadata log, run `kafka-metadata-quorum.sh --bootstrap-server <broker>:9092 add-controller`
- E. Add the new node to `controller.quorum.voters` on every broker and restart all brokers

### Question 14 — `[FUND · Node provisioning · Ordering]`

Put the following steps in the correct order to bring up the **first** controller of a brand-new Kafka 4.3 cluster from an empty disk.

1. `kafka-server-start.sh config/controller.properties`
2. `kafka-storage.sh format --cluster-id $CLUSTER_ID --standalone --config config/controller.properties`
3. `CLUSTER_ID=$(kafka-storage.sh random-uuid)`
4. `kafka-metadata-quorum.sh --bootstrap-controller localhost:9093 describe --status`

- A. 3 → 2 → 1 → 4
- B. 2 → 3 → 1 → 4
- C. 1 → 3 → 2 → 4
- D. 3 → 1 → 2 → 4

### Question 15 — `[TROUBLE · Admin tooling · Matching]`

Match each operational question (1–4) with the tool that answers it (W–Z).

| # | Operational question |
|---|---|
| 1 | "Which log directory holds partition `orders-2`, and how many bytes does it use?" |
| 2 | "Is the controller quorum healthy, and which node is the metadata leader?" |
| 3 | "Is the effective `min.insync.replicas` for topic `orders` coming from a topic override or from the broker default?" |
| 4 | "Is this cluster using a static or a dynamic controller quorum?" |

| Letter | Tool |
|---|---|
| W | `kafka-metadata-quorum.sh describe --status` |
| X | `kafka-configs.sh --describe --all --entity-type topics --entity-name orders` |
| Y | `kafka-log-dirs.sh --describe --bootstrap-server ...` |
| Z | `kafka-features.sh --bootstrap-controller ... describe` |

- A. 1-Y, 2-W, 3-X, 4-Z
- B. 1-Y, 2-Z, 3-X, 4-W
- C. 1-X, 2-W, 3-Y, 4-Z
- D. 1-Y, 2-W, 3-Z, 4-X

### Question 16 — `[CFG · Dynamic vs static config · Single]`

Clients outside the Kubernetes cluster can reach the bootstrap endpoint but every produce call times out. The administrator identifies a wrong `advertised.listeners` value and tries to correct it without downtime:

```
$ kafka-configs.sh --bootstrap-server kafka-1:19092 --alter \
    --entity-type brokers --entity-name 2 \
    --add-config advertised.listeners=PLAINTEXT://kafka-1:19092,PLAINTEXT_HOST://edge.example.com:9092
Error while executing config command with args '...'
java.lang.IllegalArgumentException: Cannot update these configs dynamically: Set(advertised.listeners)
```

What must the administrator do?

- A. Use `--bootstrap-controller controller-1:9093` instead, since listener configs are controller-owned
- B. Set `listener.security.protocol.map` first; `advertised.listeners` becomes dynamic once the map is defined
- C. Edit `advertised.listeners` in the broker's properties file and restart the broker — KRaft removed dynamic updates for this configuration
- D. Delete and re-create the broker's `meta.properties` so the new listener is picked up at registration

### Question 17 — `[CFG · Node identity · Single]`

A configuration-management template written for Kafka 2.x is applied to a new 4.3 broker. The template leaves the node identifier empty on purpose and sets `broker.id.generation.enable=true`. The broker refuses to start. What is the correct fix?

- A. Set `reserved.broker.max.id` higher than the number of brokers so an identifier can be allocated
- B. Start the broker with `--override broker.id.generation.enable=true` on the command line
- C. Set `broker.id=-1`, which instructs KRaft to derive the identifier from `directory.id`
- D. Assign an explicit `node.id`; KRaft removed both `broker.id.generation.enable` and `reserved.broker.max.id`, and every node must be given a stable identifier by the operator

### Question 18 — `[TROUBLE · Leader imbalance · Single]`

Two hours after a rolling restart, a topic looks like this:

```
$ kafka-topics.sh --bootstrap-server kafka-1:19092 --describe --topic orders
Topic: orders   TopicId: xB3k...   PartitionCount: 3   ReplicationFactor: 3   Configs: min.insync.replicas=2
        Topic: orders  Partition: 0  Leader: 4  Replicas: 2,3,4  Isr: 2,3,4  Elr:   LastKnownElr:
        Topic: orders  Partition: 1  Leader: 4  Replicas: 3,4,2  Isr: 3,4,2  Elr:   LastKnownElr:
        Topic: orders  Partition: 2  Leader: 4  Replicas: 4,2,3  Isr: 4,2,3  Elr:   LastKnownElr:
```

All three partitions are fully in sync but broker 4 leads all of them. What should the administrator do?

- A. Nothing is wrong: with `Isr` complete, leadership distribution has no effect on load
- B. Run `kafka-reassign-partitions.sh` to move the replicas so that each broker owns one partition
- C. Trigger `kafka-leader-election.sh --bootstrap-server kafka-1:19092 --election-type preferred --all-topic-partitions`, which returns leadership to the first replica in each `Replicas` list; `auto.leader.rebalance.enable` (default `true`) would also do this within `leader.imbalance.check.interval.seconds` (default 300)
- D. Set `unclean.leader.election.enable=true` so brokers 2 and 3 can take leadership back

### Question 19 — `[CFG · Config precedence · Multi — Choose 2]`

An administrator investigates why a topic is rejecting `acks=all` writes and runs:

```
$ kafka-configs.sh --bootstrap-server kafka-1:19092 --describe --all \
    --entity-type topics --entity-name payments | grep min.insync
  min.insync.replicas=3 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:min.insync.replicas=3, STATIC_BROKER_CONFIG:min.insync.replicas=2, DEFAULT_CONFIG:min.insync.replicas=1}
```

Which two conclusions are correct? (Choose two.)

- A. The effective value is 3 and it comes from a topic-level override, which wins over the broker's static configuration
- B. The effective value is 2, because a `STATIC_BROKER_CONFIG` always wins over a topic override
- C. Changing `min.insync.replicas` at the broker level will not change this topic's behaviour until the topic-level override is deleted
- D. The `DEFAULT_CONFIG` entry of 1 proves the broker was never configured and the cluster is running with defaults
- E. The `synonyms` column is only populated for broker entities; for topics it is always empty, so this output must have come from a broker query

### Question 20 — `[TROUBLE · Disk distribution · Single]`

One broker is at 91% disk usage while its peers sit near 40%. The administrator runs:

```
$ kafka-log-dirs.sh --bootstrap-server kafka-1:19092 --describe --broker-list 3
Querying brokers for log directories information
Received log directory information from brokers 3
{"version":1,"brokers":[{"broker":3,"logDirs":[{"logDir":"/data/1","error":null,"partitions":[
  {"partition":"clickstream-0","size":41203847168,"offsetLag":0,"isFuture":false},
  {"partition":"orders-1","size":109051904,"offsetLag":0,"isFuture":false}]}]}]}
```

What does this output establish, and what is the appropriate next step?

- A. `clickstream-0` alone accounts for almost all of the broker's usage, so the skew is a partition-placement problem: plan a `kafka-reassign-partitions.sh` move with `--throttle`, and remember that `--verify` is the step that removes the throttle
- B. `offsetLag: 0` proves the partition is corrupt and must be deleted
- C. The broker has only one log directory, so the fix is to add a second entry to `log.dirs`; Kafka will immediately rebalance existing partitions across both directories
- D. Reduce `log.retention.hours` cluster-wide from 168 to 24, which is the only reversible action available

### Question 21 — `[CFG · Controller administration · Single]`

An administrator needs to raise the log level of the KRaft controller process on `controller-1` to debug an election problem. Which command form is correct?

- A. `kafka-configs.sh --bootstrap-server kafka-1:19092 --alter --entity-type broker-loggers --entity-name 1 --add-config org.apache.kafka.raft=DEBUG`
- B. `kafka-configs.sh --bootstrap-controller controller-1:9093 --alter --entity-type broker-loggers --entity-name 1 --add-config org.apache.kafka.raft=DEBUG`
- C. `kafka-configs.sh --bootstrap-server controller-1:9093 --alter --entity-type controller-loggers --entity-name 1 --add-config org.apache.kafka.raft=DEBUG`
- D. Edit `log4j2.yaml` on the controller and restart it; controller log levels cannot be changed at runtime

### Question 22 — `[FUND · Two election mechanisms · Multi — Choose 2]`

A colleague claims that "Kafka elects leaders the same way everywhere: whoever has the most votes wins". Which two statements correctly distinguish the two mechanisms at work in a Kafka 4.3 cluster? (Choose two.)

- A. Partition leadership uses the ISR model: any replica currently in the in-sync replica set is eligible, so `f+1` replicas tolerate `f` failures without a majority vote
- B. Partition leadership requires a majority of the replica set to vote, which is why `replication.factor` must be odd
- C. Controller leadership uses Raft: a candidate must win votes from a **majority** of voters, and a follower grants its vote only if the candidate's log is at least as up to date as its own
- D. Controller leadership is granted to whichever controller has the lowest `node.id` among the live controllers
- E. Both mechanisms use `replica.lag.time.max.ms` (30000 ms) to decide who is eligible

### Question 23 — `[CFG · Internal topics · Multi — Choose 2]`

An engineer builds a single-broker Kafka 4.3 instance for a demo. The broker starts, but the first consumer group fails and the broker log repeatedly reports that the offsets topic cannot be created with the requested replication factor. Which two statements are correct? (Choose two.)

- A. `offsets.topic.replication.factor` defaults to 3, so a single-broker cluster must have it lowered to 1 before `__consumer_offsets` can be created
- B. `offsets.topic.num.partitions` defaults to 1 and must be raised to 50 before consumer groups can work
- C. `__consumer_offsets` has 1 partition, the same as `__cluster_metadata`
- D. The fix is to set `min.insync.replicas=0` on the broker
- E. `transaction.state.log.replication.factor` (default 3) and `transaction.state.log.min.isr` (default 2) will cause the same class of failure and must also be lowered on a single-broker cluster

### Question 24 — `[ARCH · Controller decommissioning · Single]`

A controller machine in a dynamic-quorum cluster must be retired. Which sequence protects quorum availability?

- A. Shut the machine down, then run `kafka-metadata-quorum.sh remove-controller` to clean up the stale entry
- B. Run `kafka-metadata-quorum.sh --bootstrap-controller <live-controller>:9093 remove-controller --controller-id <id> --controller-directory-id <uuid>` **before** shutting the machine down, so the voter set shrinks while a majority is still available
- C. Delete the controller's `meta.properties`, restart it, and let it re-register as an observer
- D. Remove the node from `controller.quorum.bootstrap.servers` on every broker and perform a rolling restart of the brokers

### Question 25 — `[CFG · Version upgrade · Single]`

A cluster has just been rolled from Kafka 4.2 to 4.3 on every node. The team's old runbook says: *"finish the upgrade by setting `inter.broker.protocol.version=4.3` in `server.properties` and performing a second rolling restart."* What should the administrator do instead?

- A. Follow the runbook; `inter.broker.protocol.version` is still the way to finalise an upgrade
- B. Nothing — the metadata version is derived automatically from the running binaries
- C. Finalise with `kafka-features.sh upgrade --release-version 4.3`; KRaft replaced `inter.broker.protocol.version` with `metadata.version`, which is a cluster-wide feature level and does not require a second restart
- D. Run `kafka-storage.sh format --cluster-id <id>` again on each node to write the new version into `meta.properties`

### Question 26 — `[TROUBLE · Broker failure and ISR · Multi — Choose 2]`

Broker 3 is stopped for maintenance on a cluster with `replication.factor=3`, `min.insync.replicas=2` and `unclean.leader.election.enable=false`. `kafka-topics.sh --describe` now shows `Isr: 2,4` for partitions that previously showed `Isr: 2,3,4`, and leadership for the partitions that broker 3 led has moved elsewhere. Which two statements are correct? (Choose two.)

- A. Producers using `acks=all` continue to succeed, because the ISR size of 2 still satisfies `min.insync.replicas=2`
- B. `UnderReplicatedPartitions` stays at 0, because an ISR of 2 still satisfies `min.insync.replicas=2`
- C. Leadership moved because the controller elected a replica from outside the ISR, which is why `unclean.leader.election.enable` had to be `false`
- D. Broker 3 was removed from the ISR only after `replica.lag.time.max.ms` (30000 ms) elapsed, regardless of how it was stopped
- E. When broker 3 returns, leadership will eventually move back to its preferred partitions because `auto.leader.rebalance.enable` defaults to `true`

### Question 27 — `[FUND · CCDAK Week 2 review · Single]`

A topic has `replication.factor=3` and `min.insync.replicas=2`. One broker is already down. A second broker now fails, and a producer configured with `acks=all` starts throwing:

```
org.apache.kafka.common.errors.NotEnoughReplicasException: The size of the current ISR Set(4)
is insufficient to satisfy the min.insync.replicas requirement of 2 for partition orders-1
```

An on-call engineer proposes setting `min.insync.replicas=1` on the topic to restore writes immediately. How should the administrator respond?

- A. Approve it: lowering the minimum is the standard remedy and carries no risk
- B. Reject it as the first action. Lowering `min.insync.replicas` removes the durability guarantee exactly when the cluster is least able to protect data — a single remaining replica means an acknowledged write is lost if that broker dies. Restore a failed broker first; lowering the minimum is a deliberate, time-boxed trade-off, not a reflex
- C. Approve it, but also set `acks=1` on the producer so the setting takes effect
- D. Reject it and enable `unclean.leader.election.enable=true` instead, which restores writes without touching durability

### Question 28 — `[FUND · CCDAK Week 4 review · Single]`

A consumer group named `billing` reports that offset commits started failing a few seconds after one broker was taken down for patching, even though the group's topic partitions all have healthy leaders on other brokers. What is the most likely explanation?

- A. The broker that went down hosted the leader of the `__consumer_offsets` partition `hash("billing") % 50`, so it was the group coordinator; commits fail until a new leader for that internal partition is elected and the group re-discovers its coordinator
- B. Offset commits are metadata operations and always go to the active controller, which was on the broker that went down
- C. `__consumer_offsets` is a single-partition topic, so any broker failure stops all offset commits cluster-wide
- D. The group must be re-created with `kafka-consumer-groups.sh --delete` before commits resume

---

> ✅ Done? Check your answers in [answers.md](answers.md), log every wrong answer with its **reason for being wrong** (missing knowledge / missed a qualifier / fell for a trap / ran out of time), and re-read the matching section of the [week plan](README.md) before moving on to Week 2.
