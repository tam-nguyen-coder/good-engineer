# DVA-C02 Exam Guide — Domain, trọng số & phạm vi dịch vụ

> **Nguồn (AWS official):** https://d1.awsstatic.com/training-and-certification/docs-dev-associate/AWS-Certified-Developer-Associate_Exam-Guide.pdf
> **Tuần:** 10 — Kỳ thi & Mock (tuần chốt) · **Loại:** AWS Docs (Exam Guide PDF)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn/diễn giải nhẹ ở phần task statement) — luôn đối chiếu link PDF gốc để đầy đủ & chính xác nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **4 domain + trọng số (PHẢI THUỘC — quyết định phân bổ ôn tập):**
  - **Domain 1 — Development with AWS Services: 32%** (nặng nhất → ôn kỹ nhất: `Lambda`, `API Gateway`, `DynamoDB`, `S3`, `SQS`/`SNS`).
  - **Domain 2 — Security: 26%** (IAM, KMS, `Secrets Manager`, mã hoá at-rest/in-transit, authN/authZ).
  - **Domain 3 — Deployment: 24%** (`CodeBuild`/`CodeDeploy`/`CodePipeline`, `CloudFormation`/`SAM`, blue/green + canary, `Lambda` versioning).
  - **Domain 4 — Troubleshooting & Optimization: 18%** (`CloudWatch` Logs/metrics, `X-Ray`, caching `ElastiCache`/`CloudFront`, tối ưu chi phí).
- **Điểm đậu 720/1000** (thang scaled, không phải % thô); có **câu unscored** thử nghiệm không tính điểm.
- Đề bám **task statement** trong từng domain — khi review câu sai, gắn mỗi câu về đúng domain để biết vùng yếu.
- **Nhớ ranh giới in-scope / out-of-scope:** đề chỉ hỏi các dịch vụ in-scope. Các dịch vụ out-of-scope chính thức (vd `QuickSight`, `Rekognition`, `Polly`, `WorkSpaces`, `AppStream 2.0`, `GameLift`, `Shield`, `Snow Family`, `Storage Gateway`…) nếu xuất hiện trong đáp án thường là **mồi nhử**. ⚠️ Lưu ý: `Athena` và `Route 53` là **IN-SCOPE** (đừng loại nhầm). Xem danh sách authoritative đầy đủ ở cuối file.
- Trọng số → thứ tự ưu tiên khi thời gian ít: **Development > Security > Deployment > Troubleshooting**.

> ⚠️ Cảnh báo độ chính xác: phần "Exam Overview" và "Task Statements" bên dưới do model tóm tắt lại từ PDF nên **có thể diễn giải khác câu chữ gốc** — dùng file PDF chính thức làm chuẩn cuối cùng cho câu chữ task statement.
> ✅ Ngược lại, **danh sách In-Scope / Out-of-Scope ở cuối file đã được thay bằng bản AUTHORITATIVE** lấy trực tiếp từ trang AWS Certification (docs.aws.amazon.com), không còn là bản model tóm tắt từ PDF.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# AWS Certified Developer - Associate (DVA-C02) Exam Guide

## Introduction

The AWS Certified Developer - Associate certification validates expertise in developing, deploying, and debugging cloud-based applications using AWS services. This exam assesses practical knowledge of AWS development tools, services, and best practices.

## Exam Overview

### Exam Format
- **Question Types**: Multiple choice and multiple response
- **Time Limit**: 130 minutes
- **Passing Score**: 720/1000

### Scoring Method
- **Scored Questions**: Contribute to final score
- **Unscored Questions**: AWS includes experimental questions that don't affect your score to validate future exam content

### Response Types
- **Multiple Choice**: Select one correct answer from four options
- **Multiple Response**: Select all that apply (typically 2-3 correct answers from 5+ options)

---

## Exam Content Domains

### Domain 1: Development with AWS Services — **Weight 32%**

