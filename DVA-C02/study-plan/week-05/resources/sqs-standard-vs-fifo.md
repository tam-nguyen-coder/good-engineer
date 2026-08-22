# Amazon SQS — Standard vs FIFO queues

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-queue-types.html
> **Tuần:** 5 — Messaging + Step Functions + Caching · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `SQS` có **2 loại queue**: `Standard` và `FIFO`. Chọn theo yêu cầu về **throughput** hay **thứ tự**.
- `Standard`: **throughput gần như không giới hạn**, **at-least-once delivery** (message có thể bị **trùng**), **best-effort ordering** (không đảm bảo đúng thứ tự) → code phải **idempotent**.
- `FIFO`: **exactly-once processing** (không trùng) + **first-in-first-out** (giữ đúng thứ tự **trong mỗi message group**).
- Số liệu `FIFO` hay bị hỏi: **300 msg/s không batching** (300 API call/s mỗi method); với **batching** (mỗi batch 10 message) → **3.000 msg/s**; bật **high throughput mode** → tới **30.000 TPS**.
- `FIFO` chống trùng bằng `MessageDeduplicationId` hoặc **content-based deduplication**; song song hoá bằng cách chia nhiều **message group** (mỗi group giữ thứ tự riêng).
- Cả hai đều **durable**: lưu nhiều bản sao qua nhiều `Availability Zone`; đều có **visibility timeout**.
- Bẫy đề: cần "đúng thứ tự + không trùng" → chọn **FIFO**, KHÔNG phải Standard.

---

## 📄 Nội dung (trích từ tài liệu gốc)

Amazon SQS supports two types of queues: **standard queues** and **FIFO** queues. Use the following table to determine which queue best fits your needs.

### Standard queues

- **Unlimited throughput** – Standard queues support a very high, nearly unlimited number of API calls per second, per action (`SendMessage`, `ReceiveMessage`, or `DeleteMessage`). This high throughput makes them ideal for use cases that require processing large volumes of messages quickly, such as real-time data streaming or large-scale applications. While standard queues scale automatically with demand, it is essential to monitor usage patterns to ensure optimal performance, especially in regions with higher workloads.
- **At-least-once delivery** – Guaranteed at-least-once delivery, meaning that every message is delivered at least once, but in some cases, a message may be delivered more than once due to retries or network delays. You should design your application to handle potential duplicate messages by using **idempotent operations**, which ensure that processing the same message multiple times will not affect the system's state.
- **Best-effort ordering** – Provides best-effort ordering, meaning that while Amazon SQS attempts to deliver messages in the order they were sent, it does not guarantee this. In some cases, messages may arrive out of order, especially under conditions of high throughput or failure recovery. For applications where the order of message processing is crucial, you should handle reordering logic within the application or use FIFO queues for strict ordering guarantees.
- **Durability and redundancy** – Standard queues ensure high durability by storing multiple copies of each message across multiple AWS Availability Zones. This ensures that messages are not lost, even in the event of infrastructure failures.
- **Visibility timeout** – Amazon SQS allows you to configure a visibility timeout to control how long a message stays hidden after being received, ensuring that other consumers do not process the message until it has been fully handled or the timeout expires.

**Use standard queues** to send data between applications when throughput is crucial (e.g. decoupling live user requests from intensive background work, allocating tasks to multiple worker nodes, batching messages for future processing).

### FIFO queues

- **High throughput** – When you use **batching**, FIFO queues process up to **3,000 messages per second per API method** (`SendMessageBatch`, `ReceiveMessage`, or `DeleteMessageBatch`). This throughput relies on **300 API calls per second**, with each API call handling a batch of **10 messages**. By enabling **high throughput mode**, you can scale up to **30,000 transactions per second (TPS)** with relaxed ordering within message groups. Without batching, FIFO queues support up to **300 API calls per second per API method** (`SendMessage`, `ReceiveMessage`, or `DeleteMessage`). If you need more throughput, you can request a quota increase through the AWS Support Center.
- **Exactly-once processing** – FIFO queues deliver each message once and keep it available until you process and delete it. By using features like `SendMessage` (deduplication ID) or content-based deduplication, you prevent duplicate messages, even when retrying due to network issues or timeouts.
- **First-in-first-out delivery** – FIFO queues ensure that you receive messages in the order they are sent within each message group. By distributing messages across multiple groups, you can process them in parallel while still maintaining the order within each group.

**Use FIFO queues** to send data between applications when the **order of events is important** (e.g. ensuring commands are executed in the sent order, displaying the correct product price by sending price modifications in order, preventing a student from enrolling before registering).
