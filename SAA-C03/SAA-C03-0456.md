# Question #456 - Topic 1

A company runs applications on Amazon EC2 instances in one AWS Region. The company wants to back up the EC2 instances to a second Region. The company also wants to provision EC2 resources in the second Region and manage the EC2 instances centrally from one AWS account. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Create a disaster recovery (DR) plan that has a similar number of EC2 instances in the second Region. Configure data replication.

**B.** Create point-in-time Amazon Elastic Block Store (Amazon EBS) snapshots of the EC2 instances. Copy the snapshots to the second Region periodically.

**C.** Create a backup plan by using AWS Backup. Configure cross-Region backup to the second Region for the EC2 instances.

**D.** Deploy a similar number of EC2 instances in the second Region. Use AWS DataSync to transfer the data from the source Region to the second Region.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 in one Region. Need cross-Region backup + centrally manage.
- **Existing Resources:** EC2 instances in source Region.
- **Current Issue/Goal:** Cross-Region backup, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `back up EC2 instances to a second Region` | Cross-Region backup. |
| `centrally from one account` | AWS Backup: centralized management. |
| `most cost-effectively` | Only store backups (not running instances) in DR Region. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Backup / Disaster Recovery
- **Constraints:** Cross-Region, central management, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS Backup: centralized backup service, hỗ trợ cross-Region backup.
- Configure backup plan → EC2 backups automatically copied to second Region.
- Cost-effective: chỉ trả cho backup storage, không cần running instances.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DR plan with similar instances: duy trì EC2 instances ở DR Region → tốn kém.

**❌ Đáp án B:**
- Manual EBS snapshots + copy: không centralized management, cần custom scripts.

**❌ Đáp án D:**
- Deploy instances in second Region + DataSync: tốn kém (EC2 running cost).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cross-Region backup → AWS Backup (centralized, managed). Không cần EC2 running in DR."*