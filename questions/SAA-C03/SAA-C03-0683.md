# Question #683 - Topic 1

A company is migrating its multi-tier on-premises application to AWS. The application consists of a single-node MySQL database and a multi-node web tier. The company must minimize changes to the application during the migration. The company wants to improve application resiliency after the migration. Which combination of steps will meet these requirements? (Choose two.)

## Options

**A.** Migrate the web tier to Amazon EC2 instances in an Auto Scaling group behind an Application Load Balancer.

**B.** Migrate the database to Amazon EC2 instances in an Auto Scaling group behind a Network Load Balancer.

**C.** Migrate the database to an Amazon RDS Multi-AZ deployment.

**D.** Migrate the web tier to an AWS Lambda function.

**E.** Migrate the database to an Amazon DynamoDB table.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-tier app: single-node MySQL + multi-node web tier. Minimize changes, improve resiliency.
- **Existing Resources:** On-prem MySQL database, multi-node web tier.
- **Current Issue/Goal:** Migrate with minimal changes, improve HA.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimize changes` | Giữ nguyên MySQL (không chuyển sang DynamoDB). Lambda requires code change. |
| `improve application resiliency` | RDS Multi-AZ (HA) + ALB + ASG (auto-healing). |
| `single-node MySQL` | RDS Multi-AZ → automated failover, HA. |
| `multi-node web tier` | ALB + ASG → scale, HA. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (choose two)
- **Constraints:** Minimize changes, improve resiliency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và C**

**Giải thích:**
- **A:** Web tier: EC2 trong ASG + ALB → HA, tự động scale, không cần thay đổi code (giữ nguyên web server).
- **C:** Database: RDS MySQL Multi-AZ → managed, tự động failover nếu primary fail, HA, không cần code changes.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Database trên EC2 ASG + NLB: không phù hợp (relational DB không stateless). Operational overhead cao.

**❌ Đáp án D:**
- Lambda: cần rewrite application code, không phải "minimize changes".

**❌ Đáp án E:**
- DynamoDB: NoSQL, cần rewrite application, không compatible với MySQL.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"MySQL HA → RDS Multi-AZ. Web tier HA → ALB + ASG. Minimal changes = keep MySQL."*
