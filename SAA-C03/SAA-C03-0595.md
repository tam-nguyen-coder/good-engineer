# Question #595 - Topic 1

A company's applications run on Amazon EC2 instances in Auto Scaling groups. The company notices that its applications experience sudden traffic increases on random days of the week. The company wants to maintain application performance during sudden traffic increases. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Use manual scaling to change the size of the Auto Scaling group.

**B.** Use predictive scaling to change the size of the Auto Scaling group.

**C.** Use dynamic scaling to change the size of the Auto Scaling group.

**D.** Use schedule scaling to change the size of the Auto Scaling group.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 ASG, sudden traffic increases on random days, maintain performance.
- **Existing Resources:** Auto Scaling groups.
- **Current Issue/Goal:** Respond to unpredictable traffic spikes, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sudden traffic increases on random days` | Unpredictable → cần reactive scaling (dynamic). |
| `dynamic scaling` | Scale based on real-time metrics (CPU, request count, etc.). |
| `predictive scaling` | Dựa trên historical data, không hiệu quả cho random patterns. |
| `schedule scaling` | Fixed schedule, không hiệu quả cho unexpected spikes. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effectively
- **Constraints:** Unpredictable traffic spikes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Dynamic scaling: phản ứng real-time dựa trên CloudWatch metrics (CPU utilization, memory, request count).
- Phù hợp với sudden unpredictable traffic: khi traffic lên → scale out; khi traffic xuống → scale in.
- Cost-effective: chỉ scale khi cần.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Manual scaling: phải can thiệp thủ công mỗi lần traffic tăng → không kịp thời.

**❌ Đáp án B:**
- Predictive scaling: dựa trên historical pattern → không hiệu quả cho random increases.

**❌ Đáp án D:**
- Schedule scaling: dựa trên fixed schedule → không biết trước random days.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Unpredictable traffic → Dynamic scaling (reactive). Predictive = historical. Schedule = fixed. Manual = slow."*
