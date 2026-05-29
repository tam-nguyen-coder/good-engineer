# Question #321 - Topic 1

What should a solutions architect do to ensure that all objects uploaded to an Amazon S3 bucket are encrypted?

## Options

**A.** Update the bucket policy to deny if the PutObject does not have an s3:x-amz-acl header set.

**B.** Update the bucket policy to deny if the PutObject does not have an s3:x-amz-acl header set to private.

**C.** Update the bucket policy to deny if the PutObject does not have an aws:SecureTransport header set to true.

**D.** Update the bucket policy to deny if the PutObject does not have an x-amz-server-side-encryption header set.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần enforce encryption cho tất cả objects upload lên S3 bucket.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Bắt buộc mọi PutObject phải có encryption.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypted` | Server-side encryption (SSE-S3, SSE-KMS, SSE-C). |
| `x-amz-server-side-encryption` | Header trong PutObject request chỉ định encryption (AES256, aws:kms). |
| `bucket policy` | IAM policy gán trên bucket để enforce encryption. |
| `s3:x-amz-acl` | Header cho access control, không liên quan encryption. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution ensures encryption
- **Constraints:** All uploaded objects must be encrypted

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Bucket policy với condition deny nếu PutObject không có header `x-amz-server-side-encryption` → bắt buộc mọi upload phải chỉ định encryption.
- Ngăn chặn uploads không được mã hóa.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- s3:x-amz-acl header kiểm soát ACL (public/private), không liên quan encryption.

**❌ Đáp án B:**
- Tương tự A, ACL không phải encryption.

**❌ Đáp án C:**
- aws:SecureTransport enforce HTTPS (in-transit encryption), không phải at-rest encryption.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Enforce encryption at rest → bucket policy deny PUT without x-amz-server-side-encryption. SecureTransport = in-transit."*
