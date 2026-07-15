# ✅ Answers & Explanations — Week 2: AWS Lambda in Depth

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-B · 2-B · 3-A · 4-B · 5-BC · 6-AC · 7-B · 8-B · 9-B · 10-B · 11-B · 12-B · 13-AB · 14-AB · 15-B · 16-A · 17-B · 18-AB · 19-B · 20-B · 21-BD · 22-B · 23-B · 24-B · 25-C · 26-AB

---

### Question 1 — Answer: **B**
- **Why correct:** Publishing a version creates an **immutable snapshot** of the code plus most of the configuration, with its own **qualified numbered ARN** (for example, `...:function:pay:3`). Once published, the code/ARN cannot be changed, so production is "frozen" even as developers keep overwriting `$LATEST`.
- **Why the others are wrong:** A — `$LATEST` is mutable and is overwritten on every deploy, so it is not fixed; S3 versioning is unrelated to the running Lambda version. C — provisioned concurrency only keeps environments warm; it does not lock code. D — reserved concurrency = 0 throttles the function; it does not "lock" code.
- 🧠 **Key point / trap:** "ensure immutable production code" → **publish a version**, not `$LATEST`.
- 📎 Source: `resources/lambda-versions.md` (immutable snapshot, qualified ARN).

### Question 2 — Answer: **B**
- **Why correct:** Lambda publishes a new version only when the **code has changed** relative to the last version; qualifying changes include code, environment variables, runtime, handler, layers, memory, timeout, VPC, DLQ config, SnapStart, and so on. **Reserved concurrency is an operational setting**, and changing it does NOT trigger a version publish.
- **Why the others are wrong:** A — there is no "once per day" limit. C — no memory change is required. D — version numbers increase monotonically and are never reset or reused.
- 🧠 **Key point / trap:** Changing **reserved concurrency** ≠ a qualifying change for publishing a version.
- 📎 Source: `resources/lambda-versions.md` (list of config that qualifies a publish; reserved concurrency does not qualify).

### Question 3 — Answer: **A**
- **Why correct:** An alias is a named pointer to **one version**. Clients call the **alias ARN**; deploying a new version only requires `update-alias` to repoint it, so clients never change the ARN.
- **Why the others are wrong:** B — `$LATEST` is mutable and unsuitable for stable production. C — **an alias cannot point to another alias**; this is a classic trap. D — an S3 presigned URL is unrelated to how a function is invoked.
- 🧠 **Key point / trap:** "change versions while clients keep the same ARN" → **alias**.
- 📎 Source: `resources/lambda-aliases.md` (alias = pointer to a version; update-alias).

### Question 4 — Answer: **B**
- **Why correct:** A **weighted alias** lets one alias split traffic between **exactly two versions**. Set the alias to version 1 (90%) and `AdditionalVersionWeights` for version 2 = `0.10` (10%) → this is canary/blue-green natively within Lambda.
- **Why the others are wrong:** A — using Route 53 plus two functions is overkill and not the Lambda-native approach. C — provisioned concurrency does not split traffic. D — an alias cannot point to another alias.
- 🧠 **Key point / trap:** "canary 10% to the new build" → **weighted alias between two versions**, not deploying two functions.
- 📎 Source: `resources/lambda-aliases.md` (weighted alias / canary); README Session A item 2.

### Question 5 — Answer: **B, C**
- **Why correct:** B — an alias's weighted routing splits between **exactly two versions**. C — you **cannot create an alias from an unqualified ARN**; it must point to a specific version.
- **Why the others are wrong:** A — an alias **cannot point to another alias**. D — an alias does not "split traffic with `$LATEST`"; routing is only between two **published versions**. E — an alias is just a pointer and does **not** hold a copy of the code (the version itself is the immutable copy).
- 🧠 **Key point / trap:** Alias = pointer → version (up to two versions for weighted); no alias→alias, and not from an unqualified ARN.
- 📎 Source: `resources/lambda-aliases.md`; `resources/lambda-versions.md` (an unqualified ARN cannot create an alias).

### Question 6 — Answer: **A, C**
- **Why correct:** A — layers let you **share dependencies across multiple functions** without repackaging them. C — layers **reduce the deployment package size** because they separate dependencies from the code.
- **Why the others are wrong:** B — layers are unrelated to cold starts (for Go/Rust they can even increase them). D — layers do not change the timeout. E — functions packaged as a **container image cannot use layers**; layers are only for `.zip` functions (loaded into `/opt`).
- 🧠 **Key point / trap:** Layer benefits = reuse + smaller package size; **container images do not use layers**.
- 📎 Source: `resources/lambda-layers.md` (benefits; `/opt`; `.zip` only).

