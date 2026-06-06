# Question #345 - Topic 1

A company wants to restrict access to the content of one of its main web applications and to protect the content by using authorization techniques available on AWS. The company wants to implement a serverless architecture and an authentication solution for fewer than 100 users. The solution needs to integrate with the main web application and serve web content globally. The solution must also scale as the company's user base grows while providing the lowest login latency possible. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Use Amazon Cognito for authentication. Use Lambda@Edge for authorization. Use Amazon CloudFront to serve the web application globally.

**B.** Use AWS Directory Service for Microsoft Active Directory for authentication. Use AWS Lambda for authorization. Use an Application Load Balancer to serve the web application globally.

**C.** Use Amazon Cognito for authentication. Use AWS Lambda for authorization. Use Amazon S3 Transfer Acceleration to serve the web application globally.

**D.** Use AWS Directory Service for Microsoft Active Directory for authentication. Use Lambda@Edge for authorization. Use AWS Elastic Beanstalk to serve the web application globally.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app, serverless, <100 users, global content, lowest login latency, cost-effective, scalable.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Auth + authorization + global content delivery, serverless.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `serverless architecture` | Cognito (auth), Lambda@Edge, CloudFront. |
| `fewer than 100 users` | Cognito free tier (50,000 MAU). |
| `serve web content globally` | CloudFront CDN (edge locations). |
| `lowest login latency possible` | Lambda@Edge chạy tại CloudFront edge → xác thực gần user. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Serverless, <100 users, global, low latency login

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Amazon Cognito: serverless auth, free for <50,000 MAU → cost-effective.
- Lambda@Edge: chạy authorization code tại CloudFront edge locations → lowest latency.
- CloudFront: serve web content globally từ edge.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Directory Service (Managed AD) đắt hơn Cognito. ALB không phải global CDN.

**❌ Đáp án C:**
- S3 Transfer Acceleration cải thiện upload speed, không serve web app globally. Lambda (central Region) có latency cao hơn Lambda@Edge.

**❌ Đáp án D:**
- Directory Service (AD) đắt hơn Cognito. Elastic Beanstalk không global bằng CloudFront.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Serverless global web + low latency login → Cognito + Lambda@Edge + CloudFront. AD = đắt, ALB = không global."*
