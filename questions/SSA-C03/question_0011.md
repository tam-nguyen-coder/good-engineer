# Question #11 - Topic 1

A company has an application that runs on Amazon EC2 instances and uses an Amazon Aurora database. The EC2 instances connect to the database by using user names and passwords that are stored locally in a file. The company wants to minimize the operational overhead of credential management. What should a solutions architect do to accomplish this goal?

## Options

**A.** Use AWS Secrets Manager. Turn on automatic rotation.

**B.** Use AWS Systems Manager Parameter Store. Turn on automatic rotation.

**C.** Create an Amazon S3 bucket to store objects that are encrypted with an AWS Key Management Service (AWS KMS) encryption key. Migrate the credential file to the S3 bucket. Point the application to the S3 bucket.

**D.** Create an encrypted Amazon Elastic Block Store (Amazon EBS) volume for each EC2 instance. Attach the new EBS volume to each EC2 instance. Migrate the credential file to the new EBS volume. Point the application to the new EBS volume.



## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty có application chạy trên `Amazon EC2` instances và sử dụng `Amazon Aurora` database. Các instance kết nối tới database bằng user name và password được lưu trữ cục bộ trong một file trên EC2.
- **Existing Resources:** `EC2 instances`, `Amazon Aurora database`
- **Current Issue/Goal:** Công ty muốn **giảm thiểu operational overhead** trong việc quản lý credential (username/password) cho kết nối database.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `Amazon EC2` + `Amazon Aurora` | Kiến trúc 2 tầng cơ bản: compute + managed relational database |
| user names and passwords stored locally | Anti-pattern: hardcoded/flat-file credential trên instance, khó bảo mật và tốn công rotate |
| minimize the operational overhead | Yêu cầu giảm thao tác thủ công, hướng tới tự động hóa |
| credential management | Quản lý vòng đời của secrets (lưu trữ, truy xuất, rotation) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Best practice / Solution selection
- **Constraints:** Giảm thiểu operational overhead; cần giải pháp quản lý credentials hiệu quả cho DB connection từ EC2.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** `AWS Secrets Manager` là dịch vụ chuyên biệt để quản lý secrets (đặc biệt là database credentials). Nó tích hợp native với `Amazon Aurora`, cho phép `EC2` retrieve credentials qua API/SDK thay vì đọc file local. Đặc biệt, **automatic rotation** là tính năng built-in của `Secrets Manager`, giúp tự động thay đổi password định kỳ mà không cần viết thêm script hay quản lý infrastructure phụ, từ đó giảm thiểu tối đa operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** `AWS Systems Manager Parameter Store` có thể lưu `SecureString`, nhưng **không hỗ trợ automatic rotation cho secrets một cách native**. Để rotate credential trong Parameter Store, cần triển khai thêm `Lambda` và automation tự viết, làm tăng operational overhead. `Secrets Manager` mới là lựa chọn đúng khi đề bài nhấn mạnh rotation và giảm overhead quản lý DB credentials.

**❌ Đáp án C:** Dùng `Amazon S3` + `KMS` encryption chỉ mã hóa file credentials khi lưu trữ, nhưng không giải quyết được vấn đề quản lý vòng đời credential. Application vẫn phải fetch file từ S3, không có tính năng automatic rotation, và vẫn mang nặng tính thủ công (operational overhead không giảm).

**❌ Đáp án D:** `Amazon EBS` encrypted volume chỉ cung cấp **encryption at rest** cho dữ liệu lưu trên instance. Credentials vẫn nằm trong file local, vẫn phải quản lý thủ công từng volume trên từng instance, và hoàn toàn không có khả năng automatic rotation. Đây là giải pháp kém nhất về operational overhead.

## 6. MẸO GHI NHỚ
🧠 *Trong đề thi `SAA-C03`, khi thấy yêu cầu quản lý **database credentials** + **automatic rotation** + **giảm operational overhead** → chọn `AWS Secrets Manager`. `Systems Manager Parameter Store` dùng cho configuration/parameters thông thường, không phải giải pháp rotate DB secrets chuyên sâu.*


 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ứng dụng chạy trên `Amazon EC2 instances` và sử dụng `Amazon Aurora database`. Các `EC2 instances` kết nối đến database bằng cách sử dụng username và password được lưu trữ locally trong một file trên disk.
- **Existing Resources:** `Amazon EC2 instances`, `Amazon Aurora database`, file chứa credentials lưu trên local disk của các instances.
- **Current Issue/Goal:** Công ty muốn giảm thiểu `operational overhead` trong việc quản lý credentials, đặc biệt là việc lưu trữ và cập nhật mật khẩu thủ công trên nhiều instances.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Amazon EC2` + `Amazon Aurora` | Kiến trúc 2 tầng cần quản lý database credentials một cách tập trung |
| user names and passwords stored locally | `Hard-coded` / local storage → rủi ro bảo mật và khó duy trì |
| minimize the operational overhead | Cần một `managed service` có khả năng tự động hóa, thay vì quản lý thủ công |
| automatic rotation | Tính năng then chốt; chỉ có sẵn dưới dạng `native` cho database trên `AWS Secrets Manager` |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Minimize operational overhead / Operationally efficient
- **Constraints:** Credentials dùng cho `Aurora`, ứng dụng chạy trên `EC2`, cần giảm thiểu can thiệp thủ công

## 4. ĐÁP
