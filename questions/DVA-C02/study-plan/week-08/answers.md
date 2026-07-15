# ✅ Answers & Explanations — Week 8

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-BC · 4-B · 5-C · 6-B · 7-C · 8-C · 9-B · 10-B · 11-AB · 12-B · 13-A · 14-B · 15-AB · 16-B · 17-B · 18-B · 19-AB · 20-A · 21-B · 22-A · 23-C · 24-B · 25-BCD · 26-AB · 27-A · 28-AB · 29-A · 30-ABC

---

### Question 1 — Answer: **B**
- **Why correct:** `buildspec.yml` belongs to **AWS CodeBuild**. By default the file must sit at the **root** of the source directory. You can override its name/location (for example `config/buildspec.yml`) or store it in `S3` — if it is in `S3`, the bucket must be in the **same Region** as the build project; each project uses only one buildspec.
- **Why the others are wrong:** A & D — `appspec.yml` belongs to CodeDeploy; `buildspec.yml` is not a CodeDeploy file. C — CodePipeline only orchestrates and does not read the buildspec.
- 🧠 **Key point / trap:** see `buildspec.yml` → **CodeBuild + ROOT**. This is a classic exam trap (easy to confuse with CodeDeploy).
- 📎 Source: `resources/codebuild-buildspec.md` (file name & storage location — root of source directory).

### Question 2 — Answer: **C**
- **Why correct:** The four phases run in the fixed order `install → pre_build → build → post_build`. Only `install` has `runtime-versions` (install the runtime); `pre_build` prepares (log in to ECR, `npm ci`); `build` builds; `post_build` packages/pushes the image.
- **Why the others are wrong:** A, B, D scramble the order — CodeBuild always runs these four phases in this exact sequence and cannot reorder them.
- 🧠 **Key point / trap:** remember "IN-PRE-BUILD-POST": `install → pre_build → build → post_build`.
- 📎 Source: `resources/codebuild-buildspec.md` (phases; runtime-versions only in install).

### Question 3 — Answer: **B, C**
- **Why correct:** Inject secrets securely through `env/parameter-store` (pulls from `SSM Parameter Store`; the service role needs `ssm:GetParameters`) (B) and `env/secrets-manager` (pulls from `Secrets Manager`) (C). CodeBuild automatically **masks** these values in the logs.
- **Why the others are wrong:** A — `variables` are **plaintext** and are strongly discouraged for secrets. D — hardcoding in commands still exposes the secret. E — `artifacts/name` is not a place for secrets.
- 🧠 **Key point / trap:** secrets in a build → **`parameter-store` / `secrets-manager`**, never `variables`. Note that masking only matches the original value — if you transform it (Base64, etc.), the transformed value leaks into the log.
- 📎 Source: `resources/codebuild-buildspec.md` (env/parameter-store, env/secrets-manager, variables discouraged).

### Question 4 — Answer: **B**
- **Why correct:** `artifacts` declares the **output files** that CodeBuild packages and uploads to the `S3` output bucket (for the Deploy stage to use).
- **Why the others are wrong:** A — `cache` only **keeps dependencies** (such as `node_modules`) between builds to run faster; it is not the deployment output. C — `reports` sends **test/coverage reports** to a report group (default `JUNITXML`). D — `env/variables` are environment variables.
- 🧠 **Key point / trap:** `artifacts` = output to S3; `cache` = faster builds; `reports` = test results. Do not mix them up.
- 📎 Source: `resources/codebuild-buildspec.md` (artifacts, cache, reports sections).

### Question 5 — Answer: **C**
- **Why correct:** `appspec.yml` (or `.json`) is an **AWS CodeDeploy** file used to define what to install on the instances and which hooks to run through the lifecycle. For EC2/on-premises it must be YAML named `appspec.yml` placed at the **root** of the revision.
- **Why the others are wrong:** A — CodeBuild reads `buildspec.yml`. B — CodePipeline orchestrates stages. D — CloudFormation uses a template.
- 🧠 **Key point / trap:** see `appspec.yml` → **CodeDeploy** (the symmetric trap to `buildspec.yml` = CodeBuild).
- 📎 Source: `resources/codedeploy-appspec.md` (AppSpec file reference).

