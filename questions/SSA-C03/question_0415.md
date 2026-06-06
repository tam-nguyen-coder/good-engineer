# Question #415 - Topic 1

A company is storing petabytes of data in Amazon S3 Standard. The data is stored in multiple S3 buckets and is accessed with varying frequency. The company does not know access patterns for all the data. The company needs to implement a solution for each S3 bucket to optimize the cost of S3 usage. Which solution will meet these requirements with the MOST operational efficiency?

## Options

**A.** Create an S3 Lifecycle configuration with a rule to transition the objects in the S3 bucket to S3 Intelligent-Tiering.

**B.** Use the S3 storage class analysis tool to determine the correct tier for each object in the S3 bucket. Move each object to the identified storage tier.

**C.** Create an S3 Lifecycle configuration with a rule to transition the objects in the S3 bucket to S3 Glacier Instant Retrieval.

**D.** Create an S3 Lifecycle configuration with a rule to transition the objects in the S3 bucket to S3 One Zone-Infrequent Access (S3 One Zone- IA).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Petabytes in S3 Standard, varying access frequency, unknown patterns. Optimize cost.
- **Existing Resources:** Multiple S3 buckets with data in S3 Standard.
- **Current Issue/Goal:** Cost optimization for unknown access patterns.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `does not know access patterns` | Intelligent-Tiering: tự động move data giữa tiers dựa trên access. |
| `most operational efficiency` | Set and forget, không cần phân tích. |
| `Intelligent-Tiering` | 4 tiers: Frequent, Infrequent, Archive Instant, Archive (optional). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization / Operational efficiency
- **Constraints:** Unknown access patterns, petabytes of data

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Intelligent-Tiering: tự động monitor access pattern và move objects giữa tiers.
- No retrieval cost, no minimum storage duration.
- Operational efficiency cao: chỉ cần 1 lifecycle rule, không cần manual analysis.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Storage class analysis: chỉ phân tích, không tự động move. Cần manual action → không operational efficiency.

**❌ Đáp án C:**
- Glacier Instant Retrieval: cho data biết trước là lạnh nhưng cần truy xuất nhanh. Không phù hợp khi chưa rõ pattern.

**❌ Đáp án D:**
- One Zone-IA: không durable (single AZ), rủi ro mất data nếu AZ fails.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Unknown access pattern → S3 Intelligent-Tiering (auto, set and forget)."*

