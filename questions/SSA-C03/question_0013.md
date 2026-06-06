# Question #13 - Topic 1

A company performs monthly maintenance on its AWS infrastructure. During these maintenance activities, the company needs to rotate the credentials for its Amazon RDS for MySQL databases across multiple AWS Regions. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Store the credentials as secrets in AWS Secrets Manager. Use multi-Region secret replication for the required Regions. Configure Secrets Manager to rotate the secrets on a schedule.

**B.** Store the credentials as secrets in AWS Systems Manager by creating a secure string parameter. Use multi-Region secret replication for the required Regions. Configure Systems Manager to rotate the secrets on a schedule.

**C.** Store the credentials in an Amazon S3 bucket that has server-side encryption (SSE) enabled. Use Amazon EventBridge (Amazon CloudWatch Events) to invoke an AWS Lambda function to rotate the credentials.

**D.** Encrypt the credentials as secrets by using AWS Key Management Service (AWS KMS) multi-Region customer managed keys. Store the secrets in an Amazon DynamoDB global table. Use an AWS Lambda function to retrieve the secrets from DynamoDB. Use the RDS API to rotate the secrets.



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty thực hiện bảo trì định kỳ hàng tháng trên hạ tầng `AWS`. Trong quá trình này, công ty cần xoay vòng (rotate) credentials cho các cơ sở dữ liệu `Amazon RDS for MySQL` được triển khai trên nhiều `AWS Regions`.
- **Existing Resources:** `Amazon RDS for MySQL` instances across multiple Regions.
- **Current Issue/Goal:** Tìm giải pháp cho phép rotate credentials trên nhiều Region với `LEAST operational overhead` (chi phí vận hành thấp nhất, ít can thiệp thủ công nhất).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `Rotate credentials` | Thay đổi định kỳ username/password để giảm thiểu rủi ro bảo mật |
| `Multi-Region` | Yêu cầu đồng bộ/xử lý trên nhiều vùng AWS khác nhau |
| `AWS Secrets Manager` | Dịch vụ quản lý bí mật tập trung, hỗ trợ tích hợp sẵn việc xoay vòng cho `RDS` |
| `AWS Systems Manager Parameter Store` | Kho lưu trữ tham số/cấu hình, không chuyên về tự động xoay vòng secrets |
| `LEAST operational overhead` | Ưu tiên giải pháp fully managed, không cần viết code tùy chỉnh |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Solution architecture – Chọn dịch vụ phù hợp nhất để giảm thiểu vận hành.
- **Constraints:** 
  - Rotate credentials cho `RDS for MySQL`.
  - Hoạt động trên nhiều `Regions`.
  - Lịch trình định kỳ (monthly).
  - Không được tạo ra nhiều gánh nặng vận hành (custom code, tự quản lý hạ tầng).

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** `AWS Secrets Manager` là dịch vụ được thiết kế chuyên biệt cho việc quản lý và tự động xoay vòng secrets. Giải pháp này đáp ứng yêu cầu với overhead thấp nhất vì:
- **Native `RDS` integration:** Hỗ trợ tích hợp sẵn với `Amazon RDS for MySQL`, cho phép tự động cập nhật cả secret lẫn database credentials mà không cần can thiệp thủ công.
- **Multi-Region secret replication:** Tính năng replicate secret sang nhiều `Region` một cách tự động, đảm bảo các ứng dụng ở mỗi `Region` đều truy cập được credentials mới nhất.
- **Built-in rotation on a schedule:** Cung cấp khả năng đặt lịch xoay vòng tự động bằng `AWS Lambda` function do AWS quản lý (managed rotation), loại bỏ nhu cầu viết và duy trì code tùy chỉnh.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** `AWS Systems Manager Parameter Store` (dù là `SecureString`) không phải là dịch vụ thiết kế cho việc tự động xoay vòng credentials của `RDS`. Parameter Store thiếu khả năng rotate tích hợp sẵn như `Secrets Manager`, và việc replicate multi-Region cũng không được hỗ trợ native như trong đáp án mô tả. Nếu cần rotate, ta thường phải tự viết script hoặc kết hợp với `Secrets Manager`, gây tăng overhead.

**❌ Đáp án C:** Lưu credentials trong `Amazon S3` không phải best practice cho secret management. Việc dùng `Amazon EventBridge` kích hoạt `AWS Lambda` để rotate đòi hỏi phải tự viết toàn bộ logic xoay vòng, xử lý lỗi, đảm bảo tính nhất quán trên multi-Region, tạo ra operational overhead rất lớn so với dịch vụ managed.

**❌ Đáp án D:** Dùng `Amazon DynamoDB global table` để lưu trữ secrets là anti-pattern. Dù có mã hóa bằng `AWS KMS multi-Region keys`, việc tự triển khai `AWS Lambda` để retrieve secrets và gọi `RDS API` để rotate yêu cầu rất nhiều công sức phát triển, vận hành, giám sát và xử lý lỗi. Đây là giải pháp custom với overhead cao nhất, hoàn toàn trái ngược với yêu cầu đề bài.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài nhắc đến việc rotate credentials cho `Amazon RDS`, `Amazon Redshift`, hoặc `Amazon DocumentDB` với yêu cầu overhead thấp nhất → Nghĩ ngay đến `AWS Secrets Manager` + multi-Region replication + built-in rotation. `Parameter Store` chỉ dùng cho configuration data, không phải cho secret rotation. Tránh mọi giải pháp custom (S3, DynamoDB + Lambda) vì luôn đi kèm operational overhead cao.*


