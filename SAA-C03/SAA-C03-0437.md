# Question #437 - Topic 1

A company operates an ecommerce website on Amazon EC2 instances behind an Application Load Balancer (ALB) in an Auto Scaling group. The site is experiencing performance issues related to a high request rate from illegitimate external systems with changing IP addresses. The security team is worried about potential DDoS attacks against the website. The company must block the illegitimate incoming requests in a way that has a minimal impact on legitimate users. What should a solutions architect recommend?

## Options

**A.** Deploy Amazon Inspector and associate it with the ALB.

**B.** Deploy AWS WAF, associate it with the ALB, and configure a rate-limiting rule.

**C.** Deploy rules to the network ACLs associated with the ALB to block the incomingtraffic.

**D.** Deploy Amazon GuardDuty and enable rate-limiting protection when configuring GuardDuty.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce, high request rate from illegitimate systems (changing IPs). Performance issues, DDoS concern. Block with minimal impact on legitimate users.
- **Existing Resources:** EC2, ALB, ASG.
- **Current Issue/Goal:** Block bad traffic, allow legitimate users.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `changing IP addresses` | IP-based blocking không hiệu quả. Cần rate limiting. |
| `DDoS attacks` | AWS WAF rate-based rules. |
| `minimal impact on legitimate users` | Rate limiting: allow bursts, block excessive requests. |
| `AWS WAF` | Web application firewall, associate with ALB. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / DDoS protection
- **Constraints:** Block illegitimate traffic, minimal impact on legitimate users

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS WAF associated with ALB: inspect HTTP/HTTPS requests.
- Rate-based rule: block IPs when request rate vượt ngưỡng → ngăn DDoS, vẫn cho phép traffic bình thường.
- Phù hợp cho changing IPs (rate limit vẫn hiệu quả bất kể IP có thay đổi).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Amazon Inspector: vulnerability assessment, không phải WAF/DDoS protection.

**❌ Đáp án C:**
- NACL: stateless, không thể phân biệt legitimate vs illegitimate traffic, khó quản lý khi IPs thay đổi.

**❌ Đáp án D:**
- GuardDuty: threat detection, không có "rate-limiting protection". Chỉ phát hiện, không block.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DDoS + changing IPs → WAF rate-based rules on ALB. NACL/GuardDuty không block được."*