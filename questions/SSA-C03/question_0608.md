# Question #608 - Topic 1

A company has an application that serves clients that are deployed in more than 20.000 retail storefront locations around the world. The application consists of backend web services that are exposed over HTTPS on port 443. The application is hosted on Amazon EC2 instances behind an Application Load Balancer (ALB). The retail locations communicate with the web application over the public internet. The company allows each retail location to register the IP address that the retail location has been allocated by its local ISP. The company's security team recommends to increase the security of the application endpoint by restricting access to only the IP addresses registered by the retail locations. What should a solutions architect do to meet these requirements?

## Options

**A.** Associate an AWS WAF web ACL with the ALB. Use IP rule sets on the ALB to filter traffic. Update the IP addresses in the rule to include the registered IP addresses.

**B.** Deploy AWS Firewall Manager to manage the ALB. Configure firewall rules to restrict traffic to the ALB. Modify the firewall rules to include the registered IP addresses.

**C.** Store the IP addresses in an Amazon DynamoDB table. Configure an AWS Lambda authorization function on the ALB to validate that incoming requests are from the registered IP addresses.

**D.** Configure the network ACL on the subnet that contains the public interface of the ALB. Update the ingress rules on the network ACL with entries for each of the registered IP addresses.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 20,000+ retail locations worldwide, HTTPS trên port 443, EC2 + ALB. Cần restrict access chỉ cho registered IP addresses.
- **Existing Resources:** EC2 instances, ALB, public internet access.
- **Current Issue/Goal:** IP-based access restriction cho 20,000+ IPs, tăng security.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `20.000+ retail locations` | Số lượng IP rất lớn. WAF IP sets: mỗi set tối đa 10,000 IPs, có thể dùng nhiều sets. |
| `registered IP addresses` | IP-based allowlist. |
| `restricting access` | Layer 7 filtering → WAF phù hợp. |
| `ALB` | WAF có thể associate trực tiếp với ALB. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (security)
- **Constraints:** 20,000+ IPs, HTTPS, ALB

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS WAF có thể associate với ALB, dùng IP set match condition để allowlist IPs.
- Mỗi IP set chứa tối đa 10,000 IP addresses, có thể dùng nhiều IP sets trong một rule group.
- WAF web ACL được quản lý tập trung, dễ dàng thêm/xóa IP.
- Giải pháp layer 7, tối ưu cho web application.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- AWS Firewall Manager dùng để quản lý WAF rules centrally across accounts, không phải để cấu hình IP allowlist trực tiếp cho single ALB.

**❌ Đáp án C:**
- Lambda authorizer trên ALB cho authentication (cognito/OIDC), không phải use case cho IP filtering.
- Operational overhead cao hơn WAF.

**❌ Đáp án D:**
- NACL hoạt động ở subnet level, không phải ở ALB level (ALB là managed service).
- NACL là stateless firewall, khó quản lý cho 20,000+ IPs.
- ALB không nằm trong subnet public interface theo cách có thể dùng NACL hiệu quả.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"IP allowlist cho ALB → WAF IP sets. NACL = stateless, khó quản lý 20K IPs."*
