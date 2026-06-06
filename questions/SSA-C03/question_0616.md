# Question #616 - Topic 1

A company has deployed its newest product on AWS. The product runs in an Auto Scaling group behind a Network Load Balancer. The company stores the product's objects in an Amazon S3 bucket. The company recently experienced malicious attacks against its systems. The company needs a solution that continuously monitors for malicious activity in the AWS account, workloads, and access patterns to the S3 bucket. The solution must also report suspicious activity and display the information on a dashboard. Which solution will meet these requirements?

## Options

**A.** Configure Amazon Macie to monitor and report findings to AWS Config.

**B.** Configure Amazon Inspector to monitor and report findings to AWS CloudTrail.

**C.** Configure Amazon GuardDuty to monitor and report findings to AWS Security Hub.

**D.** Configure AWS Config to monitor and report findings to Amazon EventBridge.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** After malicious attacks, cần continuous monitoring cho malicious activity trong AWS account, workloads, và S3 access patterns. Cần report suspicious activity và dashboard.
- **Existing Resources:** ASG + NLB, S3 bucket.
- **Current Issue/Goal:** Threat detection + centralized security dashboard.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `continuously monitors for malicious activity` | Amazon GuardDuty: managed threat detection service. |
| `AWS account, workloads, S3 access patterns` | GuardDuty monitor CloudTrail logs, VPC Flow Logs, DNS logs, S3 access. |
| `report suspicious activity` | GuardDuty tạo findings. |
| `display on a dashboard` | AWS Security Hub: centralized dashboard cho security findings. |
| `Security Hub` | Aggregates findings từ GuardDuty, Inspector, Macie, etc. vào một dashboard. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (security)
- **Constraints:** Continuous monitoring, malicious activity detection, dashboard

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Amazon GuardDuty: continuous threat detection, phân tích CloudTrail, VPC Flow Logs, DNS logs, và S3 access patterns để phát hiện malicious activity.
- AWS Security Hub: nhận findings từ GuardDuty, cung cấp centralized dashboard và automated compliance checks.
- Kết hợp GuardDuty + Security Hub là best practice cho security monitoring trên AWS.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Amazon Macie: phát hiện sensitive data (PII) trong S3, không phải threat detection cho account/workloads.
- AWS Config: resource compliance, không phải security dashboard.

**❌ Đáp án B:**
- Amazon Inspector: vulnerability scanning cho EC2 và container images, không phải continuous threat monitoring.
- CloudTrail: API logging, không phải security findings dashboard.

**❌ Đáp án D:**
- AWS Config: theo dõi resource configuration changes, không phát hiện malicious activity.
- EventBridge: event bus, không có security dashboard.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Threat detection → GuardDuty + Security Hub (dashboard). Macie = data, Inspector = vuln, Config = compliance."*
