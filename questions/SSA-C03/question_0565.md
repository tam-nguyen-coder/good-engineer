# Question #565 - Topic 1

A company has an on-premises MySQL database that handles transactional data. The company is migrating the database to the AWS Cloud. The migrated database must maintain compatibility with the company's applications that use the database. The migrated database also must scale automatically during periods of increased demand. Which migration solution will meet these requirements?

## Options

**A.** Use native MySQL tools to migrate the database to Amazon RDS for MySQL. Configure elastic storage scaling.

**B.** Migrate the database to Amazon Redshift by using the mysqldump utility. Turn on Auto Scaling for the Amazon Redshift cluster.

**C.** Use AWS Database Migration Service (AWS DMS) to migrate the database to Amazon Aurora. Turn on Aurora Auto Scaling.

**D.** Use AWS Database Migration Service (AWS DMS) to migrate the database to Amazon DynamoDB. Configure an Auto Scaling policy.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate MySQL database (transactional) từ on-prem lên AWS. Cần maintain compatibility với ứng dụng hiện tại và tự động scale khi demand tăng.
- **Existing Resources:** MySQL database on-premises.
- **Current Issue/Goal:** Migration với MySQL compatibility + auto scaling.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `MySQL database` | Source là MySQL |
| `maintain compatibility` | Target cần MySQL-compatible |
| `scale automatically` | Cần auto scaling |
| `Amazon Aurora` | MySQL-compatible, auto scaling (Aurora Auto Scaling) |
| `AWS DMS` | Managed migration service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** MySQL compatibility, auto scaling, transactional data

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Amazon Aurora MySQL hoàn toàn tương thích với MySQL, nên ứng dụng không cần thay đổi.
- Aurora Auto Scaling tự động thêm Aurora Replicas khi CPU utilization hoặc connections tăng.
- AWS DMS là managed service giúp migration với minimal downtime (change data capture).
- Aurora có performance cao hơn RDS MySQL (5x throughput) và tự động mở rộng storage (lên đến 128 TB).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (RDS MySQL + elastic storage):** RDS MySQL tương thích, nhưng elastic storage scaling chỉ mở rộng storage, không phải compute. Không có auto scaling cho compute (chỉ có thể scale manually hoặc dùng Multi-AZ). Aurora Auto Scaling mạnh hơn.

**❌ Đáp án B (Redshift + mysqldump):** Amazon Redshift là data warehouse (columnar), không tương thích với MySQL (OLTP). mysqldump không tối ưu cho Redshift. Không phải cho transactional data.

**❌ Đáp án D (DynamoDB + DMS):** Amazon DynamoDB là NoSQL database, không MySQL-compatible. Ứng dụng MySQL sẽ không thể chạy với DynamoDB. Cần refactor toàn bộ application code.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"MySQL migration → Aurora (MySQL-compatible, auto scale, better performance). DMS for minimal downtime migration. RDS = no compute auto scaling."*
