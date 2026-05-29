# Question #340 - Topic 1

A media company hosts its website on AWS. The website application's architecture includes a fleet of Amazon EC2 instances behind an Application Load Balancer (ALB) and a database that is hosted on Amazon Aurora. The company's cybersecurity team reports that the application is vulnerable to SQL injection. How should the company resolve this issue?

## Options

**A.** Use AWS WAF in front of the ALB. Associate the appropriate web ACLs with AWS WAF.

**B.** Create an ALB listener rule to reply to SQL injections with a fixed response.

**C.** Subscribe to AWS Shield Advanced to block all SQL injection attempts automatically.

**D.** Set up Amazon Inspector to block all SQL injection attempts automatically.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Website vulnerable to SQL injection. Architecture: EC2 + ALB + Aurora.
- **Existing Resources:** ALB, EC2, Aurora database.
- **Current Issue/Goal:** Block SQL injection attacks.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SQL injection` | Web application attack → WAF có managed rules để block SQL injection. |
| `AWS WAF` | Web Application Firewall: inspect HTTP requests, block SQL injection, XSS, etc. |
| `ALB` | WAF associate với ALB để filter traffic trước khi đến application. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** How to resolve SQL injection vulnerability
- **Constraints:** ALB, web application

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS WAF (Web Application Firewall): associate với ALB, use managed rule groups (e.g., AWS-AWSManagedRulesSQLiRuleSet) để block SQL injection attempts.
- WAF inspect HTTP requests before they reach the application, no code changes needed.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ALB listener rules chỉ route/forward traffic based on conditions, không thể "reply to SQL injections".

**❌ Đáp án C:**
- AWS Shield Advanced là DDoS protection service, không block SQL injection (layer 7 attack).

**❌ Đáp án D:**
- Amazon Inspector là vulnerability scanner, không block attacks real-time.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQL injection → AWS WAF + ALB (web ACLs, managed SQLi rules). Shield = DDoS. Inspector = scanner."*
