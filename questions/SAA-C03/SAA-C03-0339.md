# Question #339 - Topic 1

A company has a custom application with embedded credentials that retrieves information from an Amazon RDS MySQL DB instance. Management says the application must be made more secure with the least amount of programming effort. What should a solutions architect do to meet these requirements?

## Options

**A.** Use AWS Key Management Service (AWS KMS) to create keys. Configure the application to load the database credentials from AWS KMS. Enable automatic key rotation.

**B.** Create credentials on the RDS for MySQL database for the application user and store the credentials in AWS Secrets Manager. Configure the application to load the database credentials from Secrets Manager. Create an AWS Lambda function that rotates the credentials in Secret Manager.

**C.** Create credentials on the RDS for MySQL database for the application user and store the credentials in AWS Secrets Manager. Configure the application to load the database credentials from Secrets Manager. Set up a credentials rotation schedule for the application user in the RDS for MySQL database using Secrets Manager.

**D.** Create credentials on the RDS for MySQL database for the application user and store the credentials in AWS Systems Manager Parameter Store. Configure the application to load the database credentials from Parameter Store. Set up a credentials rotation schedule for the application user in the RDS for MySQL database using Parameter Store.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** App có embedded credentials để kết nối RDS MySQL. Cần secure hơn với least programming effort.
- **Existing Resources:** Custom application, RDS MySQL DB instance.
- **Current Issue/Goal:** Remove embedded credentials, add rotation, least programming effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `least amount of programming effort` | Secrets Manager có built-in rotation template cho RDS, không cần tự code Lambda. |
| `Secrets Manager` | Store + rotate credentials, tích hợp RDS. |
| `credentials rotation schedule using Secrets Manager` | Secrets Manager có sẵn rotation function cho RDS (tạo tự động). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least programming effort
- **Constraints:** RDS MySQL, remove embedded credentials, rotation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Secrets Manager: lưu credentials, application load credentials từ Secrets Manager API (gọi SDK) → remove embedded credentials.
- Secrets Manager có built-in rotation template cho RDS MySQL → chỉ cần enable rotation schedule, không cần tự code Lambda.
- Rotation tự động giúp credentials luôn được thay đổi định kỳ.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- KMS không lưu credentials (KMS lưu keys). Không thể "load database credentials from AWS KMS".

**❌ Đáp án B:**
- "Create an AWS Lambda function that rotates the credentials" → programming effort cao hơn C (C dùng built-in rotation).

**❌ Đáp án D:**
- Parameter Store không có built-in rotation cho RDS credentials (cần custom Lambda).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Least programming effort → Secrets Manager (built-in RDS rotation). KMS = keys, không credentials. Parameter Store = auto rotation cần custom code."*
