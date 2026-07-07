# Lambda quotas (giới hạn & hạn mức)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html
> **Tuần:** 2 — `Lambda` nâng cao · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Concurrent executions**: mặc định **1,000** (soft, xin tăng lên hàng chục nghìn); áp dụng **theo Region**.
- **Memory**: **128 MB → 10,240 MB** (bước 1 MB). Tại **1,769 MB** = tương đương **1 vCPU** (CPU cấp theo tỷ lệ RAM).
- **Timeout**: tối đa **900 giây (15 phút)**.
- **Environment variables**: tổng **4 KB** (tất cả biến gộp lại).
- **Layers**: **5 layer/function**.
- **Payload** (⚠️ số mới): sync **6 MB** (request & response); **200 MB** cho streamed response; **async 1 MB**. (Lưu ý: nhiều tài liệu/đề cũ ghi async = 256 KB — bảng quotas hiện hành ghi 1 MB.)
- **Deployment package**: **50 MB** zip (upload qua API/SDK hoặc console) · **250 MB** giải nén (gồm layers + custom runtime) · **10 GB** container image (uncompressed).
- **`/tmp` ephemeral storage**: **512 MB → 10,240 MB** (bước 1 MB).
- **Concurrency scaling limit**: mỗi function **1,000 execution environments mỗi 10 giây**.
- **Storage cho code (.zip + layers) qua Lambda-managed storage**: **300 GB** (unzipped, không tăng được — dùng self-managed S3 storage nếu cần thêm).
- **Resource-based policy**: **20 KB**. **File descriptors / threads**: **1,024**. **Test events console**: **10**.
- **ENI per VPC**: **500** (dùng chung với EFS...).

---

## 📄 Nội dung (trích từ tài liệu gốc)

**Important:** New AWS accounts have reduced concurrency and memory quotas for Lambda Functions and Lambda MicroVMs. AWS raises these quotas automatically based on your usage.

AWS Lambda is designed to scale rapidly to meet demand. Lambda is designed for short-lived compute tasks that do not retain or rely upon state between invocations. Code can run for up to 15 minutes in a single invocation and a single function can use up to 10,240 MB of memory.

Service quotas consist of hard limits, which you cannot change, and soft limits, which you can request increases for.

## Compute and storage

Quotas for concurrent executions and storage apply per AWS Region. Elastic network interface (ENI) quotas apply per virtual private cloud (VPC), regardless of Region. The following quotas can be increased from their default values.

| Resource | Default quota | Can be increased up to |
| --- | --- | --- |
| Concurrent executions | 1,000 | Tens of thousands |
| Storage for uploaded functions (.zip file archives) and layers using Lambda-managed storage. Each function version and layer version consumes storage. | 300 GB (unzipped) | Not increasable. Use self-managed S3 code storage for storage beyond this limit. |
| Storage for functions defined as container images (stored in Amazon ECR). | See Amazon ECR service quotas. |   |
| Elastic network interfaces per virtual private cloud (VPC). This quota is shared with other services, such as Amazon EFS. | 500 | Thousands |
| Maximum running durable executions | 1,000,000 | Millions |

## Function configuration, deployment, and execution

The following quotas apply to function configuration, deployment, and execution. Except as noted, they can't be changed.

**Note:** The Lambda documentation, log messages, and console use the abbreviation MB (rather than MiB) to refer to 1,024 KB.

| Resource | Quota |
| --- | --- |
| Function memory allocation | 128 MB to 10,240 MB, in 1-MB increments. Lambda allocates CPU power in proportion to the amount of memory configured. At 1,769 MB, a function has the equivalent of one vCPU. |
| Function timeout | 900 seconds (15 minutes) |
| Function environment variables | 4 KB, for all environment variables associated with the function, in aggregate |
| Function resource-based policy | 20 KB |
| Function layers | 5 layers |
| Function concurrency scaling limit | For each function, 1,000 execution environments every 10 seconds |
| Invocation payload (request and response) | 6 MB each for request and response (synchronous); 200 MB for each streamed response (synchronous); 1 MB (asynchronous); 1 MB for the total combined size of request line and header values |
| Bandwidth for streamed responses | Uncapped for the first 6 MB of your function's response; for responses larger than 6 MB, 2MBps for the remainder of the response |
| Deployment package (.zip file archive) size | 50 MB (zipped, when uploaded through the Lambda API or SDKs). Upload larger files with Amazon S3. 50 MB (when uploaded through the Lambda console). 250 MB — the maximum size of the contents of a deployment package, including layers and custom runtimes (unzipped). |
| Container image settings size | 16 KB |
| Container image code package size | 10 GB (maximum uncompressed image size, including all layers) |
| Test events (console editor) | 10 |
| `/tmp` directory storage | Between 512 MB and 10,240 MB, in 1-MB increments |
| File descriptors | 1,024 (Lambda Managed Instances use a higher file descriptor limit of 4,096) |
| Execution processes/threads | 1,024 |
| Maximum number of durable operations per durable execution | 3,000 |
| Durable execution storage written in megabytes | 100 MB (cumulative payload size persisted by durable functions per execution) |

## Lambda API requests

| Resource | Quota |
| --- | --- |
| Invocation requests per function per Region (synchronous) | Each instance of your execution environment can serve up to 10 requests per second. In other words, the total invocation limit is 10 times your concurrency limit. |
| Invocation requests per function per Region (asynchronous) | Each instance of your execution environment can serve an unlimited number of requests. The total invocation limit is based only on concurrency available to your function. |
| Invocation requests per function version or alias (requests per second) | 10 x allocated provisioned concurrency (applies only to functions that use provisioned concurrency). |
| GetFunction API requests | 100 requests per second. Cannot be increased. |
| GetPolicy API requests | 15 requests per second. Cannot be increased. |
| Remainder of the control plane API requests (excludes invocation, GetFunction, and GetPolicy requests) | 15 requests per second across all APIs (not per API). Cannot be increased. |

(Trang gốc còn liệt kê nhiều API rate limit cho Durable Executions: CheckpointDurableExecution 1,000 rps, GetDurableExecution 30 rps, GetDurableExecutionState 1,000 rps, v.v.)

## Lambda MicroVMs

Lambda MicroVMs support the ARM64 (AWS Graviton) architecture.

### Compute and storage

| Resource | Default quota | Adjustable |
| --- | --- | --- |
| Memory allocated across all MicroVMs (per account, per Region) | 400 GB (e.g. 200 MicroVMs at 2 GB each or 400 at 1 GB each). 1,024 GB in US East (N. Virginia), US West (Oregon), US East (Ohio), and Asia Pacific (Tokyo). Burstable up to four times this quota. | Yes |
| Maximum execution duration per MicroVM | 8 hours (28,800 seconds) | No |

### Images and versions

| Resource | Default quota | Adjustable |
| --- | --- | --- |
| MicroVM images per account per Region | 100 | Yes |
| Versions per MicroVM image | 50 | Yes |
| Concurrent image builds (per account, per Region) | 5 (10 in N. Virginia, Oregon, Ohio, Tokyo) | Yes |

## Other services

Quotas for other services (IAM, CloudFront/Lambda@Edge, Amazon VPC) can impact your Lambda functions. For example, API Gateway has a default throttle limit of 10,000 requests per second, whereas Lambda has a default concurrency limit of 1,000. Due to this mismatch, it's possible to have more incoming requests from API Gateway than Lambda can handle. You can resolve this by requesting a Lambda concurrency limit increase.
