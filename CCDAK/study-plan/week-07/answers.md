# ✅ Answers & Explanations — Week 7: Security & Testing

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-A · 3-AC · 4-B · 5-B · 6-BD · 7-B · 8-B · 9-C · 10-AC · 11-C · 12-A · 13-BD · 14-C · 15-AC · 16-B · 17-A · 18-C · 19-B · 20-A · 21-BC · 22-C · 23-B · 24-B · 25-AB · 26-AC · 27-B · 28-B · 29-A · 30-B

---

### Question 1 — Answer: **B**

- **Why correct:** `bootstrap.servers` is only used to fetch metadata. The broker answers with the addresses in `advertised.listeners`, and the client then opens a **new connection to that address** for every produce and fetch. Advertising `kafka-internal:9092`, a name that only resolves inside the Docker network, makes the first call succeed and every subsequent one fail. The broker must advertise an address the client can actually reach.
- **Why the others are wrong:** A — the listener is plaintext; adding `security.protocol=SSL` would break the handshake, not fix routing. C — an ISR shortfall produces `NotEnoughReplicasException`, not an unresolvable host. D — `PLAINTEXT` is mapped implicitly; the log clearly shows a name-resolution/connection failure.
- 🧠 **Key point / trap:** "bootstrap works, produce times out" is nearly always **`advertised.listeners`**. The usual fix is two listeners: an internal one for the Docker network and a host-facing one advertising `localhost`.
- 📎 Source: `resources/kafka-security-overview.md` (listeners vs advertised listeners) and Week 1 `labs.md` (Lab 1.1 two-listener compose).

### Question 2 — Answer: **A**

- **Why correct:** each listener name needs an entry in `listener.security.protocol.map`, the replication traffic is pinned with `inter.broker.listener.name`, and a KRaft broker must also declare `controller.listener.names`. Option A supplies all four consistently: `INTERNAL` stays plaintext, `EXTERNAL` becomes SSL, and the controller listener is named.
- **Why the others are wrong:** B — custom listener names without a protocol map are rejected, and `security.inter.broker.protocol` cannot be combined with `inter.broker.listener.name`. C — reusing the same listener for inter-broker traffic and the controller is invalid; the controller listener must be separate. D — `advertised.listeners` takes `name://host:port` values, not protocol names.
- 🧠 **Key point / trap:** with custom listener names you must always set **three** things together: the map, the inter-broker listener name, and (on KRaft) the controller listener names.
- 📎 Source: `resources/kafka-security-overview.md` (listener configuration).

### Question 3 — Answer: **A, C**

- **Why correct:** the client must speak the listener's protocol, so `security.protocol=SSL` is required (A). Because `ssl.client.auth=none`, the client only has to **verify the broker**, which needs a truststore containing the signing CA (C).
- **Why the others are wrong:** B — a keystore holds the client's own certificate and is only needed for mTLS, which this broker does not request. D — `sasl.mechanism` belongs to SASL listeners. E — `ssl.client.auth` is a broker-side setting; it is meaningless on a client.
- 🧠 **Key point / trap:** **truststore = "who do I trust", keystore = "who am I"**. Encryption-only needs a truststore; mTLS needs both.
- 📎 Source: `resources/kafka-security-ssl.md` (client SSL configuration).

### Question 4 — Answer: **B**

- **Why correct:** since Kafka 2.0 `ssl.endpoint.identification.algorithm` defaults to `https`, so clients verify that the address they dialled appears in the certificate. Modern TLS stacks ignore `CN` for this check and require a **Subject Alternative Name**. Re-issuing the certificate with the right SAN is the correct fix.
- **Why the others are wrong:** A — blanking the algorithm disables hostname verification and re-opens the cluster to man-in-the-middle attacks; it is a debugging shortcut, not a production fix. C — switching to `SASL_SSL` adds authentication but the same TLS handshake still fails. D — `super.users` is authorization, unrelated to the handshake.
- 🧠 **Key point / trap:** the exam likes the pairing "`No subject alternative names matching` → add a SAN", and wants you to reject the "just turn verification off" option.
- 📎 Source: `resources/kafka-security-ssl.md` (hostname verification).

### Question 5 — Answer: **B**

