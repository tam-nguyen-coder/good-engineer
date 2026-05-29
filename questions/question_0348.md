# Question #348 - Topic 1

A company collects data from a large number of participants who use wearable devices. The company stores the data in an Amazon DynamoDB table and uses applications to analyze the data. The data workload is constant and predictable. The company wants to stay at or below its forecasted budget for DynamoDB. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Use provisioned mode and DynamoDB Standard-Infrequent Access (DynamoDB Standard-IA). Reserve capacity for the forecasted workload.

**B.** Use provisioned mode. Specify the read capacity units (RCUs) and write capacity units (WCUs).

**C.** Use on-demand mode. Set the read capacity units (RCUs) and write capacity units (WCUs) high enough to accommodate changes in the workload.

**D.** Use on-demand mode. Specify the read capacity units (RCUs) and write capacity units (WCUs) with reserved capacity.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DynamoDB table, wearable device data. Workload constant and predictable. Cần stay within budget.
- **Existing Resources:** DynamoDB table.
- **Current Issue/Goal:** Most cost-effective DynamoDB configuration.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `constant and predictable` | Provisioned mode rẻ hơn on-demand cho workload predictable. |
| `DynamoDB Standard-IA` | Table class: lower storage cost for infrequently accessed data. |
| `Reserve capacity` | DynamoDB Reserved Capacity: commit to $ spend → discount. |
| `most cost-effectively` | Provisioned + Standard-IA + Reserved Capacity = cheapest. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Constant/predictable workload, within budget

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Provisioned mode: cheaper than on-demand for predictable workloads (you control RCU/WCU).
- DynamoDB Standard-IA: giảm storage cost (data wearable devices ít được access sau khi ingest).
- Reserved capacity (DynamoDB Reserved Capacity): commit to 1-year or 3-year spend → giảm thêm cost.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Provisioned + RCU/WCU specification: cost-effective nhưng không tối ưu bằng Standard-IA + Reserved Capacity.

**❌ Đáp án C:**
- On-demand mode: đắt hơn provisioned cho predictable workload. "Set RCU/WCU" không hợp lệ trong on-demand mode.

**❌ Đáp án D:**
- On-demand + reserved capacity: không có DynamoDB Reserved Capacity cho on-demand mode.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Predictable workload → provisioned + Standard-IA + Reserved Capacity (cheapest). On-demand = đắt cho predictable."*
