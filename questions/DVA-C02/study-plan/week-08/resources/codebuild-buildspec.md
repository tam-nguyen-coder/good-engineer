# Build specification reference for CodeBuild (buildspec)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html
> **Tuần:** 8 — Deployment / CI-CD / IaC · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `buildspec.yml` mặc định phải nằm ở **root** của source directory; có thể đổi tên/vị trí (vd `config/buildspec.yml` hoặc S3) — nếu để trong S3 thì bucket phải **cùng Region** với build project. Chỉ 1 buildspec cho mỗi project.
- Thứ tự **4 phase** (bẫy thi hay hỏi): `install` → `pre_build` → `build` → `post_build`. Chỉ `install` có `runtime-versions`.
- **Nên dùng version `0.2`** (không phải 0.1). Trong 0.1 mỗi lệnh chạy trong shell riêng (không giữ state); 0.2 giữ state giữa các lệnh.
- Lấy biến bí mật: `parameter-store` (SSM Parameter Store, cần quyền `ssm:GetParameters` trên service role) và `secrets-manager` (Secrets Manager). KHÔNG lưu secret trong `variables` (hiển thị plaintext).
- Thứ tự ưu tiên biến môi trường: **start-build override > project definition > buildspec** (buildspec thấp nhất). Không đặt tên biến bắt đầu bằng `CODEBUILD_` (dành riêng).
- `artifacts` khai báo nơi lấy output để upload lên S3; `reports` gửi test/coverage report tới report group (tối đa **5 report group** / project). File format report mặc định = `JUNITXML`.
- `exported-variables` dùng để truyền biến sang các stage sau trong `CodePipeline`. Biến bắt đầu bằng `AWS_` không export được.
- `finally` block chạy SAU `commands` kể cả khi commands fail. `on-failure`: `ABORT | CONTINUE | RETRY | RETRY-{count}` (count 0–100) — chỉ hỗ trợ EC2 compute, không hỗ trợ Lambda compute.

---

## 📄 Nội dung (trích từ tài liệu gốc)

This topic provides important reference information about build specification (buildspec) files. A *buildspec* is a collection of build commands and related settings, in YAML format, that CodeBuild uses to run a build. You can include a buildspec as part of the source code or you can define a buildspec when you create a build project.

**Topics**
- Buildspec file name and storage location
- Buildspec syntax
- Buildspec example
- Buildspec versions
- Batch build buildspec reference

## Buildspec file name and storage location

If you include a buildspec as part of the source code, by default, the buildspec file must be named `buildspec.yml` and placed in the root of your source directory.

You can override the default buildspec file name and location. For example, you can:
- Use a different buildspec file for different builds in the same repository, such as `buildspec_debug.yml` and `buildspec_release.yml`.
- Store a buildspec file somewhere other than the root of your source directory, such as `config/buildspec.yml` or in an S3 bucket. The S3 bucket must be in the same AWS Region as your build project. Specify the buildspec file using its ARN (for example, `arn:aws:s3:::<my-codebuild-sample2>/buildspec.yml`).

You can specify only one buildspec for a build project, regardless of the buildspec file's name.

To override the default buildspec file name, location, or both, do one of the following:
- Run the AWS CLI `create-project` or `update-project` command, setting the `buildspec` value to the path to the alternate buildspec file relative to the value of the built-in environment variable `CODEBUILD_SRC_DIR`.
- Run the AWS CLI `start-build` command, setting the `buildspecOverride` value to the path relative to `CODEBUILD_SRC_DIR`.
- In an AWS CloudFormation template, set the `BuildSpec` property of `Source` in a resource of type `AWS::CodeBuild::Project`.

## Buildspec syntax

Buildspec files must be expressed in YAML format. If a command contains a character not supported by YAML, you must enclose the command in quotation marks (`""`).

```yaml
version: 0.2

run-as: Linux-user-name

env:
  shell: shell-tag
  variables:
    key: "value"
  parameter-store:
    key: "value"
  exported-variables:
    - variable
  secrets-manager:
    key: secret-id:json-key:version-stage:version-id
  git-credential-helper: no | yes

proxy:
  upload-artifacts: no | yes
  logs: no | yes

batch:
  fast-fail: false | true
  # build-list:
  # build-matrix:
  # build-graph:
  # build-fanout:

phases:
  install:
    run-as: Linux-user-name
    on-failure: ABORT | CONTINUE | RETRY | RETRY-count | RETRY-regex | RETRY-count-regex
    runtime-versions:
      runtime: version
    commands:
      - command
    finally:
      - command
  pre_build:
    run-as: Linux-user-name
    on-failure: ABORT | CONTINUE | RETRY ...
    commands:
      - command
    finally:
      - command
  build:
    run-as: Linux-user-name
    on-failure: ABORT | CONTINUE | RETRY ...
    commands:
      - command
    finally:
      - command
  post_build:
    run-as: Linux-user-name
    on-failure: ABORT | CONTINUE | RETRY ...
    commands:
      - command
    finally:
      - command

reports:
  report-group-name-or-arn:
    files:
      - location
    base-directory: location
    discard-paths: no | yes
    file-format: report-format
artifacts:
  files:
    - location
  name: artifact-name
  discard-paths: no | yes
  base-directory: location
  exclude-paths: excluded paths
  enable-symlinks: no | yes
  s3-prefix: prefix
  secondary-artifacts:
    artifactIdentifier:
      files:
        - location
      name: secondary-artifact-name
      discard-paths: no | yes
      base-directory: location
cache:
  key: key
  fallback-keys:
    - fallback-key
  action: restore | save
  paths:
    - path
```

