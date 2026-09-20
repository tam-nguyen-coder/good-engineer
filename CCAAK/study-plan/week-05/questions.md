# 📝 Practice Questions — Week 5: Security Administration (listeners, TLS/mTLS, SASL, ACLs at scale, rotation)

> **30 questions** · real CCAAK exam style — scenario first, "what does a competent administrator do next?" · covers the full Week 5 material + 2 review questions from Week 4.
> ⏱️ Treat this as the **MINI-MOCK SEC**: 45 minutes, closed book. The Week 5 checkpoint is **≥ 70% (21/30)**.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain · Topic · type]`. Multi = multiple-response (the number to choose is stated). Domains: `SEC` (Security), `ARCH` (Deployment Architecture).
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[SEC · Listener design · Single]`

A team migrates a 3-broker KRaft cluster to a new listener layout. Each broker is configured as follows:

```
listeners=INTERNAL://:19092,EXTERNAL://:9192
advertised.listeners=INTERNAL://kafka-1:19092,EXTERNAL://kafka-1:9192
listener.security.protocol.map=INTERNAL:PLAINTEXT,EXTERNAL:SASL_SSL,CONTROLLER:PLAINTEXT
inter.broker.listener.name=INTERNAL
controller.listener.names=CONTROLLER
```

Applications outside the Kubernetes cluster reach the brokers through a load balancer at `kafka.acme.io:9192`. They authenticate successfully against the bootstrap server, then every `send()` times out. Replication is healthy and `UnderReplicatedPartitions` is 0. What should the administrator fix FIRST?

- A. Change `inter.broker.listener.name` to `EXTERNAL` so that external clients use the replicated listener
- B. Set `advertised.listeners` for the `EXTERNAL` listener to the externally routable address (`EXTERNAL://kafka.acme.io:9192`), because clients use the advertised address for every connection after bootstrap
- C. Add `CONTROLLER://:9093` to `listeners` on every broker so that clients can reach the controller
- D. Increase `request.timeout.ms` on the clients, since `SASL_SSL` handshakes are slower than `PLAINTEXT`

### Question 2 — `[SEC · Listener design · Single]`

An administrator wants the KRaft controller quorum to use `SASL_SSL` instead of `PLAINTEXT` on a production cluster, with no downtime. Which approach is correct?

- A. Change `listener.security.protocol.map` for the existing `CONTROLLER` listener from `PLAINTEXT` to `SASL_SSL` and restart all controllers at the same time so that they agree on the protocol
- B. Set `inter.broker.listener.name=CONTROLLER` temporarily so that the brokers negotiate the new protocol for the controller quorum
- C. Define a second controller listener (for example `CONTROLLER_SSL`) on a new port, roll the cluster with `controller.listener.names=CONTROLLER,CONTROLLER_SSL`, then roll again with `controller.listener.names=CONTROLLER_SSL,CONTROLLER` and finally remove the old listener — the first name in the list is used for outbound requests
- D. Use `kafka-configs.sh` to update `controller.listener.names` dynamically on each controller, since listener names are a per-broker dynamic configuration

### Question 3 — `[SEC · KRaft listeners · Multi — Choose 2]`

A node runs with `process.roles=broker` in a KRaft cluster where controllers are on dedicated hosts. Which two statements about its listener configuration are correct? (Choose two.)

- A. The node must define `controller.listener.names` and the security properties for that listener, even though it never accepts controller connections
- B. The controller listener must appear in the node's `listeners` property so the node can be reached by the controllers
- C. The value of `controller.listener.names` must not be the same as `inter.broker.listener.name`
- D. `advertised.listeners` must include the controller listener so that clients can be redirected to the active controller
- E. If `inter.broker.listener.name` is omitted, replication silently uses the first entry of `listeners`

### Question 4 — `[SEC · Certificate rotation · Ordering]`

