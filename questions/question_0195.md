# Question #195 - Topic 1

A company's order system sends requests from clients to Amazon EC2 instances. The EC2 instances process the orders and then store the orders in a database on Amazon RDS. Users report that they must reprocess orders when the system fails. The company wants a resilient solution that can process orders automatically if a system outage occurs. What should a solutions architect do to meet these requirements?

## Options

**A.** Move the EC2 instances into an Auto Scaling group. Create an Amazon EventBridge (Amazon CloudWatch Events) rule to target an Amazon Elastic Container Service (Amazon ECS) task.

**B.** Move the EC2 instances into an Auto Scaling group behind an Application Load Balancer (ALB). Update the order system to send messages to the ALB endpoint.

**C.** Move the EC2 instances into an Auto Scaling group. Configure the order system to send messages to an Amazon Simple Queue Service (Amazon SQS) queue. Configure the EC2 instances to consume messages from the queue.

**D.** Create an Amazon Simple Notification Service (Amazon SNS) topic. Create an AWS Lambda function, and subscribe the function to the SNS topic. Configure the order system to send messages to the SNS topic. Send a command to the EC2 instances to process the messages by using AWS Systems Manager Run Command.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Order system → EC2 → RDS. On failure, users must reprocess manually. Need resilient solution with auto-retry.
- **Existing Resources:** Order system, EC2 instances, RDS.
- **Current Issue/Goal:** Decoupled, durable queuing with auto-recovery.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `process orders automatically if a system outage occurs` | **SQS queue** (durable, decouple) |
| `reprocess orders when the system fails` | Hiện tại thiếu queue — messages bị mất |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Resilience / Messaging
- **Constraints:** Auto-process on failure, decoupled

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **SQS queue** — decouple client và EC2 instances.
- Messages trong SQS persisted → nếu EC2 fails, messages không mất, có thể xử lý sau.
- **Auto Scaling group** — tự động thay thế failed instances, consume từ queue.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EventBridge + ECS — không durable message storage, messages mất khi fail.

**❌ Đáp án B:**
- ALB — không durable, message mất khi fail.

**❌ Đáp án D:**
- SNS — push-based, không durable nếu subscriber không available. Lambda không persist messages.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS + ASG = decoupled, durable, auto-recovery. ALB/EventBridge/SNS = not durable"*
