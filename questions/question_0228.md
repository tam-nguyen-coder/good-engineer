# Question #228 - Topic 1

A company has an API that receives real-time data from a fleet of monitoring devices. The API stores this data in an Amazon RDS DB instance for later analysis. The amount of data that the monitoring devices send to the API fluctuates. During periods of heavy traffic, the API often returns timeout errors. After an inspection of the logs, the company determines that the database is not capable of processing the volume of write traffic that comes from the API. A solutions architect must minimize the number of connections to the database and must ensure that data is not lost during periods of heavy traffic. Which solution will meet these requirements?

## Options

**A.** Increase the size of the DB instance to an instance type that has more available memory.

**B.** Modify the DB instance to be a Multi-AZ DB instance. Configure the application to write to all active RDS DB instances.

**C.** Modify the API to write incoming data to an Amazon Simple Queue Service (Amazon SQS) queue. Use an AWS Lambda function that Amazon SQS invokes to write data from the queue to the database.

**D.** Modify the API to write incoming data to an Amazon Simple Notification Service (Amazon SNS) topic. Use an AWS Lambda function that Amazon SNS invokes to write data from the topic to the database.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API receives real-time data → RDS. Fluctuating traffic. DB write capacity bottleneck → timeout errors.
- **Existing Resources:** API, RDS.
- **Current Issue/Goal:** Buffer writes, minimize connections, no data loss.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `database is not capable of processing the volume of write traffic` | **SQS queue** — buffer writes |
| `minimize the number of connections to the database` | SQS + Lambda — fewer connections |
| `data is not lost` | SQS durable storage |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / Messaging
- **Constraints:** Buffer writes, minimize connections, no data loss

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **SQS queue** — buffer incoming writes, durable (no data loss).
- **Lambda** — đọc từ SQS, batch writes vào RDS → minimize connections.
- SQS scale độc lập với RDS → không timeout errors.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Increase DB size — không giải quyết connection churn, cost cao.

**❌ Đáp án B:**
- Multi-AZ — không thể write to all instances (chỉ 1 primary).

**❌ Đáp án D:**
- SNS + Lambda — SNS push không buffer, có thể overwhelm Lambda/RDS.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS + Lambda = buffer writes, minimize connections. SNS = no buffer (push model)"*