All broker certificates in a production cluster expire in three weeks. They were signed by an internal CA (`ca-2023`) that is also being retired; new certificates are signed by `ca-2026`. Hundreds of client applications, owned by different teams, connect over `SASL_SSL`. Put the following five steps into the correct order for a rotation with **no client downtime**.

- A. Remove `ca-2023` from every truststore
- B. Replace the keystore on one broker at a time, waiting for the cluster to be healthy between brokers
- C. Sign new broker certificates with `ca-2026`, making sure each certificate carries the correct SAN entries
- D. Wait until every client team confirms that the updated truststore is deployed
- E. Add `ca-2026` to the truststore of every broker and distribute the combined truststore (`ca-2023` + `ca-2026`) to all clients

*Answer with the sequence of letters, e.g. `A → B → C → D → E`.*

### Question 5 — `[SEC · Dynamic configuration · Multi — Choose 2]`

Which two security-related changes can be applied to a running Kafka 4.3 cluster **without restarting any broker**? (Choose two.)

- A. Replacing the keystore used by an existing listener, using `kafka-configs.sh --entity-type brokers --entity-name 2 --alter --add-config listener.name.external.ssl.keystore.location=/etc/kafka/secrets/new.p12`
- B. Adding a brand-new `SASL_SSL` listener on a new port to a cluster that currently exposes only `PLAINTEXT`
- C. Creating, rotating and deleting SASL/SCRAM credentials with `kafka-configs.sh --entity-type users`
- D. Changing `inter.broker.listener.name` from `INTERNAL` to `INTERNAL_SSL`
- E. Adding a new user to a SASL/PLAIN listener whose credentials come from the static broker JAAS file

### Question 6 — `[SEC · Certificate rotation · Single]`

An administrator is rotating CAs. The inter-broker listener is `INTERNAL` and currently uses certificates signed by `ca-2023`. Intending to save a step, the administrator pushes a truststore that contains **only** `ca-2026`:

```
kafka-configs.sh --bootstrap-server kafka-1:19092 --entity-type brokers --entity-name 2 \
  --alter --add-config listener.name.internal.ssl.truststore.location=/etc/kafka/secrets/trust-2026.p12
```

The command is rejected by the broker. Why?

- A. Truststore paths can only be changed at the cluster-wide default level, not per broker
- B. For the inter-broker listener, a truststore update is only allowed if the key store currently configured for that listener is trusted by the **new** truststore — the broker's current certificate is signed by `ca-2023`, which the new truststore no longer contains
- C. `listener.name.<name>.ssl.truststore.location` is a read-only configuration and always requires a rolling restart
- D. The broker rejects any truststore that contains fewer certificates than the previous one

### Question 7 — `[SEC · mTLS · Single]`

A security review asks for "client certificate authentication" on the external listener. An administrator sets `ssl.client.auth=requested`, reasoning that it is safer than `none` and less disruptive than `required`. Three months later an audit finds that several applications never installed a client certificate and have been writing to production topics all along. What happened?

- A. `requested` only enforces certificates for consumers, not for producers
- B. With `requested`, the broker asks for a certificate but accepts connections from clients that do not present one; those clients authenticate as `User:ANONYMOUS`. Only `required` enforces mTLS
- C. `requested` silently falls back to `none` when `ssl.principal.mapping.rules` is not configured
- D. The applications bypassed TLS entirely by connecting to the inter-broker listener

### Question 8 — `[SEC · TLS troubleshooting · Single]`

After replacing the certificate on `kafka-2`, one team's application fails to connect while everything else keeps working. The application log shows:

```
javax.net.ssl.SSLHandshakeException: No subject alternative names present
	at sun.security.ssl.Alert.createSSLException(Alert.java:131)
	at org.apache.kafka.common.network.SslTransportLayer.handshake(SslTransportLayer.java:452)
```

What is the correct remediation?

