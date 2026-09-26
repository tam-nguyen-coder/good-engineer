# 🎯 DVA-C02 Mock Exam 02 — 65 questions · 130 minutes

> **Exam-realistic full-length mock.** Distribution strictly follows official AWS DVA-C02 domain weights.
> ⏱️ Set a timer for **130 minutes** (~2 minutes per question). No notes, no documentation, no pausing.
> 🔒 Answers, explanations, and per-domain scoring: [answers.md](answers.md). Attempt everything first.
> Formats: `Single` (1 correct out of 4) · `Multi` (choose the stated number of options).
> Tag: `[Domain.Task · Service · Format]`. Domains: `D1` (32% · 21Q) · `D2` (26% · 17Q) · `D3` (24% · 16Q) · `D4` (18% · 11Q).
> 🧰 **Theme of Mock 02: Deployment Lifecycle, Orchestration & Troubleshooting.**
> Back to [mock index](../README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D1.2 · Lambda VPC Networking · Single]`
An AWS Lambda function is configured to connect to an Amazon RDS MySQL database inside a private subnet of a Virtual Private Cloud (VPC). The function also needs to call an external payment gateway API over the public internet. During testing, the function successfully connects to RDS, but calls to the external payment API consistently fail with connection timeout errors.
What network configuration must the developer implement to allow the Lambda function to reach the external payment API?
- A. Deploy a NAT Gateway in a public subnet, add a route in the private subnet's route table pointing `0.0.0.0/0` to the NAT Gateway, and ensure the VPC has an attached Internet Gateway.
- B. Attach an Internet Gateway directly to the private subnet where the Lambda function's Elastic Network Interfaces (ENIs) reside.
- C. Assign a public IPv4 address directly to the Lambda function in the AWS Lambda configuration console.
- D. Create an Amazon VPC endpoint for the external payment gateway's public IP address.

### Question 2 — `[D1.2 · Lambda Provisioned Concurrency & Auto Scaling · Single]`
A financial services API built on AWS Lambda experiences severe tail latency spikes every morning at 09:00 AM due to cold starts when hundreds of thousands of users open the mobile app. The developer wants to eliminate cold starts during business hours (09:00 AM – 05:00 PM) while avoiding paying for idle provisioned capacity overnight.
What solution meets these requirements with the LEAST operational overhead?
- A. Configure Provisioned Concurrency on the Lambda function's production alias, and configure Application Auto Scaling with scheduled scaling actions to increase provisioned concurrency at 08:50 AM and decrease it at 05:10 PM.
- B. Write a CloudWatch Events / EventBridge rule that invokes the Lambda function every 5 minutes with a dummy test payload.
- C. Increase the Lambda function's timeout from 30 seconds to 900 seconds.
- D. Configure Reserved Concurrency on the function with a value of 500.

### Question 3 — `[D1.2 · Lambda Layers · Single]`
A developer maintains 15 different AWS Lambda functions across several microservices. All 15 functions require a common proprietary business logic library (15 MB) and the `boto3` SDK. Deploying each function involves bundling this library into every ZIP archive, resulting in slow deployment pipelines and code duplication.
How should the developer package and share this common library?
- A. Package the proprietary library into an AWS Lambda Layer, publish the layer, and configure each of the 15 Lambda functions to reference the layer's ARN.
- B. Store the library code in an Amazon DynamoDB table and fetch it dynamically during every function execution.
- C. Embed the library code in the function's environment variables.
- D. Place the library on an Amazon S3 bucket and have the Lambda handler run `pip install` from S3 into `/tmp` at the start of each execution.

### Question 4 — `[D1.2 · Lambda Response Streaming · Single]`
A web application uses an AWS Lambda function behind an Application Load Balancer (ALB) to generate large, multi-megabyte PDF financial reports. Users complain that they experience long delays before any content appears in the browser, and occasionally the request times out with an HTTP 504 error. The developer wants the browser to start receiving document bytes as soon as the first chunk is generated, rather than waiting for the entire document to be assembled in memory.
Which AWS Lambda feature should the developer implement?
- A. Use AWS Lambda Response Streaming by wrapping the handler with `awslambda.streamifyResponse` (in Node.js) to stream response payloads incrementally through chunked transfer encoding.
- B. Compress the PDF report using ZIP compression before returning it from the handler.
- C. Split the PDF generation into 10 smaller Lambda functions and invoke them concurrently via Step Functions.
- D. Increase the ephemeral storage `/tmp` of the Lambda function to 10 GB.

### Question 5 — `[D1.3 · DynamoDB Transactional Capacity · Single]`
An e-commerce order management system uses Amazon DynamoDB. When a customer places an order, the application must atomically update two tables:
1. Deduct inventory in the `Products` table (item size 2 KB).
2. Insert a new record in the `Orders` table (item size 1 KB).
The developer uses the `TransactWriteItems` API to execute both operations atomically in an all-or-nothing transaction.
If the application processes 20 orders per second, how many Write Capacity Units (WCUs) must be provisioned across these operations?
- A. `Products`: 40 WCUs; `Orders`: 20 WCUs (Total: 60 WCUs)
- B. `Products`: 80 WCUs; `Orders`: 40 WCUs (Total: 120 WCUs)
- C. `Products`: 20 WCUs; `Orders`: 20 WCUs (Total: 40 WCUs)
- D. `Products`: 40 WCUs; `Orders`: 40 WCUs (Total: 80 WCUs)

### Question 6 — `[D1.3 · DynamoDB TTL Configuration · Single]`
A mobile gaming application records user session events in an Amazon DynamoDB table. Business rules mandate that session data older than 30 days must be deleted to minimize storage costs. The developer wants to automatically expire and delete these items without consuming provisioned write throughput (WCUs) and without writing custom deletion scripts.
How should the developer configure DynamoDB?
- A. Enable Time to Live (TTL) on the table, specify an attribute name (e.g., `expiration_time`), and ensure the application stores the expiration timestamp in Unix epoch time format (in seconds).
- B. Enable TTL and store the expiration timestamp as an ISO-8601 string (`YYYY-MM-DDTHH:mm:ssZ`).
- C. Create an AWS Lambda function triggered by Amazon EventBridge every midnight to run a `Scan` and `BatchWriteItem` deletion.
- D. Enable DynamoDB Streams and configure an Amazon SQS queue to delete expired items.

### Question 7 — `[D1.3 · DynamoDB Accelerator (DAX) Caching · Single]`
A real-time bidding platform uses Amazon DynamoDB to serve product catalog data. Read latency must be reduced from single-digit milliseconds to microseconds, and the application experiences millions of repeated reads per second for popular items. The developer implements Amazon DynamoDB Accelerator (DAX).
How does DAX handle read requests when an application makes `GetItem` and `Query` calls?
- A. DAX uses an Item Cache for `GetItem`/`BatchGetItem` and a Query Cache for `Query`/`Scan` operations; if a requested item is in the cache, DAX returns it with microsecond latency without hitting the underlying DynamoDB table.
- B. DAX only caches `Scan` operations; all `GetItem` requests are routed directly to DynamoDB.
- C. DAX caches writes asynchronously but forwards all read operations to the DynamoDB read replicas.
- D. DAX requires the developer to rewrite application queries using Redis commands.

### Question 8 — `[D1.3 · DynamoDB PartiQL · Single]`
A developer needs to query and update items in an Amazon DynamoDB table using familiar SQL-compatible syntax (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) from within an internal administrative dashboard application.
Which DynamoDB capability should the developer use?
- A. PartiQL for DynamoDB
- B. Amazon Athena federated queries
- C. Amazon Redshift Spectrum
- D. DynamoDB Local Secondary Index

### Question 9 — `[D1.1 · API Gateway Canary Deployments · Single]`
A company exposes its core business logic through an Amazon API Gateway REST API. The team wants to test a new version of the API in production by routing **10% of user traffic** to the new version, while sending the remaining **90% of traffic** to the existing stable version. If metrics look healthy over 2 hours, the team wants to promote the new version to handle 100% of traffic with zero downtime.
Which Amazon API Gateway feature should the developer use?
- A. Enable Canary release deployment on the API Gateway stage, set the canary percentage to 10%, verify metrics, and then promote the canary.
- B. Create two separate stages (`prod-v1` and `prod-v2`) and use Route 53 Weighted Routing between the two stage URLs.
- C. Use API Gateway stage variables to dynamically calculate a random integer between 1 and 10 in a Lambda authorizer.
- D. Deploy an Application Load Balancer in front of API Gateway and configure weighted target groups.

### Question 10 — `[D1.1 · API Gateway Lambda Authorizer · Single]`
A mobile application invokes an Amazon API Gateway REST API. Clients authenticate against an external OAuth 2.0 identity provider that issues custom bearer tokens with proprietary cryptographic claims. API Gateway must validate this token against a remote verification endpoint, inspect custom user permissions, and enforce fine-grained access control before allowing the request through to the backend microservice.
Which authorization mechanism should the developer choose?
- A. API Gateway Lambda Authorizer (TOKEN or REQUEST type)
- B. Amazon Cognito User Pool Authorizer
- C. API Gateway Usage Plans and API Keys
- D. Standard IAM execution role attached to the client

### Question 11 — `[D1.1 · API Gateway Mapping Templates · Single]`
An existing backend SOAP/XML service is being exposed to modern web clients via an Amazon API Gateway REST API. Web clients send JSON payloads:
```json
{
  "customerId": "CUST-10492",
  "action": "QUERY_STATUS"
}
```
The backend service expects an XML envelope:
```xml
<Request><CustomerId>CUST-10492</CustomerId><Action>QUERY_STATUS</Action></Request>
```
How can the developer transform the incoming JSON payload to XML without deploying an intermediary compute layer like AWS Lambda?
- A. Create a Velocity Template Language (VTL) mapping template in the API Gateway Integration Request with Content-Type `application/xml` that extracts values using `$input.path('$.customerId')` and `$input.path('$.action')`.
- B. Configure AWS WAF to rewrite the incoming HTTP request payload before forwarding it to API Gateway.
- C. Use API Gateway Stage Variables to store the XML string format.
- D. Configure an API Gateway Mock Integration.

### Question 12 — `[D1.3 · Amazon S3 Select · Single]`
An analytics service stores 50 GB CSV files containing billions of customer clickstream logs in an Amazon S3 bucket. A developer needs to extract only records where `country_code = 'VN'` and `device_type = 'MOBILE'`. These filtered records represent less than 0.5% (approx 250 MB) of the total file size. Currently, downloading the entire 50 GB file to an EC2 instance before filtering takes several minutes and consumes high network bandwidth.
What feature should the developer use to optimize query performance and reduce network transfer costs?
- A. Use Amazon S3 Select to run SQL queries directly on the S3 objects and retrieve only the matching data subsets.
- B. Enable S3 Transfer Acceleration on the bucket.
- C. Configure S3 Cross-Region Replication to an EC2 instance ephemeral drive.
- D. Enable S3 Object Lock on the CSV files.

### Question 13 — `[D1.1 · SQS Dead-Letter Queue & Redrive · Single]`
A backend application processes messages from an Amazon SQS queue. Some corrupted messages contain invalid formats that cause the worker application to crash every time it receives them. Because the worker crashes, the messages return to the queue after the visibility timeout expires and are reprocessed indefinitely, blocking the queue and wasting compute resources.
How should the developer prevent these "poison pill" messages from perpetually recycling through the queue?
- A. Configure a Dead-Letter Queue (DLQ) on the source queue with a `RedrivePolicy` that specifies `maxReceiveCount = 3`; after 3 failed receive attempts, SQS automatically moves the message to the DLQ.
- B. Set the source queue's `DelaySeconds` attribute to 86,400 seconds (24 hours).
- C. Increase the queue's `MessageRetentionPeriod` to 14 days.
- D. Lower the visibility timeout to 0 seconds.

### Question 14 — `[D1.1 · Amazon Kinesis Shards & Throughput · Single]`
An application streams real-time financial ticker data into an Amazon Kinesis Data Stream. The stream currently has **4 shards**. The application produces data at an average rate of **3.5 MB/sec** and **3,200 records/sec**. During peak market openings, the write rate surges to **5.5 MB/sec** and **5,000 records/sec**, causing the producer application to receive `ProvisionedThroughputExceededException` errors.
What action should the developer take to accommodate the peak write traffic?
- A. Reshard the stream by splitting existing shards to increase the shard count from 4 shards to at least 6 shards (capacity: 6 MB/sec and 6,000 records/sec).
- B. Increase the retention period of the stream from 24 hours to 7 days.
- C. Enable Enhanced Fan-Out on the producer application.
- D. Change the partition key to a static hardcoded constant string.

### Question 15 — `[D1.1 · Kinesis Enhanced Fan-Out · Single]`
A media company has an Amazon Kinesis Data Stream receiving live video telemetry data. Three separate consumer applications (real-time dashboard, anomaly detector, and long-term archiver) consume data from the stream. As the number of consumers grew from one to three, all consumers started experiencing read throughput throttling (`ReadProvisionedThroughputExceeded` errors).
How should the developer configure the Kinesis Data Stream to provide dedicated read throughput to each consumer application without contention?
- A. Register each consumer application as an Enhanced Fan-Out consumer using the `SubscribeToShard` API, which provides each consumer with dedicated 2 MB/sec read throughput per shard.
- B. Add more shards to the stream and configure all consumers to read using standard `GetRecords` polling.
- C. Place an Amazon SQS queue between the Kinesis stream and each consumer.
- D. Increase the Kinesis stream buffer size in AWS Systems Manager.

### Question 16 — `[D1.1 · Step Functions Error Handling · Single]`
A developer designs an AWS Step Functions state machine to process credit card payments. If the payment gateway returns an HTTP 500 error, the task state should retry the operation with exponential backoff up to 3 times. If the payment gateway returns an HTTP 400 error (Invalid Card Number), the state machine should immediately route the execution to a `SendFailureNotification` state without retrying.
How should the developer configure the task state in the Amazon States Language (ASL)?
- A. Configure a `Retry` block matching error `States.Http500` with `IntervalSeconds`, `MaxAttempts: 3`, and `BackoffRate: 2.0`; and configure a `Catch` block matching error `States.Http400` that specifies `Next: "SendFailureNotification"`.
- B. Write a custom bash loop inside the payment gateway Docker container.
- C. Use a `Choice` state prior to the payment task to inspect the future HTTP response code.
- D. Configure an SQS DLQ directly inside the Step Functions activity worker.

### Question 17 — `[D1.1 · Step Functions Input and Output Processing · Single]`
A Step Functions state machine executes a Lambda task state that takes an input payload containing customer account details. The task calls a credit rating service, which returns a small JSON result `{"creditScore": 750}`. The developer wants the state's output to include BOTH the original customer input payload AND the `creditScore` result, nested under the key `ratingDetails`.
Which Amazon States Language (ASL) field should the developer configure in the Task state?
- A. `ResultPath: "$.ratingDetails"`
- B. `InputPath: "$.ratingDetails"`
- C. `OutputPath: "$.ratingDetails"`
- D. `Parameters: "$.ratingDetails"`

### Question 18 — `[D1.3 · S3 Object Versioning & Lifecycle Rules · Single]`
An application stores frequently modified configuration files in an Amazon S3 bucket with S3 Versioning enabled. Over several months, the storage costs have multiplied tenfold because every overwrite creates a new noncurrent version. The developer wants to automatically permanently delete noncurrent versions 30 days after they become noncurrent, and also delete expired object delete markers.
How should the developer implement this?
- A. Configure an S3 Lifecycle rule with actions: `NoncurrentVersionExpiration` set to 30 days, and enable `ExpiredObjectDeleteMarkers: true`.
- B. Disable S3 Versioning on the bucket.
- C. Write an AWS Lambda function that runs every hour to list all versions and call `DeleteObject`.
- D. Configure S3 Object Lock in Governance mode with a 30-day retention period.

### Question 19 — `[D1.3 · S3 CORS Configuration · Single]`
A client-side JavaScript application running in web browsers on `https://portal.example.com` attempts to load custom font files (`.woff2`) stored in an Amazon S3 bucket `s3://company-assets-prod`. The browser blocks the font files from loading with a CORS error: `No 'Access-Control-Allow-Origin' header is present on the requested resource`.
What must the developer add to the S3 bucket configuration?
- A. Configure a CORS rule on the S3 bucket allowing `AllowedOrigins: ["https://portal.example.com"]`, `AllowedMethods: ["GET", "HEAD"]`, and `AllowedHeaders: ["*"]`.
- B. Change the S3 bucket policy to grant `s3:GetObject` to `Principal: "*"`.
- C. Enable S3 Transfer Acceleration on the bucket.
- D. Create an IAM role for web identity federation.

