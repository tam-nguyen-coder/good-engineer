# Question #425 - Topic 1

A company uses high block storage capacity to runs its workloads on premises. The company's daily peak input and output transactions per second are not more than 15,000 IOPS. The company wants to migrate the workloads to Amazon EC2 and to provision disk performance independent of storage capacity. Which Amazon Elastic Block Store (Amazon EBS) volume type will meet these requirements MOST cost-effectively?

## Options

**A.** GP2 volume type

**B.** io2 volume type

**C.** GP3 volume type

**D.** io1 volume type

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** High storage capacity, peak 15,000 IOPS. Need performance independent of capacity. Most cost-effective.
- **Existing Resources:** On-prem workloads.
- **Current Issue/Goal:** Select EBS volume type: IOPS independent of size.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `disk performance independent of storage capacity` | GP3: IOPS and throughput provisioned separately from size. |
| `not more than 15,000 IOPS` | GP3 max 16,000 IOPS. |
| `most cost-effectively` | GP3: rẻ hơn io2/io1. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization / Storage
- **Constraints:** IOPS independent of capacity, <= 15,000 IOPS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- GP3: baseline 3,000 IOPS, có thể provision thêm IOPS (tối đa 16,000) và throughput độc lập với volume size.
- Cost rẻ hơn io2/io1 cho cùng IOPS level.
- Phù hợp cho peak 15,000 IOPS.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- GP2: IOPS tied to volume size (3 IOPS/GB). Muốn 15,000 IOPS cần 5TB volume → tốn kém, không độc lập.

**❌ Đáp án B:**
- io2: Provisioned IOPS, độc lập với size, nhưng đắt hơn GP3.

**❌ Đáp án D:**
- io1: Provisioned IOPS, legacy, đắt hơn io2 và GP3.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"IOPS độc lập size → GP3 (up to 16K IOPS, rẻ nhất) or io2 (higher IOPS, đắt hơn)."*