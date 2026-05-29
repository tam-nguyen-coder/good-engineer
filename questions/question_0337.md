# Question #337 - Topic 1

A company has deployed a web application on AWS. The company hosts the backend database on Amazon RDS for MySQL with a primary DB instance and five read replicas to support scaling needs. The read replicas must lag no more than 1 second behind the primary DB instance. The database routinely runs scheduled stored procedures. As traffic on the website increases, the replicas experience additional lag during periods of peak load. A solutions architect must reduce the replication lag as much as possible. The solutions architect must minimize changes to the application code and must minimize ongoing operational overhead. Which solution will meet these requirements?

## Options

**A.** Migrate the database to Amazon Aurora MySQL. Replace the read replicas with Aurora Replicas, and configure Aurora Auto Scaling. Replace the stored procedures with Aurora MySQL native functions.

**B.** Deploy an Amazon ElastiCache for Redis cluster in front of the database. Modify the application to check the cache before the application queries the database. Replace the stored procedures with AWS Lambda functions.

**C.** Migrate the database to a MySQL database that runs on Amazon EC2 instances. Choose large, compute optimized EC2 instances for all replica nodes. Maintain the stored procedures on the EC2 instances.

**D.** Migrate the database to Amazon DynamoDB. Provision a large number of read capacity units (RCUs) to support the required throughput, and configure on-demand capacity scaling. Replace the stored procedures with DynamoDB streams.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL + 5 read replicas, replication lag > 1s during peak load. Cần reduce lag, minimize code changes and operational overhead.
- **Existing Resources:** RDS MySQL primary + 5 read replicas, stored procedures.
- **Current Issue/Goal:** Reduce replication lag, minimize changes, minimize overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `replication lag` | RDS MySQL read replicas dùng async binlog replication → lag khi primary busy. |
| `Amazon Aurora MySQL` | Aurora storage shared, replication at storage level → lag thấp hơn nhiều (< 1s). |
| `Aurora Replicas` | Up to 15 Aurora Replicas với lag thường ~tens of milliseconds. |
| `Aurora Auto Scaling` | Tự động scale số Aurora Replicas dựa trên load. |
| `minimize changes to the application code` | Aurora MySQL tương thích MySQL → minimal code changes. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Reduce replication lag, minimize changes and overhead
- **Constraints:** < 1s lag, stored procedures, minimize code changes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Aurora MySQL: shared storage architecture → replication at storage level, lag rất thấp (thường < 100ms).
- Aurora Replicas (up to 15) thay thế RDS read replicas, Aurora Auto Scaling tự động scale.
- Aurora MySQL tương thích MySQL → stored procedures vẫn hoạt động, minimal code changes.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ElastiCache + app modification (check cache before query) → code changes. Stored procedures → Lambda → code changes.

**❌ Đáp án C:**
- EC2 self-managed MySQL → operational overhead cao hơn RDS/Aurora. Vẫn dùng binlog replication → same lag issue.

**❌ Đáp án D:**
- DynamoDB khác hoàn toàn MySQL (NoSQL) → major application rewrite. Stored procedures → DynamoDB streams → code changes.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS MySQL replication lag → Aurora MySQL (shared storage, low lag). DDB/ElastiCache/EC2 = nhiều code changes."*
