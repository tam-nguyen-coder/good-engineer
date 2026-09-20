# ✅ Answers & Explanations — Week 9

> Open only after you have attempted every question in [questions.md](questions.md).
> Reminder: questions tagged `AWS` are **outside the CCDAK blueprint** — track them separately from your CCDAK mock score.
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-AC · 4-C · 5-B · 6-AC · 7-B · 8-AC · 9-AC · 10-C · 11-B · 12-AC · 13-AB · 14-B · 15-B · 16-B · 17-AC · 18-B · 19-B · 20-B · 21-B · 22-B · 23-B · 24-BC · 25-B · 26-A · 27-B · 28-B

---

### Question 1 — Answer: **B**

- **Why correct:** Express brokers are a **Provisioned** broker type: AWS manages storage (no EBS sizing, no storage auto-scaling), each broker delivers roughly **3× the throughput** of the equivalent Standard broker (`express.m7g.16xlarge` ≈ 500 MBps safe write vs ≈ 153.8 MBps), brokers can be added about **20× faster**, and because it is still Provisioned it supports **mTLS** (ACM Private CA), SASL/SCRAM and IAM.
- **Why the others are wrong:** A — MSK Serverless supports **only IAM access control**; mTLS is impossible. C — tiered storage moves cold segments to AWS-managed storage but the team still sizes and manages EBS for hot data, and throughput per broker does not triple. D — storage auto-scaling still means managing EBS and gives no throughput or scaling-speed gain.
- 🧠 **Key point / trap:** "no storage management + high throughput + **still need mTLS/ACLs**" → **Express**, never Serverless.
- 📎 Source: `resources/msk-cluster-types-provisioned-express-serverless.md` (Express brokers section); README §2 table.

### Question 2 — Answer: **C**

- **Why correct:** MSK Serverless has no broker sizing: pricing is per **throughput (GB in/out) + partition-hours + storage**, it scales automatically with bursty traffic, and it requires **IAM access control**, which the applications already use. Quotas (200 MBps in / 400 MBps out per cluster, 2 400 partitions) are far above a dev/QA workload.
- **Why the others are wrong:** A — `t3.small` brokers are billed **per broker-hour** even at zero traffic and need capacity planning (and `t3` has a 4 connections/s IAM limit). B — Express brokers are billed per broker-hour and are the premium option for high throughput, not for idle dev clusters. D — Kinesis is not Kafka; the applications would need rewriting, and a provisioned shard is billed hourly too.
- 🧠 **Key point / trap:** "pay only for what you use, unpredictable load, IAM already in place" → **Serverless**.
- 📎 Source: `resources/msk-cluster-types-provisioned-express-serverless.md` (MSK Serverless + quota); README §2.

### Question 3 — Answer: **A, C**

- **Why correct:** MSK listener ports are fixed: **9092** plaintext, **9094** TLS, **9096** SASL/SCRAM, **9098** IAM (A). SCRAM secrets must live in Secrets Manager with a name prefixed **`AmazonMSK_`** and be encrypted with a **customer-managed KMS key**; the default `aws/secretsmanager` key is rejected when associating the secret (C).
- **Why the others are wrong:** B — 9094 is TLS/mTLS and 9092 is plaintext. D — the default KMS key is explicitly not allowed. E — public access uses **+100** ports: 9198 for IAM, 9196 for SCRAM, 9194 for TLS.
- 🧠 **Key point / trap:** memorize **9092 / 9094 / 9096 / 9098** and public **9194 / 9196 / 9198**; SCRAM = `AmazonMSK_` + customer KMS key.
- 📎 Source: `resources/msk-cluster-types-provisioned-express-serverless.md` (Ports); README §3–4.

### Question 4 — Answer: **C**

- **Why correct:** IAM access control for the Java client requires the four properties: `security.protocol=SASL_SSL`, `sasl.mechanism=AWS_MSK_IAM`, `sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;` and `sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler`, with the `aws-msk-iam-auth` jar on the classpath. Connect on port 9098.
- **Why the others are wrong:** A — mixes the SCRAM mechanism with the IAM login module. B — `SSL` protocol with a keystore is the mTLS setup; `sasl.mechanism` is ignored without SASL. D — `SASL_PLAINTEXT` is not allowed (IAM requires TLS); the `OAUTHBEARER` mechanism is what **non-Java** clients use with a signer library, and the property name is wrong for the Java IAM library.
- 🧠 **Key point / trap:** Java = `AWS_MSK_IAM` + `IAMLoginModule` + `IAMClientCallbackHandler`; Node/Python/Go = `OAUTHBEARER` + `aws-msk-iam-sasl-signer-*`.
- 📎 Source: `resources/msk-iam-access-control.md` (client configuration); README §4.

