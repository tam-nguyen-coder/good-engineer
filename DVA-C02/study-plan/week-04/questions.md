# 📝 Practice Questions — Week 4: Amazon API Gateway + S3 + CloudFront + AppSync

> **28 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Week 4 material.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D1.1 · API Gateway · Single]`
A startup is building a serverless backend in which a mobile app calls a single AWS Lambda function directly over HTTP. The team requires the **lowest cost** and the **lowest latency**, and does NOT need API keys, request validation, or caching. Which API Gateway type is the MOST appropriate?
- A. Edge-optimized REST API
- B. WebSocket API
- C. HTTP API
- D. Private REST API

### Question 2 — `[D1.1 · API Gateway · Single]`
A SaaS company sells an API to many customers. Each customer must have its **own monthly request quota** and its **own rate limit**, and the company needs **API-tier caching** to reduce backend load and integration with **AWS WAF**. Which API Gateway type meets all of these requirements?
- A. REST API
- B. HTTP API — because it is cheaper and supports JWT
- C. WebSocket API
- D. HTTP API with a Lambda authorizer

### Question 3 — `[D1.1 · API Gateway · Single]`
A chat application needs the server to **push new messages to the client** the moment they arrive, maintaining a **persistent, bidirectional connection**. Which API Gateway type is appropriate?
- A. REST API with long polling
- B. HTTP API with Server-Sent Events
- C. REST API with S3 event notifications
- D. WebSocket API

### Question 4 — `[D1.1 · API Gateway · Multi — Choose 2]`
A team is considering migrating from a REST API to an HTTP API to save cost. They need to know which features would be **lost because they exist ONLY in REST API**. Which **two** features exist only in REST API? (Choose two.)
- A. API keys and usage plans (per-client rate limiting)
- B. Lambda proxy integration
- C. CORS configuration
- D. Per-stage caching
- E. IAM authorization

### Question 5 — `[D1.1 · API Gateway · Single]`
A developer configures the `POST /orders` method with a Lambda proxy (`AWS_PROXY`) integration. Which statement about how it works is TRUE?
- A. API Gateway transforms the request with a VTL mapping template before invoking Lambda.
- B. API Gateway passes the **entire** request (headers, query string, path, body) to Lambda as a standard event, and the Lambda function **must return** `{ statusCode, headers, body }` itself.
- C. Lambda receives only the body, not the headers or query string.
- D. The Lambda response is automatically remapped by API Gateway through an integration response template.

### Question 6 — `[D1.1 · API Gateway · Single]`
A legacy backend accepts **XML**, while clients send **JSON**. A developer wants API Gateway to **transform the payload JSON→XML on the request and XML→JSON on the response** without changing either the client or the backend code. Which approach is appropriate?
- A. Use a Lambda proxy (`AWS_PROXY`) integration.
- B. Enable caching on the stage.
- C. Use a non-proxy integration with a VTL mapping template.
- D. Use an HTTP API with auto-deploy.

### Question 7 — `[D1.1 · API Gateway · Single]`
After a deployment, a client calls the API (Lambda proxy integration) and receives a **`502 Bad Gateway`**, even though the Lambda function runs without error in CloudWatch Logs. What is the MOST likely cause?
- A. The Lambda function timed out after more than 29 seconds.
- B. The request is missing an API key.
- C. CORS is not enabled.
- D. The Lambda function **does not return the** `{ statusCode, headers, body }` format that a proxy integration requires.

### Question 8 — `[D1.1 · API Gateway · Single]`
A REST API has two stages, `dev` and `prod`. With the same API definition, `dev` must invoke the Lambda alias `DEV` while `prod` must invoke the alias `PROD`. What is the BEST way to achieve this?
- A. Create two completely separate APIs.
- B. Hardcode the alias ARN in a mapping template.
- C. Use a **stage variable** (e.g. `${stageVariables.lambdaAlias}`) in the integration, with a different value per stage that points to the corresponding alias.
- D. Use a different API key per stage.

### Question 9 — `[D2.1 · API Gateway · Single]`
Users sign in to a web app through an **Amazon Cognito User Pool** and receive an `IdToken` (JWT). A REST API must **validate this JWT** to authorize requests, and the team does NOT want to write custom code to decode/validate the token. Which authorizer is the MOST appropriate?
- A. Cognito User Pool authorizer
- B. IAM authorizer (SigV4)
- C. Lambda authorizer of type `TOKEN` that decodes the JWT itself
- D. API key

### Question 10 — `[D2.1 · API Gateway · Multi — Choose 2]`
Regarding API Gateway authorizer types, which **two** statements are TRUE? (Choose two.)
- A. IAM authorization requires the caller to **sign the request with SigV4** using AWS credentials.
- B. A Cognito User Pool authorizer requires you to write a Lambda function to validate the JWT.
- C. A Lambda authorizer of type `REQUEST` can evaluate **multiple identity sources** (headers, query string, `stageVariables`, `$context`), while `TOKEN` accepts **only a single bearer token** in a header.
- D. A Lambda authorizer cannot return an IAM policy.
- E. A `TOKEN` authorizer is more flexible than `REQUEST` because it can read `$context`.

### Question 11 — `[D1.1 · API Gateway · Single]`
A public REST API serves many partners. You need to **identify each partner** and **limit the number of requests per service tier** (Free/Pro). Which combination of features should you use?
- A. Lambda authorizer + CloudWatch
- B. Cognito + IAM
- C. Resource policy + WAF
- D. API keys + usage plans

### Question 12 — `[D1.3 · API Gateway · Single]`
A REST API calls a heavy backend and receives many duplicate requests in a short window. You enable **caching** on the stage to reduce load. Which statement about caching is TRUE?
- A. Caching is enabled at the method level, with a default TTL of 3600 seconds.
- B. Caching is available in both HTTP API and REST API.
- C. Caching is enabled **per stage**, with a **default TTL of 300 seconds** (adjustable between 0–3600s).
- D. Caching is stored on the client side, not at API Gateway.

### Question 13 — `[D1.1 · API Gateway · Single]`
A Lambda function that aggregates a report takes **~45 seconds**. When called through a Regional REST API, the client receives a timeout error. What is the CORRECT way to handle this?
- A. Nothing can be done — API Gateway is fixed at 29 seconds.
- B. The integration timeout **defaults to 29s** but can be **increased up to 300s** via Service Quotas for **Regional/private REST APIs** (trading off a lower throttle quota); alternatively, design it as **async** (return `202` and process in the background).
- C. Switch to an HTTP API to raise the timeout to 300s.
- D. Enable caching to avoid the timeout.

### Question 14 — `[D1.1 · API Gateway · Single]`
A frontend at `https://app.example.com` calls a REST API (Lambda **proxy** integration) on a different domain; the browser reports `Cross-Origin Request Blocked`. The developer clicked "Enable CORS" in the console but the error persists. What is the cause and fix?
- A. The newly created `OPTIONS` method must be deleted.
- B. CORS is supported only on HTTP API.
- C. With a **proxy integration**, the **Lambda function must return the CORS headers** (`Access-Control-Allow-Origin`, ...) in its response, because proxy does not use integration responses.
- D. Caching must be enabled for CORS to work.

