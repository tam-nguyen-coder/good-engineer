# ✅ Answers & Explanations — Week 7: Observability + Troubleshooting playbook

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

**Answer key:** 1-C · 2-D · 3-B · 4-C · 5-AB · 6-AB · 7-C · 8-B · 9-D · 10-C · 11-B · 12-AC · 13-A · 14-B · 15-C · 16-B · 17-D · 18-A · 19-BD · 20-B · 21-B · 22-AC · 23-A · 24-C · 25-A · 26-A · 27-AB · 28-A · 29-B · 30-A

---

## 📊 Chấm điểm theo domain

Đánh dấu từng câu đúng/sai rồi điền bảng. Hai domain của tuần này cộng lại là **25%** của đề thật — cụm lớn nhất.

| Domain | Tỉ trọng CCAAK | Câu số | Số đúng / Tổng | % | Ngưỡng |
| --- | --- | --- | --- | --- | --- |
| **OBS** — Observability | 10% | 1, 3, 4, 5, 15, 16, 17, 18, 19, 20, 21, 22, 23, 27, 28 | ___ / 15 | ___ | ≥ 73% (11/15) |
| **TROUBLE** — Troubleshooting | 15% | 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 24, 25, 26 | ___ / 13 | ___ | ≥ 77% (10/13) |
| **CONNECT** — ôn Tuần 6 | 12% | 29, 30 | ___ / 2 | ___ | 2/2 |
| **TỔNG** | — | 1–30 | ___ / 30 | ___ | **≥ 80%** |

> 📌 Dưới 70% ở **TROUBLE** là tín hiệu nghiêm trọng hơn dưới 70% ở OBS: domain này 15% và nó cũng là cách đề kiểm tra *"hành động đầu tiên"* trong mọi domain khác. Ôn lại **12 playbook** và **thang rẻ/đảo ngược được** trước khi chạy FULL MOCK #1.

---

### Question 1 — Answer: **C**

- **Why correct:** `UnderReplicatedPartitions > 0` means `|ISR| < |replicas|` — the data has fewer copies than configured, so **durability headroom** is reduced. It says nothing about availability. With `OfflinePartitionsCount = 0` every partition still has a leader, and with `UnderMinIsrPartitionCount = 0` every partition still has at least `min.insync.replicas = 2` replicas in sync, so `acks=all` writes are accepted. Clients notice nothing.
- **Why the others are wrong:** A — `NotEnoughReplicasException` is raised only when the ISR drops **below** `min.insync.replicas`, which is exactly what `UnderMinIsrPartitionCount = 0` rules out. B — "no leader" is what `OfflinePartitionsCount` measures, and it is 0. D — `acks=1` and `acks=0` writes are never affected by ISR size, and even `acks=all` is fine here.
- 🧠 **Key point / trap:** the single most reused distinction of this week — **URP = lost durability, still serving; UnderMinIsr = writes blocked; OfflinePartitions = nothing works.** With RF=3 / min.isr=2, losing one broker gives URP > 0 and UnderMinIsr = 0; losing two gives both.
- 📎 Source: `resources/kafka-monitoring-metrics.md` and `resources/confluent-broker-controller-metrics.md`.

### Question 2 — Answer: **D**

- **Why correct:** `min.insync.replicas` is the guarantee that an acknowledged write exists on more than one replica. Lowering it to 1 does not fix anything — it simply tells the cluster to accept writes that live on a single copy, precisely while the cluster has already proven it can lose brokers. The correct first action is to restore the failed brokers so the ISR recovers. `NotEnoughReplicasException` is the system **working as designed**: refusing to acknowledge a write it cannot make durable.
- **Why the others are wrong:** A — it is technically dynamic, but "can be raised again later" ignores that every write accepted in the meantime has no durability guarantee; this is the bait. B — raising `replica.lag.time.max.ms` does not bring dead brokers back; the replicas are not lagging, they are gone. C — unclean leader election elects a leader from **outside** the ISR and can discard acknowledged data; it also does not apply here, since the partitions still have leaders.
- 🧠 **Key point / trap:** any answer that fixes an availability symptom by weakening a durability setting is the "correct but overreaching" distractor CCAAK plants in almost every incident question. Rank actions by *cheap and reversible first*; lowering min.isr sits on the **most destructive** rung.
- 📎 Source: `resources/confluent-broker-controller-metrics.md` and [`README.md`](README.md) §A.3.

### Question 3 — Answer: **B**

