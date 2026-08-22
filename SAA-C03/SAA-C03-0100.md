# Question #100 - Topic 1

A company's containerized application runs on an Amazon EC2 instance. The application needs to download security certificates before it can communicate with other business applications. The company wants a highly secure solution to encrypt and decrypt the certificates in near real time. The solution also needs to store data in highly available storage after the data is encrypted. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create AWS Secrets Manager secrets for encrypted certificates. Manually update the certificates as needed. Control access to the data by using fine-grained IAM access.

**B.** Create an AWS Lambda function that uses the Python cryptography library to receive and perform encryption operations. Store the function in an Amazon S3 bucket.

**C.** Create an AWS Key Management Service (AWS KMS) customer managed key. Allow the EC2 role to use the KMS key for encryption operations. Store the encrypted data on Amazon S3.

**D.** Create an AWS Key Management Service (AWS KMS) customer managed key. Allow the EC2 role to use the KMS key for encryption operations. Store the encrypted data on Amazon Elastic Block Store (Amazon EBS) volumes.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Containerized app on EC2, cần download security certs, encrypt/decrypt near real-time, highly available storage.
- **Existing Resources:** EC2 instance.
- **Current Issue/Goal:** Secure encryption + HA storage, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypt and decrypt the certificates in near real time` | Cần **KMS** — quản lý key tập trung |
| `highly available storage` | **S3** (multi-AZ) > EBS (single AZ) |
| `least operational overhead` | Managed service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security + Encryption
- **Constraints:** Near real-time encryption, HA storage

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **AWS KMS** — managed encryption service, encrypt/decrypt với low latency.
- **S3** — highly available (99.99% availability), durable (11 9's), cross-region replication option.
- IAM role cho EC2 → chỉ định quyền dùng KMS key.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Secrets Manager lưu secrets (credentials), không phải để encrypt/decrypt certificates.
- Manual update — operational overhead.

**❌ Đáp án B:**
- Lambda + Python crypto library — custom encryption, operational overhead (quản lý code, keys).

**❌ Đáp án D:**
- **EBS** là block storage trong 1 AZ — không highly available như S3 (multi-AZ).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"KMS = managed encryption. S3 = highly available storage. EBS = single AZ (not HA)"*
