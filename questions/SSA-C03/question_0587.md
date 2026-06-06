# Question #587 - Topic 1

A company is designing a solution to capture customer activity in different web applications to process analytics and make predictions. Customer activity in the web applications is unpredictable and can increase suddenly. The company requires a solution that integrates with other web applications. The solution must include an authorization step for security purposes. Which solution will meet these requirements?

## Options

**A.** Configure a Gateway Load Balancer (GWLB) in front of an Amazon Elastic Container Service (Amazon ECS) container instance that stores the information that the company receives in an Amazon Elastic File System (Amazon EFS) file system. Authorization is resolved at the GWLB.

**B.** Configure an Amazon API Gateway endpoint in front of an Amazon Kinesis data stream that stores the information that the company receives in an Amazon S3 bucket. Use an AWS Lambda function to resolve authorization.

**C.** Configure an Amazon API Gateway endpoint in front of an Amazon Kinesis Data Firehose that stores the information that the company receives in an Amazon S3 bucket. Use an API Gateway Lambda authorizer to resolve authorization.

**D.** Configure a Gateway Load Balancer (GWLB) in front of an Amazon Elastic Container Service (Amazon ECS) container instance that stores the information that the company receives on an Amazon Elastic File System (Amazon EFS) file system. Use an AWS Lambda function to resolve authorization.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Capture customer activity từ nhiều web apps, process analytics + predictions, unpredictable traffic, cần authorization.
- **Existing Resources:** Web applications.
- **Current Issue/Goal:** Serverless ingestion với authentication.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `unpredictable and can increase suddenly` | Cần serverless/scalable ingestion (Kinesis Data Firehose scales automatically). |
| `integrates with other web applications` | API Gateway: RESTful API endpoints cho web apps. |
| `authorization step` | API Gateway Lambda authorizer. |
| `Amazon Kinesis Data Firehose` | Automatic scaling, delivery to S3. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Authorization, scalable, integrate with web apps

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- API Gateway: cung cấp REST endpoints cho web apps, có built-in Lambda authorizer.
- Kinesis Data Firehose: tự động scale với unpredictable traffic, deliver data to S3.
- Lambda authorizer: xác thực requests trước khi xử lý.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- GWLB dùng cho network appliances (firewall, IDS/IPS), không phải cho API ingestion. GWLB không có built-in authorizer.

**❌ Đáp án B:**
- Kinesis data stream: cần consumer xử lý (KCL, Lambda), không tự động deliver to S3. Lambda authorizer đúng nhưng Kinesis Data Firehose phù hợp hơn Data Stream cho việc deliver to S3.

**❌ Đáp án D:**
- GWLB không phù hợp cho web API ingestion. ECS + EFS kém scalable hơn serverless.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Web app ingestion + auth → API Gateway + Lambda authorizer. Unpredictable traffic → Kinesis Data Firehose (auto scaling)."*