- **Why correct:** the Apache docs state the normal value as *"only one broker in the cluster should have 1"*, and the KRaft controller table lists the valid values per node as **0 or 1**. With dedicated controllers, the brokers are never the active controller, so 0 on all three brokers is exactly what a healthy cluster looks like. The meaningful check is the **aggregated sum across the whole cluster**, which Confluent spells out: alert if it is anything other than 1.
- **Why the others are wrong:** A — split-brain would be a sum of 2 or more, not 0 on a subset of nodes. C — ZooKeeper was removed in Kafka 4.0; there is no controller znode and no `zookeeper.connect`. This is the version trap. D — the metric is emitted by every KRaft node, and the fact that admin operations succeed proves a leader exists.
- 🧠 **Key point / trap:** alert on `sum(ActiveControllerCount) != 1`, never on a single node's value. And in a Kafka 4.x question, any option mentioning znodes, `--zookeeper`, or `zookeeper.connect` can be eliminated on sight.
- 📎 Source: `resources/kafka-monitoring-metrics.md` (KRaft Controller Metrics) and `resources/confluent-broker-controller-metrics.md`.

### Question 4 — Answer: **C**

- **Why correct:** 790 ms of the 840 ms total is spent in `RequestQueueTimeMs`, which is the time a request **waits for a request-handler (I/O) thread**. The matching signal is `RequestHandlerAvgIdlePercent = 0.06`, far below the documented "ideally > 0.3". CPU at 45% shows the machine still has headroom, so adding I/O threads (`num.io.threads`, default **8**) is the right first move.
- **Why the others are wrong:** A — `NetworkProcessorAvgIdlePercent = 0.71` is healthy and `ResponseQueueTimeMs`/`ResponseSendTimeMs` are single-digit, so network threads are not the bottleneck. B — `num.replica.fetchers` governs how fast **followers** pull from the leader; it would show up as `RemoteTimeMs` or under-replication, and `RemoteTimeMs` is only 22 ms. D — `LocalTimeMs` of 12 ms proves the disk is not the problem.
- 🧠 **Key point / trap:** never tune from `TotalTimeMs` alone. Split it into its five phases first; each phase names a different subsystem. Also note the limit of this answer: if CPU had been at 100%, more threads would not help and the real answer would be **add a broker**.
- 📎 Source: `resources/kafka-monitoring-metrics.md` (request time breakdown + idle-percent thresholds).

### Question 5 — Answer: **A, B**

- **Why correct:** A — with `acks=all` the leader must wait for the in-sync followers to acknowledge before responding, and that wait **is** `RemoteTimeMs`; a non-zero value is the expected signature of durable writes. B — for fetch requests, `RemoteTimeMs` is the purgatory wait while the broker deliberately holds the response until `fetch.min.bytes` is available or `fetch.max.wait.ms` elapses; on a quiet topic it naturally sits near the wait ceiling.
- **Why the others are wrong:** C — with `acks=1` the leader answers as soon as it has written locally, so there is nothing to wait for; a non-zero `RemoteTimeMs` there would be genuinely odd. D — during a decommission, follower fetch traffic dominating `TotalTimeMs` is a real load event worth watching, not "no action required". E — zero `RemoteTimeMs` everywhere would mean no `acks=all` producers and no fetch waiting at all; that is unusual, not a definition of health.
- 🧠 **Key point / trap:** `RemoteTimeMs` is the one phase where a **large number is often correct**. The exam uses it to see whether you understand the mechanism or just memorised "high latency = bad".
- 📎 Source: `resources/kafka-monitoring-metrics.md` (note on `acks=-1` and `fetch.min.bytes`).

### Question 6 — Answer: **A, B**

- **Why correct:** A — matched shrink and expansion rates with no broker restart is the textbook definition of ISR flapping: the follower crosses `replica.lag.time.max.ms` (**30000** ms), gets evicted, catches up, rejoins, repeats. B — GC pauses of 1.8–3.2 s on a 48 GB heap point straight at the heap. Kafka reads and writes through the **OS page cache**, so an oversized heap buys nothing and costs long collections; the common recommendation is roughly **6 GB with G1GC**, leaving the rest of the RAM to the OS.
- **Why the others are wrong:** C — this is the planted trap. Raising `replica.lag.time.max.ms` stops the *metric* from flapping while leaving the follower just as slow, and it makes `min.insync.replicas` weaker by keeping laggards inside the ISR. D — `min.insync.replicas` controls when writes are refused; it has no influence on whether a replica is in sync. E — a long stop-the-world pause freezes **all** threads in that JVM, including replica fetching, which is exactly why GC causes flapping.
- 🧠 **Key point / trap:** "make the alarm stop" is never the same as "fix the fault". Tuning a threshold to hide a symptom is the most common wrong answer in the Troubleshooting domain.
- 📎 Source: [`README.md`](README.md) §A.5 and `resources/kafka-monitoring-metrics.md` (ISR shrink/expand normal value).

### Question 7 — Answer: **C**

