# Question #253 - Topic 1

A solutions architect has created two IAM policies: Policy1 and Policy2. Both policies are attached to an IAM group. A cloud engineer is added as an IAM user to the IAM group. Which action will the cloud engineer be able to perform?

## Options

**A.** Deleting IAM users

**B.** Deleting directories

**C.** Deleting Amazon EC2 instances

**D.** Deleting logs from Amazon CloudWatch Logs

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Two IAM policies (Policy1, Policy2) attached to a group. User added to group.
- **Existing Resources:** IAM group, policies.
- **Current Issue/Goal:** Determine which action is allowed (⚠️ Policy content not shown in file).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Both policies are attached to an IAM group` | Permissions là union của cả 2 policies |
| `added as an IAM user to the IAM group` | User thừa hưởng permissions từ group |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** IAM / Authorization
- **Constraints:** Xác định action được phép

## 4. ĐÁP ÁN ĐÚNG
**⚠️ File question không hiển thị nội dung Policy1 và Policy2. Cần có policy content để xác định action nào được phép.**

**Nguyên tắc:** IAM permissions là cumulative — user được cấp tất cả permissions từ tất cả policies attached đến group.

## 5. CÁC ĐÁP ÁN SAI
Không thể xác định nếu không có policy content.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"IAM policies attached to group = cumulative permissions. User inherits all from group"*
