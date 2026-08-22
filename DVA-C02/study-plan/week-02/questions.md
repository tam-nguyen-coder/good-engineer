# 📝 Practice Questions — Week 2: AWS Lambda in Depth — Versions, Aliases, Layers, Concurrency, Event Sources

> **26 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Week 2 material.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D3.1 · Lambda · Single]`
A company runs an AWS Lambda function that processes payments in production. Developers continuously update the function code in a development environment. The requirement is that the version serving production MUST remain fixed—its code and configuration must not change unintentionally—even as developers keep deploying new code. Which solution meets this requirement?
- A. Point production to `$LATEST` and enable versioning on the S3 bucket that stores the code.
- B. Publish a version of the function; the version is an immutable snapshot of the code and configuration and has its own numbered ARN.
- C. Enable provisioned concurrency to "lock" the current code in place.
- D. Set reserved concurrency to 0 to prevent any code changes.

### Question 2 — `[D1.2 · Lambda · Single]`
A developer runs `publish-version` twice in a row; between the two calls the developer changes only the function's **reserved concurrency** and nothing else about the code or configuration. The second publish does not create a new version. Why?
- A. Because `$LATEST` can be published at most once per day.
- B. Because reserved concurrency is an operational setting—changing it does not qualify the function for a new version; Lambda publishes a version only when the code (or qualifying configuration) differs from the last version.
- C. Because memory must be increased before a version can be published.
- D. Because changing reserved concurrency resets the version counter to 0.

### Question 3 — `[D3.4 · Lambda · Single]`
Several microservices invoke a Lambda function directly using its ARN. Every time a new version is deployed, the team must update the ARN in all clients, which is error-prone and easy to miss. Which solution lets the team deploy new versions WITHOUT clients having to change the ARN?
- A. Create an alias (for example, `prod`) that points to a version; clients call the alias ARN, and deploying a new version only requires `update-alias`.
- B. Always invoke through the unqualified ARN (`$LATEST`) so the ARN never has to change.
- C. Enable weighted routing between the `prod` alias and a `blue` alias.
- D. Use an S3 presigned URL that points to the new version's code file.

### Question 4 — `[D3.4 · Lambda · Single]`
A team wants to roll out new code (version 2) as a canary: 90% of traffic continues to the stable version 1 and 10% goes to version 2 to observe errors before a full rollout. Which configuration is correct?
- A. Create two separate functions and use Amazon Route 53 weighted records to split traffic 90/10.
- B. Configure a weighted alias: the alias points to version 1 as the primary, and add `AdditionalVersionWeights` for version 2 = `0.10`.
- C. Set provisioned concurrency to 10% for version 2.
- D. Create two aliases and point one alias to the other at a 90/10 ratio.

### Question 5 — `[D1.2 · Lambda · Multi — Choose 2]`
Which of the following statements about Lambda aliases are TRUE? (Choose two.)
- A. An alias can point to another alias to create a chain of environments.
- B. An alias's weighted routing splits traffic between exactly two versions.
- C. You cannot create an alias from an unqualified ARN (an ARN with no version number).
- D. An alias can point directly to `$LATEST` and split traffic with a published version.
- E. Each alias keeps its own immutable copy of the function code.

### Question 6 — `[D1.2 · Lambda · Multi — Choose 2]`
An organization has 30 Node.js Lambda functions that share one large set of libraries. They want to reduce the size of each deployment package and manage dependencies centrally. Which benefits does using Lambda layers provide? (Choose two.)
- A. Sharing the same set of dependencies across multiple functions without repackaging them into each deployment package.
- B. Automatically eliminating cold starts for every function that uses the layer.
- C. Reducing the deployment package size of each function.
- D. Increasing the function timeout limit to 30 minutes.
- E. Allowing functions packaged as container images to load layers from `/opt` at runtime.

### Question 7 — `[D3.1 · Lambda · Single]`
A build team packages a Lambda function as a **container image**. They want to extract a shared library into a Lambda layer so multiple images can reuse it. Which statement is correct?
- A. Yes, the layer will automatically attach to every container image through the `/opt` directory.
- B. No—functions packaged as a container image cannot use layers; the runtime and dependencies must be built directly into the image.
- C. Yes, but a container image can attach at most 10 layers.
- D. Yes, as long as the image is smaller than 50 MB.

### Question 8 — `[D1.2 · Lambda · Single]`
A function needs a sensitive database connection string passed through an environment variable. The requirement is to encrypt this value at rest and restrict who can decrypt it. Which approach is most appropriate?
- A. Store the connection string in `/tmp` so it exists only at runtime.
- B. Encrypt the environment variable with a dedicated AWS KMS key (a customer managed key); only principals with permission to use the key can decrypt it.
- C. Set reserved concurrency to protect the environment variable.
- D. Increase the environment variables limit to 40 KB and add a salt to the value.

### Question 9 — `[D4.3 · Lambda · Single]`
A critical function writes to an Amazon RDS database that can tolerate only a limited number of connections. During traffic spikes, Lambda scales too fast and exhausts the RDS connection pool. The team needs to both **protect the downstream** (limit the number of concurrent instances) and ensure this function always has a dedicated share of concurrency. Which solution meets these requirements?
- A. Provisioned concurrency set to a high number to keep many warm environments ready.
- B. Reserved concurrency: set a ceiling to limit the number of concurrent instances (protecting RDS) while reserving a dedicated pool for the function.
- C. Increase the account concurrency limit through AWS Support.
- D. Set a very short timeout to reduce the number of concurrent open connections.

### Question 10 — `[D4.3 · Lambda · Single]`
An interactive (web) API invokes a Lambda function synchronously, with steady traffic, and users are highly sensitive to latency. The team wants to **eliminate cold starts** for the predictable traffic. Which solution is most appropriate?
- A. Reserved concurrency set high enough.
- B. Provisioned concurrency attached to an alias/version to keep pre-initialized, warm environments ready (delivering double-digit millisecond response times).
- C. Increase memory to 10,240 MB.
- D. Switch to asynchronous invocation to bypass cold starts.

### Question 11 — `[D4.3 · Lambda · Single]`
A requirement states that an order-processing function must ALWAYS have at least 50 dedicated concurrency slots (that other functions cannot take) and must NOT scale beyond 50 to protect downstream systems. The requirement does NOT mention cold starts. Choose the correct and most cost-effective configuration.
- A. Provisioned concurrency = 50 (keep 50 warm environments).
- B. Reserved concurrency = 50 (no additional cost; acts as both a ceiling and a dedicated pool for the function).
- C. Enable SnapStart on the `prod` alias.
- D. Set the account concurrency limit for the entire Region to 50.

### Question 12 — `[D1.2 · Lambda · Single]`
During an incident, a developer wants to **completely pause** an asynchronous function from processing any events until the investigation is complete, without deleting the function or its trigger. What is the fastest way?
- A. Delete the function's `prod` alias.
- B. Set reserved concurrency = 0 → the function is fully throttled and stops processing events.
- C. Set provisioned concurrency = 0.
- D. Increase the timeout to 900s so the function stops on its own.

### Question 13 — `[D4.3 · Lambda · Multi — Choose 2]`
A Node.js function has high cold start latency. The team does not yet want to pay to keep environments warm. Which measures help REDUCE cold starts? (Choose two.)
- A. Reduce the deployment package size (remove unnecessary dependencies, use layers sensibly).
- B. Move heavy initialization (creating SDK clients, opening connections) OUTSIDE the handler so it runs once during the init phase.
- C. Switch everything to asynchronous invocation.
- D. Increase reserved concurrency to a high value.
- E. Set the timeout to the maximum of 900s.

### Question 14 — `[D4.3 · Lambda · Multi — Choose 2]`
A team runs a Java 17 function with a cold start of a few seconds. They want to reduce cold starts but do NOT want to pay to keep environments continuously warm as provisioned concurrency does. Which statements about **SnapStart** are TRUE? (Choose two.)
- A. SnapStart supports the Java, Python, and .NET runtimes (eligible versions).
- B. SnapStart can be used only on a published version/alias, not on `$LATEST`.
- C. SnapStart must be enabled together with provisioned concurrency.
- D. SnapStart guarantees the complete elimination of cold starts, just like provisioned concurrency.
- E. SnapStart works only with functions packaged as a container image.

### Question 15 — `[D1.2 · Lambda · Single]`
Which statement correctly describes the difference between synchronous (`RequestResponse`) and asynchronous (`Event`) Lambda invocation?
- A. Async: the caller receives the code's result immediately; sync: the caller receives only a `202`.
- B. Async (`Event`): Lambda places the event in an internal queue, returns `202` immediately without waiting for the code to finish, and retries automatically on error. Sync (`RequestResponse`): the caller waits for the result and must retry itself on error.
- C. Async does not support error handling or destinations.
- D. Sync and async have the same payload limit of 256 KB.

### Question 16 — `[D1.2 · Lambda · Single]`
A service sends a JSON payload of about **5 MB**. Invoking the function with `RequestResponse` (sync) works, but switching to `--invocation-type Event` (async) fails with a payload size error. What is the cause?
- A. Async limits the payload to **1 MB**, while sync allows up to **6 MB** → 5 MB exceeds the async limit.
- B. Async limits the payload to 256 KB, so 5 MB always fails with both invocation types.
- C. Sync limits to 1 MB and async to 6 MB → the limits are configured backward.
- D. Both limit to 10 MB; the error is only due to a missing `--cli-binary-format`.

### Question 17 — `[D1.2 · Lambda · Single]`
A function is invoked asynchronously by Amazon S3. Occasionally the function throws an error. By default, how does Lambda handle asynchronous errors?
- A. It immediately re-invokes 5 times and then discards the event.
- B. It retries **2 times** (**3 attempts** total); if it still fails, it sends the event to a **DLQ** or to **`OnFailure` destinations** if configured.
- C. It does not retry; the error is returned directly to S3 so S3 retries on its own.
- D. It retries indefinitely until it succeeds.

### Question 18 — `[D1.2 · Lambda · Multi — Choose 2]`
Comparing a **Dead Letter Queue (DLQ)** and **Lambda destinations** for asynchronous invocation, which statements are TRUE? (Choose two.)
- A. Destinations support both `OnSuccess` and `OnFailure`; a DLQ receives an event only on failure.
- B. A DLQ supports Amazon SQS or Amazon SNS targets; destinations support SQS, SNS, Lambda, and Amazon EventBridge.
- C. A DLQ records more metadata than destinations.
- D. Destinations can be used only with synchronous invocation.
- E. A DLQ can target Lambda or EventBridge.

### Question 19 — `[D1.2 · Lambda · Single]`
A team needs to **separately route** both **successful** and **failed** async invocation events to two different queues, along with metadata (request/response context). What should they use?
- A. A Dead Letter Queue.
- B. Lambda destinations with `OnSuccess` and `OnFailure` pointing to two different Amazon SQS queues.
- C. A CloudWatch Logs subscription filter.
- D. Reserved concurrency split by status.

### Question 20 — `[D1.2 · Lambda · Single]`
An application pushes messages to an Amazon SQS queue; Lambda needs to process the messages in batches. Which configuration is correct?
- A. Configure SQS as a push trigger that pushes messages directly into Lambda, like Amazon SNS.
- B. Create an **event source mapping** so Lambda **polls** SQS and invokes the function in batches.
- C. Enable provisioned concurrency so Lambda reads SQS on its own.
- D. Use async invocation from SQS with a payload of up to 1 MB.

### Question 21 — `[D1.2 · Lambda · Multi — Choose 2]`
Which of the following event sources integrate with Lambda through an **event source mapping** (Lambda actively polls), rather than a push trigger mechanism? (Choose two.)
- A. Amazon S3 object-created event.
- B. Amazon Kinesis Data Streams.
- C. Amazon SNS topic.
- D. Amazon DynamoDB Streams.
- E. Amazon API Gateway REST API.

### Question 22 — `[D1.2 · Lambda · Single]`
A function processes records from Amazon SQS via an event source mapping. Occasionally the same record is processed more than once, causing duplicate writes to Amazon DynamoDB. What is the correct approach per AWS recommendations?
- A. Switch to synchronous invocation to avoid duplicates.
- B. Because an event source mapping processes records **at least once** (records may be duplicated), write **idempotent** code (for example, using a unique key / conditional write) to handle duplicates safely.
- C. Increase batch size to 6 MB to combine all records into a single invocation.
- D. Enable provisioned concurrency to eliminate duplicate records.

### Question 23 — `[D1.2 · Lambda · Single]`
A function writes intermediate data to `/tmp` on one invocation and expects to read it back on a later invocation. Occasionally the data "disappears." What is the correct explanation and fix?
- A. `/tmp` is only 512 MB so it fills up; increasing it to 1 GB will make the data durable.
- B. `/tmp` is **not durable** across invocations (it exists only within the lifetime of the execution environment); to store data durably you must use Amazon S3 / DynamoDB / Amazon EFS.
- C. `/tmp` is read-only; you must write to `/opt` for durability.
- D. The lack of provisioned concurrency causes `/tmp` to be cleared between invocations.

### Question 24 — `[D1.2 · Lambda · Single]`
A function is placed in a VPC (private subnet) to access an internal RDS database. It also needs to call a public REST API on the internet, but the request times out. What is the cause and the fix?
- A. A missing Internet Gateway attached directly to the Lambda ENI; you must assign a public IP to the function.
- B. A Lambda function in a private subnet cannot reach the internet on its own; it needs routing through a **NAT Gateway** (placed in a public subnet) so the function can call the internet.
- C. You must fully disable the VPC configuration to reach the internet.
- D. Simply increasing the timeout to 900s resolves the error.

### Question 25 — `[D3.1 · Lambda · Single]`
A function requires a custom runtime and a large set of dependencies that make the unzipped package exceed **250 MB**. Which packaging approach is appropriate?
- A. Compress more aggressively to get the zip under 50 MB and upload it through the console.
- B. Split the dependencies into 6 layers to get around the 250 MB limit.
- C. Package the function as a **container image** (up to **10 GB**), suitable when the package is large or a custom runtime is needed.
- D. Use a 10 GB `/tmp` to hold the dependencies at runtime.

### Question 26 — `[D1.2 · Lambda · Multi — Choose 2]`
Which statements about Lambda quotas are TRUE? (Choose two.)
- A. The maximum timeout of an invocation is **900 seconds (15 minutes)**.
- B. Memory is configurable from 128 MB to **10,240 MB**.
- C. A deployment package zip uploaded directly through the API can be up to **500 MB**.
- D. Environment variables total up to a maximum of **40 KB**.
- E. A function can use a maximum of **10 layers**.
