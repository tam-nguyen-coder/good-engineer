# Question #433 - Topic 1

A company is running its production and nonproduction environment workloads in multiple AWS accounts. The accounts are in an organization in AWS Organizations. The company needs to design a solution that will prevent the modification of cost usage tags. Which solution will meet these requirements?

## Options

**A.** Create a custom AWS Config rule to prevent tag modification except by authorized principals.

**B.** Create a custom trail in AWS CloudTrail to prevent tag modification.

**C.** Create a service control policy (SCP) to prevent tag modification except by authorized principals.

**D.** Create custom Amazon CloudWatch logs to prevent tag modification.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multiple accounts in Organizations. Need to prevent modification of cost usage tags.
- **Existing Resources:** AWS Organizations, multiple accounts.
- **Current Issue/Goal:** Preventive control for tag modification across all accounts.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `prevent` | Preventive control, không detective. |
| `service control policy (SCP)` | Centralized policy ở Organization level. |
| `multiple AWS accounts` | SCP áp dụng cho all accounts trong OU. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Governance
- **Constraints:** Prevent tag modification across all accounts

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- SCP: deny tag modification actions (e.g., `tag:TagResources`, `tag:UntagResources`) trừ authorized principals.
- Áp dụng ở root OU → tất cả accounts trong organization.
- Preventive control → không thể modify tags regardless of IAM permissions.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS Config rule: detective (phát hiện), không prevent. Có thể remediation nhưng không phải prevention.

**❌ Đáp án B:**
- CloudTrail: audit log, không prevent actions.

**❌ Đáp án D:**
- CloudWatch logs: log monitoring, không prevent.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Prevent across all accounts = SCP. Detective = Config/CloudTrail."*