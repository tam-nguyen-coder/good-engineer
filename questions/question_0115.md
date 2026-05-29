# Question #115 - Topic 1

A medical records company is hosting an application on Amazon EC2 instances. The application processes customer data files that are stored on Amazon S3. The EC2 instances are hosted in public subnets. The EC2 instances access Amazon S3 over the internet, but they do not require any other network access. A new requirement mandates that the network traffic for file transfers take a private route and not be sent over the internet. Which change to the network architecture should a solutions architect recommend to meet this requirement?

## Options

**A.** Create a NAT gateway. Configure the route table for the public subnets to send traffic to Amazon S3 through the NAT gateway.

**B.** Configure the security group for the EC2 instances to restrict outbound traffic so that only traffic to the S3 prefix list is permitted.

**C.** Move the EC2 instances to private subnets. Create a VPC endpoint for Amazon S3, and link the endpoint to the route table for the private subnets.

**D.** Remove the internet gateway from the VPC. Set up an AWS Direct Connect connection, and route traffic to Amazon S3 over the Direct Connect connection.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 in public subnets access S3 over internet. New rule: private only, no internet.
- **Existing Resources:** EC2 in public subnets, S3 bucket.
- **Current Issue/Goal:** Private S3 access, no internet.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `private route and not be sent over the internet` | Cần **S3 VPC Gateway Endpoint** |
| `do not require any other network access` | Private subnets (không cần IGW) |
| `VPC endpoint` | Private connection to AWS services |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Network security
- **Constraints:** Private S3 access, no internet

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Move EC2 to private subnets** — không cần IGW, tăng security.
- **S3 VPC Gateway Endpoint** — kết nối private từ VPC đến S3, traffic không qua internet.
- Route table private subnets trỏ đến S3 endpoint.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- NAT gateway — traffic vẫn qua internet (NAT → internet → S3). Không private.

**❌ Đáp án B:**
- Security group restrict — traffic vẫn qua internet, không giải quyết yêu cầu private route.

**❌ Đáp án D:**
- Remove IGW + Direct Connect — tốn kém, không cần thiết. S3 Gateway Endpoint là free và đơn giản hơn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Gateway Endpoint = private + free. NAT gateway = internet (not private). Direct Connect = costly for this"*
