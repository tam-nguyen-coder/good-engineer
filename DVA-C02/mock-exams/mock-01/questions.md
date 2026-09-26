# 🎯 DVA-C02 Mock Exam 01 — 65 questions · 130 minutes

> **Exam-realistic full-length mock.** Distribution strictly follows official AWS DVA-C02 domain weights.
> ⏱️ Set a timer for **130 minutes** (~2 minutes per question). No notes, no documentation, no pausing.
> 🔒 Answers, explanations, and per-domain scoring: [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (1 correct out of 4) · `Multi` (choose the stated number of options).
> Tag: `[Domain.Task · Service · Format]`. Domains: `D1` (32% · 21Q) · `D2` (26% · 17Q) · `D3` (24% · 16Q) · `D4` (18% · 11Q).
> 🧰 **Theme of Mock 01: Core Serverless, Data Stores & Security Fundamentals.**
> Back to [mock index](../README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D1.2 · Lambda Concurrency · Single]`
A serverless image processing application uses an AWS Lambda function triggered by Amazon S3 object creation events. During peak marketing campaigns, the function receives an average of 50 invocations per second, and each execution takes an average of 4 seconds to download, resize, and upload the image. The AWS account has a default unreserved concurrency limit of 1,000.
How many concurrent executions will the Lambda function require during peak traffic, and what happens if concurrent requests exceed the function's allocated concurrency?
- A. The function requires 200 concurrent executions. If exceeded, Lambda throttles the additional requests; since S3 is an asynchronous event source, Lambda retains the throttled events in an internal queue and retries them for up to 6 hours.
- B. The function requires 12.5 concurrent executions. If exceeded, S3 immediately drops the events and logs an error to CloudTrail.
- C. The function requires 200 concurrent executions. If exceeded, the Lambda service automatically provisions EC2 instances to absorb the overflow.
- D. The function requires 50 concurrent executions. If exceeded, S3 sends the events directly to the Lambda function's Dead Letter Queue (DLQ).

### Question 2 — `[D1.2 · Lambda Execution Context · Single]`
A developer maintains an AWS Lambda function written in Node.js that queries an Amazon RDS for PostgreSQL database on each invocation. The function experiences high latency and frequently exhausts database connections under heavy load. The database connection code is currently placed inside the main `exports.handler` function:
```javascript
exports.handler = async (event) => {
    const client = new Client({ /* credentials */ });
    await client.connect();
    const result = await client.query('SELECT * FROM products WHERE category = $1', [event.category]);
    await client.end();
    return result.rows;
};
```
What modification should the developer make to reduce latency and optimize connection pooling across invocations?
- A. Move the database client instantiation and `client.connect()` call outside the `exports.handler` function so the connection is reused across warm container invocations, and do not call `client.end()` inside the handler.
- B. Increase the Lambda function memory to 10,240 MB to force Lambda to keep TCP connections open indefinitely.
- C. Store the database connection pool object in the local `/tmp` directory as a serialized JSON file and read it on each execution.
- D. Enable Provisioned Concurrency with a value of 1, which guarantees that all concurrent requests share a single execution thread.

### Question 3 — `[D1.2 · Lambda Invocation Types & DLQ · Single]`
An order processing service invokes an AWS Lambda function asynchronously with `InvocationType = "Event"`. The developer needs to ensure that if the Lambda function fails all execution attempts due to unhandled exceptions, the original event payload and error diagnostic metadata are captured for manual remediation.
Which configuration meets this requirement with the LEAST operational overhead?
- A. Configure an Amazon SQS Dead Letter Queue (DLQ) directly on the Lambda function resource.
- B. Configure a Lambda On-Failure Destination pointing to an Amazon SQS queue or Amazon SNS topic.
- C. Write a custom `try/catch` block inside the Lambda handler that manually calls `sqs.sendMessage()` when an exception is caught.
- D. Configure an Amazon CloudWatch Logs subscription filter that streams log errors to an Amazon Kinesis Data Firehose delivery stream.

### Question 4 — `[D1.2 · Lambda Deployment Packages · Single]`
A developer is packaging a Python Lambda function that requires several large machine learning dependencies (`numpy`, `pandas`, `scikit-learn`). When attempting to upload the deployment ZIP archive directly via the AWS CLI `aws lambda update-function-code`, the command fails with an `InvalidParameterValueException` stating that the request payload exceeds the maximum allowed size.
What should the developer do to deploy the function successfully?
- A. Upload the deployment ZIP archive to an Amazon S3 bucket in the same AWS Region, and specify the S3 bucket and object key in the `update-function-code` command.
- B. Submit a service quota increase request to AWS Support to raise the Lambda direct upload limit to 500 MB.
- C. Compress the ZIP archive twice using GZIP compression before uploading.
- D. Split the Python code across two Lambda functions and invoke the second function synchronously from the first function.

### Question 5 — `[D1.3 · DynamoDB Capacity Units · Single]`
An application performs 100 read operations per second against an Amazon DynamoDB table. Each item read is 10 KB in size. The application requirements mandate that the reads must be **Strongly Consistent**.
How many Read Capacity Units (RCUs) must be provisioned for this DynamoDB table?
- A. 100 RCUs
- B. 200 RCUs
- C. 300 RCUs
- D. 150 RCUs

### Question 6 — `[D1.3 · DynamoDB Capacity Units · Single]`
A developer needs to write 50 items per second to an Amazon DynamoDB table. Each item has an average size of 2.5 KB.
How many Write Capacity Units (WCUs) must be provisioned for this table?
- A. 50 WCUs
- B. 100 WCUs
- C. 150 WCUs
- D. 200 WCUs

### Question 7 — `[D1.3 · DynamoDB Secondary Indexes · Multi — Choose 2]`
A company is designing an Amazon DynamoDB table to store user orders. The primary key consists of `CustomerId` (Partition Key) and `OrderDate` (Sort Key). The application needs to support two additional query patterns:
1. Query orders by `CustomerId` filtered by `TotalAmount` (a numeric attribute).
2. Query orders across ALL customers filtered by `OrderStatus` (e.g., `PENDING`, `SHIPPED`) and sorted by `OrderDate`.
Which combination of secondary index strategies should the developer implement? (Choose two.)
- A. Create a Local Secondary Index (LSI) with `CustomerId` as the Partition Key and `TotalAmount` as the Sort Key.
- B. Create a Global Secondary Index (GSI) with `OrderStatus` as the Partition Key and `OrderDate` as the Sort Key.
- C. Create a Local Secondary Index (LSI) with `OrderStatus` as the Partition Key and `OrderDate` as the Sort Key.
- D. Create a Global Secondary Index (GSI) with `CustomerId` as the Partition Key and `TotalAmount` as the Sort Key, but only after the table has been populated with at least 10,000 items.
- E. Create an LSI on `OrderStatus` and enable DAX on the LSI.

### Question 8 — `[D1.3 · DynamoDB Partition Key Design · Single]`
A high-throughput IoT tracking application writes device sensor measurements to an Amazon DynamoDB table at a rate of 25,000 writes per second. The developer notices `ProvisionedThroughputExceededException` errors even though the total provisioned write capacity for the table is 35,000 WCUs. An inspection reveals that all sensor devices write records using the date string `YYYY-MM-DD` as the partition key.
What is the root cause of these throttling errors, and what is the recommended solution?
- A. The table is experiencing a hot partition because all writes for the current day share the same partition key value. The developer should append a random suffix (e.g., a number from 1 to 50) or use `DeviceId` as the partition key to distribute writes evenly across physical partitions.
- B. The table has reached the maximum storage size per partition (10 GB). The developer must delete older items using a batch operation.
- C. DynamoDB does not support write throughput above 10,000 WCUs per table. The developer must create multiple tables and shard the data manually.
- D. The developer must enable DynamoDB Accelerator (DAX) to buffer the incoming write spikes.

### Question 9 — `[D1.3 · DynamoDB Optimistic Locking · Single]`
Multiple worker microservices running concurrently update customer account balances stored in an Amazon DynamoDB table. To prevent lost updates caused by race conditions (where two workers read the same balance and overwrite each other's updates), the developer needs to implement optimistic locking.
How should the developer implement optimistic locking in DynamoDB?
- A. Add a numeric `version` attribute to each item; when updating an item with `PutItem` or `UpdateItem`, include a `ConditionExpression` requiring that the `version` attribute equals the version value read by the worker, and increment `version` by 1.
- B. Call `TransactWriteItems` with a pessimistic lock statement on the partition key.
- C. Call `GetItem` with `ConsistentRead=true` before every write operation.
- D. Use DynamoDB Streams to revert conflicting transactions after they are committed.

### Question 10 — `[D1.3 · DynamoDB Streams & Lambda · Single]`
An online retail platform uses an Amazon DynamoDB table to record customer purchases. Whenever an order is inserted or updated, a notification email must be sent to the customer, and an inventory microservice must be notified. If the notification processor fails on a specific record, the stream processing must not get blocked permanently, and failed records should be routed to an SQS queue.
How should this architecture be implemented?
- A. Enable DynamoDB Streams on the table (`NEW_AND_OLD_IMAGES`), configure an AWS Lambda function with the DynamoDB Stream as an event source mapping, and configure `BisectBatchOnFunctionError=true`, `MaximumRecordAgeInSeconds`, and an `On-Failure Destination` pointing to an Amazon SQS queue.
- B. Have the application write records to Amazon S3, trigger Lambda via S3 Event Notifications, and configure S3 Object Lock.
- C. Configure an Amazon SNS topic directly as a target for the DynamoDB table.
- D. Write an EC2 cron job that runs a `Scan` operation against the DynamoDB table every 60 seconds and publishes updates to SQS.

### Question 11 — `[D1.1 · API Gateway REST vs HTTP APIs · Single]`
A developer needs to build an API for an internal microservice. Requirements:
- Sub-millisecond latency overhead.
- Native integration with OpenID Connect (OIDC) and OAuth 2.0 authorization (JWT tokens).
- Lowest possible cost per million requests.
- No requirement for request transformation (mapping templates), API keys, or per-client usage plans.
Which Amazon API Gateway type should the developer choose?
- A. Amazon API Gateway HTTP API
- B. Amazon API Gateway REST API (Regional)
- C. Amazon API Gateway REST API (Edge-Optimized)
- D. Amazon API Gateway WebSocket API

### Question 12 — `[D1.1 · API Gateway Stage Variables · Single]`
A serverless application has three deployment environments: `dev`, `test`, and `prod`. The backend consists of three versions of an AWS Lambda function associated with aliases: `DEV`, `TEST`, and `PROD`. The developer wants to use a single Amazon API Gateway REST API to route requests to the correct Lambda alias based on the stage where the API is published.
How should the developer configure API Gateway?
- A. Define a stage variable named `lambdaAlias` on each API Gateway stage (with values `DEV`, `TEST`, `PROD`), and configure the integration URI as `arn:aws:apigateway:region:lambda:path/2015-03-31/functions/arn:aws:lambda:region:account-id:function:MyFunction:${stageVariables.lambdaAlias}/invocations`.
- B. Create three separate API Gateway REST APIs and maintain independent routing rules in code.
- C. Pass the target environment as an HTTP header `X-Environment` from the client and configure an API Gateway resource policy.
- D. Use a DynamoDB lookup table inside API Gateway to dynamically resolve the function ARN at runtime.

### Question 13 — `[D1.1 · API Gateway Request Validation · Single]`
A development team exposes a REST API via Amazon API Gateway that invokes a downstream AWS Lambda function. The Lambda function frequently throws uncaught runtime errors when clients omit required query string parameters (`customerId` and `startDate`) or provide an invalid JSON request body. The team wants to reject invalid requests before they reach the Lambda function to eliminate unnecessary Lambda invocation costs.
What should the developer configure?
- A. Enable Request Validation in API Gateway by creating a Request Validator for "Validate body, query string parameters, and headers", and define a JSON Schema model for the method request body.
- B. Configure an AWS WAF web ACL with custom regex rules matching the query string parameters.
- C. Create an API Gateway Lambda authorizer to parse and validate the request payload.
- D. Configure an API Gateway mapping template that converts missing query string parameters to null values.

### Question 14 — `[D1.1 · API Gateway CORS Configuration · Multi — Choose 2]`
A Single Page Application (SPA) hosted on `https://www.example.com` makes AJAX `POST` requests with a custom header `X-Custom-Auth` and `Content-Type: application/json` to an Amazon API Gateway REST API at `https://api.example.com`. In web browser tests, the request fails with the error: `Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource`.
What two configurations must the developer implement in API Gateway to resolve this error? (Choose two.)
- A. Enable CORS on the resource in API Gateway to create an `OPTIONS` mock method that returns the headers `Access-Control-Allow-Origin: 'https://www.example.com'` and `Access-Control-Allow-Headers: 'Content-Type,X-Custom-Auth'`.
- B. Ensure the backend integration response (or Lambda function proxy integration response) includes the HTTP header `Access-Control-Allow-Origin: 'https://www.example.com'` in the response payload.
- C. Delete the `OPTIONS` method because preflight checks are only required for GET requests.
- D. Change the API Gateway endpoint type from Regional to Edge-Optimized.
- E. Disable the Same-Origin Policy in the client's DNS settings.

### Question 15 — `[D1.3 · S3 Presigned URLs · Single]`
A mobile application allows users to upload private video files directly to an Amazon S3 bucket. The application backend runs on AWS Lambda. The security team mandates that:
1. Users must not be given direct AWS credentials or IAM permissions to the S3 bucket.
2. Video files must not be uploaded through the Lambda function to prevent Lambda payload limit and timeout issues.
3. Upload links must expire after 15 minutes.
Which design meets these requirements?
- A. The mobile app requests an upload link from the Lambda backend; the Lambda function generates an Amazon S3 presigned PUT URL using the AWS SDK with an expiration of 900 seconds; the mobile client uploads the binary video directly to S3 using the presigned URL.
- B. The mobile app uploads the video file to an Amazon SQS queue, and an EC2 worker pulls the message and writes to S3.
- C. The Lambda function issues a temporary IAM user access key to the mobile application with an expiration of 15 minutes.
- D. The developer configures S3 Cross-Origin Resource Sharing (CORS) with `AllowedOrigins: *` and allows anonymous `s3:PutObject` access on the bucket.

### Question 16 — `[D1.3 · S3 Multipart Upload · Single]`
A developer is writing a utility that uploads large dataset files (between 500 MB and 20 GB) to Amazon S3 over a network connection that occasionally drops. If a failure occurs halfway through an upload, the utility should resume uploading without restarting the entire file from the beginning. In addition, incomplete uploads must not incur ongoing storage costs.
Which approach should the developer take?
- A. Use the Amazon S3 Multipart Upload API to upload the file in 10 MB parts concurrently; if a part fails, retry only that part; configure an S3 Lifecycle rule to abort incomplete multipart uploads after 7 days.
- B. Upload the file using single `PutObject` calls with exponential backoff and jitter.
- C. Store the dataset in Amazon DynamoDB first, then use DynamoDB Streams to export to S3.
- D. Use S3 Transfer Acceleration combined with single-part uploads to guarantee atomic delivery.

### Question 17 — `[D1.1 · SQS Standard vs FIFO · Single]`
A banking application processes financial transaction ledger entries. Each transaction must be processed **strictly once** (no duplicates) and **in the exact chronological order** in which it occurred for each individual customer account. Transactions across different customer accounts may be processed in parallel.
Which messaging architecture satisfies these requirements?
- A. Use an Amazon SQS FIFO queue; set `MessageGroupId` to the `AccountId` and provide a unique `MessageDeduplicationId` (or enable content-based deduplication).
- B. Use an Amazon SQS Standard queue; set visibility timeout to 0 seconds and use client-side timestamp sorting.
- C. Use an Amazon SNS Standard topic fanned out to multiple SQS Standard queues.
- D. Use an Amazon SQS FIFO queue; leave `MessageGroupId` empty so all messages are processed concurrently.

### Question 18 — `[D1.1 · SQS Polling & Visibility Timeout · Multi — Choose 2]`
A fleet of worker EC2 instances polls an Amazon SQS queue for order processing jobs. Processing an order takes approximately 45 seconds. However, developers observe that multiple worker instances frequently pick up and process the **exact same order message** simultaneously, resulting in duplicated orders. In addition, the workers make thousands of empty `ReceiveMessage` API calls per minute when the queue is idle, driving up AWS costs.
What two configuration changes will solve both issues? (Choose two.)
- A. Increase the queue's Visibility Timeout from the default 30 seconds to a value greater than processing time (e.g., 90 seconds).
- B. Enable Long Polling by setting `ReceiveMessageWaitTimeSeconds` to 20 seconds.
- C. Decrease the queue's Visibility Timeout to 5 seconds so workers release messages faster.
- D. Enable Short Polling by setting `ReceiveMessageWaitTimeSeconds` to 0 seconds.
- E. Convert the queue to an Amazon Kinesis Data Firehose delivery stream.

### Question 19 — `[D1.1 · SNS Fan-Out & Message Filtering · Single]`
An e-commerce order microservice publishes purchase events to an Amazon SNS topic. Two downstream services consume these events:
1. `FraudDetectionService` must inspect ALL purchase events.
2. `LargeOrderFulfillmentService` must ONLY receive purchase events where the `order_total` exceeds $1,000.
How should the developer configure the messaging architecture with the LEAST custom code?
- A. Subscribe two Amazon SQS queues to the Amazon SNS topic; attach an SNS Subscription Filter Policy on the second SQS queue's subscription specifying `{"order_total": [{"numeric": [">", 1000]}]}`; publish messages to SNS with message attributes.
- B. Create two separate SNS topics; have the publisher evaluate the order total and decide which topic to call.
- C. Have both services poll a single SQS queue and delete messages they do not want to process.
- D. Place an AWS Lambda function between the SNS topic and the queues to manually route events.

### Question 20 — `[D1.1 · Step Functions Workflows · Single]`
An organization needs to orchestrate a credit card fraud evaluation pipeline. The pipeline processes 15,000 transactions per second, each execution completes within 3 seconds, and the execution history does not need to be audited in the AWS Step Functions console for more than 5 minutes.
Which AWS Step Functions workflow type should the developer choose?
- A. Express Workflows
- B. Standard Workflows
- C. Human Approval Workflows
- D. Activity Workflows

### Question 21 — `[D1.3 · ElastiCache Caching Strategies · Single]`
A read-heavy web application queries an Amazon RDS MySQL database for product catalog information. The database is experiencing high CPU utilization. The developer wants to introduce an Amazon ElastiCache Redis cluster using the **Lazy Loading (Cache-Aside)** pattern.
What is the sequence of operations for reading data under this pattern?
- A. The application requests data from the cache; on a cache hit, it returns the cached data; on a cache miss, it queries the database, writes the retrieved data into the cache with a TTL, and returns the data to the client.
- B. The application always writes data to the cache first; a background worker synchronizes cache data to the database.
- C. The database triggers a stored procedure that updates the Redis cache whenever a table row is updated.
- D. The application queries the database directly, and the database automatically forwards query results to ElastiCache.

---

### Question 22 — `[D2.1 · STS Cross-Account AssumeRole · Single]`
An application running on an Amazon EC2 instance in **Account A (111122223333)** needs to read files from an Amazon S3 bucket located in **Account B (444455556666)**. Company security policy prohibits storing static access keys.
Which combination of IAM configurations should the developer implement?
- A. In Account B, create an IAM role with a Trust Policy granting `sts:AssumeRole` to `arn:aws:iam::111122223333:root` and an attached permissions policy allowing `s3:GetObject` on the bucket. In Account A, attach an IAM policy to the EC2 instance role allowing `sts:AssumeRole` on the Account B role ARN. Have the application call `sts:AssumeRole`.
- B. Create an IAM user in Account B, generate an access key, and store it in an environment variable on the EC2 instance in Account A.
- C. In Account A, create an IAM role with S3 permissions, and configure Account B's S3 bucket policy to allow `Principal: "*"`.
- D. In Account B, configure the S3 bucket policy to allow `sts:AssumeRole` directly from the EC2 instance public IP.

### Question 23 — `[D2.1 · STS Web Identity Federation · Single]`
A mobile gaming application allows players to sign in using their Google or Apple accounts. After authentication, the mobile client must upload gameplay analytics directly to an Amazon Kinesis Data Stream without passing through an intermediary backend application.
Which AWS STS API should the mobile application use to acquire temporary AWS credentials?
- A. `sts:AssumeRoleWithWebIdentity`
- B. `sts:GetSessionToken`
- C. `sts:AssumeRole`
- D. `sts:GetFederationToken`

### Question 24 — `[D2.1 · IAM Policy Evaluation Logic · Single]`
An IAM user has two policies attached:
1. An identity-based policy that contains an `Allow` effect for `s3:PutObject` on all buckets.
2. A permissions boundary that allows all actions on `s3:*`.
However, the target S3 bucket has a bucket policy with the following statement:
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:PutObject",
  "Resource": "arn:aws:s3:::corporate-finance-bucket/*",
  "Condition": {
    "Bool": { "aws:SecureTransport": "false" }
  }
}
```
If the user attempts to upload an object over plaintext HTTP (`aws:SecureTransport = false`), what will be the outcome and why?
- A. The request will be **Denied** because an explicit Deny in any applicable policy always overrides all explicit Allows.
- B. The request will be **Allowed** because the identity-based policy explicitly allows `s3:PutObject`.
- C. The request will be **Allowed** because the Permissions Boundary supersedes resource-based policies.
- D. The request will be **Denied** because Permissions Boundaries do not support condition keys.

### Question 25 — `[D2.1 · IAM Permission Boundaries · Single]`
A security administrator wants to delegate the ability to create IAM roles for AWS Lambda functions to junior developers. However, the administrator must ensure that junior developers cannot escalate their privileges by creating roles with administrator permissions.
What mechanism should the administrator use?
- A. Define an IAM Permission Boundary that specifies the maximum permissions a role can have, and require developers to attach this boundary when creating any role using a condition in their IAM policy.
- B. Attach an AWS Organizations Service Control Policy (SCP) to the IAM user group.
- C. Configure an IAM session policy on the developer's credentials.
- D. Restrict developers to using only AWS managed roles in the console.

### Question 26 — `[D2.2 · KMS Envelope Encryption · Single]`
A developer needs to encrypt a 50 MB archive file locally before uploading it to Amazon S3. The developer attempts to call the AWS KMS `Encrypt` API directly and receives a `ValidationException`.
Why did this call fail, and how should the developer perform the encryption?
- A. The `kms:Encrypt` API only accepts plaintext payloads up to 4 KB. The developer must call `kms:GenerateDataKey` to obtain a plaintext data key and an encrypted data key, encrypt the file locally with the plaintext key, erase the plaintext key from memory, and store the encrypted data key alongside the encrypted file.
- B. The file must be encoded in base64 before passing it to `kms:Encrypt`.
- C. AWS KMS cannot encrypt binary archive files; the developer must convert the archive to JSON.
- D. The developer must split the 50 MB file into 4 KB chunks and call `kms:Encrypt` for each chunk.

### Question 27 — `[D2.2 · KMS Key Types & Rotation · Single]`
A financial services compliance requirement states that all customer data must be encrypted using encryption keys that:
1. Are owned and managed by the company.
2. Allow custom key policies and grants to be defined.
3. Support automatic annual rotation.
4. Can be immediately deleted or disabled in the event of a security compromise.
Which key type satisfies all requirements?
- A. AWS KMS Customer Managed Key (CMK)
- B. AWS Managed Key (`aws/s3`)
- C. AWS Owned Key
- D. Client-provided symmetric key (SSE-C)

### Question 28 — `[D2.2 · KMS Key Policies · Single]`
A developer creates a Customer Managed Key (CMK) in AWS KMS. An administrator with the `AdministratorAccess` policy attached attempts to administer the key using the AWS CLI but receives an `AccessDeniedException`.
Why did the administrator receive an Access Denied error?
- A. KMS key policies govern access to KMS keys; unless the key policy contains a statement that gives the AWS account root principal (`"Principal": {"AWS": "arn:aws:iam::<account-id>:root"}`) permission to use the key, IAM policies (including AdministratorAccess) cannot grant permissions to the key.
- B. The administrator must first create a KMS grant for themselves.
- C. IAM users can never administer KMS keys; only the root account user can administer KMS keys.
- D. The administrator's IAM policy is missing the `kms:CreateAlias` action.

### Question 29 — `[D2.2 · KMS Grants vs Policies · Single]`
An application running on Amazon EC2 instances dynamically provisions worker processes that need temporary (10-minute) access to decrypt data using a specific KMS key. These workers spin up and tear down thousands of times per day. Updating the KMS key policy on each run causes policy size limit errors (`LimitExceededException`).
What is the recommended solution?
- A. Use the `kms:CreateGrant` API to dynamically grant temporary decryption permissions to the worker's IAM role, and call `kms:RetireGrant` or `kms:RevokeGrant` when the work is finished.
- B. Create an IAM role for each worker and delete the role after 10 minutes.
- C. Use a wildcard `*` principal in the KMS key policy.
- D. Store the plaintext master key in an ElastiCache cluster.

### Question 30 — `[D2.2 · KMS Asymmetric Keys · Single]`
A software company needs to digitally sign software updates before distributing them to millions of client devices worldwide. The client devices must be able to verify the signature of the update file offline, without having AWS credentials or making network calls to AWS KMS.
Which KMS key configuration should the company use?
- A. Create an asymmetric KMS key pair with `SIGN_VERIFY` key usage; sign the software updates using `kms:Sign`; download the public key using `kms:GetPublicKey` and embed it in client devices for signature verification.
- B. Create a symmetric KMS key and share the secret key with all client devices.
- C. Create an HMAC KMS key and share the HMAC key with client devices.
- D. Export the private key of an asymmetric KMS key and sign the binaries locally on build servers.

### Question 31 — `[D2.1 · Cognito User Pools vs Identity Pools · Single]`
A company is developing a web application. Requirements:
- Provide self-service user registration, email verification, and password recovery.
- Authenticate users and issue JSON Web Tokens (JWT).
- Grant authenticated users temporary AWS credentials to upload profile pictures directly to their own folder in an Amazon S3 bucket (`s3://bucket-name/${cognito-identity.amazonaws.com:sub}/*`).
Which Amazon Cognito architecture satisfies these requirements?
- A. Use an Amazon Cognito User Pool for user registration and JWT token issuance; use an Amazon Cognito Identity Pool to exchange the User Pool token for temporary AWS STS credentials linked to an IAM role.
- B. Use an Amazon Cognito Identity Pool for user sign-up and authentication, and use a User Pool for S3 authorization.
- C. Use a Cognito User Pool only, and configure IAM policies directly inside the User Pool settings.
- D. Use Amazon Cognito Sync to store user credentials.

