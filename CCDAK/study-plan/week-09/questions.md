# 📝 Practice Questions — Week 9: Kafka on AWS (`Amazon MSK`) + Design Patterns

> **28 questions** · 15 tagged `AWS` (Amazon MSK — **outside the CCDAK blueprint**, do not count them toward your CCDAK mock score), 11 tagged `ARCH` (design patterns — CCDAK does ask these as "which design" questions), 2 review questions from Weeks 5 and 8.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (number to choose is stated). AWS parameter and IAM action names are written exactly as in the AWS CLI / IAM documentation.
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

---

### Question 1 — `[AWS · MSK cluster types · Single]`

A fintech team is moving a self-managed Kafka cluster to Amazon MSK. Requirements: the team does **not** want to manage EBS volumes or storage scaling, needs roughly **3× the per-broker write throughput** of their current `kafka.m5.4xlarge` brokers, must keep **mutual TLS** authentication with certificates issued by their private CA, and needs to add brokers within minutes during sales events. Which MSK option meets all requirements?

- A. MSK Serverless, because it removes all broker and storage management
- B. MSK Provisioned with **Express brokers**
- C. MSK Provisioned with Standard brokers and tiered storage enabled
- D. MSK Provisioned with Standard brokers and storage auto-scaling enabled

### Question 2 — `[AWS · MSK cluster types · Single]`

A startup runs a development and QA environment whose Kafka traffic is **unpredictable** (near zero at night, bursts during test runs). They want to be billed **only for the throughput, partitions, and storage they actually use**, with no broker sizing or capacity planning, and all applications already authenticate to AWS services with IAM roles. Which option is the MOST cost-effective fit?

- A. MSK Provisioned with `kafka.t3.small` Standard brokers in 2 Availability Zones
- B. MSK Provisioned with Express brokers and autoscaling
- C. **MSK Serverless**
- D. Amazon Kinesis Data Streams in provisioned mode with 1 shard

### Question 3 — `[AWS · Ports & authentication · Multi — Choose 2]`

A security review lists the listeners that clients use to reach an MSK Provisioned cluster with **IAM access control** and **SASL/SCRAM** both enabled, private connectivity only. Which two statements are correct? (Choose two.)

- A. Clients using IAM access control connect on port **9098**; SASL/SCRAM clients connect on port **9096**
- B. Clients using IAM access control connect on port **9094**; SASL/SCRAM clients connect on port **9092**
- C. The SCRAM credentials must be stored in an AWS Secrets Manager secret whose name begins with **`AmazonMSK_`** and that is encrypted with a **customer-managed KMS key**
- D. The SCRAM credentials can be stored in any Secrets Manager secret as long as it is encrypted with the default `aws/secretsmanager` key
- E. Enabling public access changes the IAM port to 9098 and the SCRAM port to 9096

### Question 4 — `[AWS · IAM client configuration · Single]`

A Java producer must connect to an MSK cluster that only allows IAM access control. The developer has added the `aws-msk-iam-auth` jar to the classpath. Which set of client properties is correct?

- A. `security.protocol=SASL_SSL` · `sasl.mechanism=SCRAM-SHA-512` · `sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;`
- B. `security.protocol=SSL` · `ssl.keystore.location=/etc/msk/keystore.jks` · `sasl.mechanism=AWS_MSK_IAM`
- C. `security.protocol=SASL_SSL` · `sasl.mechanism=AWS_MSK_IAM` · `sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;` · `sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler`
- D. `security.protocol=SASL_PLAINTEXT` · `sasl.mechanism=OAUTHBEARER` · `sasl.login.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler`

### Question 5 — `[AWS · IAM authorization · Single]`

A consumer application running on ECS assumes a role with the following policy and connects to an MSK cluster with IAM access control. The application authenticates successfully but fails with `GroupAuthorizationException: Not authorized to access group: orders-svc`.

```json
{
  "Effect": "Allow",
  "Action": ["kafka-cluster:Connect", "kafka-cluster:DescribeTopic", "kafka-cluster:ReadData"],
  "Resource": [
    "arn:aws:kafka:us-east-1:111122223333:cluster/orders-cluster/*",
    "arn:aws:kafka:us-east-1:111122223333:topic/orders-cluster/*/orders"
  ]
}
```

