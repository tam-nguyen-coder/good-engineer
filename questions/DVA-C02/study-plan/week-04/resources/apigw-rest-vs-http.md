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

## 📄 Nội dung (trích từ tài liệu gốc)

# Choose between REST APIs and HTTP APIs

REST APIs and HTTP APIs are both RESTful API products. REST APIs support more features than HTTP APIs, while HTTP APIs are designed with minimal features so that they can be offered at a lower price. Choose REST APIs if you need features such as API keys, per-client throttling, request validation, AWS WAF integration, or private API endpoints. Choose HTTP APIs if you don't need the features included with REST APIs.

## Endpoint type

The endpoint type refers to the endpoint that API Gateway creates for your API.

| Endpoint types | REST API | HTTP API |
| --- | --- | --- |
| Edge-optimized | ✅ Yes | ❌ No |
| Regional | ✅ Yes | ✅ Yes |
| Private | ✅ Yes | ❌ No |

## Security

| Security features | REST API | HTTP API |
| --- | --- | --- |
| Mutual TLS authentication | ✅ Yes | ✅ Yes |
| Certificates for backend authentication | ✅ Yes | ❌ No |
| AWS WAF | ✅ Yes | ❌ No |

## Authorization

| Authorization options | REST API | HTTP API |
| --- | --- | --- |
| IAM | ✅ Yes | ✅ Yes |
| Resource policies | ✅ Yes | ❌ No |
| Amazon Cognito | ✅ Yes | ✅ Yes¹ |
| Custom authorization with an AWS Lambda function | ✅ Yes | ✅ Yes |
| JSON Web Token (JWT)² | ❌ No | ✅ Yes |

¹ You can use Amazon Cognito with a JWT authorizer.
² You can use a Lambda authorizer to validate JWTs for REST APIs.

## API management

Choose REST APIs if you need API management capabilities such as API keys and per-client rate limiting.

| Features | REST API | HTTP API |
| --- | --- | --- |
| Custom domains | ✅ Yes | ✅ Yes |
| API keys | ✅ Yes | ❌ No |
| Per-client rate limiting | ✅ Yes | ❌ No |
| Per-client usage throttling | ✅ Yes | ❌ No |
| Developer portal | ✅ Yes | ❌ No |

## Development

| Features | REST API | HTTP API |
| --- | --- | --- |
| CORS configuration | ✅ Yes | ✅ Yes |
| Test invocations | ✅ Yes | ❌ No |
| Caching | ✅ Yes | ❌ No |
| User-controlled deployments | ✅ Yes | ✅ Yes |
| Automatic deployments | ❌ No | ✅ Yes |
| Custom gateway responses | ✅ Yes | ❌ No |
| Canary release deployments | ✅ Yes | ❌ No |
| Request validation | ✅ Yes | ❌ No |
| Request parameter transformation | ✅ Yes | ✅ Yes |
| Request body transformation | ✅ Yes | ❌ No |

## Monitoring

| Feature | REST API | HTTP API |
| --- | --- | --- |
| Amazon CloudWatch metrics | ✅ Yes | ✅ Yes |
| Access logs to CloudWatch Logs | ✅ Yes | ✅ Yes |
| Access logs to Amazon Data Firehose | ✅ Yes | ❌ No |
| Execution logs | ✅ Yes | ❌ No |
| AWS X-Ray tracing | ✅ Yes | ❌ No |

## Integrations

| Feature | REST API | HTTP API |
| --- | --- | --- |
| Public HTTP endpoints | ✅ Yes | ✅ Yes |
| AWS services | ✅ Yes | ✅ Yes |
| AWS Lambda functions | ✅ Yes | ✅ Yes |
| Private integrations with Network Load Balancers | ✅ Yes | ✅ Yes |
| Private integrations with Application Load Balancers | ✅ Yes | ✅ Yes |
| Private integrations with AWS Cloud Map | ❌ No | ✅ Yes |
| Mock integrations | ✅ Yes | ❌ No |
| Response streaming | ✅ Yes | ❌ No |
