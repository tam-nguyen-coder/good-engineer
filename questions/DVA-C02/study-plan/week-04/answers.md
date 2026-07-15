# ✅ Answers & Explanations — Week 4: Amazon API Gateway + S3 + CloudFront + AppSync

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-C · 2-A · 3-D · 4-AD · 5-B · 6-C · 7-D · 8-C · 9-A · 10-AC · 11-D · 12-C · 13-B · 14-C · 15-B · 16-C · 17-B · 18-AB · 19-C · 20-AB · 21-AB · 22-B · 23-D · 24-AB · 25-B · 26-C · 27-D · 28-AB

---

### Question 1 — Answer: **C**
- **Why correct:** A simple proxy to Lambda that is the cheapest and lowest latency, with no advanced features needed — this is exactly what an HTTP API is for.
- **Why the others are wrong:** A/D — a REST API (edge-optimized/private) is more expensive and higher latency, and none of the REST-only features are needed here. B — a WebSocket API is for real-time bidirectional traffic, not standard request/response HTTP.
- 🧠 **Key point / trap:** "cheapest + low latency + Lambda proxy" is the switch that turns on HTTP API. Do not reflexively pick REST API.
- 📎 Source: `resources/apigw-rest-vs-http.md`; README "Three API types".

### Question 2 — Answer: **A**
- **Why correct:** API keys + usage plans (per-client quota/rate limit), caching, and AWS WAF integration exist **only in REST API**.
- **Why the others are wrong:** B/D — HTTP API does NOT have API keys, usage plans, caching, or WAF. C — a WebSocket API does not serve this standard request/response model.
- 🧠 **Key point / trap:** Seeing the keyword set API keys / usage plans / caching / WAF / Private API / VTL mapping → it is definitely REST API.
- 📎 Source: `resources/apigw-rest-vs-http.md` (API management & Development tables).

### Question 3 — Answer: **D**
- **Why correct:** The server proactively pushing data to the client + a persistent bidirectional connection = WebSocket API.
- **Why the others are wrong:** A/B — long polling / SSE are workarounds over one-directional HTTP, not the true bidirectional connection the scenario requires. C — S3 event notifications have nothing to do with pushing real-time messages to a web client.
- 🧠 **Key point / trap:** "server pushes to client / real-time bidirectional" → WebSocket API.
- 📎 Source: README "Three API types".

### Question 4 — Answer: **A, D**
- **Why correct:** API keys + usage plans (A) and per-stage caching (D) exist **only in REST API**; HTTP API does not have them.
- **Why the others are wrong:** B — Lambda proxy exists in both. C — CORS can be configured in both. E — IAM authorization exists in both.
- 🧠 **Key point / trap:** The "lost when downgrading to HTTP API" group: API keys/usage plans, caching, request validation, WAF, VTL body transformation, Mock, execution logs, X-Ray, canary, custom gateway responses, resource policies.
- 📎 Source: `resources/apigw-rest-vs-http.md` (comparison tables).

### Question 5 — Answer: **B**
- **Why correct:** A Lambda proxy (`AWS_PROXY`) passes the **entire** request to Lambda as a standard event; Lambda is responsible for returning `{ statusCode, headers, body }`.
- **Why the others are wrong:** A/D — transforming with VTL / integration response templates is characteristic of **non-proxy**, not proxy. C — proxy delivers the full headers, query string, path, and body in the event.
- 🧠 **Key point / trap:** Proxy = "API Gateway forwards the request as-is; Lambda handles the response format itself".
- 📎 Source: README "Integration types" item 2.

### Question 6 — Answer: **C**
- **Why correct:** Transforming the request/response payload requires a **non-proxy integration + VTL mapping template**.
- **Why the others are wrong:** A — proxy does NOT transform the payload (Lambda must do it). B — caching does not transform data. D — HTTP API does NOT support request body transformation (REST API only).
- 🧠 **Key point / trap:** "transform/reshape the payload with a template" → non-proxy + VTL. Body transformation is a REST-only feature.
- 📎 Source: README "Mapping templates (VTL)"; `resources/apigw-rest-vs-http.md` (Request body transformation ❌ on HTTP API).

