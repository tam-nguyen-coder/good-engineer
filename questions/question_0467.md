# Question #467 - Topic 1

A company uses AWS Organizations. A member account has purchased a Compute Savings Plan. Because of changes in the workloads inside the member account, the account no longer receives the full benefit of the Compute Savings Plan commitment. The company uses less than 50% of its purchased compute power.

## Options

**A.** Turn on discount sharing from the Billing Preferences section of the account console in the member account that purchased the Compute Savings Plan.

**B.** Turn on discount sharing from the Billing Preferences section of the account console in the company's Organizations management account.

**C.** Migrate additional compute workloads from another AWS account to the account that has the Compute Savings Plan.

**D.** Sell the excess Savings Plan commitment in the Reserved Instance Marketplace.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** AWS Organizations, member account mua Compute Savings Plan nhưng đang dùng <50%.
- **Existing Resources:** Compute Savings Plan trong member account.
- **Current Issue/Goal:** Tận dụng full benefit, tránh lãng phí.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `AWS Organizations` | Nhiều accounts, có management account. |
| `Compute Savings Plan` | Flexible: áp dụng cho EC2, Lambda, Fargate. |
| `less than 50%` | Lãng phí capacity. |
| `discount sharing` | Savings Plan discount có thể share giữa các accounts trong Organization. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** AWS Organizations, member account có Savings Plan dư thừa

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Discount sharing (RI/Savings Plan sharing) được bật từ management account trong Billing Preferences.
- Khi bật, Savings Plan discount từ bất kỳ account nào trong organization đều được áp dụng cho tất cả accounts.
- Không cần migrate workloads, không cần bán lại.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Discount sharing chỉ có thể được bật từ management account, không phải member account.

**❌ Đáp án C:**
- Migrate workloads tốn công sức, không cần thiết khi có thể bật discount sharing.

**❌ Đáp án D:**
- Reserved Instance Marketplace chỉ dành cho RI (Reserved Instances), không phải Savings Plan.
- Savings Plan không thể bán trên marketplace.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Savings Plan dư → bật discount sharing ở management account. Member account không tự bật được."*
