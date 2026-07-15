# ✅ Answers & Explanations — Week 1

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-AC · 4-C · 5-AC · 6-C · 7-B · 8-C · 9-B · 10-B · 11-AD · 12-C · 13-B · 14-B · 15-B · 16-B · 17-B · 18-AB · 19-AB · 20-AB · 21-B · 22-B

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
