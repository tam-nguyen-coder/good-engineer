# ✅ Answers & Explanations — Week 3: Replication & durability, quotas, throughput and JVM/OS tuning

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

**Answer key:** 1-A · 2-C · 3-B · 4-D · 5-B · 6-C · 7-BC · 8-B · 9-C · 10-A · 11-D · 12-BD · 13-C · 14-A · 15-B · 16-D · 17-AD · 18-A · 19-A · 20-C · 21-B · 22-C · 23-B · 24-AC · 25-BD · 26-D · 27-C · 28-B · 29-B · 30-AC

---

### Question 1 — Answer: **A**

- **Why correct:** the number of brokers a topic can lose while still accepting `acks=all` writes is `replication.factor − min.insync.replicas`. With RF=3 and `min.insync.replicas=3` that is **0**, so the very first broker outage — even a planned one — drops every partition's ISR to 2 and the leader rejects the writes. The documented production triple is RF=3 / `min.insync.replicas=2` / `acks=all`, which survives exactly one broker failure without losing data.
- **Why the others are wrong:** B — `unclean.leader.election.enable` only matters when a partition has **no** in-sync replica left and therefore no leader; here every partition still has a healthy leader and an ISR of 2, so unclean election is irrelevant (and would trade away data for nothing). C — leadership is fine: `Leader:` is populated for all three partitions, and preferred-leader rebalancing has no effect on the min-ISR check. D — partition count has nothing to do with this; adding partitions would multiply the number of blocked partitions, not fix any of them.
- 🧠 **Key point / trap:** `min.insync.replicas = replication.factor` is the single most repeated trap in this domain. For RF=3 the answer is always **2**. "More durable" is not automatically "better" — it costs exactly one broker of availability.
- 📎 Source: `resources/kafka-design-replication.md` (Availability and Durability Guarantees; the `min.insync.replicas` config description).

### Question 2 — Answer: **C**

- **Why correct:** `min.insync.replicas=2` with RF=3 is the correct setting and the rejection is the mechanism working as designed — it is refusing to acknowledge writes that would exist on a single replica. The fix is to restore the missing replica so the ISR returns to 2: bring the broker back, or provision a replacement and move the replicas onto it.
- **Why the others are wrong:** A — lowering `min.insync.replicas` to 1 makes the errors disappear by removing the protection; every write acknowledged during the outage would then live on one disk, which is exactly the loss scenario the setting exists to prevent. B — unclean leader election applies to partitions with an **empty** ISR; here the ISR is 1, leaders exist, and enabling it would not unblock a single write. D — `replica.lag.time.max.ms` governs how long a *slow* follower may lag before it is removed; a broker that is offline loses its controller session and leaves the ISR regardless of that timer.
- 🧠 **Key point / trap:** CCAAK repeatedly rewards the answer that **restores redundancy** over the answer that **silences the alarm**. "Lower `min.insync.replicas` during an incident" is almost always the distractor.
- 📎 Source: `resources/kafka-design-replication.md`; `resources/kafka-monitoring-tuning-signals.md` (`UnderMinIsrPartitionCount` = `acks=all` is being rejected).

### Question 3 — Answer: **B**

- **Why correct:** the broker checks the ISR size twice. Before appending, an ISR below `min.insync.replicas` produces `NotEnoughReplicasException` — nothing was written, so a retry is clean. If the ISR shrinks **after** the leader has already appended the batch to its own log, the broker answers `NotEnoughReplicasAfterAppendException`; the record is physically in the leader's log but was never committed, so a producer retry can append it a second time unless idempotence deduplicates it.
- **Why the others are wrong:** A — both are broker-side errors surfaced to the client; neither is raised locally before the request is sent. C — both are raised only for `acks=all`; with `acks=1` or `acks=0` the `min.insync.replicas` check is not performed at all. D — both are **retriable** errors; the default producer (`enable.idempotence=true`, `acks=all`) retries them automatically.
- 🧠 **Key point / trap:** the giveaway is in the message text — "**Messages are rejected**" versus "**Messages are written to the log, but** to fewer in-sync replicas than required".
- 📎 Source: `resources/kafka-broker-configs-replication-throughput.md` (`min.insync.replicas` description names both exceptions).

### Question 4 — Answer: **D**

