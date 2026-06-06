# Question #138 - Topic 1

A company runs its ecommerce application on AWS. Every new order is published as a massage in a RabbitMQ queue that runs on an Amazon EC2 instance in a single Availability Zone. These messages are processed by a different application that runs on a separate EC2 instance. This application stores the details in a PostgreSQL database on another EC2 instance. All the EC2 instances are in the same Availability Zone. The company needs to redesign its architecture to provide the highest availability with the least operational overhead. What should a solutions architect do to meet these requirements?

## Options

**A.** Migrate the queue to a redundant pair (active/standby) of RabbitMQ instances on Amazon MQ. Create a Multi-AZ Auto Scaling group for EC2 instances that host the application. Create another Multi-AZ Auto Scaling group for EC2 instances that host the PostgreSQL database.

**B.** Migrate the queue to a redundant pair (active/standby) of RabbitMQ instances on Amazon MQ. Create a Multi-AZ Auto Scaling group for EC2 instances that host the application. Migrate the database to run on a Multi-AZ deployment of Amazon RDS for PostgreSQL.

**C.** Create a Multi-AZ Auto Scaling group for EC2 instances that host the RabbitMQ queue. Create another Multi-AZ Auto Scaling group for EC2 instances that host the application. Migrate the database to run on a Multi-AZ deployment of Amazon RDS for PostgreSQL.

**D.** Create a Multi-AZ Auto Scaling group for EC2 instances that host the RabbitMQ queue. Create another Multi-AZ Auto Scaling group for EC2 instances that host the application. Create a third Multi-AZ Auto Scaling group for EC2 instances that host the PostgreSQL database

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RabbitMQ (EC2) → Application (EC2) → PostgreSQL (EC2). Tất cả single AZ.
- **Existing Resources:** 3 EC2 instances trong 1 AZ.
- **Current Issue/Goal:** Highest availability, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highest availability` | Managed services + Multi-AZ |
| `least operational overhead` | Dùng **Amazon MQ** + **RDS** thay vì self-managed |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability
- **Constraints:** Least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Amazon MQ** (managed RabbitMQ) — active/standby across AZs, tự động failover.
- **ASG Multi-AZ** cho application — tự động scale, HA.
- **RDS PostgreSQL Multi-AZ** — managed DB, tự động failover.
- Cả 3 layers đều managed → least operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- PostgreSQL trên EC2 ASG — không managed, operational overhead cao.

**❌ Đáp án C:**
- RabbitMQ trên EC2 ASG — tự quản lý queue, không bằng Amazon MQ.

**❌ Đáp án D:**
- Tất cả self-managed trên EC2 — operational overhead cao nhất.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Amazon MQ + RDS = managed HA. Self-managed EC2 = more overhead. B là best cho cả 3 layers"*
