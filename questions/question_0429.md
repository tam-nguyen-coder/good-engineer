# Question #429 - Topic 1

The following IAM policy is attached to an IAM group. This is the only policy applied to the group. What are the effective IAM permissions of this policy for group members?

## Options

**A.** Group members are permitted any Amazon EC2 action within the us-east-1 Region. Statements after the Allow permission are not applied.

**B.** Group members are denied any Amazon EC2 permissions in the us-east-1 Region unless they are logged in with multi-factor authentication (MFA).

**C.** Group members are allowed the ec2:StopInstances and ec2:TerminateInstances permissions for all Regions when logged in with multi- factor authentication (MFA). Group members are permitted any other Amazon EC2 action.

**D.** Group members are allowed the ec2:StopInstances and ec2:TerminateInstances permissions for the us-east-1 Region only when logged in with multi-factor authentication (MFA). Group members are permitted any other Amazon EC2 action within the us-east-1 Region.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** IAM policy attached to group (only policy). Need effective permissions.
- **Existing Resources:** IAM group with policy.
- **Current Issue/Goal:** Determine what members can/cannot do.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `effective IAM permissions` | Allow + Deny + implicit deny. Deny overrides Allow. |
| `Region restriction` | us-east-1 restriction with Allow statement. |
| `MFA condition` | Deny stop/terminate without MFA. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** IAM Policy evaluation
- **Constraints:** Single policy, group members

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Allow ec2:* trong us-east-1 → mọi EC2 action được phép.
- Deny ec2:StopInstances và ec2:TerminateInstances trong us-east-1 trừ khi có MFA → chỉ stop/terminate được khi có MFA.
- Kết quả: tất cả EC2 actions trong us-east-1 được phép, nhưng stop/terminate yêu cầu MFA.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Sai: statements after Allow vẫn được evaluate.

**❌ Đáp án B:**
- Sai: deny chỉ áp dụng cho stop/terminate, không phải tất cả EC2 actions.

**❌ Đáp án C:**
- Sai: actions restricted to us-east-1 (region condition trong Allow).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Deny override Allow. Stop/terminate cần MFA, EC2 khác OK trong us-east-1."*