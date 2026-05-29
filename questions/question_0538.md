# Question #538 - Topic 1

A global video streaming company uses Amazon CloudFront as a content distribution network (CDN). The company wants to roll out content in a phased manner across multiple countries. The company needs to ensure that viewers who are outside the countries to which the company rolls out content are not able to view the content. Which solution will meet these requirements?

## Options

**A.** Add geographic restrictions to the content in CloudFront by using an allow list. Set up a custom error message.

**B.** Set up a new URL tor restricted content. Authorize access by using a signed URL and cookies. Set up a custom error message.

**C.** Encrypt the data for the content that the company distributes. Set up a custom error message.

**D.** Create a new URL for restricted content. Set up a time-restricted access policy for signed URLs.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Global video streaming company dùng CloudFront. Cần roll out content theo từng quốc gia, chặn viewers ngoài các quốc gia đó.
- **Existing Resources:** CloudFront distribution.
- **Current Issue/Goal:** Geo-restriction dạng allow list, chặn các quốc gia không được phép.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `phased manner across multiple countries` | Restrict access based on geography |
| `outside the countries` | Geo-restriction: allow list (chỉ cho phép các quốc gia được chọn) |
| `CloudFront geographic restrictions` | Cho phép allow list hoặc block list dựa trên quốc gia |
| `allow list` | Chỉ cho phép viewers từ các quốc gia trong list |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Content restriction / Security
- **Constraints:** Phased rollout, country-based restriction, CloudFront

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- CloudFront có built-in geographic restriction (geo-blocking): allow list hoặc block list dựa trên country codes.
- Dùng allow list: chỉ định các quốc gia được xem content → viewers ngoài danh sách bị chặn.
- Có thể tùy chỉnh error message (VD: "Content not available in your region").
- Đây là giải pháp đơn giản nhất, không cần URL manipulation hay signed URLs.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Signed URL và cookies dùng để kiểm soát access ở cấp độ user/file, không phải ở cấp độ quốc gia.
- Signed URL bảo vệ content khỏi truy cập trái phép nhưng không chặn theo quốc gia.

**❌ Đáp án C:**
- Encryption chỉ bảo vệ content trong quá trình truyền tải, không ngăn viewers từ quốc gia khác xem content nếu họ có quyền truy cập.

**❌ Đáp án D:**
- Time-restricted signed URLs: giới hạn thời gian truy cập, không liên quan đến geographic restriction.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"CloudFront geo-restriction = allow list/block list by country. Signed URLs = user-level access, not geo."*
