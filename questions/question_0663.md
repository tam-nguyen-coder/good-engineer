# Question #663 - Topic 1

A company is developing a new application on AWS. The application consists of an Amazon Elastic Container Service (Amazon ECS) cluster, an Amazon S3 bucket that contains assets for the application, and an Amazon RDS for MySQL database that contains the dataset for the application. The dataset contains sensitive information. The company wants to ensure that only the ECS cluster can access the data in the RDS for MySQL database and the data in the S3 bucket. Which solution will meet these requirements?

## Options

**A.** Create a new AWS Key Management Service (AWS KMS) customer managed key to encrypt both the S3 bucket and the RDS for MySQL database. Ensure that the KMS key policy includes encrypt and decrypt permissions for the ECS task execution role.

**B.** Create an AWS Key Management Service (AWS KMS) AWS managed key to encrypt both the S3 bucket and the RDS for MySQL database. Ensure that the S3 bucket policy specifies the ECS task execution role as a user.

**C.** Create an S3 bucket policy that restricts bucket access to the ECS task execution role. Create a VPC endpoint for Amazon RDS for MySQL. Update the RDS for MySQL security group to allow access from only the subnets that the ECS cluster will generate tasks in.

**D.** Create a VPC endpoint for Amazon RDS for MySQL. Update the RDS for MySQL security group to allow access from only the subnets that the ECS cluster will generate tasks in. Create a VPC endpoint for Amazon S3. Update the S3 bucket policy to allow access from only the S3 VPC endpoint.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ECS cluster, S3 bucket (assets), RDS MySQL (sensitive data). Only ECS cluster should access both.
- **Existing Resources:** ECS cluster, S3 bucket, RDS MySQL.
- **Current Issue/Goal:** Restrict access to RDS and S3 to only ECS cluster.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `VPC endpoint for RDS` | Interface endpoint để RDS chỉ nhận traffic từ trong VPC. |
| `security group` | Restrict RDS access to only ECS subnets/tasks. |
| `VPC endpoint for S3` | Gateway endpoint hoặc Interface endpoint để S3 chỉ accessible từ VPC. |
| `S3 bucket policy` | Restrict access to only the VPC endpoint. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (least privilege)
- **Constraints:** Only ECS cluster can access both RDS and S3

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- VPC endpoint for RDS (interface endpoint): RDS chỉ accessible qua VPC endpoint.
- Security group on RDS: chỉ allow traffic từ subnets ECS tasks chạy.
- VPC endpoint for S3 (gateway/interface endpoint): S3 chỉ accessible từ VPC.
- S3 bucket policy: restrict access chỉ cho phép từ S3 VPC endpoint.
- Kết hợp: traffic đến RDS và S3 chỉ từ ECS tasks trong VPC.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- KMS encryption kiểm soát decryption permissions, không kiểm soát network access.
- ECS task execution role có decrypt permission → vẫn có thể decrypt từ bên ngoài VPC.

**❌ Đáp án B:**
- AWS managed key không thể custom key policy.
- S3 bucket policy chỉ định ECS role nhưng RDS access không được kiểm soát.

**❌ Đáp án C:**
- S3 bucket policy restrict to ECS role có thể access từ bất kỳ network nào.
- RDS VPC endpoint + security group cho ECS subnets tốt, nhưng S3 vẫn có thể access từ internet qua role.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Restrict access to ECS only → VPC endpoints + security groups + bucket policy = defense in depth."*
