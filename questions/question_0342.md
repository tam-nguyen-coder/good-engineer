# Question #342 - Topic 1

A transaction processing company has weekly scripted batch jobs that run on Amazon EC2 instances. The EC2 instances are in an Auto Scaling group. The number of transactions can vary, but the baseline CPU utilization that is noted on each run is at least 60%. The company needs to provision the capacity 30 minutes before the jobs run. Currently, engineers complete this task by manually modifying the Auto Scaling group parameters. The company does not have the resources to analyze the required capacity trends for the Auto Scaling group counts. The company needs an automated way to modify the Auto Scaling group's desired capacity. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create a dynamic scaling policy for the Auto Scaling group. Configure the policy to scale based on the CPU utilization metric. Set the target value for the metric to 60%.

**B.** Create a scheduled scaling policy for the Auto Scaling group. Set the appropriate desired capacity, minimum capacity, and maximum capacity. Set the recurrence to weekly. Set the start time to 30 minutes before the batch jobs run.

**C.** Create a predictive scaling policy for the Auto Scaling group. Configure the policy to scale based on forecast. Set the scaling metric to CPU utilization. Set the target value for the metric to 60%. In the policy, set the instances to pre-launch 30 minutes before the jobs run.

**D.** Create an Amazon EventBridge event to invoke an AWS Lambda function when the CPU utilization metric value for the Auto Scaling group reaches 60%. Configure the Lambda function to increase the Auto Scaling group's desired capacity and maximum capacity by 20%.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Weekly batch jobs, EC2 ASG. CPU baseline ≥60%. Need capacity 30 min before jobs run. No resources to analyze capacity trends.
- **Existing Resources:** Auto Scaling group, EC2 instances, weekly batch jobs.
- **Current Issue/Goal:** Automated scaling before weekly jobs, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `30 minutes before the jobs run` | Cần pre-launch instances, không thể reactive. |
| `does not have the resources to analyze capacity trends` | Predictive scaling tự động học từ lịch sử để forecast. |
| `predictive scaling` | ML-based: forecast load và pre-launch instances. |
| `pre-launch 30 minutes` | Predictive scaling có option "pre-launch" instances trước khi load tăng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Pre-provision 30 min before weekly batch, no capacity analysis resources

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Predictive scaling: ML phân tích historical load patterns → tự động forecast và pre-launch instances 30 minutes before.
- Không cần manual analysis capacity trends (ML tự học).
- Pre-launch option: instances ready trước khi jobs start.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Dynamic/target tracking scaling: reactive (scale khi CPU đã 60%), không pre-launch trước 30 phút.

**❌ Đáp án B:**
- Scheduled scaling: cần biết chính xác desired capacity. "No resources to analyze" → không biết set bao nhiêu instances.

**❌ Đáp án D:**
- EventBridge + Lambda: reactive (dựa trên CloudWatch metric). Khi CPU đã 60%, quá trễ (cần pre-launch).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Pre-launch 30 min before weekly batch → Predictive Scaling (ML forecast + pre-launch). Scheduled = cần biết exact capacity."*
