# Question #271 - Topic 1

A solutions architect observes that a nightly batch processing job is automatically scaled up for 1 hour before the desired Amazon EC2 capacity is reached. The peak capacity is the same every night and the batch jobs always start at 1 AM. The solutions architect needs to find a cost-effective solution that will allow for the desired EC2 capacity to be reached quickly and allow the Auto Scaling group to scale down after the batch jobs are complete. What should the solutions architect do to meet these requirements?

## Options

**A.** Increase the minimum capacity for the Auto Scaling group.

**B.** Increase the maximum capacity for the Auto Scaling group.

**C.** Configure scheduled scaling to scale up to the desired compute level.

**D.** Change the scaling policy to add more EC2 instances during each scaling operation.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Nightly batch job at 1 AM. ASG takes 1 hour to scale to desired capacity.
- **Existing Resources:** Auto Scaling group.
- **Current Issue/Goal:** Pre-scale before job starts, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `peak capacity is the same every night` | Predictable → **Scheduled scaling** |
| `batch jobs always start at 1 AM` | Scale up before 1 AM |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Auto Scaling / Scheduling
- **Constraints:** Predictable load, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Scheduled scaling** — tăng desired capacity lên mức cần thiết trước 1 AM.
- Sau batch job, scheduled action scale down.
- Cost-effective — không giữ instances chạy cả ngày.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Tăng min capacity — instances chạy 24/7, tốn chi phí.

**❌ Đáp án B:**
- Tăng max capacity — không giúp scale nhanh hơn.

**❌ Đáp án D:**
- Change scaling policy — reactive, vẫn mất thời gian scale.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Scheduled scaling = predictable load. Reactive scaling = slow for predictable patterns"*
