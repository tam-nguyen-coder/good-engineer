# Question #255 - Topic 1

A company has an ecommerce checkout workflow that writes an order to a database and calls a service to process the payment. Users are experiencing timeouts during the checkout process. When users resubmit the checkout form, multiple unique orders are created for the same desired transaction. How should a solutions architect refactor this workflow to prevent the creation of multiple orders?

## Options

**A.** Configure the web application to send an order message to Amazon Kinesis Data Firehose. Set the payment service to retrieve the message from Kinesis Data Firehose and process the order.

**B.** Create a rule in AWS CloudTrail to invoke an AWS Lambda function based on the logged application path request. Use Lambda to query the database, call the payment service, and pass in the order information.

**C.** Store the order in the database. Send a message that includes the order number to Amazon Simple Notification Service (Amazon SNS). Set the payment service to poll Amazon SNS, retrieve the message, and process the order.

**D.** Store the order in the database. Send a message that includes the order number to an Amazon Simple Queue Service (Amazon SQS) FIFO queue. Set the payment service to retrieve the message and process the order. Delete the message from the queue.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce checkout, timeout → user resubmits → multiple orders. Need idempotency.
- **Existing Resources:** Order database, payment service.
- **Current Issue/Goal:** Prevent duplicate orders.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `multiple unique orders` | **Idempotency** needed |
| `prevent the creation of multiple orders` | **SQS FIFO** — exactly-once processing |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Messaging / Idempotency
- **Constraints:** No duplicate processing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **SQS FIFO queue** — guarantee exactly-once processing (message deduplication).
- Order number dùng làm deduplication ID → cùng order không bị xử lý 2 lần.
- Payment service consume message, process, delete → ko có duplicate.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Kinesis Firehose — cho data streaming, không message queuing, không dedup.

**❌ Đáp án B:**
- CloudTrail + Lambda — CloudTrail là audit trail, không phải message queue.

**❌ Đáp án C:**
- SNS — push model, có thể gửi duplicate, subscriber không thể poll.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS FIFO = exactly-once, dedup. Standard SQS/SNS = at-least-once (potential duplicates)"*
