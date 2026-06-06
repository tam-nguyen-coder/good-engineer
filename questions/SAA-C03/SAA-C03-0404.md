# Question #404 - Topic 1

A company has deployed a serverless application that invokes an AWS Lambda function when new documents are uploaded to an Amazon S3 bucket. The application uses the Lambda function to process the documents. After a recent marketing campaign, the company noticed that the application did not process many of the documents. What should a solutions architect do to improve the architecture of this application?

## Options

**A.** Set the Lambda function's runtime timeout value to 15 minutes.

**B.** Configure an S3 bucket replication policy. Stage the documents in the S3 bucket for later processing.

**C.** Deploy an additional Lambda function. Load balance the processing of the documents across the two Lambda functions.

**D.** Create an Amazon Simple Queue Service (Amazon SQS) queue. Send the requests to the queue. Configure the queue as an event source for Lambda.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 upload → trigger Lambda (async) → process documents. Marketing campaign → many documents not processed.
- **Existing Resources:** S3 bucket, Lambda function (S3 event notification trigger).
- **Current Issue/Goal:** Documents dropped/not processed under high volume.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `S3 event notification` | Async invocation → may be lost under load (no retry durability). |
| `did not process many` | Throttling or async invocation failure. |
| `SQS queue` | Durable buffer → Lambda polls from queue, retries on failure. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Reliability / Scalability
- **Constraints:** No data loss under high load

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- S3 → SQS → Lambda: decoupled architecture.
- SQS durable queue: messages không bị mất dù Lambda throttle hay fail.
- Lambda polls SQS → tự động scale dựa trên queue depth.
- Retry mechanism built-in (DLQ nếu cần).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Tăng timeout (max 15 min) không giải quyết mất events do throttling/concurrency limits.

**❌ Đáp án B:**
- Replication không giúp trigger lại Lambda, chỉ copy objects.

**❌ Đáp án C:**
- Thêm Lambda không giúp nếu vấn đề là async invocation failure và concurrency limits.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 → Lambda drops events under load. Add SQS in between for durability."*