- **Why correct:** `ssl.client.auth=required` turns the SSL listener into mutual TLS, so clients must present a certificate. By default the principal becomes the full distinguished name, so `ssl.principal.mapping.rules` is used to extract just the CN, giving the desired `User:orders-service` principal for ACLs.
- **Why the others are wrong:** A — `requested` makes the certificate optional (clients without one fall back to anonymous), and `SSL` is not a SASL mechanism. C — this is password-based SCRAM, not certificate authentication. D — that disables authentication and authorization entirely.
- 🧠 **Key point / trap:** with mTLS the principal is the **whole DN** unless you add mapping rules; ACLs written against `User:orders-service` will silently match nothing otherwise.
- 📎 Source: `resources/kafka-security-ssl.md` (`ssl.client.auth`, principal mapping rules).

### Question 6 — Answer: **B, D**

- **Why correct:** SCRAM stores credentials **salted and hashed** in the cluster metadata log and they are managed at runtime with `kafka-configs.sh`, so users can be added, rotated and revoked with no broker restart (B). SCRAM protects the password from replay but the exchange should still run over TLS to defeat an active man-in-the-middle, hence `SASL_SSL` (D).
- **Why the others are wrong:** A — SASL/PLAIN keeps credentials in a static JAAS file, so every change means a broker restart. C — ZooKeeper is gone in Kafka 4.x; SCRAM credentials live in the metadata log (they can also be seeded at format time with `kafka-storage.sh format --add-scram`). E — SCRAM is fully supported on KRaft.
- 🧠 **Key point / trap:** the "add/rotate users without restarting" requirement maps to **SCRAM** every time; "static file, restart needed" is **PLAIN**.
- 📎 Source: `resources/kafka-security-sasl.md` (SCRAM credential management).

### Question 7 — Answer: **B**

- **Why correct:** the PLAIN mechanism sends the username and password as clear text inside the SASL exchange. On a `SASL_PLAINTEXT` listener nothing encrypts that exchange, so anyone able to observe the network captures usable credentials. PLAIN is only acceptable over `SASL_SSL`.
- **Why the others are wrong:** A — PLAIN is technically supported on `SASL_PLAINTEXT`, which is exactly why this mistake is easy to make. C — Kerberos belongs to GSSAPI. D — the ACL setting is unrelated to the mechanism.
- 🧠 **Key point / trap:** `SASL_PLAINTEXT` means "authenticated but **not encrypted**". The word plaintext refers to the transport, not to the mechanism.
- 📎 Source: `resources/kafka-security-sasl.md` (PLAIN requires TLS).

### Question 8 — Answer: **B**

- **Why correct:** `sasl.mechanism` on the client must be one of the mechanisms the listener advertises in `sasl.enabled.mechanisms`. The broker offers only SCRAM-SHA-512 while the client insists on SCRAM-SHA-256, so negotiation fails with `UnsupportedSaslMechanismException` before any credential is checked.
- **Why the others are wrong:** A — the two SCRAM variants use different hash algorithms and stored credentials; they are not interchangeable. C — the password is never evaluated, so the error is not an authentication failure. D — Kafka never silently downgrades a mechanism.
- 🧠 **Key point / trap:** distinguish **`UnsupportedSaslMechanismException`** (wrong mechanism, negotiation) from **`SaslAuthenticationException`** (right mechanism, bad credentials). The exam tests exactly this pair.
- 📎 Source: `resources/kafka-security-sasl.md` (mechanism negotiation).

### Question 9 — Answer: **C**

- **Why correct:** on a running KRaft cluster SCRAM credentials are written through the broker with `--bootstrap-server`, using `kafka-configs.sh --alter --add-config 'SCRAM-SHA-512=[...]' --entity-type users --entity-name alice`. Specifying `iterations` is optional but valid.
- **Why the others are wrong:** A — `--zookeeper` no longer exists in Kafka 4.x. B — `kafka-acls.sh` manages authorization, not credentials, and has no `--password` flag. D — `kafka-storage.sh random-uuid` generates a cluster id; the `--add-scram` option belongs to `kafka-storage.sh format` and only applies **before** the cluster starts.
- 🧠 **Key point / trap:** two legitimate ways to create SCRAM users — `kafka-storage.sh format --add-scram` at bootstrap time (for the very first admin user) and `kafka-configs.sh` afterwards at runtime.
- 📎 Source: `resources/kafka-security-sasl.md` (SCRAM on KRaft).

### Question 10 — Answer: **A, C**

