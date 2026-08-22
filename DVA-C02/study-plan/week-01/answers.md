# ✅ Answers & Explanations — Week 1

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key — Part 1 (Q1–Q22):** 1-B · 2-C · 3-AC · 4-C · 5-AC · 6-C · 7-B · 8-C · 9-B · 10-B · 11-AD · 12-C · 13-B · 14-B · 15-B · 16-B · 17-B · 18-AB · 19-AB · 20-AB · 21-B · 22-B

**Answer key — Part 2 (Q23–Q36):** 23-B · 24-A · 25-C · 26-AC · 27-BC · 28-A · 29-B · 30-AB · 31-B · 32-B · 33-B · 34-A · 35-A · 36-AB

---

### Question 1 — Answer: **B**
- **Why correct:** In the credential provider chain, **environment variables** are evaluated **before** the shared `credentials` file. Once the chain finds valid credentials in the environment variables, it **stops immediately** and never reads the profile file.
- **Why the others are wrong:** A — "more durable" is not a criterion; the chain order is what decides. C — there is no conflict; the chain simply stops at the first valid source. D — the SDK does not merge credentials or compare access keys alphabetically.
- 🧠 **Key point / trap:** "Env var set AND a profile exists" → the **env var wins**. This is a classic DVA trap.
- 📎 Source: `resources/sdk-credential-provider-chain.md`; README "Credential provider chain".

### Question 2 — Answer: **C**
- **Why correct:** Code running on AWS should use an **IAM role**. EC2 retrieves the role's temporary credentials through **IMDS** (instance profile) — no long-term key sits on the instance or in the code, and the SDK renews them automatically on expiry.
- **Why the others are wrong:** A — this is still a long-term key stored on disk (violates the requirement). B — hard-coding a key is an anti-pattern; encrypting the file does not save you if the key leaks and it is hard to rotate. D — a key in user data is still a long-term credential, readable and not rotated.
- 🧠 **Key point / trap:** "Code on EC2/ECS/Lambda calling a service" → **attach an IAM role**, never hard-code a key.
- 📎 Source: `resources/sdk-credential-provider-chain.md` (IMDS provider); README "⚠️ Common exam traps".

### Question 3 — Answer: **A, C**
- **Why correct:** A — "Setting values that are specified in code always take precedence." C — "After valid credentials are found, the search is stopped."
- **Why the others are wrong:** B — the chain stops at the **first** valid source, it does not use the last one. D — environment variables come **before** the shared credentials file, not the other way around. E — the SDK **renews** temporary credentials automatically; no extra code is needed.
- 🧠 **Key point / trap:** Remember two rules: "code > env > file" and "found → stop".
- 📎 Source: `resources/sdk-credential-provider-chain.md`.

### Question 4 — Answer: **C**
- **Why correct:** In `~/.aws/config`, a named profile is written as `[profile dev]`; in `~/.aws/credentials` it is written as just `[dev]` (WITHOUT the word `profile`). Only `[default]` is written the same in both files.
- **Why the others are wrong:** A/B — cannot be identical, because each file has its own convention. D — reverses the roles of the two files.
- 🧠 **Key point / trap:** `config` = has the word `profile`; `credentials` = does not. This is a very common trick question.
- 📎 Source: `resources/cli-config-credentials-files.md` (Section type: `profile`).

### Question 5 — Answer: **A, C**
- **Why correct:** A — `aws configure` writes sensitive keys to `credentials`, and region/output/settings to `config`. C — "If there are credentials in both files for a profile sharing the same name, the keys in the **credentials** file take precedence."
- **Why the others are wrong:** B — the opposite (credentials wins, not config). D — reverses the header convention of the two files. E — the CLI **can** read credentials from `config` too (AWS just recommends keeping them in `credentials`).
- 🧠 **Key point / trap:** Same key duplicated across the same profile → the **`credentials` file wins**.
- 📎 Source: `resources/cli-config-credentials-files.md` ("Storing credentials in the config file").

### Question 6 — Answer: **C**
- **Why correct:** Region precedence (high → low): the **`--region`** flag > the env var `AWS_REGION`/`AWS_DEFAULT_REGION` > the `region` in the profile in `~/.aws/config`. The command-line flag beats everything.
- **Why the others are wrong:** A — the profile config has the lowest precedence of the three sources. B — the env var is overridden by the flag. D — there is no conflict; precedence is well defined, no error.
- 🧠 **Key point / trap:** A command-line option is always at the top of precedence (region, profile, output, etc.).
- 📎 Source: `resources/cli-config-credentials-files.md` (`region` setting); README "AWS CLI — configuration & profiles".

