# Question #586 - Topic 1

A company has five organizational units (OUs) as part of its organization in AWS Organizations. Each OU correlates to the five businesses that the company owns. The company's research and development (R&D) business is separating from the company and will need its own organization. A solutions architect creates a separate new management account for this purpose. What should the solutions architect do next in the new management account?

## Options

**A.** Have the R&D AWS account be part of both organizations during the transition.

**B.** Invite the R&D AWS account to be part of the new organization after the R&D AWS account has left the prior organization.

**C.** Create a new R&D AWS account in the new organization. Migrate resources from the prior R&D AWS account to the new R&D AWS account.

**D.** Have the R&D AWS account join the new organization. Make the new management account a member of the prior organization.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** R&D business tách riêng, cần organization riêng. Đã tạo management account mới.
- **Existing Resources:** 5 OUs trong AWS Organizations, R&D account in prior org, new management account.
- **Current Issue/Goal:** Move R&D account từ org cũ sang org mới.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `separating from the company` | R&D account cần rời khỏi org cũ. |
| `leave the prior organization` | Trước hết phải rời org cũ, sau đó mới được invite vào org mới. |
| `AWS Organizations` | 1 account chỉ thuộc 1 organization tại 1 thời điểm. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Process/steps for organization separation
- **Constraints:** Must leave prior org before joining new org

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS Organizations: 1 account chỉ thuộc 1 organization duy nhất.
- Quy trình: R&D account rời khỏi org cũ → sau đó new management account invite R&D account vào org mới.
- Không cần migrate resources (tốn thời gian).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Không thể là member của 2 organizations cùng lúc.

**❌ Đáp án C:**
- Tạo account mới + migrate resources → tốn thời gian và phức tạp. Có thể dùng account cũ đơn giản hơn.

**❌ Đáp án D:**
- Management account không thể là member của org khác. Management account là root của org.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Move account between orgs → leave old → invite to new. Can't be in two orgs at once."*
