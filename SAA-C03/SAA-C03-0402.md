# Question #402 - Topic 1

A company needs to ingest and handle large amounts of streaming data that its application generates. The application runs on Amazon EC2 instances and sends data to Amazon Kinesis Data Streams, which is configured with default settings. Every other day, the application consumes the data and writes the data to an Amazon S3 bucket for business intelligence (BI) processing. The company observes that Amazon S3 is not receiving all the data that the application sends to Kinesis Data Streams. What should a solutions architect do to resolve this issue?

## Options

**A.** Update the Kinesis Data Streams default settings by modifying the data retention period.

**B.** Update the application to use the Kinesis Producer Library (KPL) to send the data to Kinesis Data Streams.

**C.** Update the number of Kinesis shards to handle the throughput of the data that is sent to Kinesis Data Streams.

**D.** Turn on S3 Versioning within the S3 bucket to preserve every version of every object that is ingested in the S3 bucket.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 app sends streaming data → Kinesis Data Streams (default settings) → consumed every other day → S3 for BI. S3 missing data.
- **Existing Resources:** EC2 instances, Kinesis Data Streams (default), S3 bucket.
- **Current Issue/Goal:** Data loss between Kinesis → S3. Need to fix so all data reaches S3.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `default settings` | 1 shard (1 MB/s write, 2 MB/s read). |
| `not receiving all the data` | Throughput throttling → data dropped. |
| `large amounts of streaming data` | Need more shards for higher throughput. |
| `shards` | Đơn vị capacity của Kinesis Data Streams. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Troubleshooting / Performance
- **Constraints:** Must ingest all streaming data

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Default = 1 shard → throughput giới hạn (1 MB/s write). Nếu data vượt quá → bị throttled → mất data.
- Tăng số shard → tăng throughput → đủ capacity cho lượng data lớn.
- Kinesis shards scale horizontally.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Data retention period (default 24h) → chỉ ảnh hưởng thời gian data tồn tại, không ảnh hưởng throughput hay mất data.

**❌ Đáp án B:**
- KPL giúp batching/compression để tăng hiệu quả gửi, nhưng nếu shard throughput đã đạt giới hạn thì KPL không giải quyết được.

**❌ Đáp án D:**
- S3 Versioning giúp bảo vệ object khỏi bị overwrite/delete, không giúp data đến được S3.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Missing data in Kinesis → not enough shards (throughput). Retention ≠ throughput."*

