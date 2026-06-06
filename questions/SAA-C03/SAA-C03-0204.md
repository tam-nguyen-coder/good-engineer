# Question #204 - Topic 1

An online retail company has more than 50 million active customers and receives more than 25,000 orders each day. The company collects purchase data for customers and stores this data in Amazon S3. Additional customer data is stored in Amazon RDS. The company wants to make all the data available to various teams so that the teams can perform analytics. The solution must provide the ability to manage fine-grained permissions for the data and must minimize operational overhead. Which solution will meet these requirements?

## Options

**A.** Migrate the purchase data to write directly to Amazon RDS. Use RDS access controls to limit access.

**B.** Schedule an AWS Lambda function to periodically copy data from Amazon RDS to Amazon S3. Create an AWS Glue crawler. Use Amazon Athena to query the data. Use S3 policies to limit access.

**C.** Create a data lake by using AWS Lake Formation. Create an AWS Glue JDBC connection to Amazon RDS. Register the S3 bucket in Lake Formation. Use Lake Formation access controls to limit access.

**D.** Create an Amazon Redshift cluster. Schedule an AWS Lambda function to periodically copy data from Amazon S3 and Amazon RDS to Amazon Redshift. Use Amazon Redshift access controls to limit access.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Purchase data in S3, customer data in RDS. Need analytics + fine-grained permissions.
- **Existing Resources:** S3 bucket, RDS.
- **Current Issue/Goal:** Centralized data lake with fine-grained access control.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `fine-grained permissions` | **AWS Lake Formation** (column/row-level access) |
| `minimize operational overhead` | Lake Formation + Glue = managed data lake |
| `analytics` | Data lake |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Analytics / Data lake
- **Constraints:** Fine-grained permissions, min overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Lake Formation** — central data lake, fine-grained access controls (column/row-level).
- **Glue JDBC connection to RDS** — kết nối đến RDS, crawl schema.
- **Register S3** bucket — dữ liệu purchase trong S3 cũng được quản lý bởi Lake Formation.
- Single point of permission management.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- RDS — không scalable cho analytics trên 50M customers, permissions không fine-grained.

**❌ Đáp án B:**
- Lambda + Glue + Athena + S3 policies — S3 policies không có row/column-level security.

**❌ Đáp án D:**
- Redshift + Lambda — operational overhead, không phải least.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lake Formation = data lake + fine-grained permissions. S3 policies = no row/column level"*
