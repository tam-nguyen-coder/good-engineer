# ✅ Answers & Explanations — Week 8

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-AC · 3-B · 4-B · 5-C · 6-B · 7-A · 8-B · 9-B · 10-AB · 11-B · 12-D · 13-B · 14-A · 15-B · 16-AB · 17-BD · 18-A · 19-B · 20-D · 21-AB · 22-A · 23-C · 24-AB · 25-AC · 26-C · 27-BC · 28-D

---

### Question 1 — Answer: **B**

- **Why correct:** Kafka **disables remote JMX by default**. For processes started through the CLI scripts, exporting the environment variable **`JMX_PORT`** (e.g. `9999`) makes `kafka-run-class.sh` add `-Dcom.sun.management.jmxremote.port=...` (and the RMI port) to the JVM. Security settings (authentication, SSL, `java.rmi.server.hostname`) go in **`KAFKA_JMX_OPTS`**; production must enable auth because JMX ships unauthenticated.
- **Why the others are wrong:** A — there are no `jmx.enable`/`jmx.port` broker properties; JMX is a JVM feature, not a Kafka config. C — the JMX Exporter is one *consumer* of JMX, not a prerequisite; `jconsole` talks JMX directly. D — `JmxReporter` is already the default `metric.reporters`; it registers MBeans in-process but does not open a remote port.
- 🧠 **Key point / trap:** "make MBeans reachable remotely" → **`JMX_PORT`** env var (+ `KAFKA_JMX_OPTS` for security). Don't look for a `server.properties` key.
- 📎 Source: `resources/kafka-monitoring-broker-metrics.md` (Security Considerations for Remote Monitoring using JMX).

### Question 2 — Answer: **A, C**

- **Why correct:** A — every partition that had a replica on broker 3 now has |ISR| = 2 < |replicas| = 3, so the leaders of those partitions report **`UnderReplicatedPartitions` > 0** (normal value 0). C — the controller quorum is separate and unaffected; exactly one active controller exists, so the **sum of `ActiveControllerCount` is still 1**.
- **Why the others are wrong:** B — `OfflinePartitionsCount` counts partitions **with no leader**; with RF=3 every partition still has 2 live replicas, so a new leader is elected from the ISR and the count stays 0. D — leaders were elected **from the ISR**, so these are clean elections; `UncleanLeaderElectionsPerSec` stays 0 (its normal value is always 0). E — `UnderMinIsrPartitionCount` counts |ISR| < `min.insync.replicas` = 2; here ISR is 2, so it is 0 (`AtMinIsrPartitionCount` would be > 0 instead) and `acks=all` producers keep working.
- 🧠 **Key point / trap:** one broker down with RF=3/min.isr=2 → **URP > 0, AtMinIsr > 0, UnderMinIsr = 0, Offline = 0, ActiveController = 1**. Only a *second* failure flips UnderMinIsr.
- 📎 Source: `resources/kafka-monitoring-broker-metrics.md` (UnderReplicatedPartitions, UnderMinIsrPartitionCount, OfflinePartitionsCount, ActiveControllerCount) · Week 8 `README.md` §A.2.

### Question 3 — Answer: **B**

- **Why correct:** `TotalTimeMs` = `RequestQueueTimeMs` + `LocalTimeMs` + **`RemoteTimeMs`** + `ResponseQueueTimeMs` + `ResponseSendTimeMs`. For a **Produce** request with `acks=all`, `RemoteTimeMs` is the time the leader spends **waiting for in-sync followers to replicate** the batch before it can acknowledge. 170 of 180 ms there points to slow followers (disk, GC) or slow inter-broker network.
- **Why the others are wrong:** A — I/O thread saturation shows up as **`RequestQueueTimeMs`** (≈1 ms here). C — network-thread saturation shows up as `ResponseQueueTimeMs`/`ResponseSendTimeMs` (≈1 ms). D — leader disk time is **`LocalTimeMs`** (≈3 ms).
- 🧠 **Key point / trap:** map each latency phase to a bottleneck: RequestQueue → io threads; Local → leader disk; **Remote → followers (`acks=all`)**; ResponseQueue/Send → network threads.
- 📎 Source: `resources/kafka-monitoring-broker-metrics.md` (RequestMetrics TotalTimeMs breakdown) · Week 8 `README.md` §A.3.