### Question 32 — `[D2.1 · Cognito User Pool Triggers · Single]`
A SaaS company wants to enrich the ID tokens and Access tokens issued by Amazon Cognito with the user's `tenant_id` and assigned roles from an external database whenever the user signs in.
Which Amazon Cognito Lambda trigger should be implemented?
- A. Pre token generation Lambda trigger
- B. Post confirmation Lambda trigger
- C. Pre sign-up Lambda trigger
- D. Custom message Lambda trigger

### Question 33 — `[D2.2 · Secrets Manager Automatic Rotation · Single]`
An application running on Amazon ECS connects to an Amazon RDS for MySQL database. The company's security baseline mandates that the database password must be rotated every 30 days automatically with zero downtime.
What is the most operationally efficient solution?
- A. Store database credentials in AWS Secrets Manager and enable automatic rotation using the built-in Secrets Manager rotation Lambda template for MySQL.
- B. Store database credentials in AWS Systems Manager Parameter Store as a `SecureString` and create an EventBridge rule that triggers a custom Lambda function to rotate the password.
- C. Store credentials in an Amazon S3 bucket encrypted with SSE-KMS and write a cron job on EC2 to rotate the password.
- D. Hardcode the database credentials in the ECS task definition and update the task definition every 30 days.

### Question 34 — `[D2.2 · Secrets Manager Caching · Single]`
A serverless API built on AWS Lambda executes 5,000 times per second and retrieves an API key from AWS Secrets Manager on every invocation by calling `secretsmanager:GetSecretValue`. The API starts failing with `ThrottlingException` errors, and the monthly AWS bill shows high Secrets Manager API charges.
How should the developer resolve this issue?
- A. Use the AWS Secrets Manager client-side caching library and initialize the cache outside the Lambda handler function so the secret is reused across warm container invocations.
- B. Increase the Lambda memory to maximum to bypass Secrets Manager rate limits.
- C. Migrate the secret to an environment variable in the Lambda function configuration.
- D. Request a quota increase for `GetSecretValue` from AWS Support.