What is the minimal change that fixes the error?

- A. Add `kafka-cluster:WriteData` on the topic ARN, because consumers commit offsets by writing to `__consumer_offsets`
- B. Add `kafka-cluster:DescribeGroup` and `kafka-cluster:AlterGroup` on `arn:aws:kafka:us-east-1:111122223333:group/orders-cluster/*/orders-svc`
- C. Create a Kafka ACL with `kafka-acls.sh --add --allow-principal User:orders-svc --operation Read --group orders-svc`
- D. Replace the topic ARN wildcard `*` with the real cluster UUID; wildcards are not allowed in the UUID position

### Question 6 — `[AWS · IAM authorization · Multi — Choose 2]`

A platform team enables IAM access control on an MSK cluster running Kafka 3.9. Producers using default client settings (Kafka 4.x Java client) start failing with `ClusterAuthorizationException` even though their role has `kafka-cluster:Connect`, `kafka-cluster:DescribeTopic` and `kafka-cluster:WriteData` on the correct topic ARNs. Separately, an operator adds `Deny` Kafka ACLs with `kafka-acls.sh` to block one IAM role, but the role keeps producing. Which two statements explain these observations? (Choose two.)

- A. Default Kafka 4.x producers are idempotent, so the role also needs `kafka-cluster:WriteDataIdempotently` on the **cluster** ARN
- B. `WriteData` implicitly grants idempotent writes; the failure is caused by a missing `kafka-cluster:AlterCluster` permission
- C. Kafka ACLs have **no effect** on IAM identities; authorization for IAM principals is decided only by IAM policies, so the block must be an IAM `Deny`
- D. Kafka ACLs take effect only after `allow.everyone.if.no.acl.found` is set to `false` in the MSK configuration
- E. Idempotent producers are not supported with IAM access control; set `enable.idempotence=false`

### Question 7 — `[AWS · MSK configuration defaults · Single]`

A developer's application works against a local Kafka 4.3 broker: on first `send()` the topic is created automatically. Against a newly created MSK Provisioned cluster (no custom configuration attached) the same code fails with `UnknownTopicOrPartitionException` and the topic never appears. What is the reason?

- A. MSK requires topics to have `replication.factor=3`, and the client's default `default.replication.factor=1` is rejected
- B. The MSK default configuration sets **`auto.create.topics.enable=false`**, unlike Apache Kafka's default of `true`
- C. IAM access control blocks metadata requests until the topic ARN exists in an IAM policy
- D. MSK disables `delete.topic.enable`, which also prevents topic creation from clients

### Question 8 — `[AWS · MSK Connect · Multi — Choose 2]`

A team wants to run the Debezium PostgreSQL connector against Aurora and write change events into MSK **without managing Kafka Connect workers**. They plan to use MSK Connect. Which two statements are correct? (Choose two.)

- A. The connector plugin is provided as a ZIP or JAR uploaded to **Amazon S3** and registered as a **custom plugin**; the connector then runs on workers measured in **MCUs (1 vCPU + 4 GiB)** with provisioned or autoscaled capacity
- B. MSK Connect exposes the standard Kafka Connect REST API on port 8083 so the team can `PUT /connectors/debezium/pause`
- C. If the connector cannot write to an S3 bucket or read a Secrets Manager secret, the fix is the connector's **service execution role**, not the MSK cluster's IAM policy
- D. MSK Connect requires the source database to be an MSK cluster as well
- E. Worker properties such as `bootstrap.servers`, `group.id` and `offset.storage.topic` must be set in the worker configuration

### Question 9 — `[AWS · MSK Replicator · Multi — Choose 2]`

A company needs cross-Region disaster recovery for an MSK cluster in `us-east-1` with a standby cluster in `us-west-2`. On failover, consumer applications must **resume from where they left off** and must **not change the topic names** in their configuration. The team does not want to operate MirrorMaker 2. Which two configuration choices meet the requirements? (Choose two.)