### Question 5 — Answer: **B**

- **Why correct:** In MSK IAM access control every action has **required actions**. `kafka-cluster:ReadData` requires `Connect`, `DescribeTopic` **and `AlterGroup`**; `AlterGroup` in turn requires `DescribeGroup`. Both group actions target the **group ARN** `arn:aws:kafka:<region>:<account>:group/<cluster>/<uuid>/<group>`. The policy has no group resource at all, hence `GroupAuthorizationException`.
- **Why the others are wrong:** A — offset commits are covered by `AlterGroup`, not `WriteData`; consumers never need write permission on the data topic. C — Kafka ACLs have **no effect** on IAM identities. D — `*` in the UUID position is valid (`topic/orders-cluster/*/orders`).
- 🧠 **Key point / trap:** consumer = `Connect` + `DescribeTopic` + `ReadData` (topic ARN) + `DescribeGroup` + `AlterGroup` (group ARN). `AlterGroup` ≈ Kafka ACL `READ` on `Group`.
- 📎 Source: `resources/msk-iam-access-control.md` (Required actions table, resource ARNs).

### Question 6 — Answer: **A, C**

- **Why correct:** Since Kafka 3.0 `enable.idempotence=true` is the producer default; an idempotent producer needs the `InitProducerId` path, which under IAM maps to **`kafka-cluster:WriteDataIdempotently` on the cluster ARN** (A). Kafka ACLs created with `kafka-acls.sh` are stored but **ignored for IAM principals**; only IAM policies (including explicit `Deny`) decide authorization (C).
- **Why the others are wrong:** B — `WriteData` does not include idempotent writes, and `AlterCluster` is an admin action. D — `allow.everyone.if.no.acl.found` has **no effect** on clusters using IAM access control. E — idempotent producers work fine with IAM; disabling idempotence weakens delivery guarantees for no reason.
- 🧠 **Key point / trap:** default producer on IAM cluster → remember **`WriteDataIdempotently` (cluster ARN)**; to block an IAM role use an IAM `Deny`, not ACLs.
- 📎 Source: `resources/msk-iam-access-control.md` (Important considerations; WriteDataIdempotently required actions).

### Question 7 — Answer: **B**

- **Why correct:** The MSK default configuration deliberately differs from Apache Kafka: **`auto.create.topics.enable=false`** (Kafka default `true`), plus `default.replication.factor=3` and `min.insync.replicas=2` for 3-AZ clusters. Topics must be created explicitly (CLI/Admin API/Terraform) or a custom MSK configuration with `auto.create.topics.enable=true` must be attached.
- **Why the others are wrong:** A — a client does not set `default.replication.factor`; that is a broker property, and auto-created topics would simply use MSK's default of 3. C — IAM policies gate actions such as `CreateTopic`, but the described cluster has no IAM issue; the failure would be an authorization exception, not a silent no-op. D — `delete.topic.enable` controls deletion only.
- 🧠 **Key point / trap:** MSK defaults that differ: `auto.create.topics.enable=false`, RF=3/min.isr=2 (3 AZ), `unclean.leader.election.enable=true`, `num.network.threads=5`.
- 📎 Source: `resources/msk-configuration-and-monitoring.md` (Default Amazon MSK configuration).

### Question 8 — Answer: **A, C**

- **Why correct:** MSK Connect resources are **custom plugin** (ZIP/JAR in **S3**), **worker configuration**, and **connector**; capacity is expressed in **MCUs = 1 vCPU + 4 GiB**, either provisioned or autoscaled on CPU utilization (A). Access to AWS resources (S3 buckets, Secrets Manager, the MSK cluster via IAM) is granted through the connector's **service execution role** (C).
- **Why the others are wrong:** B — MSK Connect does **not** expose the Kafka Connect REST API; management goes through `aws kafkaconnect create/describe/update/delete-connector`. D — the source system can be anything reachable from the VPC (Aurora, on-prem via VPN, etc.); only the Kafka side must be reachable from the VPC. E — `bootstrap.servers`, `group.id`, internal storage topics, `rest.*` and security properties are **set by AWS** and cannot be overridden in a worker configuration.
- 🧠 **Key point / trap:** "Debezium/S3 sink without managing workers" → MSK Connect; permission errors → **service execution role**; there is **no port 8083**.
- 📎 Source: `resources/msk-connect.md` (connectors, capacity, worker configuration, quotas).

