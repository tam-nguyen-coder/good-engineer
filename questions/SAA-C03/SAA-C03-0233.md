# Question #233 - Topic 1

A solutions architect has created a new AWS account and must secure AWS account root user access. Which combination of actions will accomplish this? (Choose two.)

## Options

**A.** Ensure the root user uses a strong password.

**B.** Enable multi-factor authentication to the root user.

**C.** Store root user access keys in an encrypted Amazon S3 bucket.

**D.** Add the root user to a group containing administrative permissions.

**E.** Apply the required permissions to the root user with an inline policy document.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** New AWS account, secure root user.
- **Existing Resources:** Root user.
- **Current Issue/Goal:** Root user security best practices.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `secure AWS account root user` | **Strong password + MFA** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / IAM
- **Constraints:** Chọn 2, root user security

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và B**

**Giải thích:**
- **A: Strong password** — bảo vệ root user khỏi brute force.
- **B: MFA** — lớp bảo vệ thứ hai, AWS best practice cho root user.
- Root user đã có full permissions — không cần thêm policies.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án C:**
- Không nên tạo access keys cho root user — nếu có thì không lưu trong S3.

**❌ Đáp án D:**
- Root user không cần group permissions (đã có full access).

**❌ Đáp án E:**
- Inline policy không cần thiết cho root user.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Root user = strong password + MFA. No access keys. Already has full permissions"*
