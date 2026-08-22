# 📝 Practice Questions — Week 6: Security I — IAM, STS, and Amazon Cognito

> **26 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Week 6 material (Domain 2 – Security, part 1/2).
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D2.1 · IAM · Single]`
A developer is reviewing an IAM policy in JSON before deploying it. Which statement about IAM policy elements is TRUE?
- A. `Condition` is a required element in every `Statement`.
- B. Element order matters: `Action` must appear before `Resource`.
- C. `Version` should be set to `"2012-10-17"`, and the order of elements does not matter (`Resource` can appear before `Action`).
- D. `Effect` accepts three values: `Allow`, `Deny`, or `Audit`.

### Question 2 — `[D2.1 · IAM · Multi — Choose 2]`
Within the SAME `Statement`, which pairs of elements are mutually exclusive and cannot be used together? (Choose two.)
- A. `Action` and `NotAction`
- B. `Effect` and `Condition`
- C. `Resource` and `Condition`
- D. `Principal` and `NotPrincipal`
- E. `Sid` and `Effect`

### Question 3 — `[D2.1 · IAM · Single]`
While reading a policy, a developer sees the element `"Principal": {"AWS": "arn:aws:iam::111122223333:root"}`. Which conclusion is MOST accurate?
- A. This is an identity-based policy attached to an IAM role.
- B. This is a resource-based policy — it specifies who (the principal) is allowed to access the resource.
- C. This is a permissions boundary.
- D. This is an AWS Organizations SCP.

### Question 4 — `[D2.1 · IAM · Single]`
An IAM role has an identity-based policy with two statements: statement 1 `Allow`s `s3:*` on the `data-lake` bucket, and statement 2 explicitly `Deny`s `s3:DeleteObject` on that same bucket. When the role calls `s3:DeleteObject` on `data-lake`, what is the result?
- A. Allowed — because `Allow` `s3:*` is more specific and covers `DeleteObject`.
- B. Allowed — because there are more `Allow`s than `Deny`s.
- C. Denied — an explicit `Deny` always overrides `Allow`; a single `Deny` blocks the request.
- D. It depends on statement order in the policy (the later statement wins).

### Question 5 — `[D2.1 · IAM · Single]`
An IAM user has no policy attached that allows `dynamodb:PutItem`, and the DynamoDB table has no relevant resource-based policy. The user calls `PutItem`. What happens?
- A. Allowed by default, until someone explicitly adds a `Deny`.
- B. Denied by implicit deny — there is no explicit `Allow` for this action.
- C. Allowed, because the table has no resource policy blocking it.
- D. The user is prompted to enter MFA before being allowed.

### Question 6 — `[D2.1 · IAM · Single]`
Within a SINGLE AWS account, an IAM role calls `s3:GetObject`. The role's identity-based policy does NOT grant `s3:GetObject`, but the bucket policy `Allow`s `s3:GetObject` for that same principal. There is no `Deny` anywhere. What is the result?
- A. Denied — the role's identity-based policy must also `Allow` the action.
- B. Allowed — in the same account, effective permissions are the UNION of identity-based and resource-based policies; only one side needs to `Allow`.
- C. Allowed, but only if the request includes MFA.
- D. Denied — a bucket policy has no effect on a principal in the same account.

### Question 7 — `[D2.1 · IAM · Single]`
An IAM user has an identity-based policy that allows `ec2:*` and `s3:*`. An administrator then attaches a permissions boundary that allows only `s3:*`. What can this user actually do?
- A. Both `ec2:*` and `s3:*` (the union of the two policies).
- B. Only `s3:*` — effective permissions are the INTERSECTION of the identity-based policy and the permissions boundary.
- C. Nothing — the permissions boundary denies everything.
- D. Only `ec2:*`.

### Question 8 — `[D2.1 · IAM · Multi — Choose 2]`
A team's account is a member of an AWS Organizations organization. Which statements about the interaction between an SCP and an identity-based policy are TRUE? (Choose two.)
- A. When an SCP applies, effective permissions are the INTERSECTION — an action must be `Allow`ed by both the SCP and the identity-based policy to be permitted.
- B. An SCP grants permissions directly to an IAM user by itself (no identity-based policy needed).
- C. An explicit `Deny` in an SCP overrides an `Allow` in an identity-based policy.
- D. An SCP is attached directly to each individual IAM role.
- E. When an SCP is present, the result is always the UNION of the identity policy, the resource policy, and the SCP.

### Question 9 — `[D2.1 · IAM · Multi — Choose 2]`
A developer needs to grant cross-account access so an external principal can reach a resource by using a resource-based policy. Which two of the following support resource-based policies (attaching a `Principal` directly to the resource)? (Choose two.)
- A. An S3 bucket policy
- B. An SQS queue access policy
- C. An IAM managed policy attached to a group
- D. A permissions boundary attached to a user
- E. An IAM inline policy attached to a role

### Question 10 — `[D2.1 · IAM · Single]`
Which statement correctly distinguishes an identity-based policy from a resource-based policy?
- A. A resource-based policy can be managed or inline, just like an identity-based policy.
- B. An identity-based policy must contain a `Principal` element to specify the subject.
- C. A resource-based policy is inline only (no managed version) and always contains a `Principal`; an identity-based policy has no `Principal`.
- D. Only identity-based policies can be used for cross-account access.

### Question 11 — `[D2.1 · IAM · Single]`
An IAM role in account A needs to read an object from an S3 bucket in account B. Which configuration is necessary and sufficient?
- A. Only a bucket policy in account B that allows account A's principal.
- B. Only an identity-based policy in account A that allows `s3:GetObject`.
- C. Both: an identity-based policy in account A allowing the call to `s3:GetObject`, AND a bucket policy (resource-based) in account B allowing account A's principal.
- D. Create a new IAM user inside account B and give its access key to account A.

### Question 12 — `[D2.1 · Lambda · Single]`
A Lambda function needs to write items to a DynamoDB table. What is the MOST secure and standard way to grant this permission?
- A. Embed `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the function's environment variables.
- B. Attach the `dynamodb:PutItem` permission to the Lambda execution role so the function receives temporary credentials automatically.
- C. Set a bucket policy on the DynamoDB table.
- D. Hardcode an access key in the source code and encode it with base64.

