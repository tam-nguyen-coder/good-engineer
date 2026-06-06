# Question #128 - Topic 1

A company wants to run applications in containers in the AWS Cloud. These applications are stateless and can tolerate disruptions within the underlying infrastructure. The company needs a solution that minimizes cost and operational overhead. What should a solutions architect do to meet these requirements?

## Options

**A.** Use Spot Instances in an Amazon EC2 Auto Scaling group to run the application containers.

**B.** Use Spot Instances in an Amazon Elastic Kubernetes Service (Amazon EKS) managed node group.

**C.** Use On-Demand Instances in an Amazon EC2 Auto Scaling group to run the application containers.

**D.** Use On-Demand Instances in an Amazon Elastic Kubernetes Service (Amazon EKS) managed node group.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Containerized apps, stateless, tolerate disruptions, minimize cost + overhead.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Cost-effective + low overhead container orchestration.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `stateless and can tolerate disruptions` | **Spot Instances** — có thể bị reclaim |
| `minimizes cost` | Spot (rẻ hơn 60-90%) |
| `minimizes operational overhead` | **EKS managed** (AWS quản lý control plane + nodes) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization + Containers
- **Constraints:** Stateless, fault-tolerant, minimize cost + overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **EKS managed node group** — AWS quản lý control plane và node group → giảm operational overhead.
- **Spot Instances** — rẻ nhất, phù hợp cho stateless workload có thể restart.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 ASG + Docker — phải tự quản lý container orchestration → operational overhead cao hơn EKS.

**❌ Đáp án C:**
- On-Demand + ASG — đắt hơn Spot.

**❌ Đáp án D:**
- On-Demand trong EKS — operational overhead thấp nhưng cost cao hơn Spot.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Spot = stateless + fault-tolerant (cheap). EKS managed = less overhead. On-Demand = more cost"*
