# Question #619 - Topic 1

A solutions architect is designing a security solution for a company that wants to provide developers with individual AWS accounts through AWS Organizations, while also maintaining standard security controls. Because the individual developers will have AWS account root user-level access to their own accounts, the solutions architect wants to ensure that the mandatory AWS CloudTrail configuration that is applied to new developer accounts is not modified. Which action meets these requirements?

## Options

**A.** Create an IAM policy that prohibits changes to CloudTrail. and attach it to the root user.

**B.** Create a new trail in CloudTrail from within the developer accounts with the organization trails option enabled.

**C.** Create a service control policy (SCP) that prohibits changes to CloudTrail, and attach it the developer accounts.

**D.** Create a service-linked role for CloudTrail with a policy condition that allows changes only from an Amazon Resource Name (ARN) in the management account.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** AWS Organizations, developer accounts với root user access. Cần đảm bảo mandatory CloudTrail config không bị modify.
- **Existing Resources:** AWS Organizations với management account và member accounts.
- **Current Issue/Goal:** Prevent developers (kể cả root user) từ sửa/xóa CloudTrail configuration.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `root user-level access` | Root user có toàn quyền, không thể bị giới hạn bởi IAM policies. |
| `AWS Organizations` | Có thể dùng SCP để restrict permissions kể cả root. |
| `service control policy (SCP)` | SCP áp dụng cho tất cả IAM users/roles và root user trong member accounts. |
| `mandatory CloudTrail configuration` | Cần prevent disable/modify CloudTrail. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (security)
- **Constraints:** Developer accounts with root access, must not modify CloudTrail

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- SCP (Service Control Policy): áp dụng ở organization level, ảnh hưởng đến tất cả users trong member accounts, kể cả root user.
- Tạo SCP deny changes to CloudTrail → dù developer có root user access cũng không thể sửa/xóa CloudTrail configuration.
- SCP là cơ chế duy nhất có thể giới hạn root user trong member accounts.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- IAM policy attached to root user: root user không bị giới hạn bởi IAM policies → vô hiệu.

**❌ Đáp án B:**
- Organization trail được tạo từ management account có thể áp dụng cho member accounts, nhưng developer vẫn có thể disable/modify trail từ account của họ.

**❌ Đáp án D:**
- Service-linked role: chỉ cho phép CloudTrail service hoạt động, không prevent user từ sửa CloudTrail configuration.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Root user can't be stopped by IAM → cần SCP. SCP áp dụng cho cả root trong member accounts."*
