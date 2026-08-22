# Question #101 - Topic 1

A solutions architect is designing a VPC with public and private subnets. The VPC and subnets use IPv4 CIDR blocks. There is one public subnet and one private subnet in each of three Availability Zones (AZs) for high availability. An internet gateway is used to provide internet access for the public subnets. The private subnets require access to the internet to allow Amazon EC2 instances to download software updates. What should the solutions architect do to enable Internet access for the private subnets?

## Options

**A.** Create three NAT gateways, one for each public subnet in each AZ. Create a private route table for each AZ that forwards non-VPC traffic to the NAT gateway in its AZ.

**B.** Create three NAT instances, one for each private subnet in each AZ. Create a private route table for each AZ that forwards non-VPC traffic to the NAT instance in its AZ.

**C.** Create a second internet gateway on one of the private subnets. Update the route table for the private subnets that forward non-VPC traffic to the private internet gateway.

**D.** Create an egress-only internet gateway on one of the public subnets. Update the route table for the private subnets that forward non-VPC traffic to the egress-only Internet gateway.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** VPC public/private subnets across 3 AZs. Private subnets cần internet access (software updates).
- **Existing Resources:** VPC, IGW, public/private subnets.
- **Current Issue/Goal:** Enable internet for private subnets.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `three Availability Zones` | Cần HA → **NAT gateway per AZ** |
| `private subnets require access to the internet` | **NAT gateway** in public subnet |
| `IPv4 CIDR blocks` | NAT gateway (egress-only IGW là cho IPv6) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking
- **Constraints:** 3 AZs, IPv4, HA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **NAT gateway** trong public subnet — cho phép private subnet outbound internet.
- **3 NAT gateways** (1 per AZ) — đảm bảo HA: nếu 1 AZ fails, các AZ khác vẫn hoạt động.
- Route table riêng cho mỗi AZ, trỏ 0.0.0.0/0 đến NAT gateway trong cùng AZ.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **NAT instances** — phải tự quản lý (patching, HA), không managed, không tối ưu.

**❌ Đáp án C:**
- Một VPC chỉ có **1 internet gateway**. Không thể tạo IGW riêng cho private subnet.

**❌ Đáp án D:**
- **Egress-only internet gateway** chỉ dùng cho **IPv6**, không phải IPv4.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"NAT gateway = IPv4 outbound. Egress-only IGW = IPv6. 1 NAT per AZ = HA"*