### Question 4 — Answer: **B**

- **Why correct:** For **Fetch** requests, `RemoteTimeMs` is the time the request sits in the **purgatory** waiting for either `fetch.min.bytes` of data or the `fetch.max.wait.ms` timeout (default **500 ms**). With `fetch.min.bytes=1 MB` and moderate traffic, most fetches wait close to 500 ms by design. Lag ≈ 0 confirms consumers are healthy. The alert threshold should exclude FetchConsumer/FetchFollower `RemoteTimeMs` or be set much higher.
- **Why the others are wrong:** A — replication lag would show as **`UnderReplicatedPartitions`**, not as consumer-fetch remote time (and fetch of committed data doesn't wait for followers). C — `max.poll.records` is client-side batching from already-fetched data; it does not change purgatory time. D — page-cache misses would inflate **`LocalTimeMs`**, not `RemoteTimeMs`.
- 🧠 **Key point / trap:** **Remote time is bad for Produce, normal for Fetch.** Fetch remote ≈ `fetch.max.wait.ms` = waiting for `fetch.min.bytes`.
- 📎 Source: `resources/kafka-monitoring-broker-metrics.md` (RemoteTimeMs: "non-zero for produce requests when acks=-1; for fetch, time waiting for fetch.min.bytes") · Week 8 `README.md` §A.3.

### Question 5 — Answer: **C**

- **Why correct:** `RequestHandlerAvgIdlePercent` measures the **I/O (request handler) threads** (`num.io.threads`, default **8**). A value of 0.12 (< 0.3 warning, close to 0.1 critical) plus a growing `RequestQueueSize` means requests are waiting for a free handler → **increase `num.io.threads`**. `NetworkProcessorAvgIdlePercent` = 0.7 shows the network threads are fine.
- **Why the others are wrong:** A — `num.network.threads` (default 3) matters when **`NetworkProcessorAvgIdlePercent`** is low; it is 0.7 here. B — `num.replica.fetchers` speeds up follower replication (helps URP), not client request handling. D — `socket.request.max.bytes` caps request size; unrelated to thread saturation.
- 🧠 **Key point / trap:** two idle metrics, two thread pools: **RequestHandler ↔ `num.io.threads`**, **NetworkProcessor ↔ `num.network.threads`**; both should stay > 0.3.
- 📎 Source: `resources/kafka-monitoring-broker-metrics.md` (RequestHandlerAvgIdlePercent, NetworkProcessorAvgIdlePercent) · `resources/confluent-consumer-lag.md` (threshold < 0.3 / < 0.1).

### Question 6 — Answer: **B**

- **Why correct:** The de-facto standard is the **Prometheus JMX Exporter running as a Java agent inside the broker JVM**: `-javaagent:jmx_prometheus_javaagent.jar=<port>:<rules.yml>`. It reads MBeans in-process, applies the YAML `rules` (regex `pattern` → `name`, `labels`, `type`) and serves `/metrics` over HTTP (commonly **7071**) for Prometheus to scrape. No remote JMX port needs to be opened. `KAFKA_OPTS` is the environment variable `kafka-run-class.sh` appends to the JVM command line.
- **Why the others are wrong:** A — Kafka ships only `JmxReporter` (default); there is no built-in Prometheus reporter class. C — Prometheus cannot speak the JMX/RMI protocol; there is no `scheme: jmx`. D — `JmxTool` prints metrics to stdout for ad-hoc inspection; tailing its output is not a scrape endpoint and would still need remote JMX.
- 🧠 **Key point / trap:** "Prometheus + Kafka" → **JMX Exporter javaagent + rules YAML**. "Quick one-off read" → `JmxTool` / `jconsole` (needs `JMX_PORT`).
- 📎 Source: Week 8 `README.md` §A.1 · `resources/kafka-monitoring-broker-metrics.md` (JMX overview) · Lab 8.1.

### Question 7 — Answer: **A**

- **Why correct:** `batch-size-avg` ≈ 700 B versus `batch.size` = 16 384 B means batches are sent **long before they fill**; `record-queue-time-avg` ≈ 5 ms equals the default **`linger.ms` = 5 ms**, proving the linger timer — not the size limit — is closing batches. Raising `linger.ms` lets more records accumulate per partition, which increases records per request (fewer requests → lower broker CPU) and gives the compressor more data per batch, improving `compression-rate-avg` (0.95 ≈ almost no compression because batches are tiny).
- **Why the others are wrong:** B — `batch.size` is an upper bound; batches are nowhere near 16 KB, so a bigger cap changes nothing. C — `max.in.flight=1` reduces pipelining and throughput; unrelated to batch fill. D — `gzip` compresses better per byte but with tiny batches the ratio stays poor and CPU rises; fix batching first.
- 🧠 **Key point / trap:** **`batch-size-avg` ≪ `batch.size` and `record-queue-time-avg` ≈ `linger.ms` → increase `linger.ms`.** `compression-rate-avg` is compressed/uncompressed, so **lower is better**.
- 📎 Source: `resources/kafka-monitoring-client-metrics.md` (Producer Sender Metrics: batch-size-avg, record-queue-time-avg, compression-rate-avg) · Week 3 `README.md` §A.5.

### Question 8 — Answer: **B**

- **Why correct:** `min.insync.replicas` is only enforced for **`acks=all` (-1)** writes: when |ISR| (1) < min.isr (2) the leader rejects them with **`NotEnoughReplicasException`** (retriable — the producer keeps retrying until `delivery.timeout.ms`). `UnderMinIsrPartitionCount` > 0 is exactly the broker-side signal of this state. App Y with **`acks=1`** only needs the leader's local append, so it continues to succeed — but with the risk of losing data if that last broker dies.
- **Why the others are wrong:** A/C — `acks=1` is not subject to `min.insync.replicas`. D — `min.insync.replicas` is a producer-durability guard; consumers are unaffected (they can still read committed data).
- 🧠 **Key point / trap:** **`min.insync.replicas` + `acks=all` together** give durability; `acks=1` silently bypasses it. `UnderMinIsrPartitionCount` > 0 ⇔ `acks=all` producers blocked.
- 📎 Source: `resources/kafka-monitoring-broker-metrics.md` (UnderMinIsrPartitionCount) · Week 2 `README.md` (ISR / min.insync.replicas / acks).

### Question 9 — Answer: **B**

- **Why correct:** `records-lead-min` (KIP-92) is the distance between the consumer's position and the partition's **log start offset** — i.e. how far the consumer is from the *oldest* retained record. A steadily shrinking lead with a 1-hour retention means the retention cleaner is about to delete records the group has **not read yet** → **permanent data loss** for that group (it will then hit `OffsetOutOfRangeException`). This is more urgent than the lag itself.
- **Why the others are wrong:** A — `max.poll.interval.ms` relates to `time-between-poll-max`, not lead. C — `fetch.max.bytes` caps a single fetch response; unrelated. D — `offsets.retention.minutes` (7 days) applies to offsets of **empty** groups, not to an active consumer.
- 🧠 **Key point / trap:** **lag = distance to the head (LEO); lead = distance to the tail (log start).** Lead → 0 = about to lose data; raise `retention.ms` temporarily and scale consumers now.
- 📎 Source: `resources/kafka-monitoring-client-metrics.md` (records-lead-min, records-lag-max) · Week 8 `README.md` §A.5.

### Question 10 — Answer: **A, B**

- **Why correct:** The exception text itself names the cause: the gap between two `poll()` calls exceeded **`max.poll.interval.ms` (300 000 ms)**, so the coordinator considered the member dead, rebalanced, and refused its late commit. `time-between-poll-max` ≈ 320 s confirms it. Fixes: **A** — fewer records per poll (`max.poll.records`, default 500) so each batch finishes faster; **B** — raise `max.poll.interval.ms` above the worst-case batch time. (Offloading the slow call to another thread with `pause()`/`resume()` is a third valid option.)
- **Why the others are wrong:** C — `session.timeout.ms` (45 s) governs **heartbeats** from the background heartbeat thread, which kept running; it is not what expired. D — sync commits after each record slow processing further and don't change poll spacing. E — heartbeat interval must be ≪ session timeout (≈1/3); setting them equal breaks liveness detection.
- 🧠 **Key point / trap:** **`CommitFailedException` + long processing → `max.poll.interval.ms` / `max.poll.records`**, never `session.timeout.ms` (that is for heartbeats / crashes).
- 📎 Source: Week 8 `README.md` §A.7 (rebalance diagnostics table) · `resources/kafka-monitoring-client-metrics.md` (time-between-poll-max, consumer-coordinator-metrics).

### Question 11 — Answer: **B**

- **Why correct:** **Static membership** (`group.instance.id`, KIP-345) makes a restarted consumer rejoin as the *same* member: as long as it returns within `session.timeout.ms`, the coordinator does not trigger a rebalance and the member gets its previous partitions back. Setting `session.timeout.ms` above the typical 20 s restart (default is already 45 s; raise if restarts take longer) is the companion setting. `rebalance-rate-per-hour` and the sawtooth lag disappear.
- **Why the others are wrong:** A — `max.poll.interval.ms` addresses slow processing, not restarts. C — the assignor only decides *how* partitions are distributed; any member leave/join still triggers a rebalance. D — `group.initial.rebalance.delay.ms` only delays the very first rebalance of an *empty* group.
- 🧠 **Key point / trap:** "frequent quick restarts → rebalances" → **`group.instance.id` + `session.timeout.ms`**. Cooperative/KIP-848 make rebalances cheaper, static membership makes them **not happen**.
- 📎 Source: Week 4 `README.md` (static membership) · `resources/kafka-monitoring-client-metrics.md` (rebalance-rate-per-hour, last-rebalance-seconds-ago).

### Question 12 — Answer: **D**

- **Why correct:** In `kafka-consumer-groups.sh --describe`, **`CONSUMER-ID`, `HOST` and `CLIENT-ID` equal `-` when no member currently owns the partition** — the group is `Empty`/inactive (all consumers left or crashed). `CURRENT-OFFSET` is the last committed offset and stays frozen, while `LOG-END-OFFSET` keeps advancing, so `LAG` grows on every run. The fix is operational: start the application / investigate why it died.
- **Why the others are wrong:** A — running consumers would appear with a `CONSUMER-ID` like `consumer-billing-1-<uuid>` and a host. B — during a rebalance the tool prints a warning ("Consumer group 'billing' is rebalancing") rather than dashes for a long time. C — `assign()` consumers don't appear in the group's assignment at all and don't commit to it unless they set `group.id` explicitly; the tool doesn't "hide" IDs.
- 🧠 **Key point / trap:** **`CONSUMER-ID = -` ⇒ nobody is consuming.** Growing LAG with dashes = app down, not app slow.
- 📎 Source: `resources/kafka-basic-ops-reassignment.md` (Managing Consumer Groups: describe output, `CONSUMER-ID` = `-`) · `resources/confluent-consumer-lag.md`.

### Question 13 — Answer: **B**

- **Why correct:** A partition is consumed by **at most one member** of a group, so with 3 partitions only 3 of the 5 instances get work; the `--members` output (`#PARTITIONS = 0` for two members) proves they are **idle**. Adding more consumers cannot raise throughput. Either **increase the partition count** (then consumers ≤ partitions become useful — accepting that `hash(key) % N` changes and key ordering across old/new records breaks) or make the three active consumers faster.
- **Why the others are wrong:** A — 8 instances → 5 idle. C — no assignor can give one partition to two members of the same group. D — `fetch.max.bytes` changes fetch response size; a consumer never fetches partitions it isn't assigned.
- 🧠 **Key point / trap:** **parallelism ceiling = number of partitions.** "Scaled consumers, lag unchanged, some members have 0 partitions" → add partitions.
- 📎 Source: `resources/confluent-consumer-lag.md` (root causes: consumer/partition mismatch; remediation order) · Week 1 `README.md` (consumer ≤ partition).

### Question 14 — Answer: **A**

- **Why correct:** All symptoms point to a **hot partition caused by key skew**: one tenant's key hashes to partition 7, so that partition receives ~10× the traffic and its single consumer cannot keep up. Because one partition maps to exactly one consumer, the only fix is on the **producer/partitioning side**: composite keys (`tenantId#bucket`), a custom `Partitioner` that spreads the hot tenant over several partitions (accepting weaker per-tenant ordering), or dropping the key if ordering is not required.
- **Why the others are wrong:** B — the 13th consumer would be idle; partition 7 still has one consumer. C — `max.poll.records` doesn't increase the consumer's processing capacity. D — moving the partition to another broker relieves the **broker**, not the consumer bottleneck (and the broker is not the one failing here).
- 🧠 **Key point / trap:** **"lag on one partition only" → key skew**, and **adding consumers never helps a hot partition**.
- 📎 Source: Week 8 `README.md` §A.6 (lag causes table: key skew) & §A.10 (capacity planning: hot partition) · `resources/confluent-consumer-lag.md`.

### Question 15 — Answer: **B**

- **Why correct:** The consumer's `records-lag-max` is calculated from its **current fetch position** (records already fetched into the client, whether processed or committed). The CLI's `LAG` = `LOG-END-OFFSET − CURRENT-OFFSET`, where `CURRENT-OFFSET` is the **last committed offset** read from `__consumer_offsets`. With auto-commit every **5 000 ms** the committed offset trails the position, so the CLI shows a few hundred records of "lag" that the client has already fetched. Both numbers are correct; they measure different things.
- **Why the others are wrong:** A — `--bootstrap-server` can be any broker; the tool locates the coordinator itself. C — the metric updates on every fetch. D — `read_uncommitted` is the default; transactional markers are not the cause of a consistent offset gap.
- 🧠 **Key point / trap:** **client lag = position-based; CLI/Burrow lag = committed-offset-based.** Expect CLI ≥ client.
- 📎 Source: `resources/confluent-consumer-lag.md` (client-side vs broker/tool-side lag) · `resources/kafka-monitoring-client-metrics.md` (records-lag-max definition).

### Question 16 — Answer: **A, B**

- **Why correct:** This is the classic **poison pill**: the consumer's position never advances past the bad offset (nothing is committed after it), so every restart re-fetches the same record and fails again, while lag on that partition grows. Two standard remedies: **A** — a **dead-letter topic**: catch the error, publish the raw bytes with headers (`source-topic`, `source-partition`, `source-offset`, `error-reason`) to `orders-dlq`, then continue (Spring's `ErrorHandlingDeserializer`/`DeadLetterPublishingRecoverer` automate this). **B** — **skip** it: `RecordDeserializationException` carries `topicPartition()` and `offset()`; call `consumer.seek(tp, offset + 1)` and continue.
- **Why the others are wrong:** C — `auto.offset.reset` applies only when there is **no committed offset** or it is out of range; here a valid committed offset exists just before the bad record, so the reset never kicks in. D — deserialization fails instantly; time is irrelevant. E — `enable.idempotence` is a producer setting.
- 🧠 **Key point / trap:** **deserialization failure ≠ processing failure**: it happens inside `poll()` before your code runs, so only seek/DLQ/`ErrorHandlingDeserializer` help. `auto.offset.reset` is a red herring.
- 📎 Source: Week 8 `README.md` §A.8 (exception cheat-sheet: SerializationException / poison pill) · Lab 8.5.

