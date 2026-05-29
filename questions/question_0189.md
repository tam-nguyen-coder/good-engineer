# Question #189 - Topic 1

A company needs to store contract documents. A contract lasts for 5 years. During the 5-year period, the company must ensure that the documents cannot be overwritten or deleted. The company needs to encrypt the documents at rest and rotate the encryption keys automatically every year. Which combination of steps should a solutions architect take to meet these requirements with the LEAST operational overhead? (Choose two.)

## Options

**A.** Store the documents in Amazon S3. Use S3 Object Lock in governance mode.

**B.** Store the documents in Amazon S3. Use S3 Object Lock in compliance mode.

**C.** Use server-side encryption with Amazon S3 managed encryption keys (SSE-S3). Configure key rotation.

**D.** Use server-side encryption with AWS Key Management Service (AWS KMS) customer managed keys. Configure key rotation.

**E.** Use server-side encryption with AWS Key Management Service (AWS KMS) customer provided (imported) keys. Configure key rotation.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Contract documents, 5-year retention, cannot be overwritten/deleted. Encrypt at rest, auto key rotation yearly.
- **Existing Resources:** None.
- **Current Issue/Goal:** Immutable storage + encryption with key rotation, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `cannot be overwritten or deleted` | **S3 Object Lock compliance mode** (even root can't delete) |
| `rotate the encryption keys automatically every year` | **KMS customer managed key** with auto rotation |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Compliance
- **Constraints:** Chọn 2, immutable, encryption, key rotation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và D**

**Giải thích:**
- **B: S3 Object Lock compliance mode** — không ai (kể cả root) có thể overwrite/delete objects trong retention period.
- **D: KMS customer managed key + auto rotation** — you control key rotation (enable annually), tách biệt với S3.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Governance mode — users có thể delete nếu có S3:BypassGovernanceRetention permission.

**❌ Đáp án C:**
- SSE-S3 — không có "configure key rotation" option (S3 tự quản lý).

**❌ Đáp án E:**
- KMS imported keys — không thể auto-rotate, phải re-import manually.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Object Lock compliance = truly immutable. KMS CMK = you control rotation. SSE-S3 = AWS manages keys"*
