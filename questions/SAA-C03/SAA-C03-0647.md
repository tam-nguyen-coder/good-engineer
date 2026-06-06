# Question #647 - Topic 1

A gaming company is building an application with Voice over IP capabilities. The application will serve traffic to users across the world. The application needs to be highly available with an automated failover across AWS Regions. The company wants to minimize the latency of users without relying on IP address caching on user devices. What should a solutions architect do to meet these requirements?

## Options

**A.** Use AWS Global Accelerator with health checks.

**B.** Use Amazon Route 53 with a geolocation routing policy.

**C.** Create an Amazon CloudFront distribution that includes multiple origins.

**D.** Create an Application Load Balancer that uses path-based routing.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming app with VoIP, global users, HA with automated cross-region failover, minimize latency, can't rely on IP caching.
- **Existing Resources:** Multi-region application.
- **Current Issue/Goal:** Low latency + automated failover across regions, static IP.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Voice over IP` | Real-time, UDP, sensitive to latency. |
| `automated failover across AWS Regions` | Cần health check + tự động chuyển region. |
| `without relying on IP address caching` | Không dùng DNS caching (Route 53). Cần anycast static IP. |
| `AWS Global Accelerator` | Anycast IP, health check, cross-region failover, UDP support. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Global low latency, automated cross-region failover, no DNS caching dependency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Global Accelerator cung cấp 2 anycast static IP → client không cần DNS caching.
- Traffic được định tuyến qua AWS global network đến edge location gần nhất → giảm latency.
- Health check + automatic failover: nếu một region fail, traffic tự động chuyển đến region khỏe mạnh.
- Hỗ trợ UDP (VoIP).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Route 53 geolocation dùng DNS, phụ thuộc vào DNS caching trên client devices.
- DNS changes mất TTL (thời gian) để propagate.

**❌ Đáp án C:**
- CloudFront tối ưu cho HTTP/HTTPS content delivery, không hỗ trợ UDP (VoIP).

**❌ Đáp án D:**
- ALB chỉ hoạt động trong 1 region, không hỗ trợ cross-region failover.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Global Accelerator = static anycast IP + cross-region failover + low latency. Route 53 = DNS dependent."*
