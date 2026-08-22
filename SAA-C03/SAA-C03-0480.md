# Question #480 - Topic 1

A business application is hosted on Amazon EC2 and uses Amazon S3 for encrypted object storage. The chief information security officer has directed that no application traffic between the two services should traverse the public internet. Which capability should the solutions architect use to meet the compliance requirements?

## Options

**A.** AWS Key Management Service (AWS KMS)

**B.** VPC endpoint

**C.** Private subnet

**D.** Virtual private gateway

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Business app EC2 → S3 encrypted storage. Security: traffic giữa EC2 và S3 không được qua internet.
- **Existing Resources:** EC2 instance, S3 bucket với encryption.
- **Current Issue/Goal:** Traffic private, không qua internet.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `no application traffic between the two services should traverse the public internet` | Cần VPC endpoint (Gateway endpoint) cho S3. |
| `VPC endpoint` | Cho phép traffic đến AWS services qua AWS network, không qua internet. |
| `S3` | Gateway endpoint cho S3 là free, dùng route table. |
| `private subnet` | EC2 trong private subnet vẫn cần NAT/endpoint để ra ngoài. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Network compliance
- **Constraints:** No public internet traffic between EC2 and S3

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- VPC endpoint (Gateway endpoint) cho S3: traffic từ EC2 đến S3 đi qua AWS private network.
- Không cần internet gateway, NAT gateway, không tốn phí.
- Endpoint được gán vào route table, tự động route traffic đến S3 qua AWS backbone.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS KMS: quản lý encryption keys, không giải quyết network traffic privacy.
- Encryption không đồng nghĩa với private network.

**❌ Đáp án C:**
- Private subnet: EC2 trong private subnet không có direct internet access. Nhưng traffic đến S3 mặc định vẫn qua internet (qua NAT gateway).
- Riêng private subnet không đảm bảo traffic S3 không qua internet.

**❌ Đáp án D:**
- Virtual Private Gateway (VPG): dùng cho VPN/Direct Connect kết nối on-premises với VPC.
- Không liên quan đến EC2-to-S3 traffic.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EC2 → S3 không qua internet = VPC Endpoint (Gateway). KMS = encrypt, không phải network."*
