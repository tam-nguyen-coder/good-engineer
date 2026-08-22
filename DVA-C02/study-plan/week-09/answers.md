# ✅ Answers & Explanations — Week 9

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-B · 2-B · 3-C · 4-B · 5-AB · 6-C · 7-B · 8-B · 9-B · 10-B · 11-AC · 12-C · 13-B · 14-C · 15-AB · 16-B · 17-B · 18-C · 19-B · 20-AC · 21-AC · 22-B · 23-AB · 24-AB · 25-B · 26-B

---

### Question 1 — Answer: **B**
- **Why correct:** CloudWatch treats **each unique dimension combination as a separate metric**, and for **custom metrics** it does **not aggregate across dimensions**. You can only query the exact combinations that were published (`{Env=Prod, Instance=i-1}`, `{Env=Prod, Instance=i-2}`); you cannot query `{Env=Prod}` on its own — unless you use the `SEARCH` metric-math function.
- **Why the others are wrong:** A — it is the opposite: only metrics from **certain AWS services** (such as EC2) are aggregated across dimensions; custom metrics are not. C — the namespace `MyApp` is valid. D — detailed monitoring relates to resolution/frequency (EC2), not dimension roll-up.
- 🧠 **Key point / trap:** "custom metric + query on a single sub-dimension → empty" happens because **each dimension combination = one metric**; to roll up you must publish that combination or use `SEARCH`.
- 📎 Source: `resources/cloudwatch-concepts.md` (Dimension combinations; "CloudWatch does not aggregate across dimensions for your custom metrics").

### Question 2 — Answer: **B**
- **Why correct:** To get **1-second** granularity you must publish a **high-resolution custom metric** (storage resolution = 1s) with `PutMetricData`; it can then be read at periods of 1, 5, 10, or 30 seconds (or multiples of 60). Standard resolution is only 1 minute.
- **Why the others are wrong:** A — **detailed monitoring** brings EC2 down to **1-minute** granularity (not 1 second). C — a standard-resolution metric does not support sub-60s periods. D — CloudWatch **does** support high resolution down to 1 second.
- 🧠 **Key point / trap:** high resolution = **1 second** (custom metric); detailed monitoring = **1 minute** — do not confuse the two.
- 📎 Source: `resources/cloudwatch-concepts.md` (Resolution; Periods — "Only custom metrics with storage resolution of 1 second support sub-minute periods").

### Question 3 — Answer: **C**
- **Why correct:** Getting an **application-defined** value into CloudWatch means calling the **`PutMetricData`** API (a custom metric). This is the standard way to publish a business metric like "orders/minute".
- **Why the others are wrong:** A — CloudTrail records API calls (audit), not business values. B — `GetMetricStatistics` **reads** metrics; it does not create data. D — detailed monitoring only increases the frequency of AWS's existing metrics; it does not count your orders.
- 🧠 **Key point / trap:** "push a custom application value" → **`PutMetricData`** (or **EMF** if you want to extract it from logs).
- 📎 Source: `resources/cloudwatch-concepts.md` (Metrics — "publish your own application metrics"); Week 9 README (Custom metric).

### Question 4 — Answer: **B**
- **Why correct:** **EMF (Embedded Metric Format)** lets Lambda **write structured logs** and CloudWatch **extracts metrics from those logs** — no synchronous `PutMetricData` call in the handler (avoiding latency and API throttling), with support for multiple dimensions.
- **Why the others are wrong:** A — calling `PutMetricData` per request is exactly what we want to avoid (added latency + cost + throttling risk). C — a subscription filter is for **streaming logs**, not the standard metric-extraction mechanism for this. D — detailed monitoring does not create the app's custom metrics.
- 🧠 **Key point / trap:** "Lambda needs custom metrics without a separate API call / without added latency" → **EMF**.
- 📎 Source: Week 9 README (EMF — "write a log and you get a metric"); `resources/cloudwatch-logs.md` (generating metrics from logs using an embedded log format).

### Question 5 — Answer: **A, B**
- **Why correct:** A **subscription filter** delivers logs in **real time** to valid destinations: Lambda (A), Kinesis Data Streams (B), Kinesis Data Firehose, and OpenSearch. Of the given options, the two correct destinations are **Lambda** and **Kinesis Data Streams**.
- **Why the others are wrong:** C — you cannot write **directly** to S3; to land in S3 you must go through Firehose. D — SNS is **not** a subscription filter target. E — a metric filter is a different mechanism (creates a metric from a log pattern), not a streaming destination.
- 🧠 **Key point / trap:** subscription filter → **Lambda / Kinesis Data Streams / Kinesis Data Firehose** (and OpenSearch). To reach S3 you go through Firehose; SNS is not on the list.
- 📎 Source: Week 9 README (Subscription filter — real-time streaming to Lambda/Kinesis/Firehose).

