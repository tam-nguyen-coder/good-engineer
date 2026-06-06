# Question #522 - Topic 1

A company runs container applications by using Amazon Elastic Kubernetes Service (Amazon EKS). The company's workload is not consistent throughout the day. The company wants Amazon EKS to scale in and out according to the workload. Which combination of steps will meet these requirements with the LEAST operational overhead? (Choose two.)

## Options

**A.** Use an AWS Lambda function to resize the EKS cluster.

**B.** Use the Kubernetes Metrics Server to activate horizontal pod autoscaling.

**C.** Use the Kubernetes Cluster Autoscaler to manage the number of nodes in the cluster.

**D.** Use Amazon API Gateway and connect it to Amazon EKS.

**E.** Use AWS App Mesh to observe network activity.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EKS cluster với workload không consistent, cần auto scale in/out.
- **Existing Resources:** Amazon EKS cluster.
- **Current Issue/Goal:** Tự động scale EKS theo workload, operational overhead thấp nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `scale in and out` | Pod-level scaling + Node-level scaling |
| `Horizontal Pod Autoscaler (HPA)` | Scale số lượng pod dựa trên CPU/memory metrics |
| `Cluster Autoscaler` | Scale số lượng node trong EKS cluster |
| `Metrics Server` | Cung cấp resource metrics cho HPA |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Workload không consistent, EKS
- **Choose two** options

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và C**

**Giải thích:**
- **B (Metrics Server + HPA):** Metrics Server thu thập CPU/memory metrics từ pods và nodes → HPA tự động scale số lượng pods dựa trên metrics. Đây là native Kubernetes solution.
- **C (Cluster Autoscaler):** Khi HPA tạo thêm pods mà node không đủ resource, Cluster Autoscaler tự động thêm node mới. Khi scale in, nó remove node không cần thiết.
- Kết hợp cả hai: pod-level scaling (HPA) + node-level scaling (Cluster Autoscaler) → giải pháp hoàn chỉnh, operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Dùng Lambda để resize EKS cluster là custom solution, operational overhead cao hơn so với dùng native Kubernetes Cluster Autoscaler.

**❌ Đáp án D:**
- API Gateway dùng để expose REST API, không liên quan đến scaling EKS cluster.

**❌ Đáp án E:**
- App Mesh là service mesh dùng cho observability và traffic management, không phải scaling.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"HPA scale pods, Cluster Autoscaler scale nodes. Cả hai = EKS auto scaling hoàn chỉnh."*
