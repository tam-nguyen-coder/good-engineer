# Question #198 - Topic 1

A company runs a containerized application on a Kubernetes cluster in an on-premises data center. The company is using a MongoDB database for data storage. The company wants to migrate some of these environments to AWS, but no code changes or deployment method changes are possible at this time. The company needs a solution that minimizes operational overhead. Which solution meets these requirements?

## Options

**A.** Use Amazon Elastic Container Service (Amazon ECS) with Amazon EC2 worker nodes for compute and MongoDB on EC2 for data storage.

**B.** Use Amazon Elastic Container Service (Amazon ECS) with AWS Fargate for compute and Amazon DynamoDB for data storage

**C.** Use Amazon Elastic Kubernetes Service (Amazon EKS) with Amazon EC2 worker nodes for compute and Amazon DynamoDB for data storage.

**D.** Use Amazon Elastic Kubernetes Service (Amazon EKS) with AWS Fargate for compute and Amazon DocumentDB (with MongoDB compatibility) for data storage.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Kubernetes + MongoDB on-prem. Migrate to AWS, no code/deployment method changes. Min overhead.
- **Existing Resources:** Kubernetes cluster, MongoDB.
- **Current Issue/Goal:** Compatible migration, min overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Kubernetes cluster` | **Amazon EKS** (managed Kubernetes) |
| `MongoDB` | **Amazon DocumentDB** (MongoDB-compatible) |
| `no code changes or deployment method changes` | Giữ nguyên Kubernetes + MongoDB-compatible DB |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Container / Migration
- **Constraints:** Kubernetes, MongoDB-compatible, min overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **EKS Fargate** — managed Kubernetes, serverless compute, Kubernetes-compatible → deployment method giống on-prem.
- **DocumentDB** — MongoDB-compatible, managed → no code changes.
- Fargate → no worker node management → min operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ECS — deployment method khác Kubernetes, cần thay đổi.

**❌ Đáp án B:**
- ECS + DynamoDB — deployment method + DB thay đổi.

**❌ Đáp án C:**
- EKS + DynamoDB — Kubernetes giống, nhưng DynamoDB khác MongoDB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EKS = managed Kubernetes. DocumentDB = MongoDB-compatible. ECS = different orchestration"*