### Question 17 — Answer: **B, D**

- **Why correct:** **B** — `RecordTooLargeException`: the batch exceeds `max.request.size` (client, 1 048 576) or `message.max.bytes` (broker, 1 048 588) / `max.message.bytes` (topic); retrying cannot shrink it, so it is fatal for that record. **D** — `ProducerFencedException`: another producer with the same `transactional.id` bumped the epoch; the fenced instance can never commit again and must be **closed** (not retried, not aborted).
- **Why the others are wrong:** A — `NotLeaderOrFollowerException` (renamed from `NotLeaderForPartitionException` in 4.0) is **retriable**: the client refreshes metadata and retries. C — `NotEnoughReplicasException` is **retriable**: ISR may recover within `delivery.timeout.ms`. E — `LeaderNotAvailableException` is **retriable**: a leader election is in progress.
- 🧠 **Key point / trap:** retriable = cluster-state problems (leader, ISR, network, metadata); **fatal = data/config/auth/epoch problems** (size, serialization, authorization, fenced, out-of-order sequence).
- 📎 Source: Week 8 `README.md` §A.8 · Week 3 `README.md` §A.3 (retriable vs fatal table).

### Question 18 — Answer: **A**

- **Why correct:** After 10 days the committed offset points to data that retention (7 days) has already deleted, so the fetch fails with **`OffsetOutOfRangeException`**. The consumer then applies **`auto.offset.reset`**, whose default is **`latest`** → it jumps to the newest records and silently skips everything still retained. Setting `auto.offset.reset=earliest` makes it resume from the **oldest retained** record (the 7 days still on disk). `none` would surface the exception to the application instead.
- **Why the others are wrong:** B — offsets are only expired for **empty** groups after `offsets.retention.minutes` (7 days = 10 080); the question states they are still present. C — `isolation.level` filters transactional records, not out-of-range offsets. D — `fetch.max.wait.ms` is the purgatory wait, unrelated.
- 🧠 **Key point / trap:** `auto.offset.reset` has **two** triggers: no committed offset **or** committed offset out of range. Default **`latest`** = potential silent skip.
- 📎 Source: Week 8 `README.md` §A.8 (OffsetOutOfRangeException) · Week 4 `README.md` (auto.offset.reset).

