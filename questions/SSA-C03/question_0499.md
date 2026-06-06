# Question #499 - Topic 1

A company needs to minimize the cost of its 1 Gbps AWS Direct Connect connection. The company's average connection utilization is less than 10%. A solutions architect must recommend a solution that will reduce the cost without compromising security. Which solution will meet these requirements?

## Options

**A.** Set up a new 1 Gbps Direct Connect connection. Share the connection with another AWS account.

**B.** Set up a new 200 Mbps Direct Connect connection in the AWS Management Console.

**C.** Contact an AWS Direct Connect Partner to order a 1 Gbps connection. Share the connection with another AWS account.

**D.** Contact an AWS Direct Connect Partner to order a 200 Mbps hosted connection for an existing AWS account.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Company có 1 Gbps Direct Connect nhưng utilization <10%. Cần giảm cost. Không compromise security.
- **Existing Resources:** 1 Gbps Direct Connect connection.
- **Current Issue/Goal:** Giảm cost bằng cách downgrade bandwidth hoặc share.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `average connection utilization is less than 10%` | Dư thừa bandwidth → có thể downgrade. |
| `1 Gbps` | Direct Connect port-hour cost cao. |
| `reduce the cost without compromising security` | Giảm bandwidth hoặc tìm giải pháp rẻ hơn. |
| `Direct Connect Partner` | Sub-1Gbps connections chỉ có thể order qua Partner (hosted connection). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Không compromise security.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Direct Connect speeds dưới 1 Gbps (50 Mbps, 100 Mbps, 200 Mbps, v.v.) chỉ có sẵn qua **AWS Direct Connect Partners** dưới dạng **hosted connections**.
- 200 Mbps đủ cho utilization <10% của 1 Gbps (tức <100 Mbps).
- **Hosted connection** từ Partner thường rẻ hơn dedicated 1 Gbps connection.
- Security không bị ảnh hưởng (vẫn là private connection).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Share 1 Gbps với account khác: vẫn trả tiền cho 1 Gbps port. Chia sẻ cost nhưng không tối ưu.

**❌ Đáp án B:**
- 200 Mbps trong AWS Console: **Không thể**. AWS Console chỉ hỗ trợ dedicated connections với speeds 1 Gbps và 10 Gbps. Sub-1Gbps phải qua Partner.

**❌ Đáp án C:**
- Partner order 1 Gbps và share: vẫn là 1 Gbps, không giảm được cost đáng kể.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Sub-1Gbps Direct Connect → chỉ qua Partner (hosted). Console chỉ có 1Gbps/10Gbps dedicated."*
