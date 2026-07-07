# Amazon SQS — Short polling và Long polling

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html
> **Tuần:** 5 — Messaging + Step Functions + Caching · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Short polling (mặc định):** query **một tập con** server → trả về **ngay lập tức** kể cả khi không có message → nhiều **empty response** hơn, tốn request/chi phí hơn.
- **Long polling:** query **TẤT CẢ** server, **chờ** tới khi có ít nhất 1 message rồi mới trả về → **giảm empty response** và **giảm chi phí**. Đây là câu trả lời kinh điển cho "làm sao giảm chi phí/empty response khi poll SQS".
- Số PHẢI NHỚ: **long polling wait time tối đa = 20 giây** (`WaitTimeSeconds`).
- Kích hoạt long polling: đặt `WaitTimeSeconds > 0` trên request `ReceiveMessage`, HOẶC đặt thuộc tính `ReceiveMessageWaitTimeSeconds > 0` trên queue.
- Short polling xảy ra khi `WaitTimeSeconds = 0` (do request đặt 0, hoặc queue attribute = 0 và request không đặt).
- Long polling còn giảm **false empty response** (có message nhưng không được trả về) vì query toàn bộ server thay vì tập con.

---

## 📄 Nội dung (trích từ tài liệu gốc)

Amazon SQS offers short and long polling options for receiving messages from a queue. Consider your application's requirements for responsiveness and cost efficiency when choosing between these two polling options:

- **Short polling** (default) – The `ReceiveMessage` request queries a **subset of servers** (based on a weighted random distribution) to find available messages and sends an **immediate response**, even if no messages are found.
- **Long polling** – `ReceiveMessage` queries **all servers** for messages, sending a response once at least one message is available, up to the specified maximum. An **empty response is sent only if the polling wait time expires**. This option can reduce the number of empty responses and potentially lower costs.

### Consuming messages using short polling

When you consume messages from a queue (FIFO or standard) using short polling, Amazon SQS samples a **subset of its servers** (based on a weighted random distribution) and returns messages from only those servers. Thus, a particular `ReceiveMessage` request might not return all of your messages. However, if you have fewer than **1,000 messages** in your queue, a subsequent request will return your messages. If you keep consuming from your queues, Amazon SQS samples all of its servers, and you receive all of your messages.

The short-polling behavior: after a receive request, Amazon SQS samples several of its servers and returns messages from these servers. Some messages may not be returned for this request but are returned for a subsequent request.

### Consuming messages using long polling

When the wait time for the `ReceiveMessage` API action is **greater than 0**, *long polling* is in effect. The **maximum long polling wait time is 20 seconds**. Long polling helps reduce the cost of using Amazon SQS by reducing the number of **empty responses** (when there are no messages available for a `ReceiveMessage` request) and **false empty responses** (when messages are available but aren't included in a response).

Long polling offers the following benefits:

- **Reduce empty responses** by allowing Amazon SQS to wait until a message is available in a queue before sending a response. Unless the connection times out, the response contains at least one of the available messages, up to the maximum number specified. In rare cases, you might receive empty responses even when a queue still contains messages, especially if you specify a low value for the `WaitTimeSeconds` parameter.
- **Reduce false empty responses** by querying all — rather than a subset of — Amazon SQS servers.
- **Return messages as soon as they become available.**

### Differences between long and short polling

Short polling occurs when the `WaitTimeSeconds` parameter of a `ReceiveMessage` request is set to `0` in one of two ways:

- The `ReceiveMessage` call sets `WaitTimeSeconds` to `0`.
- The `ReceiveMessage` call doesn't set `WaitTimeSeconds`, but the queue attribute `ReceiveMessageWaitTimeSeconds` (via `SetQueueAttributes`) is set to `0`.
