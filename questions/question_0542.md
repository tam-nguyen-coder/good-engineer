# Question #542 - Topic 1

A media company uses an Amazon CloudFront distribution to deliver content over the internet. The company wants only premium customers to have access to the media streams and file content. The company stores all content in an Amazon S3 bucket. The company also delivers content on demand to customers for a specific purpose, such as movie rentals or music downloads. Which solution will meet these requirements?

## Options

**A.** Generate and provide S3 signed cookies to premium customers.

**B.** Generate and provide CloudFront signed URLs to premium customers.

**C.** Use origin access control (OAC) to limit the access of non-premium customers.

**D.** Generate and activate field-level encryption to block non-premium customers.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty media dùng CloudFront để phân phối nội dung qua internet. Chỉ premium customers mới được truy cập media streams và files. Nội dung lưu trong S3. Công ty cung cấp nội dung on-demand (thuê phim, tải nhạc).
- **Existing Resources:** CloudFront distribution, S3 bucket chứa nội dung.
- **Current Issue/Goal:** Kiểm soát truy cập cho từng người dùng premium cụ thể, cho từng file/content item riêng lẻ.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `premium customers` | Cần kiểm soát truy cập theo từng user |
| `content on demand` | Truy cập theo từng file riêng lẻ (per-file) |
| `movie rentals or music downloads` | Mỗi giao dịch là một file riêng → cần per-file access control |
| `CloudFront` | Content delivery network |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Chỉ premium customers được truy cập, per-file control cho on-demand content

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- CloudFront signed URLs cho phép kiểm soát truy cập ở mức từng file riêng lẻ, với thời gian hết hạn tùy chỉnh.
- Phù hợp với use case "movie rentals" hoặc "music downloads" – mỗi khách hàng được quyền truy cập vào một file cụ thể trong một khoảng thời gian giới hạn.
- Signed URLs có thể được tạo động cho từng giao dịch và gửi cho khách hàng premium.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (S3 signed cookies):** S3 signed cookies không tồn tại. Signed cookies là tính năng của CloudFront, không phải của S3. Nếu muốn dùng cookies, phải dùng CloudFront signed cookies (cho nhiều file), nhưng đề hỏi per-file access.

**❌ Đáp án C (OAC):** Origin Access Control (OAC) chỉ kiểm soát việc CloudFront có thể truy cập S3 origin hay không, không kiểm soát quyền truy cập của từng user riêng lẻ.

**❌ Đáp án D (Field-level encryption):** Field-level encryption dùng để mã hóa các trường dữ liệu nhạy cảm (như thẻ tín dụng) trong POST requests, không phải để kiểm soát truy cập.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Signed URLs = per-file access (movie rental). Signed Cookies = group/bulk access. OAC = CloudFront → S3 only. Field encryption = encrypt fields, not access control."*
