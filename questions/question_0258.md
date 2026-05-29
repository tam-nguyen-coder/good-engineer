# Question #258 - Topic 1

A company has an application that places hundreds of .csv files into an Amazon S3 bucket every hour. The files are 1 GB in size. Each time a file is uploaded, the company needs to convert the file to Apache Parquet format and place the output file into an S3 bucket. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create an AWS Lambda function to download the .csv files, convert the files to Parquet format, and place the output files in an S3 bucket. Invoke the Lambda function for each S3 PUT event.

**B.** Create an Apache Spark job to read the .csv files, convert the files to Parquet format, and place the output files in an S3 bucket. Create an AWS Lambda function for each S3 PUT event to invoke the Spark job.

**C.** Create an AWS Glue table and an AWS Glue crawler for the S3 bucket where the application places the .csv files. Schedule an AWS Lambda function to periodically use Amazon Athena to query the AWS Glue table, convert the query results into Parquet format, and place the output files into an S3 bucket.

**D.** Create an AWS Glue extract, transform, and load (ETL) job to convert the .csv files to Parquet format and place the output files into an S3 bucket. Create an AWS Lambda function for each S3 PUT event to invoke the ETL job.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Hundreds of 1GB .csv files/hour → convert to Parquet → S3.
- **Existing Resources:** Source S3 bucket.
- **Current Issue/Goal:** Serverless CSV→Parquet conversion.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `1 GB in size` | Lambda timeout risk (max 15 phút) |
| `least operational overhead` | **AWS Glue ETL** (managed, serverless) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** ETL / Data transformation
- **Constraints:** 1GB files, automated, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Glue ETL job** — serverless, managed, phù hợp cho 1GB files (no timeout).
- **Lambda** — trigger khi file mới upload → invoke Glue job.
- Glue tự động scale cho hundreds of files/hour.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda — có thể timeout cho 1GB files (max 15 phút).

**❌ Đáp án B:**
- Spark job + Lambda — cần quản lý Spark, operational overhead.

**❌ Đáp án C:**
- Glue + Athena + Lambda — phức tạp, không cần thiết.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Glue ETL + Lambda trigger = serverless CSV→Parquet. Lambda alone = timeout for large files"*