### Question 6 — Answer: **B**
- **Why correct:** The runnable lifecycle hook order for EC2/on-premises is `ApplicationStop → BeforeInstall → AfterInstall → ApplicationStart → ValidateService`. Stop the old app first, install the new one, start it, then validate.
- **Why the others are wrong:** A, C scramble the order. D — `BeforeAllowTraffic`/`AfterAllowTraffic` are **Lambda/ECS** hooks (traffic shifting), not EC2.
- 🧠 **Key point / trap:** "Stop-Before-After-Start-Validate". EC2 uses lifecycle install hooks; Lambda/ECS use AllowTraffic hooks.
- 📎 Source: Week 8 `README.md` (EC2 hooks table) + `resources/codedeploy-appspec.md` (hooks section).

### Question 7 — Answer: **C**
- **Why correct:** For Lambda, the hooks are only `BeforeAllowTraffic` (runs **before** traffic goes to the new version) and `AfterAllowTraffic` (runs **after**). Validation before the shift → `BeforeAllowTraffic`.
- **Why the others are wrong:** A, B, D — `AfterInstall`/`ApplicationStop`/`ValidateService` are **EC2/on-premises** hooks, not used for Lambda.
- 🧠 **Key point / trap:** Lambda = `BeforeAllowTraffic` / `AfterAllowTraffic`. (ECS additionally has `BeforeInstall`, `AfterInstall`, `AfterAllowTestTraffic`.)
- 📎 Source: Week 8 `README.md` (Lambda / ECS hooks) + `resources/codedeploy-appspec.md`.

### Question 8 — Answer: **C**
- **Why correct:** If unspecified, CodeDeploy uses the default **`CodeDeployDefault.OneAtATime`**. The built-in configs for EC2/on-premises are `AllAtOnce`, `HalfAtATime`, `OneAtATime` (based on minimum healthy hosts).
- **Why the others are wrong:** A, B give the wrong default config. D — `Canary`/`Linear`/`AllAtOnce` belong to **Lambda & ECS**, not EC2.
- 🧠 **Key point / trap:** EC2 = **AllAtOnce/HalfAtATime/OneAtATime**, default **OneAtATime**. `HalfAtATime`/`OneAtATime` do NOT apply to Lambda/ECS.
- 📎 Source: `resources/codedeploy-deployment-configs.md` (EC2 predefined configs; default OneAtATime).

### Question 9 — Answer: **B**
- **Why correct:** In-place applies **only** to **EC2/on-premises**. Lambda (and ECS) always deploy **Blue/Green** with traffic shifting (Canary/Linear/AllAtOnce) — there is no "in-place" concept for Lambda.
- **Why the others are wrong:** A, C — Lambda has no In-place option. D — Lambda does have Blue/Green (in fact it always uses it).
- 🧠 **Key point / trap:** In-place = **EC2/on-premises only**; Lambda/ECS = **Blue/Green** (traffic shift). A common trap.
- 📎 Source: Week 8 `README.md` (In-place EC2 only; Blue/Green EC2/ECS/Lambda) + `resources/codedeploy-deployment-configs.md`.

### Question 10 — Answer: **B**
- **Why correct:** **Canary** = shift a small slice (10%) first, then shift the remainder (90%) **all at once** after X minutes → matches the description → `LambdaCanary10Percent5Minutes`.
- **Why the others are wrong:** A — **Linear** shifts **evenly** 10% every minute until done (quite different from canary). C — `AllAtOnce` shifts everything immediately. D — `HalfAtATime` is an **EC2** config, not used for Lambda.
- 🧠 **Key point / trap:** Canary = "10% then the rest in one shot"; Linear = "10% per step, evenly". Easy to confuse.
- 📎 Source: `resources/codedeploy-deployment-configs.md` (Lambda predefined configs; canary vs linear).

