# Question #330 - Topic 1

A company is planning to store data on Amazon RDS DB instances. The company must encrypt the data at rest. What should a solutions architect do to meet this requirement?

## Options

**A.** Create a key in AWS Key Management Service (AWS KMS). Enable encryption for the DB instances.

**B.** Create an encryption key. Store the key in AWS Secrets Manager. Use the key to encrypt the DB instances.

**C.** Generate a certificate in AWS Certificate Manager (ACM). Enable SSL/TLS on the DB instances by using the certificate.

**D.** Generate a certificate in AWS Identity and Access Management (IAM). Enable SSL/TLS on the DB instances by using the certificate.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS DB instances cần encryption at rest.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Enable encryption at rest cho RDS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypt the data at rest` | Dữ liệu lưu trên disk → RDS encryption với KMS key. |
| `AWS KMS` | Managed key service, RDS tích hợp KMS để encrypt at rest. |
| `Secrets Manager` | Quản lý secrets (passwords, API keys), không encrypt RDS. |
| `ACM` | SSL/TLS certificates cho in-transit encryption. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Encrypt data at rest
- **Constraints:** RDS, at rest encryption

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Create KMS key, enable RDS encryption bằng KMS key.
- RDS tự động encrypt storage, logs, snapshots, and replicas.
- KMS là AWS managed service, best practice cho encryption at rest.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Secrets Manager lưu secrets (credentials), không thể dùng để enable encryption cho RDS instances.

**❌ Đáp án C:**
- ACM SSL/TLS → encryption in transit (kết nối đến database), không phải at rest.

**❌ Đáp án D:**
- IAM không generate certificates. SSL/TLS là in-transit encryption.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS at rest encryption → KMS key. Secrets Manager = secrets. ACM = SSL/TLS (in-transit)."*
