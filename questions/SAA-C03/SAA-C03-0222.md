# Question #222 - Topic 1

A company has hired an external vendor to perform work in the company's AWS account. The vendor uses an automated tool that is hosted in an AWS account that the vendor owns. The vendor does not have IAM access to the company's AWS account. How should a solutions architect grant this access to the vendor?

## Options

**A.** Create an IAM role in the company's account to delegate access to the vendor's IAM role. Attach the appropriate IAM policies to the role for the permissions that the vendor requires.

**B.** Create an IAM user in the company's account with a password that meets the password complexity requirements. Attach the appropriate IAM policies to the user for the permissions that the vendor requires.

**C.** Create an IAM group in the company's account. Add the tool's IAM user from the vendor account to the group. Attach the appropriate IAM policies to the group for the permissions that the vendor requires.

**D.** Create a new identity provider by choosing "AWS account" as the provider type in the IAM console. Supply the vendor's AWS account ID and user name. Attach the appropriate IAM policies to the new provider for the permissions that the vendor requires.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** External vendor needs access to company's AWS account. Vendor's tool in vendor's account.
- **Existing Resources:** Company's AWS account.
- **Current Issue/Goal:** Cross-account IAM role delegation.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `AWS account that the vendor owns` | **Cross-account IAM role** |
| `does not have IAM access` | Cần IAM role với trust policy |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / IAM
- **Constraints:** Cross-account access

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Tạo **IAM role** trong company's account.
- Trust policy cho phép vendor's IAM role assume role này.
- Attach permissions policy → vendor's tool có quyền cần thiết.
- Best practice cho cross-account access.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- IAM user với password — không phù hợp cho automated tool, không secure.

**❌ Đáp án C:**
- IAM group — không thể add IAM user từ account khác.

**❌ Đáp án D:**
- Identity provider với "AWS account" — không phải cách tạo cross-account access.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cross-account IAM role = secure vendor access. IAM user/group = wrong for cross-account"*
