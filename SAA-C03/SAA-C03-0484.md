# Question #484 - Topic 1

A company wants to move from many standalone AWS accounts to a consolidated, multi-account architecture. The company plans to create many new AWS accounts for different business units. The company needs to authenticate access to these AWS accounts by using a centralized corporate directory service. Which combination of actions should a solutions architect recommend to meet these requirements? (Choose two.)

## Options

**A.** Create a new organization in AWS Organizations with all features turned on. Create the new AWS accounts in the organization.

**B.** Set up an Amazon Cognito identity pool. Configure AWS IAM Identity Center (AWS Single Sign-On) to accept Amazon Cognito authentication.

**C.** Configure a service control policy (SCP) to manage the AWS accounts. Add AWS IAM Identity Center (AWS Single Sign-On) to AWS Directory Service.

**D.** Create a new organization in AWS Organizations. Configure the organization's authentication mechanism to use AWS Directory Service directly.

**E.** Set up AWS IAM Identity Center (AWS Single Sign-On) in the organization. Configure IAM Identity Center, and integrate it with the company's corporate directory service.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Chuyển từ standalone accounts → multi-account architecture. Tạo nhiều accounts mới cho business units. Cần centralized corporate directory để authenticate access.
- **Existing Resources:** Nhiều standalone AWS accounts, corporate directory service.
- **Current Issue/Goal:** Consolidated architecture + centralized authentication.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `consolidated, multi-account architecture` | AWS Organizations để quản lý nhiều accounts. |
| `centralized corporate directory service` | IAM Identity Center (SSO) tích hợp với corporate directory (AD, Okta, v.v.). |
| `choose two` | Two answers đúng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Multi-account + authentication architecture
- **Constraints:** Dùng corporate directory, centralized authentication.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và E**

**Giải thích:**
- **A:** AWS Organizations với all features turned on → cho phép tạo và quản lý accounts tập trung, áp dụng SCP, và tích hợp IAM Identity Center.
- **E:** IAM Identity Center (formerly AWS SSO) là service trung tâm để quản lý user access vào nhiều AWS accounts. Có thể integrate với corporate directory (Microsoft AD, Okta, Azure AD, v.v.).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Amazon Cognito dành cho customer-facing identity (external users), không phải corporate directory cho AWS accounts access.

**❌ Đáp án C:**
- SCP quản lý permissions, không phải authentication. "Add IAM Identity Center to AWS Directory Service" là sai logic.

**❌ Đáp án D:**
- AWS Organizations không có "authentication mechanism" riêng để tích hợp trực tiếp với Directory Service.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Consolidate accounts → Organizations. Centralized auth → IAM Identity Center + corporate directory."*