### Question 9 — Answer: **A, C**

- **Why correct:** MSK Replicator is the managed alternative to MirrorMaker 2 for same-Region and cross-Region replication. **Consumer group offset synchronization** copies committed offsets to the target so consumers resume where they left off (A). The **Identical topic name** option keeps `orders` as `orders` on the target (loop prevention via the `__mskmr` header), so clients need no configuration change on failover (C).
- **Why the others are wrong:** B — that is the self-managed MirrorMaker 2 approach the team wants to avoid, and it requires consumer code changes. D — Prefixed naming produces `<alias>.orders`, forcing every consumer to change its subscription to a regex; it is meant for active-active setups. E — MSK Replicator exists precisely for cross-Region replication; Kinesis is unrelated.
- 🧠 **Key point / trap:** "cross-Region DR + resume at the same offset + no topic rename" → **Replicator + offset sync + Identical topic name**.
- 📎 Source: `resources/msk-replicator.md` (topic naming, offset sync).

### Question 10 — Answer: **C**

- **Why correct:** CloudWatch monitoring levels nest: `DEFAULT` ⊂ `PER_BROKER` ⊂ `PER_TOPIC_PER_BROKER` ⊂ `PER_TOPIC_PER_PARTITION`. Consumer-group-level lag (`EstimatedMaxTimeLag`, `MaxOffsetLag`, `SumOffsetLag`) is free at `DEFAULT`, but **per-partition** `OffsetLag` / `EstimatedTimeLag` is published only at **`PER_TOPIC_PER_PARTITION`** (billable).
- **Why the others are wrong:** A — `DEFAULT` has only the aggregated lag metrics. B — CloudWatch does publish lag metrics; Open Monitoring is for Prometheus/Grafana and is not required. D — `PER_BROKER` adds broker-level metrics (request handler idle, throttling, IAM connections), not per-partition lag.
- 🧠 **Key point / trap:** "per-partition lag in CloudWatch" → **`PER_TOPIC_PER_PARTITION`**; group-level lag is already free.
- 📎 Source: `resources/msk-configuration-and-monitoring.md` (metric levels, consumer lag metrics).

### Question 11 — Answer: **B**

- **Why correct:** An MSK event source mapping works like the SQS/Kinesis mappings from DVA-C02: Lambda **polls** the topic as a consumer group, reads each partition sequentially, batches up to **`BatchSize` = 100** records (max 10 000, `MaximumBatchingWindowInSeconds` up to 300 s), and **synchronously invokes** the function. The payload is `records: { "orders-0": [ {topic, partition, offset, timestamp, key, value, headers} ], ... }` with **base64** key/value; offsets are committed **after** a successful invocation (at-least-once).
- **Why the others are wrong:** A — Kafka brokers never push; there is no per-record push. C — Kinesis is not involved; the event shape is MSK-specific. D — offsets are committed after processing; a failing batch is retried (until success, record expiry, or an on-failure destination), so the semantics are at-least-once, not at-most-once.
- 🧠 **Key point / trap:** Lambda **poll**, batch 100/10 000, `records` is a **map keyed by `topic-partition`**, values are **base64**, function timeout ≤ **14 min**.
- 📎 Source: `resources/lambda-msk-event-source-mapping.md` (example event, parameters table).

### Question 12 — Answer: **A, C**

- **Why correct:** **Event filtering** (`FilterCriteria`) evaluates patterns against the decoded JSON `value` (and `key`/`headers`) inside the poller, so non-matching records never invoke the function and are not billed (A). For partial batch failures, **`ReportBatchItemFailures`** lets the function return only the failed record identifiers so Lambda retries from that point, and an **on-failure destination** (SQS/SNS/S3) captures records that exhaust `MaximumRetryAttempts` (C). `BisectBatchOnFunctionError` is the other supported knob.
- **Why the others are wrong:** B — `BatchSize=1` multiplies invocations and cost and does not remove the retry loop for a permanently bad record. D — `StartingPosition` is read only when the group has no committed offset; it does not skip failures. E — Kafka event source mappings cap the function timeout at **14 minutes** and a longer timeout does not fix a malformed record.
- 🧠 **Key point / trap:** "only invoke for matching events" → `FilterCriteria`; "one bad record blocks the batch" → `ReportBatchItemFailures` + on-failure destination, and keep the handler idempotent.
- 📎 Source: `resources/lambda-msk-event-source-mapping.md` (FilterCriteria, error handling controls, DestinationConfig).

