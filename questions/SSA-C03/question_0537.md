# Question #537 - Topic 1

A company runs a three-tier web application in the AWS Cloud that operates across three Availability Zones. The application architecture has an Application Load Balancer, an Amazon EC2 web server that hosts user session states, and a MySQL database that runs on an EC2 instance. The company expects sudden increases in application traffic. The company wants to be able to scale to meet future application capacity demands and to ensure high availability across all three Availability Zones. Which solution will meet these requirements?

## Options

**A.** Migrate the MySQL database to Amazon RDS for MySQL with a Multi-AZ DB cluster deployment. Use Amazon ElastiCache for Redis with high availability to store session data and to cache reads. Migrate the web server to an Auto Scaling group that is in three Availability Zones.

**B.** Migrate the MySQL database to Amazon RDS for MySQL with a Multi-AZ DB cluster deployment. Use Amazon ElastiCache for Memcached with high availability to store session data and to cache reads. Migrate the web server to an Auto Scaling group that is in three Availability Zones.

**C.** Migrate the MySQL database to Amazon DynamoDB Use DynamoDB Accelerator (DAX) to cache reads. Store the session data in DynamoDB. Migrate the web server to an Auto Scaling group that is in three Availability Zones.

**D.** Migrate the MySQL database to Amazon RDS for MySQL in a single Availability Zone. Use Amazon ElastiCache for Redis with high availability to store session data and to cache reads. Migrate the web server to an Auto Scaling group that is in three Availability Zones.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Three-tier web app: ALB + EC2 web server (session states) + MySQL on EC2. Cần scale để đáp ứng traffic tăng đột ngột, HA across 3 AZs.
- **Existing Resources:** ALB, EC2 (session states), MySQL on EC2.
- **Current Issue/Goal:** Scalability + HA across 3 AZs.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `session states on EC2` | Dùng ElastiCache Redis để lưu session (stateless web tier) |
| `MySQL on EC2` | Migrate to RDS Multi-AZ → HA + managed |
| `Auto Scaling group across 3 AZs` | Scalability + HA cho web tier |
| `ElastiCache Redis` | Lưu session data + cache reads. Redis hỗ trợ HA với replication + auto failover |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Scalability + High availability
- **Constraints:** 3 AZs, traffic spikes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **RDS Multi-AZ DB cluster:** 1 writer + 2 reader instances across 3 AZs → HA cho database, tự động failover.
- **ElastiCache Redis with HA:** Lưu session data ngoài EC2 → web tier stateless, có thể scale horizontally.
  - Redis HA: replication + auto failover, phù hợp cho session store.
  - Redis cũng dùng để cache database reads → giảm load cho RDS.
- **Auto Scaling group across 3 AZs:** Web server tự động scale in/out theo traffic, phân phối đều 3 AZs.
- Đây là kiến trúc classic three-tier scalable + HA.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Memcached không hỗ trợ HA (no replication, no failover). Nếu node fail → mất session data.
- Memcached không phù hợp cho session store cần độ bền.

**❌ Đáp án C:**
- DynamoDB có thể dùng cho session store, nhưng migration từ MySQL sang DynamoDB là thay đổi lớn (relational → NoSQL).
- DAX là caching layer cho DynamoDB, không phải giải pháp session store phổ biến bằng Redis.
- Chi phí và độ phức tạp cao hơn so với RDS MySQL + Redis.

**❌ Đáp án D:**
- RDS single AZ: không HA. Nếu AZ fails, database mất.
- Yêu cầu đề là HA across 3 AZs → single AZ không đáp ứng.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"Session state → Redis (not Memcached). DB HA → RDS Multi-AZ. Web HA → Auto Scaling 3 AZs."*
