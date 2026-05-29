# Question #98 - Topic 1

An image-processing company has a web application that users use to upload images. The application uploads the images into an Amazon S3 bucket. The company has set up S3 event notifications to publish the object creation events to an Amazon Simple Queue Service (Amazon SQS) standard queue. The SQS queue serves as the event source for an AWS Lambda function that processes the images and sends the results to users through email. Users report that they are receiving multiple email messages for every uploaded image. A solutions architect determines that SQS messages are invoking the Lambda function more than once, resulting in multiple email messages. What should the solutions architect do to resolve this issue with the LEAST operational overhead?

## Options

**A.** Set up long polling in the SQS queue by increasing the ReceiveMessage wait time to 30 seconds.

**B.** Change the SQS standard queue to an SQS FIFO queue. Use the message deduplication ID to discard duplicate messages.

**C.** Increase the visibility timeout in the SQS queue to a value that is greater than the total of the function timeout and the batch window timeout.

**D.** Modify the Lambda function to delete each message from the SQS queue immediately after the message is read before processing.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 → SQS standard → Lambda xử lý ảnh → email. Users nhận multiple emails cho mỗi ảnh.
- **Existing Resources:** S3, SQS standard queue, Lambda.
- **Current Issue/Goal:** SQS standard queue gửi message nhiều lần (at-least-once delivery).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SQS standard queue` | At-least-once delivery → có thể duplicate |
| `invoking the Lambda function more than once` | Cần **FIFO queue** (exactly-once) |
| `message deduplication ID` | FIFO dùng deduplication ID |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Message processing + Deduplication
- **Constraints:** Least operational overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **SQS standard queue** — at-least-once delivery → messages có thể được deliver nhiều lần.
- **SQS FIFO queue** — exactly-once processing, hỗ trợ **message deduplication ID**.
- Chỉ cần đổi queue type, không cần sửa Lambda code nhiều.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Long polling** giảm số empty polls, không ngăn duplicate delivery.

**❌ Đáp án C:**
- **Visibility timeout** — nếu message không được delete kịp, nó xuất hiện lại. Nhưng với standard queue, message vẫn có thể duplicate ngay cả khi visibility timeout đủ.

**❌ Đáp án D:**
- Delete trước khi process — nếu processing thất bại, message bị mất. Không an toàn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Standard queue = at-least-once (possible duplicates). FIFO queue = exactly-once (no duplicates)"*
