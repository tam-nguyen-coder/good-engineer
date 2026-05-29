# Question #509 - Topic 1

A company operates a two-tier application for image processing. The application uses two Availability Zones, each with one public subnet and one private subnet. An Application Load Balancer (ALB) for the web tier uses the public subnets. Amazon EC2 instances for the application tier use the private subnets. Users report that the application is running more slowly than expected. A security audit of the web server log files shows that the application is receiving millions of illegitimate requests from a small number of IP addresses. A solutions architect needs to resolve the immediate performance problem while the company investigates a more permanent solution. What should the solutions architect recommend to meet this requirement?

## Options

**A.** Modify the inbound security group for the web tier. Add a deny rule for the IP addresses that are consuming resources.

**B.** Modify the network ACL for the web tier subnets. Add an inbound deny rule for the IP addresses that are consuming resources.

**C.** Modify the inbound security group for the application tier. Add a deny rule for the IP addresses that are consuming resources.

**D.** Modify the network ACL for the application tier subnets. Add an inbound deny rule for the IP addresses that are consuming resources.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Two-tier app (ALB public, EC2 private). Nhận triệu request từ một số IP nhỏ (DDoS/IP blocking). Cần giải pháp immediate.
- **Existing Resources:** ALB trong public subnet, EC2 trong private subnet, 2 AZs.
- **Current Issue/Goal:** Chặn IP độc hại ngay lập tức.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `small number of IP addresses` | Có thể block cụ thể từng IP. |
| `resolve the immediate performance problem` | Giải pháp nhanh, tạm thời. |
| `deny rule` | Security Group không hỗ trợ deny rule, chỉ allow. NACL hỗ trợ cả allow và deny. |
| `web tier subnets` | Nơi ALB đặt → public subnets. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Immediate problem resolution
- **Constraints:** Block specific IPs, immediate fix

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Network ACL (NACL) hỗ trợ deny rules (stateless firewall). Security Group (SG) chỉ hỗ trợ allow rules (stateful).
- Web tier subnets (public subnets nơi ALB đặt): thêm inbound deny rule cho các IP độc hại → chặn request trước khi đến ALB.
- NACL là giải pháp nhanh, immediate. Sau đó có thể triển khai WAF hoặc Shield làm permanent solution.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Security Group không hỗ trợ deny rule. Chỉ có allow rules. Không thể "add a deny rule" vào SG.

**❌ Đáp án C:**
- Security Group cho application tier private subnets: tương tự, không hỗ trợ deny rule. Ngoài ra, ở application tier, traffic đã qua ALB → source IP là ALB, không còn là IP client gốc.

**❌ Đáp án D:**
- NACL cho application tier subnets: traffic đến application tier đã qua ALB → source IP là ALB's internal IP, không phải IP của attacker.
- Block ở đây không có tác dụng vì IP gốc đã bị thay thế bởi ALB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Block IP → NACL (có deny rule). Security Group = allow only. NACL ở public subnet (trước ALB) để chặn từ xa."*