- **Why correct:** `LeaderId: -1` means the quorum has **no leader**, and with two of three controllers down the majority rule is violated — the docs state that with 3 controllers the cluster tolerates exactly **1** failure. Without a majority the controller cannot commit new metadata, so every administrative operation blocks. Brokers, however, keep serving produce and fetch from their **cached metadata** for partitions whose leadership does not need to change, which is exactly the split symptom described. Restoring one controller re-establishes the majority (2 of 3).
- **Why the others are wrong:** A — fenced brokers would break produce/fetch, which are working; restarting brokers cannot create a controller majority. B — brokers are **always** observers of `__cluster_metadata`; seeing them in `CurrentObservers` is normal, and `add-controller` would make the problem worse. D — no znodes exist in Kafka 4.x.
- 🧠 **Key point / trap:** learn the shape of this incident — *"data plane fine, control plane frozen"* is almost always a quorum-majority question. And memorise the arithmetic: **2N + 1** controllers to survive N failures, so 3 → 1, 5 → 2.
- 📎 Source: `resources/kafka-kraft-operations-debug.md` (`describe --status` output and the majority rule).

### Question 8 — Answer: **B**

- **Why correct:** the exception names its own cause: the node's `meta.properties` holds a cluster ID that differs from the one the cluster is using. That happens when the storage directory was formatted with a fresh or wrong `--cluster-id`. Reformatting **only this node** with the cluster's real ID fixes it, and leaves every other broker's data alone.
- **Why the others are wrong:** A — wiping `log.dirs` on every broker destroys the entire cluster's data to fix one node; it is the catastrophic version of the right idea. C — `allow.everyone.if.no.acl.found` is an authorization setting and has nothing to do with cluster identity. D — `controller.quorum.voters` lists **controllers**, not brokers; a rolling restart cannot reconcile mismatched cluster IDs.
- 🧠 **Key point / trap:** `InconsistentClusterIdException` is a **single-node** problem with a **single-node** fix. The second sentence of the log message ("Configured controller.quorum.voters may be unaware of this broker") is deliberately misleading bait toward answer D — read the first sentence, which names `meta.properties`.
- 📎 Source: `resources/kafka-kraft-operations-debug.md` (notes on storage and cluster identity).

### Question 9 — Answer: **D**

- **Why correct:** this is the "cheap and reversible first" ladder applied to a full disk. Reducing `retention.ms` on the biggest topics reclaims space within one `log.retention.check.interval.ms` cycle, costs nothing permanent, and can be reverted. Moving load off the broker with a **throttled** reassignment is the durable fix, and `cordoned.log.dirs` is the supported way to stop new partitions landing on a directory that is going to be removed.
- **Why the others are wrong:** A — deleting segment files by hand corrupts the log and the offset index; Kafka has no way to reconcile that. B — `log.retention.bytes` is a **ceiling**, not a cleanup command, and setting it while the disk is already full does nothing immediately; it also does not touch the active segment. C — unclean leader election addresses missing leaders, not disk space, and risks data loss for no benefit here.
- 🧠 **Key point / trap:** remember that the **active segment is never deleted**, so if lowering retention does not free space, lower `segment.ms` or `segment.bytes` so segments roll and become eligible. Also note JBOD behaviour: only partitions on `/data/d2` go offline, the other two directories keep serving.
- 📎 Source: `resources/kafka-basic-operations.md` (`cordoned.log.dirs`, throttled reassignment) and [`README.md`](README.md) playbook ⑥.

### Question 10 — Answer: **C**

- **Why correct:** every member already owns exactly one partition, so the group is at its maximum useful size — a partition has at most **one** owner within a consumer group. Lag concentrated on a single partition while the others are at zero is the signature of **key skew**: the partitioner is hashing a dominant key (or key set) onto partition 3.
- **Why the others are wrong:** A — six extra consumers would all be idle; the group already has one member per partition. B — increasing to 12 partitions only helps if the **keys** spread out, which skew by definition prevents; worse, adding partitions changes key-to-partition mapping and is a **one-way** operation. D — `max.poll.records` changes batch size per poll, not which partition the records land on.
- 🧠 **Key point / trap:** walk the lag decision tree in order — *one partition only* → skew; *uneven assignment* → too few consumers; *sawtooth lag + rebalances* → poll timeout; *even lag, enough consumers* → slow processing. Adding consumers is the cheap remedy for exactly one of those four branches.
- 📎 Source: [`README.md`](README.md) playbook ⑦ (cây quyết định lag).

### Question 11 — Answer: **B**

- **Why correct:** `CONSUMER-ID`, `HOST` and `CLIENT-ID` all show `-`, which means the coordinator has **no member assigned** to those partitions. `CURRENT-OFFSET` is therefore frozen at the last committed value while `LOG-END-OFFSET` keeps growing, so the `LAG` column grows even though nothing is consuming. The group is empty or in the middle of a rebalance.
- **Why the others are wrong:** A — running-but-slow consumers would still be listed with their IDs and hosts. C — if `__consumer_offsets` were unavailable the command would fail or return no committed offsets at all, not a clean table with `CURRENT-OFFSET` values. D — consumers using `assign()` are not tracked by the coordinator and would **not appear in this output at all**, rather than appearing with `-`.
- 🧠 **Key point / trap:** `-` in `CONSUMER-ID` is a **liveness** signal, not a lag signal. Growing lag with live consumers and growing lag with no consumers demand completely different responses, and this column is how you tell them apart in one glance.
- 📎 Source: `resources/kafka-basic-operations.md` (`--describe` columns) and `resources/confluent-consumer-lag-monitoring.md`.

