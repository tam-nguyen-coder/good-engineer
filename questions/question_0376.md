# Question #376 - Topic 1

A company has launched an Amazon RDS for MySQL DB instance. Most of the connections to the database come from serverless applications. Application traffic to the database changes significantly at random intervals. At times of high demand, users report that their applications experience database connection rejection errors. Which solution will resolve this issue with the LEAST operational overhead?

## Options

**A.** Create a proxy in RDS Proxy. Configure the users' applications to use the DB instance through RDS Proxy.

**B.** Deploy Amazon ElastiCache for Memcached between the users' applications and the DB instance.

**C.** Migrate the DB instance to a different instance class that has higher I/O capacity. Configure the users' applications to use the new DB instance.

**D.** Configure Multi-AZ for the DB instance. Configure the users' applications to switch between the DB instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL with serverless apps. Traffic spikes cause connection rejection errors.
- **Existing Resources:** RDS MySQL, serverless applications.
- **Current Issue/Goal:** Resolve connection rejection errors, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `connection rejection errors` | RDS max connections exceeded. |
| `serverless applications` | Lambda can scale rapidly → too many connections. |
| `RDS Proxy` | Connection pooling: multiplex connections from Lambda → RDS. |
| `changes significantly at random intervals` | Proxy handles connection spikes gracefully. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Connection rejections from serverless apps

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- RDS Proxy: managed connection pool, multiplexes connections từ serverless apps → RDS.
- Giảm số lượng connections đến RDS, prevent connection rejection.
- Minimal code changes: chỉ cần thay đổi connection string.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ElastiCache cache database queries, không giải quyết connection limit.

**❌ Đáp án C:**
- Upgrade instance class: tăng connection limit nhưng không giải quyết connection storm từ Lambda scale-out. Tốn kém.

**❌ Đáp án D:**
- Multi-AZ: HA/failover, không giải quyết connection limit.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Serverless + RDS connection rejection → RDS Proxy (connection pooling). Upgrade instance = tốn kém, không giải quyết gốc."*
