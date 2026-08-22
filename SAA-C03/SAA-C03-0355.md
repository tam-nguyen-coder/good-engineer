# Question #355 - Topic 1

A company is migrating an old application to AWS. The application runs a batch job every hour and is CPU intensive. The batch job takes 15 minutes on average with an on-premises server. The server has 64 virtual CPU (vCPU) and 512 GiB of memory. Which solution will run the batch job within 15 minutes with the LEAST operational overhead?

## Options

**A.** Use AWS Lambda with functional scaling.

**B.** Use Amazon Elastic Container Service (Amazon ECS) with AWS Fargate.

**C.** Use Amazon Lightsail with AWS Auto Scaling.

**D.** Use AWS Batch on Amazon EC2.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CPU-intensive batch job/hourly, 15 min runtime, 64 vCPU + 512 GB RAM on-prem. Need same performance, least operational overhead.
- **Existing Resources:** On-premises server (64 vCPU, 512 GB RAM).
- **Current Issue/Goal:** Migrate batch job, run ≤15 min, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `64 vCPU and 512 GiB` | Large instance needed: Lambda max 6 vCPU/10 GB. Fargate max 16 vCPU/120 GB. Lightsail max 16 vCPU/32 GB. |
| `CPU intensive` | Cần compute-optimized instance. |
| `batch job` | AWS Batch: managed batch computing, tự động provision EC2 instances, queue jobs. |
| `within 15 minutes` | Cần instance đủ mạnh (VD: m5.24xlarge = 96 vCPU, 384 GB). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** CPU intensive, 64 vCPU/512 GB, ≤15 min runtime

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- AWS Batch: managed service cho batch computing, tự động launch EC2 instances (có thể chọn instance type mạnh như m5.24xlarge), run job, terminate instance.
- Lambda/Fargate/Lightsail không đạt 64 vCPU + 512 GB RAM → không thể chạy ≤15 min.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda max 6 vCPU / 10 GB memory → không đủ capacity cho 64 vCPU / 512 GB.

**❌ Đáp án B:**
- Fargate max 16 vCPU / 120 GB → không đủ.

**❌ Đáp án C:**
- Lightsail max 16 vCPU / 32 GB → không đủ.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"64 vCPU + 512 GB → EC2 (AWS Batch). Lambda/Fargate/Lightsail = không đủ capacity."*
