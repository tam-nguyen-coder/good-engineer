# Question #459 - Topic 1

A company uses AWS Organizations to run workloads within multiple AWS accounts. A tagging policy adds department tags to AWS resources when the company creates tags. An accounting team needs to determine spending on Amazon EC2 consumption. The accounting team must determine which departments are responsible for the costs regardless of AWS account. The accounting team has access to AWS Cost Explorer for all AWS accounts within the organization and needs to access all reports from Cost Explorer. Which solution meets these requirements in the MOST operationally efficient way?

## Options

**A.** From the Organizations management account billing console, activate a user-defined cost allocation tag named department. Create one cost report in Cost Explorer grouping by tag name, and filter by EC2.

**B.** From the Organizations management account billing console, activate an AWS-defined cost allocation tag named department. Create one cost report in Cost Explorer grouping by tag name, and filter by EC2.

**C.** From the Organizations member account billing console, activate a user-defined cost allocation tag named department. Create one cost report in Cost Explorer grouping by the tag name, and filter by EC2.

**D.** From the Organizations member account billing console, activate an AWS-defined cost allocation tag named department. Create one cost report in Cost Explorer grouping by tag name, and filter by EC2.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Organizations multi-account. Tagging policy adds "department" tags. Accounting needs EC2 spending by department across all accounts via Cost Explorer.
- **Existing Resources:** AWS Organizations, Cost Explorer access.
- **Current Issue/Goal:** Track EC2 cost by department tag across accounts.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `user-defined cost allocation tag` | "department" tag created by company = user-defined. |
| `management account` | Activate tags at management account for all member accounts. |
| `Cost Explorer` | Group by tag name, filter by EC2. |
| `most operationally efficient` | One activation at management level. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost management / Tagging
- **Constraints:** Cross-account EC2 cost by department tag

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- "department" tag: user-defined (do company tạo, không phải AWS-defined).
- Activate at Organizations management account: áp dụng cho tất cả member accounts.
- Cost Explorer: group by tag, filter EC2 → one report for all accounts.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- AWS-defined tags: are like aws:createdBy, aws:CloudFormationStackName → không phải "department".

**❌ Đáp án C:**
- Member account activation: chỉ thấy cost của account đó, không cross-account.

**❌ Đáp án D:**
- Member account + AWS-defined tag: cả hai đều sai.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cross-account cost by tag → activate user-defined tag at management account."*