# Question #135 - Topic 1

A company runs workloads on AWS. The company needs to connect to a service from an external provider. The service is hosted in the provider's VPC. According to the company’s security team, the connectivity must be private and must be restricted to the target service. The connection must be initiated only from the company’s VPC. Which solution will mast these requirements?

## Options

**A.** Create a VPC peering connection between the company's VPC and the provider's VPC. Update the route table to connect to the target service.

**B.** Ask the provider to create a virtual private gateway in its VPC. Use AWS PrivateLink to connect to the target service.

**C.** Create a NAT gateway in a public subnet of the company’s VPUpdate the route table to connect to the target service.

**D.** Ask the provider to create a VPC endpoint for the target service. Use AWS PrivateLink to connect to the target service.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Kết nối private đến service của provider trong VPC của họ. Restricted to target service only.
- **Existing Resources:** Company VPC.
- **Current Issue/Goal:** Private kết nối, chỉ đến target service, initiated từ company VPC.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `private` | Không qua internet |
| `restricted to the target service` | Không expose entire VPC |
| `initiated only from the company's VPC` | **AWS PrivateLink** (VPC endpoint) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / Security
- **Constraints:** Private, service-specific, single direction

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **AWS PrivateLink** — kết nối private giữa VPCs thông qua VPC endpoints.
- **Provider tạo VPC endpoint** (AWS NLB + PrivateLink) — company tạo VPC endpoint trong VPC của mình.
- Chỉ access target service, không phải entire provider VPC.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- VPC peering — kết nối entire VPCs, không restricted to one service. Security team không muốn điều này.

**❌ Đáp án B:**
- Virtual private gateway dùng cho VPN/Direct Connect, không phải PrivateLink.

**❌ Đáp án C:**
- NAT gateway — traffic qua internet, không private.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"PrivateLink = kết nối private đến specific service. VPC peering = entire VPC. NAT = internet"*
