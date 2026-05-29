# Question #678 - Topic 1

A company stores sensitive data in Amazon S3. A solutions architect needs to create an encryption solution. The company needs to fully control the ability of users to create, rotate, and disable encryption keys with minimal effort for any data that must be encrypted. Which solution will meet these requirements?

## Options

**A.** Use default server-side encryption with Amazon S3 managed encryption keys (SSE-S3) to store the sensitive data.

**B.** Create a customer managed key by using AWS Key Management Service (AWS KMS). Use the new key to encrypt the S3 objects by using server-side encryption with AWS KMS keys (SSE-KMS).

**C.** Create an AWS managed key by using AWS Key Management Service (AWS KMS). Use the new key to encrypt the S3 objects by using server-side encryption with AWS KMS keys (SSE-KMS).

**D.** Download S3 objects to an Amazon EC2 instance. Encrypt the objects by using customer managed keys. Upload the encrypted objects back into Amazon S3.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Sensitive data in S3. Need full control over key lifecycle (create, rotate, disable). Minimal effort.
- **Existing Resources:** S3 bucket with sensitive data.
- **Current Issue/Goal:** Encryption with full key control.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `fully control the ability to create, rotate, and disable` | Customer managed key (CMK) cho phép custom key policy, rotation, disabling. |
| `minimal effort` | SSE-KMS với customer managed key (managed by KMS). |
| `SSE-S3` | AWS manages keys, không có control. |
| `AWS managed key` | KMS manages key policy, limited control. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Full key control, minimal effort

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Customer managed key (CMK) trong KMS: bạn tự quản lý key policy, có thể enable/disable, set rotation schedule.
- SSE-KMS: tích hợp sẵn với S3, chỉ cần specify KMS key ID.
- Minimal effort: KMS manages encryption operations, bạn chỉ quản lý key lifecycle.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- SSE-S3: AWS fully manages keys, không có control để rotate, disable keys.

**❌ Đáp án C:**
- AWS managed key: KMS manages key policy, bạn không thể control rotation schedule hay disable key dễ dàng.

**❌ Đáp án D:**
- EC2 client-side encryption: operational overhead rất cao (manage encryption/decryption manually).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Full key control → Customer Managed Key (CMK) + SSE-KMS. SSE-S3 = no control."*
