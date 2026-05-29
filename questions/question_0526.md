# Question #526 - Topic 1

A solutions architect is reviewing the resilience of an application. The solutions architect notices that a database administrator recently failed over the application's Amazon Aurora PostgreSQL database writer instance as part of a scaling exercise. The failover resulted in 3 minutes of downtime for the application. Which solution will reduce the downtime for scaling exercises with the LEAST operational overhead?

## Options

**A.** Create more Aurora PostgreSQL read replicas in the cluster to handle the load during failover.

**B.** Set up a secondary Aurora PostgreSQL cluster in the same AWS Region. During failover, update the application to use the secondary cluster's writer endpoint.

**C.** Create an Amazon ElastiCache for Memcached cluster to handle the load during failover.

**D.** Set up an Amazon RDS proxy for the database. Update the application to use the proxy endpoint.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Aurora PostgreSQL failover (scaling exercise) gây 3 phút downtime. Cần giảm downtime.
- **Existing Resources:** Aurora PostgreSQL DB cluster (writer instance + read replicas).
- **Current Issue/Goal:** Giảm downtime khi failover, operational overhead thấp.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Aurora PostgreSQL` | Aurora tự động failover nhanh hơn RDS (~30s vs ~60-120s) |
| `3 minutes of downtime` | DNS propagation + application reconnect time |
| `RDS Proxy` | Connection pooling, giảm failover downtime bằng cách duy trì connections |
| `least operational overhead` | Giải pháp đơn giản, không thay đổi kiến trúc lớn |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Giảm downtime khi failover Aurora PostgreSQL

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- RDS Proxy là managed connection pooling service cho RDS/Aurora.
- Khi failover xảy ra, RDS Proxy duy trì kết nối từ application → application không cần reconnect, downtime giảm đáng kể.
- RDS Proxy giữ cho connections tồn tại trong suốt quá trình failover và tự động chuyển hướng đến writer instance mới.
- Operational overhead thấp: chỉ cần tạo proxy và cập nhật connection string.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Read replicas không giúp giảm downtime khi writer failover.
- Read replicas chỉ phục vụ read traffic, writer failover vẫn gây downtime.

**❌ Đáp án B:**
- Secondary cluster trong cùng region → phức tạp, cần replication và cập nhật application endpoint khi failover → operational overhead cao.

**❌ Đáp án C:**
- ElastiCache Memcached là caching layer, không liên quan đến database failover downtime.
- Cache miss vẫn phải query database.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"RDS Proxy = connection pool, failover downtime gần như zero. Không cần application reconnect."*
