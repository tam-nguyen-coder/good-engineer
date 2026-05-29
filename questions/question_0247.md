# Question #247 - Topic 1

A company has deployed a database in Amazon RDS for MySQL. Due to increased transactions, the database support team is reporting slow reads against the DB instance and recommends adding a read replica. Which combination of actions should a solutions architect take before implementing this change? (Choose two.)

## Options

**A.** Enable binlog replication on the RDS primary node.

**B.** Choose a failover priority for the source DB instance.

**C.** Allow long-running transactions to complete on the source DB instance.

**D.** Create a global table and specify the AWS Regions where the table will be available.

**E.** Enable automatic backups on the source instance by setting the backup retention period to a value other than 0.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL, slow reads, need read replica. Prerequisites before creating.
- **Existing Resources:** RDS for MySQL.
- **Current Issue/Goal:** Prepare source DB for read replica.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `read replica` | Cần **automatic backups** và **binlog** |
| `Amazon RDS for MySQL` | Dùng binlog-based replication |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / RDS
- **Constraints:** Chọn 2, prerequisites for read replica

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và E**

**Giải thích:**
- **A: Enable binlog** — MySQL binlog required for replication.
- **E: Automatic backups** — backup retention > 0 để RDS duy trì binlog cho read replica sync.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Failover priority — dùng cho Multi-AZ, không liên quan read replica.

**❌ Đáp án C:**
- Long-running transactions — helpful but not a prerequisite.

**❌ Đáp án D:**
- Global table — DynamoDB feature, không phải RDS.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS read replica prerequisites: binlog + automatic backups. Failover priority = Multi-AZ only"*
