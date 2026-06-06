# Question #672 - Topic 1

A marketing company receives a large amount of new clickstream data in Amazon S3 from a marketing campaign. The company needs to analyze the clickstream data in Amazon S3 quickly. Then the company needs to determine whether to process the data further in the data pipeline. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create external tables in a Spark catalog. Configure jobs in AWS Glue to query the data.

**B.** Configure an AWS Glue crawler to crawl the data. Configure Amazon Athena to query the data.

**C.** Create external tables in a Hive metastore. Configure Spark jobs in Amazon EMR to query the data.

**D.** Configure an AWS Glue crawler to crawl the data. Configure Amazon Kinesis Data Analytics to use SQL to query the data.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Clickstream data in S3, need quick analysis to decide further processing.
- **Existing Resources:** S3 bucket with clickstream data.
- **Current Issue/Goal:** Quick SQL query, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `analyze quickly` | Serverless query → no cluster provisioning time. |
| `least operational overhead` | Glue (crawler) + Athena (serverless SQL) = minimum management. |
| `Glue crawler` | Tự động crawl S3 data, populate Data Catalog. |
| `Athena` | Serverless SQL query on S3. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Analyze S3 data quickly

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Glue crawler tự động scan S3, infer schema, populate Glue Data Catalog.
- Athena query trực tiếp trên S3 qua Data Catalog, pay-per-query.
- Cả hai đều serverless → không cần quản lý cluster, operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Glue jobs (Spark) cần provisioning, chậm hơn Athena cho ad-hoc queries.

**❌ Đáp án C:**
- EMR cần cluster → operational overhead cao, thời gian provisioning.

**❌ Đáp án D:**
- Kinesis Data Analytics dùng cho streaming data (real-time), không phải batch data trong S3.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 data analysis → Glue crawler (catalog) + Athena (serverless SQL). Quick + no servers."*
