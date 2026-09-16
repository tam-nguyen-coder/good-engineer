# 🟦 Tuần 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns

> **Domain CCDAK:** AWS + ARCH (bổ trợ, **ngoài phạm vi CCDAK**) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 9/10 — 🎯 **FULL MOCK #1** (60 câu / 90 phút, ngưỡng an toàn ≥ 75%)
>
> **Điều hướng:** [⬅️ Tuần 8](../week-08/README.md) · [🏠 Kế hoạch tổng](../../KAFKA-STUDY-PLAN.md) · [Tuần 10 ➡️](../week-10/README.md)

> ⚠️ **Đọc trước khi học:** phần `Amazon MSK` (Buổi A mục 1–9) **KHÔNG nằm trong đề CCDAK**. Đây là phần "dùng Kafka thật trên AWS" cho công việc — bạn đã đậu `SAA-C03` và đang học `DVA-C02`, nên MSK là nơi ghép Kafka với những gì đã biết (`Kinesis`, `Lambda` ESM, `SQS`, IAM, `Secrets Manager`). **Không tính MSK vào điểm mock CCDAK.** Phần Design patterns (mục 10–18) thì ngược lại: CCDAK **có** hỏi dạng "chọn thiết kế nào" (ordering theo key, số partition, EOS end-to-end, DLQ) — học kỹ.

## 🎯 Mục tiêu tuần này

- **Phân biệt được** 3 lựa chọn MSK — Provisioned **Standard brokers** / Provisioned **Express brokers** / **Serverless** — theo trục "ai quản storage, scale nhanh bao nhiêu, auth nào được hỗ trợ, trả tiền theo gì".
- **Cấu hình được** client Kafka nối MSK bằng **IAM access control** (port **9098**, `SASL_SSL` + `AWS_MSK_IAM` / `OAUTHBEARER`) và viết được IAM policy `kafka-cluster:*` đúng **required actions** + ARN topic/group.
- **Giải thích được** `Lambda` + MSK là **event source mapping (Lambda poll)** — batch, `StartingPosition`, filter, payload base64 — và so với `Kinesis`/`SQS` ESM đã học ở DVA.
- **Chọn được** MSK hay `Kinesis Data Streams` cho 1 bài toán trong 30 giây bằng bảng quyết định.
- **Tự tay** dựng Outbox + CDC (Debezium `EventRouter`) local, idempotent consumer, retry topics + DLQ bằng Node.js, và đo thí nghiệm partition sizing.
- **Giải thích được** 12 pattern (outbox, event sourcing/CQRS, saga, idempotent consumer, retry/DLQ, key design, partition sizing, schema-per-topic, EOS end-to-end, request-reply, claim-check, fan-out) → **vấn đề nào giải, đổi lấy gì**.
- **Chốt checkpoint:** làm **FULL MOCK #1** (60 câu/90 phút) đúng quy trình Buổi D, ghi điểm theo domain, đạt **≥ 75%** mới sang Tuần 10.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

> Mục 1–9 = MSK (ngoài CCDAK, ~1h45). Mục 10–18 = Design patterns (~1h15, CCDAK có hỏi).

**1. `Amazon MSK` là gì — control plane AWS, data plane Kafka nguyên bản**

- `Amazon MSK` = **fully managed Apache Kafka**: AWS lo **control plane** (tạo/sửa/xoá cluster, patch, thay broker hỏng, `KRaft` controller **miễn phí**, storage auto-scaling); bạn dùng **data plane Kafka chuẩn** — `kafka-topics.sh`, `kafkajs`, Connect, Streams **không đổi code**. Liên hệ SAA: giống `RDS` với PostgreSQL — engine là open-source, AWS lo vận hành.
- Cluster nằm trong **VPC do AWS quản**, mỗi broker cắm **1 ENI vào subnet của bạn** (mỗi AZ 1 subnet, tối thiểu 1 broker/AZ với Standard). Client trong VPC/peering/VPN/Direct Connect nối trực tiếp. Lấy địa chỉ broker bằng `aws kafka get-bootstrap-brokers --cluster-arn <arn>` → trả `BootstrapBrokerStringTls` / `...SaslScram` / `...SaslIam` / `...PublicSaslIam`.
- **Public access** chỉ bật được khi cluster đã có **TLS + auth** (IAM/SCRAM/mTLS), tắt unauthenticated access, và nếu dùng ACL thì `allow.everyone.if.no.acl.found=false`. **Multi-VPC private connectivity** = `PrivateLink` do MSK quản để client ở VPC/account khác nối vào (chỉ IAM/SCRAM/mTLS).
- MSK tự phát hiện broker hỏng → thay broker mới, **tái sử dụng EBS cũ** để giảm replicate, **giữ nguyên IP/DNS** → client không đổi `bootstrap.servers`.

**2. Ba lựa chọn cluster — BẢNG quyết định**

| Tiêu chí | **Provisioned — Standard brokers** | **Provisioned — Express brokers** | **Serverless** |
|---|---|---|---|
| Bạn chọn gì | Instance `kafka.t3.small` / `kafka.m5.*` / `kafka.m7g.*`, số broker/AZ (2–3 AZ), EBS **1–16.384 GiB**/broker | Instance `express.m7g.*`, số broker (**bắt buộc 3 AZ**) | Không chọn gì — chỉ VPC/subnet/SG |
| Storage | EBS bạn quản: **storage auto-scaling** (theo `KafkaDataLogsDiskUsed`), **tiered storage** (S3 do AWS quản, retention "vô hạn") | **AWS quản, không giới hạn**, không cần auto-scaling/tiered | AWS quản, retention **không giới hạn** (mặc định 7 ngày) |
| Throughput / scale | Tuỳ instance (`m7g.16xlarge` ~153,8 MBps ghi an toàn) | **~3× throughput/broker** (`express.m7g.16xlarge` ~500 MBps), **scale ~20× nhanh hơn**, recovery **~90% nhanh hơn**, không maintenance window | Quota/cluster: ingress **200 MBps**, egress **400 MBps**, **5/10 MBps per partition**, **2.400 partition** leader (**120** nếu compacted), 500 consumer group, message ≤ **8 MiB** |
| Auth | IAM · SASL/SCRAM · mTLS · (unauth) | IAM · SASL/SCRAM · mTLS | **Chỉ IAM access control** — không ACL Kafka, không SCRAM, không mTLS |
| Broker config | MSK Configuration (subset `server.properties`) | Ít thuộc tính sửa được hơn Standard | **Không** sửa broker config; chỉ topic-level (`retention.ms/bytes`, `max.message.bytes` ≤ 8 MiB, `compression.type`, `cleanup.policy` lúc tạo) |
| Tính tiền | Giờ broker + GiB EBS + (tiered) + data transfer | Giờ broker (đắt hơn Standard cùng size) + storage dùng | **cluster-hour** + **Throughput** (in/out GB) + **partition-hour** + **storage GB-tháng** — không có "giờ broker", nhưng **vẫn tính tiền khi cluster idle** |
| Kafka Streams / share groups | Đủ | Streams chưa đầy đủ, chưa hỗ trợ **KIP-932 share groups** | Đủ Kafka API chuẩn qua IAM |
| Chọn khi | Cần control tối đa, `t3` cho dev, workload ổn định, cần mTLS/SCRAM/ACL | Throughput cao, ghét quản EBS, muốn scale/recover nhanh, vẫn cần tính năng Provisioned | Tải **biến động/không dự đoán**, dev/test, không muốn capacity planning, team đã dùng IAM |

> 🧠 Nhớ: **"cần mTLS / Kafka ACL / sửa `server.properties`" ⇒ Provisioned.** "Ghét EBS nhưng cần throughput cao" ⇒ **Express**, không phải Serverless. "Không quản gì, trả theo dùng" ⇒ Serverless (chấp nhận chỉ IAM). Quota Standard/Express: **90 broker/account**, **30 broker/cluster** (ZooKeeper) hoặc **60** (`KRaft`).

**3. Networking & ports — thuộc bảng port**

| Port | Listener | Public | Dùng khi |
|---|---|---|---|
| **9092** | PLAINTEXT (unauthenticated, không TLS) | — | Chỉ Provisioned Standard, dev; tắt ở production |
| **9094** | TLS (encryption in transit; auth = **mTLS** nếu bật `ACM Private CA`) | **9194** | Client có chứng chỉ; hoặc TLS + unauth |
| **9096** | **SASL/SCRAM** over TLS | **9196** | User/password trong `Secrets Manager` |
| **9098** | **IAM access control** (SASL/OAUTHBEARER over TLS) | **9198** | Default khuyến nghị; **duy nhất** với Serverless |
| 11001 / 11002 | Open Monitoring — **JMX Exporter** / **Node Exporter** | — | Prometheus scrape (mục 8) |

- **Encryption**: at rest = **KMS** (AWS-managed hoặc CMK, chọn lúc tạo, không đổi sau); in transit = TLS **client↔broker** (`TLS` / `TLS_PLAINTEXT` / `PLAINTEXT`) và **broker↔broker** (bật/tắt riêng). Serverless/Express: TLS bắt buộc.
- Security group của broker phải mở port tương ứng cho SG của client/Lambda/Connect. Lỗi "connect timeout tới 9098" gần như luôn là SG hoặc route, không phải Kafka.

