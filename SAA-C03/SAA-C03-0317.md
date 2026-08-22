# Question #317 - Topic 1

A company uses a legacy application to produce data in CSV format. The legacy application stores the output data in Amazon S3. The company is deploying a new commercial off-the-shelf (COTS) application that can perform complex SQL queries to analyze data that is stored in Amazon Redshift and Amazon S3 only. However, the COTS application cannot process the .csv files that the legacy application produces. The company cannot update the legacy application to produce data in another format. The company needs to implement a solution so that the COTS application can use the data that the legacy application produces. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create an AWS Glue extract, transform, and load (ETL) job that runs on a schedule. Configure the ETL job to process the .csv files and store the processed data in Amazon Redshift.

**B.** Develop a Python script that runs on Amazon EC2 instances to convert the .csv files to .sql files. Invoke the Python script on a cron schedule to store the output files in Amazon S3.

**C.** Create an AWS Lambda function and an Amazon DynamoDB table. Use an S3 event to invoke the Lambda function. Configure the Lambda function to perform an extract, transform, and load (ETL) job to process the .csv files and store the processed data in the DynamoDB table.

**D.** Use Amazon EventBridge to launch an Amazon EMR cluster on a weekly schedule. Configure the EMR cluster to perform an extract, transform, and load (ETL) job to process the .csv files and store the processed data in an Amazon Redshift table.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Legacy app tạo CSV trong S3. COTS app chỉ query được Redshift và S3 (non-CSV formats). Cannot change legacy app.
- **Existing Resources:** S3 bucket with CSV files.
- **Current Issue/Goal:** Convert CSV data thành format mà COTS app có thể query, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Amazon Redshift and Amazon S3 only` | COTS app chỉ làm việc với Redshift và S3 → cần transform CSV → load vào Redshift. |
| `cannot process the .csv files` | Cần ETL để convert CSV sang format khác hoặc load vào database. |
| `least operational overhead` | AWS Glue là managed ETL service, không cần quản lý infrastructure. |
| `LEAST operational overhead` | Glue (serverless) < EMR (cần cluster) < EC2 (cần quản lý). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** COTS app only supports Redshift/S3, cannot change legacy app

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS Glue ETL job: managed service, serverless (không cần quản lý servers), schedule job để transform CSV và load vào Redshift.
- Redshift là destination phù hợp vì COTS app có thể query Redshift.
- Operational overhead thấp nhất: chỉ cần viết ETL script (PySpark/Scala) và schedule.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- EC2 + Python script: cần quản lý EC2 instance, cron, monitoring → operational overhead cao hơn Glue.

**❌ Đáp án C:**
- DynamoDB không được COTS app hỗ trợ (chỉ Redshift và S3).

**❌ Đáp án D:**
- EMR cluster: cần launch và terminate cluster, operational overhead cao hơn Glue (serverless).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CSV in S3 → Redshift → AWS Glue ETL (serverless). EC2/EMR = nhiều overhead hơn."*
