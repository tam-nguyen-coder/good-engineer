# 📝 Practice Questions — Week 5: Schema Registry & Serialization + Kafka Connect

> **30 questions** · real CCDAK exam style, difficulty ≥ real exam · covers the full Week 5 material (Schema Registry, serialization, Kafka Connect) plus 2 review questions from Weeks 3–4.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

---

### Question 1 — `[DEV · Schema Registry · Single]`

A developer runs `kafka-console-consumer.sh --topic orders --from-beginning` against a topic produced by a Java application that uses `KafkaAvroSerializer` with Schema Registry. Every line printed starts with a few unreadable characters followed by binary-looking data. Nothing in the producer logs indicates an error. What is the MOST likely explanation?

- A. The topic is compressed with `zstd` and the console consumer cannot decompress it; set `compression.type=none` on the producer
- B. The records use the Schema Registry wire format (a magic byte plus a 4-byte schema ID before the Avro payload); the plain console consumer does not understand it, so use `kafka-avro-console-consumer` or a consumer configured with `KafkaAvroDeserializer`
- C. The producer's `value.serializer` is misconfigured and is writing Java-serialized objects instead of Avro
- D. The broker's `message.format.version` is newer than the console consumer; upgrade the CLI tools

### Question 2 — `[DEV · Schema Registry · Single]`

A subject `payments-value` uses the default compatibility level. A developer adds a new field `currency` of type `string` (no default value) to the Avro schema and registers it with `POST /subjects/payments-value/versions`. Schema Registry returns **HTTP 409**. Which change to the schema resolves the error while keeping the default compatibility level?

- A. Change the field type to `["string", "null"]` so it can be omitted
- B. Rename the subject to `payments-value-v2` and register the schema there
- C. Give the new field a default value, for example `"type": ["null", "string"], "default": null`
- D. Set `auto.register.schemas=true` on the producer so the serializer registers the schema itself

### Question 3 — `[DEV · Schema Registry · Single]`

A team sets compatibility to `FORWARD` on subject `clicks-value`. They plan to add a new required field to the schema. In which order MUST they roll out the change so that no consumer breaks?

- A. Upgrade all producers to the new schema first, then upgrade consumers
- B. Upgrade all consumers to the new schema first, then upgrade producers
- C. The order does not matter because `FORWARD` is symmetric
- D. Upgrade producers and consumers at exactly the same time using a maintenance window

### Question 4 — `[DEV · Schema Registry · Multi — Choose 2]`

A subject is configured with `FULL` compatibility. Which TWO schema changes will be accepted by Schema Registry? (Choose two.)

- A. Adding a new field that has a default value
- B. Adding a new field without a default value
- C. Changing a field's type from `int` to `string`
- D. Removing an existing field that has a default value
- E. Removing an existing field that has no default value

### Question 5 — `[DEV · Schema Registry · Single]`

An `order-events` topic must carry several Avro record types (`OrderCreated`, `OrderShipped`, `OrderCancelled`) in a single topic so that per-order ordering is preserved. The team also wants each topic to evolve its schemas independently from other topics that use the same record types. Which subject name strategy should the producer use?

- A. `TopicNameStrategy` (the default) with a single union schema for all types
- B. `RecordNameStrategy`
- C. `TopicRecordNameStrategy`
- D. `TopicNameStrategy` with compatibility set to `NONE`

### Question 6 — `[DEV · Schema Registry · Single]`

The exact same Avro schema string is registered first under subject `orders-value` (where it becomes version 4) and later under subject `orders-archive-value` (where it becomes version 1). Which statement is correct?

- A. Schema Registry assigns two different schema IDs because the subjects differ
- B. Both registrations return the **same schema ID**; only the version differs per subject, and the wire format carries the ID, not the version
- C. The second registration fails with HTTP 409 because the schema already exists
- D. Both registrations return the same version number because versions are global

### Question 7 — `[DEV · Schema Registry · Single]`

In production, a company sets `auto.register.schemas=false` on all producers. A newly deployed producer fails at startup with a `SerializationException` wrapping `Schema not found; error code: 40403`. What is the CORRECT remediation that follows the company's governance policy?

