# Question #163 - Topic 1

A company is building a containerized application on premises and decides to move the application to AWS. The application will have thousands of users soon after it is deployed. The company is unsure how to manage the deployment of containers at scale. The company needs to deploy the containerized application in a highly available architecture that minimizes operational overhead. Which solution will meet these requirements?

## Options

**A.** Store container images in an Amazon Elastic Container Registry (Amazon ECR) repository. Use an Amazon Elastic Container Service (Amazon ECS) cluster with the AWS Fargate launch type to run the containers. Use target tracking to scale automatically based on demand.

**B.** Store container images in an Amazon Elastic Container Registry (Amazon ECR) repository. Use an Amazon Elastic Container Service (Amazon ECS) cluster with the Amazon EC2 launch type to run the containers. Use target tracking to scale automatically based on demand.

**C.** Store container images in a repository that runs on an Amazon EC2 instance. Run the containers on EC2 instances that are spread across multiple Availability Zones. Monitor the average CPU utilization in Amazon CloudWatch. Launch new EC2 instances as needed.

**D.** Create an Amazon EC2 Amazon Machine Image (AMI) that contains the container image. Launch EC2 instances in an Auto Scaling group across multiple Availability Zones. Use an Amazon CloudWatch alarm to scale out EC2 instances when the average CPU utilization threshold is breached.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Containerized app moving to AWS, thousands of users, HA, min operational overhead.
- **Existing Resources:** Containerized app.
- **Current Issue/Goal:** Managed container deployment at scale.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `containerized application` | Cần container orchestration |
| `minimizes operational overhead` | **Fargate** (serverless containers) |
| `highly available` | Multi-AZ |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Container deployment
- **Constraints:** HA, min overhead, scale

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **ECR** — managed container registry.
- **ECS Fargate** — serverless containers, không quản lý infrastructure.
- **Target tracking** — auto-scale dựa trên demand.
- **HA** — Fargate tự động phân bố containers across AZs.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ECS EC2 launch type — phải quản lý worker nodes (EC2).

**❌ Đáp án C:**
- Self-managed EC2 — highest operational overhead.

**❌ Đáp án D:**
- AMI with container image — không tận dụng container orchestration.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Fargate = serverless containers. ECS EC2 = manage nodes. Self-managed = most overhead"*
