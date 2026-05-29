# Question #130 - Topic 1

An application runs on Amazon EC2 instances across multiple Availability Zonas. The instances run in an Amazon EC2 Auto Scaling group behind an Application Load Balancer. The application performs best when the CPU utilization of the EC2 instances is at or near 40%. What should a solutions architect do to maintain the desired performance across all instances in the group?

## Options

**A.** Use a simple scaling policy to dynamically scale the Auto Scaling group.

**B.** Use a target tracking policy to dynamically scale the Auto Scaling group.

**C.** Use an AWS Lambda function ta update the desired Auto Scaling group capacity.

**D.** Use scheduled scaling actions to scale up and scale down the Auto Scaling group.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 ASG behind ALB. Best performance at ~40% CPU.
- **Existing Resources:** ASG, ALB.
- **Current Issue/Goal:** Maintain CPU at 40%.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `CPU utilization... at or near 40%` | **Target tracking** với target value = 40% |
| `maintain the desired performance` | Auto scale to keep metric at target |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Auto Scaling
- **Constraints:** Maintain CPU at 40%

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Target tracking policy** — tự động scale để giữ CPU Average ở target value (40%).
- Chọn metric `ASGAverageCPUUtilization`, set target = 40%.
- Không cần định nghĩa thresholds như simple/step scaling.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Simple scaling** — dùng CloudWatch alarms với thresholds, không tự động maintain exact target.

**❌ Đáp án C:**
- Lambda — custom, operational overhead, không cần thiết.

**❌ Đáp án D:**
- **Scheduled scaling** — dùng cho predictable traffic patterns, không dựa trên CPU utilization.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Target tracking = maintain metric at target value (e.g., 40% CPU). Simple/step = threshold-based"*