### Question 19 — Answer: **B**

- **Why correct:** **`state-change.log`** records every partition state transition the broker applies from the controller — leader changes, ISR expansions/shrinks, replica state (online/offline). It is the authoritative timeline for "who was leader when". (`controller.log` on the active controller shows the election decisions themselves; `server.log` has a summary.)
- **Why the others are wrong:** A — `kafka-authorizer.log` records ACL allow/deny decisions (use it for `TopicAuthorizationException`). C — `kafka-request.log` is the request logger (DEBUG/TRACE, very verbose) for individual client requests. D — `log-cleaner.log` covers compaction runs.
- 🧠 **Key point / trap:** leader/ISR history → **`state-change.log`**; ACL denials → **`kafka-authorizer.log`**; quorum/election → `controller.log`. Kafka 4.0 uses **Log4j2** (`log4j2.yaml`); levels can be changed at runtime via `kafka-configs.sh --entity-type broker-loggers`.
- 📎 Source: Week 8 `README.md` §A.9 (Logging & tracing) · `resources/kafka-upgrade-kraft.md` (Log4j2 / `state-change.log.[date]` rotation note).

### Question 20 — Answer: **D**

- **Why correct:** Kafka **never rebalances existing partitions onto a new broker automatically**; a new broker only receives replicas of topics **created afterwards**. To move load you must run **`kafka-reassign-partitions.sh`**: `--generate` (with `--topics-to-move-json-file` and `--broker-list 1,2,3,4,5`) to obtain a proposed assignment, `--execute` it (optionally `--throttle`), then `--verify`. Alternatively use **Cruise Control**, which computes and executes such plans automatically based on load goals.
- **Why the others are wrong:** A — a controller-only node wouldn't have `PartitionCount` at all and the symptom would differ; nothing suggests misconfigured roles. B — a mismatched `cluster.id` prevents the broker from **starting/registering**; it wouldn't sit idle in the cluster. C — `auto.leader.rebalance.enable` only moves **leadership among existing replicas**; broker 5 has no replicas to lead.
- 🧠 **Key point / trap:** **"new broker gets no traffic" → reassignment tool (or Cruise Control)**, not a config flag.
- 📎 Source: `resources/kafka-basic-ops-reassignment.md` (Expanding your cluster) · `resources/cruise-control-readme.md`.

