# Question #257 - Topic 1

A company is building a solution that will report Amazon EC2 Auto Scaling events across all the applications in an AWS account. The company needs to use a serverless solution to store the EC2 Auto Scaling status data in Amazon S3. The company then will use the data in Amazon S3 to provide near-real-time updates in a dashboard. The solution must not affect the speed of EC2 instance launches. How should the company move the data to Amazon S3 to meet these requirements?

## Options

**A.** Use an Amazon CloudWatch metric stream to send the EC2 Auto Scaling status data to Amazon Kinesis Data Firehose. Store the data in Amazon S3.

**B.** Launch an Amazon EMR cluster to collect the EC2 Auto Scaling status data and send the data to Amazon Kinesis Data Firehose. Store the data in Amazon S3.

**C.** Create an Amazon EventBridge rule to invoke an AWS Lambda function on a schedule. Configure the Lambda function to send the EC2 Auto Scaling status data directly to Amazon S3.

**D.** Use a bootstrap script during the launch of an EC2 instance to install Amazon Kinesis Agent. Configure Kinesis Agent to collect the EC2 Auto Scaling status data and send the data to Amazon Kinesis Data Firehose. Store the data in Amazon S3.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Report EC2 Auto Scaling events, serverless → S3, near-real-time dashboard. Must not affect instance launch speed.
- **Existing Resources:** EC2 Auto Scaling groups.
- **Current Issue/Goal:** Streaming Auto Scaling metrics to S3.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `serverless solution` | Không EC2, EMR cluster |
| `near-real-time` | **CloudWatch metric stream** + **Firehose** |
| `must not affect the speed of EC2 instance launches` | Không dùng bootstrap scripts |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Monitoring / Streaming
- **Constraints:** Serverless, near-real-time, no impact on launches

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **CloudWatch metric stream** — stream Auto Scaling metrics continuously.
- **Kinesis Data Firehose** → **S3** — near-real-time delivery.
- Serverless (no EC2/EMR).
- Không ảnh hưởng đến instance launches.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- EMR cluster — không serverless, operational overhead.

**❌ Đáp án C:**
- EventBridge scheduled Lambda — polling-based, không near-real-time.

**❌ Đáp án D:**
- Bootstrap script + Kinesis Agent — ảnh hưởng launch speed, không serverless.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudWatch metric stream + Firehose = near-real-time, serverless. Bootstrap = affects launch"*
