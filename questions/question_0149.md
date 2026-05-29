# Question #149 - Topic 1

A company has a service that produces event data. The company wants to use AWS to process the event data as it is received. The data is written in a specific order that must be maintained throughout processing. The company wants to implement a solution that minimizes operational overhead. How should a solutions architect accomplish this?

## Options

**A.** Create an Amazon Simple Queue Service (Amazon SQS) FIFO queue to hold messages. Set up an AWS Lambda function to process messages from the queue.

**B.** Create an Amazon Simple Notification Service (Amazon SNS) topic to deliver notifications containing payloads to process. Configure an AWS Lambda function as a subscriber.

**C.** Create an Amazon Simple Queue Service (Amazon SQS) standard queue to hold messages. Set up an AWS Lambda function to process messages from the queue independently.

**D.** Create an Amazon Simple Notification Service (Amazon SNS) topic to deliver notifications containing payloads to process. Configure an Amazon Simple Queue Service (Amazon SQS) queue as a subscriber.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Event data, order must be maintained (FIFO), minimize overhead.
- **Existing Resources:** Event producer.
- **Current Issue/Goal:** Ordered processing, serverless.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `order must be maintained throughout processing` | Cần **FIFO** queue |
| `minimizes operational overhead` | Serverless |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Messaging + Ordering
- **Constraints:** FIFO, minimal overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **SQS FIFO queue** — guaranteed exactly-once processing, first-in-first-out.
- **Lambda** — serverless, poll queue và xử lý theo thứ tự.
- FIFO đảm bảo thứ tự messages được giữ nguyên.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **SNS** — async push, không đảm bảo thứ tự.

**❌ Đáp án C:**
- **SQS Standard** — at-least-once, không đảm bảo thứ tự.

**❌ Đáp án D:**
- SNS → SQS — SNS doesn't guarantee order, even with FIFO queue.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"FIFO = first-in-first-out + exactly-once. Standard = no ordering. SNS = push (no ordering)"*