### Question 20 — `[D1.1 · SQS Message Deduplication · Single]`
A financial reporting microservice publishes messages to an Amazon SQS FIFO queue. During high-traffic bursts, the publisher application retries API calls when it encounters temporary network blips. The developer needs to ensure that duplicate messages sent within a 5-minute interval are recognized and discarded by Amazon SQS.
What two methods can be used to ensure message deduplication in an SQS FIFO queue? (Choose two.)
- A. Explicitly provide a unique `MessageDeduplicationId` for each message when calling `SendMessage`.
- B. Enable Content-Based Deduplication on the FIFO queue, which generates a deduplication ID from the SHA-256 hash of the message body.
- C. Set `ReceiveMessageWaitTimeSeconds` to 300 seconds.
- D. Decrease the visibility timeout of the queue to 0 seconds.
- E. Append a random timestamp string to the end of the `MessageGroupId`.

### Question 21 — `[D1.3 · DynamoDB Global Secondary Index Throttling · Single]`
An application writes data to an Amazon DynamoDB table configured with Provisioned Capacity (1,000 WCUs). The table has a Global Secondary Index (GSI) provisioned with only 100 WCUs. During a peak load event where the application writes 600 items per second (consuming 600 WCUs on the base table), the application receives `ProvisionedThroughputExceededException` errors on base table write operations.
What is the reason for these write throttling errors?
- A. If a write to a DynamoDB table updates an attribute projected into a GSI, DynamoDB must write to both the base table and the GSI; if the GSI lacks sufficient write capacity, writes to the base table are throttled.
- B. The base table exceeded its provisioned 1,000 WCUs.
- C. GSI writes consume RCU instead of WCU.
- D. DynamoDB automatically deletes items from the base table when a GSI is overloaded.

