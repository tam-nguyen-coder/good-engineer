# Question #391 - Topic 1

A company needs a backup strategy for its three-tier stateless web application. The web application runs on Amazon EC2 instances in an Auto Scaling group with a dynamic scaling policy that is configured to respond to scaling events. The database tier runs on Amazon RDS for PostgreSQL. The web application does not require temporary local storage on the EC2 instances. The company's recovery point objective (RPO) is 2 hours. The backup strategy must maximize scalability and optimize resource utilization for this environment. Which solution will meet these requirements?

## Options

**A.** Take snapshots of Amazon Elastic Block Store (Amazon EBS) volumes of the EC2 instances and database every 2 hours to meet the RPO.

**B.** Configure a snapshot lifecycle policy to take Amazon Elastic Block Store (Amazon EBS) snapshots. Enable automated backups in Amazon RDS to meet the RPO.

**C.** Retain the latest Amazon Machine Images (AMIs) of the web and application tiers. Enable automated backups in Amazon RDS and use point-in-time recovery to meet the RPO.

**D.** Take snapshots of Amazon Elastic Block Store (Amazon EBS) volumes of the EC2 instances every 2 hours. Enable automated backups in Amazon RDS and use point-in-time recovery to meet the RPO.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Three-tier stateless web app, ASG + dynamic scaling, RDS PostgreSQL. No local storage needed on EC2. RPO 2 hours. Maximize scalability, optimize resource utilization.
- **Existing Resources:** ASG EC2 instances (stateless), RDS PostgreSQL.
- **Current Issue/Goal:** Backup strategy for stateless app + database.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `stateless web application` | EC2 instances không cần backup EBS snapshots (có thể launch lại từ AMI). |
| `does not require temporary local storage` | Không cần EBS snapshots. |
| `retain the latest AMIs` | AMI cho ASG launch template → scalable, không tốn tài nguyên cho snapshots. |
| `RDS automated backups + PITR` | Point-in-time recovery đáp ứng RPO 2 hours. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Maximize scalability, optimize resource utilization
- **Constraints:** RPO 2 hours, stateless web, RDS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Stateless web: không cần EBS snapshots → chỉ cần retain latest AMI cho ASG launch template (scalable, không waste resources).
- RDS automated backups + PITR: restore đến bất kỳ điểm nào trong retention period → RPO 2 hours.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EBS snapshots cho ASG instances: lãng phí (instances stateless, dynamic scaling tạo/terminate instances liên tục).

**❌ Đáp án B:**
- EBS snapshot lifecycle: vẫn waste resources cho stateless instances.

**❌ Đáp án D:**
- EBS snapshots mỗi 2 hours cho EC2: không cần thiết (stateless), tốn storage và resource utilization không tối ưu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Stateless ASG → AMI (not EBS snapshots). RDS → automated backups + PITR. EBS snapshots = waste cho stateless."*
