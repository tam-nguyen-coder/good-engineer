# 📝 Practice Questions — Week 1: Developer Foundations — AWS SDK/CLI + Lambda Basics

> **36 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Week 1 material.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D1.1 · SDK/CLI · Single]`
A developer runs an application on a laptop. The current shell has exported both `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, and the file `~/.aws/credentials` also contains a `[default]` profile with a **different set of keys**. The code initializes the client **without** passing credentials explicitly. Which credentials will the SDK use?
- A. The keys in `~/.aws/credentials`, because credentials stored in a file are more durable than environment variables.
- B. The environment variables, because in the credential provider chain environment variables are evaluated **before** the shared credentials file.
- C. The SDK returns an error because it detects a credentials conflict.
- D. The SDK merges both and selects the keys with the lower access key ID in alphabetical order.

### Question 2 — `[D1.1 · SDK/CLI · Single]`
An application running on an Amazon EC2 instance needs to call Amazon S3. A security policy requires that **no long-term keys** be stored on the instance or in the code. Which approach is the **MOST secure and recommended**?
- A. Create an IAM user, generate an access key, and store it in `~/.aws/credentials` on the instance.
- B. Hard-code the access key in the application config file and then encrypt that file.
- C. Attach an IAM role to the EC2 instance (instance profile); the SDK automatically retrieves temporary credentials through IMDS.
- D. Pass the access key into the instance user data as environment variables.

### Question 3 — `[D1.1 · SDK/CLI · Multi — Choose 2]`
Which **2** statements about the AWS SDK/CLI credential provider chain are TRUE? (Choose two.)
- A. Credential values set directly in code (client parameters) have the **highest** precedence.
- B. The chain scans every source and uses the **last** valid source it finds.
- C. When valid credentials are found, the search **stops** immediately at that source.
- D. The shared `credentials` file is always checked **before** environment variables.
- E. The SDK requires manual code to refresh temporary credentials before they expire.

### Question 4 — `[D1.1 · SDK/CLI · Single]`
A developer adds a named profile `dev`. In `~/.aws/config` and `~/.aws/credentials`, how must the section header be written to be correct?
- A. `[profile dev]` in both files.
- B. `[dev]` in both files.
- C. `[profile dev]` in `~/.aws/config` and `[dev]` in `~/.aws/credentials`.
- D. `[dev]` in `~/.aws/config` and `[profile dev]` in `~/.aws/credentials`.

### Question 5 — `[D1.1 · SDK/CLI · Multi — Choose 2]`
Which **2** statements about the AWS CLI `config` and `credentials` files are TRUE? (Choose two.)
- A. `aws configure` writes sensitive keys to `~/.aws/credentials`, and settings such as region/output to `~/.aws/config`.
- B. When a profile has credentials in **both** files, the value in `~/.aws/config` takes precedence.
- C. When a profile has credentials in **both** files, the value in `~/.aws/credentials` takes precedence.
- D. A named profile must be written as `[profile dev]` in the `credentials` file and `[dev]` in the `config` file.
- E. Credentials can never be read from `~/.aws/config`.

### Question 6 — `[D1.1 · SDK/CLI · Single]`
A command runs with the flag `--region us-east-1`. At the same time the variable `AWS_REGION=eu-west-1` is exported, and the profile in use in `~/.aws/config` has `region=ap-southeast-1`. Which Region will the command use?
- A. `ap-southeast-1` (the region in the profile config).
- B. `eu-west-1` (the environment variable).
- C. `us-east-1` (the command-line flag).
- D. The command fails because three Regions conflict.

### Question 7 — `[D1.1 · SDK/CLI · Single]`
The variable `AWS_PROFILE=prod` is exported, but the developer runs `aws s3 ls --profile dev`. Which profile does the command use?
- A. `prod`, because an environment variable always overrides a command-line option.
- B. `dev`, because the `--profile` flag overrides `AWS_PROFILE`.
- C. `default`, because two profiles are being specified at the same time.
- D. Both — the command runs twice.

