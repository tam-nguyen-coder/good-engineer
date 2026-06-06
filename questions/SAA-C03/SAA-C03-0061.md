# Question #61 - Topic 1

A company is developing a two-tier web application on AWS. The company's developers have deployed the application on an Amazon EC2 instance that connects directly to a backend Amazon RDS database. The company must not hardcode database credentials in the application. The company must also implement a solution to automatically rotate the database credentials on a regular basis. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Store the database credentials in the instance metadata. Use Amazon EventBridge (Amazon CloudWatch Events) rules to run a scheduled AWS Lambda function that updates the RDS credentials and instance metadata at the same time.

**B.** Store the database credentials in a configuration file in an encrypted Amazon S3 bucket. Use Amazon EventBridge (Amazon CloudWatch Events) rules to run a scheduled AWS Lambda function that updates the RDS credentials and the credentials in the configuration file at the same time. Use S3 Versioning to ensure the ability to fall back to previous values.

**C.** Store the database credentials as a secret in AWS Secrets Manager. Turn on automatic rotation for the secret. Attach the required permission to the EC2 role to grant access to the secret.

**D.** Store the database credentials as encrypted parameters in AWS Systems Manager Parameter Store. Turn on automatic rotation for the encrypted parameters. Attach the required permission to the EC2 role to grant access to the encrypted parameters.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 + RDS, không hardcode credentials, cần auto-rotate.
- **Existing Resources:** EC2 instance, RDS database.
- **Current Issue/Goal:** Secure credential management + auto-rotation, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `not hardcode database credentials` | Cần secrets management service |
| `automatically rotate` | Built-in rotation → Secrets Manager |
| `least operational overhead` | Managed service, không tự xây dựng rotation |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security + Operational overhead
- **Constraints:** No hardcoded creds, auto-rotation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **AWS Secrets Manager** có built-in **automatic rotation** cho RDS credentials — không cần tự viết Lambda.
- EC2 instance role được gắn policy để access secret → retrieve credentials tại runtime.
- **Least operational overhead** — rotation được quản lý hoàn toàn, chỉ cần cấu hình.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Instance metadata không phải secrets store, không có rotation, không an toàn.

**❌ Đáp án B:**
- S3 + Lambda rotation — phải tự viết rotation logic → operational overhead cao hơn Secrets Manager.

**❌ Đáp án D:**
- **Parameter Store** không có built-in automatic rotation (chỉ SecureString với KMS encryption, không tự động rotate).
- Secrets Manager mới có rotation feature.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Secrets Manager = auto rotation. Parameter Store = no auto rotation. Instance metadata = never store secrets"*
