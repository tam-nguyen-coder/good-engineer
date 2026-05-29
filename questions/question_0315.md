# Question #315 - Topic 1

A company experienced a breach that affected several applications in its on-premises data center. The attacker took advantage of vulnerabilities in the custom applications that were running on the servers. The company is now migrating its applications to run on Amazon EC2 instances. The company wants to implement a solution that actively scans for vulnerabilities on the EC2 instances and sends a report that details the findings. Which solution will meet these requirements?

## Options

**A.** Deploy AWS Shield to scan the EC2 instances for vulnerabilities. Create an AWS Lambda function to log any findings to AWS CloudTrail.

**B.** Deploy Amazon Macie and AWS Lambda functions to scan the EC2 instances for vulnerabilities. Log any findings to AWS CloudTrail.

**C.** Turn on Amazon GuardDuty. Deploy the GuardDuty agents to the EC2 instances. Configure an AWS Lambda function to automate the generation and distribution of reports that detail the findings.

**D.** Turn on Amazon Inspector. Deploy the Amazon Inspector agent to the EC2 instances. Configure an AWS Lambda function to automate the generation and distribution of reports that detail the findings.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** After breach, migrate to EC2. Cần vulnerability scanning cho EC2 instances.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Actively scan for vulnerabilities, generate reports.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `actively scans for vulnerabilities` | Vulnerability assessment, không phải threat detection. |
| `Amazon Inspector` | Automated vulnerability management, scan EC2 for software vulnerabilities và network exposure. |
| `vulnerabilities` | Lỗ hổng bảo mật trong OS/application → Amazon Inspector. |
| `report` | Inspector tự động tạo findings, có thể tích hợp Lambda để gửi report. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Vulnerability scanning on EC2, automated reporting

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Amazon Inspector: dịch vụ vulnerability management, actively scan EC2 instances cho software vulnerabilities và unintended network exposure.
- Cài Amazon Inspector agent trên EC2 để scan OS/application vulnerabilities.
- Lambda automation: dùng để generate và distribute findings report.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS Shield: DDoS protection, không phải vulnerability scanner.

**❌ Đáp án B:**
- Amazon Macie: data classification (PII detection in S3), không scan EC2 vulnerabilities.

**❌ Đáp án C:**
- GuardDuty: threat detection service (phát hiện hành vi bất thường), không phải vulnerability scanner. GuardDuty không có agent để cài trên EC2.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Vulnerability scan EC2 → Amazon Inspector. Shield = DDoS. GuardDuty = threat detection. Macie = PII."*
