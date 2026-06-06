# Question #26 - Topic 1

A company needs to review its AWS Cloud deployment to ensure that its Amazon S3 buckets do not have unauthorized configuration changes. What should a solutions architect do to accomplish this goal?

## Options

**A.** Turn on AWS Config with the appropriate rules.

**B.** Turn on AWS Trusted Advisor with the appropriate checks.

**C.** Turn on Amazon Inspector with the appropriate assessment template.

**D.** Turn on Amazon S3 server access logging. Configure Amazon EventBridge (Amazon Cloud Watch Events).



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty cần kiểm tra và giám sát triển khai `AWS Cloud` của mình.
- **Existing Resources:** Các `Amazon S3 buckets` đang hoạt động trong môi trường AWS.
- **Current Issue/Goal:** Đảm bảo các `S3 buckets` không bị thay đổi cấu hình trái phép (`unauthorized configuration changes`), ví dụ như thay đổi `bucket policy`, `ACL`, `public access settings`, hoặc `encryption`.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `unauthorized configuration changes` | Thay đổi cấu hình không được phép trên tài nguyên AWS |
| `review its AWS Cloud deployment` | Kiểm tra, đánh giá toàn bộ môi trường triển khai |
| `Amazon S3 buckets` | Dịch vụ lưu trữ đối tượng cần được giám sát |
| `appropriate rules` / `checks` / `assessment template` | Các cơ chế đánh giá/quy tắc của từng dịch vụ AWS |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Lựa chọn dịch vụ AWS phù hợp nhất để giám sát và phát hiện thay đổi cấu hình trái phép.
- **Constraints:** Tập trung vào **configuration changes** (thay đổi cấu hình tài nguyên), không phải truy cập dữ liệu, quét lỗ hổng hay khuyến nghị chung.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** `AWS Config` là dịch vụ được thiết kế riêng để đánh giá, kiểm tra, ghi lại lịch sử và đánh giá tuân thủ (`compliance`) của các cấu hình tài nguyên AWS. Khi bật `AWS Config` và áp dụng các `rules` phù hợp (ví dụ: `s3-bucket-public-read-prohibited`, `s3-bucket-public-write-prohibited`, `s3-bucket-ssl-requests-only`), doanh nghiệp có thể:
- Liên tục giám sát trạng thái cấu hình `S3 buckets`.
- Ghi lại `configuration timeline` để xem ai đã thay đổi gì và khi nào.
- Nhận thông báo khi cấu hình vi phạm quy tắc hoặc có thay đổi trái phép.
Đây là giải pháp toàn diện nhất cho yêu cầu review và đảm bảo cấu hình không bị sửa đổi trái phép.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** `AWS Trusted Advisor` chủ yếu cung cấp các khuyến nghị thực hành tốt nhất (`best practices`) về chi phí, hiệu suất, bảo mật, khả năng chịu lỗi và giới hạn dịch vụ. Mặc dù có một số kiểm tra bảo mật cơ bản, nó **không** được thiết kế để liên tục theo dõi, ghi lại lịch sử chi tiết hoặc phát hiện thay đổi cấu hình cụ thể của từng `S3 bucket`.

**❌ Đáp án C:** `Amazon Inspector` là dịch vụ đánh giá bảo mật tự động dành cho `EC2 instances`, `Lambda functions` và container workloads nhằm phát hiện lỗ hổng phần mềm và lộ trình mạng không mong muốn. Nó **không** giám sát hoặc đánh giá thay đổi cấu hình của `Amazon S3`.

**❌ Đáp án D:** `Amazon S3 server access logging` chỉ ghi lại các yêu cầu truy cập vào **dữ liệu** trong bucket (ai đã tải lên, tải xuống, xóa đối tượng), chứ **không** ghi lại các thay đổi **cấu hình** của bucket (như thay đổi `bucket policy`, `ACL`, hoặc `Block Public Access`). Việc kết hợp với `Amazon EventBridge` (`Amazon CloudWatch Events`) trong option này cũng không tạo thành giải pháp chuyên dụng để audit configuration compliance như `AWS Config`.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài nhắc đến "configuration changes", "audit configuration", "compliance of resource configurations", hoặc "detect configuration drift" → Nghĩ ngay đến `AWS Config`. Tên dịch vụ đã nói lên tất cả: **Config** = Cấu hình. `Trusted Advisor` = Khuyến nghị chung. `Inspector` = Quét lỗ hổng cho compute. `S3 server access logs` = Log truy cập dữ liệu.*