### Question 11 — Answer: **A, B**
- **Why correct:** Blue/Green is supported on **EC2/on-premises, ECS, and Lambda** (A) and enables **fast rollback** by routing traffic back to the old "blue" environment (B) — you build a parallel "green" environment and then shift traffic.
- **Why the others are wrong:** C — not Lambda only. D — that describes **In-place** (updating the old instances directly), not Blue/Green. E — `HalfAtATime` is an EC2 in-place config and is not required for Blue/Green.
- 🧠 **Key point / trap:** Blue/Green = two parallel environments + fast rollback, applies to **EC2/ECS/Lambda**.
- 📎 Source: Week 8 `README.md` (In-place vs Blue/Green) + `resources/codedeploy-deployment-configs.md`.

### Question 12 — Answer: **B**
- **Why correct:** Connect GitHub to CodePipeline/CodeBuild through **`CodeConnections`** (a managed connection, no hardcoded token needed). It was formerly named *CodeStar Connections*; **AWS CodeStar (the project service) has reached end of life**, so choose the new name.
- **Why the others are wrong:** A — "the current CodeStar service" is outdated naming/context. C — hardcoding the token is a security vulnerability. D — mirroring to CodeCommit is not required.
- 🧠 **Key point / trap:** GitHub + pipeline → **`CodeConnections`** (do NOT use the CodeStar name).
- 📎 Source: Week 8 `README.md` (CodeConnections) + `resources/codepipeline-concepts.md` (source integrations / webhooks V2).

### Question 13 — Answer: **A**
- **Why correct:** Artifacts pass between actions/stages through the **`S3` artifact store**; and a **single stage processes only one execution at a time** (the stage is "locked" while it runs) — a classic exam trap.
- **Why the others are wrong:** B — artifacts are in S3 (not DynamoDB); the default execution mode is **SUPERSEDED**, not parallel. C — building still needs CodeBuild (or another build provider). D — nothing is stored on a CodeDeploy disk.
- 🧠 **Key point / trap:** artifact store = **S3**; **one stage = one execution** at a time.
- 📎 Source: `resources/codepipeline-concepts.md` (Artifacts — artifact bucket; stage locked, one execution at a time).

