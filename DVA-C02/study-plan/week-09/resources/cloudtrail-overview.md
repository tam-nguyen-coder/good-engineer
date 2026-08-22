# What Is AWS CloudTrail? (Event history, CloudTrail Lake, Trails)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html
> **Tuần:** 9 — Observability & Optimization · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **`CloudTrail` = audit API activity:** ghi lại **AI (user/role/service) đã gọi API gì, tác động resource nào, KHI NÀO, từ đâu**. Đây là ranh giới sống còn với `CloudWatch` (metrics/logs/hiệu năng).
- **3 cách ghi event:**
  1. **Event history** — record **90 ngày gần nhất** của **management events** trong 1 Region; xem/tìm/tải/immutable; **có sẵn tự động, MIỄN PHÍ**. Filter theo **1 thuộc tính** tại một thời điểm.
  2. **CloudTrail Lake** — data lake quản lý, chuyển JSON row-based sang **Apache ORC** (columnar); gom vào **event data store** (immutable); giữ tới **3.653 ngày (~10 năm)** với gói one-year extendable, hoặc **2.557 ngày (~7 năm)** với gói seven-year. Có tính phí.
  3. **Trails** — ghi liên tục & giao vào **S3 bucket** (kèm tuỳ chọn giao tới **`CloudWatch Logs`** và **`EventBridge`**). **1 bản copy management events ongoing giao vào S3 miễn phí** (chỉ trả phí lưu S3).
- **Trail có thể cho single account hoặc multi-account qua AWS Organizations.**
- Tuỳ chọn cấu hình trail: prefix S3, giao tới CloudWatch Logs, mã hoá **KMS**, bật **`SNS`** notification khi giao log file, tag.
- **Insights events**: phân tích management events để phát hiện bất thường về **API call rate / error rate**.
- 🧠 Câu bẫy: "ai đã xoá bucket / thay đổi cấu hình" → **`CloudTrail`**, không phải `CloudWatch`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# What Is AWS CloudTrail?

AWS CloudTrail is an AWS service that helps you enable operational and risk auditing, governance, and compliance of your AWS account. Actions taken by a user, role, or an AWS service are recorded as events in CloudTrail. Events include actions taken in the AWS Management Console, AWS Command Line Interface, and AWS SDKs and APIs.

CloudTrail provides three ways to record events:

+ **Event history** – The Event history provides a viewable, searchable, downloadable, and immutable record of the past 90 days of management events in an AWS Region. You can search events by filtering on a single attribute. You automatically have access to the Event history when you create your account. There are no CloudTrail charges for viewing the Event history.

+ **CloudTrail Lake** – AWS CloudTrail Lake is a managed data lake for capturing, storing, accessing, and analyzing user and API activity on AWS for audit and security purposes. CloudTrail Lake converts existing events in row-based JSON format to Apache ORC format. ORC is a columnar storage format that is optimized for fast retrieval of data. Events are aggregated into *event data stores*, which are immutable collections of events based on criteria that you select by applying advanced event selectors. You can keep the event data in an event data store for up to 3,653 days (about 10 years) if you choose the One-year extendable retention pricing option, or up to 2,557 days (about 7 years) if you choose the Seven-year retention pricing option. You can create an event data store for a single AWS account or for multiple AWS accounts by using AWS Organizations. You can import any existing CloudTrail logs from your S3 buckets into an existing or new event data store. CloudTrail Lake event data stores and queries incur charges. When you run queries in Lake, you pay based upon the amount of data scanned.

+ **Trails** – Trails capture a record of AWS activities, delivering and storing these events in an Amazon S3 bucket, with optional delivery to CloudWatch Logs and Amazon EventBridge. You can input these events into your security monitoring solutions. You can also use your own third-party solutions or solutions such as Amazon Athena to search and analyze your CloudTrail logs. You can create trails for a single AWS account or for multiple AWS accounts by using AWS Organizations. You can log Insights events to analyze your management events for anomalous behavior in API call rates and error rates. You can deliver one copy of your ongoing management events to your S3 bucket at no charge from CloudTrail by creating a trail, however, there are Amazon S3 storage charges.

Visibility into your AWS account activity is a key aspect of security and operational best practices. You can use CloudTrail to view, search, download, archive, analyze, and respond to account activity across your AWS infrastructure. You can identify who or what took which action, what resources were acted upon, when the event occurred, and other details to help you analyze and respond to activity in your AWS account.

You can integrate CloudTrail into applications using the API, automate trail or event data store creation for your organization, check the status of event data stores and trails you create, and control how users view CloudTrail events.

## Accessing CloudTrail

You can work with CloudTrail in any of the following ways:
+ CloudTrail console
+ AWS CLI
+ CloudTrail APIs
+ AWS SDKs

### CloudTrail console

Sign in to the AWS Management Console and open the CloudTrail console at https://console.aws.amazon.com/cloudtrail/. The console provides a UI for tasks such as:
+ Viewing recent events and event history for your AWS account.
+ Downloading a filtered or complete file of the last 90 days of management events from Event history.
+ Creating and editing CloudTrail trails.
+ Creating and editing CloudTrail Lake event data stores.
+ Running queries on event data stores.
+ Configuring CloudTrail trails, including: selecting an Amazon S3 bucket for trails; setting a prefix; configuring delivery to CloudWatch Logs; using AWS KMS keys for encryption of trail data; enabling Amazon SNS notifications for log file delivery on trails; adding and managing tags for your trails.
+ Configuring CloudTrail Lake event data stores, including: integrating event data stores with CloudTrail partners or with your own applications, to log events from sources outside of AWS; federating event data stores to run queries from Amazon Athena; using AWS KMS keys for encryption; adding and managing tags.

### AWS CLI

The AWS Command Line Interface is a unified tool that you can use to interact with CloudTrail from the command line. For a complete list of CloudTrail CLI commands, see `cloudtrail` and `cloudtrail-data` in the AWS CLI Command Reference.

### CloudTrail APIs

In addition to the console and the CLI, you can also use the CloudTrail RESTful APIs to program CloudTrail directly. See the AWS CloudTrail API Reference and the CloudTrail-Data API Reference.

### AWS SDKs

As an alternative to using the CloudTrail API, you can use one of the AWS SDKs. Each SDK consists of libraries and sample code for various programming languages and platforms. The SDKs provide a convenient way to create programmatic access to CloudTrail (sign requests cryptographically, manage errors, retry requests automatically).
