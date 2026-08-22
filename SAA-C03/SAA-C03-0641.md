# Question #641 - Topic 1

A company wants to monitor its AWS costs for financial review. The cloud operations team is designing an architecture in the AWS Organizations management account to query AWS Cost and Usage Reports for all member accounts. The team must run this query once a month and provide a detailed analysis of the bill. Which solution is the MOST scalable and cost-effective way to meet these requirements?

## Options

**A.** Enable Cost and Usage Reports in the management account. Deliver reports to Amazon Kinesis. Use Amazon EMR for analysis.

**B.** Enable Cost and Usage Reports in the management account. Deliver the reports to Amazon S3 Use Amazon Athena for analysis.

**C.** Enable Cost and Usage Reports for member accounts. Deliver the reports to Amazon S3 Use Amazon Redshift for analysis.

**D.** Enable Cost and Usage Reports for member accounts. Deliver the reports to Amazon Kinesis. Use Amazon QuickSight tor analysis.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Monitor AWS costs, query CUR for all member accounts once a month, detailed bill analysis.
- **Existing Resources:** AWS Organizations (management account + member accounts).
- **Current Issue/Goal:** Scalable and cost-effective querying of CUR data monthly.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Cost and Usage Reports (CUR)` | Detailed AWS billing data; enabled in management account covers all member accounts. |
| `once a month` | Low frequency → serverless query (Athena) is cost-effective. |
| `scalable and cost-effective` | Pay-per-query (Athena) vs always-on cluster (EMR, Redshift). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most scalable and cost-effective
- **Constraints:** Monthly query, cover all member accounts

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- CUR được enable ở management account → tổng hợp dữ liệu tất cả member accounts.
- Deliver CUR reports to S3.
- Amazon Athena: serverless, query bằng SQL, pay-per-query → chi phí thấp cho tần suất 1 lần/tháng.
- Athena tự động scale, không cần quản lý cluster.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Kinesis dùng cho real-time streaming, không phù hợp CUR báo cáo định kỳ hàng tháng.
- EMR cần cluster luôn chạy hoặc transient → tốn kém hơn Athena.

**❌ Đáp án C:**
- Enable CUR cho từng member account → bất tiện, management account đã tổng hợp được.
- Redshift là data warehouse luôn chạy → đắt hơn nhiều so với Athena cho tần suất 1 lần/tháng.

**❌ Đáp án D:**
- Kinesis không phù hợp CUR (dữ liệu batch, không real-time).
- QuickSight là BI tool, không phải công cụ query trực tiếp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CUR + S3 + Athena = serverless billing analysis. CUR in management account covers all."*
