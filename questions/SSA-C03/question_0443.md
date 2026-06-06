# Question #443 - Topic 1

A company wants to host a scalable web application on AWS. The application will be accessed by users from different geographic regions of the world. Application users will be able to download and upload unique data up to gigabytes in size. The development team wants a cost-effective solution to minimize upload and download latency and maximize performance. What should a solutions architect do to accomplish this?

## Options

**A.** Use Amazon S3 with Transfer Acceleration to host the application.

**B.** Use Amazon S3 with CacheControl headers to host the application.

**C.** Use Amazon EC2 with Auto Scaling and Amazon CloudFront to host the application.

**D.** Use Amazon EC2 with Auto Scaling and Amazon ElastiCache to host the application.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Global web app, upload/download GBs of data. Minimize latency, maximize performance. Cost-effective.
- **Existing Resources:** N/A.
- **Current Issue/Goal:** Global low-latency web app with large data transfers.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `different geographic regions` | CloudFront: edge caching, global distribution. |
| `minimize latency` | CloudFront edge locations. |
| `upload and download unique data` | CloudFront hỗ trợ upload (PUT/POST) qua edge. |
| `cost-effective` | CloudFront giảm tải cho origin + S3 làm origin storage. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance / Global
- **Constraints:** Global users, GB data, low latency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- EC2 + ASG: compute layer cho application logic, auto scale.
- CloudFront: CDN ở edge locations → cache content gần user → giảm latency.
- CloudFront hỗ trợ cả upload (PUT/POST) và download (GET).
- Kết hợp S3 làm origin storage cho durable data.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3: lưu trữ, không host web application. Transfer Acceleration: tăng tốc upload nhưng không phải CDN.

**❌ Đáp án B:**
- CacheControl headers: client-side caching, không giải quyết global latency.

**❌ Đáp án D:**
- ElastiCache: caching layer, không giảm latency global. Chỉ hữu ích trong cùng Region.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Global low latency = CloudFront (edge) + EC2/ASG (compute). S3 alone không phải web host."*