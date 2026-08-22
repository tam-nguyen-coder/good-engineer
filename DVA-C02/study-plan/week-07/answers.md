# ✅ Answers & Explanations — Week 7

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-D · 4-AC · 5-A · 6-C · 7-B · 8-C · 9-B · 10-D · 11-AD · 12-B · 13-C · 14-BC · 15-A · 16-D · 17-B · 18-AC · 19-C · 20-AB · 21-D · 22-A · 23-B · 24-AB

---

### Question 1 — Answer: **B**
- **Why correct:** A 1 MB file exceeds the 4 KB limit of `kms:Encrypt`, so you must use **envelope encryption**: `GenerateDataKey` returns a plaintext data key plus an encrypted data key; encrypt the file locally with the plaintext key, store the encrypted data key alongside it, and then **erase the plaintext key**.
- **Why the others are wrong:** A — chunking into 4 KB blocks and concatenating is an anti-pattern and is not the standard approach. C — you cannot import user data as key material. D — KMS does **not** automatically switch to envelope encryption; a direct call over 4 KB simply fails.
- 🧠 **Key point / trap:** data > 4 KB → **envelope encryption** (`GenerateDataKey`), never a direct `Encrypt` call.
- 📎 Source: Week 7 `README.md` (envelope encryption), `resources/kms-concepts.md` (data key / envelope encryption).

### Question 2 — Answer: **C**
- **Why correct:** The KMS `Encrypt`/`Decrypt` (and `ReEncrypt`) APIs accept a maximum of **4 KB** of data. 10 MB exceeds that limit and fails; the solution is envelope encryption.
- **Why the others are wrong:** A — an asymmetric key has an even smaller plaintext limit and is not the way to encrypt large data. B — a missing permission returns `AccessDenied`, not a size error. D — compression is not an API requirement.
- 🧠 **Key point / trap:** the **4 KB** number is the classic trap. Whenever you see "encrypt a large file / 1 MB / 10 MB" → envelope.
- 📎 Source: Week 7 `README.md` (4 KB limit), `resources/kms-concepts.md`.

### Question 3 — Answer: **D**
- **Why correct:** An asymmetric KMS key (`RSA`/`ECC`) lets you distribute a **public key** so parties outside AWS can encrypt client-side (no KMS API call needed), and it is used for **sign/verify**. This exactly matches the "client outside AWS + sign/verify" use case.
- **Why the others are wrong:** A — a symmetric key **never leaves** KMS in plaintext, so it cannot be shared externally. B — an AWS owned key cannot be used directly or controlled. C — an HMAC key is used for MAC (integrity verification), **not** encryption.
- 🧠 **Key point / trap:** "sign/verify" or "encrypt client-side outside AWS" → **asymmetric key**. Everything else is almost always symmetric.
- 📎 Source: Week 7 `README.md` (symmetric vs asymmetric).

### Question 4 — Answer: **A, C**
- **Why correct:** A — `GenerateDataKey` returns a **pair**: a plaintext data key (encrypt locally) and a data key encrypted under the CMK (store alongside). C — the required envelope step is to **erase the plaintext key** after use and keep only the encrypted copy.
- **Why the others are wrong:** B — KMS does **not** store the plaintext data key (it only transmits it over TLS). D — the encrypted data key is decrypted by calling `Decrypt` on the CMK, not by re-running `GenerateDataKey`. E — because the data key encrypts the data **locally** (not through KMS), it is not subject to the 4 KB limit, so it can encrypt large files freely.
- 🧠 **Key point / trap:** `GenerateDataKey` = **plaintext + ciphertext data key**; once done, **erase the plaintext**.
- 📎 Source: `resources/kms-concepts.md` (customer data key, envelope), Week 7 `README.md` (envelope flow).

### Question 5 — Answer: **A**
- **Why correct:** A **grant** is the mechanism for **temporary, flexible, revocable** authorization that lets a principal/service use a key for a short time — **without** modifying the key policy or IAM.
- **Why the others are wrong:** B — adding to the key policy is a lasting change, exactly what the question wants to avoid. C — an IAM policy of `kms:*` is far too broad and is also a permanent change. D — `kms:ViaService` is a scoping condition, not a temporary authorization mechanism.
- 🧠 **Key point / trap:** "temporary + revocable + no policy edits" → **grant**.
- 📎 Source: Week 7 `README.md` (grant vs key policy vs IAM).