- A. Set `ssl.endpoint.identification.algorithm=` (empty) on the affected clients, which is the supported way to work around SAN problems
- B. Add the broker hostname to `/etc/hosts` on the client machines so the name resolves locally
- C. Reissue the broker certificate with the SAN extension containing the DNS names and IP addresses that clients actually use, ensuring the SAN is present in the CSR and copied by the CA when signing
- D. Set `ssl.client.auth=none` on the broker so the handshake no longer validates identities

### Question 9 — `[SEC · mTLS principal · Single]`

An mTLS listener is enabled and ACLs were written as `User:svc-report`. The service presents a valid certificate with subject `CN=svc-report,OU=Analytics,O=Acme,C=VN`, but every request is denied. `kafka-authorizer.log` shows the principal as `User:CN=svc-report,OU=Analytics,O=Acme,C=VN`. What is the minimal correct fix?

- A. Rewrite every ACL using the full distinguished name as the principal
- B. Configure `ssl.principal.mapping.rules=RULE:^CN=(.*?),.*$/$1/,DEFAULT` on the brokers so the certificate DN is mapped to the short name `svc-report`
- C. Add `User:CN=svc-report,OU=Analytics,O=Acme,C=VN` to `super.users`
- D. Set `allow.everyone.if.no.acl.found=true` so certificate-authenticated clients are permitted by default

### Question 10 — `[SEC · SASL choice · Single]`

A platform team must onboard roughly 50 new service accounts over the next quarter onto an Apache Kafka (not Confluent) cluster. The requirements are: no broker restart when an account is added or a password is rotated, no plaintext passwords stored on broker disks, and no dependency on an external identity provider that the company does not yet operate. Which mechanism should the administrator choose?

- A. `SASL/PLAIN`, because usernames and passwords are the simplest thing to hand out to service teams
- B. `SASL/GSSAPI`, because Kerberos scales to thousands of principals
- C. `SASL/SCRAM-SHA-512`, because credentials live in the metadata log as salted hashes and are created, rotated and deleted at runtime with `kafka-configs.sh --entity-type users`
- D. `SASL/OAUTHBEARER`, because tokens expire automatically

### Question 11 — `[SEC · SCRAM bootstrap · Single]`

A new KRaft cluster will use `SASL_SSL` with `SCRAM-SHA-512` for **inter-broker** communication. During the first startup every broker fails authentication against its peers. How should the administrator have created the inter-broker credential?

- A. With `kafka-configs.sh --zookeeper localhost:2181 --alter --add-config 'SCRAM-SHA-512=[password=...]' --entity-type users --entity-name admin` before starting the brokers
- B. With `kafka-storage.sh format -t <cluster-id> -c server.properties --add-scram 'SCRAM-SHA-512=[name="admin",password="admin-secret"]'`, because the credential must exist in the metadata log before any broker can authenticate
- C. By listing `user_admin="admin-secret"` in the broker's `ScramLoginModule` JAAS section, which the broker reads at startup
- D. The inter-broker credential cannot be SCRAM; it must be `PLAIN` or `GSSAPI`

### Question 12 — `[SEC · SCRAM operations · Multi — Choose 2]`

Which two statements about SASL/SCRAM in a Kafka 4.3 KRaft cluster are correct? (Choose two.)

- A. Credentials are stored in the cluster metadata log as a salt plus a hash, with a minimum iteration count of 4096, so no cleartext password is written to broker disks
- B. Adding or changing a user takes effect only after the next rolling restart of the brokers
- C. `kafka-configs.sh --describe --entity-type users --entity-name svc-orders` prints the stored salt, stored key and iteration count, but never the password
- D. SCRAM credentials are stored in ZooKeeper under `/config/users`, which is why `--zookeeper` is still accepted by `kafka-configs.sh`
- E. Deleting a SCRAM credential immediately terminates all connections already authenticated with it

### Question 13 — `[SEC · Credential revocation · Single]`

A contractor leaves the company at 10:00. The administrator immediately deletes their SCRAM credential:

