# Amazon Cognito — Identity Pools (Federated Identities)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-identity.html
> **Tuần:** 6 — Security I: `IAM` + `STS` + `Cognito` · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **`Identity Pool` = directory of federated identities → đổi lấy AWS credentials.** Vai trò là **AUTHORIZATION**: cấp **temporary AWS credentials** để client GỌI THẲNG service AWS (S3, DynamoDB…).
- Cơ chế nền: Cognito biến claim của IdP thành request **`AssumeRoleWithWebIdentity`** tới `STS` → nhận short-term credentials, map vào **IAM role**.
- **Hai loại role:** **authenticated** (user đã đăng nhập) và **unauthenticated / guest** (chưa đăng nhập vẫn được cấp quyền hẹp). Có thể gán 1 role chung cho mọi authenticated user, hoặc chọn role theo claim.
- **Nhận nhiều loại IdP:** social OAuth (Amazon, Facebook, Google, Apple, Twitter), **`Cognito User Pool`**, OIDC provider bất kỳ, SAML provider, và **developer-authenticated identities** (tự validate rồi cấp creds bằng developer credentials).
- **Luồng điển hình (đề rất thích):** đăng nhập bằng `User Pool` (nhận JWT) → đưa JWT cho `Identity Pool` → nhận **AWS credentials tạm** → gọi thẳng AWS. User Pool = *ai bạn là*, Identity Pool = *bạn được làm gì trên AWS*.
- Hỗ trợ **attributes for access control** (biến user claim thành **IAM session tag**) và **role-based access control** để phân quyền tinh vi theo subset user.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Amazon Cognito identity pools

An Amazon Cognito identity pool is a **directory of federated identities that you can exchange for AWS credentials**. Identity pools generate **temporary AWS credentials** for the users of your app, whether they've signed in or you haven't identified them yet. With AWS Identity and Access Management (IAM) roles and policies, you can choose the level of permission that you want to grant to your users. Users can start out as guests and retrieve assets that you keep in AWS services. Then they can sign in with a third-party identity provider to unlock access to assets that you make available to registered members. The third-party identity provider can be a consumer (social) OAuth 2.0 provider like Apple or Google, a custom SAML or OIDC identity provider, or a custom authentication scheme, also called a *developer provider*, of your own design.

## Features of Amazon Cognito identity pools

**Sign requests for AWS services**
Sign API requests to AWS services like Amazon Simple Storage Service (Amazon S3) and Amazon DynamoDB. Analyze user activity with services like Amazon Pinpoint and Amazon CloudWatch.

**Filter requests with resource-based policies**
Exercise granular control over user access. Transform user claims into **IAM session tags**, and build IAM policies that grant resource access to distinct subsets of your users.

**Assign guest access**
For users who haven't signed in yet, configure your identity pool to generate AWS credentials with a **narrow scope of access**. Authenticate users through a single sign-on provider to elevate their access.

**Assign IAM roles based on user characteristics**
Assign a single IAM role to all of your authenticated users, or choose the role based on the claims of each user.

**Accept a variety of identity providers**
Exchange an ID or access token, a user pool token, a SAML assertion, or a social-provider OAuth token for AWS credentials.

**Validate your own identities**
Perform your own user validation and use your developer AWS credentials to issue credentials for your users.

## Kết nối với User Pool và STS

You might already have an Amazon Cognito **user pool** that provides authentication and authorization services to your app. You can set up your user pool as an identity provider (IdP) to your identity pool. When you do, your users can authenticate through your user pool IdPs, consolidate their claims into a common OIDC identity token, and **exchange that token for AWS credentials**.

You can also present authenticated claims from any of your identity providers directly to your identity pool. Amazon Cognito customizes user claims from SAML, OAuth, and OIDC providers into an **`AssumeRoleWithWebIdentity`** API request for short-term credentials.

Amazon Cognito user pools are like **OIDC identity providers** to your SSO-enabled apps. **Identity pools act as an *AWS* identity provider** to any app with resource dependencies that work best with IAM authorization.

## Supported identity providers
+ **Public providers:** Login with Amazon, Facebook, Google, Sign in with Apple, Twitter.
+ **Amazon Cognito user pools**
+ **OIDC provider** (any)
+ **SAML provider** (any)
+ **Developer-authenticated identities**

## Topics
+ Identity pools console overview
+ **Identity pools authentication flow**
+ **IAM roles**
+ Security best practices for Amazon Cognito identity pools
+ Using attributes for access control
+ Using role-based access control
+ Getting credentials
+ Accessing AWS services with temporary credentials
+ Identity pools third-party identity providers
+ Developer-authenticated identities
+ **Switching unauthenticated users to authenticated users**
