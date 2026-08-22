# Question #333 - Topic 1

A company's application runs on Amazon EC2 instances behind an Application Load Balancer (ALB). The instances run in an Amazon EC2 Auto Scaling group across multiple Availability Zones. On the first day of every month at midnight, the application becomes much slower when the month-end financial calculation batch runs. This causes the CPU utilization of the EC2 instances to immediately peak to 100%, which disrupts the application. What should a solutions architect recommend to ensure the application is able to handle the workload and avoid downtime?

## Options

**A.** Configure an Amazon CloudFront distribution in front of the ALB.

**B.** Configure an EC2 Auto Scaling simple scaling policy based on CPU utilization.

**C.** Configure an EC2 Auto Scaling scheduled scaling policy based on the monthly schedule.

**D.** Configure Amazon ElastiCache to remove some of the workload from the EC2 instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** End-of-month batch calculation causes CPU 100% spike predictable (first day of every month at midnight). Application disrupted.
- **Existing Resources:** ALB, EC2 Auto Scaling group, multi-AZ.
- **Current Issue/Goal:** Handle predictable monthly CPU spike, avoid downtime.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `first day of every month at midnight` | Predictable schedule → scheduled scaling policy. |
| `CPU utilization peak to 100% immediately` | Spike occurs instantly → reactive scaling (simple/target tracking) quá chậm. |
| `scheduled scaling policy` | Scale up BEFORE the event, scale down after. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Handle workload and avoid downtime
- **Constraints:** Predictable monthly pattern, immediate CPU spike

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Scheduled scaling policy: tăng số instances trước midnight ngày đầu tháng (proactive), giảm sau khi batch hoàn thành.
- Vì spike xảy ra ngay lập tức (100% CPU), reactive scaling (dựa trên CloudWatch metrics) không đủ nhanh.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFront caches static/dynamic content, không giúp xử lý financial calculation workload.

**❌ Đáp án B:**
- Simple scaling policy dựa trên CPU utilization → reactive. Khi CPU đã 100%, scaling out quá chậm, application đã bị disrupt.

**❌ Đáp án D:**
- ElastiCache cache database queries, không thể chạy financial calculation batches.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Predictable monthly spike → scheduled scaling (proactive). Reactive scaling (CPU-based) quá chậm cho spike đột ngột."*
