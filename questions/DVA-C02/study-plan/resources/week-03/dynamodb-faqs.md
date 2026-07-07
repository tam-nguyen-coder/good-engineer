# Amazon DynamoDB FAQs

> **Nguồn (AWS official):** https://aws.amazon.com/dynamodb/faqs/
> **Tuần:** 3 — DynamoDB · **Loại:** AWS FAQ
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Item size tối đa = 400 KB.** Không giới hạn số item hay tổng dung lượng table. File/ảnh lớn → lưu ở `S3`, chỉ lưu **pointer/URL/key** trong DynamoDB.
- Dữ liệu tự động replicate **đồng bộ qua 3 AZ** trong 1 Region → high availability + durability.
- **2 table class:** `Standard` (đọc/ghi rẻ, storage đắt) vs `Standard-IA` (storage rẻ, đọc/ghi đắt). Đổi qua lại **tối đa 2 lần/30 ngày**, không downtime.
- **Global Tables:** multi-Region, multi-active, **99.999% availability**, không có primary Region → không cần failover. Tiên quyết: bật **DynamoDB Streams**, cùng tên table, cùng partition key. Dùng version **2019.11.21 (Current)** cho table mới.
- **TTL:** tự xóa item hết hạn, **KHÔNG tiêu thụ write throughput**.
- **DynamoDB Streams vs Kinesis Data Streams for DynamoDB:** Streams giữ **24h**, có ordering + dedup; Kinesis giữ lâu hơn, throughput cao hơn nhưng **KHÔNG** đảm bảo ordering/dedup.
- **Encryption:** luôn mã hóa in-transit (HTTPS/TLS) và at-rest (**AES-256** qua KMS). 3 loại key: AWS owned (mặc định, free), AWS managed, Customer managed.
- **On-demand vs Provisioned:** on-demand cho workload không đoán trước / pay-per-use (scale-to-zero); provisioned cho traffic đều/đoán được.
- **Free tier:** 25 GB storage + 25 WCU + 25 RCU (~200M request/tháng).
- **VPC:** hỗ trợ **Gateway endpoint** (không cho truy cập từ on-prem / peered VPC khác Region / transit gateway) và **PrivateLink / interface endpoint**.
- Primary key có thể là single (partition key) hoặc composite (partition + sort key); query trên non-key attribute qua **GSI/LSI**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Amazon DynamoDB FAQs

## About DynamoDB

### What is DynamoDB?
DynamoDB is a serverless, fully managed, distributed NoSQL database service with "single-digit millisecond performance at any scale." It offers zero infrastructure management, zero downtime maintenance, instant scaling, and pay-per-request billing. For globally distributed applications, DynamoDB global tables provide multi-Region, multi-active database capability with "up to 99.999% availability" and support multi-Region strong consistency.

### What does DynamoDB manage on my behalf?
DynamoDB offloads administrative burdens including hardware provisioning, setup and configuration, throughput capacity planning, replication, software patching, and cluster scaling. It "automatically scales throughput capacity to meet workload demands, and partitions and repartitions your data as your table size grows." DynamoDB "synchronously replicates data across three Availability Zones (AZs) in an AWS Region" for high availability and durability.

### What are the advantages of DynamoDB?
DynamoDB is a "proven fully managed, scale-to-zero serverless database that provides single-digit millisecond performance and up to 99.999% availability."

## Storage

### What are DynamoDB table classes?
Two table classes exist: DynamoDB **Standard** (designed for maximum performance and unpredictable workloads) and DynamoDB **Standard-Infrequent Access (Standard-IA)** (optimized for tables where storage is the dominant cost). "Standard tables have lower costs for reads and writes but higher storage costs. Standard-IA tables have lower storage costs but higher costs for reads and writes." You can "switch between these table classes **twice in a 30-day period** without downtime."

### What factors should I consider when choosing a table class?
Key factors include your data's access patterns, cost considerations, and workload predictability. You can switch between table classes "without any coding or downtime."

### How do DynamoDB Standard-IA tables work with existing DynamoDB features?
Standard-IA tables use the same APIs as regular DynamoDB tables and support Global Tables, point-in-time recovery (PITR), on-demand backups, encryption at rest using AWS KMS, DynamoDB Streams, Time To Live, transactional read/write operations, and compatibility with DAX.

