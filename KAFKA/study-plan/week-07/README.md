# 🟦 Tuần 7 — Security & Testing: TLS/mTLS, SASL, ACLs, Quotas + `MockProducer`/`MockConsumer`/Testcontainers

> **Domain CCDAK:** Testing (8%) + Application Development (28%, phần security client) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 7/10 — có CHECKPOINT: mini-mock CONNECT + STREAMS + TEST ≥70% (trộn Tuần 5–7)
>
> **Điều hướng:** [⬅️ Tuần 6](../week-06/README.md) · [🏠 Kế hoạch tổng](../../KAFKA-STUDY-PLAN.md) · [Tuần 8 ➡️](../week-08/README.md)

## 🎯 Mục tiêu tuần này

- **Phân biệt được** 3 trụ security của Kafka: **encryption** (TLS) / **authentication** (TLS cert hoặc SASL) / **authorization** (ACL) — và biết trụ nào giải quyết lỗi nào trong đề.
- **Cấu hình được** listener nhiều giao thức: `listeners`, `advertised.listeners`, `listener.security.protocol.map`, `inter.broker.listener.name`, `controller.listener.names`; chọn đúng `security.protocol` cho client (`PLAINTEXT` / `SSL` / `SASL_PLAINTEXT` / `SASL_SSL`).
- **Tự tay** tạo CA + keystore/truststore, bật listener `SSL`, rồi bật `SASL_SSL` với SCRAM-SHA-512, tạo user bằng `kafka-configs.sh`, kết nối bằng `kafkajs`.
- **Giải thích được** 4 cơ chế SASL (PLAIN / SCRAM / GSSAPI / OAUTHBEARER): credential lưu ở đâu, đổi được lúc runtime không, cần TLS không, dùng ở đâu (MSK IAM = OAUTHBEARER).
- **Viết được** ACL đúng cho producer / consumer / idempotent / transactional producer với `StandardAuthorizer` (KRaft), hiểu `super.users`, `allow.everyone.if.no.acl.found`, LITERAL vs PREFIXED, Deny thắng Allow.
- **Viết được** unit test với `MockProducer` (`completeNext`/`errorNext`/`history`) và `MockConsumer` (`assign`/`updateBeginningOffsets`/`addRecord`/`schedulePollTask`), integration test với Testcontainers, contract test schema compatibility trong CI.
- **Chốt checkpoint:** đạt **≥70%** ở MINI-MOCK CONNECT + STREAMS + TEST (~30 câu trộn Tuần 5–7) trước khi sang Tuần 8.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Ba trụ security & vị trí trong luồng dữ liệu**

- **Encryption in transit** = TLS (Kafka gọi là "SSL" trong tên config). Bảo vệ byte trên đường truyền client↔broker, broker↔broker, broker↔controller. Chi phí CPU đáng kể (mất zero-copy `sendfile`, Confluent ước tính tới ~30% throughput).
- **Authentication** = "bạn là ai": bằng **TLS client cert (mTLS)** hoặc bằng **SASL** (PLAIN / SCRAM / GSSAPI / OAUTHBEARER). Kết quả là một **principal** dạng `User:alice`.
- **Authorization** = "bạn được làm gì": **ACL** kiểm tra `(principal, operation, resource, host)` qua `Authorizer` (`StandardAuthorizer` với KRaft). Lỗi ở trụ này → `TopicAuthorizationException` / `GroupAuthorizationException` / `ClusterAuthorizationException` / `TransactionalIdAuthorizationException`.
- **Encryption at rest:** Kafka **KHÔNG có built-in**. Giải pháp: mã hoá disk/volume (LUKS, EBS encryption, MSK mặc định mã hoá bằng KMS) hoặc **end-to-end** mã hoá payload ở client (serializer tùy biến, Confluent CSFLE).
- **Audit:** log của authorizer (`kafka.authorizer.logger`, mặc định ghi DENY ở INFO, ALLOW ở DEBUG) + metric `FailedAuthenticationTotal`.
- Security là **tùy chọn**: cluster có thể trộn listener plaintext và listener bảo mật.

**2. Listeners — cấu hình "cổng vào" (rất hay hỏi)**

| Config | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| `listeners` | Broker **bind** cổng nào, tên listener gì. Dạng `{NAME}://{host}:{port}`; host trống = mọi interface | `listeners=PLAINTEXT://:9092,SSL://:9095,SASL_SSL://:9097,CONTROLLER://:9093` |
| `advertised.listeners` | Địa chỉ broker **trả cho client** trong metadata. Client dùng nó cho mọi kết nối sau bootstrap → sai = "kết nối bootstrap OK nhưng produce/consume timeout" | `advertised.listeners=PLAINTEXT://localhost:9092,SSL://localhost:9095` |
| `listener.security.protocol.map` | Map **tên listener → giao thức**. Bắt buộc khi tên listener khác tên giao thức | `INTERNAL:PLAINTEXT,EXTERNAL:SASL_SSL,CONTROLLER:PLAINTEXT` |
| `inter.broker.listener.name` | Listener dùng cho **replication broker↔broker** (thay cho `security.inter.broker.protocol`; không set cả hai) | `inter.broker.listener.name=INTERNAL` |
| `controller.listener.names` | KRaft: listener dành cho **controller quorum** (không được trùng inter-broker) | `controller.listener.names=CONTROLLER` |
| `listener.name.<name>.<config>` | Override config **theo listener** (keystore riêng, JAAS riêng) | `listener.name.external.ssl.keystore.location=...` |

