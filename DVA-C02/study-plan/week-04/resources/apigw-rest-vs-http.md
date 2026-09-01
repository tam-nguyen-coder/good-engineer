	

# Choose between REST APIs and HTTP APIs (`API Gateway`)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html
> **Tuần:** 4 — `API Gateway` + `S3` (góc Developer) · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `REST API` = nhiều tính năng hơn; `HTTP API` = tối giản, **rẻ hơn + độ trễ thấp hơn**. Đề hỏi "proxy đơn giản tới `Lambda`, rẻ, độ trễ thấp" → chọn **`HTTP API`**.
- Các tính năng CHỈ có ở `REST API` (bẫy hay gặp): **`API keys`**, **per-client rate limiting / usage throttling**, **`caching`**, **request validation**, **`AWS WAF`**, **Private endpoint**, **request body transformation** (`VTL`), **Mock integration**, **execution logs**, **`X-Ray`**, **canary release**, **gateway responses tuỳ biến**, **developer portal**, **response streaming**.
- Authorization: cả hai đều hỗ trợ **`IAM`**, **`Cognito`**, **`Lambda authorizer`**. **`JWT authorizer` (OIDC/JWT)** CHỈ có ở `HTTP API`. **Resource policies** CHỈ có ở `REST API`.
- `REST API` có 3 endpoint type: **Edge-optimized, Regional, Private**. `HTTP API` **chỉ có Regional** (không có Edge-optimized, không có Private).
- Deployment: `REST API` = user-controlled deployment (bạn tự deploy). `HTTP API` = hỗ trợ thêm **automatic deployment** (auto-deploy khi thay đổi).
- Chỉ `REST API` mới có **Mock integration** (hữu ích trả CORS preflight). `HTTP API` không có.
- Cả hai hỗ trợ private integration với **NLB** và **ALB**; nhưng **`AWS Cloud Map`** private integration CHỈ có ở `HTTP API`.

---

## 📊 Bảng so sánh tổng hợp: `REST API` vs `HTTP API`

### A. Tổng quan (khác biệt cốt lõi)

| Tiêu chí                   | `REST API`                                   | `HTTP API`                                    | Ghi nhớ / Bẫy đề                                                                |
| ---------------------------- | ---------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------- |
| Triết lý thiết kế        | Full-feature, nhiều "API management"          | Tối giản, chỉ giữ phần cốt lõi           | `HTTP API` ≈ **tập con** của `REST API` (trừ 3 ngoại lệ ở bảng B) |
| Giá (us-east-1, tham khảo) | ≈**$3.50** / 1 triệu request           | ≈**$1.00** / 1 triệu request            | Đề nói "**cost-effective / lower cost**" → `HTTP API`                   |
| Độ trễ                    | Cao hơn                                       | **Thấp hơn** (~50% p99 theo AWS)        | Đề nói "**lower latency**" → `HTTP API`                                 |
| Endpoint type                | Edge-optimized · Regional ·**Private** | **Chỉ Regional**                         | Đề cần**Private API trong `VPC`** → buộc `REST API`                  |
| Deployment                   | User-controlled (tự deploy stage)             | User-controlled**+ automatic deployment** | Ngoại lệ đi ngược chiều#1                                                     |
| Lambda payload format        | 1.0                                            | **2.0** (mặc định) hoặc 1.0           | Migrate`REST` → `HTTP` phải sửa code đọc `event`                         |
| Định nghĩa API            | `OpenAPI 3.0` / Swagger 2.0                  | `OpenAPI 3.0`                                 | Cả hai import được`OpenAPI`                                                   |
| Loại thứ ba                | —                                             | —                                              | `WebSocket API` là loại riêng: dùng cho **two-way / realtime**          |

### B. Bảng gộp tính năng (một chỗ, thay cho 7 bảng rời bên dưới)

