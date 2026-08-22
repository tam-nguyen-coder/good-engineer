# Question #151 - Topic 1

A company wants to migrate its on-premises data center to AWS. According to the company's compliance requirements, the company can use only the ap-northeast-3 Region. Company administrators are not permitted to connect VPCs to the internet. Which solutions will meet these requirements? (Choose two.)

## Options

**A.** Use AWS Control Tower to implement data residency guardrails to deny internet access and deny access to all AWS Regions except ap- northeast-3.

**B.** Use rules in AWS WAF to prevent internet access. Deny access to all AWS Regions except ap-northeast-3 in the AWS account settings.

**C.** Use AWS Organizations to configure service control policies (SCPS) that prevent VPCs from gaining internet access. Deny access to all AWS Regions except ap-northeast-3.

**D.** Create an outbound rule for the network ACL in each VPC to deny all traffic from 0.0.0.0/0. Create an IAM policy for each user to prevent the use of any AWS Region other than ap-northeast-3.

**E.** Use AWS Config to activate managed rules to detect and alert for internet gateways and to detect and alert for new resources deployed outside of ap-northeast-3.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Chỉ dùng ap-northeast-3, không được kết nối VPC ra internet.
- **Existing Resources:** Chưa có trên AWS.
- **Current Issue/Goal:** Enforce Region restriction + no internet access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `only the ap-northeast-3 Region` | Cần **SCP** hoặc **Control Tower guardrails** |
| `not permitted to connect VPCs to the internet` | SCP deny CreateInternetGateway |
| `Service control policies (SCPs)` | AWS Organizations policy |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Governance / Compliance
- **Constraints:** Chọn 2

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và C**

**Giải thích:**
- **A: Control Tower guardrails** — managed policy để deny internet access + restrict Regions.
- **C: SCPs** — deny tạo IGW (internet access) + restrict Regions.
- Cả 2 đều preventive (chặn trước khi xảy ra).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- WAF — Web Application Firewall, không thể prevent internet access hoặc restrict Regions.

**❌ Đáp án D:**
- NACL có thể bị thay đổi bởi admin. IAM policy không prevent API calls ở Region-level hiệu quả như SCP.

**❌ Đáp án E:**
- AWS Config — detective (phát hiện sau), không preventive. Không đáp ứng yêu cầu "not permitted".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SCP + Control Tower = preventive (chặn trước). AWS Config = detective (phát hiện sau)"*
