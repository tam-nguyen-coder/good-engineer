# Question #518 - Topic 1

An application uses an Amazon RDS MySQL DB instance. The RDS database is becoming low on disk space. A solutions architect wants to increase the disk space without downtime. Which solution meets these requirements with the LEAST amount of effort?

## Options

**A.** Enable storage autoscaling in RDS

**B.** Increase the RDS database instance size

**C.** Change the RDS database instance storage type to Provisioned IOPS

**D.** Back up the RDS database, increase the storage capacity, restore the database, and stop the previous instance

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL sắp hết disk space. Cần tăng storage không downtime, ít effort nhất.
- **Existing Resources:** RDS MySQL DB instance.
- **Current Issue/Goal:** Tăng disk space online, zero downtime.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `low on disk space` | Cần tăng storage capacity. |
| `without downtime` | Không reboot, không interruption. |
| `LEAST amount of effort` | Càng ít thao tác càng tốt. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least amount of effort, no downtime
- **Constraints:** RDS MySQL, increase storage without downtime

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- RDS storage autoscaling tự động tăng storage khi dung lượng gần đầy (threshold có thể cấu hình).
- Không cần downtime, không cần can thiệp thủ công.
- Chỉ cần enable feature 1 lần, RDS tự động quản lý sau đó → effort thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Tăng instance size (scale up compute) không giải quyết vấn đề disk space. Instance size liên quan đến CPU/RAM, không phải storage.
- Có thể gây downtime trong quá trình modify.

**❌ Đáp án C:**
- Change storage type to Provisioned IOPS: thay đổi loại storage (gp2 → io1/io2), không tăng dung lượng storage.
- Không giải quyết vấn đề hết disk space.

**❌ Đáp án D:**
- Backup → tăng storage → restore → stop old instance: gây downtime trong quá trình backup và restore.
- Effort cao: cần nhiều thao tác thủ công.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Low disk space → RDS storage autoscaling (zero effort, zero downtime). Instance size = CPU/RAM, không phải storage."*
