# Question #106 - Topic 1

A company is preparing to store confidential data in Amazon S3. For compliance reasons, the data must be encrypted at rest. Encryption key usage must be logged for auditing purposes. Keys must be rotated every year. Which solution meets these requirements and is the MOST operationally efficient?

## Options

**A.** Server-side encryption with customer-provided keys (SSE-C)

**B.** Server-side encryption with Amazon S3 managed keys (SSE-S3)

**C.** Server-side encryption with AWS KMS keys (SSE-KMS) with manual rotation

**D.** Server-side encryption with AWS KMS keys (SSE-KMS) with automatic rotation

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Confidential data in S3, cần encryption at rest + key usage logging + yearly rotation.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Compliance: encrypt, audit, rotate.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `key usage must be logged` | **KMS** integrates with CloudTrail |
| `rotated every year` | **KMS automatic rotation** (hàng năm) |
| `most operationally efficient` | Managed, không manual |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Encryption
- **Constraints:** Key logging, rotation, efficient

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **SSE-KMS** — encryption với KMS keys, CloudTrail ghi lại mọi API call (khi nào, ai dùng key nào).
- **Automatic rotation** — KMS tự động rotate key mỗi năm, không cần can thiệp.
- SSE-S3 thiếu CloudTrail logging cho key usage.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **SSE-C** — customer cung cấp key, không rotation, không audit logging.

**❌ Đáp án B:**
- **SSE-S3** — Amazon quản lý key, không có CloudTrail logging cho key usage, không rotate visibility.

**❌ Đáp án C:**
- **SSE-KMS manual rotation** — đúng cho logging nhưng manual rotation = operational overhead.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SSE-KMS = CloudTrail logging + automatic rotation. SSE-S3 = no audit. SSE-C = self-managed"*
