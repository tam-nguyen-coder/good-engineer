# Question #133 - Topic 1

A company runs an Oracle database on premises. As part of the company’s migration to AWS, the company wants to upgrade the database to the most recent available version. The company also wants to set up disaster recovery (DR) for the database. The company needs to minimize the operational overhead for normal operations and DR setup. The company also needs to maintain access to the database's underlying operating system. Which solution will meet these requirements?

## Options

**A.** Migrate the Oracle database to an Amazon EC2 instance. Set up database replication to a different AWS Region.

**B.** Migrate the Oracle database to Amazon RDS for Oracle. Activate Cross-Region automated backups to replicate the snapshots to another AWS Region.

**C.** Migrate the Oracle database to Amazon RDS Custom for Oracle. Create a read replica for the database in another AWS Region.

**D.** Migrate the Oracle database to Amazon RDS for Oracle. Create a standby database in another Availability Zone.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Oracle DB migration to AWS. Upgrade to latest version. DR with minimal overhead. Need OS access.
- **Existing Resources:** Oracle DB on-prem.
- **Current Issue/Goal:** Managed DB + OS access + DR.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `maintain access to the database's underlying operating system` | Cần **RDS Custom** (RDS standard không cho OS access) |
| `disaster recovery (DR)` | Cross-Region |
| `minimize operational overhead` | Managed service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database migration + DR
- **Constraints:** OS access, DR, minimal overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **RDS Custom for Oracle** — managed DB với OS access (SSH, RDP).
- **Cross-Region read replica** — DR setup, tự động replication.
- Kết hợp managed + OS access + DR.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 — full control nhưng operational overhead cao (patch, backup, replication tự quản lý).

**❌ Đáp án B:**
- RDS for Oracle — managed nhưng **không có OS access**.

**❌ Đáp án D:**
- RDS for Oracle — không OS access.
- Multi-AZ là HA, không phải DR (cross-Region).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS Custom = managed + OS access. RDS Standard = managed, no OS. Cross-Region replica = DR"*
