# Question #193 - Topic 1

A company is running a batch application on Amazon EC2 instances. The application consists of a backend with multiple Amazon RDS databases. The application is causing a high number of reads on the databases. A solutions architect must reduce the number of database reads while ensuring high availability. What should the solutions architect do to meet this requirement?

## Options

**A.** Add Amazon RDS read replicas.

**B.** Use Amazon ElastiCache for Redis.

**C.** Use Amazon Route 53 DNS caching

**D.** Use Amazon ElastiCache for Memcached.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Batch app on EC2 + multiple RDS databases. High read load. Reduce DB reads + HA.
- **Existing Resources:** EC2, RDS.
- **Current Issue/Goal:** Caching to reduce reads, HA.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `reduce the number of database reads` | **Caching** (lưu kết quả query) |
| `high availability` | **Redis** (Multi-AZ replication) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database caching
- **Constraints:** Reduce reads, HA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **ElastiCache for Redis** — in-memory caching, reduce number of reads đến database.
- Supports replication (Multi-AZ) → HA.
- Dữ liệu thường xuyên đọc được cache → giảm tải cho RDS.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Read replicas — distribute reads nhưng không reduce total số lượng reads.

**❌ Đáp án C:**
- Route 53 DNS caching — không liên quan đến database reads.

**❌ Đáp án D:**
- Memcached — không có built-in replication → không HA bằng Redis.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ElastiCache Redis = caching + HA (replication). Read replicas = distribute, not reduce. Memcached = no replication"*