### Question 7 — Answer: **B**
- **Why correct:** Layers **can be used only with functions packaged as `.zip`**. A function packaged as a **container image** must build the runtime and all dependencies into the image itself and cannot attach layers.
- **Why the others are wrong:** A — layers do not automatically attach to a container image. C — there is no "10 layers for an image" limit; and images do not use layers. D — image size does not unlock the layers feature.
- 🧠 **Key point / trap:** Layers ⟺ `.zip`. Container image ⟺ package everything into the image.
- 📎 Source: `resources/lambda-layers.md` ("you can use layers only with .zip"; container: package runtime + deps in the image).

### Question 8 — Answer: **B**
- **Why correct:** Environment variables can be **encrypted with AWS KMS** (using a dedicated customer managed key for the sensitive value). Anyone who wants to decrypt must have `kms:Decrypt` permission on the key, which controls access.
- **Why the others are wrong:** A — `/tmp` is not durable and does not address encrypting the config at rest. C — reserved concurrency is unrelated to variable security. D — total environment variables are limited to **4 KB** (not 40 KB); "adding a salt" is not the protection mechanism here.
- 🧠 **Key point / trap:** Sensitive environment variables → **encrypt with KMS**; remember total env vars ≤ **4 KB**.
- 📎 Source: README Session A item 3; `resources/lambda-quotas-limits.md` (env vars 4 KB).

### Question 9 — Answer: **B**
- **Why correct:** **Reserved concurrency** acts as both a **ceiling** (limiting concurrent instances → protecting the RDS connection pool) and a **dedicated pool** for the function; it also **incurs no additional cost**.
- **Why the others are wrong:** A — provisioned concurrency keeps environments warm (reducing cold starts) but does NOT limit scaling or protect downstream. C — increasing the account limit makes things worse (more scaling). D — reducing the timeout does not control the number of concurrent connections.
- 🧠 **Key point / trap:** "limit scaling to protect downstream + reserve a dedicated pool" → **reserved concurrency**.
- 📎 Source: `resources/lambda-concurrency.md` (reserved = upper & lower bound, protects downstream).

### Question 10 — Answer: **B**
- **Why correct:** **Provisioned concurrency** keeps a set number of **pre-initialized, warm environments** ready → **eliminates cold starts**, delivering double-digit millisecond responses; ideal for a latency-sensitive interactive workload with predictable traffic. Attached to an alias/version.
- **Why the others are wrong:** A — reserved concurrency only sets a ceiling/reserves a pool; it does not address cold starts. C — increasing memory reduces init time somewhat but is not how to "eliminate cold starts" for predictable traffic. D — async is unsuitable for an interactive API that needs an immediate response.
- 🧠 **Key point / trap:** "eliminate cold starts / keep warm for steady traffic" → **provisioned concurrency** (has a cost).
- 📎 Source: `resources/lambda-concurrency.md` (provisioned = pre-initialized, reduces cold starts).

### Question 11 — Answer: **B**
- **Why correct:** The requirement is to reserve a dedicated pool + set a ceiling (not to exceed 50) and it **does not mention cold starts**, while it does require **cost-effectiveness** → **reserved concurrency = 50** (free; both a ceiling and a dedicated floor).
- **Why the others are wrong:** A — provisioned concurrency **has a cost** and solves cold starts (not asked). C — SnapStart reduces cold starts; it does not limit/reserve concurrency. D — changing the account limit for the whole Region affects every function—wrong scope.
- 🧠 **Key point / trap:** No mention of cold starts + needs to be cheap + reserve/limit a pool → **reserved**, do NOT choose provisioned.
- 📎 Source: `resources/lambda-concurrency.md`; README "Common exam traps."

### Question 12 — Answer: **B**
- **Why correct:** Setting **reserved concurrency = 0** fully **throttles** the function so it stops processing all events until the limit is removed—a fast way to "pause" without deleting the function or its trigger.
- **Why the others are wrong:** A — deleting the alias breaks clients; it is not a "pause." C — provisioned concurrency = 0 only means no warm environments are kept; the function STILL runs on demand. D — increasing the timeout does not stop processing.
- 🧠 **Key point / trap:** "fully stop processing events" → **reserved concurrency = 0**.
- 📎 Source: `resources/lambda-concurrency.md` ("set reserved concurrency to 0 to intentionally throttle").

