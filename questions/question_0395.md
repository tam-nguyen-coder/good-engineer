# Question #395 - Topic 1

An IAM user made several configuration changes to AWS resources in their company's account during a production deployment last week. A solutions architect learned that a couple of security group rules are not configured as desired. The solutions architect wants to confirm which IAM user was responsible for making changes. Which service should the solutions architect use to find the desired information?

## Options

**A.** Amazon GuardDuty

**B.** Amazon Inspector

**C.** AWS CloudTrail

**D.** AWS Config

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Security group rules not as desired. Cần xác định IAM user đã thay đổi.
- **Existing Resources:** AWS account, security groups.
- **Current Issue/Goal:** Find which IAM user made specific API calls.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `confirm which IAM user` | CloudTrail records API calls with IAM user identity. |
| `who was responsible for making changes` | CloudTrail logs: who, what, when, from where. |
| `AWS CloudTrail` | Audit trail of all API activity in AWS account. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which service to find IAM user responsible for changes
- **Constraints:** Security group changes, past event

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS CloudTrail records all API calls (AuthorizeSecurityGroupIngress, RevokeSecurityGroupEgress, etc.) với thông tin: IAM user, source IP, time, request parameters.
- Tra cứu CloudTrail logs để tìm user đã thực hiện security group changes.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- GuardDuty: threat detection (phát hiện hành vi bất thường), không log IAM user identity.

**❌ Đáp án B:**
- Inspector: vulnerability scanning, không track API calls.

**❌ Đáp án D:**
- Config: track resource configuration state changes, cung cấp configuration timeline nhưng không ghi IAM user (chỉ ghi thay đổi từ state A → B).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Who made API changes → CloudTrail (IAM user, time, IP). Config = configuration state. GuardDuty = threats."*
