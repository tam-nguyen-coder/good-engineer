# Question #164 - Topic 1

A company has two applications: a sender application that sends messages with payloads to be processed and a processing application intended to receive the messages with payloads. The company wants to implement an AWS service to handle messages between the two applications. The sender application can send about 1,000 messages each hour. The messages may take up to 2 days to be processed: If the messages fail to process, they must be retained so that they do not impact the processing of any remaining messages. Which solution meets these requirements and is the MOST operationally efficient?

## Options

**A.** Set up an Amazon EC2 instance running a Redis database. Configure both applications to use the instance. Store, process, and delete the messages, respectively.

**B.** Use an Amazon Kinesis data stream to receive the messages from the sender application. Integrate the processing application with the Kinesis Client Library (KCL).

**C.** Integrate the sender and processor applications with an Amazon Simple Queue Service (Amazon SQS) queue. Configure a dead-letter queue to collect the messages that failed to process.

**D.** Subscribe the processing application to an Amazon Simple Notification Service (Amazon SNS) topic to receive notifications to process. Integrate the sender application to write to the SNS topic.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Sender → Processing. 1000 msgs/hour, up to 2 days to process. Failed messages must be retained without blocking others.
- **Existing Resources:** Two applications.
- **Current Issue/Goal:** Decoupled messaging with DLQ for failures.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `decoupled` | **SQS queue** |
| `failed to process... retained` | **Dead-letter queue (DLQ)** |
| `do not impact the processing of any remaining messages` | DLQ isolates failed messages |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Messaging
- **Constraints:** 2-day processing, DLQ for failures

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **SQS queue** — decouple sender & processor, durable storage.
- **Visibility timeout** có thể set up to 12 hours → cho phép 2-day processing (có thể extend).
- **Dead-letter queue** — retain failed messages riêng, không block messages khác.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 + Redis — operational overhead, không durably như SQS.

**❌ Đáp án B:**
- Kinesis — real-time streaming, không phù hợp cho messages có thể mất 2 ngày để process.

**❌ Đáp án D:**
- SNS — push model, không durable retention. Không có DLQ.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS + DLQ = decoupled + durable + failure isolation. Kinesis = real-time. SNS = push (no DLQ)"*
