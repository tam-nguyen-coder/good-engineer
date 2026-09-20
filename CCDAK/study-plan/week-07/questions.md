# 📝 Practice Questions — Week 7: Security & Testing

> **30 questions** · real CCDAK exam style, difficulty ≥ real exam · covers TLS/mTLS, listeners, SASL mechanisms, ACLs with `StandardAuthorizer`, quotas, `MockProducer`/`MockConsumer`, Testcontainers, contract testing — plus 3 review questions from Weeks 5–6.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

---

### Question 1 — `[DEV · Listeners · Single]`

A Kafka 4.3 broker runs inside Docker with `listeners=PLAINTEXT://0.0.0.0:9092` and `advertised.listeners=PLAINTEXT://kafka-internal:9092`. A producer on the developer's laptop uses `bootstrap.servers=localhost:9092`. The initial metadata request succeeds, but every `send()` eventually fails with `TimeoutException: Topic orders not present in metadata after 60000 ms` and the log shows `Connection to node 1 (kafka-internal/172.18.0.2:9092) could not be established`. What is the root cause?

- A. The producer is missing `security.protocol=SSL`
- B. `advertised.listeners` returns a hostname that the client cannot resolve or reach; it must advertise an address reachable from the client (for example `localhost:9092`)
- C. The topic `orders` has `min.insync.replicas` higher than the number of brokers
- D. `listener.security.protocol.map` is missing the `PLAINTEXT` entry

### Question 2 — `[DEV · Listeners · Single]`

An operator adds a second listener to a KRaft broker so that external clients use TLS while internal replication stays in plaintext. Which configuration is valid?

- A. `listeners=INTERNAL://:9092,EXTERNAL://:9095` · `listener.security.protocol.map=INTERNAL:PLAINTEXT,EXTERNAL:SSL,CONTROLLER:PLAINTEXT` · `inter.broker.listener.name=INTERNAL` · `controller.listener.names=CONTROLLER`
- B. `listeners=INTERNAL://:9092,EXTERNAL://:9095` · `security.inter.broker.protocol=PLAINTEXT` · `inter.broker.listener.name=INTERNAL`
- C. `listeners=PLAINTEXT://:9092,SSL://:9095` · `inter.broker.listener.name=SSL` · `controller.listener.names=SSL`
- D. `listeners=INTERNAL://:9092,EXTERNAL://:9095` · `advertised.listeners=INTERNAL:PLAINTEXT,EXTERNAL:SSL`

### Question 3 — `[DEV · TLS · Multi — Choose 2]`

A broker exposes `SSL://kafka.example.com:9095` with `ssl.client.auth=none`. A Java consumer must connect with encryption only. Which two client properties are **required**? (Choose two.)

- A. `security.protocol=SSL`
- B. `ssl.keystore.location` and `ssl.keystore.password`
- C. `ssl.truststore.location` and `ssl.truststore.password` (or `ssl.truststore.certificates` in PEM)
- D. `sasl.mechanism=PLAIN`
- E. `ssl.client.auth=none`

### Question 4 — `[DEV · TLS · Single]`

After upgrading clients, a producer connecting to `10.0.4.21:9095` fails with `javax.net.ssl.SSLHandshakeException: No subject alternative names matching IP address 10.0.4.21 found`. The broker certificate has `CN=10.0.4.21` but no SAN extension. What is the correct production fix?

- A. Set `ssl.endpoint.identification.algorithm=` (empty) on every client to disable hostname verification
- B. Re-issue the broker certificate with a Subject Alternative Name containing the address or DNS name clients use; hostname verification (`ssl.endpoint.identification.algorithm=https`) is enabled by default since Kafka 2.0
- C. Change the client to `security.protocol=SASL_SSL`
- D. Add the broker IP to `super.users`

### Question 5 — `[DEV · mTLS · Single]`

A company wants clients to authenticate using X.509 certificates issued by its internal PKI, without passwords. Certificates carry subjects like `CN=orders-service,OU=payments,O=Acme,C=US`, and the team wants ACL principals to be `User:orders-service`. Which broker configuration achieves this?

