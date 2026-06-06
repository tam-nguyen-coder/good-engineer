# Question #275 - Topic 1

A company runs an internal browser-based application. The application runs on Amazon EC2 instances behind an Application Load Balancer. The instances run in an Amazon EC2 Auto Scaling group across multiple Availability Zones. The Auto Scaling group scales up to 20 instances during work hours, but scales down to 2 instances overnight. Staff are complaining that the application is very slow when the day begins, although it runs well by mid-morning. How should the scaling be changed to address the staff complaints and keep costs to a minimum?

## Options

**A.** Implement a scheduled action that sets the desired capacity to 20 shortly before the office opens.

**B.** Implement a step scaling action triggered at a lower CPU threshold, and decrease the cooldown period.

**C.** Implement a target tracking action triggered at a lower CPU threshold, and decrease the cooldown period.

**D.** Implement a scheduled action that sets the minimum and maximum capacity to 20 shortly before the office opens.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Internal app, ASG 2→20 during work hours. Slow at day start, fine by mid-morning. Scale up takes too long.
- **Existing Resources:** EC2 + ALB + ASG.
- **Current Issue/Goal:** Pre-scale before office opens, min cost.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `very slow when the day begins` | Reactive scaling quá chậm → cần **Scheduled scaling** |
| `keep costs to a minimum` | Scheduled action (scale down after hours) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Auto Scaling
- **Constraints:** No morning lag, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Scheduled action** — set desired capacity = 20 trước giờ office mở cửa.
- Instances ready khi staff bắt đầu làm việc → không lag.
- Vẫn scale down về 2 overnight → cost-effective.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Step scaling + lower CPU threshold — reactive, vẫn bị lag.

**❌ Đáp án C:**
- Target tracking + lower CPU — reactive, vẫn bị lag.

**❌ Đáp án D:**
- Set min/max to 20 — không scale down được, tốn chi phí.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Scheduled scaling = pre-warm for predictable patterns. Reactive = too slow for morning spike"*
