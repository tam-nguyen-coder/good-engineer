# Question #248 - Topic 1

A company runs analytics software on Amazon EC2 instances. The software accepts job requests from users to process data that has been uploaded to Amazon S3. Users report that some submitted data is not being processed. Amazon CloudWatch reveals that the EC2 instances have a consistent CPU utilization at or near 100%. The company wants to improve system performance and scale the system based on user load. What should a solutions architect do to meet these requirements?

## Options

**A.** Create a copy of the instance. Place all instances behind an Application Load Balancer.

**B.** Create an S3 VPC endpoint for Amazon S3. Update the software to reference the endpoint.

**C.** Stop the EC2 instances. Modify the instance type to one with a more powerful CPU and more memory. Restart the instances.

**D.** Route incoming requests to Amazon Simple Queue Service (Amazon SQS). Configure an EC2 Auto Scaling group based on queue size. Update the software to read from the queue.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 runs analytics, accepts job requests, processes data from S3. CPU 100%, some data not processed. Need to scale based on load.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Decouple + auto-scale based on queue.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `CPU utilization at or near 100%` | Instances overloaded |
| `scale the system based on user load` | **SQS queue depth** → ASG scaling |
| `some submitted data is not being processed` | Cần buffer — **SQS** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Scaling / Messaging
- **Constraints:** Decouple, auto-scale, no data loss

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **SQS queue** — buffer incoming requests, không lose data.
- **ASG based on queue size** — scale instances theo backlog.
- Software đọc từ queue → xử lý khi có capacity.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ALB + copy — không giải quyết CPU 100% (vẫn direct requests).

**❌ Đáp án B:**
- S3 VPC endpoint — không giúp scale compute.

**❌ Đáp án C:**
- Bigger instance — không scale, không decouple.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS + ASG queue depth = decouple + auto-scale. Bigger instance = vertical only. ALB = no buffer"*
