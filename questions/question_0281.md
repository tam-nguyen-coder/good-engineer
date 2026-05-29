# Question #281 - Topic 1

A company runs a fleet of web servers using an Amazon RDS for PostgreSQL DB instance. After a routine compliance check, the company sets a standard that requires a recovery point objective (RPO) of less than 1 second for all its production databases. Which solution meets these requirements?

## Options

**A.** Enable a Multi-AZ deployment for the DB instance.

**B.** Enable auto scaling for the DB instance in one Availability Zone.

**C.** Configure the DB instance in one Availability Zone, and create multiple read replicas in a separate Availability Zone.

**D.** Configure the DB instance in one Availability Zone, and configure AWS Database Migration Service (AWS DMS) change data capture (CDC) tasks.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty có RDS PostgreSQL (fleet of web servers), cần đáp ứng RPO < 1 giây cho production databases.
- **Existing Resources:** RDS for PostgreSQL DB instance.
- **Current Issue/Goal:** Cần đạt RPO < 1 second sau compliance check.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `recovery point objective (RPO)` | Lượng dữ liệu tối đa có thể mất (tính theo thời gian). RPO < 1s → đồng bộ dữ liệu gần như real-time. |
| `less than 1 second` | Cần replication đồng bộ (synchronous), không thể dùng async. |
| `Multi-AZ deployment` | RDS Multi-AZ dùng synchronous replication giữa primary và standby, RPO = 0. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** RPO < 1 second, production database

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Multi-AZ deployment sử dụng synchronous replication giữa primary instance và standby instance ở AZ khác → dữ liệu được đồng bộ ngay lập tức, RPO ≈ 0 (không mất dữ liệu).
- Khi failover, standby được promote lên primary với zero data loss, đáp ứng RPO < 1 giây.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Auto scaling chỉ giúp thay đổi kích thước instance dựa trên tải, không liên quan đến RPO hay replication.

**❌ Đáp án C:**
- Read Replicas dùng asynchronous replication → có độ trễ (lag), không thể đảm bảo RPO < 1 giây.

**❌ Đáp án D:**
- DMS CDC dùng để migrate/sync dữ liệu liên tục, không phải giải pháp HA/RPO cho RDS production. Nó có độ trễ nhất định và không phải là RDS-native HA feature.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-AZ = sync replication → RPO = 0. Read Replica = async → có lag. RPO < 1s → Multi-AZ là đủ."*
