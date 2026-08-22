# Question #156 - Topic 1

A company produces batch data that comes from different databases. The company also produces live stream data from network sensors and application APIs. The company needs to consolidate all the data into one place for business analytics. The company needs to process the incoming data and then stage the data in different Amazon S3 buckets. Teams will later run one-time queries and import the data into a business intelligence tool to show key performance indicators (KPIs). Which combination of steps will meet these requirements with the LEAST operational overhead? (Choose two.)

## Options

**A.** Use Amazon Athena for one-time queries. Use Amazon QuickSight to create dashboards for KPIs.

**B.** Use Amazon Kinesis Data Analytics for one-time queries. Use Amazon QuickSight to create dashboards for KPIs.

**C.** Create custom AWS Lambda functions to move the individual records from the databases to an Amazon Redshift cluster.

**D.** Use an AWS Glue extract, transform, and load (ETL) job to convert the data into JSON format. Load the data into multiple Amazon OpenSearch Service (Amazon Elasticsearch Service) clusters.

**E.** Use blueprints in AWS Lake Formation to identify the data that can be ingested into a data lake. Use AWS Glue to crawl the source, extract the data, and load the data into Amazon S3 in Apache Parquet format.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Consolidate batch + live stream data → S3 data lake. One-time queries + BI dashboards.
- **Existing Resources:** Databases, sensors, APIs.
- **Current Issue/Goal:** Data lake + analytics, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `one-time queries` | **Athena** (serverless SQL on S3) |
| `business intelligence tool` | **QuickSight** (managed BI) |
| `least operational overhead` | **Lake Formation + Glue** (managed data lake) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data analytics
- **Constraints:** Chọn 2, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và E**

**Giải thích:**
- **A: Athena + QuickSight** — serverless SQL queries + managed BI dashboard.
- **E: Lake Formation + Glue** — managed data lake, crawl/ETL vào S3 dạng Parquet (tối ưu cho Athena).
- Data lake trên S3 → Athena query → QuickSight visualize.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Kinesis Data Analytics — real-time analytics, không phải one-time queries.

**❌ Đáp án C:**
- Lambda + Redshift — operational overhead, không phải least.

**❌ Đáp án D:**
- Glue → OpenSearch — OpenSearch là search engine, không phải BI tool.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lake Formation + Glue = data lake. Athena = query S3. QuickSight = BI. Parquet = optimal format"*
