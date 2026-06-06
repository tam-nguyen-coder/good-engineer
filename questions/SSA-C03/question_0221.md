# Question #221 - Topic 1

A company runs an application on a group of Amazon Linux EC2 instances. For compliance reasons, the company must retain all application log files for 7 years. The log files will be analyzed by a reporting tool that must be able to access all the files concurrently. Which storage solution meets these requirements MOST cost-effectively?

## Options

**A.** Amazon Elastic Block Store (Amazon EBS)

**B.** Amazon Elastic File System (Amazon EFS)

**C.** Amazon EC2 instance store

**D.** Amazon S3

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Linux EC2 instances, retain logs 7 years. Reporting tool needs concurrent access.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Cost-effective, shared, durable log storage.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `retain all application log files for 7 years` | Durable, long-term → **S3** |
| `access all the files concurrently` | Shared storage |
| `most cost-effectively` | S3 is cheapest for long-term |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / Cost optimization
- **Constraints:** Shared, durable, 7 years

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **S3** — 11 9's durability, concurrent access từ nhiều instances.
- Cost-effective cho long-term storage ($23/TB/month).
- Có thể dùng S3 Lifecycle để transition sang Glacier/Deep Archive sau thời gian.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EBS — không shared (single-attach), chi phí cao cho 7 năm.

**❌ Đáp án B:**
- EFS — shared nhưng đắt hơn S3 cho lưu trữ dài hạn.

**❌ Đáp án C:**
- Instance store — ephemeral, mất dữ liệu khi stop/terminate.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 = shared + durable + cheap for long-term. EBS = single-attach. Instance store = temporary"*
