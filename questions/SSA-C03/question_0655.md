# Question #655 - Topic 1

A company runs a web application on Amazon EC2 instances in an Auto Scaling group that has a target group. The company designed the application to work with session affinity (sticky sessions) for a better user experience. The application must be available publicly over the internet as an endpoint. A WAF must be applied to the endpoint for additional security. Session affinity (sticky sessions) must be configured on the endpoint. Which combination of steps will meet these requirements? (Choose two.)

## Options

**A.** Create a public Network Load Balancer. Specify the application target group.

**B.** Create a Gateway Load Balancer. Specify the application target group.

**C.** Create a public Application Load Balancer. Specify the application target group.

**D.** Create a second target group. Add Elastic IP addresses to the EC2 instances.

**E.** Create a web ACL in AWS WAF. Associate the web ACL with the endpoint

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app on EC2 in ASG, need sticky sessions, public endpoint, WAF security.
- **Existing Resources:** ASG with target group.
- **Current Issue/Goal:** Public load balancer with sticky sessions + WAF.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `session affinity (sticky sessions)` | ALB hỗ trợ sticky sessions (NLB không). |
| `WAF` | AWS WAF chỉ associate được với ALB, CloudFront, API Gateway, AppSync. Không hỗ trợ NLB. |
| `public endpoint` | Internet-facing load balancer. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (choose two)
- **Constraints:** Sticky sessions, WAF, public

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C và E**

**Giải thích:**
- **C:** ALB hỗ trợ sticky sessions (cookie-based), public endpoint. ALB có thể associate với WAF.
- **E:** Tạo Web ACL trong AWS WAF, associate với ALB endpoint để bảo vệ web application.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- NLB không hỗ trợ sticky sessions (layer 4, không có cookie).
- NLB không thể associate với AWS WAF trực tiếp.

**❌ Đáp án B:**
- Gateway Load Balancer dùng cho third-party appliances (firewall, IDS/IPS), không phải web application.
- Không hỗ trợ sticky sessions.

**❌ Đáp án D:**
- Elastic IP + second target group không giải quyết sticky sessions hay WAF.
- Phá vỡ auto scaling (EIP gắn với instance cụ thể).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Sticky sessions + WAF → only ALB. NLB = no stickiness, no WAF."*