- A. Create an **MSK Replicator** with **consumer group offset synchronization** enabled
- B. Run MirrorMaker 2 on EC2 with `MirrorCheckpointConnector` and call `RemoteClusterUtils.translateOffsets()` in every consumer
- C. Configure the Replicator with the **Identical topic name** replication option (instead of the default Prefixed option)
- D. Configure the Replicator with the default **Prefixed** option and have every consumer subscribe with the regex `.*orders`
- E. Use Amazon Kinesis Data Streams cross-Region replication, since MSK cannot replicate across Regions

### Question 10 — `[AWS · Monitoring · Single]`

An operator wants CloudWatch alarms on **per-partition consumer lag** (`OffsetLag` for each partition of topic `orders`) for an MSK Provisioned cluster that currently uses the free monitoring level. Which change is required?

- A. Nothing — `OffsetLag` per partition is published at the `DEFAULT` level together with `SumOffsetLag`
- B. Enable **Open Monitoring with Prometheus** (JMX Exporter on port 11001), because CloudWatch never publishes lag metrics
- C. Raise the enhanced monitoring level to **`PER_TOPIC_PER_PARTITION`**
- D. Raise the enhanced monitoring level to `PER_BROKER`, which includes all topic and partition metrics

### Question 11 — `[AWS · Lambda event source mapping · Single]`

A developer creates a Lambda function triggered by an MSK topic `orders` (3 partitions) using an event source mapping with default settings. Which statement about how the function receives data is correct?

- A. MSK brokers push each record to Lambda as it is produced, so `event.records` is always a single record
- B. Lambda **polls** the topic as a consumer group, batches up to **100** records by default, invokes the function **synchronously**, and delivers `event.records` as a map keyed by `"<topic>-<partition>"` whose `value` fields are **base64-encoded**
- C. Lambda reads the topic through Amazon Kinesis Data Streams, so the event has the Kinesis `Records[].kinesis.data` shape
- D. Lambda commits offsets before invoking the function, so a failed invocation skips the batch (at-most-once)

### Question 12 — `[AWS · Lambda event source mapping · Multi — Choose 2]`

The same team observes two problems: (1) the function is invoked for **every** order although it only needs orders whose JSON `value.status` equals `"PAID"`, which wastes invocations; (2) when a single malformed record fails, Lambda **reprocesses the whole batch** repeatedly. Which two changes address these problems with the least custom code? (Choose two.)

- A. Add `FilterCriteria` to the event source mapping with a pattern such as `{"value":{"status":["PAID"]}}` so Lambda drops non-matching records before invocation
- B. Set `BatchSize` to 1 so each invocation contains exactly one record
- C. Enable `FunctionResponseTypes=["ReportBatchItemFailures"]` (returning the failed record identifiers) and configure an on-failure destination (SQS/SNS/S3) for records that exhaust retries
- D. Set `StartingPosition` to `LATEST` so failed batches are skipped automatically
- E. Increase the function timeout to 15 minutes so the batch always completes

### Question 13 — `[AWS · Lambda with self-managed Kafka · Multi — Choose 2]`

A company runs Apache Kafka on EC2 instances in a private VPC, secured with SASL/SCRAM-SHA-512. They create a Lambda event source mapping with `--self-managed-event-source '{"Endpoints":{"KAFKA_BOOTSTRAP_SERVERS":["b-1.internal:9096","b-2.internal:9096"]}}'`. Which two `SourceAccessConfigurations` entries are required for Lambda to reach and authenticate to this cluster? (Choose two.)

- A. `{"Type":"VPC_SUBNET","URI":"subnet-0abc..."}` and `{"Type":"VPC_SECURITY_GROUP","URI":"security_group:sg-0abc..."}` so the Lambda poller can create ENIs in the cluster's VPC
- B. `{"Type":"SASL_SCRAM_512_AUTH","URI":"arn:aws:secretsmanager:...:secret:kafka-scram"}` pointing at a secret with `username`/`password`
- C. `{"Type":"CLIENT_CERTIFICATE_TLS_AUTH","URI":"arn:aws:secretsmanager:..."}` because SCRAM over TLS requires a client certificate
- D. `{"Type":"BASIC_AUTH","URI":"arn:aws:secretsmanager:..."}`, which is the AWS name for SCRAM-SHA-512
- E. No `SourceAccessConfigurations` are needed; Lambda discovers the VPC from the bootstrap server hostnames

