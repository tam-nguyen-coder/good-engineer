# Question #168 - Topic 1

A security team wants to limit access to specific services or actions in all of the team's AWS accounts. All accounts belong to a large organization in AWS Organizations. The solution must be scalable and there must be a single point where permissions can be maintained. What should a solutions architect do to accomplish this?

## Options

**A.** Create an ACL to provide access to the services or actions.

**B.** Create a security group to allow accounts and attach it to user groups.

**C.** Create cross-account roles in each account to deny access to the services or actions.

**D.** Create a service control policy in the root organizational unit to deny access to the services or actions.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Security team wants to restrict services/actions across ALL accounts in AWS Organizations.
- **Existing Resources:** AWS Organizations with multiple accounts.
- **Current Issue/Goal:** Single point to maintain permissions, scalable.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `limit access to specific services... across all accounts` | **Service Control Policy (SCP)** |
| `single point where permissions can be maintained` | Root OU in Organizations |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Organizations
- **Constraints:** All accounts, single maintenance point, scalable

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **SCP (Service Control Policy)** — áp dụng ở root OU → tác dụng lên tất cả accounts trong organization.
- Centralized management — chỉ cần maintain SCP ở root OU.
- Dùng `Deny` effect để chặn services/actions cụ thể.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ACL (Network ACL) — cho VPC subnets, không áp dụng được cho cross-account service restriction.

**❌ Đáp án B:**
- Security group — cho EC2-level, không áp dụng cho accounts.

**❌ Đáp án C:**
- Cross-account roles — cần tạo per account, không phải single point.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SCP at root OU = central permission control for all accounts. ACL/SG = network only"*
