# Question #374 - Topic 1

A company is running several business applications in three separate VPCs within the us-east-1 Region. The applications must be able to communicate between VPCs. The applications also must be able to consistently send hundreds of gigabytes of data each day to a latency- sensitive application that runs in a single on-premises data center. A solutions architect needs to design a network connectivity solution that maximizes cost-effectiveness. Which solution meets these requirements?

## Options

**A.** Configure three AWS Site-to-Site VPN connections from the data center to AWS. Establish connectivity by configuring one VPN connection for each VPC.

**B.** Launch a third-party virtual network appliance in each VPC. Establish an IPsec VPN tunnel between the data center and each virtual appliance.

**C.** Set up three AWS Direct Connect connections from the data center to a Direct Connect gateway in us-east-1. Establish connectivity by configuring each VPC to use one of the Direct Connect connections.

**D.** Set up one AWS Direct Connect connection from the data center to AWS. Create a transit gateway, and attach each VPC to the transit gateway. Establish connectivity between the Direct Connect connection and the transit gateway.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 3 VPCs need cross-communication + hundreds GB/day to on-premises (latency-sensitive). Most cost-effective.
- **Existing Resources:** 3 VPCs in us-east-1, on-premises data center.
- **Current Issue/Goal:** VPC-to-VPC + VPC-to-on-premises connectivity.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `hundreds of gigabytes each day` | Large data volume → Direct Connect (consistent, reliable, lower cost than VPN for large data). |
| `latency-sensitive` | Direct Connect (private, consistent) > VPN (internet-based). |
| `transit gateway` | Single gateway kết nối nhiều VPCs + Direct Connect. |
| `cost-effectiveness` | 1 Direct Connect + Transit Gateway > 3 Direct Connect/VPN connections. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Maximize cost-effectiveness
- **Constraints:** 3 VPCs inter-connect + on-premises, hundreds GB/day, latency-sensitive

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Transit Gateway: kết nối 3 VPCs với nhau (routing) và với Direct Connect.
- 1 Direct Connect connection: cost-effective hơn 3 connections, vẫn đáp ứng hundreds GB/day với latency thấp.
- Single connection + Transit Gateway = centralized, cost-effective.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- 3 VPN connections: cost cao hơn 1 Direct Connect (3 connections), VPN có latency và consistency kém hơn Direct Connect.

**❌ Đáp án B:**
- Third-party appliances: cost cao, operational overhead, không cost-effective.

**❌ Đáp án C:**
- 3 Direct Connect connections: đắt hơn 1 connection + Transit Gateway.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-VPC + on-premises large data → Transit Gateway + 1 Direct Connect (cheapest, lowest latency)."*
