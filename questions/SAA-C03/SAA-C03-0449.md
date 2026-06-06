# Question #449 - Topic 1

A company runs its application on an Oracle database. The company plans to quickly migrate to AWS because of limited resources for the database, backup administration, and data center maintenance. The application uses third-party database features that require privileged access. Which solution will help the company migrate the database to AWS MOST cost-effectively?

## Options

**A.** Migrate the database to Amazon RDS for Oracle. Replace third-party features with cloud services.

**B.** Migrate the database to Amazon RDS Custom for Oracle. Customize the database settings to support third-party features.

**C.** Migrate the database to an Amazon EC2 Amazon Machine Image (AMI) for Oracle. Customize the database settings to support third-party features.

**D.** Migrate the database to Amazon RDS for PostgreSQL by rewriting the application code to remove dependency on Oracle APEX.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Oracle DB with third-party features requiring privileged access. Limited DB/backup/admin resources. Need quick, cost-effective migration.
- **Existing Resources:** Oracle database, third-party features.
- **Current Issue/Goal:** Migrate to AWS with minimal cost + effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `privileged access` | RDS Custom: cấp quyền SYS/SYSDBA, có thể cài thêm features. |
| `limited resources` | RDS Custom: managed nhưng vẫn customizable. |
| `third-party database features` | Standard RDS không cho phép cài thêm extensions. |
| `RDS Custom` | Managed DB với privileged access + customization. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration / Database
- **Constraints:** Oracle, privileged access, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- RDS Custom for Oracle: managed DB (automated backup, patching) + granted privileged access (SYS/SYSDBA).
- Cho phép cài third-party features, customize database settings.
- Cost-effective hơn EC2 (tự quản) mà vẫn linh hoạt hơn standard RDS.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Standard RDS for Oracle: không cấp privileged access → không support third-party features yêu cầu sysdba.

**❌ Đáp án C:**
- EC2 AMI for Oracle: tự quản hoàn toàn (OS, DB, backup) → operational overhead cao, limited resources.

**❌ Đáp án D:**
- Rewrite to PostgreSQL: tốn thời gian và chi phí phát triển lớn. Không "quickly migrate".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Oracle cần privileged access → RDS Custom. Standard RDS = no sysdba. EC2 = self-managed."*