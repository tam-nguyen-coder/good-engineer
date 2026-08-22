# Question #594 - Topic 1

A company plans to migrate to AWS and use Amazon EC2 On-Demand Instances for its application. During the migration testing phase, a technical team observes that the application takes a long time to launch and load memory to become fully productive. Which solution will reduce the launch time of the application during the next testing phase?

## Options

**A.** Launch two or more EC2 On-Demand Instances. Turn on auto scaling features and make the EC2 On-Demand Instances available during the next testing phase.

**B.** Launch EC2 Spot Instances to support the application and to scale the application so it is available during the next testing phase.

**C.** Launch the EC2 On-Demand Instances with hibernation turned on. Configure EC2 Auto Scaling warm pools during the next testing phase.

**D.** Launch EC2 On-Demand Instances with Capacity Reservations. Start additional EC2 instances during the next testing phase.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 On-Demand, application mất nhiều thời gian launch và load memory để ready.
- **Existing Resources:** EC2 On-Demand Instances.
- **Current Issue/Goal:** Giảm launch time trong testing phase.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `takes a long time to launch and load memory` | Hibernation: giữ nguyên memory state, resume nhanh. |
| `Auto Scaling warm pools` | Pre-initialized instances, sẵn sàng ngay khi cần. |
| `hibernation` | Stop instance → preserve memory → resume nhanh hơn boot từ đầu. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Reduce launch time
- **Constraints:** EC2 On-Demand, testing phase

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Hibernation: EC2 instance được "ngủ đông", memory preserved → resume nhanh (không cần load lại memory).
- Warm pools: ASG duy trì pre-initialized instances (đã launch nhưng không trong service) → sẵn sàng ngay khi cần scale.
- Kết hợp: launch time giảm đáng kể.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Auto scaling không tự giải quyết long launch time; chỉ scale số lượng.

**❌ Đáp án B:**
- Spot Instances: có thể bị reclaim, không đảm bảo. Không giải quyết long launch time.

**❌ Đáp án D:**
- Capacity Reservations: guarantee capacity nhưng không giảm launch time.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Long launch time → Hibernation (preserve memory) + Warm pools (pre-initialized). Capacity Reservations ≠ faster launch."*
