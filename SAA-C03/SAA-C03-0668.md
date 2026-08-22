# Question #668 - Topic 1

A company created a new organization in AWS Organizations. The organization has multiple accounts for the company's development teams. The development team members use AWS IAM Identity Center (AWS Single Sign-On) to access the accounts. For each of the company's applications, the development teams must use a predefined application name to tag resources that are created. A solutions architect needs to design a solution that gives the development team the ability to create resources only if the application name tag has an approved value. Which solution will meet these requirements?

## Options

**A.** Create an IAM group that has a conditional Allow policy that requires the application name tag to be specified for resources to be created.

**B.** Create a cross-account role that has a Deny policy for any resource that has the application name tag.

**C.** Create a resource group in AWS Resource Groups to validate that the tags are applied to all resources in all accounts.

**D.** Create a tag policy in Organizations that has a list of allowed application names.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-account via Organizations, IAM Identity Center (SSO). Dev teams must tag with approved application name. Only allow creation if tag has approved value.
- **Existing Resources:** AWS Organizations, IAM Identity Center, multiple accounts.
- **Current Issue/Goal:** Enforce approved tag values across accounts.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `tag policy` | Tính năng của Organizations: enforce approved tag keys and values across accounts. |
| `approved value` | Tag policy có thể specify list of allowed values. |
| `IAM Identity Center` | Dev teams access accounts via SSO. |
| `only if the application name tag has an approved value` | Tag policy + SCP có thể enforce tag requirements. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Multi-account, enforce tag values

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Tag policy trong AWS Organizations cho phép define approved tag keys và values.
- Áp dụng cho tất cả accounts trong organization → centralized enforcement.
- Khi dev tạo resource không đúng approved value, API sẽ bị từ chối.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- IAM group trong 1 account, không thể áp dụng cross-account.
- Conditional Allow policy phức tạp và không dễ quản lý cho nhiều accounts.

**❌ Đáp án B:**
- Deny policy cho resource có tag → ngược yêu cầu (cần cho phép tạo resource có tag, không deny).

**❌ Đáp án C:**
- AWS Resource Groups dùng để organize resources theo tags, không enforce tag values tại creation time.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Enforce tag values across organization → Tag Policy in AWS Organizations."*
