# Question #69 - Topic 1

A company is running a business-critical web application on Amazon EC2 instances behind an Application Load Balancer. The EC2 instances are in an Auto Scaling group. The application uses an Amazon Aurora PostgreSQL database that is deployed in a single Availability Zone. The company wants the application to be highly available with minimum downtime and minimum loss of data. Which solution will meet these requirements with the LEAST operational effort?

## Options

**A.** Place the EC2 instances in different AWS Regions. Use Amazon Route 53 health checks to redirect traffic. Use Aurora PostgreSQL Cross- Region Replication.

**B.** Configure the Auto Scaling group to use multiple Availability Zones. Configure the database as Multi-AZ. Configure an Amazon RDS Proxy instance for the database.

**C.** Configure the Auto Scaling group to use one Availability Zone. Generate hourly snapshots of the database. Recover the database from the snapshots in the event of a failure.

**D.** Configure the Auto Scaling group to use multiple AWS Regions. Write the data from the application to Amazon S3. Use S3 Event Notifications to launch an AWS Lambda function to write the data to the database.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Business-critical web app: ALB + ASG + Aurora PostgreSQL single-AZ.
- **Existing Resources:** ALB, ASG, Aurora PostgreSQL single-AZ.
- **Current Issue/Goal:** HA, minimum downtime/data loss, least operational effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `business-critical` | HA là bắt buộc |
| `single Availability Zone` | Hiện tại chỉ 1 AZ — cần Multi-AZ |
| `minimum downtime and minimum loss of data` | Multi-AZ cho compute và database |
| `least operational effort` | Giải pháp đơn giản nhất |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability
- **Constraints:** Min downtime, min data loss, least effort

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **ASG multiple AZs** — nếu 1 AZ fails, EC2 instances ở AZ khác vẫn chạy.
- **Aurora Multi-AZ** — tự động failover sang standby instance ở AZ khác, min downtime.
- **RDS Proxy** — quản lý connection pooling, giảm connection stress khi failover.
- Đây là giải pháp đơn giản nhất trong cùng Region.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Cross-Region là overkill — tăng latency, phức tạp, không cần thiết cho HA.

**❌ Đáp án C:**
- Single AZ — không HA. Snapshot recovery mất nhiều thời gian > RTO yêu cầu.

**❌ Đáp án D:**
- S3 + Lambda cho transactional workload — không phù hợp, phức tạp, không đảm bảo consistency.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-AZ ASG + Multi-AZ Aurora = HA trong 1 Region. Cross-Region chỉ khi cần DR"*
