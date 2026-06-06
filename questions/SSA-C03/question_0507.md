# Question #507 - Topic 1

A company has a web application for travel ticketing. The application is based on a database that runs in a single data center in North America. The company wants to expand the application to serve a global user base. The company needs to deploy the application to multiple AWS Regions. Average latency must be less than 1 second on updates to the reservation database. The company wants to have separate deployments of its web platform across multiple Regions. However, the company must maintain a single primary reservation database that is globally consistent. Which solution should a solutions architect recommend to meet these requirements?

## Options

**A.** Convert the application to use Amazon DynamoDB. Use a global table for the center reservation table. Use the correct Regional endpoint in each Regional deployment.

**B.** Migrate the database to an Amazon Aurora MySQL database. Deploy Aurora Read Replicas in each Region. Use the correct Regional endpoint in each Regional deployment for access to the database.

**C.** Migrate the database to an Amazon RDS for MySQL database. Deploy MySQL read replicas in each Region. Use the correct Regional endpoint in each Regional deployment for access to the database.

**D.** Migrate the application to an Amazon Aurora Serverless database. Deploy instances of the database to each Region. Use the correct Regional endpoint in each Regional deployment to access the database. Use AWS Lambda functions to process event streams in each Region to synchronize the databases.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Travel ticketing app mở rộng global. Cần deploy multi-region, <1s latency on updates, single primary database globally consistent.
- **Existing Resources:** Single data center database in North America.
- **Current Issue/Goal:** Global deployment, low-latency writes, strong consistency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `globally consistent` | Strong consistency, eventual consistency không đáp ứng. |
| `single primary reservation database` | Một database chính duy nhất (single writer). |
| `less than 1 second on updates` | Update nhanh, nhưng vẫn consistent. |
| `separate deployments across multiple Regions` | Multi-region web + read replicas local. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Globally consistent, single primary, <1s latency on updates, multi-region

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Aurora MySQL: single primary (writer) đảm bảo global consistency, cross-region Read Replicas cho phép đọc dữ liệu với latency thấp ở mỗi region.
- Aurora cross-region Read Replicas có replication lag thường <100ms → đáp ứng <1s.
- Web platform deploy mỗi region đọc từ local Read Replica, write vẫn về primary.
- Aurora managed service giảm operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DynamoDB global tables là multi-region active-active, nhưng chỉ hỗ trợ eventual consistency (last writer wins). Không đáp ứng "globally consistent".
- Nếu cần strongly consistent reads, chỉ available trong cùng region với write.

**❌ Đáp án C:**
- RDS MySQL read replicas cross-region được, nhưng replication performance không bằng Aurora.
- Aurora có replication latency thấp hơn và failover nhanh hơn RDS MySQL.

**❌ Đáp án D:**
- Aurora Serverless + Lambda sync tạo eventual consistency, không đảm bảo globally consistent.
- Phức tạp, dễ mất dữ liệu nếu Lambda fail. Không phải single primary pattern.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Global consistency + multi-region → Aurora global database (single writer + cross-region replicas). DynamoDB global tables = eventual consistency."*