### Question 13 — Answer: **A, B**

- **Why correct:** For a **self-managed** Kafka source Lambda cannot infer networking, so `VPC_SUBNET` and `VPC_SECURITY_GROUP` entries are required for the poller to create ENIs in the cluster VPC (A). Authentication uses `SASL_SCRAM_512_AUTH` (or `SASL_SCRAM_256_AUTH`) pointing at a Secrets Manager secret containing `username` and `password` (B).
- **Why the others are wrong:** C — `CLIENT_CERTIFICATE_TLS_AUTH` is for mTLS; SCRAM over TLS needs no client certificate (at most `SERVER_ROOT_CA_CERTIFICATE` for a private CA). D — `BASIC_AUTH` is SASL/PLAIN, not SCRAM. E — only for **MSK** sources does Lambda take the VPC from the cluster; self-managed sources must declare it.
- 🧠 **Key point / trap:** self-managed ESM = `VPC_SUBNET` + `VPC_SECURITY_GROUP` + one auth type (`SASL_SCRAM_512_AUTH` / `BASIC_AUTH` / `CLIENT_CERTIFICATE_TLS_AUTH`), optional `SERVER_ROOT_CA_CERTIFICATE`.
- 📎 Source: `resources/lambda-msk-event-source-mapping.md` (self-managed Apache Kafka section).

### Question 14 — Answer: **B**

- **Why correct:** Glue Schema Registry serializers write an **18-byte header** (1 byte version = 3, 1 byte compression flag, **16-byte schema version UUID**) before the Avro payload. Confluent serializers write **1 magic byte (0) + 4-byte schema ID** (5 bytes). A Confluent deserializer reading a Glue-encoded record misreads the header and fails. A converting step (or a common registry) is required.
- **Why the others are wrong:** A — Glue supports Avro, JSON Schema and Protobuf. C — Glue's default compatibility is `BACKWARD`; compatibility modes affect registration, not the wire format. D — `acks` is a producer durability setting unrelated to serialization.
- 🧠 **Key point / trap:** Glue **18 bytes / UUID** vs Confluent **5 bytes / int ID** → not interchangeable; Glue has no Confluent-compatible REST API or subject naming strategies.
- 📎 Source: `resources/glue-schema-registry.md` (wire format comparison); Week 5 wire format.

### Question 15 — Answer: **B**

- **Why correct:** The requirements are exactly what the Kafka ecosystem provides: existing **Connect connectors and Kafka Streams** run unchanged only against a Kafka API, **log compaction** is a Kafka topic feature, and **multi-year retention** is possible with tiered storage on Standard brokers or the unlimited retention of MSK Serverless.
- **Why the others are wrong:** A — Kinesis retention tops out at **365 days** and has no Connect/Streams compatibility; rewriting connectors is exactly the migration cost to avoid. C — Kinesis has no compaction. D — Kinesis is **not** Kafka-API compatible.
- 🧠 **Key point / trap:** "Kafka ecosystem / compaction / retention > 365 days" → **MSK**; "simple AWS-native stream, minimal ops" → **Kinesis**.
- 📎 Source: README §9 (MSK vs Kinesis decision table); `resources/msk-cluster-types-provisioned-express-serverless.md`.

### Question 16 — Answer: **B**

- **Why correct:** This is the **dual-write** problem: a database commit and a Kafka `send()` are two non-atomic operations, so a crash between them loses the event, and sending before a later rollback creates a phantom event. The **Transactional Outbox** writes the event into an `outbox` table **inside the same local transaction**; a relay (Debezium log-tailing CDC with the `EventRouter` SMT: `aggregatetype` → topic, `aggregateid` → key, `id` → header) publishes it. Events exist **iff** the transaction committed. Consumers must be idempotent (at-least-once relay).
- **Why the others are wrong:** A — Kafka transactions are atomic only across **Kafka partitions and offsets**; they cannot include a PostgreSQL commit. C — `acks=all`/`min.insync.replicas` protect against broker loss, not against the application crashing between the two writes. D — sending first produces phantom events whenever the database transaction rolls back.
- 🧠 **Key point / trap:** "DB update and event publish must be atomic" → **Outbox + CDC**, never `acks=all` or Kafka transactions.
- 📎 Source: `resources/transactional-outbox-debezium.md` (pattern + EventRouter SMT).

