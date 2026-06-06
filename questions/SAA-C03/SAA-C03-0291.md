# Question #291 - Topic 1

A media company uses Amazon CloudFront for its publicly available streaming video content. The company wants to secure the video content that is hosted in Amazon S3 by controlling who has access. Some of the company's users are using a custom HTTP client that does not support cookies. Some of the company's users are unable to change the hardcoded URLs that they are using for access. Which services or methods will meet these requirements with the LEAST impact to the users? (Choose two.)

## Options

**A.** Signed cookies

**B.** Signed URLs

**C.** AWS AppSync

**D.** JSON Web Token (JWT)

**E.** AWS Secrets Manager

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CloudFront + S3 video content, cần access control. Có 2 nhóm users: (1) không support cookies, (2) không thể thay đổi hardcoded URLs.
- **Existing Resources:** CloudFront distribution, S3 bucket.
- **Current Issue/Goal:** Secure video content với ít impact nhất lên users.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `does not support cookies` | User này cần Signed URLs (vì cookies không hoạt động). |
| `unable to change URLs` | User này cần Signed cookies (vì không cần thay đổi URL gốc). |
| `Signed cookies` | CloudFront kiểm tra cookie để authorize, URL giữ nguyên. |
| `Signed URLs` | CloudFront kiểm tra URL đã ký, không cần cookies. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two, least impact to users
- **Constraints:** Hai nhóm users khác nhau cần 2 giải pháp khác nhau

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A (Signed cookies) và B (Signed URLs)**

**Giải thích:**
- Signed cookies: Hoạt động cho users không thể thay đổi URLs → họ giữ nguyên URL, cookie chứa signature.
- Signed URLs: Hoạt động cho users không support cookies → họ dùng URL đã ký sẵn chứa signature.
- Cả hai đều dùng CloudFront signed request để kiểm soát access đến S3 content.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án C:**
- AWS AppSync là GraphQL service, không liên quan CloudFront access control.

**❌ Đáp án D:**
- JWT không phải CloudFront-native access control method. CloudFront không hỗ trợ JWT validation tự động.

**❌ Đáp án E:**
- AWS Secrets Manager quản lý secrets, không phải công cụ access control cho CloudFront.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Không cookies → Signed URLs. Không đổi URL → Signed cookies. Cả 2 đều dùng CloudFront signed request."*