### Question 35 — `[D2.2 · SSM Parameter Store Hierarchies · Single]`
A developer manages configuration settings for three microservices across `development`, `staging`, and `production` environments in AWS Systems Manager Parameter Store. The developer wants to retrieve all settings for a specific service in a single API call and enforce IAM least privilege by environment.
How should the parameters be named?
- A. Use hierarchical path names, such as `/production/order-service/db_url` and `/development/order-service/db_url`, and call `ssm:GetParametersByPath`.
- B. Use flat names with tags, such as `OrderService_DbUrl` with tag `Environment: production`.
- C. Store all settings as a single base64 string in one parameter.
- D. Prefix parameter names with the AWS Account ID.

### Question 36 — `[D2.1 · S3 Bucket Policies & TLS · Single]`
A security audit requires that an Amazon S3 bucket named `sensitive-financial-records` must strictly enforce encryption in transit by denying any requests that do not use HTTPS.
Which bucket policy statement achieves this requirement?
- A. A statement with `"Effect": "Deny"`, `"Action": "s3:*"`, `"Resource": "arn:aws:s3:::sensitive-financial-records/*"`, and `"Condition": {"Bool": {"aws:SecureTransport": "false"}}`.
- B. A statement with `"Effect": "Allow"`, `"Action": "s3:*"`, and `"Condition": {"StringEquals": {"s3:x-amz-server-side-encryption": "AES256"}}`.
- C. An IAM policy on the root user denying HTTP requests.
- D. A CORS configuration rule blocking port 80.

