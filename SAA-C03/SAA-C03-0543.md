# Question #543 - Topic 1

A company runs Amazon EC2 instances in multiple AWS accounts that are individually bled. The company recently purchased a Savings Pian. Because of changes in the company's business requirements, the company has decommissioned a large number of EC2 instances. The company wants to use its Savings Plan discounts on its other AWS accounts. Which combination of steps will meet these requirements? (Choose two.)

## Options

**A.** From the AWS Account Management Console of the management account, turn on discount sharing from the billing preferences section.

**B.** From the AWS Account Management Console of the account that purchased the existing Savings Plan, turn on discount sharing from the billing preferences section. Include all accounts.

**C.** From the AWS Organizations management account, use AWS Resource Access Manager (AWS RAM) to share the Savings Plan with other accounts.

**D.** Create an organization in AWS Organizations in a new payer account. Invite the other AWS accounts to join the organization from the management account.

**E.** Create an organization in AWS Organizations in the existing AWS account with the existing EC2 instances and Savings Plan. Invite the other AWS accounts to join the organization from the management account.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty có nhiều EC2 instances trong nhiều AWS accounts riêng lẻ. Đã mua Savings Plan nhưng hiện đã decommission nhiều instances. Muốn dùng Savings Plan discounts cho các account khác.
- **Existing Resources:** Savings Plan đã mua, nhiều AWS accounts riêng lẻ.
- **Current Issue/Goal:** Chia sẻ discount của Savings Plan sang các account khác để tận dụng dung lượng đã mua.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `individually billed` | Các account đang thanh toán riêng lẻ |
| `Savings Plan` | Gói tiết kiệm của AWS, có thể chia sẻ giữa các account |
| `discount sharing` | Cần bật tính năng chia sẻ discount |
| `decommissioned` | Không còn dùng hết dung lượng đã mua |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Multi-select (2 answers)
- **Constraints:** Tận dụng Savings Plan discount giữa các account, sử dụng tài nguyên có sẵn

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B, E**

**Giải thích:**
- **B:** Từ account đã mua Savings Plan, vào Account Management Console → billing preferences → bật discount sharing. Đây là nơi quản lý việc chia sẻ discount.
- **E:** Cần tạo AWS Organization từ account hiện tại (account đã mua Savings Plan và có EC2 instances), sau đó mời các account khác tham gia. Discount sharing hoạt động trong cùng một organization.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (Management account billing preferences):** Management account không phải là account đã mua Savings Plan. Discount sharing phải được bật từ chính account đã mua Savings Plan.

**❌ Đáp án C (AWS RAM):** AWS Resource Access Manager không hỗ trợ sharing Savings Plans. RAM dùng để share resources như subnets, transit gateways, license configurations, v.v.

**❌ Đáp án D (Tạo organization mới với payer account mới):** Không cần tạo payer account mới. Nên tạo organization từ account hiện tại có Savings Plan. Tạo organization mới cũng không tận dụng được account hiện tại.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Discount sharing: bật ở billing prefs của account mua Savings Plan + tạo Organization từ account đó. RAM không share Savings Plans."*