- **Why correct:** both MSK IAM and OIDC ride on the **OAUTHBEARER** mechanism: the client acquires a short-lived bearer token and the broker validates it (A). They differ only in how the token is obtained — a standards-based OIDC client uses `sasl.oauthbearer.token.endpoint.url`, while MSK IAM injects an AWS SigV4-derived token through the callback handler shipped in `aws-msk-iam-auth` (C).
- **Why the others are wrong:** B — GSSAPI is Kerberos and uses a KDC-issued keytab. D — OAUTHBEARER validation uses the token's signature and claims, never the SCRAM store. E — the `unsecured` login module performs no signature validation and is explicitly for development only.
- 🧠 **Key point / trap:** MSK IAM is **not** a proprietary Kafka mechanism; it is standard SASL/OAUTHBEARER with an AWS-specific callback handler. That is why any client library supporting OAUTHBEARER can talk to MSK IAM.
- 📎 Source: `resources/kafka-security-sasl.md` (OAUTHBEARER) and Week 9 `resources/msk-iam-access-control.md`.

### Question 11 — Answer: **C**

- **Why correct:** `Krb5LoginModule`, a keytab, a Kerberos principal and `sasl.kerberos.service.name` together are the signature of **GSSAPI**, Kafka's Kerberos mechanism.
- **Why the others are wrong:** A — PLAIN uses `PlainLoginModule` with a username and password. B — SCRAM uses `ScramLoginModule`. D — OAUTHBEARER uses `OAuthBearerLoginModule` and a token endpoint or callback handler.
- 🧠 **Key point / trap:** learn the four login module names; the exam identifies mechanisms by the JAAS class alone.
- 📎 Source: `resources/kafka-security-sasl.md` (GSSAPI/Kerberos).

### Question 12 — Answer: **A**

- **Why correct:** `sasl.jaas.config` embeds the JAAS entry directly in the client properties, which removes the need for a separate file or the `java.security.auth.login.config` system property. The value must name the right login module and end with a semicolon.
- **Why the others are wrong:** B — `sasl.login.config` is not a Kafka property. C — `java.security.auth.login.config` expects a **file path** and is a JVM property, not a Kafka client property. D — this is syntactically a broker-side PLAIN entry (`user_<name>=<password>`), not a client credential, and it uses the wrong module for SCRAM.
- 🧠 **Key point / trap:** the trailing semicolon inside `sasl.jaas.config` is mandatory; omitting it is a common and confusing startup failure.
- 📎 Source: `resources/kafka-security-sasl.md` (JAAS configuration).

### Question 13 — Answer: **B, D**

- **Why correct:** both grant exactly what this one producer needs. D spells out the operations explicitly (`Write` plus `Describe` on the topic); B uses the `--producer` convenience flag, which expands to the same thing plus `Create`. Neither weakens security for anyone else.
- **Why the others are wrong:** A — flipping `allow.everyone.if.no.acl.found` to `true` opens every unprotected resource cluster-wide. C — `super.users` bypasses authorization completely for that principal and needs a restart. E — switching to plaintext removes authentication and makes the principal anonymous, which is the opposite of least privilege.
- 🧠 **Key point / trap:** `--producer` is a shortcut, not a different permission model. Know what it expands to, because the exam asks both ways.
- 📎 Source: `resources/kafka-security-authorization-acls.md` (`kafka-acls.sh` convenience options).

### Question 14 — Answer: **C**

- **Why correct:** `--producer --topic <t>` grants **`Write`**, **`Describe`** and **`Create`** on that topic resource. `Describe` is needed for metadata, and `Create` covers the case where the producer triggers topic auto-creation.
- **Why the others are wrong:** A — `Write` alone leaves the producer unable to fetch metadata. B — `Read` is the consumer side and is never granted by `--producer`. D — `All` would violate least privilege and is not what the flag does.
- 🧠 **Key point / trap:** the companion fact is `--consumer --topic t --group g` = `Read` + `Describe` on the topic **plus `Read` on the group**. Add `--idempotent` when the producer is idempotent on pre-2.8 brokers.
- 📎 Source: `resources/kafka-security-authorization-acls.md`.

### Question 15 — Answer: **A, C**

