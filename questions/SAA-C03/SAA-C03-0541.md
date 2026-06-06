# Question #541 - Topic 1

A company wants to build a web application on AWS. Client access requests to the website are not predictable and can be idle for a long time. Only customers who have paid a subscription fee can have the ability to sign in and use the web application. Which combination of steps will meet these requirements MOST cost-effectively? (Choose three.)

## Options

**A.** Create an AWS Lambda function to retrieve user information from Amazon DynamoDB. Create an Amazon API Gateway endpoint to accept RESTful APIs. Send the API calls to the Lambda function.

**B.** Create an Amazon Elastic Container Service (Amazon ECS) service behind an Application Load Balancer to retrieve user information from Amazon RDS. Create an Amazon API Gateway endpoint to accept RESTful APIs. Send the API calls to the Lambda function.

**C.** Create an Amazon Cognito user pool to authenticate users.

**D.** Create an Amazon Cognito identity pool to authenticate users.

**E.** Use AWS Amplify to serve the frontend web content with HTML, CSS, and JS. Use an integrated Amazon CloudFront configuration. F. Use Amazon S3 static web hosting with PHP, CSS, and JS. Use Amazon CloudFront to serve the frontend web content.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty muốn xây dựng web application trên AWS. Lưu lượng truy cập không thể dự đoán trước và có thể idle trong thời gian dài. Chỉ khách hàng trả phí mới có thể đăng nhập và sử dụng ứng dụng.
- **Existing Resources:** Chưa có tài nguyên nào trên AWS.
- **Current Issue/Goal:** Xây dựng giải pháp tiết kiệm chi phí nhất, hỗ trợ truy cập không dự đoán được, và yêu cầu xác thực người dùng.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `not predictable` | Không thể dự đoán, cần serverless để tự động scale |
| `idle for a long time` | Có thể không có traffic trong thời gian dài → serverless không tốn chi phí khi idle |
| `paid a subscription fee` | Cần xác thực người dùng (authentication) |
| `MOST cost-effectively` | Chi phí thấp nhất có thể |
| `sign in` | Cần chức năng đăng nhập → authentication |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective (multi-select: 3 answers)
- **Constraints:** Phải hỗ trợ authentication cho subscribed users, chi phí tối thiểu

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, C, E**

**Giải thích:**
- **A (Lambda + DynamoDB + API Gateway):** Serverless stack hoàn toàn, tự động scale theo nhu cầu, không tốn chi phí khi idle. DynamoDB phù hợp với key-value lookup cho user info.
- **C (Cognito user pool):** Dùng để xác thực người dùng (authentication). User pool quản lý đăng nhập, đăng ký, và xác thực danh tính người dùng đã trả phí. Identity pool (D) dùng để cấp AWS credentials tạm thời, không phải để authenticate.
- **E (Amplify + CloudFront):** Amplify cung cấp hosting cho frontend tĩnh (HTML, CSS, JS) với CI/CD tích hợp. CloudFront CDN giảm latency. S3 static hosting (F) không hỗ trợ PHP.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (ECS + ALB + RDS):** Chi phí cao hơn nhiều so với serverless. ECS và ALB tốn chi phí ngay cả khi idle. RDS cũng tốn chi phí duy trì.

**❌ Đáp án D (Cognito identity pool):** Identity pool dùng để cấp AWS credentials tạm thời cho người dùng đã được xác thực (federated identities), không phải để xác thực. Cần user pool trước, sau đó dùng identity pool nếu cần truy cập AWS resources.

**❌ Đáp án F (S3 static hosting + PHP):** S3 static website hosting chỉ hỗ trợ nội dung tĩnh (HTML, CSS, JS), không hỗ trợ PHP (dynamic content). Amplify (E) là lựa chọn phù hợp hơn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Serverless for unpredictable traffic: API Gateway + Lambda + DynamoDB. Cognito User Pool = authentication, Identity Pool = AWS credentials. Amplify = frontend hosting with CI/CD."*
