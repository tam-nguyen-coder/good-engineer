# Question #579 - Topic 1

A company runs an application that uses Amazon RDS for PostgreSQL. The application receives traffic only on weekdays during business hours. The company wants to optimize costs and reduce operational overhead based on this usage. Which solution will meet these requirements?

## Options

**A.** Use the Instance Scheduler on AWS to configure start and stop schedules.

**B.** Turn off automatic backups. Create weekly manual snapshots of the database.

**C.** Create a custom AWS Lambda function to start and stop the database based on minimum CPU utilization.

**D.** Purchase All Upfront reserved DB instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS PostgreSQL, chỉ hoạt động giờ hành chính ngày thường.
- **Existing Resources:** RDS PostgreSQL instance.
- **Current Issue/Goal:** Optimize cost + reduce ops overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `weekdays during business hours` | Có thể stop DB ngoài giờ để tiết kiệm cost. |
| `Instance Scheduler on AWS` | AWS solution: schedule start/stop cho RDS instances. |
| `reduce operational overhead` | Instance Scheduler là managed solution, không cần custom code. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Optimize costs + reduce operational overhead
- **Constraints:** RDS PostgreSQL, weekday business hours only

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Instance Scheduler on AWS (AWS Solution) cho phép schedule start/stop RDS instances.
- Stop DB ngoài giờ → không tốn compute cost (chỉ lưu storage và backups).
- Operational overhead thấp: chỉ cần cấu hình schedule, không cần custom code.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Tắt auto backups + manual snapshots: tiết kiệm backup cost nhưng instance vẫn chạy 24/7 → compute cost vẫn cao.

**❌ Đáp án C:**
- Custom Lambda dựa trên CPU utilization: phức tạp, operational overhead cao, không cần thiết khi biết trước schedule.

**❌ Đáp án D:**
- All Upfront reserved instances: cam kết trả trước toàn bộ, dù chỉ dùng 40% thời gian (weekdays business hours) → lãng phí.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Business hours only → Instance Scheduler (start/stop on schedule). RI = waste for partial usage."*