- A. Set `auto.register.schemas=true` on this producer only, since it is a new service
- B. Set `use.latest.version=true` so the serializer picks whatever schema is already registered
- C. Change the subject compatibility to `NONE` so any schema is accepted
- D. Register the producer's schema through the controlled process (CI/CD pipeline or REST API) before deploying the producer; keep `auto.register.schemas=false`

### Question 8 — `[DEV · Schema Registry · Single]`

Before deploying a schema change, a CI pipeline must verify that the new Avro schema is compatible with the currently registered schema of subject `orders-value`, **without registering it**. Which REST call should the pipeline use?

- A. `GET /subjects/orders-value/versions/latest`
- B. `POST /compatibility/subjects/orders-value/versions/latest` with the new schema in the body
- C. `POST /subjects/orders-value/versions` with the new schema in the body
- D. `PUT /config/orders-value` with `{"compatibility": "BACKWARD"}`

### Question 9 — `[DEV · Schema Registry · Multi — Choose 2]`

Which TWO statements about how Confluent Schema Registry stores its data are correct? (Choose two.)

- A. Schemas, subjects and compatibility settings are stored in a Kafka topic named `_schemas` that has a single partition
- B. Schemas are stored in an embedded relational database on each Schema Registry node
- C. The storage topic uses `cleanup.policy=compact`, so the latest state can be rebuilt by replaying it
- D. The storage topic must have at least 50 partitions so that multiple Schema Registry instances can write concurrently
- E. Each Schema Registry instance accepts write requests independently; there is no leader

### Question 10 — `[DEV · Serialization · Single]`

A company has services in Java, Go and Python that already communicate through gRPC. They now want to publish the same strongly typed messages to Kafka with the smallest payload size and native support for the schema definitions they already maintain. Which serialization format is the BEST fit with Schema Registry?

- A. JSON Schema, because it is human readable
- B. Plain JSON with `StringSerializer`
- C. Protobuf with `KafkaProtobufSerializer`
- D. Avro with `KafkaAvroSerializer`, because it is the only format Schema Registry supports

### Question 11 — `[DEV · Schema Registry · Single]`

Subject `inventory-value` has three versions. Version 1 has field `sku`; version 2 removed `sku`; version 3 re-added `sku` **without** a default. The topic is compacted and consumers routinely replay it from the beginning. Compatibility is `BACKWARD`. Which statement is correct?

- A. Version 3 is accepted because it is compared only with version 2, and adding `sku` back restores compatibility with version 1
- B. Version 3 is rejected because `BACKWARD` compares against all previous versions
- C. Version 3 is accepted only if compatibility is `BACKWARD_TRANSITIVE`
- D. Version 3 is rejected with `BACKWARD` because adding a field without a default is not backward compatible; even if it had a default, only `BACKWARD_TRANSITIVE` would guarantee that a consumer on version 3 can still read version 1 data

### Question 12 — `[DEV · Schema Registry · Multi — Choose 2]`

A Java consumer must read Avro records that were produced with Schema Registry. Which TWO consumer properties are REQUIRED? (Choose two.)

- A. `value.deserializer=io.confluent.kafka.serializers.KafkaAvroDeserializer`
- B. `auto.register.schemas=true`
- C. `schema.registry.url=http://schema-registry:8081`
- D. `value.converter=io.confluent.connect.avro.AvroConverter`
- E. `use.latest.version=true`

### Question 13 — `[CONNECT · Internal topics · Multi — Choose 3]`

A platform team is manually pre-creating the internal topics for a Kafka Connect **distributed** cluster before starting the workers. Which THREE statements are correct? (Choose three.)

- A. The config storage topic (default `connect-configs`) must have exactly **1** partition
- B. The offset storage topic should use `cleanup.policy=delete` with a 7-day retention so old offsets expire
- C. All three internal topics must be **compacted**
- D. The status storage topic (default `connect-status`) must have exactly 1 partition
- E. The offset storage topic defaults to **25** partitions and the status topic to **5** partitions

