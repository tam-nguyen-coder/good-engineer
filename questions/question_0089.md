# Question #89 - Topic 1

A company uses Amazon S3 to store its confidential audit documents. The S3 bucket uses bucket policies to restrict access to audit team IAM user credentials according to the principle of least privilege. Company managers are worried about accidental deletion of documents in the S3 bucket and want a more secure solution. What should a solutions architect do to secure the audit documents?

## Options

**A.** Enable the versioning and MFA Delete features on the S3 bucket.

**B.** Enable multi-factor authentication (MFA) on the IAM user credentials for each audit team IAM user account.

**C.** Add an S3 Lifecycle policy to the audit team's IAM user accounts to deny the s3:DeleteObject action during audit dates.

**D.** Use AWS Key Management Service (AWS KMS) to encrypt the S3 bucket and restrict audit team IAM user accounts from accessing the KMS key.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 bucket chứa audit documents, bucket policy restrict access. Lo ngại accidental deletion.
- **Existing Resources:** S3 bucket, bucket policies.
- **Current Issue/Goal:** Protect against accidental deletion.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `accidental deletion` | Cần **MFA Delete** + Versioning |
| `more secure solution` | Thêm lớp bảo vệ |
| `audit documents` | Quan trọng, cần bảo vệ |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Data protection
- **Constraints:** Prevent accidental deletion

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3 Versioning** — giữ tất cả versions, có thể restore nếu bị delete.
- **MFA Delete** — yêu cầu MFA token để delete objects, chống accidental/malicious deletion.
- Kết hợp: versioning cho phép restore, MFA Delete ngăn delete không authorized.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- MFA trên IAM user — bảo vệ login nhưng không directly prevent S3 deletion.

**❌ Đáp án C:**
- Lifecycle policy không thể deny actions — chỉ tự động move/delete objects.

**❌ Đáp án D:**
- KMS ngăn đọc/decrypt, không ngăn delete objects.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"MFA Delete + Versioning = protection against accidental/malicious deletion. KMS = encryption, not deletion"*
