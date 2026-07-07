# What is Amazon CloudWatch Logs? (log group/stream, retention, filters, Insights)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html
> **Tuần:** 9 — Observability & Optimization · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Retention mặc định = vô hạn (không hết hạn).** Phải tự đặt retention policy cho từng **log group** (chọn từ **1 ngày đến 10 năm**) để khỏi tốn tiền lưu trữ. Đây là bẫy đề kinh điển.
- **Log classes:** `Standard` (đủ tính năng) vs `Infrequent Access` (ingest rẻ hơn, ít tính năng hơn) — chọn IA cho log ít truy cập.
- **Metric filter:** khớp **pattern** trong log (vd đếm `"NullReferenceException"` hoặc mã `404`) → sinh ra **CloudWatch metric** → làm nền cho alarm. Không cần đổi code app.
- **Subscription filter (không nêu chi tiết trên trang này nhưng là tính năng đi kèm):** stream log real-time; trang này nhấn mạnh **Live Tail** để xem log gần real-time khi troubleshoot sự cố.
- **CloudWatch Logs Insights:** query language chuyên dụng để tìm kiếm & phân tích log tương tác; có sample query cho nhiều loại AWS service log.
- **Field indexes:** đánh index field trong log event → query Insights bỏ qua event không chứa field → giảm scan volume, trả kết quả nhanh hơn.
- **Nguồn log phổ biến:** EC2, `AWS CloudTrail`, Route 53 (DNS query logs), và các service khác. Log mã hoá cả khi truyền và khi lưu (in transit + at rest).
- **Deletion protection:** chống xoá nhầm log group; **mặc định TẮT**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# What is Amazon CloudWatch Logs?

You can use Amazon CloudWatch Logs to monitor, store, and access your log files from Amazon Elastic Compute Cloud (Amazon EC2) instances, AWS CloudTrail, Route 53, and other sources.

CloudWatch Logs enables you to centralize the logs from all of your systems, applications, and AWS services that you use, in a single, highly scalable service. You can then easily view them, search them for specific error codes or patterns, filter them based on specific fields, or archive them securely for future analysis. CloudWatch Logs enables you to see all of your logs, regardless of their source, as a single and consistent flow of events ordered by time.

CloudWatch Logs also supports querying your logs with a powerful query language, auditing and masking sensitive data in logs, and generating metrics from logs using filters or an embedded log format.

CloudWatch Logs supports two *log classes*. Log groups in the *CloudWatch Logs Standard log class* support all CloudWatch Logs features. Log groups in the *CloudWatch Logs Infrequent Access log class* incur lower ingestion charges and support a subset of the Standard class capabilities.

## Features

+ **Two log classes for flexibility** – CloudWatch Logs offers two log classes so that you can have a cost-effective option for logs that you access infrequently. You also have a full-featured option for logs that require real-time monitoring or other features.
+ **Query your log data** – You can use CloudWatch Logs Insights to interactively search and analyze your log data. CloudWatch Logs Insights includes a purpose-built query language with a few simple but powerful commands. We provide sample queries, command descriptions, query autocompletion, and log field discovery to help you get started. Sample queries are included for several types of AWS service logs.
+ **Create field indexes to make queries more efficient** – You can create *field indexes* of fields in your log events. When you then use a field index in a CloudWatch Logs Insights query, the query attempts to skip processing log events that are known to not include the indexed field. This query reduces the scan volume of your queries, making it possible to return results faster.
+ **Detect and debug using Live Tail** – You can use Live Tail to quickly troubleshoot incidents by viewing a streaming list of new log events as they are ingested. You can view, filter, and highlight ingested logs in near real time. You can filter the logs based on terms you specify, and also highlight logs that contain specified terms.
+ **Monitor logs from Amazon EC2 instances** – You can use CloudWatch Logs to monitor applications and systems using log data. For example, CloudWatch Logs can track the number of errors that occur in your application logs and send you a notification whenever the rate of errors exceeds a threshold you specify. CloudWatch Logs uses your log data for monitoring; so, no code changes are required. For example, you can monitor application logs for specific literal terms (such as "NullReferenceException") or count the number of occurrences of a literal term at a particular position in log data (such as "404" status codes in an Apache access log). When the term you are searching for is found, CloudWatch Logs reports the data to a CloudWatch metric that you specify. Log data is encrypted while in transit and while it is at rest.
+ **Monitor AWS CloudTrail logged events** – You can create alarms in CloudWatch and receive notifications of particular API activity as captured by CloudTrail and use the notification to perform troubleshooting.
+ **Audit and mask sensitive data** – If you have sensitive data in your logs, you can help safeguard it with *data protection policies*. These policies let you audit and mask the sensitive data. If you enable data protection, then by default, sensitive data that matches the data identifiers you select is masked.
+ **Log retention** – By default, logs are kept indefinitely and never expire. You can adjust the retention policy for each log group, keeping the indefinite retention, or choosing a retention period between 10 years and one day.
+ **Deletion protection** – A safeguard that prevents accidental deletion of log groups and their log streams. When enabled on a log group, deletion protection blocks all deletion operations until it is explicitly disabled. By default, deletion protection is not enabled. This optional feature helps protect critical operational and compliance data from unintended removal, such as log groups that contain audit data, and production application logs for troubleshooting and analysis.
+ **Archive log data** – You can use CloudWatch Logs to store your log data in highly durable storage. The CloudWatch Logs agent makes it easy to quickly send both rotated and non-rotated log data off of a host and into the log service.
+ **Log Route 53 DNS queries** – You can use CloudWatch Logs to log information about the DNS queries that Route 53 receives.
+ **Centralize logs across accounts and regions** – You can use CloudWatch Logs Centralization to define cross-account and cross-region centralization rules that replicate log data ingested across multi-account and region environments into a central region and account.

## Related AWS services

The following services are used in conjunction with CloudWatch Logs:
+ **AWS CloudTrail** – enables you to monitor the calls made to the CloudWatch Logs API for your account, including calls made by the AWS Management Console, AWS CLI, and other services. When CloudTrail logging is turned on, CloudTrail captures API calls in your account and delivers the log files to the Amazon S3 bucket that you specify.
+ **AWS Identity and Access Management (IAM)** – helps you securely control access to AWS resources for your users.
+ **Amazon Kinesis Data Streams** – a web service you can use for rapid and continuous data intake and aggregation. Because the response time for the data intake and processing is in real time, processing is typically lightweight.
+ **AWS Lambda** – a web service you can use to build applications that respond quickly to new information. Upload your application code as Lambda functions and Lambda runs your code on high-availability compute infrastructure.

## Pricing

When you sign up for AWS, you can get started with CloudWatch Logs for free using the AWS Free Tier. Standard rates apply for logs stored by other services using CloudWatch Logs (for example, Amazon VPC flow logs and Lambda logs).