### Question 7 — Answer: **B**
- **Why correct:** "To avoid specifying the profile in every command, set `AWS_PROFILE`. **You can override it with `--profile`.**" The command-line flag beats the environment variable.
- **Why the others are wrong:** A — reverses precedence (option > env). C — specifying `--profile dev` does not activate `default`. D — the command runs only once, using `dev`.
- 🧠 **Key point / trap:** `--profile` > `AWS_PROFILE`. Same precedence logic: "option > env > file".
- 📎 Source: `resources/cli-config-credentials-files.md` ("Using named profiles").

### Question 8 — Answer: **C**
- **Why correct:** A `NextToken` in the result means there are more **pages**. You must use a **paginator** (or manually loop on `NextToken`/`Marker`) to iterate through everything — otherwise you only get the first page and miss data.
- **Why the others are wrong:** A/B — this is not a timeout or a transient error; retrying does not fetch more pages. D — changing the output format does not affect the number of records returned.
- 🧠 **Key point / trap:** "List returns too few / has a `NextToken`" → **pagination**, not an API bug.
- 📎 Source: README "AWS SDK — using it correctly" (Pagination); "🔁 Quick reflexes".

### Question 9 — Answer: **B**
- **Why correct:** A **waiter** is the SDK's standard way to poll until a resource reaches the desired state (for example a DynamoDB table `ACTIVE`, or a Lambda function ready), instead of writing your own `sleep` loop.
- **Why the others are wrong:** A — a fixed `sleep` is both wasteful (waiting too long) and risky (waiting too little). C — exiting the program does not meet the requirement. D — `adaptive` only helps when you are **throttled**; a "not yet `ACTIVE`" error is not throttling, so a retry mode does not help.
- 🧠 **Key point / trap:** "Wait for a resource to reach the ready/active state" → **waiter**.
- 📎 Source: README "AWS SDK — using it correctly" (Waiters); "🔁 Quick reflexes".

### Question 10 — Answer: **B**
- **Why correct:** Jitter = a random multiplier (full jitter) applied to the backoff delay → it **spreads** retries out over time. Without jitter, all clients that failed at the same moment retry at the same moment, creating a burst that knocks the service down again — that is the **thundering herd**.
- **Why the others are wrong:** A — nothing "guarantees" success on the second attempt. C — jitter does not touch the payload. D — jitter has nothing to do with encryption.
- 🧠 **Key point / trap:** Backoff = exponential spacing; **jitter = avoid the thundering herd**. Formula: `delay = random(0,1) × min(20s, base × 2^retry)`.
- 📎 Source: `resources/sdk-retry-behavior.md` ("Why jitter matters").

### Question 11 — Answer: **A, D**
- **Why correct:** A — throttling errors (`ThrottlingException`, base delay 1,000 ms) are **retryable**. D — transient errors including HTTP 500/`InternalError` (base delay 50 ms) are also **retryable**.
- **Why the others are wrong:** B `ValidationException`, C `AccessDeniedException`, E `ResourceNotFoundException` — all **non-retryable**: the SDK returns immediately and retrying is pointless (bad parameters / missing permission / not existing will still fail on retry).
- 🧠 **Key point / trap:** Retry **throttling + transient 5xx**; do not retry 4xx client errors (validation/access denied/not found).
- 📎 Source: `resources/sdk-retry-behavior.md` ("Which errors are retried").

### Question 12 — Answer: **C**
- **Why correct:** `adaptive` = `standard` + a client-side rate limiter that **automatically slows the send rate** when throttled. It fits this exact scenario: **one** client targeting a **single resource**, heavy throttling, tolerant of added latency.
- **Why the others are wrong:** A `legacy` — for backward compatibility only, no standardized rate limiter. B `standard` — retries + backoff but does **not** self-throttle the send rate. D — disabling retries makes the throttling situation worse.
- 🧠 **Key point / trap:** `adaptive` is for **single-resource, throttling-heavy, latency-tolerant**. It may delay even the first request.
- 📎 Source: `resources/sdk-retry-behavior.md` ("Adaptive mode" — When to use).

