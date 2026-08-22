# Question #358 - Topic 1

A social media company runs its application on Amazon EC2 instances behind an Application Load Balancer (ALB). The ALB is the origin for an Amazon CloudFront distribution. The application has more than a billion images stored in an Amazon S3 bucket and processes thousands of images each second. The company wants to resize the images dynamically and serve appropriate formats to clients. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Install an external image management library on an EC2 instance. Use the image management library to process the images.

**B.** Create a CloudFront origin request policy. Use the policy to automatically resize images and to serve the appropriate format based on the User-Agent HTTP header in the request.

**C.** Use a Lambda@Edge function with an external image management library. Associate the Lambda@Edge function with the CloudFront behaviors that serve the images.

**D.** Create a CloudFront response headers policy. Use the policy to automatically resize images and to serve the appropriate format based on the User-Agent HTTP header in the request.

## 1. CONTEXT & ĐỀ BÁI
- **Scenario:** Billions of images in S3, thousands processed/sec. Need dynamic resize + format conversion. CloudFront + ALB + EC2.
- **Existing Resources:** S3 bucket (images), CloudFront, ALB, EC2.
- **Current Issue/Goal:** Dynamic image processing at edge, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `resize images dynamically` | Cần compute tại edge để xử lý images theo request. |
| `serve appropriate formats` | Format conversion (WebP, AVIF) based on client capabilities. |
| `Lambda@Edge` | Run code at CloudFront edge locations → process images near users. |
| `least operational overhead` | Lambda@Edge serverless, không cần quản lý server farm. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Dynamic image resize/format, billions of images, thousands/sec

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Lambda@Edge: chạy code tại CloudFront edge locations, gần users → low latency.
- Image management library trong Lambda: resize và format conversion dựa trên User-Agent (VD: WebP cho Chrome).
- Serverless → không cần quản lý EC2 image processing fleet → operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 with image library: cần quản lý instances, scaling → operational overhead cao.

**❌ Đáp án B:**
- CloudFront origin request policy: chỉ modify request headers, không thể resize images hay convert format.

**❌ Đáp án D:**
- CloudFront response headers policy: chỉ modify response headers, không thể xử lý images.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Dynamic image processing at edge → Lambda@Edge (serverless). EC2 = operational overhead. Request/Response policy = không xử lý được."*