### Question 6 — Answer: **C**
- **Why correct:** A **metric filter** matches the `ERROR` pattern in the logs to produce a **CloudWatch metric**, then you set an **alarm** (for example `>= 5` in one period) with an SNS action. **No code changes** are required.
- **Why the others are wrong:** A — a subscription filter **streams** logs elsewhere, requiring you to write the counting logic downstream (more work). B — changing code to call `PutMetricData` violates the "no code changes" constraint. D — CloudTrail audits API calls; it does not match patterns in application logs.
- 🧠 **Key point / trap:** "create a metric/alarm from a **pattern in the logs**, without code changes" → **metric filter** (not a subscription filter).
- 📎 Source: `resources/cloudwatch-logs.md` (Metric filter — count "NullReferenceException"/"404"; "no code changes are required").

### Question 7 — Answer: **B**
- **Why correct:** **CloudWatch Logs Insights** is a purpose-built query language for **interactively querying and aggregating** logs that live in CloudWatch Logs (count, filter, sort, top-N, etc.).
- **Why the others are wrong:** A — Athena queries data in **S3** with SQL; these logs are in CloudWatch Logs, so Insights fits better (using Athena would require exporting to S3 first). C — a metric filter produces a continuous metric, not suited to complex ad-hoc querying. D — an X-Ray sampling rule is unrelated to log querying.
- 🧠 **Key point / trap:** logs in CloudWatch Logs → **Logs Insights**; logs/data in S3 → **Athena**.
- 📎 Source: `resources/cloudwatch-logs.md` (Logs Insights — "interactively search and analyze"); Week 9 README (Logs Insights vs Athena).

### Question 8 — Answer: **B**
- **Why correct:** When a resource stops sending a metric (EBS detached), the alarm transitions to **`INSUFFICIENT_DATA`** (shown **gray**) — meaning **there is not enough data to evaluate**, not necessarily that there is a problem. You can configure how missing data is treated.
- **Why the others are wrong:** A — `ALARM` (red) is when the threshold is breached. C — `OK` (green) is normal and still has data. D — CloudWatch **has no** `ERROR` state.
- 🧠 **Key point / trap:** the 3 states = **`OK` / `ALARM` / `INSUFFICIENT_DATA`**; gray = insufficient data (often because the resource is inactive / not sending the metric).
- 📎 Source: `resources/cloudwatch-alarms.md` (states; "EBS ... not attached ... state change to INSUFFICIENT_DATA ... not necessarily a problem").

### Question 9 — Answer: **B**
- **Why correct:** A **composite alarm** combines the states of multiple child alarms with an **AND/OR rule expression**, and only enters `ALARM` (and fires SNS) when the rule is satisfied — reducing alarm noise and consolidating to a single notification.
- **Why the others are wrong:** A — deleting alarms loses monitoring coverage. C — increasing the evaluation period does not consolidate alarms and slows detection. D — a composite alarm **can send SNS but CANNOT perform EC2 actions / Auto Scaling actions**; besides, switching to an EC2 action does not address "reduce the noise".
- 🧠 **Key point / trap:** "many noisy alarms, want one alert based on a combination" → **composite alarm**. Remember: composite alarms do SNS only, not EC2/ASG actions.
- 📎 Source: `resources/cloudwatch-alarms.md` (composite alarm — reduce alarm noise; "can't perform EC2 actions or Auto Scaling actions").

### Question 10 — Answer: **B**
- **Why correct:** The question "**who** called the `DeleteBucket` API, **when**, and **from where**" is exactly **auditing API activity** → **AWS CloudTrail** (Event history for 90 days, or a trail delivering to S3).
- **Why the others are wrong:** A — Logs Insights queries application logs, not the account's API calls. C — metrics are only time-series performance values. D — the X-Ray service map is for tracing requests/performance, not auditing "who deleted the bucket".
- 🧠 **Key point / trap:** the mantra — **"who did what / when / audit → CloudTrail"**; "performance/logs → CloudWatch".
- 📎 Source: `resources/cloudtrail-overview.md` ("identify who or what took which action, what resources were acted upon, when"); Week 9 README (the "who deleted the bucket" trap).