### Question 6 — Answer: **C**
- **Why correct:** The **key policy** is the resource-based policy **required** on every KMS key and is the final gatekeeper. If the key policy does not allow the account/principal, then even a permissive IAM policy has no effect → `AccessDenied`.
- **Why the others are wrong:** A — IAM **can** grant KMS permissions, but it must be **combined** with the key policy. B — `kms:Decrypt` is the correct action for decrypting; `GenerateDataKey` is a different action. D — asymmetric is unrelated to this authorization error.
- 🧠 **Key point / trap:** IAM + key policy must **both allow**; the key policy is the prerequisite.
- 📎 Source: Week 7 `README.md` (key policy required, combined with IAM).

### Question 7 — Answer: **B**
- **Why correct:** Automatic rotation for a CMK: **365 days** by default, with a configurable **custom rotation period** (`RotationPeriodInDays`) and **on-demand rotation**. KMS **retains the old key material** (old backing key) so old ciphertext can still be decrypted; the alias/Key ID does not change → **no code changes needed**.
- **Why the others are wrong:** A — rotation does **NOT** re-encrypt existing data. C — no alias/code change; it is fully transparent. D — customer managed keys **do** support automatic rotation (optional on/off), while AWS managed keys rotate **mandatorily** each year.
- 🧠 **Key point / trap:** **365 days + custom period + on-demand**; the old backing key is retained to decrypt old data.
- 📎 Source: `resources/kms-key-rotation.md` (default 365, custom period, on-demand, retain old material).

### Question 8 — Answer: **C**
- **Why correct:** Only a **customer managed key (CMK)** provides full control: author the key policy yourself, enable/disable rotation, and audit in CloudTrail.
- **Why the others are wrong:** A — an AWS owned key cannot be viewed, audited, or edited. B — an AWS managed key lets you view metadata and audit in CloudTrail, but you **cannot** edit its policy/rotation. D — an AWS owned key cannot take a grant like this and still cannot be controlled.
- 🧠 **Key point / trap:** need **control + audit + your own policy/rotation** → **CMK**. AWS managed = view+audit but not editable; AWS owned = fully hidden, free.
- 📎 Source: `resources/kms-concepts.md` (three-key-type table), Week 7 `README.md`.

### Question 9 — Answer: **B**
- **Why correct:** A **multi-Region key** is a replica of the key with the **same key material** across multiple Regions → ciphertext created in Region A can be decrypted in Region B; ideal for DR / global tables.
- **Why the others are wrong:** A — rotation is unrelated to cross-Region decryption. C — an AWS owned key is not a multi-Region solution you control. D — you cannot (and should not) manually copy plaintext key material; the key never leaves KMS in plaintext.
- 🧠 **Key point / trap:** "same key decrypts across Regions / DR / global table" → **multi-Region key** (Key ID has the `mrk-` prefix).
- 📎 Source: Week 7 `README.md` (multi-Region key), `resources/kms-key-rotation.md` (multi-Region).

### Question 10 — Answer: **D**
- **Why correct:** The **`kms:ViaService`** condition restricts the key so it **can only be used through a specific service** (e.g. `s3.<region>.amazonaws.com`), blocking direct API calls.
- **Why the others are wrong:** A — a grant authorizes a principal; it does not restrict "through which service." B — `aws:SourceIp` restricts by IP, not by service. C — disable/enable is an on/off toggle for the whole key, not a per-service filter.
- 🧠 **Key point / trap:** "use the key only through exactly one service" → **`kms:ViaService`**.
- 📎 Source: Week 7 `README.md` (`kms:ViaService`).

### Question 11 — Answer: **A, D**
- **Why correct:** A — `SSE-KMS` uses a KMS key, and every key use is logged to CloudTrail → detailed auditing. D — `SSE-C` (customer-provided) means the **client provides the key** in each request; AWS does **not** store the key.
- **Why the others are wrong:** B — `SSE-S3` uses keys **managed by AWS** (AES-256); you do not provide a key. C — `SSE-KMS` can be used with bucket default encryption. E — since 2023, S3 encrypts every new object **by default** with `SSE-S3`, so new objects are already encrypted.
- 🧠 **Key point / trap:** `SSE-KMS` = auditing via CloudTrail; `SSE-C` = client provides the key; `SSE-S3` = AWS-managed keys, **enabled by default**.
- 📎 Source: Week 7 `README.md` (`S3 SSE-KMS`/`SSE-S3`/`SSE-C`), spec (SSE-S3 default since 2023).

