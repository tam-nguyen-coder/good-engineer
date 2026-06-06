# Question #336 - Topic 1

A company hosts a multi-tier web application that uses an Amazon Aurora MySQL DB cluster for storage. The application tier is hosted on Amazon EC2 instances. The company's IT security guidelines mandate that the database credentials be encrypted and rotated every 14 days. What should a solutions architect do to meet this requirement with the LEAST operational effort?

## Options

**A.** Create a new AWS Key Management Service (AWS KMS) encryption key. Use AWS Secrets Manager to create a new secret that uses the KMS key with the appropriate credentials. Associate the secret with the Aurora DB cluster. Configure a custom rotation period of 14 days.

**B.** Create two parameters in AWS Systems Manager Parameter Store: one for the user name as a string parameter and one that uses the SecureString type for the password. Select AWS Key Management Service (AWS KMS) encryption for the password parameter, and load these parameters in the application tier. Implement an AWS Lambda function that rotates the password every 14 days.

**C.** Store a file that contains the credentials in an AWS Key Management Service (AWS KMS) encrypted Amazon Elastic File System (Amazon EFS) file system. Mount the EFS file system in all EC2 instances of the application tier. Restrict the access to the file on the file system so that the application can read the file and that only super users can modify the file. Implement an AWS Lambda function that rotates the key in Aurora every 14 days and writes new credentials into the file.

**D.** Store a file that contains the credentials in an AWS Key Management Service (AWS KMS) encrypted Amazon S3 bucket that the application uses to load the credentials. Download the file to the application regularly to ensure that the correct credentials are used. Implement an AWS Lambda function that rotates the Aurora credentials every 14 days and uploads these credentials to the file in the S3 bucket.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Aurora MySQL + EC2 app. Cần encrypt credentials + rotate every 14 days. Least operational effort.
- **Existing Resources:** Aurora MySQL, EC2 application tier.
- **Current Issue/Goal:** Encrypt và rotate credentials tự động.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypted` | KMS key để encrypt secret. |
| `rotated every 14 days` | Secrets Manager có built-in rotation cho RDS/Aurora. |
| `least operational effort` | Secrets Manager: không cần tự viết Lambda rotation function. |
| `Secrets Manager` | Managed service: store + rotate credentials, tích hợp RDS/Aurora. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational effort
- **Constraints:** Encrypted credentials, rotation every 14 days, Aurora

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Secrets Manager: tạo secret với KMS encryption, associate với Aurora DB cluster.
- Custom rotation period: 14 ngày (Secrets Manager tự động rotate credentials dùng Lambda template built-in).
- Application load credentials từ Secrets Manager API (SDK).
- Operational effort thấp nhất: không cần tự code Lambda rotation.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Parameter Store không có built-in rotation → phải tự viết Lambda function → operational effort cao hơn.

**❌ Đáp án C:**
- EFS file chứa credentials: không secure bằng Secrets Manager, phải tự quản lý rotation và access control. Operational effort cao.

**❌ Đáp án D:**
- S3 file chứa credentials: tương tự C, operational effort cao hơn Secrets Manager.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Least effort credential rotation → Secrets Manager (built-in rotation + KMS). Parameter Store/EFS/S3 = custom Lambda needed."*
