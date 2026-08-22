# Question #141 - Topic 1

A company runs a web-based portal that provides users with global breaking news, local alerts, and weather updates. The portal delivers each user a personalized view by using mixture of static and dynamic content. Content is served over HTTPS through an API server running on an Amazon EC2 instance behind an Application Load Balancer (ALB). The company wants the portal to provide this content to its users across the world as quickly as possible. How should a solutions architect design the application to ensure the LEAST amount of latency for all users?

## Options

**A.** Deploy the application stack in a single AWS Region. Use Amazon CloudFront to serve all static and dynamic content by specifying the ALB as an origin.

**B.** Deploy the application stack in two AWS Regions. Use an Amazon Route 53 latency routing policy to serve all content from the ALB in the closest Region.

**C.** Deploy the application stack in a single AWS Region. Use Amazon CloudFront to serve the static content. Serve the dynamic content directly from the ALB.

**D.** Deploy the application stack in two AWS Regions. Use an Amazon Route 53 geolocation routing policy to serve all content from the ALB in the closest Region.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Global portal, static + dynamic content (personalized), HTTPS, ALB + EC2 backend.
- **Existing Resources:** ALB, EC2.
- **Current Issue/Goal:** Least latency for all users globally.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `users across the world` | Global audience |
| `static and dynamic content` | **CloudFront** hỗ trợ cả static (cache) và dynamic (forward to origin) |
| `least amount of latency` | Edge locations |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Global content delivery
- **Constraints:** Least latency, static + dynamic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **CloudFront** — edge locations gần user, cache static content, forward dynamic requests to ALB origin.
- **Single Region** cho backend — đơn giản, CloudFront xử lý global distribution.
- Dynamic content được加速 qua CloudFront optimized network.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Multi-Region + Route 53 latency — không có edge caching, user vẫn phải đi đến Region.

**❌ Đáp án C:**
- Dynamic content trực tiếp từ ALB — không được hưởng lợi từ CloudFront edge, latency cao.

**❌ Đáp án D:**
- Multi-Region + geolocation — complex, không cache ở edge.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront = global edge for static + dynamic. ALB origin. Single Region backend = simpler + fast"*
