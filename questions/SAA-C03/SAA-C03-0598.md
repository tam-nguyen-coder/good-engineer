# Question #598 - Topic 1

A research company uses on-premises devices to generate data for analysis. The company wants to use the AWS Cloud to analyze the data. The devices generate .csv files and support writing the data to an SMB file share. Company analysts must be able to use SQL commands to query the data. The analysts will run queries periodically throughout the day. Which combination of steps will meet these requirements MOST cost-effectively? (Choose three.)

## Options

**A.** Deploy an AWS Storage Gateway on premises in Amazon S3 File Gateway mode.

**B.** Deploy an AWS Storage Gateway on premises in Amazon FSx File Gateway made.

**C.** Set up an AWS Glue crawler to create a table based on the data that is in Amazon S3.

**D.** Set up an Amazon EMR cluster with EMR File System (EMRFS) to query the data that is in Amazon S3. Provide access to analysts.

**E.** Set up an Amazon Redshift cluster to query the data that is in Amazon S3. Provide access to analysts.

**F.** Setup Amazon Athena to query the data that is in Amazon S3. Provide access to analysts.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-prem devices generate .csv files → SMB share → AWS Cloud analysis. Analysts use SQL, query periodically.
- **Existing Resources:** On-prem devices, SMB file share.
- **Current Issue/Goal:** Ingest .csv files to AWS, enable SQL querying, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SMB file share` | Storage Gateway File Gateway hỗ trợ SMB → chuyển file lên S3. |
| `.csv files` | Structured data → có thể query bằng SQL. |
| `SQL commands` | Athena (serverless SQL), Redshift (provisioned), EMR (big data). |
| `periodically throughout the day` | Athena: pay per query, cost-effective cho occasional queries. |
| `AWS Glue crawler` | Tạo table schema từ CSV trong S3 cho Athena. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effectively (Choose three)
- **Constraints:** .csv, SMB, SQL queries, periodic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, C, F**

**Giải thích:**
- **A (S3 File Gateway):** On-prem devices write .csv to SMB share → File Gateway syncs to S3.
- **C (AWS Glue crawler):** Crawl CSV files in S3, create/update table schema trong Glue Data Catalog.
- **F (Amazon Athena):** Serverless SQL query engine, pay per query, cost-effective cho periodic queries.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- FSx File Gateway: link to Amazon FSx (Windows file server), không tối ưu cho analytics với S3 + Athena.

**❌ Đáp án D:**
- Amazon EMR cluster: provisioned cluster, cần chạy 24/7 hoặc start/stop → cost cao hơn Athena cho occasional queries.

**❌ Đáp án E:**
- Amazon Redshift cluster: data warehouse, provisioned 24/7 → đắt, overkill cho periodic SQL queries.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CSV + SMB + periodic SQL → S3 File Gateway + Glue crawler + Athena (serverless, pay per query). EMR/Redshift = 24/7 cost."*
