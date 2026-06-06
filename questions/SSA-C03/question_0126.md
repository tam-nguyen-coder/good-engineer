# Question #126 - Topic 1

A solutions architect needs to implement a solution to reduce a company's storage costs. All the company's data is in the Amazon S3 Standard storage class. The company must keep all data for at least 25 years. Data from the most recent 2 years must be highly available and immediately retrievable. Which solution will meet these requirements?

## Options

**A.** Set up an S3 Lifecycle policy to transition objects to S3 Glacier Deep Archive immediately.

**B.** Set up an S3 Lifecycle policy to transition objects to S3 Glacier Deep Archive after 2 years.

**C.** Use S3 Intelligent-Tiering. Activate the archiving option to ensure that data is archived in S3 Glacier Deep Archive.

**D.** Set up an S3 Lifecycle policy to transition objects to S3 One Zone-Infrequent Access (S3 One Zone-IA) immediately and to S3 Glacier Deep Archive after 2 years.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 Standard, keep 25 years. First 2 years: HA + immediate retrieval. After 2 years: cost savings.
- **Existing Resources:** S3 Standard.
- **Current Issue/Goal:** Reduce costs, keep 2 years hot, then archive.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highly available and immediately retrievable` | S3 Standard (first 2 years) |
| `keep all data for at least 25 years` | Cần archive rẻ → **Glacier Deep Archive** |
| `reduce storage costs` | Lifecycle policy |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization + Lifecycle
- **Constraints:** 2 years hot, 25 years total

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **S3 Standard** cho 2 năm đầu — highly available, immediately retrievable.
- **Lifecycle → S3 Glacier Deep Archive after 2 years** — rẻ nhất cho archival (25 năm).
- Glacier Deep Archive phù hợp cho data không cần truy cập thường xuyên.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Move immediately to Deep Archive — không đáp ứng "immediately retrievable" cho 2 năm đầu.

**❌ Đáp án C:**
- Intelligent-Tiering với archiving — có thể không cost-effective bằng lifecycle policy rõ ràng.

**❌ Đáp án D:**
- **S3 One Zone-IA** — không highly available (single AZ). Không phù hợp cho "highly available".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Standard (2 years) → Glacier Deep Archive (23 years) = cost-effective for long-term retention"*
