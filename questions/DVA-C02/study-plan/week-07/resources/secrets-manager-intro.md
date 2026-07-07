# What is AWS Secrets Manager?

> **Nguồn (AWS official):** https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
> **Tuần:** 7 — KMS + Secrets + Encryption · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **`Secrets Manager` = quản lý + retrieve + ROTATE** database credentials, application credentials, OAuth token, API key... suốt vòng đời. Điểm mạnh nhất so với `Parameter Store`: **automatic rotation built-in**.
- Mục đích cốt lõi: **bỏ hard-coded credential** trong source code → app gọi API `GetSecretValue` **lúc runtime** để lấy credential động. Rotate credential **không cần deploy lại** ứng dụng.
- **Chọn service đúng (bẫy đề):**
  - AWS access credentials → **IAM** (không phải Secrets Manager).
  - Encryption keys → **KMS**.
  - SSH keys → **EC2 Instance Connect**.
  - Private keys & certificates (TLS) → **ACM**.
  - DB creds / API keys / secret cần rotate → **Secrets Manager**.
- **Mã hoá:** secret **luôn được mã hoá bằng KMS**. Dùng AWS managed key `aws/secretsmanager` là **MIỄN PHÍ**; nếu tự tạo customer managed key thì trả phí KMS.
- **Chi phí (bẫy tiết kiệm):** trả tiền theo dùng, **có phí mỗi secret + mỗi 10.000 API call**. Secret đánh dấu xoá (marked for deletion) **không tính phí**. → Đề hỏi "rẻ nhất / config đơn giản" thường nghiêng về `Parameter Store` standard (free).
- Bật rotation (trừ managed rotation) → dùng **Lambda function** để rotate → **tính thêm phí Lambda**.
- CloudTrail log mọi event của Secrets Manager là **management event** (bản đầu miễn phí).
- Nhiều AWS service lưu & dùng secret trong Secrets Manager (vd tích hợp RDS, RDS Proxy).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# What is AWS Secrets Manager?

AWS Secrets Manager helps you manage, retrieve, and rotate database credentials, application credentials, OAuth tokens, API keys, and other secrets throughout their lifecycles. Many AWS services store and use secrets in Secrets Manager.

Secrets Manager helps you improve your security posture, because you no longer need hard-coded credentials in application source code. Storing the credentials in Secrets Manager helps avoid possible compromise by anyone who can inspect your application or the components. You replace hard-coded credentials with a runtime call to the Secrets Manager service to retrieve credentials dynamically when you need them.

With Secrets Manager, you can configure an automatic rotation schedule for your secrets. This enables you to replace long-term secrets with short-term ones, significantly reducing the risk of compromise. Since the credentials are no longer stored with the application, rotating credentials no longer requires updating your applications and deploying changes to application clients.

For other types of secrets you might have in your organization:
- **AWS credentials** – We recommend AWS Identity and Access Management (IAM).
- **Encryption keys** – We recommend AWS Key Management Service (KMS).
- **SSH keys** – We recommend Amazon EC2 Instance Connect.
- **Private keys and certificates** – We recommend AWS Certificate Manager (ACM).

## Get started with Secrets Manager

If you are new to Secrets Manager, start with one of the following tutorials:
- Move hardcoded secrets to AWS Secrets Manager
- Move hardcoded database credentials to AWS Secrets Manager
- Set up alternating users rotation for AWS Secrets Manager
- Set up single user rotation for AWS Secrets Manager

Other tasks you can do with secrets:
- Manage secrets
- Control access to your secrets
- Get secrets
- Rotate secrets
- Monitor secrets
- Monitor secrets for compliance
- Create secrets in AWS CloudFormation

## Compliance with standards

AWS Secrets Manager has undergone auditing for the multiple standards and can be part of your solution when you need to obtain compliance certification.

## Pricing

When you use Secrets Manager, you pay only for what you use, with no minimum or setup fees. There is no charge for secrets that are marked for deletion.

You can use the AWS managed key `aws/secretsmanager` that Secrets Manager creates to encrypt your secrets for free. If you create your own KMS keys to encrypt your secrets, AWS charges you at the current AWS KMS rate.

When you turn on automatic rotation (except managed rotation), Secrets Manager uses an AWS Lambda function to rotate the secret, and you are charged for the rotation function at the current Lambda rate.

If you enable AWS CloudTrail on your account, you can obtain logs of the API calls that Secrets Manager sends out. Secrets Manager logs all events as management events. AWS CloudTrail stores the first copy of all management events for free. However, you can incur charges for Amazon S3 for log storage and for Amazon SNS if you enable notification.

You can use cost allocation tags in Secrets Manager to track and categorize expenses associated with specific secrets or projects.
