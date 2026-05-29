# Question #202 - Topic 1

A company is planning to move its data to an Amazon S3 bucket. The data must be encrypted when it is stored in the S3 bucket. Additionally, the encryption key must be automatically rotated every year. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Move the data to the S3 bucket. Use server-side encryption with Amazon S3 managed encryption keys (SSE-S3). Use the built-in key rotation behavior of SSE-S3 encryption keys.

**B.** Create an AWS Key Management Service (AWS KMS) customer managed key. Enable automatic key rotation. Set the S3 bucket's default encryption behavior to use the customer managed KMS key. Move the data to the S3 bucket.

**C.** Create an AWS Key Management Service (AWS KMS) customer managed key. Set the S3 bucket's default encryption behavior to use the customer managed KMS key. Move the data to the S3 bucket. Manually rotate the KMS key every year.

**D.** Encrypt the data with customer key material before moving the data to the S3 bucket. Create an AWS Key Management Service (AWS KMS) key without key material. Import the customer key material into the KMS key. Enable automatic key rotation.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Data → S3, encrypt at rest, auto rotate key yearly.
- **Existing Resources:** None.
- **Current Issue/Goal:** Encryption + key rotation, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `least operational overhead` | **SSE-S3** (AWS managed, built-in rotation) |
| `automatically rotated every year` | SSE-S3 keys tự động rotated |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Encryption
- **Constraints:** Encrypt at rest, auto key rotation, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **SSE-S3** — server-side encryption, S3 tự quản lý keys.
- Built-in key rotation — AWS tự động rotate keys, không cần cấu hình.
- Least overhead — không cần tạo/manage KMS keys.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- KMS CMK + auto rotation — thêm overhead (tạo key, cấu hình, quản lý).

**❌ Đáp án C:**
- KMS CMK + manual rotation — operational overhead cao.

**❌ Đáp án D:**
- Imported key material — không thể auto-rotate, phải re-import manually.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SSE-S3 = least overhead (auto key rotation). KMS CMK = more control but more overhead"*
