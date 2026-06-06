# Question #581 - Topic 1

A company runs a stateful production application on Amazon EC2 instances. The application requires at least two EC2 instances to always be running. A solutions architect needs to design a highly available and fault-tolerant architecture for the application. The solutions architect creates an Auto Scaling group of EC2 instances. Which set of additional steps should the solutions architect take to meet these requirements?

## Options

**A.** Set the Auto Scaling group's minimum capacity to two. Deploy one On-Demand Instance in one Availability Zone and one On-Demand Instance in a second Availability Zone.

**B.** Set the Auto Scaling group's minimum capacity to four. Deploy two On-Demand Instances in one Availability Zone and two On-Demand Instances in a second Availability Zone.

**C.** Set the Auto Scaling group's minimum capacity to two. Deploy four Spot Instances in one Availability Zone.

**D.** Set the Auto Scaling group's minimum capacity to four. Deploy two On-Demand Instances in one Availability Zone and two Spot Instances in a second Availability Zone.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Stateful production app, need at least 2 EC2 running always, HA + fault-tolerant.
- **Existing Resources:** Auto Scaling group.
- **Current Issue/Goal:** Ensure HA + fault-tolerant with ASG.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `at least two EC2 instances to always be running` | Min capacity = 2. |
| `highly available and fault-tolerant` | Instances phải ở 2 AZ khác nhau (AZ failure không ảnh hưởng tất cả). |
| `On-Demand` | Đảm bảo capacity (không bị reclaim như Spot). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Highly available + fault-tolerant
- **Constraints:** Min 2 instances, stateful production

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Min capacity = 2 đảm bảo luôn có 2 instances.
- Deploy 1 instance ở AZ1 + 1 instance ở AZ2 → fault-tolerant khi 1 AZ fails.
- On-Demand: đảm bảo capacity (Spot có thể bị reclaim).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Min capacity = 4: thừa, tốn thêm chi phí. Yêu cầu chỉ cần 2 instances.

**❌ Đáp án C:**
- Spot Instances: có thể bị reclaim (EC2回收) → không đảm bảo "always running".
- 1 AZ: single point of failure.

**❌ Đáp án D:**
- Min capacity = 4: thừa. Spot Instances: không reliable cho production stateful app.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Min 2 + spread 2 AZ + On-Demand = HA. Spot = not for stateful prod. Single AZ = not fault-tolerant."*
