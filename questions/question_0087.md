# Question #87 - Topic 1

A company hosts an application on AWS Lambda functions that are invoked by an Amazon API Gateway API. The Lambda functions save customer data to an Amazon Aurora MySQL database. Whenever the company upgrades the database, the Lambda functions fail to establish database connections until the upgrade is complete. The result is that customer data is not recorded for some of the event. A solutions architect needs to design a solution that stores customer data that is created during database upgrades. Which solution will meet these requirements?

## Options

**A.** Provision an Amazon RDS proxy to sit between the Lambda functions and the database. Configure the Lambda functions to connect to the RDS proxy.

**B.** Increase the run time of the Lambda functions to the maximum. Create a retry mechanism in the code that stores the customer data in the database.

**C.** Persist the customer data to Lambda local storage. Configure new Lambda functions to scan the local storage to save the customer data to the database.

**D.** Store the customer data in an Amazon Simple Queue Service (Amazon SQS) FIFO queue. Create a new Lambda function that polls the queue and stores the customer data in the database.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway + Lambda → Aurora MySQL. Lambda fails during DB upgrade → data loss.
- **Existing Resources:** API Gateway, Lambda, Aurora MySQL.
- **Current Issue/Goal:** Không mất data trong lúc DB upgrade.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `database upgrades` | Connection bị gián đoạn trong lúc upgrade |
| `customer data is not recorded` | Cần **RDS Proxy** để connection pooling |
| `Lambda functions` | Serverless, có thể retry ngắn |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability + Data integrity
- **Constraints:** Không mất data trong DB upgrade

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **RDS Proxy** — connection pool giữa Lambda và Aurora, tự động xử lý failover/upgrade.
- Khi DB upgrade, RDS Proxy giữ connections và **queue requests** đến khi DB available trở lại.
- Lambda functions không bị timeout/connection error.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Lambda max timeout 15 phút — upgrade có thể lâu hơn.
- Retry không giải quyết được nếu DB unavailable dài.

**❌ Đáp án C:**
- Lambda local storage (`/tmp`) là ephemeral — có thể bị mất khi Lambda cold start.
- Không durable.

**❌ Đáp án D:**
- SQS FIFO + Lambda — sẽ lưu được data nhưng không phải giải pháp tối ưu cho connection issue. Có operational overhead.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS Proxy = connection pooling + failover handling. Đúng cho Lambda + RDS/Aurora"*
