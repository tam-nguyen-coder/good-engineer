# Question #585 - Topic 1

A solutions architect is designing a disaster recovery (DR) strategy to provide Amazon EC2 capacity in a failover AWS Region. Business requirements state that the DR strategy must meet capacity in the failover Region. Which solution will meet these requirements?

## Options

**A.** Purchase On-Demand Instances in the failover Region.

**B.** Purchase an EC2 Savings Plan in the failover Region.

**C.** Purchase regional Reserved Instances in the failover Region.

**D.** Purchase a Capacity Reservation in the failover Region.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DR strategy, cần đảm bảo có EC2 capacity ở failover Region.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Guarantee EC2 capacity in failover Region.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `must meet capacity` | Cần guarantee capacity (không thể bị "out of capacity"). |
| `Capacity Reservation` | Reserve EC2 capacity in specific AZ, guarantee available when needed. |
| `failover Region` | Region dự phòng, cần đảm bảo có capacity khi DR event xảy ra. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** DR strategy → capacity guarantee
- **Constraints:** Must meet capacity in failover Region

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- On-Demand Capacity Reservation: guarantee EC2 capacity sẽ available khi cần.
- Không cần trả trước, chỉ pay when you run instances.
- Đảm bảo capacity trong failover Region khi DR event xảy ra.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- On-Demand Instances: không guarantee capacity. AWS có thể hết capacity trong 1 AZ.

**❌ Đáp án B:**
- Savings Plan: giảm giá nhưng không guarantee capacity.

**❌ Đáp án C:**
- Regional Reserved Instances: giảm giá + ưu tiên capacity nhưng không guarantee (không giống Capacity Reservation).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Guarantee capacity → Capacity Reservation. RI/Savings Plan = discount only, not guaranteed."*