- **Why correct:** a replica is removed from the ISR when it fails to catch up to the leader's log end offset within `replica.lag.time.max.ms` (30000 ms). A multi-second GC pause or a disk that stalls the fetcher threads does exactly that, and when the pause ends the replica catches up and rejoins — producing the shrink/expand oscillation with no broker restart and no change in throughput. Confluent's guidance is explicit that you size this timeout from an observed `MinFetchRate`, i.e. **measure first, tune second**.
- **Why the others are wrong:** A — `replica.lag.max.messages` was removed in Kafka 0.9; ISR membership has been time-based for over a decade, so this option is a version trap. B — lowering the timeout makes replicas leave the ISR *faster*, worsening the flapping and risking `UnderMinIsrPartitionCount` > 0. C — `min.insync.replicas` is a write-admission threshold; it does not change which replicas the leader considers in sync.
- 🧠 **Key point / trap:** ISR flapping has two usual suspects — **GC pauses** and **disk latency**. Reaching for `replica.lag.time.max.ms` first is the trap, and it is `read-only` anyway (restart required).
- 📎 Source: `resources/confluent-production-tuning.md` (Lagging replicas, `MinFetchRate` sizing rule); `resources/kafka-monitoring-tuning-signals.md` (`IsrShrinksPerSec` expected value 0).

### Question 5 — Answer: **B**

- **Why correct:** the docs state that regardless of the `acks` setting, messages are not visible to consumers until (1) they are replicated to **all** in-sync replicas **and** (2) the number of in-sync replicas is at least `min.insync.replicas`. That is the strict-min-ISR rule: with `|ISR| = 1 < min.insync.replicas = 2`, the high watermark freezes and consumers stop seeing new data even though `acks=1` writes keep landing in the leader's log.
- **Why the others are wrong:** A — `isolation.level` filters records from aborted transactions; it has nothing to do with the high watermark rule for min-ISR. C — the records are not discarded: they are appended to the leader's log, which is precisely why they can be lost if that leader dies. D — leader rebalancing does not move the high watermark; the high watermark is a property of the partition's replication state.
- 🧠 **Key point / trap:** the same rule that "hides" the records is what makes **ELR** safe — replicas that leave the ISR after the high watermark froze are guaranteed to hold every committed message.
- 📎 Source: `resources/kafka-design-replication.md` (the two visibility conditions); `resources/kafka-eligible-leader-replicas.md` (strict min ISR).

### Question 6 — Answer: **C**

- **Why correct:** the broker configuration documentation carries an explicit KRaft note: when `unclean.leader.election.enable` is enabled dynamically, "it needs to wait for the unclean leader election thread to trigger election periodically (default is 5 minutes). Please run `kafka-leader-election.sh` with unclean option to trigger the unclean leader election immediately if needed." The administrator's command was right; only the timing expectation was wrong.
- **Why the others are wrong:** A — ZooKeeper was removed in Kafka 4.0; `zookeeper.connect` no longer exists, and the config is a perfectly valid dynamic topic override. B — the setting exists at both broker and topic level; the topic-level override is honoured (and is the safer scope here). D — dynamic configs apply to live topics; nothing about unclean election is fixed at creation time.
- 🧠 **Key point / trap:** two traps in one question — the **ZooKeeper** distractor (always wrong on 4.x) and the "dynamic config didn't work" symptom whose real cause is the **5-minute election thread**.
- 📎 Source: `resources/kafka-broker-configs-replication-throughput.md` (`unclean.leader.election.enable`, KRaft note).

### Question 7 — Answer: **B, C**

- **Why correct:** B restates the documented default and its meaning — from 0.11.0.0 Kafka waits for a consistent replica rather than electing an out-of-sync one, preferring unavailability over the risk of message loss. C is the operational point an administrator is expected to know: the setting can be scoped cluster-wide with `--entity-type brokers --entity-default` or limited to a single topic with `--entity-type topics`, which is how you make one low-value topic available without exposing everything.
- **Why the others are wrong:** A — the default is `false`, not `true`. D — there is no back-fill: the docs say the elected replica's log "becomes the source of truth even though it is not guaranteed to have every committed message"; the missing messages are simply gone. E — the metric exists but lives in a different MBean domain: it is `kafka.controller:type=ControllerStats,name=UncleanLeaderElectionsPerSec`, not `kafka.server:type=ReplicaManager`.
- 🧠 **Key point / trap:** unclean election is the **last** option in every CCAAK scenario, and when it is the answer the question will have told you that data loss is acceptable.
- 📎 Source: `resources/kafka-design-replication.md` (Unclean leader election); `resources/kafka-monitoring-tuning-signals.md` (correct MBean).

### Question 8 — Answer: **B**