**4. Ba cơ chế xác thực — BẢNG + so sánh với ACL Kafka đã học Tuần 7**

| | **IAM access control** | **SASL/SCRAM** + `Secrets Manager` | **mTLS** + `ACM Private CA` |
|---|---|---|---|
| Authentication | Identity IAM (role/user) ký token **SigV4** → SASL/OAUTHBEARER | Username/password SCRAM-SHA-512 lưu trong secret tên bắt đầu **`AmazonMSK_`**, mã hoá bằng **KMS customer-managed key** (không dùng key mặc định), gắn vào cluster bằng `batch-associate-scram-secret` | Client cert do **ACM Private CA** đã gắn vào cluster ký |
| Authorization | **IAM policy** `kafka-cluster:*` — **Kafka ACL không có tác dụng** với identity IAM | **Kafka ACL** (`kafka-acls.sh`), principal `User:<username>` | **Kafka ACL**, principal `User:CN=...` (DN của cert) |
| Port | 9098 / 9198 | 9096 / 9196 | 9094 / 9194 |
| Client Java | `security.protocol=SASL_SSL` · `sasl.mechanism=AWS_MSK_IAM` · `sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;` · `sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler` · jar **`aws-msk-iam-auth`** trong classpath | `security.protocol=SASL_SSL` · `sasl.mechanism=SCRAM-SHA-512` · `sasl.jaas.config=...ScramLoginModule required username="..." password="...";` | `security.protocol=SSL` + `ssl.keystore.*` / `ssl.truststore.*` |
| Client Node (`kafkajs`) | `ssl: true`, `sasl: { mechanism: 'oauthbearer', oauthBearerProvider }` với lib **`aws-msk-iam-sasl-signer-js`** (`generateAuthToken({ region })`) | `sasl: { mechanism: 'scram-sha-512', username, password }` | `ssl: { key, cert, ca }` |
| Serverless | ✅ duy nhất | ❌ | ❌ |
| Ưu / nhược | Không quản credential, dùng role của EC2/Lambda/ECS; audit CloudTrail; giới hạn **100 connection/s/broker** (`IAMTooManyConnections`) | Quen thuộc, client nào cũng hỗ trợ; phải rotate secret | Mạnh nhất cho zero-trust; quản cert phức tạp |

- **IAM policy `kafka-cluster:*`** — action đi kèm **required actions** (thiếu → `TopicAuthorizationException`/`GroupAuthorizationException` dù "đã cho ReadData"):
  - `ReadData` cần `Connect` + `DescribeTopic` + **`AlterGroup`** (AlterGroup = quyền JOIN group, tương đương ACL `READ` trên `Group`); `AlterGroup` cần `DescribeGroup`.
  - `WriteData` cần `Connect` + `DescribeTopic`; producer **idempotent (mặc định từ 3.0)** cần thêm **`WriteDataIdempotently`** trên **cluster ARN**; transactions cần `AlterTransactionalId` + `DescribeTransactionalId`.
  - 4 loại ARN: `arn:aws:kafka:<region>:<acct>:cluster/<name>/<uuid>` · `...:topic/<name>/<uuid>/<topic>` · `...:group/<name>/<uuid>/<group>` · `...:transactional-id/<name>/<uuid>/<txid>`. Wildcard sau `topic/` hợp lệ (`topic/orders-cluster/*/orders-*`).
  - Map với Kafka ACL Tuần 7: `Operation READ on Topic` ↔ `ReadData`; `WRITE on Topic` ↔ `WriteData`; `READ on Group` ↔ `AlterGroup`; `DESCRIBE on Topic` ↔ `DescribeTopic`; `IDEMPOTENT_WRITE on Cluster` ↔ `WriteDataIdempotently`; `CREATE on Cluster/Topic` ↔ `CreateTopic`. Khác biệt: IAM policy gắn vào **identity** (role), ACL gắn vào **resource** trong broker; IAM có `Deny` tường minh + `Condition`, ACL có `Deny` nhưng không có condition.

**5. MSK Configuration — sửa được gì trong `server.properties`**

- MSK Configuration = **tập con** thuộc tính broker bạn được đặt: `auto.create.topics.enable`, `default.replication.factor`, `min.insync.replicas`, `num.partitions`, `log.retention.hours/ms/bytes`, `message.max.bytes`, `log.cleanup.policy`, `unclean.leader.election.enable`, `num.io.threads`, `num.network.threads`, `compression.type`, `transaction.max.timeout.ms`, `offsets.retention.minutes`, `replica.lag.time.max.ms` (10.000–30.000), `group.max.session.timeout.ms`, `log.segment.bytes`… Áp bằng `update-cluster-configuration` → MSK **rolling restart** từng broker.
- **Không sửa được**: `broker.id`, `listeners`/`advertised.listeners`, `log.dirs`, `zookeeper.connect`, `process.roles`, security/SSL props — AWS giữ. `custom.advertised.listeners` chỉ để đặt tên DNS riêng.
- **Default MSK khác Apache Kafka (bẫy!)**: `auto.create.topics.enable=false` (Kafka: true) · `default.replication.factor=3` và `min.insync.replicas=2` với 3 AZ (Kafka: 1/1) · `num.network.threads=5` · `num.replica.fetchers=2` · `unclean.leader.election.enable=true` (Kafka: **false**; cluster tiered: false) · `allow.everyone.if.no.acl.found=true`. Tiered storage: `log.segment.bytes` 128 MiB, `retention.ms` tối thiểu **3 ngày**, `cleanup.policy` chỉ `delete`.
- Serverless: **không có** MSK Configuration; Express: danh sách sửa được ngắn hơn Standard.

**6. `MSK Connect` — Kafka Connect được AWS quản (đối chiếu Tuần 5)**

| Khái niệm Kafka Connect (Tuần 5) | Trong `MSK Connect` |
|---|---|
| Plugin jar trên `plugin.path` của worker | **Custom plugin**: zip/jar upload **S3** → `create-custom-plugin` (quota **100** plugin) |
| `connect-distributed.properties` (converter, `offset.flush.*`…) | **Worker configuration** (quota **100**); mặc định converter = **`StringConverter`** cả key/value (không phải JsonConverter!); các prop nhạy cảm (`bootstrap.servers`, `group.id`, `config/offset/status.storage.topic`, `rest.*`, security) **AWS đặt, không ghi đè** |
| Worker JVM bạn chạy | **MCU** (MSK Connect Unit) = **1 vCPU + 4 GiB RAM**; capacity **Provisioned** (số worker × MCU cố định) hoặc **Autoscaled** (min/max worker, ngưỡng scale-in/out theo `CpuUtilization`; MSK Connect **ghi đè `tasks.max`** theo worker × MCU); vertical 1–8 vCPU qua `update-connector`; quota **60 worker/account**, **10 worker/connector**; mỗi worker chiếm **1 IP** trong subnet |
| Connect REST API `:8083` | **Không có REST API Connect trực tiếp** — quản qua `aws kafkaconnect create-connector / describe-connector / update-connector / delete-connector`; muốn pause/restart task như REST thì… không có, phải update/recreate |
| Credential trong worker | **Service execution role** (IAM role connector assume để nối MSK bằng IAM auth, ghi S3, đọc `Secrets Manager` qua config provider) — connector lỗi ghi S3 = role này thiếu quyền, **không** phải IAM của cluster |
| Log qua log4j | **Log delivery**: CloudWatch Logs / S3 / Firehose |
| Connect tới nguồn/đích | Cùng VPC, hoặc `PrivateLink` + private DNS; ra Internet cần NAT |

- Chạy Kafka Connect **2.7.1 hoặc 3.7.x**; dùng được với **MSK hoặc Kafka tự host** miễn nối được VPC. Use case điển hình: Debezium (RDS/Aurora CDC → MSK), S3 sink, OpenSearch sink. DLQ sink connector vẫn là `errors.deadletterqueue.topic.name` như Tuần 5.

**7. `MSK Replicator`, tiered storage**

- `MSK Replicator` = **MirrorMaker 2 được AWS quản** (Tuần 8): replicate **data + topic config + ACL + consumer group offset (offset sync)** giữa cluster MSK **cùng region (SRR)** hoặc **khác region (CRR)**, cùng account; cũng dùng để **di cư Kafka tự quản → MSK Provisioned**. Bất đồng bộ; metric `ReplicationLatency`, `MessageLag`, `ReplicatorThroughput`.
- 2 chế độ tên topic: **Prefixed** (mặc định; topic đích = `<sourceAlias>.orders` như MM2 → consumer subscribe regex `.*orders`, phù hợp **active-active**) vs **Identical topic name** (giữ nguyên tên → client **không đổi config khi failover**, active-passive/migration; chống loop bằng header `__mskmr`).
- Quota: **15 Replicator/account**, **750 topic/Replicator**, ingress **1 GB/s**, record ≤ **10 MB** cross-region / **20 MB** same-region.
- **Tiered storage** (Standard brokers): segment cũ chuyển sang tier remote do AWS quản (S3) → retention gần vô hạn, EBS chỉ giữ hot data (`local.retention.ms/bytes`); bật per-topic `remote.storage.enable=true`; tất cả broker cùng `kafka.m5/m7g` (không `t3`); consumer đọc data cũ chậm hơn (fetch remote); metric `RemoteCopyLagBytes`, `RemoteFetchBytesPerSec`.

