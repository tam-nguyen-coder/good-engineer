# Question #447 - Topic 1

A company has a stateless web application that runs on AWS Lambda functions that are invoked by Amazon API Gateway. The company wants to deploy the application across multiple AWS Regions to provide Regional failover capabilities. What should a solutions architect do to route traffic to multiple Regions?

## Options

**A.** Create Amazon Route 53 health checks for each Region. Use an active-active failover configuration.

**B.** Create an Amazon CloudFront distribution with an origin for each Region. Use CloudFront health checks to route traffic.

**C.** Create a transit gateway. Attach the transit gateway to the API Gateway endpoint in each Region. Configure the transit gateway to route requests.

**D.** Create an Application Load Balancer in the primary Region. Set the target group to point to the API Gateway endpoint hostnames in each Region.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Stateless web app: API Gateway + Lambda. Deploy across Regions for failover.
- **Existing Resources:** API Gateway, Lambda.
- **Current Issue/Goal:** Route traffic across multiple Regions.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `multiple AWS Regions` | Cross-region traffic routing. |
| `Regional failover` | Route 53 active-active with health checks. |
| `stateless` | Any Region can handle any request. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Global / DNS routing
- **Constraints:** Multi-Region failover for API Gateway + Lambda

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Route 53 active-active: traffic routed to all healthy Regions.
- Health checks: monitor API Gateway endpoints in each Region.
- If one Region fails → Route 53 stops routing traffic to that Region.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- CloudFront: designed for content delivery with caching. API Gateway + Lambda là API, không phải static content.
- CloudFront "health checks" không phải built-in feature như Route 53.

**❌ Đáp án C:**
- Transit Gateway: kết nối VPCs với nhau, không phải DNS/HTTP routing.

**❌ Đáp án D:**
- ALB target group: không thể point đến API Gateway endpoint hostnames (ALB targets: EC2, IP, Lambda, not API Gateway).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-Region API routing → Route 53 active-active + health checks. CloudFront = CDN, not API routing."*