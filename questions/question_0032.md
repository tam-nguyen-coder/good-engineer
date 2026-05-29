# Question #32 - Topic 1

A development team needs to host a website that will be accessed by other teams. The website contents consist of HTML, CSS, client-side JavaScript, and images. Which method is the MOST cost-effective for hosting the website?

## Options

**A.** Containerize the website and host it in AWS Fargate.

**B.** Create an Amazon S3 bucket and host the website there.

**C.** Deploy a web server on an Amazon EC2 instance to host the website.

**D.** Configure an Application Load Balancer with an AWS Lambda target that uses the Express.js framework.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một development team cần host một website để các team khác truy cập.
- **Existing Resources:** Website chỉ gồm các file nội dung tĩnh, không có hạ tầng sẵn có.
- **Current Issue/Goal:** Tìm phương pháp `MOST cost-effective` để host website với nội dung hoàn toàn tĩnh.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| HTML, CSS, client-side JavaScript, images | Đây là `static content`, không cần xử lý phía server |
| MOST cost-effective | Ưu tiên giải pháp có chi phí thấp nhất, tối thiểu hóa chi phí vận hành |
| other teams | Website được truy cập bởi nhiều team, có thể internal hoặc external |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Best practice / Cost optimization architecture
- **Constraints:** Website 100% static; không cần server-side rendering hay application logic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**
**Giải thích:** `Amazon S3` cung cấp tính năng `static website hosting` được thiết kế riêng cho các website chỉ chứa file tĩnh như HTML, CSS, JavaScript phía client và images. Với `S3`, không cần provisioning hay quản lý server, không tốn chi phí compute, chỉ trả phí lưu trữ và data transfer. Đây là giải pháp đơn giản, bền vững và tiết kiệm chi phí nhất cho static website.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `AWS Fargate` là dịch vụ chạy container serverless, phù hợp với ứng dụng cần môi trường runtime và xử lý server-side. Sử dụng `Fargate` để host static website là `overkill`, gây lãng phí chi phí compute và tăng độ phức tạp không cần thiết.

**❌ Đáp án C:** `Amazon EC2` yêu cầu chạy máy chủ 24/7, phải trả phí compute theo giờ (hoặc theo cam kết), cộng thêm chi phí vận hành hệ điều hành, bảo mật, patching và scaling. Đắt đỏ và kém hiệu quả hơn rất nhiều so với `S3` khi chỉ host static content.

**❌ Đáp án D:** `Application Load Balancer` (`ALB`) kết hợp với `AWS Lambda` và `Express.js` là kiến trúc serverless dành cho ứng dụng dynamic hoặc API cần logic xử lý phía server. `ALB` có phí hourly cố định, `Lambda` tính phí theo request và thời gian thực thi. Đây là giải pháp phức tạp, tốn kém và hoàn toàn không phù hợp cho mục đích host static website.

## 6. MẸO GHI NHỚ
🧠 *Website tĩnh (HTML/CSS/JS/images) → nghĩ ngay đến `Amazon S3 static website hosting`. Không dùng compute (`EC2`, `Fargate`, `Lambda`) khi không có server-side processing.*


