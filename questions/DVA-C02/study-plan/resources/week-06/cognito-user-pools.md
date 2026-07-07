# Amazon Cognito — User Pools

> **Nguồn (AWS official):** https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html
> **Tuần:** 6 — Security I: `IAM` + `STS` + `Cognito` · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **`User Pool` = user directory + AUTHENTICATION.** Đứng nhìn từ app, nó là một **OpenID Connect (OIDC) identity provider (IdP)**.
- Đăng nhập xong trả về **JWT** (ID / Access / Refresh token) — dùng để xác thực và ủy quyền request tới backend/API của bạn.
- **Federation:** hỗ trợ social OAuth 2.0 (Google, Facebook, Amazon, Apple) và **SAML 2.0 / OIDC** IdP bất kỳ (work/school). Cognito map claim của IdP ngoài vào user profile.
- **Managed login (Hosted UI):** bộ trang web sẵn cho sign-up / sign-in / MFA / reset password — khỏi tự build UI. Gắn domain riêng hoặc dùng prefix subdomain AWS.
- **Security:** MFA (SMS/email/TOTP app), **adaptive authentication** (threat protection — plan Plus), bỏ qua MFA cho thiết bị tin cậy, tích hợp **AWS WAF**.
- **Groups:** gom user để phân quyền; group xuất hiện trong access & ID token, có thể link tới IAM role khi đưa ID token cho identity pool.
- **Lambda triggers:** tùy biến luồng auth (sửa token, reject sign-up, custom auth challenge…). **M2M authorization:** app client kiểu client-credentials grant tạo access token cho service-to-service.
- **Kết nối với Identity Pool:** User Pool lo *bạn là ai* (JWT); đưa token cho Identity Pool để đổi lấy **AWS credentials** gọi thẳng service (DynamoDB, S3…).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Amazon Cognito user pools

An Amazon Cognito user pool is a **user directory for web and mobile app authentication and authorization**. From the perspective of your app, an Amazon Cognito user pool is an **OpenID Connect (OIDC) identity provider (IdP)**. A user pool adds layers of additional features for security, identity federation, app integration, and customization of the user experience.

You can verify that your users' sessions are from trusted sources. You can combine the Amazon Cognito directory with an external identity provider. With your preferred AWS SDK, you can choose the API authorization model that works best for your app. And you can add AWS Lambda functions that modify or overhaul the default behavior of Amazon Cognito.

## Features

### Sign-up
Amazon Cognito user pools have user-driven, administrator-driven, and programmatic methods to add user profiles. Supported sign-up models (combinable):
1. Users enter information in your app and create a profile native to your user pool (API sign-up operations, open to anyone or authorized with a client secret / AWS credentials).
2. Redirect users to a third-party IdP. Amazon Cognito processes **OIDC id tokens, OAuth 2.0 `userInfo` data, and SAML 2.0 assertions** into user profiles based on attribute-mapping rules.
3. Skip public/federated sign-up and create users from your own data source (console, API, import from CSV, or just-in-time Lambda lookup).

After sign-up, you can add users to **groups** that Amazon Cognito lists in the access and ID tokens. You can also **link user pool groups to IAM roles** when you pass the ID token to an identity pool.

> **Important:** If you activate user sign-up, anyone on the internet can sign up and sign in. Don't enable self-registration unless you want public sign-up (controlled by `AllowAdminCreateUserOnly`).

### Sign-in
Amazon Cognito can be a standalone user directory and IdP. Users can sign in with **managed login pages** hosted by Amazon Cognito, or with a custom-built service through the user pools API. Users can sign in with usernames and passwords, passkeys, and email/SMS one-time passwords. You can offer consolidated sign-in with external directories, MFA after sign-in, trusted remembered devices, and custom authentication flows.
1. Social sign-in with OAuth 2.0 — **Google, Facebook, Amazon, and Apple**.
2. **SAML and OIDC** sign-in for work and school user data — accept claims from any SAML or OIDC IdP.
3. Link external user profiles to native user profiles.

**Machine-to-machine authorization:** For a service account authorizing an automated process, add an app client that generates **client-credentials grants** (OAuth 2.0 scopes → access tokens).

### Managed login
When you don't want to build a UI, present users with customized **managed login pages** — a set of web pages for sign-up, sign-in, MFA, and password reset. Add managed login to your existing domain or use a prefix identifier in an AWS subdomain.

### Security
Users can provide an additional authentication factor with a code from SMS/email, or a **MFA** app. Amazon Cognito can bypass MFA for trusted devices. With **adaptive authentication**, Amazon Cognito can detect potential malicious activity and require MFA or block sign-in. Monitor malicious network traffic with **AWS WAF** web ACLs.

### Custom user experience
With **Lambda triggers**, you can modify an ID token or reject a sign-up request based on custom conditions, and create your own custom authentication flow. Upload custom CSS and logos to brand managed login.

### Monitoring and analytics
User pools log API requests to **AWS CloudTrail**; review metrics in **Amazon CloudWatch Logs**. With the **Plus feature plan**, monitor authentication attempts for indicators of compromise and log activity to S3, CloudWatch Logs, or Amazon Data Firehose. Log device/session data to an **Amazon Pinpoint** campaign.

### Amazon Cognito identity pools integration
The other half of Amazon Cognito is **identity pools**. Identity pools provide **credentials that authorize API requests to AWS services** (e.g. Amazon DynamoDB or Amazon S3) from your users. You can build identity-based access policies that protect your data based on how you classify users in your user pool. Identity pools can also accept tokens and SAML 2.0 assertions from a variety of identity providers, independently of user pool authentication.

**Related topics:**
+ Understanding user pool JSON web tokens (JWTs)
+ Accessing AWS services using an identity pool after sign-in
+ Amazon Cognito identity pools
