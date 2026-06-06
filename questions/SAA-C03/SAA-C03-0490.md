# Question #490 - Topic 1

A gaming company uses Amazon DynamoDB to store user information such as geographic location, player data, and leaderboards. The company needs to configure continuous backups to an Amazon S3 bucket with a minimal amount of coding. The backups must not affect availability of the application and must not affect the read capacity units (RCUs) that are defined for the table. Which solution meets these requirements?

## Options

**A.** Use an Amazon EMR cluster. Create an Apache Hive job to back up the data to Amazon S3.

**B.** Export the data directly from DynamoDB to Amazon S3 with continuous backups. Turn on point-in-time recovery for the table.

**C.** Configure Amazon DynamoDB Streams. Create an AWS Lambda function to consume the stream and export the data to an Amazon S3 bucket.

**D.** Create an AWS Lambda function to export the data from the database tables to Amazon S3 on a regular basis. Turn on point-in-time recovery for the table.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming company dùng DynamoDB lưu user data. Cần continuous backups to S3 với minimal coding. Backup không ảnh hưởng availability và không dùng RCUs.
- **Existing Resources:** DynamoDB table.
- **Current Issue/Goal:** Continuous backup to S3, no impact on app/RCUs, minimal code.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `continuous backups to an Amazon S3 bucket` | DynamoDB native export to S3 (PITR-based). |
| `minimal amount of coding` | Native feature, không cần code Lambda. |
| `must not affect availability` | Export from PITR uses backup, không ảnh hưởng production table. |
| `must not affect the RCUs` | PITR export không dùng RCUs (dùng backup storage). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Backup solution
- **Constraints:** No impact on availability/RCUs, minimal coding, continuous to S3.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- DynamoDB có **native export to S3** feature (introduced 2020): export table data directly to S3.
- **Point-in-time recovery (PITR)** tạo continuous backups với 35-day retention.
- Export từ PITR **không ảnh hưởng** production table availability và **không tiêu tốn RCUs**.
- **No custom code** required - chỉ cần enable PITR và dùng DynamoDB export console/API.
- Đây là giải pháp với minimal coding nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **EMR + Hive:** Overkill, cần quản lý cluster, code Hive job → operational overhead cao.

**❌ Đáp án C:**
- **DynamoDB Streams + Lambda:** Cần code Lambda function để xử lý stream records và write to S3 → nhiều code hơn so với native export.

**❌ Đáp án D:**
- **Lambda + PITR:** Vẫn cần code Lambda để export data. Native export đã có sẵn, không cần Lambda.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DynamoDB backup to S3 → native export + PITR = zero code, zero RCU impact."*
