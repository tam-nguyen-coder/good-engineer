# Question #555 - Topic 1

A company runs an application in a VPC with public and private subnets. The VPC extends across multiple Availability Zones. The application runs on Amazon EC2 instances in private subnets. The application uses an Amazon Simple Queue Service (Amazon SQS) queue. A solutions architect needs to design a secure solution to establish a connection between the EC2 instances and the SQS queue. Which solution will meet these requirements?

## Options

**A.** Implement an interface VPC endpoint for Amazon SQS. Configure the endpoint to use the private subnets. Add to the endpoint a security group that has an inbound access rule that allows traffic from the EC2 instances that are in the private subnets.

**B.** Implement an interface VPC endpoint for Amazon SQS. Configure the endpoint to use the public subnets. Attach to the interface endpoint a VPC endpoint policy that allows access from the EC2 instances that are in the private subnets.

**C.** Implement an interface VPC endpoint for Amazon SQS. Configure the endpoint to use the public subnets. Attach an Amazon SQS access policy to the interface VPC endpoint that allows requests from only a specified VPC endpoint.

**D.** Implement a gateway endpoint for Amazon SQS. Add a NAT gateway to the private subnets. Attach an IAM role to the EC2 instances that allows access to the SQS queue.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ứng dụng chạy trên EC2 instances trong private subnets (multi-AZ). Cần kết nối secure đến SQS queue.
- **Existing Resources:** VPC, public/private subnets, EC2 instances (private subnets), SQS queue.
- **Current Issue/Goal:** Kết nối private EC2 → SQS mà không đi qua internet, secure.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `private subnets` | Không có internet access, cần VPC endpoint để kết nối AWS services |
| `secure solution` | Traffic không đi qua internet |
| `VPC endpoint` | Kết nối AWS services mà không qua internet |
| `interface endpoint` | Sử dụng ENI, hỗ trợ security groups |
| `gateway endpoint` | Chỉ hỗ trợ S3 và DynamoDB |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Secure connection, private subnets, EC2 → SQS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Interface VPC endpoint (AWS PrivateLink) cho SQS tạo ENI (elastic network interface) trong private subnets, cho phép EC2 instances kết nối đến SQS qua AWS internal network.
- Security group gắn vào endpoint kiểm soát inbound traffic từ EC2 instances.
- Không cần NAT Gateway, Internet Gateway, hay VPN.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (Interface endpoint in public subnets):** Đặt endpoint trong public subnets thì traffic từ private subnets vẫn phải đi qua NAT/IGW. Mất tính secure.

**❌ Đáp án C (Interface endpoint in public subnets + SQS access policy):** Giống B, endpoint đặt sai subnet. SQS access policy không thể gắn trực tiếp vào VPC endpoint.

**❌ Đáp án D (Gateway endpoint for SQS):** Gateway endpoint chỉ hỗ trợ S3 và DynamoDB, không hỗ trợ SQS. NAT Gateway + IAM role là giải pháp cũ nhưng không "secure" (đi qua internet) và SQS không có gateway endpoint.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Interface endpoints (PrivateLink) = SQS, SNS, KMS, etc. Gateway endpoints = S3 + DynamoDB only. Always put endpoint in the same subnet as the client."*
