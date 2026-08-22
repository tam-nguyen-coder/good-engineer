# Question #187 - Topic 1

A company is developing an ecommerce application that will consist of a load-balanced front end, a container-based application, and a relational database. A solutions architect needs to create a highly available solution that operates with as little manual intervention as possible. Which solutions meet these requirements? (Choose two.)

## Options

**A.** Create an Amazon RDS DB instance in Multi-AZ mode.

**B.** Create an Amazon RDS DB instance and one or more replicas in another Availability Zone.

**C.** Create an Amazon EC2 instance-based Docker cluster to handle the dynamic application load.

**D.** Create an Amazon Elastic Container Service (Amazon ECS) cluster with a Fargate launch type to handle the dynamic application load.

**E.** Create an Amazon Elastic Container Service (Amazon ECS) cluster with an Amazon EC2 launch type to handle the dynamic application load.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce app: load-balanced front-end, container app, relational DB. HA + min manual intervention.
- **Existing Resources:** None.
- **Current Issue/Goal:** HA, minimal ops.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `relational database` | **RDS Multi-AZ** |
| `container-based application` | **ECS Fargate** (serverless) |
| `as little manual intervention as possible` | Managed services |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability / Containers
- **Constraints:** Chọn 2, HA, min ops

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và D**

**Giải thích:**
- **A: RDS Multi-AZ** — HA cho relational database (tự động failover).
- **D: ECS Fargate** — serverless containers, không quản lý infrastructure, HA mặc định.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Read replicas — cho read scaling, không phải HA (failover không tự động).

**❌ Đáp án C:**
- EC2 Docker cluster — operational overhead cao.

**❌ Đáp án E:**
- ECS EC2 launch type — phải quản lý worker nodes, manual intervention hơn Fargate.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS Multi-AZ = DB HA. Fargate = serverless containers. EC2 launch = more overhead"*
