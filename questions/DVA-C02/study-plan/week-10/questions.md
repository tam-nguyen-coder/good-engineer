# 📝 Practice Questions — Week 10: Final Cumulative Mock Exam (Cross-Domain)

> **25 questions** · **cross-domain mini mock** in real DVA-C02 exam style, difficulty ≥ real exam · covers **all 4 domains** (not scoped to a single topic like previous weeks).
> ⏱️ **This is a cumulative cross-domain mock — run it timed, ~50 minutes for 25 questions (pace ~2 minutes/question), straight through with no reference material, then self-grade with [answers.md](answers.md).** It is a scaled-down version of the full 65-question / 130-minute mock; use it to check your reflexes across all 4 domains before the official full mocks later in the week.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first. answers.md includes a **per-domain score analysis** → find which domain is weak and go back to the matching week.
> Exam-weighted mix: **D1 8 questions (32%) · D2 7 questions (28%) · D3 6 questions (24%) · D4 4 questions (16%)**. Domain order is **shuffled** (like the real exam).
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D1.2 · Lambda · Single]`
An internal service invokes a Lambda function **asynchronously** (`InvocationType=Event`). Recently, some JSON payloads as large as **2 MB** are rejected at invocation time, and when the function fails while processing an event, the event seems to **disappear** without a trace. Which solution will BEST allow large payloads to be accepted while ensuring failed events are not lost?
- A. The asynchronous payload limit is **6 MB**; asynchronous failures are retried **indefinitely**, so events cannot be lost.
- B. The asynchronous payload limit is **256 KB**; compress the payload and switch to **synchronous invocation** so events are not lost.
- C. The asynchronous payload limit is **1 MB**, so the 2 MB payload is rejected; store the large payload in Amazon S3 and **pass a reference**, and configure an **on-failure destination** (or a DLQ) to retain failed events.
- D. Raise the asynchronous payload limit to **6 MB** in the function configuration and enable a DLQ.

### Question 2 — `[D2.1 · STS · Single]`
A Lambda function running in **Account A** needs to read a DynamoDB table in **Account B**. The solution must follow **least privilege**, use **no long-term access keys**, and rely on **temporary credentials**. Which approach is the correct implementation?
- A. Create an IAM **user** in Account B, issue an access key, and store it in a `KMS`-encrypted environment variable of the Lambda function.
- B. Create an IAM **role** in Account B with a **trust policy** that allows the Lambda function's execution role (in Account A) to call `sts:AssumeRole`; the function calls `AssumeRole` to obtain temporary credentials and then accesses the table.
- C. Use `AssumeRoleWithWebIdentity` through an Amazon Cognito identity pool to obtain cross-account credentials.
- D. Have the function call `GetSessionToken` to obtain temporary credentials and use them directly to access the table in Account B.

### Question 3 — `[D3.4 · CodeDeploy · Single]`
A team wants to deploy a new version of a Lambda function so that: **10% of traffic** is shifted for **5 minutes** before shifting the remaining **100%**, with an **automatic rollback** when a CloudWatch alarm triggers. Which configuration is correct?
- A. `CodeDeployDefault.LambdaCanary10Percent5Minutes` — CodeDeploy shifts traffic via a **weighted alias** between the old and new versions and uses a CloudWatch alarm for automatic rollback.
- B. `CodeDeployDefault.LambdaLinear10PercentEvery5Minutes`.
- C. Use the Elastic Beanstalk **Traffic splitting** policy.
- D. `AllAtOnce` combined with **reserved concurrency**.

### Question 4 — `[D1.3 · DynamoDB · Single]`
Multiple Lambda functions run concurrently and update **the same item** (an inventory count) in DynamoDB. The team needs to **prevent lost updates** **without** a pessimistic lock, at low cost and with minimal architectural change. Which approach is the MOST appropriate?
- A. Use `TransactWriteItems` on every update to "lock" the whole table.
- B. Enable DynamoDB Streams + Lambda to serialize the updates.
- C. Before each write, run a `Scan` with `ConsistentRead=true` to read the latest value.
- D. Use **optimistic locking** with a `version` attribute + a **conditional write** (`ConditionExpression` matching the expected version); on failure, retry with exponential backoff.

### Question 5 — `[D4.2 · X-Ray · Single]`
On the X-Ray service map, the team wants to **filter/search traces by** `customerId` and `tier`, and also attach a **large debug payload** (which does not need to be searchable). Which is the correct way to record this data?
- A. Record **everything** as **annotations** to guarantee it is searchable.
- B. Record `customerId`/`tier` as **annotations** (indexed → can filter/group) and the debug payload as **metadata** (not indexed).
- C. Record **everything** as **metadata** to save cost.
- D. Use **subsegment names** to filter and put the payload in an **annotation**.

### Question 6 — `[D2.2 · KMS · Single]`
A developer needs to encrypt a **50 MB** file before storing it in Amazon S3, using a **KMS customer managed key**, with the fewest possible `KMS` API calls, and **without exposing** the data key in plaintext at rest. Which is the standard approach?
- A. Call `Encrypt` directly on the 50 MB of data with the CMK.
- B. Split the file into **4 KB** blocks and call `Encrypt` on each block.
- C. Call `GenerateDataKey` → encrypt the file **locally** with the plaintext data key, store the **encrypted data key** alongside the object, then **delete** the plaintext key from memory (envelope encryption).
- D. Use **SSE-C** and supply the key in every request.

### Question 7 — `[D1.1 · Kinesis · Single]`
A system ingests **real-time clickstream** data. Requirements: preserve **per-user ordering**, support **multiple independent consumers** (analytics + fraud) that each need their **own full throughput**, and allow **replaying 3 days** of data. Which service is the MOST appropriate?
- A. Amazon Kinesis Data Streams with partition key = `userId`; enable **enhanced fan-out** (2 MB/s per consumer per shard); set 3-day retention for replay.
- B. Amazon SQS FIFO with `MessageGroupId` = `userId` and a DLQ.
- C. An Amazon SNS FIFO topic fanning out to 2 SQS queues.
- D. Amazon Kinesis Data Firehose loading into Amazon S3, with each consumer re-reading from S3.

### Question 8 — `[D3.4 · Elastic Beanstalk · Single]`
An application on Elastic Beanstalk must deploy with **zero downtime** and these requirements: **launch entirely new instances** and **do not touch** the healthy running instances (if the new version fails, the old instances remain intact); temporarily **doubling capacity** is acceptable. Which deployment policy should be used?
- A. **All at once**.
- B. **Traffic splitting**.
- C. **Rolling with additional batch**.
- D. **Immutable** — build entirely new instances in a temporary Auto Scaling group and swap only after health checks pass; running instances are never mutated.

### Question 9 — `[D1.2 · Lambda · Multi — Choose 2]`
A latency-sensitive Lambda function written in **Java** suffers spikes in **cold starts** as it scales. It must also **guarantee** it never exceeds `N` concurrent executions to protect a backend **RDS** database. Choose the **2** correct measures. (Choose two.)
- A. Enable **SnapStart** **together with** provisioned concurrency on the same version so their benefits add up.
- B. Enable **provisioned concurrency** on the production alias to eliminate cold starts at baseline.
- C. Increase **memory to 10 GB** to completely eliminate cold starts.
- D. Set **reserved concurrency** = `N` to cap the function's concurrency and protect RDS.
- E. Point provisioned concurrency at `$LATEST` so it applies immediately.

### Question 10 — `[D2.3 · Secrets Manager · Single]`
An application needs **database credentials rotated automatically every 30 days** (with no code redeployment) and native integration with RDS. It also needs to store some **non-sensitive config** at the **lowest possible cost**. Which combination is optimal?
- A. Hard-code the credentials in a `KMS`-encrypted environment variable and rotate them manually every 30 days.
- B. Use Secrets Manager for the DB credentials (enable **automatic rotation** with RDS integration) + SSM Parameter Store (Standard, `String`) for the non-sensitive config to save cost.
- C. Use SSM Parameter Store `SecureString` for the DB credentials because it has **free built-in RDS rotation**.
- D. Use Secrets Manager for **both** the credentials and the config to keep everything in one place.

### Question 11 — `[D3.1 · CodeBuild · Multi — Choose 2]`
In `buildspec.yml`, a team needs to: (1) run unit tests and **surface a test report**, (2) **cache `Maven` dependencies** between builds, and (3) load a DB password from Secrets Manager. Which two statements about `buildspec.yml` are **correct**? (Choose two.)
- A. Use the `reports` section to declare a **report group** for the unit test results.
- B. Use `env/variables` (**plaintext**) to embed the DB password.
- C. Use the `cache` section (S3/local backend) to keep `Maven` dependencies between builds.
- D. Add a `deploy` phase so CodeBuild deploys the artifact itself.
- E. `buildspec.yml` must be placed in the `.aws/` directory for CodeBuild to recognize it.

### Question 12 — `[D4.1 · DynamoDB · Single]`
A DynamoDB table in **provisioned** mode occasionally throws `ProvisionedThroughputExceededException` **even though total capacity has plenty of headroom**. Investigation shows traffic is **concentrated on a single item** (a "celebrity" item). What is the correct root-cause diagnosis and remediation?
- A. The table is **short on total capacity** → double the RCU/WCU.
- B. **Missing a GSI** → add a GSI to increase total throughput.
- C. **Hot partition** — traffic is concentrated on one partition key; remediate with **write sharding** / use **DAX** to cache the hot item, plus **exponential backoff**.
- D. **Wrong consistency** → switch all reads to eventual consistency.

### Question 13 — `[D1.3 · API Gateway · Single]`
A **Regional REST API** in API Gateway calls a Lambda function that aggregates a report, taking up to **~90 seconds**. Requests currently fail with a timeout at **29s**. Which solution requires the **LEAST architectural change** while still returning the result **synchronously**?
- A. Increase the integration timeout of the **Regional REST API** up to **300s** via Service Quotas (applies to Regional/private REST; does **NOT** apply to edge-optimized REST & HTTP API).
- B. It is impossible to exceed 29s; you **must** switch to async (return `202` + polling).
- C. Enable API Gateway caching with a 300s TTL to return results faster.
- D. Switch to **HTTP API** to raise the integration timeout to 300s.

### Question 14 — `[D2.1 · Cognito · Single]`
A mobile app has users sign in with **Google**, after which the app must **upload files directly to Amazon S3 from the device** using **AWS credentials** scoped by an IAM role. Which configuration is correct?
- A. Use only a Cognito user pool; take the **JWT access token** and call S3 directly.
- B. Use only a Cognito identity pool; it authenticates Google itself and issues a JWT.
- C. Use a **Lambda authorizer** to issue AWS credentials to the client.
- D. Authenticate through Google (Cognito user pool or federation) → the Cognito identity pool **exchanges the token for temporary AWS credentials** (via STS) mapped to an IAM role that allows `s3:PutObject`.

### Question 15 — `[D3.4 · CloudFormation · Multi — Choose 2]`
Stack A creates a shared VPC/Security Group; Stack B (the app) must **reference** those resources. In addition, the team needs to **prevent accidental deletion** of a stateful resource when the stack is deleted. Which two statements are **correct**? (Choose two.)
- A. `Fn::ImportValue` works **even when** the value has not been `Export`ed.
- B. **Nested stacks** are the **ONLY** way to share resources between stacks.
- C. In Stack A, declare `Outputs` with `Export`; in Stack B, use `Fn::ImportValue` to reference them.
- D. Set `DependsOn` between **two separate stacks** to share values.
- E. Set `DeletionPolicy: Retain` on the stateful resource so it is **not deleted** when the stack is deleted.

### Question 16 — `[D1.1 · Step Functions · Single]`
An order-processing workflow needs: **conditional branching**, **retry + backoff** per step, **catch** to run compensation, may run for **up to several hours**, and requires **exactly-once** execution. Which service and type are the MOST appropriate?
- A. AWS Step Functions **Express** workflow because it is cheap and fast for multi-hour tasks.
- B. AWS Step Functions **Standard** workflow (ASL) with `Choice` + `Retry`/`Catch`; **exactly-once**, runs up to **1 year**.
- C. A chain of Lambda functions invoking each other directly, with `SQS` inserted between steps.
- D. An EventBridge scheduled rule to run each step in turn.

### Question 17 — `[D4.3 · Lambda · Multi — Choose 2]`
A **CPU-bound** image-processing Lambda function runs slowly and has a **high cost per invocation**. Which two measures are the MOST effective optimizations? (Choose two.)
- A. Increase **memory** (which also increases CPU/network) to the "sweet spot" — for CPU-bound workloads this typically **reduces both duration and cost**.
- B. Use **AWS Lambda Power Tuning** (a Step Functions state machine) to find the memory configuration with the best cost/performance.
- C. Reduce memory to **128 MB** to lower the price per ms.
- D. Enable **provisioned concurrency** to speed up CPU processing.
- E. Switch to **asynchronous invocation** to run faster.

### Question 18 — `[D2.2 · S3 · Single]`
A compliance requirement: **every new object** must be encrypted at rest, there must be an **audit trail for each key use** (via CloudTrail), and the key must have **rotation**; with the least code change. Which solution is correct?
- A. You must use **client-side encryption** because S3 does **not** encrypt by default.
- B. Use **SSE-C** to manage the key yourself and audit it.
- C. Use **SSE-KMS** with a **customer managed key** (each key use is logged in CloudTrail, with automatic rotation enabled); S3 encrypts every new object automatically.
- D. Use **SSE-S3** because it allows auditing each key use and custom rotation.

### Question 19 — `[D1.2 · Lambda · Multi — Choose 2]`
Regarding **event source mapping (ESM)** for `SQS → Lambda` and `DynamoDB Streams → Lambda`, which two statements are **correct**? (Choose two.)
- A. For SQS, the ESM is a **push** model from SQS to Lambda.
- B. For SQS, Lambda **polls** the queue via the ESM; if the whole batch fails, the message returns to the queue after the visibility timeout, and past `maxReceiveCount` it moves to the **queue's DLQ**.
- C. The ESM only supports synchronous invocation with a 6 MB asynchronous payload.
- D. For DynamoDB Streams/Kinesis, the ESM reads **by shard, preserving order within the shard**; a failing record can **block the shard** (poison) → configure `BisectBatchOnFunctionError`/`MaximumRetryAttempts`/on-failure destination.
- E. The DLQ for DynamoDB Streams is configured on a source SQS queue.

### Question 20 — `[D3.4 · API Gateway · Single]`
There is only **one** REST API, and the team wants the `dev` stage and the `prod` stage to each point to a **different Lambda alias** **without modifying the API**. Which is the correct approach?
- A. Use a **stage variable** (e.g. `${stageVariables.lambdaAlias}`) in the Lambda integration URI; set each stage's value to the corresponding alias (`dev`/`prod`).
- B. Create **2 separate APIs** for dev and prod.
- C. Use a **usage plan + API key** to separate the environments.
- D. Set a different Lambda **environment variable** for each stage.

### Question 21 — `[D2.1 · IAM · Single]`
A Lambda function's execution role has an identity policy that **Allows** `s3:*` on a bucket. But another policy (an SCP or a bucket policy) has an **explicit Deny** for `s3:DeleteObject`. What is the effective permission for `DeleteObject`?
- A. **Allowed**, because the identity policy already allows `s3:*`.
- B. **Denied** — an explicit `Deny` always wins over an explicit `Allow`.
- C. It depends on the **order** of the statements in the policy.
- D. Allowed **if** the request uses MFA.

### Question 22 — `[D4.2 · CloudWatch · Single]`
A Lambda function needs to emit a **high-cardinality business metric** (order count per merchant) **without** adding latency/cost from synchronous `PutMetricData` calls. Which is the best approach?
- A. Call `PutMetricData` synchronously in every request.
- B. Enable **detailed monitoring** on the Lambda function.
- C. Use an **X-Ray annotation** as the metric.
- D. Write logs in the **Embedded Metric Format (EMF)** → CloudWatch extracts metrics from the logs automatically, without synchronous `PutMetricData` calls.

### Question 23 — `[D1.3 · DynamoDB · Multi — Choose 2]`
An existing table (partition key = `userId`) now needs a query pattern **by `email`** — a need that arose **after** the table was created, and that does **not** require strongly consistent reads. Which two statements are **correct**? (Choose two.)
- A. Use a **GSI** (partition key = `email`) — it **can be created after the table exists**, has its own throughput, and is **eventually consistent only**.
- B. A **GSI** supports strongly consistent reads if you set `ConsistentRead=true`.
- C. An **LSI** must be created **at table creation time** and **shares the partition key** → not suitable for querying by `email` on an existing table.
- D. An **LSI** uses its **own** throughput and can be created **at any time**.
- E. A `Query` on a GSI returns at most **4 MB** per call.

### Question 24 — `[D3.2 · SAM · Single]`
A developer wants to **test the Lambda function + API locally** before deploying, and to **mock** an API Gateway event. Which command is correct?
- A. `sam deploy --guided`, then test in the cloud.
- B. `sam build` is enough to run the endpoint locally.
- C. `sam local start-api` (stands up a local API Gateway) and/or `sam local invoke -e event.json` to test with a mock event.
- D. `sam sync` to run unit tests locally.

### Question 25 — `[D2.2 · KMS · Multi — Choose 2]`
A security team needs to: (1) **rotate a CMK more frequently than yearly** and **rotate immediately** on suspected exposure, and (2) **encrypt/decrypt data in multiple regions** with the same key material. Which two statements are **correct**? (Choose two.)
- A. A CMK's automatic rotation is **fixed at 90 days** and cannot be changed.
- B. A CMK supports a **custom rotation period** and **on-demand rotation** (rotate immediately on suspected exposure).
- C. You can `Encrypt` up to **4 MB** of data directly.
- D. **AWS managed keys** let you write your own key policy and rotate on demand.
- E. Use **multi-Region KMS keys** to encrypt/decrypt with the same key material across multiple regions.