### Question 14 — `[AWS · Glue Schema Registry · Single]`

A team producing Avro records to MSK with the `AWSKafkaAvroSerializer` (AWS Glue Schema Registry) hands the topic to a partner team whose consumers use the Confluent `KafkaAvroDeserializer` configured against a Confluent Schema Registry. The consumers fail immediately on deserialization. Why?

- A. Glue Schema Registry supports only JSON Schema, so the records are not Avro
- B. The wire formats differ: Glue prefixes each record with an **18-byte header** (version byte, compression byte, **16-byte schema-version UUID**), whereas Confluent expects **1 magic byte + 4-byte schema ID**; the two serializers are not interchangeable
- C. Glue Schema Registry requires `FULL_ALL` compatibility, which Confluent does not support
- D. Confluent deserializers cannot read records produced with `acks=all`

### Question 15 — `[AWS · MSK vs Kinesis · Single]`

A solutions architect must choose between Amazon Kinesis Data Streams and Amazon MSK for a new platform. Requirements: reuse **existing Kafka Connect connectors and a Kafka Streams application**, keep raw events **for 3 years** for replay, and support **log-compacted** topics for latest-state lookups. Which option is correct?

- A. Kinesis Data Streams with retention extended to 365 days; connectors can be rewritten as Lambda consumers
- B. **Amazon MSK** (Provisioned with tiered storage, or Serverless), because it offers the Kafka API, the Connect/Streams ecosystem, compaction, and unlimited retention
- C. Kinesis Data Streams with enhanced fan-out, because it supports compaction natively
- D. Either service, because Kinesis Data Streams is API-compatible with Apache Kafka

### Question 16 — `[ARCH · Outbox / dual-write · Single]`

An order service does the following in its request handler: `BEGIN; INSERT INTO orders ...; COMMIT;` and then calls `producer.send(new ProducerRecord<>("order-events", orderId, orderCreatedJson))` with `acks=all` and `enable.idempotence=true`. In production, some orders exist in the database with **no corresponding event in Kafka**, and occasionally an event exists for an order that was **rolled back**. Which design eliminates both failure modes?

- A. Wrap `producer.send()` in a Kafka transaction (`transactional.id`) and commit the Kafka transaction after the database commit
- B. Use the **Transactional Outbox** pattern: insert the event into an `outbox` table in the **same database transaction** as the order, and let a CDC connector (for example Debezium with the `EventRouter` SMT) publish outbox rows to Kafka
- C. Set `acks=all` and `min.insync.replicas=2` so the event write cannot be lost
- D. Call `producer.send()` before the database `COMMIT` so the event is guaranteed to exist first

### Question 17 — `[ARCH · Idempotent consumer · Multi — Choose 2]`

A payment consumer reads `order-events` (produced through an outbox relay, so duplicates are possible) and inserts a row into a `payments` table. After a consumer crash and restart, some orders were charged twice. Which two approaches make the consumer idempotent? (Choose two.)

- A. Store each processed **event id** (from the record header/payload) in a `processed_events` table with a primary key, inserting it in the **same database transaction** as the payment; skip the event if the insert conflicts
- B. Switch the consumer to `enable.auto.commit=false` and commit offsets **before** processing, so no record is ever processed twice
- C. Store the last processed `(topic, partition, offset)` in the `payments` database in the same transaction and, on startup, `seek()` each assigned partition to that offset instead of relying on `__consumer_offsets`
- D. Set `isolation.level=read_committed` on the consumer so duplicates produced by the outbox relay are filtered out
- E. Set `enable.idempotence=true` on the outbox relay's producer so the consumer never sees duplicates

### Question 18 — `[ARCH · Retry (Week 4 review) · Single]`

A consumer calls a downstream HTTP API inside `eachMessage`. On HTTP 503 it retries in place with a fixed delay: `Thread.sleep(120_000)` up to 5 times before giving up. Consumer settings are Kafka defaults. During a downstream outage the group **rebalances continuously** and the same records are reprocessed. What is happening and what is the correct fix that **preserves per-partition ordering**?