### How does DynamoDB store data?
"A partition is an allocation of storage for a table, backed by solid state drives (SSDs) and automatically replicated across multiple Availability Zones within an AWS Region. Partition management is handled entirely by DynamoDB."

### What is the maximum allowed item size in DynamoDB?
"The maximum size of an item that can be stored in a DynamoDB table is **400 KB**. There are no predefined storage limits."

### Can DynamoDB store a Binary Large Object Storage (BLOB)?
Yes, but "it is not generally suited to storing documents or images. A better architectural pattern is to store pointers to Amazon S3 objects in a DynamoDB table."

### How long does data stay in DynamoDB?
"There is no set expiration or deletion time for data stored in an Amazon DynamoDB table by default. Data will remain in the table indefinitely unless explicitly deleted by the customer or through Time to Live (TTL) deletes if TTL is enabled."

### How many items can be stored in DynamoDB?
"There is no predefined limit to the number of items that can be stored in a DynamoDB table. DynamoDB scales to hundreds of terabytes or more of data across any number of items."

### Can you store images in DynamoDB?
Technically possible as base64-encoded binary, but "there are some limitations and drawbacks due to the 400KB item limit size. Instead of storing images directly in DynamoDB, a better practice is to store the images in Amazon S3 and then store the S3 object URL or key in DynamoDB."

### Can you store lists in DynamoDB?
Use "one of DynamoDB's list data types - either a List or a Set."

### Can DynamoDB store a map?
Yes, "DynamoDB supports storing maps as an attribute data type."

## Security

### Does Amazon DynamoDB support IAM permissions?
Yes. IAM permissions can be defined in identity-based policies, resource-based policies, or other AWS policies to control access to DynamoDB resources.

### What is AWS PrivateLink for Amazon DynamoDB?
"With AWS PrivateLink, you can simplify private network connectivity between VPCs, DynamoDB, and your on-premises data centers using interface VPC endpoints and private IP addresses." Requests do not leave the Amazon network.

### Does DynamoDB support resource-based policies?
Yes, for tables and streams. The resource-based policies for each table also cover the access permissions for the table's indexes (GSIs and LSIs).

### Does DynamoDB support attribute-based access control (ABAC)?
Yes — generally available for DynamoDB tables and indexes.

### Can I use Amazon DynamoDB in Amazon VPC?
Yes, via VPC endpoints. DynamoDB supports two types: **gateway endpoints** and **AWS PrivateLink** (interface endpoints). "Gateway endpoints do not allow access from on-premises networks, from peered VPCs in other AWS Regions, or through a transit gateway."

### What is Amazon DynamoDB fine-grained access control?
"Fine-grained access control (FGAC) gives a DynamoDB table owner granular control over data in the table through IAM policies and conditions."

### Does Amazon DynamoDB encrypt my data in transit and at rest?
"Yes, all user data in Amazon DynamoDB is fully encrypted in transit and at rest."

### How does DynamoDB encrypt my data in transit?
"HTTPS protocol is used to protect network traffic by using Secure Sockets Layer encryption."

### How does DynamoDB encrypt my data at rest?
"DynamoDB encryption at rest uses encryption keys stored in AWS KMS. Data at rest is encrypted using **AES-256**."

### What key types are available to encrypt my DynamoDB data at rest?
Three key types: **AWS owned keys** (managed by AWS, free, default); **AWS managed keys** (CMKs in KMS, created and managed by AWS); and **Customer managed keys** (created and managed by you, highest control).

### Does DynamoDB support audit logging for item level changes?
Yes, "DynamoDB is integrated with AWS CloudTrail" at the item level (creates, updates, deletes, and conditional check failures).

### Can I use DynamoDB with applications that require HIPAA compliance?
"Yes... including protected health information under an executed Business Associate Agreement (BAA) with AWS."

### What compliance certifications does DynamoDB meet?
"HIPAA eligible, FedRAMP, ISO 27001, SOC 1/SSAE 16/ISAE 3402 (formerly SAS 70), and SOC 2."

## High Availability and Resilience

### What is DynamoDB global tables?
"A fully managed, serverless, multi-Region, and multi-active database. Global tables provides **99.999% availability**, increased application resiliency, and improved business continuity. It replicates your DynamoDB tables automatically across your choice of AWS Regions."

### What is the difference between global tables versions?
Two versions: **version 2019.11.21 (Current)** and version 2017.11.29 (Legacy). "Customers should use version 2019.11.21 (Current) for all new global tables, as this version is more efficient and consumes less write capacity."

