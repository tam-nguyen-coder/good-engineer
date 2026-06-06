# Question #439 - Topic 1

A solutions architect configured a VPC that has a small range of IP addresses. The number of Amazon EC2 instances that are in the VPC is increasing, and there is an insufficient number of IP addresses for future workloads. Which solution resolves this issue with the LEAST operational overhead?

## Options

**A.** Add an additional IPv4 CIDR block to increase the number of IP addresses and create additional subnets in the VPC. Create new resources in the new subnets by using the new CIDR.

**B.** Create a second VPC with additional subnets. Use a peering connection to connect the second VPC with the first VPC Update the routes and create new resources in the subnets of the second VPC.

**C.** Use AWS Transit Gateway to add a transit gateway and connect a second VPC with the first VPUpdate the routes of the transit gateway and VPCs. Create new resources in the subnets of the second VPC.

**D.** Create a second VPC. Create a Site-to-Site VPN connection between the first VPC and the second VPC by using a VPN-hosted solution on Amazon EC2 and a virtual private gateway. Update the route between VPCs to the traffic through the VPN. Create new resources in the subnets of the second VPC.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** VPC small IP range, running out of IPs for EC2 instances.
- **Existing Resources:** VPC with small CIDR block.
- **Current Issue/Goal:** More IP addresses. Least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `VPC` | Can add secondary CIDR blocks. |
| `additional IPv4 CIDR block` | Extend VPC IP range without new VPC. |
| `least operational overhead` | Add CIDR to existing VPC (no peering/transit needed). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking
- **Constraints:** More IPs, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- VPC hỗ trợ secondary CIDR blocks (primary + secondary).
- Thêm CIDR block vào existing VPC → tạo subnets mới → deploy resources.
- Không cần VPC peering, Transit Gateway, VPN → operational overhead thấp nhất.
- Lưu ý: CIDR không được overlap với CIDR hiện tại.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Second VPC + peering: cần tạo VPC mới, peering connection, update routes → overhead cao hơn.

**❌ Đáp án C:**
- Transit Gateway: thiết kế cho hub-and-spoke với nhiều VPCs, overkill cho 2 VPCs.

**❌ Đáp án D:**
- Site-to-Site VPN via EC2: nhất là tự host VPN → overhead rất cao. Không recommended.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Need more IPs in VPC → add secondary CIDR block. Peering/Transit = more overhead."*