### Question 14 — `[CONNECT · Standalone vs Distributed · Multi — Choose 2]`

Which TWO statements correctly distinguish Kafka Connect **distributed** mode from **standalone** mode? (Choose two.)

- A. Distributed mode stores source connector offsets in a local file defined by `offset.storage.file.filename`
- B. In distributed mode connectors are created and modified through the REST API (port 8083), not through properties files on the command line
- C. Distributed mode requires ZooKeeper to coordinate the workers
- D. Workers in distributed mode join a group identified by `group.id`, and the connector configurations, offsets and statuses are stored in Kafka topics
- E. Standalone mode supports exactly-once source connectors while distributed mode does not

### Question 15 — `[CONNECT · Converter · Single]`

An S3 sink connector fails immediately with `org.apache.kafka.connect.errors.DataException: Converting byte[] to Kafka Connect data failed due to serialization error` and the log shows `Unrecognized token` at byte 0. The source topic is written by a Java producer that uses `KafkaAvroSerializer`. The worker is configured with `value.converter=org.apache.kafka.connect.json.JsonConverter`. What should the developer do?

- A. Set `value.converter.schemas.enable=false` on the connector
- B. Add an SMT `Cast$Value` to convert the value to a string
- C. Configure the connector with `value.converter=io.confluent.connect.avro.AvroConverter` and `value.converter.schema.registry.url=http://schema-registry:8081`
- D. Set `errors.tolerance=all` so the bad records are skipped

### Question 16 — `[CONNECT · Converter · Single]`

A JDBC sink connector reads a topic that contains plain JSON documents such as `{"id": 42, "status": "PAID"}` produced by a Node.js application. The task fails with `JsonConverter with schemas.enable requires "schema" and "payload" fields and may not contain additional fields`. What is the cause?

- A. The worker's `JsonConverter` has `schemas.enable=true` (the default) and expects each message to be an envelope `{"schema": ..., "payload": ...}`; either set `value.converter.schemas.enable=false` (if the sink can work schemaless) or produce with a schema-aware format such as Avro
- B. The topic uses the Schema Registry wire format and the converter must be switched to `AvroConverter`
- C. The `transforms` chain is missing a `HoistField` transformation
- D. `tasks.max` is greater than the number of partitions

### Question 17 — `[CONNECT · SMT · Single]`

A JDBC **sink** connector reads topics `db1.public.orders` and `db1.public.customers` (written by a Debezium source) and is configured with `transforms=route`, `transforms.route.type=org.apache.kafka.connect.transforms.RegexRouter`, `transforms.route.regex=db1\.public\.(.*)`, `transforms.route.replacement=$1`. What is the effect?

- A. The connector consumes from new Kafka topics named `orders` and `customers` instead of the original topics
- B. The records' topic field is rewritten to `orders` and `customers` before `put()`, so the sink writes to destination tables named `orders` and `customers` instead of `db1.public.orders`
- C. Kafka renames the source topics to `orders` and `customers`
- D. The transformation fails because `RegexRouter` can only be used with source connectors

### Question 18 — `[CONNECT · SMT · Multi — Choose 2]`

A source connector must (1) add a field `ingested_at` containing the record timestamp and (2) replace the value of the `ssn` field with nulls before the data reaches Kafka. Which TWO transformations achieve this? (Choose two.)

- A. `org.apache.kafka.connect.transforms.ReplaceField$Value` with `renames=ssn:ingested_at`
- B. `org.apache.kafka.connect.transforms.InsertField$Value` with `timestamp.field=ingested_at`
- C. `org.apache.kafka.connect.transforms.ExtractField$Value` with `field=ssn`
- D. `org.apache.kafka.connect.transforms.MaskField$Value` with `fields=ssn`
- E. `org.apache.kafka.connect.transforms.TimestampRouter` with `topic.format=${topic}-ingested_at`

### Question 19 — `[CONNECT · SMT · Single]`

