# Question #172 - Topic 1

A solutions architect is creating a new Amazon CloudFront distribution for an application. Some of the information submitted by users is sensitive. The application uses HTTPS but needs another layer of security. The sensitive information should be protected throughout the entire application stack, and access to the information should be restricted to certain applications. Which action should the solutions architect take?

## Options

**A.** Configure a CloudFront signed URL.

**B.** Configure a CloudFront signed cookie.

**C.** Configure a CloudFront field-level encryption profile.

**D.** Configure CloudFront and set the Origin Protocol Policy setting to HTTPS Only for the Viewer Protocol Policy.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CloudFront distribution, sensitive user info, HTTPS + another layer needed. Info protected throughout stack, restricted to certain apps.
- **Existing Resources:** CloudFront distribution.
- **Current Issue/Goal:** End-to-end protection + application-level access restriction.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `protected throughout the entire application stack` | **Field-level encryption** — mã hoá từ edge đến origin |
| `restricted to certain applications` | Chỉ ứng dụng có private key mới decrypt được |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Encryption
- **Constraints:** Edge-to-origin encryption, app-level restriction

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **CloudFront field-level encryption** — mã hoá sensitive fields tại edge, chỉ applications có private key mới decrypt được.
- HTTPS bảo vệ in transit, field-level encryption bảo vệ specific fields throughout stack.
- Origin/backend services không cần access plaintext sensitive data.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Signed URL — kiểm soát access to content, không mã hoá dữ liệu.

**❌ Đáp án B:**
- Signed cookie — tương tự signed URL, không mã hoá.

**❌ Đáp án D:**
- HTTPS Only — đã có HTTPS, cần thêm layer.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Field-level encryption = encrypt specific fields at edge. Signed URL/cookie = access control, not encryption"*
