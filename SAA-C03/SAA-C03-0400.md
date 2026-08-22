# Question #400 - Topic 1

A meteorological startup company has a custom web application to sell weather data to its users online. The company uses Amazon DynamoDB to store its data and wants to build a new service that sends an alert to the managers of four internal teams every time a new weather event is recorded. The company does not want this new service to affect the performance of the current application. What should a solutions architect do to meet these requirements with the LEAST amount of operational overhead?

## Options

**A.** Use DynamoDB transactions to write new event data to the table. Configure the transactions to notify internal teams.

**B.** Have the current application publish a message to four Amazon Simple Notification Service (Amazon SNS) topics. Have each team subscribe to one topic.

**C.** Enable Amazon DynamoDB Streams on the table. Use triggers to write to a single Amazon Simple Notification Service (Amazon SNS) topic to which the teams can subscribe.

**D.** Add a custom attribute to each record to flag new items. Write a cron job that scans the table every minute for items that are new and notifies an Amazon Simple Queue Service (Amazon SQS) queue to which the teams can subscribe.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DynamoDB weather data. Need alert 4 internal teams when new weather event recorded. Must not affect current app performance. Least operational overhead.
- **Existing Resources:** DynamoDB table, web application.
- **Current Issue/Goal:** Decoupled notification for new events.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `must not affect performance` | DynamoDB Streams: capture changes asynchronously, không ảnh hưởng write performance. |
| `DynamoDB Streams` | Real-time stream of changes to DynamoDB table. |
| `SNS topic` | Fan-out: 1 topic → 4 subscriptions (team managers). |
| `least operational overhead` | DynamoDB Streams + Lambda + SNS (serverless). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** No impact on current app, notify 4 teams

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- DynamoDB Streams: capture new items (INSERT events) asynchronously → zero impact on write performance.
- Lambda (trigger): read stream records → publish to single SNS topic.
- 4 team managers subscribe to the topic → fan-out.
- Serverless, operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DynamoDB transactions: không thể "configure transactions to notify". Transactions đảm bảo ACID, không phải notification mechanism.

**❌ Đáp án B:**
- Current application publish to 4 SNS topics: cần modify application code → operational overhead + ảnh hưởng performance.

**❌ Đáp án D:**
- Cron job scan table mỗi phút: inefficient (scan cost), operational overhead cao.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DynamoDB change notification → Streams + Lambda + SNS (async, no impact). Cron scan = inefficient."*
