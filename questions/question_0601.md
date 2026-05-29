# Question #601 - Topic 1

A company runs its critical database on an Amazon RDS for PostgreSQL DB instance. The company wants to migrate to Amazon Aurora PostgreSQL with minimal downtime and data loss. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create a DB snapshot of the RDS for PostgreSQL DB instance to populate a new Aurora PostgreSQL DB cluster.

**B.** Create an Aurora read replica of the RDS for PostgreSQL DB instance. Promote the Aurora read replicate to a new Aurora PostgreSQL DB cluster.

**C.** Use data import from Amazon S3 to migrate the database to an Aurora PostgreSQL DB cluster.

**D.** Use the pg_dump utility to back up the RDS for PostgreSQL database. Restore the backup to a new Aurora PostgreSQL DB cluster.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty chạy critical database trên RDS for PostgreSQL, muốn migrate lên Aurora PostgreSQL với downtime và mất dữ liệu tối thiểu.
- **Existing Resources:** RDS for PostgreSQL DB instance.
- **Current Issue/Goal:** Migration từ RDS PostgreSQL → Aurora PostgreSQL với minimal downtime và data loss.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `RDS for PostgreSQL → Aurora PostgreSQL` | Dịch vụ tương thích PostgreSQL, có thể tạo Aurora Replica từ RDS PostgreSQL. |
| `minimal downtime` | Cần giải pháp online migration, không snapshot/restore. |
| `least operational overhead` | Dịch vụ managed, ít bước thủ công nhất. |
| `Aurora read replica` | Tính năng tạo Aurora Replica từ RDS PostgreSQL → promote lên Aurora cluster. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Minimal downtime, no data loss, migrate RDS PostgreSQL → Aurora PostgreSQL

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Aurora hỗ trợ tạo Aurora Replica từ RDS for PostgreSQL DB instance thông qua tính năng "replication" built-in.
- Quá trình này là online replication → downtime rất thấp (chỉ khi promote replica).
- Sau khi replica được tạo, promote nó thành Aurora PostgreSQL DB cluster độc lập.
- Đây là giải pháp có operational overhead thấp nhất và downtime tối thiểu.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DB snapshot là point-in-time backup, cần downtime để tạo snapshot và restore.
- Dữ liệu mới phát sinh sau snapshot sẽ bị mất.

**❌ Đáp án C:**
- Data import từ S3 yêu cầu export dữ liệu ra S3 trước, sau đó import vào Aurora.
- Nhiều bước thủ công, operational overhead cao hơn.

**❌ Đáp án D:**
- pg_dump là utility backup logical, cần downtime để chạy backup và restore.
- Operational overhead cao, không phải giải pháp managed.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS PostgreSQL → Aurora → tạo Aurora Replica rồi promote. Snapshot/pg_dump = downtime."*
