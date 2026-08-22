# Question #422 - Topic 1

A company is developing a new machine learning (ML) model solution on AWS. The models are developed as independent microservices that fetch approximately 1 GB of model data from Amazon S3 at startup and load the data into memory. Users access the models through an asynchronous API. Users can send a request or a batch of requests and specify where the results should be sent. The company provides models to hundreds of users. The usage patterns for the models are irregular. Some models could be unused for days or weeks. Other models could receive batches of thousands of requests at a time. Which design should a solutions architect recommend to meet these requirements?

## Options

**A.** Direct the requests from the API to a Network Load Balancer (NLB). Deploy the models as AWS Lambda functions that are invoked by the NLB.

**B.** Direct the requests from the API to an Application Load Balancer (ALB). Deploy the models as Amazon Elastic Container Service (Amazon ECS) services that read from an Amazon Simple Queue Service (Amazon SQS) queue. Use AWS App Mesh to scale the instances of the ECS cluster based on the SQS queue size.

**C.** Direct the requests from the API into an Amazon Simple Queue Service (Amazon SQS) queue. Deploy the models as AWS Lambda functions that are invoked by SQS events. Use AWS Auto Scaling to increase the number of vCPUs for the Lambda functions based on the SQS queue size.

**D.** Direct the requests from the API into an Amazon Simple Queue Service (Amazon SQS) queue. Deploy the models as Amazon Elastic Container Service (Amazon ECS) services that read from the queue. Enable AWS Auto Scaling on Amazon ECS for both the cluster and copies of the service based on the queue size.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ML models as microservices. 1GB model data loaded at startup from S3. Async API. Irregular usage (idle days/weeks, then thousands of requests).
- **Existing Resources:** S3 bucket (model data), async API.
- **Current Issue/Goal:** Scalable ML inference. Handle burst + idle patterns.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `1 GB of model data at startup` | Lambda cold start quá lâu (1GB). ECS lưu memory giữa requests. |
| `asynchronous API` | SQS queue để buffer requests. |
| `thousands of requests at a time` | ECS scale dựa trên SQS queue depth. |
| `irregular usage` | ECS service auto scale từ 0 lên nhiều tasks. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Scalability / ML
- **Constraints:** Asynchronous, irregular load, 1GB model in memory

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- SQS queue: buffer requests, async processing.
- ECS: container giữ model 1GB trong memory persistent giữa các requests (không cold start như Lambda).
- ECS Auto Scaling based on SQS queue depth: scale out khi queue dài, scale in khi ngắn.
- Xử lý được batch requests.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- NLB → Lambda: NLB không thể invoke Lambda (NLB targets: EC2, IP, ALB).
- Lambda cold start với 1GB model data → rất chậm.

**❌ Đáp án B:**
- ALB dùng cho request-response, không async. App Mesh là service mesh, không phải scaling solution dựa trên SQS.

**❌ Đáp án C:**
- Lambda invoked by SQS: cold start 1GB model data. "AWS Auto Scaling for Lambda vCPUs" không phải tính năng thực tế.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ML model (1GB) in memory → ECS (no cold start). SQS queue → scale based on queue depth."*