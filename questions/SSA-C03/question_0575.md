# Question #575 - Topic 1

A company deploys its applications on Amazon Elastic Kubernetes Service (Amazon EKS) behind an Application Load Balancer in an AWS Region. The application needs to store data in a PostgreSQL database engine. The company wants the data in the database to be highly available. The company also needs increased capacity for read workloads. Which solution will meet these requirements with the MOST operational efficiency?

## Options

**A.** Create an Amazon DynamoDB database table configured with global tables.

**B.** Create an Amazon RDS database with Multi-AZ deployments.

**C.** Create an Amazon RDS database with Multi-AZ DB cluster deployment.

**D.** Create an Amazon RDS database configured with cross-Region read replicas.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EKS + ALB, cần PostgreSQL database, high availability, và increased capacity for read workloads.
- **Existing Resources:** EKS cluster, ALB.
- **Current Issue/Goal:** HA + read capacity cho PostgreSQL.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `PostgreSQL` | Cần relational database PostgreSQL. |
| `highly available` | Multi-AZ replication. |
| `increased capacity for read workloads` | Cần read replicas. |
| `Multi-AZ DB cluster` | 1 primary + 2 readable standby instances trong 3 AZ → vừa HA vừa read capacity. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operational efficiency
- **Constraints:** PostgreSQL, HA, read capacity

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Multi-AZ DB cluster deployment: 1 primary writer + 2 readable standby instances trong 3 AZ.
- Cung cấp HA (failover tự động) và read capacity (có thể đọc từ standby instances).
- Operational efficiency cao vì all-in-one solution, không cần manage thêm read replicas riêng.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DynamoDB là NoSQL, không PostgreSQL-compatible.

**❌ Đáp án B:**
- Multi-AZ deployment (classic): standby không readable → chỉ có HA, không tăng read capacity.

**❌ Đáp án D:**
- Cross-Region read replicas: giải quyết read capacity nhưng cross-Region (latency + cost), không phải HA trong cùng Region.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-AZ DB Cluster = HA + readable standbys (3 AZ). Classic Multi-AZ = HA only (standby không đọc được)."*
