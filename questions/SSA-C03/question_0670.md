# Question #670 - Topic 1

A company performs tests on an application that uses an Amazon DynamoDB table. The tests run for 4 hours once a week. The company knows how many read and write operations the application performs to the table each second during the tests. The company does not currently use DynamoDB for any other use case. A solutions architect needs to optimize the costs for the table. Which solution will meet these requirements?

## Options

**A.** Choose on-demand mode. Update the read and write capacity units appropriately.

**B.** Choose provisioned mode. Update the read and write capacity units appropriately.

**C.** Purchase DynamoDB reserved capacity for a 1-year term.

**D.** Purchase DynamoDB reserved capacity for a 3-year term.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DynamoDB table used for testing 4 hours/week. Known read/write operations per second. Optimize costs.
- **Existing Resources:** DynamoDB table.
- **Current Issue/Goal:** Cost optimization for predictable, low-usage workload.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `once a week` | Usage only 4 hours per week (low utilization). |
| `known how many read and write operations` | Predictable workload → provisioned mode. |
| `optimize the costs` | Provisioned mode rẻ hơn on-demand cho workload biết trước. |
| `on-demand mode` | Pay-per-request, phù hợp unpredictable traffic, đắt hơn khi biết trước. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Optimize costs
- **Constraints:** Known capacity, 4h/week, no other usage

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Provisioned mode: trả tiền cho RCU/WCU provisioned, thấp hơn on-demand khi workload predictable.
- Biết trước capacity cần → provision đúng lượng, tránh overpay.
- Không cần reserved capacity (chỉ dùng 4h/tuần → reserved lãng phí).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- On-demand mode tính per-request, đắt hơn provisioned cho workload predictable.
- "Update read/write capacity units" không áp dụng cho on-demand mode.

**❌ Đáp án C:**
- Reserved capacity cam kết 1 năm → lãng phí (chỉ dùng 4h/tuần).

**❌ Đáp án D:**
- Reserved capacity 3 năm → càng lãng phí hơn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Predictable workload → Provisioned mode (cheaper). On-demand = unpredictable. Reserved = heavy usage."*