### Question 11 — Answer: **A, C**
- **Why correct:** A (`TerminateInstances` — who called it, when) and C (who modified the security group, when) are both **API activity / audit** → they require **CloudTrail**.
- **Why the others are wrong:** B (Lambda `Duration` p99), D (counting `ERROR` lines in logs), and E (CPU utilization) are all **performance / logs** → they belong to **CloudWatch** (metrics / Logs) and do not require CloudTrail.
- 🧠 **Key point / trap:** keywords "**who / principal / called an API / configuration change / when**" → CloudTrail; "**measure/count/performance/app logs**" → CloudWatch.
- 📎 Source: `resources/cloudtrail-overview.md`; `resources/lambda-metrics.md`; `resources/cloudwatch-concepts.md`.

### Question 12 — Answer: **C**
- **Why correct:** Running Lambda **on a periodic schedule** → an **EventBridge rule with a schedule expression (`cron`/`rate`)** targeting Lambda. Serverless, low operational overhead, no self-managed cron.
- **Why the others are wrong:** A — Lambda does **not self-trigger** on a schedule; keeping it warm is not a scheduling mechanism. B — running an EC2 with crontab is unnecessary infrastructure and high operational overhead. D — SQS `DelaySeconds` maxes out at **15 minutes** and cannot make a 24-hour schedule.
- 🧠 **Key point / trap:** "run a job/Lambda on a periodic schedule" → **EventBridge schedule (`cron`/`rate`)**; do not write cron inside Lambda.
- 📎 Source: `resources/eventbridge-overview.md` (scheduled rule); Week 9 README (EventBridge schedule → Lambda).

### Question 13 — Answer: **B**
- **Why correct:** The requirements — **time zones**, large-scale **one-time invocations** (thousands of schedules), a **flexible time window**, and **no event bus** — match **EventBridge Scheduler** exactly (a dedicated scheduling service, 2022).
- **Why the others are wrong:** A — a scheduled **rule** runs in **UTC** (no native time-zone awareness) and is attached to an event bus. C — cron inside Lambda is self-managed and does not scale well. D — creating a `Wait` state per schedule is very heavy and is not a scheduling tool.
- 🧠 **Key point / trap:** "time zones / one-time / thousands of schedules / no event bus" → **EventBridge Scheduler**; a "scheduled rule" is generally remembered as **UTC + attached to an event bus**.
- 📎 Source: `resources/eventbridge-overview.md` (EventBridge Scheduler — cron/rate, one-time, flexible time window); Week 9 README (rule vs Scheduler).

### Question 14 — Answer: **C**
- **Why correct:** Only **annotations** are **indexed**, so they can be used with **filter expressions** to group/find traces. Changing `addMetadata` to **`addAnnotation('orderType', ...)`** is what lets you filter by `orderType`.
- **Why the others are wrong:** A — metadata is **never** filterable, regardless of what you enable. B — stuffing the value into a segment's `name` is not a value-based filter mechanism and corrupts the meaning of the service name. D — false: metadata is **not indexed**; it is not a matter of "waiting for indexing".
- 🧠 **Key point / trap:** this is the **#1 X-Ray trap**: "**filter/find traces by a value → annotation** (indexed); metadata is for reference only".
- 📎 Source: `resources/xray-concepts.md` (Annotations "indexed for use with filter expressions"; Metadata "not indexed"); Week 9 README (self-check gate).

### Question 15 — Answer: **A, B**
- **Why correct:** Enabling X-Ray for Lambda = (A) turn on **Active tracing** on the function + (B) grant write permission via the **`AWSXRayDaemonWriteAccess`** managed policy on the execution role.
- **Why the others are wrong:** C — you do **not** need to run the daemon yourself: for Lambda, AWS runs the daemon for you. D — you do not open UDP 2000 in the Lambda security group (that detail relates to EC2/ECS environments, not Lambda). E — detailed monitoring is unrelated to tracing.
- 🧠 **Key point / trap:** Lambda + X-Ray = **Active tracing + IAM `AWSXRayDaemonWriteAccess`**; not running the daemon yourself.
- 📎 Source: Week 9 README (Lab 1 — Active tracing ON + `AWSXRayDaemonWriteAccess`).

