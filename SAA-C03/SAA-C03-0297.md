# Question #297 - Topic 1

A company deploys an application on five Amazon EC2 instances. An Application Load Balancer (ALB) distributes traffic to the instances by using a target group. The average CPU usage on each of the instances is below 10% most of the time, with occasional surges to 65%. A solutions architect needs to implement a solution to automate the scalability of the application. The solution must optimize the cost of the architecture and must ensure that the application has enough CPU resources when surges occur. Which solution will meet these requirements?

## Options

**A.** Create an Amazon CloudWatch alarm that enters the ALARM state when the CPUUtilization metric is less than 20%. Create an AWS Lambda function that the CloudWatch alarm invokes to terminate one of the EC2 instances in the ALB target group.

**B.** Create an EC2 Auto Scaling group. Select the existing ALB as the load balancer and the existing target group as the target group. Set a target tracking scaling policy that is based on the ASGAverageCPUUtilization metric. Set the minimum instances to 2, the desired capacity to 3, the maximum instances to 6, and the target value to 50%. Add the EC2 instances to the Auto Scaling group.

**C.** Create an EC2 Auto Scaling group. Select the existing ALB as the load balancer and the existing target group as the target group. Set the minimum instances to 2, the desired capacity to 3, and the maximum instances to 6. Add the EC2 instances to the Auto Scaling group.

**D.** Create two Amazon CloudWatch alarms. Configure the first CloudWatch alarm to enter the ALARM state when the average CPUUtilization metric is below 20%. Configure the second CloudWatch alarm to enter the ALARM state when the average CPUUtilization matric is above 50%. Configure the alarms to publish to an Amazon Simple Notification Service (Amazon SNS) topic to send an email message. After receiving the message, log in to decrease or increase the number of EC2 instances that are running.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 5 EC2 instances, CPU mostly <10%, surges to 65%. Cần auto scaling tự động, tối ưu cost.
- **Existing Resources:** 5 EC2 instances, ALB, target group.
- **Current Issue/Goal:** Auto scale for cost savings + handle CPU surges.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `automate the scalability` | Cần tự động, không manual. |
| `optimize the cost` | Scale in khi CPU thấp để giảm cost. |
| `enough CPU resources when surges occur` | Scale out khi cần. |
| `target tracking scaling policy` | Auto Scaling tự động giữ target metric (VD: 50% CPU). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Automated, cost-optimized, handle surges

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Auto Scaling group với target tracking scaling policy dựa trên ASGAverageCPUUtilization (target 50%) → tự động scale out khi CPU >50% và scale in khi CPU thấp.
- Min=2, desired=3, max=6: scale in khi không cần thiết (tiết kiệm cost), scale out khi surge.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudWatch alarm trigger khi CPU <20% → terminate instance. Không handle được surges (chỉ scale in, không scale out).

**❌ Đáp án C:**
- Không có scaling policy → instances không tự động scale dựa trên CPU. Chỉ set min/desired/max → không tự động phản ứng với surges.

**❌ Đáp án D:**
- Manual: gửi email và yêu cầu login để scale → không automated. Không đáp ứng "automate the scalability".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Auto scale tự động → target tracking policy. CPU 50% target → scale out khi surge, scale in khi thấp."*
