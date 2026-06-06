# Question #129 - Topic 1

A company is running a multi-tier web application on premises. The web application is containerized and runs on a number of Linux hosts connected to a PostgreSQL database that contains user records. The operational overhead of maintaining the infrastructure and capacity planning is limiting the company's growth. A solutions architect must improve the application's infrastructure. Which combination of actions should the solutions architect take to accomplish this? (Choose two.)

## Options

**A.** Migrate the PostgreSQL database to Amazon Aurora.

**B.** Migrate the web application to be hosted on Amazon EC2 instances.

**C.** Set up an Amazon CloudFront distribution for the web application content.

**D.** Set up Amazon ElastiCache between the web application and the PostgreSQL database.

**E.** Migrate the web application to be hosted on AWS Fargate with Amazon Elastic Container Service (Amazon ECS).

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Containerized web app + PostgreSQL on-prem. Operational overhead + capacity planning limiting growth.
- **Existing Resources:** Containerized web app, PostgreSQL.
- **Current Issue/Goal:** Reduce operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `operational overhead of maintaining the infrastructure` | Cần managed services |
| `containerized` | **Fargate** — serverless containers |
| `PostgreSQL database` | **Aurora** — managed, scalable |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration + Operational efficiency
- **Constraints:** Chọn 2, reduce overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và E**

**Giải thích:**
- **A: Aurora** — managed PostgreSQL-compatible database, tự động scale, patch, backup.
- **E: Fargate + ECS** — serverless containers, không quản lý infrastructure, tự động scale.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- EC2 instances — vẫn phải quản lý infrastructure, không giảm overhead.

**❌ Đáp án C:**
- CloudFront — cải thiện performance nhưng không giảm operational overhead.

**❌ Đáp án D:**
- ElastiCache — thêm một service phải quản lý, tăng overhead.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Aurora = managed DB. Fargate = serverless containers. Both reduce operational overhead"*
