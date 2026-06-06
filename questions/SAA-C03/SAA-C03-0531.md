# Question #531 - Topic 1

A company needs to integrate with a third-party data feed. The data feed sends a webhook to notify an external service when new data is ready for consumption. A developer wrote an AWS Lambda function to retrieve data when the company receives a webhook callback. The developer must make the Lambda function available for the third party to call. Which solution will meet these requirements with the MOST operational efficiency?

## Options

**A.** Create a function URL for the Lambda function. Provide the Lambda function URL to the third party for the webhook.

**B.** Deploy an Application Load Balancer (ALB) in front of the Lambda function. Provide the ALB URL to the third party for the webhook.

**C.** Create an Amazon Simple Notification Service (Amazon SNS) topic. Attach the topic to the Lambda function. Provide the public hostname of the SNS topic to the third party for the webhook.

**D.** Create an Amazon Simple Queue Service (Amazon SQS) queue. Attach the queue to the Lambda function. Provide the public hostname of the SQS queue to the third party for the webhook.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Third-party gửi webhook để trigger Lambda function. Cần expose Lambda cho third-party gọi.
- **Existing Resources:** Lambda function đã viết sẵn.
- **Current Issue/Goal:** Expose Lambda cho webhook với operational efficiency cao nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `webhook` | HTTP(S) callback, third-party gọi URL |
| `Lambda function URL` | HTTPS endpoint built-in cho Lambda, không cần API Gateway hay ALB |
| `most operational efficiency` | Dùng Lambda function URL → đơn giản nhất, không cần thêm service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operational efficiency
- **Constraints:** Third-party webhook HTTP(S) call

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Lambda function URL là tính năng built-in, tạo HTTPS endpoint trực tiếp cho Lambda function.
- Không cần API Gateway, ALB, hay bất kỳ service nào khác.
- URL format: `https://<url-id>.lambda-url.<region>.on.aws/`.
- Có thể cấu hình auth (AWS_IAM hoặc NONE).
- Operational efficiency cao nhất: 1 click tạo URL, không cần quản lý thêm infrastructure.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ALB trước Lambda: phức tạp hơn, cần tạo ALB, target group, listener rules.
- Chi phí cao hơn, operational overhead lớn hơn.

**❌ Đáp án C:**
- SNS topic không phải HTTP endpoint để third-party gọi webhook.
- SNS hỗ trợ HTTP/HTTPS subscription, nhưng cần third-party support SNS protocol, không phải webhook callback thông thường.

**❌ Đáp án D:**
- SQS queue không phải HTTP endpoint.
- Third-party không thể gửi webhook trực tiếp đến SQS queue URL (SQS không hỗ trợ HTTP POST từ external).

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"Lambda function URL = HTTPS endpoint built-in, không cần API Gateway/ALB. Webhook đơn giản nhất."*