### Question 13 — Answer: **A, B**
- **Why correct:** A — **reducing the package size** makes loading/initialization faster. B — moving **heavy init outside the handler** (create clients, open connections once) leverages warm reuse → reduces init time on the first call.
- **Why the others are wrong:** C — async does not reduce cold starts (the event still needs an initialized environment). D — reserved concurrency sets a ceiling/pool but does NOT keep environments warm, so it does not reduce cold starts. E — a long timeout is unrelated to cold starts.
- 🧠 **Key point / trap:** Free cold-start reduction = leaner package + init outside the handler (+ SnapStart depending on runtime). Provisioned is the "paid" way.
- 📎 Source: README Session A item 5 (ways to reduce cold starts).

### Question 14 — Answer: **A, B**
- **Why correct:** A — SnapStart supports **Java 11+, Python 3.12+, and .NET 8+**. B — SnapStart can be used **only on a published version/alias**, not on `$LATEST`. It is **best-effort** and **free** (unlike provisioned).
- **Why the others are wrong:** C — SnapStart **cannot be used together** with provisioned concurrency. D — SnapStart is **best-effort**, not a "guaranteed" elimination of cold starts like provisioned. E — SnapStart is not limited to container images.
- 🧠 **Key point / trap:** SnapStart = Java/Python/.NET · version/alias only · best-effort · not combined with provisioned.
- 📎 Source: README Session A item 5 (SnapStart); the "MUST REMEMBER" table.

### Question 15 — Answer: **B**
- **Why correct:** Async (`Event`): Lambda **places the event in an internal queue**, returns **`202`** immediately (without waiting for the code), and **retries automatically** on error. Sync (`RequestResponse`): the caller **waits for the result**, and on error the **caller retries** itself.
- **Why the others are wrong:** A — this is reversed. C — async DOES support error handling and destinations. D — sync is 6 MB, async is 1 MB, not both 256 KB.
- 🧠 **Key point / trap:** Async = queue + 202 + Lambda retry; Sync = wait for result + caller retry.
- 📎 Source: `resources/lambda-async-invocation.md`; README Session C item 1.

### Question 16 — Answer: **A**
- **Why correct:** The **async payload limit is 1 MB** and the **sync limit is 6 MB**. 5 MB passes sync but exceeds the 1 MB async limit → error.
- **Why the others are wrong:** B — async is **1 MB**, not 256 KB (the old figure is outdated); and 5 MB passes sync, so it does not "fail with both." C — the limits are reversed—wrong. D — it is not 10 MB; `--cli-binary-format` is unrelated to the payload limit.
- 🧠 **Key point / trap:** ⚠️ Async = **1 MB** (NOT 256 KB), sync = **6 MB**.
- 📎 Source: `resources/lambda-quotas-limits.md` (async 1 MB, sync 6 MB); README "MUST REMEMBER" table.

### Question 17 — Answer: **B**
- **Why correct:** On an async invocation error → Lambda **retries 2 times** (**3 attempts** total); after retries are exhausted, it sends the event to a **DLQ** (SQS/SNS) or to **`OnFailure` destinations** if configured.
- **Why the others are wrong:** A — it is not 5 times. C — Lambda does retry; it does not return directly to S3. D — it does not retry indefinitely.
- 🧠 **Key point / trap:** Async error = **retry 2 times (3 attempts)** → DLQ or `OnFailure` destinations.
- 📎 Source: README Session C item 2; "MUST REMEMBER" table (async retry).

### Question 18 — Answer: **A, B**
- **Why correct:** A — **destinations** support both `OnSuccess` and `OnFailure`; a DLQ receives an event only **on failure**. B — **DLQ**: SQS/SNS; **destinations**: SQS/SNS/Lambda/EventBridge.
- **Why the others are wrong:** C — reversed: **destinations** record more metadata than a DLQ. D — destinations are used for **async** invocation (not sync). E — a DLQ can only target SQS/SNS, not Lambda/EventBridge.
- 🧠 **Key point / trap:** Destinations = more modern (OnSuccess+OnFailure, 4 targets, more metadata); DLQ = OnFailure only, 2 targets.
- 📎 Source: README Session C item 2; "MUST REMEMBER" table (DLQ targets vs. destinations targets).

### Question 19 — Answer: **B**
- **Why correct:** The need is to route **both success and failure** with metadata → use **Lambda destinations** with `OnSuccess` and `OnFailure` pointing to two different SQS queues.
- **Why the others are wrong:** A — a DLQ captures only the failure case, with no OnSuccess. C — a subscription filter is for forwarding logs, not routing invocation records by status. D — concurrency does not route events.
- 🧠 **Key point / trap:** "route both success + failure" → **destinations** (not a DLQ).
- 📎 Source: README Session C item 2 (destinations OnSuccess/OnFailure).

