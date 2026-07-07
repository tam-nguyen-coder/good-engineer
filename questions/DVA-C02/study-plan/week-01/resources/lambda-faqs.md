# AWS Lambda FAQs

> **Nguồn (AWS official):** https://aws.amazon.com/lambda/faqs/
> **Tuần:** 1 — SDK/CLI + `Lambda` cơ bản · **Loại:** AWS FAQ
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Memory:** cấu hình từ **128 MB đến 10,240 MB**; CPU (và tài nguyên khác) **tỉ lệ thuận** với memory (256 MB ≈ gấp đôi CPU của 128 MB).
- **Timeout:** tối đa **15 phút / execution** (đặt được từ 1 giây đến 15 phút).
- **Runtimes native:** Java, Go, PowerShell, Node.js, C#, Python, Ruby + **Runtime API** cho ngôn ngữ khác (custom runtime).
- **Deploy:** `.zip` archive (upload qua console/CLI/SDK) hoặc **container image** — cùng execution environment.
- **Truy cập service khác:** cấp quyền cho function qua **IAM role** (Lambda assume role khi chạy). `S3` gọi Lambda → tự tạo **resource policy**; poll `DynamoDB`/`Kinesis` stream → dùng **function role**; `SQS` → role hoặc resource policy (cái nào chặt hơn thì áp dụng).
- **Concurrency:** default safety throttle **per account per region**; set reserved concurrency cho từng function. Vượt limit: invoke **đồng bộ → lỗi 429 (throttling)**; **bất đồng bộ → absorb ~15-30 phút** rồi mới reject.
- **Scale rate:** mỗi function invoke đồng bộ scale tới **1000 concurrent executions mỗi 10 giây**, độc lập giữa các function.
- **Retry khi lỗi:** đồng bộ → trả exception; **bất đồng bộ → retry ít nhất 3 lần**, hết retry policy thì đưa vào **DLQ** (SQS queue hoặc SNS topic); stream (Kinesis/DynamoDB) → retry đến khi thành công hoặc data hết hạn (giữ tối thiểu 24h).
- **State:** function phải **stateless** (để scale nhanh); lưu state ở `S3`/`DynamoDB`. Env vars mã hoá secret bằng **KMS** (client-side).
- **SnapStart:** giảm cold start (Java 11+, Python 3.12+, .NET 8+); **không dùng chung với Provisioned Concurrency**. **Provisioned Concurrency:** giữ function initialized, phản hồi double-digit ms — dùng cho latency-sensitive.
- **Durable functions:** vượt 15 phút bằng suspend/resume, execution timeout tới **1 năm**, retention tới **90 ngày**, mỗi checkpoint tối đa **256 KB**; VPC/Layers/Code Signing (chỉ ZIP) là các fact phụ hay xuất hiện.

---

## 📄 Nội dung (trích từ tài liệu gốc)

## General

**Q: What events can trigger an AWS Lambda function?**
See the documentation for a complete list of event sources.

**Q: What languages does AWS Lambda support?**
AWS Lambda natively supports Java, Go, PowerShell, Node.js, C#, Python, and Ruby code, and provides a Runtime API which allows you to use any additional programming languages to author your functions.

**Q: How does AWS Lambda isolate my code?**
Each AWS Lambda function runs in its own isolated environment, with its own resources and file system view. AWS Lambda uses the same techniques as Amazon EC2 to provide security and separation at the infrastructure and execution levels.

**Q: How does AWS Lambda protect my data and code?**
AWS Lambda stores code in Amazon S3 and encrypts it at rest, and performs additional integrity checks while your code is in use. For sensitive information such as database passwords, use client-side encryption with AWS KMS and store resulting values as ciphertext in environment variables.

**Q: Why must AWS Lambda functions be stateless?**
Keeping functions stateless enables AWS Lambda to rapidly launch as many copies of the function as needed to scale to the rate of incoming events. While the programming model is stateless, your code can access stateful data by calling other services such as Amazon S3 or Amazon DynamoDB.

**Q: Does AWS Lambda support environment variables?**
Yes. You can create and modify environment variables from the Console, CLI, or SDKs.

**Q: Can I store sensitive information in environment variables?**
For sensitive information, use client-side encryption with AWS KMS and store the resulting values as ciphertext in your environment variable. Include logic in your function code to decrypt these values.

**Q: Can I share code across functions?**
Yes, you can package any code (frameworks, SDKs, libraries) as a **Lambda Layer** and share them across multiple functions.

**Q: How do I monitor an AWS Lambda function?**
AWS Lambda automatically monitors functions, reporting real-time metrics through Amazon CloudWatch, including total requests, account-level and function-level concurrency usage, latency, error rates, and throttled requests.

**Q: How are compute resources assigned to an AWS Lambda function?**
You choose the amount of memory for your function, and are allocated proportional CPU power and other resources. For example, choosing 256MB allocates approximately twice as much CPU as 128MB and half as much as 512MB. **You can set your memory from 128MB to 10,240MB.**