### Question 12 — Answer: **B**
- **Why correct:** A certificate used with CloudFront **must** be requested/imported in **`us-east-1`** (N. Virginia); a certificate in another Region will not appear for selection.
- **Why the others are wrong:** A — CloudFront **supports** ACM (recommended); no IAM import needed. C — a wildcard is not required. D — you **cannot** copy a certificate between Regions; you must request/import it again.
- 🧠 **Key point / trap:** CloudFront + certificate → always **`us-east-1`**. An ACM certificate is **regional** and cannot be copied cross-Region.
- 📎 Source: `resources/acm-overview.md` (CloudFront requires us-east-1; certificates are regional).

### Question 13 — Answer: **C**
- **Why correct:** ACM issues and **automatically renews** TLS certificates for integrated services (ALB/CloudFront/API Gateway) at no cost → no more expiring certificates, the least operational overhead.
- **Why the others are wrong:** A — a third-party certificate must still be renewed/re-imported manually. B, D — Secrets Manager/Parameter Store are for storing secrets/config, not for issuing and auto-renewing TLS certificates for an ALB.
- 🧠 **Key point / trap:** "auto-renewing TLS certificate for ALB/CloudFront/API GW" → **ACM**. Note that certificates **imported** into ACM are **not** auto-renewed.
- 📎 Source: `resources/acm-overview.md` (auto-renew for integrated services, free).

### Question 14 — Answer: **B, C**
- **Why correct:** B — enabling encryption on an EBS volume means snapshots (and volumes restored from them) are also encrypted with KMS. C — DynamoDB and RDS encrypt at rest with KMS, configured at table/instance **creation** time.
- **Why the others are wrong:** A — in transit uses **TLS**, not a KMS data key. D — `SSE-C` uses a **client-provided** key, not one AWS manages inside KMS. E — S3 encrypts new objects by default with `SSE-S3` (since 2023).
- 🧠 **Key point / trap:** at rest = KMS (`S3`/`EBS`/`DynamoDB`/`RDS`); in transit = **TLS**. Don't conflate the two layers.
- 📎 Source: Week 7 `README.md` (encryption at rest & in transit).

### Question 15 — Answer: **A**
- **Why correct:** Secrets Manager has **built-in automatic rotation via Lambda** and integrates natively with RDS; it changes the credentials in **both** the secret **and** the database, and the app reads the secret at runtime, so **no redeploy is needed**.
- **Why the others are wrong:** B — Parameter Store has **no** built-in rotation; a custom schedule cannot change the password on the DB side. C — a monthly redeploy is manual and violates the "automatic" intent. D — an IAM access key is not used to authenticate to an RDS DB user this way, and it is still manual.
- 🧠 **Key point / trap:** "automatically **rotate DB credentials**" → **Secrets Manager** (Lambda rotation + RDS integration).
- 📎 Source: `resources/secrets-manager-intro.md`, `resources/secrets-manager-rotation.md`.

### Question 16 — Answer: **D**
- **Why correct:** The correct trio of staging labels: `AWSPENDING` (new version being rotated, pending activation), `AWSCURRENT` (the version the app is using), `AWSPREVIOUS` (the old version for rollback).
- **Why the others are wrong:** A, C — those label names do not exist. B — reverses the meaning (`AWSCURRENT` is current, not "new"; `AWSPENDING` is new, not "old").
- 🧠 **Key point / trap:** **PENDING = new, being rotated**, **CURRENT = in use**, **PREVIOUS = old/rollback**.
- 📎 Source: `resources/secrets-manager-rotation.md` (staging labels).

### Question 17 — Answer: **B**
- **Why correct:** For a `SecureString`, you must add **`--with-decryption`** for Parameter Store to decrypt (through KMS) and return plaintext; without the flag you get only the encrypted value. The caller also needs the `kms:Decrypt` permission.
- **Why the others are wrong:** A — changing to `String` stores plaintext and breaks security. C — `get-parameters-by-path` also needs `--with-decryption`, so it is not the cause. D — the CLI can decrypt; you just need the right flag.
- 🧠 **Key point / trap:** `SecureString` + read plaintext → **`--with-decryption`** (+ `kms:Decrypt`).
- 📎 Source: `resources/ssm-parameter-store.md` (must include `--with-decryption`).

### Question 18 — Answer: **A, C**
- **Why correct:** A — values > 4 KB (up to **8 KB**) are advanced-tier only. C — **cross-account sharing** is advanced-tier only (along with parameter policies).
- **Why the others are wrong:** B — `SecureString`/KMS is available in **both** tiers. D — hierarchical path organization exists in both tiers. E — `GetParameters` retrieving up to 10 parameters is a common feature, not tier-dependent.
- 🧠 **Key point / trap:** advanced tier = **8 KB + cross-account sharing + parameter policies + charges**. Standard = 4 KB, free.
- 📎 Source: `resources/ssm-parameter-store-tiers.md` (Standard vs Advanced table).

