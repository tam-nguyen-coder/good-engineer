# Question #412 - Topic 1

An image-hosting company stores its objects in Amazon S3 buckets. The company wants to avoid accidental exposure of the objects in the S3 buckets to the public. All S3 objects in the entire AWS account need to remain private. Which solution will meet these requirements?

## Options

**A.** Use Amazon GuardDuty to monitor S3 bucket policies. Create an automatic remediation action rule that uses an AWS Lambda function to remediate any change that makes the objects public.

**B.** Use AWS Trusted Advisor to find publicly accessible S3 buckets. Configure email notifications in Trusted Advisor when a change is detected. Manually change the S3 bucket policy if it allows public access.

**C.** Use AWS Resource Access Manager to find publicly accessible S3 buckets. Use Amazon Simple Notification Service (Amazon SNS) to invoke an AWS Lambda function when a change is detected. Deploy a Lambda function that programmatically remediates the change.

**D.** Use the S3 Block Public Access feature on the account level. Use AWS Organizations to create a service control policy (SCP) that prevents IAM users from changing the setting. Apply the SCP to the account.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Image hosting on S3. Prevent accidental public exposure. All objects must stay private across entire account.
- **Existing Resources:** S3 buckets, AWS account.
- **Current Issue/Goal:** Enforce private-only access, prevent public leaks.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `entire AWS account` | Account-level setting, không per-bucket. |
| `avoid accidental exposure` | Block Public Access là preventive control. |
| `SCP` | Service control policy: ngăn thay đổi settings. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security - Preventive
- **Constraints:** All buckets, entire account

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- S3 Block Public Access (account-level): 4 settings block all public access (ACLs, bucket policies, etc.).
- SCP: deny actions that modify Block Public Access settings → enforce không ai tắt được.
- Preventive + detective control kết hợp.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- GuardDuty: phát hiện threat, không có "automatic remediation action rule" built-in cho S3 public access.

**❌ Đáp án B:**
- Trusted Advisor + manual: reactive, không tự động, chậm.

**❌ Đáp án C:**
- AWS RAM: dùng để share resources giữa accounts, không detect public buckets.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Block Public Access (account) + SCP = preventive + enforceable. Reactive = sai."*

