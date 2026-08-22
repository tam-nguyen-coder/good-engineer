# Question #472 - Topic 1

A company has a mobile chat application with a data store based in Amazon DynamoDB. Users would like new messages to be read with as little latency as possible. A solutions architect needs to design an optimal solution that requires minimal application changes. Which method should the solutions architect select?

## Options

**A.** Configure Amazon DynamoDB Accelerator (DAX) for the new messages table. Update the code to use the DAX endpoint.

**B.** Add DynamoDB read replicas to handle the increased read load. Update the application to point to the read endpoint for the read replicas.

**C.** Double the number of read capacity units for the new messages table in DynamoDB. Continue to use the existing DynamoDB endpoint.

**D.** Add an Amazon ElastiCache for Redis cache to the application stack. Update the application to point to the Redis cache endpoint instead of DynamoDB.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Mobile chat app, DynamoDB datastore. Users muốn đọc messages với latency thấp nhất.
- **Existing Resources:** DynamoDB table.
- **Current Issue/Goal:** Minimal read latency, minimal application changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `as little latency as possible` | Cần in-memory caching. |
| `minimal application changes` | DAX: drop-in cache cho DynamoDB, chỉ cần đổi endpoint. |
| `DynamoDB Accelerator (DAX)` | In-memory cache, microsecond latency. |
| `ElastiCache` | Cũng là cache nhưng cần nhiều thay đổi code hơn. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Lowest latency, minimal changes
- **Constraints:** DynamoDB, minimal app changes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- DAX là in-memory cache đặc thù cho DynamoDB, cung cấp microsecond latency.
- Minimal application changes: chỉ cần thay đổi endpoint từ DynamoDB endpoint sang DAX endpoint. Code logic giữ nguyên.
- DAX xử lý cache hit/miss tự động.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- DynamoDB không có khái niệm "read replicas" như RDS. DynamoDB tự động scale.
- Không có "read endpoint" cho read replicas.

**❌ Đáp án C:**
- Tăng RCUs: cải thiện throughput nhưng không giảm latency đáng kể (vẫn là disk IO).
- Không phải giải pháp in-memory.

**❌ Đáp án D:**
- ElastiCache for Redis: cũng giảm latency nhưng cần nhiều thay đổi code hơn (quản lý cache logic manually).
- DAX là lựa chọn "minimal changes" hơn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DynamoDB read latency thấp + ít thay đổi code → DAX. ElastiCache cũng cache nhưng cần sửa code nhiều."*
