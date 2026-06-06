# Question #368 - Topic 1

A solutions architect wants all new users to have specific complexity requirements and mandatory rotation periods for IAM user passwords. What should the solutions architect do to accomplish this?

## Options

**A.** Set an overall password policy for the entire AWS account.

**B.** Set a password policy for each IAM user in the AWS account.

**C.** Use third-party vendor software to set password requirements.

**D.** Attach an Amazon CloudWatch rule to the Create_newuser event to set the password with the appropriate requirements.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần password complexity + rotation period cho all new IAM users.
- **Existing Resources:** AWS account with IAM users.
- **Current Issue/Goal:** Enforce password policy.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `complexity requirements` | IAM account password policy: uppercase, lowercase, numbers, symbols, min length. |
| `mandatory rotation periods` | Password expiration period. |
| `overall password policy for the entire AWS account` | IAM account-level password policy áp dụng cho all IAM users. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution enforces password policy
- **Constraints:** All new users, complexity + rotation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- IAM account password policy: set at account level, applies to all IAM users.
- Can configure: min password length, require uppercase/lowercase/numbers/symbols, password expiration period.
- Cannot set per-user password policy.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- IAM không hỗ trợ per-user password policy (password policy là account-level).

**❌ Đáp án C:**
- Third-party software không cần thiết, IAM account password policy có sẵn.

**❌ Đáp án D:**
- CloudWatch Event/Rule không thể set password policy (CloudWatch phản ứng events, không configure IAM).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"IAM password complexity + rotation → Account password policy (global, not per-user)."*
