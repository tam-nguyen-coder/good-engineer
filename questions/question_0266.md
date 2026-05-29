# Question #266 - Topic 1

A company has a popular gaming platform running on AWS. The application is sensitive to latency because latency can impact the user experience and introduce unfair advantages to some players. The application is deployed in every AWS Region. It runs on Amazon EC2 instances that are part of Auto Scaling groups configured behind Application Load Balancers (ALBs). A solutions architect needs to implement a mechanism to monitor the health of the application and redirect traffic to healthy endpoints. Which solution meets these requirements?

## Options

**A.** Configure an accelerator in AWS Global Accelerator. Add a listener for the port that the application listens on, and attach it to a Regional endpoint in each Region. Add the ALB as the endpoint.

**B.** Create an Amazon CloudFront distribution and specify the ALB as the origin server. Configure the cache behavior to use origin cache headers. Use AWS Lambda functions to optimize the traffic.

**C.** Create an Amazon CloudFront distribution and specify Amazon S3 as the origin server. Configure the cache behavior to use origin cache headers. Use AWS Lambda functions to optimize the traffic.

**D.** Configure an Amazon DynamoDB database to serve as the data store for the application. Create a DynamoDB Accelerator (DAX) cluster to act as the in-memory cache for DynamoDB hosting the application data.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming platform (latency-sensitive), deployed in every Region. EC2 + ASG + ALB. Need health monitoring + traffic redirection.
- **Existing Resources:** ALBs in each Region.
- **Current Issue/Goal:** Global traffic routing + health checks.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sensitive to latency` | **Global Accelerator** (Anycast IP) |
| `monitor health... redirect traffic to healthy endpoints` | Global Accelerator health checks |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Global networking / Gaming
- **Constraints:** Low latency, health-based routing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Global Accelerator** — dùng Anycast IP, đưa traffic vào AWS edge gần user nhất → giảm latency.
- Health checks → tự động redirect traffic khỏi unhealthy endpoints.
- ALB làm Regional endpoint.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- CloudFront + Lambda — CloudFront cache có thể không phù hợp cho dynamic gaming content.

**❌ Đáp án C:**
- CloudFront + S3 — S3 không phải origin cho dynamic app.

**❌ Đáp án D:**
- DynamoDB + DAX — database caching, không phải global traffic routing.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Global Accelerator = low latency + health check routing. CloudFront = caching (better for static)"*
