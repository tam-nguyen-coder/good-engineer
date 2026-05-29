# Question #474 - Topic 1

A company has multiple VPCs across AWS Regions to support and run workloads that are isolated from workloads in other Regions. Because of a recent application launch requirement, the company's VPCs must communicate with all other VPCs across all Regions. Which solution will meet these requirements with the LEAST amount of administrative effort?

## Options

**A.** Use VPC peering to manage VPC communication in a single Region. Use VPC peering across Regions to manage VPC communications.

**B.** Use AWS Direct Connect gateways across all Regions to connect VPCs across regions and manage VPC communications.

**C.** Use AWS Transit Gateway to manage VPC communication in a single Region and Transit Gateway peering across Regions to manage VPC communications.

**D.** Use AWS PrivateLink across all Regions to connect VPCs across Regions and manage VPC communications

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multiple VPCs across multiple Regions, cần all-to-all communication.
- **Existing Resources:** Multiple VPCs.
- **Current Issue/Goal:** Least administrative effort để kết nối tất cả VPCs với nhau.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `multiple VPCs across AWS Regions` | Nhiều VPC ở nhiều Region. |
| `communicate with all other VPCs across all Regions` | All-to-all mesh. |
| `LEAST amount of administrative effort` | Cần giải pháp centralized, không peer từng cặp. |
| `Transit Gateway` | Hub-and-spoke: quản lý tập trung, dễ mở rộng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least administrative effort
- **Constraints:** Multiple regions, multiple VPCs, all-to-all

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Transit Gateway: hub centralized, attach tất cả VPCs vào TG → single point of management.
- Transit Gateway Peering: kết nối TG giữa các Regions.
- All-to-all: chỉ cần 1 TG mỗi Region + TG peering, không cần N*(N-1)/2 peer connections.
- Admin effort thấp nhất: quản lý tập trung, tự động route.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- VPC peering: cần peer từng cặp VPC (N*(N-1)/2 connections). Với nhiều VPC và Region, admin effort rất cao.
- Không hỗ trợ transitive routing.

**❌ Đáp án B:**
- Direct Connect gateway: dùng kết nối on-premises với VPCs qua DX, không phải để kết nối VPC-to-VPC.

**❌ Đáp án D:**
- PrivateLink: dùng để expose service từ 1 VPC sang VPC khác (service consumer/provider model), không hỗ trợ all-to-all communication.
- Không thiết kế cho full mesh VPC connectivity.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Nhiều VPC nhiều Region → Transit Gateway + Peering. VPC peering = mỗi cặp 1 connection (admin nightmare)."*
