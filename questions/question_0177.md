# Question #177 - Topic 1

An entertainment company is using Amazon DynamoDB to store media metadata. The application is read intensive and experiencing delays. The company does not have staff to handle additional operational overhead and needs to improve the performance efficiency of DynamoDB without reconfiguring the application. What should a solutions architect recommend to meet this requirement?

## Options

**A.** Use Amazon ElastiCache for Redis.

**B.** Use Amazon DynamoDB Accelerator (DAX).

**C.** Replicate data by using DynamoDB global tables.

**D.** Use Amazon ElastiCache for Memcached with Auto Discovery enabled.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DynamoDB read-intensive, delays. No operational overhead, no app reconfiguration.
- **Existing Resources:** DynamoDB table.
- **Current Issue/Goal:** Improve read performance transparently.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `without reconfiguring the application` | **DAX** = drop-in cache, không cần thay đổi code |
| `read intensive` | In-memory caching needed |
| `no additional operational overhead` | DAX là managed service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database caching
- **Constraints:** Read performance, no app change, no overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **DAX (DynamoDB Accelerator)** — in-memory cache, compatible với DynamoDB API → không cần thay đổi application code.
- Giảm latency từ milliseconds → microseconds.
- Fully managed → không operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ElastiCache Redis — cần re-write code để dùng Redis API, operational overhead.

**❌ Đáp án C:**
- Global tables — multi-Region replication, không cache, không giúp giảm latency.

**❌ Đáp án D:**
- ElastiCache Memcached — cần thay đổi code, operational overhead.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DAX = DynamoDB cache (transparent). ElastiCache = app changes needed. Global tables = replication, not caching"*