- A. `session.timeout.ms` (45 s) is exceeded because sleeping blocks heartbeats; fix by raising `heartbeat.interval.ms`
- B. `max.poll.interval.ms` (300 000 ms) is exceeded because 5 × 120 s of blocking retries delays the next `poll()`; fix with **blocking retry using `pause()` on the partition, keep polling, and `resume()` after the backoff** (or raise `max.poll.interval.ms` to cover the worst case)
- C. Publish the failed record to a `retry` topic and continue; ordering is unaffected because the record keeps its original key
- D. Increase `max.poll.records` from 500 to 5 000 so fewer polls are needed

### Question 19 — `[ARCH · Retry & DLQ topics · Single]`

A team implements **non-blocking retries**: records that fail with transient errors are published to `orders-retry-1`, then `orders-retry-2`, and finally `orders-dlq`, each carrying headers `attempts`, `retry-at`, `original-topic`, `original-partition`, `original-offset`. What is the main **trade-off** of this design compared with retrying in place?

- A. Non-blocking retries require exactly-once transactions between the main and retry topics
- B. Records are reprocessed **out of order** relative to later records with the same key, so the design is acceptable only when the business logic tolerates it (or is combined with an ordered-retry key registry)
- C. Kafka limits a topic to one retry topic, so the second level must live in a different cluster
- D. Consumers of the retry topics cannot use `pause()` and must block with `sleep()` until `retry-at`

### Question 20 — `[ARCH · Poison pill · Single]`

A consumer group processing `orders` stalls: one record cannot be deserialized (`SerializationException` from the value deserializer), the consumer logs the error, retries the same offset, and throws again in an endless loop. Which handling is correct?

- A. Increase `max.poll.interval.ms` so the consumer has more time to deserialize the record
- B. Treat the record as a **poison pill**: route it (raw bytes plus error headers) to a dead-letter topic **immediately without retries**, commit past its offset, and alert; retries are reserved for transient failures
- C. Publish the record to `orders-retry-1` with exponential backoff; it will eventually deserialize
- D. Delete the topic and recreate it with `cleanup.policy=compact` so the bad record is removed

### Question 21 — `[ARCH · Partition sizing · Single]`

A topic `clickstream` was created with 48 partitions, but the team measured that 12 partitions comfortably handle the load and the extra partitions increase leader-election time and end-to-end latency. They run `kafka-topics.sh --alter --topic clickstream --partitions 12`. What happens?

- A. The partition count is reduced to 12 after the broker reassigns the data from the removed partitions
- B. The command **fails**: Kafka only allows **increasing** the number of partitions; to reduce, create a new topic with 12 partitions and migrate producers/consumers
- C. The command succeeds but consumers must be restarted to pick up the new count
- D. The command succeeds only if the topic uses `cleanup.policy=compact`

### Question 22 — `[ARCH · Key design · Single]`

An IoT platform keys `telemetry` records by `tenantId` so events of a tenant stay ordered. One tenant generates **40% of all traffic**; its partition's consumer is constantly lagging while other consumers are idle. Ordering is only required **per device**, not per tenant. What is the best fix?

- A. Add more partitions to the topic so the hot tenant's records spread out
- B. Change the key to `deviceId` (the actual ordering unit), which has much higher cardinality and distributes the tenant's load across many partitions while keeping per-device ordering
- C. Remove the key (null key) so the sticky partitioner spreads records evenly
- D. Increase `max.poll.records` on the lagging consumer

### Question 23 — `[ARCH · Fan-out · Single]`

Three microservices (billing, shipping, analytics) each need to receive **every** record from `order-events`. A developer configures all three with `group.id=order-events-consumers` "so they share the load". Billing and shipping start missing orders. What is the correct design?

- A. Publish `order-events` to an Amazon SNS topic and subscribe three SQS queues, because Kafka cannot fan out
- B. Give each service its **own `group.id`**; each consumer group independently receives all records and tracks its own offsets — a Kafka topic is already a durable pub/sub log
- C. Create three copies of the topic (`order-events-billing`, `-shipping`, `-analytics`) and have the producer write three times
- D. Keep one group but set `partition.assignment.strategy=RoundRobinAssignor` so records are duplicated to all members

### Question 24 — `[ARCH · Exactly-once end-to-end · Multi — Choose 2]`

