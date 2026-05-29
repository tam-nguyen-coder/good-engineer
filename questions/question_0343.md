# Question #343 - Topic 1

A solutions architect is designing a company's disaster recovery (DR) architecture. The company has a MySQL database that runs on an Amazon EC2 instance in a private subnet with scheduled backup. The DR design needs to include multiple AWS Regions. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Migrate the MySQL database to multiple EC2 instances. Configure a standby EC2 instance in the DR Region. Turn on replication.

**B.** Migrate the MySQL database to Amazon RDS. Use a Multi-AZ deployment. Turn on read replication for the primary DB instance in the different Availability Zones.

**C.** Migrate the MySQL database to an Amazon Aurora global database. Host the primary DB cluster in the primary Region. Host the secondary DB cluster in the DR Region.

**D.** Store the scheduled backup of the MySQL database in an Amazon S3 bucket that is configured for S3 Cross-Region Replication (CRR). Use the data backup to restore the database in the DR Region.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** MySQL on EC2 in private subnet, scheduled backup. Cần cross-Region DR. Least operational overhead.
- **Existing Resources:** EC2 MySQL, scheduled backup.
- **Current Issue/Goal:** Cross-Region DR, minimal operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `multiple AWS Regions` | Cross-Region DR, không chỉ Multi-AZ (trong 1 Region). |
| `least operational overhead` | Managed service > self-managed. Aurora global database > RDS + custom replication. |
| `Aurora global database` | Built-in cross-Region replication (1s lag), managed failover. |
| `primary DB cluster / secondary DB cluster` | Global database: primary Region và secondary Region. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Cross-Region DR, MySQL

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Aurora global database: cross-Region replication built-in, tự động quản lý replication giữa primary và secondary Region.
- Không cần tự cấu hình replication, tự động failover → operational overhead thấp nhất.
- Aurora tương thích MySQL.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Self-managed EC2 MySQL replication: cần tự cấu hình, monitoring, failover → operational overhead cao.

**❌ Đáp án B:**
- RDS Multi-AZ chỉ trong 1 Region, không cross-Region. Read replicas trong AZ khác vẫn cùng Region.

**❌ Đáp án D:**
- S3 CRR backup + manual restore: RPO cao (depend on backup schedule), manual failover → operational overhead cao, không real-time.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cross-Region DR MySQL → Aurora global database (built-in replication). RDS Multi-AZ = trong 1 Region."*
