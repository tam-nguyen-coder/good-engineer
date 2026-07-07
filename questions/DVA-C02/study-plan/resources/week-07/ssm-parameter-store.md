# AWS Systems Manager Parameter Store

> **Nguồn (AWS official):** https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
> **Tuần:** 7 — KMS + Secrets + Encryption · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **`Parameter Store` = lưu config data đơn giản** (connection string, env var, endpoint URL, resource ID, tuning param). **Standard tier MIỄN PHÍ** → đề nhấn "tiết kiệm chi phí / config đơn giản" thường là `Parameter Store`.
- **3 kiểu parameter:** `String`, `StringList` (đều lưu **plain text**), và `SecureString` (**mã hoá bằng KMS**). SecureString hợp cho "lightweight encrypted config **không cần rotation**".
- **Đọc SecureString phải thêm `--with-decryption`** — nếu không sẽ chỉ nhận metadata đã mã hoá, KHÔNG có plaintext. (Bẫy CLI hay hỏi.)
- **Chọn service (bẫy đề):** cần **automatic rotation / cross-account / audit chi tiết** → dùng **`Secrets Manager`**, KHÔNG dùng Parameter Store. Cần **feature flag / dynamic config / operational lever** → dùng **`AWS AppConfig`**, không phải Parameter Store.
- **Parameter history:** giữ **100 version gần nhất** của mỗi parameter.
- **Tổ chức phân cấp theo path** (hierarchy) + versioning; lấy hàng loạt bằng `GetParametersByPath`. `GetParameters` lấy tối đa **10** param một lần.
- **Tiers:** Standard = **10.000 param/account/region, max value 4 KB, không phí, không policy**. Advanced = **100.000 param, max value 8 KB, có parameter policy, share cross-account, tính phí**.
- **Tích hợp:** Lambda (Parameters and Secrets Lambda Extension), ECS/Fargate (inject env var), CloudFormation (dynamic reference `{{resolve:ssm:...}}`), CodeBuild, AppConfig, EC2 (tham chiếu AMI ID qua public parameter).
- **API chính:** `GetParameter`, `GetParameters`, `GetParametersByPath`, `GetParameterHistory`.
- Có **default throughput**; bật **high-throughput mode** (tính phí) khi cần request rate cao để tránh throttling.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# AWS Systems Manager Parameter Store

Parameter Store enables you to securely store, organize, and retrieve simple configuration data at scale. It is designed to simplify configuration management across environments, allowing teams to standardize how applications access critical data without hardcoding values or relying on fragmented storage solutions.

Beyond simple storage, Parameter Store provides versioning, access control through AWS Identity and Access Management (IAM), and seamless integration with other AWS services such as Amazon EC2, Lambda, and CloudFormation. This enables dynamic configuration updates without requiring code changes or redeployments. With features like hierarchical naming, parameter policies, and change tracking, Parameter Store helps teams maintain consistency, enforce governance, and build more secure and maintainable systems.

Parameter Store supports `String`, `StringList`, and `SecureString` parameter types. `String` and `StringList` parameter values are stored as plain text. `SecureString` parameters encrypt values using AWS Key Management Service, making them a practical choice for lightweight encrypted configuration values that don't require rotation or other advanced secret lifecycle capabilities.

**Note:** If you manage credentials that require automatic rotation, cross-account access, or fine-grained audit logging, we recommend using AWS Secrets Manager. Secrets Manager is purpose-built for managing secrets such as database credentials, API keys, and supported third-party software-vended secrets.

Examples of configuration data you can store and manage in Parameter Store:
- **Database connection strings (non-rotating)** – jdbc:mysql://host:3306/appdb
- **Application environment variables** – ENV=production, LOG_LEVEL=debug
- **Service endpoint URLs** – internal microservice endpoints or third-party base URLs
- **Resource identifiers** – S3 bucket names, DynamoDB table names, ARNs
- **Application tuning parameters** – cache TTLs, batch sizes, polling intervals

