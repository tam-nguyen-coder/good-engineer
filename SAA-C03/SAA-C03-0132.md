# Question #132 - Topic 1

A company’s website provides users with downloadable historical performance reports. The website needs a solution that will scale to meet the company’s website demands globally. The solution should be cost-effective, limit the provisioning of infrastructure resources, and provide the fastest possible response time. Which combination should a solutions architect recommend to meet these requirements?

## Options

**A.** Amazon CloudFront and Amazon S3

**B.** AWS Lambda and Amazon DynamoDB

**C.** Application Load Balancer with Amazon EC2 Auto Scaling

**D.** Amazon Route 53 with internal Application Load Balancers

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Website với downloadable reports (static files), global demand, cost-effective, fast response.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Global static content delivery.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `scale globally` | Cần **CloudFront** edge locations |
| `fastest possible response time` | CDN cache gần user |
| `limit the provisioning of infrastructure resources` | Serverless — S3 + CloudFront |
| `downloadable historical performance reports` | Static files |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Content delivery + Cost optimization
- **Constraints:** Global, fast, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3** — store static reports, cost-effective, scalable.
- **CloudFront** — CDN global, cache tại edge, fastest response.
- No servers to provision → limit infrastructure resources.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Lambda + DynamoDB — dynamic compute/DB, overkill cho static file serving.

**❌ Đáp án C:**
- ALB + EC2 — operational overhead, không global.

**❌ Đáp án D:**
- Route 53 + internal ALB — internal only, không public global.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 + CloudFront = static content global delivery. No servers = cost-effective + fast"*