- **`security.protocol` phía client** phải khớp giao thức của **cổng** kết nối: `PLAINTEXT` (không auth, không mã hoá) · `SSL` (TLS; có mTLS nếu broker `ssl.client.auth=required`) · `SASL_PLAINTEXT` (SASL auth, không mã hoá — chỉ dev/Kerberos nội bộ) · `SASL_SSL` (SASL + TLS — chuẩn production).
- ⚠️ Client `PLAINTEXT` nối vào cổng `SSL` → log broker "*Failed authentication ... SSL handshake failed*", client thấy "*Bootstrap broker disconnected*" — không phải lỗi ACL.
- Bẫy cổng: tài liệu mặc định controller **9093**, nên lab tuần này dùng **9095** cho `SSL` và **9097** cho `SASL_SSL` để không đụng compose Tuần 1.

**3. TLS: keystore / truststore / mTLS / hostname verification**

- **Keystore** = "tôi là ai" (private key + cert của chính mình). **Truststore** = "tôi tin ai" (CA cert). Broker luôn cần keystore; client chỉ cần **truststore** nếu TLS một chiều, cần **thêm keystore** khi **mTLS**.
- Config broker: `ssl.keystore.location`, `ssl.keystore.password`, `ssl.key.password`, `ssl.truststore.location`, `ssl.truststore.password`, `ssl.keystore.type` (JKS/PKCS12/PEM), `ssl.enabled.protocols` (mặc định `TLSv1.2,TLSv1.3` trên Java 11+), `ssl.cipher.suites`.
- **`ssl.client.auth`**: `none` (mặc định) / `requested` (không khuyến nghị) / **`required` → mTLS**: client phải trình cert; **principal = DN của cert** (`CN=alice,OU=dev,O=acme`) → rút gọn bằng `ssl.principal.mapping.rules=RULE:^CN=(.*?),.*$/$1/,DEFAULT`.
- **Hostname verification**: `ssl.endpoint.identification.algorithm=https` (**mặc định từ 2.0**) → cert broker phải có **SAN** (`DNS:kafka-1.example.com`, `IP:...`) khớp host client kết nối; CN không còn được dùng. Lỗi "*No subject alternative names matching IP address*" → fix đúng là **cấp lại cert có SAN**, workaround dev là đặt rỗng `ssl.endpoint.identification.algorithm=`.
- **PEM (2.7+)**: `ssl.keystore.key`, `ssl.keystore.certificate.chain`, `ssl.truststore.certificates` — inline PEM hoặc `ssl.keystore.type=PEM` với file; không dùng `ssl.keystore.password`.
- Cert broker cần **cả** `serverAuth` và `clientAuth` (extended key usage) vì broker vừa là server vừa là client (replication).

**4. SASL — 4 cơ chế (bảng phải thuộc)**

| Mechanism | Credential lưu ở đâu | Đổi lúc runtime? | Cần TLS? | Nhận diện trong đề |
| --- | --- | --- | --- | --- |
| `PLAIN` | **Tĩnh** trong JAAS của broker (`user_alice="alice-secret"`) hoặc callback handler tùy biến (LDAP) | ❌ Phải restart broker (trừ khi custom handler) | ✅ **Bắt buộc** (password truyền plaintext) | "user/password đơn giản", "hard-code trong JAAS" |
| `SCRAM-SHA-256` / `SCRAM-SHA-512` | **Trong metadata log KRaft** (`__cluster_metadata`), salt + hash, iterations ≥ 4096 | ✅ `kafka-configs.sh --alter --add-config 'SCRAM-SHA-512=[password=...]' --entity-type users` | ✅ Khuyến nghị (chống MITM) | "không restart broker", "salted challenge", "`kafka-configs.sh --entity-type users`" |
| `GSSAPI` (Kerberos) | KDC / Active Directory; broker + client có **keytab** + **principal** | ✅ (ở KDC) | Không bắt buộc (Kerberos tự bảo vệ auth, nhưng data vẫn plaintext) | "enterprise", "keytab", "krb5.conf", `sasl.kerberos.service.name=kafka` |
| `OAUTHBEARER` | **IdP** bên ngoài (Okta, Keycloak, Entra ID, AWS IAM); token **JWT** ngắn hạn, broker verify bằng **JWKS** | ✅ token tự refresh | ✅ Bắt buộc production | "OIDC", "JWT", "token endpoint", "`MSK IAM`", "client credentials / client assertion" |

