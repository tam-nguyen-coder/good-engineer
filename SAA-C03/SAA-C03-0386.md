# Question #386 - Topic 1

An ecommerce company is running a multi-tier application on AWS. The front-end and backend tiers both run on Amazon EC2, and the database runs on Amazon RDS for MySQL. The backend tier communicates with the RDS instance. There are frequent calls to return identical datasets from the database that are causing performance slowdowns. Which action should be taken to improve the performance of the backend?

## Options

**A.** Implement Amazon SNS to store the database calls.

**B.** Implement Amazon ElastiCache to cache the large datasets.

**C.** Implement an RDS for MySQL read replica to cache database calls.

**D.** Implement Amazon Kinesis Data Firehose to stream the calls to the database.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Frontend + backend EC2, RDS MySQL. Frequent calls returning identical datasets → performance slowdown.
- **Existing Resources:** EC2 frontend/backend, RDS MySQL.
- **Current Issue/Goal:** Reduce database load from repeated identical queries.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `identical datasets` | Cache results → ElastiCache (Redis/Memcached). |
| `frequent calls` | Caching giảm database load. |
| `ElastiCache` | In-memory cache cho frequently accessed, identical data. |
| `improve performance` | Cache kết quả query để không phải query DB mỗi lần. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Improve performance
- **Constraints:** Identical datasets returned frequently

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- ElastiCache: cache identical query results → subsequent requests trả về từ cache (in-memory, nhanh hơn DB).
- Giảm database load, cải thiện response time.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- SNS: notification service, không thể "store" database calls.

**❌ Đáp án C:**
- Read replica: giảm load cho primary, nhưng vẫn phải execute query. Cache hiệu quả hơn cho identical datasets.

**❌ Đáp án D:**
- Kinesis Firehose: streaming data delivery, không caching.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Identical repeated queries → ElastiCache (cache). Read replica = vẫn query, không cache. SNS = notifications."*