A pipeline reads from PostgreSQL, publishes to Kafka, a Kafka Streams app enriches the records into a second topic, and a final consumer writes to Amazon DynamoDB. Management asks for "exactly-once end to end". Which two statements are correct? (Choose two.)

- A. Setting `processing.guarantee=exactly_once_v2` on the Streams app makes the entire pipeline, including the DynamoDB write, exactly-once
- B. The PostgreSQL → Kafka hop should use **CDC / the outbox pattern** (or a Connect source with `exactly.once.source.support=enabled`) rather than application dual-writes
- C. The Kafka → DynamoDB hop must be made **idempotent by the sink** (for example a conditional `PutItem`/upsert keyed by event id, or storing the processed offset with the item); Kafka transactions do not span external systems
- D. Enabling `enable.idempotence=true` on every producer is sufficient for end-to-end exactly-once
- E. DynamoDB writes become exactly-once when the consumer uses `isolation.level=read_committed`

### Question 25 — `[ARCH · Claim-check · Single]`

A document-processing pipeline must pass scanned PDFs (2–20 MB each) between services through Kafka on MSK Serverless. Which design is recommended?

- A. Raise `max.message.bytes` on the topic to 25 MB and `max.request.size` on the producer accordingly
- B. Use the **claim-check** pattern: upload each PDF to Amazon S3 and publish a small record containing the object key, size and checksum; consumers fetch the object from S3 (the same idea as the SQS Extended Client Library)
- C. Split each PDF into 1 MB chunks published as separate records with a sequence header and reassemble them in the consumer
- D. Compress the PDFs with `compression.type=zstd`, which guarantees they fit under 1 MB

### Question 26 — `[ARCH · Saga & CQRS · Single]`

An e-commerce checkout spans Order, Payment and Inventory services. The team wants a single component to hold the **explicit state** of every checkout, decide the next step, and issue compensating commands (`RefundPayment`, `ReleaseStock`) when a step fails, with all inter-service communication over Kafka. Which pattern matches?

- A. **Saga orchestration**: an orchestrator consumes reply events and publishes command records to each service's command topic; on failure it publishes compensating commands
- B. Saga choreography: each service reacts to the previous service's event and publishes its own; no component holds the overall state
- C. CQRS: the read model in a `KTable` holds the checkout state and decides the next step
- D. Event sourcing with a compacted topic so only the latest checkout state is retained

### Question 27 — `[DEV · Week 5 review · Schema Registry & multi-event topics · Single]`

To preserve ordering between `OrderCreated`, `OrderPaid` and `OrderShipped` events for the same order, a team publishes all three Avro record types to a **single topic** `orders` keyed by `orderId`, using Confluent Schema Registry. Registration of the second record type is rejected as an incompatible schema change. Which configuration fixes this while keeping one topic?

- A. Set `auto.register.schemas=false` and register the schemas manually as one union schema per topic
- B. Change the serializer's subject naming strategy from the default `TopicNameStrategy` to **`RecordNameStrategy`** (or `TopicRecordNameStrategy`), so each record type gets its own subject and compatibility is checked per record type
- C. Set the subject's compatibility to `NONE` for `orders-value` so any schema is accepted
- D. Split into three topics `order-created`, `order-paid`, `order-shipped`; ordering across topics is guaranteed by the shared key

### Question 28 — `[OBS · Week 8 review · Multi-region & offset translation · Single]`

A company replicates `orders` from cluster A to cluster B with MirrorMaker 2 (default Prefixed naming, so the topic becomes `A.orders` on B). During a failover, consumers restarted on cluster B with their last committed offsets from A and reprocessed millions of records. What is the cause and the fix?

- A. MirrorMaker 2 replicates records with the same offsets, so the issue is a consumer bug; set `auto.offset.reset=latest`
- B. Offsets on B differ from offsets on A (records are re-appended on B), so the consumer must use **offset translation**: enable `MirrorCheckpointConnector` (`emit.checkpoints.enabled`, optionally `sync.group.offsets.enabled=true`) and start from the translated offsets via `RemoteClusterUtils.translateOffsets()` or the synced `__consumer_offsets`
- C. Use `IdentityReplicationPolicy` so the topic keeps the name `orders`; identical names make offsets identical
- D. Increase `offsets.retention.minutes` on cluster B so the offsets from A are retained
