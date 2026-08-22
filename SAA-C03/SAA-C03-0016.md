# Question #16 - Topic 1

A company hosts a data lake on AWS. The data lake consists of data in Amazon S3 and Amazon RDS for PostgreSQL. The company needs a reporting solution that provides data visualization and includes all the data sources within the data lake. Only the company's management team should have full access to all the visualizations. The rest of the company should have only limited access. Which solution will meet these requirements?

## Options

**A.** Create an analysis in Amazon QuickSight. Connect all the data sources and create new datasets. Publish dashboards to visualize the data. Share the dashboards with the appropriate IAM roles.

**B.** Create an analysis in Amazon QuickSight. Connect all the data sources and create new datasets. Publish dashboards to visualize the data. Share the dashboards with the appropriate users and groups.

**C.** Create an AWS Glue table and crawler for the data in Amazon S3. Create an AWS Glue extract, transform, and load (ETL) job to produce reports. Publish the reports to Amazon S3. Use S3 bucket policies to limit access to the reports.

**D.** Create an AWS Glue table and crawler for the data in Amazon S3. Use Amazon Athena Federated Query to access data within Amazon RDS for PostgreSQL. Generate reports by using Amazon Athena. Publish the reports to Amazon S3. Use S3 bucket policies to limit access to the reports.



 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty đang vận hành data lake trên AWS, bao gồm dữ liệu được lưu trữ trong `Amazon S3` và `Amazon RDS for PostgreSQL`. Công ty cần một giải pháp báo cáo cung cấp khả năng trực quan hóa dữ liệu (data visualization) và tích hợp tất cả các nguồn dữ liệu trong data lake.
- **Existing Resources:** `Amazon S3` (data lake storage), `Amazon RDS for PostgreSQL` (relational database).
- **Current Issue/Goal:** Xây dựng giải pháp báo cáo với data visualization, kết nối đồng thời cả hai nguồn dữ liệu. Đội ngũ quản lý (management team) cần có quyền truy cập đầy đủ (full access) vào tất cả các visualization, trong khi phần còn lại của công ty chỉ có quyền truy cập hạn chế (limited access).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| data visualization | Cần một công cụ BI (Business Intelligence) như `Amazon QuickSight` |
| Amazon S3 + Amazon RDS for PostgreSQL | `QuickSight` có thể kết nối trực tiếp đến cả hai nguồn này |
| full access vs limited access | Cần cơ chế phân quyền chi tiết; `QuickSight` hỗ trợ chia sẻ dashboard với `users` và `groups` |
| reporting solution | Không chỉ là truy vấn dữ liệu mà cần dashboard tương tác |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most suitable solution / Meet all requirements
- **Constraints:** Phải bao gồm cả hai nguồn dữ liệu (`S3` và `RDS`), phải có khả năng trực quan hóa, phân quyền rõ ràng giữa management team và nhân viên còn lại, tối ưu operational overhead.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- `Amazon QuickSight` là dịch vụ BI serverless được quản lý toàn phần, cho phép tạ
