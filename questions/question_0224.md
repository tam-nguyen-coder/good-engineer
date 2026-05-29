# Question #224 - Topic 1

A company recently migrated its web application to AWS by rehosting the application on Amazon EC2 instances in a single AWS Region. The company wants to redesign its application architecture to be highly available and fault tolerant. Traffic must reach all running EC2 instances randomly. Which combination of steps should the company take to meet these requirements? (Choose two.)

## Options

**A.** Create an Amazon Route 53 failover routing policy.

**B.** Create an Amazon Route 53 weighted routing policy.

**C.** Create an Amazon Route 53 multivalue answer routing policy.

**D.** Launch three EC2 instances: two instances in one Availability Zone and one instance in another Availability Zone.

**E.** Launch four EC2 instances: two instances in one Availability Zone and two instances in another Availability Zone.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app on EC2 in single AZ. Redesign for HA + fault tolerant. Traffic randomly distributed.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Multi-AZ + random routing.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highly available and fault tolerant` | **Multi-AZ** (2 AZs tối thiểu) |
| `reach all running EC2 instances randomly` | **Route 53 multivalue answer** (random routing) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability / DNS
- **Constraints:** Chọn 2, HA, random distribution

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C và E**

**Giải thích:**
- **C: Multivalue answer routing** — Route 53 trả về up to 8 healthy records, randomly ordered → client chọn ngẫu nhiên.
- **E: 4 EC2 instances (2 per AZ)** — balanced across 2 AZs → HA, fault tolerant.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Failover routing — chỉ gửi traffic đến 1 record (active-passive), không random.

**❌ Đáp án B:**
- Weighted routing — distribute theo weight, không random.

**❌ Đáp án D:**
- 3 instances (2+1) — không balanced, ít fault tolerant hơn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multivalue answer = random routing. Failover = active-passive. 2 AZs balanced = HA"*
