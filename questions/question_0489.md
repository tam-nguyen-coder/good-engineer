# Question #489 - Topic 1

An ecommerce company runs an application in the AWS Cloud that is integrated with an on-premises warehouse solution. The company uses Amazon Simple Notification Service (Amazon SNS) to send order messages to an on-premises HTTPS endpoint so the warehouse application can process the orders. The local data center team has detected that some of the order messages were not received. A solutions architect needs to retain messages that are not delivered and analyze the messages for up to 14 days. Which solution will meet these requirements with the LEAST development effort?

## Options

**A.** Configure an Amazon SNS dead letter queue that has an Amazon Kinesis Data Stream target with a retention period of 14 days.

**B.** Add an Amazon Simple Queue Service (Amazon SQS) queue with a retention period of 14 days between the application and Amazon SNS.

**C.** Configure an Amazon SNS dead letter queue that has an Amazon Simple Queue Service (Amazon SQS) target with a retention period of 14 days.

**D.** Configure an Amazon SNS dead letter queue that has an Amazon DynamoDB target with a TTL attribute set for a retention period of 14 days.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce app dùng SNS gửi order messages tới on-premises HTTPS endpoint. Một số messages không được nhận. Cần retain undelivered messages trong 14 ngày để analyze.
- **Existing Resources:** SNS topic, HTTPS endpoint on-premises.
- **Current Issue/Goal:** Retain failed messages (undelivered) tối đa 14 ngày với least development effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `messages that are not delivered` | SNS dead-letter queue (DLQ) để capture failed deliveries. |
| `retention period of 14 days` | SQS retention: tối đa 14 days. |
| `least development effort` | Tận dụng SNS DLQ built-in, không cần code. |
| `dead letter queue` | SNS có thể gửi failed messages vào SQS DLQ tự động. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least development effort
- **Constraints:** Retain undelivered SNS messages 14 days.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- SNS có built-in **dead-letter queue (DLQ)** support.
- Configure SNS DLQ với target là **SQS queue**, set retention period = 14 ngày.
- Khi SNS không thể delivery message tới HTTPS endpoint, message tự động được chuyển vào DLQ.
- **Zero code** - chỉ cần configuration. Phân tích messages bằng cách poll SQS queue.
- SQS retention tối đa 14 ngày → đáp ứng yêu cầu.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DLQ với **Kinesis Data Stream** target: SNS DLQ không support Kinesis Data Stream làm target. DLQ chỉ support SQS và Lambda.

**❌ Đáp án B:**
- Thêm SQS queue giữa application và SNS: không giải quyết vấn đề undelivered messages tới HTTPS endpoint. SQS không capture messages mà SNS đã gửi nhưng không delivery được.

**❌ Đáp án D:**
- DLQ với **DynamoDB** target: SNS DLQ không support DynamoDB. Cần custom code để write từ DLQ vào DynamoDB → development effort cao.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SNS fail → DLQ (SQS). Zero code, retention 14 ngày. Kinesis/DynamoDB không phải DLQ target."*
