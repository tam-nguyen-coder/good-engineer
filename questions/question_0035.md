# Question #35 - Topic 1

A company is preparing to launch a public-facing web application in the AWS Cloud. The architecture consists of Amazon EC2 instances within a VPC behind an Elastic Load Balancer (ELB). A third-party service is used for the DNS. The company's solutions architect must recommend a solution to detect and protect against large-scale DDoS attacks. Which solution meets these requirements?

## Options

**A.** Enable Amazon GuardDuty on the account.

**B.** Enable Amazon Inspector on the EC2 instances.

**C.** Enable AWS Shield and assign Amazon Route 53 to it.

**D.** Enable AWS Shield Advanced and assign the ELB to it.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty chuẩn bị triển khai ứng dụng web `public-facing` trên AWS. Kiến trúc bao gồm các `EC2 instances` nằm trong `VPC` và được đặt phía sau một `Elastic Load Balancer (ELB)`.
- **Existing Resources:** `EC2 instances`, `VPC`, `ELB`. DNS được quản lý bởi dịch vụ third-party (không sử dụng `Amazon Route 53`).
- **Current Issue/Goal:** Kiến trúc sư cần đề xuất giải pháp để phát hiện và bảo vệ chống lại các cuộc tấn công `DDoS` quy mô lớn (`large-scale DDoS attacks`).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `EC2` behind `ELB` | Tài nguyên lõi cần được bảo vệ nằm sau load balancer |
| Third-party DNS | Không dùng `Route 53` — loại bỏ các đáp án yêu cầu `Route 53` |
| Large-scale DDoS | Tấn công quy mô lớn, cần khả năng mitigation chuyên sâu và hỗ trợ 24/7 |
| Detect **and** protect | Không chỉ giám sát, mà còn phải có khả năng ngăn chặn chủ động |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Lựa chọn dịch vụ bảo mật / DDoS protection
- **Constraints:** Ứng dụng public-facing, kiến trúc có `ELB` và `EC2`, DNS dùng third-party, yêu cầu chống DDoS quy mô lớn

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**
**Giải thích:** `AWS Shield Advanced` cung cấp khả năng bảo vệ nâng cao chống lại các cuộc tấn công `DDoS` quy mô lớn cho các tài nguyên AWS như `Elastic Load Balancer (ELB)`, `Amazon CloudFront`, `Global Accelerator`, `Elastic IP`, và `Route 53`. Khi đăng ký `Shield Advanced`, bạn cần gán (`assign`) các tài nguyên cụ thể (ở đây là `ELB`) vào dịch vụ để được bảo vệ chủ động. `Shield Advanced` còn cung cấp `DDoS Response Team (DRT)` hỗ trợ 24/7, báo cáo tấn công chi tiết, và `cost protection` cho các chi phí phát sinh do tấn công. Vì kiến trúc hiện tại có `ELB`/`EC2` và sử dụng third-party DNS, việc bật `Shield Advanced` và gán `ELB` vào đó là giải pháp duy nhất đáp ứng yêu cầu bảo vệ quy mô lớn.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (`Amazon GuardDuty`):** Đây là dịch vụ phát hiện mối đe dọa (intelligent threat detection), giám sát các hoạt động độc hại, bất thường trong tài khoản AWS (ví dụ: compromised instances, reconnaissance). `GuardDuty` **không** cung cấp khả năng bảo vệ hoặc giảm thiểu (`mitigate`) tấn công `DDoS`.

**❌ Đáp án B (`Amazon Inspector`):** Đây là dịch vụ quản lý lỗ hổng tự động, quét `EC2 instances` và container để tìm các lỗ hổng bảo mật và vi phạm best practices. `Inspector` **không** có chức năng phát hiện hay chống `DDoS`.

**❌ Đáp án C (`AWS Shield` + `Route 53`):** `AWS Shield Standard` được tự động bật miễn phí cho `CloudFront` và `Route 53`, nhưng n


