# Question #488 - Topic 1

A 4-year-old media company is using the AWS Organizations all features feature set to organize its AWS accounts. According to the company's finance team, the billing information on the member accounts must not be accessible to anyone, including the root user of the member accounts. Which solution will meet these requirements?

## Options

**A.** Add all finance team users to an IAM group. Attach an AWS managed policy named Billing to the group.

**B.** Attach an identity-based policy to deny access to the billing information to all users, including the root user.

**C.** Create a service control policy (SCP) to deny access to the billing information. Attach the SCP to the root organizational unit (OU).

**D.** Convert from the Organizations all features feature set to the Organizations consolidated billing feature set.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty dùng AWS Organizations all features. Yêu cầu: billing information của member accounts không được ai truy cập, kể cả root user của member accounts.
- **Existing Resources:** AWS Organizations with all features.
- **Current Issue/Goal:** Chặn access vào billing info cho mọi user (kể cả root).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `including the root user` | IAM policy không thể restrict root user. Chỉ SCP mới có thể. |
| `member accounts` | SCP áp dụng lên member accounts từ management account. |
| `service control policy (SCP)` | SCP có thể deny actions kể cả với root user. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security policy (restrict billing access)
- **Constraints:** Must apply to root user too.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **SCP (Service Control Policy)** được attach vào root OU → áp dụng cho tất cả member accounts.
- SCP có thể deny `aws-portal:ViewBilling` và các actions liên quan billing.
- **SCP có hiệu lực với root user** của member accounts (IAM policy không làm được điều này).
- Đây là giải pháp duy nhất trong các đáp án có thể restrict root user.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- IAM group + managed policy Billing: chỉ áp dụng cho IAM users, không thể restrict root user.

**❌ Đáp án B:**
- Identity-based policy: không thể attach cho root user. Root user luôn có full access và không bị giới hạn bởi IAM policies.

**❌ Đáp án D:**
- Convert sang consolidated billing feature set: mất các tính năng all features (SCP, v.v.). Vẫn không giải quyết được vấn đề restrict root user.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SCP = cách duy nhất để restrict root user. IAM không ảnh hưởng root."*