### Question 21 — Answer: **A, B**

- **Why correct:** **A** — `--throttle N` writes dynamic configs `leader.replication.throttled.rate`/`follower.replication.throttled.rate` on the brokers and `leader/follower.replication.throttled.replicas` on the topics. They are **not** removed when the move finishes; running **`--verify`** with the same JSON both confirms completion and **clears the throttle**. Forgetting it leaves normal replication throttled. **B** — the throttle also applies to the moving replicas' fetch; if the partitions ingest more than the throttle rate the new replicas can **never catch up**; raise it with `--execute --additional --throttle <higher>` (or wait for a low-traffic window).
- **Why the others are wrong:** C — see A: removal is manual via `--verify`. D — the throttle limits **inter-broker replication** of the reassigned replicas, not client produce. E — reassignment is online; producers and consumers keep working (leadership may move at the end).
- 🧠 **Key point / trap:** **`--verify` = check + remove throttle.** Throttle below inbound rate ⇒ reassignment stalls forever.
- 📎 Source: `resources/kafka-basic-ops-reassignment.md` (Limiting Bandwidth Usage during Data Migration: "the throttle must be removed by running --verify"; "throttle rate should be greater than the inbound rate").

### Question 22 — Answer: **A**

- **Why correct:** After a rolling restart, the first broker back up becomes leader for many partitions as others restart. The **replica lists (and preferred replicas) are unchanged**, so the right tool is **`kafka-leader-election.sh --election-type preferred --all-topic-partitions`**, which moves leadership back to the first replica of each list in seconds, with no data movement. `auto.leader.rebalance.enable=true` would eventually do this, but only every `leader.imbalance.check.interval.seconds` (300 s) and only above `leader.imbalance.per.broker.percentage` (10%).
- **Why the others are wrong:** B — reassignment moves **replicas** (copies data); unnecessary and slow when only leadership is skewed. C — `unclean` elects a non-ISR replica and is only for **offline** partitions where data loss is acceptable. D — restarting broker 1 causes another disruption and just shifts the skew to whichever broker is up.
- 🧠 **Key point / trap:** **replica placement skewed → reassignment; leadership skewed → preferred leader election.**
- 📎 Source: `resources/kafka-basic-ops-reassignment.md` (Balancing leadership: preferred replica, `auto.leader.rebalance.enable`, `kafka-leader-election.sh`).