- **Why correct:** a consumer group is its own ACL resource type, so reading topic `payments` is not enough; the principal also needs **`Read` on the `Group` resource `billing`** (A). The `--consumer` convenience flag with `--group` would have granted the topic and group permissions in one command (C).
- **Why the others are wrong:** B — offset commits are authorized by the group ACL, not by `Write` on the topic. D — `ClusterAction` is for inter-broker operations, never for application clients. E — group authorization applies regardless of the auto-commit setting, because joining the group itself requires it.
- 🧠 **Key point / trap:** `GroupAuthorizationException` always points at a **Group** resource ACL, never at the topic.
- 📎 Source: `resources/kafka-security-authorization-acls.md` (resource types).

### Question 16 — Answer: **B**

- **Why correct:** on brokers older than 2.8 an idempotent producer needed the cluster-level **`IdempotentWrite`** permission in addition to topic `Write`, which is why a default Kafka 4.3 producer (idempotence on by default) fails against a 2.7 broker with `ClusterAuthorizationException`.
- **Why the others are wrong:** A — `Alter` on `Cluster` covers administrative changes. C — `Write` on `TransactionalId` is for transactional producers, and this one is only idempotent. D — `Create` on a topic would surface as a topic-level error, not a cluster one.
- 🧠 **Key point / trap:** from 2.8 onward topic `Write` implies idempotent write, so `IdempotentWrite` is effectively legacy. The exam uses it to test whether you can read the **resource type** out of the exception name: `Cluster…Exception` → a `Cluster` ACL.
- 📎 Source: `resources/kafka-security-authorization-acls.md` (operations by resource).

### Question 17 — Answer: **A**

- **Why correct:** transactional producers are authorized on the `TransactionalId` resource. `initTransactions()` requires **`Write` on the `TransactionalId`** matching `order-processor-1`, either literally or through a prefixed pattern.
- **Why the others are wrong:** B — `Alter` on `Cluster` is administrative. C — the transactional id is not a consumer group; a read-process-write application separately needs `Read` on its actual group. D — `IdempotentWrite` applies to the `Cluster` resource, not to topics.
- 🧠 **Key point / trap:** a full read-process-write application needs **three** grants: topic `Read`, topic `Write`, group `Read`, and on top of that `Write` on the `TransactionalId`.
- 📎 Source: `resources/kafka-security-authorization-acls.md` (TransactionalId resource).

### Question 18 — Answer: **C**

- **Why correct:** prefixed ACLs are expressed with the prefix as the resource name plus `--resource-pattern-type prefixed`. That single rule covers every existing and future topic starting with `orders-`, and nothing else.
- **Why the others are wrong:** A — resource names are not glob patterns; `'orders-*'` would be taken literally. B — `'*'` is the literal wildcard for **all** topics, far broader than asked. D — `match` is a filter used when **listing or deleting** ACLs, not a pattern type you can create.
- 🧠 **Key point / trap:** three pattern types exist — `LITERAL`, `PREFIXED` and the query-only `MATCH`. Only the first two can be stored.
- 📎 Source: `resources/kafka-security-authorization-acls.md` (resource pattern types).

### Question 19 — Answer: **B**

- **Why correct:** the authorizer evaluates Deny first. Any matching Deny rule wins over every Allow rule, so Bob's connection from `10.1.1.7` is refused even though the wildcard Allow also matches him.
- **Why the others are wrong:** A — the wildcard Allow is overridden by the Deny. C — specificity does not decide the outcome; the Deny-first rule does, and it applies in both directions. D — that exception indicates the authorizer has not finished loading, which is not the case here.
- 🧠 **Key point / trap:** the precedence is **explicit Deny → explicit Allow → implicit Deny**, exactly like the IAM evaluation logic you already know from `SAA-C03`.
- 📎 Source: `resources/kafka-security-authorization-acls.md` (authorization order).

### Question 20 — Answer: **A**

- **Why correct:** `AclAuthorizer` stored ACLs in ZooKeeper, which no longer exists in Kafka 4.x. The KRaft replacement is `org.apache.kafka.metadata.authorizer.StandardAuthorizer` (KIP-801), which keeps ACLs in the `__cluster_metadata` log and replicates them through the controller quorum.
- **Why the others are wrong:** B — `SimpleAclAuthorizer` is an even older ZooKeeper-based class. C — KRaft fully supports ACLs; `super.users` is only a bypass list. D — no such class ships with Apache Kafka.
- 🧠 **Key point / trap:** remember the pairing **ZooKeeper → `AclAuthorizer`, KRaft → `StandardAuthorizer`**. Copying an old `server.properties` into a 4.x cluster is a realistic failure.
- 📎 Source: `resources/kafka-security-authorization-acls.md` (StandardAuthorizer, KIP-801).

