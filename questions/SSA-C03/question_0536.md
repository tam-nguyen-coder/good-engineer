# Question #536 - Topic 1

A company wants to provide data scientists with near real-time read-only access to the company's production Amazon RDS for PostgreSQL database. The database is currently configured as a Single-AZ database. The data scientists use complex queries that will not affect the production database. The company needs a solution that is highly available. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Scale the existing production database in a maintenance window to provide enough power for the data scientists.

**B.** Change the setup from a Single-AZ to a Multi-AZ instance deployment with a larger secondary standby instance. Provide the data scientists access to the secondary instance.

**C.** Change the setup from a Single-AZ to a Multi-AZ instance deployment. Provide two additional read replicas for the data scientists.

**D.** Change the setup from a Single-AZ to a Multi-AZ cluster deployment with two readable standby instances. Provide read endpoints to the data scientists.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS for PostgreSQL Single-AZ, muốn cho data scientists read-only access. Complex queries không ảnh hưởng production. Yêu cầu highly available + cost-effective.
- **Existing Resources:** RDS for PostgreSQL Single-AZ.
- **Current Issue/Goal:** Read-only access cho data scientists, HA, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `read-only access` | Cần database instance để read, không write |
| `complex queries` | Read replicas để offload read traffic từ production |
| `highly available` | Multi-AZ deployment (failover tự động) |
| `cost-effectively` | Multi-AZ cluster: 1 writer + 2 reader instances (có thể dùng reader cho data scientists) |
| `RDS Multi-AZ cluster` | PostgreSQL hỗ trợ Multi-AZ cluster deployment với 2 readable standby instances |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Read-only, HA, complex queries không ảnh hưởng production

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- RDS Multi-AZ cluster deployment (PostgreSQL): 1 writer instance + 2 readable standby instances trong 3 AZ khác nhau.
- Data scientists dùng reader instances để query → không ảnh hưởng writer instance.
- Reader instances có thể đọc ngay (near real-time replication).
- Highly available: nếu writer fail, tự động promote 1 reader lên writer.
- Cost-effective: tận dụng reader instances vừa làm standby (HA) vừa phục vụ read queries.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Scale production database: chỉ tăng size cho single instance → không HA, không giải quyết read-only access riêng.
- Vẫn bị ảnh hưởng performance nếu data scientists chạy complex queries.

**❌ Đáp án B:**
- Multi-AZ instance deployment: standby instance không readable (standby chỉ dùng cho failover, không serve traffic).
- "Larger secondary standby" → không được support, standby phải cùng size với primary.

**❌ Đáp án C:**
- Multi-AZ instance deployment + 2 read replicas: tổng cộng 1 writer + 1 standby (không readable) + 2 read replicas → chi phí cao hơn Multi-AZ cluster.
- Read replicas tính phí riêng, không tận dụng cho HA.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"RDS Multi-AZ cluster = 1 writer + 2 readable standbys → HA + read offload, cost-effective hơn read replicas."*