### Question 37 — `[D2.2 · S3 Server-Side Encryption · Single]`
A developer uploads objects to an Amazon S3 bucket and wants to ensure that all objects are encrypted with a Customer Managed Key (CMK) stored in AWS KMS. The bucket policy must reject any upload requests that do not specify the correct KMS key.
Which HTTP header must the upload request include to be accepted?
- A. `x-amz-server-side-encryption: aws:kms` and `x-amz-server-side-encryption-aws-kms-key-id: <KMS-Key-ARN>`
- B. `x-amz-server-side-encryption-customer-algorithm: AES256`
- C. `Authorization: Bearer <KMS-Key-Token>`
- D. `Content-MD5: <Checksum>`

### Question 38 — `[D2.1 · STS Session Tokens · Single]`
An IAM user needs to perform administrative operations via the AWS CLI that are protected by an MFA condition in their IAM policy: `"Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}`.
Which AWS STS command should the user run to obtain temporary credentials that satisfy this condition?
- A. `aws sts get-session-token --serial-number <MFA-Device-ARN> --token-code <MFA-Code>`
- B. `aws sts assume-role --role-arn <Role-ARN> --role-session-name session1`
- C. `aws sts get-federation-token --name user1`
- D. `aws sts get-caller-identity`

---

### Question 39 — `[D3.1 · CodeBuild buildspec Phases · Single]`
A developer is writing a `buildspec.yml` file for an AWS CodeBuild project that builds a Docker image and pushes it to Amazon ECR.
In which phase of the `buildspec.yml` file should the developer execute the `aws ecr get-login-password | docker login` command?
- A. `pre_build`
- B. `install`
- C. `build`
- D. `post_build`