| Nhóm          | Tính năng                                                         | `REST API` | `HTTP API` | Ghi nhớ / Bẫy đề                                                      |
| -------------- | ------------------------------------------------------------------- | ------------ | ------------ | ------------------------------------------------------------------------- |
| Endpoint       | Edge-optimized                                                      | ✅           | ❌           | Cần edge →`REST API`, hoặc đặt `CloudFront` trước `HTTP API` |
| Endpoint       | Regional                                                            | ✅           | ✅           | Mặc định của`HTTP API`                                              |
| Endpoint       | Private (`VPC` endpoint)                                          | ✅           | ❌           | **Bẫy kinh điển**: "private API only in VPC" → `REST API`     |
| Security       | Mutual TLS (`mTLS`)                                               | ✅           | ✅           | Cả hai đều có — đừng loại`HTTP API` vì `mTLS`                |
| Security       | Client certificate cho backend                                      | ✅           | ❌           | Backend cần verify request từ`API Gateway` → `REST API`            |
| Security       | `AWS WAF`                                                         | ✅           | ❌           | Đề nói**SQLi / XSS / IP block bằng `WAF`** → `REST API`    |
| Security       | Resource policies                                                   | ✅           | ❌           | Chặn theo IP / VPC / account bằng policy →`REST API`                 |
| Authorization  | `IAM` (`SigV4`)                                                 | ✅           | ✅           | Cả hai                                                                   |
| Authorization  | `Amazon Cognito`                                                  | ✅           | ✅           | `HTTP API` dùng Cognito **qua `JWT authorizer`**               |
| Authorization  | `Lambda authorizer` (custom)                                      | ✅           | ✅           | Cả hai                                                                   |
| Authorization  | `JWT authorizer` (OIDC/OAuth2 native)                             | ❌           | ✅           | Ngoại lệ đi ngược chiều#2 — "**JWT/OIDC không cần code**"  |
| API management | Custom domain                                                       | ✅           | ✅           | Cả hai                                                                   |
| API management | `API keys`                                                        | ✅           | ❌           | **Bẫy**: "phát API key cho từng partner" → `REST API`         |
| API management | Per-client rate limiting / usage plan                               | ✅           | ❌           | "**throttle theo từng client / quota**" → `REST API`            |
| API management | Developer portal                                                    | ✅           | ❌           | Bán/publish API cho dev ngoài →`REST API`                            |
| Development    | CORS configuration                                                  | ✅           | ✅           | `HTTP API` cấu hình CORS **dễ hơn** (không cần Mock)        |
| Development    | Caching (response cache)                                            | ✅           | ❌           | "**cache response để giảm tải backend**" → `REST API`        |
| Development    | Request validation (schema/model)                                   | ✅           | ❌           | "**validate body trước khi vào `Lambda`**" → `REST API`     |
| Development    | Request**parameter** transformation                           | ✅           | ✅           | Cả hai (mapping header/query/path)                                       |
| Development    | Request**body** transformation (`VTL`)                      | ✅           | ❌           | Cần`VTL` mapping template → `REST API`                              |
| Development    | Custom gateway responses (4xx/5xx tuỳ biến)                       | ✅           | ❌           | Đổi nội dung lỗi 403/429 →`REST API`                               |
| Development    | Canary release deployment                                           | ✅           | ❌           | "**shift 10% traffic sang version mới**" → `REST API`           |
| Development    | Test invocation (test từ console)                                  | ✅           | ❌           | `HTTP API` không có nút Test                                         |
| Monitoring     | `CloudWatch` metrics                                              | ✅           | ✅           | Cả hai                                                                   |
| Monitoring     | Access logs →`CloudWatch Logs`                                   | ✅           | ✅           | Cả hai                                                                   |
| Monitoring     | Access logs →`Amazon Data Firehose`                              | ✅           | ❌           | Stream log sang`S3`/`OpenSearch` qua Firehose → `REST API`         |
| Monitoring     | **Execution logs** (log chi tiết từng stage)                | ✅           | ❌           | "**debug mapping / integration error**" → `REST API`             |
| Monitoring     | `AWS X-Ray` tracing                                               | ✅           | ❌           | **Bẫy hay gặp**: cần `X-Ray` end-to-end → `REST API`        |
| Integration    | Public HTTP endpoint                                                | ✅           | ✅           | Cả hai                                                                   |
| Integration    | `AWS Lambda`                                                      | ✅           | ✅           | Cả hai                                                                   |
| Integration    | AWS services (`SQS`, `SNS`, `DynamoDB`, `Step Functions`…) | ✅           | ✅           | Cả hai (`HTTP API` gọi là "AWS service integration")                 |
| Integration    | Private integration với**NLB**                               | ✅           | ✅           | Cả hai                                                                   |
| Integration    | Private integration với**ALB**                               | ✅           | ✅           | Cả hai                                                                   |
| Integration    | Private integration với`AWS Cloud Map`                           | ❌           | ✅           | Ngoại lệ đi ngược chiều#3 — service discovery (`ECS`)            |
| Integration    | **Mock integration**                                          | ✅           | ❌           | Trả response cố định / CORS preflight thủ công →`REST API`       |
| Integration    | Response streaming                                                  | ✅           | ❌           | Stream response dài (LLM, file) →`REST API`                           |

### C. Ra quyết định nhanh theo từ khoá trong đề

| Từ khoá trong đề                                                                  | Chọn             |
| ------------------------------------------------------------------------------------- | ----------------- |
| "lowest cost", "cost-effective", "lower latency", "simple proxy to Lambda"            | `HTTP API`      |
| "`JWT` / `OIDC` / OAuth2 authorizer", "`Cloud Map` / `ECS` service discovery" | `HTTP API`      |
| "`API keys`", "usage plan", "throttle per client", "quota cho partner"              | `REST API`      |
| "`AWS WAF`", "resource policy", "private API endpoint trong `VPC`"                | `REST API`      |
| "caching", "request validation", "`VTL` mapping", "Mock", "canary"                  | `REST API`      |
| "`X-Ray`", "execution logs", "log qua `Firehose`"                                 | `REST API`      |
| "two-way communication", "realtime chat", "server push"                               | `WebSocket API` |

