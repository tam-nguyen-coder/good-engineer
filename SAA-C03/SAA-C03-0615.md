# Question #615 - Topic 1

A company runs a critical, customer-facing application on Amazon Elastic Kubernetes Service (Amazon EKS). The application has a microservices architecture. The company needs to implement a solution that collects, aggregates, and summarizes metrics and logs from the application in a centralized location. Which solution meets these requirements?

## Options

**A.** Run the Amazon CloudWatch agent in the existing EKS cluster. View the metrics and logs in the CloudWatch console.

**B.** Run AWS App Mesh in the existing EKS cluster. View the metrics and logs in the App Mesh console.

**C.** Configure AWS CloudTrail to capture data events. Query CloudTrail by using Amazon OpenSearch Service.

**D.** Configure Amazon CloudWatch Container Insights in the existing EKS cluster. View the metrics and logs in the CloudWatch console.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EKS cluster chạy microservices application, cần collect, aggregate, summarize metrics và logs từ application vào centralized location.
- **Existing Resources:** Amazon EKS cluster, microservices.
- **Current Issue/Goal:** Centralized monitoring (metrics + logs) cho EKS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `EKS` | Amazon Elastic Kubernetes Service. |
| `microservices architecture` | Nhiều services nhỏ, cần centralized monitoring. |
| `collect, aggregate, and summarize metrics and logs` | CloudWatch Container Insights chuyên cho container monitoring. |
| `centralized location` | CloudWatch console. |
| `Container Insights` | Dịch vụ chuyên thu thập metrics/logs từ container environments (EKS, ECS, K8s). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** EKS, microservices, centralized metrics + logs

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- CloudWatch Container Insights là giải pháp chuyên biệt cho container monitoring trên EKS, ECS, và Kubernetes.
- Tự động thu thập metrics (CPU, memory, network) và logs từ containers.
- Cung cấp dashboards tổng hợp, phân tích và tương quan metrics/logs trong CloudWatch console.
- Dễ dàng cấu hình trên EKS cluster.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudWatch agent có thể collect metrics và logs, nhưng Container Insights (D) là giải pháp chuyên dụng cho containers với khả năng aggregate và summarize tốt hơn.
- Tuy nhiên, trên thực tế Container Insights cũng chạy CloudWatch agent với configuration đặc biệt, nhưng Container Insights mang nhiều tính năng hơn cho container workloads.

**❌ Đáp án B:**
- AWS App Mesh là service mesh cho microservices communication, tập trung vào traffic routing và observability (envoys), không phải logs/metrics aggregation.

**❌ Đáp án C:**
- CloudTrail capture API calls (control plane + data events), không phải application metrics và logs.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EKS + metrics/logs → CloudWatch Container Insights. App Mesh = service mesh, CloudTrail = API logs."*