---

### Question 22 — `[D2.1 · STS Cross-Account & Confused Deputy · Single]`
A SaaS company builds a multi-tenant monitoring product in **Account A (Vendor)**. The product requires access to read Amazon CloudWatch metrics and EC2 metadata in customer AWS accounts (e.g., **Account B (Customer)**). The customer creates an IAM role in Account B that trusts Account A's IAM role.
What critical security mechanism must the customer configure in the role trust policy to protect against the **Confused Deputy** vulnerability?
- A. Add a `Condition` block to the role trust policy requiring a unique, secret `sts:ExternalId` supplied by the SaaS vendor for each tenant.
- B. Restrict access using the `aws:SourceIp` condition key set to the customer's on-premises IP address.
- C. Use AWS KMS customer managed keys with annual rotation.
- D. Grant the vendor an IAM user access key with MFA enabled.

### Question 23 — `[D2.1 · IAM Policies with Condition Keys · Single]`
A developer needs to create an IAM policy that allows developers in an organization to create and terminate EC2 instances, but ONLY if the instances are launched with a specific cost-allocation tag: `Environment = Development`. If a user attempts to launch an EC2 instance without this tag, the request must be denied.
Which IAM policy condition key should the developer use?
- A. `"Condition": {"StringEquals": {"aws:RequestTag/Environment": "Development"}}`
- B. `"Condition": {"StringEquals": {"aws:PrincipalTag/Environment": "Development"}}`
- C. `"Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}`
- D. `"Condition": {"IpAddress": {"aws:SourceIp": "10.0.0.0/16"}}`

