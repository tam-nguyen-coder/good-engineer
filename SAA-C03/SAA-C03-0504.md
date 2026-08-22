# Question #504 - Topic 1

A company needs to connect several VPCs in the us-east-1 Region that span hundreds of AWS accounts. The company's networking team has its own AWS account to manage the cloud network. What is the MOST operationally efficient solution to connect the VPCs?

## Options

**A.** Set up VPC peering connections between each VPC. Update each associated subnet's route table

**B.** Configure a NAT gateway and an internet gateway in each VPC to connect each VPC through the internet

**C.** Create an AWS Transit Gateway in the networking team's AWS account. Configure static routes from each VPC.

**D.** Deploy VPN gateways in each VPC. Create a transit VPC in the networking team's AWS account to connect to each VPC.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần kết nối nhiều VPC (hundreds) thuộc nhiều AWS accounts trong cùng region us-east-1. Networking team có account riêng để quản lý network.
- **Existing Resources:** Hundreds of VPCs across hundreds of accounts.
- **Current Issue/Goal:** Kết nối tất cả VPCs với nhau, operational efficiency cao nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `hundreds of accounts` | Số lượng lớn → cần hub-and-spoke, không thể mesh. |
| `connect several VPCs` | Kết nối VPC-to-VPC. |
| `MOST operationally efficient` | Giải pháp centralized managed. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operationally efficient
- **Constraints:** Hundreds of VPCs across hundreds of accounts, same region

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS Transit Gateway (TGW) là hub-and-spoke solution: 1 TGW ở networking account kết nối với tất cả VPCs.
- Quản lý centralized: chỉ cần attach VPC vào TGW và update route tables.
- Với hundreds VPCs, TGW giảm operational overhead cực kỳ lớn so với VPC peering (mesh O(n²)).
- Hỗ trợ cross-account attachment: VPC ở account khác có thể attach vào TGW của networking account.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- VPC peering không scale: với n VPCs cần n*(n-1)/2 peering connections. Với hundreds VPCs → không khả thi.
- Mỗi peering là 1-1, không hỗ trợ transitive routing.

**❌ Đáp án B:**
- NAT Gateway + IGW qua internet: không an toàn, traffic đi qua internet.
- Không phải giải pháp VPC connectivity chuẩn, không tối ưu.

**❌ Đáp án D:**
- Transit VPC (VPN-based) là giải pháp cũ trước khi có TGW. Phức tạp hơn, cần tự quản lý VPN endpoints và EC2 instances cho routing.
- TGW đơn giản hơn nhiều, là sự thay thế hiện đại cho transit VPC.

## 6. MẺO GHI NHỚ (Memory Hook)
🧠 *"Nhiều VPC → Transit Gateway (hub-and-spoke). VPC peering không scale (mesh O(n²))."*