#### Task Statements
1. **Write code for serverless applications** — Develop Lambda functions, configure event sources, manage environment variables, and implement error handling
2. **Translate functional requirements into application design** — Design cloud architectures, select appropriate AWS services, and implement scalable patterns
3. **Implement application code and configuration files** — Create and deploy application code, manage dependencies, configure settings, and implement environment-specific configurations
4. **Develop code for security** — Implement authentication, authorization, data encryption, secure credential management, and compliance with security best practices

#### Knowledge and Skills
- AWS Lambda function development and configuration
- API Gateway creation and integration
- DynamoDB and other database operations
- S3 bucket operations and management
- SQS and SNS messaging patterns
- IAM roles and policies
- Environment variables and configuration management
- Serverless application patterns

---

### Domain 2: Security — **Weight 26%**

#### Task Statements
1. **Make authenticated API calls** — Implement IAM authentication, configure credentials, manage API keys, and handle authentication across distributed systems
2. **Implement encryption** — Apply encryption at rest and in transit, manage encryption keys using KMS, configure S3 encryption, and implement application-level encryption
3. **Implement authorization and access control** — Design and enforce IAM policies, implement resource-based access control, configure cross-account access, and implement application-level authorization
4. **Manage sensitive data** — Implement secrets management using AWS Secrets Manager, handle database credentials securely, manage API keys, and implement data masking

#### Knowledge and Skills
- IAM policies and roles
- AWS KMS key management
- Secrets Manager and credential rotation
- Encryption protocols and algorithms
- API authentication mechanisms
- Data protection strategies
- Compliance and auditing

---

### Domain 3: Deployment — **Weight 24%**

#### Task Statements
1. **Prepare application for deployment** — Package applications, configure build processes, manage dependencies, and prepare artifacts for deployment
2. **Deploy application versions** — Use CodeDeploy for application deployment, implement deployment strategies (blue/green, canary), manage application versions, and rollback procedures
3. **Update applications and components** — Implement updates to Lambda functions, manage container deployments, update infrastructure, and execute zero-downtime deployments

#### Knowledge and Skills
- AWS CodeBuild configuration
- AWS CodeDeploy strategies and deployment patterns
- CloudFormation templates and Infrastructure as Code
- CodePipeline orchestration
- Lambda deployment and versioning
- Container deployment with ECS/Fargate
- Application load balancer configuration
- Artifact management and repositories

---

### Domain 4: Troubleshooting and Optimization — **Weight 18%**

#### Task Statements
1. **Troubleshoot application errors** — Identify and resolve runtime errors, analyze logs using CloudWatch, debug Lambda functions, and implement error handling strategies
2. **Troubleshoot deployments** — Diagnose deployment failures, analyze deployment logs, validate infrastructure changes, and implement rollback procedures
3. **Optimize applications** — Improve performance through caching strategies, optimize database queries, implement asynchronous processing, and reduce costs

#### Knowledge and Skills
- CloudWatch Logs and monitoring
- X-Ray service tracing and debugging
- Application performance insights
- Cost optimization techniques
- Caching strategies (ElastiCache, CloudFront)
- Performance profiling and metrics
- Log analysis and correlation
- Resource optimization

---

## In-Scope AWS Services and Features (danh sách AUTHORITATIVE)

> **Nguồn chính thức (authoritative):** https://docs.aws.amazon.com/aws-certification/latest/developer-associate-02/dva-02-in-scope-services.html
> ✅ Đây là danh sách **chính thức** lấy trực tiếp từ trang AWS Certification (không phải bản model tóm tắt từ PDF). Nhóm danh mục (category) giữ nguyên theo AWS. Danh sách là **non-exhaustive** (AWS ghi rõ có thể thay đổi & không liệt kê hết).
> ⚠️ Lưu ý so với bản tóm tắt cũ: `Athena` và `Route 53` thực chất **IN-SCOPE** (trước đây bị xếp nhầm out-of-scope); `CodeCommit`, `Fargate`, `SAM` **KHÔNG** nằm trong danh sách in-scope chính thức (đã gỡ khỏi bản cũ). Nhiều dịch vụ trước đây bị **thiếu** (vd `AppSync`, `Amplify`, `AppConfig`, `EventBridge`, `Cognito`, `STS`, `WAF`, `EKS`, `ECR`, `Aurora`…) nay đã bổ sung đầy đủ.

