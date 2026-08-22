# ✅ Nhật ký Validate kiến thức — DVA-C02 Study Plan

> **Ngày rà soát:** 2026-07-07 · **Phương pháp:** đối chiếu toàn bộ plan với tài liệu AWS **hiện hành** (bản đã crawl trong mỗi `week-NN/resources/` + kiểm tra thay đổi gần đây trên `docs.aws.amazon.com`).
> Mục tiêu: **loại bỏ thông tin lỗi thời** và **bổ sung phần còn thiếu** so với phạm vi thi thực tế.

---

## 🔴 Đã SỬA — thông tin lỗi thời / sai (quan trọng)

| # | Chỗ | Trước (lỗi thời/sai) | Sau (hiện hành) | Nguồn |
|---|---|---|---|---|
| 1 | `Lambda` async payload (week-02, §5, §6) | 256 KB | **1 MB** (kèm ghi chú AWS đã nâng) | Lambda quotas page |
| 2 | `API Gateway` integration timeout (week-04, §5, §6) | "29s là cứng, không tăng được" | **Mặc định 29s, tăng tới 300s** qua Service Quotas cho Regional/private REST API (không áp dụng edge-optimized REST & HTTP API) | API GW limits table (thay đổi 06/2024) |
| 3 | `Elastic Beanstalk` deployment policies (week-08, §5) | Liệt "Blue/Green" như 1 policy | 5 policy đúng: All at once / Rolling / Rolling+batch / **Immutable** / **Traffic splitting**. Blue/Green = kỹ thuật swap CNAME (KHÔNG phải policy) | Beanstalk deploy docs |
| 4 | `CodeStar` / `CodeConnections` (week-08) | "GitHub qua CodeConnections/CodeStar" | Chỉ **`CodeConnections`** (đổi tên từ CodeStar Connections 2024). AWS CodeStar đã **EOL 31/07/2024** | AWS What's New |
| 5 | `DynamoDB` TTL (week-03) | "~48 giờ" (con số cứng) | "**trong vài ngày**, không tức thì, không tốn WCU" (ghi chú đề cũ hay ghi 48h) | DynamoDB TTL docs |
| 6 | Danh sách in-scope services (week-10 resource) | Bản model tóm tắt từ PDF — thiếu ~20 dịch vụ, sai vài mục | Thay bằng **danh sách authoritative (47 dịch vụ)** từ trang chính thức | AWS Certification in-scope page |
| 7 | Typo (week-04) | `aws s3presign` | `aws s3 presign` | — |

---

## 🟡 Đã BỔ SUNG — phần còn thiếu so với phạm vi thi

**Ưu tiên cao**
- **`Lambda` SnapStart** (week-02, §5, §7): giảm cold start best-effort cho `Java 11+`/`Python 3.12+`/`.NET 8+`; chỉ trên version/alias; ≠ provisioned concurrency. (Trước đây "giảm cold start" chỉ có provisioned concurrency.)
- **`CloudFront` góc developer** (week-04, §5, §7): **signed URL vs signed cookies**, so sánh với **`S3` presigned URL**, **OAC** (thay OAI), cache invalidation. (Trước đây phủ 0% — đây là điểm dev hay bị hỏi.)
- **`AppSync`** (week-04): managed GraphQL, resolver, subscription real-time — đối chiếu với `API Gateway`.

**Ưu tiên trung bình**
- **`Kinesis` on-demand capacity mode** (week-05, §5, §6) — keyword "no shard/capacity management".
- **`SQS` FIFO high throughput mode** (~30.000 msg/s) (week-05, §6).
- **`Cognito` Managed Login** (week-06, §5): thế hệ mới của Hosted UI (2024) + feature plan Lite/Essentials/Plus.
- **`AWS AppConfig`** (week-08): feature flags & config runtime + gradual rollout.
- **`KMS` on-demand rotation + custom rotation period** (week-07, §5).
- **`Lambda` số liệu mới** (week-02, §6): concurrency scaling 1.000 env/10s/function; response streaming 200 MB.
- **`S3` mã hoá mặc định** (week-04): SSE-S3 tự động cho mọi object mới từ 01/2023.
- **Presigned URL expiry** (week-04): SigV4 tối đa 7 ngày; Console 12h.
- **`DynamoDB` transaction limits** (week-03): 100 action / 100 item / 4 MB; **DAX chỉ cache eventual read**.

**Ưu tiên thấp (ghi chú nhận diện)**
- `X-Ray` đang hợp nhất dưới `CloudWatch` (Application Signals, Transaction Search — 11/2024) (week-09).
- `EventBridge Scheduler` (2022) vs EventBridge rule schedule (week-09).
- `STS` regional endpoints là mặc định ở CLI v2/SDK mới (week-06).
- `Beanstalk` platform Amazon Linux 2 → **AL2023** (week-08).
- `Athena`, `Amplify`, `WAF` — ghi chú 1 dòng nhận diện keyword.
- Thuật ngữ "CMK" = customer managed key (tên cũ) (week-07).
- `ElastiCache` engine hiện tại: **Valkey / Redis OSS / Memcached** + ElastiCache Serverless (week-05).

---

## 🟢 Đã KIỂM — chính xác, không đổi

Các số liệu/khái niệm cốt lõi đã được xác nhận **đúng & cập nhật**: `Lambda` (memory 128–10240 MB, 1769 MB=1 vCPU, /tmp 512 MB–10 GB, timeout 900s, package 50/250 MB/10 GB, async retry 2 lần); `DynamoDB` (RCU/WCU, item 400 KB, GSI/LSI, Streams 24h); `API Gateway` (throttle 10.000/burst 5.000, cache TTL 300s, REST vs HTTP); `S3` (multipart, 5 TB, strong consistency); messaging (`SQS`/`SNS` 256 KB, Kinesis shard 1MB/1000rec-s); `Step Functions` (Standard vs Express); IAM (Deny>Allow>implicit Deny); STS (4 API); `KMS` (envelope, 4 KB, key policy vs grant); `Secrets Manager` vs `Parameter Store`; CI/CD (buildspec/appspec hooks, CodeDeploy configs); `CloudFormation`/`SAM`; `ECS`/`ECR` (task vs execution role); observability (`CloudWatch`/`X-Ray` annotations vs metadata).

---

> ⚠️ **Lưu ý về độ tươi của dữ liệu:** các file trong `week-NN/resources/` được crawl từ docs AWS tại thời điểm rà soát (2026-07). AWS cập nhật docs liên tục — trước ngày thi nên đối chiếu nhanh lại các **con số giới hạn** với link nguồn ghi ở đầu mỗi file resource.