- A. `ssl.client.auth=requested` and `sasl.enabled.mechanisms=SSL`
- B. `ssl.client.auth=required` on the `SSL` listener plus `ssl.principal.mapping.rules=RULE:^CN=(.*?),.*$/$1/,DEFAULT`
- C. `security.protocol=SASL_SSL` with `sasl.mechanism=SCRAM-SHA-512` and the certificate password stored in the metadata log
- D. `ssl.client.auth=none` and `allow.everyone.if.no.acl.found=true`

### Question 6 — `[DEV · SASL · Multi — Choose 2]`

A platform team must give 40 microservices individual username/password credentials. Requirements: credentials must be added, rotated and revoked **without restarting brokers**, and passwords must never be stored in clear text on the brokers. The cluster is KRaft-only (Kafka 4.3). Which two statements are correct? (Choose two.)

- A. SASL/PLAIN satisfies the requirement because usernames are listed in the broker JAAS configuration
- B. SASL/SCRAM-SHA-512 satisfies the requirement: credentials are stored salted and hashed in the cluster metadata log and managed at runtime with `kafka-configs.sh --alter --add-config 'SCRAM-SHA-512=[password=...]' --entity-type users --entity-name <user>`
- C. SCRAM credentials must be created in ZooKeeper before the broker starts
- D. SCRAM should be used over `SASL_SSL` so the challenge exchange is protected from man-in-the-middle attacks
- E. SCRAM is not supported on KRaft clusters; use GSSAPI instead

### Question 7 — `[DEV · SASL · Single]`

A developer proposes `security.protocol=SASL_PLAINTEXT` with `sasl.mechanism=PLAIN` for a production cluster reachable from several office networks, arguing that authentication alone is enough. Why is this rejected?

- A. PLAIN is not supported on SASL_PLAINTEXT listeners
- B. PLAIN transmits the username and password in clear text during the SASL exchange, so it must only be used over TLS (`SASL_SSL`)
- C. PLAIN requires a Kerberos KDC to validate the password
- D. PLAIN only works when `allow.everyone.if.no.acl.found=true`

### Question 8 — `[DEV · SASL · Single]`

A broker is configured with `sasl.enabled.mechanisms=SCRAM-SHA-512` on the `SASL_SSL://:9097` listener. A consumer uses:

```properties
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-256
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="alice" password="alice-secret";
```

The password is correct. What happens?

- A. The connection succeeds because both are SCRAM variants
- B. The client fails with `UnsupportedSaslMechanismException` because `sasl.mechanism` must be one of the broker's `sasl.enabled.mechanisms`
- C. The client fails with `SaslAuthenticationException: Authentication failed: Invalid username or password`
- D. The client falls back to PLAIN automatically

### Question 9 — `[DEV · SASL · Single]`

Which command creates a SCRAM-SHA-512 credential for user `alice` on a running Kafka 4.3 KRaft cluster?

- A. `kafka-configs.sh --zookeeper localhost:2181 --alter --add-config 'SCRAM-SHA-512=[password=alice-secret]' --entity-type users --entity-name alice`
- B. `kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:alice --password alice-secret`
- C. `kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=alice-secret]' --entity-type users --entity-name alice`
- D. `kafka-storage.sh random-uuid --add-scram 'SCRAM-SHA-512=[name=alice,password=alice-secret]'`

### Question 10 — `[DEV · SASL · Multi — Choose 2]`

A team runs Kafka on Amazon MSK with IAM access control and also connects an on-premises application through the company's OpenID Connect provider. Both approaches rely on the same Kafka SASL mechanism. Which two statements are correct? (Choose two.)

- A. Both use `sasl.mechanism=OAUTHBEARER`; the client obtains a short-lived bearer token (JWT) and the broker validates it
- B. Both use `sasl.mechanism=GSSAPI` with a keytab issued by the identity provider
- C. For the OIDC provider, the client is configured with `sasl.oauthbearer.token.endpoint.url` (client credentials or client assertion), while MSK IAM plugs in through `sasl.login.callback.handler.class` from the `aws-msk-iam-auth` library
- D. The broker validates OAUTHBEARER tokens by looking the username up in its SCRAM credential store
- E. The `unsecured` OAUTHBEARER login module is recommended for production because it avoids network calls to the identity provider