### Question 16 — Answer: **B**
- **Why correct:** Services that do not send their own segments (such as DynamoDB) are represented by X-Ray as an **inferred segment**, built from the **subsegment** that the instrumented SDK recorded for the downstream call → the DynamoDB node and edge derive from that subsegment.
- **Why the others are wrong:** A — DynamoDB does **not** send its own segment. C — an annotation is a key-value pair for filtering, not a node-creation mechanism. D — the service map is built from X-Ray trace data, not CloudTrail.
- 🧠 **Key point / trap:** a segment = data for one service; a **subsegment = a downstream call**; a downstream service that does not support tracing → an **inferred segment** from the subsegment.
- 📎 Source: `resources/xray-concepts.md` (Subsegments — "X-Ray uses subsegments to generate inferred segments" for DynamoDB).

### Question 17 — Answer: **B**
- **Why correct:** **Sampling rules** let you set a low rate for a high-traffic endpoint (health-check) to save cost, while tracing 100% of important calls (payments). By default the SDK records the **first request each second plus 5% of the rest**.
- **Why the others are wrong:** A — turning tracing off entirely loses the payment traces too (which require 100%). C — reducing retention does not reduce the **number of traces** generated (the underlying cost). D — a filter expression is for **finding** traces, not for controlling which traces are **recorded**.
- 🧠 **Key point / trap:** "reduce trace cost/volume but still trace the important group" → **sampling rules**.
- 📎 Source: `resources/xray-concepts.md` (Sampling — default first req/sec + 5%; configuring rules "disable sampling ... for calls that modify state ... sample at a low rate for health checks").

### Question 18 — Answer: **C**
- **Why correct:** On EC2/ECS, the X-Ray SDK sends segment data to the **X-Ray daemon over UDP port 2000**; the daemon buffers it and then uploads to X-Ray. No traces usually means the daemon is **not running** or **UDP port 2000** is not reachable.
- **Why the others are wrong:** A — the SDK does not send directly over 443; it sends to the daemon. B — **active tracing** is a Lambda / API Gateway term and does not apply to a self-run app on EC2. D — the daemon listens on **UDP 2000**, not TCP 80.
- 🧠 **Key point / trap:** **X-Ray daemon = UDP port 2000**; SDK → daemon → X-Ray.
- 📎 Source: Week 9 README (the MUST-KNOW table — the daemon listens on UDP 2000, buffers and sends traces).

### Question 19 — Answer: **B**
- **Why correct:** **`IteratorAge`** (for **stream** event sources like Kinesis / DynamoDB Streams) measures the **age of the last record when it is processed**. A steady increase = the consumer **cannot keep up / is falling behind** the rate at which records are written to the stream.
- **Why the others are wrong:** A — running out of memory shows up in errors / `Duration`, not `IteratorAge`. C — throttling is measured by `Throttles`. D — code errors are measured by `Errors`.
- 🧠 **Key point / trap:** high `IteratorAge` → **stream processing lag** → add shards/parallelization, increase batch size, or optimize the processing code.
- 📎 Source: `resources/lambda-metrics.md` (`IteratorAge` — "age of the last record when processed → stream processing latency, high = falling behind").

### Question 20 — Answer: **A, C**
- **Why correct:** A — `Throttles` counts invocations **rejected because the concurrency limit was exceeded** and is **NOT** included in `Errors`. C — `Errors` counts failures **due to the function** (code errors, timeouts).
- **Why the others are wrong:** B — `Throttles` is separate and not rolled into `Errors`. D — `Invocations` includes **both** successful **and** failed invocations. E — `ConcurrentExecutions` is the **number of instances running concurrently**, not the total number of invocations.
- 🧠 **Key point / trap:** distinguish **`Throttles` (concurrency exceeded)** vs **`Errors` (function failure)**; `Invocations` includes both successes and errors.
- 📎 Source: `resources/lambda-metrics.md` (metrics table — `Throttles` "NOT included in Errors"; `Invocations` "success + error"; `ConcurrentExecutions`).

### Question 21 — Answer: **A, C**
- **Why correct:** `ProvisionedThroughputExceededException` (**429**) is **client-side throttling**. A — the standard handling is **retries with exponential backoff and jitter** (usually done by the SDK automatically). C — reduce throttling by **redistributing the partition key**, switching to **on-demand**, or increasing throughput.
- **Why the others are wrong:** B — `429` is in the **4xx (client)** group, not 5xx server; no AWS ticket is needed. D — an item > 400 KB is a different error (a `ValidationException` about item size), not `429`. E — the SDK **does** retry by default; you should not write an infinite retry loop (it can worsen congestion).
- 🧠 **Key point / trap:** `429` / `ProvisionedThroughputExceededException` → **client throttling** → **retry with exponential backoff and jitter** (plus fix the root cause: hot partition / capacity).
- 📎 Source: Week 9 README (error-code table — 4xx client, 429 throttling; `ProvisionedThroughputExceededException` → backoff + jitter).

