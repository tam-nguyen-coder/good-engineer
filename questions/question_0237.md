# Question #237 - Topic 1

An application running on an Amazon EC2 instance in VPC-A needs to access files in another EC2 instance in VPC-B. Both VPCs are in separate AWS accounts. The network administrator needs to design a solution to configure secure access to EC2 instance in VPC-B from VPC-A. The connectivity should not have a single point of failure or bandwidth concerns. Which solution will meet these requirements?

## Options

**A.** Set up a VPC peering connection between VPC-A and VPC-B.

**B.** Set up VPC gateway endpoints for the EC2 instance running in VPC-B.

**C.** Attach a virtual private gateway to VPC-B and set up routing from VPC-A.

**D.** Create a private virtual interface (VIF) for the EC2 instance running in VPC-B and add appropriate routes from VPC-A.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 in VPC-A needs to access EC2 in VPC-B. Different AWS accounts. No SPOF, no bandwidth concerns.
- **Existing Resources:** VPC-A (account A), VPC-B (account B).
- **Current Issue/Goal:** Cross-account VPC connectivity.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `separate AWS accounts` | **Cross-account VPC peering** |
| `no single point of failure or bandwidth concerns` | VPC peering — không SPOF, không bandwidth limit |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / VPC
- **Constraints:** Cross-account, no SPOF, no bandwidth limits

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **VPC peering** — kết nối trực tiếp giữa 2 VPCs (cross-account supported).
- Không SPOF (không có intermediate device).
- Không bandwidth concerns (full bandwidth of instances).
- Hỗ trợ cross-Region và cross-account.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- VPC Gateway Endpoint — chỉ cho S3 và DynamoDB, không cho EC2.

**❌ Đáp án C:**
- Virtual private gateway — dùng cho VPN/Direct Connect, không phải VPC-to-VPC.

**❌ Đáp án D:**
- Private VIF — dùng cho Direct Connect, không phải VPC-to-VPC.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"VPC peering = cross-account VPC connectivity. Gateway endpoints = S3/DynamoDB only"*