### Question 7 — Answer: **D**
- **Why correct:** With a proxy integration, Lambda **must** return the exact `{ statusCode, headers, body }` structure. Returning something wrong/missing → API Gateway raises `502 Bad Gateway` even though the function ran "successfully".
- **Why the others are wrong:** A — a timeout produces a timeout/504, not a 502, and the logs show the function had no error. B — a missing API key → 403. C — a CORS error occurs in the browser and does not cause a 502.
- 🧠 **Key point / trap:** `502` + Lambda proxy + logs "OK" = wrong response format. This is a consequence of proxy pushing the formatting responsibility onto Lambda.
- 📎 Source: README "Common exam traps" (502 from wrong format).

### Question 8 — Answer: **C**
- **Why correct:** A stage variable (e.g. `${stageVariables.lambdaAlias}`) acts as a per-stage environment variable; set a different value for `dev`/`prod` so the same API definition points to a different Lambda alias.
- **Why the others are wrong:** A — splitting into two APIs is redundant and hard to maintain. B — hardcoding the ARN loses all of the multi-stage benefit. D — an API key is not used to select a backend.
- 🧠 **Key point / trap:** "same API, different backend per environment" → stage variables pointing to a Lambda alias. (When pointing to a function name you must run `lambda add-permission` yourself.)
- 📎 Source: `resources/apigw-stage-variables.md`; README "Stages + stage variables".

### Question 9 — Answer: **A**
- **Why correct:** A Cognito User Pool authorizer validates the JWT (IdToken) issued by the User Pool in a **managed** way, with no custom code required.
- **Why the others are wrong:** B — IAM (SigV4) is for callers signing with AWS credentials, not for an app user's JWT. C — a Lambda authorizer of type TOKEN that decodes the JWT is redundant work that the Cognito authorizer already does. D — an API key only identifies/meters, it does not authenticate a user.
- 🧠 **Key point / trap:** "user signs in to the app + JWT" → Cognito User Pool authorizer. On HTTP API the equivalent is the JWT authorizer.
- 📎 Source: README "Authorizers"; `resources/apigw-rest-vs-http.md` (Cognito/JWT).

### Question 10 — Answer: **A, C**
- **Why correct:** A — IAM authorization requires the caller to **sign with SigV4** using AWS credentials. C — a REQUEST authorizer evaluates multiple identity sources (headers/query/`stageVariables`/`$context`); TOKEN accepts only **one** bearer token in a header.
- **Why the others are wrong:** B — a Cognito authorizer is managed and does NOT require you to write a Lambda. D — a Lambda authorizer **must** return an IAM policy + principal. E — it is the opposite: REQUEST is the more flexible one (AWS recommends REQUEST).
- 🧠 **Key point / trap:** TOKEN = 1 token; REQUEST = multiple sources (fine-grained). `IdentityValidationExpression` (RegEx) exists ONLY on TOKEN.
- 📎 Source: `resources/apigw-lambda-authorizer.md` (Choosing a type; note recommending REQUEST).

### Question 11 — Answer: **D**
- **Why correct:** API keys identify each partner; usage plans attach quota + rate limit per tier (Free/Pro). Available only in REST API.
- **Why the others are wrong:** A — an authorizer + CloudWatch does not enforce a per-customer quota. B — Cognito/IAM are authentication, not per-tier metering. C — a resource policy/WAF is access control, not a per-client quota.
- 🧠 **Key point / trap:** "distinguish and limit per customer/tier" → API keys + usage plans.
- 📎 Source: README "Usage plans, API keys"; `resources/apigw-rest-vs-http.md`.

### Question 12 — Answer: **C**
- **Why correct:** Caching is enabled **per stage**, with a **default TTL of 300 seconds**, adjustable within 0–3600s; available only in REST API.
- **Why the others are wrong:** A — it is enabled per stage (not "method level only"), and the default TTL is 300s, not 3600. B — HTTP API does NOT have caching. D — the cache lives at API Gateway, not on the client.
- 🧠 **Key point / trap:** Remember the numbers: caching is per **stage**, default TTL **300s** (max 3600s). Caching is REST-only.
- 📎 Source: README "MUST REMEMBER" (caching enabled per stage, TTL 300s).

