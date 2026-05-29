# Question #148 - Topic 1

A company has a data ingestion workflow that includes the following components: An Amazon Simple Notification Service (Amazon SNS) topic that receives notifications about new data deliveries An AWS Lambda function that processes and stores the data The ingestion workflow occasionally fails because of network connectivity issues. When failure occurs, the corresponding data is not ingested unless the company manually reruns the job. What should a solutions architect do to ensure that all notifications are eventually processed?

## Options

**A.** Configure the Lambda function for deployment across multiple Availability Zones.

**B.** Modify the Lambda function's configuration to increase the CPU and memory allocations for the function.

**C.** Configure the SNS topic’s retry strategy to increase both the number of retries and the wait time between retries.

**D.** Configure an Amazon Simple Queue Service (Amazon SQS) queue as the on-failure destination. Modify the Lambda function to process messages in the queue.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** SNS → Lambda. Occasional network failures → data not ingested (manual rerun needed).
- **Existing Resources:** SNS topic, Lambda function.
- **Current Issue/Goal:** Ensure all notifications processed eventually (durability + retry).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `eventually processed` | Cần dead-letter queue (DLQ) |
| `network connectivity issues` | Cần retry mechanism |
| `on-failure destination` | Lambda có thể gửi failed events đến SQS |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Event-driven / Resilience
- **Constraints:** Eventually consistent processing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **SQS queue as on-failure destination** — Lambda failed events được gửi vào queue.
- Lambda có thể xử lý lại messages từ queue sau khi network khôi phục.
- Pattern: SNS → Lambda → (on failure) SQS DLQ → reprocess.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Multi-AZ Lambda — không giúp retry khi network failure.

**❌ Đáp án B:**
- Tăng CPU/memory — không giải quyết network connectivity issue.

**❌ Đáp án C:**
- SNS retry strategy — chỉ retry gửi đến Lambda, không durable storage cho failed events.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS DLQ = async retry for failed Lambda invocations. SNS retry = limited. Multi-AZ ≠ retry"*
