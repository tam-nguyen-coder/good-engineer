# Question #210 - Topic 1

A company offers a food delivery service that is growing rapidly. Because of the growth, the company's order processing system is experiencing scaling problems during peak traffic hours. The current architecture includes the following: • A group of Amazon EC2 instances that run in an Amazon EC2 Auto Scaling group to collect orders from the application • Another group of EC2 instances that run in an Amazon EC2 Auto Scaling group to fulfill orders The order collection process occurs quickly, but the order fulfillment process can take longer. Data must not be lost because of a scaling event. A solutions architect must ensure that the order collection process and the order fulfillment process can both scale properly during peak traffic hours. The solution must optimize utilization of the company's AWS resources. Which solution meets these requirements?

## Options

**A.** Use Amazon CloudWatch metrics to monitor the CPU of each instance in the Auto Scaling groups. Configure each Auto Scaling group's minimum capacity according to peak workload values.

**B.** Use Amazon CloudWatch metrics to monitor the CPU of each instance in the Auto Scaling groups. Configure a CloudWatch alarm to invoke an Amazon Simple Notification Service (Amazon SNS) topic that creates additional Auto Scaling groups on demand.

**C.** Provision two Amazon Simple Queue Service (Amazon SQS) queues: one for order collection and another for order fulfillment. Configure the EC2 instances to poll their respective queue. Scale the Auto Scaling groups based on notifications that the queues send.

**D.** Provision two Amazon Simple Queue Service (Amazon SQS) queues: one for order collection and another for order fulfillment. Configure the EC2 instances to poll their respective queue. Create a metric based on a backlog per instance calculation. Scale the Auto Scaling groups based on this metric.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Two ASGs: collection (fast) + fulfillment (slow). Peak traffic scaling issues. No data loss on scaling events. Optimize utilization.
- **Existing Resources:** Two Auto Scaling groups of EC2 instances.
- **Current Issue/Goal:** Proper scaling based on SQS backlog.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Data must not be lost` | **SQS queue** — persistent, decoupled |
| `backlog per instance calculation` | `ApproximateNumberOfMessages` / `RunningInstances` |
| `optimize utilization` | Scale dựa trên backlog, không dựa trên CPU |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Scaling / Messaging
- **Constraints:** Decoupled, no data loss, optimal utilization

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **SQS queues** — decouple collection và fulfillment, durable (no data loss).
- **Backlog per instance** metric — `ApproximateNumberOfMessages` / `RunningInstances` → số lượng messages cần xử lý mỗi instance.
- Scale dựa trên backlog → optimal utilization, không over/under provision.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Min capacity according to peak — oversizing, không optimal utilization.

**❌ Đáp án B:**
- CPU metrics + SNS create ASG — CPU không phải metric tốt cho queue-based processing.

**❌ Đáp án C:**
- Scale based on queue notifications — SQS không gửi notification trực tiếp ASG.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS backlog per instance = optimal scaling metric. CPU = wrong metric for queue-based apps"*
