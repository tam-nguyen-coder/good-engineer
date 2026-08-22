# Question #176 - Topic 1

An application runs on Amazon EC2 instances in private subnets. The application needs to access an Amazon DynamoDB table. What is the MOST secure way to access the table while ensuring that the traffic does not leave the AWS network?

## Options

**A.** Use a VPC endpoint for DynamoDB.

**B.** Use a NAT gateway in a public subnet.

**C.** Use a NAT instance in a private subnet.

**D.** Use the internet gateway attached to the VPC.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 in private subnets → access DynamoDB. Traffic must not leave AWS network.
- **Existing Resources:** EC2 instances, private subnets.
- **Current Issue/Goal:** Most secure, traffic stays within AWS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `traffic does not leave the AWS network` | **VPC endpoint** (Gateway endpoint for DynamoDB) |
| `most secure` | Không cần NAT/IGW → không expose internet |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / Security
- **Constraints:** Private subnet, no internet traffic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **VPC Gateway Endpoint for DynamoDB** — cho phép EC2 trong private subnet access DynamoDB qua AWS internal network.
- Không cần NAT Gateway, Internet Gateway → traffic không rời AWS network.
- Free, secure, HA.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- NAT Gateway — traffic đi qua internet, tốn chi phí.

**❌ Đáp án C:**
- NAT instance — traffic đi qua internet, operational overhead.

**❌ Đáp án D:**
- Internet Gateway — traffic đi qua internet, kém secure.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"VPC Gateway Endpoint = DynamoDB + S3 internal access. NAT/IGW = internet (less secure)"*
