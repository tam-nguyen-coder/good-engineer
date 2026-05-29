# Question #523 - Topic 1

A company runs a microservice-based serverless web application. The application must be able to retrieve data from multiple Amazon DynamoDB tables A solutions architect needs to give the application the ability to retrieve the data with no impact on the baseline performance of the application. Which solution will meet these requirements in the MOST operationally efficient way?

## Options

**A.** AWS AppSync pipeline resolvers

**B.** Amazon CloudFront with Lambda@Edge functions

**C.** Edge-optimized Amazon API Gateway with AWS Lambda functions

**D.** Amazon Athena Federated Query with a DynamoDB connector

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Serverless microservice web app cần retrieve data từ nhiều DynamoDB tables mà không ảnh hưởng performance.
- **Existing Resources:** Serverless web application, nhiều DynamoDB tables.
- **Current Issue/Goal:** Truy xuất nhiều DynamoDB tables hiệu quả, không impact baseline performance.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `retrieve data from multiple DynamoDB tables` | Cần gộp dữ liệu từ nhiều nguồn |
| `no impact on baseline performance` | Giải pháp không làm chậm ứng dụng |
| `AppSync pipeline resolvers` | Cho phép chain nhiều resolvers để query nhiều nguồn dữ liệu trong một request |
| `most operationally efficient` | Serverless, managed service, ít code nhất |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operationally efficient
- **Constraints:** No impact on baseline performance, microservice-based serverless

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS AppSync pipeline resolvers cho phép định nghĩa một pipeline gồm nhiều function (resolvers) → mỗi function query một DynamoDB table → gộp kết quả trả về.
- Pipeline resolvers chạy độc lập, không ảnh hưởng baseline performance.
- Operationnally efficient: không cần viết Lambda code cho việc gộp dữ liệu, cấu hình qua GraphQL schema và resolver templates.
- AppSync hỗ trợ real-time subscription, caching, và fine-grained access control.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- CloudFront + Lambda@Edge phù hợp cho CDN và edge computing, không phải để query nhiều DynamoDB tables từ serverless app.

**❌ Đáp án C:**
- API Gateway + Lambda có thể query DynamoDB nhưng mỗi Lambda function thường chỉ xử lý một table. Nếu cần query nhiều table, phải viết code orchestration phức tạp hơn AppSync.

**❌ Đáp án D:**
- Athena Federated Query dùng để query dữ liệu từ DynamoDB bằng SQL, phù hợp cho analytics, không phải cho real-time microservice web app. Latency cao.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"AppSync pipeline resolvers = GraphQL + multiple DynamoDB tables in one request, no Lambda needed."*