### Analytics
- `Amazon Athena`
- `Amazon Kinesis`
- `Amazon OpenSearch Service`

### Application Integration
- `AWS AppSync`
- `Amazon EventBridge`
- `Amazon Simple Notification Service` (`Amazon SNS`)
- `Amazon Simple Queue Service` (`Amazon SQS`)
- `AWS Step Functions`

### Compute
- `Amazon EC2`
- `AWS Elastic Beanstalk`
- `AWS Lambda`

### Containers
- `Amazon Elastic Container Registry` (`Amazon ECR`)
- `Amazon Elastic Container Service` (`Amazon ECS`)
- `Amazon Elastic Kubernetes Service` (`Amazon EKS`)

### Database
- `Amazon Aurora`
- `Amazon DynamoDB`
- `Amazon ElastiCache`
- `Amazon RDS`

### Developer Tools
- `AWS Amplify`
- `AWS CloudShell`
- `AWS CodeArtifact`
- `AWS CodeBuild`
- `AWS CodeDeploy`
- `AWS CodePipeline`
- `AWS X-Ray`
- `Amazon Q Developer`

### Management and Governance
- `AWS AppConfig`
- `AWS Cloud Development Kit` (`AWS CDK`)
- `AWS CloudFormation`
- `AWS CloudTrail`
- `Amazon CloudWatch`
- `AWS Command Line Interface` (`AWS CLI`)
- `AWS Systems Manager`

### Networking and Content Delivery
- `Amazon API Gateway`
- `Amazon CloudFront`
- `Elastic Load Balancing`
- `Amazon Route 53`
- `Amazon VPC`

### Security, Identity, and Compliance
- `Amazon Cognito`
- `AWS Identity and Access Management` (`IAM`)
- `AWS Key Management Service` (`AWS KMS`)
- `AWS Secrets Manager`
- `AWS Security Token Service` (`AWS STS`)
- `AWS WAF`

### Storage
- `Amazon Elastic Block Store` (`Amazon EBS`)
- `Amazon Elastic File System` (`Amazon EFS`)
- `Amazon S3`

> **Tổng cộng: 47 dịch vụ in-scope** (theo trang chính thức tại thời điểm crawl 2026-07-07).

---

## Out-of-Scope AWS Services and Features (danh sách AUTHORITATIVE)

> **Nguồn chính thức (authoritative):** https://docs.aws.amazon.com/aws-certification/latest/developer-associate-02/dva-02-out-of-scope-services.html
> ✅ Danh sách **chính thức** từ trang AWS Certification. AWS ghi rõ: các dịch vụ hoàn toàn không liên quan tới job role của kỳ thi thì **bị loại khỏi cả danh sách này** (nên đây cũng là non-exhaustive). Nếu một dịch vụ out-of-scope xuất hiện trong đáp án thì thường là **mồi nhử**.

### Analytics
- `Amazon QuickSight`

### Business Applications
- `Amazon Chime`
- `Amazon Connect`
- `Amazon WorkMail`

### End User Computing
- `Amazon AppStream 2.0`
- `Amazon WorkSpaces`

### Game Tech
- `Amazon GameLift`

### Machine Learning
- `Amazon Polly`
- `Amazon Rekognition`

### Management and Governance
- `AWS Managed Services` (`AMS`)

### Media Services
- `Amazon Elastic Transcoder`

### Migration and Transfer
- `AWS Application Discovery Service`
- `AWS Application Migration Service`

### Security, Identity, and Compliance
- `AWS Shield Advanced`
- `AWS Shield Standard`

### Storage
- `AWS Snow Family`
- `AWS Storage Gateway`
