# Question #298 - Topic 1

A company is running a critical business application on Amazon EC2 instances behind an Application Load Balancer. The EC2 instances run in an Auto Scaling group and access an Amazon RDS DB instance. The design did not pass an operational review because the EC2 instances and the DB instance are all located in a single Availability Zone. A solutions architect must update the design to use a second Availability Zone. Which solution will make the application highly available?

## Options

**A.** Provision a subnet in each Availability Zone. Configure the Auto Scaling group to distribute the EC2 instances across both Availability Zones. Configure the DB instance with connections to each network.

**B.** Provision two subnets that extend across both Availability Zones. Configure the Auto Scaling group to distribute the EC2 instances across both Availability Zones. Configure the DB instance with connections to each network.

**C.** Provision a subnet in each Availability Zone. Configure the Auto Scaling group to distribute the EC2 instances across both Availability Zones. Configure the DB instance for Multi-AZ deployment.

**D.** Provision a subnet that extends across both Availability Zones. Configure the Auto Scaling group to distribute the EC2 instances across both Availability Zones. Configure the DB instance for Multi-AZ deployment.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Single AZ → cần Multi-AZ HA. EC2 + RDS đều trong 1 AZ.
- **Existing Resources:** ALB, EC2 Auto Scaling group, RDS DB instance.
- **Current Issue/Goal:** Make application highly available với 2 AZs.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highly available` | Cần chịu được failure của 1 AZ. |
| `second Availability Zone` | Thêm AZ mới để đạt HA. |
| `Multi-AZ deployment` | RDS Multi-AZ tạo standby instance ở AZ khác, auto failover. |
| `subnet in each Availability Zone` | Mỗi AZ có subnet riêng (subnet không thể extend across AZs). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution makes application highly available
- **Constraints:** Multi-AZ, EC2 + RDS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Subnet riêng trong mỗi AZ (subnets không thể extend across AZs).
- Auto Scaling group distribute instances across both AZs (HA cho compute layer).
- RDS Multi-AZ tạo standby ở AZ khác, tự động failover nếu primary fails (HA cho database layer).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- "Configure the DB instance with connections to each network" → RDS single-AZ không thể kết nối tới 2 networks để đạt HA. Cần Multi-AZ.

**❌ Đáp án B:**
- Subnet không thể extend across Availability Zones (mỗi subnet thuộc đúng 1 AZ).

**❌ Đáp án D:**
- Subnet không thể extend across Availability Zones.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"HA cho EC2 → ASG across AZs. HA cho RDS → Multi-AZ. Mỗi AZ có subnet riêng."*
