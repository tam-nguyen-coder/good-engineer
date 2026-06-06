# Question #539 - Topic 1

A company wants to use the AWS Cloud to improve its on-premises disaster recovery (DR) configuration. The company's core production business application uses Microsoft SQL Server Standard, which runs on a virtual machine (VM). The application has a recovery point objective (RPO) of 30 seconds or fewer and a recovery time objective (RTO) of 60 minutes. The DR solution needs to minimize costs wherever possible. Which solution will meet these requirements?

## Options

**A.** Configure a multi-site active/active setup between the on-premises server and AWS by using Microsoft SQL Server Enterprise with Always On availability groups.

**B.** Configure a warm standby Amazon RDS for SQL Server database on AWS. Configure AWS Database Migration Service (AWS DMS) to use change data capture (CDC).

**C.** Use AWS Elastic Disaster Recovery configured to replicate disk changes to AWS as a pilot light.

**D.** Use third-party backup software to capture backups every night. Store a secondary set of backups in Amazon S3.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-premises SQL Server Standard cần DR solution với RPO ≤30s, RTO 60 phút. Chi phí tối thiểu.
- **Existing Resources:** On-premises VM chạy SQL Server Standard.
- **Current Issue/Goal:** DR solution với RPO rất thấp (30s), RTO 60 phút, minimize cost.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `RPO 30 seconds` | Cần replication gần như real-time |
| `RTO 60 minutes` | Cần recovery trong 1 giờ |
| `SQL Server Standard` | Standard edition có giới hạn tính năng so với Enterprise |
| `minimize costs` | Dùng RDS for SQL Server + DMS CDC rẻ hơn SQL Server Enterprise |
| `DMS CDC` | Change Data Capture → real-time replication |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Disaster Recovery / Cost optimization
- **Constraints:** RPO ≤30s, RTO ≤60 phút, SQL Server Standard, minimize cost

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- RDS for SQL Server là managed service, giảm operational overhead.
- DMS with CDC cung cấp real-time replication từ on-premises SQL Server đến RDS → RPO ≤30s achievable.
- Warm standby: RDS instance sẵn sàng, khi DR xảy ra chỉ cần chuyển hướng application → RTO 60 phút khả thi.
- SQL Server Standard không hỗ trợ Always On Availability Groups (cần Enterprise), nhưng DMS CDC là giải pháp thay thế cost-effective.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- SQL Server Standard không hỗ trợ Always On Availability Groups (cần Enterprise).
- Active/active với Enterprise → chi phí rất cao.

**❌ Đáp án C:**
- AWS Elastic Disaster Recovery (CloudEndure) replicate disk ở block level, không phải database-aware.
- RPO ≤30s khó đảm bảo với disk-level replication.
- Pilot light: cần start EC2 instances khi DR → RTO có thể >60 phút.

**❌ Đáp án D:**
- Nightly backup → RPO 24 giờ, không thể đáp ứng 30 giây.
- Restore từ backup trong S3 → RTO có thể rất lâu.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"SQL Server Standard + RPO 30s → DMS CDC to RDS. Always On = Enterprise only."*
