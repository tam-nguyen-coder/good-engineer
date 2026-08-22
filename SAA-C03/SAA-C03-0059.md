# Question #59 - Topic 1

A company hosts more than 300 global websites and applications. The company requires a platform to analyze more than 30 TB of clickstream data each day. What should a solutions architect do to transmit and process the clickstream data?

## Options

**A.** Design an AWS Data Pipeline to archive the data to an Amazon S3 bucket and run an Amazon EMR cluster with the data to generate analytics.

**B.** Create an Auto Scaling group of Amazon EC2 instances to process the data and send it to an Amazon S3 data lake for Amazon Redshift to use for analysis.

**C.** Cache the data to Amazon CloudFront. Store the data in an Amazon S3 bucket. When an object is added to the S3 bucket. run an AWS Lambda function to process the data for analysis.

**D.** Collect the data from Amazon Kinesis Data Streams. Use Amazon Kinesis Data Firehose to transmit the data to an Amazon S3 data lake. Load the data in Amazon Redshift for analysis.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 300+ global sites, 30TB clickstream data/day, cần transmit + process.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Streaming analytics pipeline cho lượng dữ liệu lớn.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `30 TB of clickstream data each day` | Lượng dữ liệu streaming lớn — cần Kinesis |
| `transmit and process` | Cần ingestion + processing |
| `clickstream data` | Real-time event data |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data ingestion + analytics
- **Constraints:** 30TB/day, global, real-time

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Kinesis Data Streams** — ingest clickstream data real-time từ 300+ sites.
- **Kinesis Data Firehose** — tự động load data vào S3 data lake (không cần quản lý).
- **Amazon Redshift** — analytics trên S3 data lake (Redshift Spectrum) hoặc direct load.
- Đây là kiến trúc streaming analytics chuẩn, serverless, scale tốt cho 30TB/ngày.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS Data Pipeline + EMR — phức tạp hơn, không real-time, cần quản lý cluster.

**❌ Đáp án B:**
- EC2 ASG — operational overhead (quản lý instances, scaling, patching).
- Không tối ưu cho streaming data so với Kinesis.

**❌ Đáp án C:**
- CloudFront không phải để cache data ingestion.
- Lambda có timeout (15 phút) và concurrency limits — không phù hợp cho 30TB/ngày.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Kinesis Data Streams + Firehose + S3 + Redshift = streaming analytics pipeline chuẩn"*
