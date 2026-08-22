# Question #206 - Topic 1

A company wants to manage Amazon Machine Images (AMIs). The company currently copies AMIs to the same AWS Region where the AMIs were created. The company needs to design an application that captures AWS API calls and sends alerts whenever the Amazon EC2 CreateImage API operation is called within the company's account. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create an AWS Lambda function to query AWS CloudTrail logs and to send an alert when a CreateImage API call is detected.

**B.** Configure AWS CloudTrail with an Amazon Simple Notification Service (Amazon SNS) notification that occurs when updated logs are sent to Amazon S3. Use Amazon Athena to create a new table and to query on CreateImage when an API call is detected.

**C.** Create an Amazon EventBridge (Amazon CloudWatch Events) rule for the CreateImage API call. Configure the target as an Amazon Simple Notification Service (Amazon SNS) topic to send an alert when a CreateImage API call is detected.

**D.** Configure an Amazon Simple Queue Service (Amazon SQS) FIFO queue as a target for AWS CloudTrail logs. Create an AWS Lambda function to send an alert to an Amazon Simple Notification Service (Amazon SNS) topic when a CreateImage API call is detected.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Capture CreateImage API calls, send alerts. Least operational overhead.
- **Existing Resources:** AWS account.
- **Current Issue/Goal:** Event-driven alerting.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `captures AWS API calls` | **Amazon EventBridge** (real-time event bus) |
| `sends alerts` | **SNS topic** as target |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Monitoring / Events
- **Constraints:** Real-time, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **EventBridge rule** — match `CreateImage` API call, trigger in real-time.
- Configure **SNS topic** as target → send alert immediately.
- Không cần Lambda, polling, hay query logs → least overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda + CloudTrail query — polling, không real-time, overhead.

**❌ Đáp án B:**
- CloudTrail + SNS + Athena — periodic query, không real-time.

**❌ Đáp án D:**
- SQS FIFO + Lambda + SNS — nhiều components hơn cần thiết.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EventBridge rule → SNS = real-time API alerting. Lambda + CloudTrail = polling (more overhead)"*
