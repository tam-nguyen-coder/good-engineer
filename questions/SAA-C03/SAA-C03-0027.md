# Question #27 - Topic 1

A company is launching a new application and will display application metrics on an Amazon CloudWatch dashboard. The company's product manager needs to access this dashboard periodically. The product manager does not have an AWS account. A solutions architect must provide access to the product manager by following the principle of least privilege. Which solution will meet these requirements?

## Options

**A.** Share the dashboard from the CloudWatch console. Enter the product manager's email address, and complete the sharing steps. Provide a shareable link for the dashboard to the product manager.

**B.** Create an IAM user specifically for the product manager. Attach the CloudWatchReadOnlyAccess AWS managed policy to the user. Share the new login credentials with the product manager. Share the browser URL of the correct dashboard with the product manager.

**C.** Create an IAM user for the company's employees. Attach the ViewOnlyAccess AWS managed policy to the IAM user. Share the new login credentials with the product manager. Ask the product manager to navigate to the CloudWatch console and locate the dashboard by name in the Dashboards section.

**D.** Deploy a bastion server in a public subnet. When the product manager requires access to the dashboard, start the server and share the RDP credentials. On the bastion server, ensure that the browser is configured to open the dashboard URL with cached AWS credentials that have appropriate permissions to view the dashboard.



## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty triển khai ứng dụng mới và hiển thị metrics trên `Amazon CloudWatch` dashboard. Giám đốc sản phẩm (product manager) cần xem dashboard này định kỳ nhưng không có AWS account.
- **Existing Resources:** `Amazon CloudWatch` dashboard đã được tạo cho ứng dụng mới.
- **Current Issue/Goal:** Cung cấp quyền truy cập cho người dùng bên ngoài (không có AWS account) vào một dashboard cụ thể, đồng thời tuân thủ `principle of least privilege`.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Amazon CloudWatch` dashboard | Dashboard giám sát metrics của ứng dụng |
| Product manager does not have an AWS account | Người dùng bên ngoài, không cần tạo `IAM user` |
| Principle of least privilege | Chỉ cấp quyền tối thiểu cần thiết, tránh dùng `AWS managed policy` quá rộng |
| Share the dashboard | Tính năng chia sẻ tích hợp sẵn của `CloudWatch` qua email hoặc `shareable link` |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most secure / Least privilege / Minimal operational overhead
- **Constraints:** Người dùng không có AWS account, chỉ cần xem một dashboard cụ thể, truy cập định kỳ, không được cấp quyền vượt phạm vi.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- `Amazon CloudWatch` cung cấp tính năng chia sẻ dashboard tích hợp sẵn (`dashboard sharing`) cho phép chia sẻ với người không có AWS account thông qua email hoặc `shareable