### Question 13 — `[D2.1 · IAM · Single]`
An application running on an EC2 instance needs to read and write an S3 bucket and must NOT store long-term credentials on the host. What is the correct solution?
- A. Store the access key in `~/.aws/credentials` on the instance.
- B. Attach an IAM role to the instance through an instance profile; the application retrieves temporary credentials from the instance metadata.
- C. Hardcode the key in the systemd service's environment variables.
- D. Attach a resource-based policy directly to the EC2 instance.

### Question 14 — `[D2.1 · ECS · Single]`
An ECS Fargate task fails to start: the logs show it cannot pull the image from Amazon ECR and cannot write logs to Amazon CloudWatch Logs. Which role needs to be fixed?
- A. The task role — because these are application permissions.
- B. The task execution role — the role the ECS agent uses to pull images from ECR and write to CloudWatch Logs.
- C. The cluster's EC2 instance profile.
- D. The ECS service-linked role.

### Question 15 — `[D2.1 · ECS · Single]`
An ECS container runs normally (image pull OK, logging OK), but code inside the container returns `AccessDenied` when calling `dynamodb:Query`. Which role needs to be fixed?
- A. The task execution role.
- B. The task role — the role that grants the application inside the container permission to call AWS services.
- C. The EC2 instance profile.
- D. The DynamoDB bucket policy.

### Question 16 — `[D2.1 · ECS · Multi — Choose 2]`
Regarding the ECS task role and task execution role, which two statements are TRUE? (Choose two.)
- A. The task execution role is used by the ECS agent (infrastructure) to pull images from ECR and push logs to CloudWatch Logs.
- B. The task role grants the application code inside the container permission to call AWS services (for example, S3 or DynamoDB).
- C. The task role is the role used to pull images from ECR.
- D. The task execution role grants the application inside the container access to DynamoDB.
- E. The two roles are identical and can be used interchangeably.

### Question 17 — `[D2.1 · STS · Single]`
A service in account A needs to access resources in account B using a cross-account model. Which STS API should it call, and what does that API return?
- A. `GetSessionToken` — returns permanent access keys for account B.
- B. `AssumeRole` — returns temporary credentials consisting of an access key ID, a secret access key, and a session token.
- C. `AssumeRoleWithSAML` — returns a SAML assertion.
- D. `GetFederationToken` — returns long-term credentials for a federated user.

### Question 18 — `[D2.1 · STS · Single]`
Users of a web app sign in with Google (an OIDC identity provider) and need to exchange that for an IAM role to access AWS. Which STS API is the foundation of this flow?
- A. `AssumeRoleWithSAML`.
- B. `AssumeRoleWithWebIdentity` — for OIDC federation (Google, Facebook, Cognito, and so on).
- C. `GetSessionToken`.
- D. `AssumeRole`.