### version
Required mapping. Represents the buildspec version. We recommend that you use `0.2`. (Version 0.1 is still supported but not recommended.)

### run-as
Optional sequence. Available to Linux users only. Specifies a Linux user that runs commands. Applies globally when at the top; can also be set per-phase. If not specified, all commands run as the **root** user.

### env
Optional sequence. Represents information for one or more custom environment variables.
- To protect sensitive information, AWS access key IDs, Parameter Store strings, and Secrets Manager strings are hidden in CodeBuild logs.
- Masking matches the exact stored value. If a build command transforms a secret (Base64, reverse, case-change, concatenation) before it appears in the logs, the result is a different, non-masked string.

**env/shell** — Optional. Supported shell tags:
- Linux: `bash`, `/bin/sh`
- Windows: `powershell.exe`, `cmd.exe`

**env/variables** — Custom env vars in plain text (key/value). Strongly discouraged for sensitive values. Any variable you set replaces existing ones (including `PATH`). Do not use names starting with `CODEBUILD_`.

**env/parameter-store** — Retrieves custom env vars stored in Amazon EC2 Systems Manager Parameter Store. You must add `ssm:GetParameters` to your CodeBuild service role.

**env/secrets-manager** — Retrieves custom env vars from AWS Secrets Manager. Pattern:
`<key>: <secret-id>:<json-key>:<version-stage>:<version-id>`
- `key` (Required): local env var name.
- `secret-id` (Required): name or ARN of the secret.
- `json-key` (Optional): key of the key-value pair; if omitted, entire secret text is retrieved.
- `version-stage` / `version-id` (Optional): default is version with stage `AWSCURRENT`.

```yaml
env:
  secrets-manager:
    LOCAL_SECRET_VAR: "TestSecret:MY_SECRET_VAR"
```

**env/exported-variables** — Lists env vars to export. Used with AWS CodePipeline to export env vars from the current build stage to subsequent stages. Value available starting with `install` phase, can be updated until end of `post_build`. Cannot export: Parameter Store secrets, Secrets Manager secrets, or variables starting with `AWS_`.

**env/git-credential-helper** — `yes` to use CodeBuild's Git credential helper. Not supported for builds triggered by a webhook for a public Git repository.

### proxy
Optional sequence. Settings if you run your build in an explicit proxy server.
- **proxy/upload-artifacts** — `yes` to upload artifacts. Default `no`.
- **proxy/logs** — `yes` to create CloudWatch logs. Default `no`.

### phases
Required sequence. The commands CodeBuild runs during each phase.

**Note:** In buildspec version 0.1, each command runs in a separate shell instance (isolation, no shared state). Use version 0.2 to share state (e.g. changing directories or setting env vars across commands).

- **phases/\*/run-as** — Per-phase Linux user; phase-level takes precedence over global.
- **phases/\*/on-failure** — Action if a failure occurs:
  - `ABORT` — Abort the build.
  - `CONTINUE` — Continue to the next phase.
  - `RETRY` — Retry up to 3 times (regex `.*`).
  - `RETRY-{count}` — Retry {count} times (count 0–100).
  - `RETRY-{regex}` — Retry up to 3 times matching {regex}.
  - `RETRY-{count}-{regex}` — Retry {count} times matching {regex}.
  - Not supported for Lambda compute or reserved capacity — only EC2 compute images.
- **phases/\*/finally** — Commands run AFTER `commands`, even if a command in `commands` fails. Phase succeeds only when all commands in both blocks run successfully.

Allowed build phase names:
- **install** — For installing packages. Has `runtime-versions` (supported with Ubuntu standard image 5.0+ and AL2 standard image 4.0+). Specify runtimes as `ruby: 3.2`, `nodejs: 18.x`, or `java: latest`. If two runtimes conflict, the build fails.
- **pre_build** — Commands before the build (e.g. sign in to Amazon ECR, npm install).
- **build** — Build commands.
- **post_build** — Commands after the build (e.g. package JAR/WAR, push Docker image to ECR, send SNS notification).

