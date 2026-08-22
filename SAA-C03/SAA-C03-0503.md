# Question #503 - Topic 1

A company runs an infrastructure monitoring service. The company is building a new feature that will enable the service to monitor data in customer AWS accounts. The new feature will call AWS APIs in customer accounts to describe Amazon EC2 instances and read Amazon CloudWatch metrics. What should the company do to obtain access to customer accounts in the MOST secure way?

## Options

**A.** Ensure that the customers create an IAM role in their account with read-only EC2 and CloudWatch permissions and a trust policy to the company's account.

**B.** Create a serverless API that implements a token vending machine to provide temporary AWS credentials for a role with read-only EC2 and CloudWatch permissions.

**C.** Ensure that the customers create an IAM user in their account with read-only EC2 and CloudWatch permissions. Encrypt and store customer access and secret keys in a secrets management system.

**D.** Ensure that the customers create an Amazon Cognito user in their account to use an IAM role with read-only EC2 and CloudWatch permissions. Encrypt and store the Amazon Cognito user and password in a secrets management system.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty monitoring service cần truy cập vào tài khoản AWS của khách hàng để đọc EC2 và CloudWatch metrics.
- **Existing Resources:** Company's AWS account, customer's AWS accounts.
- **Current Issue/Goal:** Cho phép company access cross-account một cách secure nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `monitor data in customer AWS accounts` | Cross-account access pattern. |
| `MOST secure way` | Không dùng long-term credentials (access key), không share secrets. |
| `read-only EC2 and CloudWatch` | Scope tối thiểu (least privilege). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most secure
- **Constraints:** Read-only EC2 + CloudWatch, cross-account access

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- IAM cross-account role là pattern chuẩn và secure nhất: customer tạo IAM role với trust policy cho phép company's account assume role.
- Sử dụng temporary credentials (STS AssumeRole), không cần share long-term access keys.
- Customer kiểm soát permission (chỉ read-only) và trust policy.
- AWS best practice: cross-account access via IAM role, không dùng IAM user keys.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Token vending machine (TVM) tự xây dựng phức tạp và không cần thiết. IAM role đã giải quyết vấn đề cấp temporary credentials.
- Operational overhead cao hơn nhiều so với IAM role.

**❌ Đáp án C:**
- Tạo IAM user + access key → long-term credentials. Nếu key bị lộ, attacker có quyền truy cập.
- Encrypt + store secrets chỉ giảm rủi ro, không loại bỏ hoàn toàn. AWS best practice khuyến cáo không dùng IAM user keys cho cross-account.

**❌ Đáp án D:**
- Cognito user không phải giải pháp cho cross-account AWS API access. Cognito dùng cho user pools (ứng dụng mobile/web).
- Lưu username/password là không secure và không theo best practice.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cross-account access → IAM role + STS AssumeRole. Không dùng IAM user keys cho cross-account."*
