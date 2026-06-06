# Question #318 - Topic 1

A company recently migrated its entire IT environment to the AWS Cloud. The company discovers that users are provisioning oversized Amazon EC2 instances and modifying security group rules without using the appropriate change control process. A solutions architect must devise a strategy to track and audit these inventory and configuration changes. Which actions should the solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Enable AWS CloudTrail and use it for auditing.

**B.** Use data lifecycle policies for the Amazon EC2 instances.

**C.** Enable AWS Trusted Advisor and reference the security dashboard.

**D.** Enable AWS Config and create rules for auditing and compliance purposes.

**E.** Restore previous resource configurations with an AWS CloudFormation template.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Users provisioning oversized EC2 instances và modifying security group rules không qua change control. Cần track và audit.
- **Existing Resources:** AWS Cloud environment, EC2 instances, security groups.
- **Current Issue/Goal:** Track and audit inventory và configuration changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `track and audit` | CloudTrail log API calls (who did what). |
| `inventory and configuration changes` | AWS Config track resource configuration changes, evaluate against rules. |
| `oversized EC2 instances` | Config rule: check instance type compliance. |
| `modifying security group rules` | CloudTrail ghi lại API calls → audit. Config track SG rule changes. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two, track and audit
- **Constraints:** EC2 sizing, security group changes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A (CloudTrail) và D (AWS Config)**

**Giải thích:**
- **CloudTrail:** records API calls (EC2 RunInstances, AuthorizeSecurityGroupIngress, etc.) → biết ai đã làm gì, khi nào, từ IP nào.
- **AWS Config:** tracks resource configuration state changes, có thể tạo rules để detect non-compliant configurations (VD: instance type không allowed, SG rule mở 0.0.0.0/0).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Data lifecycle policies dùng cho S3 (quản lý vòng đời objects), không liên quan EC2 instances.

**❌ Đáp án C:**
- Trusted Advisor đưa recommendations (cost optimization, security), không track/audit configuration changes.

**❌ Đáp án E:**
- CloudFormation template restore không track/audit changes.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Track API calls → CloudTrail. Track config changes → AWS Config + rules. Trusted Advisor = recommendations."*
