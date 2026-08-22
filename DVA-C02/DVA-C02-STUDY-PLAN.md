# 🎯 Kế hoạch luyện thi AWS Certified Developer – Associate (DVA-C02)

> Tài liệu này là **lộ trình học + checklist toàn diện** cho kỳ thi `DVA-C02`.
> Bạn đã đậu `SAA-C03` → phần lớn nền tảng hạ tầng (VPC, EC2, S3, IAM cơ bản) đã có sẵn.
> DVA-C02 **KHÔNG** hỏi "chọn kiến trúc nào tốt nhất" mà hỏi **"code/config/CLI/SDK phải viết như thế nào"**.
> Tư duy chuyển đổi: từ **Architect (thiết kế)** → **Developer (triển khai, gỡ lỗi, tối ưu, tự động hoá)**.
>
> **📅 Kế hoạch đã chốt:** **10 tuần × ~10–12h/tuần (~110 giờ)**. Mục tiêu: **đậu chắc chắn** — mỗi tuần có *cổng tự kiểm tra*, và một *cơ chế đảm bảo đậu* dựa trên ngưỡng điểm mock (xem [§3](#3-lộ-trình-học-theo-tuần)).

---

## 📑 Mục lục

1. [Tổng quan kỳ thi](#1-tổng-quan-kỳ-thi)
2. [Khác biệt DVA-C02 vs SAA-C03 — tận dụng cái đã biết](#2-khác-biệt-dva-c02-vs-saa-c03)
3. [Lộ trình học chi tiết 10 tuần (~10–12h/tuần) + Cơ chế đảm bảo đậu](#3-lộ-trình-học-theo-tuần)
4. [Kiến thức theo Domain (task statements chính thức)](#4-kiến-thức-theo-domain)
5. [Deep-dive từng dịch vụ trọng tâm](#5-deep-dive-từng-dịch-vụ-trọng-tâm)
6. [Những con số PHẢI thuộc lòng](#6-những-con-số-phải-thuộc-lòng)
7. [Bảng phản xạ: Keyword → Dịch vụ/Đáp án](#7-bảng-phản-xạ-keyword--dịch-vụ)
8. [Thực hành hands-on (labs bắt buộc)](#8-thực-hành-hands-on)
9. [Tài nguyên học tập](#9-tài-nguyên-học-tập)
10. [Chiến lược làm bài thi](#10-chiến-lược-làm-bài-thi)
11. [✅ CHECKLIST TOÀN DIỆN](#11-checklist-toàn-diện)

---

## 1. Tổng quan kỳ thi

| Hạng mục | Chi tiết |
|---|---|
| **Mã thi** | DVA-C02 (phiên bản hiện hành, thay thế DVA-C01) |
| **Số câu hỏi** | ~65 câu (khoảng 50 câu tính điểm + 15 câu "unscored" thử nghiệm) |
| **Thời gian** | 130 phút (~2 phút/câu) |
| **Loại câu** | Multiple choice (1 đáp án) + Multiple response (chọn 2+ trong 5+) |
| **Điểm đậu** | 720 / 1000 (scaled score) |
| **Chi phí** | 150 USD |
| **Hình thức** | Pearson VUE — tại trung tâm hoặc online proctored |
| **Ngôn ngữ** | Có tiếng Anh, Nhật, Hàn, Trung giản thể (không có tiếng Việt) |
| **Hiệu lực** | 3 năm |
| **Yêu cầu tiên quyết** | Không bắt buộc; khuyến nghị 1+ năm kinh nghiệm dev với AWS |

### Tỉ trọng 4 Domain (RẤT quan trọng để phân bổ thời gian học)

| Domain | Tên | Tỉ trọng | Ưu tiên |
|---|---|---|---|
| **1** | Development with AWS Services | **32%** | ⭐⭐⭐ Cao nhất |
| **2** | Security | **26%** | ⭐⭐⭐ Cao |
| **3** | Deployment | **24%** | ⭐⭐ Trung-cao |
| **4** | Troubleshooting and Optimization | **18%** | ⭐⭐ Trung bình |

> 💡 **Domain 1 + 2 = 58%**. Ba dịch vụ chiếm phần lớn câu hỏi: **`Lambda`, `DynamoDB`, `API Gateway`**. Nắm vững bộ ba này + `IAM/STS`, `Cognito`, `KMS`, `CI/CD` là đã qua được ngưỡng đậu.

---

## 2. Khác biệt DVA-C02 vs SAA-C03

### ✅ Cái bạn ĐÃ CÓ (chỉ cần ôn nhẹ)
- Nền tảng `IAM` (policy, role), `VPC`, `EC2`, `S3` cơ bản, `RDS`, `ELB`, `Route 53`, `CloudFront`.
- Khái niệm `Multi-AZ`, `Region`, tính sẵn sàng cao, encryption at rest/in transit.
- Kiến thức `KMS`, `SQS`, `SNS`, `CloudWatch` ở mức khái niệm.

### 🔥 Cái MỚI / SÂU HƠN nhiều so với SAA (đầu tư nhiều nhất)
- **Viết code thực sự**: dùng **AWS SDK** (boto3 / SDK for JavaScript / Java...), **AWS CLI**, xử lý **retry/exponential backoff/jitter**, **pagination**, **credential provider chain**.
- **`Lambda` chuyên sâu**: versions, aliases, layers, environment variables, concurrency (reserved/provisioned), cold start, `/tmp`, DLQ, destinations, event source mapping.
- **`DynamoDB` chuyên sâu**: WCU/RCU tính toán, GSI/LSI, DynamoDB Streams, DAX, conditional writes, optimistic locking, TransactWriteItems, PartiQL.
- **`API Gateway` chuyên sâu**: REST vs HTTP vs WebSocket, stages, stage variables, authorizers, usage plans, mapping templates, caching, CORS.
- **CI/CD**: `CodeCommit` *(AWS từng ngừng nhận khách mới 2024, mở lại GA 11/2025; đề vẫn có thể hỏi)*, `CodeBuild` (**buildspec.yml**), `CodeDeploy` (**appspec.yml**, hooks), `CodePipeline`, `CodeArtifact`.
- **IaC dev**: `CloudFormation` (intrinsic functions, change sets) + **`SAM`** (`sam build/deploy/local`).
- **`Cognito`** (User Pools vs Identity Pools), **`STS`** (AssumeRole...), **`Secrets Manager` vs `Parameter Store`**.
- **Observability**: `X-Ray` (segments/subsegments/annotations), `CloudWatch Logs/Metrics/Alarms`, `EventBridge`.
- **Containers cho dev**: `ECS`/`Fargate`, `ECR`.
- **`Elastic Beanstalk`** (deployment policies), **`Step Functions`**, **`ElastiCache`** (caching strategies), **`Kinesis`**.
- **Khác (in-scope)**: `CloudFront` (signed URL/cookies, OAC), `AppSync` (GraphQL), `AppConfig` (feature flags), `WAF`.

> 🧠 **Câu thần chú chuyển tư duy:** SAA hỏi *"nên dùng gì?"* — DVA hỏi *"dùng như thế nào, đặt config ở đâu, gọi API nào, sửa lỗi ra sao."*

---

## 3. Lộ trình học theo tuần

> **Kế hoạch: 10 tuần × ~10–12h/tuần (~110 giờ).** Học phủ hết kiến thức trong **Tuần 1–8**, dành **Tuần 9–10 để mock + review** — đây chính là "vùng đệm" giúp bạn **đậu chắc**. Học phủ theo tỉ trọng đề: Domain 1 (Tuần 1–5) → Domain 2 (Tuần 6–7) → Domain 3 (Tuần 8) → Domain 4 (Tuần 9) → chốt (Tuần 10).

### ⏱️ Nhịp học mỗi tuần (~11h — chia 4 buổi)

| Buổi | Thời lượng | Nội dung |
|---|---|---|
| **A — Lý thuyết** | ~3h | Xem video + đọc AWS docs chủ đề của tuần, ghi note |
| **B — Hands-on** | ~3.5h | Tự tay làm lab (Console + CLI + SDK/SAM) |
| **C — Bổ sung** | ~2.5h | Lý thuyết/hands-on phần còn lại + đọc FAQ dịch vụ |
| **D — Practice + Review** | ~2h | 25–35 câu practice đúng chủ đề → **ghi câu sai** + ôn lại (spaced repetition) |

> 📌 **Tỉ lệ vàng: Lý thuyết 35% – Hands-on 45% – Practice 20%.** DVA thắng bằng tay làm, không phải học vẹt.

---

### 🗓️ Chi tiết 10 tuần — mỗi tuần 1 thư mục riêng

> 👉 Mỗi tuần là **1 thư mục** trong [`study-plan/`](study-plan/) gồm: `README.md` (plan chi tiết: mục tiêu, nội dung từng buổi, lab từng bước, điểm phải nhớ, bẫy đề, cổng tự kiểm tra, checklist) và thư mục **`resources/`** (tài liệu AWS đã crawl sẵn để đọc offline). Bấm vào tên tuần để mở.

| Tuần | Trọng tâm | Domain | Mốc quan trọng | File |
|---|---|---|---|---|
| **1** | Developer mindset + AWS SDK/CLI + `Lambda` (cơ bản) | D1 | — | [week-01/](study-plan/week-01/README.md) |
| **2** | `Lambda` nâng cao (versions/aliases/layers/concurrency) | D1 | — | [week-02/](study-plan/week-02/README.md) |
| **3** | `DynamoDB` toàn tập | D1 | — | [week-03/](study-plan/week-03/README.md) |
| **4** | `API Gateway` + `S3` (góc dev) | D1 | — | [week-04/](study-plan/week-04/README.md) |
| **5** | Messaging + `Step Functions` + `ElastiCache` + `RDS Proxy` | D1 ✅ | 🎯 mini-mock D1 ≥70% | [week-05/](study-plan/week-05/README.md) |
| **6** | Security I: `IAM` + `STS` + `Cognito` | D2 | — | [week-06/](study-plan/week-06/README.md) |
| **7** | Security II: `KMS` + `Secrets`/`Parameter Store` + Encryption | D2 ✅ | 🎯 mini-mock D1+2 ≥72% | [week-07/](study-plan/week-07/README.md) |
| **8** | Deployment: CI/CD + `CloudFormation`/`SAM` + `Beanstalk` + `ECS`/`ECR` | D3 ✅ | 🎯 mini-mock D3 ≥70% | [week-08/](study-plan/week-08/README.md) |
| **9** | Troubleshooting & Optimization (`CloudWatch`/`X-Ray`) | D4 ✅ | 🎯 **FULL MOCK #1** | [week-09/](study-plan/week-09/README.md) |
| **10** | Tuần chốt: Mock dồn + Review + Cram + Thi | Tất cả | 🏁 **Full mock #2–4 → Thi** | [week-10/](study-plan/week-10/README.md) |

> 📈 Tiến trình phủ Domain: **D1** (Tuần 1–5, 32%) → **D2** (Tuần 6–7, 26%) → **D3** (Tuần 8, 24%) → **D4** (Tuần 9, 18%) → **chốt** (Tuần 10).

---

### ✅ Cơ chế ĐẢM BẢO ĐẬU (bắt buộc tuân thủ)

1. **Cổng tự kiểm tra:** Không sang tuần mới nếu **chưa trả lời trôi chảy** các câu hỏi ở cổng tuần hiện tại. Chưa qua → dành buổi D tuần sau ôn lại phần yếu.
2. **Sổ câu sai + Spaced repetition:** Mọi câu practice/mock sai → ghi lại (đề, đáp án đúng, **lý do mình sai**). Ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Dùng đúng workflow file phân tích như SAA-C03.
3. **Ngưỡng checkpoint:** Mini-mock cuối mỗi domain **phải đạt ngưỡng** (D1 ≥70%, D1+2 ≥72%, D3 ≥70%) mới đi tiếp. Không đạt → lùi lịch, cày lại domain đó.
4. **Ngưỡng đăng ký thi thật — CHỈ đặt lịch khi ĐỦ CẢ 4:**
   - ✅ **≥ 3 full mock KHÁC NHAU đạt ≥ 85%** (ổn định, không phải may mắn).
   - ✅ Đã **review hết 100% câu sai** và hiểu vì sao sai.
   - ✅ Đọc trôi chảy toàn bộ **bảng số §6** và **bảng phản xạ §7**.
   - ✅ Hoàn thành **toàn bộ hands-on nhóm Serverless & CI/CD** ở [§8](#8-thực-hành-hands-on).
5. **Van an toàn:** Nếu một full mock **< 75%** → **lùi lịch thi 1 tuần**, tập trung 100% vào vùng yếu (domain điểm thấp nhất) trước khi mock lại.

> 🎯 Vì sao cách này đảm bảo đậu: điểm đậu là **72% (720/1000)**. Đặt ngưỡng cá nhân **≥85% ổn định trên nhiều bộ đề khác nhau** tạo **biên an toàn ~13%** — đủ để hấp thụ độ khó dao động và áp lực phòng thi.

---

## 4. Kiến thức theo Domain

> Dưới đây là **task statements chính thức** trong AWS Exam Guide, kèm những gì cần **học / nhớ / phản xạ** cho từng mục.

### 🟦 Domain 1 — Development with AWS Services (32%)

**Task 1.1 — Develop code for applications hosted on AWS**
- Kiến trúc idempotent, stateless, xử lý lỗi & retry (**exponential backoff + jitter**).
- Giao tiếp đồng bộ/bất đồng bộ (SQS, SNS, Kinesis, EventBridge).
- Fan-out/fan-in, orchestration bằng `Step Functions`.
- Dùng **AWS SDK**: cấu hình client, region, credential provider chain, pagination, waiters.

**Task 1.2 — Develop code for AWS Lambda**
- Cấu trúc handler, event/context object, runtimes.
- Environment variables (mã hoá bằng KMS), layers, `/tmp`.
- Concurrency: reserved vs provisioned; cold start; event source mapping (SQS/Kinesis/DynamoDB Streams).
- Invocation types: sync (RequestResponse) vs async (Event) + DLQ + destinations.
- Versions & aliases; đóng gói/deploy (zip vs container image).

**Task 1.3 — Use data stores in application development**
- `DynamoDB`: partition/sort key, query vs scan, GSI/LSI, streams, conditional writes, TTL, capacity modes.
- `RDS`/`Aurora`: quản lý connection (pooling), `RDS Proxy`.
- `S3`: CRUD, presigned URL, multipart upload, event notifications.
- Caching: `ElastiCache` (lazy loading, write-through), `DAX`.
- CRUD lifecycle, data consistency (eventual vs strong).

---

### 🟩 Domain 2 — Security (26%)

**Task 2.1 — Implement authentication and/or authorization**
- `IAM`: identity-based vs resource-based policy, cấu trúc policy (Effect/Action/Resource/Condition/Principal), **explicit deny > allow**.
- `STS`: `AssumeRole`, `AssumeRoleWithWebIdentity`, `AssumeRoleWithSAML`, `GetSessionToken`; cross-account access; instance profile.
- `Cognito`: **User Pools** (authentication, JWT: ID/Access/Refresh token) vs **Identity Pools** (authorization → temporary AWS credentials).
- Federation: SAML, OIDC, social login; Hosted UI; MFA.
- API Gateway authorizers (IAM / Cognito / Lambda authorizer).

**Task 2.2 — Implement encryption using AWS services**
- `KMS`: symmetric vs asymmetric, **envelope encryption**, `GenerateDataKey`, giới hạn encrypt trực tiếp **4 KB**.
- Key policies, grants, aliases, automatic rotation.
- Encryption at rest (S3 SSE-S3/SSE-KMS/SSE-C, EBS, DynamoDB, RDS) & in transit (TLS/ACM).
- Client-side vs server-side encryption.

**Task 2.3 — Manage sensitive data in application code**
- `Secrets Manager` (rotation tự động, tích hợp RDS) vs `SSM Parameter Store` (String/SecureString, hierarchical, miễn phí tier standard).
- Không hard-code credentials → dùng IAM roles, env vars mã hoá.
- Xử lý PII, sanitize logs.

---

### 🟨 Domain 3 — Deployment (24%)

**Task 3.1 — Prepare application artifacts to be deployed to AWS**
- Đóng gói Lambda (zip/layer/container), `SAM` package, `ECR` image.
- Quản lý dependencies, environment config, artifacts (S3/`CodeArtifact`).

**Task 3.2 — Test applications in development environments**
- `sam local invoke` / `sam local start-api`, mock event.
- Test qua stages/environments; feature flags.

**Task 3.3 — Automate deployment testing**
- Tích hợp test vào pipeline (`CodeBuild` phases), unit/integration test tự động.

**Task 3.4 — Deploy code by using AWS CI/CD services**
- `CodeCommit` → `CodeBuild` (**buildspec.yml**) → `CodeDeploy` (**appspec.yml**) → `CodePipeline` (orchestration).
- Chiến lược deploy: **In-place, Blue/Green** (EC2/ECS), **Canary/Linear/AllAtOnce** (Lambda), Rolling.
- `CloudFormation`/`SAM` deploy; `Elastic Beanstalk` deployment policies (All at once, Rolling, Rolling with additional batch, Immutable, Blue/Green swap).
- Lifecycle hooks (CodeDeploy), rollback, traffic shifting.

---

### 🟥 Domain 4 — Troubleshooting and Optimization (18%)

**Task 4.1 — Assist in a root cause analysis**
- Đọc `CloudWatch Logs`, metric filters, alarms; `CloudTrail` để audit API calls.
- Diễn giải mã lỗi (4xx/5xx, throttling `ProvisionedThroughputExceededException`, `ThrottlingException`).

**Task 4.2 — Instrument code for observability**
- `X-Ray`: segments/subsegments, **annotations (index, filter được) vs metadata (không index)**, sampling, service map, daemon, active tracing cho Lambda.
- Custom CloudWatch metrics, structured logging, `EMF` (Embedded Metric Format).

**Task 4.3 — Optimize applications by using AWS services and features**
- Caching: `ElastiCache`, `DAX`, API Gateway cache, CloudFront.
- Tối ưu Lambda (memory→CPU, provisioned concurrency), DynamoDB (avoid hot partition, on-demand).
- Tối ưu chi phí & hiệu năng; RDS read replica; SQS batching.

---

## 5. Deep-dive từng dịch vụ trọng tâm

> Sắp xếp theo mức độ xuất hiện trong đề. Với mỗi dịch vụ: **cần nhớ gì** + **bẫy đề hay gặp**.

### ⭐ `AWS Lambda` (dịch vụ #1 của đề)
- **Handler / event / context**; runtimes; giới hạn (xem [§6](#6-những-con-số-phải-thuộc-lòng)).
- **Versions**: bất biến, có ARN riêng; **`$LATEST`** là bản mutable.
- **Aliases**: con trỏ tới version, hỗ trợ **weighted routing** (canary). Alias KHÔNG trỏ tới alias khác.
- **Layers**: tối đa **5 layers**, tổng unzip ≤ 250 MB; tách dependencies/dùng chung.
- **Environment variables**: ≤ **4 KB**, mã hoá bằng KMS.
- **Concurrency**: reserved (giới hạn + đảm bảo) vs provisioned (giữ ấm, chống cold start). Vượt hạn → **`TooManyRequestsException` (429)**.
- **SnapStart**: giảm cold start (best-effort) cho `Java 11+`, `Python 3.12+`, `.NET 8+`; chỉ trên **published version/alias** (không `$LATEST`); **không dùng chung provisioned concurrency**; không hỗ trợ `/tmp` > 512 MB.
- **Invocation**: sync (6 MB payload) vs async (1 MB, retry **2 lần**, DLQ/destinations) vs event source mapping (poll SQS/Kinesis/DynamoDB Streams).
- **`/tmp`**: 512 MB → tối đa 10 GB.
- **Bẫy:** async retry 2 lần; cần persistent state → KHÔNG dùng `/tmp` (không bền) → dùng S3/DynamoDB/EFS. VPC-attached Lambda cần NAT để ra internet.

### ⭐ `Amazon DynamoDB` (dịch vụ #2)
- **Item ≤ 400 KB**. Partition key (hash) + optional sort key (range).
- **RCU**: 1 RCU = 1 strongly-consistent read/s cho item ≤ **4 KB** (hoặc 2 eventually-consistent reads/s).
- **WCU**: 1 WCU = 1 write/s cho item ≤ **1 KB**.
- **GSI**: khác partition/sort key, throughput riêng, **chỉ eventually consistent**, tạo bất kỳ lúc nào.
- **LSI**: cùng partition key, khác sort key, dùng chung throughput, hỗ trợ strong consistency, **phải tạo lúc tạo bảng**.
- **Streams**: giữ **24h**, trigger Lambda; view types (KEYS_ONLY, NEW_IMAGE, OLD_IMAGE, NEW_AND_OLD_IMAGES).
- **DAX**: cache microsecond, in-VPC; **Query vs Scan** (ưu tiên Query).
- **Conditional writes, atomic counters, optimistic locking** (version number), **TransactWriteItems**, BatchGet/BatchWrite, PartiQL, TTL.
- **Capacity**: provisioned (+ auto scaling) vs on-demand.
- **Bẫy:** hot partition → phân phối key đều; throttling → exponential backoff; Scan tốn kém → dùng Query/GSI.

### ⭐ `Amazon API Gateway` (dịch vụ #3)
- **REST API** (đầy đủ tính năng) vs **HTTP API** (rẻ, nhanh, ít tính năng) vs **WebSocket API** (2 chiều).
- **Stages** (dev/prod) + **stage variables** (như biến môi trường, trỏ Lambda alias).
- **Integration**: Lambda proxy (`AWS_PROXY`) vs Lambda vs HTTP vs AWS service vs Mock.
- **Authorizers**: IAM, Cognito User Pool, **Lambda authorizer** (token/request).
- **Usage plans + API keys**, throttling, **caching** (TTL mặc định 300s), CORS, mapping templates (VTL), gateway responses.
- **Integration timeout**: mặc định **29s**; có thể **tăng tới 300s** qua `Service Quotas` cho **Regional/private REST API** (KHÔNG áp dụng edge-optimized REST & HTTP API; có thể phải giảm throttle quota). Tác vụ dài → vẫn nên async.
- **Bẫy:** CORS lỗi → cấu hình cả OPTIONS + header ở method response; canary release qua stage; proxy integration truyền nguyên request.

### `Amazon S3` (góc nhìn developer)
- CRUD, **presigned URL** (upload/download tạm thời, giới hạn thời gian).
- **Multipart upload** (khuyến nghị > 100 MB, bắt buộc > 5 GB); object tối đa **5 TB**; single PUT ≤ 5 GB.
- Encryption: **SSE-S3, SSE-KMS, SSE-C**, client-side.
- Versioning, lifecycle, storage classes, **event notifications** → Lambda/SQS/SNS.
- **Strong read-after-write consistency** (mặc định hiện nay).
- **Bẫy:** presigned URL kế thừa quyền của identity tạo ra nó; byte-range fetch để tải song song.

### `CloudFront` (góc nhìn developer)
- **Signed URL** (1 file) vs **Signed cookies** (nhiều file, giữ nguyên URL) — dùng trusted key group; so với **`S3` presigned URL** (truy cập S3 trực tiếp, kế thừa quyền IAM người tạo).
- **OAC** (thay OAI) khoá S3 chỉ cho CloudFront đọc.
- **Cache invalidation** (`CreateInvalidation`) hoặc versioned object để cập nhật nội dung.

### `SQS` / `SNS` / `Kinesis` (messaging — hay bị so sánh)
- **`SQS`**: Standard (at-least-once, thứ tự best-effort) vs **FIFO** (exactly-once, có thứ tự, `MessageGroupId`/`MessageDeduplicationId`). Message ≤ **256 KB** (lớn hơn → SQS Extended Client + S3). Visibility timeout mặc định **30s** (max 12h). Retention **4 ngày** (1 phút–14 ngày). **Long polling** (`WaitTimeSeconds` ≤ 20s). DLQ + `maxReceiveCount`.
- **`SNS`**: pub/sub, **fan-out** ra SQS/Lambda/HTTP/email/SMS; FIFO topics; message filtering.
- **`Kinesis Data Streams`**: shards (1 MB/s hoặc 1000 rec/s in, 2 MB/s out mỗi shard), retention 24h→365 ngày, ordered theo partition key, cho phép **nhiều consumer + replay**. **Capacity mode**: `on-demand` (AWS tự quản shard, không cần capacity planning) vs `provisioned` (tự đặt số shard). `Firehose` = near-real-time load vào S3/Redshift/OpenSearch (không replay).
- **Bẫy khi chọn:** cần thứ tự + nhiều consumer + replay → Kinesis; decouple đơn giản 1 consumer group → SQS; fan-out 1→N → SNS (hoặc SNS+SQS).

### `Cognito` (security)
- **User Pools** = *authentication* ("bạn là ai?") → trả **JWT** (ID/Access/Refresh). Sign-up/sign-in, MFA, social/SAML/OIDC, Hosted UI. *Hosted UI = classic; **Managed Login** (2024) = thế hệ mới (branding editor, passkey), cần feature plan **Essentials/Plus**.*
- **Identity Pools (Federated Identities)** = *authorization* ("bạn được làm gì?") → đổi token lấy **temporary AWS credentials** qua STS, map vào IAM role.
- **Bẫy:** cần gọi trực tiếp AWS service từ client (mobile) → Identity Pool. Chỉ cần đăng nhập app → User Pool.

### `KMS` (encryption)
- **Envelope encryption**: `GenerateDataKey` → mã hoá data local bằng data key, lưu data key đã mã hoá.
- Encrypt trực tiếp qua API ≤ **4 KB**.
- Symmetric (mặc định) vs asymmetric; key policy + grants; **automatic rotation** (mỗi năm với CMK); hỗ trợ **custom rotation period** và **on-demand rotation** (rotate ngay).
- Loại key: **AWS owned / AWS managed / customer managed (CMK)**.

### `IAM` + `STS`
- Cấu trúc policy JSON; **evaluation: explicit Deny > Allow > default Deny**.
- Roles cho service (Lambda execution role, EC2 instance profile, ECS task role vs execution role).
- STS APIs: `AssumeRole` (cross-account), `AssumeRoleWithWebIdentity` (federation web/OIDC), `AssumeRoleWithSAML` (federation SAML), `GetSessionToken` (MFA).

### CI/CD: `CodeCommit` / `CodeBuild` / `CodeDeploy` / `CodePipeline`
- **`buildspec.yml`** (CodeBuild): phases `install → pre_build → build → post_build`; sections `env`, `artifacts`, `cache`, `reports`. Đặt ở **root** của repo.
- **`appspec.yml`** (CodeDeploy):
  - EC2/on-prem: hooks theo thứ tự `ApplicationStop → BeforeInstall → AfterInstall → ApplicationStart → ValidateService`.
  - Lambda/ECS: dùng `AppSpec` (hooks như `BeforeAllowTraffic`, `AfterAllowTraffic`).
- **CodeDeploy deployment config**: EC2 = `AllAtOnce`/`HalfAtATime`/`OneAtATime`; Lambda/ECS = `Canary`, `Linear`, `AllAtOnce`.
- **`CodePipeline`**: stages (Source → Build → Deploy...), artifacts giữa các stage lưu ở S3, tích hợp CloudWatch Events/EventBridge để trigger.
- **`CodeArtifact`** (package repo), **`CodeGuru`** (review/profiler — biết khái niệm).

### `CloudFormation` + `SAM` (IaC)
- Template sections: **Resources (bắt buộc)**, Parameters, Mappings, Outputs, Conditions, Metadata, Transform, Rules.
- **Intrinsic functions**: `Ref`, `Fn::GetAtt`, `Fn::Sub`, `Fn::Join`, `Fn::ImportValue`, `Fn::FindInMap`, `Fn::If`, `Fn::Select`, `Fn::Base64`.
- **Cross-stack**: `Export` (Outputs) + `Fn::ImportValue`; nested stacks; **change sets**; stack policy; **DeletionPolicy** (Retain/Snapshot/Delete); `DependsOn`; `CreationPolicy`/`UpdatePolicy`; drift detection.
- **`SAM`**: `Transform: AWS::Serverless-2016-10-31`; resources rút gọn `AWS::Serverless::Function` / `::Api` / `::SimpleTable`. Lệnh: `sam build`, `sam deploy --guided`, `sam local invoke`, `sam local start-api`, `sam sync`.

### `Elastic Beanstalk`
- Platform + environment (web tier vs **worker tier** — worker đọc từ SQS).
- **Deployment policies (5)**: All at once (downtime) / **Rolling** / **Rolling with additional batch** / **Immutable** (an toàn nhất, tạo instance mới hoàn toàn) / **Traffic splitting** (canary %, cần ALB). **Blue/Green KHÔNG phải policy** — là kỹ thuật **swap CNAME/URL** giữa 2 environment.
- `.ebextensions/*.config` để tuỳ biến; `Dockerrun.aws.json`.

### `ECS` / `Fargate` / `ECR`
- Task definition, service, cluster; **EC2 launch type vs Fargate** (serverless).
- **Task role** (quyền cho app trong container) vs **execution role** (quyền kéo image/ghi log).
- `ECR`: `aws ecr get-login-password` → docker login/push/pull; lifecycle policy; image scanning.
- Dynamic port mapping với ALB.

### `Step Functions`
- **ASL (Amazon States Language)** JSON. Standard (dài, exactly-once) vs **Express** (ngắn, high-volume).
- States: `Task`, `Choice`, `Parallel`, `Map`, `Wait`, `Pass`, `Succeed`, `Fail`.
- Error handling: **`Retry`** + **`Catch`**.

### `ElastiCache`
- **Redis** (replication, persistence, sorted set, pub/sub, HA) vs **Memcached** (multi-threaded, đơn giản, không persistence).
- Caching strategies: **Lazy loading** (cache-aside) vs **Write-through** + **TTL**.

### `CloudWatch` + `X-Ray` (observability)
- **Metrics** (custom, high-resolution), namespaces, dimensions; **Logs** (log group/stream, metric filter, subscription filter); **Alarms** (OK/ALARM/INSUFFICIENT_DATA).
- **EventBridge / CloudWatch Events**: rules theo pattern hoặc schedule (cron/rate) → trigger Lambda/Step Functions...
- **`X-Ray`**: enable *active tracing* cho Lambda; **annotations** (indexed, filter được) vs **metadata** (không indexed); sampling rules; daemon (chạy trên EC2/ECS).

### `RDS` / `RDS Proxy` (góc dev)
- Quản lý connection pool → **RDS Proxy** giảm số connection (đặc biệt với Lambda), tích hợp Secrets Manager để auth.

---

## 6. Những con số PHẢI thuộc lòng

> Đề rất hay dựa vào các giới hạn/mặc định này. Học thuộc như bảng cửu chương.

### Lambda
- Timeout tối đa: **15 phút (900s)**.
- Memory: **128 MB → 10,240 MB** (CPU scale theo memory).
- `/tmp`: **512 MB** mặc định → tối đa **10 GB**.
- Deployment package: **50 MB** (zip upload trực tiếp), **250 MB** (unzip, gồm layers), **10 GB** (container image).
- Env vars: tổng **4 KB**.
- Layers: tối đa **5**.
- Concurrency mặc định/region: **1,000** (soft limit).
- Payload: **6 MB** (sync), **1 MB** (async) — *AWS đã nâng từ 256 KB; một số đề/khoá cũ vẫn ghi 256 KB*.
- Async: retry **2 lần**.
- Concurrency scaling: **1,000 execution environments / 10 giây / function**.
- Response streaming: tới **200 MB** (cách vượt cap 6 MB sync).

### DynamoDB
- Item tối đa: **400 KB**.
- 1 RCU = 1 strong read/s @ **4 KB** (hoặc 2 eventual).
- 1 WCU = 1 write/s @ **1 KB**.
- Streams retention: **24h**.
- Query kết quả tối đa **1 MB**/lần (rồi paginate).

### API Gateway
- Integration timeout: mặc định **29s**; tăng tới **300s** qua `Service Quotas` cho **Regional/private REST API** (KHÔNG áp dụng edge-optimized REST & HTTP API).
- Throttling mặc định account: **10,000 req/s** (burst **5,000**).
- Cache TTL mặc định: **300s** (0–3600s).
- Payload tối đa: **10 MB**.

### SQS
- Message tối đa: **256 KB**.
- Visibility timeout: mặc định **30s**, tối đa **12h**.
- Retention: mặc định **4 ngày**, khoảng **60s–14 ngày**.
- Long polling `WaitTimeSeconds`: tối đa **20s**.
- Delay queue: tối đa **15 phút**.
- FIFO throughput: **300 msg/s** (3,000 với batching); bật **high throughput mode** → tới **~30,000 msg/s** (theo region).

### Kinesis Data Streams
- Shard: **1 MB/s** hoặc **1,000 records/s** in; **2 MB/s** out.
- Record tối đa: **1 MB**.
- Retention: **24h** mặc định → **365 ngày**.
- **Capacity mode**: `on-demand` (AWS tự quản shard) vs `provisioned` (tự đặt số shard).

### KMS / S3 / khác
- KMS encrypt trực tiếp: tối đa **4 KB** (lớn hơn → envelope encryption).
- S3 object tối đa: **5 TB**; single PUT ≤ **5 GB**; multipart khuyến nghị > **100 MB**.
- SNS/SQS message: **256 KB**.
- Cognito JWT: ID/Access token hết hạn **1h** (mặc định), refresh token tuỳ cấu hình (đến 10 năm).

---

## 7. Bảng phản xạ: Keyword → Dịch vụ

> Luyện đọc đề → **bật ngay** đáp án. Đây là kỹ năng "phản xạ" quyết định tốc độ & độ chính xác.

| Từ khoá trong đề | Phản xạ tới |
|---|---|
| "temporary credentials", "cross-account", "assume role" | **STS `AssumeRole`** |
| "mobile app login", "social login", trả JWT | **Cognito User Pool** |
| "mobile app cần gọi trực tiếp AWS service", đổi token lấy AWS creds | **Cognito Identity Pool** |
| "decouple", "buffer", "at-least-once", 1 consumer | **SQS** |
| "ordered", "replay", "multiple consumers", real-time streaming | **Kinesis Data Streams** |
| "no shard/capacity management" (Kinesis) | **Kinesis on-demand mode** |
| "fan-out", "1 message → nhiều nơi", push notification | **SNS** (hoặc SNS + SQS) |
| "reduce Lambda cold start", giữ ấm | **Provisioned Concurrency** (đảm bảo) hoặc **SnapStart** (Java/Python/.NET, best-effort, chỉ version+alias) |
| "limit blast radius"/giới hạn concurrency 1 function | **Reserved Concurrency** |
| "microsecond latency" cho DynamoDB | **DAX** |
| "sub-millisecond cache", session store | **ElastiCache** |
| "encrypt > 4 KB data" | **Envelope encryption / `GenerateDataKey`** |
| "rotate database credentials tự động" | **Secrets Manager** |
| "lưu config/plaintext hoặc SecureString, miễn phí" | **SSM Parameter Store** |
| "canary/linear traffic shifting" cho Lambda | **CodeDeploy + alias weighted** |
| "zero-downtime, tạo môi trường mới hoàn toàn" (Beanstalk) | **Immutable** hoặc **Blue/Green** |
| "buildspec.yml" | **CodeBuild** |
| "appspec.yml", lifecycle hooks | **CodeDeploy** |
| "orchestrate multiple pipeline stages" | **CodePipeline** |
| "trace request qua nhiều service", latency breakdown | **X-Ray** |
| "filter/tìm theo giá trị trong trace" | **X-Ray annotation** (không phải metadata) |
| "custom metric", alarm, log | **CloudWatch** |
| "audit ai gọi API nào" | **CloudTrail** |
| "schedule/cron trigger" | **EventBridge (CloudWatch Events)** |
| "presigned URL" upload/download tạm | **S3 presigned URL** |
| "phân phối file private qua CDN / nhiều file" | **CloudFront signed cookies** |
| "chặn S3 chỉ cho CloudFront" | **OAC** |
| "throttling / ProvisionedThroughputExceeded" | **Exponential backoff + jitter** |
| "hot partition" | **Thiết kế partition key phân tán đều** |
| "connection pool cho Lambda → RDS" | **RDS Proxy** |
| "orchestration workflow, retry/catch giữa các bước" | **Step Functions** |
| "run container serverless" | **Fargate** |
| "quyền app trong container" vs "kéo image/ghi log" | **Task role** vs **Execution role** |

---

## 8. Thực hành hands-on

> **Bắt buộc tự tay làm** — DVA đầy câu về "config đặt ở đâu / CLI nào / hành vi thực tế". Làm trong **Free Tier**.

### Nhóm Serverless (ưu tiên cao nhất)
- [ ] Tạo Lambda bằng **Console**, **AWS CLI** (`aws lambda create-function`), và **SAM**.
- [ ] Publish **version**, tạo **alias**, cấu hình **weighted alias** (90/10).
- [ ] Tạo & gắn **Lambda layer**.
- [ ] Cấu hình **environment variables** + mã hoá KMS.
- [ ] Set **reserved** & **provisioned concurrency**, quan sát cold start.
- [ ] Async invoke + cấu hình **DLQ** và **destinations**.
- [ ] Event source mapping: SQS → Lambda, DynamoDB Streams → Lambda.

### Nhóm API + Data
- [ ] Dựng **REST API** (API Gateway) → Lambda → DynamoDB (CRUD đầy đủ).
- [ ] So sánh **REST vs HTTP API**; cấu hình **stage + stage variables** trỏ alias.
- [ ] Thêm **Cognito authorizer** & **Lambda authorizer**; bật **CORS**; **usage plan + API key**.
- [ ] DynamoDB: tạo **GSI/LSI**, bật **Streams**, thử **conditional write** + **optimistic locking**, **TransactWriteItems**, tính **WCU/RCU** thủ công.
- [ ] S3: tạo **presigned URL** (PUT & GET), **multipart upload** qua CLI, bật **event notification** → Lambda.

### Nhóm Security
- [ ] Viết IAM policy least-privilege cho Lambda; test **explicit deny**.
- [ ] `aws sts assume-role` cross-account (2 account hoặc mô phỏng).
- [ ] Cognito User Pool + Hosted UI login → nhận JWT; Identity Pool → nhận temp creds.
- [ ] KMS: `generate-data-key`, encrypt/decrypt; bật rotation.
- [ ] Lưu secret ở **Secrets Manager** (bật rotation) & param ở **Parameter Store SecureString**; đọc từ Lambda.

### Nhóm Deployment / CI-CD / IaC
- [ ] Viết **buildspec.yml** + chạy **CodeBuild**.
- [ ] Viết **appspec.yml** + deploy EC2/Lambda bằng **CodeDeploy** (thử In-place & Canary).
- [ ] Ráp **CodePipeline** end-to-end: Source → Build → Deploy.
- [ ] Viết **CloudFormation template** (Parameters/Outputs/Ref/GetAtt/Sub), tạo **change set**, thử **Export/ImportValue**.
- [ ] **SAM**: `sam init` → `sam build` → `sam local start-api` → `sam deploy --guided`.
- [ ] Deploy app lên **Elastic Beanstalk**, thử **Rolling** & **Immutable**.
- [ ] Push image lên **ECR**, chạy task trên **ECS/Fargate**.

### Nhóm Observability / Optimization
- [ ] Bật **X-Ray active tracing** cho Lambda + API GW; xem **service map**; thêm **annotation**.
- [ ] Tạo **custom CloudWatch metric**, **metric filter** từ log, **alarm**.
- [ ] Tạo **EventBridge rule** cron trigger Lambda.
- [ ] `ElastiCache`/`DAX` cache demo; đo cải thiện latency.

---

## 9. Tài nguyên học tập

### Chính thức (AWS)
- **Exam Guide (PDF)** — đọc kỹ task statements & in/out-of-scope services.
- **Sample Questions** chính thức của AWS.
- **AWS Skill Builder**: "Exam Prep: AWS Certified Developer – Associate (DVA-C02)" (có Official Practice Question Set + Exam Prep Standard/Enhanced).
- **AWS Documentation** cho từng dịch vụ (đặc biệt Lambda, DynamoDB, API Gateway Developer Guides).
- **AWS Whitepapers**: *Serverless Applications Lens (Well-Architected)*, *Best Practices for DynamoDB*.

### Khóa học video (chọn 1)
- **Stephane Maarek** — *Ultimate AWS Certified Developer Associate DVA-C02* (Udemy) — phổ biến & sát đề nhất.
- **Adrian Cantrill** — *AWS Certified Developer Associate* — sâu, nhiều hands-on.
- **A Cloud Guru / Pluralsight** — thay thế.

### Practice exams (quan trọng — luyện phản xạ)
- **Tutorials Dojo (Jon Bonso)** — bộ practice test được đánh giá tốt nhất, giải thích chi tiết.
- **Stephane Maarek practice tests** (Udemy).
- Official Practice Question Set trên Skill Builder.

### Cheat sheets
- Tutorials Dojo Cheat Sheets, `AWS-DVA-C02-cheatsheet` (GitHub).

> 💡 **Tận dụng repo này:** áp dụng lại quy trình bạn đã làm với `SAA-C03` — mỗi câu practice sai → viết 1 file phân tích trong `questions/DVA-C02/` theo format 6 mục (xem `aws-saa-c03-analysis-format.md`).

---

## 10. Chiến lược làm bài thi

- **Ngân sách thời gian:** ~2 phút/câu. Câu khó → flag & bỏ qua, quay lại sau. Đừng để 1 câu ăn hết 5 phút.
- **Đọc câu hỏi TRƯỚC, đọc đáp án SAU:** xác định keyword ("least cost", "most secure", "least operational overhead", "real-time", "ordered").
- **Loại trừ:** thường 2 đáp án sai rõ ràng → còn 2 → phân biệt bằng chi tiết (managed vs tự quản, đúng service vs sai service).
- **Chú ý qualifier:** *"most cost-effective"*, *"minimal code changes"*, *"fully managed"*, *"without provisioning servers"* → quyết định đáp án.
- **Multiple response:** đọc kỹ "Choose TWO/THREE" — chọn đủ, không thừa.
- **Bẫy phổ biến:** đáp án đúng về kỹ thuật nhưng KHÔNG đáp ứng yêu cầu (ví dụ đúng nhưng tốn kém hơn / nhiều operational overhead hơn).
- **Đừng đổi đáp án** trừ khi chắc chắn hiểu sai ban đầu.
- **Phòng thi:** dùng feature *flag for review*; kiểm tra thiết bị nếu thi online trước ngày thi.

---

## 11. CHECKLIST TOÀN DIỆN

> Tick từng mục khi **hiểu + tự tay làm được**. Nhóm theo Domain để dễ theo dõi.

### 📋 A. Chuẩn bị & Nền tảng
- [ ] Đăng ký tài khoản thi, chọn hình thức (center/online), đặt lịch tạm.
- [ ] Đọc hết **Exam Guide** chính thức + danh sách in/out-of-scope services.
- [ ] Nắm bảng tỉ trọng Domain (32/26/24/18) để phân bổ thời gian.
- [ ] Chọn 1 khóa video + 1 bộ practice test.
- [ ] Ôn nhanh nền SAA: IAM, VPC, EC2, S3, RDS, CloudFront, Route 53.
- [ ] Thành thạo **AWS CLI** cơ bản + cấu hình profile/credentials.
- [ ] Hiểu **credential provider chain** & cách SDK tìm credentials.
- [ ] Hiểu **exponential backoff + jitter**, retry, pagination, waiters trong SDK.

### 📘 B. Domain 1 — Development (32%)
**Lambda**
- [ ] Handler, event, context, runtimes.
- [ ] Versions vs `$LATEST`; aliases + weighted routing.
- [ ] Layers (≤ 5), environment variables (≤ 4 KB, KMS).
- [ ] Reserved vs provisioned concurrency; cold start.
- [ ] Sync vs async (retry 2, DLQ, destinations) vs event source mapping.
- [ ] `/tmp` (512 MB→10 GB); giới hạn timeout 15', memory 10 GB.
- [ ] Đóng gói zip vs container; Lambda trong VPC (cần NAT ra ngoài).

**DynamoDB**
- [ ] Partition/sort key; item ≤ 400 KB.
- [ ] Tính WCU/RCU (strong vs eventual); Query vs Scan.
- [ ] GSI vs LSI (khác biệt & khi nào tạo được).
- [ ] Streams (24h) + trigger Lambda; view types.
- [ ] DAX; conditional writes; optimistic locking; atomic counter.
- [ ] TransactWriteItems, BatchGet/Write, PartiQL, TTL.
- [ ] Provisioned + auto scaling vs on-demand; tránh hot partition.

**API Gateway**
- [ ] REST vs HTTP vs WebSocket.
- [ ] Stages + stage variables; integration types (proxy vs non-proxy).
- [ ] Authorizers (IAM/Cognito/Lambda); usage plan + API key.
- [ ] Caching (TTL 300s), CORS, mapping templates, timeout 29s.

**S3 & khác**
- [ ] CRUD, presigned URL, multipart upload, event notifications.
- [ ] SSE-S3/KMS/C; strong read-after-write consistency.
- [ ] RDS connection pooling / RDS Proxy.
- [ ] ElastiCache (lazy loading vs write-through).
- [ ] SDK: cấu hình client, region, endpoint, error handling.

### 🔐 C. Domain 2 — Security (26%)
- [ ] Cấu trúc IAM policy (Effect/Action/Resource/Condition/Principal).
- [ ] Policy evaluation: explicit Deny > Allow > default Deny.
- [ ] Identity-based vs resource-based policy.
- [ ] Roles: Lambda execution role, EC2 instance profile, ECS task vs execution role.
- [ ] STS: AssumeRole / AssumeRoleWithWebIdentity / GetSessionToken; cross-account.
- [ ] Cognito **User Pool** (JWT: ID/Access/Refresh) vs **Identity Pool** (temp AWS creds).
- [ ] Federation SAML/OIDC/social; MFA; Hosted UI.
- [ ] KMS: symmetric vs asymmetric; envelope encryption; `GenerateDataKey`; giới hạn 4 KB.
- [ ] Key policy vs grant; rotation; loại key (owned/managed/CMK).
- [ ] Encryption at rest (S3/EBS/DynamoDB/RDS) & in transit (TLS/ACM).
- [ ] Secrets Manager (rotation, RDS) vs Parameter Store (String/SecureString).
- [ ] Không hard-code credentials; mã hoá env vars; sanitize logs (PII).

### 🚀 D. Domain 3 — Deployment (24%)
- [ ] Đóng gói artifacts: Lambda zip/layer/container, SAM package, ECR image.
- [ ] **buildspec.yml** (phases install/pre_build/build/post_build, artifacts, cache, env).
- [ ] **appspec.yml** (hooks EC2 vs Lambda/ECS, thứ tự lifecycle).
- [ ] CodeDeploy: In-place vs Blue/Green; config AllAtOnce/HalfAtATime/OneAtATime; Canary/Linear cho Lambda.
- [ ] CodePipeline: stages, artifacts store (S3), trigger.
- [ ] CodeCommit; CodeArtifact (khái niệm); CodeGuru (khái niệm).
- [ ] CloudFormation: sections; intrinsic functions (Ref/GetAtt/Sub/Join/ImportValue/FindInMap/If).
- [ ] CloudFormation: change sets, nested stacks, Export/ImportValue, DeletionPolicy, DependsOn, drift.
- [ ] SAM: Transform, Serverless::Function/Api/SimpleTable; `sam build/deploy/local/sync`.
- [ ] Elastic Beanstalk: All at once/Rolling/Rolling+batch/Immutable/Blue-Green; `.ebextensions`; worker tier.
- [ ] ECS/Fargate: task definition, service, EC2 vs Fargate; ALB dynamic port mapping.
- [ ] ECR: login/push/pull, lifecycle policy, image scan.
- [ ] Chiến lược rollback & traffic shifting.

### 🔧 E. Domain 4 — Troubleshooting & Optimization (18%)
- [ ] CloudWatch: metrics (custom/high-res), namespaces, dimensions.
- [ ] CloudWatch Logs: log group/stream, metric filter, subscription filter, EMF.
- [ ] Alarms (OK/ALARM/INSUFFICIENT_DATA); dùng để auto-remediate.
- [ ] CloudTrail: audit API calls; phân biệt với CloudWatch.
- [ ] EventBridge/CloudWatch Events: rule pattern & schedule (cron/rate).
- [ ] X-Ray: segments/subsegments; **annotations vs metadata**; sampling; service map; daemon; active tracing.
- [ ] Đọc & xử lý mã lỗi phổ biến (429/5xx/throttling exceptions).
- [ ] Tối ưu Lambda (memory→CPU, provisioned concurrency).
- [ ] Tối ưu DynamoDB (hot partition, on-demand, DAX).
- [ ] Caching layers (ElastiCache/DAX/API GW cache/CloudFront).
- [ ] Step Functions: ASL, states, Retry/Catch, Standard vs Express.
- [ ] SQS/SNS/Kinesis: chọn đúng khi nào dùng cái nào (bảng §7).

### 🔢 F. Con số & Phản xạ
- [ ] Học thuộc toàn bộ bảng số ở [§6](#6-những-con-số-phải-thuộc-lòng).
- [ ] Luyện bảng phản xạ keyword→dịch vụ ở [§7](#7-bảng-phản-xạ-keyword--dịch-vụ) đến mức tự động.

### 🧪 G. Hands-on
- [ ] Hoàn thành TẤT CẢ lab ở [§8](#8-thực-hành-hands-on) (đặc biệt nhóm Serverless & CI/CD).

### 📝 H. Ôn luyện & Thi thử (theo Cơ chế đảm bảo đậu ở §3)
- [ ] Mini-mock **Domain 1** (Tuần 5) đạt **≥ 70%**.
- [ ] Mini-mock **Domain 1+2** (Tuần 7) đạt **≥ 72%**.
- [ ] Mini-mock **Domain 3** (Tuần 8) đạt **≥ 70%**.
- [ ] Làm **≥ 3 bộ full-length mock KHÁC NHAU** (65 câu, canh giờ 130').
- [ ] Đạt **ổn định ≥ 85%** trên ≥ 3 bộ mock khác nhau trước khi đặt lịch thi (biên an toàn so với ngưỡng đậu 72%).
- [ ] Với **mỗi câu sai** → viết file phân tích trong `questions/DVA-C02/` (format 6 mục) + ôn theo mốc 1/3/7 ngày.
- [ ] Ôn lại toàn bộ file câu sai 2–3 lần đến khi trả lời đúng 100%.
- [ ] Làm bộ Official Practice Question Set (Skill Builder).
- [ ] Đọc lại cheat sheet + bảng số §6 + bảng phản xạ §7 lần cuối trước ngày thi.
- [ ] (Van an toàn) Nếu bất kỳ full mock nào **< 75%** → lùi lịch thi 1 tuần, cày lại vùng yếu.

### 🎓 I. Trước ngày thi
- [ ] Kiểm tra thiết bị/phòng (nếu online proctored) hoặc địa điểm center.
- [ ] Ngủ đủ; chuẩn bị giấy tờ tuỳ thân.
- [ ] Ôn nhanh: bảng số (§6) + bảng phản xạ (§7) + danh sách bẫy.

---

## 📌 Tóm tắt 1 dòng để nhớ

> **Bộ ba `Lambda` + `DynamoDB` + `API Gateway` là trái tim của DVA-C02.** Bọc quanh nó là **Security (IAM/STS/Cognito/KMS/Secrets)**, **CI-CD (Code* + CFN/SAM)**, và **Observability (CloudWatch/X-Ray)**. Học lý thuyết → **tự tay code/deploy** → **cày practice + ghi lại câu sai**. Đó là con đường ngắn nhất tới 720+.

---

### 🔗 Nguồn tham khảo (đã dùng để soạn tài liệu)

- [AWS DVA-C02 Exam Guide (chính thức, PDF)](https://d1.awsstatic.com/training-and-certification/docs-dev-associate/AWS-Certified-Developer-Associate_Exam-Guide.pdf)
- [AWS Certified Developer – Associate (trang chứng chỉ chính thức)](https://docs.aws.amazon.com/aws-certification/latest/examguides/developer-associate-02.html)
- [DVA-C02 Domains — Educative](https://www.educative.io/courses/aws-certified-developer-associate/understanding-dva-c02-domains-and-exam-guide)
- [How to pass DVA-C02 — Hrishi Patel (Medium)](https://medium.com/@hrishipatel99/how-to-aws-developer-associate-dva-c02-4bdc146e2e04)
- [AWS DVA-C02 Cheatsheet (GitHub)](https://github.com/parseltonguedev/AWS-DVA-C02-cheatsheet)
- [FlashGenius — DVA-C02 Ultimate 2025 Guide](https://flashgenius.net/blog-article/aws-certified-developer-associate-dva-c02-the-ultimate-2025-guide)
