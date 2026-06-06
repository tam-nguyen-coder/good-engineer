# Question #179 - Topic 1

A solutions architect needs to securely store a database user name and password that an application uses to access an Amazon RDS DB instance. The application that accesses the database runs on an Amazon EC2 instance. The solutions architect wants to create a secure parameter in AWS Systems Manager Parameter Store. What should the solutions architect do to meet this requirement?

## Options

**A.** Create an IAM role that has read access to the Parameter Store parameter. Allow Decrypt access to an AWS Key Management Service (AWS KMS) key that is used to encrypt the parameter. Assign this IAM role to the EC2 instance.

**B.** Create an IAM policy that allows read access to the Parameter Store parameter. Allow Decrypt access to an AWS Key Management Service (AWS KMS) key that is used to encrypt the parameter. Assign this IAM policy to the EC2 instance.

**C.** Create an IAM trust relationship between the Parameter Store parameter and the EC2 instance. Specify Amazon RDS as a principal in the trust policy.

**D.** Create an IAM trust relationship between the DB instance and the EC2 instance. Specify Systems Manager as a principal in the trust policy.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Store DB credentials in SSM Parameter Store. EC2 app needs to read them securely.
- **Existing Resources:** EC2 instance, RDS DB instance.
- **Current Issue/Goal:** Secure credential storage and retrieval.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `AWS Systems Manager Parameter Store` | Lưu secret parameters |
| `IAM role` | Gắn role vào EC2 instance profile |
| `KMS key` | Encrypt/decrypt parameter |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Secrets management
- **Constraints:** EC2 access, secure

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **IAM role** — attach role vào EC2 instance profile.
- Role cần: `ssm:GetParameter` (read) + `kms:Decrypt` (nếu parameter được KMS-encrypted).
- Best practice: dùng IAM role, không dùng IAM user.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- IAM policy không được "assign" trực tiếp vào EC2 — cần IAM role.

**❌ Đáp án C:**
- Trust relationship — dùng cho IAM roles (assume role), không phải parameters.

**❌ Đáp án D:**
- Trust relationship giữa DB và EC2 — không đúng, SSM không phải principal.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SSM Parameter Store + IAM role + KMS = secure secrets. IAM policy = not assignable to EC2"*