```
kafka-configs.sh --bootstrap-server kafka-1:19092 --alter \
  --delete-config 'SCRAM-SHA-512' --entity-type users --entity-name svc-contractor
```

At 10:20 monitoring still shows that principal producing to a topic. New connection attempts do fail with `SaslAuthenticationException`. What explains this, and what is the fastest way to stop the writes right now?

- A. The deletion has not propagated yet; wait for `offsets.retention.minutes` to elapse
- B. `connections.max.reauth.ms` defaults to 0, so already-authenticated connections are never re-authenticated and stay alive; the fastest stop is to add a **Deny** ACL for that principal, which is evaluated on every request
- C. The credential was cached in the client; restart the client application
- D. SCRAM deletions only take effect after a controller failover; trigger one with `kafka-leader-election.sh`

### Question 14 — `[SEC · JAAS precedence · Single]`

A broker has all three of the following in place for its `SASL_SSL` listener and the `SCRAM-SHA-512` mechanism: a `listener.name.sasl_ssl.scram-sha-512.sasl.jaas.config` property in `server.properties`, a `sasl_ssl.KafkaServer` section in the static JAAS file, and a `KafkaServer` section in the same file. Which one takes effect?

- A. The `KafkaServer` section, because static JAAS files are loaded by the JVM before broker properties are parsed
- B. The `sasl_ssl.KafkaServer` section, because listener-scoped sections always win over broker properties
- C. The `listener.name.sasl_ssl.scram-sha-512.sasl.jaas.config` broker property, which has the highest precedence, followed by `sasl_ssl.KafkaServer`, then `KafkaServer`
- D. All three are merged, and duplicated options cause the broker to fail at startup

### Question 15 — `[SEC · SASL troubleshooting · Single]`

A cluster exposes two SASL listeners: `EXTERNAL` with `listener.name.external.sasl.enabled.mechanisms=SCRAM-SHA-512` and `ADMIN` with `listener.name.admin.sasl.enabled.mechanisms=OAUTHBEARER`. A newly onboarded application configured with `sasl.mechanism=SCRAM-SHA-256` fails against the `EXTERNAL` port while the existing applications keep working. Which statement is correct?

- A. This is an authorization problem; the new principal is missing `Describe` on the Cluster resource
- B. The client's mechanism is not in the `EXTERNAL` listener's enabled mechanism list, so negotiation fails before authentication; the fix is to use `SCRAM-SHA-512` (or to enable `SCRAM-SHA-256` on that listener)
- C. SCRAM-SHA-256 and SCRAM-SHA-512 are interchangeable at the protocol level; the real cause must be a wrong password
- D. The client accidentally connected to the `ADMIN` listener, which only accepts certificates

### Question 16 — `[SEC · Authorizer · Single]`

An administrator enables authorization on a Kafka 4.3 KRaft cluster by following an older internal runbook. After the change, the first broker to be restarted never comes up and its `server.log` ends with:

```
org.apache.kafka.common.config.ConfigException: Invalid value kafka.security.authorizer.AclAuthorizer for configuration authorizer.class.name: Class kafka.security.authorizer.AclAuthorizer could not be found.
```

What should the administrator do?

- A. Add the `kafka-security` jar to `CLASSPATH`, since the authorizer moved to an optional package in 4.0
- B. Set `authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer` on every broker **and** every controller; `AclAuthorizer` is the ZooKeeper-based implementation and was removed in 4.0
- C. Set `zookeeper.connect` so the authorizer can locate the ACL znodes
- D. Remove `authorizer.class.name` entirely and rely on `allow.everyone.if.no.acl.found=false` to deny unauthenticated access

### Question 17 — `[SEC · ACL diagnosis · Single]`

A service was just granted produce and consume access to a topic. Producing works. Consuming fails with:

```
org.apache.kafka.common.errors.GroupAuthorizationException: Not authorized to access group: billing-etl
```

Which single command grants the missing permission?

