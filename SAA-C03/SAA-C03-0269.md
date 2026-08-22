# Question #269 - Topic 1

An ecommerce company has noticed performance degradation of its Amazon RDS based web application. The performance degradation is attributed to an increase in the number of read-only SQL queries triggered by business analysts. A solutions architect needs to solve the problem with minimal changes to the existing web application. What should the solutions architect recommend?

## Options

**A.** Export the data to Amazon DynamoDB and have the business analysts run their queries.

**B.** Load the data into Amazon ElastiCache and have the business analysts run their queries.

**C.** Create a read replica of the primary database and have the business analysts run their queries.

**D.** Copy the data into an Amazon Redshift cluster and have the business analysts run their queries.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce app, RDS performance degradation from analysts' read-only SQL queries.
- **Existing Resources:** RDS.
- **Current Issue/Goal:** Offload read queries, minimal app changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `read-only SQL queries` | **Read replica** — offload reads |
| `minimal changes` | Read replica không thay đổi app |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / Performance
- **Constraints:** Read-heavy, minimal changes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Read replica** — copy của primary DB, dùng cho read queries.
- Analysts query read replica → không ảnh hưởng primary (application).
- Minimal change — chỉ cần cung cấp endpoint của read replica cho analysts.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Export to DynamoDB — major change, schema khác.

**❌ Đáp án B:**
- ElastiCache — cần app changes, không phù hợp SQL queries.

**❌ Đáp án D:**
- Redshift — major change, ETL pipeline.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Read replica = offload read queries with minimal change. ElastiCache = caching (not SQL)"*
