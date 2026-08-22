# Question #558 - Topic 1

A company has two VPCs that are located in the us-west-2 Region within the same AWS account. The company needs to allow network traffic between these VPCs. Approximately 500 GB of data transfer will occur between the VPCs each month. What is the MOST cost-effective solution to connect these VPCs?

## Options

**A.** Implement AWS Transit Gateway to connect the VPCs. Update the route tables of each VPC to use the transit gateway for inter-VPC communication.

**B.** Implement an AWS Site-to-Site VPN tunnel between the VPCs. Update the route tables of each VPC to use the VPN tunnel for inter-VPC communication.

**C.** Set up a VPC peering connection between the VPCs. Update the route tables of each VPC to use the VPC peering connection for inter-VPC communication.

**D.** Set up a 1 GB AWS Direct Connect connection between the VPCs. Update the route tables of each VPC to use the Direct Connect connection for inter-VPC communication.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Hai VPC trong cùng region (us-west-2), cùng AWS account. Cần kết nối giữa chúng với ~500 GB data transfer/tháng.
- **Existing Resources:** 2 VPCs trong cùng region, cùng account.
- **Current Issue/Goal:** Kết nối VPCs với chi phí thấp nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `two VPCs` | Chỉ 2 VPC → không cần transit gateway |
| `same AWS account / same Region` | Có thể dùng VPC peering |
| `MOST cost-effective` | Chi phí thấp nhất |
| `500 GB per month` | Lượng data không quá lớn |
| `VPC peering` | Free (chỉ tính data transfer nội vùng) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** 2 VPCs, cùng region, cùng account, 500GB/tháng

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- VPC peering là giải pháp đơn giản nhất và rẻ nhất: không tính phí hourly, chỉ tính phí data transfer.
- Data transfer giữa 2 VPCs trong cùng region qua VPC peering chỉ tính phí xử lý (thấp hơn nhiều so với NAT Gateway, Transit Gateway, v.v.).
- Không cần cấu hình phức tạp, chỉ cần tạo peering connection và update route tables.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (Transit Gateway):** Transit Gateway có phí hourly (~$0.05/hour) + phí xử lý data (~$0.02/GB). Khi chỉ có 2 VPCs, Transit Gateway đắt hơn VPC peering. Transit Gateway phù hợp khi có nhiều VPCs (hub-and-spoke).

**❌ Đáp án B (Site-to-Site VPN):** VPN có phí hourly (~$0.05/hour) và giới hạn bandwidth (< 1.25 Gbps). Phức tạp hơn VPC peering và đắt hơn. VPN dùng cho kết nối on-prem ↔ AWS.

**❌ Đáp án D (Direct Connect):** Direct Connect rất đắt (chi phí port hourly ~hàng trăm USD/tháng + data transfer). Dùng cho enterprise kết nối dedicated từ on-prem. Quá overkill cho 500 GB và chỉ 2 VPCs.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"2 VPCs same region → VPC peering (free hourly). 3+ VPCs → Transit Gateway (hub-and-spoke). Direct Connect = on-prem to AWS only."*
