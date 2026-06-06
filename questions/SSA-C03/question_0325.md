# Question #325 - Topic 1

A company is hosting a web application from an Amazon S3 bucket. The application uses Amazon Cognito as an identity provider to authenticate users and return a JSON Web Token (JWT) that provides access to protected resources that are stored in another S3 bucket. Upon deployment of the application, users report errors and are unable to access the protected content. A solutions architect must resolve this issue by providing proper permissions so that users can access the protected content. Which solution meets these requirements?

## Options

**A.** Update the Amazon Cognito identity pool to assume the proper IAM role for access to the protected content.

**B.** Update the S3 ACL to allow the application to access the protected content.

**C.** Redeploy the application to Amazon S3 to prevent eventually consistent reads in the S3 bucket from affecting the ability of users to access the protected content.

**D.** Update the Amazon Cognito pool to use custom attribute mappings within the identity pool and grant users the proper permissions to access the protected content.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 web app + Cognito auth + JWT. Protected content in another S3 bucket. Users get errors - can't access protected content.
- **Existing Resources:** S3 bucket (web app), S3 bucket (protected content), Cognito identity pool.
- **Current Issue/Goal:** Users can't access protected S3 content after authentication.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Amazon Cognito identity pool` | Cấp temporary AWS credentials cho authenticated users thông qua IAM roles. |
| `JWT` | Token xác thực từ Cognito User Pool. |
| `protected resources in another S3 bucket` | Cần IAM role policy cho phép access S3. |
| `proper permissions` | Identity pool cần IAM role với S3 access policy. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Fix permissions for protected S3 content
- **Constraints:** Cognito auth, S3 protected resources

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Cognito identity pool cho phép authenticated users assume an IAM role để lấy temporary AWS credentials.
- IAM role cần có policy granting access to the protected S3 bucket.
- Update identity pool để sử dụng đúng IAM role với S3 permissions.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- S3 ACL không phù hợp cho user-level access (không scale). Cognito identity pool + IAM role là best practice.

**❌ Đáp án C:**
- Eventually consistent reads không gây ra lỗi permissions. Vấn đề là IAM permissions, không phải consistency.

**❌ Đáp án D:**
- Custom attribute mappings trong user pool dùng cho custom claims trong JWT, không cấp AWS permissions trực tiếp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cognito auth + S3 access → identity pool + IAM role (temporary credentials). ACL = outdated. Attributes = claims."*
