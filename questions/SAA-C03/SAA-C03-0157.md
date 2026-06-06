# Question #157 - Topic 1

A company stores data in an Amazon Aurora PostgreSQL DB cluster. The company must store all the data for 5 years and must delete all the data after 5 years. The company also must indefinitely keep audit logs of actions that are performed within the database. Currently, the company has automated backups configured for Aurora. Which combination of steps should a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Take a manual snapshot of the DB cluster.

**B.** Create a lifecycle policy for the automated backups.

**C.** Configure automated backup retention for 5 years.

**D.** Configure an Amazon CloudWatch Logs export for the DB cluster.

**E.** Use AWS Backup to take the backups and to keep the backups for 5 years.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Aurora PostgreSQL, keep data 5 years, delete after. Keep audit logs indefinitely.
- **Existing Resources:** Aurora automated backups (retention max 35 days).
- **Current Issue/Goal:** 5-year backup retention + indefinite audit logs.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `5 years` | Automated backup retention max 35 ngày → cần **manual snapshot** hoặc **AWS Backup** |
| `audit logs of actions` | **CloudWatch Logs** export (Aurora audit logs) |
| `indefinitely` | CloudWatch Logs retention indefinite |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Backup + Compliance
- **Constraints:** Chọn 2

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và E**

**Giải thích:**
- **A: Manual snapshot** — giữ được indefinite (không tự động xoá), có thể delete sau 5 năm.
- **E: AWS Backup** — managed backup, có thể set retention policy 5 năm.
- Automated backup chỉ giữ tối đa 35 ngày — không đủ 5 năm.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Không có lifecycle policy cho automated backups.

**❌ Đáp án C:**
- Aurora automated backup retention max 35 ngày, không thể 5 năm.

**❌ Đáp án D:**
- CloudWatch Logs export — export logs ra S3, không phải backup DB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Manual snapshot + AWS Backup = long-term retention. Automated backup = max 35 days. CloudWatch Logs = audit, not backup"*
