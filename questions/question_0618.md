# Question #618 - Topic 1

A company wants to use Amazon FSx for Windows File Server for its Amazon EC2 instances that have an SMB file share mounted as a volume in the us-east-1 Region. The company has a recovery point objective (RPO) of 5 minutes for planned system maintenance or unplanned service disruptions. The company needs to replicate the file system to the us-west-2 Region. The replicated data must not be deleted by any user for 5 years. Which solution will meet these requirements?

## Options

**A.** Create an FSx for Windows File Server file system in us-east-1 that has a Single-AZ 2 deployment type. Use AWS Backup to create a daily backup plan that includes a backup rule that copies the backup to us-west-2. Configure AWS Backup Vault Lock in compliance mode for a target vault in us-west-2. Configure a minimum duration of 5 years.

**B.** Create an FSx for Windows File Server file system in us-east-1 that has a Multi-AZ deployment type. Use AWS Backup to create a daily backup plan that includes a backup rule that copies the backup to us-west-2. Configure AWS Backup Vault Lock in governance mode for a target vault in us-west-2. Configure a minimum duration of 5 years.

**C.** Create an FSx for Windows File Server file system in us-east-1 that has a Multi-AZ deployment type. Use AWS Backup to create a daily backup plan that includes a backup rule that copies the backup to us-west-2. Configure AWS Backup Vault Lock in compliance mode for a target vault in us-west-2. Configure a minimum duration of 5 years.

**D.** Create an FSx for Windows File Server file system in us-east-1 that has a Single-AZ 2 deployment type. Use AWS Backup to create a daily backup plan that includes a backup rule that copies the backup to us-west-2. Configure AWS Backup Vault Lock in governance mode for a target vault in us-west-2. Configure a minimum duration of 5 years.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** FSx for Windows File Server in us-east-1, SMB mount từ EC2. RPO 5 minutes, cần cross-region replication. Data must not be deleted by any user for 5 years.
- **Existing Resources:** FSx for Windows File Server, EC2 instances.
- **Current Issue/Goal:** Cross-region DR + immutable backup for 5 years.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `FSx for Windows File Server` | Managed Windows file server, SMB protocol. |
| `RPO of 5 minutes` | Multi-AZ có automatic failover, giảm RPO. |
| `cross-region replication` | AWS Backup copy backup sang region khác. |
| `must not be deleted by any user for 5 years` | AWS Backup Vault Lock – Compliance mode (không thể bị override kể cả root). |
| `Compliance mode` | Không ai có thể xóa/sửa backup policy trong thời gian lock. Governance mode có thể bị override bởi root. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** RPO 5 min, cross-region DR, immutable 5 years

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Multi-AZ: cung cấp high availability cho planned/unplanned maintenance, giúp đạt RPO 5 phút.
- AWS Backup: daily backup + cross-region copy to us-west-2.
- Backup Vault Lock Compliance mode: đảm bảo không ai (kể cả root user) có thể xóa backups trong 5 năm.
- Compliance mode khác Governance mode: Governance có thể bị override bởi root user.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Single-AZ 2: không có automatic failover, downtime khi maintenance → khó đạt RPO 5 phút.

**❌ Đáp án B:**
- Governance mode: có thể bị override bởi root user → không đảm bảo "must not be deleted by any user".

**❌ Đáp án D:**
- Single-AZ 2 + Governance mode: cả hai đều không đáp ứng yêu cầu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-AZ = HA (RPO 5 min). Compliance Lock = immutable (no one can delete). Governance = root có thể override."*
