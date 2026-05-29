# Question #25 - Topic 1

A company is designing an application. The application uses an AWS Lambda function to receive information through Amazon API Gateway and to store the information in an Amazon Aurora PostgreSQL database. During the proof-of-concept stage, the company has to increase the Lambda quotas significantly to handle the high volumes of data that the company needs to load into the database. A solutions architect must recommend a new design to improve scalability and minimize the configuration effort. Which solution will meet these requirements?

## Options

**A.** Refactor the Lambda function code to Apache Tomcat code that runs on Amazon EC2 instances. Connect the database by using native Java Database Connectivity (JDBC) drivers.

**B.** Change the platform from Aurora to Amazon DynamoDProvision a DynamoDB Accelerator (DAX) cluster. Use the DAX client SDK to point the existing DynamoDB API calls at the DAX cluster.

**C.** Set up two Lambda functions. Configure one function to receive the information. Configure the other function to load the information into the database. Integrate the Lambda functions by using Amazon Simple Notification Service (Amazon SNS).

**D.** Set up two Lambda functions. Configure one function to receive the information. Configure the other function to load the information into the database. Integrate the Lambda functions by using an Amazon Simple Queue Service (Amazon SQS) queue.



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ứng dụng sử dụng `API Gateway` kích hoạt `Lambda` để nhận thông tin và ghi trực tiếp vào `Aurora PostgreSQL`.
- **Existing Resources:** `API Gateway`, `AWS Lambda`, `Amazon Aurora PostgreSQL`.
- **Current Issue/Goal:** Trong giai đoạn PoC, công ty phải tăng đáng kể `Lambda` quotas (giới hạn concurrency) để xử lý lưu lượng dữ liệu lớn cần ghi vào database. Cần thiết kế mới để cải thiện khả năng mở rộng (scalability) và giảm thiểu công sức cấu hình.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `Lambda` quotas | Giới hạn concurrent executions của `Lambda`; dễ bị cạn kiệt khi traffic đồng thời cao. |
| High volumes of data | Lưu lượng lớn đòi hỏi cơ chế buffer hoặc xử lý bất đồng bộ để tránh quá tải downstream. |
| `Aurora PostgreSQL` | Database quan hệ có giới hạn số kết nối đồng thời (connection limit), dễ bị quá tải nếu ghi trực tiếp từ hàng nghìn `Lambda` concurrent. |
| Minimize configuration effort | Ưu tiên các dịch vụ managed, serverless, dễ triển khai không cần quản lý hạ tầng. |
| Improve scalability | Thiết kế cần chịu được traffic spike mà không phụ thuộc vào việc tăng quota thủ công. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Architecture redesign / Scalability & Decoupling.
- **Constraints:** Xử lý được lưu lượng cao, giảm thiểu cấu hình, không làm quá tải `Aurora PostgreSQL`, khắc phục việc phải tăng `Lambda` quota liên tục.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**
**Giải thích:** Tách thành hai `Lambda` functions với `Amazon SQS` ở giữa. `Lambda` thứ nhất (receiver) nhận request từ `API Gateway` và đẩy message vào `SQS` queue. `Lambda` thứ hai (loader) poll message từ `SQS` và ghi vào `Aurora PostgreSQL`. `SQS` đóng vai trò **buffer** để hấp thụ traffic cao từ phía trên mà không bị giới hạn bởi `Lambda` concurrency quota hay database connection limit. Đồng thời, có thể cấu hình **reserved concurrency** cho `Lambda` loader để điều tiết tốc độ ghi, tránh làm sập `Aurora`. Giải pháp này hoàn toàn serverless, dễ cấu hình (chỉ cần trigger `SQS` cho `Lambda`), đáp ứng yêu cầu minimize effort và cải thiện scalability.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** Chuyển sang `EC2` + `Apache Tomcat` + `JDBC`. Việc quản lý `EC2` instances (patching, scaling, connection pooling, cân bằng tải) tạo ra operational overhead rất lớn, hoàn toàn trái ngược với yêu cầu **minimize configuration effort**. Hơn nữa, đây không phải là cách tối ưu để scale so với mô hình event-driven.

**❌ Đáp án B:** Chuyển từ `Aurora PostgreSQL` sang `DynamoDB` + `DAX`. Thay đổi nền tảng database là một công việc khổng lồ (thay đổi schema, data model, rewrite logic), hoàn toàn không phải **minimize configuration effort**. Đặc biệt, `DAX` (`DynamoDB Accelerator`) chỉ dùng để cache **read operations**, không hỗ trợ tăng tốc **write operations** (loading data). Do đó, giải pháp này không giải quyết được bài toán ghi dữ liệu lớn.

**❌ Đáp án C:** Dùng `Amazon SNS` để tích h