- A. `kafka-acls.sh --add --allow-principal User:svc-billing --operation Read --topic payments.orders.created.v1`
- B. `kafka-acls.sh --add --allow-principal User:svc-billing --operation Read --group billing-etl`
- C. `kafka-acls.sh --add --allow-principal User:svc-billing --operation Describe --cluster`
- D. `kafka-acls.sh --add --allow-principal User:svc-billing --operation All --topic '*'`

### Question 18 — `[SEC · ACL defaults · Single]`

A cluster runs with `allow.everyone.if.no.acl.found=true` as a transitional setting while teams migrate to explicit ACLs. The topic `logs.app.events.v1` has never had an ACL, and every application reads from it happily. An administrator then adds one ACL granting `User:svc-search` `Read` on that topic. Within seconds, six other applications start failing with `TopicAuthorizationException`. What happened?

- A. Adding an ACL implicitly creates a Deny rule for every other principal
- B. `allow.everyone.if.no.acl.found` only relaxes access for resources that have **no** matching ACL at all; as soon as the resource has one ACL, normal evaluation applies and unlisted principals are denied
- C. The setting only applies to consumer groups, not to topics
- D. The new ACL was created with pattern type `PREFIXED`, which overrides all literal ACLs

### Question 19 — `[SEC · ACL evaluation · Single]`

A tenant has a broad grant and a narrow restriction:

```
(principal=User:svc-orders, host=*, operation=WRITE, permissionType=ALLOW)  on Topic:PREFIXED:payments.
(principal=User:svc-orders, host=*, operation=WRITE, permissionType=DENY)   on Topic:LITERAL:payments.orders.dlq.v1
```

`svc-orders` can write to `payments.orders.created.v1` but is refused on `payments.orders.dlq.v1`. A junior engineer proposes adding a second ALLOW on the literal DLQ topic so the "more specific rule wins". Will that work?

- A. Yes — literal patterns are more specific than prefixed patterns, so the new ALLOW overrides the DENY
- B. Yes, but only if the ALLOW is created after the DENY, because ACLs are evaluated in creation order
- C. No — Kafka evaluates DENY before ALLOW regardless of pattern specificity or creation order; the DENY must be removed
- D. No — writes to any topic ending in `.dlq.v1` are blocked by the broker's reserved-name rules

### Question 20 — `[SEC · ACL tooling · Single]`

An administrator investigates why a service can still produce to `payments.orders.created.v1` after its ACL was supposedly removed. They run:

```
$ kafka-acls.sh --bootstrap-server kafka-1:19092 --list --topic payments.orders.created.v1
Current ACLs for resource `ResourcePattern(resourceType=TOPIC, name=payments.orders.created.v1, patternType=LITERAL)`:
```

The output is empty. Which command actually answers the question?

- A. `kafka-acls.sh --list --topic payments.orders.created.v1 --resource-pattern-type match`
- B. `kafka-acls.sh --list --topic payments.orders.created.v1 --resource-pattern-type prefixed`
- C. `kafka-acls.sh --list --cluster`
- D. `kafka-acls.sh --list --topic '*' --resource-pattern-type literal`

### Question 21 — `[SEC · ACL shortcuts · Multi — Choose 2]`

An administrator runs:

```
kafka-acls.sh --bootstrap-server kafka-1:19092 --add --allow-principal User:svc-orders \
  --producer --topic payments. --resource-pattern-type prefixed
```

Which two statements are correct? (Choose two.)

- A. The `--producer` shortcut creates ACLs for `WRITE`, `DESCRIBE` and `CREATE` on the matching topics
- B. The principal can now also read from those topics, because `WRITE` implicitly grants `READ`
- C. Topics created later whose names start with `payments.` are covered automatically, without adding ACLs
- D. The shortcut also grants `Read` on any consumer group whose name starts with `payments.`
- E. Because `enable.idempotence` defaults to `true`, this command is insufficient on any Kafka 4.3 broker unless `--idempotent` is added

