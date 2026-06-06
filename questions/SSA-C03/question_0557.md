# Question #557 - Topic 1

A solutions architect manages an analytics application. The application stores large amounts of semistructured data in an Amazon S3 bucket. The solutions architect wants to use parallel data processing to process the data more quickly. The solutions architect also wants to use information that is stored in an Amazon Redshift database to enrich the data. Which solution will meet these requirements?

## Options

**A.** Use Amazon Athena to process the S3 data. Use AWS Glue with the Amazon Redshift data to enrich the S3 data.

**B.** Use Amazon EMR to process the S3 data. Use Amazon EMR with the Amazon Redshift data to enrich the S3 data.

**C.** Use Amazon EMR to process the S3 data. Use Amazon Kinesis Data Streams to move the S3 data into Amazon Redshift so that the data can be enriched.

**D.** Use AWS Glue to process the S3 data. Use AWS Lake Formation with the Amazon Redshift data to enrich the S3 data.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ứng dụng analytics có semistructured data lớn trong S3. Cần parallel data processing để tăng tốc và enrich data với thông tin từ Redshift.
- **Existing Resources:** S3 bucket (semistructured data), Amazon Redshift database.
- **Current Issue/Goal:** Parallel processing + enrichment từ Redshift.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `semistructured data` | JSON, Parquet, ORC, Avro – EMR xử lý tốt |
| `parallel data processing` | Cần distributed processing framework |
| `enrich the data` | Kết hợp với dữ liệu từ Redshift |
| `Amazon EMR` | Managed Hadoop/Spark framework, parallel processing |
| `Amazon Redshift` | Data warehouse, có thể kết nối từ EMR |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Parallel processing, enrich with Redshift data

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Amazon EMR hỗ trợ Apache Spark, có thể đọc dữ liệu từ S3 (semistructured data) và thực hiện parallel processing với distributed computing.
- EMR có thể kết nối trực tiếp đến Amazon Redshift thông qua Spark-Redshift connector (EMR Spark-Redshift) hoặc JDBC/ODBC để enrich dữ liệu.
- EMR tự động scale cluster, phù hợp với "large amounts of data" và "parallel data processing".

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (Athena + Glue):** Amazon Athena là query engine (SQL), không phải parallel processing framework cho ETL jobs phức tạp. AWS Glue có thể kết nối Redshift nhưng không mạnh bằng EMR cho parallel processing với semistructured data.

**❌ Đáp án C (EMR + Kinesis Data Streams):** Kinesis Data Streams dùng cho real-time streaming data, không phải để "move S3 data into Redshift". Nếu muốn move S3 → Redshift, nên dùng COPY command hoặc Redshift Spectrum.

**❌ Đáp án D (Glue + Lake Formation):** AWS Glue có thể xử lý data, nhưng không mạnh bằng EMR cho parallel processing. AWS Lake Formation dùng để quản lý data lake permissions, không phải để enrich data.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Parallel processing of semistructured data in S3 + Redshift enrich = EMR with Spark. Athena = SQL queries, not ETL."*
