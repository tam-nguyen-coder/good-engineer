# 📝 Practice Questions — Week 7: Security II — KMS, Secrets Manager, Parameter Store, Encryption

> **24 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Week 7 material (completes Domain 2).
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D2.2 · KMS/encryption · Single]`
A developer needs to encrypt a 1 MB log file **client-side** with a customer managed AWS KMS key (CMK) before uploading it to Amazon S3. When the developer calls `kms:Encrypt` directly on the file, the request fails. What should the developer do to encrypt the file?
- A. Split the file into 4 KB chunks, call `kms:Encrypt` on each chunk, and concatenate the ciphertext.
- B. Call `GenerateDataKey` to obtain a **plaintext** data key and an **encrypted** data key; use the plaintext key to encrypt the file locally, store the encrypted data key alongside the file, and erase the plaintext key from memory.
- C. Import the 1 MB file as key material for the CMK and then call `Encrypt`.
- D. Call `kms:Encrypt` directly on the 1 MB payload — KMS will automatically switch to envelope encryption.

### Question 2 — `[D2.2 · KMS/encryption · Single]`
A developer calls `kms:Encrypt` on a 10 MB object and receives an error. What is the **exact** cause?
- A. The CMK must be **asymmetric** to encrypt data larger than 4 KB.
- B. The execution role is missing the `kms:GenerateDataKey` permission.
- C. The `kms:Encrypt` and `kms:Decrypt` APIs accept a maximum of **4 KB** of data; a larger payload **must** use envelope encryption.
- D. The data must be `gzip`-compressed before calling `Encrypt`.

### Question 3 — `[D2.2 · KMS/encryption · Single]`
An external partner **outside AWS** (with no access to the KMS API) needs to encrypt data that only your application can decrypt. In addition, your system needs to **sign and verify** messages. Which type of KMS key is appropriate?
- A. A symmetric CMK, sharing the plaintext key with the partner.
- B. An AWS owned key.
- C. An HMAC key to perform the encryption.
- D. An asymmetric KMS key (`RSA`/`ECC`) — distribute the **public key** so the partner can encrypt client-side, and use it to verify signatures.

### Question 4 — `[D2.2 · KMS/encryption · Multi — Choose 2]`
Which two statements are **TRUE** about `GenerateDataKey` and envelope encryption? (Choose two.)
- A. `GenerateDataKey` returns **both** a data key in **plaintext** **and** a copy of the data key **encrypted** under the CMK.
- B. KMS stores the plaintext data key so that you can retrieve it later.
- C. After encrypting the data locally, you should **erase the plaintext data key** from memory and store only the **encrypted data key** next to the data.
- D. The encrypted data key can only be decrypted by calling `GenerateDataKey` again.
- E. A data key is limited to a maximum of 4 KB, so it cannot be used to encrypt large files.

### Question 5 — `[D2.2 · KMS/encryption · Single]`
A service running under a temporary role needs permission to **use a CMK for a short period**, and that permission must be **revocable** at any time, **WITHOUT** modifying the existing key policy or IAM policies. Which mechanism is the best fit?
- A. A KMS **grant**.
- B. Add the principal directly to the **key policy** of the key.
- C. Attach an IAM policy of `kms:*` to the principal.
- D. Add a `kms:ViaService` condition to the key policy.

### Question 6 — `[D2.2 · KMS/encryption · Single]`
A developer attached an IAM policy to a role that allows `kms:Decrypt`, but the call still returns `AccessDenied` on a customer managed key. What is the most likely cause?
- A. An IAM policy can never grant permissions for KMS.
- B. The role needs `kms:GenerateDataKey` instead of `kms:Decrypt`.
- C. The **key policy** (the resource-based policy **required** on every key) does not allow the account/principal, so the IAM policy has no effect.
- D. The key must be asymmetric to be able to decrypt.

### Question 7 — `[D2.2 · KMS/encryption · Single]`
Which statement is **TRUE** about automatic rotation of a customer managed **symmetric** CMK?
- A. Rotation **re-encrypts** all existing data with the new key material.
- B. It rotates every **365 days** by default; you can set a **custom rotation period** and perform **on-demand rotation**; KMS **retains the old key material** so old ciphertext can still be decrypted with **no code changes**.
- C. After each rotation you must change the alias and update the application code to point to the new key material.
- D. Customer managed keys do **not** support automatic rotation; only AWS managed keys can rotate.

### Question 8 — `[D2.2 · KMS/encryption · Single]`
A compliance team requires the ability to **author the key policy** themselves, **enable/disable rotation** at will, and **audit every use of the key** in AWS CloudTrail. Which type of KMS key meets these requirements?
- A. An AWS owned key.
- B. An AWS managed key (`aws/<service>`).
- C. A **customer managed key (CMK)**.
- D. An AWS owned key with a custom grant.

### Question 9 — `[D2.2 · KMS/encryption · Single]`
An Amazon DynamoDB global table replicates data between `us-east-1` and `eu-west-1`. Data encrypted in one Region must be **decryptable** in the other Region (for disaster recovery). Which KMS feature is appropriate?
- A. Enable automatic rotation for the key.
- B. A **multi-Region key** — a replica of the key with the **same key material** in multiple Regions.
- C. Use an AWS owned key.
- D. Manually copy the key material to each Region using `GenerateDataKey`.

### Question 10 — `[D2.2 · KMS/encryption · Single]`
A team wants a CMK that **can be used only when the request goes through Amazon S3** in a specific Region, and **blocks** all direct API calls to the key. Which configuration meets the requirement?
- A. A grant with an encryption context.
- B. An `aws:SourceIp` condition in the key policy.
- C. Disable the key and enable it only for S3.
- D. A **`kms:ViaService`** condition set to `s3.<region>.amazonaws.com` in the key policy.

### Question 11 — `[D2.2 · KMS/encryption · Multi — Choose 2]`
Which two statements are **TRUE** about Amazon S3 server-side encryption? (Choose two.)
- A. `SSE-KMS` uses a KMS key and **logs every key use to AWS CloudTrail**, which supports auditing.
- B. `SSE-S3` requires you to **provide** a customer managed KMS key.
- C. `SSE-KMS` cannot be used together with bucket default encryption.
- D. `SSE-C` means the **client provides and manages** the encryption key; S3/KMS does not store that key.
- E. New S3 objects are **not** encrypted by default and must be encrypted manually.

### Question 12 — `[D2.2 · KMS/encryption · Single]`
A developer configures a custom TLS certificate for an Amazon CloudFront distribution, but the certificate (issued in `eu-west-1`) **does not appear** for selection. What is the cause and the fix?
- A. CloudFront does not support ACM; the certificate must be imported into IAM.
- B. A certificate used with CloudFront **must be in the `us-east-1`** (N. Virginia) Region → request/import the certificate again in `us-east-1`.
- C. The certificate must be a wildcard to be attached to CloudFront.
- D. Copy the certificate from `eu-west-1` to `us-east-1`.

### Question 13 — `[D2.2 · KMS/encryption · Single]`
A TLS certificate on an Application Load Balancer keeps expiring and the ops team has to renew it manually. Which solution requires the **LEAST operational overhead**?
- A. Buy a 3-year certificate from a third-party provider.
- B. Store the certificate in AWS Secrets Manager and rotate it with a Lambda function.
- C. Use **AWS Certificate Manager (ACM)** to issue the certificate — ACM **automatically renews** certificates for integrated services (ALB/CloudFront/API Gateway), at no cost.
- D. Store the private key in a Parameter Store `SecureString`.

### Question 14 — `[D2.2 · KMS/encryption · Multi — Choose 2]`
Which two statements are **TRUE** about encryption at rest with KMS? (Choose two.)
- A. In-transit encryption is configured using a KMS data key.
- B. Amazon EBS volume encryption also encrypts **snapshots** created from that volume using KMS.
- C. Amazon DynamoDB and Amazon RDS support encryption at rest with KMS, enabled at table/instance **creation** time.
- D. `SSE-C` uses a customer managed key that AWS manages inside KMS.
- E. An S3 bucket is never encrypted unless you enable it manually.

### Question 15 — `[D2.3 · Secrets/ParameterStore · Single]`
An application running on Amazon ECS connects to an Amazon RDS database. A security requirement states that the database credentials must be **automatically rotated every 30 days** **without redeploying** the application. Which service is appropriate?
- A. **AWS Secrets Manager** with automatic rotation (Lambda), which integrates natively with RDS.
- B. A Parameter Store `SecureString` with a custom CloudWatch Events schedule to change the value.
- C. Store the credentials in an encrypted environment variable and redeploy the application monthly.
- D. An IAM access key rotated manually on a schedule.

### Question 16 — `[D2.3 · Secrets/ParameterStore · Single]`
During Secrets Manager rotation, what do the **staging labels** mean?
- A. `AWSNEW` / `AWSLIVE` / `AWSOLD`.
- B. `AWSCURRENT` = the **new** version; `AWSPENDING` = the **old** version.
- C. `AWSLATEST` = current; `AWSSTAGED` = the previous version.
- D. `AWSPENDING` = the **new** version being rotated; `AWSCURRENT` = the version the application is **currently using**; `AWSPREVIOUS` = the **old** version for rollback.

### Question 17 — `[D2.3 · Secrets/ParameterStore · Single]`
A developer stores a database password as a Parameter Store `SecureString`, then runs `aws ssm get-parameter --name /app/db-pass` but receives only **ciphertext** instead of plaintext. What is the correct fix?
- A. Change the parameter type to `String`.
- B. Add the **`--with-decryption`** flag so Parameter Store decrypts the value through KMS; also grant the `kms:Decrypt` permission.
- C. Use `get-parameters-by-path` instead of `get-parameter`.
- D. A `SecureString` cannot be decrypted through the CLI; you must use the console.

### Question 18 — `[D2.3 · Secrets/ParameterStore · Multi — Choose 2]`
Which two features are **ONLY** available in the **advanced tier** of Parameter Store (not in the standard tier)? (Choose two.)
- A. Values larger than 4 KB (up to **8 KB**).
- B. Encrypting values with KMS (`SecureString`).
- C. **Sharing parameters cross-account**.
- D. Organizing parameters hierarchically by path.
- E. Retrieving up to 10 parameters at once with `GetParameters`.

### Question 19 — `[D2.3 · Secrets/ParameterStore · Single]`
A team needs to store roughly **50 non-sensitive configuration values** (endpoint URLs, resource IDs, static connection strings) at the **lowest cost**, with **no rotation** required. Which option is best?
- A. AWS Secrets Manager (charges per secret + per 10,000 API calls).
- B. Parameter Store advanced tier.
- C. **Parameter Store standard tier** (free).
- D. A dedicated DynamoDB table to store the configuration.

### Question 20 — `[D2.3 · Secrets/ParameterStore · Multi — Choose 2]`
An AWS Lambda function needs to read a database secret from Secrets Manager **at runtime**, **without hard-coding** the credentials. Which two items are **REQUIRED**? (Choose two.)
- A. Grant the Lambda **execution role** the `secretsmanager:GetSecretValue` permission.
- B. Grant `kms:Decrypt` on the KMS key that encrypts the secret (if the secret uses a customer managed key).
- C. Store the password in a **plaintext** Lambda environment variable as a backup.
- D. Embed AWS access key / secret key credentials in the function code.
- E. Make the secret **public** with an open resource policy.

### Question 21 — `[D2.3 · Secrets/ParameterStore · Single]`
An AWS Lambda function is **logging the database password verbatim** to Amazon CloudWatch Logs and stores an API key in a **plaintext environment variable**. What is the **correct** way to handle this?
- A. `base64`-encode the password before logging it.
- B. Move the log group to a different Region.
- C. Set the log retention to 1 day.
- D. **Sanitize the logs** (do not write secret values to CloudWatch Logs) and **encrypt the environment variable holding the secret with KMS** (or read the secret at runtime instead of storing it in an environment variable).

### Question 22 — `[D2.3 · Secrets/ParameterStore · Single]`
Which statement is **TRUE** about how Secrets Manager Lambda-based rotation works?
- A. The rotation function updates the credentials in **both** the secret **and** the database/service (the `createSecret` → `setSecret` → `testSecret` → `finishSecret` steps); the `finishSecret` step changes the `AWSPENDING` label to `AWSCURRENT`.
- B. Rotation only changes the secret value; it does **not** change the password in the database.
- C. Rotation requires **redeploying** the application before it can pick up the new value.
- D. Parameter Store performs automatic rotation in exactly the same way.

### Question 23 — `[D2.3 · Secrets/ParameterStore · Single]`
Multiple AWS accounts need to securely retrieve a **shared, rotatable database secret**. Which solution is best?
- A. Email the credentials to each account owner.
- B. **AWS Secrets Manager** with a **resource-based secret policy** for cross-account access, combined with a KMS key policy that grants the other account permission.
- C. A Parameter Store standard `SecureString` shared cross-account.
- D. A public S3 object containing the credentials.

### Question 24 — `[D2.3 · Secrets/ParameterStore · Multi — Choose 2]`
Which two statements are **TRUE** about Parameter Store? (Choose two.)
- A. `String` and `StringList` store values as **plaintext**; only `SecureString` is encrypted with KMS.
- B. Parameter Store has **no** built-in automatic rotation; if you need rotation, use Secrets Manager.
- C. Parameter Store encrypts **every** parameter type by default.
- D. Parameter Store automatically rotates `SecureString` values every 365 days.
- E. The standard tier supports parameter policies.
