# Question #327 - Topic 1

A solutions architect must secure a VPC network that hosts Amazon EC2 instances. The EC2 instances contain highly sensitive data and run in a private subnet. According to company policy, the EC2 instances that run in the VPC can access only approved third-party software repositories on the internet for software product updates that use the third party's URL. Other internet traffic must be blocked. Which solution meets these requirements?

## Options

**A.** Update the route table for the private subnet to route the outbound traffic to an AWS Network Firewall firewall. Configure domain list rule groups.

**B.** Set up an AWS WAF web ACL. Create a custom set of rules that filter traffic requests based on source and destination IP address range sets.

**C.** Implement strict inbound security group rules. Configure an outbound rule that allows traffic only to the authorized software repositories on the internet by specifying the URLs.

**D.** Configure an Application Load Balancer (ALB) in front of the EC2 instances. Direct all outbound traffic to the ALB. Use a URL-based rule listener in the ALB's target group for outbound access to the internet.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances trong private subnet chứa sensitive data. Chỉ được access approved URLs cho software updates. Block all other internet traffic.
- **Existing Resources:** VPC, EC2 in private subnet.
- **Current Issue/Goal:** Outbound filtering by URL/domain, block other traffic.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `URLs` | Cần filter by domain/URL, không chỉ IP. |
| `AWS Network Firewall` | Managed firewall có thể filter outbound traffic by domain (domain list rule groups). |
| `private subnet` | Không có direct internet access → cần NAT gateway + route to firewall. |
| `security group` | Chỉ filter by IP/port, không filter by domain name. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Filter by domain URLs, block other internet traffic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS Network Firewall: deploy trong VPC, route table của private subnet trỏ outbound traffic tới firewall.
- Domain list rule groups: cho phép traffic chỉ tới approved domains (software repositories).
- Tất cả traffic khác bị block mặc định.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- AWS WAF bảo vệ web applications (ALB, CloudFront) ở layer 7, không filter outbound general internet traffic từ EC2.

**❌ Đáp án C:**
- Security group outbound rules chỉ filter by IP/port/protocol, không thể filter by domain name/URL.

**❌ Đáp án D:**
- ALB dùng cho inbound traffic distribution, không phải outbound proxy. Không thể direct outbound traffic từ EC2 qua ALB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Filter outbound by domain → AWS Network Firewall (domain list). SG = IP only. WAF = web inbound."*
