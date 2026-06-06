# Question #78 - Topic 1

A company needs to keep user transaction data in an Amazon DynamoDB table. The company must retain the data for 7 years. What is the MOST operationally efficient solution that meets these requirements?

## Options

**A.** Use DynamoDB point-in-time recovery to back up the table continuously.

**B.** Use AWS Backup to create backup schedules and retention policies for the table.

**C.** Create an on-demand backup of the table by using the DynamoDB console. Store the backup in an Amazon S3 bucket. Set an S3 Lifecycle configuration for the S3 bucket.

**D.** Create an Amazon EventBridge (Amazon CloudWatch Events) rule to invoke an AWS Lambda function. Configure the Lambda function to back up the table and to store the backup in an Amazon S3 bucket. Set an S3 Lifecycle configuration for the S3 bucket.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DynamoDB transaction data, cần retain 7 năm.
- **Existing Resources:** DynamoDB table.
- **Current Issue/Goal:** Retain backups 7 years, most operationally efficient.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `retain the data for 7 years` | Cần backup có retention policy dài hạn |
| `most operationally efficient` | Managed backup service → **AWS Backup** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Backup + Operational efficiency
- **Constraints:** DynamoDB, 7-year retention

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **AWS Backup** — fully managed backup service, hỗ trợ DynamoDB.
- Có thể tạo **backup schedule** và **retention policy** (7 năm).
- **Most operationally efficient** — không cần tự code, console, hay Lambda.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **PITR** chỉ giữ backup trong 35 ngày — không đủ 7 năm.

**❌ Đáp án C:**
- On-demand backup bằng console — thủ công, không tự động cho 7 năm.

**❌ Đáp án D:**
- EventBridge + Lambda — phải tự viết code quản lý backup → operational overhead cao hơn AWS Backup.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AWS Backup = managed backup + retention policy. PITR = 35 days only. Custom Lambda = overhead"*