### Question 20 — Answer: **B**
- **Why correct:** With SQS, Lambda uses an **event source mapping** to **poll** the queue and invoke the function in **batches**—this is the correct processing model for a queue.
- **Why the others are wrong:** A — SQS does not "push" directly into Lambda like SNS; Lambda must poll via an ESM. C — provisioned concurrency only keeps environments warm; it does not read SQS. D — this is not how SQS→Lambda integrates; an async 1 MB payload is unrelated.
- 🧠 **Key point / trap:** SQS/Kinesis/DynamoDB Streams → Lambda = **event source mapping (poll)**.
- 📎 Source: `resources/lambda-event-source-mapping.md` (ESM poll + batch; SQS is on the list).

### Question 21 — Answer: **B, D**
- **Why correct:** B (Kinesis Data Streams) and D (DynamoDB Streams) are **stream/queue sources** that use an **event source mapping**—Lambda **polls** records.
- **Why the others are wrong:** A (S3), C (SNS), and E (API Gateway) are **push triggers**—the source service pushes events to Lambda and manages the trigger; they are not ESMs.
- 🧠 **Key point / trap:** ESM (poll) = Kinesis/DynamoDB Streams/SQS/MQ/MSK/Kafka. Push triggers = S3/SNS/API Gateway.
- 📎 Source: `resources/lambda-event-source-mapping.md` (list of ESM sources vs. push triggers).

### Question 22 — Answer: **B**
- **Why correct:** An event source mapping processes records **at least once** → **records may be duplicated**. AWS recommends writing **idempotent** code (unique key, conditional write, and so on) to handle duplicates safely.
- **Why the others are wrong:** A — synchronous invocation does not change the at-least-once nature of an ESM. C — a larger batch size does not remove duplicates; it only groups records. D — provisioned concurrency is unrelated to duplication.
- 🧠 **Key point / trap:** ESM = **at least once** → code must be **idempotent**.
- 📎 Source: `resources/lambda-event-source-mapping.md` ("process each event at least once... make your function idempotent").

### Question 23 — Answer: **B**
- **Why correct:** `/tmp` exists only within the **lifetime of the execution environment** and is **not durable** across invocations (the environment can be reclaimed). To store data durably → Amazon S3 / DynamoDB / Amazon EFS.
- **Why the others are wrong:** A — increasing `/tmp` size (up to 10 GB) does not make it durable. C — `/tmp` is writable (512 MB–10 GB); `/opt` is where layers are extracted, not a durable store. D — provisioned concurrency does not determine `/tmp` durability.
- 🧠 **Key point / trap:** `/tmp` = temporary, **not durable** across invocations → use S3/DynamoDB/EFS for durable data.
- 📎 Source: README Session C item 3; "MUST REMEMBER" table (`/tmp`).

### Question 24 — Answer: **B**
- **Why correct:** A Lambda function in a **private subnet** cannot reach the internet on its own; the Lambda ENI has no public IP. To call the internet, it must route through a **NAT Gateway** placed in a public subnet.
- **Why the others are wrong:** A — you cannot "attach an Internet Gateway directly to the ENI" or assign a public IP to the function. C — disabling the VPC config would also lose access to the internal RDS (which is still required). D — increasing the timeout does not resolve the routing.
- 🧠 **Key point / trap:** "Lambda in a VPC needs internet" → **NAT Gateway**.
- 📎 Source: README Session C item 4 (VPC + NAT Gateway).

### Question 25 — Answer: **C**
- **Why correct:** An unzipped package > **250 MB** or a need for a **custom runtime** → use a **container image** (up to **10 GB** uncompressed).
- **Why the others are wrong:** A — compressing under 50 MB is not feasible with large dependencies; and the 250 MB limit is the **unzipped** size. B — the maximum is **5 layers** and the total unzipped size is still capped at **250 MB**—you cannot get around it. D — `/tmp` is temporary runtime storage, not a place for the deployment package.
- 🧠 **Key point / trap:** Package > 250 MB / custom runtime → **container image (10 GB)**.
- 📎 Source: `resources/lambda-quotas-limits.md` (250 MB unzipped, 10 GB container); README Session C item 4.

### Question 26 — Answer: **A, B**
- **Why correct:** A — the maximum timeout is **900 seconds (15 minutes)**. B — memory is **128 MB → 10,240 MB** (in 1 MB steps).
- **Why the others are wrong:** C — a zip uploaded directly through the API is capped at **50 MB** (not 500 MB); larger uploads go through S3. D — env vars total **4 KB** (not 40 KB). E — a maximum of **5 layers** per function (not 10).
- 🧠 **Key point / trap:** Remember the numbers: 900s · 10,240 MB · 50 MB zip / 250 MB unzip / 10 GB image · env vars 4 KB · 5 layers.
- 📎 Source: `resources/lambda-quotas-limits.md` (quotas table).
