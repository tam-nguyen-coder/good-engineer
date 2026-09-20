# ✅ Answers — CCAAK Mock Exam 01

> Chỉ mở sau khi đã làm hết 60 câu trong [questions.md](questions.md) với đồng hồ 90 phút.
> Back to [mock index](../README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-D · 4-A · 5-B · 6-C · 7-B · 8-D · 9-A · 10-B · 11-A · 12-D · 13-AD · 14-BC · 15-C · 16-D · 17-A · 18-B · 19-C · 20-C · 21-AC · 22-B · 23-D · 24-D · 25-A · 26-B · 27-BD · 28-C · 29-D · 30-A · 31-B · 32-AB · 33-C · 34-CE · 35-AD · 36-BC · 37-D · 38-A · 39-B · 40-C · 41-A · 42-D · 43-AD · 44-BC · 45-ABC · 46-A · 47-CE · 48-C · 49-B · 50-C · 51-D · 52-A · 53-BD · 54-B · 55-C · 56-D · 57-AC · 58-A · 59-B · 60-C

> 📌 Với câu `Multi`, chỉ tính **đúng** khi chọn đủ và đúng mọi phương án — không có điểm một phần.

---

## 📊 Chấm điểm theo domain

| Domain | Tỉ trọng | Câu số | Số đúng / Tổng | % | Ngưỡng |
| --- | --- | --- | --- | --- | --- |
| **CFG** — Cluster Configuration | 22% | 1, 7, 10, 13, 15, 19, 23, 26, 32, 37, 41, 44, 55 | ___ / 13 | ___ % | ≥ 77% (10/13) |
| **FUND** — Kafka Fundamentals | 15% | 3, 11, 17, 24, 29, 35, 46, 49, 53 | ___ / 9 | ___ % | ≥ 78% (7/9) |
| **SEC** — Security | 15% | 4, 12, 20, 27, 33, 39, 47, 54, 58 | ___ / 9 | ___ % | ≥ 78% (7/9) |
| **TROUBLE** — Troubleshooting | 15% | 2, 8, 14, 22, 30, 38, 43, 50, 56 | ___ / 9 | ___ % | ≥ 78% (7/9) |
| **ARCH** — Deployment Architecture | 12% | 9, 21, 31, 40, 48, 57, 59 | ___ / 7 | ___ % | ≥ 71% (5/7) |
| **CONNECT** — Kafka Connect | 12% | 5, 18, 28, 36, 45, 52, 60 | ___ / 7 | ___ % | ≥ 71% (5/7) |
| **OBS** — Observability | 10% | 6, 16, 25, 34, 42, 51 | ___ / 6 | ___ % | ≥ 67% (4/6) |
| **TỔNG** | 101%* | 1–60 | ___ / 60 | ___ % | **≥ 80% (48/60)** |

\* Tổng tỉ trọng công bố là 101% do Confluent làm tròn từng domain — đây là con số chính thức, không phải lỗi chép.

> ⚠️ Confluent **không công bố** ngưỡng đậu (chấm Pass/Fail). Con số ~75% lưu truyền trên mạng chỉ là phỏng đoán cộng đồng. Ngưỡng 80% ở trên là **ngưỡng cá nhân** đặt cao hơn để có biên an toàn.

---

### Question 1 — Answer: **B**

- **Why correct:** `--describe --all` prints `synonyms={...}` ordered **strongest first**, so the leftmost entry is the source actually in effect. Here that is `DYNAMIC_TOPIC_CONFIG`, which sits at the top of the five-level precedence list (topic override → per-broker dynamic → cluster-wide dynamic default → static `server.properties` → built-in default). Deleting the topic override does **not** restore the documented default — it falls through to the next level that still exists, which is the dynamic cluster-wide default of 86,400,000 ms.
- **Why the others are wrong:** A — configuration precedence is evaluated on every read; nothing is queued, and leader election has no bearing on it. C — Kafka 4.x is KRaft-only: the overrides live in the metadata log, there is no `/config/topics` znode, and `kafka-configs.sh` has no `--zookeeper` flag any more. D — `retention.ms` is a topic configuration and is fully dynamic; no restart is involved.
- 🧠 **Key point / trap:** "I set the cluster-wide default, so we are done" is the single most common configuration mistake in Kafka operations. A cluster-wide default can never beat an override that already exists on a topic. Always read the synonyms list.
- 📎 Source: `../../study-plan/week-02/resources/confluent-dynamic-config-precedence.md`

### Question 2 — Answer: **C**

- **Why correct:** retention only ever considers **closed** segments; the active segment is never deleted. A segment closes when it reaches `segment.bytes` (1 GiB by default) or when `segment.ms` elapses (seven days by default). At 5 MB per day this topic will not fill a 1 GiB segment for over five hundred years, so the only thing that can close it is time. Setting `segment.ms=3600000` on the topic is a dynamic override, takes effect on the next roll, and is trivially reversible.
- **Why the others are wrong:** A — `log.retention.check.interval.ms` only changes how often the retention sweep runs; the sweep is already running and correctly finding nothing eligible. B — `log.roll.hours` is the **broker-level** name for the same idea, needs a restart, and would change every topic on the cluster; the qualifier asks for the first action, not the widest one. D — deleting and re-creating a topic to expire data is destructive, disruptive to every producer and consumer, and unnecessary.
- 🧠 **Key point / trap:** "retention is set to one hour but the data is still there" is a standing CCAAK reflex question. The answer is always the segment roll, and the lever is `segment.ms` on the topic (`log.roll.ms` / `log.roll.hours` on the broker).
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs-overrides.md` (topic `segment.ms` ↔ broker `log.roll.ms`; defaults) and `../../CCAAK-STUDY-PLAN.md` §7.

### Question 3 — Answer: **D**

- **Why correct:** in KRaft the controllers form a Raft quorum of **voters**. When a voter stops hearing from the leader within `controller.quorum.fetch.timeout.ms` (2,000 ms) it stands for election, and the winner already holds the replicated metadata log on local disk — there is no state to load from anywhere, which is precisely why failover is so much faster than it was under ZooKeeper. Brokers fetch the same log but are **observers**: they never vote and are never candidates.
- **Why the others are wrong:** A — `node.id` plays no part in leader election; Raft elects on log completeness and votes. B — this is the ZooKeeper answer, and it is the single most frequently mis-taught fact in public CCAAK material: there are no ephemeral nodes in Kafka 4.x because there is no ZooKeeper. C — `__consumer_offsets` holds consumer group offsets and has nothing to do with cluster metadata; the metadata log is `__cluster_metadata`, and the new leader does not need to reload it.
- 🧠 **Key point / trap:** any option that mentions a znode, an ephemeral node, `--zookeeper` or `zookeeper.connect` is wrong on a 4.x exam. Memorise the mapping: ephemeral `/controller` node → Raft election among voters.
- 📎 Source: `../../study-plan/week-01/resources/kraft-operations-production.md` and `../../study-plan/week-01/resources/zk2kraft-removed-configs-and-cli.md`

### Question 4 — Answer: **A**

- **Why correct:** `StandardAuthorizer` (KIP-801) stores ACLs as records in `__cluster_metadata`. A `CreateAcls` request is routed to the **active controller**, which appends the record; brokers and standby controllers then read the log and refresh their in-memory ACL map. `kafka-acls.sh` returns as soon as the controller has committed, so application of the rule across the fleet is **asynchronous and eventually consistent**. A couple of hundred milliseconds of `TopicAuthorizationException` after a grant is expected behaviour.
- **Why the others are wrong:** B — there is no ZooKeeper and therefore no watch; this is a 3.x-era explanation. C — `StandardAuthorizer` does not cache negative decisions on a timer; it evaluates against the current in-memory ACL map on every request. D — a `Group` ACL **was** granted (`--group reporting` in the command), and a missing group ACL would produce `GroupAuthorizationException`, not `TopicAuthorizationException`; nor would it heal itself.
- 🧠 **Key point / trap:** the operational rule is "grant, then retry before you investigate". Re-issuing the ACL because the first attempt looked like it failed is how operators end up with duplicated and contradictory rules.
- 📎 Source: `../../study-plan/week-05/resources/kip-801-standard-authorizer.md`

### Question 5 — Answer: **B**

- **Why correct:** Connect stores the whole connector configuration state machine in the config topic and replays it in strict order on every worker, which is only possible with a **single** partition. That constraint is hard-coded, not a tunable. `offset.storage.partitions` (default 25) and `status.storage.partitions` (default 5) are genuine settings and may be changed; all three topics must be `cleanup.policy=compact`.
- **Why the others are wrong:** A — **`config.storage.partitions` does not exist.** Inventing it is the trap: there is no way to tell Connect to accept a multi-partition config topic. C — Connect is perfectly happy with pre-created internal topics; it only validates their shape. D — replication factor and partition count are unrelated; the error names partitions explicitly.
- 🧠 **Key point / trap:** remember the three internal topics as **1 / 25 / 5**, all compacted, all with replication factor 3 by default. The "1" is a requirement; the other two are defaults.
- 📎 Source: `../../study-plan/week-06/resources/connect-worker-configs-4.3.md`

### Question 6 — Answer: **C**

- **Why correct:** the controller metrics are split across two MBean types, and a JMX exporter rule that matches only one of them drops the rest without any error. `ActiveControllerCount` and `OfflinePartitionsCount` are under `kafka.controller:type=KafkaController`; `UncleanLeaderElectionsPerSec` and `LeaderElectionRateAndTimeMs` are under `kafka.controller:type=ControllerStats`; and `UnderReplicatedPartitions` is under `kafka.server:type=ReplicaManager` entirely. The alert never fires because the series never existed.
- **Why the others are wrong:** A — Yammer rate metrics do expose `Count` alongside `OneMinuteRate`, but the pattern would still not match because the **type** is wrong; fixing `Value` alone changes nothing. B — the metric has existed for many versions and is documented on the 4.3 monitoring page. D — remote JMX being off by default is true, but the exporter is clearly working: other controller metrics are being collected.
- 🧠 **Key point / trap:** a monitoring gap that is caused by a *pattern* rather than by a broker is invisible by construction. After writing exporter rules, verify by listing what actually landed in Prometheus, not by reading the YAML.
- 📎 Source: `../../study-plan/week-07/resources/kafka-monitoring-metrics.md` and `../../study-plan/VALIDATION.md` (mục *Chi tiết dễ sai — đã xác minh*).

### Question 7 — Answer: **B**

- **Why correct:** 1-Z · 2-W · 3-X · 4-Y. `num.io.threads` (default **8**) is the request-handler pool that does the actual work after a network thread has read the request. `num.replica.fetchers` (default **1**) is the per-source-broker fetcher pool that keeps followers caught up. `num.recovery.threads.per.data.dir` (default **2** since 4.0) is used only at startup recovery and at shutdown flush. `background.threads` (default **10**) is the general housekeeping pool.
- **Why the others are wrong:** A swaps the request-handler pool with the replica fetchers (`1-W`, `2-Z`) — the classic confusion between "threads that serve clients" and "threads that pull from other brokers". C swaps recovery threads and replica fetchers (`2-X`, `3-W`), i.e. a startup-only pool with a continuously running one. D makes `num.io.threads` the generic background pool and demotes `background.threads` to request handling, inverting both.
- 🧠 **Key point / trap:** learn the thread pools in the order a request travels: network thread reads the socket → request lands in the queue (`queued.max.requests`, 500) → I/O thread handles it. Replica fetchers and recovery threads sit outside that path entirely.
- 📎 Source: `../../study-plan/week-02/resources/kafka-broker-configs-storage-threads.md` and `../../CCAAK-STUDY-PLAN.md` §6.

### Question 8 — Answer: **D**

- **Why correct:** with `acks=all` the leader requires `min.insync.replicas` members in the ISR before it will append. `min.insync.replicas=3` on a topic with `replication.factor=3` means the ISR must be complete — the tolerated failure count is **zero**. Every routine restart, every GC pause long enough to evict a follower, and every network blip stops writes. The incident ends when the patched broker rejoins; the correction is `min.insync.replicas=2`, made as a planned change so RF=3 buys one replica of slack.
- **Why the others are wrong:** A — the ISR shrank because a replica was deliberately shut down, not because it lagged; raising `replica.lag.time.max.ms` would delay eviction of genuinely slow followers and mask real problems. B — unclean leader election trades data for availability and does not even apply here: the partition still has a leader, it is the `min.isr` gate that is refusing writes. C — going to RF=5 is the "correct but far too much" option: it triples replication traffic and storage to work around a one-character configuration error.
- 🧠 **Key point / trap:** memorise the matrix — with `acks=all`, the number of replica failures you can absorb is `replication.factor − min.insync.replicas`. RF=3/min.isr=2 gives 1. RF=3/min.isr=3 gives 0. RF=3/min.isr=1 gives 2, but a single surviving replica can lose acknowledged data.
- 📎 Source: `../../study-plan/week-03/resources/kafka-design-replication.md` and `../../CCAAK-STUDY-PLAN.md` §6.

### Question 9 — Answer: **A**

- **Why correct:** Cluster Linking is built into Confluent Server: the destination broker pulls from the source like an inter-cluster follower, so there is no Connect cluster, no connector and no task to operate. Replication is byte-for-byte with globally consistent offsets, so no offset translation is needed, and consumer offsets plus ACLs are synced to the destination — which is what makes the RTO low. Mirror topics are read-only on the destination until the link is promoted.
- **Why the others are wrong:** B — `IdentityReplicationPolicy` keeps the topic **name**, not the offsets; MM2 offsets never line up and `sync.group.offsets.enabled` writes *translated* (deliberately conservative) offsets, so consumers may reprocess. It also means running and operating a Connect cluster, which is the opposite of "fewest moving parts". C — a stretch cluster is synchronous and does give RPO 0, but it is a different architecture with an inter-AZ latency cost on every produce, and the question explicitly accepts asynchronous replication. D — MirrorMaker 1 was **removed in Kafka 4.0**, and `--whitelist` went with it.
- 🧠 **Key point / trap:** the decision rule is short — *"offsets must line up and I want the least to operate"* → Cluster Linking (Confluent only); *"pure Apache Kafka, or active/active"* → MirrorMaker 2.
- 📎 Source: `../../study-plan/week-04/resources/confluent-cluster-linking.md` and `../../study-plan/week-04/resources/kafka-geo-replication-mm2.md`

### Question 10 — Answer: **B**

- **Why correct:** quota precedence has **eight** levels and the most specific match wins. Level 1, (matching user, matching client-id), is not configured here. Level 2, (matching user, **default** client-id), is — so `svc-etl` with any client-id gets 5,242,880 B/s. That beats level 6 (default user quota) and level 7 (matching client-id quota) even though the client-id rule looks more specific to the eye. Quotas are enforced **per broker**, so a producer talking to six brokers can write up to six times the quota in aggregate.
- **Why the others are wrong:** A — a bare client-id rule is level 7, near the bottom; a user-scoped rule always outranks it. C — the default-user rule is level 6, below the matching-user rules. D — Kafka explicitly declined to implement cluster-wide quotas, because sharing usage between brokers is harder than the quota mechanism itself; the docs say so in as many words.
- 🧠 **Key point / trap:** two things get tested together here. First, user-scoped beats client-scoped, always. Second, **a quota is per broker** — the number you configure has to be divided by the broker count before you can call it a cluster budget.
- 📎 Source: `../../study-plan/week-03/resources/kafka-design-quotas.md`

### Question 11 — Answer: **A**

- **Why correct:** the order is 1 → 2 → 3 → 4. A single `cluster.id` must exist before anything can be formatted, because every node has to be formatted with the **same** id — a mismatch produces `InconsistentClusterIdException`. Formatting is what writes `meta.properties` and, with `--add-scram`, what seeds the inter-broker SCRAM credential; that credential cannot be created later with `kafka-configs.sh`, because the brokers need it in order to talk to the cluster in the first place. Controllers come up next so that a quorum leader exists, and brokers join last as observers.
- **Why the others are wrong:** B (1 → 3 → 2 → 4) — a node cannot be started before its storage is formatted; `kafka-storage.sh format` is a prerequisite of the first boot, not something applied to a running node. C (2 → 1 → 3 → 4) — formatting requires the id as an argument, so generating it afterwards is not a sequence. D (1 → 2 → 4 → 3) — brokers started before any controller has no quorum to register with; they will retry, but the run order is wrong and makes the failure mode much harder to read.
- 🧠 **Key point / trap:** the `--add-scram` step at format time is the part people miss. If SCRAM is the inter-broker mechanism, the credential is a **bootstrap** concern, not a day-two concern.
- 📎 Source: `../../study-plan/week-01/resources/kafka-quickstart-and-storage-format.md` and `../../study-plan/week-05/resources/kafka-sasl-operations.md`

### Question 12 — Answer: **D**

- **Why correct:** 1-Z · 2-W · 3-X · 4-Y. SCRAM credentials are kept in the KRaft metadata log, so users are added, re-hashed (minimum 4,096 iterations) and deleted with `kafka-configs.sh --entity-type users` while the cluster runs — no file on disk, no restart. PLAIN reads a static list from the broker's JAAS configuration, so every user change means editing a file and bouncing the broker unless a custom callback handler is plugged in. GSSAPI delegates identity to a Kerberos KDC and the broker authenticates with a keytab. OAUTHBEARER holds no user list at all; the broker validates a token issued by an external identity provider.
- **Why the others are wrong:** A swaps SCRAM and PLAIN (`1-W`, `2-Z`), which inverts the single most operationally important distinction of the four. B swaps Kerberos and OAuth (`3-Y`, `4-X`) — one keeps identities in a KDC you run, the other in an IdP you federate with. C puts SCRAM in a KDC and Kerberos in the metadata log, mixing both axes at once.
- 🧠 **Key point / trap:** the exam question behind this matching is always "can I revoke a user without a restart?" — yes for SCRAM and OAUTHBEARER, no for PLAIN. And even for SCRAM, revocation only closes existing connections if `connections.max.reauth.ms` is non-zero (see question 47).
- 📎 Source: `../../study-plan/week-05/resources/kafka-sasl-operations.md`

### Question 13 — Answer: **A, D**

- **Why correct:** A — `max.request.size` (default 1,048,576) is checked inside `KafkaProducer.send()` before a byte leaves the JVM, so no broker-side setting can rescue an oversized record; the exception text even names the configuration. D — the topic's `max.message.bytes` overrides the broker's `message.max.bytes` (default **1,048,588**) for that topic, and both are dynamic: `message.max.bytes` is one of the cluster-wide dynamic broker configurations, and topic overrides are always dynamic.
- **Why the others are wrong:** B — `replica.fetch.max.bytes` is explicitly **not** an absolute maximum; the docs state that if the first record batch in the first non-empty partition is larger, it is returned anyway so that replication can make progress. C — `socket.request.max.bytes` defaults to **104,857,600** (100 MiB), not 1 MiB, and is nowhere near the constraint. E — `message.max.bytes` is changeable at runtime, so the restart claim is wrong.
- 🧠 **Key point / trap:** the three tiers are producer (`max.request.size`) → broker/topic (`message.max.bytes` / `max.message.bytes`) → consumer fetch sizing. Only the first two can reject a record outright, and the exception text always tells you which one fired.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs-overrides.md` and `../../study-plan/week-03/resources/kafka-broker-configs-replication-throughput.md`

### Question 14 — Answer: **B, C**

- **Why correct:** a quota violation is enforced by **delaying the response** and muting the client's socket channel for the computed delay — the broker never raises an error for bandwidth quotas. That is exactly why the symptom is "a hard ceiling with completely clean logs". The two places the delay is visible are the client metric `produce-throttle-time-avg` / `produce-throttle-time-max` (B) and the broker MBean `kafka.server:type=Produce,user=...,client-id=...` attribute `throttle-time`, which should read 0 on an unthrottled client (C).
- **Why the others are wrong:** A — `ThrottlingQuotaExceededException` exists, but it belongs to the **controller mutation** quota (KIP-599) on administrative requests such as `CreateTopics`; bandwidth quotas never surface as an exception, so a clean log is evidence *for* a quota, not against it. D — quotas are enforced independently on each broker, not aggregated by the controller. E — `queued.max.requests` (500) governs the broker's request queue depth and has nothing to do with a per-client rate ceiling; raising it treats an invented problem.
- 🧠 **Key point / trap:** "throughput is pinned at a suspiciously round number and nothing is logged" is a quota until proven otherwise. Reach for `throttle-time` before you touch any thread or buffer setting.
- 📎 Source: `../../study-plan/week-03/resources/kafka-design-quotas.md`

### Question 15 — Answer: **C**

- **Why correct:** Kafka assigns a new partition to the data directory that currently holds the **fewest partitions**, and it counts partitions — it never looks at free space. A partition also lives entirely in one directory and is never split across two. So a topic with a handful of enormous partitions produces exactly this picture: equal counts, wildly unequal bytes. The remedy is to move specific replicas between directories on the same broker, which is `kafka-reassign-partitions.sh` with a plan that carries a `log_dirs` array alongside `replicas` (`"any"` lets Kafka choose).
- **Why the others are wrong:** A — a failing directory is reported by a non-null `error` field and by `OfflineLogDirectoryCount` / `LogDirectoryOffline`; here `error` is `null` on all three. B — `auto.leader.rebalance.enable` moves **leadership**, never bytes, and `leader.imbalance.check.interval.seconds` schedules that leadership check; nothing in Kafka rebalances disks by itself. D — Kafka's own documentation prefers JBOD to RAID: RAID costs write throughput and usable space, and the redundancy it provides is already supplied by replication. Rebuilding an array is also the "correct but disproportionate" answer to a byte-skew problem.
- 🧠 **Key point / trap:** "round-robin by partition **count**, not by free space" is a standing CCAAK fact. It is the reason disk imbalance keeps appearing on clusters whose partitions are evenly spread.
- 📎 Source: `../../study-plan/week-02/resources/kafka-hardware-os-disks-jbod.md` and `../../study-plan/week-02/resources/kafka-log-dirs-tool.md`

### Question 16 — Answer: **D**

- **Why correct:** `records-lag-max` measures the distance from the consumer's position to the **log end offset** — how far behind the writer it is. `records-lead-min` measures the distance from the position to the **log start offset** — how much margin remains before retention deletes data the consumer has not read. Lead collapsing towards zero while lag is flat means the consumer is keeping pace with the producer but the retention cliff is catching up from behind. Raising `retention.ms` is dynamic, instant and reversible, which makes it the correct first move while the real throughput problem is diagnosed.
- **Why the others are wrong:** A — lead is not a buffer metric; ignoring it is how silent data loss happens. B — raising the partition count is **one-way**, breaks key ordering for existing keys, and does nothing for records that are about to be deleted in the next few minutes. C — resetting to `latest` deliberately discards exactly the records that are at risk; it converts a warning into the loss it was warning about.
- 🧠 **Key point / trap:** lag says "am I behind?"; lead says "am I about to lose data?". Alert on both. A consumer with stable lag can still be minutes away from a gap.
- 📎 Source: `../../study-plan/week-07/resources/confluent-consumer-lag-monitoring.md` and `../../study-plan/week-07/resources/kafka-monitoring-metrics.md`

### Question 17 — Answer: **A**

- **Why correct:** Kafka 4.0 changed the producer default `linger.ms` from **0** to **5**. The producer now waits up to 5 ms for a batch to fill, which is precisely the observed picture: about 5 ms added to median latency, larger batches, fewer requests, and equal or better throughput. Setting `linger.ms=0` on this one client restores the old behaviour without affecting anyone else.
- **Why the others are wrong:** B — `acks` has defaulted to `all` since Kafka **3.0**, so it did not change in this upgrade; and reducing it to 1 would weaken durability to chase 5 ms. C — `batch.size` still defaults to 16,384 and is a size target, not a timer; it cannot add a fixed latency floor. D — broker flush behaviour is unchanged and Kafka's guidance is to leave application-level fsync off entirely and rely on replication plus OS flushing.
- 🧠 **Key point / trap:** the 4.0 default changes that bite operators are `linger.ms` 0→5, `num.recovery.threads.per.data.dir` 1→2 and `message.timestamp.after.max.ms` `Long.MAX`→1 hour. All three show up as "we changed nothing and behaviour changed".
- 📎 Source: `../../study-plan/week-07/resources/kafka-upgrade-notable-changes.md`

### Question 18 — Answer: **B**

- **Why correct:** in Kafka Connect a task that reaches `FAILED` stays there. It is not restarted by the framework, it does not trigger a rebalance, and the connector object can happily report `RUNNING` beside it — which is why `/status` must always be read down to the `tasks[]` array. `POST /connectors/{name}/restart?includeTasks=true&onlyFailed=true` restarts the connector together with just its failed tasks and returns 202 when tasks were included.
- **Why the others are wrong:** A — `scheduled.rebalance.max.delay.ms` governs how long the leader defers reassigning the tasks of a **departed worker**; it has nothing to do with a failed task on a live worker. C — restarting the whole worker does work, but it also disrupts every other connector's tasks hosted there; the REST endpoint exists precisely so you do not have to. D — deleting and re-creating the connector is the most destructive option on the list and is never required to clear a FAILED task.
- 🧠 **Key point / trap:** `connector.state: RUNNING` means nothing on its own. The two flags that matter are `tasks[].state` and, when a task has failed, `tasks[].trace`. Expect a 409 if a rebalance is in progress — retry rather than escalating.
- 📎 Source: `../../study-plan/week-06/resources/connect-rest-api-reference.md`

### Question 19 — Answer: **C**

- **Why correct:** the order is 3 → 4 → 1 → 2 — topic override, then per-broker dynamic, then cluster-wide dynamic default, then the static `server.properties` value, with Kafka's built-in `DEFAULT_CONFIG` always last. This is the exact order `kafka-configs.sh --describe --all` prints in the `synonyms={...}` list, leftmost first.
- **Why the others are wrong:** A (4 → 3 → 1 → 2) — puts per-broker dynamic above the topic override; a topic override always wins, which is why cluster-wide changes so often appear to have no effect. B (3 → 1 → 4 → 2) — swaps the two dynamic broker levels; the more specific per-broker value beats the cluster-wide default, not the other way round. D (2 → 3 → 4 → 1) — puts the static file at the top, which is the intuition people bring from ordinary application configuration and is exactly backwards for Kafka.
- 🧠 **Key point / trap:** `--delete-config` does not restore the documented default; it falls through to the next level that still exists. That is the second half of this list and the part that surprises people during incidents.
- 📎 Source: `../../study-plan/week-02/resources/confluent-dynamic-config-precedence.md`

### Question 20 — Answer: **C**

- **Why correct:** `AclAuthorizer` kept its ACLs in ZooKeeper znodes and installed ZooKeeper watches to propagate changes. With ZooKeeper removed in 4.0 the class is gone from the binary, so referencing it fails class loading and the node exits. The KRaft replacement is `org.apache.kafka.metadata.authorizer.StandardAuthorizer` (KIP-801, available since 3.2), and it must be configured on **every broker and every controller** — the controller needs it because it authorizes administrative requests forwarded by brokers.
- **Why the others are wrong:** A — `zookeeper.connect` was removed along with everything else in the `zookeeper.*` namespace; adding it would be a second `ConfigException`. B — there is no jar to add; the class does not exist in 4.x at all. D — the package changed too. `StandardAuthorizer` lives in `org.apache.kafka.metadata.authorizer`, not `kafka.security.authorizer`, and getting the package wrong produces the identical error.
- 🧠 **Key point / trap:** learn the fully qualified name, not just the class name. `super.users` and `allow.everyone.if.no.acl.found` behave identically to the old authorizer, so old ACL documentation is still semantically valid — only the class name and the storage location changed.
- 📎 Source: `../../study-plan/week-05/resources/kip-801-standard-authorizer.md` and `../../study-plan/week-05/resources/kafka-authorization-acls.md`

### Question 21 — Answer: **A, C**

- **Why correct:** A — a Raft quorum of 2N+1 voters tolerates N concurrent failures, so surviving two losses requires **five** controllers; three would only survive one. C — four voters need a majority of three to be alive, exactly like three voters, so an even quorum size tolerates the same single failure while costing an extra machine. This is why the documentation talks about 3 or 5 and never 4.
- **Why the others are wrong:** B — controllers are remarkably light: roughly 5 GB of RAM and 5 GB of disk for the metadata log directory in a typical cluster. They hold cluster metadata, not partition data, which is precisely why dedicating nodes to the role is cheap. D — brokers are **observers**; they replicate the metadata log but never vote and are never candidates, regardless of how many controllers are lost. E — the metadata log is a single Raft-replicated partition; adding voters adds durability and failure tolerance, never write throughput. If anything, more voters means more replication work per write.
- 🧠 **Key point / trap:** "how many controllers?" is answered by how many simultaneous failures you must absorb, and the answer is always an odd number. The follow-up the exam likes is the cost argument for separating roles — see question 57.
- 📎 Source: `../../study-plan/week-01/resources/kraft-operations-production.md` and `../../study-plan/week-04/resources/kafka-kraft-controller-topology.md`

### Question 22 — Answer: **B**

- **Why correct:** the order is 3 → 1 → 4 → 2. `--generate` proposes a plan and prints **two** JSON documents — the current assignment, which is your rollback, and the proposed one. `--execute` applies it, and `--throttle` is supplied at that point so replication does not saturate the network while a nearly full broker is being drained. `--verify` is then run repeatedly until every partition reports completed, and it is `--verify` that **removes the throttle**. Only then does it make sense to confirm that the disk recovered and that under-replication has cleared.
- **Why the others are wrong:** A (1 → 3 → 4 → 2) — you cannot execute a plan that has not been generated. C (3 → 1 → 2 → 4) — checking disk and under-replication before `--verify` would report a healthy-looking state while the throttle is still in force; the throttle then stays behind permanently. D (3 → 4 → 1 → 2) — verifying before executing reports nothing useful and leaves the throttle configuration untouched.
- 🧠 **Key point / trap:** the throttle is set for you but **not** removed for you. A forgotten `leader.replication.throttled.rate` is a classic cause of chronic `UnderReplicatedPartitions` weeks later, when nobody connects the two events. Always finish with `--verify`.
- 📎 Source: `../../study-plan/week-04/resources/kafka-ops-expanding-reassignment.md`

### Question 23 — Answer: **D**

- **Why correct:** tiered storage splits retention in two. `retention.ms` / `retention.bytes` govern the **total** lifetime of a record including the remote tier; `local.retention.ms` / `local.retention.bytes` (broker-level: `log.local.retention.ms` / `log.local.retention.bytes`) govern how long it also stays on broker disk. The default of **-2** means *inherit the total retention value* — so leaving it alone with `retention.ms` at 400 days keeps 400 days locally too, and nothing is saved. Setting `local.retention.ms` to a few hours is the whole point of the feature.
- **Why the others are wrong:** A — `remote.log.copy.disable=true` stops uploading **new** segments while keeping already-uploaded ones readable; it is a step in removing tiered storage from a topic, and here it would make things worse. B — there is no clamp on `retention.ms`; the value is honoured. C — tiered storage works with normal replication factors. The genuine restrictions are different ones: compacted topics are not supported, and neither is combining `remote.storage.enable=true` with multiple `log.dirs`.
- 🧠 **Key point / trap:** **-2 means "inherit", not "unlimited".** That single value is the difference between tiered storage saving money and tiered storage costing you both disk and object storage.
- 📎 Source: `../../study-plan/week-02/resources/kafka-tiered-storage.md` and `../../CCAAK-STUDY-PLAN.md` §6.

### Question 24 — Answer: **D**

- **Why correct:** the order is 2 → 4 → 1 → 3. The documented KRaft selection sequence with ELR enabled is: if the ISR is not empty, pick from it; otherwise, if the ELR set is not empty, pick an unfenced member of it; otherwise pick the last known leader if it is unfenced. If none of those apply the partition has no leader and `OfflinePartitionsCount` rises — at which point unclean leader election is the only remaining lever, and it costs data.
- **Why the others are wrong:** A (4 → 2 → 1 → 3) — puts ELR ahead of the ISR; an in-sync replica is always preferred, since ELR exists only for the case where the ISR has emptied. B (2 → 1 → 4 → 3) — puts the last known leader ahead of the ELR set, which discards the whole benefit of KIP-966: an ELR member is provably safe thanks to the strict-min-ISR rule, whereas the last known leader is a weaker fallback. C (2 → 4 → 3 → 1) — gives up before trying the last known leader, which is the pre-4.0 behaviour and is still the third rule.
- 🧠 **Key point / trap:** ELR does not replace unclean leader election; it *shrinks the set of situations where you are forced to use it*. When a partition is offline while a broker holding its data is alive, think ELR before you think unclean.
- 📎 Source: `../../study-plan/week-03/resources/kafka-eligible-leader-replicas.md`

### Question 25 — Answer: **A**

- **Why correct:** each node reports `ActiveControllerCount` as 0 or 1, and exactly one node in the cluster should report 1 — so the cluster-wide **sum** is the metric that matters. A sum of 0 has two very different causes, and the evidence here points at the boring one: administration works, so a controller clearly is active, and the likely fault is that the JMX exporter was deployed onto the broker nodes only and never onto the dedicated controllers. `kafka-metadata-quorum.sh describe --status` answers the question definitively by printing `LeaderId`.
- **Why the others are wrong:** B — only the **active** controller reports 1; standby controllers report 0, so the sum should be 1, never the number of controllers. C — `ActiveControllerCount` is a live KRaft metric documented on the 4.3 monitoring page under `kafka.controller:type=KafkaController`; `ControllerStats` is a different MBean type holding election metrics, not a replacement. D — a sum of 2 would suggest something pathological; a sum of 0 does not indicate split brain.
- 🧠 **Key point / trap:** when a cluster-wide metric reads zero, ask "is the thing absent, or is the **scrape** absent?" first. Dedicated controller nodes are the most commonly forgotten scrape target in a KRaft deployment.
- 📎 Source: `../../study-plan/week-07/resources/kafka-monitoring-metrics.md` and `../../study-plan/VALIDATION.md` (exporter not attached to controller nodes).

### Question 26 — Answer: **B**

- **Why correct:** a tombstone is a record with a `null` value. The cleaner uses it to remove every earlier record for that key, and then removes the tombstone itself once `delete.retention.ms` has elapsed since it was compacted — 86,400,000 ms (24 hours) by default. A consumer that bootstraps from offset 0 and takes three days to reach the head can therefore pass the point where a tombstone used to be and never see it, rebuilding state that still contains a deleted key. Raising `delete.retention.ms` on the topic is a dynamic override and costs only a little extra log.
- **Why the others are wrong:** A — the head of the log is exactly where *every* record is still present, tombstones included; `isolation.level` concerns transactional reads and is unrelated. C — `min.cleanable.dirty.ratio` decides *when* the cleaner picks a log up, not whether deletions are applied; lowering it makes the cleaner run more often, which removes tombstones **sooner** and makes the problem worse. D — `compact,delete` adds age-based segment deletion on top of compaction; it deletes more, faster, and again makes the race harder to win.
- 🧠 **Key point / trap:** the operational rule is `delete.retention.ms` **>** worst-case full-bootstrap time of any consumer that rebuilds state from offset 0. Write that number down somewhere the storage team can see it.
- 📎 Source: `../../study-plan/week-02/resources/kafka-design-log-compaction.md`

### Question 27 — Answer: **B, D**

- **Why correct:** B — a principal in `super.users` bypasses the authorizer altogether. The Deny rule is stored and listed correctly, it simply is never consulted for a super user. D — consequently the only remedy is to take the principal out of `super.users` on every broker **and** every controller; no ACL can constrain a super user, and no ordering of Allow/Deny changes that.
- **Why the others are wrong:** A — "Deny beats Allow" is true in general, and ACL application really is eventually consistent, but neither applies here: the rule was never evaluated. This is the tempting half-truth in the question. C — `super.users` is separated by **semicolons**, so `User:ops-admin;User:mirror-maker` is correct as written; the comma claim is inverted. E — `super.users` does not support wildcards, and `User` is case-sensitive.
- 🧠 **Key point / trap:** treat `super.users` as a break-glass list, audit it, and never put a routine service account on it. The failure mode is silent: the ACL exists, `--list` shows it, and it does nothing.
- 📎 Source: `../../study-plan/week-05/resources/kafka-authorization-acls.md`

### Question 28 — Answer: **C**

- **Why correct:** `connector.client.config.override.policy` defaults to **`All`** in Apache Kafka 4.3. It was `None` until Kafka 3.0, when KIP-722 flipped it, and the Confluent *Connect Security* page still prints "None (default)". This is a genuine disagreement between two official sources, and for an Apache-anchored exam the Apache value is the one to hold. From 4.2 the documentation recommends `Allowlist`, which becomes the default in 5.0; the valid values are `None`, `Principal`, `All` and `Allowlist`.
- **Why the others are wrong:** A — the policy applies identically in standalone and distributed mode. B — the policy governs both `producer.override.*` and `consumer.override.*` (plus `admin.override.*`); there is no per-prefix exemption. D — the policy is evaluated whenever a connector configuration is validated, including on `PUT .../config` for an existing connector; nothing is grandfathered.
- 🧠 **Key point / trap:** when two official sources disagree, note *which* source your exam is anchored to. Here the practical consequence is real: on a stock Apache 4.3 worker, a connector can override its own client credentials unless you tighten the policy deliberately.
- 📎 Source: `../../study-plan/week-06/resources/connect-worker-configs-4.3.md` and `../../study-plan/VALIDATION.md` (mục *Hai nguồn chính thức lệch nhau*).

### Question 29 — Answer: **D**

- **Why correct:** `offsets.topic.replication.factor` defaults to **3**. On a two-broker cluster the controller cannot satisfy that, so `__consumer_offsets` is never created and no group coordinator can be assigned — which is exactly what both messages say. For a two-broker staging cluster the fix is to set the property to 2 in the broker configuration (`transaction.state.log.replication.factor`, default 3, and `transaction.state.log.min.isr`, default 2, need the same treatment if transactions are used). The critical follow-on fact: the property is consulted **only when the topic is created**, so once `__consumer_offsets` exists, changing it achieves nothing and the replication factor must be raised with `kafka-reassign-partitions.sh`.
- **Why the others are wrong:** A — `default.replication.factor` (default 1) applies to ordinary auto-created topics, not to the internal offsets topic, which has its own setting. B — `min.insync.replicas` defaults to 1 and is a write-time gate, not a creation-time constraint; the broker message names the offsets setting explicitly. C — the group coordinator is a **broker** that leads a partition of `__consumer_offsets`; it has nothing to do with the controller quorum, and a two-broker cluster is perfectly capable of hosting coordinators.
- 🧠 **Key point / trap:** audit the replication factor of `__consumer_offsets`, `__transaction_state` and the Connect internal topics after any cluster resize. A sandbox that grows into production carries its RF=1 internal topics with it, and nothing recreates them.
- 📎 Source: `../../study-plan/week-03/resources/kafka-broker-configs-replication-throughput.md` and `../../CCAAK-STUDY-PLAN.md` §6.

### Question 30 — Answer: **A**

- **Why correct:** Kafka 4.3 raised the minimum permitted value of `segment.bytes` from 14 bytes to **1 MiB**. Test harnesses that forced constant segment rolls by setting a tiny segment size now fail validation at topic creation. The supported way to make segments roll quickly is time-based: `segment.ms` (with `segment.jitter.ms` if you want to avoid a thundering herd of simultaneous rolls).
- **Why the others are wrong:** B — cordoning (KIP-1066) stops the controller placing **new partitions** on a log directory; it has no bearing on configuration validation. C — there is no rule tying `segment.bytes` to `message.max.bytes`, and 1,048,576 is not 1,048,588; the error text names a flat minimum. D — `remote.log.storage.system.enable` still defaults to false and must be turned on deliberately, and tiered storage imposes no such segment minimum.
- 🧠 **Key point / trap:** this is a pure version trap with no symptom to reason from — you either know the 4.3 change or you do not. The same release also moved `group.coordinator.background.threads` from 1 to 2 and added `remote.log.metadata.topic.min.isr` with a default of 2.
- 📎 Source: `../../CCAAK-STUDY-PLAN.md` §6 (*Thay đổi đáng nhớ của Kafka 4.1 → 4.3*) and `../../study-plan/week-07/resources/kafka-upgrade-notable-changes.md`

### Question 31 — Answer: **B**

- **Why correct:** follower fetching (KIP-392) needs three pieces and all of them are required. The brokers must know their own topology (`broker.rack`, a read-only setting, so it takes a restart), the brokers must be told to use a rack-aware selector (`replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector`), and the consumers must declare their location (`client.rack`). No guarantee is weakened: a follower only serves reads up to the **high watermark**, so a consumer can never see uncommitted records, and producers continue to write to the leader.
- **Why the others are wrong:** A — `client.rack` alone does nothing; without a replica selector configured on the brokers, every fetch still goes to the leader, and brokers do not infer rack membership from client addresses. C — one Cluster Link per AZ is the "correct but wildly disproportionate" option: it duplicates storage three times and adds an entirely separate replication mechanism to solve a read-routing problem. D — unclean leader election has nothing to do with locality and trades away data.
- 🧠 **Key point / trap:** cross-AZ cost questions have exactly one answer in Apache Kafka, and it is follower fetching. Remember that `broker.rack` is read-only — enabling this on a live cluster means a rolling restart, which belongs in the change plan.
- 📎 Source: `../../study-plan/week-04/resources/kip-392-follower-fetching.md`

### Question 32 — Answer: **A, B**

- **Why correct:** the 40 under-replicated partitions were each down to two in-sync replicas, which is exactly what `min.insync.replicas=2` requires — so nothing was ever rejected. A — `acks=all` means "all **in-sync** replicas", and the gate is `min.insync.replicas`. With min.isr=2 the leader plus one follower is sufficient; the third replica may be lagging without blocking writes. B — RF=3 with min.isr=2 tolerates the loss of exactly one replica, which is the whole reason that pairing is the production standard.
- **Why the others are wrong:** C — `min.insync.replicas` is only consulted for `acks=all` (`acks=-1`) writes; a producer using `acks=1` is acknowledged by the leader alone and is entirely unaffected, which is why lowering min.isr during an incident helps only some producers while quietly weakening durability for everyone. D — `NotEnoughReplicasException` is **retriable**: the producer keeps retrying in the background until `delivery.timeout.ms` expires, so the application sees a timeout much later rather than an immediate failure. E — `acks=all` guarantees the record is on every in-sync replica at acknowledgement time; losing all three brokers permanently loses the data.
- 🧠 **Key point / trap:** the matrix to memorise is `replication.factor − min.insync.replicas` = number of replicas you can lose while still accepting `acks=all` writes. Everything else on this topic follows from that one subtraction.
- 📎 Source: `../../study-plan/week-03/resources/kafka-design-replication.md` and `../../study-plan/week-01/resources/kafka-design-replication-isr.md`

### Question 33 — Answer: **C**

- **Why correct:** for a listener that already exists, keystore and truststore are **per-broker dynamic** configurations, so they can be swapped with `kafka-configs.sh --entity-type brokers --entity-name <id>` with no restart — that is the whole answer to "rotate certificates with zero downtime". The order matters because Kafka validates trust on the inter-broker listener in two opposite directions: a new **truststore** is accepted only if it still trusts the **current** keystore, and a new **keystore** is accepted only if the **current** truststore already trusts it. Only "new CA into the truststore first, new certificate second" satisfies both checks.
- **Why the others are wrong:** A — keystore first fails the validation (the current truststore does not yet trust the new CA) or, on a non-inter-broker listener where no validation happens, instantly breaks every client. B — a restart is not required; this is the classic outdated answer. D — there is no ZooKeeper and no `/config/brokers/<id>` znode in 4.x.
- 🧠 **Key point / trap:** remember "**truststore first, keystore second**" as a single phrase. A useful practical shortcut: keep the same store password for the new keystore and you only need to change `location`, avoiding the `password.encoder.secret` machinery entirely.
- 📎 Source: `../../study-plan/week-05/resources/confluent-dynamic-config-cert-rotation.md`

### Question 34 — Answer: **C, E**

- **Why correct:** the three metrics answer three different questions. `UnderReplicatedPartitions = 214` says some partitions have fewer replicas in sync than their replication factor. `OfflinePartitionsCount = 0` says every one of them still has a **leader** (C), so producers and consumers are being served. `UnderMinIsrPartitionCount = 0` says no partition has dropped below its `min.insync.replicas`, so `acks=all` writes are still being accepted (E). Together they describe a degraded but functioning cluster — the normal picture while one broker is down in an RF=3 / min.isr=2 design.
- **Why the others are wrong:** A — the combination is not only possible, it is the expected one; URP counts "fewer than RF", UnderMinIsr counts "fewer than min.isr", and with RF=3/min.isr=2 the first crosses long before the second. B — the 214 figure is current, not stale; the two metrics simply measure different thresholds. D — enabling unclean leader election here would be actively harmful: nothing is offline, no election is needed, and the only thing it can achieve is data loss the next time a partition does go offline.
- 🧠 **Key point / trap:** read the three red-line metrics as a ladder. URP > 0 means "degraded, investigate". UnderMinIsr > 0 means "`acks=all` producers are being rejected right now". OfflinePartitions > 0 means "no leader at all, consumers are blocked too". The urgency of your response should follow that ladder, not the raw number.
- 📎 Source: `../../study-plan/week-07/resources/kafka-monitoring-metrics.md` and `../../CCAAK-STUDY-PLAN.md` §7.

### Question 35 — Answer: **A, D**

- **Why correct:** A — `__cluster_metadata` is a single-partition log replicated by the Raft protocol among the controller **voters**; that single partition is what makes a total order over all metadata records possible. D — brokers replicate the same log as **observers**: they fetch and apply every record so they can serve clients from local metadata, but they do not vote and are never candidates for controller.
- **Why the others are wrong:** B — it is not an ordinary topic and `offsets.topic.replication.factor` applies to `__consumer_offsets`; the metadata log's redundancy comes from the size of the controller quorum. C — `metadata.log.dir` defaults to **`null`**, which means the first directory listed in `log.dirs`; there is no `/tmp/kraft-metadata` default (see question 49). E — the metadata log is trimmed by **snapshots**, bounded by `metadata.max.retention.bytes` (100 MiB) and `metadata.max.retention.ms` (7 days), not by the log cleaner.
- 🧠 **Key point / trap:** the two words that resolve most KRaft questions are **voter** and **observer**. Controllers vote; brokers observe. Everything about election, quorum sizing and failover follows from that split.
- 📎 Source: `../../study-plan/week-01/resources/kraft-operations-production.md` and `../../study-plan/week-04/resources/kafka-kraft-controller-topology.md`

### Question 36 — Answer: **B, C**

- **Why correct:** B — `scheduled.rebalance.max.delay.ms` defaults to **300,000 ms**. When a worker leaves, the leader keeps its tasks unassigned for up to that long on the assumption that the worker is merely restarting; without it, every worker restart would cost two rebalances instead of none. C — lowering the value shortens the outage for a genuinely dead worker, at the price of more churn for ordinary restarts. Tuning it is a straight trade between recovery time and rebalance noise.
- **Why the others are wrong:** A — the Connect worker group's `session.timeout.ms` defaults to **10,000 ms**, not 45,000; the consumer default was raised to 45,000 but the worker group kept its own timings (`heartbeat.interval.ms` 3,000, `rebalance.timeout.ms` 60,000). Copying consumer numbers onto a worker is a common and confusing mistake. D — `connect.protocol` defaults to `sessioned`, which means **incremental cooperative** rebalancing (KIP-415); unaffected tasks keep running. E — restarting surviving workers to force reassignment is the disproportionate option and causes exactly the rebalance storm the delay exists to prevent.
- 🧠 **Key point / trap:** "tasks did not move for five minutes" is not a bug report, it is the default. Know the number, and know that Connect's group timings are not the consumer's.
- 📎 Source: `../../study-plan/week-06/resources/connect-worker-configs-4.3.md` and `../../study-plan/week-06/resources/connect-cluster-rebalance-kip415-kip891.md`

### Question 37 — Answer: **D**

- **Why correct:** `num.recovery.threads.per.data.dir` changed from **1 to 2** in Kafka 4.0, so the recalled figure is a version out of date. It is a **cluster-wide dynamic** configuration, so `kafka-configs.sh --entity-type brokers --entity-default --alter --add-config num.recovery.threads.per.data.dir=8` applies it across the fleet with no file edits — but since the threads only run during startup recovery, the change has no effect until the next restart. Setting it now, cluster-wide, is what makes the *next* incident shorter.
- **Why the others are wrong:** A — it is not read-only; treating it as a static setting means editing eight files instead of running one command, and means the rest of the cluster stays slow. B — `num.io.threads` is the request-handler pool serving clients; it does no log recovery. C — `background.threads` is a general housekeeping pool and is likewise not the recovery pool; raising it to 32 would add contention for no benefit.
- 🧠 **Key point / trap:** two facts are tested at once — the 4.0 default change, and the distinction between "dynamic" and "takes effect immediately". A dynamic configuration that is only read at startup is still dynamic; you just have to wait for the restart.
- 📎 Source: `../../study-plan/week-02/resources/kafka-broker-configs-storage-threads.md` and `../../study-plan/week-07/resources/kafka-upgrade-notable-changes.md`

### Question 38 — Answer: **A**

- **Why correct:** in Kafka 4.3 `controller.quorum.auto.join.enable` defaults to **false**, so a freshly started controller node deliberately joins as an **observer** and waits for an operator to promote it. That is exactly what the output shows: 3004 appears in `CurrentObservers`, not `CurrentVoters`, while `MaxFollowerLag: 0` confirms it has caught up. With `kraft.version=1` (dynamic quorum) the promotion is a single online command, `kafka-metadata-quorum.sh ... add-controller`, run on the new node — no restart of anything else.
- **Why the others are wrong:** B — that is the **static quorum** procedure and only applies when `kraft.version=0`; here the cluster is on 1, and a full cluster restart is the opposite of "fewest changes". C — there are no ephemeral nodes in KRaft, and restarting the node will simply make it an observer again. D — `controller.quorum.fetch.timeout.ms` governs when a voter decides the leader is gone and stands for election; it plays no part in membership, and the lag figures show nothing is timing out.
- 🧠 **Key point / trap:** read `CurrentVoters` versus `CurrentObservers` before anything else in that output. A node that is healthy, caught up and still an observer is almost always waiting for `add-controller` — and the default that makes that necessary changed recently enough that most material does not mention it.
- 📎 Source: `../../CCAAK-STUDY-PLAN.md` §6 (*Thay đổi đáng nhớ của Kafka 4.1 → 4.3*) and `../../study-plan/week-01/resources/kraft-operations-production.md`

### Question 39 — Answer: **B**

- **Why correct:** the documented behaviour is that when a resource has **no** matching ACL at all, `allow.everyone.if.no.acl.found=true` lets everyone through; the moment that resource has even one ACL, ordinary evaluation resumes and anything not explicitly allowed is denied. So adding a single Allow for `User:reader` flipped `orders` from "open to all" to "open to reader only", while the fifty untouched topics stayed open because they still have no ACLs. The correct end state is `allow.everyone.if.no.acl.found=false` plus explicit grants, which removes the cliff edge entirely.
- **Why the others are wrong:** A — Kafka never creates implicit Deny rules; the denial comes from the default-deny fallback, and adding an Allow per principal would work but treats the symptom. C — the flag applies to every resource type, not just `Cluster`. D — the propagation delay is real but lasts milliseconds (see question 4), not indefinitely, and it would not explain a consistent, permanent change in behaviour.
- 🧠 **Key point / trap:** `allow.everyone.if.no.acl.found=true` makes authorization behave discontinuously: each topic is wide open until its first ACL, then abruptly locked down. That cliff is why the setting defaults to `false` and why inheriting it from an older cluster is dangerous.
- 📎 Source: `../../study-plan/week-05/resources/kafka-authorization-acls.md`

### Question 40 — Answer: **C**

- **Why correct:** rack-aware placement spreads a partition's replicas across `min(#racks, replication.factor)` racks. With two racks and RF=3 that is two racks, so each partition gets at least one replica in each AZ — but the third replica has to go somewhere, and it lands in one AZ or the other. Lose the AZ that holds two of the three, and the partition is down to a single replica: below `min.insync.replicas=2`, so `acks=all` writes stop. The uneven 5/4 broker split also skews replica distribution, because Kafka's guidance is an equal number of brokers per rack.
- **Why the others are wrong:** A — "exactly one replica per rack" is only achievable when the number of racks is at least the replication factor; with two racks and RF=3 it is arithmetically impossible. B — `broker.rack` is read-only and requires a restart, and changing a label never triggers a re-spread of existing partitions; that needs a reassignment. D — rack awareness is a **placement** mechanism; it constrains where replicas are created, and leader election follows from the ISR, not from rack labels.
- 🧠 **Key point / trap:** two availability zones plus RF=3 is a trap architecture. It looks redundant and passes a casual review, but losing one zone leaves partitions below min.isr. Three zones is the answer; if only two exist, the durability plan has to say so explicitly.
- 📎 Source: `../../study-plan/week-04/resources/kafka-ops-expanding-reassignment.md` (rack awareness) and `../../study-plan/week-04/resources/kafka-datacenters.md`

### Question 41 — Answer: **A**

- **Why correct:** 1-Y · 2-W · 3-Z · 4-X. Plain `delete` discards **closed** segments once they age past the retention window and never touches the active segment. Plain `compact` keeps at least the latest value per key indefinitely — the log never shrinks below one record per key. `compact,delete` does both: the latest value per key is kept, and whole segments still age out of the retention window. A `null` value is a tombstone: it deletes the key, and the marker itself is cleaned up `delete.retention.ms` after it is compacted.
- **Why the others are wrong:** B swaps plain delete and plain compact (`1-W`, `2-Y`), which inverts the two most basic policies. C swaps `compact` and `compact,delete` (`2-Z`, `3-W`) — plausible-looking, but the combined policy is the one that also drops old segments. D makes plain `delete` behave like the combined policy and vice versa.
- 🧠 **Key point / trap:** the guarantee people get wrong is that compaction leaves exactly one record per key. It does not: the **head** of the log is never compacted, so recent duplicates are always present. See question 53.
- 📎 Source: `../../study-plan/week-02/resources/kafka-design-log-compaction.md` and `../../study-plan/week-02/resources/kafka-topic-configs-overrides.md`

### Question 42 — Answer: **D**

- **Why correct:** the monitoring documentation states that `UncleanLeaderElectionsPerSec` should be **0**. Anything above zero means a partition elected a leader that was not in the ISR, which can only happen when `unclean.leader.election.enable` is `true` — either as a cluster-wide default or as a topic override — and it means acknowledged records were discarded. The absence of reported outages is not reassuring; it is the point, because unclean elections trade data for availability and are therefore invisible to availability monitoring. Both levels are dynamic, so reverting to `false` needs no restart.
- **Why the others are wrong:** A — preferred leader elections are counted separately; this metric counts only unclean ones, and `auto.leader.rebalance.enable` never produces them. B — ELR elections are clean by construction: the strict-min-ISR rule guarantees an ELR member holds every committed record, which is the entire reason the feature exists. C — controller failovers are not partition leader elections and are not counted here.
- 🧠 **Key point / trap:** the four metrics the documentation says must be exactly 0 are `UnderReplicatedPartitions`, `UnderMinIsrPartitionCount`, `OfflinePartitionsCount` and `UncleanLeaderElectionsPerSec`. The last one is the only one that stays at 0 during an outage and then tells you, afterwards, that you lost data.
- 📎 Source: `../../study-plan/week-07/resources/kafka-monitoring-metrics.md`

### Question 43 — Answer: **A, D**

- **Why correct:** A — a follower is evicted from the ISR only when it fails to catch up within `replica.lag.time.max.ms` (30,000 ms). Thirty seconds is a long time, so repeated eviction means the broker genuinely stalls: long GC pauses, slow disks or a saturated network link are the three usual causes, and all three are visible outside Kafka. D — the documentation warns that `replica.fetch.wait.max.ms` (500 ms) must always stay below `replica.lag.time.max.ms`, precisely because an inverted relationship makes low-throughput topics shrink and expand their ISR continuously.
- **Why the others are wrong:** B — raising `replica.lag.time.max.ms` hides the flapping by keeping a genuinely lagging replica nominally in sync, which weakens the durability guarantee that `acks=all` relies on; it is also read-only and needs a restart. C — unclean leader election is unrelated to ISR churn, costs data, and nothing here is offline. E — more partitions means more replication work on the same struggling broker; it is the one-way, make-it-worse option.
- 🧠 **Key point / trap:** the reflex for ISR flapping is "look outside Kafka first" — GC logs, disk latency, NIC errors. Adjusting `replica.lag.time.max.ms` to stop the alerting is treating the thermometer.
- 📎 Source: `../../study-plan/week-03/resources/kafka-broker-configs-replication-throughput.md` and `../../CCAAK-STUDY-PLAN.md` §7.

### Question 44 — Answer: **B, C**

- **Why correct:** B — `replica.fetch.response.max.bytes` defaults to **10,485,760 (10 MiB)**. The 1 MiB figure that third-party material keeps printing belongs to `replica.fetch.max.bytes`, which is the **per-partition** limit. C — the documentation is explicit that neither value is an absolute maximum: if the first record batch of the first non-empty partition exceeds the limit, it is returned anyway, specifically so replication cannot deadlock on a large batch.
- **Why the others are wrong:** A — this is the wrong figure the reviewer quoted, and the whole point of the question. D — both are **read-only** and need a broker restart to change, along with `replica.lag.time.max.ms`, `queued.max.requests` and the socket buffer settings. (`num.replica.fetchers`, by contrast, *is* cluster-wide dynamic — a useful pairing to remember.) E — `socket.request.max.bytes` defaults to 104,857,600 (100 MiB).
- 🧠 **Key point / trap:** the real ceiling on record batch size is `message.max.bytes` at the broker or `max.message.bytes` at the topic. The replica fetch settings are throughput tuning, not correctness limits, and misreading them as hard caps produces a lot of unnecessary configuration changes.
- 📎 Source: `../../study-plan/week-03/resources/kafka-broker-configs-replication-throughput.md` and `../../CCAAK-STUDY-PLAN.md` §6.

### Question 45 — Answer: **A, B, C**

- **Why correct:** A — the dead letter queue is implemented in the sink task's error-handling path, so it exists only for **sink** connectors; configuring it on a source connector is silently inert. B — `errors.tolerance=all` tells the task to keep going past a bad record, and without `errors.deadletterqueue.topic.name` the record is simply dropped, with nothing but a log line to show for it — which is precisely how a record disappears for three days without a task ever failing. C — `errors.deadletterqueue.topic.replication.factor` defaults to **3**, which is correct for production and fatal on a single-broker lab, where it must be lowered to 1 before the DLQ topic can be created.
- **Why the others are wrong:** D — the DLQ captures failures from the whole conversion and transformation chain, including SMTs, not just converters. E — `errors.tolerance=none` is the default and means "fail the task on the first bad record"; it is the opposite of routing to a DLQ, and it is why a DLQ without `errors.tolerance=all` never receives anything.
- 🧠 **Key point / trap:** a DLQ needs **two** settings to work — `errors.tolerance=all` **and** a DLQ topic name. One without the other gives you either a dead task or silent data loss, which are the two failure modes this feature exists to avoid.
- 📎 Source: `../../study-plan/week-06/resources/connect-error-handling-dlq-kip298.md`

### Question 46 — Answer: **A**

- **Why correct:** `kraft.version` is the feature flag that decides how quorum membership works. `FinalizedVersionLevel: 0` means a **static** quorum: every node, brokers included, carries the full voter list in `controller.quorum.voters`, and changing membership means editing that list everywhere and restarting. Level 1 (KIP-853) switches to a dynamic quorum, where nodes only need `controller.quorum.bootstrap.servers` and membership is changed online with `kafka-metadata-quorum.sh add-controller` / `remove-controller`. So the operator's answer is "not yet — upgrade the feature first".
- **Why the others are wrong:** B — the feature level is a real, finalized value, and dynamic membership is emphatically not automatic in 4.x. C — ELR and quorum membership are independent features; `eligible.leader.replicas.version=1` imposes no constraint here. D — `metadata.version` gates metadata record formats; quorum membership is gated by `kraft.version`, which is why they are separate features.
- 🧠 **Key point / trap:** `kafka-features.sh describe` is the fastest way to answer "what can I do to this cluster online?". Check `kraft.version` before planning any controller change — and note that this question and question 38 together describe the two halves of adding a controller: the feature must allow it, and the auto-join default must be handled.
- 📎 Source: `../../study-plan/week-01/resources/kip-500-kip-853-kraft-evolution.md` and `../../study-plan/week-01/resources/kraft-operations-production.md`

### Question 47 — Answer: **C, E**

- **Why correct:** C — `connections.max.reauth.ms` defaults to **0**, which disables SASL re-authentication. Authentication happens once, at connection setup; after that the connection is never re-checked, so deleting the credential stops *new* connections but leaves every established one running indefinitely. E — setting the value on the listener (per-mechanism if needed) forces clients to re-authenticate on that interval, and a client whose credential no longer exists then fails and is disconnected. That is what turns "revoked" into "actually cut off".
- **Why the others are wrong:** A — SCRAM credentials live in the metadata log; the delete takes effect cluster-wide within milliseconds and no restart is involved. B — there is no SCRAM entry in `kafka_server_jaas.conf`; that file holds **PLAIN** credentials and the broker's own login module. D — authorization is evaluated **per request**, so a Deny ACL takes effect on an open connection immediately. That makes a Deny ACL the correct emergency stop-gap while re-authentication is being enabled — which is exactly why this option is worth getting right rather than merely eliminating.
- 🧠 **Key point / trap:** revocation has two halves: remove the credential, and force existing sessions to re-prove themselves. A cluster that never set `connections.max.reauth.ms` has no answer to "cut this client off now" other than a Deny ACL or a restart.
- 📎 Source: `../../study-plan/week-05/resources/kafka-sasl-operations.md`

### Question 48 — Answer: **C**

- **Why correct:** 1-W · 2-Y · 3-Z · 4-X. MM2 with `DefaultReplicationPolicy` renames target topics `{source}.{topic}` to break replication loops, and its offsets never line up with the source, so they must be translated. Cluster Linking replicates byte-for-byte with globally consistent offsets, keeps mirror topics read-only until promotion, and runs inside the broker with no Connect cluster. A stretch cluster is ordinary synchronous replication inside one cluster — RPO zero for `acks=all`, paid for with inter-AZ latency on every write. `MirrorCheckpointConnector` is the MM2 component that writes translated offset pairs into `{source}.checkpoints.internal`.
- **Why the others are wrong:** A swaps MM2 and Cluster Linking (`1-Y`, `2-W`) — the single distinction this matching exists to test. B puts the stretch cluster on the checkpoint description and vice versa (`3-X`, `4-Z`), confusing an architecture with a connector. D assigns the checkpoint description to MM2 as a whole and the renaming behaviour to `MirrorCheckpointConnector`, mixing up the three MM2 connectors — renaming is `MirrorSourceConnector`'s doing.
- 🧠 **Key point / trap:** memorise the three MM2 connectors by job: `MirrorSourceConnector` copies records, topic configuration and ACLs; `MirrorCheckpointConnector` translates consumer offsets; `MirrorHeartbeatConnector` emits liveness. Cluster Linking replaces all three with a broker feature — and is Confluent-only.
- 📎 Source: `../../study-plan/week-04/resources/confluent-cluster-linking.md` and `../../study-plan/week-04/resources/kafka-geo-replication-mm2.md`

### Question 49 — Answer: **B**

- **Why correct:** `metadata.log.dir` defaults to `null`, and a null value means "use the **first** directory listed in `log.dirs`". Every node therefore puts its metadata log on `/data/1` — the slowest and least reliable device in the machine. That hurts twice: metadata append latency is bounded by the worst disk, and losing `/data/1` costs the node its metadata log rather than merely some partitions, which is a far more serious failure. Giving `metadata.log.dir` its own fast, reliable device is the documented practice.
- **Why the others are wrong:** A — the metadata log is not striped or duplicated across `log.dirs`; it lives in exactly one directory per node. Redundancy comes from Raft replication across nodes. C — the default is the first entry, not the last. D — brokers absolutely do keep a local copy of the metadata log; they are observers of the quorum, and serving clients from stale metadata is a real failure mode tracked by `last-applied-record-lag-ms`.
- 🧠 **Key point / trap:** JBOD questions usually ask about partition placement. This one asks about the one directory in `log.dirs` that is special. If `log.dirs` is heterogeneous, the order of the list is a durability decision, not a formatting detail.
- 📎 Source: `../../CCAAK-STUDY-PLAN.md` §6 (KRaft) and `../../study-plan/week-01/resources/broker-configs-kraft-and-threads.md`

### Question 50 — Answer: **C**

- **Why correct:** Kafka 4.0 changed `message.timestamp.after.max.ms` from `Long.MAX_VALUE` to **one hour**. A broker now rejects any record whose `CreateTime` is more than an hour in the future, which is exactly the population that started failing: devices whose clocks run hours ahead. Raising `message.timestamp.after.max.ms` on this topic is targeted (one topic), reversible (a dynamic override) and buys time while the fleet's clocks are corrected — which is the actual fix.
- **Why the others are wrong:** A — the default timestamp type is unchanged and is `CreateTime`; nothing in the upgrade switched it. B — `message.timestamp.before.max.ms` is the mirror-image setting for timestamps in the **past**; these devices are ahead, not behind, so it is the near-miss distractor. D — retention has always worked from segment metadata for deletion decisions and has never rejected a record at append time.
- 🧠 **Key point / trap:** "we upgraded and a *subset* of producers started failing" almost always points to a validation default that got stricter. Switching the topic to `message.timestamp.type=LogAppendTime` also stops the rejections, but it throws away the producer's own timestamps — a real trade-off worth stating explicitly rather than applying by reflex.
- 📎 Source: `../../study-plan/week-07/resources/kafka-upgrade-notable-changes.md` and `../../CCAAK-STUDY-PLAN.md` §6.

### Question 51 — Answer: **D**

- **Why correct:** KIP-1100, shipped in Kafka **4.2**, standardised MBean names onto the `kafka.COMPONENT:type=...` form. Metrics that used to be published under `org.apache.kafka.server:type=...` are now under `kafka.server:type=...`. Exporter rules and dashboards written against the old names match nothing and produce empty panels while the broker is perfectly healthy — an observability gap that looks exactly like an outage and is routinely escalated as one.
- **Why the others are wrong:** A — `JMX_PORT` governs whether remote JMX is exposed at all; if it were unset, every panel in every row would be empty, not one row. B — `metrics.recording.level` is a Kafka Streams and client-metrics concept, not something the upgrade resets on brokers. C — the metrics were renamed, not removed; querying the new name returns data immediately.
- 🧠 **Key point / trap:** after any Kafka upgrade, diff the metric names your dashboards use against what the brokers actually publish. A renamed metric fails **silently**, and silence is the hardest failure mode to notice.
- 📎 Source: `../../study-plan/week-07/resources/kafka-upgrade-notable-changes.md`

### Question 52 — Answer: **A**

- **Why correct:** KIP-875 added connector offset management to the REST API in two instalments: `GET /connectors/{n}/offsets`, the `STOPPED` state and `PUT /connectors/{n}/stop` arrived in **3.5**; `PATCH` and `DELETE /offsets` arrived in **3.6**. Both mutating endpoints require the connector to be `STOPPED`, which is a genuinely different state from `PAUSED`: stopping destroys the tasks while retaining the configuration and the offsets, whereas pausing keeps the tasks alive and still owning their offsets. Stop → delete offsets → resume is therefore the supported sequence, and it preserves the name, the configuration and the DLQ.
- **Why the others are wrong:** B — `PAUSED` is not sufficient; the offsets endpoints reject the request. C — resetting the sink's consumer group by hand is the pre-3.5 workaround, and `kafka-consumer-groups.sh --reset-offsets` refuses to act on a group with active members, which a running connector certainly has. D — recreating under a new name works only because the new name gets a new consumer group; it abandons the DLQ, the status history and the original name, which the question explicitly requires keeping.
- 🧠 **Key point / trap:** `PAUSED` versus `STOPPED` is a real exam distinction. Pause = stop polling, keep the tasks. Stop = destroy the tasks, keep the configuration. Only the second unlocks offset management.
- 📎 Source: `../../study-plan/week-06/resources/connect-offset-management-kip875.md`

### Question 53 — Answer: **B, D**

- **Why correct:** the bug report is wrong, and option A explains why: the **head** of a compacted log is never cleaned, so two values for the same key near the end of the log are normal. The documentation lists four guarantees, and these are two of them. B — a message's offset never changes; compaction only removes records, so an offset is a permanent identifier for a position in the log (which is also why a compacted log has gaps in its offsets). D — a consumer reading from the start of the log sees at least the final state of every record, in the order the records were written; compaction never reorders anything.
- **Why the others are wrong:** A — this is the guarantee everyone assumes and Kafka does **not** make. The **head** of the log is never compacted, so recent records include duplicates for the same key; only the tail is deduplicated. C — compaction removes records in place and never reorders or regroups them; ordering preservation is one of the four stated guarantees, and grouping by key would violate it. E — the cleaner works only on **closed** segments; the active segment is never touched, and `min.cleanable.dirty.ratio` (0.5) is merely the threshold at which a log becomes eligible for cleaning.
- 🧠 **Key point / trap:** when a question asks what compaction guarantees, the trap answer is always "one record per key". Say instead: ordering preserved, offsets stable, head fully intact, final state visible from the beginning of the log.
- 📎 Source: `../../study-plan/week-02/resources/kafka-design-log-compaction.md`

### Question 54 — Answer: **B**

- **Why correct:** `ssl.endpoint.identification.algorithm` has defaulted to `https` — that is, hostname verification **enabled** — since Kafka 2.0, so a runbook telling you to set it is describing a no-op on any modern client. The handshake failure names the real problem: the certificate has no SAN entry, and modern TLS stacks ignore `CN` for hostname matching. The fix is to re-issue broker certificates with SAN entries for every hostname that appears in `advertised.listeners`. The older applications are not evidence of a working certificate; they are evidence of an old configuration that disables verification.
- **Why the others are wrong:** A — client certificates are about authenticating the client to the broker; they have nothing to do with the client verifying the broker's hostname. C — `ssl.client.auth` controls mutual TLS and does not change what the broker presents or how the client validates it. D — trusting the CA is necessary but not sufficient; hostname verification is a separate check that runs after chain validation, which is precisely why this failure survives a correct truststore.
- 🧠 **Key point / trap:** keep two facts apart. Hostname verification on by default since 2.0 is Kafka behaviour. Java 9+ defaulting to PKCS12 while Kafka's `ssl.keystore.type` remains `JKS` is a different fact about store formats — the Apache documentation specifies PKCS12 explicitly in every `keytool` example precisely so the guides do not depend on the Java version.
- 📎 Source: `../../study-plan/week-05/resources/kafka-ssl-operations.md` and `../../study-plan/VALIDATION.md`

### Question 55 — Answer: **C**

- **Why correct:** `auto.create.topics.enable` defaults to **true**, so any producer that writes to a non-existent topic creates it. The shape of the resulting topic comes from `num.partitions` (default **1**) and `default.replication.factor` (default **1**) — which is exactly why the junk topics have one partition and one replica, and why a single broker failure would take them offline permanently. The remedy is to disable auto-creation in production and route topic creation through a governed process. Note the source disagreement flagged in the answer: Apache 4.3's generated configuration lists this setting as `read-only`, while Confluent's broker reference lists it as `cluster-wide`; plan for a rolling restart rather than betting on a dynamic change.
- **Why the others are wrong:** A — `offsets.topic.replication.factor` (3) applies only to `__consumer_offsets`; ordinary auto-created topics use `default.replication.factor`. B — `delete.topic.enable` (default true) controls whether topics may be **deleted**; turning it off would make the junk harder to clean up, not prevent it. D — auto-created topics inherit the broker's `min.insync.replicas` (default 1), and with RF=1 that is meaningless anyway; a `CreateTopicPolicy` is a genuine control, but in KRaft it must be loaded on the **controller**, not the broker, which is a second trap in the same option.
- 🧠 **Key point / trap:** "topics with typo names, one partition, RF 1" is a fingerprint. It says auto-creation is on, and it tells you what the cluster's `num.partitions` and `default.replication.factor` are without looking them up.
- 📎 Source: `../../study-plan/week-02/resources/kafka-topic-configs-overrides.md`, `../../CCAAK-STUDY-PLAN.md` §6 and `../../study-plan/VALIDATION.md` (mục *Hai nguồn chính thức lệch nhau*).

### Question 56 — Answer: **D**

- **Why correct:** enabling Eligible Leader Replicas changes the rules around `min.insync.replicas`. The **broker-level** setting is removed and can no longer be modified; a **cluster-level** value is added automatically if one does not exist (taken from the active controller's static value) and cannot be deleted. Topic-level overrides remain available. The operator should therefore use `--entity-type brokers --entity-default` or a topic override — and should know the side effect: updating the cluster-level value, **even to the same number**, wipes the entire ELR state, and changing a topic's value wipes that topic's ELR state.
- **Why the others are wrong:** A — broker-level `min.insync.replicas` has existed for many versions and is still perfectly valid on a cluster without ELR; it is the ELR feature that removes it. B — enabling ELR does not freeze configuration, and a restart changes nothing about this rejection. C — the request is routed to the controller by the broker regardless of which bootstrap flag you use; `--bootstrap-controller` would be refused for the same reason.
- 🧠 **Key point / trap:** this is the most commonly hit ELR upgrade trap. ELR is opt-in on 4.0 (`eligible.leader.replicas.version=1`) and on by **default for new clusters from 4.1** — but an upgraded cluster does not turn it on by itself. The day someone does enable it, every broker-level `min.insync.replicas` in the configuration management repository becomes invalid.
- 📎 Source: `../../study-plan/week-03/resources/kafka-eligible-leader-replicas.md`

### Question 57 — Answer: **A, C**

- **Why correct:** A — in combined mode the controller and the broker share a process, so they cannot be rolled, patched or scaled independently; that is the operational objection the Apache documentation raises first. C — the same sharing means the controller is exposed to the broker's page-cache pressure, garbage collection and disk I/O, so data-plane load degrades metadata handling. Apache says combined servers are "simpler to operate for small use cases like a development environment" but that the controller "will be less isolated from the rest of the system"; Confluent is blunter — "combined mode is for local experimentation only and is not supported by Confluent".
- **Why the others are wrong:** B — there is no broker-count limit attached to combined mode. D — combined mode is a **KRaft** arrangement; there is no ZooKeeper anywhere in 4.x, and this is the version trap in the set. E — `StandardAuthorizer` runs on brokers and controllers alike; in fact it must be configured on both (see question 58).
- 🧠 **Key point / trap:** the controller is cheap — roughly 5 GB of RAM and 5 GB of disk — so the usual objection to separating roles, cost, does not hold. Three dedicated controllers is the default production answer on CCAAK.
- 📎 Source: `../../study-plan/week-01/resources/kraft-operations-production.md`

### Question 58 — Answer: **A**

- **Why correct:** in KRaft a broker forwards administrative requests to the active controller wrapped in an `Envelope`, and the controller performs **two** authorization checks: one on the envelope, against the forwarding broker's principal, and one on the inner request, against the original client's principal. If the controllers have no `authorizer.class.name` configured, that second check never happens and forwarded administrative operations — creating topics, altering configurations, changing ACLs — are effectively unguarded. The documentation is explicit that the authorizer must be enabled on every broker **and** every controller.
- **Why the others are wrong:** B — controllers evaluate ACLs precisely because administrative requests terminate there, not on the broker. C — ACLs are stored once, in `__cluster_metadata`; there is no second store and `kafka-acls.sh --list` is consistent regardless of which node answers. D — an unconfigured `authorizer.class.name` means no authorization at all, not a fallback to super users only; that is the opposite of safe.
- 🧠 **Key point / trap:** anything security-related in KRaft is configured in two places. Authorizer on brokers **and** controllers; `CreateTopicPolicy` and `AlterConfigPolicy` JARs on the **controller** only, since that is where they now execute. Deploying a policy JAR to brokers and wondering why it does nothing is the sibling of this mistake.
- 📎 Source: `../../study-plan/week-05/resources/kafka-authorization-acls.md` and `../../study-plan/week-01/resources/zk2kraft-removed-configs-and-cli.md`

### Question 59 — Answer: **B**

- **Why correct:** `inter.broker.protocol.version` was removed along with ZooKeeper; in 4.x the equivalent concept is `metadata.version`, and it is managed through `kafka-features.sh`, never through a properties file. The procedure is: roll one node at a time onto the new binaries, waiting for `UnderReplicatedPartitions` to return to 0 before touching the next, and only once **every** node is on 4.3 run `kafka-features.sh upgrade --release-version 4.3` to finalize. Finalizing is deliberately last because it is one-way here: 4.3 changed metadata, so unlike 4.2 it cannot be downgraded afterwards.
- **Why the others are wrong:** A — there is no `metadata.version` property in `server.properties`; the feature is finalized by command, which is exactly the change that invalidates 2.x-era runbooks. C — finalizing first would enable metadata records that nodes still on 4.1 cannot read. D — nothing is raised automatically; the finalize step exists precisely so that the operator chooses the moment, having confirmed the whole fleet is ready.
- 🧠 **Key point / trap:** check downgradeability **before** finalizing. Among recent releases 4.2.0 can be downgraded, while 4.0.1, 4.1.0 and 4.3.0 changed metadata and cannot. Finalizing is the point of no return in an upgrade plan.
- 📎 Source: `../../study-plan/week-07/resources/kafka-upgrade-notable-changes.md` and `../../study-plan/week-04/resources/kafka-rolling-upgrade-kraft.md`

### Question 60 — Answer: **C**

- **Why correct:** declaring the clusters and their bootstrap servers is not enough — MirrorMaker 2 starts no connectors until a **flow** is enabled, and flows are off by default. Adding `primary->dr.enabled = true` is what creates the `MirrorSourceConnector`, `MirrorCheckpointConnector` and `MirrorHeartbeatConnector` for that direction. This is the single most common first-time MM2 mistake, and the log evidence matches it exactly: the process is healthy and no source connector was ever started.
- **Why the others are wrong:** A — `topics = .*` is the default and is perfectly valid. B — `DefaultReplicationPolicy` is the default and works fine; `IdentityReplicationPolicy` merely keeps the original topic names and is only appropriate for active/passive or migration, never active/active. D — MirrorMaker 1 and its `--whitelist` flag were **removed in Kafka 4.0**; MM2 is a set of Connect connectors and takes no such argument.
- 🧠 **Key point / trap:** when reviewing an MM2 configuration, look for the `->` line first. Everything else can be correct and nothing will move. Two further defaults worth remembering: `tasks.max` is 1 unless raised, and `groups.exclude` filters out `console-consumer-.*` and `connect-.*`, which is why lab consumer groups never appear on the target.
- 📎 Source: `../../study-plan/week-04/resources/kafka-geo-replication-mm2.md`

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (48+/60) | Đạt ngưỡng cá nhân ngay ở bài đo đường cơ sở. Nền cấu hình của bạn chắc. | Review **100%** câu sai, viết phân tích cho từng câu vào [`../../questions/`](../../questions/README.md). Kiểm bảng domain: một domain dưới ngưỡng riêng của nó vẫn phải ôn dù tổng đã đạt. Nghỉ ít nhất 1 ngày rồi làm **Mock 02** (*trực ca và chẩn đoán*). |
| **70–79%** (42–47/60) | Gần đạt. Với một bài nặng cấu hình, khoảng này thường nghĩa là bạn **nhớ khái niệm nhưng chưa thuộc số**. | Lấy **2 domain thấp nhất**, dành **3 ngày** đọc lại đúng tuần tương ứng ở bảng dưới, và học lại [`../../CCAAK-STUDY-PLAN.md`](../../CCAAK-STUDY-PLAN.md) **§6** cho tới khi đọc vo được. Làm lại mock này sau 7 ngày (không xem đáp án trong thời gian đó) rồi mới sang Mock 02. **Chưa đặt lịch thi.** |
| **< 70%** (≤ 41/60) | Chưa sẵn sàng. | **Van an toàn: lùi lịch thi ít nhất 2 tuần.** Quay lại Buổi A + B của 3 domain thấp nhất, **chạy lại lab** của các tuần đó (không chỉ đọc), và làm mini-mock cuối mỗi tuần đạt ≥ 80% trước khi thử full mock lần nữa. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / **dính bẫy version** / hết giờ), ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may **cũng tính là câu sai**.
> 📌 Mock này cố ý nặng **bẫy version**. Đếm riêng số câu bạn sai vì chọn phương án thuộc thế giới ZooKeeper hoặc một giá trị mặc định cũ — các câu **3, 4, 6, 17, 20, 28, 30, 33, 36, 37, 38, 44, 46, 50, 51, 54, 57, 59, 60**. Sai từ **4 câu trở lên** trong nhóm này nghĩa là bạn đang học lẫn tài liệu cũ: đọc lại [`../SOURCES-AND-VALIDATION.md`](../SOURCES-AND-VALIDATION.md) và [`../../study-plan/VALIDATION.md`](../../study-plan/VALIDATION.md) trước khi làm bất kỳ mock nào khác.

---

## 🔁 Bản đồ câu sai → tuần cần học lại

| Chủ đề của câu sai | Câu số | Tuần cần học lại |
| --- | --- | --- |
| KRaft: quorum, voter/observer, controller election, feature level | 3, 11, 21, 35, 38, 46, 57 | **Tuần 1** |
| Metadata log, `metadata.log.dir`, internal topic replication | 29, 49 | **Tuần 1** (+ Tuần 3 phần replication) |
| Config precedence, synonyms, dynamic vs restart | 1, 19, 37, 44, 55 | **Tuần 2** |
| Retention, segment roll, compaction, tombstone | 2, 26, 41, 53 | **Tuần 2** |
| `log.dirs` / JBOD, phân bố đĩa, `kafka-log-dirs.sh` | 15 | **Tuần 2** |
| Tiered storage và `local.retention.ms` | 23 | **Tuần 2** |
| Message size 3 tầng, replica fetch sizing | 13, 44 | **Tuần 2 + 3** |
| `acks` × `min.insync.replicas` × RF, ISR, ELR | 8, 24, 32, 43, 56 | **Tuần 3** |
| Quota: 4 loại, 8 mức ưu tiên, cơ chế throttle | 10, 14 | **Tuần 3** |
| Thread pool broker và startup recovery | 7, 37 | **Tuần 2 + 3** |
| Deployment: rack awareness, follower fetching, DR, rolling upgrade | 9, 31, 40, 48, 59 | **Tuần 4** |
| Reassignment, throttle, mở rộng cluster | 22 | **Tuần 4** |
| Security: TLS/SAN, xoay chứng chỉ, listener | 33, 54 | **Tuần 5** |
| Security: SASL, credential, thu hồi, re-authentication | 12, 47 | **Tuần 5** |
| Security: ACL, authorizer, super users, mặc định từ chối | 4, 20, 27, 39, 58 | **Tuần 5** |
| Connect: internal topic, task state, REST, offset, DLQ, rebalance | 5, 18, 28, 36, 45, 52 | **Tuần 6** |
| MirrorMaker 2 vận hành | 60 | **Tuần 6** (+ Tuần 4 phần DR) |
| Observability: metric đèn đỏ, lag/lead, JMX exporter, đổi tên MBean | 6, 16, 25, 34, 42, 51 | **Tuần 7** |
| Bẫy version thuần tuý (mặc định đã đổi ở 4.0 → 4.3) | 17, 30, 50 | **Tuần 7** (+ §6 của kế hoạch tổng) |

> 🔗 Sau khi ôn xong một tuần, làm lại **mini-mock cuối tuần đó** (`../../study-plan/week-NN/questions.md`) trước khi quay lại mock full-length.