### Question 11 — `[DEV · SASL · Single]`

A client JAAS configuration contains `com.sun.security.auth.module.Krb5LoginModule required useKeyTab=true keyTab="/etc/security/keytabs/app.keytab" principal="app@CORP.EXAMPLE.COM";` and the client sets `sasl.kerberos.service.name=kafka`. Which SASL mechanism is in use?

- A. PLAIN
- B. SCRAM-SHA-512
- C. GSSAPI
- D. OAUTHBEARER

### Question 12 — `[DEV · SASL · Single]`

A developer wants to configure SCRAM credentials for a Java producer **without** a separate JAAS file or JVM system property. Which property is correct?

- A. `sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="app" password="s3cret";`
- B. `sasl.login.config=/etc/kafka/client_jaas.conf`
- C. `java.security.auth.login.config=org.apache.kafka.common.security.scram.ScramLoginModule`
- D. `sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required user_app="s3cret";`

### Question 13 — `[DEV · ACLs · Multi — Choose 2]`

After enabling `authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer` on a KRaft cluster (with `allow.everyone.if.no.acl.found=false`), the authenticated producer `User:orders-app` fails with `TopicAuthorizationException: Not authorized to access topics: [orders]`. Which two actions would allow the producer to write **while keeping least privilege for other users**? (Choose two.)

- A. Set `allow.everyone.if.no.acl.found=true`
- B. Run `kafka-acls.sh --bootstrap-server ... --add --allow-principal User:orders-app --producer --topic orders`
- C. Add `User:orders-app` to `super.users` on every broker and restart
- D. Grant `--operation Write --operation Describe --topic orders` to `User:orders-app`
- E. Change the producer to `security.protocol=PLAINTEXT` so the principal becomes `User:ANONYMOUS`

### Question 14 — `[DEV · ACLs · Single]`

Which set of operations does the `kafka-acls.sh --producer --topic orders` convenience option grant on the topic?

- A. `Write` only
- B. `Write` and `Read`
- C. `Write`, `Describe` and `Create`
- D. `All`

### Question 15 — `[DEV · ACLs · Multi — Choose 2]`

A consumer in group `billing` reads topic `payments`. The operator granted `Read` and `Describe` on topic `payments` to `User:billing-svc`, yet the consumer fails with `GroupAuthorizationException: Not authorized to access group: billing`. Which two statements are correct? (Choose two.)

- A. The consumer additionally needs `Read` on the `Group` resource `billing`
- B. The consumer additionally needs `Write` on topic `payments` to commit offsets
- C. The single command `kafka-acls.sh --add --allow-principal User:billing-svc --consumer --topic payments --group billing` would have granted everything needed
- D. The consumer needs `ClusterAction` on the `Cluster` resource
- E. Group ACLs are only enforced when `enable.auto.commit=false`

### Question 16 — `[DEV · ACLs · Single]`

A Kafka 4.3 producer with default settings (`enable.idempotence=true`) has `Write` and `Describe` on topic `events`. It still fails on an **older 2.7 broker** with `ClusterAuthorizationException: Cluster authorization failed`. Which ACL is missing on that broker?

- A. `Alter` on `Cluster`
- B. `IdempotentWrite` on `Cluster`
- C. `Write` on `TransactionalId`
- D. `Create` on topic `events`

### Question 17 — `[DEV · ACLs · Single]`

A transactional producer with `transactional.id=order-processor-1` calls `initTransactions()` and receives `TransactionalIdAuthorizationException`. Which ACL is required?

- A. `Write` on the `TransactionalId` resource `order-processor-1` (or a prefixed pattern that matches it)
- B. `Alter` on `Cluster`
- C. `Read` on `Group` `order-processor-1`
- D. `IdempotentWrite` on the `Topic`

### Question 18 — `[DEV · ACLs · Single]`

A team creates topics dynamically named `orders-eu`, `orders-us`, `orders-apac`, and more will follow. They want a single ACL that lets `User:orders-app` produce to all present and future `orders-*` topics but nothing else. Which command is correct?

