# Question #516 - Topic 1

A company provides an API interface to customers so the customers can retrieve their financial information. Еhe company expects a larger number of requests during peak usage times of the year. The company requires the API to respond consistently with low latency to ensure customer satisfaction. The company needs to provide a compute host for the API. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use an Application Load Balancer and Amazon Elastic Container Service (Amazon ECS).

**B.** Use Amazon API Gateway and AWS Lambda functions with provisioned concurrency.

**C.** Use an Application Load Balancer and an Amazon Elastic Kubernetes Service (Amazon EKS) cluster.

**D.** Use Amazon API Gateway and AWS Lambda functions with reserved concurrency.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API cho financial data, peak traffic theo mùa. Cần consistent low latency. Least operational overhead.
- **Existing Resources:** Customer-facing API.
- **Current Issue/Goal:** API serverless/low-overhead, low latency, handle peak traffic.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `consistently with low latency` | Không có cold start → cần provisioned concurrency. |
| `peak usage times` | Traffic không đều → serverless scale phù hợp. |
| `MOST operational overhead` | Cần giải pháp managed/serverless. |
| `provisioned concurrency` | Giữ Lambda warm sẵn → zero cold start → low latency. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Low latency (consistent), handle peaks

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- API Gateway + Lambda là serverless, không cần quản lý servers → operational overhead thấp nhất.
- Provisioned concurrency: khởi tạo sẵn một số Lambda execution environments → cold start không xảy ra → consistent low latency.
- Lambda tự động scale khi peak traffic, API Gateway tự động scale → phù hợp với unpredictable peak.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ALB + ECS: cần quản lý container cluster (EC2 hoặc Fargate). Operational overhead cao hơn Lambda.
- ECS không scale nhanh bằng Lambda.

**❌ Đáp án C:**
- ALB + EKS: Kubernetes cluster có operational overhead rất cao. Cần quản lý control plane, worker nodes, networking, monitoring.
- Không phải lựa chọn "least operational overhead".

**❌ Đáp án D:**
- Reserved concurrency chỉ giới hạn maximum concurrency (không cho Lambda scale vượt quá limit). Không giúp giảm cold start.
- Ngược lại, nó có thể gây throttling khi peak traffic (Lambda bị giới hạn).
- Provisioned concurrency (B) mới giải quyết cold start và low latency.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API low latency + serverless → API Gateway + Lambda + provisioned concurrency (giữ warm). Reserved concurrency = giới hạn, không giúp latency."*