- **JAAS**: broker ưu tiên `listener.name.<listener>.<mechanism>.sasl.jaas.config` > file tĩnh `-Djava.security.auth.login.config` (section `KafkaServer`). Client: **`sasl.jaas.config` inline** (khuyến nghị, mỗi client một credential) > file JAAS section `KafkaClient`.
- Client: `sasl.mechanism` **phải nằm trong** `sasl.enabled.mechanisms` của broker; lệch → `UnsupportedSaslMechanismException`. Sai password → `SaslAuthenticationException` (lỗi **fatal**, client không retry).
- Inter-broker: `sasl.mechanism.inter.broker.protocol` (chỉ 1 mechanism) + JAAS broker phải có `username`/`password` của chính nó.
- **SCRAM trong KRaft (KIP-554/KIP-900)**: user cho client tạo runtime bằng `kafka-configs.sh --bootstrap-server`; user cho **inter-broker** phải tồn tại **trước khi broker lên** → `kafka-storage.sh format --add-scram 'SCRAM-SHA-512=[name=admin,password=admin-secret]'` (hoặc tạo qua `--bootstrap-controller`).
- **OAUTHBEARER** production: broker `sasl.oauthbearer.jwks.endpoint.url` + `OAuthBearerValidatorCallbackHandler`; client `sasl.oauthbearer.token.endpoint.url` + `client.id`/`client.secret` (client credentials) hoặc **client assertion** (4.3: `sasl.oauthbearer.assertion.private.key.file`, `sasl.oauthbearer.jwt.retriever.class`), hoặc `sasl.login.callback.handler.class` tùy biến (đây là cách **`aws-msk-iam-auth`** cắm IAM vào). Bản `unsecured` (JAAS `unsecuredLoginStringClaim_sub`) **chỉ dev**.
- **Delegation token**: token ngắn hạn thay keytab/keystore cho job phân tán (Spark), auth qua SCRAM với `tokenauth="true"`; `delegation.token.secret.key` phải giống trên mọi broker/controller; expiry mặc định 24h, max lifetime 7 ngày. Chỉ cần **nhận diện**.

**5. Authorization — ACL với `StandardAuthorizer`**

- Bật: `authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer` (KRaft, KIP-801; ACL lưu trong `__cluster_metadata`). `kafka.security.authorizer.AclAuthorizer` là bản **ZooKeeper cũ, đã gỡ ở 4.0**.
- Mô hình ACL: "**Principal P** is **Allowed/Denied** **Operation O** from **Host H** on **Resource R** matching **ResourcePattern RP**".
  - Principal: `User:alice` (SASL username / cert DN sau mapping / Kerberos primary); `User:ANONYMOUS` cho listener PLAINTEXT; `User:*` = mọi user.
  - Operation: `Read`, `Write`, `Create`, `Delete`, `Alter`, `Describe`, `ClusterAction`, `DescribeConfigs`, `AlterConfigs`, `IdempotentWrite`, `CreateTokens`, `DescribeTokens`, `All`.
  - Resource type: `Topic`, `Group`, `Cluster`, `TransactionalId`, `DelegationToken`, `User`.
  - Pattern: `LITERAL` (mặc định, `*` = wildcard toàn bộ) / `PREFIXED` (`--resource-pattern-type prefixed --topic orders-`).
  - Quy tắc: **Deny thắng Allow**; không có ACL khớp → bị từ chối, trừ khi `allow.everyone.if.no.acl.found=true` (⚠️ production để **false**). `super.users=User:admin;User:ANONYMOUS` (ngăn cách bằng **`;`**) bỏ qua mọi ACL.
- Bảng "cần quyền gì" (thuộc lòng):

| Việc client làm | Operation + Resource cần | Shortcut `kafka-acls.sh` |
| --- | --- | --- |
| Produce thường | `Write` + `Describe` trên `Topic` (Metadata) | `--producer --topic orders` (= Write + Describe + **Create** topic) |
| Producer idempotent (`enable.idempotence=true`, **mặc định**) | **`IdempotentWrite` trên `Cluster`** (từ 2.8 chỉ cần `Write` trên Topic cũng đủ) | `--producer --idempotent` |
| Producer transactional (`transactional.id`) | **`Write` trên `TransactionalId`** + `Describe` TransactionalId (FindCoordinator) | `--transactional-id tx-1 --operation Write --operation Describe` |
| Consume với group | `Read` + `Describe` trên `Topic`, **`Read` trên `Group`** | `--consumer --topic orders --group g1` |
| Tạo topic | `Create` trên `Cluster` **hoặc** `Create` trên `Topic` (2.0+) | `--operation Create --cluster` |
| `kafka-acls.sh` (quản ACL) | `Alter` trên `Cluster` (`DescribeAcls` = `Describe` Cluster) | — |
| Xem/sửa config topic | `DescribeConfigs` / `AlterConfigs` trên `Topic` | — |
| Kafka Streams | Read/Write topic + `Create` topic (internal) + `Read` group; nếu EOS thêm `Write` TransactionalId prefix `<app.id>-` | dùng **PREFIXED** theo `application.id` |
| Kafka Connect worker | Read/Write 3 internal topic + `Read`/`Describe` group `connect-cluster` + `Create` topic | — |

**6. Quotas — chống noisy neighbor**

- 3 loại: **`producer_byte_rate`** / **`consumer_byte_rate`** (bytes/s, **tính theo từng broker**) · **`request_percentage`** (% thời gian I/O + network thread; 100 = 1 thread; tổng = `(num.io.threads + num.network.threads) × 100`) · **`controller_mutation_rate`** (số partition create/delete/s, KIP-599).
- Áp cho `(user, client-id)` > `user` > `client-id`; **8 mức ưu tiên**, cụ thể nhất thắng; `--entity-default` đặt default. Ghi vào metadata log → **hiệu lực ngay, không restart**.
- **Cách broker thực thi**: tính thời gian delay đưa client về dưới quota, **trả response kèm `throttle_time_ms`** (fetch response rỗng), **mute channel** cho đến hết delay; client hiện đại cũng tự ngừng gửi → client **KHÔNG nhận exception**, chỉ thấy throughput giảm và metric `produce-throttle-time-avg` / `fetch-throttle-time-avg` tăng.
- Lệnh: `kafka-configs.sh --alter --add-config 'producer_byte_rate=102400,consumer_byte_rate=204800' --entity-type users --entity-name alice` (thêm `--entity-type clients --entity-name app1` cho cặp).

