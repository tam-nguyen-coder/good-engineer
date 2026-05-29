# Question #527 - Topic 1

A company has a regional subscription-based streaming service that runs in a single AWS Region. The architecture consists of web servers and application servers on Amazon EC2 instances. The EC2 instances are in Auto Scaling groups behind Elastic Load Balancers. The architecture includes an Amazon Aurora global database cluster that extends across multiple Availability Zones. The company wants to expand globally and to ensure that its application has minimal downtime. Which solution will provide the MOST fault tolerance?

## Options

**A.** Extend the Auto Scaling groups for the web tier and the application tier to deploy instances in Availability Zones in a second Region. Use an Aurora global database to deploy the database in the primary Region and the second Region. Use Amazon Route 53 health checks with a failover routing policy to the second Region.

**B.** Deploy the web tier and the application tier to a second Region. Add an Aurora PostgreSQL cross-Region Aurora Replica in the second Region. Use Amazon Route 53 health checks with a failover routing policy to the second Region. Promote the secondary to primary as needed.

**C.** Deploy the web tier and the application tier to a second Region. Create an Aurora PostgreSQL database in the second Region. Use AWS Database Migration Service (AWS DMS) to replicate the primary database to the second Region. Use Amazon Route 53 health checks with a failover routing policy to the second Region.

**D.** Deploy the web tier and the application tier to a second Region. Use an Amazon Aurora global database to deploy the database in the primary Region and the second Region. Use Amazon Route 53 health checks with a failover routing policy to the second Region. Promote the secondary to primary as needed.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Regional streaming service muốn expand globally với minimal downtime. Hiện tại đang dùng Aurora global database cluster multi-AZ.
- **Existing Resources:** EC2 (Auto Scaling + ELB), Aurora global database cluster.
- **Current Issue/Goal:** Fault tolerance cao nhất khi mở rộng global.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Aurora global database` | 1 primary Region + nhiều secondary Regions, replication <1s |
| `most fault tolerance` | Cần giải pháp dự phòng đầy đủ cả compute và database |
| `Route 53 failover routing policy` | Chuyển traffic khi primary Region fails |
| `promote secondary to primary` | Trong DR scenario, cần promote secondary database |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most fault tolerance
- **Constraints:** Global expansion, minimal downtime

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Aurora global database: 1 primary Region ghi dữ liệu, secondary Region(s) đọc dữ liệu với replication latency <1 giây.
- Khi primary Region fails, promote secondary cluster thành primary → writes được phép ở secondary Region.
- Web + application tier deploy ở second Region với Auto Scaling groups.
- Route 53 failover routing policy tự động chuyển traffic khi health check fails.
- Đây là kiến trúc active-passive DR hoàn chỉnh, fault tolerance cao nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- "Extend Auto Scaling groups across Regions" là sai vì Auto Scaling groups hoạt động trong một Region, không thể extend xuyên Region.
- Cũng mơ hồ về cách deploy.

**❌ Đáp án B:**
- Cross-Region Aurora Replica khác với Aurora global database. Cross-Region Replica cần promote thủ công và không managed bằng global database.
- Không có cơ chế tự động failover cho database.

**❌ Đáp án C:**
- DMS replication không real-time, có độ trễ cao hơn Aurora global database.
- DMS không phải là native Aurora replication → operational overhead cao hơn, fault tolerance thấp hơn.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"Aurora global database = 1 primary + multiple secondary Regions, <1s replication, promote for DR."*