### Question 14 — Answer: **B**
- **Why correct:** `Fn::GetAtt` returns a **specific attribute** of a resource (for example an ELB's `DNSName`, an ARN, or an endpoint address).
- **Why the others are wrong:** A — `Ref` returns the **default value** (usually the physical ID for a resource, or the value for a parameter), not an ARN/DNSName. C — `Fn::ImportValue` reads an export from another stack. D — `Fn::FindInMap` looks up a value in `Mappings`.
- 🧠 **Key point / trap:** need a **specific attribute (ARN/DNSName)** → `Fn::GetAtt`; need the ID/default value → `Ref`.
- 📎 Source: `resources/cloudformation-intrinsic-functions.md` (Ref vs Fn::GetAtt).

### Question 15 — Answer: **A, B**
- **Why correct:** Sharing a value between two **independent** stacks = a cross-stack reference: the source stack declares an `Outputs` entry with an **`Export`** (A), and the destination stack reads it with **`Fn::ImportValue`** (B).
- **Why the others are wrong:** C — `Fn::GetAtt` works only within the **same** template and cannot read another stack's resource. D — **nested stacks** reuse a *component template* embedded in a parent stack; they are NOT for sharing a single value between two separate stacks. E — hardcoding the ID is an anti-pattern (breaks the link, fragile when the resource changes).
- 🧠 **Key point / trap:** cross-stack = **`Export` + `Fn::ImportValue`**; nested stack = reuse a child template (different purpose).
- 📎 Source: Week 8 `README.md` (cross-stack) + `resources/cloudformation-intrinsic-functions.md` (Fn::ImportValue).

### Question 16 — Answer: **B**
- **Why correct:** A **change set** lets you **preview** the changes (which resources will be modified/replaced/deleted) before executing → avoids unintended modification/deletion on production.
- **Why the others are wrong:** A — **drift detection** finds resources that were **manually** changed away from the template (already happened), not a preview of upcoming changes. C — `DeletionPolicy` acts when a resource is deleted. D — a nested stack is a structural organization mechanism.
- 🧠 **Key point / trap:** "preview changes before applying" → **change set** (do not confuse with drift).
- 📎 Source: Week 8 `README.md` (change set) + the "common exam traps" table.

### Question 17 — Answer: **B**
- **Why correct:** `DeletionPolicy: Retain` **keeps** the resource when the stack is deleted (the DB is not deleted). If you need a backup, use `Snapshot` (takes a snapshot before deletion — for RDS/EBS, etc.).
- **Why the others are wrong:** A — `Delete` (the default) would delete the DB → data loss. C — `DependsOn` only forces creation order. D — `UpdateReplacePolicy` acts during an **update**, and `Delete` still deletes.
- 🧠 **Key point / trap:** "keep a resource when the stack is deleted" → **`DeletionPolicy: Retain`** (or `Snapshot` if you need a backup).
- 📎 Source: Week 8 `README.md` (DeletionPolicy: Delete/Retain/Snapshot).

### Question 18 — Answer: **B**
- **Why correct:** **Drift detection** finds resources that were modified outside CloudFormation (manual edits) so the actual state diverges from the template.
- **Why the others are wrong:** A — a **change set** previews *upcoming* changes and does not detect manual edits. C — `Fn::FindInMap` is an intrinsic function that looks up a map. D — a stack policy prevents unintended updates but does not detect drift.
- 🧠 **Key point / trap:** "a resource manually changed away from the template" → **drift detection** (the opposite of a change set = preview).
- 📎 Source: Week 8 `README.md` (drift detection) + the "quick reflexes" table.

### Question 19 — Answer: **A, B**
- **Why correct:** `Fn::Sub` substitutes variables into a string via `${VarName}` (A); `Fn::FindInMap` looks up a two-level value in the `Mappings` section, commonly used to select an AMI by Region (B).
- **Why the others are wrong:** C — `Ref` returns the physical ID / parameter value, **not** an ARN. D — `Fn::If` is used in resource properties/`Conditions` (to conditionally create resources or assign values), **not** in `Parameters`. E — joining values into a string with a delimiter is `Fn::Join`; `Fn::GetAZs` returns the **list of AZs** in the Region.
- 🧠 **Key point / trap:** `Sub` = substitute variables into a string; `FindInMap` = look up Mappings; `Join` = join a string; `GetAZs` = list of AZs.
- 📎 Source: `resources/cloudformation-intrinsic-functions.md` (Fn::Sub, Fn::FindInMap, Fn::Join, Fn::GetAZs, Ref).

### Question 20 — Answer: **A**
- **Why correct:** The line **`Transform: AWS::Serverless-2016-10-31`** at the top of the template tells CloudFormation to expand the shorthand SAM syntax (`AWS::Serverless::Function`, `::Api`, etc.) into full CloudFormation resources at deploy time.
- **Why the others are wrong:** B — the file name does not have to be `sam.yaml` (usually `template.yaml`). C — `Resources` must NOT be empty (it is required). D — `version: 0.2` belongs to `buildspec.yml` and is unrelated to SAM.
- 🧠 **Key point / trap:** see `Transform: AWS::Serverless-2016-10-31` → **SAM**. CLI: `sam init/build/deploy/local/sync`.
- 📎 Source: `resources/sam-overview.md` (Transform header; SAM is an extension of CloudFormation).

### Question 21 — Answer: **B**
- **Why correct:** `sam local invoke` (run the Lambda locally) and `sam local start-api` (emulate API Gateway locally) let you **test offline** before deploying — matching Domain 3.2 (testing in the dev environment).
- **Why the others are wrong:** A — `sam deploy --guided` deploys to AWS (not local testing). C — `sam package` only packages the artifact. D — `sam publish` publishes the app to the Serverless Application Repository.
- 🧠 **Key point / trap:** test **locally** before deploying → **`sam local invoke` / `sam local start-api`**.
- 📎 Source: Week 8 `README.md` (Session C — `sam local invoke`, `sam local start-api`) + `resources/sam-overview.md`.

### Question 22 — Answer: **A**
- **Why correct:** `DeploymentPreference` on `AWS::Serverless::Function` (Type `Canary`/`Linear`) makes SAM **use AWS CodeDeploy** to shift traffic gradually when updating the Lambda → a safe deployment that can roll back.
- **Why the others are wrong:** B — `DeletionPolicy: Snapshot` only matters at resource deletion. C — `ReservedConcurrentExecutions: 0` would **block** invocations (fully throttled). D — `Fn::ImportValue` is a cross-stack reference, unrelated to traffic shifting.
- 🧠 **Key point / trap:** SAM safe Lambda deploy → **`DeploymentPreference` (Canary/Linear via CodeDeploy)**.
- 📎 Source: Week 8 `README.md` (SAM — DeploymentPreference) + `resources/sam-overview.md`.

### Question 23 — Answer: **C**
- **Why correct:** `Immutable` launches a **full set of NEW instances** in a separate Auto Scaling group; if a health check fails it terminates the entire new set and **does not touch** the old instances → zero-downtime, safest, easy rollback.
- **Why the others are wrong:** A — `Rolling` deploys directly onto the existing instances (reduces capacity, touches old instances). B — `All at once` has downtime. D — `Rolling with additional batch` also deploys onto the old instances (it just adds a batch to keep capacity), still touching the current instances.
- 🧠 **Key point / trap:** "zero-downtime + do NOT touch old instances" (Beanstalk) → **`Immutable`**.
- 📎 Source: `resources/beanstalk-deployment-policies.md` (Immutable — separate ASG, fresh instances).

### Question 24 — Answer: **B**
- **Why correct:** `Rolling with additional batch` launches an **extra batch of new instances FIRST** before removing the old batch → keeps **full capacity** throughout; it temporarily costs one extra batch (fewer resources than Immutable, which doubles everything).
- **Why the others are wrong:** A — `Rolling` (without an additional batch) **reduces capacity** because it pulls a batch out of service. C — `All at once` has downtime and is not batched. D — `Traffic splitting` is canary (splits traffic by %), a different goal than "batched deploy that keeps capacity".
- 🧠 **Key point / trap:** "batched deploy + keep full capacity" → **`Rolling with additional batch`**; `Rolling` typically = reduced capacity.
- 📎 Source: `resources/beanstalk-deployment-policies.md` (Rolling vs Rolling with additional batch — capacity).

### Question 25 — Answer: **B, C, D**
- **Why correct:** B — Blue/Green in Beanstalk is a **CNAME/URL swap** between two environments (a manual technique), NOT one of the five deployment policies. C — `Traffic splitting` (canary) **requires an `Application Load Balancer`**. D — a **worker tier** reads jobs from `SQS`; the environment is customized with **`.ebextensions/*.config`** files.
- **Why the others are wrong:** A — Blue/Green is NOT a Beanstalk deployment policy. E — `All at once` deploys **everything simultaneously** (not batched) and has a **brief downtime**; it does not maintain full capacity continuously.
- 🧠 **Key point / trap:** the 5 Beanstalk policies = All at once / Rolling / Rolling + additional batch / Immutable / Traffic splitting. **Blue/Green = CNAME swap (not a policy)**; Traffic splitting needs an **ALB**.
- 📎 Source: `resources/beanstalk-deployment-policies.md` (5 policies, blue/green = CNAME swap, traffic splitting requires ALB) + Week 8 `README.md` (worker tier / .ebextensions).

### Question 26 — Answer: **A, B**
- **Why correct:** A — the **task execution role** grants the **ECS agent** permission to pull images from `ECR` and write `CloudWatch` logs (used when starting a task). B — the **task role** grants the **application code inside the container** permission to call AWS APIs (S3/DynamoDB, etc.).
- **Why the others are wrong:** C — pulling ECR images is the job of the **execution** role (not the task role). D — calling DynamoDB from the app is the job of the **task** role (not the execution role) — C and D **swap** the roles. E — Fargate still needs an execution role (and a task role if the app calls AWS APIs).
- 🧠 **Key point / trap:** **execution role = pull ECR images + logs**; **task role = app permissions**. An "image pull failed / missing log permissions" error → missing **execution role**.
- 📎 Source: `resources/ecs-task-definitions.md` (task execution role vs task role) + Week 8 `README.md`.

### Question 27 — Answer: **A**
- **Why correct:** `Fargate` is a **serverless** launch type (no EC2 instances to manage); Fargate **requires** the `awsvpc` network mode — each task gets its **own ENI + private IP**.
- **Why the others are wrong:** B, D — the `EC2` launch type forces you to manage instances yourself (against the requirement). C — Fargate does not use `bridge`; only `awsvpc`.
- 🧠 **Key point / trap:** do not want to manage servers → **`Fargate`**; Fargate = **`awsvpc` required** (own ENI/IP per task).
- 📎 Source: `resources/ecs-task-definitions.md` (network mode; Fargate uses only awsvpc).

### Question 28 — Answer: **A, B**
- **Why correct:** To push an image to ECR: (A) **authenticate** with `aws ecr get-login-password | docker login ...`, then (B) `docker tag` the image with the ECR repository URI and `docker push`.
- **Why the others are wrong:** C — ECR does not accept `git push` (it is a Docker registry, not a Git repo). D — you do not use `aws s3 cp` to push an image. E — `sam deploy` deploys a serverless stack; it is not the standard way to manually push an image to ECR.
- 🧠 **Key point / trap:** ECR push = **login (get-login-password) → tag → push** (using `docker`, not git/s3).
- 📎 Source: Week 8 `README.md` (ECR login/tag/push commands).

### Question 29 — Answer: **A**
- **Why correct:** `ECR` provides a **`lifecycle policy`** to automatically clean up old/unused images, and **`image scanning`** to scan images for vulnerabilities (CVEs).
- **Why the others are wrong:** B — the images are in ECR (not your S3 bucket); `Macie` scans for sensitive data in S3, not images. C — `DeletionPolicy` belongs to CloudFormation. D — `CodeGuru` reviews code / profiles it; it does not clean up images or scan for CVEs.
- 🧠 **Key point / trap:** clean up old images → **lifecycle policy**; scan for vulnerabilities → **image scanning** (both belong to ECR).
- 📎 Source: Week 8 `README.md` (ECR — lifecycle policy + image scanning).

### Question 30 — Answer: **A, B, C**
- **Why correct:** A — `AppConfig` manages **feature flags** & runtime configuration, **decoupling config from code** (change configuration without redeploying). B — it supports **gradual rollout** (a deployment strategy that rolls out progressively by %/time). C — it **automatically rolls back** a configuration when a `CloudWatch alarm` triggers.
- **Why the others are wrong:** D — the opposite; the purpose of AppConfig is to **avoid** redeploying when config changes. E — AppConfig works across many platforms (Lambda extension, ECS, EC2, on-premises, etc.), not just EC2.
- 🧠 **Key point / trap:** AppConfig = **feature flags + gradual rollout + alarm-based rollback**, decouples config from code (no redeploy).
- 📎 Source: Week 8 `README.md` (Session A — `AWS AppConfig`: feature flags, gradual rollout, automatic rollback on alarm).