### Question 8 — `[D1.1 · SDK/CLI · Single]`
A script calls a `list`-type API and processes the results, but it consistently **misses** some records that actually exist in the account. The response contains a `NextToken` field. What is the correct fix?
- A. Increase the client socket timeout.
- B. Retry the API call with exponential backoff.
- C. Use the SDK **paginator** (or loop on `NextToken`) to iterate through all pages.
- D. Change the output format to `text`.

### Question 9 — `[D1.1 · SDK/CLI · Single]`
After creating an Amazon DynamoDB table, the code writes data immediately and occasionally fails because the table is still in the `CREATING` state. What is the **standard** way to block until the table is `ACTIVE`?
- A. Add a fixed `sleep(30)` before writing.
- B. Use an SDK **waiter** (such as "table exists/active") to poll until the desired state is reached.
- C. Catch the error and exit the program.
- D. Enable the `adaptive` retry mode.

### Question 10 — `[D1.1 · SDK/CLI · Single]`
Why does the SDK add **jitter** (randomness) on top of exponential backoff when retrying failed requests?
- A. To guarantee that a request always succeeds on the second attempt.
- B. To spread retries out over time, avoiding the **thundering herd** problem (many clients retrying at the same instant).
- C. To reduce the payload size of each request.
- D. To encrypt retry traffic.

### Question 11 — `[D1.1 · SDK/CLI · Multi — Choose 2]`
An SDK client uses the `standard` retry mode. Which **2** error types will the SDK **retry automatically**? (Choose two.)
- A. `ThrottlingException` (throttling).
- B. `ValidationException` (invalid parameters).
- C. `AccessDeniedException`.
- D. HTTP 500 `InternalError` (a transient server error).
- E. `ResourceNotFoundException`.

### Question 12 — `[D1.1 · SDK/CLI · Single]`
A batch job uses **one** SDK client targeting **a single DynamoDB table** and is frequently throttled. The workload tolerates added latency, and you want the client to **automatically slow down its send rate** when throttled. Which retry mode is the best fit?
- A. `legacy`.
- B. `standard`.
- C. `adaptive`.
- D. Disable retries (max attempts = 1).

### Question 13 — `[D1.1 · SDK/CLI · Single]`
A single SDK client sends requests to **multiple services and multiple tenants**. You need **predictable latency** on the first request and you do **not** want throttling on one resource to slow down unrelated requests. Which retry mode should you use?
- A. `adaptive`, so that all requests share one rate limiter.
- B. `standard`, the recommended default mode that does **not** delay the first request.
- C. `legacy`, for maximum compatibility.
- D. A custom mode with retries disabled.

### Question 14 — `[D1.1 · SDK/CLI · Single]`
With the SDK/CLI retry configuration, how do you **completely disable** automatic retries (only the first request, no retries)?
- A. Set `max_attempts` to `0`.
- B. Set `max_attempts` to `1` (the first call is **counted** in this value).
- C. Set `retry_mode` to `legacy`.
- D. Remove the `region` setting.

### Question 15 — `[D1.1 · SDK/CLI · Single]`
A payment service calls a "create order" API. When throttling causes the SDK to retry, it sometimes **creates duplicate orders**. What is the **BEST** way to retry safely **without** turning off retries?
- A. Set the retry mode to `legacy`.
- B. Make the operation **idempotent** using a unique **client request token** (idempotency key).
- C. Increase the function timeout.
- D. Catch the exception and ignore it.

### Question 16 — `[D1.2 · Lambda · Single]`
In an AWS Lambda handler `handler(event, context)`, which object provides `awsRequestId`, the remaining execution time, and the function name/version?
- A. `event`.
- B. `context`.
- C. The environment variables.
- D. The resource-based policy.

### Question 17 — `[D1.2 · Lambda · Single]`
A team must run a function written in a language for which Lambda does **not** provide a managed runtime. Which approach lets them run it with the **LEAST** platform change?
- A. Rewrite the code in Python because it is the only supported language.
- B. Use a **custom runtime** that implements the **Lambda Runtime API** (packaged in a layer or a container image).
- C. It is not possible; they must switch to EC2.
- D. Enable Provisioned Concurrency.

