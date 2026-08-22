# Question #58 - Topic 1

A company wants to run its critical applications in containers to meet requirements for scalability and availability. The company prefers to focus on maintenance of the critical applications. The company does not want to be responsible for provisioning and managing the underlying infrastructure that runs the containerized workload. What should a solutions architect do to meet these requirements?

## Options

**A.** Use Amazon EC2 instances, and install Docker on the instances.

**B.** Use Amazon Elastic Container Service (Amazon ECS) on Amazon EC2 worker nodes.

**C.** Use Amazon Elastic Container Service (Amazon ECS) on AWS Fargate.

**D.** Use Amazon EC2 instances from an Amazon Elastic Container Service (Amazon ECS)-optimized Amazon Machine Image (AMI).

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Chạy critical applications trong containers, không muốn quản lý infrastructure.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Focus on app maintenance, không quản lý underlying infrastructure.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `does not want to be responsible for provisioning and managing the underlying infrastructure` | Serverless containers → Fargate |
| `containers` | ECS hoặc EKS |
| `scalability and availability` | Cần managed scaling |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Operational overhead
- **Constraints:** Không quản lý infrastructure, containerized

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **AWS Fargate** là serverless compute engine cho containers — không cần quản lý EC2 instances, cluster, hay worker nodes.
- **ECS on Fargate** tự động scale, patching, và quản lý infrastructure — team chỉ focus vào ứng dụng.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Tự cài Docker trên EC2 — phải quản lý OS, Docker, patching, scaling → nhiều operational overhead.

**❌ Đáp án B:**
- **ECS on EC2** vẫn phải quản lý worker nodes (EC2 instances), scaling, patching.

**❌ Đáp án D:**
- ECS-optimized AMI trên EC2 — vẫn phải tự quản lý infrastructure.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Fargate = serverless containers (no infrastructure management). ECS on EC2 = still manage servers"*
