# Question #458 - Topic 1

A solutions architect is designing a REST API in Amazon API Gateway for a cash payback service. The application requires 1 GB of memory and 2 GB of storage for its computation resources. The application will require that the data is in a relational format. Which additional combination of AWS services will meet these requirements with the LEAST administrative effort? (Choose two.)

## Options

**A.** Amazon EC2

**B.** AWS Lambda

**C.** Amazon RDS

**D.** Amazon DynamoDB

**E.** Amazon Elastic Kubernetes Services (Amazon EKS)

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway REST API. Need 1GB memory, 2GB storage compute. Relational data.
- **Existing Resources:** API Gateway.
- **Current Issue/Goal:** Compute + database with least admin effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `1 GB of memory` | Lambda supports up to 10GB memory. |
| `2 GB of storage` | Lambda /tmp directory up to 10GB. |
| `relational format` | RDS (relational), not DynamoDB (NoSQL). |
| `least administrative effort` | Serverless + managed services. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless / Least admin effort
- **Constraints:** 1GB memory, 2GB storage, relational data

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B, C**

**Giải thích:**
- **B:** Lambda: serverless compute. 1GB memory supported, /tmp storage up to 10GB (đáp ứng 2GB). Least admin effort.
- **C:** RDS: managed relational database. SQL, ACID, relationships. Least admin effort (automated patching, backup).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2: self-managed OS, runtime → nhiều admin effort hơn Lambda.

**❌ Đáp án D:**
- DynamoDB: NoSQL, không relational.

**❌ Đáp án E:**
- EKS: managed Kubernetes nhưng vẫn cần quản lý cluster, pods, etc. → admin effort hơn Lambda.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API + compute + relational DB → Lambda (1GB RAM) + RDS. DynamoDB = NoSQL."*