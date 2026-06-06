# Question #508 - Topic 1

A company has migrated multiple Microsoft Windows Server workloads to Amazon EC2 instances that run in the us-west-1 Region. The company manually backs up the workloads to create an image as needed. In the event of a natural disaster in the us-west-1 Region, the company wants to recover workloads quickly in the us-west-2 Region. The company wants no more than 24 hours of data loss on the EC2 instances. The company also wants to automate any backups of the EC2 instances. Which solutions will meet these requirements with the LEAST administrative effort? (Choose two.)

## Options

**A.** Create an Amazon EC2-backed Amazon Machine Image (AMI) lifecycle policy to create a backup based on tags. Schedule the backup to run twice daily. Copy the image on demand.

**B.** Create an Amazon EC2-backed Amazon Machine Image (AMI) lifecycle policy to create a backup based on tags. Schedule the backup to run twice daily. Configure the copy to the us-west-2 Region.

**C.** Create backup vaults in us-west-1 and in us-west-2 by using AWS Backup. Create a backup plan for the EC2 instances based on tag values. Create an AWS Lambda function to run as a scheduled job to copy the backup data to us-west-2.

**D.** Create a backup vault by using AWS Backup. Use AWS Backup to create a backup plan for the EC2 instances based on tag values. Define the destination for the copy as us-west-2. Specify the backup schedule to run twice daily.

**E.** Create a backup vault by using AWS Backup. Use AWS Backup to create a backup plan for the EC2 instances based on tag values. Specify the backup schedule to run twice daily. Copy on demand to us-west-2.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Windows workloads on EC2 ở us-west-1. Cần DR sang us-west-2. RPO ≤ 24h, automate backup. Least administrative effort.
- **Existing Resources:** EC2 instances in us-west-1.
- **Current Issue/Goal:** Tự động backup + cross-region copy để phục hồi khi disaster.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `no more than 24 hours of data loss` | RPO ≤ 24h → backup ít nhất 2 lần/ngày. |
| `automate backups` | Không manual. |
| `quickly recover in us-west-2` | Cần copy backup sang region khác. |
| `LEAST administrative effort` | Càng ít custom code càng tốt. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least administrative effort (choose 2)
- **Constraints:** RPO ≤ 24h, automated, cross-region DR

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và D**

**Giải thích:**
- **B - AMI Lifecycle Policy:** EC2 Image Builder (AMI lifecycle) cho phép tạo AMI schedule, tự động copy sang region khác. Dùng tags để xác định instances cần backup. Automated, không cần custom code.
- **D - AWS Backup:** AWS Backup là centralized backup service. Tạo backup plan, gắn tags, schedule twice daily, define copy destination là us-west-2. AWS Backup tự động quản lý retention và cross-region copy.
- Cả B và D đều đáp ứng: automated, twice daily (RPO 12h < 24h), cross-region copy, minimal effort.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- "Copy the image on demand" → manual copy, không automated → không đáp ứng yêu cầu tự động backup.

**❌ Đáp án C:**
- Dùng AWS Backup nhưng thêm Lambda function để copy → unnecessary complexity, administrative effort cao hơn.

**❌ Đáp án E:**
- "Copy on demand to us-west-2" → manual copy → không automated.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Automated cross-region DR → AMI Lifecycle Policy hoặc AWS Backup (scheduled + auto copy region). Copy on demand = manual = sai."*
