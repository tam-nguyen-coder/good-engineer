# Question #359 - Topic 1

A hospital needs to store patient records in an Amazon S3 bucket. The hospital's compliance team must ensure that all protected health information (PHI) is encrypted in transit and at rest. The compliance team must administer the encryption key for data at rest. Which solution will meet these requirements?

## Options

**A.** Create a public SSL/TLS certificate in AWS Certificate Manager (ACM). Associate the certificate with Amazon S3. Configure default encryption for each S3 bucket to use server-side encryption with AWS KMS keys (SSE-KMS). Assign the compliance team to manage the KMS keys.

**B.** Use the aws:SecureTransport condition on S3 bucket policies to allow only encrypted connections over HTTPS (TLS). Configure default encryption for each S3 bucket to use server-side encryption with S3 managed encryption keys (SSE-S3). Assign the compliance team to manage the SSE-S3 keys.

**C.** Use the aws:SecureTransport condition on S3 bucket policies to allow only encrypted connections over HTTPS (TLS). Configure default encryption for each S3 bucket to use server-side encryption with AWS KMS keys (SSE-KMS). Assign the compliance team to manage the KMS keys.

**D.** Use the aws:SecureTransport condition on S3 bucket policies to allow only encrypted connections over HTTPS (TLS). Use Amazon Macie to protect the sensitive data that is stored in Amazon S3. Assign the compliance team to manage Macie.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Patient records (PHI) in S3. Cần encryption in transit + at rest. Compliance team administers encryption keys.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Enforce encryption in transit + at rest, team manages keys.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypted in transit` | aws:SecureTransport condition enforce HTTPS. |
| `encrypted at rest` | SSE-KMS (server-side encryption with KMS). |
| `administer the encryption key` | KMS → compliance team quản lý KMS keys (IAM/KMS policy). |
| `SSE-S3` | S3 manages keys → compliance team không thể administer. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Encryption in transit + at rest, team manages keys

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **In transit:** aws:SecureTransport bucket policy condition → deny requests không qua HTTPS/TLS.
- **At rest:** SSE-KMS default encryption → compliance team quản lý KMS key (IAM/KMS key policy).
- KMS cho phép team administer keys (create, rotate, grant permissions).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ACM certificate không thể "associate with Amazon S3" (S3 không dùng ACM). SSL chỉ enforce qua bucket policy.

**❌ Đáp án B:**
- SSE-S3: S3 quản lý keys, compliance team không thể administer keys.

**❌ Đáp án D:**
- Macie: data classification/PII detection, không encrypt dữ liệu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"In transit → SecureTransport bucket policy. At rest + team manages keys → SSE-KMS. SSE-S3 = AWS manages keys."*
