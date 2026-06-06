# Question #545 - Topic 1

A company wants to direct its users to a backup static error page if the company's primary website is unavailable. The primary website's DNS records are hosted in Amazon Route 53. The domain is pointing to an Application Load Balancer (ALB). The company needs a solution that minimizes changes and infrastructure overhead. Which solution will meet these requirements?

## Options

**A.** Update the Route 53 records to use a latency routing policy. Add a static error page that is hosted in an Amazon S3 bucket to the records so that the traffic is sent to the most responsive endpoints.

**B.** Set up a Route 53 active-passive failover configuration. Direct traffic to a static error page that is hosted in an Amazon S3 bucket when Route 53 health checks determine that the ALB endpoint is unhealthy.

**C.** Set up a Route 53 active-active configuration with the ALB and an Amazon EC2 instance that hosts a static error page as endpoints. Configure Route 53 to send requests to the instance only if the health checks fail for the ALB.

**D.** Update the Route 53 records to use a multivalue answer routing policy. Create a health check. Direct traffic to the website if the health check passes. Direct traffic to a static error page that is hosted in Amazon S3 if the health check does not pass.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty muốn chuyển hướng người dùng đến backup static error page khi website chính không khả dụng. DNS records đang dùng Route 53. Domain trỏ đến ALB.
- **Existing Resources:** Route 53 DNS, ALB, primary website.
- **Current Issue/Goal:** Failover tự động khi primary website down, tối thiểu thay đổi và overhead.

## 2. KEYWORDS QUAN TRỌng
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `backup static error page` | Trang tĩnh, có thể host trên S3 |
| `primary website is unavailable` | Cần failover khi health check fail |
| `minimizes changes and infrastructure overhead` | Giải pháp đơn giản, không phức tạp |
| `failover` | Chuyển đổi dự phòng |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Minimize changes, minimize infra overhead, tự động failover

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Route 53 active-passive failover cho phép chỉ định primary (ALB) và secondary (S3 static error page).
- Route 53 health check liên tục kiểm tra ALB endpoint. Khi health check fail, Route 53 tự động chuyển traffic sang S3 static error page.
- S3 static website hosting là giải pháp đơn giản, chi phí thấp, không cần maintenance.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (Latency routing):** Latency routing policy dùng để định tuyến đến region có độ trễ thấp nhất, không phải để failover. Không có health check.

**❌ Đáp án C (Active-active):** Active-active định tuyến traffic đến tất cả endpoints hoạt động. Không có cơ chế "chỉ gửi đến instance khi ALB fail" – cả hai đều nhận traffic. Thêm vào đó, EC2 instance để host static error page là không cần thiết (S3 đủ).

**❌ Đáp án D (Multivalue answer):** Multivalue answer trả về nhiều IP addresses một cách ngẫu nhiên, không phải failover. Khi health check fail, record đó không được trả về, nhưng không tự động chuyển hướng đến backup page đúng nghĩa.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Active-passive failover = primary ALB + secondary S3 static page. Health check decides which one gets traffic."*
