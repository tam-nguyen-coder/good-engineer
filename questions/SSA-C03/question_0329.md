# Question #329 - Topic 1

A security audit reveals that Amazon EC2 instances are not being patched regularly. A solutions architect needs to provide a solution that will run regular security scans across a large fleet of EC2 instances. The solution should also patch the EC2 instances on a regular schedule and provide a report of each instance's patch status. Which solution will meet these requirements?

## Options

**A.** Set up Amazon Macie to scan the EC2 instances for software vulnerabilities. Set up a cron job on each EC2 instance to patch the instance on a regular schedule.

**B.** Turn on Amazon GuardDuty in the account. Configure GuardDuty to scan the EC2 instances for software vulnerabilities. Set up AWS Systems Manager Session Manager to patch the EC2 instances on a regular schedule.

**C.** Set up Amazon Detective to scan the EC2 instances for software vulnerabilities. Set up an Amazon EventBridge scheduled rule to patch the EC2 instances on a regular schedule.

**D.** Turn on Amazon Inspector in the account. Configure Amazon Inspector to scan the EC2 instances for software vulnerabilities. Set up AWS Systems Manager Patch Manager to patch the EC2 instances on a regular schedule.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances không được patch thường xuyên. Cần vulnerability scanning + patching + reporting cho large fleet.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Regular security scans + patching + report.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `vulnerability scanning` | Amazon Inspector (vulnerability assessment). |
| `patch on a regular schedule` | AWS Systems Manager Patch Manager (patch management + reporting). |
| `report of each instance's patch status` | Patch Manager cung cấp compliance reports. |
| `large fleet` | Cần managed service, không cron jobs thủ công. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Regular scanning + patching + reporting, large fleet

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Amazon Inspector: scan EC2 instances for software vulnerabilities (CVE) và network exposure.
- AWS Systems Manager Patch Manager: tự động patch EC2 instances theo schedule, cung cấp patch compliance reports.
- Cả 2 đều managed, hoạt động trên large fleet.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Macie: data classification (PII), không phải vulnerability scanner. Cron job trên mỗi instance không scalable cho large fleet.

**❌ Đáp án B:**
- GuardDuty: threat detection, không scan vulnerabilities. Session Manager dùng để connect, không phải patching.

**❌ Đáp án C:**
- Detective: security investigation, không scan vulnerabilities. EventBridge event có thể trigger automation nhưng không patch trực tiếp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Vulnerability scan → Amazon Inspector. Patching + report → Systems Manager Patch Manager. Macie = PII, GuardDuty = threat."*