- **Why correct:** with ELR enabled the controller elects in the order ISR → ELR → last known leader. The `Elr: 3,4` column says brokers 3 and 4 left the ISR but are still *eligible*: because the high watermark could not advance while `|ISR| = 1 < min.insync.replicas = 2`, they are guaranteed to hold every committed message. Electing one of them restores the partition **without** data loss and **without** enabling unclean leader election.
- **Why the others are wrong:** A — this was the pre-4.0 behaviour; the whole point of KIP-966 Part 1 is that safe non-ISR replicas are now tracked and electable. C — ELR and unclean election are different mechanisms; ELR does not imply or trigger unclean election, and it does not accept data loss. D — a failed broker's log is not "replayed"; leadership must move to another replica for the partition to serve traffic.
- 🧠 **Key point / trap:** "partition needs a leader, no data loss allowed" → **ELR**. "partition needs a leader, data loss acceptable" → unclean election. The `Elr:` column is the tell.
- 📎 Source: `resources/kafka-eligible-leader-replicas.md` (Overview, election order, example describe output).

### Question 9 — Answer: **C**

- **Why correct:** the Operations page lists the controller's order verbatim: "If ISR is not empty, select one of them. If ELR is not empty, select one that is not fenced. Select the last known leader if it is unfenced." That is 3 → 2 → 1.
- **Why the others are wrong:** A and B put a weaker source ahead of the ISR, which would elect a replica that is *not* guaranteed to be caught up even though a fully in-sync one exists. D swaps the last two: the last known leader is the final fallback, used only when both the ISR and the ELR are unusable — it is the pre-4.0 behaviour for "all replicas offline".
- 🧠 **Key point / trap:** memorise the three lines in order. CCAAK's list-order format loves exactly this kind of short, strictly ordered procedure.
- 📎 Source: `resources/kafka-eligible-leader-replicas.md` (Overview).

### Question 10 — Answer: **A**

- **Why correct:** the docs state plainly that when a broker is restarted "it will only be a follower for all its partitions, meaning it will not be used for client reads and writes". Kafka's answer is the preferred replica — the first entry in the partition's `Replicas:` list. With `auto.leader.rebalance.enable=true` (the default) a controller thread re-checks the imbalance every `leader.imbalance.check.interval.seconds` (300 s) and moves leadership back; the manual equivalent is `kafka-leader-election.sh --election-type preferred --all-topic-partitions`.
- **Why the others are wrong:** B — the broker is clearly registered: it appears in `Isr:` for many partitions, and re-formatting would destroy its data. C — `kafka-preferred-replica-election.sh` and the `--zookeeper` flag no longer exist in Kafka 4.x; this is a version trap. D — `UnderReplicatedPartitions` is 0, so the replicas are already caught up; `replica.lag.time.max.ms` is not involved in leadership placement.
- 🧠 **Key point / trap:** "broker restarted, carries no traffic, URP is 0" is always the **preferred-leader** story, and the metric that quantifies it is `PreferredReplicaImbalanceCount`.
- 📎 Source: `resources/kafka-ops-setting-quotas-and-leadership.md` (Balancing leadership); `resources/kafka-broker-configs-replication-throughput.md` (`auto.leader.rebalance.enable`, `leader.imbalance.check.interval.seconds` 300).

### Question 11 — Answer: **D**

- **Why correct:** `offsets.topic.replication.factor` and `transaction.state.log.replication.factor` both default to **3** and `transaction.state.log.min.isr` to **2**. On a single-broker cluster the controller cannot satisfy RF=3 when it first creates the internal topic, so it raises `InvalidReplicationFactorException`. Setting all three to 1 in the broker configuration (and restarting, since they are `read-only`) is the standard fix for single-node development clusters.
- **Why the others are wrong:** A — internal topics do **not** inherit `default.replication.factor`; they have their own dedicated settings, which is exactly why this failure is so common. B — `min.insync.replicas` is a write-admission threshold, not a replication factor; it cannot make a 3-replica topic creatable on one broker. C — creating `__transaction_state` by hand is fragile (partition count, cleanup policy and compaction settings all matter) and the same problem returns for `__consumer_offsets`; fix the configuration instead.
- 🧠 **Key point / trap:** remember the triple **3 / 3 / 2** for internal topics and that a lab cluster must override all three. Note that the *broker* started fine — the error only appeared when a client first needed the internal topic.
- 📎 Source: `resources/kafka-broker-configs-replication-throughput.md` (Nhóm 1 — internal topic defaults and Update Mode).

### Question 12 — Answer: **B, D**

- **Why correct:** B lists the documented defaults — `offsets.topic.replication.factor` 3, `transaction.state.log.replication.factor` 3, `transaction.state.log.min.isr` 2. D captures the operational consequence: all three carry Update Mode `read-only`, so they need a broker restart, and because they are consulted when the internal topic is **created**, changing them on a cluster whose internal topics already exist has no retroactive effect.
- **Why the others are wrong:** A — they are `read-only`, not cluster-wide dynamic; `kafka-configs.sh` cannot change them at runtime. C — `transaction.state.log.min.isr` is described as the overridden `min.insync.replicas` **for the transaction topic**; `__consumer_offsets` is unaffected by it. E — replication factor of an existing topic is only changed by a partition reassignment (`kafka-reassign-partitions.sh`), never by editing the broker default.
- 🧠 **Key point / trap:** "I raised the internal-topic RF but `__consumer_offsets` is still RF=1" is a real production surprise — the setting only applied at creation time.
- 📎 Source: `resources/kafka-broker-configs-replication-throughput.md` (Nhóm 1, with Type / Default / Update Mode columns).

