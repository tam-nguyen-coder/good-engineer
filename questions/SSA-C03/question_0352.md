# Question #352 - Topic 1

A company is designing the network for an online multi-player game. The game uses the UDP networking protocol and will be deployed in eight AWS Regions. The network architecture needs to minimize latency and packet loss to give end users a high-quality gaming experience. Which solution will meet these requirements?

## Options

**A.** Setup a transit gateway in each Region. Create inter-Region peering attachments between each transit gateway.

**B.** Set up AWS Global Accelerator with UDP listeners and endpoint groups in each Region.

**C.** Set up Amazon CloudFront with UDP turned on. Configure an origin in each Region.

**D.** Set up a VPC peering mesh between each Region. Turn on UDP for each VPC.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Online multiplayer game, UDP protocol, 8 Regions. Minimize latency and packet loss.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Global low-latency UDP routing for gaming.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `UDP` | Global Accelerator supports UDP (also TCP). CloudFront does NOT support UDP. |
| `minimize latency and packet loss` | Global Accelerator dùng AWS global network, Anycast IP → user route đến nearest edge. |
| `Global Accelerator` | Improve performance by routing traffic to nearest healthy endpoint qua AWS backbone. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** UDP, 8 Regions, low latency, low packet loss

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS Global Accelerator: support UDP, dùng Anycast IP → user traffic đi đến edge location gần nhất, qua AWS backbone đến Region gần user.
- TCP optimization và packet loss reduction nhờ AWS managed network.
- Endpoint groups in each Region.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Transit gateway peering kết nối VPCs cross-Region, không tối ưu end-user latency (không có edge locations).

**❌ Đáp án C:**
- CloudFront không support UDP (chỉ HTTP/HTTPS và WebSocket).

**❌ Đáp án D:**
- VPC peering mesh cross-Region: kết nối VPCs, không tối ưu end-user latency.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"UDP game + global low latency → Global Accelerator (Anycast, AWS backbone). CloudFront = không UDP."*
