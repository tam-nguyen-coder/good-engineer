# Question #86 - Topic 1

A company has several web servers that need to frequently access a common Amazon RDS MySQL Multi-AZ DB instance. The company wants a secure method for the web servers to connect to the database while meeting a security requirement to rotate user credentials frequently. Which solution meets these requirements?

## Options

**A.** Store the database user credentials in AWS Secrets Manager. Grant the necessary IAM permissions to allow the web servers to access AWS Secrets Manager.

**B.** Store the database user credentials in AWS Systems Manager OpsCenter. Grant the necessary IAM permissions to allow the web servers to access OpsCenter.

**C.** Store the database user credentials in a secure Amazon S3 bucket. Grant the necessary IAM permissions to allow the web servers to retrieve credentials and access the database.

**D.** Store the database user credentials in files encrypted with AWS Key Management Service (AWS KMS) on the web server file system. The web server should be able to decrypt the files and access the database.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web servers access RDS MySQL Multi-AZ, cần rotate credentials frequently.
- **Existing Resources:** EC2 web servers, RDS MySQL Multi-AZ.
- **Current Issue/Goal:** Secure credential storage + frequent rotation.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `rotate user credentials frequently` | Built-in rotation → **Secrets Manager** |
| `secure method` | Managed secrets service |
| `several web servers` | IAM role for EC2 to access secrets |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security + Credential management
- **Constraints:** Rotate frequently, secure

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **AWS Secrets Manager** — lưu credentials an toàn, **built-in automatic rotation** cho RDS.
- IAM role gắn cho web servers → retrieve credentials mà không cần hardcode.
- Rotation được quản lý tự động.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **OpsCenter** dùng để quản lý operational issues, không phải secrets store.

**❌ Đáp án C:**
- S3 không có built-in rotation — phải tự xây dựng rotation mechanism.

**❌ Đáp án D:**
- Encrypted files trên file system — khó rotate, khó quản lý ở scale nhiều servers.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Secrets Manager = credentials + auto rotation. S3/File system = no built-in rotation"*
