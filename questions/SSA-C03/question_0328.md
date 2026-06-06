# Question #328 - Topic 1

A company is hosting a three-tier ecommerce application in the AWS Cloud. The company hosts the website on Amazon S3 and integrates the website with an API that handles sales requests. The company hosts the API on three Amazon EC2 instances behind an Application Load Balancer (ALB). The API consists of static and dynamic front-end content along with backend workers that process sales requests asynchronously. The company is expecting a significant and sudden increase in the number of sales requests during events for the launch of new products. What should a solutions architect recommend to ensure that all the requests are processed successfully?

## Options

**A.** Add an Amazon CloudFront distribution for the dynamic content. Increase the number of EC2 instances to handle the increase in traffic.

**B.** Add an Amazon CloudFront distribution for the static content. Place the EC2 instances in an Auto Scaling group to launch new instances based on network traffic.

**C.** Add an Amazon CloudFront distribution for the dynamic content. Add an Amazon ElastiCache instance in front of the ALB to reduce traffic for the API to handle.

**D.** Add an Amazon CloudFront distribution for the static content. Add an Amazon Simple Queue Service (Amazon SQS) queue to receive requests from the website for later processing by the EC2 instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Three-tier ecommerce: S3 website → API (ALB + 3 EC2) → backend workers async. Expecting sudden traffic spikes for product launches. Need to ensure all requests processed.
- **Existing Resources:** S3 website, ALB, 3 EC2 instances, async backend workers.
- **Current Issue/Goal:** Handle sudden traffic spikes, ensure no request loss.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sudden increase` | Traffic spike → cần buffering (SQS) và CDN cho static content. |
| `static and dynamic front-end content` | Static → CloudFront cache. Dynamic → ALB + EC2. |
| `process sales requests asynchronously` | Đã async → SQS queue sẽ buffer requests khi backend quá tải. |
| `ensure that all the requests are processed` | SQS persist requests → không mất. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Ensure all requests processed during traffic spikes
- **Constraints:** Sudden increase, already async workers

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- CloudFront cho static content: cache tại edge, giảm load lên S3 origin.
- SQS queue: buffer sales requests → khi traffic spike, requests được queue lại và backend workers xử lý dần. Không mất requests.
- S3 website + CloudFront static content + SQS cho async processing.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFront cho dynamic content không cache được (API responses thay đổi). Chỉ tăng EC2 instances = manual scaling, không đảm bảo.

**❌ Đáp án B:**
- Auto Scaling EC2 giúp scale compute nhưng thiếu buffer layer → requests có thể bị drop nếu scale chưa kịp.

**❌ Đáp án C:**
- CloudFront cho dynamic content không hiệu quả. ElastiCache trước ALB không phải design chuẩn (ElastiCache là database cache, không phải request buffer).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Traffic spike + async workers → SQS buffer + CloudFront static cache. Không cần cache dynamic content."*
