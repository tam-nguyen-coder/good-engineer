# Amazon SQS — Visibility timeout

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
> **Tuần:** 5 — Messaging + Step Functions + Caching · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Visibility timeout** = khoảng thời gian message bị **ẩn** khỏi consumer khác sau khi được nhận, để tránh 2 consumer xử lý cùng 1 message.
- Số liệu PHẢI NHỚ: **mặc định 30 giây**, **tối đa 12 giờ** (giới hạn 12h tính từ lần nhận đầu tiên — gia hạn KHÔNG reset lại 12h).
- Xử lý **lâu hơn** visibility timeout → message **tái xuất hiện** và có thể bị xử lý **trùng**. Dùng `ChangeMessageVisibility` để **gia hạn** (heartbeat) hoặc **rút ngắn**.
- Đặt `VisibilityTimeout = 0` qua `ChangeMessageVisibility` → **trả message về ngay** cho consumer khác (khi quyết định không xử lý nữa).
- **In-flight messages** (đã nhận nhưng chưa xóa): Standard queue giới hạn **~120.000**; vượt → lỗi `OverLimit` (với short polling) — long polling thì không trả lỗi, chỉ ngừng trả message mới cho tới khi giảm xuống dưới hạn.
- Message không được xóa (do lỗi/crash) → tự **visible trở lại** → không mất message; nếu lỗi lặp lại nhiều lần → dùng **Dead-Letter Queue (DLQ)**.
- Nếu tác vụ cần > 12 giờ → cân nhắc **`AWS Step Functions`** hoặc chia nhỏ tác vụ.

---

## 📄 Nội dung (trích từ tài liệu gốc)

When you receive a message from an Amazon SQS queue, it remains in the queue but becomes temporarily invisible to other consumers. This invisibility is controlled by the **visibility timeout**, which ensures that other consumers cannot process the same message while you are working on it. Amazon SQS offers two options for deleting messages after processing:

- **Manual deletion** – You explicitly delete messages using the `DeleteMessage` action.
- **Automatic deletion** – Supported in certain AWS SDKs, messages are automatically deleted upon successful processing, simplifying workflows.

### Visibility timeout use cases

- **Manage long-running tasks** – Set an appropriate visibility timeout for messages that require extended processing time. This ensures that other consumers don't pick up the same message while it's being processed, preventing duplicate work.
- **Implement retry mechanisms** – Extend the visibility timeout programmatically for tasks that fail to complete within the initial timeout. Combine with **Dead-Letter Queues (DLQs)** to manage persistent failures.
- **Coordinate distributed systems** – Set visibility timeouts that align with your expected processing times for different components to maintain consistency and prevent race conditions.
- **Optimize resource utilization** – By setting appropriate timeouts, you can ensure that messages are processed efficiently without tying up resources unnecessarily.

### Setting and adjusting the visibility timeout

The visibility timeout starts as soon as a message is delivered to you. During this period, you're expected to process and delete the message. If you don't delete it before the timeout expires, the message becomes visible again in the queue and can be retrieved by another consumer. The **default visibility timeout for a queue is 30 seconds**, but you can adjust this to match the time your application needs. You can also set a specific visibility timeout for individual messages without changing the queue's overall setting. Use the `ChangeMessageVisibility` action to programmatically extend or shorten the timeout as needed.

### In flight messages and quotas

In-flight messages are messages that have been received by a consumer but not yet deleted. For **standard queues**, there's a limit of approximately **120,000 in-flight messages**, depending on queue traffic and message backlog. If you reach this limit, Amazon SQS returns an `OverLimit` error. For **FIFO queues**, limits depend on active message groups.

- **When using short polling** – If this limit is reached, Amazon SQS returns an `OverLimit` error; no additional messages can be received until some in-flight messages are deleted.
- **When using long polling** – Amazon SQS does not return an error when the in-flight message limit is reached. Instead, it will not return any new messages until the number of in-flight messages drops below the limit.

To manage in-flight messages effectively:

1. **Prompt deletion** – Delete messages after processing to reduce the in-flight count.
2. **Monitor with CloudWatch** – Set alarms for high in-flight counts.
3. **Distribute load** – Use additional queues or consumers to balance load.
4. **Request a quota increase** – Submit a request to AWS Support if higher limits are required.

### Understanding visibility timeout in standard and FIFO queues

In both standard and FIFO queues, the visibility timeout helps prevent multiple consumers from processing the same message simultaneously. However, due to the **at-least-once delivery** model of Amazon SQS, there's no absolute guarantee that a message won't be delivered more than once during the visibility timeout period.

- **Standard queues** – The visibility timeout prevents multiple consumers from processing the same message at the same time, but at-least-once delivery means a message may still be delivered more than once within the period.
- **FIFO queues** – Messages with the same **message group ID** are processed in strict sequence. When a message with a message group ID is in-flight, subsequent messages in that group are not made available until the in-flight message is either deleted or the visibility timeout expires. This doesn't "lock" the group indefinitely — each message is processed in sequence.

### Handling failures

If you don't process and delete a message before the visibility timeout expires — due to application errors, crashes, or connectivity problems — the message becomes visible again in the queue and can be retrieved for another processing attempt. This ensures messages aren't lost even if the initial processing fails. However, setting the visibility timeout too high can delay the reappearance of unprocessed messages, slowing down retries.

### Changing and terminating visibility timeout

- **Changing the timeout** – Adjust the visibility timeout dynamically using `ChangeMessageVisibility` to extend or reduce timeout durations.
- **Terminating the timeout** – If you decide not to process a received message, terminate its visibility timeout by setting `VisibilityTimeout` to **0 seconds** through the `ChangeMessageVisibility` action. This immediately makes the message available for other consumers.

### Best practices

- **Setting and adjusting the timeout** – Start by matching the visibility timeout to the maximum time your application typically needs. If unsure, begin with a shorter timeout (e.g. 2 minutes) and extend as necessary. Implement a **heartbeat mechanism** to periodically extend the timeout.
- **Extending the timeout and handling the 12-Hour limit** – Use `ChangeMessageVisibility` to extend while processing. The visibility timeout has a **maximum limit of 12 hours** from when the message is first received. **Extending the timeout doesn't reset this 12-hour limit.** If processing requires more time, consider using **AWS Step Functions** or breaking the task into smaller steps.
- **Handling unprocessed messages** – Configure a **Dead-Letter Queue (DLQ)** so that messages that can't be processed after several retries are captured separately, preventing them from repeatedly circulating in the main queue.
