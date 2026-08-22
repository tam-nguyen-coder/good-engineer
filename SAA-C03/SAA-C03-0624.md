# Question #624 - Topic 1

A company wants to provide users with access to AWS resources. The company has 1,500 users and manages their access to on-premises resources through Active Directory user groups on the corporate network. However, the company does not want users to have to maintain another identity to access the resources. A solutions architect must manage user access to the AWS resources while preserving access to the on- premises resources. What should the solutions architect do to meet these requirements?

## Options

**A.** Create an IAM user for each user in the company. Attach the appropriate policies to each user.

**B.** Use Amazon Cognito with an Active Directory user pool. Create roles with the appropriate policies attached.

**C.** Define cross-account roles with the appropriate policies attached. Map the roles to the Active Directory groups.

**D.** Configure Security Assertion Markup Language (SAML) 2.0-based federation. Create roles with the appropriate policies attached. Map the roles to the Active Directory groups.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 1,500 người dùng, AD on-prem quản lý access. Cần dùng cùng identity để access AWS, không muốn maintain identity riêng.
- **Existing Resources:** Active Directory on-premises.
- **Current Issue/Goal:** Federation: dùng AD credentials để access AWS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Active Directory` | Identity provider on-premises. |
| `not maintain another identity` | Federation, không tạo IAM users mới. |
| `SAML 2.0-based federation` | Standard protocol cho identity federation với AD. |
| `Map the roles to the Active Directory groups` | AWS IAM roles mapped to AD groups. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (identity)
- **Constraints:** 1,500 users, existing AD, single identity

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- SAML 2.0 federation: cho phép users dùng AD credentials để login vào AWS thông qua identity federation.
- Tạo IAM roles với policies phù hợp, map roles với AD groups.
- Users không cần tạo/maintain IAM credentials riêng → single identity cho cả on-prem và AWS.
- Đây là best practice cho enterprise federation với AD.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Tạo 1,500 IAM users: users phải maintain credentials riêng, operational overhead cao → không đáp ứng yêu cầu.

**❌ Đáp án B:**
- Amazon Cognito với AD: Cognito phù hợp cho web/mobile applications với user pools, không phải enterprise federation cho AWS console/CLI access.

**❌ Đáp án C:**
- Cross-account roles: dùng cho access giữa các AWS accounts, không giải quyết federation với on-prem AD.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AD + AWS = SAML 2.0 federation. IAM roles mapped to AD groups. Không cần IAM users."*