### Question 13 — Answer: **B**
- **Why correct:** The integration timeout **defaults to 29s** and can be **increased up to 300s** via Service Quotas for **Regional/private REST APIs** (in exchange for a lower throttle quota); long-running tasks should still be async (return `202`, process in the background).
- **Why the others are wrong:** A — it is not "fixed" at 29s; it can be raised to 300s. C — HTTP API CANNOT raise the timeout (it stays at 29s), and this also does not apply to an edge-optimized REST API. D — caching is unrelated to a long-running backend timeout.
- 🧠 **Key point / trap:** 29s (default) → 300s (Regional/private REST via Service Quotas). Does NOT apply to edge-optimized REST or HTTP API.
- 📎 Source: README "MUST REMEMBER" + "Exam traps" (timeout 29s/300s).

### Question 14 — Answer: **C**
- **Why correct:** With a **proxy integration** (Lambda/HTTP proxy), API Gateway does not use integration responses, so the **backend (Lambda function) must return** the CORS headers in its response. Clicking "Enable CORS" alone is not enough for proxy.
- **Why the others are wrong:** A — do not delete `OPTIONS`; preflight still needs it. B — CORS can be configured on both REST and HTTP API. D — caching is unrelated to CORS.
- 🧠 **Key point / trap:** "Enabled CORS on proxy but still blocked" = Lambda has not returned the CORS headers. (For non-proxy, the `OPTIONS` preflight is handled by a Mock integration that returns the three headers.)
- 📎 Source: `resources/apigw-cors.md` (proxy: backend is responsible for returning the headers).

### Question 15 — Answer: **B**
- **Why correct:** A presigned URL with the **`PUT`** method lets a third party upload directly to S3 **without AWS credentials** and **without changing the bucket policy**.
- **Why the others are wrong:** A — handing an access key to each user exposes credentials, violating the requirement. C — public write is a severe security risk. D — CloudFront signed cookies are for distributing (downloading) many private files, not for uploading to S3.
- 🧠 **Key point / trap:** "let outsiders upload directly, without leaking keys" → presigned URL (PUT). For download use the `GET` method.
- 📎 Source: `resources/s3-presigned-url.md` (PUT to upload; the recipient needs no credentials).

### Question 16 — Answer: **C**
- **Why correct:** A presigned URL inherits the permissions of the **IAM principal that created** it; the SigV4 limit with an IAM user is up to **7 days**; if signed with **temporary credentials** (STS/role/instance profile) the URL expires with the credentials (even if a longer expiry is set).
- **Why the others are wrong:** A — it always has an expiry, never indefinite. B — 12h is only the limit when created through the **Console**; CLI/SDK go up to 7 days. D — the creator must have permission to perform the operation (e.g. `s3:GetObject`) for the URL to work.
- 🧠 **Key point / trap:** Three commonly trapped numbers: Console 12h · CLI/SDK 7 days · temp credentials → expires with the credentials (STS default 1h, EC2 role ~6h).
- 📎 Source: `resources/s3-presigned-url.md` (Who can create; Expiration time).

### Question 17 — Answer: **B**
- **Why correct:** multipart upload is **recommended when > 100 MB** and **required when > 5 GB** (a single `PutObject` is capped at 5 GB); benefits: parallel upload (high throughput) and retrying only the failed part on a flaky network.
- **Why the others are wrong:** A — a single `PutObject` is capped at **5 GB** (an object can be up to 5 TB, but an 8 GB file cannot be PUT in one call). C — compressing the file is a forced workaround, not the correct nature of the problem. D — Transfer Acceleration optimizes the transport path; it does not replace multipart's role for files > 5 GB.
- 🧠 **Key point / trap:** Object max **5 TB**; single PUT max **5 GB**; multipart recommended **>100 MB**, required **>5 GB**.
- 📎 Source: `resources/s3-multipart-upload.md`; README "MUST REMEMBER".

