# Question #226 - Topic 1

A company collects data from thousands of remote devices by using a RESTful web services application that runs on an Amazon EC2 instance. The EC2 instance receives the raw data, transforms the raw data, and stores all the data in an Amazon S3 bucket. The number of remote devices will increase into the millions soon. The company needs a highly scalable solution that minimizes operational overhead. Which combination of steps should a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Use AWS Glue to process the raw data in Amazon S3.

**B.** Use Amazon Route 53 to route traffic to different EC2 instances.

**C.** Add more EC2 instances to accommodate the increasing amount of incoming data.

**D.** Send the raw data to Amazon Simple Queue Service (Amazon SQS). Use EC2 instances to process the data.

**E.** Use Amazon API Gateway to send the raw data to an Amazon Kinesis data stream. Configure Amazon Kinesis Data Firehose to use the data stream as a source to deliver the data to Amazon S3.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Single EC2 receives data from thousands of devices → transform → S3. Will grow to millions. Need scalable, min overhead.
- **Existing Resources:** Single EC2 instance.
- **Current Issue/Goal:** Serverless ingestion + ETL.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highly scalable solution` | Replace single EC2 with serverless |
| `minimizes operational overhead` | **API Gateway + Kinesis + Firehose** |
| `transforms the raw data` | **AWS Glue** for transformation |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless / Data ingestion
- **Constraints:** Chọn 2, scalable, min overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và E**

**Giải thích:**
- **E: API Gateway + Kinesis + Firehose → S3** — serverless ingestion, thay thế single EC2.
- **A: AWS Glue** — serverless ETL, thay thế transformation trên EC2.
- Cả 2 đều serverless → scalable, min overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Route 53 — DNS, không giải quyết scaling của EC2.

**❌ Đáp án C:**
- More EC2 — vẫn operational overhead.

**❌ Đáp án D:**
- SQS + EC2 — vẫn cần quản lý EC2.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API Gateway + Kinesis + Firehose = serverless ingestion. Glue = serverless ETL. EC2 = more overhead"*
