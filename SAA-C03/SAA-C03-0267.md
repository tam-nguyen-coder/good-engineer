# Question #267 - Topic 1

A company has one million users that use its mobile app. The company must analyze the data usage in near-real time. The company also must encrypt the data in near-real time and must store the data in a centralized location in Apache Parquet format for further processing. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create an Amazon Kinesis data stream to store the data in Amazon S3. Create an Amazon Kinesis Data Analytics application to analyze the data. Invoke an AWS Lambda function to send the data to the Kinesis Data Analytics application.

**B.** Create an Amazon Kinesis data stream to store the data in Amazon S3. Create an Amazon EMR cluster to analyze the data. Invoke an AWS Lambda function to send the data to the EMR cluster.

**C.** Create an Amazon Kinesis Data Firehose delivery stream to store the data in Amazon S3. Create an Amazon EMR cluster to analyze the data.

**D.** Create an Amazon Kinesis Data Firehose delivery stream to store the data in Amazon S3. Create an Amazon Kinesis Data Analytics application to analyze the data.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Mobile app, 1M users. Near-real-time analysis. Encrypt + store in Parquet in S3.
- **Existing Resources:** Mobile app.
- **Current Issue/Goal:** Streaming ingestion + analytics, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `near-real time` | **Kinesis Data Firehose** (buffered delivery) |
| `store in Apache Parquet format` | Firehose tự động convert → Parquet |
| `least operational overhead` | **Kinesis Data Analytics** (serverless SQL) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Streaming / Analytics
- **Constraints:** Near-real-time, Parquet, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Firehose** — tự động convert data → Parquet, encrypt, deliver to S3.
- **KDA (Kinesis Data Analytics)** — serverless SQL analytics on streaming data.
- No EC2/EMR to manage → least operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- KDS không store data trực tiếp trong S3. Cần consumer. Complex.

**❌ Đáp án B:**
- KDS + EMR + Lambda — EMR operational overhead.

**❌ Đáp án C:**
- Firehose + EMR — EMR operational overhead hơn KDA.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Firehose → S3 (Parquet) + KDA = serverless streaming analytics. EMR = more overhead"*
