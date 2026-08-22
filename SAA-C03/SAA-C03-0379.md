# Question #379 - Topic 1

A company hosts a frontend application that uses an Amazon API Gateway API backend that is integrated with AWS Lambda. When the API receives requests, the Lambda function loads many libraries. Then the Lambda function connects to an Amazon RDS database, processes the data, and returns the data to the frontend application. The company wants to ensure that response latency is as low as possible for all its users with the fewest number of changes to the company's operations. Which solution will meet these requirements?

## Options

**A.** Establish a connection between the frontend application and the database to make queries faster by bypassing the API.

**B.** Configure provisioned concurrency for the Lambda function that handles the requests.

**C.** Cache the results of the queries in Amazon S3 for faster retrieval of similar datasets.

**D.** Increase the size of the database to increase the number of connections Lambda can establish at one time.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway + Lambda + RDS. Lambda loads many libraries → cold start latency. Need low latency, fewest operational changes.
- **Existing Resources:** API Gateway, Lambda, RDS.
- **Current Issue/Goal:** Reduce response latency (caused by Lambda cold start loading libraries).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `loads many libraries` | Cold start latency high. |
| `provisioned concurrency` | Lambda instances pre-initialized (no cold start), libraries pre-loaded. |
| `lowest possible latency` | Provisioned concurrency = zero cold start latency. |
| `fewest number of changes to operations` | Provisioned concurrency: chỉ cần config, không code changes. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Lowest latency, fewest operational changes
- **Constraints:** Lambda cold start, RDS data fetch

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Provisioned concurrency: maintain specified number of pre-initialized Lambda environments → no cold start.
- Libraries đã loaded sẵn, Lambda sẵn sàng xử lý request ngay lập tức.
- Fewest operational changes: chỉ cần configure provisioned concurrency, không code changes.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Bypass API → bỏ security layer, major architecture change → nhiều operational changes.

**❌ Đáp án C:**
- S3 caching: chỉ hữu ích cho read-heavy workloads, không giảm cold start latency.

**❌ Đáp án D:**
- Increase DB size: tăng max connections nhưng không giải quyết Lambda cold start latency.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda cold start (load libraries) → Provisioned Concurrency (pre-initialized). DB upgrade/S3 cache = không giải quyết cold start."*