### Question 22 — `[SEC · ACLs at scale · Multi — Choose 2]`

A platform hosts 300 topics for 80 applications and the ACL list has grown to several thousand entries that nobody dares to touch. Which two changes give the biggest reduction in ACL count and operational risk? (Choose two.)

- A. Enforce a topic naming convention such as `<tenant>.<domain>.<dataset>.<version>` and replace per-topic ACLs with one `PREFIXED` ACL per tenant, applying the same convention to `group.id` and `transactional.id`
- B. Add every application principal to `super.users` and rely on network segmentation instead
- C. Give each application its own principal and grant only the operations it needs, rather than sharing one principal across a team
- D. Set `allow.everyone.if.no.acl.found=true` so that new topics do not need any ACL
- E. Replace all ACLs with a single `User:*` ALLOW on `Topic:LITERAL:*` and use quotas to limit abuse

### Question 23 — `[SEC · Authorizer behaviour · Single]`

A deployment pipeline creates an ACL and then immediately starts the application. Roughly one deployment in ten fails with `TopicAuthorizationException` on the very first request, then succeeds when retried a few seconds later. Nothing is wrong with the ACL itself. What is the explanation?

- A. `kafka-acls.sh` writes the ACL asynchronously and may silently fail; the pipeline should verify with `--list`
- B. With `StandardAuthorizer` the ACL is written as a record to `__cluster_metadata` by the active controller, and each broker applies it only after replaying that record — authorization is eventually consistent across brokers
- C. ACLs are cached on brokers for `metadata.max.age.ms` and are refreshed only on that interval
- D. The first request is always evaluated against `allow.everyone.if.no.acl.found`, which defaults to `false`

### Question 24 — `[SEC · Audit & least privilege · Single]`

During an ACL cleanup, an administrator accidentally removes the grants of a running service. An excerpt from `kafka-authorizer.log` on `kafka-2` reads:

```
INFO Principal = User:svc-billing is Denied operation = Read on resource = Topic:LITERAL:payments.orders.created.v1
     from host = 10.42.7.31 for request = Fetch with resourceRefCount = 1
INFO Principal = User:svc-billing is Denied operation = Read on resource = Group:LITERAL:billing-etl
     from host = 10.42.7.31 for request = OffsetFetch with resourceRefCount = 1
```

Which command restores exactly the permissions the service needs, and nothing more?

- A. `kafka-acls.sh --add --allow-principal User:svc-billing --operation All --topic payments.orders.created.v1 --group billing-etl`
- B. `kafka-acls.sh --add --allow-principal User:svc-billing --consumer --topic payments.orders.created.v1 --group billing-etl`
- C. `kafka-acls.sh --add --allow-principal User:svc-billing --producer --topic payments.orders.created.v1`
- D. Add `User:svc-billing` to `super.users` and restart the brokers

### Question 25 — `[SEC · Super users · Single]`

An administrator enables `StandardAuthorizer` on a running cluster and adds this line to every broker and controller:

```
super.users=User:kafka-admin,User:kafka-broker
```

After the rolling restart, administrative commands fail with `ClusterAuthorizationException` and inter-broker replication starts reporting authorization errors. What is wrong?

- A. `super.users` must also be set on the clients
- B. The `super.users` list is semicolon-delimited (`User:kafka-admin;User:kafka-broker`); with a comma the whole value is parsed as a single malformed principal
- C. Super users must be declared as `Principal:User:...` in Kafka 4.x
- D. `super.users` is ignored unless `allow.everyone.if.no.acl.found=true` is also set

### Question 26 — `[SEC · Encryption at rest · Single]`

A compliance requirement states that message payloads must be unreadable to anyone who obtains the physical disks of the brokers. Which statement describes how this is achieved with Apache Kafka 4.3?