### Question 19 — `[D2.1 · STS · Single]`
An enterprise uses AD FS / Okta (SAML 2.0) to let employees sign in to AWS with single sign-on, without creating a separate IAM user for each person. Which STS API is appropriate?
- A. `AssumeRoleWithWebIdentity`.
- B. `AssumeRoleWithSAML` — for enterprise SAML identity providers.
- C. `GetSessionToken`.
- D. `AssumeRole` with `ExternalId`.

### Question 20 — `[D2.1 · STS · Single]`
An IAM user needs temporary credentials for their own session to run some sensitive actions that are protected by the `aws:MultiFactorAuthPresent` condition. Which API is the BEST fit?
- A. `AssumeRole` (used only when switching to a different role).
- B. `GetSessionToken` — issues a temporary session for the user themselves, typically with MFA (`SerialNumber` + `TokenCode`).
- C. `AssumeRoleWithWebIdentity`.
- D. `GetFederationToken` with `DurationSeconds` = 0.

### Question 21 — `[D2.1 · STS · Multi — Choose 2]`
Regarding the behavior of `sts:AssumeRole`, which two statements are TRUE? (Choose two.)
- A. When a session policy is passed, effective permissions = the INTERSECTION of the role's identity-based policy and the session policy (a session policy cannot grant permissions beyond the role).
- B. A session policy can grant additional permissions beyond the role's permissions policy.
- C. Role chaining (using temporary credentials to assume another role) limits the session to a maximum of 1 hour; passing `DurationSeconds` greater than 1 hour when chaining will fail.
- D. `DurationSeconds` defaults to 12 hours.
- E. `AssumeRole` returns permanent access keys (with no session token).

### Question 22 — `[D2.1 · Cognito · Single]`
After a user successfully signs in through an Amazon Cognito user pool, what does the app receive, and what is the default validity?
- A. A set of temporary AWS credentials valid for 12 hours.
- B. Three JWTs — an ID token, an access token, and a refresh token; the ID and access tokens expire in 1 hour by default, and the refresh token is configurable.
- C. A single SAML assertion that never expires.
- D. A permanent API key for calling API Gateway.

### Question 23 — `[D2.1 · Cognito · Single]`
A mobile app authenticates users and needs to call Amazon DynamoDB directly from the device to read a user's data. Which Cognito component provides what is needed for this?
- A. A user pool — its JWT can call DynamoDB directly.
- B. An identity pool — it exchanges the token for temporary AWS credentials through STS so the client can call AWS services directly.
- C. User pool groups.
- D. The user pool hosted UI.

### Question 24 — `[D2.1 · Cognito · Single]`
A team wants to use Managed Login (launched in 2024) instead of the classic Hosted UI. Which statement about Managed Login is TRUE?
- A. It is a first-generation interface with no branding customization.
- B. It provides a no-code branding editor, supports passkeys and dark mode, and requires the Essentials or Plus feature plan (Lite only offers the classic Hosted UI).
- C. It issues temporary AWS credentials directly to the client, replacing the identity pool.
- D. It can be used only for machine-to-machine (client credentials) flows.

### Question 25 — `[D2.1 · Cognito · Multi — Choose 2]`
Regarding the capabilities of an Amazon Cognito user pool, which two statements are TRUE? (Choose two.)
- A. It supports federation with social OAuth providers (Google, Facebook, Amazon, Apple) and with any SAML 2.0 / OIDC identity provider.
- B. A user pool returns temporary AWS credentials for calling S3 or DynamoDB directly.
- C. It supports MFA, groups (which map to an IAM role when the ID token is passed to an identity pool), and Lambda triggers to customize the auth flow.
- D. A user pool does not support external identity providers; it only has an internal user directory.
- E. A user pool is essentially an STS endpoint that exchanges a SAML assertion for an IAM role.

### Question 26 — `[D2.1 · Cognito · Multi — Choose 2]`
A mobile app: signed-in users get full functionality, while unauthenticated guests still need to read some public data in S3. Which two statements correctly describe this architecture? (Choose two.)
- A. Sign in through a user pool (receive JWTs) → pass the JWT to an identity pool → receive temporary AWS credentials → call AWS directly.
- B. Configure an unauthenticated (guest) role in the identity pool with narrow permissions for users who are not signed in.
- C. Guests receive a JWT directly from the identity pool to authenticate.
- D. The user pool issues temporary AWS credentials directly to the device, with no identity pool needed.
- E. The identity pool authenticates users' usernames and passwords like a user directory.
