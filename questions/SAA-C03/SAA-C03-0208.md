# Question #208 - Topic 1

A company needs to move data from an Amazon EC2 instance to an Amazon S3 bucket. The company must ensure that no API calls and no data are routed through public internet routes. Only the EC2 instance can have access to upload data to the S3 bucket. Which solution will meet these requirements?

## Options

**A.** Create an interface VPC endpoint for Amazon S3 in the subnet where the EC2 instance is located. Attach a resource policy to the S3 bucket to only allow the EC2 instance's IAM role for access.

**B.** Create a gateway VPC endpoint for Amazon S3 in the Availability Zone where the EC2 instance is located. Attach appropriate security groups to the endpoint. Attach a resource policy to the S3 bucket to only allow the EC2 instance's IAM role for access.

**C.** Run the nslookup tool from inside the EC2 instance to obtain the private IP address of the S3 bucket's service API endpoint. Create a route in the VPC route table to provide the EC2 instance with access to the S3 bucket. Attach a resource policy to the S3 bucket to only allow the EC2 instance's IAM role for access.

**D.** Use the AWS provided, publicly available ip-ranges.json file to obtain the private IP address of the S3 bucket's service API endpoint. Create a route in the VPC route table to provide the EC2 instance with access to the S3 bucket. Attach a resource policy to the S3 bucket to only allow the EC2 instance's IAM role for access.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 → S3, no public internet. Only EC2 can upload.
- **Existing Resources:** EC2 instance, VPC.
- **Current Issue/Goal:** Private connectivity + access control.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `no public internet` | **VPC Gateway Endpoint** for S3 |
| `only the EC2 instance` | IAM role + bucket policy |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / Security
- **Constraints:** Private, restricted access

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Gateway VPC endpoint** — cho phép EC2 access S3 qua AWS internal network (free).
- **Security group** — giới hạn traffic đến endpoint.
- **Bucket policy** — chỉ allow IAM role của EC2 instance.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Interface VPC endpoint — S3 dùng Gateway endpoint (Interface cho services like API Gateway, Lambda).

**❌ Đáp án C:**
- nslookup — S3 service API không có private IP.

**❌ Đáp án D:**
- ip-ranges.json — public IP ranges, không phải private.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Gateway endpoint = private S3 access. Interface endpoint = other services. No private IP for S3"*