### Question 23 — Answer: **C**

- **Why correct:** Kafka **does not support reducing the number of partitions** of a topic (there is no way to merge logs while preserving offsets/keys). The only path is to **create a new topic** with the desired count, copy the data (MirrorMaker 2 with `IdentityReplicationPolicy`-style renaming, a Kafka Streams/ksqlDB job, or re-produce from the source), and switch producers/consumers.
- **Why the others are wrong:** A — `--alter --partitions` only accepts a value **higher** than the current count; a lower value fails with an error. B — reassignment changes *where* replicas live, not *how many* partitions exist. D — `kafka-delete-records.sh` advances the log start offset of a partition (purges data); the partition still exists.
- 🧠 **Key point / trap:** **partitions: increase-only.** And increasing has its own trap (key → partition mapping changes).
- 📎 Source: `resources/kafka-basic-ops-reassignment.md` (Modifying topics: "Kafka does not currently support reducing the number of partitions").

### Question 24 — Answer: **A, B**

- **Why correct:** **A** — a rolling upgrade means **one broker at a time**; with RF=3/min.isr=2 the cluster tolerates exactly one missing replica per partition, so you must wait until **`UnderReplicatedPartitions` = 0** (all followers caught up) before taking down the next broker. `controlled.shutdown.enable=true` (default) transfers leadership before the stop. **B** — once every broker runs 4.3 and behaves correctly, **finalize** the metadata version with `kafka-features.sh upgrade --release-version 4.3` (or `--metadata 4.3`). Until then the cluster keeps the old `metadata.version`, allowing rollback of the binaries.
- **Why the others are wrong:** C — two brokers down can drop |ISR| to 1 < min.isr → `acks=all` writes rejected, and any partition with both remaining replicas on those brokers goes **offline**. D — `inter.broker.protocol.version` is the ZooKeeper-era mechanism; KRaft uses **`metadata.version`** managed by `kafka-features.sh`, not a static property. E — the order is reversed: finalize **after** all brokers run the new code; and note 4.3 has metadata changes, so once finalized it **cannot be downgraded**.
- 🧠 **Key point / trap:** rolling upgrade = **one broker → wait URP=0 → next…**, then **finalize with `kafka-features.sh`**; downgrade of metadata only when no metadata change between versions.
- 📎 Source: `resources/kafka-upgrade-kraft.md` (Upgrading to 4.3.0: rolling upgrade steps, finalize, downgrade note) · `resources/kafka-basic-ops-reassignment.md` (Graceful shutdown).