**8. Monitoring MSK (đối chiếu JMX Tuần 8)**

- **4 mức CloudWatch** (`EnhancedMonitoring`): `DEFAULT` (miễn phí) ⊂ `PER_BROKER` ⊂ `PER_TOPIC_PER_BROKER` ⊂ `PER_TOPIC_PER_PARTITION` (có phí, mức sau gồm mức trước). Metric đẩy mỗi **1 phút**.
- Metric phải alarm: `ActiveControllerCount` (**= 1**), `OfflinePartitionsCount` (**= 0**), `UnderReplicatedPartitions` (**= 0**), `UnderMinIsrPartitionCount`, `KafkaDataLogsDiskUsed` (% → kích storage auto-scaling, thường ngưỡng 60–85%), `CpuUser + CpuSystem` (< 60%), `KafkaFileDescriptorsUsagePercent` (< 80%), `IAMTooManyConnections` (> 0 = vượt 100 conn/s), `BurstBalance` (EBS).
- **Consumer lag có sẵn ở DEFAULT** theo group+topic: `EstimatedMaxTimeLag` (giây), `MaxOffsetLag`, `SumOffsetLag`; muốn **per partition** (`OffsetLag`, `EstimatedTimeLag`) → `PER_TOPIC_PER_PARTITION`. Không cần tự chạy `kafka-consumer-groups.sh` hay Burrow như Tuần 8.
- **Open Monitoring với Prometheus**: bật **JMX Exporter :11001** + **Node Exporter :11002** trên broker (miễn phí, chỉ trả cross-AZ transfer); SG mở 11001/11002 cho Prometheus; dashboard Grafana như Lab Tuần 8. Không bật đồng thời open monitoring + public access trên `KRaft`/Express.
- Broker log → CloudWatch Logs / S3 / Firehose. Client-side metric (`records-lag-max`, `request-latency-avg`) vẫn từ JMX của app như Tuần 8.

**9. `Lambda` + MSK, `EventBridge Pipes`, `Glue Schema Registry`, Flink, MSK vs `Kinesis`**

- **`Lambda` event source mapping (ESM)** — cùng cơ chế với `SQS`/`Kinesis`/`DynamoDB Streams` trong DVA: **Lambda poll**, không phải Kafka push. Lambda là **1 consumer group**, đọc tuần tự từng partition, gom **batch** → **invoke đồng bộ** → xong batch thì **commit offset**. Batch lỗi → **retry cả batch** (at-least-once → hàm **phải idempotent**), có `BisectBatchOnFunctionError`, `MaximumRetryAttempts`, `MaximumRecordAgeInSeconds`, `ReportBatchItemFailures`, **on-failure destination** (`SQS`/`SNS`/`S3`).
  - Tham số: `Topics` (chỉ set lúc Create) · `StartingPosition` **TRIM_HORIZON / LATEST / AT_TIMESTAMP** (+`StartingPositionTimestamp`; group **đã có offset commit thì offset thắng**) · `BatchSize` mặc định **100**, tối đa **10.000** · `MaximumBatchingWindowInSeconds` mặc định 500 ms, tối đa **300 s** · `FilterCriteria` (event filtering trên `value` JSON đã decode, `key`, `headers`) · `AmazonManagedKafkaEventSourceConfig.ConsumerGroupId` (tuỳ chỉnh group id, chỉ lúc Create) · **provisioned mode** `ProvisionedPollersConfig` `MinimumPollers` (mặc định 1) / `MaximumPollers` (mặc định 200) · `SchemaRegistryConfig` (Glue SR / Confluent SR để decode Avro/Protobuf).
  - Payload: `event.records["<topic>-<partition>"]` là mảng record; `key`/`value` **base64**; `headers[]` mảng byte; `eventSource` = `aws:kafka` (MSK) hay `SelfManagedKafka`. Function timeout tối đa **14 phút** (không phải 15).
  - Quyền: managed policy **`AWSLambdaMSKExecutionRole`** (`kafka:DescribeClusterV2`, `kafka:GetBootstrapBrokers`, `ec2:*NetworkInterface*`, logs). Cluster IAM auth → thêm `kafka-cluster:Connect/DescribeGroup/AlterGroup/DescribeTopic/ReadData/DescribeClusterDynamicConfiguration`. SCRAM → `secretsmanager:GetSecretValue`.
  - **Self-managed Kafka** (Confluent Cloud, EC2, on-prem): `--self-managed-event-source '{"Endpoints":{"KAFKA_BOOTSTRAP_SERVERS":[...]}}'` + `SourceAccessConfigurations` loại **`VPC_SUBNET` / `VPC_SECURITY_GROUP` / `SASL_SCRAM_512_AUTH` / `SASL_SCRAM_256_AUTH` / `BASIC_AUTH` / `CLIENT_CERTIFICATE_TLS_AUTH` / `SERVER_ROOT_CA_CERTIFICATE`**. Với MSK, VPC lấy từ cluster nên không khai `VPC_SUBNET`.
  - Networking: poller tạo ENI trong subnet cluster; subnet private cần **NAT hoặc VPC endpoint** tới STS/Lambda/Secrets Manager. Lỗi `PROBLEM: Connection error` = SG/route.
- **`EventBridge Pipes`**: source MSK / self-managed Kafka → (filter → enrichment `Lambda`/`Step Functions`/API) → target (`SQS`, `SNS`, `Step Functions`, `Kinesis`, `Lambda`, API Destination…) **không cần code consumer**. Cùng tham số ESM (`StartingPosition`, `BatchSize`, `ConsumerGroupID`). Chọn Pipes khi chỉ cần "chuyển + lọc + enrich", chọn Lambda ESM khi cần logic tuỳ ý.
- **`AWS Glue Schema Registry`** vs Confluent SR (Tuần 5): Glue **serverless, miễn phí**, Avro/JSON Schema/Protobuf, 8 compatibility mode (`BACKWARD` mặc định, `*_ALL` ≈ `*_TRANSITIVE`), kiểm tra theo **checkpoint version**; wire format khác — header **18 byte** (1 version + 1 compression + **16 byte UUID**) vs Confluent **5 byte** (magic + 4 byte ID) → **không đọc lẫn nhau**; Glue **không** có REST API tương thích Confluent, không có subject naming strategy; serde `software.amazon.glue:schema-registry-serde`; tích hợp `Lambda` ESM, `Kinesis`, Flink. Quota **100 registry**, **10.000 schema version**, schema ≤ **170 KB**.
- **`Amazon Managed Service for Apache Flink`** (tên cũ Kinesis Data Analytics): stream processing managed cho MSK/Kinesis, thay Kafka Streams khi cần SQL/Java/Python Flink, checkpoint vào S3 — ngoài CCDAK, chỉ nhận diện.
- **MSK vs `Kinesis Data Streams` — BẢNG quyết định (đề SAA/DVA rất hay hỏi):**

| Tiêu chí | `Kinesis Data Streams` | `Amazon MSK` |
|---|---|---|
| API | AWS API (`PutRecord`, KCL), SDK | **Kafka API** — client/tool/Connect/Streams open-source, không lock-in |
| Đơn vị scale | **Shard** (1 MB/s hoặc 1.000 rec/s ghi, 2 MB/s đọc; on-demand tự scale) | **Partition** + broker; Serverless tự scale, Express scale nhanh |
| Retention | Mặc định **24 h**, tối đa **365 ngày** | Mặc định 7 ngày, **không giới hạn** (tiered / Serverless) |
| Message size | ≤ **1 MB** | mặc định 1 MB, sửa được (Serverless ≤ 8 MiB) |
| Ordering | Theo partition key trong shard | Theo key trong partition |
| Fan-out | Enhanced fan-out 2 MB/s/consumer/shard, tối đa 20 consumer | Consumer group không giới hạn, mỗi group đọc độc lập |
| Ecosystem | Firehose, Flink, Lambda ESM | Connect (300+ connector), Streams, Schema Registry, ksqlDB, Debezium, Flink, Lambda ESM |
| Vận hành | **Đơn giản nhất**, không tuning | Cần hiểu partition/ISR/retention; Serverless giảm bớt |
| Chọn khi | Pipeline AWS-native đơn giản, team nhỏ, chỉ cần stream + Lambda/Firehose | Đã có app Kafka, cần ecosystem/EOS/compaction/Streams, retention dài, multi-cloud/on-prem hybrid, throughput rất cao |

**10. Outbox pattern + CDC — giải bài **dual-write** (ARCH, CCDAK hỏi)**