### Question 12 — Answer: **A, C**

- **Why correct:** the exception text names the cause verbatim: *"the time between subsequent calls to poll() was longer than the configured max.poll.interval.ms"*. That clock belongs to the **processing thread**, which is why low CPU and a healthy heartbeat thread are consistent with it. The two real remedies are to make one loop iteration finish faster — reduce `max.poll.records` from its default of **500** (A) — or to give the loop more room by raising `max.poll.interval.ms` above worst-case batch processing time (C).
- **Why the others are wrong:** B — `session.timeout.ms` (default **45000**) governs the **heartbeat** thread, which the scenario explicitly says is healthy; raising it changes nothing. D — more frequent heartbeats do not help either, for the same reason. E — disabling auto-commit hides the `CommitFailedException` but the member is still being evicted every four minutes, so the rebalance storm continues.
- 🧠 **Key point / trap:** Kafka consumers have **two independent liveness clocks**. Heartbeat healthy + member evicted always means `max.poll.interval.ms`, never `session.timeout.ms`. For deployment-driven rebalances the answer is different again: static membership (`group.instance.id`) or `group.protocol=consumer`.
- 📎 Source: [`README.md`](README.md) playbook ⑧ and CCDAK [`week-08/README.md`](../../../CCDAK/study-plan/week-08/README.md) §A.7.

### Question 13 — Answer: **A**

- **Why correct:** a Kafka client uses `bootstrap.servers` only to fetch metadata; it then opens connections **directly to each partition leader** using the address the broker advertises in `advertised.listeners`. Listing topics succeeds because it only needs the bootstrap connection, while producing fails because the leader's advertised address is unreachable from outside. The proof is in `server.log`: no produce request ever arrives, so the failure is before the broker, not inside it.
- **Why the others are wrong:** B — an ISR shortfall raises `NotEnoughReplicasException`, not a batch-expiry timeout, and it would be visible on the broker. C — `request.timeout.ms` would change how long the client waits, not whether it can reach the leader; the message is about `delivery.timeout.ms` expiring the batch anyway. D — a missing `Describe` ACL would have made `--list` fail too, and would surface as `TopicAuthorizationException`.
- 🧠 **Key point / trap:** *"bootstrap works, produce/consume times out"* is a fingerprint. Say `advertised.listeners` before reading the options. The classic settings are containerised deployments where the internal DNS name is advertised to external clients.
- 📎 Source: [`README.md`](README.md) playbook ⑪; reproduce it yourself in [Lab 7.5](labs.md).

### Question 14 — Answer: **B**

- **Why correct:** a hard, reproducible throughput ceiling with **no errors anywhere** is the signature of a quota. Broker-side throttling does not fail requests; it delays the response, and the client records that delay in `produce-throttle-time-avg`. Confirming the configured limit with `kafka-configs.sh --describe --entity-type clients` (or `users`) closes the diagnosis in two commands.
- **Why the others are wrong:** A — `records-lead-min` is a consumer retention-risk metric and says nothing about producer throughput. C — `LogFlushRateAndTimeMs` would point at disk, but disk pressure raises latency and eventually errors rather than producing a flat, exact ceiling. D — `IsrShrinksPerSec` reports replication health, and the scenario already states `UnderReplicatedPartitions` is 0.
- 🧠 **Key point / trap:** the cluster looking *perfectly healthy* is itself the clue. Healthy broker metrics plus a capped client is quota until proven otherwise — and the fix is a quota change or a conversation with the tenant, not thread tuning.
- 📎 Source: [`README.md`](README.md) playbook ⑩ and [`CCAAK-STUDY-PLAN.md`](../../CCAAK-STUDY-PLAN.md) §7.

### Question 15 — Answer: **C**

- **Why correct:** the two numbers measure from different reference points. The CLI computes `LOG-END-OFFSET − CURRENT-OFFSET`, where `CURRENT-OFFSET` is the last **committed** offset, and commits happen every `auto.commit.interval.ms` (default **5000** ms). The client metric `records-lag-max` measures from the consumer's current **fetch position**, which is always at or ahead of the committed offset. The gap of 8,500 records is simply what has been fetched but not yet committed.
- **Why the others are wrong:** A — compaction of `__consumer_offsets` keeps the latest offset per group/partition, so the CLI is not stale in that sense, and neither reading is "authoritative" over the other. B — `read_committed` affects which records are visible up to the LSO; it does not create this systematic difference. D — `records-lag-max` is the maximum over partitions and can absolutely be compared with the per-partition CLI figures; the mismatch here is about committed vs position, not about aggregation.
- 🧠 **Key point / trap:** expect the exam to present two lag numbers and ask which is wrong. The answer is **neither** — and the CLI figure is always the larger of the two.
- 📎 Source: `resources/confluent-consumer-lag-monitoring.md` (committed vs fetch position).

