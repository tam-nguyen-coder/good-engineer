# Question #220 - Topic 1

A solutions architect is designing a new API using Amazon API Gateway that will receive requests from users. The volume of requests is highly variable; several hours can pass without receiving a single request. The data processing will take place asynchronously, but should be completed within a few seconds after a request is made. Which compute service should the solutions architect have the API invoke to deliver the requirements at the lowest cost?

## Options

**A.** An AWS Glue job

**B.** An AWS Lambda function

**C.** A containerized service hosted in Amazon Elastic Kubernetes Service (Amazon EKS)

**D.** A containerized service hosted in Amazon ECS with Amazon EC2

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway with highly variable traffic (hours with no requests). Async processing, must complete within seconds. Lowest cost.
- **Existing Resources:** API Gateway.
- **Current Issue/Goal:** Serverless compute, pay-per-use.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `several hours can pass without receiving a single request` | Idle time — cần **pay-per-use** |
| `completed within a few seconds` | **Lambda** (max 15 min) |
| `lowest cost` | Lambda — zero cost when idle |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless / Compute
- **Constraints:** Variable traffic, seconds latency, lowest cost

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Lambda** — serverless, pay per invocation and duration.
- Zero cost khi không có request.
- Cold start ~ms, hoàn thành async processing trong seconds.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Glue job — cho ETL, startup time cao (phút), không phù hợp cho API.

**❌ Đáp án C:**
- EKS — tốn chi phí cluster ngay cả khi không có traffic.

**❌ Đáp án D:**
- ECS EC2 — tốn chi phí EC2 instances ngay cả khi idle.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda = pay-per-use (zero cost idle). EKS/ECS = cluster cost always on. Glue = ETL, not API"*