**Q: How long can an AWS Lambda function execute?**
AWS Lambda functions can be configured to run **up to 15 minutes per execution**. You can set the timeout to any value between 1 second and 15 minutes.

**Q: How will I be charged for using AWS Lambda functions?**
AWS Lambda is priced on a pay-per-use basis.

**Q: Does AWS Lambda support versioning?**
Yes. By default, each function has a single, current version of the code. Clients can call a specific version or get the latest implementation.

**Q: How can I deploy my Lambda functions?**
Package and deploy functions as **.zip file archives** (upload via console, CLI, or SDKs) or as **container images**. Both methods provide the same execution environment, scaling, and operational simplicity.

## Using AWS Lambda to process AWS events

**Q: What is an event source?**
An AWS service or developer-created application that produces events that trigger a function. Some services publish events by invoking the function directly (e.g., Amazon S3). Lambda can also poll resources that do not publish events (e.g., pull records from an Amazon Kinesis stream or an Amazon SQS queue and execute a function for each message).

**Q: How can my application trigger an AWS Lambda function directly?**
Invoke a function using a custom event through Lambda's invoke API. Only the function owner or another AWS account the owner has granted permission can invoke the function.

**Q: How do I invoke an AWS Lambda function over HTTPS?**
Define a custom RESTful API using Amazon API Gateway. This gives you an endpoint that can respond to REST calls like GET, PUT, and POST.

## AWS Lambda SnapStart

**Q: What is AWS Lambda SnapStart?**
SnapStart can improve startup performance from several seconds to as low as sub-second. It snapshots your function's initialized memory (and disk) state and caches this snapshot for low-latency access; on subsequent invokes Lambda resumes from the pre-initialized snapshot instead of initializing from scratch.

**Q: How do I choose between Lambda SnapStart and Provisioned Concurrency (PC)?**
SnapStart reduces startup latency as a **best-effort optimization** and does not guarantee elimination of cold starts. If your application has strict latency requirements and requires double-digit millisecond startup times, use Provisioned Concurrency.

**Q: Which runtimes does Lambda SnapStart support?**
Java 11 (and newer), Python 3.12 (and newer), and .NET 8 (and newer).

**Q: Can I enable both Lambda SnapStart and PC on the same function?**
No. SnapStart and PC cannot be enabled at the same time on the same function.

**Q: Can I configure a Lambda SnapStart function with a VPC?**
Yes.

**Q: Will I be charged for Lambda SnapStart?**
Yes — for caching a snapshot over the period the function version is active (minimum 3 hours, then per millisecond), and each time Lambda resumes an execution environment by restoring your snapshot. SnapStart pricing does not apply to supported Java managed runtimes, which can only cache a snapshot for up to 14 days.

## Provisioned Concurrency

**Q: What is AWS Lambda Provisioned Concurrency?**
When enabled, Provisioned Concurrency keeps functions initialized and hyper-ready to respond in **double-digit milliseconds**.

**Q: How do I set up and manage Provisioned Concurrency?**
Configure via Console, Lambda API, CLI, and CloudFormation. Use Application Auto Scaling to configure schedules or auto-adjust the level in real time.

**Q: When should I use Provisioned Concurrency?**
Ideal for latency-sensitive applications: web/mobile backends, synchronously invoked APIs, and interactive microservices.

## Lambda@Edge

**Q: What is Lambda@Edge?**
Run code across AWS locations globally, responding to end-users at the lowest network latency. Upload Node.js or Python code and configure it to be triggered in response to Amazon CloudFront requests. Lambda@Edge supports **Node.js and Python** only.

**Q: When should I use Lambda@Edge?**
Optimized for latency-sensitive use cases where viewers are distributed globally and decisions can be made at the CloudFront edge (e.g., serve content based on location or client device).

## Scalability and availability

**Q: How available are AWS Lambda functions?**
Designed to use replication and redundancy for high availability. No maintenance windows or scheduled downtimes.

**Q: Do my functions remain available when I change code/configuration?**
Yes. When you update a function, there is a brief window (typically less than a minute) when requests could be served by either the old or new version.

**Q: Is there a limit to the number of functions I can execute at once?**
No, but AWS Lambda has a **default safety throttle for the number of concurrent executions per account per region.** You can control the maximum concurrent executions for individual functions (reserve a subset of account concurrency for critical functions, or cap traffic to downstream resources). Use Service Quotas to request a limit increase.

**Q: What happens if my account exceeds the default throttle limit on concurrent executions?**
Functions invoked **synchronously return a throttling error (429 error code).** Functions invoked **asynchronously can absorb reasonable bursts of traffic for approximately 15-30 minutes,** after which incoming events are rejected as throttled. For S3 events, rejected events may be retained and retried by S3 for 24 hours. Kinesis/DynamoDB stream events are retried until the function succeeds or the data expires (retained for 24 hours).

**Q: Are default maximum concurrent execution limits applied on a per function level?**
The default limit is applied at the **account level**, but you can also set limits on individual functions.

