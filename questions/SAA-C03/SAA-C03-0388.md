# Question #388 - Topic 1

A company is deploying a two-tier web application in a VPC. The web tier is using an Amazon EC2 Auto Scaling group with public subnets that span multiple Availability Zones. The database tier consists of an Amazon RDS for MySQL DB instance in separate private subnets. The web tier requires access to the database to retrieve product information. The web application is not working as intended. The web application reports that it cannot connect to the database. The database is confirmed to be up and running. All configurations for the network ACLs, security groups, and route tables are still in their default states. What should a solutions architect recommend to fix the application?

## Options

**A.** Add an explicit rule to the private subnet's network ACL to allow traffic from the web tier's EC2 instances.

**B.** Add a route in the VPC route table to allow traffic between the web tier's EC2 instances and the database tier.

**C.** Deploy the web tier's EC2 instances and the database tier's RDS instance into two separate VPCs, and configure VPC peering.

**D.** Add an inbound rule to the security group of the database tier's RDS instance to allow traffic from the web tiers security group.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web tier (public subnets) → RDS MySQL (private subnets). Web can't connect to DB. Default configs (SG, NACL, route tables).
- **Existing Resources:** ASG in public subnets, RDS in private subnets.
- **Current Issue/Goal:** Fix connectivity from web tier to RDS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `default states` | Default SG: allows inbound only from same SG. RDS SG mặc định chỉ cho traffic từ chính nó. |
| `cannot connect to the database` | RDS security group chặn inbound từ web tier. |
| `inbound rule to the security group of the database` | Add rule: allow MySQL (3306) from web tier's SG. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Fix connectivity issue
- **Constraints:** Default configs, web → RDS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Default security group for RDS: chỉ allow inbound traffic from itself → web tier không thể connect.
- Add inbound rule to RDS security group: allow MySQL (port 3306) from web tier's security group.
- Không cần modify NACLs mặc định (default NACLs allow all traffic).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Default NACLs allow all traffic inbound/outbound → không cần explicit rules. Vấn đề là SG, không phải NACL.

**❌ Đáp án B:**
- Default route tables allow local VPC routing → không cần additional routes.

**❌ Đáp án C:**
- Separate VPCs + peering: quá phức tạp, không giải quyết vấn đề SG (peering cũng cần SG rules).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Default SG = only same SG. Web → RDS không connect → add inbound SG rule allow web SG. NACL default = allow all."*
