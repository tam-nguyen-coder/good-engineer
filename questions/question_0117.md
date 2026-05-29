# Question #117 - Topic 1

A company stores its application logs in an Amazon CloudWatch Logs log group. A new policy requires the company to store all application logs in Amazon OpenSearch Service (Amazon Elasticsearch Service) in near-real time. Which solution will meet this requirement with the LEAST operational overhead?

## Options

**A.** Configure a CloudWatch Logs subscription to stream the logs to Amazon OpenSearch Service (Amazon Elasticsearch Service).

**B.** Create an AWS Lambda function. Use the log group to invoke the function to write the logs to Amazon OpenSearch Service (Amazon Elasticsearch Service).

**C.** Create an Amazon Kinesis Data Firehose delivery stream. Configure the log group as the delivery streams sources. Configure Amazon OpenSearch Service (Amazon Elasticsearch Service) as the delivery stream's destination.

**D.** Install and configure Amazon Kinesis Agent on each application server to deliver the logs to Amazon Kinesis Data Streams. Configure Kinesis Data Streams to deliver the logs to Amazon OpenSearch Service (Amazon Elasticsearch Service).

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Application logs in CloudWatch Logs, cần stream logs → OpenSearch near-real time.
- **Existing Resources:** CloudWatch Logs log group.
- **Current Issue/Goal:** Stream logs to OpenSearch, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `near-real time` | Cần streaming |
| `least operational overhead` | Built-in feature |
| `CloudWatch Logs subscription` | Native integration với OpenSearch |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Log analytics
- **Constraints:** Near-real time, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **CloudWatch Logs subscription** — built-in tính năng stream logs đến OpenSearch.
- Chỉ cần cấu hình destination là OpenSearch domain → tự động stream.
- **Least operational overhead** — không cần Lambda, Firehose, hay Kinesis Agent.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Lambda — có thể hoạt động nhưng phải viết code, operational overhead cao hơn.

**❌ Đáp án C:**
- Kinesis Data Firehose — CloudWatch Logs không thể là source trực tiếp cho Firehose.

**❌ Đáp án D:**
- Kinesis Agent + Data Streams — phải cài agent trên từng server, operational overhead cao.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudWatch Logs subscription → OpenSearch = native integration. No Lambda/Firehose needed"*
