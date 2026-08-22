# 📝 Practice Questions — Week 9: Troubleshooting & Optimization — CloudWatch, X-Ray, CloudTrail, EventBridge

> **26 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Week 9 material (all of Domain 4).
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D4.2 · CloudWatch · Single]`
A team publishes a custom metric named `LatencyMs` (namespace `MyApp`) as two separate time series: one with the dimensions `{Env=Prod, Instance=i-1}` and one with `{Env=Prod, Instance=i-2}`. On a dashboard, a query that specifies only `{Env=Prod}` returns **no data**. What is the most likely reason?
- A. CloudWatch automatically aggregates every dimension for custom metrics, so a query that omits `unit` returns an error
- B. Each unique dimension combination is a **separate metric**; for **custom metrics**, CloudWatch does **not aggregate across dimensions**, so you can only query the exact combinations that were published (or use the `SEARCH` metric-math function)
- C. The metric does not exist because the namespace name is invalid
- D. You must enable **detailed monitoring** before the dimensions can be rolled up together

### Question 2 — `[D4.2 · CloudWatch · Single]`
A game backend needs to track a custom latency metric at **1-second granularity** to catch short spikes. The default (standard-resolution) metric only supports 1-minute granularity. What is the correct approach?
- A. Enable **detailed monitoring** to get 1-second granularity
- B. Publish the metric as a **high-resolution custom metric** (storage resolution of 1 second) with `PutMetricData`, which can then be read at periods of 1, 5, 10, or 30 seconds
- C. Keep standard resolution but set `period = 1` second when querying
- D. CloudWatch does not support sub-minute granularity under any circumstances

### Question 3 — `[D4.2 · CloudWatch · Single]`
An application needs to send a **business metric — "orders processed per minute"** (not an AWS-provided metric) — into CloudWatch to build a dashboard and set an alarm. What is the most direct approach?
- A. Enable **CloudTrail data events** to record the order count
- B. Call `GetMetricStatistics` on a schedule to generate the metric
- C. Call the `PutMetricData` API to publish a **custom metric** to the application's namespace
- D. Enable **detailed monitoring** so that AWS counts the orders automatically

### Question 4 — `[D4.2 · CloudWatch · Single]`
A Lambda function needs to emit many custom metrics (with varied dimensions) but does **not want to add synchronous `PutMetricData` calls** inside the handler (to avoid added latency and API throttling). Which approach is most appropriate?
- A. Call `PutMetricData` for each request directly in the handler
- B. Write logs in the **Embedded Metric Format (EMF)** so that CloudWatch extracts the metrics from the logs automatically, without separate `PutMetricData` calls
- C. Create a **subscription filter** that streams logs to Kinesis and compute the metrics downstream
- D. Enable **detailed monitoring** for the Lambda function

### Question 5 — `[D4.2 · CloudWatch Logs · Multi — Choose 2]`
You need to **stream logs in real time** from a CloudWatch Logs log group to a separate processing pipeline as soon as the logs are written. Which two targets are **valid subscription filter destinations** for real-time delivery? (Choose two.)
- A. AWS Lambda
- B. Amazon Kinesis Data Streams
- C. Writing directly to Amazon S3 without any intermediate service
- D. An Amazon SNS topic
- E. A **metric filter** that pushes to a CloudWatch dashboard

### Question 6 — `[D4.2 · CloudWatch Logs · Single]`
An operations team wants to be alerted when the application logs contain **more than 5 `ERROR` lines within 5 minutes**, and the application code **must not be changed**. What is the correct approach?
- A. Create a **subscription filter** that streams logs to Lambda, which counts them and sends the email itself
- B. Change the application code to call `PutMetricData` whenever an error occurs
- C. Create a **metric filter** that matches the `ERROR` pattern to generate a metric, then set an **alarm** with an SNS action
- D. Use CloudTrail to capture the error lines in the logs

### Question 7 — `[D4.1 · CloudWatch Logs · Single]`
While troubleshooting an incident, a developer needs to **interactively query** the Lambda logs (stored in CloudWatch Logs) to find the 10 slowest requests and aggregate them by status code. Which tool is most appropriate?
- A. Amazon Athena querying directly against the log group
- B. CloudWatch Logs Insights with its purpose-built query language
- C. A **metric filter** that counts status codes
- D. An X-Ray **sampling rule**

### Question 8 — `[D4.1 · CloudWatch · Single]`
An alarm is configured on a metric from an EBS volume that has just been **detached** (and is no longer sending data). On the dashboard, the alarm appears **gray**. What state is this and what does it mean?
- A. `ALARM` — the metric has breached the threshold
- B. `INSUFFICIENT_DATA` — there is not enough data to evaluate because the resource is not sending the metric; this is **not necessarily a problem**
- C. `OK` — everything is normal
- D. `ERROR` — the alarm is misconfigured

### Question 9 — `[D4.2 · CloudWatch · Single]`
On every deployment, **5 metric alarms** all transition to `ALARM` and fire a flood of SNS notifications that overwhelm the on-call engineer. You want to receive **one** notification only when a meaningful combination of conditions occurs. What is the best approach?
- A. Delete 4 of the alarms and keep only 1
- B. Create a **composite alarm** that combines the child alarms with an **AND/OR** rule, alerting only when the rule is satisfied to reduce alarm noise
- C. Increase the **evaluation period** of each alarm to 7 days
- D. Change all of the alarms' actions to **EC2 actions**

### Question 10 — `[D4.1 · CloudTrail · Single]`
A production S3 bucket was deleted last night. The security team needs to know **who called `DeleteBucket`, at what time, and from which IP address**. Which service can answer this question?
- A. CloudWatch Logs Insights running against the application logs
- B. AWS CloudTrail (Event history / a trail) — it records who called which API, when, and from where
- C. CloudWatch metrics (time-series graphs)
- D. The AWS X-Ray service map

### Question 11 — `[D4.1 · CloudTrail · Multi — Choose 2]`
Which two of the following investigation needs **require CloudTrail** (rather than CloudWatch)? (Choose two.)
- A. Determine which **IAM principal** called `TerminateInstances` on an EC2 instance and when
- B. Track the **p99** `Duration` of a Lambda function
- C. Find **who modified** a security group and **when** the change occurred
- D. Count the number of log lines containing `ERROR` in the application
- E. Track the **CPU utilization** of an EC2 instance

### Question 12 — `[D4.2 · EventBridge · Single]`
A Lambda cleanup function must run **every day at 02:00**, with the **least operational overhead** and no self-managed cron. Which solution is correct?
- A. Write an internal cron loop inside the Lambda function and keep the function warm
- B. Run an always-on EC2 instance with a crontab that invokes the Lambda function
- C. Create an **EventBridge rule with a schedule expression (`cron`/`rate`)** that targets the Lambda function
- D. Use an SQS `DelaySeconds` of 24 hours and have the message re-enqueue itself

### Question 13 — `[D4.2 · EventBridge Scheduler · Single]`
A system needs to schedule **thousands of one-time invocations** at different **local times** (per time zone), with a **flexible time window** and retries, and **does not want to use an event bus**. Which service is the best fit?
- A. An EventBridge scheduled rule (cron runs in **UTC**) on the default event bus
- B. **EventBridge Scheduler** — supports one-time and recurring schedules, **time zones**, a flexible time window, and does not require an event bus
- C. An internal cron loop inside Lambda
- D. Step Functions with a `Wait` state for each schedule

### Question 14 — `[D4.2 · X-Ray · Single]`
A developer adds `seg.addMetadata('orderType', 'PREMIUM')` to a subsegment but **cannot filter traces by `orderType`** in the console. What needs to be done so that traces can be **filtered/searched** by `orderType`?
- A. Keep `addMetadata` but enable high resolution for the segment
- B. Write `orderType` into the segment's `name` field
- C. Use `addAnnotation('orderType', 'PREMIUM')` — **annotations are indexed** so they can be filtered/queried (metadata is **not** indexed)
- D. Metadata can also be filtered; you just need to wait for X-Ray to finish indexing

### Question 15 — `[D4.2 · X-Ray · Multi — Choose 2]`
You want to enable X-Ray tracing for a Lambda function. Which two steps are **required**? (Choose two.)
- A. Enable **Active tracing** in the function's Monitoring configuration
- B. Attach the **`AWSXRayDaemonWriteAccess`** managed policy to the function's execution role
- C. Package and run the **X-Ray daemon** yourself inside the Lambda deployment package
- D. Open **UDP port 2000** in the Lambda function's security group
- E. Enable **detailed monitoring** for the Lambda function

### Question 16 — `[D4.1 · X-Ray · Single]`
On the X-Ray service map, DynamoDB appears as a downstream node **even though DynamoDB does not send trace data itself**. Why?
- A. DynamoDB sends its own **segment** to X-Ray
- B. X-Ray creates an **inferred segment** from the **subsegment** that the instrumented SDK recorded for the downstream call
- C. It is an **annotation** added by the SDK
- D. The service map gets this data from CloudTrail

### Question 17 — `[D4.3 · X-Ray · Single]`
A very high-traffic health-check endpoint generates **too many traces** (raising costs), but you must still **trace 100% of payment requests**. Which configuration is correct?
- A. Turn off active tracing entirely for the whole application
- B. Configure **sampling rules**: a low rate for the health-check, and 100% tracing for payments (by default the SDK records the first request each second plus 5% of the rest)
- C. Reduce trace retention to 1 day to lower costs
- D. Use a **filter expression** to delete some of the stored traces

### Question 18 — `[D4.1 · X-Ray · Single]`
An application running on EC2 has the X-Ray SDK installed but **no traces appear**. Which cause/mechanism is correct?
- A. The SDK sends segments **directly over HTTPS on 443**, so nothing else needs to be checked
- B. You need to enable **active tracing** (but active tracing applies only to Lambda / API Gateway)
- C. The SDK sends segments to the **X-Ray daemon over UDP port 2000**; the daemon must be running and port 2000 must be reachable
- D. The daemon listens on **TCP port 80**

### Question 19 — `[D4.1 · Lambda · Single]`
A Lambda function consumes records from Kinesis Data Streams; the **`IteratorAge`** metric keeps **increasing**. What does this indicate?
- A. The function is running out of memory
- B. The function **cannot keep up** — records are increasingly old by the time they are processed (the consumer is falling behind the stream)
- C. The number of **throttles** is increasing
- D. The number of **code errors** is increasing

### Question 20 — `[D4.1 · Lambda · Multi — Choose 2]`
Which two statements about Lambda's default metrics are **TRUE**? (Choose two.)
- A. `Throttles` counts invocations that were **rejected because the concurrency limit was exceeded** and are **NOT** included in `Errors`
- B. `Throttles` is rolled into the `Errors` metric
- C. `Errors` counts invocations that failed **due to the function** (code errors, timeouts)
- D. `Invocations` does **not** include invocations that resulted in errors
- E. `ConcurrentExecutions` is the **total number of invocations** of the function

### Question 21 — `[D4.1 · DynamoDB · Multi — Choose 2]`
An application occasionally receives a **`ProvisionedThroughputExceededException`** (HTTP **429**) when writing to / reading from DynamoDB. Which two statements/actions are **CORRECT**? (Choose two.)
- A. Handle it with **retries using exponential backoff and jitter** (the SDK usually does this by default)
- B. This is a **5xx server error**; you need to open a ticket with AWS
- C. Consider **redistributing the partition key**, switching to **on-demand**, or increasing throughput to reduce throttling
- D. `429` means the **item exceeds 400 KB**
- E. The SDK never retries, so you must write your own infinite retry loop

### Question 22 — `[D4.3 · Lambda · Single]`
A **CPU-bound** image-processing Lambda function runs slowly at 256 MB. Which statement about optimizing it is correct?
- A. Increasing memory only **costs more** and does not change speed
- B. Increasing memory **increases CPU proportionally**, so it runs faster and is sometimes **cheaper** because the shorter duration offsets the higher memory price; use **AWS Lambda Power Tuning** to find the optimal configuration
- C. Enable **Provisioned Concurrency** to increase CPU for each invocation
- D. Split the function into 3 smaller functions to get more CPU

### Question 23 — `[D4.3 · Lambda · Multi — Choose 2]`
A latency-sensitive synchronous API is seeing its p99 spike because of **cold starts**. Which two approaches **reduce cold-start latency**? (Choose two.)
- A. Enable **Provisioned Concurrency** to keep initialized environments ready
- B. Use **SnapStart** (supports Java, Python, and .NET; applied on a version/alias)
- C. Increase the `visibility timeout`
- D. Reduce memory to the minimum
- E. Switch to invoking the function **asynchronously**

### Question 24 — `[D4.3 · DynamoDB · Multi — Choose 2]`
A DynamoDB table is being throttled (`ProvisionedThroughputExceededException`) even though the **total provisioned capacity appears to be sufficient**; traffic is concentrated on a few keys. Which two actions are **most effective**? (Choose two.)
- A. Redesign the **partition key** so that traffic is distributed evenly (avoiding a **hot partition**)
- B. Add **DAX** to cache reads (read-heavy) and offload the hot partition (or use another caching layer)
- C. Simply double the **total RCU/WCU** and you are done
- D. Enable **TTL** to automatically delete old items
- E. Add an arbitrary random **GSI**

### Question 25 — `[D4.3 · Lambda · Single]`
A Lambda function is invoked **per SQS message**, so it is invoked a very large number of times and each invocation writes a **single DynamoDB item**, driving up cost and risking throttling. What is the optimization with the fewest changes?
- A. Reduce the queue's `visibility timeout` to 0
- B. Increase the **batch size** and configure a **batch window** on the event source mapping to process multiple messages per invocation, and write with `BatchWriteItem`
- C. Enable **Provisioned Concurrency** for the function
- D. Add many more parallel Lambda consumers

### Question 26 — `[D4.3 · RDS Proxy · Single]`
Hundreds of concurrent Lambda functions open **thousands of connections** to a single RDS instance, causing a **"connection storm"** that exhausts database connections. What is the fix with the **fewest code changes**?
- A. Increase the RDS `max_connections` to unlimited
- B. Put **RDS Proxy** in front of RDS to **pool and reuse connections**, reducing the number of open connections to the database
- C. Add a **read replica** to spread the load for write statements
- D. Migrate the entire workload to DynamoDB
