# Question #68 - Topic 1

A solutions architect is designing a new hybrid architecture to extend a company's on-premises infrastructure to AWS. The company requires a highly available connection with consistent low latency to an AWS Region. The company needs to minimize costs and is willing to accept slower traffic if the primary connection fails. What should the solutions architect do to meet these requirements?

## Options

**A.** Provision an AWS Direct Connect connection to a Region. Provision a VPN connection as a backup if the primary Direct Connect connection fails.

**B.** Provision a VPN tunnel connection to a Region for private connectivity. Provision a second VPN tunnel for private connectivity and as a backup if the primary VPN connection fails.

**C.** Provision an AWS Direct Connect connection to a Region. Provision a second Direct Connect connection to the same Region as a backup if the primary Direct Connect connection fails.

**D.** Provision an AWS Direct Connect connection to a Region. Use the Direct Connect failover attribute from the AWS CLI to automatically create a backup connection if the primary Direct Connect connection fails.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Hybrid architecture, on-prem → AWS.
- **Existing Resources:** On-prem infrastructure.
- **Current Issue/Goal:** HA connection, consistent low latency, minimize costs, accept slower backup.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `consistent low latency` | Cần **Direct Connect** (dedicated private connection) |
| `minimize costs` | Không muốn 2 DX connections (đắt) |
| `accept slower traffic if primary fails` | VPN over internet là backup rẻ hơn |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Hybrid networking + Cost optimization
- **Constraints:** HA, low latency primary, cost-effective backup

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Direct Connect** — consistent low latency, private connection.
- **VPN backup** — rẻ hơn DX thứ hai, dùng internet → slower nhưng chấp nhận được.
- Pattern chuẩn: DX primary + VPN backup = cost-effective HA.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- VPN không đảm bảo "consistent low latency" (đi qua internet).

**❌ Đáp án C:**
- 2 Direct Connect connections — đắt, không "minimize costs".

**❌ Đáp án D:**
- Không có "Direct Connect failover attribute" trong AWS CLI.
- Direct Connect không tự động tạo backup connection.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Direct Connect = consistent low latency. VPN = cheap backup. 2 DX = HA but expensive"*