- **Dual-write**: service `UPDATE orders` rồi `producer.send(OrderCreated)` → **không atomic**: crash giữa 2 bước ⇒ mất event; hoặc send xong DB rollback ⇒ event "ma". Kafka transaction **không** bao DB; 2PC DB↔Kafka không có.
- **Transactional Outbox**: ghi business row + row vào bảng **`outbox`** trong **cùng DB transaction**; **message relay** đọc outbox → publish. 2 kiểu relay: **polling publisher** (job quét — đơn giản, tốn DB, trễ) vs **transaction log tailing = CDC** (`Debezium` đọc WAL/binlog — near real-time, không tốn query).
- Bảng outbox chuẩn Debezium: `id` (UUID = eventId) · `aggregatetype` (→ **topic đích**) · `aggregateid` (→ **Kafka key** ⇒ ordering theo aggregate) · `type` (`OrderCreated`) · `payload` (JSONB). SMT `io.debezium.transforms.outbox.EventRouter`: `route.topic.replacement` mặc định `outbox.event.${routedByValue}`; `table.fields.additional.placement=type:header:eventType`; DELETE bị bỏ qua ⇒ app `INSERT` rồi `DELETE` ngay trong cùng transaction để outbox không phình.
- Outbox = **at-least-once** (relay crash sau publish trước khi ghi nhận) ⇒ consumer **idempotent** (mục 13). Liên hệ DVA: `DynamoDB Streams` + `Lambda` chính là "CDC" phía AWS; Debezium trên **MSK Connect** đọc RDS Postgres cần `rds.logical_replication=1`.

**11. Event sourcing + CQRS**

- **Event sourcing**: state = **chuỗi event bất biến** (`OrderCreated`, `ItemAdded`, `OrderPaid`) trong topic key = aggregate id; state hiện tại = **replay/fold** event. Kafka phù hợp làm **event store** vì append-only + retention dài + replay theo offset; nhưng **không query theo aggregate** → cần snapshot/read model. Không dùng compaction cho event store (sẽ mất lịch sử); dùng compaction cho **snapshot topic**.
- **CQRS**: tách **command side** (ghi event) và **query side** (read model tối ưu đọc). Trong Kafka: `KTable`/state store của Kafka Streams (Tuần 6) chính là **read model materialized**, query qua **interactive queries**; hoặc Connect sink đổ vào Elasticsearch/DynamoDB. Đổi lấy: **eventual consistency** giữa ghi và đọc.

**12. Saga — choreography vs orchestration**

| | **Choreography** | **Orchestration** |
|---|---|---|
| Cơ chế | Mỗi service nghe event, làm việc, phát event tiếp (`OrderCreated` → Payment → `PaymentCompleted` → Inventory…) | 1 **orchestrator** gửi command tới từng service, nhận reply, quyết định bước tiếp / compensating |
| Coupling | Thấp, không điểm trung tâm | Logic tập trung, dễ theo dõi trạng thái |
| Nhược | Luồng khó nhìn tổng thể, dễ vòng lặp event, khó debug compensating | Orchestrator là single point/bottleneck, coupling vào orchestrator |
| Kafka | Topic theo domain event, mỗi service 1 consumer group | Topic command/reply, hoặc Kafka Streams làm state machine; liên hệ DVA: `Step Functions` = orchestrator |
| Compensating action | Mỗi service tự nghe event thất bại | Orchestrator phát `CancelPayment`, `ReleaseStock` |

- Saga **không** ACID — chỉ eventual consistency + bù trừ. Mỗi bước dùng Outbox để phát event/command tin cậy.

**13. Idempotent consumer**

- Kafka + outbox + retry đều là **at-least-once** ⇒ consumer phải chịu **duplicate**. 2 cách dedup:
  - **Theo `eventId`** (UUID trong header/payload, do producer sinh): lưu vào **dedup store** (bảng `processed_events(event_id PK)`, `DynamoDB` conditional write `attribute_not_exists(eventId)` như DVA, Redis SET với TTL). Ghi kết quả nghiệp vụ + `event_id` trong **cùng DB transaction** ⇒ crash giữa chừng vẫn an toàn.
  - **Theo `(topic, partition, offset)`**: lưu offset đã xử lý **trong DB đích** cùng transaction (pattern "offset trong sink"); khi start, `seek()` tới offset đó thay vì tin `__consumer_offsets`. Dedup được cả replay/reset offset, không cần producer gửi id.
- **Idempotent bằng nghiệp vụ**: `UPSERT`/`PUT` thay `INSERT`/`+=`; "set balance = X" thay "balance += 10". Đây là cách rẻ nhất khi làm được.
- Dedup store cần **TTL/retention** (không giữ vĩnh viễn) ≥ khoảng thời gian duplicate có thể xuất hiện (retention topic hoặc thời gian replay tối đa).

**14. Retry & DLQ topics — blocking vs non-blocking, poison pill**

- Kafka **không có DLQ/`maxReceiveCount` sẵn** cho consumer (khác `SQS`); có sẵn chỉ ở **Connect sink** (`errors.tolerance=all` + `errors.deadletterqueue.topic.name`) và **Streams** exception handlers. Consumer app tự thiết kế bằng **topic**.
- **Blocking retry** (retry tại chỗ, `pause()` partition rồi `resume()` sau backoff): **giữ ordering**, đơn giản; đổi lấy: chặn cả partition, rủi ro vượt `max.poll.interval.ms` (5 phút) → rebalance nếu `sleep` thay vì `pause`.
- **Non-blocking retry**: publish sang **`orders-retry-1` → `orders-retry-2` → `orders-dlq`** với header `attempts`, `retry-at`, `original-topic/partition/offset`, `error`; consumer retry topic **`pause()` partition** tới `retry-at` rồi xử lý. Không chặn topic chính; đổi lấy **mất ordering** giữa record retry và record sau nó ⇒ chỉ khi nghiệp vụ chấp nhận (hoặc dùng ordered-retry: registry key đang retry, các record cùng key đi theo).
- **Poison pill** (không deserialize được, schema sai) → **DLQ ngay, không retry** — retry vô ích và phá `max.poll.interval.ms`. Lỗi **tạm thời** (timeout downstream, 5xx, `429`) → retry với **exponential backoff + jitter**. Lỗi **nghiệp vụ vĩnh viễn** (validation) → DLQ.
- DLQ = alert + điều tra; **redrive** thủ công (viết consumer đọc DLQ produce lại topic gốc — không có `StartMessageMoveTask` như `SQS`). `Lambda` ESM có `DestinationConfig.OnFailure` = DLQ mức **batch**.

**15. Key design — ordering, hot key, key null**

- Kafka chỉ đảm bảo ordering **trong 1 partition** ⇒ mọi event cần thứ tự với nhau phải **cùng key** = **entity id** (`orderId`, `userId`, `deviceId`). Key = "đơn vị ordering + đơn vị song song".
- **Hot key** (1 tenant/khách chiếm 40% traffic) → 1 partition quá tải, consumer đó lag. Giải: **salt** key `tenant-42#<0..7>` (mất ordering giữa các salt — chấp nhận nếu chỉ cần ordering theo sub-entity), tách key VIP ra topic/partition riêng (custom partitioner Tuần 3), hoặc đổi đơn vị ordering nhỏ hơn (`orderId` thay `customerId`).
- **Key null** → **sticky partitioner** (Tuần 3): phân bố đều theo batch, **không ordering** — dùng cho metrics/log. Đừng dùng key có cardinality thấp (`country=VN/US`) → chỉ vài partition có data.
- Nhớ Tuần 3: **thêm partition → `hash mod N` đổi → cùng key sang partition khác** → mất ordering và phá compaction. Với keyed topic: lập số partition từ đầu hoặc migrate topic mới.

**16. Partition count sizing — không giảm được**

- Công thức khởi điểm: `partitions = max( throughput_mục_tiêu / throughput_1_partition_producer , throughput_mục_tiêu / throughput_1_consumer , số consumer song song tối đa cần )` × hệ số tăng trưởng 1–2 năm. Đo `throughput_1_partition` bằng `kafka-producer-perf-test.sh` / `kafka-consumer-perf-test.sh` (Lab 9.6), thường vài chục MB/s producer, consumer tuỳ xử lý.
- **Consumer parallelism ≤ số partition**: 12 partition → tối đa 12 consumer trong 1 group có việc; consumer thứ 13 ngồi chơi. Muốn 50 consumer → ≥ 50 partition.
- **Chi phí over-partition**: mỗi partition = file handle + index + segment (broker `KafkaFileDescriptorsUsagePercent`), nhiều leader election khi broker chết (controller phải bầu lại N leader → unavailability window dài hơn), **end-to-end latency tăng** (replication theo từng partition, batch producer nhỏ hơn vì chia nhỏ theo partition), nhiều metadata, `__consumer_offsets` bận hơn. Khuyến nghị cộng đồng: **≤ ~4.000 partition/broker**, **≤ ~200.000/cluster** (`KRaft` cao hơn), MSK Serverless **2.400 leader partition**/cluster.
- **Không giảm được số partition** (`--alter --partitions` chỉ tăng) → sai thì tạo topic mới + migrate. Số partition nên là **bội số** dễ chia cho số consumer (6, 12, 24).

**17. Schema-per-topic vs multi-event topic; EOS end-to-end**

