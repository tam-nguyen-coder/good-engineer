# Question #397 - Topic 1

An ecommerce company needs to run a scheduled daily job to aggregate and filter sales records for analytics. The company stores the sales records in an Amazon S3 bucket. Each object can be up to 10 GB in size. Based on the number of sales events, the job can take up to an hour to complete. The CPU and memory usage of the job are constant and are known in advance. A solutions architect needs to minimize the amount of operational effort that is needed for the job to run. Which solution meets these requirements?

## Options

**A.** Create an AWS Lambda function that has an Amazon EventBridge notification. Schedule the EventBridge event to run once a day.

**B.** Create an AWS Lambda function. Create an Amazon API Gateway HTTP API, and integrate the API with the function. Create an Amazon EventBridge scheduled event that calls the API and invokes the function.

**C.** Create an Amazon Elastic Container Service (Amazon ECS) cluster with an AWS Fargate launch type. Create an Amazon EventBridge scheduled event that launches an ECS task on the cluster to run the job.

**D.** Create an Amazon Elastic Container Service (Amazon ECS) cluster with an Amazon EC2 launch type and an Auto Scaling group with at least one EC2 instance. Create an Amazon EventBridge scheduled event that launches an ECS task on the cluster to run the job.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Daily job, aggregate/filter sales records from S3. Objects up to 10 GB. Job up to 1 hour. CPU/memory constant, known. Minimize operational effort.
- **Existing Resources:** S3 bucket with sales records.
- **Current Issue/Goal:** Run daily batch job with minimal operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `up to an hour to complete` | Lambda max 15 min → không đủ. |
| `minimize operational effort` | Fargate (serverless containers) < EC2 launch type (quản lý instances). |
| `known constant CPU and memory` | Có thể config Fargate task size chính xác. |
| `Fargate launch type` | Serverless, không quản lý infrastructure. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Minimize operational effort
- **Constraints:** Up to 1 hour runtime, 10 GB objects, scheduled daily

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Lambda: max 15 min → không thể chạy job up to 1 hour.
- ECS Fargate: serverless containers, không cần quản lý EC2 instances. EventBridge schedule launch ECS task.
- Operational effort thấp hơn EC2 launch type (D).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda 15 min max → không đủ cho job có thể chạy 1 hour.

**❌ Đáp án B:**
- Lambda vẫn giới hạn 15 min. API Gateway không cần thiết (EventBridge có thể invoke Lambda trực tiếp).

**❌ Đáp án D:**
- ECS EC2 launch type: cần quản lý EC2 instances, ASG → operational effort cao hơn Fargate.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Up to 1 hour job → ECS/Fargate (Lambda 15 min max). Fargate = serverless, less effort than EC2."*