### Question 18 — `[D1.2 · Lambda · Multi — Choose 2]`
Which **2** are valid ways to package and deploy the code of a Lambda function? (Choose two.)
- A. Upload a `.zip` archive through the console, CLI, or SDK.
- B. Provide a **container image**.
- C. Point the function at a Git branch so that Lambda pulls it on every invocation.
- D. Paste the code directly into a DynamoDB item.
- E. Upload an AMI.

### Question 19 — `[D1.2 · Lambda · Multi — Choose 2]`
A developer needs to **invoke** an existing Lambda function for testing and from application code. Which **2** are valid ways to invoke the function? (Choose two.)
- A. Run `aws lambda invoke --function-name <name> --payload ... out.json` from the CLI.
- B. Call the `Invoke` API through the AWS SDK (for example `InvokeCommand`).
- C. SSH into the function's underlying host and run the binary directly.
- D. Write the payload to the function's DynamoDB table.
- E. Edit `~/.aws/config` to trigger execution.

### Question 20 — `[D1.2 · Lambda · Multi — Choose 2]`
An Amazon S3 bucket needs to **invoke** a Lambda function, and that same function needs to **read objects** from a different S3 bucket. Which **2** configurations are required? (Choose two.)
- A. Add a **resource-based policy** on the function that allows the principal `s3.amazonaws.com` to perform `lambda:InvokeFunction`.
- B. Grant `s3:GetObject` on the source bucket in the function's **execution role**.
- C. Add `lambda:InvokeFunction` to the function's **execution role**.
- D. Attach an IAM user policy to the bucket.
- E. Add S3 read permission to the function's **resource-based policy**.

### Question 21 — `[D1.2 · Lambda · Single]`
A function runs successfully (it returns a valid response) but **nothing appears** in CloudWatch Logs, and the log group `/aws/lambda/<name>` is not created either. What is the **MOST likely** cause?
- A. The code forgot to call a logging library.
- B. The **execution role** is missing the `logs:CreateLogGroup/CreateLogStream/PutLogEvents` permissions (for example `AWSLambdaBasicExecutionRole` is not attached).
- C. CloudTrail is turned off.
- D. The function timeout is set too high.

### Question 22 — `[D1.2 · Lambda · Single]`
For Lambda to **assume** the function's execution role at invocation, what **MUST** the role's trust policy contain?
- A. The managed policy `AWSLambdaBasicExecutionRole`.
- B. A statement that allows the service principal `lambda.amazonaws.com` to perform `sts:AssumeRole`.
- C. A resource-based policy that grants `lambda:InvokeFunction`.
- D. The developer's IAM user as the principal.

---

## Part 2 — Lambda integration & invocation models

> These scenarios drill the three ways AWS services trigger Lambda — **synchronous**, **asynchronous (event)**, and **event source mapping (poll-based)** — plus per-model error handling, scaling, event filtering, and batching. The recurring exam trap is knowing *which service uses which model* and *who owns the retry*.

### Question 23 — `[D1.1 · Lambda-Integration · Single]`
A developer configures an Amazon S3 bucket to send `s3:ObjectCreated:*` events to a Lambda function. A teammate claims this works like an Amazon SQS trigger, where Lambda continuously **polls** S3 for new events. Which statement **CORRECTLY** describes how S3 invokes the function?
- A. S3 uses an event source mapping; Lambda polls the bucket in batches and invokes the function.
- B. S3 invokes the function **asynchronously** (event mode): S3 hands the event to Lambda's internal queue, gets an immediate acknowledgement, and Lambda owns the retry behavior.
- C. S3 invokes the function **synchronously** and waits for the response before it finishes writing the object.
- D. S3 keeps an open WebSocket connection to the function and streams events over it.

