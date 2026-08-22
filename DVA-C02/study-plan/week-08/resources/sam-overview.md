# What is the AWS Serverless Application Model (AWS SAM)?

> **Nguồn (AWS official):** https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html
> **Tuần:** 8 — Deployment / CI-CD / IaC · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- SAM là **mở rộng của CloudFormation** cho serverless — cú pháp ngắn gọn hơn. SAM template được **transform** thành CloudFormation khi deploy (`Transform: AWS::Serverless-2016-10-31` ở đầu template là dấu hiệu nhận biết).
- 2 thành phần chính: **AWS SAM CLI** (develop, test local, deploy) + **AWS SAM Template** (mở rộng CloudFormation cho tài nguyên serverless: Lambda, API Gateway, DynamoDB...).
- SAM resource dùng CHUNG template với CloudFormation resource chuẩn — có thể trộn lẫn.
- Lệnh SAM CLI hay hỏi: **`sam init`** (tạo project), **`sam build`**, **`sam deploy`** (deploy qua CloudFormation), **`sam local`** (test Lambda/API Gateway local), **`sam sync`** (đồng bộ thay đổi local lên cloud nhanh cho dev/test).
- **SAM connectors** = tự sinh IAM permission giữa các resource (khai báo intent, SAM transform ra IAM policy).
- So sánh: SAM thay CloudFormation để đơn giản hóa serverless; SAM thay CDK nếu thích cách khai báo (declarative) thay vì lập trình (programmatic); có thể kết hợp SAM CLI local-test với CDK.
- SAM hỗ trợ cả **Terraform** (local debug/test Lambda) — feature ít hỏi nhưng nên biết.

---

## 📄 Nội dung (trích từ tài liệu gốc)

AWS Serverless Application Model (AWS SAM) is an open-source framework for building serverless applications using infrastructure as code (IaC). With AWS SAM's shorthand syntax, developers declare CloudFormation resources and specialized serverless resources that are transformed to infrastructure during deployment. When working with AWS SAM, you will interact with:

1. **AWS SAM CLI** — A command-line tool that helps you develop, locally test, and deploy your serverless applications.
2. **AWS SAM Template** — An extension of CloudFormation that provides simplified syntax for defining serverless resources.

When you use the **sam init** command, it creates a project directory (the AWS SAM project) that typically includes your AWS SAM template, application code, and other configuration files.

## When to use AWS SAM

AWS SAM is an ideal IaC solution for scenarios where you want simplified serverless development with the full power of CloudFormation. For example:
- **Serverless applications:** Quickly define AWS Lambda functions, Lambda durable functions, Amazon API Gateway APIs, Amazon DynamoDB tables, and other serverless resources with minimal code.
- **CloudFormation enhancement:** Combine SAM with existing CloudFormation templates to add serverless components to traditional infrastructure. SAM resources work alongside standard CloudFormation resources in the same template.
- **Local development and testing:** Use the SAM CLI to test Lambda functions locally, simulate API Gateway endpoints, and debug serverless applications before deploying to AWS.
- **CI/CD for serverless:** Build deployment pipelines using SAM templates that automatically generate the CloudFormation infrastructure needed for staging and production environments.
- **Migration from console-created resources:** Convert Lambda functions and API Gateway resources created in the AWS Management Console into infrastructure as code using SAM templates.

**Comparing AWS SAM with other IaC tools**
- Use SAM instead of CloudFormation to simplify serverless resource definitions while maintaining template compatibility.
- Use SAM instead of AWS CDK if you prefer a declarative approach to describing your infrastructure rather than a programmatic one.
- Combine SAM with AWS CDK by using SAM CLI's local testing features to enhance your CDK applications.

## Key features

- **Define your application infrastructure code quickly, using less code** — Author AWS SAM templates to define your serverless application infrastructure code. Deploy your templates directly to CloudFormation to provision your resources.
- **Manage your serverless applications through their entire development lifecycle** — Use the AWS SAM CLI to manage authoring, building, deploying, testing, and monitoring phases.
- **Quickly provision permissions between resources with AWS SAM connectors** — Use AWS SAM connectors in your templates to define permissions between AWS resources. AWS SAM transforms your code into the required IAM permissions.
- **Continuously sync local changes to the cloud as you develop** — Use the AWS SAM CLI **sam sync** command to automatically sync local changes to the cloud, speeding up development and cloud testing workflows.
- **Manage your Terraform serverless applications** — Use the AWS SAM CLI to perform local debugging and testing of your Lambda functions and layers.

## Related information
- For information on how AWS SAM works, see "How AWS SAM works".
- To start using AWS SAM, see "Getting started with AWS SAM".
- For an overview, see "How to use AWS SAM".