### How do I upgrade my global tables to version 2019.11.21 (Current)?
A one-time action in the console; "cannot be reversed."

### Does DynamoDB global tables support automatic failover if a Region becomes unavailable?
"DynamoDB global tables uses multi-active replication across Regions, where all replica tables in all Regions support read and write traffic. **A global table has no primary Region, and thus no database failover is required.**"

### What is a replica table for DynamoDB?
"A single DynamoDB table that is part of the global table replication group. Each replica table stores the same set of data items and uses the same primary key schema."

### Should I consider DynamoDB global tables for my business continuity strategy?
"Yes... With multi-Region strong consistency, you can build applications with **zero RPO**."

### What are the prerequisites for DynamoDB global tables?
"The table must have **DynamoDB Streams enabled**, have the **same name** as all other replicas, have the **same partition key** as all other replicas, and have the **same write capacity settings** specified."

### Is point-in-time recovery available on DynamoDB global tables?
"Yes, you can enable point-in-time recovery on each replica of a DynamoDB global table."

## Integrations

### Does DynamoDB support change data capture?
"Yes... implemented using a streaming model allowing applications to capture item-level changes in near real-time as a stream of data records."

### What is DynamoDB Streams and what can I do with it?
"A DynamoDB stream is an ordered flow of information about changes to items in a DynamoDB table. DynamoDB Streams captures a **de-duplicated, time-ordered** sequence of item-level modifications in a table and stores this information in a log for **up to 24 hours**."

### What is Kinesis Data Streams for DynamoDB and what can I do with it?
"Kinesis Data Streams captures item-level modifications in any DynamoDB table and replicates them to a Kinesis data stream." "Unlike DynamoDB Streams, Kinesis Data Streams for DynamoDB **does not provide record ordering nor deduplication guarantees**."

### What information is included in a stream?
A stream record includes "the specific time any item was recently created, updated, or deleted, that item's primary key, an image of the item before the modification, and an image of the item after the modification."

### When should I use DynamoDB stream vs. Kinesis data stream?
"Choose DynamoDB Streams when you specifically need to track DynamoDB table changes. Choose Kinesis Data Streams for broader streaming needs, higher throughput requirements, or when you need **longer data retention** periods."

### What is DynamoDB Time-to-Live (TTL) and what can I do with it?
"Amazon DynamoDB Time to Live (TTL) feature automatically deletes expired items... reducing storage usage and lowering costs. DynamoDB automatically deletes the item from your table **without consuming any write throughput**."

### What kind of query functionality does DynamoDB support?
"DynamoDB supports GET/PUT operations by using a user-defined primary key." You can also "query on nonprimary key attributes using **global secondary indexes and local secondary indexes**." "A primary key can be either a single-attribute partition key or a composite partition-sort key." "DynamoDB supports primary keys composed of up to eight attributes in GSIs, with up to four attributes each for the partition and sort keys."

### Why should I use DynamoDB zero-ETL integration with Amazon OpenSearch Service?
It "abstracts away the operational complexity in orchestrating the replication of data from a transactional datastore to a search datastore," enabling near real-time search results from transactional data. Choose a CDC mechanism (Streams or Incremental Exports); the integration sets up an OpenSearch Ingestion pipeline. No additional cost apart from the underlying components (OCUs, optional S3).

## Billing

### Is Amazon DynamoDB supported on Database Savings Plans?
"Yes... reduce your costs by up to **18%** when you commit to a consistent amount of usage over a 1-year term."

### Does DynamoDB offer a free tier?
"Yes, DynamoDB provides a generous free tier with **25GB of storage and 25 provisioned Write and 25 provisioned Read Capacity Units** (WCU, RCU), which is enough to handle 200M requests per month."

### When should I use DynamoDB on-demand versus provisioned capacity mode?
"On-demand is better suited to customers who prefer to only pay for what they use or have unpredictable workloads. Provisioned capacity is popular with customers with applications that demonstrate consistent or predictable traffic."

### What are the billing units for DynamoDB serverless on-demand?
"When the database is in-use, write request units and read request units are used to calculate charges."

### What are the extra cost options available for DynamoDB?
On-demand backup, Global tables for multi-region replication, DynamoDB Accelerator (DAX), and DynamoDB streams.
