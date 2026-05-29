# Question #280 - Topic 1

A company is using Amazon CloudFront with its website. The company has enabled logging on the CloudFront distribution, and logs are saved in one of the company's Amazon S3 buckets. The company needs to perform advanced analyses on the logs and build visualizations. What should a solutions architect do to meet these requirements?

## Options

**A.** Use standard SQL queries in Amazon Athena to analyze the CloudFront logs in the S3 bucket. Visualize the results with AWS Glue.

**B.** Use standard SQL queries in Amazon Athena to analyze the CloudFront logs in the S3 bucket. Visualize the results with Amazon QuickSight.

**C.** Use standard SQL queries in Amazon DynamoDB to analyze the CloudFront logs in the S3 bucket. Visualize the results with AWS Glue.

**D.** Use standard SQL queries in Amazon DynamoDB to analyze the CloudFront logs in the S3 bucket. Visualize the results with Amazon QuickSight.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CloudFront logs in S3. Need advanced analysis + visualizations.
- **Existing Resources:** CloudFront distribution, S3 bucket with logs.
- **Current Issue/Goal:** Serverless analytics + visualization.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `advanced analyses` | **Amazon Athena** (SQL on S3) |
| `build visualizations` | **Amazon QuickSight** (BI) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Analytics / Visualization
- **Constraints:** SQL analysis, visualizations

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Athena** — query CloudFront logs (CSV/JSON) trực tiếp trên S3 bằng SQL.
- **QuickSight** — BI visualization, integrated với Athena.
- Both serverless → no infrastructure to manage.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Athena + Glue — Glue là ETL, không phải visualization tool.

**❌ Đáp án C:**
- DynamoDB — wrong service for S3 log analysis. Glue — wrong for visualization.

**❌ Đáp án D:**
- DynamoDB — wrong service for S3 log analysis.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Athena = SQL on S3. QuickSight = BI visualization. DynamoDB = wrong for log analysis"*
