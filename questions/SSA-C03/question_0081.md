# Question #81 - Topic 1

A solutions architect is designing the cloud architecture for a new application being deployed on AWS. The process should run in parallel while adding and removing application nodes as needed based on the number of jobs to be processed. The processor application is stateless. The solutions architect must ensure that the application is loosely coupled and the job items are durably stored. Which design should the solutions architect use?

## Options

**A.** Create an Amazon SNS topic to send the jobs that need to be processed. Create an Amazon Machine Image (AMI) that consists of the processor application. Create a launch configuration that uses the AMI. Create an Auto Scaling group using the launch configuration. Set the scaling policy for the Auto Scaling group to add and remove nodes based on CPU usage.

**B.** Create an Amazon SQS queue to hold the jobs that need to be processed. Create an Amazon Machine Image (AMI) that consists of the processor application. Create a launch configuration that uses the AMI. Create an Auto Scaling group using the launch configuration. Set the scaling policy for the Auto Scaling group to add and remove nodes based on network usage.

**C.** Create an Amazon SQS queue to hold the jobs that need to be processed. Create an Amazon Machine Image (AMI) that consists of the processor application. Create a launch template that uses the AMI. Create an Auto Scaling group using the launch template. Set the scaling policy for the Auto Scaling group to add and remove nodes based on the number of items in the SQS queue.

**D.** Create an Amazon SNS topic to send the jobs that need to be processed. Create an Amazon Machine Image (AMI) that consists of the processor application. Create a launch template that uses the AMI. Create an Auto Scaling group using the launch template. Set the scaling policy for the Auto Scaling group to add and remove nodes based on the number of messages published to the SNS topic.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Parallel processing, stateless app, scale based on job count, loosely coupled, durable storage.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Loosely coupled, durably stored jobs, auto-scale.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `loosely coupled` | Cần **SQS queue** (decouple producers & consumers) |
| `durably stored` | SQS lưu message durably |
| `number of jobs to be processed` | Scale dựa trên **SQS queue depth** |
| `stateless` | Worker có thể thêm/xoá tự do |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Scalable processing
- **Constraints:** Loosely coupled, durable, auto-scale based on jobs

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **SQS queue** — loosely coupled, durably stores jobs.
- **ASG với scaling policy dựa trên SQS queue depth (ApproximateNumberOfMessages)** — scale chính xác theo số lượng jobs.
- **Launch template** (modern hơn launch configuration).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **SNS** không durable storage (subscriber phải available) — messages bị mất nếu không có subscriber.
- CPU usage scaling không liên quan trực tiếp đến job count.

**❌ Đáp án B:**
- SQS queue đúng, nhưng network usage không phải metric tốt để scale based on jobs.

**❌ Đáp án D:**
- SNS không durable — messages bị mất nếu không ai đọc.
- Scaling based on SNS published messages — SNS không có metric này.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS = durable + decoupled. SNS = push notification (no durability). ASG scale on queue depth = worker pattern"*
