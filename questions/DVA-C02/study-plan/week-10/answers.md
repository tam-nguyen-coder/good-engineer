# ✅ Answers & Explanations — Week 10 (Cross-Domain Cumulative Mock)

> Open only after you have attempted every question in [questions.md](questions.md) under a timed ~50 minutes.
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-C · 2-B · 3-A · 4-D · 5-B · 6-C · 7-A · 8-D · 9-BD · 10-B · 11-AC · 12-C · 13-A · 14-D · 15-CE · 16-B · 17-AB · 18-C · 19-BD · 20-A · 21-B · 22-D · 23-AC · 24-C · 25-BE

> 📊 **After grading, scroll to the [Per-domain score analysis](#-per-domain-score-analysis)** to see which domain is weak and which week to revisit.

---

### Question 1 — Answer: **C**
- **Why correct:** Asynchronous invocation (`Event`) has a **1 MB payload limit** (raised from 256 KB), so the 2 MB payload is **rejected immediately**. Large payloads → store them in S3 and pass a **reference** (the key). Asynchronous failures are retried only **twice** and then dropped, so retaining failed events requires an **on-failure destination** or a **DLQ**.
- **Why the others are wrong:** A — 6 MB is the **synchronous** limit, and async retries only twice, not indefinitely. B — 256 KB is the **outdated** figure; switching to synchronous is not how you handle large payloads or failed events. D — you **cannot** raise the async payload limit to 6 MB; 6 MB applies only to synchronous invocation.
- 🧠 **Key point / trap:** async = **1 MB** (not 256 KB) · sync = **6 MB** · async retries **twice** → DLQ/destinations. Large payload → S3 + pointer.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (Lambda) + §6; Week 2 `README.md`.

### Question 2 — Answer: **B**
- **Why correct:** The standard cross-account pattern is to create an **IAM role** in Account B with a **trust policy** allowing the principal (the Lambda execution role in Account A) to call `sts:AssumeRole`. The function calls `AssumeRole` → receives **temporary credentials** → accesses the table. No long-term key, and least privilege comes from the role's permission policy.
- **Why the others are wrong:** A — an IAM user + access key is a **long-term credential**, which violates the requirement. C — `AssumeRoleWithWebIdentity`/identity pools are for user federation (web/mobile), not cross-account service-to-service access. D — `GetSessionToken` only re-issues credentials for the **same identity** (usually with MFA); it is **not** used to obtain permissions in another account.
- 🧠 **Key point / trap:** "cross-account / assume role / temporary credentials" → **STS `AssumeRole` + trust policy**. `GetSessionToken` = MFA/same-account, NOT cross-account.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (IAM+STS), §7; Week 6 `README.md`.

### Question 3 — Answer: **A**
- **Why correct:** **Canary** = shift **part** of the traffic (10%), then after a **wait interval** (5 minutes) shift **all** the rest → exactly matches the description. CodeDeploy performs the traffic shift via a **weighted Lambda alias** and uses a **CloudWatch alarm** for **automatic rollback**.
- **Why the others are wrong:** B — **Linear** increases **in equal increments** (e.g. 10% every 5 minutes up to 100%), not "10% then jump to 100%". C — Traffic splitting belongs to Elastic Beanstalk — wrong context (the question is about Lambda + CodeDeploy). D — `AllAtOnce` has no traffic shifting; reserved concurrency is unrelated.
- 🧠 **Key point / trap:** **Canary** = 2 steps (x% → the rest). **Linear** = multiple equal increments. Both belong to **CodeDeploy** for Lambda/ECS and use a weighted alias.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (CI/CD); Week 8 `README.md`.

### Question 4 — Answer: **D**
- **Why correct:** **Optimistic locking**: add a `version` attribute, and on each write use a **conditional write** with a `ConditionExpression` checking that `version` still matches what you read; if someone wrote in between (version changed) → the condition fails → retry with backoff. Prevents lost updates, low cost, no pessimistic lock needed.
- **Why the others are wrong:** A — `TransactWriteItems` does **not lock the table**, costs **2× WCU**, and is overkill for protecting a single item. B — DynamoDB Streams does **not serialize** concurrent writes (it only emits events after a write). C — `Scan` is extremely expensive and does **not** prevent the race condition (a read-before-write can still be interleaved).
- 🧠 **Key point / trap:** "prevent lost updates / concurrent writes to the same item, low cost" → **optimistic locking (version) + conditional write**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (DynamoDB); Week 3 `README.md`.

### Question 5 — Answer: **B**
- **Why correct:** **Annotations** are **indexed** → you can **filter/group** on the service map and in trace queries. **Metadata** is **not** indexed (not searchable) but can hold a large payload for debugging. This matches the need exactly: `customerId`/`tier` as annotations, the payload as metadata.
- **Why the others are wrong:** A — cramming everything into annotations is wasteful and there is a limit on the number of indexed annotations. C — metadata cannot be filtered → you cannot search by customerId. D — filtering by subsegment name does not satisfy filtering by a `customerId` value; putting the payload in an annotation is the wrong role.
- 🧠 **Key point / trap:** **Annotation = indexed = filterable**; **Metadata = not indexed = for viewing/debugging only**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (X-Ray), §7; Week 9 `README.md`.

### Question 6 — Answer: **C**
- **Why correct:** `KMS` `Encrypt` directly accepts only **≤ 4 KB**, so 50 MB **must** use **envelope encryption**: `GenerateDataKey` returns a **plaintext data key** + an **encrypted data key**; encrypt the data **locally** with the plaintext key, store the encrypted data key alongside the object, and **delete** the plaintext key from RAM. Few KMS calls, and the data key is never stored in plaintext.
- **Why the others are wrong:** A — exceeds the 4 KB limit, invalid. B — splitting into 4 KB and calling Encrypt tens of thousands of times is expensive and impractical. D — SSE-C makes the **client manage/supply the key** on every request (high overhead) and is not the "KMS CMK envelope" model the question requires.
- 🧠 **Key point / trap:** "encrypt data > 4 KB with KMS" → **envelope encryption / `GenerateDataKey`**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (KMS), §6; Week 7 `README.md`.

### Question 7 — Answer: **A**
- **Why correct:** The requirement "real-time + per-key ordering + **multiple independent consumers with full throughput** + **replay**" is the profile of Amazon Kinesis Data Streams. Partition key = `userId` preserves per-user ordering; **enhanced fan-out** gives each consumer its own 2 MB/s per shard; retention (24h → 365 days) allows the 3-day replay.
- **Why the others are wrong:** B — SQS FIFO has **no replay** and each message is received by only one consumer (not multiple independent consumers reading the same data). C — SNS+SQS is fan-out but has **no replay / no shard-based ordered streaming per key**. D — Firehose is near-real-time, has **no replay**, and is not a real-time multi-consumer service.
- 🧠 **Key point / trap:** "ordered + multiple consumers + replay + real-time" → **Kinesis Data Streams** (enhanced fan-out for per-consumer throughput).
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (messaging), §7; Week 5 `README.md`.

### Question 8 — Answer: **D**
- **Why correct:** **Immutable** builds **entirely new instances** in a **temporary** Auto Scaling group and swaps them in only after they all pass health checks; if the deployment fails → the running instances are **never touched** → safest, zero-downtime, at the cost of temporarily doubling capacity.
- **Why the others are wrong:** A — All at once has **downtime** and updates in place. B — Traffic splitting is a **canary %** (requires an ALB), not "build all new, don't touch old". C — Rolling with additional batch still **mutates the running instances** in batches. *(Note: Blue/Green is NOT a Beanstalk deployment policy — it is a CNAME-swap technique between two environments.)*
- 🧠 **Key point / trap:** "build a completely new environment/instances, don't touch the old, zero-downtime" → **Immutable**. The 5 Beanstalk policies = All at once / Rolling / Rolling+additional batch / Immutable / **Traffic splitting**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (Elastic Beanstalk); Week 8 `README.md`.

### Question 9 — Answer: **B, D**
- **Why correct:** B — **Provisioned concurrency** keeps warm environments ready → **eliminates cold starts** at baseline (right for latency-sensitive). D — **Reserved concurrency** sets a **cap** on the function's concurrency → guarantees it never exceeds `N` → **protects RDS** behind it.
- **Why the others are wrong:** A — **SnapStart CANNOT be used together** with provisioned concurrency on the same function (their benefits do not add up). C — increasing memory reduces the init/CPU portion but does **not eliminate** cold starts. E — provisioned concurrency can only be configured on a **published version/alias**, **not** on `$LATEST`.
- 🧠 **Key point / trap:** eliminate cold starts (guaranteed) → **provisioned concurrency**; cap/guarantee a concurrency ceiling → **reserved concurrency**. SnapStart (Java/Python/.NET) is *best-effort*, version/alias only, and does **not** combine with provisioned concurrency.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (Lambda), §7; Week 2 `README.md`.

### Question 10 — Answer: **B**
- **Why correct:** Secrets Manager has built-in **automatic rotation** integrated with RDS (an AWS-provided Lambda rotation function) → 30-day rotation with no code change. **Non-sensitive** config goes in SSM Parameter Store Standard (`String`) — the standard tier is **free** → cost-optimal.
- **Why the others are wrong:** A — hard-coding credentials is an anti-pattern, and manual rotation is not automatic. C — Parameter Store has **no** "free built-in RDS rotation" (automatic rotation belongs to Secrets Manager). D — putting the **non-sensitive config** in Secrets Manager as well incurs **unnecessary cost** (each secret is billed) → not cost-optimal.
- 🧠 **Key point / trap:** "rotate credentials automatically (RDS)" → **Secrets Manager**; "config/plaintext, free" → **Parameter Store (Standard)**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §4 (Task 2.3), §7; Week 7 `README.md`.

### Question 11 — Answer: **A, C**
- **Why correct:** A — the **`reports`** section in `buildspec.yml` declares a report group for CodeBuild to surface test results. C — the **`cache`** section (S3 or local backend) keeps dependencies (e.g. Maven's `~/.m2`) between builds → faster builds.
- **Why the others are wrong:** B — the password should **not** go in `env/variables` as plaintext; use `env/secrets-manager` (or `parameter-store`). D — CodeBuild has **no `deploy` phase**; the phases are `install → pre_build → build → post_build`. E — `buildspec.yml` lives at the repo **root** by default, not in `.aws/`.
- 🧠 **Key point / trap:** `buildspec.yml` phases = **install/pre_build/build/post_build** (no `deploy`); secrets via **`env/secrets-manager`** or **`env/parameter-store`**, not plaintext; file at the **root**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (CI/CD); Week 8 `README.md`.

### Question 12 — Answer: **C**
- **Why correct:** `ProvisionedThroughputExceededException` **despite total capacity headroom** + traffic concentrated on one item = a **hot partition**: capacity is spread across partitions, so one "hot" partition key throttles locally. Remediate with **write sharding** (add a suffix to spread the key), use **DAX** to cache the hot item for reads, and **exponential backoff** for throttled requests.
- **Why the others are wrong:** A — total capacity already has headroom, so doubling it wastes money and stays locally hot. B — a GSI has its own throughput but does **not** solve a hot key on the item itself; DAX/sharding is the fix. D — changing consistency does not fix a hot write/partition.
- 🧠 **Key point / trap:** throttling "despite spare capacity" → suspect a **hot partition** → **spread the key + DAX + backoff**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (DynamoDB), §7; Week 3/Week 9 `README.md`.

### Question 13 — Answer: **A**
- **Why correct:** For a **Regional (and private) REST API**, the default **29s** integration timeout can be **raised up to 300s** via Service Quotas (you may need to lower the corresponding throttle quota). 90s < 300s, so it is valid, and this is the **smallest** change because it keeps the synchronous model.
- **Why the others are wrong:** B — "cannot exceed 29s" is **outdated**; Regional REST can go up to 300s. C — caching does not help the first call, which still takes 90s. D — **HTTP API** integration timeout maxes out at **30s** and **cannot** be raised → switching to HTTP API does not solve it.
- 🧠 **Key point / trap:** the 300s timeout is **only** for **Regional/private REST APIs**, NOT for **edge-optimized REST** & **HTTP API**. Truly long tasks → still go async.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (API Gateway), §6; Week 4 `README.md`.

### Question 14 — Answer: **D**
- **Why correct:** Signing in (Google) = **authentication** → use a Cognito user pool/federation to get a token; to call an **AWS service directly** (`s3:PutObject`) from the device you need **AWS credentials** → the Cognito identity pool **exchanges the token for temporary credentials** via STS, mapped to an IAM role with limited permissions.
- **Why the others are wrong:** A — a **JWT is not** used to call S3 directly (S3 needs SigV4/AWS creds). B — an identity pool **authorizes but does not authenticate** (it does not sign in with Google or issue a JWT itself). C — a Lambda authorizer only **authorizes requests to API Gateway**; it does not issue AWS credentials to the client.
- 🧠 **Key point / trap:** "client calls an AWS service directly / needs AWS credentials" → **identity pool**. "app sign-in / returns a JWT" → **user pool**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (Cognito), §7; Week 6 `README.md`.

### Question 15 — Answer: **C, E**
- **Why correct:** C — the standard way to share values cross-stack is: Stack A declares `Outputs` + **`Export`**, and Stack B uses **`Fn::ImportValue`**. E — `DeletionPolicy: Retain` keeps the stateful resource (e.g. a DB) **from being deleted** when the stack is deleted.
- **Why the others are wrong:** A — `Fn::ImportValue` **requires** the value to have been `Export`ed beforehand. B — nested stacks are **not** the only way; Export/ImportValue is another common way. D — `DependsOn` only orders resources **within the same stack**; it does not share values between two separate stacks.
- 🧠 **Key point / trap:** cross-stack = **`Export` (Outputs) + `Fn::ImportValue`**; prevent resource deletion = **`DeletionPolicy: Retain`/`Snapshot`**. If a value is exported and still imported → the source stack **cannot be deleted**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (CloudFormation); Week 8 `README.md`.

### Question 16 — Answer: **B**
- **Why correct:** A **long (several hours)** workflow needing **exactly-once**, branching (`Choice`), per-step **Retry/Catch**, and compensation → Step Functions **Standard** (runs up to **1 year**, exactly-once, with visual + audit history). ASL expresses `Choice`/`Retry`/`Catch`.
- **Why the others are wrong:** A — **Express** is limited to **5 minutes**, is **at-least-once**, and suits short/high-volume workloads → not a fit for "several hours + exactly-once". C — a chain of directly-invoking Lambdas is hard to orchestrate for retry/catch/compensation and is fragile. D — EventBridge is scheduling/routing, not stateful orchestration.
- 🧠 **Key point / trap:** "multi-step orchestration, retry/catch, long, exactly-once" → **Step Functions Standard**. Express = short (≤5 min) + high-volume + at-least-once.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (Step Functions), §7; Week 5 `README.md`.

### Question 17 — Answer: **A, B**
- **Why correct:** A — Lambda allocates **CPU (and network) proportional to memory**; for a **CPU-bound** workload, raising memory to the sweet spot usually runs much faster → **reduces both duration and total cost**. B — **Lambda Power Tuning** (a sample state machine) automatically measures multiple memory levels to find the best cost/performance point.
- **Why the others are wrong:** C — dropping to 128 MB → less CPU → slower, usually **increasing** total cost (runs longer). D — provisioned concurrency reduces **cold starts**, not CPU processing speed. E — async invocation only changes the invocation type; it does **not** make the processing itself faster.
- 🧠 **Key point / trap:** slow/expensive CPU-bound → **increase memory (⇒ CPU)** + use **Power Tuning** to find the optimum. "Reduce memory to save money" is the classic trap.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §4 (Task 4.3), §5 (Lambda); Week 9 `README.md`.

### Question 18 — Answer: **C**
- **Why correct:** The need for **an audit of each key use** (CloudTrail) + **rotation** you control → **SSE-KMS** with a **customer managed key**: each encrypt/decrypt operation produces a CloudTrail log, and you enable automatic rotation. S3 automatically applies encryption to every new object → least code change.
- **Why the others are wrong:** A — S3 **encrypts by default** (SSE-S3) since 2023; but the requirement is key-usage auditing, which needs KMS. B — **SSE-C**: the client holds/supplies the key on each request (high overhead) and there is **no** server-side CloudTrail key-usage log. D — **SSE-S3** does **not** allow auditing each key use or rotation you configure (AWS manages the key).
- 🧠 **Key point / trap:** "audit who/when a key is used + controllable rotation" → **SSE-KMS (CMK)**. SSE-S3 = default, no key-usage audit; SSE-C = client holds the key.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (S3/KMS), §6; Week 7 `README.md`.

### Question 19 — Answer: **B, D**
- **Why correct:** B — for SQS, the ESM makes the **Lambda service poll** the queue; if a batch fails, the message returns to the queue after the visibility timeout, and past `maxReceiveCount` it goes to the **queue's DLQ**. D — for DynamoDB Streams/Kinesis, the ESM reads **by shard, preserving order within the shard**; a single failing record can **block the whole shard** (poison) → use `BisectBatchOnFunctionError`, `MaximumRetryAttempts`, and an on-failure destination to handle it.
- **Why the others are wrong:** A — the SQS ESM is **poll**-based, not push. C — "only supports synchronous invocation with a 6 MB asynchronous payload" is nonsensical/wrong. E — the DLQ for a stream is **not** configured on a "source SQS queue"; streams use an on-failure destination (SQS/SNS) via the ESM.
- 🧠 **Key point / trap:** ESM = **poll-based** (SQS/Kinesis/DynamoDB Streams). Streams preserve **order per shard** → a poison record blocks the shard → `BisectBatchOnFunctionError` + retry cap + destination.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (Lambda); Week 2 `README.md`.

### Question 20 — Answer: **A**
- **Why correct:** **Stage variables** act like a stage's environment variables; put one in the Lambda integration URI (e.g. `...:function:myFn:${stageVariables.lambdaAlias}`) so each stage (`dev`/`prod`) points to the corresponding **Lambda alias** — no need to modify or duplicate the API.
- **Why the others are wrong:** B — 2 separate APIs is redundant and hard to manage (the question wants 1 API). C — usage plans/API keys are for **throttling/quotas** per client, not for choosing a backend by stage. D — a Lambda env var belongs to each version/alias; it is not a mechanism for API Gateway to select an alias by stage.
- 🧠 **Key point / trap:** "1 API, each stage points to a different backend/alias" → **stage variables** (combined with Lambda aliases).
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (API Gateway); Week 4 `README.md`.

### Question 21 — Answer: **B**
- **Why correct:** IAM evaluation order: **explicit `Deny` > explicit `Allow` > implicit `Deny`**. A single explicit Deny (from an SCP or bucket policy) is enough to **block** `DeleteObject`, regardless of the identity policy allowing `s3:*`.
- **Why the others are wrong:** A — Allow cannot beat Deny. C — statement order within a policy does **not** matter (it is not "first match wins"); Deny always wins. D — MFA does not override an explicit Deny (unless the Deny has a specific MFA condition, which is not stated here).
- 🧠 **Key point / trap:** **Explicit Deny always wins.** A Deny in an SCP/bucket policy → blocked, even with a broad identity Allow.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (IAM), §4 (Task 2.1); Week 6 `README.md`.

### Question 22 — Answer: **D**
- **Why correct:** **EMF (Embedded Metric Format)** lets you write structured logs so CloudWatch **extracts metrics from the logs automatically** (including high-cardinality dimensions like merchant) — no synchronous `PutMetricData` calls → **no added latency/API cost** in the processing path.
- **Why the others are wrong:** A — synchronous `PutMetricData` adds latency, can be throttled, and consumes calls. B — detailed monitoring only increases the granularity of system metrics; it does not create a business metric. C — an **X-Ray annotation is not a CloudWatch metric** (you cannot measure/alarm on it as a metric).
- 🧠 **Key point / trap:** "custom/business metric from Lambda without synchronous PutMetricData" → **EMF**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (CloudWatch), §4 (Task 4.2); Week 9 `README.md`.

### Question 23 — Answer: **A, C**
- **Why correct:** A — a **GSI** uses a different partition key (`email`), **can be created after the table exists**, has its own throughput, and is **eventually consistent only** → a fit (the question does not need strong reads). C — an **LSI** must be created **at table creation** and **shares the partition key** with the table → cannot be used to query by `email` on an existing table.
- **Why the others are wrong:** B — a GSI is **only** eventually consistent, no strong reads. D — an LSI **shares throughput** with the table and can **only** be created at table creation (not at any time, not with its own throughput). E — a `Query` (including on a GSI) returns at most **1 MB** per page (not 4 MB).
- 🧠 **Key point / trap:** **GSI** = different key, create anytime, own throughput, eventual. **LSI** = same partition key, create at table creation, shared throughput, supports strong. Query = **1 MB/page**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (DynamoDB), §6; Week 3 `README.md`.

### Question 24 — Answer: **C**
- **Why correct:** `sam local start-api` stands up a **local** API Gateway endpoint to test HTTP, and `sam local invoke -e event.json` runs the function with a **mock event** → exactly the need to test locally before deploying.
- **Why the others are wrong:** A — `sam deploy --guided` deploys to the **cloud**, not local testing. B — `sam build` only packages/compiles; it does not run an endpoint. D — `sam sync` fast-syncs to the cloud (dev loop); it does not run local unit tests.
- 🧠 **Key point / trap:** local SAM testing → **`sam local invoke`** / **`sam local start-api`**. `sam build/deploy/sync` package or push to the cloud.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (SAM), §4 (Task 3.2); Week 8 `README.md`.

### Question 25 — Answer: **B, E**
- **Why correct:** B — a KMS customer managed key now supports a **custom rotation period** (not fixed at 1 year) and **on-demand rotation** (rotate **immediately** on suspected exposure). E — **multi-Region keys** let you replicate the same **key material** across multiple regions → cross-region encrypt/decrypt with no re-encryption.
- **Why the others are wrong:** A — rotation is **not** fixed at 90 days; the default is ~1 year and is **customizable** + on-demand. C — direct `Encrypt` is at most **4 KB**, not 4 MB. D — **AWS managed keys** do **not** let you write your own key policy and do **not** support on-demand rotation (they rotate automatically, typically yearly) — only a **customer managed key** is that flexible.
- 🧠 **Key point / trap:** CMK = **custom rotation period + on-demand rotation**; same key across regions → **multi-Region keys**. Direct Encrypt = **4 KB**.
- 📎 Source: `DVA-C02-STUDY-PLAN.md` §5 (KMS), §6; Week 7 `README.md`.

---

## 📊 Per-domain score analysis

This is a **cross-domain** mock weighted like the real exam. After grading, **count the number correct per domain** and compare against the table below. Any domain **below the threshold** → **go back to the matching week** and review before attempting the full 65-question mock.

| Domain | Questions in this set | Count | Safe threshold (≥85%) | If many wrong → go back to |
|---|---|---|---|---|
| **D1 — Development (32%)** | 1, 4, 7, 9, 13, 16, 19, 23 | **8** | correct ≥ 7/8 | **Weeks 1–5** (Lambda: W1–W2, DynamoDB: W3, API GW/S3: W4, Messaging/Step Functions/Cache: W5) |
| **D2 — Security (28%)** | 2, 6, 10, 14, 18, 21, 25 | **7** | correct ≥ 6/7 | **Weeks 6–7** (IAM/STS/Cognito: W6; KMS/Secrets/Parameter Store/Encryption: W7) |
| **D3 — Deployment (24%)** | 3, 8, 11, 15, 20, 24 | **6** | correct ≥ 5/6 | **Week 8** (CI/CD Code*, CloudFormation/SAM, Beanstalk, ECS/ECR) |
| **D4 — Troubleshooting & Optimization (16%)** | 5, 12, 17, 22 | **4** | correct ≥ 3/4 | **Week 9** (CloudWatch, X-Ray, Lambda/DynamoDB optimization) |

**Converting your total score (reference, vs. the real threshold):**

| Correct / 25 | % | Meaning |
|---|---|---|
| **≥ 22** | ≥ 88% | 🟢 Solid — meets the personal bar of ≥ 85%; ready for the full 65-question mock. |
| **18–21** | 72–84% | 🟡 Above the pass line (72%) but **without enough safety margin** → drill the low-scoring domain(s). |
| **< 18** | < 72% | 🔴 Below the pass line → **go back to the week(s) of the weakest domain(s)**, redo, then mock again. |

**How to use this for self-remediation:**
1. **Only 1 low domain** → spend 1–2 sessions drilling that exact week (table above), then redo the questions you missed in this mock.
2. **Multiple low domains / total < 72%** → apply the Week 10 **safety valve**: if a full mock is < 75%, **push the exam date back 1 week** and focus on the weakest domain first.
3. **Wrong because of a number** (async payload 1 MB, timeout 300s, item 400 KB, Query 1 MB/page, KMS 4 KB...) → re-read the [§6 numbers table](../../DVA-C02-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng).
4. **Wrong because of the wrong service choice** (SQS vs Kinesis, user pool vs identity pool, Canary vs Linear, Immutable vs Traffic splitting...) → re-read the [§7 keyword-to-service table](../../DVA-C02-STUDY-PLAN.md#7-bảng-phản-xạ-keyword--dịch-vụ).
5. For each memorable miss → **write a 6-section analysis file** in `questions/DVA-C02/` (same workflow as SAA-C03) and review on the **1 / 3 / 7-day** schedule.
