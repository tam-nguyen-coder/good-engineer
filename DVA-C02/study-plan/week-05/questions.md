# 📝 Practice Questions — Week 5: Messaging (SQS/SNS/Kinesis) + Step Functions + ElastiCache + RDS Proxy

> **26 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Week 5 material (end of Domain 1).
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D1.1 · SQS · Single]`
An e-commerce platform needs to decouple order intake from the background workers that run on a fleet of Amazon EC2 instances. Order volume is extremely high during peak hours. The system does **not** require messages to be processed in order, and the worker code is already designed to be **idempotent**. Which solution is the MOST appropriate for maximizing throughput?
- A. An Amazon SQS FIFO queue with a `MessageGroupId` per customer
- B. An Amazon SQS standard queue
- C. Amazon Kinesis Data Streams with a single shard
- D. An Amazon SNS FIFO topic

### Question 2 — `[D1.1 · SQS · Multi — Choose 2]`
A payment application requires that commands be processed in the **exact order** in which they were sent and that **each command be processed only once** (no duplicates). A developer moves the workload to an Amazon SQS FIFO queue. Which two parameters or attributes are **required** to meet these requirements? (Choose two.)
- A. `MessageGroupId` to guarantee ordering within each group
- B. `VisibilityTimeout` set to 0 so messages are returned immediately
- C. `MessageDeduplicationId` (or content-based deduplication) to prevent duplicates
- D. `WaitTimeSeconds` set to 20 to enable long polling
- E. `DelaySeconds` set to 900 to space out messages

### Question 3 — `[D1.1 · SQS · Single]`
A consumer reads messages from an Amazon SQS standard queue. Processing **sometimes takes up to 8 minutes**, but the queue's visibility timeout is only **5 minutes**. As a result, the same message is received and processed a second time by a different consumer. What is the correct fix that requires the fewest changes?
- A. Switch to an SQS FIFO queue to fully eliminate duplicates
- B. Periodically call `ChangeMessageVisibility` (a heartbeat) to extend the timeout while processing is in progress
- C. Reduce the visibility timeout to 1 minute so messages return faster
- D. Enable long polling by setting `WaitTimeSeconds` to 20

### Question 4 — `[D1.1 · SQS · Single]`
Which statement is **correct** about the Amazon SQS visibility timeout, and what should a developer do if a task needs to be processed for **longer than the maximum limit**?
- A. Default is **30 seconds**, maximum is **12 hours**; if more than 12 hours is needed, use AWS Step Functions or break the task into smaller pieces
- B. Default is 30 seconds, maximum is 24 hours; calling `ChangeMessageVisibility` resets it back to 24 hours
- C. Default is 60 seconds, maximum is 12 hours; increasing retention to 14 days is sufficient
- D. Default is 0 seconds, with no maximum limit

### Question 5 — `[D1.1 · SQS · Single]`
Messages in an Amazon SQS queue must be retained for up to **10 days** so that a downstream system (which runs periodic maintenance) has time to process them. What configuration is needed, and is it feasible?
- A. Not feasible — the maximum SQS retention is 4 days
- B. Set the message retention period to 10 days (valid, because the range is ~60 seconds to 14 days; the default is 4 days)
- C. Use the SQS Extended Client to store messages in Amazon S3 for 10 days
- D. Switch to Amazon Kinesis, because SQS can only retain messages for 24 hours

### Question 6 — `[D1.1 · SQS · Single]`
An application polls an Amazon SQS queue that is frequently empty, generating many **empty responses** and increasing API costs. What is the best way to reduce empty responses and cost?
- A. Enable **long polling** by setting `WaitTimeSeconds` greater than 0 (up to a maximum of **20 seconds**)
- B. Add more consumers so the queue is polled faster
- C. Set the visibility timeout to 0
- D. Switch to **short polling** so responses return immediately

### Question 7 — `[D1.1 · SQS · Single]`
Some messages repeatedly fail during processing (poison messages) and keep returning to the main queue, clogging the consumer. Which Amazon SQS mechanism helps **isolate** these messages for investigation?
- A. A delay queue with `DelaySeconds` set to 900
- B. A dead-letter queue with a `RedrivePolicy` (`deadLetterTargetArn` plus `maxReceiveCount`)
- C. Long polling with `WaitTimeSeconds` set to 20
- D. Content-based deduplication

### Question 8 — `[D1.1 · SQS · Single]`
An application needs to send payloads of up to **1.5 MB** through Amazon SQS (for example, metadata for image-processing jobs). Which solution is the MOST appropriate?
- A. Compress the payload to under 256 KB and send it directly
- B. Split the payload into multiple 256 KB messages and reassemble them at the consumer
- C. Use the **Amazon SQS Extended Client Library**: store the payload in Amazon S3 and send a pointer through SQS (supports up to 2 GB)
- D. Switch to Amazon SNS, because SNS has no message size limit

### Question 9 — `[D1.1 · SQS · Single]`
A trading system needs an Amazon SQS FIFO queue to preserve ordering but must sustain a throughput of about **30,000 messages per second**. What is the correct way to achieve this throughput?
- A. Not feasible — SQS FIFO is hard-capped at 300 messages per second
- B. Enable **high throughput mode** for the FIFO queue and distribute messages across **many `MessageGroupId` values**
- C. Move the entire workload to an SQS standard queue
- D. Increase the visibility timeout to batch more messages together

### Question 10 — `[D1.1 · SNS · Single]`
When a new order is created, the system must push the **same event** to three **independent** processing systems: analytics, invoicing, and email — each processing at its own pace without affecting the others. Which architecture is the MOST appropriate?
- A. A single SQS standard queue that all three systems poll
- B. An SNS topic that fans out to **three SQS queues** (one dedicated queue per system)
- C. An SQS FIFO queue with three `MessageGroupId` values
- D. Writing three times to three queues from the application code

### Question 11 — `[D1.1 · SNS · Single]`
Multiple subscribers subscribe to the same Amazon SNS topic, but each subscriber wants to receive only a **subset** of messages (for example, only orders where `region = "EU"`). What should be used to avoid filtering in the consumer code?
- A. Create a separate topic for each region
- B. Attach a **filter policy** (JSON) to each subscription; SNS then delivers only matching messages
- C. Use an SQS message group to filter
- D. Enable raw message delivery on the subscription

### Question 12 — `[D1.1 · SNS/SQS · Multi — Choose 2]`
A system must **fan out** events to multiple consumers BUT must preserve **strict ordering** and **no duplicates** during distribution. Which two components must be combined? (Choose two.)
- A. An SNS **FIFO topic**
- B. An SNS standard topic with a filter policy
- C. **SQS FIFO** queues as subscribers
- D. SQS standard queues as subscribers
- E. Amazon Kinesis Data Firehose for distribution

### Question 13 — `[D1.1 · SQS/SNS/Kinesis · Multi — Choose 2]`
Requirement: the **same data** must reach **multiple consumers that read independently and concurrently**. Which two services or architectures **directly** meet this requirement? (Choose two.)
- A. Amazon SNS (pub/sub push to multiple subscribers)
- B. A single SQS standard queue polled by multiple consumers
- C. Amazon Kinesis Data Streams (multiple applications read the same stream independently)
- D. An SQS FIFO queue with a single `MessageGroupId`
- E. The SQS Extended Client

### Question 14 — `[D1.1 · Kinesis · Single]`
A platform needs to: ingest events in **real time**, preserve **ordering by partition key**, allow **multiple analytics applications to read the same data**, and be able to **replay** the last 7 days of data after a bug is discovered. Which service is the MOST appropriate?
- A. Amazon SQS standard
- B. Amazon SNS fan-out
- C. Amazon Kinesis Data Streams
- D. Amazon Kinesis Data Firehose

### Question 15 — `[D1.3 · Kinesis · Multi — Choose 2]`
An application writing to a provisioned Amazon Kinesis Data Streams starts receiving `ProvisionedThroughputExceededException` because it exceeds the per-shard write limit (**1 MB/s or 1,000 records/s**). Which two approaches are valid ways to resolve this? (Choose two.)
- A. Increase the number of shards (resharding) to raise total throughput
- B. Switch the stream to **on-demand capacity mode** so AWS manages throughput automatically
- C. Increase the stream's visibility timeout
- D. Enable long polling on the consumer
- E. Reduce the retention period to 24 hours

### Question 16 — `[D1.1 · Kinesis · Single]`
Multiple consumers read from the same Amazon Kinesis Data Streams, but they are **competing** for the **shared 2 MB/s** read limit per shard, causing latency. How can each consumer get its own dedicated **2 MB/s** read pipe per shard?
- A. Enable **enhanced fan-out** for the consumers
- B. Increase the retention period to 365 days
- C. Switch to Amazon Kinesis Data Firehose
- D. Use shared fan-out with more KCL workers

### Question 17 — `[D1.1 · Kinesis · Single]`
A startup has **spiky, unpredictable** streaming traffic, needs multiple consumers to read in real time with replay capability, but does **not want to manually calculate or adjust the number of shards**. Which option is the MOST appropriate?
- A. Amazon Kinesis Data Streams in **on-demand** capacity mode
- B. Amazon Kinesis Data Streams provisioned with a fixed single shard
- C. Amazon SQS standard
- D. Amazon Kinesis Data Firehose with size-based buffering

### Question 18 — `[D1.1 · Firehose · Single]`
Requirement: **automatically load** streaming data into Amazon S3 and Amazon Redshift with buffering (by size or time), **without writing a consumer**, and **without needing replay**. Which service is the MOST appropriate?
- A. Amazon Kinesis Data Streams with a custom KCL consumer
- B. Amazon Kinesis Data Firehose
- C. Amazon SQS with AWS Lambda
- D. Amazon SNS fan-out writing directly to S3

### Question 19 — `[D1.3 · Kinesis · Single]`
An analytics team needs to **replay** up to **1 year** of data from an Amazon Kinesis Data Streams. What must be done?
- A. Kinesis does not support replay; you must back up the data to Amazon S3 yourself
- B. Increase the retention period up to the maximum of **8,760 hours (365 days)** using `IncreaseStreamRetentionPeriod`
- C. Switch to Amazon Kinesis Data Firehose to store data longer
- D. Kinesis retention is capped at 7 days, so 1 year is not possible

### Question 20 — `[D1.1 · StepFunctions · Single]`
A process has many steps: call an API, wait, branch conditionally, **retry** on transient errors, and **catch** errors to run a compensating branch. Currently everything is crammed into a single AWS Lambda function with complex retry code. What reduces the code and improves observability?
- A. Use AWS Step Functions (Amazon States Language) with `Choice`, `Retry`, and `Catch` to orchestrate the workflow
- B. Increase the Lambda function timeout to 15 minutes
- C. Use an SQS dead-letter queue to automatically retry the entire workflow
- D. Have the Lambda function call itself recursively to repeat the steps

### Question 21 — `[D1.1 · StepFunctions · Multi — Choose 2]`
A **high-volume** IoT event-processing workload has executions that are **short (under 5 minutes)** and operations that are already **idempotent**. Which two characteristics of AWS Step Functions **Express** workflows fit this scenario? (Choose two.)
- A. A maximum run time of 5 minutes, optimized for high-volume event processing
- B. Exactly-once semantics for every execution
- C. At-least-once semantics (asynchronous), which suits idempotent operations
- D. Runs for up to 1 year for long-running workflows
- E. Billing based on the number of state transitions

### Question 22 — `[D1.2 · StepFunctions · Single]`
A **payment** workflow (non-idempotent) may run for up to **several days**, must ensure each step **runs no more than once**, and must retain **execution history for auditing**. Which type of AWS Step Functions workflow is appropriate?
- A. Express (asynchronous), because it is cheaper
- B. Express (synchronous), to wait for the result
- C. Standard — exactly-once, runs for up to 1 year, retains history for 90 days
- D. Standard, but it must be broken up because it is limited to 5 minutes

### Question 23 — `[D1.3 · ElastiCache · Multi — Choose 2]`
An application needs a caching layer with **high availability plus failover**, **persistence** (snapshots), and **rich data structures** (a sorted set for a leaderboard). Which two statements are **correct** when choosing an engine? (Choose two.)
- A. Choose Amazon ElastiCache for Redis (Valkey / Redis OSS) because it supports replication/HA and persistence
- B. Choose Memcached because it supports persistence and failover
- C. Redis supports sorted sets / lists / hashes, which suit a leaderboard
- D. Memcached is the only engine that has replication
- E. Both engines support snapshots and failover equally

### Question 24 — `[D1.3 · ElastiCache · Single]`
A cache is used for **simple** key-value data, must **scale horizontally** easily, and should take advantage of **multi-threading**, with no need for persistence or complex data structures. Which engine is the MOST appropriate?
- A. Amazon ElastiCache for Redis with cluster mode
- B. Amazon ElastiCache for Memcached
- C. Amazon DynamoDB Accelerator (DAX)
- D. An Amazon RDS read replica

### Question 25 — `[D1.3 · ElastiCache · Single]`
A development team wants to cache **only the data that is actually read** to save memory, accepts a slower first miss, and uses a **TTL** to avoid stale data. Which caching strategy correctly describes this?
- A. Write-through: write to the cache on every database write
- B. Lazy loading (cache-aside): read the cache first, and on a miss query the database and then write to the cache; combined with a TTL to prevent stale data
- C. TTL cannot be used together with lazy loading
- D. Write-behind with a 15-minute buffer

### Question 26 — `[D1.3 · RDSProxy · Multi — Choose 2]`
Many AWS Lambda functions scaling concurrently open thousands of connections to a single RDS instance, causing a **"connection storm"** that exhausts database connections. Which two benefits of Amazon RDS Proxy solve this problem **without significant code changes**? (Choose two.)
- A. Pooling and reusing connections to reduce the number of open connections to the database
- B. Automatically scaling up the RDS instance under high load
- C. Securely retrieving credentials from AWS Secrets Manager / supporting IAM authentication and improving resilience during failover
- D. Caching query results to reduce database load
- E. Replacing RDS with Amazon DynamoDB to eliminate connections entirely
