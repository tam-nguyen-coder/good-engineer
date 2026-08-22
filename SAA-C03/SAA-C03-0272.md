# Question #272 - Topic 1

A company serves a dynamic website from a fleet of Amazon EC2 instances behind an Application Load Balancer (ALB). The website needs to support multiple languages to serve customers around the world. The website's architecture is running in the us-west-1 Region and is exhibiting high request latency for users that are located in other parts of the world. The website needs to serve requests quickly and efficiently regardless of a user's location. However, the company does not want to recreate the existing architecture across multiple Regions. What should a solutions architect do to meet these requirements?

## Options

**A.** Replace the existing architecture with a website that is served from an Amazon S3 bucket. Configure an Amazon CloudFront distribution with the S3 bucket as the origin. Set the cache behavior settings to cache based on the Accept-Language request header.

**B.** Configure an Amazon CloudFront distribution with the ALB as the origin. Set the cache behavior settings to cache based on the Accept-Language request header.

**C.** Create an Amazon API Gateway API that is integrated with the ALB. Configure the API to use the HTTP integration type. Set up an API Gateway stage to enable the API cache based on the Accept-Language request header.

**D.** Launch an EC2 instance in each additional Region and configure NGINX to act as a cache server for that Region. Put all the EC2 instances and the ALB behind an Amazon Route 53 record set with a geolocation routing policy.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Dynamic website, multi-language, global users, high latency outside us-west-1. Don't want to recreate across Regions.
- **Existing Resources:** EC2 + ALB in us-west-1.
- **Current Issue/Goal:** Global low latency with minimal infra changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `support multiple languages` | Cache based on **Accept-Language** header |
| `not recreate the existing architecture across multiple Regions` | Use **CloudFront** (single origin, edge caching) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** CDN / Global optimization
- **Constraints:** Dynamic content, multi-language, no multi-Region infra

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **CloudFront** với ALB origin — cache dynamic content tại edge.
- **Accept-Language** header — cache versions theo ngôn ngữ.
- Không cần recreate infrastructure ở multiple Regions.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 — không phù hợp cho dynamic website.

**❌ Đáp án C:**
- API Gateway — cho API, không phải website serving.

**❌ Đáp án D:**
- EC2 per Region — phải recreate infrastructure, trái yêu cầu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront + ALB = global edge caching for dynamic sites. Accept-Language = multi-language cache"*
