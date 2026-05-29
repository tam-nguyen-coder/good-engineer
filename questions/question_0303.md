# Question #303 - Topic 1

A company is launching a new application deployed on an Amazon Elastic Container Service (Amazon ECS) cluster and is using the Fargate launch type for ECS tasks. The company is monitoring CPU and memory usage because it is expecting high traffic to the application upon its launch. However, the company wants to reduce costs when utilization decreases. What should a solutions architect recommend?

## Options

**A.** Use Amazon EC2 Auto Scaling to scale at certain periods based on previous traffic patterns.

**B.** Use an AWS Lambda function to scale Amazon ECS based on metric breaches that trigger an Amazon CloudWatch alarm.

**C.** Use Amazon EC2 Auto Scaling with simple scaling policies to scale when ECS metric breaches trigger an Amazon CloudWatch alarm.

**D.** Use AWS Application Auto Scaling with target tracking policies to scale when ECS metric breaches trigger an Amazon CloudWatch alarm.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ECS Fargate tasks, expected high traffic, muốn auto scale để giảm cost khi utilization thấp.
- **Existing Resources:** ECS cluster with Fargate launch type.
- **Current Issue/Goal:** Auto scale ECS services based on CPU/memory metrics.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Fargate launch type` | Serverless container, không quản lý EC2 instances. |
| `ECS tasks` | Cần Application Auto Scaling (ECS Service Auto Scaling), không phải EC2 Auto Scaling. |
| `target tracking policies` | Tự động scale để giữ target metric (VD: CPU 70%). |
| `reduce costs when utilization decreases` | Tự động scale in. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** ECS Fargate, auto scale based on utilization

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- AWS Application Auto Scaling hỗ trợ ECS services (cả Fargate và EC2 launch type) với target tracking policies.
- Target tracking tự động scale out/in để giữ CPU/memory ở target value → cost-efficient.
- Fargate tasks được scale bằng Application Auto Scaling, không phải EC2 Auto Scaling.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 Auto Scaling chỉ scale EC2 instances, không scale ECS tasks. Với Fargate, bạn không quản lý EC2 instances.

**❌ Đáp án B:**
- Có thể dùng Lambda + CloudWatch, nhưng Application Auto Scaling đã có sẵn, đơn giản hơn và là best practice.

**❌ Đáp án C:**
- EC2 Auto Scaling không scale ECS tasks/Fargate. Simple scaling policies cũng kém linh hoạt hơn target tracking.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ECS Fargate → Application Auto Scaling (not EC2 ASG). Target tracking = tự động scale giữ CPU/memory target."*
