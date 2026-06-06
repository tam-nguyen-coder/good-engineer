# Question #665 - Topic 1

A company has customers located across the world. The company wants to use automation to secure its systems and network infrastructure. The company's security team must be able to track and audit all incremental changes to the infrastructure. Which solution will meet these requirements?

## Options

**A.** Use AWS Organizations to set up the infrastructure. Use AWS Config to track changes.

**B.** Use AWS CloudFormation to set up the infrastructure. Use AWS Config to track changes.

**C.** Use AWS Organizations to set up the infrastructure. Use AWS Service Catalog to track changes.

**D.** Use AWS CloudFormation to set up the infrastructure. Use AWS Service Catalog to track changes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Automate infrastructure deployment, track/audit all incremental changes worldwide.
- **Existing Resources:** N/A
- **Current Issue/Goal:** Automation + change tracking.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `automation` | Infrastructure as Code → AWS CloudFormation. |
| `track and audit all incremental changes` | AWS Config: records configuration changes, enables auditing. |
| `AWS Organizations` | Multi-account management, không phải IaC tool. |
| `AWS Service Catalog` | Create/manage approved IT service catalog, không track changes. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Automation + change tracking + audit

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- CloudFormation: Infrastructure as Code → tự động hóa deployment, version-controlled templates.
- AWS Config: ghi lại tất cả configuration changes, hỗ trợ auditing, compliance checks.
- Kết hợp: CloudFormation deploy infrastructure, AWS Config track changes.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS Organizations quản lý accounts/policies, không phải automation tool cho infrastructure deployment.

**❌ Đáp án C:**
- AWS Organizations không phải IaC.
- Service Catalog dùng để catalog hóa approved templates, không track incremental changes.

**❌ Đáp án D:**
- CloudFormation tốt (IaC).
- Service Catalog không track changes (AWS Config mới track).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Infrastructure automation = CloudFormation. Track changes = AWS Config."*