### Question 17 — Answer: **A, C**

- **Why correct:** Both are textbook **idempotent consumer** implementations. (A) Dedup by **event id** inside the same DB transaction as the business write: a duplicate hits the primary-key conflict and is skipped; crash safety comes from the shared transaction (same idea as a DynamoDB conditional write with `attribute_not_exists(eventId)`). (C) Store the processed **`(topic, partition, offset)`** in the sink database with the business row and `seek()` there on startup; this dedups even after an offset reset because the source of truth is the sink, not `__consumer_offsets`.
- **Why the others are wrong:** B — committing **before** processing gives at-most-once: duplicates disappear but records processed during a crash are lost. D — `read_committed` filters **aborted transactional** records, not duplicate committed records from a relay. E — producer idempotence only removes duplicates from that producer's own internal retries within a session; a relay that restarts and republishes an outbox row creates a new, distinct produce.
- 🧠 **Key point / trap:** Kafka is at-least-once → dedup by **eventId** or **offset stored with the result**, or make the write an **upsert**.
- 📎 Source: README §13 (Idempotent consumer); `resources/transactional-outbox-debezium.md` (consumer must be idempotent).

### Question 18 — Answer: **B**

- **Why correct:** Blocking for up to 5 × 120 s = 600 s inside the processing loop means the consumer does not call `poll()` within **`max.poll.interval.ms` = 300 000 ms (5 min)**, so the coordinator considers it dead and rebalances, its partitions move, and the records are reprocessed. Heartbeats (`session.timeout.ms` 45 s) are sent by a background thread and are **not** the issue. The ordering-preserving fix is **blocking retry done right**: `pause()` the partition, keep calling `poll()` (which returns nothing for paused partitions but keeps the member alive), and `resume()` after the backoff — or size `max.poll.interval.ms` above the worst-case retry budget.
- **Why the others are wrong:** A — heartbeats continue during `sleep()`; the failure is poll-interval based. C — publishing to a retry topic is **non-blocking** retry and does **not** preserve ordering relative to later records with the same key. D — `max.poll.records` changes batch size, not the interval budget; more records per poll makes the overrun more likely.
- 🧠 **Key point / trap:** long in-place retries → `max.poll.interval.ms`, not `session.timeout.ms`; use **`pause()`/`resume()`** instead of `sleep()`.
- 📎 Source: `resources/kafka-error-handling-retry-dlq.md` (blocking vs non-blocking retry); Week 4 README (poll loop, `max.poll.interval.ms`).

### Question 19 — Answer: **B**

- **Why correct:** With retry topics, the failed record leaves the main partition and is processed later, while subsequent records with the **same key** are processed immediately from the main topic. Ordering per key is therefore lost. Confluent's guidance: use non-blocking retries only when the domain tolerates reordering, or implement **ordered retries** (a registry of keys currently in retry so later records with the same key are diverted to the retry path too).
- **Why the others are wrong:** A — transactions are not required; the retry producer can be plain at-least-once, since consumers are idempotent. C — any number of retry topics is allowed in the same cluster. D — retry-topic consumers typically **`pause()`** the partition until `retry-at` (exactly the recommended way to wait without breaking `max.poll.interval.ms`).
- 🧠 **Key point / trap:** non-blocking retry = **no head-of-line blocking, but per-key ordering lost**; blocking retry = ordering kept, partition blocked.
- 📎 Source: `resources/kafka-error-handling-retry-dlq.md` (Pattern 3 Retry topic, Pattern 4 Ordered retries).

### Question 20 — Answer: **B**

