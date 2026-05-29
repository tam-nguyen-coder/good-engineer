# Question #12 - Topic 1

A global company hosts its web application on Amazon EC2 instances behind an Application Load Balancer (ALB). The web application has static data and dynamic data. The company stores its static data in an Amazon S3 bucket. The company wants to improve performance and reduce latency for the static data and dynamic data. The company is using its own domain name registered with Amazon Route 53. What should a solutions architect do to meet these requirements?

## Options

**A.** Create an Amazon CloudFront distribution that has the S3 bucket and the ALB as origins. Configure Route 53 to route traffic to the CloudFront distribution.

**B.** Create an Amazon CloudFront distribution that has the ALB as an origin. Create an AWS Global Accelerator standard accelerator that has the S3 bucket as an endpoint Configure Route 53 to route traffic to the CloudFront distribution.

**C.** Create an Amazon CloudFront distribution that has the S3 bucket as an origin. Create an AWS Global Accelerator standard accelerator that has the ALB and the CloudFront distribution as endpoints. Create a custom domain name that points to the accelerator DNS name. Use the custom domain name as an endpoint for the web application.

**D.** Create an Amazon CloudFront distribution that has the ALB as an origin. Create an AWS Global Accelerator standard accelerator that has the S3 bucket as an endpoint. Create two domain names. Point one domain name to the CloudFront DNS name for dynamic content. Point the other domain name to the accelerator DNS name for static content. Use the domain names as endpoints for the web application.



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty toàn cầu đang vận hành web application trên `Amazon EC2` instances phía sau một `Application Load Balancer` (`ALB`). Ứng dụng có cả dữ liệu tĩnh (`static data`) và dữ liệu động (`dynamic data`). Dữ liệu tĩnh được lưu trữ trong `Amazon S3 bucket`. Công ty sở hữu domain name riêng và quản lý DNS thông qua `Amazon Route 53`.
- **Existing Resources:** `EC2` instances, `ALB`, `S3 bucket`, `Route 53` hosted zone.
- **Current Issue/Goal:** Cải thiện performance và giảm độ trễ (`latency`) cho **cả** static data lẫn dynamic data trên phạm vi toàn cầu.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `CloudFront` | Dịch vụ CDN toàn cầu, hỗ trợ multiple origins và cache behaviors |
| `ALB` | Application Load Balancer — nguồn cung cấp dynamic content |
| `S3 bucket` | Object storage — nguồn cung cấp static content |
| `Route 53` | DNS service để điều hướng traffic đến đúng endpoint |
| `Global Accelerator` | Dịch vụ dùng AWS global network để tối ưu đường truyền đến endpoint tại một hoặc nhiều Region |
| `Origins` | Nguồn gốc nội dung của một `CloudFront` distribution |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Architecture design — lựa chọn giải pháp tối ưu nhất
- **Constraints:** 
  - Phải tối ưu cho cả static data (từ `S3`) và dynamic data (từ `ALB`)
  - Phải tận dụng domain name hiện có trên `Route 53`
  - Loại trừ các giải pháp có thành phần không tương thích về mặt kỹ thuật

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** 
- `Amazon CloudFront` hỗ trợ cấu hình **multiple origins** trong cùng một distribution. Ta có thể thiết lập `S3 bucket` làm origin cho static content và `ALB` làm origin cho dynamic content.
- Thông qua **cache behaviors** (ví dụ: dựa trên path pattern như `*.jpg`, `*.css`, `/images/*` → `S3`; còn lại → `ALB`), `CloudFront` tự động điều hướng request đến đúng nguồn gốc.
- Với static content, `CloudFront` cache tại các edge locations toàn cầu, giảm latency tối đa. Với dynamic content, `CloudFront` vẫn giúp giảm latency bằng cách đưa kết nối của người dùng vào mạng backbone của AWS ở edge location gần nhất trước khi forward về `ALB`.
- `Route 53` chỉ cần một alias record trỏ domain đến `CloudFront distribution` là đủ, đơn giản và hiệu quả.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** 
- `AWS Global Accelerator` **không hỗ trợ** `Amazon S3` trực tiếp như một endpoint. Các endpoint hợp lệ của Global Accelerator chỉ gồm `ALB`, `NLB`, `EC2 instances`, hoặc `Elastic IP addresses`.
- Việc dùng Global Accelerator cho static content là không phù hợp khi đã có `CloudFront` — CDN chuyên dụng cho việc phân phối static content.

**❌ Đáp án C:** 
- `CloudFront distribution` **không thể** đóng vai trò làm endpoint cho `AWS Global Accelerator`. 
- Kiến trúc này phức tạp hóa không cần thiết: thay vì dùng `Route 53` trỏ trực tiếp đến `CloudFront`, lại đưa thêm `Global Accelerator` vào giữa với vai trò không hợp lệ.

**❌ Đáp án D:** 
- Tương tự như đáp án B, `Global Accelerator` không hỗ trợ `S3 bucket` là


