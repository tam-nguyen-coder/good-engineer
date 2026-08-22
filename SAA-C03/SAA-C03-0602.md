# Question #602 - Topic 1

A company's infrastructure consists of hundreds of Amazon EC2 instances that use Amazon Elastic Block Store (Amazon EBS) storage. A solutions architect must ensure that every EC2 instance can be recovered after a disaster. What should the solutions architect do to meet this requirement with the LEAST amount of effort?

## Options

**A.** Take a snapshot of the EBS storage that is attached to each EC2 instance. Create an AWS CloudFormation template to launch new EC2 instances from the EBS storage.

**B.** Take a snapshot of the EBS storage that is attached to each EC2 instance. Use AWS Elastic Beanstalk to set the environment based on the EC2 template and attach the EBS storage.

**C.** Use AWS Backup to set up a backup plan for the entire group of EC2 instances. Use the AWS Backup API or the AWS CLI to speed up the restore process for multiple EC2 instances.

**D.** Create an AWS Lambda function to take a snapshot of the EBS storage that is attached to each EC2 instance and copy the Amazon Machine Images (AMIs). Create another Lambda function to perform the restores with the copied AMIs and attach the EBS storage.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Hundreds of EC2 instances with EBS volumes, cần đảm bảo khả năng phục hồi sau disaster.
- **Existing Resources:** Hundreds of EC2 instances, EBS volumes.
- **Current Issue/Goal:** DR recovery cho tất cả EC2 instances với ít effort nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `hundreds of EC2 instances` | Scale lớn, cần giải pháp tự động hóa. |
| `recovered after a disaster` | Backup và restore toàn bộ instances. |
| `least amount of effort` | AWS Backup: centralized backup service, tự động snapshot quản lý lifecycle. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least effort / operational overhead
- **Constraints:** Hundreds of instances, EBS-based

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS Backup là managed backup service, cho phép tạo backup plan tập trung cho nhiều resources (EBS snapshots).
- Tự động hóa snapshot schedule, retention policy, cross-region copy.
- Restore API/CLI giúp phục hồi nhanh nhiều instances.
- Không cần viết code, không cần quản lý script → least effort.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Tạo snapshot thủ công từng EBS → tốn công sức với hundreds of instances.
- CloudFormation template chỉ giúp launch instance, không tự động snapshot.

**❌ Đáp án B:**
- Elastic Beanstalk dùng cho application deployment, không phải DR solution cho existing instances.
- Không phù hợp vì cần snapshot từng EBS thủ công.

**❌ Đáp án D:**
- Custom Lambda functions tạo snapshot và AMI → operational overhead cao hơn AWS Backup.
- Cần viết, maintain, debug code.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AWS Backup = centralized managed backup cho hundreds of EC2. Custom script = overhead."*