### Question 16 — Answer: **B**

- **Why correct:** Confluent states the limitation directly: *"You cannot monitor consumer lag with consumers that use the `assign()` method"*, because the group coordinator does not manage assignment for manually assigned consumers. Setting a `group.id` lets the application commit offsets, but nothing coordinates it, so it never shows up as a group member and no broker-side lag can be computed for it. The workable answer is for the application to expose its own client metric.
- **Why the others are wrong:** A — the tool reports on coordinator-managed groups; a standalone consumer will not be listed. C — the Confluent lag emitter computes lag for coordinator-managed groups; it does not change how `assign()` works. D — `read_committed` is about transactional visibility and is unrelated to group membership.
- 🧠 **Key point / trap:** this is a favourite because it looks like a tooling question and is actually an architecture question. `subscribe()` → group management, rebalances, measurable lag. `assign()` → none of the three.
- 📎 Source: `resources/confluent-consumer-lag-monitoring.md` (Important limitation).

### Question 17 — Answer: **D**

- **Why correct:** `records-lead-min` is the distance between the consumer's fetch position and the **log start offset**. As retention deletes old segments the start offset advances; if it catches up with the consumer, records are deleted before they are ever read. A lead approaching zero is therefore an imminent **data-loss** warning, and the only action that buys time is increasing `retention.ms` while the consumers are scaled out.
- **Why the others are wrong:** A — a falling lead is the opposite of catching up. B — that describes `OffsetOutOfRangeException`, which is what happens **after** the records are gone; the point of `records-lead-min` is to act before that. C — retention pressure on the broker is measured by disk usage, and reducing `retention.ms` would make the loss happen sooner.
- 🧠 **Key point / trap:** lag tells you how far behind you are; **lead tells you how much time you have left**. A group can have enormous lag and be perfectly safe on a 30-day topic, or modest lag and be minutes from loss on a 1-hour topic.
- 📎 Source: `resources/kafka-monitoring-metrics.md` (`records-lead-min`) and `resources/confluent-consumer-lag-monitoring.md`.

### Question 18 — Answer: **A**

- **Why correct:** `for: 10m` keeps the alert in the **pending** state while the condition is true but short-lived. A rolling restart produces two to three minutes of under-replication per broker, which never reaches ten minutes, so the page disappears — while a genuine replication failure, which persists, still fires. Detection sensitivity is untouched: the expression remains `> 0`.
- **Why the others are wrong:** B — raising the threshold to 50 silently loses every incident affecting fewer than 50 partitions, which includes most single-topic failures. C — `OfflinePartitionsCount` only catches partitions with **no leader at all**; under-replication with a live leader would go completely unnoticed. D — outages do not respect business hours, and suppressing by time window is how incidents are missed.
- 🧠 **Key point / trap:** the rule of thumb — **use `for:` to filter time-based noise; never raise the threshold to silence an alert.** `keep_firing_for:` is the companion knob for the opposite problem, a condition that flaps on and off.
- 📎 Source: `resources/prometheus-alerting-rules.md` (`for` clause, pending state, "allow slack in alerting").

### Question 19 — Answer: **B, D**

- **Why correct:** B — `OfflinePartitionsCount > 0` means partitions have no leader and are neither readable nor writable; Confluent lists it among the three minimum alerts and says to alert whenever it exceeds 0. This is user-visible loss of service, the textbook definition of a page. D — a filesystem filling up is the capacity case Prometheus calls out explicitly: *"being close to capacity often requires human intervention to avoid an outage in the near future"*. Once a `log.dirs` volume is full the broker takes the directory offline, and recovery is slow.
- **Why the others are wrong:** A — a saturated request-handler pool degrades latency and is a capacity ticket, not an outage. C — 15 minutes of ISR shrinking is a durability concern worth a ticket; the partitions still have leaders and clients still work. E — four under-replicated partitions for three minutes is indistinguishable from a rolling restart, which is precisely why that alert needs a longer `for:`.
- 🧠 **Key point / trap:** the dividing line is *"is a user losing reads or writes right now, or will we be unable to prevent it later?"* Reduced redundancy, by itself, never earns a 03:00 phone call.
- 📎 Source: `resources/confluent-broker-controller-metrics.md` (minimum alerts) and `resources/prometheus-alerting-rules.md` (capacity).

### Question 20 — Answer: **B**

