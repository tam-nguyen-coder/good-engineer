# Question #341 - Topic 1

A company has an Amazon S3 data lake that is governed by AWS Lake Formation. The company wants to create a visualization in Amazon QuickSight by joining the data in the data lake with operational data that is stored in an Amazon Aurora MySQL database. The company wants to enforce column-level authorization so that the company's marketing team can access only a subset of columns in the database. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use Amazon EMR to ingest the data directly from the database to the QuickSight SPICE engine. Include only the required columns.

**B.** Use AWS Glue Studio to ingest the data from the database to the S3 data lake. Attach an IAM policy to the QuickSight users to enforce column-level access control. Use Amazon S3 as the data source in QuickSight.

**C.** Use AWS Glue Elastic Views to create a materialized view for the database in Amazon S3. Create an S3 bucket policy to enforce column- level access control for the QuickSight users. Use Amazon S3 as the data source in QuickSight.

**D.** Use a Lake Formation blueprint to ingest the data from the database to the S3 data lake. Use Lake Formation to enforce column-level access control for the QuickSight users. Use Amazon Athena as the data source in QuickSight.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 data lake (Lake Formation governed) + Aurora MySQL. Cần QuickSight visualization với column-level access control.
- **Existing Resources:** S3 data lake, Lake Formation, Aurora MySQL.
- **Current Issue/Goal:** Join data + column-level auth, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `column-level authorization` | Lake Formation hỗ trợ column-level permissions (không cần IAM/S3 bucket policy cho từng column). |
| `Lake Formation blueprint` | Tự động ingest data từ Aurora MySQL vào S3 data lake. |
| `Athena as the data source` | QuickSight có thể kết nối Athena query S3 data lake. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Column-level access, join S3 + Aurora, QuickSight

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Lake Formation blueprint: ingest Aurora data vào S3 data lake tự động.
- Lake Formation: column-level access control (grant SELECT on specific columns cho marketing team).
- QuickSight kết nối Athena → Athena query S3 data lake thông qua Lake Formation permissions.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EMR → SPICE: không tích hợp Lake Formation column-level access. Phải tự xử lý column filtering.

**❌ Đáp án B:**
- IAM policy không thể enforce column-level access control (IAM chỉ check action/resource, không check column).

**❌ Đáp án C:**
- S3 bucket policy không thể enforce column-level access (bucket policy chỉ apply ở bucket/object level).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Column-level access trong data lake → Lake Formation (column permissions). IAM/S3 policy = object level, không column."*