### Question 24 — `[D1.2 · Lambda-Integration · Single]`
An Amazon SQS standard queue is configured as a trigger for a Lambda function. During an incident review, an engineer states that "SQS pushes each message to Lambda as soon as it arrives." Which statement is **ACTUALLY** correct about this integration?
- A. Lambda's **event source mapping polls** the queue, reads messages in batches, and invokes the function; SQS never pushes to Lambda.
- B. SQS invokes the function **asynchronously** and retries the event twice on failure.
- C. SQS holds an open connection and streams messages to the function in real time.
- D. The function code must call `ReceiveMessage` itself inside the handler; Lambda does not manage polling.

### Question 25 — `[D1.2 · Lambda-Integration · Single]`
An Amazon SNS topic invokes a Lambda function. Under sustained load a small percentage of invocations throw an unhandled exception. **No** on-failure destination or DLQ is configured on the function. What does Lambda do **BY DEFAULT** with a failed event?
- A. It immediately drops the event with no retry, because SNS is a fire-and-forget publisher.
- B. It returns the exception synchronously to SNS, which then retries according to its own delivery policy.
- C. It retries the event **up to two more times** (asynchronous invocation) and — because no on-failure destination or DLQ is set — the event is eventually discarded after the retries are exhausted.
- D. It places the failed event back on the SNS topic so a different subscriber can process it.

### Question 26 — `[D1.1 · Lambda-Integration · Multi — Choose 2]`
Which **2** event sources invoke a Lambda function using the **asynchronous (event)** invocation model? (Choose two.)
- A. Amazon S3 event notifications.
- B. Amazon API Gateway REST API (Lambda proxy integration).
- C. Amazon SNS.
- D. Amazon SQS.
- E. Amazon Kinesis Data Streams.

### Question 27 — `[D1.1 · Lambda-Integration · Multi — Choose 2]`
Which **2** event sources rely on an **event source mapping (poll-based)** in which Lambda reads the source and invokes the function in **batches**? (Choose two.)
- A. Amazon EventBridge (scheduled rule).
- B. Amazon DynamoDB Streams.
- C. Amazon SQS FIFO queue.
- D. Amazon SNS.
- E. Application Load Balancer (ALB).

### Question 28 — `[D1.2 · Lambda-Integration · Single]`
A Lambda function is exposed through an Amazon API Gateway REST API using **Lambda proxy integration**. Occasionally the function throws a transient error. The team is surprised that Lambda does **not** automatically retry these invocations. Which statement **BEST** explains the behavior and the correct remediation?
- A. API Gateway invokes Lambda **synchronously**; Lambda does not retry synchronous invocations, so the **client (caller)** must implement retry with backoff.
- B. API Gateway invokes Lambda asynchronously; add an on-failure destination to capture and replay the retries.
- C. Lambda always retries twice regardless of invocation type, so the retries are happening but failing silently.
- D. Enable an event source mapping on the API Gateway stage so Lambda retries the failed batch.

### Question 29 — `[D4.1 · Lambda-Integration · Single]`
A Lambda function processes records from an Amazon Kinesis Data Stream. Over the past hour the function's **`IteratorAge`** metric has been climbing steadily while the incoming record rate is unchanged. What does a **HIGH and rising** `IteratorAge` most likely indicate?
- A. The function is throwing permission errors and cannot read the stream.
- B. The function is **falling behind** — it is processing records more slowly than they arrive, so unprocessed records keep getting older.
- C. The stream has too few records, so Lambda is idling between polls.
- D. The execution role's temporary credentials are about to expire.

### Question 30 — `[D4.1 · Lambda-Integration · Multi — Choose 2]`
A Lambda function reads from an Amazon DynamoDB stream. One malformed ("poison") record repeatedly fails; because stream records are processed **in order within a shard**, the **entire shard stops making progress** and `IteratorAge` grows. Which **2** event source mapping settings let the shard make progress **WITHOUT** blocking indefinitely on the bad record? (Choose two.)
- A. Enable **bisect batch on function error** so Lambda splits the failing batch and isolates the bad record.
- B. Configure an **on-failure destination** together with a **maximum retry attempts** or **maximum record age** limit so the bad record is eventually sent aside.
- C. Increase the function's memory to 10,240 MB.
- D. Switch the function to asynchronous invocation.
- E. Enable Provisioned Concurrency on the function.

