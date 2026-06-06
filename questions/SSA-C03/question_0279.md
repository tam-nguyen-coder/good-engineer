# Question #279 - Topic 1

A company has an application that is backed by an Amazon DynamoDB table. The company's compliance requirements specify that database backups must be taken every month, must be available for 6 months, and must be retained for 7 years. Which solution will meet these requirements?

## Options

**A.** Create an AWS Backup plan to back up the DynamoDB table on the first day of each month. Specify a lifecycle policy that transitions the backup to cold storage after 6 months. Set the retention period for each backup to 7 years.

**B.** Create a DynamoDB on-demand backup of the DynamoDB table on the first day of each month. Transition the backup to Amazon S3 Glacier Flexible Retrieval after 6 months. Create an S3 Lifecycle policy to delete backups that are older than 7 years.

**C.** Use the AWS SDK to develop a script that creates an on-demand backup of the DynamoDB table. Set up an Amazon EventBridge rule that runs the script on the first day of each month. Create a second script that will run on the second day of each month to transition DynamoDB backups that are older than 6 months to cold storage and to delete backups that are older than 7 years.

**D.** Use the AWS CLI to create an on-demand backup of the DynamoDB table. Set up an Amazon EventBridge rule that runs the command on the first day of each month with a cron expression. Specify in the command to transition the backups to cold storage after 6 months and to delete the backups after 7 years.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DynamoDB table. Monthly backups, available 6 months, retained 7 years.
- **Existing Resources:** DynamoDB table.
- **Current Issue/Goal:** Backup with lifecycle management.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `backups must be taken every month` | Scheduled backup |
| `available for 6 months... retained for 7 years` | **AWS Backup lifecycle** (cold storage → expire) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Backup / Compliance
- **Constraints:** Monthly, 6 months hot, 7 years cold

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **AWS Backup** — supports DynamoDB, scheduled backup.
- **Lifecycle** — transition to cold storage after 6 months, expire after 7 years.
- Managed service, least operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- DynamoDB on-demand backup → S3 Glacier — manual, DynamoDB backup không tự động transition.

**❌ Đáp án C:**
- Custom scripts — operational overhead.

**❌ Đáp án D:**
- AWS CLI + EventBridge — CLI không có option transition/delete backup.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AWS Backup = managed DynamoDB backups with lifecycle. Custom scripts = more overhead"*
