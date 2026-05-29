# Question #354 - Topic 1

A company hosts a serverless application on AWS. The application uses Amazon API Gateway, AWS Lambda, and an Amazon RDS for PostgreSQL database. The company notices an increase in application errors that result from database connection timeouts during times of peak traffic or unpredictable traffic. The company needs a solution that reduces the application failures with the least amount of change to the code. What should a solutions architect do to meet these requirements?

## Options

**A.** Reduce the Lambda concurrency rate.

**B.** Enable RDS Proxy on the RDS DB instance.

**C.** Resize the RDS DB instance class to accept more connections.

**D.** Migrate the database to Amazon DynamoDB with on-demand scaling.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Serverless (API Gateway + Lambda) + RDS PostgreSQL. Connection timeouts during peak/unpredictable traffic. Least code changes.
- **Existing Resources:** API Gateway, Lambda, RDS PostgreSQL.
- **Current Issue/Goal:** Reduce connection timeouts, minimize code changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `database connection timeouts` | Lambda can scale rapidly → too many connections to RDS → timeouts. |
| `RDS Proxy` | Connection pooling: Lambda reuse connections via proxy, RDS không bị overwhelmed. |
| `least amount of change to the code` | RDS Proxy: chỉ cần change connection string (no code logic changes). |
| `peak traffic or unpredictable traffic` | RDS Proxy handle connection spikes gracefully. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least code changes
- **Constraints:** Connection timeouts, serverless + RDS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- RDS Proxy: managed connection pool giữa Lambda và RDS. Lambda connections được multiplexed → giảm connection churn, tránh timeouts.
- No code changes: chỉ cần update Lambda connection string to point to RDS Proxy endpoint.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Giảm Lambda concurrency: giảm errors nhưng cũng giảm throughput → không phải giải pháp tối ưu.

**❌ Đáp án C:**
- Resize instance: tăng connection limit nhưng không giải quyết connection storm từ Lambda scale-out. Tốn kém.

**❌ Đáp án D:**
- Migrate to DynamoDB: major code changes (SQL → NoSQL) → least code changes requirement không đáp ứng.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda + RDS connection timeouts → RDS Proxy (connection pooling, no code changes)."*