### Question 40 — `[D3.1 · CodeBuild Artifact & Cache · Single]`
A Java application built with Maven takes 15 minutes to run in AWS CodeBuild because it downloads all dependencies from the central Maven repository on every build.
How can the developer reduce build execution time?
- A. Specify the local Maven repository path `/root/.m2/**/*` under the `cache.paths` block in `buildspec.yml` and enable caching in the CodeBuild project.
- B. Run `mvn install` in the `post_build` phase instead of `build`.
- C. Store the compiled `.jar` file in an Amazon SQS queue.
- D. Increase the CodeBuild timeout from 60 minutes to 120 minutes.

### Question 41 — `[D3.1 · CodeBuild Environment Variables · Single]`
A developer needs to pass a database password stored in AWS Secrets Manager and an API endpoint URL stored in SSM Parameter Store into a CodeBuild build container without exposing them in plaintext in source control.
How should these variables be defined in `buildspec.yml`?
- A. Under the `env.secrets-manager` and `env.parameter-store` sections in `buildspec.yml`.
- B. Under the `env.variables` section as plaintext key-value pairs.
- C. In the `install` phase using shell `export` commands with hardcoded strings.
- D. In the `artifacts` section.

### Question 42 — `[D3.2 · CodeDeploy EC2 Lifecycle Hooks · Single]`
During an in-place deployment of an application to an Amazon EC2 instance using AWS CodeDeploy, the developer needs to run a bash script to stop the currently running Apache service before the new revision files are copied to the instance.
Which lifecycle hook in `appspec.yml` should run this script?
- A. `ApplicationStop`
- B. `BeforeInstall`
- C. `AfterInstall`
- D. `ApplicationStart`

