# Question #381 - Topic 1

A company hosts a three-tier web application that includes a PostgreSQL database. The database stores the metadata from documents. The company searches the metadata for key terms to retrieve documents that the company reviews in a report each month. The documents are stored in Amazon S3. The documents are usually written only once, but they are updated frequently. The reporting process takes a few hours with the use of relational queries. The reporting process must not prevent any document modifications or the addition of new documents. A solutions architect needs to implement a solution to speed up the reporting process. Which solution will meet these requirements with the LEAST amount of change to the application code?

## Options

**A.** Set up a new Amazon DocumentDB (with MongoDB compatibility) cluster that includes a read replica. Scale the read replica to generate the reports.

**B.** Set up a new Amazon Aurora PostgreSQL DB cluster that includes an Aurora Replica. Issue queries to the Aurora Replica to generate the reports.

**C.** Set up a new Amazon RDS for PostgreSQL Multi-AZ DB instance. Configure the reporting module to query the secondary RDS node so that the reporting module does not affect the primary node.

**D.** Set up a new Amazon DynamoDB table to store the documents. Use a fixed write capacity to support new document entries. Automatically scale the read capacity to support the reports.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** PostgreSQL metadata, documents in S3. Monthly reports take hours, must not block writes/updates. Speed up reports, least code changes.
- **Existing Resources:** PostgreSQL DB, S3 documents.
- **Current Issue/Goal:** Offload reporting queries without impacting production.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `must not prevent any document modifications` | Không ảnh hưởng primary DB. |
| `relational queries` | Cần SQL (PostgreSQL) → Aurora PostgreSQL compatible. |
| `Aurora Replica` | Aurora read replica, offload reporting queries, PostgreSQL compatible. |
| `least amount of change` | Aurora PostgreSQL = compatible with PostgreSQL, minimal code changes. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least code changes, speed up reporting
- **Constraints:** PostgreSQL, read-heavy reporting, no write impact

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Aurora PostgreSQL: tương thích PostgreSQL → minimal code changes.
- Aurora Replicas: có thể serve read queries, không ảnh hưởng primary writes.
- Report queries chạy trên Aurora Replica → không block writes.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DocumentDB (MongoDB): không tương thích PostgreSQL query → major code changes.

**❌ Đáp án C:**
- RDS Multi-AZ standby không thể serve read queries. RDS Multi-AZ standby chỉ dùng cho failover.

**❌ Đáp án D:**
- DynamoDB: NoSQL, không relational queries → major code changes.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"PostgreSQL reporting + no write impact → Aurora Replica (read replica). RDS Multi-AZ standby = không đọc được."*
