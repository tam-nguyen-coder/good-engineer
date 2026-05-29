# Question #679 - Topic 1

A company wants to back up its on-premises virtual machines (VMs) to AWS. The company's backup solution exports on-premises backups to an Amazon S3 bucket as objects. The S3 backups must be retained for 30 days and must be automatically deleted after 30 days. Which combination of steps will meet these requirements? (Choose three.)

## Options

**A.** Create an S3 bucket that has S3 Object Lock enabled.

**B.** Create an S3 bucket that has object versioning enabled.

**C.** Configure a default retention period of 30 days for the objects.

**D.** Configure an S3 Lifecycle policy to protect the objects for 30 days.

**E.** Configure an S3 Lifecycle policy to expire the objects after 30 days. F. Configure the backup solution to tag the objects with a 30-day retention period

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-prem VM backups to S3. Retain for exactly 30 days, auto-delete after 30 days.
- **Existing Resources:** Backup solution exporting to S3.
- **Current Issue/Goal:** Retain 30 days, then auto-delete.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `retained for 30 days` | Cannot be deleted before 30 days → Object Lock with retention. |
| `automatically deleted after 30 days` | Lifecycle policy expiration. |
| `Object Lock` | Write Once Read Many (WORM) protection for specified period. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (choose three)
- **Constraints:** Retain 30 days (prevent deletion), delete after 30 days

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, C và E**

**Giải thích:**
- **A:** S3 Object Lock enabled → prerequisite cho retention periods.
- **C:** Default retention period 30 days → objects được bảo vệ không thể xóa trong 30 ngày.
- **E:** S3 Lifecycle policy expiration after 30 days → tự động xóa objects sau 30 ngày.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Object versioning hỗ trợ Object Lock nhưng không cần thiết phải enable riêng nếu đã dùng Object Lock.

**❌ Đáp án D:**
- Lifecycle policy không có "protect" action. Lifecycle dùng để transition, expire, không phải để protect.

**❌ Đáp án F:**
- Tag với 30-day retention period → cần kết hợp với Object Lock retention, không tự động enforce.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Retain 30 days + auto-delete = Object Lock retention + Lifecycle expiration."*
