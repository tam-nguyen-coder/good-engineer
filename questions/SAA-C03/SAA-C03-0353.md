# Question #353 - Topic 1

A company hosts a three-tier web application on Amazon EC2 instances in a single Availability Zone. The web application uses a self-managed MySQL database that is hosted on an EC2 instance to store data in an Amazon Elastic Block Store (Amazon EBS) volume. The MySQL database currently uses a 1 TB Provisioned IOPS SSD (io2) EBS volume. The company expects traffic of 1,000 IOPS for both reads and writes at peak traffic. The company wants to minimize any disruptions, stabilize performance, and reduce costs while retaining the capacity for double the IOPS. The company wants to move the database tier to a fully managed solution that is highly available and fault tolerant. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Use a Multi-AZ deployment of an Amazon RDS for MySQL DB instance with an io2 Block Express EBS volume.

**B.** Use a Multi-AZ deployment of an Amazon RDS for MySQL DB instance with a General Purpose SSD (gp2) EBS volume.

**C.** Use Amazon S3 Intelligent-Tiering access tiers.

**D.** Use two large EC2 instances to host the database in active-passive mode.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Self-managed MySQL on EC2 + io2 1 TB EBS. Need fully managed, HA, fault tolerant. Peak 1,000 IOPS. Cost-effective.
- **Existing Resources:** EC2 MySQL, 1 TB io2 EBS.
- **Current Issue/Goal:** Migrate to fully managed RDS, HA, reduce cost.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `fully managed solution` | RDS (not self-managed EC2). |
| `highly available and fault tolerant` | Multi-AZ deployment. |
| `1,000 IOPS` | gp2 1 TB: baseline 3,000 IOPS → đủ cho 1,000 peak (và double 2,000). |
| `most cost-effectively` | gp2 rẻ hơn io2 nhiều cho workload dưới 3,000 IOPS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Fully managed, HA/fault tolerant, 1,000 IOPS peak (double capacity needed)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- RDS Multi-AZ MySQL: fully managed + HA + automatic failover.
- gp2 EBS 1 TB: baseline 3,000 IOPS (3 IOPS/GB) → đủ cho 1,000 IOPS peak và 2,000 IOPS double capacity.
- gp2 rẻ hơn io2 rất nhiều → cost-effective.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- io2 Block Express quá đắt cho 1,000 IOPS (io2 phù hợp cho IOPS-intensive workloads > 16,000 IOPS).

**❌ Đáp án C:**
- S3 Intelligent-Tiering là storage class, không phải database solution.

**❌ Đáp án D:**
- Two EC2 active-passive: không fully managed (phải tự quản lý replication, failover).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"1,000 IOPS → gp2 đủ (3,000 baseline). io2 quá đắt. RDS Multi-AZ = HA + managed."*