- **1 loại event/topic** (`order-created`, `order-paid`): schema đơn giản, `TopicNameStrategy` (Tuần 5), consumer lọc dễ; **nhược**: mất ordering giữa `OrderCreated` và `OrderPaid` cùng `orderId` vì khác topic. **Multi-event topic** (`orders` chứa mọi event của 1 order): **giữ ordering theo aggregate**, ít topic; cần `RecordNameStrategy` / `TopicRecordNameStrategy` để 1 topic có nhiều schema (hoặc Avro union / Protobuf `oneof`), consumer phải dispatch theo type. Quy tắc: **event cần ordering với nhau → cùng topic + cùng key**.
- **Exactly-once end-to-end** — 3 đoạn, 3 câu trả lời:

| Đoạn | Cơ chế | Ghi chú |
|---|---|---|
| Kafka → Kafka (consume-transform-produce) | **Transactions** (`transactional.id`, `sendOffsetsToTransaction`, consumer `read_committed`) — Tuần 3; Streams `exactly_once_v2` — Tuần 6 | Duy nhất đoạn Kafka **tự** đảm bảo EOS |
| Kafka → DB / HTTP / S3 | **Idempotent sink**: upsert theo key, hoặc lưu `(partition, offset)` cùng transaction DB; Connect sink có EOS chỉ với connector hỗ trợ (JDBC upsert, S3 sink deterministic partitioning) | Kafka transaction **không** bao sink ngoài |
| DB → Kafka | **Outbox + CDC** (mục 10) hoặc Connect source `exactly.once.source.support=enabled` (Tuần 5) | Không dùng dual-write |

**18. Request-reply, claim-check, fan-out, compacted topic as KV, backpressure, multi-region**

- **Request-reply qua Kafka**: requester gửi `request` kèm header **`correlationId`** + **`replyTo`** (reply topic của instance/nhóm); responder produce vào `replyTo` cùng `correlationId`; requester match. Reply topic **1 per requester instance** (hoặc partition riêng) để đúng instance nhận. Latency ms-cỡ, không hợp cho sync HTTP call thuần — cân nhắc gRPC/HTTP trực tiếp.
- **Claim-check**: payload lớn (ảnh, file > 1 MB) → lưu **S3**, message chỉ chứa **pointer** (bucket/key + checksum) → topic giữ nhỏ, không đụng `message.max.bytes`/`max.request.size`. Liên hệ DVA: `SQS Extended Client Library` (S3 + pointer, tới 2 GB) làm đúng việc này. Nhớ: xoá object S3 theo lifecycle ≥ retention topic.
- **Fan-out** = mỗi service **1 consumer group riêng** trên cùng topic — mỗi group nhận đủ mọi record, độc lập offset. **Không cần `SNS`**: Kafka topic vốn là pub/sub bền. Bẫy: cho 2 service **cùng `group.id`** → chia nhau partition, mỗi service chỉ thấy 1 phần.
- **Compacted topic as KV store / changelog**: `cleanup.policy=compact` giữ **giá trị mới nhất mỗi key** (Tuần 2) → bootstrap cache, config distribution, `GlobalKTable` (Tuần 6), `__consumer_offsets`. Xoá key = **tombstone** (value null, giữ `delete.retention.ms` 24 h). Không phải event store.
- **Backpressure**: consumer chậm hơn producer → lag tăng (`records-lag-max`, MSK `SumOffsetLag`). Client-side: `consumer.pause(partitions)` khi queue nội bộ đầy, `resume()` khi rỗng; giảm `max.poll.records`; scale consumer ≤ partition; tách xử lý nặng sang worker pool + commit sau. Producer-side: `buffer.memory` đầy → `max.block.ms` (Tuần 3). Broker: quota `producer_byte_rate`/`consumer_byte_rate` (Tuần 7).
- **Multi-region**: **MM2** (Tuần 8) hoặc **`MSK Replicator`** (mục 7); vấn đề cốt lõi là **offset không giống nhau** giữa 2 cluster → cần **offset translation** (MM2 `MirrorCheckpointConnector` + `RemoteClusterUtils`, MSK Replicator **consumer group offset sync**) để consumer failover đọc tiếp đúng chỗ; active-active cần tránh **loop** (prefix topic / header `__mskmr`) và xử lý conflict theo key.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + code):** [labs.md](labs.md). Lab 9.1/9.2/9.7 chạy trên AWS **có phí** (MSK Serverless tính cluster-hour + partition-hour + throughput **ngay từ lúc cluster `ACTIVE`**, kể cả khi không có message) → luôn `delete-cluster` cuối lab; Lab 9.3–9.6 chạy local với cluster 3 node Tuần 1.

**Lab 9.1 ⭐ — MSK Serverless + IAM auth (AWS, ~40 phút, có phí):** `aws kafka create-cluster-v2 --serverless`, `get-bootstrap-brokers`, IAM policy `kafka-cluster:*` cho topic `orders` + group; chạy `kafka-topics.sh --command-config client-iam.properties` từ EC2 trong VPC (jar `aws-msk-iam-auth`) và Node `kafkajs` + `aws-msk-iam-sasl-signer-js`. Kèm giải thích vì sao **không** mô phỏng được IAM ở local.

**Lab 9.2 ⭐ — `Lambda` ESM cho MSK (AWS + local, ~40 phút):** `aws lambda create-event-source-mapping --event-source-arn <msk> --topics orders --starting-position LATEST --batch-size 100 --filter-criteria ...`; handler Node.js decode base64 `event.records["orders-0"][].value`; test **local** bằng `sam local invoke` với JSON event mẫu MSK đầy đủ.

**Lab 9.3 ⭐ — Outbox + CDC local (~40 phút):** Postgres (`wal_level=logical`) + Debezium Connect (từ Tuần 5); bảng `outbox`; connector `transforms=outbox` EventRouter; app Node ghi `orders` + `outbox` trong **1 transaction** → event xuất hiện ở topic `Order-events` với key = `aggregateid`.

**Lab 9.4 — Idempotent consumer Node (~25 phút):** dedup bằng `node:sqlite` theo `eventId` **và** theo `(topic,partition,offset)`; replay bằng `kcg --reset-offsets --to-earliest` → không xử lý trùng.

**Lab 9.5 — Retry topics + DLQ Node (~35 phút):** `orders` → fail → `orders-retry` với header `attempts`/`retry-at`, delay bằng `pause()` + `setTimeout` → `orders-dlq` sau 3 lần; poison pill đi thẳng DLQ.

**Lab 9.6 — Partition sizing thí nghiệm (~30 phút):** `kafka-producer-perf-test.sh` topic 1/3/12 partition + `kafka-consumer-perf-test.sh` 1 vs 3 consumer → điền BẢNG kết quả; thử `--alter --partitions 1` để thấy "không giảm được".

**Lab 9.7 (Option) — `EventBridge Pipes` MSK → `SQS` (AWS, ~20 phút, có phí):** `aws pipes create-pipe` với `ManagedStreamingKafkaParameters` + filter → `receive-message` ở `SQS`.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Pattern → vấn đề giải quyết → đổi lấy gì (BẢNG tổng — tự viết lại bằng trí nhớ ở Buổi D)**

| Pattern | Vấn đề giải | Cơ chế Kafka | Đổi lấy / bẫy |
|---|---|---|---|
| Outbox + CDC | Dual-write DB ↔ Kafka không atomic | Bảng `outbox` cùng transaction + Debezium `EventRouter` | At-least-once → consumer idempotent; thêm Connect |
| Event sourcing | Cần lịch sử đầy đủ, audit, replay | Topic event bất biến key = aggregate, retention dài | Không query trực tiếp → snapshot/read model |
| CQRS | Read model khác write model | `KTable`/state store, Connect sink | Eventual consistency |
| Saga | Transaction xuyên nhiều service | Choreography (event) / Orchestration (command-reply) | Không ACID; phải có compensating action |
| Idempotent consumer | Duplicate do at-least-once | Dedup store theo `eventId` hoặc `(topic,partition,offset)`; upsert | Store cần TTL; phải ghi cùng transaction với kết quả |
| Retry/DLQ topics | Lỗi tạm thời vs poison pill | `orders-retry-N` + header `attempts`, `orders-dlq` | Non-blocking mất ordering; blocking chặn partition |
| Key = entity id | Ordering theo entity | murmur2 hash → cùng partition | Hot key → salt; thêm partition đổi mapping |
| Partition sizing | Throughput & parallelism | Đo perf-test, tính growth | Over-partition tốn FD/latency/election; **không giảm** |
| Schema-per-topic vs multi-event | Ordering giữa các loại event | Multi-event + `RecordNameStrategy` | Consumer dispatch theo type |
| EOS end-to-end | Không mất, không trùng | Txn (K→K), idempotent sink (K→DB), CDC (DB→K) | Không có "1 config bật EOS toàn tuyến" |
| Request-reply | Cần phản hồi qua Kafka | Header `correlationId` + `replyTo` | Latency, reply topic per instance |
| Claim-check | Payload lớn | S3 + pointer (như `SQS` Extended Client) | Lifecycle S3, 2 hệ thống |
| Fan-out | N service cùng nhận | N consumer group | Trùng `group.id` → chia partition (bẫy) |
| Compacted KV | Cache/config/latest state | `cleanup.policy=compact` + tombstone | Không phải event store |
| Backpressure | Consumer chậm | `pause()/resume()`, `max.poll.records`, quota | Lag tăng, không mất data |
| Multi-region | DR, latency vùng | MM2 / MSK Replicator + offset translation | Async, loop, conflict theo key |

