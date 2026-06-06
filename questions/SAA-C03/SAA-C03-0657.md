# Question #657 - Topic 1

A company has multiple AWS accounts in an organization in AWS Organizations that different business units use. The company has multiple offices around the world. The company needs to update security group rules to allow new office CIDR ranges or to remove old CIDR ranges across the organization. The company wants to centralize the management of security group rules to minimize the administrative overhead that updating CIDR ranges requires. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Create VPC security groups in the organization's management account. Update the security groups when a CIDR range update is necessary.

**B.** Create a VPC customer managed prefix list that contains the list of CIDRs. Use AWS Resource Access Manager (AWS RAM) to share the prefix list across the organization. Use the prefix list in the security groups across the organization.

**C.** Create an AWS managed prefix list. Use an AWS Security Hub policy to enforce the security group update across the organization. Use an AWS Lambda function to update the prefix list automatically when the CIDR ranges change.

**D.** Create security groups in a central administrative AWS account. Create an AWS Firewall Manager common security group policy for the whole organization. Select the previously created security groups as primary groups in the policy.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-account org, multiple offices worldwide, need to update SG CIDR rules across accounts. Centralize management.
- **Existing Resources:** AWS Organizations, multiple accounts.
- **Current Issue/Goal:** Minimize admin overhead for CIDR updates across accounts.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `centralize the management` | Single place to update CIDRs, propagate across accounts. |
| `prefix list` | Collection of CIDRs, reusable in SGs. |
| `AWS RAM` | Share prefix list across AWS Organizations accounts. |
| `most cost-effective` | Prefix list (free) vs Firewall Manager (pay per policy). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Centralized, multi-account, minimize admin overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Tạo VPC customer managed prefix list chứa tất cả CIDR ranges của offices.
- Dùng AWS RAM share prefix list cho tất cả accounts trong organization.
- Các accounts dùng prefix list trong security group rules → khi CIDR thay đổi, chỉ cần update prefix list 1 lần.
- Cost-effective: prefix list và RAM đều free.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Security groups trong management account chỉ áp dụng cho VPC trong management account, không thể dùng cross-account.
- Cần tạo SGs riêng cho mỗi account → không centralized.

**❌ Đáp án C:**
- AWS managed prefix list là AWS pre-defined (cho AWS services), không thể custom.
- Security Hub không có policy để enforce SG updates.

**❌ Đáp án D:**
- Firewall Manager có phí (premium).
- Phức tạp hơn prefix list + RAM cho use case này.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Prefix list + RAM = centralized CIDR management across accounts. Firewall Manager = paid."*
