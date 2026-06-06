# Question #225 - Topic 1

A media company collects and analyzes user activity data on premises. The company wants to migrate this capability to AWS. The user activity data store will continue to grow and will be petabytes in size. The company needs to build a highly available data ingestion solution that facilitates on-demand analytics of existing data and new data with SQL. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Send activity data to an Amazon Kinesis data stream. Configure the stream to deliver the data to an Amazon S3 bucket.

**B.** Send activity data to an Amazon Kinesis Data Firehose delivery stream. Configure the stream to deliver the data to an Amazon Redshift cluster.

**C.** Place activity data in an Amazon S3 bucket. Configure Amazon S3 to run an AWS Lambda function on the data as the data arrives in the S3 bucket.

**D.** Create an ingestion service on Amazon EC2 instances that are spread across multiple Availability Zones. Configure the service to forward data to an Amazon RDS Multi-AZ database.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Petabyte-scale user activity data. HA ingestion + on-demand SQL analytics. Least overhead.
- **Existing Resources:** On-prem data collection.
- **Current Issue/Goal:** Streaming ingestion + serverless analytics.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `petabytes in size` | **S3** — scalable, cheap |
| `on-demand analytics... with SQL` | **Athena** on S3 (implicit) |
| `highly available data ingestion` | **Kinesis Data Stream** (HA by design) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data ingestion / Analytics
- **Constraints:** Petabyte-scale, HA, SQL analytics

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Kinesis Data Stream** — real-time, HA ingestion.
- Data delivered to **S3** — scalable petabyte storage.
- **Athena** — query S3 data with SQL (on-demand, serverless).
- Least overhead — fully managed.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Firehose → Redshift — Redshift là provisioned, operational overhead.

**❌ Đáp án C:**
- S3 + Lambda — Lambda xử lý từng object, không phải streaming ingestion.

**❌ Đáp án D:**
- EC2 + RDS Multi-AZ — operational overhead cao, không petabyte-scale.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Kinesis + S3 + Athena = serverless streaming analytics. Redshift = provisioned (more overhead)"*
