# Question #320 - Topic 1

A company is using a fleet of Amazon EC2 instances to ingest data from on-premises data sources. The data is in JSON format and ingestion rates can be as high as 1 MB/s. When an EC2 instance is rebooted, the data in-flight is lost. The company's data science team wants to query ingested data in near-real time. Which solution provides near-real-time data querying that is scalable with minimal data loss?

## Options

**A.** Publish data to Amazon Kinesis Data Streams, Use Kinesis Data Analytics to query the data.

**B.** Publish data to Amazon Kinesis Data Firehose with Amazon Redshift as the destination. Use Amazon Redshift to query the data.

**C.** Store ingested data in an EC2 instance store. Publish data to Amazon Kinesis Data Firehose with Amazon S3 as the destination. Use Amazon Athena to query the data.

**D.** Store ingested data in an Amazon Elastic Block Store (Amazon EBS) volume. Publish data to Amazon ElastiCache for Redis. Subscribe to the Redis channel to query the data.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 ingest JSON data (up to 1 MB/s), data lost on reboot. Cần near-real-time query, scalable, minimal data loss.
- **Existing Resources:** EC2 instances ingesting data.
- **Current Issue/Goal:** Near-real-time querying, minimal data loss, scalable.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `data in-flight is lost` | Cần durable ingestion → Kinesis Data Streams persist data (24h default). |
| `near-real time` | Kinesis Data Analytics query streaming data in real-time (SQL). |
| `scalable` | Kinesis scale bằng cách thêm shards. |
| `1 MB/s` | Kinesis Data Streams handle được (1 shard = 1 MB/s input). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Near-real-time querying, scalable, minimal data loss
- **Constraints:** 1 MB/s JSON, data loss on EC2 reboot

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Kinesis Data Streams: persist data trong 24h (extendable), không mất data khi EC2 reboot.
- Kinesis Data Analytics: query streaming data in real-time với SQL.
- Scale bằng cách thêm shards (mỗi shard 1 MB/s input).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Kinesis Firehose → Redshift: Firehose gom batch rồi deliver, không real-time như KDS + Analytics. Redshift không phải real-time query engine.

**❌ Đáp án C:**
- Instance store là ephemeral → data mất khi reboot/stop. Firehose → S3 → Athena là near-real-time (có độ trễ do Firehose buffer).

**❌ Đáp án D:**
- ElastiCache for Redis không phải storage cho data persistence. Không scalable cho 1 MB/s ingestion + query cùng lúc.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Near-real-time query + durable → Kinesis Data Streams + Kinesis Data Analytics. Firehose = có độ trễ batch."*