**Note:** We *don't* recommend using Parameter Store for the following types of configuration data (use AWS AppConfig instead):
- Feature flags
- Operational levers like timeouts
- Allow lists and block lists
- Circuit breakers
- Dynamic configurations

## Parameter Store features

- **Share parameters with other accounts** — Centralize configuration data in a single AWS account and share parameters with other accounts that need access.
- **OS Patching** — Amazon EC2 lets you specify the operating system for new instances by referencing a parameter instead of hardcoding an AMI ID. AWS and operating system vendors provide public parameters that track current AMI versions. You can also define your own parameters to reference a centrally managed golden AMI.
- **Accessible from other AWS services:**
  - Lambda functions can retrieve parameters and secrets using the Parameters and Secrets Lambda Extension.
  - Amazon ECS and AWS Fargate allow you to inject environmental variables whose values are managed centrally in Parameter Store.
  - AWS CloudFormation templates can reference parameter values.
  - AWS AppConfig enables you to create configuration profiles that reference parameters.
  - AWS CodeBuild allows you to define environmental variables whose values are dynamically retrieved from Parameter Store at build time.
- **Parameter History** — Parameter Store retains the **100 most recent versions** of each parameter.
- **Events and notifications** — Automate workflows by subscribing to parameter change events. You can also use change events to enforce expiration and receive notifications when a parameter hasn't been rotated within a specified timeframe.
- **Organize parameters hierarchically** — Use parameter hierarchies to group related parameters.

## Parameter tiers

Parameter Store offers multiple parameter tiers that affect cost, scale, and performance. You individually configure parameters to use either the standard-parameter tier (the default tier) or the advanced-parameter tier.

Use:
- Standard parameters for most configuration data and low-scale workloads
- Advanced parameters when you need higher limits, larger values, or parameter policies

**Important:** You can upgrade a parameter from standard to advanced, but you cannot downgrade it.

| Feature | Standard | Advanced |
| --- | --- | --- |
| Maximum parameters (per AWS account and AWS Region) | 10,000 | 100,000 |
| Maximum value size | 4 KB | 8 KB |
| Parameter policies | Not supported | Supported |
| Share parameters across AWS accounts | Not supported | Supported |
| Cost | No additional charge | Charges apply |

## Performance and throughput

Parameter Store provides a default throughput suitable for lower scale workloads. For applications that require higher request rates, you can enable higher throughput.
- Default throughput is sufficient for typical configuration retrieval patterns.
- High-throughput mode supports significantly higher request rates for large-scale or latency-sensitive applications.
- Additional charges apply when higher throughput is enabled.

## How to retrieve parameters

You can retrieve parameters using the AWS Management Console, AWS CLI, or AWS SDKs to call the following API actions:
- `GetParameter`
- `GetParameters`
- `GetParametersByPath`

**AWS CLI** sample commands:

| Command | Usage | Best For |
| --- | --- | --- |
| get-parameter | `aws ssm get-parameter --name "<name>"` | Fetching one specific parameter value. |
| get-parameter | `aws ssm get-parameter --name "<name>" --with-decryption` | Fetching `SecureString` parameter types. **You must include the `--with-decryption` flag to see the plaintext value; otherwise, you will only receive the encrypted metadata.** |
| get-parameters | `aws ssm get-parameters --names "<name1>" "<name2>"` | Fetching up to **10** specific, unrelated parameters at once. |
| get-parameters-by-path | `aws ssm get-parameters-by-path --path "</my/app/path/>"` | Bulk retrieval of an entire environment's configuration. |
| get-parameter-history | `aws ssm get-parameter-history --name "<name>"` | Checking how a value has changed over time. |

**SDKs (e.g., Boto3 for Python):** Use methods like `get_parameter()` or `get_parameters_by_path()` within your application code to fetch values at runtime.

**CDK and CloudFormation:**
- **AWS CDK**: Use `valueForStringParameter` or `valueFromLookup` to read values during synthesis or deployment.
- **CloudFormation**: Use dynamic references like `{{resolve:ssm:parameter-name:version}}` to inject values directly into templates.

**Note:** For most dynamic parameter references, you specify the parameter name using the convention `ssm:<parameter-name>`.
