# Question #175 - Topic 1

An ecommerce company has an order-processing application that uses Amazon API Gateway and an AWS Lambda function. The application stores data in an Amazon Aurora PostgreSQL database. During a recent sales event, a sudden surge in customer orders occurred. Some customers experienced timeouts, and the application did not process the orders of those customers. A solutions architect determined that the CPU utilization and memory utilization were high on the database because of a large number of open connections. The solutions architect needs to prevent the timeout errors while making the least possible changes to the application. Which solution will meet these requirements?

## Options

**A.** Configure provisioned concurrency for the Lambda function. Modify the database to be a global database in multiple AWS Regions.

**B.** Use Amazon RDS Proxy to create a proxy for the database. Modify the Lambda function to use the RDS Proxy endpoint instead of the database endpoint.

**C.** Create a read replica for the database in a different AWS Region. Use query string parameters in API Gateway to route traffic to the read replica.

**D.** Migrate the data from Aurora PostgreSQL to Amazon DynamoDB by using AWS Database Migration Service (AWS DMS). Modify the Lambda function to use the DynamoDB table.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway + Lambda + Aurora PostgreSQL. Surge → too many connections → DB overload → timeouts.
- **Existing Resources:** API Gateway, Lambda, Aurora PostgreSQL.
- **Current Issue/Goal:** Prevent timeouts, least app changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `large number of open connections` | **RDS Proxy** = connection pooling |
| `least possible changes to the application` | RDS Proxy — chỉ cần đổi endpoint |
| `Lambda` | Lambda can cause connection churn (cold start) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / Serverless
- **Constraints:** Connection pooling, minimal change

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **RDS Proxy** — connection pooling giữa Lambda và Aurora → tái sử dụng connections, giảm số lượng open connections.
- Chỉ cần modify Lambda function để dùng RDS Proxy endpoint → minimal change.
- RDS Proxy auto-scale, HA.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Provisioned concurrency — giảm cold start, không giải quyết connection pooling.
- Global database — không giải quyết connection churn.

**❌ Đáp án C:**
- Read replica — cho read scaling, không giúp giảm connections cho writes.

**❌ Đáp án D:**
- Migrate to DynamoDB — major change, không phải least possible.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS Proxy = connection pooling for Lambda + Aurora. Least change = change endpoint only"*
