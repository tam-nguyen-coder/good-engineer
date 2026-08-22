# Question #75 - Topic 1

A company wants to move a multi-tiered application from on premises to the AWS Cloud to improve the application's performance. The application consists of application tiers that communicate with each other by way of RESTful services. Transactions are dropped when one tier becomes overloaded. A solutions architect must design a solution that resolves these issues and modernizes the application. Which solution meets these requirements and is the MOST operationally efficient?

## Options

**A.** Use Amazon API Gateway and direct transactions to the AWS Lambda functions as the application layer. Use Amazon Simple Queue Service (Amazon SQS) as the communication layer between application services.

**B.** Use Amazon CloudWatch metrics to analyze the application performance history to determine the servers' peak utilization during the performance failures. Increase the size of the application server's Amazon EC2 instances to meet the peak requirements.

**C.** Use Amazon Simple Notification Service (Amazon SNS) to handle the messaging between application servers running on Amazon EC2 in an Auto Scaling group. Use Amazon CloudWatch to monitor the SNS queue length and scale up and down as required.

**D.** Use Amazon Simple Queue Service (Amazon SQS) to handle the messaging between application servers running on Amazon EC2 in an Auto Scaling group. Use Amazon CloudWatch to monitor the SQS queue length and scale up when communication failures are detected.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-tier app với RESTful services, transactions bị drop khi overload.
- **Existing Resources:** On-prem multi-tier application.
- **Current Issue/Goal:** Chống drop transactions, modernize, most operationally efficient.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Transactions are dropped when one tier becomes overloaded` | Cần **queue** để decouple và buffer |
| `modernizes the application` | Serverless (API Gateway + Lambda) |
| `most operationally efficient` | Managed serverless services |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Application modernization
- **Constraints:** Chống dropped transactions, operational efficiency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **API Gateway + Lambda** — serverless, tự động scale, không quản lý server.
- **SQS** — decouple các tiers, buffer requests khi backend overload → không bị dropped.
- **MOST operationally efficient** — không cần quản lý EC2, ASG, patching, v.v.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Chỉ tăng size EC2 instances — reactive, không giải quyết root cause (không buffer).
- Không "modernize" — vẫn là EC2.

**❌ Đáp án C:**
- **SNS** là pub/sub, không phải message queue — không buffer được requests. Subscribers phải available để nhận.
- SNS không có "queue length" metric (SNS là topic, không phải queue).

**❌ Đáp án D:**
- SQS + EC2 ASG — đúng cho decoupling nhưng vẫn dùng EC2 (operational overhead cao hơn serverless).
- "Scale up when communication failures are detected" — reactive, không proactive.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS = buffer + decouple. SNS = push notification (no buffer). Lambda + API Gateway = serverless modernize"*