### Question 25 — Answer: **A, C**

- **Why correct:** **A** — with the broker side ready, a topic opts in with **`remote.storage.enable=true`**. **`local.retention.ms` / `local.retention.bytes`** define how long/much data stays on local disk (segments are deleted locally only **after** they have been copied to remote), while `retention.ms` / `retention.bytes` define **total** retention (effectively the remote tier). If `local.*` is unset it inherits `retention.*`. **C** — tiered storage **does not support compacted topics** (`cleanup.policy=compact`); it works only with `delete` retention.
- **Why the others are wrong:** B — only **closed (rolled) segments** are uploaded; the active segment always stays local (tail reads use the page cache). D — the opposite: `local.retention.*` must be **≤** total `retention.*`. E — no consumer setting exists; brokers transparently fetch tiered segments (visible in `RemoteFetchBytesPerSec`).
- 🧠 **Key point / trap:** **`remote.storage.enable` + `local.retention.*`**; closed segments only; **no compaction**; Kafka ships no `RemoteStorageManager` — you bring a plugin.
- 📎 Source: `resources/kafka-tiered-storage.md` (Topic Configurations, Limitations).

### Question 26 — Answer: **C**

- **Why correct:** MirrorMaker 2's default **`DefaultReplicationPolicy`** names the remote topic **`<source-alias>.<topic>`** (`primary.orders`). This is deliberate: in **active/active** (`primary->dr` and `dr->primary`) it prevents infinite replication loops (MM2 knows `primary.orders` on `dr` came from `primary` and won't mirror it back) and keeps locally produced `orders` separate from mirrored data. Consumers on either side read `orders` + `<other>.orders`. **`IdentityReplicationPolicy`** keeps the original name but has **no loop protection**, so it is only appropriate for one-directional flows (active/passive, migration, MM1 replacement).
- **Why the others are wrong:** A — using Identity in active/active creates a loop (`orders` ↔ `orders`). B — the policy is pluggable (`replication.policy.class`) and the separator configurable (`replication.policy.separator`). D — `topics` is a filter on **source** topic names; it does not add prefixes.
- 🧠 **Key point / trap:** **`A.topic` = DefaultReplicationPolicy (loop-safe, active/active); same name = IdentityReplicationPolicy (one-way only).**
- 📎 Source: `resources/kafka-georeplication-mirrormaker2.md` (Replication flows, `DefaultReplicationPolicy` vs `IdentityReplicationPolicy`).