### Question 43 — `[D3.2 · CodeDeploy EC2 Hook Order · Single]`
What is the correct execution order of AWS CodeDeploy lifecycle event hooks for an in-place deployment on an EC2/On-Premises instance?
- A. `ApplicationStop` → `BeforeInstall` → `Install` → `AfterInstall` → `ApplicationStart` → `ValidateService`
- B. `BeforeInstall` → `Install` → `ApplicationStop` → `AfterInstall` → `ValidateService` → `ApplicationStart`
- C. `DownloadBundle` → `ApplicationStart` → `ValidateService` → `ApplicationStop`
- D. `Install` → `BeforeInstall` → `AfterInstall` → `ApplicationStop` → `ApplicationStart`

### Question 44 — `[D3.2 · CodeDeploy Lambda Hooks · Single]`
A serverless application deployed via AWS CodeDeploy uses the `LambdaCanary10Percent5Minutes` deployment configuration. The developer needs to run an automated synthetic test against the newly deployed Lambda function version BEFORE any production traffic is shifted to it.
Which lifecycle hook in the `appspec.yml` file should be configured?
- A. `BeforeAllowTraffic`
- B. `AfterAllowTraffic`
- C. `BeforeInstall`
- D. `ValidateService`

### Question 45 — `[D3.2 · CodeDeploy ECS Lifecycle Hooks · Single]`
An Amazon ECS service uses an Application Load Balancer (ALB) and AWS CodeDeploy for blue/green deployments. The ALB has a production listener on port 443 and a test listener on port 8443. The developer wants to run automated validation tests against the green task set using the test listener before shifting production traffic.
Which lifecycle hook in the ECS `appspec.yaml` should invoke the test Lambda function?
- A. `AfterAllowTestTraffic`
- B. `BeforeInstall`
- C. `AfterInstall`
- D. `BeforeAllowTraffic`

### Question 46 — `[D3.2 · CodeDeploy Automatic Rollbacks · Single]`
A team deploys an application to an Auto Scaling group using AWS CodeDeploy. The team wants CodeDeploy to automatically roll back the deployment if the Application Load Balancer target 5XX error rate exceeds 1% during the deployment window.
How can this be accomplished?
- A. Create an Amazon CloudWatch alarm monitoring `HTTPCode_Target_5XX_Count`, and configure the CodeDeploy deployment group to automatically roll back when that alarm enters the `ALARM` state.
- B. Write a custom script in the `ValidateService` hook that calls `aws deploy stop-deployment`.
- C. Configure Route 53 DNS failover.
- D. Enable Auto Scaling dynamic scaling policies based on CPU utilization.

