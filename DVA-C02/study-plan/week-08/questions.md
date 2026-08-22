# 📝 Practice Questions — Week 8: Deployment — CI/CD, CloudFormation/SAM, Elastic Beanstalk, ECS/ECR, AppConfig

> **30 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Domain 3 – Deployment (24%, the heaviest week).
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (the number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D3.1 · CodeBuild · Single]`
In a CI/CD pipeline, a `buildspec.yml` file is used to define build commands. Which service consumes this file, and where must it be located in the source by default?
- A. AWS CodeDeploy; it must be placed in a `scripts/` directory
- B. AWS CodeBuild; by default it must be at the **root** of the source directory (the name/location can be overridden, and it can even be stored in `S3` in the same Region)
- C. AWS CodePipeline; it must be placed in the `S3` artifact store
- D. AWS CodeDeploy; it must be at the root next to `appspec.yml`

### Question 2 — `[D3.1 · CodeBuild · Single]`
A developer writes a `buildspec.yml` that must install the Node.js runtime, then install dependencies with `npm ci`, then build the application, then package and push a container image. In which order does AWS CodeBuild run its four phases?
- A. `pre_build → install → build → post_build`
- B. `install → build → pre_build → post_build`
- C. `install → pre_build → build → post_build`
- D. `build → install → pre_build → post_build`

### Question 3 — `[D3.1 · CodeBuild · Multi — Choose 2]`
A build needs a database password and an API key, but a security policy forbids hardcoding secrets in `buildspec.yml`. Which two approaches correctly inject these secrets into the build's environment variables? (Choose two.)
- A. Declare them under `env/variables` as plaintext values
- B. Declare them under `env/parameter-store` to pull from `SSM Parameter Store` (the service role needs `ssm:GetParameters`)
- C. Declare them under `env/secrets-manager` to pull from `Secrets Manager`
- D. Hardcode them in `phases/build/commands` and delete the logs after the build completes
- E. Embed the secret in the `artifacts/name` property

### Question 4 — `[D3.1 · CodeBuild · Single]`
In `buildspec.yml`, which section declares the **output files** that AWS CodeBuild packages and **uploads to `S3`** for a later Deploy stage to use?
- A. `cache`
- B. `artifacts`
- C. `reports`
- D. `env/variables`

### Question 5 — `[D3.4 · CodeDeploy · Single]`
Which service reads an `appspec.yml` file to manage a deployment?
- A. AWS CodeBuild
- B. AWS CodePipeline
- C. AWS CodeDeploy
- D. AWS CloudFormation

### Question 6 — `[D3.4 · CodeDeploy · Single]`
What is the correct order of the deployment lifecycle event hooks for an **EC2/on-premises** deployment?
- A. `BeforeInstall → ApplicationStop → AfterInstall → ValidateService → ApplicationStart`
- B. `ApplicationStop → BeforeInstall → AfterInstall → ApplicationStart → ValidateService`
- C. `ApplicationStart → BeforeInstall → AfterInstall → ApplicationStop → ValidateService`
- D. `BeforeAllowTraffic → AfterInstall → AfterAllowTraffic → ValidateService`

### Question 7 — `[D3.4 · CodeDeploy · Single]`
A developer deploys an AWS Lambda function with AWS CodeDeploy and must run a Lambda validation function **before** traffic is shifted to the new version. Which lifecycle hook should the developer use?
- A. `AfterInstall`
- B. `ApplicationStop`
- C. `BeforeAllowTraffic`
- D. `ValidateService`

### Question 8 — `[D3.4 · CodeDeploy · Single]`
A team deploys to an `EC2` fleet with AWS CodeDeploy but does **not** specify a deployment configuration. Which configuration does CodeDeploy use by default, and what is the valid set of built-in configurations for EC2/on-premises?
- A. Default `AllAtOnce`; EC2 configs: `AllAtOnce` / `Canary` / `Linear`
- B. Default `HalfAtATime`; EC2 configs: `HalfAtATime` / `OneAtATime`
- C. Default `OneAtATime`; EC2 configs: `AllAtOnce` / `HalfAtATime` / `OneAtATime`
- D. Default `Canary10Percent5Minutes`; EC2 configs: `Canary` / `Linear` / `AllAtOnce`

### Question 9 — `[D3.4 · CodeDeploy · Single]`
A developer wants to use an **In-place** deployment type for an AWS Lambda function through AWS CodeDeploy. Which statement is correct?
- A. It is allowed — Lambda supports both In-place and Blue/Green
- B. It is not allowed — In-place applies only to **EC2/on-premises**; Lambda always uses **Blue/Green** with traffic shifting (Canary/Linear/AllAtOnce)
- C. It is allowed, as long as the `InPlaceLambda` flag is enabled
- D. It is not allowed — Lambda supports only In-place, not Blue/Green

### Question 10 — `[D3.4 · CodeDeploy · Single]`
A Lambda deployment requirement: shift **10%** of traffic to the new version first, monitor it, then shift the **remaining 90% all at once** after 5 minutes. Which built-in deployment configuration matches this?
- A. `CodeDeployDefault.LambdaLinear10PercentEvery1Minute`
- B. `CodeDeployDefault.LambdaCanary10Percent5Minutes`
- C. `CodeDeployDefault.LambdaAllAtOnce`
- D. `CodeDeployDefault.HalfAtATime`

### Question 11 — `[D3.4 · CodeDeploy · Multi — Choose 2]`
Which statements about **Blue/Green deployments** in AWS CodeDeploy are correct? (Choose two.)
- A. Supported on **EC2/on-premises, ECS, and Lambda**
- B. Enables **fast rollback** by routing traffic back to the old ("blue") environment
- C. Supported only on Lambda
- D. Updates the current instances directly, so it is cheap and uses no extra resources
- E. Requires `HalfAtATime` on every platform

### Question 12 — `[D3.4 · CodePipeline · Single]`
A pipeline's source is a **GitHub** repository. The team wants a secure connection and does **not** want a personal access token exposed in the configuration. What should the team use?
- A. CodeStar Connections (the current CodeStar service)
- B. `CodeConnections` (a connection to GitHub; formerly named CodeStar Connections, since AWS CodeStar has reached end of life)
- C. Hardcode the token under `env/variables` in `buildspec.yml`
- D. Mirror the repository to `CodeCommit` first, which is required

### Question 13 — `[D3.3 · CodePipeline · Single]`
Which statement correctly describes how AWS CodePipeline automates a Source → Build → Test → Deploy sequence?
- A. Artifacts passed between stages are stored in an **`S3` artifact store**; each **stage** processes only **one execution** at a time (the stage is locked while it runs)
- B. Artifacts are stored in a `DynamoDB` table, and all stages run in parallel by default
- C. CodePipeline builds the source itself without needing AWS CodeBuild
- D. Artifacts are stored on the local disk of the CodeDeploy agent

### Question 14 — `[D3.4 · CloudFormation · Single]`
A template needs the **DNS name** of an `ELB` (or the **ARN** of a resource) to assign it to another property in the same template. Which intrinsic function should be used?
- A. `Ref` (returns the physical ID / the value of a parameter)
- B. `Fn::GetAtt` (returns a specific attribute such as an ARN or DNSName)
- C. `Fn::ImportValue`
- D. `Fn::FindInMap`

### Question 15 — `[D3.4 · CloudFormation · Multi — Choose 2]`
Stack A creates a VPC. Stack B is a **separate stack** that needs to reuse the **VPC ID** from stack A. What should be done? (Choose two.)
- A. In stack A: declare an `Outputs` entry with an **`Export`** (name the export for the VPC ID)
- B. In stack B: use **`Fn::ImportValue`** to read the exported value
- C. In stack B: use `Fn::GetAtt` directly against stack A's resource
- D. Nest the entire stack A inside stack B using `AWS::CloudFormation::Stack`
- E. Copy and paste the VPC ID as a hardcoded value into stack B

### Question 16 — `[D3.4 · CloudFormation · Single]`
Before applying an update to a **production** stack, the team wants to **preview** which resources will be **modified, replaced, or deleted** to avoid unintended changes. Which feature should they use?
- A. Drift detection
- B. Change set
- C. `DeletionPolicy`
- D. Nested stack

### Question 17 — `[D3.4 · CloudFormation · Single]`
When a stack is **deleted**, an `RDS` database must be **retained** (its data must never be lost). What should be configured on the RDS resource?
- A. `DeletionPolicy: Delete`
- B. `DeletionPolicy: Retain` (or `Snapshot` to take a backup before deletion)
- C. `DependsOn: RDS`
- D. `UpdateReplacePolicy: Delete`

### Question 18 — `[D3.4 · CloudFormation · Single]`
A team suspects someone **manually modified** a security group, causing the actual configuration to diverge from the template. Which CloudFormation feature detects this?
- A. Change set
- B. Drift detection
- C. `Fn::FindInMap`
- D. Stack policy

### Question 19 — `[D3.4 · CloudFormation · Multi — Choose 2]`
Which statements about `CloudFormation` intrinsic functions are correct? (Choose two.)
- A. `Fn::Sub` substitutes variables into a string using the `${VarName}` syntax
- B. `Fn::FindInMap` looks up a value in a two-level map in the `Mappings` section (for example, selecting an AMI by Region)
- C. `Ref` always returns the **ARN** of a resource
- D. `Fn::If` may be used only in the `Parameters` section
- E. `Fn::GetAZs` joins multiple values into a single string with a delimiter

### Question 20 — `[D3.4 · SAM · Single]`
Which indicator identifies a template as an **`AWS SAM`** template (which CloudFormation expands from the shorthand serverless syntax at deploy time)?
- A. The line `Transform: AWS::Serverless-2016-10-31` at the top of the template
- B. The file must be named `sam.yaml`
- C. The `Resources` section must be empty
- D. The line `version: 0.2` at the top of the template

### Question 21 — `[D3.2 · SAM · Single]`
A developer wants to **test Lambda + API Gateway locally (offline)** on their machine before deploying to AWS. Which SAM CLI command fits?
- A. `sam deploy --guided`
- B. `sam local invoke` / `sam local start-api`
- C. `sam package`
- D. `sam publish`

### Question 22 — `[D3.4 · SAM · Single]`
A developer wants to update a Lambda function **safely** by **gradually** shifting traffic (canary) when deploying through AWS SAM. What must be declared on the `AWS::Serverless::Function`?
- A. `DeploymentPreference` (Type: `Canary`/`Linear`) — SAM uses **AWS CodeDeploy** to shift traffic
- B. `DeletionPolicy: Snapshot`
- C. `ReservedConcurrentExecutions: 0`
- D. `Fn::ImportValue`

### Question 23 — `[D3.4 · Elastic Beanstalk · Single]`
A deployment on `Elastic Beanstalk` must be **zero-downtime**, must **not touch** the running instances, and if a health check fails must terminate all the new instances (easy rollback). Which deployment policy meets these requirements?
- A. `Rolling`
- B. `All at once`
- C. `Immutable`
- D. `Rolling with additional batch`

### Question 24 — `[D3.4 · Elastic Beanstalk · Single]`
A developer wants to deploy in **batches** but keep **full capacity** throughout (without reducing the number of serving instances), while using fewer resources than `Immutable`. Which policy fits?
- A. `Rolling` (reduces capacity during the deployment)
- B. `Rolling with additional batch` (launches one extra new batch before removing the old batch)
- C. `All at once`
- D. `Traffic splitting`

### Question 25 — `[D3.4 · Elastic Beanstalk · Multi — Choose 3]`
Which statements about `Elastic Beanstalk` are correct? (Choose three.)
- A. Blue/Green is an official **deployment policy** in Beanstalk's list of policies
- B. Blue/Green in Beanstalk is performed by **swapping the CNAME/URL** between two environments (it is **not** a deployment policy)
- C. `Traffic splitting` (canary) requires an **`Application Load Balancer`**
- D. A **worker environment tier** reads jobs from `SQS`; the environment is customized with **`.ebextensions/*.config`** files
- E. `All at once` deploys in batches and always keeps full capacity with no downtime

### Question 26 — `[D3.4 · ECS · Multi — Choose 2]`
Regarding IAM roles in `ECS`, which statements are correct? (Choose two.)
- A. **Task execution role**: grants permission to **pull images from `ECR`** and **write `CloudWatch` logs** (used by the ECS agent when starting a task)
- B. **Task role**: grants permission for the **application code inside the container** to call AWS APIs (for example, reading `S3` / `DynamoDB`)
- C. The task role is the role used to pull images from `ECR`
- D. The execution role is the role that grants the application code permission to call `DynamoDB`
- E. `Fargate` does not need any role

### Question 27 — `[D3.4 · ECS/Fargate · Single]`
A team wants to run containers **without managing** any EC2 instances (serverless), where each task has its **own ENI + private IP**. Which configuration should they choose?
- A. `Fargate` launch type; `awsvpc` network mode (required with Fargate)
- B. `EC2` launch type; `host` network mode
- C. `Fargate` launch type; `bridge` network mode
- D. `EC2` launch type; `none` network mode

### Question 28 — `[D3.1 · ECR · Multi — Choose 2]`
Which steps correctly **push** a Docker image to `ECR`? (Choose two.)
- A. Authenticate: `aws ecr get-login-password ... | docker login --username AWS --password-stdin <acct>.dkr.ecr.<region>.amazonaws.com`
- B. `docker tag` the image with the ECR repository URI, then `docker push`
- C. `git push` the image directly to the ECR repository
- D. `aws s3 cp` the image to the ECR bucket
- E. Use `sam deploy` to push the image to ECR

### Question 29 — `[D3.1 · ECR · Single]`
A team wants to (1) **automatically delete** old/unused images in an `ECR` repository and (2) **scan images for vulnerabilities (CVEs)**. What should they use?
- A. `Lifecycle policy` (clean up old images) + `image scanning` (scan for vulnerabilities)
- B. `S3 Lifecycle rule` + `Amazon Macie`
- C. `DeletionPolicy: Snapshot`
- D. `CodeGuru` reviewer

### Question 30 — `[D3.4 · AppConfig · Multi — Choose 3]`
Which statements about `AWS AppConfig` are correct? (Choose three.)
- A. It lets you turn **feature flags** on/off and change runtime configuration **without redeploying** code
- B. It supports **gradual rollout** (deploying configuration progressively by percentage / over time)
- C. It can **automatically roll back** a configuration when a **`CloudWatch alarm`** is triggered
- D. It requires a **full redeployment** of the application every time a single configuration value changes
- E. It works only with `EC2` instances and cannot be used with `Lambda`
