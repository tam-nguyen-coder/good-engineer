# Question #55 - Topic 1

A solutions architect is developing a VPC architecture that includes multiple subnets. The architecture will host applications that use Amazon EC2 instances and Amazon RDS DB instances. The architecture consists of six subnets in two Availability Zones. Each Availability Zone includes a public subnet, a private subnet, and a dedicated subnet for databases. Only EC2 instances that run in the private subnets can have access to the RDS databases. Which solution will meet these requirements?

## Options

**A.** Create a new route table that excludes the route to the public subnets' CIDR blocks. Associate the route table with the database subnets.

**B.** Create a security group that denies inbound traffic from the security group that is assigned to instances in the public subnets. Attach the security group to the DB instances.

**C.** Create a security group that allows inbound traffic from the security group that is assigned to instances in the private subnets. Attach the security group to the DB instances.

**D.** Create a new peering connection between the public subnets and the private subnets. Create a different peering connection between the private subnets and the database subnets.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** VPC với 6 subnets / 2 AZs: public, private, database trong mỗi AZ.
- **Existing Resources:** EC2 instances (public & private), RDS instances (database subnets).
- **Current Issue/Goal:** Chỉ EC2 trong private subnets mới access được RDS databases.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Only EC2 instances in private subnets can have access` | Cần security group allow từ private subnet resources |
| `public subnet / private subnet / database subnet` | Standard 3-tier architecture |
| `security group` | Stateful firewall, có thể reference SG khác |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Network security
- **Constraints:** Chỉ private EC2 → RDS, không public EC2 → RDS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Security group referencing** — tạo SG cho private EC2, sau đó tạo SG cho RDS với inbound rule allow traffic từ private EC2 SG.
- Đây là pattern chuẩn cho 3-tier architecture trên AWS.
- Security group là stateful — response traffic tự động được allow.
- Không cần quan tâm đến CIDR/IP — AWS tự quản lý.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Route table điều khiển routing (đường đi của traffic), không phải access control.
- Route table không thể deny/allow traffic đến database.

**❌ Đáp án B:**
- Security groups hỗ trợ **allow rules**, không có **deny rules**.
- Không thể tạo security group với "deny inbound traffic".

**❌ Đáp án D:**
- VPC peering dùng để kết nối **giữa các VPC**, không phải giữa các subnet trong cùng một VPC.
- Tất cả subnets trong cùng VPC đã có thể communicate với nhau qua local route mặc định.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Security groups = allow rules only (no deny). SG chaining: DB SG allow inbound from App SG"*