### Question 24 — `[D2.1 · IAM Resource-Based vs Identity-Based Policies · Single]`
An Amazon SQS queue in **Account A** needs to receive messages sent by an AWS Lambda function running in **Account B**.
What is the MOST operationally efficient way to grant Account B's Lambda function permission to send messages to Account A's queue without requiring role switching or temporary STS credentials?
- A. Attach an SQS Queue Policy (resource-based policy) to the queue in Account A that grants `sqs:SendMessage` to Account B's Lambda execution role ARN.
- B. Have the Lambda function call `sts:AssumeRole` to assume an IAM role in Account A.
- C. Create an IAM user in Account A and embed the access key in the Lambda environment variables.
- D. Use AWS Organizations to merge Account A and Account B into a single account.

### Question 25 — `[D2.1 · Cognito User Pool Hosted UI & PKCE · Single]`
A developer is building a public Single Page Application (SPA) using React that authenticates users against an Amazon Cognito User Pool. Because SPAs run entirely in client-side browser JavaScript, they cannot securely store a `client_secret`.
Which OAuth 2.0 grant flow and security mechanism should the developer configure in Amazon Cognito for this SPA client?
- A. Authorization code grant with Proof Key for Code Exchange (PKCE) and no client secret.
- B. Implicit grant flow with a hardcoded client secret.
- C. Client credentials grant flow.
- D. Resource owner password credentials (ROPC) flow storing the admin password in local storage.

### Question 26 — `[D2.1 · Cognito User Pools vs Identity Pools Credentials · Single]`
A developer is designing a photo storage application. When a user logs in via Amazon Cognito User Pools, the application receives three tokens: `ID Token`, `Access Token`, and `Refresh Token`. The mobile client now needs to call the Amazon S3 `PutObject` API.
Can the application use the Cognito User Pool Access Token directly in the HTTP Authorization header to upload files to Amazon S3?
- A. No; User Pool tokens are OIDC/OAuth 2.0 JWTs that AWS service APIs like S3 do not accept directly. The client must pass the ID Token to an Amazon Cognito Identity Pool to obtain temporary AWS STS credentials (`AccessKeyId`, `SecretAccessKey`, `SessionToken`).
- B. Yes; the Access Token can be passed directly as a Bearer token to Amazon S3.
- C. Yes; the ID Token can be converted to an IAM role using the AWS CLI.
- D. No; the user must be converted into an IAM user in the AWS Management Console.

