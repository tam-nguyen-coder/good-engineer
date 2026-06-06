# Question #3 - Topic 1

A company uses AWS Organizations to manage multiple AWS accounts for different departments. The management account has an Amazon S3 bucket that contains project reports. The company wants to limit access to this S3 bucket to only users of accounts within the organization in AWS Organizations. Which solution meets these requirements with the LEAST amount of operational overhead?

## Options

**A.** Add the aws PrincipalOrgID global condition key with a reference to the organization ID to the S3 bucket policy.

**B.** Create an organizational unit (OU) for each department. Add the aws:PrincipalOrgPaths global condition key to the S3 bucket policy.

**C.** Use AWS CloudTrail to monitor the CreateAccount, InviteAccountToOrganization, LeaveOrganization, and RemoveAccountFromOrganization events. Update the S3 bucket policy accordingly.

**D.** Tag each user that needs access to the S3 bucket. Add the aws:PrincipalTag global condition key to the S3 bucket policy.


# Question #3 - Topic 1

A company uses AWS Organizations to manage multiple AWS accounts for different departments. The management account has an Amazon S3 bucket that contains project reports. The company wants to limit access to this S3 bucket to only users of accounts within the organization in AWS Organizations. Which solution meets these requirements with the LEAST amount of operational overhead?

## Options

**A.** Add the aws PrincipalOrgID global condition key with a reference to the organization ID to the S3 bucket policy.

**B.** Create an organizational unit (OU) for each department. Add the aws:PrincipalOrgPaths global condition key to the S3 bucket policy.

**C.** Use AWS CloudTrail to monitor the CreateAccount, InviteAccountToOrganization, LeaveOrganization, and RemoveAccountFromOrganization events. Update the S3 bucket policy accordingly.

**D.** Tag each user that needs access to the S3 bucket. Add the aws:PrincipalTag global condition key to the S3 bucket policy.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty sử dụng `AWS Organizations` để quản lý nhiều `AWS account` cho các phòng ban khác nhau.
- **Existing Resources:** `Management account` chứa một `Amazon S3 bucket` lưu trữ project reports.
- **Current Issue/Goal:** Giới hạn quyền truy cập `S3 bucket` chỉ cho các user thuộc các account bên trong `AWS Organizations`, với **LEAST operational overhead** (ít vận hành nhất).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `AWS Organizations` | Dịch vụ quản lý tập trung nhiều AWS account |
| `Management account` | Account gốc tạo ra Organization |
| `aws:PrincipalOrgID` | Global condition key kiểm tra xem principal có thuộc Organization ID cụ thể không |
| `aws:PrincipalOrgPaths` | Global condition key kiểm tra OU path của principal trong Organization |
| `aws:PrincipalTag` | Global condition key kiểm tra tag gắn với principal |
| `S3 bucket policy` | Chính sách truy cập cấp bucket trong Amazon S3 |
| `Operational overhead` | Chi phí vận hành, bảo trì liên tục |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security & Access Control – Chọn giải pháp đơn giản, ít tốn công vận hành nhất.
- **Constraints:** 
  - Phải hoạt động với **tất cả account hiện tại và tương lai** trong Organization.
  - Không được yêu cầu cập nhật thủ công liên tục.
  - Bucket nằm ở `management account`, nhưng user truy cập từ các member account khác.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** Sử dụng global condition key `aws:PrincipalOrgID` trong `S3 bucket policy` là cách tiêu chuẩn và tối ưu nhất để giới hạn truy cập chỉ cho các principal (user/role) thuộc về một `AWS Organizations` cụ thể. 

Ví dụ policy:
```json
"Condition": {
  "StringEquals": {
    "aws:PrincipalOrgID": "o-xxxxxxxxxx"
  }
}
```

Ưu điểm:
- **Zero maintenance:** Khi có account mới được tạo hoặc mời vào Organization, chúng tự động được phép truy cập mà không cần sửa policy. Ngược lại, khi account rời Organization, quyền truy cập tự động bị từ chối.
- **Least privilege:** Chỉ cho phép đúng các account trong org.
- **Least operational overhead:** Chỉ cần thêm một dòng condition duy nhất vào bucket policy, không cần automation, tagging hay quản lý OU phức tạp.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** `aws:PrincipalOrgPaths` yêu cầu phải thiết kế cấu trúc `OU` (Organizational Unit) cho từng department và duy trì đường dẫn OU trong policy. Điều này là **không cần thiết** khi đề bài chỉ yêu cầu giới hạn ở cấp Organization (không phân biệt OU), tạo ra operational overhead cao hơn đáp án A.

**❌ Đáp án C:** Sử dụng `AWS CloudTrail` kết hợp với `EventBridge` và `Lambda` để tự động cập nhật bucket policy khi có sự kiện thay đổi account trong Organization là một kiến trúc over-engineered. Chi phí vận hành, giám sát và bảo trì code rất cao, hoàn toàn không phải "least operational overhead".

**❌ Đáp án D:** `aws:PrincipalTag` đòi hỏi phải gắn tag cho **từng user** trong **từng account** cần truy cập. Trong môi trường nhiều account và nhiều user, việc này không scalable, dễ sai sót, và yêu cầu quản lý tag liên tục → operational overhead rất lớn. Ngoài ra, cross-account access với principal tags còn phức tạp hơn vì phải truyền session tags qua AssumeRole.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài yêu cầu giới hạn truy cập resource cho toàn bộ account trong một `AWS Organizations` với ít vận hành nhất → Nghĩ ngay đến `aws:PrincipalOrgID`. Đây là "silver bullet" cho bài toán "chỉ cho phép bên trong org truy cập".*


 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty sử dụng `AWS Organizations` để quản lý nhiều `AWS account` cho các phòng ban khác nhau. `Management account` đang chứa một `Amazon S3 bucket` lưu trữ project reports.
- **Existing Resources:** `AWS Organizations`, `Management account`, `Amazon S3 bucket`.
- **Current Issue/Goal:** Giới hạn quyền truy cập `S3 bucket` chỉ cho các user thuộc các account bên trong `AWS Organizations`, đồng thời đảm bảo giải pháp có **LEAST operational overhead** (ít vận hành nhất).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `AWS Organizations` | Dịch vụ quản lý tập trung nhiều `AWS account` |
| `Management account` | Account gốc tạo ra và quản lý Organization |
| `aws:PrincipalOrgID` | `Global condition key` kiểm tra xem `principal` có thuộc `Organization ID` cụ thể hay không |
| `aws:PrincipalOrgPaths` | `Global condition key` kiểm tra đường dẫn `OU` của `principal` trong Organization |
| `aws:PrincipalTag` | `Global condition key` kiểm tra `tag` gắn với `principal` |
| `S3 bucket policy` | Chính sách truy cập cấp bucket trong `Amazon S3` |
| `Operational overhead` | Chi phí vận hành, bảo trì liên tục; đề bài yêu cầu tối thiểu hóa |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security & Access Control – Chọn giải pháp bảo mật với ít vận hành nhất.
- **Constraints:** 
  - Phải áp dụng cho **tất cả account hiện tại và t