- A. `kafka-acls.sh --add --allow-principal User:orders-app --producer --topic 'orders-*'`
- B. `kafka-acls.sh --add --allow-principal User:orders-app --producer --topic '*'`
- C. `kafka-acls.sh --add --allow-principal User:orders-app --producer --topic orders- --resource-pattern-type prefixed`
- D. `kafka-acls.sh --add --allow-principal User:orders-app --producer --topic orders- --resource-pattern-type match`

### Question 19 — `[DEV · ACLs · Single]`

The following ACLs exist on topic `audit`: `User:* Allow Read from host *` and `User:bob Deny Read from host 10.1.1.7`. Bob connects from `10.1.1.7` and tries to consume. What is the result?

- A. Bob can read because the wildcard Allow matches all users
- B. Bob is denied because a matching Deny ACL always takes precedence over Allow ACLs
- C. Bob can read because a more specific principal (`User:bob`) beats the wildcard only for Allow rules
- D. The broker returns `AuthorizerNotReadyException`

### Question 20 — `[DEV · ACLs · Single]`

A team migrates configuration from an old ZooKeeper-based cluster and sets `authorizer.class.name=kafka.security.authorizer.AclAuthorizer` on Kafka 4.3 KRaft brokers. The brokers fail to start. What should they use instead?

- A. `org.apache.kafka.metadata.authorizer.StandardAuthorizer`, which stores ACLs in the `__cluster_metadata` log (KIP-801)
- B. `kafka.security.auth.SimpleAclAuthorizer`
- C. No authorizer; KRaft enforces ACLs through `super.users` only
- D. `org.apache.kafka.common.security.authorizer.RbacAuthorizer`

### Question 21 — `[DEV · Quotas · Multi — Choose 2]`

A multi-tenant cluster limits `User:alice` to `producer_byte_rate=1048576`. Alice's producer suddenly pushes 5 MB/s. Which two statements describe the behaviour? (Choose two.)

- A. The broker rejects requests with `QuotaViolationException` and the producer callback receives the error
- B. The broker computes the delay required to bring Alice under the quota, returns the response with a non-zero `throttle_time_ms`, and mutes the channel until the delay elapses
- C. Alice's producer sees no exception, only reduced throughput and an increased `produce-throttle-time-avg` metric
- D. Quotas apply cluster-wide, so Alice gets a total of 1 MB/s across all brokers
- E. The producer must set `acks=0` to bypass quotas

### Question 22 — `[DEV · Quotas · Single]`

The following quotas exist: default user quota `producer_byte_rate=2097152`; `User:alice` `producer_byte_rate=1048576`; `(User:alice, client-id=batch-loader)` `producer_byte_rate=10485760`. Alice's `batch-loader` producer connects. Which quota applies?

- A. 2 MB/s, the default user quota
- B. 1 MB/s, because user-level quotas override client-id quotas
- C. 10 MB/s, because the `(user, client-id)` quota is the most specific match
- D. The smallest of the three (1 MB/s) is always enforced

### Question 23 — `[DEV · Encryption · Single]`

A compliance auditor requires that customer records stored in Kafka topic log segments be encrypted at rest on broker disks. Which statement is correct?

