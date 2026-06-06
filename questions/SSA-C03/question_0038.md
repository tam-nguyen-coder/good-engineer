# Question #38 - Topic 1

A company is hosting a static website on Amazon S3 and is using Amazon Route 53 for DNS. The website is experiencing increased demand from around the world. The company must decrease latency for users who access the website. Which solution meets these requirements MOST cost-effectively?

## Options

**A.** Replicate the S3 bucket that contains the website to all AWS Regions. Add Route 53 geolocation routing entries.

**B.** Provision accelerators in AWS Global Accelerator. Associate the supplied IP addresses with the S3 bucket. Edit the Route 53 entries to point to the IP addresses of the accelerators.

**C.** Add an Amazon CloudFront distribution in front of the S3 bucket. Edit the Route 53 entries to point to the CloudFront distribution.

**D.** Enable S3 Transfer Acceleration on the bucket. Edit the Route 53 entries to point to the new endpoint.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty đang lưu trữ website tĩnh trên `Amazon S3` và sử dụng `Amazon Route 53` để quản lý DNS.
- **Existing Resources:** `S3 bucket` chứa nội dung website tĩnh, `Route 53` đang điều hướng tên miền đến website.
- **Current Issue/Goal:** Lượng truy cập website tăng cao từ nhiều khu vực trên thế giới. Công ty cần giảm độ trễ (latency) cho người dùng toàn cầu một cách hiệu quả về chi phí nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `Static website on Amazon S3` | Website tĩnh được lưu trữ và phục vụ trực tiếp từ S3 |
| `Amazon Route 53` | Dịch vụ DNS để điều hướng người dùng đến endpoint |
| `Decrease latency` | Giảm thời gian phản hồi, tăng tốc độ tải trang |
| `Around the world` | Yêu cầu phân phối nội dung toàn cầu |
| `MOST cost-effectively` | Giải pháp phải tối ưu chi phí, không chỉ hiệu năng |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Chọn giải pháp tối ưu nhất (Best practice / Most cost-effective)
- **Constraints:** Website tĩnh trên S3, người dùng toàn cầu, bắt buộc giảm latency, phải hiệu quả chi phí

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**
**Giải thích:** `Amazon CloudFront` là dịch vụ `CDN` (Content Delivery Network) được thiết kế để phân phối nội dung với độ trễ thấp thông qua mạng lưới `edge locations` toàn cầu. Khi triển khai `CloudFront distribution` phía trước `S3 bucket`, nội dung website tĩnh được cache tại các điểm biên gần người dùng nhất, giảm đáng kể thời gian tải. `CloudFront` tích hợp native với `S3` (qua `Origin Access Control` hoặc `Origin Access Identity`), chi phí chỉ tính theo dữ liệu truyền ra và số lượng request, không có phí cố định hàng giờ. Việc cập nhật bản ghi `Route 53` trỏ `Alias record` đến `CloudFront distribution` là kiến trúc chuẩn, đơn giản và hiệu quả nhất cho kịch bản này.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** Sao chép `S3 bucket` sang tất cả `AWS Regions` và dùng `Route 53 geolocation routing` là cực kỳ tốn kém và phức tạp. Bạn phải chịu chi phí lưu trữ nhân bản, `Cross-Region Replication`, đồng bộ nội dung, và quản lý nhiều bucket. `Geolocation routing` chỉ điều hướng người dùng đến region gần theo vị trí địa lý chứ không tối ưu latency bằng `CDN`, đồng thời không giải quyết được bài toán cache tại edge.

**❌ Đáp án B:** `AWS Global Accelerator` sử dụng `static IP addresses` và điều hướng `Anycast`, nhưng nó chủ yếu phù hợp cho workload `TCP/UDP` hoặc khi cần IP tĩnh cho ứng dụng. Bạn không thể "associate" trực tiếp IP của accelerator với `S3 bucket` như mô tả. `Global Accelerator` có phí cố định theo giờ cho từng accelerator và không phải giải pháp tiêu chuẩn để tăng tốc website tĩnh từ S3.

**❌ Đáp án D:** `S3 Transfer Acceleration` được thiết kế riêng để tăng tốc **upload** (ghi dữ liệu lên S3) bằng cách sử dụng `CloudFront edge network` cho các yêu cầu `PUT/POST`. Nó hoàn toàn không được thiết kế để tăng tốc **download** (đọc/phục vụ nội dung) cho người dùng truy cập website. Do đó, nó không giải quyết được yêu cầu giảm latency cho người dùng cuối.

## 6. MẸO GHI NHỚ
🧠 *Website tĩnh `S3` + Toàn cầu + Giảm latency = `CloudFront`. `CloudFront` là `CDN` mặc định cho `S3`. `Transfer Acceleration` = Upload nhanh. `Global Accelerator` = `TCP/UDP`/`Static IP`, không phải cho HTTP static content. Sao chép bucket đa vùng = đắt đỏ và phức tạp.*


