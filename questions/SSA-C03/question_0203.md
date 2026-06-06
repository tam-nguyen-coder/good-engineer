# Question #203 - Topic 1

The customers of a finance company request appointments with financial advisors by sending text messages. A web application that runs on Amazon EC2 instances accepts the appointment requests. The text messages are published to an Amazon Simple Queue Service (Amazon SQS) queue through the web application. Another application that runs on EC2 instances then sends meeting invitations and meeting confirmation email messages to the customers. After successful scheduling, this application stores the meeting information in an Amazon DynamoDB database. As the company expands, customers report that their meeting invitations are taking longer to arrive. What should a solutions architect recommend to resolve this issue?

## Options

**A.** Add a DynamoDB Accelerator (DAX) cluster in front of the DynamoDB database.

**B.** Add an Amazon API Gateway API in front of the web application that accepts the appointment requests.

**C.** Add an Amazon CloudFront distribution. Set the origin as the web application that accepts the appointment requests.

**D.** Add an Auto Scaling group for the application that sends meeting invitations. Configure the Auto Scaling group to scale based on the depth of the SQS queue.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app → SQS → processing app → DynamoDB. Invitations arriving slowly as company grows.
- **Existing Resources:** EC2 web app, SQS, EC2 processing app, DynamoDB.
- **Current Issue/Goal:** Backend processing bottleneck — need to scale consumers.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `taking longer to arrive` | Consumer (processing app) không đủ capacity |
| `expand` | Cần **Auto Scaling** cho consumer |
| `depth of the SQS queue` | Metric phù hợp để scale |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Scaling / Messaging
- **Constraints:** Resolve slow processing, scale consumers

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- SQS queue depth tăng → consumer không đủ nhanh.
- **Auto Scaling group** cho processing application scale dựa trên **SQS queue depth** → tự động thêm instances.
- CloudWatch metric `ApproximateNumberOfMessagesVisible` → scale threshold.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DAX — cải thiện read performance của DynamoDB, không giải quyết processing bottleneck.

**❌ Đáp án B:**
- API Gateway — cho front-end, không giúp scale backend processing.

**❌ Đáp án C:**
- CloudFront — CDN, không liên quan.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS queue depth + ASG = scale consumers. DAX = DB cache. API Gateway/CloudFront = frontend"*