**Checklist thiết kế 1 topic mới (dùng thật ở công việc)**

1. Event nào cần ordering với nhau? → cùng topic, cùng key (entity id). Không cần → key null.
2. Throughput đỉnh + số consumer song song + growth → số partition (bội số 6/12), RF=3, `min.insync.replicas=2`.
3. Retention: `delete` bao lâu (replay cần?) hay `compact` (latest state)? Tiered nếu cần > 7 ngày trên MSK Standard.
4. Schema: Avro/Protobuf + registry (Confluent SR hay Glue SR), compatibility `BACKWARD`; 1 hay nhiều event type/topic.
5. Producer: `acks=all`, idempotent (mặc định), `transactional.id` nếu K→K EOS; sinh `eventId`.
6. Consumer: idempotent (dedup), retry/DLQ topic, `max.poll.interval.ms` phù hợp xử lý, group id **riêng mỗi service**.
7. Auth: MSK IAM (role của workload) → policy `ReadData`/`WriteData` + required actions đúng ARN topic/group.
8. Monitoring: lag (`SumOffsetLag`/`records-lag-max`), `UnderReplicatedPartitions`, DLQ depth alarm.

**Đọc thêm:** *Designing Event-Driven Systems* (Ben Stopford, Confluent — miễn phí) chương về event sourcing/CQRS/saga; *Kafka: The Definitive Guide* 2nd ed. Ch.8 (Exactly-Once), Ch.9 (Building Data Pipelines), Ch.10 (Cross-Cluster Data Mirroring); microservices.io Transactional Outbox / Idempotent Consumer / Saga; AWS MSK Developer Guide *Best practices* (partition per broker, right-size cluster); Confluent blog *Error Handling Patterns in Kafka*.

### 🅳 Buổi D — Practice + Review (~2h) — 🎯 FULL MOCK #1

> 📝 **Bộ câu hỏi của tuần:** [questions.md](questions.md) (28 câu — 14 MSK, 11 pattern, 3 ôn tuần trước) — đáp án: [answers.md](answers.md). Làm **trước** mock, ~30 phút. Câu tag `AWS` **không** tính vào điểm CCDAK.

**Quy trình FULL MOCK #1 (60 câu / 90 phút — làm như thi thật):**

1. **Chọn 1 bộ practice CCDAK 60 câu** bạn chưa từng làm (Confluent official sample questions + 1 bộ practice test có trả phí như Stephane Maarek/Udemy hoặc Whizlabs; tránh bộ ghi defaults cũ mà không chú thích). Bộ này được "đốt" cho mock #1 — mock #2–4 Tuần 10 dùng bộ khác.
2. **Điều kiện thi thật**: 90 phút đếm ngược, không tra cứu, không pause, 1 lượt; đánh dấu câu phân vân để quay lại, mục tiêu **≤ 75 giây/câu** để dư 15 phút review.
3. **Chấm và ghi điểm theo domain** (bảng dưới). Tính % từng domain, không chỉ tổng.
4. **Sổ câu sai**: mỗi câu sai/phân vân → ghi đề, đáp án đúng, **lý do mình sai** (không biết / đọc nhầm / nhớ số cũ / bẫy từ ngữ), map về Tuần nào. Viết file phân tích theo format `aws-saa-c03-analysis-format.md` vào `questions/KAFKA/` cho ≥ 10 câu đáng nhớ nhất.
5. **Quyết định**: **≥ 75%** → sang Tuần 10 theo lịch. **70–74%** → sang Tuần 10 nhưng Buổi A Tuần 10 dành trọn cho domain thấp nhất. **< 70%** → van an toàn của kế hoạch tổng: **lùi lịch thi 1 tuần**, ôn lại cụm yếu trước khi mock #2.

| Domain | Tỉ trọng | ~Số câu trong 60 | Đúng | % | Tuần ôn lại |
|---|---|---|---|---|---|
| DEV — Application Development | 28% | ~17 | | | 3, 4 |
| FUND — Fundamentals | 23% | ~14 | | | 1, 2 |
| CONNECT | 15% | ~9 | | | 5 |
| OBS — Observability | 13% | ~8 | | | 8 |
| STREAMS | 12% | ~7 | | | 6 |
| TEST | 8% | ~5 | | | 7 |
| **Tổng** | 100% | 60 | | **≥ 75%?** | |

- **Spaced repetition** mốc **1 / 3 / 7 ngày**: bộ số MSK (9092/9094/9096/9098 · 100/10.000/300 s · 200/400 MBps · 2.400 · 1 vCPU/4 GiB · 15/750 · 18 vs 5 byte) và bảng pattern Buổi C; ôn xen bộ số Tuần 3–4 vì DEV chiếm 28% mock.
- Tự viết lại bằng trí nhớ: bảng 3 loại cluster, bảng 3 auth, bảng MSK vs Kinesis, bảng pattern → vấn đề.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| 3 lựa chọn MSK | **Standard** (EBS 1–16.384 GiB, tiered, auto-scaling) · **Express** (AWS quản storage, **3×** throughput, **20×** scale, **90%** recovery nhanh hơn, 3 AZ) · **Serverless** (**chỉ IAM**, trả theo throughput + partition-hour + storage) |
| Serverless quota | Ingress **200 MBps** / egress **400 MBps** per cluster; **5/10 MBps** per partition; **2.400** leader partition (**120** compacted); **500** consumer group; message ≤ **8 MiB**; retention không giới hạn |
| Ports | **9092** plaintext · **9094** TLS/mTLS · **9096** SCRAM · **9098** IAM · public **+100** (9194/9196/9198) · Open Monitoring **11001** JMX / **11002** Node |
| Auth | IAM = auth **+ authz** bằng policy, **ACL Kafka vô hiệu**; SCRAM secret tên **`AmazonMSK_*`** + **KMS customer key**; mTLS = **ACM Private CA** + ACL |
| IAM client props | `SASL_SSL` · `AWS_MSK_IAM` · `IAMLoginModule required;` · `IAMClientCallbackHandler` · jar `aws-msk-iam-auth`; Node: `oauthbearer` + `aws-msk-iam-sasl-signer-js` |
| Required actions | `ReadData` ← `Connect` + `DescribeTopic` + **`AlterGroup`** (← `DescribeGroup`); `WriteData` ← `Connect` + `DescribeTopic`; idempotent → **`WriteDataIdempotently`** trên **cluster ARN** |
| ARN | `arn:aws:kafka:<region>:<acct>:{cluster\|topic\|group\|transactional-id}/<cluster-name>/<uuid>[/<name>]` |
| Default MSK ≠ Kafka | `auto.create.topics.enable=false`; RF=3 + `min.insync.replicas=2` (3 AZ); `unclean.leader.election.enable=true`; `num.network.threads=5` |
| MSK Connect | Plugin zip trên **S3**; **MCU = 1 vCPU + 4 GiB**; Provisioned vs **Autoscaled** (CPU threshold, ghi đè `tasks.max`); **service execution role**; mặc định converter **`StringConverter`**; **không có REST 8083**; quota 100/100/60/10 |
| MSK Replicator | SRR/CRR cùng account; replicate data + config + ACL + **offset sync**; **Prefixed** vs **Identical topic name** (header `__mskmr`); **15**/account, **750** topic, 1 GB/s |
| CloudWatch levels | `DEFAULT` ⊂ `PER_BROKER` ⊂ `PER_TOPIC_PER_BROKER` ⊂ `PER_TOPIC_PER_PARTITION`; lag group-level (`EstimatedMaxTimeLag`, `MaxOffsetLag`, `SumOffsetLag`) có ở **DEFAULT**; per-partition lag cần mức cao nhất |
| Metric phải = | `ActiveControllerCount` **1**, `OfflinePartitionsCount` **0**, `UnderReplicatedPartitions` **0**; `KafkaDataLogsDiskUsed` → auto-scaling |
| Lambda ESM | Lambda **poll**; `BatchSize` **100** (max **10.000**); window mặc định 500 ms, max **300 s**; `StartingPosition` TRIM_HORIZON/LATEST/AT_TIMESTAMP; payload **base64**; timeout hàm ≤ **14 phút**; policy `AWSLambdaMSKExecutionRole`; retry cả batch → hàm idempotent; on-failure `SQS`/`SNS`/`S3` |
| Self-managed Kafka ESM | `SourceAccessConfigurations`: `VPC_SUBNET`, `VPC_SECURITY_GROUP`, `SASL_SCRAM_512_AUTH`, `SASL_SCRAM_256_AUTH`, `BASIC_AUTH`, `CLIENT_CERTIFICATE_TLS_AUTH`, `SERVER_ROOT_CA_CERTIFICATE` |
| Glue SR vs Confluent SR | Glue miễn phí, header **18 byte** (16 byte UUID) vs Confluent **5 byte**; `*_ALL` ≈ `*_TRANSITIVE`; không REST tương thích Confluent; quota 100 registry / 10.000 version / 170 KB |
| Kinesis vs MSK | Kinesis: shard 1 MB/s in / 2 MB/s out, record ≤ 1 MB, retention ≤ **365 ngày**, đơn giản. MSK: Kafka API + ecosystem, retention vô hạn, throughput cao |
| Outbox | Bảng `outbox` **cùng DB transaction** + Debezium `EventRouter` (`aggregatetype` → topic, `aggregateid` → key, `id` → header); at-least-once |
| Idempotent consumer | Dedup theo `eventId` (DynamoDB conditional write / bảng PK) hoặc `(topic,partition,offset)` lưu **cùng transaction** với kết quả; upsert |
| Retry/DLQ | Non-blocking `orders-retry-1/2` + header `attempts` (**mất ordering**) vs blocking `pause()`/`resume()` (**giữ ordering**, chặn partition); poison pill → DLQ ngay |
| Partition sizing | parallelism ≤ partition; over-partition tốn FD/election/latency; **không giảm được**; MSK Serverless 2.400 |
| EOS end-to-end | K→K: transactions/`exactly_once_v2`; K→DB: idempotent sink; DB→K: outbox/CDC |
| Fan-out | Mỗi service **1 `group.id` riêng**; trùng group = chia partition, không phải fan-out |

