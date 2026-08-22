# Question #418 - Topic 1

A solutions architect needs to allow team members to access Amazon S3 buckets in two different AWS accounts: a development account and a production account. The team currently has access to S3 buckets in the development account by using unique IAM users that are assigned to an IAM group that has appropriate permissions in the account. The solutions architect has created an IAM role in the production account. The role has a policy that grants access to an S3 bucket in the production account. Which solution will meet these requirements while complying with the principle of least privilege?

## Options

**A.** Attach the Administrator Access policy to the development account users.

**B.** Add the development account as a principal in the trust policy of the role in the production account.

**C.** Turn off the S3 Block Public Access feature on the S3 bucket in the production account.

**D.** Create a user in the production account with unique credentials for each team member.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Team has IAM users in dev account (via group). Need access to S3 in prod account via IAM role. Least privilege.
- **Existing Resources:** Dev account IAM users/group, prod account IAM role with S3 access policy.
- **Current Issue/Goal:** Allow dev users to assume prod role (cross-account access).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `two different AWS accounts` | Cross-account IAM role. |
| `trust policy` | Cho phép dev account assume role in prod. |
| `least privilege` | Chỉ cấp quyền tối thiểu cần thiết. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Cross-account access
- **Constraints:** Least privilege, existing IAM users in dev

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Thêm dev account vào trust policy của IAM role trong prod account → cho phép IAM users từ dev assume role.
- IAM users trong dev đã có permissions qua group, chỉ cần thêm permission để assume prod role.
- Cross-account access best practice: IAM role + trust policy.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Administrator Access policy: quá rộng, vi phạm least privilege.

**❌ Đáp án C:**
- Block Public Access không liên quan đến cross-account IAM access.

**❌ Đáp án D:**
- Tạo user mới trong prod: duplicate users, khó quản lý, không scalable.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cross-account access = IAM role + trust policy. Không tạo user mới."*