- A. Set `log.encryption.enable=true` on the brokers
- B. Kafka has no built-in at-rest encryption; use disk/volume encryption (for example LUKS or cloud-provider encrypted volumes such as MSK's KMS encryption) or encrypt the payload end-to-end in the client serializer
- C. Enabling `SSL` on all listeners encrypts the log segments on disk
- D. Set `ssl.keystore.type=PEM` so segments are written encrypted

### Question 24 — `[DEV · Ecosystem security · Single]`

A Kafka Connect worker authenticates to the cluster as `User:connect`. One sink connector must instead consume as `User:reporting` with its own SCRAM credentials. Which configuration is required?

- A. Set `consumer.sasl.jaas.config` in the connector configuration; overrides are always allowed
- B. Set `connector.client.config.override.policy=All` on the worker and add `consumer.override.sasl.jaas.config=...` (plus `consumer.override.sasl.mechanism` if different) to the connector configuration
- C. Run a second Connect cluster; per-connector credentials are impossible
- D. Add `User:reporting` to `super.users` on the worker

### Question 25 — `[TEST · MockConsumer · Multi — Choose 2]`

A developer writes a unit test for a consumer loop with `MockConsumer<String, String> consumer = new MockConsumer<>("earliest");` then calls `consumer.addRecord(new ConsumerRecord<>("orders", 0, 0L, "k", "v"))` and `consumer.poll(Duration.ofMillis(100))`. The test fails with `IllegalStateException`. Which two steps are missing **before** adding records? (Choose two.)

- A. `consumer.assign(List.of(new TopicPartition("orders", 0)))` (or `subscribe` followed by `rebalance(...)`)
- B. `consumer.updateBeginningOffsets(Map.of(new TopicPartition("orders", 0), 0L))`
- C. `consumer.commitSync()` to initialise the offsets
- D. Starting a real broker with Testcontainers, because `MockConsumer` needs a coordinator
- E. `consumer.enableAutoCommit(true)`

### Question 26 — `[TEST · Test strategy · Multi — Choose 2]`

A team must test (1) that a producer callback correctly routes a `TimeoutException` to a dead-letter path, and (2) that a transactional read-process-write application produces no duplicates when a consumer instance is killed mid-batch. Which two choices are the most appropriate? (Choose two.)

- A. For (1) use `MockProducer` with `autoComplete=false` and trigger `errorNext(new TimeoutException("..."))`
- B. For (1) use Testcontainers and disconnect the network to force a real timeout in every CI run
- C. For (2) use an integration test with Testcontainers `KafkaContainer`, two consumer instances, `isolation.level=read_committed`, and stop one instance mid-transaction
- D. For (2) use `TopologyTestDriver`, because it simulates rebalances between instances
- E. For (2) use `MockConsumer.rebalance()`, which replays committed transactions

### Question 27 — `[TEST · MockProducer · Single]`

Which statement about `org.apache.kafka.clients.producer.MockProducer` is correct?

- A. With `autoComplete=true` (the default of the no-arg constructor is `false`), each `send()` returns a future that is completed only after `flush()`
- B. `history()` returns the list of `ProducerRecord`s passed to `send()` since the last `clear()`, regardless of whether their futures have completed
- C. `errorNext(e)` throws the exception directly from `send()`
- D. `MockProducer` cannot simulate transactions; use a real broker for `commitTransaction()` tests

### Question 28 — `[TEST · Contract testing · Single]`

A CI pipeline must fail a pull request when a modified Avro schema for subject `orders-value` violates the subject's compatibility level, **without** registering a new schema version. Which approach is correct?

- A. `POST /subjects/orders-value/versions` with the new schema and check for HTTP 409
- B. `POST /compatibility/subjects/orders-value/versions/latest` with `{"schema": "..."}` and fail the build when `is_compatible` is `false` (or run `mvn schema-registry:test-compatibility`)
- C. `PUT /config/orders-value` with `{"compatibility": "NONE"}` before registering
- D. `GET /schemas/ids/1` and compare the JSON manually

### Question 29 — `[STREAMS · TopologyTestDriver · Single]` *(review Week 6)*

A Kafka Streams topology uses a `Processor` with a wall-clock punctuator every 30 seconds. The developer wants a fast unit test that triggers the punctuator without waiting. What should they use?

- A. `TopologyTestDriver` with `advanceWallClockTime(Duration.ofSeconds(30))` after piping input through `TestInputTopic`
- B. `MockProducer` with `completeNext()` called 30 times
- C. Testcontainers with `Thread.sleep(30000)`
- D. `MockConsumer.schedulePollTask()`

### Question 30 — `[CONNECT · Error handling · Single]` *(review Week 5)*

A JDBC **source** connector is configured with `errors.tolerance=all` and `errors.deadletterqueue.topic.name=dlq-jdbc`. Records that fail conversion are silently dropped and nothing appears in `dlq-jdbc`. Why?

- A. `errors.tolerance` must be set to `none` for the DLQ to work
- B. Dead-letter queues are supported only for **sink** connectors; source connectors can only log or skip failed records (`errors.log.enable=true`)
- C. The DLQ topic must be named `connect-dlq`
- D. The worker needs `exactly.once.source.support=enabled`