### Question 13 — Answer: **C**

- **Why correct:** KIP-599 added the `controller_mutation_rate` quota precisely for this workload. The Multi-Tenancy page says administrators "can also define quotas on topic operations—such as create, delete, and alter—to prevent Kafka clusters from being overwhelmed by highly concurrent topic operations (see KIP-599 and the quota type `controller_mutation_rate`)". The symptom — controller queue time spiking while bandwidth and CPU are modest — points at metadata mutations, not data-plane traffic.
- **Why the others are wrong:** A and D — byte-rate quotas bound produce/consume throughput; the tenant's data volume is already modest, so they would not touch the create/delete storm. B — `request_percentage` limits time on the broker's network and I/O threads; topic creation is handled by the **controller**, and the bottleneck described is controller queue time.
- 🧠 **Key point / trap:** four quota names to keep straight — two byte rates, one CPU percentage, one **controller mutation rate**. Only the last one governs admin operations.
- 📎 Source: `resources/kafka-design-quotas.md` (Isolating tenants with quotas and rate limits; KIP-599).

### Question 14 — Answer: **A**

- **Why correct:** the broker walks the eight precedence levels and stops at the first match. Connection 1 matches level 1 (user + client-id) → **V**. Connection 2 has no (user, client-id) entry and no (user, default client-id) entry, so it falls to level 3, the plain user quota → **W**. Connection 3's user `reporting` has no quota at any user level, and no default-user entries exist, so it falls through to level 7, the matching client-id → **X**. Connection 4 matches nothing until level 8, the default client-id → **Y**.
- **Why the others are wrong:** B — puts connection 2 on the client-id entry (level 7) even though a user-level quota (level 3) matches first; user-level always outranks client-id-level. C — puts connection 1 on the user quota although a more specific (user, client-id) entry exists. D — ignores the user levels entirely and mis-assigns connections 2 and 4.
- 🧠 **Key point / trap:** the shortcut is "**user beats client-id at every level; within a level, a named entity beats the default**". Levels 1–6 all involve a user (named or default); only 7 and 8 are client-id alone.
- 📎 Source: `resources/kafka-design-quotas.md` (the eight-level precedence list); `resources/kafka-ops-setting-quotas-and-leadership.md` (command-to-level mapping table).

### Question 15 — Answer: **B**

- **Why correct:** the three facts together are the signature of quota throttling — a throughput plateau, seconds of latency, and **no errors anywhere**. The broker "computes the amount of delay needed to bring the violating client under its quota and returns a response with the delay immediately", then mutes the channel; nothing is logged as an error and no exception reaches the application. The confirming evidence is the throttle metric on either side, and the configuration is then found with `kafka-configs.sh --describe --entity-type users`.
- **Why the others are wrong:** A — a full accumulator surfaces as `TimeoutException: … failed to allocate memory within the configured max blocking time`, not as a clean sustained ceiling. C — a saturated request handler pool would show up as `RequestHandlerAvgIdlePercent` below 0.3 and would affect *all* clients on that broker, not one `client.id`. D — records over `message.max.bytes` are rejected with `RecordTooLargeException`, which would appear in the logs; nothing is dropped silently.
- 🧠 **Key point / trap:** "capped throughput + clean logs" ⇒ quota. This is one of the most recognisable symptom patterns in the whole exam.
- 📎 Source: `resources/kafka-design-quotas.md` (Enforcement; quota metrics table).

### Question 16 — Answer: **D**

- **Why correct:** this is the documented enforcement mechanism, almost word for word: the broker computes the delay, returns the response immediately carrying that delay, and mutes the socket channel so it stops processing the client's requests until the delay is over. A modern client also refrains from sending during the delay, so the throttle is applied from both sides — and an old client that ignores the delay is still back-pressured by the muted channel.
- **Why the others are wrong:** A — there is no `QuotaViolationException` returned to clients; quotas deliberately avoid error paths so that well-behaved clients simply slow down. B — the connection is muted, not closed; closing it would cause a metadata storm and would not bound the rate. C — nothing is dropped, so `FailedProduceRequestsPerSec` does not move; the records are accepted, just later.
- 🧠 **Key point / trap:** "delay, don't fail" is the whole design philosophy of Kafka quotas. Any option containing an exception name is wrong.
- 📎 Source: `resources/kafka-design-quotas.md` (Enforcement).

