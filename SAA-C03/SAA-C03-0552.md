# Question #552 - Topic 1

A company needs to optimize the cost of its Amazon EC2 instances. The company also needs to change the type and family of its EC2 instances every 2-3 months. What should the company do to meet these requirements?

## Options

**A.** Purchase Partial Upfront Reserved Instances for a 3-year term.

**B.** Purchase a No Upfront Compute Savings Plan for a 1-year term.

**C.** Purchase All Upfront Reserved Instances for a 1-year term.

**D.** Purchase an All Upfront EC2 Instance Savings Plan for a 1-year term.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty muốn tối ưu chi phí EC2 instances và cần thay đổi type/family mỗi 2-3 tháng.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Tối ưu cost với khả năng linh hoạt thay đổi instance type/family thường xuyên.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `change the type and family` | Cần linh hoạt về instance type và family |
| `every 2-3 months` | Thay đổi thường xuyên |
| `optimize the cost` | Tiết kiệm chi phí |
| `Compute Savings Plan` | Linh hoạt theo instance type, family, OS, region (với 1-year/3-year) |
| `EC2 Instance Savings Plan` | Chỉ linh hoạt trong cùng instance family và region |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Cần thay đổi instance type và family thường xuyên

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Compute Savings Plan linh hoạt nhất: áp dụng cho bất kỳ EC2 instance nào (bất kỳ family, type, size, OS, region – trong khu vực áp dụng), cũng như Fargate và Lambda.
- Giảm giá đến 66% so với On-Demand, tương đương Reserved Instances.
- No Upfront: không cần trả trước, phù hợp khi thay đổi instance thường xuyên, không muốn ràng buộc tài chính.
- 1-year term: phù hợp với nhu cầu hiện tại (có thể thay đổi sau 1 năm).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (Partial Upfront RI, 3-year):** Reserved Instances gắn với instance type và family cụ thể trong AZ/region. Không thể thay đổi family. 3-year term quá dài và không linh hoạt.

**❌ Đáp án C (All Upfront RI, 1-year):** Reserved Instances gắn với instance type cụ thể. Không thể đổi family khi cần. All Upfront cũng rủi ro tài chính nếu không dùng hết.

**❌ Đáp án D (EC2 Instance Savings Plan):** EC2 Instance Savings Plan chỉ linh hoạt trong cùng instance family (ví dụ: chỉ trong family M5), không thể đổi sang family khác (ví dụ: từ M5 sang C5). Yêu cầu của đề là thay đổi cả family.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Compute Savings Plan = flexible across families, OS, regions. EC2 Instance Savings Plan = same family only. RIs = fixed type/family."*
