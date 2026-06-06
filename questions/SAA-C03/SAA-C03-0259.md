# Question #259 - Topic 1

A company is implementing new data retention policies for all databases that run on Amazon RDS DB instances. The company must retain daily backups for a minimum period of 2 years. The backups must be consistent and restorable. Which solution should a solutions architect recommend to meet these requirements?

## Options

**A.** Create a backup vault in AWS Backup to retain RDS backups. Create a new backup plan with a daily schedule and an expiration period of 2 years after creation. Assign the RDS DB instances to the backup plan.

**B.** Configure a backup window for the RDS DB instances for daily snapshots. Assign a snapshot retention policy of 2 years to each RDS DB instance. Use Amazon Data Lifecycle Manager (Amazon DLM) to schedule snapshot deletions.

**C.** Configure database transaction logs to be automatically backed up to Amazon CloudWatch Logs with an expiration period of 2 years.

**D.** Configure an AWS Database Migration Service (AWS DMS) replication task. Deploy a replication instance, and configure a change data capture (CDC) task to stream database changes to Amazon S3 as the target. Configure S3 Lifecycle policies to delete the snapshots after 2 years.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS daily backups, retain minimum 2 years. Consistent and restorable.
- **Existing Resources:** RDS DB instances.
- **Current Issue/Goal:** Managed backup with retention.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `backups must be consistent and restorable` | **AWS Backup** — managed backup |
| `retain... for 2 years` | Backup plan with expiration |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Backup / Compliance
- **Constraints:** Daily, 2-year retention, consistent

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **AWS Backup** — centralized backup service, hỗ trợ RDS.
- Backup plan: daily schedule + expire after 2 years.
- Backups consistent and restorable.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- DLM — chỉ cho EBS snapshots, không hỗ trợ RDS.

**❌ Đáp án C:**
- CloudWatch Logs — lưu transaction logs, không phải DB backups.

**❌ Đáp án D:**
- DMS CDC — replication, không phải backup/restore solution.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AWS Backup = managed RDS backups with retention. DLM = EBS only. DMS = replication, not backup"*
