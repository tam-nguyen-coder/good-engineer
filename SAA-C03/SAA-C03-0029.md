# Question #29 - Topic 1

A company provides a Voice over Internet Protocol (VoIP) service that uses UDP connections. The service consists of Amazon EC2 instances that run in an Auto Scaling group. The company has deployments across multiple AWS Regions. The company needs to route users to the Region with the lowest latency. The company also needs automated failover between Regions. Which solution will meet these requirements?

## Options

**A.** Deploy a Network Load Balancer (NLB) and an associated target group. Associate the target group with the Auto Scaling group. Use the NLB as an AWS Global Accelerator endpoint in each Region.

**B.** Deploy an Application Load Balancer (ALB) and an associated target group. Associate the target group with the Auto Scaling group. Use the ALB as an AWS Global Accelerator endpoint in each Region.

**C.** Deploy a Network Load Balancer (NLB) and an associated target group. Associate the target group with the Auto Scaling group. Create an Amazon Route 53 latency record that points to aliases for each NLB. Create an Amazon CloudFront distribution that uses the latency record as an origin.

**D.** Deploy an Application Load Balancer (ALB) and an associated target group. Associate the target group with the Auto Scaling group. Create an Amazon Route 53 weighted record that points to aliases for each ALB. Deploy an Amazon CloudFront distribution that uses the weighted record as an origin.



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty cung cấp dịch vụ `VoIP` sử dụng giao thức `UDP`. Hệ thống chạy trên các `Amazon EC2 instances` được quản lý bởi `Auto Scaling group`, triển khai xuyên suốt nhiều `AWS Regions`.
- **Existing Resources:** `EC2 instances` trong `Auto Scaling group`, kiến trúc multi-Region.
- **Current Issue/Goal:** Cần định tuyến người dùng đến `Region` có độ trễ thấp nhất (lowest latency) đồng thời có cơ chế `failover` tự động giữa các `Region` khi xảy ra sự cố.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `VoIP`, `UDP` | Dịch vụ thoại yêu cầu giao thức tầng 4 (Layer 4), không dùng HTTP/HTTPS |
| `EC2`, `Auto Scaling group` | Tài nguyên compute cần được đính kèm vào target group |
| `Multi-Region` | Triển khai trên nhiều `Region`, yêu cầu định tuyến và failover xuyên vùng |
| `Lowest latency` | Yêu cầu định tuyến người dùng đến điểm có độ trễ mạng thấp nhất |
| `Automated failover` | Cần chuyển hướng traffic tự động khi một `Region` bị lỗi |
| `Network Load Balancer` (`NLB`) | Bộ cân bằng tải tầng 4, hỗ trợ `TCP`, `UDP`, `TLS` |
| `Application Load Balancer` (`ALB`) | Bộ cân bằng tải tầng 7, chỉ hỗ trợ `HTTP`/`HTTPS`, **không hỗ trợ UDP** |
| `AWS Global Accelerator` | Dịch vụ sử dụng anycast IP của AWS, định tuyến traffic qua mạng backbone toàn cầu đến endpoint gần nhất và khỏe nhất với failover gần như tức thì |
| `Route 53 latency record` | Ghi DNS định tuyến theo độ trễ, nhưng failover phụ thuộc vào TTL và DNS propagation |
| `Amazon CloudFront` | CDN phân phối nội dung `HTTP`/`HTTPS`, **không hỗ trợ UDP** |
| `Route 53 weighted record` | Định tuyến theo tỷ trọng (phân phối lưu lượng), không phải theo độ trễ |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Kiến trúc giải pháp (Architecture design)
- **Constraints:** 
  1. Phải hỗ trợ `UDP` (VoIP)
  2. Định tuyến đến `Region` có độ trễ thấp nhất
  3. `Failover` tự động giữa các `Region`

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:** 
- `NLB` hoạt động ở tầng 4 (Transport Layer), hỗ trợ trực tiếp giao thức `UDP` cần thiết cho dịch vụ `VoIP`. Việc gắn `target group` của `NLB` với `Auto Scaling group` đảm bảo các `EC2 instances` mới sinh ra tự động nhận traffic.
- `AWS Global Accelerator` cung cấp 2 static IP anycast (hoặc custom domain) giúp định tuyến người dùng qua mạng riêng toàn cầu của AWS đến `endpoint` (`NLB`) tại `Region` gần nhất và khỏe nhất — đáp ứng yêu cầu **lowest latency**.
- `Global Accelerator` thực hiện health check liên tục trên các `endpoint` ở mọi `Region`. Khi một `Region` bị lỗi, nó tự động ngay lập tức chuyển traffic sang `Region` khác mà không phụ thuộc vào DNS TTL (khác với giải pháp DNS thông thường) — đáp ứng yêu cầu **automated failover**.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** Dùng `ALB` làm `Global Accelerator endpoint`. `ALB` là bộ cân bằng tải tầng 7, chỉ hỗ trợ `HTTP`/`HTTPS`, hoàn toàn **không thể xử lý traffic `UDP`** của VoIP. Dù `Global Accelerator` có hỗ trợ `ALB` làm endpoint, nhưng bản thân `ALB` sẽ loại bỏ các gói tin `UDP`.

**❌ Đáp án C:** Dùng `Route 53 latency record` kết hợp `CloudFront`. Tuy `NLB` và latency record là hợp lý, nhưng `Amazon CloudFront` là dịch vụ CDN cho nội dung `HTTP`/`HTTPS`, **không hỗ trợ `UDP`**. Bạn không thể dùng `CloudFront` làm origin/proxy cho traffic VoIP. Ngoài ra, failover dựa trên DNS còn chịu ảnh hưởng bởi TTL và caching, không đạt được độ trễ failover tức thì như `Global Accelerator`.

**❌ Đáp án D:** Dùng `ALB` (không hỗ trợ `UDP`), `Route 53 weighted record` (định tuyến theo trọng số, **không phải theo độ trễ**), và `CloudFront` (không hỗ trợ `UDP`). Đáp án này vi phạm cả 3 ràng buộc của đề bài.

## 6. MẸO GHI NHỚ
🧠 *VoIP/UDP = tầng 4 = `NLB` (loại ngay `ALB` và `CloudFront`).*
🧠 *Multi-region lowest latency + instant failover = `AWS Global Accelerator` (không phải Route 53 DNS).*
🧠 *Gặp đề bài `UDP`/`TCP` thuần + multi-region: nghĩ ngay đến `NLB` + `Global Accelerator`.*


