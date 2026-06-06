# Question #2 - Topic 1

A company needs the ability to analyze the log files of its proprietary application. The logs are stored in JSON format in an Amazon S3 bucket. Queries will be simple and will run on-demand. A solutions architect needs to perform the analysis with minimal changes to the existing architecture. What should the solutions architect do to meet these requirements with the LEAST amount of operational overhead?

## Options

**A.** Use Amazon Redshift to load all the content into one place and run the SQL queries as needed.

**B.** Use Amazon CloudWatch Logs to store the logs. Run SQL queries as needed from the Amazon CloudWatch console.

**C.** Use Amazon Athena directly with Amazon S3 to run the queries as needed.

**D.** Use AWS Glue to catalog the logs. Use a transient Apache Spark cluster on Amazon EMR to run the SQL queries as needed.


## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty cần phân tích log files của ứng dụng nội bộ (proprietary application).
- **Existing Resources:** Log được lưu ở định dạng `JSON` trong `Amazon S3 bucket`.
- **Current Issue/Goal:** Cần thực hiện các truy vấn đơn giản (simple), chạy theo nhu cầu (on-demand), với ít thay đổi nhất đến kiến trúc hiện tại và **ít operational overhead nhất**.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `JSON` in `S3` | Dữ liệu đã ở data lake, chưa có cấu trúc/schema rõ ràng |
| Simple queries, on-demand | Không cần xử lý phức tạp hoặc chạy liên tục |
| Minimal changes | Cần giữ nguyên việc lưu trữ hiện tại trên `S3` |
| LEAST operational overhead | Ưu tiên giải pháp serverless, không cần provision/maintain infrastructure |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Best architecture / Least operational overhead
- **Constraints:** Không thay đổi nơi lưu trữ hiện tại (`S3`), truy vấn đơn giản và tức thì, không quản lý server/cluster

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**
**Giải thích:** `Amazon Athena` là dịch vụ serverless cho phép chạy truy vấn `SQL` trực tiếp trên dữ liệu lưu trong `Amazon S3`. Vì log đã ở định dạng `JSON` trên `S3`, solutions architect chỉ cần trỏ `Athena` đến `S3 bucket` (qua `AWS Glue Data Catalog` hoặc trực tiếp tạo table schema) là có thể query ngay lập tức. Không cần di chuyển dữ liệu, không cần cung cấp hay quản lý server/cluster, chi phí chỉ tính theo lượng dữ liệu quét (pay-per-query). Điều này đáp ứng hoàn hảo yêu cầu **minimal changes** và **least operational overhead**.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (`Amazon Redshift`):** `Redshift` yêu cầu phải load dữ liệu từ `S3` vào data warehouse, thiết kế schema, và quản lý cluster (hoặc cấu hình `Redshift Serverless`). Đây là operational overhead cao và thay đổi lớn so với việc để dữ liệu nguyên trên `S3`, không phù hợp cho các truy vấn đơn giản, on-demand.

**❌ Đáp án B (`Amazon CloudWatch Logs`):** `CloudWatch Logs` dùng để thu thập log real-time từ ứng dụng, không phải để phân tích các file `JSON` đã lưu sẵn trong `S3`. Để dùng được, công ty phải thay đổi kiến trúc hiện tại (đẩy log lên `CloudWatch` thay vì `S3`), vi phạm yêu cầu "minimal changes".

**❌ Đáp án D (`AWS Glue` + `EMR`):** Mặc dù `AWS Glue` có thể catalog dữ liệu và `EMR` có thể chạy `Spark SQL`, việc spin up một `transient Apache Spark cluster` trên `EMR` vẫn đòi hỏi cấu hình cluster, chờ khởi động, và quản lý vòng đời (dù là transient). Operational overhead cao hơn nhiều so với `Athena` cho nhu cầu query đơn giản, on-demand.

## 6. MẸO GHI NHỚ
🧠 *"S3 + SQL + On-demand = Athena"*. Nếu đề bài cho dữ liệu trên `S3`, cần query bằng `SQL`, không đổi kiến trúc, và ít overhead nhất → nghĩ ngay đến `Amazon Athena`. `Athena` được sinh ra để query trực tiếp data lake trên `S3` mà không cần ETL hay quản lý infrastructure.