**7. Security cho ecosystem**

- **Schema Registry**: HTTP basic auth (`basic.auth.credentials.source=USER_INFO`, `basic.auth.user.info=user:pass`) hoặc bearer/OAuth; SR ↔ Kafka dùng `kafkastore.security.protocol=SASL_SSL` + `kafkastore.sasl.*`.
- **Kafka Connect**: worker có `producer.*`/`consumer.*` chung; **connector override** cần `connector.client.config.override.policy=All` (mặc định `None`) rồi khai báo `producer.override.sasl.jaas.config` trong config connector; REST API bảo vệ bằng basic auth extension / TLS.
- **Amazon MSK** (Tuần 9): cổng TLS **9094**, SCRAM **9096**, IAM **9098**; IAM = SASL/OAUTHBEARER với `aws-msk-iam-auth`.
- Cấu hình thời ZooKeeper (`zookeeper.set.acl`, `AclAuthorizer`, `--zookeeper` trong `kafka-configs.sh`) **không còn** ở 4.x — thấy là **đáp án sai**.

**8. Testing (CCDAK 8%)**

- **Test pyramid** cho app Kafka: (1) **unit** logic nghiệp vụ thuần, không Kafka; (2) **unit với mock client** — `MockProducer`/`MockConsumer` (kafka-clients), `TopologyTestDriver` (Streams), `MockSchemaRegistryClient`/URL `mock://` (Avro serde); (3) **integration** với broker thật trong container — Testcontainers `KafkaContainer` (`apache/kafka-native` khởi động < 1 s) hoặc `EmbeddedKafka` (spring-kafka, cùng JVM); (4) **contract test** schema compatibility với Schema Registry trong CI; (5) **e2e/chaos** trên staging (kill instance → test rebalance, idempotency).
- **`MockProducer<K,V>`** (implements `Producer`): `new MockProducer<>(autoComplete, keySer, valueSer)`. `autoComplete=true` → mỗi `send` hoàn thành ngay; `false` → tự điều khiển bằng **`completeNext()`** (thành công) / **`errorNext(RuntimeException)`** (kích callback với exception) → test đường lỗi, retry, DLQ. `history()` trả list `ProducerRecord` đã gửi; `clear()`; `flushed()`, `closed()`. Transaction: `initTransactions`, `transactionCommitted()`, `transactionAborted()`, `commitCount()`, `uncommittedRecords()`, `fenceProducer()` → `ProducerFencedException`.
- **`MockConsumer<K,V>`** (implements `Consumer`, **không thread-safe**): `new MockConsumer<>("earliest")` (constructor `OffsetResetStrategy` deprecated từ 4.0). Chuẩn bị: **`assign(partitions)`** (hoặc `subscribe` + `rebalance(partitions)` vì mock không có coordinator) → **`updateBeginningOffsets(Map)`** (bắt buộc, thiếu → `IllegalStateException` khi poll) → **`addRecord(ConsumerRecord)`** → `poll()` trả record. **`schedulePollTask(Runnable)`**: chạy 1 task mỗi lần `poll` (dùng để `addRecord`, ném `setPollException`, gọi `wakeup()` từ test thread → test poll loop vô hạn). Kiểm tra commit: `committed(Set<TopicPartition>)`. `setPollException(KafkaException)`, `setOffsetsException`, `closed()`.
- **Serde/Schema**: Confluent serializer với `schema.registry.url=mock://<scope>` dùng `MockSchemaRegistryClient` trong bộ nhớ → test Avro/Protobuf không cần SR; `TopologyTestDriver` + `mock://` là combo test Streams Avro.
- **Testcontainers** (Java `org.testcontainers.kafka.KafkaContainer` cho image `apache/kafka`/`apache/kafka-native`, `ConfluentKafkaContainer` cho `cp-kafka`; Node `@testcontainers/kafka`): `kafka.getBootstrapServers()` → cắm vào client thật; test produce→consume, transaction, `read_committed`, consumer lag; chậm hơn mock (giây) nhưng đúng hành vi broker. **EmbeddedKafka** (`@EmbeddedKafka` spring-kafka-test) chạy broker trong JVM test — nhanh nhưng lệch version với production, chỉ Java/Spring.
- **Contract test schema**: `mvn schema-registry:test-compatibility` (plugin `kafka-schema-registry-maven-plugin`) hoặc REST `POST /compatibility/subjects/<subject>/versions/latest` → `{"is_compatible": true}`; `?verbose=true` cho lý do. Chạy trên PR trước khi `register`. `test-local-compatibility` so với schema cũ trong repo, không cần SR.
- **Test hành vi phân tán**: consumer lag (`kafka-consumer-groups.sh --describe` trong test hoặc `admin.listConsumerGroupOffsets` so `endOffsets`), retry logic (inject `errorNext` với `RetriableException` vs fatal), idempotency (gửi trùng key → hệ đích 1 bản), rebalance (kill 1 instance trong Testcontainers → kiểm tra `ConsumerRebalanceListener` commit đúng, không mất/trùng).
- **Node.js**: `kafkajs` không có mock chính thức → **dependency injection** (truyền `producer` giả có `send()` ghi lại lời gọi, `jest.fn()`/`node:test` mock) cho unit test; integration bằng `@testcontainers/kafka`.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + code):** [labs.md](labs.md).

