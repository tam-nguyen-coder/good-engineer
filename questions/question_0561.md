# Question #561 - Topic 1

A company's website handles millions of requests each day, and the number of requests continues to increase. A solutions architect needs to improve the response time of the web application. The solutions architect determines that the application needs to decrease latency when retrieving product details from the Amazon DynamoDB table. Which solution will meet these requirements with the LEAST amount of operational overhead?

## Options

**A.** Set up a DynamoDB Accelerator (DAX) cluster. Route all read requests through DAX.

**B.** Set up Amazon ElastiCache for Redis between the DynamoDB table and the web application. Route all read requests through Redis.

**C.** Set up Amazon ElastiCache for Memcached between the DynamoDB table and the web application. Route all read requests through Memcached.

**D.** Set up Amazon DynamoDB Streams on the table, and have AWS Lambda read from the table and populate Amazon ElastiCache. Route all read requests through ElastiCache.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Website millions of requests/day, cần cải thiện response time. Giảm latency khi lấy product details từ DynamoDB.
- **Existing Resources:** DynamoDB table, web application.
- **Current Issue/Goal:** Giảm read latency, ít operational overhead nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `decrease latency` | Cần in-memory caching |
| `DynamoDB` | NoSQL database, DAX là cache chuyên dụng |
| `DynamoDB Accelerator (DAX)` | In-memory cache cho DynamoDB, fully managed |
| `LEAST amount of operational overhead` | Giải pháp đơn giản, ít cấu hình nhất |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Giảm latency read từ DynamoDB

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- DAX là in-memory caching service được xây dựng riêng cho DynamoDB. Fully managed, tự động scale.
- Tích hợp trực tiếp với DynamoDB – chỉ cần thay đổi endpoint URL từ DynamoDB sang DAX. Application code gần như không cần thay đổi.
- DAX xử lý hàng triệu requests/phút với microsecond latency.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (ElastiCache Redis):** Redis là giải pháp caching tốt nhưng phải quản lý cache invalidation, cấu hình cluster, và sửa application code để đọc từ Redis thay vì DynamoDB. Operational overhead cao hơn DAX.

**❌ Đáp án C (ElastiCache Memcached):** Memcached cũng tương tự Redis nhưng không hỗ trợ persistence, replication, hay advanced data structures. Vẫn phải quản lý cache invalidation và sửa code.

**❌ Đáp án D (DynamoDB Streams + Lambda + ElastiCache):** Complex nhất. Phải cấu hình DynamoDB Streams, Lambda function để populate cache, và ElastiCache cluster. Operational overhead rất cao. Chỉ cần thiết nếu cache cần được cập nhật gần như real-time với write operations.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DynamoDB latency → DAX = purpose-built cache, least overhead. ElastiCache = more overhead (manage invalidation, change code)."*