### reports
- **report-group-name-or-arn** — Report group reports are sent to. A project can have a maximum of **five report groups**. New group name format: `<project-name>-<report-group-name>`.
- **files** (Required) — Locations of raw test result data. Supports `'**/*'`, `subdir/*`, `subdir/**/*`.
- **file-format** (Optional) — Default `JUNITXML`. Test reports: `CUCUMBERJSON`, `JUNITXML`, `NUNITXML`, `NUNIT3XML`, `TESTNGXML`, `VISUALSTUDIOTRX`. Code coverage reports: `CLOVERXML`, `COBERTURAXML`, `JACOCOXML`, `SIMPLECOV`.
- **base-directory** — Top-level directories to find raw test files.
- **discard-paths** — `yes` flattens directory structure in output.

### artifacts
Optional sequence. Where CodeBuild finds build output and how it prepares it for uploading to the S3 output bucket. Not required if e.g. only building/pushing a Docker image to ECR or running unit tests.
- Amazon S3 metadata includes header `x-amz-meta-codebuild-buildarn` (the `buildArn` of the build that publishes artifacts).
- **files** (Required) — Build output artifact locations. Supports `'**/*'`, `subdir/*`, `subdir/**/*`.
- **name** — Name for your build artifact; can be computed at build time (e.g. `myname-$(date +%Y-%m-%d)`, `myname-$AWS_REGION`, `builds/$CODEBUILD_BUILD_NUMBER/my-artifacts`).
- **discard-paths** — `yes` flattens directory structure.
- **base-directory** — Top-level directories to include.
- **exclude-paths** — Paths to exclude relative to `base-directory`. `*` matches within a name component; `**` matches across directories.
- **enable-symlinks** — For ZIP output, `yes` preserves internal symlinks.
- **s3-prefix** — Prefix when namespace type is `BUILD_ID`; output path `<s3-prefix>/<build-id>/<name>.zip`.
- **secondary-artifacts** — Multiple artifact definitions matching `secondaryArtifacts` of your project. The `artifacts/files` sequence is always required, even with only secondary artifacts.

### cache
Optional sequence. Not required if cache type is `No Cache`.
- **key** — Primary key (exact match). Example: `key: npm-key-$(codebuild-hash-files package-lock.json)`.
- **fallback-keys** — Up to five fallback keys, matched by prefix search. Ignored if `key` not provided.
- **action** — `restore` (only restore), `save` (only save). Default = both restore and save.
- **paths** (Required) — Cache locations. Supports `'**/*'`, `subdir/*`, `subdir/**/*`.

**Important:** Because a buildspec must be valid YAML, spacing is important. If you use the AWS CLI/SDKs, the buildspec must be a single string in YAML format with escaped whitespace/newlines. In the CodeBuild/CodePipeline consoles you can insert commands for the `build` phase only, separated by `&&`.

## Buildspec example

```yaml
version: 0.2

env:
  variables:
    JAVA_HOME: "/usr/lib/jvm/java-8-openjdk-amd64"
  parameter-store:
    LOGIN_PASSWORD: /CodeBuild/dockerLoginPassword

phases:
  install:
    commands:
      - echo Entered the install phase...
      - apt-get update -y
      - apt-get install -y maven
    finally:
      - echo This always runs even if the update or install command fails
  pre_build:
    commands:
      - echo Entered the pre_build phase...
      - docker login -u User -p $LOGIN_PASSWORD
    finally:
      - echo This always runs even if the login command fails
  build:
    commands:
      - echo Entered the build phase...
      - echo Build started on `date`
      - mvn install
    finally:
      - echo This always runs even if the install command fails
  post_build:
    commands:
      - echo Entered the post_build phase...
      - echo Build completed on `date`

reports:
  arn:aws:codebuild:your-region:your-aws-account-id:report-group/report-group-name-1:
    files:
      - "**/*"
    base-directory: 'target/tests/reports'
    discard-paths: no
  reportGroupCucumberJson:
    files:
      - 'cucumber/target/cucumber-tests.xml'
    discard-paths: yes
    file-format: CUCUMBERJSON # default is JUNITXML
artifacts:
  files:
    - target/messageUtil-1.0.jar
  discard-paths: yes
  secondary-artifacts:
    artifact1:
      files:
        - target/artifact-1.0.jar
      discard-paths: yes
    artifact2:
      files:
        - target/artifact-2.0.jar
      discard-paths: yes
cache:
  paths:
    - '/root/.m2/**/*'
```

## Buildspec versions

| Version | Changes |
| --- | --- |
| 0.2 | Recommended. Commands within a phase run in the same shell (shared state). |
| 0.1 | Initial definition. Each command runs in a separate shell instance (no shared state). |