### Question 13 — Answer: **B**
- **Why correct:** `standard` is the **default and recommended** mode for most workloads; the retry quota does **not** delay the first request → predictable latency. `adaptive` is **not** a fit when one client serves many resources/tenants.
- **Why the others are wrong:** A — `adaptive` shares one rate limiter across the whole client → throttling on one resource slows **every** other request; it can also delay the first request. C — `legacy` is for backward compatibility only. D — disabling retries loses tolerance to transient errors.
- 🧠 **Key point / trap:** "Multi-resource / multi-tenant + need stable latency" → **standard** (do not use adaptive).
- 📎 Source: `resources/sdk-retry-behavior.md` ("Adaptive mode" — When NOT to use; recommendation table).

### Question 14 — Answer: **B**
- **Why correct:** `max_attempts` **counts the first call**. Setting it to `1` means only 1 request, **0 retries** → retries fully disabled.
- **Why the others are wrong:** A — `0` is not a valid value for "call only once" (the minimum valid value is 1). C — `legacy` still retries, just differently. D — removing `region` has nothing to do with retries (and would cause a missing-region error).
- 🧠 **Key point / trap:** `max_attempts = 3` = 1 initial call + 2 retries; to **disable** → set it to `1`.
- 📎 Source: `resources/sdk-retry-behavior.md` ("Retry settings"); `resources/cli-config-credentials-files.md` (`max_attempts`).

### Question 15 — Answer: **B**
- **Why correct:** **Idempotency** (a client request token / unique key) ensures that calling the same operation multiple times has the same effect as calling it once → retries are safe and do not create duplicate orders. This is the correct design when you still want to keep retries.
- **Why the others are wrong:** A — changing the retry mode does not prevent duplicates. C — a timeout is unrelated to duplication. D — "catch and ignore" hides the error and may still create duplicates.
- 🧠 **Key point / trap:** "Retries create duplicate records" → **idempotency (client token)**, do not disable retries.
- 📎 Source: README "Retry & resilience" (Idempotency); "⚠️ Common exam traps".

### Question 16 — Answer: **B**
- **Why correct:** `context` carries runtime information: `awsRequestId`, remaining time, function name/version, log group/stream. `event` only contains the input data of the invocation.
- **Why the others are wrong:** A `event` — is the triggering payload/event, not runtime metadata. C — environment variables are static config and have no request ID. D — a resource-based policy is about permissions, not an object passed to the handler.
- 🧠 **Key point / trap:** `event` = input data; `context` = runtime metadata (requestId, remaining time, etc.).
- 📎 Source: `resources/lambda-programming-model.md`; README "Lambda basics — dissecting the handler".

