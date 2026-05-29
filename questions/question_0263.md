# Question #263 - Topic 1

A company is building an application that consists of several microservices. The company has decided to use container technologies to deploy its software on AWS. The company needs a solution that minimizes the amount of ongoing effort for maintenance and scaling. The company cannot manage additional infrastructure. Which combination of actions should a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Deploy an Amazon Elastic Container Service (Amazon ECS) cluster.

**B.** Deploy the Kubernetes control plane on Amazon EC2 instances that span multiple Availability Zones.

**C.** Deploy an Amazon Elastic Container Service (Amazon ECS) service with an Amazon EC2 launch type. Specify a desired task number level of greater than or equal to 2.

**D.** Deploy an Amazon Elastic Container Service (Amazon ECS) service with a Fargate launch type. Specify a desired task number level of greater than or equal to 2.

**E.** Deploy Kubernetes worker nodes on Amazon EC2 instances that span multiple Availability Zones. Create a deployment that specifies two or more replicas for each microservice.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Containerized microservices. Min maintenance/scaling effort. Cannot manage infrastructure.
- **Existing Resources:** None.
- **Current Issue/Goal:** Serverless containers.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimizes... effort for maintenance and scaling` | **Fargate** (serverless) |
| `cannot manage additional infrastructure` | No EC2 management |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Containers / Serverless
- **Constraints:** Chọn 2, no infrastructure management

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và D**

**Giải thích:**
- **A: ECS cluster** — managed container orchestration.
- **D: ECS Fargate launch type** — serverless, không quản lý EC2 instances.
- Fargate tự động scale, patching, maintenance.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Self-managed Kubernetes control plane — cần quản lý infrastructure.

**❌ Đáp án C:**
- ECS EC2 launch type — cần quản lý worker nodes.

**❌ Đáp án E:**
- Self-managed Kubernetes workers — cần quản lý EC2.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ECS + Fargate = serverless containers (no infra). ECS EC2 / self-managed K8s = manage infra"*
