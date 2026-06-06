# Question #67 - Topic 1

A company hosts an application on multiple Amazon EC2 instances. The application processes messages from an Amazon SQS queue, writes to an Amazon RDS table, and deletes the message from the queue. Occasional duplicate records are found in the RDS table. The SQS queue does not contain any duplicate messages. What should a solutions architect do to ensure messages are being processed once only?

## Options

**A.** Use the CreateQueue API call to create a new queue.

**B.** Use the AddPermission API call to add appropriate permissions.

**C.** Use the ReceiveMessage API call to set an appropriate wait time.

**D.** Use the ChangeMessageVisibility API call to increase the visibility timeout.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances đọc SQS → write RDS → delete message. Occasional duplicates in RDS.
- **Existing Resources:** EC2, SQS queue, RDS.
- **Current Issue/Goal:** SQS không có duplicate, nhưng RDS có duplicate records.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SQS queue does not contain any duplicate messages` | Vấn đề không phải do SQS gửi duplicate |
| `processes messages... writes to... deletes the message` | Worker pattern |
| `duplicate records in RDS` | Message được process nhiều lần |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Fault tolerance / Message processing
- **Constraints:** Process once only

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Visibility timeout** là thời gian message ẩn sau khi được receive. Nếu worker không delete kịp (do timeout), message trở lại queue và được xử lý lại → duplicate.
- **Tăng visibility timeout** giúp worker có đủ thời gian xử lý và delete message trước khi nó xuất hiện lại.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Tạo queue mới không giải quyết vấn đề processing duplicate.

**❌ Đáp án B:**
- AddPermission chỉ để phân quyền, không liên quan đến duplicate processing.

**❌ Đáp án C:**
- **Wait time** (long polling) giảm số lần poll rỗng, không ảnh hưởng đến duplicate processing.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Visibility timeout quá thấp → message process lại → duplicate. Tăng timeout để đủ thời gian xử lý"*
