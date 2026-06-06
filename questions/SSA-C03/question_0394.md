# Question #394 - Topic 1

A company is running a multi-tier ecommerce web application in the AWS Cloud. The application runs on Amazon EC2 instances with an Amazon RDS for MySQL Multi-AZ DB instance. Amazon RDS is configured with the latest generation DB instance with 2,000 GB of storage in a General Purpose SSD (gp3) Amazon Elastic Block Store (Amazon EBS) volume. The database performance affects the application during periods of high demand. A database administrator analyzes the logs in Amazon CloudWatch Logs and discovers that the application performance always degrades when the number of read and write IOPS is higher than 20,000. What should a solutions architect do to improve the application performance?

## Options

**A.** Replace the volume with a magnetic volume.

**B.** Increase the number of IOPS on the gp3 volume.

**C.** Replace the volume with a Provisioned IOPS SSD (io2) volume.

**D.** Replace the 2,000 GB gp3 volume with two 1,000 GB gp3 volumes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL Multi-AZ, gp3 2000 GB. Performance degrades when IOPS > 20,000. Need to improve performance.
- **Existing Resources:** RDS MySQL, gp3 2000 GB EBS.
- **Current Issue/Goal:** IOPS bottleneck > 20,000 IOPS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `IOPS is higher than 20,000` | gp3 max IOPS = 16,000 → không đủ. |
| `Provisioned IOPS SSD (io2)` | io2 Block Express hỗ trợ up to 256,000 IOPS. |
| `gp3 volume` | Max 16,000 IOPS (3,000 baseline + up to 13,000 additional provisioned). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Improve application performance
- **Constraints:** IOPS > 20,000 required

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- gp3 max IOPS = 16,000 → không thể đáp ứng IOPS > 20,000.
- io2 volume: có thể provision up to 256,000 IOPS → đủ để handle > 20,000 IOPS.
- io2 cũng có 99.999% durability.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Magnetic (standard) volume: IOPS thấp hơn nhiều → sẽ tệ hơn.

**❌ Đáp án B:**
- gp3 max IOPS = 16,000 → không thể tăng đủ để đạt > 20,000.

**❌ Đáp án D:**
- Two gp3 volumes: RDS chỉ dùng 1 volume mount ở 1 thời điểm. Multiple volumes không tăng IOPS cho single database.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"IOPS > 20,000 → io2 (max 256K). gp3 max = 16K IOPS. Magnetic = thấp hơn."*
