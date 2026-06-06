# Question #17 - Topic 1

A company is implementing a new business application. The application runs on two Amazon EC2 instances and uses an Amazon S3 bucket for document storage. A solutions architect needs to ensure that the EC2 instances can access the S3 bucket. What should the solutions architect do to meet this requirement?

## Options

**A.** Create an IAM role that grants access to the S3 bucket. Attach the role to the EC2 instances.

**B.** Create an IAM policy that grants access to the S3 bucket. Attach the policy to the EC2 instances.

**C.** Create an IAM group that grants access to the S3 bucket. Attach the group to the EC2 instances.

**D.** Create an IAM user that grants access to the S3 bucket. Attach the user account to the EC2 instances.



## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty đang triển khai ứng dụng kinh doanh mới.
- **Existing Resources:** Hai `Amazon EC2` instances và một `Amazon S3` bucket để lưu trữ tài liệu.
- **Current Issue/Goal:** Đảm bảo các `EC2` instances có thể truy cập được `S3` bucket một cách an toàn và tuân thủ AWS best practice.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `IAM role` | Đối tượng ủy quyền tạm thời, có thể gán cho dịch vụ AWS như `EC2` để cấp quyền mà không cần hard-code credentials. |
| `IAM policy` | Tài liệu JSON định nghĩa quyền hạn (permissions); phải được gán vào `role`, `user`, hoặc `group`. |
| `IAM group` | Tập hợp các `IAM user`; chỉ dùng để quản lý người dùng, không thể gán cho AWS resources. |
| `IAM user` | Identity dành cho con người hoặc ứng dụng bên ngoài AWS; không nên dùng cho `EC2`. |
| `Instance Profile` | Container giúp gán `IAM role` cho `EC2 instance` trong quá trình launch. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Best practice implementation.
- **Constraints:** Cần cấp quyền truy cập `S3` cho `EC2` mà không sử dụng hard-coded credentials.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** Tạo một `IAM role` có `IAM policy` cho phép truy cập `S3` bucket, sau đó gán (`attach`) `role` đó cho các `EC2 instances` thông qua `instance profile`. Các ứng dụng chạy trên `EC2` sẽ tự động nhận được temporary credentials từ `IAM role` thông qua `EC2 Instance Metadata Service`, đảm bảo an toàn và dễ quản lý. Đây là best practice chuẩn của AWS khi compute resources cần truy cập dịch vụ AWS khác.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** `IAM policy` chỉ là tài liệu định nghĩa quyền, không thể được gán trực tiếp vào `EC2 instance`. Policy phải được gán vào một `IAM role`, rồi `role` mới được gán cho `EC2`.
**❌ Đáp án C:** `IAM group` chỉ dùng để nhóm các `IAM user` nhằm quản lý quyền cho con người. Không thể gán `IAM group` cho `EC2 instances` hay bất kỳ AWS resource nào.
**❌ Đáp án D:** `IAM user` không được thiết kế để gán cho `EC2 instances`. Nếu dùng `IAM user` sẽ buộc phải lưu trữ access key và secret key trực tiếp trên instance (hard-code), gây rủi ro bảo mật cao và khó khăn trong việc rotation credentials.

## 6. MẸO GHI NHỚ
🧠 *`EC2` cần quyền truy cập AWS service (như `S3`) → luôn dùng `IAM Role` + `Instance Profile`. Không bao giờ attach `policy`, `group`, hay `user` trực tiếp cho `EC2`. Nhớ công thức: Compute resource (`EC2`, `Lambda`, `ECS`...) cần access AWS API = `IAM Role`.*


 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty đang triển khai ứng dụng kinh doanh mới trên AWS.
- **Existing Resources:** Hai `Amazon EC2 instances` và một `Amazon S3 bucket` dùng để lưu trữ tài liệu.
- **Current Issue/Goal:** Đảm bảo các `EC2 instances` có thể truy cập `S3 bucket` một cách an toàn, tuân thủ `AWS best practice` và giảm thiểu `operational overhead`.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `IAM role` | Một `identity` của AWS cho phép ủy quyền tạm thời. Có thể gán trực tiếp cho `EC2 instances` thông qua `instance profile`. |
| `IAM policy` | Tài liệu JSON định nghĩa `permissions`. Không thể `attach` trực tiếp vào `EC2 instance`; bắt buộc phải gán vào `IAM role`, `IAM user`, hoặc `IAM group`. |
| `IAM group` | Chỉ dùng để nhóm các `IAM user` nhằm quản lý quyền truy cập cho con người. Không thể gán cho `AWS resources` như `EC2`. |
| `IAM user` | `Identity` dành cho con người hoặc ứng dụng bên ngoài AWS. Việc dùng `IAM user` trên `EC2` đòi hỏi lưu trữ `access key` và `secret key`, gây rủi ro bảo mật. |
| `Instance profile` | Container tự động tạo ra khi gán `IAM role` cho `EC2`, giúp instance nhận `temporary credentials`. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most secure / Least operational overhead / AWS best practice.
- **Constraints:** Không được sử dụng `hard-coded credentials`; cần cấp quyền cho `EC2 instances` một cách native trên AWS.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- `Amazon EC2 instances` cần quyền truy cập `Amazon S3` → cách chuẩn là sử dụng `IAM role`.
- Khi tạo một `IAM role` với `trust policy` cho phép `EC2` `assume role`, và gán `IAM policy` cho phép truy cập `S3 bucket`, sau đó `attach` `role` này vào các `EC2 instances` (thông qua `instance profile`), các ứng dụng trên instance sẽ tự động nhận được `temporary credentials` qua `EC2 Instance Metadata Service` (`IMDS`).
- Điều này loại bỏ nhu cầu quản lý `long-term credentials`, giảm `operational overhead` và tăng cường bảo mật.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- `IAM policy` chỉ là tài liệu định nghĩa `permissions`, không phải là một `identity` có thể được `attach` trực ti
