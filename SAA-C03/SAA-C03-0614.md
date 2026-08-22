# Question #614 - Topic 1

A company is designing a new multi-tier web application that consists of the following components: • Web and application servers that run on Amazon EC2 instances as part of Auto Scaling groups • An Amazon RDS DB instance for data storage A solutions architect needs to limit access to the application servers so that only the web servers can access them. Which solution will meet these requirements?

## Options

**A.** Deploy AWS PrivateLink in front of the application servers. Configure the network ACL to allow only the web servers to access the application servers.

**B.** Deploy a VPC endpoint in front of the application servers. Configure the security group to allow only the web servers to access the application servers.

**C.** Deploy a Network Load Balancer with a target group that contains the application servers' Auto Scaling group. Configure the network ACL to allow only the web servers to access the application servers.

**D.** Deploy an Application Load Balancer with a target group that contains the application servers' Auto Scaling group. Configure the security group to allow only the web servers to access the application servers.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-tier web app: web tier (EC2 ASG) + app tier (EC2 ASG) + RDS. Cần limit app servers access chỉ từ web servers.
- **Existing Resources:** EC2 instances, Auto Scaling groups, RDS.
- **Current Issue/Goal:** Restrict traffic: web servers → app servers only.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `limit access to the application servers` | Cần security group rules để restrict source. |
| `only the web servers can access them` | SG của app servers allow inbound từ SG của web servers. |
| `web servers` | Inbound từ web tier → app tier. |
| `Auto Scaling groups` | Security groups có thể tham chiếu lẫn nhau (SG chaining). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (security)
- **Constraints:** Web → app tier access control

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Application Load Balancer: phù hợp cho HTTP/HTTPS traffic giữa web tier và app tier.
- ALB target group chứa app servers' ASG → tự động đăng ký/bỏ instance.
- Security group của app servers: allow inbound traffic từ ALB's security group.
- Web servers gửi request đến ALB → ALB forward đến app servers.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS PrivateLink dùng để expose service privately trong VPC, không phải để hạn chế access giữa các tiers.
- NACL là stateless, khó cấu hình dynamic cho ASG.

**❌ Đáp án B:**
- VPC endpoint dùng để kết nối đến AWS services, không phải để đặt trước application servers.

**❌ Đáp án C:**
- NLB hoạt động ở Layer 4, không có HTTP routing capabilities.
- NACL stateless → cần cấu hình cả inbound và outbound rules.
- ALB (Layer 7) phù hợp hơn cho web traffic.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-tier: ALB giữa web và app tiers. SG chaining (allow từ SG khác). NACL = stateless, khó xài."*