| Lab | Nội dung | Kỹ năng đề thi |
| --- | --- | --- |
| **7.1 ⭐ TLS** | Script tạo CA + keystore/truststore (SAN `localhost`), compose `docker-compose.secure.yml` thêm listener `SSL://:9095`, `kafka-console-producer --producer.config client-ssl.properties`, `kafkajs` với `ssl: { ca }`; thử bỏ SAN để thấy lỗi hostname verification; mTLS tùy chọn | keystore vs truststore, `ssl.endpoint.identification.algorithm`, `ssl.client.auth` |
| **7.2 ⭐ SASL/SCRAM** | Tạo user `alice` bằng `kafka-configs.sh --entity-type users`, listener `SASL_SSL://:9097`, JAAS inline, `kafkajs` `sasl: { mechanism: 'scram-sha-512' }`; sai password → `SaslAuthenticationException`; sai mechanism → `UnsupportedSaslMechanismException` | bảng SASL, `sasl.jaas.config`, `sasl.mechanism` khớp `sasl.enabled.mechanisms` |
| **7.3 ⭐ ACLs** | Bật `StandardAuthorizer`, `super.users`, `allow.everyone.if.no.acl.found=false`; alice bị `TopicAuthorizationException`; thêm `--producer`, `--consumer --group`, PREFIXED; `kafka-acls.sh --list` | producer/consumer shortcut, Group ACL, PREFIXED |
| **7.4 Quotas** | `producer_byte_rate=102400` cho alice, `kafka-producer-perf-test` thấy ~100 KB/s, metric throttle | quota theo user, throttle không ném lỗi |
| **7.5 ⭐ Unit test Java** | Gradle project: `MockProducer` test callback lỗi (`errorNext`), `history()`; `MockConsumer` test commit logic (`assign`/`updateBeginningOffsets`/`addRecord`/`committed`) | API `MockProducer`/`MockConsumer` |
| **7.6 Testcontainers** | `KafkaContainer("apache/kafka:4.3.1")` integration test produce→consume, kèm phương án Node `@testcontainers/kafka` | mock vs container, `getBootstrapServers()` |
| **7.7 Schema contract CI** | `curl -X POST .../compatibility/subjects/orders-value/versions/latest` trong script CI, fail build khi `is_compatible=false` | contract test, `BACKWARD` mặc định |

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định 1 — chọn `security.protocol` + mechanism**

| Tình huống đề | Chọn |
| --- | --- |
| Dev local, không yêu cầu bảo mật | `PLAINTEXT` |
| Chỉ cần mã hoá, xác thực bằng chứng chỉ do PKI nội bộ cấp | `SSL` + `ssl.client.auth=required` (**mTLS**) |
| User/password, đổi mật khẩu không restart broker, không có IdP | `SASL_SSL` + **SCRAM-SHA-512** |
| Đã có Active Directory / Kerberos toàn doanh nghiệp | `SASL_SSL` (hoặc `SASL_PLAINTEXT` nội bộ) + **GSSAPI** |
| SSO / OIDC / JWT / IAM cloud (MSK IAM, Confluent Cloud OAuth) | `SASL_SSL` + **OAUTHBEARER** |
| Nhanh gọn cho demo, chấp nhận restart khi đổi user | `SASL_SSL` + PLAIN (❌ không `SASL_PLAINTEXT` + PLAIN) |
| Job Spark/Flink phân tán, không muốn phát keytab/keystore cho mọi worker | **Delegation token** |

**Bảng quyết định 2 — chọn công cụ test**

| Tiêu chí | `MockProducer`/`MockConsumer` | `TopologyTestDriver` | `EmbeddedKafka` (spring-kafka-test) | Testcontainers `KafkaContainer` | Cluster staging thật |
| --- | --- | --- | --- | --- | --- |
| Cần broker? | ❌ | ❌ | Broker trong JVM test | Docker | ✅ |
| Tốc độ | ms | ms | ~giây (khởi động broker) | ~giây (`kafka-native` < 1 s) | phút |
| Test được gì | logic callback, retry, commit offset, transaction API | topology Streams, window, punctuation (`advanceWallClockTime`), state store | producer/consumer thật với broker giả lập | produce→consume thật, ACL/TLS/SASL, transaction, rebalance, đúng version broker | throughput, lag, chaos, quota |
| Không test được | network, serialization bởi broker, ACL/quota, rebalance thật | broker, rebalance, nhiều instance | khác version production, chỉ JVM/Spring | hiệu năng thật, đa DC | — |
| Ngôn ngữ | Java | Java | Java/Spring | Java, Node, Go, Python… | mọi |
| Vị trí pyramid | unit | unit | integration nhẹ | integration | e2e |

**Đọc thêm (Buổi C):**

- Đọc `resources/kafka-sasl-mechanisms.md` phần OAUTHBEARER production và client assertion (4.3) — CCDAK bản mới hỏi khái niệm này.
- Đọc `resources/kafka-acls-standard-authorizer.md` bảng "Operations and Resources on Protocols": tập trung vào PRODUCE / FETCH / OFFSET_COMMIT / INIT_PRODUCER_ID / CREATE_TOPICS.
- Đọc `resources/mockproducer-mockconsumer.md` rồi tự viết lại 1 test `MockConsumer` không nhìn code mẫu.
- Ôn Tuần 6: `TopologyTestDriver` + `TestInputTopic`/`TestOutputTopic` là "mock" cho Streams — tuần này chỉ ôn qua câu hỏi.

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(tiếng Anh — văn phong đề thật CCDAK.)*