### Question 18 — Answer: **A, B**
- **Why correct:** A — uploaded parts are **still billed** until Complete/Abort; set a lifecycle rule `AbortIncompleteMultipartUpload`. B — you must store the **part number + `ETag`** yourself to include in the Complete request, NOT taken from the result of `ListParts`.
- **Why the others are wrong:** C — part numbers **do not need to be consecutive** (except with checksums), and **re-uploading the same part number overwrites it**. D — S3 does **not** automatically abort incomplete multipart uploads (there is no expiry) → you must use a lifecycle rule. E — multipart is for large objects (recommended >100 MB), not "under 100 MB".
- 🧠 **Key point / trap:** Leftover parts silently cost money → always set an Abort lifecycle rule. Numbers: part number **1–10,000**, `ListParts`/`ListMultipartUploads` return up to **1,000** per call.
- 📎 Source: `resources/s3-multipart-upload.md` (pricing; complete needs part#+ETag; lifecycle).

### Question 19 — Answer: **C**
- **Why correct:** `SSE-KMS` integrates with AWS KMS → **auditing through CloudTrail**, key **rotation**, and control of key usage by policy.
- **Why the others are wrong:** A — `SSE-S3` (AES-256 managed by AWS) does not audit per key. B — `SSE-C` is customer-held keys, with no AWS-managed audit/rotation. D — a client-side static key embedded in the app is an anti-pattern and does not meet audit/rotation.
- 🧠 **Key point / trap:** "audit who uses the key + rotate + control key permissions" → `SSE-KMS` (not `SSE-S3`).
- 📎 Source: `resources/s3-server-side-encryption.md` (SSE-KMS: track keys in CloudTrail).

### Question 20 — Answer: **A, B**
- **Why correct:** A — since Jan 2023, `SSE-S3` is the **automatic, default** baseline encryption for every new object, at no cost. B — with `SSE-C` the customer **provides the key** on each request, and S3 does not store the key.
- **Why the others are wrong:** C — you **cannot** apply two SSE types to the same object at once (the four options are mutually exclusive). D — `SSE-S3` does not allow per-key auditing (that is `SSE-KMS`). E — changing the default encryption does **NOT** re-encrypt existing objects (use `S3 Batch Operations` + `S3 Inventory`).
- 🧠 **Key point / trap:** SSE-S3 = automatic default (2023). SSE-C = customer holds the key. Changing the default is not retroactive for existing objects.
- 📎 Source: `resources/s3-server-side-encryption.md` (Jan 2023 default; SSE-C; Batch Operations).

### Question 21 — Answer: **A, B**
- **Why correct:** Valid destinations of an S3 event notification are Lambda, SQS, SNS, and EventBridge. A and B are both on this list.
- **Why the others are wrong:** C — you cannot invoke EC2 directly. D — you cannot write to RDS directly. E — you cannot invoke Step Functions directly (it must go through an intermediary such as EventBridge/Lambda).
- 🧠 **Key point / trap:** Remember the four destinations: **Lambda / SQS / SNS / EventBridge**. EventBridge is the "bridge" to reach other targets (such as Step Functions).
- 📎 Source: README "MUST REMEMBER" (S3 event notification destinations).

### Question 22 — Answer: **B**
- **Why correct:** S3 now provides **strong read-after-write consistency** for all operations (PUT/GET/LIST) — a read right after a write always sees the latest data, with no retry needed.
- **Why the others are wrong:** A — this describes the old (eventual consistency) behavior, which is outdated. C/D — strong consistency does not depend on versioning or AZ.
- 🧠 **Key point / trap:** Do not pick the "eventual / must retry" answer — S3 already has global strong consistency for every object.
- 📎 Source: README "S3 for Developers" item 6 + "MUST REMEMBER" (strong read-after-write).

### Question 23 — Answer: **D**
- **Why correct:** CloudFront **signed cookies** grant access to **many files** at once while **keeping the original URLs** — suitable for a whole media/HLS library.
- **Why the others are wrong:** A — a signed URL grants access to **one file**, requiring you to sign each file (against the requirement). B — an S3 presigned URL is also typically per-object and goes straight to S3, not through the edge. C — a public bucket breaks the private requirement.
- 🧠 **Key point / trap:** **Many files / keep the original URLs** → signed cookies. **One file** → signed URL. (Both are signed with a trusted key group.)
- 📎 Source: README "CloudFront" item 7 (signed URL vs signed cookies).

### Question 24 — Answer: **A, B**
- **Why correct:** A — `OAC` supports S3 origins encrypted with `SSE-KMS` (a weakness of `OAI`) and works in every region. B — the bucket policy only allows CloudFront via OAC → users cannot access S3 directly.
- **Why the others are wrong:** C — on the contrary, `OAC` locks the bucket **private** for CloudFront only. D — `OAC` is not limited to `us-east-1`. E — `OAC` has nothing to do with enabling/disabling HTTPS.
- 🧠 **Key point / trap:** "lock the bucket so only CloudFront can read" → `OAC` (current recommendation, replaces `OAI`, supports `SSE-KMS`).
- 📎 Source: README "CloudFront" item 7 (OAC replaces OAI).

### Question 25 — Answer: **B**
- **Why correct:** A CloudFront signed URL goes **through the edge/cache** (fast, near users, global scale) and is signed with a **trusted key group/key pair**; while an S3 presigned URL accesses **S3 directly**, inheriting the IAM permissions of the identity that created the URL, suitable for temporary upload/download.
- **Why the others are wrong:** A — the description is reversed (it is the presigned URL that goes straight to S3). C — the bucket does not need to be public (combine with OAC). D — a CloudFront signed URL is used to distribute/download content, not limited to "upload only".
- 🧠 **Key point / trap:** presigned = **straight to S3**, temporary; CloudFront signed = **through the CDN**, global-scale private.
- 📎 Source: README "CloudFront" item 7 (S3 presigned vs CloudFront signed URL).

### Question 26 — Answer: **C**
- **Why correct:** `CreateInvalidation` clears the cache by path before the TTL expires (first 1,000 paths/month free); the long-term best practice is **versioned object names** (rename the file, e.g. `app.v2.js`) so you never have to invalidate.
- **Why the others are wrong:** A — deleting/recreating the distribution is overkill and causes an outage. B — TTL=0 permanently kills the caching benefit entirely. D — switching the origin to an HTTP API is unrelated.
- 🧠 **Key point / trap:** Push new content before TTL = invalidation; but versioned filenames are the "clean" and cheap long-term approach.
- 📎 Source: README "CloudFront" item 7 (Cache invalidation).

### Question 27 — Answer: **D**
- **Why correct:** AWS AppSync (GraphQL) offers a single endpoint where the client **selects exactly the fields it needs** (avoiding over-/under-fetch) and aggregates multiple data sources.
- **Why the others are wrong:** A/B — API Gateway REST/HTTP is a fixed-endpoint REST model, prone to over-/under-fetch. C — CloudFront + S3 is static content distribution, not a flexible query API.
- 🧠 **Key point / trap:** "flexible query / field selection / real-time" → AppSync (GraphQL). "traditional REST" → API Gateway.
- 📎 Source: README "AppSync" item 8 (compared with API Gateway).

### Question 28 — Answer: **A, B**
- **Why correct:** A — a resolver (VTL/JS) connects a GraphQL field to a data source such as DynamoDB/Lambda/HTTP. B — a subscription pushes real-time data to the client over WebSocket when something changes.
- **Why the others are wrong:** C — AppSync supports multiple data sources (DynamoDB, Lambda, HTTP, ...), not just DynamoDB. D — AppSync supports authorization with a Cognito User Pool / IAM / API key / Lambda authorizer (OIDC). E — AppSync is a managed **GraphQL** service, not REST.
- 🧠 **Key point / trap:** AppSync = managed GraphQL: resolvers (multiple data sources) + subscriptions (real-time WebSocket) + multiple authorization modes.
- 📎 Source: README "AppSync" item 8.
