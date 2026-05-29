# Question #312 - Topic 1

A company has an application that runs on several Amazon EC2 instances. Each EC2 instance has multiple Amazon Elastic Block Store (Amazon EBS) data volumes attached to it. The application's EC2 instance configuration and data need to be backed up nightly. The application also needs to be recoverable in a different AWS Region. Which solution will meet these requirements in the MOST operationally efficient way?

## Options

**A.** Write an AWS Lambda function that schedules nightly snapshots of the application's EBS volumes and copies the snapshots to a different Region.

**B.** Create a backup plan by using AWS Backup to perform nightly backups. Copy the backups to another Region. Add the application's EC2 instances as resources.

**C.** Create a backup plan by using AWS Backup to perform nightly backups. Copy the backups to another Region. Add the application's EBS volumes as resources.

**D.** Write an AWS Lambda function that schedules nightly snapshots of the application's EBS volumes and copies the snapshots to a different Availability Zone.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances with multiple EBS volumes. Cần nightly backup và cross-Region recovery.
- **Existing Resources:** EC2 instances, EBS volumes.
- **Current Issue/Goal:** Backup nightly, cross-Region DR, most operationally efficient.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `backed up nightly` | Cần scheduled backup hàng đêm. |
| `recoverable in a different AWS Region` | Cần copy backup cross-Region. |
| `MOST operationally efficient` | AWS Backup là managed service, không cần tự viết Lambda. |
| `AWS Backup` | Managed backup service, support EBS, schedule, cross-Region copy. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operationally efficient
- **Constraints:** Nightly backup, cross-Region recovery, EC2 + EBS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS Backup: tạo backup plan tự động nightly cho EBS volumes, copy sang Region khác.
- AWS Backup là managed service → không cần tự code Lambda, operational efficiency cao nhất.
- Add EBS volumes as resources (chứ không phải EC2 instances) vì AWS Backup backup EBS snapshots.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda snapshot script tự viết → operational overhead cao hơn dùng AWS Backup.

**❌ Đáp án B:**
- AWS Backup hỗ trợ EC2 instances, nhưng khi add EC2 instances, nó backup toàn bộ instance (bao gồm root volume). Tuy nhiên, đối với cross-Region copy, AWS Backup hoạt động ở cấp EBS snapshots → thêm EBS volumes làm resources là chính xác hơn cho data volumes.

**❌ Đáp án D:**
- Copy snapshot to different AZ (trong cùng Region) → không đáp ứng cross-Region recovery.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Nightly backup + cross-Region → AWS Backup (managed). Lambda tự viết = operational overhead cao hơn."*
