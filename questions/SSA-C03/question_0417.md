# Question #417 - Topic 1

A company uses Amazon EC2 instances and AWS Lambda functions to run its application. The company has VPCs with public subnets and private subnets in its AWS account. The EC2 instances run in a private subnet in one of the VPCs. The Lambda functions need direct network access to the EC2 instances for the application to work. The application will run for at least 1 year. The company expects the number of Lambda functions that the application uses to increase during that time. The company wants to maximize its savings on all application resources and to keep network latency between the services low. Which solution will meet these requirements?

## Options

**A.** Purchase an EC2 Instance Savings Plan Optimize the Lambda functions' duration and memory usage and the number of invocations. Connect the Lambda functions to the private subnet that contains the EC2 instances.

**B.** Purchase an EC2 Instance Savings Plan Optimize the Lambda functions' duration and memory usage, the number of invocations, and the amount of data that is transferred. Connect the Lambda functions to a public subnet in the same VPC where the EC2 instances run.

**C.** Purchase a Compute Savings Plan. Optimize the Lambda functions' duration and memory usage, the number of invocations, and the amount of data that is transferred. Connect the Lambda functions to the private subnet that contains the EC2 instances.

**D.** Purchase a Compute Savings Plan. Optimize the Lambda functions' duration and memory usage, the number of invocations, and the amount of data that is transferred. Keep the Lambda functions in the Lambda service VPC.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 (private subnet) + Lambda. Lambda needs direct network access to EC2. Running 1+ year. Maximize savings, low latency.
- **Existing Resources:** VPC, public/private subnets, EC2 in private subnet.
- **Current Issue/Goal:** Cost savings + VPC connectivity for Lambda to EC2.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `direct network access` | Lambda must be VPC-enabled, attached to same private subnet. |
| `maximize savings` | Compute Savings Plan: covers EC2 + Lambda (flexible). |
| `at least 1 year` | Savings Plan 1-year or 3-year commitment. |
| `Lambda` | SP optimization: duration + memory. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization / Networking
- **Constraints:** Lambda to EC2 direct access, max savings

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Compute Savings Plan: covers EC2 + Lambda + Fargate (linh hoạt nhất). EC2 Instance Savings Plan chỉ cover EC2.
- Lambda VPC-enabled: attach to private subnet → direct network access to EC2.
- Optimize: duration + memory usage (áp dụng cho Lambda SP).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 Instance Savings Plan: không cover Lambda → không tối ưu savings cho Lambda.

**❌ Đáp án B:**
- EC2 Instance Savings Plan: không cover Lambda. Public subnet: Lambda vẫn có thể reach private subnet qua NAT nhưng không "direct".

**❌ Đáp án D:**
- Lambda ở default VPC (Lambda service VPC): không thể reach EC2 trong private subnet (no network path).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Compute SP = EC2 + Lambda. Lambda VPC-enabled to private subnet for direct access."*