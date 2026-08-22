# Question #609 - Topic 1

A company is building a data analysis platform on AWS by using AWS Lake Formation. The platform will ingest data from different sources such as Amazon S3 and Amazon RDS. The company needs a secure solution to prevent access to portions of the data that contain sensitive information. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create an IAM role that includes permissions to access Lake Formation tables.

**B.** Create data filters to implement row-level security and cell-level security.

**C.** Create an AWS Lambda function that removes sensitive information before Lake Formation ingests the data.

**D.** Create an AWS Lambda function that periodically queries and removes sensitive information from Lake Formation tables.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Lake Formation platform ingest data từ S3 và RDS. Cần prevent access to sensitive data.
- **Existing Resources:** AWS Lake Formation, data sources (S3, RDS).
- **Current Issue/Goal:** Row-level và cell-level security cho sensitive data, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Lake Formation` | Data lake service, hỗ trợ fine-grained access control. |
| `prevent access to portions of data` | Row-level security (RLS) và cell-level security. |
| `sensitive information` | Cần masking/filter ở mức dữ liệu. |
| `least operational overhead` | Lake Formation Data Filters là built-in feature. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Prevent access to sensitive portions of data, Lake Formation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Lake Formation cung cấp built-in Data Filters cho row-level và cell-level security.
- Cho phép define filter expressions để giới hạn dữ liệu user có thể truy vấn.
- Hoàn toàn managed, không cần code thêm.
- Tích hợp với IAM và LF-Tags để quản lý permissions tập trung.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- IAM role chỉ kiểm soát truy cập ở mức table, không thể filter rows/cells.

**❌ Đáp án C:**
- Lambda remove sensitive data trước khi ingest → mất dữ liệu permanently, không linh hoạt, operational overhead cao hơn.

**❌ Đáp án D:**
- Lambda query và remove periodically → reactive, không real-time, có thể lộ dữ liệu trong khoảng thời gian giữa các lần chạy.
- Operational overhead cao hơn nhiều.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lake Formation + sensitive data → Data Filters (row-level + cell-level). Built-in, không cần Lambda."*
