# Question #448 - Topic 1

A company has two VPCs named Management and Production. The Management VPC uses VPNs through a customer gateway to connect to a single device in the data center. The Production VPC uses a virtual private gateway with two attached AWS Direct Connect connections. The Management and Production VPCs both use a single VPC peering connection to allow communication between the applications. What should a solutions architect do to mitigate any single point of failure in this architecture?

## Options

**A.** Add a set of VPNs between the Management and Production VPCs.

**B.** Add a second virtual private gateway and attach it to the Management VPC.

**C.** Add a second set of VPNs to the Management VPC from a second customer gateway device.

**D.** Add a second VPC peering connection between the Management VPC and the Production VPC.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Mgmt VPC: VPN via single CGW to DC. Prod VPC: 2 Direct Connect (redundant). VPC peering between them.
- **Existing Resources:** Mgmt VPC (VPN, 1 CGW), Prod VPC (2 DC), VPC peering.
- **Current Issue/Goal:** Mitigate single point of failure.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `single point of failure` | Single CGW cho Management VPC VPN. |
| `customer gateway` | On-prem device. One device = SPOF. |
| `second customer gateway` | Redundant on-prem device → HA VPN. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability / Networking
- **Constraints:** Mitigate SPOF in hybrid connectivity

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Management VPC: single CGW (on-prem device) là SPOF.
- Add second VPN từ second CGW → redundant connection.
- Nếu một CGW fails, VPN từ CGW kia vẫn hoạt động.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- VPN giữa Mgmt và Prod VPCs: VPC peering đã connect chúng. Additional VPN không fix SPOF của CGW.

**❌ Đáp án B:**
- Second VGW: VGW dùng cho Direct Connect, không phải VPN trên Management VPC.

**❌ Đáp án D:**
- Second VPC peering: VPC peering không phải SPOF (no bandwidth limit, no device). Thêm peering không giúp gì.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Single CGW = SPOF. Fix = second VPN + second CGW (redundant on-prem)."*