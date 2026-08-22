# Question #643 - Topic 1

A company runs several websites on AWS for its different brands. Each website generates tens of gigabytes of web traffic logs each day. A solutions architect needs to design a scalable solution to give the company's developers the ability to analyze traffic patterns across all the company's websites. This analysis by the developers will occur on demand once a week over the course of several months. The solution must support queries with standard SQL. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Store the logs in Amazon S3. Use Amazon Athena tor analysis.

**B.** Store the logs in Amazon RDS. Use a database client for analysis.

**C.** Store the logs in Amazon OpenSearch Service. Use OpenSearch Service for analysis.

**D.** Store the logs in an Amazon EMR cluster Use a supported open-source framework for SQL-based analysis.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multiple websites, tens of GB logs/day, analyze traffic patterns across all brands on demand once a week.
- **Existing Resources:** Websites generating web traffic logs.
- **Current Issue/Goal:** Scalable, cost-effective SQL querying of logs with weekly frequency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `once a week` | Tần suất thấp → serverless query (Athena) tiết kiệm nhất. |
| `standard SQL` | Athena sử dụng SQL chuẩn (Presto/Trino). |
| `most cost-effective` | Tránh luôn chạy cluster (OpenSearch, EMR, RDS). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Standard SQL, on-demand weekly, data in S3

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Logs lưu trên S3 → chi phí lưu trữ thấp.
- Dùng Athena query trực tiếp trên S3, pay-per-query → rất rẻ với tần suất 1 lần/tuần.
- Athena hỗ trợ standard SQL, không cần quản lý infrastructure.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- RDS chạy 24/7 → tốn kém. Logs tens of GB/day → nhanh đầy storage.
- RDS không tối ưu cho log analysis.

**❌ Đáp án C:**
- OpenSearch Service cluster chạy liên tục → chi phí cao hơn Athena.
- OpenSearch dùng query DSL, không phải SQL chuẩn (dù có thể dùng SQL plugin nhưng không native).

**❌ Đáp án D:**
- EMR cluster cần quản lý và chạy (dù transient) → chi phí và operational overhead cao hơn Athena.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Logs in S3 + Athena = serverless SQL, pay-per-query. Weekly analysis = Athena is cheapest."*
