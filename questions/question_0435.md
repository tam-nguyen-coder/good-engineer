# Question #435 - Topic 1

A company needs to migrate a MySQL database from its on-premises data center to AWS within 2 weeks. The database is 20 TB in size. The company wants to complete the migration with minimal downtime. Which solution will migrate the database MOST cost-effectively?

## Options

**A.** Order an AWS Snowball Edge Storage Optimized device. Use AWS Database Migration Service (AWS DMS) with AWS Schema Conversion Tool (AWS SCT) to migrate the database with replication of ongoing changes. Send the Snowball Edge device to AWS to finish the migration and continue the ongoing replication.

**B.** Order an AWS Snowmobile vehicle. Use AWS Database Migration Service (AWS DMS) with AWS Schema Conversion Tool (AWS SCT) to migrate the database with ongoing changes. Send the Snowmobile vehicle back to AWS to finish the migration and continue the ongoing replication.

**C.** Order an AWS Snowball Edge Compute Optimized with GPU device. Use AWS Database Migration Service (AWS DMS) with AWS Schema Conversion Tool (AWS SCT) to migrate the database with ongoing changes. Send the Snowball device to AWS to finish the migration and continue the ongoing replication

**D.** Order a 1 GB dedicated AWS Direct Connect connection to establish a connection with the data center. Use AWS Database Migration Service (AWS DMS) with AWS Schema Conversion Tool (AWS SCT) to migrate the database with replication of ongoing changes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate 20TB MySQL to AWS in 2 weeks. Minimal downtime. Most cost-effective.
- **Existing Resources:** On-prem MySQL 20TB.
- **Current Issue/Goal:** Large DB migration, minimal downtime, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `20 TB` | Too large for network transfer in 2 weeks (need ~155 Mbps sustained). |
| `minimal downtime` | DMS ongoing replication (CDC) → switch over quickly. |
| `most cost-effective` | Snowball Edge Storage Optimized (physical transfer). |
| `Snowball Edge Storage Optimized` | 80TB usable, for large data migration. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration / Cost optimization
- **Constraints:** 20TB, 2 weeks, minimal downtime

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Snowball Edge Storage Optimized: 80TB capacity, physical transfer nhanh hơn network cho 20TB.
- DMS + SCT: migrate schema + data, ongoing replication (CDC) để bắt changes trong quá trình vận chuyển.
- Khi Snowball đến AWS → full load, sau đó DMS tiếp tục CDC → switch over với downtime tối thiểu.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Snowmobile: cho > 10PB (exabyte-scale), overkill cho 20TB, rất đắt.

**❌ Đáp án C:**
- Snowball Edge Compute Optimized with GPU: GPU không cần cho DB migration, đắt hơn Storage Optimized.

**❌ Đáp án D:**
- 1GB Direct Connect: có thể đủ bandwidth nhưng chi phí thuê bao hàng tháng rất cao, setup > 2 tuần.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Large DB migration + tight deadline → Snowball (physical) + DMS CDC."*