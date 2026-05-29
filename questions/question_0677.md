# Question #677 - Topic 1

A company is developing an application that will run on a production Amazon Elastic Kubernetes Service (Amazon EKS) cluster. The EKS cluster has managed node groups that are provisioned with On-Demand Instances. The company needs a dedicated EKS cluster for development work. The company will use the development cluster infrequently to test the resiliency of the application. The EKS cluster must manage all the nodes. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Create a managed node group that contains only Spot Instances.

**B.** Create two managed node groups. Provision one node group with On-Demand Instances. Provision the second node group with Spot Instances.

**C.** Create an Auto Scaling group that has a launch configuration that uses Spot Instances. Configure the user data to add the nodes to the EKS cluster.

**D.** Create a managed node group that contains only On-Demand Instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Production EKS with managed node groups (On-Demand). Need dev EKS cluster used infrequently, cost-effective. Cluster must manage all nodes (managed node groups).
- **Existing Resources:** Production EKS cluster with managed node groups (On-Demand).
- **Current Issue/Goal:** Cost-effective dev EKS cluster with managed node groups.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `EKS cluster must manage all the nodes` | Phải dùng managed node groups (EKS manages). |
| `infrequently` | Spot Instances: tiết kiệm 60-90% so với On-Demand. |
| `Spot Instances` | Phù hợp cho non-production, fault-tolerant workloads. |
| `most cost-effectively` | Spot Instances là rẻ nhất. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Managed node groups, infrequent dev use

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Managed node group với Spot Instances: EKS tự quản lý nodes, giá rẻ hơn nhiều so với On-Demand.
- Dev cluster dùng không thường xuyên → Spot Instances là lựa chọn tiết kiệm nhất.
- Spot Instances có thể bị reclaim, nhưng dev cluster có thể chịu được interruption.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Hai managed node groups (On-Demand + Spot) tốn kém hơn chỉ dùng Spot.

**❌ Đáp án C:**
- Auto Scaling group tự quản lý (không phải managed node group) → violates "cluster must manage all nodes".

**❌ Đáp án D:**
- On-Demand Instances đắt hơn Spot, không cost-effective cho infrequent dev use.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Dev EKS infrequent use → managed node group with Spot Instances (cheapest)."*