### Question 31 — `[D1.2 · Lambda-Integration · Single]`
A Lambda function is triggered by an Amazon SQS standard queue. Some messages are being **processed more than once**: they reappear in the queue and are picked up again **before** the function finishes handling them. The function timeout is 60 seconds. What is the **recommended** fix?
- A. Reduce the batch size to 1.
- B. Set the queue's **visibility timeout to at least 6× the function timeout** (for example, 360 seconds) so a message stays hidden long enough to finish processing.
- C. Enable long polling on the queue.
- D. Increase the function's reserved concurrency.

### Question 32 — `[D1.2 · Lambda-Integration · Single]`
A Lambda function receives batches of 10 messages from an Amazon SQS queue. When a **single** message in a batch fails, the **whole batch** returns to the queue and all 10 messages are reprocessed, duplicating work for the 9 that already succeeded. What is the correct way to return **ONLY** the failed messages for retry?
- A. Set the batch size to 1 so every message is its own batch.
- B. Enable **partial batch response** (`ReportBatchItemFailures`) and return the IDs of only the failed messages in the function's response.
- C. Call `DeleteMessage` for each successful message from inside the handler.
- D. Move the function to asynchronous invocation with a DLQ.

### Question 33 — `[D1.2 · Lambda-Integration · Single]`
A Lambda function is triggered by an Amazon SQS queue. Messages that fail repeatedly must be moved off the main queue so they can be inspected later without blocking healthy traffic. **Where** is the **dead-letter queue** configured for this event source?
- A. On the Lambda function's asynchronous **on-failure destination** setting.
- B. On the **SQS source queue** itself, via a redrive policy with `maxReceiveCount` that points to a separate DLQ.
- C. In the function's execution role.
- D. On the event source mapping's `ReportBatchItemFailures` flag.

### Question 34 — `[D1.2 · Lambda-Integration · Single]`
A Lambda function is triggered by a DynamoDB stream, but only `INSERT` events are relevant. Today the function is invoked for every `INSERT`, `MODIFY`, and `REMOVE` change and simply returns early for the ones it does not care about — wasting invocations and cost. What is the **MOST efficient** way to invoke the function only for the relevant records?
- A. Add **filter criteria (event filtering)** to the event source mapping so Lambda invokes the function only for records that match the pattern.
- B. Add an `if` check at the top of the handler and return early for the rest.
- C. Increase the batch window so unrelated records are dropped.
- D. Create a separate stream for each event type.

### Question 35 — `[D1.2 · Lambda-Integration · Single]`
An order-processing Lambda function is triggered by an Amazon **SQS FIFO** queue and must preserve the order of messages **within each customer**. How does the Lambda event source mapping process and scale for a FIFO queue?
- A. It processes messages **in order within each message group**, handling one batch per group at a time; concurrency scales with the number of **active message groups**.
- B. It processes all messages in a single-threaded loop across the whole queue, so throughput is fixed at one message at a time.
- C. It ignores the message group ID and processes messages fully in parallel for maximum throughput.
- D. It requires Provisioned Concurrency to guarantee ordering.

### Question 36 — `[D1.1 · Lambda-Integration · Multi — Choose 2]`
An architect must choose between wiring **SNS → Lambda** and **SQS → Lambda** for a workload where downstream failures are common and **no events may be lost** during a Lambda outage. Which **2** statements are TRUE and relevant to this decision? (Choose two.)
- A. **SNS invokes Lambda asynchronously (push)**; if the async retries are exhausted and no on-failure destination/DLQ is configured, the event is lost.
- B. **SQS + Lambda uses polling**, so messages stay buffered in the queue (up to the retention period) and are retried after the visibility timeout, giving stronger durability during a Lambda outage.
- C. SNS guarantees exactly-once, in-order delivery to Lambda, which makes a queue unnecessary.
- D. With SQS, Lambda pushes messages back to the producer when it is overloaded.
- E. SNS → Lambda automatically retains undelivered events for 14 days with no extra configuration.
