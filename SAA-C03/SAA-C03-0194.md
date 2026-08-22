# Question #194 - Topic 1

A company needs to run a critical application on AWS. The company needs to use Amazon EC2 for the application's database. The database must be highly available and must fail over automatically if a disruptive event occurs. Which solution will meet these requirements?

## Options

**A.** Launch two EC2 instances, each in a different Availability Zone in the same AWS Region. Install the database on both EC2 instances. Configure the EC2 instances as a cluster. Set up database replication.

**B.** Launch an EC2 instance in an Availability Zone. Install the database on the EC2 instance. Use an Amazon Machine Image (AMI) to back up the data. Use AWS CloudFormation to automate provisioning of the EC2 instance if a disruptive event occurs.

**C.** Launch two EC2 instances, each in a different AWS Region. Install the database on both EC2 instances. Set up database replication. Fail over the database to a second Region.

**D.** Launch an EC2 instance in an Availability Zone. Install the database on the EC2 instance. Use an Amazon Machine Image (AMI) to back up the data. Use EC2 automatic recovery to recover the instance if a disruptive event occurs.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Critical app using EC2 as database (self-managed). HA + automatic failover.
- **Existing Resources:** None.
- **Current Issue/Goal:** HA with auto failover for self-managed DB on EC2.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highly available` | Multi-AZ |
| `fail over automatically` | Cluster + replication |
| `use Amazon EC2 for the application's database` | Self-managed DB |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability / Database
- **Constraints:** EC2-based DB, HA, auto failover

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Two EC2 instances in different AZs** — nếu 1 AZ fails, instance kia vẫn chạy.
- Database cluster + replication — tự động failover.
- Single Region → HA trong Region.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Single EC2 + AMI + CloudFormation — không failover tự động, cần manual recovery.

**❌ Đáp án C:**
- Cross-Region — overkill, độ trễ cross-Region cao, phức tạp.

**❌ Đáp án D:**
- Single EC2 + EC2 automatic recovery — recovery trong cùng AZ, không chống được AZ failure.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-AZ EC2 cluster = HA for self-managed DB. Single AZ = not HA. Cross-Region = overkill"*
