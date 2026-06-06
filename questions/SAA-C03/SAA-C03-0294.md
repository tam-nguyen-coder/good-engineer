# Question #294 - Topic 1

An application that is hosted on Amazon EC2 instances needs to access an Amazon S3 bucket. Traffic must not traverse the internet. How should a solutions architect configure access to meet these requirements?

## Options

**A.** Create a private hosted zone by using Amazon Route 53.

**B.** Set up a gateway VPC endpoint for Amazon S3 in the VPC.

**C.** Configure the EC2 instances to use a NAT gateway to access the S3 bucket.

**D.** Establish an AWS Site-to-Site VPN connection between the VPC and the S3 bucket.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances cần access S3 bucket, traffic không được qua internet.
- **Existing Resources:** EC2 instances, S3 bucket (cùng account hoặc khác? Không quan trọng).
- **Current Issue/Goal:** EC2 → S3 traffic qua private AWS network, không qua internet.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `must not traverse the internet` | Không dùng NAT gateway, internet gateway, VPN. |
| `gateway VPC endpoint` | Gateway endpoint cho S3 dùng AWS private network (không qua internet). |
| `VPC endpoint` | Cho phép VPC resources access AWS services privately. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** No internet traffic, EC2 in VPC, S3 access

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Gateway VPC endpoint cho S3 cho phép EC2 instances trong VPC access S3 thông qua AWS private network (sử dụng route table).
- Traffic đi qua AWS backbone, không qua internet → an toàn và miễn phí.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Private hosted zone dùng cho DNS resolution (Route 53), không ảnh hưởng đến network path.

**❌ Đáp án C:**
- NAT gateway cho phép outbound internet traffic → traffic đi qua internet, không đáp ứng yêu cầu.

**❌ Đáp án D:**
- Site-to-Site VPN kết nối on-premises với VPC, không liên quan EC2 → S3 access.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EC2 → S3 no internet → Gateway VPC Endpoint. NAT/IGW = internet. VPN = on-premises."*
