# Question #481 - Topic 1

A company hosts a three-tier web application in the AWS Cloud. A Multi-AZAmazon RDS for MySQL server forms the database layer Amazon ElastiCache forms the cache layer. The company wants a caching strategy that adds or updates data in the cache when a customer adds an item to the database. The data in the cache must always match the data in the database. Which solution will meet these requirements?

## Options

**A.** Implement the lazy loading caching strategy

**B.** Implement the write-through caching strategy

**C.** Implement the adding TTL caching strategy

**D.** Implement the AWS AppConfig caching strategy

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Three-tier web app với RDS MySQL Multi-AZ (DB layer) và ElastiCache (cache layer). Cần strategy: khi customer thêm item vào DB thì cache cũng được add/update ngay lập tức. Dữ liệu trong cache phải luôn khớp với DB.
- **Existing Resources:** RDS for MySQL Multi-AZ, ElastiCache cluster.
- **Current Issue/Goal:** Chọn caching strategy đảm bảo cache luôn consistent với DB (write-through).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `adds or updates data in the cache when a customer adds an item to the database` | Write-through: application writes to DB → cache được update đồng bộ. |
| `cache must always match the data in the database` | Write-through đảm bảo data consistency. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Caching strategy selection
- **Constraints:** Cache phải luôn match DB, update ngay khi có write vào DB.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Write-through caching:** Khi application write data vào DB, cache cũng được write ngay lập tức → data luôn consistent.
- Dữ liệu trong cache luôn phản ánh đúng dữ liệu mới nhất trong DB.
- Phù hợp với yêu cầu "adds or updates data in the cache when a customer adds an item".

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Lazy loading:** Data chỉ được load vào cache khi có cache miss (read request). Cache không được update khi write vào DB → dữ liệu có thể stale cho đến lần đọc đầu tiên.

**❌ Đáp án C:**
- **Adding TTL:** Chỉ đơn giản là set time-to-live cho cache entries. Cache sẽ bị expire sau TTL nhưng không được update ngay khi DB thay đổi → không đảm bảo consistency.

**❌ Đáp án D:**
- **AWS AppConfig:** Dùng để quản lý application configuration (feature flags, config), không phải caching strategy cho database.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Write-through = write to DB → write to cache (consistent). Lazy loading = load on cache miss (stale data risk)."*
