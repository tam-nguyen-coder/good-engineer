# Question #441 - Topic 1

A company hosts a multi-tier web application on Amazon Linux Amazon EC2 instances behind an Application Load Balancer. The instances run in an Auto Scaling group across multiple Availability Zones. The company observes that the Auto Scaling group launches more On-Demand Instances when the application's end users access high volumes of static web content. The company wants to optimize cost. What should a solutions architect do to redesign the application MOST cost-effectively?

## Options

**A.** Update the Auto Scaling group to use Reserved Instances instead of On-Demand Instances.

**B.** Update the Auto Scaling group to scale by launching Spot Instances instead of On-Demand Instances.

**C.** Create an Amazon CloudFront distribution to host the static web contents from an Amazon S3 bucket.

**D.** Create an AWS Lambda function behind an Amazon API Gateway API to host the static website contents.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-tier web app on EC2 + ALB + ASG. High static content volume → more instances launched. Optimize cost.
- **Existing Resources:** EC2, ALB, ASG across AZs.
- **Current Issue/Goal:** Reduce cost from static content driving instance scaling.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `static web content` | Offload to CloudFront + S3 → giảm tải cho EC2. |
| `launches more On-Demand Instances` | Static content không cần compute, nên dùng CDN. |
| `most cost-effectively` | CloudFront + S3: pay per request, không cần EC2 cho static. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Reduce cost from static content scaling

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- CloudFront: CDN cache static content at edge → giảm request đến EC2.
- S3: lưu static content (images, CSS, JS), cost rất thấp.
- EC2 instances: chỉ phục vụ dynamic content → ASG scale ít hơn, giảm cost.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Reserved Instances: giảm giá On-Demand nhưng vẫn trả cho EC2 xử lý static content. Không giải quyết root cause.

**❌ Đáp án B:**
- Spot Instances: rẻ hơn On-Demand nhưng static content vẫn chạy trên EC2. Risk bị interrupt.

**❌ Đáp án D:**
- Lambda + API Gateway: không tối ưu cho static content hosting (Lambda có giới hạn payload).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Static content cost optimization → CloudFront + S3. Không throw compute vào static."*