### Question 17 — Answer: **A, D**

- **Why correct:** A restates the documented scope — "This quota is defined on a per-broker basis. Each client can utilize this quota per broker before it gets throttled." Eight brokers × 10 MiB/s gives a cluster-wide ceiling of about 80 MiB/s, so 62 MiB/s with some throttling on each broker is exactly what the configuration asks for. D is the other half of the definition: "All connections of a quota group share the quota configured for the group", so every producer instance with that user and client-id shares one allocation on each broker.
- **Why the others are wrong:** B — the unit is bytes per second; 10485760 is a valid value and is being applied. C — the value is not a cluster-wide ceiling, so nothing is broken; and a rolling restart would change nothing because quotas take effect immediately. E — quotas live in the **metadata log** in KRaft; ZooKeeper was removed in Kafka 4.0, and the docs state the overrides "are read by all brokers and are effective immediately… without having to do a rolling restart".
- 🧠 **Key point / trap:** to cap a tenant at *X* across the cluster, set `X / number_of_brokers` per broker — and remember the value shifts when you add brokers.
- 📎 Source: `resources/kafka-design-quotas.md` (Network Bandwidth Quotas; Enforcement; Quota Configuration).

### Question 18 — Answer: **A**

- **Why correct:** the docs define a request quota of `n%` as "n% of one thread", with total capacity `((num.io.threads + num.network.threads) * 100)%`. With the defaults 8 and 3, capacity is 1100%, and two full threads is `request_percentage=200`.
- **Why the others are wrong:** B — 2% would be 2% of a single thread, roughly one fiftieth of one thread. C — the quota is not a share of the host's whole CPU; it is a share of the broker's request-handling and network threads, and 18% of 1100% would again be far less than two threads. D — network threads are **included** in the capacity formula; the total is `(8 + 3) × 100`, not `8 × 100`.
- 🧠 **Key point / trap:** `request_percentage` values above 100 are normal and expected. Seeing "200" and assuming "that's more than 100%, so it must be invalid" is the trap.
- 📎 Source: `resources/kafka-design-quotas.md` (Request Rate Quotas).

### Question 19 — Answer: **A**

- **Why correct:** `num.replica.fetchers` defaults to **1** — a single fetcher thread per source broker — and it carries Update Mode `cluster-wide`, so it can be raised at runtime with `kafka-configs.sh` and lowered again just as easily. The docs describe exactly this trade-off: more fetchers increase I/O parallelism on both the follower and the leader, at the cost of CPU and memory. With disk and network idle, thread parallelism is the credible bottleneck.
- **Why the others are wrong:** B — `replica.fetch.max.bytes` is `read-only`, so it costs a rolling restart of the whole cluster during an already degraded state; that is neither cheap nor reversible. C — this hides the symptom without replicating a single extra byte, and removes the durability guarantee while the cluster is under-replicated. D — reassignment copies even more data over the same links and is a heavyweight, slow operation; it is the answer for *permanently* lost replicas, not for a broker that is already catching up.
- 🧠 **Key point / trap:** rank actions by cost and reversibility. `num.replica.fetchers` is the canonical "cheap, dynamic, reversible" answer for slow ISR recovery.
- 📎 Source: `resources/kafka-broker-configs-replication-throughput.md` (`num.replica.fetchers`, Update Mode `cluster-wide`).

### Question 20 — Answer: **C**

- **Why correct:** both configs are documented as soft limits. `replica.fetch.max.bytes` (default 1048576, per partition) and `replica.fetch.response.max.bytes` (default 10485760, whole response) each say: "if the first record batch in the first non-empty partition of the fetch is larger than this value, the record batch will still be returned to ensure that progress can be made." The true ceiling on record-batch size is `message.max.bytes` / `max.message.bytes`, which the team has already raised. Increasing the fetch sizes avoids one-batch-per-fetch round trips, which is a throughput matter.
- **Why the others are wrong:** A — replication does not stall; the progress guarantee exists precisely to prevent that deadlock. B — the response limit defaults to **10 MiB**, not 1 MiB; this is a stale-default trap. D — followers use the replica fetch settings; `socket.request.max.bytes` bounds the size of a socket request, and is not a replacement for them.
- 🧠 **Key point / trap:** learn the pair **1 MiB per partition / 10 MiB per response**, and remember "not an absolute maximum" — the same wording appears in the consumer-side `fetch.max.bytes` and `max.partition.fetch.bytes`.
- 📎 Source: `resources/kafka-broker-configs-replication-throughput.md` (Nhóm 3 — follower fetcher).

### Question 21 — Answer: **B**

