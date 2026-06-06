# Question #4 - Topic 1

An application runs on an Amazon EC2 instance in a VPC. The application processes logs that are stored in an Amazon S3 bucket. The EC2 instance needs to access the S3 bucket without connectivity to the internet. Which solution will provide private network connectivity to Amazon S3?

## Options

**A.** Create a gateway VPC endpoint to the S3 bucket.

**B.** Stream the logs to Amazon CloudWatch Logs. Export the logs to the S3 bucket.

**C.** Create an instance profile on Amazon EC2 to allow S3 access.

**D.** Create an Amazon API Gateway API with a private link to access the S3 endpoint.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một ứng dụng chạy trên `Amazon EC2 instance` bên trong một `VPC`. Ứng dụng cần xử lý các log được lưu trữ trong `Amazon S3 bucket`.
- **Existing Resources:** `EC2 instance`, `S3 bucket`, `VPC`.
- **Current Issue/Goal:** `EC2 instance` cần truy cập `S3 bucket` nhưng **không được có kết nối internet**. Cần tìm giải pháp cung cấp `private network connectivity` đến `Amazon S3`.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `Amazon EC2` | Máy chủ ảo chạy ứng dụng trong `VPC` |
| `Amazon S3` | Dịch vụ lưu trữ object chứa log |
| `VPC` | Mạng riêng ảo cô lập |
| `without connectivity to the internet` | Không có `IGW`, `NAT Gateway`, hoặc public IP; thường nằm trong private subnet |
| `private network connectivity` | Kết nối qua mạng nội bộ AWS, không đi qua public internet |
| `Gateway VPC endpoint` | Điểm kết nối miễn phí cho phép VPC truy cập `S3` và `DynamoDB` qua `AWS backbone network` |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Kiến trúc kết nối mạng (Network Architecture / Private Connectivity)
- **Constraints:** Không được dùng internet; phải đảm bảo EC2 trong VPC giao tiếp được với S3 hoàn toàn qua private network.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** `Gateway VPC endpoint` là giải pháp chuẩn và tối ưu để các tài nguyên trong `VPC` (như `EC2`) truy cập `Amazon S3` mà không cần kết nối internet. Khi tạo Gateway endpoint cho S3, AWS tự động thêm prefix list vào `route table` của subnet, định tuyến lưu lượng đến S3 qua `AWS network backbone` thay vì qua internet. Giải pháp này **không tốn phí data transfer** và không yêu cầu `Internet Gateway`, `NAT Gateway`, hay `Elastic IP`.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** `CloudWatch Logs` là dịch vụ giám sát log, không phải giải pháp kết nối mạng. Việc stream log lên CloudWatch rồi export sang S3 không giải quyết được nhu cầu EC2 truy cập trực tiếp S3 qua private network. Hơn nữa, để gửi log đến CloudWatch, EC2 vẫn cần network connectivity đến CloudWatch endpoint.

**❌ Đáp án C:** `Instance profile` (IAM Role gắn vào EC2) chỉ cung cấp **quyền** (authorization) để gọi API S3, nhưng hoàn toàn không cung cấp **kết nối mạng** (network connectivity). Dù có quyền IAM, EC2 trong môi trường cô lập không có endpoint vẫn không thể đạt đến S3 qua mạng.

**❌ Đáp án D:** `Amazon API Gateway` dùng để xây dựng REST/API, không phải là cơ chế để một server truy cập trực tiếp `S3` như object storage. Việc dùng API Gateway + PrivateLink để "access the S3 endpoint" là kiến trúc sai mục đích, phức tạp và không đáp ứng yêu cầu truy cập S3 trực tiếp từ EC2.

## 6. MẸO GHI NHỚ
🧠 *Cần truy cập `S3` hoặc `DynamoDB` từ `VPC` mà không qua internet → Chọn ngay `Gateway VPC Endpoint`. Các dịch vụ AWS khác (như `CloudWatch`, `EC2 API`, `SSM`) thì dùng `Interface VPC Endpoint (AWS PrivateLink)`.*
