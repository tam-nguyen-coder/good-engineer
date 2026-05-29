# Question #578 - Topic 1

A company deployed a serverless application that uses Amazon DynamoDB as a database layer. The application has experienced a large increase in users. The company wants to improve database response time from milliseconds to microseconds and to cache requests to the database. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use DynamoDB Accelerator (DAX).

**B.** Migrate the database to Amazon Redshift.

**C.** Migrate the database to Amazon RDS.

**D.** Use Amazon ElastiCache for Redis.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Serverless app with DynamoDB, muốn improve response time từ ms → μs, cache requests.
- **Existing Resources:** DynamoDB table.
- **Current Issue/Goal:** Giảm latency (ms → μs), caching, least ops overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `microseconds` | DAX cung cấp μs response time cho DynamoDB. |
| `DynamoDB` | DAX là in-memory cache dành riêng cho DynamoDB. |
| `least operational overhead` | DAX fully managed, không cần maintain cache cluster. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** DynamoDB, improve response time, caching

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- DAX là fully managed in-memory cache built specifically for DynamoDB.
- Giảm latency từ milliseconds xuống microseconds.
- Tích hợp trực tiếp với DynamoDB: chỉ cần thay đổi endpoint URL trong app.
- Operational overhead thấp nhất: managed service, không cần quản lý cache cluster phức tạp.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Redshift là data warehouse, không phải cache cho DynamoDB.

**❌ Đáp án C:**
- RDS là relational database, không phải cache. Migrate từ DynamoDB sang RDS là thay đổi architecture lớn.

**❌ Đáp án D:**
- ElastiCache for Redis có thể cache DynamoDB data nhưng cần tự implement caching logic → operational overhead cao hơn DAX.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DynamoDB microsecond cache → DAX (native, managed). ElastiCache works but more overhead."*
