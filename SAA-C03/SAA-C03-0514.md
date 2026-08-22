# Question #514 - Topic 1

A company is running a microservices application on Amazon EC2 instances. The company wants to migrate the application to an Amazon Elastic Kubernetes Service (Amazon EKS) cluster for scalability. The company must configure the Amazon EKS control plane with endpoint private access set to true and endpoint public access set to false to maintain security compliance. The company must also put the data plane in private subnets. However, the company has received error notifications because the node cannot join the cluster. Which solution will allow the node to join the cluster?

## Options

**A.** Grant the required permission in AWS Identity and Access Management (IAM) to the AmazonEKSNodeRole IAM role.

**B.** Create interface VPC endpoints to allow nodes to access the control plane.

**C.** Recreate nodes in the public subnet. Restrict security groups for EC2 nodes.

**D.** Allow outbound traffic in the security group of the nodes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate EC2 microservices lên EKS. EKS control plane: private endpoint only (public = false). Data plane (nodes) trong private subnet. Nodes không join được cluster.
- **Existing Resources:** EKS cluster, EC2 instances (sẽ làm node).
- **Current Issue/Goal:** Nodes trong private subnet không thể kết nối đến control plane.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `endpoint private access = true` | Control plane chỉ có private endpoint (trong VPC). |
| `endpoint public access = false` | Không có public endpoint. |
| `data plane in private subnets` | Nodes không có NAT/internet access. |
| `node cannot join the cluster` | Mất kết nối từ node đến control plane. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Troubleshoot connectivity
- **Constraints:** Private control plane + private subnets

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Khi EKS control plane chỉ có private endpoint và nodes ở private subnet không có NAT Gateway, nodes không thể reach control plane qua internet.
- Giải pháp: tạo interface VPC endpoints (AWS PrivateLink) cho EKS, ECR, và các service khác (EC2, S3...) để nodes có thể kết nối đến control plane và pull images từ ECR mà không cần internet.
- Interface VPC endpoints cho phép private connectivity giữa VPC và AWS services mà không cần NAT/IGW.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- IAM role (AmazonEKSNodeRole) cần đúng permission, nhưng lỗi không join được cluster thường là do network, không phải IAM. Nếu IAM sai, error message khác.

**❌ Đáp án C:**
- Recreate nodes trong public subnet: vi phạm yêu cầu "put the data plane in private subnets" và security compliance.
- Không phải giải pháp đúng.

**❌ Đáp án D:**
- Allow outbound traffic trong security group của nodes có thể giúp nếu nodes có NAT/internet access, nhưng nodes ở private subnet không có internet connectivity.
- Với private endpoint only + private subnets, SG outbound không giải quyết được vấn đề thiếu route đến control plane.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EKS private endpoint + private subnets → cần VPC endpoints (PrivateLink) để node reach control plane."*
