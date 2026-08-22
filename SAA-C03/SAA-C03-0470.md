# Question #470 - Topic 1

A company has applications hosted on Amazon EC2 instances with IPv6 addresses. The applications must initiate communications with other external applications using the internet. However the company's security policy states that any external service cannot initiate a connection to the EC2 instances. What should a solutions architect recommend to resolve this issue?

## Options

**A.** Create a NAT gateway and make it the destination of the subnet's route table

**B.** Create an internet gateway and make it the destination of the subnet's route table

**C.** Create a virtual private gateway and make it the destination of the subnet's route table

**D.** Create an egress-only internet gateway and make it the destination of the subnet's route table

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances with IPv6, cần outbound internet communication. Security policy: không cho inbound từ internet.
- **Existing Resources:** EC2 instances with IPv6.
- **Current Issue/Goal:** Outbound-only internet access for IPv6.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `IPv6 addresses` | EC2 có IPv6 → NAT gateway không hỗ trợ IPv6. |
| `initiate communications` | Outbound connection từ EC2 ra internet. |
| `external service cannot initiate` | Outbound-only, không inbound. |
| `egress-only internet gateway` | Dành riêng cho IPv6, outbound-only. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Outbound-only IPv6 internet access
- **Constraints:** IPv6 only, outbound-only, no inbound

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Egress-Only Internet Gateway (EIGW): cho phép IPv6 instances outbound ra internet nhưng ngăn internet inbound vào instances.
- Là lựa chọn duy nhất cho IPv6 outbound-only (NAT gateway chỉ hỗ trợ IPv4).
- Route table: thêm route `::/0` → egress-only internet gateway.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- NAT gateway chỉ hỗ trợ IPv4, không hỗ trợ IPv6.

**❌ Đáp án B:**
- Internet gateway (IGW) cho phép cả inbound và outbound cho IPv6, không thỏa security policy.

**❌ Đáp án C:**
- Virtual Private Gateway (VPG) dùng cho VPN/Direct Connect kết nối on-premises với VPC, không phải internet.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"IPv6 + outbound-only = Egress-Only Internet Gateway. NAT gateway = IPv4 only. IGW = 2 chiều (in + out)."*