### Question 21 — Answer: **B, C**

- **Why correct:** Kafka does not reject quota-exceeding traffic. The broker computes how long the client must pause to fall back under the limit, returns that value in `throttle_time_ms` and mutes the channel for the delay (B). From the client's point of view there is no error, only lower throughput and a rising `produce-throttle-time-avg` metric (C).
- **Why the others are wrong:** A — there is no `QuotaViolationException` delivered to producer callbacks. D — quotas are enforced **per broker**, so the effective cluster-wide ceiling is the quota multiplied by the number of brokers the client writes to. E — `acks` has no effect on quota enforcement.
- 🧠 **Key point / trap:** "throughput mysteriously capped with no errors in the log" is the fingerprint of a quota. Check `produce-throttle-time-avg` or `fetch-throttle-time-avg`.
- 📎 Source: `resources/kafka-quotas.md` (throttling mechanism).

### Question 22 — Answer: **C**

- **Why correct:** quota resolution walks from the most specific match to the least specific, and a `(user, client-id)` entry is the most specific one available. Alice's `batch-loader` producer therefore gets **10 MB/s**.
- **Why the others are wrong:** A — a default only applies when no more specific quota exists. B — user-level quotas do not override the combined `(user, client-id)` entry; they sit one level below it. D — Kafka does not take the minimum across levels; it picks a single winner by specificity.
- 🧠 **Key point / trap:** the precedence chain is `(user, client-id)` → `user` → `client-id` → defaults. The intent is to let an operator grant an exception to one noisy application of one tenant.
- 📎 Source: `resources/kafka-quotas.md` (quota precedence).

### Question 23 — Answer: **B**

- **Why correct:** Kafka has **no built-in encryption at rest**. TLS protects data in transit only. Compliance is met either at the storage layer (encrypted volumes, or KMS-backed encryption as `Amazon MSK` provides) or by encrypting the payload in the client before it is serialized, which also protects it from broker operators.
- **Why the others are wrong:** A and D — `log.encryption.enable` does not exist and `ssl.keystore.type` only selects the keystore format. C — SSL listeners encrypt the connection; segments are written to disk in the clear.
- 🧠 **Key point / trap:** "encryption at rest" → disk/volume encryption or end-to-end payload encryption. This is a frequent exam distractor because every other system seems to have a broker-side switch.
- 📎 Source: `resources/kafka-security-overview.md` (scope of Kafka security) and Week 9 `resources/msk-configuration-and-monitoring.md`.

### Question 24 — Answer: **B**

- **Why correct:** per-connector client credentials require the worker to permit overrides via `connector.client.config.override.policy` (`All`, or `Principal`/`Allowlist` for a narrower scope), after which the connector configuration supplies `consumer.override.*` properties such as the JAAS config and, if it differs, the mechanism.
- **Why the others are wrong:** A — overrides are refused unless the worker policy allows them; the default policy is `None`. C — a second cluster is unnecessary precisely because this override mechanism exists. D — `super.users` grants sweeping privileges and does not change the identity the connector authenticates as.
- 🧠 **Key point / trap:** the override policy lives on the **worker** and the override values live on the **connector**. Kafka 4.2 added the `Allowlist` policy for finer control.
- 📎 Source: Week 5 `resources/connect-user-guide-configs-rest.md` (client config override policy).

### Question 25 — Answer: **A, B**

- **Why correct:** `MockConsumer` does not talk to a coordinator, so the test must set up the state a real consumer would have received: an assignment (A, via `assign()` or `subscribe()` followed by `rebalance()`) and starting offsets for those partitions (B, `updateBeginningOffsets`). Without both, `addRecord` and `poll` throw `IllegalStateException`.
- **Why the others are wrong:** C — `commitSync()` does not initialise positions and would itself fail without an assignment. D — the entire point of `MockConsumer` is to avoid a broker. E — there is no such method; auto-commit is not what is missing.
- 🧠 **Key point / trap:** the `MockConsumer` recipe is always the same three steps: **assign → updateBeginningOffsets → addRecord**, then poll.
- 📎 Source: `resources/kafka-mock-clients-javadoc.md` (`MockConsumer` usage).

### Question 26 — Answer: **A, C**

