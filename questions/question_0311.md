# Question #311 - Topic 1

A company is using AWS to design a web application that will process insurance quotes. Users will request quotes from the application. Quotes must be separated by quote type, must be responded to within 24 hours, and must not get lost. The solution must maximize operational efficiency and must minimize maintenance. Which solution meets these requirements?

## Options

**A.** Create multiple Amazon Kinesis data streams based on the quote type. Configure the web application to send messages to the proper data stream. Configure each backend group of application servers to use the Kinesis Client Library (KCL) to pool messages from its own data stream.

**B.** Create an AWS Lambda function and an Amazon Simple Notification Service (Amazon SNS) topic for each quote type. Subscribe the Lambda function to its associated SNS topic. Configure the application to publish requests for quotes to the appropriate SNS topic.

**C.** Create a single Amazon Simple Notification Service (Amazon SNS) topic. Subscribe Amazon Simple Queue Service (Amazon SQS) queues to the SNS topic. Configure SNS message filtering to publish messages to the proper SQS queue based on the quote type. Configure each backend application server to use its own SQS queue.

**D.** Create multiple Amazon Kinesis Data Firehose delivery streams based on the quote type to deliver data streams to an Amazon OpenSearch Service cluster. Configure the application to send messages to the proper delivery stream. Configure each backend group of application servers to search for the messages from OpenSearch Service and process them accordingly.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web application xử lý insurance quotes. Cần phân loại theo type, respond trong 24h, không được mất messages.
- **Existing Resources:** (none specified, designing new)
- **Current Issue/Goal:** Decouple quote submission from processing, ensure no data loss, operational efficiency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `must not get lost` | Cần durable queue (SQS), không phải pub/sub không có persistence (SNS alone). |
| `separated by quote type` | Cần routing theo type → SNS message filtering + SQS queues riêng. |
| `responded to within 24 hours` | Không cần real-time processing → SQS polling đủ. |
| `minimize maintenance` | Managed services (SNS + SQS), không Kinesis/EC2. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Maximize operational efficiency, minimize maintenance
- **Constraints:** No data loss, separated by type, 24-hour SLA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- SNS fan-out: 1 SNS topic nhận tất cả quotes, filter theo type → publish tới SQS queue tương ứng.
- SQS queue persist messages → không bị mất (durable).
- Backend servers poll SQS queue riêng → mỗi server xử lý quote type của mình.
- SNS + SQS là managed services → maintenance thấp, operational efficiency cao.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Kinesis Data Streams dùng cho real-time streaming (seconds), không cần thiết cho 24h SLA. KCL phức tạp hơn SQS polling.

**❌ Đáp án B:**
- SNS + Lambda: SNS không persist messages → nếu Lambda fails, message bị mất (trừ khi có DLQ). Không đáp ứng "must not get lost".

**❌ Đáp án D:**
- Kinesis Data Firehose → OpenSearch: không phải message queue. Firehose gom batch rồi deliver, backend phải query từ OpenSearch → phức tạp và không cần thiết.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Must not lose messages + need filtering → SNS + SQS (fan-out). Kinesis = real-time, SNS alone = no persistence."*