An Elasticsearch sink connector crashes whenever it receives a record with a `null` value (a tombstone emitted by a Debezium source after a `DELETE`). The team wants to drop those records inside Connect without modifying the source. Which configuration is correct?

- A. `transforms=drop` with `transforms.drop.type=org.apache.kafka.connect.transforms.Filter` and no predicate
- B. `errors.tolerance=all` so that null values are skipped
- C. `transforms=drop`, `transforms.drop.type=org.apache.kafka.connect.transforms.Filter`, `transforms.drop.predicate=isTombstone`, `predicates=isTombstone`, `predicates.isTombstone.type=org.apache.kafka.connect.transforms.predicates.RecordIsTombstone`
- D. `value.converter=org.apache.kafka.connect.converters.ByteArrayConverter`

### Question 20 — `[CONNECT · Error handling · Single]`

A developer configures a JDBC **source** connector with `errors.tolerance=all`, `errors.log.enable=true` and `errors.deadletterqueue.topic.name=dlq-jdbc-source`. A malformed row causes a conversion error, but no record ever appears in `dlq-jdbc-source`, although the task keeps running. Why?

- A. Dead letter queues are supported only for **sink** connectors; for a source connector the failed record is only logged and skipped
- B. `errors.deadletterqueue.context.headers.enable` must be set to `true` for records to be written to the DLQ
- C. The DLQ topic must be created manually before the connector starts
- D. `errors.retry.timeout` is `0`, so the record is dropped before reaching the DLQ

### Question 21 — `[CONNECT · Error handling · Single]`

`GET /connectors/orders-sink/status` shows the connector in state `RUNNING` but task 0 in state `FAILED` with a `trace` containing a `DataException`. The connector uses default error handling settings. After fixing the offending record upstream, what must the operator do to resume processing?

- A. Nothing; Connect automatically restarts failed tasks after `scheduled.rebalance.max.delay.ms`
- B. Increase `tasks.max` so a new healthy task is created
- C. Restart the whole worker JVM; a task failure always requires a worker restart
- D. Call `POST /connectors/orders-sink/restart?includeTasks=true&onlyFailed=true` (or `POST /connectors/orders-sink/tasks/0/restart`), because failed tasks are never restarted automatically

### Question 22 — `[CONNECT · Error handling · Multi — Choose 2]`

An S3 **sink** connector must keep running when it meets records that fail deserialization, and each failed record must be written to topic `dlq-s3-orders` together with headers that identify the original topic, partition, offset and the exception. `errors.deadletterqueue.topic.name=dlq-s3-orders` is already set. Which TWO additional properties are REQUIRED? (Choose two.)

- A. `errors.tolerance=all`
- B. `errors.retry.timeout=-1`
- C. `errors.deadletterqueue.context.headers.enable=true`
- D. `errors.log.include.messages=true`
- E. `errors.deadletterqueue.topic.replication.factor=1`

### Question 23 — `[CONNECT · Tasks · Single]`

A team deploys a Debezium PostgreSQL source connector with `tasks.max=8` on a 4-worker Connect cluster, but `GET /connectors/pg-cdc/tasks` shows only one task. Why?

- A. The Connect cluster needs at least 8 workers to run 8 tasks
- B. `tasks.max` is only an upper bound; the connector decides how many tasks it can actually create, and the Debezium PostgreSQL connector always uses a single task (one replication slot)
- C. The connector is paused; call `PUT /connectors/pg-cdc/resume`
- D. `offset.storage.partitions` is too low; increase it to 25

### Question 24 — `[CONNECT · REST API · Single]`

An operator needs to change `flush.size` on an existing running connector `orders-s3` in a distributed Connect cluster with the minimum number of API calls and without losing offsets. Which call is correct?

- A. `DELETE /connectors/orders-s3` followed by `POST /connectors` with the new configuration
- B. `POST /connectors/orders-s3/config` with the new value
- C. `PUT /connectors/orders-s3/config` with the full updated configuration object
- D. `PATCH /connectors/orders-s3/offsets` with the new value

### Question 25 — `[CONNECT · Offsets · Single]`

