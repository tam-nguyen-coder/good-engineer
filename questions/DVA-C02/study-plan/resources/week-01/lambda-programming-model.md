# Understanding the Lambda programming model

> **Nguồn (AWS official):** https://docs.aws.amazon.com/lambda/latest/dg/foundation-progmodel.html
> **Tuần:** 1 — SDK/CLI + `Lambda` cơ bản · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Programming model** = giao diện giữa code của bạn và hệ thống `Lambda`. Bạn khai báo **handler** (entry point) trong cấu hình function; runtime truyền vào **event** (dữ liệu invoke) và **context** (function name, request ID, ...).
- **Hai mô hình:** standard functions chạy tối đa **15 phút** · **Durable Functions** chạy tối đa **1 năm** (stateful, có `DurableContext` với `step()`, `wait()`, `waitForCallback()`, checkpoint/persistence tự động).
- **Initialization code** (khai báo NGOÀI handler) được **tái sử dụng** giữa các invoke vì class ở lại trong bộ nhớ → tạo **SDK client** ở init để tiết kiệm thời gian. Một instance có thể xử lý hàng nghìn request.
- **`/tmp`**: local storage tạm, dùng chung được giữa nhiều invocation (transient cache).
- **Logging tự động**: runtime bắt output của function và gửi tới **`CloudWatch Logs`**; log cả lúc invocation start/end + report log (request ID, billed duration, init duration, ...). Log có thể mất do throttling hoặc khi instance bị dừng (chịu CloudWatch Logs quotas).
- **X-Ray:** khi bật, runtime ghi subsegment riêng cho **initialization** và **execution**.
- **Stateless & scale:** `Lambda` scale bằng cách chạy thêm instance khi demand tăng → request có thể xử lý **out of order / concurrently**; **đừng phụ thuộc instance sống lâu**, lưu state ở nơi khác (`S3`, `DynamoDB`).
- Nếu function throw error, runtime trả error đó về cho invoker.

---

## 📄 Nội dung (trích từ tài liệu gốc)

Lambda offers two programming models: standard functions that run up to 15 minutes, and Durable Functions that can run up to one year. While both share core concepts, Durable Functions add capabilities for long-running, stateful workflows.

Lambda provides a programming model that is common to all of the runtimes. The programming model defines the interface between your code and the Lambda system. You tell Lambda the entry point to your function by defining a *handler* in the function configuration. The runtime passes in objects to the handler that contain the invocation *event* and the *context*, such as the function name and request ID.

**For Durable Functions, the handler also receives a DurableContext object that provides:**
- Checkpointing capabilities through `step()`
- Wait state management through `wait()` and `waitForCallback()`
- Automatic state persistence between invocations

When the handler finishes processing the first event, the runtime sends it another. For Durable Functions, the handler can pause execution between steps, and Lambda will automatically save and restore state when the function resumes. **The function's class stays in memory, so clients and variables that are declared outside of the handler method in *initialization code* can be reused.** To save processing time on subsequent events, create reusable resources like AWS SDK clients during initialization. Once initialized, each instance of your function can process thousands of requests.

Your function also has access to local storage in the **`/tmp` directory**, a transient cache that can be used for multiple invocations.

When **AWS X-Ray tracing** is enabled, the runtime records separate subsegments for **initialization** and **execution**.

The runtime captures logging output from your function and sends it to Amazon CloudWatch Logs. In addition to logging your function's output, the runtime also logs entries when function invocation starts and ends. This includes a **report log with the request ID, billed duration, initialization duration, and other details.** If your function throws an error, the runtime returns that error to the invoker.

> **Note:** Logging is subject to CloudWatch Logs quotas. Log data can be lost due to throttling or, in some cases, when an instance of your function is stopped.

**Key differences for Durable Functions:**
- State is automatically persisted between steps
- Functions can pause execution without consuming resources
- Steps are automatically retried on failure
- Progress is tracked through checkpoints

Lambda scales your function by running additional instances of it as demand increases, and by stopping instances as demand decreases. This model leads to variations in application architecture:
- Unless noted otherwise, incoming requests might be processed **out of order or concurrently**.
- Do not rely on instances of your function being long lived; instead store your application's state elsewhere.
- Use local storage and class-level objects to increase performance, but keep to a minimum the size of your deployment package and the amount of data transferred onto the execution environment.

For a hands-on introduction in your preferred language, see the runtime chapters: Node.js, Python, Ruby, Java, Go, C#, PowerShell.
