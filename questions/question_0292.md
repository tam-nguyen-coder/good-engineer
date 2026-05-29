# Question #292 - Topic 1

A company is preparing a new data platform that will ingest real-time streaming data from multiple sources. The company needs to transform the data before writing the data to Amazon S3. The company needs the ability to use SQL to query the transformed data. Which solutions will meet these requirements? (Choose two.)

## Options

**A.** Use Amazon Kinesis Data Streams to stream the data. Use Amazon Kinesis Data Analytics to transform the data. Use Amazon Kinesis Data Firehose to write the data to Amazon S3. Use Amazon Athena to query the transformed data from Amazon S3.

**B.** Use Amazon Managed Streaming for Apache Kafka (Amazon MSK) to stream the data. Use AWS Glue to transform the data and to write the data to Amazon S3. Use Amazon Athena to query the transformed data from Amazon S3.

**C.** Use AWS Database Migration Service (AWS DMS) to ingest the data. Use Amazon EMR to transform the data and to write the data to Amazon S3. Use Amazon Athena to query the transformed data from Amazon S3.

**D.** Use Amazon Managed Streaming for Apache Kafka (Amazon MSK) to stream the data. Use Amazon Kinesis Data Analytics to transform the data and to write the data to Amazon S3. Use the Amazon RDS query editor to query the transformed data from Amazon S3.

**E.** Use Amazon Kinesis Data Streams to stream the data. Use AWS Glue to transform the data. Use Amazon Kinesis Data Firehose to write the data to Amazon S3. Use the Amazon RDS query editor to query the transformed data from Amazon S3.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Real-time streaming data platform, cần transform và lưu vào S3, query bằng SQL.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Ingest real-time streams, transform, store in S3, SQL query.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `real-time streaming data` | Cần Kinesis Data Streams hoặc MSK để capture stream. |
| `transform the data` | Kinesis Data Analytics (SQL-based) hoặc AWS Glue (ETL). |
| `write the data to Amazon S3` | Kinesis Data Firehose có thể write trực tiếp vào S3. |
| `query the transformed data` | Amazon Athena query S3 bằng SQL (Presto engine). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two
- **Constraints:** Real-time streaming, transform, S3 destination, SQL query

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và B**

**Giải thích:**

**Đáp án A:**
- Kinesis Data Streams ingest real-time data.
- Kinesis Data Analytics transform data using SQL.
- Kinesis Data Firehose write to S3.
- Athena query S3 using SQL.

**Đáp án B:**
- MSK ingest streaming data via Kafka.
- AWS Glue transform data và write to S3 (ETL job).
- Athena query S3 using SQL.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án C:**
- DMS dùng cho database migration, không phải real-time streaming ingestion.

**❌ Đáp án D:**
- RDS query editor không thể query S3 (RDS query editor chỉ query RDS databases).

**❌ Đáp án E:**
- RDS query editor không thể query S3.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Real-time stream → Kinesis Data Streams / MSK. Transform → Kinesis Data Analytics / Glue. Sink → Firehose / Glue → S3. Query → Athena."*
