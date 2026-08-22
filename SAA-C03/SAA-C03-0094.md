# Question #94 - Topic 1

A company is designing an application where users upload small files into Amazon S3. After a user uploads a file, the file requires one-time simple processing to transform the data and save the data in JSON format for later analysis. Each file must be processed as quickly as possible after it is uploaded. Demand will vary. On some days, users will upload a high number of files. On other days, users will upload a few files or no files. Which solution meets these requirements with the LEAST operational overhead?

## Options

**A.** Configure Amazon EMR to read text files from Amazon S3. Run processing scripts to transform the data. Store the resulting JSON file in an Amazon Aurora DB cluster.

**B.** Configure Amazon S3 to send an event notification to an Amazon Simple Queue Service (Amazon SQS) queue. Use Amazon EC2 instances to read from the queue and process the data. Store the resulting JSON file in Amazon DynamoDB.

**C.** Configure Amazon S3 to send an event notification to an Amazon Simple Queue Service (Amazon SQS) queue. Use an AWS Lambda function to read from the queue and process the data. Store the resulting JSON file in Amazon DynamoDB.

**D.** Configure Amazon EventBridge (Amazon CloudWatch Events) to send an event to Amazon Kinesis Data Streams when a new file is uploaded. Use an AWS Lambda function to consume the event from the stream and process the data. Store the resulting JSON file in an Amazon Aurora DB cluster.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Upload small files → S3 → process → JSON. Demand thay đổi (có thể zero).
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Process nhanh, scale to zero, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `processed as quickly as possible` | Event-driven processing |
| `Demand will vary` | Có thể zero traffic → scale to zero |
| `least operational overhead` | Serverless |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Event-driven processing + Operational efficiency
- **Constraints:** Quick processing, variable demand

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **S3 event → SQS queue** — durable, decoupled.
- **Lambda** — serverless, scale tự động, scale to zero khi không có files.
- **DynamoDB** — lưu JSON, serverless, không cần quản lý.
- Toàn bộ serverless → **least operational overhead**.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **EMR** — overkill cho "simple processing", operational overhead cao.

**❌ Đáp án B:**
- **EC2** — phải quản lý instances, không scale to zero, overhead cao.

**❌ Đáp án D:**
- **EventBridge + Kinesis** — phức tạp hơn S3 + SQS cho use case này.
- Aurora có operational overhead hơn DynamoDB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 → SQS → Lambda = serverless processing pipeline. Scale to zero, pay per use"*
