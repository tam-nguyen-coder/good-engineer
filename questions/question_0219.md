# Question #219 - Topic 1

A company's application is having performance issues. The application is stateful and needs to complete in-memory tasks on Amazon EC2 instances. The company used AWS CloudFormation to deploy infrastructure and used the M5 EC2 instance family. As traffic increased, the application performance degraded. Users are reporting delays when the users attempt to access the application. Which solution will resolve these issues in the MOST operationally efficient way?

## Options

**A.** Replace the EC2 instances with T3 EC2 instances that run in an Auto Scaling group. Make the changes by using the AWS Management Console.

**B.** Modify the CloudFormation templates to run the EC2 instances in an Auto Scaling group. Increase the desired capacity and the maximum capacity of the Auto Scaling group manually when an increase is necessary.

**C.** Modify the CloudFormation templates. Replace the EC2 instances with R5 EC2 instances. Use Amazon CloudWatch built-in EC2 memory metrics to track the application performance for future capacity planning.

**D.** Modify the CloudFormation templates. Replace the EC2 instances with R5 EC2 instances. Deploy the Amazon CloudWatch agent on the EC2 instances to generate custom application latency metrics for future capacity planning.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Stateful app, in-memory tasks on M5 instances. Performance degrades with traffic. Users report delays.
- **Existing Resources:** CloudFormation, M5 instances.
- **Current Issue/Goal:** Fix performance, operationally efficient.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `in-memory tasks` | Memory-intensive → **R5** (memory-optimized) |
| `M5` | General-purpose — không đủ memory |
| `MOST operationally efficient` | Modify CloudFormation templates + CloudWatch agent |
| `application latency` | Custom metric cần **CloudWatch agent** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance / Compute
- **Constraints:** Memory-bound, operationally efficient

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **R5 instances** — memory-optimized, phù hợp in-memory workloads.
- **CloudWatch agent** — thu thập memory metrics (built-in EC2 không có).
- CloudFormation — infrastructure as code, operationally efficient.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- T3 (burstable) — worse performance cho memory-intensive app.

**❌ Đáp án B:**
- Manual scaling — không operationally efficient, vẫn dùng M5.

**❌ Đáp án C:**
- "Built-in EC2 memory metrics" — CloudWatch không có memory metrics mặc định (cần agent).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"R5 = memory-optimized. CloudWatch agent = custom metrics (memory/latency). T3 = burst (not for memory)"*