- **Why correct:** the broker default `compression.type=producer` means "retain the original compression codec set by the producer" — batches are stored exactly as received, so the broker neither decompresses nor recompresses, and it can serve consumers straight from the page cache. Setting an explicit codec forces the broker to decompress and re-compress every incoming batch, which burns CPU with no change in bytes in or messages in, and also defeats the zero-copy send path.
- **Why the others are wrong:** A — `uncompressed` would make the broker *decompress* and store raw; that also costs CPU, but the option's stated reason ("spend CPU compressing every batch") is backwards, and it would visibly change on-disk size and `BytesInPerSec` downstream. C — `producer` is the default, so setting it changes nothing, and it does not alter checksum validation. D — broker-side compression is one of the classic CPU consumers; dismissing it is wrong, and `num.io.threads` would show up as a low `RequestHandlerAvgIdlePercent`, not as a CPU jump with flat traffic.
- 🧠 **Key point / trap:** "CPU up, bytes flat" after a config change points at **re-compression**. Keep `compression.type=producer` on brokers unless you have a specific reason not to.
- 📎 Source: `resources/kafka-broker-configs-replication-throughput.md` (`compression.type`, default `producer`).

### Question 22 — Answer: **C**

- **Why correct:** `RequestHandlerAvgIdlePercent` of 0.08 means the request handler threads are idle only 8% of the time — far under the documented healthy guidance of "between 0 and 1, ideally > 0.3". `NetworkProcessorAvgIdlePercent` of 0.61 shows the network layer has room, and a low mean `RemoteTimeMs` rules out waiting on followers. The targeted fix is more request handler threads, and `num.io.threads` is `cluster-wide`, so it can be raised without a restart.
- **Why the others are wrong:** A — the network processors are 61% idle; adding threads there addresses a bottleneck that does not exist. B — `queued.max.requests` only enlarges the queue in front of the same saturated handlers; requests would wait longer rather than being processed faster, and it is `read-only` anyway. D — `RemoteTimeMs` of 4.2 ms is small; it shows followers are keeping up, so it argues *against* blaming replication. Dropping to `acks=1` would also weaken durability to fix a thread-pool problem.
- 🧠 **Key point / trap:** the **0.3** threshold applies to both idle-percent metrics, and each points at its own config: handler pool → `num.io.threads`, network processors → `num.network.threads`.
- 📎 Source: `resources/kafka-monitoring-tuning-signals.md` (Thread & request pipeline; the derived reflex table).

### Question 23 — Answer: **B**

- **Why correct:** Kafka writes into the OS page cache rather than keeping data on the heap, and Confluent states it "does not require setting heap sizes more than 6 GB. This will result in a file system cache of up to 28-30 GB on a 32 GB machine." A 32 GB heap both lengthens GC pauses — long enough here to stall fetcher threads past `replica.lag.time.max.ms` and trigger the ISR shrinks — and starves the page cache, which is why consumer fetches started hitting disk. Dropping to ~6 GB with G1GC fixes both symptoms at once.
- **Why the others are wrong:** A — a larger heap makes each collection cover more memory and typically lengthens pauses further, while shrinking the page cache even more. C — the serial collector is single-threaded and would make pauses dramatically worse on a 32 GB heap; the documented collector for brokers is **G1GC**. D — raising `replica.lag.time.max.ms` masks the ISR symptom while leaving the 2-second stalls and the cold page cache untouched (and it is `read-only`, so it costs a restart anyway).
- 🧠 **Key point / trap:** "broker is slow → give the JVM more memory" is a trap. For Kafka the heap is small on purpose; the RAM belongs to the page cache.
- 📎 Source: `resources/confluent-production-tuning.md` (Memory — heap 6 GB, page cache 28–30 GB); `resources/kafka-hardware-os-java.md` (Java Version — documented flags).

### Question 24 — Answer: **A, C**

- **Why correct:** A is the argument list printed verbatim in the Java Version page, with `-Xms` equal to `-Xmx` at 6 GB and `-XX:+UseG1GC`. C is the reference data published alongside it: 60 brokers, 50k partitions at replication factor 2, 800k messages/sec, 300 MB/sec inbound and 1 GB/sec+ outbound, with "a 90% GC pause time of about 21ms with less than 1 young GC per second".
- **Why the others are wrong:** B — the documented arguments set `-Xms6g -Xmx6g`, i.e. **equal**, so the heap is fixed and the JVM never resizes it at runtime. D — G1GC is exactly what the documentation prescribes; ZGC is not required or recommended for brokers. E — there is no `broker.heap.bytes` property; the heap comes from the `KAFKA_HEAP_OPTS` environment variable read by the start script.
- 🧠 **Key point / trap:** heap size is **not** a Kafka configuration — it is a JVM environment variable, which is why changing it always means restarting the broker process.
- 📎 Source: `resources/kafka-hardware-os-java.md` (Java Version); `resources/confluent-production-tuning.md` (JVM).

