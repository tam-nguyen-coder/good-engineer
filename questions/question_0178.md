# Question #178 - Topic 1

A company's infrastructure consists of Amazon EC2 instances and an Amazon RDS DB instance in a single AWS Region. The company wants to back up its data in a separate Region. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS Backup to copy EC2 backups and RDS backups to the separate Region.

**B.** Use Amazon Data Lifecycle Manager (Amazon DLM) to copy EC2 backups and RDS backups to the separate Region.

**C.** Create Amazon Machine Images (AMIs) of the EC2 instances. Copy the AMIs to the separate Region. Create a read replica for the RDS DB instance in the separate Region.

**D.** Create Amazon Elastic Block Store (Amazon EBS) snapshots. Copy the EBS snapshots to the separate Region. Create RDS snapshots. Export the RDS snapshots to Amazon S3. Configure S3 Cross-Region Replication (CRR) to the separate Region.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 + RDS in one Region. Need cross-Region backup.
- **Existing Resources:** EC2 instances, RDS DB instance.
- **Current Issue/Goal:** Least operational overhead for cross-Region backup.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `back up... in a separate Region` | **AWS Backup** — managed backup, hỗ trợ cross-Region copy |
| `least operational overhead` | AWS Backup tự động hoá |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Backup / DR
- **Constraints:** Cross-Region, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **AWS Backup** — centralised backup service, hỗ trợ cả EC2 (AMI) và RDS.
- Configure backup plan → tự động copy snapshots sang Region khác.
- Single point of management → least overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- DLM — chỉ cho EBS snapshots, không hỗ trợ RDS.

**❌ Đáp án C:**
- AMI copy + read replica — manual steps, more overhead.

**❌ Đáp án D:**
- EBS snapshots + RDS export + S3 CRR — quá nhiều bước, overhead cao.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AWS Backup = centralised cross-Region backup (EC2 + RDS). DLM = EBS only. Manual = overhead"*
