# 📝 Practice Questions — Week 1: Developer Foundations — AWS SDK/CLI + Lambda Basics

> **22 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Week 1 material.
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
