# Question #365 - Topic 1

A company runs a web application that is backed by Amazon RDS. A new database administrator caused data loss by accidentally editing information in a database table. To help recover from this type of incident, the company wants the ability to restore the database to its state from 5 minutes before any change within the last 30 days. Which feature should the solutions architect include in the design to meet this requirement?

## Options

**A.** Read replicas

**B.** Manual snapshots

**C.** Automated backups

**D.** Multi-AZ deployments

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Accidental data loss. Cần restore RDS database to any point within last 30 days (5 minutes before change).
- **Existing Resources:** RDS DB instance.
- **Current Issue/Goal:** Point-in-time recovery (PITR) within 30-day window.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `restore to its state from 5 minutes before any change` | Point-in-time recovery (PITR). |
| `within the last 30 days` | Automated backup retention: 1-35 days. |
| `Automated backups` | Enable PITR to any second trong retention period. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which feature enables PITR
- **Constraints:** Restore to any point in last 30 days

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- RDS Automated backups: tự động backup hàng ngày + transaction logs → cho phép PITR (point-in-time recovery) đến bất kỳ second nào trong retention period (1-35 days, configurable).
- Restore to 5 minutes before the change is possible với PITR.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Read replicas: for read scaling, không phải backup/restore.

**❌ Đáp án B:**
- Manual snapshots: chỉ restore được đến thời điểm snapshot, không phải "5 minutes before any change".

**❌ Đáp án D:**
- Multi-AZ: high availability, tự động failover, không phải PITR.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Restore to any point in time → Automated backups (PITR). Manual snapshots = chỉ restore đến thời điểm snapshot."*
