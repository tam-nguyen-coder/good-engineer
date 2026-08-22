# Question #521 - Topic 1

A retail company has several businesses. The IT team for each business manages its own AWS account. Each team account is part of an organization in AWS Organizations. Each team monitors its product inventory levels in an Amazon DynamoDB table in the team's own AWS account. The company is deploying a central inventory reporting application into a shared AWS account. The application must be able to read items from all the teams' DynamoDB tables. Which authentication option will meet these requirements MOST securely?

## Options

**A.** Integrate DynamoDB with AWS Secrets Manager in the inventory application account. Configure the application to use the correct secret from Secrets Manager to authenticate and read the DynamoDB table. Schedule secret rotation for every 30 days.

**B.** In every business account, create an IAM user that has programmatic access. Configure the application to use the correct IAM user access key ID and secret access key to authenticate and read the DynamoDB table. Manually rotate IAM access keys every 30 days.

**C.** In every business account, create an IAM role named BU_ROLE with a policy that gives the role access to the DynamoDB table and a trust policy to trust a specific role in the inventory application account. In the inventory account, create a role named APP_ROLE that allows access to the STS AssumeRole API operation. Configure the application to use APP_ROLE and assume the crossaccount role BU_ROLE to read the DynamoDB table.

**D.** Integrate DynamoDB with AWS Certificate Manager (ACM). Generate identity certificates to authenticate DynamoDB. Configure the application to use the correct certificate to authenticate and read the DynamoDB table.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Nhiều business accounts (mỗi team có AWS account riêng), mỗi account có DynamoDB table inventory. Central inventory reporting app deployed trong shared account cần read items từ tất cả DynamoDB tables.
- **Existing Resources:** DynamoDB tables trong mỗi business account, AWS Organizations.
- **Current Issue/Goal:** Authenticate cross-account để central app đọc được DynamoDB của từng business account, với security cao nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `cross-account access` | IAM role + trust policy + STS AssumeRole |
| `most securely` | Không dùng IAM user keys (long-lived credentials), không dùng Secrets Manager cho DynamoDB auth |
| `trust policy` | Cho phép role ở account A assume role ở account B |
| `IAM role` | Temporary credentials, secure hơn IAM user access keys |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most secure
- **Constraints:** Cross-account, nhiều business accounts, central inventory app

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- IAM role với cross-account trust policy là best practice cho cross-account access.
- Ở mỗi business account: tạo BU_ROLE với policy cho phép read DynamoDB table, trust policy cho phép APP_ROLE từ inventory account assume.
- Ở inventory account: APP_ROLE có quyền gọi STS AssumeRole.
- Application assume BU_ROLE → nhận temporary credentials → truy cập DynamoDB.
- Temporary credentials tự động rotate, không cần quản lý long-lived keys.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Secrets Manager dùng để lưu secrets (database credentials, API keys), không phải để authenticate DynamoDB cross-account.
- DynamoDB không hỗ trợ auth qua Secrets Manager.

**❌ Đáp án B:**
- IAM user access keys là long-lived credentials, security kém hơn temporary credentials từ role.
- Phải manually rotate keys mỗi 30 ngày → operational overhead cao.
- AWS khuyến cáo không dùng IAM user keys cho cross-account access.

**❌ Đáp án D:**
- ACM dùng để quản lý SSL/TLS certificates, không phải để authenticate DynamoDB.
- DynamoDB không hỗ trợ certificate-based authentication.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"Cross-account = IAM role + STS AssumeRole. Không dùng IAM user keys cho cross-account."*
