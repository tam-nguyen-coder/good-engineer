# Question #140 - Topic 1

A solutions architect needs to help a company optimize the cost of running an application on AWS. The application will use Amazon EC2 instances, AWS Fargate, and AWS Lambda for compute within the architecture. The EC2 instances will run the data ingestion layer of the application. EC2 usage will be sporadic and unpredictable. Workloads that run on EC2 instances can be interrupted at any time. The application front end will run on Fargate, and Lambda will serve the API layer. The front-end utilization and API layer utilization will be predictable over the course of the next year. Which combination of purchasing options will provide the MOST cost-effective solution for hosting this application? (Choose two.)

## Options

**A.** Use Spot Instances for the data ingestion layer

**B.** Use On-Demand Instances for the data ingestion layer

**C.** Purchase a 1-year Compute Savings Plan for the front end and API layer.

**D.** Purchase 1-year All Upfront Reserved instances for the data ingestion layer.

**E.** Purchase a 1-year EC2 instance Savings Plan for the front end and API layer.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 (sporadic, interruptible), Fargate (front-end, predictable), Lambda (API, predictable).
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Most cost-effective purchasing options.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sporadic and unpredictable` | **Spot Instances** |
| `can be interrupted at any time` | Spot — phù hợp vì có thể interrupt |
| `predictable` | **Savings Plan** (1-year) |
| `Fargate... Lambda` | Compute Savings Plan (covers EC2, Fargate, Lambda) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Chọn 2

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và C**

**Giải thích:**
- **A: Spot Instances** cho data ingestion — sporadic, interruptible → rẻ nhất.
- **C: Compute Savings Plan** — covers **Fargate + Lambda** (và EC2 nếu cần), linh hoạt hơn EC2 Instance Savings Plan.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- On-Demand cho sporadic workload — đắt hơn Spot.

**❌ Đáp án D:**
- Reserved Instance cho sporadic workload — không optimal, RI tốt cho steady state 24/7.

**❌ Đáp án E:**
- EC2 Instance Savings Plan — chỉ cover EC2, **không cover Fargate và Lambda**.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Spot = sporadic + interruptible. Compute Savings Plan = covers EC2 + Fargate + Lambda. EC2 SP = EC2 only"*