- Làm 30 câu của tuần (security client config + ACL + quotas + testing), ghi sổ câu sai theo nhóm: *listener / TLS / SASL / ACL / quota / mock / integration*.
- **⭐ MINI-MOCK CONNECT + STREAMS + TEST (~30 câu)**: trộn 10 câu Tuần 5 (Schema Registry + Connect) + 10 câu Tuần 6 (Streams) + 10 câu Tuần 7 (Testing + security). Thời gian 45 phút. Mục tiêu **≥70%**.
- **Spaced repetition** 1 / 3 / 7 ngày: flashcard bảng SASL (4 dòng), bảng ACL "cần quyền gì" (9 dòng), API `MockProducer`/`MockConsumer` (10 method), 3 loại quota.
- Chỉ sang Tuần 8 khi mini-mock **≥70%**; nếu chưa, đọc lại phần đáp án giải thích của Tuần 5–6 trước.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
| --- | --- |
| 4 giá trị `security.protocol` | `PLAINTEXT` · `SSL` · `SASL_PLAINTEXT` · `SASL_SSL` (production = `SASL_SSL` hoặc `SSL` + mTLS) |
| `advertised.listeners` | Địa chỉ trả cho client trong metadata; sai → bootstrap OK nhưng produce/consume fail |
| `listener.security.protocol.map` | Bắt buộc khi tên listener ≠ tên giao thức (`INTERNAL:PLAINTEXT,EXTERNAL:SASL_SSL`) |
| Keystore vs truststore | Keystore = **tôi là ai** (private key); truststore = **tôi tin ai** (CA). Client TLS 1 chiều chỉ cần truststore |
| mTLS | `ssl.client.auth=required`; principal = **DN** cert → `ssl.principal.mapping.rules` |
| Hostname verification | `ssl.endpoint.identification.algorithm=https` **mặc định từ 2.0**; cert cần **SAN**; tắt = đặt rỗng |
| `ssl.enabled.protocols` mặc định | `TLSv1.2,TLSv1.3` (Java 11+) |
| PLAIN | Credential **tĩnh** trong JAAS, đổi = restart; **phải** đi với TLS |
| SCRAM | `SCRAM-SHA-256`/`-512`, credential trong **metadata log**, tạo runtime bằng `kafka-configs.sh --alter --add-config 'SCRAM-SHA-512=[password=...]' --entity-type users --entity-name alice`; iterations mặc định **4096**; inter-broker user → `kafka-storage.sh format --add-scram` |
| GSSAPI | Kerberos: keytab + principal + `sasl.kerberos.service.name=kafka` |
| OAUTHBEARER | JWT từ IdP; client `sasl.oauthbearer.token.endpoint.url`; broker `sasl.oauthbearer.jwks.endpoint.url`; **MSK IAM** dùng cơ chế này; `unsecured` chỉ dev |
| Lỗi SASL | Sai mechanism → `UnsupportedSaslMechanismException`; sai password → `SaslAuthenticationException` (fatal, không retry) |
| Authorizer KRaft | `authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer` (KIP-801); `AclAuthorizer` = ZK, đã gỡ 4.0 |
| ACL mặc định | Không ACL khớp → **từ chối**; `allow.everyone.if.no.acl.found=false`; `super.users=User:a;User:b` (ngăn cách `;`); **Deny thắng Allow** |
| `--producer` shortcut | `Write` + `Describe` + `Create` trên Topic; `--consumer --group` = `Read` + `Describe` Topic + `Read` Group |
| Idempotent / transactional | `IdempotentWrite` trên **Cluster** (hoặc `Write` Topic từ 2.8) · `Write` trên **TransactionalId** |
| Pattern type | `LITERAL` (mặc định; `*` = wildcard) · `PREFIXED` (`--resource-pattern-type prefixed`) |
| Quota | `producer_byte_rate` / `consumer_byte_rate` (bytes/s **mỗi broker**) · `request_percentage` · `controller_mutation_rate`; (user, client-id) > user > client-id; broker **delay response + mute channel**, không ném lỗi |
| Encryption at rest | **Không built-in** → disk/volume encryption hoặc mã hoá payload end-to-end |
| `MockProducer` | `new MockProducer<>(autoComplete=false, keySer, valSer)` → `completeNext()` / `errorNext(ex)`; `history()`; `fenceProducer()` |
| `MockConsumer` | `new MockConsumer<>("earliest")`; `assign` → `updateBeginningOffsets` (bắt buộc) → `addRecord` → `poll`; `schedulePollTask`; `committed()`; không thread-safe |
| Testcontainers | `org.testcontainers.kafka.KafkaContainer("apache/kafka-native:…")` → `getBootstrapServers()`; Node `@testcontainers/kafka` |
| Contract test | `POST /compatibility/subjects/<s>/versions/latest` → `{"is_compatible": true}`; `mvn schema-registry:test-compatibility`; mặc định `BACKWARD` |

## ⚠️ Bẫy đề hay gặp

