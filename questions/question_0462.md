# Question #462 - Topic 1

A company has an application that processes customer orders. The company hosts the application on an Amazon EC2 instance that saves the orders to an Amazon Aurora database. Occasionally when traffic is high the workload does not process orders fast enough. What should a solutions architect do to write the orders reliably to the database as quickly as possible?

## Options

**A.** Increase the instance size of the EC2 instance when traffic is high. Write orders to Amazon Simple Notification Service (Amazon SNS). Subscribe the database endpoint to the SNS topic.

**B.** Write orders to an Amazon Simple Queue Service (Amazon SQS) queue. Use EC2 instances in an Auto Scaling group behind an Application Load Balancer to read from the SQS queue and process orders into the database.

**C.** Write orders to Amazon Simple Notification Service (Amazon SNS). Subscribe the database endpoint to the SNS topic. Use EC2 instances in an Auto Scaling group behind an Application Load Balancer to read from the SNS topic.

**D.** Write orders to an Amazon Simple Queue Service (Amazon SQS) queue when the EC2 instance reaches CPU threshold limits. Use scheduled scaling of EC2 instances in an Auto Scaling group behind an Application Load Balancer to read from the SQS queue and process orders into the database.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Application xử lý orders trên EC2, lưu vào Aurora. Khi traffic cao, xử lý không kịp.
- **Existing Resources:** EC2 instance, Aurora database.
- **Current Issue/Goal:** Write orders reliably và nhanh nhất có thể.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `reliably` | Dùng queue để buffer, không mất data khi traffic spike. |
| `as quickly as possible` | SQS decouple + Auto Scaling scale out workers để xử lý song song. |
| `when traffic is high` | Không phải lúc nào cũng high traffic → Auto Scaling dựa trên Queue depth (backlog). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Reliable + Fast processing
- **Constraints:** Handle traffic spikes, write reliably

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- SQS queue: buffer orders khi traffic spike → không mất data, decouple producer khỏi consumer.
- Auto Scaling group scale dựa trên SQS queue depth (ApproximateNumberOfMessagesVisible).
- ALB không thực sự cần thiết ở đây (workers poll SQS trực tiếp), nhưng đây là pattern phổ biến.
- Nhiều EC2 instances xử lý song song → tăng throughput.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- SNS không phải queue: push-based, nếu database không kịp xử lý thì mất message. Database endpoint không thể subscribe SNS trực tiếp.
- Scale up instance (vertical) có giới hạn, không tối ưu.

**❌ Đáp án C:**
- SNS: không có persistence, message bị mất nếu consumer không kịp xử lý.
- Database không thể subscribe SNS topic.
- Worker đọc từ SNS không được khuyến khích (không có polling mechanism).

**❌ Đáp án D:**
- "Write orders to SQS queue when CPU threshold limits" → sai logic: orders phải luôn được ghi vào queue, không chỉ khi CPU high.
- "Scheduled scaling" → không phản ứng kịp với traffic spike đột ngột. Cần scaling dựa trên metric.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Backend processing bottleneck → SQS buffer + Auto Scaling workers. SNS = push, mất message; SQS = queue, không mất."*
