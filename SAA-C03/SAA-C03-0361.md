# Question #361 - Topic 1

A company hosts a multiplayer gaming application on AWS. The company wants the application to read data with sub-millisecond latency and run one-time queries on historical data. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use Amazon RDS for data that is frequently accessed. Run a periodic custom script to export the data to an Amazon S3 bucket.

**B.** Store the data directly in an Amazon S3 bucket. Implement an S3 Lifecycle policy to move older data to S3 Glacier Deep Archive for long- term storage. Run one-time queries on the data in Amazon S3 by using Amazon Athena.

**C.** Use Amazon DynamoDB with DynamoDB Accelerator (DAX) for data that is frequently accessed. Export the data to an Amazon S3 bucket by using DynamoDB table export. Run one-time queries on the data in Amazon S3 by using Amazon Athena.

**D.** Use Amazon DynamoDB for data that is frequently accessed. Turn on streaming to Amazon Kinesis Data Streams. Use Amazon Kinesis Data Firehose to read the data from Kinesis Data Streams. Store the records in an Amazon S3 bucket.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multiplayer gaming app: sub-millisecond reads cho hot data + one-time queries on historical data. Least operational overhead.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Low-latency reads + historical analytics.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sub-millisecond latency` | DAX (DynamoDB Accelerator) cung cấp microsecond latency cho DynamoDB reads. |
| `one-time queries on historical data` | Athena query S3 (serverless, pay per query). |
| `DynamoDB table export to S3` | Built-in feature (PITR export), không cần custom streaming. |
| `least operational overhead` | DynamoDB + DAX (managed) + built-in export + Athena (serverless). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Sub-ms reads + historical queries

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- DynamoDB: fast reads (~single-digit ms), DAX in-memory cache cho sub-millisecond reads.
- DynamoDB built-in table export to S3: không cần custom code.
- Athena: serverless query trên S3, pay per query.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- RDS không đạt sub-millisecond latency cho high-throughput gaming. Custom export script = operational overhead.

**❌ Đáp án B:**
- S3 không đạt sub-millisecond latency (millisecond range nhưng không sub-ms).

**❌ Đáp án D:**
- Kinesis Data Streams + Firehose → S3: operational overhead cao hơn built-in DynamoDB export.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Sub-ms reads → DynamoDB + DAX. Historical queries on S3 → Athena. Built-in export → không cần custom streaming."*
