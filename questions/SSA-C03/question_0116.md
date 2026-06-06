# Question #116 - Topic 1

A company uses a popular content management system (CMS) for its corporate website. However, the required patching and maintenance are burdensome. The company is redesigning its website and wants anew solution. The website will be updated four times a year and does not need to have any dynamic content available. The solution must provide high scalability and enhanced security. Which combination of changes will meet these requirements with the LEAST operational overhead? (Choose two.)

## Options

**A.** Configure Amazon CloudFront in front of the website to use HTTPS functionality.

**B.** Deploy an AWS WAF web ACL in front of the website to provide HTTPS functionality.

**C.** Create and deploy an AWS Lambda function to manage and serve the website content.

**D.** Create the new website and an Amazon S3 bucket. Deploy the website on the S3 bucket with static website hosting enabled.

**E.** Create the new website. Deploy the website by using an Auto Scaling group of Amazon EC2 instances behind an Application Load Balancer.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CMS website → chuyển sang static site (update 4x/năm, no dynamic content).
- **Existing Resources:** CMS website.
- **Current Issue/Goal:** High scalability, enhanced security, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `does not need to have any dynamic content` | **S3 static website hosting** |
| `enhanced security` | **CloudFront** (HTTPS, DDoS protection) |
| `least operational overhead` | Serverless, no patching |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Web hosting + Security
- **Constraints:** Chọn 2, static, scalable, secure

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và D**

**Giải thích:**
- **D: S3 static website hosting** — không cần server, không patching, scale tự động, giá rẻ.
- **A: CloudFront** — CDN phía trước S3, cung cấp HTTPS, DDoS protection, low latency global.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **WAF** provides security (block SQL injection, XSS) nhưng **không cung cấp HTTPS**. WAF + CloudFront mới đúng.

**❌ Đáp án C:**
- Lambda serve content — không phù hợp (Lambda trả về response qua API Gateway, không phải web server).

**❌ Đáp án E:**
- EC2 ASG + ALB — operational overhead (patching, maintenance), không cần thiết cho static site.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 + CloudFront = static website best practice. No servers = no patching = least overhead"*