### Question 47 — `[D3.3 · CodePipeline Manual Approvals · Single]`
A CI/CD pipeline built with AWS CodePipeline has three stages: `Source`, `Build`, and `Deploy`. Company policy mandates that a QA manager must manually review the build output and grant explicit approval before artifacts are deployed to the `Deploy` stage.
How should the developer configure CodePipeline?
- A. Add an action with category `Approval` and provider `Manual` between the `Build` and `Deploy` stages, and associate an Amazon SNS topic subscribed to the QA manager's email address.
- B. Add a Lambda function in the Build stage that calls `time.sleep()` for 24 hours.
- C. Configure an SQS queue between stages and require the manager to delete a message.
- D. Configure GitHub branch protection rules to block the pipeline.

### Question 48 — `[D3.3 · CodePipeline EventBridge Trigger · Single]`
A development team uses AWS CodePipeline with an AWS CodeCommit repository. The current pipeline detects code changes via periodic polling, which causes up to a 3-minute delay before a build starts. The team wants the pipeline to trigger immediately when a developer pushes code to the `main` branch.
What is the recommended solution?
- A. Configure an Amazon EventBridge rule that matches CodeCommit `referenceUpdated` events on the `main` branch and targets the CodePipeline pipeline.
- B. Increase the CodePipeline polling frequency setting.
- C. Write a custom daemon on an EC2 instance that polls Git every 2 seconds.
- D. Add an SNS topic that sends an SMS message to CodePipeline.

### Question 49 — `[D3.4 · SAM CLI Commands · Single]`
A developer has initialized an AWS SAM project and written the application code in Python. What is the standard sequence of AWS SAM CLI commands to build the deployment artifacts, upload them to Amazon S3, and deploy the CloudFormation stack with guided prompts?
- A. `sam build` followed by `sam deploy --guided`
- B. `sam init` followed by `sam run`
- C. `sam compile` followed by `sam publish`
- D. `sam package` followed by `sam start-api`

### Question 50 — `[D3.4 · SAM Template Transform · Single]`
What is the required line in an AWS CloudFormation template that instructs CloudFormation to treat the template as an AWS Serverless Application Model (SAM) template?
- A. `Transform: AWS::Serverless-2016-10-31`
- B. `AWSTemplateFormatVersion: '2010-09-09'`
- C. `Type: AWS::Serverless::Function`
- D. `Description: Serverless Application`

### Question 51 — `[D3.4 · CloudFormation Intrinsic Functions · Single]`
A developer needs to reference an Amazon S3 bucket name that is created within the same CloudFormation template and pass it as an environment variable to an AWS Lambda function.
Which CloudFormation intrinsic function should the developer use?
- A. `!Ref MyBucketResource`
- B. `!GetAtt MyBucketResource.Arn`
- C. `!ImportValue MyBucketResource`
- D. `!Sub "${AWS::StackName}-bucket"`

### Question 52 — `[D3.4 · Elastic Beanstalk Deployment Policies · Single]`
An application running on AWS Elastic Beanstalk cannot tolerate any reduction in server capacity during new version deployments, and cost is a secondary concern. The deployment must maintain 100% capacity at all times without creating an entirely new environment URL.
Which deployment policy should the developer select?
- A. Rolling with additional batch
- B. All at once
- C. Rolling
- D. Blue/Green (External DNS swap)

### Question 53 — `[D3.4 · Elastic Beanstalk Immutable Deployment · Single]`
A mission-critical payment processing application deployed on AWS Elastic Beanstalk requires zero downtime and the fastest, safest rollback capability if a new release fails health checks. The team prefers launching a completely separate temporary Auto Scaling group of instances to test the new release before terminating the old instances.
Which deployment policy meets these requirements?
- A. Immutable
- B. Rolling
- C. All at once
- D. Traffic splitting

### Question 54 — `[D3.4 · ECS Task Execution Role vs Task Role · Single]`
A containerized web service runs on Amazon ECS using the AWS Fargate launch type. The application code inside the container reads and writes records to an Amazon DynamoDB table. During container startup, the ECS agent needs to pull a private Docker image from Amazon ECR and send container logs to Amazon CloudWatch Logs.
Which IAM roles must be configured in the ECS task definition?
- A. Set the **Task Role** with permissions for `dynamodb:*`, and set the **Task Execution Role** with permissions for ECR image pull (`ecr:GetAuthorizationToken`, `ecr:BatchGetImage`) and CloudWatch logging (`logs:CreateLogStream`, `logs:PutLogEvents`).
- B. Set the Task Execution Role with DynamoDB permissions and the Task Role with ECR permissions.
- C. Attach an IAM role to the underlying Fargate host hardware.
- D. Embed IAM access keys in the Docker container image.

---

### Question 55 — `[D4.2 · CloudWatch High-Resolution Metrics · Single]`
A trading application requires a custom latency metric to be monitored in Amazon CloudWatch at **1-second granularity** so that micro-spikes lasting only a few seconds can be detected and alerted on.
How should the developer publish this custom metric using the AWS CLI or SDK?
- A. Call `PutMetricData` specifying the parameter `StorageResolution = 1`.
- B. Call `PutMetricData` with standard resolution and set the CloudWatch Alarm period to 1 second.
- C. Enable Detailed Monitoring on the application's EC2 instances.
- D. CloudWatch does not support metric granularity below 1 minute.

### Question 56 — `[D4.2 · CloudWatch Metric Dimensions · Single]`
A developer publishes a custom CloudWatch metric `OrderCount` with two dimensions: `{"Environment": "Prod", "Region": "us-east-1"}`. When querying CloudWatch for the metric `OrderCount` with only the dimension `{"Environment": "Prod"}`, the query returns no data.
What is the reason for this behavior?
- A. CloudWatch treats every unique combination of dimensions as an entirely separate metric; metrics are not automatically aggregated across dimensions unless metric math or the `SEARCH` function is used.
- B. Custom metrics can only have one dimension.
- C. The developer forgot to enable detailed monitoring for custom metrics.
- D. The metric data expired because custom metrics are only retained for 3 hours.