### Question 25 — Answer: **B, D**

- **Why correct:** B is the Apache recommendation word for word — "We recommend at least 100000 allowed file descriptors for the broker processes as a starting point" — because every log segment and every connection consumes descriptors. D is Confluent's guidance on swap: set `vm.swappiness` "to a very low value, such as 1", and explicitly "it is not recommended to use a value of 0, because it would never allow a swap under any circumstances, thus forfeiting the safety net".
- **Why the others are wrong:** A — 0 is the value the documentation warns against; it removes the safety net that keeps the OS from killing the broker under memory pressure. C — the recommended mount option is **`noatime`**, which *disables* access-time updates; Kafka never reads `atime`, and leaving it on adds pointless filesystem writes. E — 1,024 descriptors is the distro default the documentation calls out as far too low for Kafka.
- 🧠 **Key point / trap:** three OS numbers to carry into the exam — fd **100000**, `vm.swappiness` **1**, `vm.max_map_count` (e.g. **262144**, because each log segment costs two map areas).
- 📎 Source: `resources/kafka-hardware-os-java.md` (OS — file descriptor limits, `vm.max_map_count`, `noatime`); `resources/confluent-production-tuning.md` (Tuning virtual memory).

### Question 26 — Answer: **D**

- **Why correct:** the three metrics answer three different questions. `UnderReplicatedPartitions` = 0 means `|ISR| = |all replicas|` everywhere, so no replica is missing. `AtMinIsrPartitionCount` = 17 means seventeen partitions have `|ISR|` exactly equal to `min.insync.replicas` — still writable, but one replica away from blocking. `UnderMinIsrPartitionCount` = 0 confirms nothing is blocked yet. That combination is an early-warning signal, not an outage.
- **Why the others are wrong:** A — rejection of `acks=all` corresponds to `UnderMinIsrPartitionCount` > 0, which is 0 here. B — the three are not mutually exclusive; they measure different comparisons (`|ISR|` vs replica count, vs min-ISR, at min-ISR), and this combination is internally consistent. C — offline partitions are reported by the controller metric `OfflinePartitionsCount`, and unclean election is irrelevant while every partition has a full ISR.
- 🧠 **Key point / trap:** learn the three definitions as three different inequalities. Only `UnderMinIsrPartitionCount` means "writes are being refused right now".
- 📎 Source: `resources/kafka-monitoring-tuning-signals.md` (Replication & ISR table).

### Question 27 — Answer: **C**

- **Why correct:** every clause is documented. XFS outperformed EXT4 in Apache's own comparison — "XFS resulted in much better local times (160ms vs. 250ms+ for the best EXT4 configuration)"; `noatime` is the recommended mount option for data directories; the docs recommend "using multiple drives to get good throughput and not sharing the same drives used for Kafka data with application logs or other OS filesystem activity"; and Confluent's sizing table says explicitly "Separate OS disks from Apache Kafka storage".
- **Why the others are wrong:** A — Confluent lists RAID 5 as **not recommended** (RAID 1/10 preferred, then RAID 0), and sharing the Kafka volume with the OS and application logs is exactly what both vendors warn against. B — the docs advise avoiding file-based NAS: it is slower, has higher and more variable latency, and is a single point of failure. D — disabling journaling and `data=writeback` are listed as EXT4 *tuning* options that are "generally unsafe in a failure scenario" and can cause corruption, not as a safe default.
- 🧠 **Key point / trap:** the pair of numbers **160 ms vs 250 ms+** is the memorable hook for "XFS over EXT4".
- 📎 Source: `resources/kafka-hardware-os-java.md` (Disks and Filesystem; Filesystem Selection; General Filesystem Notes); `resources/confluent-production-tuning.md` (Hardware recommendations; Disks; Filesystem).

### Question 28 — Answer: **B**

- **Why correct:** `num.replica.fetchers` has Update Mode `cluster-wide`, so it is changed live with `kafka-configs.sh --entity-type brokers --entity-default` → **W**. `replica.lag.time.max.ms` is `read-only`, so it requires a configuration edit plus a rolling restart → **X**. A client quota is written to the metadata log and is effective immediately on every broker → **V**. The heap comes from `KAFKA_HEAP_OPTS`, an environment variable outside Kafka's own configuration system, so it needs a process restart → **Y**.
- **Why the others are wrong:** A — swaps 1 and 2, treating the fetcher count as restart-only and the ISR lag timeout as dynamic; the Update Mode column says the opposite. C — makes `replica.lag.time.max.ms` a quota-style change and the quota a restart-only broker config; neither is true. D — swaps the quota and the heap, implying a quota needs a broker restart, which contradicts the documented "effective immediately" behaviour.
- 🧠 **Key point / trap:** when an exam item says "during business hours" or "without restarting brokers", the **Update Mode** column is what eliminates options — read it before the default value.
- 📎 Source: `resources/kafka-broker-configs-replication-throughput.md` (Update Mode on every row); `resources/kafka-design-quotas.md` (Quota Configuration — metadata log, effective immediately).

