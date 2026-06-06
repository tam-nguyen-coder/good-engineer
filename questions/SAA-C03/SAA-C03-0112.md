# Question #112 - Topic 1

A company hosts a containerized web application on a fleet of on-premises servers that process incoming requests. The number of requests is growing quickly. The on-premises servers cannot handle the increased number of requests. The company wants to move the application to AWS with minimum code changes and minimum development effort. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS Fargate on Amazon Elastic Container Service (Amazon ECS) to run the containerized web application with Service Auto Scaling. Use an Application Load Balancer to distribute the incoming requests.

**B.** Use two Amazon EC2 instances to host the containerized web application. Use an Application Load Balancer to distribute the incoming requests.

**C.** Use AWS Lambda with a new code that uses one of the supported languages. Create multiple Lambda functions to support the load. Use Amazon API Gateway as an entry point to the Lambda functions.

**D.** Use a high performance computing (HPC) solution such as AWS ParallelCluster to establish an HPC cluster that can process the incoming requests at the appropriate scale.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Containerized web app on-prem, growing requests, need to move to AWS.
- **Existing Resources:** On-prem servers.
- **Current Issue/Goal:** Migrate containers, min code changes, min dev effort, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `containerized web application` | Đã có container → dùng **ECS/EKS** |
| `minimum code changes` | Giữ nguyên container images |
| `least operational overhead` | **Fargate** (serverless containers) |
| `Application Load Balancer` | Distribute traffic |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Container migration + Operational efficiency
- **Constraints:** Min code changes, min overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **AWS Fargate** — serverless containers, không quản lý infrastructure.
- **Service Auto Scaling** — tự động scale theo request.
- **ALB** — distribute traffic.
- Không cần thay đổi container images → **minimum code changes**.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- 2 EC2 instances — không scale, operational overhead (quản lý OS, Docker).

**❌ Đáp án C:**
- Lambda + API Gateway — yêu cầu **viết lại code**, nhiều dev effort.

**❌ Đáp án D:**
- ParallelCluster HPC — overkill, không phù hợp cho web application.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Fargate = serverless containers (no infra management). Lambda = new code required. EC2 = more overhead"*
