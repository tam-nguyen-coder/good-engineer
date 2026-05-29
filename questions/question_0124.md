# Question #124 - Topic 1

A company has a highly dynamic batch processing job that uses many Amazon EC2 instances to complete it. The job is stateless in nature, can be started and stopped at any given time with no negative impact, and typically takes upwards of 60 minutes total to complete. The company has asked a solutions architect to design a scalable and cost-effective solution that meets the requirements of the job. What should the solutions architect recommend?

## Options

**A.** Implement EC2 Spot Instances.

**B.** Purchase EC2 Reserved Instances.

**C.** Implement EC2 On-Demand Instances.

**D.** Implement the processing on AWS Lambda.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Batch processing, stateless, can be interrupted, 60+ minutes.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Scalable, cost-effective batch processing.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `stateless` | Có thể restart, không sợ mất state |
| `can be started and stopped at any time with no negative impact` | **Spot Instances** — có thể bị terminate |
| `upwards of 60 minutes` | Lambda max 15 min → không dùng được Lambda |
| `cost-effective` | Spot rẻ hơn On-Demand 60-90% |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Stateless, >60 min, fault-tolerant

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **EC2 Spot Instances** — tận dụng capacity dư thừa, giá rẻ hơn 60-90% so với On-Demand.
- **Stateless + interruptible** — job có thể restart nếu Spot bị thu hồi.
- **60+ minutes** — không thể dùng Lambda (max 15 phút).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **Reserved Instances** — cam kết 1-3 năm, không phù hợp cho batch job không thường xuyên.

**❌ Đáp án C:**
- **On-Demand** — đắt hơn Spot, không tận dụng được tính chất fault-tolerant của job.

**❌ Đáp án D:**
- **Lambda** — max 15 phút timeout, không đáp ứng "upwards of 60 minutes".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Spot = stateless + fault-tolerant batch. Lambda = max 15 min. Reserved = steady state 24/7"*
