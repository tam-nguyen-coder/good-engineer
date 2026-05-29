# Question #390 - Topic 1

A company hosts a three-tier ecommerce application on a fleet of Amazon EC2 instances. The instances run in an Auto Scaling group behind an Application Load Balancer (ALB). All ecommerce data is stored in an Amazon RDS for MariaDB Multi-AZ DB instance. The company wants to optimize customer session management during transactions. The application must store session data durably. Which solutions will meet these requirements? (Choose two.)

## Options

**A.** Turn on the sticky sessions feature (session affinity) on the ALB.

**B.** Use an Amazon DynamoDB table to store customer session information.

**C.** Deploy an Amazon Cognito user pool to manage user session information.

**D.** Deploy an Amazon ElastiCache for Redis cluster to store customer session information.

**E.** Use AWS Systems Manager Application Manager in the application to manage user session information.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce app, ASG + ALB, RDS MariaDB Multi-AZ. Cần durable session storage.
- **Existing Resources:** ASG, ALB, RDS MariaDB.
- **Current Issue/Goal:** Optimize session management, durable storage.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `store session data durably` | Cần persistent/durable storage cho sessions. |
| `DynamoDB` | Durable, scalable, serverless session store. |
| `ElastiCache for Redis` | In-memory + AOF persistence (durable), fast session storage. |
| `sticky sessions` | Ephemeral (instance-bound), không durable. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two, durable session storage
- **Constraints:** ASG (instances come and go), durable

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B (DynamoDB) và D (ElastiCache for Redis)**

**Giải thích:**
- **B (DynamoDB):** Durable (multi-AZ), auto-scaling, serverless → centralized session store cho ASG.
- **D (ElastiCache for Redis):** In-memory + AOF persistence → fast and durable. Hỗ trợ replication và failover.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Sticky sessions: gắn user vào 1 instance. Nếu instance bị terminated, session mất. Không durable.

**❌ Đáp án C:**
- Cognito user pools: authentication/authorization, không phải session storage.

**❌ Đáp án E:**
- Systems Manager AppManager: quản lý ứng dụng, không phải session store.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Durable session storage cho ASG → DynamoDB hoặc ElastiCache Redis (AOF). Sticky sessions = không durable (instance-bound)."*
