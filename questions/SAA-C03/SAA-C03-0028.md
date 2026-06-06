# Question #28 - Topic 1

A company is migrating applications to AWS. The applications are deployed in different accounts. The company manages the accounts centrally by using AWS Organizations. The company's security team needs a single sign-on (SSO) solution across all the company's accounts. The company must continue managing the users and groups in its on-premises self-managed Microsoft Active Directory. Which solution will meet these requirements?

## Options

**A.** Enable AWS Single Sign-On (AWS SSO) from the AWS SSO console. Create a one-way forest trust or a one-way domain trust to connect the company's self-managed Microsoft Active Directory with AWS SSO by using AWS Directory Service for Microsoft Active Directory.

**B.** Enable AWS Single Sign-On (AWS SSO) from the AWS SSO console. Create a two-way forest trust to connect the company's self-managed Microsoft Active Directory with AWS SSO by using AWS Directory Service for Microsoft Active Directory.

**C.** Use AWS Directory Service. Create a two-way trust relationship with the company's self-managed Microsoft Active Directory.

**D.** Deploy an identity provider (IdP) on premises. Enable AWS Single Sign-On (AWS SSO) from the AWS SSO console.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty đang di chuyển ứng dụng lên AWS, triển khai trên nhiều `account` khác nhau.
- **Existing Resources:** Sử dụng `AWS Organizations` để quản lý tập trung các `account`.
- **Current Issue/Goal:** Security team cần giải pháp `single sign-on (SSO)` xuyên suốt tất cả các `account`. Công ty phải tiếp tục quản lý `users` và `groups` trên `on-premises self-managed Microsoft Active Directory`.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `AWS Organizations` | Dịch vụ quản lý tập trung và thanh toán cho nhiều AWS accounts |
| `AWS SSO` / `IAM Identity Center` | Dịch vụ cung cấp single sign-on xuyên suốt nhiều AWS accounts và ứng dụng |
| `AWS Directory Service for Microsoft Active Directory` | `AWS Managed Microsoft AD` - dịch vụ AD được quản lý bởi AWS, dùng làm identity source |
| `One-way forest/domain trust` | Mối quan hệ tin cậy một chiều, đủ để on-prem users xác thực vào AWS |
| `Two-way forest trust` | Mối quan hệ tin cậy hai chiều, không bắt buộc cho AWS SSO |
| `Self-managed Microsoft AD` | Active Directory vận hành on-premises bởi chính công ty |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Solution architecture - Identity & Access Management