- Thấy "client kết nối được bootstrap nhưng produce timeout / *Connection to node 1 (kafka-1/10.0.0.5) could not be established*" → dễ đổ lỗi firewall/ACL, nhưng đúng là **`advertised.listeners`** trả hostname/IP client không tới được.
- Thấy "*SSL handshake failed*" khi client dùng `security.protocol=PLAINTEXT` → dễ chọn "thiếu ACL", nhưng đúng là **lệch giao thức với cổng** (listener là `SSL`).
- Thấy "*No subject alternative names present / matching*" → dễ chọn đổi keystore client, nhưng đúng là **cert broker thiếu SAN** (hoặc tắt `ssl.endpoint.identification.algorithm` chỉ cho dev).
- Thấy "cần mật khẩu user, đổi không restart broker" → dễ chọn PLAIN, nhưng đúng là **SCRAM** (PLAIN là JAAS tĩnh).
- Thấy "dùng SASL/PLAIN với `SASL_PLAINTEXT` để đơn giản" → **sai**: PLAIN truyền password rõ, phải `SASL_SSL`.
- Thấy `SaslAuthenticationException` → dễ nghĩ retry sẽ hết, nhưng đây là **lỗi fatal**, client đóng kết nối; sửa credential.
- Thấy "đổi sang cluster KRaft, ACL không hoạt động với `kafka.security.authorizer.AclAuthorizer`" → đúng là phải dùng **`StandardAuthorizer`** (AclAuthorizer đã gỡ).
- Thấy "consumer có `Read` trên topic vẫn lỗi `GroupAuthorizationException`" → thiếu **`Read` trên `Group`** — ACL group là resource riêng.
- Thấy "producer mặc định (idempotent) bị `ClusterAuthorizationException`" → thiếu **`IdempotentWrite` trên Cluster** (đề cũ) hoặc broker cũ < 2.8; đừng chọn tắt idempotence trước.
- Thấy "user vừa Allow vừa nằm trong Deny cho 1 host" → dễ nghĩ Allow cụ thể hơn thắng, nhưng **Deny luôn thắng**.
- Thấy "quota bị vượt" → dễ chọn client nhận `QuotaViolationException`, nhưng thực tế broker **delay response + mute channel**, client chỉ thấy throttle-time.
- Thấy "mã hoá dữ liệu trên disk broker bằng config Kafka" → **không có** config đó; dùng disk encryption / mã hoá payload.
- Thấy "test callback lỗi của producer không cần broker" → dễ chọn Testcontainers, nhưng đúng là **`MockProducer(autoComplete=false)` + `errorNext`**.
- Thấy `MockConsumer.poll` ném `IllegalStateException` → thiếu **`updateBeginningOffsets`** (không phải thiếu `subscribe`).
- Thấy "kiểm tra schema mới có tương thích trước khi merge PR" → dễ chọn `register` rồi xem lỗi, nhưng đúng là **`/compatibility` endpoint hoặc `test-compatibility` goal** (không tạo version mới).

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
| --- | --- |
| địa chỉ broker trả cho client, Docker/NAT, bootstrap OK nhưng sau đó fail | **`advertised.listeners`** |
| tên listener tùy ý → giao thức | **`listener.security.protocol.map`** |
| replication dùng listener nào | **`inter.broker.listener.name`** |
| KRaft controller dùng listener nào | **`controller.listener.names`** |
| CA cert phía client | **truststore** (`ssl.truststore.location`) |
| client phải trình cert, principal = DN | **mTLS** `ssl.client.auth=required` + `ssl.principal.mapping.rules` |
| SAN, hostname mismatch | **`ssl.endpoint.identification.algorithm`** (`https` mặc định) |
| user/password, không restart, salted | **SCRAM-SHA-512** + `kafka-configs.sh --entity-type users` |
| keytab, KDC, realm | **GSSAPI** |
| JWT, OIDC, token endpoint, MSK IAM | **OAUTHBEARER** |
| credential inline trong client props | **`sasl.jaas.config`** |
| `UnsupportedSaslMechanismException` | `sasl.mechanism` không thuộc **`sasl.enabled.mechanisms`** |
| KRaft authorizer | **`StandardAuthorizer`** (`org.apache.kafka.metadata.authorizer`) |
| bỏ qua mọi ACL | **`super.users`** (`;`) |
| topic `orders-*` một ACL | **`--resource-pattern-type prefixed`** |
| consumer thiếu quyền group | **`Read` trên `Group`** |
| idempotent producer thiếu quyền | **`IdempotentWrite` trên `Cluster`** |
| transactional producer thiếu quyền | **`Write` trên `TransactionalId`** |
| giới hạn MB/s theo user | **`producer_byte_rate`/`consumer_byte_rate`** |
| giới hạn CPU broker theo client | **`request_percentage`** |
| test callback/retry producer không broker | **`MockProducer` + `errorNext`** |
| test commit offset consumer không broker | **`MockConsumer` + `assign`/`updateBeginningOffsets`/`addRecord`** |
| test topology Streams | **`TopologyTestDriver`** |
| test Avro serde không cần SR | **`mock://` / `MockSchemaRegistryClient`** |
| broker thật trong test, mọi ngôn ngữ | **Testcontainers** |
| kiểm tra schema trước merge | **`/compatibility` REST** hoặc **`schema-registry:test-compatibility`** |

## 🧪 Lab checklist

