# Question #143 - Topic 1

A company wants to migrate its existing on-premises monolithic application to AWS. The company wants to keep as much of the front-end code and the backend code as possible. However, the company wants to break the application into smaller applications. A different team will manage each application. The company needs a highly scalable solution that minimizes operational overhead. Which solution will meet these requirements?

## Options

**A.** Host the application on AWS Lambda. Integrate the application with Amazon API Gateway.

**B.** Host the application with AWS Amplify. Connect the application to an Amazon API Gateway API that is integrated with AWS Lambda.

**C.** Host the application on Amazon EC2 instances. Set up an Application Load Balancer with EC2 instances in an Auto Scaling group as targets.

**D.** Host the application on Amazon Elastic Container Service (Amazon ECS). Set up an Application Load Balancer with Amazon ECS as the target.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate monolithic app → microservices (break into smaller apps). Keep code as much as possible.
- **Existing Resources:** On-prem monolithic application.
- **Current Issue/Goal:** Microservices, highly scalable, min operational overhead, min code changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `break the application into smaller applications` | Microservices architecture |
| `keep as much of the... code as possible` | Containerize existing code |
| `minimizes operational overhead` | Managed orchestration |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration + Microservices
- **Constraints:** Min code changes, scalable, min overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **ECS** — container orchestration, cho phép chạy monolithic app trong containers với ít thay đổi code.
- Break thành microservices dần dần, mỗi service là một ECS service riêng.
- **ALB** — route traffic đến các containers.
- Scalable, managed orchestration.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda + API Gateway — yêu cầu viết lại code (phải refactor thành functions), không giữ được code.

**❌ Đáp án B:**
- Amplify — frontend framework, không phù hợp cho backend monolith migration.

**❌ Đáp án C:**
- EC2 ASG — không có container orchestration, phải tự quản lý.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ECS = containerize monolith → microservices. Lambda = rewrite code. EC2 = more overhead"*
