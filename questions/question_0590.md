# Question #590 - Topic 1

A company migrated a MySQL database from the company's on-premises data center to an Amazon RDS for MySQL DB instance. The company sized the RDS DB instance to meet the company's average daily workload. Once a month, the database performs slowly when the company runs queries for a report. The company wants to have the ability to run reports and maintain the performance of the daily workloads. Which solution will meet these requirements?

## Options

**A.** Create a read replica of the database. Direct the queries to the read replica.

**B.** Create a backup of the database. Restore the backup to another DB instance. Direct the queries to the new database.

**C.** Export the data to Amazon S3. Use Amazon Athena to query the S3 bucket.

**D.** Resize the DB instance to accommodate the additional workload.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL sized cho average daily workload. Monthly report queries cause slow performance.
- **Existing Resources:** RDS MySQL DB instance.
- **Current Issue/Goal:** Run monthly reports without affecting daily workload performance.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `read replica` | Offload read queries (reporting) từ primary DB. Không ảnh hưởng daily workload. |
| `once a month` | Không phải thường xuyên, read replica có thể start/stop hoặc dùng serverless. |
| `maintain the performance of the daily workloads` | Cần tách reporting workload khỏi primary. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Maintain performance
- **Constraints:** MySQL, monthly report queries

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- RDS read replica: primary xử lý daily workload, replica xử lý reporting queries.
- Không ảnh hưởng performance của primary.
- Chi phí thấp: chỉ chạy replica khi cần (hoặc có thể để chạy 24/7 với instance nhỏ).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Backup → restore → query: mất thời gian, không real-time data, operational overhead cao.

**❌ Đáp án C:**
- Export to S3 + Athena: không real-time, cần ETL process, không phải solution tốt nhất cho occasional queries.

**❌ Đáp án D:**
- Resize instance: tốn thêm chi phí 24/7 cho capacity chỉ cần 1 lần/tháng.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Monthly reporting ≠ impact prod → Read Replica (offload reads). Resize = 24/7 cost for monthly use."*
