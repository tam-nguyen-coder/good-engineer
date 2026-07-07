# AWS SDKs and Tools standardized credential providers (Credential provider chain)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/sdkref/latest/guide/standardized-credentials.html
> **Tuần:** 1 — SDK/CLI + `Lambda` cơ bản · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Credential provider chain** = chuỗi các nguồn mà SDK/CLI kiểm tra **theo thứ tự** để tìm credentials hợp lệ; **tìm thấy hợp lệ ở đâu thì dừng ở đó**.
- **Giá trị set trong code (client) luôn có precedence cao nhất**, sau đó tới **environment variables**, rồi tới **shared `config`/`credentials` files**.
- SDK **tự động renew** credentials khi hết hạn — không cần code thêm, bất kể provider nào trong chain.
- Các provider chuẩn hoá (thường gặp): **AWS access keys** (IAM user), **Assume role** (kể cả web identity/OIDC JWT qua STS), **Login credentials**, **IAM Identity Center (SSO)**, **Container** (ECS/EKS), **Process** (nguồn ngoài, gồm IAM Roles Anywhere), **IMDS** (EC2 instance profile qua metadata service).
- **Không phải SDK nào cũng hỗ trợ hết mọi provider** — chi tiết chuỗi cụ thể khác nhau theo từng SDK (có trang riêng cho Java, Python/Boto3, JavaScript, Go, .NET, ...).
- Điểm bẫy DVA: code chạy trên EC2 → dùng **IMDS/instance profile**; trên ECS/EKS → dùng **Container provider**; **không hard-code key**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

Many credential providers have been standardized to consistent defaults and to work the same way across many SDKs. All settings can be overridden in code.

> **Important:** Not all SDKs support all providers, or even all aspects within a provider.

## Understand the credential provider chain

All SDKs have a series of places (or sources) that they check in order to find valid credentials to use to make a request to an AWS service. **After valid credentials are found, the search is stopped.** This systematic search is called the credential provider chain.

When using one of the standardized credential providers, the AWS SDKs always attempt to renew credentials automatically when they expire. The built-in credential provider chain provides your application with the ability to refresh your credentials regardless of which provider you are using in the chain. No additional code is required for the SDK to do this.

Although the distinct chain used by each SDK varies, they most often include sources such as the following:

| Credential provider | Description |
| --- | --- |
| **AWS access keys** | AWS access keys for an IAM user (such as `AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY`). |
| **Federate with web identity or OpenID Connect** (Assume role credential provider) | Sign in using a well-known external IdP (Login with Amazon, Facebook, Google, or any OIDC-compatible IdP). Assume the permissions of an IAM role using a JSON Web Token (JWT) from AWS STS. |
| **Login credentials provider** | Get credentials for a new or existing console session that you are logged in to. |
| **IAM Identity Center credential provider** | Get credentials from AWS IAM Identity Center. |
| **Assume role credential provider** | Get access to other resources by assuming the permissions of an IAM role (retrieve and then use temporary credentials for a role). |
| **Container credential provider** | Amazon ECS and Amazon EKS credentials. Fetches credentials for the customer's containerized application. |
| **Process credential provider** | Custom credential provider. Get your credentials from an external source or process, including IAM Roles Anywhere. |
| **IMDS credential provider** | Amazon EC2 instance profile credentials. Associate an IAM role with each EC2 instance; temporary credentials for that role are delivered through the EC2 metadata service. |

For each step in the chain, there are multiple ways to assign setting values. **Setting values that are specified in code always take precedence.** However, there are also **Environment variables** and the **shared `config` and `credentials` files**. (See *Precedence of settings*.)

## SDK-specific and tool-specific credential provider chains

To go directly to your SDK's or tool's **specific** credential provider chain details, choose your SDK or tool:
- AWS CLI
- SDK for C++
- SDK for Go
- SDK for Java
- SDK for JavaScript
- SDK for Kotlin
- SDK for .NET
- SDK for PHP
- SDK for Python (Boto3)
- SDK for Ruby
- SDK for Rust
- SDK for Swift
- Tools for PowerShell

### Related standardized provider topics
- AWS access keys
- Login provider
- Assume role provider
- Container provider
- IAM Identity Center provider
- IMDS provider
- Process provider