- **Why correct:** A record that fails deserialization will fail identically on every attempt — a **poison pill**. Retrying is pointless and blocks the partition (and, done in place, risks exceeding `max.poll.interval.ms`). The correct handling is to capture the **raw bytes** (use a `ByteArrayDeserializer` or an error-handling deserializer wrapper), publish them to a **dead-letter topic** with headers (`original-topic`, `partition`, `offset`, `error`, `timestamp`), commit past the offset, and alert for manual inspection. Kafka Connect sinks (`errors.tolerance=all` + `errors.deadletterqueue.topic.name`) and Kafka Streams (`DeserializationExceptionHandler`) offer the same behavior built in.
- **Why the others are wrong:** A — more time does not make invalid bytes valid. C — exponential backoff is for **transient** errors (503, timeouts), not for permanent ones. D — deleting the topic destroys all data; compaction does not remove a record whose key is not overwritten.
- 🧠 **Key point / trap:** deserialization/validation failure → **DLQ immediately, no retry**; transient downstream failure → retry with backoff.
- 📎 Source: `resources/kafka-error-handling-retry-dlq.md` (Dead Letter Queue pattern, poison pill); Week 5 Connect DLQ.

### Question 21 — Answer: **B**

- **Why correct:** Kafka's `--alter --partitions N` only accepts **N greater than the current count**; the broker rejects a decrease with `InvalidPartitionsException` ("Topic currently has 48 partitions, which is higher than the requested 12"). Reducing would require merging partition logs and rewriting offsets, which Kafka never does. The only path is a **new topic** with the desired count and a producer/consumer migration.
- **Why the others are wrong:** A — no data movement or merge exists for shrinking. C and D — the command does not succeed under any policy.
- 🧠 **Key point / trap:** partitions can be **increased, never decreased**; and increasing changes key → partition mapping (Week 3). Size carefully up front.
- 📎 Source: README §16 (Partition count sizing); Week 3 README (adding partitions changes the hash mapping).

### Question 22 — Answer: **B**

- **Why correct:** The key defines both the **ordering unit** and the **parallelism unit**. Since ordering is only required per device, key by **`deviceId`**: the hot tenant's traffic is spread over many partitions (high cardinality) while each device's events remain in one partition, in order. This is the general "choose the smallest key that still satisfies the ordering requirement" rule; salting (`tenantId#n`) is the fallback when no natural finer key exists.
- **Why the others are wrong:** A — more partitions do not help: all of the tenant's records still hash to **one** partition, and adding partitions remaps every other key too. C — a null key (sticky partitioner) destroys per-device ordering. D — `max.poll.records` cannot make one consumer outrun a partition receiving 40% of the traffic.
- 🧠 **Key point / trap:** hot key → **finer-grained key** or **salt**; never "just add partitions".
- 📎 Source: README §15 (Key design); Week 3 README (partitioner, hot keys).

### Question 23 — Answer: **B**

- **Why correct:** A Kafka topic is a durable **pub/sub log**: every **consumer group** receives every record and maintains its own offsets. Fan-out to N services = N distinct `group.id` values on the same topic. With a shared `group.id`, the three services form **one** group and the partitions are **divided** among them, so each service sees only a subset — exactly the observed missing orders.
- **Why the others are wrong:** A — Kafka fans out natively; SNS/SQS is the pattern for services that lack pub/sub. C — triples storage and reintroduces multi-write consistency problems. D — assignors distribute partitions among members; no assignor duplicates records to all members.
- 🧠 **Key point / trap:** "every service needs all events" → **one consumer group per service**; shared `group.id` = load sharing, not fan-out.
- 📎 Source: README §18 (Fan-out); Week 4 README (consumer groups).

### Question 24 — Answer: **B, C**

- **Why correct:** End-to-end exactly-once is assembled hop by hop. **DB → Kafka**: avoid dual-writes; use **CDC/outbox** or a Connect source with `exactly.once.source.support=enabled` + `exactly.once.support=required` (B). **Kafka → external sink**: Kafka transactions stop at the Kafka boundary, so the sink must be **idempotent** — conditional `PutItem` on an event id, upsert by key, or storing the consumed offset together with the item (C). The middle hop (Kafka → Kafka) is covered by Streams `exactly_once_v2`.
- **Why the others are wrong:** A — `exactly_once_v2` covers only Kafka → Kafka processing (input offsets + output records in one transaction); the DynamoDB write is outside. D — producer idempotence only deduplicates a producer's own retries within a session, per partition. E — `read_committed` hides aborted transactional records; it does nothing for the sink's own retries.
- 🧠 **Key point / trap:** EOS = **transactions (K→K) + idempotent sink (K→external) + CDC/outbox (external→K)**; there is no single switch.
- 📎 Source: README §17 (EOS end-to-end table); Week 3 README (transactions limits); Week 5 README (exactly-once source).

### Question 25 — Answer: **B**