To re-ingest a file from the beginning, an operator deletes the `FileStreamSource` connector `log-source` with `DELETE /connectors/log-source` and recreates it with the same name and configuration. The connector immediately reports it is up to date and produces nothing. What happened, and what is the correct procedure on Kafka 3.6+?

- A. The file has been truncated by the sink; recreate the file
- B. Deleting a connector does **not** delete its offsets in `connect-offsets`, so the recreated connector resumed from the old position; the correct procedure is `PUT /connectors/log-source/stop`, then `DELETE /connectors/log-source/offsets`, then `PUT /connectors/log-source/resume`
- C. The connector must be created with a different `group.id`
- D. `DELETE /connectors/log-source` also deleted the target topic; recreate the topic first

### Question 26 — `[CONNECT · Exactly-once · Multi — Choose 2]`

After a worker crash, a source connector re-emitted several hundred duplicate records. The team runs Kafka 3.8 in distributed mode and wants the framework to guarantee exactly-once delivery for this source connector and to fail fast if that is not possible. Which TWO settings are required? (Choose two.)

- A. Connector property `enable.idempotence=true`
- B. Worker property `exactly.once.source.support=enabled` (rolled out via `preparing` first)
- C. Connector property `errors.tolerance=none`
- D. Worker property `processing.guarantee=exactly_once_v2`
- E. Connector property `exactly.once.support=required`

### Question 27 — `[CONNECT · Offsets (Week 4 review) · Single]`

A sink connector named `es-orders` appears to lag behind the `orders` topic. Which command shows the current lag per partition, and what must be true before the operator can reset that position with `kafka-consumer-groups.sh --reset-offsets`?

- A. `kafka-consumer-groups.sh --describe --group connect-es-orders`; the connector must be stopped (group inactive) before the reset is allowed
- B. `kafka-consumer-groups.sh --describe --group es-orders`; the reset works while the connector is running
- C. `kafka-console-consumer.sh --topic connect-offsets --property print.key=true`; the reset requires `PATCH /connectors/es-orders/config`
- D. `GET /connectors/es-orders/status`; the reset requires deleting `connect-status`

### Question 28 — `[CONNECT · Debezium CDC · Multi — Choose 2]`

A Debezium PostgreSQL connector with default settings captures table `public.customers` into topic `pg1.public.customers`. A row is deleted. Which TWO records does the connector emit for that delete? (Choose two.)

- A. A change event whose value has `"op": "d"`, `before` populated (at least the primary key) and `"after": null`
- B. A change event with `"op": "u"` where `after` contains a `deleted=true` flag
- C. A change event with `"op": "r"` re-reading the row
- D. A **tombstone** record with the same key and a `null` value, so that log compaction can remove the key
- E. Nothing, because log-based CDC cannot capture deletes

### Question 29 — `[CONNECT · Client overrides · Single]`

A team wants one sink connector to consume with `max.poll.records=2000` while all other connectors keep the worker default. They add `consumer.override.max.poll.records=2000` to the connector config, but `POST /connectors` is rejected with a validation error saying the override is not allowed. What is the cause?

- A. Connector-level consumer overrides must use the `consumer.` prefix, not `consumer.override.`
- B. `max.poll.records` can only be changed by restarting the worker with a new `consumer.max.poll.records`
- C. The worker's `connector.client.config.override.policy` is set to `None` (or a `Principal`/`Allowlist` policy that excludes this key); it must allow the override, for example `All`
- D. Sink connectors cannot override consumer settings; only source connectors can override producer settings

### Question 30 — `[DEV · Transactions (Week 3 review) · Single]`

A source connector runs with exactly-once support enabled (KIP-618). A downstream Java consumer with default settings occasionally sees records that were later reported as duplicates or missing in the connector's committed output. Which consumer setting fixes this?

- A. `enable.auto.commit=false`
- B. `isolation.level=read_committed`, because transactional source records are only guaranteed once for consumers that skip aborted transactions
- C. `auto.offset.reset=earliest`
- D. `group.protocol=consumer`