## ⚠️ Bẫy đề hay gặp

- Thấy "không muốn quản broker/EBS, cần scale nhanh, **vẫn cần mTLS/ACL**" → dễ chọn Serverless, nhưng Serverless **chỉ IAM** → đúng là **Express brokers** (Provisioned).
- Thấy "trả tiền theo throughput, tải biến động, ít vận hành nhất" → chọn Express là thừa → đúng là **Serverless** (chấp nhận chỉ IAM, không sửa broker config).
- Thấy "đã cấp `kafka-cluster:ReadData` mà consumer vẫn `GroupAuthorizationException`" → tưởng sai ARN topic, nhưng thiếu **`AlterGroup` + `DescribeGroup` trên ARN group** (required actions).
- Thấy "producer mặc định báo `ClusterAuthorizationException` dù có `WriteData`" → idempotence mặc định bật → thiếu **`WriteDataIdempotently` trên cluster ARN**.
- Thấy "cluster IAM, tạo ACL bằng `kafka-acls.sh` để chặn user" → **ACL không có tác dụng với identity IAM** → phải dùng IAM policy (`Deny`).
- Thấy "SCRAM secret tạo trong Secrets Manager nhưng `batch-associate-scram-secret` lỗi" → tên secret không bắt đầu **`AmazonMSK_`** hoặc dùng **KMS key mặc định** (phải customer-managed).
- Thấy "topic tự tạo khi producer gửi lần đầu ở Kafka local nhưng MSK báo `UnknownTopicOrPartition`" → default MSK **`auto.create.topics.enable=false`**.
- Thấy "Lambda nhận message từ MSK" → dễ nghĩ Kafka **push** → đúng là **ESM Lambda poll** (giống `Kinesis`/`SQS`), Lambda là consumer group.
- Thấy "Lambda đọc `record.value` ra chuỗi lạ" → quên **base64 decode**; và `records` là **map `topic-partition` → array**, không phải array phẳng như `Kinesis`.
- Thấy "1 record lỗi, Lambda xử lý lại cả 100 record" → hành vi chuẩn **retry cả batch** → dùng `ReportBatchItemFailures`/`BisectBatchOnFunctionError` + hàm idempotent, không phải giảm `BatchSize` về 1.
- Thấy "chỉ muốn Lambda nhận event `status=PAID`" → viết `if` trong code là tốn tiền → đúng là **`FilterCriteria`** trên ESM.
- Thấy "cần Debezium đọc RDS vào MSK, không muốn quản worker" → dễ chọn Connect trên EC2/ECS → đúng là **MSK Connect** (plugin S3 + autoscaled capacity); connector lỗi ghi S3 → **service execution role**.
- Thấy "MSK Connect: gọi REST `:8083/connectors` để pause" → **không có** REST Connect trên MSK Connect → dùng API `kafkaconnect`.
- Thấy "DR cross-region cho MSK, consumer failover tiếp đúng offset" → dựng MM2 là câu trả lời cũ → đúng là **MSK Replicator + consumer group offset sync**; "không đổi tên topic khi failover" → **Identical topic name**.
- Thấy "xem lag từng partition trong CloudWatch" → `DEFAULT` chỉ có `SumOffsetLag`/`MaxOffsetLag` theo group → cần **`PER_TOPIC_PER_PARTITION`**.
- Thấy "schema registry cho MSK, miễn phí, không quản server" → chọn `cp-schema-registry` trên EC2 là sai hướng → **Glue Schema Registry** (nhưng không tương thích wire format Confluent).
- Thấy "đảm bảo event chỉ phát khi DB commit" → chọn `acks=all` hay Kafka transaction là **sai** (không bao DB) → **Outbox + CDC**.
- Thấy "consumer xử lý trùng sau khi reset offset" → tưởng bug producer → **idempotent consumer** (dedup theo eventId/offset), Kafka là at-least-once.
- Thấy "retry lỗi tạm thời nhưng phải giữ ordering theo key" → non-blocking retry topic **mất ordering** → dùng **blocking retry `pause()`/`resume()`** (hoặc ordered-retry).
- Thấy "record không deserialize được, consumer retry mãi rồi rebalance" → poison pill → **DLQ ngay**, không retry; `max.poll.interval.ms` bị vượt do retry tại chỗ.
- Thấy "topic 24 partition quá nhiều, giảm về 12" → **không giảm được** → tạo topic mới + migrate.
- Thấy "2 microservice cùng cần mọi event, để cùng `group.id` cho tiện" → mỗi service chỉ thấy 1 nửa → **group id riêng mỗi service**.
- Thấy "payload 5 MB qua Kafka" → tăng `message.max.bytes` là cách tệ → **claim-check** (S3 + pointer).

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
|---|---|
| "no broker management, pay per throughput, IAM only" | **MSK Serverless** |
| "3× throughput, 20× faster scaling, AWS-managed storage, still Provisioned" | **Express brokers** |
| "need mTLS / Kafka ACLs / custom `server.properties`" | **Provisioned Standard** (hoặc Express nếu không cần sửa config nhiều) |
| "port 9098" / "9198" | IAM access control (private / public) |
| "port 9096" / "9094" / "9092" | SCRAM / TLS (mTLS) / plaintext |
| "`sasl.mechanism=AWS_MSK_IAM`, `IAMLoginModule`" | IAM auth Java, jar `aws-msk-iam-auth` |
| "Node/Python client with IAM" | `OAUTHBEARER` + signer lib (`aws-msk-iam-sasl-signer-js`) |
| "secret name `AmazonMSK_`" | SASL/SCRAM + `Secrets Manager` + KMS customer key |
| "`ReadData` denied / `GroupAuthorizationException`" | thiếu `AlterGroup` + `DescribeGroup` (ARN group) |
| "`WriteDataIdempotently`" | cluster ARN, cần cho idempotent producer |
| "Kafka ACLs have no effect" | cluster dùng IAM access control |
| "topic not auto-created on MSK" | `auto.create.topics.enable=false` mặc định |
| "managed Kafka Connect, plugin from S3, MCU" | **MSK Connect** (1 vCPU/4 GiB, autoscaled) |
| "connector can't write to S3" | **service execution role** |
| "managed MirrorMaker 2 / cross-region / offset sync" | **MSK Replicator** |
| "clients keep topic names after failover" | Replicator **Identical topic name** |
| "infinite retention on Standard brokers" | **tiered storage** |
| "per-partition consumer lag in CloudWatch" | `PER_TOPIC_PER_PARTITION` |
| "`ActiveControllerCount` ≠ 1 / `OfflinePartitionsCount` > 0" | alarm ngay, cluster không khoẻ |
| "Prometheus scrape MSK" | Open Monitoring **11001/11002** |
| "Lambda + Kafka" | **ESM, Lambda poll**, batch 100/10.000, base64, `AWSLambdaMSKExecutionRole` |
| "Lambda only for `status=FAILED` events" | **`FilterCriteria`** |
| "Confluent Cloud / on-prem Kafka → Lambda" | self-managed ESM + `SourceAccessConfigurations` |
| "route Kafka → SQS/Step Functions, no code" | **`EventBridge Pipes`** |
| "free serverless schema registry for MSK" | **Glue Schema Registry** (18-byte header, không tương thích Confluent) |
| "simple AWS-native stream, retention ≤ 365 days" | **`Kinesis Data Streams`** |
| "Kafka API compatibility, Connect/Streams ecosystem" | **MSK** |
| "atomically update DB and publish event" | **Outbox + CDC** |
| "duplicate after retry/replay" | **idempotent consumer** (eventId / offset / upsert) |
| "retry without blocking, ordering not required" | **non-blocking retry topics** + header `attempts` |
| "retry but keep per-key ordering" | **blocking retry** `pause()`/`resume()` |
| "deserialization failure" | **poison pill → DLQ**, không retry |
| "events for the same order must be ordered" | **same topic + key = orderId** (multi-event topic, `RecordNameStrategy`) |
| "one tenant dominates traffic" | **hot key → salt** / partition riêng |
| "reduce number of partitions" | **không thể** → topic mới |
| "exactly-once into PostgreSQL" | **idempotent sink / offset in DB**, không phải Kafka txn |
| "message > 1 MB" | **claim-check** (S3 + pointer) |
| "several services need all events" | **consumer group per service** |
| "latest value per key / cache" | **compacted topic** + tombstone |
| "consumer overwhelmed" | **`pause()`/`resume()`**, `max.poll.records`, scale ≤ partition |
| "reply to request over Kafka" | header **`correlationId`** + **`replyTo`** |