> 💡 **Quy tắc chốt:** mặc định chọn **`HTTP API`** (rẻ + nhanh). Chỉ chuyển sang **`REST API`** khi đề nêu **một** trong các từ khoá cột `REST API` ở trên.

## 🧠 MẸO GHI NHỚ (Memory Hook)

<!-- TODO(human): viết memory hook của riêng bạn cho phần này -->

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Choose between REST APIs and HTTP APIs

REST APIs and HTTP APIs are both RESTful API products. REST APIs support more features than HTTP APIs, while HTTP APIs are designed with minimal features so that they can be offered at a lower price. Choose REST APIs if you need features such as API keys, per-client throttling, request validation, AWS WAF integration, or private API endpoints. Choose HTTP APIs if you don't need the features included with REST APIs.

## Endpoint type

The endpoint type refers to the endpoint that API Gateway creates for your API.

| Endpoint types | REST API | HTTP API |
| -------------- | -------- | -------- |
| Edge-optimized | ✅ Yes   | ❌ No    |
| Regional       | ✅ Yes   | ✅ Yes   |
| Private        | ✅ Yes   | ❌ No    |

## Security

| Security features                       | REST API | HTTP API |
| --------------------------------------- | -------- | -------- |
| Mutual TLS authentication               | ✅ Yes   | ✅ Yes   |
| Certificates for backend authentication | ✅ Yes   | ❌ No    |
| AWS WAF                                 | ✅ Yes   | ❌ No    |

## Authorization

| Authorization options                            | REST API | HTTP API |
| ------------------------------------------------ | -------- | -------- |
| IAM                                              | ✅ Yes   | ✅ Yes   |
| Resource policies                                | ✅ Yes   | ❌ No    |
| Amazon Cognito                                   | ✅ Yes   | ✅ Yes¹ |
| Custom authorization with an AWS Lambda function | ✅ Yes   | ✅ Yes   |
| JSON Web Token (JWT)²                           | ❌ No    | ✅ Yes   |

¹ You can use Amazon Cognito with a JWT authorizer.
² You can use a Lambda authorizer to validate JWTs for REST APIs.

## API management

Choose REST APIs if you need API management capabilities such as API keys and per-client rate limiting.

| Features                    | REST API | HTTP API |
| --------------------------- | -------- | -------- |
| Custom domains              | ✅ Yes   | ✅ Yes   |
| API keys                    | ✅ Yes   | ❌ No    |
| Per-client rate limiting    | ✅ Yes   | ❌ No    |
| Per-client usage throttling | ✅ Yes   | ❌ No    |
| Developer portal            | ✅ Yes   | ❌ No    |

## Development

| Features                         | REST API | HTTP API |
| -------------------------------- | -------- | -------- |
| CORS configuration               | ✅ Yes   | ✅ Yes   |
| Test invocations                 | ✅ Yes   | ❌ No    |
| Caching                          | ✅ Yes   | ❌ No    |
| User-controlled deployments      | ✅ Yes   | ✅ Yes   |
| Automatic deployments            | ❌ No    | ✅ Yes   |
| Custom gateway responses         | ✅ Yes   | ❌ No    |
| Canary release deployments       | ✅ Yes   | ❌ No    |
| Request validation               | ✅ Yes   | ❌ No    |
| Request parameter transformation | ✅ Yes   | ✅ Yes   |
| Request body transformation      | ✅ Yes   | ❌ No    |

## Monitoring

| Feature                             | REST API | HTTP API |
| ----------------------------------- | -------- | -------- |
| Amazon CloudWatch metrics           | ✅ Yes   | ✅ Yes   |
| Access logs to CloudWatch Logs      | ✅ Yes   | ✅ Yes   |
| Access logs to Amazon Data Firehose | ✅ Yes   | ❌ No    |
| Execution logs                      | ✅ Yes   | ❌ No    |
| AWS X-Ray tracing                   | ✅ Yes   | ❌ No    |

## Integrations

| Feature                                              | REST API | HTTP API |
| ---------------------------------------------------- | -------- | -------- |
| Public HTTP endpoints                                | ✅ Yes   | ✅ Yes   |
| AWS services                                         | ✅ Yes   | ✅ Yes   |
| AWS Lambda functions                                 | ✅ Yes   | ✅ Yes   |
| Private integrations with Network Load Balancers     | ✅ Yes   | ✅ Yes   |
| Private integrations with Application Load Balancers | ✅ Yes   | ✅ Yes   |
| Private integrations with AWS Cloud Map              | ❌ No    | ✅ Yes   |
| Mock integrations                                    | ✅ Yes   | ❌ No    |
| Response streaming                                   | ✅ Yes   | ❌ No    |