### Question 19 — Answer: **C**
- **Why correct:** Non-sensitive config, no rotation needed, cheapest option → **Parameter Store standard tier** (free), more than enough for 50 parameters.
- **Why the others are wrong:** A — Secrets Manager **charges** per secret + per API call → expensive for simple config. B — the advanced tier charges and is not needed here. D — standing up DynamoDB to store config is unnecessary operational overhead and not optimal.
- 🧠 **Key point / trap:** "simple config, **cheapest**, no rotation" → **Parameter Store standard** (free). Don't pick Secrets Manager (it charges).
- 📎 Source: `resources/ssm-parameter-store.md`, `resources/secrets-manager-intro.md` (pricing).

### Question 20 — Answer: **A, B**
- **Why correct:** A — the execution role must have `secretsmanager:GetSecretValue` to read the secret at runtime. B — if the secret is encrypted with a customer managed key, the role also needs `kms:Decrypt` on that key to decrypt it.
- **Why the others are wrong:** C — storing the password in a plaintext environment variable defeats the "no hard-coding / no exposure" goal. D — embedding access keys in code is absolutely forbidden; use an **IAM role**. E — making the secret public is a serious vulnerability.
- 🧠 **Key point / trap:** read a secret from Lambda = **role with `GetSecretValue` + `kms:Decrypt`**, never hard-code credentials.
- 📎 Source: Week 7 `README.md` (Lab 4 — read a secret from Lambda), `resources/secrets-manager-intro.md`.

### Question 21 — Answer: **D**
- **Why correct:** Both problems (logs exposing the secret + plaintext environment variable) are addressed by: **sanitizing the logs** (do not write the secret to CloudWatch Logs) and **encrypting the environment variable with KMS** (or, better, reading the secret at runtime instead of storing it in the env var).
- **Why the others are wrong:** A — `base64` is just encoding, **not** encryption; it is still exposed. B — changing Regions does not hide the secret. C — reducing retention does not prevent the secret from being read during that period.
- 🧠 **Key point / trap:** **never log secrets** + **an env var holding a secret must be KMS-encrypted** (or fetched at runtime). `base64` ≠ encryption.
- 📎 Source: Week 7 `README.md` (managing sensitive data, log sanitization, KMS-encrypted env vars).

### Question 22 — Answer: **A**
- **Why correct:** Lambda-based rotation updates the credentials in **both** the secret **and** the database/service, following the four steps `createSecret` → `setSecret` → `testSecret` → `finishSecret`; the final step changes `AWSPENDING` → `AWSCURRENT`.
- **Why the others are wrong:** B — rotation changes the password on the DB side **as well** (that is the difference from Parameter Store). C — the app reads the secret at runtime, so **no** redeploy is needed. D — Parameter Store does **not** have automatic rotation.
- 🧠 **Key point / trap:** rotation = change in **both secret + database**; four steps, `finishSecret` locks in `AWSCURRENT`.
- 📎 Source: `resources/secrets-manager-rotation.md` (four-step rotation function).

### Question 23 — Answer: **B**
- **Why correct:** Secrets Manager supports **cross-account** access via a **resource-based policy** on the secret, plus a KMS key policy that allows the other account to `Decrypt`; and the secret can still be rotated.
- **Why the others are wrong:** A, D — serious credential exposure, not secure. C — Parameter Store **standard** tier does **not** support cross-account sharing (only advanced), and Parameter Store has **no** rotation → fails the "rotatable" requirement.
- 🧠 **Key point / trap:** "cross-account + rotate" → **Secrets Manager** (resource policy + KMS key policy). Standard Parameter Store cannot share cross-account.
- 📎 Source: Week 7 `README.md` (comparison table — cross-account), `resources/secrets-manager-intro.md`.

### Question 24 — Answer: **A, B**
- **Why correct:** A — `String`/`StringList` store **plaintext**; only `SecureString` is encrypted with KMS. B — Parameter Store has **no** built-in automatic rotation; use Secrets Manager if you need rotation.
- **Why the others are wrong:** C — only `SecureString` is encrypted, not "every type." D — Parameter Store does **not** auto-rotate `SecureString`. E — parameter policies are available only in the **advanced** tier, not standard.
- 🧠 **Key point / trap:** Parameter Store: only `SecureString` is encrypted, **no built-in rotation**; parameter policies are advanced-only.
- 📎 Source: `resources/ssm-parameter-store.md`, `resources/ssm-parameter-store-tiers.md`.