### Question 22 — Answer: **B**
- **Why correct:** In Lambda, **more memory → proportionally more CPU** → a CPU-bound function runs faster; it is sometimes **cheaper** because the shorter duration offsets the higher memory price. Use **AWS Lambda Power Tuning** to find the optimal cost/speed configuration.
- **Why the others are wrong:** A — false, because CPU scales with memory so speed does change. C — **Provisioned Concurrency** addresses **cold starts**, not CPU for the processing itself. D — splitting the function is not a way to "add CPU" and increases complexity.
- 🧠 **Key point / trap:** "slow / CPU-bound Lambda" → **increase memory (CPU scales with it)** + **Power Tuning**; do not confuse with cold start (that is Provisioned Concurrency / SnapStart).
- 📎 Source: Week 9 README (Lambda optimization — memory→CPU, Power Tuning).

### Question 23 — Answer: **A, B**
- **Why correct:** Reducing **cold starts** = (A) **Provisioned Concurrency** (keeps initialized environments ready) and (B) **SnapStart** (a snapshot of the initialized environment; supports Java, Python, .NET; used on a version/alias).
- **Why the others are wrong:** C — `visibility timeout` belongs to SQS and is unrelated to cold starts. D — reducing memory slows initialization and does not reduce cold starts. E — switching to async does not eliminate cold starts and changes the synchronous-API invocation model.
- 🧠 **Key point / trap:** "cold start / consistent startup latency" → **Provisioned Concurrency** or **SnapStart** (remember SnapStart is Java/Python/.NET only, on a version/alias).
- 📎 Source: Week 9 README (Optimization — Provisioned Concurrency); SPEC (SnapStart for Java/Python/.NET).

### Question 24 — Answer: **A, B**
- **Why correct:** Throttling despite available capacity is usually due to a **hot partition**. A — redesigning the **partition key** for even distribution addresses the root cause. B — adding **DAX** (or a caching layer) offloads reads from the hot partition for a read-heavy workload.
- **Why the others are wrong:** C — doubling total RCU/WCU does **not** fix a hot partition (traffic still concentrates on one partition). D — TTL only auto-deletes expired items; it does not reduce throttling. E — adding an arbitrary random GSI does not solve key distribution and consumes extra capacity.
- 🧠 **Key point / trap:** "throttling despite available capacity" → **hot partition** → redistribute the partition key (+ DAX/caching / consider on-demand). Increasing total capacity is the trap.
- 📎 Source: Week 9 README (DynamoDB optimization — hot partition, DAX for read-heavy; caching layer).

### Question 25 — Answer: **B**
- **Why correct:** Increase the **batch size** + configure a **batch window** on the **event source mapping** so that one invocation processes **multiple messages**, combined with a bulk write via `BatchWriteItem` → fewer invocations, fewer requests to DynamoDB → **cheaper and less throttling**.
- **Why the others are wrong:** A — a `visibility timeout` of 0 makes messages reappear immediately and does not optimize cost. C — Provisioned Concurrency addresses cold starts, not the number of invocations. D — adding parallel consumers **increases** the load on DynamoDB, not decreases it.
- 🧠 **Key point / trap:** "reduce invocations / batch many records" → **SQS batching (batch size + batch window)** + `BatchWriteItem`.
- 📎 Source: Week 9 README (Optimization — SQS batching to reduce the number of requests); `resources/lambda-metrics.md` (event source mapping).

### Question 26 — Answer: **B**
- **Why correct:** **RDS Proxy** **pools and reuses connections** in front of RDS → many concurrent Lambda functions no longer open thousands of direct connections → the "connection storm" is resolved, with **few code changes** (only the connection endpoint changes).
- **Why the others are wrong:** A — setting `max_connections` to unlimited is infeasible and not sustainable; RDS still gets overloaded. C — a read replica spreads **read** load; it does not provide connection pooling (especially for writes). D — migrating to DynamoDB is a very large change, not a "small change".
- 🧠 **Key point / trap:** "too many Lambda functions opening too many RDS connections / connection storm" → **RDS Proxy** (pooling + retrieves credentials from Secrets Manager, more resilient during failover).
- 📎 Source: Week 9 README (Other optimizations — caching/batching/pooling); SPEC (RDS Proxy).
