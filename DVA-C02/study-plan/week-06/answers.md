# ✅ Answers & Explanations — Week 6

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-C · 2-AD · 3-B · 4-C · 5-B · 6-B · 7-B · 8-AC · 9-AB · 10-C · 11-C · 12-B · 13-B · 14-B · 15-B · 16-AB · 17-B · 18-B · 19-B · 20-B · 21-AC · 22-B · 23-B · 24-B · 25-AC · 26-AB

---

### Question 1 — Answer: **C**
- **Why correct:** `Version` should be `"2012-10-17"` (the latest version, which supports policy variables — it is NOT the policy creation date). The order of elements does not matter — `Resource` can appear before `Action`, and `Condition` is optional.
- **Why the others are wrong:** A — `Condition` is optional, not required. B — element order has no effect. D — `Effect` accepts only `Allow` or `Deny`; there is no `Audit`.
- 🧠 **Key point / trap:** `Version = "2012-10-17"`, `Effect` is only Allow/Deny, element order is free, and `Condition` is optional.
- 📎 Source: `resources/iam-policy-json-elements.md` (order doesn't matter; Effect = Allow/Deny; Condition optional).

### Question 2 — Answer: **A, D**
- **Why correct:** The mutually exclusive pairs (cannot be used together in one statement) are `Action`/`NotAction` (A), `Principal`/`NotPrincipal` (D), and `Resource`/`NotResource`.
- **Why the others are wrong:** B — `Effect` and `Condition` are used together normally. C — `Resource` and `Condition` are used together normally. E — `Sid` and `Effect` coexist in one statement.
- 🧠 **Key point / trap:** The three mutually exclusive pairs are **Action/NotAction, Principal/NotPrincipal, Resource/NotResource**.
- 📎 Source: `resources/iam-policy-json-elements.md` (mutually exclusive pairs).

### Question 3 — Answer: **B**
- **Why correct:** Seeing a `Principal` element in the JSON means it is definitely a resource-based policy (or a role's trust policy) — it specifies who is allowed to access the resource.
- **Why the others are wrong:** A — an identity-based policy has no `Principal` (the subject is already the identity the policy is attached to). C/D — a permissions boundary and an SCP are identity-based in structure and do not use `Principal` to name an external subject.
- 🧠 **Key point / trap:** A `Principal` element present = resource-based (or trust policy). This is a classic trap.
- 📎 Source: `resources/iam-policy-json-elements.md`, `resources/iam-identity-vs-resource-policies.md`.

### Question 4 — Answer: **C**
- **Why correct:** Evaluation order: explicit `Deny` > explicit `Allow` > implicit `Deny`. A single explicit `Deny` blocks the request regardless of how many `Allow`s exist for the same action.
- **Why the others are wrong:** A — there is no "more specific Allow beats Deny" concept. B — "more Allows" is meaningless; Deny always wins. D — statement order does not affect the evaluation result.
- 🧠 **Key point / trap:** Same action both Allowed and Denied → result = Deny.
- 📎 Source: `resources/iam-policy-evaluation-logic.md` (Deny > Allow > implicit Deny).

### Question 5 — Answer: **B**
- **Why correct:** No explicit `Allow` for the action → implicit deny (deny by default). This is IAM's "deny by default" principle.
- **Why the others are wrong:** A — the default is deny, not allow. C — with no `Allow`, the request is denied even when there is no `Deny`. D — MFA is unrelated to the absence of an `Allow`.
- 🧠 **Key point / trap:** Nothing granted = implicit Deny (not implicitly allowed).
- 📎 Source: `resources/iam-policy-evaluation-logic.md` (implicit deny default).

### Question 6 — Answer: **B**
- **Why correct:** In the same account, the effective permissions of identity-based + resource-based policies are the UNION — the action is allowed if at least one of the two policies `Allow`s it (and nothing `Deny`s it). The bucket policy `Allow` is enough.
- **Why the others are wrong:** A — the same account does not require both to Allow (that is the cross-account rule). C — MFA is not required in this scenario. D — a bucket policy still applies to a principal in the same account.
- 🧠 **Key point / trap:** Same account = UNION (one side's Allow is enough). Cross-account requires both.
- 📎 Source: `resources/iam-policy-evaluation-logic.md`, `resources/iam-identity-vs-resource-policies.md` (union same-account).

### Question 7 — Answer: **B**
- **Why correct:** Identity-based policy + permissions boundary → effective permissions = INTERSECTION. The boundary allows only `s3:*`, so even though the identity policy grants `ec2:*` too, the final result is only `s3:*`. Adding a boundary can narrow permissions.
- **Why the others are wrong:** A — the boundary intersects, it does not union. C — the boundary does not deny everything; it caps the maximum. D — `s3:*` is the intersection, not `ec2:*`.
- 🧠 **Key point / trap:** A permissions boundary is a maximum-permissions ceiling (INTERSECTION); it does not grant permissions by itself.
- 📎 Source: `resources/iam-policy-evaluation-logic.md` (permissions boundary intersection).

### Question 8 — Answer: **A, C**
- **Why correct:** A — an identity policy + SCP is an INTERSECTION: the action must be `Allow`ed by both the SCP and the identity policy. C — an explicit `Deny` in an SCP overrides any `Allow` (SCP/RCP/identity policy — a Deny anywhere wins).
- **Why the others are wrong:** B — an SCP does not grant permissions; it is only a guardrail that caps the maximum, so an identity policy `Allow` is still needed. D — an SCP is attached to an account / OU in Organizations, not to a role. E — an SCP produces an INTERSECTION, not a union.
- 🧠 **Key point / trap:** An SCP is a guardrail (INTERSECTION) and never grants permissions by itself; an explicit Deny in an SCP always wins.
- 📎 Source: `resources/iam-policy-evaluation-logic.md` (SCP/RCP intersection, explicit deny override).

### Question 9 — Answer: **A, B**
- **Why correct:** A resource-based policy attaches a `Principal` directly to the resource. An S3 bucket policy (A) and an SQS queue access policy (B) are both resource-based (like a Lambda resource policy, an SNS topic policy, a KMS key policy, and so on).
- **Why the others are wrong:** C — a managed policy attached to a group is identity-based. D — a permissions boundary is identity-based (it limits a user's/role's permissions). E — an inline policy attached to a role is identity-based.
- 🧠 **Key point / trap:** Resource-based examples: S3 bucket, SQS, SNS, Lambda resource policy, KMS key, DynamoDB table/stream. They attach to the resource, not the identity.
- 📎 Source: `resources/iam-identity-vs-resource-policies.md` (resource-based examples, inline only).

### Question 10 — Answer: **C**
- **Why correct:** A resource-based policy is inline only (there is no managed version) and always has a `Principal` (specifying who may access it). An identity-based policy (managed or inline) has no `Principal` because the subject is the identity it is attached to.
- **Why the others are wrong:** A — a resource-based policy has no managed form, only inline. B — an identity-based policy has no `Principal`. D — cross-account access typically uses resource-based policies (or a combination with `AssumeRole`), not "identity-based only".
- 🧠 **Key point / trap:** Resource-based = inline only + has a `Principal`; identity-based = managed/inline + no `Principal`.
- 📎 Source: `resources/iam-identity-vs-resource-policies.md`.

### Question 11 — Answer: **C**
- **Why correct:** For cross-account access the UNION rule does not apply — you need both: an identity-based policy in the source account (A) that allows the `s3:GetObject` call, AND a resource-based policy (bucket policy) in the destination account (B) that allows account A's principal. Missing either side fails.
- **Why the others are wrong:** A/B — one side alone is not enough for cross-account access. D — creating an IAM user and issuing a permanent access key is an anti-pattern; use a resource-based policy or cross-account `AssumeRole` instead.
- 🧠 **Key point / trap:** Cross-account = BOTH (identity in A + resource-based in B). This is the key difference from same-account (UNION).
- 📎 Source: `resources/iam-identity-vs-resource-policies.md` (cross-account requires policies in BOTH accounts).

### Question 12 — Answer: **B**
- **Why correct:** The Lambda execution role lets the function obtain temporary credentials to call other services (DynamoDB, S3, SNS, and so on) — with no access key embedded in code or environment variables.
- **Why the others are wrong:** A/D — embedding a long-term access key in environment variables or source code is an anti-pattern: it leaks and is hard to rotate. C — DynamoDB has no "bucket policy"; that is an S3 concept.
- 🧠 **Key point / trap:** A Lambda function that needs to call other services → the execution role (temporary credentials); never hardcode a key.
- 📎 Source: Week 6 README (Lambda execution role); `resources/sts-temporary-credentials.md`.

### Question 13 — Answer: **B**
- **Why correct:** Attach an IAM role to EC2 through an instance profile; the application retrieves temporary credentials from the instance metadata (IMDS) — no long-term key is stored on the host, and the credentials rotate automatically.
- **Why the others are wrong:** A/C — storing or hardcoding an access key on the instance is an anti-pattern. D — an EC2 instance does not receive permissions through a resource-based policy; it uses an instance profile (identity-based through a role).
- 🧠 **Key point / trap:** An app on EC2 that needs AWS permissions → an instance profile (IAM role) + IMDS, not a long-term key.
- 📎 Source: Week 6 README (EC2 instance profile); `resources/sts-temporary-credentials.md` (roles for EC2).

### Question 14 — Answer: **B**
- **Why correct:** Pulling the image from ECR and writing to CloudWatch Logs (and reading secrets at task startup) is done by the ECS agent / infrastructure → this belongs to the task execution role.
- **Why the others are wrong:** A — the task role grants permissions to the application inside the container, not for pulling the image. C — the EC2 instance profile is relevant only for the EC2 launch type, and is not the correct cause here (the question stresses ECR/logs → execution role). D — the service-linked role is not responsible for pulling a task's image.
- 🧠 **Key point / trap:** Cannot pull the ECR image / cannot write logs → the task execution role (NOT the task role).
- 📎 Source: Week 6 README (task role vs. execution role table).

### Question 15 — Answer: **B**
- **Why correct:** Code inside the container calling an AWS service (DynamoDB) gets its permissions from the task role. Image pull / logging being OK means the execution role is fine; the fault is in the task role.
- **Why the others are wrong:** A — the execution role handles infrastructure (ECR/logs), not permissions for the app to call DynamoDB. C — the instance profile is not where a container app gets its permissions. D — DynamoDB has no "bucket policy".
- 🧠 **Key point / trap:** The app in the container cannot call an AWS service → fix the task role (NOT the execution role).
- 📎 Source: Week 6 README (task role vs. execution role table).

### Question 16 — Answer: **A, B**
- **Why correct:** A — the task execution role = permissions for the ECS agent (infrastructure): pull images from ECR, write CloudWatch Logs, read secrets at startup. B — the task role = permissions for the application code inside the container to call AWS services.
- **Why the others are wrong:** C — pulling images is the execution role's job, not the task role's. D — calling DynamoDB (the app) is the task role's job, not the execution role's. E — the two roles have entirely different jobs and are not interchangeable.
- 🧠 **Key point / trap:** execution role = infrastructure (ECR + Logs); task role = the application inside the container. This pair is frequently swapped in exam questions.
- 📎 Source: Week 6 README (ECS task role vs. task execution role table).

### Question 17 — Answer: **B**
- **Why correct:** Cross-account (and same-account role switching) → `AssumeRole`. It returns temporary credentials: an access key ID + secret access key + session token (with an `Expiration`).
- **Why the others are wrong:** A — `GetSessionToken` does not grant cross-account access and does not return permanent keys (its credentials are still temporary). C — `AssumeRoleWithSAML` is for a SAML IdP and does not return a "SAML assertion" (it returns temporary credentials). D — every STS API returns temporary credentials, not long-term keys.
- 🧠 **Key point / trap:** Cross-account role switching → `AssumeRole` → temporary credentials (key + secret + session token).
- 📎 Source: `resources/sts-assumerole-api.md` (AssumeRole returns temp creds, cross-account).

### Question 18 — Answer: **B**
- **Why correct:** Federation through an OIDC provider (Google, Facebook, Cognito, Login with Amazon, and so on) uses `AssumeRoleWithWebIdentity`.
- **Why the others are wrong:** A — `AssumeRoleWithSAML` is for enterprise SAML IdPs, not OIDC social. C — `GetSessionToken` is for the user's own temporary session, not a web identity. D — `AssumeRole` needs an existing AWS principal (it does not use an external OIDC token).
- 🧠 **Key point / trap:** OIDC / social federation (Google/Facebook/Cognito) → `AssumeRoleWithWebIdentity`. (For mobile, AWS recommends wrapping this with Amazon Cognito.)
- 📎 Source: `resources/sts-temporary-credentials.md` (OIDC federation), `resources/cognito-identity-pools.md` (AssumeRoleWithWebIdentity).

### Question 19 — Answer: **B**
- **Why correct:** An enterprise SAML 2.0 IdP (AD FS, Okta SAML, and so on) for single sign-on to AWS → `AssumeRoleWithSAML`.
- **Why the others are wrong:** A — `AssumeRoleWithWebIdentity` is OIDC/social, not SAML. C — `GetSessionToken` is not used for IdP federation. D — `ExternalId` is only about preventing the confused-deputy problem in a cross-account `AssumeRole` with a third party, not SAML SSO.
- 🧠 **Key point / trap:** Enterprise SAML → `AssumeRoleWithSAML`; OIDC/social → `AssumeRoleWithWebIdentity`. Do not swap the two.
- 📎 Source: `resources/sts-temporary-credentials.md` (SAML federation).

### Question 20 — Answer: **B**
- **Why correct:** `GetSessionToken` issues temporary credentials for the user themselves (no role switch), typically with MFA (`SerialNumber` + `TokenCode`) to run sensitive actions protected by `aws:MultiFactorAuthPresent`.
- **Why the others are wrong:** A — `AssumeRole` is used when switching to a different role; here only a temporary session for the user is needed. C — `AssumeRoleWithWebIdentity` is OIDC federation. D — `GetFederationToken` is for a federation broker, and `DurationSeconds` = 0 is meaningless.
- 🧠 **Key point / trap:** A temporary session for yourself + MFA → `GetSessionToken`.
- 📎 Source: `resources/sts-assumerole-api.md` (MFA), Week 6 README (STS API table — GetSessionToken).

### Question 21 — Answer: **A, C**
- **Why correct:** A — a session policy makes the resulting permissions = the INTERSECTION of the role's permissions policy and the session policy; it does not grant permissions beyond the role. C — role chaining limits the session to a maximum of 1 hour; passing `DurationSeconds` greater than 1 hour when chaining will fail.
- **Why the others are wrong:** B — a session policy cannot grant permissions beyond the role (the opposite of A). D — `DurationSeconds` defaults to 3600s (1 hour), not 12 hours (12 hours is the maximum ceiling, depending on the role's max session duration). E — `AssumeRole` always returns temporary credentials with a session token, not permanent keys.
- 🧠 **Key point / trap:** Session policy = INTERSECTION (only narrows); role chaining ≤ 1 hour; default `DurationSeconds` = 3600s.
- 📎 Source: `resources/sts-assumerole-api.md` (session policy intersection, role chaining ≤ 1h, DurationSeconds default 3600s).

### Question 22 — Answer: **B**
- **Why correct:** An Amazon Cognito user pool = authentication → it returns three JWTs: an ID token, an access token, and a refresh token. The ID and access tokens expire in 1 hour by default; the refresh token's validity is configurable (used to obtain new tokens).
- **Why the others are wrong:** A — temporary AWS credentials are a product of the identity pool, not the user pool. C — a user pool returns JWTs, not a SAML assertion, and JWTs do expire. D — it is not a permanent API key.
- 🧠 **Key point / trap:** User pool → three JWTs, ID/access valid 1 hour. "Returns JWTs / sign-in" = user pool.
- 📎 Source: `resources/cognito-user-pools.md` (JWT), Week 6 README (ID/access token 1 hour).

### Question 23 — Answer: **B**
- **Why correct:** A client that needs to call an AWS service directly needs temporary AWS credentials, which is exactly the identity pool's role (it exchanges the token for credentials through STS `AssumeRoleWithWebIdentity` and maps to an IAM role). In practice: sign in with a user pool → pass the JWT to an identity pool.
- **Why the others are wrong:** A — a user pool's JWT is only for authentication / calling your own backend; it cannot sign an AWS request directly. C — groups only handle authorization / IAM role mapping and do not issue credentials by themselves. D — the hosted UI is just a sign-in interface and does not issue AWS credentials.
- 🧠 **Key point / trap:** "Mobile app calling DynamoDB/S3 directly / needs AWS credentials" → an identity pool (NOT a user pool).
- 📎 Source: `resources/cognito-identity-pools.md` (temp AWS creds, calling S3/DynamoDB directly).

### Question 24 — Answer: **B**
- **Why correct:** Managed Login (2024) is the new generation: a no-code branding editor, support for passkeys and dark mode; it requires the Essentials or Plus feature plan (Lite only offers the classic Hosted UI). Plus adds threat protection / adaptive auth.
- **Why the others are wrong:** A — that describes the classic Hosted UI (first-generation); the new Managed Login supports no-code branding. C — it is a sign-in UI and does not issue AWS credentials (that is the identity pool). D — it is not only for M2M.
- 🧠 **Key point / trap:** Hosted UI = classic; Managed Login (2024) = no-code branding + passkeys + dark mode, requires Essentials/Plus.
- 📎 Source: Week 6 README (Hosted UI vs. Managed Login), `resources/cognito-user-pools.md` (managed login).

### Question 25 — Answer: **A, C**
- **Why correct:** A — a user pool supports federation with social OAuth (Google, Facebook, Amazon, Apple) and with any SAML 2.0 / OIDC IdP. C — it supports MFA, groups (which map to an IAM role when the ID token is passed to an identity pool), and Lambda triggers (Pre Sign-up, Post Confirmation, Pre Token Generation, and so on) to customize the auth flow.
- **Why the others are wrong:** B — returning AWS credentials is the identity pool's job, not the user pool's. D — a user pool does support external IdPs (social/SAML/OIDC). E — a user pool is an OIDC IdP to the app, not an STS endpoint exchanging SAML for a role.
- 🧠 **Key point / trap:** User pool = authentication + federation + MFA + groups + Lambda triggers → JWTs. It does not issue AWS credentials.
- 📎 Source: `resources/cognito-user-pools.md` (federation, MFA, groups, Lambda triggers).

### Question 26 — Answer: **A, B**
- **Why correct:** A — the classic combined flow: a user pool authenticates → JWTs → an identity pool exchanges them for temporary AWS credentials → the client calls AWS directly. B — configure an unauthenticated (guest) role in the identity pool so users who are not signed in still get narrow permissions (reading public data in S3).
- **Why the others are wrong:** C — the identity pool issues AWS credentials (through STS); it does not issue JWTs. D — a user pool does not issue AWS credentials by itself; it must go through an identity pool. E — an identity pool handles authorization (exchanging a token for credentials), not authentication of usernames and passwords like a user directory (that is the user pool).
- 🧠 **Key point / trap:** User pool = who you are (JWTs); identity pool = what you can do on AWS (temp credentials, with both an authenticated and an unauthenticated role).
- 📎 Source: `resources/cognito-identity-pools.md` (combined flow, guest/unauthenticated role), Week 6 README (User Pool vs. Identity Pool reflex).
