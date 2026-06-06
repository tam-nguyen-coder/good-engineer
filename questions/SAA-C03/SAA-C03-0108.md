# Question #108 - Topic 1

A company has an automobile sales website that stores its listings in a database on Amazon RDS. When an automobile is sold, the listing needs to be removed from the website and the data must be sent to multiple target systems. Which design should a solutions architect recommend?

## Options

**A.** Create an AWS Lambda function triggered when the database on Amazon RDS is updated to send the information to an Amazon Simple Queue Service (Amazon SQS) queue for the targets to consume.

**B.** Create an AWS Lambda function triggered when the database on Amazon RDS is updated to send the information to an Amazon Simple Queue Service (Amazon SQS) FIFO queue for the targets to consume.

**C.** Subscribe to an RDS event notification and send an Amazon Simple Queue Service (Amazon SQS) queue fanned out to multiple Amazon Simple Notification Service (Amazon SNS) topics. Use AWS Lambda functions to update the targets.

**D.** Subscribe to an RDS event notification and send an Amazon Simple Notification Service (Amazon SNS) topic fanned out to multiple Amazon Simple Queue Service (Amazon SQS) queues. Use AWS Lambda functions to update the targets.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Auto sales website, RDS database. When sold: remove listing + send data to multiple targets.
- **Existing Resources:** RDS database, website.
- **Current Issue/Goal:** Fanout event to multiple target systems.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sent to multiple target systems` | Cần **SNS fanout** pattern |
| `RDS event notification` | RDS có thể publish events |
| `fanned out` | SNS → multiple SQS queues |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Event-driven / Messaging
- **Constraints:** Multiple targets

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **RDS event notification** — phát hiện khi database updated (sold event).
- **SNS topic** — publish event, **fanout** đến multiple SQS queues (mỗi target một queue).
- Mỗi SQS queue → Lambda function xử lý cho target tương ứng.
- Pattern chuẩn: SNS fanout → SQS → Lambda.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- RDS không thể trực tiếp trigger Lambda. Cần event notification hoặc CDC.

**❌ Đáp án B:**
- Giống A — không trigger trực tiếp.
- FIFO không cần thiết cho fanout.

**❌ Đáp án C:**
- SQS fanout to SNS topics — sai pattern. SNS fanout to SQS mới đúng.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SNS → SQS = fanout pattern (1 event → many consumers). SQS → SNS không phải fanout"*
