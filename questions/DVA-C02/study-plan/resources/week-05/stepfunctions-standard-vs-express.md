# AWS Step Functions — Standard vs Express workflows

> **Nguồn (AWS official):** https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html
> **Tuần:** 5 — Messaging + Step Functions + Caching · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- Khi tạo state machine phải chọn **Type**: `Standard` (mặc định) hoặc `Express`. **Type KHÔNG đổi được** sau khi tạo (immutable).
- **Standard:** chạy tới **1 năm**, **exactly-once**, phù hợp workflow dài/kiểm toán/**non-idempotent** (vd charge payment, start EMR). Tính phí theo **state transition**. Execution history giữ **90 ngày**.
- **Express:** chạy tối đa **5 phút**, **at-least-once** (async), phù hợp **high-volume / event-processing** (IoT, streaming, mobile backend), nên dùng cho action **idempotent**. Tính phí theo **số lần chạy + thời lượng + bộ nhớ**.
- Express có 2 kiểu: **Asynchronous** (at-least-once, không chờ kết quả, xem log ở `CloudWatch Logs`) và **Synchronous** (at-most-once, chờ tới khi hoàn tất rồi trả kết quả — dùng `StartSyncExecution`).
- Số hay hỏi: `StartSyncExecution` từ **console** hết hạn sau **60 giây**; muốn chạy đủ tới 5 phút phải gọi qua **SDK/CLI**.
- **Execution history:** Standard xem/replay được qua API + console (giữ 90 ngày, có thể giảm về 30 ngày qua quota request); Express **không** được Step Functions lưu history → phải bật **CloudWatch Logs**.
- **Service integration:** Express **KHÔNG hỗ trợ** `.sync` (Job-run) và `.waitForTaskToken` (Callback); **Distributed Map** và **Activities** chỉ Standard hỗ trợ.

---

## 📄 Nội dung (trích từ tài liệu gốc)

When you create a state machine, you must choose a **Type** of either *Standard* (default) or *Express*. You define both state machine types using the **Amazon States Language (ASL)**. Both can start in response to events, such as HTTP requests from Amazon API Gateway, IoT rules, and over 140 other event sources in Amazon EventBridge.

> **Workflow type is immutable** – The workflow type can **not** be updated after you create a state machine.

**Standard Workflows** are ideal for long-running (up to one year), durable, and auditable workflows. You can retrieve the full execution history using the Step Functions API for up to **90 days** after execution completes. Standard Workflows follow an **exactly-once** model, where tasks and states are never run more than once, unless you specified `Retry` behavior in ASL. This makes them suited to orchestrating **non-idempotent** actions, such as starting an Amazon EMR cluster or processing payments. Standard Workflow executions are billed according to the **number of state transitions** processed.

**Express Workflows** are ideal for high-volume, event-processing workloads such as IoT data ingestion, streaming data processing/transformation, and mobile application backends. They can run for up to **five minutes**. Express Workflows use an **at-least-once** model, so an execution could potentially run more than once. This makes them better suited for orchestrating **idempotent** actions, such as transforming input data to store in Amazon DynamoDB using a PUT action. Express Workflow executions are billed by **number of executions, total duration of execution, and memory consumed**.

### Comparison of Standard and Express workflow types

| Type / Category | Standard Workflows | Express Workflows (Synchronous and Asynchronous) |
| --- | --- | --- |
| **Maximum duration** | One year | Five minutes |
| **Supported state transition rate** | See quotas related to state throttling | No limit |
| **Pricing** | Priced by number of **state transitions** (counted each time a step completes) | Priced by number of **executions**, their **duration**, and **memory consumption** |
| **Execution history** | Listed/described with Step Functions APIs; visually debugged in console; also in CloudWatch Logs if logging enabled | Unlimited execution history within a 5-minute period; inspected in CloudWatch Logs or console **only if logging enabled** |
| **Execution semantics** | Exactly-once workflow execution | *Asynchronous:* At-least-once · *Synchronous:* At-most-once |
| **Service integrations** | Supports **all** service integrations and patterns | Supports all service integrations, but **NOT** Job-run (`.sync`) or Callback (`.waitForTaskToken`) patterns |
| **Distributed Map** | Supported | Not supported |
| **Activities** | Supported | Not supported |

### Synchronous and Asynchronous Express Workflows

- **Asynchronous Express Workflows** return confirmation that the workflow was started, but don't wait for completion. To get the result, you must poll **CloudWatch Logs**. Use when you don't require immediate response output. Started in response to an event, by a nested workflow, or via the `StartExecution` API.
- **Synchronous Express Workflows** start a workflow, **wait until it completes**, and then return the result. Used to orchestrate microservices without extra code for errors, retries, or parallel tasks. Invoked from Amazon API Gateway, AWS Lambda, or via `StartSyncExecution`.

> **Note:** If you run Express Workflows synchronously from the console, the `StartSyncExecution` request **expires after 60 seconds**. To run synchronously for up to five minutes, make the `StartSyncExecution` request using the AWS SDK or AWS CLI instead of the console. Synchronous Express execution API calls don't contribute to existing account capacity limits; Step Functions provides capacity on demand and automatically scales. Surges may be throttled until capacity is available.

### Execution guarantees

| Standard Workflows | Asynchronous Express Workflows | Synchronous Express Workflows |
| --- | --- | --- |
| Exactly-once workflow execution | At-least-once workflow execution | At-most-once workflow execution |
| Execution state internally **persists** between state transitions | Execution state **doesn't persist** between state transitions | Execution state **doesn't persist** between state transitions |
| Automatically returns an idempotent response on starting an execution with the same name as a currently-running workflow (new workflow doesn't start; exception thrown once current one completes) | Idempotency **not** automatically managed; starting multiple workflows with the same name results in concurrent executions | Idempotency **not** automatically managed; Step Functions waits and returns the result on completion; workflows don't restart if an exception occurs |
| Execution history data **removed after 90 days** (can reduce to 30 days via quota request); names reusable after removal | Execution history **not captured** by Step Functions; enable Amazon CloudWatch Logs | Execution history **not captured** by Step Functions; enable Amazon CloudWatch Logs |
