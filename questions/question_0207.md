# Question #207 - Topic 1

A company owns an asynchronous API that is used to ingest user requests and, based on the request type, dispatch requests to the appropriate microservice for processing. The company is using Amazon API Gateway to deploy the API front end, and an AWS Lambda function that invokes Amazon DynamoDB to store user requests before dispatching them to the processing microservices. The company provisioned as much DynamoDB throughput as its budget allows, but the company is still experiencing availability issues and is losing user requests. What should a solutions architect do to address this issue without impacting existing users?

## Options

**A.** Add throttling on the API Gateway with server-side throttling limits.

**B.** Use DynamoDB Accelerator (DAX) and Lambda to buffer writes to DynamoDB.

**C.** Create a secondary index in DynamoDB for the table with the user requests.

**D.** Use the Amazon Simple Queue Service (Amazon SQS) queue and Lambda to buffer writes to DynamoDB.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway → Lambda → DynamoDB → microservices. DynamoDB throughput maxed, losing requests. Budget limited.
- **Existing Resources:** API Gateway, Lambda, DynamoDB.
- **Current Issue/Goal:** Buffer writes to DynamoDB to smooth traffic spikes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `provisioned as much DynamoDB throughput as its budget allows` | Không thể tăng thêm WCU |
| `losing user requests` | Cần **buffer** — **SQS** |
| `without impacting existing users` | SQS giúp decouple, không cần thay đổi client |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless / Database
- **Constraints:** Budget-limited, buffer writes, no impact on users

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **SQS queue** giữa Lambda và DynamoDB → buffer writes, smooth traffic spikes.
- Lambda đọc từ SQS và write vào DynamoDB với tốc độ ổn định → không vượt WCU.
- Không ảnh hưởng đến API Gateway hay users.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Throttling API Gateway — từ chối requests, gây mất requests.

**❌ Đáp án B:**
- DAX — cache for reads, không buffer writes.

**❌ Đáp án C:**
- Secondary index — không giúp tăng write capacity.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS + Lambda = buffer writes to DynamoDB. DAX = read cache. Throttling = drops requests"*