- **Why correct:** scenario (1) is pure client-side error handling, which `MockProducer` covers deterministically: disable auto-completion and fail the pending future with `errorNext(...)` (A). Scenario (2) depends on real broker behaviour — transaction markers, `read_committed` visibility and a genuine rebalance — so it needs an integration test against a real broker, which Testcontainers provides (C).
- **Why the others are wrong:** B — forcing real network timeouts in CI is slow and flaky when a mock gives the same coverage. D — `TopologyTestDriver` tests a Streams topology in a single thread and does not simulate rebalances between instances. E — `MockConsumer.rebalance()` simulates an assignment change locally and knows nothing about transactions.
- 🧠 **Key point / trap:** the dividing line is **"does the assertion depend on broker behaviour?"** No → mock. Yes → Testcontainers.
- 📎 Source: `resources/kafka-mock-clients-javadoc.md` and `resources/testcontainers-kafka.md`.

### Question 27 — Answer: **B**

- **Why correct:** `history()` returns every `ProducerRecord` handed to `send()` since the last `clear()`, independently of whether the corresponding futures have been completed. That is what makes it useful for asserting what the code under test attempted to publish, including keys, headers and target topics.
- **Why the others are wrong:** A — with `autoComplete=true` futures complete immediately; no `flush()` is needed. C — `errorNext(e)` completes the next pending future **exceptionally**; `send()` itself does not throw. D — `MockProducer` does implement the transactional API and records whether transactions were committed or aborted.
- 🧠 **Key point / trap:** `MockProducer` gives you three assertion surfaces: `history()`, the completion state of the returned futures, and the transaction flags.
- 📎 Source: `resources/kafka-mock-clients-javadoc.md` (`MockProducer`).

### Question 28 — Answer: **B**

- **Why correct:** the compatibility endpoint tests a candidate schema against the subject's configured compatibility level and returns `is_compatible` **without registering anything**, which is exactly what a pull-request check needs. The Maven plugin goal `test-compatibility` wraps the same call.
- **Why the others are wrong:** A — this registers the schema when it happens to be compatible, polluting the subject with versions created by CI. C — lowering the compatibility level to `NONE` defeats the purpose of the check. D — fetching a schema by id verifies nothing about compatibility.
- 🧠 **Key point / trap:** `POST /compatibility/...` is read-only; `POST /subjects/.../versions` mutates. Choosing the wrong one is the trap.
- 📎 Source: `resources/schema-registry-compatibility-testing.md` and Week 5 `resources/schema-registry-rest-api.md`.

### Question 29 — Answer: **A**

- **Why correct:** `TopologyTestDriver` runs the topology in-process with a virtual clock. `advanceWallClockTime(Duration)` moves that clock forward and fires any wall-clock punctuator that is due, so a 30-second punctuator can be tested in milliseconds.
- **Why the others are wrong:** B — `MockProducer` has nothing to do with Streams topologies. C — sleeping for 30 seconds in CI is exactly what the virtual clock is meant to avoid. D — `MockConsumer.schedulePollTask()` schedules work on a mock consumer, not a Streams punctuator.
- 🧠 **Key point / trap:** the driver advances **stream time** through piped records and **wall-clock time** through `advanceWallClockTime`. Match the method to the punctuation type.
- 📎 Source: Week 6 `resources/streams-testing-topologytestdriver.md`.

### Question 30 — Answer: **B**

- **Why correct:** dead-letter queues in Kafka Connect are implemented in the sink task's record-processing path, so `errors.deadletterqueue.topic.name` is honoured only for **sink** connectors. A source connector can log failures (`errors.log.enable=true`) or skip them under `errors.tolerance=all`, but it has no DLQ.
- **Why the others are wrong:** A — `errors.tolerance=none` makes the task fail immediately; it does not enable a DLQ. C — the topic name is free-form. D — exactly-once source support concerns transactional offset commits, not error routing.
- 🧠 **Key point / trap:** remember the asymmetry — **sink connectors have a DLQ, source connectors do not**. For a source you need an upstream validation step or a custom SMT.
- 📎 Source: Week 5 `resources/connect-error-handling-dlq-kip298.md`.

---

> ✅ Logged every wrong answer? Sort them into *listeners / TLS*, *SASL mechanisms*, *ACLs*, *quotas* and *testing*, then re-read the matching part of the [week plan](README.md). The checkpoint to leave Week 7 is **≥ 70%** on the CONNECT + STREAMS + TEST mini-mock.