**Q: How quickly do my functions scale?**
Each synchronously invoked function can scale at a rate of **up to 1000 concurrent executions every 10 seconds.** The concurrency scaling limit is a function-level limit — each function scales independently.

**Q: What happens if my function fails while processing an event?**
Synchronous → responds with an exception. **Asynchronous → retried at least 3 times.** Kinesis/DynamoDB streams → retried until the function succeeds or the data expires (retained a minimum of 24 hours).

**Q: What happens if my function invocations exhaust the available policy?**
For asynchronous invocations, on exceeding the retry policy you can configure a **dead letter queue (DLQ)**; without a DLQ the event may be rejected. For stream-based invocations, the data would have already expired and is rejected.

**Q: What resources can I configure as a dead letter queue?**
An **Amazon SQS queue** or an **Amazon SNS topic**.

## Security and access control

**Q: How do I allow my function access to other AWS resources?**
You grant permissions using an **IAM role**. AWS Lambda assumes the role while executing your function.

**Q: How do I control which S3 buckets can call which functions?**
When you configure an S3 bucket to send messages to a function, a **resource policy rule** is created that grants access.

**Q: How do I control which DynamoDB table or Kinesis stream a function can poll?**
Managed through the **Lambda function role** — the role determines which resources Lambda can poll on its behalf.

**Q: How do I control which SQS queue a function can poll?**
Managed by the **Lambda function role** or a **resource policy** on the queue. If both are present, the more restrictive of the two permissions is applied.

**Q: How do I access resources in Amazon VPC from my function?**
Specify the subnet and security group in your function configuration. VPC-configured functions do not have internet access by default; use internet gateways (or NAT) for internet. By default functions communicate over IPv4 in a dual-stack VPC; you can configure IPv6.

**Q: What is Code Signing for AWS Lambda?**
Trust and integrity controls to verify only unaltered code from approved developers is deployed. Use AWS Signer to digitally sign artifacts. **Code Signing is only available for functions packaged as ZIP archives.** Signature checks at deployment: corrupt, mismatched, expired, and revoked signatures. No additional cost.

## Advanced monitoring capabilities

**Q: What advanced logging controls are supported?**
Natively capture Lambda function logs in **JSON structured format**, control **log level filtering** without code changes, and customize the CloudWatch **log group** Lambda sends logs to. No additional charge (standard CloudWatch Logs ingestion/storage applies).

**Q: What is CloudWatch Application Signals with Lambda?**
An APM solution providing pre-built dashboards, correlated traces, and dependency interactions — without manual instrumentation.

**Q: What is CloudWatch Live Tail with Lambda?**
Interactive real-time log streaming for developing/troubleshooting functions (speeds up the inner dev loop and reduces MTTR).

## AWS Lambda durable functions

**Q: When should I use durable functions vs AWS Step Functions?**
Use durable functions to build logic in Lambda's familiar programming model (local testing, IDE integration, preferred language). Use Step Functions for visual workflow design, cross-team visibility, 220+ native service integrations, or zero-maintenance infrastructure.

**Q: Which languages are supported?**
JavaScript, TypeScript, Python, and Java.

**Q: Can I build applications that run longer than 15 minutes?**
Yes. The per-invocation timeout remains 15 minutes, but durable functions can suspend and resume across multiple invocations. When invoked asynchronously, the **durable execution timeout can extend up to one year.** For on-demand functions, there are no compute charges during suspension.

**Q: How do execution timeout and retention period relate?**
Execution timeout (**up to 1 year**) governs how long an execution can run. Retention period (**up to 90 days**) governs how long history and checkpoint data are retained after a terminal state.

**Q: Will I be billed for compute while waiting?**
No — for on-demand functions, no compute charges during suspension.

**Q: Where is execution state stored and what are the size limits?**
In a fully managed internal state store. Each checkpointed operation (step or callback) can store **up to 256 KB** of returned data. Large payloads can be offloaded to S3/DynamoDB via custom serializers.

**Q: How does concurrency work with durable functions?**
They use the **same account-level concurrency pool** as standard functions. Concurrency slots are released during waits, so thousands of executions can wait without consuming concurrency.

## AWS Lambda MicroVMs

**Q: What is AWS Lambda MicroVMs?**
A serverless compute primitive combining VM-level isolation, near-instant launch/resume, and state persistence across interactions. Built on Firecracker.

**Q: When should I use Lambda MicroVMs?**
When your workload needs an isolated environment that starts near-instantly, preserves state across interactions (**up to 8 hours**), or requires privileged OS capabilities (dev environments, security testing, data analytics, CI/CD, AI coding assistants, agent sandboxes).

**Q: What can I run inside a Lambda MicroVM?**
Anything packaged as a container running on Amazon Linux 2023. Supports **up to 32 GB of memory and 16 vCPUs.**

**Q: How does suspend and resume work?**
Full memory and disk state is preserved for **up to 8 hours** (no compute charge while suspended); resume is near-instant via snapshotting.

**Q: What is the SLA for Lambda MicroVMs?**
Covered by the AWS Lambda SLA — Monthly Uptime Percentage of at least **99.5%** for instance-level availability.
