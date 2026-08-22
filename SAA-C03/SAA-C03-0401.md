# Question #401 - Topic 1

A company wants to use the AWS Cloud to make an existing application highly available and resilient. The current version of the application resides in the company's data center. The application recently experienced data loss after a database server crashed because of an unexpected power outage. The company needs a solution that avoids any single points of failure. The solution must give the application the ability to scale to meet user demand. Which solution will meet these requirements?

## Options

**A.** Deploy the application servers by using Amazon EC2 instances in an Auto Scaling group across multiple Availability Zones. Use an Amazon RDS DB instance in a Multi-AZ configuration.

**B.** Deploy the application servers by using Amazon EC2 instances in an Auto Scaling group in a single Availability Zone. Deploy the database on an EC2 instance. Enable EC2 Auto Recovery.

**C.** Deploy the application servers by using Amazon EC2 instances in an Auto Scaling group across multiple Availability Zones. Use an Amazon RDS DB instance with a read replica in a single Availability Zone. Promote the read replica to replace the primary DB instance if the primary DB instance fails.

**D.** Deploy the application servers by using Amazon EC2 instances in an Auto Scaling group across multiple Availability Zones. Deploy the primary and secondary database servers on EC2 instances across multiple Availability Zones. Use Amazon Elastic Block Store (Amazon EBS) Multi-Attach to create shared storage between the instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate on-prem app to AWS. Need HA, resilient, no SPOF, scale to meet demand.
- **Existing Resources:** On-prem application, database server.
- **Current Issue/Goal:** Data loss from DB crash (power outage). Need HA + scalability.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `no single points of failure` | Multi-AZ for both compute and database. |
| `highly available and resilient` | ASG across AZs + RDS Multi-AZ. |
| `scale to meet demand` | ASG (compute scaling). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Highly available, fault-tolerant, scalable
- **Constraints:** No SPOF, scale on demand

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- ASG across multiple AZs: compute HA + scaling.
- RDS Multi-AZ: synchronous standby replica in different AZ → automatic failover, no data loss, no SPOF.
- Kết hợp cả compute + database HA.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Single AZ → SPOF. EC2 Auto Recovery chỉ restart instance, không HA thực sự.
- Database trên EC2 tự quản → không managed HA.

**❌ Đáp án C:**
- Read replica in single AZ: không tự động failover, cần promote thủ công → downtime.
- Read replica không hỗ trợ HA như Multi-AZ.

**❌ Đáp án D:**
- EBS Multi-Attach không hỗ trợ shared storage cho database (chỉ io1/io2, tối đa 16 instances, không dùng cho database cluster).
- Tự quản DB trên EC2 → operational overhead cao, không resilient.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ASG multi-AZ + RDS Multi-AZ = compute HA + database HA. Read replica ≠ HA."*

