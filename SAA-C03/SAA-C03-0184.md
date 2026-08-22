# Question #184 - Topic 1

A company has an AWS account used for software engineering. The AWS account has access to the company's on-premises data center through a pair of AWS Direct Connect connections. All non-VPC traffic routes to the virtual private gateway. A development team recently created an AWS Lambda function through the console. The development team needs to allow the function to access a database that runs in a private subnet in the company's data center. Which solution will meet these requirements?

## Options

**A.** Configure the Lambda function to run in the VPC with the appropriate security group.

**B.** Set up a VPN connection from AWS to the data center. Route the traffic from the Lambda function through the VPN.

**C.** Update the route tables in the VPC to allow the Lambda function to access the on-premises data center through Direct Connect.

**D.** Create an Elastic IP address. Configure the Lambda function to send traffic through the Elastic IP address without an elastic network interface.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Lambda function (created via console, not in VPC) needs to access on-prem DB via Direct Connect.
- **Existing Resources:** Direct Connect to on-prem, VPC with virtual private gateway.
- **Current Issue/Goal:** Lambda access on-prem database.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Lambda function` | Mặc định không ở trong VPC |
| `virtual private gateway` | Direct Connect kết nối VPC với on-prem |
| `private subnet in the company's data center` | Cần VPC access |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless / Networking
- **Constraints:** Lambda → on-prem via Direct Connect

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Lambda mặc định không có VPC access → không thể reach on-prem qua Direct Connect.
- Cấu hình Lambda chạy trong VPC (attach ENI) → có thể route traffic qua Direct Connect.
- Thêm security group để kiểm soát access.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- VPN không cần thiết, đã có Direct Connect. Lambda vẫn cần VPC.

**❌ Đáp án C:**
- Route tables — Lambda vẫn cần được đặt trong VPC trước.

**❌ Đáp án D:**
- Elastic IP — Lambda không thể dùng EIP trực tiếp, cần VPC + NAT Gateway.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda outside VPC → no Direct Connect. Lambda in VPC + security group → access on-prem"*
