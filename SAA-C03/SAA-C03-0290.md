# Question #290 - Topic 1

A company hosts a web application on multiple Amazon EC2 instances. The EC2 instances are in an Auto Scaling group that scales in response to user demand. The company wants to optimize cost savings without making a long-term commitment. Which EC2 instance purchasing option should a solutions architect recommend to meet these requirements?

## Options

**A.** Dedicated Instances only

**B.** On-Demand Instances only

**C.** A mix of On-Demand Instances and Spot Instances

**D.** A mix of On-Demand Instances and Reserved Instances

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Auto Scaling group web app, cần tối ưu cost nhưng không muốn long-term commitment.
- **Existing Resources:** Auto Scaling group with EC2 instances.
- **Current Issue/Goal:** Cost savings without long-term commitment.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `without making a long-term commitment` | Không thể dùng Reserved Instances (1-3 year term). |
| `Auto Scaling group` | Có thể scale in/out → linh hoạt về số lượng instances. |
| `Spot Instances` | Giá rẻ hơn On-Demand đến 90%, không có long-term commitment, có thể bị reclaim (interruptible). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which purchasing option
- **Constraints:** Cost savings, no long-term commitment, Auto Scaling

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Mix On-Demand + Spot: On-Demand đảm bảo baseline capacity không bị gián đoạn, Spot dùng cho phần capacity linh hoạt (có thể scale lên với chi phí thấp).
- Spot Instances không yêu cầu long-term commitment và tiết kiệm đến 90% so với On-Demand.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Dedicated Instances đắt nhất (dành cho compliance/bare-metal requirements), không tối ưu cost.

**❌ Đáp án B:**
- On-Demand only đơn giản nhưng không tối ưu cost bằng mix với Spot.

**❌ Đáp án D:**
- Reserved Instances yêu cầu 1-3 năm commitment → không phù hợp với yêu cầu "without long-term commitment".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"No long-term commitment → Spot + On-Demand (not Reserved). Auto Scaling + Spot = tiết kiệm tối đa."*
