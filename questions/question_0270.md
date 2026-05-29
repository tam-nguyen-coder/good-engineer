# Question #270 - Topic 1

A company is using a centralized AWS account to store log data in various Amazon S3 buckets. A solutions architect needs to ensure that the data is encrypted at rest before the data is uploaded to the S3 buckets. The data also must be encrypted in transit. Which solution meets these requirements?

## Options

**A.** Use client-side encryption to encrypt the data that is being uploaded to the S3 buckets.

**B.** Use server-side encryption to encrypt the data that is being uploaded to the S3 buckets.

**C.** Create bucket policies that require the use of server-side encryption with S3 managed encryption keys (SSE-S3) for S3 uploads.

**D.** Enable the security option to encrypt the S3 buckets through the use of a default AWS Key Management Service (AWS KMS) key.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Centralized log data in S3. Encrypt at rest (before upload) + in transit.
- **Existing Resources:** S3 buckets.
- **Current Issue/Goal:** Client-side encryption + HTTPS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypted at rest before the data is uploaded` | **Client-side encryption** — encrypt trước khi gửi |
| `encrypted in transit` | HTTPS (implicit with client-side encryption) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Encryption
- **Constraints:** Encrypt before upload + in transit

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Client-side encryption** — mã hoá dữ liệu trước khi upload lên S3 → encrypted at rest trước khi đến AWS.
- Encrypted in transit (HTTPS) — khi upload, data đã encrypted.
- AWS không có access đến encryption keys.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Server-side encryption — S3 encrypt sau khi nhận dữ liệu, không phải "trước khi upload".

**❌ Đáp án C:**
- Bucket policy SSE-S3 — yêu cầu SSE, nhưng encrypt sau khi upload.

**❌ Đáp án D:**
- Default KMS key — SSE-KMS, encrypt sau khi upload.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Client-side = encrypt before upload. SSE = encrypt after upload. 'Before uploaded' = client-side"*
