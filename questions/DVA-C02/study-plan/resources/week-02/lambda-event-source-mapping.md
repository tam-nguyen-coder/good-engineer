# How Lambda processes records from stream and queue-based event sources (Event source mappings)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html
> **Tuần:** 2 — `Lambda` nâng cao · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Event source mapping (ESM)** = tài nguyên Lambda **poll** (kéo) record từ stream/queue rồi gọi function theo **batch**. Do **Lambda** tạo & quản lý.
- Nguồn dùng ESM: `DynamoDB`, `Kinesis`, `SQS`, `Amazon MQ`, `Amazon MSK`, self-managed `Kafka`, `Amazon DocumentDB`.
- Khác với **trigger** (S3/SNS/API Gateway): trigger là dịch vụ **push** event tới Lambda, được lưu/quản lý bởi **dịch vụ nguồn**, hợp với event rời rạc/real-time.
- ⚠️ ESM xử lý **at least once** → có thể **trùng record** → code phải **idempotent**.
- Lambda gọi function khi 1 trong 3 điều kiện đạt: (1) **batching window** hết; (2) đạt **batch size**; (3) payload đạt **6 MB** (không sửa được).
- **Batching window** mặc định: **0 giây** cho Kinesis/DynamoDB/SQS; **500 ms** cho MSK/Kafka/MQ/DocumentDB. Cấu hình `MaximumBatchingWindowInSeconds` từ **0–300 giây**.
- ⚠️ Đã đổi window theo giây thì **không quay lại được 500 ms** mặc định (phải tạo ESM mới).
- Lỗi function: mặc định **reprocess cả batch** đến khi thành công hoặc item hết hạn; với **stream (DynamoDB/Kinesis)** cấu hình được số lần retry tối đa và gửi record bị bỏ tới **destination**.
- **Provisioned mode** (chỉ MSK, self-managed Kafka, SQS): đặt min/max event pollers; scale nhanh **3×**, throughput cao **16×**. SQS pollers: min 2–200 (mặc định 2), max 2–2000 (mặc định 200). Kafka pollers: min 1–200 (mặc định 1), max 1–2000 (mặc định 200).

---

## 📄 Nội dung (trích từ tài liệu gốc)

An *event source mapping* is a Lambda resource that reads items from stream and queue-based services and invokes a function with batches of records. Within an event source mapping, resources called *event pollers* actively poll for new messages and invoke functions. By default, Lambda automatically scales event pollers, but for certain event source types, you can use provisioned mode to control the minimum and maximum number of event pollers dedicated to your event source mapping.

The following services use event source mappings to invoke Lambda functions:
- Amazon DocumentDB (with MongoDB compatibility)
- Amazon DynamoDB
- Amazon Kinesis
- Amazon MQ
- Amazon Managed Streaming for Apache Kafka (Amazon MSK)
- Self-managed Apache Kafka
- Amazon Simple Queue Service (Amazon SQS)

**Warning:** Lambda event source mappings process each event at least once, and duplicate processing of records can occur. To avoid potential issues related to duplicate events, we strongly recommend that you make your function code idempotent.

## How event source mappings differ from direct triggers

Some AWS services can directly invoke Lambda functions using *triggers*. These services push events to Lambda, and the function is invoked immediately when the specified event occurs. Triggers are suitable for discrete events and real-time processing. The trigger is actually stored and managed by the service that generates the events, not by Lambda. Examples:
- **Amazon S3:** Invokes a function when an object is created, deleted, or modified in a bucket.
- **Amazon SNS:** Invokes a function when a message is published to an SNS topic.
- **Amazon API Gateway:** Invokes a function when an API request is made to a specific endpoint.

Event source mappings are Lambda resources created and managed within the Lambda service. Event source mappings are designed for processing high-volume streaming data or messages from queues. Processing records from a stream or queue in batches is more efficient than processing records individually.

## Batching behavior

By default, an event source mapping batches records together into a single payload that Lambda sends to your function. To fine-tune batching behavior, you can configure a batching window (`MaximumBatchingWindowInSeconds`) and a batch size (`BatchSize`). A batching window is the maximum amount of time to gather records into a single payload. A batch size is the maximum number of records in a single batch. Lambda invokes your function when one of the following three criteria is met:

- **The batching window reaches its maximum value.** Default batching window behavior varies depending on the specific event source.
  - **For Kinesis, DynamoDB, and Amazon SQS event sources:** The default batching window is 0 seconds. This means that Lambda invokes your function as soon as records are available. To set a batching window, configure `MaximumBatchingWindowInSeconds`. You can set this parameter to any value from 0 to 300 seconds in increments of 1 second. If you configure a batching window, the next window begins as soon as the previous function invocation completes.
  - **For Amazon MSK, self-managed Apache Kafka, Amazon MQ, and Amazon DocumentDB event sources:** The default batching window is 500 ms. You can configure `MaximumBatchingWindowInSeconds` to any value from 0 seconds to 300 seconds in increments of seconds.
  - **For Amazon MQ and Amazon DocumentDB event sources:** The default batching window is 500 ms. A batching window begins as soon as the first record arrives.

  **Note:** Because you can only change `MaximumBatchingWindowInSeconds` in increments of seconds, you cannot revert to the 500 ms default batching window after you have changed it. To restore the default batching window, you must create a new event source mapping.

- **The batch size is met.** The minimum batch size is 1. The default and maximum batch size depend on the event source. See the `BatchSize` specification for the `CreateEventSourceMapping` API operation.
- **The payload size reaches 6 MB.** You cannot modify this limit.

The `CreateEventSourceMapping` `BatchSize` parameter controls the maximum number of records that can be sent to your function with each invoke. A larger batch size can often more efficiently absorb the invoke overhead across a larger set of records, increasing your throughput.

Lambda doesn't wait for any configured extensions to complete before sending the next batch for processing. This can cause throttling issues if you breach any of your account's concurrency settings or limits.

By default, if your function returns an error, the event source mapping reprocesses the entire batch until the function succeeds, or the items in the batch expire. To ensure in-order processing, the event source mapping pauses processing for the affected shard until the error is resolved. For stream sources (DynamoDB and Kinesis), you can configure the maximum number of times that Lambda retries when your function returns an error. Service errors or throttles where the batch does not reach your function do not count toward retry attempts. You can also configure the event source mapping to send an invocation record to a destination when it discards an event batch.

## Provisioned mode

Lambda event source mappings use event pollers to poll your event source for new messages. By default, Lambda manages the autoscaling of these pollers based on message volume.

In provisioned mode, you can fine-tune the throughput of your event source mapping by defining minimum and maximum limits for dedicated polling resources that remain ready to handle expected traffic patterns. These resources auto-scale 3 times faster to handle sudden spikes in event traffic and provide 16 times higher capacity to process millions of events.

In Lambda, an event poller is a compute unit with throughput capabilities that vary by event source type. Using provisioned mode incurs additional costs based on your event poller usage. Provisioned mode is available for Amazon MSK, self-managed Apache Kafka, and Amazon SQS event sources.

Each event poller supports different throughput capacity:
- For Amazon MSK and self-managed Apache Kafka: up to 5 MB/sec of throughput or up to 5 concurrent invokes
- For Amazon SQS: up to 1 MB/sec of throughput or up to 10 concurrent invokes or up to 10 SQS polling API calls per second.

For Amazon SQS event source mappings, you can set the minimum number of pollers between 2 and 200 with a default of 2, and the maximum number between 2 and 2,000 with a default of 200. Lambda scales the number of event pollers between your configured minimum and maximum, quickly adding up to 1,000 concurrency per minute.

For Kafka event source mappings, you can set the minimum number of pollers between 1 and 200 with a default of 1, and the maximum number between 1 and 2,000 with a default of 200.

Note that for Amazon SQS event sources, the maximum concurrency setting cannot be used with provisioned mode. When using provisioned mode, you control concurrency through the maximum event pollers setting.

To minimize latency in provisioned mode, set `MaximumBatchingWindowInSeconds` to 0. After configuring provisioned mode, you can observe the usage of event pollers by monitoring the `ProvisionedPollers` metric.

## Event source mapping API

To manage an event source with the AWS CLI or an AWS SDK, you can use the following API operations:
- `CreateEventSourceMapping`
- `ListEventSourceMappings`
- `GetEventSourceMapping`
- `UpdateEventSourceMapping`
- `DeleteEventSourceMapping`
