# Question #385 - Topic 1

A solutions architect is creating a new VPC design. There are two public subnets for the load balancer, two private subnets for web servers, and two private subnets for MySQL. The web servers use only HTTPS. The solutions architect has already created a security group for the load balancer allowing port 443 from 0.0.0.0/0. Company policy requires that each resource has the least access required to still be able to perform its tasks. Which additional configuration strategy should the solutions architect use to meet these requirements?

## Options

**A.** Create a security group for the web servers and allow port 443 from 0.0.0.0/0. Create a security group for the MySQL servers and allow port 3306 from the web servers security group.

**B.** Create a network ACL for the web servers and allow port 443 from 0.0.0.0/0. Create a network ACL for the MySQL servers and allow port 3306 from the web servers security group.

**C.** Create a security group for the web servers and allow port 443 from the load balancer. Create a security group for the MySQL servers and allow port 3306 from the web servers security group.

**D.** Create a network ACL for the web servers and allow port 443 from the load balancer. Create a network ACL for the MySQL servers and allow port 3306 from the web servers security group.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** VPC: LB (public), web servers (private), MySQL (private). Web uses HTTPS only. Least access required.
- **Existing Resources:** Security group for LB allowing 443 from 0.0.0.0/0.
- **Current Issue/Goal:** Security groups with least privilege (SG chaining).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `least access required` | SG chaining: chỉ allow traffic từ SG nguồn, không 0.0.0.0/0. |
| `security group` | SG là stateful, phù hợp cho least privilege. NACL là stateless. |
| `web servers use only HTTPS` | Port 443 từ LB's SG. |
| `MySQL` | Port 3306 từ web servers' SG. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least access configuration
- **Constraints:** HTTPS, MySQL, security groups

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Web SG: inbound HTTPS (443) chỉ từ LB's SG → không expose web servers ra ngoài.
- MySQL SG: inbound MySQL (3306) chỉ từ web servers' SG → least privilege.
- Security groups (stateful) dễ quản lý hơn NACL cho use case này.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Web SG allow 443 from 0.0.0.0/0 → quá rộng, không least privilege.

**❌ Đáp án B:**
- NACL: stateless → cần inbound + outbound rules phức tạp hơn. NACL không support referencing SG (chỉ CIDR).

**❌ Đáp án D:**
- NACL: stateless + không support SG reference → không thể "allow from web servers security group".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Least privilege → SG chaining (LB→Web→MySQL). Không dùng 0.0.0.0/0 cho SG private. NACL = stateless + no SG reference."*
