# Question #612 - Topic 1

A company has an application that runs on Amazon EC2 instances in a private subnet. The application needs to process sensitive information from an Amazon S3 bucket. The application must not use the internet to connect to the S3 bucket. Which solution will meet these requirements?

## Options

**A.** Configure an internet gateway. Update the S3 bucket policy to allow access from the internet gateway. Update the application to use the new internet gateway.

**B.** Configure a VPN connection. Update the S3 bucket policy to allow access from the VPN connection. Update the application to use the new VPN connection.

**C.** Configure a NAT gateway. Update the S3 bucket policy to allow access from the NAT gateway. Update the application to use the new NAT gateway.

**D.** Configure a VPC endpoint. Update the S3 bucket policy to allow access from the VPC endpoint. Update the application to use the new VPC endpoint.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances in private subnet cần truy cập S3 bucket để xử lý sensitive information, không được dùng internet.
- **Existing Resources:** EC2 instances in private subnet, S3 bucket.
- **Current Issue/Goal:** Private connectivity EC2 → S3 without internet.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `private subnet` | Không có internet access mặc định. |
| `must not use the internet` | Không được dùng IGW, NAT, VPN (VPN dùng internet dù encrypted). |
| `VPC endpoint` | Kết nối trực tiếp đến AWS services qua AWS private network, không qua internet. |
| `S3 gateway endpoint` | Gateway endpoint cho S3, free, dùng AWS private network. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (security/compliance)
- **Constraints:** Private subnet, no internet, EC2 → S3

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- VPC Endpoint (Gateway type) for S3: cho phép EC2 trong private subnet kết nối đến S3 qua AWS private network.
- Không cần internet gateway, NAT gateway, hay VPN.
- S3 bucket policy có thể restrict access chỉ từ VPC endpoint → tăng security.
- Gateway endpoint là free, không tính phí.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Internet gateway: private subnet không thể dùng IGW trực tiếp, và dùng internet → vi phạm yêu cầu.

**❌ Đáp án B:**
- VPN connection: dùng internet để kết nối (dù encrypted) → vi phạm yêu cầu "not use internet".

**❌ Đáp án C:**
- NAT gateway: dùng để outbound internet, EC2 trong private subnet đi qua NAT → vẫn dùng internet.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Private subnet + S3 + no internet → VPC Gateway Endpoint (free, private, no internet)."*
