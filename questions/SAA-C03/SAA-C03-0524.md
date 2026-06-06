# Question #524 - Topic 1

A company wants to analyze and troubleshoot Access Denied errors and Unauthorized errors that are related to IAM permissions. The company has AWS CloudTrail turned on. Which solution will meet these requirements with the LEAST effort?

## Options

**A.** Use AWS Glue and write custom scripts to query CloudTrail logs for the errors.

**B.** Use AWS Batch and write custom scripts to query CloudTrail logs for the errors.

**C.** Search CloudTrail logs with Amazon Athena queries to identify the errors.

**D.** Search CloudTrail logs with Amazon QuickSight. Create a dashboard to identify the errors.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần analyze và troubleshoot Access Denied / Unauthorized errors từ IAM permissions. CloudTrail đã được bật.
- **Existing Resources:** AWS CloudTrail (đã enabled).
- **Current Issue/Goal:** Tìm errors liên quan IAM permissions với ít effort nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `CloudTrail logs` | Ghi lại tất cả API calls, bao gồm Access Denied errors |
| `Athena` | Query dữ liệu trực tiếp từ S3 bằng SQL, không cần ETL |
| `least effort` | Giải pháp đơn giản nhất, không cần custom code/infrastructure |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least effort
- **Constraints:** CloudTrail đã enabled, cần identify IAM errors

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- CloudTrail logs được lưu trong S3 buckets.
- Amazon Athena cho phép query trực tiếp CloudTrail logs bằng SQL chuẩn mà không cần ETL.
- Athena có sẵn schema cho CloudTrail logs (tự động nếu dùng CloudTrail console setup) → chỉ cần viết SQL query đơn giản: `SELECT * FROM cloudtrail_logs WHERE errorcode = 'AccessDenied' OR errorcode = 'Unauthorized'`.
- Serverless, pay-per-query, không cần quản lý infrastructure.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS Glue cần thiết lập crawler, catalog, và viết custom scripts → effort nhiều hơn Athena.

**❌ Đáp án B:**
- AWS Batch cần tạo compute environment, job definition, và viết custom scripts → effort cao.

**❌ Đáp án D:**
- QuickSight là BI tool dùng để visualize dữ liệu, không phải để query và tìm kiếm errors cụ thể. Cần setup SPICE dataset và dashboard → effort nhiều hơn.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"CloudTrail logs in S3 + Athena SQL = query Access Denied errors in seconds."*
