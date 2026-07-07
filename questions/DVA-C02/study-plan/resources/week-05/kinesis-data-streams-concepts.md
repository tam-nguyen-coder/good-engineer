# Amazon Kinesis Data Streams — Terminology & concepts

> **Nguồn (AWS official):** https://docs.aws.amazon.com/streams/latest/dev/key-concepts.html
> **Tuần:** 5 — Messaging + Step Functions + Caching · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- Kiến trúc: **producers** đẩy dữ liệu vào stream → **consumers** xử lý real-time; kết quả có thể lưu vào `DynamoDB`, `Redshift`, `S3`...
- **Shard** là đơn vị scale. Số PHẢI NHỚ mỗi shard: **ghi 1 MB/s HOẶC 1.000 records/s**; **đọc 2 MB/s** và **tối đa 5 giao dịch đọc/s**; **data blob ≤ 1 MB**.
- **Retention period:** mặc định **24 giờ**, tăng tối đa **8.760 giờ = 365 ngày** (`IncreaseStreamRetentionPeriod`), giảm tối thiểu về **24 giờ** → cho phép **replay** dữ liệu (tính phí thêm nếu > 24h).
- **Partition key** quyết định record vào **shard nào** (băm MD5 128-bit); giữ **thứ tự theo partition key** trong shard. Partition key là chuỗi Unicode, tối đa **256 ký tự**.
- **Nhiều consumer** đọc **cùng** một stream **độc lập & đồng thời** (khác `SQS`); 2 loại: **shared fan-out** và **enhanced fan-out**.
- **Capacity mode:** `on-demand` (AWS tự quản shard, trả theo throughput dùng) vs `provisioned` (tự chỉ định số shard, trả theo giờ/shard).
- **KCL (Kinesis Client Library):** đảm bảo mỗi shard có 1 record processor; dùng bảng **`DynamoDB`** lưu checkpoint (tạo **3 bảng** mỗi application).
- **Sequence number:** duy nhất theo partition key trong shard, gán khi ghi; KHÔNG dùng làm index để tách tập dữ liệu.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### High-level architecture

**Producers** continually push data to Kinesis Data Streams, and **consumers** process the data in real time. Consumers (such as a custom application running on Amazon EC2 or an Amazon Data Firehose delivery stream) can store their results using an AWS service such as Amazon DynamoDB, Amazon Redshift, or Amazon S3.

### Kinesis Data Stream

A *Kinesis data stream* is a set of **shards**. Each shard has a sequence of data records. Each data record has a **sequence number** assigned by Kinesis Data Streams.

### Data Record

A *data record* is the unit of data stored in a Kinesis data stream. Data records are composed of a **sequence number**, a **partition key**, and a **data blob** (an immutable sequence of bytes). Kinesis Data Streams does not inspect, interpret, or change the data in the blob. **A data blob can be up to 1 MB.**

### Capacity Mode

A data stream *capacity mode* determines how capacity is managed and how you are charged. You can choose between **on-demand** mode and **provisioned** mode.

- **On-demand** – Kinesis Data Streams automatically manages the shards to provide the necessary throughput. You are charged only for the actual throughput you use, and it automatically accommodates workload throughput needs as they ramp up or down.
- **Provisioned** – You must specify the number of shards. The total capacity of a data stream is the sum of the capacities of its shards. You can increase or decrease the number of shards as needed and you are charged for the number of shards at an hourly rate.

### Retention Period

The *retention period* is the length of time that data records are accessible after they are added to the stream. A stream's retention period is set to a **default of 24 hours** after creation. You can **increase the retention period up to 8760 hours (365 days)** using the `IncreaseStreamRetentionPeriod` operation, and **decrease it down to a minimum of 24 hours** using the `DecreaseStreamRetentionPeriod` operation. Additional charges apply for streams with a retention period set to more than 24 hours.

### Producer

*Producers* put records into Amazon Kinesis Data Streams (e.g. a web server sending log data to a stream).

### Consumer

*Consumers* get records from Amazon Kinesis Data Streams and process them. These consumers are known as **Amazon Kinesis Data Streams Applications**.

### Amazon Kinesis Data Streams Application

A consumer of a stream that commonly runs on a fleet of EC2 instances. There are two types of consumers you can develop: **shared fan-out consumers** and **enhanced fan-out consumers**. The output of an application can be input for another stream, enabling complex real-time topologies. **There can be multiple applications for one stream, and each application can consume data from the stream independently and concurrently.**

### Shard

A *shard* is a uniquely identified sequence of data records in a stream. A stream is composed of one or more shards, each providing a fixed unit of capacity. **Each shard can support up to 5 transactions per second for reads, up to a maximum total data read rate of 2 MB per second, and up to 1,000 records per second for writes, up to a maximum total data write rate of 1 MB per second (including partition keys).** The data capacity of your stream is a function of the number of shards. The total capacity of the stream is the sum of the capacities of its shards. If your data rate increases, you can increase or decrease the number of shards (resharding).

### Partition Key

A *partition key* is used to **group data by shard** within a stream. Kinesis Data Streams segregates data records into multiple shards, using the partition key associated with each record to determine which shard it belongs to. Partition keys are **Unicode strings, with a maximum length of 256 characters** for each key. An **MD5 hash function** maps partition keys to 128-bit integer values and to shards using the hash key ranges. When an application puts data into a stream, it must specify a partition key.

### Sequence Number

Each data record has a *sequence number* that is **unique per partition-key within its shard**. Kinesis Data Streams assigns the sequence number after you write to the stream with `client.putRecords` or `client.putRecord`. Sequence numbers for the same partition key generally increase over time; the longer the time between write requests, the larger the sequence numbers become.

> **Note:** Sequence numbers cannot be used as indexes to sets of data within the same stream. To logically separate sets of data, use partition keys or create a separate stream for each dataset.

### Kinesis Client Library (KCL)

Compiled into your application to enable **fault-tolerant consumption** of data from the stream. KCL ensures that for every shard there is a **record processor** running and processing that shard. It uses **Amazon DynamoDB tables** to store metadata related to data consumption, creating **three tables per application** that is processing data.

### Application Name

Each application must have a **unique name** scoped to the AWS account and Region. This name is used as the name for the control table in DynamoDB and the namespace for CloudWatch metrics.

### Server-Side Encryption

Kinesis Data Streams can automatically encrypt sensitive data as a producer enters it into a stream, using **AWS KMS** master keys. To read from or write to an encrypted stream, producer and consumer applications must have permission to access the master key. Using server-side encryption incurs AWS KMS costs.
