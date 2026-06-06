# Question #181 - Topic 1

A company has a legacy data processing application that runs on Amazon EC2 instances. Data is processed sequentially, but the order of results does not matter. The application uses a monolithic architecture. The only way that the company can scale the application to meet increased demand is to increase the size of the instances. The company's developers have decided to rewrite the application to use a microservices architecture on Amazon Elastic Container Service (Amazon ECS). What should a solutions architect recommend for communication between the microservices?

## Options

**A.** Create an Amazon Simple Queue Service (Amazon SQS) queue. Add code to the data producers, and send data to the queue. Add code to the data consumers to process data from the queue.

**B.** Create an Amazon Simple Notification Service (Amazon SNS) topic. Add code to the data producers, and publish notifications to the topic. Add code to the data consumers to subscribe to the topic.

**C.** Create an AWS Lambda function to pass messages. Add code to the data producers to call the Lambda function with a data object. Add code to the data consumers to receive a data object that is passed from the Lambda function.

**D.** Create an Amazon DynamoDB table. Enable DynamoDB Streams. Add code to the data producers to insert data into the table. Add code to the data consumers to use the DynamoDB Streams API to detect new table entries and retrieve the data.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Monolithic → microservices on ECS. Data processing sequential but order of results doesn't matter.
- **Existing Resources:** Legacy app on EC2.
- **Current Issue/Goal:** Decoupled async communication between microservices.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sequential` | Data is processed in sequence |
| `order of results does not matter` | SQS standard queue (not FIFO) |
| `microservices` | Async, decoupled — **SQS** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Microservices / Messaging
- **Constraints:** Decoupled, async, ECS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **SQS queue** — decouple producers and consumers, durable, scalable.
- Standard queue — không guarantee order (result order không quan trọng).
- Microservices trên ECS có thể scale consumers independently.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- SNS — pub/sub, one-to-many, không phù hợp cho point-to-point queuing.

**❌ Đáp án C:**
- Lambda — synchronous invocation, không durable, không phù hợp inter-service messaging.

**❌ Đáp án D:**
- DynamoDB Streams — dùng để trigger Lambda on table changes, không phải message queue.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS = decouple microservices. SNS = pub/sub. Lambda sync = not durable queue"*