- [ ] Lab 7.1 ⭐ — Tạo CA + keystore/truststore (SAN `localhost`), bật listener `SSL://:9095`, produce/consume bằng `client-ssl.properties` và `kafkajs` `ssl.ca`; tái hiện lỗi hostname verification.
- [ ] Lab 7.2 ⭐ — Tạo user `alice` SCRAM-SHA-512, listener `SASL_SSL://:9097`, connect bằng `kafkajs`; tái hiện `SaslAuthenticationException` và `UnsupportedSaslMechanismException`.
- [ ] Lab 7.3 ⭐ — Bật `StandardAuthorizer`, tái hiện `TopicAuthorizationException`, cấp `--producer`, `--consumer --group`, PREFIXED; `kafka-acls.sh --list`.
- [ ] Lab 7.4 — Quota `producer_byte_rate=102400` cho alice, `kafka-producer-perf-test` thấy ~100 KB/s.
- [ ] Lab 7.5 ⭐ — Gradle project với test `MockProducer` (`errorNext`, `history`) và `MockConsumer` (commit logic) chạy xanh.
- [ ] Lab 7.6 — Testcontainers `KafkaContainer` produce→consume (Java hoặc Node).
- [ ] Lab 7.7 — Script CI gọi `/compatibility`, fail khi thêm field bắt buộc không default.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Client chỉ cần file nào để nối tới listener `SSL` một chiều? Khi nào cần thêm keystore?**
  **Đáp án gọn:** chỉ **truststore** (CA); cần **keystore** khi broker `ssl.client.auth=required` (mTLS).
- **Kể 4 cơ chế SASL và cơ chế nào cho phép đổi password không restart broker?**
  **Đáp án gọn:** PLAIN / SCRAM-SHA-256|512 / GSSAPI / OAUTHBEARER; **SCRAM** (credential trong metadata log, `kafka-configs.sh --entity-type users`).
- **Producer mặc định Kafka 4.x cần ACL gì trên topic `orders`?**
  **Đáp án gọn:** `Write` + `Describe` Topic (shortcut `--producer` thêm `Create`), và vì idempotent mặc định → `IdempotentWrite` Cluster (hoặc đủ `Write` Topic từ 2.8); transactional thêm `Write` TransactionalId.
- **Consumer group `g1` đọc `orders` cần gì? Không có ACL nào khớp thì sao?**
  **Đáp án gọn:** `Read` + `Describe` Topic, `Read` Group `g1`; không khớp → **từ chối** (trừ `allow.everyone.if.no.acl.found=true` hoặc `super.users`).
- **Broker thực thi quota thế nào? Client thấy gì?**
  **Đáp án gọn:** tính delay, trả response kèm throttle time, **mute channel**; client không nhận exception, chỉ thấy throughput giảm / metric throttle.
- **Test callback lỗi của producer không cần broker dùng gì? Bước nào bắt buộc trước khi `MockConsumer.poll`?**
  **Đáp án gọn:** `MockProducer(autoComplete=false)` + `errorNext(ex)`; `assign` + **`updateBeginningOffsets`** rồi `addRecord`.
- **Kiểm tra schema mới tương thích trong CI mà không tạo version mới?**
  **Đáp án gọn:** `POST /compatibility/subjects/<s>/versions/latest` (`is_compatible`) hoặc `mvn schema-registry:test-compatibility`.
- **⭐ CHECKPOINT:** đã đạt **≥70%** MINI-MOCK CONNECT + STREAMS + TEST (~30 câu, trộn Tuần 5–7) chưa? Nếu chưa → **KHÔNG** sang Tuần 8, ôn lại câu sai theo nhóm trước.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- Apache Kafka Docs 4.3 — Security: Overview, Listener Configuration, Encryption and Authentication using SSL, Authentication using SASL, Authorization and ACLs (`https://kafka.apache.org/43/security/...`).
- Apache Kafka Docs 4.3 — Design → Quotas; Operations → Basic Kafka Operations → Setting quotas.
- KIP-801 (`StandardAuthorizer` lưu ACL trong `__cluster_metadata`), KIP-554 (SCRAM Admin API cho KRaft), KIP-900 (`kafka-storage.sh --add-scram`).
- Javadoc 4.3: `org.apache.kafka.clients.producer.MockProducer`, `org.apache.kafka.clients.consumer.MockConsumer`, `org.apache.kafka.streams.TopologyTestDriver`.
- Testcontainers Java — Kafka module (`java.testcontainers.org/modules/kafka/`); Node `@testcontainers/kafka`.
- Confluent Docs — Schema Registry Maven plugin (`test-compatibility`), Schema Registry REST API `/compatibility`; Confluent Platform Security overview.
- Khoá học: Confluent Developer *Apache Kafka Security* (free), Stephane Maarek *Apache Kafka Series — Kafka Security (SSL SASL Kerberos ACL)*; sách *Kafka: The Definitive Guide* 2nd ed. — Chương 11 *Securing Kafka*; *Kafka Streams in Action* 2nd ed. — chương Testing.

## ✅ Checklist hoàn thành Tuần 7

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (SASL 4 dòng, ACL "cần quyền gì", quota, API mock)
- [ ] Vẽ lại được luồng client → listener → auth → authorizer → quota bằng trí nhớ
- [ ] Hoàn thành 7 lab (TLS, SCRAM, ACL, quota, MockProducer/MockConsumer, Testcontainers, contract test)
- [ ] Làm xong 30 câu [questions.md](questions.md), ghi sổ câu sai
- [ ] **Đạt ≥70% MINI-MOCK CONNECT + STREAMS + TEST (~30 câu)** — CHECKPOINT
- [ ] Vượt Cổng tự kiểm tra
