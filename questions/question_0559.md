# Question #559 - Topic 1

A company hosts multiple applications on AWS for different product lines. The applications use different compute resources, including Amazon EC2 instances and Application Load Balancers. The applications run in different AWS accounts under the same organization in AWS Organizations across multiple AWS Regions. Teams for each product line have tagged each compute resource in the individual accounts. The company wants more details about the cost for each product line from the consolidated billing feature in Organizations. Which combination of steps will meet these requirements? (Choose two.)

## Options

**A.** Select a specific AWS generated tag in the AWS Billing console.

**B.** Select a specific user-defined tag in the AWS Billing console.

**C.** Select a specific user-defined tag in the AWS Resource Groups console.

**D.** Activate the selected tag from each AWS account.

**E.** Activate the selected tag from the Organizations management account.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Nhiều accounts trong AWS Organizations, mỗi account có resources đã được tag. Cần xem chi phí theo product line dùng consolidated billing.
- **Existing Resources:** AWS Organizations, multiple accounts, tagged resources (EC2, ALB).
- **Current Issue/Goal:** Kích hoạt cost tracking theo user-defined tags trong consolidated billing.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `tagged each compute resource` | User-defined tags (ví dụ: ProductLine) |
| `consolidated billing` | Hóa đơn tập trung trong Organizations |
| `more details about the cost` | Cost allocation tags |
| `user-defined tag` | Tag do user tạo (cost allocation tags) |
| `Organizations management account` | Nơi kích hoạt cost allocation tags |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Multi-select (2 answers)
- **Constraints:** Track cost by product line using existing tags, consolidated billing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B, E**

**Giải thích:**
- **B:** Trong AWS Billing console, chọn "user-defined tag" để làm cost allocation tag. AWS generated tags (như aws:createdBy) không phù hợp vì tags do teams tự định nghĩa.
- **E:** Kích hoạt cost allocation tags từ Organizations management account (payer account). Việc này enable tags cho tất cả accounts trong organization.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (AWS generated tag):** AWS generated tags (có prefix aws:) không phải tags do teams tự tag. Đề đã nói "tagged each compute resource" → user-defined tags.

**❌ Đáp án C (Resource Groups console):** AWS Resource Groups console không liên quan đến cost allocation tags. Cost allocation tags được quản lý trong Billing console.

**❌ Đáp án D (Activate tag từ mỗi account):** Trong Organizations với consolidated billing, cost allocation tags phải được kích hoạt từ management account (payer), không phải từ từng member account.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cost allocation tags: kích hoạt ở management account (payer) trong Billing console. Chọn user-defined tags. Not in Resource Groups."*