### Question 17 — Answer: **B**
- **Why correct:** Lambda provides a **Runtime API** that lets you use **any language** through a **custom runtime** (packaged in a layer or a container image) — the least rewriting required.
- **Why the others are wrong:** A — Python is not the only language (native runtimes include Java, Go, PowerShell, Node.js, C#, Python, Ruby). C — no need to switch to EC2. D — Provisioned Concurrency reduces cold starts and has nothing to do with language support.
- 🧠 **Key point / trap:** A language with no managed runtime → **Runtime API / custom runtime**.
- 📎 Source: `resources/lambda-faqs.md` ("What languages does AWS Lambda support?").

### Question 18 — Answer: **A, B**
- **Why correct:** Lambda deploys code as a **`.zip` archive** (uploaded through console/CLI/SDK) or as a **container image** — both use the same execution environment.
- **Why the others are wrong:** C — Lambda does not auto-pull from a Git branch on every invocation. D — you do not paste code into DynamoDB. E — an AMI is for EC2, not Lambda.
- 🧠 **Key point / trap:** Two packaging types: **ZIP** and **container image**. (Note: Code Signing applies only to ZIP.)
- 📎 Source: `resources/lambda-faqs.md` ("How can I deploy my Lambda functions?").

### Question 19 — Answer: **A, B**
- **Why correct:** Valid invocation methods include: the **CLI** `aws lambda invoke ...` (remember `--cli-binary-format raw-in-base64-out` when passing a JSON payload) and the **SDK** `Invoke` API (`InvokeCommand`). (Together with the Console, that gives the three standard create/invoke methods: Console/CLI/SDK.)
- **Why the others are wrong:** C — you do not SSH into the function's host (serverless, you do not manage the host). D — writing to DynamoDB does not invoke the function (unless a separate event source mapping exists — that is not a "direct invoke"). E — editing `~/.aws/config` only changes configuration, it does not trigger execution.
- 🧠 **Key point / trap:** Three standard methods: **Console, CLI (`aws lambda invoke`), SDK (`Invoke`)**.
- 📎 Source: `resources/lambda-faqs.md` ("How can my application trigger... invoke API"); README Session B (invoke steps via CLI & SDK).

### Question 20 — Answer: **A, B**
- **Why correct:** These are two different directions of permission:
  - A — Letting S3 **invoke** the function → use a **resource-based policy** (principal `s3.amazonaws.com`, action `lambda:InvokeFunction`). This is "who is allowed to invoke".
  - B — Letting the function **read S3** → grant `s3:GetObject` in the **execution role**. This is "what the function is allowed to call".
- **Why the others are wrong:** C — `lambda:InvokeFunction` does not belong in the execution role (it is the permission for *someone else* to invoke, not the function's permission to call out). D — you do not attach an IAM user policy to the bucket for this. E — the function's S3 read permission must live in the **execution role**, not the resource-based policy.
- 🧠 **Key point / trap:** **Resource-based policy = "who can invoke the function"**; **execution role = "who the function can call"**. This is a very common exam trap.
- 📎 Source: `resources/lambda-execution-role.md`; `resources/lambda-faqs.md` ("How do I control which S3 buckets can call which functions?"); README "Execution role vs Resource-based policy".

### Question 21 — Answer: **B**
- **Why correct:** Lambda **automatically** pushes stdout/stderr to CloudWatch Logs, but only when the **execution role has the** `logs:CreateLogGroup/CreateLogStream/PutLogEvents` permissions (contained in `AWSLambdaBasicExecutionRole`). Missing those permissions → the log group cannot be created and there are no logs even though the function runs fine.
- **Why the others are wrong:** A — no special library is needed; `console.log`/`print` is enough, logging is automatic. C — CloudTrail records API audit events, not the function's application logs. D — a high timeout does not block log writing.
- 🧠 **Key point / trap:** "Function runs but there are no logs" → **missing `logs:*` permission in the execution role**, not a code bug.
- 📎 Source: `resources/lambda-execution-role.md`; `resources/lambda-programming-model.md` (automatic logging); README "⚠️ Common exam traps".

### Question 22 — Answer: **B**
- **Why correct:** For Lambda to **assume** the execution role, the role's **trust policy** must declare the service principal **`lambda.amazonaws.com`** with the action `sts:AssumeRole`. Lambda assumes the role automatically at invocation (it does not call `sts:AssumeRole` in code).
- **Why the others are wrong:** A — `AWSLambdaBasicExecutionRole` is a **permissions policy** (what the function may do), not a trust policy (who may assume it). C — a resource-based policy with `lambda:InvokeFunction` governs "who can invoke the function", which is different from assuming a role. D — you do not set an IAM user as the principal for a service execution role.
- 🧠 **Key point / trap:** Trust policy = **who can assume the role** (here `lambda.amazonaws.com`); permissions policy = **what the role can do**.
- 📎 Source: `resources/lambda-execution-role.md` ("trust policy must specify the Lambda service principal").

---

## Part 2 — Lambda integration & invocation models

> The whole part hinges on one matrix. **Synchronous (RequestResponse):** caller waits for the result and **owns the retry** — `API Gateway`, ALB, `Cognito`, `Step Functions`, Lex/Alexa, `Lambda@Edge`, `S3 Batch Operations`, and direct SDK/CLI invokes; payload up to **6 MB**. **Asynchronous (Event):** the service hands the event to Lambda's internal queue and gets a `202` back; **Lambda retries up to 2 more times** then sends to a DLQ / on-failure destination — `S3` notifications, `SNS`, `EventBridge`, SES, CloudFormation, IoT, CloudWatch Logs, Config; payload up to **1 MB**. **Event source mapping (poll-based):** **Lambda polls the source** and invokes in batches — `SQS` (standard & FIFO), `Kinesis Data Streams`, `DynamoDB Streams`, Amazon MQ, MSK/self-managed Kafka, DocumentDB.

### Question 23 — Answer: **B**
- **Why correct:** `S3` event notifications invoke Lambda **asynchronously (Event mode)**. S3 places the event in Lambda's internal queue, receives an immediate acknowledgement, and **Lambda** (not S3) handles retries — up to 2 automatic retries, then a DLQ / on-failure destination if configured. There is no polling and no event source mapping involved.
- **Why the others are wrong:** A — this is the classic trap; `S3` → Lambda is **push/async**, not poll-based (only `SQS`/`Kinesis`/`DynamoDB Streams`/MQ/Kafka are polled). C — S3 does not invoke synchronously or wait on the function. D — there is no persistent WebSocket; S3 fires a discrete async event.
- 🧠 **Key point / trap:** `S3` → Lambda = **ASYNC push**. Do not confuse it with `SQS` → Lambda (poll). Async payload limit = **1 MB**.
- 📎 Source: `resources/lambda-faqs.md` ("What is an event source?" — *"Some services publish events by invoking the function directly, e.g. Amazon S3"*); AWS Lambda Developer Guide — invocation modes.

### Question 24 — Answer: **A**
- **Why correct:** `SQS` → Lambda is an **event source mapping**: a Lambda-managed poller **pulls** messages from the queue in batches and invokes the function (internally synchronous). SQS itself never pushes to Lambda.
- **Why the others are wrong:** B — SQS does not invoke Lambda asynchronously; the "retry twice" behavior belongs to the async model (`S3`/`SNS`). C — there is no streamed/open connection; Lambda polls on an interval. D — you do **not** call `ReceiveMessage` in the handler; the event source mapping delivers messages in the `event` payload for you.
- 🧠 **Key point / trap:** `SQS` → Lambda = **poll / event source mapping** (Lambda pulls). `SNS` → Lambda = **push / async**. Same-looking messaging services, opposite models.
- 📎 Source: `resources/lambda-faqs.md` ("What is an event source?" — *"Lambda can also poll resources... pull records from an Amazon Kinesis stream or an Amazon SQS queue"*).

### Question 25 — Answer: **C**
- **Why correct:** `SNS` → Lambda is **asynchronous**. On failure Lambda **retries the event up to two more times** (with delays). Because no on-failure destination or DLQ is configured, the event is **discarded** once the retries are exhausted.
- **Why the others are wrong:** A — async does retry (it is not fire-and-forget from Lambda's side). B — Lambda does not hand the exception back to SNS synchronously; SNS already got its `202` when it delivered the event. D — Lambda does not re-publish failed events back onto the SNS topic.
- 🧠 **Key point / trap:** Async failure path = **2 retries → DLQ / on-failure destination → otherwise dropped**. Configure a destination/DLQ if you cannot afford to lose events.
- 📎 Source: `resources/lambda-faqs.md` ("What happens if my function fails while processing an event?"; "What happens if my function invocations exhaust the available policy?" — DLQ).

### Question 26 — Answer: **A, C**
- **Why correct:** A `S3` event notifications and C `SNS` both **push** events and invoke Lambda **asynchronously** (Event mode).
- **Why the others are wrong:** B `API Gateway` invokes **synchronously** (RequestResponse). D `SQS` and E `Kinesis Data Streams` are **poll-based event source mappings**, not async push.
- 🧠 **Key point / trap:** Async push senders to remember: **`S3`, `SNS`, `EventBridge`**, SES, CloudFormation, IoT, CloudWatch Logs, Config.
- 📎 Source: `resources/lambda-faqs.md` ("What is an event source?"); AWS Lambda Developer Guide — asynchronous invocation.

### Question 27 — Answer: **B, C**
- **Why correct:** B `DynamoDB Streams` and C `SQS FIFO queue` are consumed through **event source mappings** — Lambda **polls** the source and invokes the function in batches. (Both standard and FIFO SQS are poll-based.)
- **Why the others are wrong:** A `EventBridge` (scheduled rule) invokes Lambda **asynchronously**. D `SNS` is **async push**. E `ALB` invokes **synchronously**.
- 🧠 **Key point / trap:** Poll-based sources to remember: **`SQS` (standard + FIFO), `Kinesis Data Streams`, `DynamoDB Streams`**, Amazon MQ, MSK/Kafka, DocumentDB.
- 📎 Source: `resources/lambda-faqs.md` ("What is an event source?"); AWS Lambda Developer Guide — event source mappings.

### Question 28 — Answer: **A**
- **Why correct:** `API Gateway` (like ALB, `Cognito`, `Step Functions`, `Lambda@Edge`) invokes Lambda **synchronously**. Lambda does **not** retry synchronous invocations — it returns the result or the error to the caller — so the **caller/client** must implement retry with backoff (or handle the error).
- **Why the others are wrong:** B — API Gateway is synchronous, not asynchronous; on-failure destinations apply to async invocations only. C — the "2 retries" behavior is async-only; there is no automatic retry for synchronous calls. D — you cannot attach an event source mapping to API Gateway; that concept applies to poll-based sources.
- 🧠 **Key point / trap:** **Sync = caller owns the retry.** No automatic Lambda retry for `API Gateway`/ALB/SDK invokes. Sync payload limit = **6 MB**.
- 📎 Source: `resources/lambda-faqs.md` ("How do I invoke an AWS Lambda function over HTTPS?" — API Gateway); AWS Lambda Developer Guide — synchronous invocation.

### Question 29 — Answer: **B**
- **Why correct:** `IteratorAge` measures the age of the last record processed from a shard. A **high and rising** value means the consumer is **falling behind** — records are being read slower than they arrive, so the "oldest unprocessed record" keeps aging. Remedies: raise the **parallelization factor** (up to 10 for Kinesis), add shards, increase batch size/memory, or speed up the function.
- **Why the others are wrong:** A — a permission failure surfaces as read/`AccessDenied` errors, not a steadily climbing `IteratorAge`. C — too few records would keep `IteratorAge` **low**, not rising. D — Lambda refreshes execution-role credentials automatically; it does not drive `IteratorAge`.
- 🧠 **Key point / trap:** **`IteratorAge` climbing = processing lag / consumer behind** on a stream. It is *the* metric to watch for `Kinesis`/`DynamoDB Streams`.
- 📎 Source: AWS Lambda Developer Guide — monitoring Kinesis/DynamoDB stream event sources (`IteratorAge`); `resources/lambda-faqs.md` (stream retry until success or expiry).

### Question 30 — Answer: **A, B**
- **Why correct:** In stream sources, records are processed **in order per shard**, so one failing record **blocks the whole shard** until it succeeds or the data expires. To let the shard progress: A **bisect batch on function error** splits the batch to isolate the poison record; B a **maximum retry attempts** / **maximum record age** limit plus an **on-failure destination** lets Lambda give up on the bad record (sending its metadata aside) and move on.
- **Why the others are wrong:** C — more memory speeds a slow function but does not stop a *deterministic* failure from re-blocking the shard. D — you cannot make a stream event source "asynchronous"; the poison-record blocking is inherent to ordered stream processing. E — Provisioned Concurrency addresses cold starts, not a poison record.
- 🧠 **Key point / trap:** Stream poison-record toolkit: **bisect on error + max retry attempts / max record age + on-failure destination**. Error in 1 record blocks the shard by default.
- 📎 Source: AWS Lambda Developer Guide — error handling for Kinesis/DynamoDB stream event source mappings; `resources/lambda-faqs.md` (streams retried until success or expiry).

### Question 31 — Answer: **B**
- **Why correct:** When an `SQS` message is delivered to Lambda it becomes invisible for the **visibility timeout**. If the function has not finished (and deleted the message) before that window elapses, the message becomes visible again and is processed a second time. AWS recommends a **visibility timeout ≥ 6× the function timeout** (here 6 × 60 s = 360 s) to give processing plenty of headroom.
- **Why the others are wrong:** A — a batch size of 1 reduces batching but does not fix a visibility window that is too short. C — long polling only reduces empty `ReceiveMessage` calls; it has nothing to do with reprocessing. D — more concurrency does not stop a message from reappearing mid-processing.
- 🧠 **Key point / trap:** `SQS` + Lambda reprocessing → **visibility timeout ≥ 6× function timeout**. On failure, the message returns to the queue after the visibility timeout.
- 📎 Source: AWS Lambda Developer Guide — using Lambda with Amazon SQS (visibility timeout recommendation).

### Question 32 — Answer: **B**
- **Why correct:** **Partial batch response** (`ReportBatchItemFailures`) lets the function return the IDs of only the messages that failed. Lambda then makes **only those** messages visible again for retry and treats the rest as successfully processed — so the 9 good messages are not reprocessed.
- **Why the others are wrong:** A — batch size 1 avoids the problem but throws away batching efficiency and increases invocation count/cost. C — deleting successful messages yourself is fragile and not the managed pattern; if the batch still reports failure the deletes race the redelivery. D — moving to async with a DLQ changes the whole model and does not apply to an SQS event source.
- 🧠 **Key point / trap:** "Only retry the failed items in a batch" → **`ReportBatchItemFailures` (partial batch response)**. Works for SQS, Kinesis, and DynamoDB Streams.
- 📎 Source: AWS Lambda Developer Guide — batch item failures / partial batch response.

### Question 33 — Answer: **B**
- **Why correct:** For an `SQS` event source, the **dead-letter queue lives on the SQS source queue** — you set a **redrive policy** with `maxReceiveCount` that points to a separate DLQ. After a message is received that many times without being deleted, SQS moves it to the DLQ.
- **Why the others are wrong:** A — the function's **on-failure destination / async DLQ** applies to the **asynchronous** invocation model (`S3`/`SNS`/`EventBridge`), not to a polled SQS source. C — the execution role governs permissions, not failed-message routing. D — `ReportBatchItemFailures` controls which items are retried, not where exhausted messages land.
- 🧠 **Key point / trap:** `SQS` DLQ = **on the queue** (redrive policy). Async DLQ / on-failure destination = **on the Lambda function**. Do not mix them up.
- 📎 Source: AWS Lambda Developer Guide — Amazon SQS dead-letter queues; `resources/lambda-faqs.md` ("What resources can I configure as a dead letter queue?" — SQS queue or SNS topic).

### Question 34 — Answer: **A**
- **Why correct:** Event source mappings for `SQS`, `Kinesis`, and `DynamoDB Streams` support **filter criteria (event filtering)**. Lambda evaluates each record against the filter and **only invokes** the function for matching records — cutting invocations and cost, with no wasted "invoke-then-return-early" runs.
- **Why the others are wrong:** B — the early-return `if` still **invokes** the function (you pay for every invocation), which is exactly the waste to eliminate. C — the batch window batches records over time; it does not drop non-matching records. D — a separate stream per event type is heavy, and DynamoDB Streams cannot be split by event type anyway.
- 🧠 **Key point / trap:** "Invoke only for matching records / cut wasted invocations" → **event filtering (filter criteria)** on the event source mapping.
- 📎 Source: AWS Lambda Developer Guide — event filtering for event source mappings.

### Question 35 — Answer: **A**
- **Why correct:** For an `SQS FIFO` source, Lambda guarantees ordering **within each message group ID**: it processes one batch per group at a time and, on failure, stops that group to preserve order. Throughput scales **horizontally with the number of active message groups** — many customers (group IDs) run in parallel while each customer's messages stay ordered.
- **Why the others are wrong:** B — it is not a single global loop; different message groups are processed concurrently. C — FIFO explicitly honors the message group ID; it does not process a group fully out of order. D — ordering is inherent to FIFO handling and does not require Provisioned Concurrency.
- 🧠 **Key point / trap:** `SQS FIFO` + Lambda = **order preserved per message group**, concurrency scales with the count of active groups.
- 📎 Source: AWS Lambda Developer Guide — using Lambda with SQS FIFO queues (message group ordering & scaling).

### Question 36 — Answer: **A, B**
- **Why correct:** A — `SNS` → Lambda is **async push**; once the 2 async retries are exhausted with no on-failure destination/DLQ, the event is **lost**. B — `SQS` → Lambda is **poll-based**: messages stay **buffered in the queue** up to the retention period and are retried after the visibility timeout, so a Lambda outage does not lose events — the durability advantage the scenario needs.
- **Why the others are wrong:** C — SNS does **not** guarantee exactly-once, in-order delivery to Lambda; a queue is exactly what adds the buffering/durability here. D — Lambda never "pushes back" to the producer; SQS simply retains messages. E — SNS → Lambda does **not** auto-retain undelivered events for 14 days; you must configure a DLQ/on-failure destination.
- 🧠 **Key point / trap:** Need a **buffer / no-loss during outages** → prefer **`SQS` (poll, retained + visibility-timeout retry)** over **`SNS` (async push, lost after retries)**. Fan-out pattern `SNS → SQS → Lambda` combines both.
- 📎 Source: `resources/lambda-faqs.md` ("What is an event source?"; async failure/DLQ behavior); AWS Lambda Developer Guide — comparing SNS vs SQS event sources.