- A. Set `log.encryption.enabled=true` and provide `log.encryption.key.file` on each broker
- B. Kafka has no built-in encryption at rest; use volume or disk encryption at the infrastructure layer, or encrypt the payload in the client before producing
- C. Enabling `SASL_SSL` on all listeners also encrypts the segment files, since the broker stores what it receives
- D. Configure `cleanup.policy=compact` with `compression.type=gzip`, which obfuscates the record contents on disk

### Question 27 — `[SEC · Enabling security · Ordering]`

A cluster currently runs `PLAINTEXT` only. The goal is `SASL_SSL` for clients and `SSL` for inter-broker traffic, with no downtime. Put the following four phases into the correct order.

- A. Incrementally bounce the cluster again with `security.inter.broker.protocol=SSL` so that replication uses the secured port
- B. Incrementally bounce the cluster a final time to remove the `PLAINTEXT` listener
- C. Incrementally bounce the cluster to open the additional `SSL` and `SASL_SSL` ports while keeping the `PLAINTEXT` port open
- D. Reconfigure the client applications to use the `SASL_SSL` port and restart them

*Answer with the sequence of letters, e.g. `A → B → C → D`.*

### Question 28 — `[SEC · Diagnosing failures · Matching]`

Match each observation (1–5) with its single most likely root cause (A–E). Each cause is used exactly once.

| # | Observation |
| --- | --- |
| 1 | Client log: `org.apache.kafka.common.errors.SaslAuthenticationException: Authentication failed during authentication due to invalid credentials with SASL mechanism SCRAM-SHA-512` |
| 2 | Client log: `Bootstrap broker kafka-1:9192 (id: -1 rack: null) disconnected`; broker log: `Failed authentication with /10.42.7.31 (SSL handshake failed)` |
| 3 | Client log: `sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target` |
| 4 | Client connects and runs fine, but throughput is pinned at exactly 10 MB/s and no errors appear anywhere |
| 5 | Client log: `org.apache.kafka.common.errors.TransactionalIdAuthorizationException` |

- A. The client's truststore does not contain the CA that signed the broker certificate (or is missing an intermediate)
- B. The principal is missing `Write` on the `TransactionalId` resource
- C. A `producer_byte_rate` quota is throttling the principal; the broker delays responses instead of raising an error
- D. The client's `security.protocol` does not match the protocol mapped to the port it connected to
- E. The SCRAM credential is wrong or has been deleted

### Question 29 — `[ARCH · Week 4 review · Single]`

A regulated workload must fail over to a second data centre with **identical consumer offsets**, so that consumers resume exactly where they stopped without any translation step. The company runs Confluent Platform in both sites. Which replication approach meets the requirement?

- A. MirrorMaker 2 with `DefaultReplicationPolicy` and the `MirrorCheckpointConnector` enabled
- B. MirrorMaker 2 with `IdentityReplicationPolicy`, which preserves both topic names and offsets
- C. Cluster Linking, which replicates partitions byte-for-byte and preserves offsets on the destination cluster
- D. A stretch cluster with `broker.rack` set per data centre and `min.insync.replicas=1`

### Question 30 — `[ARCH · Week 4 review · Multi — Choose 2]`

A cluster is being designed for a three-rack availability zone layout with a dedicated KRaft controller quorum. Which two statements are correct? (Choose two.)

- A. Setting `broker.rack` on every broker makes the controller spread replicas of each partition across racks when assigning new partitions
- B. A 5-node controller quorum tolerates the loss of 2 controllers, while a 3-node quorum tolerates the loss of 1
- C. Rack awareness automatically moves the replicas of existing partitions when a new rack is added
- D. Consumers read from the closest replica as soon as `broker.rack` is configured on the brokers
- E. A 4-node controller quorum is preferred over 3 because an even number of voters improves availability

---

> ✅ Done? Check your answers in [answers.md](answers.md), fill in the domain scoring table there, and log every wrong answer with the reason you got it wrong. The gate to leave Week 5 is **≥ 70% (21/30)** on this set.
