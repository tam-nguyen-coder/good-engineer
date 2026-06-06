# Question #424 - Topic 1

A company is running a custom application on Amazon EC2 On-Demand Instances. The application has frontend nodes that need to run 24 hours a day, 7 days a week and backend nodes that need to run only for a short time based on workload. The number of backend nodes varies during the day. The company needs to scale out and scale in more instances based on workload. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Use Reserved Instances for the frontend nodes. Use AWS Fargate for the backend nodes.

**B.** Use Reserved Instances for the frontend nodes. Use Spot Instances for the backend nodes.

**C.** Use Spot Instances for the frontend nodes. Use Reserved Instances for the backend nodes.

**D.** Use Spot Instances for the frontend nodes. Use AWS Fargate for the backend nodes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Frontend: 24/7. Backend: short-lived, variable load. Most cost-effective.
- **Existing Resources:** EC2 On-Demand instances.
- **Current Issue/Goal:** Optimize cost: RI for steady, Spot for variable.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `24 hours a day, 7 days a week` | Reserved Instances: cost saving cho workload ổn định. |
| `short time based on workload` | Spot Instances: rẻ nhất (60-90%), có thể bị interrupt. |
| `most cost-effectively` | RI (steady) + Spot (variable). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Frontend 24/7, backend short/variable

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Frontend 24/7 → Reserved Instances: trả trước, giảm giá so với On-Demand.
- Backend short-lived, variable → Spot Instances: rẻ nhất, có thể scale nhanh.
- Spot phù hợp cho fault-tolerant, stateless backend workloads.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Fargate: serverless container, không phải EC2. Frontend vẫn là EC2 RI ok, nhưng backend Fargate không rẻ bằng Spot cho short-lived tasks.

**❌ Đáp án C:**
- Spot cho frontend 24/7: risk bị interrupt → không phù hợp workload steady.

**❌ Đáp án D:**
- Spot cho frontend: tương tự C, không phù hợp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Steady 24/7 → Reserved. Variable/short → Spot. Spot for fault-tolerant workloads."*