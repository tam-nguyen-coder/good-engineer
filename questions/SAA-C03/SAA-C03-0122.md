# Question #122 - Topic 1

A company wants to build a scalable key management infrastructure to support developers who need to encrypt data in their applications. What should a solutions architect do to reduce the operational burden?

## Options

**A.** Use multi-factor authentication (MFA) to protect the encryption keys.

**B.** Use AWS Key Management Service (AWS KMS) to protect the encryption keys.

**C.** Use AWS Certificate Manager (ACM) to create, store, and assign the encryption keys.

**D.** Use an IAM policy to limit the scope of users who have access permissions to protect the encryption keys.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Developers cần encrypt data. Cần scalable key management với minimal operational burden.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Reduce operational burden for key management.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `scalable key management` | Cần **AWS KMS** |
| `reduce the operational burden` | Managed key service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Key management
- **Constraints:** Scalable, reduce burden

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **AWS KMS** — managed service cho encryption keys.
- Tích hợp với nhiều AWS services (S3, EBS, RDS, Lambda).
- Tự động key rotation, access control, audit logging.
- Developers dùng KMS API mà không cần quản lý key infrastructure.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- MFA là authentication mechanism, không phải key management.

**❌ Đáp án C:**
- **ACM** quản lý SSL/TLS certificates, không phải encryption keys cho application data.

**❌ Đáp án D:**
- IAM policy kiểm soát access, không quản lý keys.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"KMS = managed encryption keys. ACM = SSL/TLS certs. IAM = access control"*