- **Why correct:** the `for: 2m` clause means Prometheus must see the expression evaluate true continuously for two minutes before the alert transitions to firing. At 10:01:30 only 90 seconds have passed, so the alert is **pending** — visible in the Prometheus UI but not yet sent to Alertmanager.
- **Why the others are wrong:** A — that would be the behaviour of a rule **without** a `for` clause; those fire on the first evaluation. C — `sum()` without `by (...)` does drop the `instance` label, so the annotation will render an empty instance, but that is a cosmetic bug and does not make the alert inactive. D — `keep_firing_for` only extends an alert **after** the condition stops being true; its absence cannot resolve an alert that has not fired.
- 🧠 **Key point / trap:** knowing the pending → firing transition is what makes Lab 7.1 meaningful — an alert rule that has never been observed changing state has not been tested. *(Worth noting in passing: `sum(...) by (instance)` would fix the annotation.)*
- 📎 Source: `resources/prometheus-alerting-rules.md` (`for` clause and pending state).

### Question 21 — Answer: **B**

- **Why correct:** KIP-1100 landed in Kafka **4.2** and standardised MBean names onto the `kafka.<component>` domain, replacing names such as `org.apache.kafka.server:type=AssignmentsManager,...` with `kafka.server:type=AssignmentsManager,...`. JMX exporter rules match MBean names with regular expressions, so rules written against the old names stop matching and the corresponding Prometheus series simply cease to exist — the exporter target stays `up`, which is why this looks like a broker outage at first glance. Verifying against the raw `/metrics` output is the fastest way to confirm.
- **Why the others are wrong:** A — MBeans register at startup; a second restart changes nothing. C — `inter.broker.protocol.version` is no longer used in 4.x, and metric publication has never depended on it. D — there is no ZooKeeper and no JMX bridge in Kafka 4.x.
- 🧠 **Key point / trap:** an observability failure that **looks exactly like** an infrastructure failure. The discriminator is that the cluster is demonstrably serving traffic. Always confirm from the exporter endpoint (`curl :7071/metrics`) rather than from the dashboard you are trying to debug.
- 📎 Source: `resources/kafka-upgrade-notable-changes.md` (KIP-1100 in 4.2).

### Question 22 — Answer: **A, C**

- **Why correct:** A — `state-change.log` is written whenever the controller changes the state of a resource; it defaults to TRACE and is the file that records which replica became leader for a partition and when. C — `kafka-authorizer.log` holds authorization decisions, with **denials logged at INFO by default** and allowed requests only visible once DEBUG is enabled, which is exactly what is needed to confirm or rule out an access denial in that window.
- **Why the others are wrong:** B — `log-cleaner.log` concerns log compaction; the cleaner thread takes no leadership decisions. D — `server.properties` is a configuration file and stores no history. E — `kafka-request.log` is **disabled by default** and logs individual client requests, not controller leadership decisions.
- 🧠 **Key point / trap:** learn the four files by the question they answer — `server.log` "what is this broker doing", `controller.log` "what did the controller decide", `state-change.log` "when exactly did this partition change leader", `kafka-authorizer.log` "who was refused". Note also the default asymmetry in the authorizer log: you will see denials without changing anything, but never the allows.
- 📎 Source: `resources/confluent-logging-rolling-restart.md`.

### Question 23 — Answer: **A**

- **Why correct:** Kafka exposes each broker's loggers as the dynamic config entity `broker-loggers`, keyed by `--entity-name <node.id>`. The change takes effect immediately with no restart, and `--delete-config` reverts it. The change is also not persisted across a restart, which is a useful safety net for a temporary DEBUG session.
- **Why the others are wrong:** B — Kafka does not reload `log4j2.yaml` on `SIGHUP`; the documented runtime mechanism is the dynamic config entity. C — ZooKeeper does not exist in Kafka 4.x, and log levels were never stored there anyway. This is the version trap. D — the entity type is `broker-loggers`, not `brokers`, and the key is the logger name (`kafka.request.logger`), not a `log4j.logger.*` property.
- 🧠 **Key point / trap:** two details the exam likes — `--entity-name` is the **node id**, not a hostname, and the request logger is heavy enough that "for about 60 seconds" is part of the correct procedure, not a detail of the story.
- 📎 Source: `resources/confluent-logging-rolling-restart.md` (dynamic log level section).

### Question 24 — Answer: **C**

