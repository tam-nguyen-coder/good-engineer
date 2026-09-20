# ✅ Answers & Explanations — Week 5: Security Administration

> Open only after you have finished the timed run of [questions.md](questions.md) (45 minutes, closed book).
> Back to [week plan](README.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-AC · 4-`C → E → D → B → A` · 5-AC · 6-B · 7-B · 8-C · 9-B · 10-C · 11-B · 12-AC · 13-B · 14-C · 15-B · 16-B · 17-B · 18-B · 19-C · 20-A · 21-AC · 22-AC · 23-B · 24-B · 25-B · 26-B · 27-`C → D → A → B` · 28-`1-E, 2-D, 3-A, 4-C, 5-B` · 29-C · 30-AB

---

## 📊 Chấm điểm theo chủ đề — MINI-MOCK SEC

Đánh dấu từng câu đúng/sai rồi điền bảng. Đây là **checkpoint của Tuần 5**: dưới ngưỡng tổng thì **không** sang Tuần 6.

| Chủ đề | Câu số | Số đúng / Tổng | % | Ngưỡng |
| --- | --- | --- | --- | --- |
| **Thiết kế listener & KRaft** | 1, 2, 3 | ___ / 3 | ___ | ≥ 67% (2/3) |
| **TLS & xoay chứng chỉ** | 4, 5, 6, 8 | ___ / 4 | ___ | ≥ 75% (3/4) |
| **mTLS & principal mapping** | 7, 9 | ___ / 2 | ___ | ≥ 50% (1/2) |
| **SASL & vòng đời credential** | 10, 11, 12, 13, 14, 15 | ___ / 6 | ___ | ≥ 67% (4/6) |
| **Authorizer & ACL ở quy mô** | 16, 17, 18, 19, 20, 21, 22, 23, 24, 25 | ___ / 10 | ___ | ≥ 70% (7/10) |
| **Encryption at rest & quy trình bật bảo mật** | 26, 27 | ___ / 2 | ___ | ≥ 50% (1/2) |
| **Chẩn đoán tổng hợp** | 28 | ___ / 1 | ___ | — |
| **ARCH — ôn Tuần 4** | 29, 30 | ___ / 2 | ___ | ≥ 50% (1/2) |
| **TỔNG** | 1–30 | ___ / 30 | ___ | **⭐ ≥ 70% (21/30)** |

> 📌 Nhóm **Authorizer & ACL** chiếm 10/30 câu vì đó là phần đề CCAAK hỏi dày nhất trong domain Security và cũng là phần khác biệt nhất so với CCDAK. Sai quá 3 câu ở nhóm này thì dù tổng điểm qua ngưỡng vẫn nên làm lại Lab 5.4 và 5.5.

---

### Question 1 — Answer: **B**

- **Why correct:** `listeners` controls what the broker **binds**, `advertised.listeners` controls the address the broker **hands back to clients in the metadata response**. After bootstrap, every producer and consumer connection goes to the advertised address. Here the `EXTERNAL` listener advertises `kafka-1:9192`, an internal Kubernetes name that external applications cannot resolve, so bootstrap (which uses the address the client typed) succeeds and all subsequent produce requests time out. The fix is to advertise the externally routable address.
- **Why the others are wrong:** A — the inter-broker listener is for replication; pointing it at `EXTERNAL` would route replication through the load balancer and would not change what clients are told. C — the controller listener is never exposed to clients, and on a broker-only node it must not be in `listeners`; client requests bound for the controller are forwarded by the broker. D — a timeout on every send with healthy replication is a routing problem, not a handshake-latency problem; raising the timeout only makes the failure slower.
- 🧠 **Key point / trap:** "authenticates against bootstrap but every send times out" is the signature of a wrong `advertised.listeners`, and it stays true no matter which security protocol is in play. Healthy `UnderReplicatedPartitions` rules out a broker-side problem.
- 📎 Source: `resources/kafka-security-overview-and-listeners.md` (listener syntax, advertised vs bound, controller listener not advertised).

### Question 2 — Answer: **C**

- **Why correct:** `controller.listener.names` accepts a **list**, and the documentation states that when several controller listeners are defined, "the first one in the list will be used for outbound requests". That is precisely the mechanism for a no-downtime protocol or port change: one roll to expose the new listener alongside the old, a second roll to promote the new listener to first position, and a final roll to remove the old one.
- **Why the others are wrong:** A — restarting all controllers simultaneously loses the quorum, which is downtime by definition, and mid-roll the controllers would not be able to talk to each other. B — the controller listener must **never** equal the inter-broker listener; the documentation forbids it and the node refuses to start. D — `controller.listener.names` and `listeners` are read-only configurations; only the per-listener security settings of an **existing** listener (keystore, truststore, and similar) are dynamic.
- 🧠 **Key point / trap:** the ability to list several controller listeners exists for exactly one reason — rolling changes. If an exam option offers a simultaneous restart of the quorum, it is wrong.
- 📎 Source: `resources/kafka-security-overview-and-listeners.md` (multiple controller listeners, first entry used for outbound).

### Question 3 — Answer: **A, C**

- **Why correct:** A — the docs are explicit that "even if a server does not have the `controller` role enabled (i.e. it is just a broker), it must still define the controller listener along with any security properties that are needed to configure it", because the broker is a **client** of the controllers. C — "Controllers must use separate listener which is defined by the `controller.listener.names` configuration. This cannot be set to the same value as the inter-broker listener."
- **Why the others are wrong:** B — inverted: on a broker-only node the controller listener is **not** included in `listeners`; the port comes from `controller.quorum.bootstrap.servers`. D — controller listeners are not advertised to clients at all; requests bound for the controller are forwarded by the broker over an `Envelope`. E — if `inter.broker.listener.name` is omitted, Kafka falls back to `security.inter.broker.protocol` (default `PLAINTEXT`), not to "the first entry of `listeners`".
- 🧠 **Key point / trap:** "broker-only node must still configure the controller listener but must not bind it" is a favourite CCAAK distinction. Remember the direction of the connection: brokers dial out to controllers.
- 📎 Source: `resources/kafka-security-overview-and-listeners.md` (KRaft broker-only example).

### Question 4 — Answer: **`C → E → D → B → A`**

- **Why correct:** the invariant is **truststore first, keystore second**. (C) issue the new certificates with correct SANs. (E) distribute a truststore containing **both** CAs everywhere — nothing changes functionally, but every party is now prepared to trust the new chain. (D) wait for the slowest participant, the client fleet; this is the step that takes days and the reason the rotation is planned weeks ahead. (B) swap broker keystores one broker at a time, checking cluster health between nodes. (A) only once no certificate signed by the old CA remains, drop the old CA from the truststores.
- **Why the others are wrong:** any order that places B before E means the brokers present a certificate chain that clients and peers do not trust yet — external clients drop instantly and inter-broker TLS breaks. Placing A before B removes trust in the certificates that are still in use. Placing D before E is meaningless, since there is nothing to deploy yet.
- 🧠 **Key point / trap:** expand trust first, change identity second, shrink trust last. The same shape applies to rotating a SASL mechanism, a controller listener, or any credential: **add the new, migrate, remove the old** — never the reverse.
- 📎 Source: `resources/confluent-dynamic-config-cert-rotation.md` (the two inter-broker trust validation rules) and `README.md` mục A.3.

### Question 5 — Answer: **A, C**

- **Why correct:** A — the keystore of an **existing** listener is a per-broker dynamic configuration (`listener.name.{listenerName}.ssl.keystore.location` and friends), changeable with `kafka-configs.sh` without a restart. C — SCRAM credentials live in the metadata log and are created, altered and deleted at runtime with `kafka-configs.sh --entity-type users`.
- **Why the others are wrong:** B — `listeners` is a read-only configuration; adding a listener that did not exist requires the rolling procedure. D — `inter.broker.listener.name` is read-only and changing it is part of the four-phase procedure. E — SASL/PLAIN credentials come from the static JAAS configuration, so adding a user means editing a file on each broker and bouncing it.
- 🧠 **Key point / trap:** the line between "dynamic" and "restart" runs between **changing the security material of an existing listener** (dynamic) and **changing the shape of the listener set** (restart). Keep that boundary in your head and half the operational security questions answer themselves.
- 📎 Source: `resources/confluent-dynamic-config-cert-rotation.md` (update modes and the list of dynamic `listener.name.*.ssl.*` configs).

### Question 6 — Answer: **B**

- **Why correct:** for the **inter-broker** listener the broker validates truststore changes: "the update is allowed only if the existing key store for that listener is trusted by the new trust store". The broker's live certificate is signed by `ca-2023`; a truststore containing only `ca-2026` would immediately break replication, so the broker refuses the change. The correct move is to push a truststore containing **both** CAs.
- **Why the others are wrong:** A — truststore locations for a listener are explicitly **per-broker** dynamic configs, not cluster-wide only. C — they are dynamic, which is the whole point of the rotation procedure; read-only would make no-downtime rotation impossible. D — there is no rule about certificate counts; the check is a trust check, not a cardinality check.
- 🧠 **Key point / trap:** the two validation rules point in **opposite directions** and both exist to protect replication — keystore change: *new keystore must be trusted by current truststore*; truststore change: *current keystore must be trusted by new truststore*. Non-inter-broker listeners are **not** validated, which is more dangerous, not less: the command succeeds and the clients fall over.
- 📎 Source: `resources/confluent-dynamic-config-cert-rotation.md` (both trust validation rules, verbatim).

### Question 7 — Answer: **B**

- **Why correct:** `ssl.client.auth=requested` makes the broker request a certificate but accept the connection when none is presented. Those clients are authenticated as `User:ANONYMOUS` and, with no authorizer or with permissive ACLs, keep working. The Kafka documentation calls this out directly: the usage of `requested` "is discouraged as it provides a false sense of security and misconfigured clients will still connect successfully".
- **Why the others are wrong:** A — the setting is per listener and applies to every connection, producers and consumers alike. C — there is no such fallback; `ssl.principal.mapping.rules` only reshapes the principal string of clients that **did** present a certificate. D — the inter-broker listener is a separate listener; if the applications had reached it the audit would have found plaintext internal traffic, and in any case the question states they were writing over the external path.
- 🧠 **Key point / trap:** three values, one usable in production. `none` = encryption only (authenticate with SASL instead), `required` = real mTLS, `requested` = the trap answer that looks like a safe middle ground.
- 📎 Source: `resources/kafka-ssl-operations.md` (`ssl.client.auth` three values and the "false sense of security" wording).

### Question 8 — Answer: **C**

- **Why correct:** hostname verification has been on by default since Kafka 2.0 and checks the SAN entries of the broker certificate against the host the client dialled. "No subject alternative names present" means the replacement certificate was issued without the SAN extension — most often because the CA did not copy the extension from the CSR. The fix is to reissue the certificate with the right SANs and verify with `openssl x509 -in certificate.crt -text -noout`.
- **Why the others are wrong:** A — emptying `ssl.endpoint.identification.algorithm` does make the error disappear, which is exactly why it is the attractive wrong answer; it disables man-in-the-middle protection and the docs say there is "no good reason" to do it. B — the problem is not name resolution; the client reached the broker and completed the TCP connection. D — `ssl.client.auth` governs whether the **client** must present a certificate; it has no effect on the client's verification of the **broker**.
- 🧠 **Key point / trap:** only this one broker was rotated, so only this one certificate is wrong — the blast radius tells you where to look. And note that SAN must be present in the **CSR** and preserved by the CA at signing time; checking only the keystore you generated is not enough.
- 📎 Source: `resources/kafka-ssl-operations.md` (hostname verification, SAN in CSR, "failure to copy extension fields when signing").

### Question 9 — Answer: **B**

- **Why correct:** with mTLS the default principal is the full X.500 distinguished name of the certificate. `ssl.principal.mapping.rules` maps the DN to a short name; the rules are evaluated in order and the first match wins, so `RULE:^CN=(.*?),.*$/$1/,DEFAULT` turns `CN=svc-report,OU=Analytics,O=Acme,C=VN` into `svc-report` and the existing ACLs start matching. Nothing else has to change.
- **Why the others are wrong:** A — it works but is the opposite of minimal: every ACL in the cluster now depends on the exact OU/O/C fields, so re-issuing a certificate with a different OU silently revokes access. C — super users bypass **all** ACLs, which turns an authorization bug into a privilege-escalation bug. D — `allow.everyone.if.no.acl.found=true` would open every resource that has no ACL to everyone, and would not even help here because the topic **does** have ACLs.
- 🧠 **Key point / trap:** the authorizer log already told you the answer — it printed the principal the broker actually sees. Always compare "the principal in the log" with "the principal in the ACL" before touching anything else.
- 📎 Source: `resources/kafka-authorization-acls.md` (customizing SSL user name, rule syntax and evaluation order).

### Question 10 — Answer: **C**

- **Why correct:** every requirement maps to SCRAM. Credentials are stored in the metadata log as salt plus hash (no cleartext on disk), created and rotated at runtime with `kafka-configs.sh --alter --add-config 'SCRAM-SHA-512=[password=...]' --entity-type users --entity-name <u>` with no restart, and nothing outside Kafka is required.
- **Why the others are wrong:** A — PLAIN keeps credentials in the static broker JAAS configuration, so each of the 50 onboardings and each password rotation is a rolling restart of the whole cluster. B — Kerberos scales, but it requires a KDC/Active Directory the company does not run, plus keytab distribution and clock synchronisation. D — OAUTHBEARER is an excellent answer **when an identity provider already exists**; the question rules that out.
- 🧠 **Key point / trap:** CCAAK picks the SASL mechanism by the **credential-management** story, not by the connection story. Read the constraints: "no restart" eliminates PLAIN, "no external IdP" eliminates OAUTHBEARER, "no existing directory" eliminates Kerberos.
- 📎 Source: `resources/kafka-sasl-operations.md` (SCRAM credential management) and `README.md` bảng 4 mechanism.

### Question 11 — Answer: **B**

- **Why correct:** the inter-broker credential is needed **before** any broker can authenticate to any other broker, so it cannot be created through the normal runtime path, which itself requires a working cluster. `kafka-storage.sh format ... --add-scram 'SCRAM-SHA-512=[name="admin",password="admin-secret"]'` writes the credential into the metadata log at format time, which is exactly the bootstrap case the option exists for.
- **Why the others are wrong:** A — `--zookeeper` does not exist in Kafka 4.x; every tool uses `--bootstrap-server` (or `--bootstrap-controller`), and there is no ZooKeeper to write to. C — `user_<name>=` entries are the **PLAIN** login module's syntax; `ScramLoginModule` takes only `username` and `password` for the broker's own identity and never defines other users. D — SCRAM is a perfectly valid inter-broker mechanism; it just has this chicken-and-egg bootstrap requirement.
- 🧠 **Key point / trap:** two ways to create a SCRAM user, and the exam tests that you know **which one for which moment**: `kafka-storage.sh format --add-scram` before first boot (inter-broker, first admin), `kafka-configs.sh --entity-type users` at runtime (everyone else).
- 📎 Source: `resources/kafka-sasl-operations.md` (creating SCRAM credentials, both commands).

### Question 12 — Answer: **A, C**

- **Why correct:** A — the docs state SCRAM stores credentials in the metadata log with a minimum iteration count of 4096, salted and hashed. C — `--describe` prints the SCRAM identity (salt, stored key, server key, iterations); the password itself is never recoverable, which is the whole point of a salted challenge-response scheme.
- **Why the others are wrong:** B — the exact opposite: runtime changes are the reason to choose SCRAM over PLAIN. D — ZooKeeper storage was the pre-KRaft implementation; `--zookeeper` was removed and in 4.x the store is `__cluster_metadata`. E — deleting a credential blocks **new** authentications; with `connections.max.reauth.ms=0` (the default) existing connections are never re-authenticated and keep working (see Question 13).
- 🧠 **Key point / trap:** D and E are the two most common false beliefs about SCRAM, and they fail in opposite directions — one underestimates KRaft, the other overestimates revocation.
- 📎 Source: `resources/kafka-sasl-operations.md` (SCRAM section and security considerations).

### Question 13 — Answer: **B**

- **Why correct:** `connections.max.reauth.ms` defaults to **0**, which disables SASL re-authentication. A connection that authenticated successfully before the credential was deleted is never asked to prove itself again, so it keeps producing until it is closed for some other reason. Authorization, by contrast, is evaluated on **every request**, so adding a Deny ACL for that principal stops the writes immediately.
- **Why the others are wrong:** A — `offsets.retention.minutes` governs how long committed offsets survive for an empty group; it has nothing to do with authentication. C — the client caches nothing that matters here; the credential was verified once, at connection time, on the broker. D — there is no relationship between controller elections and credential deletion, and forcing a leader election to revoke access would be a remarkably indirect remedy.
- 🧠 **Key point / trap:** "revoke a credential" and "cut off a live session" are two different operations in Kafka. Remember the pair: **`connections.max.reauth.ms` for the long-term fix, a Deny ACL for the incident.**
- 📎 Source: `resources/kafka-sasl-operations.md` (re-authentication note) and `README.md` Playbook.

### Question 14 — Answer: **C**

- **Why correct:** the documented order of precedence is: broker configuration property `listener.name.{listenerName}.{saslMechanism}.sasl.jaas.config`, then the `{listenerName}.KafkaServer` section of the static JAAS file, then the plain `KafkaServer` section.
- **Why the others are wrong:** A — the static file is not "loaded first wins"; Kafka applies the precedence above explicitly. B — listener-scoped **file sections** rank below the listener-scoped **property**. D — the configurations are not merged; the highest-precedence one is used and the others are ignored, so nothing fails at startup and you can spend a long afternoon editing a JAAS file that has no effect.
- 🧠 **Key point / trap:** the property form is what makes **per-listener, per-mechanism** credentials possible (`EXTERNAL` on SCRAM, `ADMIN` on OAUTHBEARER on the same broker). That is why it outranks everything else.
- 📎 Source: `resources/kafka-sasl-operations.md` (order of precedence, three levels).

### Question 15 — Answer: **B**

- **Why correct:** `sasl.enabled.mechanisms` is configurable **per listener** (`listener.name.external.sasl.enabled.mechanisms`). The client offers `SCRAM-SHA-256`, the `EXTERNAL` listener advertises only `SCRAM-SHA-512`, and the negotiation fails before any credential is exchanged — the client sees an unsupported-mechanism error, not an authentication or authorization error.
- **Why the others are wrong:** A — authorization failures produce `TopicAuthorizationException` / `GroupAuthorizationException` / `ClusterAuthorizationException`, and they happen **after** a successful authentication. C — SHA-256 and SHA-512 are distinct mechanisms with distinct stored credentials; they are not interchangeable, and a wrong password would give `SaslAuthenticationException` instead. D — the `ADMIN` listener uses OAUTHBEARER, not certificates, and the question states the client failed against the `EXTERNAL` port.
- 🧠 **Key point / trap:** "existing applications keep working" localises the fault to the new client's configuration. Then the exception name tells you the layer: mechanism negotiation, not credentials, not ACLs.
- 📎 Source: `resources/kafka-sasl-operations.md` (enabling multiple mechanisms, per-listener prefixes).

### Question 16 — Answer: **B**

- **Why correct:** `kafka.security.authorizer.AclAuthorizer` is the ZooKeeper-based authorizer. ZooKeeper support was removed in Kafka 4.0, the class is no longer in the distribution, and `ConfigDef` therefore rejects the value with exactly the `ConfigException` shown. The KRaft authorizer is `org.apache.kafka.metadata.authorizer.StandardAuthorizer` (KIP-801, available since 3.2.0) and it must be configured on **controllers as well as brokers**, because the controllers authorize forwarded admin requests.
- **Why the others are wrong:** A — there is no optional `kafka-security` jar; the class was deleted, not relocated. C — `zookeeper.connect` no longer exists in 4.x, and adding it would not make the missing class appear. D — removing `authorizer.class.name` leaves the cluster with **no authorization at all**; `allow.everyone.if.no.acl.found` is only consulted by an authorizer that is actually running.
- 🧠 **Key point / trap:** this is the canonical CCAAK version trap. Any option mentioning `AclAuthorizer`, `--zookeeper`, `zookeeper.connect`, `zookeeper.set.acl` or znodes is wrong on Kafka 4.x. Note also the second half of the answer: forgetting the **controllers** leaves forwarded admin operations unauthorized.
- 📎 Source: `resources/kip-801-standard-authorizer.md` and `resources/kafka-authorization-acls.md` (enabling the authorizer on all nodes).

### Question 17 — Answer: **B**

- **Why correct:** consuming needs `Read` + `Describe` on the **Topic** and `Read` on the **Group**. Producing works, so the topic side is fine; the exception names the group explicitly, so the missing grant is `Read` on `Group:billing-etl`.
- **Why the others are wrong:** A — adds a topic permission that is evidently not the problem, and `Read` on the topic may already be present. C — `Describe` on Cluster is what `ListGroups` needs; it does not let a member join a group. D — granting `All` on every topic is both far too broad and still does not touch the Group resource, so the error would persist.
- 🧠 **Key point / trap:** the exception class name **is** the resource type. `TopicAuthorizationException` → Topic, `GroupAuthorizationException` → Group, `ClusterAuthorizationException` → Cluster, `TransactionalIdAuthorizationException` → TransactionalId. Read it before touching anything.
- 📎 Source: `resources/kafka-authorization-acls.md` (OFFSET_COMMIT / JOIN_GROUP require Read on Group).

### Question 18 — Answer: **B**

- **Why correct:** `allow.everyone.if.no.acl.found=true` relaxes access only for a resource that matches **no ACL at all**. The moment the topic has one ACL, the normal rule applies again: allowed principals are those with a matching ALLOW, everyone else is denied. Adding one grant for `svc-search` therefore revoked implicit access for all the other applications.
- **Why the others are wrong:** A — Kafka does not synthesise Deny rules; the default outcome is simply "no match → deny". C — the setting applies to every resource type, not just groups. D — pattern type does not change the semantics of the setting, and the ACL in the scenario is literal anyway.
- 🧠 **Key point / trap:** this is the single most expensive misunderstanding in ACL rollouts. Treat `allow.everyone.if.no.acl.found=true` as a **per-resource** switch that flips the instant that resource gets its first ACL — which is why the migration order must be "write all ACLs for a topic, then verify, then move on", never "add one and see".
- 📎 Source: `resources/kafka-authorization-acls.md` and `resources/confluent-acl-overview-at-scale.md` (evaluation and defaults).

### Question 19 — Answer: **C**

- **Why correct:** Kafka evaluates DENY before ALLOW, unconditionally. There is no notion of specificity or ordering between ACLs: if any DENY matches the (principal, operation, resource, host) tuple, the request is refused, however many ALLOWs also match. To restore access the DENY must be removed (or narrowed by host).
- **Why the others are wrong:** A — this imports IAM-style "most specific wins" reasoning, which Kafka does not implement. B — ACLs are a set, not an ordered list; creation time is irrelevant. D — there are no reserved-name rules for topics ending in `.dlq.v1`; topic names are only constrained by the legal character set and length.
- 🧠 **Key point / trap:** "Deny beats Allow, always" is one of a handful of rules worth memorising word for word. In practice it means DENY entries should be rare and documented — they are invisible to anyone reading only the ALLOW list for a prefix.
- 📎 Source: `resources/confluent-acl-overview-at-scale.md` ("deny ACLs take precedence").

### Question 20 — Answer: **A**

- **Why correct:** `--list --topic <name>` with the default pattern type only returns ACLs stored against that **literal** pattern. Access is very likely granted through a `PREFIXED` pattern (`payments.`) or the wildcard `*`. `--resource-pattern-type match` is documented as the filter that "will perform pattern matching to list or remove all ACLs that affect the supplied resource(s)" — literal, wildcard and prefixed together.
- **Why the others are wrong:** B — `prefixed` as a filter lists ACLs whose pattern type is prefixed **and whose name equals the string given**, so it would look for a prefix literally called `payments.orders.created.v1`, not for prefixes that cover it. C — cluster ACLs do not grant topic writes. D — that lists ACLs on the wildcard resource only, missing every prefixed ACL.
- 🧠 **Key point / trap:** `literal` and `prefixed` **create** ACLs; `any` and `match` only **query** them. When an ACL audit says "there is nothing here" and reality disagrees, `match` is the command that reconciles the two.
- 📎 Source: `resources/kafka-authorization-acls.md` (`--resource-pattern-type` semantics and the `match` example).

### Question 21 — Answer: **A, C**

- **Why correct:** A — the documented expansion of `--producer` is ALLOW on `WRITE`, `DESCRIBE` and `CREATE` for the topic resource. C — because the pattern type is `prefixed`, the ACL matches by name prefix, so any topic created later whose name starts with `payments.` is covered with no further ACL work. That is precisely why naming conventions matter.
- **Why the others are wrong:** B — inverted implication. `WRITE` implicitly grants `DESCRIBE`, never `READ`; reading requires an explicit `READ` grant. D — `--producer` touches only the Topic resource; group permissions come from `--consumer --group`. E — `--idempotent` adds `IdempotentWrite` on Cluster, which brokers **older than 2.8** required; on a 4.3 broker a plain `Write` on the topic is sufficient for an idempotent producer.
- 🧠 **Key point / trap:** two implicit-permission facts decide what "least privilege" really means — READ/WRITE/DELETE imply DESCRIBE, and ALTER_CONFIGS implies DESCRIBE_CONFIGS. And option E is the "old default" trap: `IdempotentWrite` is genuine Kafka history, just not current practice.
- 📎 Source: `resources/kafka-authorization-acls.md` (`--producer` expansion, IdempotentWrite note) and `resources/confluent-acl-overview-at-scale.md` (implicitly-derived operations).

### Question 22 — Answer: **A, C**

- **Why correct:** A — a naming convention plus prefixed ACLs is the documented way to manage families of topics; it collapses hundreds of per-topic entries into a handful per tenant and removes ACL work from the "create a topic" path entirely. C — "create one principal per application and give each principal only the ACLs required" is the practice that makes both auditing and revocation possible; shared principals make every later question ("who is using this?") unanswerable.
- **Why the others are wrong:** B — super users bypass the authorizer completely, so this deletes authorization rather than simplifying it, and network segmentation cannot distinguish two applications on the same host. D — as Question 18 showed, this setting is per-resource and collapses as soon as a topic gets its first ACL; it is also explicitly discouraged in production. E — a blanket `User:*` ALLOW is the same as having no authorization, and quotas limit throughput, not access.
- 🧠 **Key point / trap:** scale problems in ACLs are solved by **structure** (naming + prefixes + one principal per app), never by **weakening** (super users, allow-everyone, wildcards). Any option that reduces the ACL count by reducing enforcement is the wrong kind of simplification.
- 📎 Source: `resources/confluent-acl-overview-at-scale.md` (managing ACLs at scale).

### Question 23 — Answer: **B**

- **Why correct:** with `StandardAuthorizer` an ACL change is a record appended to `__cluster_metadata` by the active controller. Brokers apply it only after they replay that record, so there is a short window in which the controller has acknowledged the change and a given broker has not yet seen it. Authorization is therefore eventually consistent, and a pipeline that starts an application in the same second as it creates the ACL will occasionally lose that race.
- **Why the others are wrong:** A — `kafka-acls.sh` returns after the controller has committed the change; it is not fire-and-forget, and a `--list` immediately afterwards would typically succeed while a broker still lagged. C — ACLs are not refreshed on the `metadata.max.age.ms` schedule; that is a **client-side** metadata refresh interval. D — `allow.everyone.if.no.acl.found` is consulted only when no ACL matches, and it is a static setting, not a first-request special case.
- 🧠 **Key point / trap:** the operational habit that follows is worth more than the fact itself: **create ACLs as a separate, earlier pipeline stage**, and retry the first connection. Intermittent authorization failures right after a grant are a propagation symptom, not a configuration bug.
- 📎 Source: `resources/kip-801-standard-authorizer.md` (ACLs stored in the metadata log, brokers replay the log).

### Question 24 — Answer: **B**

- **Why correct:** the two DENY lines name exactly what is missing — `Read` on `Topic:payments.orders.created.v1` and `Read` on `Group:billing-etl`. That is precisely the expansion of `--consumer --topic <t> --group <g>`: `READ` and `DESCRIBE` on the topic plus `READ` on the group. Minimal, and it matches the evidence rather than guessing.
- **Why the others are wrong:** A — `All` grants every operation including `Delete` and `Alter` on that topic; it fixes the symptom while creating a much larger privilege than the service ever had. C — `--producer` grants WRITE/DESCRIBE/CREATE, which is the wrong direction entirely and leaves both denials in place. D — super user status removes the service from authorization altogether, and it needs a restart because `super.users` is a static configuration.
- 🧠 **Key point / trap:** the authorizer log is the **specification** for the fix. Denials are logged at INFO by default (allows only at DEBUG), so the DENY lines are there without changing any logging configuration — which is why `kafka-authorizer.log` is the first file to open for any authorization incident.
- 📎 Source: `resources/kafka-authorization-acls.md` (`--consumer` expansion) and `README.md` mục A.5 (audit, DENY=INFO / ALLOW=DEBUG).

### Question 25 — Answer: **B**

- **Why correct:** the documentation states the delimiter is a **semicolon** precisely because SSL distinguished names may contain commas: `super.users=User:Bob;User:Alice`. Written with a comma the whole string is parsed as one principal named `kafka-admin,User:kafka-broker`, which matches nobody — so neither the admin nor the broker principal is a super user, and both admin commands and replication start failing authorization.
- **Why the others are wrong:** A — `super.users` is a broker/controller-side setting; clients know nothing about it. C — the format is `PrincipalType:name`, and `User` is the type; `Principal:User:...` is not a thing. D — `super.users` is independent of `allow.everyone.if.no.acl.found`; super users bypass the authorizer whether or not that flag is set.
- 🧠 **Key point / trap:** remember *why* the delimiter is a semicolon and you will never get it wrong — DNs contain commas. Related habit: set `super.users` **before** enabling the authorizer, and verify the exact principal string in `kafka-authorizer.log`, or you will lock yourself out of your own cluster.
- 📎 Source: `resources/kafka-authorization-acls.md` (super users, semicolon delimiter, case-sensitive `User`).

### Question 26 — Answer: **B**

- **Why correct:** Kafka has no encryption-at-rest feature — the security overview page lists authentication, encryption **in transit**, authorization and pluggable authorization, and says nothing about data on disk. The two real options are infrastructure-level volume or disk encryption (transparent to Kafka), or client-side payload encryption (protects even against a cluster administrator, at the cost of losing broker-side processing and content-based compaction, plus you own the key management).
- **Why the others are wrong:** A — `log.encryption.enabled` and `log.encryption.key.file` do not exist; inventing plausible configuration names is a common distractor pattern. C — TLS protects bytes on the wire; the broker decrypts on receipt and writes plaintext segments. D — compaction is a retention policy and compression is a space optimisation; neither provides any confidentiality.
- 🧠 **Key point / trap:** when an option names a configuration you have never seen, check it against the real configuration reference rather than trusting that it sounds right. "Kafka does not have this built in" is a legitimate and frequently correct answer in the Security domain.
- 📎 Source: `resources/kafka-security-overview-and-listeners.md` (the four supported security measures — encryption at rest is not among them).

### Question 27 — Answer: **`C → D → A → B`**

- **Why correct:** the documented phases are: incrementally bounce to open the additional secured ports while keeping `PLAINTEXT` open (C); restart the clients against the secured port (D); incrementally bounce again to switch broker-to-broker traffic to the secured protocol (A); a final incremental bounce to close the `PLAINTEXT` port (B). A `PLAINTEXT` port must remain open throughout so that brokers and not-yet-migrated clients can keep communicating.
- **Why the others are wrong:** any order that closes `PLAINTEXT` before the last phase splits the cluster or cuts off clients. Switching inter-broker security before the new ports exist on every node (A before C) breaks replication during the roll. Moving clients before the secured ports exist (D before C) simply fails to connect.
- 🧠 **Key point / trap:** clients move **between** the two broker bounces, not before and not last. Also remember the per-node discipline the same page prescribes: stop brokers cleanly with SIGTERM and wait for the restarted replica to rejoin the ISR before touching the next node.
- 📎 Source: `resources/kafka-incorporating-security-running-cluster.md` (four phases, verbatim).

### Question 28 — Answer: **1-E, 2-D, 3-A, 4-C, 5-B**

- **Why correct:** (1) `SaslAuthenticationException` naming the mechanism is a credential failure — wrong or deleted SCRAM password (E). (2) "Bootstrap broker disconnected" on the client with "SSL handshake failed" on the broker means the client spoke the wrong protocol to that port, for example `PLAINTEXT` into a `SASL_SSL` listener (D). (3) `SunCertPathBuilderException: unable to find valid certification path` is a trust-chain failure — the CA (or an intermediate) is missing from the client truststore (A). (4) A hard, error-free throughput ceiling is the signature of a quota: the broker delays responses and returns `throttle_time_ms` instead of raising an exception (C). (5) `TransactionalIdAuthorizationException` names its own resource type — the principal lacks `Write` on the `TransactionalId` (B).
- **Why the others are wrong:** the classic mis-pairings are 1↔3 (both "TLS/credentials feel similar" but one is an authentication failure and the other a certificate-chain failure) and 2↔3 (both surface as connection failures, but 2 never gets far enough to validate a certificate — the protocols do not match at all). Pairing 4 with any security cause is the "silent failure" trap: quotas produce no exception anywhere.
- 🧠 **Key point / trap:** three questions in order, every time — *did the connection establish?* (protocol/TLS) → *did it authenticate?* (credential) → *was the operation permitted?* (ACL). A symptom with **no** error message at all belongs to a fourth category: quotas.
- 📎 Source: `README.md` bảng quyết định 2 (Buổi C), `resources/kafka-ssl-operations.md`, `resources/kafka-authorization-acls.md`, và `../../../CCDAK/study-plan/week-07/resources/kafka-quotas.md`.

### Question 29 — Answer: **C**

- **Why correct:** Cluster Linking (Confluent Platform) has brokers on the destination cluster fetch directly from the source and replicate partitions byte-for-byte, so offsets on the destination are **identical** to the source. Consumers can fail over and resume at the same offsets with no translation step. The company already runs Confluent Platform, so the feature is available.
- **Why the others are wrong:** A — MirrorMaker 2 writes records as a new producer on the target, so offsets differ; `MirrorCheckpointConnector` provides offset **translation**, which is exactly the extra step the requirement forbids. B — `IdentityReplicationPolicy` only preserves **topic names** (no `source.` prefix); it does nothing about offsets. D — a stretch cluster avoids the problem but is a different architecture with strict latency requirements, and `min.insync.replicas=1` would undermine the durability the workload needs.
- 🧠 **Key point / trap:** the discriminator between MM2 and Cluster Linking in the exam is almost always the word **offset**. "Offsets must be preserved / identical / byte-for-byte" → Cluster Linking. "Apache Kafka only, no Confluent" → MM2 plus offset translation.
- 📎 Source: `../../CCAAK-STUDY-PLAN.md` §5 (bảng Disaster recovery: MM2 vs Cluster Linking vs stretch cluster).

### Question 30 — Answer: **A, B**

- **Why correct:** A — `broker.rack` makes the controller distribute the replicas of each partition across as many distinct racks as possible when partitions are created or reassigned, which is what survives the loss of an entire zone. B — a KRaft quorum tolerates the loss of `(N-1)/2` voters: 1 of 3, 2 of 5.
- **Why the others are wrong:** C — rack awareness affects **placement decisions**; existing partitions are not moved automatically and need `kafka-reassign-partitions.sh` (with a throttle). D — reading from the closest replica is follower fetching (KIP-392) and additionally requires `replica.selector.class=RackAwareReplicaSelector` on the brokers and `client.rack` on the consumers. E — an even number of voters adds a voter without adding fault tolerance: 4 voters still tolerate only 1 failure, same as 3, while making elections more expensive; quorums are sized 3 or 5.
- 🧠 **Key point / trap:** rack awareness is a **placement** feature, not a **routing** feature, and not a **repair** feature. Three separate mechanisms — placement (`broker.rack`), routing (KIP-392), repair (reassignment) — that the exam likes to blur together.
- 📎 Source: `../../CCAAK-STUDY-PLAN.md` §4 Domain 5 và §6 (KRaft quorum 3 hoặc 5, chịu mất `(N-1)/2`).

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (24+/30) | Vượt checkpoint thoải mái. | Review 100% câu sai và ghi vào sổ câu sai kèm **lý do sai** (thiếu kiến thức / đọc sót qualifier / dính bẫy version / hết giờ). Sang [Tuần 6](../week-06/README.md). |
| **70–79%** (21–23/30) | **Đạt checkpoint**, nhưng còn lỗ hổng cục bộ. | Xác định nhóm thấp nhất trong bảng chấm điểm ở trên, đọc lại đúng mục Buổi A tương ứng và **làm lại lab của mục đó** (listener → Lab 5.1 · rotation → Lab 5.2 · SASL → Lab 5.3 · ACL → Lab 5.4 + 5.5). Rồi mới sang Tuần 6. |
| **< 70%** (≤ 20/30) | ❌ **Chưa qua checkpoint — KHÔNG sang Tuần 6.** | Làm lại **Lab 5.1, 5.2, 5.4, 5.5** từ đầu (security là domain mà lab thay thế được lý thuyết, không chiều ngược lại), đọc lại `resources/` theo đúng thứ tự trong [INDEX](resources/INDEX.md), rồi tự trộn một bộ 30 câu mới từ questions.md Tuần 1–5 và thi lại. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai**, phân loại theo 5 nhóm của tuần (**listener · TLS/rotation · SASL/credential · ACL · version trap**) và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may cũng tính là câu sai.
> 📌 Riêng nhóm **version trap** (câu 11, 12, 16, 21, 25): sai ở đây là dấu hiệu bạn đang học từ tài liệu đời ZooKeeper. Đọc lại cảnh báo về đề CCAAK công khai ở [§9 kế hoạch tổng](../../CCAAK-STUDY-PLAN.md).
