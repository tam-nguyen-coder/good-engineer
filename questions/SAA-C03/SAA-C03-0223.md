# Question #223 - Topic 1

A company has deployed a Java Spring Boot application as a pod that runs on Amazon Elastic Kubernetes Service (Amazon EKS) in private subnets. The application needs to write data to an Amazon DynamoDB table. A solutions architect must ensure that the application can interact with the DynamoDB table without exposing traffic to the internet. Which combination of steps should the solutions architect take to accomplish this goal? (Choose two.)

## Options

**A.** Attach an IAM role that has sufficient privileges to the EKS pod.

**B.** Attach an IAM user that has sufficient privileges to the EKS pod.

**C.** Allow outbound connectivity to the DynamoDB table through the private subnets' network ACLs.

**D.** Create a VPC endpoint for DynamoDB.

**E.** Embed the access keys in the Java Spring Boot code.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EKS pod in private subnet → DynamoDB. No internet exposure.
- **Existing Resources:** EKS cluster, private subnets.
- **Current Issue/Goal:** Private access + IAM permissions.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `without exposing traffic to the internet` | **VPC Gateway Endpoint** for DynamoDB |
| `EKS pod` | **IAM role for service account (IRSA)** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Networking
- **Constraints:** Chọn 2, private, EKS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và D**

**Giải thích:**
- **A: IAM role for EKS pod** — IRSA (IAM Roles for Service Accounts) gán permissions cho pod.
- **D: VPC Gateway Endpoint for DynamoDB** — cho phép traffic từ private subnet đến DynamoDB qua AWS network, không qua internet.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- IAM user — không nên gán cho pod, best practice là IAM role.

**❌ Đáp án C:**
- NACL — không đủ, chỉ network-level, vẫn cần IAM permissions.

**❌ Đáp án E:**
- Embed access keys — bad practice, security risk.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EKS pod + DynamoDB = IRSA (IAM role) + VPC Gateway Endpoint. Access keys = bad practice"*
