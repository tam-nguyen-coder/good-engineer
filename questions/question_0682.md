# Question #682 - Topic 1

A company needs a solution to enforce data encryption at rest on Amazon EC2 instances. The solution must automatically identify noncompliant resources and enforce compliance policies on findings. Which solution will meet these requirements with the LEAST administrative overhead?

## Options

**A.** Use an IAM policy that allows users to create only encrypted Amazon Elastic Block Store (Amazon EBS) volumes. Use AWS Config and AWS Systems Manager to automate the detection and remediation of unencrypted EBS volumes.

**B.** Use AWS Key Management Service (AWS KMS) to manage access to encrypted Amazon Elastic Block Store (Amazon EBS) volumes. Use AWS Lambda and Amazon EventBridge to automate the detection and remediation of unencrypted EBS volumes.

**C.** Use Amazon Macie to detect unencrypted Amazon Elastic Block Store (Amazon EBS) volumes. Use AWS Systems Manager Automation rules to automatically encrypt existing and new EBS volumes.

**D.** Use Amazon inspector to detect unencrypted Amazon Elastic Block Store (Amazon EBS) volumes. Use AWS Systems Manager Automation rules to automatically encrypt existing and new EBS volumes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Enforce EBS encryption at rest on EC2. Auto-detect noncompliant resources, auto-remediate.
- **Existing Resources:** EC2 instances, EBS volumes.
- **Current Issue/Goal:** Enforce encryption compliance with least admin overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `automatically identify noncompliant resources` | AWS Config: evaluate resource compliance against rules. |
| `enforce compliance policies` | AWS Systems Manager Automation: auto-remediate. |
| `IAM policy to allow only encrypted` | Preventive control (block creation of unencrypted volumes). |
| `least administrative overhead` | AWS Config managed rules + SSM Automation documents. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least administrative overhead
- **Constraints:** Auto-detect + auto-remediate

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- IAM policy: preventive control, block users from creating unencrypted volumes ngay từ đầu.
- AWS Config: detect unencrypted volumes (managed rule `encrypted-volumes`).
- AWS Systems Manager Automation: auto-remediate (attach encryption or snapshot + recreate encrypted).
- Kết hợp preventive + detective + corrective → least admin overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Lambda + EventBridge: operational overhead cao hơn AWS Config managed rules.
- KMS manage access không phải detection mechanism.

**❌ Đáp án C:**
- Amazon Macie dùng để discover sensitive data (PII), không detect unencrypted volumes.

**❌ Đáp án D:**
- Amazon Inspector dùng để vulnerability assessment, không detect unencrypted volumes.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Enforce EBS encryption: IAM (prevent) + AWS Config (detect) + SSM (auto-remediate)."*