- **Why correct:** Large binary payloads belong in object storage; Kafka carries a **claim check** (S3 bucket/key, size, checksum, content type). Topics stay small and fast, broker memory and replication are unaffected, and consumers fetch the object only when needed. This is the same design as the **SQS Extended Client Library** (payload in S3, pointer in the queue). Remember an S3 lifecycle rule at least as long as the topic retention.
- **Why the others are wrong:** A — MSK Serverless caps `max.message.bytes` at **8 MiB**, and even on Provisioned, multi-megabyte records hurt broker heap, batching and replication. C — chunking adds reassembly complexity and ordering/partial-failure handling for no benefit. D — scanned PDFs are already compressed images; `zstd` cannot guarantee any size bound.
- 🧠 **Key point / trap:** "large payload through Kafka" → **claim-check (S3 + pointer)**, not bigger `message.max.bytes`.
- 📎 Source: README §18 (Claim-check); `resources/msk-cluster-types-provisioned-express-serverless.md` (Serverless 8 MiB limit).

### Question 26 — Answer: **A**

- **Why correct:** A component that **holds the saga state**, tells each participant what to do via **commands**, consumes their **replies**, and issues **compensating commands** on failure is the **orchestrator** in the saga orchestration style. Over Kafka this means a command topic per service (`payment-commands`, `inventory-commands`) and reply/event topics the orchestrator consumes, often implemented as a Kafka Streams state machine or a service with a persistent saga table — the analogue of AWS Step Functions.
- **Why the others are wrong:** B — choreography has **no** central state holder; each service reacts to events and there is no single place that decides compensation. C — CQRS separates read and write models; a `KTable` read model does not issue commands. D — event sourcing stores history; a compacted topic keeps only the latest value and cannot serve as a decision-making coordinator.
- 🧠 **Key point / trap:** "central component decides next step and compensations" → **orchestration**; "services react to each other's events" → **choreography**.
- 📎 Source: README §12 (Saga table); Ben Stopford, *Designing Event-Driven Systems*.

### Question 27 — Answer: **B**

- **Why correct:** The default **`TopicNameStrategy`** derives the subject from the topic (`orders-value`), so all record types in `orders` share one subject and the second Avro record type is an incompatible change under `BACKWARD`. **`RecordNameStrategy`** (subject = fully-qualified record name) or **`TopicRecordNameStrategy`** (`<topic>-<record name>`) gives each event type its own subject and compatibility lineage, enabling the **multi-event topic** design that preserves per-`orderId` ordering.
- **Why the others are wrong:** A — a union schema works but forces every producer to evolve one giant schema and gives up per-type compatibility; `auto.register.schemas=false` alone changes nothing. C — `NONE` disables all safety and still produces one confusing subject. D — separate topics **destroy** cross-event ordering: ordering is guaranteed only within a partition of a single topic; a shared key across topics means nothing.
- 🧠 **Key point / trap:** "several event types in one topic (for ordering)" → **`RecordNameStrategy` / `TopicRecordNameStrategy`**; `TopicNameStrategy` = one schema lineage per topic.
- 📎 Source: Week 5 README (subject naming strategies); README §17 (schema-per-topic vs multi-event topic).

### Question 28 — Answer: **B**

- **Why correct:** MirrorMaker 2 **re-produces** records on the target cluster, so a record at offset 1 000 000 on A may be at offset 998 500 on `A.orders` in B (different compaction, retention, transaction markers, replication start point). Consumers must **translate** offsets: `MirrorCheckpointConnector` emits checkpoints (`A.checkpoints.internal`) mapping source group offsets to target offsets; applications use `RemoteClusterUtils.translateOffsets()` or enable `sync.group.offsets.enabled=true` so MM2 writes translated offsets straight into the target's `__consumer_offsets` for idle groups. MSK Replicator's **consumer group offset sync** does the same job managed.
- **Why the others are wrong:** A — offsets are **not** preserved across clusters; `latest` would skip records instead of reprocessing them (data loss). C — `IdentityReplicationPolicy` keeps the topic **name**; it does not make offsets identical. D — the offsets committed on A were never present on B; retention on B is irrelevant.
- 🧠 **Key point / trap:** cross-cluster failover → **offset translation** (MM2 checkpoints / Replicator offset sync); offsets are per cluster, never portable.
- 📎 Source: Week 8 README (MirrorMaker 2, checkpoints); `resources/msk-replicator.md` (offset synchronization).