### Question 27 — Answer: **B, C**

- **Why correct:** **B** — **`MirrorCheckpointConnector`** periodically emits checkpoints (`<source>.checkpoints.internal`) that map each consumer group's committed offset on the source to the equivalent offset on the target; with `sync.group.offsets.enabled=true` it writes the translated offsets directly into the target's `__consumer_offsets` (while the group is inactive there), and clients can also call `RemoteClusterUtils.translateOffsets()`. **C** — **`MirrorHeartbeatConnector`** emits records to the `heartbeats` topic; their propagation is used to verify connectivity and measure **replication latency** (`replication-latency-ms`, `checkpoint-latency-ms` metrics complement this).
- **Why the others are wrong:** A — `MirrorSourceConnector` copies the **records, topic configs and ACLs**; it is essential but does not translate consumer offsets or emit heartbeats. D/E — there is no `MirrorOffsetConnector` or `MirrorSinkConnector`; MM2 is built from three **source** connectors on Kafka Connect.
- 🧠 **Key point / trap:** **Source = data, Checkpoint = consumer offsets, Heartbeat = liveness/latency.** MM1 was removed in 4.0.
- 📎 Source: `resources/kafka-georeplication-mirrormaker2.md` (three connectors, offset translation, metrics).

### Question 28 — Answer: **D**

- **Why correct:** Partition count ≈ **max(T/P, T/C)** where T = target throughput, P = per-partition write capacity, C = per-consumer processing capacity. Here T/P = 200 / 10 = **20**, T/C = 200 / 4 = **50** → the consumer side dominates, so at least 50 partitions are needed for 50 parallel consumers. Adding ~20% headroom → **60**. (Rounding to a number with many divisors also eases future scaling of the consumer group.)
- **Why the others are wrong:** A — 20 satisfies the write side only; 20 consumers × 4 MB/s = 80 MB/s of processing → lag grows. B — 24 is 20 + headroom but ignores the consumer constraint. C — 50 meets the requirement with **zero** headroom, contrary to the stated 20% margin.
- 🧠 **Key point / trap:** always compute **both** ratios and take the **max**; consumers are usually the binding constraint. Remember disk = throughput × retention × RF (+ headroom), and keep ≲ 4 000 partitions per broker.
- 📎 Source: Week 8 `README.md` §A.10 (Capacity planning) · Week 1 `README.md` §C.2 (choosing partition count).