## 🧪 Lab checklist

- [ ] Lab 9.1 ⭐ — Tạo MSK Serverless, IAM policy topic `orders` + group, list/create topic bằng `kafka-topics.sh --command-config client-iam.properties` và Node `kafkajs` + signer; **đã `delete-cluster`**.
- [ ] Lab 9.2 ⭐ — Tạo ESM `--topics orders --starting-position LATEST --batch-size 100 --filter-criteria`; handler decode base64; `sam local invoke` với event mẫu MSK chạy đúng; **đã xoá ESM + function**.
- [ ] Lab 9.3 ⭐ — Postgres + Debezium Connect, connector `EventRouter`; insert order + outbox trong 1 transaction → thấy event ở topic `outbox.event.Order` (mặc định của `EventRouter`; đổi `route.topic.replacement` nếu muốn tên khác), key = `aggregateid`, header `eventType`.
- [ ] Lab 9.4 — Idempotent consumer: reset offset `--to-earliest`, chạy lại → 0 record xử lý trùng (cả 2 chiến lược dedup).
- [ ] Lab 9.5 — Retry topics: record lỗi tạm đi `orders-retry` 3 lần (header `attempts` 1→3) rồi vào `orders-dlq`; poison pill vào DLQ ngay; delay bằng `pause()`.
- [ ] Lab 9.6 — Điền bảng perf-test 1/3/12 partition × 1/3 consumer; xác nhận `--alter --partitions 1` bị từ chối.
- [ ] Lab 9.7 (Option) — Pipe MSK → SQS nhận message; **đã xoá pipe + queue + cluster**.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Khi nào chọn Serverless, khi nào Express, khi nào Standard?**
  **Đáp án gọn:** Serverless = tải biến động, không quản gì, chấp nhận chỉ IAM + không sửa broker config; Express = throughput cao, ghét EBS, scale/recover nhanh, vẫn cần SCRAM/mTLS; Standard = control tối đa (instance, EBS, tiered, `t3` dev, mọi config).
- **IAM access control khác SCRAM + ACL ở đâu? Consumer cần action nào?**
  **Đáp án gọn:** IAM làm cả auth + authz bằng policy gắn identity, ACL vô hiệu; SCRAM chỉ auth, authz bằng ACL trên broker. Consumer: `Connect` + `DescribeTopic` + `ReadData` (topic ARN) + `DescribeGroup` + `AlterGroup` (group ARN); port 9098.
- **Lambda đọc MSK theo cơ chế gì, tham số nào quyết định batch, lỗi xử lý thế nào?**
  **Đáp án gọn:** ESM, Lambda poll như consumer group, invoke đồng bộ; `BatchSize` (100/10.000) + `MaximumBatchingWindowInSeconds` (≤ 300 s); lỗi → retry cả batch (idempotent!), `ReportBatchItemFailures`/bisect, on-failure destination SQS/SNS/S3; payload base64.
- **MSK vs Kinesis — 3 tiêu chí quyết định?**
  **Đáp án gọn:** (1) cần Kafka API/ecosystem (Connect, Streams, SR, Debezium) → MSK; (2) retention > 365 ngày / compaction / EOS → MSK; (3) pipeline AWS-native đơn giản, team nhỏ, ít vận hành → Kinesis.
- **Vì sao dual-write sai và Outbox sửa thế nào?**
  **Đáp án gọn:** DB commit và `send()` không atomic → mất event hoặc event ma; Outbox ghi event vào bảng cùng transaction, Debezium CDC đọc WAL publish lên topic (EventRouter: `aggregatetype` → topic, `aggregateid` → key); at-least-once nên consumer dedup theo `id`.
- **Idempotent consumer làm được bằng cách nào (2 chiến lược)?**
  **Đáp án gọn:** (a) dedup theo `eventId` do producer sinh — lưu store (DynamoDB conditional write / bảng PK) cùng transaction với kết quả; (b) lưu `(topic,partition,offset)` đã xử lý trong DB đích, `seek()` khi start; hoặc thiết kế nghiệp vụ upsert.
- **Non-blocking retry đổi lấy gì? Poison pill xử lý sao?**
  **Đáp án gọn:** Không chặn partition nhưng mất ordering giữa record retry và record sau; poison pill (không deserialize/validation vĩnh viễn) → DLQ ngay, không retry.
- **⭐ CHECKPOINT — FULL MOCK #1 đạt ≥ 75% chưa? Domain nào thấp nhất?**
  **Đáp án gọn:** Ghi con số thật vào bảng Buổi D. ≥ 75% → Tuần 10; 70–74% → Tuần 10 nhưng ưu tiên domain yếu; < 70% → lùi lịch thi 1 tuần, ôn lại cụm yếu rồi mock lại.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được (9 file: MSK cluster types, IAM, Connect, Replicator, config & monitoring, Lambda ESM, Glue SR, Outbox/Debezium, error handling).

- AWS Docs — `Amazon MSK` Developer Guide: [What is MSK](https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html) · [Express brokers](https://docs.aws.amazon.com/msk/latest/developerguide/msk-broker-types-express.html) · [MSK Serverless](https://docs.aws.amazon.com/msk/latest/developerguide/serverless.html) · [Port information](https://docs.aws.amazon.com/msk/latest/developerguide/port-info.html) · [IAM access control](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html) · [Kafka actions](https://docs.aws.amazon.com/msk/latest/developerguide/kafka-actions.html) · [SASL/SCRAM](https://docs.aws.amazon.com/msk/latest/developerguide/msk-password.html) · [mTLS](https://docs.aws.amazon.com/msk/latest/developerguide/msk-authentication.html) · [Custom configuration](https://docs.aws.amazon.com/msk/latest/developerguide/msk-configuration-properties.html) · [Monitoring levels](https://docs.aws.amazon.com/msk/latest/developerguide/metrics-details.html) · [Open Monitoring](https://docs.aws.amazon.com/msk/latest/developerguide/open-monitoring.html) · [MSK Connect](https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html) · [MSK Replicator](https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator.html) · [Tiered storage](https://docs.aws.amazon.com/msk/latest/developerguide/msk-tiered-storage.html) · [Quotas](https://docs.aws.amazon.com/msk/latest/developerguide/limits.html) · [Best practices](https://docs.aws.amazon.com/msk/latest/developerguide/bestpractices.html).
- AWS Docs — `Lambda`: [Using Lambda with Amazon MSK](https://docs.aws.amazon.com/lambda/latest/dg/with-msk.html) · [ESM parameters](https://docs.aws.amazon.com/lambda/latest/dg/msk-esm-parameters.html) · [Self-managed Kafka](https://docs.aws.amazon.com/lambda/latest/dg/with-kafka.html) · [Event filtering](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventfiltering.html). `EventBridge Pipes`: [MSK source](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-msk.html). `Glue Schema Registry`: [docs](https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html).
- GitHub: [aws/aws-msk-iam-auth](https://github.com/aws/aws-msk-iam-auth) · [aws/aws-msk-iam-sasl-signer-js](https://github.com/aws/aws-msk-iam-sasl-signer-js) · [Debezium Outbox Event Router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html).
- Patterns: [microservices.io — Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html) · [Idempotent Consumer](https://microservices.io/patterns/communication-style/idempotent-consumer.html) · [Saga](https://microservices.io/patterns/data/saga.html) · Confluent blog [Error Handling Patterns in Kafka](https://www.confluent.io/blog/error-handling-patterns-in-kafka/) · [Confluent Developer — Event Streaming Patterns](https://developer.confluent.io/patterns/) · [How to choose the number of partitions](https://www.confluent.io/blog/how-choose-number-topics-partitions-kafka-cluster/).
- Khoá học: Confluent Developer — *Event Sourcing and Event Storage with Apache Kafka*, *Designing Events and Event Streams*; Stephane Maarek — *Apache Kafka Series* mục Kafka on AWS (MSK) + *AWS Certified Developer* mục Lambda ESM/MSK; sách *Kafka: The Definitive Guide* 2nd ed. Ch.8–10; *Designing Event-Driven Systems* (Ben Stopford, free PDF từ Confluent).

## ✅ Checklist hoàn thành Tuần 9

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (ports, quota Serverless, required actions, số Lambda ESM, MCU, Replicator)
- [ ] Tự viết lại 4 bảng bằng trí nhớ: 3 loại cluster · 3 auth · MSK vs Kinesis · pattern → vấn đề
- [ ] Hoàn thành Lab 9.3–9.6 (local) + ít nhất Lab 9.1 hoặc 9.2 trên AWS (đã xoá tài nguyên)
- [ ] Làm xong 28 câu questions.md, xem lại 100% câu sai
- [ ] **🎯 FULL MOCK #1 (60 câu / 90 phút) ≥ 75%**, đã ghi điểm theo domain và sổ câu sai — CHECKPOINT
- [ ] Vượt Cổng tự kiểm tra