### Question 15 — `[D2.1 · S3 · Single]`
A web app must let users **upload files directly to S3** from the browser **without exposing AWS credentials** and **without changing the bucket policy**. Which approach is appropriate?
- A. Give each user an IAM user + access key.
- B. Create a **presigned URL** with the **`PUT`** HTTP method and return the URL to the client to upload.
- C. Enable public write on the bucket.
- D. Use CloudFront signed cookies.

### Question 16 — `[D2.1 · S3 · Single]`
Regarding an S3 presigned URL, which statement is the MOST correct?
- A. The URL grants access indefinitely until it is manually deleted.
- B. The URL always has a maximum lifetime of 12 hours regardless of how it is created.
- C. The URL **inherits the permissions of the IAM principal that created it**; if signed with an IAM user credential + SigV4 the maximum is **7 days**, but if created with **temporary credentials** (STS/role) the URL **expires when the credentials expire** even if a longer expiry is set.
- D. Anyone can create a working URL without any permissions.

### Question 17 — `[D1.3 · S3 · Single]`
A team needs to upload many **8 GB video files** to S3 over an unstable network, wants parallel uploads and to retry only failed parts, and asks about the mandatory threshold. Which statement is TRUE?
- A. A single `PutObject` supports up to 5 TB, so multipart is not needed.
- B. **multipart upload is recommended when an object > 100 MB** and **required when > 5 GB** (a single `PutObject` is capped at 5 GB); multipart allows parallel upload and per-part retry.
- C. Files must be compressed below 5 GB before uploading.
- D. `S3 Transfer Acceleration` is mandatory instead of multipart.

### Question 18 — `[D1.3 · S3 · Multi — Choose 2]`
Regarding S3 multipart upload, which **two** statements are TRUE? (Choose two.)
- A. After initiation, uploaded parts are **still billed for storage** until `CompleteMultipartUpload` or `AbortMultipartUpload`; you should set a lifecycle rule with **`AbortIncompleteMultipartUpload`** to clean up leftovers.
- B. On completion, you must provide the **part number + `ETag`** of each part (stored by you, **NOT** taken from the result of `ListParts`).
- C. Part numbers must be consecutive and can never be overwritten.
- D. S3 automatically aborts incomplete multipart uploads after 24 hours.
- E. multipart upload can be used only for objects under 100 MB.

### Question 19 — `[D2.2 · S3 · Single]`
A compliance requirement states that you must be able to **audit who used the encryption key and when** (logged through CloudTrail), **automatically rotate the key**, and control key usage by policy. Which S3 encryption type meets this?
- A. `SSE-S3`
- B. `SSE-C`
- C. `SSE-KMS`
- D. Client-side encryption with a static key embedded in the app

