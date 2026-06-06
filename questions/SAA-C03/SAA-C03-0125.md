# Question #125 - Topic 1

A company runs its two-tier ecommerce website on AWS. The web tier consists of a load balancer that sends traffic to Amazon EC2 instances. The database tier uses an Amazon RDS DB instance. The EC2 instances and the RDS DB instance should not be exposed to the public internet. The EC2 instances require internet access to complete payment processing of orders through a third-party web service. The application must be highly available. Which combination of configuration options will meet these requirements? (Choose two.)

## Options

**A.** Use an Auto Scaling group to launch the EC2 instances in private subnets. Deploy an RDS Multi-AZ DB instance in private subnets.

**B.** Configure a VPC with two private subnets and two NAT gateways across two Availability Zones. Deploy an Application Load Balancer in the private subnets.

**C.** Use an Auto Scaling group to launch the EC2 instances in public subnets across two Availability Zones. Deploy an RDS Multi-AZ DB instance in private subnets.

**D.** Configure a VPC with two public subnets, two private subnets, and two NAT gateways across two Availability Zones. Deploy an Application Load Balancer in the public subnets.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Two-tier ecommerce: ALB → EC2 → RDS. EC2 + RDS không public. EC2 cần internet cho payment.
- **Existing Resources:** ALB, EC2, RDS.
- **Current Issue/Goal:** Highly available, EC2 + RDS private, EC2 outbound internet.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `should not be exposed to the public internet` | Private subnets |
| `require internet access` | NAT gateway |
| `highly available` | Multi-AZ |
| `Application Load Balancer` | Public subnets (internet-facing) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking + HA
- **Constraints:** Chọn 2 đáp án

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và D**

**Giải thích:**
- **A: EC2 + RDS private** — ASG launch EC2 in private subnets, RDS Multi-AZ in private subnets.
- **D: VPC architecture** — public subnets (cho ALB) + private subnets (cho EC2/RDS) + NAT gateways (outbound internet) + multi-AZ.
- ALB in public subnets nhận traffic từ internet → forward đến EC2 private subnets.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ALB cannot be deployed in private subnets (internet-facing ALB needs public subnets).

**❌ Đáp án C:**
- EC2 in public subnets → exposed to internet, không đáp ứng yêu cầu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ALB = public subnets. EC2 + RDS = private subnets. NAT gateway = outbound internet. Multi-AZ = HA"*
