# Question #51 - Topic 1

A company is developing an application that provides order shipping statistics for retrieval by a REST API. The company wants to extract the shipping statistics, organize the data into an easy-to-read HTML format, and send the report to several email addresses at the same time every morning. Which combination of steps should a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Configure the application to send the data to Amazon Kinesis Data Firehose.

**B.** Use Amazon Simple Email Service (Amazon SES) to format the data and to send the report by email.

**C.** Create an Amazon EventBridge (Amazon CloudWatch Events) scheduled event that invokes an AWS Glue job to query the application's API for the data.

**D.** Create an Amazon EventBridge (Amazon CloudWatch Events) scheduled event that invokes an AWS Lambda function to query the application's API for the data.

**E.** Store the application data in Amazon S3. Create an Amazon Simple Notification Service (Amazon SNS) topic as an S3 event destination to send the report by email.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ứng dụng cung cấp shipping statistics qua REST API. Cần extract data, format HTML, gửi email báo cáo mỗi sáng.
- **Existing Resources:** REST API của application.
- **Current Issue/Goal:** Scheduled job mỗi sáng: query API → format HTML → gửi email.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `at the same time every morning` | Scheduled event → EventBridge (CloudWatch Events) |
| `organize the data into HTML format` | Cần formatting, SES hỗ trợ HTML email |
| `send the report to several email addresses` | SES có thể gửi email đến nhiều recipients |
| `REST API` | Cần Lambda để gọi API (Glue không phù hợp) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless scheduling + notification
- **Constraints:** Chọn 2 đáp án.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và D**

**Giải thích:**
- **D: EventBridge scheduled event + Lambda** — Lambda chạy schedule mỗi sáng, gọi REST API của ứng dụng để lấy shipping statistics. Đây là pattern chuẩn cho cron job serverless.
- **B: Amazon SES** — Nhận dữ liệu từ Lambda, format thành HTML, gửi email đến nhiều địa chỉ. SES hỗ trợ HTML email và bulk sending.

Luồng: EventBridge (schedule) → Lambda (query API) → SES (format HTML + send email)

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Kinesis Data Firehose dùng cho streaming data real-time, không phải scheduled report.

**❌ Đáp án C:**
- AWS Glue là ETL service cho data transformation trên data lake, không phải để gọi REST API định kỳ. Overkill và tốn kém.

**❌ Đáp án E:**
- SNS không có khả năng format HTML.
- S3 event destination trigger khi object được tạo, không phải scheduled — không đúng yêu cầu "cùng giờ mỗi sáng".
- SNS gửi email không mạnh mẽ bằng SES (SNS email chỉ là notification đơn giản).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EventBridge + Lambda = cron job serverless; SES = email formatting + sending"*
