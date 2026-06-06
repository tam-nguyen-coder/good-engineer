# Question #476 - Topic 1

A company is expecting rapid growth in the near future. A solutions architect needs to configure existing users and grant permissions to new users on AWS. The solutions architect has decided to create IAM groups. The solutions architect will add the new users to IAM groups based on department. Which additional action is the MOST secure way to grant permissions to the new users?

## Options

**A.** Apply service control policies (SCPs) to manage access permissions

**B.** Create IAM roles that have least privilege permission. Attach the roles to the IAM groups

**C.** Create an IAM policy that grants least privilege permission. Attach the policy to the IAM groups

**D.** Create IAM roles. Associate the roles with a permissions boundary that defines the maximum permissions

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Rapid user growth, IAM groups by department. Need most secure way to grant permissions.
- **Existing Resources:** IAM users, IAM groups (by department).
- **Current Issue/Goal:** Most secure permission management.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `IAM groups` | Group users by department. Gán policy vào group → users inherit permissions. |
| `MOST secure` | Least privilege principle: chỉ grant quyền tối thiểu cần thiết. |
| `service control policies (SCPs)` | Dùng trong Organizations để quản lý permission boundary cho accounts, không dùng cho users/groups. |
| `Attach the roles to the IAM groups` | Không thể attach role vào IAM group. Role được assume, không được attach. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most secure permission management
- **Constraints:** IAM groups by department, growth

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Tạo IAM policy với least privilege permissions → chỉ grant quyền cần thiết cho department đó.
- Attach policy vào IAM group → tất cả users trong group đều có permissions.
- Secure vì theo nguyên tắc least privilege, dễ quản lý khi scale.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- SCPs áp dụng cho AWS accounts/organizational units trong Organizations, không cho IAM users/groups.
- Không phải cách grant permissions cho users.

**❌ Đáp án B:**
- Không thể attach IAM roles vào IAM groups. Roles được assume bởi users/instances/services, không attach vào groups.

**❌ Đáp án D:**
- Permissions boundary: đặt maximum permissions cho user/role, nhưng không phải cách trực tiếp nhất để grant permissions.
- Roles + permissions boundary không giải quyết việc grant permissions cho users trong groups.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Group + permissions = Attach IAM policy (least privilege) vào group. Role không attach vào group được. SCP = cấp account."*
