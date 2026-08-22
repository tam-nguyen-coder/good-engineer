# Question #666 - Topic 1

A startup company is hosting a website for its customers on an Amazon EC2 instance. The website consists of a stateless Python application and a MySQL database. The website serves only a small amount of traffic. The company is concerned about the reliability of the instance and needs to migrate to a highly available architecture. The company cannot modify the application code. Which combination of actions should a solutions architect take to achieve high availability for the website? (Choose two.)

## Options

**A.** Provision an internet gateway in each Availability Zone in use.

**B.** Migrate the database to an Amazon RDS for MySQL Multi-AZ DB instance.

**C.** Migrate the database to Amazon DynamoDB, and enable DynamoDB auto scaling.

**D.** Use AWS DataSync to synchronize the database data across multiple EC2 instances.

**E.** Create an Application Load Balancer to distribute traffic to an Auto Scaling group of EC2 instances that are distributed across two Availability Zones.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Single EC2 instance hosting stateless Python app + MySQL DB. Small traffic. Need HA, cannot modify code.
- **Existing Resources:** Single EC2 instance.
- **Current Issue/Goal:** Highly available architecture.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `stateless Python application` | Can scale horizontally with ALB + ASG. |
| `MySQL database` | Cần HA cho DB → RDS Multi-AZ. |
| `cannot modify the application code` | Phải giữ nguyên MySQL (không thể chuyển DynamoDB). |
| `Multi-AZ` | Automated failover cho DB. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (choose two)
- **Constraints:** Cannot modify code, HA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và E**

**Giải thích:**
- **B:** RDS MySQL Multi-AZ → tự động failover nếu primary DB fail → HA cho database.
- **E:** ALB + ASG across 2 AZs → HA cho application tier. Nếu 1 AZ fail, traffic vẫn đến AZ còn lại.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Internet Gateway là resource của VPC, mỗi VPC chỉ cần 1 IGW. Không cần provision trong mỗi AZ.

**❌ Đáp án C:**
- DynamoDB yêu cầu thay đổi code (application đang dùng MySQL) → violate "cannot modify code".

**❌ Đáp án D:**
- DataSync không phải giải pháp HA cho database. Không hỗ trợ real-time replication cho MySQL.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"HA for stateless app + MySQL: ALB + ASG across AZs + RDS Multi-AZ."*