### Question 57 — `[D4.2 · CloudWatch Embedded Metric Format · Single]`
A high-throughput AWS Lambda function processes 10,000 requests per second. The developer wants to record several custom business metrics (e.g., items sold, processing time) in CloudWatch without making synchronous `PutMetricData` API calls that would introduce latency and incur high API request costs.
Which solution should the developer use?
- A. Output structured JSON logs matching the CloudWatch Embedded Metric Format (EMF) specification to `stdout`; CloudWatch Logs automatically extracts the metrics asynchronously without API charges.
- B. Buffer metrics in local `/tmp` memory and write them to S3.
- C. Send metric data to an Amazon SQS queue and process them with an EC2 instance.
- D. Call `PutMetricData` in a separate asynchronous thread inside the Lambda handler.

### Question 58 — `[D4.2 · CloudWatch Metric Filters · Single]`
An application writes application logs to a CloudWatch Logs log group. The operations team wants to create an alarm that notifies engineers via SNS whenever the word `FATAL_ERROR` appears more than 5 times within a 10-minute window. No changes can be made to the application code.
How should the developer implement this?
- A. Create a Metric Filter on the CloudWatch Logs log group with the filter pattern `[..., words = "*FATAL_ERROR*", ...]`, assign a metric name, and create a CloudWatch Alarm on that metric with a threshold of > 5.
- B. Write a Lambda function that continuously polls the log group using `FilterLogEvents`.
- C. Export logs to Amazon S3 and run Athena queries on a cron schedule.
- D. Enable AWS CloudTrail Insights on the log group.

### Question 59 — `[D4.2 · CloudWatch Synthetics Canaries · Single]`
A company needs to continuously monitor the availability and latency of its customer checkout REST API endpoint every 5 minutes. The monitoring system must simulate customer behavior by sending HTTP POST requests with a test payload, verify the HTTP 200 response, and alert the team if the endpoint is degraded or down.
Which service should the developer implement?
- A. Amazon CloudWatch Synthetics Canary
- B. AWS CloudTrail Event History
- C. VPC Flow Logs
- D. AWS X-Ray Sampling Rules

### Question 60 — `[D4.2 · CloudWatch Subscription Filters · Multi — Choose 2]`
A developer needs to stream application logs from an Amazon CloudWatch Logs log group in **real time** to an Amazon OpenSearch Service (formerly Elasticsearch) analytics cluster.
Which two AWS services can be configured as direct targets for a CloudWatch Logs Subscription Filter? (Choose two.)
- A. Amazon Kinesis Data Streams
- B. AWS Lambda
- C. Amazon S3 directly without intermediate services
- D. Amazon SNS topic directly
- E. Amazon DynamoDB table directly

### Question 61 — `[D4.2 · X-Ray Tracing Architecture · Single]`
A developer wants to instrument an application running on an Amazon EC2 instance with AWS X-Ray. The developer has instrumented the application code using the AWS X-Ray SDK.
What additional software component must be installed and running on the EC2 instance to listen for UDP traffic on port 2000 and relay trace data to the AWS X-Ray API?
- A. AWS X-Ray Daemon
- B. Unified CloudWatch Agent only
- C. AWS Systems Manager Agent
- D. AWS CodeDeploy Agent

### Question 62 — `[D4.2 · X-Ray Annotations vs Metadata · Single]`
A developer instruments a distributed serverless application with AWS X-Ray. The developer needs to record contextual details on traces:
1. `customerTier` (e.g., `PLATINUM`, `GOLD`) which must be indexed so developers can filter and search traces on the X-Ray service map.
2. `debugPayload` (a large JSON object containing raw request data) which is needed for diagnosing errors but does NOT need to be indexed or searched.
How should the developer record these two attributes using the X-Ray SDK?
- A. Record `customerTier` as an **Annotation**, and record `debugPayload` as **Metadata**.
- B. Record both `customerTier` and `debugPayload` as Annotations.
- C. Record both `customerTier` and `debugPayload` as Metadata.
- D. Record `customerTier` as Metadata, and record `debugPayload` as an Annotation.

### Question 63 — `[D4.2 · X-Ray Sampling Rules · Single]`
A high-traffic e-commerce microservice handles 2,000 requests per second. If all requests are traced in AWS X-Ray, the tracing costs will exceed the team's budget. The developer wants to ensure that the service records at least 1 request per second and samples 5% of all additional requests.
How should the developer configure the X-Ray Sampling Rule?
- A. Set `Reservoir size = 1` and `Fixed rate = 0.05 (5%)`.
- B. Set `Reservoir size = 50` and `Fixed rate = 0.01 (1%)`.
- C. Set `Reservoir size = 100` and `Fixed rate = 1.0 (100%)`.
- D. Disable sampling and use CloudWatch Logs instead.

### Question 64 — `[D4.2 · X-Ray Context Propagation · Single]`
In a microservices architecture, Service A calls Service B over HTTP. To ensure that Service A and Service B appear as connected nodes in the same end-to-end trace on the AWS X-Ray service graph, how must the trace context be passed from Service A to Service B?
- A. Service A must inject the trace context into the HTTP request header `X-Amzn-Trace-Id` when invoking Service B.
- B. Service A must write the trace ID to an Amazon S3 bucket, and Service B must read it.
- C. The services must run in the same VPC subnet.
- D. AWS X-Ray automatically traces cross-service calls without any HTTP header propagation.

### Question 65 — `[D4.3 · CloudFront Cache Optimization · Multi — Choose 2]`
A global media company uses Amazon CloudFront to deliver static assets (images, CSS, JavaScript) from an Amazon S3 bucket. The development team releases an urgent patch to `main.js`. However, users continue to receive the outdated version of `main.js` from CloudFront edge caches.
What are two valid ways to ensure users immediately receive the new file version? (Choose two.)
- A. Create a CloudFront invalidation for `/main.js` (or `/*`).
- B. Use versioned object names in application code (e.g., `main.v2.js` or `main.js?v=2`).
- C. Change the S3 bucket name.
- D. Delete the CloudFront distribution and recreate it.
- E. Lower the CloudFront Minimum TTL to -1.