- **Why correct:** with `replication.factor=1` there is exactly one copy of the data, and it is on the failed disk. Leader election of any flavour can only choose among replicas that exist; unclean election merely widens the candidate set to replicas outside the ISR, and here the set is empty. The honest options are to wait for the hardware or to recreate the topic and accept the loss.
- **Why the others are wrong:** A — unclean election needs a surviving out-of-sync replica; there is none. B — `kafka-reassign-partitions.sh` can raise the replication factor, but it replicates from an existing leader; with the only replica offline there is no source. D — ELR (KIP-966) tracks replicas that were in the ISR and are eligible to become leader; it cannot invent a replica that was never created.
- 🧠 **Key point / trap:** the exam rewards recognising when **no recovery action exists**. RF=1 has no recovery path, full stop — which is why `default.replication.factor=1` (the Kafka default!) must be overridden in any production cluster.
- 📎 Source: [`README.md`](README.md) playbook ② and [`CCAAK-STUDY-PLAN.md`](../../CCAAK-STUDY-PLAN.md) §6 (`default.replication.factor` **1**).

### Question 25 — Answer: **A**

- **Why correct:** 1-X — `NotEnoughReplicasException` is raised by the leader when the ISR is below `min.insync.replicas` and the producer asked for `acks=all`; the broker is refusing the write on purpose. 2-Z — `NotLeaderOrFollowerException` (renamed from `NotLeaderForPartitionException` in 4.0) is retriable and means the client's cached metadata is stale after a leadership move; the client refreshes and retries by itself. 3-Y — a `GroupAuthorizationException` names the **group** resource, so the missing ACL is `Read` on Group, not anything on the topic. 4-W — `OffsetOutOfRangeException` means the offset the consumer wants no longer exists, typically after retention deleted it or the topic was recreated.
- **Why the others are wrong:** B swaps the causes of `NotLeaderOrFollowerException` and `OffsetOutOfRangeException`, which confuses a transient metadata refresh with permanent data deletion. C makes `NotEnoughReplicas` a leadership problem and misassigns the two authorization/offset causes. D correctly places 1 and 2 but swaps the group-ACL and offset causes.
- 🧠 **Key point / trap:** the pair that costs the most marks is `TopicAuthorizationException` vs `GroupAuthorizationException` — administrators routinely grant topic ACLs and then wonder why the consumer still fails. **Read the resource named in the exception.**
- 📎 Source: [`README.md`](README.md) §A.11 (exception cheat-sheet).

### Question 26 — Answer: **A**

- **Why correct:** the method is **metric → log → config → action**. Step 2 first: cluster-health metrics rule out (or confirm) a broker-side outage, because tuning a consumer while partitions are offline is wasted effort. Then step 4: the logs explain *why* the metrics look that way. Then step 1: the effective configuration, read with the synonyms column so you know whether a value came from a topic override, a dynamic broker config, or the static file. Only then step 3: act, cheapest reversible option first.
- **Why the others are wrong:** B starts with logs, which means reading thousands of lines without knowing what to look for. C reads configuration before logs, so you inspect settings with no hypothesis to test. D acts first and diagnoses afterwards — the fastest route to an unnecessary, irreversible change.
- 🧠 **Key point / trap:** the ordering is not bureaucracy; each step narrows the search space for the next. The `--describe --all` synonyms column matters specifically because a broker-level change often does **not** apply to topics that already carry an override.
- 📎 Source: [`README.md`](README.md) §A.9 (quy trình 4 bước + thang rẻ/đảo ngược được).

### Question 27 — Answer: **A, B**

- **Why correct:** A — the documentation recommends the Java agent *"because it avoids remote JMX/RMI setup"*, and only MBeans that match a rule are exported, which keeps scrapes small. B — `KAFKA_OPTS` is consumed by every script under `bin/`, so running a CLI tool on the broker host starts a second JVM with the same `-javaagent` argument and it fails to bind the port.
- **Why the others are wrong:** C — this inverts the guidance; standalone mode is for cases where you **cannot** attach an agent, and it *requires* remote JMX. D — the exporter only translates existing MBeans; it invents nothing, and end-to-end producer latency is not a JMX metric. E — Apache Kafka **disables remote JMX by default**; it must be enabled with `JMX_PORT`, and secured with `KAFKA_JMX_OPTS`.
- 🧠 **Key point / trap:** option B describes a real incident pattern — "`kafka-topics.sh` fails on the broker host with `Address already in use`". The workaround is `JMX_PORT= KAFKA_OPTS= kafka-topics.sh ...`, or running the CLI from a node without the agent.
- 📎 Source: `resources/prometheus-alerting-rules.md` (phần 2 — JMX Exporter) and CCDAK [`week-08/labs.md`](../../../CCDAK/study-plan/week-08/labs.md) Lab 8.1.

### Question 28 — Answer: **A**

