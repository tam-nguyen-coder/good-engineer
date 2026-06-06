# Question #563 - Topic 1

A company runs its applications on both Amazon Elastic Kubernetes Service (Amazon EKS) clusters and on-premises Kubernetes clusters. The company wants to view all clusters and workloads from a central location. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use Amazon CloudWatch Container Insights to collect and group the cluster information.

**B.** Use Amazon EKS Connector to register and connect all Kubernetes clusters.

**C.** Use AWS Systems Manager to collect and view the cluster information.

**D.** Use Amazon EKS Anywhere as the primary cluster to view the other clusters with native Kubernetes commands.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty chạy ứng dụng trên EKS clusters và on-premises Kubernetes clusters. Cần xem tất cả clusters và workloads từ một central location.
- **Existing Resources:** EKS clusters, on-premises Kubernetes clusters.
- **Current Issue/Goal:** Centralized view của tất cả clusters, ít operational overhead nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `view all clusters and workloads` | Centralized cluster management/visibility |
| `Amazon EKS` | Managed Kubernetes trên AWS |
| `on-premises Kubernetes` | Kubernetes không phải trên AWS |
| `Amazon EKS Connector` | Dịch vụ register và kết nối bất kỳ Kubernetes cluster nào vào AWS console |
| `central location` | AWS Console (EKS console) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Centralized view, cả EKS và on-premises clusters

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Amazon EKS Connector là tính năng của EKS cho phép đăng ký bất kỳ Kubernetes cluster nào (bao gồm on-premises, các cloud khác) vào EKS console.
- Sau khi register, có thể xem tất cả clusters, workloads, và tài nguyên Kubernetes từ EKS console – một central location.
- Chỉ cần cài đặt EKS Connector agent trên on-premises cluster và cấu hình IAM permissions.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (CloudWatch Container Insights):** Container Insights cung cấp monitoring metrics và logs cho containers, nhưng không cung cấp khả năng "view all clusters and workloads" như một centralized management console.

**❌ Đáp án C (Systems Manager):** AWS Systems Manager quản lý EC2 instances và on-premises servers, không hỗ trợ Kubernetes cluster management.

**❌ Đáp án D (EKS Anywhere):** EKS Anywhere là giải pháp chạy EKS on-premises. Nó không phải là công cụ centralized để xem tất cả clusters; nó chỉ là một cluster khác. Yêu cầu cài đặt và quản lý phức tạp hơn EKS Connector.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Centralized Kubernetes view = EKS Connector. Register any K8s cluster (on-prem, other clouds) to EKS console."*
