# Question #214 - Topic 1

A company's reporting system delivers hundreds of .csv files to an Amazon S3 bucket each day. The company must convert these files to Apache Parquet format and must store the files in a transformed data bucket. Which solution will meet these requirements with the LEAST development effort?

## Options

**A.** Create an Amazon EMR cluster with Apache Spark installed. Write a Spark application to transform the data. Use EMR File System (EMRFS) to write files to the transformed data bucket.

**B.** Create an AWS Glue crawler to discover the data. Create an AWS Glue extract, transform, and load (ETL) job to transform the data. Specify the transformed data bucket in the output step.

**C.** Use AWS Batch to create a job definition with Bash syntax to transform the data and output the data to the transformed data bucket. Use the job definition to submit a job. Specify an array job as the job type.

**D.** Create an AWS Lambda function to transform the data and output the data to the transformed data bucket. Configure an event notification for the S3 bucket. Specify the Lambda function as the destination for the event notification.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Hundreds of .csv files daily → convert to Parquet → store in transformed bucket.
- **Existing Resources:** Source S3 bucket.
- **Current Issue/Goal:** CSV→Parquet ETL, least development effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `convert these files to Apache Parquet` | **AWS Glue ETL** (built-in transform) |
| `least development effort` | Glue ETL — managed, GUI-based |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** ETL / Data transformation
- **Constraints:** CSV→Parquet, least dev effort

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Glue crawler** — tự động discover schema của CSV.
- **Glue ETL job** — convert CSV → Parquet, write to transformed bucket.
- Visual ETL jobs available — minimal code.
- Serverless, managed.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EMR + Spark — cần viết Spark application, quản lý cluster.

**❌ Đáp án C:**
- AWS Batch + Bash — not suitable for CSV→Parquet conversion, dev effort.

**❌ Đáp án D:**
- Lambda — time limit (15 phút), có thể timeout cho files 2-5GB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Glue ETL = managed CSV→Parquet. EMR + Spark = more dev effort. Lambda = timeout risk"*