### Question 29 — Answer: **B**

- **Why correct:** retention deletes whole **segments**, and the active segment — the one currently being appended to — is never a deletion candidate. On a low-traffic topic that segment can stay open for a very long time, because it only rolls when it reaches `segment.bytes` (1 GiB by default) or `segment.ms`. Lowering one of those forces the segment to close, at which point `retention.ms` can act on it.
- **Why the others are wrong:** A — `retention.ms` is the time-based retention for the `delete` cleanup policy; it is compaction that behaves differently, and `retention.bytes` is a *size* limit, not a prerequisite. C — `log.retention.check.interval.ms` defaults to 300000 ms (5 minutes), so the cleaner has run many times in twelve hours. D — a topic-level config overrides the broker default; that is the whole point of topic overrides, and the precedence order puts `DYNAMIC_TOPIC_CONFIG` first.
- 🧠 **Key point / trap:** "retention set, data still there" ⇒ think **active segment**, then `segment.ms` / `segment.bytes`. This is the classic Week 2 carry-over.
- 📎 Source: `../../../CCDAK/study-plan/week-02/resources/kafka-topic-configs.md` (`retention.ms`, `segment.ms`, `segment.bytes`); `../../CCAAK-STUDY-PLAN.md` §7 (row "Retention đặt 1 giờ mà data vẫn còn").

### Question 30 — Answer: **A, C**

- **Why correct:** A and C are the two documented properties of multiple log directories: "If you configure multiple data directories partitions will be assigned round-robin to data directories" (Confluent words it as "the broker places a new partition in the path with the least number of partitions currently stored") and "Each partition will be entirely in one of the data directories. If data is not well balanced among partitions this can lead to load imbalance between disks."
- **Why the others are wrong:** B — Kafka never stripes one partition across directories; striping is what RAID does at a lower level, which is the alternative to JBOD, not how JBOD works. D — with KRaft JBOD a single failed log directory takes only the partitions stored on it offline; the broker keeps serving the rest. E — adding a directory does not move existing partitions; only new partitions land there, and rebalancing existing ones requires a reassignment that specifies log directories.
- 🧠 **Key point / trap:** partitions are distributed by **count**, not by size — which is why one oversized topic can fill a single disk while the others stay half empty. Note also that Confluent Tiered Storage requires a single mount point and therefore cannot be combined with JBOD.
- 📎 Source: `resources/kafka-hardware-os-java.md` (Disks and Filesystem); `resources/confluent-production-tuning.md` (Disks — partition placement, Tiered Storage/JBOD note).

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (24+/30) | Vượt xa ngưỡng checkpoint. | Review 100% câu sai, ghi vào sổ câu sai kèm **lý do sai**. Làm luôn **⭐ MINI-MOCK CFG** (~30 câu trộn Tuần 2 + Tuần 3, 45 phút). Đạt ≥70% thì sang Tuần 4. |
| **70–79%** (21–23/30) | Đạt checkpoint nhưng còn lỗ hổng. | Xác định nhóm yếu nhất trong 5 nhóm (durability / ELR & leader election / quota / throughput tuning / JVM-OS), đọc lại đúng mục đó ở [Buổi A](README.md#-buổi-a--lý-thuyết-3h) và **làm lại lab tương ứng**. Rồi mới chạy mini-mock CFG. |
| **60–69%** (18–20/30) | Chưa qua cổng. | Học lại Buổi A của Tuần 3, vẽ lại **Bảng 1** (ma trận durability) và **Bảng 3** (8 mức quota) từ trí nhớ, làm lại **Lab 3.1, 3.2, 3.4**. Làm lại bộ 30 câu này sau 2 ngày. |
| **< 60%** (≤ 17/30) | **Không** sang Tuần 4. | Quay lại cả Tuần 2 và Tuần 3: đọc `resources/kafka-design-replication.md` và `resources/kafka-design-quotas.md` từ đầu, chạy lại **toàn bộ 7 lab**, rồi mới thử lại. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / dính bẫy version / hết giờ), và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may cũng tính là câu sai.
>
> 🎯 **Cổng bắt buộc của Tuần 3:** đạt **≥70%** ở **MINI-MOCK CFG** (~30 câu trộn ngẫu nhiên từ `week-02/questions.md` và `week-03/questions.md`) mới được sang [Tuần 4](../week-04/README.md).
