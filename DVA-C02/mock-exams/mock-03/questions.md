# 🎯 DVA-C02 Mock Exam 03 — 65 questions · 130 minutes

> **Exam-realistic full-length mock.** Distribution strictly follows official AWS DVA-C02 domain weights.
> ⏱️ Set a timer for **130 minutes** (~2 minutes per question). No notes, no documentation, no pausing.
> 🔒 Answers, explanations, and per-domain scoring: [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (1 correct out of 4) · `Multi` (choose the stated number of options).
> Tag: `[Domain.Task · Service · Format]`. Domains: `D1` (32% · 21Q) · `D2` (26% · 17Q) · `D3` (24% · 16Q) · `D4` (18% · 11Q).
> 🧰 **Theme of Mock 03: Advanced Architecture, Performance Trade-offs & Deep-Dive Scenarios (Hardest / Boss Exam).**
> Back to [mock index](../README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D1.2 · Lambda Asynchronous Error Handling & Destinations · Single]`
A financial microservice uses an AWS Lambda function triggered asynchronously by Amazon S3 object creation events to process settlement records. When a settlement record contains malformed transaction data, the Lambda function throws an unhandled runtime error. The engineering team needs to capture the original invocation record, the function response payload, the error message, and the complete stack trace without modifying the application code or writing custom exception logging wrappers.
Which solution meets these requirements with the LEAST operational overhead?
- A. Configure an On-Failure Lambda Destination on the Lambda function pointing to an Amazon SQS queue or Amazon EventBridge.
- B. Configure a standard Dead-Letter Queue (DLQ) on the Lambda function pointing to an Amazon SQS queue.
- C. Wrap the Lambda handler logic in a `try/catch` block and write the stack trace to an Amazon DynamoDB table.
- D. Increase the Lambda retry attempts from 2 to 5 in the asynchronous invocation configuration.

---

### Question 2 — `[D1.3 · DynamoDB Transactional RCU Calculation · Single]`
An inventory management application uses Amazon DynamoDB. During a warehouse auditing process, a background service executes transactional reads using the `TransactGetItems` API.
The audit transaction reads the following items in a single operation:
- 10 items of size **3 KB** each
- 5 items of size **7 KB** each
If the service executes **4 audit transactions per second**, how many Read Capacity Units (RCUs) must be provisioned on the DynamoDB table?
- A. 160 RCUs
- B. 80 RCUs
- C. 40 RCUs
- D. 240 RCUs

---

### Question 3 — `[D1.2 · Lambda Ephemeral Storage (/tmp) for Media Processing · Single]`
A media company runs an AWS Lambda function to generate preview clips from video files stored in Amazon S3. The video source files range in size from 2 GB to 6 GB. Previously, the developer attempted to process the videos in memory, but the function encountered `OutOfMemoryError` failures. The developer wants to download the video files to local disk storage inside the Lambda execution environment, process them with FFmpeg, and upload the preview clip back to S3.
What configuration change should the developer make to support processing files up to 6 GB in Lambda?
- A. Configure the Lambda function's ephemeral storage (`/tmp`) to a custom capacity between 512 MB and 10,240 MB (10 GB).
- B. Mount an Amazon Elastic Block Store (EBS) volume directly to the Lambda function.
- C. Increase the Lambda memory allocation to 10,240 MB, which automatically increases `/tmp` to 10 GB.
- D. Attach an Amazon S3 bucket as a local POSIX file system inside the Lambda function configuration.

---

### Question 4 — `[D1.1 · API Gateway WebSocket APIs · Single]`
A gaming company is developing a multiplayer trivia game that requires bidirectional, real-time message exchange between mobile game clients and backend microservices. The backend must be able to push new trivia questions to connected clients without waiting for clients to poll for updates.
Which solution provides real-time bidirectional communication with the LEAST management overhead?
- A. Create an Amazon API Gateway WebSocket API, use `$connect`, `$disconnect`, and custom routes with Lambda integrations, and push messages to connected clients using the `@connections` API with the stored `connectionId`.
- B. Create an Amazon API Gateway REST API and have mobile clients implement short polling every 500 milliseconds.
- C. Create an API Gateway HTTP API and configure HTTP long polling with a 30-second timeout.
- D. Deploy an Application Load Balancer with an Auto Scaling group of EC2 instances running custom socket.io servers.

---

### Question 5 — `[D1.3 · DynamoDB Atomic Counters vs Conditional Writes · Single]`
An e-commerce flash-sale platform stores product stock levels in an Amazon DynamoDB table. During a promotional sale, thousands of customers attempt to purchase the same limited-inventory product simultaneously. The application must decrement the `stock` attribute by 1 for each successful purchase, but MUST NEVER allow the `stock` attribute to drop below 0 (no overselling).
Which update strategy must the developer use?
- A. Execute an `UpdateItem` operation with an `UpdateExpression` of `SET stock = stock - :val` and a `ConditionExpression` of `stock >= :val`.
- B. Execute an `UpdateItem` operation using an atomic counter with `UpdateExpression` of `ADD stock :negVal`.
- C. Execute a `GetItem` with Strongly Consistent Read to check `stock > 0`, followed by a `PutItem` to write the decremented value.
- D. Use DynamoDB Accelerator (DAX) write-behind caching to serialize updates in memory.

---

### Question 6 — `[D1.1 · SQS Extended Client Library for Large Payloads · Single]`
A medical billing system sends insurance claim records through an Amazon SQS queue to be processed by a backend billing service. Some claim records include high-resolution medical scan attachments, resulting in total message payload sizes between **15 MB and 200 MB**. Standard Amazon SQS queues enforce a strict maximum message size of **256 KB**.
How should the developer handle these large payloads without splitting files or writing custom S3 upload and download boilerplate?
- A. Use the Amazon SQS Extended Client Library for Java or Python, configuring an Amazon S3 bucket to automatically store and retrieve message payloads exceeding 256 KB.
- B. Request a service quota increase from AWS Support to raise the SQS maximum message size to 256 MB.
- C. Compress the payload using gzip before sending it to SQS; gzip is guaranteed to compress 200 MB into under 256 KB.
- D. Use Amazon Kinesis Data Streams instead of Amazon SQS.

---

### Question 7 — `[D1.1 · SQS FIFO High Throughput Mode · Single]`
A financial exchange application processes equity trade orders using an Amazon SQS FIFO queue. Under normal trading hours, the queue handles 250 transactions per second. However, during market opening surges, the transaction volume spikes to **15,000 transactions per second**. By default, SQS FIFO queues support up to 300 transactions per second (without batching) or up to 3,000 transactions per second (with batching).
What should the developer configure to support 15,000 transactions per second while maintaining strict message ordering per customer account?
- A. Enable High Throughput mode for the SQS FIFO queue by setting `DeduplicationScope` to `messageGroup` and `FifoThroughputLimit` to `perMessageGroupId`, and use customer account ID as the `MessageGroupId`.
- B. Switch from SQS FIFO queue to an SQS Standard queue and implement custom sorting logic in the consumer workers.
- C. Create 50 separate standard SQS FIFO queues and hash incoming orders across the queues.
- D. Increase the SQS visibility timeout to 43,200 seconds (12 hours).

---

### Question 8 — `[D1.2 · Lambda Function URLs Authentication & CORS · Single]`
A startup needs to expose a single AWS Lambda function as a public webhook endpoint for a third-party payment processor (Stripe). The webhook requires an HTTPS endpoint that is accessible over the internet, supports CORS, and does not require complex routing, API keys, or request transformations. The developer wants to minimize both operational complexity and AWS service costs.
Which approach meets these requirements?
- A. Create an AWS Lambda Function URL for the function, set the `AuthType` to `NONE`, and configure the Function URL's CORS settings to allow requests from Stripe.
- B. Deploy an Amazon API Gateway REST API with a Regional endpoint and create a Lambda proxy integration.
- C. Deploy an Application Load Balancer (ALB) across two public subnets and register the Lambda function as a target.
- D. Create an Amazon CloudFront distribution pointing directly to the Lambda function's internal ARN.

---

### Question 9 — `[D1.3 · DynamoDB Global Tables Conflict Resolution · Single]`
A multi-region web application uses Amazon DynamoDB Global Tables replicated across `us-east-1` and `eu-west-1`. An application user simultaneously updates their profile from two different devices: Device A connects to `us-east-1` and Device B connects to `eu-west-1`. Both updates attempt to modify the user's phone number attribute at nearly the exact same instant.
How does Amazon DynamoDB Global Tables resolve this concurrent write conflict between regions?
- A. DynamoDB uses a "Last Writer Wins" (LWW) conflict resolution mechanism based on the reconciliation of timestamps recorded when updates are applied.
- B. DynamoDB rejects both writes and returns a `TransactionCanceledException` to both clients.
- C. The region geographically closest to the AWS headquarters in Seattle always takes precedence.
- D. DynamoDB merges the two values into a comma-separated list attribute.

---

### Question 10 — `[D1.1 · Step Functions Distributed Map State · Single]`
A data engineering pipeline in AWS Step Functions needs to process an Amazon S3 bucket containing **500,000 JSON log files** (totaling 2 TB of data). For each file, the workflow must parse the contents, filter errors, and write summarized records to DynamoDB. The existing Step Functions standard `Map` state is constrained by an inline iteration limit and execution history limits (25,000 events), causing the workflow to fail.
Which Step Functions feature should the developer implement to process these 500,000 files in parallel?
- A. Configure the `Map` state in **Distributed Mode** with `ItemReader` reading directly from Amazon S3 (`s3:GetObject`), setting `MaxConcurrency` to run child workflow executions in parallel.
- B. Write a Python script inside a single AWS Lambda function that processes all 500,000 files sequentially in a `for` loop.
- C. Use a Step Functions `Parallel` state with 500,000 hardcoded branch tasks.
- D. Convert the state machine into an Express Workflow.

---

### Question 11 — `[D1.2 · API Gateway Integration Timeout vs Lambda Timeout · Single]`
A web application allows users to request heavy machine learning batch reports through an Amazon API Gateway REST API backed by an AWS Lambda function. The report generation algorithm takes between 45 seconds and 3 minutes to complete. When users invoke the endpoint, the API consistently returns an `HTTP 504 Gateway Timeout` error after exactly **29 seconds**, even though the Lambda function continues running successfully in the background.
What is the root cause of this error, and how should the developer resolve it?
- A. API Gateway has a maximum hard integration timeout limit of 29 seconds; refactor the API to invoke the Lambda function asynchronously (`X-Amz-Invocation-Type: Event`) returning an immediate HTTP 202 Accepted with a task ID, or use AWS Step Functions.
- B. The Lambda function memory allocation is too low; increase memory to 10 GB.
- C. Request an increase in the API Gateway integration timeout quota to 15 minutes by submitting an AWS Support ticket.
- D. Switch from API Gateway REST API to an API Gateway HTTP API, which supports up to 15-minute integration timeouts.

---

### Question 12 — `[D1.3 · DynamoDB FilterExpression vs Query Consumption · Single]`
A developer runs an Amazon DynamoDB `Query` operation on a table with a Partition Key of `DepartmentId` and a Sort Key of `HireDate`. The developer specifies a `KeyConditionExpression` to retrieve all 10,000 employees in `DepartmentId = "ENG"`. Each employee item is 2 KB in size.
To only return active employees, the developer adds a `FilterExpression: "status = :active"`. Exactly 100 out of the 10,000 employees have `status = "ACTIVE"`.
How many Read Capacity Units (RCUs) does this `Query` operation consume for an Eventually Consistent read?
- A. 2,500 RCUs
- B. 25 RCUs
- C. 5,000 RCUs
- D. 50 RCUs

---

### Question 13 — `[D1.1 · SNS Subscription Filter Policies on Attributes · Single]`
An order dispatch system publishes order event messages to an Amazon SNS topic named `OrderEvents`. Different backend fulfillment services must receive subsets of messages:
1. `PharmacyQueue` (SQS) must only receive orders where `category = "PHARMACY"`.
2. `ElectronicsQueue` (SQS) must only receive orders where `category = "ELECTRONICS"` AND `orderValue >= 500`.
The developer wants to prevent fulfillment services from receiving unnecessary messages and wants to avoid writing intermediate filtering Lambda functions.
What should the developer implement?
- A. Define **Subscription Filter Policies** on the respective Amazon SNS subscriptions that evaluate message attributes for exact string matching and numeric range conditions.
- B. Deploy an AWS Lambda function between the SNS topic and the SQS queues to inspect the body and route messages.
- C. Create two separate SNS topics (`PharmacyTopic` and `ElectronicsTopic`) and have publishers double-publish messages.
- D. Configure SQS dead-letter queues to filter messages based on HTTP headers.

---

### Question 14 — `[D1.3 · DynamoDB Local Secondary Index 10 GB Collection Limit · Single]`
An IoT tracking application writes sensor metrics to an Amazon DynamoDB table. The table is created with a Partition Key `DeviceId` and a Sort Key `Timestamp`. The developer also created a Local Secondary Index (LSI) with Sort Key `SensorReading`.
After a single high-frequency industrial sensor generates data for 6 months, writes for that specific `DeviceId` begin failing with an `ItemCollectionSizeLimitExceededException` error, while writes for all other sensors continue normally.
What is the cause of this failure, and what is the permanent architectural resolution?
- A. A table with one or more LSIs imposes a strict 10 GB limit on any single item collection (items sharing the same partition key value); migrate from an LSI to a Global Secondary Index (GSI), which does not impose the 10 GB item collection size restriction.
- B. The DynamoDB table has run out of storage space in the AWS Region; request a table storage increase.
- C. The individual item size exceeded 400 KB; compress the sensor reading payload.
- D. The provisioned WCU on the LSI was exhausted; enable auto-scaling on the LSI.

---

### Question 15 — `[D1.1 · API Gateway Private REST API with VPC Endpoints · Single]`
An enterprise security policy requires an internal microservice hosted on Amazon EC2 instances in a private VPC subnet to access an Amazon API Gateway REST API. The API traffic must NEVER traverse the public internet, and the API must be accessible ONLY from within that specific VPC.
How should the developer configure the API Gateway REST API?
- A. Configure the API Gateway endpoint type as **Private**, create an Interface VPC Endpoint (`com.amazonaws.region.execute-api`) in the VPC, and attach an API Gateway Resource Policy that allows access only from the VPC endpoint ID (`aws:sourceVpce`).
- B. Configure the API Gateway endpoint type as Regional and deploy a NAT Gateway in the private subnet.
- C. Create an Edge-Optimized API Gateway and attach an AWS WAF WebACL restricting traffic to private RFC 1918 IP addresses.
- D. Create an Amazon VPC Peering connection between the customer VPC and the AWS service account VPC.

---

### Question 16 — `[D1.2 · Lambda Layers Immutability & Versioning · Single]`
A developer updates a shared security utility packaged as an AWS Lambda Layer named `SecurityAuthLayer`. The developer publishes a new version of the layer using the AWS CLI:
`aws lambda publish-layer-version --layer-name SecurityAuthLayer --zip-file fileb://layer.zip`
The command returns version `3`.
However, during integration testing of the 10 microservice Lambda functions that use this layer, the functions continue running the old vulnerability-affected version `2` logic.
Why did the Lambda functions fail to use the new layer logic?
- A. Lambda Layer versions are immutable; publishing a new layer version creates a new distinct ARN (ending in `:3`), and each Lambda function must be explicitly updated to reference the new layer version ARN.
- B. Lambda Layers require up to 24 hours to replicate across AWS Availability Zones.
- C. The developer must restart the AWS Lambda service daemon on the underlying host.
- D. Lambda functions automatically pull the latest layer only when the function code itself is re-uploaded.

---

### Question 17 — `[D1.3 · DynamoDB BatchWriteItem & UnprocessedItems · Single]`
A batch import process writes 500 records to an Amazon DynamoDB table using consecutive `BatchWriteItem` API calls (25 items per request). During high-traffic periods, several `BatchWriteItem` calls succeed partially: some items are written successfully, while the API response contains a populated `UnprocessedItems` map. The developer notes that the AWS SDK does NOT automatically throw an exception when `UnprocessedItems` is returned.
How must the developer handle this scenario in application code?
- A. Check the `UnprocessedItems` attribute in the response; if non-empty, implement an exponential backoff and retry loop passing the unprocessed items in subsequent `BatchWriteItem` calls.
- B. Catch the `BatchWriteItemException` and re-execute the entire batch of 25 items from the beginning.
- C. Increase the table's WCU to 40,000 to eliminate unprocessed items permanently.
- D. Switch from `BatchWriteItem` to a single `PutItem` call with a 10-second timeout.

---

### Question 18 — `[D1.1 · SQS Dead-Letter Queue Redrive Task · Single]`
A developer deployed a bug in a worker application that caused 25,000 messages in an Amazon SQS queue to fail processing and be moved to a Dead-Letter Queue (DLQ). The developer fixes and redeploys the worker bug. The developer now needs to move all 25,000 messages from the DLQ back to the primary source queue so the worker can process them.
What is the MOST operationally efficient way to redrive these messages?
- A. Use the **SQS Dead-Letter Queue Redrive** feature directly in the Amazon SQS console or via the `StartMessageMoveTask` API to programmatically move messages from the DLQ back to the source queue.
- B. Write a custom Python script running on an EC2 instance that loops through `ReceiveMessage`, `SendMessage`, and `DeleteMessage` calls.
- C. Purge the DLQ and ask the original message publishers to regenerate all 25,000 messages.
- D. Swap the URLs of the primary queue and the DLQ in the application configuration.

---

### Question 19 — `[D1.2 · Lambda SnapStart for Java Functions · Single]`
An enterprise runs a mission-critical financial calculation API built with Java 17 on AWS Lambda. Due to JVM class loading, JIT compilation, and dependency injection framework initialization (Spring Boot), cold start latency reaches 8 to 11 seconds. The business mandates that cold start latency must be reduced to under 1 second without paying continuously for Provisioned Concurrency.
Which AWS Lambda feature should the developer enable?
- A. AWS Lambda SnapStart for Java
- B. Lambda Response Streaming
- C. AWS Lambda Layers with GraalVM native images
- D. Increase Lambda ephemeral storage `/tmp` to 10 GB

---

### Question 20 — `[D1.1 · Amazon EventBridge Schema Registry & Code Bindings · Single]`
A development team is building an event-driven architecture using Amazon EventBridge. Microservices written in TypeScript and Python produce and consume dozens of custom event types with complex JSON structures. Developers frequently make typos in event property names and struggle to keep track of event schema changes across microservices.
Which Amazon EventBridge capability should the team use to generate typed data bindings and automate schema management?
- A. Amazon EventBridge Schema Registry with Schema Discovery enabled, and download code bindings for TypeScript and Python using the AWS Toolkit or AWS CLI.
- B. Amazon API Gateway Model validation using JSON Schema Draft 4.
- C. AWS CloudTrail Event History with Amazon Athena queries.
- D. AWS Systems Manager Parameter Store with JSON validation rules.

---

### Question 21 — `[D1.3 · AWS AppSync GraphQL Subscriptions · Single]`
A mobile collaboration app requires real-time updates when team members post comments on shared documents. The backend data is managed via an AWS AppSync GraphQL API connected to Amazon DynamoDB.
How does AWS AppSync support real-time data push to mobile clients?
- A. AppSync natively manages real-time updates via GraphQL **Subscriptions**, establishing an automated WebSocket connection between the client and AppSync that triggers on GraphQL mutations.
- B. AppSync requires clients to make repeated HTTP POST queries every 1 second.
- C. AppSync deploys an Amazon SQS queue per mobile device.
- D. AppSync streams data to clients through Amazon Kinesis Video Streams.

---

### Question 22 — `[D2.1 · IAM Permissions Boundaries for Delegated Admins · Single]`
A company wants to empower senior developers to create new IAM roles and attach policies for their serverless Lambda applications. However, the central security team mandates that developers MUST NOT be able to escalate their own privileges or create IAM roles with administrative permissions (such as `AdministratorAccess` or permissions exceeding the developer's assigned scope).
How can the security team enforce this constraint while delegating IAM role creation?
- A. Create an IAM policy with a `Permissions Boundary` defining the maximum allowed permissions, and attach an IAM policy to developers that allows `iam:CreateRole` ONLY IF the `iam:PermissionsBoundary` condition matches the defined boundary ARN.
- B. Attach a Service Control Policy (SCP) to the developer's IAM user.
- C. Require MFA for all AWS Management Console logins.
- D. Use AWS Organizations to place developers in an isolated Organizational Unit (OU) without internet access.

---

### Question 23 — `[D2.2 · KMS Multi-Region Customer Managed Keys · Single]`
A global payment application runs active-active in both `us-east-1` (N. Virginia) and `eu-central-1` (Frankfurt). Credit card numbers are encrypted client-side before being written to an Amazon DynamoDB Global Table. When a transaction is encrypted in `us-east-1`, the application running in `eu-central-1` must be able to decrypt the ciphertext locally in Frankfurt with minimal latency and without making cross-region network calls to `us-east-1` KMS endpoints.
Which AWS KMS feature fulfills this requirement?
- A. Create an **AWS KMS Multi-Region Key** (`mrk-`) primary key in `us-east-1` and replicate it to `eu-central-1`; both keys share the same key ID and key material.
- B. Call `kms:ReEncrypt` across regions whenever an item is replicated by DynamoDB Global Tables.
- C. Export the plaintext KMS private key from `us-east-1` and import it into `eu-central-1`.
- D. Use AWS CloudHSM with manual key replication over an encrypted SSH tunnel.

---

### Question 24 — `[D2.1 · Cognito Pre-Token Generation Lambda Trigger (v2) · Single]`
A SaaS company uses Amazon Cognito User Pools for user authentication. The backend microservices require custom claims inside the OIDC `ID Token` and `Access Token` indicating the tenant ID, billing tier, and enterprise group memberships. These custom attributes reside in an external PostgreSQL database and change dynamically.
Which Amazon Cognito feature allows the developer to customize token claims and scopes immediately before Cognito issues tokens to the user?
- A. Amazon Cognito Pre-Token Generation Lambda Trigger
- B. Amazon Cognito Post-Confirmation Lambda Trigger
- C. Amazon Cognito Pre-Sign-up Lambda Trigger
- D. Amazon Cognito Custom Authentication Challenge

---

### Question 25 — `[D2.2 · Secrets Manager Multi-User Rotation Strategy · Single]`
An application connects to an Amazon RDS PostgreSQL database using credentials managed by AWS Secrets Manager. The application has strict high-availability requirements and cannot tolerate any downtime or failed database connections during the scheduled 30-day credential rotation window.
Which Secrets Manager rotation strategy should the developer implement?
- A. Use the **Multi-User (Alternating Users)** rotation strategy, where Secrets Manager maintains two database users (`User_A` and `User_B`); one user is active while the other is being rotated with the new password.
- B. Use the Single-User rotation strategy during scheduled maintenance windows at midnight.
- C. Disable automatic rotation and update passwords manually once a year.
- D. Hardcode a secondary master password inside the application container image.

---

### Question 26 — `[D2.1 · OIDC Federation for GitHub Actions CI/CD · Single]`
A DevOps team uses GitHub Actions to build and deploy containerized microservices to Amazon ECR and Amazon ECS. Previously, the team stored long-lived AWS IAM User `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in GitHub Secrets. A recent security audit flagged this as a critical vulnerability due to the risk of credential leakage.
What is the recommended AWS best practice to allow GitHub Actions to deploy to AWS without using long-lived access keys?
- A. Configure OpenID Connect (OIDC) identity federation between GitHub Actions and AWS IAM, configure an IAM Role with a trust policy allowing `sts:AssumeRoleWithWebIdentity`, and restrict access using condition `token.actions.githubusercontent.com:sub`.
- B. Store the IAM Access Key in an S3 bucket with public read access.
- C. Create an IAM User with a password and automate console login via Puppeteer.
- D. Use AWS CodeCommit instead of GitHub.

---

### Question 27 — `[D2.2 · KMS Grants for Ephemeral Service Delegation · Single]`
An application running on an Amazon EC2 instance needs to dynamically delegate temporary, programmatic permission to an internal background worker to use an AWS KMS Customer Managed Key (CMK) to decrypt customer data files. The permission must be temporary, easily revoked, and must NOT require modifying or redeploying the static KMS Key Policy.
Which KMS capability should the developer use?
- A. Create an **AWS KMS Grant** (`CreateGrant`) specifying the grantee principal, allowed operations (`Decrypt`), and optionally an encryption context constraint.
- B. Edit the KMS Key Policy JSON document and add the worker's IAM role ARN.
- C. Create an IAM User Access Key and share it over an encrypted SQS queue.
- D. Create an alias for the KMS key named `worker-alias`.

---

### Question 28 — `[D2.1 · S3 Pre-signed URL Enforcing KMS Encryption Headers · Single]`
A web client needs to upload confidential patient medical documents directly to an Amazon S3 bucket using a Pre-signed URL generated by an AWS Lambda function. The security team mandates that every uploaded object must be encrypted at rest using a specific AWS KMS Customer Managed Key (CMK). If a client attempts to upload an object without specifying KMS encryption, the upload must be rejected.
How must the developer implement this?
- A. When generating the Pre-signed URL in Lambda, include `ServerSideEncryption: "aws:kms"` and `SSEKMSKeyId: <KMS_KEY_ARN>`; ensure the client includes the matching `x-amz-server-side-encryption` headers in its HTTP PUT request.
- B. Client-side Pre-signed URLs cannot enforce KMS encryption; files must be uploaded through an API Gateway proxy.
- C. S3 will automatically encrypt objects with KMS without requiring any header in the Pre-signed URL.
- D. Pre-signed URLs only support SSE-S3 (`AES256`), not KMS encryption.

---

### Question 29 — `[D2.2 · Systems Manager Parameter Store Hierarchies & Batch Retrieval · Single]`
A developer manages environment configuration parameters for 10 microservices across `dev`, `staging`, and `prod` environments in AWS Systems Manager Parameter Store. The developer organizes parameters using a path hierarchy:
- `/microservices/orders-service/prod/db_host`
- `/microservices/orders-service/prod/db_port`
- `/microservices/orders-service/prod/api_timeout`
When the `orders-service` microservice initializes in production, it needs to fetch all parameters belonging to its production environment in a single API call with decryption enabled.
Which AWS CLI / SDK command should the developer use?
- A. `aws ssm get-parameters-by-path --path "/microservices/orders-service/prod" --recursive --with-decryption`
- B. `aws ssm get-parameter --name "/microservices/orders-service/prod/*"`
- C. `aws ssm get-parameters --names "/microservices/orders-service/prod"`
- D. `aws ssm describe-parameters --filters "Key=Path,Values=/microservices/orders-service/prod"`

---

### Question 30 — `[D2.1 · IAM Policy Evaluation Logic (Explicit Deny Precedence) · Single]`
An IAM user named `Alice` is assigned an IAM Identity Policy that grants `Allow` for `s3:GetObject` on `arn:aws:s3:::corporate-data/*`.
The S3 bucket `corporate-data` has a Bucket Policy with the following statement:
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::corporate-data/confidential/*"
}
```
When Alice attempts to call `s3:GetObject` on `arn:aws:s3:::corporate-data/confidential/q4_results.xlsx`, what will be the evaluation outcome?
- A. Access is **Denied**, because in AWS IAM policy evaluation, an explicit Deny in any applicable policy always overrides any explicit Allows.
- B. Access is Allowed, because Alice's identity-based policy explicitly allows `s3:GetObject` on the bucket.
- C. Access is Allowed, because identity-based policies have higher priority than resource-based policies.
- D. Alice's IAM user will be automatically deleted by AWS IAM.

---

### Question 31 — `[D2.2 · S3 Bucket Policy Enforcing TLS (aws:SecureTransport) · Single]`
A security audit discovers that an Amazon S3 bucket allows plain unencrypted HTTP requests. The compliance team mandates that all data transferred to and from the S3 bucket must be transmitted over encrypted HTTPS connections (TLS). Any HTTP request must be explicitly rejected.
Which statement in the S3 Bucket Policy achieves this enforcement?
- A.
  ```json
  {
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": [
      "arn:aws:s3:::my-bucket",
      "arn:aws:s3:::my-bucket/*"
    ],
    "Condition": {
      "Bool": {
        "aws:SecureTransport": "false"
      }
    }
  }
  ```
- B.
  ```json
  {
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": "arn:aws:s3:::my-bucket/*",
    "Condition": {
      "StringEquals": {
        "aws:Protocol": "https"
      }
    }
  }
  ```
- C. Enable S3 Object Lock on all existing objects.
- D. Enable Default Encryption with SSE-S3.

---

### Question 32 — `[D2.1 · Cognito User Pool TOTP Software Token MFA · Single]`
A company provides a mobile banking portal using Amazon Cognito User Pools. Due to SIM-swapping attacks, regulatory compliance mandates that Multi-Factor Authentication (MFA) must NOT rely on SMS text messages. Instead, users must use authenticator applications (such as Google Authenticator or 1Password) that generate Time-based One-Time Passwords (TOTP).
How should the developer configure Amazon Cognito User Pools?
- A. In the Cognito User Pool MFA configuration, set MFA to "Required" or "Optional", enable **Time-based One-time Password (TOTP) software token**, and disable SMS text message MFA.
- B. Write a custom Lambda trigger on Pre-Sign-up that sends verification codes via Amazon SES email.
- C. Deploy an Amazon Cognito Identity Pool with IAM role delegation.
- D. Cognito User Pools only support SMS text message MFA.

---

### Question 33 — `[D2.2 · KMS Asymmetric Key Pairs for Digital Signatures · Single]`
A software company distributes signed firmware binary updates to edge IoT devices. The devices need to verify the authenticity and integrity of firmware files using the company's public key. The company must ensure that the private signing key can NEVER be extracted or exported from AWS hardware, even by AWS administrators.
Which AWS KMS configuration should the developer select?
- A. Create an **Asymmetric KMS Key** with Key Spec `RSA_4096` or `ECC_NIST_P256` and Key Usage `SIGN_VERIFY`; generate signatures in the cloud using `kms:Sign`, and distribute the public key to IoT devices.
- B. Create a Symmetric KMS key with `kms:Encrypt`.
- C. Store an OpenSSL private key file in an Amazon S3 bucket encrypted with SSE-KMS.
- D. Store the private key inside an AWS Systems Manager Parameter Store `String` parameter.

---

### Question 34 — `[D2.1 · API Gateway Mutual TLS (mTLS) Authentication · Single]`
A B2B banking integration requires that corporate partner clients authenticate directly at the transport layer using client X.509 certificates when invoking an Amazon API Gateway REST API. The API must verify both client and server identities during the TLS handshake before processing any application-level requests.
Which API Gateway configuration should the developer implement?
- A. Configure **Mutual TLS (mTLS)** on an API Gateway Custom Domain Name, creating a truststore containing the partner Certificate Authority (CA) bundle in an Amazon S3 bucket.
- B. Deploy an AWS WAF WebACL to inspect client certificate HTTP request headers.
- C. Use API Gateway API Keys and Usage Plans.
- D. Configure a Cognito User Pool with client credentials grant.

---

### Question 35 — `[D2.2 · AWS Encryption SDK with Caching CMM · Single]`
A high-throughput application encrypts hundreds of thousands of small data records per second using the AWS Encryption SDK before storing them in Amazon DynamoDB. The application is encountering severe KMS throttling (`KMS ThrottlingException`) and generating thousands of dollars in KMS `GenerateDataKey` API costs.
How can the developer optimize performance and reduce KMS API requests while maintaining envelope encryption?
- A. Implement the **Caching Cryptographic Materials Manager (Caching CMM)** in the AWS Encryption SDK to cache data keys in local memory across encryption requests.
- B. Switch from AWS KMS to plaintext base64 encoding.
- C. Store the master encryption key in a public S3 bucket.
- D. Hardcode a single static AES key in application memory for all records permanently.

---

### Question 36 — `[D2.1 · IAM PassRole Permission · Single]`
A developer attempts to create a new AWS Lambda function and attach an existing IAM execution role named `LambdaDynamoDBExecutionRole` using the AWS CLI:
`aws lambda create-function --function-name DataProcessor --role arn:aws:iam::123456789012:role/LambdaDynamoDBExecutionRole ...`
The command fails with the following error:
`An error occurred (AccessDeniedException) when calling the CreateFunction operation: User: arn:aws:iam::123456789012:user/DevUser is not authorized to perform: iam:PassRole on resource: arn:aws:iam::123456789012:role/LambdaDynamoDBExecutionRole`
Why is the `iam:PassRole` permission required?
- A. `iam:PassRole` authorizes a user to pass an IAM role to an AWS service (such as Lambda or EC2) so the service can assume that role and act on behalf of the user.
- B. `iam:PassRole` allows the developer to modify the trust policy of the role.
- C. `iam:PassRole` converts an IAM User into an IAM Role.
- D. The developer typed the wrong function name.

---

### Question 37 — `[D2.2 · Secrets Manager Caching Client Library · Single]`
A high-traffic e-commerce microservice deployed on AWS Lambda queries AWS Secrets Manager on every incoming HTTP request to fetch a third-party payment API token. Under peak traffic of 5,000 requests per second, the microservice fails with `ThrottlingException` errors from Secrets Manager, and Secrets Manager API call costs skyrocket.
What is the recommended best practice to eliminate throttling and reduce costs?
- A. Use the **AWS Secrets Manager Caching Client library** to cache secrets in memory with a configurable Time to Live (TTL), reusing the cached secret across warm Lambda invocations.
- B. Request a service limit increase to 100,000 requests/second from AWS Support.
- C. Store the payment API token directly in the function's Git repository.
- D. Hardcode the token in the frontend React client bundle.

---

### Question 38 — `[D2.1 · S3 Block Public Access (BPA) Precedence · Single]`
An AWS account administrator configures Amazon S3 Block Public Access at the **AWS Account level**, enabling "Block public access to buckets and objects granted through new access control lists (ACLs)" and "Block public access to buckets and objects granted through any access control lists (ACLs)".
A junior developer creates a new S3 bucket in this account and attaches an S3 Bucket Policy granting public `s3:GetObject` permission to `Principal: "*"`.
What is the resulting accessibility of objects in this S3 bucket?
- A. Objects remain **completely private** and inaccessible to the public; S3 Block Public Access settings at the account level take precedence over individual bucket policies and ACLs.
- B. Objects become publicly readable because bucket policies override account-level settings.
- C. The bucket is automatically deleted by AWS.
- D. The bucket is accessible only via SSH.

---

### Question 39 — `[D3.1 · CodeBuild Local and S3 Artifact Caching · Single]`
A complex Java Maven project built in AWS CodeBuild takes 18 minutes to complete. Analysis of the build logs reveals that 14 minutes are spent re-downloading thousands of Maven dependencies and Docker base image layers on every build run.
How can the developer reduce build execution time with the MINIMAL architectural change?
- A. In the CodeBuild project settings and `buildspec.yml`, configure **Build Caching** using local caching (custom directory for `.m2/repository` and Docker layer cache mode) or Amazon S3 caching.
- B. Increase the CodeBuild compute environment from `BUILD_GENERAL1_SMALL` to `BUILD_GENERAL1_2XLARGE`.
- C. Write a custom cron script on an EC2 instance to download dependencies.
- D. Check in all Maven dependency JAR files directly into the Git repository.

---

### Question 40 — `[D3.2 · CodeDeploy AppSpec Hooks for EC2 vs Lambda · Single]`
A developer needs to configure lifecycle validation scripts in an `appspec.yml` file for an application deployed to an Auto Scaling group of Amazon EC2 instances. The deployment must execute a script to stop the local service, install new files, start the service, and verify that the local HTTP endpoint returns `200 OK`.
Which sequence of lifecycle hooks should the developer define in `appspec.yml`?
- A. `ApplicationStop` → `BeforeInstall` → `AfterInstall` → `ApplicationStart` → `ValidateService`
- B. `BeforeAllowTraffic` → `AllowTraffic` → `AfterAllowTraffic`
- C. `BeforeInstall` → `Install` → `AfterInstall` → `AllowTestTraffic`
- D. `DownloadBundle` → `StartContainers` → `StopContainers`

---

### Question 41 — `[D3.3 · CodePipeline Manual Approval Stage with SNS · Single]`
A development team wants to implement a Continuous Delivery pipeline using AWS CodePipeline. The pipeline must build and deploy code to a `Staging` environment automatically, run automated integration tests, and then pause execution until a QA Lead explicitly reviews test reports and approves deployment to `Production`.
How should the developer configure this workflow in CodePipeline?
- A. Add an **Approval** action of type `Manual` between the Staging and Production stages, configuring an Amazon SNS topic to notify the QA Lead via email with an approval/rejection link.
- B. Write a custom Lambda function that sleeps in an infinite loop for 7 days.
- C. Create two completely separate AWS CodePipelines in different AWS accounts.
- D. Use a GitHub webhook to disable git merge commits.

---

### Question 42 — `[D3.4 · CloudFormation Cross-Stack References (Export & ImportValue) · Single]`
A DevOps engineer maintains two separate CloudFormation stacks:
1. `NetworkStack`: Provisions a VPC, public and private subnets, and internet gateways.
2. `AppStack`: Provisions an Application Load Balancer and EC2 Auto Scaling group.
The `AppStack` needs to reference the private subnet IDs created by `NetworkStack`.
What is the standard AWS CloudFormation mechanism to share resource values across stacks?
- A. In `NetworkStack`, export the subnet IDs in the `Outputs` section using the `Export: Name:` attribute; in `AppStack`, reference the exported values using the `Fn::ImportValue` intrinsic function.
- B. Hardcode the generated Subnet IDs into `AppStack` template parameters.
- C. Write an AWS Lambda custom resource that queries the EC2 API on every deployment.
- D. Combine both stacks into a single 5,000-line template.

---

### Question 43 — `[D3.4 · CloudFormation Custom Resources with Lambda · Single]`
A team deploys an Amazon Aurora PostgreSQL database using AWS CloudFormation. After the database cluster is successfully created, the stack must automatically connect to PostgreSQL, create an initial application database schema, and populate default reference lookup tables. CloudFormation does not have a native resource type for executing SQL commands on an arbitrary PostgreSQL database.
Which CloudFormation feature enables this custom workflow?
- A. Create a **CloudFormation Custom Resource** (`Custom::DatabaseInitializer`) backed by an AWS Lambda function that executes the SQL scripts inside the VPC and returns a status response to the presigned S3 URL (`cfn-response`).
- B. Embed SQL statements directly into the `Parameters` section of the template.
- C. Use the `AWS::CloudFormation::WaitCondition` resource with an SQS queue.
- D. Run SQL commands inside the CloudFormation stack policy.

---

### Question 44 — `[D3.4 · SAM Template Globals Section · Single]`
A developer writes an AWS Serverless Application Model (SAM) template that defines 12 different AWS Lambda functions (`AWS::Serverless::Function`). All 12 functions require identical configuration values: `Runtime: nodejs18.x`, `Timeout: 30`, `MemorySize: 512`, and an environment variable `STAGE: prod`.
How can the developer define these shared properties once, avoiding repetitive code in each function resource?
- A. Define the shared properties inside the top-level **`Globals:`** section under `Function:`.
- B. Define the shared properties inside `Metadata:`.
- C. Create an IAM policy with the environment variables.
- D. SAM templates do not support global configuration inheritance.

---

### Question 45 — `[D3.4 · Elastic Beanstalk Traffic Splitting Deployment · Single]`
A company runs a high-traffic production web service on AWS Elastic Beanstalk. Management requires a deployment policy that:
1. Deploys the new application release to an isolated temporary fleet of instances.
2. Directs a small percentage of real production traffic (e.g., 10%) to the new version for an evaluation period (e.g., 15 minutes) while 90% stays on the old version.
3. Automatically cancels the deployment and rolls back to the old version if CloudWatch alarms report elevated error rates during the evaluation period.
4. Promotes 100% of traffic to the new version if the evaluation passes successfully.
Which Elastic Beanstalk deployment policy meets these requirements?
- A. **Traffic Splitting**
- B. All at once
- C. Rolling
- D. Rolling with additional batch

---

### Question 46 — `[D3.4 · ECS Task Definition Task Role vs Task Execution Role · Single]`
A developer containerizes a microservice to run on Amazon ECS on AWS Fargate. The container needs to:
1. Allow the ECS agent to authenticate to Amazon ECR to pull the private container image and stream container logs to Amazon CloudWatch Logs.
2. Allow the application code running inside the container to read and write items in an Amazon DynamoDB table.
Which IAM roles must the developer configure in the ECS Task Definition?
- A. Configure the **Task Execution Role** (`executionRoleArn`) with permissions for ECR and CloudWatch Logs; configure the **Task Role** (`taskRoleArn`) with permissions for Amazon DynamoDB.
- B. Configure the Task Role with ECR and CloudWatch Logs permissions; leave Task Execution Role empty.
- C. Assign an IAM role directly to the AWS Fargate hypervisor instance.
- D. Embed the AWS IAM access keys in the Dockerfile `ENV` variables.

---

### Question 47 — `[D3.4 · CloudFormation Drift Detection · Single]`
An operations engineer suspects that an administrator manually changed an EC2 security group rule and modified an RDS instance class directly in the AWS Management Console, bypassing the source-controlled CloudFormation template that manages the stack.
How can the engineer identify all out-of-band modifications made to the stack's resources?
- A. Run **CloudFormation Drift Detection** on the stack to compare the actual resource configurations with the template definitions and view detailed drift status.
- B. View the AWS CloudTrail event history for the past 90 days.
- C. Re-deploy the CloudFormation template using `sam deploy`.
- D. Delete the CloudFormation stack and recreate it from scratch.

---

### Question 48 — `[D3.1 · CodeBuild VPC Access for Private Database Integration Tests · Single]`
A continuous integration pipeline in AWS CodeBuild runs integration test suites against an Amazon Aurora MySQL database cluster hosted in private subnets of a VPC. During the `build` phase, test scripts attempt to connect to the database endpoint `aurora-db.cluster-custom.us-east-1.rds.amazonaws.com:3306`, but the connection times out.
What configuration must the developer apply to the AWS CodeBuild project?
- A. Configure the CodeBuild project to enable **VPC access**, selecting the VPC ID, private subnet IDs, and a security group that is allowed ingress in the Aurora database security group.
- B. Assign a public IPv4 address to the Amazon Aurora database cluster.
- C. Place the database credentials in AWS Secrets Manager.
- D. Download the database data into CodeBuild ephemeral disk storage.

---

### Question 49 — `[D3.4 · CloudFormation Rollback Failed State Recovery · Single]`
A CloudFormation stack update fails due to a configuration error in an RDS database instance. CloudFormation initiates a rollback, but the rollback also fails because an Amazon S3 bucket designated for deletion contains non-empty objects. The stack enters the **`UPDATE_ROLLBACK_FAILED`** state.
What action must the developer take to restore the stack to a working state?
- A. Empty the S3 bucket (or fix the underlying blocking issue), and call `ContinueUpdateRollback` (optionally specifying the S3 bucket in `ResourcesToSkip`).
- B. Delete the AWS account and re-register.
- C. Update the stack template and click `CreateStack`.
- D. CloudFormation stacks in `UPDATE_ROLLBACK_FAILED` can never be recovered and must be abandoned.

---

### Question 50 — `[D3.2 · CodeDeploy Deployment Alarms & Automatic Rollback · Single]`
A development team deploys an updated Lambda function using AWS CodeDeploy with a Canary deployment configuration (`LambdaCanary10Percent5Minutes`). The team wants CodeDeploy to automatically halt the deployment and roll back 100% of traffic to the original version if an Amazon CloudWatch alarm monitoring `5XXError` spikes during the 5-minute canary window.
Where should the developer configure this behavior?
- A. In the CodeDeploy Deployment Group settings, configure **Deployment Alarms** with the CloudWatch alarm and enable **Automatic Rollback** when alarms are triggered.
- B. Write a bash script that listens to CloudWatch metrics and calls `aws deploy stop-deployment`.
- C. In the `appspec.yml` file under `files` section.
- D. CodeDeploy does not support automated rollback based on CloudWatch Alarms.

---

### Question 51 — `[D3.4 · SAM Accelerate for Rapid Serverless Development · Single]`
A developer working on an AWS SAM application finds that running `sam build` followed by `sam deploy` takes 3 to 4 minutes on every minor code tweak because CloudFormation must compute change sets and update stack resources. The developer wants to synchronize local code changes directly to AWS Lambda within seconds during active development.
Which AWS SAM CLI command should the developer use?
- A. `sam sync --watch`
- B. `sam deploy --fast`
- C. `sam local invoke --sync`
- D. `sam publish`

---

### Question 52 — `[D3.4 · Elastic Beanstalk Worker Environment Architecture · Single]`
A web application receives intensive image-processing requests. The developer decides to offload image processing to an **AWS Elastic Beanstalk Worker Environment**.
How does the Elastic Beanstalk Worker tier deliver tasks from an Amazon SQS queue to the application running on EC2 worker instances?
- A. Elastic Beanstalk runs a background daemon named **`sqsd`** on each EC2 worker instance; `sqsd` polls the SQS queue and sends messages to the local application via HTTP `POST` requests to `http://localhost/`.
- B. The worker instances connect to SQS using WebSocket streaming.
- C. SQS pushes messages directly to the public IP address of each worker EC2 instance.
- D. The developer must write a custom multi-threaded SQS poller in application code.

---

### Question 53 — `[D3.3 · CodePipeline Monorepo Filtering with EventBridge · Single]`
An organization stores three independent microservices (`service-a`, `service-b`, and `service-c`) in a single monorepo on GitHub. Each microservice has its own dedicated AWS CodePipeline. When a developer pushes a commit modifying files only in `/service-a/`, ONLY `Pipeline-A` should be triggered; `Pipeline-B` and `Pipeline-C` must NOT run.
How should the developer configure this selective triggering?
- A. Use **Amazon EventBridge** rules that evaluate GitHub push webhook events, filtering on the file paths changed in the commit, to trigger only the matching CodePipeline.
- B. CodePipeline natively inspects Git subdirectories without extra configuration.
- C. Create three separate branches in GitHub for each microservice.
- D. Merge all three pipelines into a single pipeline with manual approvals.

---

### Question 54 — `[D3.4 · CloudFormation Template Transforms · Single]`
In an AWS CloudFormation template, a developer wants to use simplified serverless resource types like `AWS::Serverless::Function` and `AWS::Serverless::SimpleTable`.
Which top-level declaration MUST be present in the CloudFormation template to enable CloudFormation to expand these serverless macros?
- A. `Transform: AWS::Serverless-2016-10-31`
- B. `AWSTemplateFormatVersion: '2010-09-09'`
- C. `Description: Serverless Application`
- D. `Metadata: AWS::CloudFormation::Serverless`

---

### Question 55 — `[D4.1 · CloudWatch Metric Math SEARCH and Aggregate Expressions · Single]`
An operations engineer needs to monitor an Auto Scaling group of 50 Amazon EC2 instances where instances are continuously being terminated and launched. The engineer wants to create a single CloudWatch dashboard widget showing the average CPU utilization across all current and future EC2 instances without manually adding new instance IDs to the dashboard.
Which CloudWatch feature solves this dynamically?
- A. Use CloudWatch **Metric Math** with the `SEARCH()` function (e.g., `SEARCH('{AWS/EC2,AutoScalingGroupName} MetricName="CPUUtilization"', 'Average', 300)`).
- B. Write a cron script that calls `PutMetricAlarm` every time an instance launches.
- C. Enable EC2 Detailed Monitoring on each instance.
- D. Create an Amazon SQS queue to collect CloudWatch metrics.

---

### Question 56 — `[D4.2 · CloudWatch High-Resolution Custom Metrics · Single]`
A high-frequency trading application requires monitoring of transaction order processing latency with a granularity of **1 second**. Standard CloudWatch custom metrics aggregate data with a minimum resolution of 1 minute (60 seconds).
How can the developer publish and alarm on sub-minute metrics in Amazon CloudWatch?
- A. Call `PutMetricData` specifying `StorageResolution: 1` in the `MetricDatum`, creating a **High-Resolution Custom Metric**.
- B. High-resolution metrics require an enterprise AWS Support contract and cannot be published via API.
- C. Call `PutMetricData` 60 times per minute with standard resolution.
- D. Stream the metrics to an S3 Glacier Flexible Retrieval vault.

---

### Question 57 — `[D4.2 · AWS X-Ray Sampling Rules Configuration · Single]`
An API handles 10,000 requests per second. Recording an AWS X-Ray trace for 100% of requests would incur high service costs and degrade application performance. The developer wants to ensure that X-Ray traces **at least 1 request per second** consistently, plus **5% of all additional requests** exceeding that initial rate.
How should the developer configure the AWS X-Ray Sampling Rule?
- A. Set `ReservoirSize: 1` and `FixedRate: 0.05` (5%).
- B. Set `ReservoirSize: 100` and `FixedRate: 1.0`.
- C. Set `ReservoirSize: 0.05` and `FixedRate: 1`.
- D. Set `SamplingMode: Random` with a 50% rate.

---

### Question 58 — `[D4.2 · AWS X-Ray Annotations vs Metadata · Single]`
A developer instruments a microservice with AWS X-Ray. The developer wants to record two types of trace details:
1. `customerTier` (e.g., "PLATINUM", "STANDARD") — operations engineers need to query and filter traces in the X-Ray console using filter expressions like `annotation.customerTier = "PLATINUM"`.
2. `rawPayloadData` — a 5 KB JSON debug payload that should be inspected when viewing a single trace, but does NOT need to be indexed or searchable.
How should the developer record these details in the X-Ray subsegment?
- A. Record `customerTier` as an **Annotation** (`putAnnotation`); record `rawPayloadData` as **Metadata** (`putMetadata`).
- B. Record both values as Annotations.
- C. Record both values as Metadata.
- D. Record `customerTier` in CloudWatch Metrics and `rawPayloadData` in DynamoDB.

---

### Question 59 — `[D4.1 · CloudWatch Embedded Metric Format (EMF) · Single]`
A high-throughput serverless microservice running on AWS Lambda needs to emit custom business metrics (e.g., `OrderProcessedCount`, `OrderProcessingTime`). Calling the standard `PutMetricData` API synchronously inside the Lambda handler adds 50 to 100 milliseconds of network latency to every customer request and risks hitting API throttling limits.
What is the recommended pattern to generate custom CloudWatch metrics asynchronously without adding network latency?
- A. Print metrics to `stdout` formatted according to the **CloudWatch Embedded Metric Format (EMF)** JSON specification; CloudWatch Logs automatically extracts and publishes the metrics asynchronously.
- B. Launch an Amazon EC2 instance in the same VPC to collect metrics over UDP.
- C. Write metrics to an Amazon SQS queue and process them with another Lambda function.
- D. Store metrics in a local `/tmp` file and delete them when the container shuts down.

---

### Question 60 — `[D4.3 · CloudFront Cache Policy vs Origin Request Policy · Single]`
A web application uses Amazon CloudFront in front of an API origin. The origin needs to receive the `User-Agent` and `Authorization` headers to authenticate clients and customize content. However, caching responses based on `User-Agent` causes the cache hit ratio to plummet near 0% because every browser version creates a distinct cache key entry.
How should the developer configure CloudFront to forward these headers to the origin without fragmenting the cache?
- A. Create a **Cache Policy** that does NOT include `User-Agent` in the cache key; create an **Origin Request Policy** that forwards `User-Agent` and `Authorization` to the origin.
- B. Whitelist `User-Agent` in the Cache Policy.
- C. Disable CloudFront caching completely.
- D. Use Lambda@Edge to strip the `User-Agent` header.

---

### Question 61 — `[D4.1 · Kinesis Enhanced Fan-Out Latency Optimization · Single]`
A stock trading dashboard consumes market data from an Amazon Kinesis Data Stream. The dashboard application uses standard Kinesis consumer polling (`GetRecords`). Traders complain that price updates appear on the dashboard with a 1,000 to 1,500 millisecond delay. The technical requirement is to reduce the end-to-end propagation latency between Kinesis and the consumer to under **100 milliseconds**.
What architectural change achieves this?
- A. Register the dashboard consumer as an **Enhanced Fan-Out** consumer and use the HTTP/2 `SubscribeToShard` push API, delivering records with an average latency of ~70 ms.
- B. Double the number of shards in the Kinesis Data Stream.
- C. Decrease the Kinesis stream data retention period from 7 days to 24 hours.
- D. Replace Kinesis Data Streams with Amazon S3.

---

### Question 62 — `[D4.3 · ElastiCache Cache Stampede / Thundering Herd Prevention · Multi — Choose 2]`
An online media portal uses Amazon ElastiCache for Redis to cache trending news articles. When a hot breaking news article's cache key expires (TTL reaches 0), hundreds of concurrent web application workers simultaneously discover the cache miss and query the backend PostgreSQL database for the exact same article at the same millisecond. This sudden spike in database queries overwhelms and crashes the PostgreSQL database (Cache Stampede / Thundering Herd problem).
Which two techniques mitigate this cache stampede? (Choose two.)
- A. Implement a distributed mutex lock (locking the cache key) so only one worker queries the database while other workers wait or receive stale data.
- B. Implement probabilistic early expiration (e.g., XFetch algorithm) where workers asynchronously refresh the cache key before it officially expires.
- C. Set the cache TTL to 0 seconds.
- D. Disable ElastiCache Redis clustering.
- E. Route all read traffic directly to the PostgreSQL database primary node.

---

### Question 63 — `[D4.1 · Amazon S3 Request Rate Limits & Prefix Partitioning · Single]`
A data ingestion pipeline uploads 20,000 image files per second to a single Amazon S3 bucket. All files are uploaded with keys formatted as `s3://image-ingestion-bucket/2026/09/26/image_12345.jpg`. Under this load, S3 responds with `HTTP 503 Slow Down` errors.
What is the root cause of these errors, and how should the developer resolve them?
- A. Amazon S3 automatically scales to 3,500 PUT/POST/DELETE and 5,500 GET requests per second per partitioned prefix; storing all images under a single date prefix `/2026/09/26/` exceeds the 3,500 PUT limit. Distribute objects across multiple prefixes using random hashes or customer IDs (e.g., `s3://image-ingestion-bucket/<hash>/image_12345.jpg`).
- B. The Amazon S3 bucket has exceeded its maximum total object limit.
- C. S3 Transfer Acceleration was not enabled on the bucket.
- D. The developer forgot to set `StorageClass: INTELLIGENT_TIERING`.

---

### Question 64 — `[D4.2 · CloudWatch Composite Alarms · Single]`
An operations team experiences "alert fatigue" because whenever an Amazon EC2 instance undergoes a routine batch job, multiple separate CloudWatch alarms fire simultaneously: `HighCPUUtilization`, `HighDiskReadOps`, and `LowFreeMemory`. The team wants to receive a paging alert ONLY when `HighCPUUtilization` is in ALARM **AND** `LowFreeMemory` is in ALARM at the same time.
Which CloudWatch feature should the developer implement?
- A. Create a **CloudWatch Composite Alarm** that uses a boolean rule expression: `ALARM("HighCPUUtilization") AND ALARM("LowFreeMemory")`.
- B. Configure a single metric alarm with an evaluation period of 7 days.
- C. Combine the metrics using CloudWatch Logs Insights.
- D. Disable all alarms and rely on manual dashboard checks.

---

### Question 65 — `[D4.3 · API Gateway Throttling Limits & 429 Too Many Requests · Single]`
An API client application invoking an Amazon API Gateway REST API suddenly begins receiving `HTTP 429 Too Many Requests` responses. The developer investigates and finds that the API client is assigned to a Usage Plan with a Rate limit of **500 requests per second** and a Burst limit of **1,000 requests**. During a sudden batch operation, the client sent 1,200 requests in a 100-millisecond window.
What algorithm does Amazon API Gateway use for throttling, and how should the client handle the 429 response?
- A. API Gateway uses the **Token Bucket algorithm**; the burst of 1,200 requests exhausted the bucket capacity of 1,000 tokens. The client must implement exponential backoff and jitter on HTTP 429 responses.
- B. API Gateway uses Round Robin routing; the client must change its IP address.
- C. The backend Lambda function crashed; the client must increase Lambda memory.
- D. The client must disable HTTPS and use HTTP.