### Question 20 — `[D2.2 · S3 · Multi — Choose 2]`
Which **two** statements about S3 encryption (current behavior) are TRUE? (Choose two.)
- A. Since January 2023, **`SSE-S3` is the automatic, default baseline encryption** for every newly uploaded object, at no extra cost.
- B. With **`SSE-C`**, the customer **provides the key** on each request; S3 encrypts/decrypts but **does not store the key**.
- C. Both `SSE-S3` and `SSE-KMS` can be applied to the same object at the same time.
- D. `SSE-S3` allows per-key auditing through CloudTrail.
- E. Changing a bucket's default encryption to `SSE-KMS` automatically re-encrypts all existing objects.

### Question 21 — `[D1.3 · S3 · Multi — Choose 2]`
You need to **run code whenever a new file arrives** in a bucket (e.g. to generate a thumbnail). You configure an S3 event notification (`s3:ObjectCreated:*`). Which **two** are valid direct destinations of an S3 event notification? (Choose two.)
- A. AWS Lambda
- B. Amazon SQS
- C. Amazon EC2 (invoked directly on the instance)
- D. Amazon RDS (written directly to the DB)
- E. AWS Step Functions (invoked directly as a state machine)

### Question 22 — `[D1.3 · S3 · Single]`
A Lambda function **writes an object (`PutObject`) then immediately reads it back (`GetObject`)** with the same key in the same execution. Regarding current S3 consistency, which statement is TRUE?
- A. It may read stale data due to eventual consistency; you must retry.
- B. S3 provides **strong read-after-write consistency** for all operations (PUT/GET/LIST) — a read right after a write always sees the latest data.
- C. Strong consistency applies only when versioning is enabled.
- D. Strong consistency applies only within the same Availability Zone.

### Question 23 — `[D1.1 · CloudFront · Single]`
You need to distribute a **private HLS video library made of many files** through CloudFront, only to paying users, **without signing each URL individually** and while **keeping the original URLs**. Which mechanism is appropriate?
- A. A CloudFront **signed URL** per file
- B. An S3 presigned URL per file
- C. Public bucket + AWS WAF
- D. CloudFront **signed cookies**

### Question 24 — `[D2.1 · CloudFront · Multi — Choose 2]`
A team is moving from `OAI` to **`OAC` (Origin Access Control)** so that CloudFront can access a private S3 bucket. Which **two** statements about `OAC` are TRUE? (Choose two.)
- A. `OAC` supports S3 origins encrypted with **`SSE-KMS`** (something `OAI` does not support well).
- B. The bucket policy only allows **CloudFront (via OAC)** to read, so users **cannot access S3 directly**.
- C. `OAC` makes the S3 bucket public.
- D. `OAC` works only in the `us-east-1` region.
- E. `OAC` completely replaces the need to use HTTPS.

### Question 25 — `[D1.1 · CloudFront · Single]`
You need to distinguish an S3 presigned URL from a CloudFront signed URL for **private content distributed globally at large scale**. Which statement is the MOST correct?
- A. S3 presigned URLs are served through the global edge cache; CloudFront signed URLs go directly to S3.
- B. CloudFront signed URLs are distributed **through the edge/cache** (near users, at scale) and are signed with a **trusted key group / key pair**; while S3 presigned URLs access **S3 directly**, inheriting the IAM permissions of the identity that created the URL, suitable for temporary upload/download.
- C. Both require the bucket to be public.
- D. CloudFront signed URLs are only for uploads, not downloads.

### Question 26 — `[D1.1 · CloudFront · Single]`
You just deployed a new JS build, but CloudFront still returns the old one because the object is still within its TTL. What is the immediate fix and the long-term best practice?
- A. Delete the distribution and recreate it.
- B. Set the TTL to 0 permanently.
- C. Create an **invalidation** (`CreateInvalidation`) by path to clear the cache before the TTL expires (first 1,000 paths/month are free); the better long-term approach is to use **versioned object names** (e.g. `app.v2.js`) so no invalidation is needed.
- D. Switch the origin to an HTTP API.

### Question 27 — `[D1.1 · AppSync · Single]`
A mobile client needs **flexible querying**: fetch only the fields it needs (avoiding over-fetch/under-fetch) and aggregate multiple data sources through **a single endpoint**. Which service is the MOST appropriate?
- A. API Gateway REST API with multiple resources
- B. API Gateway HTTP API
- C. CloudFront + static S3
- D. AWS AppSync (GraphQL)

### Question 28 — `[D1.1 · AppSync · Multi — Choose 2]`
Regarding AWS AppSync, which **two** statements are TRUE? (Choose two.)
- A. A resolver (written in VTL or JS) connects a GraphQL field to a data source such as DynamoDB, Lambda, or an HTTP endpoint.
- B. A subscription **pushes real-time data** to the client over WebSocket when data changes.
- C. AppSync supports only DynamoDB as its single data source.
- D. AppSync does not support authorization with a Cognito User Pool.
- E. AppSync is a traditional REST service, not GraphQL.
