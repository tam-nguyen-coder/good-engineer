# Question #370 - Topic 1

A company runs a public three-tier web application in a VPC. The application runs on Amazon EC2 instances across multiple Availability Zones. The EC2 instances that run in private subnets need to communicate with a license server over the internet. The company needs a managed solution that minimizes operational maintenance. Which solution meets these requirements?

## Options

**A.** Provision a NAT instance in a public subnet. Modify each private subnet's route table with a default route that points to the NAT instance.

**B.** Provision a NAT instance in a private subnet. Modify each private subnet's route table with a default route that points to the NAT instance.

**C.** Provision a NAT gateway in a public subnet. Modify each private subnet's route table with a default route that points to the NAT gateway.

**D.** Provision a NAT gateway in a private subnet. Modify each private subnet's route table with a default route that points to the NAT gateway.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 in private subnets cần internet access (license server). Multi-AZ. Need managed solution, minimal maintenance.
- **Existing Resources:** VPC, private subnets with EC2 instances.
- **Current Issue/Goal:** Outbound internet access for private subnets.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `managed solution` | NAT Gateway (managed) > NAT Instance (self-managed EC2). |
| `minimizes operational maintenance` | NAT Gateway = managed service, không cần patch/manager. |
| `private subnets` | Route table default route → NAT Gateway in public subnet. |
| `public subnet` | NAT Gateway must be in public subnet (with Internet Gateway). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Managed solution, minimal maintenance
- **Constraints:** EC2 in private subnets need outbound internet

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- NAT Gateway: managed AWS service (highly available, auto-scaled, no maintenance).
- NAT Gateway phải được đặt trong public subnet (có route đến Internet Gateway).
- Route table private subnets: default route 0.0.0.0/0 → NAT Gateway.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- NAT Instance: self-managed EC2 → operational maintenance cao (patch, monitor, failover).

**❌ Đáp án B:**
- NAT Instance in private subnet: không thể access internet (không có route đến IGW).

**❌ Đáp án D:**
- NAT Gateway in private subnet: không thể access internet (NAT cần ở public subnet).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Managed outbound internet → NAT Gateway in public subnet. NAT Instance = self-managed (operational overhead)."*