### Question 27 — `[D2.2 · KMS Key Policy Cross-Account · Single]`
An Amazon S3 bucket in Account A is encrypted with an AWS KMS Customer Managed Key (CMK) also located in Account A. An application running under an IAM role in Account B needs to upload objects to this bucket. The S3 bucket policy in Account A already grants `s3:PutObject` to Account B's role. However, when Account B's application attempts to upload an object, it receives an `Access Denied` error from AWS KMS.
What must be updated to resolve this issue?
- A. The KMS Key Policy in Account A must be updated to allow Account B (or Account B's role) permission to call `kms:GenerateDataKey` and `kms:Decrypt`, AND the IAM role policy in Account B must allow those same KMS actions on the key ARN.
- B. Account B must create an identical KMS key with the same key ID.
- C. The S3 bucket must be switched to use SSE-S3.
- D. The developer must disable the KMS key policy.

### Question 28 — `[D2.2 · KMS Encryption Context · Single]`
A developer encrypts sensitive employee salary records stored in Amazon DynamoDB using the AWS KMS SDK. The developer wants to ensure that encrypted ciphertext data keys cannot be maliciously decrypted and swapped between different employee records.
Which AWS KMS feature provides additional authenticated data (AAD) that must match between encryption and decryption calls?
- A. KMS Encryption Context (a set of key-value pairs passed to `Encrypt`/`GenerateDataKey` and validated during `Decrypt`)
- B. KMS Key Policy
- C. KMS Key Alias
- D. KMS Asymmetric Signature

### Question 29 — `[D2.2 · Secrets Manager Multi-Region Replication · Single]`
A disaster recovery requirement dictates that a mission-critical web application running in `us-east-1` must be capable of failing over to `us-west-2` within 10 minutes. The application connects to an Amazon Aurora Global Database. Database credentials are stored in AWS Secrets Manager in `us-east-1`.
How should the developer manage database credentials in `us-west-2` to support seamless failover?
- A. Configure Secrets Manager Multi-Region secret replication from `us-east-1` to `us-west-2`; Secrets Manager automatically keeps the replica secret synchronized and encrypted under a KMS key in `us-west-2`.
- B. Write a cron script that calls `GetSecretValue` in `us-east-1` and `CreateSecret` in `us-west-2` every hour.
- C. Share the `us-east-1` secret ARN across regions over a VPC peering connection.
- D. Store credentials in plaintext inside a Git repository.

### Question 30 — `[D2.2 · SSM Parameter Store SecureString & KMS · Single]`
A developer needs to store a third-party payment API secret key in AWS Systems Manager Parameter Store. The secret must be encrypted at rest and only accessible by authorized Lambda functions.
Which parameter type and encryption configuration should the developer choose?
- A. `SecureString` parameter type, encrypted with a Customer Managed Key (CMK) or the default AWS KMS key for Systems Manager (`aws/ssm`).
- B. `String` parameter type with an attached IAM policy.
- C. `StringList` parameter type with base64 encoding.
- D. `SecureBinary` parameter type.

### Question 31 — `[D2.1 · IAM Policy Simulator · Single]`
A developer has crafted an intricate IAM policy with multiple statements, condition keys, and resource wildcards for an application role. Before attaching the policy to production roles, the developer needs to test and verify whether specific API actions (e.g., `s3:GetObject`, `dynamodb:PutItem`) will be allowed or denied for various context parameters without actually executing the actions against real AWS resources.
Which AWS tool should the developer use?
- A. AWS IAM Policy Simulator
- B. AWS CloudTrail Event History
- C. AWS Config Rules
- D. Amazon Inspector

### Question 32 — `[D2.2 · S3 Object Lock & Compliance · Single]`
A healthcare application must store medical audit logs in Amazon S3 for exactly 7 years. Regulatory compliance mandates that once an object is written, it CANNOT be overwritten or deleted by any user—including the AWS account root user—until the 7-year retention period expires.
Which Amazon S3 feature meets this strict requirement?
- A. Amazon S3 Object Lock in **Compliance Mode** with a retention period of 7 years.
- B. Amazon S3 Object Lock in **Governance Mode** with a retention period of 7 years.
- C. S3 Versioning enabled with an S3 Lifecycle rule.
- D. An S3 bucket policy with an explicit Deny for `s3:DeleteObject`.

### Question 33 — `[D2.1 · Cognito User Pool Hosted UI Branding · Single]`
A startup uses Amazon Cognito User Pools for customer authentication. To build customer trust, the login page must display the company's logo, custom CSS stylesheets, and be served from the company's custom domain name (`auth.example.com`).
What configuration allows the developer to customize the Cognito authentication experience?
- A. Configure a custom domain for the Cognito User Pool Hosted UI, associate an ACM SSL/TLS certificate in the `us-east-1` region, and upload custom CSS via the User Pool console.
- B. Host a static login webpage on Amazon EC2 and call the Cognito private API.
- C. Cognito Hosted UI does not support custom branding or custom domains.
- D. Deploy an NGINX reverse proxy inside an on-premises datacenter.

### Question 34 — `[D2.2 · AWS Secrets Manager vs Parameter Store Cost · Single]`
A software company manages 2,500 non-sensitive environment configuration parameters (URLs, timeouts, feature toggles) and 10 database passwords across 50 microservices. The engineering lead wants to optimize AWS monthly costs while adhering to best practices.
What is the MOST cost-effective storage allocation?
- A. Store the 2,500 non-sensitive configuration parameters in AWS Systems Manager Parameter Store (Standard tier is free), and store the 10 database passwords needing automatic rotation in AWS Secrets Manager ($0.40/secret/month).
- B. Store all 2,510 parameters in AWS Secrets Manager.
- C. Store all parameters in Amazon DynamoDB.
- D. Store all parameters in Amazon S3 standard storage class.

### Question 35 — `[D2.1 · IAM Role Session Tags · Single]`
An enterprise uses an external SAML 2.0 identity provider to federate employees into an AWS account. Developers assume the `EngineeringRole` when accessing AWS. A security architect wants to write a single IAM policy that automatically restricts each developer to accessing only the Amazon S3 objects within their own department folder (`s3://company-shared/${aws:PrincipalTag/Department}/*`).
Which IAM feature allows attributes from the identity provider to be passed into the temporary AWS STS session?
- A. IAM Role Session Tags
- B. IAM Permissions Boundary
- C. Service Control Policies (SCPs)
- D. IAM Access Analyzer

### Question 36 — `[D2.2 · KMS ReEncrypt API · Single]`
A company migrates encrypted customer records stored in Amazon S3 from an old KMS Customer Managed Key (`CMK-Alpha`) to a new KMS Customer Managed Key (`CMK-Beta`) to comply with a corporate divestiture. The developer needs to re-encrypt the data under the new key without exposing the plaintext data to the application memory or network.
Which AWS KMS API should the developer invoke?
- A. `kms:ReEncrypt`
- B. `kms:Decrypt` followed by `kms:Encrypt`
- C. `kms:GenerateDataKey`
- D. `kms:UpdateKey`

### Question 37 — `[D2.1 · SQS Queue Policy Least Privilege · Single]`
A developer needs to configure an Amazon SQS queue named `OrderProcessingQueue` in Account A so that an Amazon SNS topic named `OrderEventsTopic` in Account B can publish messages into it.
Which policy should the developer configure on the SQS queue?
- A. An SQS Queue Policy granting `sqs:SendMessage` with `"Principal": {"AWS": "arn:aws:iam::AccountB:root"}` and a condition `"ArnEquals": {"aws:SourceArn": "arn:aws:sns:region:AccountB:OrderEventsTopic"}`.
- B. An IAM policy attached to Account A root user.
- C. An S3 bucket policy.
- D. Enable public access on the SQS queue.

### Question 38 — `[D2.2 · Secrets Manager Rotation Lambda Function · Single]`
When AWS Secrets Manager automatically rotates a secret for an Amazon RDS database, what are the four lifecycle steps executed by the rotation Lambda function?
- A. `createSecret` → `setSecret` → `testSecret` → `finishSecret`
- B. `generateSecret` → `applySecret` → `verifySecret` → `completeSecret`
- C. `initSecret` → `encryptSecret` → `saveSecret` → `closeSecret`
- D. `checkSecret` → `rotateSecret` → `auditSecret` → `publishSecret`

---

### Question 39 — `[D3.2 · CodeDeploy Lambda Deployment Configurations · Single]`
A development team wants to deploy a new version of an AWS Lambda function using AWS CodeDeploy. The team wants to shift **10% of traffic** to the new version every **10 minutes** until 100% of traffic is shifted to the new version.
Which CodeDeploy deployment configuration should the developer select?
- A. `CodeDeployDefault.LambdaLinear10PercentEvery10Minutes`
- B. `CodeDeployDefault.LambdaCanary10Percent10Minutes`
- C. `CodeDeployDefault.LambdaCanary10Percent5Minutes`
- D. `CodeDeployDefault.LambdaAllAtOnce`

### Question 40 — `[D3.2 · CodeDeploy ECS Lifecycle Hook Sequence · Single]`
In an Amazon ECS blue/green deployment orchestrated by AWS CodeDeploy, what is the exact execution order of lifecycle hooks?
- A. `BeforeInstall` → `Install` → `AfterInstall` → `AllowTestTraffic` → `AfterAllowTestTraffic` → `BeforeAllowTraffic` → `AllowTraffic` → `AfterAllowTraffic`
- B. `ApplicationStop` → `DownloadBundle` → `BeforeInstall` → `Install` → `AfterInstall` → `ApplicationStart`
- C. `BeforeAllowTraffic` → `AllowTraffic` → `AfterAllowTraffic`
- D. `Install` → `AllowTraffic` → `ValidateService`

### Question 41 — `[D3.4 · CloudFormation Stack Policies · Single]`
A critical production CloudFormation stack contains an Amazon RDS Multi-AZ database instance named `ProductionDatabase` and several EC2 instances. The team wants to allow developers to update the stack (e.g., adding EC2 instances or updating alarms), but wants to prevent any accidental deletion or replacement of the `ProductionDatabase` resource during stack updates.
What should the developer attach to the CloudFormation stack?
- A. A CloudFormation **Stack Policy** with a statement denying `Update:Replace` and `Update:Delete` on the `ProductionDatabase` logical resource.
- B. An IAM permissions boundary on all developers.
- C. An S3 bucket policy.
- D. An SCP in AWS Organizations.

### Question 42 — `[D3.4 · CloudFormation DeletionPolicy Attribute · Single]`
A developer defines an Amazon DynamoDB table in an AWS CloudFormation template. If the CloudFormation stack is deleted or if the table resource is removed from the template during an update, the team mandates that a final snapshot backup of the table must be created before the table is destroyed.
Which attribute must the developer add to the DynamoDB resource in the template?
- A. `DeletionPolicy: Snapshot`
- B. `DeletionPolicy: Retain`
- C. `DeletionPolicy: Delete`
- D. `UpdatePolicy: Backup`

### Question 43 — `[D3.4 · SAM CLI Local Testing · Single]`
A developer is writing an AWS Lambda function that handles API Gateway requests using the AWS Serverless Application Model (SAM). The developer wants to test the API locally on their development laptop by simulating HTTP requests and receiving responses without deploying any resources to AWS.
Which AWS SAM CLI command should the developer run?
- A. `sam local start-api`
- B. `sam local invoke`
- C. `sam deploy --dry-run`
- D. `sam test`

### Question 44 — `[D3.4 · Elastic Beanstalk Configuration Files (.ebextensions) · Single]`
A developer needs to configure environment properties, install custom Linux software packages (such as `htop` and `git`), and run shell configuration commands on Amazon EC2 instances launched by AWS Elastic Beanstalk.
Where should the developer place these configuration files in the application source bundle?
- A. Inside a top-level directory named `.ebextensions` with files having the extension `.config` (e.g., `.ebextensions/app.config`).
- B. Inside the `src/` directory in a file named `beanstalk.json`.
- C. In the root directory in a file named `appspec.yml`.
- D. In the root directory in a file named `buildspec.yml`.

### Question 45 — `[D3.4 · Elastic Beanstalk Procfile · Single]`
A developer is packaging a Node.js web application for AWS Elastic Beanstalk. The application has two components: a main web server listening on port 5000 and a background worker script that consumes tasks from SQS.
What configuration file should the developer include in the root directory of the application source bundle to instruct Elastic Beanstalk on how to start both processes?
- A. A file named `Procfile` containing entries such as `web: npm start` and `worker: node worker.js`.
- B. An `appspec.yml` file.
- C. A `docker-compose.yml` file.
- D. A `package.json` scripts section only.

### Question 46 — `[D3.4 · ECS Rolling Update Capacity Parameters · Single]`
An Amazon ECS service runs with a desired task count of 4 tasks on AWS Fargate. During a rolling deployment of a new task definition revision, the application must NEVER experience a reduction in capacity below 4 running tasks (100% capacity), and the service must not exceed 6 running tasks (150% capacity) due to memory reservation limits on the cluster.
How should the developer configure the deployment parameters in the ECS service definition?
- A. Set `minimumHealthyPercent = 100` and `maximumPercent = 150`.
- B. Set `minimumHealthyPercent = 50` and `maximumPercent = 100`.
- C. Set `minimumHealthyPercent = 0` and `maximumPercent = 200`.
- D. Set `minimumHealthyPercent = 100` and `maximumPercent = 100`.

### Question 47 — `[D3.3 · CodePipeline Artifact S3 Encryption · Single]`
An enterprise security policy mandates that all build artifacts produced by AWS CodeBuild and passed between stages in AWS CodePipeline must be encrypted at rest using an AWS KMS Customer Managed Key (CMK) instead of the default AWS managed key (`aws/s3`).
Where must the developer configure the KMS CMK?
- A. In the CodePipeline configuration, configure the pipeline's artifact store (Amazon S3 bucket) with the KMS CMK ARN, and grant CodeBuild and CodePipeline IAM service roles permission to use the KMS key.
- B. Hardcode the KMS key inside the application source code.
- C. Upload the KMS key to GitHub.
- D. CodePipeline artifact stores only support SSE-S3.

### Question 48 — `[D3.4 · CloudFormation Nested Stacks · Single]`
A company maintains a large CloudFormation template with more than 500 resources, exceeding the maximum CloudFormation template resource limit (500 resources). The architecture contains reusable components (VPC networking, security groups, database tiers) that are shared across multiple stacks.
How should the developer refactor the CloudFormation infrastructure?
- A. Use **CloudFormation Nested Stacks** by breaking the architecture into dedicated templates, storing them in Amazon S3, and referencing them from a root stack using `AWS::CloudFormation::Stack` resources.
- B. Increase the CloudFormation template resource limit by contacting AWS Support.
- C. Convert the resources into a shell script and run it on an EC2 instance.
- D. Merge all resources into a single DynamoDB table.

### Question 49 — `[D3.4 · CloudFormation Helper Scripts (cfn-init) · Single]`
An Amazon EC2 instance defined in a CloudFormation template needs to install Apache, download an application archive from S3, and start the service when the instance launches. The developer wants to use CloudFormation metadata to define the packages, files, and commands, and ensure CloudFormation waits until the setup completes successfully before marking stack creation as `CREATE_COMPLETE`.
Which combination of CloudFormation helper scripts and resources should the developer use?
- A. Define metadata under `AWS::CloudFormation::Init`, invoke `cfn-init` in the EC2 user data, and use `cfn-signal` with a `CreationPolicy` on the EC2 resource to notify CloudFormation of success.
- B. Invoke `cfn-hup` in a cron job and use an SQS queue.
- C. Use `sam build` inside the EC2 user data.
- D. Run `aws deploy create-deployment` in the EC2 user data.

### Question 50 — `[D3.1 · CodeBuild Custom Docker Images · Single]`
A continuous integration build in AWS CodeBuild requires a legacy compiler and specialized testing tools that are not installed on any of the standard AWS CodeBuild managed container environments.
How can the developer run builds with these specific tools?
- A. Build a custom Docker image containing the required compiler and tools, push the image to an Amazon ECR repository, and configure the CodeBuild project to use the custom Docker image.
- B. Submit a feature request to AWS Support to add the compiler to the standard Amazon Linux 2 runtime.
- C. Install the compiler during the `post_build` phase in `buildspec.yml`.
- D. CodeBuild does not support custom container images.

### Question 51 — `[D3.2 · CodeDeploy Deployment Groups · Single]`
A developer needs to configure AWS CodeDeploy to deploy an application revision to a fleet of 20 EC2 instances. The deployment must deploy to instances in batches of 5 instances at a time. If more than 2 instances in any batch fail, the deployment must stop.
What should the developer configure?
- A. In the CodeDeploy Deployment Group, create a custom Deployment Configuration with `minimumHealthyHosts` set to `FLEET_PERCENT: 75%` or type `HOST_COUNT: 15`.
- B. Write a custom bash loop on the developer's local laptop that calls `aws deploy create-deployment` 4 times.
- C. Configure an Elastic Beanstalk environment.
- D. Use CodePipeline manual approvals between each instance.

### Question 52 — `[D3.3 · CodePipeline Action Types · Single]`
In AWS CodePipeline, which valid action categories are natively supported in pipeline stages?
- A. `Source`, `Build`, `Test`, `Deploy`, `Approval`, and `Invoke`
- B. `Package`, `Compile`, `Verify`, `Ship`
- C. `Download`, `Execute`, `Audit`, `Publish`
- D. `Input`, `Process`, `Output`

### Question 53 — `[D3.4 · SAM Policy Templates · Single]`
In an AWS Serverless Application Model (SAM) template, a developer needs to grant an AWS Lambda function permission to perform read and write operations on an Amazon DynamoDB table.
Instead of writing a verbose raw IAM policy statement, which SAM feature provides pre-defined, least-privilege policy scopes?
- A. SAM Policy Templates (e.g., `DynamoDBCrudPolicy: { TableName: !Ref MyTable }`)
- B. IAM Permissions Boundary
- C. AWS Organizations SCP
- D. CloudFormation Metadata

### Question 54 — `[D3.4 · CloudFormation DependsOn Attribute · Single]`
In an AWS CloudFormation template, an Amazon EC2 instance needs to communicate through an Internet Gateway. Both the EC2 instance and the VPC Gateway Attachment (`AWS::VPCGatewayAttachment`) are created in the same template. CloudFormation attempts to launch the EC2 instance before the Internet Gateway has finished attaching to the VPC, resulting in a network failure during EC2 bootstrap.
How can the developer explicitly enforce the creation order?
- A. Add the `DependsOn: VPCGatewayAttachment` attribute to the EC2 instance resource definition.
- B. Use the `!Ref` intrinsic function on the security group.
- C. Add a `WaitCondition` timer of 60 seconds.
- D. Split the template into two separate AWS accounts.

---

### Question 55 — `[D4.1 · CloudWatch Logs Insights Query Syntax · Single]`
An operations team needs to query an Amazon CloudWatch Logs log group containing millions of API access logs to identify the top 20 slowest requests in the last 24 hours. The log events contain the fields `@timestamp`, `@message`, and `durationMs`.
Which CloudWatch Logs Insights query syntax achieves this requirement?
- A.
  ```sql
  fields @timestamp, @message, durationMs
  | filter durationMs > 0
  | sort durationMs desc
  | limit 20
  ```
- B.
  ```sql
  SELECT @timestamp, @message, durationMs FROM log_group ORDER BY durationMs DESC LIMIT 20
  ```
- C.
  ```sql
  grep "durationMs" | sort -r | head -n 20
  ```
- D.
  ```sql
  fields @timestamp, @message | count(durationMs) by bin(5m)
  ```

### Question 56 — `[D4.2 · CloudWatch Alarms Missing Data Handling · Single]`
A serverless photo editing microservice runs an AWS Lambda function only when customers upload photos. On weekend nights, there are hours where zero photos are uploaded, and the Lambda function emits no metric data points. A CloudWatch alarm configured on the `Errors` metric intermittently enters the `INSUFFICIENT_DATA` state and triggers false-positive paging alerts to on-call engineers.
How should the developer configure the CloudWatch alarm to prevent these false alerts during periods of zero traffic?
- A. Configure the alarm's `TreatMissingData` setting to `notBreaching` (treat missing data as within threshold).
- B. Configure `TreatMissingData` to `breaching`.
- C. Increase the alarm evaluation period to 24 hours.
- D. Configure the Lambda function to emit metric points of 0 every 10 seconds using an EC2 cron instance.

### Question 57 — `[D4.2 · CloudWatch Agent Memory Metrics · Single]`
A developer notices that an Amazon EC2 instance running a Java web service is crashing due to Out Of Memory (OOM) errors. However, the standard CloudWatch metrics dashboard for the EC2 instance only shows `CPUUtilization`, `DiskReadBytes`, and `NetworkIn`. The memory usage metric is completely missing.
Why is memory utilization missing from standard EC2 metrics, and what is the solution?
- A. RAM utilization is an operating-system-level metric that the underlying EC2 hypervisor cannot inspect; install and configure the Unified Amazon CloudWatch Agent on the EC2 instance to collect and publish `mem_used_percent`.
- B. The developer forgot to enable Detailed Monitoring on the EC2 instance.
- C. The instance type does not support memory monitoring.
- D. Memory metrics can only be gathered using AWS CloudTrail.

### Question 58 — `[D4.2 · X-Ray Custom Subsegments · Single]`
A developer is instrumenting a Node.js microservice with the AWS X-Ray SDK. The service receives an HTTP request, calls an internal helper function that performs a complex 3-second mathematical calculation, and then calls an external third-party payment API over HTTPS. In the X-Ray service map, the 3-second calculation time is lumped into the main Lambda execution segment and cannot be distinguished.
What should the developer do to isolate the mathematical calculation as an independent, timed step on the X-Ray trace timeline?
- A. Create a custom **Subsegment** around the mathematical calculation code block using `AWSXRay.captureFunc()` or `segment.addNewSubsegment()`, and close the subsegment when the calculation completes.
- B. Add an X-Ray annotation with the duration of the calculation.
- C. Add an X-Ray metadata field with the calculation start and end timestamps.
- D. Call `PutMetricData` before and after the calculation.

### Question 59 — `[D4.2 · X-Ray Daemon on Amazon ECS Fargate · Single]`
A developer containerizes a microservice to run on Amazon ECS with the **AWS Fargate** launch type. The application is instrumented with the AWS X-Ray SDK. Because Fargate is a serverless container environment, the developer cannot access the underlying EC2 host to install the X-Ray daemon.
How should the developer deploy the AWS X-Ray daemon on ECS Fargate?
- A. Add the official AWS X-Ray daemon container (`amazon/aws-xray-daemon`) as a **sidecar container** in the same ECS task definition, mapping port `2000/udp`.
- B. Install the X-Ray daemon inside the application container's Dockerfile.
- C. Fargate does not support AWS X-Ray tracing.
- D. Configure a VPC Peering connection to an EC2 instance running the X-Ray daemon.

### Question 60 — `[D4.1 · Kinesis Consumer ExpiredIteratorException · Single]`
A Python worker application uses the AWS SDK to read records from an Amazon Kinesis Data Stream using the `GetRecords` API. The worker application processes records in batches. Under high data volume, the worker takes longer than 5 minutes to process a single batch of records. On the next call to `GetRecords`, the application crashes with an `ExpiredIteratorException`.
What is the root cause of this error, and how should it be resolved?
- A. A Kinesis shard iterator has a maximum lifetime of 300 seconds (5 minutes); if a consumer does not call `GetRecords` within 300 seconds, the iterator expires. The developer should reduce the batch size (`Limit` parameter) so processing completes in under 5 minutes, or handle the exception by requesting a new iterator from the last processed sequence number.
- B. The Kinesis shard was deleted due to data retention limits.
- C. The worker's IAM role expired after 5 minutes.
- D. Kinesis does not support processing batches larger than 10 records.

### Question 61 — `[D4.3 · ElastiCache Redis Cluster Mode Enabled vs Disabled · Single]`
An analytics platform uses Amazon ElastiCache for Redis (Cluster Mode Disabled) with one primary node and two read replicas. During peak sales events, write throughput to the primary node exceeds its maximum capacity, resulting in write latency and rejected commands. The developer needs to scale write capacity horizontally across multiple nodes.
What architectural change is required?
- A. Migrate to ElastiCache for Redis with **Cluster Mode Enabled**, which partitions data across multiple shards (each shard having its own primary read/write node and up to 5 replicas).
- B. Add three more read replicas to the existing cluster.
- C. Switch from Redis to Memcached.
- D. Enable Multi-AZ failover on the primary node.

### Question 62 — `[D4.1 · Amazon RDS Proxy Connection Pooling · Single]`
An AWS Lambda function is invoked 3,000 times per second and connects to an Amazon Aurora PostgreSQL database. During peak spikes, the database throws errors: `FATAL: remaining connection slots are reserved for non-replication superuser connections`, causing massive transaction failures.
What is the recommended solution to eliminate these connection exhaustion errors?
- A. Deploy an **Amazon RDS Proxy** between the Lambda functions and the Aurora database; configure the Lambda functions to connect to the RDS Proxy endpoint to share and pool database connections.
- B. Increase the database instance class to the largest available instance size.
- C. Reduce the Lambda function concurrency to 10.
- D. Replace Aurora PostgreSQL with Amazon S3.

### Question 63 — `[D4.2 · CloudWatch Log Subscription Payload Decompression · Single]`
A developer configures an Amazon CloudWatch Logs Subscription Filter to stream log records to an AWS Lambda function for real-time security analysis. Inside the Lambda function handler, the developer attempts to inspect `event.awslogs.data`, but receives a base64-encoded binary blob that cannot be parsed as JSON.
How must the developer process this data payload inside the Lambda function?
- A. Base64-decode the `data` string, decompress the resulting binary payload using GZIP, and then parse the decompressed UTF-8 string as JSON.
- B. The CloudWatch subscription filter configuration is corrupted; delete and recreate the filter with JSON encoding.
- C. Call `PutLogEvents` to convert the binary blob back to plaintext.
- D. Cast the data object directly to a JavaScript Map object.

### Question 64 — `[D4.3 · API Gateway Cache Invalidation Permissions · Single]`
An Amazon API Gateway REST API has stage caching enabled. A client application needs to invalidate the cache for a specific resource by sending an HTTP request with the header `Cache-Control: max-age=0`. However, the API Gateway cache does not invalidate, and the client continues to receive stale data. The API Gateway cache is configured with "Require authorization" for cache invalidation.
What must the developer configure to allow the client to invalidate the cache?
- A. Grant the client's IAM identity the `execute-api:InvalidateCache` permission on the API Gateway resource ARN.
- B. Change the HTTP method from GET to POST.
- C. Delete the API Gateway stage and recreate it.
- D. Increase the API Gateway cache size to 237 GB.

### Question 65 — `[D4.3 · CloudFront Cache-Control Headers (s-maxage vs max-age) · Single]`
A developer configures an origin web server behind Amazon CloudFront. The developer wants CloudFront edge locations to cache responses for **1 hour (3600 seconds)**, but wants end-user web browsers to cache responses for only **1 minute (60 seconds)** so that browsers check back with CloudFront frequently.
Which HTTP `Cache-Control` header directive should the origin web server return?
- A. `Cache-Control: max-age=60, s-maxage=3600`
- B. `Cache-Control: max-age=3600, s-maxage=60`
- C. `Cache-Control: no-cache, no-store`
- D. `Cache-Control: public, ttl=3600`
