# Question #111 - Topic 1

A company recently migrated a message processing system to AWS. The system receives messages into an ActiveMQ queue running on an Amazon EC2 instance. Messages are processed by a consumer application running on Amazon EC2. The consumer application processes the messages and writes results to a MySQL database running on Amazon EC2. The company wants this application to be highly available with low operational complexity. Which architecture offers the HIGHEST availability?

## Options

**A.** Add a second ActiveMQ server to another Availability Zone. Add an additional consumer EC2 instance in another Availability Zone. Replicate the MySQL database to another Availability Zone.

**B.** Use Amazon MQ with active/standby brokers configured across two Availability Zones. Add an additional consumer EC2 instance in another Availability Zone. Replicate the MySQL database to another Availability Zone.

**C.** Use Amazon MQ with active/standby brokers configured across two Availability Zones. Add an additional consumer EC2 instance in another Availability Zone. Use Amazon RDS for MySQL with Multi-AZ enabled.

**D.** Use Amazon MQ with active/standby brokers configured across two Availability Zones. Add an Auto Scaling group for the consumer EC2 instances across two Availability Zones. Use Amazon RDS for MySQL with Multi-AZ enabled.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ActiveMQ → consumer → MySQL. Tất cả đang chạy trên EC2.
- **Existing Resources:** EC2 cho ActiveMQ, consumer, MySQL.
- **Current Issue/Goal:** Highest availability, low operational complexity.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highest availability` | Managed services + Multi-AZ |
| `low operational complexity` | Dùng managed services |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability
- **Constraints:** Highest possible HA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Amazon MQ** (managed ActiveMQ) — active/standby across 2 AZs → HA cho message broker.
- **ASG cho consumer** — tự động thay thế instances khi fail, scale, multi-AZ.
- **RDS MySQL Multi-AZ** — tự động failover, managed.
- Tất cả layers đều managed + Multi-AZ → **highest availability**.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Tất cả self-managed trên EC2 — operational complexity, không tự động recovery.

**❌ Đáp án B:**
- Amazon MQ managed → tốt. Nhưng MySQL self-managed + 1 consumer instance → không HA cao nhất.

**❌ Đáp án C:**
- RDS Multi-AZ → tốt. Nhưng 1 consumer instance → single point of failure.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Amazon MQ + RDS Multi-AZ + ASG = HA cho tất cả layers. Self-managed EC2 = lower availability"*
