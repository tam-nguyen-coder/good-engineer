# Question #453 - Topic 1

A company wants to implement a backup strategy for Amazon EC2 data and multiple Amazon S3 buckets. Because of regulatory requirements, the company must retain backup files for a specific time period. The company must not alter the files for the duration of the retention period. Which solution will meet these requirements?

## Options

**A.** Use AWS Backup to create a backup vault that has a vault lock in governance mode. Create the required backup plan.

**B.** Use Amazon Data Lifecycle Manager to create the required automated snapshot policy.

**C.** Use Amazon S3 File Gateway to create the backup. Configure the appropriate S3 Lifecycle management.

**D.** Use AWS Backup to create a backup vault that has a vault lock in compliance mode. Create the required backup plan.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Backup EC2 + S3. Regulatory: retain for specific period, cannot alter files.
- **Existing Resources:** EC2, S3 buckets.
- **Current Issue/Goal:** Immutable backup for compliance.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `must not alter the files` | Immutable backup (write once, read many - WORM). |
| `retention period` | AWS Backup Vault Lock. |
| `compliance mode` | No one (including root) can delete/change retention. |
| `AWS Backup` | Centralized backup for EC2, S3, and other services. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Compliance / Backup
- **Constraints:** Immutable retention, EC2 + S3

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- AWS Backup: centralized backup service hỗ trợ EC2 + S3.
- Vault Lock in compliance mode: WORM (Write Once Read Many), không thể thay đổi retention policy.
- Compliance mode: even root cannot delete/alter backups during retention.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Governance mode: user với IAM permissions có thể bypass → không đủ compliance.

**❌ Đáp án B:**
- Data Lifecycle Manager: chỉ quản lý EBS snapshots, không cover S3.

**❌ Đáp án C:**
- S3 File Gateway: truy cập file từ on-prem, không phải backup solution cho EC2 + S3.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Immutable backup → AWS Backup + Vault Lock compliance mode. Governance = có thể bypass."*