- **Why correct:** 1-X — `RequestQueueTimeMs` is time spent waiting for a request-handler thread, which pairs with `RequestHandlerAvgIdlePercent` and `num.io.threads`. 2-W — `LocalTimeMs` is the leader's own processing, dominated by appending and flushing to disk, so it pairs with `LogFlushRateAndTimeMs`. 3-Z — `RemoteTimeMs` on a produce request is the wait for in-sync followers to acknowledge, which is normal and expected under `acks=all`. 4-Y — `ResponseSendTimeMs` is the time to write the response onto the network, so it points at the path to the client.
- **Why the others are wrong:** B swaps the queue and local phases and misplaces the remaining two. C assigns the follower wait to `LocalTimeMs` and the disk to `RemoteTimeMs`, exactly backwards. D makes `RequestQueueTimeMs` a network problem and `ResponseSendTimeMs` a thread-pool problem.
- 🧠 **Key point / trap:** the pairing to burn in is **queue phases → threads, local phase → disk, remote phase → other machines**. `ResponseQueueTimeMs` (not shown here) belongs with the network threads, alongside `NetworkProcessorAvgIdlePercent`.
- 📎 Source: `resources/kafka-monitoring-metrics.md` (request time broken down by stage).

### Question 29 — Answer: **B**

- **Why correct:** a connector and its tasks have independent states, which is why the connector can report `RUNNING` while individual tasks are `FAILED`. Failed tasks do **not** restart themselves. `POST /connectors/<name>/restart?includeTasks=true&onlyFailed=true` restarts exactly the failed tasks in place, without deleting configuration or offsets.
- **Why the others are wrong:** A — deleting and recreating works but is heavy-handed: it disrupts healthy tasks and risks losing the connector's committed offsets if the name or configuration changes. C — pause/resume affects the connector and its tasks but is not the documented mechanism for clearing a failed task state. D — restarting workers triggers a rebalance of every connector on the cluster to fix two tasks.
- 🧠 **Key point / trap:** always read `/status` for both the connector **and** each task before acting — the connector-level state alone hides task failures. `onlyFailed=true` is the detail that distinguishes a surgical restart from a blunt one.
- 📎 Source: Week 6 [`resources/connect-rest-api-reference.md`](../week-06/resources/connect-rest-api-reference.md) and [`CCAAK-STUDY-PLAN.md`](../../CCAAK-STUDY-PLAN.md) §4 Domain 6.

### Question 30 — Answer: **A**

- **Why correct:** the dead letter queue is a **sink**-connector feature: it forwards records that a sink could not process to a Kafka topic. A source connector reads from an external system and writes into Kafka, so there is no DLQ mechanism for it. With `errors.tolerance=all` and `errors.log.enable=false`, bad records are skipped and nothing is recorded anywhere — which is exactly the silence the team observed. Turning on `errors.log.enable=true` (and `errors.log.include.messages=true`) makes them visible again.
- **Why the others are wrong:** B — no DLQ topic was ever going to be created for a source connector, regardless of auto-creation. C — `errors.deadletterqueue.topic.name` has **no default**; leaving it unset means no DLQ at all, and it never derives from the connector name. D — `errors.tolerance=all` is in fact the setting a DLQ is normally used **with**; setting it to `none` makes the task fail on the first bad record instead.
- 🧠 **Key point / trap:** the pairing to remember is `errors.tolerance=all` **plus** either a DLQ (sink) or `errors.log.enable=true` (source). Tolerance on its own is a silent data-loss switch — which is precisely the incident described here.
- 📎 Source: Week 6 [`resources/connect-error-handling-dlq-kip298.md`](../week-06/resources/connect-error-handling-dlq-kip298.md) and [`CCAAK-STUDY-PLAN.md`](../../CCAAK-STUDY-PLAN.md) §7 ("Sink connector bỏ record hỏng im lặng").

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (24+/30) | Đạt ngưỡng cá nhân. | Review 100% câu sai, viết file phân tích trong `CCAAK/questions/`. Chạy thẳng **🎯 FULL MOCK #1** (60 câu / 90 phút) trong Buổi D. |
| **73–79%** (22–23/30) | Gần đạt, lỗ hổng cục bộ. | Xem bảng chấm theo domain ở đầu file: domain nào dưới ngưỡng thì đọc lại đúng mục đó trong [`README.md`](README.md) (OBS → §A.1–A.8; TROUBLE → §A.9–A.11) rồi làm lại câu sai trước khi vào FULL MOCK #1. |
| **< 73%** (≤ 21/30) | Chưa sẵn sàng cho full mock. | Làm lại **Lab 7.2 / 7.3 / 7.4** — ba lab "gây hỏng rồi sửa" này dạy đúng phần bạn đang yếu. Sau đó đọc lại **12 playbook** và làm lại bộ 30 câu, rồi mới chạy FULL MOCK #1. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / dính bẫy "quá tay" / hết giờ), và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may cũng tính là câu sai.
>
> 🎯 **Ngưỡng của Tuần 7 là FULL MOCK #1, không phải bộ 30 câu này.** Đạt **≥75%** ở full mock thì sang Tuần 8; dưới **70%** thì kích hoạt **van an toàn: lùi lịch thi 1 tuần**. Ngưỡng đăng ký thi vẫn là **≥80% trên 3 bộ mock khác nhau**.
