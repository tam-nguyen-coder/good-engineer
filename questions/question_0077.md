# Question #77 - Topic 1

A company needs to configure a real-time data ingestion architecture for its application. The company needs an API, a process that transforms data as the data is streamed, and a storage solution for the data. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Deploy an Amazon EC2 instance to host an API that sends data to an Amazon Kinesis data stream. Create an Amazon Kinesis Data Firehose delivery stream that uses the Kinesis data stream as a data source. Use AWS Lambda functions to transform the data. Use the Kinesis Data Firehose delivery stream to send the data to Amazon S3.

**B.** Deploy an Amazon EC2 instance to host an API that sends data to AWS Glue. Stop source/destination checking on the EC2 instance. Use AWS Glue to transform the data and to send the data to Amazon S3.

**C.** Configure an Amazon API Gateway API to send data to an Amazon Kinesis data stream. Create an Amazon Kinesis Data Firehose delivery stream that uses the Kinesis data stream as a data source. Use AWS Lambda functions to transform the data. Use the Kinesis Data Firehose delivery stream to send the data to Amazon S3.

**D.** Configure an Amazon API Gateway API to send data to AWS Glue. Use AWS Lambda functions to transform the data. Use AWS Glue to send the data to Amazon S3.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Real-time data ingestion: cần API + stream transformation + storage.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Real-time ingestion, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `real-time data ingestion` | Cần **Kinesis** streaming |
| `transforms data as the data is streamed` | Lambda + Firehose transformation |
| `least operational overhead` | Serverless, không EC2 |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Real-time streaming + Operational efficiency
- **Constraints:** API, stream transform, storage

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **API Gateway** — managed API, không cần EC2.
- **Kinesis Data Streams** — real-time data ingestion.
- **Kinesis Data Firehose** — automatically load data vào S3, với **Lambda** để transform.
- Tất cả đều serverless — **least operational overhead**.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 để host API — operational overhead (quản lý OS, patching, scaling).

**❌ Đáp án B:**
- **AWS Glue** là ETL batch, không phải real-time streaming.
- EC2 + Glue — operational overhead cao.

**❌ Đáp án D:**
- API Gateway → Glue — không hỗ trợ real-time streaming (Glue là batch).
- Glue không phải streaming destination cho API Gateway.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API Gateway + Kinesis + Firehose + Lambda = serverless real-time ingestion pipeline"*
